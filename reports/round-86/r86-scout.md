# R86 scout — the pw-cli / pw-dump / pw-metadata / pw-top / pw-jack control-plane lattice

Round 86 pre-measurement. Host `plazir27`, measured **2026-10-15 ~03:40–04:05
UTC−3** (06:40–07:05Z). Repo `~/Projects/shokunin/audio-shokunin` @ HEAD
`a2616f7`. Toolchain: PipeWire **1.6.8** (pw-cli/pw-dump/pw-metadata/pw-top/
pw-jack/pw-link/pw-record/pw-play all 1.6.8), WirePlumber **0.5.17** (implements
the `default`/`settings`/`sm-*` metadata stores), libpulse **17.0-98-gb096**
(pactl, protocol 35), **pipewire-jack 1:1.6.8-1** (system libjack *is*
PipeWire's; no jack2), Python **3.14.7** (numpy 2.5.3), Linux **7.2.3-arch1-3**.

**Seat: SCOUT (leaf). Zero tracked-file edits. Every write under
`corpus/live/r86-scout/` + this report** (`receipts/abcd.txt` rep-pass,
`snaps/dump_{1..5}.json`, `volprobe.sh`, `tone1k.wav`, `mon.wav`).
`corpus/fixtures` never read/imported/executed. Seat-owned objects tagged
`r86ctl_*` (`r86ctl_ns` null-sink, `r86ctl_src` remap-source); every
`pactl unload-module` was index-verified against `sink_name=`/`source_name=`
immediately before the call; nothing was unloaded by name. Session defaults and
metadata were flipped deliberately and **restored verbatim** (§5.6/§10).

**Contention.** Quiet graph for most of the window (10 nodes, 0 links at
entry). A foreign `r79lb_*` pw-record spawned at 03:59 recording from its own
null-sink — observed, never touched (§10). Prior-round overlap: pw-cli destroy /
link lifetimes were measured r80; pactl default-set side r84; neither was
re-measured.

---

## 0. Headline — the frontier cells

| # | frontier item | verdict | the single sharpest measured fact |
| --- | --- | --- | --- |
| 1 | `pw-cli ls`/`info` census + addressing | **PINNED + NAMESPACE SPLIT** | `pw-cli ls <N>` matches **`object.serial`**, `pw-cli info <N>` matches **`object.id`** — `ls 46`→Client(serial 46), `info 63`→Port(id 63). Unknown/lowercase classes → **empty rc=0**, indistinguishable from a real empty class |
| 2 | `enum-params` exposure matrix | **TYPED PER OBJECT CLASS** | Node={Props,PropInfo,EnumFormat} only; Port={EnumFormat,Latency,IO,Meta} only; Device={Profile,EnumProfile,Route,EnumRoute} only; Client/Factory/Link → `not implemented on object`; everything else → remote `res:-2 ENOENT`; **`Format` is absent pre-negotiation and its EIO error text is racy** |
| 3 | `set-param` write reach | **LIVE-DSP + SPLIT AUTHORITY** | `Props { channelVolumes: [0.25,0.25] }` on a null-sink → monitor peak 8000→**2000 (linear!)** where `pactl … 25%`→**125 (cubic)**; `mute:true`→0; but `{ volume: 0.25 }` lands in the param store and moves **nothing** — display-dead key. Port/Latency writes accepted-rc0 and **silently dropped** |
| 4 | rc discipline | **NEW CLASS LAW** | every pw-cli/pw-metadata/pw-dump refusal measured returns **rc=0** — local `Error:` texts, remote `res:-2/-5` lines, and `None` parse-echoes are the *only* verdicts; rc is never one |
| 5 | `pw-dump` determinism | **BYTE-STABLE MODULO SELF** | 5 snaps ×0.5 s, 82 objects: identical except the dump's **own Client row** (`application.name:"pw-dump"` — volatile props `application.process.id`, `core.name`, `object.serial`, `pipewire.sec.pid`); order = registry order (not id-sorted), stable across reps |
| 6 | `pw-metadata` semantics | **STORE LAWS + AUTHORITY SPLIT** | writes echo `set property:` but persist **only for live subject ids** (subject 99998 echoed, never read back; subject 133 persisted); `-d` removes a key without touching the session default (WP re-persists lazily); **`default.audio.sink` AND `.source` writes are both authoritative AND functional** when the name resolves — a `.monitor` name silently ignores |
| 7 | `pw-top` headless | **ARMED + CRASH CLASS** | `pw-top -b -n N` → rc=0, clean plain-text table, **no tty needed**; TUI mode also works piped (curses escapes) but SIGTERM/SIGINT → **SIGABRT rc=134** `loop.c:189 remove_from_poll` assertion + core (3/3); only SIGKILL (137) exits clean |
| 8 | `pw-jack` / JACK bridge | **NAMED COVERAGE GAP + ENV LAW** | `pw-jack` is a POSIX script that only exports `PIPEWIRE_REMOTE/-DEBUG/-QUANTUM` then `exec`s — its `LD_LIBRARY_PATH` line is **commented out** (unneeded: `/usr/lib/libjack.so.0.3.1608` IS pipewire's). **No jackd, no jack_lsp, no jack_* tools at all** — the bridge is library-only |

---

## 1. `pw-cli ls`/`info` census lattice (`receipts/abcd.txt` §A/B, ×3)

### 1.1 Class census (quiet graph at entry; my objects add Node+3/Port+10/Link+2/Client+2)

| class | rows | | class | rows |
| --- | --- | --- | --- | --- |
| Core | 1 | | Factory | 13 |
| Device | 3 | | Metadata | 9 |
| Node | 10 | | Profiler | 1 |
| Port | 24 | | Module | 13 |
| Client | 6 | | Link | 0 (idle) |
| Session / Endpoint / EndpointStream / ClientNode / ClientEndpoint | 0 | | **Bogus / `node` (lowercase)** | **0 — same shape** |

- **`ls` prints nothing for unknown class names and exits rc=0** — `ls Bogus`
  ≡ `ls Session` ≡ `ls node`. An arm cannot distinguish "class absent" from
  "zero objects"; the class name is case-sensitive (`Node` works, `node` empty).
- **Addressing split**: `pw-cli ls <N>` selects by **`object.serial`**
  (`ls 46` → Client id45 serial46; `ls 63` → serial-63 object; `ls 99999` →
  empty). `pw-cli info <N>` selects by **`object.id`** (`info 63` → Port id63,
  *not* the serial-63 SPDIF node). pactl also uses serial (r85) → the serial
  family is {pactl, `pw-cli ls`}, the id family is {`info`, `enum-params`,
  `set-param`, `destroy`}. 3/3.
- Output shapes differ: `ls` prints `type PipeWire:Interface:X/Y` (space),
  `info` prints `type: PipeWire:Interface:X/Y` (colon) plus port/state info —
  grep patterns are not interchangeable.
- `pw-cli info <link-id>` is the **live-format census arm**: prints
  `output-node-id/-port-id`, `input-node-id/-port-id`, `state`, and the
  **negotiated `Format` pod** — the only surface measured that shows a link's
  format directly.
- `pw-cli info all` dumps every object in the same schema; `info bogus` /
  `info 99999` → `Error: "info: unknown global 'X'"` stderr, rc=0.
- REPL note: bare `pw-cli </dev/null` prints the `Welcome to PipeWire…` banner
  + `>> ` prompt + `Error: "unsupported type PipeWire:Interface:SecurityContext"`
  (WP's SecurityContext global has no pw-cli proxy) then exits rc=0 on EOF;
  one-shot commands do not emit it.

## 2. `enum-params` matrix (`receipts/abcd.txt` §C, ×3 + flake reps ×6)

Param ids accept **names or numbers** (`enum-params 133 3` ≡ `EnumFormat`;
`999` → `unknown param type: 999`; `all` → `unknown param type: all`). Verbatim
outcomes on this host:

| param | Node 133 (null-sink) | Port 104 (its playback_FL) | Device 48 (USB card) |
| --- | --- | --- | --- |
| Props | **dumps pod** | ENOENT | ENOENT |
| PropInfo | **dumps** | ENOENT | ENOENT |
| EnumFormat | **dumps** | **dumps** | ENOENT |
| Format | **EMPTY** (EIO text racy) | **EMPTY** (EIO text racy) | ENOENT |
| Latency | EMPTY | **dumps** | ENOENT |
| ProcessLatency | EMPTY | ENOENT | ENOENT |
| IO | ENOENT | **dumps** | ENOENT |
| Meta | ENOENT | **dumps** | ENOENT |
| Profile / EnumProfile / Route / EnumRoute | ENOENT | ENOENT | **dump** |

Object classes: Client/Factory/Link → `Error: "enum-params not implemented on
object <id> type:PipeWire:Interface:<T>"` (local refusal).

Refusal/error classes (all **rc=0**, text on **stderr**):

| class | signature | meaning |
| --- | --- | --- |
| `ep_local_unknown_type` | `Error: "enum-params: unknown param type: X"` | name not in the param-id enum (incl. bogus numerics) |
| `ep_local_not_impl` | `Error: "enum-params not implemented on object N type:…"` | object type has no param interface (Client/Factory/Link/Module) |
| `ep_remote_enoent` | `remote 0: error id:N seq:S res:-2 (No such file or directory): enum params id:K (…) failed` | **deterministic** — param exists in the enum but this object doesn't expose it |
| `ep_remote_eio_racy` | `remote 0: error … res:-5 (Input/output error) … id:4 (Format) failed` | **RACY** — same leg prints EIO or nothing (~1/12 error-text rate); the *absence of Format objects* is what's stable |
| `ep_silent_empty` | zero output lines, no error | param exposed with no current objects (Node Latency/ProcessLatency; Node+Port Format pre-negotiation) |
| `ep_unknown_global` | `Error: "enum-params … unknown global 'N'"` | bad object id |
| `ep_usage` | `Error: "enum-params <object-id> <param-id>"` | missing args |

**Arm rule: judge enum-params on pod output presence/absence; never on remote
error text — `seq:S` numbers churn per connection and the Format EIO emits
nondeterministically.**

## 3. `set-param` write surface (`receipts/abcd.txt` §D + `volprobe.sh` runs)

### 3.1 The functional law — Props param is live DSP with a LINEAR scale

Instrument: `pw-play tone1k.wav → r86ctl_ns`, monitor tap via
`pw-record -P stream.capture.sink=true --target r86ctl_ns`, write at t≈2.0 s,
0.25 s windows. Baseline peak 8000.

| write at t=2.0 | peak after (windows) | law |
| --- | --- | --- |
| `{ channelVolumes: [0.25,0.25] }` ×3 | **2000** | linear 0.25× — **live** |
| `{ channelVolumes: [0.5,0.5] }` ×3 | **4000** | linear 0.5× |
| `{ mute: true }` ×2 | **0** | live |
| `{ volume: 0.25 }` ×3 | **8000 unchanged** | **display-dead key** — lands in the param store (`enum-params` reads Float 0.25 back) but moves no audio and pactl still shows 100% |
| `pactl set-sink-volume … 25%` (contrast) | **125** | cubic 0.25³ (r84 law) |

**Same numeric "0.25", three outcomes**: Props.channelVolumes→2000 (linear),
pactl→125 (cubic), Props.volume→8000 (dead). After `channelVolumes=0.5`,
`pactl get-sink-volume` reads **79%** (=∛0.5) — the param store and the pulse
volume are the *same* underlying state seen through different scales; only the
scalar `volume` key is decoupled.

### 3.2 Write-refusal lattice (all rc=0; `Error:` on stderr, pod echoes on stdout)

| arm | verbatim result | verdict |
| --- | --- | --- |
| `set-param 133 Props 'garbage'` | prints `None` | malformed spa-json → parse echo, **silent** |
| `… Props '{ }'` | `Object: size 8 … Props` empty pod | accepted no-op |
| `… Props '{ zzz.r86: 7 }'` | `Object: size 8` empty pod; key absent on re-enum | **unknown keys stripped, not stored** |
| `… Props '{ volume: "high" }'` | pod echo shows `volume` → `None` | wrong-type value → None-typed slot |
| `… EnumFormat '{ mediaType: 1, … }'` | rc=0 pod echo; re-enum unchanged | **write-to-readonly accepted, no effect** |
| `… Format '{ mediaType: 1, … }'` | same | same |
| `set-param 104 Latency '{ minQuantum: 2.0 }'` | rc=0 echo; re-enum minQuantum still `Float 0.000000` | **port writes accepted, dropped** (ports are read-mostly) |
| `… Bogus '{ }'` | `Error: "set-param: unknown param type: Bogus"` | local refusal |
| `set-param 99999 Props '{ }'` | `Error: "set-param: unknown global '99999'"` | bad id |
| `set-param 133 Props` (no json) | `Error: "set-param <object-id> <param-id> <param-json>"` | usage |

Deliberately **not armed**: `set-param <device> Profile|Route` — a successful
write reconfigures real hardware routing; enumerations above were read-only.
`send-command`/`permissions` probed to usage text only.

## 4. `pw-dump` surface (`snaps/dump_{1..5}.json`, `mon.txt`)

- **Determinism**: 5 snapshots 0.5 s apart on the quiet graph — 82 objects,
  byte-identical except ONE row: the invocation's **own Client** object
  (`application.name="pw-dump"`). Volatile props inside it:
  `application.process.id`, `core.name` (`pipewire-vgpnk-<pid>`),
  `object.serial`, `pipewire.sec.pid`. **Canonical arm: drop the object whose
  `info.props["application.name"]=="pw-dump"`, then byte-diff.** 5/5.
- Ordering = registry insertion order (first ids `[0,1,3,2,5,4,…]` — **not**
  id-sorted) but stable across reps; id list identical 5/5.
- `pw-dump <id>` → single-object array; `pw-dump 99999` / `bogus` → **zero
  bytes of output**, rc=0 (not even `[]`).
- `pw-dump -m` → full array then streamed update objects, **unbounded**
  (8 776 lines in 1.5 s capture incl. metadata `update:` rows); must be
  timeout-killed.
- `pw-dump -s` → SPA-syntax output (`id = 133`, `type = "…"`) — a second
  wire format, not JSON.
- Each pw-dump is itself a graph event: it adds one Client + bumps serials —
  serial counters are *monotonic, never recycled* (r85 law re-confirmed:
  self-serials 40399/40400 on consecutive runs).

## 5. `pw-metadata` lattice

### 5.1 Inventory

`pw-metadata -l` → 9 stores on this host: `settings`(31), `schema-sm-settings`
(37), `persistent-sm-settings`(38), `sm-settings`(39), `sm-objects`(40),
`default-profile`(41), `default`(42), `filters`(43), `route-settings`(44).
`-n <bogus>` → **no `Found` line at all**, empty, rc=0 — the Found line is the
existence check. `pw-metadata` bare ≡ `-n default`.

### 5.2 Write/read/overwrite/delete semantics (seat keys, ≥3 cycles)

| arm | result |
| --- | --- |
| `pw-metadata -n default 0 K 'V'` | echoes `set property: id:0 key:K value:V type:(null)` on stdout |
| read `… 0 K` | `update: id:0 key:'K' value:'V' type:'(null)'`; absent key → **no update row** (silent) |
| overwrite `K 'V2'` | full replace (no merge) |
| `… 0 K 'V' 'Spa:String'` | type persists verbatim (`type:'Spa:String'` vs `(null)` default) |
| `-d 0 K` | `delete property:` → key gone |
| `-d 0 <absent>` | **same echo, silent no-op** — deleting absent is not a refusal |
| `-d <subject>` (no key) | `delete properties: id:N` — wipes **all keys under that subject** (verified on seat subject; `id:0` untouched). **Never `-d 0` bare** — that is the session-default store |
| write under nonexistent subject `99998` | echoes `set property:` but **never reads back** — WirePlumber's `default` store drops writes whose subject isn't a live object (2/2) |
| write under live subject `133` (my node) | persists, reads back — the echo is a *local print*, not a server ack; **verify by read** |
| `-m` | prints current rows then streams live `update:`s (unbounded) |

### 5.3 Authority split — `default.audio.*` is writable AND functional

| arm | pactl witness | functional witness |
| --- | --- | --- |
| `default.audio.sink = {"name":"r86ctl_ns"}` | `get-default-sink` → **r86ctl_ns** | untargeted `pw-play` **linked `→ node 133`** — live re-route |
| restore to SPDIF | SPDIF again | — |
| `default.audio.source = {"name":"r86ctl_src"}` | `get-default-source` → **r86ctl_src** | untargeted `pw-record` linked `81→stream` |
| `default.audio.source = {"name":"r86ctl_ns.monitor"}` | **unchanged** (Line) | — **`.monitor` is a pulse alias, not a pw node name → silently ignored** |
| `default.configured.audio.source` write | stored; default follows `default.audio.source` | — |

- **Baseline asymmetry**: `default.audio.sink` was persisted at rest;
  `default.audio.source` was **absent** until something set it. After my
  restore+`-d`, the key is absent again and the store matches baseline shape.
- **`-d` does not reset a default**: deleting `default.audio.source` while the
  session default still pointed at my source left `pactl get-default-source`
  = r86ctl_src, and WirePlumber **re-persisted the key** on the next
  default-change event. Delete only works on keys whose value isn't live state.
- Both writes needed a **resolvable pw node name** — value is `{"name":<pw
  node.name>}`; pactl-side `@DEFAULT_*@` aliases and `.monitor` names don't
  resolve here.

## 6. `pw-top` headless (`/tmp/pwtop-*.err`, cores in coredumpctl)

| arm | result |
| --- | --- |
| `pw-top -b -n 2` (pipe, no tty) | **rc=0, clean** — plain `S ID QUANT RATE WAIT BUSY W/Q B/Q ERR FORMAT NAME` table; row prefixes C/S/I/R; runs `-n` iterations then exits normally |
| `pw-top` piped (TUI mode) | emits full curses escapes to the pipe, live table incl. `r86ctl_*` nodes with WAIT/BUSY µs; **runs until killed** |
| `kill -TERM` / `-INT` | **SIGABRT rc=134**, stderr `'source->loop == &impl->loop' failed at ../pipewire/spa/plugins/support/loop.c:189 remove_from_poll()` — **core dumped, 3/3** (incl. `timeout 3` kill) |
| `kill -KILL` | rc=137, silent, clean |

Arm: always `pw-top -b -n N` for headless; if the TUI stream is wanted, kill
with SIGKILL — a `timeout`-only harness reads the rc=134 assertion as a crash
(because it is one).

## 7. `pw-jack` / JACK bridge presence

- `/usr/bin/pw-jack` is a **POSIX shell script**: parses `-r` (→
  `PIPEWIRE_REMOTE`), `-v` (increments `PIPEWIRE_DEBUG`), `-s`/`-p` (→
  `PIPEWIRE_QUANTUM="<period>/<rate>"`, default rate 48000), then `exec "$@"`.
  The `LD_LIBRARY_PATH=/usr/lib/pipewire-0.3/jack` line is **commented out** —
  `pipewire-jack 1:1.6.8-1` installs `libjack.so.0.3.1608` into `/usr/lib`
  directly (`ldd` → `libpipewire-0.3.so.0`); **jack2 is not installed**.
- Arms: `pw-jack -s 44100 -p 256 sh -c 'echo $PIPEWIRE_QUANTUM'` → `256/44100`;
  `-p 512` alone → `512/48000`; `pw-jack true` rc=0; `pw-jack <bogus>` →
  `exec: …: not found` **rc=127**.
- **Coverage gap (named)**: zero `jack_*` tools on PATH — no `jackd`,
  `jack_lsp`, `jack_connect`, `jack_alias`, `jack_control`. The JACK surface
  on this host is **library-only**: any client that links `libjack.so.0` gets
  PipeWire's implementation (r78's `ffmpeg -f jack` arm already rode it).

## 8. Refusal taxonomy (verbatim, all rc=0 unless noted)

| class | signature | where |
| --- | --- | --- |
| `pwcli_rc0_lies` | every refusal below exits 0 | all pw-cli verbs |
| `local_error` | `Error: "<verb>: …"` / `Error: "<verb> <usage>"` on stderr | bad param name, bad global, missing arg, `connect`→`failed to connect: Host is down`, `info/enum-params/set-param` unknown global |
| `remote_error` | `remote 0: error id:N seq:S res:-2/-5 (…): … failed` on stderr | ENOENT param absence (deterministic), EIO Format (racy), bind-race `no global N` |
| `not_impl` | `Error: "enum-params not implemented on object N type:…"` | param verbs on Client/Factory/Link/Module |
| `silent_empty` | zero output | `ls <unknown-class>`, `ls <dead-serial>`, `enum-params` silent-empty params, `pw-dump <bad-id>`, `pw-metadata -n <bogus>` / absent key read |
| `pod_echo` | spa pod dump on stdout | successful `set-param`, successful `enum-params` |
| `set_echo_lies` | `set property: …` printed, nothing persisted | pw-metadata write under dead subject id |
| `pwtop_sigabrt` | rc=134 `loop.c:189` assertion + core | TERM/INT on pw-top |
| `pwlink_eexist` | `failed to link ports: File exists` | duplicate `pw-link` (rc=0) |
| `pwjack_exec127` | `exec: <cmd>: not found`, rc=127 | bad pw-jack payload |

## 9. Falsification list — claims an arm must not make

1. "pw-cli failures exit nonzero" — every measured refusal is rc=0; verdicts
   live in stderr text or output absence.
2. "`set-param` writes never reach the node" — `channelVolumes`/`mute` are live
   DSP on a null-sink (8000→2000/0); only `volume` is a dead key and port
   params accept-then-drop.
3. "sink volume percent is linear" — pactl `%` is cubic (125 @25%),
   `channelVolumes` is linear (2000 @0.25); never equate them.
4. "`ls` and `info` take the same id" — `ls` = object.serial, `info` =
   object.id; `ls 46`/`info 63` hit different objects.
5. "`enum-params Format` erroring means the object lacks formats" — Format is
   just absent pre-negotiation; its EIO text is racy and unarmable.
6. "`set property:` echo = persisted" — echo is local; dead subject ids drop
   silently. Read back.
7. "deleting `default.audio.*` resets the default" — it removes the key only;
   the live default stays and WP re-persists it lazily.
8. "two `pw-dump`s differ" — only if the self-Client row isn't canonicalized
   out.
9. "`pw-top` needs a tty" — works piped; but `-b -n` is the only clean-exit
   shape (graceful signals SIGABRT).
10. "`pw-jack` shims `LD_LIBRARY_PATH`" — commented out on this build; the
    system libjack *is* PipeWire's; no `jack_*` tools exist.
11. "`.monitor` names resolve in pw-metadata" — pulse aliases only;
    `default.audio.source={"name":"X.monitor"}` is silently ignored.

## 10. Ledger + exit state

- Seat objects: `r86ctl_ns` (module 536870922) + `r86ctl_src` (module
  536870918), both unloaded by index verified against `sink_name=`/
  `source_name=` in the same listing; 0 `r86ctl_*` nodes/modules/metadata-keys
  at exit; `pactl` defaults restored (`…SPDIF__sink` / `…Line__source`);
  `default.audio.source` key deleted (baseline-absent) after restoring the
  Line default.
- Foreign contact: one `r79lb_*` pw-record appeared at 03:59 on its own
  null-sink — observed, untouched, still running at exit. No foreign module was
  ever unloaded; only seat objects were destroyed.
- Self-inflicted + repaired: an orphaned `pw-record --target ''` (my probe,
  `/dev/null` output, empty-target → binds current default — noted as an arm
  edge) was killed by pid; a stale pactl 25% left on `r86ctl_ns` between arms
  was reset before functional reps.
- Traps for the battery author: `pw-play -q` is `--quality` and *eats the
  filename* (no-file usage error); `pw-record`'s `-q` is also quality —
  silence flags are not `pw-play`'s; `pw-cli` REPL banner/`>>` goes to stdout
  on interactive paths only; remote `seq:` counters and the SecurityContext
  bind-error are per-connection noise.

Scratch: `corpus/live/r86-scout/` (~1.2 MB: 5 dumps + rep receipts + probe +
tone). Report written 2026-10-15T07:0xZ.
