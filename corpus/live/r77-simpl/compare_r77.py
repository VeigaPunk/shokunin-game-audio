#!/usr/bin/env python3
"""r77 simplifier replay comparator (calibrated on the 3 canonical clean runs).

Three levels, all reported:

  A STRICT   — every leaf outside the declared host-drift *classes* must be
               equal. The drift classes are the r77-author report §8 items,
               taken as CLASSES (the parenthetical "+-1 frame" is the author's
               envelope claim and is falsified by the receipts themselves: see
               report; the observed envelope on sever legs is up to 2048
               frames).
  B CONTRACT — the pinned verdict classes must be equal: failures maps, error
               classes, finalize classes, reader verdicts, consumed nodes, tone
               booleans, split sizes, format leaves, eintr/busy cell lists,
               topology witness, sha256 of the bounded legs.
  C SELF     — the receipt's own derived relations must hold in BOTH receipts
               (bytes == data_actual + 44; honest_frames == data_actual //
               frame_bytes; declared_echo <=> value == declared != honest;
               lattice consumed-node == the per-cell default sink / target).

Calibration: on the three canonical clean capture-r77 receipts the comparator
must report A = 0 and B = 0.

Usage: compare_r77.py CONTROL.json CAND.json [--json]
"""
import json
import re
import sys

SEVER_LEG = (r"^measurements\.capture_arecord_sever_r77_probe\.legs\.[^.]+"
             r"|^measurements\.capture_readers_r77_probe\.wounds\.[^.]+")
# D1 — sever-wall-clock magnitudes (author §8 item 1), taken as a class.
SEVER_MAG = re.compile(
    SEVER_LEG + r"\.(file\.(bytes|data_actual|data_declared)"
    r"|readers\.(honest_frames|declared_frames|ffprobe\.duration_s"
    r"|ffprobe\.value|wave\.value|sndfile\.value|soxi_s\.value|soxi_D\.value"
    r"|soxi_s\.raw|soxi_D\.raw))$")
# D2 — wall-clock times and rate-window buckets (author §8 item 2).
WALL = re.compile(r"(^|\.)wall_s$")
RATE = re.compile(r"^measurements\.capture_target_loss_r77_probe"
                  r"\.wall_clock\.(rates|samples)")
# D3 — host state (author §8 item 3).
HOST = re.compile(
    r"^measurements\.capture_target_loss_r77_probe\.sink_load\.module_id$"
    r"|^measurements\.capture_source_lattice_r77_probe\.(contention\.|inventory\."
    r"(sinks|sources|monitors)\[)"
    r"|^measurements\.capture_source_lattice_r77_probe\.legs\.[^.]+"
    r"\.content\.(peak|nonzero_frac)$"
    r"|^measurements\.capture_split_sentinel_r77_probe"
    r"\.(undershoot|crossing)\.wall_s$")

# Contract leaves: compared at level B (class equality) as well as level A.
CONTRACT = re.compile(
    r"\.(failures|error_class|error|early_exit_code|signal|blocked|confound|"
    r"confound_observed|eintr_cells|alsa_busy_cells|sink_gone|rename_is_silent|"
    r"contended|unloaded|consumed_nodes|link_producers|target_object_prop|"
    r"carries_tone|verdict|data_finalized|data_declared_field|riff_size_field|"
    r"tag|channels|rate|bits|data_limit|total_limit|byte_cap|"
    r"requested_path_exists|byte_capped|frames_requested|expected_fmt|"
    r"requested|default_sink_is_stable|scout_alsa_read_eintr_reproduced|"
    r"host_is_quiet|ambiguous_topology|foreign_links_ignored|sha_match_control|"
    r"sha_match_dead_sink|nodes_before|nodes_after|fallback_node|frames_per_second|"
    r"all_zero_payload|data_actual_zero|link_after_exit|target_arg|"
    r"capture_sink_prop|live_at_link_sample|bound_flags|device|signal)$")


def flat(o, p=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from flat(v, f"{p}.{k}" if p else k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from flat(v, f"{p}[{i}]")
    else:
        yield p, o


def leaves(path):
    with open(path) as fh:
        rec = json.load(fh)
    return dict(flat(rec)), rec


def drift_class(path):
    if SEVER_MAG.match(path):
        return "D1 sever-wall-clock magnitude"
    if WALL.search(path) or RATE.match(path):
        return "D2 wall/rate bucket"
    if HOST.match(path):
        return "D3 host state"
    return None


def self_consistency(rec, label, out):
    """Derived relations the instrument claims. Any violation is a defect in
    that receipt, independent of the other one."""
    m = rec["measurements"]

    def bad(msg):
        out.append(f"{label}: {msg}")

    for entry in ("capture_arecord_sever_r77_probe", "capture_readers_r77_probe"):
        bag = m.get(entry, {})
        cells = dict(bag.get("legs") or bag.get("wounds") or {})
        if entry.endswith("readers_r77_probe"):
            cells = {k: v for k, v in cells.items() if "blocked" not in v}
        for name, cell in cells.items():
            f, rd = cell.get("file") or {}, cell.get("readers")
            if f.get("exists") and f.get("bytes") and not name.startswith("ffmpeg"):
                # ffmpeg's wav carries extra chunks, so its data offset is not
                # 44; every other leg here writes the bare 44-byte header.
                if f.get("data_actual") is not None and \
                        f["bytes"] != f["data_actual"] + 44:
                    bad(f"{entry}.{name}: bytes != data_actual + 44")
            if not rd:
                continue
            fb = rd.get("frame_bytes")
            if fb and f.get("data_actual") is not None:
                want = f["data_actual"] // fb
                if rd.get("honest_frames") != want:
                    bad(f"{entry}.{name}: honest_frames != data_actual // {fb}")
            for r in ("wave", "ffprobe", "soxi_s", "soxi_D", "sndfile"):
                leaf = rd.get(r) or {}
                v, verdict = leaf.get("value"), leaf.get("verdict")
                honest, declared = rd.get("honest_frames"), rd.get("declared_frames")
                if verdict is None or v is None:
                    continue
                if honest == 0:
                    want = "honest_empty" if v == 0 else "inflated"
                elif v == honest:
                    want = "honest"
                elif declared != honest and v == declared:
                    want = "declared_echo"
                elif v > honest:
                    want = "inflated"
                else:
                    want = "underreports"
                if verdict != want:
                    bad(f"{entry}.{name}.readers.{r}: verdict {verdict} != {want}")

    lat = m.get("capture_source_lattice_r77_probe", {})
    for name, leg in (lat.get("legs") or {}).items():
        if "blocked" in leg or leg.get("confound"):
            continue
        got = leg.get("consumed_nodes") or []
        if name in ("noprop_default_sink", "noprop_default_sink_monitor"):
            if got:
                bad(f"lattice {name}: a no-prop sink target consumed {got}")
        elif name.startswith("prop_") and name != "prop_other_sink":
            # the law: with the prop every non-sink target silently falls back
            # to the default sink's monitor (prop_other_sink is the control
            # that consumes a *different* sink, per the lattice table).
            want = leg.get("default_sink_at_cell")
            if want and got not in ([], [want]):
                bad(f"lattice {name}: consumed {got} neither empty nor {want}")
    split = m.get("capture_split_sentinel_r77_probe", {})
    if split.get("crossing", {}).get("siblings"):
        sib = split["crossing"]["siblings"]
        if "rot-01.wav" in sib and \
                sib["rot-01.wav"]["bytes"] != split.get("total_limit"):
            bad("split crossing: rot-01.wav != total_limit")
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
    out = {"control": ctl, "candidate": cand, "leaves": len(keys),
           "A_strict_diffs": len(strict), "B_contract_diffs": len(contract),
           "declared_drift_diffs": len(drift),
           "C_self_consistency_violations": selfbad,
           "control_failures": cfail, "candidate_failures": dfail,
           "strict": strict, "contract": contract}
    if as_json:
        print(json.dumps(out, indent=1))
    else:
        print(f"leaves compared          : {len(keys)}")
        print(f"A strict diffs           : {len(strict)}")
        print(f"B contract-leaf diffs    : {len(contract)}")
        print(f"  (declared drift diffs  : {len(drift)})")
        print(f"C self-consistency viols : {len(selfbad)}")
        print(f"control   failures       : {json.dumps(cfail)[:200]}")
        print(f"candidate failures       : {json.dumps(dfail)[:200]}")
        for k, va, vb in strict:
            print(f"  STRICT {k}: {va!r} != {vb!r}")
        for s in selfbad:
            print(f"  SELF   {s}")
    ok = not strict and not selfbad and not cfail and not dfail
    print(f"VERDICT: {'PASS' if ok else 'FAIL'} "
          f"(A={len(strict)} B={len(contract)} C={len(selfbad)} "
          f"failures ctl={len(cfail)} cand={len(dfail)})")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
