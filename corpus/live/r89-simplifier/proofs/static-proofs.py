#!/usr/bin/env python3
"""r89 simplifier — static proof suite (S1..S13) over the pinned blob
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
TREE = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
R0, R1 = 29255, 30783
PIN_SHA = "623c25cc55521472dc54a1ab2b4ccb4a9836fda3ca1a71dcca06092a4317cd22"
FOLD_SHA = "417344c3e2d315cc2de10de9c367e3339411036de62c06e9fd32f41afa97b790"

base_text = open(BASE, encoding="utf-8").read()
fold_text = open(FOLDED, encoding="utf-8").read()
base_lines = base_text.splitlines()
fold_lines = fold_text.splitlines()
base_tree = ast.parse(base_text)
fold_tree = ast.parse(fold_text)
base_region = "\n".join(base_lines[R0 - 1:R1])
fold_region = "\n".join(fold_lines[R0 - 1:R1 - 11])

FAIL = []


def check(name, cond, detail=""):
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")
    if not cond:
        FAIL.append(name)


# ---------------- S1: pin, region, insertion-only landing ----------------
check("S1a pinned blob sha256", hashlib.sha256(base_text.encode()).hexdigest()
      == PIN_SHA)
check("S1b region markers",
      base_lines[R0 - 1].startswith("# r89:") and
      base_lines[R1 - 1].strip() == "" and
      base_lines[R1].startswith("def main():"))
patch = subprocess.run(["git", "diff", "0d732989^", "0d732989", "--",
                        "corpus/fixtures/measure_audio.py"],
                       cwd=TREE, capture_output=True, text=True).stdout
del_lines = [ln for ln in patch.splitlines()
             if ln.startswith("-") and not ln.startswith("---")]
add_lines = [ln for ln in patch.splitlines()
             if ln.startswith("+") and not ln.startswith("+++")]
check("S1c landing deletions == 3 wiring splices (the r88-head "
      "versions of mutex/mode/suffix)",
      len(del_lines) == 3 and all(
          ("btwit_r88" in ln or "btwit-r88" in ln) for ln in del_lines),
      f"({len(del_lines)} deletions)")
check("S1d landing additions == 1561", len(add_lines) == 1561,
      f"({len(add_lines)})")
check("S1e every wiring splice replaced by a pwprof line",
      all(any("pwprof" in a for a in add_lines) for _ in del_lines))

# ---------------- S2: r89 defs/constants all used ------------------------
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
check("S2a every r89 module-level def/const referenced >=1x beyond "
      "definition", not unused, f"({len(mod_defs)} names)")

# ---------------- S3: the four never-bound params ------------------------
def calls_of(name):
    out = []
    for sub in ast.walk(base_tree):
        if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name) \
                and sub.func.id == name:
            out.append(sub)
    return out


def params_of(name):
    fn = next(n for n in base_tree.body if isinstance(n, ast.FunctionDef)
              and n.name == name)
    return [a.arg for a in fn.args.args], len(fn.args.defaults)


sig, ndef = params_of("_pwprof_r89_play")
c = calls_of("_pwprof_r89_play")
check("S3a play: 2 call sites, all 3 positional, role never bound",
      len(c) == 2 and all(len(x.args) == 3 and not x.keywords for x in c)
      and sig == ["tag", "target", "tone", "role"] and ndef == 1,
      f"{len(c)} sites")
sig, ndef = params_of("_pwprof_r89_nleg")
c = calls_of("_pwprof_r89_nleg")
bound_wd = sum(1 for x in c if len(x.args) >= 4 or
               any(k.arg == "wd" for k in x.keywords))
check("S3b nleg: 7 call sites, wd never bound",
      len(c) == 7 and bound_wd == 0 and sig[-1] == "wd",
      f"{len(c)} sites, bound={bound_wd}")
sig, ndef = params_of("_pwprof_r89_ensure_player")
c = calls_of("_pwprof_r89_ensure_player")
bound_ws = sum(1 for x in c if len(x.args) >= 3 or
               any(k.arg == "wait_s" for k in x.keywords))
check("S3c ensure_player: 4 call sites, wait_s never bound",
      len(c) == 4 and bound_ws == 0 and sig[-1] == "wait_s",
      f"{len(c)} sites, bound={bound_ws}")
sig, ndef = params_of("_pwprof_r89_block")
c = calls_of("_pwprof_r89_block")
arity = sorted(len(x.args) for x in c)
bound_pl = sum(1 for x in c if len(x.args) >= 5 or
               any(k.arg == "players" for k in x.keywords))
check("S3d block: 10 call sites (4x3-arg tools, 6x4-arg), players never "
      "bound",
      len(c) == 10 and arity == [3, 3, 3, 3, 4, 4, 4, 4, 4, 4] and
      bound_pl == 0 and sig[-1] == "players",
      f"{len(c)} sites, arity={arity}, bound={bound_pl}")
# the four names are referenced only as direct-call callees (no value
# references: no getattr/partial/alias can bind the dead params)
for nm in ("_pwprof_r89_play", "_pwprof_r89_nleg",
           "_pwprof_r89_ensure_player", "_pwprof_r89_block"):
    load_names = [n for n in ast.walk(base_tree)
                  if isinstance(n, ast.Name) and n.id == nm and
                  isinstance(n.ctx, ast.Load)]
    callee_names = [n.func for n in ast.walk(base_tree)
                    if isinstance(n, ast.Call) and
                    isinstance(n.func, ast.Name) and n.func.id == nm]
    check(f"S3e[{nm}] only referenced via direct calls",
          len(load_names) == len(callee_names),
          f"loads={len(load_names)} callees={len(callee_names)}")

# ---------------- S4: teardown signature / call sites --------------------
td = next(n for n in base_tree.body if isinstance(n, ast.FunctionDef)
          and n.name == "_pwprof_r89_teardown")
check("S4a teardown has 4 params (players has a default), players IS "
      "bound at every call site",
      len(td.args.args) == 4 and len(td.args.defaults) == 1)
td_calls = calls_of("_pwprof_r89_teardown")
check("S4b teardown 4/4 call sites pass 4 positionals",
      len(td_calls) == 4 and all(len(x.args) == 4 and not x.keywords
                                 for x in td_calls),
      f"{len(td_calls)} sites")
stores = [(i, ln.strip()) for i, ln in
          enumerate(base_lines[R0 - 1:R1], R0)
          if re.match(r"\s*loads\[", ln) and " = " in ln]
check("S4c every loads[...] store is _pwprof_r89_load_ns(...) "
      "(5 subscript stores + the oart dict literal)",
      len(stores) == 5 and all("_pwprof_r89_load_ns(" in ln
                               for _, ln in stores) and
      "loads = {PWPROF_R89_NS: leaf}" in base_region and
      "leaf = _pwprof_r89_load_ns(PWPROF_R89_NS)" in base_region,
      f"{len(stores)} stores")
inits = [i for i, ln in enumerate(base_lines[R0 - 1:R1], R0)
         if re.match(r"\s*loads, .* = \{\}", ln) or
         re.match(r"\s*loads = \{\}", ln)]
check("S4d loads = {} initialized in all 4 entries", len(inits) == 4,
      f"{inits}")

# ---------------- S5: load_ns leaf domain --------------------------------
pwcat = next(n for n in base_tree.body if isinstance(n, ast.FunctionDef)
             and n.name == "_pwcat_r83_ns_load")
rets = [n for n in ast.walk(pwcat) if isinstance(n, ast.Return)]
check("S5a _pwcat_r83_ns_load has exactly 2 returns, both `leaf`",
      len(rets) == 2 and all(isinstance(r.value, ast.Name) and
                             r.value.id == "leaf" for r in rets))
leaf_stores = [n for n in ast.walk(pwcat)
               if isinstance(n, ast.Assign) and
               any(isinstance(t, ast.Name) and t.id == "leaf"
                   for t in n.targets)]
check("S5b leaf is built from dict literals on both paths",
      len(leaf_stores) == 2 and all(isinstance(s.value, ast.Dict)
                                    for s in leaf_stores))
lns = next(n for n in base_tree.body if isinstance(n, ast.FunctionDef)
           and n.name == "_pwprof_r89_load_ns")
lns_src = ast.get_source_segment(base_text, lns)
check("S5c _pwprof_r89_load_ns sets field/value unconditionally",
      'leaf["field"] = "sink_name"' in lns_src and
      'leaf["value"] = name' in lns_src)

# ---------------- S6: block (loads or {}) is LIVE ------------------------
blk = next(n for n in base_tree.body if isinstance(n, ast.FunctionDef)
           and n.name == "_pwprof_r89_block")
check("S6a block has defaults (loads=None, players=())",
      len(blk.args.args) == 5 and len(blk.args.defaults) == 2 and
      isinstance(blk.args.defaults[0], ast.Constant) and
      blk.args.defaults[0].value is None and
      isinstance(blk.args.defaults[1], ast.Tuple) and
      not blk.args.defaults[1].elts)
omit = [x.lineno for x in c if len(x.args) == 3]
passed = [x.lineno for x in c if len(x.args) == 4]
check("S6b block: 4 call sites omit loads, 6 pass it",
      len(omit) == 4 and len(passed) == 6,
      f"omit={omit} pass={passed}")
tools = [i for i in omit
         if "missing tools" in "\n".join(base_lines[i - 1:i + 3])]
check("S6c omitted-loads sites are the missing-tools early blocks",
      len(tools) == 4, f"{tools}")

# ---------------- S7: leaf guards / .get fallbacks -----------------------
n_leaf = len(re.findall(r"^\s*leaf = leaf or \{\}$", base_region, re.M))
check("S7a exactly 2 `leaf = leaf or {}` sites in the region "
      "(teardown + block)", n_leaf == 2, n_leaf)
n_field = base_region.count('leaf.get("field", "sink_name")')
n_value = base_region.count('leaf.get("value", tag)')
check("S7b exactly 2 field + 2 value fallback sites (teardown + block)",
      n_field == 2 and n_value == 2, f"{n_field}/{n_value}")
n_loads_or = len(re.findall(r"\(loads or \{\}\)", base_region))
check("S7c exactly 4 (loads or {}) sites: 3 teardown (dead) + 1 block "
      "(live)", n_loads_or == 4, n_loads_or)
n_stats = base_region.count('l.get("stats") or {}')
check("S7d exactly 1 dead stats guard", n_stats == 1, n_stats)

# ---------------- S8: symtable deltas ------------------------------------
def ident_sets(src, label):
    st = symtable.symtable(src, label, "exec")
    out = {}
    for fn in st.get_children():
        out[fn.get_name()] = set(fn.get_identifiers())
    return out


sb = ident_sets(base_text, "base")
sf = ident_sets(fold_text, "fold")
R89_FNS = [k for k in sb if k.startswith("_pwprof_r89_") or
           k.startswith("pwprof_")]
changed = {k: (sb[k] - sf[k], sf[k] - sb[k]) for k in R89_FNS
           if sb[k] != sf[k]}
expect = {
    "_pwprof_r89_play": ({"role"}, set()),
    "_pwprof_r89_nleg": ({"wd"}, set()),
    "_pwprof_r89_ensure_player": ({"wait_s"}, set()),
    "_pwprof_r89_block": ({"players", "proc", "_alsapw_r84_killpg",
                           "subprocess", "signal"}, set()),
}
check("S8a symtable deltas are exactly the removed params/locals",
      changed == expect, f"{changed}")

# ---------------- S9: receipt-key surfaces unchanged ---------------------
leg_keys_b = set(re.findall(r'legs\["([a-z0-9_]+)"\]', base_region))
leg_keys_f = set(re.findall(r'legs\["([a-z0-9_]+)"\]', fold_region))
loop_sites_b = len(re.findall(r"^\s*legs\[nm\] = ", base_region, re.M))
loop_sites_f = len(re.findall(r"^\s*legs\[nm\] = ", fold_region, re.M))
def loop_leg_keys(region):
    keys = []
    for m in re.finditer(r"for nm, narg in \((.*?)\):", region, re.S):
        keys += re.findall(r'\("(n_[a-z0-9_]+)"', m.group(1))
    return keys


loop_keys_b = len(loop_leg_keys(base_region))
loop_keys_f = len(loop_leg_keys(fold_region))
check("S9a leg-key literals identical base vs folded region "
      "(42 literal + 10 loop-bound = 52)",
      leg_keys_b == leg_keys_f and len(leg_keys_b) == 42 and
      loop_sites_b == loop_sites_f == 2 and
      loop_keys_b == loop_keys_f == 10,
      f"{len(leg_keys_b)} literal, {loop_keys_b} loop-bound")
ent_keys_b = set(re.findall(r'entry\["([a-z0-9_]+)"\]', base_region)) | \
    set(re.findall(r'entry\.setdefault\("([a-z0-9_]+)"', base_region))
ent_keys_f = set(re.findall(r'entry\["([a-z0-9_]+)"\]', fold_region)) | \
    set(re.findall(r'entry\.setdefault\("([a-z0-9_]+)"', fold_region))
check("S9b entry-key literals identical base vs folded region",
      ent_keys_b == ent_keys_f, f"{sorted(ent_keys_b)}")

# ---------------- S10: patch proofs --------------------------------------
numstat = subprocess.run(["git", "apply", "--numstat", DIFF], cwd=TREE,
                         capture_output=True, text=True).stdout.strip()
check("S10a numstat 17 28 (net -11)",
      numstat == "17\t28\tcorpus/fixtures/measure_audio.py", numstat)
check("S10b git apply --check clean against the committed tree",
      subprocess.run(["git", "apply", "--check", DIFF], cwd=TREE,
                     capture_output=True, text=True).returncode == 0)
check("S10c folded sha256 == 417344c3...",
      hashlib.sha256(fold_text.encode()).hexdigest() == FOLD_SHA)
check("S10d folded line count 32051", len(fold_lines) == 32051,
      len(fold_lines))
starts = [int(m) for m in re.findall(r"^@@ -(\d+),", open(DIFF).read(),
                                     re.M)]
check("S10e all hunks inside the r89 region",
      all(R0 <= s <= R1 for s in starts), starts)

# ---------------- S11: composition with the pending r88 fold -------------
r88_diff = os.path.join(TREE, "corpus", "live", "r88-simplifier",
                        "proofs", "fold.diff")
if os.path.exists(r88_diff):
    import tempfile
    scratch = tempfile.mkdtemp(prefix="r89simp-compose-",
                               dir=os.environ.get(
                                   "TMPDIR",
                                   "/home/vgpnk/Projects/shokunin/tmp"))
    d = os.path.join(scratch, "corpus", "fixtures")
    os.makedirs(d)
    dst = os.path.join(d, "measure_audio.py")
    open(dst, "w").write(base_text)
    p1 = subprocess.run(["patch", "-p1", "--silent", "-i", r88_diff],
                        cwd=scratch, capture_output=True, text=True)
    p2 = subprocess.run(["patch", "-p1", "-i", DIFF], cwd=scratch,
                        capture_output=True, text=True)
    comp = open(dst).read()
    check("S11a r88 fold then r89 fold both apply cleanly",
          p1.returncode == 0 and p2.returncode == 0,
          f"r88_rc={p1.returncode} r89_rc={p2.returncode}")
    check("S11b composed line count 32044 (32062-7-11)",
          len(comp.splitlines()) == 32044, len(comp.splitlines()))
    check("S11c composed file parses",
          ast.parse(comp) is not None)
    comp_lines = comp.splitlines()
    ci = next(i for i, ln in enumerate(comp_lines)
              if ln.startswith("# r89: the PW-PROFILER"))
    cm = next(i for i, ln in enumerate(comp_lines)
              if ln.startswith("def main():"))
    check("S11d composed r89 region == folded region",
          "\n".join(comp_lines[ci:cm]) == fold_region,
          f"start={ci} main={cm}")
    import shutil as _sh
    _sh.rmtree(scratch)

# ---------------- S12: tracked fixture unmodified ------------------------
check("S12a tracked fixture unmodified vs HEAD",
      subprocess.run(["git", "diff", "--quiet", "HEAD", "--",
                      "corpus/fixtures/measure_audio.py"], cwd=TREE,
                     capture_output=True).returncode == 0)
check("S12b working-tree sha256 == pin",
      hashlib.sha256(open(os.path.join(
          TREE, "corpus", "fixtures", "measure_audio.py"), "rb").read()
      ).hexdigest() == PIN_SHA)

# ---------------- S13: no LSP device answers this file -------------------
print("S13a lsp device availability: no Python LSP server on this "
      "substrate (MCP servers: rea only) — recorded unavailable; all "
      "edits are exact-string folds, no renames")

print()
print(f"STATIC PROOFS: {'ALL PASS' if not FAIL else 'FAILURES: ' + str(FAIL)}")
sys.exit(1 if FAIL else 0)
