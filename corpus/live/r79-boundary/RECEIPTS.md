# r79-boundary receipts

Seat: BOUNDARY (audio, round 79). Host `plazir27`, PipeWire **1.6.8**,
WirePlumber 0.5.17, pactl 17.0-98-gb096, Python 3.14.7 (numpy 2.5.3),
Linux 7.2.3-arch1-3. Repo `~/Projects/shokunin/audio-shokunin` @ HEAD
`a2616f7` (`r78 LOG: adjudicator ADMIT-corr`).

**Tracked edits: zero.** All artifacts below are untracked additions
(`corpus/live/r79-boundary/` + `reports/round-79/r79-boundary.md`). The tree's
tracked dirt (`SHONEN.md`, `corpus/fixtures/measure_audio.py`,
`corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`) belongs to the
r79 author / sibling seats and was never touched here.

## Harness

| file | sha256 | role |
| --- | --- | --- |
| `r79b_probe.py` | `02be5fcf7236c28448cc166e1b37af52ad118a2c1a31eb125c85627d59387691` | main harness, subcommands `g1`..`g7` (own tone, own graph reader, own classifier; never imports `corpus/fixtures`) |
| `r79b_freeze_order.py` | `d90bc95cecc0c93ec9e763f9f9195824a72eedcb78d4b7dc87ead3c1ad63ca41` | SIGSTOP + tone-swap marker; 5 configurations × 2 reps (`source-first`, `loopback-first`, `harness-like`, `harness-like-1swap`, `loopback-first-2swap`) |
| `r79b_selfsink.py` | `d2af3f5553db7d2bd8e827b5ffe1b99482356ae89ec416d45808200eb3541c14` | same-sink self-loop gain (burst + continuous), `-P output.<self>`, `-C output.<self>` |

Reproduction (repo root): `python3 corpus/live/r79-boundary/r79b_probe.py g1`
(…`g2`…`g7`), then `python3 corpus/live/r79-boundary/r79b_freeze_order.py`,
`python3 corpus/live/r79-boundary/r79b_selfsink.py`. Each run is bounded,
probe-owned (`r79b_<pid>_*`, `r79bo_*`, `r79bs_*`), and ends with a
`final_check` block asserting no own node/sink/process survives.

## Receipts (JSON)

| receipt | sha256 | legs |
| --- | --- | --- |
| `r79b-g1.json` | `88b2b59c5d348c6c2d2aecbe825eb656e70e9949d0e2d673dad88b54fa5810cf` | E1 both `-C`/`-P` in one client (g1a–g1g) |
| `r79b-g2.json` | `19f986d32aa8e1d5bccbbc531b2723fbce630507596009f5e55b579b10678824` | E2 kill mid-capture (g2a) + freeze (g2b) + source/consumer freeze controls (g2c, g2d) |
| `r79b-g3.json` | `ebe0098b627a705b65d227e58c8737dee7f022b2500be519b4479e32ac0db07f` | E3 two-loopback cycle (g3a prop, g3b no prop) + kill-return-leg control |
| `r79b-g4.json` | `9f513b11aecb7c66255c52ee67beedd397b9797c9d68497a49750553be46a543` | E4 `pw-cli set-param` mid-stream (5 writes) |
| `r79b-g5.json` | `c188555d7abf5e1189bfb98e91ae39db50bc89dda9b4f78f5a99d027cf69e8b2` | E5 serial vs name (pw-record ×5, pw-loopback ×3) |
| `r79b-g6.json` | `2f59f6980b175cd9771b0beafc991fa3f088b3739340b0592944f648356c6fac` | E6 suspended target (idle, mid-route ×2, at spawn) |
| `r79b-g7.json` | `299f512eb05c1532d7f8d8b19d8517518d1ffa4662789de23d759789f64685e1` | E7 self-binding (5 self-name forms + same-sink) |
| `r79b-freeze-order.json` | `6a772b203cfa2d89b3302983c3a2b0d09cc083307a6fcbe27049db4facffdb70` | freeze + swap-marker, 10 legs (5 configurations × 2) |
| `r79b-selfsink.json` | `3ab64e5752f15bd25d171c5570b800966f2c26149112210604af7133410ecd62` | same-sink gain: burst, continuous, self-name forms B/C |
| `host/null-sink-suspend.txt` | `2961d545b52ed0ee976670f5c698d55cd8de4d32dc9329756aacf8e9e23dca9c` | null-sink suspend semantics (idle SUSPENDED → with stream RUNNING → `suspend-sink 1` rc 0, state unchanged) |
| `host/freeze-phase-check.txt` | `85f60584ee1f9753ec27237036fd9ad8ae454feb5c69d1e2819283b24f0eb1f9` | sine-fit residual on every retained freeze tap: the 1.5 kHz marker is a pure continuous sine (residual ratio 5.3e-5, amp 8191.4) where present; absent in all 2-swap legs |
| `host/contention-20261015T082044Z.txt` | `659f944feee17d82c57f26c04210ecbefe16b3f3bc81ffe895267e20e654810e` | 08:20:44Z read-only contention witness: SPDIF monitor tap all-zero, 0 links touching SPDIF, 11 sibling procs |
| `host/state-end.txt` | `5b863998f65b07b9b717a5812581077275c3a02fdf72cb3d02196371b08fcc2d` | end-of-seat state: defaults, sink states, own-object check (empty), tracked dirt |

Every group JSON carries `host_start`/`host_end` snapshots (default sink/source
metadata, foreign `r7x/r8x` nodes, foreign processes) and a `final_check`
(own nodes after, own sink modules after, own procs alive — all empty in every
group).

## Raw audio (tap witnesses)

`raw/` holds 55 WAVs (55 MB) — the taps analysed in the JSON. Key ones:

| file | what it witnesses |
| --- | --- |
| `raw/g2a_tap_b.wav` | tone ends 1.975 s (kill at 2.0 s), tail 4.0–6.9 s **all-zero** |
| `raw/g2a_tap_out.wav` | consumer attached to the killed node: no fmt/data chunk (killed at the 10 s bound, never progressed) |
| `raw/g2b_tap_b.wav` | freeze leg (2-swap configuration): pre-freeze tone → silence, no marker |
| `raw/g2c_tap_a.wav` | pw-cat source frozen: tone 8191 → 0 for the stop, resumes after SIGCONT |
| `raw/g2d_tap_b.wav` | pw-record consumer frozen: file size constant 2.5 s, resumes after SIGCONT |
| `raw/g3a-cycle-prop_tap_b.wav` | burst recirculates ≥6 s at steady ~983; `…after_kill_l2.wav` = all-zero control |
| `raw/g7f-same-sink-both-sides_…tap.wav` | same-sink loop: ch1 peak 32768 (s16 rail) |
| `raw/selfsink_cont_tap.wav` | continuous: ch1 rail-locked for the whole run **and 2.5 s after the source is killed**; ch0 cancels |
| `raw/r79bo_*_freeze_*.wav` (20 files, 3 script runs) | freeze + swap marker: 1.5 kHz present in **14/20** legs (all 14 single-swap legs), absent in **6/20** (all 6 two-swap legs); where present it is a pure continuous sine (`host/freeze-phase-check.txt`) |

Tones/bursts in `scratch/` were pruned after analysis (deterministic, rebuilt by
the harness on every run).
