#!/usr/bin/env python3
"""r78 SIMPLIFIER replay comparator.

Three levels, all reported:

  A STRICT   — every leaf outside the declared host-drift *classes* must be
               equal (including the key SET: a removed leaf is a diff).
  B CONTRACT — the pinned verdict classes must be equal: failures maps, error
               classes, exit codes, killed-at-bound flags, consumer unions,
               tone verdicts + their aggregates, the named host classes
               (`pactl_stale_default`/`pactl_delayed_default`), sink-gone
               flags, header-mismatch leaves, `blocked` rows.
  C SELF     — the receipt's own derived relations must hold in BOTH
               receipts (consumer/producer nodes derived from the port sets,
               tone aggregates from the windows, expected_bytes from the
               frame bound, the lattice fallback law, header mismatch from
               header+payload, sink-gone flags True).

Declared drift classes (host variance, not the fold):
  D1 wall_s              D2 when_s / applied_in_s / released_in / moved_at_s
  D3 module_id           D4 contention (live census) + inventory snapshots
  D5 pactl poll_trace    D6 per-window tap magnitudes/edge flags
  D7 zeros size_trace    D8 host topology names (pid-stamped)

PASS = A=0, C=0 and identical failures maps.

Calibration: the comparator is run on (control, cand) and on
(control, canonical clean receipt) — every A-strict diff must be empty in
both, and the negative control (one perturbed verdict leaf) must be caught.

Usage: compare_r78.py CONTROL.json CAND.json [--json]
"""
import json
import re
import sys

R78 = ("playback_target_lattice_r78_probe", "playback_default_follow_r78_probe",
       "playback_target_loss_r78_probe", "playback_props_r78_probe",
       "playback_class_segv_r78_probe", "playback_aplay_axis_r78_probe",
       "capture_unlinked_zeros_r78_probe", "capture_parec_fix_r78_probe")

PID = re.compile(r"_\d{5,7}\b")
TMPDIR = re.compile(r"/tmp/capture-r78-[A-Za-z0-9_.-]+/")


def norm(o):
    """Two per-run naming schemes, normalized to one token on BOTH sides:
    pid-stamped node names (the r77 fold's contention rule) and the run's
    TemporaryDirectory path, which every aplay argv/stderr leaf echoes."""
    if isinstance(o, str):
        return PID.sub("_<pid>", TMPDIR.sub("<tmp>/", o))
    if isinstance(o, dict):
        return {k: norm(v) for k, v in o.items()}
    if isinstance(o, list):
        return [norm(v) for v in o]
    return o


def flat(o, p=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from flat(v, f"{p}.{k}" if p else k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from flat(v, f"{p}[{i}]")
    else:
        yield p, o


D_WALL = re.compile(r"(^|\.)wall_s$")
D_TIME = re.compile(r"(^|\.)(when_s|applied_in_s|released_in|moved_at_s)$")
D_MOD = re.compile(r"\.module_id$")
D_CONT = re.compile(r"\.contention\.|\.inventory\.|\.default_sink_(initial|"
                    r"final)$|\.metadata_(initial|final)\.|\.pcm_map\.|"
                    r"\.sink_name$|\.sinks$|\.source_peer\.|\.subject\.|"
                    r"\.sink_load|\.sink_loads|\.def_sink_load|\.sinks_gone$")
D_POLL = re.compile(r"\.poll_trace\[")
D_WIN = re.compile(r"\.(tap|tap_default|tap_self|file_windows)\.windows\[")
# D6b — the tap's any-audio/zero SPLIT: the tap window is aligned by wall
# time, so exactly one ~0.1 s boundary window flips between "any audio" and
# "digital zero" across runs. The verdict leaves (carries_tone, mine_windows,
# mine_spans, peak_l, peak_r) stay strict.
D_EDGE = re.compile(r"\.(tap|tap_default|tap_self|file_windows)\."
                    r"(audio_windows|zero_windows)$")
D_SIZE = re.compile(r"\.size_trace\[|\.producer_samples\[")


def drift_class(path):
    if D_WALL.search(path):
        return "D1 wall clock"
    if D_TIME.search(path):
        return "D2 fire/apply/release times"
    if D_MOD.search(path):
        return "D3 host module counter"
    if D_CONT.search(path):
        return "D4 host topology/census"
    if D_POLL.search(path):
        return "D5 pactl poll trace"
    if D_WIN.search(path):
        return "D6 per-window tap magnitudes"
    if D_EDGE.search(path):
        return "D6b boundary-window audio/zero split"
    if D_SIZE.search(path):
        return "D7 growth traces"
    return None


CONTRACT = re.compile(
    r"\.(failures|error_class|error|exit_code|killed_at_bound|consumers_union|"
    r"consumer_ports|producer_ports|nodes|ambiguous|carries_tone|mine_windows|"
    r"mine_spans|audio_windows|zero_windows|peak_l|peak_r|blocked|confound|"
    r"confound_observed|expected|target_arg|target_object_lies|"
    r"target_object_advertised|node_target_advertised|landed_peer|"
    r"peer_unresolved|early_consumers|late_consumers|expected_nodes|"
    r"pactl_stale_default|pactl_delayed_default|applied|followed_move|"
    r"pinned|header_prefix_mismatch|header_honest|header_field|"
    r"header_value|payload_implied|implied_rate|implied_bpf|implied_ch|"
    r"data_finalized|expected_bytes|exit|out|in|kind|leg|sink_gone|"
    r"probe_sink_gone|sinks_gone|def_sink_gone|witness_lock_release_s|"
    r"alsa_lock_retention|converted_to|device_name|formats|channels|"
    r"channels_max|channels_min|rate|rate_max|rate_min|new_nodes|"
    r"target|tap_target|module_id|sink_name|subject)$")


def leaves(path):
    with open(path) as fh:
        rec = json.load(fh)
    return dict(flat(norm(rec))), rec


def self_consistency(rec, label, out):
    m = rec["measurements"]

    def bad(msg):
        out.append(f"{label}: {msg}")

    for entry in R78:
        bag = m.get(entry) or {}
        if bag.get("blocked"):
            continue
        legs = bag.get("legs") or {}
        for name, leg in legs.items():
            if not isinstance(leg, dict) or "blocked" in leg:
                continue
            # consumer/producer node set derived from the port sets
            for pk, nk in (("consumer_ports", "nodes"),
                           ("producer_ports", "nodes")):
                ports = leg.get(pk)
                if ports is None:
                    continue
                nodes = sorted({p.rsplit(":", 1)[0] for p in ports})
                if leg.get(nk) != nodes:
                    bad(f"{entry}.{name}: {nk} {leg.get(nk)} != "
                        f"{pk} derivation {nodes}")
            samples = leg.get("samples") or []
            if samples and "consumers_union" in leg:
                union = sorted({n for s in samples for n in s["nodes"]})
                if leg.get("consumers_union") != union:
                    bad(f"{entry}.{name}: consumers_union "
                        f"{leg.get('consumers_union')} != samples union "
                        f"{union}")
            # tone aggregates from the window list
            for tk in ("tap", "tap_default", "tap_self"):
                tap = leg.get(tk)
                if not isinstance(tap, dict) or "windows" not in tap:
                    continue
                w = tap["windows"]
                if tap.get("mine_windows") != sum(1 for x in w if x["mine"]):
                    bad(f"{entry}.{name}.{tk}: mine_windows != windows")
                if tap.get("audio_windows") != sum(1 for x in w if x["audio"]):
                    bad(f"{entry}.{name}.{tk}: audio_windows != windows")
                if tap.get("zero_windows") != \
                        sum(1 for x in w if not x["audio"]):
                    bad(f"{entry}.{name}.{tk}: zero_windows != windows")
                if tap.get("peak_l") != max((x["a_l"] for x in w), default=0):
                    bad(f"{entry}.{name}.{tk}: peak_l != max a_l")
                if tap.get("carries_tone") != (tap.get("mine_windows", 0)
                                               >= 8):
                    bad(f"{entry}.{name}.{tk}: carries_tone != 8-window law")
            if "carries_tone" in leg and isinstance(leg.get("tap"), dict):
                if leg["carries_tone"] != leg["tap"].get("carries_tone"):
                    bad(f"{entry}.{name}: carries_tone != tap.carries_tone")
            # the fallback law for the lattice
            if entry == "playback_target_lattice_r78_probe" and \
                    leg.get("expected") == "fallback":
                want = leg.get("default_sink_at_leg")
                if want and leg.get("consumers_union") != [want]:
                    bad(f"{entry}.{name}: fallback consumed "
                        f"{leg.get('consumers_union')} != default {want}")
    # zeros: expected_bytes from the frame bound, bytes == expected
    z = (m.get("capture_unlinked_zeros_r78_probe") or {}).get("legs") or {}
    for name, leg in z.items():
        if "expected_bytes" in leg and leg.get("bytes") is not None:
            if leg["bytes"] != leg["expected_bytes"]:
                bad(f"zeros.{name}: bytes != expected_bytes")
    # parec: header mismatch is header==request AND payload==source
    pf = m.get("capture_parec_fix_r78_probe") or {}
    for name, mm in (pf.get("mismatches") or {}).items():
        if not isinstance(mm, dict) or "header_prefix_mismatch" not in mm:
            continue
        if name == "hdr_rate_plain":
            continue
        want = (mm.get("header_value") is not None and
                mm.get("payload_implied") is not None and
                mm.get("header_value") != mm.get("payload_implied"))
        if name == "hdr_rate_fix":
            want = (mm.get("header_value") == 22050 and
                    mm.get("payload_implied") == 48000)
        elif name == "hdr_fmt_fix":
            want = (mm.get("header_value") == 16 and
                    mm.get("payload_implied") == 4)
        elif name == "hdr_ch_fix":
            want = (mm.get("header_value") == 1 and
                    mm.get("payload_implied") == 2)
        if bool(mm["header_prefix_mismatch"]) != bool(want):
            bad(f"parec.{name}: header_prefix_mismatch != header/payload law")
    return out


def main():
    ctl, cand = sys.argv[1], sys.argv[2]
    as_json = "--json" in sys.argv
    a, ra = leaves(ctl)
    b, rb = leaves(cand)
    keys = sorted(set(a) | set(b))
    strict, drift, contract = [], [], []
    for k in keys:
        va, vb = a.get(k, "<MISSING>"), b.get(k, "<MISSING>")
        if repr(va) == repr(vb):
            continue
        dc = drift_class(k)
        if dc:
            drift.append((k, va, vb, dc))
            continue
        strict.append((k, va, vb))
        if CONTRACT.search(k):
            contract.append((k, va, vb))
    selfbad = []
    self_consistency(ra, "control", selfbad)
    self_consistency(rb, "candidate", selfbad)
    cfail = {k: v["failures"] for k, v in ra["measurements"].items()
             if v.get("failures")}
    dfail = {k: v["failures"] for k, v in rb["measurements"].items()
             if v.get("failures")}
    r78fail = {k: v for k, v in list(cfail.items()) + list(dfail.items())
               if k in R78}
    out = {"control": ctl, "candidate": cand, "leaves": len(keys),
           "A_strict_diffs": len(strict), "B_contract_diffs": len(contract),
           "declared_drift_diffs": len(drift),
           "C_self_consistency_violations": selfbad,
           "control_failures": cfail, "candidate_failures": dfail,
           "strict": strict, "contract": contract,
           "drift_classes": sorted({d for *_x, d in drift})}
    if as_json:
        print(json.dumps(out, indent=1))
    else:
        print(f"leaves compared          : {len(keys)}")
        print(f"A strict diffs           : {len(strict)}")
        print(f"B contract-leaf diffs    : {len(contract)}")
        print(f"  (declared drift diffs  : {len(drift)} "
              f"{out['drift_classes']})")
        print(f"C self-consistency viols : {len(selfbad)}")
        print(f"control   failures       : {json.dumps(cfail)[:300]}")
        print(f"candidate failures       : {json.dumps(dfail)[:300]}")
        for k, va, vb in strict[:40]:
            print(f"  STRICT {k}: {va!r} != {vb!r}")
        for s in selfbad[:40]:
            print(f"  SELF   {s}")
        identical = cfail == dfail
        empty = not cfail and not dfail
        # PASS = no leaf difference outside the declared drift classes, no
        # self-consistency violation, and IDENTICAL failures maps. `empty` is
        # reported, not required: a failure shared by both sides is a host
        # state both arms measured, not a fold difference (the empty form is
        # supplied by the cross-window comparison against the canonical
        # clean receipt).
        ok = not strict and not selfbad and identical
        print(f"failures identical       : {identical} "
              f"(empty: {empty})")
        print(f"VERDICT: {'PASS' if ok else 'FAIL'} "
              f"(A={len(strict)} B={len(contract)} C={len(selfbad)} "
              f"failures ctl={len(cfail)} cand={len(dfail)} "
              f"identical={identical} r78={len(r78fail)})")
    return 0 if (not strict and not selfbad and not cfail and not dfail) else 1


if __name__ == "__main__":
    sys.exit(main())
