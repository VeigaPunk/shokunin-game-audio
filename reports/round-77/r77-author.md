# R77 AUTHOR (audio) — source selection, target loss, reader trust, the bound-derived header, the 2 GiB split

Round: 77. Wave: `shokunin-train-20261101-w17`. Repo
`~/Projects/shokunin/audio-shokunin` @ HEAD `503689c` (base for the diff:
`503689c:corpus/fixtures/measure_audio.py`; the working tree was clean
before this seat's edit).

**Seat: AUTHOR. Tracked edits: exactly one file —
`corpus/fixtures/measure_audio.py` (+1552 / −2).** The two deleted lines are
the `mode` and `suffix` ternaries, rewritten prepend-only so every prior
flag's value is unchanged (verified by string assertion, §8). Everything
else is new symbols plus one new `--probe-capture-r77` flag. Receipts and
logs under `corpus/live/r77-author/` (36 KB) and
`corpus/live/runs/*-capture-r77/`. **No commit.**

Toolchain (this host, this session): PipeWire **1.6.8**, pacat
**17.0-98-gb096**, alsa-utils **1.2.16**, ffmpeg **n9.0.1**, SoX_ng
**14.8.0.1**, numpy **2.5.3**, Python **3.14.7**, Linux **7.2.3-arch1-3**.
Host `plazir27`, default sink `…HiFi__SPDIF__sink`, default source
`…HiFi__Line__source`.

---

## Declared move

`--probe-capture-r77`: six entries over the capture-SOURCE frontier the r76
record direction left open — the `stream.capture.sink` fallback lattice, a
destroyed target, the five-witness reader matrix, arecord's open-time header
and device axis, the 2 GiB split sentinel, and the pw-record format axis.
Insertion-only; the r76 folds' guards (`data_actual_zero`, leg totality,
`alsa_busy` carve-out) are inherited, not relaxed.

---

## 0. Headline

| # | frontier | verdict | the single sharpest measured fact |
| --- | --- | --- | --- |
| 1 | source-selection lattice | **LAW CONFIRMED, both witnesses, 11/11 cells** | under the prop, `{source, default, pulse, garbage, auto}` all consume the **default sink's monitor** at rc=1 / 384044 B / finalized / empty stderr — and the capture's own `target.object` names the node you *asked* for in **every** live cell, including the fallback ones |
| 2 | target loss | **NEW, SHARPER THAN THE SCOUT** | the capture does not merely "sustain" — it **re-links to the default sink's monitor**; the artifact is byte-identical (`sha e3a90286b3b54201`) to *that node's own* same-bound control, at exactly 384044 B, rc=1, finalized, and 98–102 % of nominal rate across the loss |
| 3 | reader matrix | **MATRIX PINNED, 12 wounds × 5 witnesses** | `sndfile-info` honest **12/12**; `ffprobe` 11/12; `wave` fails safe (3 rejects) but 3 `declared_echo`; `soxi -s`/`-D` wrong **6/12** — and the mechanism is a **named class**: `declared_echo` (the reader repeats the header's *declared* size, i.e. the caller's own request) |
| 4 | arecord open header | **r76 ROW RE-SCOPED** | the size field is written at OPEN from the leg's own bound: `-d N` → `N×192000` B, `-s S` → `S×4` B, unbounded → `0x80000000`. **The r76 `0x80000000` row is the UNBOUNDED case of this law**, and a bounded KILL over-declares by 32× at w=0.5 s / 5.05× at w=2.5 s |
| 5 | device-dependent TERM | **NOT REPRODUCED (15/15 cells)** | the scout's `alsa_read_eintr` + `placeholder_80000000` on `sysdefault` did not reproduce at any device × wall time; all TERM cells finalize with `aborted_by_signal`. Recorded as a contended-host event, not a per-route partition |
| 6 | split sentinel | **CONFIRMED + CORRECTED** | crossing `0x80000000` data bytes renames `<name>.wav` → `-01`,`-02`,… at rc=0; the requested path **never exists**; `rot-01.wav` is exactly **2147483692 B** = `0x80000000 + 44` — and its finalized field is **`0x7FFFFFFF`**, *not* the `0x80000000` the scout read off a live file |
| 7 | format axis | **LAW CONFIRMED** | 12/12 legal requests honored and reported verbatim (`--channels 6` → tag 65534), 4/4 illegal ones → rc=1, `usage_refusal`, **no file at all** |

**Two falsifications of the scout's pre-measurement** (§4, §5) and **one
strengthening** (§2). All three are recorded with the mechanism, not just
the delta.

---

## 1. FRONTIER 1 — the source-selection lattice (11 cells, two witnesses each)

`pw-record [-P stream.capture.sink=true] --target T -n 96000 --rate 48000
--channels 2 --format s16`, serialized, tone-anchored. The tone is played
to the **current** default sink explicitly (see §7.2 for why).

| leg | `--target` | rc | bytes | consumed node (`pw-link -l`, differenced) | tone | `target.object` = request? |
| --- | --- | --- | --- | --- | --- | --- |
| `prop_default_sink` | default sink | 1 | 384044 | **SPDIF sink** | yes | **yes** |
| `prop_default_sink_monitor` | `<sink>.monitor` | 1 | 384044 | **SPDIF sink** | yes | **yes** |
| `prop_other_sink` | hdmi sink | 1 | 384044 | **hdmi sink** | no (silent) | **yes** |
| `prop_source` | Line **source** | 1 | 384044 | **SPDIF sink** | yes | **yes** |
| `prop_default_token` | `default` | 1 | 384044 | **SPDIF sink** | yes | **yes** |
| `prop_pulse_token` | `pulse` | 1 | 384044 | **SPDIF sink** | yes | **yes** |
| `prop_garbage` | `no_such_node_r77` | 1 | 384044 | **SPDIF sink** | yes | **yes** |
| `prop_auto` | *(none)* | 1 | 384044 | **SPDIF sink** | yes | n/a |
| `noprop_default_sink` | default sink | 1 | **44** | — | — | no node |
| `noprop_default_sink_monitor` | `<sink>.monitor` | 1 | **44** | — | — | no node |
| `noprop_source` | Line source | 1 | 384044 | **Line source** | no (silent) | **yes** |

**The law.** With the prop, a *sink* target is honored; a *source* name,
`default`, `pulse`, garbage and "no target at all" all silently fall back to
the **default sink's monitor** — identical rc, identical byte count,
identical finalized header, empty stderr, no error class. Without the prop,
sink targets fail with `no_target_node` and leave the 44-byte empty wav;
only a real source node resolves.

**Both discriminators hold in the same run, which the scout could not do.**
The scout had `pw-link -l` on one run and content on another (§1.1 vs §1.3);
here every cell carries both. `prop_other_sink` is the control that kills
the "the prop overrides `--target` entirely" hypothesis: it consumes
*hdmi*, not the default, and is silent while the default-monitor cells carry
the tone.

**The provenance trap is now pinned as a per-cell leaf.**
`target_object_is_request = true` in **every live cell**, including all five
fallback cells: the capture node advertises `target.object =
alsa_input.…Line__source` while its `input_FL/FR` ports are fed by
`alsa_output.…SPDIF__sink:monitor_*`. `pw-dump` states intent;
`pw-link -l` states consumption; content states what was actually carried.

---

## 2. FRONTIER 2 — target loss: it **re-links**, it does not merely sustain

A probe-owned `module-null-sink` (`sink_name=r77_loss_sink`) is captured
with `-P stream.capture.sink=true --target r77_loss_sink -n 96000`, then
`pactl unload-module` fires mid-run. Three legs, all with the same frame
bound:

| leg | rc | bytes | finalized | payload all-zero | sha256[:16] |
| --- | --- | --- | --- | --- | --- |
| `baseline` (probe sink alive) | 1 | **384044** | yes | yes | `e3a90286b3b54201` |
| `fallback_control` (default sink monitor) | 1 | **384044** | yes | yes | `e3a90286b3b54201` |
| `after_loss` (probe sink destroyed at 0.6 s) | 1 | **384044** | yes | yes | `e3a90286b3b54201` |

Topology, differenced against a pre-spawn baseline:

```
nodes_before  ['r77_loss_sink']
nodes_after   ['alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink']
unload rc=0   sink_gone True     contended False
```

Wall-clock leg (unbounded, unload at 1.0 s, SIGTERM at 3.0 s):
`102 % → 101 % → 98 %` of nominal across the loss, rc=1, finalized, 573484 B.

**So the honest form of the scout's `sustained_after_target_loss` is
stronger and more useful:** destroying the target does not stall the capture
and does not change rc, the frame count or the finalize — it **re-links the
stream to the default sink's monitor**, and the resulting artifact is
byte-identical to *that* node's own same-bound capture. The scout's
"byte-identical to the no-event baseline" is true here only because both the
probe sink and the SPDIF monitor are digitally silent at that moment; that
is a host-state coincidence, not the law. The probe therefore asserts
against the **fallback node's own control** and records
`sha_match_dead_sink` separately as a coincidence witness — both are
`True` in the clean run.

**Why this matters for any future arm:** a bounded capture of a destroyed
node is *indistinguishable from a healthy capture of the fallback node*.
Neither `rc`, nor the frame count, nor the header, nor the byte count, nor
the payload silence separates them; only node identity does.

---

## 3. FRONTIER 3 — the reader matrix, 12 wounds × 5 witnesses

Unit calibration first (`soxi -s` = **frames**, not interleaved samples:
96000 on a 96000-frame 2ch file; `ffprobe nb_frames` is a packet count and
is not used). Sever at w = 2.5 s.

| wound | rc | bytes | declared | actual | `wave` | `ffprobe` | `soxi -s` | `soxi -D` | `sndfile` |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `pw_record_monitor` TERM | 1 | 471084 | 471040 | 471040 | honest | honest | honest | honest | honest |
| `pw_record_monitor` KILL | −9 | 479276 | **0** | 479232 | **rejects** | honest | **declared_echo** | **declared_echo** | honest |
| `pw_cat_record` TERM | 1 | 479276 | 479232 | 479232 | honest | honest | honest | honest | honest |
| `pw_cat_record` KILL | −9 | 479276 | **0** | 479232 | **rejects** | honest | **declared_echo** | **declared_echo** | honest |
| `parecord_monitor` TERM | 0 | 131116 | 131072 | 131072 | honest | honest | honest | honest | honest |
| `parecord_monitor` KILL | −9 | 131116 | **0** | 131072 | **rejects** | honest | **declared_echo** | **declared_echo** | honest |
| `arecord_bounded` TERM | 1 | 456180 | 456136 | 456136 | honest | honest | honest | honest | honest |
| `arecord_bounded` KILL | −9 | 456044 | **2304000** | 456000 | **declared_echo** | honest | **declared_echo** | **declared_echo** | honest |
| `arecord_unbounded` TERM | 1 | 456184 | 456140 | 456140 | honest | honest | honest | honest | honest |
| `arecord_unbounded` KILL | −9 | 456044 | **2147483648** | 456000 | **declared_echo** | honest | **declared_echo** | **declared_echo** | honest |
| `ffmpeg_pulse` TERM | 255 | 489678 | 489600 | 489600 | honest | honest | honest | honest | honest |
| `ffmpeg_pulse` KILL | −9 | 262144 | **4294967295** | 262066 | **declared_echo** | **inflated** | **underreports** | **underreports** | honest |

Aggregate over the 12 wounds:

```
sndfile  honest 12   wrong 0
ffprobe  honest 11   inflated 1
wave     honest  6   rejects 3   declared_echo 3   -> wrong 3
soxi_s   honest  6   declared_echo 5   underreports 1 -> wrong 6
soxi_D   honest  6   declared_echo 5   underreports 1 -> wrong 6
```

**The new class is `declared_echo`, and it is derived, not asserted:** a
reader answer is `declared_echo` when it equals `data_declared / frame_bytes`
rather than the audio's own frame count. That single class explains both of
the scout's soxi defects with one mechanism:

- `soxi -s`/`-D` → **0** on the `placeholder_8` + `zero` family (a 479276-byte,
  2.5 s capture read as empty) — the declared field is `0`.
- `soxi -s`/`-D` → **2304000 frames / 12.000000 s** on `arecord_bounded_kill`,
  i.e. **the leg's own `-d 12` read back as a measurement**, on 0.375 s of
  audio; **536870912 / 11184.810667 s** on `arecord_unbounded_kill`.
  (The scout's `12173.943583 s` is the same declared frame count divided by
  a **44100** header rate — their leg carried `-f cd`. Same mechanism,
  different header rate.)
- `wave` is honest on every finalized capture and fails **safe** by rejecting
  the `placeholder_8`/`zero` family — but it *accepts and inflates* on an
  over-declared header (`arecord_*_kill`), so "fails safe" is not
  "never wrong".

**Pinned ordering for this host: `sndfile-info` ≳ `ffprobe` > `wave`
(fails safe) > `soxi` (fails loud, in both directions).**

---

## 4. FRONTIER 4 — arecord's open-time header is BOUND-DERIVED (r76 row re-scoped)

| leg | signal @ w | rc | declared | actual | riff field | class |
| --- | --- | --- | --- | --- | --- | --- |
| `-d 3` | KILL 0.5 s | −9 | **576000** | 72000 | `other` | — |
| `-d 5` | KILL 0.5 s | −9 | **960000** | 72000 | `other` | — |
| `-d 12` | KILL 0.5 s | −9 | **2304000** | 72000 | `other` | — |
| `-d 12` | KILL 2.5 s | −9 | **2304000** | 456000 | `other` | — |
| `-s 300000` | KILL 0.5 s | −9 | **1200000** | 72000 | `other` | — |
| *(unbounded)* | KILL 1.0 s | −9 | **2147483648** | 168000 | `other` | — |
| `-d 3` / `-d 5` / `-d 12` / `-s 300000` / *(unbounded)* | TERM | 1 | == actual | == declared | `finalized` | `aborted_by_signal` |

**Law.** arecord writes a size field at OPEN, computed from the leg's own
bound: `-d N` → `N × 192000` data bytes, `-s S` → `S × 4`, unbounded →
`0x80000000` (2 GiB, the split ceiling). TERM finalizes and patches it to
the truth; KILL leaves the *prediction*. The inflation is therefore a
function of the sever wall time, not a consumer constant: `-d 12` at
w=0.5 s over-declares **32×**, at w=2.5 s **5.05×**.

**Consequence for r76's pinned row.** "arecord KILL ⇒ `0x80000000`
placeholder, 8134× inflated" is **correct and is the unbounded case of this
law** — not a consumer shape and not a per-device property. Both are
asserted in the same entry, so the re-scoping cannot silently lose the r76
row: `bound_unbounded_kill` still requires
`data_declared_field == placeholder_80000000`.

### 4.1 Device axis — the scout's `alsa_read_eintr` did **not** reproduce

15 cells: `{hw:0,0, plughw:0,0, sysdefault}` × TERM @ {0.5, 1.0, 1.5, 2.5}
+ KILL @ 2.5, with a 1.0 s settle between legs (an ALSA release is not
immediately re-acquirable — the r76 LOW-7 contention).

| device | TERM @ 0.5 / 1.0 / 1.5 / 2.5 | KILL @ 2.5 |
| --- | --- | --- |
| `hw:0,0` | finalized, `aborted_by_signal` (4/4) | unfinalized |
| `plughw:0,0` | finalized, `aborted_by_signal` (4/4) | unfinalized |
| `sysdefault` | finalized, `aborted_by_signal` (4/4) | unfinalized |

`eintr_cells: []`, `alsa_busy_cells: []`. The scout's per-route partition
(`sysdefault` → `placeholder_80000000` + `read error: Interrupted system
call`) is **not reproducible here in 15/15 cells**, including at their own
wall times. `alsa_read_eintr` is implemented as an r77-local class and the
receipt carries `scout_alsa_read_eintr_reproduced: false` with a note — a
shape that does not reproduce is recorded as not reproduced, never inferred
away. Most likely it was a contended-host event (the scout had a concurrent
seat; §7).

---

## 5. FRONTIER 5 — the 2 GiB split: silent rename, confirmed and corrected

Byte-capped legs: `-D null -f S16_LE -r 48000 -c 2 -t wav -s <frames>`,
in a bounded scratch dir, with a **20 ms watchdog** that SIGKILLs the process
group above 2.4 GB and a 60 s wall cap.

| leg | frames | rc | wall | dir peak | requested path exists | siblings |
| --- | --- | --- | --- | --- | --- | --- |
| undershoot | 536630912 | 0 | 0.38 s | 2146523692 | **yes** | `rot.wav` only |
| crossing | 537110912 | 0 | 0.38 s | 2148443736 | **NO** | `rot-01.wav`, `rot-02.wav` |

```
rot-01.wav  2147483692 B  = 0x80000000 + 44 exactly
            riff/data declared = 0x7FFFFFFF  (finalized member)
rot-02.wav    960044 B    declared 960000   (finalized)
```

**Confirmed:** the split threshold is exactly `0x80000000` data bytes
(`0x80000000 + 44` total), the split is silent (rc=0, empty stderr), and the
requested filename **does not exist** afterwards — the caller's own
`os.path.exists` check reports "no file" for a capture that wrote two
gigabytes into names it never asked for.

**Corrected:** the scout read `data_declared = 0x80000000` off a *live*
(unfinalized) flood file and named it "the 2 GiB split sentinel". It is not:
`0x80000000` is the **open-time placeholder** — it appears on any severed
arecord wav, including a 216 KB one (§4) — while the **finalized** split
member declares **`0x7FFFFFFF`**, the RIFF clamp. The two values coincide
only because the split limit *is* the placeholder's value. A reader that
uses the field value to infer "this file was split" is wrong in both
directions: a KILL'd 216 KB file carries it, and the real split member does
not.

**A detail worth keeping:** because the clamp is one byte short of the data
it describes, a *fully successful, rc=0, 2 GiB* capture produces a member
whose header is internally inconsistent by exactly 1 byte
(`data_finalized: false`, declared 2147483647 vs actual 2147483648) — so the
`data_finalized` leaf cannot be read as a success witness on a split member.

---

## 6. FRONTIER 6 — the pw-record format axis

`-n 4800` is a **frame** bound, so the byte count is rate-invariant.

| request | rc | bytes | reported `fmt` | verdict |
| --- | --- | --- | --- | --- |
| baseline s16/2ch/48 k | 1 | 19244 | `tag 1 / 2 / 48000 / 16` | honored |
| `--format s24 / s32 / f32 / f64 / u8` | 1 | 28844 / 38444 / 38488 / 76888 / 9644 | `1/24`, `1/32`, `3/32`, `3/64`, `1/8` | honored |
| `--rate 8000 / 44100 / 96000 / 192000` | 1 | 19244 each | rate verbatim | honored |
| `--channels 1` | 1 | 9644 | `1/1/48000/16` | honored |
| `--channels 6` | 1 | 57680 | **`tag 65534`** / 6 / 48000 / 16 | honored, EXTENSIBLE |
| `--format bogus` / `--rate 0` / `--channels 0` / `--channels 1 --channel-map FL,FR` | 1 | **no file** | — | **`usage_refusal`** |

Every legal request is honored and reported back verbatim — the source's own
format (`s24le` Line, `s16le` SPDIF monitor, `s32le` Speaker monitor) never
constrains the output. All four refusals are pre-capture, never touch the
device, dump `pw-record [options]` on stderr, and leave **no file at all** —
structurally different from the 44-byte `no_target_node` empty wav, and now
a named class. `f32` is 44 bytes larger than `s32` (38488 vs 38444): an
extra chunk, recorded but not asserted.

---

## 7. Guards, byte discipline, and three witness-integrity rules

### 7.1 Byte discipline (the 36 GB flood is structurally impossible here)
- The split legs use `-s <frames>` + a **20 ms dir-summing watchdog** with a
  hard 2.4 GB SIGKILL and a 60 s wall cap, in `corpus/live/capture-r77-split`
  removed in a `finally`. Peak measured 2.148 GB; the cap never fired.
- Every other `-D null` leg is `-d`/`-s` bounded (r76 rule).
- Scratch footprint at hand-off: **36 KB** (`corpus/live/r77-author/`), plus
  the untracked receipts under `corpus/live/runs/`. No scratch dir survives.

### 7.2 The default sink is not stable across a run (new)
In an earlier run the default sink **moved mid-probe** (SPDIF → Speaker), so
cells 2–8 all reported a different consumed node than the entry-time default.
The law is therefore stated **relationally**: the expectation is *the
default sink as of that cell*, read per cell and recorded as
`default_sink_trace`, with `default_sink_is_stable` as an explicit leaf. The
tone is also played to the current default explicitly. Cause is **not**
proven — the most likely driver is WirePlumber's default-node policy
following an explicitly targeted node, and a concurrent seat's sink churn
was live on the host at the time. Named as an open edge, §9.

### 7.3 A failed capture's link outlives its process (new)
`pw-record --target <sink>.monitor` without the prop exits immediately
(rc=1, 44-byte file, `no_target_node`) **yet its link to the monitor stays in
`pw-link -l` for ~1–2 s** (sampled at 0.2/0.5/1.0/2.0 s: present; at 3.0 s:
gone). A topology witness sampled after the fact would therefore read a
*ghost* as consumption. The probe records `link_after_exit` and
`topology_witness` per cell, and judges the `noprop_*` cells on the file
shape instead.

### 7.4 `pw-link -l` merges concurrent clients — so the probe differences the table
`pw-link -l` lists ports by name, so a **foreign** `pw-record` on the same
host merges into the same `pw-record:input_FL/FR` entries and its link is
indistinguishable from this cell's. Two instruments were added:
- **FL∩FR intersection** — the consumed node must be the producer present on
  *both* channels, which kills a one-sided stale entry.
- **delta vs a pre-spawn baseline** — a foreign client's steady link is
  present in both samples and cancels; only a client that starts or stops
  *inside* the cell survives, and that residual is reported as
  `ambiguous_topology` and named as a **confound** rather than read as a
  measurement.

A concurrent seat was live on this host for the whole window
(`r77-baseline` running `p0_confound.py` / `p7p8_bigwav_counter.py` /
`transient_probe.py` and its own `pw-record` captures; `r77-boundary`
running a `--rate 768000 --channels 64` capture into `/dev/shm`; g2d
`r77-baseline/phase2.sh`). One early run consumed a foreign sink named
`r78a_media_class_override`; the receipt now carries
`contention: {pw_record, fixture_runs, host_is_quiet}` and
`confound_observed` with the foreign node named.

---

## 8. Evidence: determinism, prior rows, scope

**Three clean runs** (`failures: {}` in all three):
`corpus/live/runs/20261014T200120162289Z-capture-r77` (run6),
`…200431704613Z` (run7), `…200645323501Z` (run8).

**Determinism.** Comparing the full receipts across the three runs, with
only the **declared host-drift leaves** excluded, leaves **zero**
differences:

1. the byte count of a capture severed by **wall clock** (±1 frame) and every
   frame-domain reader answer derived from it — TERM *and* KILL legs;
2. sampled rate-window buckets and raw wall times;
3. host state: node-inventory cardinality (a foreign sink appeared between
   runs), the pactl module-id counter, contention counts, raw content peaks.

**Everything else is identical** across the three runs: all `failures`
maps, all 11 lattice cells (consumed node, tone, bytes, class,
`target_object_is_request`), the target-loss topology and all three sha256
values, every reader verdict and the honesty tally, every bound declaration,
the device-axis finalize classes, `eintr_cells`/`alsa_busy_cells`, the split
sizes (exact: 2147483692 / 960044) and all 16 format `fmt` leaves.

**Prior flags untouched.**
- Diff is **+1552 / −2**; the only two deleted lines are the `mode` and
  `suffix` ternaries, rewritten prepend-only (string-asserted).
- `--probe-capture-r76` re-run against the pre-edit baseline receipt
  (`corpus/live/runs/20261014T193039362478Z-capture-r76`, written at
  19:30:39Z — before this seat's first edit, and by a *different* seat, so
  it is independent of this one; the working tree was clean at that time,
  i.e. it is HEAD's `measure_audio.py`): `failures {}` in both; **23/23
  measurement keys identical**; every capture entry's `legs`/`gate` key
  coverage identical (8/8, 7/7, 12/12, 14/14); a **recursive key-structure
  comparison over all 23 entries reports zero divergence**; and every pinned
  deterministic leaf identical — the 12-entry gate `(rc, error_class)` map,
  the `-D null` oracle `192044 B` + `wall_lt_0.5s`, `pwrecord_monitor_bound`
  bytes, `dev_null` bytes, and the whole device-axis `rc` map.
  Receipt: `corpus/live/r77-author/r76-regress.stdout.json`.
- `--probe-failing` still runs and still produces its deliberate failure
  signature.
- The r77 error classes live in a **new r77-local tuple** rather than being
  appended to the shared `_CAPTURE_ERR_CLASSES`: inserting an
  earlier-matching pattern there (`alsa_read_eintr`) could reclassify an r76
  leg's stderr under contention and perturb a committed prior row. Hoisting
  it later is a deliberate diff.

**Scope.** `git status` on tracked paths: only
`M corpus/fixtures/measure_audio.py`. Report: this file. No commit, no push,
no deploy. No LSP server is exposed to this seat's toolset, so the
insertion was hand-edited — recorded per the seat card (it is a pure
insertion of new top-level symbols plus one flag; no rename, reference or
code-action work was required).

---

## 9. Remaining risks and honest edges

- **The fallback trigger is characterised, not explained.** The probe pins
  *which* names fall back and proves it two ways; it does not read
  libpipewire's capture-sink resolution to establish whether the fallback is
  a `node.target` miss that then hits auto-target or an explicit
  `stream.capture.sink` policy. A source read would close it.
- **`@DEFAULT_MONITOR@` is still not separated from the fallback** (the
  scout's §10 edge). The probe does not carry that leg; a cell that first
  moves the default sink and then asks for `@DEFAULT_MONITOR@` would.
- **The default sink moved in one run** (§7.2). The probe now resolves per
  cell and records the trajectory, but the *cause* is unproven and the
  condition under which it moves is not pinned.
- **`alsa_read_eintr` is not reproduced in 15/15 cells.** That is a
  non-reproduction on a contended host, not a disproof: the scout observed
  it, and the r77-local class exists so a future arm can catch it. A
  deliberate load sweep (concurrent captures while TERMing `sysdefault`)
  would decide it.
- **The rate bucket is coarse by construction** (a 4-point window), so
  `after_loss_pct` varies 98–100 % across runs; the assertion floor is 95 %.
  A finer instrument would need a tighter sampler than the 20 ms poll.
- **`sndfile-info` was honest in 12/12 wounds here**, matching the scout's
  11/11 — but both samples are on this host with these 12 wound shapes, and
  the `ffmpeg` KILL wound (`0xFFFFFFFF`) is the one case where it could
  plausibly differ. It is a 12-wound pin, not a portability claim.
- **`ffprobe` inflated exactly once** (`ffmpeg_pulse_kill`, declared
  `0xFFFFFFFF`), the same wound where soxi *under*reports. The two readers
  fail in opposite directions on the same file; the matrix records both.
- **Nothing here is a portability claim.** Every number is a this-host pin
  at the toolchain above.
- The `pw-record`-style `usage_refusal` pattern matches
  `pw-record \[options\]`; a locale change would break it (the same
  brittleness the r76 classes already carry).

---

## 10. Seat accounting

- One tracked file changed: `corpus/fixtures/measure_audio.py`, +1552 / −2,
  one new flag, six new entries, **67 new top-level symbols** (33 constants,
  34 helpers + the 6 entries).
- Six entries, **all clean**: `failures: {}` in the final run and in two
  repeats.
- Byte discipline: hard watchdog on the only unbounded-capable leg; scratch
  36 KB at hand-off; the 2.4 GB cap never fired.
- Falsifications recorded with mechanism, not just delta: the scout's
  `placeholder_80000000`-as-split-sentinel reading (§5), the scout's
  device-dependent TERM partition (§4.1), and the scout's
  "byte-identical to the no-event baseline" framing of target loss (§2,
  strengthened to a re-link measured against the fallback's own control).
- Two new witness-integrity rules added to the instrument itself: the ghost
  link after a failed capture (§7.3) and the concurrent-client merge in
  `pw-link -l` (§7.4), the latter solved by differencing rather than by
  caveat.
- Prior-row stability: r76 regression green on key structure, pinned leaves
  and failures; `--probe-failing` green.
- Not done, and deliberately so: no commit, no push, no judgment, no
  scope beyond the assigned arm.

---

## 11. Receipts

| artifact | path |
| --- | --- |
| clean run 6 (reported) | `corpus/live/runs/20261014T200120162289Z-capture-r77/measurements.json` |
| repeat run 7 | `corpus/live/runs/20261014T200431704613Z-capture-r77/measurements.json` |
| repeat run 8 | `corpus/live/runs/20261014T200645323501Z-capture-r77/measurements.json` |
| r76 regression | `corpus/live/r77-author/r76-regress.stdout.json` |
| run stdout (runs 1–8) | `corpus/live/r77-author/r77-run{1..8}.stdout.json` |

Runs 1–5 are the iteration trail — two crashes (a name typo, a `dict(tuple)`
misuse) and three assertion/confound iterations (a wrong `-n` byte
expectation, a wrong `pw-link -l` parse, the default-sink drift, the device
busy collision, a foreign sink, and the concurrent-client merge) — and are
kept deliberately: they are the evidence for §7.2–§7.4.
