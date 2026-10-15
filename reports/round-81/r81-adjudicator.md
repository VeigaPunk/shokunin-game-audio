# r81 ADJUDICATOR — GStreamer↔PipeWire binding lattice

Seat: ADJUDICATOR (orchestrator) | round 81 | work `6aa03e6` + fold `07c0671`

## Verdict: ADMIT-corr

Admitted with corrections folded in-session. Eleven seat reports on
record: scout, boundary + boundary-readonly, baseline, author, critic,
reviewer, simplifier, verifier, verifier2, scribe, fold.

## What the round measured

`--probe-gst-r81` — the GStreamer↔PipeWire binding lattice (post-fold
54 legs over 7 entries): `pipewiresrc`/`pipewiresink` property grammar
and two-key `target-object=` write; element-prop-beats-stream-props
precedence (inverse of r78's flag-beats-prop law); `device=` silent
fallback vs `pulsesrc` strict refusal; direction-split target loss
(+0.203 s relink on playback vs frozen 204 844 B captures);
`PIPEWIRE_REMOTE` decisiveness; env-vector precedence
(`target.object` > `node.target`); exit-class lattice (rc 1 parse /
255 runtime / outliers); autodetect→pulsesink + missing-default
inheritance; `client.name` null (name rides `application.name`);
`stream.capture.sink`/`node.autoconnect` as STRING "TRUE"/"FALSE".

## The mechanism (r91 scout, folded as context)

`gstpipewiresrc.c:1207` sets `PW_STREAM_FLAG_DONT_RECONNECT`
unconditionally on capture; WirePlumber `prepare-link.lua:73` drops
re-links under it — the capture-freeze law is explained, not just
measured. Reviewer F2's own receipt carries the discriminator:
`node.dont-reconnect: true` on all 96 gst-capture samples.

## Record corrections applied in fold (`07c0671`)

- Scout hex constant FALSIFIED twice: frozen-WAV `data` field is
  `0x7FFF0000` (riff_size `0x7FFF0024`), never `0x7FFFF000` —
  boundary-readonly + author receipts both confirmed; the fold made
  the freeze predicate PIN the corrected constants (reviewer F1 /
  simplifier S7 — the landed predicate previously accepted the
  falsified value, dead acceptance criterion).
- Scout `num-buffers` claim falsified by boundary: on the pulse
  record path `frames = num-buffers x blocksize/frame_bytes`, exact
  9/9.
- Simplifier S1-S9 + L1 folded: ports build, `_props`, kill_proc/call
  arms, ns/tag ctx keys, `<tone>` token, expect_class write-only
  slots, `_gst_r81_ns_ensure` -> `_loopback_r79_sinks_load` reuse,
  redundant wall_caps, dead leg p8 (byte-identical to p5).
- Reviewer F3: e3/e8/e9 given real filesink out_paths (vacuous
  assertions -> substantive; the naive e8 fix was tested and rejected
  — wavenc accepts F64LE — replaced with a tee-based pipeline that
  still refuses caps honestly).
- Claim corrections recorded: exit-count 6/8 (baseline) vs author's
  "7/8" — baseline's commands.log rules (scribe F3); "369"-style
  arithmetic clean on audio side; scout `Codec/Muxer` truncated klass
  (actual `Codec/Muxer/Audio`).

## Finding dispositions

| finding | disposition |
|---|---|
| freeze predicate accepts falsified 0x7FFFF000 | FIXED (pins corrected constants) |
| num-buffers not-a-bound claim | FALSIFIED — exact relation recorded |
| dead leg p8 / S1-S9 dead code | FOLDED (-75/+50, verifier2-verified) |
| e3/e8/e9 vacuous assertions | FIXED (real out_paths) |
| reviewer F2 dont-reconnect witness unreferenced | RECORDED — mechanism scout c58ac36 covers it; fixture framing noted |
| critic F4 foreign r92s_* in capture window | RECORDED — sibling scout contention, named class |
| scribe F1/F2 scout text retains falsified constants | ACCEPTED — historical report; corrections live in boundary/author/fold |
| scribe F3 author/baseline exit-count discrepancy | RECORD-corrected (6/8) |
| verifier reservation: capture-r78 follow leg host-luck | DISCLOSED — contention class, not r81 regression |
| comm-keyed quiet-check blind spot (pw-record comms) | RECORDED — census limitation, pre-existing |

## Evidence status

- Folded bytes `07c0671`: verifier2 VERIFIED — `--probe-gst-r81`
  failures {} over 54 legs, freeze legs empirically carry corrected
  constants, battery 86/136 unchanged, `normal` receipt sha
  `8e8cdad6…` byte-identical (7-way across seats).
- Non-author chain: r81-verifier VERIFIED-WITH-RESERVATIONS on
  `6aa03e6` (all claims verbatim; 2 transient reds = sibling r92s
  contention, `normal` byte-identity exonerated); r81-verifier2
  VERIFIED on fold. Satisfies non-author requirement on admitted
  bytes; single git identity fleet-wide, disclosed.
- Residuals: capture-r78 `playback_default_follow` leg is
  host-contention-sensitive by construction (baseline reds under
  r91-scout, verifier's under r92-scout — named class); 5/12 shipped
  configs not authoritatively measured (second-PipeWire refusal,
  shared host); formal-run stdout not pinned (receipts only).

## LOG entry

round 81 — gst↔pipewire binding lattice (ADMIT-corr); commits
`6aa03e6` (work) + `07c0671` (fold) + this record commit.
