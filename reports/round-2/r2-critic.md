# Round 2 critic: distinctness and loop-seam proxies

## Scope

I attempted to falsify the declared “distinct” and loop-endpoint criteria using their written definitions and the existing measurement implementation. This is an analytical counterexample review, not an audio-quality judgment. I did not synthesize or publish samples, run shell commands, or edit fixture code.

## Distinctness threshold: concrete counterexample

The claim accepts a variant if its measured duration differs from baseline OR its full-signal magnitude-weighted spectral centroid differs by at least 10%, while each still passes the coarse fixture bands and ±1 ms duration check. This is not a robust proxy for perceptual or functional distinctness.

For duration, baseline tolerance permits a legal duration shift up to 1 ms in either direction. A variant whose duration changes by, for example, 0.5 ms meets a literal “distinct duration” test (if defined as any nonzero difference), yet is unlikely to be distinguishable as an SFX; it may also be less than one video/audio frame at common rates. The claim does not state a minimum delta for this alternative, unlike its centroid alternative. If “distinct duration” instead means a larger threshold, that threshold is currently unspecified and the claim cannot be replayed consistently.

For centroid, a single aggregate can shift without a meaningful change to the salient body of the sound. E.g. preserve the baseline waveform for all but a very short tail and add a quiet, high-frequency transient there; a brief tail can disproportionately pull a magnitude-weighted centroid while the event remains functionally the same, and its peak/RMS can remain within bounds. Conversely, a perceptually obvious envelope or rhythmic change can leave the global centroid within 10%. Therefore the test establishes numerical difference on one descriptor, not distinctly different sound/function. This is especially weak given the recorded limitation that centroid is global and time-varying spectrum is discarded.

There is also an integration limit: the current `measure_audio.py` `SPECS` and measurement loop enumerate only `ui`, `impact`, `movement`, `ambience`, and `stem`; the existing builder rewrites only those five named artifacts. Until the parent integrates variant names and measures raw variant files, a passing five-item receipt cannot establish the round-2 claim about eight SFX. This is an observability gap, not evidence that any proposed variant fails.

## Loop endpoint proxy: concrete counterexample

The current proxy is `abs(samples[0] - samples[-1]) <= .03`. It constrains only endpoint amplitude. A constructed sequence can have `samples[0] == samples[-1] == 0` (delta exactly zero), but `samples[1] = +0.5` and `samples[-2] = -0.5`. The amplitude matches at the join, while adjacent differences around the boundary are large and have opposite signs: a derivative/slope discontinuity remains. A smooth periodic waveform can be modified to have these local neighbor values without changing the equal endpoints. Thus this check can pass a loop with a sharp cusp/click-like transient at or near the join; it does not establish seamless playback.

The other direction is also limited: a small endpoint amplitude difference can pass the .03 bound while becoming audible depending on gain, playback level, spectral context, codec, or repeated loop rate. Raw PCM endpoint values alone do not resolve that.

## Verdict / useful bound

The written threshold is falsifiable as a deliberately narrow fixture proxy, but not as a claim of perceptual distinctness or loop quality. Preserve that distinction in any round verdict. At minimum, define a nonzero duration-difference threshold (or remove duration as a distinctness route), retain the raw per-variant measurements, and describe the endpoint metric as an amplitude-jump check only. A stronger seam proxy would inspect local first-difference/slope near the join and still require playback/context checks before a perceptual claim. These are suggested scope clarifications, not requested code changes.
