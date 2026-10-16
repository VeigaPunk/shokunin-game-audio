#!/usr/bin/env python3
"""r89 critic: nested-field vacuity sweep + error-class lattice probe.

(1) Deletes each key inside `stats` (s_window) / `info`+`enum`
    (x_profobj) / `own_row` (x_top) one at a time and re-runs the
    verbatim committed verdict block. GREEN on deletion = fail-open.
(2) Slices `_pwprof_r89_errclass` (and the inherited r88 table it
    falls back to) verbatim out of the commit and probes the
    precedence lattice with synthetic texts.
"""
import copy
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
COMMIT = "0d732989"
FIXTURE = "corpus/fixtures/measure_audio.py"
RUN = "20261016T074733533774Z"
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


rec = json.loads((ROOT / "corpus/live/runs" /
                  f"{RUN}-pwprof-r89/measurements.json").read_text())
base = rec["measurements"]

report = {"run": RUN, "nested": []}
NESTED = [("pwprof_schema_r89_probe", "s_window", "stats"),
          ("pwprof_xw_r89_probe", "x_profobj", "info"),
          ("pwprof_xw_r89_probe", "x_profobj", "enum"),
          ("pwprof_xw_r89_probe", "x_top", "own_row")]
for e, leg, sub in NESTED:
    for key in sorted(base[e]["legs"][leg].get(sub) or {}):
        mut = copy.deepcopy(base)
        mut[e]["legs"][leg][sub].pop(key)
        got, fails, cb = run_block(e, mut[e])
        report["nested"].append({"entry": e, "leg": leg, "sub": sub,
                                 "key": key, "got": got,
                                 "failures": fails[:1],
                                 "cb": (cb[-1] if cb else None)})

# ---------- error-class lattice, sliced verbatim ----------
def slice_def(name):
    start = next(i for i, l in enumerate(lines)
                 if l.startswith(f"def {name}("))
    end = next(j for j in range(start + 1, len(lines))
               if lines[j].startswith("def ") or
               (lines[j].strip() and not lines[j].startswith((" ", ")", "}"))))
    return "".join(lines[start:end])


class_src = ""


def top_level_blocks(pattern):
    """Every top-level block whose header line matches `pattern`."""
    import re as _re
    out = []
    i = 0
    while i < len(lines):
        if _re.match(pattern, lines[i]):
            j = i + 1
            while j < len(lines) and (not lines[j].strip() or
                                      lines[j][0] in " \t)"):
                j += 1
            out.append("".join(lines[i:j]))
            i = j
        else:
            i += 1
    return out


# the whole error-class chain: every table + every resolver, verbatim
for pat in (r"^_[A-Z0-9_]*ERR_CLASSES\s*=", r"^def _[a-z0-9_]*errclass\("):
    class_src += "".join(top_level_blocks(pat))

env = {"re": __import__("re")}
exec(compile(class_src, "class-lattice", "exec"), env)
errclass = env["_pwprof_r89_errclass"]

CASES = [
    ("connect_down", "pw-profiler: Can't connect to server: Host is down",),
    ("cant_open", "pw-profiler: Can't open file '.': Is a directory",),
    ("opt", "pw-profiler: unrecognized option '--r89bogus'",),
    ("opt_after_connect",
     "Can't connect to server: Host is down\nunrecognized option '--x'",),
    ("connect_before_opt",
     "unrecognized option '--x'\nCan't connect to server: Host is down",),
    # r89-local table must shadow the identical inherited r88 regex
    # (`pwtop_connect_down` carries the same pattern).
    ("r89_shadows_r88_connect",
     "Can't connect to server: Host is down"),
    ("r89_vs_r88_opt",
     "invalid option -- 'x'\nunrecognized option '--x'"),
    ("r88_fallback_only",
     'Error: "unsupported type PipeWire:Interface:Profiler"'),
    ("empty", ""),
    ("noise", "logging 12 samples"),
]
lattice = []
for name, text in CASES:
    cls, hit = errclass(text)
    lattice.append({"case": name, "text": text, "class": cls,
                    "hit": hit})
report["class_lattice"] = lattice
report["class_src_sha256"] = __import__("hashlib").sha256(
    class_src.encode()).hexdigest()

(OUT / "nested-sweep.json").write_text(json.dumps(report, indent=2) + "\n")
print("nested deletions:", len(report["nested"]))
for k in report["nested"]:
    flag = "  <-- FAIL-OPEN" if k["got"] == "GREEN" else ""
    print(f"  {k['entry']}.{k['leg']}.{k['sub']}.{k['key']}: {k['got']}{flag}")
print("class lattice:")
for l in lattice:
    print("  ", l["case"], "->", l["class"], "|", (l["hit"] or "")[:50])
