# Round 25 independent verifier (r25-verifier)

## Result

I independently replayed the 19 runner executions serially in the Round 22 verifier order: normal, two third-join edges, the 15 prior flags (including `--probe-invalid`), then restored normal. Successful replay exit vector: `[0,0,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0]`. All produced receipts; there was no runner setup error or exit 2. Intentional negative controls exit 1. The invalid receipt contains eight records: the prior six retain their expected statuses and the new two are expected `format` failures. Each new control differs from the native16 positive in exactly one targeted field. Both direct `measure()` controls have only the expected rate/channel format failure under broad `(4.0,100,1000,False)` spec.

## Serial replay: exact commands, exits, receipts, failure sets

| # | Exact command | Exit | Receipt | Failure set (or invalid observed failures) |
|---:|---|---:|---|---|
| 1 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T014011312756Z-normal/measurements.json` | `{}` |
| 2 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T014012185127Z-layer-third-join-edge-pass/measurements.json` | `{}` |
| 3 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T014013055442Z-layer-third-join-edge-fail/measurements.json` | `{"join200_edgefail_probe": ["sections: internal join adjacent sample gap > .03 full scale"]}` |
| 4 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T014013934912Z-layer-third-join/measurements.json` | `{"join200_probe": ["sections: internal join adjacent sample gap > .03 full scale"]}` |
| 5 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T014014813403Z-layer-third-slope-edge-pass/measurements.json` | `{}` |
| 6 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T014015672800Z-layer-third-slope-edge-fail/measurements.json` | `{"edgefail_probe": ["sections: internal join side slope mismatch > .001 full scale per sample"]}` |
| 7 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T014016541338Z-layer-third-slope/measurements.json` | `{"slope200_probe": ["sections: internal join side slope mismatch > .001 full scale per sample"]}` |
| 8 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | 1 | `.shokunin/audio/corpus/live/runs/20261013T014017402378Z-layer-alt-reverse/measurements.json` | `{"reverse180_probe": ["sections: 180 Hz component amplitude contrast < 6 dB or invalid"]}` |
| 9 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T014018266148Z-layer-alt-slope/measurements.json` | `{"slope180_probe": ["sections: internal join side slope mismatch > .001 full scale per sample"]}` |
| 10 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T014019131033Z-layer-alt-join/measurements.json` | `{"join180_probe": ["sections: internal join adjacent sample gap > .03 full scale"]}` |
| 11 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T014019990478Z-layer-alt-flat/measurements.json` | `{"flat180_probe": ["sections: 180 Hz component amplitude contrast < 6 dB or invalid"]}` |
| 12 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T014020857122Z-layer-slope/measurements.json` | `{"layer_slope_probe": ["sections: internal join side slope mismatch > .001 full scale per sample"]}` |
| 13 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T014021725830Z-layer-join/measurements.json` | `{"join_probe": ["sections: internal join adjacent sample gap > .03 full scale"]}` |
| 14 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T014022592183Z-flat/measurements.json` | `{"flat30_probe": ["sections: 30 Hz component amplitude contrast < 6 dB or invalid"]}` |
| 15 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T014023471658Z-layer-flat/measurements.json` | `{"flat120_probe": ["sections: 120 Hz component amplitude contrast < 6 dB or invalid"]}` |
| 16 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T014024330392Z-slope/measurements.json` | `{"slope_probe": ["loop seam: slope mismatch > .001 full scale per sample"]}` |
| 17 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `.shokunin/audio/corpus/live/runs/20261013T014025146381Z-failing/measurements.json` | `{"ambience": ["spectrum: centroid outside fixture band", "loop seam: endpoint jump > .03 full scale"]}` |
| 18 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `.shokunin/audio/corpus/live/runs/20261013T014025494866Z-invalid/measurements.json` | `{"corrupt": "decode", "mono441_probe": "format", "native16_probe": null, "native24_probe": "format", "odd_sections": "section count", "short_sections": "section count", "stereo48_probe": "format", "wrong_format": "format"}` |
| 19 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T014026304512Z-normal/measurements.json` | `{}` |

The invalid receipt `.shokunin/audio/corpus/live/runs/20261013T014025494866Z-invalid/measurements.json` contains exactly these eight rows:

| Probe | Status | Observed failure | Metadata |
|---|---|---|---|
| `short_sections` | expected_failure | section count | 48000 Hz mono PCM16; 144000 decoded samples |
| `corrupt` | expected_failure | decode | ffprobe exit 1 on intentionally invalid RIFF |
| `wrong_format` | expected_failure | format | 44100 Hz, 2 channels, PCM16 (combined mismatch preserved) |
| `odd_sections` | expected_failure | section count | 48000 Hz mono PCM16; 101 decoded samples |
| `native16_probe` | expected_pass | none | 48000 Hz mono `pcm_s16le`, 16-bit |
| `native24_probe` | expected_failure | format | 48000 Hz mono `pcm_s24le`, 24-bit |
| `stereo48_probe` | expected_failure | format | 48000 Hz, 2 channels, `pcm_s16le`, 16-bit, 4 s; channels only differs from native16 |
| `mono441_probe` | expected_failure | format | 44100 Hz, mono, `pcm_s16le`, 16-bit, 4 s; sample rate only differs from native16 |

The invalid receipt tests format metadata; it does not measure ordinary acoustic conditions for those controls.

## Direct `measure()` calls

Exact invocations/exits and full returned JSON:

### `python3 -c 'import importlib.util,json; from pathlib import Path; s=importlib.util.spec_from_file_location("measure_audio",".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(json.dumps(m.measure("stereo48_probe",(4.0,100,1000,False),Path('"'"'/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-25/stereo48_probe.wav'"'"'),),indent=2))'` — exit 0

```json
{
  "path": "live/round-25/stereo48_probe.wav",
  "duration_s": 4.0,
  "sample_rate_hz": 48000,
  "channels": 2,
  "codec_name": "pcm_s16le",
  "bits_per_sample": 16,
  "peak_full_scale": 0.199981689453125,
  "rms_dbfs": -16.98997934609775,
  "integrated_lufs": -14.7,
  "spectral_centroid_hz": 563.261685059,
  "spectral_bandwidth_hz": 2804.790029152878,
  "seam_endpoint_delta_full_scale": null,
  "seam_slope_delta_full_scale_per_sample": null,
  "failures": [
    "format: expected 48kHz mono"
  ]
}
```

### `python3 -c 'import importlib.util,json; from pathlib import Path; s=importlib.util.spec_from_file_location("measure_audio",".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(json.dumps(m.measure("mono441_probe",(4.0,100,1000,False),Path('"'"'/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-25/mono441_probe.wav'"'"'),),indent=2))'` — exit 0

```json
{
  "path": "live/round-25/mono441_probe.wav",
  "duration_s": 4.0,
  "sample_rate_hz": 44100,
  "channels": 1,
  "codec_name": "pcm_s16le",
  "bits_per_sample": 16,
  "peak_full_scale": 0.199981689453125,
  "rms_dbfs": -16.989995250871296,
  "integrated_lufs": -17.7,
  "spectral_centroid_hz": 457.77161048241146,
  "spectral_bandwidth_hz": 507.19182681703705,
  "seam_endpoint_delta_full_scale": null,
  "seam_slope_delta_full_scale_per_sample": null,
  "failures": [
    "format: expected 48kHz mono"
  ]
}
```

Both calls report exactly `format: expected 48kHz mono`, with duration 4.0 s, peak 0.199981689453125, RMS about -16.99 dBFS, and centroid inside the supplied 100–1000 Hz band. Stereo48 reports 563.261685059 Hz and mono441 457.771610482 Hz. SoX float decoding is flattened into a scalar sequence: stereo48 contains 384000 interleaved scalar samples (192000 frames × 2), not 192000 mono samples. Consequently its FFT sample-count and centroid semantics are not channel-aware or equivalent to mono. This limits interpretation; the result does not claim acoustic equivalence.

## Guard checks

All 13 canonical WAV hashes match the pre-round `30530e17a4f20ba28d7f81cda41c8949f4652697` Git blobs:

- `ambience.wav` — `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198`
- `ambience_alt.wav` — `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc`
- `impact.wav` — `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc`
- `impact_alt.wav` — `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6`
- `movement.wav` — `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d`
- `movement_alt.wav` — `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639`
- `stem.wav` — `fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0`
- `stem_layer.wav` — `ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9`
- `stem_layer_alt.wav` — `74926bf517298fa241e9960099aca60a728a54c41d9454876366dfe4d90adaa9`
- `stem_layer_third.wav` — `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445`
- `stem_sections.wav` — `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702`
- `ui.wav` — `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9`
- `ui_alt.wav` — `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f`

Initial/restored normal each have 13 measurements, no failures, and all five passing `_alt` distinctness records: `ui_alt`, `impact_alt`, `movement_alt`, `ambience_alt`, `stem_layer_alt`. Normal receipt contents compare equal after removing measurement paths. Threshold objects across all replay receipts carrying them compare equal, including the two normals; no thresholds or prior mode behavior changed.

Builder scratch reproducibility: `python3 .shokunin/audio/corpus/fixtures/build_artifacts.py --probe-invalid` — exit **0**. The SHA-256 hashes of both new controls were unchanged by regeneration: stereo48 `1a71090267d97dc07c14f4a057e2b14a433b45086a424cb99128f55831328987`; mono441 `1bd9aac91baecffb03cb667c7e4116806eb149aa1c39b5cc787e1b861c965e69`. Builder source inspection confirms the deterministic analytic 4-second 440 Hz PCM16 generation. Source diff is limited to the declared builder and invalid-probe inventory/route; `format_failures()` and thresholds are unchanged.

## Setup disclosure and bounds

I first attempted the 19 commands with the whole command string quoted as the executable. Those 19 wrapper attempts exited **127** (`No such file or directory`) and created no receipts; they are setup failures and are excluded from the replay. The corrected commands were executed with repository-root `cd` and are the 19 successful executions listed above. No other setup failure occurred.

This verifies only the current isolated 48 kHz stereo and 44.1 kHz mono PCM16 examples, the listed runner modes, and scoped repository receipts. It does not establish universal WAV/codec handling, acoustic equivalence, sound quality, engine behavior, rights, or publishing. SHONEN status/promotion is outside my authority; no promotion claim is made.
