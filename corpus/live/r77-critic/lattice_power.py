#!/usr/bin/env python3
"""r77 CRITIC — battery E: how many lattice rows can separate the law from
the single hypothesis "the target name is ignored and the capture always
consumes the CURRENT DEFAULT sink's monitor"?

Driven by the fixture's own CAPTURE_R77_LATTICE table (imported, not
retyped) and cross-checked against the live r77 receipt and the boundary
seat's moved-default receipt.
"""
import importlib.util
import json
from pathlib import Path

ROOT = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
spec = importlib.util.spec_from_file_location(
    "ma_r77", ROOT / "corpus/fixtures/measure_audio.py")
ma = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ma)

live = json.loads(sorted(
    ROOT.glob("corpus/live/runs/*capture-r77*/measurements.json"))[-1]
    .read_text())["measurements"]["capture_source_lattice_r77_probe"]
bnd = json.loads((ROOT / "corpus/live/r77-boundary/probe-p1c-mechanism.json")
                 .read_text())

print("fixture table (name, resolver, prop, expected node, expected tone):")
fallback_consistent, discriminating = [], []
for name, resolver, prop, exp, tone in ma.CAPTURE_R77_LATTICE:
    leg = live["legs"].get(name, {})
    # H_fallback: target ignored -> the CURRENT default sink's monitor.
    h_fb_node = leg.get("default_sink_at_cell")
    fb_consistent = (exp == "default_sink") and (tone is True)
    (fallback_consistent if fb_consistent else discriminating).append(
        (name, resolver, exp, tone))
    print(f"  {name:28s} prop={str(prop):5s} expect={exp:11s} "
          f"tone={str(tone):5s}  fallback-consistent={fb_consistent}")

print(f"\nrows satisfied by H_fallback ALONE: {len(fallback_consistent)}"
      f"/{len(ma.CAPTURE_R77_LATTICE)}")
for n in fallback_consistent:
    print(f"    {n[0]}")
print(f"rows that can separate the law from H_fallback: "
      f"{len(discriminating)}")
for n in discriminating:
    print(f"    {n[0]} (expect={n[2]}, tone={n[3]})")

print("\nrows whose TARGET is a `.monitor` name:",
      [n for n, r, p, e, t in ma.CAPTURE_R77_LATTICE
       if "monitor" in (r or "")])
print("of those, rows whose target is a NON-default sink's monitor:",
      [n for n, r, p, e, t in ma.CAPTURE_R77_LATTICE
       if r == "other_sink_monitor"])

print("\nboundary seat's falsifying row (default moved to Speaker):")
for row in bnd["moved_matrix"]:
    if "monitor" in row["target"]:
        print(f"  target={row['target'].split('.')[-2]}.monitor "
              f"signature={row['signature']} consumed={row['consumed']}")
print("  -> under the moved default the r77 row would compute "
      f"want={bnd['default_after_move'].split('.')[-2]} and got=the same "
      "node: PASS, whether or not the `.monitor` name resolved.")
print("  -> pw-dump monitor-named nodes: "
      f"{bnd['node_inventory']['monitor_named_nodes']}")
