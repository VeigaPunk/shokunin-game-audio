# Round 39 scribe — orientation decision table and fit/setup record

## Scope and evidence status

The LOG declaration is a *looping ambience* denominator-orientation test using the same two equal-duration scratch WAVs in forward and reverse roles. At report time, the executor scratch directory contains `baseline.wav`, `variant.wav`, a measurement helper, and additional `test-*.wav` / `sweep-*.wav` candidates. Presence of files is not a measurement receipt. No successful project-helper measurement or forward/reverse runner receipt was available to this scribe; therefore no centroid, ratio, strict split, pass/fail, duration, or ordinary-check result is asserted below. Wave-2 author integration/replay is later evidence and remains pending; it must not be backfilled into this wave-1 report.

## Before/after orientation decision table

Existing rule under test: `abs(variant_centroid - baseline_centroid) / baseline_centroid > 0.10` (duration arm is expected to be exactly zero for the intended equal-duration pair). The required LOG condition is `A < B`, `abs(B-A)/A > 0.10`, and `abs(B-A)/B < 0.10`, measured from the project helper. Cells marked pending are intentionally untested here.

| State / mode | Baseline → variant | Baseline-relative centroid ratio | Strict `.10` outcome | Duration delta / ordinary checks |
|---|---|---|---|---|
| Before / forward | A (lower centroid) → B (higher centroid); actual measured values **pending** | `abs(B-A)/A`; actual float **pending**; must be `> .10` | **Pending / untested**; declared expectation is pass only if measured ratio is strictly above `.10` and all other checks pass | **Pending / untested**; target `0.0`, ordinary/seam failures must be empty |
| After / reverse | B (higher centroid) → A (lower centroid), same two WAVs; actual measured values **pending** | `abs(B-A)/B`; actual float **pending**; must be `< .10` | **Pending / untested**; declared expectation is sole distinctness failure only if measured ratio is strictly below `.10` | **Pending / untested**; target `0.0`, ordinary/seam checks must pass |

Thus the round-39 strict split is **not yet measured or demonstrated** in this report. No inference is drawn from planned values or prior rounds. In particular, the round-30 UI scratch orientation example and round-37/38 ambience above/below controls do not supply the required same-pair ambience forward/reverse evidence.

## Setup failures versus numerical fit outcomes

I ran this exact shell command:

```sh
python3 .shokunin/audio/corpus/live/round-39/executor/measure_pair.py
```

It exited **1** during setup/import, before any pair measurements. The traceback ended with `FileNotFoundError` for `/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/fixtures/measure_audio.py`; the helper resolved its fixture path incorrectly. This is a **setup/path failure**, not a numerical failed fit and not a runner outcome. No successful correction or measurement was performed by this scribe.

**Numerical fit record:** no fit result available to classify as successful or failed; the listed test/sweep files have no reported helper floats here. Treat numeric fitting as pending, not as a failed fit. **Setup record:** one helper-path setup failure above. Keep those categories separate in subsequent reports.

## Limits

This is a numerical baseline-denominator orientation probe only. It makes no audition, perceptual/spectral similarity, seamlessness, quality, production, rights, engine, publish, or promotion claim. No threshold or other constant is changed.
