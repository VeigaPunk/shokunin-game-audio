# r81 AUTHOR — the GStreamer↔PipeWire lattice armed into the lane harness

host: devin (`Linux plazir27 7.2.3-arch1-3`). Seat: author (r81). Scope: arm
the r81 scout's seven pinned frontier claims
(`reports/round-81/r81-scout.md` §0; receipts `corpus/live/r81-scout/`) into
`corpus/fixtures/measure_audio.py` as a **new parallel ledger family,
insertion-only**, run it twice green, replay the full prior battery twice
with prior rows byte-stable, and document evidence + corrections. **No
commit, no push.**

Toolchain (receipt-verified): GStreamer **1.28.6**, gst-plugin-pipewire
**1.6.8** (the gst plugin tracks PipeWire's version), PipeWire **1.6.8**,
libpulse **17.0+r98** (protocol 35), WirePlumber **0.5.17**, Python 3.14.7,
NumPy 2.5.3, `gst-launch-1.0`/`gst-inspect-1.0` under `/usr/bin/`.

## 1. Declared move

`--probe-gst-r81`: **seven entries, 55 legs**, one per pinned claim:

| entry (measurements key) | legs | claim |
| --- | --- | --- |
| `gst_element_lattice_r81_probe` | 15 | (1) availability lattice, two reps per element |
| `gst_naming_r81_probe` | 5 | (2) node/Client naming crossover |
| `gst_routing_r81_probe` | 12 | (3) routing vectors, precedence, envs, capture prop gate |
| `gst_pulse_axis_r81_probe` | 6 | (4) `device=` axis + direction split |
| `gst_target_loss_r81_probe` | 7 | (5) playback re-links / capture freezes |
| `gst_exit_classes_r81_probe` | 7 | (6) parse vs runtime refusal, pulsesrc outlier |
| `gst_autodetect_r81_probe` | 3 | (7) autodetect backend + ALSA control |

Harness anchors: family block `measure_audio.py:12543`–`14203`;
constants `:12592`–`12610`; error-class tuple `:12615` (separate table —
never prepended into the shared `_CAPTURE_ERR_CLASSES`, same rule as
r77/r78); runner `_gst_r81_leg` `:12919`; entries `:13030`/`:13151`/
`:13306`/`:13612`/`:13765`/`:14010`/`:14125`; wiring `:14326` (flag),
`:14334` (mutex), `:15216` (mode), `:15237` (suffix), `:14624` (dispatch).
Tracked diff: **+1 686/−3** (the −3 are the three wiring lines — mutex
sum, mode ternary, suffix ternary — each rewritten as a prepend-only
ternary; every other byte is insertion). `python3 -m py_compile` clean;
the `__pycache__` .pyc was `git checkout`-ed back so the tracked diff is
the source edit alone.

**Contention (mandatory, inherited and tightened):** every routing leg
targets the seat-owned null sink `gst_r81_auth_<pid>` or is read-only;
stream/node names are `gst_r81_<pid>_*`; **every unload goes by the
name-verified index** — `pactl list modules short` is re-read immediately
before firing and only the index whose *argument string* carries
`sink_name=gst_r81_auth_<pid>` is unloaded (`_gst_r81_unload_own`,
`:12828`; a bare captured index is never trusted — indices recycle LIFO,
the scout's §10/r80-class incident); `pactl set-default-sink`/
`set-default-source` are never invoked; every capture leg is
**triple-bounded** in the same loop that owns the process group — element
bound (`num-buffers`/`-n`) inside argv + wall cap + byte cap
(`_gst_r81_leg`, `:12919`; no watchdog thread — the r77 flood lesson);
graph identity is by **object id** with the client join
`node.client.id → Client.application.process.id` — never by name (two
gst pipelines both publish `gst-launch-1.0`).

**Two consecutive formal runs** on byte-identical frozen code:
`20261015T171719214164Z-gst-r81` and `20261015T171856751772Z-gst-r81`,
both `{"receipt": …, "failures": {}}`, exit 0, `sinks_gone`/`own_nodes_after`
clean in every loaded entry. Run-to-run stability (`percase.py`,
`corpus/live/r81-author/stability-r81-runsAB.txt`): **0 semantic diffs
over 6 835 leaf paths** (5 569 exact / 710 volatile / 556 jitter — jitter
is object ids, wall times, sample counts; normalized-key collisions: 0).

Receipts: `corpus/live/runs/20261015T171719214164Z-gst-r81/measurements.json`
(run 1, sha `ebd93c36…`) and
`corpus/live/runs/20261015T171856751772Z-gst-r81/measurements.json`
(run 2, sha `aba69d9e…`); copies pinned under
`corpus/live/r81-author/gst-r81-runs/`. All quoted values below are run-2
verbatim.

## 2. Headline — the seven claims, re-measured

All seven claims **CONFIRMED as laws on this host** — each with the graph
witness, not just rc.

### Claim 1 — element availability lattice → `gst_element_lattice_r81_probe`

`gst-inspect-1.0` × 2 reps per element, all rows stable:

| element | rc | klass | plugin | version |
| --- | --- | --- | --- | --- |
| `pipewiresink` | 0 | `Sink/Audio/Video` | `libgstpipewire.so` | **1.6.8** |
| `pipewiresrc` | 0 | `Source/Audio/Video` | `libgstpipewire.so` | **1.6.8** |
| `pulsesink` | 0 | `Sink/Audio` | `libgstpulseaudio.so` | 1.28.6 |
| `pulsesrc` | 0 | `Source/Audio` | `libgstpulseaudio.so` | 1.28.6 |
| `autoaudiosink` | 0 | `Sink/Audio` | `libgstautodetect.so` | 1.28.6 |
| `autoaudiosrc` | 0 | `Source/Audio` | `libgstautodetect.so` | 1.28.6 |
| `alsasink`/`alsasrc` | 0 | `Sink`/`Source/Audio` | `libgstalsa.so` | 1.28.6 |
| `audiotestsrc` | 0 | `Source/Audio` | `libgstaudiotestsrc.so` | 1.28.6 |
| `wavenc` | 0 | **`Codec/Muxer/Audio`** | `libgstwavenc.so` | 1.28.6 |
| `filesink` | 0 | `Sink/File` | `libgstcoreelements.so` | 1.28.6 |
| `fakesink` | 0 | `Sink` | `libgstcoreelements.so` | 1.28.6 |
| `openalsink` | **255** | — | — | `No such element or plugin 'openalsink'` |
| `nosuchelement_r81_xyz` | **255** | — | — | same first line (control) |
| plugin `pipewire` | 0 | — | — | **1.6.8** |

The rc asymmetry the scout pinned is armed too: the *same* absence is
**255 through `gst-inspect-1.0`** (this entry) and **1 through
`gst-launch`'s parser** (`e1_missing_element` in claim 6 — never read one
tool's rc as the other's).

### Claim 2 — naming crossover → `gst_naming_r81_probe`

All legs `audiotestsrc wave=silence num-buffers=96 → S16LE →
pipewiresink target-object=<ns>`; our node resolved by client object id:

| leg | node.name | node.description / media.name | pw Client name |
| --- | --- | --- | --- |
| n0_bare | `gst-launch-1.0` | `gst-launch-1.0` / `gst-launch-1.0` | `gst-launch-1.0` |
| n1 (`stream-properties node.name=`) | `gst_r81_…_snk` | `gst-launch-1.0` / `gst-launch-1.0` | `gst-launch-1.0` |
| n2 (`client-name=`) | **`gst_r81_…_client`** | **`gst_r81_…_client` / `gst_r81_…_client`** | `gst-launch-1.0` |
| n3 (`client-properties application.name=`) | `gst-launch-1.0` | `gst-launch-1.0` / `gst-launch-1.0` | **`gst_r81_…_app`** |
| n4 (capture, `client-name=`) | `gst_r81_…_src_client` | `gst_r81_…_src_client` ×3 | `gst-launch-1.0` |

The crossover is verbatim: `client-name=` moves all three *node* strings
while the Client keeps `gst-launch-1.0`; `client-properties` moves the
*Client* while the node keeps `gst-launch-1.0` on all three strings.
Also measured (receipt detail): gst never sets `client.name` — the Client
name is carried on `application.name`; `application.name` is **absent**
from a native-protocol node's props (n0 asserts it `None`).

### Claim 3 — routing vectors → `gst_routing_r81_probe`

| leg | vector | node.target / target.object | link | rc |
| --- | --- | --- | --- | --- |
| r1 | `target-object=<ns>` | `<ns>` / `<ns>` — **two-key write** | →`<ns>` | 0 |
| r2 | `stream-properties node.target=<ns>` | `<ns>` / absent | →`<ns>` | 0 |
| r3 | `stream-properties target.object=<ns>` | absent / `<ns>` | →`<ns>` | 0 |
| r4 | `target-object=<bogus>` | `<bogus>` / `<bogus>` verbatim | →**default** (silent) | 0 |
| r5 | `target-object=<ns>` + `props,target.object=<bogus>` | `<ns>` / `<ns>` | →`<ns>` | 0 |
| r6 | env `PIPEWIRE_PROPS={ node.name=<tag> node.target=<ns> }` | `<ns>` / absent, node renamed `<tag>` | →`<ns>` | 0 |
| r7 | env `PIPEWIRE_NODE=<ns>` | absent / `<ns>` (lands as target.object) | →`<ns>` | 0 |
| r8 | `stream-properties node.autoconnect=false` | `<ns>` / `<ns>`; autoconnect = **STRING `"FALSE"`** | **unlinked** to wallcap | −9 |
| c0 | `pipewiresrc target-object=<ns>` **no prop** | — | refused | **255 `target not found`** + 0 B |
| c1 | + `props,stream.capture.sink=true` | capture prop = STRING `"TRUE"` | `<ns>` monitor → in | 0, finalized wav, **tag tone landed** |
| c4 | `target-object=<ns>.monitor` + prop | — | **default** monitor (r77 residual) | 0 |
| c7 | prop-only `stream.capture.sink=true,node.target=<ns>` | prop-only | `<ns>` monitor → in | 0 |

**Precedence both ways pinned with authorities:** on gst elements the
`target-object=` **element property overwrites** `stream-properties`
(r5) — the inverse of r78's `-P`-beats-`--target` law on pw-cat
(`corpus/live/r78-*` / fixture `playback_*_r78` family). Both laws stand
as client-specific facts, neither generalizes to "props always win" or
"the flag always wins".

### Claim 4 — `pulsesink device=` axis → `gst_pulse_axis_r81_probe`

| leg | input | rc | target.object on node | link |
| --- | --- | --- | --- | --- |
| p1 | `device=<ns>` | 0 | `<ns>` | →`<ns>` |
| p2 | `device=<bogus>` | **0** | `<bogus>` **verbatim** | →**default** (stderr silent) |
| p3 | `PULSE_SINK=<ns>` bare | 0 | `<ns>` | →`<ns>` |
| p4 | `PULSE_SINK=<ns>` + `device=<default>` | 0 | `<default>` | →`<default>` (**device wins**) |
| p5 | `server=unix:/nonexistent-r81` | **255** | — | `Connection refused` + `Failed to set pipeline to PAUSED` |
| p6 | `pulsesrc device=<bogus>` | **1** | — | `Failed to connect stream: No such entity` + **0-byte artifact** |

`device=` is a name handed to the *server*, not a client-side bind: the
client writes it into `target.object` verbatim, WirePlumber resolves —
playback on a bogus name is rc=0 + silent fallback to the current
default; the record direction refuses the same input (rc=1). All pulse
nodes carry `client.api=pipewire-pulse` — the backend witness.

### Claim 5 — target loss, split by direction → `gst_target_loss_r81_probe`

Every leg: seat-owned `<ns>` loaded and monitor-gated, unload fired at
+1.2 s by the name-verified index (all `verified_index`==`captured`,
`recycled:false`, rc 0), 0.2 s sample timeline, wall cap 4.5 s.

| leg | client | pre-unload | post-unload | end |
| --- | --- | --- | --- | --- |
| t1 | `pipewiresink target-object=<ns>` | consumers `[<ns>]` | **re-linked → default at +0.203 s** (one empty-link sample at the boundary) | alive at wallcap, stderr empty |
| t2 | `pulsesink device=<ns>` | `[<ns>]` | **re-linked → default at +0.203 s** | alive at wallcap, empty |
| t3 | `pipewiresrc target-object=<ns>` + prop | producers `[<ns>]` | **`[]` for every remaining sample — no re-link**; file **frozen at 204 844 B** | alive at wallcap, empty |
| t4 | `on-disconnect=error` | same | identical freeze | identical |
| t5 | `on-disconnect=eos` | same | identical freeze | identical |
| t6 | prop-only `target.object=<ns>` | same | identical freeze | identical |
| t7 | `pw-record` control | `[<ns>]` | **re-linked → default monitor at +0.202 s**, file kept growing 233 516→864 300 B | alive at wallcap |

The split law is verbatim: playback re-links within one 0.2 s sample and
never exits/errors; the gst capture does **not** re-link — the artifact
freezes at the last buffer with an **unfinalized wavenc streaming
header** (`riff_size 0x7FFF0024`, `data` declared `0x7FFF0000`), no
error, no EOS, process alive — while a same-event `pw-record` re-links.
`t6` freezes identically with no `target-object=` on the element — the
stale `node.target` prop is ruled out as the cause.

### Claim 6 — exit classes → `gst_exit_classes_r81_probe`

| leg | fault | rc | artifact | class |
| --- | --- | --- | --- | --- |
| e1 | `nosuchelementsrc_r81` | **1** | **none** | `WARNING: erroneous pipeline: no element "…"` |
| e3 | `audiotestsrc bogus-prop=42` | **1** | — | `no property "bogus-prop" in element` |
| e8 | `F64LE → pulsesink` (caps) | **1** | — | `can't handle caps` — parse class in gst-launch terms |
| e9 | `audiotestsrc !` (truncated) | **1** | — | `syntax error` |
| e10 | `pipewiresrc target-object=<bogus>` no prop | **255** | **0-byte** | `stream error: target not found` |
| e11 | `pulsesrc device=<bogus>` | **1** | **0-byte** | `Failed to connect stream: No such entity` — **the outlier** |
| p8 | `pulsesink server=unix:/nonexistent` | **255** | — | `Connection refused` + `Failed to set pipeline to PAUSED` |

The pair law: parse refusals are rc=1 + no artifact (`class_summary.
parse_rc1_no_artifact: true`); runtime state-change refusals are rc=255 +
0-byte artifact; `pulsesrc` is the rc=1 + 0-byte outlier.

### Claim 7 — autodetect → `gst_autodetect_r81_probe`

| leg | rc | backend witness | result |
| --- | --- | --- | --- |
| a0 `autoaudiosink` | 0 | `client.api=pipewire-pulse`, `media.name="audiotest wave"` | a **pulse-path** node appeared, linked to the default sink → `autoaudiosink` resolves to `pulsesink` |
| a1 `autoaudiosrc` | **1** | stderr `GstPulseSrc:autoaudiosrc0-actual-src-puls` + `Failed to connect stream: No such entity` + `not-negotiated (-4)` + 0-byte artifact | resolves to `pulsesrc` and **inherits r77's missing default** |
| a2 `alsasink device=null` | 0 | **no pw stream node** | control — a native-ALSA path publishes nothing; the "no node" signature is real |

## 3. Measured corrections / additions during authoring

1. **Scout-report hex misquote (claim 5).** The report's §4.2 table and
   appendix A24 say the frozen header's `data` field is `0x7FFFF000`.
   The scout's own receipt records `"other:2147418112"` = **`0x7FFF0000`**
   (and `riff_size 0x7FFF0024`). The author's re-measurement confirms
   `data_declared == 0x7FFF0000` on all four frozen captures — and the
   r81-boundary seat's committed read-only analysis (`dbe3a7f`,
   `reports/round-81/r81-boundary-readonly.md`) independently falsified
   the same constant (`0x7FFF0024`/`0x7FFF0000`). The law — "unfinalized
   wavenc streaming placeholders" — stands; the hex literal in the scout
   report text is corrected to `0x7FFF0000`/`0x7FFF0024`.
2. **`wavenc` klass fuller than the scout's table row.** The scout table
   prints `Codec/Muxer`; `gst-inspect-1.0` reports **`Codec/Muxer/Audio`**
   (armed verbatim; cosmetic row width, not a claim change).
3. **`client.name` is unset on gst clients.** The naming receipt shows
   the Client's `client.name` is `null` on every leg — the name surfaces
   through `application.name`; the crossover works because the two
   objects have *separate* naming authorities, not because either field
   shadows the other.
4. **`stream.capture.sink` / `node.autoconnect` land as STRINGS.**
   gst writes `"TRUE"` / `"FALSE"` onto the node props (receipt-verbatim
   values), not booleans — matching the r77/r78 string-prop convention.
5. **The `.monitor` suffix law decided on a non-default probe sink**:
   `pipewiresrc target-object=<ns>.monitor` does not resolve the
   probe sink's monitor — it lands the *default* sink's monitor
   (producer = default SPDIF node). Confirms the r77 residual claim on
   an isolated target.
6. **A frozen capture's size samples can pause mid-run** (65580 B at
   0.4 s, still 65580 at 0.6 s): pipewiresrc delivers in bursts — the
   "frozen" assertion is therefore post-unload flatness + the
   unfinalized header, not per-sample growth.

## 4. The full prior battery, replayed ≥2×

**Battery definition** — the r81-baseline seat's prior battery verbatim
(`corpus/live/r81-baseline/battery.sh`): the four commands `normal`,
`--probe-capture-r78`, `--probe-capture-r79`, `--probe-module-r80`,
replayed **twice** on the live tree with the r81-extended fixture
(sha `0dad37ee…`, recorded before/after every command — constant).
Driver: `corpus/live/r81-author/battery.sh`; logs, receipts and shas
under `corpus/live/r81-author/runs-{a,b}/`.

- **Commands: 8** (4 modes × 2 passes), **all exit 0** — vs the
  baseline's own pass (7/8 exit 0: its runs-a `capture-r79` logged the
  `b05_garbage` foreign-source confound and its runs-b `capture-r78`
  logged 3 foreign default-sink-contention failures, both environmental,
  per its receipts).
- **Row totals per pass: 86 entries / 136 legs** — `normal` 17/0,
  `capture-r78` 25/59, `capture-r79` 25/67, `module-r80` 19/10 —
  **identical to the baseline's census in every run**; ×2 passes =
  **172 entry-rows / 272 leg-rows replayed**. Failure dicts: **empty in
  all 8 of my runs**.
- **Byte-identity**: the `normal` receipt sha `8e8cdad6…` is
  **byte-identical 5 ways** — author-a, author-b, baseline-a, baseline-b
  and the tracked canonical receipt
  (`corpus/live/r81-baseline/byte-identity.txt` pins the canonical sha).
- **Semantic stability** (`percase.py`, pid/scratch/clock-normalized;
  `corpus/live/r81-author/stability-*.txt`): author A-vs-B on identical
  code: `normal` **373/373 leaves exact**; `module-r80` **0 semantic**
  (1 785 leaves); `capture-r79` **1 semantic** (23 619 leaves);
  `capture-r78` **133 semantic** (12 405 leaves) — all inside
  `playback_default_follow_r78_probe`'s live-routing cells (tone
  windows, `pinned`, `bound_to_target`, `carries_tone`), the same
  environmental-variance class that hit the baseline's own a-vs-b.
  Cross-checking my pair against the baseline pair (4-way): `r80` 1,
  `r79` 276, `r78` 424 semantic leaves — the increments over my
  A-vs-B are dominated by the baseline's confound-hit runs, not code.
- **No prior row changed its verdict surface**: every failure dict is
  empty, every entry count and leg count matches, and the only literal
  byte-equality claim (the `normal` battery — the mode carrying the
  17-entry standard corpus) holds 5 ways byte-for-byte.

## 5. Contention ledger

- The r81-**baseline** seat's battery ran concurrently in its frozen tree
  (`corpus/live/r81-baseline/`): my two formal `gst-r81` runs overlapped
  its `runs-b` `capture-r79`/`module-r80` window (17:14–17:21Z). All my
  resources are `gst_r81_auth_<pid>`/`gst_r81_<pid>_*`; its are inside
  the tree dir + `r81_*` names. Zero shared-object writes; my probes
  never read-or-mutate foreign objects by name (object-id join only).
- An `r81-boundary` lane was live earlier in the window
  (`gst_r81_bnd_*` names observed) — same isolation argument.
- The host default sink (`alsa_output.usb-Generic_USB_Audio-00.HiFi__
  SPDIF__sink`) was read-only observed, never set.
- `pactl set-default-sink`/`set-default-source`: **0 invocations**
  (grep-clean over the family).
- Every unload in the family goes through `_gst_r81_unload_own`:
  `pactl list modules short` re-read, `sink_name=<ours>` verified in the
  args before `pactl unload-module <verified-index>` — receipts record
  `verified_index`/`captured`/`recycled` per unload (all runs:
  `recycled:false`, rc 0).
- Post-run sweep: `sinks_gone` true and `own_nodes_after []` in every
  loaded entry, both formal runs; a `gst_r81`/`gst_r81_auth` census after
  the battery shows **zero** probe resources left on the host.

## 6. Write scope, replay, tree state

- **Tracked edits: one file** — `corpus/fixtures/measure_audio.py`
  (**+1 686/−3**, sha256
  `0dad37ee6500ca3d547d6b9654ad526249ae3d80215fcca3614703429b95fe56`,
  `python3 -m py_compile` clean; the `__pycache__` `.pyc` was
  `git checkout`-ed back so `git status` shows exactly the source edit —
  it is the only tracked modification in the tree at handoff).
- **Untracked artifacts**: `corpus/live/r81-author/` (battery driver +
  `runs-a/`/`runs-b/` receipts and command logs, `gst-r81-runs/`
  receipt copies, `stability-*.txt` compare outputs, `receipt-shas.txt`);
  the canonical receipts the fixture wrote under `corpus/live/runs/`
  (two `-gst-r81` dirs + eight battery dirs); this report. `SHONEN.md`
  was dirty earlier in the window but is clean at handoff (a sibling
  committed during the session: HEAD `7a75a36`). **No commit, no push.**
- **Replay**: `python3 corpus/fixtures/measure_audio.py --probe-gst-r81`
  from the repo root (~3 min; writes a `-gst-r81` receipt, prints
  `{"receipt": …, "failures": {}}`, exit 0 on a clean run).
- **Authoring-window probes**: direct `gst-inspect`/`gst-launch`/pw-dump
  smoke probes ran before coding to pin the Client pid-join, the
  two-key write, `client-name`/`client-properties` crossover, the
  `pulsesink device=` fallback and the freeze shape; all
  `gst_r81_smoke*`/`gst_r81_bnd*`-independent resources from those
  probes were unloaded; post-probe census showed zero leftovers.

