# r20-executor — round 20 leaf report

**Role:** r20-executor (leaf). Worktree `/home/vgpnk/Projects/prymeagnt/audio`, branch `craft/audio-r1`, HEAD `a905a26`.

**Verdict:** `join200_candidate.wav` is a **sole-gap fit** (numpy/sox prediction; runner has no `--probe-layer-third-join` yet).

**Report path:** `.shokunin/audio/reports/round-20/r20-executor.md`  
**Scratch WAV:** `.shokunin/audio/corpus/live/round-20/join200_candidate.wav`

---

## 1. Build candidate

Loaded canonical PCM16 `stem_layer_third.wav`, copied, applied `frames[96000] += 1050` and `frames[96001] += 1050` (int16, no wrap), wrote mono 48 kHz sampwidth-2 WAV matching `build_artifacts.py` header style.

```python
# Python (REPL), cwd /home/vgpnk/Projects/prymeagnt/audio
import wave, hashlib, numpy as np
from pathlib import Path
RATE = 48000
CANON = Path('.shokunin/audio/corpus/artifacts/stem_layer_third.wav')
OUT = Path('.shokunin/audio/corpus/live/round-20'); OUT.mkdir(parents=True, exist_ok=True)
with wave.open(str(CANON), 'rb') as w:
    frames = np.frombuffer(w.readframes(w.getnframes()), dtype='<i2').copy()
# frames[95998:96002] == [-26, -13, 0, 43]
cand = frames.copy()
cand[96000] += 1050
cand[96001] += 1050
# cand[95998:96002] == [-26, -13, 1050, 1093]
# only changed indices: [96000, 96001]
with wave.open(str(OUT / 'join200_candidate.wav'), 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE)
    w.writeframes(cand.astype('<i2').tobytes())
```

**Exit:** success (no exception). File size 384044 bytes.

## 2. SHA-256 and changed frames

| file | SHA-256 |
|------|---------|
| canonical `stem_layer_third.wav` | `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445` (matches parent) |
| candidate `join200_candidate.wav` | `b3d8f595514ed413826ce861e0b18d29de676fcd23916313c21db8cf5184568e` |

Changed frame indices only: **96000, 96001**.

## 3. Measure (runner-equivalent prediction)

Runner decode path is `sox PATH -t f32 -e floating-point -` then `np.frombuffer(..., dtype="<f4")`.  
**This is a direct numpy/sox measure = prediction until parent wires `--probe-layer-third-join`.**

```bash
# sox decode used via Python subprocess.run(..., check=True) — exit 0
sox .shokunin/audio/corpus/live/round-20/join200_candidate.wav -t f32 -e floating-point -
# ffprobe
ffprobe -v error -show_entries stream=sample_rate,channels:format=duration -of json \
  .shokunin/audio/corpus/live/round-20/join200_candidate.wav
```

**ffprobe exit:** 0  
**ffprobe:** sample_rate 48000, channels 1, duration 4.000000

Decoded float32 samples at join (sox scale = count/32768):

| index | count | float |
|------:|------:|------:|
| 95998 | -26 | -0.00079345703125 |
| 95999 | -13 | -0.000396728515625 |
| 96000 | 1050 | 0.03204345703125 |
| 96001 | 1093 | 0.033355712890625 |

### Internal join (section_contrast formulas)

- **gap** `abs(s[96000]-s[95999])` = **0.032440185546875** FS (= 1063/32768)  
  - threshold fail if `> .03` → **FAILS gap gate** (desired negative)
- **side-slope** `abs((s[96001]-s[96000])-(s[95999]-s[95998]))` = **0.00091552734375** FS/sample (= 30/32768)  
  - threshold fail if `> .001` → **PASSES** (≤ .001)

Design: same +1050 on both 96000 and 96001 keeps two-frame step identical to canonical (43 counts), so slope stays 30 counts.

### 200 Hz section contrast (section_contrast style)

- `component_bin = 200 * 96000 // 48000` = **400**
- amplitudes FS: half0 ≈ **0.014999984892417233**, half1 ≈ **0.04999805655680512**
- RMS FS: ≈ **0.0106065941723389**, **0.03535426841712669**
- valid (amps ≥ .01, rms ≥ .001): **True**
- contrast dB: **10.457246036573986** (≥ 6) → **PASSES**

### Outer seam / generic (measure loop gates + level)

- outer endpoint `abs(s[0]-s[-1])` = **0.001312255859375** ≤ .03 → **PASS**
- outer slope `abs((s[-1]-s[-2])-(s[1]-s[0]))` = **0.00091552734375** ≤ .001 → **PASS**
- peak FS ≈ **0.04998779296875** < .95 → **PASS**
- rms ≈ **0.026100039609614916** (≥ .001); rms_dbfs ≈ **-31.667** → **PASS**
- format 48 kHz mono 4.0 s → **PASS**

## 4. Sole-gap isolation

| gate | result |
|------|--------|
| internal gap > .03 | **FAIL (only intentional)** |
| internal side-slope > .001 | pass |
| 200 Hz contrast ≥ 6 dB | pass (~10.457 dB) |
| outer seam / outer slope | pass |
| peak/rms/format | pass |

**No second gate fails.** Offset N=1050 is already the hypothesized fit; **no alternate N needed.**

Canonical was not modified. Builder/runner/MANIFEST/SCORECARD/LOG/PROVINCE/SHONEN untouched.

## 5. Finding (5 lines)

1. Wrote sole-gap scratch `.shokunin/audio/corpus/live/round-20/join200_candidate.wav` (SHA-256 `b3d8f595514ed413826ce861e0b18d29de676fcd23916313c21db8cf5184568e`) from canonical third layer +1050 on frames 96000–96001 only.  
2. sox float32 gap = 0.032440185546875 > .03; side-slope = 0.00091552734375 ≤ .001; contrast ≈ 10.457 dB; outer/generic pass.  
3. Candidate is a **sole-gap fit** for future `--probe-layer-third-join` (200 Hz internal-gap-only scratch negative).  
4. Measurements are **numpy/sox predictions**, not a wired runner mode (r19 has no third-join route).  
5. Parent must add route + pair negative control; leaf did not edit runner/builder or commit.

## Commands / exits summary

| step | command / action | exit |
|------|------------------|------|
| write WAV | Python `wave.open` write | 0 / ok |
| sox f32 decode candidate | `sox ... -t f32 -e floating-point -` via subprocess check=True | 0 |
| sox f32 decode canonical | same | 0 |
| ffprobe candidate | `ffprobe -v error -show_entries stream=sample_rate,channels:format=duration -of json <cand>` | 0 |
| measure_audio.py --probe-layer-third-join | **not run** (mode absent; leaf must not edit runner) | n/a |

Setup: none failed. No multi-gate failure. Canonical SHA unchanged.
