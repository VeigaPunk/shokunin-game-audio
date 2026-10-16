# r99 author — the native RTP network-transport surface

Implementation of the round-99 move: an insertion-only `rtp` family in
`corpus/fixtures/measure_audio.py` (appended after the r95 block, before
`def main()`), wired as `--probe-rtp-r99`, plus one new fixture source,
`corpus/fixtures/r99rtp.py` — the seat's own UDP/RTP codec, tone
generator and WAV analyser. **Six entries, 33 legs.** The host has no
`roc` / `snapcast` / `jack-trip`, and the module's only peer in this
family is that fixture, so every r99 claim is read off bytes this
repository produced and parsed itself.

Seat: AUTHOR (leaf). Host `plazir27`, window **2026-10-16 10:35Z →
10:44Z** for the two green passes (dev iterations from 06:0xZ).
Branch `wt-r99` at `6fcff792`. **Zero commits.**

Every armed law is a boundary-surviving claim from
`reports/round-99/r99-boundary.md`. The scout's falsified rows are
dropped or re-armed at the boundary's corrected values — and **one row
the boundary confirmed is re-armed corrected here**, because this seat's
census did not reproduce it (see `c_docs` below).

## Files changed

- `corpus/fixtures/measure_audio.py` — **+2160 / −3**. The only deletions
  are the three shared-line splices the wiring requires (mutex
  `sum([...])` list, `mode` select, receipt `suffix`; identical
  convention to r86–r95).
- `corpus/fixtures/r99rtp.py` — **new**, 459 lines, the fixture source
  (own UDP/RTP codec: `tone`, `recv`, `send`, `wav`).
- `corpus/live/measure_audio-rtp-r99.lock` — fixed-path family lock
  created at runtime (untracked, same convention as r86–r95).
- `corpus/live/r99-author/` — this seat's receipts: both green
  `measurements.json`, both CLI logs, `manifest.sha256`,
  `exit-census.json`.
- `corpus/live/runs/20261016T103556786349Z-rtp-r99/` — green run #1.
- `corpus/live/runs/20261016T104041659031Z-rtp-r99/` — green run #2.
- `reports/round-99/r99-author.md` — this file.

Nothing committed. (`corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`
is the interpreter's build artifact and was already tracked-dirty at
entry, as the r95 scout and boundary both recorded.)

**Cleanup note, recorded rather than hidden.** During teardown the five
non-green development run dirs were deleted, and run #1's dir was
removed in the same sweep. Run #1's `measurements.json` was preserved
byte-identically in `corpus/live/r99-author/` first, so its dir was
restored from that copy: the restored file's sha256
(`fc120288733633452775750c55dea2f8e77b3eaa9cce5aa3cd0d7433ae31fb65`)
is the hash of the preserved receipt, and a run dir holds nothing else.

## Conventions carried over

- Namespace `r99a_<pid>` for every node, sink, source and client name;
  `sess.name = r99a<pid>` so `node.description` and `media.name` are
  seat-owned too; ports in a per-pid window (`46500 + pid % 400`).
- Fixed-path lock `corpus/live/measure_audio-rtp-r99.lock` (flock, never
  `$TMPDIR`); `TMPDIR=~/Projects/shokunin/tmp` for all runs.
- **Private core + private WirePlumber** per entry (own runtime dir ⇒ own
  socket). The shared daemons are never signalled, loaded into or
  reconfigured; **no `pactl set-default-*` is ever issued**.
- Volatile text (ids, serials, ssrc, ts offsets, wall times, loadavg,
  packet rates, the receive-path peak) is recorded, never armed.
- A missing tool / fixture / private core is a **named coverage block**,
  never a silent green; an entry that cannot measure names why.
- r99-local error classes checked before the inherited tables
  (`rtp_r99_no_daemon`, `rtp_r99_bad_args`).

## Entries and legs

### 1. `rtp_census_r99_probe` — availability, absence, documentation (3 legs)

- `c_modules`: **34** native modules in `/usr/lib/pipewire-0.3/`, of which
  **10** are network-capable — `rtp-sink`, `rtp-source`, `rtp-sap`,
  `vban-send`, `vban-recv`, `netjack2-driver`, `netjack2-manager`,
  `pipe-tunnel`, `pulse-tunnel`, `avb`; the three RTP `.so` files are
  hashed into the receipt.
- `c_absent`: `pacman -Q pipewire-zeroconf roc-toolkit snapcast jack-trip`
  → **4 × "was not found"**; `snapcast`/`snapclient`/`roc-send`/
  `roc-recv`/`jack-trip` all absent from PATH.
- `c_docs` — **the one boundary verdict this seat re-arms corrected.**
  C1's "no man page exists for any of the three RTP modules" is
  **CONFIRMED as false on this host**: all three pages ship in
  `pipewire-audio 1:1.6.8-1` and resolve via `man -w`. The **sink** page
  documents `sess.min-ptime` default **2** and `sess.max-ptime` default
  **20** — exactly the defaults C2b measured the module actually using —
  and lists `rtp.ptime`/`rtp.framecount` under **MODULE OPTIONS**, which
  C16 shows the module does not honour there. The **source** page
  documents a different set (`source.ip`/`source.port`,
  `sess.ignore-ssrc`, `sess.ts-direct`, `stream.may-pause`) and no
  min/max-ptime at all. Armed: pages present, sink-page defaults 2/20,
  and `rtp.ptime` under MODULE OPTIONS.

### 2. `rtp_sink_r99_probe` — props, socket, wire, lattice (7 legs)

`pw-cli load-module` held open for the leg (the **client route**: ~1 s
instead of a full core restart, byte-identical on the wire).

- `s_props` (explicit `sess.min/max-ptime = 1`): node is `Audio/Sink`,
  `node.network=true`, `node.always-process=true`, ports
  **`send_FL/send_FR`** (inputs) + **`monitor_FL/monitor_FR`** (outputs),
  `rtp.ptime=1.000000`, `rtp.framecount=48`, `rtp.mime=L16`,
  `rtp.payload=127`, `net.header=28`, `net.mtu=1280`, `rtp.dscp=34`,
  `rtp.ttl=1`, `rtp.rate=48000`, `rtp.channels=2`;
  `node.description` = the session name and `media.name` =
  `RTP Session with <sess.name>`; **one connected UDP socket**
  (`ESTAB … <ephemeral> → <destination>`) — the bind is `0.0.0.0:0` +
  `connect(destination)`, so the sender's port is never the destination
  port. Wire: **204 B**, `V=2`, `PT=127`, marker 0, `seq` +1, ts steps
  every multiple of 16 ≥ 48, and the **peak is exactly `0.499969482`
  (16383/32768) on both channels**. The ts-delta law is armed on the
  *clean* steps; a leg that straddles a 2³² rollover contributes one huge
  delta and it is recorded separately (C4b's own correction, applied).
- `s_default` (no ptime args): **6.458333 ms / 310 frames / 1252 B** —
  C2b's falsification of "the defaults are 1 ms/48 frames".
- `s_lattice_mtu200`, `s_lattice_mtu8000`: 204 B — MTU is advisory at a
  fixed ptime.
- `s_lattice_10_20`: 10.0 ms / 480 / 1932 B.
- `s_lattice_50_100`: 50.0 ms / 2400 / **9612 B** — C9b's falsification
  of the "2048-byte cap", which was the scout's own tap buffer. 9612 =
  12 + 2400 × 4 exactly.
- `s_two`: two sinks on one destination coexist — one wire size, two
  connected sockets with **different ephemeral source ports** and the
  **same destination port**.

### 3. `rtp_source_r99_probe` — shape, crafted delivery, repairs (6 legs)

Source legs run on the **fragment route** (the module is listed in the
private daemon's own config and each leg restarts the core). This is a
measured choice, not a stylistic one — see "Route is a measured law".

- `r_shape` — **sends nothing**, so the init-time fakes are read before
  any packet could have arrived: `media.class=Audio/Source`, ports
  `receive_FL/receive_FR`, `rtp.receiving=true`, `rtp.ssrc=0`, a
  per-load `rtp.receiver-ts-offset`, a group join in the log, and **no**
  `sync to timestamp` line.
- `r_mcast` (C12 corrected): a correctly delivered crafted stream — the
  family's own sender, group `239.255.42.99` on `lo` — **plays**: the
  source records the tone and logs `sync to timestamp`. Armed: the sender
  sent, the module logged `join IPv4 group: 239.255.42.99`, the recording
  is non-silent, and the sync line exists.
- `r_unicast_same` (C8b): a unicast source, sender bound to exactly
  `source.port` → plays.
- `r_unicast_foreign` (C8b): same source, sender from a foreign port →
  **silence, all-zero, no sync line**; and (armed) a unicast source joins
  no group.
- `r_ts_offset` (C12b): `sess.ts-offset` as a module arg plus an
  arbitrary `ts0 = 7000000` → plays.
- `r_s24be` (C14): `audio.format=S24BE` → `rtp.mime=L24`, **300 B** =
  12 + 48 × 6.

### 4. `rtp_refusal_r99_probe` — the refusal lattice (8 legs)

All on the **fragment route**, with no session manager: a module-init
failure is observed as the **core's exit code**.

| leg | input | result |
| --- | --- | --- |
| `x_destip` | `destination.ip=999.1.2.3` | core **rc 234** |
| `x_f32` | `audio.format=F32LE` | core **rc 234** |
| `x_media` | `sess.media="r99a_bogus"` | core **rc 234** |
| `x_srcport0` | `source.port=0` | core **rc 234** |
| `x_ifname` | `local.ifname=r99a_nosuchif` | **loads**; node created, `suspended` |
| `x_ptime_pair` | `rtp.ptime=20 rtp.framecount=960` in `stream.props` | core **rc −8 (SIGFPE)** |
| `x_ptime_module_args` | the same pair as **module args** | silently dropped; props stay `1.000000`/`48` |
| `x_ptime_props_only` | `rtp.ptime=20` in `stream.props` only | `rtp.ptime="20"`, `rtp.framecount="960"` |

The SIGFPE leg is C10c's falsification of the "module-init `-EINVAL` or
nothing at all" dichotomy, and `x_ptime_module_args` is C16: the man page
lists those two keys under MODULE OPTIONS, the module reads them from
`stream.props` only. (A value set through `stream.props` keeps the
literal text the caller wrote — `"20"`, not `"20.000000"` — which the
module only produces for a value it derived itself.)

### 5. `rtp_e2e_r99_probe` — native pair, SAP, relink, confinement (5 legs)

- `e_native` — the scout's and boundary's shape: both modules on the
  fragment route, sink → `239.255.42.99`(lo) → source → `pw-record`.
  **Result this seat measures: the sink's side is exact and the source's
  side is silence**, so the leg is a **named coverage block**, not a
  green and not a red. See "C6 is unmeasured here" below.
- `e_sap` (C13) — fragment route, `sap.ip=239.255.42.98`,
  `local.ifname=lo`: **no node is created**, and the module logs
  `join IPv4 group: 239.255.42.98 iface:1`. Armed: zero own nodes and the
  join line on the named interface.
- `e_relink` (AX-RELINK) — the sink keeps emitting while no client is
  linked (9001 packets captured), and a second player re-locks: **84.5 %**
  of the captured frames are non-zero. Armed: flow > 0 and content > 2 %.
- `e_lan` (C7) — 20 s idle / 20 s arm / 20 s idle on the default-route
  interface, with ~20 000 packets emitted from a `local.ifname=lo` sink.
  Both green passes put the **arm window at or below the bracketing idle
  band** (run 1: −232; run 2: −1322), which is the boundary's own
  strongest form, and the leg arms that form directly.
- `e_lan_control` — the **positive control, disclosed**: the same sink
  bound to the operator's LAN interface for one 6 s tone. It adds **8626**
  (run 1) / **6975** (run 2) packets against a nominal 6000-packet
  emission — 144 % / 116 % — so the counter demonstrably resolves a real
  leak and the confinement verdict is not vacuous.

### 6. `rtp_axis_r99_probe` — the independent axes (4 legs)

- `a_quantum`: `clock.force-quantum` 256 then 1024 in the private core's
  own settings store. Armed as the **falsification**, not set equality:
  `48` is a step in both, every clean step is a multiple of 16, and no
  step is `quantum/64` (4 and 16). The exact sets are recorded and **did
  differ** between the arms (`[48]` vs `[48, 64]`) in both green passes,
  so the scout's "multiples of 16 = the graph quantum/64" is falsified as
  a mechanism while set equality is not asserted.
- `a_rate`: module `audio.rate=44100` against a 48000 graph →
  `rtp.rate=44100`, `rtp.ptime=0.997732`, `rtp.framecount=44`, **188 B**
  packet, and the clean 48-step lattice is destroyed.
- `a_order`: reversing the first two module args reproduces the canonical
  props and the 204 B wire.
- `a_target_pos`: `pw-play --target X <file>` **and**
  `pw-play <file> --target X` both stream (~16 000 packets, one size).

## Evidence

- Implementation sha256 (both green runs identical bytes):
  `measure_audio.py 1bb2f98bb9deffa9674ee0e643040191da70100f49c21685f82044352bf58fbf`,
  `r99rtp.py 36b6b6f8ae332d768e6129fc1fbcf56e634c2e636ceaaa043f97ad11cccfa6a1`.
- Run 1: `corpus/live/runs/20261016T103556786349Z-rtp-r99/measurements.json`
  — `failures: {}` in all six r99 entries.
- Run 2: `corpus/live/runs/20261016T104041659031Z-rtp-r99/measurements.json`
  — `failures: {}` in all six r99 entries.
- `corpus/live/r99-author/` carries byte-identical copies of both
  receipts, both CLI logs, a `manifest.sha256`, and `exit-census.json`.
- Post-run census (both passes): **0 `r99a` objects in the shared graph,
  0 `r99a` processes, 0 `r99a` rows in the operator's
  `stream-properties`, 0 private sockets left**; shared defaults
  `…HiFi__SPDIF__sink` / `…HiFi__Line__source` unchanged; the shared
  daemons are the systemd user units (MainPIDs 3549292/3549293/3549294)
  and were never signalled. **No `pactl set-default-*` was ever issued.**
- The two coverage blocks that *do* fire are named in the receipt
  (`legs.e_native.verdict` carries both sides' measurements; `e_lan`
  carries the resolution arithmetic) — never a silent green.

## The route is a measured law, not a convenience

Two arming routes are used and the choice is itself measured:

- **FRAGMENT route** — the module sits in the private daemon's own
  `context.modules` drop-in. A module-init failure takes the **core** down
  with it, which is the only way to observe the rc 234 / rc −8 classes,
  so every `x_*` leg and every *source* leg uses it.
- **CLIENT route** — `pw-cli load-module` held open for the leg. Cheap
  and byte-identical on the wire (the boundary's AX-GRAPH), so every
  *sink* leg uses it.

**A client-side RTP source does not receive.** Measured both ways with the
same module version, the same args and the same private core: on the
client route `ss` shows the socket bound to `239.255.42.99:<port>` in the
same network namespace and the same reuse group, and the source records
silence and logs no join; on the fragment route the same args produce
`join IPv4 group: 239.255.42.99` and a tone-carrying recording. A
client-side load also writes the module's own `pw_log` lines to
`pw-cli`'s stdout rather than to the core log, which is why `e_sap` was
moved to the fragment route too — otherwise its join line is unmeasurable.

## C6 is unmeasured here, not falsified

`e_native` is a **named coverage block**. What this seat measured, in
both green passes:

- the sink **emits correctly**: a wildcard, lo-joined tap read ~6000 ×
  **204 B** packets carrying the **exact `0.499969482`** peak (the wire
  law of `s_props`, independently witnessed on the native path);
- the sink's socket is **`192.168.0.253%lo:<port> → 239.255.42.99:<port>`**
  — the host's LAN address stamped on a packet that leaves `lo`, because
  `module-rtp-sink` sets no `IP_MULTICAST_IF` and the kernel's route
  lookup for the group selects the LAN interface;
- the co-located source, bound to the **group**, recorded **silence**
  (`peak 0.0`, `rtp.ssrc` still `0`) while logging `sync to timestamp`
  once;
- the **loopback-unicast** form is structurally unavailable:
  `module-rtp-source`'s unicast branch **connects** its socket, so it
  accepts only datagrams whose source port is exactly `source.port`, while
  the sink binds `0.0.0.0:0` — C8b's own law makes that pair impossible.
  (That was measured, then abandoned; the leg was rewritten.)

The boundary's own `e2e_native` receipts recorded the tone over this same
multicast path (`peak_l` 0.580841 / 0.584717). The difference is host
state — a receiver-side address check, not a module law — so the leg
records both sides and blocks; it does **not** claim C6 and does **not**
falsify it. The crafted path that C12 actually rests on (`r_mcast`,
`r_unicast_same`) **is** green, so the falsification of the scout's
clock-gating attribution is carried by legs that reproduce.

## Remaining risks / blockers

- None blocking. Honest exposures, recorded rather than hidden:
  - **C6 unmeasured** (above): the native pair's source side does not
    accept the sink's lo-bound multicast on this host. A follow-up should
    pin the receiver-side address check (the sink's `%lo` socket carrying
    `192.168.0.253`) and, if it is an `rp_filter`-class behaviour, arm the
    leg with a group the kernel routes via `lo`.
  - **`a_quantum` set equality did not reproduce**: the clean lattice was
    `[48]` at quantum 256 and `[48, 64]` at 1024 in both green passes.
    The mechanism claim is armed; the exact set is recorded. A follow-up
    with more reps should say whether the extra `64` step is a scheduling
    artefact.
  - **The LAN counter's resolution**: the idle band on `enp7s0` spanned
    6599–8505 packets per 20 s in the green passes (0.33–0.43 × the
    emitted volume). The leg therefore arms the boundary's *strongest*
    form (arm ≤ idle band), which both passes satisfied, and falls back to
    a **coverage block** when the arm exceeds the band and the band is too
    wide to resolve it. The positive control (~116–144 % of a real
    emission) is what keeps the verdict non-vacuous.
  - **The receive-path peak overshoot** (scout `[?]`2) reproduced: the
    source-side recording clips at **1.0** in every tone-carrying leg
    here (the boundary saw 0.569–0.587 on the same path). It remains
    unexplained, so it is **recorded, never armed** — the armed peak law
    lives on the **wire**, where it is exact to 9 decimals in every rep of
    both passes.
  - **Shared host daemon**: the family's cores are private and the shared
    daemons were never touched, but the host was heavily loaded throughout
    (60+ foreign `yes` processes and sibling r100/r93 batteries). Every
    wall-time-sensitive quantity is recorded; the *shape* laws (packet
    sizes, ptime table, prop sets, socket shapes, refusal classes,
    lattice) were identical across both green passes.
  - **`[?]` opus / MIDI / VBAN / netjack2 / avb remain unmeasured** —
    named gaps, unchanged from the scout.
  - The scout's and boundary's `stream-properties` rows are still in the
    operator's store (the r90 class: no CLI deletes them); **this seat
    added none** and the exit census proves it.

*Leaf seat — implemented, measured, and green on frozen bytes; not judged.*
