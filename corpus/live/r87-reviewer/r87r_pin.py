#!/usr/bin/env python3
"""r87 reviewer — pin the committed landing and prove the diff shape.

Reads ONLY committed objects (git show d1e687b9 / d1e687b9^) plus the
worktree copy for a byte-identity check. Writes one JSON receipt.
No tracked writes.
"""
import difflib
import hashlib
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
COMMIT = "d1e687b9"
PARENT = "d1e687b9^"
OUT = REPO / "corpus/live/r87-reviewer/runs/pin.json"


def git(*args):
    return subprocess.run(["git", "-C", str(REPO), *args],
                          capture_output=True, text=True, check=True).stdout


def blob_lines(rev, path):
    return git("show", f"{rev}:{path}").splitlines()


def main():
    rec = {"commit": COMMIT, "parent": PARENT}
    rec["commit_meta"] = {
        "sha": git("rev-parse", COMMIT).strip(),
        "subject": git("log", "-1", "--format=%s", COMMIT).strip(),
        "numstat": git("diff", "--numstat", PARENT, COMMIT).strip(),
    }
    new = blob_lines(COMMIT, "corpus/fixtures/measure_audio.py")
    old = blob_lines(PARENT, "corpus/fixtures/measure_audio.py")
    new_bytes = git("show", f"{COMMIT}:corpus/fixtures/measure_audio.py").encode()
    rec["blob"] = {
        "lines": len(new),
        "sha256": hashlib.sha256(new_bytes).hexdigest(),
        "git_hash_object": git("hash-object", "-t", "blob", "--stdin",
                               "--path=corpus/fixtures/measure_audio.py")
        .strip() if False else subprocess.run(
            ["git", "-C", str(REPO), "hash-object", "-t", "blob", "--stdin"],
            input=new_bytes, capture_output=True).stdout.decode().strip(),
    }
    wt = (REPO / "corpus/fixtures/measure_audio.py").read_bytes()
    rec["worktree"] = {
        "sha256": hashlib.sha256(wt).hexdigest(),
        "byte_identical_to_commit": wt == new_bytes,
    }
    # py_compile the committed blob (pinned copy, never the worktree)
    pinned = REPO / "corpus/live/r87-reviewer/runs/measure_audio_d1e687b9.py"
    pinned.write_bytes(new_bytes)
    proc = subprocess.run([sys.executable, "-m", "py_compile", str(pinned)],
                          capture_output=True, text=True)
    rec["py_compile"] = {"rc": proc.returncode,
                         "stderr": proc.stderr[-400:]}
    # opcode-level diff shape
    sm = difflib.SequenceMatcher(None, old, new, autojunk=False)
    ops = []
    added = deleted = 0
    recon = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            recon.extend(old[i1:i2])
            if i2 - i1 > 200:
                ops.append({"op": "equal", "old": [i1 + 1, i2],
                            "new": [j1 + 1, j2], "lines": i2 - i1})
        elif tag == "insert":
            added += j2 - j1
            ops.append({"op": "insert", "new": [j1 + 1, j2],
                        "lines": j2 - j1})
        elif tag == "replace":
            added += j2 - j1
            deleted += i2 - i1
            entry = {"op": "replace", "old": [i1 + 1, i2],
                     "new": [j1 + 1, j2]}
            # string surgery: remove the r87 term, the result must be the
            # old line byte-for-byte
            terms = [", args.probe_pwbind_r87",
                     '"probe-pwbind-r87" if args.probe_pwbind_r87 else ',
                     '"-pwbind-r87" if args.probe_pwbind_r87 else ']
            ok = []
            for k in range(j1, j2):
                hit = None
                for term in terms:
                    if term in new[k]:
                        hit = term
                        recon.append(new[k].replace(term, "", 1))
                        break
                else:
                    recon.append(new[k])
                ok.append(hit)
            entry["terms_removed"] = ok
            entry["surgery_equals_old_line"] = (
                all(ok) and recon[-len(ok):] == old[i1:i2])
            ops.append(entry)
        else:
            raise SystemExit("unexpected delete opcode")
    rec["diff_shape"] = {
        "opcodes": ops,
        "added_lines": added,
        "deleted_lines": deleted,
        "insertion_only": deleted == 0,
        "reconstruction_equals_parent": recon == old,
        "reconstruction_method": ("drop every inserted block, remove the "
                                  "r87 term from each replaced line"),
    }
    OUT.write_text(json.dumps(rec, indent=1) + "\n")
    print(json.dumps({k: rec[k] for k in ("blob", "worktree", "py_compile",
                                          "diff_shape")}, indent=1)[:2000])
    print("receipt:", OUT)


if __name__ == "__main__":
    main()
