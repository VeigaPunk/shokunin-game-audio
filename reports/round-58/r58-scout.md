# R58 scout — valid-bits history and local 14/16 decoder observation

## Historical map

- R22’s extensible PCM24 alternate produced a 24-bit container with `wValidBitsPerSample=20` (payload quantized to 20 significant high bits). The recorded ffprobe query reported `codec_name=pcm_s24le`, `sample_fmt=s32`, `bits_per_sample=24`, `bits_per_raw_sample=24`, 48 kHz mono for this and the 24-valid-bit counterpart. It did not expose the differing valid-bits field. SoX decoded both. This is container/decoder metadata, not proof of 20-bit valid precision. The R22 runner-era format check was rate/channel only; its later PCM16 check tests `codec_name == pcm_s16le` and `bits_per_sample == 16`, not `wValidBitsPerSample`.
- Current `measure_audio.py` likewise checks 48 kHz mono, `codec_name=pcm_s16le`, and `bits_per_sample=16`. It does not inspect valid bits. ffprobe’s `sample_fmt` (`s16` here) and SoX’s `16-bit Signed Integer PCM` description concern decoded/container representation. These fields do not by themselves say whether a 14- or 15-bit extensible signal is honored.
- R57 selected the **alt** pair, not executor pair. The selected 5,760-frame mono 48 kHz PCM16-container extensible pair had identical all-even (left-aligned) signed16 payloads, SHA-256 `a6ec402df430818fd02a8437a85af7ab335e51084ca7e224f2b1b15cc2d2b89a`; tag `0xfffe`, `fmt` size 40, `cbSize=22`, mask `0x4`, PCM subtype GUID, with only `wValidBitsPerSample` differing (15 vs 16). Integrated WAV SHA-256: valid15 `4f41ace3a386c78217c991dae6972be49f3be4a9fa918211c58e3a019af47b2b`; valid16 `95d180f4c894751924317eb9b7add4d5c84e714a7807eeb14d1319a6ff1f785f`. Both returned ffprobe `pcm_s16le`/16 bits, and SoX-f32 decoded vectors were identical for this payload. Integrated project measurements were clean for both: `.120000s`, peak `.2098388671875`, RMS `-18.84202236105824 dBFS`, centroid `2153.742616905067 Hz`; fresh integrated results exited 0. The 2,520/5,760 odd samples belong to the **rejected executor candidate**, not selected alt; it is not evidence against selected payload alignment. The selected pair only establishes behavior of those inputs on those readers, not general valid-bit handling.

## Original local valid14/valid16 pair (scout scratch)

I made a fresh matched pair under `.shokunin/audio/corpus/live/round-58/scout/` to check the declared 14-bit possibility without editing source. Both have 5,760 frames of identical signed-16 payload, all sample values divisible by four (left-aligned 14-bit-compatible values); one header declares 14 valid bits, the other 16. Header fields are RIFF/WAVE, `fmt ` size 40, format tag `0xfffe`, `cbSize=22`, mono, 48,000 Hz, byte rate 96,000, block align 2, 16-bit container, mask `0x4`, PCM subtype GUID bytes `0100000000001000800000aa00389b71`. Only `wValidBitsPerSample` differs (14 vs 16). Both files are 11,588 bytes; RIFF declared size 11,580. Identical payload SHA-256: `5575fed1d9b1229767ac18cf3d6b5d13c5a01eeca129cbc7bf27fc128002b1ac`. WAV SHA-256: valid14 `8ab31ecca30626d5ec620d4f95006e235bf52b47adca3d5c83048a11f28e5652`; valid16 `8aa2d5ae915992c6c328e4a579256541084eeb10df3834ae2958dbc1eabe852f`.

Exact external commands and exits:

```sh
for f in .shokunin/audio/corpus/live/round-58/scout/valid{14,16}.wav; do echo "FILE=$f"; ffprobe -v error -show_entries stream=codec_name,sample_fmt,bits_per_sample,bits_per_raw_sample,sample_rate,channels:format=duration -of json "$f"; echo FFPROBE_EXIT=$?; sox --i "$f"; echo SOX_INFO_EXIT=$?; done
```

Overall shell exit **0**; each ffprobe and SoX-info invocation exited **0**. Both ffprobe outputs: `codec_name=pcm_s16le`, `sample_fmt=s16`, `sample_rate=48000`, `channels=1`, `bits_per_sample=16`, duration `0.120000`; `bits_per_raw_sample` omitted. SoX reported one channel, 48 kHz, precision 16-bit, 5,760 samples, 16-bit Signed Integer PCM. Neither report surfaced the 14/16 valid-bit distinction.

```sh
sox .shokunin/audio/corpus/live/round-58/scout/valid14.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-58/scout/valid14.f32
sox .shokunin/audio/corpus/live/round-58/scout/valid16.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-58/scout/valid16.f32
```

Both commands exited **0**. Comparing the f32 outputs in Python: 5,760 samples each; `array_equal=True`, maximum absolute difference `0`, differing samples `0`; each vector SHA-256 `93b02edd2bea29836f1ef59cb1dc9ac005e958ffe32948a3294b5004a2ef9ed0`.

The exact unchanged direct project measurement invocation exited **0**:

```sh
python3 -c 'import importlib.util; from pathlib import Path; s=importlib.util.spec_from_file_location("m", ".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); p=Path(".shokunin/audio/corpus/live/round-58/scout").resolve(); [print(m.measure("ui",m.SPECS["ui"],p/f)) for f in ("valid14.wav","valid16.wav")]'
```

Both returned `failures: []`, 0.12 s, 48 kHz mono, `pcm_s16le`/16 bits, peak `0.3154296875`, RMS `-14.629058704483988 dBFS`, centroid `1129.5544042946667 Hz`, bandwidth `418.1831779600012 Hz`, LUFS `null`. This is a direct `measure()` result, not an integrated runner receipt. For this particular pair, SoX and the project measurement path yielded equal output for valid14 and valid16; the observation is consistent with those tools ignoring this metadata distinction, but does not establish universal decoder behavior.

## Setup, scope, limits

No failed setup command or failed fit occurred in this scout work. WAV construction was performed with Python in the REPL, not an external shell command; the exact shell commands above cover ffprobe, SoX decoding, and project measurement. Scratch files (including f32 decode outputs) are only in `corpus/live/round-58/scout/`. I did not run the opt-in runner modes or create replay receipts.

Evidence is limited to R22’s recorded 24-container/20-valid metadata observations, R57’s reported 15/16 history (including its sample-alignment caveat), and this one 14/16 PCM16-container payload on this host’s ffprobe, SoX, and direct project-measurer paths. It is not a standards-conformance verdict, general valid-bit support test, proof of meaningful precision/fidelity, or audible/production/rights/engine/publishing claim. No shared source, LOG, SCORECARD, canonical artifact, or other report was changed; no commit or push was made.
