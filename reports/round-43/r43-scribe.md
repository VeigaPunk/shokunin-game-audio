# R43 scribe — decoded crest/RMS decision table

## Decision scope

LOG declares one calibration move for the unchanged combined level predicate `peak >= .95 or rms < .001`. The intended control uses periodic 1000 Hz, 5760-frame, 48 kHz mono PCM16 fixtures with decoded crest counts 46 and 47. Both decoded peaks must remain below `.95`; only RMS should route one fixture to the existing combined level failure. This is an adjacent **crest-count** control, not a claim of adjacent RMS values, exact `.001` equality, perceived silence, or audio quality.

## Decision table

| Decoded absolute PCM16 crest | Decoded peak FS | Decoded RMS FS (dBFS) | Combined-predicate route | Expected exit / failure list | Evidence status |
|---:|---:|---:|---|---|---|
| 46 | 46/32768 = 0.00140380859375 | 0.0009918604133909925 (−60.07098885448798) | `peak >= .95`: false; `rms < .001`: true | exit 1; sole `level: clipping headroom or near silence` failure | Executor direct `measure()` reports the numeric fit and sole intended failure. Runner mode and serial replay pending. |
| 47 | 47/32768 = 0.001434326171875 | 0.0010130695326051166 (−59.88721491134572) | `peak >= .95`: false; `rms < .001`: false | exit 0; no failures | Executor direct `measure()` reports the numeric fit and no failures. Runner mode and serial replay pending. |

Executor reports both decoded peaks are `< .95`; centroids are 1333.1671762128612 Hz (46) and 2221.1801421740442 Hz (47), inside the declared 250–4000 Hz UI band. Each WAV is 5760 frames, 48 kHz, mono PCM16. Distinct SHA-256 values: 46 `869d1e5ada618a3c9daaa7be3100c9a01dc1342df63d732355a23a306130adfc`; 47 `4c8c67a08558f14ad0642cac99563056407eeeecdc6b05e974f7b24cf74804b3`.

These are decoded/helper measurements, not runner receipts or CLI exit outcomes. The requested runner modes and the 46-run fresh serial replay are pending; no runner outcome is inferred from helper results. The single failure on 46 is the intended numeric gate result, not a setup error.

## Setup errors versus numeric fits

The executor reports its first helper invocation used relative fixture paths and exited **1** with `ValueError` from `Path.relative_to(ROOT)`. That is a path/setup error, not a numeric failed fit or gate evidence. Re-running with resolved absolute paths exited **0** and produced the measurements summarized above. No numeric fit search was attempted or failed; executor directly generated the requested crest counts. The values meet the stated crest, RMS-side, centroid, format, duration, and peak-isolation targets.

## Exact command and exit reported by executor

Executor reports this exact helper command (launched via Python `subprocess.run(..., shell=True)`) exited **0**:

```sh
python3 -c 'import importlib.util; from pathlib import Path; p=Path(".shokunin/audio/corpus/fixtures/measure_audio.py"); s=importlib.util.spec_from_file_location("measure_audio",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); [print(m.measure("ui",m.SPECS["ui"],Path(f".shokunin/audio/corpus/live/round-43/executor/crest-{n}.wav").resolve())) for n in (46,47)]'
```

The WAVs were generated in-session in Python using `n = np.arange(5760)` and `np.rint(c * np.cos(2*np.pi*1000*n/48000)).astype('<i2')`, for `c` 46 and 47. This was not a shell command; no shell exit code applies to generation. I ran no shell commands for this report and rely on the executor's exact command/exit and decoded results.

## Limits

This numerical fixture calibration does not establish exact equality at `.001`, perceived silence, audibility, sound quality, production suitability, rights, engine behavior, publishing, or promotion. No canonical source, LOG, scorecard, or other report is assessed or changed here.
