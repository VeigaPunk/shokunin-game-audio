# Round 35 reviewer — minimal movement-family candidate

## Recommendation

Recommend the existing `alt` scratch candidate as the selected fit for the parent to consider integrating: one deterministic source-generation block in `build_artifacts.py`, one `SPECS["movement_third"] = (.30, 100, 16000, False)` entry, and a separate `movement_family_comparisons` record for `movement` and `movement_alt`. Leave the generic `_alt` loop and its thresholds unchanged. This is a proposal only; no canonical artifact or source integration was made here. Parent integration and independent verification are still required before anything is canonical/admitted.

The candidate source uses 48 kHz, 14,400 samples, deterministic NumPy RNG seed 3501, a short attack transient, and a decaying 1.8 kHz tone. Direct project measurement gave 0.30 s, 48 kHz mono PCM16, peak 0.489501953125 FS, RMS -14.025186267550422 dBFS, centroid 4553.583280111138 Hz, and no ordinary fixture failures. Relative centroid deltas are 0.6184516010427937 vs `movement` and 0.6212989100908565 vs `movement_alt`; duration deltas are 0.06 s vs each. Each independently clears the declared >=10% centroid selection criterion and the existing duration >=.020 s OR branch. The candidate scratch SHA-256 is `0e5f815e1987e13646170571e1f1e977b25e3566d90ebcca558c72ed07851d44`.

Suggested comparison-record shape, separate from generic `_alt` comparisons:

```python
movement_family_comparisons = {}
third_movement = measurements["movement_third"]
for name in ("movement", "movement_alt"):
    base = measurements[name]
    duration_delta = abs(third_movement["duration_s"] - base["duration_s"])
    centroid_relative_delta = abs(
        third_movement["spectral_centroid_hz"] - base["spectral_centroid_hz"]
    ) / base["spectral_centroid_hz"]
    passed = duration_delta >= .020 or centroid_relative_delta >= .10
    movement_family_comparisons[name] = {
        "baseline": name,
        "variant": "movement_third",
        "duration_delta_s": duration_delta,
        "centroid_relative_delta": centroid_relative_delta,
        "passed": passed,
    }
    if not passed:
        third_movement["failures"].append(
            f"movement family distinctness: movement_third vs {name} below duration and centroid minima"
        )
```

## Commands and fit/setup evidence

Executed from `/home/vgpnk/Projects/prymeagnt/audio`:

1. `python3 -c 'import importlib.util,json; p=".shokunin/audio/corpus/fixtures/measure_audio.py"; s=importlib.util.spec_from_file_location("measure_audio",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(json.dumps(m.measure("movement_third",(.30,100,16000,False),".shokunin/audio/corpus/live/round-35/alt/movement_third_candidate.wav"),indent=2))'` — exit **1**. This was invocation/setup error: passed a string where the project `measure()` expects a `Path`.
2. `python3 -c 'import importlib.util,json,pathlib; p=".shokunin/audio/corpus/fixtures/measure_audio.py"; s=importlib.util.spec_from_file_location("measure_audio",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(json.dumps(m.measure("movement_third",(.30,100,16000,False),pathlib.Path(".shokunin/audio/corpus/live/round-35/alt/movement_third_candidate.wav")),indent=2))'` — exit **1**. Setup/path error: relative candidate path was resolved against corpus ROOT, not repository root.
3. `python3 -c 'import importlib.util,json,pathlib; p=".shokunin/audio/corpus/fixtures/measure_audio.py"; s=importlib.util.spec_from_file_location("measure_audio",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(json.dumps(m.measure("movement_third",(.30,100,16000,False),pathlib.Path("/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-35/alt/movement_third_candidate.wav")),indent=2))'` — exit **0**. Candidate fit values above; `failures: []`.
4. `python3 -c 'import importlib.util,json,pathlib; p=".shokunin/audio/corpus/fixtures/measure_audio.py"; s=importlib.util.spec_from_file_location("measure_audio",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); r={n:m.measure(n,m.SPECS[n]) for n in ("movement","movement_alt")}; print(json.dumps(r,indent=2))'` — exit **0**. Baseline values used above: movement 0.24 s / 11934.484045946316 Hz, movement_alt 0.36 s / 12024.214879348818 Hz; both ordinary checks pass.

The two initial errors are setup failures, not candidate fit failures. Candidate project measurement succeeded. No audition or perceptual evaluation was performed. Duration and spectral-centroid differences are numeric proxies only; they establish no auditory/perceptual novelty, sound quality, production suitability, rights status, engine compatibility, publication readiness, or promotion.
