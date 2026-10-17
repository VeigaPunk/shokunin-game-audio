#!/usr/bin/env python3
"""r92 verifier — independent law re-derivation for --probe-filterchain-r92.

Reads a measurements.json receipt (and, when --scratch is given, the raw
WAV captures the receipt came from) and re-derives every armed cell of the
r92 family from the recorded data.  It never imports the fixture and never
reads the entry's own `failures` list as a detector (that list is only
cross-checked at the end).

Per-leg verdicts: PASS / FAIL / BLOCKED (BLOCKED = the leg's evidence is
absent behind a named gate/block, i.e. never green).

Usage: python3 r92v_laws.py <receipt.json> [--scratch DIR] [--json OUT]
"""
import argparse
import json
import math
import os
import struct
import sys

import numpy as np

RATE = 48000
FREQS = (200, 1000, 4000, 12000, 20000)
WIN = 24000
BLOCKSIZE = 1024
ENTRIES = ("filterchain_arm_r92_probe", "filterchain_dsp_r92_probe",
           "filterchain_ir_r92_probe", "filterchain_wpx_r92_probe")


# ------------------------------------------------------------------ raw WAV
def wav_read(path):
    raw = open(path, "rb").read()
    if raw[:4] != b"RIFF" or raw[8:12] != b"WAVE":
        raise ValueError("not RIFF/WAVE")
    pos, fmt, data = 12, None, None
    while pos + 8 <= len(raw):
        cid, sz = raw[pos:pos + 4], struct.unpack("<I", raw[pos + 4:pos + 8])[0]
        body = raw[pos + 8:pos + 8 + sz]
        if cid == b"fmt ":
            tag, ch, rate, _br, _ba, bits = struct.unpack("<HHIIHH", body[:16])
            fmt = (tag, ch, rate, bits)
        elif cid == b"data":
            data = body
        pos += 8 + sz + (sz & 1)
    tag, ch, rate, bits = fmt
    if tag == 1 and bits == 16:
        x = np.frombuffer(data, "<i2").astype(np.float64) / 32768.0
    elif tag == 1 and bits == 24:
        u = np.frombuffer(data, np.uint8).reshape(-1, 3).astype(np.uint32)
        v = (u[:, 0] | (u[:, 1] << 8) | (u[:, 2] << 16)).astype(np.int32)
        v = np.where(v & 0x800000, v - 0x1000000, v)
        x = v.astype(np.float64) / 8388608.0
    elif tag == 3 and bits == 32:
        x = np.frombuffer(data, "<f4").astype(np.float64)
    else:
        raise ValueError("unsupported fmt tag=%s bits=%s" % (tag, bits))
    return {"x": x, "rate": rate, "ch": ch, "bytes": len(raw)}


def best_window(x, win=WIN, step=2400):
    if len(x) <= win:
        return x, 0
    best, bi = -1.0, 0
    for i in range(0, len(x) - win + 1, step):
        seg = x[i:i + win]
        r = float(np.dot(seg, seg))
        if r > best:
            best, bi = r, i
    return x[bi:bi + win], bi


def dft_mag(x, freqs):
    n = len(x)
    t = np.arange(n)
    out = {}
    for f in freqs:
        w = 2 * np.pi * f / RATE
        re = float(np.dot(x, np.cos(w * t)))
        im = float(np.dot(x, np.sin(w * t)))
        out[int(f)] = 2.0 * math.hypot(re, im) / n
    return out


def gain_db(mo, mr, floor=1e-15):
    out = {}
    for k in mo:
        a, b = mo[k], mr.get(k, 0.0)
        if not (math.isfinite(a) and math.isfinite(b)):
            out[str(k)] = None
        elif a <= floor and b <= floor:
            out[str(k)] = None
        else:
            out[str(k)] = round(20 * math.log10(max(floor, a) / max(floor, b)), 3)
    return out


# ---------------------------------------------------------------- RBJ (own)
def rbj_gains(label, f0, q, gain_db_=0.0, rate=RATE, freqs=FREQS):
    if q == 0:
        q = 0.707
    A = 10.0 ** (gain_db_ / 40.0)
    w0 = 2 * math.pi * f0 / rate
    cw, sw = math.cos(w0), math.sin(w0)
    al = sw / (2 * q)
    if label == "lp":
        b, a = [(1 - cw) / 2, 1 - cw, (1 - cw) / 2], [1 + al, -2 * cw, 1 - al]
    elif label == "pk":
        b, a = [1 + al * A, -2 * cw, 1 - al * A], [1 + al / A, -2 * cw, 1 - al / A]
    elif label == "nt":
        b, a = [1, -2 * cw, 1], [1 + al, -2 * cw, 1 - al]
    else:
        raise ValueError(label)
    b = np.array(b, dtype=np.float64) / a[0]
    a = np.array(a, dtype=np.float64) / a[0]
    out = {}
    for f in freqs:
        z = np.exp(-2j * np.pi * f / rate)
        h = (b[0] + b[1] * z + b[2] * z * z) / (a[0] + a[1] * z + a[2] * z * z)
        out[int(f)] = round(20 * math.log10(abs(h)), 3)
    return out


def shift_ok(delta, want, tol=2):
    if delta is None:
        return False
    return any(abs(delta - (want + k * BLOCKSIZE)) <= tol for k in range(-4, 5))


# ------------------------------------------------------------------ law book
class Laws:
    def __init__(self):
        self.rows = []          # (leg, law_id, status, detail)
        self.legs = {}          # leg_key -> [statuses]
        self.absent = set()     # leg keys absent from this receipt

    def law(self, leg, lid, ok, detail="", blocked=False):
        status = "PASS" if ok else ("BLOCKED" if blocked else "FAIL")
        self.rows.append((leg, lid, status, detail))
        self.legs.setdefault(leg, []).append((lid, status, detail))
        return ok

    def leg_status(self, leg):
        st = self.legs.get(leg) or []
        if not st:
            return "FAIL", "no law recorded for this leg"
        if any(s == "FAIL" for _, s, _ in st):
            return "FAIL", "; ".join(f"{l}: {d}" for l, s, d in st if s == "FAIL")
        if any(s == "BLOCKED" for _, s, _ in st):
            return "BLOCKED", "; ".join(f"{l}: {d}" for l, s, d in st if s == "BLOCKED")
        return "PASS", ""

    def settle(self):
        """An absent leg can never read red: its FAILs become BLOCKED."""
        if not self.absent:
            return
        rows, legs = [], {}
        for leg, lid, st, det in self.rows:
            if leg in self.absent and st == "FAIL":
                st = "BLOCKED"
            rows.append((leg, lid, st, det))
            legs.setdefault(leg, []).append((lid, st, det))
        self.rows, self.legs = rows, legs

    def summary(self):
        self.settle()
        n = len(self.rows)
        p = sum(1 for _, _, s, _ in self.rows if s == "PASS")
        f = sum(1 for _, _, s, _ in self.rows if s == "FAIL")
        b = sum(1 for _, _, s, _ in self.rows if s == "BLOCKED")
        return n, p, f, b


def approx(a, b, tol):
    return a is not None and b is not None and abs(a - b) <= tol


class Legs(dict):
    """A receipt's leg dict that records a BLOCKED law for an absent leg
    (a receipt that predates a leg must never read as a silent green)."""

    def __init__(self, data, laws, entry):
        super().__init__(data or {})
        self.laws = laws
        self.entry = entry

    def __missing__(self, key):
        self.laws.absent.add(key)
        self.laws.law(key, f"{key}.present_in_receipt", False,
                      f"leg absent from the {self.entry} receipt", blocked=True)
        return {}


def close_set(a, b, probes, tol):
    bad = []
    for p in probes:
        k = str(p)
        if a.get(k) is None or b.get(k) is None or abs(a[k] - b[k]) > tol:
            bad.append({"hz": p, "a": a.get(k), "b": b.get(k)})
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("receipt")
    ap.add_argument("--scratch", default=None)
    ap.add_argument("--json", default=None)
    ap.add_argument("--tag", default="run")
    args = ap.parse_args()

    rec = json.load(open(args.receipt))
    m = rec["measurements"]
    L = Laws()
    cells = {}

    # ------------------------------------------------ top-level / entry hygiene
    L.law("__mode__", "mode", rec.get("mode") == "probe-filterchain-r92",
          f"mode={rec.get('mode')}")
    for e in ENTRIES:
        ent = m[e]
        L.law(e + ".hygiene", f"{e}.daemon_ok",
              (ent.get("daemon") or {}).get("ok") is True,
              json.dumps(ent.get("daemon")), blocked=True)
        L.law(e + ".hygiene", f"{e}.tools_present",
              all((ent.get("tools") or {}).values()),
              json.dumps(ent.get("tools")), blocked=True)
        L.law(e + ".hygiene", f"{e}.own_nodes_after_empty",
              ent.get("own_nodes_after") == [],
              f"own_nodes_after={ent.get('own_nodes_after')}")
        L.law(e + ".hygiene", f"{e}.live_after_procs_empty",
              (ent.get("live_after") or {}).get("procs") == [],
              f"live_after={ent.get('live_after')}")
        L.law(e + ".hygiene", f"{e}.no_coverage_block",
              not ent.get("coverage_blocked"),
              json.dumps(ent.get("coverage_blocked")))
        L.law(e + ".hygiene", f"{e}.failures_empty_crosscheck",
              not ent.get("failures"),
              json.dumps(ent.get("failures")))
        if e != "filterchain_wpx_r92_probe":
            gone = ent.get("sinks_gone") or {}
            L.law(e + ".hygiene", f"{e}.sinks_gone_all_true",
                  bool(gone) and all(v is True for v in gone.values()),
                  json.dumps({k: v for k, v in gone.items() if v is not True}))
        cells[f"{e}.host_is_quiet"] = (ent.get("contention") or {}).get("host_is_quiet")
        cells[f"{e}.fixture_runs"] = (ent.get("contention") or {}).get("fixture_runs")
        cells[f"{e}.foreign_r92a_nodes"] = ent.get("foreign_r92a_nodes")
        cells[f"{e}.reader_tries"] = ent.get("reader_tries")

    # ============================================================ entry 1: arm
    a = Legs(m["filterchain_arm_r92_probe"]["legs"], L, "arm")
    cells["arm_leg_keys"] = sorted(a.keys())

    l = a["a_lifetime"]
    sh = l.get("live_shape") or {}
    L.law("a_lifetime", "a_lifetime.no_gate", not l.get("gate"), str(l.get("gate")), blocked=bool(l.get("gate")))
    L.law("a_lifetime", "a_lifetime.both_nodes", sh.get("nodes") == [True, True], str(sh.get("nodes")))
    L.law("a_lifetime", "a_lifetime.capture_class", sh.get("capture_class") == "Audio/Sink", str(sh.get("capture_class")))
    L.law("a_lifetime", "a_lifetime.capture_ports",
          sorted(sh.get("capture_ports") or []) == ["monitor_MONO", "playback_MONO"],
          str(sh.get("capture_ports")))
    L.law("a_lifetime", "a_lifetime.own_edges_empty", sh.get("own_edges") == [], str(sh.get("own_edges")))
    L.law("a_lifetime", "a_lifetime.id_unload_refused",
          (l.get("id_unload") or {}).get("error_class") == "fc92_unload_unknown",
          str((l.get("id_unload") or {}).get("error_class")))
    L.law("a_lifetime", "a_lifetime.nodes_survive_id_unload",
          (l.get("after_id_unload") or {}).get("capture_present") is True
          and (l.get("after_id_unload") or {}).get("playback_present") is True,
          str(l.get("after_id_unload")))
    L.law("a_lifetime", "a_lifetime.var_unload_destroys",
          l.get("var_unload") is not None
          and (l.get("after_var_unload") or {}).get("capture_present") is False
          and (l.get("after_var_unload") or {}).get("playback_present") is False,
          str(l.get("after_var_unload")))
    L.law("a_lifetime", "a_lifetime.reload_live",
          (l.get("after_reload") or {}).get("capture_present") is True,
          str(l.get("after_reload")))
    ae = l.get("after_session_exit") or {}
    L.law("a_lifetime", "a_lifetime.client_local",
          ae.get("capture_present") is False and ae.get("playback_present") is False
          and ae.get("reload_present") is False, str(ae))
    cells["a_lifetime"] = {"id_class": (l.get("id_unload") or {}).get("error_class"),
                           "live_nodes": sh.get("nodes"), "after_exit": ae}

    l = a["a_ports_none"]
    L.law("a_ports_none", "a_ports_none.no_gate", not l.get("gate"), str(l.get("gate")), blocked=bool(l.get("gate")))
    L.law("a_ports_none", "a_ports_none.loaded", l.get("loaded") is True, str(l.get("loaded")))
    L.law("a_ports_none", "a_ports_none.class", l.get("capture_class") == "Stream/Input/Audio", str(l.get("capture_class")))
    L.law("a_ports_none", "a_ports_none.no_playback_port",
          "playback_MONO" not in (l.get("capture_ports") or []), str(l.get("capture_ports")))
    L.law("a_ports_none", "a_ports_none.feed_refused",
          (l.get("feed_link") or {}).get("rc") not in (0, None), str(l.get("feed_link")))
    cells["a_ports_none"] = {"loaded": l.get("loaded"), "class": l.get("capture_class"),
                             "ports": l.get("capture_ports"), "feed_rc": (l.get("feed_link") or {}).get("rc")}

    l = a["a_ports_sink"]
    L.law("a_ports_sink", "a_ports_sink.no_gate", not l.get("gate"), str(l.get("gate")), blocked=bool(l.get("gate")))
    L.law("a_ports_sink", "a_ports_sink.loaded", l.get("loaded") is True, str(l.get("loaded")))
    L.law("a_ports_sink", "a_ports_sink.class", l.get("capture_class") == "Audio/Sink", str(l.get("capture_class")))
    L.law("a_ports_sink", "a_ports_sink.ports",
          sorted(l.get("capture_ports") or []) == ["monitor_MONO", "playback_MONO"], str(l.get("capture_ports")))
    L.law("a_ports_sink", "a_ports_sink.feed_ok", (l.get("feed_link") or {}).get("rc") == 0, str(l.get("feed_link")))
    L.law("a_ports_sink", "a_ports_sink.own_edges_empty", l.get("own_edges") == [], str(l.get("own_edges")))
    cells["a_ports_sink"] = {"loaded": l.get("loaded"), "class": l.get("capture_class"),
                             "ports": l.get("capture_ports"), "feed_rc": (l.get("feed_link") or {}).get("rc")}

    L.law("a_links_quoted", "a_links_quoted.loaded", a["a_links_quoted"].get("loaded") is True,
          str(a["a_links_quoted"].get("error_class")))
    want_cls = {"a_links_bare": "fc92_props_parse", "a_hash_uri": "fc92_props_parse",
                "a_graph_num": "fc92_graph_not_object", "a_graph_empty": "fc92_graph_no_nodes",
                "a_bad_label": "fc92_label_missing", "a_bad_type": "fc92_type_missing",
                "a_ffmpeg": "fc92_type_missing", "a_ladspa": "fc92_ladspa_missing",
                "a_bare_spaced": "fc92_props_parse"}
    for tag, cls in want_cls.items():
        l = a[tag]
        L.law(tag, tag + ".refused", l.get("loaded") is False, f"loaded={l.get('loaded')}")
        L.law(tag, tag + ".class", l.get("error_class") == cls,
              f"got={l.get('error_class')} hit={l.get('error_hit')}")
        cells[tag] = {"loaded": l.get("loaded"), "class": l.get("error_class")}
    l = a["a_quoted_spaced"]
    L.law("a_quoted_spaced", "a_quoted_spaced.loaded_clean",
          l.get("loaded") is True and not l.get("warn_lines"),
          f"loaded={l.get('loaded')} warn={l.get('warn_lines')}")
    l = a["a_typo_ctl"]
    L.law("a_typo_ctl", "a_typo_ctl.warning_only",
          l.get("loaded") is True and l.get("error_class") == "fc92_control_typo",
          f"loaded={l.get('loaded')} class={l.get('error_class')}")
    cells["a_quoted_spaced"] = {"loaded": l.get("loaded"), "warns": len(l.get("warn_lines") or [])}

    for tag in ("a_ebur128", "a_sofa", "a_sofa_cfg"):
        L.law(tag, tag + ".loaded", a[tag].get("loaded") is True, str(a[tag].get("error_class")))
    l = a["a_ebur128_bad"]
    L.law("a_ebur128_bad", "a_ebur128_bad.exact_label",
          l.get("loaded") is False and l.get("error_class") == "fc92_label_missing",
          f"loaded={l.get('loaded')} class={l.get('error_class')}")

    labs = a["a_labels"]
    rows = sorted(k for k in labs if "#" in k)
    L.law("a_labels", "a_labels.row_count", len(rows) == 64, f"rows={len(rows)}")
    ok_labs = sorted({k.split("#")[0] for k in rows if k.split("#")[0] in (
        "abs", "bq_allpass", "bq_bandpass", "bq_highpass", "bq_highshelf", "bq_lowpass",
        "bq_lowshelf", "bq_notch", "bq_peaking", "bq_raw", "clamp", "convolver", "copy",
        "dcblock", "delay", "exp", "invert", "linear", "log", "max", "mixer", "mult",
        "noisegate", "param_eq", "recip", "sine")})
    fail_labs = sorted({k.split("#")[0] for k in rows if k.split("#")[0] not in ok_labs})
    for k in rows:
        lab, rep = k.split("#")
        row = labs[k]
        if lab in ok_labs:
            L.law("a_labels", f"label:{lab}#{rep}.loaded", row.get("loaded") is True,
                  f"class={row.get('error_class')}")
        else:
            L.law("a_labels", f"label:{lab}#{rep}.refused",
                  row.get("loaded") is False and row.get("error_class") == "fc92_label_missing",
                  f"loaded={row.get('loaded')} class={row.get('error_class')}")
    L.law("a_labels", "a_labels.ok_half_count", len(ok_labs) == 26, f"ok={len(ok_labs)}")
    L.law("a_labels", "a_labels.fail_half_count", len(fail_labs) == 6, f"fail={fail_labs}")
    cells["a_labels"] = {"rows": len(rows), "ok_labels": len(ok_labs), "fail_labels": fail_labs}

    l = a["a_eof_null"]
    L.law("a_eof_null", "a_eof_null.sigabrt", l.get("exit_code") == -6, f"rc={l.get('exit_code')} sig={l.get('signal')}")
    L.law("a_eof_null", "a_eof_null.abort_class", l.get("error_class") == "fc92_abort_loop",
          f"class={l.get('error_class')}")
    l = a["a_eof_pipe"]
    L.law("a_eof_pipe", "a_eof_pipe.hangs", l.get("killed_at_bound") is True, f"rc={l.get('exit_code')}")
    l = a["a_quit"]
    L.law("a_quit", "a_quit.clean_exit", l.get("exit_code") == 0 and not l.get("killed_at_bound"),
          f"rc={l.get('exit_code')} killed={l.get('killed_at_bound')}")
    cells["eof"] = {"null_rc": a["a_eof_null"].get("exit_code"), "null_class": a["a_eof_null"].get("error_class"),
                    "pipe_killed": a["a_eof_pipe"].get("killed_at_bound"), "quit_rc": a["a_quit"].get("exit_code")}

    for tag in ("a_load_noconfig", "a_load_missing"):
        l = a[tag]
        st = l.get("log_stats") or {}
        L.law(tag, tag + ".silent_load",
              l.get("loaded") is True and st.get("E") == 0 and st.get("W") == 0,
              f"loaded={l.get('loaded')} E={st.get('E')} W={st.get('W')}")
        cells[tag] = {"loaded": l.get("loaded"), "E": st.get("E"), "W": st.get("W")}
    l = a["a_load_dbg5"]
    st = l.get("log_stats") or {}
    L.law("a_load_dbg5", "a_load_dbg5.silent_debug5",
          l.get("loaded") is True and st.get("E") == 0 and st.get("W") == 0 and (st.get("lines") or 0) >= 500,
          f"loaded={l.get('loaded')} E={st.get('E')} W={st.get('W')} lines={st.get('lines')}")
    cells["a_load_dbg5"] = {"loaded": l.get("loaded"), "E": st.get("E"), "W": st.get("W"), "lines": st.get("lines")}

    # ============================================================ entry 2: dsp
    d = Legs(m["filterchain_dsp_r92_probe"]["legs"], L, "dsp")
    DSP_TAGS = ("d_copy", "d_lp", "d_pk6", "d_peq", "d_nt", "d_f0", "d_fneg",
                "d_fhi", "d_g20", "d_g20x", "d_gneg", "d_gnegx", "d_q707",
                "d_q10", "d_q1e9", "d_qneg", "d_raw", "d_coeff", "d_lp_g6",
                "d_gneg140")
    cells["dsp_leg_keys"] = sorted(d.keys())
    for tag in sorted(set(list(d.keys()) + list(DSP_TAGS))):
        l = d[tag]
        if l.get("gate"):
            L.law(tag, tag + ".measured", False, f"gate={l['gate']}", blocked=True)
            continue
        if not l.get("valid"):
            L.law(tag, tag + ".measured", False,
                  f"valid=False links_ok={l.get('links_ok')}",
                  blocked=not l.get("links_ok"))
            continue
        L.law(tag, tag + ".measured", True, "")

    def g(tag):
        return (d[tag].get("analysis") or {}).get("gain_db") or {}

    for tag in sorted(set(list(d.keys()) + list(DSP_TAGS))):
        cells["gain_" + tag] = g(tag)

    gc = g("d_copy")
    L.law("d_copy", "d_copy.five_probes", len(gc) == 5, str(sorted(gc)))
    L.law("d_copy", "d_copy.unity", len(gc) == 5 and all(abs(v) <= 0.05 for v in gc.values() if v is not None), str(gc))
    ref = rbj_gains("lp", 1000, 0.707)
    bad = close_set(g("d_lp"), {str(k): v for k, v in ref.items()}, (200, 1000, 4000, 12000), 0.06)
    L.law("d_lp", "d_lp.rbj_lowpass", not bad, json.dumps(bad))
    ref = rbj_gains("pk", 1000, 1.0, 6.0)
    bad = close_set(g("d_pk6"), {str(k): v for k, v in ref.items()}, FREQS, 0.06)
    L.law("d_pk6", "d_pk6.rbj_peaking", not bad, json.dumps(bad))
    L.law("d_pk6", "d_pk6.plus6_at_fc", approx(g("d_pk6").get("1000"), 6.0, 0.06), str(g("d_pk6").get("1000")))
    bad = close_set(g("d_peq"), g("d_pk6"), FREQS, 0.05)
    L.law("d_peq", "d_peq.equals_peaking", not bad, json.dumps(bad))
    nt = g("d_nt")
    L.law("d_nt", "d_nt.notch_at_fc", nt.get("1000") is not None and nt["1000"] <= -60, str(nt.get("1000")))
    L.law("d_nt", "d_nt.skirts_pass",
          approx(nt.get("200"), -0.184, 0.5) and approx(nt.get("4000"), -0.284, 0.5),
          f"200={nt.get('200')} 4000={nt.get('4000')}")
    for tag in ("d_f0", "d_fneg", "d_raw"):
        an = d[tag].get("analysis") or {}
        L.law(tag, tag + ".exact_zeros",
              an.get("out_nz_exact") == 0 and (an.get("out_bytes") or 0) >= 1000,
              f"nz={an.get('out_nz_exact')} bytes={an.get('out_bytes')}")
        cells["silent_" + tag] = {"nz": an.get("out_nz_exact"), "bytes": an.get("out_bytes")}
    gf = g("d_fhi")
    L.law("d_fhi", "d_fhi.passthrough", len(gf) == 5 and all(abs(v) <= 0.05 for v in gf.values() if v is not None), str(gf))
    L.law("d_g20", "d_g20.plus20_at_fc", approx(g("d_g20").get("1000"), 20.0, 0.06), str(g("d_g20").get("1000")))
    bad = close_set(g("d_g20x"), g("d_g20"), FREQS, 0.05)
    L.law("d_g20x", "d_g20x.clamped_to_20", not bad, json.dumps(bad))
    ref = rbj_gains("pk", 1000, 1.0, -120.0)
    bad = close_set(g("d_gneg"), {str(k): v for k, v in ref.items()}, (200, 4000, 12000, 20000), 0.5)
    L.law("d_gneg", "d_gneg.rbj_minus120", not bad, json.dumps(bad))
    L.law("d_gneg", "d_gneg.annihilated_at_fc", (g("d_gneg").get("1000") or 0) <= -60, str(g("d_gneg").get("1000")))
    bad = close_set(g("d_gnegx"), g("d_gneg"), (200, 4000, 12000, 20000), 1.0)
    L.law("d_gnegx", "d_gnegx.clamped_min", not bad, json.dumps(bad))
    g140 = g("d_gneg140")
    L.law("d_gneg140", "d_gneg140.is_minus120_response", approx(g140.get("200"), -46.362, 1.5), str(g140.get("200")))
    L.law("d_gneg140", "d_gneg140.not_unclamped",
          g140.get("200") is not None and abs(g140["200"] - (-66.362)) >= 5.0, str(g140.get("200")))
    L.law("d_q707", "d_q707.plus20_at_fc", approx(g("d_q707").get("1000"), 20.0, 0.06), str(g("d_q707").get("1000")))
    L.law("d_q10", "d_q10.plus20_at_fc", approx(g("d_q10").get("1000"), 20.0, 0.06), str(g("d_q10").get("1000")))
    bad = close_set(g("d_q1e9"), g("d_q10"), FREQS, 0.05)
    L.law("d_q1e9", "d_q1e9.clamped_to_10", not bad, json.dumps(bad))
    qn, q7 = g("d_qneg"), g("d_q707")
    L.law("d_qneg", "d_qneg.not_default_at_200",
          qn.get("200") is not None and q7.get("200") is not None and abs(qn["200"] - q7["200"]) >= 3.0,
          f"qneg200={qn.get('200')} q707200={q7.get('200')}")
    L.law("d_qneg", "d_qneg.broadband_shape",
          bool(qn) and (max(qn.values()) - min(qn.values())) <= 2.0, str(qn))
    bad = close_set(g("d_coeff"), g("d_lp"), (200, 1000, 4000, 12000), 0.06)
    L.law("d_coeff", "d_coeff.coeff_ports_inert", not bad, json.dumps(bad))
    bad = close_set(g("d_lp_g6"), g("d_lp"), (200, 1000, 4000, 12000), 0.06)
    L.law("d_lp_g6", "d_lp_g6.gain_port_inert", not bad, json.dumps(bad))

    # ---- raw re-derivation from the captured WAVs (own reader/DFT/window)
    if args.scratch:
        for tag in sorted(set(list(d.keys()) + list(DSP_TAGS))):
            if tag in L.absent:
                continue
            l = d[tag]
            if l.get("kind") == "silent" or l.get("gate") or not l.get("valid"):
                continue
            att = l.get("attempt", 0)
            rp = os.path.join(args.scratch, f"{tag}_{att}_ref.wav")
            op = os.path.join(args.scratch, f"{tag}_{att}_out.wav")
            if not (os.path.exists(rp) and os.path.exists(op)):
                L.law(tag, tag + ".raw_bytes_present", False, f"missing {rp} / {op}", blocked=True)
                continue
            try:
                wr, wo = wav_read(rp), wav_read(op)
                sr, offr = best_window(wr["x"])
                so, offo = best_window(wo["x"])
                gr = gain_db(dft_mag(so, FREQS), dft_mag(sr, FREQS))
                # second, differently-placed window PER TAP (the two taps are
                # separate streams with their own time base — a shared offset
                # is invalid): a window-placement probe.
                fx = wr["x"][offr + 12000:offr + 12000 + WIN]
                fy = wo["x"][offo + 12000:offo + 12000 + WIN]
                gfixed = gain_db(dft_mag(fy, FREQS), dft_mag(fx, FREQS))
            except Exception as exc:                      # noqa: BLE001
                L.law(tag, tag + ".raw_recompute", False, f"{exc}", blocked=True)
                continue
            rec_g = l.get("analysis", {}).get("gain_db") or {}
            deltas = {k: (None if rec_g.get(k) is None or gr.get(k) is None
                          else round(abs(rec_g[k] - gr[k]), 3)) for k in rec_g}
            cells["rawdelta_" + tag] = deltas
            worst = max([v for v in deltas.values() if v is not None], default=None)
            L.law(tag, tag + ".raw_recompute_matches",
                  worst is not None and worst <= 0.02,
                  f"max|recorded-recomputed|={worst} dB (recorded={rec_g}, recomputed={gr})")
            fd = {k: (None if gr.get(k) is None or gfixed.get(k) is None
                      else round(abs(gr[k] - gfixed[k]), 3)) for k in gr}
            worst_f = max([v for v in fd.values() if v is not None], default=None)
            cells["window_spread_" + tag] = worst_f
            # window placement must not move a cell the stimulus actually
            # excites with real level (recorded ref magnitude above the
            # analysis threshold and a response above -20 dB); attenuated
            # and floor-dominated cells are recorded, not armed — the
            # author's own instrument-spread note (deep cells carry a
            # +/-0.6 dB spread under contention).
            refm = l.get("analysis", {}).get("ref_mags") or {}
            rms_sr = float(np.sqrt(np.mean(sr * sr))) if len(sr) else 0.0
            rms_so = float(np.sqrt(np.mean(so * so))) if len(so) else 0.0
            rms_fx = float(np.sqrt(np.mean(fx * fx))) if len(fx) else 0.0
            rms_fy = float(np.sqrt(np.mean(fy * fy))) if len(fy) else 0.0
            steady = (len(fx) == WIN and len(fy) == WIN and rms_sr > 0 and rms_so > 0
                      and rms_fx >= 0.9 * rms_sr and rms_fy >= 0.9 * rms_so)
            cells["second_window_steady_" + tag] = {
                "rms_ref": (round(rms_sr, 5), round(rms_fx, 5)),
                "rms_out": (round(rms_so, 5), round(rms_fy, 5)),
                "steady": steady}
            shallow = {k: fd[k] for k in fd
                       if steady and rec_g.get(k) is not None
                       and abs(rec_g[k]) <= 20
                       and (refm.get(k) or 0.0) >= 1e-4 and fd[k] is not None}
            deep = {k: fd[k] for k in fd
                    if rec_g.get(k) is not None and 20 < abs(rec_g[k]) <= 60
                    and (refm.get(k) or 0.0) >= 1e-4 and fd[k] is not None}
            cells["window_spread_deep_" + tag] = deep
            if shallow:
                worst_s = max(shallow.values())
                L.law(tag, tag + ".window_independent", worst_s <= 0.05,
                      f"shallow-cell max|maxwin-secondwin|={worst_s} dB "
                      f"({shallow})")

    # ============================================================= entry 3: ir
    ir = Legs(m["filterchain_ir_r92_probe"]["legs"], L, "ir")
    cells["ir_leg_keys"] = sorted(ir.keys())
    specs = ("i_2tap", "i_gain05", "i_d100", "i_decay512", "i_441", "i_stereo", "i_clip",
             "i_noconfig", "i_missing", "i_empty", "i_text", "i_dir",
             "d_10ms", "d_1ms", "d_50ms", "d_over", "d_over2")
    for tag in specs:
        l = ir[tag]
        if l.get("gate"):
            L.law(tag, tag + ".measured", False, f"gate={l['gate']}", blocked=True)
            continue
        if not l.get("valid"):
            L.law(tag, tag + ".measured", False, f"valid=False links_ok={l.get('links_ok')}",
                  blocked=not l.get("links_ok"))
            continue
        L.law(tag, tag + ".measured", True, "")

    def an(tag):
        return ir[tag].get("analysis") or {}

    a_ = an("i_2tap")
    L.law("i_2tap", "i_2tap.gap64", a_.get("peak_gap") == 64, str(a_.get("peak_gap")))
    L.law("i_2tap", "i_2tap.ratio_half", approx(a_.get("peak_ratio"), 0.5, 0.0015), str(a_.get("peak_ratio")))
    L.law("i_2tap", "i_2tap.first_tap",
          approx(((a_.get("out_top") or [[None, None]])[0] or [None, None])[1], 0.99994, 0.002),
          str(a_.get("out_top")))
    L.law("i_2tap", "i_2tap.ir0_at_ref", shift_ok(a_.get("delta_samples"), 0), f"delta={a_.get('delta_samples')}")
    a_ = an("i_gain05")
    L.law("i_gain05", "i_gain05.gap64", a_.get("peak_gap") == 64, str(a_.get("peak_gap")))
    L.law("i_gain05", "i_gain05.scaled_half",
          approx(((a_.get("out_top") or [[None, None]])[0] or [None, None])[1], 0.49997, 0.002),
          str(a_.get("out_top")))
    a_ = an("i_d100")
    L.law("i_d100", "i_d100.shift100", shift_ok(a_.get("delta_samples"), 100), f"delta={a_.get('delta_samples')}")
    L.law("i_d100", "i_d100.single_impulse", a_.get("out_n_gt") == 1, str(a_.get("out_n_gt")))
    a_ = an("i_441")
    L.law("i_441", "i_441.resampled_peak", shift_ok(a_.get("peak_delta"), 110), f"peak_delta={a_.get('peak_delta')}")
    L.law("i_441", "i_441.tap_count", (a_.get("out_n_gt") or 0) >= 30, str(a_.get("out_n_gt")))
    a_ = an("i_stereo")
    L.law("i_stereo", "i_stereo.channel0_only", shift_ok(a_.get("delta_samples"), 10), f"delta={a_.get('delta_samples')}")
    L.law("i_stereo", "i_stereo.single_impulse", a_.get("out_n_gt") == 1, str(a_.get("out_n_gt")))
    a_ = an("i_clip")
    L.law("i_clip", "i_clip.hard_clip",
          a_.get("out_stats", {}).get("max_abs") is not None
          and 0.99 <= a_["out_stats"]["max_abs"] <= 1.0, str(a_.get("out_stats", {}).get("max_abs")))
    L.law("i_clip", "i_clip.gap64", a_.get("peak_gap") == 64, str(a_.get("peak_gap")))
    silent_cls = {"i_noconfig": "fc92_convolver_cfg", "i_missing": "fc92_convolver_file",
                  "i_empty": "fc92_convolver_file", "i_text": "fc92_convolver_file",
                  "i_dir": "fc92_convolver_file"}
    for tag, cls in silent_cls.items():
        L.law(tag, tag + ".exact_zeros", an(tag).get("out_nz_exact") == 0, f"nz={an(tag).get('out_nz_exact')}")
        L.law(tag, tag + ".activation_class", ir[tag].get("error_class") == cls,
              f"got={ir[tag].get('error_class')} hit={ir[tag].get('error_hit')}")
    delay = {"d_1ms": 48, "d_10ms": 480, "d_50ms": 2400, "d_over": 2431, "d_over2": 2431}
    for tag, want in delay.items():
        L.law(tag, tag + ".delay_samples", shift_ok(an(tag).get("delta_samples"), want),
              f"delta={an(tag).get('delta_samples')} want={want}")
        L.law(tag, tag + ".single_impulse", an(tag).get("out_n_gt") == 1, str(an(tag).get("out_n_gt")))
    res_present = "i_residual" in ir
    res = ir["i_residual"] if res_present else {}
    cells["i_residual"] = res
    for tag, want in (("i_2tap", 1.0), ("i_decay512", 1.0), ("i_d100", 0.5)):
        r = res.get(tag) or {}
        L.law("i_residual", f"i_residual:{tag}.le_{want}lsb",
              r.get("max_residual_lsb") is not None and r["max_residual_lsb"] <= want,
              json.dumps(r), blocked=not res_present)
        L.law("i_residual", f"i_residual:{tag}.none_over_1lsb",
              r.get("n_gt_1lsb") == 0, str(r.get("n_gt_1lsb")),
              blocked=not res_present)

    # ---- raw re-derivation of the IR cells (own convolution + alignment)
    if args.scratch:
        delta = os.path.join(args.scratch, "r92a_delta100.wav")
        for tag, irfile, want_lsb in (("i_2tap", "r92a_ir_2tap.wav", 1.0),
                                      ("i_decay512", "r92a_ir_decay512.wav", 1.0),
                                      ("i_d100", "r92a_ir_d100.wav", 0.5)):
            l = ir[tag]
            att = l.get("attempt", 0)
            op = os.path.join(args.scratch, f"{tag}_{att}_out.wav")
            if not (os.path.exists(op) and os.path.exists(delta)):
                L.law(tag, tag + ".raw_residual", False, "capture/IR missing", blocked=True)
                continue
            try:
                xo = wav_read(op)["x"]
                irx = wav_read(os.path.join(args.scratch, irfile))["x"]
                st = wav_read(delta)["x"]
                e = np.convolve(st, irx)
                n = len(e)
                best = None
                for lag in range(-128, len(xo) - n + 129, 64):
                    a = max(0, -lag)
                    b = min(n, len(xo) - lag)
                    if b - a < n - 128:
                        continue
                    m_ = float(np.max(np.abs(e[a:b] - xo[a + lag:b + lag])))
                    if best is None or m_ < best[0]:
                        best = (m_, lag)
                assert best is not None
                for lag in range(max(-128, best[1] - 64), min(len(xo) - n + 128, best[1] + 64) + 1):
                    a = max(0, -lag)
                    b = min(n, len(xo) - lag)
                    if b - a < n - 128:
                        continue
                    m_ = float(np.max(np.abs(e[a:b] - xo[a + lag:b + lag])))
                    if m_ < best[0]:
                        best = (m_, lag)
                m_, lag = best
                lsb = 1.0 / 32768.0
                rlsb = round(m_ / lsb, 3)
                L.law(tag, tag + ".raw_residual_recomputed",
                      rlsb <= want_lsb, f"{rlsb} LSB at lag {lag} (recorded {(res.get(tag) or {}).get('max_residual_lsb')})")
                cells["rawres_" + tag] = {"lsb": rlsb, "lag": lag}
            except Exception as exc:                      # noqa: BLE001
                L.law(tag, tag + ".raw_residual_recomputed", False, str(exc), blocked=True)

    # ============================================================ entry 4: wpx
    w = Legs(m["filterchain_wpx_r92_probe"]["legs"], L, "wpx")
    cells["wpx_leg_keys"] = sorted(w.keys())
    l = w["w_print"]
    L.law("w_print", "w_print.rc0_and_marker",
          l.get("exit_code") == 0 and "r92a hello from wpexec" in (l.get("stdout") or ""),
          f"rc={l.get('exit_code')} stdout={(l.get('stdout') or '')[:60]}")
    l = w["w_globals"]
    L.law("w_globals", "w_globals.namespace",
          l.get("exit_code") == 0 and "Core=table LocalModule=function Settings=table require_api=nil" in (l.get("stdout") or ""),
          f"rc={l.get('exit_code')} stdout={(l.get('stdout') or '')[:90]}")
    for tag in ("w_rawget", "w_require_api"):
        l = w[tag]
        L.law(tag, tag + ".bare_runtime_error",
              l.get("exit_code") == 70 and l.get("error_class") == "fc92_wpx_runtime",
              f"rc={l.get('exit_code')} class={l.get('error_class')}")
    l = w["w_settings"]
    L.law("w_settings", "w_settings.reachable",
          l.get("exit_code") == 0 and "restore-props=" in (l.get("stdout") or ""),
          f"rc={l.get('exit_code')} stdout={(l.get('stdout') or '')[:80]}")
    l = w["w_localmodule"]
    live = [s for s in (l.get("snapshots") or []) if s.get("own_nodes")]
    L.law("w_localmodule", "w_localmodule.live_graph", bool(live), f"snapshots={l.get('snapshots')}")
    L.law("w_localmodule", "w_localmodule.self_cleaning", l.get("own_nodes_after") == [],
          str(l.get("own_nodes_after")))
    L.law("w_localmodule", "w_localmodule.link_free",
          not any(s.get("own_edges") for s in (l.get("snapshots") or [])), str(l.get("snapshots")))
    cells["w_localmodule"] = {"snaps": [(s.get("at_s"), len(s.get("own_nodes") or [])) for s in (l.get("snapshots") or [])],
                              "after": l.get("own_nodes_after"), "rc": l.get("exit_code")}
    for tag in ("w_lm_bad_module", "w_lm_bad_label"):
        l = w[tag]
        L.law(tag, tag + ".silent_nil",
              l.get("exit_code") == 0 and "pcall ok=true mod=nil" in (l.get("stdout") or ""),
              f"rc={l.get('exit_code')} stdout={(l.get('stdout') or '')[:80]}")
    for tag in ("w_noquit", "w_empty"):
        L.law(tag, tag + ".hangs", w[tag].get("killed_at_bound") is True,
              f"rc={w[tag].get('exit_code')} killed={w[tag].get('killed_at_bound')}")
    for tag, cls in (("w_syntax", "fc92_wpx_compile"), ("w_missing", "fc92_wpx_locate"),
                     ("w_noargv", "fc92_wpx_locate")):
        l = w[tag]
        L.law(tag, tag + ".rc70_class",
              l.get("exit_code") == 70 and l.get("error_class") == cls,
              f"rc={l.get('exit_code')} class={l.get('error_class')} hit={l.get('error_hit')}")
    l = w["v_spa"]
    L.law("v_spa", "v_spa.six_plugins_no_ffmpeg",
          "libspa-filter-graph.so" in (l.get("filter_graph_dir") or [])
          and not l.get("spa_ffmpeg_hits") and l.get("filter_graph_count") == 6,
          json.dumps({k: l.get(k) for k in ("filter_graph_count", "spa_ffmpeg_hits")}))
    l = w["v_ladspa"]
    L.law("v_ladspa", "v_ladspa.search_path_absent",
          sorted(l.get("absent_dirs") or []) == ["/usr/lib/ladspa", "/usr/lib64/ladspa"],
          json.dumps(l))
    l = w["v_lv2"]
    L.law("v_lv2", "v_lv2.no_dsp_plugin",
          (l.get("bundle_count") or 0) >= 1 and l.get("so_count") == 0, json.dumps(l))
    l = w["v_kemar"]
    L.law("v_kemar", "v_kemar.unshipped_ir",
          l.get("conf_exists") is True and bool(l.get("conf_refs"))
          and not any((l.get("refs_exist") or {}).values()), json.dumps(l))
    cells["v_spa"] = {"count": w["v_spa"].get("filter_graph_count"), "ffmpeg": w["v_spa"].get("spa_ffmpeg_hits")}
    cells["v_lv2"] = {"bundles": w["v_lv2"].get("bundle_count"), "so": w["v_lv2"].get("so_count")}
    cells["v_kemar"] = {"conf": w["v_kemar"].get("conf_exists"), "refs": w["v_kemar"].get("conf_refs")}

    # ---------------------------------------------------------------- report
    n, p, f, b = L.summary()
    print(f"# {args.tag}: {args.receipt}")
    print(f"laws: {n}  PASS: {p}  FAIL: {f}  BLOCKED: {b}")
    all_legs = []
    for e in ENTRIES:
        all_legs += sorted((m[e]["legs"] or {}).keys())
    print(f"leg keys seen: {len(all_legs)}")
    fails = []
    blocked = []
    for leg in sorted(L.legs):
        st, det = L.leg_status(leg)
        if st == "FAIL":
            fails.append((leg, det))
        elif st == "BLOCKED":
            blocked.append((leg, det))
    print(f"legs FAIL: {len(fails)}  legs BLOCKED: {len(blocked)}")
    for leg, det in fails:
        print(f"  FAIL {leg}: {det}")
    for leg, det in blocked:
        print(f"  BLOCKED {leg}: {det}")
    print("FAILED LAWS:")
    for leg, lid, st, det in L.rows:
        if st == "FAIL":
            print(f"  {lid}: {det}")
    if args.json:
        json.dump({"tag": args.tag, "receipt": args.receipt, "laws": n, "pass": p,
                   "fail": f, "blocked": b,
                   "leg_status": {leg: L.leg_status(leg)[0] for leg in sorted(L.legs)},
                   "failed_laws": [{"id": lid, "detail": det} for _, lid, st, det in L.rows if st == "FAIL"],
                   "cells": cells},
                  open(args.json, "w"), indent=1, default=str)
    return 0 if (f == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
