# r20-scout — 200 Hz internal-gap mode coverage claim

Role: READ ONLY scout. Wrote only this path. No probe built, no commits.

Worktree: `/home/vgpnk/Projects/prymeagnt/audio` branch `craft/audio-r1` HEAD `a905a26`.

## 1. r19 verifier table — 16 mode rows, flags, 200 Hz gap?

Source: `.shokunin/audio/reports/round-19/r19-verifier.md`.

Row count: **exactly 16** mode invocations (table rows 1–16).

| # | Flag / command mode | Exit |
|---:|---|---:|
| 1 | *(no probe flag — normal)* `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 |
| 2 | `--probe-layer-third-slope-edge-pass` | 0 |
| 3 | `--probe-layer-third-slope-edge-fail` | 1 |
| 4 | `--probe-layer-third-slope` | 1 |
| 5 | `--probe-layer-alt-reverse` | 1 |
| 6 | `--probe-layer-alt-slope` | 1 |
| 7 | `--probe-layer-alt-join` | 1 |
| 8 | `--probe-layer-alt-flat` | 1 |
| 9 | `--probe-layer-slope` | 1 |
| 10 | `--probe-layer-join` | 1 |
| 11 | `--probe-flat` | 1 |
| 12 | `--probe-layer-flat` | 1 |
| 13 | `--probe-slope` | 1 |
| 14 | `--probe-failing` | 1 |
| 15 | `--probe-invalid` | 1 |
| 16 | *(no probe flag — normal replay)* | 0 |

**200 Hz internal-gap route?** **No.** 200 Hz (`stem_layer_third`) appears only as:

- `--probe-layer-third-slope`
- `--probe-layer-third-slope-edge-pass`
- `--probe-layer-third-slope-edge-fail`

All three are **side-slope** controls (failure text `internal join side slope mismatch > .001 full scale per sample`). Gap-only routes in the table are **120 Hz** `--probe-layer-join` and **180 Hz** `--probe-layer-alt-join` (`join_probe: internal join adjacent sample gap > .03 full scale`). There is **no** `--probe-layer-third-join`.

### Search evidence (not assumption)

Commands run from repo root (Python scan equivalent to grep):

```text
# measure_audio.py lines matching join|third (case-insensitive)
28: SPECS stem_layer_third
92-106: internal_join_* fields; join_delta/join_slope at samples[95998..96001]
152: --probe-layer-join
155: --probe-layer-alt-join
158-160: --probe-layer-third-slope, -edge-pass, -edge-fail
# NO --probe-layer-third-join argument
199-201: probe_layer_join -> join_probe / stem_layer (120 Hz)
208-210: probe_layer_alt_join -> join180_probe / stem_layer_alt (180 Hz)
217-223: third modes -> slope200_probe / edgepass_probe / edgefail_probe only
244-247: gap failure append includes join_probe + third slope probes; slope failure list includes third slope probes but OMITs join_probe

# build_artifacts.py
99: save stem_layer_third 200 Hz
100-118: layer_third_slope* only (+8 / +2 / +3 at frame 96001)
138-149: layer_alt_join_probe (180 Hz)
151-158: join_probe (120 Hz stem_layer)
191-199: CLI flags — join, alt-join, third-slope* only; NO third-join
```

Exact check used:

```python
import re
from pathlib import Path
for p in [
    Path('.shokunin/audio/corpus/fixtures/measure_audio.py'),
    Path('.shokunin/audio/corpus/fixtures/build_artifacts.py'),
]:
    for i, line in enumerate(p.read_text().splitlines(), 1):
        if re.search(r'join|third', line, re.I):
            print(f'{p}:{i}: {line}')
```

Result: **no** `third-join` / `probe-layer-third-join` / `join200` symbol in either file. Claim “no 200 Hz gap mode” is a search result.

## 2. Decode `stem_layer_third.wav`

Path: `.shokunin/audio/corpus/artifacts/stem_layer_third.wav`  
SHA-256: `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445` (matches parent + r19).  
Frames: **192000**, 48 kHz mono PCM16.

### PCM16 direct (`wave` + `<i2`)

Signed counts at zero-based frames:

| frame | count |
|---:|---:|
| 95998 | **-26** |
| 95999 | **-13** |
| 96000 | **0** |
| 96001 | **43** |

### SoX path (same as runner)

```bash
sox .shokunin/audio/corpus/artifacts/stem_layer_third.wav -t f32 -e floating-point -
```

Exit: **0**. `np.frombuffer(..., dtype="<f4")` length **192000**.

| frame | float32 FS | ×32768 (exact int) |
|---:|---:|---:|
| 95998 | -0.00079345703125 | -26.0 |
| 95999 | -0.000396728515625 | -13.0 |
| 96000 | 0.0 | 0.0 |
| 96001 | 0.001312255859375 | 43.0 |

**PCM16 vs SoX:** identical when SoX floats are scaled by **32768** (diffs all 0.0). Scaling by 32767 does **not** match (sub-count residuals). Runner gate math uses SoX float64 samples; equivalent integer math is count/32768.

### Canonical join arithmetic (measured)

```text
gap   = abs(s[96000]-s[95999]) = abs(0 - (-13)) = 13 counts
      = 13/32768 = 0.000396728515625 FS   (pass: not > .03)
slope = abs((s[96001]-s[96000])-(s[95999]-s[95998]))
      = abs((43-0)-(-13-(-26))) = abs(43 - 13) = 30 counts
      = 30/32768 = 0.00091552734375 FS/sample   (pass: not > .001)
```

**Note vs parent brief:** parent wrote gap `0/32768` while listing counts `[-26,-13,0,43]`. Measured gap is **13**, not 0. Outer seam (not these frames): `abs(s[0]-s[-1]) = 43/32768 = 0.001312255859375`; outer slope `30/32768 = 0.00091552734375` (both pass).

## 3. Smallest integer offset N and dual-frame edit

Threshold: gap FS `> .03` iff counts gap `> 0.03 * 32768 = 983.04`, so integer gap **≥ 984**.

### N such that N/32768 > .03 (parent style)

```text
min N with N/32768 > .03: N = 984
  983/32768 = 0.029998779296875  (not > .03)
  984/32768 = 0.030029296875     (> .03)
parent hypothesis N = 1050
  1050/32768 = 0.03204345703125
```

### Edit: `frames[96000] += N` and `frames[96001] += N` (N=1050)

Preserves two-frame step `s[96001]-s[96000]`:

```text
before step 96000→96001: 43 - 0 = 43
after  (0+1050)=1050, (43+1050)=1093; step = 43 (unchanged)
left step 95998→95999: -13 - (-26) = 13 (unchanged)
side-slope counts = abs(43 - 13) = 30  → 30/32768 = 0.00091552734375  (still ≤ .001; not > .001)
```

Gap after edit:

```text
abs((0+1050) - (-13)) = 1063 counts
1063/32768 = 0.032440185546875 FS  > .03  → gap gate trips
```

**Smallest N that trips gap with this dual-frame pattern** (baseline gap 13 toward negative neighbor): need `abs(N - (-13)) = N+13 ≥ 984` ⇒ **N ≥ 971**. Parent’s “N/32768 > .03” floor **984** still works and is slightly larger.

### Outer endpoint / outer slope impact

Frames 96000/96001 are the **internal** mid-file join, not loop ends. Dual-frame +N **does not change** `s[0], s[1], s[-2], s[-1]`. Outer endpoint and outer slope **unchanged** at the values above.

## 4. Predicted gates: trip vs must-not-trip

Runner failure append strings (from `measure_audio.py`):

```text
sections: internal join adjacent sample gap > .03 full scale
sections: internal join side slope mismatch > .001 full scale per sample
sections: {hz} Hz component amplitude contrast < 6 dB or invalid
loop seam: endpoint jump > .03 full scale
loop seam: slope mismatch > .001 full scale per sample
```

r19 **receipt short forms** for existing join modes:

```text
join_probe: internal join adjacent sample gap > .03 full scale
```

(from failures on measurement key `join_probe`).

### Hypothesis prediction (N=1050 on both 96000 and 96001; scratch WAV; not integrated)

| Gate | Prediction | Why |
|---|---|---|
| **Internal adjacent gap > .03** | **SOLE expected trip** | gap 0.03244 FS > .03 |
| Internal side-slope > .001 | **must not** | still 30/32768 ≈ 0.000916 |
| 200 Hz contrast ≥ 6 dB | **must not** | in-memory FFT on mod/32768: contrast ≈ **10.45725 dB** (canonical ≈ 10.45724); amps still ≥ .01; rms ≥ .001 |
| Loop outer endpoint / outer slope | **must not** | ends untouched |
| format / duration / level / centroid band | **must not** (expected) | still 4.0s 48k mono; peak still ≈ 0.04999 < .95 |
| distinctness of unrelated `_alt` pair | **must not** | canonical alts unchanged if builder only adds scratch probe |

**Predicted sole failure string** once a future `--probe-layer-third-join` wires a measurement name like `join200_probe` through `section_contrast(..., 200)` and the gap append path:

```text
sections: internal join adjacent sample gap > .03 full scale
```

Receipt summary style (by analogy to r19 join rows):

```text
join200_probe: internal join adjacent sample gap > .03 full scale
```

(exact measurement key TBD by integrator — not present today).

### Important runner asymmetry (unknown for integrator)

`join_probe` (120 Hz) is on the **gap** failure name-list but **omitted** from the **side-slope** failure name-list (`measure_audio.py` ~244–247). `join180_probe` **is** on both lists. A new 200 Hz join probe must be added to the gap list (and to `section_contrast` 200 Hz branch + SPECS-like measure call). Whether it is also added to the slope list affects whether a sloppy edit could hide a dual failure — hypothesis keeps slope safe either way.

## 5. Short Python prediction (no probe built)

```python
import wave
import numpy as np
from pathlib import Path

path = Path(".shokunin/audio/corpus/artifacts/stem_layer_third.wav")
with wave.open(str(path), "rb") as w:
    s = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float64)
N = 1050  # or min gap-trip dual-edit N=971; parent floor N=984
mod = s.copy()
mod[96000] += N
mod[96001] += N
gap = abs(mod[96000] - mod[95999]) / 32768
slope = abs((mod[96001] - mod[96000]) - (mod[95999] - mod[95998])) / 32768
# gap > .03 and slope <= .001  →  predicted sole internal gap fail
```

Observed with N=1050: `gap=0.032440185546875`, `slope=0.00091552734375`.

## Remaining unknowns

1. Integrator measurement key / live path naming (`join200_probe` vs other) and whether slope-check name-list includes the new probe (join120 omits slope check; join180 includes it).
2. Whether builder copies canonical PCM then patches (like slope200) or resynthesizes (like join180) — hypothesis assumes **copy + dual-frame +N**; resynthesis could drift contrast/peak.
3. SoX float path on the **scratch** file not executed here (scout did not write scratch); prediction uses PCM/32768 ≡ SoX on canonical.
4. Parent brief gap “0 FS” vs measured **13 counts** — arithmetic uses measured 13.
5. Second-gate fit search if contrast ever fails: not required at N=1050 in float prediction; unproven until runner receipt exists.
6. r19 row 1 and 16 both normal — not a new mode class; coverage claim correctly targets missing **gap-only 200 Hz** class.

## 5-line finding (for parent message)

1. r19 table has **16** modes; flags listed above; **no** 200 Hz internal-gap route; search shows **no** `third-join` in measure/build.  
2. Canonical frames **[-26, -13, 0, 43]**; SoX≡PCM/32768; gap **13/32768**, slope **30/32768**.  
3. Dual +**N** (1050 or ≥971) keeps slope **30/32768**, outer untouched; gap trips.  
4. Predicted **sole** fail: `sections: internal join adjacent sample gap > .03 full scale` (join-style short form).  
5. No probe built; wire `--probe-layer-third-join` still absent — coverage claim remains open until integrator + verifier.
