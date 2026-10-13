# Round 26 reviewer: minimal duplicate-variant route

## Claim under review
The round-26 depth claim is narrowly to exercise the existing `_alt` distinctness check with one matched scratch duplicate pair. The pair should use the existing `ui` measurement spec, pass its ordinary checks individually, and produce exactly one failure on the variant: `distinctness: duration < .020 s and centroid delta < 10%`. This is a proposed route only; I did not build or run it.

## Minimal builder/runner route

- Add one opt-in builder switch (for example `--probe-ui-clone`) that writes `ui_clone.wav` and `ui_clone_alt.wav` only under `corpus/live/round-26/`. Generate one 48 kHz mono PCM16 waveform once and write the same samples to both files. Leave the existing canonical `ui.wav` and all other artifacts untouched by this option.
- Add a matching opt-in runner switch. In that mode, retain the normal canonical measurements, then call the existing `measure(name, SPECS["ui"], path)` for each scratch file, storing the results under keys `ui_clone` and `ui_clone_alt`. Keep the existing distinctness loop and its `.020` / `.10` OR rule unchanged.
- The existing lookup `base = measurements[name[:-4]]` is correct for the key `ui_clone_alt`: removing the four-character suffix `_alt` gives `ui_clone`, the intended matched baseline. Do not look up `measurements["ui"]`; that would compare against the canonical rather than the matched duplicate. Record the explicit `baseline` field as `ui_clone`.
- To keep the route opt-in, do not extend `SPECS` with scratch names or make every normal run require these files. Apply the existing `measure()` checks to both scratch WAVs; use the runner's ordinary failed-measurement exit behavior, expecting exit 1 only for the variant distinctness failure if all fit conditions are satisfied. The ordinary normal route should remain unchanged.

## Expected evidence and limits
The runner receipt should show both scratch measurements have empty ordinary `failures`, identical duration and centroid, and a `ui_clone_alt` distinctness record with `duration_delta_s: 0`, `centroid_relative_delta: 0`, `passed: false`, and the sole distinctness failure. This would demonstrate the exact duplicate negative at zero/zero under the existing rule, not behavior at either threshold boundary, general deduplication, auditory similarity, or engine behavior. No route or exit result was verified here.

## Commands
No shell commands were run. The exact invocation and exits cannot be supplied as observed results; the suggested command names above are illustrative until the builder/runner flags exist.
