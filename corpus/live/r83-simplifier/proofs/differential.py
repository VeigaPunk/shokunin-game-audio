#!/usr/bin/env python3
"""r83-simplifier differential harness — the narrow behavioral check.

Imports the BASE and FOLDED copies from a scratch dir (never from the repo,
so no __pycache__ lands in the tree) and compares the edited helpers on
identical inputs. D0 re-applies the patch to a scratch copy with `patch -p1`
and asserts byte-identity with the folded copy. No live PipeWire process is
ever spawned: the modules' own `subprocess` / `os` / `pw-dump` surfaces are
rebound INSIDE the imported module only (the global modules are untouched).

Run:  PYTHONDONTWRITEBYTECODE=1 python3 -B differential.py
Exit 0 = every check PASS.
"""
import ast
import hashlib
import importlib.util
import json
import os as real_os
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
BASE = REPO / "corpus/live/r83-simplifier/proofs/base-measure_audio.py"
FOLDED = REPO / "corpus/live/r83-simplifier/folded/measure_audio.py"
PATCH = REPO / "corpus/live/r83-simplifier/r83-simplifier.patch"
SCRATCH = Path("/tmp/r83sprobe")
fails = []


def check(cond, msg, extra=""):
    print(("PASS  " if cond else "FAIL  ") + msg +
          (("  " + extra) if extra else ""))
    if not cond:
        fails.append(msg)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def slice_between(path, start_marker, end_marker, occurrence=0):
    """Source slice [start_marker line, end_marker line) of a file copy."""
    txt = Path(path).read_text().splitlines()
    hits = [k for k, l in enumerate(txt) if start_marker in l]
    i = hits[occurrence]
    j = next(k for k, l in enumerate(txt) if k > i and end_marker in l)
    return "\n".join(txt[i:j])


def replay(path, start_marker, end_marker, env, ret="None"):
    """Exec a source slice as a function body (dedented) and return the
    value of `ret` (a comma-list of names, evaluated after the slice)."""
    body = textwrap.dedent(slice_between(path, start_marker, end_marker))
    src = "def _probe():\n" + textwrap.indent(body, "    ") + \
          f"\n    return ({ret})\n"
    scope = dict(env)
    exec(compile(src, str(path), "exec"), scope)
    return scope["_probe"]()


print("== D0: patch re-application is byte-identical to the folded copy ==")
if SCRATCH.exists():
    shutil.rmtree(SCRATCH)
(SCRATCH / "apply/corpus/fixtures").mkdir(parents=True)
shutil.copy(BASE, SCRATCH / "apply/corpus/fixtures/measure_audio.py")
r = subprocess.run(["patch", "-p1", "-i", str(PATCH)],
                   cwd=SCRATCH / "apply", capture_output=True, text=True)
applied = SCRATCH / "apply/corpus/fixtures/measure_audio.py"
check(r.returncode == 0, "patch -p1 applied clean",
      f"(rc={r.returncode} {r.stdout.strip()[:120]})")
check(sha(applied) == sha(FOLDED), "patched copy == folded copy (sha256)",
      f"{sha(applied)[:16]} == {sha(FOLDED)[:16]}")
check(sha(BASE) ==
      "26431adf29ab122bbf1f55ef03c9aa47bf9825c61654562d9a421117434f5eea",
      "base copy == committed fixture sha", sha(BASE)[:16])

print("\n== D1: import both copies from the scratch dir ==")
mods = {}
for tag, src in (("base", BASE), ("fold", FOLDED)):
    dst = SCRATCH / f"{tag}_measure_audio.py"
    shutil.copy(src, dst)
    spec = importlib.util.spec_from_file_location(f"r83_{tag}", dst)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mods[tag] = mod
base, fold = mods["base"], mods["fold"]
check(True, "both modules import (bytecode disabled)")

# --------------------------------------------------------------- shims
KILLS = []


class FakeProc:
    def __init__(self, argv, live=True):
        self.argv = list(argv)
        self.pid = 900000 + len(KILLS)
        self._live = live
        self.returncode = None if live else 0
        self.stderr = _Empty()

    def poll(self):
        return None if self._live else self.returncode

    def wait(self, timeout=None):
        if self._live and timeout is not None:
            raise subprocess.TimeoutExpired(self.argv[0], timeout)
        self._live = False
        if self.returncode is None:
            self.returncode = 0
        return self.returncode


class _Empty:
    def read(self):
        return b""


class SubprocessShim:
    DEVNULL = subprocess.DEVNULL
    PIPE = subprocess.PIPE
    TimeoutExpired = subprocess.TimeoutExpired
    CompletedProcess = subprocess.CompletedProcess

    def __init__(self, live_argv_prefixes=("pw-loopback",)):
        self.seen = []
        self.live_prefixes = live_argv_prefixes

    def Popen(self, argv, **kw):
        self.seen.append(list(argv))
        live = any(argv[0] == p for p in self.live_prefixes)
        return FakeProc(argv, live=live)

    def run(self, argv, **kw):
        self.seen.append(list(argv))
        return subprocess.CompletedProcess(argv, 1, b"", b"")


class OsShim:
    def killpg(self, pid, sig):
        KILLS.append((pid, sig))

    def __getattr__(self, k):
        return getattr(real_os, k)


def arm(mod):
    shim = SubprocessShim()
    mod.subprocess = shim
    mod.os = OsShim()
    mod._pwcat_r83_graph = lambda: {"nodes": {}, "ports": {}, "links": []}
    mod._pwcat_r83_wait_node = lambda name, timeout_s=None: (True, 0.0)
    mod._loopback_r79_wait_ports = lambda name, timeout_s=None: (True, 0.0)
    return shim


# keys whose value is a wall-clock/timing observation, not a verdict surface
VOLATILE = {"wall_s", "link_waited_s", "at_s", "waited_s"}


def strip_volatile(obj):
    """Recursively drop VOLATILE keys so two live runs compare on the
    verdict surface only (the r82 [O] convention)."""
    if isinstance(obj, dict):
        return {k: strip_volatile(v) for k, v in obj.items()
                if k not in VOLATILE}
    if isinstance(obj, list):
        return [strip_volatile(v) for v in obj]
    return obj


print("\n== D2: _pwcat_r83_rec_leg end-to-end differential (stubbed spawn) ==")
CTX = {"tmp": "/tmp", "tone": "/tmp/t.wav", "own_sinks": {"nsa", "nsb"},
       "redact": ["nsa", "nsb"]}
REC_KW = dict(props=("stream.capture.sink=true",
                     "media.name=R83RECV bogus.prop=9"),
              sink="nsa", frames=144000, sample_at=1.0)
for tag in ("base", "fold"):
    arm(mods[tag])
cell_b = mods["base"]._pwcat_r83_rec_leg("pr_land", CTX, **REC_KW)
cell_f = mods["fold"]._pwcat_r83_rec_leg("pr_land", CTX, **REC_KW)
check(sorted(set(cell_b) - {"extra_argv"}) == sorted(cell_f),
      "D2 rec_leg cell: the ONLY key delta is extra_argv",
      f"(Δ={sorted(set(cell_b) ^ set(cell_f))})")
for k in sorted(set(cell_b) & set(cell_f)):
    if k in VOLATILE:
        check(isinstance(cell_b[k], (int, float)) and
              isinstance(cell_f[k], (int, float)),
              f"D2 rec_leg cell[{k!r}] present and numeric in both "
              f"(timing value, excluded from equality)",
              f"({cell_b[k]} / {cell_f[k]})")
        continue
    check(cell_b[k] == cell_f[k], f"D2 rec_leg cell[{k!r}] identical",
          f"({str(cell_b[k])[:60]})")
check(cell_b["extra_argv"] == [] and "extra_argv" not in cell_f,
      "D2 DISCLOSED surface delta: base extra_argv=[] leaf removed in "
      "folded", f"(base={cell_b.get('extra_argv')})")
check(cell_b["argv"] == cell_f["argv"],
      "D2 the redacted argv is byte-identical (the folded slot was always "
      "empty)", f"({cell_b['argv'][:70]}…)")
# the removed surface, documented: base still accepts a NON-empty extra
arm(mods["base"])
cell_b2 = mods["base"]._pwcat_r83_rec_leg(
    "pr_land", CTX, extra=("--rate", "44100"), **REC_KW)
check(cell_b2["extra_argv"] == ["--rate", "44100"] and
      cell_b2["argv"] != cell_b["argv"],
      "D2 base `extra` was a real knob (never exercised by any call site)",
      f"(extra_argv={cell_b2['extra_argv']})")
try:
    mods["fold"]._pwcat_r83_rec_leg("pr_land", CTX,
                                    extra=("--rate", "44100"), **REC_KW)
    f2 = "ACCEPTED"
except TypeError:
    f2 = "TypeError"
check(f2 == "TypeError",
      "D2 removed surface documented: folded rec_leg extra= -> TypeError "
      "(the sole call site never passed it)")

print("\n== D3: `ftag` fold — the feed-reap loop differential ==")
lb_cells = {}
for tag, path in (("base", BASE), ("fold", FOLDED)):
    mod = mods[tag]
    shim = arm(mod)
    KILLS.clear()
    cell = mod._pwcat_r83_lb_leg(
        "t1", ["-C", "nsa"], CTX,
        bound_s=0.35, feed_sink="nsa", feed_at=0.05, sample_at=(0.1,))
    lb_cells[tag] = (cell, list(shim.seen), list(KILLS))
cb, seen_b, kills_b = lb_cells["base"]
cf, seen_f, kills_f = lb_cells["fold"]
check(cb["feeds"] == cf["feeds"] and bool(cb["feeds"]),
      "D3 feed reap: identical `feeds` leaf",
      f"({cb['feeds']})")
check(cb["killed_at_bound"] == cf["killed_at_bound"] is True,
      "D3 feed reap: the loopback is killed at bound in both",
      f"({cb['killed_at_bound']}/{cf['killed_at_bound']})")
check(seen_b == seen_f,
      "D3 identical spawn sequence (loopback + feed argv)",
      f"({[a[:3] for a in seen_b]})")
check(kills_b == kills_f and len(kills_b) == 1,
      "D3 identical killpg calls (only the loopback pgid)",
      f"({kills_b})")
check(sorted(cb) == sorted(cf), "D3 lb_leg cell keys identical",
      f"(Δ={sorted(set(cb) ^ set(cf))})")
check(strip_volatile(cb) == strip_volatile(cf),
      "D3 lb_leg cell identical on the verdict surface (timing keys "
      "excluded: wall_s/port_waits/at_s)",
      f"(volatile-only diff: "
      f"{[k for k in sorted(set(cb) & set(cf)) if cb[k] != cf[k]]})")

print("\n== D4: dm_move verdict arms — reachability differential ==")
DM_SLICE = ('            leg = legs["dm_move"]',
            '            if not (leg.get("tap")')
dm_res = {}
for name, path in (("base", BASE), ("fold", FOLDED)):
    results = {}
    for cname, leg in {
        "moved_ok": {"move_rc": 0, "post_move_consumers": ["nsb"]},
        "moved_bad": {"move_rc": 0, "post_move_consumers": ["other"]},
        "moved_rc": {"move_rc": 5, "post_move_consumers": ["nsb"]},
        "skipped": {"move_skipped": "stream absent from sink-inputs"},
    }.items():
        failures = []
        env = {"legs": {"dm_move": dict(
                    leg,
                    pre_move={"node": {"props": {"node.dont-move": True}}},
                    tap={"carries_tone": True})},
               "failures": failures, "nsb": "nsb",
               "_pwcat_r83_check_props": lambda *a, **k: None}
        replay(path, *DM_SLICE, env)
        results[cname] = failures
    dm_res[name] = results
check(dm_res["base"] == dm_res["fold"],
      "D4 dm_move verdicts identical over 4 synthetic legs",
      f"({ {k: len(v) for k, v in dm_res['base'].items()} })")
check(dm_res["base"]["skipped"] == dm_res["fold"]["skipped"] == [],
      "D4 the removed `move never fired` arm is silent in BOTH copies "
      "(unreachable diagnostic)", f"({dm_res['base']['skipped']})")
check(len(dm_res["base"]["moved_bad"]) == 1 and
      len(dm_res["base"]["moved_rc"]) == 1 and
      dm_res["base"]["moved_ok"] == [],
      "D4 the surviving rc / consumer arms still fire and the clean case "
      "stays silent")

print("\n== D5: subsumed-predicate differential (p_empty / n_empty) ==")
CASES = [(cons, cls) for cons in ([], ["a"], ["a", "b"], ["nsa"], ["nsb"],
                                  ["nsb", "x"])
         for cls in ("Audio/Sink", "Audio/Source", None)]
PE_SLICE = ('                if len(cons) != 1 or cons[0] in own_names',
            '                if s.get("input_producers") != [nsa]:')
NE_SLICE = ('                ok = (len(cons) == 1 and cons[0] not in '
            'own_names',
            '                leg["outcome"] = (')
pe, ne = {}, {}
for name, path in (("base", BASE), ("fold", FOLDED)):
    res = []
    for cons, cls in CASES:
        failures = []
        env = {"cons": cons, "own_names": {"nsa", "nsb"},
               "ccls": {cons[0]: cls} if cons else {}, "nsa": "nsa",
               "nsb": "nsb", "failures": failures, "rep": 0,
               "s": {"default_sink_now": None}}
        replay(path, *PE_SLICE, env)
        res.append(bool(failures))
    pe[name] = res
    res = []
    for cons, cls in CASES:
        env = {"cons": cons, "own_names": {"nsa", "nsb"},
               "ccls": {cons[0]: cls} if cons else {}, "nsa": "nsa",
               "nsb": "nsb"}
        res.append(replay(path, *NE_SLICE, env, ret="ok"))
    ne[name] = res
check(pe["base"] == pe["fold"],
      "D5 p_empty condition identical over 18 (consumers, class) cells",
      f"({sum(pe['base'])}/18 fire)")
check(ne["base"] == ne["fold"],
      "D5 n_empty condition identical over 18 cells",
      f"({sum(ne['base'])}/18 ok)")
check(True in ne["base"] and False in ne["base"] and
      True in pe["base"] and False in pe["base"],
      "D5 both surviving conditions are non-degenerate (each arm realized)")

print("\n== D6: `min is None` guard differential (channel stats) ==")
with tempfile.TemporaryDirectory(prefix="r83sprobe-tone-") as tmp:
    wav = Path(tmp) / "tone.wav"
    base._playback_r78_write_tone(wav, 0.6)
    b = base._pwcat_r83_channel_stats(wav, freqs=(440, 660))
    f = fold._pwcat_r83_channel_stats(wav, freqs=(440, 660))
    check(b == f, "D6 channel_stats dicts identical on a real tone",
          f"(chans={len(b.get('channels') or [])})")
    check(all("min" in c for c in b.get("channels") or []),
          "D6 every channel leaf carries `min` (the guard's input "
          "contract)")
    b2 = base._pwcat_r83_channel_stats(Path(tmp) / "nope.wav")
    f2 = fold._pwcat_r83_channel_stats(Path(tmp) / "nope.wav")
    check(b2 == f2 and bool(b2.get("unsupported")),
          "D6 missing-file path identical", f"({b2})")

print("\n== D8: `tapf` init fold — tapped-leg differential (stubbed spawn) ==")
tap_cells = {}
for tag in ("base", "fold"):
    mod = mods[tag]
    arm(mod)
    mod._playback_r78_tap = lambda target, path, frames, name: \
        FakeProc(["pw-record"], live=False)
    mod._capture_tail = lambda txt, path: None
    mod._playback_r78_tone_windows = lambda path: {"windows": []}
    lb = mod._pwcat_r83_lb_leg("t2", ["-C", "nsa"], CTX, bound_s=0.2,
                               tap_target="nsb", tap_seconds=0.2,
                               sample_at=(0.05,))
    pl = mod._pwcat_r83_play_leg("t3", CTX, sink="nsb", tap_seconds=0.2,
                                 bound_s=0.2, sample_at=0.05)
    tap_cells[tag] = (lb, pl)
lb_b, pl_b = tap_cells["base"]
lb_f, pl_f = tap_cells["fold"]
check("tap" in lb_b and "tap" in lb_f,
      "D8 lb_leg: the `tap` leaf is produced by BOTH copies",
      f"(base keys={sorted(lb_b['tap'])})")
check(strip_volatile(lb_b) == strip_volatile(lb_f),
      "D8 lb_leg tapped cell identical on the verdict surface",
      f"({[k for k in sorted(set(lb_b) & set(lb_f)) if lb_b[k] != lb_f[k]]})")
check(sorted(lb_b) == sorted(lb_f), "D8 lb_leg cell keys identical",
      f"(Δ={sorted(set(lb_b) ^ set(lb_f))})")
check(strip_volatile(pl_b) == strip_volatile(pl_f),
      "D8 play_leg tapped cell identical on the verdict surface",
      f"({[k for k in sorted(set(pl_b) & set(pl_f)) if pl_b[k] != pl_f[k]]})")
check(sorted(pl_b) == sorted(pl_f), "D8 play_leg cell keys identical",
      f"(Δ={sorted(set(pl_b) ^ set(pl_f))})")
# the untapped path must stay clean in both (tapf never read)
for tag, mod in (("base", mods["base"]), ("fold", mods["fold"])):
    arm(mod)
    c = mod._pwcat_r83_lb_leg("t4", ["-C", "nsa"], CTX, bound_s=0.15,
                              sample_at=(0.05,))
    check("tap" not in c, f"D8 {tag}: untapped lb_leg produces no tap leaf "
                          f"(tapf never read)", f"({sorted(c)[:6]}…)")

print("\n== D7: AST / literal census re-run on the folded copy ==")


def blk(path):
    """The r83 family block of a copy (header comment .. `def main()`)."""
    txt = Path(path).read_text().splitlines()
    i = next(k for k, l in enumerate(txt) if l.startswith("# r83: the pw-cat"))
    j = next(k for k, l in enumerate(txt) if k > i and l.startswith("def main("))
    return "\n".join(txt[i:j]), i + 1, j


base_blk, bi_b, bj_b = blk(BASE)
fold_blk, bi_f, bj_f = blk(FOLDED)
print(f"  base block lines {bi_b}-{bj_b} ({bj_b - bi_b} lines) / "
      f"folded block lines {bi_f}-{bj_f} ({bj_f - bi_f} lines)")


def loads_in(src, ident):
    return [n.lineno for n in ast.walk(ast.parse(src))
            if isinstance(n, ast.Name) and n.id == ident
            and isinstance(n.ctx, ast.Load)]


check(loads_in(fold_blk, "ftag") == [],
      "folded r83 block: no `ftag` Load anywhere",
      f"(base block: {loads_in(base_blk, 'ftag')})")
check(base_blk.count("(leaf or {})") == 2 and
      fold_blk.count("(leaf or {})") == 0,
      "folded r83 block: no `(leaf or {})` guard left (base had 2)")
check(fold_blk.count("cons[0] == nsb") == 0 and
      fold_blk.count("cons[0] != nsb") == 0 and
      base_blk.count("cons[0] == nsb") == 1 and
      base_blk.count("cons[0] != nsb") == 1,
      "folded: both subsumed nsb predicates gone")
check('if c.get("min") is None' not in fold_blk and
      'if c.get("min") is None' in base_blk,
      "folded: dead `min` guard gone")
check("move never fired" not in fold_blk and
      "move never fired" in base_blk,
      "folded: unreachable dm_move diagnostic gone")
check(fold_blk.count('if leg.get("move_rc") is not None:') == 1,
      "folded: dm_move arm collapsed to the single live guard")
check(base._pwcat_r83_rec_leg.__code__.co_kwonlyargcount ==
      fold._pwcat_r83_rec_leg.__code__.co_kwonlyargcount + 1,
      "folded: rec_leg has one fewer keyword-only parameter",
      f"({base._pwcat_r83_rec_leg.__code__.co_kwonlyargcount} -> "
      f"{fold._pwcat_r83_rec_leg.__code__.co_kwonlyargcount})")
check(len(list(ast.walk(ast.parse(fold_blk)))) <
      len(list(ast.walk(ast.parse(base_blk)))),
      "folded: the block AST has strictly fewer nodes",
      f"({len(list(ast.walk(ast.parse(base_blk))))} -> "
      f"{len(list(ast.walk(ast.parse(fold_blk))))})")
check(len(base_blk.splitlines()) - len(fold_blk.splitlines()) == 8,
      "folded: net -8 lines inside the r83 block",
      f"({len(base_blk.splitlines())} -> {len(fold_blk.splitlines())})")

print()
if fails:
    print(f"RESULT: {len(fails)} FAILURE(S): {fails}")
    sys.exit(1)
print("RESULT: ALL DIFFERENTIAL CHECKS PASS")
