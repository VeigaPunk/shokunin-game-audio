# r20-alt — independent 200 Hz internal-gap isolation (counterexample lane)

**Role:** r20-alt leaf. Worktree `/home/vgpnk/Projects/prymeagnt/audio`, branch `craft/audio-r1`, HEAD `a905a265517828d2d10efc33b7dbcf36655e935f`.  
**Write paths only:** `.shokunin/audio/corpus/live/round-20/*other*` and this report. No builder/runner/MANIFEST edits. No commits.

## Canonical baseline (re-verified)

```text
$ python3 - <<'PY'
# wave+sha of .shokunin/audio/corpus/artifacts/stem_layer_third.wav
PY
```

- SHA-256: `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445` (matches brief)
- PCM16 mono 48 kHz, 192000 frames
- Decoded int16 frames 95998–96001: **[-26, -13, 0, 43]** (matches brief)
- Internal gap `abs(s[96000]-s[95999])` = **13/32768 = 0.000396728515625 FS** (brief said 0; actual is 13 counts — still ≪ 0.03)
- Side-slope `abs((s[96001]-s[96000])-(s[95999]-s[95998]))` = **30/32768 = 0.00091552734375 FS/sample** (≤ 0.001)

**Gap math for both-frame +N:** new gap counts = `|(0+N) - (-13)| = N+13`. Threshold 0.03 FS = 983.04 counts ⇒ need **N+13 ≥ 984** ⇒ **N ≥ 971**. Side-slope stays 30 if both 96000 and 96001 get the same +N.

Design hypothesis N=1050 assumed gap = N/32768 from a 0→N step; with real left sample -13, gap is **(N+13)/32768**.

## Commands and exits (sox float32 decode)

All trials: copy canonical PCM16, patch, `wave` write, then:

```bash
sox <path> -t f32 -c 1 <path>.f32
# exit 0 every trial below
```

Python/`wave` path used for exact int16 edits; sox used for FS metrics (identical to int16/32768 for these values).

## Table of N results

| mode | N | frames 95998–96001 | gap FS (sox) | side-slope FS/sample (sox) | gap > .03 | slope ≤ .001 | sole-gap class? |
|------|---:|--------------------|-------------:|---------------------------:|:---------:|:------------:|:---------------:|
| both +N | 984 | [-26, -13, 984, 1027] | 0.030426025390625 | 0.00091552734375 | Y | Y | **YES** |
| both +N | 1050 | [-26, -13, 1050, 1093] | 0.032440185546875 | 0.00091552734375 | Y | Y | YES |
| both +N | 2000 | [-26, -13, 2000, 2043] | 0.061431884765625 | 0.00091552734375 | Y | Y | YES (overshoot) |
| only 96000 +N | 984 | [-26, -13, 984, 43] | 0.030426025390625 | 0.02911376953125 | Y | **N** | NO (gap+slope) |
| only 96000 +N | 1050 | [-26, -13, 1050, 43] | 0.032440185546875 | 0.0311279296875 | Y | **N** | NO |
| only 96000 +N | 2000 | [-26, -13, 2000, 43] | 0.061431884765625 | 0.06011962890625 | Y | **N** | NO |

**Paired-control distinction:** adding N only to frame 96000 (not 96001) keeps the same gap but blows side-slope to ~N/32768 (≫ 0.001). That is **not** the selected gap-only class. Compensated both-frame +N is required so slope stays 30/32768.

Trial WAVs (scratch, names contain `other`):

- `.shokunin/audio/corpus/live/round-20/trial_both_N984_other.wav`
- `.shokunin/audio/corpus/live/round-20/trial_both_N1050_other.wav`
- `.shokunin/audio/corpus/live/round-20/trial_both_N2000_other.wav`
- `.shokunin/audio/corpus/live/round-20/trial_only96000_N984_other.wav`
- `.shokunin/audio/corpus/live/round-20/trial_only96000_N1050_other.wav`
- `.shokunin/audio/corpus/live/round-20/trial_only96000_N2000_other.wav`

## Selected sole-gap scratch

**Best N = 984** (smallest tested integer that still fails gap while preserving slope; tighter than design 1050).

- **File:** `.shokunin/audio/corpus/live/round-20/join200_other.wav`
- **SHA-256:** `9214de79c9d87d5760cb349170e412daca7867ce9f2c0e6f9682877953c4755e`
- **Patch:** PCM16 copy of canonical; `s[96000] += 984`; `s[96001] += 984`
- **sox metrics:** gap=0.030426025390625, side=0.00091552734375, sox exit=0
- N=1050 also isolates gap alone (side unchanged); parent may prefer either. **r20-alt prefers 984.**

No `--probe-layer-third-join` flag exists yet in `measure_audio.py` (r19: third only has slope/edge routes). This lane did **not** edit the runner; fixture measure of the new mode is parent/executor work. Scratch is not a new canonical WAV.

## Misread warning (one way)

Someone could treat `join200_other.wav` as a **new canonical 200 Hz layer** or as evidence that the **0.03 gap threshold should move** because 984 is “barely over.” It is neither: it is a **live scratch negative** that deliberately trips the existing gap gate only, with thresholds and canonical `stem_layer_third.wav` unchanged.

## 5-line finding

1. Real join samples are [-26,-13,0,43]; both-frame +N yields gap=(N+13)/32768, side fixed at 30/32768.  
2. N∈{984,1050,2000} all isolate gap>0.03 with slope≤0.001 when both frames are offset.  
3. Offset on 96000 alone fails slope (side≈0.029–0.060) — not the gap-only class.  
4. Wrote `join200_other.wav` at **N=984**, SHA `9214de79c9d87d5760cb349170e412daca7867ce9f2c0e6f9682877953c4755e` (differs from design 1050; both valid).  
5. Not a canonical and not a threshold change — scratch counterexample for future `--probe-layer-third-join` only.
