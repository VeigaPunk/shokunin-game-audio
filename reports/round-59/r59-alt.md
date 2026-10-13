# R59 independent alternate — extensible PCM valid-bits 13/16 pair

## Construction and direct header/sample inspection

Created a fresh matched pair in `.shokunin/audio/corpus/live/round-59/alt/`, independently of the R58 pair constructions. Both contain 5,760 signed PCM16 samples (120 ms, mono, 48 kHz). The payload is synthesized from a two-tone signal at 733 Hz and 1,733 Hz with phase offset, scaled and rounded, then each signed sample is multiplied by eight. Every sample is therefore divisible by eight (13-bit-left-aligned-compatible); both files have the exact same 11,520-byte payload. Only `wValidBitsPerSample` differs: 13 versus 16.

The WAVs were constructed directly in Python in the REPL (no shell generator command). Their file SHA-256 values are valid13 `6675145e7cbf11a3ad2a01a20d601f948e382b1e2f063c91eafd2cde34cf2d23` and valid16 `89f72a83f449443e2c86934a24a314c8dfb37d5a78903505fdb1f8b2e7546c77`. Payload SHA-256 for both: `69f4c93791dd6efcb9e560fa0ac044dbc2858ae78e8b3a5b48af52fa925a45ba`; observed signed sample range: `-9008..9000`.

Direct RIFF/header and sample inspection command (exit **0**):

```sh
python3 -c 'import struct,hashlib,pathlib,numpy as np; p=pathlib.Path(".shokunin/audio/corpus/live/round-59/alt");
for n in ("valid13.wav","valid16.wav"):
 b=(p/n).read_bytes(); print(n,"sha256",hashlib.sha256(b).hexdigest(),"size",len(b),"riff",b[:4],struct.unpack_from("<I",b,4)[0],"wave",b[8:12],"fmt_size",struct.unpack_from("<I",b,16)[0],"tag/ch/rate/byte_rate/align/container",struct.unpack_from("<HHIIHH",b,20),"cbsize/valid/mask",struct.unpack_from("<HHI",b,36),"guid",b[44:60].hex(),"data_size",struct.unpack_from("<I",b,64)[0]); x=np.frombuffer(b[68:],dtype="<i2"); print("samples",len(x),"all_div8",bool(np.all(x.astype(np.int32)%8==0)),"payload_sha",hashlib.sha256(b[68:]).hexdigest())'
```

Both files are 11,588 bytes with RIFF size 11,580; `WAVE`; fmt size 40; format tag `0xfffe`; mono; 48,000 Hz; byte rate 96,000; block align 2; 16-bit container; `cbSize=22`; speaker mask `0x4`; PCM subtype GUID `0100000000001000800000aa00389b71`; data size 11,520. Valid bits are 13 and 16 respectively. Direct parsing confirms 5,760 samples per file, each divisible by eight, with identical payload SHA. Header output confirms the valid-bits field is the only intended difference.

## ffprobe, SoX, and project metrics

Exact command (overall shell exit **0**; both ffprobe and SoX invocations for each file exit **0**):

```sh
for f in .shokunin/audio/corpus/live/round-59/alt/valid{13,16}.wav; do echo "=== $f"; ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt:format=duration -of json "$f"; echo "ffprobe_exit=$?"; sox "$f" -t f32 -e floating-point "${f%.wav}.f32"; echo "sox_exit=$?"; done
```

For both, ffprobe reports `pcm_s16le`, sample format `s16`, 48,000 Hz, mono, 16 bits/sample, duration `0.120000`. It does not report the differing valid-bit field; that came from the direct RIFF parse.

SoX output-vector comparison command (exit **0**):

```sh
python3 -c 'import numpy as np,hashlib,pathlib; p=pathlib.Path(".shokunin/audio/corpus/live/round-59/alt"); a=np.fromfile(p/"valid13.f32",dtype="<f4"); b=np.fromfile(p/"valid16.f32",dtype="<f4"); print("n",len(a),len(b),"sha",hashlib.sha256(a.tobytes()).hexdigest(),hashlib.sha256(b.tobytes()).hexdigest(),"equal",bool(np.array_equal(a,b)),"max_abs",float(np.max(np.abs(a-b))),"range",float(a.min()),float(a.max()))'
```

Both decoded vectors contain 5,760 float32 values and have SHA-256 `bbbb82bf8617651923a2ec5df448a0236859531f3cab6bc5a23d64fc71c5d506`. They compare equal (`True`), max absolute difference `0.0`; range `-0.27490234375..0.274658203125`.

Unchanged direct project UI measurement command (exit **0**):

```sh
python3 -c 'import importlib.util; from pathlib import Path; s=importlib.util.spec_from_file_location("m", ".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); p=Path(".shokunin/audio/corpus/live/round-59/alt").resolve(); [print(m.measure("ui",m.SPECS["ui"],p/f)) for f in ("valid13.wav","valid16.wav")]'
```

Both direct measurements report duration `.12 s`, 48 kHz mono `pcm_s16le`/16-bit, 5,760 decoded samples, peak `0.27490234375`, RMS `-16.417913628356494 dBFS`, centroid `2183.8567726975975 Hz`, bandwidth `3782.1286179645645 Hz`, integrated LUFS `null`, and `failures: []`. This is direct `measure()` evidence, not an integrated runner invocation or receipt.

## Scope and limitations

No command failed; no setup error, runner receipt, or receiptless runner attempt occurred. This alternate did not invoke either integrated opt-in runner mode and is not the named non-author replay. Evidence is limited to this independently synthesized matched pair, its all-divisible-by-eight payload and headers, and this host's ffprobe/SoX/project-measurement path. It does not establish valid-bit metadata enforcement, meaningful precision or fidelity, behavior for arbitrary payloads or other containers/readers, universal extensible-WAV support, audibility or quality, production suitability, rights, engine behavior, publishing, or promotion. No shared source, LOG, SCORECARD, canonical artifact, or other report was changed; no commit or push was made.
