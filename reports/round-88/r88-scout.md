# R88 scout — bluetooth audio on this host: absent-class measurement + pw-dump/pw-top vs pw-cli witness diff

Round 88 pre-measurement. Host `plazir27`, measured 2026-10-15 03:47–03:53
UTC−3 (06:47–06:53Z). Repo `~/Projects/shokunin/audio-shokunin` @ HEAD
`a2616f7` (`r78 LOG: adjudicator ADMIT-corr`). Tracked files dirty at entry —
`SHONEN.md`, `corpus/fixtures/measure_audio.py` (sibling-owned; never touched).
Toolchain: PipeWire **1.6.8** (pipewire-audio 1:1.6.8-1), WirePlumber
**0.5.17-1**, libpulse **17.0** (pactl 17.0-98-gb096, protocol 35), bluez
**5.87-2** (bluetoothd pid 1365, running since 2026-10-13 11:02), alsa-utils
1.2.16, Python 3.14.7.

**Seat: SCOUT (leaf). Zero tracked-file edits. Every write is under
`corpus/live/r88-scout/` plus this report. Not committed.** No node, link,
module, device or client was created or destroyed by this seat: the four
`pactl load-module` probes and two `pactl set-card-profile`/`send-message`
probes all refused (rc 1) and the pactl module-id set is **identical before and
after** the probe batch (`1,2,4,6,8,10,12,14,16,17,18,20,22,536870912–915,
536870918,536870921,536870922`; receipts `r88-legs.json:census`). Exit check:
zero `r88*` objects in the graph. Scratch 3.5 MB.

**Windows.** Main harness `r88_scout.py`: 49 legs / 131 fresh subprocesses in
**06:48:37.298–06:48:37.697Z (399 ms)**. Addendum `r88_addendum.py`: 15 legs /
43 runs in 06:50:13.100–06:50:15.822Z. Manual probes 03:47–03:53 local. The
graph was under live sibling-seat churn throughout (r79exp3_*, r82ffx_*,
`Lavf63.1.101`, r86ctl_ns) — every contention contact is listed in §8.

---

## 0. Headline — the brief's two branches

| # | branch | verdict | the single sharpest measured fact |
| --- | --- | --- | --- |
| 1 | any bluez audio device? | **NO — and the one paired device cannot become one** | the only bluez device object is a *DualSense Wireless Controller* `BC:C7:46:34:C5:66` (`Connected=false`, `Bonded/Trusted=true`, Class 1288, Icon `input-gaming`) whose UUIDs are **HID 0x1124 + PnP 0x1200 only** — no A2DP/HFP UUIDs, so no connect can yield a bluez audio node; `pactl list \| rg -i 'bluez\|a2dp\|sco'` matches **exactly 1 line** and it is the core property `session.services` |
| 2 | module-bluez5 loaded? | **DOES NOT EXIST ON THIS HOST** | `pactl load-module module-bluez5-{discover,device}` → `Failure: No such entity` rc 1, **6/6**; `find /usr/lib* -name '*module-bluez5*'` empty; the bluez5 SPA libs belong to **pipewire-audio**, not pipewire — 1.6.8's bluez support is wireplumber Lua (`monitors/bluez/*`) + `libspa-bluez5.so`, so the pulse module namespace has no target at all |
| 3 | is the stack dead? | **NO — live, endpoints registered, zero devices** | the current wireplumber (pid 2883626, started 02:08:27) holds **21 A2DP media endpoints** with bluetoothd (`sbc, aac, aptx, aptx_hd, aptx_ll_0/1, aptx_ll_duplex_0/1, faststream, faststream_duplex, ldac, opus_g, opus_05, opus_05_duplex` × sink/source), adapter UUIDs advertise A2DP src/sink (110a/110b), AVRCP (110c/110e), HFP HF/AG (111e/111f), BLE-MIDI; and the graph carries one live bluez5 node, `bluez_midi.server` (id 35, factory `api.bluez5.midi.node`) |
| 4 | codec switch a2dp↔hfp, SBC-XQ vs SBC params | **UNMEASURABLE — device-absence, not stack-absence** | no bluez media node exists to `enum-params`; what exists is static+endpoint evidence: 15 SPA codec plugins incl. `libspa-codec-bluez5-sbc.so` carrying `sbc_xq`/`SBC-XQ`/`spa.bluez5.codecs.sbc`, prop surface `bluez5.enable-sbc-xq`, `bluez5.enable-msbc`, `bluez5.enable-faststream`, `bluez5.enable-a2dp-duplex`, `bluez5.enable-hw-volume`, `bluez5.enable-lc3-a127`, `bluez5.roles`, `bluez5.headset-roles`, `bluez5.hfphsp-backend`, `bluez5.bap.*`, `bluez5.telephony.*`; **`bluez5.codecs` is not a string in libspa-bluez5.so** (measured absence) |
| 5 | pivot: pw-dump vs pw-cli | **TWO LAWS: set-query vs singleton, and keys agree while values/types/state do not** | `pw-dump <N>` returns **{object.id==N} ∪ {object.serial==N}** — verified 8/8 keys; key **60** → pw-dump `{node 35 bluez_midi.server (serial 60), port 60}` vs pw-cli `{port 60}`; key **35** → pw-dump `{client 32 (serial 35), node 35}`; `pw-cli info` prop keys are byte-identical to pw-dump's (13/13, 56/56, 19/19) but it stringly-types every value and drops all param values |
| 6 | pivot: pw-top | **`-n 1` is a trap; refresh 2 is the first valid frame** | `pw-top -b -n 1` (2 ms) shows **every row state `C` = CREATING** (man-page legend), 7/7 observations incl. a busy-graph window; `-n 2`'s second refresh carries real `S/I/R` that match the native state — wall cost of the extra frames measured 3–21 ms (busy window, `-n 2`) vs 1002 ms (idle, `-n 2`) |

---

## 1. BlueZ device class: absent, and structurally unable to appear

**Pulse layer.** `pactl list` at 03:48 has exactly **one** line matching
`bluez|a2dp|sco`, and it is not an object — it is the core property:

```
session.services = "[video-capture, policy.linking.standard, api.v4l2,
 api.alsa-seq, policy.linking.role-based, midi, api.libcamera, audio,
 policy.device.routes, bluetooth.midi, api.alsa, api.bluez, bluetooth.audio,
 policy.default-nodes, policy.device.profile]"
```

`pactl list cards` = 3 ALSA cards (GB205, USB Audio, Radeon); sinks/sources =
ALSA only. `pactl list modules` contains no bluez module. The advertisement is
component-derived: `/usr/share/wireplumber/scripts/session-services.lua:10-11`
maps `monitor.bluez → {bluetooth.audio, api.bluez}` and
`monitor.bluez-midi → {bluetooth.midi, api.bluez}` — so `bluetooth.audio` in
the services string **proves the bluez monitor component is loaded and
advertising**, while no bluez audio object exists. Advertised capability and
actual object class are decoupled; a consumer that trusts `session.services`
would over-claim.

**D-Bus layer.** `busctl --system tree org.bluez` = adapter
`/org/bluez/hci0` + exactly one device `dev_BC_C7_46_34_C5_66`. No
`org.bluez.MediaTransport*` objects exist (nothing is streaming). Adapter
`3C:EF:A5:44:96:DE` alias `plazir27`, `Powered=true`, `Connectable=false`,
`Discovering=false`, roles `central`+`peripheral`, Media1
`SupportedUUIDs=[110a,110b]` (A2DP source+sink), `SupportedFeatures=[tx-timestamping]`,
UUIDs (11): 110e AVRCP-target, 111f HFP-AG, 1200 PnP, 110b A2DP-sink,
110a A2DP-source, 110c AVRCP-controller, 1800/1801/180a GATT, BLE-MIDI
`03b80e5a-…`, 111e HFP-HF.

**The one device (full record, receipts `bluez-device-props`):** Name/Alias
`DualSense Wireless Controller`, Class `1288` (0x0508 — peripheral/gamepad),
Icon `input-gaming`, `Connected=false`, `ServicesResolved=false`,
`Paired/Bonded/Trusted=true`, `WakeAllowed=true`, `LegacyPairing=false`,
interfaces `org.bluez.Device1` + `org.bluez.Input1` (`ReconnectMode=device`),
`Modalias usb:v054Cp0CE6d0100` (Sony 0x0CE6 = DualSense), UUIDs
`[00001124 (HID), 00001200 (PnP)]`.

Two consequences, one observed and one inferred:

- **Observed:** the record's UUID set contains no A2DP (110a/110b) or HFP
  (111e/111f) UUID. Even if this device were connected, bluez would expose HID
  input only; a bluez *audio* node cannot originate from it. (Connecting it was
  deliberately not attempted — host-state mutation, and the UUID set already
  decides the class.)
- **Inference (labeled):** prior rounds r76–r78 recorded a DualSense **as a USB
  ALSA device** (`alsa_input.usb-Sony_Interactive_Entertainment_DualSense_Wireless_Controller-00.Direct__Direct__source`,
  `reports/round-78/r78-baseline.md:138-140,177-178`; `LOG.md:1328-1334`).
  Today `aplay -l` has no Sony entry and the pulse card list has no such card —
  the controller's audio face is USB and currently unplugged; the BT pairing
  above is the same physical device (Modalias match). This is consistent, not
  re-measured.

**The live bluez5 object that does exist:** node **35 `bluez_midi.server`**,
`media.class=Midi/Bridge`, `factory.name=api.bluez5.midi.node`,
`device.api=bluez5`, `api.bluez5.role="server"`, `node.description="BLE MIDI 1"`,
Props param `{deviceName="BLE MIDI 1", latencyOffsetNsec=0}`. Bluez **MIDI** is
live on this host while bluez **audio** is absent — a clean illustration that
"bluez works" and "bluez audio works" are different axes.

---

## 2. Refusal class, measured exactly (fresh process ×3 each)

| probe | rc | channel | exact text |
| --- | --- | --- | --- |
| `pactl load-module module-bluez5-discover` | 1,1,1 | stderr | `Failure: No such entity` |
| `pactl load-module module-bluez5-device` | 1,1,1 | stderr | `Failure: No such entity` |
| `pactl load-module module-bluez5-device path=/org/bluez/hci0` | 1,1,1 | stderr | `Failure: No such entity` |
| `pactl load-module module-bluez5-discover a2dp_source=false` | 1 | stderr | `Failure: No such entity` |
| `pactl send-message /org/bluez/hci0 /org/bluez/hci0` | 1,1,1 | stderr | `Send message failed: No such entity` |
| `pactl set-card-profile bluez_card.BC_C7_46_34_C5_66 a2dp-sink` | 1,1,1 | stderr | `Failure: No such entity` |
| `pw-cli info 99999` | **0**,0,0 | stderr | `Error: "info: unknown global '99999'"` |
| `pw-cli enum-params 99999 Format` | **0**,0,0 | stderr | `Error: "enum-params: unknown global '99999'"` |
| `pw-cli enum-params 35 Format` (param absent on node) | **0**,0,0 | stderr | `remote 0: error id:52 seq:256 res:-2 (No such file or directory): enum params id:4 (Spa:Enum:ParamId:Format) failed` |
| `pw-dump 99999` | **0**,0,0 | — | empty stdout, no stderr — **silent absence** |

Two laws fall out. (a) The **pulse** surface refuses by name with rc 1 — the
module/recipient/card does not exist in pipewire-pulse's namespace, which is
literal: there is no `libpipewire-module-bluez5*.so` anywhere in `/usr/lib*`
(`find` empty; `pacman -Ql pipewire | rg -c bluez` = 0; the SPA libs are owned
by `pipewire-audio 1:1.6.8-1`), and no bluez object exists in the graph.
(b) The **native** CLIs refuse with **rc 0** and route the failure to stderr —
scripted callers that check `$?` will read a pw-cli/pw-dump failure as success;
`pw-dump` on an unknown id is the worst case (rc 0, empty output, no message).
Never probe "does this bluez card exist" with exit status.

Note the module probes changed **nothing**: module-id set identical before/after
(§ header), and no module with a bluez name exists to be loaded.

---

## 3. Codec surface without a device (what can and cannot be said)

**Live D-Bus witness** (`bluez-endpoint-log`, current sender `:1.75450` =
wireplumber pid 2883626; 21 paths): `A2DPSink/{sbc,aac,aptx,aptx_hd,opus_g,opus_05,opus_05_duplex}`,
`A2DPSource/{sbc,aac,aptx,aptx_hd,ldac,opus_g,opus_05,opus_05_duplex,faststream,faststream_duplex,aptx_ll_0,aptx_ll_1,aptx_ll_duplex_0,aptx_ll_duplex_1}`.
There are **no HFP/HSP media endpoints** — expected, HFP is not an A2DP media
endpoint (it runs over RFCOMM/SCO); the HFP surface is
`bluez5.headset-roles`/`bluez5.hfphsp-backend` and the `hfp-*` codec plugins,
not a registered endpoint. So "HFP is missing" cannot be concluded from this
list, and was not.

**Static witness** (15 files in `/usr/lib/spa-0.2/bluez5/`):
`libspa-bluez5.so` + codec plugins `sbc, aac, aptx, faststream, g722,
hfp-cvsd, hfp-lc3-a127, hfp-lc3-swb, hfp-msbc, lc3, ldac, opus, opus-g`.
`libspa-codec-bluez5-sbc.so` carries the strings `sbc_xq`, `SBC-XQ`,
`spa.bluez5.codecs.sbc` — i.e., the SBC-XQ mode lives inside the SBC codec
plugin, reachable only through a live bluez media node. Prop surface from
`libspa-bluez5.so` includes `bluez5.enable-sbc-xq`, `bluez5.enable-msbc`,
`bluez5.enable-faststream`, `bluez5.enable-a2dp-duplex`,
`bluez5.enable-hw-volume`, `bluez5.enable-lc3-a127`, `bluez5.roles`,
`bluez5.headset-roles`, `bluez5.media-source-role`, `bluez5.hfphsp-backend`,
`bluez5.auto-connect`, `bluez5.autoswitch-routes`, `bluez5.hw-offload-datapath`,
the LE-Audio `bluez5.bap.*` family and `bluez5.telephony.*`. **`bluez5.codecs`
does not appear as a string in `libspa-bluez5.so`** — in 1.6.8 codec
preference is expressed through the `enable-*` flags plus the registered
endpoint set (or set per device at runtime); the classic
`bluez5.codecs=[...]` property string was not found here (searched, absent —
absence of a string is not proof of absence of a runtime prop, see §6).

**Host config, unexercised:** `~/.config/wireplumber/wireplumber.conf.d/bluetooth-a2dp-autoconnect.conf`
(mtime 2026-10-03) sets `monitor.bluez.rules → bluez5.auto-connect =
[a2dp_sink a2dp_source]`. The wireplumber user journal since 02:08 shows no
config-parse error and no bluez line at the current log level, so the rule is
parsed but has had nothing to act on.

**Not measurable here, named:** a2dp↔hfp profile switch and its media.class
churn (needs a connected headset); live `pw-cli enum-params` for SBC-XQ vs SBC
params (needs a bluez media node); codec negotiation/bitpool behavior; AVRCP;
BLE-MIDI end-to-end (node exists, no BLE-MIDI peer).

---

## 4. Pivot — same object, four witnesses, five disagreements

Receipts: `receipts/analysis.json` (`objects`, `set_rule`, `pwt`, `pactl_map`).
Objects compared: node **35** `bluez_midi.server`, node **46**
`alsa_output.usb-…SPDIF__sink`, node **133** `r86ctl_ns`, plus port **60** as a
control.

### 4.1 `pw-dump <N>` is a set query; `pw-cli info <N>` is a singleton

`pw-dump <N>` prints **every object with `object.id == N` or
`object.serial == N`**. Verified on 8 keys, 8/8 (`set_rule`):

| key | pw-dump returns | pw-cli info returns |
| --- | --- | --- |
| 35 | client 32 (serial 35) **+** node 35 `bluez_midi.server` | node 35 |
| 46 | client 45 (serial 46) **+** node 46 SPDIF sink | node 46 |
| **60** | **node 35** (serial 60) **+** port 60 | **port 60 only** — HDMI sink's `playback_FL`, `node.id=57`, `object.path=alsa:acp:NVidia:4:playback:playback_0` |
| 32 / 33 / 45 / 133 | single object | single object |
| 99999 | empty stdout, rc 0 | `unknown global` error, rc 0 |

The serial collision is not exotic: on this host 3 of 7 live keys queried
(35, 46, 60) return a two-object bundle, and for key 60 the two witnesses
answer with **different objects of different types** (`Node` vs `Port`).
`pw-dump`'s own manpage says `[<id>]`; nothing warns that the match is
id-or-serial. Any harness that equates "the pw-dump result for id N" with "the
object N" is wrong — select by `.id == N` from a full dump, or expect bundles.

### 4.2 Property keys agree; types, params and state do not

- **Keys:** identical sets on all three objects — 13/13 (35), **56/56** (46),
  19/19 (133); zero value mismatches.
- **Types:** `pw-cli info` quotes every value as a string; `pw-dump` preserves
  JSON types. Node 46: 19 ints + 3 bools among 56 props. Example pair —
  dump `"factory.id": 19` (number) / `"node.pause-on-idle": false` (boolean)
  vs cli `factory.id = "19"` / `node.pause-on-idle = "false"`.
- **Params — key presence ≠ value availability.** Both witnesses list the same
  param names per object (35: `PropInfo/Props/IO`; 46 and 133: 9 params; port
  60: 7 incl. `Meta/IO/Buffers`), but `pw-dump` emits **empty lists** for
  unreadable params while `pw-cli info` reports the **access flags** and no
  values at all. Port 60: `Format` (`-w`) → `[]`, `Buffers` (`--`) → `[]`,
  `Tag` → `[]`, while `EnumFormat` → `F32P`, `Meta` → `{Header,32}`,
  `IO` → `{Buffers,8}`, `Latency` → 2 entries. Node 133: `Format` (`-w`) → `[]`,
  `Latency/ProcessLatency/Tag` (`rw`) → `[]`. Neither witness alone answers
  "what can this object do": cli has rights, dump has values, and empty in
  dump does not mean the param is absent.
- **State — different vocabularies, measured same-instant ×3.** Node 133
  (tight triple, 3/3): `pactl` **IDLE** / `pw-dump` **running** / `pw-cli`
  **running** / `pw-top` refresh-2 **R**. Node 46 at rest (tight triple, 3/3):
  all four agree (`SUSPENDED`/`suspended`/`S`). State is also the churn axis —
  an earlier capture had node 46 `running` in pw-dump while the pulse leg
  seconds earlier said `SUSPENDED`. Rule: compare states only within one
  tight window, and expect the pulse vocabulary (stream/sink activity) to
  disagree with the native vocabulary (node scheduling) on the same object.

### 4.3 `pw-top`: the first refresh is not a witness

`pw-top -b -n 1` (2 ms) prints **one** frame in which every row shows `C`.
The manpage legend (captured, `raw/add-pwtop-man.1.txt`): `E`=ERROR,
**`C`=CREATING**, `S`=SUSPENDED, `I`=IDLE, `R`=RUNNING, `t`/`T`=transport.
Observed 7/7: `-n 1` legs and the first frame of every `-n 2`/`-n 3` run
(all-`C`), including runs during an actively cycling sibling graph. The second
frame carries real states that match the native witnesses. Wall cost of the
extra frames, two windows measured: in the busy window (addendum, 06:50:13,
sibling driver cycling) the three `-n 2` runs took **3, 3, 21 ms** and the
three `-n 3` runs **~1.0 s each**; idle (06:57) `-n 2` = **1002 ms** and
`-n 3` = **2002 ms**. The cadence is **not** a simple per-frame constant and its
mechanism (stats-driven vs fixed timer) is **unresolved** — but the operational
rule is stable: **never read state from `-n 1`; use `-n 2` and read the last
frame.**

Other pw-top deltas: it shows `node.name` (never `node.description` — node 35
renders `bluez_midi.server`, not "BLE MIDI 1"), no `media.class`, devices are
absent (only nodes), and its row set churns with sibling activity
(`r79exp3_*`, `r82ffx_*`, transient `Lavf63.1.101` seen mid-harness).

### 4.4 `pactl` index is the native **serial**, not the native id

| pactl index | native node id | native serial | name |
| --- | --- | --- | --- |
| 59 | 57 | 59 | hdmi-stereo |
| 63 | 46 | 63 | SPDIF sink |
| 64 | 54 | 64 | Speaker |
| 65 | 53 | 65 | Headphones |
| 37244 | 133 | 37244 | r86ctl_ns |
| 40501 | 158 | 40501 | r82ff_ns (sibling, gone by 03:51) |

So "pactl sink 63" and "pw-cli id 63" are **different objects** (sink 63 ↔ node
46; id 63 is a port). Correlate pulse↔native through `object.serial`
(equivalently: resolve name → native id), never through the number itself.

### 4.5 One unresolved observation (classified, not folded)

At 03:48:0x `pactl list sinks short` listed `r79exp2_ns_3700278` (index 40601)
while the native census taken seconds later contained **no** such node and the
full dump text did not contain the name at all; by 03:51 the sink was gone from
the pulse list too. Hypotheses: (a) a pulse-layer ghost (sink object alive after
its native node died), (b) a sibling-owned transient node destroyed between the
two legs (r79exp3_* experiments were actively creating/destroying nodes in that
exact window). Five tight brackets (pulse set vs native set, ~12 ms apart,
03:51:19) showed **identical sets** — not reproduced. Falsification test if it
matters: bracket `pactl list sinks` and `pw-dump` inside one process loop and
record every pulse-only name with timestamps.

---

## 5. Falsification list (what was tried that could have killed each claim)

| claim | falsifier attempted | outcome |
| --- | --- | --- |
| no bluez audio device | search pactl objects, pw-dump nodes (`device.api=bluez5` / `bluez_card*`), busctl MediaTransport objects | 0/0/0; only bluez5 object is MIDI node 35; adapter *does* advertise A2DP (capability ≠ object) |
| module-bluez5 unavailable | load it 3×2 (name and args variants), `find /usr/lib*`, `pacman -Ql pipewire`, `pacman -Qo` the SPA libs | 6/6 `No such entity`; no `.so`; pipewire ships 0 bluez files; libs owned by `pipewire-audio` |
| stack is dead, not just device-less | journal endpoint registrations, bluez_midi node, adapter Powered, Media1 SupportedUUIDs | all positive: 21 endpoints from the live wireplumber pid; MIDI node live; stack alive |
| DualSense could be the missing audio device | read its UUID set + interfaces + Connected | UUIDs HID+PnP only, no A2DP/HFP; HID-only record decides the class (connect not attempted, mutation) |
| pw-cli info ≡ pw-dump (props) | set-diff both directions on 3 objects + port control | equal key sets, **but** type representation, param values and state diverge (§4.2) |
| `pw-dump <N>` is a single-object view | 8 keys incl. serial-collision keys 35/46/60 | falsified 3/8 — id-or-serial bundle law |
| `pw-top -n 1` is a valid state witness | 7 captures incl. busy-graph window | falsified 7/7 — all rows `C`=CREATING |
| pactl state matches native state | tight triple on node 133, ×3 | falsified 3/3 — `IDLE` vs `running`/`R` |
| refusal probes changed host state | module-id set before/after, graph search for `r88*` | unchanged / none |

## 6. Named coverage (not measured, and why)

- **No real bluez audio flow**: profile switch a2dp↔hfp, media.class churn,
  codec negotiation, SBC-XQ vs SBC live params, bitpool, AVRCP, HW volume,
  latency — all need a connected bluez audio device; none exists and none can
  be fabricated from the paired HID record.
- **`bluez5.codecs` runtime semantics**: the property string is absent from
  `libspa-bluez5.so` (searched); whether it is accepted per-device at runtime
  is only observable with a device. Treat the `enable-*` flags + endpoint list
  as the 1.6.8 surface; do not cite `bluez5.codecs` as live.
- **HFP/HSP endpoint registration**: not an A2DP media endpoint; the endpoint
  log cannot speak to it.
- **BLE-MIDI end-to-end**: node exists (id 35); no BLE-MIDI peer tested.
- **WirePlumber bluez monitor internals**: no bluez lines in the user journal
  at the current log level; only advertisement + endpoint witnesses obtained.
- **pw-top refresh-cadence mechanism**: two windows disagree (0.02 s vs 1.0 s
  per extra frame); unresolved.
- **DualSense over BT**: deliberately not connected.

## 7. Artifacts & provenance

`corpus/live/r88-scout/` (untracked, 3.5 MB):

- `scripts/r88_scout.py` (49 legs / 131 runs), `scripts/r88_addendum.py`
  (15 legs / 43 runs), `scripts/r88_analysis.py` (diff engine; reads raw/,
  writes `receipts/analysis.json`).
- `receipts/r88-legs.json`, `receipts/r88-addendum.json` — per-run argv, rc,
  stdout/stderr sha256, UTC start/end; `receipts/analysis.json` — stability
  table, per-object prop/param/state diffs, set-rule verification, pw-top
  frame parses, pactl map, endpoint list, refusal texts. Provenance caveat: the
  main harness calls the `pw-top-n1` leg three times under one name, so raw/
  keeps only the last of those three captures (the receipts keep all three
  hashes); the addendum's `-n 2`/`-n 3` captures are all present and are the
  ones the pw-top claims rest on.
- `raw/` — 346 captured files (stdout + stderr per run) incl. `pactl-list.{1..3}.txt`,
  `pw-dump-{35,46,133}.{1..3}.json`, `pw-cli-info-*`, `pw-cli-{props,format,propinfo}-*`,
  `pw-top-n1.*`, `add-pwtop-n{2,3}.*`, `add-dump-{32,33,35,45,46,60}.json`,
  `bluez-*` (tree, device/adapter/Media1 introspection, endpoint log),
  `add-pwtop-man.1.txt` (state legend), `spa-bluez5-inventory`,
  `pipewire-modules-inventory`.

**Stability.** 56/62 legs byte-identical across fresh ×3. The 6 unstable legs
are all explained and expected: `pactl-info` (its `Client Index` increments per
connection — 40799 vs 40800), `pactl-list`, `wpctl-status`, `pw-dump-census`
(sibling churn), `add-pwtop-n2`, `add-pwtop-n3` (churn + cadence). Nothing in
the headline rests on an unstable leg.

**Confidence.** High: the absent class (multiple independent witnesses: pactl,
pw-dump, busctl, package/file inventory), the refusal texts (6/6 and 3/3),
the set-rule (8/8), the prop/param diffs (3 objects + port control), the
pw-top `-n 1` artifact (7/7), the state-vocabulary split (3/3 tight), the
endpoint list (single live sender). Medium: the USB-vs-BT DualSense identity
(Modalias match, not re-measured); the pw-top cadence mechanism. Low/unresolved:
the single pulse-only sink observation (§4.5).

## 8. Contention ledger (shared objects observed, none mutated)

| window | contact | effect |
| --- | --- | --- |
| throughout | sibling nodes `r79exp3_*`, `r82ffx_*`, `r86ctl_ns`, `r82ff_ns`, transient `Lavf63.1.101` | read-only; drove census/pw-top instability and the pulse-only sink observation |
| 03:45–03:51 | wireplumber log: `s-linking: … No input node for loopback-*` + `wp-properties: wp_properties_get: assertion 'self != NULL' failed` (03:50:48) | sibling activity; not mine |
| 02:53:10–16 (pre-seat) | `rfkill unblock bluetooth` (user journal) + bluetoothd `Disconnecting failed: already disconnected` / `No matching connection for device` | host event before this window; recorded, not interpreted |
| 03:48–03:52 | my probes: pactl list/info/modules, pw-dump/pw-cli/pw-top, busctl get/introspect/tree, journalctl, 4 `load-module` refusals, 3 `send-message` refusals, 3 `set-card-profile` refusals | no module/node/link/file outside `corpus/live/r88-scout/`; module-id set identical before/after |
