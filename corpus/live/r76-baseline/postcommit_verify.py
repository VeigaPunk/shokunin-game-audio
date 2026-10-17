#!/usr/bin/env python3
"""r76-baseline post-commit re-verification.
Run AFTER the operator commits the r76 author diff (HEAD moves off 2250be9).
Checks, vs frozen anchor 2250be9:
 1. committed ledger corpus/live/r70-author/ledger-r71.tsv blob sha unchanged
    at the new HEAD;
 2. full `git ls-tree -r` object-id diff of corpus/live/runs between the two
    commits (0 lines = every committed receipt byte-identical);
 3. the changed-path list (git diff --stat names);
 4. measure_audio.py: insertion-only guard — every deleted line in the diff
    must be one of the three dispatch-wiring chains (exclusivity sum, mode=
    chain, suffix= chain) extended with the new probe flag.
Writes postcommit-verify.txt.
"""
import re
import subprocess
import sys
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
OLD = "2250be9552afb3b06a4e13aeaabd802787fcc6de"
NEW = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO,
                     capture_output=True, text=True).stdout.strip()


def git(*a, text=True):
    return subprocess.run(["git", *a], cwd=REPO, capture_output=True,
                          text=text).stdout


def main():
    out = []
    out.append(f"old={OLD}\nnew={NEW}")
    out.append(f"new_subject={git('log','-1','--format=%s',NEW).strip()}")
    # 1. ledger sha at both commits
    for tag, ref in (("2250be9", OLD), ("HEAD", NEW)):
        blob = git("rev-parse", f"{ref}:corpus/live/r70-author/ledger-r71.tsv").strip()
        body = git("show", f"{ref}:corpus/live/r70-author/ledger-r71.tsv")
        out.append(f"ledger-r71.tsv @{tag}: blob={blob} sha256={sha256(body.encode()).hexdigest()}")
    # 2. runs object-identity diff
    lt_old = git("ls-tree", "-r", OLD, "corpus/live/runs").splitlines()
    lt_new = git("ls-tree", "-r", NEW, "corpus/live/runs").splitlines()
    diff = [l for l in lt_old if l not in set(lt_new)] + \
           [l for l in lt_new if l not in set(lt_old)]
    out.append(f"runs ls-tree rows old={len(lt_old)} new={len(lt_new)} "
               f"object-id diff lines={len(diff)}")
    out += diff[:40]
    # 3. changed paths
    names = git("diff", "--name-only", OLD, NEW).splitlines()
    out.append(f"changed paths ({len(names)}):")
    out += ["  " + n for n in names]
    # 4. insertion-only check on measure_audio.py if it changed
    if "corpus/fixtures/measure_audio.py" in names:
        d = git("diff", OLD, NEW, "--", "corpus/fixtures/measure_audio.py")
        dels = [l[1:] for l in d.splitlines()
                if l.startswith("-") and not l.startswith("---")]
        out.append(f"measure_audio.py deleted lines: {len(dels)}")
        for l in dels:
            cls = ("WIRING-CHAIN" if ("sum([" in l or "mode =" in l
                                    or "suffix =" in l) else "OTHER-DELETION")
            out.append(f"  {cls}: {l[:140]}")
    else:
        out.append("measure_audio.py unchanged")
    Path(HERE / "postcommit-verify.txt").write_text("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
