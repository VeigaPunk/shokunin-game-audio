# R75 baseline — frozen-HEAD replay of the 124-command battery (recovery generation; consumers2-r75 commit landed post-replay)

host: devin (`Linux plazir27 7.2.3-arch1-3`, `toolchain.txt`). Seat: baseline.
Frozen state = `git archive HEAD` of pre-move HEAD **`6f905c3`** ("xsentinel
w12 fold: ignore r71-critic big.wav + measure-env/ clone trees"). HEAD stayed
`6f905c3` through my whole replay window and moved to **`db46fba`** ("r75:
consumer-class breadth — paplay + aplay + ffplay …") at ~16:52 UTC — after
the replay completed; the post-commit re-verification below anchors on
`db46fba`. All freeze anchors reference `6f905c3` exclusively.

## Recovery context (prior generation died ~16:10Z)

The prior generation's artifacts survive under
`corpus/live/r75-baseline/recovery-prior/`. Verified state at takeover:

- Their frozen tar is **`head-49747ba.tar`** — the pre-move HEAD *at their
  freeze time* (~16:03Z). `6f905c3` landed mid-their-window; their
  `build_env.py` already noted the fold. Since the wave instruction pins the
  freeze to current HEAD and `49747ba != 6f905c3`, I **re-froze** at
  `6f905c3` (`frozen/head-6f905c3.tar`); their tar/manifest/sha kept under
  `recovery-prior/frozen/` as evidence.
- `git diff 49747ba 6f905c3` = **`corpus/.gitignore` +4 lines only**
  (`live/r71-critic/big.wav`, `live/*/measure-env/`); `comm -3` of the two
  `ls-tree -r` name lists is empty both ways. Therefore every blob the env
  materialized is byte-identical at `6f905c3`; spot `git rev-parse
  <sha>:<path>` re-checks (measure_audio.py, build_artifacts.py, ui.wav,
  lavf_iss.iss) all SAME.
- Their replay died after 5/124 rows (`recovery-prior/ledger-partial-5rows.tsv`,
  `recovery-prior/out/` captures, `rerun-partial.log`). Their 5 receipts persist inside
  `measure-env/corpus/live/runs/` — **3/5 byte-equal to my fresh receipts**
  (normal `8e8cdad6…` = the canonical normal sha since r66; sndfile-r72
  `f7faaedb…`; ffprobe-r71 `578cad95…`); lavfsweep + consumers differ only in
  the declared jitter classes (cross-generation determinism evidence).
- Reused as-is: `measure-env/` (663 files, `env-proofs.txt` 663/663 EQUAL,
  `env-comm.txt` 0/0 direction checks), `build_env.py` + `rerun.py`
  (docstrings/pin updated to `6f905c3`), and regenerated all state captures
  (`pre-state.txt`, `toolchain.txt`, `committed-ledger-sha.before.txt`,
  `runs-canonical-before.txt`).

## Frozen archive (receipt, not materialization — never extracted)

`corpus/live/r75-baseline/frozen/head-6f905c3.tar` — sha256
`6cc5de458ef43c259392114803427a7464f51f6ecc5cb390592f0518cdbfe74f`
(`frozen/archive-sha256.txt`), **29,028 tar members = 22,355 files + 6,673
directory entries** (`frozen/archive-manifest.txt`), exactly the
`git ls-files` count at `6f905c3` (comm-diff **0 in both directions**).
Zero `node_modules` members. 2,348 committed file members sit under prior
seats' tracked `measure-env/` trees (r69-baseline 766, r69-verifier 777,
r70-baseline 776, r72-baseline 29 — pre-w12-fold tracked content; the new
ignore rule only prevents *future* tracking). No tar member is a live
`frozen/`, `tree/`, `head/`, `snapshot/`, `base/` scratch dir beyond those
committed trees.

**Committed ledger:** `corpus/live/r70-author/ledger-r71.tsv`, sha256
`8d59f552e1370c5e0b50989eacff93e6f4bdf35352a31aa7121616e176579b95` / blob
`c4f5c6196f398585f55a8237ab9cbc3f34760621` — identical before the window,
after the replay, **and at post-move HEAD `db46fba`**
(`committed-ledger-sha.{before,after}.txt`, `postcommit-verify.txt`).
Standing caveat (unchanged since r73): this ledger is the r70-order battery
plus a second `""` normal — no r71–r75 family rows.

**Battery definition:** 124 commands — the r73-author ordering verbatim from
worktree `corpus/live/r73-author/run_ledger.py` MODES with
`--probe-lavfsweep-r74` inserted newest-first at position 02 (`rerun.py`,
`assert len == 124`). No committed 124-row ledger exists; this ordering is
the freshest encoding of the full committed probe surface.

## Replay vehicle — minimal verified materialization (replaces extraction)

`measure-env/corpus/` — the **663-file tracked-only subset** materialized
from pinned-commit blobs (`build_env.py`): `corpus/fixtures/` (incl. tracked
`__pycache__`), `corpus/artifacts/`, every tracked `corpus/live/round-*/`
fixture, plus an initially-empty `live/runs/`. All 663 byte-equal to their
commit blobs (`env-proofs.txt`; `env-filelist.txt` lists the set; direction
checks clean both ways, `env-comm.txt` 0/0). `measure_audio.py:19` anchors
`ROOT = parents[1]` of the fixture file, so all regeneration and receipt
writes stayed inside the env — canonical writes are impossible from it.
Ten probed members/artifacts re-checked byte-equal to `6f905c3` blobs
**after** the replay (`post-replay-fixture-check.txt` — all 10 EQUAL, same
sha values r74 recorded: `777b6764…`, `325fb967…`, `6373923f…`, `fd7911a3…`,
`f073e70a…` ×2, `4bb56ddf…`, `3d2048e4…`, `b18c8170…`, `49ca24fb…`).

## Replay result — deterministic; prior rows byte-stable modulo the known classes

`rerun.py` ran **16:34:42 → 16:42:22 UTC (~7 m 40 s), 124/124 rows**
(`rerun.log`; per-command captures `out/{01..124}.{stdout,stderr}` = 248
files). Outputs: `ledger-r75-baseline.tsv`, `ledger-compare-mode.tsv`,
`ledger-compare-mismatches.txt`, `receipt-compare.tsv`,
`receipt-membership.tsv`, `semantic-compare.txt`, `compare.py` (anchor-pinned
to `6f905c3`, immune to the mid-window commit), `semantic_compare.py`,
`receipt-shas.txt`.

- **Counts by exit: 51 × exit 0 / 73 × exit 1** — committed ledger-r71 is
  50/71 on 121 rows (including **7** normal rows). Fresh 124 = committed
  mode set minus one duplicated `normal` (6 kept) plus four newer modes
  {ffprobe-transport-r71 exit 0, sndfile-transport-r72 exit 1,
  consumers-r73 exit 1, lavfsweep-r74 exit 0} — the two fork-verdict arms
  carry the +2 exit-1; vs r74's 50/73-on-123 the single added row is
  lavfsweep-r74 (exit 0).
- **Ledger compare (mode-keyed vs committed ledger-r71 @ `6f905c3`):
  120/121 MATCH** on (exit, failure-summary) — `ledger-compare-mode.tsv`.
  The single **EXIT-ONLY**: `fifo-hold-ladder-r70` — committed failsum
  carries a second chunked-flake clause (`chunked … h=0.05` band) while my
  run produced the clean distribution with the oneshot clause verbatim
  identical (`h=0.0 -> 10x blocked`). Same load-dependent band class
  documented since r70 — byte-equal to r74's finding.
- **Committed-receipt anchors: 106/121 byte-identical** (sha256 of
  `git show 6f905c3:` blob = fresh env receipt) — `receipt-compare.tsv`.
- **Fresh-receipt membership: 109/124** sha256 present in the committed
  same-mode receipt set (`receipt-membership.tsv`). Includes the decoder
  rows matching every committed counterpart.
- **15 NOT-INSET receipts:** the 13-mode **path-embedding class**
  (EQUAL-ANCHORED-TAIL on JSON leaf-walk, `semantic-compare.txt` — differing
  leaves all `corpus/`-anchored with equal post-anchor suffix and the
  `live/r75-baseline/measure-env/` infix; same 13-mode set as r68–r74, zero
  CONTENT-DIFF), **plus the two anchorless modes** — row-02 `lavfsweep-r74`
  (`ebddda25…`) and row-03 `consumers-r73` (`f6d5379a…`), committed set
  size 0 for both.
- **committed-02 `normal` anomaly (pre-existing, not new drift):** its
  anchored receipt `98f76ff9…` remains the strict superset carrying an
  inserted `ffprobe_*_r71_probe` block from an uncommitted impl variant —
  STRUCTURE-DIFF with `only-fresh=[]`, same as r74. All my fresh normal
  receipts are the canonical `8e8cdad6…`.
- **committed-03 `fifo-hold-ladder-r70`:** STRUCTURE-DIFF — committed
  receipt carries the extra chunked-band failure bucket; fresh is the clean
  canonical signature (the EXIT-ONLY ledger mismatch above).

### Anchorless rows vs canonical sibling receipts (untracked `corpus/live/runs/`)

- **lavfsweep-r74** vs 7 canonical siblings: **3 byte-EQUAL**
  (`153739783116Z`, `154034384723Z`, `154138420733Z`), **3 STRUCTURE-DIFF**
  (`153027*`, `153053*`, `153341*` — lack the `fork_kind` keys; pre-fold
  mid-flight impl variants), **1 CONTENT-DIFF** (`153635*` —
  `lavf_iss_multi.fork_kind` value differs; another mid-flight variant).
- **consumers-r73** vs 16 canonical siblings: **2 byte-EQUAL**
  (`150142232207Z`, `151240011154Z`), **7 JITTER-LEAVES** (declared
  `pacing_{instant,trickle}.wall_s` only), **5 STRUCTURE-DIFF** (early
  `1451*`–`150305*` receipts lacking `pwcat_name_axis` legs / carrying
  `stderr_tail` variants — pre-fold impl variants), **2 CONTENT-DIFF**
  (`153153*`, `154324*` — confined to
  `daemon_live.default_sink`: canonical `…SPDIF__sink.2` vs fresh
  `…SPDIF__sink`; the USB sink re-enumerated across the observed pipewire
  restart between their window and mine — daemon pids `1905/2290` at
  prior-gen capture → `1203634/1203790` now; same physical device,
  environment jitter not corpus drift).
- **Census: env `runs/` = 124 fresh + 5 prior-generation receipts = 129,
  zero extras** (`receipt-shas.txt`). All 124 ledger col-3 paths carry the
  `r75-baseline/measure-env/` infix. Canonical `corpus/live/runs/` grew
  **5,615 → 5,618** during my window (+3 sibling `consumers2-r75` receipts —
  the r75 author arm mid-flight; `runs-canonical-{before,after,added,final}
  .txt`); **zero name overlap** with my env receipts, zero canonical writes
  by me.
- Committed-ledger guard: `8d59f552…` before, after, and @`db46fba` —
  replay wrote only to scratch.

**Drift: zero.** Every receipt delta is one of the known classes
(path-embedding ×13; the ledger's own uncommitted-impl normal receipt; the
declared load-dependent ladder band; consumers wall_s jitter and the
sink-rename environment jitter; pre-fold sibling variants — no committed
anchor exists for consumers-r73 or lavfsweep-r74).

## Post-commit re-verification (r75 work commit `db46fba`, landed ~16:52 UTC)

- `git diff 6f905c3 db46fba` touches **2 paths only**:
  `corpus/fixtures/measure_audio.py` (+936/−3) and
  `reports/round-75/r75-author.md` (+174). **Zero `live/runs/` paths** — all
  5,290 committed receipt blobs byte-identical across the move by object
  identity (`postcommit-verify.txt`: full `ls-tree -r` object-id diff of
  `corpus/live/runs` between the two commits = 0 lines).
- Deletions inside `measure_audio.py` are confined to the three dispatch
  wiring lines — the exclusivity `sum()` (old :929), the `mode=` chain, and
  the `suffix=` chain — each replaced by the same line extended with
  `args.probe_consumers2_r75` / `"probe-consumers2-r75"` /
  `"-consumers2-r75"`. Insertion-only guard holds for every prior probe arm
  (same deletion class as r74's `168b165`).
- New mode wired: `--probe-consumers2-r75` — argparse `measure_audio.py:3023`,
  exclusivity `:3025`, dispatch `:3295`, mode chain `:3782`, suffix chain
  `:3802` (@`db46fba`); probe entries `consumers2_paplay_ops_entry` `:2390`,
  `consumers2_aplay_ops_entry` `:2584`, `consumers2_ffplay_ops_entry` `:2744`.
  The `consumers-r73` and `lavfsweep-r74` blocks are untouched, so all prior
  probe surfaces keep the shape my frozen-HEAD replay measured.
- **Sibling-battery counts at `db46fba`:** still no committed 124/125-row
  ledger; committed `runs/` count unchanged (5,290). Canonical untracked
  receipts now include consumers-r73 ×16, lavfsweep-r74 ×7,
  sndfile-transport-r72 ×15, ffprobe-transport-r71 ×12,
  fifo-hold-ladder-r70 ×5, consumers2-r75 ×3 (sha-identical ×3 per the
  commit message). Expected sibling battery once an r75 ledger lands = 125
  rows (consumers2-r75 newest-first at 02).
- Frozen archive validity post-move: the tar remains a faithful
  byte-receipt of `6f905c3` (immutable git object set); nothing in
  `db46fba` alters the frozen anchors.

## Toolchain + consumer-class viability (measured)

`SoX_ng v14.8.0.1`, `ffmpeg/ffprobe n9.0.1`, `python3 3.14.7` +
`numpy 2.5.3`, `libsndfile` (ctypes load ok), `pw-cat` w/ libpipewire
**1.6.8**, `mpv v0.41.0`, `pactl`: PulseAudio-on-PipeWire live, default sink
`alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink` (`toolchain.txt`).
**Environment event:** pipewire restarted inside the window — pids
`1905/2290` (prior-gen capture ~16:03Z) → `1203634/1203790` (mine ~16:34Z);
the `.2`-suffix delta on `default_sink` in the two newest canonical
consumers receipts is the visible fingerprint. Daemon stayed live
throughout; daemon-gated legs unaffected.

## Live-tree events during the window (observed, not mine)

- `6f905c3` was already HEAD at takeover; `db46fba` (r75 author work)
  committed 16:52Z by the integrator.
- `post-state.txt` (~16:44Z) caught ` M corpus/fixtures/measure_audio.py` —
  the author's +936 worktree diff was live-but-uncommitted in the tree
  during my replay. My env runs pinned `git show` blobs, so the replay
  surface was unaffected (all 124 receipts carry the env infix; 10/10
  fixture re-check EQUAL post-replay).
- +3 canonical `consumers2-r75` receipts during my window; sibling
  `corpus/live/r75-{author,boundary,critic,reviewer,scout,scribe,
  simplifier}/` scratch dirs active; `reports/round-75/` sibling reports
  (boundary/scout/scribe/author) appeared.
- Pre-existing uncommitted state persists untouched:
  ` M corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`
  (import-time regen, resolved by the `db46fba` commit) and untracked
  r71–r74 leftovers.

## Write-scope accounting

Wrote only: this report; `corpus/live/r75-baseline/` (`frozen/`
head-6f905c3.tar + manifest + sha — ignored dir per `corpus/.gitignore:4`,
receipt only, never extracted; `recovery-prior/` preservation set;
`measure-env/` 663 verified files + 129 receipt dirs; `build_env.py`,
`rerun.py`, `rerun.log`, `ledger-r75-baseline.tsv`, `out/` 248 captures,
`compare.py`, `semantic_compare.py`, `ledger-compare-mode.tsv`,
`ledger-compare-mismatches.txt`, `receipt-compare.tsv`,
`receipt-membership.tsv`, `semantic-compare.txt`, `receipt-shas.txt`,
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
- `consumers-r73` and `lavfsweep-r74` have **no committed receipt anchor**;
  sibling-receipt compares stand in (byte-EQUAL cores present for both).
- `consumers2-r75` joined the anchorless set — my battery predates its
  wiring; the next round's ordering should carry it newest-first.
- `fifo-hold-ladder-r70` remains a load-dependent band: this run landed the
  canonical stable signature; occasional EXIT-ONLY failsum drift expected.
- The consumers-r73 `daemon_live.default_sink` leaf is environment-live —
  expect CONTENT-DIFF vs siblings whenever the USB sink re-enumerates
  (observed once this round via the pipewire restart).
