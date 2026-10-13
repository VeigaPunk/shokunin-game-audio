# R57 independent alternate — extensible PCM valid-bits pair

## Construction and header inspection

Independently generated an original 5,760-frame / 0.120 s mono, 48,000 Hz UI-shaped PCM signal in `.shokunin/audio/corpus/live/round-57/alt/`. Both WAVs have the same 11,520-byte sample payload; their sole header difference is `wValidBitsPerSample` (15 vs 16). Signal uses signed values from rounded `.30*sin(2π·997t)+.12*sin(2π·1733t)`, scaled within ±8191 then multiplied by two, so the 15-valid-bit samples are left-aligned in 16-bit containers. This choice makes the payload identical without asserting equal decoding for arbitrary valid-bit encodings.

Exact generation command and exit:

```sh
python3 .shokunin/audio/corpus/live/round-57/alt/generate_pair.py
# exit 0
```

| File | Bytes | SHA-256 |
|---|---:|---|
| `valid15.wav` | 11,588 | `4f41ace3a386c78217c991dae6972be49f3be4a9fa918211c58e3a019af47b2b` |
| `valid16.wav` | 11,588 | `95d180f4c894751924317eb9b7add4d5c84e714a7807eeb14d1319a6ff1f785f` |

The generator also printed payload length 11,520, payload SHA-256 `a6ec402df430818fd02a8437a85af7ab335e51084ca7e224f2b1b15cc2d2b89a`, and signed sample range `-6876..6874` (left-aligned payload values `-13752..13748`).

Exact direct RIFF-field inspection command (exit **0**):

```sh
python3 -c 'from pathlib import Path; import struct; p=Path(".shokunin/audio/corpus/live/round-57/alt");
for name in ("valid15.wav","valid16.wav"):
 b=(p/name).read_bytes(); i=b.index(b"fmt "); size=struct.unpack_from("<I",b,i+4)[0]; f=b[i+8:i+8+size]; print(name,"riff",b[:4],"fmt_size",size,"tag",hex(struct.unpack_from("<H",f)[0]),"channels",struct.unpack_from("<H",f,2)[0],"rate",struct.unpack_from("<I",f,4)[0],"block_align",struct.unpack_from("<H",f,12)[0],"container_bits",struct.unpack_from("<H",f,14)[0],"cbSize",struct.unpack_from("<H",f,16)[0],"valid_bits",struct.unpack_from("<H",f,18)[0],"mask",hex(struct.unpack_from("<I",f,20)[0]),"guid",f[24:40].hex())'
```

Actual output confirms both are RIFF/WAVE, `fmt` size 40, tag `0xfffe`, mono, 48,000 Hz, block align 2, 16 container bits, `cbSize=22`, mask `0x4`, PCM subtype GUID bytes `0100000000001000800000aa00389b71`; valid bits are 15 and 16 respectively. Thus container bits are 16 for both; `wValidBitsPerSample` is the changed field.

## Actual metadata, decoder, and project metrics

Exact ffprobe command (the loop and each ffprobe invocation exited **0**):

```sh
for f in .shokunin/audio/corpus/live/round-57/alt/valid{15,16}.wav; do echo "=== $f"; ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt:format=duration -of json "$f"; echo "ffprobe_exit=$?"; done
```

For **each** file ffprobe reported `codec_name=pcm_s16le`, `sample_fmt=s16`, `sample_rate=48000`, `channels=1`, `bits_per_sample=16`, and duration `0.120000`. ffprobe's reported bits/sample and `sample_fmt` describe the decoded PCM/container representation here; the valid-bit counts above came from direct `fmt ` parsing, not ffprobe.

Exact unchanged project UI measurement command (exit **0**):

```sh
python3 -c 'import importlib.util; from pathlib import Path; s=importlib.util.spec_from_file_location("m", ".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); p=Path(".shokunin/audio/corpus/live/round-57/alt").resolve(); [print(m.measure("ui",m.SPECS["ui"],p/f)) for f in ("valid15.wav","valid16.wav")]'
```

Both project measurements decoded 5,760 samples and reported duration `.12 s`, 48,000 Hz mono, `pcm_s16le`/16-bit, peak `0.2098388671875`, RMS `-18.84202236105824 dBFS`, centroid `2153.742616905067 Hz`, bandwidth `3627.640459173434 Hz`, LUFS `null`, and `failures: []`. Both are clean under this unchanged UI measurement specification.

Exact SoX commands (each exited **0**) and comparison (exit **0**):

```sh
sox ".shokunin/audio/corpus/live/round-57/alt/valid15.wav" -t f32 -e floating-point ".shokunin/audio/corpus/live/round-57/alt/valid15.f32"
sox ".shokunin/audio/corpus/live/round-57/alt/valid16.wav" -t f32 -e floating-point ".shokunin/audio/corpus/live/round-57/alt/valid16.f32"
python3 -c 'import numpy as n; from pathlib import Path; p=Path(".shokunin/audio/corpus/live/round-57/alt"); a=n.fromfile(p/"valid15.f32",dtype="<f4"); b=n.fromfile(p/"valid16.f32",dtype="<f4"); print("count",len(a),len(b),"equal",n.array_equal(a,b),"max_abs_diff",float(n.max(n.abs(a-b))),"different",int(n.count_nonzero(a!=b)),"15_range",float(a.min()),float(a.max()),"16_range",float(b.min()),float(b.max()))'
```

Output: 5,760 samples each, `equal True`, maximum absolute difference `0.0`, differing samples `0`; both decoded ranges were `[-0.2098388671875, 0.20977783203125]`. This establishes equal SoX-f32 decoding for this particular deliberately left-aligned same-payload pair in this environment, not a general valid-bit decode rule.

## Receipt and scope distinction

This alternate only built and measured scratch files. It did **not** invoke the integrated runner modes or produce runner receipts, and is not the non-author verifier replay. There were no receiptless runner attempts: no runner command was attempted. The observed ffprobe, SoX decode, and project measurement setup all succeeded, so this alternate supplies no decode/setup rejection evidence. It independently supports a bounded valid15/valid16 example only; it does not establish all valid-bit values, arbitrary payload alignment, general extensible PCM acceptance, standards conformance, decoder portability, fidelity, audibility/quality, production suitability, rights, engine behavior, or publishing. No shared source, LOG, SCORECARD, canonical artifact, or other report was changed; no commit or push was made.
