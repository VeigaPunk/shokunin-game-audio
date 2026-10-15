# R83 boundary — edge stress of the r83 scout pins under load

**Seat: BOUNDARY (executor-class, leaf).** Host `plazir27`, repo
`~/Projects/shokunin/audio-shokunin` @ HEAD **`2333fac`** (`r82 baseline:
86/136 x2 frozen…`). Window **2026-10-15 ~16:34–16:53 UTC−3**. Toolchain:
PipeWire **1.6.8** (pw-loopback/pw-cat/pw-record/pw-mididump/pw-midiplay/
pw-link/pw-cli/pw-dump), pactl **17.0-98-gb096**, numpy **2.5.3**, 32 cores.
Everything under `corpus/live/r83-boundary/` (own harness `r83b_probe.py` +
`r83b_run.py` + `r83b_onsets.py`, own tones, own FFT/Goertzel classifiers,
`receipts/` ×22, `runs/**`, `manifest.json`). **No tracked-file edits, no
commits, no `set-default-*`, no foreign object touched except the disclosed
Midi Through pins (§8).** All seat objects `r83b_*`; the only modules loaded
were five `module-null-sink` (`r83b_nsa`, `r83b_nsb`, `r83b_nsm` mono,
`r83b_ns48`, `r83b_ns44` rate=44100), each unloaded by the index returned by
`load-module` re-verified against `module-null-sink` + `sink_name=` (§9).

Host state was *not* quiet: foreign seats held loadavg **12–122 / 32 cores**
for the whole window (§8). Every decisive cell was re-run with 16 seat-owned
CPU hogs on top (loadavg 47–117) and the two artifact cells are byte-stable
across quiet and loaded reps.

The single frozen-`probeParent` labrat was dispatched once, read-only, to
audit the scout's own receipt corpus; its findings are folded into §4 and its
net result was advisory only (no edits, no side effects).

---

## 0. Verdict table — the scout's own falsification list (§7 of r83-scout.md)

| # | scout pin | verdict | sharpest measured fact |
| --- | --- | --- | --- |
| 1 | all five `-i`/`-o` prop syntax forms land verbatim | **CONFIRMED** | S1–S5 replayed: `media.name`/`bogus.prop` both land on the respective node in space, comma, brace, quoted-brace and JSON-colon forms |
| 2 | `-i ''`/`-o ''` SIGSEGV 6/6 | **CONFIRMED + generalized** | 8/8 quiet (3 `-i`, 3 `-o`, 2 direct spawn) + 3/3 under 16 hogs, rc **-11** (shell 139), `timeout: the monitored command dumped core`; **`-i ' '` (whitespace-only) also SIGSEGVs**; **`pw-cat -P ''` and `pw-record -P ''` SIGSEGV too** |
| 3 | malformed `}{ garbage` silently drops the whole value | **CONFIRMED for that input / FALSIFIED as a general law** | `}{`, `[1,2`, `{ }`, `null`, `"str"`, `a=b,` drop silently; but `a=b }{ c=d`, `{ bad`, `media.name=` → **rc=255**, `error: syntax error in --capture-props: …`, **zero nodes spawned** |
| 4 | `audio.position`/`audio.channels`/`channelmap.map` props do not remix the copy | **CONFIRMED** (props) / **author-ready A3 cell wrong** | C1/C2/C5/C6 all stereo passthrough (amp 8191.3/8191.4); but the §6 A3 cell `-m '[ MONO ]'` alone gives a **time-varying asymmetric mix** (1 s window: 4095.6/4095.6; later: 1551.9@1k / 2046.9@1.5k) — only `-c 1 -m '[ MONO ]'` is the clean stable `0.5·(L+R)` (4095.6/4095.6, 3 windows) |
| 5 | `stream.dont-remix` effective; `node.dont-remix`/`channelmix.*` inert | **CONFIRMED** | M2 `[8192,0]` and D3 FL-only 8191.3 both reproduce (also under 16 hogs); M1/M3/M4/W1/W2/W3/W4 land verbatim with zero link/content change |
| 6 | upmix full-amp; downmix `0.5·(L+R)` (amp 4095.9, peak 7802) | **CONFIRMED** | M0 8191.3/8191.3; D0 4095.6@1k **and** @1.5k, peak 7801 |
| 7 | `resample.disable=true` + 44.1k→48k → all-zero monitor | **CONFIRMED** | `all_zero=true`, 144000/144000 frames exact 0, links live, stderr empty; 2/2 under 16 hogs; **matched-rate + disable still carries tone** (mismatch required); `disable=false` + mismatch carries tone |
| 8 | `resample.peaks=true` + mismatch → **half-wave rectified**, fundamental survives | **FALSIFIED in shape/spectrum; confirmed in mean/zeroing/determinism** | the artifact is **full-wave `\|x\|`** (exact-zero fraction 8.3 % ≈ 1/12, no run >2, `\|sin\|` V at zero crossings) with the **fundamental destroyed**: their own `PK44_1.wav` gives amp@1k=**0.9** vs 4095.5 clean and amp@2k=**1586** (octave shift, not "no detune"); mean +4383.3/+4382.4, gap histogram 12×1187 / 13×549 and 2/2 determinism all reproduce exactly (PK44_1/2 byte-identical, sha256 `2ba24ad4…`) |
| 9 | `-l` int-ms×48, `-d` float-s×16000, `-l` beats `-d` both orders | **CONFIRMED + one new mode** | 240/48000, 96/48000 (2.5→2), 480000/48000, 4000/48000, 16000/48000, LD/DL=240/48000; `-l 0`/`abc`/`-d -1`/`abc`/`0` absent; **`-l -5` → `4294967056/48000`** (uint32 wrap) |
| 10 | `-d 1.0` adds no measurable onset delay (~43 ms ≈ control) | **FALSIFIED** | timestamped interleaved transport: control **0.103–0.127 s** vs `-d 1.0` **1.103–1.148 s** (5/5, incl. under load); scaling `-d 0.25` → +0.25 s, `-d 1.0` → +1.0 s; `-l 100`/`-l 1000` add nothing (prop-only) |
| 11 | midi play/dump have no name/auto target resolution; manual pins work both ways | **CONFIRMED** | auto/`Midi-Bridge`/bogus all rc=1 `no target node available`; `--target 0` publishes `Stream/Output/Midi`; manual pins: mididump printed `Note On (channel 1): note C4, velocity 96`, aseqdump `14:0 Note on 0, note 60, velocity 96` |
| 12 | `pw-filter` absent | **CONFIRMED** | `which` rc=1, `man -w` no entry, `find /usr -name 'pw-filter*'` empty, no bin in `pacman -Ql pipewire-audio`, `libspa-filter-graph-plugin-{builtin,ebur128,ladspa,lv2,sofa}.so` present |
| 13 | `-C`/`-P` resolve `object.serial` | **CONFIRMED** | `-C 87120 -P 87129` → links land on `r83b_nsa`/`r83b_nsb`, `target.object` = the serials |

**Headline score: 10 pins confirmed, 2 falsified (`-d` delay; peaks waveform
class), 1 over-generalized (malformed props), 1 author-ready cell corrected
(`-m '[ MONO ]'` needs `-c 1`), plus 6 unstated modes found (§7).**

---

## 1. Claims 1–3 — the pw-loopback arg lattice (`receipts/s1-args.json`, `s1x-ext*.json`, `s1y-o-props.json`)

Route on every leg: `-C r83b_nsa -i stream.capture.sink=true -P r83b_nsb`
(both probe-owned). "Lands" = present in the pw-dump node props.

**Syntax forms.** S1 `media.name=SPACEV bogus.prop=42` → both land on
`input.*`; S2 `{ media.name = BRACEV bogus.prop = 42 }` → both; S3
`{ "media.name" = "BRACEQ" "bogus.prop" = "42" }` → both; S4
`{ "media.name": "COLONV" }` → lands; S5 comma form → both. **Claim 1
CONFIRMED.** One-sided placement also confirmed: `-o 'media.name=OUTV
bogus.prop=7'` lands on `output.*` only, `input.*` keeps `… input` defaults.

**Empty props.** `-i ''` ×3, `-o ''` ×3 and two direct (non-`timeout`) spawns:
all **rc=-11** (SIGSEGV; shell rc 139), stderr `timeout: the monitored
command dumped core`, zero nodes. 3 more `-i ''` reps under 16 CPU hogs
(loadavg 47.4): 3/3 SIGSEGV. **Claim 2 CONFIRMED (8/8 + 3/3).** Extensions
(unstated): `-i ' '` (single space) → SIGSEGV; `pw-cat -p -P ''` → SIGSEGV;
`pw-record -P ''` → SIGSEGV — the empty-props crash is a *parser* class, not
a loopback quirk.

**Malformed props are not uniformly silent.** `}{ garbage` → both nodes spawn
with defaults, 4 links, empty stderr (claim holds). But the generalized
headline "a malformed string silently drops the *whole* props value" is
false: `a=b }{ c=d` → rc=255, `error: syntax error in --capture-props:
Mismatched bracket`, no node ever; `{ bad` → same; `media.name=` → rc=255
`Expected object value`. Meanwhile `}{`, `[1,2`, `{ }`, `null`, `"str"`,
`a=b,` do silently drop. **Claim 3 FALSIFIED as a universal law.**

---

## 2. Claim 4 — channel props decorate, flags steer (`receipts/s2-channel.json`)

Content witness: 1 kHz on L, 1.5 kHz on R, amp 8192, played into `r83b_nsa`,
monitor of `r83b_nsb` recorded.

| leg | prop | monitor content | verdict |
| --- | --- | --- | --- |
| C0 base | — | 8191.3 @1k / 8191.4 @1.5k | baseline |
| C1 | `-i 'audio.position=[ MONO ]'` | stereo passthrough, identical | **prop-only** |
| C2 | both sides `[ MONO ]` | stereo passthrough | prop-only |
| C5 | `-i 'channelmap.map=[ MONO ]'` | stereo passthrough | lands, inert |
| C6 | `-i 'audio.channels=1 audio.position=[ MONO ]'` | stereo passthrough | prop-only |
| C3 | `-m '[ MONO ]'` (channels stay 2) | **unstable**: 0.5–1.0 s clean `0.5·(L+R)` (4095.6/4095.6), then 1 k decays (1551.9 FFT-Hann ≈ 3104 true) while 1.5 k stays (2046.9 ≈ 4094) | **author cell wrong** |
| C4 | `-c 1 -m '[ MONO ]'` | clean stable `0.5·(L+R)`, 4095.6/4095.6 in all windows | the armable form |

**Claim 4 CONFIRMED** for the props. But §6 A3 of the scout report
(`pw-loopback -n X -m '[ MONO ]' … -> both ch = 0.5·(L+R), amp≈2047.6/freq`)
is **not reproducible as written**: with the default `-c 2` the map is
malformed (2 channels, 1-entry `[ MONO ]`) and the matrix is time-varying.
The author must arm `-c 1 -m '[ MONO ]'`.

---

## 3. Claims 5–6 — remix laws (`receipts/s3-remix.json`, loadavg 94–117)

| leg | prop | ports | monitor | verdict |
| --- | --- | --- | --- | --- |
| M0 | — | 2 links | [8192,8192] 8191.3 both | full-amp dup |
| M1 | `node.dont-remix=true` | 2 links | identical | lands, **inert** |
| M2 | `stream.dont-remix=true` | **1 link** | **[8192,0]**, FL 8191.3 | **effective** |
| M2_ld (16 hogs) | same | 1 link | [8192,0] identical | stable under load |
| M3/M4 | `channelmix.upmix/disabled` | 2 links | identical | lands, inert |
| W0–W4 | widen 0.5/1.0, upmix-method | 2 links | 8191.3/8191.4 identical | lands, zero spectral effect |
| D0/D1/D2 | stereo→mono | 1 link | 4095.6 @1k **and** @1.5k, peak 7801 | `0.5·(L+R)` |
| D3 | `stream.dont-remix=true` | 1 link | peak 8192, **pure 1k**, FL only | **effective** |
| D3_ld | same + 16 hogs | 1 link | identical | stable |

Claims 5 and 6 **CONFIRMED**, including under load.

---

## 4. Claims 7–8 — adaptive resampler (`receipts/s4-resample.json`, `s4x-s5b.json`)

Player-node props (captured correctly in the second pass): S0
`node.rate=1/44100`, `node.latency=4410/44100`; S1 `resample.disable=true`;
S4 `resample.peaks=true`; S4c `node.rate=1/48000` → 44.1 k sink.

| leg | measured | verdict |
| --- | --- | --- |
| S0 tone44→48 k | dom 1000/1500, peak 8193/8191, overshoot 8193 | pitch preserved |
| **S1 disable + mismatch** | **all-zero, 144000/144000 exact 0**; 2/2 under 16 hogs | **CONFIRMED** |
| S1b disable + **matched** rate | clean tone | mismatch required |
| S1c disable=false + mismatch | clean tone | disable is the switch |
| **S4 peaks + mismatch** | peak 8191, min 0, neg_frac 0, dom DC 4790.8, gaps median 12 (1949/1999 in 11–13), mean 4790.95 in the settled window | shape reproduced |
| S4 quiet vs `S4_ld1/2` | **byte-identical stats** (mean 3168.41 over the 3 s capture, same zero-run histogram) | deterministic under load |
| S4b peaks + matched | clean tone | harmless at matched rate |
| **S4c peaks + 48 k→44.1 k** | clean tone, mean 0, min -8192 | **artifact is upsample-only** (new) |
| S5 `--rate 48000` | player `node.rate` stays `1/44100` | flag ignored (CONFIRMED) |
| LB0/LB1/LB2 loopback 44.1→48 | tone verifies in all; both nodes default `resample.disable=true` | loopback unaffected |
| LB3 peaks on loopback | tone verifies | no artifact |

**Claim 7 CONFIRMED. Claim 8 falsified in waveform class and fundamental.**
The scout's own evidence settles it: `PK44_1.wav` (24000 frames, mean
+4383.29/+4382.43, gap histogram 12×1187 / 13×549 — exactly the report's
numbers) has exact-zero fraction 8.3 % (not ~50 %), a `|sin|` V at zero
crossings, amp@1k = **0.9** (ch0) against a 4095.5 clean baseline by the same
Hann-FFT method, and amp@2k = **1586** (ch1: amp@1.5k = 8.6, amp@3k = 1586).
That is **full-wave magnitude `|x|` plus one forced zero every ~12 samples**,
not half-wave rectification, and the tone's fundamental is **destroyed — the
octave dominates**, so "rectification adds DC+harmonics, not detune" is wrong
(the report's `amp@1k=12882 > baseline 11450` is not reproducible from the
cited evidence by any method tried; the 900–1100 Hz band max there is 2.0).

Labrat (read-only, advisory) audited the receipt corpus and found: the
per-rep means exist only in report prose (the receipt serializes one run) and
the receipt's cited `S4_peaks_mon.wav` was trimmed from `raw/`. My own
analysis of the retained `PK44_{1,2}.wav` shows they are **byte-identical**
(sha256 `2ba24ad4…`) and carry the claimed means exactly — so the "2/2
deterministic reps" claim is substantiated by the retained evidence, while
the *receipt* simply lacks a rep dimension.

---

## 5. Claims 9–10 — latency units and the `-d` delay (`receipts/s5-latency.json`, `s5-onsets*.json`, `s5-scale.json`)

**Units (claim 9 CONFIRMED):** `-l 5`→`240/48000`; `-l 2.5`→`96/48000`;
`-l 10000`→`480000/48000`; `-d 0.25`→`4000/48000`; `-d 1.0`→`16000/48000`;
`-l 0`/`-l abc`/`-d -1`/`-d abc`/`-d 0` → prop absent, no error;
`-l 5 -d 0.25` and `-d 0.25 -l 5` → `240/48000` both orders; `-g r83b_grp`
→ `node.group=r83b_grp`. New: **`-l -5` → `4294967056/48000`** (uint32 wrap,
≈ 89478 s).

**Onset (claim 10 FALSIFIED).** Loopback up and linked, recorder started, tone
started 150 ms later, both spawn times timestamped; transport = first tone
sample − (t_tone − t_mon):

| leg | node.latency prop | transport |
| --- | --- | --- |
| control ×3 (+2 under 16 hogs) | *(absent)* | **0.1025–0.127 s** |
| `-d 1.0` ×3 (+2 under load) | `16000/48000` | **1.103–1.148 s** |
| `-d 0.25` ×2 | `4000/48000` | 0.356 / 0.398 s |
| `-l 100` ×2 | `4800/48000` | 0.106 / 0.106 s |
| `-l 1000` ×2 | `48000/48000` | 0.106 / 0.148 s |

`-d` adds **≈ d seconds** of real transport delay at every value tested and
under load; `-l` adds nothing even at 1.0 s nominal. So the scout's
"latency props are prop-only on this topology" holds for `-l` but is
**false for `-d`** — their 42.7 ms "identical to control" content witness did
not see the delay.

---

## 6. Claims 11–13 — midi / filter / serial (`receipts/s6-midi.json`, `s6x-pins.json`, `s7-filter.json`, `s8-serial.json`)

**Midi (claim 11 CONFIRMED).** `pw-mididump <file>` rc=0 prints
`Note On (channel 1): note C4, velocity 96` / `Note Off … velocity 64`;
missing file rc=255. Bare `pw-mididump` publishes node `midi-dump`
(`media.type=Midi`, `media.category=Filter`, `media.role=DSP`, no
`media.class`, `node.want-driver=true`), **zero links** at spawn.
`pw-midiplay` auto / `--target Midi-Bridge` / bogus name → rc=1
`no target node available`, node dies. `--target 0` publishes
`r83b_mplay` (`Stream/Output/Midi`) unlinked, alive. Manual pins both
directions: `pw-link 'Midi-Bridge:Midi Through: Port-0 (capture)'
'midi-dump:input'` rc=0 → aplaymidi note appears on mididump stdout with
frame counters; `pw-link 'r83b_mplay:output_1' '…(playback)'` rc=0 →
aseqdump `14:0 Note on 0, note 60, velocity 96` + `Note off … 64`.

**pw-filter (claim 12 CONFIRMED).** `which` rc=1; `man -w` "No manual
entry"; `find /usr -name 'pw-filter*'` empty; `pipewire-audio` bin list has
no `pw-filter`; `libspa-filter-graph-plugin-{builtin,ebur128,ladspa,lv2,sofa}.so`
and man7 `libpipewire-module-filter-chain` exist; `pw-cli` module count 13.

**Serial targets (claim 13 CONFIRMED).** `-C 87120 -P 87129` → 4 links land on
`r83b_nsa`/`r83b_nsb`; `target.object` shows the serials.

---

## 7. Unstated modes found (not in the scout's list)

1. **`-i ' '` (whitespace-only) SIGSEGVs** — same class as `-i ''`.
2. **`pw-cat -P ''` and `pw-record -P ''` SIGSEGV** — the empty-props crash is
   shared by the pw-cat family, not loopback-specific.
3. **`-C ''` does not segv — it silently links the capture to the *default
   sink's monitor*** (`SPDIF.monitor → input.*`, rc=0, 2 s). A fail-open
   default, not a drop.
4. **`-P ''` silently links playback to the *default sink*** (`output.* →
   SPDIF playback`, rc=0, 2 s). In this seat's legs only silence was played
   (no tone was ever injected into `r83b_nsa` during those legs).
5. **`-n ''` breaks target resolution**: nodes publish as
   `input.capture.props` / `output.capture.props` (group
   `loopback-<pid>-<n>`), playback links to the **default sink despite
   `-P r83b_nsb`**, capture side unlinked in the 2.5 s window.
6. **`-l -5` → `4294967056/48000`** (uint32 wrap) instead of a drop.
7. `stream.dont-remix=true` on a loopback capture node lands but does not
   change the copy (stereo→stereo); `resample.peaks` on the downsample path is
   clean (§4).

---

## 8. Contention ledger (by name; mandatory)

Foreign seats live during the window, observed read-only and never touched:

| foreign object / process | what it was doing |
| --- | --- |
| `r93-scout` (audio-shokunin) | `probes/r93driver.py <stage> 3` battery; sinks `r93s_in`, `r93s_fc_in` (RUNNING/SUSPENDED across my window) |
| `r94-scout` (audio-shokunin) | `run_all.sh` + `probes/r94driver.py` stages (started ~16:40) |
| `r82ff` fold (audio-shokunin) | `measure_audio.py --probe-ffmpeg-r82` (pid 3036129), sink `r82ff_ns_3036129`, recorded **SPDIF.monitor** during my early window |
| `r78/r79` fold (audio-shokunin) | `pw-loopback -n r79lb_1875167_c02_second_sink` live at teardown; sinks `r79lb_ns_a/b2_1875167` |
| `game-dev-3d r96-boundary` | `driver.py --arm loadff --reps 2 --jobs 6` and `--arm tps30 --jobs 4` — **CPU load arms** |
| `game-dev-3d r99-boundary` | `driver.py --batch` sweeps (jobs 6) |
| `game-dev r88-verify2` / `r92-verify2` | `run_battery.py --godot` batteries |
| leaked `yes` ×12 (pgid 4052818, reparented to systemd --user, 16:38:11) | previous game-dev load arm leak — **not this seat's** (own 16-hog windows verified reaped; see `s1-args.json`/`s5-*`) |
| `alsa_playback.aplay`, `r84b_envp` | foreign clients linked to SPDIF during the s1 window |
| default sink/source | unchanged SPDIF / Line across the whole window (setup + teardown receipts) |

Interference caused by this seat (all disclosed, all bounded): two 2 s
fail-open legs linked my streams to SPDIF (`-P ''`, `-n ''`) and one 2 s
capture leg to SPDIF.monitor (`-C ''`) — **silence only, no tone ever
targeted SPDIF**; midi pins + `aplaymidi`/`aseqdump` on the shared ALSA-seq
bus for ~4 s (links died with my clients); 16 `yes` hogs for 4 bounded
windows (verified killed). No foreign module, node, stream or default was
unloaded, moved, suspended or re-volumed.

---

## 9. Cleanup (verified)

All five modules unloaded by index re-verified against
`module-null-sink` + `sink_name=r83b_*` (5/5 rc=0). At exit:
`pactl list short {sinks,sources,modules} | grep r83b` → **0**; no `r83b`
process, no `midi-dump` link, no seat hog remains
(`receipts/teardown2.json`). Defaults still SPDIF / Line.

---

## 10. Receipts index (sha256 prefix)

| artifact | sha16 |
| --- | --- |
| `receipts/setup.json` | `cf24f60d0f9fcc60` |
| `receipts/s1-args.json` | `1615ff56b0864dc0` |
| `receipts/s1x-ext.json` / `s1x-ext2` / `s1x-ext3` | `93a4dc7429b6f471` / `4cd200a4655dd970` / `1410c11d815155b1` |
| `receipts/s1y-o-props.json` | `2fe6341af4d39a06` |
| `receipts/s2-channel.json` | `c8871a6ccaf45310` |
| `receipts/s3-remix.json` | `11ea7fd0fb1e252d` |
| `receipts/s4-resample.json` | `213089a60c691bd6` |
| `receipts/s4x-s5b.json` | `ce8c08b658ca91e7` |
| `receipts/s5-latency.json` | `723fa87fc0be83d7` |
| `receipts/s5-onsets.json` / `s5-onsets-load.json` | `5f790ceaf7aa38f1` / `b4b4c32a249e391e` |
| `receipts/s5-scale.json` | `9c4a47f5b9200c79` |
| `receipts/s6-midi.json` / `s6x-pins.json` | `82940a4877cfabea` / `a3281685c0501a98` |
| `receipts/s7-filter.json` | `070671d5d8e32ab7` |
| `receipts/s8-serial.json` | `417dd9db5037e552` |
| `receipts/s9-misc.json` / `s9x-move.json` | `74856f101227b3df` / `52da1064fb4d266e` |
| `receipts/teardown.json` / `teardown2.json` | `1c8e6a939a21731b` / `be4faa2b6aa92685` |
| `manifest.json` | 444 files, 36 588 709 B, 22 receipts (regenerated after teardown) |

Per-leg `runs/<stage>/<leg>/{cmd.txt,stderr.txt,meta.json}` plus raw monitor
wavs in `raw/` are covered by `manifest.json`.

---

## 11. What the author may safely pin (and must not)

- **Do not pin** "malformed props always drop silently" — three shapes hard
  error rc=255 with `syntax error in --capture-props` and spawn nothing.
- **Do not pin** the §6 A3 cell as written; arm `-c 1 -m '[ MONO ]'`.
- **Do not pin** "latency props are prop-only": `-d` is real (≈ d seconds of
  transport delay); `-l` is prop-only. And pin `-l -5` as the uint32 wrap.
- **Reclassify** `peaks_rectified_artifact` → `peaks_abs_octave_artifact`:
  full-wave `|x|`, one forced zero every ~12 samples, mean +4383 (their
  window) / +4791 (settled), DC-dominant, **fundamental destroyed → octave**.
  Upsample-only (48→44.1 k is clean).
- **Pin** the empty-props SIGSEGV class with its extensions (whitespace,
  `pw-cat`/`pw-record` `-P ''`) and the fail-open `-C ''`/`-P ''`/`-n ''`
  default-sink fallbacks.
- Pin `stream.dont-remix` as the only effective remix switch, the
  `0.5·(L+R)` downmix / full-amp upmix gains, `resample.disable` zeros,
  the midi target refusal + manual-pin round-trip, pw-filter absence, and
  serial targets — all reproduced here under load.

Seat stop. No commits, no tracked writes, no scope widening, no shipping
decision.
