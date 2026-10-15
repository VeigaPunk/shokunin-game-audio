# R80 CRITIC (audio) — the `pactl load-module` lattice + topology lifecycle: what survives attack

Seat: **CRITIC** (audio-shokunin round 80). Lane
`~/Projects/shokunin/audio-shokunin`, host `plazir27`, PipeWire 1.6.8,
pactl 17.0-98-gb096, WirePlumber 0.5.17, Python 3.14.7. **No commit, no
tracked-file edit** — this seat wrote only `reports/round-80/r80-critic.md`
and untracked artifacts under `corpus/live/r80-critic/`. Every `pactl
load-module` this seat ran was unloaded by its captured index; node census
before/after the battery: `[]`/`[]` (`r80c_*` prefix, transcript in
`controls-transcript.txt`).

Artifact under review (verified, not taken on trust):

```
sha256(corpus/fixtures/measure_audio.py) = 3b69541f684c0cf414084c6f7e4cb313facff050783dde95c335308850d046c4  ✓ matches report
git diff HEAD = +905/−3               ✓ prepend-only: one 894-line block + arg/sum/entry/mode/suffix wiring
receipt run1 (134301)  = 8a3a37a4…   ✓  receipt run2 (134359) = ba565dc7…  ✓ (receipt-shas.txt)
failures: {} both runs, exit 0, 10/10 legs
```

**Independent replay (control).** One full `--probe-module-r80` run on the
live host: exit 0, `failures: {}`, stderr 0 B, receipt
`corpus/live/runs/20261015T153859764877Z-module-r80/measurements.json`
(copy of the stdout line in `replay-stdout.json`). The 31-leg verdict
surface is **identical** to author run 2 (normalized diff: NONE — script
output archived). Post-run host census: zero `r80md_*`/`r80c_*` nodes, zero
r80 links. Teardown is honest on the green path.

**Axes this seat judged against** (named, per-round): `falsifiability`
(can each leg go red when its claim is false — stimulus presence,
readback), `mechanism-accuracy` (does the documented law match what the
system actually does), `witness-integrity` (vacuous-pass holes),
`host-safety` (can the probe damage foreign work on this contended host),
`provenance` (report numbers == receipt numbers), `replication`.

**Headline: no live forge found.** Every leg's verdict is genuinely
falsifiable and all ten laws replicated under my own run. The defects
found are one **falsified mechanism claim** (live-disproven below), one
**real shared-host hazard** (same blast radius as the banned by-name
unload), several assertion/witness laxities where the recorded data is
stronger than the check, and report provenance mislabels. All fixable.

---

## F1 — `description=` is not "dropped": it lands verbatim as a literal node prop — and so does EVERY unknown key (medium, mechanism-accuracy)

The arm's header comment (measure_audio.py:11565), the a1 docstring
(11851), the author report (§0/§2 "an UNKNOWN KEY — silently dropped"),
and the scout table (§1 "no prop", §1.1 "a bare unknown key at module
level is dropped" / "`sink_properties=` is the only prop vector") all
assert the value is **dropped**.

**Counterexample (live):**

```
pactl load-module module-null-sink sink_name=r80c_nmk description=R80CMARKERZZZ
→ rc=0, node.description = 'r80c_nmk Audio/Sink sink'   (verdict surface: still true)
→ node props carry: {'description': 'R80CMARKERZZZ'}     (the arg LANDED)

pactl load-module module-null-sink sink_name=r80c_unk2 foo.bar=R80FOOBAR totally.unknown.key=R80UNK42
→ rc=0, node props carry: {'foo.bar': 'R80FOOBAR', 'totally.unknown.key': 'R80UNK42'}
```

(Transcript: `controls-transcript.txt`, `controls.json`. The control load
without the arg has no `description` prop — the prop exists iff the arg is
passed. Both nodes unloaded by id; census clean.)

So the real law is: **bare module args are a prop vector** — every
unrecognized `key=value` is copied verbatim into the node props under its
literal key name. `description` lands under prop `description`, which the
display layer ignores (`node.description` is the field that matters, and
it stays derived). The scout's "no prop" and the arm's "silently dropped"
are both falsified — including the scout's `totally.unknown.key=42 →
silently ignored` row.

**Impact:** the a1 leg's *verdict* is untouched (it asserts the right
prop — `node.description` — and still goes red if the marker had won the
display field). But the armed ledger teaches a false mechanism; under
that model a future seat would never grep props for an arg's landing site
— exactly where a forge would hide (an arg "not working" while actually
mutating node state).

**Smallest safe correction:** reword the a1 claim to "lands as literal
prop `description`, ignored by the display path" (fix the same false law
in the scout row/§1.1), and record the landing in the receipt — e.g. add
`props.get("description")` (or a `raw_props` dict) to the
`_module_r80_nodes` leaf so the pass-through is visible in the artifact.

## F2 — teardown re-unloads stale module ids; a5 probes one deliberately — on a LIFO-recycled namespace this is the banned foreign-unload, one indirection removed (medium, host-safety)

The convention bans by-NAME unload because a name can name a foreign
module (scout §10). The same blast radius exists by-id whenever the id
has been **re-allocated**. The scout's own §3.1 measures the index law:
"indices are recycled aggressively … the next `load-module` anywhere on
the host gets the just-freed index". Confirmed live in my battery: four
sequential load/unload pairs all returned **536870921** (immediate LIFO
reuse), the foreign `r89prof_ns` null-sink at **536870936** appeared and
vanished during this session, and my replay's a5 leg was itself assigned
**536870936** — the just-freed foreign id.

Two code paths unload ids that are already freed:

- `_module_r80_teardown` (11813-11814): `for leaf in loads.values():
  _module_r80_unload(mid)` — the args entry's five ids were **already
  unloaded inside their legs** (lines 11891/11907/11923/11947/11960), so
  teardown unconditionally re-unloads five stale ids — and **discards the
  return value**. Between leg-unload and teardown the staleness window is
  ~10–40 s; any concurrent `load-module` (fleet lanes, other seats —
  `host_is_quiet: false` in both author receipts, and a concurrent r80
  run `…T153530…` happened during this review) that captures the freed id
  is silently killed. No witness records it.
- a5's `re_unload` (11965) pokes a ~1.2 s-stale id and *requires* rc=1
  `No such entity`. If the id recycled to a foreign module in that
  window, the probe returns rc=0 — the leg fails with a confusing verdict
  **and** a foreign module is destroyed.

Dormant on a quiet host (both green runs), live on the fleet's own
documented contention. The replay being green does not discharge this —
it's a race, not a law violation.

**Smallest safe correction:** legs mark `loads[name]["unloaded"]=True`
when their in-leg unload returns rc=0 and teardown skips those; replace
a5's destructive re-probe with a non-destructive absence witness (`pactl
list modules` — the id absent, or none whose `argument:` names an
`r80md_` sink). If a destructive check is kept, re-resolve the id's
current argument string first and unload only when it carries our tag.

## F3 — absence-witnesses fail OPEN on reader failure; presence-witnesses fail closed (medium-low, witness-integrity)

The teardown witnesses are only as good as their readers, and the readers
degrade silently:

- `_capture_r77_sink_names()` returns `[]` on pactl error →
  `sinks_gone = {nm: True for all}` — a pactl failure at teardown time
  makes every surviving sink report "gone" (11821-11826).
- `_playback_r78_node_names()` returns `None` on pw-dump error →
  `own_nodes_after: null` is **recorded** but `if rest:` never flags it
  (11827-11830) — a transient pw-dump failure yields a green receipt with
  a null witness and real strays possible.
- `_playback_r78_links()` returns `[]` on pw-link error → t3's
  `linked_after_death` absence-check passes vacuously (12378-12380); same
  shape anywhere an absence is asserted from a fallible reader.

Direction asymmetry: presence checks (node_seen, linked_immediately,
edge_a_linked) fail closed on reader failure; the "nothing survives"
checks all fail open. A flaky 100 ms of pw-dump at exactly teardown turns
green into "witness never ran".

**Smallest safe correction:** on a `None`/error reader, record
`coverage_blocked` or append a named failure — never a silent pass. The
`own_nodes_after: null` leaf already distinguishes the state; the verdict
just needs to read it.

## F4 — the report's "run 2 verbatim" column is run-1 data; one number matches no receipt on record (low-medium, provenance)

The §2 table is headed "measured (run 2 verbatim)". Against receipt
`…T134359…` (run 2, pid 736128):

| claimed verbatim | receipt run 2 | actually matches |
| --- | --- | --- |
| `pmid stale 536870942` | 536870931 | run 1 |
| `pw-cli destroy 151` | destroyed_id 227 | run 1 |
| `peak 8137` | peak_r 8189 | run 1 |
| `count 23→23` | 49→49 | **no receipt** (run1 49→49, verifier 47→47) |

The laws are identical across runs — only volatile fields differ — so no
verdict is affected. But "verbatim" is a provenance claim, and `23→23`
cites a number no receipt in the corpus contains (likely an
authoring-window probe). In a ledger whose axis is receipt fidelity this
is a defect, not a nit.

**Smallest safe correction:** regenerate the column from the run-2
receipt or relabel the column (drop "verbatim").

## F5 — t4's move assertion is weaker than its claim: `edge_dst` presence only, never pre-move absence / post-move exclusivity (low, falsifiability)

`t4_move_sticky` asserts `(tag:output_FL → mv_b:playback_FL) ∈
edges_first ∧ ∈ edges_late` (12394-12397). It never asserts
`edge_dst ∉ edges_before` and never asserts the `mv_a` edges are gone —
and it checks FL only. A stream that was *already* dual-linked to mv_a
**and** mv_b at spawn would satisfy every gate (move rc=0, edge present,
mv_b tap carries tone) while the move did nothing — the
sticky-move claim would pass on a stream that never moved. The recorded
`edges_before` already contains the discriminating data (this run:
exclusive mv_a, then exclusive mv_b — the receipt supports the strong
claim); the check just doesn't read it.

**Smallest safe correction:** assert `edge_dst ∉ edges_before`, assert
the mv_a edges absent at both post-move samples, and check both FL/FR
tuples (t5 already asserts its edge_src both ways in the same file —
12408-12431 is the model).

## F6 — the blocked path drops the teardown witnesses entirely (low, witness-integrity)

`_module_r80_block` (11833-11843) unloads `loads` and returns — no
`sinks_gone`, no `own_nodes_after`, no stray sweep. A mid-load-loop
failure (e.g. one of six sinks never enumerates) exits through the block
with blind unloads whose results are discarded (F2's hazard inside the
block path too: a recycled id → foreign kill + our node left up) and
**no witness** that anything leaked. Coverage is named honestly
(`coverage_blocked`) but the block's cleanliness is unmeasured.

**Smallest safe correction:** run the same teardown-witness tail in the
block path (it already takes `loads`), and don't discard the unloads.

## F7 — t3 inherits t2's stale edge on a `teardown_d` failure: same port tuple, wrong attribution (low, contamination)

t2's linger link is `lnk_a:monitor_FL → lnk_b:playback_FL`; t3's -m link
is the **identical tuple** (12219-12222 reuse `out_p`/`in_p`).
`teardown_d`'s rc is recorded (12211-12218) but never asserted. If
`pw-link -d` ever failed, the stale t2 edge satisfies
`linked_while_running` vacuously and trips `linked_after_death` — the
receipt would report "the -m link SURVIVED its client's death" while the
actual defect was t2's leaked link. Fail-red with a wrong cause is still
a misdiagnosis in a corpus whose receipts are the ledger.

**Smallest safe correction:** after `teardown_d`, gate t3 on the edge set
not containing the tuple (one `_module_r80_edges` sample) before spawning
`-m`.

## F8 — hygiene notes (no verdict impact)

- `tries` combine loads never join `loads` (12159-12181): a hypothetical
  rc=0 attempt leaks its module — the module-count check names the delta
  (red) but nothing unloads it. Fold successful attempt ids into `loads`.
- a1/a2/a3/a5 read node props immediately after `_module_r80_wait_node`
  with no settle (a4 settles at 11934): params like `EnumFormat` can lag
  presence in pw-dump → spurious red (fail-closed; flake risk only).
- t1's `module_count` spans a contended host — foreign churn between the
  two samples fails the leg spuriously (fail-closed; acceptable, but the
  failure text could name that).
- `sinks_gone` is vacuous for the a4 source-class node (never a pactl
  sink); `own_nodes_after` covers it — no hole, noted for completeness.

---

## What was attacked and held

- **No stimulus deletions, no spec-echo pins.** All ten legs drive a real
  stimulus and read back a graph/content witness: props via pw-dump,
  EnumFormat via params, pactl listings, directed pw-link edges, and
  pid-tagged-frequency monitor taps. `carries_tone` requires ≥8 `mine`
  windows of a per-run pid-derived L/R pair — t4's mv_b tap shows a
  continuous `mine` span [0.6–5.1 s], t5's dm_a tap [0.5–5.2 s]; the
  content pins are load-bearing and discriminate (a foreign/dual-link
  failure would break the span).
- **a3 is a real discriminator.** Controls: default load advertises a
  rate *range* `{default:48000, min:1, max:2147483647}`; `rate=44100` →
  `[44100]`; `rate=768001` (>768k) → `[768001]` verbatim. `[99999]` in
  the receipt is the arg's own write — the no-range-check law is real and
  even stronger than claimed.
- **t1's refusal is @DEFAULT_SINK@-specific.** Positive control (absent
  from the arm, present in the scout's §2.1, re-run live):
  `slaves=<real>` rc=0, `sinks=<real>` rc=0, `slaves=<nonexistent>` → the
  same rc=1 `Input/Output error` — the refusal signature is exactly
  "literal name doesn't resolve", i.e. non-expansion. The arm's leg is
  narrower than its claim but the corpus evidence covers the gap.
- **a4/a5 multi-phase lifecycle verified** live and in receipts:
  Audio/Source with 0 in-ports, source `<n>` listed, no sink, no
  `.monitor`; linger orphan survives unload with stale
  `pulse.module.id`, stays pactl-listed as sink+monitor, `pw-cli destroy`
  is the only removal path.
- **Wiring honest:** exclusivity sum includes `probe_module_r80`, mode +
  suffix prepend-only, `return bool(failed)` → exit code, absent legs go
  red (missing leg → `None` fields → failure appended), a mid-entry crash
  propagates (no receipt, nonzero exit — not green).
- **Teardown verified live**: `own_nodes_after: []`, all sinks gone, and
  my post-run census on the host shows zero r80 residue.
- **Run-to-run stability**: author's runs 1/2 and my replay share an
  identical 31-flag verdict surface; only volatile leaves differ (pids,
  recycled module ids 536870942→931→936, object ids, tap peaks,
  pid-derived tag frequencies 1210/1000 Hz — all disclosed classes).

## Impacted axes

- `mechanism-accuracy`: **F1** (falsified "dropped" law — includes the
  scout's pass-through model).
- `host-safety`: **F2**, partially **F6** (stale-id unloads under LIFO
  recycling; silent foreign damage possible under fleet contention).
- `witness-integrity`: **F3**, **F6**, **F7** (fail-open absence
  witnesses; block path unwitnessed; misattributed confound).
- `falsifiability`: **F5** (assertion weaker than claim; receipt data
  covers it).
- `provenance`: **F4** (verbatim-column mislabels; one number from no
  recorded run).
- `replication`, `falsifiability` of the ten verdicts themselves: intact
  — every law replicated on this seat's own run.

## Inspection record

Read `measure_audio.py` r80 block (11555-12440) + the shared r77/r78/r79
helpers it calls; both author receipts, the verifier receipt
(`…T152510…`), `r80-author.md`, `r80-scout.md` §1-§3.1, `r80-baseline.md`;
`git diff` verified +905/−3 prepend-only. Live: full replay (exit 0,
`failures: {}`), 9-load control battery with per-load id-unload and
before/after censuses (`controls.json`, `controls-transcript.txt`), 4-load
prop-marker battery (F1 evidence). Zero leftover modules/nodes/links from
this seat. Nothing committed; `measure_audio.py` untouched by this seat.
