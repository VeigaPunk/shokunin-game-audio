# R68 adjudicator (Sol) — post-table fallback fork + pipe-refusal member

Round: 68. Wave: `shokunin-train-20261014-w7`. Work commit: `6c91040`
("r68: post-table fallback fork = NAME-resolvability (declared
seekability claim falsified-as-stated) + txw pipe-refusal seekable
reader gate — ledger 112->114, prior rows byte-identical").

## Declared move (depth)

Pin the post-table fallback path: a no-CHECK-match member claimed to
fork on transport seekability ({file,redirected_fd} vs
{stdin_pipe,fifo_path}) via a retry/re-read for fallback classification
with pipes losing the ≤257-byte prefetch; plus one tracked txw/smp
pipe-refusal member. Preserve all 112 prior rows byte-stably.

## Seat convergence

| seat | landing | contribution |
|---|---|---|
| author | yes | `build_artifacts.py` +46/−1 (`build_ui_posttable_r68_probe`), `measure_audio.py` +34/−3 (2 probe flags + 2 members); ledger 114 rows 49/65; prior-112 zero mismatches; falsification absorbed pre-land — comments encode the named-axis mechanism |
| scout | yes | falsified the declared partition independently (13×8 matrix): `{file,fifo_path}` vs `{stdin_pipe,redirected_fd}` = named axis; found the orthogonal `-t` type-forcing escape earlier (r67 close) |
| critic | yes | convergent falsification (6×4 + strace): `ft->seekable` never read post-table; prefetch pending-buffer-replayed not consumed; `.f32`-named fifo decodes 150/150 — namedness sufficient |
| boundary | yes | 19-arm 229-leg matrix; fifo starved-delivery detection flip (protocol artifact); extension-less name = nonce-embedding hazard flagged |
| simplifier | yes | all 9 deletion candidates load-bearing (incl. `.wav` extension — demonstrated mkdtemp-nonce nondeterminism without it); arm structure reuse confirmed; no extraction warranted |
| reviewer | yes | r67 committed-state audit survives on all items |
| scribe | yes | own posttable matrix on landed r67 machinery + strace replay of all 3 named arms; lesson+LOG drafts adopted (member-name corrected to `txw_piperefuse`) |
| baseline | yes | frozen 112/112 rows green at `bd5e1fe`, drift zero |
| verifier | yes | **AGREE 5/5** on `6c91040` — independent 114-cmd replay 49/65/0-UNPARSED byte-identical to author's; 112 prior rows byte-identical to r67 committed; members byte-identical to verbatim rebuild; probes deterministic (5 copies each); seed untouched |

## Measured headline (four-seat falsification convergence)

- **Post-table partition = NAMED axis**: `{file, fifo_path}` → `RIFF
  header not found` (extension→wav handler→reader verdict) vs
  `{stdin_pipe, redirected_fd}` → `can't determine type of \`-'`. The
  `redirected_fd` arm (seekable+anonymous) is the falsification
  counterexample: rewind succeeds, buys nothing — no second pass exists.
- **The declared seekable partition is real but lives elsewhere**: txw
  reader `!seekable` gate → `{file,redirected_fd}` decode 64 samples vs
  `{stdin_pipe,fifo_path}` `input must be a file, not a pipe`.
- **First detection-fork counterexample**: `.snd`-named members arm an
  ext-gated CHECK row → detection itself forks on namedness (r67's
  transport-invariance claim now bounded to non-ext-gated members).
- **5 post-table verdict classes** measured; none seekability-selected.

## Adjudicator own reproduction (committed tree)

- `--probe-transport-posttable-nomatch-r68`: fork receipt exact —
  file/fifo `RIFF header not found` vs pipe/redir `can't determine
  type of \`-'` (recorded as the probe's measured "failures" fork).
- `--probe-transport-txw-piperefuse-r68`: file/redir decode-64 vs
  pipe/fifo pipe-refusal — verbatim.
- Verifier's byte-identical independent replay corroborates both.

## Bounds

SoX_ng 14.8.0.1 USING_FFMPEG + ffmpeg n9.0.1, this host; serial
ledger-execution stability claim; starved-fifo detection flip is a
protocol artifact (disclosed); `.snd` family bounded to the measured
ext-gate row; no conformance/fidelity/production inference.

## Verdict — **ADMIT**

The declared claim was falsified as stated; the falsification IS the
finding and the ledger encodes the corrected mechanism (named-axis
partition + reader-level seekable gate separately tracked). Falsified
claims count as measured outcomes.

- coverage: **improved locally** — post-table fallback class now
  tracked, 112→114 rows, 5 verdict classes enumerated.
- depth: **improved locally** — named-vs-seekable transpose pinned;
  prefetch replay-not-consume mechanism; first detection-fork
  counterexample; genuine seekable reader gate tracked.
- calibration: **unchanged** — additive members + flags only.

Work commit `6c91040`; report-last commit follows.
