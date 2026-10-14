# SoX_ng transport as a first-class axis — detection transport-invariant, decode forks exactly on the act/gsrt members (round 67)

- Source: round-67 seat evidence (`reports/round-67/r67-{author,critic,reviewer,simplifier,baseline,boundary,verifier}.md`); harness `corpus/fixtures/measure_audio.py` (`TRANSPORT_R67_ARMS`, `transport_leg`, `transport_matrix`). Commit: 366fcc1.
- Verified at: 2026-10-14, host `/usr/bin/sox` SoX_ng v14.8.0.1 (USING_FFMPEG build), ffmpeg/ffprobe n9.0.1. Work commit: 366fcc1.
- Recheck when: SoX or ffmpeg version/build changes, when the CHECK table changes, when `AUTO_DETECT_SIZE` changes, when the ffmpeg bridge's input re-open path changes, or when fixture families change shape. Receipt byte-stability is bounded to SERIAL ledger execution — `build_artifacts.py` rewrites WAVs non-atomically and concurrent rebuild+replay can observe partial files (critic-flagged; fix = temp-file + `os.replace`, not yet integrated).

## The four arms (the {named × seekable} proxy space)

`TRANSPORT_R67_ARMS` in measure_audio.py:

| arm | named? | seekable? | mechanism |
|---|---|---|---|
| `file` | yes | yes | `sox -V6 <path> -n stat` |
| `stdin_pipe` | no | no | `sox -V6 - -n stat` with piped stdin |
| `redirected_fd` | no | yes | `sox -V6 - -n stat` with `< <file>` redirection |
| `fifo_path` | yes | no | `sox -V6 <fifo> -n stat`, writer lingers `TRANSPORT_R67_FIFO_WRITER_HOLD_S = 1.0`s |

## Measured partition over the 10 tracked members (112-row ledger: 49 exit-0 / 63 exit-1, zero UNPARSED)

**Detection never forks.** `sox_detected_format` is identical across all four arms on all ten members — the detection predicate consumes the same first ≤257 bytes regardless of transport. Every fork is decode-stage.

**Fork set = exactly the 5 act/gsrt-detected members** (under the ledger's `(detected, route, exit, samples, error)` verdict tuple):

- `preempt_act`, `dec_act`, `preempt_both` — the act/ffmpeg bridge forks on *name resolvability within the seekable camp too*: `file` decodes (e.g. dec_act → 278 samples), `redirected_fd` → `premature EOF`, `stdin_pipe`/`fifo_path` → `can't find Sun/NeXT/DEC identifier`. The bridge re-opens the input BY NAME (open #2); an anonymous fd gives it nothing to re-resolve.
- `preempt_gsrt`, `lengate_gsrt_25` — the native gsrt reader forks on the seekable bit alone: `file`/`redirected_fd` → `premature EOF`; `stdin_pipe`/`fifo_path` → checksum loop skipped → decode proceeds (88 samples class) or `invalid format for this file type`.

**Invariant set = the 5 hcom/wav-detected members** (`preempt_hcom`, `dec_hcom`, `lengate_gsrt_24`, `lengate_hcom_131`, `lengate_hcom_132`): identical verdict×4 — e.g. dec_hcom decodes 9 samples on every arm; the below-gate members fail identically (`bad compression type`, `fmt chunk not found`, `premature EOF`) on every arm.

## Boundary/scout refinements — the proxy is not the contract

- Scout extension over all 18 tracked members × 8 transports: **12/18
  fork** under the error-inclusive signature (8 act + valid_56 + 3 gsrt);
  the "exact fork set" is member-set- and signature-granularity-relative —
  at {exit, samples}-only granularity it is 8/18.
- Mechanism pinned by strace: the act ffmpeg bridge re-opens the input
  **by name** (`ffmpeg -i <path>` — fifo needs a lingering writer; `-i -`
  inherits the consumed fd0). `-` is nameless forever even when fd0 is a
  seekable file; `/dev/stdin` on the same fd0 is file-equivalent.
- **The orthogonal `-t` axis**: `cat f | sox -t act -` decodes on a pipe
  (3,839 samples) — type-forcing bypasses autodetection entirely, so the
  bridge inherits a virgin stream. `-t` forcing is not a transport.

- The real gate is **what the ffmpeg child can re-resolve**, not `{named × seekable}` per se: named-seekable works; anonymous-seekable fails at the bridge; fifo-with-live-writer tail-steals; fifo-with-dead-writer **hangs the whole command** (the child's `openat(fifo)` blocks).
- fifo determinism requires the writer-linger protocol (1.0 s hold, pinned in every receipt); a bare one-shot writer races the bridge's second open. Residual risk under extreme load; `O_RDWR` holder or process-group kill would be more robust.
- Early-EOF on fifo flips detection at each member's own len gate — transport can change *detection* when the byte supply is truncated, not the predicate.
- stdin+ffmpeg-bridge remains structurally dead (r66 boundary: undrained `pending_buffer` EPIPE + stdio-prefetch 4,096-B loss on seekable stdin).

## Critic absorption

- "Verdict forks" should be read as **verdict+error signature**: under a strict `{exit, samples}`-only reading the fork set shrinks to the 2 act members; under the implemented tuple it is 5. The core claim (≥1 member forks; exact set pinned) holds under both readings.
- gsrt forking on the tracked members is die-position-level, not decode-level — the same fork mechanism (checksum gate skipped on non-seekable) decodes on pipes.
- The autodetect prefetch is the true fork locus for act members (278 samples decode on a pipe when the prefetch path is exercised).

## Next-round gap

`txw`/`smp` pipe refusal (r66 boundary) has no tracked member yet — the post-table fallback cascade is the declared audio r68 frontier.
