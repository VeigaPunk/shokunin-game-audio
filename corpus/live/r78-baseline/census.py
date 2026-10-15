#!/usr/bin/env python3
"""r78-baseline census + write-scope accounting.

 - canonical corpus/live/runs: receipt-dir count, committed blob count at the
   frozen anchor (git ls-tree), and the set of canonical receipt dirs whose
   mtime falls inside this seat's replay window (attributed to other seats).
 - proof that no ledger receipt path leaves the env tree (env infix check).
 - post-replay fixture re-check: re-hash the probed fixture members against the
   frozen blobs.
Writes census.txt + runs-canonical-after.txt + post-replay-fixture-check.txt.
"""
import calendar
import json
import re
import subprocess
import time
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
FROZEN = "731937ccf731c711b54942d22ae4f32b7683c498"
INFIX = "corpus/live/r78-baseline/measure-env/"
RUNS = REPO / "corpus" / "live" / "runs"
# replay window (first and last receipt timestamps of this seat's ledger)
LEDGER = HERE / "ledger-r78-baseline.tsv"


def git(*a, text=True):
    return subprocess.run(["git", *a], cwd=REPO, capture_output=True,
                          text=text).stdout


def main():
    rows = [l.split("\t") for l in LEDGER.read_text().splitlines() if l.strip()]
    fresh = [Path(r[2]) for r in rows]
    out = []
    out.append(f"ledger rows: {len(rows)}")
    outside = [str(p) for p in fresh if INFIX not in str(p)]
    out.append(f"receipt paths outside the env tree: {len(outside)} "
               f"{outside[:3]}")
    stamps = sorted(p.parent.name[:15] for p in fresh)
    out.append(f"replay window (from ledger dir names): {stamps[0]} -> "
               f"{stamps[-1]}")
    canon = sorted(RUNS.glob("*/measurements.json"))
    out.append(f"canonical corpus/live/runs receipt dirs now: {len(canon)}")
    committed = git("ls-tree", "-r", "--name-only", FROZEN,
                    "corpus/live/runs/").split()
    committed = [p for p in committed if p.endswith("measurements.json")]
    out.append(f"committed receipt blobs @ {FROZEN[:9]}: {len(committed)}")
    live = git("ls-tree", "-r", "--name-only", "HEAD", "corpus/live/runs/").split()
    live = [p for p in live if p.endswith("measurements.json")]
    out.append(f"committed receipt blobs @ HEAD: {len(live)} "
               f"(diff vs frozen: {len(live) - len(committed)})")
    # canonical receipts touched inside the replay window
    t0 = calendar.timegm(time.strptime(stamps[0], "%Y%m%dT%H%M%S")) - 60
    recent = []
    for p in canon:
        st = p.stat().st_mtime
        if st >= t0:
            recent.append(f"{time.strftime('%H:%M:%SZ', time.gmtime(st))} "
                          f"{p.parent.name}")
    out.append(f"canonical receipt dirs with mtime >= replay start - 60 s: "
               f"{len(recent)}")
    out += ["  " + r for r in sorted(recent)[-40:]]
    (HERE / "census.txt").write_text("\n".join(out) + "\n")
    (HERE / "runs-canonical-after.txt").write_text(
        "\n".join(str(p.parent.name) for p in canon) + "\n")
    print("\n".join(out))

    # archive receipt check: tar members vs git ls-files at the frozen anchor
    arc = []
    manifest = HERE / "frozen" / "archive-manifest.txt"
    members = [m for m in manifest.read_text().splitlines()]
    files = [m for m in members if not m.endswith("/")]
    dirs = len(members) - len(files)
    # -z: raw (unquoted) path names — paths with spaces/quotes otherwise
    # appear as quoted fragments and fake a symmetric difference.
    raw = git("ls-tree", "-r", "-z", "--name-only", FROZEN)
    tracked = set(x for x in raw.split("\0") if x)
    arc.append(f"tar members={len(members)} (files={len(files)} dirs={dirs})")
    arc.append(f"git ls-tree -r -z @ {FROZEN[:9]} = {len(tracked)}")
    arc.append(f"files-only diff vs tracked: {len(set(files) ^ tracked)} "
               f"entries symmetric-difference")
    arc.append(f"archive sha256: "
               f"{(HERE / 'frozen' / 'archive-sha256.txt').read_text().strip()}")
    arc.append(f"archive bytes: {(HERE / 'frozen' / 'head-731937c.tar').stat().st_size}")
    arc.append(f"node_modules members: "
               f"{sum('node_modules' in m for m in members)}")
    # committed ledger anchor
    led = "corpus/live/r70-author/ledger-r71.tsv"
    for ref in (FROZEN, "HEAD"):
        blob = subprocess.run(["git", "rev-parse", f"{ref}:{led}"], cwd=REPO,
                              capture_output=True, text=True).stdout.strip()
        arc.append(f"{led} @ {ref[:9]}: blob {blob}")
    # live-tree state after the replay (other seats' in-flight work)
    arc.append(f"live HEAD now: {git('rev-parse', 'HEAD').strip()}")
    arc.append("worktree dirty (git status --porcelain, tracked only):")
    for line in git("status", "--porcelain", "--untracked-files=no").splitlines():
        arc.append("  " + line)
    (HERE / "archive-check.txt").write_text("\n".join(arc) + "\n")
    print("\n".join(arc))

    # post-replay fixture re-check (probed members + the fixture sources)
    check = []
    probes = [
        "corpus/fixtures/measure_audio.py",
        "corpus/fixtures/build_artifacts.py",
        "corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc",
        "corpus/fixtures/__pycache__/build_artifacts.cpython-314.pyc",
    ]
    artifacts = [p for p in git("ls-files", "corpus/artifacts").split()]
    for rel in probes + artifacts[:6]:
        wt = sha256((REPO / rel).read_bytes()).hexdigest()
        blob = sha256(subprocess.run(["git", "show", f"{FROZEN}:{rel}"],
                                     cwd=REPO, capture_output=True).stdout
                      ).hexdigest()
        check.append(f"{'EQUAL' if wt == blob else 'DIFF'} {rel} {wt}")
    (HERE / "post-replay-fixture-check.txt").write_text(
        "\n".join(check) + "\n")
    print("\n".join(check))


if __name__ == "__main__":
    main()
