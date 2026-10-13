# Round 40 scribe — endpoint decision table and evidence

## Declared rule and limits

The LOG declares one numerical calibration: the existing ambience loop endpoint comparator is strict `abs(first-last) > .03` full scale; do not alter it. At 48 kHz mono PCM16, the requested bracket is 983/32768 = **0.029998779296875** (endpoint arm should pass) versus 984/32768 = **0.030029296875** (endpoint arm should fail). The mode-level requirements also demand 2.0 s, centroid 5–200 Hz, level checks, slope mismatch <= .001, and no other failures. Counts refer to decoded PCM16 full-scale values, not audible click/seam limits.

## Before/after decision table (direct helper measurements, not runner receipts)

| Case / decision | Decoded endpoint difference | Format, duration, level, centroid, slope | Numeric outcome |
|---|---:|---|---|
| Before / 983-count `executor/loop983.wav` (SHA-256 `67e91c188809cf616701c5a3243e85b80ed9b2541e009728b8a56c8c906928bf`) | 983 counts = .029998779296875; first .05999755859375, last .089996337890625 | PCM16 mono 48 kHz, 96000 frames / 2.0 s; peak .92999267578125, RMS -3.9222346076314585 dBFS; centroid **292.7427086016555 Hz** (outside 5–200); slope mismatch .000030517578125 | Endpoint check passes, but **overall numeric fit fails** centroid band. Not an expected clean pass. |
| After / 984-count `executor/loop984.wav` (SHA-256 `ea9bb1aaebb4f66f1f7b0ff9b2498333479086f8aa1a382bde662aeee5acb962`) | 984 counts = .030029296875; first .05999755859375, last .09002685546875 | PCM16 mono 48 kHz, 96000 frames / 2.0 s; peak .930023193359375, RMS -3.9222281877179443 dBFS; centroid **292.96086648342737 Hz** (outside 5–200); slope mismatch .000030517578125 | Endpoint arm fails as expected, but overall fit has **two** failures: centroid and endpoint. Not the required sole-endpoint failure. |
| Independent `alt/edge983.wav` (SHA-256 `dc2d8591f06eae59039f15b07d80365dd713d1da1eb5bb4ad87294635aa77f12`) | 983 counts = .029998779296875; first 0, last .029998779296875 | PCM16 mono 48 kHz, 96000 frames / 2.0 s; peak .23004150390625, RMS -16.925057863412828 dBFS; centroid **823.4143890979116 Hz** (outside 5–200); slope mismatch 0 | Endpoint arm passes, overall numeric fit fails centroid band. |
| Independent `alt/edge984.wav` (SHA-256 `4c529dab929ac8236630a309454eeb2aa5b1cc1656ddea39f47d77d5c1ebbb04`) | 984 counts = .030029296875; first 0, last .030029296875 | PCM16 mono 48 kHz, 96000 frames / 2.0 s; peak .230072021484375, RMS -16.925057800832892 dBFS; centroid **824.1228156393933**? Hz (outside 5–200); slope mismatch 0 | Endpoint arm fails as expected, overall numeric fit has centroid and endpoint failures; not sole endpoint. |

The last centroid above is **824.1228156393933** as initially transcribed; see measurement output if exact final digits matter. All four files have the intended frame count, format, endpoint counts, and slope values at/below the declared limit. Neither pair demonstrates the required runner pass/fail behavior because each has an independent centroid-band miss. I did not run either opt-in runner mode, and make no runner-exit or gate receipt claim.

## Commands, setup versus fit

I ran direct one-off helper measurements, not the runner. Exact shell commands and exits:

```sh
python3 -c "import importlib.util,json; s=importlib.util.spec_from_file_location('m','.shokunin/audio/corpus/fixtures/measure_audio.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(json.dumps({n:m.measure(n,(2.0,5,200,True),'.shokunin/audio/corpus/live/round-40/executor/loop'+n+'.wav') for n in ('983','984')},indent=2))"
```
Exit 1: setup/invocation error, because `measure` requires a `Path` and `.relative_to` was called on a string. No fit result from this attempt.

```sh
python3 -c "import importlib.util,json; from pathlib import Path; s=importlib.util.spec_from_file_location('m','.shokunin/audio/corpus/fixtures/measure_audio.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(json.dumps({n:m.measure(n,(2.0,5,200,True),Path('.shokunin/audio/corpus/live/round-40/executor/loop'+n+'.wav')) for n in ('983','984')},indent=2))"
```
Exit 1: setup/path error; relative path is outside helper `ROOT` (`.shokunin/audio/corpus`). No fit result from this attempt.

```sh
python3 -c "import importlib.util,json; from pathlib import Path; s=importlib.util.spec_from_file_location('m','.shokunin/audio/corpus/fixtures/measure_audio.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(json.dumps({n:m.measure(n,(2.0,5,200,True),Path(m.ROOT/'live/round-40/executor/loop'+n+'.wav')) for n in ('983','984')},indent=2))"
```
Exit 1: setup/code error, `PosixPath + str` while constructing the path. No fit result.

```sh
python3 -c "import importlib.util,json; from pathlib import Path; s=importlib.util.spec_from_file_location('m','.shokunin/audio/corpus/fixtures/measure_audio.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(json.dumps({n:m.measure(n,(2.0,5,200,True),Path(m.ROOT)/'live/round-40/executor'/('loop'+n+'.wav')) for n in ('983','984')},indent=2))"
```
Exit 0. This produced the executor values/table above. The helper reported numeric centroid-band failures for **both** candidates; 984 additionally reported `loop seam: endpoint jump > .03 full scale`.

```sh
python3 -c "import importlib.util,json; from pathlib import Path; s=importlib.util.spec_from_file_location('m','.shokunin/audio/corpus/fixtures/measure_audio.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(json.dumps({n:m.measure(n,(2.0,5,200,True),Path(m.ROOT)/'live/round-40/alt'/('edge'+n+'.wav')) for n in ('983','984')},indent=2))"
```
Exit 0. This produced the alt values/table above. Both candidates failed the centroid band; 984 additionally failed the endpoint check.

The first three are setup/invocation errors, not numeric misses. The latter two are successful helper invocations with numeric failed fits, not runner outcomes. No source-generation command, audition, or runner command was performed by this scribe.

## Scope

No constants were changed. These are fixture-local PCM measurements only. No audition, sound-quality, production, rights, engine, publish, or promotion claim is made. No inference is made about equality exactly at .03 or an audible seam threshold.
