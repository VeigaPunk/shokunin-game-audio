# R57 scribe — conditional replay / decode ledger

## Status and scope

Read `/tmp/mission-audio-standing.md`, R57 declaration in `.shokunin/audio/LOG.md`, R56 source/reports, and the R57 executor scratch. The declared test is a matched mono 48 kHz, 5,760-frame extensible PCM-subtype WAV pair; `wValidBitsPerSample` is 15 vs 16 while the 16-bit container, payload, mask `0x4`, and other header fields are held constant.

**No integrated R57 runner modes or source wiring are present in the inspected tree.** The current runner has the R56 mask flags but no valid-bits flags and does not route `valid-15.wav`/`valid-16.wav`. Accordingly, no guessed runner invocation was made, no R57 runner receipt exists, and the 74-command replay is conditional on integration. Do not count the direct measurements below as runner receipts or serial-replay evidence. Once actual option names and mode-to-file routing are integrated, execute those two exact modes followed by the unchanged prior-72 verifier sequence from `reports/round-56/r56-verifier.md`; expected count is 74 only if both modes produce receipts. Verify 72 prior rows by complete JSON equality to the R56 ledger. A runner command rejected before producing a measurement receipt is **receiptless setup/integration**, not a validation or numeric failure; report its attempted command and exit separately. A produced receipt whose `failures` or process exit is nonzero is a **runner/gate result**, not setup.

## Observed executor pair (not replay)

Scratch files already existed; I did not generate or alter them. Direct header inspection found both files are 11,588 bytes, RIFF/WAVE with `fmt ` size 40, tag `0xfffe`, mono, 48,000 Hz, container bits 16, `cbSize=22`, channel mask `0x4`, PCM subtype GUID bytes `0100000000001000800000aa00389b71`; only valid bits differ (15 vs 16). Both have 11,520-byte data payload, SHA-256 `67ea695da5665554f467cae513d0c2d3d62d588516299f7eb4872bf79d58df4e`.

| file | WAV SHA-256 | valid bits | ffprobe result |
|---|---|---:|---|
| `corpus/live/round-57/executor/valid-15.wav` | `d3835a35014b3536c1710aafed8a104ef32eaa84acb37c87213127785f18175c` | 15 | `pcm_s16le`, `s16`, 16 bits/sample, mono, 48,000 Hz, `0.120000` s |
| `corpus/live/round-57/executor/valid-16.wav` | `bd7d95901935c0effe21fd64e44a47487372be9d0c80f86cc725380df0352f47` | 16 | `pcm_s16le`, `s16`, 16 bits/sample, mono, 48,000 Hz, `0.120000` s |

Exact metadata commands, each exit **0**:

```sh
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt:format=duration -of json .shokunin/audio/corpus/live/round-57/executor/valid-15.wav
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt:format=duration -of json .shokunin/audio/corpus/live/round-57/executor/valid-16.wav
```

SoX decode commands, each exit **0**:

```sh
sox .shokunin/audio/corpus/live/round-57/executor/valid-15.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-57/executor/valid-15.wav.f32
sox .shokunin/audio/corpus/live/round-57/executor/valid-16.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-57/executor/valid-16.wav.f32
```

Readback of both output vectors: 5,760 float32 samples each; exact equality (`array_equal=True`), max absolute difference `0.0`, non-equal count 0. This is an observed local decode result, not a universal decoder conclusion.

Exact project measurement command (exit **0**):

```sh
python3 -c 'import importlib.util; from pathlib import Path; s=importlib.util.spec_from_file_location("m", ".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); p=Path(".shokunin/audio/corpus/live/round-57/executor").resolve(); [print(f,m.measure("ui",m.SPECS["ui"],p/f)) for f in ("valid-15.wav","valid-16.wav")]'
```

Both direct project measurements report duration `0.12 s`, 48,000 Hz, mono, `pcm_s16le`/16 container bits, peak `0.31536865234375`, RMS `-14.628519169868087 dBFS`, centroid `1123.322704293326 Hz`, bandwidth `276.15444981222976 Hz`, LUFS `null`, and `failures: []`. Both therefore pass the unchanged direct UI measurement gates in this local invocation. This does not prove the integrated runner mode passes.

## Setup attempts, numeric outcomes, transcription

One exploratory RIFF-inspection shell command was malformed (`fmt \ ` instead of `fmt `), exited **1** with `ValueError: subsection not found`; it generated no runner receipt and is a **scribe setup/inspection error**, not a target decode or numeric failure. Re-running the header inspection in Python succeeded. There was no attempted R57 runner command and hence no receiptless runner failure to report. The observed ffprobe, SoX, and direct measure commands succeeded; no numeric gate failure was observed in those direct checks. No speech or transcription was used: transcription is **not tested**, not a pass/fail result, and no transcript correction occurred.

## Replay boundary and limits

R56 ended with 72 fresh serial runner commands (34 exit 0 / 38 expected validation exit 1); use its successful exact command list and receipt mapping as the prior sequence, not old receipts as new R57 evidence. After integration, the R57 pair commands must come first and use the actual implemented flags; then rerun those 72 prior commands serially. Record every actual command, exit, fresh receipt path, and failures, even if count differs from 74. Distinguish missing receipts from validation outcomes, inspect both valid-bit fields and ffprobe/SoX decoding, and do not assume equal decoded values merely because payload bytes match. No claim here about other valid/container widths, masks, headers, decoders, standards conformance, fidelity, audibility/quality, production, rights, engine behavior, publishing, or promotion. No source, LOG, SCORECARD, canonical artifact, or other report was changed; no commit or push was made.
