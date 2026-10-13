# Round 32 critic — mixed-signal attribution and duration confound

## Scope and result

I read the declared Round 32 specification in `.shokunin/audio/LOG.md`. At the time of review, there is no Round 32 integration, receipt, or generated pair in the workspace; therefore I cannot validate an observed Round 32 comparator outcome. I did not run shell commands or alter project code, fixtures, thresholds, or canonical assets. This is a falsification review of what the specified result could establish, not confirmation of a run.

## Attribution challenge

The proposed pair changes duration (5760 vs. 6719 frames) and centroid together. If an eventual receipt confirms `0 < duration_delta < .020 s`, `centroid_relative_delta >= .10`, ordinary per-file checks pass under their declared specs, and `_alt` passes, that is consistent with the current OR comparator taking its centroid arm. It does not isolate centroid as a cause independent of duration: changing the sample count changes the waveform analyzed by the whole-file FFT, and can itself change the measured centroid. The fixture also changes its time support, not merely a single spectral parameter. A matched-duration centroid contrast (or other controlled comparison) would be needed to support stronger causal attribution; the round's single joint pair cannot do that.

The claim should be limited to a specific measured mixed-input comparator observation, conditional on the actual receipt. Do not describe it as proof that centroid alone caused a perceptual distinction, that the duration signal has no effect, or that the OR rule is universally validated. Verify the comparator fields and failure list from the runner receipt rather than infer branch selection from coefficient choices.

## Separately declared duration confound / conformance

The proposed variant is 6719/48000 s = 0.1399791667 s, about 19.979 ms longer than the 0.120 s baseline. It is not within canonical UI duration tolerance (0.120 ± 0.001 s). Measuring the variant with a separately declared 6719/48000 s spec can show that its ordinary checks pass against that scratch spec; it does not make it canonical-duration-conforming. Preserve that distinction in any report. A passing ordinary-check set under the scratch spec is not evidence of canonical duration conformance.

Even if the measured duration delta is below the distinctness duration threshold, duration remains a deliberately changed input and a plausible influence on centroid. The receipt must separately show the actual ffprobe durations/delta, centroid values/relative delta, per-file failures, and comparator result. If the actual delta reaches .020 s, the claimed centroid-arm-only observation is falsified; if centroid delta is below .10, the OR pass is not established. If either ordinary check fails, the stipulated outcome is not met. Failed tuning/setup attempts, if any, should remain separately classified and not be reinterpreted as a gate result.

## Commands and evidence

No shell command was run; there are no command exit codes or failed fit/setup attempts to report. Declared LOG context only: Round 31's integrated joint-below observation had duration delta `0.019978999999999997` and centroid-relative delta `0.09964036511023265`, with the OR failing. That is a different comparator quadrant and does not validate the Round 32 proposed pair.

No claim here about perceptual/audible distinctness, causal independence, exact threshold equality, rights, engine behavior, publication, or promotion. No changes to `.020`/`.10` or canonical `.12 s` duration.
