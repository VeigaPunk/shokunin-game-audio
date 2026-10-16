#!/usr/bin/env python3
"""r87-verifier family-lock probe (verifier-owned; helper extracted
verbatim by anchor from the frozen-tree fixture, never imported).

Checks the r84 F1 fold as the r87 landing declares it:
  1. the r87 lock path is fixed (ROOT/live/...) and NOT TMPDIR-scoped —
     executed under a foreign TMPDIR;
  2. exclusion is real (a second exclusive attempt blocks while held);
  3. the r86-F1 corollary: the fixed path is ROOT-relative, so two tree
     materializations hold two different lock files *simultaneously* —
     cross-tree runs are not serialized (the wave observed exactly this);
  4. control: the r85 helper (tempfile.gettempdir()) lands under the
     foreign TMPDIR — the TMPDIR-scoping contrast is proven, not assumed.
"""
import fcntl
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

FIXTURE = sys.argv[1] if len(sys.argv) > 1 else \
    "corpus/live/r87-verifier/tree/corpus/fixtures/measure_audio.py"


def extract(src, name):
    m = re.search(rf"^def {name}\(\):.*?(?=^def |^class )", src,
                  re.S | re.M)
    if not m:
        raise SystemExit(f"anchor not found: {name}")
    return m.group(0)


def namespace(root, pid, ns, role):
    return {"ROOT": Path(root), "os": os, "fcntl": fcntl,
            "PWBIND_R87_PID": pid, "PWBIND_R87_NS": ns,
            "PWBIND_R87_ROLE": role, "tempfile": tempfile,
            "Path": Path, "re": re}


def main():
    src = open(FIXTURE).read()
    r87 = extract(src, "_pwbind_r87_family_lock")
    r85 = extract(src, "_pactlmon_r85_family_lock")
    out = {"fixture": FIXTURE,
           "r87_helper_mentions_tmpdir": bool(
               re.search(r"tempfile|TMPDIR|gettempdir", r87)),
           "r87_path_expr": re.search(r"path = .*", r87).group(0).strip(),
           "tests": []}
    tmp = Path(os.environ.get("TMPDIR", "/tmp"))
    foreign = Path(tempfile.mkdtemp(prefix="r87v-foreign-tmp-", dir=tmp))
    os.environ["TMPDIR"] = str(foreign)      # the foreign scratch TMPDIR

    frozen = Path(FIXTURE).resolve().parents[1]     # <tree>/corpus
    # 1. r87 helper under foreign TMPDIR, ROOT = frozen tree
    ns1 = namespace(frozen, 424242, "r87v_ns_424242", "r87vrole424242")
    exec(compile(r87, "<r87helper>", "exec"), ns1)
    fd = ns1["_pwbind_r87_family_lock"]()
    lock = frozen / "live" / "measure_audio-pwbind-r87.lock"
    out["tests"].append({
        "t": "r87 lock under foreign TMPDIR",
        "lock_path": str(lock),
        "exists_at_frozen": lock.exists(),
        "exists_under_foreign_tmpdir": (foreign /
                                        "measure_audio-pwbind-r87.lock").exists(),
        "witness": lock.read_text() if lock.exists() else None,
        "returned_fd": fd is not None})

    # 2. exclusion: second exclusive attempt blocks while held
    def try_nb(path):
        f = os.open(str(path), os.O_RDWR | os.O_CREAT, 0o644)
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return f, None
        except BlockingIOError as e:
            os.close(f)
            return None, type(e).__name__

    f2, err = try_nb(lock)
    blocked = err == "BlockingIOError"
    os.close(fd)                                  # release
    f3, err2 = try_nb(lock)
    out["tests"].append({"t": "exclusion while held",
                         "second_attempt": err,
                         "blocked": blocked,
                         "after_release": "acquired" if f3 is not None
                         else err2})
    if f3 is not None:
        os.close(f3)

    # 3. cross-materialization: two ROOTs -> two lock files, both held
    tree_a = Path(tempfile.mkdtemp(prefix="r87v-treeA-", dir=tmp))
    tree_b = Path(tempfile.mkdtemp(prefix="r87v-treeB-", dir=tmp))
    for t in (tree_a, tree_b):
        (t / "corpus" / "live").mkdir(parents=True)
    nsa = namespace(tree_a / "corpus", 1, "r87v_ns_1", "r87vrole1")
    nsb = namespace(tree_b / "corpus", 2, "r87v_ns_2", "r87vrole2")
    exec(compile(r87, "<r87helper>", "exec"), nsa)
    exec(compile(r87, "<r87helper>", "exec"), nsb)
    fa = nsa["_pwbind_r87_family_lock"]()
    fb = nsb["_pwbind_r87_family_lock"]()      # must NOT block: distinct path
    out["tests"].append({
        "t": "cross-materialization non-serialization",
        "lockA": str(tree_a / "corpus/live/measure_audio-pwbind-r87.lock"),
        "lockB": str(tree_b / "corpus/live/measure_audio-pwbind-r87.lock"),
        "A_held": fa is not None, "B_held": fb is not None,
        "both_held_simultaneously": fa is not None and fb is not None,
        "witnessA": (tree_a / "corpus/live/measure_audio-pwbind-r87.lock"
                     ).read_text().strip(),
        "witnessB": (tree_b / "corpus/live/measure_audio-pwbind-r87.lock"
                     ).read_text().strip()})
    for f in (fa, fb):
        if f is not None:
            os.close(f)

    # 4. control: r85 helper is TMPDIR-scoped
    n85 = namespace(frozen, 3, "r85v_ns_3", "r85vrole3")
    n85["PACTLMON_R85_PID"] = 3
    n85["PACTLMON_R85_TAP"] = "r85v_tap_3"
    n85["PACTLMON_R85_NS"] = "r85v_ns_3"
    n85["PACTLMON_R85_ROLE"] = "r85vrole3"
    exec(compile(r85, "<r85helper>", "exec"), n85)
    f5 = n85["_pactlmon_r85_family_lock"]()
    out["tests"].append({
        "t": "r85 control (TMPDIR-scoped)",
        "under_foreign_tmpdir": (foreign /
                                 "measure_audio-pactlmon-r85.lock").exists(),
        "under_frozen_live": (frozen / "live" /
                              "measure_audio-pactlmon-r85.lock").exists()})
    if f5 is not None:
        os.close(f5)

    for d in (foreign, tree_a, tree_b):
        shutil.rmtree(d, ignore_errors=True)
    print(json.dumps(out, indent=1))
    ok = (out["tests"][0]["exists_at_frozen"]
          and not out["tests"][0]["exists_under_foreign_tmpdir"]
          and out["tests"][1]["blocked"]
          and out["tests"][2]["both_held_simultaneously"]
          and out["tests"][3]["under_foreign_tmpdir"]
          and not out["tests"][3]["under_frozen_live"])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
