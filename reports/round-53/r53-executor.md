# Round 53 executor — float32/PCM16 matched UI-shaped pair

## Construction and artifacts

Read the R53 declaration in `.shokunin/audio/LOG.md`. Generated an original 5760-frame, mono, 48000 Hz signed PCM16 fixture and IEEE float32 WAV fixture. Signal is a 1 kHz plus 1.5 kHz two-sine waveform; signed16 samples are rounded integer values and float32 samples are exactly `signed16 / 32768`. Both are 0.120 s. Scratch artifacts are confined to `.shokunin/audio/corpus/live/round-53/executor/`.

Generation command (exit 0):

```sh
python3 .shokunin/audio/corpus/live/round-53/executor/generate.py
```

WAV SHA-256: float32 `1a1d9ec23e0a9cc7fdd62f1bfb30c51260b6847c879467317783d744c774deef` (23084 bytes); PCM16 `2d201f849ecb416401b15c88e172527f9beec852c8998123f5f06131c712fee0` (11564 bytes).

## Actual probe and project gate results

Command (exit 0):

```sh
for f in .shokunin/audio/corpus/live/round-53/executor/*.wav; do ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json "$f"; done
```

Actual metadata: float fixture `pcm_f32le`, 32 bits, 48000 Hz, mono, duration `0.120000`; PCM16 fixture `pcm_s16le`, 16 bits, 48000 Hz, mono, duration `0.120000`.

The project measurement command exited 0:

```sh
python3 .shokunin/audio/corpus/live/round-53/executor/measure.py
```

It invokes unchanged `measure(path, SPECS["ui"], path)` from `.shokunin/audio/corpus/fixtures/measure_audio.py`. Both project SoX-f32 decoded measurements: 5760 samples, duration `0.12 s`, peak `0.315399169921875`, RMS `-14.628083420045229 dBFS`, spectral centroid `1123.8154138173777 Hz`, bandwidth `292.5430341707052 Hz`, integrated LUFS `null`. Both pass numeric UI gates (duration ±1 ms, peak <.95, RMS >=.001, centroid 250–4000 Hz), and both are mono 48 kHz. Float32 failure list is exactly [`format: expected PCM16`]; PCM16 failure list is `[]`.

Explicit decoder commands (both exit 0):

```sh
sox .shokunin/audio/corpus/live/round-53/executor/float32.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-53/executor/float32-decoded.f32
sox .shokunin/audio/corpus/live/round-53/executor/pcm16.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-53/executor/pcm16-decoded.f32
```

SoX emitted `WARN wav: wave header missing extended part of fmt chunk` for the float fixture but returned 0 and decoded it. Comparison command (exit 0):

```sh
python3 -c 'import numpy as n; from pathlib import Path; p=Path(".shokunin/audio/corpus/live/round-53/executor"); a=n.fromfile(p/"float32-decoded.f32",dtype="<f4"); b=n.fromfile(p/"pcm16-decoded.f32",dtype="<f4"); print(len(a),len(b),n.array_equal(a,b),float(n.max(n.abs(a-b))),float(n.max(n.abs(a))),float(n.sqrt(n.mean(a.astype(n.float64)**2))))'
```

Output: `5760 5760 True 0.0 0.315399169921875 0.18560763156982443`. Thus decoded float32/PCM16 sample vectors are exactly equal for this construction.

## Setup event and limits

An initial measurement-wrapper attempt (before resolving the scratch path) exited 1 with `ValueError: ... is not in the subpath .../.shokunin/audio/corpus`; the wrapper passed a relative path where the project measurer expects a corpus-root path. I corrected the wrapper to resolve the scratch directory and reran successfully. This was setup only, not a gate failure or numeric fit. The float WAV is a simple IEEE-float `fmt` chunk; ffprobe and SoX identify/decode it, with the warning recorded above. Evidence tests only this matched pair and the existing format predicate: it does not establish general float acceptance/conversion, higher dynamic range, fidelity, audibility, quality, production, rights, engine behavior, or promotion. No source, LOG, scorecard, canonical artifact, or other report was changed.
