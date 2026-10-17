#!/usr/bin/env python3
"""r77-baseline env materialization: the tracked-only battery input subset at
frozen HEAD b0b5d4d ("r76 report-last: 9 seat reports + adjudicator +
LOG/SCORECARD"). corpus/artifacts + corpus/fixtures (incl tracked __pycache__)
+ every tracked corpus/live/round-* fixture -> measure-env/corpus/ (plus empty
live/runs/). Commit-pinned enumeration via `git ls-tree -r <sha>` (ls-tree
pathspecs do NOT glob 'round-*', so we filter by regex) + `git show <sha>:<path>`
blobs. Writes env-filelist.txt + env-proofs.txt (per-file EQUAL/DIFF vs frozen
blob) + env-comm.txt (untracked-env / missing-tracked direction checks).
Same recipe as r73/r75/r76-baseline (tracked-only subset at the frozen anchor).
"""
import re
import subprocess
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
ENV = HERE / "measure-env" / "corpus"
FROZEN = "b0b5d4d5c8bfd3356fb6c761cae7f40d0978d588"
WANT = re.compile(r"^corpus/(artifacts|fixtures)/|^corpus/live/round-[^/]+/")


def git(*args, text=False):
    return subprocess.run(["git", *args], cwd=REPO,
                          capture_output=True, text=text)


def main():
    all_names = git("ls-tree", "-r", "--name-only", FROZEN,
                    text=True).stdout.split()
    names = [n for n in all_names if WANT.match(n)]
    proofs = []
    n_eq = 0
    for rel in names:
        blob = git("show", f"{FROZEN}:{rel}").stdout
        dest = ENV / Path(rel).relative_to("corpus")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(blob)
        got = sha256(dest.read_bytes()).hexdigest()
        ok = got == sha256(blob).hexdigest()
        n_eq += ok
        proofs.append(f"{'EQUAL' if ok else 'DIFF'} "
                      f"{Path(rel).relative_to('corpus')} {got}")
    (ENV / "live" / "runs").mkdir(parents=True, exist_ok=True)
    (HERE / "env-filelist.txt").write_text("\n".join(sorted(names)) + "\n")
    (HERE / "env-proofs.txt").write_text("\n".join(proofs) + "\n")
    # direction checks: every file under env must be in `names`; every name
    # must exist under env.
    env_files = sorted(str(p.relative_to(ENV)) for p in ENV.rglob("*")
                       if p.is_file() and "live/runs" not in str(p))
    want = sorted(str(Path(n).relative_to("corpus")) for n in names)
    extra = [f for f in env_files if f not in want]
    missing = [f for f in want if f not in env_files]
    (HERE / "env-comm.txt").write_text(
        "== untracked-input check (env files not in frozen commit):\n"
        + "\n".join(extra) + f"\ncount={len(extra)}\n"
        + "== tracked inputs missing from env:\n"
        + "\n".join(missing) + f"\ncount={len(missing)}\n")
    print(f"materialized {len(names)} files, {n_eq} byte-equal to frozen "
          f"blobs; extra={len(extra)} missing={len(missing)}")


if __name__ == "__main__":
    main()
