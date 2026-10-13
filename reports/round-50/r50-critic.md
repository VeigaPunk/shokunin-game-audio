# R50 critic — stereo interleaving and project measurement

## Scope / setup

Read `.shokunin/audio/LOG.md` Round 50 declaration. This is an independent scratch-pair test of the specified 5760-frame, 48 kHz PCM16 mono/stereo condition, via the unchanged `measure(..., SPECS["ui"])` implementation. I did not edit source, LOG, scorecard, canonical artifacts, or other reports; scratch WAVs were under `/tmp/r50critic-lcq3jby1/` and are not project artifacts.

I generated `x[n] = round(32767*(0.20*sin(2*pi*1200*n/48000) + 0.12*sin(2*pi*2400*n/48000)))` as little-endian PCM16 for n=0..5759. Mono stores x; stereo stores `(x[n],x[n])` per frame. SHA-256: mono `6545bb3ca8bea26f0946b174e09515f9e7374828df38e841cddf669f92874a15`; stereo `4a4b2887b91e805438dc48260dc1557980b62c05d2020729c01381b5be985c9b`.

Exact metadata command, run separately for each file (`mono.wav`, then `stereo.wav`), exit 0:

```sh
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json /tmp/r50critic-lcq3jby1/mono.wav
```

The same command with `stereo.wav` also exited 0. Actual stream metadata: mono `pcm_s16le`, 48000 Hz, 1 channel, 16 bits, format duration `0.120000`; stereo `pcm_s16le`, 48000 Hz, 2 channels, 16 bits, format duration `0.120000`.

Exact SoX decode command, separately for each file, exited 0:

```sh
sox /tmp/r50critic-lcq3jby1/mono.wav -t f32 -e floating-point -
```

and for stereo the same command ending in `stereo.wav`. `numpy.frombuffer(stdout, dtype="<f4")` produced 5760 scalar samples for mono and 11520 scalar samples for stereo. For stereo these are interleaved channel samples, not 11520 audio frames; there are 5760 frames. The project `measure` function FFTs the flattened vector and constructs its frequency grid using the stream sample rate (48 kHz) and flattened sample count.

## Project numeric results

I invoked the project's existing `measure` function directly on the scratch paths with `SPECS["ui"]`, without changing its thresholds/comparator. Actual results:

| Input | Project duration | Project peak | Project RMS dBFS | Whole-vector centroid | Project failures |
|---|---:|---:|---:|---:|---|
| mono | 0.12 s | 0.275909423828125 | -15.65466367368931 | 1651.4403776159181 Hz | none |
| stereo | 0.12 s | 0.275909423828125 | -15.65466367368931 | 1966.6035588188736 Hz | `format: expected 48kHz mono` only |

Both project whole-vector centroids lie inside the declared 250–4000 Hz UI band; duration, peak, and RMS checks pass. The sole stereo failure is the declared format predicate. Decoded mono and stereo peak/RMS coincide here because the stereo channels are identical; this is not evidence about dissimilar channels. The centroid differs despite identical per-channel data: flattening the stereo interleave produces alternating `x[n],x[n]`, a 11520-point FFT while the project frequency grid still uses 48 kHz. Thus this measurement is not an equal-per-channel centroid calculation and is not the same FFT grid as mono. It is the project's observed whole-vector computation, not an assertion of channel-agnostic handling or a general stereo/downmix property.

The direct project invocation attempt via an external `/tmp` path failed before measurement return with `ValueError` at `path.relative_to(ROOT)` (exit 1); that was a **setup/path error**, not a numeric fit. I then loaded the existing module in-process and set only its ROOT for the scratch receipt path to obtain the table above. The project has no R50 integration mode at this point, so this critic did not run a CLI mode or generate project run receipts.

## Conclusion / limits

This deterministic identical-channel pair does **not** falsify the declared sole-format-isolation result: both other UI numeric gates pass, with the stereo rejection attributable only to the channel-count format check. It does expose a calibration caveat: SoX emits interleaved scalar samples, and the existing whole-vector FFT uses sample count but not channel count when forming the frequency grid. Report stereo centroid as the measured project metric, not as either a per-channel result or a channel-agnostic stereo analysis. No failed numeric fits occurred in the final pair; the failed external-path invocation was setup only. No transcription issue. No claim about audition, quality, perception, production, rights, engine, publishing, or promotion.
