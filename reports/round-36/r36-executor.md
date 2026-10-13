# Round 36 executor report

## Candidate and method
Generated an original 2.0 s continuous 110 Hz sine at 48,000 samples/s, amplitude 0.30, quantized to signed PCM16; wrote mono WAV directly in scratch. This is an analytic fixture, not an auditioned sound asset. Candidate: `.shokunin/audio/corpus/live/round-36/executor/ambience_third.wav`; SHA-256 `bee0beb7f8c0895a168bcfebfa11d2d14fc12c0e1e64deff9a48dcb6ba6ac3c7`.

Applied the declared project helper `measure_audio.measure` directly to this candidate and both existing ambience WAVs, using the declared ambience spec `(2.0, 5, 200, True)`. The candidate's helper result: exactly 2.0 s, 48,000 Hz, mono, `pcm_s16le`, 16-bit; peak `0.29998779296875`, RMS `-13.468131842088988 dBFS`, weighted positive-frequency centroid `123.61925440416788 Hz`, endpoint delta `0.00433349609375`, side-slope mismatch `0.000030517578125`; failures `[]`. Both seam proxies are within declared cutoffs (.03 and .001).

| Baseline | Baseline centroid Hz | Duration delta s | Relative centroid delta | Helper failures |
|---|---:|---:|---:|---|
| `ambience.wav` | 36.61640767851373 | 0.0 | 2.376061777810794 | `[]` |
| `ambience_alt.wav` | 58.01919713436623 | 0.0 | 1.130661238173961 | `[]` |

Both explicit comparisons clear .10 on centroid with zero duration difference; under the unchanged OR threshold these comparisons pass by centroid alone. Candidate centroid lies within the existing 5–200 Hz band. Numerical seam checks do not establish seamless perception; centroid is not perceptual/spectral-distribution novelty evidence. No audition, quality, production, rights, engine, publishing, or promotion claim.

## Exact shell commands and exits
Candidate generation was performed in the Python REPL, not via shell. The direct measurement shell command (exit 0) was:

```sh
python3 -c 'import importlib.util,json,pathlib; p=pathlib.Path(".shokunin/audio/corpus/fixtures/measure_audio.py"); s=importlib.util.spec_from_file_location("ma",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); spec=(2.0,5,200,True); paths={"ambience_third":pathlib.Path(".shokunin/audio/corpus/live/round-36/executor/ambience_third.wav").resolve(),"ambience":pathlib.Path(".shokunin/audio/corpus/artifacts/ambience.wav").resolve(),"ambience_alt":pathlib.Path(".shokhun/audio/corpus/artifacts/ambience_alt.wav").resolve()}; paths["ambience_alt"]=pathlib.Path(".shokunin/audio/corpus/artifacts/ambience_alt.wav").resolve(); data={k:m.measure(k,spec,v) for k,v in paths.items()}; cand=data["ambience_third"]; comparisons={k:{"duration_delta_s":abs(cand["duration_s"]-v["duration_s"]),"centroid_relative_delta":abs(cand["spectral_centroid_hz"]-v["spectral_centroid_hz"])/v["spectral_centroid_hz"]} for k,v in data.items() if k!="ambience_third"}; out={"candidate":cand,"baselines":{k:v for k,v in data.items() if k!="ambience_third"},"comparisons":comparisons}; pathlib.Path(".shokunin/audio/corpus/live/round-36/executor/measurement.json").write_text(json.dumps(out,indent=2)+"\n"); print(json.dumps(out,indent=2))'
```

Setup failure, separately (initial measurement attempt, shell exit 1): same direct-helper command was run with relative `Path(...)` arguments instead of `.resolve()`. `measure()` failed when `path.relative_to(ROOT)` rejected the candidate path outside the fixtures root (`ValueError`); no measurement or candidate-fit conclusion was drawn from it. The corrected resolved-path invocation above exited 0. One REPL harness misuse (`await` on an already-completed `BashResult`) was a Python-side error after the command had exited, not a shell/setup or fit result.

No source, canonical artifact, LOG, SCORECARD, or other report was edited; no commit or push.
