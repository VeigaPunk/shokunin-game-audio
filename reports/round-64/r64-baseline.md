# R64 baseline — frozen before-state replay of the 86-command ledger

host: devin. Seat: baseline (scout). Frozen state = `git archive` of canonical
HEAD **`37d4c57`** ("audio r63 adjudication: ADMIT — …"), the HEAD at dispatch
and at archive time. Extraction:
`corpus/live/r64-baseline/tree/` (119 MB, incl. all 2,968 tracked run receipts).

Frozen-commit proof (HEAD moved during the window — needed disambiguation):
extracted tree lacks `corpus/live/r64-reviewer/` (added by `5cc0eb0`) and its
`corpus/knowledge/2026-10-13-sox-act-autodetect-predicate.md` sha256
`c7a4e172…` equals `git show 37d4c57:` (5cc0eb0 version is `4d7b3dbf…`).
In-tree `r63-author/ledger-r63.tsv` sha256 `602c29fe…` = committed bytes.

Toolchain: `SoX_ng v14.8.0.1`, `ffmpeg/ffprobe n9.0.1`, `python3 3.14.7` +
`numpy 2.5.3` (`toolchain.txt`) — matches the r63 verifier's declared set.

## Standalone-capability finding

`measure_audio.py` anchors `ROOT = Path(__file__).resolve().parents[1]`
(= `tree/corpus`): every fixture input, probe wav, and receipt write resolves
inside the frozen tree — **the frozen copy runs fully standalone**, no in-place
replay needed. The runner has **no `--runs` flag** (argparse carries probe
flags only); receipts land at `ROOT/live/runs/<stamp>-<suffix>/`, which inside
the frozen tree is self-isolating. Contamination risk: none — my replay wrote
zero files outside `corpus/live/r64-baseline/`.

## Replay result — deterministic, exact

`rerun.py` (verbatim 86-MODES copy of `r63-author/run_ledger.py`, serial, cwd=
tree root) finished 00:38:11→00:39:42 UTC (~91 s). Ledger:
`ledger-r64-baseline.tsv`; per-command captures `out/{01..86}.{stdout,stderr}`;
census `runs-{before,after,new}.txt`; hash table `committed-shas.tsv`,
`receipt-compare.tsv`.

- **Counts by exit: 43 × exit 0 / 43 × exit 1** — matches committed ledger
  exactly (r62's 43/41 + the two r63 exit-1 probes).
- **86/86 rows identical** to the frozen committed `ledger-r63.tsv` on
  (idx, exit, failure-summary) — `diff` over TSV cols 1,2,4 → empty.
- **Census: 2,968 → 3,054 run dirs (+86, zero extras).** All 86 fresh receipt
  paths resolve under `r64-baseline/tree/corpus/live/runs/`.
- **Receipts: 84/86 byte-identical** (sha256) to the committed counterparts
  named in ledger col 3. The 2 differing rows are the known path-coupled ones:
  - row 03 `ui-route-act-00-r63`: fresh `a0949a852f39…` vs committed
    `a29552cce25d…` — sole diff is the frozen-tree absolute path inside
    `sox_stderr`; `sed` path-normalization restores `a29552cce25d…` exactly.
  - row 81 `--probe-invalid`: fresh `3de3f1dd8e81…` vs committed
    `2ee5f71bc97c…` — sole diff is the embedded `round-6/corrupt.wav` absolute
    path in `detail.stderr`; normalized sha matches exactly.
  - Effective before-state: **86/86 receipts identical modulo the two disclosed
    absolute-path embeddings** — a host-path coupling, not content drift.
- Key receipt SHAs: row 01 normal `8e8cdad6cc3c…` (fresh == committed); row 02
  `ui-route-act-84-r63` `f242bd6bc966…` (fresh == committed — act/ffmpeg route
  re-derived identically in frozen tree).
- Fixture regeneration deterministic in-tree: post-replay
  `pair_route_84.wav` `cf5edecc…`, `pair_route_00.wav` `cb77db31…` — unchanged
  from committed bytes.

## Live-tree contamination observed during the window (report, not mine)

- Commit `5cc0eb0` landed 21:38:17 -0300 mid-replay (r64 interim: reviewer +
  scout reports; knowledge-entry wording fix). Did not affect the frozen replay.
- Working tree currently dirty: `M corpus/fixtures/measure_audio.py`,
  `M corpus/fixtures/build_artifacts.py`, `M __pycache__/*.pyc`, and
  **`M corpus/live/r63-author/ledger-r63.tsv` — the committed r63 ledger was
  overwritten at 21:39:00** with an 86-row all-`exit 2` UNPARSED run (a copied
  `run_ledger.py` keeps the hardcoded r63-author TSV output path; run from cwd
  `corpus/live/runs/` the relative `.shokunin/audio/…` measure path fails).
  Committed bytes are intact; the worktree copy of r63 evidence is corrupt
  until restored. Sibling dirs `corpus/live/r64-{scout,reviewer}/` active;
  canonical `corpus/live/runs/` gained ~185 untracked dirs (2,968→3,153)
  across sibling replays. Attribution between r64-scout/r64-reviewer not
  established from the filesystem — flagged for the lane lead.

## Write-scope accounting

Wrote only: this report; `corpus/live/r64-baseline/` (`rerun.py`,
`ledger-r64-baseline.tsv`, `out/`, `runs-{before,after,new}.txt`,
`committed-shas.tsv`, `receipt-compare.tsv`, `toolchain.txt`, `rerun.log`,
`tree/`). No canonical `corpus/live/runs/` writes, no tracked-file edits, no
commits. Leaf seat — no dispatch performed.

## Residual gaps

- The two path-embedded receipts can never be raw-byte-identical off the
  canonical path; normalized comparison is the strongest check available in a
  displaced tree.
- Sibling mutations of `measure_audio.py`/`build_artifacts.py` in the live
  tree are uncommitted r64 sweep work-in-progress; the frozen replay
  deliberately does not see them — before-state is `37d4c57` by construction.
- Live-tree ledger clobber is a working-tree event; whether it is repaired or
  re-committed is outside my seat.
