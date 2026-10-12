# Round 17 scout — SPECS and 200 Hz geometry map

## Scope and evidence

I read `.shokunin/audio/LOG.md` Round 17 declaration, `corpus/fixtures/measure_audio.py`, `corpus/fixtures/build_artifacts.py`, and the fixture-battery notes. I ran no shell commands, did not synthesize or measure a WAV, and changed no source or canonical artifact. Thus no shell command/exit code applies. This report is a source map and formula-based prediction only; it is not integrated-runner evidence.

## Existing canonical SPECS

`measure_audio.py` currently has twelve named canonical entries (duration seconds, centroid minimum/maximum Hz, loop checks):

| Name | Duration | Centroid band | Outer endpoint/slope checks |
|---|---:|---:|---|
| `ui`, `ui_alt` | .12, .16 | 250–4000 | no |
| `impact`, `impact_alt` | .32 | 50–15000 | no |
| `movement`, `movement_alt` | .24, .36 | 100–16000 | no |
| `ambience`, `ambience_alt` | 2.0 | 5–200 | yes |
| `stem` | 2.0 | 100–2000 | yes |
| `stem_sections` | 4.0 | 100–2000 | yes |
| `stem_layer` | 4.0 | 100–2000 | yes |
| `stem_layer_alt` | 4.0 | 100–2000 | yes |

The per-row loop bit applies existing outer checks: endpoint delta <=.03 FS and slope delta <=.001 FS/sample. No existing `stem_layer_third` SPECS key or 200 Hz section entry exists. In current `sections` comprehension, `stem_sections`/`flat30_probe` use 30 Hz, `stem_layer` and its 120 Hz controls use 120 Hz, and `stem_layer_alt` and 180 Hz controls use 180 Hz. `section_contrast` splits exactly 192,000 decoded samples into two 96,000-sample halves; it estimates the nominated exact FFT-bin amplitude in each, requires each amplitude >=.01 FS and each half RMS >=.001 FS, and accepts signed `20*log10(A2/A1) >= 6 dB`. Existing applicable internal join checks are gap <=.03 FS and side-slope mismatch <=.001 FS/sample.

## Coverage distinction and proposed numeric prediction (not measured)

The declared addition would extend the two-step layer fixture component cases from 120 and 180 Hz to a third 200 Hz case. It reuses the existing 4.0 s, 100–2000 Hz, loop-checked stem-layer envelope and existing section/gap/slope criteria; it does not require or justify a new threshold. The 200 Hz analysis bin is `200 * 96000 / 48000 = 400`, rather than the current 240/360 bins for 120/180 Hz. The current generic centroid band contains 200 Hz, but passing the full-waveform centroid is a separate measurement, not implied by component-bin validity.

For the declared analytic formula `where(t < 2, .015, .050) * sin(2*pi*200*t)` at 48 kHz, with existing builder PCM16 rule `round(clip(x,-1,1)*32767)`, a local formula/quantization calculation predicts frames 95998..96001 near `[-.00079348, -.00039674, 0, .00131230]` FS. This predicts an internal join adjacent gap about `.00039674` FS and side-slope mismatch about `.00091556` FS/sample. At the outer boundary, the same periodic-phase calculation predicts endpoint delta about `.00131230` FS and slope mismatch about `.00091556` FS/sample. These are predictions from the source formula and PCM16 quantization, not decoded SoX/ffprobe/runner results; actual tool measurements must decide. They are under the existing `.03` and `.001` bounds but slope margin is only about `.00008445` FS/sample, so the local shape is comparatively close to the existing slope limit. If runner decoding/rounding crosses the limit, record the fit failure and adjust source waveform shape without moving thresholds.

The same calculation predicts section amplitudes near `.01500044` and `.04999956` FS and signed contrast near `+10.45724 dB`; both exceed the existing .01 validity floor, and the contrast exceeds 6 dB. Formula-only full-waveform magnitude centroid is about 287.94 Hz. These calculated values are hypotheses, not a receipt, and do not demonstrate actual level, format, duration, outer checks, section checks, or all other gates. The 200 Hz tone is numerically distinct from 120 and 180 Hz component selection, but distinct fixture coverage is not evidence of perceptual distinction or improved playback.

## Minimal integration map / cautions

The likely narrow integration points are: original builder's `save("stem_layer_third", ...)` alongside the two layer saves; a `SPECS` entry using `(4.0, 100, 2000, True)`; section inclusion mapped to 200 Hz; and the existing internal gap/slope applicability checks including that new measured name. Apply existing section validity/contrast and outer checks without an exception or threshold change. Then independently verify new WAV format/hash and all gates, unchanged twelve old artifact hashes and five `_alt` records, and prior modes before admission. This is a source-location map, not an implementation recommendation beyond the declared coverage move.

No claim here about audibility, musicality, seamless playback, an adaptive/game engine, external compatibility, security, production readiness, or rights to external recordings. The waveform is original analytic synthesis; this scouting pass does not add external material.
