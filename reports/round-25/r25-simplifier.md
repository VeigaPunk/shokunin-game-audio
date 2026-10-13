# Round 25 simplifier review

## Minimal move

Keep the existing `format_failures(stream)` predicate and its `format` classification. Add only the two matched WAV controls to the existing invalid-probe inventory: `sine_48k_stereo_pcm16.wav` (48 kHz, 2 channels) and `sine_44k1_mono_pcm16.wav` (44.1 kHz, mono). Expect each to classify as `format`; preserve the six current entries and their expected statuses. Do not add a predicate, threshold, format-specific validator, compatibility path, or refactor. The evidence is one-factor-at-a-time input isolation against the existing 48 kHz mono PCM16 expectation, not separate error messages for rate and channels.

## Candidate metadata evidence

Both executor candidates are 4.000-second PCM16 440 Hz sine files generated at nominal 0.2 amplitude. `ffprobe` reports the stereo candidate as 48000 Hz, 2 channels, `pcm_s16le`, 16 bits; the mono candidate as 44100 Hz, 1 channel, `pcm_s16le`, 16 bits. Thus each candidate differs from the expected format in exactly one of the two targeted fields; codec and bit depth match.

Exact commands and exits:

```text
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-25/executor/sine_48k_stereo_pcm16.wav
exit 0

ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-25/executor/sine_44k1_mono_pcm16.wav
exit 0
```

## Limits and fit

This is a good fit for the declared narrow depth move if the integrated invalid receipt reports both as `format` and leaves the six existing outcomes unchanged. This review did not run the integrated invalid mode, establish the two expected-failure receipt rows, or independently verify the old controls/hashes; those remain parent integration and verifier work, not passes claimed here. The invalid path inspects metadata and does not run the ordinary acoustic checks on these two candidates, so their peak/RMS/centroid behavior is not established by these commands. No threshold or source code was changed here. No sound-quality, codec-compatibility, engine, rights, or publishing claim follows.

A harness result-display mistake occurred after the first successful `ffprobe`: the command had already returned exit 0, but trying to `await` its completed result object raised `TypeError`. The command was not a failed probe; the second metadata command and output were obtained normally. No other fit/setup failure was encountered in this review.
