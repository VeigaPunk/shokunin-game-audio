# Round 37 critic — falsification and numeric interpretation

## Question and finding

The declaration asks whether the proposed negative can be attributed to the existing distinctness rule, rather than ordinary or loop-seam checks, when duration delta is zero. The measured scratch fits support that narrow numerical claim: both the executor's 60/64 Hz pair and the independent alt pair pass `measure()`'s ordinary/seam checks, have duration delta exactly `0.0`, and have nonzero centroid-relative deltas below `.10`. Under the existing OR expression, both terms are false, so the expected *pair-level* result is distinctness failure only. This falsifies duration mismatch and individual numeric/seam failure as explanations for those measured fits.

Important limitation: the declared `--probe-ambience-centroid-below` runner mode is not present in the inspected `measure_audio.py`; no integrated runner receipt or exit-1 gate result exists yet. The fit demonstrates the inputs and existing predicate numerically, not that a new opt-in mode has actually produced an isolated runner failure. The code's generic `_alt` loop appends `distinctness: duration < .020 s and centroid delta < 10%` to a variant after its individual measurement; the new mode must route its scratch pair through that path and receipt to establish the integrated claim.

## Evidence for numeric fit vs setup

The two extant Round 37 wave-one fit reports record independent candidates:

- `r37-executor.md`: baseline 67.3718262596 Hz and variant 71.8086398234 Hz; relative delta 0.0658556226. Both 2 s, 48 kHz mono PCM16; helper `failures: []`; peak about .22 FS; endpoint jumps .00174/.00183 FS and slope mismatches .00003052 FS/sample. The generator's one failed invocation (`ModuleNotFoundError: scipy`) was an environment/setup failure, followed by a successful standard-library WAV generator and a successful measured fit. No numeric candidate was reported as a failed fit.
- `r37-alt.md`: baseline 81.1200010910 Hz and variant 85.4656028614 Hz; relative delta 0.0535700408. Both 2 s, 48 kHz mono PCM16; helper `failures: []`; peak .3100/.3250 FS; endpoint deltas .00278/.00308 FS and slope mismatch .00003052 FS/sample. Its first measurement invocation used relative paths and failed at `path.relative_to(ROOT)` (setup/path issue); the corrected absolute-path measurement succeeded. No numeric fit was reported as failed.

I independently invoked the existing project `measure()` helper against the executor scratch files. Exact shell command and exit:

```sh
python3 - <<'PY'
import importlib.util, pathlib, json
p=pathlib.Path('.shokunin/audio/corpus/fixtures/measure_audio.py')
s=importlib.util.spec_from_file_location('measure_audio',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
spec=(2.0,5,200,True)
root=pathlib.Path('.shokunin/audio/corpus/live/round-37/executor')
a=m.measure('baseline',spec,root/'baseline.wav'); b=m.measure('variant',spec,root/'variant.wav')
print(json.dumps({'baseline':a,'variant':b,'duration_delta_s':abs(a['duration_s']-b['duration_s']),'centroid_relative_delta':abs(b['spectral_centroid_hz']-a['spectral_centroid_hz'])/a['spectral_centroid_hz']},indent=2))
PY
```

Exit **1**: `ValueError` from `path.relative_to(ROOT)` because the candidate path was relative. This is setup/path handling, not a numeric fit result.

Corrected invocation (only `root.resolve()` changed) and exit:

```sh
python3 - <<'PY'
import importlib.util, pathlib, json
p=pathlib.Path('.shokunin/audio/corpus/fixtures/measure_audio.py')
s=importlib.util.spec_from_file_location('measure_audio',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
spec=(2.0,5,200,True)
root=pathlib.Path('.shokunin/audio/corpus/live/round-37/executor').resolve()
a=m.measure('baseline',spec,root/'baseline.wav'); b=m.measure('variant',spec,root/'variant.wav')
print(json.dumps({'baseline':a,'variant':b,'duration_delta_s':abs(a['duration_s']-b['duration_s']),'centroid_relative_delta':abs(b['spectral_centroid_hz']-a['spectral_centroid_hz'])/a['spectral_centroid_hz']},indent=2))
PY
```

Exit **0**. It returned both empty `failures` arrays, duration delta `0.0`, and relative centroid delta `0.06585562259644766`. This independently verifies one numerical fit; it does not invoke the absent round-37 runner flag. The other candidate's reported absolute-path corrected command also succeeded, per `r37-alt.md`.

## Proxy interpretation / attempted falsification

The fit satisfies the declared numeric band and limits but does not establish that the sounds are similar or dissimilar in any perceptual sense. The helper's whole-wave centroid is a scalar weighted positive-frequency statistic; very different spectra can share a centroid, and small centroid differences need not indicate close spectra. The executor's single-tone candidates are especially a warning: despite nominal 60/64 Hz components, the helper reports centroids 67.37/71.81 Hz and bandwidths around 339/348 Hz, illustrating that the centroid is not a component-frequency label or a spectrum-distance test. Conversely, nonidentical analytic coefficients or hashes do not establish perceptual novelty. Endpoint and endpoint-slope metrics are numeric seam proxies only.

Thus I find no numeric counterexample among the measured candidates to the narrow statement “this equal-duration pair fails only the existing numeric distinctness predicate.” I do reject any broader reading that this tests perceptual similarity, fully calibrates the threshold, or validates an integrated opt-in runner before its receipt exists. The runner must retain both per-file empty ordinary/seam failure lists and show only the variant's distinctness entry; if it reports anything else, that falsifies “solely distinctness” for that run.

No audition, sound-quality, production, rights, engine, publishing, or promotion claim is made. No shared source, LOG, SCORECARD, canonical artifact, other report, commit, or push was changed.
