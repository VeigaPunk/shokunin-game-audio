# Round 22 independent verifier (r22-verifier)

Independent replay from repository root, in the exact round-21 verifier order. I did not edit code, LOG, SCORECARD, canonical artifacts, or other reports. Runner-created receipts are under `.shokunin/audio/corpus/live/runs/`; this report is the only report I wrote. Exit 1 is expected for intentional negative modes; exit 2 or setup error invalidates that execution. The serial runner replay had no exit 2 or setup error.

## Serial runner replay (19 executions)

| # | Exact shell invocation | Exit | Receipt | Failure set |
|---:|---|---:|---|---|
| 1 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T010810788169Z-normal/measurements.json` | none |
| 2 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T010811648246Z-layer-third-join-edge-pass/measurements.json` | none |
| 3 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T010812495732Z-layer-third-join-edge-fail/measurements.json` | join200_edgefail_probe: ['sections: internal join adjacent sample gap > .03 full scale'] |
| 4 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T010813339890Z-layer-third-join/measurements.json` | join200_probe: ['sections: internal join adjacent sample gap > .03 full scale'] |
| 5 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T010814182622Z-layer-third-slope-edge-pass/measurements.json` | none |
| 6 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T010815030001Z-layer-third-slope-edge-fail/measurements.json` | edgefail_probe: ['sections: internal join side slope mismatch > .001 full scale per sample'] |
| 7 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T010815882922Z-layer-third-slope/measurements.json` | slope200_probe: ['sections: internal join side slope mismatch > .001 full scale per sample'] |
| 8 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | 1 | `.shokunin/audio/corpus/live/runs/20261013T010816730147Z-layer-alt-reverse/measurements.json` | reverse180_probe: ['sections: 180 Hz component amplitude contrast < 6 dB or invalid'] |
| 9 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T010817574796Z-layer-alt-slope/measurements.json` | slope180_probe: ['sections: internal join side slope mismatch > .001 full scale per sample'] |
| 10 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T010818423685Z-layer-alt-join/measurements.json` | join180_probe: ['sections: internal join adjacent sample gap > .03 full scale'] |
| 11 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T010819277396Z-layer-alt-flat/measurements.json` | flat180_probe: ['sections: 180 Hz component amplitude contrast < 6 dB or invalid'] |
| 12 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T010820134370Z-layer-slope/measurements.json` | layer_slope_probe: ['sections: internal join side slope mismatch > .001 full scale per sample'] |
| 13 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T010821007188Z-layer-join/measurements.json` | join_probe: ['sections: internal join adjacent sample gap > .03 full scale'] |
| 14 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T010821850654Z-flat/measurements.json` | flat30_probe: ['sections: 30 Hz component amplitude contrast < 6 dB or invalid'] |
| 15 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T010822692960Z-layer-flat/measurements.json` | flat120_probe: ['sections: 120 Hz component amplitude contrast < 6 dB or invalid'] |
| 16 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T010823514996Z-slope/measurements.json` | slope_probe: ['loop seam: slope mismatch > .001 full scale per sample'] |
| 17 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `.shokunin/audio/corpus/live/runs/20261013T010824294787Z-failing/measurements.json` | ambience: ['spectrum: centroid outside fixture band', 'loop seam: endpoint jump > .03 full scale'] |
| 18 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `.shokunin/audio/corpus/live/runs/20261013T010824568740Z-invalid/measurements.json` | short_sections: section count; corrupt: decode; wrong_format: format; odd_sections: section count; native16_probe: None; native24_probe: format |
| 19 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T010825350561Z-normal/measurements.json` | none |


Exit vector: `[0,0,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0]`. This is normal, both new third-join-edge controls, the remaining 15 prior flags in round-21 verifier order (including `--probe-invalid`), then restored normal. Historical outcomes held: intentional negatives returned 1 with expected failure kinds, positive modes returned 0, and no mode returned 2. The invalid mode returned 1 as expected, with all six named records valid: `short_sections` -> section count, `corrupt` -> decode, `wrong_format` -> format, `odd_sections` -> section count, `native16_probe` -> expected_pass (no failure), `native24_probe` -> expected_failure (`format`). Native controls report 48,000 Hz mono: native16 `pcm_s16le`, 16 bits; native24 `pcm_s24le`, 24 bits. The corrupt fixture's ffprobe subcommand returns 1 as intended and is recorded in the receipt; this is not a runner setup error.

### Matched `measure()` PCM comparison

I independently invoked `measure()` from the project script using the project's `python3`, the executor's matched native PCM fixtures, and custom spec `(4.0, 100, 1000, True)` (duration 4 s, centroid band 100–1000 Hz, section checks enabled). These are exact invocations and exits:

- `python3 -c 'import importlib.util,json; from pathlib import Path; s=importlib.util.spec_from_file_location("measure_audio",".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(json.dumps(m.measure("native_pcm16",(4.0,100,1000,True),Path(".shokunin/audio/corpus/live/round-22/executor/native_pcm16.wav").resolve()),indent=2))'` — exit **0**, `failures: []`; ffprobe fields 48,000 Hz mono, `pcm_s16le`, 16 bits.
- `python3 -c 'import importlib.util,json; from pathlib import Path; s=importlib.util.spec_from_file_location("measure_audio",".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(json.dumps(m.measure("native_pcm24",(4.0,100,1000,True),Path(".shokunin/audio/corpus/live/round-22/executor/native_pcm24.wav").resolve()),indent=2))'` — exit **0**, only failure `format: expected PCM16`; ffprobe fields 48,000 Hz mono, `pcm_s24le`, 24 bits.

Setup error disclosure: I first issued the same two `-c` invocations with non-resolved relative `Path(...)`; both exited **1** in result serialization at `path.relative_to(ROOT)` because `ROOT` is absolute. Those attempts are invalid setup attempts, not test results. I corrected only the path to `.resolve()` and reran the two commands above successfully. No source or fixture change was made to correct this setup issue.

## Receipts and regression checks

- Initial and restored normal: `.shokunin/audio/corpus/live/runs/20261013T010810788169Z-normal/measurements.json` and `.shokunin/audio/corpus/live/runs/20261013T010825350561Z-normal/measurements.json`. Parsed JSON is equal after recursively removing `path` keys; each has 13 measurements, no measurement failures, and five passing distinctness records.
- Invalid control: `.shokunin/audio/corpus/live/runs/20261013T010824568740Z-invalid/measurements.json`. Six probe statuses match expectation, including positive native16 and native24 format rejection above.
- Both newly generated normal / edge receipts include all five `_alt` distinctness records (`ui_alt`, `impact_alt`, `movement_alt`, `ambience_alt`, `stem_layer_alt`), all passed. Each standard normal contains 13 measurements; each join-edge mode contains 14. The edge-pass receipt has no failures. The edge-fail receipt's sole runner failure is `join200_edgefail_probe: sections: internal join adjacent sample gap > .03 full scale`; measured join delta is `0.030029296875`, side-slope mismatch `0.0`, contrast `10.457519263296449 dB`. The pass edge has `0.029998779296875`, slope `0.0`, contrast `10.457519260400565 dB`. Section `passed` alone denotes section contrast validity; whole-run failure set distinguishes the edge endpoint. No threshold changed in the receipts.
- Every replay receipt's threshold object is identical. Recorded existing constants remain 48,000 Hz; duration tolerance 0.001 s; peak `<0.95`; RMS `>0.001`; seam endpoint `0.03`; seam slope `0.001`; section contrast `6 dB`; internal join adjacent delta `0.03`; internal join side-slope mismatch `0.001`; section component amplitude `0.01`; section RMS `0.001`; distinctness minima 0.02 s and 0.1 relative centroid. No thresholds were tuned.
- Canonical artifact inventory compared by SHA-256 to `git show 14cf986:<path>`: **13/13 match**.

| Canonical WAV | SHA-256 |
|---|---|
| `ambience.wav` | `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198` |
| `ambience_alt.wav` | `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc` |
| `impact.wav` | `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc` |
| `impact_alt.wav` | `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6` |
| `movement.wav` | `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d` |
| `movement_alt.wav` | `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639` |
| `stem.wav` | `fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0` |
| `stem_layer.wav` | `ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9` |
| `stem_layer_alt.wav` | `74926bf517298fa241e9960099aca60a728a54c41d9454876366dfe4d90adaa9` |
| `stem_layer_third.wav` | `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445` |
| `stem_sections.wav` | `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702` |
| `ui.wav` | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` |
| `ui_alt.wav` | `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f` |

## Result and limits

The independent replay verifies the narrow runner behavior for the tested native PCM16/PCM24 examples: matching 48 kHz mono PCM16 is accepted, and the matched 48 kHz mono PCM24 sample is rejected with only the explicit PCM16 format failure. The six-record invalid probe and historical flag suite behave as expected; canonical artifacts, five alternate distinctness records, and thresholds remain unchanged. No claim about audibility, rights, engine behavior, or a universal WAV validator is made. **SHONEN box 4 remains open.**
