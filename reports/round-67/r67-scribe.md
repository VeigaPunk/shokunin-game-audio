# R67 scribe — TRANSPORT axis independently re-derived: fork set {5 gsrt/act-detected members} reproduced verbatim; decode-level gsrt fork (88/11,076 on pipe) demonstrated on untracked carriers; bare-fifo HANG + held-writer au-magic both cells observed

Seat: **scribe** (leaf, report-only). Host: devin (`/usr/bin/sox` = SoX_ng
v14.8.0.1 USING_FFMPEG build — observed in `-V4` log headers this session;
ffmpeg/ffprobe n9.0.1; python 3.14.7). Canonical repo
`/home/vgpnk/Projects/shokunin/audio-shokunin`; the brief's line-6 worktree
`~/Projects/prymeagnt/audio` resolves `.shokunin/audio` via symlink into the
canonical repo (same note as r67-baseline). Scratch
`corpus/live/r67-scribe/`; this file is the only report path written.

Axis-move (verbatim, from the brief): *"pin TRANSPORT as a measured
first-class axis of the autodetect ledger: r65/r66 established that fd
seekability and pipe transport silently fork outcomes (gsrt decodes 88
samples on pipe vs premature EOF on file; the stdin ffmpeg bridge is
structurally dead; txw/smp readers refuse pipes outright) yet NO receipt
field records transport. Declared falsifiable claim: at least one tracked
member's verdict forks on transport (gsrt does — file vs pipe); the set of
transport-forking members is exactly measurable. Land an additive transport
arm on measure_audio.py (per-member {file, stdin-pipe, redirected-fd,
fifo-path} detection+decode verdict matrix over the existing fixture set —
or the sharpest discriminating subset with justification) recording
transport explicitly in the ledger/receipt shape; all 102 prior ledger rows
+ receipts byte-stable."*

## Prior-work disposition (a prior instance of this seat died mid-run — verified and extended, not restarted)

State found in `corpus/live/r67-scribe/` at this session's start:

- `run_transport.py` (177 lines): own four-transport harness — `file` /
  `pipe` (`cat | sox -`) / `redir` (`sox - < f`) / `fifo` (named fifo,
  one-shot `cat` writer), each leg `sox -V4 … -n stat` in its own process
  group with a 30 s cap and `killpg` teardown.
- `runs/transport-matrix.tsv` (69 lines = header + 68 rows): 17 fixtures ×
  4 transports — all 10 tracked autodetect members + `ui.wav` control +
  `pair_route_84.wav` + 5 r66-boundary carriers.
- `runs/logs/*.log`: 68 verbatim `-V4` per-leg captures.
- `probes/` (empty dir — prior instance never populated it; left as is).

**Reuse verification performed this session:**

- `git diff` vs commit `366fcc1` (which swept a mid-run snapshot of this
  scratch dir): the committed `run_transport.py` held `wr.close()` inside
  the `finally` (parent's fifo write-end stayed open during `communicate()`
  → masked the true EOF semantics); the working-tree version moves
  `wr.close()` immediately after the `cat` spawn — the fix. The `M`-state
  log diffs are `start-up time` jitter only (e.g. `8.4e-05`→`8.5e-05`), i.e.
  the prior instance re-ran the matrix after the fix; the TSV on disk is the
  post-fix matrix.
- Spot re-verification of recorded verdicts against the retained full `-V4`
  logs: every `file`/`fifo` tail that the TSV truncates mid-path resolves to
  the correct verbatim FAIL message in the log (e.g.
  `pair_preempt_gsrt.wav.fifo.log` → `invalid format for this file type`;
  `pair_lengate_gsrt_25.wav.fifo.log` → `invalid/missing file name in
  header`). The TSV `tail` column is capped at 100 chars — a cosmetic
  truncation in *my own scratch*; the logs carry the untruncated strings.

**Extension executed this session** (`run_transport_ext.py`, own
construction — 31 legs → `runs/transport-matrix-ext.tsv` + logs):

1. `fifo_hold` transport: parent opens the fifo `O_RDWR` before sox starts
   (a writer is always attached → the bridge's second `open()` can never
   block), writes the payload once, polls `FIONREAD` until the pipe buffer
   drains or sox exits, then closes → deterministic EOF. No timing constant;
   the writer-close is evidence-driven. Distinct protocol from the landed
   arm's pinned 1.0 s linger — same target cell.
2. Decode-fork carriers the tracked member set lacks: the r65-critic 600-B
   `D2_gsrt{ULAW,ALAW}+act.wav` pair (sha `bf60b294…`/`063d320a…` — the
   literal "88 samples" lineage) and r65-boundary `coll_gsrt_{alaw,g726}.wav`
   + `coll_act_base.wav` (11,588 B), all tracked files, read-only.
3. `fifo_hold` re-run on the 3 act-routed fixtures in my matrix + gsrt/hcom/
   wav controls.

## Independent-derivation results (my own constructions and runs)

### Fork map on the tracked autodetect family — byte-for-byte the author's partition

| fixture | detected | file | stdin pipe | redirected fd | fifo (bare writer) | fifo_hold (O_RDWR + drain-close) |
|---|---|---|---|---|---|---|
| `pair_preempt_act.wav` ≡ `pair_route_84.wav` ≡ `coll_act_base.wav` (sha `cf5edecc…`) | act | decode 3839 | au-magic fail | `premature EOF` | **HANG** ≥30 s (killpg) | au-magic fail |
| `pair_dec_act.wav` (sha `777b6764…`) | act | decode 278 | au-magic fail | `premature EOF` | **HANG** ≥30 s | au-magic fail |
| `pair_preempt_gsrt.wav` ≡ `coll_gsrt_g726.wav` (sha `477bd371…`) | gsrt | `premature EOF` | `invalid format for this file type` | `premature EOF` | `invalid format…` | `invalid format…` |
| `pair_preempt_both.wav` | gsrt | `premature EOF` | `invalid format…` | `premature EOF` | `invalid format…` | — |
| `pair_lengate_gsrt_25.wav` | gsrt | `premature EOF` | `invalid/missing file name in header` | `premature EOF` | `invalid/missing…` | — |
| `pair_preempt_hcom.wav` | hcom | `bad compression type` ×4 (+invariant under fifo_hold on the class — preempt_hcom not re-run; `pair_dec_hcom` x2 transports confirm) | | | | |
| `pair_dec_hcom.wav` | hcom | decode 9 | decode 9 | decode 9 | decode 9 | decode 9 |
| `pair_lengate_gsrt_24.wav` | wav | `fmt chunk not found` ×4 | | | | |
| `pair_lengate_hcom_131.wav` | wav | decode 43 ×4 | | | | |
| `pair_lengate_hcom_132.wav` | hcom | `premature EOF` ×4 | | | | |
| `artifacts/ui.wav` | wav | decode 5760 ×4 (+fifo_hold 5760) | | | | |

"au-magic fail" = `can't find Sun/NeXT/DEC identifier`, exit 2. All FAIL
strings extracted verbatim from `runs/logs/*.log`.

Under the landed signature `(detected, route, exit, samples, error)` the
fork set on my own matrix = **{preempt_act, preempt_gsrt, preempt_both,
dec_act, lengate_gsrt_25}** — exactly the author's 5/10; the hcom- and
wav-detected members are transport-invariant. Detection (`detected file
format type`) is **identical across all five transport legs on all 22
fixture rows** in my matrix — every fork is decode-stage, matching the
author/verifier/critic claim.

### The decode-level gsrt fork — reproduced on the untracked carriers

| fixture | file | pipe | redir | fifo | fifo_hold |
|---|---|---|---|---|---|
| `D2_gsrtULAW+act.wav` (600 B) | gsrt `premature EOF` | **gsrt decode 88, exit 0** | `premature EOF` | **decode 88** | **decode 88** |
| `D2b_gsrtALAW+act.wav` (600 B) | gsrt `premature EOF` | **gsrt decode 88, exit 0** | `premature EOF` | **decode 88** | **decode 88** |
| `coll_gsrt_alaw.wav` (11,588 B) | gsrt `premature EOF` | **gsrt decode 11,076, exit 0** | `premature EOF` | **decode 11,076** | **decode 11,076** |

This is the brief's parenthetical literally: the same byte stream yields
`premature EOF` on seekable transports and a successful decode on
non-seekable ones — because the `file_size >= 2 && ft->seekable` checksum
scan (gsrt.c:88, corroborative) reads `RIFF`@0 as BE `0x52494646` ≈ 1.38 G
samples on a seekable fd and is skipped entirely on a non-seekable one. On
the *tracked* gsrt members the encoding byte is G726 → the reader dies at
`invalid format for this file type` on the same non-seekable arms — same
fork, die-position-level instead of decode-level (author, critic, and
simplifier all record this distinction; my matrix confirms it on the
byte-identical `coll_gsrt_g726` ≡ `pair_preempt_gsrt`).

### fifo + act is a two-cell protocol-bivalent verdict

- **Bare one-shot writer** (my `fifo` arm): all three act fixtures
  (`pair_route_84`, `pair_preempt_act`, `pair_dec_act`, `coll_act_base`)
  recorded `SCRIBE-TIMEOUT-30s-killpg` — sox detects act, the popen'd
  ffmpeg child re-opens the fifo by name (open #2), and with the writer
  already gone that `open()` blocks indefinitely. Independent confirmation
  of the r67-boundary/r67-critic hang cell.
- **Held writer** (my `fifo_hold` arm): same fixtures resolve in ~0.45 s
  (log marker `SCRIBE-HOLD:drained=False t=14.55s-left` — the verdict landed
  before any drain-poll completed; sox's au-parse of the post-prefetch tail
  fails on the first bytes) to **`can't find Sun/NeXT/DEC identifier`** —
  identical to the author's pinned-linger cell and to the `stdin_pipe` arm.
  Verdict robust across two independent writer protocols.
- Cross-check on non-act members: `fifo_hold` on `pair_preempt_gsrt` →
  `invalid format…`, `pair_dec_hcom` → 9, `ui.wav` → 5760 — the arm changes
  nothing where no bridge runs.
- Orphan accounting: `pgrep -af ffmpeg` shows 24 blocked bridge children on
  this host — all under sibling/`/tmp` paths (`r67-boundary/probes/.*`,
  `r67-author/fifo/*`, `/tmp/r67*`, scout's wedged shells); **zero under
  `r67-scribe`** — the `start_new_session` + `killpg` teardown reaps ffmpeg
  grandchildren (they share sox's process group).

### Boundary carriers (r66 fixtures, re-run under my harness)

| fixture | file | pipe | redir | fifo |
|---|---|---|---|---|
| `g_txw_hcom.bin` (txw) | decode 178 | `input must be a file, not a pipe` | decode 178 | pipe refusal |
| `p_smp_intact.bin` (smp) | `header is not version 2.1` | pipe refusal | `header is not version 2.1` | pipe refusal |
| `p_voc_intact.bin` (voc) | FAIL, empty error tail | FAIL | FAIL | FAIL — invariant |
| `a_wve_valid.bin` (wve) | decode 16 ×4 — invariant | | | |
| `g_amrnb_hcom.bin` (amr-nb) | decode 800 | decode 1120 | decode 800 | decode 1120 |

- txw/smp refusal is **seekability-keyed**, not name-keyed: a named fifo
  refuses identically to an anonymous pipe, and a nameless seekable fd
  (redir) passes — "input must be a file, not a pipe" really means "not
  seekable". r66-boundary's claim reproduced verbatim.
- amr-nb is a **samples-level** fork (800 seekable / 1120 non-seekable,
  identical verdict otherwise) — would count under the landed signature
  (`samples_read` differs) but has no tracked member; simplifier flagged it
  as a second-priority add. Reproduced on fifo too.

## Cross-seat verification (this session, executed by me)

- **49-arm crosscheck vs the author's scratch matrix**
  (`corpus/live/r67-author/transport-matrix.json`) →
  `runs/crosscheck-vs-author.txt`: detected format, exit, samples identical
  on every comparable arm; all 9 string-level "DIFF"s are my TSV tail
  truncation (path eats the 100-char budget) — the verbatim log strings
  match (enumerated above). The only semantic delta is `fifo(bare)` = HANG
  vs author's `fifo_path` = au-magic — a protocol difference, both cells
  real, my `fifo_hold` confirming the author's pinned value.
- **Committed ledger shape**: `corpus/live/r67-author/ledger-r67.tsv` =
  112 rows; `awk -F'\t' '{print $2}' | sort | uniq -c` → **49 × 0 / 63 × 1**
  — matches author/verifier.
- **Receipt determinism on already-on-disk receipts** (no new writes):
  `sha256sum`/`cmp` over three `*-transport-dec-act-r67` receipts →
  byte-identical ×3, sha `195d7554…` (the digest the author/verifier/critic
  quoted); two `*-transport-preempt-act-r67` → `434d82d3…` (verifier's
  value). I did not re-run any `measure_audio.py` mode — receipts land in
  `corpus/live/runs/`, outside my write scope.
- **Receipt shape**: committed `measure_audio.py` (HEAD `366fcc1`,
  +186 lines on `corpus/fixtures/measure_audio.py` per `git show --stat`)
  records per entry `transport_axis` {arm → input, detected, route, exit,
  samples, error, stderr_tail (scrubbed), named, seekable},
  `transport_protocol` {arm_timeout_s 10, fifo_writer_hold_s 1.0, feed},
  `transport_verdict_groups`, `transport_fork`, `failures[]` carrying the
  fork verbatim. Confirmed by reading `…052219421143Z-transport-dec-act-r67/
  measurements.json`.
- **Prior-102 byte-stability**: not re-executed by this seat (ledger runs
  write to `corpus/live/runs/`); corroborated by verifier (102 pairs, 0
  mismatches, AGREE 5/5), critic (re-ran `compare_receipts.py`), simplifier
  (isolated-replica byte-identical), baseline (102/102 anchored to
  `git show 0df212f:` blobs).
- **Commit state**: HEAD `366fcc1` "r67: transport as first-class ledger
  axis" (landed by parent, not a seat); `git status` shows only `M` on my
  scratch (post-commit edits/regenerated logs) + `??` sibling/new scratch.

## Conflicts / findings reported verbatim for the judge

1. **Claim parenthetical is mechanism-true but member-inexact** — "gsrt
   decodes 88 samples on pipe" is literally reproduced only on the
   *untracked* 600-B `D2_gsrt{ULAW,ALAW}+act.wav` carriers (my ext matrix;
   r65-critic's originals). On all three *tracked* gsrt members the pipe arm
   dies at `invalid format for this file type` / `invalid/missing file
   name in header` — the fork is error-class-level, not decode-level.
   `transport_fork` under the landed signature counts it correctly; a
   stricter {exit, samples}-only reading would leave only the two act
   members forking (critic's wording correction — I confirm the distinction
   empirically). ≥1 member forks either way: claim stands.
2. **fifo+act needs a writer-liveness disclosure to be a verdict at all** —
   the bare-writer fifo leg hangs indefinitely (ffmpeg's second open; my
   independent observation on 4 act fixtures). The landed arm pins the
   contended-fifo cell via `transport_protocol`; my evidence-free-of-timing-
   constant `fifo_hold` variant lands the same au-magic verdict. The
   verdict is protocol-robust; the hang is the unmitigated truth. Residual
   per critic: a >1.0 s ffmpeg spawn delay would flip the pinned arm to
   `blocked:` — self-describing, unexercised here.
3. **Concurrency caveat on "receipts byte-stable"** (critic's
   counterexample, observed in author's defect TSVs
   `ledger-r67-run{1,2}-defect.tsv` on disk): demonstrated for serial
   execution; concurrent `build_artifacts.py` rebuilds of
   `corpus/artifacts/*.wav` can crash a row. Pre-existing, process-level,
   not introduced by the arm.
4. **My own scratch was swept into `366fcc1` mid-run** — the committed
   `run_transport.py` is the pre-`wr.close()` variant; the working tree
   holds the fix + regenerated logs. Provenance note only; current TSV/logs
   are self-consistent (post-fix).
5. **TSV `tail` truncation is my scratch cosmetic** — full strings live in
   `runs/logs/`; 9 apparent crosscheck DIFFs all resolved to truncation.
6. **Knowledge-entry filename divergence (late event, verbatim)**: while
   this report was being finalized, `corpus/knowledge/
   2026-10-14-sox-transport-axis.md` appeared on disk (untracked; names a
   slightly different path than the brief's
   `2026-10-14-sox-autodetect-transport-axis.md`), and
   `reports/round-67/r67-adjudicator.md` landed recording **ADMIT**
   (coverage/depth improved locally, calibration unchanged; work commit
   `366fcc1`), noting this seat "pending at adjudication write — respawned;
   scratch in progress". `git status` concurrently shows `M LOG.md`,
   `M SCORECARD.md` — parent integration activity, none of it mine. My
   fenced draft below retains the brief's filename; the parent owns final
   placement.
7. **Seat-status at observation time**: sibling reports on disk — author,
   baseline, boundary, critic, reviewer, simplifier, verifier (AGREE 5/5),
   adjudicator (ADMIT). Scout scratch exists (`r67-scout/runs/…`); two
   wedged scout shell invocations (PIDs 2238073/2238077, ~4 h elapsed) hold
   fifo references — observed, not mine to clean.

## Touched surfaces / out-of-scope

- Wrote this session: `reports/round-67/r67-scribe.md`;
  `corpus/live/r67-scribe/run_transport_ext.py`,
  `corpus/live/r67-scribe/runs/transport-matrix-ext.tsv`,
  `corpus/live/r67-scribe/runs/crosscheck-vs-author.txt`, +31 leg logs under
  `runs/logs/`. Prior instance wrote `run_transport.py`,
  `runs/transport-matrix.tsv`, 68 logs, `probes/` — verified/reused.
- Commands executed by me (all scratch-scoped or read-only):
  `python3 corpus/live/r67-scribe/run_transport_ext.py` (31 legs);
  `sha256sum`/`cmp` on committed receipts + fixtures; `git rev-parse/status/
  diff/show/log` (read-only); `pgrep -af ffmpeg`; `awk`/`wc`/`grep` over
  ledgers and logs; python crosscheck → `crosscheck-vs-author.txt`.
- Read-only: tracked members `corpus/live/round-{63,65,66}/`,
  `corpus/artifacts/ui.wav`, carriers under `corpus/live/r65-{boundary,
  critic}/…`, `r66-boundary/probes/`, author's `r67-author/` artifacts,
  `corpus/live/runs/*` receipts, all sibling reports, `measure_audio.py`.
- Not done (out of scope / not mine): no commits/pushes/merges (the
  `366fcc1` landing is the parent's); no `measure_audio.py` mode runs
  (receipt writes land outside my scope); no tracked edits; no knowledge-
  file write (draft below is parent-decision content); no subagent
  dispatch; no judgment of the axis.

## Bounded UNKNOWNs retained

- Single host/toolchain: SoX_ng 14.8.0.1 USING_FFMPEG + ffmpeg n9.0.1.
  Verdict strings and the bridge existence are build-specific.
- The fifo_hold drain poll exited via `p.poll()` on every act leg
  (`drained=False`): the au-magic verdict lands before full tail-drain is
  observable; whether ffmpeg read all, some, or none of the post-prefetch
  bytes before dying is unmeasured on my harness (boundary's strace shows
  tail-steal on theirs).
- `premature EOF` remains a ≥3-emitter string (checksum-wall EOF, fd-offset
  leak, genuine short stream) — verdict-level, not mechanism-level.
- fifo + act "writer gone" is observed as ≥30 s block (killed); "hangs
  forever" not formally proven (boundary's strace shows indefinite
  `openat` block).
- The empty `probes/` dir suggests the prior instance intended further
  carrier work; not reconstructed — the shipped matrix is complete.

## Draft knowledge entry — for `corpus/knowledge/2026-10-14-sox-autodetect-transport-axis.md`

(Seat draft for parent decision; `[pending]` slots await the
work/knowledge commit SHAs the integration step assigns.)

```markdown
# SoX_ng autodetect TRANSPORT axis — {named × seekable} verdict matrix landed; fork set = exactly the act+gsrt-detected members (round 67)

- Source: round-67 seat evidence (`reports/round-67/r67-{author,baseline,
  boundary,critic,reviewer,simplifier,scribe,verifier}.md`; independent
  matrices `corpus/live/r67-{author,boundary,critic,scribe}/…`); upstream
  sox_ng-14.8.0.1 `src/formats.c`, `gsrt.c` corroborative; all load-bearing
  claims empirical. Work commit: [pending]; this file's commit: [pending].
- Verified at: 2026-10-14, host `/usr/bin/sox` SoX_ng v14.8.0.1
  (USING_FFMPEG build), ffmpeg/ffprobe n9.0.1.
- Recheck when: SoX or ffmpeg version/build changes; the act row is
  `#if USING_FFMPEG` — ffmpeg-less builds compile it out (and shrink
  AUTO_DETECT_SIZE to 132), collapsing every act-route fork; CHECK-table
  additions can reroute members; fixture rebuilds change payloads.

## The transport classes measured

Every receipt entry now carries a 2×2 {named × seekable} arm set
(`measure_audio.py` `TRANSPORT_R67_ARMS`, modes
`--probe-transport-<member>-r67`):

| arm | named | seekable | invocation shape |
|---|---|---|---|
| `file` | yes | yes | `sox -V6 <path> -n stat` |
| `stdin_pipe` | no | no | `sox -V6 - -n stat`, bytes on a real pipe |
| `redirected_fd` | no | yes | `sox -V6 - -n stat`, stdin = the member's own fd |
| `fifo_path` | yes | no | `sox -V6 <fifo> -n stat`, one-shot write + 1.0 s writer linger |

Verdict signature per arm = `(detected, route, exit, samples, error)`;
`error` = normalized post-`':` text of the last `sox FAIL` line.

## The fork map (measured, four seats convergent)

Over the complete tracked autodetect family (r65 preempt ×4 + r66
dec/lengate ×6), verdicts fork on exactly the 5 members routed to the two
transport-sensitive readers — **every gsrt- and act-detected member**:

| member | detected | verdict groups |
|---|---|---|
| preempt_act / dec_act | act | `file`=decode 3839\|278 · `stdin_pipe`+`fifo_path`=au-magic `can't find Sun/NeXT/DEC identifier` · `redirected_fd`=`premature EOF` (3 groups) |
| preempt_gsrt / preempt_both | gsrt | `file`+`redirected_fd`=`premature EOF` · `stdin_pipe`+`fifo_path`=`invalid format for this file type` (2 groups) |
| lengate_gsrt_25 | gsrt | `file`+`redirected_fd`=`premature EOF` · `stdin_pipe`+`fifo_path`=`invalid/missing file name in header` (2 groups) |

Invariant (1 group on all 4 arms): `preempt_hcom` (`bad compression type`),
`dec_hcom` (decode 9), `lengate_gsrt_24` (`fmt chunk not found`),
`lengate_hcom_131` (decode 43), `lengate_hcom_132` (`premature EOF`).

**Detection never forks** — `detected` is identical on all arms of all
members (autodetect consumes only the sequential ≤257-B prefetch); every
fork is decode-stage.

## Per-reader transport binding

- **gsrt — the seekable bit.** `gsrt.c:88` `file_size >= 2 && ft->seekable`
  gates a whole-stream checksum scan; a RIFF collider reads
  `file_size = 0x52494646` ≈ 1.38 G → seekable arms die `premature EOF`,
  non-seekable arms skip the gate and reach the header parse. Decode-level
  fork needs a valid encoding byte: untracked 600-B carriers
  (`r65-critic/var/D2_gsrt{ULAW,ALAW}+act.wav`) decode **88 samples** on
  pipe/fifo vs `premature EOF` on file/redir; 11,588-B `coll_gsrt_alaw`
  decodes **11,076**. Tracked members carry G726 → die at the encoding
  check (`invalid format…`) — same fork, error-class level.
- **act — the bridge needs a re-openable path AND intact bytes.**
  `popen("ffmpeg -nostdin -i <literal-spec> -f au -")`: `file` decodes;
  `redirected_fd` dies `premature EOF` (inherited fd offset past the
  prefetch = EOF at open); `stdin_pipe` dies au-magic (pending-buffer
  residue of the 257-B detection read); `fifo_path` is bivalent — writer
  gone → second `openat` blocks indefinitely, writer held → tail-steal →
  au-magic (receipts pin the held cell via `transport_protocol`).
- **txw/smp — non-seekable refusal.** `input must be a file, not a pipe`
  on pipe AND fifo alike; a nameless seekable fd (redir) passes — the gate
  is seekability, the message says "file". No tracked member detects
  txw/smp; boundary carriers only.
- **wav/hcom — transport-invariant** on this member set (detection +
  decode identical on all arms).
- Outside the arm but measured this round: `/dev/stdin`-over-file decodes
  like `file` (the bridge needs path re-openability, not fd seekability);
  socket-as-path fails `ENXIO` pre-detection; early-EOF fifo writes flip
  *detection* at each member's length gate (act→wav below byte 257);
  `-t act` on a pipe decodes (the stdin bridge is dead *because detection
  consumed the stream*, not because the bridge cannot read pipes);
  amr-nb forks at samples level (800 seekable / 1120 non-seekable).

## Receipt shape note

Per-member entries add `transport_axis` (per-arm verdict cells incl.
`named`/`seekable` + scrubbed `stderr_tail`), `transport_protocol`
(`arm_timeout_s`, `fifo_writer_hold_s`, feed shape — the protocol-sensitive
constants committed to the receipt), `transport_verdict_groups` (signature
partition), `transport_fork` (bool). A fork records verbatim in
`failures[]` → the member exits 1; invariant members exit 0. Ledger grew
102 → 112 rows (49 exit 0 / 63 exit 1); all 102 prior receipts
byte-identical under serial execution (concurrent `build_artifacts.py`
rebuilds of `corpus/artifacts/` are a known flake class — non-atomic
in-place rewrite; documented, not retrofitted).

## Falsifiable recheck conditions

1. `sox -V6 <member> -n stat` on each of the 10 members must reproduce the
   `file`-arm cell of the table above; any detected-format change
   invalidates the member row and the fork-set partition.
2. `cat corpus/live/r65-critic/var/D2_gsrtULAW+act.wav | sox -V4 - -n stat`
   must print `detected file format type `gsrt'` + `Samples read: 88`
   exit 0 while the file leg dies `premature EOF` — any other pair
   falsifies the seekability-gate mechanism.
3. `cat corpus/live/round-66/pair_dec_act.wav | sox -V4 - -n stat` must
   fail `can't find Sun/NeXT/DEC identifier`; `sox -V4 - -n stat <
   pair_dec_act.wav` must fail `premature EOF`; only the named-path leg
   decodes 278 — a decode on either stdin arm falsifies the
   bridge-path-dependence claim.
4. fifo+act with a dead writer must block ≥N s (bounded by the arm's
   `blocked:` verdict); fifo+act with a held writer must yield au-magic —
   a decode or any other error falsifies the tail-steal account.
5. Byte-stability: re-running the 112-command ledger serially must hold
   49/63 with all prior-102 receipts `cmp`-identical; any content diff on
   a prior row falsifies the additive-only claim.
6. Toolchain change (SoX/ffmpeg version or USING_FFMPEG flag) → re-run
   the seat matrices (`r67-scribe/run_transport{,_ext}.py`,
   `r67-author/probe_transports.py`); verdict strings are build-specific.

## Bounded UNKNOWNs retained

- Single host/build; the {named × seekable} 2×2 is a *representative* set —
  the bridge's true predicate is child-side spec resolvability
  (`/dev/stdin` decodes, `/proc/self/fd/N` dies ENOENT inside the fd-
  sanitized child) — accurate inside the four arms, a proxy outside them.
- Verdict signatures are verdict-level: `premature EOF` merges ≥3
  mechanisms; identical strings do not prove identical causes.
- fifo+act writer-liveness margin: the pinned 1.0 s linger covers an
  observed ~0.5–1.0 s ffmpeg spawn-to-open latency — thin under extreme
  load; records `blocked:` honestly if it trips.
- "Hangs forever" on the dead-writer fifo is verified only to ≥20–30 s
  bounds (indefinite `openat` block in strace; killed legs).
- gsrt non-seekable stream-length semantics (declared ~1.38 G vs delivered
  samples) unmapped; amr-nb's 800-vs-1120 mechanism unexplained (carried
  from r66).
```

Stop. Report filed.
