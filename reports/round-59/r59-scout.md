# R59 scout — valid-bit history and local 13/16 observation

## Historical map

- R22’s WAVE_FORMAT_EXTENSIBLE PCM24 pair included 24-valid-bit and 20-valid-bit headers in a 24-bit container. Its recorded ffprobe output reported `pcm_s24le`, `sample_fmt=s32`, `bits_per_sample=24`, `bits_per_raw_sample=24`, 48 kHz mono for both; it did not expose the differing valid-bits field. `s32` described FFmpeg’s decoded representation, not a PCM32 container. R22-era format checks were rate/channel only; the later/current PCM16 predicate checks `codec_name == pcm_s16le` and `bits_per_sample == 16`, not `wValidBitsPerSample`.
- Current `measure_audio.py` `format_failures()` checks 48 kHz mono, `pcm_s16le`, and 16 bits/sample. ffprobe `sample_fmt` and SoX’s `16-bit Signed Integer PCM` are representation/container reports here, not reports of valid-bit precision. R22 evidence therefore separates container/decoder metadata from valid bits but does not establish valid-bit enforcement.
- R57 selected the **alt** pair: matching 5,760-frame mono48k PCM16-container extensible files with valid-bits 15/16, same all-even payload (left-aligned-compatible); ffprobe reported PCM16/16 and SoX decoded identical vectors. The separate executor candidate had 2,520 odd values and was rejected, not evidence about the selected pair. R58 selected matched 14/16 files with all 5,760 payload values divisible by four; ffprobe/SoX also reported PCM16/16 and equal decoded vectors. Neither round proves general valid-bit semantics or metadata enforcement.

## R59 scout pair and header

Constructed two original synthetic 120 ms UI-shaped mono48k files in `corpus/live/round-59/scout/`. The 5,760 signed-16 samples are generated from `0.25*sin(2π·1000·i/48000) + 0.08*sin(2π·1500·i/48000)`, rounded to signed16 and then quantized to multiples of eight. All values are divisible by eight, so the shared payload is compatible with the declared 13-bit left-aligned case. Both payloads are identical, 11,520 bytes; payload SHA-256 `1e12f8c409d505c2e8b066b37f54ed776c693f3813d6d5883216fb7598746336`.

Direct RIFF/WAVE layout for both: total 11,588 bytes; RIFF declared size 11,580; `fmt ` size 40; format tag `0xfffe`; `cbSize=22`; 1 channel; 48,000 Hz; byte rate 96,000; block align 2; 16-bit container; channel mask `0x4`; PCM subtype GUID bytes `0100000000001000800000aa00389b71`; data size 11,520. Only `wValidBitsPerSample` changes: 13 versus 16. Whole-WAV SHA-256: valid13 `601982df82fe5e25e1729238761bd69c336fabea20f2eb694e74944622e0037a`; valid16 `4781281428d997462160361318c527f135d865149907fa4ac2aa787526d33d65`.

WAV construction used Python in the REPL (not a shell command): generated the stated sample expression, rounded each signed16 value to a multiple of 8, packed little-endian `<h`, and wrote a RIFF WAVE containing `fmt` packed as `struct.pack('<HHIIHH',0xfffe,1,48000,96000,2,16) + struct.pack('<HHI',22,valid_bits,4) + bytes.fromhex('0100000000001000800000aa00389b71')`, followed by the identical `data` chunk. No source/runner mode was invoked or edited.

## Commands, exits, observations

Exact ffprobe and SoX header-info command (loop exit **0**; each ffprobe and `sox --i` exited **0**):

```sh
for f in .shokunin/audio/corpus/live/round-59/scout/valid{13,16}.wav; do echo FILE=$f; ffprobe -v error -show_entries stream=codec_name,sample_fmt,bits_per_sample,bits_per_raw_sample,sample_rate,channels:format=duration -of json "$f"; echo FFPROBE_EXIT=$?; sox --i "$f"; echo SOX_INFO_EXIT=$?; done
```

Both ffprobe results: `codec_name=pcm_s16le`, `sample_fmt=s16`, `sample_rate=48000`, `channels=1`, `bits_per_sample=16`, duration `0.120000`; `bits_per_raw_sample` omitted. Both SoX reports: mono, 48 kHz, 16-bit precision / `16-bit Signed Integer PCM`, 5,760 samples, 0.12 seconds. These commands do not expose the 13/16 valid-bit difference.

Exact SoX f32 decode commands (each exited **0**):

```sh
sox .shokunin/audio/corpus/live/round-59/scout/valid13.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-59/scout/valid13.f32
sox .shokunin/audio/corpus/live/round-59/scout/valid16.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-59/scout/valid16.f32
```

Each decoded file had 5,760 f32 samples; SHA-256 for each was `c30b512086ec8764bfac096a1dfba2549e153dc6a830f6eb8aa219fa60cd8a49`. Python vector comparison: exact equal, max absolute difference 0, differing sample count 0.

Exact unchanged direct project measurement command (exit **0**):

```sh
python3 -c 'import importlib.util; from pathlib import Path; s=importlib.util.spec_from_file_location("m", ".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); p=Path(".shokunin/audio/corpus/live/round-59/scout").resolve(); [print(m.measure("ui",m.SPECS["ui"],p/f)) for f in ("valid13.wav","valid16.wav")]'
```

Both direct `measure()` results were clean (`failures: []`): 0.12 s; 48,000 Hz mono; `pcm_s16le`/16 bits; peak `0.3154296875`; RMS `-14.628290486326076 dBFS`; LUFS `null`; centroid `1139.787098582088 Hz`; bandwidth `581.6182895405447 Hz`. These are direct measurement calls, not integrated runner receipts or an independent replay.

## Setup and limits

No failed shell setup, decode, or numeric fit occurred in this scout. Construction/header parsing used Python REPL operations; external commands and exits are listed above. No opt-in runner probes or replay receipts were run.

This establishes only that these constructed matched files produce equal SoX/project decoded measurements and the listed metadata on this host. It does not show ffprobe/SoX/project measurement enforce the valid-bits field, general decoder or extensible-WAV behavior, meaningful precision/fidelity, standards conformance, audible quality, production suitability, rights, engine behavior, publishing, or promotion. No shared source, LOG, SCORECARD, canonical artifact, or other report was changed; no commit or push was made. Scratch artifacts are confined to `corpus/live/round-59/scout/`; this is the only report written.
