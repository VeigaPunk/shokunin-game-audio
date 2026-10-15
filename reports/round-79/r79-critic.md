# R79 CRITIC (audio) — the pw-loopback frontier: what the gates let through

Seat: **CRITIC** (audio-shokunin round 79). Lane
`~/Projects/shokunin/audio-shokunin`, HEAD
`a2616f732253ed90110ba16a223ec7d10224740c`, host `plazir27`, PipeWire 1.6.8,
Python 3.14.7. **No commit, no tracked-file edit** — this seat wrote only
`reports/round-79/r79-critic.md` and untracked forge artifacts under
`corpus/live/r79-critic/`.

Artifact under review (verified, not taken on trust):

```
sha256(corpus/fixtures/measure_audio.py) = 4ee754b3fa7dab6c7be7c60930fc8c14854acf7f5439c9b150bb40aba0805095
bytes = 672390                       == frozen-artifact.txt      ✓
sha256(receipt run B) = 658773646ec8381badd3c5427c95655f0d7fe3c99361b195988f498512f30285  ✓
sha256(receipt run C) = f4572530cbf0c7083920454a0601c6b2e67b93fc97d32a65d188658f90d47a37  ✓
66 r79 legs across 8 entries, every entry failures:[] in run B            ✓
```

**Independent reproduction (control).** Before forging anything I ran the
*frozen* `loopback_capture_lattice_r79_entry()` end-to-end from an
unmodified copy (`corpus/live/r79-critic/control-unmodified-entry.out`): it
reproduced run B's verdict surface cell-for-cell — `b01=[ns_a]`,
`b04=[…Mic__source]`, `b09=[…SPDIF__sink]`, the same five
`capture_default_source_unnegotiated` outcomes, `failures: []`,
`own_nodes_after: []`. Every forge below therefore starts from a harness
that agrees with the author's receipts.

**Axes this seat judged against** (named, per-round): `provenance` (does the
named cause follow from the leaves the receipt actually records),
`falsifiability` (can the arm go red when its claim is false),
`coverage` (is a claimed class measured by the run that claims it),
`contamination` (can a witness be satisfied by a foreign or bypassed
source), `replication`, `regression-safety`.

---

## C1 — `capture_default_source_unnegotiated` is armed by a session constant, so **any** unnegotiated watched node is excused with a false cause

**Counterexample (live, end-to-end).** The round's *headline* arm — `b01`
(`-C <probe sink> -i stream.capture.sink=true` → that sink's monitor, the
"honored" arm of the two-arm lattice) — is made to publish **unnegotiated**
instead of linking. The entry then returns `failures: []` and reports

```
capture b01_sink_prop: capture_default_source_unnegotiated — no session
default source at this leg (source_meta=None); the capture stream published
with zero ports and never linked
```

i.e. a broken sink-prop arm is re-labelled as an environment condition
about the *default source* — a class the sink-prop arm does not depend on
at all (it has an explicit, resolvable target).

Forge diff (the only change; 10 inserted lines at
`_loopback_r79_leg`, verified by `difflib` as a single hunk —
`corpus/live/r79-critic/forge1-measure_audio.py`, sha256
`cf6da78fad9fa18996228fe6e21ad4195b50725fede49eaa6b9d657d90f9df7b`):

```python
    cell["carries_tone"] = (cell.get("tap") or {}).get("carries_tone")
+   # ---- FORGE 1 (r79 critic): the sink-prop arm publishes unnegotiated.
+   if name == "b01_sink_prop":
+       for _s in run["samples"]:
+           _w = (_s.get("watch") or {}).get(f"input.{ltag}")
+           if _w is not None:
+               for _k in ("input_ports", "output_ports", "producers",
+                          "producer_ports", "consumers", "consumer_ports"):
+                   _w[_k] = []
+           (_s.get("nodes") or {}).get(f"input.{ltag}", {})["state"] = \
+               "suspended"
    return cell
```

Live result (`corpus/live/r79-critic/forge1.out`), real sinks, real spawns,
12 legs, teardown clean:

```
"failures": [], "coverage_blocked": null, "confound_observed": true,
"named_outcomes": ["capture b01_sink_prop: capture_default_source_unnegotiated …",
                   "capture b02 …", "capture b03 …", "capture b05 …", "capture b07 …"],
"b01": {"outcome": "capture_default_source_unnegotiated", "producers_union": [],
        "expected_producers": ["r79lb_ns_a_112759"],
        "tap_carries_tone": true, "killed_at_bound": true},
"own_nodes_after": []                                 → ENTRY_GREEN
```

Note the leg is *fully green*: no `coverage_blocked`, no failure, and the
content pin passes because the **playback** side is intact.

**Evidence.**
* Gate, `corpus/fixtures/measure_audio.py:9306-9310`:
  `if not union and _loopback_r79_unnegotiated(...) and (ora_at_leg.get("source_meta") is None or (dsource_probe is not None and not dsource_probe.get("available")))`
  — an **`or`**, and **in the formal pair** the first disjunct is a constant:
  **all 47 leg oracles in run B carry `source_meta: None`** (census over the
  receipt; the author measured why: WirePlumber has no
  `default.audio.source` key and drops a written one — `r79-author.md`
  §3.1). It is *not* a constant in general — run 3's oracles read
  `source_meta: "r86ctl_src"` (see C7) — which is exactly why a *cached*
  session-wide probe is the wrong instrument for this gate.
* The probe is passed **only** for `kind == "dsource"`
  (`measure_audio.py:10010-10014`), so for every other kind
  (`node`/`dsink`/`none`/all playback legs) the gate collapses to the
  constant.
* **F1c (live unit, real receipt leg):** with `dsource_probe={"available":
  True}` — a session that *does* have a default source — the class is
  **still** assigned, proving the second witness is never consulted
  (short-circuit). **F1d control:** with `source_meta` set on the leg's own
  oracle, the same leg correctly **fails** — so the gate is the oracle leaf,
  not the leg's arm.
* **F1b (live unit):** the same branch, reached from the *playback* side
  (`c01_sink` output node unnegotiated), emits a **capture-side** explanation
  ("… the capture stream published with zero ports") for a write-side node.
* Chronology (receipts): run2 `06:46Z` and run3 `07:04Z` record this exact
  measurement as **failures** (`capture b05_garbage: expected producers
  […Line__source], got []`); run4 `07:10Z` — after the branch was added in
  this same round (author's declared repair #4) — is green. The class is
  real and independently witnessed (§3.1), but inside the frozen artifact
  its trigger is a constant, so the *formal* pair cannot distinguish "the
  session has no default source" from "this arm's target did not resolve".

**Impacted axes:** `provenance` (named cause ≠ recorded cause),
`falsifiability` (the headline arm cannot fail), `coverage` (b01's class
goes unmeasured inside a green run).

**Smallest safe correction (fixable defect).** Make the branch leg-local:
(a) pass `dsource_probe` for **every** capture-side check, not only
`kind == "dsource"` (`10010-10014`, `9821-9828`); (b) replace the `or` at
`9307` with `and` so the class requires *both* a fresh probe verdict and the
leg's own arm to be the default-source arm; (c) read the probe **per leg**
(drop `LOOPBACK_R79_DSOURCE_CACHE`, `9511/9529-9530`, or key it by
timestamp) — a cached session-wide reading is the wrong instrument for an
authority the author himself measured flapping (`9300-9304`). One-line
fallback if the class must stay: refuse the named outcome unless
`side_key == "producers"`.

---

## C2 — the tap-provenance guard is a precedence bug, and the content pin is not injective

**Counterexample (live, one token).** A real leg is spawned through the
frozen `_loopback_r79_leg` with `feed_sink` pointed at the **tap's** sink
instead of the leg's capture source. The route under test is
`tone → ns_a → loopback → ns_b2`; the tap listens on `ns_b`, which the
loopback never feeds. Both legs come back **PASS** with *identical* content
witnesses (`corpus/live/r79-critic/forge_bypass.out`):

| | control (feed source) | forge (feed tap target) |
| --- | --- | --- |
| loopback consumers | `[ns_b2]` | `[ns_b2]` |
| links from loopback → tap target | `[ns_b2:playback_FL, …FR]` | **`[]`** |
| tap `bound_to_target` / producers | `true` / `[ns_b2]` | `true` / `[ns_b]` |
| tap `mine_windows` / peaks | `40` / 7980,8136 | **`40` / 7980,8136** |
| failures | `[]` | `[]` |

The frozen `_loopback_r79_guard_playback` (`9029-9046`) accepts it — it only
checks that the *loopback's* target is probe-owned, never that the feed
target is upstream of the tap — and nothing else in the arm notices. The
receipt cannot tell a working route from a bypassed one.

**Evidence.**
* `measure_audio.py:9376-9379` — operator precedence: the guard is
  `not (A or ((B & C) | D))` with `D = set(leg.get("input_producers_union"))`,
  so **the confound is unreachable for every leg whose capture side is
  linked** (i.e. all ten playback-lattice legs, whose `input_producers_union`
  is `[ns_a]` in run B, plus b01/b04/b08/b09/b12 and the hot-plug legs).
  **F2 (live unit, real receipt leg):** tap bound to
  `bound_producers=["some_foreign_node_r79"]` → **no confound, no failure**.
  **F2b:** the same forge with the capture union emptied → the confound
  fires, proving the `|` operand is what masks it. The author's §10 claim
  ("a tap that never bound is a named confound, never a pass") holds only
  when the leg's capture side is empty.
* The `bound_to_target` test is node-level (`producers == [target]`,
  `9089`), and the tap's producer for a sink monitor is always the *sink*
  (`_playback_r78_producers`, `6083-6093`) — so it names the tapped sink,
  never the client that played into it.

**Impacted axes:** `provenance`, `contamination`, `falsifiability` (the
`want_tone=True` content pin is satisfied by any client that plays the tag
tone into the tap target).

**Smallest safe correction (fixable defect).** (a) `9376-9379`:
`not (bound_to_target or (set(bound_producers) & (set(output_consumers_union) | set(input_producers_union))))`
— i.e. a tap is attributed only when its producer is one of the leg's own
peers; (b) refuse the tautology at spawn: in `_loopback_r79_leg`
(`9198-9212`), `if feed_sink is not None and tap_target is not None and feed_sink == tap_target: raise ValueError(...)`; (c) for `want_tone=True`,
require the tap's producer ports to be the *leg's* consumer ports (the
`consumer_ports` leaf already exists in every sample).

---

## C3 — the `foreign_tone` ceiling is an amplitude-gated excuse whose provenance sentence no leaf supports

**Counterexample (live, measured).** A probe null sink is fed a tag-shaped
tone on **this run's own pid-derived frequency pair** at three amplitudes; a
never-fed leg's `want_tone=False` contract ("our tag may never appear on
this path") is then evaluated by the real `_loopback_r79_check_tap`
(`corpus/live/r79-critic/forge_ceiling.out`):

| amp | tap peaks (L/R) | mine windows | verdict |
| --- | --- | --- | --- |
| 8192 (this arm's own nominal) | 8189 / 7725 | 16 | **FAILED** — "tag tone … contamination, not coverage" |
| 9000 | 8997 / 8487 | 16 | **EXCUSED** — `foreign_tone_on_shared_monitor`, `failures: []` |
| 12000 (≈ the 07:16Z event) | 11996 / 11316 | 16 | **EXCUSED** — same named outcome |

The forbidden-tone pin flips from red to green across a **9.9 % amplitude
step**, and the excuse is decided by `peak > PLAYBACK_R78_TONE_AMP * 1.05`
(`9401`) — our *nominal* constant, not a per-leg measurement of our own tone
(the arm's own tone reads 7725/8189 corrected on fed legs and 4094/4094 on
the mix legs, i.e. the constant is not the observed value). Any lane that
writes its tone 5 % louder than this repo's constant is excused on the very
legs whose contract is silence.

**Evidence.**
* `measure_audio.py:9400-9419`. The witness it writes
  (`foreign_tone_witness`) records `capture_producers` = **the leg's own
  capture route**, not the tone's producer; the excuse's sentence ("a
  concurrent lane's tone is forwarded here") is an inference from amplitude
  alone — the only origin evidence in the arm is
  `_playback_r78_tone_windows` (`6382-6432`), which is a frequency+amplitude
  test on the tap file and has no origin term at all. In my forge the tone
  was played by a known pw-cat tag (`r79cr_feed_139023_*`) and **no leaf in
  the arm can name it**.
* The branch has **never been exercised by the phenomenon it addresses**:
  the only observed foreign event (run A, `07:16Z`) predates the branch —
  that receipt's `b09` leg has `mine_windows: 11`, peaks 11997/8997,
  `bound_to_target: true`, **no `foreign_tone_witness` key**, and the failure
  is the pre-ceiling contamination message. Runs B/C had no recurrence, so
  the two green formal runs do not test the new path at all.
* Latent trap: `leg["fed"]` is only set by the capture/playback/pw-cat
  lattices; the shape, matrix and hot-plug entries never set it (verified in
  the receipt: `fed=None` on a1/cm1-4/e1-e3). A future `want_tone=False` on
  one of those fed legs would be read as "never fed" and its own tone would
  be named foreign.

**Impacted axes:** `falsifiability` (silence contract is amplitude-gated),
`provenance` (the named producer is unverifiable), `contamination`
(a shared-monitor leg can be green while carrying a tag tone).

**Smallest safe correction (fixable defect).** Keep the measurement, drop
the excuse: record `foreign_tone_witness` **and** keep the failure (the
receipt then shows both the fact and the peaks). If the excuse must stay,
gate it on origin, not gain — the arm tags every feed
(`<ltag>_feed`, `9049-9057`), so require the tapped tone's producer node to
be outside this run's own feed tags **and** require the peak to exceed the
peak measured on a fed sibling leg in the same entry (self-calibration, the
pattern the matrix entry already uses at `10380-10397`). Also set
`leg["fed"]` in the shape/matrix/hot-plug entries (the shape entry never
sets it at all, `9682-9723`; matrix `10322-10331`; hot-plug `10723-10772`).

---

## C4 — a probe-target leg that silently falls back to the default authority is excused as "the authority moved"

**Counterexample (live unit, real receipt leg).** `b01`'s capture side is
made to bind the **default sink monitor** instead of its probe sink (the
`-P`/`-C` silent-fallback shape the author measured on other legs). The
verdict is `failures: []`, `coverage_blocked: ["capture b01_sink_prop:
default_reasserted mid-leg"]`, and the confound reads

```
default re-asserted: expected r79lb_ns_a_3943556, authority now
['alsa_input…Line__source', 'alsa_output…SPDIF__sink'] — consumers track the live default
```

The authority never moved: the leg bound the wrong node. The tap still
passes (`want_tone=True`, playback side intact), so the leg is green while
the class it claims (`capture_sink_prop_monitor`) is unmeasured.

**Evidence.** `measure_audio.py:9325-9338`. `live_now` is built as
`{sink_meta or sink_pactl, source_meta or source_pactl}` — **sink and source
authorities are conflated into one set**, so a capture-side leg that binds
the *sink* while the arm expects the *source* (or vice versa) is inside the
excuse; and `want not in live_now` is what makes the excuse reachable for
probe-target legs (for the `dsource`/`dsink` kinds `want` is derived from
the same oracle, so those are correctly refused — **F3 is a killed
counterexample**: b02 binding the SPDIF monitor still fails, as it should).
Reachable live case for a *node* leg: any run where the sink prop is ignored
and the fallback answers (the b09/b12/e3/a6 legs show the fallback target is
real and is exactly `SPDIF`).

**Impacted axes:** `provenance` (false "re-asserted" cause), `coverage`
(the leg's class is unmeasured, only a confound is recorded).

**Smallest safe correction (fixable defect).** Split the authorities
(`live_sinks`, `live_sources`) and restrict the excuse to a genuine
same-authority re-assert (`want in live_now`); when the bound node is the
*other* authority, record a distinct class (`wrong_domain_binding`) and
**fail** — or at minimum emit `coverage_blocked` plus an explicit
`class_measured: false` leaf so the entry cannot read as two-arm coverage.

---

## C5 — union-only fingerprints: bimodal link history and one-port links pass

**Counterexamples (live unit, real receipt legs).**
* **F4 — bimodal history.** `b01`'s route is present at the first sample
  (`t=1.3 s`) and **gone at the last** (`t=2.7 s`). `_loopback_r79_union`
  (`9266-9269`) unions across samples, so `union == [ns_a]` and the leg
  passes: `failures: []`. The hot-plug entry proves this host *does* drop
  and re-acquire routes mid-leg (e1/e2/e3), so a flap inside a lattice leg
  is invisible — the lattices assert no per-sample route at all.
* **F5 — half a link.** With only `…:monitor_FL` as the producer port, the
  lattice's port pin (`10020-10037`) passes: it is
  `all(":monitor_" in p for p in pports)` — a substring test gated on
  `pports` being non-empty, not an inventory. (The forge keeps the real
  producer *node* name and reduces only the port list to one entry, which is
  all the pin inspects.) Only the SHAPE entry's `a1` leg pins exact port lists
  (`9752-9765`), and only for that one leg; the playback lattice has no port
  pin at all. A stream that negotiated one channel instead of two is a full
  pass everywhere else.

**Impacted axes:** `falsifiability`, `coverage`.

**Smallest safe correction (fixable defect).** Assert the route at every
sample in `_loopback_r79_check_side` (the hot-plug entry's per-sample
pattern, `10789-10802`), or at minimum require `union == [want]` at the
first *and* last sample; and add an exact expected-port-inventory argument to
`check_side` (default `(FL, FR)` per direction), reusing the `a1` check.

---

## C6 — the record entry's `d2a` class rests on an ambiguous error class

**Counterexample/evidence.** `measure_audio.py:10602-10617` assigns
`capture_default_source_unnegotiated` when
`not prods and error_class == "no_target_node" and (source_meta is None or
not dsrc.available)` — again an `or` whose first disjunct is the constant.
`no_target_node` is the *same* class this fleet measured for an explicit
unresolvable target (`exp-capture-ports-r79.json`: `pw-record --target
<garbage>` dies `no target node available`). For `d2a` the two candidate
causes — "the session has no default source" and "`input.<lb>` is not a
source" — are indistinguishable in the recorded leaves
(`stderr_tail: "remote error: … no target node available"`), and the receipt
asserts the former. The class is likely right (the probe independently
reproduces it) but the *leg* does not establish it.

**Impacted axes:** `provenance`.

**Smallest safe correction (fixable defect).** In the same leg window, run
the discriminator the arm already owns: a `pw-record --target <garbage>`
control and a plain `pw-record` with no `--target`; require both to fail
identically before naming the class, and read the probe fresh at the leg
(see C1c).

---

## C7 — the round's headline law has **no positive instance in either formal receipt**, although the author's own run-3 receipt measures it positively

**Counterexample to the round's coverage, not to its law.** In runs B and C
every `-C` default-source arm (`b02/b03/b05/b06/b07`, plus `a5` and `d2a`)
lands in the named outcome: **the "ungated default-source fallback" arm is
never positively observed in the formal pair.** The only positive instance
in the whole round is run 3 (`07:04Z`, a *different* artifact revision),
where a concurrent lane's null source was the live default and the fallback
linked:

```
run3 capture lattice: b02_sink_noprop  producers=['r86ctl_src'] exp=['r86ctl_src'] → PASS
                      b03_dotmonitor    producers=['r86ctl_src'] exp=['r86ctl_src'] → PASS
                      oracle: {"source_meta": "r86ctl_src", "source_pactl": "r86ctl_src"}
                      inventory.sources.default = "r86ctl_src"
```

So a **probe-owned null source can be made the session default** on this
host and the fallback then links to it. The author's diagnostic tried only a
*metadata write* to `default.audio.source` (`exp-default-source-r79.json`,
which WirePlumber drops) and never `pactl set-default-source`, nor a null
*source* (both diagnostics load `module-null-sink` only:
`exp_default_source.py:141`, `exp_capture_ports.py:148`).

**Impacted axes:** `coverage`, `replication` (the law is measured in a
non-formal, pre-fix revision only).

**Smallest safe correction (fixable defect, cheap).** Add one probe-owned
null **source** leg to the capture lattice: load
`module-null-source`/`module-null-sink`+monitor, `pactl set-default-source
<it>`, assert the oracle sees it, then run `b02`/`b03` and require
`union == [that source]` **as a pass** (and drop the named-outcome branch for
those two legs in that window). That converts the round's headline from
"measured absent" to "measured both ways" in the formal pair, and it
exercises C1's corrected gate.

---

## Tested and **killed** counterexamples (the gates do hold here)

| forge | result |
| --- | --- |
| **A** — loopback publishes only one node (drop `output.<n>`) | killed: `wait_nodes` records `ready:false`, the sample's watch leaf is empty, the output-side `check_side` fails (`expected consumers [ns_b], got []`), and the shape entry's both-nodes-published check (`9743-9746`) fails independently |
| **B** — `-P <probe sink>` silently falls back to the default sink on an honored arm (`c01`) | killed twice: `union == [SPDIF]` → `want=ns_b ∉ live_now` → failure (the excuse in C4 is reachable only for the *capture*-side probe legs), and the tap on `ns_b` carries no tone (`9385-9388`) |
| **B'** — `-P <sink2>` falls back to the *other probe sink* | killed: `[ns_b] ⊄ live_now` → failure, and the tap is silent |
| **F3** — a `dsource` leg binds the default **sink** monitor where the default **source** is expected | killed: `want` is derived from the same oracle and is in `live_now`, so the excuse cannot apply → failure |
| **F1d** — control for C1: same unnegotiated leg with `source_meta` set | killed: fails as it should, which is what makes C1 a *gate* defect rather than a design choice |

## Provenance / regression checks (all clean)

* Prepend-only confirmed at the AST level: 51 top-level names added, **all**
  r79-namespaced; **no** pre-existing top-level name removed or shadowed;
  only `main`'s line number moved. The three rewritten wiring lines
  (exclusivity sum, `mode`, `suffix`) keep every prior flag's value
  (`measure_audio.py:11656`, `12505`, `12525`).
* r78 arms that block: the author's §11 self-report is corroborated
  independently — `_playback_r78_wait_source` (`6197-6207`) requires
  `name in source_names and _playback_r78_output_ports(name)` with
  `name = "<sink>.monitor"`, while this host publishes the monitor ports on
  the *sink* node; the gate can never confirm. Un-blocking it would move a
  committed row, so "report, don't fix" is the right call.
* Declared cosmetic wart confirmed: `c04_source_name.target_requested` is
  the raw `@SRC@` in run B (`adv`/verdict use the substituted name).
* Dead code, cosmetic: `extra_tw` (`10170-10177`) is built and never used.
* `wait_nodes[…]["ready"]` is recorded but never asserted (`9120-9122`) —
  harmless today (a dead leg fails downstream), worth asserting as
  `coverage_blocked` if the readiness gate is meant to be load-bearing.

## Run conditions of this review, and two further notes

* **Contention.** Every forge ran while **two sibling lanes were executing the
  same `--probe-capture-r79` artifact** (`pgrep -af measure_audio`: pids
  127171, 139148) and three orphaned `r79lb_*` null-sink sets (pids 4041488,
  127171, 139148) were live on the host. My unmodified control still
  reproduced run B's lattice verdicts cell-for-cell under that contention,
  which is real evidence for the arm's pid-stamped naming discipline. All
  forge residue was cleaned (`r79cr_`: 0 nodes, 0 modules, 0 sinks, 0
  processes; every `teardown_sink_gone: true`, `own_nodes_after: []`).
* **Note (coverage, not a defect):** the `@SRC@` source for `b04/b08/c04` is
  picked from the *session inventory* (`real_sources`, `9892-9894`,
  `10105-10108`) and is **not probe-owned**. In run 3 it selected a foreign
  lane's transient null source (`inventory.sources.all_real` includes
  `r86ctl_src`, and `b02/b03` then bound it); in runs B/C it is the hardware
  `…Mic__source`. The receipt records the chosen name, so this is honest —
  but "the named source is honored" is a host-state claim, and the round's
  own `-C` fallback law is *provable* on that same object (see C7).
* **Note (host hygiene):** the three orphaned `r79lb_*` sink sets above are
  *not* this arm's and not this seat's; they show that a killed r79 probe
  leaves pid-stamped sinks behind. `_loopback_r79_own_nodes` (`9003-9011`)
  filters by `r79lb_<pid>` and is therefore correct — but a round-level
  "no `r79lb_` node survives" sweep cannot distinguish a sibling lane's
  leftovers from its own, so any such sweep must stay pid-scoped.

## Seat position

C1, C2, C4, C5, C6, C7 are **fixable defects with named minimal pins**; C3
is a fixable defect *plus* a tradeoff the canonical judge must weigh if the
author prefers to keep the excuse (a green run bought with a 5 % amplitude
margin is not the same object as a green run bought with provenance). None
of the eight entries is admitted or rejected here — that is the judge's
call. The strongest single counterexample is C1 + C2 together: **the
headline `-C` arm can go unmeasured (forge 1) and the content pin that is
supposed to catch it can be satisfied by a tone that never traversed the
loopback (forge 2), with the receipt showing identical witnesses in both
cases.**

Artifacts: `corpus/live/r79-critic/` — `forge_unit.py` + `.out` (F1–F5 live
units), `make_forge1.py` / `forge1-measure_audio.py` / `run_forge1.py` +
`forge1.out` (end-to-end), `control-unmodified-entry.out` (independent
reproduction), `forge_ceiling.py` + `.out`, `forge_bypass.py` + `.out`.
