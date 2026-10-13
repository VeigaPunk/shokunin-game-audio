# R59 reviewer — conditional valid-bits 13/16 integration proposal

## Scope and evidence status

This is a source-only review. I read `/tmp/mission-audio-standing.md`, the R59 declaration in `.shokunin/audio/LOG.md`, the R58 source wiring and R58 reviewer/executor/alternate reports. The R59 LOG declares a fresh mono 48 kHz, 5,760-frame extensible PCM16-subtype pair: `fmt` size 40, `cbSize=22`, channel mask `0x4`, 16-bit container, shared signed16 payload all divisible by eight, and only `wValidBitsPerSample` differs (13 versus 16).

Current source includes the R58 builder and `--probe-ui-extensible-valid-14-r58` / `--probe-ui-extensible-valid-16-r58` wiring, but no R59 builder or valid-13/16-r59 flags. No R59 fixture was built, parsed, decoded, measured, or run through the integrated runner in this review. Therefore there are **no observed R59 command exit codes, header bytes, ffprobe/SoX metadata, sample vectors, metrics, hashes, or receipts**. R58 outcomes are precedent only and must not be presented as R59 results.

## Minimal conditional two-flag proposal

Add R59 wiring only after the original executor pair has actually been checked and both files meet the declared shape. Specifically, directly parse RIFF and verify `RIFF/WAVE`, a 40-byte extensible `fmt ` chunk, tag `0xfffe`, `cbSize=22`, mono/48,000 Hz, block align 2, 16-bit container, mask `0x4`, PCM subtype GUID bytes `0100000000001000800000aa00389b71`, and `wValidBitsPerSample` 13/16. Confirm same 11,520-byte payload (5,760 signed16 samples), every sample divisible by eight, and the valid-bits field is the only differing header/file byte. Then separately run ffprobe, SoX decode, and the unchanged UI measurement path on each file. Do not infer these properties from the R58 builder, ffprobe `bits_per_sample`, or `sample_fmt`.

If both originals satisfy those checks, the minimal opt-in source change is:

- Add two uniquely named builder flags, `--probe-ui-extensible-valid-13-r59` and `--probe-ui-extensible-valid-16-r59`, that build only under `corpus/live/round-59/`. Reuse one deterministic shared payload for both headers, quantized so all signed16 values are divisible by eight; do not change canonical artifacts or prior round fixtures.
- Add matching runner flags with the existing one-probe-mode exclusivity guard and forward only the selected builder flag.
- Add a small supplemental measurement branch for the selected `pair_valid_{13,16}.wav`, using the existing `measure("ui", SPECS["ui"], path)` and distinct R59 receipt names. Do not add either fixture to canonical, family, section, or `_alt` comparisons.
- Leave `format_failures()`, UI specs/thresholds, prior modes, canonical source inputs, and baseline battery behavior unchanged.

Before describing integration evidence, report the standalone checks. For each flag, record the actual runner exit, receipt path and full relevant receipt metadata/metrics. Compare the independently SoX-decoded vectors (length, equality, differing sample count and maximum difference); report the observed result, including any rejection or numeric gate failure. If a decoder fails before a runner receipt, give its exact command and exit separately as receiptless setup/decode/unsupported evidence; do not call it a runner format failure, numeric gate failure, or receipt. A 78-command replay is conditional: only claim it if the two added modes both produce receipts and the non-author replay actually completes. Do not change thresholds or force a receipt count to match the plan.

## Commands, exits, headers, metadata, and metrics

No external command was run for this review; source files were read through the Python REPL. Thus there are no executed shell commands/exits to report, and all R59 header values above are the **declared target**, not observations. No measured metadata or metrics exist in this report. Commands below are suggested future checks, not executed evidence; their exit statuses are **not observed / N/A**:

```sh
python3 -c 'import struct; from pathlib import Path; p=Path(".shokunin/audio/corpus/live/round-59/executor");
for f in ("valid-13.wav","valid-16.wav"):
 b=(p/f).read_bytes(); i=b.index(b"fmt "); n=struct.unpack_from("<I",b,i+4)[0]; x=b[i+8:i+8+n]; d=b[b.index(b"data")+8:]; print(f,"bytes",len(b),"fmt",n,"tag",hex(struct.unpack_from("<H",x)[0]),"channels",struct.unpack_from("<H",x,2)[0],"rate",struct.unpack_from("<I",x,4)[0],"block_align",struct.unpack_from("<H",x,12)[0],"container",struct.unpack_from("<H",x,14)[0],"cbSize",struct.unpack_from("<H",x,16)[0],"valid_bits",struct.unpack_from("<H",x,18)[0],"mask",hex(struct.unpack_from("<I",x,20)[0]),"guid",x[24:40].hex(),"data_bytes",len(d))'
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt:format=duration -of json .shokunin/audio/corpus/live/round-59/executor/valid-13.wav
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt:format=duration -of json .shokunin/audio/corpus/live/round-59/executor/valid-16.wav
sox .shokunin/audio/corpus/live/round-59/executor/valid-13.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-59/executor/valid-13.f32
sox .shokunin/audio/corpus/live/round-59/executor/valid-16.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-59/executor/valid-16.f32
```

These suggested commands alone do not establish project gate metrics or integrated receipts. Run measurements/runner modes only after the observed header and decoder checks; record each exact invocation and exit in the executor/integrated-run evidence. If the source builder is integrated, its synthetic payload and header checks also need actual validation, not assumption.

## Limits and write boundary

A successful result would concern only the specified 13/16-valid-bit pair, aligned synthetic payload, local ffprobe/SoX/project path and unchanged UI gate. It would not establish valid-bit enforcement, meaningful 13-bit resolution or fidelity, decoder-wide behavior, arbitrary WAVE headers, standards conformance, audibility, quality, production suitability, rights, engine behavior, publishing, or promotion.

I wrote only `.shokunin/audio/reports/round-59/r59-reviewer.md`. No shared source, LOG, SCORECARD, canonical artifact, scratch fixture, or other report was changed; no commit or push was made.
