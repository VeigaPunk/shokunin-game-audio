# R78 adjudicator — playback-direction lattice, default-follow law, props resolution, host-confound accounting

Round: 78. Wave: `shokunin-train-20261101-w19/w20/w21` mixed Sol /
swe-2 / deepseek-v4.1-flash / zfl seats. Work commit `d9aa6f9`
(+2401/−3, 8 entries, 60+ legs); fold lands in this commit
(+~/−~ in `corpus/fixtures/measure_audio.py`).

## Declared move

`--probe-capture-r78`: the playback-direction lattice —
`playback_target_lattice_r78` (target flag/prop/node.target/env
resolution incl. `monitor_name` and `source_peer` legs),
`playback_default_follow_r78` (metadata default follow/moved/
still_probe/restored legs), `playback_target_loss_r78` (unlink-driven
re-link classes), `playback_props_r78` (15-leg prop/flag/env matrix
incl. two stall-class legs), `playback_class_segv_r78` (class-segv
envelopes), `playback_aplay_axis_r78` (ALSA bridge axis),
`capture_unlinked_zeros_r78` and `capture_parec_fix_r78` (capture-side
zeros + parec monitor legs).

## Claim adjudication

- **Target lattice CONFIRMED** — `--target` flag, `target.object`
  prop, `node.target`, and `PIPEWIRE_PROPS` env resolution all armed
  with content-verified taps; the fold made negative pins require a
  *bound* witness tap (unattributed silence proves nothing) and
  `monitor_name` got a second tap on the peer so a peer-only landing
  is still content-verified.
- **Default-follow law CONFIRMED + oracle corrected** — the stream
  follows `default.audio.sink` *metadata* at spawn, not pactl's
  stored default; the fold refreshes the oracle per leg and accepts
  consumers ⊆ {spawn_default, intended} settling to the intended.
  A live session-manager re-assertion (SPDIF over our pw-metadata
  write) was caught by the moved leg landing the live default —
  classified `default_reasserted`, not a failure; pactl-vs-metadata
  divergence is now named `pactl_unmeasured` coverage.
- **Stall class ENVELOPE-VERIFIED** — `class_source_stall`/
  `autoconnect_false` are bimodal: never-scheduled (suspended →
  killed at bound) or scheduled `running` → consume file → rc=0.
  Both realizations share the load-bearing pins (zero consumers,
  output ports published); `stall_realization` is recorded and only
  `other` fails.
- **Host-confound accounting ARMED** — zeros legs snapshot the
  producer edge before unlink; a capture bound to a foreign monitor
  or a feed that never linked records `setup misroute — class never
  armed` (named confound, blocked coverage) instead of a false class
  failure. aplay axis splits foreign nodes (`gst_r81_client` et al.)
  from probe nodes by tag; hold/EBUSY cascades guarded behind
  never-armed checks.
- **Readiness races FIXED fail-closed** — fresh null sinks must
  enumerate in `pactl` AND publish `pw-link -i` playback ports
  (monitor sources: `pw-link -o` output ports) before target legs
  spawn; `boundary_source` must publish capture ports. Probe #6's
  four prop_b fallbacks were enumerated-but-unlinkable ports.
- **Probe arc**: #4/#5 invalidated by disclosed sibling contention
  (r80 by-name `unload-module` lifecycle; r81 `gst_r81_client`);
  #6 → 4 port-readiness failures → wait fix; #7 → 1 runthrough
  realization → stall envelope; #8 → **zero failures** (receipt
  `corpus/live/runs/20261015T055701745739Z-capture-r78/`).
- **Prior behavior**: all pre-r78 probe entries untouched; the fold
  is confined to r78 machinery and shared helpers whose new gates
  only fire on r78 legs.

## Corrections folded

Critic M2–M9 (tap provenance, vacuous pair, absent-leg handling,
loss binding, boundary-source port asserts, stall/follow gates),
reviewer F1 (metadata-guarded pactl delay) + F2–F6, simplifier
(+71/−109, sha fadc1d08 vfold; its `Stream/Input/Audio` host
falsification — rc=1 refusal vs −11 — recorded), boundary's
14 named classes (record-level; future-arm material), verifier
AGREE with coverage findings. Segv legs got `died_before_s`; arecord
legs got the class assert + `alsa_busy` contention naming.

## Record notes

- Foreign-node confounds are *named in receipts*, never silent.
- The bimodal stall realization is scheduler-load dependent — both
  outcomes are the same measured law (no consumer, output ports).
- probe #4/#5 receipts retained under `corpus/live/runs/` as the
  contention-evidence trail; #8 is the clean quiet-window run.

## Verdict

**ADMIT-corr** — the r78 playback/capture lattice is pinned
fail-closed with content-verified taps, spawn-time metadata oracles,
readiness gates, and honest confound/coverage classes.
Seats: scout, author (Sol), boundary, baseline, critic, reviewer,
simplifier, verifier, scribe; fold + adjudicator on swe-2.
