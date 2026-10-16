# r95 author — the JACK ↔ PipeWire interop lattice

Implementation of the round-95 move: an insertion-only `jack` family in
`corpus/fixtures/measure_audio.py` (appended after the r89 block, before
`def main()`), wired as `--probe-jack-r95`, plus one new fixture source,
`corpus/fixtures/r95jack.c` — the seat's own JACK client, compiled into
each entry's temp dir with `gcc -O1 -w -ljack -lm`. Five entries,
**24 legs**. Every armed law is a boundary-surviving claim from
`reports/round-95/r95-boundary.md`; the scout's falsified/refined rows are
dropped or re-armed at the boundary's corrected values.

Seat: AUTHOR (leaf). Host `plazir27`, window **2026-10-16 08:52–08:56Z**.
Branch `wt-r95` at `5a632a4f`. **Zero commits.**

## Files changed

- `corpus/fixtures/measure_audio.py` — **+1805 / −3**. The only
  deletions are the three shared-line splices the wiring requires
  (mutex `sum([...])` list, `mode` select, receipt `suffix`; identical
  convention to r86–r89).
- `corpus/fixtures/r95jack.c` — **new**, 764 lines, the fixture source
  (own JACK client; modes `info shape rtprio rtprio_poison tone stall
  bufsize latency transport metadata xconnect`; `R95A_NAME` env client
  name override so the seat pid rides in every exact-name open).
- `corpus/live/measure_audio-jack-r95.lock` — fixed-path family lock
  created at runtime (untracked, same convention as r86–r89).
- `corpus/live/r95-author/` — this seat's receipts (copies of the two
  green `measurements.json`, the two CLI logs, `manifest.sha256`,
  `RECEIPTS.md`, `exit-census.json`).
- `corpus/live/runs/20261016T085442157241Z-jack-r95/` — green run #1.
- `corpus/live/runs/20261016T085527000328Z-jack-r95/` — green run #2.
- `reports/round-95/r95-author.md` — this file.

Nothing committed. (`corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`
is the interpreter's build artifact and was already tracked-dirty at entry,
as the r95 scout and boundary both recorded.)

## Conventions carried over

- Namespace `r95a_<pid>` for every node, sink and client name; the
  private `r95arole<pid>` `media.role` key on the one `pw-play` follower.
- Fixed-path lock `corpus/live/measure_audio-jack-r95.lock` (flock,
  never `$TMPDIR`); `TMPDIR=~/Projects/shokunin/tmp` for all runs.
- Name-verified teardown: re-read the module table immediately before
  firing and unload only the index whose args carry our `sink_name=`;
  residual `r95a_<pid>` nodes destroyed by id via `pw-cli destroy`; final
  `sinks_gone` / `own_nodes_after` census armed.
- Never `pactl set-default-*`; every spawned process is its own session
  leader, bounded by SIGTERM→SIGKILL process-group escalation.
- Volatile text (ids, serials, uuids, nsec counters, `cpu_load`, wall
  times, loadavg, sibling driver names, the RT-priority garbage values,
  capture shas/frames) is recorded, never armed.
- r95-local error classes checked before the inherited tables
  (`jack_r95_no_daemon`, `jack_r95_unknown_mode`).
- A missing compiler / header / libjack / tool is a **named coverage
  block**, never a silent green; `_jack_r95_run`'s `mid` hook is the
  concurrent witness (a `pw-dump` / `pw-metadata` snapshot taken while
  the client runs) and a witness exception can never abort the leg.

## Entries and legs

### 1. `jack_surface_r95_probe` — availability + citizen shape (3 legs)

- `a_avail`: `jackd`/`jack_lsp`/`jack_connect` **absent**, `pw-jack`
  present, `pacman -Q pipewire-jack` → `1:1.6.8-1`, libjack sha256
  recorded, `nm -D --defined-only` → **168 exported `jack_*` text
  symbols** and the exact absent class (`jack_net_open`,
  `jack_client_activate`, `jack_uuid_to_string`, `jack_error`,
  `jack_info`, `jack_log`, `jack_create_adapter`) plus the present class
  (`jack_session_notify`, `jack_reserve_client_name`, both RT-priority
  accessors, `jack_set_buffer_size`, `jack_connect`, `jack_set_property`,
  `jack_transport_reposition`); version `"3.1.6.8 (using PipeWire
  1.6.8)"`, `version_ints [3,1,6,8]`.
- `s_shape` (own null sink present, **not** linked): `client.api=jack`;
  node `group.dsp.0` / `media.category=Duplex` / `media.role=DSP` /
  `node.always-process=true` / no `media.class`; the five ports carry
  `port.alias=<client>:<port>`, `object.path=<client>:output_<n>`,
  `port.direction`, `format.dsp="32 bit float mono audio"`;
  `jack_port_flags` round-trips **2 / 1 / 6 / 18** for
  `out`/`in`/`outp`/`outt` and **2** for `outm` (see the corrections
  below); `port.physical` on `outp`, `port.terminal` on `outt`, **no**
  prop and no `port.extra` on `outm`; monitor API `request_monitor_rc=0`,
  `monitoring_input=1`, `ensure_monitor_rc=0`, **0 links**;
  `out_connected=0` and no link touching the client; the JACK census
  contains all five own ports and resolves each; the null sink's rendered
  alias is exactly `<device.description>:playback_MONO` while its
  `object.path` is `<node.name>:playback_0`; driver resolves to
  `Dummy-Driver` (`node.driver=true`, `priority.driver=200000`).
- `s_liveness` (no seat sink at all): `cb=85` in **both** green runs
  (1.8 s), frames advance, driver `Dummy-Driver` — the boundary's F1
  (the always-process node keeps the fallback driver running; it is
  never idle).

### 2. `jack_addr_r95_probe` — the addressing law (4 legs)

Both domains are witnessed: the probe's own `jack_port_connected` /
`jack_port_get_connections` **and** a concurrent `pw-dump` link edge.

- `x_rendered` → dst `<device.description>:playback_MONO`:
  `src_found=true`, `dst_found=true`, `connect_rc=0`, `connected=1`,
  edge `r95a_<pid>_xc:out|->r95a_ns_<pid>:playback_MONO`.
- `x_native` → dst `<node.name>:playback_MONO`: `dst_found=false`,
  `connect_rc=22 (EINVAL)`, `connected=0`, **no** edge.
- `x_fillalias` (`PIPEWIRE_PROPS='{ jack.fill-aliases = true }'`) → dst
  `<node.name>:playback_0`: `dst_found=true`, `connect_rc=0`, edge
  present. The connection list reports the **canonical rendered name**
  (`r95a_ds_<pid>:playback_MONO`), not the alias that was used — an
  author-level reading of the same law.
- `x_corner` (the F6 corner: `node.description == node.name`):
  `dst_found=true`, `connect_rc=0`, edge present; the graph snapshot
  proves the two names coincide.

### 3. `jack_bytes_r95_probe` — both byte witnesses (2 legs)

- `b_jack2pw`: the probe's 997 Hz / amp-0.5 tone is `jack_connect`ed into
  a probe-owned null sink and captured on its monitor by
  `pw-record -P stream.capture.sink=true --target <ns>`. Armed: the link
  edge, `conn_rc=0`, capture peak ∈ [0.4985, 0.5005] (measured **0.5**
  both runs), rms/sine-ideal ∈ [0.80, 1.02] (0.9821 / 0.9165), nonzero
  fraction ≥ 0.70, frames ∈ [60000, 300000], and the 997 Hz energy
  within [0.90, 1.03] × `(0.25·cb·bufsize_live)²` (measured **0.9534 /
  0.9541**). The whole-file sha256 (5dc9f06… vs be178a25…) and the
  frames (88064 vs 102400) differ between the two runs and are
  **recorded, never armed** — the boundary's F2 window law, encoded.
- `b_pw2jack`: an own int16 fixture tone (1.5 s, 997 Hz, int16 peak
  **16383**) is played by `pw-play` with `node.autoconnect=false` and
  linked into the probe's input. Armed: the `pw-link` edge, `in_peak`
  **exactly** the source's own `peak_i16/32768 = 0.499969482` (Δ < 1e-9,
  both runs), `in_nonzero` ∈ [30000, 75000] (53245 both runs — the
  player is linked after it starts, so the head of the tone is lost and
  the band is a fraction, not an exact count), `cb_in_nonzero` ≥ 10, and
  the 997 Hz energy within [0.985, 1.005] × `(0.25·in_nonzero)²`
  (measured **0.9999812** in both runs, identical to 6 decimals).

### 4. `jack_quantum_r95_probe` — the period-size lattice (10 legs)

- `q_default`: `jack_set_buffer_size(2048)` **inactive** → rc 0 but
  `jack_get_buffer_size` still 1024 (armed as *unchanged*, i.e. the
  latency default, not as the literal 1024); after `jack_activate` →
  `bufsize_activated=2048` and node prop `node.force-quantum="2048"`;
  `settings clock.force-quantum` stays `"0"`.
- `q_live`: a live `jack_set_buffer_size(512)` → rc 0,
  `bufsize_after_set_active=512`, `bufsize_cbs` 1→2,
  `last_bufsize_cb_after=512`, **and the node prop is rewritten to
  `"512"`** (an author-level extension: the boundary measured the
  effective size and the callback, not the prop).
- `q_cross`: a second JACK client opened during the window reads
  `bufsize_active=2048` — the per-client prop moves the graph quantum for
  other clients.
- `q_env` / `q_wrapper`: `PIPEWIRE_QUANTUM=512/48000` and
  `pw-jack -p 512` produce the same node props
  (`force-quantum="512"`, `force-rate="48000"`) and
  `bufsize_activated=bufsize_live=512`.
- `q_env_rate`: `PIPEWIRE_QUANTUM=512/44100` lands `force-rate="44100"`
  and the client **runs** at 44100 (`srate_active=srate_live=44100`,
  `bufsize_live=512`) despite `clock.allowed-rates=[ 48000 ]`;
  `clock.rate` is unchanged after the arm.
- `q_bufsize1` (the F7 nuance): without the opt-in, `set_buffer_size(1)`
  writes node prop `force-quantum="1"` and the effective bufsize is
  **4** (armed as a 1..8 band, recorded exactly).
- `q_global` + `q_global_second` + `q_global_reset`: with
  `PIPEWIRE_PROPS='{ jack.global-buffer-size = true }'`,
  `jack_set_buffer_size(512)` writes `settings clock.force-quantum="512"`
  (visible during and **after** the writer exits), a second client reads
  `bufsize_active=512`, and `jack_set_buffer_size(1)` restores `"0"`.
  The settings store is diffed before/after: **no key moved except the
  one this arm owns** (`settings_moved: []`).

### 5. `jack_defects_r95_probe` — the broken families (5 legs)

- `d_xrun_stall`: 8 × 150 ms in-callback stalls → `stall_cycles=8`,
  `cb=36`, `xrun_cbs=1` (armed as an envelope ≤ 1 — a client-aware
  counter would fire ≥ 8), `xrun_delayed_usecs=0.0`. The arm is
  deliberately an envelope, not the boundary's exact 0: the count is a
  *driver*-counter divergence (F3), and the leg is a coverage block (not
  a failure) if the client does not return inside the bound.
- `d_rtprio_poison`: the stack-poison control returns the pattern
  verbatim — `poison_aa` → `0xaaaaaaa0` (masked), `poison_bb` →
  `0xbbbbbbb0`, 3 samples each, while the plain baseline in the same run
  reads `77/82` then garbage (`-1359737185`, `-1`, …).
- `d_latency`: default and post-set ranges are `[0,0]/[0,0]` (a set is
  invisible before activation); after activation exactly `[100,200]` /
  `[10,20]`, `total=150`, `recompute_rc=0`, the input port stays `[0,0]`.
- `d_transport`: state `0` before and after activation; `start` → `1`
  with the frame advancing (23552 / 22528); `stop` → `0` with the frame
  frozen; `locate(123456)` rc 0 and `reposition` rc 0 leave the frame
  **unchanged**; the connected port reports `out_connected=1`.
- `d_metadata`: set/get round-trip (`value1`/`text/plain`, port
  `portval`), missing key → `-1`, `own_desc_count=2`, `remove` rc 0 with
  the client's own getter still stale (`value1`), the live `default`
  store row `r95a/key1` keyed by the object's **registry id** (row
  subject == the node's pw-dump id; the port row carries the port id),
  and the rows gone after the writer exits.

## Evidence

- Implementation sha256 (both runs identical bytes):
  `measure_audio.py 164a915825dd054b4d0e20d9eee83df9c3196b73531ac58b1622e93d7c1d79da`,
  `r95jack.c 55d4d4111bd8d46be743d0425a40dc8d938d15e071ce37f460db70de0df997be`.
- Run 1: `corpus/live/runs/20261016T085442157241Z-jack-r95/measurements.json`
  — `failures: {}` in all five r95 entries, `coverage_blocked` empty.
- Run 2: `corpus/live/runs/20261016T085527000328Z-jack-r95/measurements.json`
  — `failures: {}` in all five r95 entries, `coverage_blocked` empty.
- `corpus/live/r95-author/` carries copies of both receipts, the two CLI
  logs, a `manifest.sha256`, and `exit-census.json`.
- Post-run census (both runs, `exit-census.json`): 0 `r95a` modules, 0
  `r95a` nodes, 0 `r95a` clients, 0 probe processes,
  `sinks_gone` all-true, `own_nodes_after: []`,
  **0 `stream-properties` rows from this seat**, `clock.force-quantum=0`,
  `clock.rate=48000`, `clock.quantum=1024`, `allowed-rates=[ 48000 ]`.
  No `pactl set-default-*` was ever issued; the foreign default-source
  churn seen between the two censuses is a sibling seat's
  (`r91a_src_*`), recorded as a confound.

## Boundary corrections actually encoded

- **F1 (driver-id)**: `s_liveness` runs with no seat sink and arms the
  `Dummy-Driver` resolution + advancing frames; if a foreign node is the
  resolved driver the leg records a **coverage block** naming it instead
  of pretending the fallback law held.
- **F2 (byte identity is a window artifact)**: both byte legs arm
  peak / nonzero fraction / energy *ratios* against the tone that
  produced them; the capture sha256, frames and rms are recorded — the
  two green runs' shas differ (5dc9f06… / be178a25…) exactly as the
  boundary predicted.
- **F3 (xrun count is a driver divergence)**: the stall arm arms
  `xrun_cbs ≤ 1` against 8 deliberate stalls and records the delayed
  values; no startup-artifact claim is made.
- **F4 (the `sink_properties` parse artifact)**: every null sink uses
  the **space-separated** form, so `state.restore-props` parses to
  boolean false and `device.description` lands exactly; the teardown
  witnesses the `stream-properties` store and fails if this seat left a
  row (`stream_properties_own_rows: []` in all five entries, both runs).
- **F6 (the rendered/native corner)**: armed as its own leg
  (`x_corner`) with the graph proving `description == name`.
- **F7 (the reset is metadata-only)**: `q_bufsize1` arms the node prop
  `"1"` and the effective bufsize band, and `q_global_reset` arms the
  metadata `"0"` separately.

### Author-level corrections found while encoding (new)

1. **The scout's `JackPortCanMonitor` round-trip row (0xA) is wrong.**
   `jack_port_flags` on the CanMonitor port returns **2** (IsOutput
   only) in every arm here *and in the boundary's own receipts*
   (`h_shape.json` / `q_shape.json` `lat_outm.flags == 2`, 3/3 each) —
   the flag is dropped in both directions (no PW prop, no round-trip).
   The armed value is 2; the scout's 0xA is not encoded.
2. **The fill-aliases alias addresses the port but does not rename it.**
   With `jack.fill-aliases=true`, `jack_port_by_name("<node.name>:playback_0")`
   resolves and `jack_connect` returns 0, yet the connection list (and
   the pw-dump link) reports the canonical rendered
   `<node.description>:playback_MONO` name.
3. **A live `jack_set_buffer_size` rewrites `node.force-quantum`**
   (`"2048"` → `"512"` after the live set), not just the effective size
   and the callback.
4. **`pw-dump` carries no metadata rows on this host** (`Metadata`
   objects have `info: null`), so every metadata witness goes through
   `pw-metadata -n <store>`; the parser tolerates the trailing
   `type:' type:' type:''` quirk some rows carry.
5. **`jack_get_all_properties` counted 2 own descriptions** (client +
   port) in every run — the count is armed, the global description count
   is only recorded (foreign writers can inflate it).

## Remaining risks / blockers

- None blocking. Honest exposures, recorded rather than hidden:
  - **Shared host daemon**: `clock.force-quantum` and the default
    node are host-global; the `q_*` legs assert the value this family
    wrote and the teardown re-verifies the restore, but a sibling seat
    writing the same key inside the arm window would surface as a real
    red with the value in the receipt. `settings_moved` ignores only the
    key this arm owns.
  - **The stall arm is a self-inflicted RT perturbation**: in one dev
    pass the client did not return inside the 25 s bound and was killed;
    that path is a named coverage block (xrun envelope unjudged), never a
    silent green.
  - **`b_pw2jack` links the player after it starts**, so only ~74 % of
    the 1.5 s tone reaches the input (53245 of 72000 samples, identical
    in both runs); the arm is a fraction band plus the exact-peak and
    energy-ratio laws, never an exact nonzero count.
  - **`b_jack2pw`'s capture window** is process-timing dependent (88064
    vs 102400 frames across the two runs): the frames/rms/sha are
    recorded, and the armed quantities are ratios to the tone the probe
    actually generated.
  - **gcc + libjack headers are a fixture dependency**: absent
    compiler/header/library is a named `coverage_blocked` entry, and the
    build record (compiler path, rc, stderr tail, binary sha256) is in
    every entry's receipt.
  - `valgrind` is absent on this host; the RT-priority claim rests on the
    in-fixture stack-poison control (0xAA/0xBB pattern returned verbatim)
    — the same control the boundary used.
  - The r95 scout's and boundary's `stream-properties` rows (4 + 9) are
    still in the operator's store; the r90 class stands (no CLI deletes
    them) and this seat added none.
- Labrat fold (frozen `probeParent`, exactly one read-only child): four
  source-mechanism hypotheses against the fetched 1.6.8 tree came back
  **CONFIRMED** — the two `jack_set_buffer_size` branches with the
  `nframes==1 → "0"` special-case on the metadata path only
  (`pipewire-jack.c:5380–5386`), the RT-priority accessor shape
  (`:7568`, `:7575–7580`; the `spa_thread_utils_get_rt_range` ENOTSUP
  path itself is not in the fetched corpus, so the *dynamic* poison
  control is the measurement), the xrun callback's driver-counter gate
  with the first-divergence guard (`:2070–2073`, `:2031–2035`), and the
  port-flag mapping with `JackPortCanMonitor` absent from the whole file
  (`:5622–5625`; flags > 0x1f go to `port.extra`, CanMonitor is inside
  the mask and gets nothing).

*Leaf seat — implemented, measured, and green on frozen bytes; not judged.*
