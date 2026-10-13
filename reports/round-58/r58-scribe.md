# R58 scribe — conditional replay and decode ledger

## Scope/status

Read `/tmp/mission-audio-standing.md`, the R58 declaration in `.shokunin/audio/LOG.md`, and R57 source/reports (including `r57-scribe.md` and `r57-verifier.md`). The declared move is a matched 5,760-frame, mono/48 kHz, WAVE_FORMAT_EXTENSIBLE PCM-subtype pair: fmt size 40, `cbSize=22`, channel mask `0x4`, 16-bit container and same payload (all signed values divisible by four), differing only in `wValidBitsPerSample` 14 vs 16.

At inspection time, the working tree has **no integrated R58 runner options or source routing**: `measure_audio.py` contains no `valid-14` / `valid-16` probe. Thus I made no speculative runner invocation, and there is no integrated R58 receipt or fresh replay. The planned 76-command replay (74 prior R57 commands plus two new probes) is conditional on integration and on both probes producing receipts. This note does not claim replay or integration. Direct inspections/measurements below are not runner receipts.

## Independent scratch-pair inspection

I inspected executor, alt, and critic pairs in their respective `corpus/live/round-58/<role>/` scratch directories. Each pair has 11,588-byte RIFF/WAVE files; mono 48,000 Hz; byte rate 96,000; block align 2; fmt size 40; tag `0xfffe`; `cbSize=22`; container bits 16; mask `0x4`; PCM GUID bytes `0100000000001000800000aa00389b71`; 11,520-byte data payload (5,760 samples); and all payload samples divisible by four. Within each pair the payloads are byte-identical and the sole header change is valid bits 14 vs 16. The three independent scratch pairs have different audio payloads from one another; they are not one cross-pair sample comparison.

| Pair/file | WAV SHA-256 | Payload SHA-256 | valid bits |
|---|---|---|---:|
| executor `valid-14.wav` | `6b4b07d1eee022f99116a043b444821914acc68110544a644ba7204f3a63fb26` | `0b40e3c0f28aa6a50937f87c0fa260b2100f97572dbc8fdf517cea981e79b4fc` | 14 |
| executor `valid-16.wav` | `738263969d226d31a0525bbad1c7dda8609b270dd3ec8fa82645905d4667a7f2` | same as pair | 16 |
| alt `valid14.wav` | `c56dd1946015796b3d96e2b699899682a773a6e3daa4084b5b16cde81ebd1a89` | `501477dbee28e2f9380a8d5027b379020d7e87801946657079399a06310443f5` | 14 |
| alt `valid16.wav` | `2bc6d22183197478bf56d36ed7bf7fd715d1e6932a5a59d253f79083432cbee1` | same as pair | 16 |
| critic `valid14.wav` | `f02d3e960d0b641558c34a97803aa0566de6db666de65fb2bf50c8c9a9961eb6` | `0e4e786426ecc152d5b1189c05252fc1a8cf287c749a97cad2ac9e887031782e` | 14 |
| critic `valid16.wav` | `fbc8ebdc1a2d3d5c430ff139f4bbe4ff36bca402d901729d15ac00c44bac2b60` | same as pair | 16 |

The following exact ffprobe commands each exited **0** and reported `pcm_s16le`, `s16`, 16 bits/sample, mono, 48,000 Hz, duration `0.120000` s:

```sh
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt,duration -of json .shokunin/audio/corpus/live/round-58/executor/valid-14.wav
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt,duration -of json .shokunin/audio/corpus/live/round-58/executor/valid-16.wav
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt,duration -of json .shokunin/audio/corpus/live/round-58/alt/valid14.wav
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt,duration -of json .shokunin/audio/corpus/live/round-58/alt/valid16.wav
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt,duration -of json .shokunin/audio/corpus/live/round-58/critic/valid14.wav
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt,duration -of json .shokunin/audio/corpus/live/round-58/critic/valid16.wav
```

The following exact SoX decode commands each exited **0**:

```sh
sox .shokunin/audio/corpus/live/round-58/executor/valid-14.wav -t f32 -e floating-point /tmp/executor-valid-14.wav.f32
sox .shokunin/audio/corpus/live/round-58/executor/valid-16.wav -t f32 -e floating-point /tmp/executor-valid-16.wav.f32
sox .shokunin/audio/corpus/live/round-58/alt/valid14.wav -t f32 -e floating-point /tmp/alt-valid14.wav.f32
sox .shokunin/audio/corpus/live/round-58/alt/valid16.wav -t f32 -e floating-point /tmp/alt-valid16.wav.f32
sox .shokunin/audio/corpus/live/round-58/critic/valid14.wav -t f32 -e floating-point /tmp/critic-valid14.wav.f32
sox .shokunin/audio/corpus/live/round-58/critic/valid16.wav -t f32 -e floating-point /tmp/critic-valid16.wav.f32
```

Each decoded vector has 5,760 float32 samples. Within each of the three pairs, 14- and 16-bit vectors are exactly equal; respective vector SHA-256 values were executor `ca42332f650f6e2361ebd56649629322a85bb3d72d03e2b2861a112c36915aa8`, alt `8a8d20cfa2ab30a4dbe3415e78363c63cd1ba90374318e23e6232f0eb79fa470`, critic `b18887926c056995a876639981e13704bf052fbf498e58b2ffe79d33d0892485`. This is only the observed SoX path on these files.

## Direct project measurement (not runner)

The exact measurement invocation below exited **0**. It calls the existing UI measure function on six absolute paths; all have `failures: []`, LUFS `null`, and the measured format/duration fields agree with ffprobe.

```sh
python3 -c 'import importlib.util; from pathlib import Path; s=importlib.util.spec_from_file_location("m", ".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); [print(str(p),m.measure("ui",m.SPECS["ui"],p)) for p in [Path(".shokunin/audio/corpus/live/round-58/executor/valid-14.wav").resolve(),Path(".shokunin/audio/corpus/live/round-58/executor/valid-16.wav").resolve(),Path(".shokunin/audio/corpus/live/round-58/alt/valid14.wav").resolve(),Path(".shokunin/audio/corpus/live/round-58/alt/valid16.wav").resolve(),Path(".shokunin/audio/corpus/live/round-58/critic/valid14.wav").resolve(),Path(".shokunin/audio/corpus/live/round-58/critic/valid16.wav").resolve()]]'
```

| Pair | Peak FS | RMS dBFS | Centroid Hz | Bandwidth Hz |
|---|---:|---:|---:|---:|
| executor, both valid bits | 0.3153076171875 | -14.629479252569332 | 1129.9910331085607 | 412.58546294347246 |
| alt, both valid bits | 0.3199462890625 | -15.349264723890549 | 2090.91125087851 | 3562.6781107930465 |
| critic, both valid bits | 0.419677734375 | -12.821422447778616 | 2153.742616905067 | 3627.640459173434 |

All are local direct numeric fits, not opt-in runner-mode results. No numeric-fit failure or decode rejection was observed in these direct checks.

## Setup errors and replay boundary

An initial direct-measure command used relative `Path` arguments; it exited **1** with `ValueError` (`path.relative_to(ROOT)`), produced no runner receipt, and was a scribe setup/path error. Retrying with absolute paths exited 0 as shown above. This is neither a decode failure nor a numeric-gate failure. I did not try a runner command because its R58 flags/routing are absent. Therefore there is no attempted runner setup/decode failure to misclassify, no receiptless runner outcome, and no R58 serial command ledger. Once integration exists, record actual commands/exits/receipts and failures; count only actual receipts, and compare the exact prior-74 complete JSON objects per R57 verifier rather than asserting 76 in advance. A pre-receipt invocation/setup error is not a decode or numeric failure; a receipt with failed measurement is a gate result.

No transcription was attempted. No source, LOG, SCORECARD, canonical artifact, or other report was changed. No commit or push was made. Limits: these scratch observations do not establish integrated runner behavior, broad valid-bit enforcement, standards conformance, other headers/decoders, 14-bit fidelity, audibility/quality, production, rights, engine behavior, publishing, or promotion.
