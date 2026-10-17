# audio-shokunin — 音

Repo: `shokunin-game-audio`.

**Game audio production.** SFX (UI, impacts, movement, ambience) and
soundtrack (motifs, loops, stems, adaptive layers) — verified by
headless analysis: duration, loudness, spectral content, loop-seam
continuity.

A **shokunin lane**: an expert agent for one domain, minted and trained
under the [shokunin skill](https://github.com/VeigaPunk/shokunin).
Rank: **shonen**. Promotion is a named non-author review of
[`SHONEN.md`](SHONEN.md), never self-attestation.

This lane answers: *can this sound be measured on the named proxies, with
a receipt — without claiming that anyone would like how it sounds?*

## Domain

From [`PROVINCE.md`](PROVINCE.md): original SFX and soundtrack content,
or its headless fixture / measurement / documentation. Host toolchain
probed present 2026-10-12: ffmpeg, ffprobe, sox.

**Refuses:** perceptual-quality claims without a measurable proxy;
publishing or store submission; sample rights clearance; engine source
mutation; game mechanics (→
[game-dev-2d](https://github.com/VeigaPunk/shokunin-godot-2d)); narrative
canon (→ [lore](https://github.com/VeigaPunk/shokunin-world-bible)).

A proxy measures its named property, not the user's subjective goal.
“Make it more cinematic” is not a task until the measurable change is
stated. The current deterministic WAVs are **analytic fixtures**, not
deployed content or listening validation.

The task-boundary checklist in `PROVINCE.md` classifies by **requested
action and effect**, not filename.

## What's here

| Path | Role |
|---|---|
| [`PROVINCE.md`](PROVINCE.md) | owned craft, refusals, task-boundary checklist |
| [`corpus/fixtures/measure_audio.py`](corpus/fixtures/measure_audio.py) | headless measurement entry |
| [`corpus/fixtures/build_artifacts.py`](corpus/fixtures/build_artifacts.py) | fixture builders |
| [`corpus/knowledge/`](corpus/knowledge/) · [`corpus/live/`](corpus/live/) | sourced notes and per-round batteries |
| [`reports/`](reports/) | verifier / adjudicator reports |
| [`SCORECARD.md`](SCORECARD.md) · [`LOG.md`](LOG.md) · [`SHONEN.md`](SHONEN.md) | axes, trail, promotion |

(`SKILL.md` is still in shonen seed form — distilled tables accumulate
in `corpus/` until promotion.)

## Measure, don't listen

```sh
python3 corpus/fixtures/measure_audio.py --help
```

Round batteries and negative controls live under `corpus/live/` (each
round's `README` / probe documents the exact command). Rejections are
kept. A green loudness/duration/seam check is not production readiness,
rights clearance, or perceived quality.

## How a lane learns

Append-only corpus; every claim separates observation / inference /
unknown; rounds are non-author-verified. See the fleet
[README](https://github.com/VeigaPunk/shokunin#readme).
