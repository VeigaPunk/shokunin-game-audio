# r96 integration — block-extraction splice into main (97ed1b1c)

**Method.** Block-extraction, not `git merge` (the r94/r95 playbook, the r90
worked example): the r96 family block and its dispatch block were extracted
from the author worktree
(`/home/vgpnk/Projects/shokunin/audio-shokunin/audio-shokunin-wt-r96`,
uncommitted author work) and spliced into main's
`corpus/fixtures/measure_audio.py` — the family block immediately before
`def main():`, the dispatch block immediately before
`if args.probe_pactlmon_r85:` (the author's own anchor, which main shares) —
then the four shared-line wiring edits were applied at unique anchors. The
worktree branch base (`5755be5b`, the r89 foldfix) predates main's r90–r95
landings, so a merge would have dragged stale r89–r95 block copies back over
main.

**Splice verification.**

| item | evidence |
| --- | --- |
| family block | merged lines 41471–43787 (2317 lines, one leading blank line then the banner — the author's own inserted span) sha256 `be60f1bae6db9859839ebe2f3daf6938af3bc03f2d7595bdf5c97ac82968b97d`; WT lines 31091–33407 sha256 `be60f1ba…` — **byte-identical** |
| dispatch block | merged lines 44554–44590 (37 lines) sha256 `75bc7fdd9f6b3d983db6816b6ea8a925c6cdd602e65e1645db0665639c467d65`; WT lines 34007–34042 sha256 `75bc7fdd…` — **byte-identical** |
| argparse row | `parser.add_argument("--probe-pulsecli-r96", action="store_true")` (byte-verbatim from the WT) inserted at merged line 43922, after the r92 row |
| mutex-sum line | `args.probe_pulsecli_r96` appended at the list end: `… args.probe_filterchain_r92, args.probe_pulsecli_r96]) > 1:` — 139 tokens (was 138) |
| `mode` ternary | `mode = "probe-pulsecli-r96" if args.probe_pulsecli_r96 else "probe-filterchain-r92" if …` (merged line 45241) — r96 first |
| `suffix` ternary | `suffix = "-pulsecli-r96" if args.probe_pulsecli_r96 else "-filterchain-r92" if …` (merged line 45261) — r96 first |
| symbol census | 74 module-level names defined by the block, **0 collisions** (each defined 1× inside the block, 0× outside); the five dispatch keys `pulsecli_avail_r96_probe` / `pulsecli_target_r96_probe` / `pulsecli_attr_r96_probe` / `pulsecli_props_r96_probe` / `pulsecli_cork_r96_probe` **1× each** |
| py_compile | `python3 -m py_compile corpus/fixtures/measure_audio.py` rc=0 |
| conflict markers | none — `^<<<<<<< `, `^>>>>>>> `, `^=======$` all 0 hits |
| fixture sha | `corpus/fixtures/pulse_r96_probe.c` (383 lines) sha256 `fe2c168352144cd66e6977debd84c3ebee80b9ace80c26c4f0bc37d00a8fc64c` — **verbatim** copy from the WT; `gcc -fsyntax-only -Wall $(pkg-config --cflags libpulse)` rc=0 (libpulse 1.x headers present on this host) |
| author report | `reports/round-96/r96-author.md` sha256 `6d7b6880f1c46e311f79743c930e18d937dbf0791206ce2069cdc4edf96c65e2` — verbatim both sides |
| diff stat | `corpus/fixtures/measure_audio.py \| 2358 +…, 3 -…` in 6 hunks (2317-line family block, 37-line dispatch, 1-line argparse row, 3 replaced wiring lines) |
| merged sha | `97ed1b1c586d2d5446f2ae85d1ab158e43b0f7d71edf430c2c5f045ed5299efc` — **≠** the WT file's `b545283e6355d77346e11e0883d9d79792180f0732f2a5851623dbfb353786c8` (expected: the merged file differs from the worktree file) |

**Behavioral checks (narrow).**

- `python3 corpus/fixtures/measure_audio.py --help` → rc 0; usage lists
  `[--probe-pulsecli-r96]` and the option description.
- `python3 corpus/fixtures/measure_audio.py --probe-pulsecli-r96
  --probe-filterchain-r92` → rc 2, `measure_audio.py: error: choose one probe
  mode` — the r96 flag participates in the probe mutex alongside the r92 flag.
- The C instrument fixture compiles clean (`-fsyntax-only`, `-Wall`, libpulse
  cflags) — the r96 arms that need an own-libpulse client are not blocked by a
  bad fixture on this host.
- Both python exits happen inside `parse_args`; no run dir, receipt, or lock
  file was written by either check.

**Disclosures (two placement choices, both non-semantic).**

1. The author's argparse row was inserted immediately after
   `--probe-pwprof-r89` in the worktree — the newest r9x row of *their* base.
   Main's r9x argparse group is round-ordered (`--probe-pwprof-r89`,
   `--probe-wpstate-r90`, `--probe-gstfrz-r91`, `--probe-filterchain-r92`,
   `--probe-sox-r94`, `--probe-jack-r95`), so the row was inserted after the
   r92 row (the newest row with a smaller round number), keeping the group
   round-ordered as each landing appends. The r92 anchor row is itself two
   physical lines; the insertion point is computed past its closing paren.
2. The mutex token was appended at the list end — the author's own placement
   in their worktree; the r90 landing prepended instead. Either position arms
   the same mutual exclusion. The r96 author diff **did** arm the mutex list,
   so no token beyond the author's bytes was added.
3. The r96 family block's first line is a blank line (the author's inserted
   span starts one line above the banner; their base carried two blank lines
   before `def main():`). The full span was spliced verbatim, so the merged
   file carries the author's blank line as part of the block — verified by
   the byte-identical span sha above.

**Not touched.** No `corpus/live/**` receipt, run dir, or lock was added,
modified, or committed; the `__pycache__` churn from `py_compile` was reverted
(`git checkout -- corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`)
before staging; the worktree was not committed and was not modified; main's
r89–r92 blocks are untouched.

**Carried files.** `reports/round-96/r96-author.md` (verbatim copy from the
worktree) + this note + `corpus/fixtures/pulse_r96_probe.c` (the author's
instrument fixture). Commit: the commit that carries this file
(`r96 author: pulsecli PulseAudio-native client API (5 entries/178 legs, +2358/-3)`).
