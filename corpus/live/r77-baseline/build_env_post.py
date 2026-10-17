#!/usr/bin/env python3
"""r77-baseline POST-COMMIT env materialization: the same tracked-only subset
recipe as build_env.py, but pinned to the r77 author work commit 65790f13
("r77 work: capture-source lattice + fallback law + reader matrix") instead of
the frozen pre-move HEAD b0b5d4d. Materializes into measure-env-post/corpus/
so the post-commit replay runs against the committed post-move bytes while the
Phase-1 env stays byte-frozen.

Same recipe as build_env.py (commit-pinned `git ls-tree -r` + `git show`
blobs, per-file EQUAL/DIFF proofs, both-direction comm checks).
Writes env-post-filelist.txt + env-post-proofs.txt + env-post-comm.txt.
"""
import re
import subprocess
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
ENV = HERE / "measure-env-post" / "corpus"
PIN = "65790f13e75a69afb2ef2b3ccdb1fd488d778eff"
WANT = re.compile(r"^corpus/(artifacts|fixtures)/|^corpus/live/round-[^/]+/")


def git(*args, text=False):
    return subprocess.run(["git", *args], cwd=REPO,
                          capture_output=True, text=text)


def main():
    all_names = git("ls-tree", "-r", "--name-only", PIN, text=True).stdout.split()
    names = [n for n in all_names if WANT.match(n)]
    proofs = []
    n_eq = 0
    for rel in names:
        blob = git("show", f"{PIN}:{rel}").stdout
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
        f"pin={PIN}\n== untracked-input check (env files not in pinned commit):\n"
        + "\n".join(extra) + f"\ncount={len(extra)}\n"
        + "== tracked inputs missing from env:\n"
        + "\n".join(missing) + f"\ncount={len(missing)}\n")
    print(f"materialized {len(names)} files, {n_eq} byte-equal to {PIN[:7]} "
          f"blobs; extra={len(extra)} missing={len(missing)}")


if __name__ == "__main__":
    main()
