# R77 BOUNDARY (audio) — capture/playback assumption edges, live-probed

Seat: **executor (BOUNDARY)**. Repo `~/Projects/shokunin/audio-shokunin` @ HEAD
`b0b5d4d` (`r76 report-last`). Host `plazir27`, measured 2026-10-14
**16:41–17:0x UTC**.

**Write scope: exactly `corpus/live/r77-boundary/` (untracked, new) plus this
report. Zero tracked-file edits. The author's live edit to
`corpus/fixtures/measure_audio.py` was never read or imported** — every harness
here is seat-private (`r77b_lib.py` + `p*.py`).

Toolchain (this host, this session): PipeWire **1.6.8**, pacat/parec/pactl
**17.0-98-gb096** (libpulse 17.0.0, protocol 35), alsa-utils **1.2.16**, ffmpeg
**n9.0.1**, SoX_ng **14.8.0.1**, Python **3.14.7**, numpy 2.5.3, Linux 7.2.3.

---

## 0. Headline

| # | frontier | verdict | the single sharpest measured fact |
| --- | --- | --- | --- |
| 1 | fallback-law edges | **LAW + MECHANISM, falsifies an r77-scout row** | under `-P stream.capture.sink=true` a `.monitor`-suffixed name is **never resolved**: with the default sink moved to Speaker, `--target <SPDIF>.monitor` consumed the **Speaker** monitor (the fallback), while bare `--target <SPDIF>` consumed SPDIF. `pw-dump` shows **0 nodes named `*.monitor`** |
| 2 | moving the default sink | **NEW TRAP** | `pactl set-default-sink X` returns **rc=0 and does nothing** (5/5 samples over 2 s, metadata untouched). Only `pw-metadata -n default 0 default.audio.sink '{"name":X}'` moves it |
| 3 | multiple `-P` props | **NEW, 6 rows** | duplicate keys are **last-wins** (`…=true …=false` ⇒ the no-prop 44-byte empty wav); `stream.capture.sink=0` ⇒ false; `=TRUE` ⇒ true; **`=yes_please` ⇒ silently false**, never an error; `node.target=` and `target.object=` props both bind |
| 4 | `sustained_after_target_loss` | **SHARPENED, 3 provider-death classes** | the zombie is **not** a flood: it is silence at the clock, **byte-exact to the `-n` bound** (1 152 044 B, overrun **0**), rc=1, finalized — *indistinguishable from a healthy silent capture*. Same for graceful unload, **hard `kill -9` of the node-owning client**, and feeder kill |
| 5 | split sentinel | **arecord = rename; pw-record = no rename, a different sentinel** | arecord's split file is **exactly 2 147 483 692 B** and renames to `<name>-01.wav`; a **finalized** 4.29 GiB pw-record wav carries `riff_size_field = 0xFFFFFFFF` + a `fact` chunk with the true frame count. `-m/--max-file-time` **never fires on `-D null`** |
| 6 | reader matrix gaps | **`soxi -s` == `soxi -D`, always; `wave` is not fail-safe; the ranking inverts above 4 GiB** | on the same wound `soxi -s`/`-D` agree in **6/6** wounds; python `wave` **inflates to 536 870 912 frames** on the `0x80000000` family and **1 073 741 823** on `placeholder_ff`; on a finalized **4.29 GiB** capture `soxi` says **0**, `sndfile-info` says 10.923 s (truth 11.71875 s) and **`ffprobe` is the only honest reader**. A *player* is honest: `ffplay` ran 1.66 s on the wound whose declared size implies 12 173.9 s |
| 7 | format axis | **truthful** | resample to 8 k/11 k/44.1 k/96 k/192 k keeps the FFT peak at **1000.0 Hz** and the level within +0.2 %; **24-bit roundtrip is bit-exact** (all samples ≡ 0 mod 256, aligned residual 0.0); `--channels 6` upmix is truthful (tone only in FL/FR) |
| 8 | contention | **no hazard on the pulse path; `alsa_busy` is arecord-vs-arecord only** | two `pw-record` on one source → **identical sha256**; monitor roundtrip while another capture holds the source → carries the tone; a *second* `arecord -D hw:0,0` → `Device or resource busy` |
| 9 | 4 GiB boundary | **no cap, no error, no rename** | a single pw-record file grew to **5 624 336 992 B (5.24 GiB)** with no stderr, no second file, no rotation; its advertised `--container rf64`/`w64` both **fail** (`Format not recognised`, 0 bytes) |
| 10 | the split counter at −99 → −100 | **UNMEASURED (named cost)** | the counter only advances on the **2 GiB byte split** under `-D null`; 100 advances cost **~214 GB written**. I refused that on a shared host — see §10 |

---

## 1. Method and the tone anchor

This host's real sources (Line, Mic) are **digital silence** (`peak = 0`,
`nz = 0.0`), so byte identity between two captures is evidence of nothing. Every
verdict below that says "which node did the capture consume" is anchored on an
injected **1 kHz stereo tone** (`corpus/live/r77-boundary` harness writes it:
`peak = 16384`, `nz = 0.958`, `fft = 1000.0 Hz`, 768 044 B).

A capture that carries the tone **consumed the monitor of the sink the tone was
played into**; a silent capture consumed some other node. `sig2()` runs **both**
placements (tone→SPDIF, tone→Speaker) and reports the 2-bit signature, because a
one-sided leg cannot separate *"the target was honoured"* from *"the target fell
back to the node the tone happened to be in"* — which is exactly the trap that
made the scout's `<default sink>.monitor → honoured` row vacuous.

Calibration: clean tone leg = `peak 16384, fft 1000.0, nz 0.72–0.76, 384 044 B,
rc=1`. **`rc=1` is the normal rc of a healthy bounded `pw-record` capture** —
reproduced in every receipt of this seat.

---

## 2. FRONTIER 1 — the fallback law, and the mechanism behind it

### 2.1 A `.monitor` name is never resolved (falsifies the scout's row)

`probe-p1-fallback-law.json`, `probe-p1b-moved-default.json`,
`probe-p1c-mechanism.json`:

| `--target` under the prop | tone→SPDIF | tone→Speaker | consumed | verdict |
| --- | --- | --- | --- | --- |
| `<SPDIF sink>` (default) | yes | – | default/SPDIF monitor | honoured |
| `<Speaker sink>` | no | **yes** | Speaker monitor | **honoured** |
| `<Speaker>.monitor` | **yes** | no | default/SPDIF monitor | **fallback** |
| `<HDMI>.monitor` | **yes** | no | default/SPDIF monitor | **fallback** |
| `<SPDIF>.monitor` (= default) | yes | no | default/SPDIF monitor | **indistinguishable** |
| `<Speaker>.monitor.monitor` | yes | – | default monitor | fallback |
| `<Speaker>.` (trailing dot) | yes | – | default monitor | fallback |
| `<Speaker name minus 5 chars>` | yes | – | default monitor | fallback |
| `<LINE source>` | yes | – | default monitor | fallback (scout) |
| `no_such_node_xyz` | yes | – | default monitor | fallback (scout) |
| `@DEFAULT_MONITOR@` | yes | – | default monitor | indistinguishable |
| *(no `--target`, prop)* | yes | – | default monitor | auto |

**The falsifying experiment** (`p1c`): move the default sink to Speaker
(genuinely — see §2.2) and re-run:

| target, default = **Speaker** | signature (SPDIF?, SPK?) | consumed |
| --- | --- | --- |
| `<SPDIF sink>` (bare) | [True, False] | **SPDIF monitor** — a bare sink node name is honoured |
| `<SPDIF sink>.monitor` | [**False, True**] | **Speaker monitor = the fallback** |
| `<Speaker sink>` (bare) | [False, True] | Speaker monitor |
| `no_such_node_xyz` | [False, True] | Speaker monitor |

So `<SPDIF>.monitor` did **not** follow the name it was given — it followed the
*default*. The scout's row `prop|<default sink>.monitor → "target honoured"` is
**vacuous and now falsified**: honoured and fallback land on the same node only
while that sink is the default.

**Mechanism (measured, not inferred from source):** `pw-dump` enumerates 14
nodes — 4 `Audio/Sink` (`…hdmi-stereo`, `…SPDIF__sink`, `…Speaker__sink`,
`…Headphones__sink`), 2 `Audio/Source`, and **zero nodes whose `node.name`
contains `.monitor`**. In PipeWire a monitor is not a node; `<sink>.monitor` is
a *pulse-layer* alias (which is why `parec -d <sink>.monitor` works — the scout
measured that — while native `pw-record` cannot resolve it). `pw-record` with
`stream.capture.sink=true` resolves `node.name` among **Audio/Sink** nodes; a
bare sink name matches, everything else misses and falls back to the current
default sink's monitor.

### 2.2 `pactl set-default-sink` is a silent no-op on this host

| action | `pactl get-default-sink` | `default` metadata `default.audio.sink` |
| --- | --- | --- |
| before | `…SPDIF__sink` | `{"name":"…SPDIF__sink"}` |
| `pactl set-default-sink …Speaker__sink` (rc=0, stderr empty) | `…SPDIF__sink` ×5 samples / 2 s | **unchanged** |
| `pw-metadata -n default 0 default.audio.sink '{"name":"…Speaker__sink"}'` | `…Speaker__sink` ×5 | updated |

`pactl_set_effective = False`, `pw_metadata_effective = True`. This is why the
scout's "the fallback should move with the default — not measured" was
untestable as written: the naive mover does nothing, silently. It is a live trap
for any harness that "moves the default sink" with pactl and then measures a
fallback.

### 2.3 Multiple `-P` props (`probe-p1-fallback-law.json`, `multi_prop`)

| props | result |
| --- | --- |
| `-P node.target=<Speaker> -P stream.capture.sink=true`, no `--target` | **honoured** (Speaker monitor) |
| `-P stream.capture.sink=true -P target.object=<Speaker>` | **honoured** — the prop `pw-dump` advertises as intent *does bind* as input |
| `-P stream.capture.sink=true -P stream.capture.sink=false` | **last wins ⇒ false**: 44-byte finalized wav, `data(0)`, no link, rc=1 |
| `-P stream.capture.sink=false -P stream.capture.sink=true` | last wins ⇒ true: honoured |
| `-P stream.capture.sink=0` | false (44-byte empty, no link) |
| `-P stream.capture.sink=TRUE` | true (honoured) — case-insensitive |
| `-P stream.capture.sink=yes_please` | **silently false** (44-byte empty, no link, **no error**) |
| `-P r77b.bogus=1 -P stream.capture.sink=true` | unknown prop ignored, capture-sink still honoured |

### 2.4 Without the prop

`<SPDIF>.monitor` and `<Speaker>.monitor` both land a **44-byte finalized wav
with `data(0)`**, rc=1, stderr `<file>\nstream node <N> error`. Monitor names
never resolve; only a bare *source* node name does (scout §1.1, re-confirmed).

---

## 3. FRONTIER 2 — the zombie capture is clock-paced silence, not a flood

`probe-p2-zombie.json`, `probe-p2b-hard-kill-provider.json`. Nominal for a
6 s `-n 288000` s16/2ch/48 k capture: **1 152 044 B**.

| provider death | rc | bytes | overrun vs nominal | riff | frames | peak | nz | rate after loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `pactl unload-module` of the captured null sink | 1 | **1 152 044** | **0** | finalized | 288 000 | 0 | 0.0 | 192 228 B/s (nominal 192 000) |
| **`kill -9` of the node-owning `pw-cli` client** (`object.linger=false`) | 1 | **1 152 044** | **0** | finalized | 288 000 | 0 | 0.0 | 191 262 B/s |
| `kill -9` of the *feeder* (`pw-cat -p` into a surviving sink) | 1 | **576 044** | **0** | finalized | 144 000 | 16 384→0 | 0.86→0.02→0.0 | – |

- The unload **succeeded** (sink gone from `pactl list short sources`) and the
  `kill -9` client was **reaped with rc=−9** and its sink disappeared
  (`sink_still_listed: false`). The capture did not notice either.
- Pacing samples (0.15 s cadence) are linear across the loss event
  (`190 965 B/s` before → `192 228 B/s` after): **the stream stays frame-clocked
  and `-n` still bounds it exactly.** The scout's "keeps producing bytes at 100 %
  rate, forever" is sharpened: it is not unbounded — it is *exactly* the
  requested number of frames of digital silence.
- The feeder-kill segments show the signal stopping (tone 0.86 → 0.02 → 0.00)
  while the stream keeps its clock to the bound.

**Named class kept: `sustained_after_target_loss`.** Its operational form is
harsher than "the artifact lies": **the artifact is byte-count-identical to a
healthy capture of a silent source**, and its rc (1), header state (finalized)
and data sizes are identical too. The only honest witnesses are (a) an external
link query, or (b) the fact that the node no longer exists.

---

## 4. FRONTIER 3 — the split sentinel: arecord renames, pw-record does not

### 4.1 arecord

- `strings /usr/bin/arecord` (exact lines): `%s-01.%s`, `%s-01`,
  `%s-%02i.%s`, `%s-%02i` — one first-file template + one counter template;
  `%02i` is a *minimum width*, so 100 prints `-100`.
- **The split file size is exactly 2 147 483 692 B** (= `0x80000000` + 44),
  measured in three consecutive split files: `pt2-01.wav`, `pt2-02.wav`,
  `pt2-03.wav` at 3 s of a free-running `-D null -f cd` leg. The requested
  `<name>.wav` **does not exist** — arecord renamed it.
- **`-m/--max-file-time` does not fire on `-D null`.** Two measurements:
  `-d 130` (130 s of audio) finished in **0.003 s wall** with **one** 2 080 044 B
  file; a `timeout 3` leg with `--period-size=16 --buffer-size=64` (throttled to
  ~250 MB/s) also produced **one** file with no `-m` rotation. Under `-D null`
  the only rotation observed is the **byte** split, in every case.
- `-D pipewire -f cd` cannot be used for this: `arecord: set_params:1462:
  Unable to install hw params` (reproduces the r76 critic's note).

### 4.2 pw-record / libsndfile — the answer to "does the sentinel exist there too?"

- No rotation: `grep -c` for a `%s-NN` rename template in `/usr/bin/pw-record`
  is **0**, and `pw-record --help` has no rotation/split flag.
- Its advertised 64-bit containers are **broken**: `--container rf64` and
  `--container w64` (both listed by `--list-containers`) produce a **0-byte file**
  at rc=1 with `sndfile: failed to open audio file: "…": Format not recognised.
  error: open failed: Input/output error`. `--container caf` (388 096 B) and
  `--container raw` (384 000 B) work; `--container wav` is byte-identical to the
  default.
- **A single file simply grows past 4 GiB — no error, no rename, no second
  file.** Measured 5 624 336 992 B (5.24 GiB, still growing, killed by my own
  cap) and then, in a leg that **ended on its own `-n` bound**, a *finalized*
  **4 608 000 608 B** file (= 9 000 000 frames × 512 B + 608) whose header is
  `RIFF ffffffff WAVE` — i.e. **`riff_size_field = 0xFFFFFFFF` (unknown size)**,
  with a **`fact` chunk carrying the true frame count 9 000 000** and a `PEAK`
  chunk (520 B). The requested filename stayed valid.

So: **arecord splits and silently renames, with a per-file `0x80000000`
sentinel; pw-record never renames and marks the RIFF size `0xFFFFFFFF` while
keeping the file self-describing via `fact`.** The two "sentinels" are different
mechanisms, and only arecord's breaks the caller's path check.

### 4.3 Readers on that finalized >4 GiB file — the ranking inverts

`probe-p9-readers-over-4gib.json`: the same capture, re-created
(4 608 000 608 B, `riff_size_field = 0xFFFFFFFF`, `fact` = 9 000 000 frames,
71.5 s, ended on its own `-n` bound), read by the metadata witnesses **before
deletion**. Truth: **9 000 000 frames = 11.71875 s**, 64 ch, 768 kHz.

| witness | answer | verdict |
| --- | --- | --- |
| `ffprobe format.duration` | **11.718750** | ✅ **the only honest reader** |
| `sndfile-info` | **8 388 607 frames / 10.923 s** + `Warning : filelength > 0xffffffff. This is bad!!!!` | **WRONG (−6.8 %)** |
| `soxi -s` | **0** | **FALSE** (a 4.29 GiB, 11.72 s capture called empty) |
| `soxi -D` | **0.000000** | **FALSE** |
| python `wave` | **rejects**: `unknown extended format: 00000003-0000-0010-8000-00aa00389b71` | honest abstention — but for a *format* reason (the extensible IEEE-float GUID), not a size reason |

`soxi` emits `soxi WARN wav: wave header missing extended part of fmt chunk` /
`data length is unspecified; taking it from the file length` and then answers
**0** anyway. `sndfile-info`'s number is the frame count implied by the
`0xFFFFFFFF` **declared** size (naive arithmetic: `(0xFFFFFFFF − 608)/512 =
8 388 606`, reported 8 388 607) — i.e. **it trusts the sentinel and produces a
plausible-looking wrong duration** while printing a warning. The reader that was
honest on 6/6 small wounds is the one that lies here, and the reader that
abstains on some small wounds is the only one that is right.

---

## 5. FRONTIER 4 — reader-matrix gaps

`probe-p3-readers.json`. Availability first, because two of the brief's rows are
**absent on this host, and are reported as absent, not skipped**:
`mediainfo` **MISSING** (`command -v` → nothing); python **`soundfile`
MISSING** (`ModuleNotFoundError`; `~/.cache/pip` holds no wheel). `sndfile-info`
and `ffplay` are present.

### 5.1 Six witnesses on six wounds (this seat's own wounds)

| wound | rc | bytes | riff field | data declared | `sndfile-info` | `ffprobe` | python `wave` | `soxi -s` | `soxi -D` |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `pw-record` KILL | −9 | 294 956 | `placeholder_8` | `zero` | 73 728 ✅ | 1.536 ✅ | **rejects** (fmt/data missing) | **0** | **0.000000** |
| `arecord -D hw:0,0` KILL | −9 | 264 668 | finalized | `placeholder_80000000` | 66 156 ✅ | 1.500136 ✅ | **536 870 912** | **536 870 912** | **12 173.943583** |
| `arecord -D hw:0,0` TERM | 1 | 264 772 | finalized | finalized | 66 182 ✅ | 1.500726 ✅ | 66 182 ✅ | 66 182 ✅ | 1.500726 ✅ |
| `arecord -D sysdefault` TERM | 1 | 267 004 | finalized | `placeholder_80000000` | 66 740 ✅ | 1.513379 ✅ | **536 870 912** | **536 870 912** | **12 173.943583** |
| `ffmpeg -f pulse` KILL | −9 | 524 288 | `placeholder_ff` | `placeholder_ff` | 131 052 ✅ | 2.730271 ✅ | **1 073 741 823** | **0** | **0.000000** |
| `ffmpeg -f pulse` TERM | 255 | 585 678 | finalized | finalized | 146 400 ✅ | 3.050000 ✅ | 146 400 ✅ | 146 400 ✅ | 3.050000 ✅ |

- **`soxi -s` vs `soxi -D` on the same wound: they never differ** (6/6 agree —
  both 0 on the `placeholder_8`/`zero` family, both 536 870 912 / 12 173.943583
  on the `0x80000000` family, both honest elsewhere). They are one witness, not
  two; `soxi -s` is frames and `soxi -D` is size-derived seconds of the *same*
  wrong number.
- **python `wave` is not fail-safe.** It *rejects* the `placeholder_8` family
  (honest abstention, matching the scout) but **inflates to 536 870 912 frames**
  on the `0x80000000` family and **1 073 741 823 frames** on `placeholder_ff`
  (≈ 6 h 20 m of "audio" from a 0.5 MB file). The scout's "wave fails safe by
  rejecting" is **falsified in scope**: it is fail-safe on one family and
  fail-loud on the other two — the same failure mode as `soxi`, on different
  bytes.
- `sndfile-info` is honest **6/6 below 4 GiB** — and **wrong above it** (§4.3), so
  its record is **6/7**, with the failure boundary named. `ffprobe
  format.duration` is honest whenever it answers. Reader ordering for a future
  arm: **below 4 GiB** `sndfile-info ≳ ffprobe > wave (family-dependent) > soxi
  (fail-loud on two families)`; **above 4 GiB** `ffprobe > sndfile-info >
  wave (abstains) > soxi (answers 0)`. A reader choice pinned on the small-wound
  matrix is the wrong choice for the large-file matrix, and vice versa.
- **New wound row:** `arecord -D sysdefault` **TERM** is the same reader family
  as KILL (data `0x80000000`) and fools `wave`, `soxi -s` and `soxi -D`
  identically, whereas `hw:0,0` TERM is honest to all six. The r76 device axis
  (scout §4.4) extends to the reader layer: on `sysdefault`, **no reader can
  distinguish TERM from KILL**.
- **New decode-side class:** `ffmpeg`/`ffplay` on the `placeholder_ff` wound
  print `[pcm_s16le @ …] Invalid PCM packet, data has size 2 but at least 4
  needed` — the payload is not a whole number of frames — yet rc=0 and the real
  content plays.

### 5.2 Does the inflated arecord header PLAY 3 h of silence? **No.**

`ffplay -nodisp -autoexit` (SDL dummy driver), bounded at 6 s, and
`ffmpeg -i <wound> -f null -`:

| wound | declared size if trusted | `ffplay` wall | hit cap | rc | `ffmpeg -f null` wall |
| --- | --- | --- | --- | --- | --- |
| `arecord` KILL | 12 173.9 s | **1.66 s** | False | 0 | 0.032 s |
| `arecord` TERM | 1.5007 s | 1.66 s | False | 0 | 0.034 s |
| `pw-record` KILL | 0 (declared) | 1.59 s | False | 0 | 0.030 s |
| `ffmpeg` KILL | – | 2.78 s | False | 0 | 0.033 s |
| 0-byte rf64 artifact | – | 0.03 s (`Invalid data found`) | False | 0 | 0.021 s, rc=183 |

**The player is EOF-driven, not declared-size-driven**: on every wound it ran
≈ the *real* content duration. The inflated declared size never becomes playback
time. So the reader failure modes are **metadata-reader-specific** — a decoder
or player is the sixth witness and it is honest.

---

## 6. FRONTIER 5 — format axis

`probe-p4-format.json`, `probe-p4b-format-truth.json`. Tone-anchored, so "did
the conversion keep the signal" is measured (FFT peak + level), not assumed.

### 6.1 Resampling is truthful in frequency and level

| leg | bytes | reported `fmt` | frames | peak | **fft** |
| --- | --- | --- | --- | --- | --- |
| `-n 96000` baseline s16/2ch/48 k | 384 044 | tag 1 / 2ch / 48000 / 16 | 96 000 | 16 384 | **1000.0** |
| `--rate 8000 --channels 1` | 32 044 | 1ch / 8000 / 16 | 16 000 | **16 401** | **1000.0** |
| `--rate 8000 --channels 1 --quality 15` | 32 044 | 1ch / 8000 / 16 | 16 000 | **16 421** | **1000.0** |
| `--rate 11025 --channels 2` | 88 244 | 2ch / 11025 / 16 | 22 050 | 16 383 | **1000.0** |
| `--rate 44100 --channels 1` | 176 444 | 1ch / 44100 / 16 | 88 200 | 16 387 | **1000.0** |
| `--rate 96000 --channels 1` | 384 044 | 1ch / 96000 / 16 | 192 000 | 16 384 | **1000.0** |
| `--rate 192000 --channels 2` | 1 536 044 | 2ch / 192000 / 16 | 384 000 | 16 384 | **1000.0** |

**The 1 kHz tone lands at 1000.0 Hz at every rate, mono and stereo, and the level
is preserved within +0.2 %** (resampler overshoot), i.e. legal-but-weird combos
resample *truthfully* — no garbage, no aliasing peak, no gain error. (Two legs in
the first pass measured 15 384 / 21 867 — those ran while a concurrent seat's
playback was in the monitor; the level moved, **the frequency never did**. Those
rows are labelled confounded, and the table above is the clean-window re-run.)
`-q 0` and `-q 15` are byte-identical to the default at 48 k (384 044 B, peak
16 384), so `-q` remains unobservable in the artifact.

### 6.2 24-bit roundtrip is bit-exact (phase-independent proof)

The first pass compared the s24 leg against the s16 leg sample-by-sample and got
a huge delta (`max 32 394` s16-LSB) — that was **capture-to-capture phase
offset**, not quantisation, and it is recorded as a killed hypothesis. The
phase-independent tests:

| test | result |
| --- | --- |
| s24 `fmt` | tag 1, **24 bits, `block_align = 6` (packed 3-byte)**, 96 000 frames |
| s24 peak | **4 194 304 = 256 × the s16 peak** |
| every s24 sample ≡ 0 (mod 256) | **true** (distinct residues = `{0}`) |
| aligned residual vs (s16 × 256) | **lag 0, max 0.0, rms 0.0** |
| f32 peak (float units) | **0.500000** = s16/32768, ratio **1.0** |
| s32 leg | **confounded** (concurrent playback in the monitor) → s32 exactness **not verified** |
| `--format u8` | peak 192 = 128 + 64 → s16>>8 + bias ✅ |
| `--channels 6` upmix | tag **65534 (WAVE_FORMAT_EXTENSIBLE)**, `block_align` 12, per-channel peak **[16384, 16384, 0, 0, 0, 0]** → truthful upmix, no duplication |
| `--channels 1 --channel-map FL` | **succeeds** (192 044 B, 1ch) — the scout's refusal row is specifically `FL,FR` (2 names for 1 channel); a single valid name is accepted |
| `--container rf64` / `w64` | **0 bytes, rc=1, `Format not recognised`** (see §4.2) |

---

## 7. FRONTIER 6 — contention and the roundtrip under a foreign holder

`probe-p5b-contention.json` (canonical; `probe-p5-contention.json` is the
superseded first pass — see §9).

| leg | result |
| --- | --- |
| two `pw-record` on the **same real source**, concurrent | both rc=1, 384 044 B, **identical sha256 `e3a90286b3b54201`** |
| `arecord -D hw:0,0` first, `pw-record` on the same source second | arecord rc=0 / 352 844 B **and** pw-record rc=1 / 384 044 B — **both succeed** |
| `pw-record` first, `arecord -D hw:0,0` second | both succeed (384 044 B / 352 844 B) |
| **two concurrent `arecord -D hw:0,0`** | first rc=0 / 352 844 B; second rc=1, **no file**, `arecord: main:850: audio open error: Device or resource busy` ⇒ **`alsa_busy`** |
| `parec --raw` while a `pw-record` holds the same source | rc=0, 65 536 B delivered (`write() failed: Broken pipe` from my `head -c`) |
| **monitor roundtrip while another capture holds the source** (the brief's question) | monitor leg **carries the tone** (peak 16 384, 384 044 B) while the source-hold leg gets its full 144 000 frames → **no hazard** |

So `alsa_busy` is pinned for **arecord-vs-arecord** on `hw:0,0`; the PipeWire
pulse path multiplexes freely. Device availability around the run: the preflight
needed **23 attempts / 11.0 s** before `arecord -D hw:0,0` could open (a
concurrent seat was probing), and was free on the **first** attempt at all three
later checkpoints — named as a *foreign-holder* latency, not a clean
release-time pin.

---

## 8. Confounds, provenance, and what I got wrong

1. **Two concurrent seats were live.** The author's
   `measure_audio.py --probe-capture-r77` (started ≈16:45, 900 s timeout) and the
   `r77-baseline` seat's `--probe-fifo-hold-ladder-r70` + an `ffmpeg` leg. Their
   playback was visible in the SPDIF monitor as **level inflation with the tone
   intact** (peaks 20 379 / 21 867 / 32 768 / 4 124-at-220 Hz vs the clean
   16 384). Every verdict in this report is taken from the **frequency/identity**
   witness (`fft == 1000.0 ± 25 Hz` **and** both tone placements), which survived
   the confound; every *level* row that was measured in a confounded window is
   labelled as such (p4's baseline/8 k legs, p4b's s32 leg, p1's `moved_*` block).
2. **`p0` silence baseline** (`probe-p0-confound.json`, non-invasive — it plays
   nothing): SPDIF/Speaker/HDMI clean (`peak 0`), then **SPDIF busy**
   (`peak 5 648`, `fft 220 Hz`, `nz 0.971`) on the 4th sample — the concurrent
   seat's playback appearing mid-probe. This is the honest status of the host
   during my window.
3. **My "silence gate" in p4b was invalid by construction** — the helper always
   plays the tone, so `confounded: True` there measures my own tone, not silence.
   Recorded as a harness bug; `p0` is the correct instrument.
4. **I mis-read the rotation mechanism once and corrected it.** The 7 files
   produced by a `-D null -m 1` leg are the **2 GiB byte split**, not `-m`
   rotations: the throttled `--period-size=16` leg ran 3 s of wall time and
   produced **one** file, so `-m` does not fire on `-D null` at all. §4.1 states
   the corrected version.
5. **My own byte-discipline incident.** The un-watchdogged rotation validation
   wrote **~13 GB** into `/dev/shm` (7 files × ~1.86 GB) and hit
   `Disk quota exceeded`; the next counter attempt then died immediately with
   `arecord: begin_wave:2773: write error` (a `PosixPath.truncate` bug killed my
   watchdog thread before it truncated anything). Own fault, named. `/dev/shm` is
   back to **16.15 GB free** and all scratch is deleted.
6. **The delegated labrat was BLOCKED and produced no evidence.** Its seat
   substrate exposes no exec tool (only find/grep/read), so it could not run
   `strings`, `arecord` or python; it also reported `arecord` as absent from
   `/usr/bin`, which is **wrong** — `command -v arecord` → `/usr/bin/arecord`,
   `arecord --version` → 1.2.16. Its file-finder is sandboxed away from `/usr`.
   Recorded as a named substrate blocker; **I ran the sentinel probe myself** and
   it is measured in §4.1. Its advisory inference (`%02i` widens, no cap) agrees
   with the strings evidence; neither of us measured past `-07`.
7. Every number here is this-host / this-toolchain / this-session. Nothing is a
   portability claim, and the mechanism claims in §2.1 are *inferences from the
   measurements above* (node inventory, the moved-default 2×2, the 3 ms
   free-run) — no alsa-utils or libpipewire source was read (none on this host).

---

## 9. Superseded rows (kept for the record, with the reason)

| artifact | why superseded |
| --- | --- |
| `probe-p1-fallback-law.json` `moved_default` block | **VOID**: the default never moved (`pactl set-default-sink` no-op). Replaced by `p1b`/`p1c` |
| `probe-p1-fallback-law.json` one-sided `consumed` verdicts | every positive `a`-leg verdict is re-verified two-sided in `p1b`/`p1c` |
| `probe-p5-contention.json` legs B/C/D | snapshot-before-reap (partial files) and a device already busy from a foreign holder; replaced by `p5b` |
| `probe-p4-format.json` `s24_roundtrip` block | phase-offset artefact; replaced by `p4b`'s phase-independent tests |
| `probe-p4-format.json` 8 k level rows (15 384 / 21 867) | confounded by the concurrent seat's playback; replaced by the clean 16 401 / 16 421 rows |
| `probe-p4b-format-truth.json` `silence_baseline` | invalid instrument (it plays the tone); `p0` is correct |
| `probe-p7p8` phase 8 (counter) | quota exhausted before it started (`PosixPath.truncate` bug); **no counter data** |

---

## 10. Honest edges — what is measured, what is predicted, what is blocked

- **MEASURED**: §2, §3, §4.1–4.3, §5, §6, §7, and the finalized >4 GiB header
  **and** its reader matrix.
- **PREDICTED (not measured):** the arecord counter past `-07`. The only
  reachable route under `-D null` is the **2 GiB byte split**, so 100 advances
  cost **~214 GB written**; the `-m` route does not fire on `-D null` and would
  need a **100 s exclusive real-ALSA hold** (`hw:`/`sysdefault`), which I
  refused on a host with two live seats. The `%02i` format string (single
  occurrence, minimum-width int) makes a terminal NN unlikely, but I am not
  claiming it as measured.
- **BLOCKED:** `mediainfo` and python `soundfile` are **not installed** on this
  host and there is no wheel in the pip cache; those two reader rows cannot be
  produced here at all.
- **NOT VERIFIED:** `--format s32` exactness (its leg was confounded); the
  fallback behaviour under *no* default sink (not reachable — PipeWire always has
  one); `@DEFAULT_MONITOR@` vs the fallback remain **indistinguishable** by
  construction (same node), now with a moved-default basis; `sndfile-info`'s
  `8 388 607` is quoted with the naive arithmetic that reproduces it, but I did
  not read libsndfile source to name the exact clamp.
- **NOT ATTEMPTED:** reading alsa-utils/libpipewire source to confirm the
  resolver's target class and the `-m` clock.

---

## 11. Receipts

All under `corpus/live/r77-boundary/` (untracked, new; operator to commit).
Harnesses: `r77b_lib.py` + `p0_confound.py`, `p1_fallback.py`, `p1b_moved.py`,
`p1c_mechanism.py`, `p2_zombie.py`, `p2b_hardkill.py`, `p3_readers.py`,
`p4_format.py`, `p4b_truthtest.py`, `p5_contention.py`, `p5b_contention.py`,
`p6_sentinel.py`, `p7p8_bigwav_counter.py`, `p9_readers_4gib.py`.

| receipt | sha256 (first 16) |
| --- | --- |
| `probe-p0-confound.json` | `425bfceb7fa630e0` |
| `probe-p1-fallback-law.json` | `509b190f323444c6` |
| `probe-p1b-moved-default.json` | `aef640c6aaca407c` |
| `probe-p1c-mechanism.json` | `b926a7a50f683c9c` |
| `probe-p2-zombie.json` | `f5cf1c31c9070d05` |
| `probe-p2b-hard-kill-provider.json` | `f172cfac1ff5e613` |
| `probe-p3-readers.json` | `4820a319a7adbe89` |
| `probe-p4-format.json` | `78557670bf7dcdef` |
| `probe-p4b-format-truth.json` | `9530476851ab2712` |
| `probe-p5-contention.json` (superseded) | `a32bbfd7d0dcc8f4` |
| `probe-p5b-contention.json` | `a0b2b9f3ca7f6b4e` |
| `probe-p6-sentinel.json` | `62a1e00377abc34f` |
| `probe-p7p8-bigwav-and-counter.json` | `4d4a8ab178cb4fdf` |
| `probe-p9-readers-over-4gib.json` | `71a252f782a5c69a` |

Final state of the seat's scratch: `/dev/shm/r77b` deleted, `/dev/shm` back to
**16.15 GB free**; `git status` shows only `?? corpus/live/r77-boundary/` and the
untracked report — **no tracked file was modified by this seat**.
