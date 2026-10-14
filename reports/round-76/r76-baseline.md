# R76 baseline — frozen-HEAD replay of the 125-command battery (consumers2-r75 newest-first)

host: devin (`Linux plazir27 7.2.3-arch1-3`, `toolchain.txt`). Seat: baseline.
Frozen state = `git archive HEAD` of pre-move HEAD **`2250be9`** ("r75
report-last: 9/9 seats — AGREE all claims, ADMIT-corr (consumer breadth,
falsifications folded)"). HEAD stayed `2250be9` through the whole replay
window (17:30:43 → 17:39:33 UTC) and moved to **`d566a31`** ("r76:
capture-side consumers — pw-record/parecord/arecord/ffmpeg capture
lattice") at **18:30:53 UTC** — long after the replay completed; the
post-commit re-verification below anchors on `d566a31`. All freeze anchors
reference `2250be9` exclusively.

## Frozen archive (receipt, not materialization — never extracted)

`corpus/live/r76-baseline/frozen/head-2250be9.tar` — sha256
`e22f852a0e184f6f4ca6b428f2aaa030b45089ce6d634123ed4ebb313b466489`
(`frozen/archive-sha256.txt`), **29,039 tar members = 22,365 files + 6,674
directory entries** (`frozen/archive-manifest.txt`), exactly the
`git ls-files` count at `2250be9` (comm-diff 0 in both directions). Zero
`node_modules` members. 2,348 committed file members sit under prior seats'
tracked `measure-env/` trees (pre-w12-fold tracked content; the ignore rule
only prevents future tracking). No tar member is a live scratch dir beyond
those committed trees.

**Committed ledger:** `corpus/live/r70-author/ledger-r71.tsv`, sha256
`8d59f552e1370c5e0b50989eacff93e6f4bdf35352a31aa7121616e176579b95` / blob
`c4f5c6196f398585f55a8237ab9cbc3f34760621` — identical before the window and
after the replay (`committed-ledger-sha.{before,after}.txt`). Standing caveat
(unchanged since r73): this ledger is the r70-order battery plus a second `""`
normal — no r71–r75 family rows.

**Battery definition:** 125 commands — the r75-baseline ordering verbatim with
`--probe-consumers2-r75` (committed at `db46fba`, inside `2250be9`'s history)
inserted newest-first at position 02 (`rerun.py`, `assert len == 125`). No
committed 125-row ledger exists; r75-author carries no ledger file — this
ordering is the freshest encoding of the full committed probe surface.

## Replay vehicle — minimal verified materialization (replaces extraction)

`measure-env/corpus/` — the **663-file tracked-only subset** materialized
from pinned-commit blobs (`build_env.py`): `corpus/fixtures/` (incl. tracked
`__pycache__`), `corpus/artifacts/`, every tracked `corpus/live/round-*/`
fixture, plus an initially-empty `live/runs/`. All 663 byte-equal to their
`2250be9` blobs (`env-proofs.txt`; `env-filelist.txt` lists the set;
direction checks clean both ways, `env-comm.txt` 0/0).
`measure_audio.py:19` anchors `ROOT = parents[1]` of the fixture file, so all
regeneration and receipt writes stayed inside the env — canonical writes are
impossible from it. Ten probed members/artifacts re-checked byte-equal to
`2250be9` blobs **after** the replay (`post-replay-fixture-check.txt` — all
10 EQUAL, same sha values recorded since r74: `777b6764…`, `325fb967…`,
`6373923f…`, `fd7911a3…`, `f073e70a…` ×2, `4bb56ddf…`, `3d2048e4…`,
`b18c8170…`, `49ca24fb…`).

## Replay result — deterministic; prior rows byte-stable modulo the known classes

`rerun.py` ran **17:30:43 → 17:39:33 UTC (~8 m 50 s), 125/125 rows**
(`rerun.log`; per-command captures `out/{01..125}.{stdout,stderr}` = 250
files). Outputs: `ledger-r76-baseline.tsv`, `ledger-compare-mode.tsv`,
`ledger-compare-mismatches.txt`, `receipt-compare.tsv`,
`receipt-membership.tsv`, `semantic-compare.txt`, `compare.py` (anchor-pinned
to `2250be9`), `semantic_compare.py`, `receipt-shas.txt`.

- **Counts by exit: 52 × exit 0 / 73 × exit 1** — vs r75's 51/73-on-124 the
  single added row is consumers2-r75 at exit 0 (row-02 `none` failsum; the
  9-member × 3-consumer matrix plus three ops entries measured clean on this
  host — 29 measurement keys in the fresh receipt).
- **Ledger compare (mode-keyed vs committed ledger-r71 @ `2250be9`):
  120/121 MATCH** on (exit, failure-summary) — `ledger-compare-mode.tsv`.
  The single **EXIT-ONLY**: `fifo-hold-ladder-r70` — committed failsum
  carries a second chunked-flake clause (`h=0.05 -> 9x(exit 2, can't find
  Sun/NeXT/DEC identifier)/1x blocked`) while my run produced the clean
  distribution with the oneshot clause verbatim identical
  (`h=0.0 -> 10x blocked`). Same load-dependent band class documented since
  r70 — byte-equal to the r74/r75 finding.
- **Committed-receipt anchors: 106/121 byte-identical** (sha256 of
  `git show 2250be9:` blob = fresh env receipt) — `receipt-compare.tsv`.
- **Fresh-receipt membership: 109/125** sha256 present in the committed
  same-mode receipt set (`receipt-membership.tsv`). Includes the decoder
  rows matching every committed counterpart; all six fresh `normal`
  receipts are the canonical `8e8cdad6…` (unchanged since r66).
- **16 NOT-INSET receipts:** the 13-mode **path-embedding class**
  (EQUAL-ANCHORED-TAIL on JSON leaf-walk, `semantic-compare.txt` — differing
  leaves all `corpus/`-anchored with equal post-anchor suffix and the
  `live/r76-baseline/measure-env/` infix; same 13-mode set as r68–r75, zero
  CONTENT-DIFF), **plus the three anchorless modes** — row-02
  `consumers2-r75` (`4ca81e4f…`), row-03 `lavfsweep-r74` (`ebddda25…` —
  byte-identical sha to r75's fresh), row-04 `consumers-r73` (`8c77c3e2…`);
  committed set size 0 for all three.
- **committed-02 `normal` anomaly (pre-existing, not new drift):** its
  anchored receipt `98f76ff9…` remains the strict superset carrying an
  inserted `ffprobe_*_r71_probe` block from an uncommitted impl variant —
  STRUCTURE-DIFF with `only-fresh=[]`, same as r74/r75.
- **committed-03 `fifo-hold-ladder-r70`:** STRUCTURE-DIFF — committed
  receipt carries the extra chunked-band failure bucket; fresh is the clean
  canonical signature (the EXIT-ONLY ledger mismatch above).

### Anchorless rows vs canonical sibling receipts (untracked `corpus/live/runs/`)

- **lavfsweep-r74** vs 7 canonical siblings: **3 byte-EQUAL**
  (`153739783116Z`, `154034384723Z`, `154138420733Z`), **3 STRUCTURE-DIFF**
  (`153027*`, `153053*`, `153341*` — lack the `fork_kind` keys; pre-fold
  mid-flight impl variants), **1 CONTENT-DIFF** (`153635*` —
  `lavf_iss_multi.fork_kind` value differs). Identical partition to r75;
  fresh receipt is byte-identical to r75's fresh (`ebddda25…`).
- **consumers-r73** vs 16 canonical siblings: **0 byte-EQUAL** this round
  (r75 landed 2 — the `150142*`/`151240*` pair now classify JITTER-LEAVES,
  i.e. only the declared `wall_s` clocks differ), **9 JITTER-LEAVES**
  (`pacing_{instant,trickle}.wall_s`, `daemon_gate.wall_s` only),
  **5 STRUCTURE-DIFF** (early `1451*`–`150305*` receipts lacking
  `pwcat_name_axis` legs / carrying `stderr_tail` variants — pre-fold impl
  variants), **2 CONTENT-DIFF** (`153153*`, `154324*` — confined to
  `daemon_live.default_sink`: canonical `…SPDIF__sink.2` vs fresh
  `…SPDIF__sink`; the USB sink re-enumeration environment jitter documented
  at r75 — daemon pids are the `1203634/1203790` pair throughout my window,
  no restart observed this round).
- **consumers2-r75** vs 7 canonical siblings: **0 byte-EQUAL, 6
  STRUCTURE-DIFF, 1 CONTENT-DIFF.** All seven canonical siblings are
  r75-window mid-flight impl variants of a family that was itself folded
  twice in-flight (`5f60747` honest-label/vacuity/tail-scrub folds land in
  my anchor's history): five siblings carry the pre-fold `sigterm_immune`
  key names where fresh carries `alive_after_term1` plus the added
  `viable_legs` legs; `171455*` additionally carries `failures[]` entries
  the folded impl no longer emits; `172034*` differs only inside the
  `aplay … file.stderr_tail` scrub window. No committed anchor exists —
  the folded impl at `2250be9` is the reference and my receipt is its
  first post-fold capture.
- **Census: env `runs/` = 125 fresh receipts, zero extras**
  (`receipt-shas.txt`). All 125 ledger col-3 paths carry the
  `r76-baseline/measure-env/` infix. Canonical `corpus/live/runs/` held at
  **5,622** through the replay (+0, `runs-canonical-{before,after,
  added}.txt`); post-replay growth during the commit watch is recorded in
  `runs-canonical-final.txt` and "Live-tree events" below. **Zero name
  overlap** with my env receipts, zero canonical writes by me.
- Committed-ledger guard: `8d59f552…`/`c4f5c619…` before and after —
  replay wrote only to scratch.

**Drift: zero.** Every receipt delta is one of the known classes
(path-embedding ×13; the ledger's own uncommitted-impl normal receipt; the
declared load-dependent ladder band; consumers wall_s jitter and the
sink-rename environment jitter; pre/post-fold sibling variants — no
committed anchor exists for consumers-r73, lavfsweep-r74, or
consumers2-r75).

## Post-commit re-verification (r76 work commit `d566a31`, landed 18:30:53 UTC)

- `git diff 2250be9 d566a31` touches **2 paths only**:
  `corpus/fixtures/measure_audio.py` (+1150/−3) and
  `reports/round-76/r76-author.md` (+241). **Zero `live/runs/` paths** — all
  5,290 committed receipt blobs byte-identical across the move by object
  identity (`postcommit-verify.txt`: full `ls-tree -r` object-id diff of
  `corpus/live/runs` between the two commits = 0 lines).
- Deletions inside `measure_audio.py` are confined to the three dispatch
  wiring lines — the exclusivity `sum()` (old :3062), the `mode=` chain,
  and the `suffix=` chain — each replaced by the same line extended with
  `args.probe_capture_r76` / `"probe-capture-r76"` / `"-capture-r76"`.
  Insertion-only guard holds for every prior probe arm (same deletion
  class as r74's `168b165` and r75's `db46fba`).
- New mode wired: `--probe-capture-r76` — argparse `measure_audio.py:4184`,
  exclusivity `:4186`, dispatch `:4477`, mode chain `:4963`, suffix chain
  `:4983` (@`d566a31`); probe entries `capture_gate_r76_entry` `:3343`,
  `capture_bounded_r76_entry` `:3458`, `capture_sever_r76_entry` `:3633`,
  `capture_name_axis_r76_entry` `:3764`, `capture_device_axis_r76_entry`
  `:3859`, `capture_roundtrip_r76_entry` `:3916`. The `consumers2-r75`,
  `lavfsweep-r74`, and `consumers-r73` blocks are untouched, so all prior
  probe surfaces keep the shape my frozen-HEAD replay measured.
- **Sibling-battery counts at `d566a31`:** still no committed 126-row
  ledger; committed `runs/` count unchanged (5,290). Canonical untracked
  receipts now include capture-r76 ×10 (all landed 18:13–18:34Z during my
  watch window), consumers2-r75 ×7, consumers-r73 ×16, lavfsweep-r74 ×7,
  sndfile-transport-r72 ×18, ffprobe-transport-r71 ×15,
  fifo-hold-ladder-r70 ×14. Expected sibling battery once an r76 ledger
  lands = 126 rows (capture-r76 newest-first at 02).
- Frozen archive validity post-move: the tar remains a faithful
  byte-receipt of `2250be9` (immutable git object set); nothing in
  `d566a31` alters the frozen anchors.

## Toolchain + consumer-class viability (measured)

`SoX_ng v14.8.0.1`, `ffmpeg/ffprobe n9.0.1`, `python3 3.14.7` +
`numpy 2.5.3`, `libsndfile` (ctypes load ok), `pw-cat` w/ libpipewire
**1.6.8**, `mpv v0.41.0`, `pactl`: PulseAudio-on-PipeWire live, default sink
`alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink` (`toolchain.txt`).
PipeWire daemon pids `1203634/1203790` throughout — the same pair r75's
post-restart window recorded; **no restart inside my window**, and the fresh
consumers-r73 receipt confirms `.2`-less `default_sink` naming persists.

## Live-tree events during the window (observed, not mine)

- `2250be9` held as HEAD for the entire replay; `d566a31` (r76 author work)
  committed 18:30:53Z by the integrator.
- `post-state.txt` (~17:44Z) caught ` M corpus/fixtures/measure_audio.py` —
  the author's +1150 worktree diff was live-but-uncommitted during and after
  my replay (first observed as a +3 imports-only partial mid-window, grown
  to +1116/−3 by ~18:10Z). My env runs pinned `git show` blobs, so the
  replay surface was unaffected (all 125 receipts carry the env infix;
  10/10 fixture re-check EQUAL post-replay).
- Canonical `corpus/live/runs/` held at 5,622 through the replay itself,
  then grew **5,622 → 5,633** during the post-replay watch (+10 sibling
  `capture-r76` receipts — the r76 author arm mid-flight — plus one
  `failing` sibling receipt at 18:26Z;
  `runs-canonical-{before,after,added,final}.txt`); **zero name overlap**
  with my env receipts, zero canonical writes by me.
- Sibling scratch dirs `corpus/live/r76-{author,boundary,scout,scribe}/`
  active; sibling reports `reports/round-76/{boundary,scout,scribe}.md`
  landed during the window; `r76-author.md` landed inside `d566a31`.
- Pre-existing uncommitted state persists untouched: untracked r71–r75
  leftovers (`git status` set enumerated in `pre-state.txt`/`post-state.txt`).

## Write-scope accounting

Wrote only: this report; `corpus/live/r76-baseline/` (`frozen/`
head-2250be9.tar + manifest + sha — ignored dir per `corpus/.gitignore`,
receipt only, never extracted; `measure-env/` 663 verified files + 125
receipt dirs; `build_env.py`, `rerun.py`, `rerun.log`,
`ledger-r76-baseline.tsv`, `out/` 250 captures, `compare.py`,
`semantic_compare.py`, `postcommit_verify.py`,
`ledger-compare-mode.tsv`, `ledger-compare-mismatches.txt`,
`receipt-compare.tsv`, `receipt-membership.tsv`, `semantic-compare.txt`,
`receipt-shas.txt`, `env-filelist.txt`, `env-proofs.txt`, `env-comm.txt`,
`post-replay-fixture-check.txt`,
`committed-ledger-sha.{before,after}.txt`, `postcommit-verify.txt` (on
commit), `toolchain.txt`, `pre-state.txt`, `post-state.txt`,
`runs-canonical-{before,after,added,final}.txt`, `head-moved.txt`). No
canonical `corpus/live/runs/` writes, no tracked-file edits, no commits, no
pushes. Leaf seat — no dispatch performed.

## Residual gaps

- The 13 path-embedding receipts can never raw-match off the canonical
  path; anchored-tail JSON compare is the strongest displaced-tree check
  (unchanged since r68).
- Committed ledger-r71 row-02 anchors a receipt no frozen tree can
  reproduce (uncommitted-impl artifact); flagged, not correctable from this
  seat.
- `consumers-r73`, `lavfsweep-r74`, and `consumers2-r75` have **no committed
  receipt anchor**; sibling-receipt compares stand in (byte-EQUAL cores
  present for lavfsweep ×3; consumers2's seven canonical siblings are all
  mid-flight variants of the twice-folded impl — my receipt is the first
  post-fold capture and becomes the next round's sibling reference).
- consumers-r73 byte-EQUAL count dropped 2 → 0 this round purely on the
  declared `wall_s` jitter class — no new divergence class.
- `fifo-hold-ladder-r70` remains a load-dependent band: this run landed the
  canonical stable signature; occasional EXIT-ONLY failsum drift expected.
- The consumers-r73 `daemon_live.default_sink` leaf is environment-live —
  expect CONTENT-DIFF vs `.2`-suffixed siblings whenever the USB sink
  re-enumerates (observed at r75 via pipewire restart; none this round).
