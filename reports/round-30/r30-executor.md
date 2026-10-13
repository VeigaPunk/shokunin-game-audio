# Round 30 executor — byte-swapped UI centroid orientation

## Result

The pre-integration measured pair crosses the existing baseline-denominator `.10` threshold in the declared orientation test. I copied the two existing round-29 source-generated WAVs byte-for-byte into executor scratch, then assigned the same bytes to the opposite baseline/alternate roles. The forward pair (baseline k=1.00, alternate k=.95) gives relative centroid delta `0.09901901500217196`, so the existing distinctness OR comparator rejects it (duration delta 0). The reverse pair (baseline k=.95, alternate k=1.00) gives `0.10990133715464667`, so it passes (duration delta 0). All four individual files pass the existing canonical `SPECS["ui"]` ordinary checks: 48 kHz mono PCM16, .120 s, valid level and centroid band. No source or thresholds changed.

This is only the numeric orientation effect of the existing baseline-denominator formula on these two files. It is not a perceptual similarity, symmetry-norm, quality, codec-generalization, rights, engine, publishing, or promotion claim.

## Byte identity

SHA-256:

- forward baseline (k=1.00) = reverse alternate (k=1.00): `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9`
- forward alternate (k=.95) = reverse baseline (k=.95): `6e626b9b5b177cd6f7ba986758b12ec612cf003f9947bd170b766f1652d9bac2`

All four scratch files are 11,564 bytes. Direct measurements are in `corpus/live/round-30/executor/measurements.json`.

## Commands and exits

1. Copied the already generated original pair into scratch and duplicated them with role-swapped names using Python `shutil.copyfile`; exit 0 (REPL operation). No WAV generation or edits to source fixtures were needed: the declared round-29 pair already has the exact requested 5760-frame, 48 kHz mono PCM16 UI waveforms at k=1/.95.
2. Initial direct project-measure invocation used relative scratch paths; **exit 1**, setup/path failure (`ValueError`: relative path was not under project corpus root). Excluded from measurement evidence. Exact command:

```sh
python3 -c "import importlib.util,json,pathlib; p=pathlib.Path('.shokunin/audio/corpus/fixtures/measure_audio.py'); s=importlib.util.spec_from_file_location('project_measure',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); d=pathlib.Path('.shokunin/audio/corpus/live/round-30/executor'); a=m.measure('forward_base',m.SPECS['ui'],d/'forward-base.wav'); b=m.measure('forward_alt',m.SPECS['ui'],d/'forward-alt.wav'); c=m.measure('reverse_base',m.SPECS['ui'],d/'reverse-base.wav'); e=m.measure('reverse_alt',m.SPECS['ui'],d/'reverse-alt.wav'); out={'measurements':{'forward_base':a,'forward_alt':b,'reverse_base':c,'reverse_alt':e},'forward_delta':abs(b['spectral_centroid_hz']-a['spectral_centroid_hz'])/a['spectral_centroid_hz'],'reverse_delta':abs(e['spectral_centroid_hz']-c['spectral_centroid_hz'])/c['spectral_centroid_hz']}; (d/'measurements.json').write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out))"
```

3. Corrected direct project-measure invocation by resolving scratch directory to absolute path; **exit 0**. It imported `measure_audio.py` and used its `measure(..., SPECS["ui"], path)` for each of the four WAV files. Exact command:

```sh
python3 -c "import importlib.util,json,pathlib; p=pathlib.Path('.shokunin/audio/corpus/fixtures/measure_audio.py'); s=importlib.util.spec_from_file_location('project_measure',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); d=pathlib.Path('.shokunin/audio/corpus/live/round-30/executor').resolve(); a=m.measure('forward_base',m.SPECS['ui'],d/'forward-base.wav'); b=m.measure('forward_alt',m.SPECS['ui'],d/'forward-alt.wav'); c=m.measure('reverse_base',m.SPECS['ui'],d/'reverse-base.wav'); e=m.measure('reverse_alt',m.SPECS['ui'],d/'reverse-alt.wav'); out={'measurements':{'forward_base':a,'forward_alt':b,'reverse_base':c,'reverse_alt':e},'forward_delta':abs(b['spectral_centroid_hz']-a['spectral_centroid_hz'])/a['spectral_centroid_hz'],'reverse_delta':abs(e['spectral_centroid_hz']-c['spectral_centroid_hz'])/c['spectral_centroid_hz']}; (d/'measurements.json').write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out))"
```

4. SHA-256 calculation on four scratch WAVs via Python `hashlib.sha256(path.read_bytes())`; exit 0.
