# R67 author — TRANSPORT pinned as a first-class measured axis: fork set measured exactly = the gsrt- and act-detected members (5/10); hcom/wav members transport-invariant (5/10)

host: devin (same lane as R61–R66)
Clean-before: canonical lane repo `/home/vgpnk/Projects/shokunin/audio-shokunin` HEAD `0df212f`;
worktree `/home/vgpnk/Projects/prymeagnt/audio` (`.shokunin/audio` symlinks into the canonical repo).
Toolchain under test: SoX_ng v14.8.0.1 (`/usr/bin/sox` -> `sox_ng` symlink), ffmpeg/ffprobe n9.0.1, python 3.14.7.

## Scoped move — declared falsifiable claim CONFIRMED and measured exactly

The declared claim: *at least one tracked member's verdict forks on transport
(gsrt does — file vs pipe); the set of transport-forking members is exactly
measurable.* Measured over the **complete tracked autodetect member set** (the
10 members whose route is a detection decision — r65 preempt family + r66
dec/lengate family), on the full 2x2 transport space:

| transport | named | seekable | invocation |
|---|---|---|---|
| `file` | yes | yes | `sox -V6 <path> -n stat` |
| `stdin_pipe` | no | no | `sox -V6 - -n stat` with member bytes on a real pipe |
| `redirected_fd` | no | yes | `sox -V6 - -n stat` with stdin = the member's own fd |
| `fifo_path` | yes | no | `sox -V6 <fifo> -n stat`, one-shot writer + 1.0 s linger |

Verdict signature per arm = `(detected, route, exit, samples, error)` where
`error` is the post-`':` message of the last `sox FAIL` line (None on decode).

**Fork set (5 members — exactly the gsrt- and act-detected ones):**

| member | detected | verdict groups |
|---|---|---|
| `pair_preempt_act` | act | `file`=decode 3839 \| `stdin_pipe`/`fifo_path`=`can't find Sun/NeXT/DEC identifier` \| `redirected_fd`=`premature EOF` (3 groups) |
| `pair_preempt_gsrt` | gsrt | `file`/`redirected_fd`=`premature EOF` \| `stdin_pipe`/`fifo_path`=`invalid format for this file type` (2 groups) |
| `pair_preempt_both` | gsrt | identical shape to preempt_gsrt (first-match wins is transport-stable) |
| `pair_dec_act` | act | `file`=decode 278 \| `stdin_pipe`/`fifo_path`=au-magic \| `redirected_fd`=`premature EOF` (3 groups) |
| `pair_lengate_gsrt_25` | gsrt | `file`/`redirected_fd`=`premature EOF` \| `stdin_pipe`/`fifo_path`=`invalid/missing file name in header` (2 groups) |

**Invariant set (5 members + base control):**

| member | detected | verdict (all 4 transports) |
|---|---|---|
| `pair_preempt_hcom` | hcom | `bad compression type` |
| `pair_dec_hcom` | hcom | decode 9 samples, exit 0 — the transport-invariant positive-decode control |
| `pair_lengate_gsrt_24` | wav | `fmt chunk not found` |
| `pair_lengate_hcom_131` | wav | decode 43 samples, exit 0 |
| `pair_lengate_hcom_132` | hcom | `premature EOF` |
| `artifacts/ui.wav` (scratch-only control) | wav | decode 5760, exit 0 |

## What the axis decomposition shows

- **Detection itself never forks** — `sox_detected_format` is identical across
  all four arms on all members (autodetect needs only the sequential prefetch).
  Every fork is decode-stage.
- **Native readers fork purely on the seekable bit**: for all gsrt members
  `{file,redirected_fd}` (seekable) = `premature EOF` (the gsrt.c:88
  checksum-scan that dies on the RIFF-derived 1.38 G sample count) vs
  `{stdin_pipe,fifo_path}` (non-seekable) = the reader-ladder error. Namedness
  does not rescue a fifo; the unnamed-fd redirect does not harm a file.
- **The act bridge forks on name within the seekable camp too**: `file`
  decodes, `redirected_fd` dies `premature EOF` (the r64 fd-offset leak), and
  both non-seekable arms die `can't find Sun/NeXT/DEC identifier` (the r64
  pending-buffer poison / truncated-stream class). Three verdict groups.
- **gsrt members' non-seekable error differs by member**: `invalid format for
  this file type` (preempt_gsrt, preempt_both — unsupported encoding byte, the
  `coll_gsrt_g726` class) vs `invalid/missing file name in header`
  (lengate_gsrt_25 — the truncated header fails earlier in the ladder). Both
  recorded verbatim.
- The gsrt pipe verdict on the tracked members is an EINVAL-class fail, **not**
  a decode: r65-boundary's 11,076-sample pipe decode was `coll_gsrt_alaw`; the
  tracked `pair_preempt_gsrt` is byte-identical to `coll_gsrt_g726`
  (unsupported encoding on pipe). Same fork mechanism (checksum gate skipped),
  different ladder step — consistent with r65-boundary, not a contradiction.
- **fifo + act measures "bridge on a contended fifo"**: the ffmpeg bridge
  re-opens the input by name (open #2 — verified via strace: a second
  `openat(fifo, O_RDONLY)` that blocks once the one-shot writer detaches). The
  recorded arm uses a writer that lingers 1.0 s holding the fifo open so open
  #2 resolves deterministically; ffmpeg then reads only the tail left after
  reader #1's autodetect prefetch — byte-split starvation yielding the same
  `au-magic` terminal class as the pipe arm, via a different mechanism. A
  bare one-shot writer was observed to race open #2 (5/5 shell runs -> exit 2
  au-magic; one python run blocked >10 s) — the linger is what makes the arm
  deterministic, and it is pinned in the receipt (`transport_protocol`).

## Tracked changes (additive only)

`corpus/fixtures/measure_audio.py` **+183/−3** (no other tracked source
touched; `build_artifacts.py` unchanged — all 10 members already tracked under
`corpus/live/round-65|66`, no new fixtures needed):

- 10 flags `--probe-transport-{preempt-act,preempt-gsrt,preempt-hcom,preempt-both,dec-hcom,dec-act,lengate-gsrt-24,lengate-gsrt-25,lengate-hcom-131,lengate-hcom-132}-r67`; mutual-exclusion sum +10; `mode`/`suffix` chain heads prepended (mode strings `probe-transport-*-r67`).
- New arm block (newest-first position, before the r66 block,
  measure_audio.py:604-632): resolves the member from
  `TRANSPORT_R67_MEMBERS`, records `transport_<member>_r67_probe` in
  `measurements`.
- Helpers (measure_audio.py:172-306): `TRANSPORT_R67_ARMS` (the 2x2),
  `transport_error` (normalized FAIL message), `transport_leg` (bounded
  `sox -V6 -n stat` -> verdict dict, 10 s arm timeout), `transport_matrix`
  (the four arms; fifo via `tempfile` + `os.mkfifo` + writer thread with
  `TRANSPORT_R67_FIFO_WRITER_HOLD_S = 1.0` linger), `transport_entry`
  (receipt entry).
- Receipt shape per entry: `path`, `pair_member`, `transport_axis`
  {arm -> input, sox_detected_format, sox_route, exit_code, samples_read,
  error, stderr_tail (input-name + ASLR-scrubbed), named, seekable},
  `transport_protocol` {arm_timeout_s, fifo_writer_hold_s, fifo_feed},
  `transport_verdict_groups` (verdict-signature partition of the four arms),
  `transport_fork` (bool), `failures` — a fork records
  `transport: detection+decode verdict forks across transports (<groups>)`
  so the ledger's failure column carries the fork verbatim. Invariant
  members record an empty `failures` (exit 0).
- New module imports: `os`, `tempfile`, `threading`, `time`. Base `measure()`
  and every prior probe path untouched — the transport axis exists only on
  the new entries, which is what keeps prior receipts byte-identical.
- No `lsp` device is exposed on this substrate — edits applied by hand
  against read file text per the fallback rule (same as r64/r65/r66).

## What ran — 112-command ledger (102 prior verbatim + 10 new modes at positions 2-11)

Commands `python3 .shokunin/audio/corpus/fixtures/measure_audio.py <flag>`
from the worktree root; receipts under `corpus/live/runs/<stamp>-<suffix>/`.
Runner `corpus/live/r67-author/run_ledger.py`; TSV `ledger-r67.tsv`;
comparison `compare_receipts.py`. Final contiguous run: **49 exit 0 /
63 exit 1**, zero UNPARSED (r66's 44/58 + 5 fork rows exit 1 + 5 invariant
rows exit 0).

Prior-102 replay (rows {1} u {12-112} mapped to r66 rows 1-102): exit sequence
position-identical and **all 102 receipts byte-identical** to the r66 receipt
files (`compare_receipts.py`: "102 prior-mode pairs checked, 0 mismatches",
exit 0). Normal-run receipt
`runs/20261014T051933143689Z-normal/measurements.json` byte-identical to
r66's `20261014T023251113379Z-normal` (cmp-verified earlier against
`20261014T051602299499Z-normal` too).

New-mode receipts (deterministic — `transport-dec-act-r67` re-run 4x and
`transport-preempt-gsrt-r67` re-run 2x, byte-identical receipts each time;
sha256 `195d7554…` stable across the three dec-act reruns):

- `--probe-transport-preempt-act-r67` -> exit 1,
  `runs/20261014T051935238922Z-transport-preempt-act-r67/measurements.json`;
  `transport_preempt_act_r67_probe`: fork, 3 groups
  (file=decode 3839 | pipe/fifo=`can't find Sun/NeXT/DEC identifier` |
  redir=`premature EOF`).
- `--probe-transport-preempt-gsrt-r67` -> exit 1,
  `runs/20261014T051937266727Z-transport-preempt-gsrt-r67/measurements.json`;
  2 groups (file/redir=`premature EOF` | pipe/fifo=`invalid format for this
  file type`).
- `--probe-transport-preempt-hcom-r67` -> exit 0,
  `runs/20261014T051939299887Z-transport-preempt-hcom-r67/measurements.json`;
  invariant `bad compression type` x4.
- `--probe-transport-preempt-both-r67` -> exit 1,
  `runs/20261014T051941347471Z-transport-preempt-both-r67/measurements.json`;
  same 2-group gsrt fork (first-match wins is transport-stable).
- `--probe-transport-dec-hcom-r67` -> exit 0,
  `runs/20261014T051943391440Z-transport-dec-hcom-r67/measurements.json`;
  invariant decode 9 x4 — the transport-invariant control.
- `--probe-transport-dec-act-r67` -> exit 1,
  `runs/20261014T051945489969Z-transport-dec-act-r67/measurements.json`;
  3 groups (file=decode 278 | pipe/fifo=au-magic | redir=`premature EOF`).
- `--probe-transport-lengate-gsrt-24-r67` -> exit 0,
  `runs/20261014T051947532835Z-transport-lengate-gsrt-24-r67/measurements.json`;
  invariant `fmt chunk not found` x4 (wav-detected below-gate member).
- `--probe-transport-lengate-gsrt-25-r67` -> exit 1,
  `runs/20261014T051949574088Z-transport-lengate-gsrt-25-r67/measurements.json`;
  2 groups (file/redir=`premature EOF` | pipe/fifo=`invalid/missing file name
  in header`).
- `--probe-transport-lengate-hcom-131-r67` -> exit 0,
  `runs/20261014T051951621574Z-transport-lengate-hcom-131-r67/measurements.json`;
  invariant decode 43 x4 (wav-detected).
- `--probe-transport-lengate-hcom-132-r67` -> exit 0,
  `runs/20261014T051953669140Z-transport-lengate-hcom-132-r67/measurements.json`;
  invariant `premature EOF` x4.

Empirical sweep ahead of the tracked arm (scratch
`corpus/live/r67-author/probe_transports.py` ->
`transport-matrix.json`): all 10 members + `artifacts/ui.wav` control x4
transports — the tracked matrix reproduces it verbatim.

## Ledger-run defects observed (transient, disclosed)

Two earlier ledger attempts each had exactly one UNPARSED row, both in the
shared base-measurement stage (outside the transport arm), both consistent
with a mid-write read of `corpus/artifacts/*.wav`: run 1 row 06
(`--probe-transport-dec-hcom-r67`) -> `ValueError: Invalid number of FFT data
points (0)` (sox returned an empty f32 stream on a valid artifact); run 2
row 26 (`--probe-ui-extensible-valid-56-r64`, a prior mode) -> ffprobe exit 1
on `corpus/artifacts/impact.wav`. Sibling r67 seats rebuild the shared
`corpus/artifacts/` files concurrently (mtime evidence: `impact.wav`
rewritten 02:21:40 between runs; `r67-baseline|boundary|critic|reviewer|scout|
scribe|simplifier` scratch dirs exist). Defect TSVs kept as
`ledger-r67-run1-defect.tsv` / `ledger-r67-run2-defect.tsv`; run 3 (the
TSV on file) is contiguous and clean. `run_ledger.py` also gained a
failsum newline-join (traceback text had split a row's physical line in
run 1 — 113 lines for 112 logical rows).

Setup notes: `python3 -m py_compile` on `measure_audio.py` (the only touched
tracked script) + the scratch tools -> exit 0; `git diff --check` -> clean.
Tracked `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc` differs —
mechanical `py_compile` regeneration churn, same disclosure as r62-r66;
parent decides.

## Labrat (the seat's one bounded probe)

One `ufo-labrat` on the hypothesis "the transport-fork set over the 10 tracked
members is exactly the gsrt- and act-detected members". Returned **CONFIRMED**
(analysis-only — its toolset exposes no shell; its value is independent
reading of my artifacts). Its checks: matrix matches the claimed partition
verbatim incl. the wav-detected lengate members staying invariant (point a);
verdict signature adequate with one stated limit — "premature EOF" merges >=3
mechanisms at string level, verdict-correct but mechanism-blind (b); the gsrt
pipe EINVAL-vs-decode difference resolves to the `coll_gsrt_g726` encoding
byte, no contradiction with r65-boundary (c); fifo+act verdict is fair but is
"bridge on a contended fifo" — disclose the second-open mechanism (d). All
carried above/in limits. Its note that scratch `transport-matrix.json` embeds
absolute fifo paths (not receipt-shaped) is correct — scratch is
corroborative, the tracked receipts are canonical.

## Per-axis claim (author evidence only; verdict belongs to verifier + adjudicator)

- **depth**: transport moved from an invisible receipt property to a measured
  axis — every autodetect member now carries a named x seekable 2x2 verdict
  matrix; the axis decomposition isolates *which* transport bit each reader
  cares about (native readers: seekable only; act bridge: both bits, plus a
  second-open dependency on non-seekable named inputs).
- **coverage**: +10 tracked members measured -> fork set over the complete
  autodetect family is now exact ({5 forking, 5 invariant} = every gsrt- and
  act-detected member forks; every hcom- and wav-detected member does not).
  Ledger 102->112 commands.
- **calibration**: 102/102 prior receipts byte-identical; new receipts
  byte-deterministic across reruns; the fifo arm's only protocol-sensitive
  value (writer linger) is pinned in the receipt itself.

## Conditional replay shape (for the non-author verifier)

112 commands = the r66 102 verbatim with
`--probe-transport-{preempt-act,preempt-gsrt,preempt-hcom,preempt-both,dec-hcom,dec-act,lengate-gsrt-24,lengate-gsrt-25,lengate-hcom-131,lengate-hcom-132}-r67`
inserted newest-first at positions 2-11 (TSV order in `ledger-r67.tsv`).
Expected 49 exit 0 / 63 exit 1; prior-102 receipts byte-identical to r66's;
new receipts deterministic (each re-produced byte-identical JSON — fifo arm
needs ~1 s writer linger, pinned in `transport_protocol`).

## UNKNOWNs / limits

- Verified on this host only: SoX_ng 14.8.0.1 handler order + ffmpeg n9.0.1.
- Verdict signatures are verdict-level, not mechanism-level: identical error
  strings can have different causes (`premature EOF` covers >=3 mechanisms in
  this matrix). Within-member grouping is unaffected.
- fifo + act records "bridge on a contended fifo" — the au-magic verdict is
  reached on the post-prefetch tail stream via the bridge's second open,
  which needs a still-attached writer (hence the pinned linger). A bare
  one-shot fifo writer can deadlock open #2 — itself a transport behavior,
  bounded here by the 10 s arm timeout as verdict `blocked:` if ever hit
  (not hit on the recorded runs).
- Base artifact `ui.wav` verified transport-invariant in scratch only (same
  wav-reader class as `pair_lengate_hcom_131`); it is not a tracked arm
  member — the tracked set is the autodetect member family.
- Ledger runs are exposed to sibling-seat rebuilds of the shared
  `corpus/artifacts/` dir — two transient mid-write flakes observed and
  disclosed above; the final TSV is one contiguous clean run.
- No standards-conformance, decoder-correctness, fidelity, audibility,
  production, rights, engine, or promotion claim — local fixture
  measurements.

## Blockers

None. One bounded labrat dispatched (CONFIRMED, advisory). No commit/push/merge
performed; parent integrates.
