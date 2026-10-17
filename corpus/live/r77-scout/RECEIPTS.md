# r77-scout receipts

Seat: **scout** (leaf). Repo `~/Projects/shokunin/audio-shokunin` @ HEAD
`d566a317e6b849032c444155e933b33a102bbada`. Host `plazir27`, measured
2026-10-14 ~16:20–16:45 UTC.

**Write scope:** every file below is under `corpus/live/r77-scout/` (untracked).
**Zero tracked-file edits by this seat.** The ` M corpus/fixtures/measure_audio.py`
visible at HEAD is a *concurrent* seat's live edit (mtime 16:26:38, the r76
critic's fix set) — see `reports/round-77/r77-scout.md` §7. This harness never
imports `corpus/fixtures`.

## Harness

| file | sha256 |
| --- | --- |
| `r77_probe.py` | `7fa77e1806f20b001ffb89b49184e9b736b39e2230b509689a65df466a6b4fdc` |
| `toolchain.txt` | `b5ba2bc171eba24b07d0e027a44e7cf52f61819eb9e7d990a5ee9ecc099d8596` |

Self-contained: own `inspect()`, `out_kind()`, `errclass()`, `readers()`.
Own classifiers — no fixture import.

## Receipts (canonical)

| probe | file | sha256 |
| --- | --- | --- |
| FRONTIER 1 final lattice | `probe-capture-sink-lattice-r77.json` | `f6d1294748ae383adfd81ff08f1bcb5981d8afba7a75d457b8a7886300a99b87` |
| FRONTIER 4 v2 (5 witnesses) | `probe-sever-readers2-r77.json` | `49ee33b28ed7a110ff4ff09b3530b47aa665b6e3950d29db32a65323dc7220f0` |
| FRONTIER 3 (format axis) | `probe-format-axis-r77.json` | `6e5f49cf8c82340ae0571262ba9a5dc247d2aac821df3b4cbd23e48cf76cbe00` |
| FRONTIER 1 enumeration (60 cells) | `probe-source-lattice-r77.json` | `b01e2e64915273a28a0c6849d215d8721b57408404342423c5a002952ecd1a6f` |
| FRONTIER 2/7 (hot-plug, provider kill) | `probe-hotplug-r77.json` | `4e5ed0f16bf9db5446b375ddacbdb1485a40fb4d23ea6b4f35df7ef699151044` |
| arecord device-dependent sever | `probe-arecord-device-sever-r77.json` | `f18c36ef4d2b2757195ee75a82de09ac736ac4938ced7d0ad5cf9adccc8eb7a2` |
| 2 GiB split sentinel / flood boundary | `probe-flood-boundary-r77.json` | `d7f02123f5a66cebfe463f3fa01e2ae1d84510cdbd8821970b2276f285c05c40` |
| FRONTIER 1e serialized content witness | `probe-override-content-serial-r77.json` | `5240c0fdab25421dc2d028226c38f086693f88d8666d9127973b977bf1fc044a` |
| FRONTIER 1c link topology | `probe-override-extent2-r77.json` | `a6e6e48971445741c3b813dc9ba2c961afaeb21be246f30b4600da92ef412063` |

## Superseded / confounded (kept for the record)

| file | sha256 | why superseded |
| --- | --- | --- |
| `probe-target-override-r77.json` | `0d9406c6939263c85238defd54e3f27f2a0ed37fa12744f13d255745d9cb07a9` | byte-identity read as override; falsified by `probe-override-content-serial` |
| `probe-override-extent-r77.json` | `3dd7b59a19e6aec86293994dae558ccdbf1cd8a67a7cd5e145cc77264f2260d4` | broken `pw-link` block parser (`|<-` producer lines); fixed in `extent2` |
| `probe-override-content-r77.json` | `07ba15f15f6cf07da7f92ef4d9dd807875890822bb5c1cdc7ad068db59437b6d` | ran concurrently with `probe-raw-concurrent`; tone leaked across sinks |
| `probe-raw-concurrent-r77.json` | `3c98f95ee0bdc0ed19cb0ab9b5d8adc8659bfb9b0d2cd058c5f63640f249ba0b` | same confound; `BASELINE_no_playback` measured `nz=0.8777` with no playback |
| `probe-sever-readers-r77.json` | `71a7f104d7040f91c0832b16af8caf08d1f023146ceb649cd642d076253241e4` | v1: `ffprobe nb_frames` is a **packet** count (24 for 96000 frames); v2 uses `format.duration` |
| `probe-a3_override_extent.py` | — | superseded by `probe_a3b_override_extent.py` |

## Probe scripts

`probe_a_lattice.py` · `probe_a2_target_override.py` ·
`probe_a3_override_extent.py` · `probe_a3b_override_extent.py` ·
`probe_a4_override_content.py` · `probe_a5_override_content_serial.py` ·
`probe_b_format.py` · `probe_c_sever_readers.py` ·
`probe_c2_sever_readers.py` · `probe_d_hotplug.py` ·
`probe_e_raw_concurrent.py` · `probe_g_flood_boundary.py` ·
`probe_h_lattice_final.py`

## Byte discipline

- Per-leg cap: **262144 B** (`CAP_BYTES`), enforced by the reader for stdout
  consumers and by an inner duration/`-n` flag for file consumers; every leg
  also carries an outer `subprocess` timeout.
- **A violation occurred and is reported.** `probe_c2_sever_readers.py` ran the
  unbounded `arecord -D null` legs, which auto-rotate at the 2 GiB wav limit
  and wrote **36 GB** into `corpus/live/r77-scout/scratch/`; a follow-up
  device test filled the 16 GB `/tmp` tmpfs (`Disk quota exceeded`), which
  invalidated one arecord comparison until it was re-run on a non-full disk
  (`probe-arecord-device-sever-r77.json` is the clean re-run).
- All flood artifacts deleted (`find … -size +50M -delete`, `rm /tmp/r77_arec*`).
  Final seat footprint: **36 MB**. `df` verified back to baseline
  (`/home` 10 %, `/tmp` 46 %).

## Confounds

- A concurrent `r76-verifier` seat ran `measure_audio.py --probe-capture-r76`
  on this host for most of the window (pid 2925184 at 16:20, still in flight
  at 16:31) and was editing `corpus/fixtures/measure_audio.py` (mtime 16:26:38).
- This host's default source (Line) and Mic are **digital silence**
  (`nonzero_frac = 0.0`, `peak = 0`), so byte identity between two source
  captures is not evidence; the tone anchor in `probe_h_lattice_final.py` is
  what makes the lattice decidable.
- All numbers are this-host pins: PipeWire 1.6.8, pacat 17.0-98-gb096,
  alsa-utils 1.2.16, ffmpeg n9.0.1, SoX_ng 14.8.0.1, Python 3.14.7.
