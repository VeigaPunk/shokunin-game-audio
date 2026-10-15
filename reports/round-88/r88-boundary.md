# R88 boundary — falsification of the r88 scout claims, under load

**Seat: BOUNDARY (falsification).** Lane `~/Projects/shokunin/audio-shokunin`.
Host `plazir27`, measured **2026-10-15 20:07:44Z–20:13Z** (17:07–17:13 local −03),
at HEAD **`1abd9549`** (r85 boundary) — note the scout measured at `a2616f7`, so both
the host **and the repo** have moved since the scout window (03:47–03:53 local).
Toolchain unchanged: PipeWire 1.6.8, WirePlumber 0.5.17-1, libpulse 17.0
(pactl 17.0-98-gb096), bluez 5.87-2, Python 3.14.7.

**Zero tracked-file writes, no commits.** Everything this seat wrote is under
`corpus/live/r88-boundary/` (11 MB, 499 files) plus this report. All audio objects
this seat created are `r88b_*` and all are gone; all burners/streams this seat
started were killed by pid (16/16 `r88b_hog`, `r88b_stream`, 3 `r88b_*` null sinks
unloaded). Exit check: `pw-dump | grep -c r88b_` = **0**, `pactl list modules | grep -c r88b_` = **0**,
processes matching `r88b` = **0**.

**The host rebooted between the scout window and this one** (boot 13:38 local, uptime
3:35 at exit; scout's session had bluetoothd pid 1365 / wireplumber 2883626, now 1384 / 2063).
That is the single largest host-state variation in this report, and it is what makes the
replays below non-trivial: the graph, the module set and the pivot objects are all new,
while the scout's laws had to be re-earned on a new object population.

**Approx. 692 process runs** across 7 batteries; per-leg argv/rc/sha256/timestamps in
`receipts/B*.json`, every stdout/stderr in `raw/`, consolidated verdicts in
`receipts/summary.json` (22 verdicts). Re-run: `python3 scripts/r88b_probe.py <battery>`
then `python3 scripts/r88b_analysis.py`.

**Labrat probe (frozen probeParent duty): dispatched exactly one** (`ufo-labrat`, agent
`6fbd506f`, bounded depth-2, read-only, hypothesis = pw-cli witness keying). It returned
**UNRESOLVED — not measured**: its substrate exposed filesystem read/search tools only and
no execution interface, so it ran zero commands and mutated nothing. Its P1–P5 legs were
therefore absorbed into this seat's own battery (B3/B8) — recorded here as *no independent
corroboration obtained*, not as a measurement.

---

## 0. Headline verdict table

| # | scout claim | verdict | sharpest measured fact |
| --- | --- | --- | --- |
| V6 | "`bluez5.codecs` is **not a string** in `libspa-bluez5.so` (measured absence)" | **FALSIFIED** | `strings -a` gives **2 hits** on the same byte-identical file (sha256 `a2e8537a…`): `spa.bluez5.codecs` and **`property bluez5.codecs '%s' is not an array`** — the error string proves 1.6.8 *parses* the property. Only the *standalone* line form is absent (`grep -xc` = 0), which is the likely origin of the error |
| V7 | "15 files in `/usr/lib/spa-0.2/bluez5/`" | **FALSIFIED (off-by-one)** | `ls -1` = **14**; the scout's own `raw/spa-bluez5-inventory.1.txt` lists 14 entries, and the same sentence names 1 + 13 = 14 |
| V8 | "56/62 legs byte-identical across fresh ×3" | **FALSIFIED (arithmetic)** | recomputed from the scout's own receipts: **58/64** legs stable; their 6-leg unstable list is exactly right |
| V18 | §2 `pactl set-card-profile bluez_card.… a2dp-sink` → 1,1,1 | **PROVENANCE GAP** | that probe has **no receipt anywhere** in `corpus/live/r88-scout/`; re-run here 3/3 rc 1 (receipts now exist) |
| V3 | the rc-1 text identifies a missing object | **WEAKENED (confound)** | a *bogus profile on an existing card* returns the **same** `Failure: No such entity` rc 1 — the text cannot separate "no such card" from "no such profile"; the card's absence rests on the independent `pactl list cards` witness |
| V10 | "the serial collision is not exotic: 3 of 7 live keys" bundle | **NOT REPRODUCIBLE (mechanism found)** | **0 bundles in 150 keys**; bundle requires a live id to equal another object's serial, and max live id **258** < min shifted serial **47326** — the ranges are disjoint by construction, so bundles are a *fresh-instance* phenomenon |
| V16 | "expect the pulse vocabulary to disagree with the native vocabulary on the same object" | **NOT REPRODUCIBLE as a rule** | 24/24 agreement over 6 sinks × 3 tight reps; controlled A/B on my own null sink: idle = `SUSPENDED`/`suspended`/`S` and active = `RUNNING`/`running`/`R`, 3/3 each |
| V17 | §4.5 pulse-only sink while its native node was gone | **NOT REPRODUCED** | **0 pulse-only events in 70 tight brackets**, including 15 while my own `r88b_ns` existed in both witnesses and 40 after unloading it (sensitivity verified) |
| V1 | no bluez audio device; the paired DualSense is HID-only | SURVIVES (re-measured post-reboot) | same device record, same UUID set, `Connected=false`; `pactl list cards` = 3 ALSA cards; `pactl list \| rg -i 'bluez\|a2dp\|sco'` = 1 line (that line's *ordering* is boot-local) |
| V2 | module-bluez5 does not exist on this host | SURVIVES + control | 6/6 load-module refusals rc 1; `find /usr/lib*` = 0; SPA lib owned by `pipewire-audio`; **control**: `load-module module-null-sink` rc 0 → the command class works, the bluez5 name has no target |
| V4 | stack alive: 21 A2DP endpoints, zero devices | SURVIVES across reboot | verbatim journalctl argv now returns **42 registrations = 2 boots × 21**, single sender each (:1.75450 old, :1.47 = wireplumber pid 2063 now); **unique path sets identical** to the scout's 21; `bluez_midi.server` live (id 49) |
| V5 | codec switch unmeasurable (device-absence, not stack-absence) | SURVIVES + new witness | `create-node` with `api.bluez5.a2dp-sink` / `.sink` / `.source` / `.midi.node` all refused (res −2 / −22), nothing created; 14 SPA bluez5 codec files present |
| V9 | `pw-dump <N>` = `{id==N} ∪ {serial==N}` | SURVIVES exactly, mode-invariant | **133/133 stable keys match**; 40/40 nested-reference checks show ports are *not* returned by their `node.id`; membership identical under `-s`/`-R`/`-i 0` |
| V11 | `pw-cli info` is a singleton keyed by native id | SURVIVES, extended | **40/40 serial-only keys** → rc 0 + `unknown global`; 0 id-keys misreported; new silent classes (below) |
| V12 | prop keys agree, types/params/state differ | SURVIVES, extended to Device + Client | device 44: **40/40 keys equal**; client 32: **41/41**; bools become quoted strings (`api.acp.auto-port` `false` → `"false"`) |
| V13 | `pw-top -n 1` is a trap (all rows `C`) | SURVIVES under load | 12/12 busy-window **plus 6/6 under +16 own burners**; 25/25 including the scout's 7 |
| V14 | cadence 3–21 ms busy vs 1002 ms idle; mechanism unresolved | REPRODUCED + **MECHANISM RESOLVED** | the second frame carries the driver row **QUANT 1024 / RATE 48000 = 21.3 ms**; measured per-frame walls cluster on that cycle (n2 6.8–25.5 ms, n3 40–44 ms, n4 40–49 ms) while the graph runs, 1010 ms idle; unchanged under CPU hog |
| V15 | pactl index is the native **serial**, not the id | SURVIVES, strengthened | **14/14 sinks, 16/16 sources, 5/5 sink-inputs**; 11 witnesses have serial ≠ id and every one follows the serial (e.g. `r96s_ns`: idx 116459, id 110, serial 116459) |
| V19 | — (new) | NEW FINDING | `pw-cli ls Metadata` = **9** ids vs `pw-dump` = **4**, extra `[35,37,38,41,42]`, **4/4 tight brackets, both sockets**; `pw-dump 35` and `pw-cli info 35` both rc 0 with empty stdout while `ls` prints the object |
| V20 | — (new) | NEW FINDING | `pw-cli info all` describes **135** of 141 objects — silently omits `[3,5,31,34,36,39]` (SecurityContext, Profiler, all visible Metadata) |
| V21 | — (new) | NEW HAZARDS | rc-0 failures: `pw-dump <non-numeric\|overflow>` silent-empty; `pw-dump ''` = **full dump**; `pw-dump <id1> <id2>` returns **only id1**; `--color=always` breaks JSON; `pw-cli create-node` failure = **rc 0**; `pw-top -n -1` / `-n abc` = **infinite**; `pw-dump -1` / `pw-top -r bogus` = rc 255 |
| V22 | — (new) | NEW HAZARD | `pw-cli info` prop-block layout is **class-dependent**: nodes/ports print flat `key = value`, Device/Client print `* properties:` + `*\t\tkey = value` — a node-tuned parser silently yields **0 props** there (this analysis hit it) |

---

## 1. The falsifications, with exact evidence

### 1.1 `bluez5.codecs` — a headline "measured absence" that is wrong

The scout's §0 row 4, §3 and §6 all assert absence, and §6 turns it into guidance
("do not cite `bluez5.codecs` as live"). Measured now, on the **same file the scout
inventoried** (size 965416, mtime Jul 10 03:31 — identical to their raw line):

```
$ sha256sum /usr/lib/spa-0.2/bluez5/libspa-bluez5.so
a2e8537a1577d7998b2f1ed778010955d5c6622c779acac2ad6f5cd40469dd06
$ strings -a … | grep -n 'bluez5\.codecs'
2152:spa.bluez5.codecs
4267:property bluez5.codecs '%s' is not an array
$ strings -a … | grep -xc 'bluez5\.codecs'      # standalone line form
0
```

So the *substring* is present twice, and line 4267 is an error message that names the
property and complains it is not an array — i.e. the library has code that reads and
type-checks `bluez5.codecs`. The report's "measured absence" is false as written; the
only true form is "no standalone string". A neighbouring string inventory gives **116
distinct `bluez5.*` names**, and every prop the scout *did* list is present
(`enable-sbc-xq`, `enable-msbc`, `enable-faststream`, `enable-a2dp-duplex`,
`enable-hw-volume`, `enable-lc3-a127`, `roles`, `headset-roles`, `media-source-role`,
`hfphsp-backend`, `auto-connect`, `autoswitch-routes`, `hw-offload-datapath`,
5 × `bluez5.telephony.*`, 26 × `bluez5.bap*`). Their §3 *prop list* is right; the
*absence* claim and its guidance are not. (What remains unmeasured — whether the
property is honoured per-device at runtime — is exactly what the scout's own hedge says,
and it stays unmeasured; V5.)

### 1.2 "15 files" is 14

`ls -1 /usr/lib/spa-0.2/bluez5/ | wc -l` = 14 (1 `libspa-bluez5.so` + 13 codec
plugins), and the scout's own receipt `raw/spa-bluez5-inventory.1.txt` contains exactly
14 entries plus `.`/`..`/`total`. The same sentence in the report names 1 + 13 = 14.
Off-by-one, self-contradicted by their raw.

### 1.3 Stability numbers

Recomputed from `r88-scout/receipts/r88-legs.json` (49 legs) + `r88-addendum.json`
(15 legs): **64 legs, 58 `stable_stdout`**, unstable = `pactl-list`, `pactl-info`,
`wpctl-status`, `pw-dump-census`, `add-pwtop-n2`, `add-pwtop-n3` — the *set* the report
names is exactly right, the counts "56/62" are not.

### 1.4 The one probe with no receipt, and what it really shows

`pactl set-card-profile bluez_card.BC_C7_46_34_C5_66 a2dp-sink` is presented in §2 as a
×3 fresh-process measurement; `grep -rl set-card-profile corpus/live/r88-scout/` finds
**nothing**. Re-run here (receipts B1): 3/3 rc 1 `Failure: No such entity`. But the
controls make the inference weaker than the report's: on an existing ALSA card,
`set-card-profile <card> output:hdmi-stereo` (its own current profile) is **rc 0**, and
`set-card-profile <card> bogus-profile-xyz` is **rc 1 with the identical
`Failure: No such entity`**. The refusal text is therefore *not* diagnostic of a missing
object — the scout's "the module/recipient/card does not exist" reading needs the
independent witness (`pactl list cards` shows no bluez card), which they do have.
Their *conclusion* stands; their *evidence path* for this row does not.

---

## 2. Verbatim replays under load (18 legs compared against scout receipts)

Every refusal class replicates with **identical rc values and byte-identical stderr
text** (`replay_rc_value_mismatches: []`, `replay_stderr_mismatches: []`):

| leg | scout | mine | stderr |
| --- | --- | --- | --- |
| `load-module module-bluez5-{discover,device,device path=…}` | 1,1,1 | 1,1,1 | `Failure: No such entity` |
| `load-module module-bluez5-discover a2dp_source=false` | 1 | 1 | `Failure: No such entity` |
| `send-message /org/bluez/hci0 …` | 1,1,1 | 1,1,1 | `Send message failed: No such entity` |
| `set-card-profile bluez_card.… a2dp-sink` (no scout receipt) | 1,1,1 | 1,1,1 | `Failure: No such entity` |
| `pw-cli info 99999` | 0,0,0 | 0,0,0 | `Error: "info: unknown global '99999'"` |
| `pw-cli enum-params 99999 Format` | 0,0,0 | 0,0,0 | `Error: "enum-params: unknown global '99999'"` |
| `pw-dump 99999` | 0,0,0 | 0,0,0 | *(silent)* |

**Under my own hog (+16 `r88b_hog` burners, 8 s soak) the refusal legs are
byte-identical to their non-hog runs** (`stderr_sha256` equal for all three compared
legs) and `pw-dump`-spot set-rule checks are 14/14 — load does not touch this class.

Two host-variation results on the same argv:

- `pactl list | rg -i 'bluez|a2dp|sco'` still returns **exactly 1 line**, but that line
  is the `session.services` string and its **member order differs** from the scout's
  quoted capture (now `[bluetooth.audio, api.alsa, …]` vs `[video-capture,
  policy.linking.standard, …]`). The count is durable; the quoted string is boot-local.
- The scout's journalctl argv (`--since 2026-10-15 02:08:27`) now spans **two boots**:
  42 `Endpoint registered` (21 from `:1.75450`, the old wireplumber, + 21 from `:1.47`,
  the current one) and 21 `Endpoint unregistered` (from `:1.75426`, the sender *before*
  the scout's). **The unique 21-path set is identical between the scout's boot and this
  one** — the A2DP endpoint surface is a build/config constant here, not a boot accident.

---

## 3. The set-rule law, re-earned on a new object population (V9/V10)

Sweep: census → `pw-dump <K>` for **every** K in ids ∪ serials → census again; a key is
"stable" only if its predicted member set is identical in both censuses.

- **133/133 stable keys match exactly** (predicted = `{id==K} ∪ {serial==K}`, live
  objects only).
- The 17 non-matches are all the same shape: keys that were the **serial of an object
  that died mid-sweep** (my own short-lived `pw-dump` clients) → `pw-dump <K>` returns
  **rc 0, empty stdout, empty stderr**. New instance of the silent-absence class.
- **Nested references do not expand: 40/40.** For 40 ports, `pw-dump <node.id>` never
  returned the port — the scout tested 8 keys but never this case.
- **Mode-invariance:** membership is identical under `-s` (SPA), `-R` (raw) and `-i 0`;
  SPA output shows both `id = 131` and `object.serial = 47326` for a serial-only key.
- **0 bundles**, and the mechanism: a bundle needs a *live id* to equal *some other
  object's serial*. Here ids are ≤ 258 (slot reuse) while every non-aligned serial is
  ≥ 47326 (the counter races ahead with each client connection — 692 of them from this
  seat alone). Disjoint ranges ⇒ bundles are impossible in this session and were a
  property of the scout's freshly-started PipeWire instance. **A consumer's correct
  defence is unchanged (select `.id == N` from a full dump), but the "3 of 7" frequency
  claim must not be carried forward as typical.**
- Where the serial actually lives matters for implementations: it is
  `info.props["object.serial"]` — there is **no top-level `.serial`** and no top-level
  `.object.serial` field, so `jq '.[]|select(.serial==N)'` and
  `select(.object.serial==N)` both find nothing.

## 4. Witness modes the scout never used (all new findings)

`pw-cli ls <iface>` — never exercised by the scout — agrees with `pw-dump` exactly for
Node 22/22, Device 3/3, Client 22/22, Port 54/54, Link 7/7, Factory 13/13, Module 13/13,
Core 1/1, Profiler 1/1, SecurityContext 1/1 … **except Metadata**:

```
pw-cli ls Metadata   → 9 ids: 31,34,35,36,37,38,39,41,42
pw-dump (Metadata)   → 4 ids: 31,34,36,39          (extra: 35,37,38,41,42)
```

Reproducible **4/4** in ~90 ms brackets, on the default socket *and* on
`pipewire-0-manager` (same 9 vs 4), so it is not a visibility/socket effect: `ls` prints
registry-event props (e.g. `metadata.name = "persistent-sm-settings"`, `"sm-objects"`,
`"default-profile"`, `"filters"`, `"route-settings"`) for globals that `pw-dump` omits.
For those 5 ids, `pw-dump 35` and `pw-cli info 35` both return **rc 0 with empty stdout
and empty stderr** while `ls Metadata` happily prints them. *Labeled inference:* `ls`
enumerates registry globals while `pw-dump` only emits objects it can bind/read info
for; the mechanism is **unresolved** (both tools see the same socket and the same
manager socket gives the same split).

`pw-cli info all` — **135 objects vs 141 in pw-dump**, silently missing
`[3, 5, 31, 34, 36, 39]` = SecurityContext, Profiler and *all four visible* Metadata
objects. `pw-cli info <metadata id>` is rc 0 with **no message at all** (4 ids), while
`SecurityContext`/`Profiler` at least say `Error: "unsupported type …"`. So the pw-cli
"silent absence" class the scout documented as `unknown global` is really **four**
distinct rc-0-empty behaviours: unknown global (has a message), unsupported type (has a
message), metadata (no message), and `info all` omission (nothing at all).

`pw-cli ls Node` *does* expose `object.serial` — so a serial-only key that `info` cannot
resolve **is** resolvable through `ls` (`object.serial = "60843"` appears next to
`id 175`). "pw-cli cannot see serials" is wrong; "pw-cli `info` is id-keyed" is right.

Param-name modes (`enum-params <obj> <name>` on a node, a device, a client, a port):
`Profiles` and any unknown name are rejected by name —
`Error: "enum-params: unknown param type: <name>"` (rc 0); the profile surface is
`EnumProfile`/`Profile`; a bare number is accepted (`4` ≡ `Format`); clients answer
`Error: "enum-params not implemented on object 32 type:PipeWire:Interface:Client"`;
and a mid-sweep object death surfaces as a **new error shape**:
`remote 0: error id:149 seq:296 res:-116 (Stale file handle): no global 180 any more`.

`pw-cli info`'s prop block is **class-dependent** (V22): nodes/ports print flat
`key = value`, Device/Client print `* properties:` then `*\t\tkey = value`. A parser
tuned on nodes returns 0 props for devices/clients — which is exactly what happened
while building this analysis, and is worth a line in the report precisely because the
scout's §4.2 keyset comparison covered only nodes and a port.

## 5. pw-top under load: the trap holds, and the cadence mechanism is resolved

- **`-n 1` all-`C`: 12/12** in a busy window (26 rows each, 6.4–15.4 ms) and **6/6**
  under +16 own burners (32 rows each) — with the scout's 7/7 that is **25/25**, and the
  trap is load-invariant.
- **`-n 2/3/4`: first frame all-`C`, second frame real — 9/9 legs, plus the 8 correlation
  runs → 17/17 first frames.**
- **Cadence.** The scout left this unresolved (3–21 ms busy vs 1002/2002 ms idle). The
  second frame carries the driver row `R 231 1024 48000` → one graph cycle =
  1024/48000 = **21.33 ms**. Measured per-run wall times while the graph runs:
  `-n 2` 6.8–25.5 ms, `-n 3` 40.4–44.3 ms, `-n 4` 40.0–49.3 ms — i.e. **≈ one cycle per
  extra frame**. The same `-n 2` took **1010 ms** earlier in this session when every
  node was suspended (and the scout measured 1002/2002 ms in their idle window). Under
  CPU hog the cadence stays cycle-quantized (9.6–18.3 ms). So: **refresh is driven by
  graph stats updates (one per cycle while the graph runs), with a ~1 s fallback when it
  is idle — not a fixed timer and not CPU-load dependent.** The ~1 s fallback itself is
  still a black box (sibling streams kept the graph busy for the rest of my window).
- **Frame count is not `N`:** `-n 3` produced 4 frames in one run, `-n 2` produced 3 in
  another (headers verified at lines 1/28/55/82 of `raw/pwt-n3-rep2.txt`). The scout's
  operational rule survives unchanged — *read the last frame, never the first* — but
  "the second frame" is not guaranteed to be the last one.
- **Boundary modes:** `-n 0` prints exactly one frame; `-n -1` and `-n abc` are
  **infinite** (both hit my 30 s timeout: 966 / 1642 lines); `-r bogus-remote` fails
  loudly (`Can't connect: Host is down`, rc 255) — the one place in this family where a
  bad argument is not silent.

## 6. pactl ↔ native: the serial law, strengthened; two scout generalisations withdrawn

- **`pactl` index = native serial, 14/14 sinks, 16/16 sources (monitor sources resolved
  through their owning node), 5/5 sink-inputs.** Eleven witnesses have serial ≠ id and
  every one follows the serial: `r96s_ns` idx 116459 / id 110 / serial 116459;
  `r82ff_ns_2737990` idx 121099 / id 87; HDMI sink idx 60843 / id 175. Cards 3/3 but
  non-discriminating (id == serial there).
- **State vocabulary: 24/24 agreement, so the scout's "expect disagreement" rule is
  withdrawn as a generalisation.** Their n=1 was `r86ctl_ns` (pactl `IDLE` vs native
  `running`); that object no longer exists. My controlled A/B on one namespaced object:
  `r88b_state` idle → `SUSPENDED`/`suspended`/`S`; the same sink with my own `pw-cat`
  stream → `RUNNING`/`running`/`R`; 3/3 each, plus 18/18 across 6 sibling sinks. The
  advice "compare within one tight window" stands; "expect disagreement" does not.
- **§4.5 pulse-only ghost: 0/70.** I implemented the scout's own suggested falsification
  test (bracket `pactl list sinks` against `pw-dump` in one loop, recording pulse-only
  names with timestamps), 15 brackets before, 15 while my `r88b_ns` existed in *both*
  witnesses, 40 after unloading it — **zero** pulse-only names, so the bracket had
  sensitivity and the 4.5 observation did not reproduce (their own 5 tight brackets also
  failed to reproduce it).

## 7. BlueZ absent-class, re-measured after a reboot (V1/V2/V4/V5)

- Tree: adapter `hci0` + exactly one device `dev_BC_C7_46_34_C5_66`; Class 1288, Icon
  `input-gaming`, `Connected=false`, `Paired/Bonded/Trusted=true`, `ServicesResolved=false`,
  Modalias `usb:v054Cp0CE6d0100`, **UUIDs = HID `00001124` + PnP `00001200` only** — the
  HID-only record survived the reboot, so the class argument is durable, not a session
  artifact. Adapter: `Powered=true`, `Connectable=false`, `Discovering=false`,
  `Roles=[central, peripheral]`, 11 UUIDs.
- No bluez audio object: `pactl list cards` = 3 ALSA cards; no `bluez_card*`; no node with
  `device.api=bluez5` other than the MIDI bridge (`bluez_midi.server`, id 49,
  `factory.name=api.bluez5.midi.node`); the one `bluez|a2dp|sco` line in `pactl list` is
  `session.services`, i.e. *advertisement*, not an object.
- The DualSense USB-audio inference the scout labeled as unmeasured stays unmeasured, but
  is corroborated negatively: `aplay -l` and `pactl list cards` show **no Sony entry**
  (only "USB Audio"/"Generic USB Audio").
- **Fabrication attempt (new witness for V5):** `pw-cli create-node spa-node-factory
  '{ factory.name=api.bluez5.a2dp-sink node.name=r88b_fake }'` → refused
  `res:-2 (No such file or directory)`, `.sink` → `res:-2`, `.a2dp.source` and
  `.midi.node` → `res:-22 (Invalid argument)`; **all rc 0** and nothing created
  (cleanup check 0). There are only 13 generic factories; bluez5 nodes cannot be
  fabricated without a device.

## 8. Silent-failure inventory (the scout's §2 law, extended)

| probe | rc | stdout | stderr |
| --- | --- | --- | --- |
| `pw-dump 99999` (scout) | 0 | empty | empty |
| `pw-dump abc` / `pw-dump 99999999999999999999` | 0 | empty | **empty** |
| `pw-dump <serial of a dead object>` | 0 | empty | **empty** |
| `pw-dump ''` | 0 | **full dump** (398 KB) | empty |
| `pw-dump 60 61` (two ids) | 0 | **only id 60** | empty |
| `pw-dump --color=always 60` | 0 | JSON + ANSI escapes | empty |
| `pw-dump -1` | **255** | — | option error |
| `pw-cli info 99999` | 0 | empty | `unknown global` |
| `pw-cli info <metadata id>` | 0 | empty | **empty** |
| `pw-cli ls -N Node` (bad arg order) | 0 | **help text** | empty |
| `pw-cli create-node <bad factory>` | 0 | empty | protocol error |
| `pw-top -n -1` / `-n abc` | 124 (timeout) | endless frames | — |
| `pw-top -r bogus` | 255 | empty | `Can't connect: Host is down` |

Rule for downstream harnesses: never key on exit status, and never treat empty output as
absence — for `pw-dump` a *malformed* id and a *dead-object serial* are indistinguishable
from a live-but-invisible object.

## 9. What I could not falsify / open items

- **V1's "cannot become"** is an inference from the UUID set; the connect was not
  attempted (host mutation), and the scout's own reasoning for not doing so is sound.
- **The `~1 s` idle fallback mechanism** (V14): sibling streams (`r93s_in` drives the
  graph) held the graph busy for my whole window, so I could not produce an idle window
  myself without touching sibling objects.
- **`ls Metadata` 9-vs-4 mechanism** (V19): the split is deterministic and socket-independent;
  the reason `pw-dump` omits those 5 globals is unresolved.
- **`bluez5.codecs` runtime semantics** (V5/V6): the property is demonstrably parsed by
  the library; whether it is honoured per device still needs a device.
- **The `pactl IDLE` vs native `running` observation** (V16): not reproducible; the
  object that exhibited it (`r86ctl_ns`) is gone and no sibling currently reproduces it.
- **The scout's `bluez5.codecs` error's exact command** is unknown — there is no receipt,
  so I can only report the contradiction, not the mistake's shape (an exact-line grep
  would explain it).

## 10. Contention ledger (by name, all read-only from my side)

| contact | effect |
| --- | --- |
| **g3d lane** `yes` burners, cwd `/home/vgpnk/Projects/shokunin/game-dev-3d-shokunin` (ppid 1537; 48 at my entry, 64 while my 16 ran, **92 at exit** — that lane kept adding) | host already at loadavg 60–77 on 32 CPUs, `pressure/cpu some avg10` 53–75 % before I added anything; my "under load" legs are therefore *host-saturated*, and the hog battery adds a controlled +16 on top. None of the 92 is mine: my burners carry `argv[0]=r88b_hog` and `pgrep -f '^r88b_hog$'` is empty |
| audio siblings live in the graph throughout: `r82ff_ns_2737990`, `r82ff_2737990_tns/tdef_*_alias/env_sink`, `r86b_ns`, `r87b_ns`, `r87b_ns2`, `r87bfmt`, `r89b_ns`, `r89b_ns44`, **`r93s_in` (graph driver, QUANT 1024)**, `r93s_fc_in`, `r93s_fc_out`, `r93s_rec`, `r96s_ns`, `r98s_ns`, `r98s_stall`, `Lavf63.1.101`, `pw-play` ×2, `pw-cat`, `pipewire -c filter-chain.conf` (pid 2377877) | drove census drift (110→121→141 objects; 150 keys), the 17 mid-sweep object deaths, frame counts and the busy-window cadence; never mutated by me |
| my own objects (all removed, verified 0) | `r88b_ctl`, `r88b_ns`, `r88b_state` null sinks; `r88b_stream` (pw-cat); `r88b_tone.wav`; 16 × `r88b_hog` burners (16/16 killed, no survivors) |

**Kill discipline note (own error, recorded):** my first hog run discovered its burners
with `pgrep -x r88b_hog`, which matches `comm` (`yes`), not `argv[0]` — so it found none,
killed none and left 16 burners running. I detected them, killed all 16 by
`pgrep -f '^r88b_hog$'`, verified `[]` remaining and the foreign `yes` count back to 48,
then fixed the harness and re-ran the battery cleanly (16/16 killed). No sibling process
was signalled at any point.

## 11. Artifacts & provenance

`corpus/live/r88-boundary/` — `scripts/r88b_probe.py` (7 batteries), `r88b_fix.py`
(tab-safe ls counts, param matrix), `r88b_state.py` (idle↔active A/B),
`r88b_analysis.py` (verdict consolidation) → `receipts/summary.json`;
`receipts/B1…B11.json` + 9 censuses (per-run argv, rc, stdout/stderr sha256, wall ms,
UTC start); `raw/` = 475 captured files incl. `census-*.json`, `pwt-*`, `mode-*`,
`hog-*`, `verbatim-bluez-endpoint-log-since0208.txt`, `r88b_tone.wav`.

Stability: refusal texts byte-identical across all reps and across the hog boundary
(`stderr_sha256` equality); set-rule match on 133/133 stable keys; `ls` counts stable
4/4; the only unstable legs are the ones the scout also found unstable (pulse/native
census under sibling churn) — my censuses are kept per phase for that reason.
