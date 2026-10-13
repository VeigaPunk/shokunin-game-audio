# R50 scribe — measured gate decision (integrated runner pending)

## Current evidence and decision

The round-50 scratch WAV pair is present under `corpus/live/round-50/executor/`. I applied the existing project `measure("ui", SPECS["ui"], path)` directly to each file. This is an observed project-measurement result, **not** an integrated runner receipt: the declared opt-in runner modes/replay and their exit statuses are pending. The unchanged ordinary UI gate outcome is nevertheless clear for this pair:

| Scratch file | SHA-256 (WAV) | ffprobe stream / duration | SoX f32 decoded scalar samples | Project peak / RMS / whole-wave centroid | UI gate outcome |
|---|---|---|---:|---|---|
| `live/round-50/executor/mono.wav` | `93223ee4df8c027d6efaa12d9eca47af3de4fba1eba90c27f29c49ab0086a54a` | 48000 Hz, 1 channel, `pcm_s16le`, 16 bit; 0.120000 s | 5760 | 0.3160400390625 / -19.902100515581505 dBFS / 1928.2134621890698 Hz | No failures; predicted control pass |
| `live/round-50/executor/stereo.wav` | `59e508f1b30d17eef5f00951434915bc7974e02d6988faf07a557270611e950e` | 48000 Hz, 2 channels, `pcm_s16le`, 16 bit; 0.120000 s | 11520 | 0.3160400390625 / -19.902100515581505 dBFS / 2019.8445020922231 Hz | Sole failure: `format: expected 48kHz mono`; predicted exit 1 |

Both fit the UI duration (0.12 s ± 0.001), level (peak < .95; RMS >= .001), and whole-wave centroid (250–4000 Hz) checks using the project's SoX-decoded stream. The stereo SoX decode contained 11520 scalar samples versus 5760 for mono; the table reports the helper's actual whole-wave measurement, not per-channel analysis. The existing predicate requires exactly 48000 Hz and one channel, so stereo fails its format check; PCM16 is satisfied on both. This is evidence for this specific measured pair, not channel-agnostic stereo handling or a general statement about stereo/downmix behavior.

## Commands and exits

The metadata command used for each file (both ffprobe invocations exited **0**):

```sh
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json "$f"
```

The SoX decode/metrics command was run for each file as part of this shell pipeline (both pipelines exited **0**):

```sh
sox "$f" -t f32 -e floating-point - | python -c 'import sys,numpy as np; x=np.frombuffer(sys.stdin.buffer.read(),dtype="<f4").astype(np.float64); s=np.abs(np.fft.rfft(x)); r=np.fft.rfftfreq(len(x),1/48000); print("decoded_samples",len(x),"peak",np.max(np.abs(x)),"rms_dbfs",20*np.log10(np.sqrt(np.mean(x*x))),"centroid_hz",np.dot(r,s)/s.sum())'
```

The exact project UI measurement command (exit **0**, printing both measurement rows and their failure lists) was:

```sh
python -c "import importlib.util,json; from pathlib import Path; p=Path('.shokunin/audio/corpus/fixtures/measure_audio.py'); s=importlib.util.spec_from_file_location('m',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); base=Path('.shokunin/audio/corpus/live/round-50/executor').resolve(); print(json.dumps({k:m.measure('ui',m.SPECS['ui'],base/(n+'.wav')) for k,n in [('mono','mono'),('stereo','stereo')]},indent=2))"
```

The scratch WAVs' SHA values are above. The integrated runner is not yet wired to these paths/modes, so there is no integrated command/exit or receipt to transcribe here. Do not treat the direct measurement process exit 0 as the gate's exit: its returned `failures` are empty for mono and contain the single format failure for stereo.

## Setup, numeric fits, and transcription

A few attempts to invoke the direct-measure helper failed during setup only: an initial shell-quoting typo was rejected before a command ran; a misspelled helper path produced `FileNotFoundError` (exit 1); and a relative scratch path raised `ValueError` because it was outside the helper's resolved corpus root (exit 1). I corrected the path and used absolute-resolved scratch paths. These are setup errors, not gate results. The measured pair had **no failed numeric UI fits**. No integrated runner transcription has yet been made; integrated mode exits/receipts remain pending.

No audition or claims about audio quality, perception, production, rights, engine behavior, publishing, or promotion are made.
