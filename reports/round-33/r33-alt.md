# Round 33 alt — independent analytic UI fixture fit

**Scope:** analytic fixture only. No audition, quality, production-readiness, rights, engine, publishing, or promotion claim. The candidate remained scratch at `corpus/live/round-33/alt/ui_third.wav`; no source, LOG, SCORECARD, canonical artifact, or other report was edited. No commits or pushes.

## Method and command

Generated 9,600 frames at 48 kHz, mono PCM16 from the existing UI chirp equation at nominal 0.20 s: `0.38*sin(2*pi*(700*t + 800*t*t))*exp(-30*t)`, clipped and rounded as the project builder does. Invoked the project `measure_audio.py` module's `measure()` directly for `ui`, `ui_alt`, and the scratch candidate, using each file's intended spec (`ui_third`: `(.20,250,4000,False)`). Pair deltas below follow the project `_alt` distinctness convention: absolute duration difference **OR** absolute centroid difference relative to the existing UI file.

Exact shell command: `python3 .shokunin/audio/corpus/live/round-33/alt/fit.py` — **exit 0**. No failed fit or setup failure.

## Measurements

| File | Measured duration (s) | Rate / channels / codec / bits | Peak | RMS dBFS | Centroid Hz | Ordinary helper failures |
|---|---:|---|---:|---:|---:|---|
| `ui` | 0.12 | 48000 / 1 / pcm_s16le / 16 | 0.375946044921875 | -19.991687666366516 | 966.8966593379727 | none |
| `ui_alt` | 0.16 | 48000 / 1 / pcm_s16le / 16 | 0.31878662109375 | -20.525534144496497 | 1423.1532540422852 | none |
| scratch `ui_third` | 0.20 | 48000 / 1 / pcm_s16le / 16 | 0.375946044921875 | -22.20695387316763 | 966.7216217320357 | none |

| Existing UI baseline → candidate | Duration delta (s) | Relative centroid delta | Duration arm (`>=.020`) | Centroid arm (`>=.10`) | Existing OR rule |
|---|---:|---:|---|---|---|
| `ui` → `ui_third` | 0.08000000000000002 | 0.00018103031409457665 | true | false | pass |
| `ui_alt` → `ui_third` | 0.04000000000000001 | 0.3207185389302337 | true | true | pass |

Candidate ordinary per-file checks pass under its declared 0.20 s UI-band spec. Pair rule passes against both existing UI files; the `ui` comparison passes only through duration, while `ui_alt` passes both arms. This demonstrates the specified numeric fixture check only; duration alone does not establish perceptual distinctness or fixture quality. Candidate is scratch, not a proposed canonical artifact; parent integration and round gates remain outstanding.
