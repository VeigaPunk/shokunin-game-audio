#!/usr/bin/env python3
"""r77-baseline post-commit re-verification.
Run AFTER the operator commits the r77 author diff (HEAD moves off b0b5d4d).
Checks, vs frozen anchor b0b5d4d:
 1. committed ledger corpus/live/r70-author/ledger-r71.tsv blob sha unchanged
    at the new HEAD;
 2. full `git ls-tree -r` object-id diff of corpus/live/runs between the two
    commits (0 lines = every committed receipt byte-identical);
 3. the changed-path list (git diff --name-only);
 4. measure_audio.py: insertion-only guard — every deleted line in the diff
    must be one of the dispatch-wiring chains (exclusivity sum, mode= chain,
    suffix= chain) extended with the new probe flag, or an explicitly
    enumerated fold replacement (printed verbatim for review).
Writes postcommit-verify.txt.
"""
import re
import subprocess
import sys
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
OLD = "b0b5d4d5c8bfd3356fb6c761cae7f40d0978d588"
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
    for tag, ref in (("b0b5d4d", OLD), ("HEAD", NEW)):
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
    stat = git("diff", "--shortstat", OLD, NEW).strip()
    out.append(f"changed paths ({len(names)}): shortstat: {stat}")
    out += ["  " + n for n in names]
    # 4. insertion-only check on measure_audio.py if it changed
    if "corpus/fixtures/measure_audio.py" in names:
        d = git("diff", OLD, NEW, "--", "corpus/fixtures/measure_audio.py")
        adds = [l for l in d.splitlines()
                if l.startswith("+") and not l.startswith("+++")]
        dels = [l[1:] for l in d.splitlines()
                if l.startswith("-") and not l.startswith("---")]
        out.append(f"measure_audio.py added lines: {len(adds)} "
                   f"deleted lines: {len(dels)}")
        for l in dels:
            cls = ("WIRING-CHAIN" if ("sum([" in l or "mode =" in l
                                    or "suffix =" in l) else "OTHER-DELETION")
            out.append(f"  {cls}: {l[:200]}")
        # new probe arms wired in
        for pat in (r'add_argument\("--probe-[\w-]+"', r'probe-\w+-r77'):
            hits = sorted(set(re.findall(pat, "\n".join(adds))))
            out.append(f"  added[{pat}]: {hits[:12]}")
    else:
        out.append("measure_audio.py unchanged")
    # 5. anchor fixture sha at both commits
    for tag, ref in (("b0b5d4d", OLD), ("HEAD", NEW)):
        out.append(f"measure_audio.py @{tag}: "
                   f"{git('rev-parse', f'{ref}:corpus/fixtures/measure_audio.py').strip()}")
    Path(HERE / "postcommit-verify.txt").write_text("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
