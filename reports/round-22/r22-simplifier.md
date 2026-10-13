# r22-simplifier — depth-axis minimality review

## Finding

The current format rule is repeated: `measure()` rejects non-48-kHz/non-mono streams, while `invalid_probes()` independently repeats those same comparisons for `wrong_format`. Adding PCM16 checks in both places would grow that duplication and risks the two paths disagreeing.

## Smallest coherent integration (recommendation only; no shared edits)

Use one format predicate over ffprobe stream metadata, and call it from both `measure()` and the invalid-probe classifier. Extend the existing ffprobe selection in both call sites to include `codec_name`, `bits_per_sample`, and `sample_fmt`; have the shared predicate require 48,000 Hz, one channel, and the explicitly supported PCM16 representation (at minimum `codec_name == "pcm_s16le"` and `bits_per_sample == 16`). Keep the ordinary measurement result’s existing `format: ...` failure category and have invalid probes classify a failed predicate as `format`. This is a local helper/refactor, not decoder hardening or arbitrary export support. If tool metadata for the generated native PCM16 control does not meet the proposed representation, stop and use only a metadata predicate demonstrated by the fixtures; do not weaken the control or infer support for other encodings.

The PCM24 invalid control should be a matched 48-kHz mono rendering of the same source, and its receipt should preserve the relevant ffprobe metadata and show `observed_failure: format`. The positive PCM16 control should be checked by that same predicate, independently of level/spectrum checks. Preserve all existing numerical audio gates and invalid outcomes.

## Axis and limits

This identifies the smallest way to implement the declared depth change without duplicated format policy; it is a design review, not evidence that the axis improved. I did not run controls, perform an integration, or verify the ffprobe fields on the candidate WAVs, so the PCM24/PCM16 behavior and predicate acceptance remain unproven here. No failed-fit experiments were run. No shell commands were invoked (therefore no shell exit codes to report). No claim about sample rights, perception, engines, publishing, other codecs, or general format compatibility.
