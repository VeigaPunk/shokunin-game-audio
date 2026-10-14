# r67 scout — transport axis map for the autodetect ledger

Seat: scout (leaf). Lane: audio. Repo state at measurement: `audio-shokunin` HEAD `366fcc1`
("r67: transport as first-class ledger axis") — **the author had already landed when this
seat ran**, so this report is an independent verification + extension map, not a pre-land
preview. Prior instance scratch under `corpus/live/r67-scout/` was verified and extended
(member shas re-checked: 19/19 OK against `runs/member-shas.txt`).

Host: `SoX_ng v14.8.0.1` at `/usr/bin/sox`, `ffmpeg` at `/usr/bin/ffmpeg`, Linux
7.2.3-arch1-3.

## 1. Transport inventory (what SoX accepts on this build)

Eight transports were exercised per member (`run_transport.sh`, 158 legs, results in
`runs/transport.tsv`):

| arm | invocation | {named, seekable} class | notes |
|---|---|---|---|
| `file` | `sox f -n stat` | T,T | baseline; every prior ledger row ran this implicitly |
| `pipe` | `cat f \| sox - -n stat` | F,F | `-` is always "the stdin stream"; name bit forced off |
| `redir` | `sox - -n stat < f` | F,T | fd0 IS seekable (`lseek(0)=0` in strace) but `-` keeps the unnamed bit |
| `dspipe` | `cat f \| sox /dev/stdin -n stat` | T-name,F | `/dev/stdin` resolves to the pipe → unseekable; ≡ pipe |
| `dsredir` | `sox /dev/stdin -n stat < f` | T,T | `/dev/stdin` resolves to the regular file → seekable AND re-openable by name → **equivalent to `file`** (act members decode) |
| `fifo` | `sox fifo.wav -n stat`, writer exits promptly | T,F | detection reads fine; act bridge re-opens by name → races writer exit |
| `fifo_hold` | same, writer lingers 8 s | T,F | same verdict as `fifo` — hold is race-hardening, not a different verdict |
| `popen` | `sox "\|cat f" -n stat` | F,F | ≡ pipe for detected members; unique fallback for undetectable input (below) |

Flags/probes that matter:

- **Detection line** `sox INFO formats: detected file format type \`X'` requires **`-V4`+**
  (absent at `-V2`/`-V3`, measured). The `(ffmpeg)` route tag on the `Input File:` line is
  also present at `-V4`+. `-V6` adds DBUG noise the receipt must normalize away.
- **`-t` forcing skips autodetect entirely** — and this forks the fork (see §3): the reader
  then sees a *virgin* stream, so `cat f | sox -t act -` **decodes 3839 samples on a pipe**
  (strace: `ffmpeg -i -` inherits fd0 unconsumed). `-t` is an orthogonal axis
  (detection-bypass), not a transport.
- **`soxi -t` on a fifo works** (returns `act`) — detection probes don't need seekability.
- **`file(1)` oracle contrast**: `file` reports only the RIFF shell for every colliding
  member (`pair_preempt_act.wav` → "RIFF WAVE audio" etc.); the SoX-specific predicates
  (act = RIFF@0 ∧ byte[256]==0x84, gsrt@16, hcom@128) are invisible to it.
- **Undetectable-input fallthrough** (`probes/nodetect.*`, 300 zero bytes): named transports
  fall back to the *extension* handler (`fifo named .wav` → wav reader → "RIFF header not
  found"; `.bin` → "no handler for file extension"); `-` has no name → "can't determine
  type"; `|cmd` **assumes file-type `sox`** then fails "can't find sox file format
  identifier". Extension fallback exists only on named transports.

## 2+3. Predicted → measured fork map (all 18 tracked members + control)

Signature = `(detected_format, exit, samples_read, normalized FAIL text)` — the same
granularity the landed receipt uses. Full table: `runs/fork-groups.txt`; raw:
`runs/transport.tsv` + `runs/logs/*.log`.

**Detection never forks** — `detected` is constant per member across all 8 transports
(content sniffing, not extension). Every fork is decode-stage.

| member family | members | verdict groups across transports |
|---|---|---|
| act, decode-capable | route_84, valid_8/9/24/25/57, preempt_act, dec_act (8) | **3 groups**: `{file, dsredir}`=decode N samples \| `{redir}`="premature EOF" \| `{pipe, dspipe, fifo, fifoh, popen}`="can't find Sun/NeXT/DEC identifier" |
| act, all-fail | valid_56 | **2 groups**: `{file,redir,dsredir}`="premature EOF" \| `{pipe,dspipe,fifo,fifoh,popen}`=au-magic |
| gsrt | preempt_gsrt, preempt_both (invalid format), lengate_gsrt_25 (missing filename) | **2 groups**: `{file,redir,dsredir}`="premature EOF" \| `{pipe,dspipe,fifo,fifoh,popen}`=member-specific body error |
| wav-detected fail | route_00 (valid-bits), lengate_gsrt_24 (fmt chunk) | 1 group — no fork |
| hcom | preempt_hcom, lengate_hcom_132 (all-fail); dec_hcom, lengate_hcom_131 (decode) | 1 group — no fork |
| control | ui (5760 everywhere) | 1 group — no fork |

**Fork counts under the author's 4-arm set** `{file, stdin_pipe, redirected_fd, fifo_path}`:
- on their 10-member set (r65+r66): **5/10 fork** — preempt_act, dec_act (3 groups each),
  preempt_gsrt, preempt_both, lengate_gsrt_25 (2 groups each). Matches their commit claim
  exactly (`corpus/live/r67-author/transport-matrix.json`, `ledger-r67.tsv` rows 02–11).
- extended to all 18 tracked pair members: **12/18 fork** — the 8 act members plus valid_56
  plus 3 gsrt; the r63/r64 members fork identically to their r65/r66 kin.

**Granularity caveat (sharp, matters for "exactly measurable")**: the count depends on the
signature. With the author's error-inclusive signature it's 5/10 (12/18). At coarser
verdict granularity (`exit`+`samples` only) it's **2/10** (8/18) — only the decode-capable
act members fork; the gsrt members all-fail on every transport and their fork lives purely
in the failure *reason*. The brief's claim "gsrt forks file-vs-pipe" is TRUE at signature
level; the r65/r66 *decode*-fork (gsrt 88 samples on pipe, `premature EOF` on file) was
measured on **untracked** scratch fixtures (`E7_triple_bothdecodable.wav`,
`T04_gsrt_riff_collide` — r65-critic.md:70, r66-scribe.md:127), not on the tracked pair
family, whose gsrt bodies are deliberately malformed.

## Mechanism (strace-backed)

- **act/ffmpeg bridge re-opens by name.** fifo: sox opens the fifo (`lseek`→ESPIPE), reads
  600 B, detects act, execs `ffmpeg -i <fifopath>` — a **second open** that blocks unless a
  writer is attached → writer-linger is required for determinism (`runs/strace-fifo-act.txt`;
  the author's `fifo_writer_hold_s=1.0` is ample — my prompt-exit and 8 s-hold legs agree).
- **`-` is nameless forever.** redir: `lseek(0)=0` (seekable), detection leaves fd0 at
  offset 4096, then `ffmpeg -i -` inherits the *consumed* fd → truncated stream →
  "premature EOF" — a third, distinct group (`runs/strace-redir-act.txt`). `/dev/stdin`
  on the same fd0 instead gets opened fresh by name → file-equivalent. The bridge's fate is
  decided by the *string it re-passes to ffmpeg*, not by fd properties.
- **pipe**: `ffmpeg -i -` inherits a pipe drained by detection → empty → ffmpeg produces no
  AU → sox's au reader reports "can't find Sun/NeXT/DEC identifier" — the recorded FAIL is
  the *bridge output* reader, not the input probe.
- **`-t act` on pipe** = virgin fd0 for ffmpeg → full decode (`runs/forced-t-legs.txt`,
  `runs/strace-tact-pipe.txt`).
- **gsrt**: seekable-gated checksum loop (r65-adjudicator pins it at `gsrt.c:88` —
  corroborative cite, not re-derived this round). seekable arms die in the loop
  ("premature EOF"); unseekable arms skip it and fail later in body validation
  ("invalid format…" / "invalid/missing file name in header").

## 4. Receipt shape (as landed)

Per-member `--probe-transport-<member>-r67` flags → receipt entry
`transport_<member>_r67_probe` containing `transport_axis` (4 arms ×
{`input`, `sox_detected_format`, `sox_route` ∈ {ffmpeg,native,none}, `exit_code`,
`samples_read`, `error`, `stderr_tail` normalized via `<input>`-quoting and ASLR
` @ 0x…]` stripping, `named`, `seekable`}), `transport_protocol` (timeouts + fifo feed
description), `transport_verdict_groups` (signature-grouped arms), `transport_fork`
(bool), and a `failures[]` pin when forked. Receipt:
`corpus/live/runs/<stamp>-transport-<member>-r67/measurements.json`; ledger =
`idx \t exit \t receipt_path \t failure_summary` (forking members exit 1).

## 5. Insertion map (`corpus/fixtures/measure_audio.py`, landed +186/-… lines)

- constants `TRANSPORT_R67_ARMS/_MEMBERS/_ARM_TIMEOUT_S/_FIFO_WRITER_HOLD_S`: L172–197
- helpers `transport_error`/`transport_leg`/`transport_matrix`/`transport_entry`: L200–306
- argparse flags: L407–416; exclusivity `sum()`: L418
- dispatch: L604–632 (before the r66 block)
- `mode`/`suffix` chains: ~L1021, ~L1045; receipt write unchanged (~L1048)
- runner: `corpus/live/r67-author/run_ledger.py` inserts the 10 modes at positions 02–11.

## Verification of author claims

- **102 prior rows stable**: semantic check — 97 shared probe keys between
  `r67-baseline/ledger-r67-baseline.tsv` and `r67-author/ledger-r67.tsv`, **0 mismatched**
  on (exit, failure). Caveat: ledger rows embed timestamped receipt paths, so "byte-stable"
  holds at receipt level (their `compare_receipts.py`), not literally at ledger-row level.
- **fifo writer-hold**: 1.0 s is sufficient headroom; the hazard it removes is real
  (ffmpeg's second `open()` on a fifo blocks forever if the writer has fully exited).

## Unresolved gaps / risks for downstream seats

1. **Member-set boundary**: the declared claim says "the set of transport-forking members
   is exactly measurable" over "the existing fixture set". The landed arm covers the
   r65+r66 ten only; under the identical signature the r63/r64 members add 7 more forkers
   (12/18 total). "Exact" is set-relative — the receipt should carry the member-set
   definition it measured (it does: `TRANSPORT_R67_MEMBERS`), and reviewers comparing
   "fork set" claims must normalize on member set AND signature granularity.
2. **`redirected_fd` spelling sensitivity**: implemented as `-` on a redirected fd →
   {F,T}. The same fd0 via `/dev/stdin` is {T,T}≡file. If "redirected fd" is meant as an
   fd property rather than the `-` spelling, the two spellings split (measured: act decodes
   on dsredir, fails "premature EOF" on redir).
3. **`popen` excluded** from the arm set; it's pipe-equivalent for detected members but has
   a unique undetectable-input fallback (assumes type `sox`).
4. **`-t` arms unmeasured in the ledger** — `-t act -` decodes on pipe (detection-bypass
   axis); a future round wanting "transport × forcing" has the evidence above.
5. `stderr_tail` normalization is byte-deterministic on this host (`<input>` quoting +
   ` @ 0x…]` strip); DBUG tails at `-V6` include `start-up time` only mid-stream, not the
   last line — safe as recorded.

Confidence: **high** on the measured matrix (158 legs, sha-verified inputs, deterministic
re-reasoning script `run_transport.sh`), **medium-high** on mechanism (strace-backed for
act on fifo/redir/`-t` pipe; gsrt checksum gate cited from r65 adjudication, not
re-derived from gsrt.c this round).

Artifacts: `corpus/live/r67-scout/{run_transport.sh, runs/transport.tsv,
runs/fork-groups.txt, runs/member-shas.txt, runs/strace-fifo-act.txt,
runs/strace-redir-act.txt, runs/strace-tact-pipe.txt, runs/forced-t-legs.txt,
runs/logs/ (158), probes/, fifo/}`.
