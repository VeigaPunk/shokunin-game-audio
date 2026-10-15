# R80 BOUNDARY — seat output (labrat/BOUNDARY leaf)

**Provenance:** seat 43afb293, glm-5.3-flash lane (ufo-labrat), dispatched
2026-10-15 post-15:01 window. Seat ran **read-only** (find/grep/read — no
shell, no write). Report body persisted verbatim by orchestrator; the seat
executed zero commands and created zero modules/nodes/links/files — nothing
to clean up. Every "measured" verdict below is mined from recorded receipts
(`corpus/live/r80-scout/receipts/*`, `corpus/live/r80-author/*`,
`corpus/live/r78-boundary/*`); every edge with no recorded measurement is
marked **UNMEASURED** with the probe command for a future exec-capable seat.

**Hypothesis under test:** the r80 author's 10-leg lattice + scout laws break
at edges the legs didn't cover (id reuse, contradictory props, class
partition, mid-move death, source-side dont-move, double-linking,
name-unload).

**Axes:** falsification-sharpness · hazard-severity · evidence-cited
(file:line) · cost.

---

## Named boundary classes

### B1 — Stale-id collision hazards — **CONFIRMED, sharpened** · severity: medium-high (teardown safety)

Expected: `pulse.module.id` recycles; probed whether **object.id and
client.id** recycle too.

Measured (receipts, verbatim):

- **module index LIFO reuse**: 6 linger-orphans all stamped
  `pulse.module.id=536870917` (`p3-linger-orphans.json:15,36,57,78,99,120`);
  unload of that index → `rc=1 Failure: No such entity` (`:200-203`). In the
  **author's own 3rd receipt** (`…T152510343508Z`), a5's orphan carried pmid
  `536870943` (`:710`) and `lnk_a`'s live module *then* received the same
  `536870943` (`:790`) — **a stale pmid pointing at a different live module,
  inside one receipt**.
- **`object.id` recycles within seconds**: author's receipt shows legs a1→a5
  **all** `object_id: 290` (`:414,477,539,592,660`) while serials climb
  102101→102146; scout `class_ovr` reps 1&2 both id `102`
  (`p1-null-args.json:2822,2887`); `unknown_k` reps all id `220`.
  **`pw-cli destroy <stale-id>` can kill a different node** — the author's
  destroy-by-id was safe only because it scraped the id by *name match* in
  the same instant.
- **`client.id` recycles**: `94` on a1–a4; `239` on all `unknown_k` reps;
  `176` on class_ovr reps 1&2.
- **`object.serial` never reused**: monotonic across the session
  (76236→…→76361→…→102146) — the only stable cross-time handle. No serial
  wrap is observable (u64).

Conclusion: stale-id hazard is **real and three-layered** (pmid, object.id,
client.id all recycle; only serial is safe). Confirms scout §3.1/§5.2 and
adds object.id/client.id as concrete kill-the-wrong-node vectors for any
cached-id teardown.

### B2 — "pactl resolves a duplicated sink name to the second node" is a **receipt artifact** — scout claim **PARTIALLY FALSIFIED** · severity: medium

Expected: pactl name→object resolution picks one of the same-named nodes.

Measured: `pactl_sinks()` in `r80_probe.py:168-175` builds
`out[name] = row` — a dict keyed by sink **name**, so the second
`r80_p1_dup` row **overwrites** the first; the receipt's
`"r80_p1_dup": {"index": "76361"}` (`p1-null-args.json:3551`) is
last-write-wins of the parse, **not** a pactl resolution measurement. The
raw stdout keeps **all** same-named rows (p3 `pactl-view-of-orphans` stdout
at `:150` lists three `r80_p1_lng` sinks 76263/76275/76296 — pactl itself
resolves nothing here).

The **only real name-resolution measurement on this host** is r78b's
`dup_name_lowest_serial_wins` (`r78-boundary.md` §1,
`probe-p1-forged-target-r78b.json`): `--target`/WirePlumber routing resolves
to the **LOWEST serial / first-created** node, 3/3 — the *opposite*
direction of the scout's claim.

Conclusion: the scout's dup-name row measured dict overwrite, not
resolution. Whether pactl **verbs** (`set-sink-volume <name>`,
`move-sink-input <idx> <name>`, `set-default-sink <name>`) resolve to first
or second same-named node is **UNMEASURED** — and is itself the sharp
probe: `pactl set-sink-volume <dupname> 47%` then read which serial's
volume moved.

### B3 — `pactl list short modules` enumerates **native** libpipewire modules; native-id/name unload is an unmeasured kill-switch — **UNMEASURED** · severity: potentially critical

Expected: pactl's module namespace is pulse-only.

Measured **refuting**: `pactl list short modules` contains ids 1–22 =
`libpipewire-module-rt`, `-protocol-native`, `-metadata`, `-client-node`,
`-adapter`, `-link-factory`, `-session-manager`, … (`p5-index-law.json:2229-2242`;
`pactl_module_list_has_native: true` at `p7…:387`). The unload matrix tested
`536870000` → `Failure: Access denied` (`:1175`) but **never a live native
id**.

UNMEASURED edges — **do not run on a live/shared host**:

- `pactl unload-module 12` (live `libpipewire-module-client-node`): refuses
  via below-base check, or **actually unloads a core module** — the two
  code paths are distinguishable only by running it.
- `pactl unload-module libpipewire-module-adapter`: the name-unload path
  that destroyed every `module-null-sink` (scout §10) may name-match
  native modules.
- `pactl unload-module r80_p1_lng` (a *node* name, not a module name):
  expected `not loaded` rc=0 no-op (like `bogus-string`), unverified.

Conclusion: scout §3.3's "two disjoint namespaces" claim holds for
**loading** but the **enumeration** claim is wrong — the namespaces are
disjoint for load/unload while pactl's *listing* is the union. Any seat
that enumerates modules by index range can mistake native ids for
unclaimed slots. Probe only under a disposable daemon
(`PIPEWIRE_RUNTIME_DIR` isolation).

### B4 — Two contradictory `sink_properties` in one arg string — **UNMEASURED** · severity: low

Expected edge: `sink_properties=device.description=A device.description=B`
or two `sink_properties=` modargs.

Evidence base: author §3's truncation (`description=r80md desc <pid>
marker` → `node.description="r80md"`) proves the value is whitespace-split
into a proplist — but the same-key-twice winner is unmeasured (PA proplist
semantics suggest last-wins inside the string; the separate-modargs case
may replace the entire proplist — inference, not measurement). Probe:
`load-module module-null-sink sink_name=X "sink_properties=device.description=AAA device.description=BBB"` → `pw-dump`
`node.description`; then `sink_properties=device.description=AAA sink_properties=node.nick=BBB` → which prop survives?

### B5 — `media.class` beyond `Audio/Source` on module args — **UNMEASURED** · severity: medium

Measured: `Audio/Source` → source node 0in/1out `capture_FR`, no
`.monitor` (author a4, verbatim `:590-632`); explicit `Audio/Sink` (p2
null-props). Untested and sharp: `media.class=Stream/Output/Audio` on a
sink node — WirePlumber's stream-linking policy could autoconnect the
module-made "stream" node's outputs **into the default sink** (a fake
producer); `media.class=Foo/Bar` (unknown — verbatim prop, WP ignores?);
`media.class=` empty; `Audio/Duplex`, `Video/Sink`; `Audio/Source`+
`object.linger` (does a lingering source-class orphan also get
pactl-listed/managed?). r78b's crash/stall partition was **stream-node**
props (`-P`), a different vector — the module arg is a verbatim proplist
write, so the interesting question is WP's downstream policy reaction, not
module refusal.

### B6 — `move-sink-input` when the target vanishes mid-move — **CONFIRMED via r78b prior evidence; strict-race variant untested** · severity: low (already benign)

Measured (`probe-p3-move-races-r78b.json:2409-2613`, `r78-boundary.md`
§3): move rc=0 → `unload-module` of the destination **+0.35 s later** →
consumers `{}` ~0.35 s → re-link to the SPDIF default, stream alive.
Loss-fallback composes with move; the stream does **not** re-pin to the
dead target. Siblings measured: move→nonexistent rc=1 `No such entity`
stays put; move→source/`.monitor`/stale-idx rc=1; move-sink-input on a
**source-output** idx rc=1; double-move 60 ms apart → **transient
fan-out** {old,new} ~0.3–0.5 s (non-atomic move).
UNMEASURED variants: unload *during* the move call (true race); move
**by name** to a duplicated name (which serial gets the stream — couples
to B2); move to a **linger orphan** (pactl-valid sink with no module —
should succeed; untested).

### B7 — `node.dont-move` on a source — **UNMEASURED** · severity: low-medium

Measured only on sink-inputs (r80 t5: rc=0 silent no-op, edges unchanged;
r77: `move-source-output` itself works). Untested: `pactl
move-source-output` on a `node.dont-move=true` capture stream (plausibly
the same no-op via the shared `linking.allow-moving-streams` policy —
inference); `dont-move` on the **sink node** as a move-*target* filter;
`node.dont-reconnect`/`dont-move` combos.

### B8 — `pw-link` on already-linked ports / link idempotency — **UNMEASURED** · severity: medium

r80's t2/t3 (and scout p7-A) linked **unlinked** ports — the recorder was
`--target 0`-pinned (`probe_p7_authority.py:85`). Untested: `pw-link <o>
<i>` where WP already linked the pair (second Link object created? dedup?
does WP reap the foreign link?); the same `pw-link` twice (idempotent?);
`pw-link -m` on an already-linked pair — if a second link is created,
killing `-m` leaves the WP link; if it *replaces*, killing unlinks the WP
edge (surprise). r78b's `move_revives_unlinked` (a `pw-link -d`'d stream
re-links on move) shows the link/move layers are non-exclusive — the
double-link coexistence question is open.

### B9 — `module-combine-sink` with no `slaves=` binds **foreign and orphan** sinks — **CONFIRMED (documented), sharpened** · severity: medium

p8 `combine-noargs` (args `[]`, receipt `:1479+`): one
`output.<n>_<slave>` branch **per sink present at load time, foreign +
orphan sinks included**. Two boundary implications beyond the report's
wording: (a) a no-slaves combine silently fans a stream into *another
lane's* sink — cross-lane interference primitive; (b) a branch named for
a **linger orphan** binds to a node that has no module — and
`slaves=<orphan-name>` explicitly is untested (orphans are first-class
pactl sinks, so the load should succeed: inference from p3's listing).

### B10 — `rate=` outside the EnumFormat range — **UNMEASURED** · severity: low

a3's `rate=99999` landed verbatim (`:554`); the node's offered range is
`[1, 2147483647]` (`:432`) — 99999 is *in-range*, so "no range check" is
proven only for valid values. Untested: `rate=0`, `rate=-1`,
`rate=2147483648`, `rate=abc` — clamp, refuse, or verbatim? `format=` with
PA-valid-but-unsupported tokens likewise unprobed.

---

## r80 pinned claims: falsified vs confirmed

**Falsified / corrected (1):**

- Scout §1 `dup_name` interpretation — "pactl's name→object lookup returns
  the *second* node" is a **dict-key artifact**, not a resolver
  measurement (B2). The only measured resolution on this host (r78b,
  WirePlumber) goes to the **first-created/lowest serial**. The
  underlying fact (two same-named nodes coexist; pactl-verb resolution
  ambiguous) stands; the direction claim does not.
- Scout §3.3 "two disjoint namespaces" — **enumerable-union correction**:
  `pactl list short modules` lists native `libpipewire-module-*` ids 1–22
  alongside pulse ids (B3). Disjoint for load/unload, unified for
  listing.

**Confirmed (all 10 author legs + scout laws, third receipt
…T152510343508Z, `failures: []`):** a1 `description=` dropped/derived
string; a2 `sink_properties=device.description=` wins; a3 `rate=99999`
verbatim; a4 source-class 0/1 + `capture_FR`; a5 orphan lifecycle
(client_id null → re-unload rc=1 `No such entity` → `pw-cli destroy 290`
gone); t1 `@DEFAULT_SINK@` refusal `pa_io_error` both spellings (47→47
modules); t2 linger +2.0 s; t3 `-m` dies (exit −9); t4 sticky at
+1.2 s/+4.6 s with tone on mv_b tap (`f_l≈1210, a_l≈7980`); t5 dont-move
no-op. Plus: LIFO index reuse, `#N`/bogus-string rc=0 no-ops, `#`
dead-index, name-unload-destroys-all (scout §10 incident), orphan
unreachable-via-pactl, stream-linger does not extend life.

**New boundary gaps for a future exec-capable seat** (priority): B3
native-id/name unload (**never blind on a live host** — disposable daemon
only) > B8 double-link/pw-link-on-occupied-port > B5 module-side
media.class partition (`Stream/Output/Audio` on a sink is the dangerous
row) > B2 pactl-verb dup-name resolution > B7 source-side dont-move > B4
contradictory sink_properties > B10 out-of-range rate >
B6-strict-race/B9-orphan-slave.

**Cleanup status:** trivially clean — no loadable was loaded, no
node/link/file/process created, repo unmutated (read-only evidence
mining). `r80-boundary` artifacts not written (tool constraint,
disclosed); this output is the report body for verbatim persistence.
