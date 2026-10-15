# R99 scout — the native RTP network-transport surface (`module-rtp-sink` / `module-rtp-source` / `module-rtp-sap`), measured on a private core

Host `plazir27`, measured **2026-10-15 20:34Z → 21:5xZ** (host local UTC−3).
Repo `~/Projects/shokunin/audio-shokunin` @ entry HEAD `58adad60`
(`r97 scout: WirePlumber policy…`); no tracked file was touched by this seat at
any point (`git status --porcelain | grep -v '^??'` is empty at entry and exit).
Toolchain: PipeWire **1.6.8** (`1:1.6.8-1`), pipewire-audio `1:1.6.8-1`,
WirePlumber **0.5.17-1**, libpulse **17.0-98-gb096**, avahi `1:0.9rc5-1`
(daemon active), Python 3.14.7, gcc 16.2.1, Linux **7.2.3-arch1-3**.

**Seat: SCOUT (leaf). Zero tracked-file writes; the only file written outside
`corpus/live/r99-scout/` is this report.** Every object this seat created is
`r99s_*` and lives in a **private core + private WirePlumber** under
`corpus/live/r99-scout/run` (own runtime dir ⇒ own socket; r97's arming shape).
The shared daemons (pid 2060 pipewire, 2063 wireplumber, 2694 pipewire-pulse)
were never signalled, restarted or reconfigured; **no `pactl set-default-*` was
ever issued**; exit census: **0 `r99s` objects in the shared graph, 0 seat
processes, defaults SPDIF/Line unchanged, 0 `r99s` rows in the shared
`stream-properties`**. All LAN-facing sends were measured and are bounded (§5.4).

**Label legend.** `[O]` = directly observed on this host in this window;
`[I]` = read from the **version-matched upstream source** (fetched from the
`1.6.8` tag; URLs + shas in `sources/SOURCES.sha256`) or from the installed
binary; `[?]` = not resolved.

---

## 0. Why this surface (the pick, and what it displaces)

The assignment names "network/transport audio — PipeWire RTP/ROC/zeroconf
modules if present (check module list), snapcast/jack-trip availability, or the
virtual-cable routing lattice if network modules are absent".

**The network modules are present** — so the primary branch was taken and the
virtual-cable fallback is displaced (r79 measured the `pw-loopback` -C/-P
topology and prop lattice, r83 the DSP prop lattice, r92 the filter-chain host,
r90 the module namespace; the null-sink↔source lattice has no unclaimed cell of
comparable value).

What was already known before this seat: r87 catalogued the *names*
(`rtp-sink`, `rtp-source`, `rtp-sap`, `netjack2-*`, `vban-*`, `pulse-tunnel`,
`pipe-tunnel`) and pinned the RAOP/zeroconf *absence*; r90 loaded
`module-rtp-send` through pipewire-pulse for ~0.1 s as a presence probe and
recorded it as an accepted LAN risk. **No round ever sent or received a single
RTP packet, and no round ever measured the wire format, the packetization law,
the socket shape, the refusals, or whether audio actually survives the round
trip.** That is the gap this seat closes.

---

## 1. Headline claims (each ×3 reps unless noted)

| # | claim | label | sharpest single fact | evidence |
| --- | --- | --- | --- | --- |
| 1 | **The transport is present but `roc`/`zeroconf`/`snapcast` are not.** | `[O]` | 34 native modules, **10** network-capable: `rtp-sink`, `rtp-source`, `rtp-sap`, `vban-send`, `vban-recv`, `netjack2-driver`, `netjack2-manager`, `pipe-tunnel`, `pulse-tunnel`, `avb`; `pacman -Q pipewire-zeroconf roc-toolkit snapcast jack-trip` → **4× "was not found"**; `snapcast`/`snapclient`/`roc-send`/`roc-recv`/`jack-trip` all absent from PATH; avahi-daemon active but nothing consumes it; **no man page exists** for any of the three RTP modules | `receipts/stage-a.json` |
| 2 | **The sink is a real `Audio/Sink` whose defaults are a 1 ms/48-frame L16 stream.** | `[O]`+`[I]` | node props: `rtp.ptime=1.0`, `rtp.framecount=48`, `rtp.mime=L16`, `rtp.payload=127`, `rtp.rate=48000`, `rtp.channels=2`, `net.mtu=1280`, `net.header=28`, `rtp.dscp=34`, `rtp.ttl=1`, `node.network=true`, `node.always-process=true`, `media.class=Audio/Sink`; `rtp.ssrc`/`rtp.sender-ts-offset` **random per load** | `stage-b.json` ×3, `sources/module-rtp/stream.h:14-29` |
| 3 | **The sink socket is a *connected* UDP socket with an ephemeral source port.** | `[O]` | `ss -unp` → `127.0.0.1:39003 → 127.0.0.1:46100 users:(("pipewire",pid=<core>))`; the bind is `0.0.0.0:0` + `connect(destination)`, so **the sender's port is never the destination port** | `stage-b.json` ×3, `sources/module-rtp-sink.c:214-241` |
| 4 | **204-byte packets at 1 kHz: 12-byte RTP header + 48 frames of S16BE stereo.** | `[O]` | wire capture: `n=3106/3069/3154`, **one size (204)**, `V=2`, `PT=127`, `seq` deltas `[1]`, `ts` deltas `{48,80,96,112,128,144}` (multiples of 16 = the graph quantum/64), inter-arrival 0.65–1.3 ms | `stage-b.json` ×3, `stage-h.json` |
| 5 | **The tone survives the wire sample-exact.** | `[O]` | 997 Hz / 0.5 tone into the sink → decoded from the RTP payloads: **peak 0.499969 (=16383/32768) on both channels**, Goertzel² 997 Hz **16.7 M / 69.0 M / 53.6 M** vs 440 Hz 26.5 k / 8.2 k / 26.8 k and 2000 Hz 2.1 k / 3.5 k / 0.7 k (×3 reps) | `stage-b.json` ×3 (`raw/b/rep*.recv.json.payload`) |
| 6 | **The native pair works end-to-end: sink → multicast(lo) → source → `pw-record` carries the tone.** | `[O]` | recorded from the rtp-source node: `frames 239 296 / 246 336 / 236 672`, peak **0.581 / 0.587 / 0.587**, Goertzel² 997 Hz **18.2 M / 10.7 M / 3.3 M** vs 440 Hz 8.6 k / 3.0 k / 3.3 k; the tap on the same group saw the same tone (peak 0.499969) | `stage-d2.json` ×3 |
| 7 | **Multicast with `local.ifname=lo` never reaches the LAN.** | `[O]` | 20 s arms: idle enp7s0 `tx_packets` delta **5 796**; `mcast-lo` emitted **17 266** RTP packets with delta **3 802** (below idle); positive control `mcast-en` delta **22 313**; a 20 000-packet synthetic burst: idle 0/0/0/0, `SO_BINDTODEVICE=lo` **10/13/14/14**, default route **20 087/20 014/20 011/20 019** | `receipts/lan-footprint.json`, `probes/r99lan.py` |
| 8 | **`source.port` has no default: 0 is a hard module-init error.** | `[O]`+`[I]` | `source.port=0` → the daemon **fails to create the context, rc 234 (−EINVAL)**, log `invalid source.port`; a real arm binds `0.0.0.0:46102` and `connect()`s it to `127.0.0.1:46102` | `stage-e.json` ×3, `sources/module-rtp-source.c:965-970` |
| 9 | **The packetization law is `sess.min/max-ptime` × MTU, with a 2048-byte packet cap.** | `[O]` | `min-ptime=1` → ptime 1.0 ms / 48 frames / 204 B (MTU 200 and 8000 both ignored); default (2/20) → **6.458333 ms / 310 frames / 1252 B**; `10/20` → 10.0 / 480 / 1932 B; `50/100` → 50.0 / **2400 frames but 2048 B on the wire** | `stage-h.json` ×2 per cell |
| 10 | **Refusals are module-init (−EINVAL, core dies) or nothing at all.** | `[O]` | `destination.ip=999.1.2.3`, `audio.format=F32LE` (`unsupported audio format:283`), `sess.media="r99s_bogus"` → **rc 234, the whole private core fails to start** ×3; `local.ifname=r99s_nosuchif` and `net.mtu=64` → **load fine, node created, no error at load**; `rtp-sap` without `local.ifname` joins `239.255.255.255` with `iface:0` (default interface) and starts its listener + send timer | `stage-f.json` ×3, `refusal-detail.json` |
| 11 | **`rtp.receiving=true` is a lie at startup: it is faked at module init.** | `[O]`+`[I]` | `module-rtp-source.c:997-999`: *"Because we don't know the stream receiving state at the start, we try to fake it"* → `rtp.receiving=true` is set before any packet exists; a **random `rtp.receiver-ts-offset`** is drawn per load (observed 507 500 787 / 2 611 782 104 / 4 005 960 651) | `stage-d0.json`, `sources/module-rtp-source.c:986-989,997-999` |
| 12 | **A third-party sender needs clock-aligned RTP timestamps; the native pair gets them for free.** | `[O]`+`[I]` | crafted RTP (correct size/PT/seq/SSRC, tone verified **on the wire**: peak 0.499969) → the source records **silence** while `rtp.receiving=true`; mechanism: the source's capture path compares the ring write index against `pos->clock.position` and drops sync if they differ by more than one clock duration (`audio.c:692-697`), re-aligning via `ts_align = actual_timestamp - read_index` (`audio.c:707-711`); the native sink's timestamps **are** the graph clock (`rtp_timestamp = ts_offset + ts_align + timestamp`, `audio.c:549`) | `stage-d.json`, `stage-d0.json`, `crafted.json`, `crafted-tsoff.json`, labrat fold §2 |

---

## 2. Falsifications (predeclared attacks, with outcomes)

| id | predeclared attack | outcome |
| --- | --- | --- |
| **F1** | "the RTP modules are present but unusable — the graph will not activate a network node without a session manager" | **PARTLY FALSIFIED.** With the private WirePlumber (r97 shape) the sink node goes `running`, opens its socket and emits packets within ~1 s, and a `pw-play` stream is linked to it automatically; the tone lands on the wire (§3.2). *Without* WirePlumber the node is created and stays `suspended` with 0 packets — the session manager is load-bearing. |
| **F2** | "the sink sends from the destination port" (the AES67/connected-socket intuition) | **FALSIFIED.** `bind(0.0.0.0:0)` + `connect(dst)` ⇒ ephemeral source port (39 003 / 40 762 / 54 188 in the three reps). Consequence: a *unicast* native sink→source pair is impossible in the general case (§3.5, F5). |
| **F3** | "`net.mtu` sizes the RTP packet" | **FALSIFIED.** With `sess.min-ptime=1` the packet is 204 B at MTU 200 **and** at MTU 8000; the ptime wins. Only the *default* ptime (2–20 ms window) is MTU-derived (310 frames / 1252 B ≈ MTU 1280 − headers). |
| **F4** | "a tiny MTU is refused" | **FALSIFIED.** `net.mtu=64` loads, runs, and still emits 204-byte packets (the MTU is advisory). |
| **F5** | "a unicast `source.ip` gives a plain listening socket" | **FALSIFIED — stronger shape.** For a unicast `source.ip` the module binds `INADDR_ANY:source.port` **and then `connect()`s the socket to `source.ip:source.port`** (`module-rtp-source.c:520-537, 570-577`), so only packets whose *source port* is `source.port` are accepted — and `source.port` cannot be 0 (F6). Unicast receive therefore only works with a peer that sends from the exact same port. |
| **F6** | "`source.port` defaults to an ephemeral port" | **FALSIFIED — the documented default is dead.** `source.port=0` (the documented default, `module-rtp-source.c:57`) is rejected at init: `-EINVAL`, "invalid source.port", the whole core fails (`rc 234`). A port must be given. |
| **F7** | "a correct RTP stream is enough for the source to play it" | **FALSIFIED.** A crafted stream that is *verified on the wire* (3000 × 204 B, seq+1, ts+48, tone at peak 0.499969) yields `rtp.receiving=true` but **silence** in the recorded output, because the source's capture path requires the RTP timeline to map onto the graph clock within one quantum; the native sink satisfies this by construction, a third-party sender must pin `sess.ts-offset`/align via SAP. |
| **F8** | "the source's socket joins the group on the interface you name" | **CONFIRMED (not falsified).** `local.ifname=lo` → `join IPv4 group: 239.255.42.99` on lo, packets from a lo-bound sender are received (§3.5); without `local.ifname`, `rtp-sap` joins `239.255.255.255` with `iface:0` (the kernel default = the LAN interface). |
| **F9** | "`rtp.receiving` proves packets arrived" | **FALSIFIED.** The property is faked at init (`module-rtp-source.c:997-999`) and is `true` on a source that has never seen a packet (measured on the `source.port=0` and bad-ifname arms). The only reliable arrival witnesses are the `sync to timestamp` log line and the recorded content. |

**Harness correction (disclosed).** The multicast tap in stages `c`/`d2` is a
Python `recvfrom` loop competing with the native socket for the same group; it
loses packets (sequence deltas of 0–120 in `raw/d2/rep*.tap.json.payload`,
`ts_deltas` showing wraps). The labrat flagged this as an anomaly. It is a
**tap-side artifact**: in stage `b` (unicast, the tap is the only receiver)
every sequence delta is exactly 1 and the timestamp deltas are the clean
`{48,80,96,112,128,144}` set. Audio-content analysis is unaffected (a
concatenation of payloads is a concatenation regardless of dropped packets, and
all three reps show the same tone). The `ts_delta` set itself is a real sender
property: the sink's timestamps come from the graph clock (`audio.c:549`), so
consecutive packets can step 48 + k·16 samples while the *wall* cadence stays
1 ms.

---

## 3. Laws in detail

### 3.1 The module census and the absent classes (`receipts/stage-a.json`)
10 of 34 native modules are network-capable; **no** `roc`, `zeroconf`, `raop`
or `snapcast` anything (package, binary or module) exists; `pipewire-aes67` and
`pipewire-avb` are **symlinks to the `pipewire` binary** whose config name comes
from `argv[0]`, and both configs ship in `/usr/share/pipewire/`. The three RTP
modules have **no man pages** — their only documentation is the C comment block
(which this seat fetched and pinned).

### 3.2 Arming shape (`probes/up.sh`, `r99_probe.py`)
Private core (copy of the shipped `pipewire.conf` + a fragment that disables
`module.rt`/`profiler`/`portal` and keeps `module.access`) + private
WirePlumber with a private `XDG_CONFIG_HOME` and the r97 hardware-monitor
disables. RTP modules are **added by the fragment** (`context.modules`) so the
node is a daemon-side node; a leg is one core restart (~1.5 s).
`pw-cli load-module …` at runtime loads the module **in the pw-cli process**
(client-side) — the node dies with the client and the daemon log never mentions
the module (measured, then abandoned in favour of the fragment route).

### 3.3 The sink (`stage-b.json` ×3)
Node: `media.class=Audio/Sink`, `node.network=true`,
`node.always-process=true`, `node.virtual=false`, ports `send_FL/send_FR`
(inputs) + `monitor_FL/monitor_FR` (outputs, `port.monitor=true`) — note the
**`send_*` naming**, not `playback_*`. Socket: connected UDP, ephemeral source
port → `destination.ip:destination.port`. Packets: 204 B = 12 + 48·2·2, V=2,
PT=127, `mime=L16`, seq+1, ts steps of 48 + k·16, ~1 kHz. Content: peak
0.499969 on both channels; Goertzel² 997 Hz dominates by 3–4 orders (numbers in
§1 row 5). The tone only flows while WirePlumber has linked a client to the
sink — the link is created automatically for `pw-play --target` and dies with
the player.

### 3.4 The packetization lattice (`stage-h.json`, 2 reps/cell)
| `net.mtu` | `sess.min/max-ptime` | `rtp.ptime` | `rtp.framecount` | wire packet | packets/s |
| --- | --- | --- | --- | --- | --- |
| 1280 | 1 / 1 | 1.0 ms | 48 | 204 B | ~1000 |
| 200 | 1 / 1 | 1.0 ms | 48 | 204 B | ~1000 |
| 8000 | 1 / 1 | 1.0 ms | 48 | 204 B | ~1000 |
| 1280 | **2 / 20 (default)** | **6.458333 ms** | **310** | **1252 B** | ~155 |
| 1280 | 10 / 20 | 10.0 ms | 480 | 1932 B | ~100 |
| 1280 | 50 / 100 | 50.0 ms | 2400 | **2048 B (cap)** | ~20 |

The default ptime (6.458333 ms) is what the *source* complains about when
`sess.latency.msec` is not an integer multiple of it
(`sess.latency.msec 100.000000 should be an integer multiple of rtp.ptime
6.458333`, `stream.c:889`).

### 3.5 The source (`stage-d.json`, `stage-e.json`, `crafted*.json`)
Ports `receive_FL/receive_FR` (outputs). `source.port` **must** be non-zero
(F6). Multicast `source.ip` → `IP_ADD_MEMBERSHIP` on `local.ifname`'s ifindex
and a plain bound socket; unicast `source.ip` → bind `INADDR_ANY:port` **plus
`connect(source.ip:port)`** (F5). `rtp.receiving` is faked at init (F9). The
receive→ring→graph path is clock-gated (F7): the ring is written at
`timestamp = ntohl(hdr.ts) − ts_offset` and `+ target_buffer`
(`audio.c:364-375`), the capture process compares the ring index against
`pos->clock.position` and drops sync on a >1-quantum deviation (`audio.c:692-697`),
re-aligning with `ts_align = actual − read_index` (`audio.c:707-711`). The
native sink's timestamps are graph-clock-derived (`audio.c:549`), which is why
the native pair locks immediately (stage-d2) and the crafted sender does not.

### 3.6 The SAP module (`stage-f.json`, `refusal-detail.json`)
`rtp-sap` loads with no node, joins `sap.ip` (default `239.255.255.255:9875`)
with `iface:0` when `local.ifname` is absent, starts a **SAP send timer** and a
listener, and logs `Successfully loaded module-rtp-sap`. Defaults read from the
source: `sap.ip=239.255.255.255`, `sap.port=9875`, `net.ttl=32`,
`net.loop=false`, `igmp.deadline.sec=45`. The `create-stream`/`announce-stream`
rules from `pipewire-aes67.conf` are the only discovery mechanism on this host
(there is no `pipewire-zeroconf`).

### 3.7 Refusal lattice (`stage-f.json` ×3, `refusal-detail.json`)
| input | result |
| --- | --- |
| `destination.ip=999.1.2.3` | module `-EINVAL` → **daemon context creation fails, rc 234** |
| `audio.format=F32LE` | `-EINVAL`, log `unsupported audio format:283 channels:2`, rc 234 |
| `sess.media="r99s_bogus"` | `-EINVAL`, log `unsupported media type`, rc 234 |
| `local.ifname=r99s_nosuchif` | **loads**, node created, stays suspended; the `SO_BINDTODEVICE` failure is deferred to stream start (`module-rtp-sink.c:230-236` → `goto error`) |
| `net.mtu=64` | **loads and runs** (204 B packets) |
| `source.port=0` | `-EINVAL`, log `invalid source.port`, rc 234 |
| `rtp-sap` with no `local.ifname` | loads; joins on `iface:0` (default interface) |

Supported wire formats (`stream.c:309-317`): `U8 (L8)`, `ALAW (PCMA)`,
`ULAW (PCMU)`, `S16BE/S16LE (L16)`, `S24BE (L24)`, `rtp-midi`, `opus` —
**no S24LE, no S32, no F32** (F32 exists only as the opus path's internal
format).

---

## 4. Author-ready rows — proposed `--probe-rtp-r99` entry

Each row is a candidate for the canonical battery (`corpus/fixtures/measure_audio.py`
opt-in probe). All rows are `r99s_*`-namespaced, run in a **private core +
private WirePlumber** (never the shared daemons), and use only loopback
addresses (`127.0.0.1` unicast, `239.255.42.99` multicast with
`local.ifname=lo` — measured LAN-clean, §5.4).

1. **Census row** — 34 native modules, 10 network-capable, RTP sink/source/SAP
   present; `roc`/`zeroconf`/`snapcast`/`jack-trip` absent; no man pages.
   (`stage-a.json`)
2. **Sink-shape row** — node is `Audio/Sink`, ports `send_*`/`monitor_*`,
   `node.network=true`, `rtp.ptime=1.0`, `framecount=48`, `mime=L16`,
   `payload=127`, `net.header=28`, random `ssrc`/`sender-ts-offset`.
   (`stage-b.json`)
3. **Socket-shape row** — connected UDP, ephemeral source port; two sinks on
   one destination coexist (bind is `0.0.0.0:0`). (`stage-b.json`)
4. **Wire row** — 204 B, V=2, PT=127, seq+1, ts steps 48 + k·16, ~1 ms
   cadence, tone peak 0.499969, Goertzel² 997 Hz ≫ 440/2000 Hz.
   (`stage-b.json`, payloads kept under `raw/b/`)
5. **Packetization row** — the §3.4 table (6 cells), incl. the 2048 B cap and
   the MTU-ignored-at-fixed-ptime law. (`stage-h.json`)
6. **Native end-to-end row** — sink → `239.255.42.99`(lo) → source →
   `pw-record`: tone present (peak 0.58, 997 Hz dominant). (`stage-d2.json`)
7. **Multicast-confinement row** — `local.ifname=lo` + `SO_BINDTODEVICE`;
   enp7s0 `tx_packets` delta below the idle baseline while 17 266 packets are
   emitted; positive control egresses. (`lan-footprint.json`)
8. **Source-shape row** — ports `receive_*`, `source.port≠0` required,
   `rtp.receiving` faked at init, random `rtp.receiver-ts-offset`, unicast =
   connected socket. (`stage-e.json`, `stage-d0.json`)
9. **Refusal row** — the §3.7 table; note the two classes (init-`EINVAL` kills
   the core vs. silently-deferred `SO_BINDTODEVICE`). (`stage-f.json`)
10. **Clock-alignment row (negative control)** — a crafted sender with correct
    headers but an unaligned timestamp records silence while the tap proves the
    tone is on the wire; assert the *mechanism* (ring vs graph clock) not the
    silence. (`stage-d0.json`, `crafted.json`)
11. **SAP-arming row** — loads, joins `239.255.255.255` on the default
    interface, starts listener + send timer, creates no node; **this row must
    run with `local.ifname=lo` and `sap.ip` on a loopback-reachable group, or it
    will emit SAP onto the operator's LAN.** (`refusal-detail.json`)
12. **Absent-class row** — `pactl load-module module-roc-sink` /
    `module-zeroconf-discover` refusals are already pinned (r90) — do **not**
    re-author; reference r90 §1.3 instead.

---

## 5. Contention ledger, host-state, cleanup

### 5.1 Sibling seats
The audio lane was otherwise quiet; the **g2d lane's r99-boundary seat** was
live (bash matrices under `game-dev-2d-shokunin/corpus/live/r99-boundary`,
observed in `ps`, never touched). The r91-boundary seat's `pw-play` processes
appeared in the shared graph mid-session (observed only). No shared-graph
object was created, read for mutation, or destroyed by this seat.

### 5.2 Seat-owned host state
Per leg: one private core + one private WirePlumber (own runtime dir, own
`XDG_CONFIG_HOME`/`XDG_STATE_HOME`/`XDG_DATA_HOME`), one RTP module in the core
fragment, one `r99s_*` node, up to three Python UDP sockets on the seat's ports
(46 100–46 199) and, on tone legs, one `pw-play`/`pw-record`. All teardown by
pid file + `/proc` cmdline matching (`probes/killseat.py`) — the shared daemons
cannot match those patterns.

### 5.3 Residue
Exit: 0 `r99s` objects in the shared graph; 0 seat processes; 0 `r99s` rows in
the shared `~/.local/state/wireplumber/stream-properties` (the private
WirePlumber writes to the seat's own state dir); shared defaults
`…HiFi__SPDIF__sink` / `…HiFi__Line__source` unchanged. **One stale private
socket** was left behind by an early harness bug (the pid file held the
`setsid` wrapper's pid) — cleaned; the bug is recorded because it produced one
false "core up" reading in an early stage-f leg.

### 5.4 LAN footprint (measured, not assumed)
The only interface with a multicast route is `enp7s0` (the operator's LAN).
Three arms over 20 s each (`receipts/lan-footprint.json`) plus a 20 000-packet
synthetic burst (`probes/r99lan.py`):
* **`local.ifname=lo` confines the send**: 17 266 RTP packets emitted, enp7s0
  `tx_packets` delta 3 802 — *below* the idle baseline (5 796). Synthetic
  bursts: 10–14 stray packets per 20 000.
* **Positive control** (`local.ifname=enp7s0`): delta 22 313 (≈ idle + burst),
  and the loopback-joined receiver saw **0** packets — i.e. the counter method
  detects egress and delivery is per-interface.
* The IGMP **joins** (`rtp-sap` on `239.255.255.255`, source joins on lo) are
  passive; only the SAP arms without `local.ifname` touch the default interface.
  Every measurement in this report used `lo`.

---

## 6. Remaining `[?]`, risks, blockers

1. `[?]` **The crafted-sender silence is mechanistically attributed but not
   repaired.** The clock-gating code is read and cited, the wire content is
   verified, but no arm produced audio from a third-party sender. A follow-up
   should pin `sess.ts-offset` **at module-arg level** (my arms put it in
   `stream.props`, which the module does not read — `rtp.receiver-ts-offset`
   stayed random in both arms) and/or replay the native sink's timestamp
   sequence into a second core.
2. `[?]` **The receive-path peak overshoot** (0.581–0.587 vs the 0.499969 on
   the wire, ×3) is real but unexplained: candidates are the DLL/rate-match
   correction during resync and the adapter's format conversion. A row must
   assert *presence and spectral dominance*, not an exact peak, until this is
   pinned.
3. `[?]` **`net.mtu` semantics at ptime < 1 ms** and the exact 2048-byte packet
   cap site were not read in the source (`stream.c` ptime computation is only
   partially read); the measured table stands on its own.
4. `[?]` **SAP announce/receive end-to-end was not exercised** (it would emit
   SAP onto the LAN, or need a loopback-reachable group and a crafted
   announcement). The arming law (§3.6) is measured; the discovery flow is not.
5. `[?]` **Opus / MIDI / VBAN / netjack2 / avb paths unmeasured** (the sink
   links `libopus`; `sess.media=opus|midi` are accepted code paths). Named
   gaps for a follow-up round.
6. **Risk (bounded):** the battery restarts a private core per leg; a
   `source.port` collision or a stale socket can produce a false "core up".
   The harness's `core_up` now verifies the pid *and* a live `pw-cli info 0`
   response.
7. **Blocker for authoring:** none. The surface is fully drivable headless,
   self-cleaning, and loopback-confined when `local.ifname=lo` is used.

---

## 7. Artifacts & provenance

`corpus/live/r99-scout/` (untracked):

- `r99_probe.py` — stage driver (a/b/c/d/d0/d2/e/f/h), receipts + raw capture.
- `probes/r99udp.py` — UDP RTP receiver/sender (own code; `SO_BINDTODEVICE`
  on every multicast send), `probes/r99lan.py` + `probes/r99lanarm.py` — LAN
  footprint, `probes/killseat.py` — precise teardown, `probes/up.sh`/`down.sh`
  — private instance, `probes/r99crafted*.py`, `probes/r99recvpath.py`,
  `probes/r99d0debug.py`, `probes/r99f2.py` — mechanism probes.
- `receipts/` — `stage-a.json` … `stage-h.json`, `lan-footprint.json`,
  `crafted.json`, `crafted-tsoff.json`, `refusal-detail.json`, `summary.json`.
- `raw/` — per-leg JSON + the raw captured payloads (`raw/b/rep*.recv.json.payload`,
  `raw/d2/rep*.tap.json.payload`) and the recorded WAVs of the tone-carrying
  arms. **Silent bulk artifacts were trimmed** (the `d`/`d0`/`e` silence wavs
  and the `lan` arm's silence payloads): their measured content is preserved
  verbatim in the receipts (`wav.frames`/`peak`/`goertzel`), which is what the
  claims cite.
- `runs/` — `core.log` (last leg), `wp.log`.
- `sources/` — version-matched upstream 1.6.8 (`module-rtp-sink.c`,
  `module-rtp-source.c`, `module-rtp-sap.c`, `module-rtp/{stream,audio,midi,opus}.c`,
  `module-rtp/{stream,sap,ptp}.h`, `network-utils.h`, `context.c`,
  `pipewire-daemon.c`, `module-protocol-native.c`) + `SOURCES.sha256`.
- `scratch/` — recon scripts (socket behavior, LAN counters, tone WAV).
- `PREDECLARED.md` — the hypotheses frozen before the battery.

Labrat fold: one read-only `ufo-labrat` probe independently decoded the d2
first-packet headers across all three reps (V=2, PT=127, seq/ts/SSRC all match
the receipt), confirmed the mechanism lines verbatim (`audio.c:364/375/549/707-711`,
including the `set_timestamp`/`direct_timestamp` conditionals my paraphrase had
omitted), and flagged the tap-loss `ts_delta` anomaly (§2 harness correction).
It had **no shell executor**, so it could not independently re-decode the audio:
the tone claims are single-witness (this seat's own Goertzel) and are marked as
such.

*scout leaf — measured and read, not judged.*
