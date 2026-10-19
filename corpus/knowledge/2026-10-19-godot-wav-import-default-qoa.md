source: S010 — https://docs.godotengine.org/en/4.4/classes/class_resourceimporterwav.html — Properties table `int compress/mode = 2` + Description "By default, Godot imports WAV files using the lossy Quite OK Audio compression"; S009 — https://docs.godotengine.org/en/4.3/classes/class_resourceimporterwav.html — Properties table `int compress/mode = 0`; S008 — https://docs.godotengine.org/en/stable/classes/class_resourceimporterwav.html (stable = 4.7 per page header, 2026-10-19) — `int compress/mode = 2`; S013 — host `godot --headless --path <scratch> --import` (Godot 4.7.2.stable.arch_linux.ed1daf0bf) — generated `ui.wav.import` / `stem.wav.import` `compress/mode=2`; S011 (rejected for this scope) — https://docs.godotengine.org/en/4.4/tutorials/assets_pipeline/importing_audio_samples.html — "Disabled (default)"
verified-at: 2026-10-19 (Godot docs 4.3 / 4.4 / stable-4.7 pages fetched; host Godot 4.7.2; lane fixtures at base defbe128)
recheck: for v in 4.3 4.4 stable; do printf '%s ' $v; curl -sL https://docs.godotengine.org/en/$v/classes/class_resourceimporterwav.html | sed 's/<[^>]*>//g' | grep -oE 'int compress/mode = [0-9]' | head -1; done; P=$(mktemp -d); printf 'config_version=5\n' > $P/project.godot; cp corpus/artifacts/ui.wav corpus/artifacts/stem.wav $P/; godot --headless --path $P --import >/dev/null 2>&1; grep -h '^compress/mode=' $P/*.wav.import; stat -c '%n %s' $P/.godot/imported/*.sample $P/*.wav

# Godot ≥ 4.4 imports WAV as lossy QOA by default — lane PCM16 measurements do not describe default-imported bytes

**Claim.** The default of Godot's WAV importer `compress/mode` changed from `0` (uncompressed) in the 4.3 class reference to `2` (Quite OK Audio, lossy) in the 4.4 and stable (4.7) class references, and the host's Godot 4.7.2 applies `compress/mode=2` when it imports the lane's own fixtures with no settings changed. The same-version 4.4 tutorial still says "Disabled (default)", so for import defaults the generated class reference — and a headless import — outrank the tutorial. Consequence for this lane: every seam, peak, centroid and loudness figure the harness records is measured on PCM16 masters (`format: expected PCM16`, `corpus/fixtures/measure_audio.py:58-60`), not on the bytes a default Godot ≥ 4.4 project ships.

## Observed (2026-10-19)

| Surface | `compress/mode` default | Command |
|---|---|---|
| 4.3 class reference (S009) | `0` | `recheck:` loop, line 1 |
| 4.4 class reference (S010) | `2`, plus the Description sentence "By default, Godot imports WAV files using the lossy Quite OK Audio compression" (1 match) | same; `curl -sL …/4.4/classes/class_resourceimporterwav.html \| grep -c 'By default, Godot imports WAV files using the lossy Quite OK Audio compression'` → 1 |
| stable (4.7) class reference (S008) | `2` (sentence: 1 match; 4.3: 0 matches) | same |
| 4.4 tutorial (S011) | "Three compression modes can be chosen from for WAV files: Disabled (default), RAM (Ima-ADPCM), or QOA (Quite OK Audio)." | `curl -sL https://docs.godotengine.org/en/4.4/tutorials/assets_pipeline/importing_audio_samples.html` + tag strip |
| host Godot 4.7.2 headless import of `ui.wav`, `stem.wav` (S013) | `compress/mode=2`; `edit/trim=false`, `edit/normalize=false`, `edit/loop_mode=0` | `recheck:` line 2 (rc 0) |

- The other importer defaults are identical across 4.3, 4.4 and stable: `edit/normalize = false`, `edit/trim = false`, `edit/loop_mode = 0`, `edit/loop_begin = 0`, `edit/loop_end = -1`, `force/8_bit = false`, `force/mono = false`, `force/max_rate = false`, `force/max_rate_hz = 44100` — tag-stripped property table of each page, 2026-10-19. Only `compress/mode` moved.
- Imported `.sample` resource vs source WAV: `stem` 39,247 B vs 192,044 B; `ui` 2,743 B vs 11,564 B — `stat -c %s`, 2026-10-19 (the `.sample` is Godot's resource container, so this is a size observation, not a codec bitrate).
- Host ffmpeg n9.0.1 has a QOA **decoder** and no QOA **encoder** — `ffmpeg -hide_banner -decoders | grep -i ' qoa'` → `A....D qoa QOA (Quite OK Audio)`; `ffmpeg -hide_banner -encoders | grep -ci ' qoa'` → 0, 2026-10-19.
- Independent re-run: the round-101 scout seat recorded the same `compress/mode=2` and `.sample` sizes (`reports/round-101/r101-scout-godot.md`).

## Inference

- [INFERENCE] Seam-continuity, sample-peak and true-peak margins measured on the PCM16 masters may shift after QOA coding; the lane's loop-seam gates (`.03` FS jump, `.001` FS/sample slope) were calibrated on PCM16 only.
- [INFERENCE] A game lane that needs bit-exact or uncompressed playback must set `compress/mode=0` in the asset's `.import` file — that is an engine-integration decision (Adjacent: game-dev-2d / game-dev-3d), not this lane's to make (`PROVINCE.md` refuses engine integration changes).

## Unknown

- The size of the QOA-induced delta on the lane's seam/peak/centroid/loudness measurements: unmeasured. Measuring it needs decodable QOA bytes — Godot's `.sample` container would have to be unwrapped, or a reference `qoaconv` encoder installed (lead: phoboslab/qoa, unopened).
- Whether Godot's documentation for 4.5 / 4.6 matches (not opened by this entry; the ART dossier's O11 lead says 4.5 also shows `2`).

coverage: corpus/README.md coverage map — Core, gap entered round 101: ship formats + engine import defaults
