# R41 executor — outer slope pair

Scope: original source-generated numeric fixtures only. No listening or inference about audible smoothness, sound quality, production, rights, engine behavior, publishing, or promotion.

## Recipe and files

Generated two distinct 2.0 s / 96,000-frame, 48 kHz mono PCM16 WAVs, using Python `wave` and NumPy. Starting source was `x[n] = rint(0.15 * sin(2*pi*120*n/96000) * 32768)` for `n=0..95999`; then set `x[1]=6` for the 32-count fixture and `x[1]=5` for the 33-count fixture. Samples were written little-endian signed 16-bit PCM. This single sample adjustment sets the absolute difference between the two outer side slopes to the intended integer count while leaving endpoints fixed.

- `.shokunin/audio/corpus/live/round-41/executor/slope-32.wav` SHA-256 `0bc9c6f07b53b13336b253db069cc57702e9520634106eabf85fc27e329b4547`
- `.shokunin/audio/corpus/live/round-41/executor/slope-33.wav` SHA-256 `b86a34d343a57e943ab4289cb67b992b8597d93002f3b4a7ef9981e6b30952fb`

## Direct project-helper measurements

Called `measure()` from `.shokunin/audio/corpus/fixtures/measure_audio.py` directly with `(2.0, 5, 200, True)` on each WAV. Both decode as 96,000 samples. For 32: endpoint delta `39/32768 = 0.001190185546875`; outer slope mismatch `32/32768 = 0.0009765625` (pass); centroid `150.16139474032187 Hz`; peak `0.149993896484375`; RMS `-19.48848493684799 dBFS`; failures `[]`. For 33: endpoint delta `39/32768 = 0.001190185546875`; outer slope mismatch `33/32768 = 0.001007080078125` (fail); centroid `152.54369633957694 Hz`; peak `0.149993896484375`; RMS `-19.488484936889183 dBFS`; sole failure `loop seam: slope mismatch > .001 full scale per sample`. Format, duration, level and 5–200 Hz centroid checks pass for both. This is the requested local numerical bracket, not an assertion at exact equality (`.001*32768` is not an integer).

## Commands and exits

`python3 -c 'import runpy,pathlib,json; m=runpy.run_path(".shokunin/audio/corpus/fixtures/measure_audio.py"); root=pathlib.Path(".shokunin/audio/corpus"); print(json.dumps({str(p):m["measure"](p.stem,(2.0,5,200,True),p) for p in sorted((root/"live/round-41/executor").glob("*.wav"))},indent=2))'` — exit **1**, setup/path mistake: relative paths were passed where helper expects paths beneath its absolute `ROOT`; no numeric receipt. Corrected:

`python3 -c 'import runpy,pathlib,json; m=runpy.run_path(".shokunin/audio/corpus/fixtures/measure_audio.py"); root=pathlib.Path(".shokunin/audio/corpus").resolve(); print(json.dumps({p.name:m["measure"](p.stem,(2.0,5,200,True),p) for p in sorted((root/"live/round-41/executor").glob("*.wav"))},indent=2))'` — exit **0**, direct helper output above.

`python3 -c 'import subprocess, pathlib, numpy as np, json; base=pathlib.Path(".shokunin/audio/corpus/live/round-41/executor"); print(json.dumps({p.name:len(np.frombuffer(subprocess.run(["sox",str(p.resolve()),"-t","s16","-e","signed-integer","-"],check=True,capture_output=True).stdout,dtype="<i2")) for p in sorted(base.glob("*.wav"))},indent=2))'` — exit **0**, decoded sample counts `slope-32.wav: 96000`, `slope-33.wav: 96000`.

Two earlier numerical fits were rejected, not setup errors: initial `x[1]+=32/33` yielded slope deltas `.001007080078125` / `.00103759765625` (both failed); replacing x[1] with 38/39 samples yielded `0` / `.000030517578125`, wrong target counts. Final files above are regenerated with exact x[1]=6/5.
