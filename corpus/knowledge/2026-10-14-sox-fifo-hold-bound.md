# SoX_ng fifo writer-hold bound — transition zone not a point h*; verdict = attach x close-before-deadline; chunked feed is the binary control (round 70)

- Source: round-70 seat evidence (`reports/round-70/r70-{baseline,critic,reviewer,scout}.md`); operator replay `corpus/live/runs/20261014T124018313832Z-fifo-hold-ladder-r70/measurements.json`; baseline's independent ladder `corpus/live/r70-baseline/hold-ladder.json` (10 reps/cell, leg_wall_s + writer_closed_at_s per rep); scout mechanism map `corpus/live/r70-scout/`.
- Verified at: 2026-10-14, host `/usr/bin/sox` SoX_ng v14.8.0.1 (USING_FFMPEG), ffmpeg n9.0.1, Python 3.14.
- Recheck when: SoX/ffmpeg bridge behavior changes, the fifo arm protocol changes, or host load profile shifts materially.

## The measured law

The `fifo_writer_hold_s` constant is not a bound point — the outcome space is **attach-at-open-#2 x close-before-deadline**:

- `oneshot` feed: `h=0` → 10/10 `blocked: no verdict within 10 s` (writer detaches before the ffmpeg bridge's open #2; grandchild dead-locks in `openat(fifo, O_RDONLY)`); `h>=0.05` → 10/10 exit-2 au-magic (`can't find Sun/NeXT/DEC identifier`). Transition zone on this host/load ≈ **(0, 50ms]** — the critic's finer sweep found a mixed band around ~18ms; the honest report shape is `{max_divergent, min_stable}` per run, never a scalar h*.
- `chunked` feed: stable at **every** hold incl. `h*=0` — the feed duration itself spans the bridge's open window, so the writer is still attached when open #2 resolves. This is the claim's "correctly blocking writer" control arm — and it refutes strict binary-on-attach: a third outcome exists (attach-through-delivery).
- The pinned `1.0 s` default sits ~20x above the measured zone — a defensible margin, not a bound.
- Member routing: open #2 exists only on the ffmpeg route (`dec_act`, `preempt_act`); every other member is single-open → hold-invariant.

## Harness consequences (landed in `measure_audio.py`)

- A blocked leg leaves a dead-locked ffmpeg **grandchild** — killpg is necessary but NOT sufficient (the bridge child can escape the child's process group; critic observed a 5+-min survivor). `reap_fifo_orphans` sweeps /proc cmdlines for the fifo path as the verdict-neutral backstop on BOTH fifo legs.
- The committed receipt carries verdict DISTRIBUTIONS per {feed, hold} cell (`verdict_distribution` signature→count) — never per-rep wall floats; byte-identity discipline preserved.
- `MEASURE_FIFO_WRITER_HOLD_S` env override exists for ad-hoc legs and is always recorded in `transport_protocol` — never silent.
- Residual: `run_ledger`-style serial drivers have no per-row timeout; a fully-divergent ladder cell burns `arm_timeout_s` per rep — bounded but slow (critic note).

## Edges

- `writer.join(timeout=hold + feed_span + 5)` bounds cleanup — the `+5` grace is the unrecorded timing constant, now documented in-fixture.
- h=0 under load: whether the detached-verdict *ever* wins on a cold cache is open (scribe/baseline 0/20+ observed); treat the (0,50ms] zone as load-dependent.
- O_RDWR holder alternative exists unmerged in r67-scribe scratch (`run_fifo_hold`): `os.open(fifo, O_RDWR)` → writer always attached, no timing constant — a cleaner arm shape if a future round wants timing-free determinism.
