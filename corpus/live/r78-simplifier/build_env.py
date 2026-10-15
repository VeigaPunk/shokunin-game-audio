#!/usr/bin/env python3
"""r78 SIMPLIFIER env materialization (control + candidate).

Tracked-only battery input subset at the r78 arm HEAD d9aa6f9, materialized
into /tmp/r78-simpl/{control,cand}/corpus via `git show <sha>:<path>` blobs.
The candidate env then receives the deletion batch. Both envs are proven
byte-equal to the pinned blobs except for the candidate fixture.

usage: build_env.py
"""
import re
import subprocess
import sys
from hashlib import sha256
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
OUT = Path("/tmp/r78-simpl")
ANCHOR = "d9aa6f9"
WANT = re.compile(r"^corpus/(artifacts|fixtures)/|^corpus/live/round-[^/]+/")


def git(*args):
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True)


def build(env):
    names = [n for n in git("ls-tree", "-r", "-z", "--name-only", ANCHOR)
             .stdout.decode().split("\0") if n and WANT.match(n)]
    proofs, n_eq = [], 0
    for rel in names:
        blob = git("show", f"{ANCHOR}:{rel}").stdout
        dest = env / "corpus" / Path(rel).relative_to("corpus")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(blob)
        got = sha256(dest.read_bytes()).hexdigest()
        ok = got == sha256(blob).hexdigest()
        n_eq += ok
        proofs.append(f"{'EQUAL' if ok else 'DIFF'} "
                      f"{Path(rel).relative_to('corpus')} {got}")
    (env / "corpus" / "live" / "runs").mkdir(parents=True, exist_ok=True)
    (OUT / f"env-proofs-{env.name}.txt").write_text("\n".join(proofs) + "\n")
    env_files = sorted(str(p.relative_to(env / "corpus"))
                       for p in (env / "corpus").rglob("*")
                       if p.is_file() and "live/runs" not in str(p))
    want = sorted(str(Path(n).relative_to("corpus")) for n in names)
    extra = [f for f in env_files if f not in want]
    missing = [f for f in want if f not in env_files]
    print(f"{env.name}: {len(names)} files at {ANCHOR}, {n_eq} byte-equal; "
          f"extra={len(extra)} missing={len(missing)}")
    return names


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name in ("control", "cand"):
        build(OUT / name)
    # the candidate fixture is the deletion batch's output
    src = OUT / "cand" / "corpus" / "fixtures" / "measure_audio.py"
    print("cand fixture sha256:", sha256(src.read_bytes()).hexdigest())


if __name__ == "__main__":
    sys.exit(main())
