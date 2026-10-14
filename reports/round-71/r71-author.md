# audio round 71 — author (seat: author; **operator-substituted**, host: devin)

> Provenance: the r71 author seat died to the free-model rate-limit
> massacre (reset 16:01 UTC). Operator authored the diff under disclosed
> substitution; verifier/critic/boundary seats dispatched post-landing
> to check it independently.

## Declared move (verbatim)

Second decoder runtime (ffmpeg/ffprobe n9.0.1) on the tracked transport
member set: per-decoder × per-transport × per-member verdict matrix.
Claim: ffmpeg's verdicts track CONTENT probing, not the r68/r69
named/suffix axis — it accepts members SoX extension-rejects when content
is parseable and rejects by content where SoX accepts by suffix.

## Landed changes (corpus/fixtures/measure_audio.py only; insertion-only)

- `TRANSPORT_R71_MEMBERS` — 9 members reusing tracked corpus: r69's five
  identical-byte suffix members (isolate the suffix axis), the r68 pair
  (post-table/no-match content), dec_act/dec_hcom (the members whose SoX
  verdicts already cross the ffmpeg bridge).
- `ffprobe_leg` — ffprobe detection (format_name/probe_score JSON) +
  `ffmpeg -v error -i <in> -f null -` decode verdict, 15s bounded.
- `ffmpeg_transport_matrix` — same 4 transports as the SoX arm; fifo legs
  get a **per-process fifo+writer** (first run found the r67-analog
  defect: the ffmpeg leg opened the writer-dead fifo and blocked — fixed
  by fresh fifo per subprocess, fifo unlinked after use).
- `ffprobe_transport_entry` — verdict groups keyed on
  (ffprobe_format, ffmpeg_exit, ffmpeg_error) + detection-only
  ffprobe_verdict_groups; transport_fork pin.
- `--probe-ffprobe-transport-r71` flag; prior ledger rows untouched —
  new measurement keys only.

### Self-caught artifact disclosed (fixed before landing)

First run forked `redirected_fd` on dec_act/dec_hcom ("detect-ok,
decode Invalid-data") — traced to a shared-fd bug in my own fixture: the
ffprobe leg consumed the fd's offset and the ffmpeg leg read EOF. Fixed
to open a FRESH fd per subprocess (stdin_path). Post-fix run shows
redirected_fd behaves identically to stdin_pipe under ffmpeg's `pipe:`
protocol — the quadrant is **not** a distinct ffmpeg transport class
(recorded as such for the critic to check).

## Measured result (receipt `20261014T140155796326Z-normal`, exit 0)

- **Claim CONFIRMED**: all 7 no-match members reject on ALL 4 transports
  ("Invalid data found"), incl. the .wav/.txw/.snd names SoX routed to
  handlers — ffmpeg ignores the name, content-probes, rejects.
- dec_act → `wav`, dec_hcom → `hcom` detected by content on every
  transport (incl. fifo) — **transport-invariant** under ffmpeg, zero
  forks. The SoX named/anonymous partition has no ffmpeg analogue at
  this member set.
- probe_score returned null on n9.0.1 (field absent in this build's
  format dict — recorded null, critic to confirm whether the key exists).

## Evidence

- Receipt: `corpus/live/runs/20261014T140155796326Z-normal/measurements.json`
- `corpus/live/r71-author/run_ledger.py` (121 modes), `compare_receipts.py`
  (byte-identity vs r70 ledger).
- Runs: ~3min wall, 0 fifo survivors (per-process writer + reap).

## Unknowns for boundary/next-round

- ffmpeg fifo writer-hold band vs sox's (r70 ladder analogue);
- probesize cliffs on truncated members; `-f` hint arms;
- whether `pipe:` over a real seekable fd can ever diverge from a true
  pipe under a different ffmpeg build.
