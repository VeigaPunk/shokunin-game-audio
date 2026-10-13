# Round 21 critic — sole-gap boundary and proxy falsification

**Scope:** read-only critic review. I did not edit the builder, runner, canonical fixtures, or scratch WAVs. The only file written for this task is this report.

## Evidence inspected

- `.shokunin/audio/LOG.md`, round-21 declaration: calibration-only proposal; paired internal-gap controls at 983/984 PCM16 counts; strict `> .03` gate; preserve 13 canonical hashes, five `_alt` checks and 17 prior replay modes.
- `.shokunin/audio/corpus/fixtures/measure_audio.py`: `section_contrast()` decodes through SoX to float32, measures gap `abs(samples[96000]-samples[95999])`, side-slope mismatch from the two neighboring differences, and 200 Hz component contrast. The runner appends a gap failure only for `> .03`; the generic centroid band for `stem_layer_third` is 100–2000 Hz. This is a fixture-local numerical gate, not a perception test.
- Existing non-author receipt `.shokunin/audio/corpus/live/runs/20261012T232009162006Z-layer-third-join/measurements.json` (Round 20): `join200_probe` is valid, with 200 Hz contrast 10.4575192633 dB, internal gap 0.030029296875 FS, internal side-slope 0, centroid 1209.6397189 Hz, and exactly one failure: internal gap > .03. Its WAV is `.shokunin/audio/corpus/live/round-20/join200_probe.wav`, SHA-256 `5194bd8e2cc9929d5287d3ddd910d32b3c24aa2f76ba66f267d83dbbe84d97fd`.
- `.shokunin/audio/reports/round-20/r20-verifier.md` independently reports that same sole-gap runner result. This is historical evidence for the 984-count side, not replay of round-21 controls.

## Boundary challenge

The 984-count differential is not a sample value: the existing WAV's decoded PCM16 values around the join are `[-290, -145, 839, 984]` at frames `[95998:96002]`. Thus the measured join jump is `839 - (-145) = 984` counts, or `984/32768 = 0.030029296875` FS, and strict `>` rejects it.

I evaluated the paired offset `-1` on an in-memory copy of that PCM array, adding the same -1 count to frames 96000 and 96001. That gives `[-290, -145, 838, 983]`, a 983-count jump `0.029998779296875` FS, and side-slope mismatch 0. This is a mathematical/NumPy proxy, **not a written 983 WAV or an integrated runner pass**. The existing 984 receipt plus this paired arithmetic is consistent with the proposed adjacent PCM-grid bracket, but does not establish the declared two-mode replay.

The integer thresholds do produce an adjacent-grid bracket around the literal decimal `.03`: `983/32768 < .03 < 984/32768`. The claim is narrow: strict comparator behavior on this 48 kHz PCM16 fixture and SoX decode path. It does not establish a universal tolerance, perceptual threshold, or robustness across encoders/representations.

## Falsification attempts and limits

- **Sole-gap isolation:** the existing 984 runner receipt supports isolation for that one waveform: contrast/validity pass, centroid is within its broad band, side slope is 0, and the failure list contains only the gap check. It does not prove that an arbitrary perturbation at this join will preserve those guards. The 983 paired proxy is not a runner receipt, so positive-side isolation remains unverified here.
- **Centroid:** the existing 984 signal includes the extra 220/330 Hz bed (per `r20` builder/report); it is not a waveform-identical edit of the canonical third layer. Its measured centroid is about 790.36 Hz below the 2000 Hz ceiling, so centroid does not confound this particular negative. It cannot establish that every 984-count perturbation, especially on another baseline, stays inside the centroid band.
- **Side slope:** equal offsets on the two frames preserve their difference and therefore preserve the measured side-slope value, as the in-memory 983 arithmetic shows. This is a local algebraic property, not independent runner evidence; it says nothing about slope behavior under a one-frame edit or other waveform baselines.
- **Threshold calibration:** the controls can demonstrate comparator polarity/grid arithmetic, not that `.03` is calibrated to audibility. The existing `section.passed: true` field means section validity/contrast only; the complete runner failure list is authoritative for gap isolation.
- **Integration:** at the inspected source snapshot I found no 983/984 edge-specific CLI mode. Do not count a scratch candidate, arithmetic calculation, or Round-20 receipt as proof that both declared Round-21 modes are wired and replayed. I did not run the full suite; independent non-author replay and receipt inspection remain necessary.

## Commands / exit codes

| Exact shell command | Exit | Use / limitation |
|---|---:|---|
| `python3 -c 'import wave,numpy as np; p=".shokhun/audio/corpus/live/round-20/join200_probe.wav"; w=wave.open(p,"rb"); x=np.frombuffer(w.readframes(w.getnframes()),dtype="<i2").copy(); w.close(); print("base",x[95998:96002].tolist()); print(*[(d,(lambda a:(a.__setitem__([96000,96001],a[[96000,96001]]+d),a[95998:96002].tolist(),abs(int(a[96000])-int(a[95999]))/32768,abs((int(a[96001])-int(a[96000]))-(int(a[95999])-int(a[95998])))/32768))(x.copy())) for d in (-1,0)],sep="\n")'` | 0 | Read the existing WAV and calculate in-memory paired boundary proxies. Output: base `[-290,-145,839,984]`; offsets -1/0 yield `[...838,983]` gap `.029998779296875`, slope 0 / `[...839,984]` gap `.030029296875`, slope 0. No file was written; not a runner execution. |
| `python3 .shokhun/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join` | 1 (historical non-author receipt, Round 20) | Receipt `20261012T232009162006Z-layer-third-join/measurements.json`; sole 984-count-gap failure. I did not rerun this command in this critic task. |

**Assessment:** no counterexample falsifies the narrow arithmetic polarity of the 983/984 boundary. The current evidence is insufficient to verify the full declared paired runner boundary claim: only the 984 gap-negative has an integrated receipt; the 983 result here is an in-memory prediction. Keep calibration admission pending the declared independent replay and exact paired receipts. No auditory/perceptual, general threshold, or full-runner integration claim follows from scratch arithmetic.
