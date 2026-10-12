# Round 17 simplifier review

## Scope and inspection

I reviewed the Round 17 declaration in `.shokunin/audio/LOG.md`, current `build_artifacts.py` and `measure_audio.py`, and the scout, executor, alternate, critic, and reviewer reports. This is a static integration review; I did not run the builder or measurement runner, edit source, or verify canonical hashes/mode behavior. The executor and alternate scratch reports report the same generated SHA and measurements, but that is not integrated runner or independent replay evidence.

Shell inventory commands and exits:

```sh
find .shokunin/audio -maxdepth 4 -type f | sort | tail -80
# exit 0
find .shokunin/audio -type f | grep 'round-17' | sort
# exit 1 (no round-17 paths existed at that inspection)
git status --short
# exit 0; at that inspection only LOG.md was modified
```

A later `git status --short` exited 0 and showed the in-progress Round 17 reports/scratch and `fixtures/__pycache__`; it is inventory only, not validation. Python REPL reads of files and prior reports are not shell commands.

## Smallest implementation

- Keep one canonical source: add the 4-second 200 Hz `.015/.050` synthesis beside the existing `stem_layer` and `stem_layer_alt` saves in `build_artifacts.py`, under the new canonical name `stem_layer_third`. Do not create a second analyzer, hand-written parallel fixture, scratch probe mode, or separate source of target amplitudes.
- Add its ordinary `(4.0, 100, 2000, True)` entry to `SPECS`. Add the new name to the existing section-analysis selection and select 200 Hz for that name. Add it to the same existing internal-join gap and slope checks applied to layered fixtures. Reuse the existing `section_contrast`, validity floor, signed `>=6 dB` comparison, `.03` gap, `.001` slope, and generic outer checks; no new threshold or branch with different acceptance logic.
- Preserve the existing mappings and criteria as-is. The current component-frequency selection and join applicability are explicit name lists; adding the new fixture to those existing lists is the smallest safe patch. A mapping refactor is unnecessary for this one addition and risks widening the change. Do not alter the `_alt` distinctness loop: it only evaluates existing `_alt` pairs. A third fixture does not create a new distinctness pass/fail obligation.
- The only intended receipt shape change is the additional canonical measurement and 200 Hz section result. Existing fixture output, opt-in behavior, thresholds, and old failure sets must remain unchanged. Generated artifacts are a consequence of the normal builder and must be checked against the pre-round baseline; this review does not establish they are unchanged.

The reported scratch candidate is promising but has limited slope headroom: executor/alternate report outer and internal slope mismatch `.000915527344` FS/sample versus the existing `.001` bound. Their scratch measurements are not proof that the integrated runner accepts it. If integration rejects it, record the measured failure and adjust the source waveform without relaxing thresholds.

## Evidence boundary

No builder/runner result, unchanged canonical hashes, old mode replay, or independent verification is established here. The proposed integration supports only adding a deterministically synthesized fixture evaluated by existing numeric checks. It does not support a distinctness, audible, musical, engine, adaptive, compatibility, or production claim.
