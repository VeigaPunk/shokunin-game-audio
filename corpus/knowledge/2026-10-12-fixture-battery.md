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

## Round 2 extension: measured SFX variants

The same `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` entrypoint now regenerates and measures nine original mono PCM16/48 kHz files: the original five plus `ui_alt` (0.16 s), `impact_alt` (0.32 s), `movement_alt` (0.36 s), and `ambience_alt` (2.00 s). Each new file uses the original category's level and centroid bounds; `ambience_alt` additionally uses the existing endpoint threshold. Recipes and independent worker measurements are in `reports/round-2/r2-{ui,impact,movement,ambience}.md`. All files use analytic oscillators or newly seeded NumPy noise and no external samples.

The receipt adds `distinctness` for each variant, derived from the decoded WAV measurements rather than synthesis parameters. The declared round-2 criterion is absolute duration difference >=0.020 s **or** absolute centroid difference / baseline centroid >=0.10. The 20 ms minimum was tightened before integration after `r2-critic.md` showed that any nonzero sub-millisecond difference would otherwise pass. This is an intentionally local numerical distinction check, not evidence of perceptually distinct audio. A loop's endpoint amplitude can match while its slope is discontinuous; current seam results cannot certify playback-quality loops. The original five records and the existing failing-probe behavior remain in the same receipt. No new loudness target is imposed; `integrated_lufs: null` still indicates the brief-SFX gated floor, not silence.

## Round 3 extension: slope behavior at loop joins

The same nine-file entry point now records `seam_slope_delta_full_scale_per_sample` on loop fixtures (`ambience`, `ambience_alt`, `stem`) as `abs((last - penultimate) - (second - first))` on SoX-decoded samples. A local bound of <=0.001 FS/sample complements, never replaces, endpoint amplitude <=0.03 FS. In the clean PCM16/48 kHz distribution the three slope gaps are 0.000030517578125, 0, 0.000030517578125 FS/sample; the chosen bound leaves ~32.8× headroom over that tiny fixture set. `r3-metric.md`, `r3-fixture.md`, and `r3-calibration.md` record the derivation and cautions. This is not a universal audibility/mastering or codec threshold; amplitude scaling, frequency and sample rate change its meaning.

Run `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope`: expected exit **1** and a `-slope` receipt. It synthesizes an original 1-second `corpus/live/round-3/slope_probe.wav` with equal decoded endpoints (delta 0) but neighboring slope gap 0.469970703125 FS/sample; only `slope_probe` should fail slope, not endpoint. `--probe-failing` retains the prior broken-amplitude control and exit 1. Re-run normal mode (expected exit 0) to restore clean outputs. The slope probe demonstrates a case missed by endpoint amplitude alone. Neither probe establishes audible seam quality or runtime looping behavior.

## Round 4 extension: two-section soundtrack fixture

Normal entry now also builds `stem_sections.wav` as a second original soundtrack loop: 4 s mono PCM16/48 kHz, two exact 96,000-sample sections with shared 220/330 Hz analytic terms and a 30 Hz component whose authored peak amplitude changes from .012 to .060. Source recipe and raw decoded measurements are in `audio/reports/round-4/r4-composer.md`. The fixture retains the existing stem's local format/level/centroid and endpoint/slope guards, but this is not engine-adaptive music or evidence of a perceptible motif.

Section proxy: for each SoX-decoded 96,000-sample half, compute `2*abs(np.fft.rfft(section)[60])/96000`; at 48 kHz the bin is 30 Hz. Require finite peak component amplitudes each >=.01 FS, section RMS each >=.001 FS, and signed section-2/section-1 component energy contrast `20*log10(A2/A1) >=6 dB`. In the clean decoded WAV, amplitudes are .0119994651 and .0599980712 FS, producing 13.979508 dB; each RMS clears the floor. These are local analytic contrast conditions, not proof of motif identity or audible development. The exact-bin estimator is narrow and unsuitable for detuned/time-varying target components without revising this decision table.

`python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` builds a distinct 30 Hz-matched `corpus/live/round-4/flat30_probe.wav` with both section component amplitudes .0359986155 FS. Its 0 dB contrast fails **only** the section test (expected exit 1); all normal guards pass. Re-run normal mode (exit 0) for clean restoration. Wave-1 worker's separate `flat_probe.wav` varies/checks 440 Hz and is retained as failed-fit telemetry, not evidence for this 30 Hz control. `--probe-slope` and `--probe-failing` retain their existing expected exit-1 behavior. Neither the 6 dB contrast nor loop guards establish musicality, perceptual quality, or runtime seam behavior.
