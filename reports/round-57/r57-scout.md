# R57 scout — historical valid-bit versus container-bit evidence

## Scope and historical map

Read the standing brief, R57 declaration in `.shokunin/audio/LOG.md`, R22 reports, and R55–R56 reports/source. Historical evidence is narrow:

- R22 `r22-alt.md` documents ordinary native PCM24 and WAVE_FORMAT_EXTENSIBLE PCM24 with both 24 valid bits and 20 valid bits in a 24-bit container. For both extensible files, queried ffprobe fields reported `pcm_s24le`, `s32`, `bits_per_sample=24` (and `bits_per_raw_sample=24` where requested), 48 kHz mono. The 20-valid-bit setting was not exposed by those ffprobe queries. So `bits_per_sample`/`bits_per_raw_sample` represented container/codec width in that evidence, not valid-bit precision; `sample_fmt=s32` described FFmpeg’s decoded representation, not PCM32 or valid bits.
- R22–R23 source/evidence explicitly bounded the then-added PCM16 predicate to `codec_name == "pcm_s16le"` and `bits_per_sample == 16`; it did not inspect `wValidBitsPerSample`. R55–R56 positive extensible probes both used 16 valid bits in a 16-bit container and therefore also do not separate the fields.
- Current `measure_audio.py` `format_failures()` checks 48 kHz/mono plus `codec_name == "pcm_s16le"` and `bits_per_sample == 16`. These are ffprobe codec/container-width checks, not a valid-bits check. SoX `--i` similarly describes decoded input as 16-bit signed PCM here; its f32 decode normalizes samples and does not report the extensible `wValidBitsPerSample` field. Neither tool output alone establishes valid-bit semantics.

## Original scratch observation

I created `.shokunin/audio/corpus/live/round-57/scout/scout-valid15.wav` and `scout-valid16.wav` from the R55 UI-shaped 5,760-frame mono 48 kHz signed-16 payload. Both are 11,588-byte RIFF/WAVE with tag `0xfffe`, 40-byte `fmt `, `cbSize=22`, one channel, 48,000 Hz, byte rate 96,000, block align 2, container bits 16, mask `0x4`, PCM subtype GUID bytes `0100000000001000800000aa00389b71`; the `wValidBitsPerSample` field is respectively 15 and 16. Both data chunks contain the same 11,520 payload bytes (SHA-256 `67ea695da5665554f467cae513d0c2d3d62d588516299f7eb4872bf79d58df4e`). WAV SHA-256: valid15 `d3835a35014b3536c1710aafed8a104ef32eaa84acb37c87213127785f18175c`; valid16 `bd7d95901935c0effe21fd64e44a47487372be9d0c80f86cc725380df0352f47`.

The exact scratch generation was performed in the Python REPL (not a shell command): pack samples `round(32767*(.25*sin(2*pi*1000*i/48000)+.08*sin(2*pi*1500*i/48000)))` as little-endian signed16, then write the same payload under the two extensible headers described above. Direct byte construction confirmed the header field and identical payload. Note a semantic caveat: the shared signal contains 2,520 odd-valued samples; a 15-valid-bit PCM signal in a 16-bit container is conventionally left-aligned, so this same-payload pair is not proof that the 15-bit stream is a conforming left-aligned 15-bit sample representation. It is a useful probe of how these local readers treat the metadata field, not a standards-conformance or precision test.

Exact external invocations and results:

```sh
for f in .shokunin/audio/corpus/live/round-57/scout/scout-valid{15,16}.wav; do echo "FILE=$f"; ffprobe -v error -show_entries stream=codec_name,sample_fmt,bits_per_sample,bits_per_raw_sample,sample_rate,channels:format=duration -of json "$f"; echo FFPROBE_EXIT=$?; sox --i "$f"; echo SOX_INFO_EXIT=$?; done
```

Overall shell exit **0**. For each input ffprobe exited **0** and returned `codec_name=pcm_s16le`, `sample_fmt=s16`, `sample_rate=48000`, `channels=1`, `bits_per_sample=16`, duration `0.120000`; it omitted `bits_per_raw_sample` and did not expose valid bits. SoX info exited **0** on both, reporting one channel, 48 kHz, `16-bit Signed Integer PCM`, 0.12 s / 5,760 samples. Thus ffprobe/SoX report the container/decode width, not the differing 15/16 valid-bit header field.

```sh
sox .shokunin/audio/corpus/live/round-57/scout/scout-valid15.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-57/scout/scout-valid15.f32
sox .shokunin/audio/corpus/live/round-57/scout/scout-valid16.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-57/scout/scout-valid16.f32
```

Both SoX commands exited **0**. Comparing their little-endian f32 files in the project Python environment gave 5,760 samples each, exact `array_equal=True`, max difference 0, differing-sample count 0; each decoded-vector SHA-256 is `d80f13858e4fdcf641f2164b440a99a42711fd4213239ad809c8136ee4620ce7`. The equivalent stdout checks `sox <file> -t f32 -e floating-point - | sha256sum` exited pipeline statuses `0 0` on each and produced that same hash.

Direct unchanged project-measurer invocation exited **0**:

```sh
python3 -c 'import importlib.util; from pathlib import Path; s=importlib.util.spec_from_file_location("m", ".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); p=Path(".shokunin/audio/corpus/live/round-57/scout").resolve(); [print(m.measure("ui",m.SPECS["ui"],p/f)) for f in ("scout-valid15.wav","scout-valid16.wav")]'
```

Both direct measurement results have `failures: []`, duration `.12 s`, 48 kHz mono, `pcm_s16le`/16 bits, peak `0.31536865234375`, RMS `-14.628519169868087 dBFS`, centroid `1123.322704293326 Hz`, bandwidth `276.15444981222976 Hz`, LUFS `null`. These are direct `measure()` observations, **not** integrated runner receipts or independent replay. Since the project format predicate only observes codec/container bit fields, matching outputs here do not show the predicate distinguishes 15 from 16 valid bits.

## Boundary

This scouting supports only the historical metadata distinction and the local behavior for these constructed mono PCM extensible headers on current ffprobe/SoX/project-measurer versions. It does not prove standards conformance, preservation of meaningful 15-bit precision, generalized valid-bit detection, codec/container compatibility, or perceptual/fidelity quality. No runner mode, historical replay battery, source, LOG, SCORECARD, canonical artifact, or other report was changed. Scratch files are confined to `corpus/live/round-57/scout/`; this report is the only report written.
