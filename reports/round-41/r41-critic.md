# R41 critic — independent falsification

## Scope and verdict

I read the R41 declaration in `.shokunin/audio/LOG.md`: this is the **outer loop side-slope** check, `abs((last - penultimate) - (second - first)) > .001`, separate from the R21 internal join and R40 endpoint check. I inspected the stable SHA-pinned executor and alternate scratch WAVs under `corpus/live/round-41/`; I did not audition them. This review supports the narrow numerical pass/fail bracket, not any broader sonic claim. It is not an exact-equality test: `.001 * 32768 = 32.768`, not an integer PCM16 count.

## Stable candidate evidence

Independent SoX decode of the four checked-in candidate files confirms 96,000 PCM16 samples each and these raw boundary samples / slope mismatches:

| Candidate | SHA-256 | first, second, penultimate, last decoded counts | slope mismatch |
|---|---|---|---:|
| executor 32 | `0bc9c6f07b53b13336b253db069cc57702e9520634106eabf85fc27e329b4547` | `0, 6, -77, -39` | 32 counts |
| executor 33 | `b86a34d343a57e943ab4289cb67b992b8597d93002f3b4a7ef9981e6b30952fb` | `0, 5, -77, -39` | 33 counts |
| alt 32 | `e23036abb2e3585eb18f9debec2c12f0b330d3e2d815dd36004ebda07b6780c1` | `25000, 25000, 25000, 25032` | 32 counts |
| alt 33 | `69db5b901f1657c7c9f6f93dc0d2304b7ec1405d01c9a394a8b0f8753d5fe3bc` | `25000, 25000, 25000, 25033` | 33 counts |

Thus the decoded values are exactly `32/32768 = 0.0009765625` (below threshold) and `33/32768 = 0.001007080078125` (above). The executor changes the second sample between its pair; the alternate changes the last sample. Neither is literally a one-variable waveform identity test across all metrics. The relevant comparator outcomes are isolated: both 32 files pass and both 33 files fail **only** the slope comparator, while endpoint deltas stay below `.03` and ordinary checks pass. The pairs use separate waveforms and SHA values; neither reuses the R21 join or R40 endpoint-fail fixture.

The project helper independently measured executor 32 as 2.0 s, 48 kHz mono PCM16, peak `0.149993896484375`, RMS `-19.48848493684799 dBFS`, centroid `150.16139474032187 Hz`, endpoint delta `0.001190185546875`, slope `0.0009765625`, no failures. Executor 33 had the same format/peak, RMS `-19.488484936889183 dBFS`, centroid `152.54369633957694 Hz`, endpoint delta `0.001190185546875`, slope `0.001007080078125`, and sole failure `loop seam: slope mismatch > .001 full scale per sample`.

The alternate helper results: both 2.0 s / 48 kHz mono PCM16, peak `0.88995361328125`, RMS about `-2.13214 dBFS`; centroids `117.27808903942851` and `117.29804831044468 Hz`; endpoint deltas respectively `.0009765625` and `.001007080078125`; slope deltas equal those respective 32/33-count values. The 32 candidate has no failures; the 33 candidate has only `loop seam: slope mismatch > .001 full scale per sample`.

Endpoint delta changes with the alternate's last-sample mutation but stays far inside `.03` in both cases; it cannot account for the 33-only failure. Centroids differ slightly within 5–200 Hz, and peak/headroom is below `.95` for both pairs. They do not trigger centroid or level failures. The headroom differs substantially between independently authored pairs, but that is not a confound of the slope comparison: in each pair the pass/fail result tracks the decoded slope count while all ordinary limit checks pass. This says nothing about audible smoothness or quality.

## Exact commands / exits and error classification

Decoded-count/SHA command run by this critic (exit **0**):

```sh
python3 -c "import wave,hashlib,numpy as np,pathlib; root=pathlib.Path('.shokunin/audio/corpus/live/round-41'); [(lambda b,w,y: print(str(p), 'sha256='+hashlib.sha256(b).hexdigest(), 'frames='+str(len(y)), 'outer='+str((int(y[0]),int(y[1]),int(y[-2]),int(y[-1]))), 'slope_counts='+str(abs((int(y[-1])-int(y[-2]))-(int(y[1])-int(y[0]))))))(p.read_bytes(), wave.open(str(p),'rb'), np.frombuffer(wave.open(str(p),'rb').readframes(96000),dtype='<i2')) for p in sorted(root.rglob('slope-*.wav'))]"
```

Project helper command run by this critic (exit **0**):

```sh
python3 -c "import importlib.util,json; from pathlib import Path; s=importlib.util.spec_from_file_location('measure_audio','.shokunin/audio/corpus/fixtures/measure_audio.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(json.dumps([m.measure('x',(2.0,5,200,True),Path('.shokunin/audio/corpus/live/round-41/alt/slope-%d.wav'%n).resolve()) for n in (32,33)],indent=2))"
```

The alternate author reports earlier helper failures from a `str` instead of `Path` and a relative path failing `relative_to(ROOT)`; both are setup/path errors, not numeric failures, and corrected absolute-path helper run exited 0. The alternate also reports an earlier waveform recipe with centroid `2801.84/2801.81 Hz`, outside the band: numeric failed fit, not setup. Executor reports an initial sample adjustment with slope results `.001007080078125/.00103759765625` (both wrong/failing fits), then a 0/1-count result; these are numeric failed fits. Its first relative-path helper command exited 1 as a setup error; corrected absolute-path command exited 0. These exploratory candidates are not the stable SHA-pinned pair above.

No audible, sound-quality, production, rights, engine, publish, promotion, or threshold-equality inference is warranted. No source, LOG, scorecard, canonical asset, or other report was edited.
