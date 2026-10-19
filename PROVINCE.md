# audio province

Owns: game audio production — SFX (UI, impacts, movement, ambience) and
soundtrack (motifs, loops, stems, adaptive layers) — verified by headless
analysis: duration, loudness, spectral content, loop-seam continuity.

Sources (read-only):
- host audio toolchain (ffmpeg, ffprobe, sox — probed present 2026-10-12)
- ~/Projects/gamez/research/AIAudio.md (demand context)
- real-world sample/reference works only through a cited reference ledger
  (attribution / rights / training permission kept distinct)

Refuses: perceptual-quality claims without a measurable proxy; publishing or
store submission; sample rights clearance; engine source mutation; game
mechanics (game-dev-2d); narrative canon (lore).

Only writes `.shokunin/audio/**` and its own reports.

## Task boundary checklist — round 24, 2026-10-13

Classify the **requested action and effect**, not its filename or the requester's assertion. This lane may write only `.shokunin/audio/**` and its own final `.shokunin/reports/round-N/audio.md`; its leaf workers write only assigned audio-scoped reports/scratch. The orchestration-owned mint commit `0f60e7658a63030ed054fb83ec7b830bea7be08b` also wrote `.shokunin/MANIFEST.json` and `.shokunin/mints/audio.md`; this is historical setup, **not** a standing permission for audio to edit fleet bookkeeping. Round 1's named verifier report `.shokunin/reports/audio-r1-verifier.md` is a documented historical report exception, not a general output path. No write to engine/game/lore source, other lanes, or external systems is implied by an audio file's extension.

| Decision | Task test | Action |
|---|---|---|
| Audio-province | The deliverable is original SFX, ambience, soundtrack motif/loop/stem/layer **audio content** or its headless fixture/measurement/documentation, entirely within the write scope above. | Do the audio-only work, record provenance and measured duration/level/spectral/loop/format proxies with named receipts. The current deterministic 13 WAVs are analytic fixtures, not deployed content or listening validation. |
| Refuse the consequential part | Publishing/store submission; actual sample-rights/training/distribution clearance; changing engine integration, layer triggers/mixer, import/build runtime; game mechanics or narrative canon; representing fixture metrics as proof of perceived quality. | Do not perform or certify that action. Audio may report its measured data, but routes external decisions to the responsible owner/operator. The operator's rights or canon assertion alone does not confer authority on this lane. |
| Uncertain or mixed | Audio asset request entails a runtime trigger, an unapproved lore cue, an uncleared reference sample, a destination outside scope, or a subjective “better” judgment with no tested relevant proxy. | Split only if a genuinely independent audio-only deliverable exists; otherwise pause the out-of-province part and route the specific ownership question to the operator. A proxy measures its named property, not the user's subjective goal. Never silently absorb another province. |

Examples to classify without oral context: (1) synthesize an original UI click and log FFT centroid → **audio-province**; (2) create an isolated 200 Hz stem layer WAV and check seam/gap → **audio-province**, but wiring adaptive layer selection in engine → **refuse**; (3) “make the impact more cinematic” → **uncertain** until the measurable requested change is stated, and no claim of cinematic quality; (4) inspect sample rate of an external recording → **audio-only analysis** if no rights inference is requested, while clearing the sample for a store release → **refuse**; (5) generate a soundtrack matching a new character backstory → audio can build a signal from a *separately approved* brief, but setting narrative canon → **refuse/route to lore owner**; (6) export an audio-only asset into an engine directory → **refuse** because destination and integration are outside the write boundary. A mixed task does not become audio-owned merely because its WAV is in this tree.

Evidence boundary for this checklist: `.shokunin/audio/reports/round-24/r24-history.md` inspected 47 first-parent commits from after mint `0f60e76` through pre-round `2a19811` and found post-mint changed paths only under audio/reports trees; mint's two fleet bookkeeping paths and round-1 verifier report are named above. A separate non-author verifier must independently check the tracked range and held-out classifications before any SHONEN box-4 decision. Neither Git path names nor fixture metrics prove absence of untracked/external behavior, universal domain compliance, perceived quality, rights clearance, or production readiness.

## Correction — round 101 (2026-10-19)

The declared write scope `.shokunin/audio/**` is the pre-extraction path: `reports/round-8/r8-verifier.md:3` records the exit-127 failure, and `ls -d .shokunin` fails in this checkout. Real write surfaces are repository-root `corpus/**`, `reports/**`, `ports/**`, and the ledgers.

## Core / Frontier / Adjacent — round 101

### Core — held

SFX/stem synthesis and headless measurement battery (fixture-battery, audio-checklist, threshold-calibration, seed); loop seams and section joins; decoder/transport behaviour (SoX_ng, ffmpeg, libsndfile — the 10 sox/ffmpeg knowledge entries: `ls corpus/knowledge | grep -E '^2026-10-1[34]-' | grep -cE 'sox|ffmpeg'` → 10, 2026-10-19).

### Core — gap entered this round

Per-asset normalization tooling (K1); loudness-measurement conventions — mono/dual-mono and true peak (K3); ship formats and engine import defaults (K4); platform loudness targets (K5).

### Frontier

Realtime transport / PipeWire-Pulse-JACK-GStreamer consumer lattices (rounds 71–100: held only in LOG.md, reports/, and corpus/live receipts; port `ports/frontier/fb-pipewire.md`); engine-native adaptive music (Godot AudioStreamInteractive/Synchronized); AI-audio terms ledger (record-only); ship-codec round-trip deltas (Ogg/Opus/QOA, unmeasured).

### Adjacent

Engine integration/triggers, bus routing, runtime peak monitoring, and game mechanics (game-dev-2d / game-dev-3d); narrative canon (lore); sample-rights clearance and publishing (operator); research method (chousa); middleware licensing/integration (FMOD/Wwise — record only).
