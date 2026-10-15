# R80 scout — the `pactl load-module` lattice + dynamic topology lifecycle

Round 80 pre-measurement. Host `plazir27`, measured 2026-10-15 ~01:50–02:25 UTC−3.
Repo `~/Projects/shokunin/audio-shokunin` @ HEAD `d9aa6f9`. Toolchain: PipeWire
**1.6.8** (pactl/pw-cli/pw-dump/pw-link/pw-cat/pw-record 1.6.8), libpulse **17.0**
(pactl 17.0-98-gb096, protocol 35), WirePlumber **0.5.17**, Python **3.14.7**
(numpy 2.5.3), Linux **7.2.3-arch1-3**.

**Seat: SCOUT (leaf). Zero tracked-file edits. Every write is under
`corpus/live/r80-scout/` plus this report.** `corpus/fixtures/measure_audio.py`
was **dirty at entry** (sha256 `c756c6c29eb94020…`, 521096 B, mtime 01:46:19) and
**changed again at 02:13:15 during this session** (now `3ea9163af388e91a…`) —
both mutations belong to the live fold run, **not to this seat**: the file was
never read, imported or executed here, and the harness contains no import path to
`corpus/fixtures` (own tone, own classifiers, own analysis). `git status` shows
exactly two new untracked paths from this seat: `corpus/live/r80-scout/` and
`reports/round-80/`. Nothing committed; no `--probe-*` was ever invoked.

**Contention.** A sibling lane (r78-named, pid 2713802/2819738) was live for the
whole session doing the same frontier (`r78_loss_sink`, `r78_def_sink`,
`r78_fix_sink`, `r78fol_moved` + `r78fol_moved_tap` linked to the SPDIF sink).
§10 is the mandatory ledger: it names one real interference event **caused by
this seat** (a by-name module unload that destroyed the sibling's
`r78_fix_sink_2713802`) and the windows in which this seat's re-link legs put a
tone into the shared default sink.

**Instrument.** `r80_probe.py` (snap/load/unload/wav+FFT classifiers),
`probe_p1..p10` drivers, `analyze_windows.py` (window-resolved content witness).
Every leg ≥3 repetitions; per-leg receipts under `runs/<probe>/<leg>/`
(`*.cmd`, `*.stdout`, `*.stderr`) and consolidated JSON under
`corpus/live/r80-scout/receipts/`. Board snapshots at entry/exit:
`runs/00-baseline`, `01-pre-p2`, `02-post-p4`, `03-pre-p6`, `99-final`.
Scratch footprint 6.9 MB (recorded wavs trimmed; the window-analysis JSON is the
durable content witness).

---

## 0. Headline

| # | brief item | verdict | the single sharpest measured fact |
| --- | --- | --- | --- |
| 1 | `pactl load-module` family | **PINNED (cell table §1, §2)** | the plain `description=` argument is **silently dropped** (node.description stays the derived `"<sink_name> Audio/Sink sink"`) while `sink_properties=device.description=` **is** honored; `rate=99999` is accepted verbatim into `EnumFormat`; `slaves=`/`sinks=` both work but **`@DEFAULT_SINK@` in them is not expanded** → `rc=1 Failure: Input/Output error` |
| 2 | hot-unload lifecycle | **the "third mode" collapses into r79's target-loss; one genuinely new mode found** | unload the sink's module mid-play → stream **re-links to the default sink in ≤1 sample (≤110 ms), client never dies** (target-loss, not link-loss); unload a **lingering** sink's module → **the stream never notices** (link preserved, no re-link, no tone at the fallback) |
| 3 | `media.class` override / monitor / `object.linger` | **MEASURED, sharp** | `media.class=Audio/Source` turns the null sink into a **source with 0 input ports and no sink entry in pactl**; `object.linger=true` produces a **permanent orphan**: the node outlives `pactl unload-module`, keeps a **stale `pulse.module.id`**, is still listed by pactl as a sink *and* a `.monitor` source, and is reachable **only** by `pw-cli destroy` |
| 4 | `pw-cli`/`pw-link -m` vs `pactl` for linking | **MEASURED** | `pw-link <o> <i>` (linger) link **survives**; `pw-link -m <o> <i>` link **dies with the process**; `pactl move-sink-input` is **sticky** (still moved at +6 s) but is a **silent no-op under `node.dont-move=true`** (rc=0, no move) |
| 5 | `wpctl` policy surface | **BOUNDARY (cheap check done)** | `wpctl status` sees module-created sinks; `wpctl inspect` needs an **ID** (rc=1 on a name) and **never exposes `pulse.module.id`** — wpctl has no module surface at all |

---

## 1. `module-null-sink` argument lattice (`runs/p1-null-args/`, `receipts/p1-null-args.json`)

3 reps/leg, all stable unless noted. Node observed keyed by `pulse.module.id ==
returned index`, so auto-named modules are caught. **Stability:** 19 of 20 legs
give one identical semantic signature across their 3 reps (rc, stderr, and every
non-volatile node prop); the exception is `object.linger=true`, whose 3 reps
legitimately differ because each rep's orphan survives and accumulates (that
instability *is* the law). `client.id`, `object.id`, `object.serial` and port ids
are volatile by construction and were excluded from the comparison.

| leg args | rc | node.name | node.description | media.class | in/out ports | audio.position | `pactl` view |
| --- | --- | --- | --- | --- | --- | --- | --- |
| *(none)* | 0 | **`null-sink`** | `null-sink Audio/Sink sink` | `Audio/Sink` | 2/2 | `[ FL, FR ]` | sink `null-sink` + source `null-sink.monitor` |
| `sink_name=X` | 0 | `X` | `X Audio/Sink sink` | `Audio/Sink` | 2/2 | `[ FL, FR ]` | sink `X` + `X.monitor` |
| `sink_name=X description=D` | 0 | `X` | `X Audio/Sink sink` — **`D` dropped** | `Audio/Sink` | 2/2 | `[ FL, FR ]` | as above |
| `sink_name=X sink_properties=device.description=D media.class=Audio/Sink` | 0 | `X` | **`D`** — the prop **wins** | `Audio/Sink` | 2/2 | `[ FL, FR ]` | as above |
| `channels=1` | 0 | `X` | … | `Audio/Sink` | **1/1** | `[ MONO ]` | sink + monitor |
| `channels=6` | 0 | `X` | … | `Audio/Sink` | **6/6** | `[ UNK, UNK, UNK, UNK, UNK, UNK ]` | sink + monitor |
| `channel_map=mono` | 0 | `X` | … | `Audio/Sink` | 1/1 | `[ MONO ]` | sink + monitor |
| `channel_map=front-left,front-right` | 0 | `X` | … | `Audio/Sink` | 2/2 | `[ FL, FR ]` | sink + monitor |
| `channel_map=surround-51` | 0 | `X` | … | `Audio/Sink` | 6/6 | **`[ FL, FR, RL, RR, FC, LFE ]`** | sink + monitor |
| `channel_map=notachannel` | **1** | — | — | — | — | — | `Failure: Invalid argument`, **no module created** |
| `format=s16le` | 0 | `X` | … | `Audio/Sink` | 2/2 | `[ FL, FR ]` | `EnumFormat.format = S16LE` |
| `format=u8` | 0 | `X` | … | `Audio/Sink` | 2/2 | `[ FL, FR ]` | `EnumFormat.format = U8` |
| `format=not_a_format` | **1** | — | — | — | — | — | `Failure: Invalid argument` |
| `rate=44100` / `rate=96000` | 0 | `X` | … | `Audio/Sink` | 2/2 | `[ FL, FR ]` | `EnumFormat.rate = 44100` / `96000` |
| `rate=99999` | 0 | `X` | … | `Audio/Sink` | 2/2 | `[ FL, FR ]` | `EnumFormat.rate = 99999` — **no range check** |
| `media.class=Audio/Source` | 0 | `X` | **`X Audio/Source sink`** | **`Audio/Source`** | **0/1** | `[ FL, FR ]` | **no sink entry; source `X`** (not `X.monitor`) |
| `object.linger=true` | 0 | `X` | … | `Audio/Sink` | 2/2 | `[ FL, FR ]` | sink + monitor; node has **no `client.id`**, `object.linger=true` |
| `sink_properties=monitor.passthrough=false node.pause-on-idle=false` | 0 | `X` | … | `Audio/Sink` | 2/2 | `[ FL, FR ]` | both props land verbatim on the node |
| `totally.unknown.key=42` | 0 | `X` | … | `Audio/Sink` | 2/2 | `[ FL, FR ]` | unknown key **silently ignored** |
| two loads, same `sink_name` | 0 | `X` ×2 | … | `Audio/Sink` | 2/2 each | `[ FL, FR ]` | **two distinct nodes**; pactl resolves the name to **one** (the later node's `object.serial`); the other is shadowed |

### 1.1 The null-sink laws

- **Node shape is fixed**: `factory.name=support.null-audio-sink`,
  `node.driver=true`, `monitor.passthrough=true`, `monitor.channel-volumes=true`,
  `clock.quantum-limit=8192`, `node.loop.name=data-loop.0`, `port.group=stream.0`,
  `media.class=Audio/Sink`, and the pair `object.id` (global id) /
  `object.serial` (pactl index) / `pulse.module.id` (pulse module index).
  `pactl list short sinks` prints the **`object.serial`**, not the global id.
- **`node.description` is derived unless you go through `sink_properties`.**
  The default is always `"<node.name> <media.class> sink"` (note: the *class*
  string is interpolated — the `media.class=Audio/Source` leg yields
  `"X Audio/Source sink"`). The plain module argument `description=D` is an
  **unknown key** and is silently dropped (rc=0, no prop); the same value as
  `sink_properties=device.description=D` **does** land as `node.description=D`
  and wins over the derived string (measured in `runs/p2-family/null-props`).
- **`sink_properties=` is the only prop vector** (`media.class`,
  `object.linger`, `device.description`, `monitor.*`, `node.*` all land through
  it). A bare unknown key at module level is dropped.
- **`rate=`/`format=` are real but only visible in `params.EnumFormat`** — the
  node props carry no rate/format key at all, so a `pw-dump` grep on props will
  miss them.
- **`channel_map` implies `channels`** and is validated (invalid → rc=1); a
  `channels`/`channel_map` pair that disagrees (e.g. `channels=1
  channel_map=mono master_channel_map=front-left,front-right` on remap) → rc=1
  `Failure: Invalid argument`.
- **Duplicate `sink_name` is allowed** and produces two live nodes; pactl's
  name→object lookup then returns one of them (measured: the *second*), so
  `pactl`-level addressing of a duplicated name is ambiguous while `pw-dump`
  sees both.

---

## 2. The module family (`runs/p2-family/`, `runs/p8-combine-and-params/`, `runs/p9-native-namespace/`)

### 2.1 Acceptance table (3 reps/leg, stable unless noted)

| module | args | rc / stderr | nodes created (name — class — in/out) | link topology |
| --- | --- | --- | --- | --- |
| `module-null-sink` | any valid | 0 | `X` `Audio/Sink` 2/2 | none (is a sink) |
| `module-remap-sink` | *(no master)* | 0 | `X` `Audio/Sink` 2/2 + `output.X` `Stream/Output/Audio` 0/2 | `output.X → <default sink>:playback_F{L,R}` |
| `module-remap-sink` | `master=<sink>` | 0 | same pair | `output.X → <master>:playback_*` |
| `module-remap-sink` | `master=no_such_sink` | 0 | same pair | **falls back to the default sink** |
| `module-remap-sink` | `channels=1 channel_map=mono master_channel_map=front-left,front-right` | **1** `Failure: Invalid argument` | — | — |
| `module-remap-source` | `master=@DEFAULT_SOURCE@` | 0 | `X` `Audio/Source` 0/2 + `input.X` `Stream/Input/Audio` **0/0** | **none** (master source was SUSPENDED/IDLE in this host state) |
| `module-combine-sink` | `slaves=<literal sink>` | 0 | `X` `Audio/Sink` 2/2 + **one `output.X_<slavename>` per slave** 0/2 | each branch → its slave's `playback_*` |
| `module-combine-sink` | `sinks=<literal sink>` | 0 | identical to `slaves=` | identical |
| `module-combine-sink` | `slaves=A,B` | 0 | two branches | both linked |
| `module-combine-sink` | `slaves=@DEFAULT_SINK@` | **1** `Failure: Input/Output error` | — | — (same for `sinks=@DEFAULT_SINK@`) |
| `module-combine-sink` | *(no slaves)* | 0 | `X` + **one branch per sink in the system at load time** (foreign + orphan sinks included) | branch per sink |
| `module-combine-sink` | `+ latency_compensate=false` / `remix=no` / `adjust_time=1` | 0 | unchanged | unchanged (`adjust_time` is ignored by design — the module ships the string *"The `adjust_time` modarg is ignored"*) |
| `module-echo-cancel` | `aec_method=webrtc\|null`, explicit masters | 0 | `X` `Audio/Sink` 2/2, `Xs` `Audio/Source` 0/2, `echo-cancel-capture` `Stream/Input/Audio` **2/2**, `echo-cancel-playback` `Stream/Output/Audio` 0/2 | capture ← master source's `monitor_*`; playback → master sink's `playback_*` |
| `module-echo-cancel` | `sink_master=no_such source_master=no_such` | 0 | same 4 nodes, but capture is **0/0** | playback → **default sink** (fallback); capture **unlinked** |
| `module-echo-cancel` | `aec_method=nosuchmethod` | **1** `Failure: No such entity` | — | — |
| `module-loopback` | `source=X.monitor sink=X` | 0 | `input.loopback-<pid>-<n>` `Stream/Input/Audio` 2/2 + `output.loopback-<pid>-<n>` `Stream/Output/Audio` 0/2 | **both sides are real graph links** (`X:monitor_*→input.…`, `output.…→X:playback_*`) |
| `module-virtual-sink` | `sink_name=X` | 0 | `input.X` `Audio/Sink` 2/2 + `output.X` `Stream/Output/Audio` 0/2 | `output.X → <default sink>:playback_*` |
| `module-virtual-source` | `source_name=X` | 0 | `output.X` `Audio/Source` 0/2 + `input.X` `Stream/Input/Audio` 2/2 | none |
| `module-pipe-sink` | `file=<path>` | 0 | `X` `Audio/Sink` 2/2 | **creates the FIFO** (`mode 0o10666`) and **removes it on unload** |
| `module-always-sink` | *(2nd instance)* | **1** `Failure: Entity exists` | — | — |
| `module-does-not-exist` | — | **1** `Failure: No such entity` | — | — |
| `libpipewire-module-*` | via **pactl** | **1** `Failure: No such entity` | — | — (pactl's namespace is pulse-only) |

Refusal shapes are typed and stable: `Failure: Invalid argument` (bad value),
`Failure: No such entity` (unknown module / unknown aec_method / dead index),
`Failure: Entity exists` (duplicate singleton), `Failure: Input/Output error`
(unexpandable `@DEFAULT_*@` inside a slave list), `Failure: Access denied`
(index below the pulse base).

### 2.2 Shape taxonomy (what the module *is*)

- **null-sink** = one node, `support.null-audio-sink` factory, `node.driver=true`.
- **remap / combine / echo-cancel / virtual-*** = one client with **2–N nodes**,
  all sharing one `client.id`; the module's own `output.<…>` / `input.<…>`
  streams are **real graph nodes with real links** (contrast r79's `pw-loopback`,
  whose pair has *no* inter-node link — the copy is in-client; the same is true
  here: `module-loopback`'s two nodes are linked only to their *external*
  endpoints, never to each other).
- **Grouping props**: combine sets
  `node.group = node.link-group = combine-sink-<pulse-server-pid>-<n>`,
  echo-cancel sets `… = echo-cancel-<pid>-<n>`; both set `node.virtual=true`,
  `node.autoconnect=true`. `node.description` for combine is the **raw
  `sink_name`** (unlike null-sink's derived string).
- **Combine branch naming is deterministic**: `output.<sink_name>_<slave_name>`.

---

## 3. Module index namespace + the unload argument matrix

### 3.1 Allocation law — **LIFO free-list** (`runs/p5-index-law/`, `receipts/p5-index-law.json`)

Measured 3/3 (the *first* of the four loads differs between rep 0 and reps 1–2
because the previous rep's cleanup freed indices in a different order — which is
itself the LIFO law showing through):

```
live dynamic modules at start = {…, 915, 923, 929}
rep 0   load ×4  -> 922, 921, 920, 919     (fills the free gap downward)
rep 1/2 load ×4  -> 919, 922, 921, 920     (919 was the last index freed by rep 0's cleanup)
any rep unload a1 (921) ; load -> 921      (reuse = the just-freed index)
        unload a3 (919) ; load -> 919
        unload a0 (922) ; load -> 922
```

The same law explains the p4 run independently (fresh allocation walks *up* when
the free list is empty: 924…929; after a batch unload the *last-freed* index
comes back first: 929). Consequences for an arm table:

- **Indices are recycled aggressively.** Any index you read is only valid while
  the module is alive; the next `load-module` *anywhere on the host* (including
  another seat's) can take that index.
- **`pulse.module.id` is a stamp, not a handle.** A lingering orphan keeps
  `pulse.module.id=0x20000005` forever (§5); a later module can own the same
  index, so a `pulse.module.id` read off a node is **not** proof of ownership.
- Index base `0x20000000`; the four pre-loaded singletons occupy
  `0x20000000…0x20000004` (`module-always-sink`, `module-device-manager`,
  `module-device-restore`, `module-stream-restore`).

### 3.2 Unload argument matrix (3 reps/leg, `runs/p5-index-law/`)

| argument | module state | rc | stderr | effect |
| --- | --- | --- | --- | --- |
| `<index>` | live | 0 | — | **unloaded** |
| `<index>` | dead | **1** | `Failure: No such entity` | — |
| `#<index>` | live | **0** | `Failed to unload module: Module #<index> not loaded` | **NO-OP — the module stays loaded** |
| `#<index>` | dead | **0** | same message | no-op |
| `<index below base>` (536870000) | — | **1** | `Failure: Access denied` | — |
| `<huge index>` (999999999) | — | **1** | `Failure: No such entity` | — |
| `<arbitrary string>` | — | **0** | `Failed to unload module: Module <str> not loaded` | **NO-OP, rc=0** |
| `module-null-sink` (a *name*) | 1..N instances | **0** | — | **unloads EVERY module with that name — including foreign ones, with no warning** |

**Arm on effect, never on rc.** Two of these forms return rc=0 while doing
nothing, and one returns rc=0 while destroying other lanes' modules.

### 3.3 Two disjoint module namespaces (`runs/p9-native-namespace/`, `runs/p10-client-scope/`)

| namespace | id space | loader | unloader | visible to pactl? |
| --- | --- | --- | --- | --- |
| **pulse** (`module-null-sink`, …) | `0x20000000+n` | `pactl load-module` | `pactl unload-module <n>` | yes (`pactl list modules`) |
| **native** (`libpipewire-module-*`) | small ints 1..22 | `pw-cli load-module` | `pw-cli unload-module <var>` | **no** — a native name through pactl is `No such entity` |

- `pw-cli load-module libpipewire-module-null-audio-sink` → **rc=0 with
  `Error: "Could not load module"` on stderr** — pw-cli's rc is not a verdict
  (the module does not exist; `support.null-audio-sink` is a **SPA factory**,
  not a PipeWire module).
- `pw-cli create-node adapter '{ factory.name=support.null-audio-sink
  node.name=X media.class=Audio/Sink }'` → rc=0, node exists **only while the
  pw-cli client lives**; with **`object.linger=true`** the node survives the
  client's exit and **pactl then lists it as a sink**. `object.register=false`
  makes pw-cli die with `Broken pipe` (rc=0).
- A **pactl** module's node outlives the pactl process by design (server-owned).
- **`pw-cli destroy <node-id>` kills the owning pulse module too**: destroying a
  null sink's node natively leaves the sink **not re-created** and the module
  **gone** (`pactl unload-module <that index>` then says `No such entity`). The
  module is a *view over a node*, not a container.

---

## 4. Hot-unload lifecycle — destruction modes (`runs/p6-lifecycle/`, `receipts/p6-lifecycle.json`, `receipts/p6-window-analysis.json`)

Instrument: a 100 ms `pw-dump` sampler (nodes + every link touching the probe
names) plus a **default-sink-monitor recorder** as the content witness, split at
the action boundary into PRE `[0,1.5 s)` and POST `[1.65 s, 4 s)`. All legs ×3.
**Every leg's recorder was re-pointed at the default sink at spawn and linked to
the SPDIF sink in all 21 legs** — that is the internal witness that the shared
default sink did not move under a leg (§10 item 3).

| leg | action at t≈1.5 s | stream after | links after | POST window (default-sink monitor) | class |
| --- | --- | --- | --- | --- | --- |
| **L1** unload the sink's module | `pactl unload-module <idx>` | **alive, never exits** (3/3) | `play:output_* → <default sink>:playback_*` **within the first 110 ms sample** | 3/3: pre peak 0 → post peak **819**, `L@1000 = 819.1`, `R@1500 = 819.0`, cross-terms 0.0 → **the tone arrives at the fallback** | **target-loss → fallback re-link** (r79 law, now on the *sink* side) |
| **L2** r78 control: `pw-link -d` the live link | manual disconnect (2 links, rc=0), target alive | **alive, never exits** (3/3) | **none** — the sink node and the stream both survive, the link does not | 3/3: post peak **0**, all bins **0.0** | r78's *invisible link loss* reproduced |
| **L3** L1 + `node.dont-move=true` on the player | `pactl unload-module` | alive (3/3) | **re-links to the default sink anyway** | 3/3: post bins `819.1/819.0` (peak 9010 = the transient in §4.2) | **`node.dont-move` does NOT protect against target death** |
| **L4** capture stream on the sink's monitor | `pactl unload-module` | recorder runs to its `-n` bound (rc=1 = normal finalize) | `SPDIF:monitor_* → rec:input_*` within 110 ms (3/3) | 3/3: bins ≈ 0.2–1.3 → **no tone** (nothing was playing into the fallback) | the capture side follows the same fallback |
| **L5** unload the **master** of a remap-sink | `pactl unload-module` (master) | player alive, still linked to the remap sink `rm5` (3/3) | the module's own `output.rm5` **re-links from the master to the default sink** within 110 ms (3/3) | 3/3: post bins 784–819 at 1000/1500 Hz | the law holds **for a module's internal stream**, not just client streams |
| **L6** unload a **lingering** sink's module | `pactl unload-module` | alive (3/3) | **unchanged — `play:output_* → ns6:playback_*` survives the unload** (3/3, same port ids) | 3/3: bins ≈ 0.6–1.5 → **no tone at the fallback** | **the fourth mode: module death is a graph no-op** |
| **L7** `pw-cli destroy <sink node-id>` while playing | native destroy (rc=0) | alive (3/3) | re-links to the default sink within 110 ms (3/3) | 3/3: post bins 819.0–819.7 | **native destruction ≡ module unload** for the stream; and it takes the module with it |

### 4.1 The laws

- **Module unload of a live target is target-loss, not link-loss.** The consumer
  never dies and never errors; WirePlumber re-links it to the **current default
  sink** inside one 110 ms sample. There is **no third destruction class** on
  this path — r78's `pw-link -d` (link loss, silent zeros) and r79's target loss
  cover it. The *new* distinction is that the target's disappearance is now
  caused by the **pulse module's death**, and it is still routed as target-loss.
- **`object.linger=true` is the only way to make module unload invisible to the
  graph** (L6): the node outlives its module, so nothing is lost and the
  consumer keeps its link. This is the arm-able knob for "unload without
  disturbing a running stream".
- **`node.dont-move` is a session-manager hint, not a lifecycle guard.** It
  blocks a `pactl move-sink-input` (§6) but not the fallback re-link (L3).
- **Fallback asymmetry persists** (echo-cancel, §2): an unresolvable *sink*
  master falls back to the default sink; an unresolvable *source* master leaves
  the capture node with **no ports at all** — the same one-sided fallback r78
  found for `pw-record`.

### 4.2 An unattributed transient (weakest claim — do not arm without a re-measure)

A ≈0.5 full-scale excursion (peak **8192–9010**, i.e. 10× the tone) appears in
**15 of the 21 legs** — in the PRE window as often as in the POST window, with
**no correlation to the leg class** (L1 is clean in all 3 reps: pre 0, post
exactly 819; L2 and L6 have no re-link at all yet still show it). It is therefore
**not attributable to the module-unload path**. The two candidate sources, both
plausible and neither excluded: (a) the **recorder's own monitor link-up**
transient (it links to the default sink's monitor ~0.1 s into every recording,
i.e. inside the PRE window), and (b) **foreign node churn on the shared default
sink** — the sibling lane was creating and destroying sinks throughout (§10).
A 10 ms sampler plus a *dedicated* sink (never the shared default) is required
before this becomes an arm-able row.

---

## 5. `media.class` override, monitor sources, `object.linger` (`runs/p3-linger-orphans/`)

### 5.1 `media.class` override is a real class change, not decoration

`pactl load-module module-null-sink sink_name=X media.class=Audio/Source`
(or `sink_properties=media.class=Audio/Source`) yields a node with
`media.class=Audio/Source`, **0 input ports / 1 output port**, description
`"X Audio/Source sink"`, and pactl exposes it as a **source named `X`** with
**no sink entry and no `X.monitor`**. Nothing can be played into it; it is a
silent source. There is **no monitor-source synthesis for it** (the `.monitor`
suffix is a pactl-side alias generated for `Audio/Sink` nodes only).

### 5.2 `object.linger=true` — the permanent orphan

Measured (3/3, and independently 3/3 via `sink_properties=object.linger=true`):

```
pactl load-module module-null-sink sink_name=r80_p1_lng object.linger=true   -> rc=0 idx=0x20000005
  node: object.linger=True, client.id=ABSENT, pulse.module.id=0x20000005
pactl unload-module 0x20000005                                              -> rc=0  (module gone)
  node: STILL THERE — object.linger=True, client.id=ABSENT, pulse.module.id=0x20000005
pactl list short sinks   -> ... 76263  r80_p1_lng  PipeWire float32le 2ch 48000Hz SUSPENDED
pactl list short sources -> ... 76263  r80_p1_lng.monitor ...
pactl unload-module 0x20000005                                              -> rc=1 Failure: No such entity
pw-cli destroy 214                                                          -> rc=0, node gone
```

Laws:

- **`object.linger=true` removes the client binding** (`client.id` absent) and
  makes the node survive its owning module.
- The orphan keeps a **stale `pulse.module.id`**; because indices are recycled
  (§3.1) that stamp can later point at a *different, live* module.
- **pactl still lists the orphan as a sink and as a `.monitor` source**, and
  those names are usable (`pw-record --target X.monitor` with
  `stream.capture.sink=true`, `pw-cat --target X`) — the orphan is a
  first-class route target with **no module to unload**.
- **The only destruction path is native**: `pw-cli destroy <node-id>` (rc=0).
  `pactl` has no reach into it at all.
- On a **stream** node the same prop does **not** extend life: a `pw-cat`
  client's node carries `object.linger=true` and a live `client.id` while
  running, and is **gone after the client exits** (3/3). Linger protects
  *server-created* objects, not client-owned ones.

---

## 6. Link authority — who creates links, who tears them down (`runs/p7-linkauthority/`)

| creator | form | link survives? | note |
| --- | --- | --- | --- |
| `pw-link <out> <in>` | default `-L/--linger` | **yes** — present immediately and still present at +2 s (3/3) | WirePlumber does **not** reap it |
| `pw-link -m <out> <in>` | monitor mode (non-linger) | **no** — present while `pw-link -m` runs, **gone after it is killed** (3/3) | the link is the client's |
| `pactl move-sink-input <sink-input-idx> <sink>` | pulse reroute | **sticky** — moved at +1 s, +3.5 s and **+6 s** (3/3) | rc=0; not the "temporary move" the `temporary_move_target_timeout` symbol suggests for the *unload* path |
| `pactl move-sink-input` on a stream with **`node.dont-move=true`** | pulse reroute | **silent no-op** — rc=0, links unchanged (3/3) | prop confirmed on the node via `pw-dump` *and* via `pactl -f json list sink-inputs` |
| `pactl` | *no link command at all* | — | pulse's only topology verb is `move-*` |

Index spaces seen in this round (three different ones, easy to confuse):
`pactl` **sink/source index = `object.serial`** (e.g. 76263, 58253),
**sink-input index = the stream node's `object.serial`** (e.g. 82574),
**module index = `0x20000000+n`**.

---

## 7. `wpctl` surface (boundary — cheap check only)

- `wpctl status` → rc=0, **sees module-created sinks** by name (r80_q_w1 present).
- `wpctl inspect <name>` → **rc=1** (usage error): inspect takes an **ID**.
- `wpctl inspect <id>` output contains **no `pulse.module.id`** — wpctl has no
  module concept at all (it is the WirePlumber view: nodes/devices/settings).
- `wpctl settings` → rc=0, lists policy keys (`node.stream.restore-props`, …).

**Boundary:** wpctl exposes nothing about pulse modules that pactl does not, and
nothing about the module↔node lifetime. No further wpctl probing is in scope
for this frontier.

---

## 8. Proposed arm table (verbatim-armable rows + expected signature)

Each row: command → expected `rc` / stderr → expected graph → expected content
signature. All rows measured ≥3× on this host; the *signature* column is what a
test should assert (never rc alone).

| # | arm | expected rc / stderr | expected topology | expected signature |
| --- | --- | --- | --- | --- |
| A1 | `pactl load-module module-null-sink sink_name=<n>` | 0 / — | node `<n>` `Audio/Sink` 2/2, `node.description="<n> Audio/Sink sink"`, `pulse.module.id=<idx>` | `pactl list short sinks` has `<n>`; `pactl list short sources` has `<n>.monitor` |
| A2 | same + plain `description=D` | 0 / — | `node.description` **≠ D** (derived string) | lie row; the `sink_properties=device.description=D` route *does* land and is a different row |
| A2b | same + `sink_properties=device.description=D` | 0 / — | `node.description == D` | prop wins over the derived string |
| A3 | same + `rate=99999` | 0 / — | `params.EnumFormat[0].rate == 99999` | props have **no** rate key |
| A4 | same + `channel_map=notachannel` | 1 / `Failure: Invalid argument` | **no node** | module list unchanged |
| A5 | same + `media.class=Audio/Source` | 0 / — | node `Audio/Source` **0/1** | pactl: source `<n>`, **no sink, no `.monitor`** |
| A6 | same + `object.linger=true` | 0 / — | node with `client.id` absent | after `unload-module <idx>`: node **still present**, `pactl unload-module <idx>` → **rc=1 `No such entity`**, `pw-cli destroy <node>` → gone |
| A7 | `pactl unload-module <idx>` (live) | 0 / — | node gone | module list loses `<idx>` |
| A8 | `pactl unload-module #<idx>` (live) | **0** / `Failed to unload module: Module #<idx> not loaded` | **node still present** | module list **unchanged** (no-op lie row) |
| A9 | `pactl unload-module <dead idx>` | 1 / `Failure: No such entity` | — | — |
| A10 | `pactl unload-module <arbitrary string>` | **0** / `Failed to unload module: Module <str> not loaded` | nothing changes | no-op lie row |
| A11 | `pactl unload-module module-null-sink` | 0 / — | **every** null-sink module on the host unloads, foreign ones included | **never arm this on a shared host** |
| A12 | `pactl load-module module-combine-sink sink_name=<n> slaves=<literal sink>` | 0 / — | `<n>` 2/2 + `output.<n>_<slave>` 0/2 → `<slave>:playback_*` | branch name is deterministic |
| A13 | … `slaves=@DEFAULT_SINK@` | **1** / `Failure: Input/Output error` | **no node** | `@DEFAULT_*@` is not expanded in slave lists |
| A14 | `pactl load-module module-combine-sink sink_name=<n>` (no slaves) | 0 / — | one branch **per sink present at load time** | branch count = `pactl list short sinks` count |
| A15 | `pactl load-module module-remap-sink sink_name=<n> master=no_such` | 0 / — | `output.<n>` → **default sink** | fallback row |
| A16 | `pactl load-module module-echo-cancel sink_name=<s> source_name=<r> aec_method=nosuchmethod` | 1 / `Failure: No such entity` | no nodes | — |
| A17 | `pactl load-module module-pipe-sink sink_name=<n> file=<path>` | 0 / — | `<n>` `Audio/Sink`; **FIFO exists (0o10666)** | after unload the **FIFO is removed** |
| A18 | `pactl load-module libpipewire-module-*` | 1 / `Failure: No such entity` | — | namespace separation row |
| A19 | unload a playing stream's target module (L1) | 0 / — | stream re-links to the **default sink** | default-sink monitor POST window: peak 819, `L@1000≈819.1`, `R@1500≈819.0`, cross≈0 |
| A20 | same, target loaded with `object.linger=true` (L6) | 0 / — | **link unchanged** | POST window peak **0** (and the sink node still exists) |
| A21 | same, player with `node.dont-move=true` (L3) | 0 / — | re-links anyway | POST window tone present |
| A22 | `pw-link -d <link-id>` on a live link (L2) | 0 / — | no links | POST window peak **0** (link-loss is invisible) |
| A23 | `pw-cli destroy <sink-node-id>` while playing (L7) | 0 / — | re-link to default sink; **pulse module gone** | `pactl unload-module <idx>` afterwards → `No such entity` |
| A24 | `pw-link <out> <in>` then wait 2 s | 0 / — | link **persists** | `pw-link -l` shows it |
| A25 | `pw-link -m <out> <in>` then kill it | 0 / — | link **disappears with the process** | `pw-link -l` empty |
| A26 | `pactl move-sink-input <idx> <other sink>` | 0 / — | link moves and **stays** (≥6 s) | links point at `<other sink>` |
| A27 | A26 on a `node.dont-move=true` stream | **0** / — | **no move** | links unchanged (silent no-op row) |

---

## 9. Falsification list (what would prove each claim wrong)

1. **"`description=` is dropped"** — a `pw-dump` on this host showing
   `node.description == <given description>` for a `module-null-sink` load with
   the **plain** `description=` argument. (Would falsify §1's
   derived-description law. Note the *prop* route
   `sink_properties=device.description=D` **is** honored and is a separate row —
   do not confuse the two.)
2. **"`object.linger` orphans survive module unload"** — an unload that removes
   the node, or an orphan that `pactl` cannot list. (Would falsify §5.2.)
3. **"the orphan is unreachable via pactl"** — any `pactl unload-module` form
   that removes a lingering orphan with rc=0 *and* effect.
4. **"module unload → fallback re-link"** — a leg in which the stream exits,
   errors, or stays unlinked for >1 s. (Would falsify §4.1; L2 is the control
   that shows the *link-loss* class is different.)
5. **"`node.dont-move` does not stop the fallback re-link"** — a L3 leg with
   POST peak 0 and no new link. (Also check the prop really landed: `pw-dump`
   must show `node.dont-move=true`.)
6. **"index allocation is LIFO"** — a sequence in which a load after a *single*
   unload returns an index other than the just-freed one while other indices are
   free. (p4's step-3 result is explained by LIFO; a counterexample kills §3.1.)
7. **"`#N` never unloads"** — any `#N` unload that removes a live module.
8. **"the name form unloads every instance"** — a `unload-module module-null-sink`
   that leaves another null-sink module alive. (This is the dangerous row; it was
   observed *once* under §10 conditions and is also the one place this seat
   disturbed a foreign module.)
9. **"`@DEFAULT_*@` is not expanded in `slaves=`"** — a combine load with
   `slaves=@DEFAULT_SINK@` that succeeds on another host/build.
10. **"the re-link transient exists"** — a 10 ms-resolution re-measure, on a
    **dedicated** sink (not the shared default), showing no 8192–9010 excursion
    at the re-link instant. §4.2 is explicitly **unattributed**: the excursion
    appears in 15/21 legs in both windows with no leg-class correlation, so it
    may be the recorder's own link-up or a foreign lane's churn rather than the
    unload path. Do not arm a click row on this evidence.
11. **"`pw-link -m` links die with the process"** — a `-m` link that outlives
    its creator.

---

## 10. Contention ledger (mandatory)

**Foreign state at entry** (`runs/00-baseline`, 01:54Z): 11 nodes — 4 ALSA
sinks/sources, Dummy/Freewheel drivers, Midi-Bridge, bluez_midi, plus a
**sibling-owned null sink `r78p_check`** (pulse module `0x20000004`, i.e.
536870916). Default sink `…HiFi__SPDIF__sink`, default source
`…HiFi__Line__source`. Clients: WirePlumber (33, 43), xdg-desktop-portal (32),
portal-hyprland (40), pipewire (211, 230), waybar (226).

**A live sibling lane was probing the same frontier** for the whole session.
Observed in this seat's receipts: sinks `r78_def_sink_2713802`,
`r78_loss_sink_2713802`, `r78_fix_sink_2819738`, `r78_prop_a_2713802`,
`r78_prop_b_2713802`; a `pw-record … -P node.name=r78loss_unload_tap --target
<SPDIF sink>` process (pid 2854096, `/tmp/capture-r78-loss-…/tap_unload_default.wav`);
and `r78fol_moved` / `r78fol_moved_tap` **linked to the SPDIF sink**
(`pw-link -l`, 02:04Z). Its default-sink experiments mean the host's default
sink is not exclusively this seat's to rely on — every leg in §4 therefore
records the actual link target, and the recorder was re-pointed at the default
sink at the start of **each** leg (all 21 legs resolved it to the SPDIF sink,
which is the internal witness that the default did not move under a leg).

### Interference events

1. **Caused by this seat (disclosed, not repaired):** at ~02:0xZ the p4
   `unload-module module-null-sink` (by-name form) destroyed **every** module
   named `module-null-sink` on the host, including the sibling's
   `r78_fix_sink_2713802` and the stale `r78p_check`. `r78p_check` is the only
   node that is **missing at exit** (`runs/99-final`: `gone since baseline =
   ['r78p_check']`); the sibling's `r78_fix_sink_*` reappeared within minutes
   under a new pid, which is why that lane may have seen one failed leg. No
   further by-name unload was issued after this discovery; §3.2/§9.8 record it
   as a law *and* a hazard.
2. **Also caused by this seat:** `pactl unload-module 536870915
   (module-stream-restore)` succeeded (rc=0, no protection, no auto-respawn) in
   the p4 static-module leg. It was **reloaded at 02:0xZ**
   (`pactl load-module module-stream-restore` → index 536870915) and is present
   in `runs/99-final`.
3. **Shared default sink:** the §4 re-link legs (L1, L3, L5, L7 — 12 of 21
   legs) deliberately route a 1 kHz/1.5 kHz dual tone into the **shared SPDIF
   sink** for the remainder of each 4 s window, at `--volume 0.05` (peak 819).
   That is a real, disclosed disturbance of any concurrent SPDIF-monitor
   recording — including the sibling's `r78loss_unload_tap`, whose window
   overlaps L1/L3/L5/L7. Attribution is safe in *this* seat's direction because
   the tone's bin amplitude is exactly 819.1/819.0 (its own volume signature),
   but the reverse attribution is **not**: the sibling's recordings in those
   windows contain this seat's tone.
4. No other seat's module index, node or link was touched, and no `--probe-*`
   was run on `measure_audio.py`.
5. **Observed in the other direction (not caused by this seat):** in p2's
   `module-loopback` reps 1 and 2 a **foreign stream** appeared linked into this
   seat's loopback input node —
   `r78prop_class_source_stall:216→input.loopback-761930-13:187` and the same
   for the second channel. A `module-loopback` / `module-virtual-*` input node
   is a valid autoconnect target for any client's stream on the host, so a
   probe-owned loopback can silently capture another lane's audio (and, read the
   other way, another lane's probe can be routed into this seat's node). Any
   loopback-based measurement should tag and assert its producers (§1's
   `pw-link -l` producer-set witness) rather than assume exclusivity.

**Exit state** (`runs/99-final`, 02:2xZ): 10 nodes (baseline minus `r78p_check`),
**zero** `r80*` nodes, zero `r80*` modules, only the four static pulse modules
loaded (`module-always-sink`, `-device-manager`, `-device-restore`,
`-stream-restore` — the last restored by this seat), no FIFO left behind
(`tmp/r80_p9.fifo` removed by its own module unload). Scratch **6.9 MB**
(per-leg receipts + the 21-leg lifecycle JSON; the recorded wavs were trimmed and
the window analysis JSON kept as the durable content witness). One foreign module
(`r78_prop_a_2981439`, sibling-owned) was live at exit and was not touched.

---

## 11. Receipts index + remaining unknowns

**Receipts** (all under `corpus/live/r80-scout/`):

> **Harness fault, disclosed.** §4 was first executed as four partial runs
> (`p6b/c/d.log`); the JSON of the first two was overwritten by the later ones,
> so the whole battery was re-executed in a single run. The first re-execution
> was **void** — the footprint trim had deleted `tmp/r80_tone.wav`, so every
> player exited immediately (no stream nodes at all; every window peak 0). That
> void run was discarded, the tone regenerated, and the battery re-run; the
> `p6-lifecycle.json` referenced below is the third, valid execution. Verifiers
> should read `p6full2.log` (valid) and ignore `p6full.log` (void) — the log
> names encode this, and the void log is kept rather than deleted so the
> discrepancy can be audited.

| probe | consolidated JSON | per-leg dirs |
| --- | --- | --- |
| P1 null-sink args | `receipts/p1-null-args.json` | `runs/p1-null-args/<leg>/{load,unload}.{cmd,stdout,stderr}` |
| P2 module family | `receipts/p2-family.json` | `runs/p2-family/<leg>/` |
| P3 linger orphans | `receipts/p3-linger-orphans.json` | `runs/p3-linger-orphans/` |
| P4 index (first pass) | `receipts/p4-index.json` | `runs/p4-index/` |
| P5 allocation + unload matrix | `receipts/p5-index-law.json` | `runs/p5-index-law/` |
| P6 lifecycle | `receipts/p6-lifecycle.json` (all 7 legs × 3 reps, one run) | `runs/p6-lifecycle/<leg>/` + `p6full2.log` (per-sample link traces) |
| P6 content witness | `receipts/p6-window-analysis.json` (21 legs, regenerated from the same run) | — |
| P7 link authority | `receipts/p7-linkauthority.json` | `runs/p7-linkauthority/` |
| P8 combine/params | `receipts/p8-combine-and-params.json` | `runs/p8-combine-and-params/` |
| P9 native namespace + FIFO | `receipts/p9-native-namespace.json` | `runs/p9-native-namespace/` |
| P10 client scope | `receipts/p10-client-scope.json` | `runs/p10-client-scope/` |
| board snapshots | `runs/00-baseline`, `01-pre-p2`, `02-post-p4`, `03-pre-p6`, `99-final` | `ledger.json`, `pw-dump.json`, `pactl-*.txt` |

**Remaining unknowns (named, not guessed):**

1. **`module-remap-source` produced an unlinked `input.X` (0/0)** with
   `master=@DEFAULT_SOURCE@` — is that a fallback-asymmetry law (source side
   never falls back) or an artifact of the default source being SUSPENDED? P8's
   echo-cancel leg proves the *capture* side links when the master is a
   **monitor of a running sink**; the source-side case needs a RUNNING default
   source to decide.
2. **`description=` loss mechanism** — is `device.description` set on the
   *device* object (not probed) and merely shadowed on the node? The probe
   asserted `node.description` only.
3. **The `temporary_move_target_timeout` symbol** — `pactl move-sink-input` is
   sticky in my measurement (3/3, ≥6 s); the "temporary" path must be a
   different trigger (likely the *unload* path in `pipewire-pulse`), not probed.
4. **`#N` unload semantics** — the mechanism (pactl-side name lookup vs server
   index path) is not resolved; only the observable no-op is measured.
5. **Re-link latency floor** — 110 ms is the sampler's resolution, not the
   engine's; a 10 ms sampler would give the true bound (and would settle the
   click question in §4.1).
6. **`wpctl`** — no module surface found; if the r80 author needs WirePlumber
   policy (`node.stream.restore-props`, `default-nodes`), that is a separate
   frontier, not this one.

---

*Seat output only. No edits to tracked files, no commits, no judgment passed on
any other lane's work; the canonical Rust runtime remains the sole judge.*
