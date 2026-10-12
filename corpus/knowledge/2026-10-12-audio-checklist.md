# audio production checklist — initial (mint)

| artifact | falsifiable probe sketch | status |
|---|---|---|
| sine test tone | sox generates 440Hz/1s; ffprobe duration == 1.00s ±10ms, peak < 1.0 | unprobed |
| UI blip | 100ms enveloped sine sweep; duration + envelope decay measured | unprobed |
| impact | layered transient: noise burst + sine thump; peak/duration in spec | unprobed |
| footstep | filtered noise burst, 4 variants differ by measured jitter | unprobed |
| ambience bed | brown-noise loop 30s; seam delta below threshold at loop point | unprobed |
| music loop | 4-bar loop, seam continuity verified sample-level | unprobed |
| stems | 2 stems sum to mix (numpy check within float tolerance) | unprobed |
| adaptive | crossfade 2s between states; loudness continuity measured | unprobed |
| format | wav→ogg round-trip: duration preserved ±20ms | unprobed |
