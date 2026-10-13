# R56 critic — falsification of extensible PCM16 mask-0 case

## Scope

I read the standing brief, R56 declaration in `.shokunin/audio/LOG.md`, and R55 source/evidence (`build_artifacts.py`, `measure_audio.py`, and R55 executor/critic/verifier reports). I created only original scratch fixtures in `.shokunin/audio/corpus/live/round-56/critic/` and this report. The check targets whether a mono WAVE_FORMAT_EXTENSIBLE channel mask of zero is actually distinct/accepted versus `0x4`, whether the GUID/header are constructed as claimed, and whether decoder/gate metadata could hide a failure. It does not replay an integrated R56 runner mode or the verifier battery.

## Construction and header inspection

Generation command (exit **0**):

```sh
python3 ".shokunin/audio/corpus/live/round-56/critic/generate.py"
```

It generated 5,760 mono signed-16 samples at 48 kHz (0.120 s; 11,520 payload bytes), the same `.25*sin(2π·1000t)+.08*sin(2π·1500t)` source as the R55 reference. The pair differs only in channel mask; both headers are tag `0xfffe`, 40-byte `fmt `, `cbSize=22`, valid/container bits 16, one channel, byte rate 96,000, block align 2, and PCM subtype GUID on disk `0100000000001000800000aa00389b71` (canonical displayed GUID `{00000001-0000-0010-8000-00aa00389b71}`). Direct parsed output:

```text
mask0.wav bytes 11588 fmt_size 40 tag 0xfffe channels 1 rate 48000 align 2 bits 16 cbSize 22 valid 16 mask 0x0 guid 0100000000001000800000aa00389b71 frames 5760
mask4.wav bytes 11588 fmt_size 40 tag 0xfffe channels 1 rate 48000 align 2 bits 16 cbSize 22 valid 16 mask 0x4 guid 0100000000001000800000aa00389b71 frames 5760
```

SHA-256: `mask0.wav` **3399ae3661b0ebd6eb4fe7c3a7cf6f4f97cd2d5ec259638164d93c810952a193**; `mask4.wav` **bd7d95901935c0effe21fd64e44a47487372be9d0c80f86cc725380df0352f47** (R55 known fixture hash). `mask0` is a real zero field, not an omitted extension or an incorrectly endian-encoded GUID. At this channel count it means no speaker-position assignment is supplied; it should not be read as front-center, a speaker layout, or proof of any multi-channel behavior.

## Metadata, decode, and UI gate

For each of `mask0.wav` and `mask4.wav`, this command exited **0**:

```sh
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt:format=duration -of json <file>
```

Both reported `codec_name=pcm_s16le`, `sample_fmt=s16`, `sample_rate=48000`, `channels=1`, `bits_per_sample=16`, duration `0.120000`.

Both SoX decode commands exited **0** without output:

```sh
sox ".shokunin/audio/corpus/live/round-56/critic/mask0.wav" -t f32 -e floating-point ".shokunin/audio/corpus/live/round-56/critic/mask0.wav.f32"
sox ".shokunin/audio/corpus/live/round-56/critic/mask4.wav" -t f32 -e floating-point ".shokunin/audio/corpus/live/round-56/critic/mask4.wav.f32"
```

The decoded `<f4` vectors contain 5,760 samples each, are elementwise equal (`array_equal=True`), max absolute difference `0.0`; each decoded-file SHA is `d80f13858e4fdcf641f2164b440a99a42711fd4213239ad809c8136ee4620ce7`.

Unchanged project measurement call for the pair exited **0** and returned no failures for either:

```sh
python3 -c 'import importlib.util; from pathlib import Path; s=importlib.util.spec_from_file_location("m",".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); p=Path("<absolute critic scratch path>"); [print(x,m.measure("ui",m.SPECS["ui"],p/x)) for x in ("mask0.wav","mask4.wav")]'
```

Each receipt: duration `.12 s`, 48,000 Hz mono, PCM16, peak `0.31536865234375`, RMS `-14.628519169868087 dBFS`, centroid `1123.322704293326 Hz`, bandwidth `276.15444981222976 Hz`, integrated LUFS `null`, failures `[]`. So the zero mask does not make the current mono UI gate silently fail or alter its measured decoded samples. This is a direct project-measurer call, not an integrated runner receipt.

## Negative-control / confound check

I also built `bad-guid.wav`, same structural header except subtype GUID first DWORD changed from 1 (PCM) to 2, to check whether “ffprobe says PCM” follows the intended GUID. Its parsed GUID is `0200000000001000800000aa00389b71`, SHA `e797114d14d5fc4949907326a57d5c763a3243dd1bf81c33408f609fdbf0bb0f`. ffprobe exited **0**, but reports `codec_name=adpcm_ms`, `sample_fmt=s16`, `bits_per_sample=4`, 48 kHz mono, duration `.480000`—not PCM16. So ffprobe does distinguish this bad subtype; merely observing `sample_fmt=s16` would be insufficient, but the declared metadata check includes codec and bit depth. SoX command exited **2** with `WARN wav: wave header missing extended part of fmt chunk` and `FAIL ... format[Microsoft ADPCM]: expects wExtSize >= 4`. The unchanged UI measurement attempted across all three files exited **1** because its SoX subprocess raised `CalledProcessError` on this deliberately invalid control; it printed clean measurements for mask0 and mask4 before that failure. This negative-control error is not a failure of either target fixture and was not treated as an expected gate receipt.

## Result and limits

I found no falsifier for the narrow positive claim: this exact valid PCM-subtype GUID / mono / 16-valid-bit / mask-0 extensible fixture is accepted by ffprobe and SoX, has PCM16 metadata, decodes byte-identically to the same mask-`0x4` payload, and passes existing non-format/UI checks. The zero mask conveys unspecified speaker positions, not a positive speaker layout. A malformed subtype control shows why GUID plus codec/bit-depth evidence matters; ffprobe can still return a stream description for a bad header, and the project measurer is not a general malformed-WAV validator.

Bounded to one mono mask-0 fixture, one mask-`0x4` comparison, one altered-GUID negative control, this host's ffprobe/SoX, and current UI measurer. No other masks/layouts, multichannel mapping, chunk permutations, alternate valid bits, codecs, decoder versions, integrated R56 runner exits/replay, production, rights, engine, perception, quality, or general fidelity claim was tested. No shared source, LOG, SCORECARD, canonical artifact, or other report was changed; no commit/push.
