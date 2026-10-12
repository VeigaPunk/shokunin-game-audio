# Round 5 independent verifier replay

## Scope and method

Non-author replay and table audit for the declared round-5 calibration claim. I read round-5 sections in `.shokunin/audio/LOG.md`, `.shokunin/audio/corpus/knowledge/2026-10-12-threshold-calibration.md`, `.shokunin/audio/corpus/fixtures/measure_audio.py`, and the replay receipts listed below. I independently ran the prescribed commands from repository root, in order, including final normal restoration. I did not change code or artifacts. Values below are recomputed from the resulting JSON receipts; the checker itself decodes WAV through SoX/ffprobe. This is a fixture-table verification, not a perceptual or mastering assessment.

## Exact replay commands and outcomes

```text
python3 .shokunin/audio/corpus/fixtures/measure_audio.py
exit 0; receipt .shokunin/audio/corpus/live/runs/20261012T165559423568Z-normal/measurements.json; 10 measurements, no failures
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat
exit 1; receipt .shokunin/audio/corpus/live/runs/20261012T165600065823Z-flat/measurements.json; sole failure flat30_probe section contrast
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope
exit 1; receipt .shokunin/audio/corpus/live/runs/20261012T165600690434Z-slope/measurements.json; sole failure slope_probe slope mismatch
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing
exit 1; receipt .shokunin/audio/corpus/live/runs/20261012T165601269726Z-failing/measurements.json; ambience fails centroid and endpoint jump
python3 .shokunin/audio/corpus/fixtures/measure_audio.py
exit 0; receipt .shokunin/audio/corpus/live/runs/20261012T165601852330Z-normal/measurements.json; 10 measurements, no failures
```

The first and restoring normal receipts have no failures. The restoring normal receipt's full `measurements` and `sections` exactly equal cited clean receipt `20261012T164320494590Z-normal`.

## Recomputed table figures and polarity

- **RMS boundary:** code tests `rms < .001` as failure, therefore `.001` equality passes (`RMS >= .001`). The receipt still labels the value `rms_min_exclusive: 0.001`; that key is misleading, as LOG and table disclose. No threshold/code change was made.
- Across the ten normal fixtures, peak is **0.172363–0.808777 FS**, so nearest margin below `<.95` is **.141223 FS**. Linear RMS decoded from reported dBFS is **.064715–.180272 FS**; nearest margin above `>=.001` is **.063715 FS**. Table's rounded extrema/margins agree.
- Each centroid is within its fixture-specific inclusive band. Recomputed nearest-edge margins (Hz): ui 716.897; ui_alt 1173.153; impact 4156.873; impact_alt 423.792; movement 4065.516; movement_alt 3975.785; ambience 31.616; ambience_alt 53.019; stem 172.676; stem_sections 101.871. Table values agree.
- Four loop fixtures (`ambience`, `ambience_alt`, `stem`, `stem_sections`): endpoint deltas range .000671–.011383 FS; max .011383 leaves **.018617 FS** below inclusive .03. Slope gaps range 0–.000152588 FS/sample; max .000152588 leaves **.000847412 FS/sample** below inclusive .001. Table values agree.
- Variant OR values (duration delta s / relative centroid delta): ui_alt .040/.471877; impact_alt 0/.956305; movement_alt .120/.007519; ambience_alt 0/.584514. Each passes at least one branch of `duration >= .020 OR centroid relative delta >= .10`; values/table agree. No duplicate-base negative control is present.
- `stem_sections`: decoded sample count 192000; component amplitudes .011999465/.059998071 FS (nearest >=.01 floor margin .001999465); section RMS .063810315/.076155261 FS (nearest >=.001 floor margin .062810315); signed contrast 13.979508 dB, **7.979508 dB** over the >=6 bound. Table agrees.
- Clean LUFS: six null (the six SFX) and four finite: ambience -30.7, ambience_alt -24.7, stem -15.8, stem_sections -24.7. Table explicitly says null is not silence or a -70 LUFS measurement and there is **no declared or enforced LUFS acceptance window**. No LUFS pass criterion is implied.

## Probe isolation / limitations

- Flat probe is valid: both 30 Hz amplitudes .0359986155 FS, both section RMS .0681745007 FS, contrast 0 dB; sole failure is contrast. It demonstrates rejection of this matched flat case, not the exact 6 dB edge or section-floor rejection.
- Slope probe has endpoint delta 0 and slope gap .469970703 FS/sample; only slope fails. It demonstrates this large slope mismatch, not near-boundary sensitivity.
- Broken ambience has centroid 2690.188 Hz (above its 200 Hz ceiling) and endpoint jump .499329 FS (above .03); both fail. It is not an isolated control for either rule.
- Table correctly identifies wrong format, duration edge, peak/RMS boundaries, centroid edges, variant boundaries, section sample-count/floors, and LUFS reporting behavior as lacking dedicated negative controls. Positive clean samples and far-from-boundary failures do not establish edge sensitivity, population calibration, or perceptual quality.

## Canonical artifact preservation

I computed SHA-256 for all ten `.shokunin/audio/corpus/artifacts/*.wav` before and after replay: unchanged for every file. Independently, each current file's Git blob at `358f625:<path>` matches the before/after file content. Blob IDs:

| artifact | Git blob at 358f625 |
|---|---|
| ambience.wav | `57934d4dfce588247d8105f3d5d6fae5efba5011` |
| ambience_alt.wav | `c8ff048023a260a66bf12e2e7cb6c4d1978244ee` |
| impact.wav | `3d6ab86764390fc162ce717a8d773509bbc4fc4c` |
| impact_alt.wav | `59444145ca1b7c657e51aadd4ee4c11993b63f2e` |
| movement.wav | `93af9d3cd7ed43e0197625f7dfcfa431277775c6` |
| movement_alt.wav | `021e02ce78cfcd1f9f9b8d6d94294e29e1dde175` |
| stem.wav | `bd886f23df4efe9996112dd3c1b363bf6bfcef41` |
| stem_sections.wav | `ba31691718bb05020f677dce5ba4a3ca9161633b` |
| ui.wav | `0dca35d3cf7a44b2bcb9965d496240fb4d9e62fc` |
| ui_alt.wav | `a5a1fafce4513960b3b6b5aa1b0b06b2c7eecac6` |

## Verification finding

The table's key decoded ranges, margins, variant OR branches, section figures, LUFS/null disclosure, and probe-isolation wording agree with independent replay. The RMS equality correction is accurate and preserves the legacy receipt key while explaining its mismatch. This verifies replay and descriptive fixture accounting only; it does not validate threshold selection or make perceptual/mastering claims.
