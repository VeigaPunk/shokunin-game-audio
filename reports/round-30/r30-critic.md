# Round 30 critic — falsification of orientation evidence

## Finding

The proposed numerical orientation effect survives a direct check on the four supplied scratch WAVs, but the available evidence is a pre-integration scratch check, **not** a round-30 runner execution or replay. I found no round-30 flags/modes in `measure_audio.py` at inspection time. Consequently, this does not validate the declared two-mode wiring, receipt naming/attribution, or runner's `_alt` pairing for round 30.

## Byte identity and role names

The four files in `.shokunin/audio/corpus/live/round-30/alt/` are each 5760-frame, 48 kHz, mono PCM16 WAVs. SHA-256 results show the intended swaps are exact at the whole-file byte level:

| Filename | SHA-256 | Role asserted by filename |
|---|---|---|
| `forward-base.wav` | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` | higher-centroid baseline |
| `forward-variant.wav` | `6e626b9b5b177cd6f7ba986758b12ec612cf003f9947bd170b766f1652d9bac2` | lower-centroid alternate |
| `reverse-base.wav` | `6e626b9b5b177cd6f7ba986758b12ec612cf003f9947bd170b766f1652d9bac2` | lower-centroid baseline |
| `reverse-variant.wav` | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` | higher-centroid alternate |

Thus `forward-base == reverse-variant` and `forward-variant == reverse-base` byte-for-byte; file headers and sample payloads are included in this comparison. The names and hashes agree on the intended role swap. That validates only these artifacts, not their provenance from a forthcoming integrated builder or attribution in an eventual runner receipt.

## Direct measurement and denominator check

The available direct script measured forward base/variant centroids as `966.8966593379727` / `871.155504521436` Hz, and reverse base/variant as `871.155504521436` / `966.8966593379727` Hz. All four were 0.12 s, 5760 frames, 48 kHz mono PCM16. Peak values were ~0.376 and RMS ~0.1001. These values lie within the declared UI duration, level and 250–4000 Hz centroid bands; this is a direct value check, not a canonical runner ordinary-check receipt.

With duration delta zero, the existing baseline-denominator formula predicts:

- forward: `abs(871.155504521436 - 966.8966593379727) / 966.8966593379727 = 0.09901901500217196`, below `.10` (centroid arm does not pass);
- reverse: `abs(966.8966593379727 - 871.155504521436) / 871.155504521436 = 0.10990133715464667`, above `.10` (centroid arm passes).

This is a numeric denominator-orientation effect for this pair. The absolute difference is the same; the denominator follows the baseline. It is not evidence that symmetric normalization is expected or normative, or that these signals are perceptually similar.

## Falsification boundaries / evidence scope

- No discrepancy in byte identity, filenames-to-hash role mapping, or the stated ratio orientation was found for the scratch artifacts.
- The round-30 runner modes do not yet appear integrated in the inspected source. No end-to-end test establishes that swapped bytes reach the intended baseline and `_alt` measurement names, that both receipt modes select the right label, or that ordinary checks and sole distinctness outcomes are correctly attributed.
- Therefore do not count the direct scratch measurements as the declared round-30 runner evidence or as independent replay. They support fit feasibility only. A successful forward runner receipt should show the below-cutoff distinctness failure and reverse should pass, with both ordinary checks clean; swapped file hashes and receipt baseline labels should be checked then.
- No failed fit or setup attempt was made by this critic; no failed attempt is evidence. No canonical artifacts or shared source were changed.

## Commands run and exits

From repository root:

```sh
sha256sum .shokunin/audio/corpus/live/round-30/alt/*.wav
```
Exit `0`; hashes above.

```sh
python3 .shokunin/audio/corpus/live/round-30/alt/measure_direct.py .shokunin/audio/corpus/live/round-30/alt/forward-base.wav .shokunin/audio/corpus/live/round-30/alt/forward-variant.wav .shokunin/audio/corpus/live/round-30/alt/reverse-base.wav .shokunin/audio/live/round-30/alt/reverse-variant.wav
```
This exact spelling was **not** used; the actual final argument was `.shokunin/audio/corpus/live/round-30/alt/reverse-variant.wav`. The actual command exited `0` and printed the four measurements above. (No need to rerun.)

```sh
grep -n -E 'ui_lower_centroid|lower_centroid|round-29' .shokunin/audio/corpus/fixtures/build_artifacts.py; git status --short
```
Exit `0`; inspected builder remains round-29-labelled for lower-centroid probes; status showed existing LOG modification and untracked round-30 corpus/reports from other work, not changes made by this critic.

Python inspection (not a shell command) confirmed the four WAV frame/format parameters and the matching hashes. No canonical runner invocation was made because round-30 modes were not present at inspection.

## Scope

Numeric baseline-denominator orientation only. No perceptual similarity or audio-quality conclusion; no symmetry normative claim, rights, engine, publishing, or promotion claim.
