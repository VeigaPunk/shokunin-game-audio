#!/usr/bin/env python3
"""r78-baseline commit watch (bounded): polls HEAD every POLL_S until the r77
author work commit lands — a commit whose diff vs the frozen anchor touches
corpus/fixtures/measure_audio.py — or WINDOW_S elapses. Logs every distinct
HEAD with its subject and whether measure_audio.py is in its diff.
Writes commit-watch.txt.
"""
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
FROZEN = "731937ccf731c711b54942d22ae4f32b7683c498"
OUT = HERE / "commit-watch.txt"
POLL_S = 20
WINDOW_S = 1800


def git(*a):
    return subprocess.run(["git", *a], cwd=REPO, capture_output=True,
                          text=True).stdout.strip()


def main():
    t0 = time.time()
    seen = set()
    with OUT.open("a") as fh:
        fh.write(f"=== commit watch start {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} "
                 f"frozen={FROZEN[:7]} window={WINDOW_S}s ===\n")
        fh.flush()
        while time.time() - t0 < WINDOW_S:
            head = git("rev-parse", "HEAD")
            if head not in seen:
                seen.add(head)
                subj = git("log", "-1", "--format=%s", head)
                names = git("diff", "--name-only", FROZEN, head).splitlines()
                touches = "corpus/fixtures/measure_audio.py" in names
                fh.write(f"{time.strftime('%H:%M:%SZ', time.gmtime())} {head[:9]} "
                         f"author_commit={touches} paths={len(names)} {subj}\n")
                fh.flush()
                if touches:
                    print(f"AUTHOR COMMIT {head}", file=sys.stderr)
                    return
            time.sleep(POLL_S)
        fh.write("=== window elapsed without an author commit ===\n")


if __name__ == "__main__":
    main()
