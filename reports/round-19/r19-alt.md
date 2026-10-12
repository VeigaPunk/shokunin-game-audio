# Round 19 alternate: PCM grid and counterexample check

## Scope

Read `.shokunin/audio/LOG.md` (round-19 claim/spec) and inspected `corpus/fixtures/measure_audio.py` and `build_artifacts.py` at clean source revision `010f88b`. I made no source/LOG/SCORECARD/canonical edits. Scratch WAVs are under `corpus/live/round-19/`; this report is the only report file I wrote. This is a decoded-number check, not an audible, engine, or production claim.

## Grid experiment

Source `corpus/artifacts/stem_layer_third.wav`, SHA-256 `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445`, has PCM16 frame 96001 = 43. I copied it and changed only that sample by +1, +2, +3, and +4 integer counts, producing `plus1.wav` through `plus4.wav` (hashes respectively `28dc8e6619bea8c1fb96f27d88c857ccc461e688d48c98550f8fd2a395df55e1`, `512b38026eb102fac4773bca1b61e7994261b6f6297e0ec544fb4b47b1104496`, `48e2167dd405d05dc66aab304fc7b3c4712d2734dca021fdfd92d15a3e8d2a38`, `1004915d372bd58035c02c9f6d54ed5b56c0dd2ad80de4333c7133d0e40aa9a5`). Direct SoX float32 decode and the same side-slope formula as `section_contrast` give:

| edit at PCM frame 96001 | decoded internal side-slope mismatch (FS/sample) | integer grid units (32768 × value) | comparator `> .001` |
|---|---:|---:|---|
| +1 (43→44) | .000946044921875 | 31 | pass |
| +2 (43→45) | .0009765625 | 32 | pass |
| +3 (43→46) | .001007080078125 | 33 | fail |
| +4 (43→47) | .00103759765625 | 34 | fail |

This is a one-edit local sweep, not proof about all PCM signals. The scalar threshold equals 32.768 such units, so this local sequence brackets it; integer PCM cannot equal it. The exact edit producing the nearest below-threshold point is +2, and +3 is nearest above. A negative one-count countercheck (43→42) yields .000885009765625 (29 units), consistent with local direction but not exhaustive.

## Counterexample / gate interpretation

`section_contrast()` reports `passed: true` on all four: that field is specifically the section validity / >=6 dB contrast gate. In particular +3 has 33 units (> .001), but its `section_contrast` object still says passed. This is not a counterexample to the *integrated* strict internal-slope gate; it exposes an API-layer distinction and a tempting false reading. The caller separately applies `internal_join_side_slope_mismatch_full_scale_per_sample > .001`. Similarly, calling `measure()` alone gives an empty failures list on these scratches: it only computes the *outer* endpoint slope, not the internal join gate. Thus neither helper alone establishes overall acceptance/rejection. The round-19 runner must be used for that claim.

For context, internal gap is .000396728515625 FS for the one-frame edits and the 200Hz section contrast is approximately 10.457243 dB (valid, above 6 dB); generic format/duration/level/centroid and outer seam measurements passed on these files in direct `measure()`. Those observations do not replace runner receipts.

## Exact commands and setup issue

Python generated the PCM edits with `wave`/NumPy in the REPL; the SoX decode command used was `sox .shokunin/audio/corpus/live/round-19/plusN.wav -t f32 -e floating-point -` (exit **0** for N=1,2,3,4). I first tried the imported helper against a relative scratch path. Exact failed command:

```sh
python3 -c 'import importlib.util,pathlib,json; p=pathlib.Path(".shokunin/audio/corpus/fixtures/measure_audio.py"); s=importlib.util.spec_from_file_location("m",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); root=pathlib.Path(".shokunin/audio/corpus/live/round-19"); spec=m.SPECS["stem_layer_third"]; [(lambda p: (lambda r,c: print(p.name, json.dumps({"measurement":r,"section":c},sort_keys=True)))(m.measure("x",spec,p),m.section_contrast(p,200)))(root/f"plus{n}.wav") for n in range(1,5)]'
```

It exited **1** with `ValueError: '.shokunin/audio/corpus/live/round-19/plus1.wav' is not in the subpath of '/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus'`: helper `measure()` needs resolved absolute paths for `relative_to(ROOT)`. This was a test-harness path/setup issue, not a fit result. Corrected exact command (all four records; exit **0**):

```sh
python3 -c 'import importlib.util,pathlib,json; p=pathlib.Path(".shokunin/audio/corpus/fixtures/measure_audio.py").resolve(); s=importlib.util.spec_from_file_location("m",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); root=pathlib.Path(".shokunin/audio/corpus/live/round-19").resolve(); spec=m.SPECS["stem_layer_third"]; [(lambda p: (lambda r,c: print(p.name, json.dumps({"measurement":r,"section":c},sort_keys=True)))(m.measure("x",spec,p),m.section_contrast(p,200)))(root/f"plus{n}.wav") for n in range(1,5)]'
```

The correct call returned internal slope values above; `measure()` outer `failures` was empty for each, exactly because that helper does not add the internal-slope failure. A further negative-one check command exited **0**:

```sh
python3 -c 'import importlib.util,pathlib,json; p=pathlib.Path(".shokunin/audio/corpus/fixtures/measure_audio.py").resolve(); s=importlib.util.spec_from_file_location("m",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); p=pathlib.Path(".shokunin/audio/corpus/live/round-19/minus1.wav").resolve(); print(json.dumps(m.section_contrast(p,200),sort_keys=True))'
```

No runner mode exists in the inspected pre-integration source for these new +2/+3 controls. I did not modify it or claim a full-runner result. Parent's independent integration/replay should establish runner outcomes. No threshold or acceptance rule was changed.
