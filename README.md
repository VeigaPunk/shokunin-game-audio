# shokunin-game-audio

Game audio — SFX and soundtrack — verified by headless measurement.

Duration, loudness, spectral content, loop-seam continuity. A number from
a fixture is a number about that signal. It is not a listening test, a
rights clearance, or a claim that the sound is "better."

Rank: **shonen**. `SHONEN.md` is still here. Registered in the fleet
`MANIFEST.json` as audio-shokunin since 2026-10-11. There is no
`SKILL.md` in this checkout. The fixtures, the lessons, and the reports
are the craft record.

## Province

**Owns.** Original SFX (UI, impacts, movement, ambience) and soundtrack
material (motifs, loops, stems, adaptive layers), plus the headless
fixtures and measurements of that material. The province's task table
classifies by the requested action and effect, not by filename.

**Hands off.** Perceptual-quality claims without a measurable proxy.
Publishing and store submission. Sample-rights clearance. Engine source
and engine integration, including wiring a layer into a mixer. Game
mechanics (game-dev-2d). Narrative canon (lore). The province's examples
are the classification key: an isolated stem with a seam check is in
province; selecting that stem from gameplay is not.

Sources the province names as read-only: the host audio toolchain
(ffmpeg, ffprobe, sox — probed present 2026-10-12) and
`~/Projects/gamez/research/AIAudio.md` as demand context. Real-world
samples enter only through a cited reference ledger that keeps
attribution, rights, and training permission as distinct questions.

## Start here

1. `PROVINCE.md` — the task-boundary table. Use it before accepting a
   request that happens to mention a WAV.
2. `corpus/fixtures/measure_audio.py` — the headless checker. The module
   docstring says it checks deterministic WAV fixtures and writes a JSON
   receipt even on failure. Probe modes are explicit `--probe-*` flags.
3. `reports/` — the exact command and the non-author verdict for a round.
   Prefer the report over a remembered flag.
4. `corpus/knowledge/` and `corpus/lessons/` — what the measurement
   established.
5. `SCORECARD.md` — depth, coverage, and calibration stay unassigned as
   scalars. Verdicts are in the per-round tables. The mint row saying
   "no rounds yet" is the mint snapshot; later sections are the record.

## The tree

| Path | What it is |
|---|---|
| `corpus/fixtures/` | Generators, the measurement checker, and the per-round probes |
| `corpus/artifacts/` | Analytic WAV fixtures |
| `corpus/knowledge/` | Measurement notes |
| `corpus/live/` | Preserved run receipts |
| `reports/` | Round verdicts |
| `ports/frontier/` | Frontier notes; `fb-pipewire.md` is the PipeWire note |
| `generate_timings.sh` | Five `gnuplot TimingN.plot` lines. The plot files are not in this tree |

A fixture's RMS, loudness, centroid, or seam delta measures the named
property. The round-1 scorecard verdict records that short-SFX gated
loudness can be null while RMS remains available, and that seam and
centroid proxies do not establish perceptual quality.

## Fleet

Minted under [shokunin](https://github.com/VeigaPunk/shokunin).
