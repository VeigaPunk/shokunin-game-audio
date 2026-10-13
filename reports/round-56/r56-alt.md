# R56 independent alternate — extensible PCM16 channel-mask pair

## Construction

Independently generated a 5,760-frame (0.120 s), mono, 48,000 Hz signed PCM16 signal and wrote identical sample bytes to two WAVE_FORMAT_EXTENSIBLE RIFF/WAVE files in `.shokunin/audio/corpus/live/round-56/alt/`. Signal: `.21*sin(2π·733t)+.09*sin(2π·1823t)+.035*sin(2π·3111t)`, rounded/clipped to signed 16-bit. Both headers use format tag `0xfffe`, 40-byte `fmt ` payload, `cbSize=22`, valid bits 16, PCM subtype GUID `00000001-0000-0010-8000-00aa00389b71`; the sole intended difference is mono channel mask `0x0` versus `0x4` (front center).

Generation command (exit **0**):

```sh
python3 .shokunin/audio/corpus/live/round-56/alt/generate_pair.py
```

| File | Bytes | SHA-256 |
|---|---:|---|
| `mask0.wav` | 11,588 | `a97b448403159f395d85bb125074fa8770a8922e85dd693c39e0cd2b70ed8a64` |
| `mask4.wav` | 11,588 | `2e27b356969c02f6d8c2a882513ab3c35dc2ddbaa75ed8ce46c2b0d3fee09db1` |

I inspected the RIFF `fmt ` bytes with this command (exit **0**):

```sh
python3 -c 'from pathlib import Path; import struct; p=Path(".shokunin/audio/corpus/live/round-56/alt");
for name in ("mask0.wav","mask4.wav"):
 b=(p/name).read_bytes(); i=b.index(b"fmt "); size=struct.unpack_from("<I",b,i+4)[0]; f=b[i+8:i+8+size]; print(name,"fmt_size",size,"tag",hex(struct.unpack_from("<H",f)[0]),"channels",struct.unpack_from("<H",f,2)[0],"rate",struct.unpack_from("<I",f,4)[0],"validbits",struct.unpack_from("<H",f,18)[0],"mask",hex(struct.unpack_from("<I",f,20)[0]),"guid",f[24:40].hex())'
```

Actual output confirms both have `fmt_size 40`, tag `0xfffe`, one channel, 48,000 Hz, valid bits 16 and the PCM subtype GUID bytes `0100000000001000800000aa00389b71`; masks are `0x0` and `0x4` respectively.

## Metadata, decoder, and UI checks

ffprobe command (exit **0** for the loop and each file):

```sh
for f in .shokunin/audio/corpus/live/round-56/alt/mask{0,4}.wav; do echo "$f"; ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt:format=duration -of json "$f"; done
```

For both: `codec_name=pcm_s16le`, `sample_fmt=s16`, 48,000 Hz, one channel, 16 bits/sample, duration `0.120000` s.

SoX decode commands (each exit **0**):

```sh
sox .shokunin/audio/corpus/live/round-56/alt/mask0.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-56/alt/mask0.f32
sox .shokunin/audio/corpus/live/round-56/alt/mask4.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-56/alt/mask4.f32
```

Vector comparison (exit **0**):

```sh
python3 -c 'import numpy as n; from pathlib import Path; p=Path(".shokunin/audio/corpus/live/round-56/alt"); a=n.fromfile(p/"mask0.f32",dtype="<f4"); b=n.fromfile(p/"mask4.f32",dtype="<f4"); print(len(a),len(b),n.array_equal(a,b),float(n.max(n.abs(a-b))),int(n.count_nonzero(a!=b)))'
```

Output: `5760 5760 True 0.0 0`. SoX-f32 vectors were elementwise identical for this same-payload pair.

Unchanged project UI measurement command (exit **0**):

```sh
python3 -c 'import importlib.util; from pathlib import Path; s=importlib.util.spec_from_file_location("m", ".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); p=Path(".shokunin/audio/corpus/live/round-56/alt").resolve(); [print(m.measure("ui",m.SPECS["ui"],p/f)) for f in ("mask0.wav","mask4.wav")]'
```

Both project receipts have duration `.12 s`, 48,000 Hz mono, `pcm_s16le`/16-bit; peak `0.332763671875`, RMS `-15.733827796556053 dBFS`, centroid `2395.3473292229046 Hz`, bandwidth `3257.8551461120132 Hz`, LUFS `null`, and `failures: []`. Thus both pass the current project UI measurement gates. These are direct measurements, not integrated runner-mode or replay receipts.

## Limits and scope

This independent result supports only these two matched mono PCM16 payloads, the exact extensible PCM subtype/valid-bits header, masks `0x0` and `0x4`, and the local ffprobe/SoX/project-measurement environment. It does not establish behavior for other masks/layouts, arbitrary extensible headers, codec compatibility generally, fidelity beyond equality of these decoded vectors, audibility/quality, production, rights, engine behavior, or publishing. No shared source, LOG, SCORECARD, canonical artifact, or other report was changed; no commit or push was made.
