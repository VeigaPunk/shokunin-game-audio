# R42 reviewer — minimal decoded-peak boundary modes

## Review basis and scope

The R42 LOG declares a calibration-only bracket of the unchanged peak comparator `peak >= .95`: decoded PCM16 peak magnitude 31129 counts passes (`31129/32768 = 0.949981689453125`), while 31130 counts fails (`31130/32768 = 0.95001220703125`). The comparator also retains `rms < .001` as the same level failure. This is the outer numeric boundary at representable PCM16 counts, not a change to either threshold.

Recommend exactly two opt-in source-generated modes, e.g. `--probe-ui-peak-31129` and `--probe-ui-peak-31130`, each creating a distinct scratch WAV only under `corpus/live/round-42/`. Route each through the existing `ui` measurement spec `(.12, 250, 4000, False)` and ordinary receipt/exit handling. Do not add a generalized probe framework, alter canonical assets, or change the comparator or unrelated checks.

## Minimal fixture construction

Use a 5760-sample, 48 kHz mono PCM16 sine at a fixed in-band frequency with an integer number of cycles in .12 s; 1000 Hz is a simple choice (120 cycles). Phase the sine so a sampled crest is exactly 1.0 in normalized form, scale the source to the requested integer PCM count divided by 32768, and encode to signed PCM16. The only source parameter that should differ between the two fixtures is the crest count. Verify the actual decoded PCM count from each emitted WAV rather than relying only on pre-encode floats. The expected decoded peak magnitudes are exactly 31129 and 31130 counts. A 1000 Hz tone puts the centroid in the UI band; its RMS is far above .001. Both fixtures should otherwise pass duration, 48 kHz mono PCM16 format, and centroid checks. Confirm the generated files have distinct SHA-256 hashes and that canonical files remain untouched.

Expected outcomes using the existing comparison: 31129 has no failures and exits 0; 31130 has only `level: clipping headroom or near silence` and exits 1. The same level label is used for either branch of the existing combined peak/RMS predicate; do not describe this as evidence that the fixture failed the RMS floor.

## Commands and evidence

No shell commands were run for this source/spec review. There are no command exit codes, WAVs, receipts, decoded count measurements, hashes, setup errors, or numeric failed-fit results to report. In particular, no run result is being asserted here. If later attempts fail, report command and exit exactly, and classify helper/path/encoding invocation failures as setup errors separately from successfully decoded fixtures that miss a numeric target (for example, wrong peak count or an out-of-band centroid).

The arithmetic bracket is adjacent PCM16 counts around .95 because `.95 * 32768 = 31129.6`; it does not test equality at exactly .95. This is numerical fixture calibration only. It does not support claims about audition, audible clipping, sound quality, headroom suitability, production, rights, engine integration, publishing, or promotion.
