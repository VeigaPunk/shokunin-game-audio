#!/usr/bin/env python3
"""r77 verifier — prior-row stability: run `--probe-capture-r76` on the
post-r77 fixture and diff the receipt against the committed PRE-r77
receipt (written 19:30:39Z by a different seat, working tree clean at
HEAD 503689c, i.e. HEAD's measure_audio.py before the r77 edit).

Usage: v6_prior_r76.py [baseline_receipt]
Writes corpus/live/r77-verifier/v6_prior_r76.json + a run receipt under
corpus/live/runs/ (written by the fixture itself).
"""
import json
import subprocess
import sys
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
OUT = REPO / "corpus/live/r77-verifier"
DEFAULT_BASE = (REPO / "corpus/live/runs/"
                "20261014T193039362478Z-capture-r76/measurements.json")


def flatten(obj, prefix=""):
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.update(flatten(v, f"{prefix}/{k}"))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.update(flatten(v, f"{prefix}/{i}"))
    else:
        out[prefix] = obj
    return out


def main():
    base_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_BASE
    proc = subprocess.run([sys.executable,
                           str(REPO / "corpus/fixtures/measure_audio.py"),
                           "--probe-capture-r76"],
                          capture_output=True, text=True, timeout=1200,
                          cwd=str(REPO))
    (OUT / "v6_r76.stdout.json").write_text(proc.stdout)
    (OUT / "v6_r76.stderr.log").write_text(proc.stderr)
    entry = {"probe": "r77-verifier prior r76 row stability",
             "baseline": str(base_path.relative_to(REPO)),
             "rc": proc.returncode,
             "failures": []}
    try:
        new = json.loads(proc.stdout)["receipt"]
    except (ValueError, KeyError):
        entry["failures"].append("the r76 run produced no receipt json")
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "v6_prior_r76.json").write_text(json.dumps(entry, indent=2) + "\n")
        print(json.dumps({"receipt": str(OUT / "v6_prior_r76.json"),
                          "failures": entry["failures"]}))
        return
    entry["new_receipt"] = str(Path(new).relative_to(REPO))
    a = json.loads(Path(base_path).read_text())
    b = json.loads(Path(new).read_text())
    entry["baseline_failures"] = a.get("failures")
    entry["new_failures"] = b.get("failures")
    if a.get("failures") or b.get("failures"):
        entry["failures"].append("a run reported failures")
    fa, fb = flatten(a), flatten(b)
    only_a = sorted(set(fa) - set(fb))
    only_b = sorted(set(fb) - set(fa))
    diffs = [p for p in sorted(set(fa) & set(fb)) if fa[p] != fb[p]]
    entry["keys_baseline"] = len(fa)
    entry["keys_new"] = len(fb)
    entry["only_in_baseline"] = only_a[:40]
    entry["only_in_new"] = only_b[:40]
    entry["diff_leaves"] = [{"path": p, "baseline": fa[p], "new": fb[p]}
                            for p in diffs][:200]
    entry["diff_count"] = len(diffs)
    # the arm's own pinned claims that must be identical
    pinned = [d for d in entry["diff_leaves"] if any(
        s in d["path"] for s in ("/failures", "gate", "oracle", "dev_null",
                                 "pwrecord_monitor_bound", "error_class"))]
    entry["pinned_diff_leaves"] = pinned
    if pinned:
        entry["failures"].append(
            f"{len(pinned)} pinned (deterministic) leaves differ")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "v6_prior_r76.json").write_text(json.dumps(entry, indent=2) + "\n")
    print(json.dumps({"receipt": str(OUT / "v6_prior_r76.json"),
                      "failures": entry["failures"],
                      "diff_count": entry["diff_count"]}))


if __name__ == "__main__":
    main()
