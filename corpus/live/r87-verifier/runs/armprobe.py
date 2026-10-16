#!/usr/bin/env python3
"""r87-verifier arm probe: (a) execute the committed `mdump_live` verdict
slice (extracted verbatim by anchor from the frozen-tree fixture) against
synthetic realizations, either-way; (b) static occurrence scan of the
declared record-only rows inside the committed r87 block.
"""
import json
import sys
import textwrap

FIXTURE = sys.argv[1] if len(sys.argv) > 1 else \
    "corpus/live/r87-verifier/tree/corpus/fixtures/measure_audio.py"
A1 = sys.argv[2] if len(sys.argv) > 2 else \
    "corpus/live/runs/20261016T070036115509Z-pwbind-r87/measurements.json"


def main():
    src = open(FIXTURE).read()
    start = src.index('    live = legs["mdump_live"]["attempts"]')
    end = src.index('    for name in ("pactl_raop"', start)
    slice_ = textwrap.dedent(src[start:end])
    out = {"slice": slice_, "cases": []}

    def run_case(name, attempts):
        ns = {"legs": {"mdump_live": {"attempts": attempts}},
              "failures": [], "entry": {}}
        exec(compile(slice_, "<mdump_slice>", "exec"), ns)
        out["cases"].append({
            "case": name,
            "attempts": attempts,
            "failures": ns["failures"],
            "coverage_blocked": ns["entry"].get("coverage_blocked")})

    real = json.load(open(A1))["measurements"]["pwbind_midi_r87_probe"][
        "legs"]["mdump_live"]["attempts"]
    run_case("real A1 (published+notes)", real)
    run_case("synthetic: 3 attempts, no node",
             [{"attempt": i, "node": False} for i in range(3)])
    run_case("synthetic: node published, no Note lines",
             [{"attempt": 0, "node": True, "stdout": "no notes here"}])
    run_case("synthetic: attempts list empty (bridge absent path)",
             [])

    # static occurrence scan of declared record-only rows
    block = src[src.index("# r87: the DEVICE-BINDING lattice"):
                src.index("def pwbind_mix_r87") if
                "def pwbind_mix_r87" in src else len(src)]
    scan = {}
    for name in ("wake_after_suspend", "remote_stall", "collision_objects",
                 "tap_windows", "foreign_candidates", "foreign_r87a_nodes",
                 "m_sysex", "props_unk", "fmt_unlinked"):
        lines = [i + 1 for i, ln in enumerate(src.splitlines())
                 if name in ln and src.index("# r87: the DEVICE-BINDING"
                                            " lattice") <
                 len("\n".join(src.splitlines()[:i])) + 1]
        occ = [(i + 1, ln.strip()[:110]) for i, ln in enumerate(
            src.splitlines()) if name in ln]
        armed = [o for o in occ
                 if "failures.append" in o[1] or "!= 0" in o[1] or
                 "!= 0" in o[1]]
        scan[name] = {"n_occurrences": len(occ),
                      "in_failure_or_armed_lines": armed,
                      "all": occ}
    out["scan"] = scan
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
