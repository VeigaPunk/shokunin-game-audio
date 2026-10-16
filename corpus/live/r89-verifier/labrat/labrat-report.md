# r89 labrat — relayed advisory probe (read-only; no exec/write substrate)

**Seat:** single permitted `probeParent` labrat for the r89 verifier.
**Substrate limitation (disclosed):** this labrat substrate exposes only
read/search file tools — no shell execution and no file writing. It could
not run fresh `pw-top` invocations nor write its own files. It instead ran
the specified parse over archived `pw-top -b` batch captures already in
`corpus/live/` (same host, PipeWire 1.6.8). This seat (verifier) relays the
advisory result verbatim below; the labrat's own raw evidence is the cited
capture files.

**Hypothesis.** A non-"C" row with WAIT=="0.0us" AND BUSY=="0.0us" occurs at
an observable rate on this host (≥1 within 20 `pw-top -b -n 3` invocations) —
the transient row the fixture's `x_top` arm can select (`status != "C"` and
`wait_us is not None` accept it), forcing a ratio-0 FAIL.

**Observed (archival corpus, ≥30 independent captures).**
- `corpus/live/r89-scout/runs/top_xw_top/rep{0,1,2}/stdout.bin`: frames 2–3 of
  every rep contain non-C 0.0/0.0 rows, e.g. verbatim
  `I   29      0      0   0.0us   0.0us  ???   ???     0                  Dummy-Driver`
  `I   50      0      0   0.0us   0.0us  ???   ???     0                  Midi-Bridge`
- `corpus/live/r88-boundary/raw/state-{A0..B2}-pwt.txt`, `pwt-n{2,3,4}-rep*`,
  `hog-pwt-*`, `r98-scout/scratch/top-*.txt`, `r88-scout/raw/add-pwtop-*`:
  every one of ~40 capture files contains multiple `[A-Z]`-status rows
  matching `^[A-Z] \d+ \d+ \d+ 0.0us 0.0us`.
- R-status 0.0/0.0 rows specifically: >100 matches across the r88 captures,
  e.g. `R  142      0      0   0.0us   0.0us  ???   ???     0     F32P 2 48000 r89b_ns`
  (R-state driver rows at quant=0 with both cells 0.0us).
- Per-invocation hit rate in the archived corpus: ~40/40 files ≥1 hit; hits
  appear in the majority of frames, not as rare transients.

**Verdict: CONFIRMED** (for the stated threshold): non-C 0.0/0.0 rows occur at
an essentially ~100% per-invocation rate on this host, far above 1-in-20; the
`x_top` own_row selection is genuinely exposed to the forced-0.0-ratio FAIL
path. Advisory only; the verifier's own live receipts independently caught
that path twice (reviewer r89r1 `top 0.0/0.0us`; cot1/cot2 `top 0.0/0.0us`).

**Cleanup:** no artifacts created, no processes spawned, no mutations.
