# Round 34 scout — impact baseline, generation, and pair measurement

## Existing impact baseline

The clean-before state recorded in `LOG.md` is commit `d6bfc6ea374e634fd6eb1322030d014612ff98cb`, with 14 deterministic canonical WAVs. Impact currently has exactly two: `corpus/artifacts/impact.wav` and `impact_alt.wav`. Both are declared `.32 s`, 48 kHz mono PCM16, with ordinary centroid band 50–15,000 Hz; peak must be `< .95` and RMS `> .001`. The logged baseline values are approximately 10,843 Hz centroid for `impact.wav` and 474 Hz for `impact_alt.wav`; their durations match. The original generic `_alt` comparison passes via centroid, not duration. Round 2’s executor report (`reports/round-2/r2-impact.md`) records the measured values: baseline centroid 10,843.127 Hz, RMS .09548, peak .80878; alt centroid 473.792 Hz, RMS .13599, peak .75616. Those values were measurements of decoded WAV data, not subjective judgments.

## Original generation and measurement provenance

`corpus/fixtures/build_artifacts.py` regenerates the canonical pair at 48 kHz. The baseline is a 0.32-second sum of a 90 Hz decaying sine (`.40 * sin(2π90t) * exp(-16t)`) and deterministic Gaussian noise (`.23 * noise * exp(-65t)`); the shared `default_rng(20261012)` makes the noise repeatable. The alt is a deterministic sum of 95, 340, and 900 Hz decaying sines with respective amplitudes .55/.25/.12 and decay exponents 14/35/50. `save()` clips, rounds to signed little-endian PCM16, then writes mono WAV. The round-2 report documents the alt expression, 15,360 samples, and no source-audio input. A third impact should be newly generated analytically; copying or merely renaming the current alt would not add an independent fixture.

`measure_audio.py` probes duration/stream properties with ffprobe and decodes samples to float32 with SoX. Its centroid is the whole-file magnitude-weighted positive-frequency FFT centroid: `abs(rfft(samples))`, weighted by `rfftfreq`, divided by summed magnitudes. It also measures RMS, peak, bandwidth, and optional loudness; ordinary checks require 48 kHz mono PCM16, duration within ±1 ms of the declared spec, peak `<.95`, RMS `>=.001`, and centroid inside the declared band. The comparison uses absolute duration difference and relative centroid difference from the named baseline: `abs(candidate_duration - baseline_duration)` and `abs(candidate_centroid - baseline_centroid) / baseline_centroid`. It passes if duration delta `>= .020 s OR` centroid-relative delta `>= .10`. For the round-34 proposal, explicit comparisons should use `impact` and `impact_alt` each as baseline against `impact_third`; keep the existing generic `_alt` comparison and thresholds unchanged. A third-family receipt is only a numeric proxy and does not establish perceptual distinctness.

## Pairing implications / caveats

Because the two existing impact fixtures are both .32 s, a .40 s candidate with a valid measured duration yields an `.08 s` duration delta against each and therefore passes the existing OR rule even if its centroid barely differs. The declared round spec also prefers relative centroid difference >=.10 against each; that is a stronger additional fit objective, not an existing distinctness threshold. The broad common centroid band only says each measurement is in 50–15,000 Hz; it does not assure frequency novelty. Confirm both per-pair measured deltas and all ordinary checks after generation. Preserve the old fourteen WAV hashes/metrics during integration and independently verify the new file/hash before admission.

This is only an analytic fixture/proxy map. No audition or sound-quality, production-readiness, rights, engine, publication, or promotion claim is made.

## Shell activity

No shell commands were run for this report; consequently there are no shell exit codes. Source and report provenance above were inspected as text. No fit was attempted here, and no failed synthesis or setup attempt is being counted as fit evidence.
