# r83 CRITIC — adversarial review of the landed pwcat/pw-record family (`a151a226`)

Host `plazir27`, 2026-10-15 22:11–22:21Z (−03 19:11–19:21). Seat: **CRITIC
(wave-B gate, leaf)**. Scope: the r83 landing `git archive a151a226` →
`/tmp/r83critic-src` (fixture md5 `1fd0a2496b8fb2c4f65b58b33fe044f1` =
committed blob; +2 426/−3, 7 entries / 128 legs), against
`reports/round-83/r83-{scout,boundary,author}.md` and the two committed
receipts. Toolchain: PipeWire **1.6.8**, pactl **17.0-98-gb096**, Python
**3.14.7** (numpy 2.5.3), kernel **7.2.3-arch1-3**, 32 cores.

**Probe environment.** Ambient load only: loadavg **75.98** at the replay
start, **81.6** mid-replay, **122–124 / 32 cores** during the probes (sibling
seats, incl. a foreign `r83a_4030452` family run live in `pw-dump` the whole
probe window). No hogs of mine. **Zero tracked writes, no commits, no
`set-default-*`, no foreign object touched.** Seat namespace `r83c_*`; every
object loaded by me was unloaded and verified (below). The working tree was
**dirty and moving** during the window (HEAD `a151a226` → `bc3f55ca` →
`2b221233`; a sibling fold rewrote `measure_audio.py` at 19:16:13) — every
number below is against the pinned export, never the worktree.

**Evidence.** `corpus/live/r83-critic/` (MANIFEST.md + SHA256SUMS + 14
artifacts) and one read-only depth-2 labrat receipt audit (folded as §8).

## Verdict

**ADMIT-with-findings.** The family reproduces cleanly on the pinned commit:
my own full replay under load returned `{"failures": {}}`, **128 legs /
7 entries**, all 14 name-verified unloads `rc=0 recycled=false`,
`sinks_gone` all-true, `own_nodes_after []` — a **third green run** on the
committed revision, and the labrat independently re-derived both committed
receipts as internally consistent with every reachable pin substantiated.
**But three latent defects are live and were each reproduced
empirically**: (F1) two entry-3 pins can read green while unmeasured —
proven with the committed entry function; (F2) the inherited
"name-verified" unload index is a **substring** predicate and destroyed the
wrong module in my probe (this contradicts the r83 reviewer's F6 "sinks
unaffected"); (F3) every leg spawns with `env=None`, and ambient
`PIPEWIRE_LATENCY`/`PIPEWIRE_NODE`/`PIPEWIRE_PROPS` override the very flags
the family pins — including the `-P ''` fail-open's "session default"
referent. None of the three fired in the committed runs; F2 is the only one
that can damage a foreign object.

## 1. Independent replay on the pinned tree (green, third run)

| field | value |
| --- | --- |
| command | `python3 corpus/fixtures/measure_audio.py --probe-pwcat-r83` (exported tree) |
| window | 22:11:54Z → 22:17:00Z (≈5 min), loadavg 76–82 / 32 cores |
| result | `{"receipt": "…/20261015T221700821010Z-pwcat-r83/measurements.json", "failures": {}}` |
| r83 legs | 29/19/26/13/18/15/8 = **128**, every `failures` `[]` |
| teardown | 14/14 `unloads` rc=0 `recycled=false`; `sinks_gone` all true; `own_nodes_after []`; `generic_capture_props_nodes_after []` |
| folded corrections reproduced | rc=255 ×8 + rc=1 ×5 classes; SIGSEGV **18/18 rc=-11** vs live control (-9); `-l -5`→`4294967056/48000`; d10 deltas `[0.9983,0.9983,1.0381]`, d025 transports `[0.3956,0.3976]`, `l1000` `[0.1032,0.1439]`; matrix `c1_audio_legs 3`, `m_alone [stable_mono]×3`; resample `s4_peaks` ×3 `full_wave_abs_octave`, `s1_disable` ×3 `all_zero`; `n_empty failopen_foreign_sink` |

Receipt sha256 `60a235c6…` (`corpus/live/r83-critic/replay-run1.measurements.json`).
The two committed receipts were audited independently by the labrat (§8):
**CONFIRMED** — 128 legs each, all 52 `failures` arrays empty, every
reachable pin present and in-envelope, all unmeasured arms disclosed
(`c1_mono_1 silent_or_thin`, `m_alone_1 unmeasured`).

## 2. Findings, ranked

### F1 — entry 3's `-d 0.25` and `-l 1000` pins can be green while unmeasured (false-green path, live-proven)

The ctl arm requires ≥2 measured legs (`:17687`) and the d10 arm requires
≥2 **and** a `linked` gate per rep (`:17704`, `:17741`), but the d025 and
l1000 arms have **no minimum-count gate** — they filter `None` transports
and iterate whatever remains (`:17719-17730`, `:17731-17740`). The real
`_pwcat_r83_onset_leg` returns exactly that `None` shape whenever the
loopback never links: `cell["blocked"] = "loopback never linked both
sides"; return cell` with no `transport_s` (`:17138-17143`). So two
load-sensitive arms of the round's headline `-d`-delay/`-l`-prop-only pin
can vanish silently while the entry reads green.

**Proof (probe A).** Called the committed `pwcat_latency_props_r83_entry()`
with `_pwcat_r83_onset_leg` monkeypatched to return that exact blocked
cell for the four d025/l1000 reps (ctl/d10 ran for real):

```
"failures": [],
"onset_summary": {"ctl_transports": [0.1214,0.1218,0.1671], "ctl_median_s": 0.1218,
                  "d10_deltas_vs_ctl": [0.9795,1.0261,0.9823],
                  "d025_transports": [], "l1000_transports": []},
"blocked_flags": {"onset_d025_0": "loopback never linked both sides", … ×4}
```

Green with both pins unmeasured. **Fix shape:** mirror the d10 gate —
require ≥1 (ideally 2) measured reps and/or append a failure when a rep
carries `blocked`. (`corpus/live/r83-critic/probeA-onset-hole.json`.)

### F2 — the "name-verified" unload index is a substring predicate, and it fired on the wrong module (live-proven; inherited; contradicts reviewer F6)

`_pwcat_r83_unload_own` (`:16548`) routes through
`_gst_r81_unload_own` → `_gst_r81_sink_module_index`, whose ownership
proof is `f"sink_name={sink_name}" in ln` (`:12802-12818`) — a substring
containment, not a field equality. The r82 critic proved this predicate
can select a foreign module; r83 inherits it unchanged and the reviewer's
F6 asserts "sink unloads are unaffected … against the exact `sink_name=`".
**That assertion is false**, and I re-proved the defect live on the
committed helper:

| run | modules listed (index order) | helper(`r83c_a`) | fired | outcome |
| --- | --- | --- | --- | --- |
| 1 | `536870921 r83c_a2`, `536870926 r83c_a` | **536870921** | `_pwcat_r83_unload_own(536870926, "r83c_a")` | **`r83c_a2` destroyed**, `exit_code 0`, `recycled: true` |
| 2 | `536870924 r83c_a`, `536870929 r83c_a2` | 536870924 | same call | correct module (order-dependent) |

Run 1 is the destructive case: the nested module was listed first (its
index came from LIFO recycling — the exact hazard the helper exists for)
and was silently unloaded while our own module stayed. **r83 exposure:**
`PWCAT_R83_NS_*` are `r83a_ns_*_<pid>`; any concurrent r83-family run
whose pid is a decimal **prefix** of ours (e.g. `…_351263` ⊂
`…_3512630`, or any foreign module whose args extend our name) can be
selected and destroyed by our loss legs or teardown. The self-inflicted
half is caught by `sinks_gone` (our sink still listed → red), but the
foreign module's destruction is silent. The `recycled` flag records the
drift and nothing gates it. **Fix shape:** anchor the match (equality on
the `sink_name=` field, or require tab/whitespace/end after it) — one
shared-helper patch fixes r81/r82/r83 at once.
(`probeB-unload-substring-run{1,2}.json`.)

### F3 — every leg inherits the ambient environment; `PIPEWIRE_*` overrides the flags the family pins (live-proven)

All six leg runners (`_pwcat_r83_shot/-lb_leg/-play_leg/-rec_leg/-feed/
-onset_leg`) spawn with `env=None`, so the operator's/session's whole
environment reaches the clients. libpipewire honours `PIPEWIRE_PROPS`,
`PIPEWIRE_NODE`, `PIPEWIRE_LATENCY`, … and my probes show each one
overriding an r83-pinned behaviour:

| ambient env | r83 leg shape | measured | pin affected |
| --- | --- | --- | --- |
| `PIPEWIRE_LATENCY=1024/48000` | `pw-loopback … -l 5` | `node.latency` = **`1024/48000`** (control `240/48000`) | entry 3's 10 latency pins **and** the 5 "prop absent" drop pins (an env latency materializes the prop → false reds) |
| `PIPEWIRE_NODE=r83c_e2` | `pw-loopback -C r83c_e1 … -P ''` | `input_producers=[r83c_e2]`, `out_consumers=[r83c_e2]` while `pactl get-default-sink` still reads SPDIF | entry 7's fail-open **"session default" referent** — the route-shape gate still passes, `failopen_target_is_default` silently reads False |
| `PIPEWIRE_PROPS='{ node.name=r83c_envname }'` | `pw-cat -p --target …` (no `-P node.name=`) | node published as **`r83c_envname`** | ambient props can be injected into any leg that doesn't override them |
| `PULSE_SINK=r83c_e2` | `pw-cat -p --target ''` | **no effect** (SPDIF consumer) | attacked, survived — the r82-F5 class does **not** transfer to native clients |

No current receipt is affected (my shell has no ambient audio env, and
three green runs prove the clean baseline), so this is an environmental
fragility rather than a wrong pin today; the entry-7 half is the silent
one. **Fix shape:** spawn legs with an explicit scrubbed `env`
(`PIPEWIRE_*`, `PULSE_*`) — the pattern already exists in the r82
`f0`/`f1` ffplay legs. (`probeC-env-hermeticity.json`,
`probeD-failopen-env.json`.)

### F4 — entry 6's headline `|x|`-artifact pins are conditional on `med_clean`

`if med_clean is not None:` (`:18425`) wraps the whole `s4_peaks` /
`s4b_matched` / `s4c_downsample` verdict block. `med_clean` is built only
from `ch_amp(s0_ctl, 0, fl)` (`:18378-18394`); the s0 legs are gated on
`carries_tone` (which would fail a silent control), but a control whose
tap windows parse while `_pwcat_r83_channel_stats` returns
`unsupported`/no channels would leave `clean == []` → **no failure and no
artifact pin** — the round's sharpest new class silently unmeasured.
(Contrast the remix entry, which does fail on `med is None`, `:18175`.)
**Fix shape:** append the failure when `med_clean is None`; keep the
skip only for the s4 sub-checks that genuinely need a reference.

### F5 — the `-n ''` pin can be unmeasured while green (`nodes_not_seen` recorded, not failed)

`:18654-18659`: if either literal node is absent from the sample, the leg
sets `outcome = "nodes_not_seen"` and appends a named outcome — **no
failure**. The `-n ''` fail-open pin is then unmeasured while the entry
reads green. (Distinct from reviewer F3, which is about pid attribution
of the same leg; both stand — this one is the unmeasured path.)
**Fix shape:** fail or `coverage_blocked` when the nodes are not seen.

### F6 — `dm_move`'s skipped path passes without exercising the claim

`:18259-18262`: when `_module_r80_sink_input` cannot resolve the stream,
`move_skipped` is set and **no failure is appended** — only the tone check
remains. The `node.dont-move` → "move-sink-input is a silent rc=0 no-op"
pin is then unmeasured. Both committed runs (and my replay) realized the
move (`move_rc 0`, consumers unchanged), so the hole is latent; the
recorded skip is honest but un-gated. **Fix shape:** treat `move_skipped`
as a failure (or name it `coverage_blocked`).

### F7 — `pc_drop` never asserts that the malformed value actually dropped

The pw-loopback silent-drop legs assert defaults + absent `bogus.prop`
(`:17388-17408`); the pw-cat counterpart `pc_drop` (`:17423-17435`) only
asserts "ran to bound", "no `syntax error`", "node published". A pw-cat
build that *partially* parsed `}{ garbage` (e.g. landed a bogus prop)
would pass. Also the "no syntax error" test reads only the normalized
**last** stderr line (`_consumer_tail` `:1015-1026`) — the same nit as
reviewer F7; harmless today because the leg's `stderr_tail` is empty.
**Fix shape:** assert the node carries the default prop set / no
`bogus.prop`, and read the full stderr for the phrase.

### F8 — citation/label defects in the author report (already reported; independently re-confirmed by the labrat)

The reviewer (`52c5d807`, F1/F5) and the scribe (`2b221233`, ADJ-1/ADJ-2)
already landed: the report's run1 stamp `21:50:17Z` names a **red,
uncommitted** run (committed run1 = `22:01:05Z`), §5 quotes run2's
transports under mixed delta/transport labels, "+ ~2,240 lines" vs the
actual +2 426/−3, and "No commits; everything working-tree-only" (L111)
contradicts the committed receipts it cites. My labrat reached the same
labeling/attribution nits independently from the JSON alone (it could not
verify the stamps — neither receipt carries a timestamp). No new critic
action; listed here so the wave's finding set is complete.

## 3. What survived the attack (worth saying)

- **The content witness is authenticated now.** Taps use the r78
  **pid-keyed** pair (`997 + 211·(pid%4)`, `+503`) with 6 % tolerance and
  a 3000-amp floor, and every tap targets a probe-owned sink — the r82-F3
  constant-collision class is gone; forging `carries_tone` would require a
  foreign stream playing our exact pid-class pair **into our pid-unique
  sink**.
- **Fail-closed where it matters:** entry 7 *fails* on unreadable
  `object.serial` instead of silently dropping the serial legs (r82-F8 not
  repeated); refusal legs gate rc **and** class **and** stderr fragment
  **and** zero nodes; the SIGSEGV family gates rc **and** signal **and**
  zero nodes against a live control that runs to bound; `killed_at_bound`
  is a separate class from a crash.
- **Teardown discipline:** every unload re-reads the module table and
  records `verified_index`/`captured`/`recycled`; `sinks_gone` +
  `own_nodes_after` are gated; the `-n ''` literal names are recorded
  separately rather than claimed. (The predicate's strength is F2; the
  discipline is real.)
- **Tone routing is fail-closed:** `_pwcat_r83_feed` raises on a
  non-probe-owned sink (`:16852`); the fail-open legs carry no feed and
  say so in `content_witness`.
- **Boundary corrections are genuinely encoded and reproduce** (see §1),
  including the reclassified `peaks_abs_octave_artifact` with
  fundamental-destroyed/octave-dominant gates that the *boundary* would
  have caught had the author shipped the original shape.
- **Receipts are honest:** every unmeasured arm is a named outcome
  (`c1_mono_1`, `m_alone_1`), the zero-fraction spread (8.3 % boundary vs
  14.6 % this run) is disclosed, and the stale-default episode
  (`r93b_in`) is receipted rather than papered over.

## 4. Probe summary (all under ambient load; `r83c_*` namespace)

| probe | result |
| --- | --- |
| Full `--probe-pwcat-r83` replay, pinned export | **green**, `failures: {}`, 128 legs, ~5 min @ loadavg 76–82 |
| Committed entry-3 function + blocked d025/l1000 reps | **green** with `d025_transports: []`, `l1000_transports: []` — F1 |
| `_gst_r81_sink_module_index("r83c_a")` with nested `r83c_a2` loaded | run 1: returned the **a2** index, `_pwcat_r83_unload_own` **destroyed `r83c_a2`** (rc=0, `recycled: true`); run 2: order-dependent correct pick — F2 |
| `PIPEWIRE_LATENCY=1024/48000` + `-l 5` | `node.latency` = `1024/48000` (not `240/48000`) — F3 |
| `PIPEWIRE_NODE` + `-P ''` fail-open | consumers = env node, `pactl` default unchanged — F3 |
| `PIPEWIRE_PROPS` + `pw-cat` | node named by the env props — F3 |
| `PULSE_SINK` + `pw-cat --target ''` | no effect (native clients) — survived |
| Module/sink/process residue | zero `r83c_*`/`3512630` objects; defaults unchanged (SPDIF / Line) |

## 5. Contention ledger (by name; never touched)

- **`r83a_4030452` family run (audio-shokunin sibling wave-B seat)** — live
  modules `r83a_ns_a_4030452` / `r83a_ns_b_4030452` and in-flight
  `pw-loopback -n r83a_4030452_l2_5` / `…_lneg5` legs observed in
  `pw-dump`/`ps` throughout the probe window (my replay ran 22:11–22:17Z;
  its legs appeared from ~22:12Z). Never touched; it is also the live
  instance of the F2 prefix-nesting exposure (pids `3512630` vs
  `4030452` did **not** nest, so no collision occurred).
- Sibling fold rewriting `corpus/fixtures/measure_audio.py` (worktree,
  19:16:13) and the wave-B commits `bc3f55ca`/`52c5d807`/`2b221233`
  landing mid-window — hence the commit pin.
- Ambient CPU load 76→124 / 32 cores from sibling seats; no hogs of mine.
- Default sink/source unchanged across the window
  (`…SPDIF__sink.29` / `…Line__source.29`).
- Interference caused by me: none on shared sinks — every tone leg was
  bound to `r83c_*` sinks; my four probes loaded only `r83c_*` modules
  (all unloaded by index and verified gone). The pre-existing tracked
  `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc` modification
  predates this seat.

## 6. Receipts index (sha256, `corpus/live/r83-critic/`)

| artifact | sha256 (prefix) |
| --- | --- |
| `replay-run1.measurements.json` (the green 128-leg replay) | `60a235c6b916c824…` |
| `replay-run1.stdout.json` / `replay-run1.stderr.txt` | `4c8248fd6304cd9c…` / `e3b0c442…` (empty) |
| `probeA-onset-hole.json` | `102dd07405f6a518…` |
| `probeB-unload-substring-run1.json` / `…-run2.json` | `37a151874c139ac8…` / `bddb848763d253d3…` |
| `probeC-env-hermeticity.json` / `probeD-failopen-env.json` | `5e155cd829953a69…` / `723254a5dc1d7e51…` |
| `probe_onset_hole.py` / `probe_unload_substring.py` / `probe_env_hermeticity.py` / `probe_failopen_env.py` | `e04d648a7efc7f05…` / `d5abf36b8d7dc1cb…` / `f2613d45f4144fc0…` / `261fdada589c71d2…` |
| `receipt-audit.txt` (3-way leg/failure/pin audit) | `fe01ac83295f7c58…` |
| `labrat-receipt-audit.md` | `5fef38c038c59c16…` |
| `SHA256SUMS` / `MANIFEST.md` | full list / provenance |

## 7. Remaining risks / blockers

- **F1** is the one defect I would want closed before this family is
  called load-bearing: the `-d`-delay and `-l`-prop-only arms are exactly
  the load-sensitive cells, and their failure mode is a silent
  unmeasured-but-green entry. One-gate fix.
- **F2** is inherited from `_gst_r81_*` and affects r81/r82/r83 alike; a
  shared-helper anchor is the right patch. It is also the only finding
  that can damage a foreign object (silently).
- **F3** is family-wide (the r82 legs share the `env=None` pattern);
  scrubbing the audio env is a one-line runner change.
- **F4–F7** are latent coverage gaps with recorded-but-ungated fields; no
  committed receipt is affected.
- **F8** is already adjudicated by the reviewer/scribe seats.
- Nothing blocks the ledger standing. No seat-blocking defect found; no
  shipping decision is made here (canonical judge's call).

Report ends. No tracked edits, no commits, no pushes; `r83c_*` objects
fully torn down and verified.
