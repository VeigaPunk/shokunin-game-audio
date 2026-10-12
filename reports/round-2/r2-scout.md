# Round 2 scout: fixture integration map

## Scope and observed baseline

Read `.shokunin/audio/LOG.md` round-2 claim/spec and the current `corpus/fixtures/build_artifacts.py`, `build_artifacts.sh`, and `measure_audio.py`. The builder deterministically synthesizes five original mono PCM16/48 kHz WAVs (`ui`, `impact`, `movement`, `ambience`, `stem`) into `corpus/artifacts`; its RNG seed is `20261012`. The measurement entrypoint invokes that builder on every run, then iterates the five-name `SPECS` mapping. For each artifact it obtains WAV format/duration from ffprobe, decodes samples with SoX, and records peak, RMS dBFS, centroid, bandwidth, optional ebur128 LUFS, and (for ambience and stem) endpoint delta. The existing checks enforce 48 kHz mono, per-name duration ±1 ms, peak <.95, RMS >.001, centroid within the existing category band, and endpoint delta ≤.03 for loop specs. It emits a timestamped JSON receipt under `corpus/live/runs/` and exits nonzero if any measurement fails. Keep these five specs, checks, receipt fields/semantics, and the normal build/measure path intact.

## Minimal integration recommendation

- Keep original fixtures in `corpus/artifacts` and variant deliverables at the specified `corpus/live/round-2/{ui,impact,movement,ambience}_alt.wav`; do not replace baseline files or make the live variants the builder's canonical outputs.
- Add four deterministic source-generation functions (or a compact name-to-generator mapping) with explicit variant durations/parameters, writing original samples directly to their distinct live paths. Avoid reading, copying, mixing, or transforming existing WAVs. Reuse the established PCM16 mono 48 kHz encoding convention and fixed RNG seeds for any noise-based variant.
- Extend measurement with a small variant specification/path mapping, rather than changing the existing `SPECS` entries or hard-coded baseline resolution. Each variant should use the same format, level, duration, and centroid-band validation as its category. Apply the endpoint check to ambience_alt. Record the variant measurements in the same run receipt without changing meanings of existing baseline measurement keys; make variant paths explicit so replay is traceable.
- Evaluate the round's distinctness condition using raw artifact measurements: compare each variant's measured duration and centroid with its corresponding baseline, and pass distinctness only if duration differs OR `abs(variant_centroid - baseline_centroid) / baseline_centroid >= 0.10`. Do not infer distinctness from synthesis parameters. Report this separately from ordinary category-band validity; both must pass. The current centroid is a magnitude-weighted whole-waveform FFT centroid, not a timbre or perceived-quality claim.
- Keep the ambience variant's endpoint delta under the existing .03 bound. A duration change alone can establish distinctness but does not establish loop quality; the seam check remains required.
- Retain the current ebur128 handling: null for absent/non-finite/≤−70 LUFS gated-floor readings, with RMS dBFS as a separate measure. Describe thresholds as local fixture bounds, not production standards.

## Observability / validation gaps to close

A replay should demonstrate (1) all original five still pass, (2) all four variant files exist and are independently measured, (3) each variant passes its category's existing constraints including ambience seam, (4) each distinctness comparison is computed from measurements of both raw files, and (5) variant generation is deterministic and does not depend on the artifacts already on disk. An explicit variant block or flat variant-name measurements plus a distinctness result is sufficient; avoid restructuring old baseline records. A positive normal receipt alone cannot prove the source generator is deterministic—compare hashes across a repeated build/replay, while preserving measurement receipts for both runs.

## Commands

No shell commands were run for this scout; therefore there are no command exit codes to report.
