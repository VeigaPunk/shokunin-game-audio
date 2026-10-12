# Audio round 1: reproducible fixture battery

## Run

From the repository root, use `python3 .shokunin/audio/corpus/fixtures/measure_audio.py`.
It builds from original analytic waveforms with fixed random seed, overwrites five
PCM16 WAV files in `corpus/artifacts/`, then writes a new timestamped JSON receipt
in `corpus/live/runs/`. Exit 0 means all declared checks passed. Run again with
`--probe-failing`; exit 1 is expected, with `ambience`'s `loop seam` failure
in that run's JSON. Re-run normal mode afterwards to restore clean artifacts.
Requires python3 + numpy, ffprobe, ffmpeg, sox; no audio server or soundfile.
The shell entry `corpus/fixtures/build_artifacts.sh` rebuilds just the artifacts.

## Decision table (round-specific proxies, not universal mastering limits)

| decision | measurement and threshold | action on failure | source / derivation |
|---|---|---|---|
| Asset has expected length and decode format | ffprobe format duration within ±0.001 s of declared 0.12/0.32/0.24/2/2 s; one channel, 48000 Hz | check builder's sample counts / WAV header | ffprobe `-show_entries`, [ffprobe docs](https://ffmpeg.org/ffprobe.html); fixed `round(seconds*RATE)` in `build_artifacts.py` |
| No silence or excessive sample peak | decoded samples RMS >0.001 full scale; absolute sample peak <0.95 | inspect gain/envelope, then regenerate | PCM `sox ... -t f32 -` conversion per [SoX format docs](https://sox.sourceforge.net/soxformat.html); thresholds are local conservative design choices, *not* broadcast standards |
| Spectrum belongs to declared fixture | magnitude-weighted full-signal FFT centroid within per-fixture ranges in JSON; bandwidth recorded, not gated | inspect signal or unexpected discontinuity | [NumPy rfft docs](https://numpy.org/doc/stable/reference/generated/numpy.fft.rfft.html); ranges derive from clean generated fixtures, not auditory judgment |
| Loop boundary avoids a large discontinuity | absolute decoded last-to-first sample delta <=0.03 full scale for ambience + stem | regenerate periodic source, avoid endpoint corruption | fixture periodicity and threshold chosen here; endpoint sample check only, not a perceptual loop guarantee |
| Loudness reading is interpretable | log ebur128 integrated LUFS where >−70; otherwise report null and use RMS dBFS | do not treat gated floor as actual loudness of a brief SFX | [FFmpeg ebur128 filter](https://ffmpeg.org/ffmpeg-filters.html#ebur128), [EBU R128](https://tech.ebu.ch/publications/r128); these are measurement definitions, not fixture loudness targets |

## Error patterns and limits

| pattern | observed or expected indicator | interpretation / next step |
|---|---|---|
| A loop's endpoint is modified | `--probe-failing`: ambience seam delta ~0.499, above 0.03; centroid also fails | corruption is caught; multiple failed probes are allowed, but the seam result is the intended positive control |
| Short SFX ebur128 floor | −70 LUFS output (UI, impact, movement in first local run) | gating floor; JSON null after correction; compare RMS dBFS instead, not LUFS |
| A pop despite passing endpoint check | test compares one endpoint sample only | slope mismatch, phase/codec behavior, masking and game-engine looping remain unknown; decode shipped formats and test joins before claiming seamless playback |
| A centroid passes but timbre is wrong | global FFT reduces time-varying spectrum to one number | use windowed spectral tests and listening before production acceptance; no perceptual-quality claim follows |
| Source rights ambiguity | only analytic sine and seeded numpy noise in this round | no borrowed audio; future references need independent attribution, asset rights, and AI-training permission checks |

## Reference ledger

No real-world sound recording or composition is used or evaluated in these fixtures.
The cited FFmpeg, SoX, NumPy and EBU documentation supports measurement methods,
not sample acquisition. Attribution: link the named documentation above. Asset
rights: not applicable to these source-generated WAVs; no claim about rights to
external recordings. AI-training permission: not requested or implied for any
external audio. Future samples require separate answers to all three questions.
