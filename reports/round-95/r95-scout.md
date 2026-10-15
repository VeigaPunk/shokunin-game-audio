# R95 scout — JACK↔PipeWire interop (`pipewire-jack` 1.6.8), measured with an own JACK client

Round 95 pre-measurement. Host `plazir27`, measured **2026-10-15 16:30–17:55 local (UTC−3)
= 19:30–20:55Z**. Repo `~/Projects/shokunin/audio-shokunin` @ entry HEAD **`2333fac`**,
exit HEAD **`58e45e9c`** (sibling commits moved it: `cdacdc43 r94 scout: SoX_ng DSP
lattice`, `58e45e9c r83 boundary` — neither is this surface; r93 was the ebur128
filter-graph node, r94 SoX_ng file DSP, so JACK was not in flight elsewhere).
Tracked-dirty at entry/exit is the sibling-owned `corpus/fixtures/measure_audio.py`
(+ its `.pyc`), never read/imported/executed here; own synth, own Goertzel, own harness.
Toolchain: PipeWire **1.6.8** (`1:1.6.8-1`), **pipewire-jack `1:1.6.8-1`**,
WirePlumber 0.5.17-1, Python 3.14.7, gcc 16.1.1, Linux 7.2.3-arch1-3.

**Seat: SCOUT (leaf). Zero tracked-file writes; the only file written outside
`corpus/live/r95-scout/` is this report.** Every child is triple-bounded (element bound
in argv + wall cap + byte cap; `start_new_session` + `os.killpg`, `RLIMIT_CORE=0`).
Seat-owned names only (`r95s_*`, JACK client names `r95s_*`); modules are unloaded by
id after a name check; **no `pactl set-default-*` was ever issued**. One disclosed
host-state mutation (the `clock.force-quantum` metadata arm, §6.4) was restored and
verified 3/3. Final census: **0 `r95s` nodes, 0 `r95s` modules, 0 seat processes,
defaults unchanged**; 4 permanent `stream-properties` rows remain (§11, r90 class).

**Label legend.** `[O]` = directly observed on this host in this window (probe output
or on-disk read). `[I]` = read from the version-matched upstream source fetched over
the network (URLs + shas in `sources/`) or inferred from measured laws. `[?]` = not
resolved by this seat.

---

## 0. Why this surface (the pick, and what it displaces)

The brief's priority-1 surface is **JACK↔PipeWire interop if available**. It is
available, but not in the shape the brief names: `jackd`/`jack_lsp`/`jack_connect` are
**absent** (no jack2 package), while **`pipewire-jack 1:1.6.8-1` is installed** — the
host's *only* `libjack.so` is PipeWire's reimplementation, with `pw-jack(1)`,
`jack.conf`, and the full JACK client headers. r90 explicitly named this gap
("pw-jack and PipeWire metadata objects were not exercised either") and no round since
has taken it. r93 (ebur128) and r94 (in flight) are elsewhere; r82 ffmpeg↔PW, r81
gst↔PW, r92 filter-chain are all *other* client surfaces.

So this seat measures **the JACK client ABI as a PipeWire client surface**, with an
own C client (`probes/r95jack.c`, linked `-ljack` against the PipeWire libjack — no
`pw-jack` wrapper needed on this host, §2.3) and byte-level witnesses in both
directions. Headline: **the interop works end-to-end and byte-exactly in both
directions, but three JACK API families (xrun accounting, RT-priority accessors,
transport control) are broken or non-functional projections, and the period-size law
is inverted relative to JACK semantics.**

---

## 1. Headline claims

| # | claim | label | sharpest single fact | evidence |
| --- | --- | --- | --- | --- |
| 1 | **There is no JACK server: the "server" is the PipeWire daemon and a JACK client is a native PW client node.** | `[O]` | `jackd`/`jack_lsp` absent, `jack2` not installed, the only `libjack` is pipewire-jack's (`libjack.so.0.3.1608`, sha `34bbb09a…`); a live JACK client appears in `pw-dump` as `client.api="jack"`, `client.name="r95s_shape"`, `application.name="r95jack"`, with node `node.group="group.dsp.0"`, `media.category="Duplex"`, `media.role="DSP"`, **`node.always-process=true`** | `receipts/a_avail.json`, `receipts/b_shape.json` (`graph`), §2/§3 |
| 2 | **JACK ports become PW ports with an alias triple, and two of the five JACK port flags survive.** | `[O]` | JACK port `out` → PW port `port.name="out"`, `port.alias="r95s_shape:out"`, `object.path="r95s_shape:output_0"`, `format.dsp="32 bit float mono audio"`; `JackPortIsPhysical`→`port.physical=true`, `JackPortIsTerminal`→`port.terminal=true`, **`JackPortCanMonitor`→no prop at all** (and `port.extra` empty) | `receipts/b_shape.json` (`pw_ports`), §3.2 |
| 3 | **A JACK client sees the *whole* graph and can link any native PW port — but only by the JACK-rendered name, not by the native `node.name:port` name.** | `[O]` | `jack_get_ports(NULL,NULL,0)` = 71 ports (41 outputs, 30 inputs, 17 physical, 67 dsp) 3/3; `jack_connect("r95s_shape:out","r95s_ns Audio/Sink sink:playback_MONO")` → **rc 0 + link present**; the same port by its native name `r95s_ns:playback_MONO` → **not found, rc 22 (EINVAL)** 3/3; with `jack.fill-aliases=true` the alias `r95s_ns:playback_0` resolves and links (rc 0) | `receipts/b_shape_xconnect.json` (arms `rendered`/`native`/`fillalias`), §4 |
| 4 | **The audio path is byte-exact in both directions.** | `[O]` | JACK→PW: JACK-generated 997 Hz/0.5 tone linked into a null sink, captured by `pw-record` on the monitor → **peak 0.5, RMS 0.294556, Goertzel@997 mag²=912488472.0, byte-identical 3/3**; PW→JACK: `pw-play` tone linked into the JACK client's input → **in_peak 0.499969482, in_nonzero 71997/71997, Goertzel mag²=323955146.78 3/3 identical** (in_rms 0.241242/0.241242/0.242045 — rep 2 differs 0.3% in rms, identical in mag²) | `receipts/c_jack2pw.json`, `receipts/c_pw2jack.json`, §5 |
| 5 | **JACK's "global period size" is a per-client `node.force-quantum` prop by default — and it moves the graph quantum for other clients too.** | `[O]` | `jack_set_buffer_size(2048)` while inactive → rc 0 but `jack_get_buffer_size` still 1024; after activate the node carries **`node.force-quantum=2048`**, bufsize reads 2048 and a *second* JACK client also reads 2048; `jack_set_buffer_size(512)` live → bufsize 512 + buffer-size callback fires (`bufsize_cbs` 1→2, `last_bufsize_cb_after=512`) 3/3; `clock.force-quantum` metadata stays 0 | `receipts/d_quantum.json` (`per_client`, `cross_client`), §6.1–6.3 |
| 6 | **`jack.global-buffer-size=true` turns the same call into a PipeWire metadata write (`clock.force-quantum`), and `jack_set_buffer_size(1)` is the reset.** | `[O]` | during: settings metadata `clock.force-quantum='512'`; after the client exits: still `512`; a second client reads 512; reset arm (`set_buffer_size(1)`) → **`'0'` restored**, verified 3/3; only that one key was touched | `receipts/d_global.json`, §6.4 |
| 7 | **`PIPEWIRE_QUANTUM=512/48000` and `pw-jack -p 512` both land as `node.force-quantum`/`node.force-rate` on the client node and yield bufsize 512.** | `[O]` | env arm and wrapper arm produce the same node props `(force-quantum=512, force-rate=48000)` and `bufsize_active=bufsize_live=512`, 3/3 each | `receipts/d_quantum.json` (`env_PIPEWIRE_QUANTUM`, `pw_jack_wrapper`), §6.3 |
| 8 | **The JACK xrun callback does not report client-side stalls; a spurious callback fires on the control arm.** | `[O]` | control (no stall): `xrun_cbs=1` 3/3; deliberate stall (every 4th cycle sleeps 150 ms, 8 stalls): `xrun_cbs=0/0/1`, callbacks instead *drop* (cb 53→36) and `jack_get_xrun_delayed_usecs` never exceeds **0.004** | `receipts/e_xrun.json`, §7.1 |
| 9 | **`jack_client_real_time_priority()` / `jack_client_max_real_time_priority()` return uninitialized stack garbage.** | `[O]`+`[I]` | measured values include `82`, `-1`, `77`, `-676097905`, `-676101078`, `-676101270`, `-1316538390`, `-2052993238`, `-1739931494`; mechanism: the lib's private `thread_utils_impl` implements no `get_rt_range`, so `spa_thread_utils_get_rt_range()` returns `-ENOTSUP` **without writing `min`/`max`**, and the accessor returns `SPA_MIN(max, rt_max)-1` on the garbage | `receipts/e_rtprio.json`; `sources/pipewire-jack.c:7572-7580`, `:3454`; `sources/thread.h` (labrat read, §12) |
| 10 | **`jack_set_property` writes the PipeWire `default` metadata object, keyed by the object's registry id, and it round-trips.** | `[O]` | live `pw-metadata -n default` during the run: `id:122 key:'r95s/key1' value:'value1' type:'text/plain'` (ids 122/113/92 across reps = the node's pw-dump id, **not** the uuid index 103360…); `jack_get_property` → rc 0/`value1`/`text/plain`; missing key → rc −1; rows gone after exit (removed, 3/3) | `receipts/g_metadata.json`, §7.4 |
| 11 | **The JACK transport is a read-only projection of the PW graph position; `start`/`stop` gate it, `locate`/`reposition` are accepted but inert.** | `[O]` | linked client: state `0` (Stopped) before/after activate, frame 0; `jack_transport_start()` → **state 1 (Rolling), frame 22528**; `stop()` → state 0, frame frozen; `locate(123456)` rc 0 and `reposition(frame=48000)` rc 0 but **frame unchanged** 3/3 | `receipts/f_transport.json`, §7.5 |
| 12 | **Latency ranges are write-then-read through the data loop: default 0/0, sets are invisible until activation, then read back exactly.** | `[O]` | before activate: `{0,0}`/`{0,0}` even after `jack_port_set_latency_range(out, cap,{100,200})`; after activate: `lat_cap=[100,200]`, `lat_play=[10,20]`, `total=150`, 3/3 identical | `receipts/e_latency.json`, §7.3 |
| 13 | **The JACK client name is a projection of the PW `node.description`, so overriding it makes exact-name opens fail.** | `[O]` | `PIPEWIRE_PROPS='{ node.description = "r95s_forced" }'` → `jack_client_open` returns NULL, **status 4 (JackNameNotUnique)** 3/3; a control prop (`mem.warn-mlock`) → status 0; `node.name` override → status 0 (name check uses the description-derived name) | `receipts/b_nameproj.json`, §3.3 |
| 14 | **An unlinked JACK client still runs when any driver is active (`node.always-process=true`), but is idle with no driver.** | `[O]` | null-sink driver present, **no links**: `cb=38/38/37` over 1.6 s ≈ 47/s (1024/48 k) 3/3; pw-top shows the node at `QUANT 0` when the graph is idle and callbacks stop | `receipts/b_tone_unlinked.json`, §3.4 |
| 15 | **The JACK 3.x advertisement is bigger than the object: 52 of 218 declared `jack_*` functions are not exported.** | `[O]` | `nm -D libjack` = 168 `T jack_*`; headers declare 218 `jack_* (`; absent classes: all `jack_net_*`/`jack_slist_*` (netjack), `jack_create_adapter`/`jack_flush_adapter`, `jack_error`/`jack_info`/`jack_log`, `jack_client_activate`, `jack_uuid_to_string`; also `jack_session_notify` **exists but is a stub** (`pw_log_warn("not implemented")` → allocated zeroed struct) and `jack_reserve_client_name` is a warn+0 stub | `receipts/a_avail.json` (`symbols`), `sources/pipewire-jack.c:7505-7540`, §2.2 |

---

## 2. Availability & provenance

### 2.1 Tools and packages
`[O]` `jackd`, `jack_lsp`, `jack_connect`, `jack_disconnect`, `jackdbus`, `jack_control`
are **all absent** from `$PATH`; `pacman -Q jack2` → not found; `pacman -Q pipewire-jack`
→ `1:1.6.8-1`. Present: `/usr/bin/pw-jack`, `libjack.so{,.0,.0.3.1608}`,
`libjacknet.so`, `libjackserver.so`, `/usr/include/jack/*.h` (16 headers),
`/usr/share/pipewire/jack.conf`, `man pw-jack(1)`; **no `pipewire-jack(7)` man page**
(`man -w` → "No manual entry").

Binary shas: `libjack.so.0.3.1608 34bbb09aceb7de3a…`, `jack.conf 77a3a26091c63a50…`,
`pw-jack 9f6268e435de8089…` (`sources/BINARIES.sha256`).

### 2.2 API surface, measured against the headers
`[O]` 168 `T jack_*` exports vs 218 declared functions; the 52 declared-but-absent
names are the netjack/slist/adapter families plus `jack_error`/`jack_info`/`jack_log`
(weak helpers), `jack_client_activate`, `jack_uuid_to_string` (`receipts/a_avail.json`).
`[I]` `jack_session_notify()` is present as a **stub** that warns and returns a zeroed
command struct; `jack_reserve_client_name()` is a warn + `return 0`
(`sources/pipewire-jack.c:7512-7550`). The JACK version string is
**`"3.1.6.8 (using PipeWire 1.6.8)"`** — the version quadruple is `[3,1,6,8]`, i.e. the
library claims JACK 3.x API while behaving like the 1.6.8 tree.

### 2.3 `pw-jack` on this host
`[O]` `/usr/bin/pw-jack` has its `LD_LIBRARY_PATH` lines **commented out**; on this host
the system `libjack.so` *is* PipeWire's, so the wrapper's only effects are env:
`-r`→`PIPEWIRE_REMOTE`, `-s/-p`→`PIPEWIRE_QUANTUM`, `-v`→`PIPEWIRE_DEBUG`. Measured:
`pw-jack -p 512 ./probes/r95jack info` is byte-equivalent to
`PIPEWIRE_QUANTUM=512/48000` (same node props, same bufsize; §6.3). Direct `-ljack`
linking works without the wrapper (the probe's `ldd` shows
`libjack.so.0 => /usr/lib/libjack.so.0`, which itself links `libpipewire-0.3.so.0`).

### 2.4 `jack.conf` option lattice (on-disk, all commented = defaults)
`[O]` keys present: `jack.default-as-system`, `jack.fill-aliases`, `jack.filter-char`,
`jack.filter-name`, `jack.fix-midi-events`, `jack.flag-midi2`, `jack.global-buffer-size`,
`jack.locked-process`, `jack.max-client-ports`, `jack.merge-monitor`,
`jack.other-connect-mode`, `jack.self-connect-mode`, `jack.short-name`,
`jack.show-midi`, `jack.show-monitor`, `jack.writable-input` (+ `jack.properties`,
`jack.rules`, `node.latency/rate/quantum`, `node.lock-quantum`, `node.force-quantum`).
The file ships a `jack_bufsize` rule with the comment *"quantum set globally using
metadata"* — the in-file advertisement of claim 6, now measured.

---

## 3. The JACK client as a PipeWire citizen

### 3.1 Shape (3/3, `receipts/b_shape.json`)
`[O]` A running JACK client is visible from other processes as:

```
Client:  client.name="r95s_shape", client.api="jack", application.name="r95jack",
         application.process.binary="r95jack", pipewire.sec.pid=<pid>
Node:    node.name="r95s_shape", node.description="r95s_shape", client.api="jack",
         node.group="group.dsp.0", media.category="Duplex", media.role="DSP",
         node.always-process=true, media.class=<absent>, node.latency=<absent>
```

`[I]` `node.always-process=true` is set by the library itself
(`pwjack.c:4441-4442`, with the in-code comment *"JACK clients always need
ALWAYS_PROCESS=true or else they don't …"*), and the node name is the requested client
name (`PW_KEY_NODE_NAME`, `pwjack.c:4425`). No autoconnect: `pw-link -l` carried **0**
`r95s` links while the client ran 3/3.

### 3.2 Ports and flags (3/3)
`[O]` `jack_port_register(client,"out",JACK_DEFAULT_AUDIO_TYPE,JackPortIsOutput,0)`
produces a PW port with `format.dsp="32 bit float mono audio"`,
`port.name="out"`, `port.alias="r95s_shape:out"`, `object.path="r95s_shape:output_0"`.
Flag mapping (measured on 5 ports):

| JACK flags | PW port props | `jack_port_flags` round-trip |
| --- | --- | --- |
| `IsOutput` (2) | `port.direction=out` | 2 |
| `IsInput` (1) | `port.direction=in` | 1 |
| `IsOutput\|IsPhysical` (6) | `port.physical=true` | 6 |
| `IsOutput\|IsTerminal` (0x12) | `port.terminal=true` | 0x12 |
| `IsOutput\|CanMonitor` (0xA) | **nothing** (`port.extra` empty) | 0xA |

`[I]` source: `pwjack.c:5616-5624` maps only `PW_KEY_PORT_PHYSICAL` and
`PW_KEY_PORT_TERMINAL`; `JackPortCanMonitor` has no PW prop, and the local monitor
request state (`jack_port_request_monitor` rc 0, `jack_port_monitoring_input` → 1 on
the CanMonitor **output** port) creates **no link** — the monitor API is bookkeeping
only (`receipts/b_shape.json` `monitor`, `links_while_running=[]`).

### 3.3 Naming law and the name-projection defect
`[O]` Port full names are `<node.name>:<port>` where the node part is computed from
`node.description` (fallback nick → node.name → object.path); native PW ports therefore
appear to JACK as `<node.description>:<port_name>` — e.g. the seat null sink shows as
`r95s_ns Audio/Sink sink:playback_MONO` (description) with native
`object.path=r95s_ns:playback_0`.
`[O]` **The JACK client's own name is the same projection**, so
`PIPEWIRE_PROPS='{ node.description = "r95s_forced" }'` makes `jack_client_open` fail
with **status 4 (JackNameNotUnique)** 3/3, while `node.name` overrides do not
(`receipts/b_nameproj.json`; source: `pwjack.c:4530-4540` compares the requested name
with the registry-derived `c->name`). Side finding: `sink_properties=state.restore-props=false,device.description=X`
yields `node.description="X Audio/Sink sink"` while `device.description=X` alone yields
`node.description="X"` — the two-property form loses the description (1 observation
each; the exact argv is in §10).

### 3.4 Liveness (3/3, `receipts/b_tone_unlinked.json`)
`[O]` With a null-sink driver present and **no links**, the process callback runs
(`cb=38/38/37` in 1.6 s ≈ 47.2/s = 48000/1024) and the input buffer is all zeros.
With the graph idle (no driver), the node sits at `QUANT 0` in `pw-top` and the
callbacks stop — so "JACK clients always run" is conditional on a live graph driver.

---

## 4. Addressing and cross-domain linking (the interop law)

`[O]` `jack_get_ports()` is a **whole-graph census**: 71 ports (41 outputs / 30 inputs /
17 physical / 67 `32 bit float mono audio`) 3/3 — it lists native streams, device ports
and monitors alike. `jack_connect` uses `find_port_by_name`, which matches
`port.name` (JACK-rendered), `alias1`/`alias2` (only when `jack.fill-aliases=true`),
and, for *default* ports, the synthetic `system:*` name (`pwjack.c:861-877`).

Measured addressing matrix (`receipts/b_shape_xconnect.json`, 3 reps per arm; target =
the seat null sink's `playback_MONO` port):

| arm | name used | `jack_port_by_name` | `jack_connect` | link present while running |
| --- | --- | --- | --- | --- |
| rendered | `r95s_ns Audio/Sink sink:playback_MONO` | found | **rc 0** | yes (3/3) |
| native | `r95s_ns:playback_MONO` | **not found** | **rc 22 (EINVAL)** | no |
| fillalias (`PIPEWIRE_PROPS='{ jack.fill-aliases = true }'`) | `r95s_ns:playback_0` (object.path alias) | found | **rc 0** | yes (3/3) |

`[O]` The mirror direction is `pw-link`: `pw-link r95s_play:output_MONO r95s_probe:in`
→ rc 0 (3/3, §5.2) and `pw-link r95s_probe:out …` worked on the native side too.
So both domains can drive the link; only the *name form* differs. **Author rule: to
address a native node from a JACK client, use its `node.description:port` form (or turn
on `jack.fill-aliases` and use `node.name:portindex`); the native `node.name:portname`
form never resolves.**

---

## 5. Byte witnesses (both directions)

### 5.1 JACK → PipeWire (`receipts/c_jack2pw.json`, 3/3 byte-identical)
Rig: `module-null-sink sink_name=r95s_ns channels=1` (with `state.restore-props=false`);
`pw-record -P stream.capture.sink=true --target r95s_ns`; JACK client `r95s_probe`
generating a 997 Hz/0.5 sine in its process callback and `jack_connect`ing
`r95s_probe:out` → the rendered null-sink name.

- links during the run (verbatim): `r95s_probe:out |-> r95s_ns:playback_MONO` and
  `r95s_ns:monitor_MONO |-> r95s_rec:input_MONO`.
- captured WAV: `frames=174080`, `peak=0.5000`, `rms=0.294556`,
  **`goertzel_mag2=912488472.0`** — identical in all three reps (ideal window value
  `(0.25·N)²` for the 119 captured cycles = 928055296; ratio 0.9832 is the
  prefill/edge window, identical 3/3, i.e. deterministic).
- JACK side: `cb=119`, `bufsize_live=1024`, `wall=2.51 s`.

### 5.2 PipeWire → JACK (`receipts/c_pw2jack.json`, 3/3)
Rig: own `scratch/tone997.wav` (1.5 s, 997 Hz, amp 0.5, 48 k mono, sha in receipt);
`pw-play -P node.autoconnect=false -P node.name=r95s_play --channels 1`;
`pw-link r95s_play:output_MONO r95s_probe:in` → rc 0 3/3.

- JACK client's own input analysis: **`in_peak=0.499969482`** (= the int16 0.5),
  `in_rms=0.241242/0.241242/0.242045`, `in_nonzero=71997` (= the tone length),
  `cb_in_nonzero=71`, **`goertzel_mag2=323955146.78` 3/3 identical** (ideal
  `(0.25·71997)² = 324,000,000`; −0.01% window edge).
- No host-sink contact: `node.autoconnect=false` kept the `pw-play` stream unlinked to
  the operator's SPDIF sink (verified in `pw-link -l` censuses).

---

## 6. Period size / quantum law (the inverted JACK semantic)

### 6.1 Per-client default (`receipts/d_quantum.json` `per_client`, 3/3 identical)
| step | measured |
| --- | --- |
| `jack_set_buffer_size(2048)` **inactive** | rc 0, but `jack_get_buffer_size` still **1024** (inactive reads the latency default) |
| after `jack_activate` | `bufsize_activated=2048`, node prop **`node.force-quantum=2048`** |
| second JACK client during the same window | reads **2048** (`cross_client`, 3/3) |
| `jack_set_buffer_size(512)` **live** | rc 0 → `bufsize_after_set_active=512`, buffer-size callback fires (`bufsize_cbs` 1→2, `last_bufsize_cb_after=512`) |
| settings metadata | untouched: `clock.force-quantum='0'` throughout |

`[I]` Mechanism: `pwjack.c:5371-5395` writes `PW_KEY_NODE_FORCE_QUANTUM` on the client
node when `jack.global-buffer-size` is false. **JACK semantics inverted**: JACK's period
size is a server-global property; here the default write is per-client-node — yet it
still moves the graph quantum for *other* clients (measured), so "per-client" names the
storage location, not the scope. `nframes==1` is special-cased to `"0"` (reset).

### 6.2 Live changes are delivered (contract preserved)
`[O]` A mid-run `jack_set_buffer_size` produces a real quantum change and a
buffer-size callback on the same client (§6.1 table), i.e. the JACK callback contract
("period size may change while running") is honored by this implementation.

### 6.3 Env and wrapper (`env_PIPEWIRE_QUANTUM`, `pw_jack_wrapper`, 3/3 each)
`[O]` `PIPEWIRE_QUANTUM=512/48000` and `pw-jack -p 512` both land
`node.force-quantum=512` + `node.force-rate=48000` on the client node, `bufsize=512`
inactive→active. `[I]` `pwjack.c:4405-4413` maps the env to those two props.

### 6.4 Global arm — a JACK API call that writes PipeWire metadata (disclosed mutation)
`[O]` 3/3 (`receipts/d_global.json`), exact sequence:
`PIPEWIRE_PROPS='{ jack.global-buffer-size = true }'` + `jack_set_buffer_size(512)`:
- `pw-metadata -n settings` **during**: `clock.force-quantum='512'` (no other key moved);
- after the client exits: **still `512`** (metadata outlives the writer);
- a second JACK client reads `bufsize=512`;
- reset arm `jack_set_buffer_size(1)` → `clock.force-quantum='0'` — **restored and
  verified 3/3**, and `clock.quantum/min/max/rate` never moved.

`[I]` Mechanism: `pwjack.c:5377-5384` calls
`pw_metadata_set_property(c->settings->proxy, 0, "clock.force-quantum", "", val)` where
the proxy is the PW `settings` metadata object (id 31; `metadata.name='settings'`).
**This is the only JACK API call this seat found that mutates operator-visible host
state.** It is bounded and reversible, and was restored each rep.

---

## 7. Broken / non-functional API families (the interesting part)

### 7.1 xrun accounting does not see client-side stalls (`receipts/e_xrun.json`)
`[O]` control (no stall, linked): `xrun_cbs=1` in **3/3** runs, `xrun_delayed_usecs`
0.000–0.004, `max_delayed_usecs` 0.000–0.004.
stall arm (every 4th callback `usleep(150000)`, 8 stalls in 2 s): `xrun_cbs=0/0/1`,
callbacks **drop** (cb 53/69/79 → 36/36/28) and the delayed values stay ≤0.004.
`[I]` Mechanism (`pwjack.c:2033-2035, 2070-2073`): a client's own missed wakeups
increment `activation->xrun_count` and set `xrun_delay = 0`, but the callback fires only
when `c->xrun_count != driver->xrun_count` — a mirror of the **driver's** counter — so
client-side stalls are invisible to the JACK API, while a single spurious callback is
delivered at graph start. `[?]` The exact reason the driver counter differs once at
startup was not isolated.
`[I]` `jack_get_xrun_delayed_usecs` = `driver_activation->xrun_delay / 1e6`
(`sources/statistics.c:20-25`) while the core header documents `xrun_delay` as
*"delay of last xrun in microseconds"* (`sources/private.h:626`) — a scale/unit
anomaly consistent with the sub-µs readings; the setter path in the core was not read
`[?]`.

### 7.2 RT-priority accessors return stack garbage (`receipts/e_rtprio.json`)
`[O]` 3 reps × 7 calls, values seen: `82`, `77`, `-1`, `-676097905`, `-676101078`,
`-676101270` (plus earlier smoke values `-1316538390`, `-2052993238`, `-1739931494`).
Rep 2 was garbage **from the first (pre-activate) call**; reps 0–1 read `77/82` once,
then `-1` for `max` while active.
`[I]` Mechanism: `pwjack.c:7572-7580` calls
`spa_thread_utils_get_rt_range(&c->context.thread_utils, NULL, &min, &max)` where that
iface is the library's own `thread_utils_impl` (`pwjack.c:3454-3460`) implementing only
`create/join/acquire_rt/drop_rt`; the SPA inline returns `-ENOTSUP` **without writing
`min`/`max`** (labrat read, `sources/thread.h:89-95`), so `SPA_MIN(max, rt_max)-1` reads
uninitialized stack. Correction folded from the labrat: the two accessors **are**
declared in the installed headers (`/usr/include/jack/thread.h:53,61` as
`JACK_OPTIONAL_WEAK_EXPORT`) — this seat's C probe omitted that header, which is why
they were redeclared locally.

### 7.3 Latency is a local store, not a graph computation (`receipts/e_latency.json`)
`[O]` 3/3 identical: default ranges `{0,0}`; `jack_port_set_latency_range(out,
JackCaptureLatency,{100,200})` and `(JackPlaybackLatency,{10,20})` are **invisible
before activation** (get still `{0,0}`); after activation the getters return exactly
`[100,200]`/`[10,20]` with `jack_port_get_total_latency=150`; `jack_recompute_total_latency`
returns 0. `[I]` `pwjack.c:6761-6800` maps the set into `spa_latency_info` through the
data loop (hence invisible while the loop is not running) and
`jack_port_get_total_latency` is a local `port_get_latency`, not a graph walk — so no
JACK-style latency propagation exists here.

### 7.4 Metadata maps to the `default` metadata object (`receipts/g_metadata.json`)
`[O]` 3/3: set/get round-trip for the client and the port subjects
(`r95s/key1=value1@text/plain`, `r95s/portkey=portval`), missing key → −1,
`jack_get_all_properties` → 2 descriptions (client+port). Live PW witness during the
run: `pw-metadata -n default` row `id:122 key:'r95s/key1' value:'value1' type:'text/plain'`
— the **registry id** (122/113/92), while `jack_uuid_to_index()` reported the
`object.serial` (103360/103436/103517). After exit the rows are **gone** (removed
in-process; 3/3). Note the immediate post-remove `jack_get_property` still returns the
old value after 250 ms — the client-side description cache is not updated by its own
removal.
`[I]` `pwjack.c:3546-3567` binds the metadata named `default`/`settings`
(`pwjack.c:4081-4110`) and writes with `o->id` (registry id), not the serial.

### 7.5 Transport is a projection (`receipts/f_transport.json`)
`[O]` 3/3 identical with the client linked to a running null-sink driver:
`state_before_activate=0`, `state_after_activate=0`, `frame_after=0`,
`current_frame=0`; `jack_transport_start()` → **state 1 (Rolling)** and
`frame_after_start=22528` (= 22 quanta of 1024 ≈ the 0.47 s since start);
`jack_transport_stop()` → state 0, frame frozen; `jack_transport_locate(123456)` rc 0
and `jack_transport_reposition(frame=48000, JackPositionBBT)` rc 0 leave the frame
**unchanged**.
`[I]` `position_to_jack` (`pwjack.c:1910-1935`) maps the PW position state to
`JackTransportStopped/Starting/Rolling/Looping`; `transport_update`
(`pwjack.c:7405-7420`) only sets `node.transport`/`node.sync` props on the client node,
and `reposition` writes into the driver activation's `reposition` slot — nothing on
this host consumes it (no transport driver), hence the inert locate/reposition.

### 7.6 Prior-art contrast — JACK2 expectations, the pulse path, and native PW

| axis | JACK2 (documented prior art, not installed here) | pipewire-jack 1.6.8 (measured here) | pulse/native PW path (earlier rounds) |
| --- | --- | --- | --- |
| server | `jackd` process owns graph, transport, metadata | **no server process** — the PW daemon is the graph; the client lib *is* the JACK emulation | PW daemon; `pipewire-pulse` for the pulse ABI (r90) |
| period size | one global period, set server-wide | per-client `node.force-quantum` by default; graph-wide only via the `jack.global-buffer-size` opt-in metadata write (§6) | `clock.force-quantum` metadata is the native knob (r90 C1 lattice) |
| xrun reporting | per-client counter, callback on missed periods | callback mirrors the *driver* counter; client stalls invisible; 1 spurious callback at start (§7.1) | pw-top ERR column is the native view (r92 used it) |
| metadata | server-owned store | PW `default` metadata object, registry-id subject; rows die with the writer unless removed (§7.4) | `default`/`settings`/`sm-settings` objects, WP-owned (r90 C1/C3) |
| transport | server-owned, locate/reposition real | projection of the PW position; start/stop gate it, locate/reposition inert (§7.5) | no native transport in this graph (position state only) |
| stream restore | n/a | JACK clients leave **no** `stream-properties` rows (`[O]`: the store carried only the 4 seat null-sink keys; `[I]`: the hook keys on `media.class`, which the JACK node lacks — r90 C3/C9) | every named stream/device leaves a row unless `state.restore-props=false` (r90 C8/C9) |
| latency | propagated through the graph | local `spa_latency_info` store, 0/0 default, deferred writes (§7.3) | `node.latency` props / quantum-derived (r90 C18-C21) |

The practical consequence for the province: a JACK-based game-audio tool will *work*
headless on this host (byte-exact both ways) but its own xrun/transport/RT-priority
diagnostics are not trustworthy; a wrapper that wants a stable period size must set
`node.force-quantum` (or the global opt-in) itself and must address native ports by
`node.description:port`.

---

## 8. Falsification list (what was tried that could have killed each claim)

| claim | falsifier attempted | outcome |
| --- | --- | --- |
| a JACK client is a native PW client | `pw-dump`/`pw-cli ls Client` while running, 3/3 | **confirmed** (`client.api=jack`, node + ports) |
| a JACK client auto-connects somewhere | `pw-link -l` census while running, 3/3 | **falsified** — 0 links unless explicitly connected |
| JACK can only see JACK ports | whole-graph census + native-port link | **falsified** — 71 ports seen, native links made |
| native `node.name:port` is addressable | 3/3 arm | **falsified** — not found, rc 22 |
| `jack.fill-aliases` makes the *port name* addressable | alias arm | **refined** — only `object.path` (`:playback_0`), not `:playback_MONO` |
| JACK ports are stereo pairs | register + census | **falsified** — one mono F32P port each (`format.dsp="32 bit float mono audio"`) |
| `JackPortCanMonitor` reaches the graph | PW port props | **falsified** — no prop, no link, monitor API is local bookkeeping |
| the tone path is approximate | 3/3 byte-identical Goertzel + peak/RMS on both directions | **confirmed byte-exact** (values above) |
| `jack_set_buffer_size` is a no-op | per-client arm + callback witness | **falsified** — node prop + live quantum change + callback |
| buffer size is a fixed JACK period | cross-client arm | **falsified** — second client sees the changed quantum |
| the global arm leaves host state behind | restore + verify, 3/3 | **falsified** — `clock.force-quantum` back to 0 |
| the xrun callback reports stalls | 150 ms×8 stall arm | **falsified** — 0–1 callbacks, same as control; control even fires once |
| RT-priority accessors are merely mislabeled | 3 reps × 7 calls, -O0/stack variation | **falsified** — values are stack garbage, changing per call site |
| latency defaults are meaningful | set/get across activation | **falsified** — 0/0 default; sets deferred to the data loop |
| metadata is server-persistent like JACK2 | remove + re-read + PW row census | **refined** — PW rows removed with the client; local cache stale after removal |
| transport start/stop are no-ops | linked client, 3/3 | **falsified** — start→Rolling, stop→Stopped; but locate/reposition are inert |
| the seat perturbs host state | census + defaults before/after every stage | only the disclosed `clock.force-quantum` window (§6.4); 4 permanent `stream-properties` rows (§11) |

---

## 9. Author directives

### Verbatim-ready row proposals (≥3 reps, byte-stable, exact argv in the receipts)

1. **Availability row** — no `jackd`/`jack_lsp`; `pipewire-jack 1:1.6.8-1`;
   `libjack.so.0.3.1608 sha 34bbb09aceb7de3a…`; version string
   `"3.1.6.8 (using PipeWire 1.6.8)"`; 168/218 exports. (`a_avail.json`)
2. **Citizen row** — a running JACK client is a PW client+node:
   `client.api=jack`, `node.group=group.dsp.0`, `media.category=Duplex`,
   `media.role=DSP`, `node.always-process=true`, 0 autoconnect links. (`b_shape.json`)
3. **Port alias row** — `port.alias=<client>:<port>`,
   `object.path=<client>:output_<n>`, `format.dsp="32 bit float mono audio"`;
   Physical→`port.physical`, Terminal→`port.terminal`, CanMonitor→nothing. (`b_shape.json`)
4. **Addressing row** — `jack_connect` to the rendered
   `<node.description>:<port>` → rc 0; to `<node.name>:<port>` → rc 22; with
   `jack.fill-aliases=true` the `object.path` alias → rc 0. (`b_shape_xconnect.json`)
5. **Byte-path rows** — JACK→PW `peak=0.5000 rms=0.294556 mag²=912488472.0` (3/3);
   PW→JACK `in_peak=0.499969482 in_nonzero=71997 mag²=323955146.78` (3/3).
   (`c_jack2pw.json`, `c_pw2jack.json`)
6. **Quantum rows** — inactive set rc 0 but read-back 1024; activated 2048 with
   `node.force-quantum=2048`; live set → 512 + buffer-size callback; second client
   sees 2048; `PIPEWIRE_QUANTUM=512/48000` ≡ `pw-jack -p 512`. (`d_quantum.json`)
7. **Global-metadata row** — `jack.global-buffer-size=true` +
   `jack_set_buffer_size(512)` → `settings clock.force-quantum='512'`, persists past
   exit, reset by `jack_set_buffer_size(1)` → `'0'`. (`d_global.json`)
8. **Defect rows** — control xrun `xrun_cbs=1` vs stall `0/0/1` with 150 ms stalls;
   rt-prio garbage values list; latency set deferred to activation
   (`{0,0}`→`[100,200]`/`[10,20]`, total 150); metadata row
   `id:<registry_id> r95s/key1=value1@text/plain`; transport start→Rolling/frame
   advancing, locate/reposition inert. (`e_xrun`, `e_rtprio`, `e_latency`,
   `g_metadata`, `f_transport`)
9. **Name-projection row** — `PIPEWIRE_PROPS='{ node.description = "r95s_forced" }'`
   → open status 4 (JackNameNotUnique) 3/3. (`b_nameproj.json`)

### Bimodal / envelope cells (do not arm as a single shape)

- **Buffer size is dynamic**: `bufsize_live` varied 1024/2048/512 across stages
  (sibling drivers changed the graph quantum mid-window, §11). Arm a *current* value
  plus the callback, never a constant.
- **`jack_get_buffer_size` while inactive** returns the latency default (1024 here),
  not the force-quantum — do not use it as a read-back of a set made before activate.
- **xrun callback count**: treat "1" as a startup artifact, not an xrun.
- **`jack_get_property` after `jack_remove_property`** is stale for at least 250 ms.
- **Latency getters before activation** are always 0/0 regardless of sets.
- **`node.description` overrides** break exact-name opens (claim 13).

---

## 10. Remaining unknowns

1. `[?]` Why the driver xrun counter differs once at graph start (the spurious
   `xrun_cbs=1`); needs a core-side activation witness.
2. `[?]` The true unit/scale of `xrun_delay`/`max_delay` in the core (header says µs,
   `statistics.c` divides by 1e6, readings are ~0.004).
3. `[?]` Whether a `jack.show-monitor`/`jack.merge-monitor` client (client-level props,
   settable via `PIPEWIRE_PROPS`) changes the *port name* rendering for monitors — not
   armed (the census already shows monitors as `<desc>:monitor_MONO`).
4. `[?]` `jack.self-connect-mode` / `jack.other-connect-mode` enforcement in
   `check_connect` — not exercised (default `allow`).
5. `[?]` MIDI/OSC/UMP ports (`jack.show-midi`, `jack.flag-midi2`) — out of province,
   not measured.
6. `[?]` Freewheel: `jack_set_freewheel` exists as a symbol; `jack_is_realtime` is
   implemented as `!c->freewheeling` (`pwjack.c:5008-5013`) — the freewheel arm was not
   run (a graph-wide mode; operator decision).
7. `[?]` Why `jack_port_monitoring_input()` returns 1 for a CanMonitor *output* port
   (local state vs flag semantics).
8. `[?]` `jack_client_close` behavior with live links (the seat always disconnected
   first, except the tone/transport stages where the link died with the client).
9. `[?]` The 4 `stream-properties` rows this seat could not delete (§11) — the r90
   finding stands: no CLI deletes them.

---

## 11. Contention ledger + exit state

| window | contact | effect |
| --- | --- | --- |
| whole window | sibling lanes visible in `pw-dump`/`pw-top`: `r79lb_*`, `r83b_nsa/nsb/nsm` (null sinks), `r78fol_*`, game-dev-3d `r95-boundary` shm probe (`shm_probe.py --transport=shm --rt=1`, load) | read-only contact; my link listings carry their rows; no foreign object touched. The sibling 3D probe is CPU/RT-loading and explains part of the quantum variability (1024↔2048) seen mid-battery. |
| 16:35–16:53 | this seat: ~90 bounded battery legs + ~12 manual smoke legs, 1 null sink + 1 pw-record/1 pw-play per audio leg, all unloaded by id after a name check | own residue zero at exit (0 modules, 0 nodes, 0 procs) |
| 16:48–17:52 | **seat-induced interference (disclosed, fixed)**: the seat's preflight `sweep()` briefly matched any `pw-record`/`pw-play` process (namespace-blind); the final census killed **3 sibling `r85-boundary` mix-leg children** (`pw-record … r85b_mx_t0`, `pw-play … r85b_mx_p0/pd`) | the matcher was tightened the same minute to require the `r95s` namespace in the cmdline; `probes/r95driver.py` carries the incident note. The affected r85-boundary legs are theirs to re-run; no foreign *objects* (nodes/modules/links) were touched at any point |
| 16:47–16:48 | **disclosed host mutation**: `clock.force-quantum='512'` for ≈2.4 s ×3 reps (global arm, §6.4) | restored to `'0'` and verified each rep; no other metadata key moved; no audible test tone ever reached a host sink |
| 16:36–16:40 | 3 manual description-test sinks (`r95s_d1/d2/d3`) created **without** `state.restore-props=false` | 3 permanent `stream-properties` rows (r90 class, not deletable by CLI) |
| whole window | `~/.local/state/wireplumber/stream-properties` | 4 seat rows remain (`r95s_d1`, `r95s_d2`, `r95s_d3`, `r95s_ns`); all other legs used `state.restore-props=false` and left none |
| exit | `pactl list modules short \| grep r95s` = 0; `pw-dump` r95s nodes/clients/ports = 0; `ps` seat procs = 0; defaults SPDIF/Line unchanged; `clock.force-quantum=0`, `clock.quantum=1024`, min/max/rate unchanged | clean |

---

## 12. Labrat fold (frozen `probeParent` — exactly one child, advisory)

One read-only `ufo-labrat` was dispatched with a single falsifiable hypothesis
("rt-priority accessors return stack garbage") plus a stack-perturbation control.
**Result: NOT RUN** — that seat's toolset on this dispatch was filesystem-read only
(no exec), so it could not compile or execute the probe. It returned one *measured*
correction which is folded into §7.2: the two accessors **are** declared in the
installed headers (`/usr/include/jack/thread.h:53,61`,
`JACK_OPTIONAL_WEAK_EXPORT`) — the parent's "absent from the installed headers" premise
was wrong (the probe simply did not include that header); and one read of
`/usr/include/spa-0.2/spa/support/thread.h:89-95` confirming that a missing
`get_rt_range` method returns `-ENOTSUP` **without touching `min`/`max`** (source-level
support for the mechanism, not a dynamic falsification). The dynamic claim therefore
rests on this seat's own 3-rep measurement (`receipts/e_rtprio.json`).

---

## 13. Artifacts & provenance

`corpus/live/r95-scout/` (untracked, 2.5 MB, 42 files):
`probes/r95jack.c` (own JACK client; modes info/shape/tone/stall/bufsize/latency/
transport/metadata/rtprio/xconnect), `probes/r95jack` (binary),
`probes/r95driver.py` (bounded stage battery + own synth + own Goertzel),
`receipts/{a_avail,b_shape,b_shape_xconnect,b_tone_unlinked,b_nameproj,c_jack2pw,
c_pw2jack,d_quantum,d_global,e_xrun,e_latency,e_rtprio,f_transport,g_metadata,
summary}.json` (+ `receipts.sha256`), `runs/battery1.log`, `runs/battery2.log`,
`runs/quantum2.log`, `runs/smoke_tone.json`, `scratch/` (tone997.wav stimulus + the
three captured `c1_rep*.wav` + manual smoke JSONs), `sources/` (7 fetched
version-matched source files + `SOURCES.md` + `SOURCES.sha256` + `BINARIES.sha256`).

Key receipt shas (prefix): `a_avail 666b98f261b36490`, `b_shape 18ceba74b9c06954`,
`b_shape_xconnect a22fc6d7bfbd3ca9`, `b_nameproj 17e360699dbd307e`,
`c_jack2pw 9d1861b0746aacb6`, `c_pw2jack 09b2dd58778a159a`,
`d_quantum bed06057523811dc`, `d_global f399bba95bb11900`,
`e_xrun a16e1f12f935c454`, `e_rtprio cbfd03f8c2b30551`,
`e_latency 3f1e770605e478bd`, `f_transport b3c271e10be084a9`,
`g_metadata a5192240aa2b35c4`, `summary 9628cd37e3664b35`.

Upstream source anchors: `pipewire-jack.c` (open/name 4530-4540; props 4441;
port register 5512-5660; find_port_by_name 861-877; update_port_name 3693-3730;
metadata bind 4081-4110; metadata write 3546-3567; buffer size 5371-5395;
sample rate 5400-5430; xrun 2033-2073; rt-prio 7572-7580; transport 7314-7420;
freewheel/is_realtime 5008-5013), `statistics.c:20-35`, `uuid.c`, `private.h:626`.

*scout leaf — measured and read, not judged.*
