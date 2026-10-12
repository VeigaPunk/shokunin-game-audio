# Round 18 executor — 200 Hz +8-count candidate

## Scope and construction

Built the requested scratch candidate from canonical `corpus/artifacts/stem_layer_third.wav`, not by resynthesizing: copied its PCM16 mono sample array and increased only zero-based frame 96001 by 8 counts. Canonical local samples at frames 95998–96001 were `[-26,-13,0,43]`; candidate is `[-26,-13,0,51]`. This is a scratch candidate, not a canonical fixture or a runner mode. No source, LOG, SCORECARD, canonical WAV, or commit was changed.

Exact Python construction used in the persistent REPL:
```python
p = Path(".shokunin/audio/corpus/artifacts/stem_layer_third.wav")
data = p.read_bytes()
a = np.frombuffer(data[44:], dtype="<i2").copy()
a[96001] += 8
with wave.open(".shokunin/audio/corpus/live/round-18/slope200_candidate.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(48000)
    w.writeframes(a.astype("<i2").tobytes())
```
Construction completed without error. Candidate: `.shokunin/audio/corpus/live/round-18/slope200_candidate.wav`, 384044 bytes, SHA-256 `e7c98cc5af858d8dab2be01a4f76382e06008573a017909c2760e68a585b1881`.

## Direct decode and checks

`ffprobe -v error -show_entries stream=sample_rate,channels,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-18/slope200_candidate.wav` — exit 0; decoded metadata is PCM16, 48000 Hz, mono, 4.000000 s. `sox .shokunin/audio/corpus/live/round-18/slope200_candidate.wav -t f32 -e floating-point - | wc -c` — exit 0; 768000 output bytes = 192000 float32 samples. `sha256sum .shokunin/audio/corpus/live/round-18/slope200_candidate.wav` — exit 0; hash above.

Decoded signed PCM counts and normalization were independently calculated from the WAV data (`count / 32768`). Full-wave results: peak `0.04998779296875` FS; RMS `0.026099826390242643` FS (`-31.66724762948755 dBFS` via fixture helper); centroid `303.8188333213146 Hz`. Generic 4 s / 48 kHz mono / peak / RMS / 100–2000 Hz centroid checks pass. Outer endpoint delta is `0.001312255859375` FS; outer slope mismatch is `0.00091552734375` FS/sample, under `.001`.

Direct 200 Hz section checks on the decoded samples: component amplitudes `[0.014999984892417233, 0.04999803919712925]` FS; section RMS `[0.0106065941723389, 0.03535395360161179]` FS; signed second-to-first contrast `+10.457243020771665 dB` (passes >=6 dB). At the internal join, adjacent gap is `0.000396728515625` FS (passes <=.03); side-slope mismatch is `0.00115966796875` FS/sample (**fails** unchanged strict `.001` limit by `0.00015966796875`). Thus the +8-count hypothesis crosses the intended existing internal-side-slope failure gate. The value exceeds the strict `.001` threshold by `0.00015966796875` FS/sample; this is the measured failure margin, not evidence of an upper-bound overshoot or candidate disqualification. All other directly measured gates above pass, so direct arithmetic predicts this is a sole-slope negative probe, pending integrated runner verification.

The existing helper was run for full-wave metrics and 200 Hz section calculation:
```sh
python3 -c 'import sys,pathlib; sys.path.insert(0,".shokunin/audio/corpus/fixtures"); import measure_audio as m; p=pathlib.Path(".shokunin/audio/corpus/live/round-18/slope200_candidate.wav").resolve(); print(m.measure("slope200_candidate",(4.0,100,2000,True),p)); print(m.section_contrast(p,200))'
```
Exit **0**. Its `measure()` failure list is empty because this helper's `measure()` does not include the additional 200 Hz internal-join slope check; the separately reported section helper says contrast passes but does not itself apply the internal slope limit. Applying the runner's existing internal-side-slope condition to the direct value above yields the failure. This was not a runner replay and should not be described as one.

## Failed setup/measurement attempts (not audio fits)

- An initial inline helper call passed the WAV path as a string; it exited **1** with `AttributeError: 'str' object has no attribute 'relative_to'`.
- Retrying with a relative `Path` exited **1** because the helper requires an absolute path under its corpus root (`ValueError: ... is not in the subpath .../corpus`).
- Retrying with an absolute path succeeded (command and exit 0 above). These are setup/API invocation mistakes, not candidate audio failures or passing checks.
- No alternate +N fit was attempted. The only measured candidate is the exact requested +8 count and it fails the internal side-slope bound as stated; no threshold was changed.

No claim is made about sound, audibility, musical quality, production behavior, or an engine. No source edits or canonical changes were made.
