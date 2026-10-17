#!/usr/bin/env python3
"""r77 verifier — assert the six r77 claims against the verifier's OWN
canonical receipt (`--probe-capture-r77` run by this seat).

Usage: v0_receipt_checks.py <path/to/measurements.json> [out.json]

Each claim becomes a {claim, verdict, detail} row. A claim is AGREE only
when every leaf assertion under it holds on this receipt.
"""
import json
import sys
from pathlib import Path

SPLIT_TOTAL = 0x80000000 + 44
SPLIT_DATA = 0x7FFFFFFF


def check(path):
    d = json.loads(Path(path).read_text())
    m = d["measurements"]
    rows = []

    def row(claim, ok, detail):
        rows.append({"claim": claim, "verdict": "AGREE" if ok else "DISAGREE",
                     "detail": detail})

    row("failures:{} on this run", not d.get("failures") and all(
        not v["failures"] for v in m.values()),
        json.dumps({k: v["failures"] for k, v in m.items()
                    if v["failures"]})[:400])

    # 1 lattice
    lat = m["capture_source_lattice_r77_probe"]
    sink = lat["inventory"]["default_sink"]
    legs = lat["legs"]
    bad = []
    for name in ("prop_default_sink", "prop_default_sink_monitor",
                 "prop_source", "prop_default_token", "prop_pulse_token",
                 "prop_garbage", "prop_auto"):
        lg = legs.get(name, {})
        if lg.get("consumed_nodes") != [sink]:
            bad.append(f"{name}: consumed {lg.get('consumed_nodes')}")
        if not lg.get("content", {}).get("carries_tone"):
            bad.append(f"{name}: no tone")
    other = legs.get("prop_other_sink", {})
    if other.get("consumed_nodes") == [sink]:
        bad.append("prop_other_sink: fell back to the default (control dead)")
    if other.get("content", {}).get("carries_tone") is not False:
        bad.append("prop_other_sink: carried tone")
    for name in ("noprop_default_sink", "noprop_default_sink_monitor"):
        lg = legs.get(name, {})
        if lg.get("file", {}).get("bytes") != 44 or \
                lg.get("error_class") != "no_target_node":
            bad.append(f"{name}: {lg.get('file', {}).get('bytes')} B / "
                       f"{lg.get('error_class')}")
    nsrc = legs.get("noprop_source", {})
    if nsrc.get("consumed_nodes") != [lat["inventory"]["default_source"]]:
        bad.append("noprop_source: did not consume the source")
    live = [n for n in legs if legs[n].get("target_object_is_request")
            and legs[n].get("consumed_nodes")]
    row("1 fallback lattice (prop: default monitor; noprop: empty wav / "
        "real source)", not bad, "; ".join(bad) or
        f"{len(legs)} cells, {len(live)} live, "
        f"default_sink_is_stable={lat.get('default_sink_is_stable')}, "
        f"confound={lat.get('confound_observed', False)}")

    # 2 target loss
    loss = m["capture_target_loss_r77_probe"]
    b = loss["bounded"]
    bad = []
    for k in ("baseline", "fallback_control", "after_loss"):
        lg = b[k]
        if (lg.get("exit_code"), lg.get("bytes"), lg.get("data_finalized")) \
                != (1, 384044, True):
            bad.append(f"{k}: rc={lg.get('exit_code')} "
                       f"bytes={lg.get('bytes')} "
                       f"fin={lg.get('data_finalized')}")
    if not b.get("sha_match_control"):
        bad.append("post-loss artifact != fallback control sha")
    if b.get("nodes_before") != [loss["sink_name"]] or \
            b.get("nodes_after") != [b["fallback_node"]]:
        bad.append(f"topology {b.get('nodes_before')} -> "
                   f"{b.get('nodes_after')}")
    if not loss.get("sink_gone"):
        bad.append("probe sink survived")
    row("2 sustained_after_target_loss == re-link to the fallback node",
        not bad, "; ".join(bad) or
        f"sha_match_control={b.get('sha_match_control')} "
        f"sha_match_dead_sink={b.get('sha_match_dead_sink')} "
        f"after_loss_pct="
        f"{loss['wall_clock']['rates'].get('after_loss_pct')} "
        f"contended={b.get('contended')}")

    # 3 readers
    rd = m["capture_readers_r77_probe"]
    wounds = rd["wounds"]
    tally = rd["reader_honesty"]
    cal = rd["unit_calibration"]["readers"]
    bad = []
    if cal["soxi_s"]["value"] != 96000:
        bad.append(f"unit calibration: soxi -s={cal['soxi_s']['value']}")
    for k, w in wounds.items():
        if "blocked" in w:
            continue
        if w.get("readers", {}).get("sndfile", {}).get("verdict") != "honest":
            bad.append(f"{k}: sndfile "
                       f"{w.get('readers', {}).get('sndfile', {}).get('verdict')}")
    if wounds["arecord_bounded_kill"]["file"]["data_declared"] != 2304000:
        bad.append("arecord_bounded_kill declaration")
    if wounds["arecord_unbounded_kill"]["file"]["data_declared_field"] != \
            "placeholder_80000000":
        bad.append("arecord_unbounded_kill placeholder")
    if wounds["arecord_unbounded_kill"]["readers"]["soxi_s"]["verdict"] != \
            "declared_echo":
        bad.append("arecord_unbounded_kill soxi not declared_echo")
    row("3 reader matrix: sndfile honest on every wound; soxi/wave "
        "declared_echo on over-declared headers",
        not bad, "; ".join(bad) or
        f"tally={json.dumps({k: {x: y for x, y in v.items() if x.startswith('_')} for k, v in tally.items()})}")

    # 4 arecord open header
    ar = m["capture_arecord_sever_r77_probe"]
    legs4 = ar["legs"]
    bad = []
    for label, want in (("bound_d3_kill_early", 3 * 48000),
                        ("bound_d5_kill_early", 5 * 48000),
                        ("bound_d12_kill_early", 12 * 48000),
                        ("bound_d12_kill_late", 12 * 48000),
                        ("bound_s300k_kill", 300000)):
        got = (legs4[label].get("file", {}).get("data_declared") or 0) // 4
        if got != want:
            bad.append(f"{label}: {got} != {want}")
    if legs4["bound_unbounded_kill"]["file"]["data_declared_field"] != \
            "placeholder_80000000":
        bad.append("unbounded KILL placeholder")
    for label in ("bound_d3_term", "bound_d5_term", "bound_d12_term",
                  "bound_s300k_term", "bound_unbounded_term"):
        fin = legs4[label]["file"]
        if fin["data_finalized"] is not True or \
                fin["data_declared"] != fin["data_actual"]:
            bad.append(f"{label}: TERM did not finalize/patch")
    row("4 arecord open header is bound-derived (-d N -> N x 192000 B; "
        "unbounded -> 0x80000000)",
        not bad, "; ".join(bad) or
        f"eintr_cells={ar.get('eintr_cells')} "
        f"busy_cells={len(ar.get('alsa_busy_cells', []))} "
        f"device_legs={len([k for k in legs4 if k.startswith(('term_', 'kill_'))])}")

    # 5 split sentinel
    sp = m["capture_split_sentinel_r77_probe"]
    cross, under = sp["crossing"], sp["undershoot"]
    sib = cross.get("siblings") or {}
    first = sib.get("rot-01.wav") or {}
    bad = []
    if under.get("requested_path_exists") is not True or \
            list(under.get("siblings") or {}) != ["rot.wav"]:
        bad.append("undershoot shape")
    if cross.get("requested_path_exists") is not False:
        bad.append("crossing: requested path exists")
    if first.get("bytes") != SPLIT_TOTAL:
        bad.append(f"rot-01.wav bytes={first.get('bytes')}")
    if first.get("data_declared") != SPLIT_DATA:
        bad.append(f"rot-01.wav declared={first.get('data_declared')}")
    if first.get("riff_size_field") != "other":
        bad.append(f"rot-01.wav riff={first.get('riff_size_field')}")
    if cross.get("byte_capped") or under.get("byte_capped"):
        bad.append("a split leg tripped its own byte watchdog")
    row("5 split sentinel: silent rename to -01/-02, requested path never "
        "exists, finalized member declares 0x7FFFFFFF",
        not bad, "; ".join(bad) or
        f"rot-01={first.get('bytes')} B declared="
        f"{hex(first.get('data_declared', 0))} siblings={sorted(sib)} "
        f"peak={cross.get('peak_dir_bytes')} "
        f"cap={cross.get('byte_cap')} rename_is_silent="
        f"{sp.get('rename_is_silent')}")

    # 6 format axis
    fm = m["capture_format_axis_r77_probe"]
    legs6 = fm["legs"]
    bad = []
    for name, leg in legs6.items():
        exp = leg.get("expected_fmt") or {}
        got = leg.get("file", {}).get("fmt") or {}
        for k, want in exp.items():
            if got.get(k) != want:
                bad.append(f"{name}: fmt.{k}={got.get(k)} != {want}")
        if leg.get("requested") and not exp:
            if leg.get("error_class") != "usage_refusal":
                bad.append(f"{name}: class={leg.get('error_class')}")
            if leg.get("file", {}).get("exists") is not False:
                bad.append(f"{name}: file left behind")
    if legs6["baseline"]["file"]["bytes"] != 19244:
        bad.append("baseline bytes")
    row("6 format axis: legal requests honored verbatim, refusals leave no "
        "file", not bad, "; ".join(bad) or
        f"{len(legs6)} legs, refusals="
        f"{[k for k, v in legs6.items() if v.get('error_class') == 'usage_refusal']}")
    return rows


if __name__ == "__main__":
    rows = check(sys.argv[1])
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else \
        Path("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/"
             "r77-verifier/v0_claims.json")
    out.write_text(json.dumps({"receipt": sys.argv[1], "rows": rows},
                              indent=2) + "\n")
    for r in rows:
        print(r["verdict"], "|", r["claim"], "|", r["detail"][:200])
    print("receipt:", out)
