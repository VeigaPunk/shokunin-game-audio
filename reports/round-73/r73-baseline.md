# R73 baseline — frozen-HEAD replay of the 122-command battery (sndfile-transport-r72 now committed)

host: devin (`Linux plazir27 7.2.3-arch1-3`, `toolchain.txt`). Seat: baseline.
Frozen state = `git archive HEAD` of canonical HEAD **`f5d7faf`** ("r72
reviewer-fold: lazy libsndfile load … + blocked-verdict arm"). HEAD was
`50f55eb` at first inspection (~14:39 UTC during survey) and `f5d7faf` by
pre-state capture (14:43:16 UTC, `pre-state.txt`) — a sibling fold commit
landed inside my window before the freeze; the archive, env proofs, and all
anchors below reference **`f5d7faf`** exclusively. HEAD remained `f5d7faf`
through post-state (14:56:03 UTC).

**Convention (carried from r62–r70):** the archive is a receipt, not a
materialization. `corpus/live/r73-baseline/frozen/head-f5d7faf.tar` —
344,576,000 B, sha256
`b6290bfda4e30ffdcf06273b099edb7c6958099ac56224e48850505b95ae8605`
(`frozen/archive-sha256.txt`), **28,995 tar members = 22,325 files + 6,670
directory entries** (`frozen/archive-manifest.txt`), exactly the
`git ls-files` count at `f5d7faf`. Zero `node_modules` members; zero members
under any `corpus/live/r*-*/{frozen,tree,head,snapshot,base,*extract*}/`
(gitignore set verified, `corpus/.gitignore:4-16`). **Never extracted.**

**Committed ledger:** `corpus/live/r70-author/ledger-r71.tsv` @ `f5d7faf`,
**121 rows**, sha256 `8d59f552…` identical before and after my window
(`committed-ledger-sha.{before,after}.txt`). Caveat disclosed in detail below:
this ledger is the r70-order battery plus a second `""` normal at row 02 — it
contains **no** `ffprobe-transport-r71` or `sndfile-transport-r72` rows. Those
two modes' committed anchors are their `corpus/live/runs/` receipts instead
(3 tracked runs each, committed at `4fff488`).

**Battery definition:** 122 commands — the r70-order prior set plus
`--probe-ffprobe-transport-r71` and `--probe-sndfile-transport-r72`, both
wired into `corpus/fixtures/measure_audio.py` at `f5d7faf` (argparse lines
1129–1131, mode dispatch 1819+). Ordering = the worktree
`corpus/live/r72-author/run_ledger.py` MODES verbatim (untracked sibling
scratch; `rerun.py` carries the list verbatim, `assert len == 122`):
newest-first, sndfile at position 02, ffprobe at 03, fifo-hold-ladder at 04.
The committed tree contains no 122-row ledger; this ordering is the freshest
encoding of the full committed probe surface.

## Replay vehicle — minimal verified materialization (replaces extraction)

`measure-env/corpus/` — the **657-file tracked-only subset** materialized
directly from `git show f5d7faf:` blobs: `corpus/fixtures/` (incl. tracked
`__pycache__`), `corpus/artifacts/`, every `corpus/live/round-*/` fixture path
the battery reads, plus an empty `live/runs/`. Every file byte-equals its
HEAD blob — **657/657 EQUAL** (`env-proofs.txt`; `env-filelist.txt` lists the
set). Direction checks clean both ways (`env-comm.txt`): 0 untracked env
members, 0 tracked inputs missing. `measure_audio.py:19` anchors
`ROOT = Path(__file__).resolve().parents[1]` and `build_artifacts.py` is
invoked via `Path(__file__).with_name(...)` (line 1136, 1145), so every
regeneration and receipt write stayed inside the env — canonical writes are
impossible from it. Nine probed members/artifacts re-checked byte-equal to
HEAD **after** the replay (`post-replay-fixture-check.txt`: `pair_dec_act`
`777b6764…`, `pair_dec_hcom` `325fb967…`, `posttable_nomatch` `6373923f…`,
`txw_piperefuse` `fd7911a3…`, `extsuffix_nomatch.wav`/`.snd` `f073e70a…`,
`ui.wav` `4bb56ddf…`, `stem_layer_third` `3d2048e4…`, `ambience`
`b18c8170…`).

## Replay result — deterministic; prior rows byte-stable modulo two known classes

`rerun.py` ran **14:45:50 → ~14:52:00 UTC (~6 m 09 s), driver exit 0**
(`rerun.log`; per-command captures `out/{01..122}.{stdout,stderr}` = 244
files). Outputs: `ledger-r73-baseline.tsv`, `ledger-compare-mode.tsv`,
`ledger-compare-mismatches.txt`, `receipt-compare.tsv`,
`receipt-membership.tsv`, `semantic-compare.txt`, `compare.py`.

- **Counts by exit: 50 × exit 0 / 72 × exit 1** — committed ledger-r71 is
  50/71; the +1 exit-1 is the new row-02 `sndfile-transport-r72` fork verdict
  (committed r72 receipts are the same exit-1 fork — consistent).
- **Ledger compare (mode-keyed vs committed ledger-r71): 120/121 MATCH** on
  (exit, failure-summary) — `ledger-compare-mode.tsv`. The single
  **EXIT-ONLY**: `fifo-hold-ladder-r70` — committed failsum carries a second
  clause (`chunked … h=0.05 -> 9x verdict/1x blocked`, band
  `{max_div 0.05, min_stable 0.0}`) from a 1/10 chunked-feed flake on that
  run; my run produced the clean 10/10 chunked distribution, and the oneshot
  clause is **verbatim identical** (`h=0.0 -> 10x blocked`; band
  `{0.0, 0.05}`). Same load-dependent band class documented since r70.
- **Committed-receipt anchors: 106/121 byte-identical** (sha256 of
  `git show f5d7faf:` blob = fresh env receipt) — `receipt-compare.tsv`.
- **Fresh-receipt membership: 109/122** sha256 present in the committed
  same-mode receipt set (`receipt-membership.tsv`; all committed `runs/`
  receipts hashed via `git show`). Includes the two newest rows matching
  **every** committed counterpart: row-02 sndfile `f7faaedb…` = 3/3 committed
  r72 receipts (142618906524Z, 142634507936Z, 142733592435Z); row-03 ffprobe
  `578cad95…` = 3/3 committed r71 receipts (141008229687Z, 141033155858Z,
  142028085688Z).
- **13 NOT-INSET receipts = the known path-embedding class**, all
  **EQUAL-ANCHORED-TAIL** on JSON leaf-walk (`semantic-compare.txt`):
  identical structure, every differing leaf `corpus/`-anchored in both
  receipts with equal post-anchor suffix and the
  `live/r73-baseline/measure-env/` infix — `ui-lengate-gsrt-{24,25}-r66`,
  `ui-lengate-hcom-132-r66`, `ui-preempt-{act,gsrt,hcom,both}-r65`,
  `ui-extensible-valid-{24,25,56,57}-r64`, `ui-route-act-00-r63`, `invalid`.
  Differing keys: `sox_{bridge,native,stat,}_stderr` / `invalid_probes[].…`
  only. Same 13-mode set as r68–r70, zero CONTENT-DIFF, zero STRUCTURE-DIFF.
- **committed-02 `normal` anomaly (pre-existing in the committed ledger, not
  new drift):** its anchored receipt `98f76ff9…` is a strict superset of the
  canonical normal receipt — identical except one inserted 854-line
  `ffprobe_*_r71_probe` block (lines 360–1213), i.e., a `-normal`-stamped
  receipt produced by an **uncommitted** impl variant (`git log -S
  ffprobe_posttable_nomatch_r71_probe` → no commit ever carried it). All six
  of my fresh normal receipts are the canonical `8e8cdad6…` — the same value
  the r66–r70 baselines recorded for row 01.
- **Census: env `runs/` 0 → 122, zero extras.** 122/122 col-3 receipt paths
  carry the `r73-baseline/measure-env/` infix. Canonical `corpus/live/runs/`
  grew **5432 → 5455** during my window (+23 sibling receipts —
  `runs-canonical-added.txt`, incl. five `consumers-r73` runs: the r73 arm is
  mid-flight on sibling worktrees); **zero name overlap** with my env
  receipts, zero canonical writes by me.
- Row-01 receipt sha `8e8cdad6cc3c356d07c463498f4759b8d73e73935cf591d117732f09
  ffaffb1b` — identical to the r66–r70 baseline value.
- Committed-ledger guard: `8d59f552…` before and after — replay wrote only to
  scratch.

**Drift: zero.** Every receipt delta is one of the two known classes
(path-embedding; the ledger's own uncommitted-impl normal receipt) or the
declared load-dependent ladder band.

## Toolchain + r73 consumer-class viability (measured, for the pw-cat gate)

`SoX_ng v14.8.0.1`, `ffmpeg/ffprobe n9.0.1`, `python3 3.14.7` + `numpy 2.5.3`,
`libsndfile-1.2.2` (`toolchain.txt`) — unchanged declared set. Round-73
additions measured on this host: **pipewire daemon LIVE**
(`pgrep`: `/usr/bin/pipewire` pid 1905, `/usr/bin/pipewire-pulse` pid 2290),
`pw-cat` present, compiled with libpipewire **1.6.8**; `mpv v0.41.0`
(built 2026-08-28); `pacman`: pipewire 1:1.6.8-1, mpv 1:0.41.0-6. The pw-cat
arm's daemon-required gate **passes on this host**.

## Live-tree events during the window (observed, not mine)

- HEAD `50f55eb` → `f5d7faf` mid-survey (committed 14:38:20 UTC; the r72
  reviewer fold — lazy libsndfile import + blocked-verdict arm in
  `measure_audio.py`, +83 lines). Frozen after the move; all anchors are
  f5d7faf.
- Sibling r73 seats mid-flight: `corpus/live/r73-{author,boundary,critic,
  reviewer,scout,scribe,simplifier}/` scratch dirs and six sibling reports
  already under `reports/round-73/`; `r73-author/` had only `scratch/`.
- Canonical `runs/` +23 during my replay (above) — none mine.
- Pre-existing uncommitted sibling edits persist untouched: ` M
  corpus/live/r72-baseline/measure-env/corpus/fixtures/measure_audio.py`,
  untracked `r72-author/`, `pwcat_tmp.err`, untracked
  `reports/round-72/r72-{baseline,reviewer,verifier}.md`. Mid-window
  sibling edits also landed on tracked `LOG.md` and `SCORECARD.md`
  (absent from `pre-state.txt`, present at post-state); the earlier ` M
  corpus/live/r72-verifier/lattice.json` was folded away by the
  `f5d7faf` commit.

## Write-scope accounting

Wrote only: this report; `corpus/live/r73-baseline/` (`frozen/` tar +
manifest + sha — ignored dir per `corpus/.gitignore:5`, receipt only, never
extracted; `measure-env/` 657 verified files + 122 fresh receipt dirs;
`rerun.py`, `rerun.log`, `ledger-r73-baseline.tsv`, `out/` 244 captures,
`compare.py`, `ledger-compare-mode.tsv`, `ledger-compare-mismatches.txt`,
`receipt-compare.tsv`, `receipt-membership.tsv`, `semantic-compare.txt`,
`env-filelist.txt`, `env-proofs.txt`, `env-comm.txt`,
`post-replay-fixture-check.txt`, `committed-ledger-sha.{before,after}.txt`,
`toolchain.txt`, `pre-state.txt`, `post-state.txt`,
`runs-canonical-{before,after,added}.txt`). No canonical `corpus/live/runs/`
writes, no tracked-file edits, no commits, no pushes. Leaf seat — no
dispatch performed.

## Residual gaps

- The 13 path-embedding receipts can never raw-match off the canonical path;
  anchored-tail JSON compare is the strongest displaced-tree check (unchanged
  since r68).
- Committed ledger-r71 row-02 anchors a receipt no frozen tree can
  reproduce (uncommitted impl artifact); flagged, not correctable from this
  seat.
- `fifo-hold-ladder-r70` remains a load-dependent band: this run landed on
  the canonical stable signature (4 committed r70 receipts byte-equal), but
  the chunked h≈0.05 cell has measured 1/10 flakes — expect occasional
  EXIT-ONLY failsum drift on that row.
- `measure-env/` is the minimal tracked replay surface (657 files), not a
  full snapshot; the full-fidelity proof of HEAD is the frozen tar,
  reproducible byte-identically from `f5d7faf`.
- The 122-row ordering exists only in untracked `r72-author` scratch; if the
  author seat lands a different canonical ordering this round, the
  mode-keyed comparisons here remain valid but position-keyed diffs would
  shift.
