#!/usr/bin/env python3
"""r89 critic: systematic vacuity sweep.

For every recorded leg key, delete it (one at a time) and re-run the
verbatim committed verdict block. Outcome GREEN = the arm does not read
that key at all (unarmed field: expected for volatile/aux text, a
finding for a claim input). Also deletes each whole leg (loud-fail
check) and each entry-level key.
"""
import copy
import json
import subprocess
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
    return key.replace("_probe", "_entry")


def slice_verdict_block(entry_name):
    start = next(i for i, l in enumerate(lines)
                 if l.startswith(f"def {entry_name}()"))
    end = next(j for j in range(start + 1, len(lines))
               if lines[j].startswith("def "))
    body = lines[start:end]
    vm = next(k for k, l in enumerate(body)
              if l.strip() == "# ---------------- verdicts ----------------")
    tail = next(k for k in range(vm, len(body))
                if body[k].strip() == 'entry["legs"] = legs')
    return "".join(body[vm:tail])


BLOCKS = {e: slice_verdict_block(fn_name(e)) for e in ENTRIES}


def run_block(entry_key, entry):
    env = {"legs": entry["legs"], "entry": copy.deepcopy(entry),
           "failures": []}
    try:
        exec(compile("if True:\n" + BLOCKS[entry_key],
                     f"verdict-{entry_key}", "exec"), env)
    except Exception as exc:
        return "CRASH", [f"{type(exc).__name__}: {exc}"], None
    cb = env["entry"].get("coverage_blocked")
    return ("RED" if env["failures"] else
            "CB" if cb else "GREEN"), env["failures"], cb


run = RUNS[0]
rec = json.loads((ROOT / "corpus/live/runs" /
                  f"{run}-pwprof-r89/measurements.json").read_text())
base = rec["measurements"]

report = {"run": run, "key_deletions": [], "leg_deletions": [],
          "entry_key_deletions": []}

for e in ENTRIES:
    for leg, val in base[e]["legs"].items():
        if not isinstance(val, dict):
            continue
        for key in sorted(val):
            mut = copy.deepcopy(base)
            mut[e]["legs"][leg].pop(key)
            got, fails, cb = run_block(e, mut[e])
            report["key_deletions"].append(
                {"entry": e, "leg": leg, "key": key, "got": got,
                 "failures": fails[:1], "cb": (cb[-1] if cb else None)})

for e in ENTRIES:
    for leg in list(base[e]["legs"]):
        mut = copy.deepcopy(base)
        mut[e]["legs"].pop(leg)
        got, fails, cb = run_block(e, mut[e])
        report["leg_deletions"].append(
            {"entry": e, "leg": leg, "got": got, "failures": fails[:1]})

for e in ENTRIES:
    for key in ("refs", "failures", "coverage_blocked", "unloads",
                "sinks_gone", "own_nodes_after", "loadavg", "tools"):
        if key not in base[e]:
            continue
        mut = copy.deepcopy(base)
        mut[e].pop(key)
        got, fails, cb = run_block(e, mut[e])
        report["entry_key_deletions"].append(
            {"entry": e, "key": key, "got": got, "failures": fails[:1]})

(OUT / "sweep.json").write_text(json.dumps(report, indent=2) + "\n")

green = [k for k in report["key_deletions"] if k["got"] == "GREEN"]
print("key deletions:", len(report["key_deletions"]),
      "unarmed (GREEN):", len(green))
for k in green:
    print("   UNARMED", k["entry"], k["leg"], k["key"])
print("leg deletions:", len(report["leg_deletions"]),
      "outcomes:", {o: sum(1 for k in report["leg_deletions"]
                           if k["got"] == o)
                    for o in ("CRASH", "RED", "CB", "GREEN")})
print("entry-key deletions:")
for k in report["entry_key_deletions"]:
    print("   ", k["entry"], k["key"], k["got"], k["failures"][:1])
