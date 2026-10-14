# R70 baseline — frozen-HEAD replay of the 119-command r69 ledger + fifo_writer_hold_s measured-bound ladder

host: devin (`Linux plazir27 7.2.3-arch1-3`, `toolchain.txt`). Seat: baseline.
Frozen state = `git archive HEAD` of canonical HEAD **`939fe47`** ("corpus
ignore: close the non-tree snapshot side-channel (xsentinel w8-F4)"). HEAD was
`939fe47` at dispatch, at archive time (12:04 UTC), and at env-verification
time (12:05 UTC); a sibling commit moved HEAD to `cded2dd` ("corpus ignore:
cover *tree* dirs at any depth", `corpus/.gitignore` +3 lines only) at
**12:08:26 UTC, mid-replay** — one mid-window commit this round, disclosed
below and fully absorbed by the frozen-commit anchoring.

**Convention (w8 seat rule, carried from r69):** the archive is a receipt, not
a materialization. `corpus/live/r70-baseline/frozen/head-939fe47.tar` —
278,548,480 B, sha256
`fa5ece80139096b6dc9f45985451bd4dabc1ea16facae520cf3316f5725adaa5`
(`frozen/archive-sha256.txt`), **26,107 tar members = 20,160 files + 5,947
directory entries** (`frozen/archive-manifest.txt`), exactly the
`git ls-files` count at `939fe47`. Zero `node_modules` members; **zero**
members under any `corpus/live/r*-baseline/{frozen,tree,head,snapshot,base,
*extract*}/` — the gitignore set keeps populated snapshot trees untracked.
**The archive was never extracted.**

**Committed ledger:** `corpus/live/r69-author/ledger-r69.tsv` (committed at
`30bb86d` "r69: extension-suffix sweep … ledger 114->119"), **119 rows** — the
prior 114 plus five `transport-extsuffix-*-r69` modes at positions 02–06.
Secondary committed reference: `corpus/live/r69-verifier/ledger-r69v.tsv`
(same 119-mode order, identical cols 1/2/4 — verified 0-byte diff). Both
sha256'd identical as worktree file and `git show 939fe47:` blob, before and
after my window (`74ed54b3…` / `99cb2d66…`, `committed-ledger-sha.before.txt`,
`post-state.txt`).

Repo-path note: the brief's line 6 names `~/Projects/prymeagnt/audio`; that
worktree resolves `.shokunin/audio` via symlink into this canonical repo
(`/home/vgpnk/Projects/shokunin/audio-shokunin`). All scratch/report writes
land in the canonical repo, as in r62–r69.

## Replay vehicle — minimal verified materialization (replaces extraction)

The seat rule forbids extracting the archive, and `measure_audio.py:17`
anchors `ROOT = Path(__file__).resolve().parents[1]`, so the replay ran
against `corpus/live/r70-baseline/measure-env/corpus/` — a **657-file
tracked-only subset** copied from the clean worktree (`git status` showed
zero modified tracked files at copy time, ~12:05 UTC): `corpus/fixtures/`
(measure_audio.py + build_artifacts.py, both `__file__`-anchored so their
regeneration writes stay in-env), `corpus/artifacts/`, and every
`corpus/live/round-*/` fixture path the 119 modes read, plus an empty
`live/runs/`. **Every copied file byte-equals its `git show 939fe47:` blob —
657/657 EQUAL** (`env-proofs.txt`; env-filelist.txt lists the set). The
input-set direction also checks clean under the brief's `comm -23` form:
`comm -23 <(find measure-env -type f -not -path '*/live/runs/*' | …) <(git ls-files)`
→ **0 untracked input members**; the reverse comm → **0 tracked inputs
missing**. (`measure-env/corpus/live/runs/` holds only my 119 fresh receipts —
outputs, not members.) Same isolation the r62–r69 frozen trees provided, with
the snapshot receipt (the tar) separated from the runnable surface.

`build_artifacts.py` regenerates fixture wavs under env's ROOT — all probed
members stayed byte-identical to HEAD post-replay
(`post-replay-fixture-check.txt`: `posttable_nomatch.wav` `6373923f…`,
`txw_piperefuse.wav` `fd7911a3…`, `pair_preempt_act.wav` `cf5edecc…`,
`pair_preempt_both.wav` `a37adc7c…`, `pair_dec_hcom.wav` `325fb967…`,
`pair_dec_act.wav` `777b6764…`, `extsuffix_nomatch.wav` `f073e70a…`,
`extsuffix_nomatch.snd` `f073e70a…` — identical bytes under two suffixes, the
r69 point —, `ui.wav` `4bb56ddf…`, `stem_layer_third.wav` `3d2048e4…`).

## Replay result — deterministic, exact

`rerun.py` (imports `MODES` verbatim from the committed
`r69-author/run_ledger.py`, `assert len == 119`; serial; per-command captures
to `out/{01..119}.{stdout,stderr}` = 238 files) ran **12:05:30→12:09:43 UTC
(~4 min 13 s), exit 0** (`rerun.log`). Outputs: `ledger-r70-baseline.tsv`,
`runs-env-before.txt` (0) / `runs-env.txt` (119), `committed-shas.tsv`,
`receipt-compare.tsv`, `semantic-compare.tsv`, `compare.py`,
`semantic_compare.py`, `frozen/archive-manifest.txt`,
`frozen/archive-sha256.txt`, `committed-ledger-sha.before.txt`,
`pre-state.txt`, `post-state.txt`, `env-proofs.txt`,
`post-replay-fixture-check.txt`, `toolchain.txt`,
`runs-canonical-{before,after,added}.txt`,
`ledger-cols-diff-r69-{author,verifier}.txt` (both 0 bytes).

- **Counts by exit: 49 × exit 0 / 70 × exit 1** — matches committed
  `ledger-r69.tsv` exactly (the r69-verifier ledger agrees identically) and
  the brief's declared expectation.
- **119/119 rows identical** to committed on (idx, exit, failure-summary) —
  `diff` over TSV cols 1,2,4 → empty against **both** committed r69 ledgers
  (`ledger-cols-diff-*.txt`, both 0 bytes).
- **Census: env `runs/` 0 → 119 (+119, zero extras).** All 119 fresh receipts
  resolve under `r70-baseline/measure-env/corpus/live/runs/` (stamps
  `20261014T120530…T120943`); grep-verified 119/119 col-3 paths carry the env
  infix; comm -12 vs the canonical runs listing → **0 name overlap**. **Zero
  writes to canonical `corpus/live/runs/`** — the `__file__` anchor makes
  canonical writes impossible from the env.
- **Committed-receipt anchor: 119/119** committed receipts named in
  `ledger-r69.tsv` col 3 are byte-identical to their `git show 939fe47:`
  blobs (`compare.py` `tracked-committed=119/119`), anchored on the frozen
  commit explicitly so the mid-window HEAD move cannot skew the anchor.
- **Receipts: 106/119 byte-identical** (sha256) to committed counterparts —
  including all ten r67+r68+r69 transport rows (02–18), whose receipts carry
  no absolute paths by design; **2 normalized** (rows 36
  `ui-route-act-00-r63`, 114 `--probe-invalid`): absolute paths embedded in
  full stderr leaves — the env→canonical infix rewrite
  (`corpus/live/r70-baseline/measure-env/corpus/` → `corpus/`) restores the
  committed sha256 exactly; **11 raw-DIFFERS, all the known truncation
  class** — rows 21–22 (`ui-lengate-gsrt-{24,25}-r66`), 24
  (`ui-lengate-hcom-132-r66`), 25–28 (`ui-preempt-{act,gsrt,hcom,both}-r65`),
  31–34 (`ui-extensible-valid-{24,25,56,57}-r64`): `tail[-1][-160:]` cuts the
  embedded absolute path mid-token at the leaf head, so no prefix rewrite can
  sha-match; anchored suffix after the last `corpus/` is byte-identical.
  Same 13-mode differing set as r68/r69, shifted +5 by the newest-first
  ledger convention.
- JSON-level comparison (`semantic_compare.py`): identical structure on all
  119 rows; every differing string leaf is `corpus/`-anchored in both
  receipts with equal post-anchor suffix and carries the
  `live/r70-baseline/measure-env/` infix — **106 EQUAL, 13 EQUAL-MOD-PATHS,
  0 CONTENT-DIFF, 0 STRUCTURE-DIFF** (`semantic-compare.tsv`). All differing
  leaves are `sox_{bridge,native,stat,}_stderr` / `invalid_probes[1].detail.
  stderr` — the path-embedding class only.
- Row-01 normal receipt sha `8e8cdad6cc3c356d07c463498f4759b8d73e73935cf591
  d117732f09ffaffb1b` — identical fresh and committed; the same value the
  r66, r67, r68 and r69 baselines recorded for the opening row.
- Committed-ledger guard: `ledger-r69.tsv` sha256 `74ed54b3…` and verifier
  `99cb2d66…` identical before and after my run — the replay writes only to
  scratch.
- **Drift: zero** — all deltas are explained by the known path-embedding
  convention.

Toolchain: `SoX_ng v14.8.0.1`, `ffmpeg/ffprobe n9.0.1`, `python3 3.14.7` +
`numpy 2.5.3` — unchanged from the r63–r69 declared set.

## Axis-move — `fifo_writer_hold_s` is a measured bound, not a point constant

The declared r70 claim: a minimum stable hold h* < 1.0 s exists and is
rep-stable on this host; OR the verdict is binary on writer-attached-at-open-#2
(h*=0 with a correctly blocking writer). The ladder ran both arms against the
`dec_act` member (`corpus/live/round-66/pair_dec_act.wav`, 600 B — the arm that
needs the ffmpeg bridge's second open), through the identical verdict path the
ledger uses (`transport_leg` imported from the verified env
`measure_audio.py`; `sox -V6 <fifo> -n stat`, 10 s arm timeout).
`hold_ladder.py` → `hold-ladder-reps.tsv` (70 reps) + `hold-ladder.json`
(the receipt-shaped per-hold distributions — `hold_ladder` groups, not a
point pin).

### hold_ladder groups — dec_act fifo arm, 10 reps/cell

| feed | hold_s | reps | verdict distribution | leg wall |
|---|---|---|---|---|
| oneshot | 0 | 10 | **10× blocked: no verdict within 10 s** (exit=None; detection still `act`/ffmpeg — the arm dies inside open #2) | 10.001–10.011 s |
| oneshot | 0.05 | 10 | **10× exit 2, "can't find Sun/NeXT/DEC identifier"** (act/ffmpeg) — the committed verdict | 0.054 s |
| oneshot | 0.2 | 10 | 10× exit 2, same verdict | 0.204–0.205 s |
| oneshot | 0.5 | 10 | 10× exit 2, same verdict | 0.504–0.505 s |
| oneshot | 1.0 | 10 | 10× exit 2, same verdict — **identical signature to the committed r69 receipt's fifo_path arm** | 1.004–1.005 s |
| oneshot | 2.0 | 10 | 10× exit 2, same verdict | 2.004–2.005 s |
| chunked | 0 | 10 | **10× exit 2, same verdict** — 10×60 B paced ~0.1 s apart (~1.0 s attached-via-feed), zero post-write linger | 1.005–1.006 s |

The leg wall-time is `hold + ~4.4 ms` in every stable cell: reader-2's post-open
read parks until writer detach delivers EOF; the verdict content is decided by
attachment, the clock by the hold.

### Mechanism, observed directly (`open2_strace_probe.py` → `open2-strace.txt`)

`strace -f -ttt -e trace=%file` on the same leg:

- **hold=0.05**: writer open @5.6 ms, close @55.7 ms; bridge **open #2
  (`openat(fifo, O_RDONLY)`, child pid) @33.3 ms → `= 3`** — writer attached
  at open #2 by a ~22 ms margin. Deterministic verdict.
- **hold=0**: writer open+close @5.3 ms; bridge **open #2 @32.2 ms, never
  returns** (no `= N` in the trace) — no writer attached → open #2 parks
  forever; sox still blocked at the 12 s probe cutoff (and the ledger arm's
  own 10 s timeout is what turns this into the recorded `blocked:` verdict).

So the detach→open-#2 gap on this host is ~28–33 ms, and the predicate is
exactly binary: **writer attached when the bridge fires open #2**.

### Resolution of the declared claim — both arms measured true

- **(a) h* < 1.0 s exists and is rep-stable.** Smallest laddered stable hold:
  **0.05 s → 10/10 au-magic**; h=0 → **0/10** (10/10 deterministic block
  under this harness). h* therefore sits in (0, 0.05] s — i.e., the real
  bound is the ~33 ms detach→open-#2 gap, not a magic number. The pinned
  1.0 s is ~30× that gap: conservative, rep-stable (10/10 here, and
  byte-stable across the r67–r70 replays), but **not** a measured minimum.
- **(b) the verdict IS binary on writer-attached-at-open-#2.** The
  chunked-feed variant carries attachment through the feed itself (~1.0 s
  pacing window, 10×60 B @ 0.1 s): at **hold = 0** it is 10/10 stable
  au-magic — **h*=0 with a correctly pacing writer**, as claimed. Attachment
  is the invariant; the post-write hold is only one way to span the gap.
- r67-author cross-check: my shell-side bare one-shot replication
  (`(cat pair_dec_act.wav > fifo &) ; timeout 10 sox …`,
  `shell-oneshot-h0-rep{1..5}.log`) gives **5/5 exit 2 au-magic** — the
  author's exact observation — while the python-threaded writer at h=0 gives
  **10/10 blocks**. Same binary predicate, opposite race outcome by harness:
  under `cat`, the writer's fd teardown lands just past open #2; under the
  python writer the close lands ~28 ms before it. That variance IS the
  measurement: h=0 is never a protocol, and 1.0 s was bought exactly because
  the gap is harness-timing-dependent.

**Reported as data, not a pin:** `fifo_writer_hold_s=1.0` is now a measured
conservative bound (bound ≈ 33 ms; stable from ≥0.05 s oneshot, or h*=0 under
an attachment-spanning feed). Lowering it or restructuring the feed is the
author lane's call; the sibling's in-flight `--probe-fifo-hold-ladder-r70`
work (uncommitted ` M corpus/fixtures/measure_audio.py`, same
`{0, .05, .2, .5, 1, 2}`×10 grid + chunked variant with 100 B/0.05 s
constants) will land its own numbers — this lane's independent ladder is
consistent with that design.

## Live-tree events during the window (observed, not mine)

- **Mid-window commit**: HEAD `939fe47` → `cded2dd` at 12:08:26 UTC (during
  my 12:05:30→12:09:43 replay). Diff = `corpus/.gitignore` +3 lines
  (`live/**/*tree*/` — xsentinel w9; the commit message credits "r70-baseline
  read-side check" from a sibling). Not a replay input; the frozen anchor
  (939fe47) and env proofs are unaffected.
- Sibling r70 lanes mid-flight: untracked `corpus/live/r70-{critic,scribe,
  simplifier}/` dirs plus this lane's `r70-baseline/`.
- Canonical `corpus/live/runs/` grew 4,972 → 5,057 during my replay window
  (+85): a sibling lane's live r69-ledger replay landing canonical receipts
  (`runs-canonical-added.txt`; names stamped 120500–121xxxZ). **Zero name
  overlap** with my 119 env receipts; none written by this replay.
- Uncommitted sibling edit: ` M corpus/fixtures/measure_audio.py`
  (`09d426b5…` → `72eee353…` — the r70 ladder work above). My replay consumed
  only the env copy, verified `09d426b5…` = `git show 939fe47:` blob =
  `git show cded2dd:` blob both before and after (`env-proofs.txt`,
  `post-replay-fixture-check.txt`); the mid-window modification cannot have
  skewed any receipt — this is the isolation the env exists for.

## Write-scope accounting

Wrote only: this report; `corpus/live/r70-baseline/` (`frozen/` holding the
archive + manifest + sha only — no extraction —, `measure-env/` (657 verified
HEAD-equal files + the 119 fresh receipt dirs), `rerun.py`, `rerun.log`,
`ledger-r70-baseline.tsv`, `out/` (238 captures), the census/hash/diff tables
listed above, `hold_ladder.py`, `hold-ladder.{log,json}`,
`hold-ladder-reps.tsv`, `open2_strace_probe.py`, `open2-strace.txt`,
`shell-oneshot-h0-rep{1..5}.log`, `env-filelist.txt`, `env-proofs.txt`,
`post-replay-fixture-check.txt`, `toolchain.txt`, `pre-state.txt`,
`post-state.txt`). No canonical `corpus/live/runs/` writes, no tracked-file
edits, no commits, no pushes. Leaf seat — no dispatch performed.

## Residual gaps

- Path-embedded receipts (rows 21–22, 24–28, 31–34, 36, 114) can never be
  raw-byte-identical off the canonical path; 11 of the 13 truncate the path
  mid-token at the leaf head, so anchor-level JSON comparison is the
  strongest check available in a displaced tree — unchanged from r68/r69.
- `measure-env/` is a minimal materialization, not a full snapshot: it
  carries the 657 tracked files the replay surface reads. The full-fidelity
  proof of HEAD is the tar in `frozen/` (reproducible byte-identically from
  `939fe47`), not the env.
- The ladder's h* is host-bound: the ~33 ms detach→open-#2 gap is measured on
  this host under this harness; a slower host could widen it. The claim's
  structural half (attachment-at-open-#2, chunked h=0 → 10/10) is
  host-independent by construction and is the stronger pin.
- The sibling live replay filling canonical `corpus/live/runs/` is another
  lane's evidence path; canonical census numbers here are a snapshot of
  ~12:10 UTC, and the sibling's uncommitted worktree edits will move those
  files' shas once the parent integrates.
