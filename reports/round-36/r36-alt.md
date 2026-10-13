# Round 36 — independent ambience candidate fit (alt)

## Scope and result

Fit one independent original 2.0-second loop candidate with the project measurement helper. Candidate and fitter scratch are confined to `corpus/live/round-36/alt/`; this is not a canonical artifact. The fit passed the declared format, duration, 5–200 Hz centroid band, peak/RMS, and loop seam checks. Both explicit pair comparisons pass the unchanged `.020 s OR .10 relative centroid` rule; duration contributes zero, so the centroid arm alone passes.

## Candidate measurements

`ambience_alt_candidate.wav` SHA-256: `c2c8e0bb2385bc93b39c70b719d0f56553c771969986ef1f732d24af5677d404`.

Project helper result: 2.0 s; 48,000 Hz mono PCM16; peak `0.225006103515625` FS; RMS `-16.92261930553234` dBFS; weighted positive-frequency centroid `112.03210352691181` Hz; bandwidth `528.6301100034675` Hz; endpoint delta `0.002777099609375` FS; seam side-slope mismatch `0.0` FS/sample; failures `[]`.

| Existing baseline | Baseline centroid (Hz) | Duration delta (s) | Relative centroid delta | Rule result |
|---|---:|---:|---:|---|
| `ambience` | 36.61640767851373 | 0.0 | 2.059614818322321 | pass: centroid arm |
| `ambience_alt` | 58.01919713436623 | 0.0 | 0.9309488765840295 | pass: centroid arm |

Existing baselines were read from canonical WAVs with the same helper and loop specification; their measured durations are both 2.0 s and their helper failures are empty.

## Commands and setup

Exact shell command and exit status:

- `python3 .shokunin/audio/corpus/live/round-36/alt/fit_candidate.py` — exit `0`.

The helper loads `fixtures/measure_audio.py` and measures the candidate at its live scratch path. The two baseline measurements used these exact Python commands (invoked from the project via `subprocess.run`, each exit `0`):

- `python3 -c 'import sys;sys.path.insert(0,"/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/fixtures");import measure_audio as m;print(m.measure("ambience",(2,5,200,True)))'`
- `python3 -c 'import sys;sys.path.insert(0,"/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/fixtures");import measure_audio as m;print(m.measure("ambience_alt",(2,5,200,True)))'`

No failed setup or fit command occurred.

## Limits

These are numerical proxies only. Seam metrics do not establish seamless perception; centroid difference does not establish perceived novelty or musical quality. No audition, production, rights, engine, publish, or promotion claim is made. Parent integration and verification are required before any canonical status; this candidate is not canonical.
