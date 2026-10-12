# Round 8 independent serial replay — verifier report

Verifier role: named non-author replay of the declared companion-layer coverage claim. This report records the serial rerun in this checkout. The first seven attempted replay invocations were malformed. The Python wrapper constructed `bash(f'"""{cmd}"""')`, wrapping the full executable-plus-arguments string as a single shell command token; all seven calls exited **127** (`/usr/bin/bash: line 4: python3 .shokunin/audio/corpus/fixtures/measure_audio.py ...: No such file or directory`). They are setup failures, not test passes, and created no receipts. I then reran these exact seven commands, each passed to `bash` as an unwrapped command string, serially:

```text
python3 .shokunin/audio/corpus/fixtures/measure_audio.py
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid
python3 .shokunin/audio/corpus/fixtures/measure_audio.py
```

The earlier parent receipts are not substituted for this replay.

## Corrected replay

| order | mode | exit | receipt | outcome |
|---:|---|---:|---|---|
| 1 | normal | 0 | `corpus/live/runs/20261012T172620813098Z-normal/measurements.json` | 11 canonical assets; no failures; four SFX variant checks pass |
| 2 | `--probe-layer-flat` | 1 | `corpus/live/runs/20261012T172637297691Z-layer-flat/measurements.json` | Only `flat120_probe` fails its section-contrast gate; flat layer is valid and 0.0 dB contrast |
| 3 | `--probe-flat` | 1 | `corpus/live/runs/20261012T172638021452Z-flat/measurements.json` | Existing flat30 negative control fails its section-contrast gate |
| 4 | `--probe-slope` | 1 | `corpus/live/runs/20261012T172638719794Z-slope/measurements.json` | Existing slope negative control fails loop slope gate |
| 5 | `--probe-failing` | 1 | `corpus/live/runs/20261012T172639377325Z-failing/measurements.json` | Existing failing fixture reports centroid-band and endpoint-seam failures |
| 6 | `--probe-invalid` | 1 | `corpus/live/runs/20261012T172639602990Z-invalid/measurements.json` | All four named expected failures: short section count, corrupt decode, wrong format, odd section count |
| 7 | normal restore | 0 | `corpus/live/runs/20261012T172640257036Z-normal/measurements.json` | 11 canonical assets; no failures; restores clean state |

The initial baseline normal run, also exit 0, was `20261012T172620813098Z-normal`; this is order 1 above, prior to controls.

## Layer measurements and coverage check

The normal receipt reports `stem_layer` as 4.000 s, mono 48 kHz, with no generic failures. Its 120 Hz component amplitudes are 0.01199958745 and 0.05999774520 full scale, with `section_energy_delta_db` 13.9793723 (the implementation uses 20 log10 of component amplitude ratio). The section gate passes. The flat120 control has amplitudes 0.03599720971 in each half, 0.0 dB, valid RMS/floor checks, and the only failure is the 120 Hz section contrast. The flat30 control continues to fail only its corresponding 30 Hz section contrast. Receipts establish only this analytic component contrast; they do not assess the layer's internal transition, audibility, adaptive playback behavior, mix, or perceptual quality. Outer seam metrics compare only the first/last endpoints and adjacent slopes.

Compared every one of the ten canonical WAVs present in baseline commit `75c95d9b0cca34f8da8d7481b445ab6f9f07ebb6` against the current tree by SHA-256: all ten hashes match. Current normal receipt has eleven measurements, including `stem_layer`; all four SFX alternative distinctness checks pass. The flat120 probe is generated scratch, not a canonical production asset. Existing numeric thresholds remain fixture-local; no threshold tuning or perceptual claim is made.

## Bounded outcome

Independent replay supports that the new source-generated time-aligned numeric companion layer is added without altering the ten previous assets, and that its matched flat120 control is rejected by the intended analytic section-contrast check. It does not prove runtime synchronization, engine integration, useful adaptive audio, production quality, rights status, or general audio quality. Round-level axis adjudication remains with the separate adjudicator.


## Hash and threshold/source audit

For the ten prior assets, I obtained the baseline file list with `git ls-tree --name-only 75c95d9:.shokunin/audio/corpus/artifacts`, then for each listed path ran `git show 75c95d9:.shokunin/audio/corpus/artifacts/<name> | sha256sum`; I compared each resulting digest with Python `hashlib.sha256(Path(...).read_bytes()).hexdigest()` for the current canonical WAV. All ten matched. Candidate checks used `sha256sum` on `.shokunin/audio/corpus/artifacts/stem_layer.wav`, `corpus/live/round-8/stem_layer_candidate.wav`, `corpus/live/round-8/flat120_candidate.wav`, and generated `corpus/live/round-8/flat120_probe.wav`: canonical layer and candidate both `ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9`; flat candidate and generated probe both `bfc71f84f6d9bae0f5e9b1d786d10bc7becd2e766b406fe5583cfd5fcf0af1bd`.

I inspected `git diff 75c95d9 -- .shokunin/audio/corpus/fixtures/measure_audio.py`. The existing constants remain: 48,000 Hz, ±.001 s duration, peak .95, RMS .001, endpoint .03, slope .001, component amplitude/RMS floors .01/.001, section contrast 6 dB, distinctness .020 s / 10%, and centroid bands. The 30 Hz path still uses the default component argument and the old `--probe-flat` receipt passes its equal-amplitude 30 Hz control to the expected 0 dB rejection. Changes parameterize the component/bin and add the 120 Hz layer/probe; no numeric threshold was altered. I did not run a separate historical-baseline executable replay for this round; baseline comparison here is source diff plus the corrected current 30 Hz flat-control replay.
