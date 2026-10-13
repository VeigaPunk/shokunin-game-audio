# R52 scout — current PCM format predicate and prior invalid coverage

## Finding

In `corpus/fixtures/measure_audio.py`, `format_failures(stream)` currently has two independent format checks:

- `sample_rate == 48000` and `channels == 1`, else `format: expected 48kHz mono`.
- `codec_name == "pcm_s16le"` **and** `bits_per_sample == 16`, else `format: expected PCM16`.

The second check rejects PCM8 WAV metadata (`pcm_u8`, 8 bits) as `format: expected PCM16`. The ordinary `measure(name, spec, path)` invokes these same checks, then evaluates duration against the chosen spec (UI target `.12 s`, tolerance ±`.001 s`), peak `<.95`, RMS `>=.001`, and whole decoded-vector centroid within that spec’s band (UI 250–4000 Hz). A format rejection by itself does not show the other UI gates pass; the invalid-probe branch is metadata-only.

## PCM8 WAV identification

I made a tiny mono 48 kHz, 5760-frame PCM8 WAV in the allowed scout scratch directory `.shokunin/audio/corpus/live/round-52/scout/pcm8-identification.wav` (5,804 bytes; this is an identification example, not a measured UI candidate). Exact command and exit:

```sh
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt,duration:format=duration -of json .shokunin/audio/corpus/live/round-52/scout/pcm8-identification.wav
```

Exit **0**. ffprobe identifies `codec_name: pcm_u8`, `sample_fmt: u8`, `bits_per_sample: 8`, `sample_rate: 48000`, `channels: 1`, duration `.120000` s. This establishes what ffprobe reports for this generated WAV; I did not run it through the project measure/runner, so this report does not claim measured numeric-gate results or a runner receipt for it.

## Prior invalid coverage

Current `invalid_probes()` enumerates eight historical controls: `short_sections`, `corrupt`, `wrong_format`, `odd_sections`, `native16_probe`, `native24_probe`, `stereo48_probe`, and `mono441_probe`. There is no PCM8/native8 entry. Existing `native24_probe` tests the PCM-depth predicate in the opposite direction (mono 48 kHz `pcm_s24le`, 24 bits), not a below-16-bit WAV. The combined `wrong_format` and rate/channel controls test rate/channel mismatches, not 8-bit depth. Thus the prior invalid set does not contain a dedicated PCM8 control. Its format-invalid branches check metadata only rather than all ordinary UI gates.

No source or existing artifact was changed. I did not attempt an ordinary UI numeric fit or make a report-transcription correction. The only shell command run was the successful ffprobe command above; no test runner was run. No claims beyond the current predicate and this WAV’s metadata identification are made.
