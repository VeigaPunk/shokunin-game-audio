# R41 scribe — 32/33 PCM decision table

## Decision and limits

R41 LOG declares a numerical fixture calibration only: bracket the existing outer-loop side-slope comparator `abs((last-penultimate)-(second-first)) > .001` full scale/sample with 32/32768 = **0.0009765625** (pass) and 33/32768 = **0.001007080078125** (fail), while endpoint jump stays <= .03 and ordinary fixture checks pass. The comparator/threshold is unchanged. Gate-level runner results and full replay are **pending**; the table below is helper measurement of current scratch files, not runner receipt evidence.

## Decision table (decoded PCM/helper measurements)

| Pair/file | SHA-256 | Decoded boundary sample counts (first, second, penultimate, last) | Outer side-slope mismatch | Endpoint delta | Ordinary checks / helper outcome |
|---|---|---|---:|---:|---|
| executor final `slope-32.wav` | `0bc9c6f07b53b13336b253db069cc57702e9520634106eabf85fc27e329b4547` | final pair: 32-count decoded mismatch | 32/32768 = **0.0009765625** | 0.001190185546875 | 2.0s, 48k mono PCM16; centroid 150.16139474032187 Hz; no failures; intended pass. |
| executor final `slope-33.wav` | `b86a34d343a57e943ab4289cb67b992b8597d93002f3b4a7ef9981e6b30952fb` | final pair: 33-count decoded mismatch | 33/32768 = **0.001007080078125** | 0.001190185546875 | 2.0s, 48k mono PCM16; centroid 152.54369633957694 Hz; sole failure: `loop seam: slope mismatch > .001 full scale per sample`; intended fail. |
| independent alt `slope-32.wav` | `e23036abb2e3585eb18f9debec2c12f0b330d3e2d815dd36004ebda07b6780c1` | 25000, 25000, 25000, 25032 | 32/32768 = **0.0009765625** | 32/32768 = 0.0009765625 | 2.0s, 48k mono PCM16; peak .88995361328125; centroid 117.27808903942851 Hz; no failures. Intended pass fit. |
| independent alt `slope-33.wav` | `69db5b901f1657c7c9f6f93dc0d2304b7ec1405d01c9a394a8b0f8753d5fe3bc` | 25000, 25000, 25000, 25033 | 33/32768 = **0.001007080078125** | 33/32768 = 0.001007080078125 | 2.0s, 48k mono PCM16; peak .88995361328125; centroid 117.29804831044468 Hz; sole helper failure: `loop seam: slope mismatch > .001 full scale per sample`. Intended fail fit. |

**Measurement interpretation and chronology:** The first executor candidate hashes (`b1c7…e4568` / `c42c…1dff`) were transient numeric failed fits: native PCM boundary values gave raw mismatches of 32/33 counts, but project-helper SoX-float decoding yielded respectively 0 and 1 count, so the expected bracket did not occur. They were regenerated. The final executor hashes listed above are the current successful pair according to the parent’s rerun of the same absolute-path helper: 32 passes and 33 fails solely on slope; both have endpoint delta .001190185546875 and centroids within 5–200 Hz. Do not describe the transient pair as current executor state. The independent alt pair also measures intended 32/33 pass/sole-fail outcomes. Neither pair is an internal section-join test or an outer-endpoint-fail substitute.
## Commands, exits, and fit/setup distinction

I ran no runner mode. The following successful direct helper commands were run (exit 0); they do not establish runner exits or gate status:

```sh
python3 -c "import importlib.util,json,hashlib; from pathlib import Path; s=importlib.util.spec_from_file_location('m','.shokunin/audio/corpus/fixtures/measure_audio.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(json.dumps({n:{'sha256':hashlib.sha256((Path(m.ROOT)/'live/round-41/executor'/('slope-'+n+'.wav')).read_bytes()).hexdigest(),**m.measure('ambience',(2.0,5,200,True),Path(m.ROOT)/'live/round-41/executor'/('slope-'+n+'.wav'))} for n in ('32','33')},indent=2))"
```

```sh
python3 -c "import importlib.util,json,hashlib; from pathlib import Path; s=importlib.util.spec_from_file_location('m','.shokunin/audio/corpus/fixtures/measure_audio.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(json.dumps({n:{'sha256':hashlib.sha256((Path(m.ROOT)/'live/round-41/alt'/('slope-'+n+'.wav')).read_bytes()).hexdigest(),**m.measure('ambience',(2.0,5,200,True),Path(m.ROOT)/'live/round-41/alt'/('slope-'+n+'.wav'))} for n in ('32','33')},indent=2))"
```

There were no setup/invocation errors in my commands. The transient executor pair was a **numeric failed calibration fit** (helper-decoded mismatch 0/1 counts); it was replaced by the final successful pair above. Do not treat its failure as the current executor result. The alt report records a first exploratory pair whose helper invocation exited 0 but both candidates failed the numeric centroid band (2801.8438588548047 and 2801.814634859037 Hz); those files were overwritten, and are not the final candidate pair. I did not run or observe that exploratory command, so do not attribute its command text or exit to this scribe. The alt report also records two setup/path errors (exit 1: passing `str` where `Path` is required and using relative path outside helper `ROOT`), followed by a corrected direct-helper invocation exit 0. These setup errors are distinct from the numeric centroid miss. The alt report's exact corrected command is:

```sh
python3 -c "import importlib.util,json; from pathlib import Path; s=importlib.util.spec_from_file_location('measure_audio','.shokunin/audio/corpus/fixtures/measure_audio.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(json.dumps([m.measure('x',(2.0,5,200,True),Path('.shokunin/audio/corpus/live/round-41/alt/slope-%d.wav'%n).resolve()) for n in (32,33)],indent=2))"
```

## Pending evidence and scope

Parent’s final-helper rerun confirms the intended 32 pass / 33 sole slope failure for the final executor pair. Runner-mode receipts and the 42-run serial replay remain pending; do not present those gate results as established until receipts/replay exist. R41 remains fixture-local PCM calibration: the 32/33 integer points do not test equality at exactly `.001` (32.768 counts). No audition, sound-quality, production, rights, engine, publish, or promotion inference is made. No constants were changed by this scribe.
