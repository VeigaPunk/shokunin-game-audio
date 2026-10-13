# R41 independent alternate outer-slope fixture pair

## Scope and result

Independent original candidate pair for the declared 32/33 decoded PCM16 count outer side-slope bracket. Files are scratch only, not canonical fixtures. The final pair hits the specified adjacent grid points and retains the ordinary project measurement checks. This is numerical fixture calibration only; it is not an audition or a sound-quality, production, rights, engine, publishing, or promotion result. Counts 32/33 do not test equality at `.001` (32.768 counts).

## Recipe and hashes

Scratch files: `.shokunin/audio/corpus/live/round-41/alt/slope-32.wav` and `slope-33.wav`.

Generated directly with Python `wave`, mono PCM16 little-endian, 48,000 Hz, 96,000 frames (2.0 s). Start from `round(rint((0.78 + .08*sin(2*pi*37*t) + .03*sin(2*pi*83*t))*32768))` for `t = arange(96000)/48000`; set decoded integer samples `[0]` and `[1]` to 25,000, `[-2]` to 25,000, and `[-1]` to 25,000+n, where n is 32 or 33; clip to int16 and write. This is a synthetic offset waveform selected for measured fixture bounds, not a playable sound-design claim.

- slope-32 SHA-256: `e23036abb2e3585eb18f9debec2c12f0b330d3e2d815dd36004ebda07b6780c1`
- slope-33 SHA-256: `69db5b901f1657c7c9f6f93dc0d2304b7ec1405d01c9a394a8b0f8753d5fe3bc`

## Project-helper measurements

Measured by the project `measure_audio.measure` helper with spec `(2.0, 5, 200, True)`. Both: 2.0 s; 48 kHz mono PCM16; peak 0.88995361328125; RMS -2.13214 dBFS; centroid within 5–200 Hz; endpoint delta <= .03; all ordinary checks pass.

| n | Decoded outer side-slope mismatch | Endpoint delta | Centroid | Helper result |
|---|---:|---:|---:|---|
| 32 | 32/32768 = 0.0009765625 | 0.0009765625 | 117.2780890394 Hz | no failures (pass) |
| 33 | 33/32768 = 0.001007080078125 | 0.001007080078125 | 117.2980483104 Hz | sole failure: `loop seam: slope mismatch > .001 full scale per sample` |

The pair isolates the outer slope comparator at neighboring PCM16 increments: changing only the final sample from baseline by 32 to 33 counts makes the declared comparator fail. Endpoint check passes in both. This is not the internal R21 section join nor the R40 endpoint-fail fixture.

## Commands and failures

Exact project-helper command (shell exit 0):

```sh
python3 -c "import importlib.util,json; from pathlib import Path; s=importlib.util.spec_from_file_location('measure_audio','.shokunin/audio/corpus/fixtures/measure_audio.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(json.dumps([m.measure('x',(2.0,5,200,True),Path('.shokunin/audio/corpus/live/round-41/alt/slope-%d.wav'%n).resolve()) for n in (32,33)],indent=2))"
```

Two exploratory helper invocations failed as **setup/path errors**, not measurement failures: the first passed `str` where the helper requires `Path` (exit 1, `AttributeError: 'str' object has no attribute 'relative_to'`); the second used a relative `Path` and `relative_to(ROOT)` failed (exit 1, `ValueError: ... is not in the subpath ...`). The corrected absolute-path command above exited 0.

A first waveform recipe (DC 0.32, components .055 at 37 Hz and .025 at 83 Hz, same boundary construction) was a **numeric failed fit**, not setup: helper exit 0 while both fixtures failed only `spectrum: centroid outside fixture band` (centroids 2801.8438588548047 and 2801.814634859037 Hz). Those files were overwritten by the final recipe; their hashes are not presented as candidate fixtures.
