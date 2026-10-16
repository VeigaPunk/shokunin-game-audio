#!/usr/bin/env python3
"""r88-verifier fixed-path lock probe (r84/r86/r87 fold re-check).

Extracts the committed lock helper verbatim from the frozen c19bec96 tree
and proves, executed:
  1. with TMPDIR pointed at a foreign dir, the lock lands at
     <ROOT>/live/measure_audio-btwit-r88.lock and NOT under TMPDIR
  2. a second exclusive attempt blocks while held, succeeds after release
  3. cross-materialization: two ROOTs -> two locks held simultaneously
  4. control: the r85 TMPDIR-scoped helper lands under the foreign TMPDIR
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import textwrap
import time
from pathlib import Path

TREE = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
OUT.mkdir(parents=True, exist_ok=True)
# ROOT is the corpus dir in the fixture (Path(__file__).parents[1])
ROOT = TREE / "corpus"

src = (ROOT / "fixtures" / "measure_audio.py").read_text()


def extract(name):
    m = re.search(r"^def " + name + r"\(.*?(?=^def |\Z)", src, re.S | re.M)
    assert m, name
    return m.group(0)


r88_fn = extract("_btwit_r88_family_lock")
r85_fn = extract("_pactlmon_r85_family_lock")

CHILD = textwrap.dedent('''
    import fcntl, json, os, sys, time
    from pathlib import Path
    ROOT = Path(sys.argv[1])
    MODE = sys.argv[2]
    OUTP = Path(sys.argv[3])
    PID = int(sys.argv[4])
    BTWIT_R88_PID = PID
    BTWIT_R88_NS = f"r88v_ns_{{PID}}"
    BTWIT_R88_ROLE = f"r88vrole{{PID}}"
    {fn}
    rec = {{"pid": PID}}
    rec["lock_path"] = str(ROOT / "live" / "measure_audio-btwit-r88.lock")
    if MODE == "hold":
        fd = {helper}()
        rec["fd"] = fd is not None
        rec["lock_exists"] = os.path.exists(rec["lock_path"])
        if rec["lock_exists"]:
            rec["lock_content"] = open(rec["lock_path"]).read().strip()
        (OUTP / (MODE + "-" + str(PID) + ".json")).write_text(
            json.dumps(rec) + "\\n")
        time.sleep(6)
    elif MODE == "try":
        rec["lock_exists_before"] = os.path.exists(rec["lock_path"])
        try:
            fd2 = os.open(rec["lock_path"], os.O_RDWR | os.O_CREAT, 0o644)
            try:
                fcntl.flock(fd2, fcntl.LOCK_EX | fcntl.LOCK_NB)
                rec["blocked"] = False
                fcntl.flock(fd2, fcntl.LOCK_UN)
            except BlockingIOError:
                rec["blocked"] = True
            os.close(fd2)
        except OSError as e:
            rec["err"] = str(e)
        fd = {helper}()
        rec["got_lock"] = fd is not None
        rec["lock_content"] = open(rec["lock_path"]).read().strip() \\
            if os.path.exists(rec["lock_path"]) else None
    (OUTP / (MODE + "-" + str(PID) + ".json")).write_text(
        json.dumps(rec) + "\\n")
''')

results = {}
foreign_tmp = tempfile.mkdtemp(prefix="r88v-foreign-tmp-")
env = dict(os.environ, TMPDIR=foreign_tmp)
lock_path = ROOT / "live" / "measure_audio-btwit-r88.lock"

# 1+2: hold in one child (ROOT = frozen tree corpus), try in another
hold = subprocess.Popen(
    [sys.executable, "-c",
     CHILD.format(fn=r88_fn, helper="_btwit_r88_family_lock"),
     str(ROOT), "hold", str(OUT), "424242"], env=env)
time.sleep(1.5)
subprocess.run(
    [sys.executable, "-c",
     CHILD.format(fn=r88_fn, helper="_btwit_r88_family_lock"),
     str(ROOT), "try", str(OUT), "424243"], env=env, timeout=30,
    capture_output=True)
results["hold"] = json.loads((OUT / "hold-424242.json").read_text())
results["try_while_held"] = json.loads((OUT / "try-424243.json").read_text())
hold.wait(timeout=30)
results["lock_in_tree"] = lock_path.exists()
results["lock_under_tmpdir"] = any(
    "measure_audio-btwit-r88.lock" in str(p) for p in
    Path(foreign_tmp).rglob("*"))

# after release, the same attempt succeeds (no blocking)
subprocess.run(
    [sys.executable, "-c",
     CHILD.format(fn=r88_fn, helper="_btwit_r88_family_lock"),
     str(ROOT), "try", str(OUT), "424244"], env=env, timeout=30,
    capture_output=True)
results["try_after_release"] = json.loads((OUT / "try-424244.json").read_text())

# 3: cross-materialization — two scratch ROOTs, both locks held at once
scratch = []
for i in (1, 2):
    root = OUT / f"scratch-root-{i}" / "corpus"
    (root / "live").mkdir(parents=True, exist_ok=True)
    scratch.append(root)
procs = []
for i, root in enumerate(scratch, 1):
    procs.append(subprocess.Popen(
        [sys.executable, "-c",
         CHILD.format(fn=r88_fn, helper="_btwit_r88_family_lock"),
         str(root), "hold", str(OUT), f"42425{i}"], env=env))
time.sleep(1.5)
cross = []
for i, root in enumerate(scratch, 1):
    p = root / "live" / "measure_audio-btwit-r88.lock"
    cross.append({"root": str(root), "exists": p.exists(),
                  "content": p.read_text().strip() if p.exists() else None})
for pr in procs:
    pr.wait(timeout=30)
results["cross_materialization"] = cross

# 4: control — the r85 helper is TMPDIR-scoped
ctl = subprocess.run(
    [sys.executable, "-c", textwrap.dedent(f'''
        import tempfile, os
        from pathlib import Path
        ROOT = Path({str(ROOT)!r})
        PACTLMON_R85_PID = 424245
        PACTLMON_R85_NS = "r88v_ns_424245"
        PACTLMON_R85_ROLE = "r88vrole424245"
        {r85_fn}
        fd = _pactlmon_r85_family_lock()
        lock = Path(tempfile.gettempdir()) / "measure_audio-pactlmon-r85.lock"
        print("fd_none=" + str(fd is None))
        print("under_tmpdir=" + str(lock.exists()))
        print("lock_path=" + str(lock))
        print("under_tree=" + str(
            (ROOT / "live" / "measure_audio-pactlmon-r85.lock").exists()))
    ''')], env=env, timeout=30, capture_output=True)
results["r85_control"] = {
    "stdout": ctl.stdout.decode(),
    "stderr": ctl.stderr.decode()[-300:]}

(OUT / "lockprobe.json").write_text(json.dumps(results, indent=1) + "\n")
print(json.dumps(results, indent=1))
