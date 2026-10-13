# R55 critic — extensible PCM16 header and decoder check

## Scope and setup

I read the R55 declaration in `.shokunin/audio/LOG.md` and the R54 executor/critic evidence. I used only an original matched pair in `.shokunin/audio/corpus/live/round-55/critic/`; no shared source, LOG, SCORECARD, canonical artifact, or other report was changed. This is a falsification check of the declared mono PCM16 WAVE_FORMAT_EXTENSIBLE representation against a conventional PCM16 WAV, not a general WAV/decoder claim.

Generation command (exit **0**):

```sh
python3 .shokunin/audio/corpus/live/round-55/critic/generate.py
```

It prints `11520 40 0100000000001000800000aa00389b71`: 5,760 mono samples at 48,000 Hz, 11,520 PCM data bytes, 40-byte `fmt ` payload, and PCM subtype GUID bytes. `extensible.wav` uses tag `0xfffe`, one channel, 48,000 Hz, 96,000 byte/s, block-align 2, container bits16, extension size22, valid bits16, channel mask `0x4` (front-center), and the PCM subtype GUID `{00000001-0000-0010-8000-00aa00389b71}` in RIFF byte order. The control is ordinary format-tag-1 PCM16. Both contain the same synthesized signed-16 sample stream (`.25*sin(2*pi*1000*t)+.08*sin(2*pi*1500*t)`, rounded from `x*32767`).

SHA-256 / bytes: extensible `bd7d95901935c0effe21fd64e44a47487372be9d0c80f86cc725380df0352f47` / 11,588; conventional PCM16 `9ac26f38a7df9b1dd60c6130049d1e37056811fcd241f15a03559b5766bb4ba9` / 11,564.

## Metadata and project gate

Metadata command (exit **0**):

```sh
for f in .shokunin/audio/corpus/live/round-55/critic/*.wav; do echo "$f"; ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt:format=duration -of json "$f"; done
```

For both files ffprobe reports `codec_name=pcm_s16le`, `sample_fmt=s16`, 16 bits, mono, 48,000 Hz, duration `.120000` s. No ffprobe error or setup issue occurred.

Unchanged project UI measurer command (exit **0**):

```sh
python3 -c 'import importlib.util; from pathlib import Path; s=importlib.util.spec_from_file_location("m",".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); p=Path(".shokunin/audio/corpus/live/round-55/critic").resolve(); [print(m.measure("ui",m.SPECS["ui"],p/f)) for f in ("extensible.wav","pcm16.wav")]'
```

Both receipts pass with no failures: duration `.12 s`, 48,000 Hz mono, peak `0.31536865234375`, RMS `-14.628519169868087 dBFS`, centroid `1123.322704293326 Hz`, bandwidth `276.15444981222976 Hz`; integrated LUFS is `null`. The project's `format_failures` predicate sees PCM16 metadata for both. These are direct measurer receipts, not execution of any future opt-in runner mode or replay of the 70-command verifier battery.

SoX decoder commands each exit **0**, with no warning/output:

```sh
sox .shokunin/audio/corpus/live/round-55/critic/extensible.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-55/critic/extensible.f32
sox .shokunin/audio/corpus/live/round-55/critic/pcm16.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-55/critic/pcm16.f32
```

Comparison command (exit **0**):

```sh
python3 -c 'import numpy as n; from pathlib import Path; p=Path(".shokunin/audio/corpus/live/round-55/critic"); a=n.fromfile(p/"extensible.f32",dtype="<f4"); b=n.fromfile(p/"pcm16.f32",dtype="<f4"); print(len(a),len(b),n.array_equal(a,b),float(n.max(n.abs(a-b))))'
```

Output: `5760 5760 True 0.0`. SoX-f32 vectors are elementwise equal for this identical sample payload.

## Falsification result and limits

I found no counterexample to this local claim: the extensible header has the declared PCM subtype GUID, mono front-center mask, 16 valid/container bits and 40-byte format chunk; ffprobe identifies PCM16; SoX decodes; and the unchanged project measurer passes both containers. There was no setup failure or gate failure in these tests. This does not establish acceptance of other channel masks, channel layouts, valid-bit/container-bit combinations, GUIDs, chunk ordering/padding, multichannel files, other PCM widths/codecs, or other decoder versions. It also does not establish extensible support in an untested runner integration, audibility, quality, general fidelity, production, rights, or promotion. I did not test malformed GUID/mask variants or replay the historical/canonical invariants; those remain for the integration/verifier lane.
