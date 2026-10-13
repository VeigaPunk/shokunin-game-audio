# r25-scout — current format failures and invalid controls

## Scope and finding

Read-only inventory of `.shokunin/audio/corpus/fixtures/measure_audio.py`, `build_artifacts.py`, the current six-entry `--probe-invalid` receipt, and native WAV metadata. No source or fixture was changed. The round-25 declaration asks for two new single-predicate controls (48 kHz stereo PCM16 and 44.1 kHz mono PCM16); neither exists in the current builder or six-entry invalid receipt. The current `wrong_format.wav` is 44.1 kHz **stereo** PCM16, so its rejection does not isolate rate from channels.

`format_failures(stream)` currently returns the same single string, `format: expected 48kHz mono`, if **either** sample rate differs from 48000 or channel count differs from 1. A separate conditional returns `format: expected PCM16` if codec is not `pcm_s16le` or bit depth is not 16. Thus receipt-level `observed_failure: "format"` does not identify which predicate caused rejection. There is no new threshold in this mapping.

## Six current invalid controls and exact metadata

Current `invalid_probes()` order and expected outcome:

| Probe | Source / metadata | Expected → observed | Meaning |
|---|---|---|---|
| `short_sections` | `live/round-6/short_sections.wav`; ffprobe: 48000 Hz, mono, `pcm_s16le`, 16-bit, 3.000000 s | `section count` → `section count` | Valid format; 144000 decoded samples vs required 192000. |
| `corrupt` | `live/round-6/corrupt.wav`; 16-byte incomplete RIFF header; ffprobe exits 1 and reports invalid data | `decode` → `decode` | Decode/probe failure, not a rate/channel test. |
| `wrong_format` | `live/round-6/wrong_format.wav`; ffprobe: 44100 Hz, **2 channels**, `pcm_s16le`, 16-bit, 4.000000 s | `format` → `format` | Both rate and channel predicates are violated; cannot attribute the result to either one alone. |
| `odd_sections` | `live/round-7/odd_sections.wav`; ffprobe: 48000 Hz, mono, `pcm_s16le`, 16-bit, 0.002104 s | `section count` → `section count` | Valid format; 101 decoded samples vs required 192000. |
| `native16_probe` | `live/round-22/native16_probe.wav`; ffprobe: 48000 Hz, mono, `pcm_s16le`, 16-bit, 4.000000 s | none → none (`expected_pass`) | Native-format positive control. Invalid mode checks metadata only; it does not run ordinary acoustic checks on this control. |
| `native24_probe` | `live/round-22/native24_probe.wav`; ffprobe: 48000 Hz, mono, `pcm_s24le`, 24-bit, 4.000000 s | `format` → `format` | Isolates codec/bit-depth mismatch while rate and channels match. |

The wrong-rate/stereo WAV builder uses a four-second 44.1 kHz stereo PCM16 signal with 440 Hz at .30 FS and 660 Hz at .25 FS. This gives the invalid container a plausible non-silent signal and exact duration, but `--probe-invalid` takes the metadata-only branch for it; the invalid receipt does **not** attest its peak, RMS, centroid, or other acoustic conditions. The requested new matched controls should each be measured for metadata and ordinary acoustic conditions separately if the claim requires those conditions to pass.

## Existing numeric/failure surface relevant to this map

The 13 canonical `SPECS` entries are checked by `measure()`: format (48 kHz mono PCM16), duration within ±0.001 s, peak `<.95`, RMS `>=.001` (code rejects `<.001`), per-fixture centroid band, and—where the spec marks a loop—endpoint delta `<=.03` and slope mismatch `<=.001` FS/sample. Section-bearing assets additionally use the 192000-sample section check, component amplitude floors `.01`, section RMS floor `.001`, and component-amplitude contrast `>=6 dB`; internal join checks apply to listed layer fixtures. `_alt` pairs use duration delta `>=.020 s OR` centroid relative delta `>=.10`. These are existing local fixture checks, not claims about audible quality.

The invalid-mode branches are deliberately distinct from `measure()`: `short_sections`/`odd_sections` call `section_contrast()`; `corrupt` classifies ffprobe failure; `wrong_format` and the native-width controls call `ffprobe` then `format_failures()`. They do not run all numeric checks on invalid entries. The current format result is a category, not an isolated predicate receipt.

## Exact shell evidence and exits

1. Source inspection was performed by reading the two Python files directly (no shell command).
2. Metadata command used (with the six paths substituted as shown; each `ffprobe` exit is printed):

```sh
for f in .shokunin/audio/corpus/live/round-6/{short_sections,corrupt,wrong_format}.wav .shokunin/audio/corpus/live/round-7/odd_sections.wav .shokunin/audio/corpus/live/round-22/{native16_probe,native24_probe}.wav; do
  echo ===$f
  ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,duration -of json "$f"
  echo exit:$?
done
```

Shell command exit **0** (the loop completed); individual `ffprobe` exits: short 0; corrupt 1; wrong_format 0; odd 0; native16 0; native24 0. Corrupt stderr: `Invalid data found when processing input`.
3. Read the already-existing invalid receipt `.shokunin/audio/corpus/live/runs/20261013T011828577717Z-invalid/measurements.json` (no command executed to generate a new receipt). It contains the six entries and expected/observed statuses listed above. No invalid-mode replay was performed for this scouting task.

## Round-25 implication / limitations

The current implementation can report category-level format rejection, but neither the current combined wrong-format control nor its receipt says whether rate or channel mismatch independently suffices. Native16 is the format positive; native24 is a width negative. Preserve these controls and add the two declared matched cases to test exactly one changed field each. Metadata alone supports the intended format attribution; it does not establish acoustic pass status. No new control was built here, no fit/setup attempt failed, and no claim is made about audio quality, engine behavior, rights, or publication.
