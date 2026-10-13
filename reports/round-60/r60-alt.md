# R60 independent alternate — extensible PCM valid-bits 0/16 pair

## Construction and direct header/sample inspection

Built a fresh matched pair in `.shokunin/audio/corpus/live/round-60/alt/` independently of the executor. A deterministic two-tone signed-16 mono signal (811 Hz and 1,901 Hz with fixed phase offsets) supplies 5,760 samples (120 ms at 48 kHz); the same 11,520-byte payload is used in both files. Each is a RIFF/WAVE `WAVE_FORMAT_EXTENSIBLE` file: fmt size 40, tag `0xfffe`, `cbSize=22`, channel mask `0x4`, PCM subtype GUID `0100000000001000800000aa00389b71`, 16-bit container. Only `wValidBitsPerSample` differs: 0 versus 16. The zero-valid-bits case is intentionally malformed/unspecified, not a conforming positive format example. Files were constructed directly in the Python REPL (no shell generator command).

File SHA-256: valid0 `7acaf3dd482247b3ec314051bf79b780460682be511f46e6699ceb88c93cfaa3`; valid16 `67ea24646cda770a8aad028a298ddeb3b3876824ac4ba3a5e2f4533a6b409af1`. Both are 11,588 bytes, RIFF size 11,580, data size 11,520; payload SHA-256 is identical: `b90445495a6598319bfd12fe33452957711d2987004393119cfae752e6654a4b`. Signed-sample range: `-13695..13687`.

Exact direct RIFF/header and sample inspection command (exit **0**):

```sh
python3 -c 'import struct,hashlib,pathlib,numpy as np; p=pathlib.Path(".shokunin/audio/corpus/live/round-60/alt");
for n in ("valid0.wav","valid16.wav"):
 b=(p/n).read_bytes(); print(n,"sha256",hashlib.sha256(b).hexdigest(),"size",len(b),"riff",b[:4],struct.unpack_from("<I",b,4)[0],"wave",b[8:12],"fmt_size",struct.unpack_from("<I",b,16)[0],"tag/ch/rate/byte_rate/align/container",struct.unpack_from("<HHIIHH",b,20),"cbsize/valid/mask",struct.unpack_from("<HHI",b,36),"guid",b[44:60].hex(),"data_size",struct.unpack_from("<I",b,64)[0]); x=np.frombuffer(b[68:],dtype="<i2"); print("samples",len(x),"payload_sha",hashlib.sha256(b[68:]).hexdigest(),"range",int(x.min()),int(x.max()))'
```

Observed fields for each: mono, 48,000 Hz, byte rate 96,000, block align 2, container 16; valid-bits field 0 or 16 as named. There are 5,760 signed samples in each.

## ffprobe, SoX decode, and project measurement

Exact command (overall shell exit **0**; each ffprobe and SoX command exited **0**):

```sh
for f in .shokunin/audio/corpus/live/round-60/alt/valid{0,16}.wav; do echo "=== $f"; ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt:format=duration -of json "$f"; echo "ffprobe_exit=$?"; sox "$f" -t f32 -e floating-point "${f%.wav}.f32"; echo "sox_exit=$?"; done
```

For both files ffprobe reports `pcm_s16le`, `s16`, 48,000 Hz, mono, 16 bits/sample, duration `0.120000`; it does not expose the differing valid-bits field. SoX successfully wrote both float32 vectors.

Exact decoded-vector comparison command (exit **0**):

```sh
python3 -c 'import numpy as np,hashlib,pathlib; p=pathlib.Path(".shokunin/audio/corpus/live/round-60/alt"); a=np.fromfile(p/"valid0.f32",dtype="<f4"); b=np.fromfile(p/"valid16.f32",dtype="<f4"); print("n",len(a),len(b),"sha",hashlib.sha256(a.tobytes()).hexdigest(),hashlib.sha256(b.tobytes()).hexdigest(),"equal",bool(np.array_equal(a,b)),"max_abs",float(np.max(np.abs(a-b))),"range",float(a.min()),float(a.max()))'
```

Both decoded vectors contain 5,760 values, SHA-256 `b2bfc4b727fa063c117a5c2ac1e8c3fd336dff63cff81a6d3b9784d077aca61d`; they are exactly equal, max absolute difference `0.0`, range `-0.417938232421875..0.417694091796875`.

Exact unchanged direct project-measurer command (exit **0**):

```sh
python3 -c 'import importlib.util; from pathlib import Path; s=importlib.util.spec_from_file_location("m", ".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); p=Path(".shokunin/audio/corpus/live/round-60/alt").resolve(); [print(m.measure("ui",m.SPECS["ui"],p/f)) for f in ("valid0.wav","valid16.wav")]'
```

Both `measure()` calls succeeded and returned `failures: []`: duration `.12 s`, 48 kHz mono `pcm_s16le`/16-bit, peak `0.417938232421875`, RMS `-12.506253973644831 dBFS`, centroid `1840.434813087789 Hz`, bandwidth `3315.585657322026 Hz`, integrated LUFS `null`. These are direct measurer results, not integrated runner receipts.

## Runner status, errors, limits

Neither integrated opt-in runner mode was invoked, so this lane has no runner receipt or runner failure to report. There were no decoder, ffprobe, SoX, or direct project-measurement errors. This evidence is limited to this independently generated payload/header pair and this host's ffprobe/SoX/project-measurer behavior. The malformed valid-bits-zero field was accepted and interpreted as PCM16 by these tools on this pair; this does not establish conformance, validation behavior on other readers or payloads, real zero-bit audio, precision/fidelity, audibility, quality, or production suitability. No shared source, LOG, SCORECARD, canonical artifact, or other report was changed; no commit or push was made.
