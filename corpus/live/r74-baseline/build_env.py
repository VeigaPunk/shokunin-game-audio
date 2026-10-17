#!/usr/bin/env python3
"""r74-baseline env materialization: the tracked-only battery input subset at
frozen HEAD 1ba8103 — corpus/artifacts + corpus/fixtures (incl tracked
__pycache__) + every tracked corpus/live/round-* fixture — materialized via
`git show HEAD:<path>` into measure-env/corpus/ (plus empty live/runs/).
Writes env-filelist.txt + env-proofs.txt (per-file EQUAL/DIFF vs HEAD blob)
+ env-comm.txt (untracked-env / missing-tracked direction checks).
Same recipe as r73-baseline (657 files expected).
"""
import subprocess
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
ENV = HERE / "measure-env" / "corpus"


def git(*args, text=False):
    return subprocess.run(["git", *args], cwd=REPO,
                          capture_output=True, text=text)


def main():
    names = git("ls-files", "corpus/artifacts", "corpus/fixtures",
                "corpus/live/round-*", text=True).stdout.split()
    proofs = []
    n_eq = 0
    for rel in names:
        blob = git("show", f"HEAD:{rel}").stdout
        dest = ENV / Path(rel).relative_to("corpus")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(blob)
        got = sha256(dest.read_bytes()).hexdigest()
        ok = got == sha256(blob).hexdigest()
        n_eq += ok
        proofs.append(f"{'EQUAL' if ok else 'DIFF'} "
                      f"{Path(rel).relative_to('corpus')} {got}")
    (HERE / "env-filelist.txt").write_text(
        "\n".join("corpus/" + str(Path(n).relative_to("corpus"))
                  for n in sorted(names)) + "\n")
    (HERE / "env-proofs.txt").write_text("\n".join(proofs) + "\n")
    # direction checks: every file under env must be in `names`; every name
    # must exist under env.
    env_files = sorted(str(p.relative_to(ENV)) for p in ENV.rglob("*")
                       if p.is_file() and "live/runs" not in str(p))
    want = sorted(str(Path(n).relative_to("corpus")) for n in names)
    extra = [f for f in env_files if f not in want]
    missing = [f for f in want if f not in env_files]
    (HERE / "env-comm.txt").write_text(
        "== untracked-input check (env files not in HEAD):\n"
        + "\n".join(extra) + f"\ncount={len(extra)}\n"
        + "== tracked inputs missing from env:\n"
        + "\n".join(missing) + f"\ncount={len(missing)}\n")
    print(f"materialized {len(names)} files, {n_eq} byte-equal to HEAD blobs; "
          f"extra={len(extra)} missing={len(missing)}")


if __name__ == "__main__":
    main()
