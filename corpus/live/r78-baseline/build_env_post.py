#!/usr/bin/env python3
"""r78-baseline PHASE 2 env materialization: the tracked-only battery input
subset at the LANDED r78 arm commit (the first commit after the frozen Phase-1
anchor 731937c whose diff touches corpus/fixtures/measure_audio.py), -> 
measure-env-post/corpus/ (plus empty live/runs/).

Usage:  python3 build_env_post.py <arm-sha>
Same recipe as build_env.py / r73-r77-baseline (tracked-only subset at the
pinned anchor; blobs via `git show`), so every Phase-2 receipt is attributable
to the arm bytes and cannot be confused with the frozen Phase-1 env.
"""
import re
import subprocess
import sys
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
ENV = HERE / "measure-env-post" / "corpus"
WANT = re.compile(r"^corpus/(artifacts|fixtures)/|^corpus/live/round-[^/]+/")


def git(*args, text=False):
    return subprocess.run(["git", *args], cwd=REPO,
                          capture_output=True, text=text)


def main():
    anchor = sys.argv[1] if len(sys.argv) > 1 else None
    if not anchor:
        sys.exit("usage: build_env_post.py <arm-sha>")
    names = [n for n in git("ls-tree", "-r", "-z", "--name-only", anchor,
                            text=True).stdout.split("\0")
             if n and WANT.match(n)]
    proofs, n_eq = [], 0
    for rel in names:
        blob = git("show", f"{anchor}:{rel}").stdout
        dest = ENV / Path(rel).relative_to("corpus")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(blob)
        got = sha256(dest.read_bytes()).hexdigest()
        ok = got == sha256(blob).hexdigest()
        n_eq += ok
        proofs.append(f"{'EQUAL' if ok else 'DIFF'} "
                      f"{Path(rel).relative_to('corpus')} {got}")
    (ENV / "live" / "runs").mkdir(parents=True, exist_ok=True)
    (HERE / "env-post-filelist.txt").write_text("\n".join(sorted(names)) + "\n")
    (HERE / "env-post-proofs.txt").write_text("\n".join(proofs) + "\n")
    env_files = sorted(str(p.relative_to(ENV)) for p in ENV.rglob("*")
                       if p.is_file() and "live/runs" not in str(p))
    want = sorted(str(Path(n).relative_to("corpus")) for n in names)
    extra = [f for f in env_files if f not in want]
    missing = [f for f in want if f not in env_files]
    (HERE / "env-post-comm.txt").write_text(
        f"pin={anchor}\n"
        "== untracked-input check (env files not in the pinned commit):\n"
        + "\n".join(extra) + f"\ncount={len(extra)}\n"
        + "== tracked inputs missing from env:\n"
        + "\n".join(missing) + f"\ncount={len(missing)}\n")
    print(f"materialized {len(names)} files at {anchor}, {n_eq} byte-equal; "
          f"extra={len(extra)} missing={len(missing)}")


if __name__ == "__main__":
    main()
