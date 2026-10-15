# r99-boundary — PREDECLARED attacks (frozen before the battery)

Target: `reports/round-99/r99-scout.md` (native RTP transport surface, private
core, `r99s_*`). This seat replays the armed cells with **fresh processes**,
**quiet-ish (0 own hogs) and under load (>=12 own hogs, argv-marked
`r99b_hog`)**, and varies the named axes.

Namespace `r99b_*`; ports 46200–46299; private core + private WirePlumber under
`corpus/live/r99-boundary/run`. Own PIDs only (pid files + argv marker
`r99b_hog`/`r99b_`); never a foreign sweep. Zero tracked writes.

## Claims to pin (C) and the attack that would falsify each

| id | claim (from r99-scout) | attack |
| --- | --- | --- |
| C1 | 34 native modules, 10 network-capable; `roc`/`zeroconf`/`snapcast`/`jack-trip` absent; no RTP man pages | re-census (`ls`/`pacman -Q`/`man -w`) under load |
| C2 | sink node props: `rtp.ptime=1.0`, `framecount=48`, `mime=L16`, `payload=127`, `net.mtu=1280`, `net.header=28`, `dscp=34`, `ttl=1`, `node.network=true`, `media.class=Audio/Sink` | load sink with explicit `sess.min/max-ptime=1`, read `pw-dump` |
| C2b | **"the sink defaults are a 1 ms / 48-frame L16 stream"** | load sink with **no** ptime args; falsified if the true defaults are `2/20` → `6.458333 ms / 310 frames / 1252 B` (the scout's own §3.4 "default" row) |
| C3 | sink socket = connected UDP, ephemeral source port (`bind 0.0.0.0:0` + `connect`) | `ss -unp` on the core pid, 3 reps |
| C3b | two sinks on one destination coexist (ephemeral binds) | two `r99b_*` sinks in one core, one receiver, two SSRCs/ports |
| C4 | wire: 204 B, V=2, PT=127, seq+1, one size, ~1 kHz; ts deltas multiples of 16 | capture with a 64 KiB recv buffer; full delta sets |
| C4b | **report §1.4/§2 says the ts-delta set is `{48,80,96,112,128,144}`** | receipts of the scout itself show `160,176` too; measure the full set |
| C5 | tone survives the wire sample-exact: peak `0.499969` both channels, 997 Hz dominant | decode payload; align against a locally generated `int(0.5*32767*sin)` tone for byte-exact match |
| C6 | native end-to-end (sink→mcast lo→source→`pw-record`) carries the tone | replay, tap + record |
| C7 | `local.ifname=lo` keeps the multicast send off the LAN (enp7s0 delta below idle) | 15 s arms: idle / mcast-lo / mcast-en; counter deltas |
| C8 | `source.port=0` is a hard init error (`-EINVAL`, rc 234, "invalid source.port") | replay ×3 |
| C8b | unicast `source.ip` binds `INADDR_ANY:port` + `connect(peer)`; only packets **from `source.port`** are accepted | real send from the exact port and from a foreign port; the scout's own stage-e never sent (`no-bound-socket`) |
| C9 | packetization table: 1/1→204 B @ MTU 200/8000/1280; 2/20→6.458333/310/1252; 10/20→10.0/480/1932; 50/100→50.0/2400/**2048 B** | replay all 6 cells |
| C9b | **"50/100 → 2400 frames but 2048 B on the wire (2048-byte packet cap)"** | the scout's own tap reads `recvfrom(2048)` — a **tap cap**. Re-capture with a 64 KiB buffer; falsified if the datagram is `12 + 2400*4 = 9612 B` |
| C10 | refusals: bad dest ip / `F32LE` / bogus `sess.media` → rc 234 core death; bad `local.ifname` / `net.mtu=64` load fine | replay ×1 each (no WP for the refusal class) |
| C10b | **scope of "load fine"**: measured without a session manager | replay bad-ifname **with** WP: does the node go running and error at stream start? |
| C11 | `rtp.receiving=true` is faked at init (never an arrival witness); `rtp.receiver-ts-offset` random per load | read props before any packet; two loads |
| C12 | crafted RTP with correct headers but arbitrary ts → silence while `rtp.receiving=true`; mechanism = ring vs graph clock | **correct delivery path** (multicast on lo; the scout's crafted arms actually sent unicast to 127.0.0.1) |
| C12b | (scout's own `[?]` #1) `sess.ts-offset` **as a module arg** can repair the crafted sender | sweep `sess.ts-offset` around the measured clock position; non-silence would *prove* the mechanism, persistent silence would leave it unproven |
| C13 | `rtp-sap` loads with no node, joins `239.255.255.255` with `iface:0` when `local.ifname` is absent, starts listener + send timer | replay; `ss` membership + LAN counter; then `local.ifname=lo` arm |
| C14 | supported formats: no `S24LE`/`S32`/`F32`; `S24BE` is supported | load `S24BE` (wire size 12+48*6=300 B) |
| C15 | load invariance: every cell above is the same under load as quiet-ish | quiet vs load sha/verdict compare |

## Axes

| axis | variation |
| --- | --- |
| private-core vs shared graph | (a) daemon-side module in the private core (scout shape); (b) client-side `pw-cli load-module` against the **private** core; (c) client-side against the **shared** core (`r99b_*` node, loopback dest, dies with client, residue checked) |
| rates / quantum | private-core `default.clock.quantum` 256 / 1024 / 4096; `default.clock.rate` 48000 / 44100; module `audio.rate` 48000 / 44100 — do the ts-delta multiples track `quantum/64`? |
| flag order | module-arg order reversed; duplicate `sess.min-ptime` (which wins?); `rtp.ptime` in `stream.props` vs module arg; `pw-play <file> --target X` vs `--target X <file>` |
| sibling presence | two sinks + one source + SAP in one core; foreign nodes/processes live in the shared graph (witnessed read-only) |
| source-loss / relink | player start→first packet, kill→silence, restart→re-lock; sender stop→restart while the source keeps running |

## Falsification priorities

1. **C9b** (a "wire cap" that may be the tap's own buffer) — if true it changes
   the packetization table and the "50 ms" content claim.
2. **C2b** ("defaults") — the scout's §1.2 wording contradicts its own §3.4.
3. **C12/C12b** — the crafted-sender silence may be a delivery-path artifact
   (unicast vs multicast) rather than the clock-gating mechanism.
4. **C10b** — "loads fine" may be a no-session-manager artifact.
5. C8b — the unicast acceptance law was never exercised with a real packet.
