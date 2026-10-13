# R60 scribe — conditional replay and outcome-classification ledger

## Scope and current boundary

Read `/tmp/mission-audio-standing.md`, the R60 LOG declaration, and R59 integrated source/reports, including `r59-scribe.md`, `r59-executor.md`, `r59-alt.md`, `r59-verifier.md`, and `r59-critic.md`. R60 declares a deliberately malformed WAVE_FORMAT_EXTENSIBLE PCM-subtype header pair: 5,760-frame mono 48 kHz, fmt40, `cbSize=22`, mask `0x4`, 16-bit container, identical signed16 payload; only `wValidBitsPerSample` differs (invalid/unspecified 0 versus control 16). This is not a conforming positive case.

The working tree currently has R60 executor and alternate scratch fixtures but no integrated R60 CLI flags/source routing, no R60 measurement receipt, and no R60 runner invocation. Therefore there is no R60 runner exit code, validation failure, decoder failure, numeric-gate result, or replay ledger yet. **Do not report an 80-command replay as completed.** The 80-command count is conditional on integrating both probes and both runner commands producing receipts. Direct decoder/tool checks below are independent inspection, not runner receipts.

## Fixture/tool observations (not runner receipts)

Executor fixture inspection command, exit **0**:

```sh
python3 .shokunin/audio/corpus/live/round-60/executor/inspect.py
```

It reports both files are 11,588 bytes, RIFF size 11,580, WAVE, fmt size 40, tag `0xfffe`, mono, 48,000 Hz, byte rate 96,000, block align 2, 16-bit container, `cbSize=22`, mask `0x4`, PCM subtype GUID `0100000000001000800000aa00389b71`, 11,520 data bytes / 5,760 samples. Valid bits are 0 and 16. Executor WAV SHA-256: valid0 `5ab169fc3f43b29c0bb17cc86e6b76fb424e590b7d788a503a002501c8a2f394`; valid16 `d7f08d659b608e003e5ef2aaccf325dae3bd4e961caeaa450bd933c406b4cc46`. Identical payload SHA-256: `6e76d877b1e153b636b883f06dea7d3fd7f43374a72fa2cba678c8f4560c9711`. The `wValidBitsPerSample` field is the intended sole header difference. Independent alternate files also exist under `corpus/live/round-60/alt/`, with different shared payload SHA `b90445495a6598319bfd12fe33452957711d2987004393119cfae752e6654a4b`; they are scratch evidence, not integrated runner inputs.

Exact ffprobe command for executor valid0 (exit **0**):

```sh
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt:format=duration -of json .shokunin/audio/corpus/live/round-60/executor/valid-0.wav
```

The same command with `valid-16.wav` also exited **0**. Both report `pcm_s16le`, `s16`, 48,000 Hz, mono, 16 bits/sample and duration `0.120000`; ffprobe exposes container/codec observations, not the differing valid-bits field.

Exact SoX decode commands (each exit **0**):

```sh
sox .shokunin/audio/corpus/live/round-60/executor/valid-0.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-60/executor/valid-0.f32
sox .shokunin/audio/corpus/live/round-60/executor/valid-16.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-60/executor/valid-16.f32
```

A direct vector comparison command (exit **0**) found 5,760 float32 samples each, exact equality, zero differing samples, maximum difference `0.0`, and both vector SHA-256 `adc56a24cd7a2bc4c34ef6112b384b3567f6d6b1e4568aef0c8722f6170dca6c`:

```sh
python3 -c 'import numpy as np,hashlib; from pathlib import Path; p=Path(".shokunin/audio/corpus/live/round-60/executor"); a=np.fromfile(p/"valid-0.f32",dtype="<f4"); b=np.fromfile(p/"valid-16.f32",dtype="<f4"); print("samples",len(a),len(b),"equal",np.array_equal(a,b),"different",int(np.count_nonzero(a!=b)),"maxdiff",float(np.max(np.abs(a-b))),"sha0",hashlib.sha256(a.tobytes()).hexdigest(),"sha16",hashlib.sha256(b.tobytes()).hexdigest())'
```

Unchanged direct project `measure()` command (exit **0**):

```sh
python3 -c 'import importlib.util; from pathlib import Path; s=importlib.util.spec_from_file_location("m", ".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); p=Path("/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-60/executor"); [print(m.measure("ui",m.SPECS["ui"],p/f)) for f in ("valid-0.wav","valid-16.wav")]'
```

Both direct results have duration `.12`, 48 kHz mono `pcm_s16le`/16-bit, peak `0.082489013671875`, RMS `-26.87354274685677 dBFS`, centroid `2139.5871109211243 Hz`, bandwidth `3627.575019576501 Hz`, LUFS null, and `failures: []`. These are direct measurements, not project-runner receipts. Current source has no valid0 R60 flag/routing. This direct pass cannot be substituted for a runner result or used to claim valid0 acceptance by the integrated runner.

## Conditional 80-command replay ledger

Only after integration, run serially: fresh normal baseline (#1), the actual integrated valid0 probe (#2), valid16 control (#3), then the R59 verifier's designated ledger commands #2–#78 as fresh #4–#80. This is prior78 plus two R60 probe receipts: the fresh normal #1 maps to prior R59 #1, while prior R59 #2–#78 map to fresh #4–#80. Record each exact command, process exit, receipt path, and receipt classification. Use the actual integrated option names, not guessed ones. Confirm prior mapped complete JSON objects and exits against R59 and first/final normal equality. The 80 count is justified only if both selected modes yield receipts; if valid0 is rejected before receipt, report that actual attempt and do not pad or claim 80 receipts. Record each exact command, process exit, receipt path, and receipt classification. Use the actual integrated option names, not guessed ones. Confirm prior mapped complete JSON objects and exits against R59 and first/final normal equality. The 80 count is justified only if both selected modes yield receipts; if valid0 is rejected before receipt, report that actual attempt and do not pad or claim 80 receipts.

For the selected pair, independently record header hashes/fields, ffprobe and SoX commands/exits, decoded sample count/equality, and actual runner receipt or absence. Keep these categories separate:

- **Setup / receiptless invocation:** wrong/missing flag, environment or path problem before runner receipt. Record exact command, exit, stderr; it is not decoder or gate evidence.
- **Decoder/format failure:** independent ffprobe/SoX rejection is their tool outcome. A runner decode/format result requires its actual receipt and error classification. If decoder rejects before receipt, identify as receiptless decode/setup outcome, not validation failure.
- **Validation failure:** runner produced a receipt and reports the existing format/validation predicate failure for selected valid0. Preserve exact error/field and exit. Do not call this a decoder failure or a numeric fit.
- **Numeric gate failure:** receipt exists and selected measurements fail a UI numeric gate. Name field and actual failure; do not adjust thresholds.
- **Clean probe:** receipt exists, exit and failures are recorded. Do not infer valid-bit semantics from PCM16/container metadata.
- **No receipt:** explicitly state whether the attempt reached decoder, project validation, or failed earlier; do not manufacture a receipt or count it in the 80.

R59 verifier disclosed a separate complete 78-receipt rehearsal in addition to its designated 78-command replay; the rehearsal was object-for-object identical, caused by mistaken belief the first results were lost after a receiptless malformed shell invocation. For the R60 baseline, use only the designated R59 ledger's 78 receipts once, not 156. If an R60 rehearsal/duplicate occurs, disclose its full boundaries, relationship, reason, and whether paths/JSON are duplicated; do not add it to the designated count or silently discard it. A zero-receipt setup invocation is not a replay and does not justify repeating a successful receipt-producing sequence.

## Limits and writes

Current findings are limited to these fixture bytes and the host ffprobe/SoX/direct-measure path; malformed `valid_bits=0` is not a standards-conforming positive example. No valid-bit enforcement, universal decoder behavior, real zero-bit audio, precision/fidelity, audibility, quality, production, rights, engine, publishing, or promotion claim. No runner was invoked; no setup failure or runner validation/decode/numeric failure was observed. I changed no shared source, LOG, SCORECARD, canonical artifact, or other report. This scribe artifact is the sole intended write; no commit or push.
