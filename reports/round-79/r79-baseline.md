# R79 baseline — pre-r79 freeze + r78-probe regression anchor at `a2616f7`

host: devin (`Linux plazir27 7.2.3-arch1-3`). Seat: baseline.
Scope per dispatch: record HEAD, run `--probe-capture-r78` once on the clean
tree as the prior-row regression anchor, record env. No tracked edits.

## 1. Frozen state

- **HEAD: `a2616f732253ed90110ba16a223ec7d10224740c`** ("r78 LOG: adjudicator
  ADMIT-corr"), branch `main`, committed 2026-10-15 03:00:23 -0300.
- HEAD was captured at **06:01:35Z** (`pre-state.txt`) and **never moved**
  through the probe window — a 15 s watcher (`head-watch.log`, 18 samples,
  06:01:44 → 06:05:59Z) shows `a2616f7` at every tick and no status change on
  `corpus/fixtures/measure_audio.py` or `corpus/fixtures/__pycache__`.
- **Pre-existing tracked dirt (not mine):** ` M SHONEN.md` — a rewritten
  promotion checklist already present before this seat's first command.
  Unrelated to the probe surface (fixture code never reads it).
- **`measure_audio.py` is clean:** worktree hash `39286c725c25b034fcb0dcfc0f23bd5c3910a2ee`
  == HEAD blob (verified pre-run and re-verified post-run at 06:06:01Z). The
  probe executed byte-identical code to the committed `a2616f7` fixture.
- No r79 author tracked edits landed inside the probe window; no `/tmp`
  worktree freeze was needed. `corpus/live/r79-scout/` and
  `reports/round-79/r79-scout.md` exist (sibling seat, concurrent).

## 2. Environment (`env.txt`)

- PipeWire **1.6.8** (compiled+linked), pactl **17.0-98-gb096** (libpulse
  17.0.0), PulseAudio-on-PipeWire server **15.0.0**; Python **3.14.7**;
  arecord/aplay **1.2.16**; ffmpeg **n9.0.1**; sox **14.8.0.1**; kernel
  **7.2.3-arch1-3**.
- Defaults at capture: sink `alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink`,
  source `alsa_input.usb-Generic_USB_Audio-00.HiFi__Line__source` (the r78-round
  DualSense default-source episode is over — the USB line source is default
  again). All HiFi sinks/sources were **SUSPENDED** at capture.
- **Concurrent-seat topology (declared contention class):** five foreign null
  sinks were loaded at 06:01:35Z — `r82ff_ns`, `r83dsp_p4_ns`,
  `r83dsp_v_ns48`, `r83dsp_v_ns44`, `r84alsa_ns`. By 06:06Z all but
  `r84alsa_ns` had unloaded: other seats were actively creating/destroying
  null sinks (and therefore plausibly writing `default.audio.sink` metadata)
  **inside** my probe window. The ~10 h stale `aplay -D null` (pid 2202613,
  another seat's leak, already named by the r78 baseline) persists.

## 3. Anchor run — `--probe-capture-r78`

- Command: `python3 corpus/fixtures/measure_audio.py --probe-capture-r78`,
  once, repo root, **06:01:46 → 06:05:13Z** (3 m 27 s). Exit **1**.
- Canonical receipt: `corpus/live/runs/20261015T060513912020Z-capture-r78/measurements.json`
  — 489,120 B, sha256 `9910b4653869d3cba049696712b3c2d74b82938cf26703aef30ad150d4931dd7`;
  byte-equal copy at `corpus/live/r79-baseline/anchor-receipt-…json`.
  Probe stderr: empty (`probe-capture-r78.stderr.log`, 0 B). stdout summary:
  `probe-capture-r78.stdout.json`. Tempdirs were the script's own
  `tempfile.TemporaryDirectory` scratch — no `.wav` persisted.
- Result: 17/17 fixture probes clean; **6/8 r78 arms clean**
  (`playback_target_loss`, `playback_props`, `playback_class_segv`,
  `playback_aplay_axis`, `capture_unlinked_zeros`, `capture_parec_fix`);
  **2 arms failed**:

  ```
  playback_target_lattice_r78_probe:
    lattice absent_sink: the monitor tap on
    alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink carried no
    tag-tone windows — consumption without content is not a playout verdict
  playback_default_follow_r78_probe:
    follow moved: last live consumers
    ['alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink'] — the stream
    never settled on the live default at ITS spawn (r78_def_sink_3341762)
  ```

## 4. Anchor reading — red on the two highest-flap arms, not a code delta

- Prior sibling record (`prior-runs-summary.txt`): **2 GREEN of 13** r78
  receipts (22:19:45Z and **05:57:01Z — eight minutes before mine**, on the
  same committed bytes). Failure incidence across the 13: `default_follow`
  6/13, `target_lattice` 4/13, `props` 3/13, `parec_fix` 3/13, and one each of
  `class_segv`, `target_loss`, `aplay_axis`, `unlinked_zeros`. My two failing
  arms are the family's two most frequent, and both are session-default-sink
  legs — exactly the surface a concurrent seat's null-sink/metadata churn
  perturbs (§2).
- Mechanism match: `follow moved` expects a stream spawned after the leg's
  metadata write to land `r78_def_sink_3341762`; it landed the SPDIF default —
  the observed signature of `default.audio.sink` being re-pointed between
  write and spawn. `absent_sink` got links but no tag tone on the (suspended)
  SPDIF monitor — the same "tap heard nothing" class r78's own 22:05Z run
  recorded as `no LATE tag-tone span`.
- **Verdict for the anchor: environmental/contention red, code-stable.** Same
  bytes were GREEN 8 min earlier; HEAD did not move; nothing in the diff
  surface changed. The regression bar for post-landing is therefore: the r78
  family must not accrue **new or renamed** failure classes, new keys, or
  changed thresholds vs this receipt — not that every re-run be green (this
  family flaps under multi-seat load; 11/13 receipts already carry some
  red arm).

## 5. Write-scope accounting

Wrote only: this report; `corpus/live/r79-baseline/` =
`pre-state.txt`, `env.txt`, `runs-before.txt`, `head-watch.log`,
`probe-capture-r78.stdout.json`, `probe-capture-r78.stderr.log` (0 B),
`anchor-receipt-20261015T060513912020Z-capture-r78.json` (478 KiB),
`post-state.txt`, `prior-runs-summary.txt`; plus the canonical
`corpus/live/runs/20261015T060513912020Z-capture-r78/measurements.json`
written by the probe itself. All JSON/log — no `.wav`, no tar, nothing
>1 MB except the two byte-equal receipts. **Zero tracked edits by this seat.**

## 6. Remaining unknowns

- Whether the pre-existing `SHONEN.md` edit belongs to the r79 author or
  another seat (its blob was not hashed pre-run; noted as pre-existing).
- Which specific concurrent seat owned the `r82ff/r83dsp/r84alsa` null sinks —
  attribution by name prefix only.
- If the judge wants a *green* anchor specifically, a re-run in a `/tmp`
  worktree at `a2616f7` during a quieter window is the prepared move; this
  seat ran the probe exactly once per dispatch.
