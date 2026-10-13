# R42 scribe — decoded peak decision table

## Decision scope

LOG declares one numerical fixture-calibration claim: isolate the existing `peak >= .95` level-check route with adjacent decoded PCM16 peak magnitudes. The boundary is `.95 * 32768 = 31129.6`; this pair brackets it, not equality at the threshold. It does not establish audible clipping, headroom quality, production suitability, rights, engine use, publishing, or promotion.

## Decision table

| Decoded absolute PCM16 peak | Decoded normalized peak | Expected runner route | Expected exit / failure list | Evidence status |
|---:|---:|---|---|---|
| 31129 | 31129/32768 = 0.949981689453125 | Pass peak check | exit 0; no failures | Executor's direct measurement confirms this numeric fixture fits. Runner mode and serial replay are pending. |
| 31130 | 31130/32768 = 0.95001220703125 | Fail existing peak check (`peak >= .95`) | exit 1; sole expected failure `level: clipping headroom or near silence` | Executor's direct measurement confirms this numeric fixture fits and isolates the level route. Runner mode and serial replay are pending. |

The executor's decoded WAV inspection reports signed extrema ±31129 and ±31130, respectively; both are 5760-frame, 48 kHz, mono PCM16. Its direct helper measurements report duration 0.12 s, RMS −3.4559832611867107 / −3.455749141202171 dBFS, centroid 1002.249073839976 / 1000.2482261395106 Hz, and no failure on 31129 / only the expected level failure on 31130. Those are **direct `measure()` results**, not runner receipts or CLI exit outcomes.

## Setup versus numeric-fit failures; runner status

No setup error or numeric-fit failure is reported for the executor's final pair. A setup error would mean the invocation/generation/decode did not produce a valid measurement; a numeric-fit failure would mean a successfully measured probe missed a specified RMS, centroid, peak, or ordinary-check target. Do not count either as an expected gate failure. For these files, the observed direct measurements meet the stated numeric targets; only 31130's intended level threshold is a gate failure.

The R42 CLI probe modes, their exit codes/receipts, the 44-run non-author serial replay, and normal-run restore are **pending**. No runner outcome is inferred from the direct helper call.

## Commands and exits available from executor report

The executor reports these exact commands, run from repository root:

```sh
python3 .shokunin/audio/corpus/live/round-42/executor/generate.py
```

Exit **0**. It printed frame counts, signed extrema and SHA-256 values; the WAVs decode to 5760 samples each with peak counts 31129 and 31130.

```sh
python3 -c 'import importlib.util,json,pathlib; p=pathlib.Path(".shokunin/audio/corpus/fixtures/measure_audio.py"); s=importlib.util.spec_from_file_location("measure_audio",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); spec=m.SPECS["ui"]; paths=[pathlib.Path(".shokunin/audio/corpus/live/round-42/executor/ui-peak-31129.wav"),pathlib.Path(".shokunin/audio/corpus/live/round-42/executor/ui-peak-31130.wav")]; print(json.dumps([m.measure("ui",spec,x.resolve()) for x in paths],indent=2))'
```

Exit **0**; direct measurement only, not a CLI/runner test.

No additional shell command was run by this scribe. I rely on the executor report for the exact commands and their exits; runner outcomes remain pending.
