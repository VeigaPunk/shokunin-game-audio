# audio seed knowledge

## Host toolchain census (probed 2026-10-12, commands + outputs on record)
- ffmpeg  /usr/bin/ffmpeg    — synthesis, mixing, format conversion
- ffprobe /usr/bin/ffprobe   — duration/loudness/stream analysis (JSON output)
- sox     /usr/bin/sox       — scriptable synthesis (sine/noise/brown noise,
                               envelopes), precise trimming, concatenation
- aplay   /usr/bin/aplay     — playback (headless verification never uses it)
- pipewire + pw-cli present  — audio server; headless verification must not
                               depend on a running server
- python3 numpy 2.5.3 present; python-soundfile ABSENT — recorded so rounds
  don't assume it; sox/ffmpeg are the analysis pipe instead

## Verification discipline (the lane's core rule)
Every audio claim is a measurement, not a listen: duration (ffprobe), peak
and mean loudness (ffprobe/sox stat), spectral content (sox stat spectral
stats / ffmpeg astats), loop-seam continuity (sample-level diff at the seam
via numpy after sox conversion to raw PCM). "Sounds good" is not a verdict;
a measurable proxy (e.g. no clipping: peak < 1.0; loop seam delta below
threshold) is.

## Production map (candidate round claims, north to south)
sfx:    UI blips → impacts (layered noise+sine transients) → movement
        (footsteps: filtered noise bursts, variation via jitter) → ambience
        (looped brown-noise beds with slow LFO)
music:  motif → loop with clean seam → layered stems (base/drum/lead) →
        adaptive crossfade between intensity states
format: wav (master) → ogg (ship) → loop-point metadata; headless checks at
        each step
