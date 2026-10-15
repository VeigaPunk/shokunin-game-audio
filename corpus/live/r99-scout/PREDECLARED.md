# r99-scout — PREDECLARED hypotheses (frozen before the battery)

Written after the *recon* phase (module inventory, one private-core sink
smoke test, socket-shape reading) and **before** stages a/b/c/d/d0/d2/e/f/h ran.
The recon observations are listed separately so the battery's hypotheses are not
trivially true.

## Recon facts already in hand when this file was written
- `libpipewire-module-rtp-{sink,source,sap}.so` exist (34 native modules).
- A private core (shipped `pipewire.conf` + fragment, `core.daemon=true`,
  `core.name=pipewire-0`) loads an RTP sink in `context.modules`; the node goes
  `running` only when a private WirePlumber is present (r97 arming shape).
- `pw-cli load-module` loads the module **client-side** (node dies with pw-cli;
  daemon log silent).
- The sink's socket appears as a connected UDP socket with an ephemeral source
  port; silence packets flow at ~1 kHz, 204 B, PT 127.
- `SO_BINDTODEVICE(lo)` + `IP_MULTICAST_IF=127.0.0.1` keeps a multicast send
  off enp7s0 (synthetic burst: 10–14/20 000 vs 20 087/20 000 default-route).

## Hypotheses (each with the attack that would falsify it)

- **H1 (availability).** The three RTP modules are the whole native network
  transport on this host; `roc`, `zeroconf`, `snapcast`, `jack-trip` are absent
  at every level (package, binary, module).
  *Falsified by*: any `*roc*`/`*zeroconf*`/`*raop*` module or binary.
- **H2 (sink shape).** The sink is a real `Audio/Sink` with ports
  `send_FL/FR` + `monitor_FL/FR`, `node.network=true`, and defaults
  S16BE/48 kHz/2 ch, `sess.min/max-ptime=2/20`.
  *Falsified by*: `playback_*` port names, or non-default format props.
- **H3 (wire format).** Packets are 12-byte RTP headers, V=2, PT=127, seq+1,
  timestamp steps of `rtp.framecount`, one size per configuration.
  *Falsified by*: a PT other than 127, or a size ≠ 12 + framecount·stride.
- **H4 (content).** A 997 Hz tone played into the sink arrives in the captured
  RTP payloads with peak ≈ 0.5 and 997 Hz spectral dominance.
  *Falsified by*: silence, or a non-997 Hz spectrum.
- **H5 (end-to-end).** The native pair (sink → multicast on lo → source →
  `pw-record`) carries the tone.
  *Falsified by*: a silent recording, or a link/topology failure.
- **H6 (LAN confinement).** `local.ifname=lo` + `SO_BINDTODEVICE` keeps the
  multicast send off `enp7s0` (counter-verified), while the positive control
  (`local.ifname=enp7s0`) shows up in the counter.
  *Falsified by*: an enp7s0 `tx_packets` delta ≈ the packet count in the
  `mcast-lo` arm.
- **H7 (packetization).** `sess.min/max-ptime` sets `rtp.ptime`/`framecount`
  and the wire packet size; `net.mtu` only matters for the *default* ptime
  window.
  *Falsified by*: an MTU change altering a fixed-ptime packet.
- **H8 (refusals).** Invalid destination IP / unsupported format / unsupported
  media are module-init errors that kill the core (`-EINVAL`); invalid
  `local.ifname` and tiny `net.mtu` are **not** refused at load.
  *Falsified by*: a load-time refusal for the latter two, or a clean load for
  the former three.
- **H9 (source shape).** `source.port` must be non-zero; a unicast `source.ip`
  produces a *connected* socket (`bind INADDR_ANY:port` + `connect(peer)`);
  `rtp.receiving=true` is set at init and is not an arrival witness.
  *Falsified by*: a working `source.port=0`, a plain (unconnected) unicast
  socket, or `rtp.receiving=false` on a fresh source.
- **H10 (third-party sender).** A crafted RTP stream with correct headers but
  an arbitrary timestamp offset will **not** produce audio in the graph even
  though it is received (the source's ring is clock-gated).
  *Falsified by*: audio appearing from a crafted stream with an arbitrary
  timestamp offset.
- **H11 (SAP).** `rtp-sap` loads without a node, joins `sap.ip` on the
  interface named by `local.ifname` (or `iface:0` when absent) and starts a
  listener + send timer.
  *Falsified by*: a node being created, or a refusal to load.
- **H12 (hygiene).** No shared-graph object, no shared daemon, no
  `set-default-*`, no tracked file is touched; the private core/WP leave no
  shared residue.
  *Falsified by*: any `r99s` object in the shared graph, a shared-daemon
  signal, or a non-`??` `git status` line.

## Predeclared falsification priorities
1. H5 first (the headline) — a silent recording would demote the whole surface
   to "presence only".
2. H4 (content) — a wire-format-correct but silent payload would point at the
   adapter/format negotiation.
3. H9/H10 (source shape) — the connected-socket and clock-gating laws are the
   ones an author must not get wrong.
