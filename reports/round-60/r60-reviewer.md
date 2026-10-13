# R60 reviewer — conditional malformed-valid-bits 0/16 integration

## Scope and evidence status

This is a source-only review. I read `/tmp/mission-audio-standing.md`, the R60 declaration in `.shokunin/audio/LOG.md`, current `build_artifacts.py` and `measure_audio.py`, and R59 source/reports (`r59-executor`, `r59-alt`, `r59-reviewer`, `r59-simplifier`, `r59-scribe`, `r59-guard`, plus the R59 declaration/closeout). The R60 declaration specifies 5,760-frame mono 48 kHz WAVE_FORMAT_EXTENSIBLE PCM-subtype headers, fmt40/cbSize22/mask0x4, 16-bit container, same UI-shaped signed16 payload, comparing `wValidBitsPerSample=0` against 16. The zero value is explicitly malformed/unspecified, not a conforming positive case.

Current source already contains R59 valid13/16 builder and two opt-in modes. I found no R60 valid0/16 builder or R60 flags. R59 provides a narrow pattern, not R60 evidence: its executor recorded direct RIFF checks, ffprobe/SoX decode and direct UI measurements on a conforming 13/16 pair. In that R59 setup both files decoded to equal 5,760-sample vectors, but that cannot predict malformed valid0 handling. This review did not generate/inspect an R60 file, run ffprobe, SoX, project measurement, or runner, and created no receipt. Thus there are no observed R60 header bytes, metadata, decoded samples, errors, metrics, or command exits here.

## Conditional recommendation

First inspect the *original executor* R60 pair. Only recommend source integration if evidence establishes both actual headers and the local decoder/project path's behavior. Parse RIFF directly and record exact bytes/values: RIFF/WAVE; fmt size 40, tag `0xfffe`; mono, 48,000 Hz, byte rate 96,000, block align 2, 16-bit container; cbSize 22; channel mask `0x4`; PCM subtype GUID `0100000000001000800000aa00389b71`; valid bits respectively 0 and 16; 5,760-frame/11,520-byte equal payload. Confirm by byte/sample comparison that only the valid-bits field differs. Run ffprobe, SoX decode, and unchanged project UI measurement separately for each file. Record any rejection, exact error and exit, decoded vector length/equality/difference, and numeric gate result. Do not infer valid-bits from ffprobe's PCM16/container metadata.

If inspection and decoder results justify probing the malformed field, keep the integration to two unique opt-in flags, e.g. `--probe-ui-extensible-valid-0-r60` and `--probe-ui-extensible-valid-16-r60`, a pair-local deterministic builder under `corpus/live/round-60/`, and the existing UI measurement call on only the selected fixture. Use distinct receipt names. Keep one-probe exclusivity. No generic abstraction or decoder-policy layer is needed. A decoder rejection before runner invocation is an unsupported/decode observation, not a runner format failure or a receipt. If it rejects valid0 or the project measurer cannot make the intended observation, do not wire a passing probe or force a replay count; report the actual outcome.

Preserve `format_failures()`, UI spec/thresholds, prior modes, canonical17 and baseline battery/comparison families/sections. Do not turn a decode error into a receipt and do not alter predicate or thresholds. Only if both modes actually produce receipts is an 80-command serial replay (prior78 plus two) a conditional candidate; claim it only after the non-author replay completes and audit each receipt. A receipt-producing runner failure remains an observed runner result and must be distinguished from a receiptless setup/decode attempt.

## Commands, exits, errors, metadata and metrics

No shell/external command was run for this review; source/report reads were performed in Python. Therefore there are no executed command lines/exits, R60 setup attempts, decoder errors, runner receipts, headers, metadata, or metrics to report. All R60 properties above are **declared target conditions**, not observations. Suggested future checks are not executed evidence and have no observed exit status:

```sh
# Direct RIFF parser: inspect both files, including full fmt bytes, payload SHA,
# sample count and the exact differing offsets before invoking any runner mode.
python3 -c 'import struct; from pathlib import Path; p=Path(".shokunin/audio/corpus/live/round-60/executor");
for f in ("valid-0.wav","valid-16.wav"):
 b=(p/f).read_bytes(); i=b.index(b"fmt "); n=struct.unpack_from("<I",b,i+4)[0]; x=b[i+8:i+8+n]; j=b.index(b"data"); d=b[j+8:j+8+struct.unpack_from("<I",b,j+4)[0]]; print(f,"bytes",len(b),"riff",b[:4],"wave",b[8:12],"fmt",n,"tag",hex(struct.unpack_from("<H",x)[0]),"channels",struct.unpack_from("<H",x,2)[0],"rate",struct.unpack_from("<I",x,4)[0],"byte_rate",struct.unpack_from("<I",x,8)[0],"align/container",struct.unpack_from("<HH",x,12),"cbSize/valid",struct.unpack_from("<HH",x,16),"mask",hex(struct.unpack_from("<I",x,20)[0]),"guid",x[24:40].hex(),"data_bytes",len(d))'
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt:format=duration -of json .shokunin/audio/corpus/live/round-60/executor/valid-0.wav
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt:format=duration -of json .shokunin/audio/corpus/live/round-60/executor/valid-16.wav
sox .shokunin/audio/corpus/live/round-60/executor/valid-0.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-60/executor/valid-0.f32
sox .shokunin/audio/corpus/live/round-60/executor/valid-16.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-60/executor/valid-16.f32
```

The requested source-only integration recommendation is conditional; these suggested commands do not supply their results. If a command fails, report its exact invocation and exit/error as setup or decoder evidence, separately from each runner exit/receipt. Record all receipt metadata and measured metrics if runner is reached; do not synthesize missing evidence.

## Bounded limits and write boundary

Any eventual result is limited to this malformed valid-bits-zero header, its matched control/payload, and this local ffprobe/SoX/project path. Even a pass would indicate only that this path accepted/handled this fixture; it would not establish standards conformance, valid-bit enforcement, real zero-bit audio, precision/fidelity, general extensible-WAV or decoder behavior, audibility, quality, production suitability, rights, engine behavior, publishing, or promotion.

I wrote only `.shokunin/audio/reports/round-60/r60-reviewer.md`. I did not change shared source, LOG, SCORECARD, canonical artifacts, scratch fixtures, or another report; I did not commit or push.
