# R84 scout — ALSA-direct lattice + pulse-compat deeper params

Round 84 pre-measurement. Host `plazir27`, measured **2026-10-15 ~05:54–06:35 UTC**.
Repo `~/Projects/shokunin/audio-shokunin` @ HEAD `a2616f73`. Toolchain: PipeWire
**1.6.8**, libpulse **17.0-98-gb096** (pactl, protocol 35), alsa-utils **1.2.16**
(aplay/arecord/speaker-test), WirePlumber (alive throughout), Python **3.14.7**
(numpy 2.5.3), Linux **7.2.3-arch1-3**.

**Seat: SCOUT (leaf). Zero tracked-file edits. Every write is under
`corpus/live/r84-scout/` + this report** (`runs/` per-leg receipts,
`receipts/*.json` consolidated, `r84_probe.py` harness — own tone synth, own FFT
windows, own classifiers; `corpus/fixtures` never read or imported). Seat-owned
objects tagged `r84alsa_*`; every `pactl unload-module` was **index-verified
against `sink_name=` first** and nothing was ever unloaded by name. Two sibling
lanes were live the whole session (`r83dsp_*` streams RUNNING, `r82ff_*` present)
— §10 is the ledger, including one stream-restore contamination this seat caused
and repaired, and verified clean at exit (0 `r84alsa_*` sinks/modules remain).

**Coordination note (r82/r83 in flight):** no ffmpeg, GStreamer, or DSP surface
was re-measured. One foreign stream (`Lavf63.1.101`/`r82ff-play`, ffmpeg) did
appear inside my `pactl list sink-inputs` snapshots — observed, never touched.

---

## 0. Headline: seven frontier claims

| # | frontier | verdict | the single sharpest measured fact |
| --- | --- | --- | --- |
| 1 | aplay/arecord `-D` lattice | **PINNED (30+ play devices, 22 capture legs ×3)** | `hw:`/`plughw:`/`front:`/`surround*`/`iec958 d0`/`hdmi:*`/`null`/`sysdefault` all resolve; `pulse` is **not** a PCM; refusal classes split five ways by *which layer* fails (§1.3) |
| 2 | `pipewire:ARG=` device-string params | **NEW SURFACE** | the plugin conf takes `NODE/ROLE/RATE/FORMAT/CHANNELS/PERIOD_BYTES/BUFFER_BYTES/EXCLUSIVE/SERVER`: `NODE=` writes **`target.object`** (pins, silent-fallback on miss), `ROLE=` writes **`media.role`**, `PERIOD_BYTES=4096` → `node.latency=1024/48000`; env `PIPEWIRE_NODE`/`PIPEWIRE_PROPS` also land |
| 3 | plugin *capture* path is state-unstable | **THREE SHAPES FOR ONE COMMAND** | `arecord -D pipewire|default`: `Unable to install hw params` (06:0x batch) → `TICK_TIME: [0 0]` (06:2x batch) — r78 saw TICK_TIME, r78p saw it **work**; but `pipewire:NODE=<source-name|serial>` **captures fine in the same batch** |
| 4 | speaker-test headless | **USABLE + cells pinned** | `-D null` exits in 0.16 s; plugin lands `alsa_playback.speaker-test` linked to current default; `pipewire:NODE=` pins it; `-c 6` completes in 18.1 s; `-c 1` on `hw:0,0` → `Channels count (1) not available` |
| 5 | `PULSE_PROP_*` env | **VERBATIM PROP VECTOR, two exceptions** | arbitrary keys land on the pw node (`zzz.invented=42` lands as int; `application.icon_name`→`application.icon-name`); `application.name`/`media.name` env **lose** to the client's own proplist; pulse view normalizes `media.role Communication→phone` while the node keeps the raw string; **bare `PULSE_PROP=` is also parsed** |
| 6 | pactl write surface on a live stream | **CUBIC LAW + SUSPEND-AS-HINT** | monitor taps are **post-gain**: `set-sink-volume 50%` → 8192→**1024** (0.5³), `150%`→**27648** (3.375×), `25%`→**128** — exact cubic→linear on the sink AND on `set-source-volume <sink>.monitor`; `suspend-*` on a **linked** object is a silent no-op (state stays RUNNING, flow unbroken); on an idle object it flips to SUSPENDED and playing into a suspended sink wakes it |
| 7 | `parec --monitor-stream` deep | **STREAM-PIN LAW** | pin captures exactly one sink-input **pre-mix** (two-tone separation 1k vs 2k), `-d` is **ignored entirely** once `--monitor-stream` is present (bogus and foreign `-d` still capture); index must be a **sink-input** serial — a source-output serial is rc=0 with a 44-B empty wav; stream death → file stops growing, no EOS/error; `move-sink-input` mid-run → capture **follows the stream**; `set-sink-input-volume` mid-run is **invisible** to the tap (pre-gain) but the same value persists via stream-restore and re-appears as stream-node gain on respawn |

Plus two unasked-for classes: **`arecord -D null` does not emit zeros** —
~668 nonzero frame-rows per second in ~80-frame bursts spaced exactly 5512
frames (period edges), peak ≈ 32500 — and **`pactl set-sink-input-volume`
persists through module-stream-restore** to later streams of the same restore
key (measured respawn reads the old volume, visible even in the per-stream tap).

---

## 1. FRONTIER 1 — the `-D` device lattice (`receipts/p1-aplay.json`, `p2-arecord.json`)

Host inventory: `aplay -L` = {null, sysdefault, pipewire, default,
sysdefault:CARD=Audio, front:CARD=Audio,DEV=0, surround21/40/41/50/51/71,
iec958 DEV=0..1, hdmi:CARD=NVidia,DEV=0..3, hdmi:CARD=Generic,DEV=0..3};
`arecord -L` is shorter (no surround/iec958/hdmi — card 0 capture = devs 0–2
only, `00-03` is playback-only). `pulse` is **absent** from both lists.

### 1.1 Playback resolution (1.2 s dual-tone wav, amp 8192, ×3 reps, all stable)

| dev | rc | witness |
| --- | --- | --- |
| `null` | 0 | instant discard (unpaced) |
| `sysdefault` / `sysdefault:CARD=Audio` | 0 | no pw node — direct to card 0 sysdefault |
| `pipewire` / `default` | 0 | node `alsa_playback.aplay` → linked to **current default sink** (SPDIF in these reps) |
| `front`/`surround51`/`surround71` `:CARD=Audio,DEV=0` | 0 | no node; surround plugs a stereo file onto the 8ch-capable PCM |
| `iec958:CARD=Audio,DEV=0` | 0 | direct |
| `iec958:CARD=Audio,DEV=1` | **1** | **listed in `-L` but open fails** `No such file or directory` |
| `hdmi:CARD=NVidia,DEV=0..3` / `hdmi:CARD=Generic,DEV=0` | 0 | direct; **`DEV` is a slot index** — `DEV=2` resolves even though card 1 has no subdevice 2 |
| `hw:0,0` `hw:0,1` `hw:0,2` `hw:0,3` `hw:1,3` `hw:2,3` | 0 | no node; bypasses the graph entirely |
| `plughw:0,0` `plughw:0,3` | 0 | same + plug conversion layer |
| `hw:CARD=Audio,DEV=0` `hw:CARD=NVidia,DEV=3` | 0 | name form ≡ numeric form |

### 1.2 Capture resolution (`-f cd`, −d N, ×3)

| dev | rc | file/peak |
| --- | --- | --- |
| `sysdefault`, `sysdefault:CARD=Audio`, `front:CARD=Audio,DEV=0`, `hw:0,0`, `plughw:0,0`, `plughw:0,1`, `hw:CARD=Audio,DEV=1` | 0 | 176444 B/s; **analog floor peak ≈ 620–663 on dev 0** routes; `hw:0,1`/`hw:0,2`/`hw:CARD=Audio,DEV=1` read **exact 0** (silent digital paths — route pins the content law, per r78) |
| `null` | 0 | **NOT zeros** — see §7.1 |
| `hw:0,3` | 1 | `audio open error: No such file or directory` — playback-only PCM has no capture subdevice |
| `hw:1,3` | 1 | same (HDMI has no capture) |
| `pipewire` / `default` | **1** | **state-dependent** — `Unable to install hw params` in the first batch, `TICK_TIME: [0 0]` in the second, same command, minutes apart (§3) |
| `pipewire:NODE=<Line source>` `…<Mic>` `…<serial 66>` | **0** | real capture in the same batch where bare `pipewire` fails — **explicit `NODE=` revives the plugin capture path**; node is `alsa_capture.aplay` with `target.object=<arg>` |
| `pipewire:NODE=<sink>` / `NODE=no_such` / `ROLE=…` | 1 | TICK_TIME — capture-side target miss is a refusal, not a fallback (one-sided fallback law holds through the plugin too) |

### 1.3 Refusal taxonomy — five layers, all rc=1 (stable ×3)

| class | signature (verbatim stderr) | triggers |
| --- | --- | --- |
| `alsa_unknown_pcm` | `ALSA lib pcm.c:2722:(snd_pcm_open_noupdate) [error.pcm] Unknown PCM <x>` | `pulse`, `nosuch_pcm_r84`, `-D ''` (aplay prints the empty name; arecord then eats `-d` as the device → `Unknown PCM -d`) |
| `alsa_card_index` | `ALSA lib confmisc.c:165:(snd_config_get_card) [error.core] Cannot get card index for <x>` | `hw:9`, `hw:9,9`, `plughw:9,9`, `hw:CARD=NosuchR84` |
| `alsa_card_parse` | `ALSA lib confmisc.c:855:(parse_card) [error.core] cannot find card '<x>'` | `sysdefault:CARD=Nosuch`, `front:CARD=Nosuch` — same failure one layer down (named-PCM expansion) |
| `alsa_pcmdef_missing` | `ALSA lib confmisc.c:1377:(snd_func_refer) Unable to find definition 'cards.0.pcm.iec958.9:…'` | `iec958:CARD=Audio,DEV=9` — definition absent before the card is even resolved |
| `alsa_unknown_param` | `ALSA lib conf.c:5701:(snd_config_expand) [error.core] Unknown parameters CARD=Audio` | args passed to a PCM that takes none (`default:CARD=Audio`) |
| `alsa_open_enoent` | `aplay/arecord: main:850: audio open error: No such file or directory` | name resolves, subdevice absent/not-capture (`hw:0,9`, `iec958 DEV=1`, `hw:1,3` c, `hw:0,3` c) |
| `alsa_open_ebusy` | `main:850: audio open error: Device or resource busy` | PipeWire holds the PCM: measured 3/3 with a live `pw-play`→Speaker on `hw:0,0`/`plughw:0,0` and a live `pw-record`→Line on `hw:0,1`; `/proc/asound/card0/pcm0p/sub0/status` reads `RUNNING` while the refusal fires |
| `alsa_params` | `aplay: set_params:1404: Channels count non available` | post-open negotiation: `pipewire:CHANNELS=6` + stereo file, `CHANNELS=1` + stereo file (**mono file + CHANNELS=1 → rc=0** — the arg must match the file) |
| `alsa_pw_conn` | `aplay: main:850: audio open error: Host is down` | `pipewire:SERVER=nonexistent_r84` |
| `alsa_pw_capture_unstable` | `Unable to install hw params` **or** `TICK_TIME: [0 0]` | plugin capture without a working NODE= — *which* refusal you get is host-state dependent (§3) |

---

## 2. FRONTIER 2 — `pipewire:` device-string args (`receipts/p1b-plugin-args.json`)

`/usr/share/alsa/alsa.conf.d/50-pipewire.conf` declares args
`SERVER NODE EXCLUSIVE ROLE RATE FORMAT CHANNELS PERIOD_BYTES BUFFER_BYTES`.
Measured on the live node props + link witness (×3 each):

| leg | node prop written | link/effect |
| --- | --- | --- |
| `pipewire:NODE=r84alsa_ns` | `target.object="r84alsa_ns"` | links to `r84alsa_ns:playback_*` — **device-string-level pin, no CLI needed** |
| `pipewire:NODE=no_such_r84` | `target.object="no_such_r84"` | **rc=0, links to the current default sink** — silent fallback (r78 playback law through the plugin) |
| `pipewire:ROLE=Communication` | `media.role="Communication"` | routes normally |
| `pipewire:RATE=44100` + 48 k wav | — | rc=0 + `Warning: rate is not accurate (requested=48000, got=44100)` — negotiated to the arg |
| `pipewire:CHANNELS=2` + stereo wav | — | rc=0; `CHANNELS=6`/mono-mismatch → `Channels count non available` (rc=1) |
| `pipewire:PERIOD_BYTES=4096,BUFFER_BYTES=16384` | `node.latency="1024/48000"` (vs default 6000) | real param — period in *frames* lands on the node |
| `pipewire:FORMAT=s32le` | — | rc=0, no refusal |
| `pipewire:EXCLUSIVE=1` | — | rc=0, links normally (no exclusive-prop visible on node) |
| env `PIPEWIRE_NODE=r84alsa_ns` | `target.object` set | routes to `r84alsa_ns` — env vector honored |
| env `PIPEWIRE_PROPS={node.name=r84alsa_envp media.role=Communication}` | `node.name` **and** `media.role` land | env props reach the plugin |
| `pipewire:SERVER=nonexistent` | — | rc=1 `Host is down` |

The plugin is a full prop/targeting surface: **NODE, ROLE, and the env vectors
are cell-armable device-string params.** Node names: playback `alsa_playback.<bin>`
, capture `alsa_capture.aplay` (even for arecord — the client id is the library's,
`application.name="PipeWire ALSA [aplay]"`).

---

## 3. FRONTIER 3 — plugin capture is state-unstable (the third shape)

`arecord -D pipewire -d N -f cd` (and `-D default`, bare, `-f dat`, bare-u8):

| session | result | class |
| --- | --- | --- |
| r78 scout | rc=1 `TICK_TIME: [0 0]` | `alsa_tick_time` |
| r78 playback scout | **rc=0, real file** (16044 B u8; 352844 B cd) | works |
| r84 first batch (~06:0x) | rc=1 `Unable to install hw params:` | `alsa_pw_hwparams` |
| r84 second batch (~06:2x) | rc=1 `TICK_TIME: [0 0]` | `alsa_tick_time` |

**Both r84 shapes are rc=1, missing file, 3/3 stable within their window** — the
window flips between them. And the discriminating fact: in the `Unable to
install hw params` window, `pipewire:NODE=<a real Audio/Source name>` captured
successfully 3/3 (`node_line` rc=0, 176444 B, `target.object` prop set) — the
un-targeted autoconnect path failed while the explicit pin worked. Arm on the
*sum*: "plugin capture without NODE= fails in current host states (rc=1, no
file); `pipewire:NODE=<source>` captures." Which stderr shape fires is not
arm-able yet.

---

## 4. FRONTIER 4 — `speaker-test` headless (`receipts/p3-speaker.json`, ×3)

Fully usable headless (no display, `-l` bounds loops). Node on plugin devices:
`alsa_playback.speaker-test`; `-D pipewire:NODE=r84alsa_ns` pins it to my sink —
**the device-string target works for speaker-test too**.

| leg | rc | wall | note |
| --- | --- | --- | --- |
| `-D null -c2 -l1 -t sine` | 0 | **0.16 s** | null is unpaced — `-l` still bounds it |
| `-D pipewire`/`-D default` -c2 -l1 -S5 | 0 | ~6.2 s | node → current default sink (SPDIF) |
| `-D pipewire:NODE=r84alsa_ns` -c2 -l1 | 0 | ~6.1 s | links `r84alsa_ns:playback_*` |
| `-D hw:0,0` / `plughw:0,0` -c2 -l1 | 0 | ~6.3 s | no pw node — direct |
| `-c 6 -l1` (plughw or hw:0,0) | 0 | **18.1 s** | ≈3 s/channel × 6; a 12 s cap reads as a false hang — bound generously |
| `-c 8 -l1` hw:0,0 | — | >14 s | same pacing law (killed at my cap; device accepts [2 8]ch) |
| `-c 1` hw:0,0 | 1 | 0.16 s | `Channels count (1) not available for playbacks: Invalid argument` — hw refuses below the PCM floor |
| `-c 0` | 0 | 0.16 s | **accepted, instant no-op** |
| `-D nosuch` | 1 | | `Unknown PCM` (same class as aplay) |
| `-t bogus` | 1 | | `Invalid test type bogus` |
| `-t wav` -c2 -l1 | 0 | 3.5 s | uses `/usr/share/sounds/alsa/Front_*.wav` |
| `-t pink` | 0 | | instant on null |
| `-s 1` | 0 | | single-speaker |
| `-m bogusmap` | 1 | | `Unable to parse channel map string: bogusmap` |
| `-r 96000` / `-F FLOAT_LE` plughw | 0 | | plug layer converts |

---

## 5. FRONTIER 5 — `PULSE_PROP_*` env (`receipts/p4-props.json`, ×3, paplay `-d r84alsa_ns` + parec side)

Witness = the stream's **pw node props** (pw-dump) vs its **pulse-side proplist**
(`pactl -f json list sink-inputs`/`source-outputs`). They differ:

| env | pw node prop | pactl proplist | verdict |
| --- | --- | --- | --- |
| `PULSE_PROP_media.role=Communication` | `media.role="Communication"` (raw) | `media.role="phone"` + `module-stream-restore.id=sink-input-by-media-role:phone` | **lands; pulse layer canonicalizes role to PA names** |
| `…=notarole` / `…=Video` | raw value | raw value | bogus roles pass verbatim |
| `PULSE_PROP_application.name=r84alsa_app` | `application.name="paplay"` | same | **DROPPED — client-set wins over env** |
| `PULSE_PROP_media.name=r84alsa_media` | `media.name=<filename>` | same | **DROPPED — pacat sets media.name from the file** |
| `PULSE_PROP_application.icon_name=x` | `application.icon-name=x` (**key normalized to `-`**) | `application.icon_name=x` | lands on node with normalized key |
| `PULSE_PROP_application.process.binary=x` | `application.process.binary="x"` | same | **lands and overrides pacat's own `pacat`** |
| `PULSE_PROP_module-stream-restore.id=x` | `module-stream-restore.id="x"` | `sink-input-by-application-name:paplay` | lands on node; **server ignores it for the restore key** |
| `PULSE_PROP_filter.want=echo-cancel` | `filter.want="echo-cancel"` | same | lands (prop only — no aec module spawned here) |
| `PULSE_PROP_zzz.invented=42` | `zzz.invented=42` (int in pw-dump) | `"42"` | **arbitrary keys land verbatim** |
| bare `PULSE_PROP=media.role=Communication` | `media.role="Communication"` | `phone` | **the suffix-less env is also parsed** |

Same both directions (parec rec side identical pattern, node `parec`,
`target.object=r84alsa_ns`). Also measured: `paplay --property=K=V` exists as a
CLI vector (not exercised — env was the frontier).

Law: **env props are a verbatim pass-through to the pw node except keys the
client sets itself** (`application.name`, `media.name` — those are the client's
own proplist members and win), and the pulse bridge renames `_`→`-` on some keys
plus canonicalizes `media.role` to PA names in the proplist view.

---

## 6. FRONTIER 6 — pactl write surface, live (`receipts/p5b-live-write.json`, `p5-pactl.json`)

Instrument: `pw-play` (tag `r84alsa_p5play`, 7 s tone amp 8192) into `r84alsa_ns`;
witness = `pw-record -P stream.capture.sink=true --target r84alsa_ns`
(continuous-writer — see §8 trap), 0.25 s windows; action at t=2.0 s. All 3/3.

### 6.1 Volume is post-gain on the monitor path — and the % scale is cubic

| action at t≈2.0 s | monitor amp after | exact law |
| --- | --- | --- |
| `set-sink-volume ns 50%` | **1024** | 8192 × 0.5³ = 1024.0 |
| `set-sink-volume <serial> 25%` | **128** | 8192 × 0.015625 = 128.0 |
| `set-sink-volume ns 150%` | **27648** | 8192 × 3.375 = 27648.0 (no clip at 32767) |
| `set-sink-volume ns 0%` then 100% | 0 → 8192 | applies ≤250 ms either direction |
| `set-sink-mute ns 1` then 0 | 0 → 8192 | mute = post-tap too (r78p law re-pinned) |
| `set-source-volume ns.monitor 50%` | **1024** | source-volume scales the monitor-source read path identically — mid-stream |

`set-sink-volume` % is **PA's cubic mapping** (`amp_ratio = (pct/100)³`), applied
to a running stream inside one 250 ms window, on sink and monitor-source alike.

### 6.2 suspend = an idle-hint, never a gate

| leg | result |
| --- | --- |
| `suspend-sink ns 1` while RUNNING/linked | rc=0, state stays **RUNNING**, pw node `running`, tone 8192 unbroken, player wall = full 7.1 s |
| `suspend-source ns.monitor 1` mid-capture | rc=0, capture keeps delivering 8192 |
| `suspend-sink ns 1` on an IDLE sink | state → **SUSPENDED** |
| `suspend-sink ns 0` after that | stays SUSPENDED — unsuspend does not force-run |
| play into a SUSPENDED sink | wakes it: RUNNING + links, player rc=0 full duration |
| `suspend-sink <ns> 2` | rc=1 `Invalid suspend specification.` |
| `suspend-sink|source no_such` / dead idx | rc=1 `Failure: No such entity` |

(NEVER-arm hazard: bare `pactl suspend` exists and suspends *everything* — not
run here; noted for the fleet.)

### 6.3 Port lattice + refusal classes (all ×3, verbatim stderr)

| arm | rc | stderr |
| --- | --- | --- |
| `set-sink-volume <ns> bogus` | 1 | `Invalid volume specification` |
| `set-sink-volume 999999 50%` / `no_such 50%` | 1 | `Failed to get sink information: No such entity` |
| `set-sink-volume <ns> 50% 60%` | 0 | per-channel pair accepted |
| `set-sink-volume <ns> -10%` | 0 | relative step accepted |
| `set-sink-volume <ns> 700%` | 0 | >100% accepted (no clamp at 100) |
| `set-source-volume no_such 50%` | 1 | `Failed to get source information: No such entity` |
| `set-sink-input-volume 999999 50%` | 1 | `Failed to get sink input information: No such entity` |
| `set-sink-port <ns(no ports)> x` | 1 | `Failure: No such entity` |
| `set-sink-port <hdmi-sink> hdmi-output-0` | 0 | sets its only port (no-op on value) |
| `set-sink-port <hdmi> bogus` / `<spdif> spdif-output` / `<Mic-src> bogus` | 1 | `Failure: No such entity` — note the USB sinks' `Active Port: "[Out] SPDIF"` is a display string, not a settable port |
| `get-sink-volume @DEFAULT_SINK@` | 0 | read-only alias OK (returned the foreign default's volume) |

---

## 7. FRONTIER 7 — `parec --monitor-stream` deep (`receipts/p6-monstream.json`, ×3)

Two players into `r84alsa_ns`: `r84alsa_ta` (L1k/R1.5k) + `r84alsa_tb` (2k).
`--latency-msec=50` used to kill parec's ~2 s buffer head (see §8 trap).

| leg | result |
| --- | --- |
| `-d ns.monitor` | mixed — `A+B` peak 16104 ≈ both tones |
| `-d ns --monitor-stream=<A>` | **only A** (1000/1500 bins, 2000 ≈ 0) — pre-mix per-stream pin |
| `--monitor-stream=<A>` (no `-d`) | rc=0, same A-only capture — `-d` not required |
| `-d no_such_r84 --monitor-stream=<A>` | rc=0, **still captures A** — `-d` ignored entirely |
| `-d ns2 --monitor-stream=<A>` (A on ns) | rc=0, captures A — **stream pin beats sink selection** |
| `--monitor-stream=0` / `999999` | rc=1 `Stream error: No such entity` + 44-B wav |
| `--monitor-stream=<a source-output serial>` | **rc=0, 44-B file, empty** — accepted, delivers nothing |
| pin A, kill A at 2.4 s | file **stops growing**, parec alive, no error, no EOS — silence/stall, not a close |
| pin A, `move-sink-input A ns2` at 2.4 s | capture **follows A** (bins keep reading A) |
| pin A, `set-sink-input-volume A 50%` at 2.4 s | tap amp **unchanged 8192** — the tap is **pre-stream-gain** |
| pin A, `set-sink-input-mute A 1` → 0 | tap drops to 0 → returns — **mute is node-level, volume is mix-level** |

**Stream-restore side law (wasn't asked, caused a real contamination, §10):**
`set-sink-input-volume` writes persist via module-stream-restore to **future**
streams of the same restore key: after a 30 % write + stream death, the next
`pw-play` sink-input lists `value_percent: 30%` (19660 = 0.3³×65536 — cubic
again) *and* its monitor-stream tap reads reduced — restored volume is baked as
**stream-node gain** (tap-visible), unlike a mid-stream write (mix-level,
tap-invisible). Two different sinks of one number.

---

## 8. Method hazards

1. **parec buffers ~1.5–2 s before first byte.** Default-latency `parec` sits at
   a 44-B header until ~2.0 s, then flushes ~64 KiB granules; a short capture
   window returns a file that is **headless in time** (my first p5 run read only
   the last ~2 s and looked flat). `--latency-msec=50` gives first write ≤0.4 s
   and continuous growth; `pw-record` writes continuously throughout. Any arm
   that reads parec's file early must set `--latency-msec`.
2. **`-D ''` diverges between aplay and arecord.** `aplay -D ''` → `Unknown PCM `
   (empty string used); `arecord -D '' -d 1` → `Unknown PCM -d` — arecord's arg
   parsing slides to the next flag. Same invocation shape, different device
   string consumed.
3. **`-D null` capture is not zeros** — periodic ~80-frame garbage bursts every
   5512 frames (peak ≈ 32500), 3/3, 668 nz rows per 1.0 s file. The `-L`
   description "generate zero samples" lies at period edges.
4. **speaker-test `-c 6` needs an ≥19 s bound** — ~3 s/channel pacing; my first
   cap read it as a hang.
5. **`arecord` node name is `alsa_capture.aplay`** — a probe grepping "arecord"
   in node names sees nothing (I missed it on first pass; the producer witness
   was empty for a measurement gap reason, not absence).
6. **`pactl list` on a shared default is unstable** — the session default moved
   under me twice this window (sibling steering). Every "lands on default" cell
   records the *measured* link target, never an assumed one.

---

## 9. Named classes added this round

| class | signature | where |
| --- | --- | --- |
| `alsa_unknown_pcm` | `Unknown PCM <x>` (pcm.c snd_pcm_open_noupdate) | -D pulse/bogus/'' both tools, speaker-test |
| `alsa_card_index` | `Cannot get card index for <x>` | hw:N/plughw:N bad card |
| `alsa_card_parse` | `cannot find card '<x>'` | named PCM + CARD=bad |
| `alsa_pcmdef_missing` | `Unable to find definition 'cards.<c>.pcm.<t>.<d>:…'` | iec958 DEV=9 |
| `alsa_unknown_param` | `Unknown parameters <k=v>` (conf.c expand) | args on argless PCM (`default:CARD=`) |
| `alsa_open_enoent` | `audio open error: No such file or directory` | absent/wrong-direction subdevice |
| `alsa_open_ebusy` | `audio open error: Device or resource busy` | PipeWire holds the PCM (live stream or lock retention) |
| `alsa_pw_conn` | `audio open error: Host is down` | pipewire:SERVER=bad |
| `alsa_pw_hwparams` | `Unable to install hw params:` | plugin capture, one of TWO state-dependent shapes |
| `alsa_tick_time` (r78's, re-seen) | `TICK_TIME: [0 0]` | plugin capture, other shape |
| `alsa_null_periodic_garbage` | `arecord -D null` → ~80 nonzero frames per 5512-frame period | null capture is not zeros |
| `pa_vol_cubic` | `set-sink|source-volume N%` applies (N/100)³ to monitored signal | pactl vol mid-stream |
| `pa_suspend_hint_only` | suspend-* on linked object: rc=0, RUNNING, flow unbroken | pactl suspend-* |
| `parec_buffer_head` | default parec: 44 B until ~2 s, then 64 KiB granules | all parec reads |
| `si_vol_sticky_restore` | `set-sink-input-volume` persists to same-key respawns via stream-restore | pactl + module-stream-restore |
| `monstream_pre_gain` | monitor-stream tap sees post-node/pre-mix data: stream-mute visible, stream-volume not | parec --monitor-stream |

---

## 10. Contention ledger (mandatory)

**Foreign state at entry:** r83dsp lane live (`r83dsp_p4_ns`, `r83dsp_p1_nsa/nsb`,
`r83dsp_p4_nsm` + running streams `r83dsp_pbX`, `input.r83dsp_p1_P8_nodename_o`);
r82 lane present (`r82ff_ns`, `r82ff_scout_ns`, and an `r82ff-play` ffmpeg
sink-input `Lavf63.1.101` appeared mid-window); `r78_def_sink_3197079`,
`r78_prop_a/b_3197079` leftover sinks. Default sink moved at least twice this
session (`r78_def_sink_3197079` ↔ `…SPDIF__sink`) — sibling steering, not mine.

**Events caused by this seat:**

1. **Plugin/default playback legs landed ~1.2 s of tag tone each** (aplay
   `-D pipewire|default`, `pipewire:NODE=bogus` fallback, PIPEWIRE_PROPS legs;
   speaker-test `-D pipewire|default` −l 1 at −S 5) on the *current* default
   sink — SPDIF for most reps, possibly the sibling's `r78_def_sink` early on.
   Bounded, disclosed; every landing is recorded as a link witness in receipts.
2. **`set-sink-input-volume` wrote through to module-stream-restore** and left
   `pw-play`'s restore volume at 30 %/50 % for a window (§7 tail) — any sibling
   `pw-play` in that window would have spawned attenuated. **Repaired and
   verified**: a fresh pw-play + `set-sink-input-volume 100 %` + respawn read
   `100 %`. Host restore state back to nominal.
3. **A duplicate `r84alsa_ns` existed briefly** (one leaked from an interrupted
   first p5 attempt, one live) — the `susp_before_play` state listing shows both
   serials; pactl name-resolution was ambiguous for ≤1 rep. Both were mine; the
   leaked one was index-verified (`sink_name=r84alsa_ns`, module 536870918) and
   unloaded. Zero `r84alsa_*` modules/sinks at exit.
4. `set-sink-port <hdmi-sink> hdmi-output-0` and `<spdif-sink> spdif-output`
   were benign writes to real sinks (one no-op set of its own port; one refused)
   — idle sinks, no port change resulted.

**Nothing was unloaded by name; no foreign module/node/stream was killed,
moved, suspended, or re-volumed; `pactl suspend` (bare), `pactl exit`,
`move-*` on foreign streams were never invoked.** At exit: no `r84alsa_*`
objects, no leftover players/recorders.

---

## 11. Verbatim-armable cells

| # | arm | expected |
| --- | --- | --- |
| C1 | `aplay -D hw:0,0 <wav>` / `-D plughw:0,0` | rc=0, ~file-duration wall, **zero new pw nodes** |
| C2 | `aplay -D default` or `-D pipewire` | rc=0; node `alsa_playback.aplay` links to **current default sink** `playback_*` |
| C3 | `aplay -D 'pipewire:NODE=<mysink>'` | rc=0; node `target.object=<mysink>`; links `<mysink>:playback_*` |
| C4 | `aplay -D 'pipewire:NODE=no_such'` | rc=0; `target.object=no_such` prop set but links go to default sink (silent fallback) |
| C5 | `aplay -D 'pipewire:ROLE=Communication'` | rc=0; node `media.role="Communication"` |
| C6 | `aplay -D 'pipewire:PERIOD_BYTES=4096'` | node `node.latency="1024/48000"` (period in frames) |
| C7 | `PIPEWIRE_NODE=<mysink>` / `PIPEWIRE_PROPS='{node.name=X}'` env + `-D pipewire` | routes to mysink / node renamed X |
| C8 | `aplay -D pulse` / `-D nosuch` | rc=1 `Unknown PCM <x>` |
| C9 | `aplay -D hw:9` / `hw:CARD=Nosuch` | rc=1 `Cannot get card index for <x>` |
| C10 | `aplay -D hw:0,9` / `iec958:CARD=Audio,DEV=1` | rc=1 `audio open error: No such file or directory` |
| C11 | `aplay -D default:CARD=Audio` | rc=1 `Unknown parameters CARD=Audio` |
| C12 | `aplay -D 'pipewire:SERVER=nonexistent'` | rc=1 `audio open error: Host is down` |
| C13 | `aplay -D hw:0,0 <wav>` while PipeWire plays on Speaker | rc=1 `Device or resource busy`; `/proc/asound/card0/pcm0p/sub0/status`=RUNNING |
| C14 | `arecord -D hw:0,0|hw:0,1 -d1 -f cd` | rc=0 file; peak ~600 (dev0) / exactly 0 (dev1) — route picks the content floor |
| C15 | `arecord -D hw:0,3` / `hw:1,3` | rc=1 ENOENT (no capture subdevice) |
| C16 | `arecord -D pipewire` / `-D default` | rc=1, no file — stderr is `TICK_TIME: [0 0]` **or** `Unable to install hw params` (state-dependent; assert rc+missing file, not the text) |
| C17 | `arecord -D 'pipewire:NODE=<source name>'` | rc=0 real capture even when C16 fails; node `alsa_capture.aplay`, `target.object=<src>` |
| C18 | `arecord -D null -d1 -f cd` | rc=0 file with **~668 nonzero frame-rows** in period-spaced bursts (not zeros) |
| C19 | `speaker-test -D null -c2 -l1 -t sine` | rc=0 in <0.5 s (unpaced) |
| C20 | `speaker-test -D 'pipewire:NODE=<mysink>' -c2 -l1` | node `alsa_playback.speaker-test` → `<mysink>:playback_*` |
| C21 | `speaker-test -D hw:0,0 -c1 -l1` | rc=1 `Channels count (1) not available for playbacks` |
| C22 | `PULSE_PROP_media.role=Communication paplay -d <ns>` | node `media.role="Communication"`; pactl proplist shows `"phone"` + restore id `sink-input-by-media-role:phone` |
| C23 | `PULSE_PROP_zzz.invented=42` / `PULSE_PROP_application.process.binary=x` | land verbatim on node (invented lands as int 42 in pw-dump) |
| C24 | `PULSE_PROP_application.name=x` / `PULSE_PROP_media.name=x` | **dropped** — client-set values win |
| C25 | `pactl set-sink-volume <ns> 50%` mid-play, capture `<ns>.monitor` | monitor amp ×0.125 exactly (cubic); `150%`→×3.375; `25%`→×0.015625; ≤250 ms |
| C26 | `pactl set-source-volume <ns>.monitor 50%` during capture | captured amp ×0.125 — source volume applies mid-stream |
| C27 | `pactl suspend-sink <ns> 1` mid-play | rc=0; sink stays RUNNING; monitor tone unbroken; on an IDLE sink state→SUSPENDED; play into suspended sink wakes it |
| C28 | `pactl set-sink-volume <ns> bogus` / `suspend-sink <ns> 2` | rc=1 `Invalid volume specification` / `Invalid suspend specification.` |
| C29 | `parec -d <ns> --monitor-stream=<sink-input idx>` while two streams play | capture carries only the pinned stream's content (FFT separation) |
| C30 | `parec -d no_such --monitor-stream=<valid idx>` | rc=0, captures anyway — `-d` ignored under the pin |
| C31 | `parec --monitor-stream=<source-output idx>` | rc=0, 44-B empty wav |
| C32 | `parec --monitor-stream=<A>` + `pactl move-sink-input A <ns2>` | capture follows A across sinks |
| C33 | `parec --monitor-stream=<A>` + kill A | file stops growing; parec stays alive; no error/EOS |
| C34 | `parec --monitor-stream=<A>` + `set-sink-input-volume A 50%` mid-run | tap amp unchanged (pre-gain); `set-sink-input-mute A 1` → tap reads 0 |
| C35 | `set-sink-input-volume <A> 30%`, let A die, respawn same client | new sink-input reads `value_percent: 30%` — stream-restore stickiness |

---

## 12. Falsification list

1. **"NODE= writes target.object"** — a `pipewire:NODE=` leg whose node lacks
   `target.object` or whose `node.target` is set instead.
2. **"silent fallback on NODE= miss"** — a `pipewire:NODE=bogus` leg that errors
   rc≠0 or links to anything but the current default sink.
3. **"plugin capture needs explicit NODE="** — a host state where bare
   `-D pipewire` capture works while `NODE=<source>` fails; or the reverse
   asymmetry reproduced.
4. **"the two plugin-capture refusal texts are state-dependent"** — a state
   where one of the two texts reliably maps to a *named* precondition (e.g.
   TICK_TIME iff a specific sibling node exists). Currently unattributed.
5. **"volume % is cubic"** — a `set-sink-volume <ns> N%` whose monitor amp is
   not within ~2 % of `8192·(N/100)³` — i.e. a linear or dB mapping.
6. **"suspend is hint-only"** — a `suspend-sink` on a *linked* sink that
   actually drops the stream's audio or flips state to SUSPENDED.
7. **"monitor-stream is pre-gain, post-node"** — a leg where
   `set-sink-input-volume` mid-run *does* change the tap amp, or where
   `set-sink-input-mute` does *not* zero it.
8. **"monitor-stream ignores -d"** — a `-d <other> --monitor-stream=<idx>` leg
   whose content is not the pinned stream's.
9. **"env props lose to client proplist"** — a `PULSE_PROP_application.name=x`
   that overrides `paplay`'s own application.name on the node.
10. **"null capture ≠ zeros"** — an `arecord -D null` that is all-zeros, or
    whose burst period isn't the ~5512-frame spacing (period-dependent law).
11. **"source-output index → 44-B accept"** — a `--monitor-stream=<source-output>`
    that actually captures or refuses.

---

## 13. Remaining unknowns (honest edges)

- **Which host state flips the plugin-capture refusal text** (TICK_TIME vs
  hw-params vs r78p's success) — unattributed; candidate witnesses: whether the
  plugin's default-source autoconnect produced a node at all, and sibling-held
  device state. Not re-measurable on demand.
- **`EXCLUSIVE=1` semantics** — accepted, links normally; whether it locks the
  *node* or the *PCM* unmeasured (needs a second opener racing it).
- **`set-sink-volume` while the sink is SUSPENDED** — applied-to-prop vs
  deferred unmeasured.
- **`speaker-test` channel-map `-m` legal values** — only the bogus-map refusal
  is pinned.
- **`parec --monitor-stream` + `--fix-*`/`--channels` interaction** —
  r78's fix-laws were measured on sink monitors, not per-stream taps.
- **`paplay --property=` / `--stream-name=`** — exist as CLI prop vectors;
  env-vs-CLI precedence on the same key unmeasured.
- **`pactl send-message`/`subscribe`** — pipewire-pulse extras; out of scope.
- **monitor-stream tap vs `channel-volumes` props** on the stream node — the
  respawn-visible gain is inferred as node-baked from the tap's post-restore
  reduction, not directly diffed.

---

## 14. Receipts index

`corpus/live/r84-scout/receipts/`:
`p1-aplay.json` (47 legs×3, device lattice + plugin args + env),
`p1b-plugin-args.json` (channel-match/refusal + prop landing),
`p2-arecord.json` (22 capture legs×3 + peaks),
`p2b-plugin-capture.json` + `p2c-node-capture.json` (state-flip pair + NODE=
revival), `p2d-ebusy.json` (contention refusals), `p3-speaker.json`,
`p4-props.json` (env lattice, node vs proplist), `p5-pactl.json` (refusal
classes + suspend-before-play), `p5b-live-write.json` (windowed cubic law +
suspend/mute legs), `p6-monstream.json` (pin/move/kill/gain legs).
Per-leg `cmd`/`stdout`/`stderr`/`result.json` under `runs/<probe>/<leg>/rep*/`.
Baseline board `runs/00-baseline.json`. Scratch ~5.0 MB, all scratch-side.
