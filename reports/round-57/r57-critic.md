# R57 critic — valid-bits-15 falsification

## Scope and outcome

I read `/tmp/mission-audio-standing.md`, the R57 declaration in `.shokunin/audio/LOG.md`, and R56 source/reports. I wrote only this report and scratch SoX outputs under `.shokunin/audio/corpus/live/round-57/critic/`. This check challenges whether `wValidBitsPerSample=15` changes decoding, whether the headers truly vary only in that field, and whether the alleged 15-valid-bit samples meet the left-aligned valid-bit representation. This is not an integrated runner replay.

**Observed narrow outcome:** the two executor WAVs have real, valid-looking RIFX/RF64-independent RIFF/WAVE extensible headers with correct PCM subtype GUID and valid=15 vs16 fields. On this host, ffprobe labels *both* `pcm_s16le`/`s16`/16-bit and SoX decodes both successfully to identical float32 vectors; the unchanged project UI measurement returns no failures for either. Thus the tested decoder/gate path does not reject or alter this particular valid15 declaration. However, executor's two files are byte-identical in audio payload and contain many odd-valued 16-bit samples, inconsistent with 15 significant bits left-aligned in 16-bit containers. Equal decode is therefore not evidence of correct 15-bit sample encoding or generalized valid-bit support. The independent alt pair uses properly even (left-aligned) payload values and likewise decodes equal, but has different payloads across the pair only? Its generated pair has same payload and only valid-bits header differs; measured equal as expected.

## Commands, metadata, and header validation

Initial shell invocations constructed as `bash("\"\"\"<command>\"\"\"")` mistakenly quoted the entire command. All eight attempts (ffprobe and SoX for both files in each of executor and alt) exited **127**, `/usr/bin/bash: ... No such file or directory`; they produced no output artifact/measurement receipt. These were command-setup failures, not decode or gate failures. I reran the commands normally; successful commands and exits follow.

Generation source was inspected, not rerun. Executor generator writes same 5,760-frame signed16 payload for `valid-15.wav`/`valid-16.wav`; alt generator writes a separately synthesized payload shared by its `valid15.wav`/`valid16.wav` pair. Direct RIFF parsing yielded:

| File | WAV SHA-256 | Bytes | fmt/tag | cbSize | valid/container bits | channels/rate | mask | PCM subtype GUID bytes | data bytes |
|---|---|---:|---|---:|---|---|---|---|---:|
| executor `valid-15.wav` | `d3835a35014b3536c1710aafed8a104ef32eaa84acb37c87213127785f18175c` | 11588 | 40 / `0xfffe` | 22 | 15 / 16 | 1 / 48000 | `0x4` | `0100000000001000800000aa00389b71` | 11520 |
| executor `valid-16.wav` | `bd7d95901935c0effe21fd64e44a47487372be9d0c80f86cc725380df0352f47` | 11588 | 40 / `0xfffe` | 22 | 16 / 16 | 1 / 48000 | `0x4` | `0100000000001000800000aa00389b71` | 11520 |
| alt `valid15.wav` | `4f41ace3a386c78217c991dae6972be49f3be4a9fa918211c58e3a019af47b2b` | 11588 | 40 / `0xfffe` | 22 | 15 / 16 | 1 / 48000 | `0x4` | `0100000000001000800000aa00389b71` | 11520 |
| alt `valid16.wav` | `95d180f4c894751924317eb9b7add4d5c84e714a7807eeb14d1319a6ff1f785f` | 11588 | 40 / `0xfffe` | 22 | 16 / 16 | 1 / 48000 | `0x4` | `0100000000001000800000aa00389b71` | 11520 |

The GUID bytes are the WAVE little-endian form of `{00000001-0000-0010-8000-00aa00389b71}` (PCM subtype). Header fields other than valid bits matched within each pair. ffprobe command, run separately for each of the four paths, exited **0**:

```sh
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt:format=duration -of json "<file>"
```

Each returned `codec_name=pcm_s16le`, `sample_fmt=s16`, `sample_rate=48000`, `channels=1`, `bits_per_sample=16`, and `duration=0.120000`. Notably this metadata does not expose/confirm `wValidBitsPerSample`; `bits_per_sample` and `sample_fmt` describe the 16-bit container/decoder output, not the header's valid-bit field.

For each file, SoX command exited **0** (no stdout/stderr):

```sh
sox "<file>" -t f32 -e floating-point ".shokunin/audio/corpus/live/round-57/critic/<role>-<file>.f32"
```

Each produced 5,760 float32 values. Executor decoded-file SHA-256 was `d80f13858e4fdcf641f2164b440a99a42711fd4213239ad809c8136ee4620ce7` for each valid15 and valid16 file; elementwise equality true, max difference 0. Alt decoded-file SHA-256 was `8418a33a87b8f511b89af0021d579e24eb60e50d143e408df0ef8305e69160a9` for both; elementwise equality true, max difference 0. Executor decoded min/max `-0.31536865 / 0.31536865`, RMS `0.1855983203`; alt min/max `-0.20983887 / 0.20977783`, RMS `0.1142612266`.

## Existing project measurement

I invoked the unchanged `measure_audio.measure("ui", SPECS["ui"], Path(...))` once per file using this exact command template (absolute input path substituted); all four invocations exited **0**:

```sh
python3 -c 'import importlib.util; from pathlib import Path; s=importlib.util.spec_from_file_location("m", ".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(m.measure("ui",m.SPECS["ui"],Path("<absolute-file-path>")))'
```

Executor valid15 and valid16 each: duration `.12 s`, 48000 Hz mono `pcm_s16le`/16-bit, peak `0.31536865234375`, RMS `-14.628519169868087 dBFS`, integrated LUFS `None`, centroid `1123.322704293326 Hz`, bandwidth `276.15444981222976 Hz`, failures `[]`. Alt valid15 and valid16 each: duration `.12 s`, same rate/channel/codec/bits, peak `0.2098388671875`, RMS `-18.84202236105824 dBFS`, integrated LUFS `None`, centroid `2153.742616905067 Hz`, bandwidth `3627.640459173434 Hz`, failures `[]`. These are direct measurement function calls, not receipts from the integrated R57 opt-in runner modes.

## Semantic confound and conclusion

An extensible `wValidBitsPerSample` smaller than `wBitsPerSample` says the valid precision occupies the most-significant bits of each container; lower unused bits are padding. A properly 15-bit signed signal left-aligned in a 16-bit container has zero low-order padding bit. Executor's ostensibly shared payload ranges `-10334..10334` and has **2,520 / 5,760 odd samples** (nonzero low bit), so it is not a clean 15-valid-bit encoded source. The 15 and 16 headers are byte-different only in the field, but executor's sample payload does not honor the 15-bit precision declaration. Its equal SoX decode therefore demonstrates only that local SoX/ffprobe/project path ignored or did not apply that valid-bit field to this payload. Alt payload values range `-6876..6874`, with **0 / 5,760 odd samples**, consistent with one zero padding LSB; it too yields identical output for valid15 and valid16 because identical payload is decoded. The direct metric equality is not an independent fidelity/quality result.

This falsifies any broad inference that a nominal 15-valid-bit tag alone establishes preservation of correctly encoded 15-bit signal. It does *not* falsify the narrow observed behavior that these specific headers are accepted and decode equal. Correctly aligned 15-bit content and a comparison against a valid16 signal quantized to the same 15-bit precision are needed to test whether decoder interpretation preserves the intended amplitude/precision. No SoX/ffprobe failure, project gate failure, or receiptless decode/setup failure occurred after correcting the eight shell setup invocations; those initial exits127 were setup only. No integrated runner receipt was attempted.

Bounded to two independently generated matched pairs, this machine's ffprobe/SoX and current UI measurement. No universal WAV conformance, other valid/container bit-widths, other decoders, fidelity/audibility/quality, production, rights, engine, publishing, or promotion claim. No shared source, LOG, SCORECARD, canonical artifact, or other report changed; no commit/push.
