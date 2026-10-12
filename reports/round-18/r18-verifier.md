# Round 18 independent 14-mode replay

Verifier: independent serial replay (non-author). Working directory: `/home/vgpnk/Projects/prymeagnt/audio`. Commands ran in order with Python 3; exit 1 is expected for deliberate negative/invalid probes. Each invocation generated an immutable timestamped receipt under `.shokunin/audio/corpus/live/runs/`.

| # | Command | Exit | Receipt | Result |
|---:|---|---:|---|---|
| 1 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261012T192010370491Z-normal/measurements.json` | `pass` |
| 2 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261012T192011238149Z-layer-third-slope/measurements.json` | `{"slope200_probe": ["sections: internal join side slope mismatch > .001 full scale per sample"]}` |
| 3 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | 1 | `.shokunin/audio/corpus/live/runs/20261012T192012084965Z-layer-alt-reverse/measurements.json` | `{"reverse180_probe": ["sections: 180 Hz component amplitude contrast < 6 dB or invalid"]}` |
| 4 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261012T192012939855Z-layer-alt-slope/measurements.json` | `{"slope180_probe": ["sections: internal join side slope mismatch > .001 full scale per sample"]}` |
| 5 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 | `.shokunin/audio/corpus/live/runs/20261012T192013795795Z-layer-alt-join/measurements.json` | `{"join180_probe": ["sections: internal join adjacent sample gap > .03 full scale"]}` |
| 6 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261012T192014666885Z-layer-alt-flat/measurements.json` | `{"flat180_probe": ["sections: 180 Hz component amplitude contrast < 6 dB or invalid"]}` |
| 7 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261012T192015528669Z-layer-slope/measurements.json` | `{"layer_slope_probe": ["sections: internal join side slope mismatch > .001 full scale per sample"]}` |
| 8 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | `.shokunin/audio/corpus/live/runs/20261012T192016385023Z-layer-join/measurements.json` | `{"join_probe": ["sections: internal join adjacent sample gap > .03 full scale"]}` |
| 9 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261012T192017253394Z-flat/measurements.json` | `{"flat30_probe": ["sections: 30 Hz component amplitude contrast < 6 dB or invalid"]}` |
| 10 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261012T192018105092Z-layer-flat/measurements.json` | `{"flat120_probe": ["sections: 120 Hz component amplitude contrast < 6 dB or invalid"]}` |
| 11 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261012T192018942177Z-slope/measurements.json` | `{"slope_probe": ["loop seam: slope mismatch > .001 full scale per sample"]}` |
| 12 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `.shokunin/audio/corpus/live/runs/20261012T192019728750Z-failing/measurements.json` | `{"ambience": ["spectrum: centroid outside fixture band", "loop seam: endpoint jump > .03 full scale"]}` |
| 13 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `.shokunin/audio/corpus/live/runs/20261012T192019957962Z-invalid/measurements.json` | `{"corrupt": "decode", "odd_sections": "section count", "short_sections": "section count", "wrong_format": "format"}` |
| 14 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261012T192020754277Z-normal/measurements.json` | `pass` |

## Checks

- Exactly 14 modes ran serially; the final normal run restored clean artifacts and passed (exit 0).
- All 13 tracked canonical WAVs match SHA-256 of baseline `7083a3f`; exact mapping follows.
- Five variant distinctness checks passed in the final normal receipt.
- Expected targeted failures: new 200 Hz probe fails only internal side-slope (> .001); prior probes retain their expected distinct gates; failing and invalid controls fail as expected.
- No perceptual/audio-quality claim. No canonical artifacts were modified by the replay.

### Canonical artifact SHA-256

- `ambience.wav` `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198`
- `ambience_alt.wav` `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc`
- `impact.wav` `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc`
- `impact_alt.wav` `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6`
- `movement.wav` `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d`
- `movement_alt.wav` `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639`
- `stem.wav` `fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0`
- `stem_layer.wav` `ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9`
- `stem_layer_alt.wav` `74926bf517298fa241e9960099aca60a728a54c41d9454876366dfe4d90adaa9`
- `stem_layer_third.wav` `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445`
- `stem_sections.wav` `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702`
- `ui.wav` `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9`
- `ui_alt.wav` `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f`

Selected 200 Hz probe WAV SHA-256: `e7c98cc5af858d8dab2be01a4f76382e06008573a017909c2760e68a585b1881`.

The new probe measurement reports 200 Hz contrast `10.457243020771665 dB`, internal gap `0.000396728515625` FS (within `.03`), and side-slope mismatch `0.00115966796875` FS/sample (the sole failure; threshold `.001`). The probe is valid and contrast passes.

## Additional independent replay checks

Commands below were run from `/home/vgpnk/Projects/prymeagnt/audio`; each exited 0.

- First/final normal receipt equality: `python3 -c "import json,pathlib; a=json.loads(pathlib.Path('.shokunin/audio/corpus/live/runs/20261012T192010370491Z-normal/measurements.json').read_text()); b=json.loads(pathlib.Path('.shokunin/audio/corpus/live/runs/20261012T192020754277Z-normal/measurements.json').read_text()); print('equal=',a==b); assert a==b"` → `equal= True` (all JSON keys/data equal).
- Candidate/generated/alternate byte identity: `python3 -c "import hashlib,pathlib; p=pathlib.Path('.shokunin/audio/corpus/live/round-18'); names=['slope200_candidate.wav','slope200_other.wav','slope200_probe.wav']; d={n:hashlib.sha256((p/n).read_bytes()).hexdigest() for n in names}; print(d); assert len(set(d.values()))==1"` → exit 0; all three SHA-256 `e7c98cc5af858d8dab2be01a4f76382e06008573a017909c2760e68a585b1881` (byte equality by matching hashes).
- Only changed PCM sample vs baseline source `stem_layer_third.wav`: command `python3 -c "import pathlib,subprocess,numpy as np; base=subprocess.check_output(['git','show','7083a3f:.shokunin/audio/corpus/artifacts/stem_layer_third.wav']); out=pathlib.Path('.shokunin/audio/corpus/live/round-18/slope200_candidate.wav').read_bytes(); assert base[:44]==out[:44]; a=np.frombuffer(base[44:],dtype='<i2'); b=np.frombuffer(out[44:],dtype='<i2'); d=np.flatnonzero(a!=b); print('changed=',[(int(i),int(a[i]),int(b[i])) for i in d]); assert d.tolist()==[96001] and int(a[96001])==43 and int(b[96001])==51"` → exit 0, `changed= [(96001, 43, 51)]`.
- Independently parsed new-mode receipt: `python3 -c "import json,pathlib; r=json.loads(pathlib.Path('.shokunin/audio/corpus/live/runs/20261012T192011238149Z-layer-third-slope/measurements.json').read_text()); s=r['sections']['slope200_probe']; print({k:s[k] for k in ['valid','passed','component_amplitude_contrast_db','internal_join_adjacent_delta_full_scale','internal_join_side_slope_mismatch_full_scale_per_sample']},r['measurements']['slope200_probe']['failures']); assert s['valid'] and s['passed'] and s['component_amplitude_contrast_db']>6 and s['internal_join_adjacent_delta_full_scale']<=.03 and s['internal_join_side_slope_mismatch_full_scale_per_sample']>.001"` → exit 0. Values: valid/pass `True`; contrast `10.457243020771665 dB`; internal gap `0.000396728515625` FS; side-slope mismatch `0.00115966796875` FS/sample. Receipt's sole failure is the side-slope threshold (`.001`).

## Fresh non-author serial replay (2026-10-12 19:22 UTC)

Re-ran the complete requested 14-mode sequence serially from `/home/vgpnk/Projects/prymeagnt/audio`; no setup errors occurred. These are this replay’s receipts (distinct from prior report receipts). The `--probe-invalid` mode exercises only invalid probe fixtures; it does not measure or assert anything about canonical WAVs.

| # | Exact command | Exit | Receipt ID | Failure set |
|---:|---|---:|---|---|
| 1 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `20261012T192207972055Z-normal` | `none` |
| 2 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope` | 1 | `20261012T192208841992Z-layer-third-slope` | `{"slope200_probe": ["sections: internal join side slope mismatch > .001 full scale per sample"]}` |
| 3 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | 1 | `20261012T192209704270Z-layer-alt-reverse` | `{"reverse180_probe": ["sections: 180 Hz component amplitude contrast < 6 dB or invalid"]}` |
| 4 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | 1 | `20261012T192210575319Z-layer-alt-slope` | `{"slope180_probe": ["sections: internal join side slope mismatch > .001 full scale per sample"]}` |
| 5 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 | `20261012T192211449612Z-layer-alt-join` | `{"join180_probe": ["sections: internal join adjacent sample gap > .03 full scale"]}` |
| 6 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 | `20261012T192212319925Z-layer-alt-flat` | `{"flat180_probe": ["sections: 180 Hz component amplitude contrast < 6 dB or invalid"]}` |
| 7 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 | `20261012T192213184025Z-layer-slope` | `{"layer_slope_probe": ["sections: internal join side slope mismatch > .001 full scale per sample"]}` |
| 8 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | `20261012T192214052279Z-layer-join` | `{"join_probe": ["sections: internal join adjacent sample gap > .03 full scale"]}` |
| 9 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `20261012T192214914278Z-flat` | `{"flat30_probe": ["sections: 30 Hz component amplitude contrast < 6 dB or invalid"]}` |
| 10 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `20261012T192215779403Z-layer-flat` | `{"flat120_probe": ["sections: 120 Hz component amplitude contrast < 6 dB or invalid"]}` |
| 11 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `20261012T192216635327Z-slope` | `{"slope_probe": ["loop seam: slope mismatch > .001 full scale per sample"]}` |
| 12 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `20261012T192217441364Z-failing` | `{"ambience": ["spectrum: centroid outside fixture band", "loop seam: endpoint jump > .03 full scale"]}` |
| 13 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `20261012T192217670831Z-invalid` | `{"corrupt": "decode", "odd_sections": "section count", "short_sections": "section count", "wrong_format": "format"}` |
| 14 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `20261012T192218476174Z-normal` | `none` |

### Fresh replay cross-checks

- First and final normal parsed receipts are exactly equal: `True`; initial `20261012T192207972055Z-normal`, final `20261012T192218476174Z-normal`. Both had 13 measurements, mode `normal`, and no failures. Five variant distinctness checks passed in both normal receipts: `True`.
- Generated `slope200_probe.wav`, selected `slope200_candidate.wav`, and alternate `slope200_other.wav` each SHA-256 `e7c98cc5af858d8dab2be01a4f76382e06008573a017909c2760e68a585b1881`; all hashes equal.
- Binary-safe comparison of selected candidate PCM against Git baseline `7083a3f:.shokunin/audio/corpus/artifacts/stem_layer_third.wav` found exactly one changed int16 sample: frame 96001, 43 → 51 (+8).
- Independently recomputed SHA-256 for all 13 current canonical WAVs against their `git show 7083a3f` blobs: all equal (`True`). Hash mapping above.
- Fresh slope200 receipt `20261012T192208841992Z-layer-third-slope` reports valid/pass `True/True`, 200 Hz contrast `10.457243020771665 dB`, internal gap `0.000396728515625` FS (<= .03), and side-slope `0.00115966796875` FS/sample (> .001). Sole failure is strict internal side-slope threshold; generic/outer checks pass.
- The old probe failure sets match those tabulated above: reverse contrast, 180Hz slope, join gap, flat contrast, layer slope, join gap, 30Hz flat contrast, 120Hz flat contrast, and outer seam slope each fail their expected single gate; `--probe-failing` retains the two expected ambience failures. `--probe-invalid` reports section-count/decode/format failures only.
- No audible, engine, or production inference follows from these measurements.
