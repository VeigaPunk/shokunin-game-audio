# R69 baseline — frozen-HEAD replay of the 114-command r68 ledger

host: devin (`Linux plazir27 7.2.3-arch1-3`, `toolchain.txt`). Seat: baseline.
Frozen state = `git archive HEAD` of canonical HEAD **`7b8d423`** ("r68
report-last: ADMIT — named-axis post-table fork (falsified-as-stated claim
recorded) + txw seekable reader gate; verifier AGREE 5/5;
knowledge/LOG/SCORECARD"). HEAD was `7b8d423` at dispatch (~10:52 UTC), at
archive time (10:55 UTC), and is still `7b8d423` at report time (11:02 UTC)
— **zero mid-window commits** this round.

**Convention change (w8 seat rule):** the archive is a receipt, not a
materialization. `corpus/live/r69-baseline/frozen/head-7b8d423.tar` —
177,244,160 B, sha256 `5db1e9b1605e6faa8f74c85719ea0482924f3fab01abdd5db0
da1b7afd2429d6` (`frozen/archive-sha256.txt`), **22,200 tar members =
17,105 files + 5,095 directory entries** (`frozen/archive-manifest.txt`),
exactly the `git ls-files` file count at `7b8d423`. Zero `node_modules`
members; **zero** members under any `corpus/live/r*-baseline/{frozen,*tree*}/`
(the `live/*/frozen/`, `live/*/tree/`, `live/*/*tree*/` gitignore set keeps
populated snapshot trees untracked — the 1,553 tracked `r*-baseline` members
are scratch ledgers/proofs only, e.g. `r68-baseline/frozen-proofs.txt`).
**The archive was never extracted** — no populated tree anywhere in my
scope.

**Committed ledger:** `corpus/live/r68-author/ledger-r68.tsv` (committed at
`6c91040` "r68: post-table fallback fork = NAME-resolvability"), **114
rows** — the prior 112 plus the two r68 transport modes at positions 02–03.
Secondary committed reference: `corpus/live/r68-verifier/
ledger-r68-verifier.tsv` (same 114-mode order). Both sha256'd identical as
worktree file and `git show 7b8d423:` blob, before and after my window
(`22140ade…` / `22adbd00…`, `committed-ledger-sha.before.txt`,
`post-state.txt`).

## Replay vehicle — minimal verified materialization (replaces extraction)

The seat rule forbids extracting the archive, and `measure_audio.py:17`
anchors `ROOT = Path(__file__).resolve().parents[1]`, so the replay ran
against `corpus/live/r69-baseline/measure-env/corpus/` — a **652-file
tracked-only subset** copied from the clean worktree (`git status` showed
zero modified tracked files at copy time, ~10:56 UTC): `corpus/fixtures/`
(measure_audio.py + build_artifacts.py, both `__file__`-anchored so their
regeneration writes stay in-env), `corpus/artifacts/`, and every
`corpus/live/round-*/` fixture dir the 114 modes read, plus an empty
`live/runs/`. **Every copied file byte-equals its `git show 7b8d423:` blob —
652/652 EQUAL** (`env-proofs.txt`). This is the same isolation the r62–r68
frozen trees provided, with the snapshot receipt (the tar) separated from
the runnable surface; the shape follows the tracked `r65/r66-simplifier/
replica/` precedent. `build_artifacts.py` regenerates fixture wavs under
env's ROOT — all probed members stayed byte-identical to HEAD post-replay
(`post-replay-fixture-check.txt`: `posttable_nomatch.wav` `6373923f…`,
`txw_piperefuse.wav` `fd7911a3…`, `pair_preempt_act.wav` `cf5edecc…`,
`pair_preempt_both.wav` `a37adc7c…`, `pair_dec_hcom.wav` `325fb967…`,
`pair_lengate_hcom_132.wav` `a1abdac4…`, `ui.wav` `4bb56ddf…`,
`stem_layer_third.wav` `3d2048e4…`).

Repo-path note: the brief's line 6 names `~/Projects/prymeagnt/audio`; that
worktree resolves `.shokunin/audio` via symlink into this canonical repo
(`/home/vgpnk/Projects/shokunin/audio-shokunin`, the dispatch header's repo).
All scratch/report writes land in the canonical repo as in r62–r68.

## Replay result — deterministic, exact

`rerun.py` (imports `MODES` verbatim from the committed
`r68-author/run_ledger.py`, `assert len == 114`; serial; per-command
captures to `out/{01..114}.{stdout,stderr}` = 228 files) ran
**10:57:26→10:59:41 UTC (~2 min 15 s), exit 0** (`rerun.log`). Outputs:
`ledger-r69-baseline.tsv`, `runs-env-before.txt` (0) / `runs-new.txt` (114),
`committed-shas.tsv`, `receipt-compare.tsv`, `semantic-compare.tsv`,
`compare.py`, `semantic_compare.py`, `frozen/archive-manifest.txt`,
`frozen/archive-sha256.txt`,
`committed-ledger-sha.before.txt`, `pre-state.txt`, `post-state.txt`,
`env-proofs.txt`, `post-replay-fixture-check.txt`, `toolchain.txt`,
`runs-canonical-{before,after,added}.txt`, `ledger-cols-diff-r68-{author,
verifier}.txt` (both 0 bytes).

- **Counts by exit: 49 × exit 0 / 65 × exit 1** — matches committed
  `ledger-r68.tsv` exactly (the r68-verifier ledger agrees identically) and
  the brief's declared expectation.
- **114/114 rows identical** to committed on (idx, exit, failure-summary) —
  `diff` over TSV cols 1,2,4 → empty against **both** committed r68 ledgers
  (`ledger-cols-diff-*.txt`).
- **Census: env `runs/` 0 → 114 (+114, zero extras).** All 114 fresh receipts
  resolve under `r69-baseline/measure-env/corpus/live/runs/` (stamps
  `20261014T105733…T105941`); grep-verified 114/114 col-3 paths carry the
  env infix. **Zero writes to canonical `corpus/live/runs/`** — the
  `__file__` anchor makes canonical writes impossible from the env.
- **Committed-receipt anchor: 114/114** committed receipts named in
  `ledger-r68.tsv` col 3 are byte-identical to their `git show 7b8d423:`
  blobs (`compare.py` `tracked-committed=114/114`).
- **Receipts: 101/114 byte-identical** (sha256) to committed counterparts —
  including all twelve r67+r68 transport rows (02–13), whose receipts carry
  no absolute paths by design; **2 normalized** (rows 31
  `ui-route-act-00-r63`, 109 `--probe-invalid`): absolute paths embedded in
  full stderr leaves — the env→canonical infix rewrite
  (`corpus/live/r69-baseline/measure-env/corpus/` → `corpus/`) restores the
  committed sha256 exactly; **11 raw-DIFFERS, all the known truncation
  class** — rows 16, 17, 19 (`ui-lengate-{gsrt-24,gsrt-25,hcom-132}-r66`),
  20–23 (`ui-preempt-{act,gsrt,hcom,both}-r65`), 26–29
  (`ui-extensible-valid-{24,25,56,57}-r64`): `tail[-1][-160:]` cuts the
  embedded absolute path mid-token at the leaf head (fresh row-16 leaf
  begins `"nput file …"` vs committed `"sox FAIL formats: can't open input
  file …"`), so no prefix rewrite can sha-match; anchored suffix after the
  last `corpus/` is byte-identical. Same 13-mode set as r68's differing
  rows, shifted +2 by the newest-first ledger convention.
- JSON-level comparison (`semantic_compare.py`): identical structure on all
  114 rows; every differing string leaf is `corpus/`-anchored in both
  receipts with equal post-anchor suffix and carries the
  `live/r69-baseline/measure-env/` infix — **101 EQUAL, 13 EQUAL-MOD-PATHS,
  0 CONTENT-DIFF, 0 STRUCTURE-DIFF** (`semantic-compare.tsv`). All 30
  differing leaves are `sox_{bridge,native,stat,}_stderr` /
  `invalid_probes[1].detail.stderr` — the path-embedding class only.
- Row-01 normal receipt sha `8e8cdad6cc3c356d07c463498f4759b8d73e73935cf591
  d117732f09ffaffb1b` — identical fresh and committed; the same value the
  r66, r67 and r68 baselines recorded for the opening row.
- Committed-ledger guard: `ledger-r68.tsv` sha256 `22140ade…` and verifier
  `22adbd00…` identical before and after my run — the replay writes only to
  scratch.
- **Drift: zero** — all deltas are explained by the known path-embedding
  convention.

Toolchain: `SoX_ng v14.8.0.1`, `ffmpeg/ffprobe n9.0.1`, `python3 3.14.7` +
`numpy 2.5.3` — unchanged from the r63–r68 declared set.

## Live-tree events during the window (observed, not mine)

- Sibling r69 lanes mid-flight: untracked `corpus/live/r69-{author,boundary,
  critic,reviewer,scout,scribe}/` dirs plus this lane's `r69-baseline/`.
- Canonical `corpus/live/runs/` grew 4,784 → 4,793 during my replay window
  (`runs-canonical-{before,after,added}.txt`): 2 continuation rows of a
  sibling's live r68-ledger replay (`…T105949…-transport-posttable-nomatch-
  r68`, `…T105951…-transport-txw-piperefuse-r68`) plus 4 new
  `transport-extsuffix-{wav,bin,snd}-r69` dirs — the r69 author lane's
  declared EXTENSION-SUFFIX sweep landing. Zero name overlap with my 114
  env receipts; none written by this replay.
- At ~11:00 UTC the author lane's additive edits touched the worktree:
  `git status` now shows ` M corpus/fixtures/measure_audio.py`
  (`f7da1e46…` → `09d426b5…`), ` M corpus/fixtures/build_artifacts.py`, and
  the two tracked `__pycache__/*.pyc` — uncommitted, HEAD unchanged. My
  replay consumed only the verified env copies (`f7da1e46…` / `96bfc1ea…`,
  re-verified post-run MATCH-HEAD), so the mid-window modification cannot
  have skewed any receipt — this is the isolation the env exists for.

## Write-scope accounting

Wrote only: this report; `corpus/live/r69-baseline/` (`frozen/` holding the
archive + manifest + sha only — no extraction —, `measure-env/` (652
verified HEAD-equal files + the 114 fresh receipt dirs), `rerun.py`,
`rerun.log`, `ledger-r69-baseline.tsv`, `out/` (228 captures), the census,
hash and diff tables listed above, `pre-state.txt`, `post-state.txt`,
`env-proofs.txt`, `post-replay-fixture-check.txt`, `toolchain.txt`). No
canonical `corpus/live/runs/` writes, no tracked-file edits, no commits, no
pushes. Leaf seat — no dispatch performed.

## Residual gaps

- Path-embedded receipts (rows 16–17, 19–23, 26–29, 31, 109) can never be
  raw-byte-identical off the canonical path; 11 of the 13 truncate the path
  mid-token at the leaf head, so anchor-level JSON comparison is the
  strongest check available in a displaced tree — unchanged from r68.
- `measure-env/` is a minimal materialization, not a full snapshot: it
  carries the 652 tracked files the replay surface reads. The full-fidelity
  proof of HEAD is the tar in `frozen/` (reproducible byte-identically from
  `7b8d423`), not the env.
- The sibling live replay filling canonical `corpus/live/runs/` is another
  lane's evidence path; canonical census numbers here are a snapshot of
  ~11:01 UTC, and the author's uncommitted worktree edits will move those
  files' shas once the parent integrates.
