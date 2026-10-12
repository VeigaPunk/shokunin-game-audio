# Round 16 reviewer: minimal reverse-probe wiring

## Recommendation

Add one opt-in `--probe-layer-alt-reverse` mode to the fixture builder and measurement runner. Keep it an isolated scratch probe under `corpus/live/round-16/`; do not alter `stem_layer_alt.wav` or any canonical fixture. Reuse `SPECS["stem_layer_alt"]`, `measure()`, `section_contrast(..., 180)`, and the existing section validity / `>= 6.0 dB` rule. Do not add a reverse-specific threshold or a new gate.

The intended probe is the 4 s, mono, 48 kHz, PCM16 180 Hz layer with first-half amplitude `.050` and second-half amplitude `.015` FS. This reverses the canonical layer's section ordering. Existing contrast is signed as `20*log10(second/first)`, so the expected contrast is about `-10.46 dB`; the existing `>= 6 dB` predicate should reject it. Both amplitudes remain above the existing `.01` validity floor. These are predictions from the waveform specification, not runner results.

## Minimal code-path changes

1. In `build_artifacts.py`, add a default-false `layer_alt_reverse_probe` option and argparse flag `--probe-layer-alt-reverse`, pass it through the existing `main(...)` call, and add a small branch after creation of `stem_layer_alt`. Synthesize from the same `t` and 180 Hz formula, with `np.where(t < 2, .050, .015) * np.sin(2*np.pi*180*t)`. Use `save("reverse180_probe", ..., OUT.parent / "live" / "round-16")`. This reuses `save()`'s PCM16 format and does not write canonical outputs beyond the builder's ordinary existing fixture generation.
2. In `measure_audio.py`, add the matching argparse flag and include it in the mutually exclusive probe count. Forward it to the builder; measure `ROOT / "live" / "round-16" / "reverse180_probe.wav"` using `SPECS["stem_layer_alt"]`; include the named probe in the section-results comprehension at 180 Hz and in the existing internal-join gap and side-slope applicability tuples. The section loop will then apply existing validity and contrast rules and report the existing failure string. Set the mode and receipt suffix for the new flag, following the adjacent layer-alt probe branches.
3. No change is needed to `SPECS`, threshold values, `section_contrast`, or generic `measure()` logic. Do not weaken or special-case the existing `delta_db >= 6.0` test. Confirm that generic checks pass and the probe's only failure is the existing section-contrast failure before claiming the intended coverage move.

## Gate fit to verify (not yet measured)

At the 2 s amplitude transition, the 180 Hz sine is at a zero crossing. The expected internal adjacent-sample gap is roughly `.00118` FS, below `.03`; the expected side-slope mismatch is roughly `.00082` FS/sample, below `.001`. The 4 s waveform also starts and ends at zero phase. These estimates do not substitute for the runner's decoded-float32 measurements. Generic level, centroid (180 Hz is inside the existing 100–2000 Hz band), duration, format, and distinctness checks also need to pass in the actual receipt. If they do not, record a failed fit rather than sole-failure evidence.

## Scope and evidence

I read `.shokunin/audio/LOG.md` and the current `corpus/fixtures/build_artifacts.py` and `measure_audio.py` source. I ran no shell commands and made no source, fixture, log, or scorecard edits. Thus there are no command exit codes or fresh measurements to report. This is a wiring recommendation only; it makes no audible, engine, musical-quality, or production claim.
