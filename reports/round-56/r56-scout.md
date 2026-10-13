# R56 scout — extensible mono channel-mask evidence

## Scope and existing behavior

Read `/tmp/mission-audio-standing.md`, the R56 declaration in `.shokunin/audio/LOG.md`, and R55 source/reports. R56 narrows its proposed comparison to two WAVE_FORMAT_EXTENSIBLE mono PCM16 headers differing only in channel mask: unspecified `0x0` versus front-center `0x4`. The R55 matched standard/extensible pair is a useful precedent, but its extensible header tests only mask `0x4`; it does not predict mask-zero behavior. The R55 reviewer/executor/verifier/adjudicator describe tag `0xfffe`, 40-byte `fmt `, `cbSize=22`, 16 valid/container bits, mono PCM subtype GUID, and same sample bytes as ordinary tag-1 PCM16.

The bounded history search found no earlier dedicated mask-0 versus mask-0x4 mono PCM16 pair in the inspected LOG/reports. R22 documents extensible PCM24 and PCM24 with 20 valid bits; queried ffprobe fields expose `pcm_s24le` / 24 bits, not the 20-bit valid field. R55 is positive evidence only for the tested valid-16/mask-0x4 PCM-subtype header. R53's simple float fmt warning is not an extensible-header test.

Current measurement behavior remains the existing categorical format predicate: 48 kHz, mono, `codec_name == "pcm_s16le"`, and `bits_per_sample == 16`. `measure()` obtains decoded samples via SoX and applies the existing UI numeric checks; changing a mask should not alter the encoded PCM16 sample stream, but acceptance must be measured rather than assumed. This scout did not test an integrated R56 runner mode or verifier replay.

## Original scratch comparison

Generated an original 5,760-frame / 48,000-Hz mono signed-PCM16 signal using rounded samples from `.25*sin(2*pi*1000*t)+.08*sin(2*pi*1500*t)`. Two valid RIFF files use identical 11,520-byte audio payloads. Both use tag `0xfffe`, `fmt ` payload size 40, `cbSize=22`, valid bits 16, PCM subtype GUID `00000001-0000-0010-8000-00aa00389b71`, one channel, 48,000 Hz, 96,000 byte/s, block align 2, and 16 container bits. The only header-field change is mask `0x00000000` versus `0x00000004`.

Scratch files are confined to `.shokunin/audio/corpus/live/round-56/scout/`:

- `mask0.wav`: 11,588 bytes, SHA-256 `3399ae3661b0ebd6eb4fe7c3a7cf6f4f97cd2d5ec259638164d93c810952a193`.
- `mask4.wav`: 11,588 bytes, SHA-256 `bd7d95901935c0effe21fd64e44a47487372be9d0c80f86cc725380df0352f47` (same deterministic fixture hash as the R55 extensible sample/header).

The exact metadata/header command, run from repository root (overall shell exit **0**; each ffprobe and SoX-info command printed exit **0**), was:

```sh
for f in .shokunin/audio/corpus/live/round-56/scout/mask0.wav .shokunin/audio/corpus/live/round-56/scout/mask4.wav; do echo "FILE=$f"; ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt:format=duration -of json "$f"; echo "FFPROBE_EXIT=$?"; sox --i "$f"; echo "SOX_INFO_EXIT=$?"; done
```

Both ffprobe outputs: `codec_name=pcm_s16le`, `sample_fmt=s16`, sample rate `48000`, `channels=1`, `bits_per_sample=16`, duration `0.120000`. For each, `sox --i` reported one channel, 48 kHz, 16-bit signed integer PCM, 0.12 s / 5,760 samples. These tools report the decoded audio properties; they do not report the extensible channel mask, which I verified from the constructed RIFF `fmt ` fields.

Explicit SoX-f32 decode and comparison command (shell exit **0**, `SOX_PAIR_EXIT=0`):

```sh
sox .shokunin/audio/corpus/live/round-56/scout/mask0.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-56/scout/mask0.f32 && sox .shokunin/audio/corpus/live/round-56/scout/mask4.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-56/scout/mask4.f32; echo SOX_PAIR_EXIT=$?; python3 -c 'import numpy as n; from pathlib import Path; p=Path(".shokunin/audio/corpus/live/round-56/scout"); a=n.fromfile(p/"mask0.f32",dtype="<f4"); b=n.fromfile(p/"mask4.f32",dtype="<f4"); print(len(a),len(b),n.array_equal(a,b),float(n.max(n.abs(a-b))),float(n.max(n.abs(a))),float(n.sqrt(n.mean(a.astype(n.float64)**2))))'
```

Output: `5760 5760 True 0.0 0.31536865234375 0.18559832032281998`. The vectors are exactly equal for these files and this local SoX decode path.

Direct invocation of unchanged project measurement function (exit **0**):

```sh
python3 -c 'import importlib.util; from pathlib import Path; s=importlib.util.spec_from_file_location("m",".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); p=Path(".shokunin/audio/corpus/live/round-56/scout").resolve(); [print(m.measure("ui",m.SPECS["ui"],p/f)) for f in ("mask0.wav","mask4.wav")]'
```

Both calls returned `failures: []` with matching measurements: duration `.12 s`, peak `.31536865234375`, RMS `-14.628519169868087 dBFS`, centroid `1123.322704293326 Hz`, bandwidth `276.15444981222976 Hz`, 48 kHz mono PCM16; integrated LUFS is `null`. These are direct `measure()` results, not runner receipts or fresh verifier evidence.

## Limits

Observed local ffprobe, SoX and project-measurer behavior is positive for these exact mono PCM16 extensible headers, with mask `0x0` and `0x4`; both decode equally and pass current UI checks. It does not establish other masks, multichannel/layout semantics, standards conformance generally, other valid-bit/container widths or GUIDs, arbitrary chunk layouts, decoder versions, general codec/container support, fidelity beyond the equal vectors, audibility, quality, production suitability, rights, engine behavior, publishing, or promotion. No thresholds/predicates were changed. Only this report and its own scratch files were written; no shared source, LOG, SCORECARD, canonical artifact, or other report was changed. No commit or push was made.
