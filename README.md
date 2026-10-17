# shokunin-game-audio — audio-shokunin

**Game audio production — SFX and soundtrack — verified by headless
analysis:** duration, loudness, spectral content, loop-seam continuity.

This is a [shokunin](https://github.com/VeigaPunk/shokunin) lane. Rank:
shonen. Canonical lane name: `audio-shokunin`. A proxy measures its
named property. It does not measure "cinematic," "better," or perceived
quality.

Host toolchain, probed present 2026-10-12 (`PROVINCE.md`): ffmpeg,
ffprobe, sox. The current deterministic WAVs are analytic fixtures, not
deployed content or listening validation.

## Province

**Owns:** original SFX (UI, impacts, movement, ambience) and soundtrack
(motifs, loops, stems, adaptive layers) as audio content or its
headless fixture / measurement / documentation, entirely inside this
repo.

**Refuses:** perceptual-quality claims without a measurable proxy;
publishing or store submission; sample rights clearance; engine source
mutation; wiring adaptive layer selection in an engine; game mechanics
(→ game-dev-2d); narrative canon (→ lore). Classify the requested
*action and effect*, not the filename. A mixed task does not become
audio-owned because its WAV sits in this tree.

Write scope is this repository and this lane's own reports. Fleet
bookkeeping (`MANIFEST.json`, mint files) is historical setup, not a
standing permission. Full boundary and the six-row task checklist:
[`PROVINCE.md`](PROVINCE.md).

## Start here

1. [`PROVINCE.md`](PROVINCE.md) — owns / refuses / task-boundary checklist.
2. [`corpus/fixtures/measure_audio.py`](corpus/fixtures/measure_audio.py) — headless measurement.
3. [`SHONEN.md`](SHONEN.md) — promotion checklist.
4. [`reports/`](reports/) — per-round author / verifier / adjudicator record.

This lane is still in shonen seed form: distilled `SKILL.md` lives in
the corpus until promotion. `corpus/QUALITY.md` is the admission bar.

## Measurement

```
python3 corpus/fixtures/measure_audio.py
```

Additional fixtures in `corpus/fixtures/` pin loopback, host-lock,
stream-scope, and format-specific witnesses. A passing measurement
proves the named proxy on the named file. It does not clear a sample
for a store release, prove a mixer graph, or certify perceived quality.

Rights, attribution, and AI-training permission are kept as distinct
questions on any cited reference. The operator's assertion alone does
not confer authority on this lane.

## What's in the repo

```
shokunin-game-audio/
├── PROVINCE.md              domain + task-boundary checklist
├── SHONEN.md                promotion checklist
├── LOG.md                   append-only audit trail
├── SCORECARD.md             axis verdicts
├── generate_timings.sh      timing helper
├── ports/                   port notes
├── reports/                 per-round seat reports
└── corpus/
    ├── fixtures/            measure_audio.py + format witnesses
    ├── knowledge/
    └── lessons/
```

Protocol: append-only corpus; every claim separates observation /
inference / unknown; rounds are non-author-verified. See the fleet
[README](https://github.com/VeigaPunk/shokunin#readme) for how a lane
learns.
