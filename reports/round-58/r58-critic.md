# R58 critic — valid14 left-alignment and decode challenge

## Scope and result

Read the standing brief, R58 LOG declaration, and R57 source/reports. This is an independent scratch check, not an integrated-runner replay. I generated a matched 5,760-frame mono/48 kHz WAVE_FORMAT_EXTENSIBLE PCM16-subtype pair with identical payload, all signed values divisible by four, and valid-bits 14 versus 16. Both files were accepted by ffprobe and SoX; SoX vectors were exactly equal, and unchanged project UI measurement reported no failures for either. This is a narrow observed acceptance/equal-output result; it does **not** show that the parser validates or decoder honors `wValidBitsPerSample`.

## Commands, header, and payload evidence

Generation command `python3 .shokunin/audio/corpus/live/round-58/critic/generate.py` exited **0**. It created scratch files only in `corpus/live/round-58/critic/`. Generator output: valid14 WAV SHA-256 `f02d3e960d0b641558c34a97803aa0566de6db666de65fb2bf50c8c9a9961eb6`; valid16 SHA-256 `fbc8ebdc1a2d3d5c430ff139f4bbe4ff36bca402d901729d15ac00c44bac2b60`; both 11,588 bytes. The shared 11,520-byte payload SHA-256 is `0e4e786426ecc152d5b1189c05252fc1a8cf287c749a97cad2ac9e887031782e`; signed sample range is `-13752..13748`, all 5,760 values divisible by four (zero values not divisible by four). That is consistent with two low-order padding bits for a 14-valid-bit value in a 16-bit container.

Direct RIFF parser/metadata comparison command exited **0**:

```sh
python3 -c 'import numpy as n, hashlib, struct; from pathlib import Path; p=Path(".shokunin/audio/corpus/live/round-58/critic");
for name in ("valid14.wav","valid16.wav"):
 b=(p/name).read_bytes(); i=b.index(b"fmt "); z=struct.unpack_from("<I",b,i+4)[0]; f=b[i+8:i+8+z]; print(name,"fmt",z,"tag",hex(struct.unpack_from("<H",f)[0]),"channels",struct.unpack_from("<H",f,2)[0],"rate",struct.unpack_from("<I",f,4)[0],"align",struct.unpack_from("<H",f,12)[0],"container",struct.unpack_from("<H",f,14)[0],"cbSize",struct.unpack_from("<H",f,16)[0],"valid",struct.unpack_from("<H",f,18)[0],"mask",hex(struct.unpack_from("<I",f,20)[0]),"guid",f[24:40].hex()); d=b[b.index(b"data")+8:]; print("payload",len(d),hashlib.sha256(d).hexdigest())
a=n.fromfile(p/"valid14.f32",dtype="<f4"); b=n.fromfile(p/"valid16.f32",dtype="<f4"); print("decode",len(a),len(b),"equal",n.array_equal(a,b),"different",int(n.count_nonzero(a!=b)),"maxdiff",float(n.max(n.abs(a-b))),"hash",hashlib.sha256((p/"valid14.f32").read_bytes()).hexdigest(),hashlib.sha256((p/"valid16.f32").read_bytes()).hexdigest())'
```

Header output: both are fmt size 40, tag `0xfffe`, one channel, 48,000 Hz, block align 2, container bits 16, `cbSize=22`, mask `0x4`, GUID bytes `0100000000001000800000aa00389b71` (PCM subtype). Valid bits are 14 versus 16, the sole header field changed; payload hashes match.

ffprobe command (both invocations and enclosing command exited **0**):

```sh
for f in .shokunin/audio/corpus/live/round-58/critic/valid{14,16}.wav; do echo ===$f; ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt:format=duration -of json "$f"; echo exit=$?; done
```

For each: `codec_name=pcm_s16le`, `sample_fmt=s16`, `sample_rate=48000`, `channels=1`, `bits_per_sample=16`, duration `0.120000`. ffprobe output reports the 16-bit PCM stream/container, not valid bits.

Each exact SoX command exited **0**:

```sh
sox .shokunin/audio/corpus/live/round-58/critic/valid14.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-58/critic/valid14.f32
sox .shokunin/audio/corpus/live/round-58/critic/valid16.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-58/critic/valid16.f32
```

Comparison in the direct-parser command above: 5,760 decoded values each, exact array equality, 0 differing samples, max absolute difference `0.0`; both float32 files have SHA-256 `b18887926c056995a876639981e13704bf052fbf498e58b2ffe79d33d0892485`.

## Existing project gate and semantic limitation

Unchanged project UI measurement command exited **0**:

```sh
python3 -c 'import importlib.util; from pathlib import Path; s=importlib.util.spec_from_file_location("m", ".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); p=Path(".shokunin/audio/corpus/live/round-58/critic").resolve(); [print(m.measure("ui",m.SPECS["ui"],p/f)) for f in ("valid14.wav","valid16.wav")]'
```

Both results: duration `.12 s`, 48 kHz mono, `pcm_s16le`/16 bits, peak `0.419677734375`, RMS `-12.821422447778616 dBFS`, centroid `2153.742616905067 Hz`, bandwidth `3627.640459173434 Hz`, LUFS `None`, failures `[]`.

I inspected existing `format_failures`: it checks ffprobe sample rate/channels, codec name, and `bits_per_sample`; it does not inspect the extensible valid-bits field. So clean project results are expected if ffprobe presents both files as PCM16; they cannot establish that `wValidBitsPerSample=14` is validated. Equal SoX output for this validly aligned payload means only that this SoX path produced identical decoded samples for these headers. It does not demonstrate metadata was applied (or establish how another decoder handles it), nor compare against a separately encoded equivalent 14-bit reference. No decode/setup rejection or numeric-fit failure was observed; no malformed-command setup failure occurred.

## Bounded conclusion

This evidence does not falsify the narrow observed claim that this specifically aligned valid14/valid16 pair is accepted, yields equal SoX vectors, and passes the current UI measurement. It falsifies a stronger interpretation that clean `format_failures` outcomes validate valid-bit semantics: the predicate does not inspect that field. Header isolation and low-bit alignment were verified for this pair. Do not generalize to other valid widths, container combinations, payloads, decoders, WAV conformance, fidelity, audibility, quality, production, rights, engine, or publishing. No integrated runner receipt was attempted; do not count this as verifier replay. No shared source, LOG, SCORECARD, canonical artifact, or other report changed; no commit/push.
