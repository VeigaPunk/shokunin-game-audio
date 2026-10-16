#!/usr/bin/env python3
"""r86-simplifier static proofs S1-S12 over the fa5994a0-pinned blob and
the folded copy. Exit non-zero on the first failed assertion."""
import ast
import hashlib
import sys
from pathlib import Path

BASE = Path("base-measure_audio.py")
FOLD = Path("folded/measure_audio.py")
base = BASE.read_text(encoding="utf-8")
fold = FOLD.read_text(encoding="utf-8")
bt, ft = ast.parse(base), ast.parse(fold)
BL, BH = 23730, 25451
checks = []


def ck(name, cond, detail=""):
    checks.append((name, bool(cond), detail))
    if not cond:
        print(f"FAIL {name} {detail}")
    else:
        print(f"PASS {name} {detail}")


def in_block(n):
    return BL <= n.lineno <= BH


# S1 — dead constants ------------------------------------------------------
for nm in ("PWCTL_R86_LINK_WAIT_S", "PWCTL_R86_TAP_WAIT_S"):
    ck(f"S1 {nm} def-only in base",
       sum(1 for ln in base.splitlines() if nm in ln) == 1)
    ck(f"S1 {nm} absent from folded",
       nm not in fold)
ck("S1 contrast PWCTL_R86_STREAM_WAIT_S is loaded",
   sum(1 for ln in base.splitlines()
       if "PWCTL_R86_STREAM_WAIT_S" in ln) == 2
   and sum(1 for ln in fold.splitlines()
           if "PWCTL_R86_STREAM_WAIT_S" in ln) == 2)

# S2 — self_serials --------------------------------------------------------
b_lines = [i for i, ln in enumerate(base.splitlines(), 1)
           if "self_serials" in ln]
f_lines = [i for i, ln in enumerate(fold.splitlines(), 1)
           if "self_serials" in ln]
ck("S2 base self_serials occurrences == 5",
   len(b_lines) == 5, str(b_lines))
ck("S2 base has 3 write sites",
   sum(1 for ln in base.splitlines()
       if "self_serials = []" in ln or "self_serials.append" in ln) == 3)
ck("S2 folded keeps only the recorded dict key",
   len(f_lines) == 1 and '"self_serials"' in fold.splitlines()[f_lines[0] - 1],
   str(f_lines))
ck("S2 no accumulator append in folded",
   "self_serials.append" not in fold and "self_serials = " not in fold)

# S3 — teardown call sites -------------------------------------------------
def calls_of(tree, name):
    out = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) \
                and n.func.id == name:
            out.append(n)
    return out


tear_calls = calls_of(bt, "_pwctl_r86_teardown")
ck("S3 teardown call sites == 5", len(tear_calls) == 5,
   str([c.lineno for c in tear_calls]))
ck("S3 every teardown call passes a 3rd positional arg",
   all(len(c.args) >= 3 for c in tear_calls))
tear_def = next(n for n in bt.body if isinstance(n, ast.FunctionDef)
                and n.name == "_pwctl_r86_teardown")
n_pos = len(tear_def.args.args)
n_def = len(tear_def.args.defaults)
ck("S3 teardown signature has no default for loads",
   tear_def.args.args[2].arg == "loads"
   and n_pos - n_def == 3 and n_def == 1,
   f"pos={n_pos} defaults={n_def} third="
   f"{tear_def.args.args[2].arg}")

# S4 — block call sites: loads default is live -----------------------------
blk_calls = calls_of(bt, "_pwctl_r86_block")
with_loads = [c for c in blk_calls if len(c.args) >= 4]
without = [c for c in blk_calls if len(c.args) < 4]
ck("S4 block call sites == 15", len(blk_calls) == 15)
ck("S4 exactly 5 block calls omit loads (guard retained)",
   len(without) == 5 and len(with_loads) == 10,
   f"without={len(without)} with={len(with_loads)}")

# S5 — leaf domain: _pwcat_r83_ns_load returns dict on both paths ----------
nsload = next(n for n in bt.body if isinstance(n, ast.FunctionDef)
              and n.name == "_pwcat_r83_ns_load")
rets = [n for n in ast.walk(nsload) if isinstance(n, ast.Return)]
ck("S5 _pwcat_r83_ns_load has exactly 2 returns", len(rets) == 2)
leaf_assigns = [n for n in ast.walk(nsload) if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == "leaf"
                        for t in n.targets)]
ck("S5 both leaf assignments are dict literals",
   len(leaf_assigns) == 2 and all(isinstance(a.value, ast.Dict)
                                  for a in leaf_assigns))
r86_loads = [n for n in ast.walk(bt) if isinstance(n, ast.Call)
             and isinstance(n.func, ast.Name)
             and n.func.id == "_pwctl_r86_load_ns"]
ck("S5 five r86 load sites", len(r86_loads) == 5)

# S6 — own_links guard domain: out/in are f-strings ------------------------
links = next(n for n in bt.body if isinstance(n, ast.FunctionDef)
             and n.name == "_pwctl_r86_links")
joined = [n for n in ast.walk(links)
          if isinstance(n, ast.Dict)
          and any(isinstance(k, ast.Constant)
                  and k.value in ("out", "in") for k in n.keys)]
ck("S6 _pwctl_r86_links out/in are JoinedStr",
   len(joined) >= 1 and all(
       isinstance(v, ast.JoinedStr) for d in joined for k, v in
       zip(d.keys, d.values)
       if isinstance(k, ast.Constant) and k.value in ("out", "in")))

# S7 — dsp early-return dominance -----------------------------------------
dsp = next(n for n in bt.body if isinstance(n, ast.FunctionDef)
           and n.name == "pwctl_dsp_r86_entry")
lines = base.splitlines()
i_store = next(i for i in range(BL, BH)
               if 'legs["tap_link"] = {"edges": edges' in lines[i - 1])
i_guard = next(i for i in range(BL, BH)
               if lines[i - 1].strip() == "if not edges:")
i_return = next(i for i in range(i_guard, BH)
                if "_pwctl_r86_block(" in lines[i - 1]
                and "return" in lines[i - 1])
i_verdict = next(i for i in range(BL, BH)
                 if 'if not legs["tap_link"]["edges"]' in lines[i - 1])
ck("S7 dominance store<guard<return<verdict",
   i_store < i_guard < i_return < i_verdict,
   f"{i_store}<{i_guard}<{i_return}<{i_verdict}")
ck("S7 folded removes the unreachable verdict",
   'if not legs["tap_link"]["edges"]' not in fold)

# S8 — solo_hi init --------------------------------------------------------
ck("S8 base has the None init", "solo_lo, solo_hi = mark(), None" in base)
ck("S8 folded drops the None init and keeps the real assignment",
   "solo_lo, solo_hi = mark(), None" not in fold
   and "solo_hi = mark()" in fold)

# S9 — ser str domain ------------------------------------------------------
ser_assign = next(i for i in range(BL, BH)
                  if lines[i - 1].strip().startswith("ser = "))
ck("S9 ser is str(...)", "str(" in lines[ser_assign - 1])
ck("S9 folded predicate == \"None\"",
   'ser == "None"' in fold and 'ser in (None, "None")' not in fold)

# S10 — module-level r86 surface intact ------------------------------------
def r86_names(tree):
    return {n.name for n in tree.body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            and (n.name.startswith("_pwctl_r86")
                 or n.name.startswith("pwctl_")
                 and n.name.endswith("_r86_entry"))}


bn, fn = r86_names(bt), r86_names(ft)
ck("S10 r86 module-level defs unchanged",
   bn == fn and len(bn) == 25, f"{len(bn)} vs {len(fn)}")
for entry in ("pwctl_addr_r86_entry", "pwctl_params_r86_entry",
              "pwctl_dsp_r86_entry", "pwctl_meta_r86_entry",
              "pwctl_tools_r86_entry"):
    ck(f"S10 {entry} present in folded", entry in fn)

# S11 — wiring intact ------------------------------------------------------
main = next(n for n in ft.body if isinstance(n, ast.FunctionDef)
            and n.name == "main")
main_src = ast.get_source_segment(fold, main)
for frag in ('parser.add_argument("--probe-pwctl-r86"',
             "args.probe_pwctl_r86",
             'measurements["pwctl_addr_r86_probe"]',
             'measurements["pwctl_params_r86_probe"]',
             'measurements["pwctl_dsp_r86_probe"]',
             'measurements["pwctl_meta_r86_probe"]',
             'measurements["pwctl_tools_r86_probe"]',
             "_r86_family_lock = _pwctl_r86_family_lock()",
             'mode = "probe-pwctl-r86" if args.probe_pwctl_r86',
             'suffix = "-pwctl-r86" if args.probe_pwctl_r86'):
    ck(f"S11 wiring fragment present: {frag[:44]}", frag in main_src)

# S12 — patch confinement --------------------------------------------------
patch = Path("../r86-simplifier.patch").read_text(encoding="utf-8")
starts = [int(ln.split("-")[1].split(",")[0]) for ln in
          patch.splitlines() if ln.startswith("@@ -")]
ck("S12 all hunks inside the r86 block",
   all(BL <= s <= BH for s in starts), str(starts))
ck("S12 patch sha256",
   hashlib.sha256(patch.encode()).hexdigest()
   == "5cc93d42cb77288c5877ad63db22e6c8011c86481df1f22ac42d5414306dccf7")

# S13 — no line outside the r86 block is changed --------------------------
import re
import subprocess
d = subprocess.run(["diff", "-u", "base-measure_audio.py",
                    "folded/measure_audio.py"],
                   capture_output=True, text=True).stdout
old_no = new_no = None
bad, n_changed = [], 0
for ln in d.splitlines():
    if ln.startswith("@@"):
        m = re.match(r"@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@", ln)
        old_no, new_no = int(m.group(1)), int(m.group(2))
        continue
    if old_no is None:
        continue
    if ln.startswith("-") and not ln.startswith("---"):
        n_changed += 1
        if not (BL <= old_no <= BH):
            bad.append(("old", old_no, ln))
        old_no += 1
    elif ln.startswith("+") and not ln.startswith("+++"):
        n_changed += 1
        if not (BL <= new_no <= BH):
            bad.append(("new", new_no, ln))
        new_no += 1
    elif ln.startswith(" "):
        old_no += 1
        new_no += 1
ck("S13 all changed lines inside the r86 block",
   not bad, f"{n_changed} changed lines; bad={bad[:3]}")

n_fail = sum(1 for _, ok, _ in checks if not ok)
print(f"\n{len(checks) - n_fail}/{len(checks)} PASS")
sys.exit(1 if n_fail else 0)
