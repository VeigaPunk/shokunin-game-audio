# Round 26 simplifier review

## Minimal move

Keep the existing variant rule unchanged: `abs(duration_delta) >= .020 OR relative_centroid_delta >= .10`. This role recommends no general duplicate detector, no new threshold, and no canonical asset. The narrow candidate is one opt-in `ui_clone` / `ui_clone_alt` scratch pair, generated from one 48 kHz mono PCM16 UI waveform and measured against the existing UI spec. Route the two explicit names/paths through the runner's existing measurement and distinctness calculation only for this probe; do not scan arbitrary files or change how the five canonical `_alt` pairs are handled. Exact same source samples should yield zero duration and centroid deltas and the existing rule's distinctness failure, while each measurement must independently have no ordinary failures. If the runner cannot expose this without broadening the mechanism, report the fit failure rather than introduce generic duplicate machinery.

## Source review and limits

Source inspection found the `_alt` comparisons in `measure_audio.py` are currently selected by `name.endswith("_alt")`, with the base name looked up by removing that suffix; only names in `SPECS` are ordinarily measured. Thus merely creating scratch files named `ui_clone` and `ui_clone_alt` does not make the normal runner measure them. The appropriate integration is opt-in and pair-specific, not an unbounded name/path discovery feature. Both inputs should be explicitly measured using the existing `ui` spec and explicit scratch paths; the negative should be attributable only to the already-existing OR rule. Preserve the thirteen canonicals and five existing variant comparisons.

This review did not generate or measure audio, run the runner, or verify receipts, hashes, historical modes, and invalid controls. It establishes no successful probe fit. No thresholds or source files were changed by this role. It makes no auditory similarity, engine, rights, publishing, or promotion claim.

## Commands

No shell commands were run; there are no shell exit codes to report. I inspected the source and prior round report in the Python REPL only.
