# R77 verifier — capture-SOURCE arm (`--probe-capture-r77`), independent re-derivation

Seat: verifier (LEAF). Repo `~/Projects/shokunin/audio-shokunin`.
Commit under test: **`65790f13e75a69afb2ef2b3ccdb1fd488d778eff`** (r77 work:
capture-source lattice + fallback law + reader matrix).
Fixture under test: `corpus/fixtures/measure_audio.py`, working-tree blob
**`5457376ad5d20031e3ec38a0c52fa0abff135cb5311ba047d507a568c86667b7`** —
identical to `git show HEAD:…` (asserted both ways in §11). The tracked tree
was clean before this seat's work and is clean after it.

Scratch: `corpus/live/r77-verifier/` (232 KB) plus the receipts the fixture
itself writes under `corpus/live/runs/`. No tracked file was modified by
this seat. Toolchain: this host, this session — PipeWire 1.6.8, pacat
17.0-98, alsa-utils 1.2.16, ffmpeg n9.0.1, SoX_ng, numpy/Python 3.14.7,
Linux 7.2.3-arch1-3, host `plazir27`.

**All evidence below was produced by this seat's own legs** (own scripts in
`corpus/live/r77-verifier/v*.py`, own null sink, own reader invocations).
Every leg this seat authored is byte-capped far under 16 MB (`-n` frame
bounds 0.5–2.0 s, ≤ 0.58 MB); the only multi-GB legs in this report are the
ones the canonical probe runs under its own 2.4 GB watchdog, which this seat
did not re-author (§7).

---

## §0 Bottom line

**AGREE with every claim in the brief.** My canonical `--probe-capture-r77`
run reported **`failures: {}`**, exit 0, empty stderr, and all six pinned
classes reproduced on this host in my own shell:

- the `stream.capture.sink` fallback lattice (4 prop cells + 2 noprop
  controls, `pw-link` + content + `target.object` witnesses);
- `sustained_after_target_loss` — with a **real** loss transition this time,
  which the arm's own wall-clock leg does not actually measure (N2);
- the 5-reader matrix (4 wounds read by my own invocations of
  `wave`/`ffprobe`/`soxi -s`/`soxi -D`/`sndfile-info`);
- arecord's bound-derived open header (exact `N × 192000`, 32.0× / 5.05×
  inflation, `0x80000000` on a 164 KB file);
- the 2 GiB split sentinel (exact `0x80000000 + 44`, silent rename,
  finalized member declares `0x7FFFFFFF`);
- the format axis (`usage_refusal` leaves **no file at all**);
- prior-row stability: my fresh `--probe-capture-r76` receipt is
  **leaf-identical** to the committed pre-r77 receipt (1172 leaves, 0 diffs).

Four new findings, all evidenced and none of them a claim falsification:

- **N1** `--probe-capture-r77` is **missing from the mutual-exclusion
  guard**: `--probe-capture-r77 --probe-capture-r76` runs both families and
  writes the result under a receipt labelled `mode: probe-capture-r77`.
- **N2** the arm's **wall-clock loss leg never sees a loss**: the bounded
  leg already unloaded the sink, so its first sample (0.4 s) consumes the
  fallback; its "102 → 101 → 98 %" is a fallback steady rate. My own leg
  reloads the sink and measures a real transition: **100 / 100 / 101 %**.
- **N3** on a contended host the lattice/loss **topology witness degrades to
  a hard failure** instead of the named confound the arm intends: an empty
  `pw-link` delta is not `ambiguous`, and a foreign tone on the fallback
  breaks the byte-identity assertion — while the receipt's own
  `contention.host_is_quiet` leaf already says `False`.
- **N4** the `contention.pw_record` counter (`pgrep -a -f pw-record`)
  counts **command lines**, not clients — it matches other seats' shell
  wrappers and zombies, so `host_is_quiet` is biased `False`.

---

## §1 Claim-by-claim verdicts

| # | Claim (brief) | Verdict | Evidence (this seat's own legs) |
| --- | --- | --- | --- |
| 1 | `--probe-capture-r77` → `failures: {}` on my run | **AGREE** | `20261014T202043466524Z-capture-r77`, `EXIT=0`, stderr 0 B, all six entry `failures` maps empty (§2) |
| 2 | fallback lattice: `capture.sink=true` + garbage/source target → default monitor, `pw-link` witness | **AGREE** | own `v1_lattice.py`: 6 cells, `failures []`; garbage/source/`default`-style cells consume the **SPDIF sink monitor** with the tone; the hdmi control consumes hdmi and is silent; noprop sink → 44 B; noprop source → Line source (§3) |
| 3 | `sustained_after_target_loss` re-derived | **AGREE** | own `v2_loss.py` with **own** null sink `r77v_loss_sink`: rc=1 / 384044 B / finalized on all three bounded legs, `['r77v_loss_sink'] → ['…SPDIF__sink']`, post-loss artifact byte-identical to the fallback's own control (§4) |
| 4 | reader matrix spot-check (3 wounds × own readers; sndfile honest, soxi `declared_echo`, wave inflate/reject) | **AGREE** | own `v3_readers.py`: 4 wounds (3 KILL + 1 TERM control), `failures []`; sndfile honest 4/4; soxi `declared_echo` on both over-declared/zero-declared KILLs; wave rejects the unwritten header and inflates the over-declared one (§5) |
| 5 | arecord open-header law (`-d N` → `N × 192000`) | **AGREE** | own `v4_arecord_header.py`: declared = 576000 / 960000 / 2304000 / 1200000 B exactly; inflation 32.0× (w=0.5 s) and 5.05× (w=2.5 s); unbounded KILL declares `0x80000000` on a **168044 B** file (§6) |
| 6 | split sentinel (byte-capped, `<name>-01.wav`, `0x7FFFFFFF`) | **AGREE** | my canonical receipt: `rot-01.wav` = **2147483692 B** = `0x80000000 + 44`, `riff other`, declared **`0x7FFFFFFF`**, `rot-02.wav` 960044 B, requested path absent, byte cap 2.4 GB never tripped, `rename_is_silent: True` (§7) |
| 7 | format axis `usage_refusal` leaves no file | **AGREE** | own `v5_format.py`: 11 legs, `failures []`; 7 legal legs honored verbatim (incl. `channels_6` → tag 65534, 57680 B); 4 refusals → rc=1, usage dump, **file does not exist** (§8) |
| 8 | prior `--probe-capture-r76` rows stable | **AGREE** | own `v6_prior_r76.py`: fresh run vs committed pre-r77 receipt `20261014T193039362478Z-capture-r76` → **1172 leaves, 0 differences, 0 missing/extra keys, `failures {}` both sides** (§9) |
| 9 | determinism vs the author's own run (claim, not briefed) | **AGREE** | my receipt vs `…T200645323501Z`: 2556 leaves, 140 diffs, **all 140 inside the author's declared drift classes, 0 structural diffs** (§9) |
| N1 | (new) probe-mode exclusivity guard covers r77 | **DISAGREE** | `v7_guard.py` (stubbed entries, zero device side effects): `--probe-capture-r77 --probe-capture-r76` → guard does **not** fire; `--probe-capture-r76 --probe-consumers2-r75` → fires (§10) |
| N2 | (new) the wall-clock leg measures a loss transition | **DISAGREE** | three independent receipts show the fallback node at t=0.4 s, before the leg's own 1.0 s unload (§4.2) |
| N3 | (new) a contended host yields a named confound, not a failure | **DISAGREE** | another seat's run `…T201336507976Z`: 3 hard failures with `contention.host_is_quiet: False` recorded in the same receipt (§10) |
| N4 | (new) `contention.pw_record` counts capture clients | **DISAGREE** | `pgrep -a -f pw-record` matches shell wrappers and `[pw-record] <defunct>` (§10) |

---

## §2 My canonical run

| field | value |
| --- | --- |
| receipt | `corpus/live/runs/20261014T202043466524Z-capture-r77/measurements.json` |
| stdout | `corpus/live/r77-verifier/probe-r77-run1.stdout.json` → `{"failures": {}}` |
| exit / stderr | `EXIT=0`; `probe-r77-run1.stderr.log` = 0 B |
| entry failures | `capture_target_loss_r77_probe`, `capture_source_lattice_r77_probe`, `capture_readers_r77_probe`, `capture_arecord_sever_r77_probe`, `capture_split_sentinel_r77_probe`, `capture_format_axis_r77_probe` — **all `[]`** |
| `contention` (recorded leaf) | `{pw_record: 3, fixture_runs: 6, host_is_quiet: false, own_pid: 3109282}` |
| lattice | 11 cells, 9 live, `default_sink_is_stable: true`, `confound_observed` absent |
| target loss | `['r77_loss_sink'] → ['alsa_output…SPDIF__sink']`, `sha_match_control: true`, `sha_match_dead_sink: true`, `after_loss_pct: 98` |
| split | `rot-01.wav` 2147483692 B / declared 2147483647 / `riff other`; `rot-02.wav` 960044 B; peak dir 2148443736 B, cap never tripped |
| reader tally | `sndfile {honest: 12}`; `wave {honest 6, rejects 3, declared_echo 3}`; `ffprobe {honest 11, inflated 1}`; `soxi_s`/`soxi_D` `{honest 6, declared_echo 5, underreports 1}` |
| arecord device axis | 15 device cells, `eintr_cells: []`, `alsa_busy_cells: []` |
| format | 16 legs; refusals `format_bogus`, `rate_0`, `channels_0`, `channel_map_mismatch` |

**How the quiet window was obtained.** At 20:11:12Z this seat started a
canonical run and discovered a *second* identical `--probe-capture-r77`
process (another seat, started 9 s later) sharing
`corpus/live/capture-r77-split` and the `pw-link` port names. This seat
**killed its own run only** (never the other seat's), waited for the host to
drain, and fired again at 20:18:5xZ. The reported run is the clean one; the
aborted attempt left no receipt. Note that even the clean run records
`fixture_runs: 6` — non-capture seats were live throughout — and still
passed, which pins the real contaminant as **a concurrent `pw-record`
client or a concurrent split leg**, not "any other seat".

---

## §3 Claim 1 — the fallback lattice, re-derived (`v1_lattice.py`)

Own implementation (no import of the fixture), `-n 96000` frames = 2.0 s,
tone anchor `pw-cat -p --target <current default sink>`, topology sampled at
t=0.8 s *inside* the capture, differenced against a pre-spawn `pw-link -l`
snapshot; content from my own RIFF walk; `target.object` from `pw-dump`.

| cell | rc | bytes | consumed (`pw-link`, both channels) | tone (peak) | `target.object` = request? |
| --- | --- | --- | --- | --- | --- |
| `prop_default_sink` | 1 | 384044 | **SPDIF sink** | yes (4124) | **yes** |
| `prop_garbage` (`no_such_node_v77`) | 1 | 384044 | **SPDIF sink** | yes (4124) | **yes** |
| `prop_source` (Line **source** name) | 1 | 384044 | **SPDIF sink** | yes (4124) | **yes** |
| `prop_other_sink` (hdmi, control) | 1 | 384044 | **hdmi-stereo** | no (0) | **yes** |
| `noprop_default_sink` | 1 | **44** | — | — | no |
| `noprop_source` | 1 | 384044 | **Line source** | no (0) | **yes** |

`failures: []`. The law reproduces exactly as the author states it: with the
prop, a sink target is honored; a source name, `default`, `pulse` and
garbage all fall back to the default sink's monitor at the same rc / byte
count / finalized header; without the prop a sink target is the 44-byte
empty wav with `no target node available` (my own stderr capture) and only a
real source node resolves. The **provenance trap is reproduced**: in every
live cell, including all three fallback cells, the capture node advertises
`target.object` = the node *asked for* while its input ports are fed by the
SPDIF monitor. Peak 4124 is identical to the author's run8 leaf, and the
hdmi control was digitally silent in my window (measured independently:
peak 0 over 24000 frames, §10/N6 note).

*Instrument note (own bug, recorded):* my first lattice attempt used a 0.5 s
capture and sampled the topology at 0.7 s — after the capture had exited —
and reported `consumed_nodes: []` for every cell. That is a timing artifact,
not an absence; the script now records `live_at_sample` and refuses to read
an empty witness from a dead sample. No such claim is made in this report
from that attempt.

---

## §4 Claim 2 — target loss (`v2_loss.py`)

### 4.1 Bounded legs, verifier-owned sink

Own null sink `r77v_loss_sink` (own `module-null-sink` load, id 536870917),
`-n 96000` frames, unload at 0.6 s mid-run:

| leg | rc | bytes | declared | sha256[:16] | wall |
| --- | --- | --- | --- | --- | --- |
| `baseline` (sink alive) | 1 | 384044 | 384000 | `e3a90286b3b54201` | 2.03 s |
| `fallback_control` (SPDIF, same bound) | 1 | 384044 | 384000 | `e3a90286b3b54201` | 2.03 s |
| `after_loss` (sink destroyed at 0.6 s) | 1 | 384044 | 384000 | `e3a90286b3b54201` | 2.02 s |

Topology: `['r77v_loss_sink'] → ['alsa_output…SPDIF__sink']`;
`sha_match_control: true`; `sha_match_dead_sink: true`; sink gone after the
unload (`sink_gone: true`, verified from `pactl list sinks`). `failures: []`.
This is the author's §2 claim — *re-link*, not mere sustain — reproduced with
a sink the author's probe never touched.

### 4.2 The arm's wall-clock leg does not measure a loss (**N2**)

The arm's entry loads the null sink **once**, and the bounded `after_loss`
leg unloads it at 0.6 s. The wall leg then runs with `unload_after_s=1.0`,
but by then `r77_loss_sink` **no longer exists**: its own first sample
already consumes the fallback, and its "unload" is
`pactl unload-module ""` (the id lookup returns `""`), which returns **rc=0**
with `Failed to unload module: Module  not loaded` — a no-op that even a
recorded `unloaded` leaf could not distinguish, and the wall entry does not
record one at all.

Evidence, three independent receipts (author run8, this seat's run, another
seat's run):

| receipt | wall sample @0.4 s | wall rates |
| --- | --- | --- |
| `…T200645323501Z` (author) | `['…SPDIF__sink']` | 102 / 98 / 100 |
| `…T202043466524Z` (this seat) | `['…SPDIF__sink']` | 102 / 101 / 98 |
| `…T201650898147Z` (other seat) | `['…SPDIF__sink']` | 102 / 101 / 98 |

So "102 % → 101 % → 98 % of nominal across the loss" (author §2) is a
measurement of the **fallback's steady rate**, not of a post-loss rate — the
loss happened before the leg started. The bounded legs are unaffected and do
measure the transition.

**My own wall leg reloads the sink first**, so it measures a real loss
(unload at 1.0 s, SIGTERM at 3.0 s, unbounded):

| t (s) | bytes | consumed |
| --- | --- | --- |
| 0.4 | 77868 | **`r77v_loss_sink`** |
| 1.21 | 233516 | `…SPDIF__sink` (fallback) |
| 1.81 | 348204 | `…SPDIF__sink` |
| 2.8 | 540716 | `…SPDIF__sink` |

Rates **100 / 100 / 101 %** of nominal; rc=1; header finalized
(declared 577536 = actual). The unload is real (`module 536870917, rc 0,
stderr ''`). **The sustained-rate claim survives a genuine transition** — it
is now measured rather than inferred.

---

## §5 Claim 3 — reader matrix, spot-checked (`v3_readers.py`)

Own reader invocations on four wounds (KILL at 2.5 s + one TERM control);
`honest`/`declared` frames derived from my own RIFF walk, never from a
reader. `failures: []`.

| wound | rc | bytes | declared B | wave | soxi `-s` | sndfile | ffprobe |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `pw_record_kill` | −9 | 479276 | **0** | **rejects** | **declared_echo (0)** | honest 119808 | honest |
| `pw_record_term` | 1 | 479276 | 479232 | honest | honest | honest | honest |
| `arecord_bounded_kill` (`-d 12`) | −9 | 456044 | **2304000** | **declared_echo (576000)** | **declared_echo (576000)** | honest 114000 | honest |
| `ffmpeg_pulse_kill` | −9 | 262144 | **0xFFFFFFFF** | **declared_echo (1073741823)** | **underreports (0)** | honest 65516 | inflated 65517 |

Every value matches the arm's own receipt leaf-for-leaf
(`479276 / 119808`, `456044 / 114000`, `262144 / 65516`), and the classes
match its tally: `sndfile` honest on every wound; `soxi` repeats the header's
*declared* size in both directions (0 on the unwritten header, 576000 on the
`-d 12` prediction, **0** on the `0xFFFFFFFF` wound where it under-reports);
`wave` fails safe by rejecting the unwritten header but accepts and inflates
the over-declared one. `declared_echo` is a real, derived class, not a label
of convenience.

---

## §6 Claim 4 — arecord's open header (`v4_arecord_header.py`)

`-D hw:0,0`, paced, KILL/TERM at the stated wall times, 1 s ALSA settle
between legs. `failures: []`.

| leg | sever | rc | declared (data) | actual | inflation | header |
| --- | --- | --- | --- | --- | --- | --- |
| `-d 3` KILL | 0.5 s | −9 | **576000** = 3×192000 | 72000 | 8.0× | unfinalized |
| `-d 5` KILL | 0.5 s | −9 | **960000** = 5×192000 | 72000 | 13.3× | unfinalized |
| `-d 12` KILL | 0.5 s | −9 | **2304000** = 12×192000 | 72000 | **32.0×** | unfinalized |
| `-d 12` KILL | 2.5 s | −9 | **2304000** | 456000 | **5.05×** | unfinalized |
| `-s 300000` KILL | 0.5 s | −9 | **1200000** = 300000×4 | 72000 | 16.7× | unfinalized |
| *(unbounded)* KILL | 1.0 s | −9 | **2147483648 = 0x80000000** | 168000 | — | unfinalized |
| `-d 3` TERM | 0.5 s | 1 | 72136 | 72136 | 1.0× | **finalized** |

The law holds exactly: the size field is written at OPEN from the leg's own
bound; TERM patches it to truth; KILL leaves the prediction, whose inflation
is a function of sever wall time (32.0× vs 5.05× on the same `-d 12` bound —
the author's numbers, reproduced to the digit). Byte counts match the
author's table (72000 / 456000 / 168000 actual).

**The cheap falsifier of the scout's reading:** the unbounded KILL declares
`0x80000000` on a **168044-byte** file. `0x80000000` is therefore the
open-time placeholder on *any* severed arecord wav — it is not, by itself,
a "2 GiB split sentinel" (see §7 for the finalized member's value). Note for
future arms: this leaf is the **data chunk's** size field
(`data_declared`), not the RIFF size field — my first pass asserted the RIFF
field and got `other`; the arm's `data_declared_field` leaf is the correct
one and the arm reads it correctly.

---

## §7 Claim 5 — the 2 GiB split, from my own canonical receipt

Byte discipline: the brief caps this seat's authored legs at < 16 MB, so I
did **not** author a second 2.1 GB leg; the split legs are the canonical
probe's, run by me at 20:18–20:20Z under its own 2.4 GB watchdog + 60 s wall
cap, and the claim is re-derived from *my* receipt's leaves:

| leaf | my run | author run8 |
| --- | --- | --- |
| undershoot requested path exists | **true**, siblings `['rot.wav']` (2146523692 B) | same shape |
| crossing requested path exists | **false** | false |
| `rot-01.wav` bytes | **2147483692 = 0x80000000 + 44** | identical |
| `rot-01.wav` declared | **2147483647 = 0x7FFFFFFF**, `riff other` | identical |
| `rot-02.wav` | 960044 B, finalized, declared 960000 | identical |
| dir peak / cap | 2148443736 B / 2400000000 B, **cap never tripped** | 2148443736 B |
| `rename_is_silent` | **true** (rc=0, no requested path, siblings present) | true |

Independent corroboration of the *correction*: my §6 `0x80000000` witness is
a 164 KB KILL'd file, and the finalized split member declares `0x7FFFFFFF` —
the two values coincide only because the split limit *is* the placeholder's
value, exactly as the author argues. The 1-byte internal inconsistency the
author flags is visible in my receipt too: `rot-01.wav` declares 2147483647
over 2147483648 actual bytes (`data_finalized: false` on a fully successful
rc=0 capture).

---

## §8 Claim 6 — format axis (`v5_format.py`)

`-n 4800` frames, target = the default **source**. `failures: []`.

| request | rc | bytes | reported `fmt` |
| --- | --- | --- | --- |
| baseline s16/2ch/48k | 1 | **19244** | tag 1 / 2 / 48000 / 16 |
| `--format s24` | 1 | 28844 | tag 1 / 24 |
| `--format f32` | 1 | 38488 | tag 3 / 32 |
| `--format u8` | 1 | 9644 | tag 1 / 8 |
| `--rate 192000` | 1 | 19244 | rate 192000 verbatim |
| `--channels 1` | 1 | 9644 | 1 ch |
| `--channels 6` | 1 | 57680 | **tag 65534 (EXTENSIBLE)** / 6 ch |
| `--format bogus` / `--rate 0` / `--channels 0` / `--channels 1 --channel-map FL,FR` | 1 | **no file** | usage dump on stderr |

Every byte count is identical to the author's table. The four refusals are
pre-capture: rc=1, `pw-record [options]` usage text, and `exists: false` on
my own `os.path.exists` check — structurally different from the 44-byte
`no_target_node` empty wav.

---

## §9 Prior rows and determinism

**r76 rows (`v6_prior_r76.py`).** Fresh `--probe-capture-r76` run
(`20261014T202511898134Z-capture-r76`, exit 0, `failures {}`) compared
leaf-by-leaf against the committed **pre-r77** receipt
`20261014T193039362478Z-capture-r76` (written 19:30:39Z by a different seat
on the pre-edit fixture): **1172 leaves on both sides, 0 differing leaves,
0 keys only-in-either, no failure on either side.** This is a stronger
statement than the author's own §8 (which compared 23 measurement keys and a
recursive key structure); it is a full leaf identity.

**Determinism vs the author's run8.** My receipt vs
`…T200645323501Z-capture-r77`: 2556 leaves, **140 differing leaves**, and
every one falls inside the author's declared drift classes — 117 on
wall-clock-severed arecord legs, 13 on wall-clock-severed reader wounds, 10
sampled/host-state leaves (rate windows, `contention.*`, `own_pid`,
`nonzero_frac`, split `wall_s`). **0 structural diffs**: no `exit_code`,
`error_class`, `failures`, `data_finalized`, `verdict`, `riff_size_field` or
`data_declared_field` leaf differs anywhere. All six entries' pinned
classes, the 11 lattice cells, the loss topology and all three sha256 values,
the 12-wound reader verdicts and the honesty tally, the split sizes and the
16 format `fmt` leaves are identical.

**Static claim: prior flags untouched.** `git diff --numstat 503689c
65790f1 -- corpus/fixtures/measure_audio.py` → **1552 / 2**; the only two
deleted lines are the `mode` and `suffix` ternary lines. Parsing both
ternaries from both blobs: 120 pre-existing flags, **0 changed values**,
exactly one new flag (`probe_capture_r77` → `probe-capture-r77` /
`-capture-r77`). AGREE.

---

## §10 New findings

**N1 — the new probe mode is outside the mutual-exclusion guard.** The
argparse guard is `if sum([…, args.probe_capture_r76]) > 1:
parser.error("choose one probe mode")`; `probe_capture_r77` is **absent from
that sum** (verified statically and at runtime). `v7_guard.py` imports the
fixture with every capture entry stubbed (zero device side effects) and
calls `main()`:

| flags | guard fired? |
| --- | --- |
| `--probe-capture-r76 --probe-consumers2-r75` | **yes** (`SystemExit 2`) |
| `--probe-capture-r77 --probe-capture-r76` | **no** — main ran to completion |
| `--probe-capture-r77 --probe-consumers2-r75` | **no** |
| `--probe-capture-r77` | n/a |

The consequence is visible in the stub receipt
(`v7_guard_receipt_witness.json`): a combined run writes **12 capture
entries** under `mode: probe-capture-r77` / suffix `-capture-r77`, i.e. the
r76 family's rows land in a receipt labelled as r77. Corroboration: the
r77-baseline seat's own runtime check
(`corpus/live/r77-baseline/exclusivity-check.txt`) reports `rc=124` (ran to
timeout) for both r77-involving pairs. Fix is a one-token diff (add
`args.probe_capture_r77` to the sum); it is not mine to make.

**N2 — the wall-clock loss leg measures no loss.** §4.2.

**N3 — contended-host failure vs confound.** Another seat's run
`20261014T201336507976Z-capture-r77` reported three failures:

```
lattice prop_auto: expected consumption of default_sink (…SPDIF__sink), got [] (target_arg=None)
target loss: expected the capture to consume the probe sink before the unload and …SPDIF__sink after, got ['r77_loss_sink'] -> []
target loss: the post-loss artifact is NOT byte-identical to the FALLBACK node's own same-bound control
```

and the same receipt records `contention: {pw_record: 1, fixture_runs: 6,
host_is_quiet: false}`. The mechanism is the differencing itself: a foreign
`pw-record` client already linked to the *same* node cancels this capture's
own link (`before ∩ during` identical ⇒ empty delta), and
`_capture_r77_link_delta`'s `ambiguous` flag only fires on **>1** nodes, so
an empty delta is read as a hard mismatch — `foreign_links_ignored: true`
and `ambiguous_topology: false` are in the same cell. The content witness in
that very cell shows the fallback *was* consumed (`peak 4457`,
`carries_tone: true`), i.e. the law held and only the topology witness was
blinded. Likewise `sha_match_control` fails when the fallback node's content
is not steady across legs (that run's `fallback_control`/`after_loss` shas
differ and `all_zero_payload: false` — a foreign tone was playing to the
default sink). The arm's confound taxonomy covers ">1 node" but not "0
nodes" nor "non-silent fallback"; a `host_is_quiet: false` carve-out would
name both. This matters because the arm's §7.4 promises exactly the opposite
("reported as `ambiguous_topology` and named as a confound rather than read
as a measurement") — true for the ambiguous residual, false for the
cancelled one.

**Controlled confirmation (`v8_confound.py`, this seat).** I set the
mechanism up deliberately: one foreign `pw-record` client linked to the
default sink monitor (raw table before the cell:
`['alsa_output…SPDIF__sink']`), then one ordinary cell targeting the same
node.

| witness | value |
| --- | --- |
| raw `pw-link` table, before the cell | `['alsa_output…SPDIF__sink']` |
| cell's **differenced** consumed nodes | **`[]`** (empty) |
| cell's content witness | **tone, peak 4124**, full 384044 B capture |
| cell `ambiguous_topology` | `false` |

So a real consumption is invisible to the differenced witness and reported
as an empty set — the exact leaf the arm asserts against. This is a
*reproducible* contended-host shape, not a one-off host accident.

**Dispatched L2 probe (this seat is the frozen probeParent; exactly one
`ufo-labrat`, read-only).** The probe was asked to re-derive the hypothesis
above with its own commands. It returned **INCONCLUSIVE — probe not
executed**: its substrate session exposed only read-only file tools
(`find_file_by_name`, `grep`, `read`) and no shell/exec surface, so it could
run none of `pactl`/`pw-record`/`pw-link`/`pw-cat`/`pw-dump` and reported the
capability blocker rather than a fabricated measurement (nothing started,
nothing written, repo untouched). Recorded as a **probe-unavailability**,
not as a falsification: the empirical evidence for N3 in this report is the
controlled `v8_confound.py` experiment above, which I ran myself.

**N4 — `contention.pw_record` counts command lines, not clients.**
`pgrep -a -f pw-record` matches any process whose command line contains the
string: in my check it matched a sibling seat's `bash -c … pw-record …`
wrapper, this seat's own shell line, and `[pw-record] <defunct>`. So the
leaf is an upper bound on clients and `host_is_quiet` is biased `False` —
my clean run records `pw_record: 3` while the lattice found no confound.
`pgrep -x pw-record` (or `-f` plus a `/proc/<pid>/exe` check) would measure
what the leaf claims.

**N5 (hygiene, this seat).** `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`
is a **tracked** file; importing the fixture (as any verifier will, to test
a guard) rewrites it (157038 → 412393 bytes here). I restored it with
`git checkout --` and the tracked tree is clean again. Worth knowing before
the next seat's `git status` is read as a diff.

---

## §11 Receipts (this seat)

| artifact | path |
| --- | --- |
| canonical run stdout / stderr / exit | `corpus/live/r77-verifier/probe-r77-run{1}.std{out.json,err.log}`, `probe-r77-run1.exit` |
| canonical receipt | `corpus/live/runs/20261014T202043466524Z-capture-r77/measurements.json` |
| claim checks vs that receipt | `corpus/live/r77-verifier/v0_claims.json` (`v0_receipt_checks.py`) |
| lattice (own legs) | `v1_lattice.json` (`v1_lattice.py`) |
| target loss (own sink, real transition) | `v2_loss.json` (`v2_loss.py`) |
| reader matrix (own readers) | `v3_readers.json` (`v3_readers.py`) |
| arecord open header | `v4_arecord_header.json` (`v4_arecord_header.py`) |
| format axis | `v5_format.json` (`v5_format.py`) |
| prior r76 rows | `v6_prior_r76.json` + `v6_r76.stdout.json` (`v6_prior_r76.py`); new receipt `corpus/live/runs/20261014T202511898134Z-capture-r76` |
| probe-mode guard | `v7_guard.json`, `v7_guard_receipt_witness.json` (`v7_guard.py`) |
| N3 mechanism (controlled) | `v8_confound.json` (`v8_confound.py`) |
| fixture identity | working tree `sha256sum` == `git show HEAD:…` = `5457376ad5d2…67b7` |

Byte discipline and hygiene at hand-off: authored legs ≤ 0.58 MB each
(largest: the 3 s wall leg, 577580 B); scratch 232 KB; the probe's split
scratch `corpus/live/capture-r77-split` removed; no verifier null sink left
loaded (`pactl list short sinks | grep r77` empty); no stray process of this
seat's (the only live capture process during the hand-off check belonged to
a sibling seat, scratch `/tmp/capture-r77-*`); the three stub receipts my
guard check wrote into `corpus/live/runs/` were removed; tracked tree clean.

---

## §12 Remaining risks and honest edges

- **The split sentinel rests on my canonical run, not on a second 2.1 GB leg
  of my own** — a deliberate consequence of the < 16 MB byte cap. The claim's
  *distinguishing* half is independently re-derived cheaply (§6/§7).
- **N2's consequence for the record:** the author's §2 sentence "102 % →
  101 % → 98 % of nominal across the loss" is not supported by the leg it
  cites. The claim itself is not wrong — my reloaded wall leg measures
  100/100/101 % through a real transition — but the receipt's wall entry
  should either reload the sink or record that its unload was a no-op.
- **N3 is a contention-taxonomy gap, not a measurement error**: on a quiet
  host the arm is deterministic (three runs here, mine included); the
  failure carrier simply fires on host state the receipt already knows about.
- **`alsa_read_eintr` is still not reproduced** — my canonical run's
  `eintr_cells: []` across the same 15 device cells, consistent with the
  author's non-reproduction; a deliberate load sweep remains the deciding
  experiment.
- **Every number here is a this-host pin** (toolchain above), including the
  reader classes; the `0xFFFFFFFF` ffmpeg wound is the one case where
  `sndfile-info` could plausibly differ elsewhere.
- **`usage_refusal` pattern brittleness** (a locale-dependent
  `pw-record [options]` match) is inherited from the r76 classes, as the
  author notes; my v5 legs match on the same string.
