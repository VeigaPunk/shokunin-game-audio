# r97 integration — block-extraction splice into main (7358f13b)

**Method.** Block-extraction, not `git merge` (the r94/r95/r96 playbook): the
r97 family block and its dispatch block were extracted from the author
worktree (`audio-shokunin/audio-shokunin-wt-r97`, uncommitted author work) and
spliced into main's `corpus/fixtures/measure_audio.py` — the family block
immediately before `def main():`, the dispatch block immediately before
`if args.probe_pactlmon_r85:` (the author's own anchor, which main shares and
where the r96 dispatch already sits) — then the three shared-line wiring edits
were applied at unique anchors. The worktree branch base (`5755be5b`, the r89
foldfix) predates main's r90–r96 landings, so a merge would have dragged stale
r89–r96 block copies back over main.

**Splice verification.**

| item | evidence |
| --- | --- |
| family block | merged lines 43788–45905 (2118 lines: banner first, two trailing blank lines last) sha256 `f58f0290fff2f76c5c343db643585d3b9bb32912dee99aa7e129f262cc8243f5`; WT lines 31091–33208 sha256 `f58f0290…` — **byte-identical**; followed by `def main():` |
| dispatch block | merged lines 46710–46743 (34 lines) sha256 `68de4d267dded2a4ad2c5ae5f5a7a59e823d63d594bdcd8a8a48317644dea3b9`; WT lines 33808–33841 sha256 `68de4d26…` — **byte-identical**; preceded by `            _pulsecli_r96_cork_entry()`, followed by `    if args.probe_pactlmon_r85:` |
| argparse row | `parser.add_argument("--probe-wppol-r97", action="store_true")` (byte-verbatim from the WT) inserted at merged line 46041, immediately after the r96 row |
| mutex-sum line | `args.probe_wppol_r97` prepended at the list head: `if sum([args.probe_wppol_r97, args.probe_wpstate_r90, … args.probe_pulsecli_r96]) > 1:` — 140 tokens (was 139) |
| `mode` ternary | `mode = "probe-wppol-r97" if args.probe_wppol_r97 else "probe-pulsecli-r96" if …` (merged line 47394) — r97 first |
| `suffix` ternary | `suffix = "-wppol-r97" if args.probe_wppol_r97 else "-pulsecli-r96" if …` (merged line 47414) — r97 first |
| symbol census | 77 module-level names defined by the family block, **0 collisions** (each defined exactly 1× in the merged file); the five dispatch keys `wppol_arming_r97_probe` / `wppol_defaults_r97_probe` / `wppol_linking_r97_probe` / `wppol_wpexec_r97_probe` / `wppol_settings_r97_probe` appear 2× each — the family's `_wppol_r97_entry_head("<key>")` self-name and the dispatch key (the author's own bytes) |
| py_compile | `python3 -m py_compile corpus/fixtures/measure_audio.py` rc=0 |
| conflict markers | none — `^<<<<<<< `, `^>>>>>>> `, `^=======$` all 0 hits |
| diff stat | `corpus/fixtures/measure_audio.py \| 2156 +…, 3 -…` in 6 hunks (2118-line family block, 34-line dispatch, 1-line argparse row, 3 replaced wiring lines) — the author's own `git diff --numstat` shape |
| author report | `reports/round-97/r97-author.md` sha256 `f912538c15ea1be96d8ef775d77a4282268158115c82801c14973b2fcac80466` — verbatim both sides |
| merged sha | `7a070fa817c4de6f4ae5eb5be38e7cfc2cdbb18cad605ee52427afcf0a6ca2bc` (47424 lines) — **≠** the WT file's `f0eb6c509ecc20bff8a4652ec09e2ddf6607153fc01fbe150e679aee54b7d50e` (expected: the merged file carries main's r90–r96 blocks on top) |

**Behavioral checks (narrow).**

- `python3 corpus/fixtures/measure_audio.py --help` → rc 0; usage lists
  `[--probe-wppol-r97]` (after `[--probe-pulsecli-r96]`).
- `--probe-wppol-r97` paired with `--probe-pulsecli-r96` → rc 2;
  with `--probe-pactlmon-r85` → rc 2; with `--probe-filterchain-r92` → rc 2;
  with `--probe-failing` → rc 2 — all `measure_audio.py: error: choose one
  probe mode`. The r97 flag participates in the probe mutex alongside both the
  newest (r96) and the legacy rows.
- Every check exits inside `parse_args`; no run dir, receipt, or lock file was
  written by any check (`corpus/live/measure_audio-wppol-r97.lock` absent in
  main). The r97 family needs no shared daemon — it builds a **private**
  PipeWire core + private WirePlumber pair under its own runtime dir — so no
  host-side probe run was made; the author's two frozen-byte batteries are the
  evidence of record (`corpus/live/runs/…-wppol-r97/`, untracked, not carried).

**Disclosures (three placement choices, all non-semantic).**

1. The author's argparse row was inserted immediately after `--probe-btwit-r88`
   in the worktree — the end of *their* r9x subgroup, since their base predates
   r90–r96. Main's r9x argparse group carries the later landings
   (`--probe-pwprof-r89`, `--probe-wpstate-r90`, `--probe-gstfrz-r91`,
   `--probe-filterchain-r92`, `--probe-pulsecli-r96`, `--probe-sox-r94`,
   `--probe-jack-r95`), so the row was inserted after the r96 row — the newest
   r9x row in main, the same rule the r96 landing applied to the r92 row.
2. The mutex token was **prepended** at the list head — the author's own
   placement in their worktree. The r96 landing appended at the tail, the r90
   landing prepended; either position arms the same mutual exclusion, and the
   author diff did arm the list, so no token beyond the author's bytes was
   added.
3. Blank-line context: the author's base carried two blank lines before
   `def main():` and the family block begins at the banner, so their file has
   two blank lines between `return entry` and the banner. Main carried one.
   The block span (banner → two trailing blank lines) was spliced verbatim, so
   the merged file has **one** blank line before the banner and the author's
   two blank lines before `def main():` — verified by the byte-identical span
   sha above; no separator byte was fabricated.

**Not touched.** No `corpus/live/**` receipt, run dir, or lock was added,
modified, or committed; the `__pycache__` churn from `py_compile` was reverted
(`git checkout -- corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`)
before staging; the worktree was not committed and was not modified (fixture
sha `f0eb6c50…` and status both unchanged across the integration); main's
r89–r96 blocks are untouched. No new fixture file accompanies this landing —
unlike r96's C instrument, the r97 harness writes its confs and Lua into
private scratch dirs at runtime.

**Carried files.** `reports/round-97/r97-author.md` (verbatim copy from the
worktree) + this note. Commit: `r97 author: wppol WirePlumber policy lattice
(5 entries/69 legs, +2156/-3)`.
