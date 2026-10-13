# R50 reviewer — minimal opt-in mono/stereo UI probe design

## Review scope

I read the R50 declaration in `.shokunin/audio/LOG.md` and inspected the current measurement and fixture-builder source. This is a design review only. I did not generate or measure R50 artifacts, so there are no R50 shell command exits, ffprobe metadata, hashes, decoded metrics, or numeric-fit results from this reviewer.

## Smallest mode shape

The requested control pair is a single 5760-frame PCM16 sample sequence represented in two WAV layouts: mono has that sequence once per frame; stereo has that same sequence in both channels for every frame. Both headers must be 48000 Hz. One opt-in invocation that builds both files and calls the existing `measure("ui", SPECS["ui"], path)` for each is smaller and less error-prone than two independently selectable modes: it directly couples the control and candidate and leaves default behavior untouched. If separate flags are required by integration, keep them narrowly named, mutually exclusive, and have both select the same deterministic underlying sequence. Do not add a generic channel mode or broaden any acceptance logic.

For an ordinary paired invocation, preserve the existing `format_failures` predicate and `SPECS["ui"]` unchanged. The expected metadata-only distinction is mono `48000 Hz / 1 channel / pcm_s16le / 16-bit` versus stereo `48000 Hz / 2 channels / pcm_s16le / 16-bit`. The expected outcomes declared in LOG are mono with no failures and stereo with only `format: expected 48kHz mono`. Those are predictions pending actual execution, not measurements in this report. The UI duration, peak, RMS, and whole-wave centroid must be reported for both; do not skip those checks for stereo.

A shared deterministic sample array is the key control: write the same quantized PCM16 sequence into the mono stream and into both stereo channels. The sequence should be selected or confirmed to satisfy the existing UI bounds after the project's actual SoX f32 decode, including its scalar interleaved stereo output. The measurement implementation computes a whole-output-stream FFT and RMS; it does not analyze each channel separately. If the decoded stereo metric fails a bound, report that as a numeric fit failure. Do not change the predicate, UI target, thresholds, or sample sequence after observing results merely to force the declared outcome; any revised signal must be documented as a new choice and both paired files regenerated from it.

## Scope safeguards

- Keep existing rate-probe options, ordinary run, predicate, and other modes unchanged.
- Add only the requested opt-in probe path(s), with no generalized stereo acceptance or channel-handling claim.
- Report actual ffprobe fields and SoX-decoded project metrics, not just file-header assumptions. Distinguish a setup/command failure from a successful measurement that misses a numeric bound, and distinguish both from a transcription correction.
- The stereo scalar decode may interleave channel samples. A passing project result establishes only this particular file's result under the current whole-stream measurement; it does not establish per-channel analysis, channel-agnostic stereo handling, or equivalence of stereo and mono generally.

## Run status and claims

No R50 setup or measurement command was run by this reviewer. Therefore no setup errors, failed numeric fits, or transcription corrections were observed. No audition was performed. This report makes no claim about audio quality, perception, production, rights, engine behavior, publishing, or promotion.
