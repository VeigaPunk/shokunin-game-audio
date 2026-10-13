# R59 critic — valid13 left-alignment, header, decoder, and parser challenge

## Scope and result

I read `/tmp/mission-audio-standing.md`, the R59 declaration in `.shokunin/audio/LOG.md`, and the R58 source/reports (especially `r58-critic.md` and `r58-executor.md`). This is a critic scratch check, not an integrated-runner replay. I challenged the executor's original pair in `corpus/live/round-59/executor/valid-{13,16}.wav`, then ran the direct header/payload check, ffprobe, SoX decode, and the unchanged project UI measurement. For this exact pair, valid13 and valid16 are WAVE_FORMAT_EXTENSIBLE PCM16-subtype headers with identical 5,760-sample payload (every signed sample divisible by eight); only the 13/16 `wValidBitsPerSample` field differs. ffprobe calls both PCM_S16LE/16-bit, SoX yields exactly equal vectors, and both pass unchanged UI measurements. The parser predicate does not inspect valid bits, so this is not evidence of valid-bit metadata enforcement or a meaningful 13-bit decode.

## Direct header and payload check

Exact command, exit **0**:

```sh
python3 -c 'import struct,hashlib,numpy as np; from pathlib import Path; p=Path(".shokunin/audio/corpus/live/round-59/executor"); names=("valid-13.wav","valid-16.wav"); bs=[(p/x).read_bytes() for x in names]; fs=[]
for b in bs:
 i=b.index(b"fmt "); z=struct.unpack_from("<I",b,i+4)[0]; f=b[i+8:i+8+z]; j=b.index(b"data"); d=b[j+8:]; fs.append((f,d)); a=np.frombuffer(d,dtype="<i2"); print("file",len(b),"sha",hashlib.sha256(b).hexdigest(),"fmt",z,"tag",hex(struct.unpack_from("<H",f)[0]),"channels",struct.unpack_from("<H",f,2)[0],"rate",struct.unpack_from("<I",f,4)[0],"align",struct.unpack_from("<H",f,12)[0],"container",struct.unpack_from("<H",f,14)[0],"cbSize",struct.unpack_from("<H",f,16)[0],"valid",struct.unpack_from("<H",f,18)[0],"mask",hex(struct.unpack_from("<I",f,20)[0]),"guid",f[24:40].hex(),"data_len",len(d),"payload_sha",hashlib.sha256(d).hexdigest(),"samples",len(a),"range",int(a.min()),int(a.max()),"divisible8",bool(np.all(a%8==0)),"nondiv8",int(np.count_nonzero(a%8)))
print("same_payload",fs[0][1]==fs[1][1],"only_fmt_field_changed",fs[0][0][:18]+fs[0][0][20:]==fs[1][0][:18]+fs[1][0][20:])'
```

Observed: both files 11,588 bytes, fmt size 40, tag `0xfffe`, mono, 48,000 Hz, block align 2, container 16 bits, `cbSize=22`, mask `0x4`, PCM subtype GUID `0100000000001000800000aa00389b71`. The sole differing fmt bytes are valid bits `0d00` versus `1000`. Both data chunks are 11,520 bytes, SHA-256 `88cac2a0475a0fdbedc4be3758a2215b3937219f13a5c8ff0515a10f1e09ccd1`; 5,760 signed16 samples, range `-21624..21616`, all divisible by 8 (0 non-divisible samples). WAV SHA-256 valid13 `873485d5dd0d5108f0523ab974cbba6ce792e715861d481db0ad68ea35f2f2e0`; valid16 `c8f327e38f34125a15bfe3e490905852a228ba26436b0a3b1633a6f58a4a1f3b`.

## Independent host decode and metadata

Exact command, enclosing exit **0**; both ffprobe invocations and both SoX conversions reported exit **0**:

```sh
for f in .shokunin/audio/corpus/live/round-59/executor/valid-{13,16}.wav; do echo ===$f; ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt:format=duration -of json "$f"; echo exit=$?; done
sox .shokunin/audio/corpus/live/round-59/executor/valid-13.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-59/critic/valid13.f32; echo sox13_exit=$?
sox .shokunin/audio/corpus/live/round-59/executor/valid-16.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-59/critic/valid16.f32; echo sox16_exit=$?
python3 -c 'import numpy as np,hashlib; from pathlib import Path; p=Path(".shokunin/audio/corpus/live/round-59/critic"); a=np.fromfile(p/"valid13.f32",dtype="<f4"); b=np.fromfile(p/"valid16.f32",dtype="<f4"); print("decode",len(a),len(b),"equal",np.array_equal(a,b),"different",int(np.count_nonzero(a!=b)),"maxdiff",float(np.max(np.abs(a-b))),"sha13",hashlib.sha256((p/"valid13.f32").read_bytes()).hexdigest(),"sha16",hashlib.sha256((p/"valid16.f32").read_bytes()).hexdigest())'; echo compare_exit=$?
```

Each ffprobe JSON says `codec_name=pcm_s16le`, `sample_fmt=s16`, sample rate 48000, mono, `bits_per_sample=16`, duration `.120000`; it does not report valid-bits metadata. Each decode has 5,760 samples; vectors equal, 0 differing, max difference 0.0, both decoded-f32 SHA-256 `afb6ad28ef01a4ed9f3a9ebf4423ee7fc7324982f1ed3fd5ad2a711c6c84c3b7`. To challenge what that equality means, exact check against ordinary signed16/container scaling also exited **0**:

```sh
python3 -c 'import numpy as np; from pathlib import Path; p=Path(".shokunin/audio/corpus/live/round-59/executor/valid-13.wav"); b=p.read_bytes(); d=b[b.index(b"data")+8:]; raw=np.frombuffer(d,dtype="<i2").astype(np.float32)/32768; got=np.fromfile(".shokunin/audio/corpus/live/round-59/critic/valid13.f32",dtype="<f4"); print("expected_s16_scale_equal",np.array_equal(raw,got),"different",int(np.count_nonzero(raw!=got)),"maxdiff",float(np.max(np.abs(raw-got))),"sample_head",got[:8].tolist())'
```

It reports exact equality to signed16 divided by 32768 (0 differing, max difference 0; first samples `[0.0, 0.1005859375, 0.198486328125, 0.290771484375, 0.375244140625, 0.44921875, 0.51123046875, 0.559326171875]`). This demonstrates only that this SoX path decodes these aligned payload bytes identically under both headers and applies ordinary PCM16 scaling; it does not show valid13 metadata is interpreted or compare against a valid-13-reference decoder.

## Existing project gate interpretation

Exact unchanged project measurement command exited **0**:

```sh
python3 -c 'import importlib.util; from pathlib import Path; s=importlib.util.spec_from_file_location("m", ".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); p=Path(".shokunin/audio/corpus/live/round-59/executor").resolve(); [print(m.measure("ui",m.SPECS["ui"],p/f)) for f in ("valid-13.wav","valid-16.wav")]'; echo measurement_exit=$?
```

Both clean results: duration `.12`, 48 kHz mono, `pcm_s16le`/16 bits, peak `0.659912109375`, RMS `-8.811743007017897 dBFS`, LUFS `None`, centroid `2139.5871109211243 Hz`, bandwidth `3627.575019576501 Hz`, failures `[]`. Inspection of `format_failures` in `measure_audio.py` shows it checks only ffprobe sample rate/channels and codec name/`bits_per_sample`; it does not parse `wValidBitsPerSample`. Thus the clean predicate result is expected from ffprobe's PCM16 metadata and the identical decoded signal. It cannot establish valid-bit validation. No selected decode/setup failure or numeric gate failure observed, and no malformed-command setup failure was part of this critic check.

## Bounded conclusion and limitations

I did not falsify the narrow result for this deliberately left-aligned pair: the headers differ only in valid bits, both host probes accept them as PCM16, SoX outputs identical vectors, and unchanged UI gate returns no failures. I do challenge any interpretation that the gate or equal decoder outputs demonstrate 13-bit semantics: the existing project parser ignores valid bits, ffprobe exposes only 16-bit PCM, and SoX output exactly follows container-width scaling. No claim about valid-bit enforcement, 13-bit precision/fidelity, other payloads/valid widths, other decoders, universal WAV conformance, audibility, quality, production, rights, engine, or publishing. This was not a runner receipt/verifier replay; it contributes no runner receipt count. All commands above were setup/inspection/decode/gate checks and exited 0; there were no receiptless runner attempts or unexpected command exits. I read R58 source/reports as context but did not rerun them. My generated float scratch files are only under `corpus/live/round-59/critic/`; I changed no shared source, LOG, SCORECARD, canonical artifact, or other report, and did not commit/push.
