#!/usr/bin/env python3
"""r96 VERIFIER law set — re-derives every r96 leg from a receipt's RECORDED
fields only. The entry-level `failures` / `coverage_blocked` lists are never
an input to a law (two receipt-level cross-checks at the end compare the
derived red/blocked sets against them).

Basis: the committed bytes of 7358f13b. Two sources of truth are used, both
outside the fixture's own Python:

  1. my own transcription of the SERVER-side law from the committed C source
     `corpus/live/r96-scout/sources/pipewire-1.6.8-module-protocol-pulse-pulse-server.c`
     (`fix_playback_buffer_attr` :434-525, `clamp_latency` :427-433,
     `frac_to_bytes_round_up` :418-425, `load_defaults` :5550-5567) — see
     `fix_attr()` below;
  2. my own implementation of the `pa_atou` parse law (pulseaudio
     pulsecore/core-util.c:2299-2397 as specified by the r96 boundary) — see
     `my_atou()` below.

Usage:
  r96v_laws.py RECEIPT.json [RECEIPT2.json ...]      # per-receipt law run
  r96v_laws.py --compare A.json B.json               # cross-run leaf walk
  r96v_laws.py --forge RECEIPT.json                  # receipt-forgery suite
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys

RATE = 48000
UINT32_MAX = 0xFFFFFFFF
MAXLENGTH = 4 * 1024 * 1024
QUANTUM_LIMIT = 8192
MIN_QUANTUM = (256, 48000)
FRAME = {"s16le": 2, "s24le": 3, "float32le": 4}

ENTRY_LEGS = {
    "pulsecli_avail_r96_probe": 41,
    "pulsecli_target_r96_probe": 27,
    "pulsecli_attr_r96_probe": 66,
    "pulsecli_props_r96_probe": 20,
    "pulsecli_cork_r96_probe": 22,
}

# law-cell ownership: which entry a law cell belongs to (leg-name prefixes)
CELL_PREFIX = {
    "pulsecli_avail_r96_probe": ("a_", "b_"),
    "pulsecli_target_r96_probe": ("c_", "seat_sinks", "capture_miss_census"),
    "pulsecli_attr_r96_probe": ("t_", "late_attr_census"),
    "pulsecli_props_r96_probe": ("p_", "props."),
    "pulsecli_cork_r96_probe": ("e_", "client_build"),
}


def owns(entry, cell):
    if cell.startswith(entry + ".") or cell.startswith(f"struct.{entry}."):
        return True
    return any(cell.startswith(p) for p in CELL_PREFIX.get(entry, ()))

# the 13-family server lattice: leg name -> (rc, error class)
SRV_LATTICE = {
    "b_default": (0, None),
    "b_unix_prefix": (0, None),
    "b_bare_path": (0, None),
    "b_unix_missing": (1, "pulse_refused"),
    "b_tcp_refused": (1, "pulse_refused"),
    "b_tcp6_refused": (1, "pulse_refused"),
    "b_trailing_slash": (1, "pulse_refused"),
    "b_runtime_path": (1, "pulse_refused"),
    "b_empty_server": (1, "pulse_invalid_server"),
    "b_flag_beats_env": (0, None),
    "b_env_loses_to_flag": (1, "pulse_refused"),
    "b_info_s_after_subcmd": (0, None),
    "b_clientconfig_badserver": (1, "pulse_refused"),
}

# the 17-cell pa_atou parse lattice: cell -> expected env_ms (None = invalid)
PARSE_CELLS = {
    "0x64": 100, "0100": 100, "007": 7, "0X64": None, "00x64": None,
    " 100": None, "\t100": None, "+100": None, "+0x64": None, "-0x64": None,
    "100.5": None, "1e3": None, "99999999999": None, "": None, "abc": None,
    "0": None, "-5": None,
}


# ---------------------------------------------------------------- transcription
def round_down(num, value):
    return (num // value) * value


def round_up(num, value):
    return ((num + value - 1) // value) * value


def frac_to_bytes_round_up(num, denom, frame, rate=RATE):
    """C: u = num*1e6*rate/denom; u = (u + 1e6-1)/1e6; u *= frame_size."""
    u = (num * 1000000 * rate) // denom
    u = (u + 1000000 - 1) // 1000000
    return u * frame


def usec_to_bytes(usec, frame, rate=RATE):
    """C: pa_usec_to_bytes — (usec * rate / 1e6) * frame_size, integer."""
    return (usec * rate // 1000000) * frame


def fix_attr(attr, frame, rate=RATE, adjust=False, early=False):
    """My own transcription of fix_playback_buffer_attr + clamp_latency."""
    a = {"maxlength": UINT32_MAX, "tlength": UINT32_MAX,
         "minreq": UINT32_MAX, "prebuf": UINT32_MAX}
    a.update({k: v for k, v in attr.items() if v is not None})

    maxlength = round_down(MAXLENGTH, frame)
    minreq_base = frac_to_bytes_round_up(256, 48000, frame)
    max_latency = QUANTUM_LIMIT * frame

    if a["maxlength"] == UINT32_MAX or a["maxlength"] > maxlength:
        a["maxlength"] = maxlength
    else:
        a["maxlength"] = round_down(a["maxlength"], frame)

    minreq = min(minreq_base, a["maxlength"])

    if a["tlength"] == UINT32_MAX:
        a["tlength"] = frac_to_bytes_round_up(96000, 48000, frame)
    a["tlength"] = min(max(a["tlength"], minreq), a["maxlength"])
    a["tlength"] = round_up(a["tlength"], frame)

    if a["minreq"] == UINT32_MAX:
        process = frac_to_bytes_round_up(960, 48000, frame)
        m = round_down(a["tlength"] // 4, frame)
        a["minreq"] = min(process, m)
    a["minreq"] = max(a["minreq"], minreq)

    if a["tlength"] < a["minreq"] + frame:
        a["tlength"] = min(a["minreq"] + frame, a["maxlength"])

    if early:
        latency = a["minreq"]
    elif adjust:
        if a["tlength"] > a["minreq"] * 2:
            latency = min(max_latency,
                          (a["tlength"] - a["minreq"] * 2) // 2)
        else:
            latency = a["minreq"]
        latency = round_down(latency, frame)
        if a["tlength"] >= latency:
            a["tlength"] -= latency
    else:
        if a["tlength"] > a["minreq"] * 2:
            latency = min(max_latency, a["tlength"] - a["minreq"] * 2)
        else:
            latency = a["minreq"]

    if a["tlength"] < latency + 2 * a["minreq"]:
        a["tlength"] = min(latency + 2 * a["minreq"], a["maxlength"])

    a["minreq"] = round_down(a["minreq"], frame)
    if a["minreq"] <= 0:
        a["minreq"] = frame
        a["tlength"] += frame * 2
    if a["tlength"] <= a["minreq"]:
        a["tlength"] = min(a["minreq"] * 2 + frame, a["maxlength"])

    max_prebuf = a["tlength"] + frame - a["minreq"]
    if a["prebuf"] == UINT32_MAX or a["prebuf"] > max_prebuf:
        a["prebuf"] = max_prebuf
    a["prebuf"] = round_down(a["prebuf"], frame)

    lat_num = latency // frame
    lat_denom = rate
    mq_num, mq_denom = MIN_QUANTUM
    if (lat_num * mq_denom) // lat_denom < mq_num:
        lat_num = (mq_num * lat_denom + (mq_denom - 1)) // mq_denom

    return {"tlength": a["tlength"], "prebuf": a["prebuf"],
            "minreq": a["minreq"], "maxlength": a["maxlength"],
            "latency_num": lat_num, "latency_denom": lat_denom}


def my_atou(text):
    """My own pa_atou: reject leading space/`+`/`-`; strip leading zeros
    unless the string starts with lowercase `0x`; strtoul base 0 with a
    full-string check and the UINT32 bound."""
    if text is None or text == "":
        return None
    if text[0] in " \t\n\r+-\x0b\x0c":
        return None
    if text.startswith("0x"):
        body = text[2:]
        if not body or not re.fullmatch(r"[0-9a-fA-F]+", body):
            return None
        val = int(body, 16)
    else:
        body = text.lstrip("0") or "0"
        if not re.fullmatch(r"[0-9]+", body):
            return None
        val = int(body, 10)
    if val > UINT32_MAX:
        return None
    return val


def env_ms(text):
    """The PULSE_LATENCY_MSEC gate: pa_atou < 0 or ms <= 0 is ignored."""
    v = my_atou(text)
    return None if v is None or v <= 0 else v


def predict_leg(latency_ms, process_ms, env_raw, frame):
    """My own model of one attr cell: the CLI request (pacat's own attr
    from --latency-msec/--process-time-msec) is then rewritten by
    patch_buffer_attr (PULSE_LATENCY_MSEC) and resolved by fix_attr."""
    attr = {}
    adjust = False
    if latency_ms is not None:
        attr["tlength"] = usec_to_bytes(latency_ms * 1000, frame)
        adjust = True
    if process_ms is not None:
        attr["minreq"] = usec_to_bytes(process_ms * 1000, frame)
    if env_raw is not None:
        ms = env_ms(env_raw)
        if ms is not None:
            attr = {"maxlength": UINT32_MAX, "tlength": usec_to_bytes(
                ms * 1000, frame), "minreq": UINT32_MAX, "prebuf": UINT32_MAX}
            adjust = True
    return fix_attr(attr, frame, adjust=adjust), env_ms(env_raw)


# ---------------------------------------------------------------------- laws
class Laws:
    def __init__(self):
        self.cells = []

    def L(self, cid, ok, detail=""):
        self.cells.append((cid, "PASS" if ok else "FAIL", detail))

    def BL(self, cid, detail):
        self.cells.append((cid, "BLOCKED", detail))

    def counts(self):
        out = {"PASS": 0, "FAIL": 0, "BLOCKED": 0}
        for _, st, _ in self.cells:
            out[st] += 1
        return out


def derive(receipt):
    """Re-derive every leg from the receipt's recorded fields."""
    L = Laws()
    m = receipt.get("measurements") or {}

    L.L("receipt.mode", receipt.get("mode") == "probe-pulsecli-r96",
        f"mode={receipt.get('mode')!r}")

    # ---- structural: entries present and the declared leg census ----------
    for entry, n in ENTRY_LEGS.items():
        e = m.get(entry)
        if not isinstance(e, dict):
            L.L(f"struct.{entry}.present", False, "entry missing")
            continue
        legs = e.get("legs") or {}
        L.L(f"struct.{entry}.legs", len(legs) == n,
            f"legs={len(legs)} declared={n}")
    total = sum(len((m.get(k) or {}).get("legs") or {}) for k in ENTRY_LEGS)
    # a legitimately blocked entry (named block, no legs) contributes 0
    # legs by design — the census law counts the entries that were judged
    judged = [k for k in ENTRY_LEGS
              if (m.get(k) or {}).get("legs")
              or not (m.get(k) or {}).get("coverage_blocked")]
    declared = sum(ENTRY_LEGS[k] for k in judged)
    L.L("struct.total_legs", total == declared,
        f"total={total} declared={declared} (judged entries: {len(judged)}/5)")

    # ---- shared entry machinery ------------------------------------------
    for entry in ENTRY_LEGS:
        e = m.get(entry) or {}
        gate = e.get("server_gate") or {}
        L.L(f"{entry}.server_gate.rc", gate.get("exit_code") == 0,
            f"rc={gate.get('exit_code')} wall={gate.get('wall_s')}")
        L.L(f"{entry}.server_gate.server_name",
            "Server Name:" in (gate.get("stdout") or ""),
            "pactl info answered the server identity")
        L.L(f"{entry}.own_nodes_after", e.get("own_nodes_after") == [],
            f"own_nodes_after={e.get('own_nodes_after')}")
        sg = e.get("sinks_gone") or {}
        L.L(f"{entry}.sinks_gone", bool(sg) and all(v is True
                                                    for v in sg.values()),
            f"sinks_gone={sg}")
        for tag, leaf in (e.get("unloads") or {}).items():
            L.L(f"{entry}.unload.{tag}",
                leaf.get("exit_code") == 0
                and leaf.get("captured") == leaf.get("verified_index")
                and leaf.get("recycled") is False,
                f"captured={leaf.get('captured')} "
                f"verified={leaf.get('verified_index')} "
                f"rc={leaf.get('exit_code')} recycled={leaf.get('recycled')}")
        L.L(f"{entry}.foreign_r96a_census",
            isinstance(e.get("foreign_r96a_nodes"), list),
            f"foreign r96a nodes observed at entry: "
            f"{e.get('foreign_r96a_nodes')} (census, not armed)")
        srv = e.get("pulse_server") or {}
        L.L(f"{entry}.server_is_pipewire",
            (srv.get("server_name") or "").startswith("PulseAudio (on PipeWire"),
            f"server_name={srv.get('server_name')!r}")
        L.L(f"{entry}.socket", (srv.get("server_string") or "").startswith("/"),
            f"server_string={srv.get('server_string')!r}")

    # ---- 1. avail ---------------------------------------------------------
    e = m.get("pulsecli_avail_r96_probe") or {}
    legs = e.get("legs") or {}
    bins = (legs.get("a_bins") or {}).get("parsed") or {}
    for b in ("pacmd", "pa-info", "pax11publish", "pw-pulse"):
        L.L(f"a_bins.{b}_absent", bins.get(b) == "MISSING",
            f"{b}={bins.get(b)!r}")
    for b in ("pactl", "pacat", "paplay", "parec", "parecord", "pamon"):
        L.L(f"a_bins.{b}_present", bool(bins.get(b))
            and bins.get(b) != "MISSING", f"{b}={bins.get(b)!r}")
    sym = legs.get("a_symlinks") or {}
    for b in ("paplay", "parec", "parecord", "pamon"):
        L.L(f"a_symlinks.{b}", (sym.get(b) or {}).get(
            "same_inode_as_pacat") is True, f"{b}={sym.get(b)}")
    shas = legs.get("a_shas") or {}
    p_sha = (shas.get("pactl") or {}).get("sha256_16")
    c_sha = (shas.get("pacat") or {}).get("sha256_16")
    L.L("a_shas.differ", bool(p_sha) and bool(c_sha) and p_sha != c_sha,
        f"pactl={p_sha} pacat={c_sha}")
    for b in ("pactl", "pacat"):
        leaf = (legs.get("a_version") or {}).get(b) or {}
        L.L(f"a_version.{b}", leaf.get("exit_code") == 0
            and "17.0" in (leaf.get("stdout") or ""),
            f"rc={leaf.get('exit_code')} out={leaf.get('stdout')!r}")
    info = legs.get("a_info") or {}
    L.L("a_info.pipewire_pulse",
        "PulseAudio (on PipeWire" in (info.get("stdout_raw") or ""),
        "Server Name matched pipewire-pulse")
    guard = legs.get("a_pacmd_equiv_guard") or {}
    for verb in ("kill-sink-input", "kill-source-output", "dump"):
        name = f"a_pacmd_{verb}"
        guarded = (guard.get("index0_sink_input") if "sink" in verb else
                   guard.get("index0_source_output")) if verb != "dump" else False
        leaf = legs.get(name)
        if guarded:
            L.BL(name, "an index-0 object existed; refusal leg not fired")
        elif leaf is None:
            L.L(name, False, "leg missing")
        else:
            L.L(f"{name}.refused", leaf.get("exit_code") not in (0, None),
                f"rc={leaf.get('exit_code')}")
            L.L(f"{name}.class", leaf.get("error_class") == "pulse_no_cmd",
                f"class={leaf.get('error_class')!r}")
    for fam, (rc, cls) in SRV_LATTICE.items():
        for rep in (1, 2):
            leaf = legs.get(f"{fam}__r{rep}")
            if leaf is None:
                L.L(f"{fam}__r{rep}", False, "leg missing")
                continue
            L.L(f"{fam}__r{rep}.rc", leaf.get("exit_code") == rc,
                f"rc={leaf.get('exit_code')} want {rc}")
            L.L(f"{fam}__r{rep}.class", leaf.get("error_class") == cls,
                f"class={leaf.get('error_class')!r} want {cls!r}")
    for rep in (1, 2):
        leaf = legs.get(f"b_cookie_devnull__r{rep}") or {}
        L.L(f"b_cookie_devnull__r{rep}.rc", leaf.get("exit_code") == 0,
            f"rc={leaf.get('exit_code')}")
        L.L(f"b_cookie_devnull__r{rep}.warning",
            "Failed to truncate cookie file" in (leaf.get("stderr") or ""),
            f"stderr={leaf.get('stderr')!r}")
        leaf = legs.get(f"b_host_bogus__r{rep}") or {}
        L.L(f"b_host_bogus__r{rep}.rc", leaf.get("exit_code") == 1,
            f"rc={leaf.get('exit_code')}")
        L.L(f"b_host_bogus__r{rep}.class",
            leaf.get("error_class") == "pulse_refused",
            f"class={leaf.get('error_class')!r}")
        L.L(f"b_host_bogus__r{rep}.dns_floor", (leaf.get("wall_s") or 0) >= 2.0,
            f"wall={leaf.get('wall_s')} s (armed floor 2.0)")
        leaf = legs.get(f"b_clientconfig_defaultsink__r{rep}") or {}
        ns_name = ((e.get("unloads") or {}).get("ns") or {}).get("value")
        L.L(f"b_clientconfig_defaultsink__r{rep}.row",
            leaf.get("row_seen") is True, f"row_seen={leaf.get('row_seen')}")
        tgt = ((leaf.get("row") or {}).get("props") or {}).get("target.object")
        L.L(f"b_clientconfig_defaultsink__r{rep}.steered",
            leaf.get("landed_sink_name") == ns_name or tgt == ns_name,
            f"landed={leaf.get('landed_sink_name')!r} target={tgt!r} "
            f"seat={ns_name!r}")

    # ---- 2. target --------------------------------------------------------
    e = m.get("pulsecli_target_r96_probe") or {}
    legs = e.get("legs") or {}
    seat = e.get("seat_sinks") or {}
    ns = (seat.get("ns") or {})
    ns2 = (seat.get("ns2") or {})
    L.L("seat_sinks.recorded", bool(ns.get("name")) and ns.get("index")
        is not None and bool(ns2.get("name")) and ns2.get("index") is not None,
        f"ns={ns} ns2={ns2}")
    L.L("seat_sinks.distinct", ns.get("index") != ns2.get("index"),
        "two distinct seat sinks")

    def landed(name, idx, reps=(1, 2)):
        for rep in reps:
            leaf = legs.get(f"{name}__r{rep}")
            if leaf is None:
                L.L(f"{name}__r{rep}", False, "leg missing")
                continue
            L.L(f"{name}__r{rep}.linked", leaf.get("linked") is True,
                f"linked={leaf.get('linked')}")
            L.L(f"{name}__r{rep}.landed",
                leaf.get("landed_sink_index") == idx,
                f"landed={leaf.get('landed_sink_index')} want {idx}")

    def fallback(name, literal):
        for rep in (1, 2):
            leaf = legs.get(f"{name}__r{rep}")
            if leaf is None:
                L.L(f"{name}__r{rep}", False, "leg missing")
                continue
            L.L(f"{name}__r{rep}.linked", leaf.get("linked") is True,
                f"linked={leaf.get('linked')}")
            L.L(f"{name}__r{rep}.landed_somewhere",
                leaf.get("landed_sink_index") is not None,
                f"landed={leaf.get('landed_sink_index')}")
            tgt = ((leaf.get("row") or {}).get("props") or {}).get(
                "target.object")
            L.L(f"{name}__r{rep}.literal_target", tgt == literal,
                f"target.object={tgt!r} want {literal!r}")

    landed("c_env_sink_seat", ns.get("index"))
    landed("c_env_sink_index2", ns2.get("index"))
    landed("c_flag_seat", ns.get("index"))
    for rep in (1, 2):
        leaf = legs.get(f"c_env_sink_index__r{rep}") or {}
        L.L(f"c_env_sink_index__r{rep}.canonicalized",
            ((leaf.get("row") or {}).get("props") or {}).get(
                "target.object") == ns.get("name"),
            f"target.object="
            f"{((leaf.get('row') or {}).get('props') or {}).get('target.object')!r}"
            f" want {ns.get('name')!r}")
    landed("c_env_sink_index", ns.get("index"))
    fallback("c_env_sink_badindex", "2147483000")
    fallback("c_env_sink_missing", "r96a_bogus_sink_zxqw")
    fallback("c_env_sink_monitor", f"{ns.get('name')}.monitor")
    fallback("c_env_sink_empty", "")
    for name in ("c_env_sink_default", "c_flag_beats_env"):
        for rep in (1, 2):
            leaf = legs.get(f"{name}__r{rep}") or {}
            L.L(f"{name}__r{rep}.linked", leaf.get("linked") is True,
                f"linked={leaf.get('linked')}")
            L.L(f"{name}__r{rep}.landed_somewhere",
                leaf.get("landed_sink_index") is not None,
                f"landed={leaf.get('landed_sink_index')}")
    for rep in (1, 2):
        leaf = legs.get(f"c_source_seat_monitor__r{rep}") or {}
        L.L(f"c_source_seat_monitor__r{rep}.linked",
            leaf.get("linked") is True, f"linked={leaf.get('linked')}")
        L.L(f"c_source_seat_monitor__r{rep}.source_is_sink",
            leaf.get("landed_source_index") == ns.get("index"),
            f"source={leaf.get('landed_source_index')} sink={ns.get('index')}")
    census = e.get("capture_miss_census") or {}
    for rep in (1, 2, 3):
        leaf = legs.get(f"c_source_missing__r{rep}") or {}
        if leaf.get("killed_at_bound"):
            L.BL(f"c_source_missing__r{rep}",
                 "rep hung to the 8 s wall cap — refusal unmeasured")
            continue
        L.L(f"c_source_missing__r{rep}.rc", leaf.get("exit_code") == 1,
            f"rc={leaf.get('exit_code')}")
        L.L(f"c_source_missing__r{rep}.class",
            leaf.get("error_class") == "pulse_no_entity",
            f"class={leaf.get('error_class')!r}")
    L.L("capture_miss_census",
        census.get("measured") == census.get("refused", 0) + census.get("hung", 0)
        and census.get("measured") == 3,
        f"census={census}")
    for rep in (1, 2):
        leaf = legs.get(f"c_pacat_default_monitor__r{rep}") or {}
        L.L(f"c_pacat_default_monitor__r{rep}.row",
            leaf.get("row_seen") is True, f"row_seen={leaf.get('row_seen')}")
        L.L(f"c_pacat_default_monitor__r{rep}.linked",
            leaf.get("linked") is True, f"linked={leaf.get('linked')}")

    # ---- 3. attr ----------------------------------------------------------
    e = m.get("pulsecli_attr_r96_probe") or {}
    legs = e.get("legs") or {}
    attr_cells = {
        "t_default": (None, None, None, 2),
        "t_lat_100": (100, None, None, 2),
        "t_env_100": (None, None, "100", 2),
        "t_env_10": (None, None, "10", 2),
        "t_env_2000": (None, None, "2000", 2),
        "t_env250_flag100": (100, None, "250", 2),
        "t_env100_flag250": (250, None, "100", 2),
        "t_proc_5": (None, 5, None, 2),
        "t_proc_lat_a": (100, 5, None, 2),
        "t_stereo_100": (100, None, None, 4),
        "t_f32_100": (100, None, None, 4),
        "t_f32_default": (None, None, None, 4),
        "t_s24_100": (100, None, None, 3),
        "t_s24_default": (None, None, None, 3),
        "t_maxlength": (None, None, "100000", 2),
    }
    for cell in PARSE_CELLS:
        name = "t_parse_" + (cell.encode().hex() or "empty")
        attr_cells[name] = (None, None, cell, 2)

    fields = ("tlength", "prebuf", "minreq", "maxlength",
              "latency_num", "latency_denom")
    for cell, (lat_ms, proc_ms, env_raw, frame) in attr_cells.items():
        pred, ms = predict_leg(lat_ms, proc_ms, env_raw, frame)
        for rep in (1, 2):
            leaf = legs.get(f"{cell}__r{rep}")
            if leaf is None:
                L.L(f"{cell}__r{rep}", False, "leg missing")
                continue
            if leaf.get("attr_present") is not True:
                L.BL(f"{cell}__r{rep}.measured",
                     "pulse.attr.* never landed within the re-snapshot bound")
                continue
            if leaf.get("frame_size") != frame:
                L.L(f"{cell}__r{rep}.frame_size", False,
                    f"frame={leaf.get('frame_size')} want {frame}")
                continue
            own = {k: pred[k] for k in fields}
            got = leaf.get("attrs_after_resnapshot") or {}
            fixture_pred = leaf.get("predicted") or {}
            L.L(f"{cell}__r{rep}.own_transcription_matches_fixture_prediction",
                all(fixture_pred.get(k) == pred[k] for k in fields),
                f"own={own} fixture={ {k: fixture_pred.get(k) for k in fields} }")
            L.L(f"{cell}__r{rep}.measured_matches_own_transcription",
                all(got.get(k) == pred[k] for k in fields),
                f"measured={ {k: got.get(k) for k in fields} } own={own}")
            if env_raw is not None:
                L.L(f"{cell}__r{rep}.env_ms", leaf.get("env_ms") == ms,
                    f"env_ms={leaf.get('env_ms')} own={ms}")
                if ms is None:
                    L.L(f"{cell}__r{rep}.silent_ignore",
                        (leaf.get("stderr_bytes") or 0) == 0,
                        f"stderr_bytes={leaf.get('stderr_bytes')} "
                        f"tail={leaf.get('stderr_tail')!r}")
    for rep in (1, 2):
        leaf = legs.get(f"t_f32le_invalid__r{rep}") or {}
        L.L(f"t_f32le_invalid__r{rep}.rc", leaf.get("exit_code") == 1,
            f"rc={leaf.get('exit_code')}")
        L.L(f"t_f32le_invalid__r{rep}.class",
            leaf.get("error_class") == "pulse_bad_spec",
            f"class={leaf.get('error_class')!r}")
        L.L(f"t_f32le_invalid__r{rep}.no_row",
            (leaf.get("row") or {}).get("index") is None,
            f"row={leaf.get('row')}")
    # the modulo falsifier: s24 (frame 3) maxlength is 4194303, never 4194304
    for cell in ("t_s24_default", "t_s24_100"):
        got = (legs.get(f"{cell}__r1") or {}).get("attrs_after_resnapshot") or {}
        L.L(f"{cell}.maxlength_modulo_falsifier",
            got.get("maxlength") == round_down(MAXLENGTH, 3) == 4194303,
            f"maxlength={got.get('maxlength')} (mask form would be 4194304)")
    late = e.get("late_attr_census") or {}
    L.L("late_attr_census.legs", late.get("legs") == 64,
        f"late_attr_census={late}")

    # ---- 4. props ---------------------------------------------------------
    e = m.get("pulsecli_props_r96_probe") or {}
    legs = e.get("legs") or {}
    pid = None
    for name, leaf in legs.items():
        tag = ((leaf.get("row") or {}).get("props") or {}).get(
            "application.name") or ""
        mm = re.fullmatch(r"r96a_prop_(\d+)", tag)
        if mm:
            pid = pid or mm.group(1)
    L.L("props.seat_pid", bool(pid), f"seat pid tag={pid!r}")

    def prop_law(cell, key, want_fn, reps=(1, 2)):
        for rep in reps:
            leaf = legs.get(f"{cell}__r{rep}")
            if leaf is None:
                L.L(f"{cell}__r{rep}", False, "leg missing")
                continue
            got = ((leaf.get("row") or {}).get("props") or {}).get(key)
            L.L(f"{cell}__r{rep}.{key}", want_fn(got), f"{key}={got!r}")

    prop_law("p_vector", "application.name",
             lambda v: bool(re.fullmatch(r"r96a_prop_\d+", v or "")))
    prop_law("p_vector", "media.role", lambda v: v == "game")
    prop_law("p_vector", "zzz.invented", lambda v: v == "42")
    prop_law("p_vector", "media.name",
             lambda v: bool(re.fullmatch(r"r96a_streamname_\d+", v or "")))
    prop_law("p_dup", "media.role", lambda v: v == "second")
    prop_law("p_empty", "zzz.empty", lambda v: v == "")
    prop_law("p_streamname_then_prop", "media.name",
             lambda v: bool(re.fullmatch(r"r96a_streamname_\d+_b", v or "")))
    prop_law("p_prop_then_streamname", "media.name",
             lambda v: bool(re.fullmatch(r"r96a_streamname_\d+_a", v or "")))
    prop_law("p_clientname", "application.name",
             lambda v: bool(re.fullmatch(r"r96a_prop_\d+", v or "")))
    prop_law("p_env_loses", "application.name",
             lambda v: bool(re.fullmatch(r"r96a_prop_\d+", v or "")))
    for rep in (1, 2):
        leaf = legs.get(f"p_malformed__r{rep}") or {}
        L.L(f"p_malformed__r{rep}.rc", leaf.get("exit_code") == 1,
            f"rc={leaf.get('exit_code')}")
        L.L(f"p_malformed__r{rep}.class",
            leaf.get("error_class") == "pulse_invalid_property",
            f"class={leaf.get('error_class')!r}")
    for cell in ("p_restore_off_playback", "p_restore_off_capture"):
        for rep in (1, 2):
            leaf = legs.get(f"{cell}__r{rep}") or {}
            before = leaf.get("restore_before") or {}
            after = leaf.get("restore_after") or {}
            if not leaf.get("tag"):
                L.BL(f"{cell}__r{rep}", "restore store unreadable")
                continue
            L.L(f"{cell}__r{rep}.row", leaf.get("row_seen") is True,
                f"row_seen={leaf.get('row_seen')}")
            L.L(f"{cell}__r{rep}.suppressed",
                after.get("rows") == before.get("rows") == 0,
                f"rows {before.get('rows')} -> {after.get('rows')} for tag "
                f"{leaf.get('tag')!r}")

    # ---- 5. cork ----------------------------------------------------------
    e = m.get("pulsecli_cork_r96_probe") or {}
    legs = e.get("legs") or {}
    build = e.get("client_build") or {}
    L.L("client_build.source_sha",
        build.get("source_sha256")
        == "fe2c168352144cd66e6977debd84c3ebee80b9ace80c26c4f0bc37d00a8fc64c",
        f"source_sha256={build.get('source_sha256')}")
    L.L("client_build.binary_sha",
        build.get("binary_sha256")
        == "c3fc4cefed41157e7eac22e0a399ae232e7dfc4e695657ce0ed00b2ca2a46433",
        f"binary_sha256={build.get('binary_sha256')}")
    L.L("client_build.ok", build.get("ok") is True
        and build.get("cc_exit") == 0, f"ok={build.get('ok')} "
        f"cc_exit={build.get('cc_exit')}")
    for rep in (1, 2):
        leaf = legs.get(f"e_cork__r{rep}") or {}
        fl = leaf.get("cork_flip") or {}
        tap = leaf.get("tap") or {}
        L.L(f"e_cork__r{rep}.corked_witness",
            (fl.get("corked_true_samples") or 0) >= 1, f"flip={fl}")
        L.L(f"e_cork__r{rep}.uncorked_witness",
            (fl.get("uncorked_samples") or 0) >= 1, f"flip={fl}")
        L.L(f"e_cork__r{rep}.onset_recorded",
            fl.get("first_corked_t") is not None
            and fl.get("first_uncorked_t") is not None
            and fl["first_uncorked_t"] > fl["first_corked_t"],
            f"t {fl.get('first_corked_t')} -> {fl.get('first_uncorked_t')}")
        L.L(f"e_cork__r{rep}.flow_gate",
            (tap.get("nonzero_frames") or 0) > 0, f"tap={tap}")
        L.L(f"e_cork__r{rep}.peak", (tap.get("peak") or 0) > 0,
            f"tap={tap}")
    for rep in (1, 2, 3):
        leaf = legs.get(f"e_trigger__r{rep}") or {}
        tap = leaf.get("tap") or {}
        L.L(f"e_trigger__r{rep}.silent",
            tap.get("nonzero_frames") == 0 and tap.get("peak") == 0,
            f"tap={tap}")
        L.L(f"e_trigger__r{rep}.trigger_event",
            any(ev.get("line", "").startswith("trigger")
                for ev in (leaf.get("events") or [])),
            "client reported the trigger event")
    for cell, reps, lo, hi in (
            ("e_prebuf_default_slow", (1, 2), 30000, None),
            ("e_prebuf_zero_slow", (1, 2, 3), None, 12000),
            ("e_prebuf_zero_fast", (1, 2), 20000, None),
            ("e_prebuf_default_fast", (1, 2), 30000, None)):
        for rep in reps:
            leaf = legs.get(f"{cell}__r{rep}") or {}
            n = (leaf.get("tap") or {}).get("nonzero_frames")
            ok = (n is not None and (lo is None or n >= lo)
                  and (hi is None or n <= hi))
            L.L(f"{cell}__r{rep}", ok, f"nonzero_frames={n} "
                f"bounds=({lo},{hi})")
    for rep in (1, 2):
        leaf = legs.get(f"e_record_cork__r{rep}") or {}
        L.L(f"e_record_cork__r{rep}.corked_readable_zero",
            "bytes=0" in (leaf.get("readable_corked_line") or ""),
            f"line={leaf.get('readable_corked_line')!r}")
        L.L(f"e_record_cork__r{rep}.uncorked_peak",
            (leaf.get("readable_peak") or 0) >= 80000,
            f"peak={leaf.get('readable_peak')}")
        L.L(f"e_record_cork__r{rep}.drained",
            bool(leaf.get("drained_bytes")), f"drained={leaf.get('drained_bytes')}")
        L.L(f"e_record_cork__r{rep}.corked_snapshot",
            any(x.get("corked") is True
                for x in (leaf.get("corked_samples") or [])),
            "server-side corked snapshot taken")
    for rep in (1, 2):
        leaf = legs.get(f"e_latency_query__r{rep}") or {}
        rcs = leaf.get("latency_rcs") or []
        L.L(f"e_latency_query__r{rep}.call_count",
            (leaf.get("latency_samples") or 0) >= 3,
            f"samples={leaf.get('latency_samples')}")
        L.L(f"e_latency_query__r{rep}.nodata",
            bool(rcs) and all(rc == -16 for rc in rcs), f"rcs={rcs}")
        L.L(f"e_latency_query__r{rep}.introspection_zeros",
            bool(leaf.get("introspection_latency_fields"))
            and all(f.get("buffer_latency_usec") == 0.0
                    and f.get("sink_latency_usec") == 0.0
                    for f in leaf["introspection_latency_fields"]),
            f"fields={leaf.get('introspection_latency_fields')}")
    for rep in (1, 2):
        leaf = legs.get(f"e_subscribe__r{rep}") or {}
        L.L(f"e_subscribe__r{rep}.one_change",
            leaf.get("changes_at_uncork") == 1,
            f"after={leaf.get('changes_at_uncork')} "
            f"before={leaf.get('changes_before_uncork')}")
        L.L(f"e_subscribe__r{rep}.new_event",
            (leaf.get("new_events") or 0) >= 1, f"new={leaf.get('new_events')}")
        L.L(f"e_subscribe__r{rep}.foreign_censused",
            isinstance(leaf.get("foreign_sink_input_events"), int)
            and leaf["foreign_sink_input_events"] >= 0,
            f"foreign={leaf.get('foreign_sink_input_events')}")
    for rep in (1, 2):
        leaf = legs.get(f"e_native_corked__r{rep}") or {}
        L.L(f"e_native_corked__r{rep}.row", (leaf.get("row") or {}).get(
            "index") is not None, f"row={leaf.get('row')}")
        L.L(f"e_native_corked__r{rep}.no_pulse_corked_prop",
            leaf.get("has_pulse_corked") is False,
            f"has_pulse_corked={leaf.get('has_pulse_corked')}")
        if leaf.get("projection_agrees") is True:
            L.L(f"e_native_corked__r{rep}.projection",
                True, f"Corked={leaf.get('corked_field')} state="
                f"{leaf.get('node_state_before')}->"
                f"{leaf.get('node_state_after')}")
        else:
            L.BL(f"e_native_corked__r{rep}.projection",
                 f"Corked={leaf.get('corked_field')!r} vs live "
                 f"{leaf.get('node_state_before')!r}->"
                 f"{leaf.get('node_state_after')!r} — value recorded, "
                 "not armed (cached dev_info)")

    # ---- entry-level named blocks are BLOCKED, never PASS, never FAIL -----
    # An entry that carries a named entry-level block (no legs at all +
    # a coverage_blocked reason) cannot be law-judged: every cell that
    # would have judged it is a BLOCKED cell instead. This is the r96
    # family's own discipline (`_pulsecli_r96_block`) applied to the law
    # set: a wedged daemon or a failed instrument build must not read as
    # a green (and must not read as a red either — it is unmeasured).
    for entry in ENTRY_LEGS:
        e = m.get(entry) or {}
        legs = e.get("legs") or {}
        cb = e.get("coverage_blocked") or []
        if legs or not cb:
            continue
        note = f"entry-level named block: {cb[0][:200]}"
        L.cells = [(cell, "BLOCKED" if owns(entry, cell) else st,
                    note if owns(entry, cell) else det)
                   for cell, st, det in L.cells]
        L.BL(f"{entry}.entry_block", note)

    # a fully blocked receipt (every entry a named block) cannot arm the
    # global leg census either
    if all(not (m.get(k) or {}).get("legs")
           and (m.get(k) or {}).get("coverage_blocked") for k in ENTRY_LEGS):
        L.cells = [(cell, "BLOCKED" if cell == "struct.total_legs" else st,
                    "every entry is a named entry-level block"
                    if cell == "struct.total_legs" else det)
                   for cell, st, det in L.cells]

    # ---- receipt-level cross-checks (the lists are NOT law inputs) --------
    derived_fail = sorted({c.split("__r")[0].split(".")[0]
                           for c, st, _ in L.cells if st == "FAIL"})
    receipt_fail = sorted(k for k, v in m.items()
                          if isinstance(v, dict) and v.get("failures"))
    L.L("receipt.failures_agree",
        (len(receipt_fail) == 0) == (not derived_fail),
        f"receipt failures={receipt_fail} derived FAIL cells="
        f"{len([1 for _, st, _ in L.cells if st == 'FAIL'])}")
    receipt_block_entries = sorted(
        k for k in ENTRY_LEGS if (m.get(k) or {}).get("coverage_blocked"))
    derived_block_entries = sorted(
        k for k in ENTRY_LEGS
        if any(st == "BLOCKED" and owns(k, cell) for cell, st, _ in L.cells))
    L.L("receipt.blocked_agree",
        receipt_block_entries == derived_block_entries,
        f"receipt blocked entries={receipt_block_entries} "
        f"derived={derived_block_entries}")
    return L


# --------------------------------------------------------------- cross-run walk
VOLATILE = re.compile(
    r"(wall_s|utc|loadavg|contention|host|pulse_server|server_string|index|"
    r"module_id|client_build\.binary|tag|oracle|path|recycled|"
    r"first_.*_t|_t$|exit_code|unloads|captured|verified|argv|env_keys|"
    r"own_pid|fixture_runs|nsec|"
    r"foreign_sink_input_events|"
    r"foreign_r96a_nodes|own_sink_input_indexes|"
    r"row\.|inventory|late_attr_census|capture_miss_census|landed_|socket|"
    r"latency_usec|sink_latency_usec|client_build\.source)")


def walk(a, b, path="", out=None):
    if out is None:
        out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            walk(a.get(k), b.get(k), f"{path}.{k}", out)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append((path, f"len {len(a)} vs {len(b)}"))
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                walk(x, y, f"{path}[{i}]", out)
    else:
        if a != b and not VOLATILE.search(path):
            out.append((path, f"{a!r} vs {b!r}"))
    return out


def compare(path_a, path_b):
    ra = json.load(open(path_a))["measurements"]
    rb = json.load(open(path_b))["measurements"]
    diffs = walk(ra, rb)
    leaves = []

    def count(x, p=""):
        if isinstance(x, dict):
            for k, v in x.items():
                count(v, f"{p}.{k}")
        elif isinstance(x, list):
            for i, v in enumerate(x):
                count(v, f"{p}[{i}]")
        else:
            leaves.append(p)

    count(ra)
    print(json.dumps({"leaf_comparisons": len(leaves),
                      "differences": len(diffs),
                      "diff_sample": diffs[:40]}, indent=1))


# ------------------------------------------------------------------- forgeries
def forgeries(receipt):
    base = copy.deepcopy(receipt)
    cases = {}

    def mutate(name, fn):
        r = copy.deepcopy(base)
        fn(r)
        cases[name] = r

    mutate("none", lambda r: None)
    mutate("blank-lists", lambda r: [v.pop("failures", None) or
                                     v.pop("coverage_blocked", None)
                                     for v in r["measurements"].values()])
    mutate("forge-attr-measured",
           lambda r: r["measurements"]["pulsecli_attr_r96_probe"]["legs"]
           ["t_lat_100__r1"]["attrs_after_resnapshot"].update({"tlength": 6721}))
    mutate("forge-attr-predicted",
           lambda r: r["measurements"]["pulsecli_attr_r96_probe"]["legs"]
           ["t_env_10__r1"]["predicted"].update({"prebuf": 1027}))
    mutate("forge-parse",
           lambda r: r["measurements"]["pulsecli_attr_r96_probe"]["legs"]
           ["t_parse_30783634__r1"].update({"env_ms": 101}))
    mutate("pop-leg",
           lambda r: r["measurements"]["pulsecli_props_r96_probe"]["legs"]
           .pop("p_dup__r2"))
    mutate("forge-build",
           lambda r: r["measurements"]["pulsecli_cork_r96_probe"]
           ["client_build"].update({"binary_sha256": "0" * 64}))
    mutate("forge-census",
           lambda r: r["measurements"]["pulsecli_target_r96_probe"]
           ["sinks_gone"].update({"ns": False}))
    mutate("forge-native-class",
           lambda r: r["measurements"]["pulsecli_cork_r96_probe"]["legs"]
           ["e_native_corked__r1"].update({"has_pulse_corked": True}))
    mutate("forge-corked-flip",
           lambda r: r["measurements"]["pulsecli_cork_r96_probe"]["legs"]
           ["e_cork__r1"]["cork_flip"].update({"corked_true_samples": 0}))
    mutate("forge-latency",
           lambda r: r["measurements"]["pulsecli_cork_r96_probe"]["legs"]
           ["e_latency_query__r1"].update({"latency_rcs": [0, 0, 0]}))
    mutate("forge-restore",
           lambda r: r["measurements"]["pulsecli_props_r96_probe"]["legs"]
           ["p_restore_off_playback__r1"].update(
               {"restore_after": {"path": "x", "rows": 1}}))
    return cases


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("receipts", nargs="*")
    ap.add_argument("--compare", nargs=2)
    ap.add_argument("--forge", metavar="RECEIPT")
    ap.add_argument("--json-out")
    args = ap.parse_args()

    if args.compare:
        compare(*args.compare)
        return 0

    if args.forge:
        r = json.load(open(args.forge))
        summary = {}
        for name, mutated in forgeries(r).items():
            L = derive(mutated)
            c = L.counts()
            fails = sorted({cell for cell, st, _ in L.cells if st == "FAIL"})
            blocks = sorted({cell for cell, st, _ in L.cells if st == "BLOCKED"})
            summary[name] = {"counts": c, "fails": fails[:12],
                             "n_fails": len(fails), "n_blocks": len(blocks)}
        print(json.dumps(summary, indent=1))
        return 0

    report = {}
    for path in args.receipts:
        r = json.load(open(path))
        L = derive(r)
        c = L.counts()
        report[path] = {
            "counts": c,
            "legs": sum(len((r["measurements"].get(k) or {}).get("legs") or {})
                        for k in ENTRY_LEGS),
            "fails": [{"cell": cell, "detail": det}
                      for cell, st, det in L.cells if st == "FAIL"],
            "blocks": [{"cell": cell, "detail": det}
                       for cell, st, det in L.cells if st == "BLOCKED"],
        }
        print(f"{path}: legs={report[path]['legs']} "
              f"laws={c['PASS'] + c['FAIL'] + c['BLOCKED']} "
              f"PASS={c['PASS']} FAIL={c['FAIL']} BLOCKED={c['BLOCKED']}")
        for cell, st, det in L.cells:
            if st == "FAIL":
                print(f"   FAIL {cell}: {det}")
    if args.json_out:
        open(args.json_out, "w").write(json.dumps(report, indent=1) + "\n")
    return 0 if all(v["counts"]["FAIL"] == 0 for v in report.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
