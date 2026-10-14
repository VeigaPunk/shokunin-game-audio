# R74 baseline — frozen-HEAD replay of the 123-command battery (consumers-r73 now wired; lavfsweep-r74 commit landed mid-window)

host: devin (`Linux plazir27 7.2.3-arch1-3`, `toolchain.txt`). Seat: baseline.
Frozen state = `git archive HEAD` of pre-move HEAD **`1ba8103`** ("r73
report-last: adjudicator ADMIT-corr …"). HEAD was `1ba8103` at first
inspection (~15:21 UTC), stayed `1ba8103` through the whole replay, and moved
to **`168b165`** ("r74: lavf no-seek demuxer sweep … + pw-cat ops-2 …") at
15:37:52 UTC — after my replay completed; the post-commit re-verification
below anchors on `168b165`. All freeze anchors reference `1ba8103`
exclusively.

**Convention (carried from r62–r73):** the archive is a receipt, not a
materialization. `corpus/live/r74-baseline/frozen/head-1ba8103.tar` —
344,842,240 B, sha256
`ee145eede717572b018b6e894b6af8ab8ba364af2e72ac77d06b1f3c77765459`
(`frozen/archive-sha256.txt`), **29,010 tar members = 22,339 files + 6,671
directory entries** (`frozen/archive-manifest.txt`), exactly the
`git ls-files` count at `1ba8103` (comm-diff 0 in both directions). Zero
`node_modules` members; zero members under any
`corpus/live/r*-*/{frozen,tree,head,snapshot,base,*extract*}/` directory
(the only `*extract*` hits are tracked source filenames —
`lattice_extract.py` et al., not dirs; `corpus/.gitignore:4-16` set verified
by enumeration). **Never extracted.**

**Committed ledger:** `corpus/live/r70-author/ledger-r71.tsv` @ `1ba8103`,
**121 rows**, sha256 `8d59f552…` identical before the window, after the
replay, **and at the post-move HEAD `168b165`**
(`committed-ledger-sha.{before,after}.txt`, `postcommit-verify.txt`).
Standing caveat (unchanged since r73): this ledger is the r70-order battery
plus a second `""` normal at row 02 — no `ffprobe-transport-r71`,
`sndfile-transport-r72`, or `consumers-r73` rows. The committed receipt
anchors for r71/r72 live in `corpus/live/runs/` (3 tracked runs each, since
`4fff488`); **consumers-r73 still has zero committed receipts** at `168b165`
— its anchors are the untracked canonical sibling receipts (15 at capture
time).

**Battery definition:** 123 commands — the r73-author ordering taken verbatim
from worktree `corpus/live/r73-author/run_ledger.py` MODES (`rerun.py`
carries the list, `assert len == 123`): newest-first, `consumers-r73` at
position 02, `sndfile-transport-r72` at 03, `ffprobe-transport-r71` at 04,
`fifo-hold-ladder-r70` at 05. The committed tree contains no 123-row ledger;
this ordering is the freshest encoding of the full committed probe surface.

## Replay vehicle — minimal verified materialization (replaces extraction)

`measure-env/corpus/` — the **657-file tracked-only subset** materialized
directly from `git show 1ba8103:` blobs (`build_env.py`):
`corpus/fixtures/` (incl. tracked `__pycache__`), `corpus/artifacts/`, every
tracked `corpus/live/round-*/` fixture the battery reads (incl. the r73
pacer `artifacts/stem_sections.wav` and the shared 9-member matrix under
round-65/66/68/69), plus an empty `live/runs/`. Every file byte-equals its
HEAD blob — **657/657 EQUAL** (`env-proofs.txt`; `env-filelist.txt` lists the
set). Direction checks clean both ways (`env-comm.txt`): 0 untracked env
members, 0 tracked inputs missing. `measure_audio.py:19` anchors
`ROOT = Path(__file__).resolve().parents[1]` and `build_artifacts.py` is
invoked via `Path(__file__).with_name(...)`, so every regeneration and
receipt write stayed inside the env — canonical writes are impossible from
it. Ten probed members/artifacts re-checked byte-equal to HEAD **after** the
replay (`post-replay-fixture-check.txt`: `pair_dec_act` `777b6764…`,
`pair_dec_hcom` `325fb967…`, `posttable_nomatch` `6373923f…`,
`txw_piperefuse` `fd7911a3…`, `extsuffix_nomatch.wav`/`.snd` `f073e70a…`,
`ui.wav` `4bb56ddf…`, `stem_layer_third` `3d2048e4…`, `ambience`
`b18c8170…`, `stem_sections` `49ca24fb…`).

## Replay result — deterministic; prior rows byte-stable modulo the known classes

`rerun.py` ran **15:23:40 → 15:30:27 UTC (~6 m 47 s), driver exit 0**
(`rerun.log`; per-command captures `out/{01..123}.{stdout,stderr}` = 246
files). Outputs: `ledger-r74-baseline.tsv`, `ledger-compare-mode.tsv`,
`ledger-compare-mismatches.txt`, `receipt-compare.tsv`,
`receipt-membership.tsv`, `semantic-compare.txt`, `compare.py`,
`semantic_compare.py`.

- **Counts by exit: 50 × exit 0 / 73 × exit 1** — committed ledger-r71 is
  50/71; the +2 exit-1 rows are the r72 sndfile fork and the r73 consumers
  fork verdicts (consistent with the committed r71/r72 receipts and the r73
  sibling receipts).
- **Ledger compare (mode-keyed vs committed ledger-r71): 120/121 MATCH** on
  (exit, failure-summary) — `ledger-compare-mode.tsv`. The single
  **EXIT-ONLY**: `fifo-hold-ladder-r70` — committed failsum carries a second
  clause (`chunked … h=0.05 -> 9x verdict/1x blocked`, band
  `{max_div 0.05, min_stable 0.0}`) from a 1/10 chunked-feed flake on that
  committed run; my run produced the clean distribution and the oneshot
  clause is **verbatim identical** (`h=0.0 -> 10x blocked`; band
  `{0.0, 0.05}`). Same load-dependent band class documented since r70.
- **Committed-receipt anchors: 106/121 byte-identical** (sha256 of
  `git show 1ba8103:` blob = fresh env receipt) — `receipt-compare.tsv`.
- **Fresh-receipt membership: 109/123** sha256 present in the committed
  same-mode receipt set (`receipt-membership.tsv`; all committed `runs/`
  receipts hashed via `git show`). Includes the two decoder rows matching
  **every** committed counterpart: row-03 sndfile = 3/3 committed r72
  receipts; row-04 ffprobe = 3/3 committed r71 receipts.
- **13 NOT-INSET receipts = the known path-embedding class**, all
  **EQUAL-ANCHORED-TAIL** on JSON leaf-walk (`semantic-compare.txt`):
  identical structure, every differing leaf `corpus/`-anchored in both
  receipts with equal post-anchor (last-`corpus/`) suffix and the
  `live/r74-baseline/measure-env/` infix — `ui-lengate-gsrt-{24,25}-r66`,
  `ui-lengate-hcom-132-r66`, `ui-preempt-{act,gsrt,hcom,both}-r65`,
  `ui-extensible-valid-{24,25,56,57}-r64`, `ui-route-act-00-r63`, `invalid`.
  Differing keys: `sox_{bridge,native,stat,}_stderr` /
  `invalid_probes[].detail.stderr` only. Same 13-mode set as r68–r73, zero
  CONTENT-DIFF, zero STRUCTURE-DIFF.
- **14th NOT-INSET = row-02 `consumers-r73`** (`9b422aa2…`, committed set
  size 0 — no committed anchor exists). Cross-checked against the 15
  untracked canonical sibling consumers receipts: **byte-EQUAL to 3**
  (`145606550135Z`, `150103164753Z`, and `152502427863Z` — the last written
  to the canonical tree *during my replay*, an independent canonical-tree
  corroboration of my env receipt), **JITTER-LEAVES vs 7** (differences
  confined to `pacing_{instant,trickle}.wall_s` — the declared realtime
  pacing jitter), **STRUCTURE-DIFF vs 5 early receipts**
  (`1451*`–`150305963053Z`) which lack the `pwcat_name_axis` block or carry
  variant `stderr_tail` keys — pre-fold mid-flight impl variants, not
  committed-surface drift.
- **committed-02 `normal` anomaly (pre-existing, not new drift):** its
  anchored receipt `98f76ff9…` remains a strict superset of the canonical
  normal receipt — identical except an inserted `ffprobe_*_r71_probe` block
  produced by an uncommitted impl variant (`git log -S` → never committed).
  All six of my fresh normal receipts are the canonical `8e8cdad6…` — the
  same value r66–r73 recorded for row 01.
- **Census: env `runs/` 0 → 123, zero extras.** 123/123 col-3 receipt paths
  carry the `r74-baseline/measure-env/` infix. Canonical `corpus/live/runs/`
  grew **5,593 → 5,607** during my window (+14 sibling receipts —
  `runs-canonical-{before,after,added,final}.txt`, incl. five
  `lavfsweep-r74` runs: the r74 arm was mid-flight); **zero name overlap**
  with my env receipts, zero canonical writes by me.
- Committed-ledger guard: `8d59f552…` before, after, and @`168b165` —
  replay wrote only to scratch.

**Drift: zero.** Every receipt delta is one of the known classes
(path-embedding ×13; the ledger's own uncommitted-impl normal receipt; the
declared load-dependent ladder band; consumers wall_s jitter / pre-fold
sibling variants — no committed anchor exists for that family).

## Post-commit re-verification (r74 commit `168b165`, landed 15:37:52 UTC)

- `git diff 1ba8103 168b165` touches **8 paths only**: `measure_audio.py`
  (+584 net), six new `corpus/live/round-74/lavf_*` members, and
  `reports/round-74/r74-author.md`. **Zero `live/runs/` paths** — all 5,290
  committed receipt blobs are byte-identical across the move by object
  identity (40-sample spot-check: 0 changed).
- Deletions inside `measure_audio.py` are confined to the three dispatch
  wiring lines (exclusivity `sum()`, `mode=`, `suffix=`) — each replaced by
  the same line extended with `probe_lavfsweep_r74` — plus a 6-line
  falsified-claim comment restatement. Insertion-only guard holds for every
  prior probe arm.
- New mode wired: `--probe-lavfsweep-r74` (argparse `measure_audio.py:2111`
  @`168b165`; mode dispatch 2849; suffix 2869). `consumer_pwcat_ops2_r74_probe`
  is emitted **inside the lavfsweep arm** (`:2353`, key at `:2382`) — the
  `consumers-r73` block (`:2333`–`:2352`) is untouched, so consumers receipts
  at `168b165` keep the same shape my frozen-HEAD replay measured.
- **Sibling-battery counts:** the committed tree still carries **no**
  123/124-row ledger ( freshest ordering remains the untracked r73-author
  MODES; the r74-author dir holds logs/`members/`/`mk_members.py`, no ledger
  file yet). Canonical untracked receipts now: consumers ×15, lavfsweep ×5
  (4 distinct shas — mid-flight variants), sndfile ×17, ffprobe ×14,
  fifo-hold ×14. Expected sibling battery at `168b165` = 124 rows
  (lavfsweep newest-first at 02) whenever the r74 ledger lands.
- Frozen archive validity post-move: the tar remains a faithful
  byte-receipt of `1ba8103` (immutable git object set); nothing in `168b165`
  alters the frozen anchors.

## Toolchain + consumer-class viability (measured)

`SoX_ng v14.8.0.1`, `ffmpeg/ffprobe n9.0.1`, `python3 3.14.7` +
`numpy 2.5.3`, `libsndfile-1.2.2` (ctypes lazy load), `pw-cat` w/
libpipewire **1.6.8**, `mpv v0.41.0`, `pactl`: PulseAudio-on-PipeWire live,
default sink `alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink`
(`toolchain.txt`) — unchanged declared set; pipewire daemon LIVE
(`/usr/bin/pipewire` pid 1905, `pipewire-pulse` pid 2290).

## Live-tree events during the window (observed, not mine)

- Sibling `corpus/live/r74-author/` work appeared mid-window:
  ` M corpus/fixtures/measure_audio.py` (the +544-line worktree diff that
  became `168b165`), `?? corpus/live/round-74/` members, `?? r74-author/`
  scratch; +14 canonical `runs/` receipts (5 lavfsweep, 2 consumers, plus
  sndfile/ffprobe/extsuffix/dec-act legs). All folded/committed by `168b165`.
- `reports/round-74/` appeared with six sibling reports
  (author/boundary/critic/reviewer/scout/scribe).
- Pre-existing uncommitted state persists untouched:
  ` M corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`
  (import-time regen), untracked `r71-critic`/`r72-*` leftovers,
  `pwcat_tmp.err`.

## Write-scope accounting

Wrote only: this report; `corpus/live/r74-baseline/` (`frozen/` tar +
manifest + sha — ignored dir per `corpus/.gitignore:5`, receipt only, never
extracted; `measure-env/` 657 verified files + 123 fresh receipt dirs;
`build_env.py`, `rerun.py`, `rerun.log`, `ledger-r74-baseline.tsv`, `out/`
246 captures, `compare.py`, `semantic_compare.py`,
`ledger-compare-mode.tsv`, `ledger-compare-mismatches.txt`,
`receipt-compare.tsv`, `receipt-membership.tsv`, `semantic-compare.txt`,
`env-filelist.txt`, `env-proofs.txt`, `env-comm.txt`,
`post-replay-fixture-check.txt`,
`committed-ledger-sha.{before,after}.txt`, `postcommit-verify.txt`,
`toolchain.txt`, `pre-state.txt`, `post-state.txt`,
`runs-canonical-{before,after,added,final}.txt`). No canonical
`corpus/live/runs/` writes, no tracked-file edits, no commits, no pushes.
Leaf seat — no dispatch performed.

## Residual gaps

- The 13 path-embedding receipts can never raw-match off the canonical
  path; anchored-tail JSON compare is the strongest displaced-tree check
  (unchanged since r68).
- Committed ledger-r71 row-02 anchors a receipt no frozen tree can
  reproduce (uncommitted-impl artifact); flagged, not correctable from this
  seat.
- `consumers-r73` still has **no committed receipt anchor** — my row-02
  check is against untracked sibling receipts (3 byte-equal + jitter-only
  remainder). If the arm's receipts get committed later, the membership
  cell becomes exact.
- `fifo-hold-ladder-r70` remains a load-dependent band: this run landed on
  the canonical stable signature (all 14 committed r70-family receipts
  byte-covered), but the chunked h≈0.05 cell has measured 1/10 flakes —
  expect occasional EXIT-ONLY failsum drift on that row.
- `measure-env/` is the minimal tracked replay surface (657 files), not a
  full snapshot; the full-fidelity proof of pre-move HEAD is the frozen
  tar, reproducible byte-identically from `1ba8103`.
- The 123-row ordering exists only in untracked `r73-author` scratch, and
  no committed 124-row ordering exists yet at `168b165`; if the r74-author
  seat lands a different canonical ordering, mode-keyed comparisons remain
  valid but position-keyed diffs would shift.
