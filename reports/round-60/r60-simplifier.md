# R60 simplifier — malformed valid-bits control

## Recommendation

Do not add a generic extensible-WAV framework or change `format_failures()`, thresholds, canonical data, or prior probes. The declared `wValidBitsPerSample=0` case is malformed/unspecified, not a conforming positive format. The executor pair was accepted by this host’s ffprobe and SoX, and both unchanged direct UI measurements were clean. This supports a narrowly named, opt-in malformed-header control alongside the valid16 control only if the parent’s integration plan needs runner receipts. Keep the builder and pair round-local, use distinct receipt names, and report that a clean gate exposes missing validation only for this case; it is not evidence of standards conformance or general valid-bit semantics. If the parent elects not to integrate, the bounded host observation is still complete. No runner probe/replay was run by this simplifier.

## R60 executor evidence

I read the standing brief, R60 LOG declaration, and R59 source/reports. I inspected the executor’s existing files; I did not modify them. Direct header parser command (exit **0**):

```sh
python3 -c 'import struct,hashlib,numpy as np; from pathlib import Path; p=Path(".shokunin/audio/corpus/live/round-60/executor"); bs=[]
for name in ("valid-0.wav","valid-16.wav"):
 b=(p/name).read_bytes(); i=b.index(b"fmt "); z=struct.unpack_from("<I",b,i+4)[0]; f=b[i+8:i+8+z]; j=b.index(b"data"); d=b[j+8:]; x=np.frombuffer(d,dtype="<i2"); print(name,"bytes",len(b),"wav_sha",hashlib.sha256(b).hexdigest(),"riff_size",struct.unpack_from("<I",b,4)[0],"fmt_size",z,"tag",hex(struct.unpack_from("<H",f)[0]),"channels",struct.unpack_from("<H",f,2)[0],"rate",struct.unpack_from("<I",f,4)[0],"byte_rate",struct.unpack_from("<I",f,8)[0],"align",struct.unpack_from("<H",f,12)[0],"container",struct.unpack_from("<H",f,14)[0],"cbSize",struct.unpack_from("<H",f,16)[0],"valid",struct.unpack_from("<H",f,18)[0],"mask",hex(struct.unpack_from("<I",f,20)[0]),"guid",f[24:40].hex(),"data_size",len(d),"payload_sha",hashlib.sha256(d).hexdigest(),"samples",len(x),"range",int(x.min()),int(x.max())) ; bs.append((b,f,d,x))
print("same_payload",bs[0][2]==bs[1][2],"fmt_equal_except_valid",bs[0][1][:18]+bs[0][1][20:]==bs[1][1][:18]+bs[1][1][20:])'
```

Both files are 11,588 bytes (RIFF size 11,580), WAVE, fmt40, tag `0xfffe`, mono 48,000 Hz, byte rate 96,000, block align 2, 16-bit container, `cbSize=22`, mask `0x4`, and PCM subtype GUID `0100000000001000800000aa00389b71`; data is 11,520 bytes / 5,760 signed16 samples. Valid0 SHA-256 `5ab169fc3f43b29c0bb17cc86e6b76fb424e590b7d788a503a002501c8a2f394`; valid16 SHA-256 `d7f08d659b608e003e5ef2aaccf325dae3bd4e961caeaa450bd933c406b4cc46`. Valid bits are respectively 0 and 16; headers differ only at that field. Both have identical payload SHA-256 `6e76d877b1e153b636b883f06dea7d3fd7f43374a72fa2cba678c8f4560c9711`, length 11,520; 5,760 samples range −2703..2702.

Exact host metadata command (overall exit **0**; each ffprobe and SoX info call exit **0**):

```sh
for f in .shokunin/audio/corpus/live/round-60/executor/valid-{0,16}.wav; do echo "=== $f"; ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt:format=duration -of json "$f"; echo "ffprobe_exit=$?"; sox --i "$f"; echo "sox_info_exit=$?"; done
```

For both: ffprobe reports `pcm_s16le`, `s16`, 48,000 Hz, mono, 16 bits/sample, duration `0.120000`; SoX reports 16-bit signed integer PCM and 5,760 samples. Neither reports the valid-bits field. SoX decoding commands each exited **0**:

```sh
sox .shokunin/audio/corpus/live/round-60/executor/valid-0.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-60/executor/valid-0.f32
echo "sox_decode_exit=$?"
sox .shokunin/audio/corpus/live/round-60/executor/valid-16.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-60/executor/valid-16.f32
echo "sox_decode_exit=$?"
```

The comparison command exited **0**. Both vectors contain 5,760 float32 samples, SHA-256 `adc56a24cd7a2bc4c34ef6112b384b3567f6d6b1e4568aef0c8722f6170dca6c`; exactly equal, zero differing samples, maximum absolute difference 0.0.

Unchanged direct project UI measurement command exited **0**:

```sh
python3 -c 'import importlib.util; from pathlib import Path; s=importlib.util.spec_from_file_location("m", ".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); p=Path(".shokunin/audio/corpus/live/round-60/executor").resolve(); [print(m.measure("ui",m.SPECS["ui"],p/f)) for f in ("valid-0.wav","valid-16.wav")]'
```

Both direct results are clean (`failures: []`): 0.12 s, 48 kHz mono PCM_S16LE/16, peak `0.082489013671875`, RMS `-26.87354274685677 dBFS`, LUFS null, centroid `2139.5871109211243 Hz`, bandwidth `3627.575019576501 Hz`. These are direct measurements, not runner receipts or replay evidence.

## Setup, receipt status, limits

The executor generator’s ordinary command `python3 ".shokunin/audio/corpus/live/round-60/executor/generate.py"` exited **1** during setup: its sibling `inspect.py` shadowed the standard library `inspect` module, causing NumPy import to fail (`AttributeError: module 'inspect' has no attribute 'cleandoc'`). This was an environment/import-path setup issue, not a malformed-WAV rejection or measurement failure. Re-running isolated as `python3 -I ".shokunin/audio/corpus/live/round-60/executor/generate.py"` exited **0** and reproduced the same payload/WAV SHA-256 values above. No runner mode was invoked, so there are no receipts or numeric runner-gate outcomes; no replay is claimed. ffprobe and SoX did not reject valid0 in these observed calls.

Conclusion is bounded to this matched pair and local tool path: the host exposes this invalid zero valid-bits declaration as PCM16 and the unchanged UI measurement accepts its decoded container samples. It does not establish standards conformance, universal decoder behavior, valid-bit enforcement, meaningful precision/fidelity, audibility, quality, production suitability, rights, engine behavior, publishing, or promotion.

This is the only file I wrote: `.shokunin/audio/reports/round-60/r60-simplifier.md`. No shared source, LOG, SCORECARD, canonical artifact, or other report was changed; no commit or push was made.
