# r101 ScoutGodot — host Godot WAV import defaults (read-only seat; transcribed by the L1)

Seat: `W2RoundAudio-8.ScoutGodot-2` (scout, lane-dispatched — still the lane). Transcript: `history://W2RoundAudio-8.ScoutGodot-2` (session-scoped; the commands below are the reproducible evidence). Scratch: `/tmp/r101-scoutgodot/` (not evidence; re-run to reproduce).

Commands (scratch project with `project.godot` `config_version=5`, copies of `corpus/artifacts/ui.wav` and `corpus/artifacts/stem.wav`):

- `godot --version` → `4.7.2.stable.arch_linux.ed1daf0bf`
- `godot --headless --path /tmp/r101-scoutgodot/proj --import` → completed; banner `Godot Engine v4.7.2.stable.arch_linux.ed1daf0bf (2026-08-17 01:18:38 UTC)`
- both generated `*.wav.import` files: `edit/trim=false`, `edit/normalize=false`, `edit/loop_mode=0`, `edit/loop_begin=0`, `edit/loop_end=-1`, `compress/mode=2`, `force/8_bit=false`, `force/mono=false`, `force/max_rate=false`, `force/max_rate_hz=44100`
- `stat -c %s` imported `.sample` vs source WAV: `stem` 39,247 B vs 192,044 B; `ui` 2,743 B vs 11,564 B

Observed: the host Godot 4.7.2 default import of a lane fixture is `compress/mode=2` (QOA), consistent with the class reference. No import setting was changed; nothing was written in the lane worktree.
