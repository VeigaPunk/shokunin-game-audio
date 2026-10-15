# R99 boundary — native RTP transport replayed under load: 21 confirmed, 4 falsified

Round 99 **boundary** (executor seat, leaf). Attacks every pinnable claim in
`reports/round-99/r99-scout.md` by replaying its armed cells with **fresh
processes**, **quiet-ish (0 own hogs) and under load (14 own hogs held across
the whole pass)**, and by varying the named independent axes.

Host `plazir27`, measurement window **2026-10-15 21:34:48Z → 21:57:35Z** (host
local UTC−3). Repo `~/Projects/shokunin/audio-shokunin`, HEAD **`de59a276`** at
entry → **`3836de94`** at exit (a sibling's `r97 boundary` commit landed
mid-window; this seat never touched a tracked file). Toolchain re-pinned:
PipeWire **1.6.8** (`1:1.6.8-1`), pipewire-audio `1:1.6.8-1`, WirePlumber
**0.5.17-1**, Python 3.14.7, Linux 7.2.3-arch1-3. The three module `.so` files
were re-hashed into `receipts/census.json`.

**Seat discipline.** Zero tracked-file writes; nothing committed; the only file
written outside `corpus/live/r99-boundary/` is this report. Every object this
seat created is `r99b_*` in a **private core + private WirePlumber** under
`corpus/live/r99-boundary/run` (own runtime dir ⇒ own socket), plus **one
disclosed transient leg in the shared graph** (§4, AX-GRAPH). All teardown by
own pid file + `/proc/<pid>/cmdline` marker re-check (`r99b_hog`, our conf path,
`pw-cli`); no pattern sweep, no `pkill`, no foreign signal (r95 precedent). The
shared daemons (pid 2060/2063/2694) were never signalled or reconfigured; no
`pactl set-default-*`/`wpctl set-*` was ever issued.

---

## 0. What was replayed, and the boundary questions

56 armed cells in each pass (112 process legs total, plus 5 LAN windows per
pass), re-implemented independently (`probes/r99b_*`, own RTP codec, own RIFF
reader, own Goertzel, own tone generator — byte-identical to the scout's
stimulus):

| pass | own hogs | window (cells) | loadavg1 over the cells | procs_running (median) |
| --- | --- | --- | --- | --- |
| quiet-ish | 0 | 21:34:48Z → 21:47Z | min 99.92 · p50 108.61 · max 121.14 · mean 111.48 | 108 |
| load | 14 held | 21:46Z → 21:53Z | min 99.50 · p50 118.62 · max 123.96 · mean 114.50 | 116 |

The load pass held **14 argv-marked `r99b_hog` processes** across
cells + LAN arms: `runs/load/hogs-all.json` — `census_during` 14/14 with the
marker, `reaped` 14/14 (`marker_ok` true, `killed` true), `final_alive: []`,
`final_census: []`, **3010 CPU-s over 414.6 s = 7.26 CPU-equivalents**.

The three questions a boundary seat exists to ask:

1. **Is the law load-invariant?** → the *shape* laws are (packet sizes, ptime
   table, prop sets, socket shapes, refusal classes are identical in both
   passes); the *content* metrics are not (fill fraction, 997 Hz dominance,
   packet cadence all degrade under load).
2. **Is the law seat-invariant?** → the scout's numbers reproduce (props,
   204 B/PT 127/seq+1, peak 0.499969, the packetization table, the refusal
   classes), except the four falsifications in §2.
3. **Does any independent axis change it?** → yes in two places: the *rate*
   axis destroys the clean ts lattice, and `rtp.ptime`/`rtp.framecount` are not
   module args at all (C16, including a SIGFPE core death).

---

## 1. Verdict table

30 verdicts. **21 CONFIRMED, 4 FALSIFIED, 1 mixed (C15), 4 MEASURED** (axes).
Machine-readable: `receipts/verdicts.json`; rendered:
`runs/analysis-verdicts.txt`. Verdicts are evaluated per pass; a row that
differs is shown as `quiet / load`.

| id | verdict | claim |
| --- | --- | --- |
| C1 | CONFIRMED | 34 native modules, 10 network-capable; `roc`/`zeroconf`/`snapcast`/`jack-trip` absent; no RTP man pages |
| C2 | CONFIRMED | sink props (explicit 1 ms ptime): 204 B L16 stream, `send_*`/`monitor_*`, `net.mtu=1280`, `net.header=28`, `dscp=34`, `ttl=1`, `node.network=true` |
| **C2b** | **FALSIFIED** | the sink ***defaults*** are a 1 ms / 48-frame L16 stream |
| C3 | CONFIRMED | sink socket = connected UDP with an ephemeral source port |
| C3b | CONFIRMED | two sinks on one destination coexist (2 SSRCs, 2 ephemeral ports) |
| C4 | CONFIRMED | wire: 204 B, V=2, PT=127, seq+1, one size, ~1 kHz |
| C4b | CONFIRMED | the report's ts-delta set `{48,80,96,112,128,144}` is a strict subset of the measured set |
| C5 | CONFIRMED | tone survives the wire: peak exactly `0.499969` on both channels in every rep |
| C6 | CONFIRMED | native end-to-end sink→mcast(lo)→source→`pw-record` carries the tone (both passes) |
| C7 | CONFIRMED | `local.ifname=lo` keeps the multicast send off the LAN (20 s windows, 19 588 packets emitted) |
| C8 | CONFIRMED | `source.port=0` is a hard init error (rc 234, "invalid source.port") |
| C8b | CONFIRMED | unicast source = connected socket; only packets **from `source.port`** are accepted (real send, both arms) |
| C9 | CONFIRMED | the 6-cell packetization table reproduces exactly, both passes |
| **C9b** | **FALSIFIED** | the 50/100 cell is "capped at 2048 B on the wire" |
| C10 | CONFIRMED | bad dest IP / `F32LE` / bogus media kill the core (rc 234); bad ifname / tiny MTU load |
| C10b | CONFIRMED | "loads fine" is a *load*-time statement: the failure is deferred to stream start |
| C11 | CONFIRMED | `rtp.receiving=true` is faked at init; `receiver-ts-offset` random per load |
| **C12** | **FALSIFIED** | crafted RTP with an arbitrary ts records silence because of clock gating |
| C12b | CONFIRMED | `sess.ts-offset` as a module arg is a working repair (all 5 offsets play the tone) |
| C13 | CONFIRMED | `rtp-sap`: no node; joins the group (`iface:0` without `local.ifname`); listener + send timer |
| C14 | CONFIRMED | `S24BE` is supported (300 B wire packet); no `S24LE`/`S32`/`F32` |
| C15 | CONFIRMED / MEASURED | shape laws identical quiet vs load; content metrics load-sensitive |
| C16 | CONFIRMED (new) | `rtp.ptime`/`rtp.framecount` are read from `stream.props`, not module args; a *consistent* pair kills the daemon |
| **C10c** | **FALSIFIED** | the refusal dichotomy "module-init `-EINVAL` or nothing at all" |
| AX-GRAPH | CONFIRMED | daemon-side private module ≡ client-side `pw-cli` module; the shared graph hosts it and stays clean |
| AX-QUANTUM | MEASURED | the ts lattice does **not** track `quantum/64` |
| AX-RATE | MEASURED | a rate mismatch (module vs graph) destroys the clean ts lattice |
| AX-ORDER | MEASURED | module-arg order irrelevant; duplicate `min-ptime` non-discriminating |
| AX-FLAGORDER | CONFIRMED | `pw-play --target` before **and** after the file both hit the target (2 sinks) |
| AX-RELINK | MEASURED | re-lock 0–2 ms after a player restart; the tone stops with the client |

---

## 2. The falsified claims — exact receipts

### 2.1 **C2b — the sink "defaults" are not 1 ms / 48 frames**

Claim as written (`r99-scout.md` §1.2): *"The sink is a real `Audio/Sink` whose
**defaults** are a 1 ms/48-frame L16 stream."* The evidence cited is
`stage-b.json` ×3 — but the scout's own `sink_args()` **always** passed
`sess.min-ptime = 1 sess.max-ptime = 1`, and its own §3.4 table lists
"2 / 20 (default) → 6.458333 ms → 310 frames → 1252 B".

Direct replay (`raw/*/sink_default-rep*.json`, no ptime args, fresh processes):

| pass | rep | `rtp.ptime` | `rtp.framecount` | wire size | packets |
| --- | --- | --- | --- | --- | --- |
| quiet | 0/1 | **6.458333** | **310** | **[1252]** | 465 / 454 |
| load | 0/1 | **6.458333** | **310** | **[1252]** | 462 / 462 |

**Verdict: FALSIFIED (wording).** The module defaults are `sess.min/max-ptime =
2/20` → 6.458333 ms / 310 frames / 1252 B. The 1 ms/48-frame stream requires an
explicit `sess.min-ptime=1 sess.max-ptime=1`. Armable corrected form: *"with
`min/max-ptime=1` the sink is a 1 ms/48-frame L16 stream; the module defaults
are 2/20 → 6.458333 ms/310 frames/1252 B."*

### 2.2 **C9b — the "2048-byte packet cap" is the scout's own tap buffer**

Claim as written (`r99-scout.md` §1.9 and §3.4): *"`50/100` → 50.0 / **2400
frames but 2048 B on the wire**"*, and §6 `[?]`3 *"the exact 2048-byte packet
cap site was not read in the source."*

The scout's own capture helper (`probes/r99udp.py`, line 51) reads
`s.recvfrom(2048)`: **any datagram larger than 2048 B is truncated by the tap**,
and the "cap" appears nowhere in the module sources (the sender transmits
`psamples × stride` bytes in one `sendmsg`, `module-rtp/{audio.c:554-564}`).

Direct replay with a 64 KiB receive buffer (`raw/*/lattice-rep5.json`, identical
in both passes):

| pass | `rtp.ptime` | `rtp.framecount` | measured sizes | packets | decoded frames | continuity |
| --- | --- | --- | --- | --- | --- | --- |
| quiet | 50.0 | 2400 | **[9612]** | 51 | 122 400 | sample-exact, no holes |
| load | 50.0 | 2400 | **[9612]** | 51 | 122 400 | sample-exact, no holes |

9612 = 12 + 2400 × 4 exactly. **Verdict: FALSIFIED.** There is no 2048-byte cap;
the wire packet is 9612 B and the 50 ms cell is the *most* faithful of the
lattice (one packet size, ts delta exactly 2400, zero holes). The scout's
"2048 B" and its §3.4 note are a measurement artefact of its own receiver.
This also closes the scout's own `[?]`3: the cap site does not exist.

### 2.3 **C12/F7 — the crafted-sender silence was a delivery artifact, not clock gating**

Claim as written (`r99-scout.md` §1.12, F7, §3.5): *"crafted RTP (correct
size/PT/seq/SSRC, tone verified on the wire) → the source records **silence**
while `rtp.receiving=true`; mechanism: the source's capture path compares the
ring write index against `pos->clock.position` …"*.

The scout's crafted arms called its own `sender(46101, …)` with
`host` defaulting to **`127.0.0.1`** (unicast) while the source was configured
`source.ip = 239.255.42.99` — its **own receipt says so**:
`crafted.json → "send": {"sent": 3000, …, "host": "127.0.0.1", "port": 46101}`.
For a multicast `source.ip` the module binds the socket to the **group address**
(`module-rtp-source.c:515-525`, bind at `:565`), so the unicast datagrams never
reached it. `/proc/net/udp` proves it:

```
quiet crafted_unicast rep0 (scout shape: multicast source + unicast sender)
  2669: 00000000:B485 ...   <- the tap (0.0.0.0:46213) received all 2500
  2669: 632AFFEF:B485 ...   <- the SOURCE socket, bound to 239.255.42.99:46213
wav peak_l = 0.0, no "sync to timestamp" line in the core log
```

A/B with the same source config, changing **only** the delivery path
(`raw/*/crafted_mcast-rep*.json`, both passes):

| arm | tap | source recording | source log |
| --- | --- | --- | --- |
| unicast (scout shape) | 2500 pkts, tone peak 0.499969 | **peak 0.0, all-zero** | no `sync to timestamp` |
| multicast on `lo` (correct) | 2500 pkts, tone peak 0.499969 | **peak 0.5, g997 803 M / 792 M** | `sync to timestamp:731566816 seq:0 …` |
| unicast source (C8b same-port) | — | peak 0.5, g997 803 M | `sync to timestamp:3039794896 seq:0 …` |

Under load the same three arms reproduce (0.0 / 809 M / 791 M).

**Verdict: FALSIFIED (mechanism).** The clock-gating code exists but is *not*
what produced the silence: a correctly delivered crafted stream (multicast on
`lo`, or a unicast source) plays immediately at full amplitude with an
arbitrary `ts0 = 1 000 000`, with **no** `sess.ts-offset` needed. The scout's
`[?]`1 ("mechanistically attributed but not repaired") is now repaired — and the
repair falsifies the attribution. Armable corrected form: *"a crafted sender
must deliver to the address the source socket is bound to (the group for a
multicast `source.ip`); with correct delivery the tone plays."*

### 2.4 **C10c — the refusal dichotomy is false: a consistent `rtp.ptime`/`rtp.framecount` pair kills the daemon with SIGFPE**

Claim as written (`r99-scout.md` §1.10): *"Refusals are module-init (−EINVAL,
core dies) **or nothing at all**."*

`receipts/axis-order-ptime.json`:

| input | result |
| --- | --- |
| `rtp.ptime = 20 rtp.framecount = 960` **in `stream.props`** | log `sess.latency.msec 0.000000 should be an integer multiple of rtp.ptime 0.000000`, then **`core died rc=-8` (SIGFPE)** |
| same pair as **module args** | silently ignored (props stay 1.0 / 48) |
| `rtp.ptime = 20 rtp.framecount = 480` (inconsistent) in `stream.props` | loads; prop says `framecount=480` but the wire is **3852 B** and ts delta **960** |
| `rtp.ptime = 20` only in `stream.props` | 20 ms / 960 frames / 3852 B |

Mechanism (read, `stream.c:841-864` + `:888-891`): with `ptime` and `framecount`
both present *and consistent*, none of the three branches assigns `psamples`,
so `impl->psamples` stays 0 → `fmodf(target_buffer, 0)` → `SPA_ROUND_DOWN(x, 0)`
→ integer division by zero. **Verdict: FALSIFIED** — a third class exists
(arithmetic fault, rc −8), and it is reachable from a documented property.

### 2.5 C4b — a report-set imprecision, not a law error

`r99-scout.md` §1.4 and §2 print the ts-delta set as
`{48, 80, 96, 112, 128, 144}`. Measured (both passes, all reps):
`{48, 80, 96, 112, 128, 144, 160, 176}` (+ a wrap pair when a leg straddles a
2³² rollover). The report's set is a strict **subset** of the receipt's own
`ts_deltas`; the law (one step size 48 + k·16, k ∈ {0,2..8}) stands. Arm the
full set, or say "multiples of 16 ≥ 48".

### 2.6 C5 — what "sample-exact" does and does not mean

Peak `0.499969` (= 16383/32768) on both channels is exact in **every** rep of
both passes — the strongest single witness the scout had. The qualification the
scout's §2 harness note did not make: at 1 ms ptime the *stream* is not
continuous. Per-payload metrics (`payload_metrics` over the captured bytes):

| pass | rep | decoded frames | non-zero frames | longest zero run | tone slices exact |
| --- | --- | --- | --- | --- | --- |
| quiet | 0 | 156 192 | 80.3 % | 24 369 | 83.7 % of non-zero |
| quiet | 1 | 139 104 | 71.4 % | 24 416 | 100 % of non-zero |
| load | 0 | 156 192 | 83.7 % | 20 720 | 2.2 % of non-zero |
| load | 1 | 157 680 | 80.6 % | 24 673 | 15.7 % of non-zero |

The transmitted samples *are* exact copies of the tone (constant frame offset,
16-sample granularity), but the ring is not always filled, so the concatenated
payload is tone-with-holes; the scout's Goertzel figures (16.7 M / 69.0 M /
53.6 M) vary by 4× across reps for exactly this reason. Arm "peak is exactly
0.499969" and "non-zero samples are exact tone slices", not "the tone survives
sample-exact" without the hole caveat. The 6.46/10/50 ms cells have **no holes
and are fully sample-exact**.

---

## 3. Load vs quiet-ish: how the condition was built and evidenced

- **14 own hogs**, one per process, argv-marked `r99b_hog`, started 60 s before
  the first cell so the 1-min loadavg reflects them and held across
  `cells` + `lan` (`runs/load/hogs-all.json`).
- Lifecycle: `census_during` 14 entries all with `r99b_hog` in
  `/proc/<pid>/cmdline`; `reaped` 14/14 with `marker_ok`+`killed`;
  `final_alive: []`; `final_census: []`. (The receipt's top-level `marker_ok`
  map was sampled *after* reaping and is therefore vacuous — a harness
  ordering bug, fixed in `probes/r99b_loadrun.py` for the repro path; the
  evidence is `census_during` + `reaped[]`.)
- **CPU accounting**: 3010.0 CPU-s over 414.6 s wall = **7.26 CPU-equivalents**
  (per-hog 205.0 / 215.0 / 225.9 CPU-s over the pass).
- **The loadavg delta is not attributable to this seat alone**: the host was
  already ~3.4× oversubscribed (32 CPUs, ~108 runnable tasks, 60+ foreign `yes`
  processes plus the r93-boundary sibling battery's own 12 hogs). Quiet-ish =
  *0 own hogs*; it is not a quiet machine. Loadavg over the cells: 111.5 → 114.5
  mean, i.e. this seat's 7 CPU-equivalents moved the mean by ~3.
- **What the load changes**: shape laws unchanged; content metrics degrade —
  packet cadence 887→637 pkt/s in the smoke leg, non-zero fraction, 997 Hz
  dominance (e.g. `e2e_native` rep1 g997/g440 = 6.4 under load vs 868 quiet),
  and the per-sample exactness of tone slices (2–16 % vs 84–100 %).
  Every falsification in §2 reproduces in **both** passes, so none of them is a
  load artefact.

---

## 4. Independent axes

| axis | how varied | result |
| --- | --- | --- |
| **private-core vs shared graph** | (a) daemon-side module in the private core (scout shape); (b) client-side `pw-cli load-module` against the **private** core; (c) client-side against the **shared** core | (a) and (b) identical: the client-side node is `running` while `pw-cli` lives (1485 packets captured) and gone after it exits (`node_after_cli_exit: null`). (c) **one disclosed leg**: node `r99b_sink_sh` (id 241) + 4 ports appeared in the operator's shared graph for ~4 s, the shared-graph `pw-play` tone reached our loopback receiver (4081 × 204 B), and the post census is empty: `pre`/`post` = 0 `r99b` objects, 0 `r99b` rows in `~/.local/state/wireplumber/stream-properties`. The scout's "`pw-cli load-module` is client-side" is confirmed at the shared-graph boundary. |
| **rates / quantum** | core `default.clock.quantum` 256 / 1024 / 4096 (effective 256 / 1024 / 2048, `pw-metadata`-verified) with ptime 1 ms; module `audio.rate` 44100; core `default.clock.rate` 44100 | the ts lattice is **identical** `{48,80,…,176}` at every quantum → the scout's parenthetical "multiples of 16 = the graph quantum/64" is **falsified as a mechanism** (at quantum 256, quantum/64 = 4). A *rate* mismatch destroys it: module 44100 → `rtp.rate=44100`, ptime 0.997732, fc 44, wire 188 B, deltas `{44,71,…,167}`; core 44100 with module 48000 → 204 B but deltas `{48,54,57,…,1010}`. |
| **flag order** | module-arg order reversed; duplicate `sess.min-ptime` (1 then 20); `rtp.ptime` in `stream.props`; `pw-play <file> --target X` vs `pw-play --target X <file>` (two sinks so the target discriminates) | reversed args ≡ canonical (204 B, 1.0/48); duplicate `min-ptime` non-discriminating (`max-ptime=1` clamps both orders to 48); `rtp.ptime` in `stream.props` → C16; `--target` **works in both positions** (target peak 0.499969, other sink peak 0.0, both reps, both passes). |
| **sibling presence** | two sinks in one core to the same destination; a sink + source + SAP in one core; foreign nodes/processes live in the shared graph (witnessed read-only) | two sinks coexist: 2 SSRCs (`1c033acf`/`d1afb0a5`), 2 ephemeral source ports, one size (204 B), 6087/6093 packets; the sink/source/SAP trio loads without interference; 144 pre-existing foreign `r9Xb` rows in the shared `stream-properties` and 30+ foreign seat processes were live throughout with no effect on the shape laws. |
| **source-loss / relink timing** | player start → first packet; kill → tone stop; restart → re-lock; tap timeline at 48 frames/packet | first tone packet 0.979 s / 0.857 s after the tap starts (player launched at 1.002 / 1.009 s); the last tone-carrying packet precedes the kill by 0.54 / 2.38 s (the tone is *intermittent* at 1 ms ptime, so this is a lower bound on when the tone stopped); after the restart at 7.505 s the first tone packet is at **7.505 / 7.516 s ⇒ re-lock 0.000 / 0.001 s**; the load pass reproduces it (0.001 / 0.002 s). Silence packets continue at ~1 kHz while no client is linked (`node.always-process=true`), so the packet flow is *not* a client-presence witness — only the content is. |

---

## 5. Extensions the scout did not pin

1. **`rtp.ptime`/`rtp.framecount` are stream props, not module args (C16).**
   As module args they are silently dropped (props stay 1.0/48); in
   `stream.props` a *consistent* pair kills the daemon with SIGFPE; an
   inconsistent pair silently mislabels `rtp.framecount` (prop 480, wire 960
   frames / 3852 B / ts delta 960). This is the only arithmetic-fault refusal
   class found, and it is a `stream.c` bug, not a user error.
2. **The unicast acceptance law, exercised with a real packet (C8b).** The
   scout's own stage-e never sent (`send: no-bound-socket`, regex mismatch): the
   socket shows as `127.0.0.1:46202 → 127.0.0.1:46202`. Replayed with a sender
   bound to exactly `source.port`: tone peak 0.5 / g997 803 M + a
   `sync to timestamp` log; from a foreign source port: peak 0.0, no log.
3. **20 s LAN confinement with a byte counter.** 19 588 RTP packets emitted from
   a `local.ifname=lo` sink; the containing 20 s enp7s0 window is **below both
   bracketing idle windows** (9914 pkts / 7.28 MB vs 12 322 / 9.31 MB and
   11 003 / 9.39 MB). Had the stream egressed, +19 588 packets / +4.0 MB would
   appear. A synthetic 3000-packet `SO_BINDTODEVICE(lo)` burst likewise adds
   nothing above matched idle windows (3193 vs 4991/5332/4997 per 8 s). The
   positive control (`local.ifname=enp7s0`) adds ≈ the emitted count
   (quiet +10 171 vs 2166/1188-1879 idle; load +13 910 vs 9022/5155-7820).
   Clarification of the scout's §5.4: the `192.168.0.253` peer it saw in its
   `mcast-lo` arm is **this host itself** — Linux delivers the local copy of a
   lo-bound multicast send to sockets joined on *any* interface, so an
   enp7s0-joined receiver sees the stream with the host's own LAN address.
4. **`sess.ts-offset` repair (C12b).** All five offsets in a ±2048-sample sweep
   around the estimated clock position play the tone (g997 796 M – 852 M),
   i.e. the crafted path needs no clock alignment at all once delivered.
5. **`S24BE`** (C14): loads and runs; wire packet 300 B = 12 + 48 × 6, PT 127.
6. **`rtp-sap` ifname law (C13)**: `join IPv4 group: 239.255.255.255 iface:0`
   without `local.ifname`; `join IPv4 group: 239.255.42.98 iface:1` with
   `local.ifname=lo`; no node is created in either arm. The no-ifname arm's
   enp7s0 tx delta (1038 over ~4.5 s) is within the contemporaneous LAN idle
   band — bounded, but the announcement path is not provably confined.
7. **Two sinks on one destination** (C3b) and **`pw-play` flag position**
   (AX-FLAGORDER) — neither was in the scout's battery.

---

## 6. Imprecisions that are *not* falsifications (arm them differently)

- **Goertzel dominance is a fill metric.** The scout's three stage-b numbers
  (16.7 M / 69.0 M / 53.6 M) differ by 4× because the ring fill differs; my
  quiet reps give 6110× and 164× dominance, load reps 187 639× and 4987×, and a
  smoke rep as low as 1.5×. Arm "997 Hz is the dominant bin" with the ratio, or
  arm peak equality (stable) instead.
- **The receive-path peak overshoot** (scout `[?]`2: 0.581–0.587 vs 0.499969)
  reproduces at 0.569–0.585 (both passes) and remains unexplained; assert
  presence + spectral dominance, not the peak value.
- **`rtp.receiving`/`rtp.ssrc` on the source** are init-time values (`ssrc=0`,
  `receiving=true`, random ts offset `448 550 046 … 2 408 521 541` across four
  loads); only the `sync to timestamp` log line and the recorded content are
  arrival witnesses — the scout said this and it held in every arm.
- **"~1 kHz cadence"** is a nominal rate: the measured single-sink packet rate
  varies **667–939 pkt/s** across legs and passes at 1 ms ptime (two-sink arms
  double it), and the *wall* cadence is not the ts cadence (ts steps 48 + k·16).
- **`net.mtu` is advisory at fixed ptime** (C9 row) and the *default* ptime is
  MTU-derived — both confirmed; the scout's F3/F4 stand.

---

## 7. Contention ledger (foreign, disclosed)

| window | contact | effect |
| --- | --- | --- |
| whole window | 48–60+ foreign `yes` processes (r89-verify load generator) + ≥8 sibling batteries | baseline loadavg 92–127 on 32 CPUs; wall times inflated 2–5×; no shape-law effect |
| whole window | **r93-boundary sibling battery** (`r93b_hog.py` ×12, its own private core, `r93b_*` nodes) | loadavg +12; its private core is separate; never touched |
| 21:34Z–21:57Z | foreign default-node mutations: entry default sink `…hdmi-stereo.99` (+ its monitor source) → exit default `…HiFi__SPDIF__sink.29` / `…HiFi__Line__source.29` | witnessed read-only; **no `set-default-*` was issued by this seat** (the default-node change is foreign, and no file leg in either pass depended on the default node) |
| 21:45Z | sibling commit `3836de94 r97 boundary` landed | HEAD moved mid-window; no r99 file touched |
| 21:47Z (own) | one transient shared-graph node `r99b_sink_sh` + 4 ports, ~4 s, loopback destination | 0 objects and 0 `stream-properties` rows at exit |
| 21:34Z (own) | LAN positive control (`local.ifname=enp7s0`), 8 s | bounded multicast egress on the operator's LAN (239.255.42.99, TTL 1), ≈ 8 k packets, disclosed |
| own | 14 `r99b_hog` processes, 414.6 s, 3010 CPU-s | 0 PipeWire objects, all reaped |

Exit state: 0 `r99b_*` nodes/sockets/processes anywhere (private or shared), 0
`r99b` rows in the shared WirePlumber state, shared daemons 2060/2063/2694
intact, tracked-dirty set = the pre-existing sibling `measure_audio.py` (+ its
`.pyc`) only.

---

## 8. Limits, residual risk, blockers

1. **No truly quiet window exists on this host** (≈50–60 foreign `yes` + the
   r93-boundary battery): "quiet-ish" = 0 own hogs at loadavg ~111. The load
   arm added only ~7 CPU-equivalents to a host already ~3.4× oversubscribed, so
   the strongest supportable load claim is "14 concurrent CPU-bound processes
   were resident for the whole pass and the shape laws did not move".
2. **The enp7s0 counter cannot resolve ≤20 % leakage** at the load-pass noise
   level (idle windows themselves spanned 5155–7820 per 8 s). The confinement
   verdict rests on the dedicated 20 s windows (19 588 packets emitted, window
   *below* both idles), the synthetic control, and the positive control — not on
   the bracketed 8 s arms alone.
3. **The shared-graph leg is a single rep** (~4 s). It proves the client-side
   module works and leaves no residue; it does not characterise shared-graph
   policy (WirePlumber may route/duck differently at scale).
4. **`sess.ts-offset` repair is a measurement, not a derivation**: it shows the
   crafted path needs no alignment, not *why* the receive ring accepts an
   arbitrary ts (the `audio.c:692-711` resync path absorbs the offset).
5. **The SIGFPE is characterised by one arm per pass** (plus the
   inconsistent-pair wire check); the exact division site is read
   (`stream.c:888-891`), not debugged.
6. **Not judged here**: nothing in this report is a shipping decision; the
   canonical Rust runtime remains the only judge, and no `--probe-rtp-r99` row
   was added or modified by this seat.

---

## 9. Artifacts & repro

`corpus/live/r99-boundary/` (untracked): `probes/` (10 files: common, UDP
codec, hog, driver, load runner, quantum check, relink rerun, census,
analyzer, manifest), `receipts/` (14 JSON incl. `verdicts.json`,
`cells-summary.json`, `census.json`, `lan-quiet/load.json`,
`lan-confinement-20s.json`, `axis-order-ptime/wire.json`,
`axis-quantum-metadata.json`, `load-summary.json`, `relink-hogs.json`),
`raw/` (56 + 56 cell receipts + payloads/WAVs/taps), `runs/` (per-pass logs,
`load/hogs-all.json`, `analysis-verdicts.txt`), `conf/` (private core + WP),
`PREDECLARED.md`, `RECEIPTS.md`, `manifest.sha256`.

```
cd corpus/live/r99-boundary
./run_all.sh quiet     # 0-hog pass + LAN arms        (~7 min)
./run_all.sh load      # 14-hog pass + LAN arms       (~8 min)
./run_all.sh analyze   # verdicts + manifest + verify
```

Manifest: **349 files / 82.9 MB, `sha256sum -c` verified 349/349 OK**, manifest
sha256 `b5bbe5ed70fd6e2acb829e28a7fc4a923cea0832cec20a04348f91c5d6013a2c`.

*boundary leaf — replayed, varied, falsified where the receipts demanded it; not judged.*
