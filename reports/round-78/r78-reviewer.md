# R78 REVIEWER (audio) — independent re-derivation of `d9aa6f9`

Target: `d9aa6f9` ("r78 work: playback-direction lattice — 8 entries, 60+ legs"),
3 files: `corpus/fixtures/measure_audio.py` (+2401/−3), its tracked `.pyc`, and
`reports/round-78/r78-author.md`. **Seat: REVIEWER. Tracked edits: none**
(one new untracked report + untracked scratch under `corpus/live/r78-reviewer/`).

Method: (a) mechanical insertion-only proof of the diff; (b) my own full
`--probe-capture-r78` run on a **displaced env tree materialized from `d9aa6f9`
blobs** (so no tracked file was written); (c) my own **raw re-implementations**
(own tone L 880 / R 1320 Hz @ 10000, own `pw-link` edge parser, own WAV/FFT
classifier — `corpus/live/r78-reviewer/raw-checks.py`); (d) a fresh
`--probe-capture-r77` run on the same env tree for prior-cell stability.

**My receipts** (this session):
- `corpus/live/r78-reviewer/receipts/r78-measurements-run2.json` — my second
  full `--probe-capture-r78` run (own pid 949695, 23:28:42–23:35:57Z, taken
  under a concurrent sibling probe: 5 contended failures). It reproduces the
  follow straddle of report F1.
- `corpus/live/r78-reviewer/logs/r78-run1-compare-extract.txt` — the surviving
  record of my **first** r78 run (own pid 921933, 23:01:50–23:06:34Z, 2
  contended failures; the per-entry leaf comparison transcribed verbatim).
  Its receipt file was destroyed by my own scratch cleanup (a `cp` of two
  receipts into one filename before pruning the env tree) — the run-1 receipt
  path quoted in earlier drafts no longer exists.
- `corpus/live/r78-reviewer/receipts/measurements.json` — my fresh
  `--probe-capture-r77` receipt (own pid 944607, 23:25:14–23:28:5xZ,
  **`failures: {}`**, 6/6 entries clean).
- raw receipts: `corpus/live/r78-reviewer/raw-checks.json` + `logs/*.log`.

Host this window: `plazir27`, PipeWire 1.6.8, pactl/pw-cat 17.0-98-gb096,
alsa-utils 1.2.16, Python 3.14.7, Linux 7.2.3-arch1-3. **The topology moved
again since r78-baseline named the environmental set**: the DualSense USB audio
device is *gone* (kernel `usb 10-3: USB disconnect` 22:55:12Z, HID re-joined
over BT), so the default source is now
`…HiFi__Line__source` and there is no `…Direct__Direct__sink`/`source` pair at
all. A stale `aplay -D null /tmp/nowriter-r75-…/nowriter.wav` (pid 2202613,
>3 h) holds the host at `host_is_quiet=false` for every seat.

---

## 0. Headline — AGREE / DISAGREE per claim (8 cells + props + priors)

| # | cell | verdict | my own receipt |
| --- | --- | --- | --- |
| 1 | `--target` fallback lattice | **AGREE** (13 fallback legs + the `--target 0` stall, all reproduced) | my harness run reproduces all 14 legs leaf-for-leaf (rc/killed/wall/consumers); my own raw tone re-derives 8 legs: garbage / absent-after-unload / `default` / `@DEFAULT_SINK@` / source name / `<null-sink>.monitor` → SPDIF rc=0, wall 2.62–2.67 s, **my** tag tone on the default's tap (26/36 windows); honored → probe sink; `--target 0` → rc=−9, consumers `[]`, **0/36** tone windows |
| 1b | `.monitor` is a racy source-domain target | **PARTIAL** | my run lands the default sink (the admissible leg); the *peer* landing is not reproducible on this topology and appears only in the author's **superseded** receipts (see §3) |
| 2 | `followed_move` (active stream follows a live default move) | **AGREE** | raw: stream consumers SPDIF @1.0 s → probe sink @2.6 s and @4.0 s → SPDIF @5.4 s after restore; metadata sampler shows the write applied at 1.78 s and held 2.8 s. The author's class is right; the harness's own `moved`-leg pin is over-strict (§4 F1) |
| 2b | `pactl set-default-sink` is **stale** | **DISAGREE (class)** | raw: rc=0 and the write **landed at 3.5 s** (`pactl_delayed_default`, the other admissible class) — not stale; and after it landed, a fresh `pw-metadata` write reverted within 0.25 s (§4 F4) |
| 3 | `playback_relink_on_target_loss` | **AGREE** | my harness run: pre `[loss_sink]` → post `[SPDIF]` @3.0/5.0 s, rc=0, wall 6.03 s, tap carries the tag tone only after the loss |
| 4 | `unlinked_sustained_playout` | **AGREE** | my harness run: `pw-link -d` → consumers `[]` @3.0/5.0 s, rc=0, wall 6.08 s, no tone on the default |
| 5 | `class_override_segv` rc=−11 | **AGREE** | raw: `Audio/Sink`, `Stream/Input/Audio`, `Audio/Duplex`, `Audio/Bogus` → rc=−11, **stderr_len 0**, no ports/consumers; `Stream/Output/Audio` rc=0; `Audio/Source` stalls (rc=−9). The crash is immediate (0.06 s raw); the receipt's 2.01 s is the sampler's schedule (§4 F3) |
| 6 | aplay EBUSY + lock-retention bracket | **AGREE** | my harness run reproduces the whole entry leaf-for-leaf: witness EBUSY rc=1, `witness_lock_release_s` **5.9 s**, `+1 s` busy / `+7 s` free, `aplay -f FLOAT_LE` → `format is changed to S16_LE`, `arecord` → `alsa_sample_format` `S24_3LE`, plugin split, per-direction envelope. Raw: EBUSY rc=1 and release 5.9 s reproduced; the `+7 s`/convert legs were contended in my raw re-run (see §5) |
| 7 | `unlinked_sustained_zeros` | **AGREE** (exact) | raw: producer cut → sizes `[155692, 401452, 499756, 593964, 786476, 880684]`, final = expected **960044 B**, 14/14 pre-unlink windows carry **my** tone, **27/27 post-unlink windows silent (peak 0)**; consumer cut → frozen at **311340 B** across 3 samples then resumed to 1344044 B |
| 8 | `parec --fix-*` header lies | **AGREE** (exact) | raw: `hdr_rate_fix` payload 195756 B/s (→48000) with header rate **22050**; `hdr_rate_plain` 85111 B/s (→22050) header 22050; `rate_fix_raw` 195756 vs `rate_req_raw` 85111 |
| + | prop precedence (`-P` > `--target`, `PIPEWIRE_PROPS`) | **AGREE** | my harness run reproduces all 14 legs leaf-for-leaf |
| + | prior cells vs the r77 canonical | **AGREE — zero undeclared** | fresh `--probe-capture-r77` `failures: {}`; 302 differing leaves vs the canonical, **all** in declared classes (§6) |

---

## 1. Structural: the diff is insertion-only and value-preserving

`difflib` opcodes over `bdf748e:…/measure_audio.py` → `d9aa6f9`: **3 inserts**
(2372 lines at old:5905, the 1-line argparse entry, the 25-line dispatch block)
**+ 3 single-line replaces**. Stripping the inserts leaves a 6857-line residual
that differs from the old file in **exactly 3 lines**, each a pure
prepend/insertion (byte-verified):

- guard: `…probe_capture_r77]) > 1:` → `…probe_capture_r77, args.probe_capture_r78]) > 1:`
  (exact `str.replace` of the old line);
- `mode`: new = `    mode = "probe-capture-r78" if args.probe_capture_r78 else ` + old[11:];
- `suffix`: new = `    suffix = "-capture-r78" if args.probe_capture_r78 else ` + old[11:].

2398 + 3 = **2401 insertions**, 3 deletions — matches `--numstat` exactly. No
prior symbol is edited; `sed -n '4400,4700p'` of the r77 lattice block is
md5-identical between `bdf748e` and HEAD.

**F5 (low, hygiene).** The commit carries a **stale tracked `.pyc`**:
`corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc` embeds
`source_size = 499311` while the committed source is `502350` bytes (mtime
21:57:02Z, i.e. compiled from an earlier revision). Precedent: `bdf748e`,
`731937c`, `1a84ca7` carry *matching* pycs, `65790f1` was stale too. Harmless
at runtime (Python invalidates on size/mtime), but the artifact does not
describe its own source.

---

## 2. My own full r78 run — what it reproduces

Run 1 on a displaced env tree (`git archive d9aa6f9`; fixture sha256 verified
equal to the commit blob `af28ead…`, so no tracked file was written): `failures:
[]` for lattice-minus-target_0, target loss, props, segv, aplay, zeros, parec;
two contended failures on lattice `target_0` and follow `moved` (§4). The
per-entry comparison is preserved in
`logs/r78-run1-compare-extract.txt` (the run-1 receipt file itself was lost to
my scratch cleanup — provenance note in the header of this report).

Leaf-for-leaf against the author's receipt
(`corpus/live/runs/20261014T221945369366Z-capture-r78`), modulo the PID-stamped
probe names: **lattice 14/14 legs, loss 2/2, props 14/14, segv 6/6, zeros 2/2
(identical size traces and byte counts), parec 10/10 (identical bps, buckets and
headers), aplay 18/18** — e.g. the aplay entry is identical including
`witness_lock_release_s: 5.9`, `retention_1s.alsa_busy`, `retention_7s rc=0`,
`convert_float.converted_to: S16_LE`, `arecord_constrain: alsa_sample_format`,
`plugin_default/pipewire` rc=0 with the tag tone on the current default, and the
envelope `formats ['S16_LE','S32_LE','S24_3LE'] channels [2,8]` playback vs
`['S16_LE','S24_3LE'] channels 2` capture.

Only the **follow** entry differs run-to-run (run 1: `moved` = `[probe, SPDIF]`,
`still_probe` = `[SPDIF, SPDIF]`, `pactl.moved_at_s = 0.5`; author: `[probe,
probe]`, `[probe, probe]`, `moved_at_s = None`) — see F1/F4.

**Run 2** (`receipts/r78-measurements-run2.json`, same env recipe) was taken
while a sibling probe was live and is the honest contended counter-example:
5 failures, all named confounds — the F1 straddle again, a target-loss leg whose
fallback tap measured the *sibling's* default sink (its probe sink was unloaded
mid-run), one segv leg that lost its probe sink (`no target node available`),
and a `consumer_unlink` whose file kept growing (the capture never bound to the
probe sink's monitor). None of these is a law violation; together they are the
evidence that this family's `failures: {}` requires a quiet host.

---

## 3. The `.monitor` cell: what is actually evidenced

The final receipt's `monitor_name` leg lands the default sink at all three
samples in **both** the author's and my run (`landed_peer: False`,
`carries_tone: True`). The racy peer landing is **not** in the cited receipt —
it is in the author's *superseded* receipts, which I read: `…214821510582Z`
landed `…DualSense…Direct__Direct__sink` (and failed under the then-current
pin), `…220520747866Z` landed the default first (failed an intermediate
"must first land the peer" pin), `…221326175535Z` and `…221945369366Z` land the
default cleanly. So the *class* is receipt-backed across the family, but the
cited receipt alone carries only the default leg, and on today's topology (no
DualSense peer) I can reproduce only the default leg. Verdict: PARTIAL — the
claim is honest about its evidence, but the receipt does not pin the racy class.

---

## 4. Findings

### F1 — MEDIUM: the follow gate fails closed on a *transitional* sample the same harness admits elsewhere

My run failed `follow moved: expected consumers [r78_def_sink_921933], got
[SPDIF, r78_def_sink_921933]`. The stream was observed on the old default at
0.8 s and the new default at 1.8 s — the session manager's re-link is
asynchronous, and **the harness already admits exactly this straddle for
`still_probe`** ("its consumers may be the old metadata default, the pactl
target, or both") and for `nofollow` (`post ⊆ {spawn, restore}`). The `moved`
leg alone asserts a single node. The same shape is in the author's own family:
`…214821510582Z`'s `still_probe` = `[probe, SPDIF]`. Fold: give `moved` the
`still_probe` allowance (or sample it after a settle).

Corollary (same entry): the `pactl` sub-test has **no guard that the metadata is
still `s_new` when the write fires**. If the metadata has already moved back
(the case my run shows), `moved_at_s` is a spurious 0.5 s and the row is
classified `pactl_delayed_default` for the wrong reason. Record the metadata
state at write time (the trace already exists) and skip/annotate the row when
it is not `s_new`.

### F2 — MEDIUM: the content witness has no foreign guard and its tone is not seat-unique

My run failed `lattice target_0: tag tone reached the default sink` — the
default's tap carried **25 consecutive `mine` windows from 3.1 s to 5.6 s at
amplitude 8189**, while the same receipt shows the `--target 0` stream's
consumers `[]` at 1.0/2.5/4.5 s and its node `suspended` at all three samples.
The harness's discriminator is L 1000 / R 1500 @ amp 8192 — **the same tone the
r79 scout used** (r78-boundary deliberately switched to 1100/1750 @ 12000 for
this reason), so a concurrent lane's tone is indistinguishable from the probe's
own. Forensics on the window: the lattice entry's own contention snapshot shows
`fixture_runs: 0` and no `pw-play`/`pw-record`/`pw-cat` process, and no sibling
receipt was written between 23:00 and 23:12Z (canonical `corpus/live/runs/` and
`/tmp` both clean), so the tone's *process* is not identified — but it
cannot be the measured stream, whose consumption witness is empty throughout.
My own raw re-run with a distinct tone (880/1320) shows `target_0` → rc=−9,
consumers `[]`, **0/36 tone windows**: the law holds; the failure is a
contended-host content confound. Fold: a seat-unique tone per run (e.g. derive
L/R from the pid) or a foreign-window guard on the stall leg.

### F3 — LOW: the segv `wall_s ≈ 2.01` is the sampler's schedule, not the crash

Raw, my 4 crash legs die in **0.06 s** (rc=−11, empty stderr, no node). The
harness's `_playback_r78_run` fires its timed samples (0.7 s, 2.0 s) before
reaping, so the recorded `wall_s` is ~2.01 s for every crash leg. The `< 4 s`
pin still separates crash from stall, but the leaf reads as a measured death
latency; label it as the schedule bound.

### F4 — MEDIUM: `pw-metadata` is authoritative only until a `pactl` write lands; the classes are not cleanly separated

Raw (`raw-checks.json:follow`):
- `pw-metadata` write → the metadata sampler shows it applied at 1.78 s and
  **held 2.8 s** until I restored it; the active stream re-linked both ways.
- `pactl set-default-sink SPDIF` (rc=0) → the metadata stayed on the probe sink
  for 3.0 s, then landed at **3.5 s** — `pactl_delayed_default`, *not* stale.
- Durability probe (no stream running), immediately after that pactl write: a
  fresh `pw-metadata` write to the probe sink was **gone at the first 0.25 s
  sample** — the session manager re-asserted the pactl-configured default over
  it.

So the author's §2.2 conclusion ("`pw-metadata`, not `pactl`, is the reliable
switch") is directionally right, but the headline "stale" overstates: on this
host the verb is *delayed* (3.5 s here, ≥5.6 s in the author's three runs,
~3.5 s in their own earlier run), and once it lands it *overrides* later
`pw-metadata` writes. Fold: record `pre_metadata` at write time and pin the
class on it (F1 corollary), and add the "pactl lands then wins" ordering to the
named-class notes.

### F6 — LOW (cross-seat, named): reviewer↔simplifier interference

The r78-simplifier lane was running `pair_replay.py` (`--probe-capture-r78`)
throughout my window. Two interactions, both named so no receipt is
mis-attributed:
1. My first `raw-checks.py` invocation started while its probe had
   `default.audio.sink` pointed at its own `r78_def_sink_927430`; my script
   recorded that as "the" default and its `finally` wrote it back at 23:09:43Z.
   I restored SPDIF at 23:10Z and pinned the real default in the script
   (`restore_host_default`). Its attempt-1 control run then failed
   `playback_default_follow_r78_probe` — that failure is mine, not the arm's.
2. My later checks overlapped its attempt-2/attempt-3 windows; its
   `pair3.log` control failures (`playback_class_segv_r78_probe`,
   `playback_aplay_axis_r78_probe`) coincide with my aplay raw run at
   23:22:22–23:22:38. Its `clean()` gate also cannot pass on this host for any
   seat (`host_is_quiet=false` from the stale pid 2202613), so its pair can
   never be clean regardless.

---

## 5. What I did **not** independently reproduce

- **aplay `+7 s` free and the convert leg, raw.** My raw aplay run at 23:22:2x
  was contended (sibling probe holding `hw:0,0`): `retention_7s rc=1` and
  `convert rc=1` (no `format is changed`). The same two leaves *are*
  reproduced in my own harness run (§2) and the witness EBUSY + 5.9 s lock
  release were reproduced raw. Classified as contended, not as disagreement.
- **The `.monitor` peer landing** (topology: no DualSense peer today).
- **A quiet-host counter-run** — impossible this window (stale `aplay`, three
  live sibling lanes). All my receipts carry `host_is_quiet: false`.

---

## 6. Prior-cell stability vs the r77 canonical

Fresh `--probe-capture-r77` on the `d9aa6f9` env: **`failures: {}`** (all six
entries: target-loss, source lattice, readers, arecord sever, split sentinel,
format axis). Leaf-diff against the canonical
`corpus/live/runs/20261014T210316456683Z-capture-r77` (sha256 `09ecf6e6…`):
**302 differing leaves, 0 undeclared** (`logs/r77-vs-canonical.txt`,
`logs/r77-classification.txt` — the buckets below sum to exactly 302):

| class | leaves | what it is |
| --- | --- | --- |
| bounded-capture frame jitter | 189 | the class r78-baseline named (18 035 vs 18 034 frames, 72 036 vs 72 136 B …): TERM-severed captures land a few frames off |
| env-topology (DualSense → Line) | 46 | source-name substitution in `consumed_nodes`/`link_producers`/`argv`/inventory, and `noprop_source.content.carries_tone` True→False: the DualSense *Direct* source/sink share one duplex PCM (the source hears the sink), the Line source is an independent input |
| confound shape on `noprop_default_sink*` | 24 | the canonical's two cells fell back to the default source (`fallback_default_source`, 384 044 B with a foreign tone); mine refused cleanly (`no_target_node`, 44 B). The gate accepts both shapes and flags the fallback as a confound |
| pre-r78 provenance witness | 16 | `target_object_prop` `[]` (canonical) vs `['<target>']` (mine) and the derived `target_object_is_request`: the canonical receipt (21:03:16Z) **predates `bdf748e` fold-2** (21:40:31Z), which fixed the client-id→PID provenance witness — a pre-r78 impl class, not r78 drift |
| wall / contention / scrub | 12 | declared since r68 (stderr scrub windows, wall keys) |
| per-pid probe names | 10 | the r77 fold's per-process naming (`r77_loss_sink_944607` vs `…_1265995`) |
| conditional confound keys | 3 | the canonical recorded `confound_observed: True` + `fallback_source_cells: [noprop_default_sink, noprop_default_sink_monitor]`; my run had no such confound |
| module ids | 2 | `probe_sink_load/module_id`, `sink_load/module_id` (536870919 vs 536870920) |

Note for the record: `20261014T210316456683Z-capture-r77` is called the
"folded-run receipt" in r78-baseline §6, but it predates the fold-2 commit, so
it is *not* a post-`bdf748e` reference; the 16 provenance leaves above are the
visible consequence.

No prior row's *verdict* changed: both receipts carry `failures: []` for the r77
family, and my structural proof (§1) shows the r78 diff cannot touch prior code.

---

## 7. Residual risk

- **Host topology moved again** (DualSense USB audio gone at 22:55:12Z). The
  environmental set r78-baseline named no longer describes the host; any
  round-to-round comparison against r76/r77 receipts must re-derive the
  source-name substitution against *today's* default source.
- **The stale `aplay -D null` (pid 2202613)** keeps every receipt at
  `host_is_quiet=false` and invalidates any quiet-host claim fleet-wide.
- **Shared-host gates**: the follow entry's `moved` pin and the r78 tone
  identity are the two places where a contended host flips a pass into a fail
  (F1, F2). The author's `failures: {}` is real but not reproducible under
  concurrent lanes.
- **Evidence provenance**: my first r78 receipt file was destroyed by my own
  scratch cleanup; the leaf-for-leaf comparison survives only as the transcribed
  extract (`logs/r78-run1-compare-extract.txt`) and run 2
  (`receipts/r78-measurements-run2.json`) is contended. A future seat wanting a
  clean r78 receipt must re-run on a quiet host — none exists from this window.
- My review left the tracked tree untouched (`git status` shows only the new
  untracked `reports/round-78/r78-reviewer.md` + `corpus/live/r78-reviewer/`);
  the metadata default is back at SPDIF, no r78-reviewer module survives.

## Recommendation

**ACCEPT the diff.** Insertion-only and value-preserving (3 exact prepend
rewrites); all eight headline cells independently re-derived — six of them
leaf-for-leaf identical on my own run and raw re-implementations, the segv,
zeros and parec cells confirmed by from-scratch code with a distinct tone; the
prior r77 family is `failures: {}` with **zero undeclared** leaf differences
against the canonical. **Fold F1, F2 and the F1-corollary** before citing the
receipt family as a gate on a shared host: each is a guard against a confound
the probe already computes (transitional consumer sets; a seat-unique tone;
the metadata state at pactl-write time). F3–F6 are labeling/hygiene.
