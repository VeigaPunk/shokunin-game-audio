# R60 critic — valid-bits zero is not a valid positive case

## Question and bounded conclusion

I read `/tmp/mission-audio-standing.md`, the R60 declaration in `.shokunin/audio/LOG.md`, and R59 source/reports (`r59-executor.md`, `r59-critic.md`, `r59-verifier.md`, `r59-adjudicator.md`, plus `measure_audio.py`). The R60 probe asks whether a WAVE_FORMAT_EXTENSIBLE PCM-subtype header whose `wValidBitsPerSample` is zero is rejected by the host reader or passes through as PCM16. Zero is an invalid/unspecified declaration here, **not** a conforming “0-bit audio” positive format. The meaningful result is that the inspected host stack does not expose/reject this field in the tested path: ffprobe reports 16-bit PCM, SoX decodes it as PCM16, and the project’s direct `measure()` call passes its ordinary numeric/format checks. This is evidence of acceptance/ignorance for these files on this host, not evidence that a standards-conforming reader should accept zero or that all readers accept it.

This is **not an integrated runner replay**. Current runner/builder source has no R60 valid0 mode. I did not edit shared files or create a runner receipt. Do not count the unsupported flag attempt below as a decoder rejection or gate failure.

## Original candidate and paired control

I examined the executor’s original `.shokunin/audio/corpus/live/round-60/executor/{valid-0,valid-16}.wav`. Exact header/payload inspection command (exit **0**):

```sh
python3 - <<'PY'
import struct,hashlib,numpy as np
from pathlib import Path
p=Path('.shokunin/audio/corpus/live/round-60/executor')
for name in ['valid-0.wav','valid-16.wav']:
 b=(p/name).read_bytes(); i=b.index(b'fmt '); z=struct.unpack_from('<I',b,i+4)[0]; f=b[i+8:i+8+z]; j=b.index(b'data'); d=b[j+8:]; a=np.frombuffer(d,dtype='<i2')
 print(name,'bytes',len(b),'sha256',hashlib.sha256(b).hexdigest(),'riff_size',struct.unpack_from('<I',b,4)[0],'fmt_size',z,'tag',hex(struct.unpack_from('<H',f)[0]),'channels',struct.unpack_from('<H',f,2)[0],'rate',struct.unpack_from('<I',f,4)[0],'byte_rate',struct.unpack_from('<I',f,8)[0],'block_align',struct.unpack_from('<H',f,12)[0],'container_bits',struct.unpack_from('<H',f,14)[0],'cbSize',struct.unpack_from('<H',f,16)[0],'valid_bits',struct.unpack_from('<H',f,18)[0],'mask',hex(struct.unpack_from('<I',f,20)[0]),'guid',f[24:40].hex(),'data_bytes',len(d),'payload_sha',hashlib.sha256(d).hexdigest(),'frames',len(a),'range',(int(a.min()),int(a.max())))
PY
```

Both files are 11,588 bytes (RIFF size 11,580), fmt size 40, tag `0xfffe`, mono 48,000 Hz, byte rate 96,000, block align 2, 16-bit container, `cbSize=22`, channel mask `0x4`, PCM subtype GUID `0100000000001000800000aa00389b71`, and 11,520-byte data chunks / 5,760 frames. Only valid-bits is intended to differ: 0 versus 16. Both payloads have SHA-256 `6e76d877b1e153b636b883f06dea7d3fd7f43374a72fa2cba678c8f4560c9711`; file SHA-256 valid0 `5ab169fc3f43b29c0bb17cc86e6b76fb424e590b7d788a503a002501c8a2f394`, valid16 `d7f08d659b608e003e5ef2aaccf325dae3bd4e961caeaa450bd933c406b4cc46`. Payload signed-sample range is −2703..2702. This payload is not the R59 executor payload: that prior matched 13/16 comparison used its own divisible-by-eight payload, and its critic further showed SoX applied ordinary PCM16 scaling. R60 uses its own unshifted PCM16 sample payload; equal decode still says nothing about valid0 semantics.

## Reader/decoder observations

Exact ffprobe command, run once for each file (both exits **0**):

```sh
for f in .shokunin/audio/corpus/live/round-60/executor/valid-{0,16}.wav; do echo ===$f; ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt:format=duration -of json "$f"; echo ffprobe_exit=$?; done
```

Both outputs report `pcm_s16le`, `s16`, sample rate 48000, one channel, `bits_per_sample: 16`, duration `0.120000`. This selected metadata query does not report `wValidBitsPerSample`; it therefore cannot show the field was interpreted as zero or enforced.

Exact SoX decode commands (each exit **0**) and comparison (exit **0**):

```sh
sox .shokunin/audio/corpus/live/round-60/executor/valid-0.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-60/critic/valid0.f32
echo sox0_exit=$?
sox .shokunin/audio/corpus/live/round-60/executor/valid-16.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-60/critic/valid16.f32
echo sox16_exit=$?
python3 -c 'import numpy as np,hashlib; from pathlib import Path; p=Path(".shokunin/audio/corpus/live/round-60/critic"); a=np.fromfile(p/"valid0.f32",dtype="<f4"); b=np.fromfile(p/"valid16.f32",dtype="<f4"); print("samples",len(a),len(b),"equal",np.array_equal(a,b),"different",np.count_nonzero(a!=b),"maxdiff",np.max(np.abs(a-b)),"sha0",hashlib.sha256((p/"valid0.f32").read_bytes()).hexdigest(),"sha16",hashlib.sha256((p/"valid16.f32").read_bytes()).hexdigest())'
echo compare_exit=$?
```

Each decode produced 5,760 float32 samples. Vectors are exactly equal (zero differing samples, max difference 0.0), both SHA-256 `adc56a24cd7a2bc4c34ef6112b384b3567f6d6b1e4568aef0c8722f6170dca6c`. This establishes that this SoX invocation accepted and decoded both byte-identical payloads alike; it does not establish that SoX recognizes zero valid bits as meaningful audio precision.

## Project numeric gate versus fixture-format gate

I called the unchanged project measurement function directly on both files. Exact command (exit **0**):

```sh
python3 -c 'import importlib.util; from pathlib import Path; s=importlib.util.spec_from_file_location("m", ".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); p=Path(".shokunin/audio/corpus/live/round-60/executor").resolve(); [print(m.measure("ui",m.SPECS["ui"],p/f)) for f in ("valid-0.wav","valid-16.wav")]'
echo measure_exit=$?
```

Both direct results have duration `.12`, rate 48000, mono, `pcm_s16le`/16 bits, peak `0.082489013671875`, RMS `-26.87354274685677 dBFS`, LUFS null, centroid `2139.5871109211243 Hz`, bandwidth `3627.575019576501 Hz`, and empty `failures`. The valid0 file is therefore accepted by the **existing measurement path**, with numeric checks passing. This is not an R60 integrated receipt or an R60 parser change.

The distinction matters: `format_failures(stream)` checks ffprobe’s sample rate/channels, codec name `pcm_s16le`, and container `bits_per_sample == 16`. It does not parse the RIFF extensible `wValidBitsPerSample` at offset 38. Thus the current fixture-format gate is a **PCM16 container/stream gate**, not validation of the valid-bits field. Passing its format and numeric checks cannot establish valid0 conformance. In contrast, a real gate rejection would be a structured project `format` failure after decoding/measurement; a tool/setup/CLI refusal before a receipt is a separate outcome.

As a bounded check that no R60 runner path is integrated yet, I tried the declared-style flag. Exact command (exit **2**):

```sh
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-valid-0-r60
```

Argparse says `unrecognized arguments: --probe-ui-extensible-valid-0-r60`; there is no receipt. This is an unavailable-runner/setup result, **not** a reader/decoder rejection, not a fixture-format gate result, and not evidence either way about how an integrated mode would report valid0.

## Other original candidates and limits

The wave also has original alt and scout scratch pairs. I inspected only RIFF facts (command exit **0**): all are 11,588-byte mono48k extensible PCM16 files with valid bits 0/16 and each pair has identical payload bytes internally. They use different payloads from the executor and from each other; hashes are recorded by their owners. I did not run separate SoX/project-measurement commands on those alternatives; they are not substitutes for the executor result or integrated verifier evidence.

I make no standards-conformance ruling beyond the mission’s characterization that zero is invalid/unspecified; no universal-reader or all-decoder claim, no meaningful zero-bit audio/precision/fidelity claim, and no audible, quality, production, rights, engine, publishing, or promotion claim. This critic generated only decoded scratch under `.shokunin/audio/corpus/live/round-60/critic/` and wrote only this scoped report; no shared source, LOG, SCORECARD, canonical artifact, other report, commit, or push was touched.
