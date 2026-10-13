# R42 simplifier review

## Declaration read

Read `.shokunin/audio/LOG.md`, “Round 42 declared calibration claim and wave spec.” The scoped move is a decoded PCM16 peak bracket at 31129/32768 = 0.949981689453125 (pass) and 31130/32768 = 0.95001220703125 (fail), for original 0.12 s / 5760-frame / 48 kHz mono PCM16 UI-shaped scratch WAVs. The latter must fail only `level: clipping headroom or near silence`; both must pass other ordinary checks. The comparator remains unchanged (`peak >= .95`). This does not test equality at .95.

## Minimal-diff recommendation

Keep this to the two opt-in modes and their pair-specific source generator / measurement dispatch. Avoid a generic probe framework, shared threshold or measurement changes, canonical fixture changes, and all unrelated modes. Generate integer PCM whose decoded absolute maximum is exactly the declared count; a floating-point target alone is not sufficient. Verify decoded PCM count, format/frame count, RMS, centroid and all failure lists from the receipts; hash-pin the two distinct fixtures. Report any fit that misses another constraint as a numeric failed fit, separate from setup errors (e.g. command/path/tool/generation failure).

## Evidence from this review

I ran no fixture generator, decoder, or measurement command, so this review has no decoded-count result, numeric fit result, or setup error. The only shell command run was `git status --short` (exit 0); it showed the LOG modified and untracked round-42 scratch files already present, which I did not change. No command output is treated as calibration evidence.

This is a minimal-diff review only. No inference about audition, sound quality, production, rights, engine use, publishing, or promotion.
