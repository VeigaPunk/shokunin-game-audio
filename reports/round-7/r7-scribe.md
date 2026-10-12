# Round 7 scribe — odd-section exception decision table

Scope: draft evidence table for the declared depth move only. This is a report, not a test or verification. I read `.shokunin/audio/LOG.md` and the current `.shokunin/audio/corpus/fixtures/measure_audio.py`. No shell commands were run; therefore there are no command exit codes to report. I did not inspect or make claims about audio perceptual quality, security, or production suitability.

## Before/after decision table

| Evidence point | Before-state / expected behavior | After-state / required evidence | Decision status here |
|---|---|---|---|
| Old section exception on odd input | LOG declares baseline `3b02c31` predates the count-before-split guard; on the exact valid mono PCM16 48 kHz 101-frame odd scratch, `np.split(samples, 2)` should raise `ValueError`. | Independent baseline executor records the exact command, exception and exit, using the named odd scratch. | **Pending**; no odd scratch or baseline report was present when drafted. Do not treat the declared expectation as a reproduced result. |
| New invalid receipt for odd input | Current integrated implementation is expected to reject count 101 against 192000 before split. | `--probe-invalid` should persist `odd_sections` with `observed_failure: "section count"`, section count fields (101 vs 192000), `status: expected_failure`, exit 1, with no traceback. | **Not yet demonstrated.** Current source inspected here iterates only `short_sections`, `corrupt`, and `wrong_format`; no `odd_sections` entry is present in that version. Parent integration and independent verifier evidence are required. |
| Existing invalid controls | Round 6 established three named failure categories for short length, corrupt decode, and wrong format. | Preserve those three statuses while adding the odd case; receipts should be independently replayed. | **Prior-round evidence only**, as summarized in LOG; not a Round 7 replay. |
| Canonical assets and existing controls | Declared guard: ten canonical WAV hashes and old flat/slope/failing/normal behavior remain unchanged. | Non-author verifier compares all ten hashes with `cba2748`, exercises invalid/normal/flat/slope/failing/restore, and reports exact commands/exits/receipts. | **Pending verifier**; no Round 7 results available to this scribe. |

## Narrow decision rule and caveats

Admit the depth move only if the old-source odd-input `ValueError` is directly reproduced and the integrated invalid mode produces a persisted, correctly classified `odd_sections` receipt without traceback, while the independent guard checks pass. Otherwise mark the move unproven or blocked; do not infer success from source inspection or from the even 144000-frame Round 6 short control. This test covers one deliberately odd, structurally short input and one specific precheck path only. It is not evidence about arbitrary malformed WAVs, codecs, security, perceptual quality, or production audio.

No borrowed baseline, verifier, or perceptual/security claims are made in this report.
