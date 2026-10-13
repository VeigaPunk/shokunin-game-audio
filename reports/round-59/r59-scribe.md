# R59 scribe — conditional replay and classification ledger

## Scope and current boundary

Read `/tmp/mission-audio-standing.md`, the R59 LOG declaration, R58 integrated source and reports (including `r58-scribe.md`, `r58-executor.md`, and `r58-verifier.md`), and R57 scribe/verifier context. The declared R59 comparison is a fresh matched 5,760-frame, mono/48 kHz WAVE_FORMAT_EXTENSIBLE PCM-subtype pair: fmt40, `cbSize=22`, mask `0x4`, 16-bit container, identical signed16 payload with every value divisible by eight, and only `wValidBitsPerSample` changed (13 vs 16).

At this inspection, the working tree has no R59 integrated flags/source routing and no R59 pair or replay receipts. The R58 runner and source remain the current integrated baseline; no R59 runner command was attempted. Consequently there is no R59 runner exit code or receipt yet, and the planned 78-command ledger is conditional on integration and both new probes producing receipts. I did not replay any command before integration. This report records the replay boundary and mapping, not a replay or integration claim.

## Conditional 78-command serial ledger plan

After integration, replay serially in this order: fresh normal baseline (#1); the two R59 probe commands (#2 valid13, #3 valid16); then the prior R58 76-command sequence as fresh #4–#78. The mapping is prior R58 #1 → fresh #1 and prior R58 #2–#76 → fresh #4–#78. Record for every actual invocation its exact command, process exit, receipt path if any, and receipt classification. The first three command forms are expected to be:

```sh
python3 .shokunin/audio/corpus/fixtures/measure_audio.py
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-valid-13-r59
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-valid-16-r59
```

These two flag spellings are conditional expectations from the round declaration, not observed integrated CLI options; use the actual integrated option names. For the remaining 75 commands, use the exact R58 verifier ledger order and commands, substituting fresh invocations and receipt paths; do not infer outcomes from prior exits. Validate that the mapped prior commands, exits, and complete JSON objects (including all mode/failure fields) match R58 exactly, and that first/final normal JSON matches. If either new mode does not yield a receipt, report actual attempts and classify the shortfall; do not claim 78 receipts or force a replay count. Preserve canonical17, controls, and unchanged threshold evidence as in the R58 verifier.

## Classification rules / evidence to collect

- **Setup / no receipt:** invocation, option, path, or environment error before a measurements JSON exists. Record exact command and exit/stderr; it is neither decode nor numeric-gate evidence. Do not count it among receipts.
- **Decode / format outcome:** only classify as such when a runner receipt reports the actual decode/format failure, or independent ffprobe/SoX commands on the selected pair fail and their exact command/exits are recorded. Distinguish independent-tool results from runner outcomes.
- **Numeric failure:** a receipt exists and reports a selected probe measurement/gate failure. Record the exact failed field/reason; do not call it setup or adjust thresholds.
- **Clean probe:** receipt exists, command exit and measurement failures are recorded, with actual sample count/format/metrics. Direct measurements are not runner receipts.
- **Report transcription:** an inaccurate statement in a report that conflicts with raw artifact/receipt evidence; correct it explicitly, without relabeling underlying gate evidence. Keep any historical report correction separate from R59 run outcomes.

Before replay, validate the selected pair's RIFF fields and hashes; independently record ffprobe and SoX command/exits and decoded vector count/equality; run unchanged direct UI measurement only as supplementary evidence. Do not assume valid13 acceptance, equality, or clean numeric fit.

## Historical setup and transcription context (not R59 results)

R58 scribe documents one initial direct-measure relative-path error (`ValueError`, exit 1), corrected with absolute paths; this was scribe setup, not a runner receipt, decode failure, or numeric fit. R58 executor likewise documents relative-path direct measurement setup errors, later corrected; R58 alt had a malformed inspection attempt before correction. R58 verifier reports no receiptless/setup attempt in its 76-command replay. These are separate event types and must not be merged into a future R59 outcome. R58 reports also corrected a scout's R57 historical SHA/alignment mix-up as report transcription, not R58 gate evidence. No analogous R59 error or transcription has been observed.

## Limits and writes

No source, LOG, SCORECARD, canonical artifact, or other report was changed. No commit, push, or replay was made. This is a conditional ledger specification only; it makes no claim about valid-bit metadata enforcement, meaningful resolution/fidelity, general WAVE extensible or decoder behavior, audibility, quality, production, rights, engine, publishing, or promotion.
