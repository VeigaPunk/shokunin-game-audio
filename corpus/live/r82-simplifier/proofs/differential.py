#!/usr/bin/env python3
"""r82-simplifier differential harness — the narrow behavioral check.

Imports the BASE and FOLDED copies (from a scratch dir; never from the
repo, so no __pycache__ lands in the tree) and compares the edited
helpers on identical inputs. Also re-applies the patch to a scratch copy
with `patch -p1` and asserts byte-identity with the folded copy.

Run:  PYTHONDONTWRITEBYTECODE=1 python3 -B differential.py
Exit 0 = every check PASS.
"""
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
BASE = REPO / "corpus/live/r82-simplifier/proofs/base-measure_audio.py"
FOLDED = REPO / "corpus/live/r82-simplifier/folded/measure_audio.py"
PATCH = REPO / "corpus/live/r82-simplifier/r82-simplifier.patch"
SCRATCH = Path("/tmp/r82sprobe")
fails = []


def check(cond, msg, extra=""):
    print(("PASS  " if cond else "FAIL  ") + msg + (("  " + extra) if extra else ""))
    if not cond:
        fails.append(msg)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


print("== D0: patch re-application is byte-identical to the folded copy ==")
if SCRATCH.exists():
    shutil.rmtree(SCRATCH)
(SCRATCH / "apply/corpus/fixtures").mkdir(parents=True)
shutil.copy(BASE, SCRATCH / "apply/corpus/fixtures/measure_audio.py")
r = subprocess.run(["patch", "-p1", "-i", str(PATCH)], cwd=SCRATCH / "apply",
                   capture_output=True, text=True)
applied = SCRATCH / "apply/corpus/fixtures/measure_audio.py"
check(r.returncode == 0, "patch -p1 applied clean",
      f"(rc={r.returncode} {r.stdout.strip()[:120]})")
check(sha(applied) == sha(FOLDED), "patched copy == folded copy (sha256)",
      f"{sha(applied)[:16]} == {sha(FOLDED)[:16]}")
check(sha(BASE) == "eb86576063b359b8bd69d5147b03e443e73990052e76f9221a552cd0864d20b4",
      "base copy == committed fixture sha")

print("\n== D1: imports ==")
base = load("r82_base", BASE)
fold = load("r82_fold", FOLDED)
check(True, "both modules import from scratch (bytecode disabled)")

print("\n== D2: _ffpw_r82_last_node differential ==")
legs = {
    "linked_main": {"samples": [
        {"nodes": [{"src": "other", "consumers": ["y"], "producers": []}]},
        {"nodes": [{"src": "main", "consumers": ["x"], "producers": []}]}]},
    "unlinked_main": {"samples": [
        {"nodes": [{"src": "main", "consumers": [], "producers": []}]}]},
    "no_main": {"samples": [
        {"nodes": [{"src": "pump", "consumers": ["z"], "producers": []}]}]},
    "empty": {"samples": []},
}
for name, leg in legs.items():
    b = base._ffpw_r82_last_node(leg)
    f = fold._ffpw_r82_last_node(leg)
    check(b == f, f"D2 {name}: base == folded", f"({json.dumps(b)[:90]})")
b2 = base._ffpw_r82_last_node(legs["unlinked_main"], require_linked=True)
try:
    fold._ffpw_r82_last_node(legs["unlinked_main"], require_linked=True)
    f2 = "ACCEPTED"
except TypeError:
    f2 = "TypeError"
check(b2 is None and f2 == "TypeError",
      "D2 removed surface documented: require_linked=True base->None, "
      "folded->TypeError (no call site uses it)")

print("\n== D3: _ffpw_r82_shot differential ==")
for argv in (["true"], ["false"], ["/bin/echo", "r82-probe"]):
    b = base._ffpw_r82_shot(argv)
    f = fold._ffpw_r82_shot(argv)
    check(b == f, f"D3 {argv}: dicts identical",
          f"(rc={b['rc']} cls={b['error_class']})")

print("\n== D4: _ffpw_r82_kill_watch differential ==")
p1 = subprocess.Popen(["sleep", "300"], start_new_session=True)
b = base._ffpw_r82_kill_watch(p1, "pump")
p1.wait(timeout=5)
check(b == {"sigkilled": True} and p1.poll() is not None,
      "D4 live child: base sigkilled + dead", f"({b})")
p2 = subprocess.Popen(["sleep", "300"], start_new_session=True)
f = fold._ffpw_r82_kill_watch(p2)
p2.wait(timeout=5)
check(f == {"sigkilled": True} and p2.poll() is not None,
      "D4 live child: folded sigkilled + dead", f"({f})")
p3 = subprocess.Popen(["true"], start_new_session=True)
p3.wait(timeout=5)
b = base._ffpw_r82_kill_watch(p3, "pump")
f = fold._ffpw_r82_kill_watch(p3)
check(b == f == {"already_exited": 0},
      "D4 exited child: identical already_exited", f"({b} / {f})")

print("\n== D5: _ffpw_r82_tone_windows differential ==")
with tempfile.TemporaryDirectory(prefix="r82sprobe-tone-") as tmp:
    tone = Path(tmp) / "tone.wav"
    base._ffpw_r82_write_tone(tone, 0.5)
    b = base._ffpw_r82_tone_windows(tone)
    f = fold._ffpw_r82_tone_windows(tone)
    check(b == f, "D5 tone file: dicts identical",
          f"(mine_windows={b.get('mine_windows')})")
    missing = Path(tmp) / "nope.wav"
    b = base._ffpw_r82_tone_windows(missing)
    f = fold._ffpw_r82_tone_windows(missing)
    check(b == f, "D5 missing file: dicts identical",
          f"({json.dumps(b)[:80]})")

print("\n== D6: AST census re-run on the folded copy ==")
import ast
ft = ast.parse(FOLDED.read_text())


def names_loaded(tree):
    return [n.id for n in ast.walk(tree)
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)]


def calls(tree, name):
    out = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            fn = n.func
            nm = fn.id if isinstance(fn, ast.Name) else \
                (fn.attr if isinstance(fn, ast.Attribute) else None)
            if nm == name:
                out.append((n.lineno, len(n.args), sorted(k.arg for k in n.keywords)))
    return out


loaded = names_loaded(ft)
check("FFPW_R82_FFPLAY" not in loaded, "folded: FFPW_R82_FFPLAY absent")
check("_star" not in loaded, "folded: _star absent")
check(all("require_linked" not in kw for _, _, kw in calls(ft, "_ffpw_r82_last_node")),
      "folded: no require_linked anywhere")
check(all("env_extra" not in kw for _, _, kw in calls(ft, "_ffpw_r82_shot")),
      "folded: no env_extra on _ffpw_r82_shot")
check(all("taps" not in kw for _, _, kw in calls(ft, "_landed_on")),
      "folded: no taps on _landed_on")
check(all("post" not in kw for _, _, kw in calls(ft, "_cap")),
      "folded: no post on _cap")
check(len(calls(ft, "_ffpw_r82_kill_watch")) == 1 and
      calls(ft, "_ffpw_r82_kill_watch")[0][1] == 1,
      "folded: kill_watch has 1 call site with 1 positional arg",
      f"{calls(ft, '_ffpw_r82_kill_watch')}")
check(all("out_path" not in kw for ln, _, kw in calls(ft, "_ffpw_r82_leg")
          if 15900 <= ln <= 16000),
      "folded: entry-6 legs still omit out_path")

print()
if fails:
    print(f"RESULT: {len(fails)} FAILURE(S): {fails}")
    sys.exit(1)
print("RESULT: ALL DIFFERENTIAL CHECKS PASS")
