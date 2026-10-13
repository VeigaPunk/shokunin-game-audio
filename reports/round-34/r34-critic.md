# Round 34 critic — numeric proxy falsification

## Scope and result

This is a numeric fixture/proxy challenge only. It makes no perception, sound-quality, production, rights, engine, publishing, or promotion claim. I did not edit the LOG, SCORECARD, source, canonical artifacts, or another report. No candidate was retained in the canonical artifact directory.

The existing distinctness predicate is an OR: duration delta ≥0.020 s **or** relative whole-wave FFT centroid delta ≥0.10. For a .40 s candidate against either declared .32 s impact, duration alone is .08 s and clears the predicate. Thus a two-pair “pass” does not establish spectral difference on both pairs; it can pass even if both centroid deltas are zero. A shared duration target for both pairs also makes the duration evidence duplicated, not two independent dimensions.

## Numeric challenge

I made a scratch-only 48 kHz mono PCM16 candidate: 0.38-amplitude exponentially decaying linear chirp, `sin(2π(1800t + 3000t²)) exp(-18t)`, at .40 s. I also truncated the identical generated signal to .32 s. Both were measured by the project `measure()` implementation; neither is canonical.

| Input | Duration | Centroid (Hz) | Bandwidth (Hz) | Peak FS | RMS dBFS | ordinary failures |
|---|---:|---:|---:|---:|---:|---|
| `impact.wav` | .32 s | 10843.127203 | 7693.962697 | .808777 | -20.402187 | none |
| `impact_alt.wav` | .32 s | 473.791536 | 1435.019898 | .756165 | -17.329571 | none |
| scratch .40 s candidate | .40 s | 2215.983112 | 1577.483934 | .377808 | -22.998533 | none |
| same candidate truncated to .32 s | .32 s | 2217.729164 | 1590.018717 | .377808 | -22.029474 | none |

Candidate-vs-impact relative centroid delta is **0.795632**; candidate-vs-impact_alt is **3.677127**. Those exceed .10, but both comparisons also pass from duration alone (.08 s). Truncating the exact same candidate by .08 s changes centroid only **0.000788 relative** (~0.079%), while satisfying an exactly equal .32 s duration target. This is a direct duration/truncation confound: duration change is sufficient for the pair predicate and need not imply meaningful spectral proxy change. Conversely, a single centroid is a lossy scalar: the measurement does not compare spectra, and matching/near-matching centroids cannot establish matching spectral distributions. Therefore the proposed pairwise centroid+duration receipts support only those numeric scalar comparisons, not “spectrally distinct” content or perceptual distinctness.

Candidate SHA-256: `bdcc241c3bd4e6e61c56377389326688bbda1abbc8ddb32123871f30fcceee37`; truncated scratch SHA-256: `1071ef0bbbff618f1046eee2b4a897519e5588c58c56b818b0548b73de41fe59`. Existing impacts SHA-256 observed: `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc` and `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6`.

## Command receipts and setup failures

- Exact command: `python3 /tmp/r34_critic.py` — exit **1** on initial setup because the temporary script imported unavailable `scipy`; no fit result was produced. Removed the unused import.
- Exact command: `python3 /tmp/r34_critic.py` — exit **1** on next setup because project `measure()` requires a path relative to its corpus root and scratch was initially outside that root; no candidate measurement was produced. Moved scratch under `corpus/live/round-34/critic-scratch/` (not `artifacts/`) and reran.
- Exact command: `python3 /tmp/r34_critic.py` — exit **0**, produced the table and hashes above. These are temporary scratch measurements; scratch WAVs were removed after recording results. No fit failure is being counted as evidence.

## Assessment

The pair condition is falsifiable as a spectral claim: duration-only passes are explicitly allowed, and a centroid is not a full-spectrum comparison. If the parent integrates the proposed third fixture, describe it only as another fixture with recorded duration/centroid/ordinary-check values. Do not infer spectral or perceptual novelty from a two-pair OR pass.
