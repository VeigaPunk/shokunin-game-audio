# shokunin-game-audio

Game audio production — sound effects and soundtrack — checked by
headless measurement: duration, loudness, spectral content, and
loop-seam continuity.

The lane id is `audio`. Rank is shonen. There is no root `SKILL.md`.
The boundary is `PROVINCE.md`. The measurements live in `corpus/`.

## The job

`PROVINCE.md` owns original SFX (UI, impacts, movement, ambience) and
soundtrack work (motifs, loops, stems, adaptive layers), plus the
headless fixtures that measure them. Sources it names, read-only: the
host audio toolchain (`ffmpeg`, `ffprobe`, `sox`, probed present
2026-10-12), the demand note `~/Projects/gamez/research/AIAudio.md`, and
real-world references only through a cited ledger that keeps attribution,
rights, and training permission as distinct questions.

A perceptual-quality claim needs a measurable proxy. The proxy measures
the property it names. Publishing, store submission, sample-rights
clearance, engine source changes, game mechanics, and narrative canon
are refused. The province's round-24 checklist classifies a request by
the action and its effect: an original click plus an FFT centroid is
in province; wiring an adaptive layer inside an engine is not; "make it
more cinematic" waits until the requested change is measurable.

The current deterministic WAVs are analytic fixtures. The province says
so: they are not deployed content and they are not a listening test.

`generate_timings.sh` at the repo root is five `gnuplot TimingN.plot`
lines. Those plot files are not at the repository root; copies live
inside round working directories under `corpus/live/`. The script is a
plot driver for a directory that already contains the plots. It is not
the verifier.

## Read this first

1. [`PROVINCE.md`](PROVINCE.md) — the task-boundary checklist. Use it before starting a mixed request.
2. `corpus/knowledge/` — admitted measurement notes.
3. `corpus/fixtures/` — the analytic fixtures.
4. `corpus/live/` — per-round probe runs. Start at the latest round you are auditing, not at a random `run_all.sh`.
5. [`SHONEN.md`](SHONEN.md) — the promotion checklist. Still present.

## On disk

| Path | Role |
|---|---|
| `PROVINCE.md` | Boundary and the classify-the-action table. |
| `corpus/fixtures/`, `corpus/artifacts/`, `corpus/knowledge/` | Fixtures, captured artifacts, admitted notes. |
| `corpus/live/` | Round probes, batteries, and their receipts. |
| `ports/frontier/` | Frontier notes, including `fb-pipewire.md`. |
| `reports/` | Verifier and adjudicator reports. |
| `generate_timings.sh` | Five `gnuplot TimingN.plot` lines. The plots live in round directories under `corpus/live/`, not beside the script. |
| `SCORECARD.md`, `LOG.md` | Axis verdicts and the audit trail. |
| `SHONEN.md` | Promotion checklist. |

## Fleet

Protocol and roster: [shokunin](https://github.com/VeigaPunk/shokunin).
Roster id `audio`, repository name `shokunin-game-audio`, rank **shonen**.
Mechanics belong to the Godot and 3D lanes. Canon belongs to
[shokunin-world-bible](https://github.com/VeigaPunk/shokunin-world-bible).
