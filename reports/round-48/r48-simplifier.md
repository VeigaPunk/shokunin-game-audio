# Round 48 simplifier review

## Scope and recommendation

I read the Round 48 declaration in `.shokunin/audio/LOG.md`, the current builder and runner. This is a source-level recommendation only. Keep the existing `format_failures()` predicate (integer stream rate must equal 48000 and channels must equal one) and every measurement threshold unchanged. Add just two opt-in modes and one paired fixture builder; do not add rate converters, threshold arguments, shared configuration, or a new validation framework.

The cleanest fixture generation is to construct the existing UI-shaped 5760-sample PCM16 sequence once, then write those exact same PCM bytes twice with WAV rates 47999 and 48000. A narrow `save(..., rate=RATE)` optional parameter is one small way to do that; alternatively use the existing `wave` writer locally in the new builder. Keep both files under `corpus/live/round-48/<executor>/`, not in canonical artifacts. Preserve exactly 5760 frames and mono, 16-bit PCM. At 47999Hz, ffprobe duration should be about 0.1200025s (within the existing ±.001s UI duration band); at 48000Hz, .12s. Verify actual metadata and all measured gates before asserting this. Same bytes do not ensure identical SoX-decoded samples if SoX resamples during float decode, so report the actual decode outcome rather than presuming it.

The runner can follow the established centroid-probe pattern: one `--probe-ui-rate-below` / `--probe-ui-rate-at` pair, mutually exclusive, each dispatching the builder, selecting its corresponding path, and measuring only that selected probe against `SPECS["ui"]`. The existing `measure()` already reports ffprobe stream rate/codec/channels/bit depth, duration, peak, RMS, centroid and failures. The normal runner return is already nonzero when a measurement has failures. Add the mode/suffix labels in the existing receipt labeling; avoid refactoring its historical mode logic for this single addition. Expected outcomes are 47999: exit 1 with only `format: expected 48kHz mono`; 48000: exit 0 with no failures. Existing format logic also checks PCM16, while other ordinary UI gates still run, so actual evidence must establish that these are the only differences. Do not modify the comparator or thresholds.

## Evidence limits and command record

No fixture was built or run; no ffprobe query or SoX decode was performed. Thus there are no actual Round 48 ffprobe metadata, decoded project metrics, receipt paths, or numeric-fit results to report. In particular, the expected durations above are calculations, not measurements. This review makes no inference about universal sample-rate behavior, resampling/conversion, transcription, audition, perceived quality, production readiness, rights, engine integration, or publishing/promotion.

The only shell command run was:

```sh
git status --short; find .shokunin/audio/corpus -maxdepth 3 -type f | head -25; grep -R "def format_failures\|probe-ui\|round-47\|mono441" -n .shokunin/audio/corpus/fixtures .shokunin/audio 2>/dev/null | head -100
```

It exited **0**. Its status output showed `.shokunin/audio/LOG.md` already modified; I did not edit it. I did not edit builder/runner source, canonical fixtures, SCORECARD, or any other report, and made no commit or push.
