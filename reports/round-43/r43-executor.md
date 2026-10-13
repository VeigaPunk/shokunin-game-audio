# Round 43 executor — decoded RMS crest-count fixtures

## Scope

Built only two original scratch fixtures under `.shokunin/audio/corpus/live/round-43/executor/`. This is numerical fixture calibration against the project measurement helper, not an audition or sound-quality assessment. No canonical source, LOG, scorecard, or other report was changed.

## Recipe

For each signed PCM16 target count `c` in `(46, 47)`, generate `n = np.arange(5760)` and
`pcm = np.rint(c * np.cos(2*np.pi*1000*n/48000)).astype('<i2')`.
Write `pcm.tobytes()` as mono, 16-bit WAV at 48,000 Hz. The cosine has 120 cycles in 5760 frames; its phase places the crest at a sample. The realized max absolute decoded integer count is exactly `c` for both. These are adjacent crest-count controls, not adjacent RMS values.

| Crest count | Scratch WAV | SHA-256 | Frames / format | Decoded peak FS | RMS dBFS | RMS FS | Centroid Hz | Helper failures |
|---:|---|---|---|---:|---:|---:|---:|---|
| 46 | `corpus/live/round-43/executor/crest-46.wav` | `869d1e5ada618a3c9daaa7be3100c9a01dc1342df63d732355a23a306130adfc` | 5760; 48 kHz mono PCM16 | 0.00140380859375 (=46/32768) | -60.07098885448798 | 0.0009918604133909925 | 1333.1671762128612 | `level: clipping headroom or near silence` only |
| 47 | `corpus/live/round-43/executor/crest-47.wav` | `4c8c67a08558f14ad0642cac99563056407eeeecdc6b05e974f7b24cf74804b3` | 5760; 48 kHz mono PCM16 | 0.001434326171875 (=47/32768) | -59.88721491134572 | 0.0010130695326051166 | 2221.1801421740442 | none |

Both centroids are within the declared UI fixture band 250–4000 Hz. The helper returns `integrated_lufs: null`; it is not used for this RMS check. The check's combined predicate is `peak >= .95 or rms < .001`; both peaks are far below `.95`, isolating the RMS branch. The 46-count fixture is below `.001 FS`; 47-count fixture is above. This does not establish an exact `.001` equality case or an audible silence boundary.

## Commands and execution status

In-session Python generation wrote the two files using the recipe above; both writes completed. SHA-256 was computed from each resulting WAV's bytes.

Exact helper invocation (the shell command was launched through Python `subprocess.run(..., shell=True)`):

```sh
python3 -c 'import importlib.util; from pathlib import Path; p=Path(".shokunin/audio/corpus/fixtures/measure_audio.py"); s=importlib.util.spec_from_file_location("measure_audio",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); [print(m.measure("ui",m.SPECS["ui"],Path(f".shokunin/audio/corpus/live/round-43/executor/crest-{n}.wav").resolve())) for n in (46,47)]'
```

Exit **0**. Direct `measure()` results are tabulated above. An initial attempt used the same invocation with non-absolute fixture paths and exited **1** on `Path.relative_to(ROOT)` (`ValueError`: relative fixture path was not under the absolute project root). That was a measurement-path setup error; rerunning with `.resolve()` succeeded. No numeric fit search was attempted or failed: the specified integer crests were generated directly. The initial path error is not a numeric failed fit or fixture failure.

## Limits

This is executor evidence only. It does not establish independent verification, round admission, exact equality at the threshold, perceived silence, sound quality, production suitability, rights, engine behavior, or publishing/promotion suitability.
