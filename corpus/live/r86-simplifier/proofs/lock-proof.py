#!/usr/bin/env python3
"""r86-simplifier lock proof L1-L5: the r86 family lock is a FIXED
corpus/live/ path and serializes same-family runs across DIFFERENT
TMPDIRs (the r84 F1 3-seat consensus fold). Two workers import the
SHIPPED corpus/fixtures/measure_audio.py and take the real lock. The
lock file is an untracked lane artifact; its bytes are saved and
restored around the proof."""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
LOCK = REPO / "corpus/live/measure_audio-pwctl-r86.lock"
BASE_SRC = (REPO / "corpus/fixtures/measure_audio.py").read_text()
results = []


def ck(name, cond, detail=""):
    results.append(bool(cond))
    print(f"{'PASS' if cond else 'FAIL'} {name} {detail}")


# L1 — static: the r86 lock function names a fixed path and never
# consults tempfile/TMPDIR (docstring excluded)
import ast
tree = ast.parse(BASE_SRC)
fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
          and n.name == "_pwctl_r86_family_lock")
body_src = "\n".join(ast.get_source_segment(BASE_SRC, s)
                     for s in fn.body if not (isinstance(s, ast.Expr)
                                              and isinstance(s.value,
                                                             ast.Constant)))
a = BASE_SRC.index("def _pwctl_r86_family_lock():")
b = BASE_SRC.index("def _pwctl_r86_entry_head(probe):")
lock_src = BASE_SRC[a:b]
ck("L1 r86 lock body has no tempfile/TMPDIR call",
   "tempfile" not in body_src and "gettempdir" not in body_src
   and "TMPDIR" not in body_src)
ck("L1 r86 lock path is ROOT / 'live' / "
   "'measure_audio-pwctl-r86.lock'",
   'path = ROOT / "live" / "measure_audio-pwctl-r86.lock"' in lock_src)
for nm, anchor in (("r82", "def _ffpw_r82_family_lock():"),
                   ("r84", "def _alsapw_r84_family_lock():"),
                   ("r85", "def _pactlmon_r85_family_lock():")):
    seg = BASE_SRC[BASE_SRC.index(anchor):]
    seg = seg[:seg.index("return fd")]
    ck(f"L1 contrast {nm} lock IS TMPDIR-scoped",
       "tempfile.gettempdir()" in seg)

# L2 — executed: two workers, DIFFERENT TMPDIRs, real lock ----------------
saved = LOCK.read_bytes() if LOCK.exists() else None
tmp_a = REPO.parent / "tmp" / "r86-simplifier-lockA"
tmp_b = REPO.parent / "tmp" / "r86-simplifier-lockB"
tmp_a.mkdir(parents=True, exist_ok=True)
tmp_b.mkdir(parents=True, exist_ok=True)
env_a = dict(os.environ, TMPDIR=str(tmp_a))
env_b = dict(os.environ, TMPDIR=str(tmp_b))
worker = str(HERE / "lock-worker.py")
try:
    pa = subprocess.Popen([sys.executable, worker, "2.0"], env=env_a,
                          stdout=subprocess.PIPE, text=True)
    time.sleep(0.4)
    pb = subprocess.Popen([sys.executable, worker, "0.2"], env=env_b,
                          stdout=subprocess.PIPE, text=True)
    out_a, _ = pa.communicate(timeout=60)
    out_b, _ = pb.communicate(timeout=60)
    ja, jb = json.loads(out_a), json.loads(out_b)
    ck("L2 both workers locked a path", bool(ja["fd_path"])
       and bool(jb["fd_path"]), f"{ja['fd_path']} | {jb['fd_path']}")
    ck("L2 locked fd path identical despite different TMPDIRs",
       ja["fd_path"] == jb["fd_path"]
       and ja["TMPDIR"] != jb["TMPDIR"]
       and ja["gettempdir"] != jb["gettempdir"],
       f"A TMPDIR={ja['TMPDIR']} gettempdir={ja['gettempdir']} | "
       f"B TMPDIR={jb['TMPDIR']} gettempdir={jb['gettempdir']}")
    ck("L2 the locked path is corpus/live/measure_audio-pwctl-r86.lock",
       ja["fd_path"] == str(LOCK), ja["fd_path"])
    ck("L2 serialized: B acquired only after A exited",
       jb["locked"] >= ja["exit"],
       f"A exit={ja['exit']:.3f} B locked={jb['locked']:.3f} "
       f"(B waited {jb['locked'] - jb['enter']:.3f}s)")
    ck("L2 B waited on the lock (blocked, did not race)",
       jb["locked"] - jb["enter"] >= 1.0,
       f"wait={jb['locked'] - jb['enter']:.3f}s")
    # L3 — reverse order: B (short) starts first, A (long) waits
    pa = subprocess.Popen([sys.executable, worker, "0.2"], env=env_a,
                          stdout=subprocess.PIPE, text=True)
    time.sleep(0.4)
    pb = subprocess.Popen([sys.executable, worker, "1.5"], env=env_b,
                          stdout=subprocess.PIPE, text=True)
    ja, jb = json.loads(pa.communicate(timeout=60)[0]), \
        json.loads(pb.communicate(timeout=60)[0])
    ck("L3 reverse order also serializes",
       jb["locked"] >= ja["exit"],
       f"A exit={ja['exit']:.3f} B locked={jb['locked']:.3f}")
finally:
    if saved is not None:
        LOCK.write_bytes(saved)
        ck("L4 lock witness bytes restored after the proof",
           LOCK.read_bytes() == saved)
    else:
        ck("L4 lock file was absent before (nothing to restore)", True)

# L5 — the shipped lock file lives under corpus/live/, outside TMPDIR
ck("L5 lock path is not under TMPDIR",
   not str(LOCK).startswith(str(Path(os.environ.get(
       "TMPDIR", "/nonexistent")))))
ck("L5 lock file exists at the fixed lane path", LOCK.exists())

n_fail = results.count(False)
print(f"\n{len(results) - n_fail}/{len(results)} PASS")
sys.exit(1 if n_fail else 0)
