# Round 40 outer-endpoint pair — executor

## Result

Generated two original deterministic 2.000 s, 96,000-frame, 48 kHz mono PCM16 loop scratch WAVs in `.shokunin/audio/corpus/live/round-40/executor/`:

| File | SHA-256 | decoded first → last PCM16 | endpoint delta | project `measure()` result |
|---|---|---:|---:|---|
| `loop983.wav` | `2f7dd5517ff2cfe380cc6710e6ac99d0939d95dece81d0cdedaddcee95b20286` | 24,248 → 25,231 (983 counts) | 0.029998779296875 FS | pass, no failures |
| `loop984.wav` | `c5ca108680557a584cca19dead3a900a382ed8dfa1252ab994196624c0eb94c6` | 24,248 → 25,232 (984 counts) | 0.030029296875 FS | fails only `loop seam: endpoint jump > .03 full scale` |

**Correction:** the first version of this report misstated the decoded first/last counts as 25,165 → 26,148/26,149. Decoding both SHA-pinned stable WAVs and reproducing them from the recipe below confirms the corrected counts above; the WAV bytes and hashes were not changed.

Exact generation recipe (run from the repository root) for each `k` in `(983, 984)`:

```python
N = 96000
n = np.arange(N)
t = n / 48000
base = 0.7 + 0.04 * np.cos(2 * np.pi * 30 * t)
target = k / 32768
correction = target - (base[-1] - base[0])
samples = base + np.linspace(0, correction, N)  # includes both endpoints
pcm = np.rint(samples * 32768).astype(np.int16)
# No post-quantization sample edits.
with wave.open(str(out / f"loop{k}.wav"), "wb") as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(48000)
    wav.writeframes(pcm.astype("<i2").tobytes())
```

This yields first/last signed PCM16 counts 24248→25231 for `k=983` and 24248→25232 for `k=984`, with the SHA-256 values in the table. The gradual correction keeps the outer side-slope comparison small while isolating the endpoint comparator. Exact decoded measurements from `measure()`:

| measurement | 983 | 984 |
|---|---:|---:|
| duration | 2.0 s | 2.0 s |
| format | 48,000 Hz, mono, `pcm_s16le`, 16 bit | same |
| peak | 0.769989013671875 FS | 0.77001953125 FS |
| RMS | -2.9064579145372624 dBFS | -2.9062715288071326 dBFS |
| integrated LUFS | -37.5 | -37.5 |
| centroid | 170.56815710368392 Hz | 170.73676058919554 Hz |
| bandwidth | 1471.8827036884138 Hz | 1472.627122425995 Hz |
| outer endpoint delta | 0.029998779296875 FS | 0.030029296875 FS |
| outer slope mismatch | 0.0 FS/sample | 0.0 FS/sample |
| failures | `[]` | `['loop seam: endpoint jump > .03 full scale']` |

The pair brackets the existing strict `> .03` rule using decoded PCM16 values; it does not establish behavior at exactly .03 or an audible threshold.

## Commands and execution telemetry

The project helper was called through this exact command (exit **0**):

```sh
python3 -c 'import importlib.util,json; from pathlib import Path; s=importlib.util.spec_from_file_location("m",".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(json.dumps([m.measure("loop983",(2.0,5,200,True),m.ROOT/"live/round-40/executor/loop983.wav"),m.measure("loop984",(2.0,5,200,True),m.ROOT/"live/round-40/executor/loop984.wav")],indent=2))'
```

Earlier helper invocations were setup errors, not fit outcomes: the same command with string paths exited **1** (`AttributeError: 'str' object has no attribute 'relative_to'`); with a relative path outside `m.ROOT` exited **1** (`ValueError: ... is not in the subpath ...`); with a relative path under `m.ROOT` but process cwd at repository root, it exited **1** because ffprobe could not find the file. Passing the absolute project-root-relative `Path` fixed the helper setup.

Numerical candidate fits were also attempted before this final pair. These were failed fits, not project-gate runs: a 160 Hz cosine initially produced a centroid around 1362 Hz (outside the ambience band); 30 Hz candidates at amplitudes .012, .2, .4, .7 and .85 produced centroids respectively around 1347, 806, 519, 344 and 297 Hz (outside band); further low-frequency cosine/sweep candidates remained above 200 Hz. A DC-offset 30 Hz candidate at .9 also failed the level/headroom check. A .7 DC offset with .04-amplitude 30 Hz component yielded the selected clean pair. These exploratory values are not retained as gate evidence.

No audition or claims about sound quality, production, rights, engine behavior, publishing, or promotion are made. This is numeric fixture calibration only.
