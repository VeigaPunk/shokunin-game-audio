# R51 scout — PCM16 codec predicate vs ordinary UI gates

## Scope / code reading

Read `.shokunin/audio/LOG.md` R51 declaration. In `corpus/fixtures/measure_audio.py`, `format_failures(stream)` applies two independent format checks: rate/channels must be 48000 Hz/mono (`format: expected 48kHz mono`), and `codec_name == "pcm_s16le"` **and** `bits_per_sample == 16` (`format: expected PCM16`). `measure(..., SPECS["ui"])` then checks duration against `.12 s` with ±`.001 s` tolerance, peak `< .95`, RMS `>= .001` (failure on lower RMS), and whole decoded-vector magnitude-spectrum weighted centroid within `250–4000 Hz`. These do not establish audio quality; they are the fixture's ordinary UI gates.

## Historical native24 probe

Receipt inspected: `corpus/live/runs/20261013T081427532797Z-invalid/measurements.json`, mode `probe-invalid`. Its `native24_probe` entry reports `live/round-22/native24_probe.wav`, expected/observed failure `format`, status `expected_failure`, stream **48000 Hz, mono, `pcm_s24le`, 24 bits/sample**. Historical file SHA-256: `3c7c3db68c1571b4ae14db89d4c15a8a48095189c0bf1d62ab2e291a6fae7125`.

Exact inspection commands (both exit 0):

```text
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-22/native24_probe.wav
sox .shokunin/audio/corpus/live/round-22/native24_probe.wav -t f32 -e floating-point -
```

ffprobe returned duration `4.000000`, 48000 Hz, one channel, `pcm_s24le`, 24 bits/sample. SoX stdout was decoded as little-endian float32, then promoted to float64 for the project's metric math: 192000 values; peak `0.19999992847442627`, RMS `0.14142133818970307` (`-16.98970115181744 dBFS`), centroid `440.04095271509937 Hz`. It is **not** a matched ordinary UI input: duration misses `.12 s` by 3.88 s (beyond ±1 ms), though measured peak, RMS, and centroid are within UI numeric limits. The historical invalid-probe path only records the format check; it does not call `measure` on this probe. Thus it demonstrates a PCM24 format rejection, not an isolated UI candidate where other ordinary gates were shown to pass.

## Ordinary UI reference

For context, inspected existing `corpus/artifacts/ui.wav` (not a new matched R51 control), SHA-256 `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9`. Exact commands, both exit 0:

```text
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/artifacts/ui.wav
sox .shokunin/audio/corpus/artifacts/ui.wav -t f32 -e floating-point -
```

Actual metadata: `.120000 s`, 48000 Hz mono, `pcm_s16le`, 16 bits/sample. Decoded 5760 float32 values; peak `0.375946044921875`, RMS `0.10009574508393186` (`-19.991687666366516 dBFS`), centroid `966.896659337973 Hz`; all cited ordinary UI checks are within bounds. This reference is not paired to the native24 file and does not substitute for the R51 matched PCM24/PCM16 experiment.

No numeric candidate was generated or tuned in this scout, so no failed numeric fit to report. No transcription was run. No setup errors occurred. No inference beyond the specific format predicate, historical probe, and measured fixture gates above.
