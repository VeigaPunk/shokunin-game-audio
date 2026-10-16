# r98 integration — block-extraction splice into main (a2c6e3b7)

**Method.** Block-extraction, not `git merge` (the r94–r97 playbook): the r98
family block and its dispatch block were extracted from the author worktree
(`audio-shokunin/audio-shokunin-wt-r98`, uncommitted author work) and spliced
into main's `corpus/fixtures/measure_audio.py` — the family block immediately
before `def main():`, the dispatch block immediately before
`if args.probe_pactlmon_r85:` (the author's own anchor, which main shares and
where the r96/r97 dispatches already sit) — then the shared-line wiring edits
were applied at unique anchors. The worktree branch base (`5755be5b`, the r89
foldfix) predates main's r90–r97 landings, so a merge would have dragged stale
r89–r96 block copies back over main.

**Splice verification.**

| item | evidence |
| --- | --- |
| family block | landed blob lines 45906–48256 (2351 lines: banner first, two trailing blank lines last) sha256 `ba7e3b58fbae83df040bef69d4568e9e0eb51526f7d5f8bdcbf71bda46471ada`; WT lines 31091–33441 sha256 `ba7e3b58…` — **byte-identical**, and byte-identical to the author's own block source `corpus/live/r98-author/r98block.py` (116914 B); followed by `def main():` |
| dispatch block | landed blob lines 49096–49126 (31 lines) sha256 `965e7e3d189fca5b730f162cb8a76baba49d0f4bd7427bf7d9f1c0e0a7fd956b`; WT lines 34041–34071 sha256 `965e7e3d…` — **byte-identical**; preceded by `wppol_settings_r97_entry()`, followed by `    if args.probe_pactlmon_r85:` |
| argparse row | `parser.add_argument("--probe-pwstream-r98", action="store_true")` (byte-verbatim from the WT, sha256 `5b2c034f820465c8dfbbf6b3f8e2c3ea09ecb6831a1bed82f16d1d1d438a45ba`) inserted after `--probe-wppol-r97` (before `--probe-sox-r94`) — main's newest r9x row by round |
| mutex-sum line | `args.probe_pwstream_r98` prepended at the list head: `if sum([args.probe_pwstream_r98, args.probe_wppol_r97, …]) > 1:` — 141 tokens (was 140) |
| `mode` ternary | `mode = "probe-pwstream-r98" if args.probe_pwstream_r98 else …` (landed blob line 49777) — r98 first |
| `suffix` ternary | `suffix = "-pwstream-r98" if args.probe_pwstream_r98 else …` (landed blob line 49797) — r98 first |
| symbol census | 52 module-level names defined by the family block, **0 collisions** (each defined exactly 1× in the landed file); the six dispatch keys appear 4× each (2 in the family: the def name and `_pwstream_r98_entry_head("<key>")`; 2 in the dispatch) |
| py_compile | `python3 -m py_compile corpus/fixtures/measure_audio.py` rc=0 — both on the landed blob and on the working-tree file |
| conflict markers | none — `^<<<<<<< `, `^>>>>>>> `, `^=======$` all 0 hits |
| diff stat | `corpus/fixtures/measure_audio.py \| 2386 +…, 3 -…` in 6 hunks (2351-line family block, 1-line argparse row, 1-line mutex, 31-line dispatch, `mode`, `suffix`) |
| author report | `reports/round-98/r98-author.md` sha256 `2dc27a1ae3661ec046683ae6233cb2c3ffad4b4643b8ed34ce3b7c55cb00923a` — verbatim both sides |
| C fixture | `corpus/fixtures/r98stream.c` sha256 `9f840a6b8b23196124270d96532b3b35b2b868d089aef4eb58ad2d6b0950d323` — verbatim both sides; equals the author's recorded fixture sha (`corpus/live/r98-author/fixture-sha256.txt`) |
| landed fixture | sha256 `b0678fb1e29c5ee829dfd13f8975dff1d5ec26502a7102be0d6b44c12aea4fbe` (49807 lines) — **≠** the WT file's `c9d7627b25179616bee489c1093a525d25dd1812c96a6b969bb2eff01607d768` (expected: the landed file carries main's r90–r97 blocks on top) |

**Behavioral checks (narrow).**

- `python3 corpus/fixtures/measure_audio.py --help` → rc 0; usage lists
  `[--probe-pwstream-r98]` (after `[--probe-wppol-r97]`).
- `--probe-pwstream-r98` paired with `--probe-wppol-r97` → rc 2; with
  `--probe-wpstate-r90` → rc 2; with `--probe-pactlmon-r85` → rc 2; with
  `--probe-failing` → rc 2 — all `measure_audio.py: error: choose one probe
  mode`. The r98 flag participates in the probe mutex alongside the newest
  (r97) and the legacy rows.
- `gcc -fsyntax-only $(pkg-config --cflags libpipewire-0.3)
  corpus/fixtures/r98stream.c` → rc 0.
- Every check exits inside `parse_args`; no run dir, receipt, or lock file was
  written by any check (`corpus/live/measure_audio-pwstream-r98.lock` absent in
  main). The r98 family needs a private PipeWire core + private WirePlumber
  pair, so no host-side probe run was made; the author's two frozen-byte
  batteries are the evidence of record (`corpus/live/runs/*-pwstream-r98/`,
  untracked, not carried).

**Disclosures.**

1. **Mutex token — added by this integration.** The author's diff has only the
   two wiring deletions (`mode`, `suffix`): their worktree base (`5755be5b`)
   predates main's r90 mutex list, so `--probe-pwstream-r98` was not armed
   there. This integration prepends `args.probe_pwstream_r98` at the list head
   (the r90 landing's placement; r96 appended at the tail) — the third
   replaced wiring line, and one extra insertion.
2. **Numstat label.** The measured landed diff is `+2386/−3` in 6 hunks. The
   assigned commit label reads `+2385/−3`: `+2385` is the author's insertion
   count (their worktree diff is `+2385/−2`); the mutex token this assignment
   mandated adds the third deletion **and** one insertion, so the landed
   insertion count is 2386 (the r90 precedent: its label `+2183/−3` carries the
   landed count after its integrate-side mutex guard). The assigned message
   string was committed verbatim; the exact measured stat is recorded here.
3. **Argparse placement.** The author's own row went after `--probe-btwit-r88`
   (the end of *their* r9x subgroup, since their base predates r90–r96); main's
   newest r9x row by round is `--probe-wppol-r97`, so the row was inserted
   there (before `--probe-sox-r94`) — the same rule the r97 landing applied to
   the r96 row.
4. **Concurrent r90-foldfix lane in main's tree — preserved, untouched.** While
   this integration was in flight, a sibling r90-foldfix lane had already
   applied its uncommitted FF1–FF6 changes to main's
   `corpus/fixtures/measure_audio.py` (`+659/−194`, last write 10:19:11Z) and
   `reports/round-90/r90-author.md` (`+109/−16`); its two verification
   batteries in `/home/vgpnk/Projects/shokunin/r90f-tree` were green
   (`failures: {}`, run dirs `…101922340578Z-wpstate-r90` and
   `…102137287133Z-wpstate-r90`) and it had not committed by the time this
   landing was sealed. To honour both, the landed commit was built from
   `a2c6e3b7`'s blob + the r98 delta (the splice was rehearsed and verified
   against both byte-states; the two change sets are disjoint — the foldfix
   touches the r90 family/dispatch region, not this landing's six hunks), the
   r98 delta was also applied to the working-tree file so the tree carries r98
   on top of the foldfix, and the sibling's changes were left uncommitted and
   unmodified. The working tree's fixture sha
   (`4d0a1fe66eff45d3e50d6b2d3969f3b63e8685da8850bb6139f1f61920b581d2`, 50272
   lines, family block at tree lines 46322–48672) therefore differs from the
   landed blob's `b0678fb1…` by exactly the sibling's hunks; a verifier
   comparing tree vs commit will see that delta — it is the sibling's landing,
   not this one.

**Not touched.** No `corpus/live/**` receipt, run dir, or lock was added,
modified, or committed; the `__pycache__` churn from `py_compile` was reverted
(`git checkout -- corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`)
before staging; the author worktree was not committed and was not modified
(fixture sha `c9d7627b…` and status unchanged across the integration); main's
r89–r97 blocks are untouched.

**Carried files.** `corpus/fixtures/r98stream.c` (verbatim copy from the
worktree, 1005 lines) + `reports/round-98/r98-author.md` (verbatim copy) +
this note. Commit: `r98 author: pw-stream core/run/route/cap/sbx lattice
(6 entries/67 legs, +2385/-3)`.
