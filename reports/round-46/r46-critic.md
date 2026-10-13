# R46 critic — isolation and boundary claim audit

## Verdict

The declared measurement-level bracket is numerically supported by the executor pair, but its scope must stay narrow. These are different 5760-frame UI-shaped fixtures that differ in nominal sinusoid frequency; they establish that the existing **whole-wave magnitude-FFT centroid predicate** rejects one measured fixture and accepts another while the other ordinary checks pass. They do not show a pure, independently varied “spectrum” factor: frequency, quantized samples, and the full FFT distribution all change together. Nor do they establish behavior at exactly 250 Hz, or prove integrated runner modes/replay unless the later integration and fresh receipts do so.

This is distinct from R29: R29 compared a pairwise relative centroid delta against a baseline; this bracket addresses the ordinary per-file absolute band `250 <= centroid <= 4000`.

## Evidence actually measured

I independently invoked the existing project `measure()` on the executor WAVs. It uses ffprobe duration/format and SoX float32 decode, then computes the centroid as `dot(rfftfreq(N, 1/rate), abs(rfft(samples))) / sum(abs(rfft(samples)))` over the entire decoded file. Exact command from repository root:

```sh
python3 -c 'import importlib.util,json; from pathlib import Path; p=Path(".shokunin/audio/corpus/fixtures/measure_audio.py").resolve(); s=importlib.util.spec_from_file_location("m",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); d=Path(".shokunin/audio/corpus/live/round-46/executor").resolve(); print(json.dumps({n:m.measure(n,m.SPECS["ui"],d/("ui-centroid-"+n+".wav")) for n in ("below","above")},indent=2))'
```

Exit **0**. Actual project-decoded measurements:

| candidate | SHA-256 | duration / format | centroid | bandwidth | peak FS | RMS dBFS | ordinary failures |
|---|---|---|---:|---:|---:|---:|---|
| executor below | `fff9d981fe76c9163ba6a0db851e498b15fe193a1597427c8b73993b4666bfdf` | .12 s / 5760 frames, 48 kHz mono PCM16 | 249.71389590882862 Hz | 625.8273248256264 Hz | .279754638671875 | -18.327838866709165 | `spectrum: centroid outside fixture band` only |
| executor above | `6e453ff6cdf02e3fb72e0ebb0734f39a566a823841da8949187ad73d74a90a2a` | .12 s / 5760 frames, 48 kHz mono PCM16 | 250.3250670185918 Hz | 625.8448652317335 Hz | .27984619140625 | -18.32783946042307 | none |

Both pass duration, format, peak `<.95`, and RMS `>=.001`; integrated LUFS is null and is not an acceptance predicate. The gate-level result is indeed sole-spectrum-failure vs no failure. Do not conflate this with evidence the samples differ *only* in a spectral scalar; this broad centroid is computed from the complete FFT magnitude distribution and is sensitive to waveform envelope, window/leakage, quantization, and all spectral components.

The final nominal frequencies were 225 and 226 Hz (executor report). They are not the reported centroid: the respective decoded centroids are about 24.714 Hz above and 24.325 Hz above nominal. A one-Hz nominal change yielded about 0.611-Hz centroid change, with both measured centroids shifted from the intended boundary by taper/leakage and finite-record effects. The observed measured centroid, not oscillator label or target, determines pass/fail. The approximately 626-Hz bandwidths further caution that this scalar centroid does not describe a narrow single-frequency component.

## Falsification / limitations

- **“Sole spectrum isolation” overclaim:** the failure lists isolate which existing predicate rejects the below candidate, not a causal experiment in which only a scalar centroid changed and everything else remained invariant. Two separate quantized PCM waveforms were generated; the spectral distributions and decoded peak/RMS are not identical. The safe statement is “these two fixtures differ in the existing spectrum gate outcome, while their other checks pass.”
- **Quantization / FFT confounds:** PCM16 quantization and a finite 5760-sample record feed an unwindowed, whole-wave FFT magnitude centroid. The FFT bin spacing is 48000/5760 = 8.333… Hz. The executor generation recipe uses a Hann window, which broadens the FFT distribution; the measured centroid is not the nominal tone and should not be presented as a precise oscillator estimate or a pure tone frequency. The two actual results are only about .61 Hz apart across the threshold; there is no measured uncertainty/repeatability interval or quantization-sensitivity sweep. These caveats do not invalidate the concrete outcomes from the unchanged deterministic project path, but constrain generalization.
- **Equality:** source condition is inclusive (`250 <= centroid <= 4000`). Neither candidate measures exactly 250 Hz. There is no equality fixture/result and no basis to state observed equality behavior, floating-point edge behavior, or a sharp physically meaningful boundary. At most, source inspection indicates the comparison's stated inclusive semantics.
- **Measurement and runner scope:** my command measured scratch files directly through `measure()`, not the CLI runner, not either proposed opt-in mode, and not the requested fresh serial replay. Thus it independently confirms candidate numbers and check lists, not runner wiring, receipt persistence, canonical preservation, or replay. Parent should only claim those after checking integration and replay receipts.
- **Counterexamples to nominal-frequency inference:** executor's reported earlier fitting attempts nominal 230/270 Hz measured 253.80451803986455 / 293.3534382718592 Hz (both on the passing side); 180/190/200/210/215/218/220 Hz attempts measured 203.49356156298964 / 214.04197054391747 / 224.82545582968012 / 233.60780677342987 / 238.72811691578477 / 241.74486157112997 / 243.28423052433737 Hz (below side). These figures are transcribed from executor/reviewer reports, not measurements I reran. They illustrate fitting iterations, not additional integrated fixtures.

## Errors and provenance distinctions

My helper measurement command above had no setup error and no failed numeric fit. I made no new candidate fits. Executor reports its earlier 230/270 attempt as a numeric fit miss (both above threshold), followed by final measured fit; not a project setup/gate failure. Reviewer and scribe report relative-path helper invocations exiting 1 with `ValueError` because candidate paths were not beneath helper `ROOT`: those are setup/path errors, not numerical failures. Alt reports a similar path setup error and prior decaying-sine fits with both candidates in band (or otherwise not bracketing); those are failed numeric fits after successful helper measurement, not a broken ordinary gate. Scribe's “no qualifying bracket” refers to its limited inspection of the alt pair, and is superseded by the executor pair in the separate executor report; it is not evidence that the executor pair fails.

For transparency, I ran exactly the command above (exit 0) and no other shell commands. Hashes and reported nominal recipe/failed-fit history are read from the executor report. I did not audition anything.

## Conclusion and limits

The executor candidate data demonstrate a *fixture-level numerical bracket* around the ordinary lower UI centroid check: measured 249.7138959 Hz fails only the spectrum predicate; measured 250.3250670 Hz passes all ordinary checks. Independent alt report also describes a separate measured below/above pair, but its broader distance from the boundary does not address near-boundary sensitivity. Do not claim pure-spectrum causal isolation, exact 250-Hz equality, universal centroid calibration, perceptual timbre/novelty/quality, or any production, rights, engine, publishing, or promotion inference. Numerical fixture calibration only.
