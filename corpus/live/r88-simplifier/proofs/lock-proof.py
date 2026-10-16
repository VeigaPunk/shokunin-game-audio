#!/usr/bin/env python3
"""r88 simplifier — family-lock proof (L1..L7).

L1 static: the r88 lock function is fixed-path (no tempfile/TMPDIR); the
r82/r84/r85 locks are the TMPDIR stragglers; r86/r87 share the fixed form.
L0: the committed lane path resolution (ROOT=corpus) is the on-disk lock.
L2/L3 executed in scratch trees: two workers with DIFFERENT TMPDIRs on
the SAME fixture copy resolve the SAME lock path and the second blocks.
L6/L7 either-way control: holder treeA vs contender treeB (a different
fixture copy) resolve DIFFERENT lock paths and RACE (tree-relative
residual, inherited).

Scratch trees only: the real lane lock/witness is never opened for write;
the repo tree is read-only for this script."""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TREE = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
BASE = os.path.join(HERE, "base-measure_audio.py")
WORKER = os.path.join(HERE, "lock-worker.py")
SCRATCH = os.path.join(os.environ.get(
    "TMPDIR", "/home/vgpnk/Projects/shokunin/tmp"), "r88simp-lock")
FAIL = []


def check(name, cond, detail=""):
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")
    if not cond:
        FAIL.append(name)


text = open(BASE, encoding="utf-8").read()
lines = text.splitlines()


def fn_src(name):
    m = re.search(rf"^def {name}\(.*?(?=^def |\Z)", text, re.M | re.S)
    return m.group(0)


def fn_code(name):
    """Function source with docstring and comment lines stripped."""
    src = fn_src(name)
    try:
        import ast
        fn = next(n for n in ast.parse(text).body
                  if getattr(n, "name", None) == name)
        if (fn.body and isinstance(fn.body[0], ast.Expr)
                and isinstance(fn.body[0].value, ast.Constant)):
            src = src.replace(ast.get_source_segment(text, fn.body[0]), "")
    except Exception:
        pass
    return "\n".join(ln for ln in src.splitlines()
                     if not ln.strip().startswith("#"))


# ---------------- L1: static fixed-path census ---------------------------
lock_src = fn_src("_btwit_r88_family_lock")
lock_code = fn_code("_btwit_r88_family_lock")
check("L1a r88 lock CODE (docstring/comments excluded) has no "
      "tempfile/gettempdir/TMPDIR",
      not re.search(r"tempfile|gettempdir|TMPDIR", lock_code))
check("L1b r88 lock path is ROOT/live/measure_audio-btwit-r88.lock",
      'path = ROOT / "live" / "measure_audio-btwit-r88.lock"' in lock_src)
root_line = [ln for ln in lines if ln.startswith("ROOT = ")][0]
check("L1c ROOT derives from the fixture's own location",
      root_line == "ROOT = Path(__file__).resolve().parents[1]", root_line)
for name, tag in (("_ffpw_r82_family_lock", "r82"),
                  ("_alsapw_r84_family_lock", "r84"),
                  ("_pactlmon_r85_family_lock", "r85")):
    check(f"L1d[{tag}] contrast lock CODE uses tempfile.gettempdir()",
          "tempfile.gettempdir()" in fn_code(name))
for name, tag in (("_pwctl_r86_family_lock", "r86"),
                  ("_pwbind_r87_family_lock", "r87")):
    check(f"L1e[{tag}] contrast lock CODE is fixed-path (no tempfile)",
          not re.search(r"tempfile|gettempdir|TMPDIR", fn_code(name)))

# ---------------- L0: committed lane path resolution ---------------------
lane = os.path.join(TREE, "corpus", "live", "measure_audio-btwit-r88.lock")
check("L0a committed resolution ROOT=corpus -> the on-disk lane lock",
      os.path.exists(lane), lane)
if os.path.exists(lane):
    content = open(lane, "rb").read()
    check("L0b lane lock holds a one-line pid/ns/role witness",
          re.fullmatch(rb"pid=\d+ ns=r88a_ns_\d+ role=r88arole\d+\n",
                       content) is not None, content[:80])
    st = os.stat(lane)
    print(f"      lane lock: size={st.st_size} mtime={st.st_mtime:.3f} "
          f"({time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(st.st_mtime))})")

# ---------------- L2/L3 + L6/L7: executed scratch-tree proof -------------
if os.path.exists(SCRATCH):
    shutil.rmtree(SCRATCH)


def make_tree(tag, with_live=True):
    d = os.path.join(SCRATCH, tag)
    os.makedirs(os.path.join(d, "corpus", "fixtures"))
    if with_live:
        os.makedirs(os.path.join(d, "corpus", "live"))
    dst = os.path.join(d, "corpus", "fixtures", "measure_audio.py")
    shutil.copyfile(BASE, dst)
    os.chmod(dst, 0o755)
    return dst


fx_a = make_tree("treeA")
fx_b = make_tree("treeB")
td_a = os.path.join(SCRATCH, "tmpA")
td_b = os.path.join(SCRATCH, "tmpB")
os.makedirs(td_a)
os.makedirs(td_b)

HOLD = 2.5


def start(fixture, tmpdir, mode):
    env = dict(os.environ, TMPDIR=tmpdir, PYTHONDONTWRITEBYTECODE="1")
    return subprocess.Popen([sys.executable, WORKER, fixture, str(HOLD),
                             mode], stdout=subprocess.PIPE, text=True,
                            env=env)


def first_line(proc):
    return json.loads(proc.stdout.readline())


# same tree, different TMPDIRs -> must exclude
a = start(fx_a, td_a, "A")
la = first_line(a)
time.sleep(0.2)
b = start(fx_a, td_b, "B")
lb = first_line(b)
b.wait(timeout=20)
a.wait(timeout=20)
check("L2a both TMPDIRs differ and both resolve the same lock path",
      la["tmpdir"] != lb["tmpdir"] and la["resolved"] == lb["resolved"]
      and la["resolved"].endswith("corpus/live/measure_audio-btwit-r88.lock"),
      f"{la['resolved']}")
check("L3a contender (different TMPDIR) blocked until holder exited",
      lb["wait_s"] >= 1.8, f"waited {lb['wait_s']}s (holder held {HOLD}s)")
check("L3b holder acquired immediately", la["wait_s"] < 0.5,
      f"{la['wait_s']}s")

# different trees (different fixture copies) -> different lock paths, race
c = start(fx_a, td_a, "C")
lc = first_line(c)
time.sleep(0.2)
d = start(fx_b, td_b, "D")
ld = first_line(d)
d.wait(timeout=20)
c.wait(timeout=20)
check("L6a cross-tree runs resolve DIFFERENT lock paths",
      lc["resolved"] != ld["resolved"],
      f"A={lc['resolved']} B={ld['resolved']}")
check("L7a cross-tree contender did NOT block (race, residual)",
      ld["wait_s"] < 1.0, f"waited {ld['wait_s']}s while holder held {HOLD}s")

# fail-open caveat (inherited): missing live/ dir -> os.open fails -> None
fx_n = make_tree("treeNoLive", with_live=False)
n = start(fx_n, td_a, "N")
ln_ = first_line(n)
n.wait(timeout=20)
check("L8a fail-open: missing corpus/live/ -> lock returns None (no "
      "exclusion), recorded as inherited caveat",
      ln_["fd"] is None and ln_["resolved"] is None and ln_["wait_s"] < 0.5,
      str(ln_))

print()
print(f"LOCK PROOFS: {'ALL PASS' if not FAIL else 'FAILURES: ' + str(FAIL)}")
sys.exit(1 if FAIL else 0)
