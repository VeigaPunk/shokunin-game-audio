# audio corpus — index

## Index

The first 14 knowledge rows are the pre-round files in base `defbe128`; the four 2026-10-19 rows were indexed by the L1 after admission at the round-101 gate (`corpus/lessons/round-101.md` `## Gate`); the existing frontier note is listed last. Sources for the 2026-10-19 rows: `corpus/SOURCES.md`.

| path | what it holds |
|---|---|
| `corpus/knowledge/seed.md` | Host tool inventory and the lane's measurement-not-listening verification discipline. |
| `corpus/knowledge/2026-10-12-audio-checklist.md` | Initial falsifiable probes for SFX, ambience, loops, stems, adaptive transitions, and formats. |
| `corpus/knowledge/2026-10-12-fixture-battery.md` | Seeded fixture construction, headless checks, receipts, and the normal/failing run protocol. |
| `corpus/knowledge/2026-10-12-threshold-calibration.md` | Fixture-local thresholds, observations, controls, and explicit limits on what they establish. |
| `corpus/knowledge/2026-10-13-sox-ffmpeg-packet-residue.md` | Measured decode-length loss from FFmpeg packet residue through the SoX bridge on malformed extensible WAVs. |
| `corpus/knowledge/2026-10-13-sox-act-autodetect-predicate.md` | Byte-exact SoX `act` autodetection predicate and its build/fixture preconditions. |
| `corpus/knowledge/2026-10-13-sox-validbits-codec-map.md` | `wValidBitsPerSample`-to-codec reclassification under the `act`/FFmpeg bridge. |
| `corpus/knowledge/2026-10-14-sox-autodetect-preemptor-ordering.md` | Measured RIFF preemptor order `gsrt ≺ hcom ≺ act ≺ wav`. |
| `corpus/knowledge/2026-10-14-sox-preemptor-map-complete.md` | Completed SoX preemptor map for RIFF+0x84@256, including decodable controls and length gates. |
| `corpus/knowledge/2026-10-14-sox-transport-axis.md` | Four-arm transport matrix and the member-local detection/decode forks. |
| `corpus/knowledge/2026-10-14-sox-posttable-fallback.md` | Post-table fallback selected by name/extension, plus the genuine seekability-gated `txw` refusal. |
| `corpus/knowledge/2026-10-14-sox-extension-suffix.md` | Identical no-match bytes dispatched by suffix, including the `.snd` detection fork. |
| `corpus/knowledge/2026-10-14-sox-fifo-hold-bound.md` | FIFO writer-hold transition zone and the chunked-feed control; no scalar hold bound. |
| `corpus/knowledge/2026-10-14-ffmpeg-cross-decoder-transport.md` | Round 71 FFmpeg/ffprobe transport results contrasted with SoX's named-axis partition. |
| `corpus/knowledge/2026-10-19-loudnorm-short-sfx-regimes.md` | ffmpeg n9.0.1 loudnorm's three paths on short SFX (peak-normalize below the −70 LUFS gate, linear < 3 s, dynamic ≥ 3 s); `loudnorm` itself runs at 192 kHz for every path, while this recheck's final stream is 48 kHz after downstream resampling. Core gap row: per-asset normalization tooling. |
| `corpus/knowledge/2026-10-19-ebur128-dualmono-and-true-peak-on-fixtures.md` | 17-fixture table of sample vs true peak and mono vs dual-mono LUFS (+3.010/+3.011 LU); the sample-peak gate does not bound true peak. Core gap row: loudness-measurement conventions. |
| `corpus/knowledge/2026-10-19-godot-wav-import-default-qoa.md` | Godot WAV import default moved to lossy QOA in 4.4 (class refs + host 4.7.2 headless import); tutorial rejected. Core gap row: ship formats + engine import defaults. |
| `corpus/knowledge/2026-10-19-game-loudness-whole-mix-protocol.md` | ASWG / PlayStation / EBU targets are whole-mix, ≥ 30-min captures; basis for no per-fixture LUFS window. Core gap row: platform loudness targets. |
| `ports/frontier/fb-pipewire.md` | Pre-measurement notes on realtime `pw-cat`/`pw-play` and mpv playback consumers. |

## Coverage map

### Core held

- SFX/stem synthesis and the headless measurement battery: seeded fixtures, numeric checks, and receipt-backed reruns (`fixture-battery`, `audio-checklist`, `threshold-calibration`, `seed`).
- Loop seams and section joins are measured with sample-level boundaries and per-section checks, not subjective audition.
- Decoder/transport behavior spans SoX_ng, FFmpeg, and libsndfile; the 10 SoX/FFmpeg knowledge entries are counted at base by `ls corpus/knowledge | grep -cE 'sox|ffmpeg'` → `10`.

### Core gap

- K1 — per-asset normalization regimes for short SFX.
- K3 — loudness-measurement conventions for mono/dual-mono and true peak on fixtures.
- K4 — ship formats and Godot WAV-import defaults, including QOA.
- K5 — platform loudness targets and a whole-mix protocol.

These four rows were uncovered at base (0 entries — `git -C . ls-tree --name-only defbe128 corpus/knowledge/ | grep -ciE 'loudnorm|dualmono|true.?peak|qoa|godot|whole-mix'` → 0, 2026-10-19) and were each entered by one admitted round-101 entry, indexed above.

### Frontier

- Realtime transport and PipeWire/Pulse/JACK/GStreamer consumer lattices across rounds 71–100 (held chiefly in `LOG.md`, reports, and `corpus/live/`; see the existing `ports/frontier/fb-pipewire.md`).
- Engine-native adaptive music with Godot `AudioStreamInteractive` and `AudioStreamSynchronized`.
- AI-audio terms ledger, record-only.
- Ship-codec round-trip deltas for Ogg/Opus/QOA, not yet measured.

### Adjacent

- Engine integration/triggers, bus routing, runtime peak monitoring, and mechanics: game-dev-2d/3d.
- Narrative canon: lore.
- Rights clearance and publishing: operator.
- Research method: chousa.
- FMOD/Wwise middleware licensing: record-only.

## Known gaps

The proposed “rounds 71–100 produced zero knowledge entries” claim does not reproduce: the sweep finds an existing round-71 page. It narrows the knowledge-entry gap to rounds 72–100.

Sweep command:

```sh
grep -RniE 'round[- ]?(7[1-9]|8[0-9]|9[0-9]|100)|\br(7[1-9]|8[0-9]|9[0-9]|100)\b' corpus/knowledge/
```

Output:

```text
corpus/knowledge/2026-10-14-ffmpeg-cross-decoder-transport.md:1:# r71 — second decoder (ffmpeg/ffprobe) on the transport matrix
```

The one hit is round 71; the same sweep has no round-72–100 hit.

## Frontier

- Realtime playback/consumer behavior remains host- and server-sensitive; the lane's round 71 cross-decoder note is already in `corpus/knowledge/`, while the PipeWire consumer surface is summarized in `ports/frontier/fb-pipewire.md`. Round 72–100 discoveries remain scattered through the ledger, reports, and live receipts rather than individual knowledge pages.
- Godot's native interactive and synchronized streams are documented leads, not yet exercised as adaptive-music behavior by this corpus.
- Ogg/Opus/QOA ship-codec round-trip deltas and engine import effects remain unmeasured.
- AI-audio terms remain a record-only ledger; no rights clearance is asserted.
