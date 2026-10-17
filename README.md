# shokunin-game-audio

Game audio production — sound effects and soundtrack — checked by
headless measurement: duration, loudness, spectral content, and loop-seam
continuity.

Lane id: **audio-shokunin**. Rank: **shonen**. [`SHONEN.md`](SHONEN.md)
records four boxes checked by named non-author verifiers, scoped to the
fixture workflow and the province audit they actually ran. There is no
root `SKILL.md`. The craft notes are `corpus/knowledge/`.

Fleet: [shokunin](https://github.com/VeigaPunk/shokunin).

## The question

> Do these fixtures meet the declared duration, level, spectrum, and
> loop-seam proxies, with a receipt a second run can compare?

A proxy measures the property it names. It is not a claim about perceived
quality, cinematic feel, or store readiness. `PROVINCE.md` refuses
perceptual-quality claims that lack a measurable proxy.

## Boundary

**Owns:** original SFX (UI, impacts, movement, ambience) and soundtrack
material (motifs, loops, stems, adaptive layers), plus the headless
fixtures and measurements for them, inside this repository.

**Hands off:** publishing and store submission, sample-rights clearance,
engine integration (triggers, mixer, import), game mechanics
([shokunin-godot-2d](https://github.com/VeigaPunk/shokunin-godot-2d)), and
narrative canon
([shokunin-world-bible](https://github.com/VeigaPunk/shokunin-world-bible)).
The task-boundary table in `PROVINCE.md` classifies mixed requests. An
audio file extension does not pull engine wiring into this lane.

Host tools recorded present at mint: ffmpeg, ffprobe, sox. Real-world
recordings enter only through a cited reference ledger that keeps
attribution, rights, and training permission as separate questions.

## Run

The checked-in battery entry is `corpus/fixtures/measure_audio.py`
(docstring: headless checks of deterministic WAV fixtures, JSON receipt
even on failure). It imports numpy and shells out to the host audio
tools. `--probe-failing` is still a flag on that file. The round-1 exit
contract — exit 0 when the declared checks pass, exit 1 expected under
`--probe-failing` — is written in
`corpus/knowledge/2026-10-12-fixture-battery.md`, which also names
`corpus/fixtures/build_artifacts.sh` as the artifact rebuild.

```sh
python3 corpus/fixtures/measure_audio.py
```

Later rounds added guards under `corpus/fixtures/test_*.py` (host lock,
RTP loopback, wireplumber, sofa witnesses, and others). Read the test
module you intend to run. `corpus/live/` holds per-round probe trees;
those are evidence of a round, not a second copy of the battery to start
from. `generate_timings.sh` runs five gnuplot scripts named `Timing1.plot`
through `Timing5.plot` and does nothing else.

## Map

| Path | What it is |
|---|---|
| [`PROVINCE.md`](PROVINCE.md) | owned audio work and the task-boundary table |
| [`corpus/knowledge/`](corpus/knowledge/) | fixture battery, checklist, threshold calibration, tool notes |
| [`corpus/fixtures/`](corpus/fixtures/) | `measure_audio.py`, `build_artifacts.py`, later guards |
| `corpus/artifacts/` | WAV fixtures the battery writes when it runs (`ARTIFACTS` in `measure_audio.py`) |
| [`reports/`](reports/) | verifier and adjudicator reports |
| [`SHONEN.md`](SHONEN.md), [`SCORECARD.md`](SCORECARD.md), [`LOG.md`](LOG.md) | probation, verdicts, audit trail |

Analytic fixtures are not deployed content and not a listening test.
