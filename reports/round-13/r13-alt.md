# Round 13 independent flat-180 control (`r13-alt`)

## Construction and scope

Created original synthetic PCM16 mono `flat180_other.wav` in `.shokunin/audio/corpus/live/round-13/`: 4.0 seconds, 48,000 Hz, 192,000 frames, `round(0.035 * sin(2π·180t) * 32767)` samples. This holds the 180 Hz component amplitude constant across each 96,000-frame half. SHA-256: `1ce465466af7bbcb2d1c854266f8daf63e4eb03fd53b5b3c2de452a0c0a0a5b8`. Only this assigned scratch and this report were written. No source, LOG, SCORECARD, canonical fixture, or commit was changed.

## Independent measurement

Loaded the existing measurement functions directly against the scratch WAV (rather than changing the shared runner):

```sh
python3 -c 'import importlib.util,json,pathlib; p=pathlib.Path(".shokunin/audio/corpus/fixtures/measure_audio.py").resolve(); s=importlib.util.spec_from_file_location("measure_audio",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); f=(p.parent.parent / "live/round-13/flat180_other.wav"); print(json.dumps({"generic":m.measure("flat180_other",(4.0,100,2000,True),f),"section":m.section_contrast(f,180)},indent=2))'
```

Exit **0**. Results:

- Generic format/duration/level/spectrum/seam checks all pass: 4.0 s, 48 kHz mono; peak `.035003662109375` FS; RMS `-32.12882027117345` dBFS; centroid `225.32688010982727` Hz; bandwidth `846.7417503782573` Hz; endpoint delta `.000823974609375` FS; seam slope mismatch `0.0` FS/sample; `failures: []`.
- 180 Hz two-half fit is valid: component amplitudes `[.03500047667725067, .03500047667725067]` FS; half RMS `[.02474907583673609, .02474907583673609]` FS. Contrast is **0.0 dB**, so it fails the existing section-contrast predicate (`< 6 dB or invalid`). Internal join gap `.000823974609375` FS passes `.03`; internal side-slope mismatch `0.0` FS/sample passes `.001`.
- Thus the only failed fit/gate is the intended section-contrast check. The contrast is *valid* but flat; it is not a malformed/invalid section. No generic or seam failure was found.

For context, comparison to the baseline layer centroid in the round-12 normal receipt gives relative centroid delta `0.18503701369725753`, above `.10`; this fixture is not an `_alt`-named variant and the runner's `_alt` distinctness gate does not apply to it. This is not a new threshold or an acceptance claim.

## Shell attempts / exits

Two initial measurement-command attempts failed before any measurement and did not change project files:

1. `python3 -c 'import importlib.util,json,pathlib; p=pathlib.Path(".shokuni/audio/corpus/fixtures/measure_audio.py"); s=importlib.util.spec_from_file_location("measure_audio",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); f=pathlib.Path(".shokuni/audio/corpus/live/round-13/flat180_other.wav"); print(json.dumps({"generic":m.measure("flat180_other",(4.0,100,2000,True),f),"section":m.section_contrast(f,180)},indent=2))'` — exit **1** (`FileNotFoundError`: typo `.shokuni`).
2. `python3 -c 'import importlib.util,json,pathlib; p=pathlib.Path(".shokunin/audio/corpus/fixtures/measure_audio.py"); s=importlib.util.spec_from_file_location("measure_audio",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); f=pathlib.Path(".shokunin/audio/corpus/live/round-13/flat180_other.wav"); print(json.dumps({"generic":m.measure("flat180_other",(4.0,100,2000,True),f),"section":m.section_contrast(f,180)},indent=2))'` — exit **1** (`ValueError`: relative path was not under resolved ROOT).

No audible, playback-engine, adaptive-behavior, music, rights, security, or production-quality claim is made. This is a numerical control measurement of original synthetic PCM only.
