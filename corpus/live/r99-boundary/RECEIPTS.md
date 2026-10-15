# r99-boundary receipts — index

`receipts/` (JSON, machine-readable):

| file | what |
| --- | --- |
| `verdicts.json` | 28 verdicts, each evaluated per pass (quiet / load) with the raw detail |
| `cells-summary.json` | per-pass cell counts + windows (from `raw/`) |
| `census.json` | C1 static census + module `.so` sha256s + toolchain |
| `lan-quiet.json`, `lan-load.json` | 5-window bracketed LAN arms per pass (idle / mcast-lo / idle / mcast-en / idle) |
| `lan-confinement-20s.json` | the 20 s confinement windows (19 588 RTP packets emitted, enp7s0 below both idles) |
| `load-summary.json` | hog lifecycle + CPU accounting (14 hogs, 3010 CPU-s, all reaped) |
| `axis-quantum-metadata.json` | effective `clock.quantum` (256/1024/2048) vs the ts lattice |
| `axis-order-ptime.json` | `rtp.ptime`/`rtp.framecount` as module args vs `stream.props` (incl. the SIGFPE death) |
| `axis-order-wire.json` | the wire size when the `rtp.framecount` prop disagrees with the actual packet |
| `relink-hogs.json` | the second (load) hog cohort used for the relink rerun |

`raw/<pass>/<cell>-rep<N>.json` — one file per process leg (56 per pass), with
the loadavg / procs_running at entry and exit, wall time, and the measured
artifacts inline. Payloads/WAVs/taps live in `raw/cells-quiet/` and
`raw/cells-load/`; the LAN arms in `raw/lan-quiet/` and `raw/lan-load/`.

`runs/` — `quiet.log`, `load.log`, `lan-quiet.log`, `lan-load.log`,
`relink-load.log`, `analysis-verdicts.txt`, `load/hogs-all.json`, and the last
`core.log`/`wp.log` of the private core.

`PREDECLARED.md` — the frozen attacks (claims + falsifiers) written before the
battery. `manifest.sha256` — sha256 of every seat artifact (excluding `run/`
and itself).
