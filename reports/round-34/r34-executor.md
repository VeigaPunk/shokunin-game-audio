# Round 34 executor — impact third candidate

## Result
Generated an original candidate at `.shokunin/audio/corpus/live/round-34/executor/impact_third.wav` only; it is scratch, not canonical. It is 0.400 s, 48 kHz, mono, PCM16 (19,200 frames). SHA-256: `e676f1ba5431970d72e9123cb6c907a117a231176912d5164980f3d0b1f9f07d`.

The deterministic synthesis used a seeded, exponentially decaying noise transient plus decaying 720 Hz and 2100 Hz components, with a 2 ms onset ramp. The scratch-generation code ran in the Python kernel (not a shell command); it used `numpy.random.default_rng(3413)`, `.20*noise*exp(-55t) + .48*sin(2π720t)*exp(-9t) + .20*sin(2π2100t)*exp(-18t)`, multiplied by `min(t/.002, 1)`, clipped to ±.9 and rounded to PCM16. No canonical builder or source was edited.

## Direct project measurement
Used the project’s `measure_audio.measure` on both existing impact fixtures and this candidate with candidate spec `(.40, 50, 15000, False)`. Exact successful shell command and exit:

```sh
python3 - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, '.shokunin/audio/corpus/fixtures')
import measure_audio as m
root=Path('.shokunin/audio/corpus').resolve()
for name,rel,spec in [('impact','artifacts/impact.wav',m.SPECS['impact']),('impact_alt','artifacts/impact_alt.wav',m.SPECS['impact_alt']),('candidate','live/round-34/executor/impact_third.wav',(.4,50,15000,False))]:
 print(name, m.measure(name,spec,root/rel))
PY
```
Exit: **0**.

| File | Measured duration | Rate/channels/encoding | Peak FS | RMS dBFS | Centroid Hz | Ordinary failures |
|---|---:|---|---:|---:|---:|---|
| impact | .32 s | 48000 / mono / PCM16 | .8087768555 | -20.40218668 | 10843.127203 | none |
| impact_alt | .32 s | 48000 / mono / PCM16 | .7561645508 | -17.32957041 | 473.791536 | none |
| candidate | .40 s | 48000 / mono / PCM16 | .8911743164 | -17.48928519 | 9216.903937 | none |

Candidate centroid relative difference is `abs(candidate-base)/base = 0.1499773299` (about 15.00%) against `impact`, and `abs(candidate-alt)/alt = 18.4535006281` (about 1845.35%) against `impact_alt`. Both exceed the requested >=.10 numeric criterion. Duration is also .08 s from each baseline, exceeding .020 s. This reports numeric fixture measurements only; it does not establish perceived distinctness or sound quality.

## Failed setup attempts (not evidence)
1. First direct-measure helper passed path strings to `measure()`, which expects `Path` objects. Exact shell command:

```sh
python3 - <<'PY'
import sys
sys.path.insert(0, '.shokunin/audio/corpus/fixtures')
import measure_audio as m
for name,path in [('impact', '.shokunin/audio/corpus/artifacts/impact.wav'), ('impact_alt', '.shokunin/audio/corpus/artifacts/impact_alt.wav'), ('candidate', '.shokunin/audio/corpus/live/round-34/executor/impact_third.wav')]:
 spec=(.4,50,15000,False) if name=='candidate' else m.SPECS[name]
 r=m.measure(name,spec,path)
 print(name, r)
PY
```
Exit: **1**, `AttributeError: 'str' object has no attribute 'relative_to'`. Setup/type error; no measurement result counted.
2. Retried using relative `Path`s, but `measure()` requires paths relative to the resolved corpus root. Exact command:

```sh
python3 - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, '.shokunin/audio/corpus/fixtures')
import measure_audio as m
for name,path in [('impact', Path('.shokunin/audio/corpus/artifacts/impact.wav')), ('impact_alt', Path('.shokunin/audio/corpus/artifacts/impact_alt.wav')), ('candidate', Path('.shokunin/audio/corpus/live/round-34/executor/impact_third.wav'))]:
 spec=(.4,50,15000,False) if name=='candidate' else m.SPECS[name]
 print(name, m.measure(name,spec,path))
PY
```
Exit: **1**, `ValueError` because the relative paths are not under `ROOT`. Setup/path error; no measurement result counted.

The successful call uses resolved paths under `ROOT`. No runner integration, independent verification, canonical promotion, or quality/production/rights/engine/publish claim is made here.
