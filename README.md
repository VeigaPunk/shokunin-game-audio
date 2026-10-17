# shokunin-game-audio — audio-shokunin

**Game audio production** — SFX (UI, impacts, movement, ambience) and
soundtrack (motifs, loops, stems, adaptive layers) — verified by
headless analysis: duration, loudness, spectral content, loop-seam
continuity.

A fixture metric measures the named property. It is not proof of
perceived quality, rights clearance, or production readiness.

This is a **shokunin lane** of the [shokunin fleet](https://github.com/VeigaPunk/shokunin).
Canonical name: `audio-shokunin`. Rank: **shonen**.

## The craft

- Host toolchain recorded at mint: ffmpeg, ffprobe, sox
  (`PROVINCE.md`). Later rounds also pin PipeWire / gst / parec
  surfaces in `reports/` and `corpus/fixtures/measure_audio.py`.
- Original audio content and its measurements stay inside this repo.
- The deterministic WAVs in-tree are **analytic fixtures**, not
  deployed content or listening validation (`PROVINCE.md` task
  boundary checklist, round 24).
- Publishing, store submission, sample-rights clearance, and engine
  mixer wiring are refused. "Make it more cinematic" is uncertain
  until a measurable change is stated.

SHONEN boxes 1–4 have named non-author verifiers on record
(`SHONEN.md`: audio-r1-verifier, r2-verifier, r3-adjudicator,
r24-verifier). That is fixture-scoped evidence, not a ship stamp.

## Province

Owns: original SFX / soundtrack content and its headless
fixture / measurement / documentation, entirely within this repo.

**Refuses:** perceptual-quality claims without a measurable proxy;
publishing or store submission; sample rights clearance; engine
source mutation; game mechanics (game-dev-2d); narrative canon
(lore). Write scope is this lane's tree and its own reports — not
fleet bookkeeping, not engine directories.

See [`PROVINCE.md`](PROVINCE.md).

## What's in this repository

```
shokunin-game-audio/
├── PROVINCE.md              task-boundary checklist (round 24)
├── SHONEN.md                four named-verifier boxes
├── LOG.md                   long-run fixture + toolchain record
├── SCORECARD.md
├── generate_timings.sh
├── ports/                   frontier ports
├── reports/                 round-1 … round-100+
└── corpus/
    ├── fixtures/            measure_audio.py + WAV fixtures
    ├── artifacts/
    ├── knowledge/
    └── live/                receipts, verifier freezes
```

`SKILL.md` is not at repo root (shonen seed form — the corpus and
`measure_audio.py` *are* the skill). Start from `PROVINCE.md`.

## Start here

```sh
python3 corpus/fixtures/measure_audio.py --help
```

Pick **one** `--probe-*` mode; combining modes is a parse error
(exit 2), by design. A receipt under `corpus/live/` is a measurement
of the named probe, not a listening test.

`generate_timings.sh` rebuilds timing tables from recorded runs.

## How a round works

One axis-move. Lane identity should be
`audio-shokunin <audio@shokunin.local>` on specialist commits.

## Fleet

[VeigaPunk/shokunin](https://github.com/VeigaPunk/shokunin) ·
[kimi-shokunin](https://github.com/VeigaPunk/kimi-shokunin)
