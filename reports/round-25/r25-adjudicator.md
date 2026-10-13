# Round 25 — Sol independent axis adjudication

**Verdict: ADMIT the narrow depth move.** Admission requires at least one improved owned axis and zero harmed axes. Depth **improved**, coverage **unchanged**, calibration **unchanged**; no scoped harm demonstrated. This admits two isolated metadata-negative fixtures, not a rank change or a new validator.

## Evidence and attribution

I read the Round 25 LOG declaration, all eight wave-1 reports (`r25-{scout,executor,alt,critic,reviewer,simplifier,scribe,guard}.md`), named non-author `r25-verifier.md`, actual invalid/normal/restored receipts, `SHONEN.md`, and fixture-source diff against clean before `30530e17a4f20ba28d7f81cda41c8949f4652697`. The diff adds deterministic four-second 440 Hz amplitude .2 PCM16 generation and two cases to the existing `--probe-invalid` route. `format_failures()` remains the same shared `rate != 48000 or channels != 1` predicate with single `format: expected 48kHz mono` message. No new gate, canonical artifact or numerical threshold changed.

Non-author invalid receipt `.shokunin/audio/corpus/live/runs/20261013T014025494866Z-invalid/measurements.json` has eight records. Native16 positive is 48000 Hz / mono / `pcm_s16le` / 16 bits (`expected_pass`, observed none). Against that tuple, `stereo48_probe` changes **channels only** (48000 Hz, two channels, PCM16), while `mono441_probe` changes **rate only** (44100 Hz, mono, PCM16). Each reports `expected_failure`, observed `format`. Old 44100 Hz **stereo** PCM16 `wrong_format` remains co-confounded; native24 isolates encoded width instead. The prior six retain ordered expected/observed/status tuples compared with historical `20261013T011828577717Z-invalid/measurements.json`: `short_sections` → `section count`; `corrupt` → `decode`; `wrong_format` → `format`; `odd_sections` → `section count`; `native16_probe` → pass; `native24_probe` → `format`.

Invalid mode checks metadata, **not** ordinary acoustic conditions. Independent verifier additionally used direct `measure()` with broad custom `(4.0,100,1000,False)` spec on both actual controls. Each returned only `format: expected 48kHz mono`: duration 4.0 s, peak .199981689 FS, RMS about −16.99 dBFS, centroids 563.262 Hz (stereo48) and 457.772 Hz (mono441) inside that supplied band. Thus no other condition fails *under this spec*. This does not prove arbitrary fixture-band fit or stereo-to-mono acoustic equivalence. As the critic flagged, SoX f32 decoding flattens stereo into 384000 interleaved scalar samples (192000 frames × two channels); FFT/sample-count and centroid semantics are not mono-equivalent. Isolation is of **format metadata**, not downstream audio semantics.

The non-author serial replay of 19 historical modes produced all receipts and expected exit vector `[0,0,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0]`, without runner exit 2. Initial/restored normal receipts `20261013T014011312756Z-normal` and `20261013T014026304512Z-normal` each have thirteen passing canonical measurements and five passing `_alt` distinctions (`ui_alt`, `impact_alt`, `movement_alt`, `ambience_alt`, `stem_layer_alt`), equal after measurement-path identity is excluded. Prior negative failure sets and thresholds in replay receipts remain unchanged. All thirteen canonical WAV SHA-256 digests match pre-round; regenerated new controls preserve hashes `1a71090267d97dc07c14f4a057e2b14a433b45086a424cb99128f55831328987` (stereo48) and `1bd9aac91baecffb03cb667c7e4116806eb149aa1c39b5cc787e1b861c965e69` (mono441). The verifier disclosed nineteen initial shell-wrapper attempts exiting **127**, creating no receipts; those were setup errors **excluded** from the successful 19-mode replay, not audio-control outcomes.

## Separate owned-axis judgments

| Axis | Judgment | Reason |
|---|---|---|
| Depth | **Improved** | Deterministic single-field negatives now establish independent rate-only and channel-only rejection by the existing predicate for these PCM16 examples, unlike the previous combined negative. |
| Coverage | **Unchanged** | Attribution within existing format invalid-probe category improves, but no new asset class, codec family, general WAV acceptance surface or runner mode is covered. Existing 19 modes and 13 canonicals hold. |
| Calibration | **Unchanged** | Predicate, comparator polarity, numerical thresholds and five variant checks persist. Broad-spec direct fit is a scoped confound check, not a new numerical gate or stronger acoustic calibration. |

No owned axis is harmed in scoped evidence. `SHONEN.md` has all four probation boxes checked, but this round does **not** change rank or establish promotion. No codec/perceptual/general WAV/production/rights/engine/publishing claim follows.

## Exact shell commands I ran and exits

- `git diff 30530e17a4f20ba28d7f81cda41c8949f4652697 -- .shokunin/audio/corpus/fixtures/build_artifacts.py .shokunin/audio/corpus/fixtures/measure_audio.py` — exit **0**; only the declared builder and invalid-probe route changed.
- `git status --short; git diff --check; git diff 30530e17a4f20ba28d7f81cda41c8949f4652697 -- .shokunin/audio/corpus/artifacts .shokunin/audio/SHONEN.md` — combined exit **0**; check printed no errors and final artifact/SHONEN diff was empty. Combined exit alone does not independently attest each subcommand.
- `sha256sum .shokunin/audio/corpus/artifacts/*.wav` — exit **0**; thirteen hashes match `r25-guard.md` and `r25-verifier.md`.

I did **not** rerun the 19 audio modes; the named non-author verifier recorded those exact commands/exits and receipts. My additional receipt checks were read-only Python inspection, not shell commands. I wrote only this report; no shared edit, commit, push or child spawn.
