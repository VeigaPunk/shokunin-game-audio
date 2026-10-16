# r91 integration — block-extraction splice into main (7f9ee31b)

**Method.** Block-extraction, not `git merge` (the r94/r95 playbook, the r90
worked example): the r91 family block and its dispatch block were extracted
from the author worktree
(`/home/vgpnk/Projects/shokunin/audio-shokunin-wt-r91`, uncommitted author
work) and spliced into main's `corpus/fixtures/measure_audio.py` — the family
block immediately before `def main():`, the dispatch block immediately before
`if args.probe_pactlmon_r85:` (the author's own anchor, which main shares) —
then the four shared-line wiring edits were applied at unique anchors. The
worktree branch base (`5a632a4f`, the r87+r88 fold) predates main's
r89–r95 and r90 landings, so a merge would have dragged stale r89–r95 block
copies back over main.

**Splice verification.**

| item | evidence |
| --- | --- |
| family block | merged lines 37712–39175 (1464 lines) sha256 `6fe734a8ff7cd530b8790c4ada4cec6fae58216955ef3cbe7d5bc6fc0a52570d`; WT lines 30982–32445 sha256 `6fe734a8…` — **byte-identical** |
| dispatch block | merged lines 39878–39910 (33 lines) sha256 `91bb18f8decae5beb30232ead31c03e3be917c59200705530419dde747f2e562`; WT lines 33045–33076 sha256 `91bb18f8…` — **byte-identical** |
| argparse row | `parser.add_argument("--probe-gstfrz-r91", action="store_true")` inserted at merged line 39307, after `--probe-wpstate-r90` |
| mutex-sum line | `args.probe_gstfrz_r91` appended at the list end: `… args.probe_jack_r95, args.probe_gstfrz_r91]) > 1:` — 137 tokens (was 136) |
| `mode` ternary | `mode = "probe-gstfrz-r91" if args.probe_gstfrz_r91 else "probe-wpstate-r90" if …` (merged line 40561) — r91 first |
| `suffix` ternary | `suffix = "-gstfrz-r91" if args.probe_gstfrz_r91 else "-wpstate-r90" if …` (merged line 40581) — r91 first |
| symbol census | 51 module-level names defined by the block, **0 collisions** (each defined 1× inside the block, 0× outside); the five dispatch keys `gstfrz_prop_r91_probe` / `gstfrz_clock_r91_probe` / `gstfrz_resume_r91_probe` / `gstfrz_srcloss_r91_probe` / `gstfrz_connect_r91_probe` **1× each** |
| py_compile | `python3 -m py_compile corpus/fixtures/measure_audio.py` rc=0 |
| conflict markers | none — `^<<<<<<< `, `^>>>>>>> `, `^=======$` all 0 hits |
| fixture sha | `corpus/fixtures/gstfreeze_r91_resume.py` (155 lines) sha256 `066d6fff7ba74ef40d11b2f3a71ae336d4ee21c6d73d0975d6dc94fe714b1dc2` — **verbatim** copy from the WT; `compile()` rc 0 |
| author report | `reports/round-91/r91-author.md` sha256 `de9e9ecd5bf8914d045303df54a66533fdc10315bf8dc57877c63700d8a30bd5` — verbatim both sides |
| diff stat | `corpus/fixtures/measure_audio.py \| 1501 +…, 3 -…` in 6 hunks (1464-line family block, 33-line dispatch, 1-line argparse row, 3 replaced wiring lines) |
| merged sha | `7f9ee31b3b7f9269333387868a036a54beb38d633abac0a69cf839c434943cb3` — **≠** the WT file's `b0ab6fda8b35eafa76b753ce8e31687b14ec278396fbdd00c8efc2b432124af0` (expected: the merged file differs from the worktree file) |

**Behavioral checks (narrow).**

- `python3 corpus/fixtures/measure_audio.py --help` → rc 0; usage lists
  `[--probe-gstfrz-r91]` and the option description.
- `python3 corpus/fixtures/measure_audio.py --probe-gstfrz-r91 --probe-sox-r94`
  → rc 2, `measure_audio.py: error: choose one probe mode` — the r91 flag
  participates in the probe mutex.
- Both exits happen inside `parse_args`; no run dir, receipt, or lock file was
  written by either check.

**Disclosures (two placement choices, both non-semantic).**

1. The author's argparse row was inserted immediately after
   `--probe-pwprof-r89` in the worktree — the newest r9x row of *their* base.
   Main's r9x argparse group is round-ordered (`--probe-pwprof-r89`,
   `--probe-wpstate-r90`, `--probe-sox-r94`, `--probe-jack-r95`), so the row
   was inserted after `--probe-wpstate-r90` (the newest row with a smaller
   round number), keeping the group round-ordered as each landing appends.
2. The mutex token was appended at the list end — the author's own placement
   in their worktree (`… args.probe_pwprof_r89, args.probe_gstfrz_r91])`); the
   r90 landing prepended instead. Either position arms the same mutual
   exclusion. The r91 author diff **did** arm the mutex list (unlike r90's),
   so no token beyond the author's bytes was added.

**Not touched.** No `corpus/live/**` receipt, run dir, or lock was added,
modified, or committed; the `__pycache__` churn from `py_compile` was reverted
(`git checkout -- corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`)
before staging; the worktree was not committed and was not modified; main's
r89–r95 and r90 blocks are untouched.

**Carried files.** `reports/round-91/r91-author.md` (verbatim copy from the
worktree) + this note + `corpus/fixtures/gstfreeze_r91_resume.py` (the
author's fixture). Commit: the commit that carries this file
(`r91 author: gst capture-freeze mechanism lattice (5 entries/15 legs, +1501/-3)`).
