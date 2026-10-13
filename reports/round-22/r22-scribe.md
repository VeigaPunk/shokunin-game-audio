# r22-scribe — decision table and scope limits

## Basis and current decision

The round-22 declaration identifies a depth gap: `measure()` currently rejects sample rate or channel count mismatches, but its ffprobe query requests only `sample_rate`, `channels`, and container duration. It does not request or validate codec, bit depth, or sample format. The builder emits canonical WAVs as mono PCM16 at 48 kHz. Existing `--probe-invalid` controls cover short/odd section counts, decode corruption, and a wrong-rate/channel format; they do not establish rejection of 48 kHz mono PCM24.

**Decision from evidence presently available to this scribe:** the proposed format-depth rejection is a plausible, narrowly scoped depth move, but it is **not yet demonstrated**. Round-22 PCM24/PCM16 scratch measurements, an integrated invalid-probe receipt, and non-author replay are not present in the material I inspected. Do not treat the table’s target outcomes as observed outcomes or admit the move on this report alone.

## Decision table

| Input/control | Known or required metadata | Existing behavior / evidence | Decision if tested | What it would establish |
|---|---|---|---|---|
| Canonical WAVs | 48 kHz, mono, PCM16 (builder specification) | Existing canonical baseline; declaration requires all 13 hashes and prior coverage outcomes preserved | Must continue to pass; hashes unchanged | No regression for the canonical set, not general format support |
| Matched positive control | Native 48 kHz mono PCM16; `ffprobe` identifies PCM16 (for example `codec_name=pcm_s16le`, `bits_per_sample=16`, or a suitable PCM16 `sample_fmt`) | A direct positive-control receipt is not available to this scribe | Must be accepted by the new explicit PCM16 predicate and retain existing numeric-gate behavior | Predicate admits its intended PCM16 input on this tested path |
| Matched negative control | Same original waveform and duration, written as native 48 kHz mono PCM24; metadata identifies PCM24 (for example `codec_name=pcm_s24le`, `bits_per_sample=24`, or a suitable PCM24 `sample_fmt`) | Current `measure()` checks only rate and channels for the `format` failure; PCM24 rejection has not been measured here. Other numeric gates could independently fail and must not be mistaken for format rejection. | Required isolated outcome: `observed_failure: format` from the new explicit PCM16 predicate, while the paired PCM16 control passes and unrelated gates do not explain the result | Narrow rejection of this PCM24 control by the declared format predicate—not general decoder hardening |
| Existing malformed controls | Short/odd section count; corrupt decode; wrong rate/channel format | Existing controls and outcomes are documented in the round-22 declaration; no round-22 replay was inspected here | Prior expected outcomes must remain; do not relabel these as bit-depth evidence | Preservation of existing invalid-input coverage only |

An acceptance claim requires the actual ffprobe metadata for both matched controls (including the field the implementation really predicates on), a receipt identifying the PCM24 control by name with `observed_failure: format`, the positive PCM16 control accepted by that predicate, unchanged other gates/thresholds, preserved prior outcomes, and the required independent serial replay. If metadata exposes no reliable field for the promised distinction, record a failed fit and narrow the predicate to what source and metadata support; do not force the declared result.

## Limits and failed fits

- This is a WAV/PCM16-only contract for the specified 48 kHz mono fixture path. It does not claim support for arbitrary codecs, containers, export settings, or sample representations.
- A PCM24 control rejected only for level, spectrum, duration, decode, or another legacy gate is **not** evidence for the new format predicate. The PCM16/PCM24 pair should derive from the same original waveform so width is the intended variable.
- `codec_name`, `bits_per_sample`, and `sample_fmt` are examples of candidate ffprobe metadata, not interchangeable guarantees. Report the exact field observed and predicate used; do not claim a broader sample-format rule than tested.
- These numeric/file-format checks say nothing about perception, audibility, sample rights, engine behavior, publishing, or external compatibility.
- No round-22 scratch fit or failure was available to this scribe. The round-21 reports’ unrelated numeric join-probe failed fits are not PCM-width experiments and are not evidence for or against this round’s depth claim.

## Commands and exits

No shell command was invoked for this report. I read the round-22 declaration in `.shokunin/audio/LOG.md`, inspected the current measurement source, and checked for round-22 reports/scratch with Python filesystem reads only. Accordingly there are no shell command exit codes or new audio measurements to report. This report is a decision-table draft, not test evidence.
