# R43 reviewer — minimal opt-in RMS controls

## Recommendation

Use exactly two new mutually exclusive scratch modes, e.g. `--probe-ui-rms-46` and `--probe-ui-rms-47`. Reuse the existing `SPECS["ui"]` (0.12 s, 250–4000 Hz, non-looping); do not add a generic mode framework or alter canonical fixtures. Builder writes only `live/round-43/ui-rms-46.wav` / `ui-rms-47.wav`, as deterministic 5760-frame, 48 kHz mono PCM16 `round(crest_count * cos(2π·1000·n/48000))`. Runner measures only the selected file under the UI spec and records its mode/receipt. Keep the current combined predicate literally unchanged: `if peak >= .95 or rms < .001:` with its existing failure label. No threshold, ordinary check, or other source behavior needs to change.

## Numerical-only check / caveat

I checked the intended quantized cosine numerically in the REPL (no shell command or project runner invoked). For signed PCM16 values decoded as sample/32768, 5760 frames yield:

| Crest count | decoded peak | decoded RMS (FS) | RMS dBFS | FFT-weighted centroid |
|---:|---:|---:|---:|---:|
| 46 | 46/32768 = 0.00140380859375 | 0.0009918604133909925 | -60.07098885448798 | 1333.1671762128672 Hz |
| 47 | 47/32768 = 0.001434326171875 | 0.0010130695326051164 | -59.88721491134572 | 2221.180142174043 Hz |

Both crest peaks are well below .95; arithmetic predicts 46 fails only the RMS side of the combined `level` condition and 47 passes it, with centroid inside the UI band. This calculation is a candidate calibration, **not** evidence of SoX-f32 decoded output, generated WAV hash, or a runner exit/receipt. The very low-amplitude quantized cosine has notable quantization harmonics, reflected in its centroid; still within the specified UI band. Builder and runner must validate the actual decoded files before claiming the declared outcomes. Report numerical candidate-fit failures distinctly from environment/setup errors; do not call setup failures failed numeric fits.

No shell commands were run, so there are no command exit codes to report. This is numerical fixture calibration only—not audition, sound-quality, production, rights, engine, publish, or promotion evidence. The 46/47 pair brackets RMS behavior using adjacent target crest counts; it does not establish adjacent attainable RMS values or exact equality at `.001`.
