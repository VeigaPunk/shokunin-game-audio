# Round 21 scout — internal-gap gate polarity and baseline

## Scope
Read-only mapping for the declared 983/984-count 200 Hz internal-join calibration probe. I did not edit builder/runner code, canonical artifacts, or the LOG. I did not run the audio runner, generate scratch, or independently reproduce any receipt; the baseline numbers below are cited from the committed round-20 verifier/adjudicator reports and source inspection. They are not round-21 integration evidence.

## Gate and polarity

In `.shokunin/audio/corpus/fixtures/measure_audio.py`, `section_contrast()` decodes the WAV with `sox ... -t f32 -e floating-point -`, then computes `internal_join_adjacent_delta_full_scale = abs(samples[96000] - samples[95999])`. The later runner gate independently appends `sections: internal join adjacent sample gap > .03 full scale` when that measured value is **strictly greater than** `.03`. Thus equality passes this predicate; a value at or below `.03` passes it, and only `> .03` fails it. The receipt names the corresponding maximum as `internal_join_adjacent_delta_max_full_scale: 0.03`.

This is one section-level gate, separate from section contrast/validity, the internal side-slope limit (`> .001` fails), generic format/duration/level/centroid gates, and outer-loop endpoint/slope gates. `section.passed` means contrast/validity only; it does not summarize the complete runner failure list. A round-21 pass/fail pair supports the polarity claim only if other relevant gates remain passing and the runner reports the intended isolated outcome.

## Baseline evidence

- Round 20's selected `join200_probe` receipt is documented in `.shokunin/audio/reports/round-20/r20-verifier.md` and `.shokunin/audio/reports/round-20/r20-adjudicator.md`: measured adjacent gap `.030029296875` FS, reported as the sole failure, with side-slope `0.0`, valid 200 Hz contrast `10.457519263296449` dB, and centroid in-band. The selected scratch had PCM values `pcm[95999]=-145`, `pcm[96000]=839`, a difference of 984 counts. This selected builder includes a 220/330 Hz bed; it is not a two-frame waveform-identical corruption of the canonical 200 Hz stem. The earlier round-20 failed fit had both centroid and gap failures and is not the selected evidence.
- The round-20 non-author replay preserved 13 canonical WAV hashes and prior failure kinds; see `r20-verifier.md`. That is historical baseline evidence, not replay of the round-21 pair.
- Source polarity is directly inspectable at the condition `result["internal_join_adjacent_delta_full_scale"] > .03`; no independent execution was done for this report.

## Boundary arithmetic and limits

For the declared PCM16 count comparison, `.03 * 32768 = 983.04` counts. Therefore 983 counts normalize to `983/32768 = 0.029998779296875` FS, which is `0.000001220703125` below the bound and should pass the strict gap predicate. 984 counts normalize to `984/32768 = 0.030029296875` FS, which is `0.000029296875` above and should fail it. The adjacent quantized integer values straddle the threshold; there is no integer PCM16 count exactly equal to `.03 * 32768`.

This arithmetic predicts the predicate for a measured 983- or 984-count adjacent difference. It does not show the round-21 builder preserves other gates, that SoX reports those exact values for generated controls, that runner modes are wired correctly, or that the full run has isolated failures. Nor does a numerical sample-gap threshold establish audibility, perceptual click risk, or a universal threshold. Those require the specified scratch receipts and non-author replay.

## Commands run by this scout

Exact shell command: `git rev-parse HEAD && git status --short` — exit **0**. Output: HEAD `b1af040b3cca2e70dabaafa982c5261c971d03a9`; pre-existing worktree changes shown by Git were `M .shokunin/audio/LOG.md`, `?? .shokunin/audio/corpus/live/round-21/`, and `?? .shokunin/audio/reports/round-21/`. I made no shell edits. No audio check was run (so there are no runner exit codes to report).
