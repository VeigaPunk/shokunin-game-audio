# r92 integration — block-extraction splice into main (4e5fe3e6)

**Method.** Block-extraction, not `git merge` (the r94/r95 playbook, the r90
worked example): the r92 family block and its dispatch block were extracted
from the author worktree
(`/home/vgpnk/Projects/shokunin/audio-shokunin-wt-r92`, uncommitted author
work) and spliced into main's `corpus/fixtures/measure_audio.py` — the family
block immediately before `def main():`, the dispatch block immediately before
`if args.probe_pactlmon_r85:` (the author's own anchor, which main shares) —
then the four shared-line wiring edits were applied at unique anchors. The
worktree branch base (`5a632a4f`, the r87+r88 fold) predates main's r89–r95
and r90/r91 landings, so a merge would have dragged stale r89–r95 block
copies back over main.

**Splice verification.**

| item | evidence |
| --- | --- |
| family block | merged lines 39176–41470 (2295 lines) sha256 `a1b418be71203602eb012084a4e9b12080265cbedd0264babfd6f41b0f992291`; WT lines 30982–33276 sha256 `a1b418be…` — **byte-identical** |
| dispatch block | merged lines 42208–42235 (28 lines) sha256 `802f23d1ef75cd2b8514704d0d70ded4f56b4ad3c89f5c1dc2202f9f0f67ae11`; WT lines 33877–33903 sha256 `802f23d1…` — **byte-identical** |
| argparse row | `parser.add_argument("--probe-filterchain-r92",` / `action="store_true")` (2 lines, byte-verbatim from the WT) inserted at merged lines 41603–41604, after `--probe-gstfrz-r91` |
| mutex-sum line | `args.probe_filterchain_r92` appended at the list end: `… args.probe_gstfrz_r91, args.probe_filterchain_r92]) > 1:` — 138 tokens (was 137) |
| `mode` ternary | `mode = "probe-filterchain-r92" if args.probe_filterchain_r92 else "probe-gstfrz-r91" if …` (merged line 42886) — r92 first |
| `suffix` ternary | `suffix = "-filterchain-r92" if args.probe_filterchain_r92 else "-gstfrz-r91" if …` (merged line 42906) — r92 first |
| symbol census | 78 module-level names defined by the block, **0 collisions** (each defined 1× inside the block, 0× outside); the four dispatch keys `filterchain_arm_r92_probe` / `filterchain_dsp_r92_probe` / `filterchain_ir_r92_probe` / `filterchain_wpx_r92_probe` **1× each** |
| py_compile | `python3 -m py_compile corpus/fixtures/measure_audio.py` rc=0 |
| conflict markers | none — `^<<<<<<< `, `^>>>>>>> `, `^=======$` all 0 hits |
| fixture | none (the r92 landing carries no fixture file) |
| author report | `reports/round-92/r92-author.md` sha256 `aba104aa0b8e291894c638e8c16776f07724c9b7fdf41079a6603fdc5726b8b5` — verbatim both sides |
| diff stat | `corpus/fixtures/measure_audio.py \| 2328 +…, 3 -…` in 6 hunks (2295-line family block, 28-line dispatch, 2-line argparse row, 3 replaced wiring lines) |
| merged sha | `4e5fe3e673d8cb586523f3d5462e915c3db255ce4ba0013c5f7157756096ca90` — **≠** the WT file's `5b17ad3dad4381905228c0789f0ef8d14b9366bf2cdbad38986d97e80fecd20c` (expected: the merged file differs from the worktree file). The WT sha matches the sha the author report itself declares, so the extracted source is the authored byte image. |

**Behavioral checks (narrow).**

- `python3 corpus/fixtures/measure_audio.py --help` → rc 0; usage lists
  `[--probe-filterchain-r92]` and the option description.
- `python3 corpus/fixtures/measure_audio.py --probe-filterchain-r92
  --probe-gstfrz-r91` → rc 2, `measure_audio.py: error: choose one probe mode`
  — the r92 flag participates in the probe mutex alongside the r91 flag.
- Both exits happen inside `parse_args`; no run dir, receipt, or lock file was
  written by either check.

**Disclosures (two placement choices, both non-semantic).**

1. The author's argparse row was inserted immediately after
   `--probe-pwprof-r89` in the worktree — the newest r9x row of *their* base.
   Main's r9x argparse group is round-ordered (`--probe-pwprof-r89`,
   `--probe-wpstate-r90`, `--probe-gstfrz-r91`, `--probe-sox-r94`,
   `--probe-jack-r95`), so the row was inserted after `--probe-gstfrz-r91`
   (the newest row with a smaller round number), keeping the group
   round-ordered as each landing appends.
2. The mutex token was appended at the list end — the author's own placement
   in their worktree; the r90 landing prepended instead. Either position arms
   the same mutual exclusion. The r92 author diff **did** arm the mutex list,
   so no token beyond the author's bytes was added.

**Not touched.** No `corpus/live/**` receipt, run dir, or lock was added,
modified, or committed; the `__pycache__` churn from `py_compile` was reverted
(`git checkout -- corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`)
before staging; the worktree was not committed and was not modified; main's
r89–r91 blocks are untouched.

**Carried files.** `reports/round-92/r92-author.md` (verbatim copy from the
worktree) + this note. Commit: the commit that carries this file
(`r92 author: filter-chain DSP lattice (4 entries/80 legs, +2328/-3)`).
