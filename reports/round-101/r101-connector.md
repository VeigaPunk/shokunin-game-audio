# r101 ConnectorR101 — sibling-overlap scan (read-only seat; transcribed verbatim by the L1)

Seat: `W2RoundAudio-8.ConnectorR101-2` (connector, lane-dispatched). Paths are sibling main checkouts under `/home/vgpnk/Projects/shokunin/` (read-only) and kaika-w1 dossiers.

| Surface | Sibling path:line | Class | Ground / boundary |
|---|---|---|---|
| In-engine audio playback | `game-dev-2d-shokunin/corpus/fixtures/audio_playback.gd:5-24` | Adjacent | sibling-owned: headless tree playback advance + 120-frame drain (`r12-headless-audio.md:1-12`) |
| AudioServer bus routing | `game-dev-2d-shokunin/corpus/fixtures/audio_bus_route.gd:7-41` | Adjacent | sibling-owned: engine bus index/route resolution, fallback to Master index 0 |
| Engine mix clock + spatial audio | `game-dev-2d-shokunin/corpus/fixtures/audio_lattice.gd:7-20` | Adjacent | sibling-owned: Dummy driver 128-frame mix quanta, `AudioStreamPlayer2D` attenuation |
| Headless audio dummy driver | `game-dev-3d-shokunin/corpus/fixtures/r100_fpslat.gd:59,360` | Adjacent | sibling-owned: `--audio-driver Dummy` on Godot 4.7.2 |
| Godot WAV import default (QOA) | game-dev-2d, game-dev-3d: 0 matches | Core (audio, K4) | siblings set `compress/mode` only for textures (`export_launch_s05.gd:62`) |
| Adaptive music (Interactive/Synchronized) | game-dev-2d, game-dev-3d: 0 matches | Frontier (audio) | 0 sibling occurrences |
| Loudness / LUFS / dBTP / BS.1770 | game-dev-2d, game-dev-3d: 0 matches | Core (audio) | offline DSP measurement; fleet lead `connect-sources.md:149` |
| Middleware + AI-audio terms | all siblings: 0 matches | Adjacent / Frontier | record-only in audio; choice/clearance belongs to game-dev / operator |
| SOURCES rows S001–S013 | all sibling `corpus/SOURCES.md`: 0 collisions | Core | `game-dev-2d/corpus/SOURCES.md:12` independently opened a CLI tutorial as its S006 |

Contested scope (for the report):
- Engine bus peaks vs offline stem loudness: `game-dev-2d-shokunin/corpus/fixtures/r88_surfaces.gd:423` queries `AudioServer.get_bus_peak_volume_left_db`. Boundary: audio owns offline loudness/true-peak measurement; game lanes own engine-side routing and runtime peak monitoring.
- WAV stem hand-off vs Godot ≥4.4 QOA import: `fleet-ledger/.ufo/waves/kaika-w1/connect-sources.md:88` has audio handing deterministic WAV stems to game fixtures; K4 shows the default import is lossy QOA (`compress/mode=2`). Game lanes set `compress/mode=0` if uncompressed bytes are required — reported, not absorbed.

Reuse leads (mirror, never copy): `game-dev-2d-shokunin/corpus/QUALITY.md` Q4 `:16` (header-triplet census), Q5 `:17` (runnable recheck), Q21 `:33` (tier floor: each `source:` cites ≥1 A/B row for its scope); `game-dev-2d-shokunin/corpus/SOURCES.md:46-52` structured search log, `:21,37` rejection format.
