# R78 scribe (audio) — r77 ledger re-derivation + r78 landing watch

Seat: **SCRIBE (leaf, report-only)**. Repo `/home/vgpnk/Projects/shokunin/audio-shokunin`.
Host `plazir27`, Linux 7.2.3-arch1-3, Python 3.14.7.

Write scope: **this report only** (`reports/round-78/r78-scribe.md`). Audit scratch
lives in `/tmp/r78_scribe/` (outside the repo). **No git mutation** (no `add`,
`commit`, `push`, `checkout`, `stash`), no tracked file created/edited/deleted,
**no audio probe re-run**, no PipeWire client, sink, module or `pactl` verb was
issued by this seat — the r78-baseline battery was live on this host throughout
and the r77 ledger's own confound lessons make that a hard constraint, not a
courtesy. The single program this seat *executed* is the r77 simplifier's own
patch script, against a `/tmp` copy of the pre-fold fixture (a pure text
transform; §1.1).

**Stamps.** All readings are at **HEAD `731937c`** ("r77 report-last: adjudicator
+ LOG + SCORECARD", 2026-10-14T21:25:51Z) and were taken
**21:12–21:31Z (2026-10-14)** unless a different stamp is named. The wave is
live: the r78-baseline lane was mid-battery (§6.2) and `corpus/live/r78-author/`
appeared as an empty dir at 21:30Z. Fixture content at read time is
byte-identical to `HEAD:corpus/fixtures/measure_audio.py`
(`e5b00f60ee4fc309…`, §1.1) and `git status --porcelain corpus/artifacts/` is
empty.

---

## 0. Audit surface and commands

| # | audit item (from the assignment) | command / method |
|---|---|---|
| A1 | fold commit vs its declared inventory | `git show 1a84ca7` → `/tmp/r78_scribe/fold.diff`; `git show 1a84ca7:corpus/fixtures/measure_audio.py` → `post.py` (`fd33fc41…`), `git show 65790f1:…` → `pre.py` (`6299b335…`) |
| A2 | simplifier `+56/−58` batch | faithful re-execution of `corpus/live/r77-simpl/apply_simplifications.py` on a `/tmp` copy of `pre.py`; plus a 26-hunk containment check of the batch's new text against `post.py` |
| A3 | exclusivity guard | line-level read of the `if sum([…])` guard in both blobs |
| A4 | folded-run receipt `failures:{}` | `python3` leaf walk over `corpus/live/runs/20261014T210316456683Z-capture-r77/measurements.json` (`09ecf6e6…`) |
| A5 | pre-fold → fold receipt delta | full leaf flatten + set/compare of `…T200120162289Z-capture-r77` vs the folded receipt; verdict-leaf filter |
| A6 | r76 regression classification | failure census of all 19 `corpus/live/runs/*capture-r76*` receipts + the 5 replica receipts under `corpus/live/r77-baseline/measure-env{,-post}/corpus/live/runs/`; `grep -rl "gate parec_no_device" corpus/live --include=measurements.json` |
| A7 | seat-record ids in the adjudicator | `sha256sum reports/round-77/*.md`; `sha256sum .ufo/waves/shokunin-train-20261101-w17/tasks/*.md`; repo-wide grep for the 8-hex ids |
| A8 | seed-mutation restoration | `sha256sum corpus/artifacts/ambience.wav` vs `git show HEAD:… \| sha256sum` |
| A9 | contention-class artifact (18.6 %) | per-run artifacts under `corpus/live/r77-baseline/` (`transient-shape.txt`, `residue-ab.txt`, `roundtrip-repeat.txt`, `gain-source.txt`) summed against the report's own table |
| A10 | r78 landing watch | `git log`, `ls corpus/live/`, `find corpus/live/runs -newermt`; r78 scout report stamps vs file mtimes |

---

## 1. The fold commit `1a84ca7` vs its declared inventory

`git show --numstat 1a84ca7` = `336 127 corpus/fixtures/measure_audio.py` +
`- - corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`
(`Bin 157038 -> 420472`). The adjudicator's "`+336/−127` in
`corpus/fixtures/measure_audio.py`" and LOG's "Folds `1a84ca7` (+336/-127)" are
**exact**. Fixture blob `6299b33…` → `fd33fc41…`.

| # | declared inventory item (commit body / adjudicator §Fold inventory / LOG) | artifact check | verdict |
|---|---|---|---|
| 1 | "Simplifier batch (+56/-58 zero-diff)" | faithful re-run of the simplifier's own script on `pre.py` prints `# batch: 26 replacements, +56 / -58 lines`, exit 0 | **confirmed, exact** |
| 2 | "exclusivity guard now covers `probe_capture_r77`" | guard line 5801 (pre) ends `…args.probe_capture_r76])`; line 6010 (post) carries `args.probe_capture_r77` **and** `probe_capture_r76` | **confirmed** |
| 3 | "N2 wall-leg vacuity: fresh sink + exact module id" | diff adds `mid2 = _capture_r77_null_sink_load()` + `sink_load_wall` leaf + `unload_module_id=` parameter threaded into `_capture_r77_run`; fail-closed `unload rc != 0` and pre-loss-consumption clauses added | **confirmed** |
| 4 | "sink name per-process (`r77_loss_sink_<pid>`)" | `CAPTURE_R77_NULL_SINK = f"r77_loss_sink_{os.getpid()}"`; folded receipt `sink_name: r77_loss_sink_1265995` | **confirmed** |
| 5 | "`prop_probe_sink` lattice row: discriminating" | row added to `CAPTURE_R77_LATTICE`; folded receipt: 12 cells, `prop_probe_sink` `consumed_nodes: ['r77_loss_sink_1265995']`, `carries_tone: False`, `data_finalized: True` — the probe sink is consumed while the tone goes to the default sink | **confirmed** |
| 6 | "F5: bounded header reads, chunked zero scan, np.memmap" | `_capture_wav_inspect` reads `min(size, 65536)` + `path.stat()`; `_capture_r77_pcm_stats` uses `np.memmap`; `_capture_r77_all_zero` reads 4 MiB blocks | **confirmed** |
| 7 | "`sink_gone` vacuity armed" | `pactl list sinks short` (was `sources`); new `probe_sink_gone` leaf + teardown failure clause | **confirmed** |
| 8 | "confounds honored: stale_link deltas, foreign-client /proc counting" | `stale_link_before_cell` confound branch; probe-sink excluded from `foreign`; `_capture_r77_foreign_clients` rewritten to `/proc/*/comm` + `cmdline` | **confirmed** |
| 9 | "fail-closed asserts: reader calibration 96000×5, device-axis file existence+header class, format-axis `usage_refusal`/no-file/rc, frame-bound `data_actual` bytes, `probe_sink_gone`, wall unload-fired + pre-loss consume" | all six assert sites present in `post.py`; §2 shows the two receipt-visible ones firing | **confirmed** |
| 10 | "`carries_tone` raw fraction (bucket dead-zone removed)" | `raw_frac = float((mag > 0).mean())`; `carries_tone = raw_frac > 0.05`, bucketed leaf retained | **confirmed** |
| 11 | "`sha_match_control` fails closed" | new `_capture_r77_sha_pair(a, b)` returning `None` when either side is absent | **confirmed** |
| 12 | "`noprop` fallback class named when the default source is live" | `noprop_source` `exp_tone` → `None`; `cell_class: fallback_default_source` + `fallback_source_cells`; folded receipt carries `['noprop_default_sink', 'noprop_default_sink_monitor']` | **confirmed** |

**1.1 The `+56/−58` figure reproduces exactly, and the batch is a strict subset of
the fold.** `python3 corpus/live/r77-simpl/apply_simplifications.py
/tmp/r78_scribe/cand.py` (copy of the pre-fold blob) exits 0 with
`26 replacements, +56 / -58`. All 26 hunks' `new` text is present verbatim in
`post.py` (`missing=[]`), so the fold = the batch + the wave-B corrections, as
claimed. Independently: `sha256(pre.py) = 5457376a…` (the r77 work blob
`6299b335…`), `sha256(post.py) = e5b00f60ee4fc309…` == the committed
`HEAD:corpus/fixtures/measure_audio.py` == the live worktree file.

*Caveat on method:* my first two attempts re-derived the batch by re-applying the
`rep()` calls I extracted with `ast.walk` and produced `+55/−53` and a spurious
count mismatch — `ast.walk` is breadth-first, so the 26 hunks were replayed
**out of source order**. The script's own sequential run is the authoritative
form and it is the one reported here.

---

## 2. The folded-run receipt `20261014T210316456683Z` — `failures:{}` re-derived

`corpus/live/runs/20261014T210316456683Z-capture-r77/measurements.json`,
sha256 `09ecf6e6bd722ce83006cf362a0b903b7a72f4a94ef119b13fb30edc88e4852c`,
`mode: probe-capture-r77`, **23 entries** (17 ordinary rows + 6 r77 probes).
**Every one of the 23 `failures` maps is `[]`.** The adjudicator's "all 6 probes
`failures: {}` under a contended host" and the commit body's "Folded probe: 6
probes, failures={}" both reproduce.

**The receipt is fold-tree-derived, not a stale rerun** — it carries four leaves
that exist only in `post.py`: `probe_sink_load`, `probe_sink_gone`,
`sink_load_wall`, and `cell_class: fallback_default_source`. Third-party
provenance anchor: the r78-scout-playback seat recorded the *pre-commit* worktree
fixture as `sha256 e5b00f60ee4fc309` (`reports/round-78/r78-scout-playback.md`
§8) — the same digest as `post.py` and as `HEAD` — so the 21:03:16Z receipt was
produced from the content that became `1a84ca7` 20 min later.

**Contention is disclosed, not hidden.** The receipt's own
`capture_source_lattice_r77_probe/contention` leaf is
`{pw_record: 5, fixture_runs: 0, own_pid: 1265995, host_is_quiet: False}`, and
the receipt's inventory contains the **r78 scout-playback lane's live null sinks**
(`r78p_ns`, `r78p_ns2` + their monitors) — that lane was writing raw captures at
21:03:16Z, the same second. Both the adjudicator ("under a contended host") and
LOG ("under contention") say so. ✓

**The two vacuity fixes are receipt-visible, and the pre-fold state they replaced
is visible in all 11 pre-fold receipts:**

| leaf | all 11 pre-fold r77 receipts | folded receipt |
|---|---|---|
| `wall_clock/file/unloaded` | `exit_code: 0`, `error: "Failed to unload module: Module  not loaded"` (the rc-0 no-op, verifier N2) | `exit_code: 0`, `error: None` |
| `sink_gone` | `True` — vacuously (sources enumerated for a sink name, simplifier S6) | `True` — non-vacuous (`probe_sink_gone: True` after a real load/unload) |
| `wall_clock/nodes_before → nodes_after` | `[] → []` (differencing blinded) | `['r77_loss_sink_1265995'] → ['alsa_output…SPDIF__sink']` |
| `rates.segments` | n/a | `98 / 104 / 102 %` — LOG's "98/104/102%" **exact** |

---

## 3. Pre-fold → fold receipt delta (independent leaf walk)

`…T200120162289Z-capture-r77` (author canonical) vs the folded receipt:
**2,710 → 2,759 leaves**; 11 leaves only pre-fold, 60 only post-fold, **237
common-key diffs**.

- **The 60 post-fold-only leaves are the fold's own additions**: the
  `prop_probe_sink` cell (29 leaves), `probe_sink_load` / `probe_sink_gone`,
  `sink_load_wall`, `wall_clock/nodes_before|after`, `cell_class` /
  `fallback_source_cells` / `default_sink_trace/11`, and the host-inventory rows
  for the r78 scout's sinks and the DualSense source.
- **Verdict-surface diffs are 21 of 237, and every one is a declared class**:
  the two `noprop_*` cells moving to the new named class
  (`error_class: no_target_node → None`, `carries_tone: None → True`,
  `topology_witness: 'unavailable…' → 'live'`), `noprop_source`'s
  `carries_tone: False → True`, and 12 `readers/honest_frames` values that are
  the D1 sever-wall-clock magnitudes. **No `failures`, `error_class`, `verdict`,
  `sha_match*`, `data_finalized`, `eintr_cells`/`alsa_busy_cells` or
  `reader_honesty` leaf moved except through those declared classes.**
- The remaining 216 diffs are the author's declared drift classes (arecord sever
  frame magnitudes ±1–2, ffprobe durations, `soxi` raw strings) plus 16
  `capture_format_axis_r77_probe/legs/*/argv` rows whose target name changed
  from the Line source to the DualSense source — **environmental argv drift, not
  a verdict leaf**.

So "prior cells byte-stable modulo declared drift" is **supported at the verdict
surface** for this pair, with one exception of semantics (§5.3) and one of
witness death (§5.2).

---

## 4. The r76 regression classification — the A/B leg has no artifact

**What is claimed.** `r77-adjudicator.md:70-75`:

> "Folded probe: all 6 probes `failures: {}` under a contended host (receipt
> `20261014T210316456683Z`). r76 regression on the folded tree: 3 failures all
> classified host-state — `parec_no_device` + arecord legs reproduce
> **identically on pre-fold HEAD** (device topology changed: DualSense source now
> default; PCM paths freed), and the roundtrip-witness failure matches the named
> 18.6 % contention false-alarm class."

`LOG.md:1325-1329` repeats it ("3 host-state failures all reproduced on pre-fold
HEAD or match named contention classes"); the fold commit body says "r76
regression on same tree shows only host-topology drift identical to pre-fold HEAD
(environmental)".

**What the artifacts say.** The post-fold-tree r76 battery exists in exactly two
receipts, both unreferenced by any report or seat artifact
(`grep -rl "210650075098\|211525652736" corpus/live reports` → no hits):

| receipt | stamp | failures |
|---|---|---|
| `…T210650075098Z-capture-r76` | 21:06:50Z | 3: `gate parec_no_device: expected (1,pa_no_such_entity) got (None,None)`; `arecord -D default: expected the set_params:1462 capture block or a busy`; `arecord -D pipewire: …` |
| `…T211525652736Z-capture-r76` | 21:15:25Z | the same 3 + `roundtrip content witness deviated (…)` |

The pre-fold-tree r76 receipts are **green** for this set: all 17 pre-fold
receipts under `corpus/live/runs/` (plus one empty receipt dir,
`…T181356386452Z`) and the r77-baseline's own 5 replica runs
(`r77-baseline/measure-env/corpus/live/runs/…T194043238882Z`, `…T195105042290Z`,
`…T195154481817Z`, `…T195239476759Z` and `measure-env-post/…T201349561281Z`)
carry **0** `parec_no_device` and **0** device-axis failures. The one pre-fold
receipt that carries three failures at all — `…T181454123380Z-capture-r76`
(18:14:54Z, the r76 round's own run 1) — has a **completely different** set
(`ffmpeg KILL deviated`, `arecord KILL deviated`, `roundtrip sox detect leg`),
i.e. the r76-era iteration trail, not this set. Repo-wide,
`grep -rl "gate parec_no_device" corpus/live --include=measurements.json` returns
**exactly the two post-fold receipts**.

⇒ **The environmental class is right; the "reproduce identically on pre-fold
HEAD" leg is unproven.** The mechanism *is* receipt-visible and unambiguous: the
pre-fold receipts' `inventory.sources` lists only the USB Line/Mic sources, while
the post-fold receipts' inventory adds
`alsa_input.usb-Sony…DualSense…Direct__Direct__source` and `parec --raw` with no
`-d` stops returning `pa_no_such_entity` and blocks instead
(`exit_code: null`, `error_class: null`, `"blocked: no verdict within 10 s"`).
So the change is host topology, not the fold — but the fold's own verification
never produced the pre-fold half of the A/B, and **no receipt records it**.

**Why this matters more than a bookkeeping nit.** The fold is **not** purely
r77-local: it modifies the shared helper `_capture_wav_inspect` (10 call sites,
including the r76 capture legs), the same helper the reviewer's *pre-fold*
insertion-only proof certified as untouched. The claim that the r76 battery did
not regress therefore rests entirely on the missing A/B. Two of the three
failures (`arecord -D default|pipewire`) are arecord error-class expectations
that the header change cannot plausibly explain, and the third is an
`exit_code: null` timeout — but "plausible" is not "measured", and the fold
commit body's own words ("identical to pre-fold HEAD") assert a measurement that
is not on disk.

**The contention half *is* supported.** The roundtrip-witness false alarm fired
pre-fold in 2 of the 5 replica runs (`…T194043238882Z`, `…T195154481817Z`) and
0 of the other 3, and post-fold in 1 of 2 — an intermittent class, not a fold
signature. The 18.6 % figure re-derives from the baseline's own per-run
artifacts: `1 (replay) + 1/6 (repeat) + 1/6 (residue A/B) + 5/18 (transient) +
0/12 (gain) = 8/43 = 18.6 %`, and `transient-shape.txt` itself is 5/18 with
`+4.459, +3.342, +4.3, +3.195, +4.3 dB` — the report's table row-for-row. ✓

---

## 5. Conflicts and prose-vs-artifact gaps (verbatim, for the canonical judge)

### 5.1 — A pre-fold A/B asserted with no artifact (the round's largest gap)

Quote: `r77-adjudicator.md:71-73` "`parec_no_device` + arecord legs reproduce
**identically on pre-fold HEAD**"; `LOG.md:1327` "3 host-state failures all
reproduced on pre-fold HEAD"; fold body "identical to pre-fold HEAD
(environmental)". Artifact: §4. **No pre-fold receipt carries those three
failures** — the only pre-fold receipt with three failures at all
(`…T181454123380Z`) carries a different set, and the only two receipts that do
are post-fold and are cited by nothing. The verdict ADMIT-corr is unaffected
(the class is right and the mechanism is visible), but the *evidence* the ledger
attributes to the classification does not exist. This is a repeat of the r76
scribe's C1 pattern: a byte/identity claim whose artifact falsifies it.

### 5.2 — The fold silently emptied the provenance witness it was sharpening

Quote: `r77-author.md:88` "`target_object_is_request = true` in **every live
cell**" and `:377` "all 11 lattice cells (consumed node, tone, bytes, class,
`target_object_is_request`)" inside the "everything else is identical" claim.
Artifact: in **every** pre-fold r77 receipt `target_object_prop` is non-empty and
`is_request` is `True` for 9 of 11 cells; in the **folded receipt**
`target_object_prop` is `[]` and `target_object_is_request` is `False` on **all
12 cells**. The only code change on that path is the fold's own critic fix
(`_capture_r77_node_props(owner_pid=proc.pid)`, matching
`props.get("application.process.id") != str(owner_pid)` → `continue`). Neither
leaf is read by any failure clause in either blob, so no gate changed — but the
witness is dead in the round's final receipt and **no report names it**. The
mechanism (key absent from node props / int-vs-str / pid mismatch) is **not
resolvable from on-disk artifacts**: the only captured `pw-dump` props on disk
are the r78 scout's, and its harness projects a fixed key list that does not
include `application.process.id`. Resolution is one cheap r78 row (dump the raw
node props during a live `pw-record`).

### 5.3 — `confound_observed: True` now means two different things, undisclosed

Quote: `r77-reviewer.md:98` reads the leaf as the cleanliness witness
("`failures: {}`, `alsa_busy_cells: []`, `confound_observed: None`"). Artifact:
the folded receipt's lattice entry is `confound_observed: True` with
`confound: None` and `fallback_source_cells: ['noprop_default_sink',
'noprop_default_sink_monitor']` — the fold's new `fallback_default_source` branch
sets the *confound* flag for a **named, expected, measured** host class. A reader
diffing receipts sees "confounded run" where the fold means "named fallback
class". The fold inventory describes the class but never the flag it reuses.

### 5.4 — "exact module id" is a weaker handle than stated

Quote: adjudicator "fresh per-run sink + `r77_loss_sink_<pid>` + exact module
id". Artifact: the folded receipt's three loads all report `module_id:
536870920` (`probe_sink_load`, `sink_load`, `sink_load_wall`) — this host reuses
a module id after unload (pre-fold receipts show the same counter at
536870916/917 across runs). The N2 vacuity *is* closed, but by the pre-loss
consumption assert (`nodes_before == ['r77_loss_sink_1265995']`) and the
unload-fired assert, not by id uniqueness. Worth one clause in the ledger so the
next round does not lean on the id as an instance token.

### 5.5 — Adjudicator seat-record ids are unresolvable

`r77-adjudicator.md:79-82` pins the seats as `author b92a17d4`, `boundary
79539680`, `baseline 660f1e30`, `scribe 4f70d450`, `critic b47b…`, `reviewer
8c9f…`, `verifier 47e18c85`, `simplifier 11f727f2`, `scout 3e81acc7`. **None
matches any artifact this seat can find**: report-file sha256 prefixes are
`3ef99db8 / 4811ed7e / 61a774ef / 7044f7de / ba8a4a1f / 3c86d7a7 / 87373f9e /
6adecfa4 / 7d25f398`; the w17 task-brief sha256s are `a47ab7a2 / b3f99d88 /
700013e6 / 4922fade / …`; `.ufo/` carries no r77 prompts; a repo-wide grep for
the ids returns only the adjudicator itself. The convention is consistent across
rounds but is not checkable from the repo — an auditability gap, not a defect.

### 5.6 — Two r78 scout reports label local time as UTC

`reports/round-78/r78-scout.md:4` "measured 2026-10-14 ~16:50–17:15 UTC";
`reports/round-78/r78-scout-playback.md:3` "~17:50–18:30 UTC". Artifact: their
files are stamped 16:52–17:04 and 17:53–18:20 **local (-0300)**, i.e.
19:52–20:04Z and 20:53–21:20Z. The wave's `Z` stamps are true UTC (e.g. the
folded receipt `20261014T210316456683Z` = 18:03 local), so both scout windows are
mislabelled by three hours. Low severity — no measured number depends on it —
but it matters here because it is the same window in which the folded r77
receipt was produced (§2), and the contention cross-reference between the two
lanes has to be read with the offset applied.

---

## 6. r78 landing watch

**6.1 No r78 author commit has landed at read time.** `git log --oneline -3` →
`731937c` (21:25:51Z) ← `1a84ca7` ← `65790f1`. `corpus/live/r78-author/` is an
**empty dir created 21:30Z**; `reports/round-78/` holds only
`r78-scout.md` (tracked) and `r78-scout-playback.md` (untracked); no new receipt
dir has appeared under `corpus/live/runs/` since 21:15:25Z. **Nothing r78-author
has landed, so there is nothing of it to re-derive** — the r78 author arm
(`--probe-capture-r78` playback lattice: write-side fallback matrix,
live-default-follow, mid-play target loss, `target.object`-vs-argv precedence +
`PIPEWIRE_PROPS`, bogus `media.class` SIGSEGV, aplay device axis, capture-side
gaps) is still open.

**6.2 r78-baseline Phase 1 is live and already reproduces the environmental set.**
`corpus/live/r78-baseline/` is mid-battery (stamps 21:27:24Z onward, `rerun.log`
`001 exit=0 normal` at read time). Its `toolchain.txt` records **Default Source =
`…DualSense…Direct__Direct__source`** on this host — the same topology that
produced the three post-fold r76 failures in §4 — and its `contention-watch.txt`
opened a 1500 s window at 21:27:43Z. This is *corroboration for the r77
classification*, arriving one round later than the adjudicator claimed it.

**6.3 The r77 seed-mutation side-effect recurred in r78.** The adjudicator parked
"read-only seeds is r78 work"; the r78 scout-playback seat reports a concurrent
lane regenerating `corpus/artifacts/*.wav` at 18:14 local during its session
(bytes identical, `git status --porcelain corpus/artifacts/` empty). The hazard
is still live; the byte-determinism is still holding.

---

## 7. Out of scope / not audited

- The six r77 probe entries' **measured physics** (fallback law, reader matrix,
  arecord bound-derived headers, split sentinel, format partition) — re-derived
  by the verifier from its own harness and corroborated here only at the leaf
  level (§3). This seat ran no probe.
- The r76 canonical pair's own claims (the r76 scribe's audit covers them).
- `reports/round-77/gst-scout.md` (GStreamer arm) and the g2d/g3d lanes.
- `corpus/live/r77-boundary`, `r77-scout`, `r77-simpl`, `r77-verifier` seat
  scratch beyond the files cited above.
- The r78 author's frontier: not landed (§6.1).

---

## 8. Verdict of this seat

The r77 ledger is **substantially artifact-backed**: the fold's declared
inventory reproduces item for item, the `+56/−58` batch is exact and contained,
the folded receipt's `failures:{}` holds on all 23 entries under disclosed
contention, both vacuity fixes are visible in the receipt *and* their pre-fold
no-op state is visible in all 11 pre-fold receipts, prior-row stability holds at
the verdict surface, the seed restoration is real, and the 18.6 % class
re-derives from the baseline's own artifacts.

Three gaps are recorded for the canonical judge, in severity order: **(5.1)** the
r76-regression A/B leg is asserted with no artifact, on a fold that touches a
shared helper — the verdict stands on the mechanism, not on the cited evidence;
**(5.2)** the fold emptied the provenance witness (`target_object_prop` /
`target_object_is_request`) it was written to sharpen, undisclosed; **(5.3)**
`confound_observed` now carries a second, undisclosed meaning. None of the three
changes a `failures` map in any receipt, and none is a claim this seat can
promote to execution evidence beyond what is written above.

**Findings are reported as findings; the canonical Rust judge is the sole
Pareto judge of this round.**

---

## 9. Artifact paths (all repo-relative unless noted)

- This report: `reports/round-78/r78-scribe.md`
- Fold: `git show 1a84ca7` → `/tmp/r78_scribe/fold.diff`; blobs `pre.py`
  (`6299b335…`) / `post.py` (`fd33fc41…`) in `/tmp/r78_scribe/`
- Folded receipt: `corpus/live/runs/20261014T210316456683Z-capture-r77/measurements.json`
  (`09ecf6e6…`)
- Pre-fold canonical: `corpus/live/runs/20261014T200120162289Z-capture-r77/measurements.json`
- Post-fold r76 receipts: `…/20261014T210650075098Z-capture-r76/`,
  `…/20261014T211525652736Z-capture-r76/`
- Pre-fold r76 replicas: `corpus/live/r77-baseline/measure-env/corpus/live/runs/`
  and `…/measure-env-post/corpus/live/runs/`
- Simplifier batch: `corpus/live/r77-simpl/apply_simplifications.py`,
  `replay-proof.txt`, `attempt1/`, `attempt2/`
- Baseline class artifacts: `corpus/live/r77-baseline/{transient-shape,residue-ab,roundtrip-repeat,gain-source,prior-rows-stable,post-rows-stable}.txt`,
  `exclusivity-check.txt`
- Verifier: `corpus/live/r77-verifier/{v1_lattice.json,v6_prior_r76.json,v6_r76.stdout.json,v7_guard.json}`
- r78: `corpus/live/r78-baseline/{toolchain.txt,contention-watch.txt,rerun.log,ledger-r78-baseline.tsv}`,
  `corpus/live/r78-scout/`, `corpus/live/r78-scout-playback/`
- Reports audited: `reports/round-77/{r77-adjudicator,r77-author,r77-baseline,r77-critic,r77-reviewer,r77-scribe,r77-simplifier,r77-verifier}.md`,
  `LOG.md` §Round 77, `SCORECARD.md` §r77
