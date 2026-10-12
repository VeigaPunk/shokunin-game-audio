# r20-reviewer — minimal builder/runner diff for `--probe-layer-third-join`

**Role:** READ ONLY advisory. Parent applies edits. This leaf did not edit `build_artifacts.py`, `measure_audio.py`, canonical WAVs, thresholds, MANIFEST, SCORECARD, LOG, PROVINCE, SHONEN.

**Worktree:** `/home/vgpnk/Projects/prymeagnt/audio` (branch `craft/audio-r1`, HEAD a905a26 assumed at spawn).

**Coverage claim (round 20):** add exactly one previously uncovered mode class — 200 Hz **internal-gap-only** scratch negative — flag `--probe-layer-third-join`, live WAV `live/round-20/join200_probe.wav`, measurement name `join200_probe`. Not a new canonical WAV. Paired negative control is the gap failure itself (isolated from slope/contrast/generic/outer if the integer offset fit holds).

**Design hypothesis (unmeasured here):** copy canonical `stem_layer_third.wav` PCM16; add integer offset **1050** to frames **96000** and **96001** so:
- gap `abs(s[96000]-s[95999])` becomes `(0+1050)/32768 = .03204345703125 FS > .03` → internal-gap fail
- side-slope stays `30/32768 = .00091552734375 FS/sample ≤ .001` (same two-frame step as canonical)
- 200 Hz contrast about +10.457 dB unchanged if only those two samples move by the same amount
- outer seam / generic gates expected pass

If a second gate fails after parent lands the mode, try the **smallest integer offset ≥ 984** (`ceil(.03*32768)+ε` relative to s[95999]=−13 → need s[96000] such that |s[96000]+13| > .03*32768 ≈ 983.04, so offset from 0 needs >983; 1050 is the hypothesized start) that isolates gap only. **Do not relax thresholds. Do not rewrite canonical.**

---

## 1. Sites inspected (exact)

### `build_artifacts.py`
| Site | Lines (approx) | Current |
|------|----------------|---------|
| `main(...)` signature | L60 | ends `..., layer_third_slope_edge_fail=False)` — **no** `layer_third_join_probe` |
| third-slope / edge blocks | L100–123 | copy `stem_layer_third.wav`, mutate `frames[96001]` only, write `live/round-18` or `round-19` |
| argparse flags | L185–200 | last third flags: `--probe-layer-third-slope`, `-edge-pass`, `-edge-fail`; **no** `--probe-layer-third-join` |
| `main(...)` call | L205 | positional chain of 13 booleans after broken — **must append new arg** |

### `measure_audio.py`
| Site | Lines (approx) | Current |
|------|----------------|---------|
| argparse | L147–161 | mirrors builder; **no** third-join flag |
| **exclusive-mode sum** | L163–164 | `sum([... 14 flags ...]) > 1` → `parser.error` — **must include new flag or multi-mode is allowed** |
| builder invocation | L175–188 | splat list of `*(["--flag"] if args.x else [])` — **must forward new flag** |
| probe path / measure block | L190–223 | pattern: if flag → path under `live/round-N/` → `measurements[name] = measure(..., SPECS[...], path)` |
| `section_contrast` Hz name sets | L236–238 | 200 Hz set: `("stem_layer_third", "slope200_probe", "edgepass_probe", "edgefail_probe")` — **add `join200_probe`** |
| sections dict keys | L239–240 | same names list — **add `join200_probe`** |
| failure append contrast | L241–243 | all section names |
| **internal-gap name tuple** | L244–245 | includes third + slope200 + edges + joins for 120/180 — **add `join200_probe`** |
| **internal-slope name tuple** | L246–247 | note: **`join_probe` (120 Hz) is intentionally NOT in slope tuple**; 180 `join180_probe` **IS** in slope tuple. Task says include `join200_probe` in **both** gap and slope tuples so gap fails and slope is still checked. |
| mode ternary | L248 | nested ternaries ending `... else "normal"` — **insert `probe-layer-third-join` branch** |
| receipt suffix ternary | L265 | parallel chain `-layer-third-slope-...` — **insert `-layer-third-join`** |
| thresholds dict | L250–261 | **do not change** constants `.03`, `.001`, `6.0` |

**Canonical 200 Hz path:** `artifacts/stem_layer_third.wav` only **read** by builder probes (like L101–102 pattern). No write to `ARTIFACTS` / `OUT` for the scratch.

---

## 2. Minimal opt-in (parent should apply)

### A. `build_artifacts.py`

1. **`main` signature (L60):** add `layer_third_join_probe=False` at end of kwargs (after `layer_third_slope_edge_fail`).
2. **New block** (after edge-pass/fail loop ~L123, before `layer_alt_reverse` or after third-edge block — keep third-family together):

```python
    if layer_third_join_probe:
        with wave.open(str(OUT / "stem_layer_third.wav"), "rb") as wav:
            frames = np.frombuffer(wav.readframes(wav.getnframes()), dtype="<i2").copy()
        offset = 1050  # hypothesized gap-only; parent may retune smallest isolating int
        frames[96000] = np.int16(int(frames[96000]) + offset)
        frames[96001] = np.int16(int(frames[96001]) + offset)
        out = OUT.parent / "live" / "round-20"
        out.mkdir(parents=True, exist_ok=True)
        with wave.open(str(out / "join200_probe.wav"), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(RATE)
            wav.writeframes(frames.tobytes())
```

   Notes:
   - Prefer `int(frames[i]) + offset` then clip/cast carefully; canonical values at 95998–96001 are small; 0+1050 and 43+1050 fit int16.
   - **Do not** `save()` into `OUT` (artifacts).
   - **Do not** change L99 `save("stem_layer_third", ...)`.

3. **argparse (after L199):**  
   `parser.add_argument("--probe-layer-third-join", action="store_true")`
4. **`main(...)` call (L205):** append `args.probe_layer_third_join` as last positional (order must match signature).

### B. `measure_audio.py`

1. **argparse (~L160):**  
   `parser.add_argument("--probe-layer-third-join", action="store_true")`
2. **Exclusive sum (L163) — CRITICAL:** append `args.probe_layer_third_join` inside the `sum([...])` list. Omitting it allows combining with other probe modes.
3. **Builder forward (L175–188):** add  
   `*(["--probe-layer-third-join"] if args.probe_layer_third_join else []),`
4. **Measure block (after edge block ~L223):**

```python
    if args.probe_layer_third_join:
        path = ROOT / "live" / "round-20" / "join200_probe.wav"
        measurements["join200_probe"] = measure("join200_probe", SPECS["stem_layer_third"], path)
```

5. **section_contrast Hz (L236):** extend 200 Hz membership:  
   `name in ("stem_layer_third", "slope200_probe", "edgepass_probe", "edgefail_probe", "join200_probe")`
6. **sections comprehension name list (L239–240):** add `"join200_probe"`.
7. **internal-gap tuple (L244):** add `"join200_probe"` (with other layer names).
8. **internal-slope tuple (L246):** add `"join200_probe"` per task (check slope, do not skip) — **unlike** 120 Hz `join_probe` which is gap-only in the slope tuple today.
9. **mode string (L248):** insert near other third modes, e.g.  
   `... else ("probe-layer-third-join" if args.probe_layer_third_join else ("probe-layer-third-slope-edge-pass" if ...`  
   (exact nest order free as long as exclusive sum holds; prefer grouping with third-* flags).
10. **suffix (L265):** parallel  
    `"-layer-third-join" if args.probe_layer_third_join else (...)`  
    so receipt dir is `live/runs/<stamp>-layer-third-join`.

**Do not:** change SPECS, threshold literals, `section_contrast` math, canonical writes, refactors, or unrelated mode chains beyond one new branch each.

---

## 3. Advisory unified diff sketch (parent applies; not applied by reviewer)

```diff
--- a/.shokunin/audio/corpus/fixtures/build_artifacts.py
+++ b/.shokunin/audio/corpus/fixtures/build_artifacts.py
@@ main signature
- def main(..., layer_third_slope_edge_fail=False):
+ def main(..., layer_third_slope_edge_fail=False, layer_third_join_probe=False):
@@ after edge fail/pass block
+    if layer_third_join_probe:
+        with wave.open(str(OUT / "stem_layer_third.wav"), "rb") as wav:
+            frames = np.frombuffer(wav.readframes(wav.getnframes()), dtype="<i2").copy()
+        offset = 1050
+        frames[96000] = np.int16(int(frames[96000]) + offset)
+        frames[96001] = np.int16(int(frames[96001]) + offset)
+        out = OUT.parent / "live" / "round-20"
+        out.mkdir(parents=True, exist_ok=True)
+        with wave.open(str(out / "join200_probe.wav"), "wb") as wav:
+            wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(RATE)
+            wav.writeframes(frames.tobytes())
@@ argparse
+    parser.add_argument("--probe-layer-third-join", action="store_true")
@@ main() call
-        main(..., args.probe_layer_third_slope_edge_fail)
+        main(..., args.probe_layer_third_slope_edge_fail, args.probe_layer_third_join)

--- a/.shokunin/audio/corpus/fixtures/measure_audio.py
+++ b/.shokunin/audio/corpus/fixtures/measure_audio.py
@@ argparse + exclusive sum + builder splat + measure if
+ --probe-layer-third-join / args.probe_layer_third_join in ALL three
+ measurements["join200_probe"] = measure(..., SPECS["stem_layer_third"], live/round-20/join200_probe.wav)
@@ section_contrast 200 Hz set, sections keys, gap tuple, slope tuple
+ "join200_probe"
@@ mode + suffix ternaries
+ "probe-layer-third-join" / "-layer-third-join"
```

---

## 4. Confirmations (reviewer)

| Constraint | Status |
|------------|--------|
| No canonical WAV write in proposed diff | Yes — only `live/round-20/join200_probe.wav` |
| No threshold constant change | Yes — keep `.03`, `.001`, `6.0`, SPECS bands |
| No refactor | Yes — copy existing third-slope / join180 patterns |
| New mode class only | Yes — gap-only 200 Hz; r19 had slope/edge only for 200 Hz |
| Exclusive-mode sum must gain flag | **Warned** — omit ⇒ multi-probe silent combine |
| Mode/suffix ternaries must gain branch | **Warned** — omit ⇒ receipt labeled `normal` while probe ran |
| Scratch not new canonical | Yes |
| This leaf did not edit builder/runner | Yes |

---

## 5. Verification commands parent should run after apply (not run by this leaf)

Exact commands for integrator (quote in LOG as needed):

```bash
cd /home/vgpnk/Projects/prymeagnt/audio
python .shokunin/audio/corpus/fixtures/build_artifacts.py --probe-layer-third-join
# expect: live/round-20/join200_probe.wav exists; artifacts/stem_layer_third.wav SHA unchanged
sha256sum .shokunin/audio/corpus/artifacts/stem_layer_third.wav
# expect: 3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445

python .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join
# expect: exit non-zero (failures present); receipt mode "probe-layer-third-join"
# join200_probe failures include internal join adjacent gap > .03
# join200_probe should NOT list side-slope > .001 if offset fit holds
# contrast still >= 6 dB; outer seam gates pass
```

**Setup errors are telemetry, not passes** — if sox/ffprobe missing, record exit/stderr; do not claim coverage.

**This leaf:** no measure/build executed (advisory-only role). No exit codes collected here.

---

## 6. Five-line finding (for parent message)

1. Add opt-in `--probe-layer-third-join` mirrored in builder `main`/argparse/call and runner argparse/**exclusive sum**/builder forward/measure/sections/gap+slope tuples/mode+suffix.  
2. Builder: read-only copy `stem_layer_third.wav`, add same int offset (start 1050) to frames 96000 and 96001, write `live/round-20/join200_probe.wav` only.  
3. Runner: measure as `join200_probe` with `SPECS["stem_layer_third"]`, `section_contrast` at 200 Hz; include name in internal-gap **and** internal-slope tuples.  
4. Critical footguns: exclusive-mode `sum` and mode/suffix ternaries — missing flag ⇒ combined modes or wrong receipt label.  
5. No canonical write, no threshold edits, no refactor; offset retune only if multi-gate fail after land.

---

## 7. Line checklist (every site that must gain flag or name)

**build_artifacts.py**
- [ ] L60 `main` param `layer_third_join_probe=False`
- [ ] ~L123+ body block → `live/round-20/join200_probe.wav`
- [ ] ~L199 `add_argument("--probe-layer-third-join")`
- [ ] L205 `main(..., args.probe_layer_third_join)`

**measure_audio.py**
- [ ] ~L160 `add_argument("--probe-layer-third-join")`
- [ ] L163 exclusive `sum([... args.probe_layer_third_join ...])`
- [ ] L175–188 builder argv forward
- [ ] ~L223 `measurements["join200_probe"] = ...`
- [ ] L236 200 Hz name set + `join200_probe`
- [ ] L239–240 sections key list + `join200_probe`
- [ ] L244 gap tuple + `join200_probe`
- [ ] L246 slope tuple + `join200_probe` (task-required; differs from 120 Hz `join_probe` omission)
- [ ] L248 mode ternary + `probe-layer-third-join`
- [ ] L265 suffix ternary + `-layer-third-join`

---

*End r20-reviewer advisory. Report path: `.shokunin/audio/reports/round-20/r20-reviewer.md`*
