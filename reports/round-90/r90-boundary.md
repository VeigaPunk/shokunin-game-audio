# R90 boundary — falsification of the r90 scout under load, host-state variation and unstated modes

**Seat: BOUNDARY (executor-class, leaf).** Host `plazir27`, lane
`~/Projects/shokunin/audio-shokunin` @ HEAD **`1abd954`** (the scout measured
`ee6d684`; the tree moved on between rounds). Window **2026-10-15 20:05–20:26
UTC** (17:05–17:26 UTC−3). Toolchain re-verified: PipeWire **1.6.8**,
WirePlumber **0.5.17-1**, pactl 17.0-98-gb096, Python 3.14.7.

**Zero tracked-file edits, no commits, no `set-default-*`.** Entry tracked-dirty
set was sibling-owned (`corpus/fixtures/measure_audio.py` + its `.pyc`); at exit
`git status` has **no tracked modifications at all**. Every write is under
`corpus/live/r90-boundary/` (harness `r90b_probe.py`, `run_all.sh`, 2 silent
tones, `receipts/s0–s8.json`, `runs/**` 899 raw files, 3.6 MB) plus this report.
**Every audio object this seat created is named `r90b_*`**; every census/sweep
matched only that prefix. Module unloads are **by id with a namespace guard**
(the id's args must contain `r90b_`, else the unload is refused); the single
by-name unload (the C13 replay) ran on `module-loopback` only after a
**zero-foreign pre-check**, so its blast radius was this seat's own modules.
**Exit state: `pactl list short modules | grep r90b_` → 0 rows, `pw-dump` → 0
`r90b_*` nodes/links, `pgrep r90b_` → 0 processes, hogs 0**
(`receipts/s7.json`; re-verified after the last stage).

**Labrat.** The single permitted `probeParent` labrat was dispatched once for a
read-only source hypothesis ("is there a pulse-path store writer that bypasses
the ~1 s debounce?"). It returned **FALSIFIED** with citations: all writes funnel
through `saveStreamProps` → `state:save_after_timeout`
(`/usr/share/wireplumber/scripts/node/state-stream.lua:451-459`, call sites
255/321/389); `/usr/include/wireplumber-0.5/wp/state.h:40-44` shows
`wp_state_save_after_timeout` takes **no timeout argument** (the delay is an
internal C constant; the binary constant itself was not extractable with its
read-only toolset). Zero side effects. Every measurement below is seat-owned.

---

## 0. Verdict table

| # | r90 scout claim | verdict | sharpest measured fact |
| --- | --- | --- | --- |
| 1 | C1 `wpctl settings` = 25-entry typed lattice, nothing saved | **CONFIRMED** | 25 settings; live `sm-settings` metadata keys **25/25 set-equal**; state dir = `default-nodes` + `stream-properties` only, **no `settings` file**; `-d/-s/-r` flags present (s0) |
| 2 | C2 `device.routes.default-sink-volume 0.064` ↔ SPDIF live volume | **CONFIRMED** | SPDIF `params.Props[0].channelVolumes = [0.063997, 0.063997]` vs setting `0.064` (s0 re-run after fixing the parse: the value lives in `info.params`, not `info.props`) |
| 3 | C4 store writes are debounced ≈1.0–1.2 s | **CONFIRMED, refined** | one **coalescing timer anchored on the last change**: creation 0.91–1.50 s, pw-cli Props 0.99–1.60 s, target 1.00–1.87 s (quiet and load pooled); a re-used key shows a **stale hit at t≈0** |
| 4 | C5 "pulse-protocol volume write lands **≤0.01 s**" | **FALSIFIED** | the 0.01 s hit is a **stale-row read**: f6b B wrote the same key (`r90s{rep}`) at **1.22 s** (its own polls, 3/3) and f2c V re-read it; clean fresh-key measurement: `pactl` returns in 8–29 ms and the row lands **1.004–1.783 s** (3/3 quiet + 3/3 load) |
| 5 | C5 field split: pulse writes `channelVolumes`, not `volume` | **CONFIRMED** | clean leg: `channelVolumes [0.125,0.125]`, `volume 1.0`; pw-cli path writes `volume 0.5` (3/3) |
| 6 | C6 replay restores the stored field only | **CONFIRMED** | replay of the pulse-written key: live Props `channelVolumes [0.125,0.125]`, `volume 1.0` — 3/3 quiet + 3/3 load |
| 7 | C7 target restore + `default` metadata witness | **CONFIRMED + new edge** | replay without `--target` links to stored `r90b_rb` + `target.object` metadata (3/3 quiet+load); **an explicit `--target` beats the stored target** (3/3, new) |
| 8 | C8 opt-out per stream and per device node | **CONFIRMED** | stream `state.restore-props=false` → no row in 3.0 s; device `sink_properties=…` → no row in 2.5 s; controls land 0.89–1.89 s (3/3) |
| 9 | C9 store keys route-less device nodes; no CLI deletes rows | **CONFIRMED (first half)** | control `Audio/Sink:node.name:r90b_oc*` rows appeared; deletion **not re-run** (would write operator state) |
| 10 | C10 capture needs `stream.capture.sink=true` | **CONFIRMED** | noprop `pw-record --target <sink>` → rc 1, `res:-2 no target node available` (14–22 ms, 3/3); with prop → `Input/Audio:application.name:…` row at **1.025–1.026 s** (3/3) |
| 11 | C10 "a stream that errors out in <1 s still wrote its row (3/3)" | **PARTLY FALSIFIED — bimodal** | scout's own receipts: `e_new_keys=[]` for reps 2–3 and `r90g2`/`r90g3` **absent at stage end** — only `r90g1` ever appeared (1/3); my faithful replay: rep1 no row, reps 2–3 row → **3/6 combined** |
| 12 | C11 pulse module namespace table | **CONFIRMED for replayed rows + 2 new classes** | null-sink control rc 0; zeroconf discover rc 1 `No such entity` / publish rc 0; stubs `Entity exists`; unknown `No such entity` (3/3); **`server=unix:/tmp/…` → rc 1 `Connection refused`** (not a phantom); `127.0.0.1:9` **bimodal** (rc 1 `Unknown error code` / rc 0 phantom) |
| 13 | C12 "id returned ≠ module alive" (phantom tunnel) | **CONFIRMED, method corrected** | s4 M1 (port 1, 3 reps quiet) + s6 (3 reps load) + a manual matrix for ports 1/2/7/9: args-aware probes at 0.017–4.0 s show **mine=False everywhere**; **but id-membership alone is unsound** — a free id was re-occupied by a foreign module 3 times (see §3.2) |
| 14 | C12 `unload-module <phantom-id>` → `No such entity` | **witnessed safely** | raw call on the free phantom id **declined** (recycle risk); error class witnessed on a provably-unassignable id: `unload-module 4000000001` → rc 1 `Failure: No such entity` |
| 15 | C13 `unload-module <name>` unloads EVERY module of that name | **CONFIRMED (safe vehicle)** | on `module-loopback` (0 foreign before): 2 loaded → one by-name unload → **0** remain, my null sinks untouched (3/3); **new edges**: prefix `module-loopb` → rc 0 + stderr `… not loaded`, nothing removed; a node/sink name → same rc 0 + `not loaded`; unknown name **rc 0 with the error only on stderr** |
| 16 | C14 single-pair grammar, extras silently ignored | **CONFIRMED** | bulk connect → 1 link rc 0; bulk `-d` → 2 links become 1; two link ids → rc 255, **nothing unlinked**; reversed/glob rc 255; duplicate `File exists`; single id works (3/3) |
| 17 | C15 "`-w` blocks indefinitely" | **REFINED (conditional)** | missing port → blocks (3/3 quiet + 3/3 load, 3.0 s bound); **valid pair → rc 0 in 5–11 ms**; **port appears late → rc 0 ≈50 ms after it appears** (3/3) |
| 18 | C16 listing patterns are slot-bound | **CONFIRMED + extended** | `pw-link -i '<pat>'` leaks the other side (slot-bound); `-i '' '<pat>'` filters; **`pw-link -l <pattern>` ignores the pattern entirely** (a no-match pattern still prints every link) |
| 19 | C17 link id is the first token of the `\|->` row; `-P` marker invisible | **CONFIRMED + new props surface** | ids usable for `-d` (3/3); `-p '{"foo":"bar"}'` → **`foo=bar` on the Link object** (3/3); `-p '{"link.passive":true}'` accepted rc 0 but **no `link.passive` prop** (3/3) |
| 20 | C18 EnumFormat is negotiation-invariant | **CONFIRMED byte-identical** | node EnumFormat sha `1735b4739ef7…` identical at rest / 48 k / post / 44.1 k (3/3; matches the scout's `1735b473…`) |
| 21 | C19 Format readability is negotiation-state dependent | **CONFIRMED** | port Format: `res:-5` at rest and after, readable `5a828addfad7…` while linked; node Format sticky `91f7342230f7…` after the stream ends (3/3) |
| 22 | C20 graph rate vs file rate | **CONFIRMED** | stream Format `e718690a7ce2…` @48 k and `684a7c8dad24…` @44.1 k; sink node stays `91f7342230f7…` (3/3; all match the scout) |
| 23 | C21 mid-stream sink-side `set-param Format` rejected −5, stdout lies | **CONFIRMED + node-class split** | rc 0, stderr `res:-5 … set param id:4 failed`, **622 B stdout echo**, link + stream survive (3/3 quiet + 3/3 load); **stream-node variant: rc 0, stderr empty (silent discard)** — the seal is node-class dependent, both classes measured in one window |
| 24 | C22 pw-v4l2 absent-class; advertisement ≠ objects | **CONFIRMED** | `which pw-v4l2` empty, no `/dev/video*`, no `/sys/class/video4linux`, `lsmod` count 0, `pw-cli ls Device \| grep -c v4l2` = 0 — while `pactl list` still advertises `api.v4l2` |
| 25 | C3 formKey / store hooks source-traceable | **CONFIRMED (read-only)** | `formKey` at `state-stream.lua:462-487`; hooks at 180-259 / 262-323 / 346-391; `saveStreamProps` 451-459 → `state:save_after_timeout` (single writer — labrat) |
| 26 | named unknown: "does `-t` ever print rows here?" | **CLOSED (negative)** | `pw-link -t` printed **no rows** in all four configurations: null↔null, null↔null + live stream, device-backed link, device-backed + live stream (3/3, out_len 0) |
| 27 | named unknown: `-m` never tested | **MEASURED** | `pw-link -m` alone → rc 255 `missing output and input port names to connect`; `-m -l` / `-m -o` stream `+` deltas and block (2 s bound, non-empty output) |

---

## 1. The headline falsification — C5's "≤0.01 s pulse store" is a stale-row artifact

The scout's own receipts contain the refutation; the boundary seat only had to
read them and then measure cleanly.

**1.1 The contamination chain (all from `corpus/live/r90-scout/receipts/`).**

1. `f6b` stage (B leg) writes the pulse volume for app `r90s{rep}`:
   `pactl set-sink-input-volume <idx> 50%` (ms = 2–3, rc 0), then polls the
   store for field `volume == 0.5` — the **wrong field** — and reports
   `ok=false` after 8 s. Its raw poll log shows the real event:
   `channelVolumes` goes `[1.0,1.0] → [0.125,0.125]` at **t = 1.22 s, 3/3**
   (polls at 0.01/0.41/0.82/1.22 s).
2. `f6b` stage-end `r90_store_keys` contains `Output/Audio:application.name:r90s1`
   (and `r90s2`, `r90s3` by the later reps).
3. `f2c` stage (V leg) **re-uses the same app names** `r90s{rep}`, runs the same
   `pactl set-sink-input-volume … 50%`, and polls for
   `channelVolumes == [0.125,0.125]` — the value already written ~minutes
   earlier. Its first poll (t = 0.01 s) hits the **pre-existing row**.
   The scout reports this as "lands ≤0.01 s (3/3)".

So the scout measured a *read of an old row*, not a write. This is the same
error class the scout itself diagnosed in `f6` ("the 0.1 s window only ever saw
the pre-existing row") — here it is the same key reused across stages.

**1.2 Clean re-measurement (fresh `r90b_*` keys, stat-gated 2 ms watcher,
pre-value guard recorded).**

| leg | quiet (s3 reps 2–3) | load (s6, 3/3) | command ms |
| --- | --- | --- | --- |
| pulse `pactl set-sink-input-volume 50%` → row change | **1.004 / 1.006 s** | **1.004 / 1.783 / 1.004 s** | 8–29 ms |
| `pw-cli set-param Props {volume:0.5}` → row change | 1.009 / 1.005 s | 1.0 / 0.992 / 1.597 s | 12–29 ms |
| creation (node → row appears) | 1.501 / 0.932 s | 0.919 / 0.911 / 0.945 s | — |
| target (`move-sink-input`) → `target` stored | 1.867 / 1.007 s | 0.999 / 1.0 / 1.005 s | 7 ms |

In the clean leg the row **did not exist before** the command (`p3_pre = null`
in s6 rep3 and in the load legs) and appears with the new value ~1.0 s later —
there is no ≤0.01 s path. The labrat's source trace agrees: a single writer,
`state:save_after_timeout`, no bypass hook; the ≤0.01 s reading is only
explicable as a stale/visible-before-write artifact.

**Refined law (replaces the scout's two-speed story):** the session-manager
store is one **coalescing debounce ≈1.0 s after the last change**, shared by
creation, Props and target paths; the table content is always the latest state.
A harness that reuses a key therefore sees the old value at t≈0 — the only way
to measure the write latency is a **fresh key or a pre-value guard**.

---

## 2. Restore law under load and host-state variation

`receipts/s3.json` (quiet) and `receipts/s6.json` (32 `yes` + 4 `dd` writers;
loadavg ≈75 → ≈150 during the stage). All legs ≥3 reps; every write leg records
the pre-value.

- **P1 creation** — clean log shows `null → row` (e.g. s6: `[0.0, null]` then
  `[0.919, {…channelVolumes [1.0,1.0]}]`). Quiet 0.93–1.50 s, load 0.91–0.95 s.
  No load-induced stretch.
- **P2 pw-cli Props** — quiet 1.005/1.009 s; load 0.992/1.0/**1.597** s (one
  outlier). Pre-value present (creation row) in 4/6 clean reps; the write
  replaces `volume` and leaves `channelVolumes` untouched.
- **P3 pulse** — the falsification core (§1); the command returns in 8–29 ms,
  the row changes ~1.0 s later (one 1.783 s outlier under load).
- **P4 replay field split** — 6/6 (quiet+load) live Props show
  `channelVolumes [0.125,0.125]` restored and `volume 1.0` untouched.
- **P5/P7 target** — stored `target: r90b_rb` / `r90b_rc` at 1.00–1.87 s;
  replay without `--target` links to the stored sink (own rows
  `r90b_rb:playback_*`) and publishes `target.object` in the `default` metadata
  (subject = bound-id, value = object serial), 6/6.
- **P6 explicit vs stored (new)** — replaying the same key **with**
  `--target r90b_ra` links to `r90b_ra` (3/3 quiet + 3/3 load): an explicit
  target beats the stored one (consistent with `restore_stream_hook` skipping
  restore when `target.object`/`node.target` is present, source lines 143-151).
- **P7 vanished stored target (host-state variation, new)** — store
  `target: r90b_rc`, unload the sink, replay without a target: **no link forms**
  (own rows show only the stream's output ports) 3/3 quiet + 3/3 load. The
  stale-target lookup fails in the restore hook (`if target_node and metadata`),
  and no fallback to the default sink materialized within the 2.2 s window.
- **P8/P9 opt-outs** — stream and device-node opt-outs produce no row over
  3.0/2.5 s; controls land at 0.89–1.89 s (3/3 each).
- **Host-state variation** — the store grew from 2691→2750 rows in the scout's
  window to **4437 rows / 663 771 B** at this seat's entry and 4564 rows at exit;
  `default-nodes` was modified by others mid-window (mtime 17:15, 450 B, entries
  `default.configured.audio.source.0=r86ctl_src` and
  `…sink.0=r87b_ns` — sibling objects); the live default sink stayed
  `…HiFi__SPDIF__sink` throughout. This seat never issued `set-default-*`.

---

## 3. Pulse module namespace under replay and variation

### 3.1 Phantom tunnel (C12) — confirmed, 6 × 8 probes

`pactl load-module module-tunnel-sink server=127.0.0.1:1 sink_name=r90b_tun*` →
rc 0 + id, then **args-aware** probes at 0/30/60/120/250/500/1000/2000 ms: the
id is never held by my module (`mine=False` in all 24 quiet probes (s4, 3 reps)
and all 24 load probes (s6, 3 reps)); no node, no pactl sink. A manual matrix
extended this to ports **1, 2, 7** (absent at every probe up to 4 s) and
confirmed `unload-module <id>` → `Failure: No such entity` on a
never-assignable id.

### 3.2 The recycled-index hazard (new; the scout's method is unsound here)

Module indices are recycled immediately. Three independent events:

1. **Manual matrix, port 9**: at t=4.0 s the free id `536870925` was held by a
   **foreign** module (`module-null-sink sink_name=r82ff_ns_2422178`); a raw
   `unload-module 536870925` returned **rc 0** and killed the sibling's module.
   *Disclosed interference event* — the sibling re-created it (it is present
   again). This is why the harness now refuses/skips raw unloads of free ids.
2. `s4` rep3: the phantom id was held by a foreign `module-null-sink` at unload
   time → guard recorded `skipped: held_by_foreign`, no unload issued.
3. `s6` rep3: the phantom id was held by sibling `r98s_ns` → guard `refused`.

Consequence for the scout's table: "the id is already gone at the first probe"
is right, but an **id-membership liveness check can also read false-alive**
(a recycled id owned by another seat). The sound witness is the module row
(name + args), which is what this seat used.

### 3.3 By-name unload (C13) — confirmed on a safe vehicle, with new edges

Zero `module-loopback` existed before each rep (pre-check). Two loopbacks loaded
(`source=r90b_m6a.monitor sink=r90b_m6b`, node names `r90b_lb*`) → one
`pactl unload-module module-loopback` → **0 loopbacks remain, my null sinks
alive, no foreign module lost** (3/3). New edges:

- `pactl unload-module module-loopb` (prefix) → **rc 0**, stderr
  `Failed to unload module: Module module-loopb not loaded`, nothing removed
  (matching is exact, not prefix) 3/3;
- `pactl unload-module r90b_m6a` (a sink/node name) → same rc 0 + `not loaded`
  (args are not searched) 3/3;
- **an unknown name is rc 0 with the error only on stderr** — the scout's
  "rc is not a validity witness" theme extends to the name-form unload.

### 3.4 Other module classes (3/3 unless noted)

- `server=unix:/tmp/r90b_nope.sock` → **rc 1 `Connection refused`** (a unix
  socket fails synchronously — no phantom).
- `server=127.0.0.1:9` → **bimodal**: rc 1 `Unknown error code` (rep1) vs
  rc 0 + phantom (reps 2–3) — named as unstable, not a law.
- `reconnect_interval_ms=1000` → rc 0, alive at 0.6 s, no node, unload rc 0.
- `module-zeroconf-discover` rc 1 `No such entity`; `module-zeroconf-publish`
  rc 0 and alive (marker arg `r90b_marker=1` landed as a prop, which is how the
  guard could unload it by id), **but `avahi-browse -a/-t/-r -p` showed an empty
  baseline and no `_pulse-sink._tcp`/`_pulse-source._tcp` service while publish
  was loaded with a live sink** (0 bytes, 3/3) — "publishes" remains
  **unconfirmed**; the browse baseline is empty, so this is a bounded negative,
  not a proof of failure.
- preloaded stubs → `Entity exists`; `module-not-a-module` → `No such entity`.

---

## 4. `pw-link` grammar replays and unstated modes

Replays (`receipts/s1.json`, 3/3): connect rc 0 → 1 link; bulk connect
`A B A2 B2` → **first pair only** (1 link, rc 0); bulk `-d A B A2 B2` → 2 links
become 1; `-d <id1> <id2>` → rc 255 `failed to unlink ports: No such file or
directory` with **both links still present** (own_links = 2); reversed
direction and globs → rc 255; duplicate → rc 255 `File exists`; single link id
→ rc 0. Listing: `-i '<ns_b pat>'` leaks the other side (slot-bound), `-i ''
'<ns_b pat>'` filters; **`-l <pattern>` ignores the pattern** (a no-match
pattern printed 343–829 B of rows).

Unstated modes (`receipts/s5.json`, 3/3):

- **`-w` late port** — `pw-link -w r90b_late:monitor_FL <in>` started with the
  port absent; the sink was loaded at t=1.5 s and the command **returned rc 0
  ≈50 ms later**, link present. `-w` is a wait-for-creation primitive, not a
  hang; it hangs only when the port never appears (3/3 quiet + 3/3 load at the
  3.0 s bound).
- **`-p` props** — `-p '{"foo":"bar"}'` → the Link object carries
  `"foo": "bar"` (3/3); `-p '{"link.passive":true}'` → rc 0 but **no
  `link.passive`** prop (3/3) — same invisibility the scout found for `-P`.
- **`-m`** — standalone → rc 255 `missing output and input port names to
  connect`; `-m -l` / `-m -o` stream `+` deltas and block (2 s bound).
- **`-t`** — no rows in all four configurations, including a device-backed link
  with a live (silent) stream (3/3). The scout's named unknown is closed
  negative.
- **`-v`** — verbose listing prints port properties (non-empty).

---

## 5. EnumFormat / Format replays

`receipts/s2.json`, 3/3 — all shas **identical to the scout's**:

| object | rest | mid-48 k | post | mid-44.1 k |
| --- | --- | --- | --- | --- |
| sink node `EnumFormat` | `1735b4739ef7…` | `1735b4739ef7…` | `1735b4739ef7…` | `1735b4739ef7…` |
| sink node `Format` | `res:-5` (empty) | `91f7342230f7…` | `91f7342230f7…` | — |
| sink port `Format` | `res:-5` | `5a828addfad7…` | `res:-5` | — |
| stream node `Format` | — | `e718690a7ce2…` | — | `684a7c8dad24…` |

- Mid-stream sink-side `set-param Format {…44100…}` → rc 0, stderr
  `res:-5 (Input/output error): set param id:4 … failed`, **622 B stdout echo**,
  link and stream survive (3/3 quiet + 3/3 load).
- **Stream-node variant (new)**: same pod on the live stream node → rc 0,
  **stderr empty**, stream survives (3/3). The scout cited r87 for a "silently
  discarded" stream-node write but never measured it in r90; measured here, the
  seal is node-class dependent: explicit −5 on the sink node, silent acceptance
  on the stream node.

---

## 6. Read-only replays (settings, v4l2) and the C2 cross-witness

`receipts/s0.json`: 25 settings parsed with Name/Desc/Type/Default/Value;
`sm-settings` metadata key set is **exactly** the CLI's key set (25/25);
`ls -la ~/.local/state/wireplumber/` shows only `default-nodes` +
`stream-properties`; `wpctl settings -h` lists `-d/--delete`, `-s/--save`,
`-r/--reset`. The SPDIF live volume (`params.Props[0].channelVolumes
[0.063997, 0.063997]`) matches `device.routes.default-sink-volume 0.064`.

v4l2: `which pw-v4l2` empty; no `/dev/video*`; no `/sys/class/video4linux`;
`lsmod` match count 0; `pw-cli ls Device | grep -c v4l2` = 0 — while
`pactl list` still advertises `api.v4l2` in `session.services` (advertisement ≠
objects, as the scout said).

---

## 7. C10 replay — and a second stale-claim correction

- Noprop capture: `pw-record --target r90b_ca /dev/null` → rc 1,
  `res:-2 no target node available` in 14–22 ms (3/3) — the r76/r77-pinned law
  holds.
- With the prop: `Input/Audio:application.name:r90b_cap{rep}` appears at
  **1.025–1.026 s** (3/3), process alive.
- **"Dying stream still stores" is bimodal, not 3/3.** The scout's own f6b E
  receipt: `e_new_keys = ['…r90g1']` for rep1 and `[]` for reps 2–3, and
  `r90g2`/`r90g3` are **absent at stage end** — the report's "3/3" is not
  supported by its own data (only rep1 produced a row). My faithful replay
  (`pw-record` noprop, node created then stream fails) produced: rep1 **no
  row**, reps 2–3 **row** — 2/3. Pooled: **3/6**. The store is keyed on a
  transient node's Props change, and whether that save is scheduled before the
  node is destroyed is a sub-second race. (A `pw-play` of a missing file, where
  no node is created, stored nothing 3/3.)

---

## 8. Harness bugs, instabilities and contention (mandatory disclosure)

1. **My own s3 rep1 was contaminated by my own dry run** — the battery reused
   the key names (`r90b_cr1q` …) created minutes earlier, so rep1 read stale
   rows (all delays 0.0, `keys_added=0`). Rep1 is **invalidated**; reps 2–3 and
   all load reps are clean. Same error class as the scout's f2c V, self-caught.
2. **First s4 run crashed** (`TypeError`) after loading two null sinks; they
   were cleaned by id before the rerun. The battery rerun is clean (`left=[]`
   each rep).
3. **`probe_module` was initially id-membership only** and read a false "alive"
   for `127.0.0.1:9` in the dry run; the manual matrix exposed the cause (the
   free id had been taken by a foreign module). Fixed to record the module row
   (name+args) and a `mine` flag; the phantom table above uses the fixed probe.
4. **`link_ids()` was initially global** (all links on the host). Audited: in
   the first s1 run `c8` disconnected one of **my** links each rep (own_links
   2→1; total rows dropped by exactly one link's two rows), so no sibling link
   was lost — but the pattern was unsafe and was replaced with a
   namespace-filtered, deduped listing before the s1 receipt was regenerated.
5. **`link_rows` double-counts** each link (one `|->` row and one `|<-` row);
   all counts quoted here are from `pw-dump` link objects (`own_links`), not
   row counts.
6. **`-p` dump race** in the first dry run (dump before the link materialized);
   fixed with a 0.3 s settle.
7. **s0's SPDIF parse initially read `info.props`** (empty) instead of
   `info.params.Props[0]`; fixed and s0 re-run.
8. **Interference events caused by this seat** (both pre-battery, both
   disclosed): the raw unload of the recycled id `536870925` killed sibling
   `r82ff_ns_2422178`; the sibling's lane loads/unloads modules per leg and the
   module was observed present again minutes later (and is absent again now —
   the lane's normal churn). The harness itself never unloaded a foreign
   module: three free/foreign-held ids were refused or skipped by the
   namespace guard.
9. **Contention ledger (by name, live during the window).** Audio lane:
   `r82ff` (ffmpeg lane; `r82ff_2422178_*` links/nodes), `r86b`
   (`r86b_probe.py`, `r86b_ns`, and the `default-nodes` entry `r86ctl_src`),
   `r87b` (`r87b_ns`, `r87b_ns2`), `r89b` (r89-boundary: `r89b_ns`,
   `r89b_ns44`, `r89b_ns_b`, tone legs), `r93s` (`r93s_in`/`r93s_fc_in/out`,
   a `pipewire -c filter-chain.conf` process), `r96s` (`r96s_cli.py`,
   `r96s_ns`, `r96s_pulse_trigger`), `r98s` (`r98s_ns`, `r98s_drain`).
   Game-dev lane: godot batteries (`r92-verify2 reps-hog`, `r95b_order`,
   `r100_gui`, `r89-simplifier`, `r90-author`, `r92b`, `r94b`). Loadavg over
   the window **48 → 153** (≈60–75 ambient "quiet", ≈150 during my hog
   stages; per-stage values in every receipt's `loadavg`/`hogs` fields). This
   seat added 32 `yes` + 4 `dd` writers only inside s6, killed in `finally`;
   quiet passes are quiet *relative to* the load passes, not on an idle host.
10. **`default-nodes` was changed by others mid-window** (mtime 17:15, 450 B,
    entries referencing `r86ctl_src`/`r87b_ns`); my seat never issued
    `set-default-*`. Store rows: 4437 at entry → 4566 at the final check;
    **this seat added 73 `r90b_*` rows** (the same permanent-residue class as
    every prior round — no CLI deletion exists; `wpctl settings -d` covers
    settings keys, not the stream store; late debounced saves can still add a
    few more).

---

## 9. Remaining unknowns (honest edges)

- **The timer constant.** Data are consistent with "save fires ≈1.0 s after the
  last change", but the C-level value was not extracted (the labrat could not
  read the binary; the Lua call site passes no timeout).
- **`127.0.0.1:9` bimodality** (rc 1 `Unknown error code` vs rc 0 phantom) is
  measured, not explained.
- **zeroconf-publish's actual registration** is unconfirmed (avahi-browse shows
  an empty baseline even with publish + a live sink; journal is empty for
  wireplumber here).
- **The dying-stream store race** (which sub-second ordering schedules the save)
  is characterised (3/6) but not read.
- **Row deletion** was not re-run (would write operator state); the scout's
  C9 second half stands as-is.
- **`-p` prop filtering**: `foo` lands, `link.passive` does not — mechanism
  unread (likely the link factory normalizes it).

---

## 10. Artifacts & provenance

`corpus/live/r90-boundary/` (untracked, 3.6 MB): harness `r90b_probe.py`
(stages s0–s8), `run_all.sh`, silent tones `r90b_sil48.wav`/`r90b_sil441.wav`,
`receipts/` and `runs/` (899 raw files, incl. `runs/battery.log`,
`runs/s*/rep*/` stdout/stderr + `*.cmd`).

| receipt | sha256 (prefix) | content |
| --- | --- | --- |
| `s0.json` | `f1960bbcd0f8fb19` | settings lattice, sm-settings set-equal, state dir, v4l2, store census |
| `s1.json` | `f018fc50bb9a3c54` | pw-link grammar replays (3 reps, namespace-filtered ids) |
| `s2.json` | `99f2096fece79b51` | EnumFormat/Format + mid-stream set-param (3 reps) |
| `s3.json` | `c8559a489ddeca04` | restore law quiet (rep1 self-contaminated; reps 2–3 valid) |
| `s4.json` | `4c408dee71b4a91e` | modules: phantom, by-name (safe class), zeroconf (3 reps) |
| `s5.json` | `742443fc3b1ae935` | unstated modes: `-w` late, `-p`, `-m`, `-t`, `-v` (3 reps) |
| `s6.json` | `914deabc6c1ed041` | restore + phantom + `-w` + set-param under 32+4 hog load (3 reps) |
| `s7.json` | `84133203ea2d6564` | cleanup + final census |
| `s8.json` | `2ef83aa68569994d` | C10 capture replay + dying-stream bimodality |

**Verdicts here are seat-side falsification attempts; the canonical Rust runtime
remains the only judge.**
