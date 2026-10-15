# R79 BOUNDARY — the pw-loopback edges the arms did not probe

Round 79 post-landing boundary pass. Repo `~/Projects/shokunin/audio-shokunin`
@ HEAD `a2616f7` (`r78 LOG: adjudicator ADMIT-corr`). Host `plazir27`.
Toolchain: PipeWire **1.6.8** (pw-loopback / pw-record / pw-cat / pw-cli /
pw-dump / pw-link), WirePlumber **0.5.17**, pactl **17.0-98-gb096**, Python
**3.14.7** (numpy 2.5.3), Linux **7.2.3-arch1-3**. Measured 2026-10-15
04:59–08:21Z.

**Seat: BOUNDARY (leaf). Zero tracked-file edits.** Every write is under
`corpus/live/r79-boundary/` plus this report; nothing committed. The tree's
tracked dirt (`SHONEN.md`, `corpus/fixtures/measure_audio.py` (+2737/−3,
author-owned), `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`)
was present at entry and was **never read, imported or executed** by this seat
— the harness is self-contained (own tone, own graph reader, own classifiers;
no import path to `corpus/fixtures`). `git status` shows exactly two new
untracked paths from this seat: `corpus/live/r79-boundary/` and
`reports/round-79/`.

**Concurrency.** Sibling r79 seats were live for the whole window: the
`--probe-capture-r79` arm was being re-run repeatedly (`r79lb_*` probe nodes,
r79-simplifier control runs, r79-verify forge runs), and foreign null
sinks (`r79lb_ns_a_4041488`, `r79lb_ns_b_4041488`, `r79lb_ns_b_224789`,
`r79lb_ns_a_229236`, `r79lb_ns_b_229236`, `r79lb_hp_229236`, …) persisted in
the graph. Every leg here is `r79b_<pid>_*` / `r79bo_*` / `r79bs_*`-tagged and
torn down in a `finally`; every group JSON carries `host_start`/`host_end`
snapshots and a `final_check` (own nodes/modules/processes after: **all empty
in all seven group runs**). §6 is the contamination ledger.

**Fail-closed tone discipline (inherited from the r79 scout).** Tone only ever
enters probe-owned null sinks. Any leg whose effective destination can be the
shared default sink (SPDIF) is fed **digital silence** or nothing, and its
verdict is topology-only (`content_witness = declined_shared_default`). The
legs whose capture side reads the shared sink monitor (g1c/g1e/g7a/g7c) never
receive tone from this seat.

---

## 0. Headline — the seven assigned edges

| # | assigned edge | class (canonical) | verdict | the single sharpest measured fact |
| --- | --- | --- | --- | --- |
| 1 | `-C` and `-P` both resolvable / unresolvable in one client | `both_sides_independent`; `both_sides_fallback_pair_self_loops_shared_sink` | **independent sides; the both-fallback pair is a loop, not an inert pair** | g1b/c: one side honored while the other falls back, no coupling. g1d: no prop + both garbage → capture **unnegotiated** (zero ports, `suspended`) + playback → default sink. g1e: prop + both garbage → capture ← **default sink monitor** and playback → **default sink** in the *same client* — a self-loop through the shared sink (structural; content injection declined) |
| 2 | kill the loopback client mid-capture (partial-link teardown) | `kill_teardown_atomic_within_25ms`; `orphan_consumer_survives_unlinked` | **atomic teardown; the consumer attached to the node is orphaned silently** | at +0.1 s after SIGKILL both nodes and every link touching them are gone; the ns_b tap's tone ends at 1.975 s vs kill at 2.0 s (**≤25 ms**) and the tail 4.0–6.9 s is all-zero; the `pw-record --target output.<lb>` consumer stays present, unlinked, never errors, and never completes (killed at the 10 s bound → WAV with no fmt/data chunk) |
| 2b | (bonus) freeze the client mid-capture | `freeze_outcome_is_reconfiguration_dependent` (14/20 vs 6/20); `freeze_keeps_path_live_for_in_flight_sources`; controls `single_stream_freeze_blocks` | **the loopback's path is not reliably gated by its client process — and not reliably live either** | with the client in state `T` (`TLl`, 3 threads) the ns_b tap carried the **swapped-in 1.5 kHz marker** at full amplitude (pure continuous sine, residual ratio 5.3e-5) in **14/20 retained legs — every single-swap leg — and in none of the 6 two-swap legs**; the marker lasts only ~1.3–2 s of tap time before silence, and sources created while frozen never sustain. Controls: a frozen `pw-cat` source goes silent and a frozen `pw-record` consumer's file stops growing — a *single stream* is client-gated, the loopback pair is not |
| 3 | two loopbacks targeting each other (cycle) | `cycle_allowed_no_refusal`; `burst_recirculation_bounded`; `cycle_requires_capture_sink_prop` | **no refusal; the cycle is a stable recirculator** | 8 links close the loop (ns_a:monitor→L1.input, L1.output→ns_b, ns_b:monitor→L2.input, L2.output→ns_a); a 0.25 s burst leaves a sustained ~**983** (≈12 % of injected) oscillation for the whole 5.4 s tail with a flat trend, and killing L2 drops the tap to **all-zero** in ≤1 s. Without `stream.capture.sink=true` no cycle exists (capture unnegotiated, tap all-zero) |
| 4 | `node.target` written via `pw-cli set-param` mid-stream | `set_param_props_accepted_not_applied` | **accepted (rc=0) and completely inert** | five writes (output `target.object`→ns_c, output `target.object`→garbage, output `node.autoconnect=false`, input `target.object`→ns_c, input `stream.capture.sink=false`) all return rc=0 with empty stderr; read-back props are **unchanged**, links never move, tone keeps landing at ns_b and ns_c stays all-zero, client alive |
| 5 | `pw-record` targeting a loopback output node by serial vs name | `numeric_target_is_object_serial_not_node_id`; `numeric_nonmatch_falls_back_like_garbage`; `capture_class_serial_target_links_monitor_without_prop` | **numeric = `object.serial`, never the global node id; serial and name are not equivalent** | `--target output.<lb>` and `--target 74176` (its serial) resolve the **same node** (tone carried); `--target 149` (its global id) dies `no target node available` (44-byte file). For the *capture* node, `--target 74177` (serial, **no prop**) links `input.<lb>:monitor_*` and carries tone, while the same node by *name* without the prop does not link — the prop is required for *name* targets only. `pw-loopback -C/-P` numeric targets follow the same serial rule; ids fall back like garbage (both sides → SPDIF) |
| 6 | loopback created while its target is suspended | `null_sink_suspend_noop_for_state_and_path`; `suspended_target_links_and_carries` | **suspension is unobservable on a null sink — the edge is vacuous here** | idle null sink = `SUSPENDED`; with a stream = `RUNNING`; `pactl suspend-sink 1` returns rc=0 and the state stays `RUNNING`. A loopback created against an explicitly suspended target links and carries tone (peak 8192); suspending either side mid-route changes neither links nor content. Real ALSA sinks were not probed (contamination scope) |
| 7 | `target.object` at the loopback's own peer (self-binding) | `spawn_time_self_reference_unresolved`; `same_sink_loop_comb_resonator` | **self-names never resolve; the same-sink form is an unstable resonator** | all five self-name forms (`-C output.<self>`, `-P input.<self>`, `-C input.<self>`, `-o target.object=input.<self>`, `-i target.object=input.<self>`) fail to bind to the client's own peer and land on the r78 fallback lattice instead (default sink / default sink monitor / unnegotiated) — **no self-link is ever created**. But `-C ns_a -P ns_a` (same sink both sides) is a loop through the sink: at 1.5 kHz the tap goes from 8192 to **16384 to 32768 (s16 rail)** within 0.25 s and **stays rail-locked for 2.5 s after the source is killed**; at 1 kHz the loop cancels (8192→8217→28) |

---

## 1. Method

One harness (`r79b_probe.py`, subcommands `g1`…`g7`) plus two focused
follow-ups (`r79b_freeze_order.py`, `r79b_selfsink.py`). Every leg:

* fresh processes (a new `pw-loopback` per leg; fresh `pw-record`/`pw-cat`
  per sample), tagged `r79b_<pid>_<leg>` / `r79bo_*` / `r79bs_*`;
* bounded (outer `timeout -s KILL` for the persistent client; `pw-record -n`
  frame counts; `sh()` timeouts);
* probe-owned sinks only, with the fail-closed tone rule above;
* sampled from a live graph (`pw-dump` parsed into nodes/ports/links by
  `node.name`, plus `pw-link -l` and `ps` cross-checks);
* analysed with per-channel peak/RMS, an rfft dominant-frequency classifier,
  a per-channel Goertzel amplitude scan (50 ms windows / 25–50 ms steps) for
  transitions and recirculation, and a sine-fit residual check (phase
  continuity, used to rule out stale-buffer replay);
* torn down in a `finally` and verified (`final_check`).

Receipts, sha256s and the raw tap WAVs are indexed in
`corpus/live/r79-boundary/RECEIPTS.md`. All seven group JSONs carry
`final_check` with no own node, module or process surviving; the two follow-up
scripts tear down in a `finally` and a post-run check (after the last script)
found no `r79bo_*`/`r79bs_*` node, sink or module left.

**Known harness defects (declared).** (a) `pw-record`'s file time axis lags the
process start by ≈0.5–1.5 s on this host, so *tap-relative* timestamps were
never used to date an event; the freeze legs use an in-band **tone-swap marker**
instead, and the kill leg's ≤25 ms figure is a *tap-local* delta (last tone
window vs the kill's tap-local position). (b) The `sink_state()` helper in
`r79b_probe.py` mis-parsed `pactl list sinks short` under load and reported
"absent"; the suspend-state evidence therefore comes from the dedicated
transcript `host/null-sink-suspend.txt` (shell, same probe sink), and the g6
content verdicts stand on their own taps.

---

## 2. Findings per edge

### E1 — both sides in one client (`r79b-g1.json`, legs g1a–g1g)

| leg | `-C` / `-P` | capture resolved to | playback resolved to | content |
| --- | --- | --- | --- | --- |
| g1a | ns_a + prop / ns_b | `ns_a:monitor_FL/FR` | `ns_b:playback_FL/FR` | tone at ns_b, peak 8192 |
| g1b | ns_a + prop / garbage | `ns_a:monitor_FL/FR` | **SPDIF** (default sink) | — (silence-fed) |
| g1c | garbage + prop / ns_b | **SPDIF monitor** | `ns_b:playback_FL/FR` | — (silence-fed) |
| g1d | garbage / garbage, **no prop** | **none** (zero ports, `suspended`) | **SPDIF** | — |
| g1e | garbage + prop / garbage | **SPDIF monitor** | **SPDIF playback** | — (structural loop) |
| g1f | ns_a + prop / ns_b + `-o target.object=ns_c` | `ns_a:monitor_FL/FR` | **ns_c** (prop beats flag) | tone at ns_c 8192 |
| g1g | `--capture`/`--playback` long forms | as g1a | as g1a | tone at ns_b 8192 |

* The two sides are **resolved independently in one client**: a fallback on
  one side never changes the other side's resolution (g1b, g1c).
* The capture fallback is the author's conditional: with the prop and no
  resolvable target → default sink monitor (g1c, g1e); **without** the prop →
  the source domain, and with no live `default.audio.source` on this host the
  capture node publishes **zero ports and `suspended`** (g1d) — the
  `capture_default_source_unnegotiated` shape, reproduced in a both-sides leg.
* **New class — the both-fallback pair is a loop.** g1e has
  `SPDIF:monitor_* → input.<lb>` *and* `output.<lb> → SPDIF:playback_*` in one
  client: any content on the shared default sink is copied back into it. No
  tone was fed and no content witness was taken (contamination rule), so this
  is a *structural* verdict — but §2/E7 measures what that structure does to
  content when it can (comb resonator, §2/E7). The author's b09/c03…c06 legs
  each fall back on **one** side only; the pair is a cell the arm never builds.
* Long-form flags are equivalent to `-C`/`-P` (`--capture`/`--playback`), as
  the help text implies; the brief's `--capture-target`/`--playback-target`
  spellings do not exist on this version.

### E2 — kill mid-capture (`r79b-g2.json`, legs g2a–g2d) + freeze follow-ups

**g2a (SIGKILL at t≈2.0 s of a live tone-carrying route).**

| witness | before | after |
| --- | --- | --- |
| loopback nodes | `input.<lb>`, `output.<lb>` present, `running` | **both gone at +0.1 s** |
| links | ns_a:monitor→input, output→ns_b playback, output→tap_out (×2 ch) | **none at +0.1 s** (every link touching the pair gone together; no orphan link object) |
| tap on ns_b (sink monitor) | tone 8191 | last tone window **1.975 s** → silence within one 25 ms step; tail 4.0–6.9 s peak/rms **0** |
| `pw-record --target output.<lb>` | linked to the output node's ports, `running` | present and unlinked at +0.1/+0.3/+0.6 s (`running`→`idle`), **never exits**, no error; killed at the 10 s reap bound → WAV with **no fmt/data chunk** |

So the teardown is atomic and fast, and the *consumer* attached to the dying
node is silently orphaned — it neither errors nor falls back. (One earlier
iteration of the same leg — not retained as a receipt — showed the other
possible shape: the orphan ran to completion and wrote a full-length,
silent tail. Both shapes agree on "no error, no fallback"; the difference is
whether the orphan keeps consuming.)

**g2b (SIGSTOP the client; tone-swap marker) + the freeze-order follow-up.**

The marker design removes the tap's time-axis offset: at the freeze instant the
1 kHz source is killed and a 1.5 kHz source started; if the 1.5 kHz appears in
the tap *while the client is in state `T`*, the route is live. The follow-up
script ran 5 configurations × 2 reps (`r79b-freeze-order.json`), and the
harness leg ran the same shape twice:

| configuration (retained) | legs | marker present | marker absent |
| --- | --- | --- | --- |
| `source-first` (tone, then loopback) | 4 | 4 | 0 |
| `loopback-first` (loopback, then tone) | 4 | 4 | 0 |
| `harness-like-1swap` (loopback → wait → tone → tap → stop, one swap) | 2 | 2 | 0 |
| `harness-like` (same, two swaps) | 4 | 0 | 4 |
| `loopback-first-2swap` | 2 | 0 | 2 |
| harness g2b (two swaps) | 2 | 0 | 2 |

* Where the marker is present it is a **pure continuous 1.5 kHz sine** at amp
  8191.4 (sine-fit residual ratio 5.3e-5 — not stale-buffer replay, not noise);
  it appears **within one 250 ms sample of the swap** and lasts ~1.3–2 s of tap
  time before the tap goes silent.
* **Single swap: 14/14 live. Two swaps: 0/6 live.** The association is strong
  and reproducible, but *acausal on its face* (the second swap happens after
  the first), and the mechanism is **unexplained** — the honest reading is
  `freeze_outcome_is_reconfiguration_dependent`: the frozen route can carry
  live content and can be silent, and sources created while it is frozen
  deliver only briefly.
* Controls under identical treatment (g2c, g2d): a frozen **`pw-cat` source**
  stops producing (tap 8191 → 0, resumes after SIGCONT); a frozen **`pw-record`
  consumer** stops consuming (tap file size constant at 389164 B for 2.5 s,
  then grows again after SIGCONT). So a *single stream* is client-gated; the
  loopback pair is not.
* Earlier ad-hoc iterations of the same test (scripts and taps not retained)
  showed the marker in 9/9 runs; they are cited only as context, not as
  receipts.

Consequences for the arm: **client liveness is not path liveness** (a stopped
client is still `alive`), and **path silence is not client death** either. A
stall-envelope or hot-plug verdict must not be inferred from rc or process
state alone.

### E3 — two loopbacks targeting each other (`r79b-g3.json`)

g3a (`-C ns_a -i prop -P ns_b` and `-C ns_b -i prop -P ns_a`):

```
ns_a:monitor_FL/FR -> input.L1     output.L1:output_FL/FR -> ns_b:playback_FL/FR
ns_b:monitor_FL/FR -> input.L2     output.L2:output_FL/FR -> ns_a:playback_FL/FR
```

* **No refusal**: WirePlumber creates all four links; both clients stay alive;
  no stderr, no error state. `node.link-group` (the "client links these
  itself" hint) does not act as cycle detection.
* A 0.25 s / 8192 burst into ns_a leaves a **sustained ~983** (≈12 %)
  1 kHz oscillation in the ns_b tap for the remaining 5.4 s; the amplitude
  trend is flat (833–983, no growth, no decay), i.e. a stable recirculation
  with comb interference, not a runaway.
* Control: killing L2 (the return leg) drops the tap to **all-zero** within
  1 s — the sustained tone was the cycle, not a stale tap.
* g3b (no `stream.capture.sink=true`): no capture links (unnegotiated), no
  cycle, tap all-zero. On this host the cycle **requires the capture-side prop
  on both clients** — without a live default source there is no other way for
  a capture stream to reach a sink monitor.

### E4 — `pw-cli set-param` mid-stream (`r79b-g4.json`)

Live route `ns_a (tone) → input.lb → output.lb → ns_b`, then five writes with
`pw-cli set-param <node-id> Props '<json>'`:

| write | target | rc | read-back | links | content |
| --- | --- | --- | --- | --- | --- |
| `{ "target.object": "<ns_c>" }` | output id 93 | 0 | `target.object` stays `ns_b` | unchanged | tone at ns_b 8192, ns_c all-zero |
| `{ "target.object": "no_such_node_<pid>" }` | output | 0 | unchanged | unchanged | (same route) |
| `{ "node.autoconnect": false }` | output | 0 | `node.autoconnect` stays `True` | unchanged (still linked) | — |
| `{ "target.object": "<ns_c>" }` | input id 116 | 0 | unchanged | unchanged | — |
| `{ "stream.capture.sink": false }` | input | 0 | unchanged | unchanged | — |

`target.object` is a **spawn-time** property: the session manager resolves it
when the stream registers, and later `Props` writes neither re-resolve nor
unlink. (The write may not even reach the param — the read-back is identical —
so the class is deliberately "accepted, not applied"; an `enum-params Props`
witness was not taken.)

### E5 — serial vs name (`r79b-g5.json`)

Node identities in the leg: `input.<lb>` id 88 / serial 74177; `output.<lb>`
id 149 / serial 74176; ns_a id 152 / serial 74158; ns_b id 94 / serial 74165.

| leg | target | resolved producers | content |
| --- | --- | --- | --- |
| g5a | `output.<lb>` (name) | `output.<lb>:output_FL/FR` | tone 8192 |
| g5b | `74176` (output **serial**) | `output.<lb>:output_FL/FR` | tone 8192 |
| g5c | `149` (output **global id**) | *(none)* `no target node available`, 44 B file | — |
| g5d | `74177` (input serial, **no prop**) | `input.<lb>:monitor_FL/FR` | tone 8192 |
| g5e | `input.<lb>` (name) + prop | `input.<lb>:monitor_FL/FR` | tone 8192 |
| g5f | `pw-loopback -C 74158 -P 74165` | ns_a monitor / ns_b playback | tone at ns_b |
| g5g | `pw-loopback -C 152 -P 94` (ids) | **SPDIF monitor / SPDIF playback** (both fallback) | — (silence-fed) |
| g5h | `-C 74158` + `-P ns_b` | ns_a monitor / ns_b playback | tone at ns_b |

* Numeric targets are matched against **`object.serial`**, never the global
  node id (pw-record and pw-loopback alike). A non-match behaves exactly like
  garbage: pw-record fails with `no target node available`; pw-loopback falls
  back silently to the default sink / default sink monitor.
* **Name and serial are not equivalent for a capture-class node**: by *name*
  without the sink prop, `input.<lb>` is looked up in the source domain and
  does not link (the author's d2a); by *serial* the same node links its
  `monitor_*` ports and carries tone. The "the prop is required to reach the
  monitor" rule is a *name-target* rule.
* Structural hazard (inference, not measured): any numeric target that happens
  to equal *another* node's serial silently resolves to that node. Ids and
  serials are different namespaces on this host (ids ≈ 88–152, serials ≈
  74158+), so a collision is unlikely but not excluded.

### E6 — suspended target (`r79b-g6.json` + `host/null-sink-suspend.txt`)

* Idle null sink: `SUSPENDED`. With a stream attached: `RUNNING`.
  `pactl suspend-sink <null-sink> 1` → rc 0, **state unchanged** (`RUNNING`);
  `suspend-sink 0` → rc 0. Suspension of a null sink is a no-op.
* g6a (idle/suspended playback target): links form, tone carried (8192).
  Mid-route suspend of the playback target, then of the capture target:
  links and content **unchanged** in every phase (idle → suspended → resumed →
  capture suspended → capture resumed), tone 8192 throughout.
* g6e (target explicitly suspended *before* the loopback spawns): links form,
  tone carried — identical to the idle case.
* The edge as assigned is therefore **vacuous on null sinks**; a real
  suspended ALSA device could not be probed without touching the shared
  devices (out of contamination scope). A future leg built on `pactl
  suspend-sink <null-sink>` would be a false negative by construction.

### E7 — self-binding (`r79b-g7.json`, `r79b-selfsink.json`)

| leg | form | what happened |
| --- | --- | --- |
| g7a | `-C output.<self>` + prop | capture fell back to **SPDIF monitor** (self-name unresolved); playback ns_b |
| g7b | `-P input.<self>` | output fell back to **SPDIF** |
| g7c | `-C input.<self>` + prop | capture fell back to **SPDIF monitor** |
| g7d | `-P ns_b -o target.object=input.<self>` | output fell back to **SPDIF** (prop beats flag → unresolvable → fallback) |
| g7e | `-C ns_a -i target.object=input.<self>` | capture **unnegotiated** (zero ports, `suspended`) |
| selfsink-B | `-P output.<self>` | output → **SPDIF** |
| selfsink-C | `-C output.<self>` (no prop) | capture **unnegotiated**; output → ns_b |

* **Spawn-time self-reference never resolves**: in 7/7 forms the client's own
  peer node is not a usable target at link time. The r79 scout's shape
  invariant ("zero links join the pair") survives — not because a self-link is
  refused, but because the name is not resolvable when the session manager
  resolves targets. This is the *mechanism* behind that invariant, and it
  means a self-target is a silent fallback, not an error.
* **The same-sink form is a loop**: g7f (`-C ns_a -P ns_a`) links
  `ns_a:monitor → input.lb` and `output.lb → ns_a:playback`. With a continuous
  stereo tone (L 1 kHz / R 1.5 kHz, amp 8192), `r79b-selfsink.json` A2:

| tap time | ch0 (1 kHz) peak | ch1 (1.5 kHz) peak | note |
| --- | --- | --- | --- |
| 0.00 s | 8192 | **16384** | first lap already summed |
| 0.25 s → 2.75 s | 8195 → 8217 (slow creep) | **32768** (s16 rail, clipped) | ch1 resonant, ch0 near-cancelling |
| 3.00 s (source killed) | **28** | **32768** | ch1 keeps oscillating at the rail |
| 5.50 s (client killed) | 0 | 0 | control |

  The same-sink loop is a **comb resonator**: at frequencies where the loop
  delay is constructive it is unstable (grows to the rail and **self-sustains
  after the source is removed**); where it is destructive it cancels. With a
  0.25 s burst (amp 1024) instead, the loop held a steady 1023 for 3.5 s
  (bounded, no growth) and went to zero when the client was killed.
* Measurement bound: the tap is s16, so "32768" is the *tap's* rail; the graph
  itself is float32 and may exceed ±1.0. No claim is made about the graph's
  internal amplitude beyond "≥ full scale".

---

## 3. Named classes (canonical list)

| class | one-line definition | receipt |
| --- | --- | --- |
| `both_sides_independent` | in one client the two sides resolve independently; a fallback on one side does not move the other | g1.json g1a–g1c, g1f, g1g |
| `capture_side_fallback_needs_live_default_source` | `-C` without the sink prop falls to the *source* domain; with no live default source the node publishes zero ports and stays `suspended` | g1.json g1d |
| `both_sides_fallback_pair_self_loops_shared_sink` | prop + both targets unresolvable → capture = default-sink monitor and playback = default sink in one client → a loop through the shared sink | g1.json g1e; g5.json g5g |
| `kill_teardown_atomic_within_25ms` | SIGKILL of the client removes both nodes and every link in ≤25 ms, no orphan link | g2.json g2a |
| `orphan_consumer_survives_unlinked` | a consumer attached to the destroyed node stays present, unlinked, never errors, never falls back; either stalls (unfinalized WAV) or runs out its frame count silently | g2.json g2a (`raw/g2a_tap_out.wav`) |
| `freeze_outcome_is_reconfiguration_dependent` | with the owning process SIGSTOP'd, the route's liveness depends on the source-reconfiguration sequence: the swap marker appears in every single-swap leg (14/14) and in no two-swap leg (0/6); mechanism unexplained | freeze-order.json (20 legs) |
| `freeze_keeps_path_live_for_in_flight_sources` | when live, the marker appears within one 250 ms sample of the swap as a pure continuous sine (residual 5.3e-5), then fades within ~1.3–2 s; sources created while frozen never sustain | freeze-order.json; host/freeze-phase-check.txt |
| `single_stream_freeze_blocks` | a frozen `pw-cat` source stops producing; a frozen `pw-record` consumer stops consuming | g2.json g2c/g2d |
| `cycle_allowed_no_refusal` | two loopbacks targeting each other link without error; no cycle detection | g3.json g3a |
| `burst_recirculation_bounded` | the cycle sustains a burst at a steady level (no growth, no decay) for the whole window | g3.json g3a (`raw/g3a-cycle-prop_tap_b.wav`) |
| `recirculation_stops_when_return_leg_killed` | killing one leg of the cycle silences the tap | g3.json g3a control |
| `cycle_requires_capture_sink_prop` | without the capture prop there is no cycle on a host with no live default source | g3.json g3b |
| `set_param_props_accepted_not_applied` | `pw-cli set-param <node> Props …` returns rc 0 but nothing changes (props, links, content) | g4.json |
| `numeric_target_is_object_serial_not_node_id` | numeric targets match `object.serial`; the global node id never matches | g5.json g5b/g5c, g5f/g5g |
| `numeric_nonmatch_falls_back_like_garbage` | a numeric non-match behaves as garbage: silent r78 fallback (loopback) / `no target node available` (record) | g5.json g5c, g5g |
| `capture_class_serial_target_links_monitor_without_prop` | for a capture-class node, serial targeting reaches its `monitor_*` ports without the sink prop, unlike name targeting | g5.json g5d vs d2a |
| `null_sink_suspend_noop_for_state_and_path` | `pactl suspend-sink` on a null sink changes neither state nor path | host/null-sink-suspend.txt; g6.json |
| `suspended_target_links_and_carries` | a loopback created against a (explicitly) suspended null-sink target links and carries tone | g6.json g6e, g6a |
| `spawn_time_self_reference_unresolved` | the client's own `input.<self>`/`output.<self>` is never a usable target at link time; every form falls to the fallback lattice | g7.json g7a–g7e; selfsink.json B/C |
| `same_sink_loop_comb_resonator` | `-C ns -P ns` is a resonator: constructive frequencies grow to the rail and self-sustain after the source stops; destructive ones cancel; bursts stay bounded | g7.json g7f; selfsink.json A/A2 |
| `shared_sink_amplification_hazard` (inference) | the both-fallback pair is structurally the same loop through the shared default sink, so foreign content on that sink can be amplified/clipped for as long as such a client lives | derived from g1e + selfsink A2 |

---

## 4. Falsification list

Each class dies on the stated counter-evidence; none was observed in this
window.

1. `both_sides_independent` — a leg where a fallback on one side changes the
   other side's resolution (none in g1a–g1g).
2. `both_sides_fallback_pair_self_loops_shared_sink` — a host with a live
   default source where the capture side of the both-fallback pair resolves to
   that source instead of the default sink monitor. The class is *conditional*
   on the author's own `capture_default_source_unnegotiated` condition.
3. `kill_teardown_atomic_within_25ms` — a lingering link or node at +0.1 s, or
   a tone tail longer than one 25 ms window (2/2 runs: none).
4. `orphan_consumer_survives_unlinked` — an orphan that errors, exits cleanly
   with the loss reported, or re-links elsewhere. Observed shapes: stalled
   (2/2 retained) and completed-silent (1 earlier run) — both are "survives
   silently"; a *reporting* orphan would falsify the class.
5. `freeze_outcome_is_reconfiguration_dependent` / `freeze_keeps_path_live_for_in_flight_sources`
   — the two shapes already coexist (14 live / 6 silent, cleanly split by the
   swap sequence). The class set is falsified if the split is shown to be a
   harness artifact (e.g. all live legs share a different driver); a
   driver-ownership instrument (`pw-top` driver column, or the source) would
   settle it. A further falsifier: a single-swap leg with no marker, or a
   two-swap leg with one.
6. `cycle_allowed_no_refusal` — a refusal/error on the second link, or a
   WirePlumber version that detects the cycle.
7. `burst_recirculation_bounded` — monotone growth of the burst amplitude
   (peak doubling per lap). The 0.25 s burst did not grow; the *continuous*
   source did (same-sink form) — so "bounded" is a burst claim only.
8. `set_param_props_accepted_not_applied` — any write whose read-back changes
   (then the class becomes "applied but not acted upon", a different finding).
9. `numeric_target_is_object_serial_not_node_id` — a node whose serial equals
   another node's id (misresolution) or a version that accepts node ids.
10. `capture_class_serial_target_links_monitor_without_prop` — a serial target
    that fails to link while the name target links (would restore symmetry).
11. `null_sink_suspend_noop_for_state_and_path` — a state change or content
    gate on a null sink under `pactl suspend-sink` (not observed: `RUNNING`
    stays `RUNNING`, tone 8192 in every phase).
12. `spawn_time_self_reference_unresolved` — any self-name form that links to
    the client's own peer (7/7 failed to).
13. `same_sink_loop_comb_resonator` — a frequency/delay combination where no
    growth occurs (ch0 at 1 kHz is exactly such a case; the class is
    frequency-conditional by construction).

---

## 5. Which r79 legs each class threatens

| class | threatened r79 legs (author `r79-author.md` §; scout `r79-scout.md` §) | why |
| --- | --- | --- |
| `both_sides_fallback_pair_self_loops_shared_sink` | b09 (scout B09), c03–c06, c10, e1, e3; scout §9 contamination ledger | each of those legs makes **one** side fall back to the shared default sink; the pair is a new cell. If any future leg pins capture→default-sink-monitor *and* playback→default-sink, its "topology-only, content declined" verdict is no longer sufficient: the leg is an active loop, and (via `same_sink_loop_comb_resonator`) foreign content can be amplified. The fail-closed tone guard protects *our* tone, not the shared sink from being driven |
| `kill_teardown_atomic_within_25ms`, `orphan_consumer_survives_unlinked` | d2a–d2d, D17; §10 teardown (`own_nodes_after: []`) | the arm's record legs attach consumers to loopback nodes and sample **while alive**; the boundary shows what happens when the node dies under a live consumer — no error, no fallback, no name the arm's teardown assertion would catch (the orphan is not `r79lb_*`). §10's "client never exits" statements hold for hot-plug (target unload) but not for client death |
| `freeze_outcome_is_reconfiguration_dependent`, `freeze_keeps_path_live_for_in_flight_sources`, `single_stream_freeze_blocks` | e1–e3 ("client alive throughout"), d12/d13 (`killed_at_bound` expected shape), inherited-defect #3 class (`no target node available`) | the arm uses **client liveness** (`rc −9 at bound`, process alive) as the witness that the route is up. A stopped client is also alive, and a live client can be silent: liveness and silence are both non-witnesses for the loopback pair. Any stall-envelope verdict ("never links", "stalls to the bound") must not be inferred from rc alone |
| `set_param_props_accepted_not_applied` | §1 prop inventory ("`target.object` stored verbatim"), §2/§3 resolution model | supports both: props are spawn-time; there is no mid-stream control surface via `pw-cli`. A future "move a live route by writing props" leg is refused by measurement |
| `numeric_target_is_object_serial_not_node_id`, `numeric_nonmatch_falls_back_like_garbage` | d2b/d2c/D17 (record by name), b/c lattices (by name), b06/c05 (`0`) | the arm's targets are all **names**; the numeric namespace is a separate lattice cell with a different non-match behaviour (record: hard error; loopback: silent fallback). `--target 0` remains the don't-link idiom; `-C 0`/`-P 0` remain "not a don't-link idiom" |
| `capture_class_serial_target_links_monitor_without_prop` | d2a (the `input.<lb>` no-prop arm) | d2a's verdict ("default-source arm") is **name-specific**; by serial the same node links its monitor ports. The rule "the prop is required to reach the monitor" needs "for name targets" |
| `cycle_allowed_no_refusal`, `burst_recirculation_bounded` | §10/§12 guards, e1–e3 content witnesses, `node.link-group` reading | the graph has no cycle detection for monitor-fed loops; `node.link-group` is not a guard. If any arm leg ever closes a loop (none does today), every content witness inside it is suspect |
| `null_sink_suspend_noop_for_state_and_path` | none (pre-emptive) | the arm has no suspended-target leg; a would-be leg on a null sink is vacuous (false negative by construction) |
| `spawn_time_self_reference_unresolved` | §1 shape ("zero links join the pair") | **supports** it — and supplies the mechanism (unresolvability at spawn, not a refusal) |
| `same_sink_loop_comb_resonator` | g7f-style legs (none in the arm); the both-fallback pair | see row 1 |
| `orphan_consumer_survives_unlinked` (shape 2) | §11's r78-side defect note (`coverage_blocked` vs green) | the same "no failure recorded because nothing was checked" pattern: an orphan consumer is not a failure in any counter, only in the graph |

---

## 6. Contamination ledger

* **This seat never fed tone into the shared default sink (SPDIF) and never
  wrote global metadata.** Tone entered only `r79b_<pid>_ns_*`,
  `r79bo_*_ns_*`, `r79bs_*_ns*` null sinks. The legs whose destinations can be
  the shared sink (g1b–g1e, g5g, g7a–g7e, selfsink B/C) were fed nothing or
  digital silence and are topology verdicts.
* **Legs that read the shared sink monitor** (no writes): g1c/g1e (capture ←
  SPDIF monitor), g7a/g7c (same fallback). No content witness was taken on
  them; their verdicts are link inventories. Reading the SPDIF monitor adds a
  consumer to the shared sink for ≤14 s per leg.
* **The two legs that *drive* the shared sink as a loop** — g1e (both-fallback
  pair) and g5g (both numeric targets fall back) — lived 8 s and 14 s
  respectively, fed nothing, and were killed by their bounds. If a sibling had
  been playing tone into SPDIF in those windows, the loop would have copied it
  back into the sink (and, per `same_sink_loop_comb_resonator`, could have
  amplified it to the s16 rail for the duration). The read-only contention
  witness at 08:20:44Z shows the SPDIF monitor **all-zero** with **0 links**
  touching SPDIF and 11 sibling processes live; sibling arm runs
  (`--probe-capture-r79` under `pidpin`, r79-verify forge runs) were active in
  the same window, and foreign `r79lb_*` nodes/sinks (some left loaded) are
  named in every group's `host_start`/`host_end`.
* **No sibling object was touched**: teardown is by recorded module id and
  by own PID tag only; `final_check` is empty in all group runs. Probe-owned
  module ids were never scraped from `pw-cli` replies (the scout's §10.1
  hazard).
* **Diagnostics' footprint**: one probe-owned null sink was suspended/resumed
  for the suspend receipt; it was unloaded and verified gone (0 sinks, 0
  modules, 0 nodes). No default-sink/source metadata was written.

## 7. Confidence, limits, remaining unknowns

**High** (two or more runs, or content + topology witnesses): E1 lattice and
the both-fallback loop structure; E2 kill teardown and orphan shape; E3 cycle
+ bounded recirculation + control; E4 inert set-param (five writes); E5 serial
rule (two tools, six legs); E6 null-sink suspend no-op; E7 self-name
unresolvability (7 forms) and the same-sink resonator (two independent legs,
burst and continuous).

**Medium**: `freeze_outcome_is_reconfiguration_dependent` — 20 retained legs
split 14/6 by the source-reconfiguration sequence, with the mechanism
unresolved (the split is *acausal on its face*, so a hidden state such as
driver ownership is the leading candidate). The
`both_sides_fallback_pair` *content* consequence is an inference (structure
measured, amplification measured only on a probe sink).

**Not claimed**: any perceived-quality claim; anything about real ALSA sinks
(suspend, latency, or the shared devices) — only null sinks and the SPDIF
*monitor* were observed; the internal (float32) amplitude of a loop; the
exact pw-record startup offset; whether `pw-cli set-param` writes reach the
node's Props param at all; any claim that these classes hold on another
PipeWire/WirePlumber version or another session manager.

**Remaining unknowns**: (1) what moves data through a stopped loopback client
(server-side buffer forwarding vs a client-node whose process callback is not
needed for this pair) — needs source, `strace`/`perf`, or a different host;
(2) why the two-swap freeze legs are silent (0/6) while every single-swap leg
is live (14/14) — the split is reproducible but acausal on its face; driver
ownership is the leading candidate, creation order and swap timing are ruled
out; (3) whether the numeric-target misresolution can be triggered (needs a
serial/id collision); (4) the suspend behaviour of a real ALSA target;
(5) whether the orphan consumer's two shapes correlate with anything (frame
count, tap linkage) — 2 stalled / 1 completed, not enough reps; (6) whether
the marker's ~1.3–2 s life is a property of the frozen path or of the new
source's prefill.
