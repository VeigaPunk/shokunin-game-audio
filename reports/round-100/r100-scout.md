# R100 scout — capstone residue verdict: ranked remaining surfaces, `sofa`/`spatializer` pinned

**Seat:** scout (leaf; frozen `probeParent` — exactly one read-only `ufo-labrat`
child, advisory, folded §6). **Lane:** `/home/vgpnk/Projects/shokunin/audio-shokunin`.
**Host:** `plazir27`, PipeWire **1.6.8**, WirePlumber 0.5.17-1, libpulse 17.0-98-gb096,
Python 3.14.7, loadavg **86.5** at entry (sibling seats live).
**HEAD at entry/exit:** `58adad60` (r97 scout) — zero tracked writes, no commits.
**Read set:** `LOG.md` (all 1379 lines), scouts **r62–r98** (r62–r70 file/transport,
r71–r82 decoder/consumer, r83–r90 CLI/control planes, r91–r98 mechanism/DSP/API),
the r83–r90 boundary reports, `SCORECARD.md`, `PROVINCE.md`, wave-w22 task cards.
**Scratch:** `corpus/live/r100-scout/` (25 files, 7.13 MB, `manifest.sha256` +
`RECEIPTS.md`). **r99 is in flight** (`corpus/live/r99-scout/` has live RTP
module sources; no r99 report yet) — its surface is excluded from the ranking.

---

## 0. Headline

1. **The largest residue is not a surface — it is unlanded work.** Sixteen
   consecutive scout rounds (**r83–r98**) produced author-ready rows and *none*
   are armed: `corpus/fixtures/measure_audio.py` contains **zero** `r83+` probe
   flags; the last author commit is `aa03c347` (r82). The r82 round is also
   unclosed (wave-B reports landed, simplifier patch queued, no fold, no
   report-last; LOG/SCORECARD end at r81).
2. **Of the genuinely unmeasured surfaces, one is both large and proven
   pinnable headless: the `sofa`/`spatializer` HRTF node** — the *only* one of
   the five filter-graph plugin types never measured (builtin r92, ebur128 r93,
   ladspa/lv2 absent-class r92, **sofa load-only**). This seat pinned it: a real
   shipped HRIR file at graph rate 44100 gives **azimuth-dependent binaural
   output** — ILD 0.000 dB (az 0) → **+4.611/+4.612/+4.612 dB** (az 90) →
   **−4.612 dB ×3** (az 270, exact mirror) → 0.000 dB with a **−1.45 dB**
   front/back spectral offset (az 180) — 3 reps per cell, analysis-stable.
3. The no-config spatializer is **not** a silent pass-through: it is a hard
   **graph-start error (−22)** plus pure silence (r92 `[?]3` answered). A graph
   rate *mismatch* (48000 vs the file's 44100) does **not** silence it: the IR
   length scales **512 → 558** and ILD survives (+4.616 dB, ×3).
4. Everything else remaining is either narrow residue of an already-measured
   surface, or **vacuous on this host** (bluetooth audio flow, device-profile
   switching, foreign-object mutation) — §2 ranks all of it.

---

## 1. How the residue was computed

For every scout r62–r98 the report's own "remaining unknowns" / "named coverage"
/ "not measured" sections were harvested and de-duplicated into **surfaces**
(not individual `[?]` items). A surface is called **pinnable** only if a
headless, bounded, self-cleaning probe can arm it on this host with
seat-owned object names and no operator mutation; **vacuous** if the missing
evidence is structurally absent here (no hardware, no second server, or the
probe itself would mutate the operator's session).

Two levels of residue are reported separately because they have different
owners: **process residue** (unlanded rows, unclosed rounds — §2a) and
**surface residue** (§2b). The ranking weighs: unmeasured-ness × pinnability ×
province value (SFX/soundtrack content, duration/loudness/spectral/loop-seam)
× named-gap closure × leg budget.

---

## 2a. Process residue (owner: operator/orchestrator, not a scout)

| # | residue | evidence | state |
| --- | --- | --- | --- |
| P1 | **r83–r98 scout rows unlanded** (16 rounds: pw-cat props r83, aplay `-D` r84, sndfile-info r85, pw-cli r86, pw-cat `--target`/midi r87, bluez r88, pw-profiler r89, WP settings/pw-link/v4l2 r90, gst-freeze mechanism r91, filter-chain r92, ebur128 r93, SoX_ng r94, JACK r95, PA-native r96, WP policy r97, pw_stream r98) | `grep -o 'probe-.*r\(8[3-9]\|9[0-9]\)' corpus/fixtures/measure_audio.py` → **empty**; `git log --oneline \| grep -Ei 'r(8[3-9]\|9[0-9]) author'` → **empty**; last author commit `aa03c347` | **pending** |
| P2 | **r82 round unclosed** — author `aa03c347` + all wave-B reports landed (verifier VERIFIED 76/76 ×2; simplifier −25 lines queued; scribe ADJ-1..12) | `git log`; no r82 fold/report-last; `SCORECARD.md` and `LOG.md` end at r81 | **pending** |
| P3 | **r99 (network transport) in flight** — RTP/ROC/zeroconf module sources fetched, no report | `corpus/live/r99-scout/sources/module-rtp*.c` (live dirs 17:34) | **in flight** |

## 2b. Ranked remaining surfaces (pinnable vs vacuous)

| # | surface | state before r100 | pinnable on this host? | evidence / why | verdict |
| --- | --- | --- | --- | --- | --- |
| **1** | **`sofa`/`spatializer` HRTF binaural node** (type=sofa, label=spatializer; Azimuth/Elevation/Radius; shipped SOFA HRIR) | **unmeasured** — load-only 3/3 (r92 §5.2/§5.4); no-config behaviour `[?]`; no SOFA file ever fed | **YES — proven this seat** | 17 bounded legs, 0 residue; ILD law ×3 (§3); plugin + man-page contract; real HRIR at `/usr/share/libmysofa/MIT_KEMAR_normal_pinna.sofa` | **PIN NOW** |
| 2 | **Control/volume lattice** — `filter.graph.capture.volumes`/`playback.volumes` (notify port → stream volume), stream volume/mute props, live control-port change on a running filter node | **unmeasured**, named 4× | **YES** | man page §Volumes + §"changed at runtime"; r98's harness already calls params; r92 §3.1 proved the control table is readable and clamp-lawed | **PIN (next author)** |
| 3 | **`filter.smart` / `node.filter-graph.rules` `create-filter-graph` policy path** (policy-created DSP graphs) | **unmeasured** (r92 `[?]8`, r97 `[?]6`) | **YES**, with the r97 §2 private-instance shape (env matrix measured) | implementation on disk (`/usr/share/wireplumber/scripts/node/filter-graph.lua:116,126`), official example shipped | **PIN (private pair)** |
| 4 | **ebur128 residue** — LRA on a dynamic program, True-Peak oversampling semantics, `label=null` failure mechanism, installed-binary vs fetched-tag revision | partially measured (r93, 42+ legs) | **YES** | r93 harness + ffmpeg `ebur128` cross-witness exist | **PIN (narrow)** |
| 5 | **`pw_stream` C API residue** — `return_buffer`, `emit_event`, `set_control`, `new_simple`, `DRIVER`/freewheel/lazy | partially measured (r98 named gaps §6.5) | **YES** | r98's own C harness, self-cleaning | **PIN (narrow)** |
| 6 | **MIDI/UMP deep** — UMP mode, SysEx/midi-clip, event-timing fidelity, midi-bridge targetability, BLE-MIDI end-to-end | partially measured (r78, r83 §3, r87 §5) | **YES** (software-only; ALSA seq on host) | r83's `pw-mididump`/`pw-midiplay` harness; r78 midi frontier | **PIN (narrow)** |
| 7 | **`wpexec` Lua namespace** — a fragment-added `script/lua` never loads; `Settings` unbound; rc 70 with no location | partially measured (r92 `[?]2`, r97 `[?]1`, §5.3) | **YES** (private pair) | r97 arming shape + `settings-instance` anchor (`wireplumber.conf:282-297`) | **PIN (narrow)** |
| 8 | **Shipped filter-chain config matrix** — 5/12 configs unmeasured (upmix-5.1, hesuvi 7.1, source-duplicate-FL + 2 LADSPA-dead); the hesuvi IR dir is missing | partially (r92 §7.4) | **YES** with a verbatim-preserving transform (or `pipewire -c filter-chain.conf`, which r92 refused on the shared host) | r92 §7.4 records the exact transform defect | **FOLD into #1's round** |
| 9 | **Module-* family remainder** — echo-cancel, remap-source against a *running* default source, combine-stream, pulse-tunnel positive branch | partially (r80 `[?]1`, r90 named coverage) | **PARTIAL** — tunnel positive branch needs a second server (vacuous here); the rest pinnable | r80 §11, r90 §3 | **PARTIAL** |
| 10 | **pw-top `.log`/`.art` follower-column semantics** (~200-column tail undecoded), `cpu_load0/1/2` windows, `followerClock` emission condition | partially (r89 residue; xrun injection closed by r98) | **YES** | r89's gnuplot-title anchors | **LOW VALUE** |
| 11 | **ALSA-direct device paths** — dmix/plug route identity, `sysdefault` EINTR finalize, direct hw param negotiation | partially (r77, r82 §6, r84) | **PARTIAL** (hardware/shared-host bound; `null` PCM only) | r77 §10, r84 | **LOW VALUE** |
| 12 | **File-format edges untested by r85** — tag/metadata writes, RF64/W64/CAF/Opus paths | mostly measured (r62–r74, r85, r85-boundary, r94) | **YES** | thin residue only | **LOW RESIDUE** |
| 13 | **Device-profile policy** — `policy.device.profile` hooks (8), route priorities >15000, autoswitch | **unmeasured** (r97 `[?]5`) | **NO on this host** — switching profiles mutates the operator's 3 ALSA cards (`pactl list cards`: hdmi-stereo/-extra1, USB); r97 refused a second daemon on host PCMs | r97 §2.5/`[?]5`; `pactl list cards short` (3 cards, live profiles) | **VACUOUS (shared host)** |
| 14 | **Bluetooth/bluez audio flow** — A2DP↔HFP switch, codec negotiation, HW volume, latency, BLE-MIDI end-to-end | unmeasured, structurally | **NO** — no bluez audio device exists; `bluez5.codecs` is not live (r88) | r88 §6 named coverage | **VACUOUS (no device)** |
| 15 | **Foreign-object mutation classes** — `destroy`/`send-command`/`permissions`-write/`move-sink-input` on foreign nodes | deliberately unexercised (r87 §12) | **NO** — destructive under live sibling seats | r87 §12 | **VACUOUS (needs quiesced host)** |
| — | **Network transport** (RTP/ROC/zeroconf/tunnel) | **claimed by r99 (in flight)** | — | r99 dirs live | **EXCLUDED** |

**Worthiest = #1**, for four reasons: it is a whole plugin *type* (not residue of
one), it produces the province's **first spatial/stereo output path** (every
canonical fixture is mono), it is **proven pinnable with zero contention**
(file-local, ~8 s/leg), and it closes three named gaps at once (r92 `[?]3`,
§5.4, and the §5.3 silent-IR class). #2 is the runner-up if the next round wants
a control-plane move instead.

---

## 3. The pinned surface — measurements (verbatim)

**Arming shape** (identical to r92 §2.4, plus a stereo playback stream; every
link rc 0 on `tries: 1`):

```
pactl load-module module-null-sink sink_name=r100s_in channels=1 rate=<rate> \
      sink_properties=state.restore-props=false
pw-cli load-module libpipewire-module-filter-chain \
  node.description=r100s_sofa,filter.graph={nodes=[{type=sofa,name=s0,label=spatializer,
    config={filename=/usr/share/libmysofa/MIT_KEMAR_normal_pinna.sofa},
    control={Azimuth=<az>,Elevation=0.0,Radius=1.0}}]},
  audio.channels=1,audio.position=[MONO],audio.rate=<rate>,
  capture.props={node.name=r100s_sofa_in,node.autoconnect=false,media.class=Audio/Sink},
  playback.props={node.name=r100s_sofa_out,node.autoconnect=false,audio.channels=2,
    audio.position=[FL,FR]}
pw-link r100s_in:monitor_MONO r100s_sofa_in:playback_MONO
pw-record --channels 2 -P node.name=r100s_rec -P node.autoconnect=false cap.wav   # post tap
pw-link r100s_sofa_out:output_FL r100s_rec:input_FL ; … output_FR → input_FR
pw-play --target r100s_in tone.wav        # 440 Hz, amp 0.5, 1.6 s, mono
```

| pin | measured | reps | receipt |
| --- | --- | --- | --- |
| **Ports/shape** | capture stream mono (`playback_MONO`), playback stream stereo (`output_FL`/`output_FR`); graph 1-in/2-out; module loads, both nodes publish | 12 legs | `runs/sofa_*.json` |
| **No config** (`{type=sofa,name=s0,label=spatializer}`) | load OK, then at activation: `[E] plugin_sofa.c:60 spatializer: no config was given` → `[E] stream.c:429 error (-22) can't start graph: Invalid argument` → module error line; capture **pure silence** (`rms 0.0`, peak 0.0) | 1 (r92 `[?]3`) | `sofa_gate.json` |
| **Real SOFA @44100** | `[I] plugin_sofa.c:222 using n_samples:512 256:4096 blocksize gain:1.000000 sofa:/usr/share/libmysofa/MIT_KEMAR_normal_pinna.sofa`; `[I] plugin_sofa.c:268 making spatializer with 0.000000 0.000000 1.000000` | 3 | `sofa_azimuth.json` |
| **Rate mismatch @48000** | **not refused**: instantiation succeeds, `n_samples:558` (= 512·48000/44100 = 557.3 → 558), output non-silent (rms 0.12149002/ch, az default 0); the plugin's `Only the same sampling rate supported` string is **not reached on this path** | 1 (+3 az90) | `sofa_gate.json`, `sofa_extra.json` |
| **Azimuth law @44100** | az 0 → ILD **0.000** (L=R=0.11650363); az 90 → **+4.611 / +4.612 / +4.612 dB** (L 0.16277655/0.16278089/0.162781, R 0.09572808/0.09572184/0.09572185); az 270 → **−4.612 dB ×3**, an *exact mirror* of az 90; az 180 → ILD **0.000** (0.09856998/0.09856943) | 3 each | `sofa_azimuth.json`, `sofa_extra.json` |
| **Front/back is spectral, not ILD** | az 180 vs az 0 at 440 Hz: **−1.4517 dB** (rms −1.4519 dB), both channels equal | 2 | `sofa_extra.json` |
| **Azimuth survives the rate mismatch** | az 90 @48000 → ILD **+4.616 dB ×3** (L 0.16979696, R 0.09979693; tone 0.24012915/0.14113418) | 3 | `sofa_extra.json` |
| **Not a pass-through** | az 0 output rms 0.11650363 vs the stimulus's 0.35355339 → **−9.642 dB**; the node is a real filter, not a copy | 3 | `sofa_azimuth.json` |
| **Teardown** | every stage ends `final sweep: {'clean': True}` (no `r100s` nodes, modules or procs); unloads verified by module index + name | all | every receipt |

Analysis-level stability: per-channel rms and 440 Hz Goertzel magnitudes are
identical to **≤2e-5 relative** across reps; capture **WAV bytes are not
identical** (pw-record start offset differs — `win_offset` in each row).

---

## 4. Author-ready rows — proposed `--probe-sofa-r100` entry

Every row is namespace-safe (`r100s_*`), silence-only until fed, and needs one
private mono null sink (`rate=<leg>`, `state.restore-props=false`) unloaded by
verified index. Namespace, teardown and `node.autoconnect=false` per r92 §2.4.

1. **Arm/ports row** — module loads; capture stream mono, playback stream
   stereo (`output_FL`/`output_FR`); graph 1-in/2-out with inputs/outputs
   omitted; all links rc 0 on `tries: 1`. (`sofa_azimuth.json` all legs)
2. **No-config row (silent-failure class)** — `{type=sofa,name=s0,label=spatializer}`
   → load OK, activation **error −22** (`spatializer: no config was given`),
   capture all-zero. Gate on `error` + zero rms, never on load rc.
   (`sofa_gate.json` `noconfig_48k`)
3. **Instantiate row** — real file @44100 → `using n_samples:512 256:4096`,
   `making spatializer with <az> <el> <radius>`; pin the two log lines.
   (`sofa_azimuth.json`)
4. **Rate-mismatch row** — graph 48000 vs file 44100 → instantiation succeeds,
   `n_samples:558`, output non-silent; record that
   `Only the same sampling rate supported` is *not* emitted here.
   (`sofa_gate.json` `sofa_48k`, `sofa_extra.json`)
5. **Azimuth ladder row** — az ∈ {0, 90, 180, 270} → ILD 0.000 / +4.611…4.612 /
   0.000 / −4.612 dB; assert the 90↔270 mirror to ≤1e-3 dB.
   (`sofa_azimuth.json`, `sofa_extra.json`)
6. **Front/back spectral row** — az 180 vs az 0, 440 Hz component **−1.45 dB**
   with equal L/R. (`sofa_extra.json`)
7. **Rate-mismatch azimuth row** — az 90 @48000 → **+4.616 dB ×3**.
   (`sofa_extra.json`)
8. **IR/latency row** *(proposed, unmeasured)* — single-sample delta through the
   spatializer at 44100: expect a 512-tap HRIR convolution; pin first-nonzero
   and the plugin's `latency` config key. (r92 §4 convolver method)
9. **Runtime azimuth row** *(proposed, unmeasured — r92 `[?]9`)* — change
   `Azimuth` on the live node (control port / `pw-cli set-param`) and measure
   the ILD step without a reload; man page says "can be changed at runtime".
10. **Elevation/Radius row** *(proposed, unmeasured)* — elevation ladder and
    `Radius` 0…100; expect ILD symmetry preserved, spectrum changes.
11. **Second-file row** *(proposed, unmeasured)* — `/usr/share/libmysofa/default.sofa`:
    **first hash-compare it with `MIT_KEMAR_normal_pinna.sofa`** (the labrat
    flagged this as untested); if identical, pin the duplication instead of
    pretending it is a second corpus.
12. **Crash-class / cleanup row (negative control)** — after the −22 leg,
    `pw-cli` can die (`BrokenPipeError` on unload, r92 §2.7 class). Exclude
    from pass/fail gating; assert teardown by verified index instead.

---

## 5. Falsification list — what an arm must NOT claim

- **Not perceptual/spatial-audio quality.** ILD and a 440 Hz magnitude delta
  are *energy proxies*; they do not establish HRTF accuracy, externalization,
  or "3D audio" quality. No listening claim.
- **Not a general spatializer law.** Bounded to PipeWire 1.6.8 +
  `libspa-filter-graph-plugin-sofa` + this one HRIR file on this host.
- **No SOFA-data rights claim.** The file's own metadata says *"No license
  provided, ask the author for permission"* — it is used as a test fixture only;
  clearance stays with the operator.
- **Do not read the plugin's `Only the same sampling rate supported` string as
  dead** — this path does not reach it; another config path might.
- **Do not call the no-config node a pass-through** — it is a hard graph-start
  error (−22) plus silence.
- **Do not key anything on the capture file's rate** — `pw-record` clocked at
  the host rate (**48000**) even when the graph ran at 44100 (labrat flag, §6);
  the ILD is rate-insensitive but the byte stream is not the graph's rate.
- **Analysis-level stability only** — WAV bytes differ across reps; the pins are
  rms/Goertzel values to ≤2e-5 relative, not sha-identical captures.
- **No wall-time claims** — loadavg 86.5 during measurement; content fields are
  load-independent, wall times are not.
- **Never gate on the crash-class row** (r92 §2.7 `pwcli_eof_abort`; this seat
  re-hit it as `BrokenPipeError` on the −22 leg's unload).

---

## 6. Labrat fold (frozen `probeParent` — exactly one child, advisory)

One read-only `ufo-labrat` was dispatched with hypothesis H (azimuth-dependent
binaural output; az0 identity; 90/270 mirror; rate-mismatch non-silence with
n_samples 512→558) and four falsifier attacks. **Toolset limit disclosed: read/
grep/glob only — no exec**, so it could not arm PipeWire objects. It performed
an artifact-level falsification on this seat's receipts and returned
**SUPPORTS** with no contradiction:

- **Pass-through attack (analytic, and it strengthens the claim):** stimulus
  440 Hz amp 0.5 → expected copy rms 0.3536; measured az0 rms 0.1165 (−9.6 dB)
  and tone magnitude 0.165 vs ≈0.5 input → the output is filtered, not copied.
- **Rig-artifact attack (analytic):** a static rig asymmetry cannot produce
  az90/az270 as *exact numerical mirrors* (az270 L = az90 R = 0.09572184 to the
  8th decimal; az270 R = az90 L = 0.16278089/0.162781) — the asymmetry follows
  the `Azimuth=` token, not the port order. Residual risk: low, but the
  physical channel-swap leg was **not run**.
- **Untested by the child (recorded, not hidden):** (i) channel-swap
  measurement; (ii) byte-comparison of `default.sofa` vs
  `MIT_KEMAR_normal_pinna.sofa`; (iii) whether az90 ILD survives the 48k
  mismatch — *this seat's `extra` stage, launched after the child read the
  receipts, has since closed (iii): +4.616 dB ×3*.
- **Child-caught parent gap (folded):** every capture file reports rate 48000,
  including the 44100-graph legs — `pw-record` clocked at the host rate. The
  parent's analysis used the file's own rate, so the ILD numbers stand; the
  disclosure is now in §5.
- Child created no artifacts and touched no PipeWire object.

---

## 7. Harness disclosures (recorded, not hidden)

1. **Defect 1 (fixed):** the first rig version used a second null sink as the
   post-tap; `pw-link … r100s_rec:input_FL` fails (`No such file or directory`,
   12 tries) because a null sink has no `input_*` ports. Replaced with a
   `pw-record` stream (`input_FL`/`input_FR`), the r92 shape.
2. **Defect 2 (fixed):** the unload call was unguarded; after the −22 leg
   `pw-cli` died → `BrokenPipeError` killed the stage before `save()`. Now
   caught (`unload: {error: …}`), a leg can no longer kill a stage; the extra
   stage was re-run and its rows are in `runs/sofa_extra.json`.
3. **Sibling harness reuse:** `probes/sofa_probe.py` imports the r92-scout
   `pwlib` **read-only** (no import of `corpus/fixtures/measure_audio.py`, which
   is tracked and sibling-owned).
4. **Contention:** loadavg 86.5; no cross-seat object was touched; every leg's
   `pre_sweep`/`post_sweep` is in the receipts and all stages ended
   `clean: True`.
5. **A stray `Segmentation fault` occurred once in this seat's own ad-hoc
   `ctypes` call into `libmysofa_getfilter_float` (wrong signature, exploratory,
   not part of the probe) — disclosed; the shipped probe does not use ctypes.**

---

## 8. Artifacts & provenance

- Report: `reports/round-100/r100-scout.md` (this file; **untracked**, no commit).
- Scratch: `corpus/live/r100-scout/` — `probes/sofa_probe.py`,
  `runs/sofa_{gate,azimuth,extra}.json`, `receipts/sofa_probe_*.json`,
  `scratch/cap_*.wav` + stimuli, `manifest.sha256`, `RECEIPTS.md` (25 files).
- External read-only references: `/usr/bin/mysofa2json` (SOFA header),
  `man 7 libpipewire-module-filter-chain` (§SOFA FILTERS, §Volumes),
  `strings libspa-filter-graph-plugin-sofa.so`, r92/r93/r97/r98 scout reports.
- **Remaining risks:** the ILD law is a two-channel energy proxy for one HRIR
  file at one elevation/radius; runtime azimuth control, elevation/radius
  ladders, IR/latency and the second SOFA file are **proposed, not measured**;
  r83–r98 author rows remain unlanded (P1) and r82/r99 remain open (P2/P3).

*scout leaf — measured, not judged.*
