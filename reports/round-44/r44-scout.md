# Round 44 scout — ordinary duration tolerance vs distinctness

## Map

The declared control concerns the per-file ordinary duration check in `measure()`: `duration = float(ffprobe format.duration)` and failure is appended only when `abs(duration - spec[0]) > .001` (`duration: outside ±1 ms`). This is distinct from the R27 pairwise distinctness duration arm, which compares `abs(variant_duration - baseline_duration) >= .020` (or accepts when centroid-relative delta is `>= .10`). R27's 6719/6720-frame pair tested the `.020 s` pairwise rule, using separately declared duration specs for the longer scratch variants; it did not calibrate the ordinary ±.001 s per-file check.

For a target UI duration of .12 s at 48 kHz, 5760 frames is nominal. 5807 frames is 47 extra frames: `47/48000 = 0.0009791666666666666 s` nominal deviation, inside .001. 5809 is 49 extra: `49/48000 = 0.0010208333333333334 s`, outside .001. Their nominal durations are `5807/48000 = 0.12097916666666667` and `5809/48000 = 0.12102083333333333` seconds. Adjacent counts are 1/48000 s apart; 5808 frames is nominally .001 s above target, but is not part of this pair or an equality claim.

These are frame-count arithmetic predictions, not measurements of candidate files. ffprobe reports a decimal duration string (the canonical UI fixture below reports six decimal places); Python parses that string to binary float before the strict `> .001` test. Therefore the actual probed duration and computed delta determine each outcome. Do not infer exact equality from frame arithmetic or decimal presentation. A proper paired fixture would need 5807 exit 0/no failures and 5809 exit 1 solely for the ordinary duration failure, with the other ordinary checks passing. Distinctness's `.020` threshold is 20 times larger than this ordinary tolerance and measures a different pairwise property; do not conflate the two.

## Shell evidence and limits

One shell invocation was malformed by quoting the whole command as a single executable; it returned **127**, so it is a shell/setup error, not a fixture or numeric failure. Exact attempted command:

```sh
"ffprobe -v error -show_entries 'stream=sample_rate,channels,codec_name,bits_per_sample:format=duration' -of json .shokunin/audio/corpus/artifacts/ui.wav"
```

The corrected exact command was:

```sh
ffprobe -v error -show_entries 'stream=sample_rate,channels,codec_name,bits_per_sample:format=duration' -of json .shokunin/audio/corpus/artifacts/ui.wav
```

Exit **0**. Output: sample rate 48000, mono, `pcm_s16le`, 16 bits, `format.duration: "0.120000"`. This is only the existing canonical UI artifact's ffprobe result; it is not a probe of either proposed frame-count candidate. I did not run the runner, generate candidates, or measure candidate ffprobe durations, deltas, hashes, or exits. Thus there are no candidate numeric-fit results (successful or failed) to report, and no inference that the declared calibration pair has passed. Setup error above is kept separate from numeric fit status.

Numerical fixture calibration only. No audition, quality, production, rights, engine, publishing, or promotion inference.
