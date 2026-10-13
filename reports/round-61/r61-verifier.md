# R61 non-author verifier — 82-command serial replay

## Bounded scope

Exactly 82 runner commands were executed serially once each on this host (devin), each producing a distinct, new receipt path: **43 exit 0 / 39 expected validation exit 1**. The designated R60 80-command sequence was replayed as commands #1 and #4–#82: **42 exit 0 / 38 exit 1**, and all 80 matched the R60 designated ledger exactly — command text, exit status, and complete parsed JSON receipt. The two new R61 modes occupy commands #2–#3: `--probe-ui-extensible-valid-17-r61` exited 1 with a receipt; `--probe-ui-extensible-valid-16-r61` exited 0 clean. No author, historical, or rehearsal receipt path was reused; no extra or missing receipts occurred.

The test does **not** establish universal valid-bit enforcement, spec-mandated reader behavior, conforming valid-bit metadata, precision, fidelity, audibility, quality, production suitability, rights, engine behavior, publishing, or promotion. `wValidBitsPerSample=17` is a malformed declaration (valid bits > 16-bit container depth), **not** a conforming positive test vector. Results are limited to the specified files, installed ffprobe n9.0.1/SoX_ng v14.8.0.1, the unchanged project measurement gate, and this host. I made no source changes, commits, or pushes; this verifier report is the only file I wrote — the runner generated the receipts.

## Replay method and receipt freshness

`corpus/live/runs/` was snapshotted before replay (2,369 pre-existing dirs) and after. Exactly **82 new directories** appeared, one per executed command, in monotonically increasing timestamps `20261013T165521565727Z`–`20261013T165707012269Z`; the new set equals my 82 receipt paths exactly — zero duplicates, zero extras, zero pre-existing paths reused. Each command's stdout JSON `receipt`/`failures` payload was captured per command; all 82 parsed cleanly with no receiptless runner errors and no retries.

## New-mode receipts (independent parse)

- Command #2 `--probe-ui-extensible-valid-17-r61` → exit **1**, receipt `20261013T165522836463Z-ui-extensible-valid-17-r61/measurements.json`, mode `probe-ui-extensible-valid-17-r61`. Sole failing entry across the whole receipt: `ui_extensible_valid_17_r61_probe` with exactly `['format: expected PCM16', 'duration: outside ±1 ms', 'level: clipping headroom or near silence', 'spectrum: centroid outside fixture band']`. All 17 canonical measurements and every distinctness/family/section record carry empty failures. Probe measurement: `pcm_s24le`, 24 bits/sample, 48,000 Hz mono, duration `0.08` s, peak `0.992279052734375`, RMS `-7.797933085328953` dBFS, centroid `12180.625368025178` Hz, bandwidth `7171.544640451181` Hz — all identical to the author's recorded values.
- Command #3 `--probe-ui-extensible-valid-16-r61` → exit **0**, receipt `20261013T165524127908Z-ui-extensible-valid-16-r61/measurements.json`, zero failures. Probe measurement: `pcm_s16le`, 16 bits, duration `0.12` s, peak `0.088226318359375`, RMS `-25.58802390050348` dBFS, centroid `1250.916113037482` Hz, bandwidth `585.4256545144334` Hz — identical to the author's values.
- Both of my new-mode receipts are **complete-JSON identical to the author's own receipts** (`164943766168Z-ui-extensible-valid-17-r61`, `165003992146Z-ui-extensible-valid-16-r61`). The exit-1 outcome is a gate validation result captured in the receipt, not a decoder crash.

## Prior-80 subset, normal equality, and author cross-check

Mapping: my #1 ↔ R60 #1 (normal); my #4–#82 ↔ R60 #2–#80. All **80/80** compared pairs match on exact command text, exit status, and complete parsed receipt JSON (the R60 ledger itself carries 42 exit 0 / 38 exit 1). My six normal receipts equal R60's normal JSON; the author's R61 normal receipt `165005333529Z-normal` is likewise identical to R60 normal `132816640667Z-normal`, and the author's prior-mode spot check `165033697535Z-ui-extensible-valid-0-r60` is identical to the R60 designated valid0 receipt — consistent with the author's deterministic-rebuild claim (regenerated R60 WAV SHAs `5ab169fc…`/`d7f08d65…` recorded there match R60's published values).

Unchanged controls verified inside the identical normal receipts: 17 canonical measurement entries; five generic `_alt` distinctness comparisons; two comparisons in each of the ui/impact/movement/ambience family maps; section records for `stem_sections`, `stem_layer`, `stem_layer_alt`, `stem_layer_third`; the eight invalid-battery classifications (`short_sections` section count, `corrupt` decode, `wrong_format` format, `odd_sections` section count, `native16_probe` expected pass, `native24_probe`/`stereo48_probe`/`mono441_probe` format); and the unchanged threshold block (48,000 Hz; duration ±0.001 s; peak <0.95; RMS >0.001; existing centroid bands; loop endpoint ≤0.03; loop slope ≤0.001; section contrast ≥6 dB; component amplitude/RMS minima; join delta/slope limits; distinctness duration/centroid limits). Canonical-17 metric ledger (duration, peak, RMS, centroid) matches the R60 published table entry-for-entry, e.g. `ui` 0.12 s / 0.375946044921875 / −19.991687666366516 / 966.8966593379727; `stem_layer_third` 4.0 s / 0.04998779296875 / −31.66724765274306 / 287.93805923844434.

The 39 exit-1 outcomes are expected validation failures recorded in their receipts (38 inherited prior cases including the invalid battery, plus the new valid17 case), not decoder/setup failures.

## Byte-exact evidence and independent tool observations

Integrated `corpus/live/round-61/pair_valid_{17,16}.wav`, each 11,588 bytes:

| file | SHA-256 | wValidBitsPerSample |
|---|---|---:|
| `pair_valid_17.wav` | `15cadf242eff13ede3ff25b992f4410ec89a76a9814e2afad346b4052eb63fe4` | 17 |
| `pair_valid_16.wav` | `2c5e244fb19bed5f6abdaa605ae503dd6685f88cb440de93a4cd313959591d00` | 16 |

I confirmed: **only offset 38 differs** (0x11 vs 0x10); both parse as RIFF/WAVE fmt40, tag `0xfffe`, mono, 48,000 Hz, 16-bit container, cbSize 22, mask `0x4`, PCM subtype GUID `0100000000001000800000aa00389b71`; identical payload SHA-256 `7ebc75f1e6f7af3533113826b7cdbfe61813d7ca6c55d53fefc00a4cd5b10cc2`.

Independent tool invocations on this host (fresh, not the author's):

- ffprobe `pair_valid_17.wav` exit 0: `codec_name=pcm_s24le`, `sample_fmt=s32`, `bits_per_sample=24`, `bits_per_raw_sample=24`, duration `0.080000` — ffprobe reclassifies the stream to 24-bit when declared valid bits exceeds the 16-bit container.
- ffprobe `pair_valid_16.wav` exit 0: `pcm_s16le`, `s16`, 16 bits, `0.120000`.
- SoX f32 decode: valid17 → 3,839 samples (`15356` bytes), valid16 → 5,760 samples. My freshly decoded f32 SHAs `3cda59787933bc3057c7db939382a05a247fc56f2f0f726325d6fe4ce51e707c` / `407e8c22c48ae31952ab5ad117681c7e54148d8f6cebcd435033ac751b6f9a97` are **byte-identical to the author's kept artifacts** `valid17.f32`/`valid16.f32`. Decoded vectors differ in length; the valid17 rejection follows from the reclassified stream, not from the predicate inspecting the valid-bits field directly.

## Integrated diff against clean-before

Compared working tree against clean-before `cd62e6d` (R60 final). `git diff --stat`: `build_artifacts.py` +19/−1, `measure_audio.py` +12/−4 (31+/5− total) — matching the author's stated numbers. The diff is additive-only: two new argparse flags, the mutual-exclusion sum extended by the same two, a new deterministic builder `build_ui_extensible_valid17_probe()`, one new measurement block on `live/round-61/pair_valid_{17,16}.wav` under the existing UI spec, and the new `mode`/`suffix` chain heads placed ahead of the R60 heads. `format_failures()`, `SPECS`, all thresholds, the canonical 17, and all prior probe modes are untouched. Working tree carries the changes uncommitted (`M` on both fixture scripts), consistent with the author's "nothing was committed".

## Agreement with author claims

Every executed-evidence claim in `r61-author.md` reproduced exactly: valid17 exit 1 with receipt and the four named failures on the sole failing entry; valid16 exit 0 clean; normal receipt identical to R60 normal; replay shape 82 commands → 43 exit 0 / 39 exit 1; WAV SHAs, offset-38-only difference, payload SHA, ffprobe reclassification (`pcm_s24le`, 0.08 s), SoX decode lengths and f32 SHAs; additive-only diff stats; uncommitted state. **No disagreement found.** Naming note: the R61 prior ledger is R60's **80-command designated set (42/38)**, reproduced as an exact complete-JSON subset; the task brief's "prior-78 (40/38)" phrasing describes R60's own prior subset, not the R61 replay target.

## UNKNOWNs

- Whether ffmpeg's 17→24-bit rounding is spec-mandated, heuristic, or version-specific; no WAV spec was consulted and no other decoder/host was tested.
- Why SoX's ffmpeg-backend decode yields 3,839 samples rather than the arithmetic 3,840 (11,520/3); the one-frame difference is unexplained and reproduced identically for author and verifier.
- Whether other representable values >16 (e.g. 24, 32) behave identically; only 17 was probed.
- I did not re-run `python3 -m py_compile`/`git diff --check` as gate steps; the diff shown above was inspected directly and all runner invocations succeeded.

## Exact 82-command serial ledger

Exit-1 entries are expected validation outcomes, not setup errors. Every path below is unique and new.

| # | Exact command | Exit | Fresh receipt path | Failure / classification |
|---:|---|---:|---|---|
| 01 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `corpus/live/runs/20261013T165521565727Z-normal/measurements.json` | none |
| 02 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-valid-17-r61` | 1 | `corpus/live/runs/20261013T165522836463Z-ui-extensible-valid-17-r61/measurements.json` | ui_extensible_valid_17_r61_probe: format: expected PCM16; duration: outside ±1 ms; level: clipping headroom or near silence; spectrum: centroid outside fixture band |
| 03 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-valid-16-r61` | 0 | `corpus/live/runs/20261013T165524127908Z-ui-extensible-valid-16-r61/measurements.json` | none |
| 04 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-valid-0-r60` | 0 | `corpus/live/runs/20261013T165525376108Z-ui-extensible-valid-0-r60/measurements.json` | none |
| 05 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-valid-16-r60` | 0 | `corpus/live/runs/20261013T165526645328Z-ui-extensible-valid-16-r60/measurements.json` | none |
| 06 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-valid-13-r59` | 0 | `corpus/live/runs/20261013T165527954115Z-ui-extensible-valid-13-r59/measurements.json` | none |
| 07 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-valid-16-r59` | 0 | `corpus/live/runs/20261013T165529271720Z-ui-extensible-valid-16-r59/measurements.json` | none |
| 08 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-valid-14-r58` | 0 | `corpus/live/runs/20261013T165530608083Z-ui-extensible-valid-14-r58/measurements.json` | none |
| 09 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-valid-16-r58` | 0 | `corpus/live/runs/20261013T165531879395Z-ui-extensible-valid-16-r58/measurements.json` | none |
| 10 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-valid-15` | 0 | `corpus/live/runs/20261013T165533135502Z-ui-extensible-valid-15/measurements.json` | none |
| 11 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-valid-16` | 0 | `corpus/live/runs/20261013T165534431757Z-ui-extensible-valid-16/measurements.json` | none |
| 12 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-mask-zero` | 0 | `corpus/live/runs/20261013T165535725001Z-ui-extensible-mask-zero/measurements.json` | none |
| 13 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-mask-center` | 0 | `corpus/live/runs/20261013T165536976061Z-ui-extensible-mask-center/measurements.json` | none |
| 14 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-pcm16` | 0 | `corpus/live/runs/20261013T165538221270Z-ui-extensible-pcm16/measurements.json` | none |
| 15 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-standard-pcm16-r55` | 0 | `corpus/live/runs/20261013T165539485732Z-ui-standard-pcm16-r55/measurements.json` | none |
| 16 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm32` | 1 | `corpus/live/runs/20261013T165540750934Z-ui-pcm32/measurements.json` | ui_depth_pcm32_r54_probe: format: expected PCM16 |
| 17 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm16-r54` | 0 | `corpus/live/runs/20261013T165541987069Z-ui-pcm16-r54/measurements.json` | none |
| 18 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-float32` | 1 | `corpus/live/runs/20261013T165543196094Z-ui-float32/measurements.json` | ui_depth_float32_r53_probe: format: expected PCM16 |
| 19 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm16-r53` | 0 | `corpus/live/runs/20261013T165544408346Z-ui-pcm16-r53/measurements.json` | none |
| 20 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm8` | 1 | `corpus/live/runs/20261013T165545642696Z-ui-pcm8/measurements.json` | ui_depth_pcm8_r52_probe: format: expected PCM16 |
| 21 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm16-r52` | 0 | `corpus/live/runs/20261013T165546883540Z-ui-pcm16-r52/measurements.json` | none |
| 22 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm24` | 1 | `corpus/live/runs/20261013T165548150309Z-ui-pcm24/measurements.json` | ui_depth_pcm24_probe: format: expected PCM16 |
| 23 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm16` | 0 | `corpus/live/runs/20261013T165549436113Z-ui-pcm16/measurements.json` | none |
| 24 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-channel-stereo` | 1 | `corpus/live/runs/20261013T165550673002Z-ui-channel-stereo/measurements.json` | ui_channel_stereo_probe: format: expected 48kHz mono |
| 25 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-channel-mono` | 0 | `corpus/live/runs/20261013T165551934571Z-ui-channel-mono/measurements.json` | none |
| 26 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-rate-48001` | 1 | `corpus/live/runs/20261013T165553156719Z-ui-rate-48001/measurements.json` | ui_rate_r49_48001_probe: format: expected 48kHz mono |
| 27 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-rate-48000-r49` | 0 | `corpus/live/runs/20261013T165554387184Z-ui-rate-48000-r49/measurements.json` | none |
| 28 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-rate-47999` | 1 | `corpus/live/runs/20261013T165555634945Z-ui-rate-47999/measurements.json` | ui_rate_47999_probe: format: expected 48kHz mono |
| 29 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-rate-48000` | 0 | `corpus/live/runs/20261013T165556885256Z-ui-rate-48000/measurements.json` | none |
| 30 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-upper-centroid-below` | 0 | `corpus/live/runs/20261013T165558132103Z-ui-upper-centroid-below/measurements.json` | none |
| 31 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-upper-centroid-above` | 1 | `corpus/live/runs/20261013T165559383605Z-ui-upper-centroid-above/measurements.json` | ui_upper_centroid_above_probe: spectrum: centroid outside fixture band |
| 32 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-absolute-centroid-below` | 1 | `corpus/live/runs/20261013T165600606817Z-ui-absolute-centroid-below/measurements.json` | ui_absolute_centroid_below_probe: spectrum: centroid outside fixture band |
| 33 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-absolute-centroid-above` | 0 | `corpus/live/runs/20261013T165601844202Z-ui-absolute-centroid-above/measurements.json` | none |
| 34 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-tolerance-5713` | 0 | `corpus/live/runs/20261013T165603074377Z-ui-lower-tolerance-5713/measurements.json` | none |
| 35 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-tolerance-5711` | 1 | `corpus/live/runs/20261013T165604310912Z-ui-lower-tolerance-5711/measurements.json` | ui_lower_tolerance_5711_probe: duration: outside ±1 ms |
| 36 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-tolerance-5807` | 0 | `corpus/live/runs/20261013T165605547949Z-ui-tolerance-5807/measurements.json` | none |
| 37 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-tolerance-5809` | 1 | `corpus/live/runs/20261013T165606788413Z-ui-tolerance-5809/measurements.json` | ui_tolerance_5809_probe: duration: outside ±1 ms |
| 38 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-crest-46` | 1 | `corpus/live/runs/20261013T165608020246Z-ui-crest-46/measurements.json` | ui_crest_46_probe: level: clipping headroom or near silence |
| 39 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-crest-47` | 0 | `corpus/live/runs/20261013T165609232394Z-ui-crest-47/measurements.json` | none |
| 40 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-peak-31129` | 0 | `corpus/live/runs/20261013T165610448881Z-ui-peak-31129/measurements.json` | none |
| 41 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-peak-31130` | 1 | `corpus/live/runs/20261013T165611641797Z-ui-peak-31130/measurements.json` | ui_peak_31130_probe: level: clipping headroom or near silence |
| 42 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-slope-32` | 0 | `corpus/live/runs/20261013T165612869800Z-outer-slope-32/measurements.json` | none |
| 43 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-slope-33` | 1 | `corpus/live/runs/20261013T165614081229Z-outer-slope-33/measurements.json` | slope_33_probe: loop seam: slope mismatch > .001 full scale per sample |
| 44 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-endpoint-983` | 0 | `corpus/live/runs/20261013T165615320881Z-outer-endpoint-983/measurements.json` | none |
| 45 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-endpoint-984` | 1 | `corpus/live/runs/20261013T165616575979Z-outer-endpoint-984/measurements.json` | endpoint_984_probe: loop seam: endpoint jump > .03 full scale |
| 46 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-orientation-forward` | 0 | `corpus/live/runs/20261013T165617867448Z-ambience-orientation-forward/measurements.json` | none |
| 47 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-orientation-reverse` | 1 | `corpus/live/runs/20261013T165619165375Z-ambience-orientation-reverse/measurements.json` | ambience_orientation_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 48 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-centroid-above` | 0 | `corpus/live/runs/20261013T165620458579Z-ambience-centroid-above/measurements.json` | none |
| 49 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-centroid-below` | 1 | `corpus/live/runs/20261013T165621782507Z-ambience-centroid-below/measurements.json` | ambience_probe_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 50 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-mixed-pass` | 0 | `corpus/live/runs/20261013T165623021786Z-ui-mixed-pass/measurements.json` | none |
| 51 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-joint-below` | 1 | `corpus/live/runs/20261013T165624283020Z-ui-joint-below/measurements.json` | ui_joint_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 52 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-forward` | 1 | `corpus/live/runs/20261013T165626153611Z-ui-orientation-forward/measurements.json` | ui_orientation_forward_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 53 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-reverse` | 0 | `corpus/live/runs/20261013T165628197757Z-ui-orientation-reverse/measurements.json` | none |
| 54 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-below` | 1 | `corpus/live/runs/20261013T165630229859Z-ui-lower-centroid-below/measurements.json` | ui_lower_centroid_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 55 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-above` | 0 | `corpus/live/runs/20261013T165632222091Z-ui-lower-centroid-above/measurements.json` | none |
| 56 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-below` | 1 | `corpus/live/runs/20261013T165634171131Z-ui-centroid-below/measurements.json` | ui_centroid_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 57 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-above` | 0 | `corpus/live/runs/20261013T165636137068Z-ui-centroid-above/measurements.json` | none |
| 58 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-below` | 1 | `corpus/live/runs/20261013T165638003908Z-ui-duration-below/measurements.json` | ui_duration_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 59 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-at` | 0 | `corpus/live/runs/20261013T165639393275Z-ui-duration-at/measurements.json` | none |
| 60 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-clone` | 1 | `corpus/live/runs/20261013T165640716758Z-ui-clone/measurements.json` | ui_clone_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 61 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-pass` | 0 | `corpus/live/runs/20261013T165642025420Z-layer-third-join-edge-pass/measurements.json` | none |
| 62 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-fail` | 1 | `corpus/live/runs/20261013T165643323880Z-layer-third-join-edge-fail/measurements.json` | join200_edgefail_probe: sections: internal join adjacent sample gap > .03 full scale |
| 63 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join` | 1 | `corpus/live/runs/20261013T165644566557Z-layer-third-join/measurements.json` | join200_probe: sections: internal join adjacent sample gap > .03 full scale |
| 64 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-pass` | 0 | `corpus/live/runs/20261013T165645918963Z-layer-third-slope-edge-pass/measurements.json` | none |
| 65 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-fail` | 1 | `corpus/live/runs/20261013T165647170182Z-layer-third-slope-edge-fail/measurements.json` | edgefail_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 66 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope` | 1 | `corpus/live/runs/20261013T165648415461Z-layer-third-slope/measurements.json` | slope200_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 67 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | 1 | `corpus/live/runs/20261013T165649613754Z-layer-alt-reverse/measurements.json` | reverse180_probe: sections: 180 Hz component amplitude contrast < 6 dB or invalid |
| 68 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | 1 | `corpus/live/runs/20261013T165650821985Z-layer-alt-slope/measurements.json` | slope180_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 69 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 | `corpus/live/runs/20261013T165652074677Z-layer-alt-join/measurements.json` | join180_probe: sections: internal join adjacent sample gap > .03 full scale |
| 70 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 | `corpus/live/runs/20261013T165653356447Z-layer-alt-flat/measurements.json` | flat180_probe: sections: 180 Hz component amplitude contrast < 6 dB or invalid |
| 71 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 | `corpus/live/runs/20261013T165654625765Z-layer-slope/measurements.json` | layer_slope_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 72 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | `corpus/live/runs/20261013T165655842568Z-layer-join/measurements.json` | join_probe: sections: internal join adjacent sample gap > .03 full scale |
| 73 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `corpus/live/runs/20261013T165657063935Z-flat/measurements.json` | flat30_probe: sections: 30 Hz component amplitude contrast < 6 dB or invalid |
| 74 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `corpus/live/runs/20261013T165658311968Z-layer-flat/measurements.json` | flat120_probe: sections: 120 Hz component amplitude contrast < 6 dB or invalid |
| 75 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `corpus/live/runs/20261013T165659524991Z-slope/measurements.json` | slope_probe: loop seam: slope mismatch > .001 full scale per sample |
| 76 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `corpus/live/runs/20261013T165700681389Z-failing/measurements.json` | ambience: spectrum: centroid outside fixture band; ambience: loop seam: endpoint jump > .03 full scale |
| 77 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `corpus/live/runs/20261013T165701077902Z-invalid/measurements.json` | invalid battery: short_sections=section count, corrupt=decode, wrong_format=format, odd_sections=section count, native16_probe=pass, native24_probe=format, stereo48_probe=format, mono441_probe=format |
| 78 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `corpus/live/runs/20261013T165702258536Z-normal/measurements.json` | none |
| 79 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `corpus/live/runs/20261013T165703398161Z-normal/measurements.json` | none |
| 80 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `corpus/live/runs/20261013T165704628242Z-normal/measurements.json` | none |
| 81 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `corpus/live/runs/20261013T165705843181Z-normal/measurements.json` | none |
| 82 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `corpus/live/runs/20261013T165707012269Z-normal/measurements.json` | none |
