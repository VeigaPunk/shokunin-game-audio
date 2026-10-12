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

## Round 6 extension: three bounded invalid-input receipts

`python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` creates three original scratch files only in `corpus/live/round-6/` and writes a timestamped `-invalid/measurements.json`. An expected successful **probe** returns exit **1**, with `invalid_probes` entries each `status: expected_failure` and explicit `observed_failure`:

| named scratch | construction | reported category | method and limit |
|---|---|---|---|
| `short_sections.wav` | valid 48 kHz mono PCM16, 144000 frames rather than required 192000 | `section count`, actual 144000 | `section_contrast()` checks count **before** split/FFT; does not assert every possible truncated file is handled |
| `corrupt.wav` | 16-byte incomplete original RIFF header | `decode`, ffprobe exit 1 | only a `subprocess.CalledProcessError` from ffprobe for this **named** file is mapped to `decode`; unrelated missing tools/programming/receipt errors are not reclassified |
| `wrong_format.wav` | valid analytic 44.1 kHz stereo PCM16, four seconds | `format`, rate 44100/channels 2 | parsed ffprobe metadata mismatch; does not prove general decoder behavior |

Builder source is `corpus/fixtures/build_artifacts.py`; round-6 scoped executor reports carry reproduction and hashes. `--probe-invalid` does not overwrite any of the ten canonical WAVs. Normal mode and existing `--probe-flat`, `--probe-slope`, `--probe-failing` retain their prior semantics. The dedicated JSON receipt demonstrates only these three named cases with the installed toolchain. It is not a guarantee for arbitrary corrupt WAVs, codec security, file permissions, missing executables or production deployment. `corpus/knowledge/2026-10-12-threshold-calibration.md` remains a before-round snapshot of the prior malformed-count caveat; this extension records the narrow fix.

## Round 7 extension: odd-length exception-path control

`--probe-invalid` now also regenerates an original 101-frame PCM16/48k mono `corpus/live/round-7/odd_sections.wav` (executor recipe and SHA in `reports/round-7/r7-odd.md`). The section count **101** is intentionally odd. Against the `3b02c31` source function on this exact file, the old split-before-count path raised `ValueError: array split does not result in an equal division` at `np.split` (isolated old-function command/exits in `r7-baseline.md`; first attempt had a documented setup NameError, then corrected). The current count-before-split path emits a fourth JSON `invalid_probes` entry with `failure_kind: "section count"`, `actual_samples: 101`, `status: expected_failure`; new receipt and non-author replay paths are logged in LOG. This compares direct old function behavior to new opt-in runner behavior; the old CLI did **not** expose arbitrary-file invalid-probe input. It does not generalize to every odd/truncated file or establish audio quality, decoder security or production robustness.

## Round 8 extension: synchronized numeric companion layer

`corpus/fixtures/build_artifacts.py` now generates an original 4.000s mono PCM16/48 kHz `stem_layer.wav` on the same 192000-frame/two-96000-frame grid as `stem_sections.wav`: 120 Hz sine at .012 FS then .060 FS. It is a **separate analytic soundtrack layer file**, not an engine mix or adaptive playback demonstration. `measure_audio.py` measures it under the existing generic duration/format/peak/RMS/centroid/outer-loop endpoint+slope checks and parameterizes the same `section_contrast()` component (30 Hz default for prior stem, 120 Hz for layer). At 48k/96000 half, 120 Hz maps to unwindowed FFT bin 240 (30 Hz to bin 60); its measured 120 Hz amplitudes are .011999587 and .059997745 FS, component **amplitude** ratio `20*log10(A2/A1)` = 13.979372 dB. The inherited receipt key `section_energy_delta_db` is imprecise: it holds an amplitude-ratio contrast, **not** integrated section energy. The top-level `thresholds.section_component_hz: 30` also remains legacy metadata for the original stem; it does not describe every section now that the layer uses 120 Hz. Read the per-section `component_hz` instead. This ambiguity is disclosed, not yet corrected in the receipt schema. Both halves pass the pre-existing >=.01 FS component and >=.001 FS RMS floors; >=6 dB contrast remains fixture-local. Existing 30Hz calculations and bounds remain.

`python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` rebuilds one original matched .036/.036 FS 120 Hz `corpus/live/round-8/flat120_probe.wav` scratch (four seconds, same grid and checker), expected exit **1** with its sole failure `sections: 120 Hz component amplitude contrast < 6 dB or invalid`, measured 0.0 dB. Re-run normal for a clean receipt. Original worker candidate recipes/hashes live in `reports/round-8/r8-{layer,flat}.md`; parent and independent receipt paths/exits live in LOG. The 2s internal amplitude transition is deliberate and **not** assessed for continuity by the outer-loop endpoint/slope metrics. A passing numeric companion and flat control do not establish an audible result, adaptive game behavior or production suitability.

## Round 9 new-receipt field mapping (historical JSON unchanged)

For **newly generated** receipts only, `sections.<name>.section_energy_delta_db` becomes `sections.<name>.component_amplitude_contrast_db`. It has the **same** signed value `20*log10(component_amplitudes_full_scale[1] / component_amplitudes_full_scale[0])` when valid, else null. No numeric gate, FFT bin, audio generation or threshold changed. The top-level `thresholds.section_component_hz: 30` is **removed** from new receipts: `sections.<name>.component_hz` is the one authoritative frequency (`30` for original sections/flat30, `120` for layer/flat120). Historic committed JSON retains the old key and top-level constant byte-for-byte; readers of mixed history must explicitly interpret both schemas. This is a breaking schema change for unknown external consumers, not a claim of backward compatibility. The presence of no in-repository parser does not prove external consumers absent. Exact before/new receipt comparisons and named non-author replay live in round-9 LOG/reports. The move improves labeling/auditability only, not empirical threshold calibration or any audible, adaptive or production property.

## Round 10 extension: internal layer section-join sample gap

The existing outer loop endpoint/slope checks inspect only the file's start/end. New `sections.stem_layer.internal_join_adjacent_delta_full_scale` measures `abs(decoded_pcm[96000]-decoded_pcm[95999])` at the 2s internal boundary of the 192000-frame layer, using SoX-decoded PCM. A new fixture-local `thresholds.internal_join_adjacent_delta_max_full_scale: .03` gates **only `stem_layer` and the named `join_probe`**, fails on `> .03` (equality passes), reusing the numeric outer endpoint bound without calibrating it for audibility. Other section records also expose the adjacent gap as telemetry, but are **not gated** by this new predicate; short/odd invalid records use null because exact count is not met.

Normal clean layer's decoded join gap is `.00018310546875` FS. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` generates original analytic PCM16 scratch `corpus/live/round-10/join_probe.wav`: source layer plus .03-FS 60Hz sine and a single changed frame 96000 to `round(.0305*32767)`, isolated local join gap `.030914306640625` FS. Expected exit **1** with only `sections: internal join adjacent sample gap > .03 full scale`; 120Hz component contrast remains valid (~13.97937 dB), generic format/level/centroid and outer seam gates pass. The source-generated candidate and alternate/failed-fit telemetry are in `reports/round-10/r10-{probe,control,scribe}.md`; parent and independent receipts/commands are in LOG. The spectral adjustment affects global content but stays within existing centroid bound, so this is isolation against named gates, **not** a waveform-identical one-sample corruption. This single adjacent-sample proxy does not test click audibility, internal slope continuity, smooth transitions, adaptive engine timing or production quality.

## Round 11 extension: internal join side-slope proxy

At the same 2 s `stem_layer` boundary, add `sections.<name>.internal_join_side_slope_mismatch_full_scale_per_sample = abs((x[96001]-x[96000])-(x[95999]-x[95998]))` on exactly 192000 SoX-decoded PCM samples. Null on invalid count. Only `stem_layer` and the new `layer_slope_probe` are gated at **strictly `> .001` FS/sample** (equality passes), reusing the old outer loop slope comparator as a fixture-local rule, not empirically tuning audibility. All other exact-length sections, including the pre-existing `join_probe`, carry ungated slope telemetry; this preserves `--probe-layer-join`'s existing sole-gap-failure interpretation. Clean layer slope mismatch is `.000762939453125` FS/sample with adjacent gap `.00018310546875` FS.

`python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` generates scratch `corpus/live/round-11/slope_probe.wav` from the source-generated canonical layer by adding `round(.0004*32767)` PCM16 counts to frame 96001 alone. The matched worker candidate hash and receipts are in round-11 LOG/reports. This gives decoded side-slope mismatch `.00115966796875` FS/sample, while adjacent gap `.00018310546875` passes .03; section 120Hz amplitude contrast and generic/outer checks pass. Expected exit 1 and **sole new slope-predicate failure**. A single two-sided adjacent-slope comparison is a numeric proxy; it does not prove a click-free or musically smooth transition, evaluate a transition window, playback engine timing or production fitness.

## Round 12 extension: second measured 4s layer fixture

`stem_layer_alt.wav` is a new deterministic original 4s/48kHz/mono PCM16 fixture, `.015*sin(2π180t)` for frames 0–95999 and `.050*sin(2π180t)` for frames 96000–191999, quantized by existing `save()`. It extends fixture coverage from one to two stepped-amplitude layer signals, not actual adaptive playback. Both `stem_layer` (120Hz) and this 180Hz alternative are measured separately for half-component amplitude contrast (>=6dB, component amplitudes >=.01FS, RMS >=.001FS), outer generic/seam checks, and exact-edge internal gap <=.03FS and side-slope mismatch <=.001FS/sample. The existing `_alt` duration-or-centroid comparison uses `stem_layer` as baseline; no new comparator or threshold was added. The chosen candidate's original scratch WAV has the same SHA-256 as canonical `stem_layer_alt` and its measured metrics/independent receipts are recorded in round-12 LOG/reports. 180Hz is a DFT component choice, not evidence of musical contrast or timbre, and numeric seam checks do not prove audible smoothness. Historical JSON unchanged; new normal receipts contain a new measurement, distinctness and section record. No listening/engine/adaptive behavior or external strict JSON compatibility is established.
