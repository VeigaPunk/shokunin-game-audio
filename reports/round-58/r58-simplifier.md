# R58 simplifier — keep the valid-bits probe narrow

## Recommendation

Use only the already-proposed paired fixture and two explicit opt-in runner modes for the declared `wValidBitsPerSample=14` versus `16` comparison. Keep the implementation local: one deterministic pair builder, two flags/dispatch branches, and the existing unchanged `measure("ui", SPECS["ui"], path)` path. Do not add a generic WAVE header abstraction, decoder policy, or valid-bit predicate. Keep `format_failures()`, UI thresholds, canonical artifacts, normal mode, and prior probes unchanged. The measurement is informative precisely because the existing predicate checks 16-bit container/codec output, not the extensible valid-bit field.

## Evidence read and command boundary

Read `/tmp/mission-audio-standing.md`, the R58 declaration in `.shokunin/audio/LOG.md`, R57 source and reports, and the current R58 executor generator source. I did not run a shell command, generate/alter fixtures, invoke ffprobe/SoX/the runner, or produce a receipt. Therefore I have **no R58 command exit codes, parsed header observation, decoder metadata, or measured metrics**; the generator's intended output is not observed output. No setup command failed in this lane. No source or shared project files were changed.

R58 executor scratch currently contains only `corpus/live/round-58/executor/generate.py`. Its source intends to create two 5,760-frame mono, 48-kHz WAVs using signed-16 samples quantized in multiples of four, with the same payload. It specifies extensible `fmt` size 40, tag `0xfffe`, `cbSize=22`, 16-bit container, mask `0x4`, and PCM subtype GUID bytes `0100000000001000800000aa00389b71`; the `valid-14.wav`/`valid-16.wav` header field is set to 14/16. These are **source-declared construction details only**, not independently inspected files or decoder results. The generator's stated build command is `python3 .shokunin/audio/corpus/live/round-58/executor/generate.py`; I did not execute it and report no exit status.

## R57 evidence relevant to keeping R58 honest

R57 reports establish a useful local precedent, not R58 evidence. The selected R57 pair was the alternate/integrated pair (not the executor's odd-valued draft): fmt40/tag `0xfffe`, `cbSize=22`, mono/48,000 Hz, mask `0x4`, PCM subtype, 16-bit container, valid bits 15/16; shared payload was 11,520 bytes and all samples even. WAV SHA-256 values were valid15 `4f41ace3a386c78217c991dae6972be49f3be4a9fa918211c58e3a019af47b2b` and valid16 `95d180f4c894751924317eb9b7add4d5c84e714a7807eeb14d1319a6ff1f785f`.

The R57 alternate report gives the exact observed metadata command (each file; ffprobe exit 0):

```sh
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt:format=duration -of json "$f"
```

For both, ffprobe reported `pcm_s16le`, `s16`, 48,000 Hz, mono, 16 bits/sample, `0.120000` s. Those fields did not expose the `wValidBitsPerSample` difference. The unchanged project measurement command exited 0 for each; both were 5,760 samples, duration `.12 s`, peak `0.2098388671875`, RMS `-18.84202236105824 dBFS`, centroid `2153.742616905067 Hz`, bandwidth `3627.640459173434 Hz`, and `failures: []`. SoX f32 conversion exited 0 for both; 5,760-sample vectors matched exactly (max absolute difference 0). This is only that valid15/16 pair and local path. R57's non-author integrated replay had 74 fresh receipts (36 exit 0, 38 expected validation exit 1), with both new modes clean and prior72 exact full-JSON matches; that is not an R58 replay.

R57 also demonstrates why setup and evidence must remain separate: an executor candidate with odd PCM16 samples was rejected as a valid left-aligned 15-bit encoding despite equal decoder outputs. R58's all-multiples-of-four payload is intended to address the alignment concern for valid14; it still needs actual header parse, ffprobe, SoX/vector comparison, unchanged project metrics, and integrated receipts before any outcome is claimed.

## Minimal evidence/report boundary

For R58, report actual command strings and exit status separately for generator, independent header parsing, each ffprobe/SoX conversion, project measurement, and integrated runner invocations. Record receipt paths and metrics only when produced. If a command fails before a runner receipt, call it a setup/decoder outcome, not a clean or failed fixture gate. If decoded vectors differ, report the observed difference; do not infer equality from shared payload. Do not infer valid-bit enforcement from ffprobe's 16-bit output or from passing the existing PCM16 predicate.

The result can support only a bounded observation about these constructed mono PCM-subtype extensible WAVs and this host's ffprobe/SoX/project path. It does not establish general extensible support, valid-bit enforcement, 14-bit precision/fidelity, other layouts/decoders, audibility, production suitability, rights, engine behavior, publishing, or promotion. This lane made no commit or push.
