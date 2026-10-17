# shokunin-game-audio — audio

The question this lane answers is whether a game-audio artifact meets a headless measurement: duration, loudness, spectral content, and loop-seam continuity, for SFX and soundtrack (`PROVINCE.md`).

**Rank:** `SHONEN.md` is titled probation. All four boxes are `[x]`, checked by named non-author verifiers `audio-r1-verifier`, `r2-verifier`, `r3-adjudicator` with `r3-verifier`, and `r24-verifier`, with the evidence paths written in that file. The rank file still titles the lane probation. This README does not invent a rank above that.

## Owns / refuses

Owns game audio production: UI, impacts, movement, and ambience SFX, and soundtrack motifs, loops, stems, and adaptive layers, verified by those headless measures. Sources named in `PROVINCE.md`: the host audio toolchain (ffmpeg, ffprobe, sox, probed present 2026-10-12), `~/Projects/gamez/research/AIAudio.md` as demand context, and real-world samples only through a cited reference ledger that keeps attribution, rights, and training permission distinct.

Refuses perceptual-quality claims without a measurable proxy, publishing or store submission, sample-rights clearance, engine source mutation, game mechanics (game-dev-2d), and narrative canon (lore). The task-boundary table in `PROVINCE.md` classifies the requested action, not the filename.

There is no root `SKILL.md`. `PROVINCE.md` holds the decision table. There is no `corpus/README.md`.

## Start here

`corpus/fixtures/measure_audio.py` is the headless checker. Its docstring says it checks deterministic WAV fixtures and writes a JSON receipt even on failure. The argparse block is a long list of `--probe-*` flags. Run `--help` to see them; do not treat a probe flag as the default battery.

```sh
python3 corpus/fixtures/measure_audio.py --help
```

`generate_timings.sh` at the repo root is five `gnuplot TimingN.plot` lines and nothing else. It is not the measurement gate.

`PROVINCE.md` says the current deterministic WAVs are analytic fixtures, not deployed content and not a listening test.

## Map

| Path | What it is |
|---|---|
| `PROVINCE.md` | Boundary and the round-24 task table |
| `SHONEN.md` | Probation checklist, boxes checked by named verifiers |
| `LOG.md` | Append-only record |
| `SCORECARD.md` | Axis verdicts |
| `corpus/fixtures/` | Measurement scripts and fixture drivers |
| `corpus/artifacts/` | Fixture outputs the tools read |
| `corpus/knowledge/` | Sourced notes |
| `corpus/live/` | Preserved run records |
| `generate_timings.sh` | Gnuplot timing plots |
| `ports/frontier/fb-pipewire.md` | Frontier note shipped under `ports/` |
| `reports/` | Verifier reports |

## Neighbors

game-dev-2d owns mechanics. lore owns canon. A soundtrack that would set a character's backstory is split in the `PROVINCE.md` examples: audio can build a signal from a separately approved brief, and setting canon is refused. Rights clearance is refused even when the operator asserts it.

Fleet protocol: [VeigaPunk/shokunin](https://github.com/VeigaPunk/shokunin).
