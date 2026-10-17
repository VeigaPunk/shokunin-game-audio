#!/usr/bin/env python3
"""r82-simplifier receipt census over the four pinned author runs.

Confirms the 0-hit facts the deletions rest on. Read-only; exit 0 = all
facts hold. Run from the repo root:
    python3 receipt-census.py
"""
import glob
import json
import sys

RUNS = sorted(glob.glob("corpus/live/r82-author/ffmpeg-r82-runs/"
                        "*.measurements.json"))
assert len(RUNS) == 4, RUNS
fails = []


def check(cond, msg):
    print(("PASS  " if cond else "FAIL  ") + msg)
    if not cond:
        fails.append(msg)


entries = {}
for p in RUNS:
    d = json.load(open(p))
    entries[p] = d["measurements"]

print("== A: all 8 r82 entries green in all 4 runs ==")
for p, m in entries.items():
    r82 = {k: v for k, v in m.items() if k.startswith("ffpw_")}
    check(len(r82) == 8 and all(v.get("failures") == [] for v in r82.values()),
          f"{p.split('/')[-1]}: {len(r82)} entries, "
          f"failures={ {k: v.get('failures') for k, v in r82.items() if v.get('failures') != []} }")

print("\n== B: T5 — e1..e6 'out' is null in every run (check can never fire) ==")
ok = True
for p, m in entries.items():
    legs = m["ffpw_error_classes_r82_probe"]["legs"]
    for k in sorted(legs):
        if legs[k].get("out") is not None:
            ok = False
            print(f"      {p}: {k} out={legs[k].get('out')}")
check(ok, "e1..e6 out is None in all 4 runs (6 legs x 4)")

print("\n== C: T7 — d2 carries no 'starred' leaf; d3/d4 do ==")
for p, m in entries.items():
    legs = m["ffpw_device_surfaces_r82_probe"]["legs"]
    check("starred" not in legs["d2_sources_pipewire"] and
          "starred" in legs["d3_sources_pulse"] and
          "starred" in legs["d4_sinks_pulse"],
          f"{p.split('/')[-1]}: d2 no starred, d3/d4 starred present")

print("\n== D: T10 — kill_watch fired with sigkilled:true; no 'missing' ==")
for p, m in entries.items():
    tl = m["ffpw_target_loss_r82_probe"]["legs"]
    fired = [f for leg in tl.values() if isinstance(leg, dict)
             for f in (leg.get("fired") or []) if f.get("kind") == "kill_watch"]
    res = [f["result"] for f in fired]
    check(len(fired) == 3 and all(r == {"sigkilled": True} for r in res),
          f"{p.split('/')[-1]}: 3 kill_watch events, results={res}")

print("\n== E: T6 — d0 device rows complete + stable across the two reps ==")
want = {"alsa": "DE", "pulse": "DE", "jack": "D.", "oss": "DE", "sndio": "DE"}
for p, m in entries.items():
    legs = m["ffpw_device_surfaces_r82_probe"]["legs"]
    r0 = legs["d0_devices_r0"]["audio_rows"]
    r1 = legs["d0_devices_r1"]["audio_rows"]
    pinned = {k: r0.get(k) for k in want}
    check(pinned == want and r1 == r0 and "pipewire" not in r0,
          f"{p.split('/')[-1]}: pinned subset {pinned}, no pipewire row, "
          f"reps equal")

print("\n== F: 0-hit arm census (armed envelopes, never realized) ==")
for p, m in entries.items():
    c3 = m["ffpw_capture_lattice_r82_probe"]["c3_default_realizations"]
    a5 = m["ffpw_alsa_split_r82_probe"]["a5_realization"]
    check(c3 == ["eio_251"] * 3 and a5 == "params_251",
          f"{p.split('/')[-1]}: c3={c3} a5={a5}")
killed = {}
for p, m in entries.items():
    for k, v in m.items():
        if not k.startswith("ffpw_"):
            continue
        for ln, leg in (v.get("legs") or {}).items():
            if isinstance(leg, dict) and leg.get("killed"):
                killed.setdefault(leg["killed"], 0)
                killed[leg["killed"]] += 1
check(not killed, f"no wallcap/bytecap kills in any r82 leg (got {killed})")

print("\n== G: error-class vocabulary realized (context) ==")
cls = set()
for p, m in entries.items():
    for k, v in m.items():
        if not k.startswith("ffpw_"):
            continue
        for leg in (v.get("legs") or {}).values():
            if isinstance(leg, dict) and leg.get("error_class"):
                cls.add(leg["error_class"])
print(f"      realized: {sorted(cls)}")
check(cls == {"ff_unknown_format", "ff_libio_error".replace("ff_libio_error",
      "ff_io_error"), "ff_no_such_process", "ff_access_denied",
      "ff_pulse_sink_info", "ff_sched_assert", "ff_option_range",
      "ff_libpulse_assert", "ff_alsa_busy", "ff_alsa_params",
      "ff_alsa_unknown_pcm"},
      "every tuple class except the other_error catch-all is realized")

print()
if fails:
    print(f"RESULT: {len(fails)} FAILURE(S)")
    sys.exit(1)
print("RESULT: ALL RECEIPT FACTS HOLD")
