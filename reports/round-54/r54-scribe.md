# R54 scribe — fresh replay ledger and evidence separation

## Scope and status

This is a replay plan, not a replay result. I read `/tmp/mission-audio-standing.md`, the R54 declaration in `.shokunin/audio/LOG.md`, and R53 executor, verifier, and adjudicator reports. I did not invoke the runner or other measurement commands. No R54 pair artifact, hash, ffprobe output, SoX decode, project measurement, or receipt is established by this report.

R54 declares a constructed 5,760-frame, mono, 48,000-Hz signed PCM32 WAV with signed samples `s16*65536`, paired with signed PCM16, intended to yield equal project SoX-f32 decoded samples. This is only an expected construction. Proposed exact runner flags below (`--probe-ui-pcm32-r54`, `--probe-ui-pcm16-r54`) follow the round suffix convention, but **must be confirmed against the integrated runner and builder before replay**. If the implemented spelling differs, record the actual command; do not run a guessed option. The unchanged target limits are duration `.120 s ±.001 s`, peak `<.95`, RMS `>=.001`, centroid `250–4000 Hz`, mono 48 kHz. The expected result is PCM32 sole `format: expected PCM16` failure and clean PCM16 control, but this is a hypothesis only.

## Evidence classification

- **Setup:** No R54 setup or author command has been observed by this scribe. During execution, quote any helper/build/setup command and exit separately; do not count it as a replay row. Setup errors are not gate failures.
- **Format gate:** The declared expected PCM32-only format rejection and PCM16 pass are unverified until their new receipts are parsed.
- **Numeric fit:** No R54 measurements or decoded-vector comparison are available. Do not claim numeric gates pass or vectors match before actual ffprobe/SoX/project measurement. Any non-format gate failure is a numeric/other fit failure to report, not an expected format result.
- **Transcription:** No transcription task or transcription correction is specified; status is not tested, not pass/fail.
- **Replay:** Run serially from repository root. Each row is one runner invocation and must produce a distinct fresh receipt. Do not substitute author runs, historical receipts, or command predictions.

## Fresh 68-command replay ledger (not executed here)

Rows 1–2 are the new PCM32/PCM16 pair. Rows 3–68 reproduce, in order, all 66 commands of the R53 non-author verifier ledger (which itself begins with a normal run, the R53 pair, then the prior R52 sequence). Exit, receipt path, and receipt failures are pending, not inferred. Confirm the new flags exist in the integrated source before starting.

| # | Exact command | New receipt path | Exit | Receipt failure(s) |
|---:|---|---|---:|---|
| 01 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm32-r54` | pending — not run by scribe | pending | pending — not run by scribe |
| 02 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm16-r54` | pending — not run by scribe | pending | pending — not run by scribe |
| 03 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | pending — not run by scribe | pending | pending — not run by scribe |
| 04 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-float32` | pending — not run by scribe | pending | pending — not run by scribe |
| 05 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm16-r53` | pending — not run by scribe | pending | pending — not run by scribe |
| 06 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm8` | pending — not run by scribe | pending | pending — not run by scribe |
| 07 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm16-r52` | pending — not run by scribe | pending | pending — not run by scribe |
| 08 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm24` | pending — not run by scribe | pending | pending — not run by scribe |
| 09 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm16` | pending — not run by scribe | pending | pending — not run by scribe |
| 10 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-channel-stereo` | pending — not run by scribe | pending | pending — not run by scribe |
| 11 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-channel-mono` | pending — not run by scribe | pending | pending — not run by scribe |
| 12 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-rate-48001` | pending — not run by scribe | pending | pending — not run by scribe |
| 13 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-rate-48000-r49` | pending — not run by scribe | pending | pending — not run by scribe |
| 14 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-rate-47999` | pending — not run by scribe | pending | pending — not run by scribe |
| 15 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-rate-48000` | pending — not run by scribe | pending | pending — not run by scribe |
| 16 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-upper-centroid-below` | pending — not run by scribe | pending | pending — not run by scribe |
| 17 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-upper-centroid-above` | pending — not run by scribe | pending | pending — not run by scribe |
| 18 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-absolute-centroid-below` | pending — not run by scribe | pending | pending — not run by scribe |
| 19 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-absolute-centroid-above` | pending — not run by scribe | pending | pending — not run by scribe |
| 20 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-tolerance-5713` | pending — not run by scribe | pending | pending — not run by scribe |
| 21 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-tolerance-5711` | pending — not run by scribe | pending | pending — not run by scribe |
| 22 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-tolerance-5807` | pending — not run by scribe | pending | pending — not run by scribe |
| 23 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-tolerance-5809` | pending — not run by scribe | pending | pending — not run by scribe |
| 24 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-crest-46` | pending — not run by scribe | pending | pending — not run by scribe |
| 25 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-crest-47` | pending — not run by scribe | pending | pending — not run by scribe |
| 26 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-peak-31129` | pending — not run by scribe | pending | pending — not run by scribe |
| 27 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-peak-31130` | pending — not run by scribe | pending | pending — not run by scribe |
| 28 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-slope-32` | pending — not run by scribe | pending | pending — not run by scribe |
| 29 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-slope-33` | pending — not run by scribe | pending | pending — not run by scribe |
| 30 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-endpoint-983` | pending — not run by scribe | pending | pending — not run by scribe |
| 31 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-endpoint-984` | pending — not run by scribe | pending | pending — not run by scribe |
| 32 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-orientation-forward` | pending — not run by scribe | pending | pending — not run by scribe |
| 33 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-orientation-reverse` | pending — not run by scribe | pending | pending — not run by scribe |
| 34 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-centroid-above` | pending — not run by scribe | pending | pending — not run by scribe |
| 35 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-centroid-below` | pending — not run by scribe | pending | pending — not run by scribe |
| 36 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-mixed-pass` | pending — not run by scribe | pending | pending — not run by scribe |
| 37 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-joint-below` | pending — not run by scribe | pending | pending — not run by scribe |
| 38 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-forward` | pending — not run by scribe | pending | pending — not run by scribe |
| 39 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-reverse` | pending — not run by scribe | pending | pending — not run by scribe |
| 40 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-below` | pending — not run by scribe | pending | pending — not run by scribe |
| 41 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-above` | pending — not run by scribe | pending | pending — not run by scribe |
| 42 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-below` | pending — not run by scribe | pending | pending — not run by scribe |
| 43 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-above` | pending — not run by scribe | pending | pending — not run by scribe |
| 44 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-below` | pending — not run by scribe | pending | pending — not run by scribe |
| 45 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-at` | pending — not run by scribe | pending | pending — not run by scribe |
| 46 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-clone` | pending — not run by scribe | pending | pending — not run by scribe |
| 47 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-pass` | pending — not run by scribe | pending | pending — not run by scribe |
| 48 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-fail` | pending — not run by scribe | pending | pending — not run by scribe |
| 49 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join` | pending — not run by scribe | pending | pending — not run by scribe |
| 50 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-pass` | pending — not run by scribe | pending | pending — not run by scribe |
| 51 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-fail` | pending — not run by scribe | pending | pending — not run by scribe |
| 52 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope` | pending — not run by scribe | pending | pending — not run by scribe |
| 53 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | pending — not run by scribe | pending | pending — not run by scribe |
| 54 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | pending — not run by scribe | pending | pending — not run by scribe |
| 55 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | pending — not run by scribe | pending | pending — not run by scribe |
| 56 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | pending — not run by scribe | pending | pending — not run by scribe |
| 57 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | pending — not run by scribe | pending | pending — not run by scribe |
| 58 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | pending — not run by scribe | pending | pending — not run by scribe |
| 59 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | pending — not run by scribe | pending | pending — not run by scribe |
| 60 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | pending — not run by scribe | pending | pending — not run by scribe |
| 61 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | pending — not run by scribe | pending | pending — not run by scribe |
| 62 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | pending — not run by scribe | pending | pending — not run by scribe |
| 63 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | pending — not run by scribe | pending | pending — not run by scribe |
| 64 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | pending — not run by scribe | pending | pending — not run by scribe |
| 65 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | pending — not run by scribe | pending | pending — not run by scribe |
| 66 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | pending — not run by scribe | pending | pending — not run by scribe |
| 67 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | pending — not run by scribe | pending | pending — not run by scribe |
| 68 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | pending — not run by scribe | pending | pending — not run by scribe |

## Replay cross-check and bounded inference

After the verifier executes all rows, check 68 unique fresh receipt paths; parse actual JSON for every command and report every exit/failure. Compare rows 3–68 to the R53 verifier ledger exactly (its 66 commands, modes, exits, receipt failure classifications, and normal restoration checks). Compare the final normal output and canonical17 SHA/metrics with the historical baseline as the verifier does. Expected totals are **30 exit 0 / 38 expected validation exit 1 only if** the new pair produces one format-only rejection plus one clean pass and the prior 66 are unchanged. Do not force this count if observations differ.

For the new pair, separately report generated WAV SHA-256 values; actual `ffprobe` codec name, sample format/bit depth, channels, rate and duration; actual SoX-f32 decoded vector lengths and equality/difference; and actual project metrics and gate failures. Keep setup, intended format rejection, numeric failures and transcription status distinct. The declared `s16*65536` construction can test this particular width-metadata distinction if measured as intended; it does not test extra 32-bit precision, arbitrary PCM32 conversion, fidelity, audibility, quality, rights, engine behavior, production, publishing, or promotion.

No shared source, LOG, SCORECARD, canonical artifact, or other report was edited; no replay was run, and no commit or push was made.
