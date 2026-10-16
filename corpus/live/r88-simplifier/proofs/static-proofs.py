#!/usr/bin/env python3
"""r88 simplifier — static proof suite (S1..S12) over the pinned blob
and the unapplied fold. Reads only; writes nothing."""
import ast
import hashlib
import os
import re
import subprocess
import sys
import symtable

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "base-measure_audio.py")
FOLDED = os.path.join(HERE, "folded", "measure_audio.py")
DIFF = os.path.join(HERE, "fold.diff")
TREE = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))  # repo root
R0, R1 = 27507, 29252
PIN_SHA = "ad9d59b1e0dc5e2be4274f4966e571dabefed94076c06093eed1bf4cd2aef4c4"
FOLD_SHA = "1beac939703a163093c2f634c3ec61e3e5d2bea6ac7a56966c3f398e55a045a6"

base_text = open(BASE, encoding="utf-8").read()
fold_text = open(FOLDED, encoding="utf-8").read()
base_lines = base_text.splitlines()
fold_lines = fold_text.splitlines()
base_tree = ast.parse(base_text)
fold_tree = ast.parse(fold_text)
base_region = "\n".join(base_lines[R0 - 1:R1])
fold_region = "\n".join(fold_lines[R0 - 1:R1 - 7])

FAIL = []


def check(name, cond, detail=""):
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")
    if not cond:
        FAIL.append(name)


# ---------------- S1: pin, region, insertion-only landing ----------------
check("S1a pinned blob sha256", hashlib.sha256(base_text.encode()).hexdigest()
      == PIN_SHA)
check("S1b region markers",
      base_lines[R0 - 1].startswith("# r88:") and
      base_lines[R1 - 1].strip() == "return entry" and
      base_lines[R1 + 2].startswith("def main():"))
patch = subprocess.run(["git", "diff", "c19bec96^", "c19bec96", "--",
                        "corpus/fixtures/measure_audio.py"],
                       cwd=TREE, capture_output=True, text=True).stdout
del_lines = [ln for ln in patch.splitlines()
             if ln.startswith("-") and not ln.startswith("---")]
add_lines = [ln for ln in patch.splitlines()
             if ln.startswith("+") and not ln.startswith("+++")]
check("S1c landing deletions == 3 wiring splices",
      len(del_lines) == 3 and all(
          ("pwbind_r87" in ln or "probe_pwbind_r87" in ln)
          for ln in del_lines),
      f"({len(del_lines)} deletions)")
check("S1d landing additions == 1772", len(add_lines) == 1772,
      f"({len(add_lines)})")
check("S1e every wiring splice replaced by a btwit line",
      all(any("btwit" in a for a in add_lines) for _ in del_lines))

# ---------------- S2: r88 defs/constants all used ------------------------
mod_defs = {}
for node in base_tree.body:
    if R0 <= node.lineno <= R1:
        if isinstance(node, ast.FunctionDef):
            mod_defs[node.name] = node.lineno
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    mod_defs[t.id] = node.lineno
unused = []
for name in mod_defs:
    pat = re.compile(r"(?<![\w.])" + re.escape(name) + r"(?![\w])")
    uses = [i for i, ln in enumerate(base_lines, 1) if pat.search(ln)]
    if len(uses) < 2:
        unused.append((name, uses))
check("S2a every r88 module-level def/const referenced >=1x beyond "
      "definition", not unused, f"({len(mod_defs)} names)")

# ---------------- S3: runner dead parameters -----------------------------
run_fn = next(n for n in base_tree.body if isinstance(n, ast.FunctionDef)
              and n.name == "_btwit_r88_run")
params = [a.arg for a in run_fn.args.args]
calls = []
for sub in ast.walk(base_tree):
    if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name) \
            and sub.func.id == "_btwit_r88_run":
        calls.append((sub.lineno, len(sub.args),
                      sorted(k.arg for k in sub.keywords)))
check("S3a runner call sites == 19", len(calls) == 19)
check("S3b zero call sites bind env/stdin_data",
      all(("env" not in kw) and ("stdin_data" not in kw) and npos <= 2
          for _, npos, kw in calls))
check("S3c env/stdin_data appear only inside the runner",
      all((("env" not in ln and "stdin_data" not in ln) or
           (27659 <= i <= 27680))
          for i, ln in enumerate(base_lines[R0 - 1:R1], R0)))
body_src = ast.get_source_segment(base_text, run_fn)
check("S3d runner body uses both params only in the folded expressions",
      "stdin_data is not None" in body_src and "env=env" in body_src
      and "communicate(input=stdin_data" in body_src)

# ---------------- S4: teardown signature / call sites --------------------
td = next(n for n in base_tree.body if isinstance(n, ast.FunctionDef)
          and n.name == "_btwit_r88_teardown")
check("S4a teardown has 3 params, 0 defaults",
      len(td.args.args) == 3 and len(td.args.defaults) == 0)
td_calls = [sub for sub in ast.walk(base_tree)
            if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name)
            and sub.func.id == "_btwit_r88_teardown"]
check("S4b teardown 3/3 call sites pass 3 positionals, no kwargs",
      len(td_calls) == 3 and all(len(c.args) == 3 and not c.keywords
                                 for c in td_calls))
stores = [(i, ln.strip()) for i, ln in
          enumerate(base_lines[R0 - 1:R1], R0)
          if re.match(r"\s*loads\[", ln) and " = " in ln]
check("S4c every loads[...] store is _btwit_r88_load_ns(...)",
      len(stores) == 4 and all("_btwit_r88_load_ns(" in ln
                               for _, ln in stores))
check("S4d loads = {} initialized in all 3 entries",
      sum(1 for ln in base_lines[R0 - 1:R1] if ln.strip() == "loads = {}")
      == 3)

# ---------------- S5: _pwcat_r83_ns_load always returns a dict -----------
pwcat = next(n for n in base_tree.body if isinstance(n, ast.FunctionDef)
             and n.name == "_pwcat_r83_ns_load")
returns = [n for n in ast.walk(pwcat) if isinstance(n, ast.Return)]
check("S5a _pwcat_r83_ns_load has exactly 2 returns, both `leaf`",
      len(returns) == 2 and all(
          isinstance(r.value, ast.Name) and r.value.id == "leaf"
          for r in returns))
dict_assigns = [n for n in ast.walk(pwcat)
                if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == "leaf"
                        for t in n.targets)
                and isinstance(n.value, ast.Dict)]
check("S5b leaf is built from 2 dict literals (else-path + except-path)",
      len(dict_assigns) == 2)
check("S5c load_ns sets field/value unconditionally",
      all(f'leaf["field"] = "sink_name"' in ast.get_source_segment(
              base_text, next(n for n in base_tree.body
                              if isinstance(n, ast.FunctionDef)
                              and n.name == "_btwit_r88_load_ns"))
          for _ in (0,)) and
      'leaf["value"] = name' in ast.get_source_segment(
          base_text, next(n for n in base_tree.body
                          if isinstance(n, ast.FunctionDef)
                          and n.name == "_btwit_r88_load_ns")))

# ---------------- S6: block default / call-site split --------------------
blk = next(n for n in base_tree.body if isinstance(n, ast.FunctionDef)
           and n.name == "_btwit_r88_block")
blk_calls = [sub for sub in ast.walk(base_tree)
             if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name)
             and sub.func.id == "_btwit_r88_block"]
omitted = [c.lineno for c in blk_calls if len(c.args) == 3]
passed = [c.lineno for c in blk_calls if len(c.args) == 4]
check("S6a block has default loads=None",
      len(blk.args.args) == 4 and len(blk.args.defaults) == 1)
check("S6b block: 3 call sites omit loads, 5 pass it",
      len(omitted) == 3 and len(passed) == 5,
      f"omit={omitted} pass={passed}")
check("S6c omitted-loads sites are the missing-tools early blocks",
      all("missing tools" in base_lines[ln + 1]
          for ln in omitted), str(omitted))

# ---------------- S7: _frames_cache no-op pops ---------------------------
occ = [(i, ln.strip()) for i, ln in enumerate(base_lines, 1)
       if "_frames_cache" in ln]
check("S7a exactly 4 _frames_cache occurrences in the whole file",
      len(occ) == 4 and [i for i, _ in occ] == [29047, 29070, 29132, 29175])
tu = next(n for n in base_tree.body if isinstance(n, ast.FunctionDef)
          and n.name == "_btwit_r88_top_until")
tu_writes = [n for n in ast.walk(tu)
             if isinstance(n, ast.Subscript)
             and isinstance(n.ctx, ast.Store)
             and isinstance(n.slice, ast.Constant)
             and n.slice.value == "_frames_cache"]
check("S7b top_until never writes _frames_cache", not tu_writes)
check("S7c the only write is on legs['pt_n3'] (line 29047)",
      "legs[\"pt_n3\"][\"_frames_cache\"]" in base_lines[29046])

# ---------------- S8: T6 comprehension target ----------------------------
comp = None
for sub in ast.walk(base_tree):
    if isinstance(sub, ast.comprehension) and \
            isinstance(sub.target, ast.Tuple) and \
            [e.id for e in sub.target.elts] == ["nid", "n"]:
        comp = sub
check("S8a found the (nid, n) comprehension", comp is not None)
if comp:
    loads_nid = [x for x in ast.walk(comp)
                 if isinstance(x, ast.Name) and isinstance(x.ctx, ast.Load)
                 and x.id == "nid"]
    check("S8b `nid` never loaded inside the comprehension",
          not loads_nid)

# ---------------- S9: symtable equivalence ------------------------------
def syms(path):
    st = symtable.symtable(open(path, encoding="utf-8").read(), path, "exec")
    return {child.get_name(): {s.get_name() for s in child.get_symbols()}
            for child in st.get_children()}

sb, sf = syms(BASE), syms(FOLDED)
fn_names = {n.name for n in base_tree.body
            if isinstance(n, ast.FunctionDef) and R0 <= n.lineno <= R1}
check("S9a every r88 function has a symtable entry",
      not (fn_names - set(sb)), str(fn_names - set(sb)))
diffs = {n: (sb[n] ^ sf[n]) for n in fn_names
         if n in sb and sb[n] != sf[n]}
check("S9b only _btwit_r88_run's symbol set changes, by exactly "
      "{env, stdin_data}",
      set(diffs) == {"_btwit_r88_run"} and
      diffs.get("_btwit_r88_run") == {"env", "stdin_data"}, str(diffs))

# ---------------- S10: leg-key / entry-key census unchanged -------------
def keys_of(text, lines, region_slice):
    reg = "\n".join(lines[region_slice])
    legs = set(re.findall(r'legs\["([^"]+)"\]', reg))
    legs |= set(re.findall(r'legs\.get\("([^"]+)"\)', reg))
    ent = set(re.findall(r'entry\["([^"]+)"\]', reg))
    ent |= set(re.findall(r'entry\.setdefault\("([^"]+)"', reg))
    ent |= set(re.findall(r'entry\.get\("([^"]+)"\)', reg))
    return legs, ent

bl, be = keys_of(base_text, base_lines, slice(R0 - 1, R1))
fl, fe = keys_of(fold_text, fold_lines, slice(R0 - 1, R1 - 7))
check("S10a leg-key set identical base vs folded",
      bl == fl and len(bl) > 70, f"({len(bl)} keys)")
check("S10b entry-key set identical base vs folded",
      be == fe and len(be) > 5, f"({sorted(be)})")

# ---------------- S11: patch round-trip ----------------------------------
numstat = subprocess.run(["git", "apply", "--numstat", DIFF], cwd=TREE,
                         capture_output=True, text=True).stdout.strip()
check("S11a numstat 12 19 (net -7)", numstat ==
      "12\t19\tcorpus/fixtures/measure_audio.py", repr(numstat))
chk = subprocess.run(["git", "apply", "--check", DIFF], cwd=TREE,
                     capture_output=True, text=True)
check("S11b git apply --check clean against live tree",
      chk.returncode == 0 and not chk.stderr.strip(), repr(chk.stderr))
check("S11c folded sha256 == 1beac939...",
      hashlib.sha256(fold_text.encode()).hexdigest() == FOLD_SHA)
check("S11d folded line count 30497", len(fold_lines) == 30497)
hunk_starts = [int(m) for m in re.findall(r"^@@ -(\d+)", open(DIFF).read(),
                                          re.M)]
check("S11e all hunks inside the r88 region",
      all(R0 - 3 <= h <= R1 for h in hunk_starts), str(hunk_starts))
dlines = [ln for ln in open(DIFF).read().splitlines()
          if ln.startswith("-") and not ln.startswith("---")]
alines = [ln for ln in open(DIFF).read().splitlines()
          if ln.startswith("+") and not ln.startswith("+++")]
check("S11f patch adds 12 / deletes 19 lines (net -7)",
      len(alines) == 12 and len(dlines) == 19,
      f"add={len(alines)} del={len(dlines)}")

# ---------------- S12: no tracked writes by this seat --------------------
tracked = subprocess.run(["git", "diff", "--numstat", "HEAD", "--",
                          "corpus/fixtures/measure_audio.py"],
                         cwd=TREE, capture_output=True, text=True).stdout
check("S12a tracked fixture unmodified vs HEAD", tracked.strip() == "")

print()
print(f"STATIC PROOFS: {'ALL PASS' if not FAIL else 'FAILURES: ' + str(FAIL)}")
sys.exit(1 if FAIL else 0)
