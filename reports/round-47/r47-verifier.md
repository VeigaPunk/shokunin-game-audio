# Round 47 non-author verifier — fresh 54-command replay

## Verdict

**The declared UI upper-centroid calibration bracket reproduces on current source.** I serially executed all 54 runner commands and verified 54 distinct, newly created receipt paths. There were **23 exit 0 / 31 expected fixture-validation exit 1** results, with no setup failures. Sequence: initial normal (#1); new upper-centroid below/above probes (#2–#3); the complete R46 52-command sequence #2–#52 shifted to #4–#54, ending with normal (#54). The prior52 subset (#1 and #4–#54) is **22 exit 0 / 30 expected exit 1**, matching the historical R46 replay counts. No historical or author-run receipt was reused.

The below probe exited 0 with no failures; above exited 1 with its sole `spectrum: centroid outside fixture band` failure. The normal first and last receipts contain exactly the same 17 canonical measurements and no failures. This verifies a numerical gate-level bracket, **not causal single-variable spectral isolation**.

## New upper-bound probe receipts

| Probe | SHA-256 | Frames / format | Duration | Peak FS | RMS dBFS | Project SoX-f32 whole-wave centroid | Result |
|---|---|---|---:|---:|---:|---:|---|
| below | `b04d00164fc57a97a0cdd591a589a44792d0084ba66cdc2118989183ae22fc17` | 5760; 48 kHz mono PCM16 | 0.12 s | 0.279754638671875 | -18.327854015660773 | 3999.922795974407 Hz | exit 0; no failures |
| above | `8f6dd0411d240e46ea619c32e3c344b8c03491d860ebc6ab32b248cbd51e4383` | 5760; 48 kHz mono PCM16 | 0.12 s | 0.2789306640625 | -18.32785200392649 | 4000.427101452783 Hz | exit 1; sole spectrum failure |

New fresh runner receipts:
- #2 below: `.shokunin/audio/corpus/live/runs/20261013T071531697506Z-ui-upper-centroid-below/measurements.json`
- #3 above: `.shokunin/audio/corpus/live/runs/20261013T071532741662Z-ui-upper-centroid-above/measurements.json`

Both pass 48 kHz mono PCM16 format, .12 s duration, peak < .95 and RMS >= .001. The below receipt's additional `ui_upper_centroid_below_probe` metric is 3999.922795974407 Hz with no failures; above's `ui_upper_centroid_above_probe` metric is 4000.427101452783 Hz and only the ordinary spectrum failure. Nominal oscillator frequencies 3983/3984 Hz are not measured centroids. No exact 4000 Hz equality is tested.

## Source diff, historical controls, and preservation

Clean-before is `90c4aea`. Against it, source changes are confined to two opt-in upper-centroid modes in `corpus/fixtures/build_artifacts.py` and `measure_audio.py`. `SPECS["ui"]`, the ordinary inclusive `250 <= centroid <= 4000` comparator, thresholds, and other checks are unchanged. The new flags are mutually exclusive with other probe modes. `git diff --check 90c4aea -- .shokunin/audio/corpus/fixtures/build_artifacts.py .shokunin/audio/corpus/fixtures/measure_audio.py` exited 0. `git diff --quiet 90c4aea -- .shokunin/audio/corpus/artifacts` exited 0.

Fresh normal #1/#54 measurements are identical JSON: 17 canonical measurements, no failures. I SHA-256 checked all 17 canonical WAVs against the historical R46 verifier table; every digest matched. Preserved historical checks carried in the R46 baseline include five generic `_alt` comparisons, four family groups/eight comparisons, thresholds/sections, and eight invalid-fixture outcomes. The full shifted prior52 sequence was rerun and reproduced its 22/30 expected exit count. These prior controls are context, not evidence for the new upper-bound result.

The R47 executor's earlier nominal 3950/4050 and 3980/4020 pairs were **valid but broad numeric brackets**, not failed numeric fits. An alternate independently generated pair had different SHAs but the same polarity. Helper relative-path errors and the executor's redundant path correction/report text are setup/report issues, not gate results. They are not confused with the fresh replay: this replay had no setup failures. All 54 exact commands, exits, fresh receipt paths, and reported failures are listed below.

## Complete serial command ledger

| # | Exact command | Exit | New receipt | Recorded failures |
|---:|---|---:|---|---|
| 1 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T071530637991Z-normal/measurements.json` | none |
| 2 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-upper-centroid-below` | 0 | `.shokunin/audio/corpus/live/runs/20261013T071531697506Z-ui-upper-centroid-below/measurements.json` | none |
| 3 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-upper-centroid-above` | 1 | `.shokunin/audio/corpus/live/runs/20261013T071532741662Z-ui-upper-centroid-above/measurements.json` | ui_upper_centroid_above_probe: ['spectrum: centroid outside fixture band'] |
| 4 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-absolute-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T071533807536Z-ui-absolute-centroid-below/measurements.json` | ui_absolute_centroid_below_probe: ['spectrum: centroid outside fixture band'] |
| 5 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-absolute-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T071534870153Z-ui-absolute-centroid-above/measurements.json` | none |
| 6 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-tolerance-5713` | 0 | `.shokunin/audio/corpus/live/runs/20261013T071535940542Z-ui-lower-tolerance-5713/measurements.json` | none |
| 7 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-tolerance-5711` | 1 | `.shokunin/audio/corpus/live/runs/20261013T071537011059Z-ui-lower-tolerance-5711/measurements.json` | ui_lower_tolerance_5711_probe: ['duration: outside ±1 ms'] |
| 8 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-tolerance-5807` | 0 | `.shokunin/audio/corpus/live/runs/20261013T071538078953Z-ui-tolerance-5807/measurements.json` | none |
| 9 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-tolerance-5809` | 1 | `.shokunin/audio/corpus/live/runs/20261013T071539141791Z-ui-tolerance-5809/measurements.json` | ui_tolerance_5809_probe: ['duration: outside ±1 ms'] |
| 10 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-crest-46` | 1 | `.shokunin/audio/corpus/live/runs/20261013T071540196308Z-ui-crest-46/measurements.json` | ui_crest_46_probe: ['level: clipping headroom or near silence'] |
| 11 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-crest-47` | 0 | `.shokunin/audio/corpus/live/runs/20261013T071541253808Z-ui-crest-47/measurements.json` | none |
| 12 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-peak-31129` | 0 | `.shokunin/audio/corpus/live/runs/20261013T071542323777Z-ui-peak-31129/measurements.json` | none |
| 13 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-peak-31130` | 1 | `.shokunin/audio/corpus/live/runs/20261013T071543363318Z-ui-peak-31130/measurements.json` | ui_peak_31130_probe: ['level: clipping headroom or near silence'] |
| 14 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-slope-32` | 0 | `.shokunin/audio/corpus/live/runs/20261013T071544437593Z-outer-slope-32/measurements.json` | none |
| 15 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-slope-33` | 1 | `.shokunin/audio/corpus/live/runs/20261013T071545498186Z-outer-slope-33/measurements.json` | slope_33_probe: ['loop seam: slope mismatch > .001 full scale per sample'] |
| 16 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-endpoint-983` | 0 | `.shokunin/audio/corpus/live/runs/20261013T071546567555Z-outer-endpoint-983/measurements.json` | none |
| 17 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-endpoint-984` | 1 | `.shokunin/audio/corpus/live/runs/20261013T071547638401Z-outer-endpoint-984/measurements.json` | endpoint_984_probe: ['loop seam: endpoint jump > .03 full scale'] |
| 18 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-orientation-forward` | 0 | `.shokunin/audio/corpus/live/runs/20261013T071548747260Z-ambience-orientation-forward/measurements.json` | none |
| 19 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-orientation-reverse` | 1 | `.shokunin/audio/corpus/live/runs/20261013T071549877746Z-ambience-orientation-reverse/measurements.json` | ambience_orientation_alt: ['distinctness: duration < .020 s and centroid delta < 10%'] |
| 20 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T071550996181Z-ambience-centroid-above/measurements.json` | none |
| 21 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T071552123026Z-ambience-centroid-below/measurements.json` | ambience_probe_alt: ['distinctness: duration < .020 s and centroid delta < 10%'] |
| 22 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-mixed-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T071553210660Z-ui-mixed-pass/measurements.json` | none |
| 23 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-joint-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T071554302094Z-ui-joint-below/measurements.json` | ui_joint_below_alt: ['distinctness: duration < .020 s and centroid delta < 10%'] |
| 24 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-forward` | 1 | `.shokunin/audio/corpus/live/runs/20261013T071555400281Z-ui-orientation-forward/measurements.json` | ui_orientation_forward_alt: ['distinctness: duration < .020 s and centroid delta < 10%'] |
| 25 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-reverse` | 0 | `.shokunin/audio/corpus/live/runs/20261013T071556489442Z-ui-orientation-reverse/measurements.json` | none |
| 26 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T071557589550Z-ui-lower-centroid-below/measurements.json` | ui_lower_centroid_below_alt: ['distinctness: duration < .020 s and centroid delta < 10%'] |
| 27 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T071558682507Z-ui-lower-centroid-above/measurements.json` | none |
| 28 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T071559775320Z-ui-centroid-below/measurements.json` | ui_centroid_below_alt: ['distinctness: duration < .020 s and centroid delta < 10%'] |
| 29 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T071600867381Z-ui-centroid-above/measurements.json` | none |
| 30 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T071601964201Z-ui-duration-below/measurements.json` | ui_duration_below_alt: ['distinctness: duration < .020 s and centroid delta < 10%'] |
| 31 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-at` | 0 | `.shokunin/audio/corpus/live/runs/20261013T071603066763Z-ui-duration-at/measurements.json` | none |
| 32 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-clone` | 1 | `.shokunin/audio/corpus/live/runs/20261013T071604150437Z-ui-clone/measurements.json` | ui_clone_alt: ['distinctness: duration < .020 s and centroid delta < 10%'] |
| 33 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T071605237324Z-layer-third-join-edge-pass/measurements.json` | none |
| 34 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T071606307408Z-layer-third-join-edge-fail/measurements.json` | join200_edgefail_probe: ['sections: internal join adjacent sample gap > .03 full scale'] |
| 35 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T071607405704Z-layer-third-join/measurements.json` | join200_probe: ['sections: internal join adjacent sample gap > .03 full scale'] |
| 36 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T071608459659Z-layer-third-slope-edge-pass/measurements.json` | none |
| 37 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T071609527513Z-layer-third-slope-edge-fail/measurements.json` | edgefail_probe: ['sections: internal join side slope mismatch > .001 full scale per sample'] |
| 38 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T071610596047Z-layer-third-slope/measurements.json` | slope200_probe: ['sections: internal join side slope mismatch > .001 full scale per sample'] |
| 39 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | 1 | `.shokunin/audio/corpus/live/runs/20261013T071611673639Z-layer-alt-reverse/measurements.json` | reverse180_probe: ['sections: 180 Hz component amplitude contrast < 6 dB or invalid'] |
| 40 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T071612746549Z-layer-alt-slope/measurements.json` | slope180_probe: ['sections: internal join side slope mismatch > .001 full scale per sample'] |
| 41 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T071613823555Z-layer-alt-join/measurements.json` | join180_probe: ['sections: internal join adjacent sample gap > .03 full scale'] |
| 42 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T071614909393Z-layer-alt-flat/measurements.json` | flat180_probe: ['sections: 180 Hz component amplitude contrast < 6 dB or invalid'] |
| 43 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T071615975118Z-layer-slope/measurements.json` | layer_slope_probe: ['sections: internal join side slope mismatch > .001 full scale per sample'] |
| 44 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T071617052564Z-layer-join/measurements.json` | join_probe: ['sections: internal join adjacent sample gap > .03 full scale'] |
| 45 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T071618128272Z-flat/measurements.json` | flat30_probe: ['sections: 30 Hz component amplitude contrast < 6 dB or invalid'] |
| 46 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T071619212421Z-layer-flat/measurements.json` | flat120_probe: ['sections: 120 Hz component amplitude contrast < 6 dB or invalid'] |
| 47 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T071620273288Z-slope/measurements.json` | slope_probe: ['loop seam: slope mismatch > .001 full scale per sample'] |
| 48 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `.shokunin/audio/corpus/live/runs/20261013T071621278252Z-failing/measurements.json` | ambience: ['spectrum: centroid outside fixture band', 'loop seam: endpoint jump > .03 full scale'] |
| 49 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `.shokunin/audio/corpus/live/runs/20261013T071621621573Z-invalid/measurements.json` | short_sections: section count; corrupt: decode; wrong_format: format; odd_sections: section count; native16_probe: None; native24_probe: format; stereo48_probe: format; mono441_probe: format |
| 50 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T071622625268Z-normal/measurements.json` | none |
| 51 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T071623622112Z-normal/measurements.json` | none |
| 52 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T071624634920Z-normal/measurements.json` | none |
| 53 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T071625650420Z-normal/measurements.json` | none |
| 54 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T071626664428Z-normal/measurements.json` | none |

## Limits

This supports only the numerical fixture-gate bracket against the existing ordinary absolute UI band. The tones differ in nominal frequency, quantized samples, and full FFT distributions, so the evidence does not isolate one causal variable. It does not establish exact-4000 equality, timbre, audio quality, perception, production suitability, rights, engine integration, publishing, promotion, or rank. No source, LOG, SCORECARD, canonical artifact, other report, commit, or push was changed by this verifier. I wrote only this report; the runner generated fresh receipts under `corpus/live/runs/`.
