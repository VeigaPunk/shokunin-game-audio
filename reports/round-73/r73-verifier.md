# R73 verifier — replay of the committed CONSUMER arm (pw-cat + mpv)

Round: 73. Wave: `shokunin-train-20261101-w12`. Seat: verifier (LEAF).
Author commit `febf34b`; replayed on committed tree at HEAD `3b4c3b7`
(= febf34b + reviewer-fold D12, a comment-only restatement inside the
`--probe-consumers-r73` arm — verified `git diff febf34b..HEAD` touches
9 comment lines, zero code). Lane fixture sha
`77f10786…` == `HEAD:corpus/fixtures/measure_audio.py`.

## Method / receipts

The committed fixture hardcodes receipt output to
`corpus/live/runs/<stamp>-<suffix>/` (no `--runs` flag exists — argparse
would reject it); receipts copied post-hoc into this seat's scope.

| run | mode | exit | receipt |
|---|---|---|---|
| 1 | `--probe-consumers-r73` | 1 | `corpus/live/runs/20261014T151025447162Z-consumers-r73/measurements.json` → `corpus/live/r73-verifier/runs/20261014T151025447162Z-consumers-r73/measurements.json` |
| 2 | `--probe-consumers-r73` | 1 | `corpus/live/runs/20261014T151240011154Z-consumers-r73/measurements.json` → `corpus/live/r73-verifier/runs/20261014T151240011154Z-consumers-r73/measurements.json` |
| 3 | `--probe-sndfile-transport-r72` | 1 | `corpus/live/runs/20261014T151120708825Z-sndfile-transport-r72/` |
| 4 | `--probe-transport-extsuffix-snd-r69` | 1 | `corpus/live/runs/20261014T151122702806Z-transport-extsuffix-snd-r69/` |
| 5 | `--probe-transport-txw-piperefuse-r68` | 1 | `corpus/live/runs/20261014T151124708058Z-transport-txw-piperefuse-r68/` |
| 6 | `--probe-transport-dec-act-r67` | 1 | `corpus/live/runs/20261014T151126775738Z-transport-dec-act-r67/` |

Exit=1 is the expected `return bool(failed)` — the measured transport
forks are recorded as failures by convention (r67). Stdout/stderr
captures: `corpus/live/r73-verifier/run{1,2}.stdout.json`,
`prior-*.stdout.json`, matching `.stderr.log` (all empty stderr).

## Result: consumers-r73 replay (run 1)

Fresh receipt vs committed reference
`corpus/live/runs/20261014T145502288182Z-consumers-r73/measurements.json`:
**semantically identical — raw JSON diff is exactly 4 lines**, two
`wall_s` leaves: `pacing_instant.wall_s` 4.032→4.033,
`pacing_trickle.wall_s` 6.003→6.004 (measured realtime jitter, ≤1 ms —
documented volatile). `daemon_gate.wall_s` 0.002→0.002,
`fifo_no_writer.waited_s` 3.0→3.0 unchanged.

Failures object (verbatim, run 1 stdout):
```json
{"consumer_dec_hcom_r73_probe": ["transport: mpv verdict forks across transports (file/redirected_fd=2/hcom/Operation not permitted vs stdin_pipe/fifo_path=0/hcom/None)"],
 "consumer_extsuffix_snd_r73_probe": ["transport: pw-cat verdict forks across transports (file/fifo_path=0/None vs stdin_pipe/redirected_fd=1/Format not recognised.)"]}
```
Exactly the 2 expected member forks; the other 7 members
(posttable_nomatch, txw_piperefuse, dec_act, extsuffix_{wav,bin,txw,f32})
are transport-invariant on BOTH consumers; ops entry `failures: []`.

## Per-claim adjudication

### (a) mpv × dec_hcom inverted seekability fork — AGREE

`consumer_dec_hcom_r73_probe.consumers["mpv"].transport_verdict_groups`:

| transports | verdict [rc, lavf, seek_failed] |
|---|---|
| file, redirected_fd | [2, "hcom", "Operation not permitted"] |
| stdin_pipe, fifo_path | [0, "hcom", null] |

Arm fields pin the mechanism, matching the committed receipt
field-for-field: the two SEEKABLE arms report
`stream_not_seekable: false`, `refresh_seek: true`,
`seek_failed: "Operation not permitted"`,
`mpv_verdict: "no audio or video data played (reason 4)"`; the two
non-seekable arms report `stream_not_seekable: true`, no refresh seek,
`mpv_verdict: "success (reason 0)"`. lavf detects hcom at score=100 on
all four arms — detection is transport-invariant; only the mandatory
refresh-seek forks decode. `redirected_fd` correctly groups with `file`
(the fd IS seekable) — the fork tracks the seekable bit, and it is
INVERTED (seekable arms fail). pw-cat on the same member: uniform rc=0,
no fork.

### (b) pw-cat × extsuffix_snd name-axis fork — AGREE

`consumer_extsuffix_snd_r73_probe.consumers["pw-cat"].transport_verdict_groups`:

| transports | verdict [rc, sndfile_error] | named | seekable |
|---|---|---|---|
| file, fifo_path | [0, null] | T, T | T, F |
| stdin_pipe, redirected_fd | [1, "Format not recognised."] | F, F | F, T |

The fork tracks `named` exactly — `redirected_fd` is seekable yet fails
(member carries no magic; only the `.snd` name triggers libsndfile's
post-sniff extension fallback), `fifo_path` is non-seekable yet succeeds
(fifo name carries the extension). mpv on the same member: uniform rc=2
`[2, null, null]` — name-insensitive, consistent.

### (c) name-axis 2×2 isolation cell (`pwcat_name_axis`) — AGREE

Ops entry, verbatim from run 1 receipt:
```json
"pwcat_name_axis": {"member": "live/round-69/extsuffix_nomatch.snd",
 "legs": {
  "axis.snd": {"exit_code": 0, "sndfile_error": null, "pw_error": null},
  "axis.wav": {"exit_code": 1, "sndfile_error": "Format not recognised.",
               "pw_error": "open failed: Input/output error"},
  "axis.bin": {"exit_code": 1, "sndfile_error": "Format not recognised.",
               "pw_error": "open failed: Input/output error"}}}
```
Identical bytes, same fifo arm, only the fifo's NAME moves → rc {0,1,1}.
Byte-identical to the committed receipt.

### (d) ops surface pins — AGREE (all five sub-pins reproduced verbatim)

- `daemon_live`: `pactl_exit: 0`, `server_name: "PulseAudio (on
  PipeWire 1.6.8)"`, `live: true` — daemon gate satisfiable on this host.
- `daemon_gate`: `env_override: "PIPEWIRE_RUNTIME_DIR=<empty dir>"`,
  `exit_code: 1`, `wall_s: 0.002`,
  `stderr_tail: "error: pw_context_connect() failed: Host is down"` —
  gate fires BEFORE input open (2 ms, no fifo block).
- `fifo_no_writer`: `blocked: true`, `wchan: "wait_for_partner"`,
  `waited_s: 3.0`, `exit_code: -9` — writerless open blocks in
  wait_for_partner, SIGKILL-bound.
- `fifo_empty_writer`: `exit_code: 1`,
  `sndfile_error: "Format not recognised."`,
  `pw_error: "open failed: Input/output error"`.
- `pacing_instant`: `exit_code: 0`, `wall_s: 4.033` ≥
  0.75×`content_duration_s: 4.0`, `playback_paced: true`,
  `bytes: 384044` on `artifacts/stem_sections.wav`.
- `pacing_trickle`: `chunks: 8`, `chunk_gap_s: 0.75`,
  `delivery_window_s: 6.0`, `exit_code: 0`, `wall_s: 6.004`,
  `starved_ok: true` — starved stream blocks to EOF, no underrun abort.

### (e) prior-row byte stability — AGREE

Four prior modes replayed; each fresh receipt **byte-identical**
(`cmp -s`) to the newest committed receipt of the same mode:

| mode | committed ref | fresh | result |
|---|---|---|---|
| sndfile-transport-r72 | `…T145850288541Z` | `…T151120708825Z` | byte-identical |
| transport-extsuffix-snd-r69 | `…T145854422707Z` | `…T151122702806Z` | byte-identical |
| transport-txw-piperefuse-r68 | `…T145856462943Z` | `…T151124708058Z` | byte-identical |
| transport-dec-act-r67 | `…T145852388812Z` | `…T151126775738Z` | byte-identical |

Fork failure strings reproduce verbatim (e.g. r72:
`file/fifo_path=RAW (header-less)/U-Law vs
stdin_pipe/redirected_fd=Format not recognised.`). The r73 arm did not
perturb any prior row.

## Determinism (run 2 vs run 1)

`--probe-consumers-r73` second run: exit 1, identical failure object.
Semantic diff (all fields minus `wall_s`/`waited_s`): **equal**.
Volatile drift: `pacing_instant.wall_s` 4.033→4.032 (−1 ms);
`pacing_trickle.wall_s` 6.004→6.004; `daemon_gate.wall_s` 0.002→0.002;
`waited_s` 3.0→3.0. Within the documented ≤few-ms jitter envelope.

## Notes / bounds

- Host gate held throughout: PipeWire 1.6.8 live
  (`PulseAudio (on PipeWire 1.6.8)` via pactl), pw-cat linked
  libpipewire 1.6.8, mpv v0.41.0 — same toolchain as the committed
  receipts (`corpus/live/r73-verifier/env.txt`).
- `corpus/live/r73-verifier/` already held an earlier seat attempt's
  captures (11:47–11:58 local, incl. `consumer_matrix_verifier.py` +
  `r73-working.stdout.json` pointing at run `…T145628804590Z`); left
  untouched, this seat's artifacts added alongside.
- Fixture tool writes receipts under `corpus/live/runs/` by design
  (six new `…-consumers-r73`/prior-mode dirs); copies of this seat's
  two consumers-r73 receipts live under
  `corpus/live/r73-verifier/runs/` for the evidence trail.

## Verdict

**AGREE on all five claim items (a–e).** The committed arm replays
byte-for-byte on every semantic field; the two member-local fork
signatures, the 2×2 name-axis cell, and all ops pins reproduce exactly
on this host; prior rows untouched; determinism holds within the
documented wall_s jitter.
