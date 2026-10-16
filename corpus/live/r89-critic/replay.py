#!/usr/bin/env python3
"""r89 critic: census + claim table + VERBATIM arm replay.

The four committed verdict blocks are sliced byte-exact out of the
commit object (git show 0d732989:corpus/fixtures/measure_audio.py) at
their `# ---------------- verdicts ----------------` markers and exec'd
against each committed receipt's own recorded `legs`/`entry`. No
paraphrase, no dedent (the slice is exec'd inside `if True:` so its
4-space indent stays byte-exact). Writes census.json / claims.json /
arm-replay.json under corpus/live/r89-critic/.
"""
import copy
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
COMMIT = "0d732989"
FIXTURE = "corpus/fixtures/measure_audio.py"
RUNS = ["20261016T074733533774Z", "20261016T074816877001Z"]
ENTRIES = ["pwprof_gate_r89_probe", "pwprof_oart_r89_probe",
           "pwprof_schema_r89_probe", "pwprof_xw_r89_probe"]

src = subprocess.run(["git", "show", f"{COMMIT}:{FIXTURE}"], cwd=ROOT,
                     capture_output=True, text=True).stdout
lines = src.splitlines(keepends=True)


def fn_name(key):
    """measurements key `pwprof_gate_r89_probe` -> `pwprof_gate_r89_entry`."""
    return key.replace("_probe", "_entry")


def slice_verdict_block(entry_name):
    """Byte-exact slice from the verdict marker to the closing return."""
    start = None
    for i, l in enumerate(lines):
        if l.startswith(f"def {entry_name}()"):
            start = i
            break
    assert start is not None, entry_name
    end = None
    for j in range(start, len(lines)):
        if lines[j].startswith("def ") and j > start:
            end = j
            break
    body = lines[start:end]
    vm = None
    for k, l in enumerate(body):
        if l.strip() == "# ---------------- verdicts ----------------":
            vm = k
            break
    assert vm is not None, entry_name
    tail = None
    for k in range(vm, len(body)):
        if body[k].strip() == 'entry["legs"] = legs':
            tail = k
            break
    assert tail is not None, entry_name
    return "".join(body[vm:tail])


blocks = {e: slice_verdict_block(fn_name(e)) for e in ENTRIES}

# ---------- census + claims ----------
census = {"commit": COMMIT, "runs": {}, "leg_counts": {},
          "verdict_block_shas": {}}
claims = {}
for e in ENTRIES:
    b = blocks[e]
    claims.setdefault("_block_sha256", {})[e] = hashlib.sha256(
        b.encode()).hexdigest()
    (OUT / f"verdict-{e}.py").write_text(b)

for run in RUNS:
    rec = json.loads((ROOT / "corpus/live/runs" /
                      f"{run}-pwprof-r89/measurements.json").read_text())
    m = rec["measurements"]
    ent = {}
    for e in ENTRIES:
        entry = m[e]
        legs = entry["legs"]
        ent[e] = {
            "legs": len(legs),
            "leg_names": list(legs),
            "failures": entry.get("failures"),
            "coverage_blocked": entry.get("coverage_blocked"),
            "blocked": entry.get("blocked"),
            "unloads": entry.get("unloads"),
            "sinks_gone": entry.get("sinks_gone"),
            "own_nodes_after": entry.get("own_nodes_after"),
            "loadavg": entry.get("loadavg"),
            "refs": entry.get("refs"),
            "residual_destroy": entry.get("residual_destroy"),
            "contention_quiet": (entry.get("contention") or {})
                                .get("host_is_quiet"),
        }
    census["runs"][run] = {"mode": rec.get("mode"),
                           "entries": ent,
                           "legs_total": sum(v["legs"] for v in ent.values()),
                           "top_level_keys": sorted(rec.keys())}

# per-leg claim table: what the arms read, and whether it is recorded
for run in RUNS:
    rec = json.loads((ROOT / "corpus/live/runs" /
                      f"{run}-pwprof-r89/measurements.json").read_text())
    m = rec["measurements"]
    c = {}
    for e in ENTRIES:
        for name, leg in m[e]["legs"].items():
            c[f"{e}:{name}"] = {
                "keys": sorted(leg) if isinstance(leg, dict) else None,
                "exit_code": leg.get("exit_code") if isinstance(leg, dict)
                else None,
                "alive_at_sig": leg.get("alive_at_sig")
                if isinstance(leg, dict) else None,
                "error_class": leg.get("error_class")
                if isinstance(leg, dict) else None,
            }
    claims[run] = c

# ---------- verbatim replay ----------
def replay(block, entry):
    legs = entry["legs"]
    failures = []
    env = {"legs": legs, "entry": copy.deepcopy(entry),
           "failures": failures, "json": json, "signal": __import__(
               "signal"), "set": set, "sorted": sorted, "len": len,
           "float": float, "all": all, "any": any, "range": range}
    if True:
        exec(compile("if True:\n" + block,
                     f"verdict-{entry['probe']}", "exec"), env)
    return failures, env["entry"].get("coverage_blocked")


replay_res = {"commit": COMMIT, "runs": {}}
for run in RUNS:
    rec = json.loads((ROOT / "corpus/live/runs" /
                      f"{run}-pwprof-r89/measurements.json").read_text())
    m = rec["measurements"]
    rr = {}
    for e in ENTRIES:
        f, cb = replay(blocks[e], m[e])
        rr[e] = {"failures": f, "coverage_blocked": cb}
    replay_res["runs"][run] = rr

(OUT / "census.json").write_text(json.dumps(census, indent=2) + "\n")
(OUT / "claims.json").write_text(json.dumps(claims, indent=2) + "\n")
(OUT / "arm-replay.json").write_text(json.dumps(replay_res, indent=2) + "\n")

print("== census ==")
for run in RUNS:
    print(run, "legs_total", census["runs"][run]["legs_total"],
          "mode", census["runs"][run]["mode"])
    for e in ENTRIES:
        v = census["runs"][run]["entries"][e]
        print("   ", e, v["legs"], "fail", v["failures"],
              "cb", v["coverage_blocked"], "sinks_gone",
              v["sinks_gone"], "own_after", v["own_nodes_after"])
print("== replay ==")
for run in RUNS:
    for e in ENTRIES:
        v = replay_res["runs"][run][e]
        print(run, e, "failures", len(v["failures"]), v["failures"][:3],
              "cb", v["coverage_blocked"])
