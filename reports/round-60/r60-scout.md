# R60 scout — malformed extensible WAV valid-bits field (0)

## Historical map and question

- R57–R59 each compared matched WAVE_FORMAT_EXTENSIBLE PCM-subtype PCM16-container files against valid-bit control 16 (respectively valid15, valid14, valid13). The selected fixtures had identical payloads aligned to multiples of 2, 4 and 8 as applicable. For those files, recorded ffprobe reported `pcm_s16le`, `sample_fmt=s16`, 16 `bits_per_sample`, mono 48 kHz, `.120000` s; SoX `--i` reported 16-bit Signed Integer PCM and SoX f32 decodes were equal within each matched pair. Project `format_failures()` checked sample rate, channel count, codec name and container bit count, not `wValidBitsPerSample`. R22 historical PCM24/20-valid evidence similarly reported container/decoder fields without exposing valid bits. These prior results are bounded host-path observations, not valid-bit enforcement or fidelity tests.
- R60 is different: `wValidBitsPerSample=0` is an invalid/unspecified declaration for PCM extensible, deliberately malformed, not a conforming positive case. This scout tested whether local ffprobe/SoX/direct project measurement reject it or proceed as PCM16. It did not run the integrated opt-in runner or create a receipt.

## Fresh original scratch pair

Created with Python REPL in `.shokunin/audio/corpus/live/round-60/scout/`, not shell. Both are synthetic UI-shaped 5,760-frame (120 ms), mono, 48 kHz signed16 payloads; the exact same payload is under the valid-bits-zero and valid-bits-16 headers. The two files are each 11,588 bytes (RIFF declared size 11,580). Payload SHA-256 is `67ea695da5665554f467cae513d0c2d3d62d588516299f7eb4872bf79d58df4e`. WAV SHA-256: valid0 `04a57567f7f9b28996cb9555704bae3413b27765c2cc67ddc4aeef29680721db`; valid16 `bd7d95901935c0effe21fd64e44a47487372be9d0c80f86cc725380df0352f47`.

A direct RIFF parser observed for each: `fmt ` size 40, tag `0xfffe`, `cbSize=22`, mono, 48,000 Hz, byte rate 96,000, block align 2, container bits 16, channel mask `0x4`, PCM subtype GUID `0100000000001000800000aa00389b71`, data bytes 11,520. The sole header difference is the `wValidBitsPerSample` field (0 versus 16); these are distinct values only, and zero is not endorsed as valid metadata.

## Commands and observed exits

Exact header/metadata command, overall shell exit **0**; for both files parser, ffprobe and SoX info each exited **0**:

```sh
for f in .shokunin/audio/corpus/live/round-60/scout/valid{0,16}.wav; do echo "FILE=$f"; python3 -c 'import struct,hashlib,sys; b=open(sys.argv[1],"rb").read(); i=b.index(b"fmt "); n=struct.unpack_from("<I",b,i+4)[0]; x=b[i+8:i+8+n]; j=b.index(b"data"); d=b[j+8:]; print({"bytes":len(b),"riff_size":struct.unpack_from("<I",b,4)[0],"fmt_size":n,"tag":hex(struct.unpack_from("<H",x)[0]),"channels":struct.unpack_from("<H",x,2)[0],"rate":struct.unpack_from("<I",x,4)[0],"byte_rate":struct.unpack_from("<I",x,8)[0],"block_align":struct.unpack_from("<H",x,12)[0],"container_bits":struct.unpack_from("<H",x,14)[0],"cbSize":struct.unpack_from("<H",x,16)[0],"valid_bits":struct.unpack_from("<H",x,18)[0],"mask":hex(struct.unpack_from("<I",x,20)[0]),"guid":x[24:40].hex(),"data_bytes":len(d),"payload_sha256":hashlib.sha256(d).hexdigest()})' "$f"; echo PARSE_EXIT=$?; ffprobe -v error -show_entries stream=codec_name,sample_fmt,bits_per_sample,bits_per_raw_sample,sample_rate,channels:format=duration -of json "$f"; echo FFPROBE_EXIT=$?; sox --i "$f"; echo SOX_INFO_EXIT=$?; done
```

For both valid0 and valid16, ffprobe returned exit 0 and `codec_name=pcm_s16le`, `sample_fmt=s16`, sample rate 48000, channels 1, `bits_per_sample=16`, format duration `.120000`; `bits_per_raw_sample` was omitted. SoX info returned exit 0 and reported 1 channel, 48 kHz, precision 16-bit, 5,760 samples, `16-bit Signed Integer PCM`. Neither tool surfaced valid-bits=0 or rejected the file.

Exact SoX decode + vector-compare command, overall shell exit **0**; each decode and comparison exited **0**:

```sh
set +e
sox .shokunin/audio/corpus/live/round-60/scout/valid0.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-60/scout/valid0.f32; echo SOX_DECODE0_EXIT=$?
sox .shokunin/audio/corpus/live/round-60/scout/valid16.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-60/scout/valid16.f32; echo SOX_DECODE16_EXIT=$?
python3 -c 'import numpy as np,hashlib; from pathlib import Path; p=Path(".shokunin/audio/corpus/live/round-60/scout"); a=np.fromfile(p/"valid0.f32",dtype="<f4"); b=np.fromfile(p/"valid16.f32",dtype="<f4"); print("n",len(a),len(b),"equal",np.array_equal(a,b),"different",int(np.count_nonzero(a!=b)),"maxdiff",float(np.max(np.abs(a-b))),"sha0",hashlib.sha256((p/"valid0.f32").read_bytes()).hexdigest(),"sha16",hashlib.sha256((p/"valid16.f32").read_bytes()).hexdigest())'; echo COMPARE_EXIT=$?
```

Both decodes yielded 5,760 f32 samples, exactly equal (0 differing; max difference 0); each decoded-vector SHA-256 `d80f13858e4fdcf641f2164b440a99a42711fd4213239ad809c8136ee4620ce7`.

Exact direct unchanged project UI-measurement command, exit **0**:

```sh
python3 -c 'import importlib.util; from pathlib import Path; s=importlib.util.spec_from_file_location("m", ".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); p=Path(".shokunin/audio/corpus/live/round-60/scout").resolve(); [print(m.measure("ui",m.SPECS["ui"],p/f)) for f in ("valid0.wav","valid16.wav")]'
```

Both direct measurements returned `failures: []`: `.12` s, 48 kHz mono, `pcm_s16le`/16 bits, peak `0.31536865234375`, RMS `-14.628519169868087 dBFS`, LUFS `null`, centroid `1123.322704293326 Hz`, bandwidth `276.15444981222976 Hz`. This is direct `measure()`, **not** an integrated runner receipt. The source predicate still only tests rate/channels and `pcm_s16le`/16 bits. For this exact malformed header on this local path, neither ffprobe, SoX nor direct project measure rejected it; the project gate sees a PCM16 stream and the unchanged UI numeric checks pass.

## Setup and limits

WAV creation and local inspection setup used Python REPL. An initial REPL mistake attempted to `await` an already completed BashResult; it was harness orchestration only, produced no extra command or audio result. No ffprobe, SoX decode, or direct measurement command failed. No integrated runner mode/replay was invoked, so no runner receipt, setup failure, decoder failure or gate-failure classification is claimed. Scratch files are confined to the permitted `corpus/live/round-60/scout/`; this report is the only report written.

This demonstrates only that one constructed malformed `validBits=0` extensible PCM16-subtype header was accepted and treated as PCM16 by these installed local tools and the unchanged direct measurement function, with this payload. It is not standards conformance, a valid zero-bit signal, universal decoder behavior, valid-bit enforcement/precision/fidelity, or an assertion that the integrated runner creates a receipt. No source, LOG, SCORECARD, canonical artifact, or other report was changed; no commit or push was made.
