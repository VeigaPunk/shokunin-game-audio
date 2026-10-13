# R58 independent alternate — extensible PCM valid-bits pair

## Construction and direct header inspection

Independently generated a fresh 5,760-frame (0.120 s), mono 48,000 Hz UI-shaped signed PCM16 pair in `.shokunin/audio/corpus/live/round-58/alt/`. Both have the same 11,520-byte audio payload, with every signed sample divisible by four (14-bit left-aligned values). The sole header difference is `wValidBitsPerSample`: 14 versus 16. Payload samples came from rounded `8191*(.22*sin(2π·887t)+.10*sin(2π·1901t))`, multiplied by four.

Exact generation command and exit:

```sh
python3 ".shokunin/audio/corpus/live/round-58/alt/generate_pair.py"
# exit 0
```

| File | Bytes | WAV SHA-256 |
|---|---:|---|
| `valid14.wav` | 11,588 | `c56dd1946015796b3d96e2b699899682a773a6e3daa4084b5b16cde81ebd1a89` |
| `valid16.wav` | 11,588 | `2bc6d22183197478bf56d36ed7bf7fd715d1e6932a5a59d253f79083432cbee1` |

Generator output also recorded payload length 11,520, payload SHA-256 `501477dbee28e2f9380a8d5027b379020d7e87801946657079399a06310443f5`, signed sample range `-10484..10484`, and `all_div4=True`.

Direct RIFF header inspection command (exit **0**):

```sh
python3 ".shokunin/audio/corpus/live/round-58/alt/inspect_headers.py"
```

Actual output for both: RIFF/WAVE, `fmt` size 40, tag `0xfffe`, mono, 48,000 Hz, block align 2, container bits 16, `cbSize=22`, mask `0x4`, PCM subtype GUID `0100000000001000800000aa00389b71`, 11,520 data bytes. `valid14.wav` declares 14 valid bits; `valid16.wav` declares 16. Thus container width is 16 for both and the valid-bits field is the only intended header change.

## ffprobe, SoX decode, and unchanged project UI gate

Exact ffprobe command (loop and both invocations exited **0**):

```sh
for f in .shokunin/audio/corpus/live/round-58/alt/valid{14,16}.wav; do echo "=== $f"; ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt:format=duration -of json "$f"; echo "ffprobe_exit=$?"; done
```

For each file ffprobe returned `codec_name=pcm_s16le`, `sample_fmt=s16`, `sample_rate=48000`, `channels=1`, `bits_per_sample=16`, duration `0.120000`. These describe decoded/container PCM here; valid bits were read directly from the RIFF header above.

Each SoX decode command exited **0**:

```sh
sox ".shokunin/audio/corpus/live/round-58/alt/valid14.wav" -t f32 -e floating-point ".shokunin/audio/corpus/live/round-58/alt/valid14.f32"
sox ".shokunin/audio/corpus/live/round-58/alt/valid16.wav" -t f32 -e floating-point ".shokunin/audio/corpus/live/round-58/alt/valid16.f32"
```

Exact comparison command (exit **0**):

```sh
python3 ".shokunin/audio/corpus/live/round-58/alt/compare_decode.py"
```

Both decoded vectors contain 5,760 float32 samples, SHA-256 `8a8d20cfa2ab30a4dbe3415e78363c63cd1ba90374318e23e6232f0eb79fa470`, range `[-0.3199462890625, 0.3199462890625]`. Arrays compare equal: `equal True`, maximum absolute difference `0.0`, different samples `0`. This is only the observed SoX result for this specific left-aligned matched payload.

Exact unchanged project `measure_audio.py` UI measurement command (exit **0**):

```sh
python3 -c 'import importlib.util; from pathlib import Path; s=importlib.util.spec_from_file_location("m", ".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); p=Path(".shokunin/audio/corpus/live/round-58/alt").resolve(); [print(m.measure("ui",m.SPECS["ui"],p/f)) for f in ("valid14.wav","valid16.wav")]'
```

Both direct project measurements decoded 5,760 samples and reported duration `.12 s`, 48,000 Hz mono, `pcm_s16le`/16-bit, peak `0.3199462890625`, RMS `-15.349264723890549 dBFS`, centroid `2090.91125087851 Hz`, bandwidth `3562.6781107930465 Hz`, LUFS `null`, and `failures: []`. Both pass the unchanged project UI format/numeric checks when measured directly.

## Receipt/setup distinction and limits

This alternate built original scratch WAVs and ran ffprobe, SoX, and the direct project measurement function. It did **not** invoke the integrated runner modes, produce runner receipts, or perform the named non-author replay. No runner command was attempted, so there is no runner receipt or receiptless runner failure to count. One malformed shell quoting attempt while preparing an inspection command failed at Python parse time (no command was run and no fixture/receipt was produced); corrected header inspection above exited 0. It is setup only, not a decode or gate failure.

Evidence is limited to these two 16-bit-container, 14/16-valid-bit mono PCM files, the specified all-divisible-by-four payload, and the observed local ffprobe/SoX/project path. It does not establish general valid-bit enforcement/semantics, other valid-bit/container combinations, arbitrary payload alignment, decoder portability, WAVE extensible conformance, fidelity, audibility/quality, production suitability, rights, engine behavior, or publishing. Scratch scripts and files are confined to `.shokunin/audio/corpus/live/round-58/alt/`; this report is the only report written. No shared source, LOG, SCORECARD, canonical artifact, or other report was changed; no commit or push was made.
