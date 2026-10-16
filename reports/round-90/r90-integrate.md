# r90 integration — block-extraction splice into main (a969ea73)

**Method.** Block-extraction, not `git merge` (the r94/r95 playbook): the r90
family block was extracted from the author worktree
(`/home/vgpnk/Projects/shokunin/audio-shokunin-wt-r90`, uncommitted author
work) and spliced into main's `corpus/fixtures/measure_audio.py` before
`def main():`, then the three shared-line wiring edits were applied by hand
at unique anchors. The worktree branch base (`5a632a4f`, the r87+r88 fold)
predates main's r91–r95 landings, so a merge would have dragged stale r89–r95
block copies back over main.

**Splice verification.**

| item | evidence |
| --- | --- |
| family block | merged lines 35553–37711 (2159 lines) sha256 `85f10b6619f9c45bb3b535a8f389dabfae0fcd750c3d67bf3115a156774d7eaa`; WT lines 30982–33140 sha256 `85f10b66…` — **byte-identical** (same marker-delimited span both sides) |
| dispatch block | 20 lines spliced immediately before `if args.probe_pwprof_r89:` (the author's anchor), sha256 `797be5b6dbedcaaa54775b2a88158bffcd2f1d67a8d4a1303ef607d248792c80` |
| argparse row | `parser.add_argument("--probe-wpstate-r90", action="store_true")` inserted after `--probe-pwprof-r89` |
| mutex-sum line | `args.probe_wpstate_r90` prepended: `if sum([args.probe_wpstate_r90, args.probe_sox_r94, …]) > 1:` — 136 tokens (was 135) |
| `mode` ternary | `mode = "probe-wpstate-r90" if args.probe_wpstate_r90 else "probe-sox-r94" if …` — r90 first |
| `suffix` ternary | `suffix = "-wpstate-r90" if args.probe_wpstate_r90 else "-sox-r94" if …` — r90 first |
| symbol census | `wpstate_store_r90_probe` / `wpstate_pmod_r90_probe` / `wplink_r90_entry` / `wpformat_r90_entry` defined **1× each**; the four dispatch rows **1× each**; `_r90_family_lock = _wpstate_r90_family_lock()   # held to exit` **1×**; prefix counts merged/WT = `wpstate` 315/314 (+1 = the mutex row), `wplink` 6/6, `wpformat` 7/7 |
| py_compile | `python3 -m py_compile corpus/fixtures/measure_audio.py` rc=0 |
| conflict markers | none — `^<<<<<<< `, `^>>>>>>> `, `^=======$` all 0 hits (the `# ====…` lines are decorative rules) |
| AST name check | 372 names loaded by the spliced block, **0 unresolved** at module level (no r91–r95 symbol loss) |
| fixture sha | merged `d3119c5d88228349b54996e23978cf726d59bfc615739838177a5a5e14551154` — **≠** the two greens' declared `d9a07b14af4e605353b2b07e6fccff41ff0eb083c1d430fb58e7192b1fb276eb` (expected: the merged file differs from the worktree file) |
| diff stat | `corpus/fixtures/measure_audio.py | 2183 +…, 3 -…` in 4 hunks (2159-line block, 20-line dispatch, 1-line argparse row, 3 replaced wiring lines) |

**Behavioral checks (narrow).**

- `python3 corpus/fixtures/measure_audio.py --help` → rc 0; usage lists
  `[--probe-wpstate-r90]` and the option description.
- `python3 corpus/fixtures/measure_audio.py --probe-wpstate-r90 --probe-sox-r94`
  → rc 2, `measure_audio.py: error: choose one probe mode` — the r90 flag now
  participates in the probe mutex (in the author's worktree bytes it did not).
- Both exits happen inside `parse_args`; no run dir, receipt, or lock file was
  written by either check.

**Deliberate 1-line deviation from the author's worktree.** The author's diff
deletes only 2 lines (`mode`, `suffix`) and never adds `args.probe_wpstate_r90`
to the `if sum([…]) > 1` guard. The canonical landing shape for every prior
r8x/r9x author diff is exactly 3 deleted lines — `mutex-sum`,
`mode-ternary`, `suffix-ternary` (`corpus/live/r89-critic/custody.json`
`deleted_kinds`, same shape in the r83–r85 reports) — and the r90 assignment
named the probe mutex list as one of the three shared-line edits. The merged
landing therefore carries it; the author's worktree omission is recorded here
and in `r90-author.md` (which declares `+2182/−2`; the merged landing is
`+2183/−3`). Behavior of the r90 family itself is unchanged — the added token
only arms mutual exclusion.

**Not touched.** No `corpus/live/**` receipt, run dir, or lock was added,
modified, or committed; the `__pycache__` churn from `py_compile` was reverted
(`git checkout -- corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`)
before staging; the worktree was not committed; main's r91–r95 blocks are
untouched.

**Carried files.** `reports/round-90/r90-author.md` (verbatim copy from the
worktree) + this note. Commit: the commit that carries this file
(`r90 author: wpstate/pw-link/wp-format lattice (4 entries/60 legs, +2183/-3)`).
