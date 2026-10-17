# shokunin-game-audio

**Game audio production — SFX and soundtrack, verified by headless
analysis, never by vibes.**

Lane name: **audio-shokunin**. A **shokunin lane** minted and trained
under the [shokunin](https://github.com/VeigaPunk/shokunin) skill.

**Wiki:** [lane overview](https://app.devin.ai/org/veigapunk/wiki/VeigaPunk/shokunin-game-audio?branch=main)

## Domain

From `PROVINCE.md`:

- SFX — UI, impacts, movement, ambience
- soundtrack — motifs, loops, stems, adaptive layers
- headless proxies: duration, loudness, spectral content, loop-seam continuity

A proxy measures its named property. It does not prove perceived
quality, cinematic impact, rights clearance, or production readiness.
The current deterministic WAVs are analytic fixtures, not deployed
content or listening validation.

Host toolchain named in the province (probed present 2026-10-12):
ffmpeg, ffprobe, sox. Real-world sample/reference works enter only
through a cited reference ledger — attribution, rights, and training
permission stay distinct questions.

## Task boundary

Classify the **requested action and effect**, not the filename
(`PROVINCE.md` §Task boundary checklist):

| Decision | When |
|---|---|
| Audio-province | original SFX / ambience / motif / loop / stem / layer, or its fixture / measurement / documentation, entirely inside the write scope |
| Refuse the consequential part | publishing; sample-rights clearance; engine mixer / trigger wiring; game mechanics; narrative canon; fixture metrics as proof of perceived quality |
| Uncertain or mixed | split only if a genuinely independent audio-only deliverable exists; otherwise pause and route |

Write scope: this repository and its own reports. Fleet bookkeeping
(`MANIFEST.json`, mint files) is not a standing permission.

## What it refuses

Perceptual-quality claims without a measurable proxy; publishing or
store submission; sample rights clearance; engine source mutation; game
mechanics ([game-dev-2d](https://github.com/VeigaPunk/shokunin-godot-2d));
narrative canon ([lore](https://github.com/VeigaPunk/shokunin-world-bible)).

## In this repository

```
PROVINCE.md     domain + task-boundary checklist
SHONEN.md  SCORECARD.md  LOG.md
corpus/
  artifacts/    fixtures/    knowledge/    live/
reports/        per-round author / verifier / scribe records
ports/frontier
generate_timings.sh    gnuplot Timing1–5 (local plot helper)
```

This lane is still in shonen seed form — distilled `SKILL.md` is absent;
the corpus and reports are the craft record.

## How a lane learns

Append-only corpus; every claim separates observation / inference /
unknown; rounds are non-author-verified. See the fleet
[README](https://github.com/VeigaPunk/shokunin#readme).
