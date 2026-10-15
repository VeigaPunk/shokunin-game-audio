# R78 VERIFIER (audio) — receipt-level verdict on `d9aa6f9`

Seat: **VERIFIER (leaf)**. Repo `~/Projects/shokunin/audio-shokunin`.
Commit under test: **`d9aa6f9`** ("r78 work: playback-direction lattice —
8 entries, 60+ legs"). Canonical receipt:
`corpus/live/runs/20261014T221945369366Z-capture-r78/measurements.json`,
sha256 **`45135e3fd524c7c22fa5e3327ec4945c6456f3ff6bf0d2c8666b3226ee45befe`**,
`mode: probe-capture-r78`, 25 rows (17 ordinary + 8 r78 probes), 70
recorded legs + 1 warmup.

**Read-only on tracked files held**: every check ran in `/tmp/r78_verifier/`;
`git status --porcelain` shows zero modified tracked files; worktree
`corpus/fixtures/measure_audio.py` sha256 `af28eade…` == `HEAD:` blob (the
committed arm). No probe was re-run on the live host — the brief is
receipt-level and the host carried concurrent lanes (the receipt's own
`contention` leaf: `aplay: 1`, `host_is_quiet: false`).

## Method

1. **Cell re-derivation**: every r78 cell's fields re-read from the raw
   receipt and compared against `r78-author.md` tables leaf-for-leaf.
2. **Prior-row stability**: leaf-level flatten + set-compare of the 17
   shared ordinary rows vs the r77 folded receipt
   (`…T210316456683Z-capture-r77`) and the newest r76 receipt
   (`…T202511898134Z-capture-r76`).
3. **Fail-closed gates**: each probe's contiguous gate block was extracted
   **line-exact** from the fixture (sed ranges below) and `exec`'d against
   locals reconstructed from the receipt; host-touching calls
   (`_capture_r77_sink_names`) stubbed to the receipt's own post-state.
   The aplay probe's gates are interleaved with measurement — those were
   replicated clause-for-clause by hand. Then **60 targeted mutations**:
   one leaf flipped per run, verbatim gate re-evaluated, the named failure
   required to fire.

   | probe | gate lines (measure_audio.py @ d9aa6f9) |
   |---|---|
   | lattice | 6677–6800 |
   | follow | 6956–7038 |
   | loss | 7155–7236 |
   | props | 7350–7390 |
   | segv | 7448–7479 |
   | zeros | 7936–8011 |
   | parec | 8210–8273 |

## §0 Bottom line

**AGREE with every claim.** The canonical receipt's `failures: []` on all
25 rows re-derives; all 7 verbatim gate blocks evaluate to **0 failures**
on the receipt; 59/60 single-leaf mutations trip their named clause (the
60th needs a two-layer corruption — the gate recomputes from raw evidence,
§F5); prior rows are byte-identical; the SIGSEGV partition is identical
across all four r78 receipts; the relink/unlinked classes are independently
evidenced in topology *and* content leaves.

---

## 1. Commit shape and wiring — AGREE

- `git show --numstat d9aa6f9`: `2401 / 3` on
  `corpus/fixtures/measure_audio.py` + regenerated
  `__pycache__/measure_audio.cpython-314.pyc` + `r78-author.md` — matches
  the report's "+2401 / −3" exactly.
- Exactly **3 deleted lines**: the one-mode exclusivity `sum([…])`
  (appends `args.probe_capture_r78`), the `mode` ternary and the `suffix`
  ternary (each prepends the r78 clause). Every prior flag's value is
  order-preserved (r78 arm evaluated first only on its own flag).
- `if args.probe_capture_r78:` block wires all 8 entries (lines
  8696–8717); the flag is inside the exclusivity sum (line 8404).
- **r77 sibling preserved**: `_capture_r77_node_props` (fold-2's
  client-id→PID fix) is byte-identical bdf748e→HEAD (diff of lines
  4394–4450 both sides: empty). All r78 hunks are ≥5903.

## 2. The `failures: {}` claim — AGREE

All 25 measurement rows carry `failures: []` on the canonical receipt.
The three earlier committed r78 receipts show the iteration trail
(14 → 7 → 3 → 0 failures): the pin-only nofollow law, the single-consumer
`.monitor` expectation, the missing-fmt wav legs (pipe seekability), and
the implied-rate bucketing all failed **before** the classes were
corrected — the named classes are measured outcomes, not post-hoc
accommodation.

## 3. Prior-row stability — AGREE (stronger than claimed)

Leaf-flattened compare of the 17 shared ordinary rows:

| pair | leaf diffs | leaves only-L | leaves only-R |
|---|---|---|---|
| r78 receipt vs r77 folded `…T210316456683Z` | **0** | 0 | 0 |
| r78 receipt vs r76 `…T202511898134Z` | **0** | 0 | 0 |

Top-level keys `thresholds`, `distinctness`, `ui/impact/movement/ambience_
family_comparisons`, `sections` are likewise byte-equal to **both**
priors; only `mode` differs (`probe-capture-r78` vs `probe-capture-r77`/
`r76`). The 221 leaves in these rows are deterministic fixture
measurements — they carry no host-dependent leaves, so no environmental
or contention class needed invoking. (The r78-baseline seat's broader
environmental-set enumeration — env 66 / contention 58 / drift 24 / 0
unclassified on the row-03 `capture-r76` replay — is corroborating
context, not needed here.)

## 4. Fail-closed gate verification — AGREE

All 7 verbatim gate blocks + the hand-replicated aplay gates evaluate to
**0 failures** on the canonical receipt. Mutation results:

- **59/60 single-leaf mutations fired the expected clause** (consumers
  emptied/wrong, rc flips, tone witnesses stripped, stall legs released,
  unfrozen size traces, wrong implied rates, honest headers, surviving
  teardown sinks, foreign monitor consumers, dirty metadata, third-node
  eaters, missing fmt chunks, symmetric envelopes, …).
- **The one miss is stronger, not weaker** (§F5): clearing the stored
  `target_object_lies` leaf does nothing — the gate **recomputes** it
  from `samples[].node.target_object` + `target_arg`. Defeating the
  provenance-trap assert required clearing the leaf *and* corrupting the
  underlying evidence; then it fired the exact string
  `lattice: no fallback leg advertised the requested target while
  consuming the default — the provenance trap did not reproduce`.

Teardown gates are also fail-closed: stubbing the post-run sink list to
contain a probe sink fires the `teardown: … survived the unload` clause
in all four families that carry one (lattice, loss, props via
`sinks_gone`, segv, zeros, parec).

## 5. Per-frontier cell re-derivation — all AGREE

### 5.1 Lattice (14 legs) — AGREE

10 fallback legs (`garbage, absent_sink, default_token, pulse_token,
at_default_sink, at_default_monitor, at_default_source, source_name,
empty_target, no_target`): each `exit_code=0`, `error_class=null`,
`consumers_union=[…SPDIF__sink]`, `carries_tone=true`, `wall_s=2.63`
(real-time on the 2.6 s tone). `target_object_advertised` = the request
on every fallback leg — 8 legs carry `target_object_lies=true` (the
provenance trap). `probe_sink`/`other_sink` honored (probe null sink /
hdmi). `target_0`: `killed_at_bound` (rc=−9), `consumers_union=[]`,
FL/FR ports published at all 3 samples, node `suspended`, 0 tap
mine-windows → `unlinked_stall`. `monitor_name` (the racy row): this run
landed `[SPDIF]` at all samples (`landed_peer=false`, within the allowed
`{default, source-peer}` set); the **earliest** committed receipt
(`…T214821`) shows the peer-only landing with the SPDIF tap carrying the
tag 2.1–3.1 s — the claimed mid-leg re-link is receipt-visible.

### 5.2 Live-default follow (5 legs) — AGREE

`switches.to_probe.applied.applied_in_s = 0.0` (pw-metadata is the
authoritative switch); `before/moved/restored` consumers =
`[SPDIF]/[r78_def_sink_844895]/[SPDIF]` each with tone; `pactl` verb
`exit_code=0`, `moved_at_s=null`, 11-poll trace 0.5–5.6 s all showing
`r78_def_sink_844895` on **both** metadata and pactl reads →
`pactl_stale_default=true` (`pactl_delayed_default=false` remains
admissible); `still_probe` inside the transitional set; `nofollow`
pre=`[def]`@1.0 → restore fired@1.6 exit 0 → post=`[SPDIF]`@2.6,4.0 →
`followed_move=true, pinned=false`; `metadata_final == metadata_initial`
(host not dirtied); `def_sink_gone=true`.

### 5.3 Target loss (2 legs) — AGREE, independently

- `unload_relink`: consumers `[r78_loss_sink]`@1.0 → `[SPDIF]`@3.0,5.0;
  `unload_module` fired@2.0 exit 0; rc=0 wall 6.03; SPDIF tap `mine`
  spans 2.5→6.4 (40 windows), zero `mine` before the loss →
  **`playback_relink_on_target_loss`**.
- `manual_unlink`: consumers `[r78_loss_sink]`@1.0 → `[]`@3.0,5.0; both
  `pw-link -d` edges exit 0; rc=0 wall 6.03; default tap **0** mine
  windows; self tap `mine` only ≤2.3 s (pre-unlink only) →
  **`unlinked_sustained_playout`**. A player reports success while
  emitting nothing — receipt-proven at the port level and the content
  level.

### 5.4 Props precedence (14 legs) — AGREE

`consumers_union == expected_nodes` on every non-stall leg:
`flag_a_prop_b→[B]`, `flag_b_prop_a→[A]`, `prop_only→[A]`,
`node_target→[A]`, `flag_garbage_prop_b→[B]`, `prop_garbage→[SPDIF]`,
`node_target_garbage→[SPDIF]`, `env_props_flag_a→[B]`,
`env_props_flag_garbage→[B]`, `role/capture/monitor decoration→[A]`.
Both stall legs (`autoconnect_false`, `class_source_stall`):
`killed_at_bound`, `consumers_union=[]`, FL/FR ports published. →
`-P target.object` beats `--target` both directions; `node.target`
routes identically; `PIPEWIRE_PROPS` is an independent second vector.

### 5.5 SIGSEGV partition (6 legs) — AGREE, deterministic across runs

All **four** committed r78 receipts carry the identical partition
`{segv_sink:−11, segv_audio:−11, segv_duplex:−11, segv_bogus:−11,
control_output:0, boundary_source:−9}`. Crash legs: `node.found=false`
at every sample (no node ever published), `stderr_tail=null`, wall
2.01–2.02 s. Boundary `Audio/Source`: node found `suspended`, 0
consumers at 3 samples, killed at bound — stall, not crash. Control
`Stream/Output/Audio`: running, consumed `[r78_prop_a_844895]`. →
`class_override_segv` with a named stall boundary; the crash is a
pw-play client death, not a server refusal.

### 5.6 aplay axis (17 legs) — AGREE

Subject `hw:0,0` (Speaker sink). Envelope: playback `channels [2,8]`
incl. `S32_LE` vs capture `channels=2` `{S16_LE,S24_3LE}` (params_cap
rc=1 — playback-only device). `busy_under_witness` rc=1
`alsa_busy` ("Device or resource busy"); `witness_lock_release_s=5.9`;
retention `{+1 s: alsa_busy, +7 s: rc=0}` → `alsa_lock_retention`.
`convert_float` rc=0 + `"format is changed to S16_LE"`; `arecord
_constrain` rc=1 `alsa_sample_format` listing exactly `S16_LE,S24_3LE`;
`arecord_honored` `-f cd` rc=0 → `aplay_converts_arecord_constrains`.
`refuse_bogus` rc=1 `aplay_bad_format` <1 s. `plugin_default`/
`plugin_pipewire` rc=0 with tap `carries_tone` on SPDIF (plugin routes
through PipeWire); `pulse` → `alsa_unknown_pcm`; `null` rc=0 wall 0.0
(unpaced); `hw_baseline` `new_nodes=[]` — the direct path bypasses the
graph.

### 5.7 Capture link loss (2 legs) — AGREE, direction split proven

- `consumer_unlink` (cut the capture's input): `size_trace` **frozen at
  311 340 B** across samples 2.1/2.6/3.4, resumes after re-link to
  `expected_bytes` 1 344 044, rc=1, `data_finalized`, unlink/relink rcs
  all 0; producer samples `[c]→[]→[c]`; 70 file windows, 69 carry the
  tone, **0 all-zero** → `unlinked_stall`.
- `producer_unlink` (cut the feed): file keeps growing
  401 452→880 684→final 960 044 = `expected_bytes`, rc=1; 50 windows:
  **33 all-zero starting at file offset 1.7 s** (16 pre-unlink tone
  windows prove the baseline) → `unlinked_sustained_zeros`.

### 5.8 parec `--fix-*` (10 legs) — AGREE

Byte-rate slopes and the snap buckets re-derive exactly: `rate_req`
76 600 B/s → 22050 (honored); `rate_fix` 195 756 → 48000 (source
adopted); `fmt_req`/`fmt_fix` 383 002 → 4 B/smp; `ch_req` 97 878 → 1 ch;
`ch_fix` 195 756 → 2 ch. WAV legs (`seekable: true` — the discovered
libsndfile seek constraint): `hdr_rate_fix` fmt.rate=**22050** vs
payload-implied **48000**; `hdr_fmt_fix` fmt.bits=**16** vs payload
**4 B**; `hdr_ch_fix` fmt.channels=**1** vs payload **2** — all three
`header_prefix_mismatch: true`; `hdr_rate_plain` `header_honest: true`.
`mismatches` table in the receipt reproduces the report's §8 verbatim.
`sink_gone=true`.

## 6. The three scout corrections — all AGREE

1. **`.monitor` racy, not fallback** — the scout's Q1 table put
   `.monitor` in the clean default-fallback set; the earliest committed
   r78 receipt falsified that hard-set (peer-only landing + SPDIF
   re-link visible on the tap), and the final gate accepts exactly
   `{default, source-peer}`.
2. **`pactl` stale class** — the scout flagged the no-op; the receipt
   carries the measured 11-poll trace and the named
   `pactl_stale_default` class (rc=0 while the routing authority does
   not move).
3. **Active *fallback* stream follows the move** — the scout's pin claim
   was measured on the no-op `pactl` verb (vacuous); the receipt's
   `nofollow` leg shows the metadata write re-linking the running
   stream within ~1 s. The gate admits pin-or-follow and records which —
   `followed_move=true` on this host; the boundary seat independently
   measured the same law ("a fallback-riding stream follows the
   default live").

## 7. Cross-seat corroboration — no contradictions

- **Boundary** (`r78-boundary.md`): extends the segv crash set, confirms
  `-P target.object=0` falls back where `--target 0` pins (flag-only pin
  law), confirms the fallback-follows-default move, and scopes the
  honored-vs-fallback asymmetry — all consistent with this arm's cells.
- **Baseline**: prior-row stability reproduced on the full 127-command
  battery (125/126 ROW-STABLE; the one moved row is the named
  environmental set, 0 unclassified).
- **Scribe**: pre-dates the landing (recorded the arm as open at read
  time); no conflict.

## 8. Findings (informational; none touches a verdict)

- **F1 — the `nofollow` tap is not an independent destination witness.**
  The def-sink monitor tap carried the tag continuously 0.5→5.5 s
  *across* the move while link topology shows the stream on SPDIF at
  2.6/4.0 — consistent with the capture tap itself following the default
  move (the same policy the playout stream obeyed), not with continued
  delivery to the def sink. The leaf is recorded but correctly **never
  read by the gate** — the pin is the consumer-port samples. One
  sentence of caveat in the ledger would forestall a future reader
  treating it as counter-evidence.
- **F2 — §3 table "event at ~1.5 s"**: the receipt's `fired.at_s` is
  **2.0** (constant `PLAYBACK_R78_LOSS_EVENT_S`). Cosmetic prose slip;
  the receipt is authoritative.
- **F3 — `.monitor` run numbering**: the report's "run 2 … re-linked
  mid-leg" is dev-run numbering; in the committed receipts the
  peer-landing run is the earliest (`…T214821`). The mechanism is
  receipt-visible there (§5.1). Cosmetic.
- **F4 — stale comment**: `measure_audio.py` ~line 7458 calls the crash
  class a "~1.5 s death"; measured wall is 2.01–2.02 s (the gate bound
  is `<4.0` — correct). Cosmetic.
- **F5 — `target_object_lies` is sticky-true at receipt level**: the
  gate recomputes it and only ever sets True; a forged stored True
  survives corrupted underlying evidence. In the live path the leaf is
  fresh-built each leg, so this is a replay-only curiosity — noted
  because the mutation run needed the two-layer defeat to fire.
- **F6 — commit scope**: the commit also carries the regenerated
  `__pycache__/*.pyc` (tracked cache, prior-round convention); the
  author's "exactly one file" is true of source.
- **F7 — "No commit" in the author report** was true at write time; the
  wave then committed the identical worktree diff as `d9aa6f9`
  (worktree blob == HEAD blob, sha `af28eade…`).

## 9. Artifacts

- This report: `reports/round-78/r78-verifier.md` (only tracked write).
- Scratch (outside repo): `/tmp/r78_verifier/` — `eval_gates.py`
  (verbatim gate evaluator + receipt-derived locals), `mutations.py`
  (60-mutation suite), `gate_{lattice,follow,loss,props,segv,zeros,
  parec}.py.raw` (sed-extracted gate blocks), `r77_nodeprops_{base,
  head}.py` (sibling-preservation diff inputs).
- Receipts audited:
  `corpus/live/runs/20261014T{214821510582Z,220520747866Z,221326175535Z,
  221945369366Z}-capture-r78/measurements.json` (4 r78 runs),
  `…T210316456683Z-capture-r77`, `…T202511898134Z-capture-r76` (stability
  priors).

**The canonical Rust runtime is the sole Pareto judge; this seat's
verdict is evidence, not a decision.**
