#!/usr/bin/env python3
"""r87 simplifier — receipt census (R1-R12) over BOTH pinned green runs.

The two author runs are the replay oracle; this seat runs no live
family replay.  Every check reads the committed receipt bytes and
asserts the surfaces the fold touches (or must not touch) are identical
to what the author table claims.
"""
import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]          # audio-shokunin/
RUNS = {
    "A": ROOT / "corpus/live/runs/20261016T070036115509Z-pwbind-r87/measurements.json",
    "B": ROOT / "corpus/live/runs/20261016T070305393338Z-pwbind-r87/measurements.json",
}
EXPECT_SHA = {
    "A": "01f04d354f2186dbcf4bc984e2d62a49f378ea8ca2f810d79c7586797d1f1667",
    "B": "2970c944375f2e3b8b6f3ab16bdd5a343521222844d9a3a044a0a7d9a974a655",
}
ENTRIES = ("pwbind_modes_r87_probe", "pwbind_target_r87_probe",
           "pwbind_cli_r87_probe", "pwbind_midi_r87_probe")

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(f"{'PASS' if ok else 'FAIL'}  {name}  {detail}")


R = {}
for tag, p in RUNS.items():
    R[tag] = json.loads(p.read_text())

# ------------------------------------------------------------------ R1
sha_ok = True
for tag, p in RUNS.items():
    got = hashlib.sha256(p.read_bytes()).hexdigest()
    sha_ok &= got == EXPECT_SHA[tag]
check("R1 receipt shas match the author table", sha_ok,
      " ".join(f"{t}:{hashlib.sha256(RUNS[t].read_bytes()).hexdigest()[:16]}"
               for t in RUNS))

# ------------------------------------------------------------------ R2
raw = {t: RUNS[t].read_text() for t in RUNS}
check("R2 no LINK_WAIT/TAP_WAIT surface in either receipt",
      all("LINK_WAIT" not in raw[t] and "TAP_WAIT" not in raw[t] for t in RUNS),
      "the two dead constants have zero receipt surface")

# ------------------------------------------------------------------ R3
ok = True
det = []
shapes = {}
for t in RUNS:
    for e in ENTRIES:
        un = R[t]["measurements"][e].get("unloads") or {}
        for tag, rec in un.items():
            if rec.get("skipped") == "not_listed":
                shapes.setdefault("not_listed", 0)
                shapes["not_listed"] += 1
                if rec.get("verified_index") is not None or \
                        "recycled" in rec or "exit_code" in rec:
                    ok = False
                    det.append(f"{t}/{e}/{tag}:{rec}")
            elif rec.get("verified_index") == rec.get("captured") and \
                    rec.get("recycled") is False and rec.get("exit_code") == 0:
                shapes.setdefault("fired", 0)
                shapes["fired"] += 1
            else:
                ok = False
                det.append(f"{t}/{e}/{tag}:{rec}")
check("R3 unloads are either name-verified-fired or not_listed-skipped",
      ok, f"{shapes}" if ok else str(det))
# the cli entry's module was already destroyed by id (destroy_sink_module
# leg) — its teardown unload is the designed not_listed skip, not a miss
ok = all(R[t]["measurements"]["pwbind_cli_r87_probe"]["unloads"][
             next(iter(R[t]["measurements"]["pwbind_cli_r87_probe"]["unloads"]))
         ].get("skipped") == "not_listed" for t in RUNS)
check("R3b cli unload is the designed not_listed skip (module destroyed by id)",
      ok)

# ------------------------------------------------------------------ R4
ok = True
det = []
for t in RUNS:
    for e in ENTRIES:
        m = R[t]["measurements"][e]
        if m.get("sinks_gone") not in ({}, ) and not all(
                (m.get("sinks_gone") or {}).values()):
            ok = False
            det.append(f"{t}/{e}/sinks_gone={m.get('sinks_gone')}")
        if m.get("own_nodes_after") != []:
            ok = False
            det.append(f"{t}/{e}/own_nodes_after={m.get('own_nodes_after')}")
        if m.get("foreign_r87a_nodes") != []:
            ok = False
            det.append(f"{t}/{e}/foreign={m.get('foreign_r87a_nodes')}")
check("R4 sinks_gone all true / own_nodes_after [] / no foreign residue",
      ok, "all 4 entries x2" if ok else str(det))

# ------------------------------------------------------------------ R5
ok = all("coverage_blocked" not in R[t]["measurements"][e] and
         "blocked" not in R[t]["measurements"][e]
         for t in RUNS for e in ENTRIES)
check("R5 no coverage_blocked/blocked on any entry (both runs green)", ok)

# ------------------------------------------------------------------ R6
ok = all(R[t]["measurements"][e].get("failures") == []
         for t in RUNS for e in ENTRIES)
check("R6 failures [] on all 4 entries x2", ok)

# ------------------------------------------------------------------ R7
ok = True
det = []
for t in RUNS:
    cli = R[t]["measurements"]["pwbind_cli_r87_probe"]["legs"]
    regs = cli["regions"]
    solo = regs["solo"]["median_peak"]
    if not (8192 * 0.85 <= solo <= 8192 * 1.18):
        ok = False
        det.append(f"{t}/solo={solo}")
    if abs(regs["vol25"]["median_peak"] / solo - 0.25) > 1e-9:
        ok = False
        det.append(f"{t}/vol25={regs['vol25']['median_peak']}")
    if abs(regs["restore"]["median_peak"] / solo - 1.0) > 1e-9:
        ok = False
        det.append(f"{t}/restore={regs['restore']['median_peak']}")
    if regs["mute"]["median_peak"] != 0.0:
        ok = False
        det.append(f"{t}/mute={regs['mute']['median_peak']}")
    if abs(regs["unmute"]["median_peak"] / solo - 1.0) > 1e-9:
        ok = False
        det.append(f"{t}/unmute={regs['unmute']['median_peak']}")
    for wn in ("w_v25", "w_v10", "w_mute", "w_unmute", "w_unk"):
        w = cli["writes"][wn]
        if w.get("exit_code") != 0 or w.get("errors"):
            ok = False
            det.append(f"{t}/{wn}:{w.get('exit_code')}/{w.get('errors')}")
check("R7 dsp regions exact ratios + all 5 writes rc=0/errors=[]", ok,
      f"solo={[R[t]['measurements']['pwbind_cli_r87_probe']['legs']['regions']['solo']['median_peak'] for t in RUNS]}"
      if ok else str(det))

# ------------------------------------------------------------------ R8
ok = True
det = []
for t in RUNS:
    cli = R[t]["measurements"]["pwbind_cli_r87_probe"]["legs"]
    tgt = R[t]["measurements"]["pwbind_target_r87_probe"]
    # solo window (solo_hi read) is the fold's T5 surface
    for name in ("solo", "vol25", "restore", "mute", "unmute"):
        tt = cli["regions"][name]["t"]
        if not (isinstance(tt, list) and len(tt) == 2 and tt[1] > tt[0]):
            ok = False
            det.append(f"{t}/{name}:{tt}")
    # DEF (the fold's T7 surface): the recorded default is stable
    if not tgt.get("default_sink_at_start") or \
            tgt.get("default_sink_at_start") != tgt.get("default_sink_at_end"):
        ok = False
        det.append(f"{t}/DEF={tgt.get('default_sink_at_start')}")
    # p_coll consumers (T9 surface)
    pc = tgt["legs"]["p_coll"]["consumers"]
    if len(pc) != 1:
        ok = False
        det.append(f"{t}/p_coll={pc}")
    # cold_nowarm blob (T8 surface)
    blob = (cli["cold_nowarm"].get("stdout") or "") + \
        (cli["cold_nowarm"].get("stderr") or "")
    if "unknown global" not in blob:
        ok = False
        det.append(f"{t}/cold blob missing")
check("R8 fold-touched surfaces recorded as expected", ok,
      "regions windows + stable DEF + 1-consumer p_coll + cold blob" if ok
      else str(det))

# ------------------------------------------------------------------ R9
ok = True
det = []
for t in RUNS:
    live = R[t]["measurements"]["pwbind_midi_r87_probe"]["legs"]["mdump_live"]["attempts"]
    noted = [a for a in live if a.get("node")]
    if not noted or not any("Note On" in (a.get("stdout") or "") for a in noted):
        ok = False
        det.append(f"{t}/attempts={len(live)} noted={len(noted)}")
    pin = R[t]["measurements"]["pwbind_midi_r87_probe"]["legs"]["pin"]
    f = pin.get("file") or {}
    if not f.get("has_mthd") or not all(f.get("note_ons") or []):
        ok = False
        det.append(f"{t}/pin={f}")
check("R9 mdump_live published+pinned and pin SMF carries the events", ok,
      "both runs" if ok else str(det))

# ------------------------------------------------------------------ R10
ok = True
det = []
for t in RUNS:
    vl = R[t]["measurements"]["pwbind_cli_r87_probe"]["legs"]["volume_legs"]
    r50 = vl["v050"].get("ratio_vs_v100")
    r150 = vl["v150"].get("ratio_vs_v100")
    if r50 is None or not (0.40 <= r50 <= 0.60):
        ok = False
        det.append(f"{t}/v050={r50}")
    if r150 is None or not (1.35 <= r150 <= 1.65):
        ok = False
        det.append(f"{t}/v150={r150}")
    if vl["v000"].get("median_peak") != 0.0:
        ok = False
        det.append(f"{t}/v000={vl['v000'].get('median_peak')}")
check("R10 --volume ratios v050/v150/v000 in envelope", ok,
      "both runs" if ok else str(det))

# ------------------------------------------------------------------ R11
ok = all(R[t].get("mode") == "probe-pwbind-r87" and
         all(e in R[t]["measurements"] for e in ENTRIES) for t in RUNS)
check("R11 mode + 4 r87 entries present in both receipts", ok)

# ------------------------------------------------------------------ R12
ok = True
det = []
for t in RUNS:
    for e in ENTRIES:
        m = R[t]["measurements"][e]
        if m.get("probe") is None or not str(m.get("probe")).startswith("r87a"):
            ok = False
            det.append(f"{t}/{e}/probe={m.get('probe')}")
check("R12 entry probe strings are the r87a namespace", ok,
      "all 8 entries" if ok else str(det))

bad = [n for n, ok, _ in results if not ok]
print(f"\n{len(results) - len(bad)}/{len(results)} PASS")
sys.exit(1 if bad else 0)
