# Round 26 executor — matched UI duplicate scratch

## Result

Created two original scratch WAVs under `corpus/live/round-26/executor/`:

- `ui_clone.wav`
- `ui_clone_alt.wav`

Both are mono PCM16, 48 kHz, 5,760 frames (0.120 s), synthesized from the same analytic waveform `round(0.30 * sin(2π·700·t) * exp(-20t) * 32767)` for `t = arange(5760)/48000`, clipped to PCM range. Their SHA-256 hashes are both `57b3061d6a1b3ea7d94dcf4ea9c1bf6638d22e5284adaff37d3caf3d07b59ce1`; the files are byte-identical.

Direct invocation of the repository `measure()` function using the `ui` spec `(0.12, 250, 4000, False)` passed for both. Each reported duration 0.12 s, 48,000 Hz, mono, `pcm_s16le`/16-bit, peak 0.2978515625 FS, RMS −20.3165302447 dBFS, centroid 971.8642231 Hz, and no failures. LUFS was null; no LUFS claim is made.

Pair comparison: `duration_delta_s = 0.0`; `centroid_relative_delta = 0.0`; existing OR distinctness predicate (`duration_delta >= .020 or centroid_relative_delta >= .10`) is false. Thus this is a matched exact-duplicate negative candidate only; it was not integrated into or run through the shared CLI and does not establish runner-level failure isolation.

## Commands and outcomes

The direct check used this shell command, from the repository root:

```sh
python3 -c 'import importlib.util,json; from pathlib import Path; p=Path(".shokunin/audio/corpus/fixtures/measure_audio.py").resolve(); s=importlib.util.spec_from_file_location("m",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); spec=(.12,250,4000,False); paths=[Path(".shokunin/audio/corpus/live/round-26/executor/ui_clone.wav").resolve(),Path(".shokunin/audio/corpus/live/round-26/executor/ui_clone_alt.wav").resolve()]; results=[m.measure(n,spec,x) for n,x in zip(("ui_clone","ui_clone_alt"),paths)]; print(json.dumps(results,indent=2)); d=abs(results[1]["duration_s"]-results[0]["duration_s"]); c=abs(results[1]["spectral_centroid_hz"]-results[0]["spectral_centroid_hz"])/results[0]["spectral_centroid_hz"]; print(json.dumps({"duration_delta_s":d,"centroid_relative_delta":c,"distinctness_passed":d>=.020 or c>=.10}))'
```

Exit **0**. Output confirmed both measurements passed with no failures and distinctness false at zero/zero.

Two setup attempts failed and are not passes: the initial direct-check command used relative paths without resolving them, so `measure()` raised `ValueError` (`exit 1`, path not relative to `ROOT`); the next command used the misspelled path `.shokhun/audio/...` and failed `FileNotFoundError` (`exit 1`). The corrected command above resolved the paths and succeeded. No shared source, canonical asset, log, scorecard, or other report was edited. No listening, engine, rights, publishing, or promotion claim is made.
