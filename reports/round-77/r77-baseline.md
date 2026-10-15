# R77 baseline — frozen-HEAD replay of the 126-command battery (capture-r76 newest-first)

host: devin (`Linux plazir27 7.2.3-arch1-3`, `toolchain.txt`). Seat: baseline.
Frozen state = `git archive HEAD` of pre-move HEAD **`b0b5d4d`** ("r76
report-last: 9 seat reports + adjudicator + LOG/SCORECARD"). HEAD was
`b0b5d4d` when the archive was cut (19:39:40Z) and stayed there through the
whole replay window (**19:39:57 → 19:49:22 UTC**); it moved to **`503689c`**
("r77 scribe: r76 ledger audit (gates pass, prose corrections logged)", one
path: `reports/round-77/r77-scribe.md`) at 19:56:13Z, i.e. after the replay.
All freeze anchors reference `b0b5d4d` exclusively.

## Frozen archive (receipt, not materialization — never extracted)

`corpus/live/r77-baseline/frozen/head-b0b5d4d.tar` — sha256
`2411cebfbd7fac84dd02acf7c996c8f87c5568c00601d87f7c20e82382ff2af9`
(`frozen/archive-sha256.txt`), **29,050 tar members = 22,375 files + 6,675
directory entries** (`frozen/archive-manifest.txt`). The file set is exactly
`git ls-files` at `b0b5d4d` — 22,375 entries, comm-diff **0 lines** in both
directions (directory entries account for the remaining 6,675 member rows).
Zero `node_modules` members. Same shape as the r76 archive (29,039 members =
22,365 files + 6,674 dirs, +10 files for the r76 report set).

**Committed ledger:** `corpus/live/r70-author/ledger-r71.tsv` — blob
`c4f5c6196f398585f55a8237ab9cbc3f34760621` / sha256
`8d59f552e1370c5e0b50989eacff93e6f4bdf35352a31aa7121616e176579b95`, identical
at `b0b5d4d` and at the moved HEAD `503689c`
(`committed-ledger-sha.{before,after}.txt`). Standing caveat (unchanged since
r73): this ledger is the r70-order battery plus a second `""` normal — no
r71–r76 family rows, and no `capture-r76` row.

**Battery definition:** 126 commands — the r76-baseline ordering verbatim
(125) with `--probe-capture-r76` (committed at `d566a31`, inside `b0b5d4d`'s
history) inserted newest-first at position 02 (`rerun.py`,
`assert len(MODES) == 126`). No committed 126-row ledger exists; r76-author
carries no ledger file. This ordering is the freshest encoding of the full
committed probe surface.

## Replay vehicle — minimal verified materialization

`measure-env/corpus/` — the **663-file tracked-only subset** materialized from
pinned-commit blobs (`build_env.py`): `corpus/fixtures/` (incl. tracked
`__pycache__`), `corpus/artifacts/`, every tracked `corpus/live/round-*/`
fixture, plus an initially-empty `live/runs/`. All **663 byte-equal** to their
`b0b5d4d` blobs (`env-proofs.txt`; `env-filelist.txt` lists the set; direction
checks clean both ways, `env-comm.txt` 0/0). `measure_audio.py:19` anchors
`ROOT = parents[1]` of the fixture file, so all regeneration and receipt writes
stayed inside the env — canonical writes are impossible from it. Ten probed
members/artifacts re-checked byte-equal to `b0b5d4d` blobs **after** the
replay (`post-replay-fixture-check.txt` — 10/10 EQUAL).

## Replay result — prior rows byte-stable; one new row deviates

`rerun.py` ran **19:39:57 → 19:49:22 UTC (9 m 25 s), 126/126 rows**
(`rerun.log`; per-command captures `out/{01..126}.{stdout,stderr}` = 252
files). Outputs: `ledger-r77-baseline.tsv`, `ledger-compare-mode.tsv`,
`ledger-compare-mismatches.txt`, `receipt-compare.tsv`,
`receipt-membership.tsv`, `semantic-compare.txt`, `prior-rows-stable.txt`,
`prior-receipt-compare.tsv`, `receipt-shas.txt`, plus the mechanism probes
below.

- **Counts by exit: 52 × exit 0 / 74 × exit 1** — vs r76's 52/73-on-125 the
  single added row is `capture-r76` at exit 1 (see "the one deviating row").
- **Committed-ledger compare (mode-keyed vs ledger-r71 @ `b0b5d4d`): 120/121
  MATCH** — `ledger-compare-mode.tsv`. The single **EXIT-ONLY** is
  `fifo-hold-ladder-r70`, byte-for-byte the same finding as r74/r75/r76: the
  committed failsum carries a second chunked-flake clause
  (`h=0.05 -> 9x(exit 2, can't find Sun/NeXT/DEC identifier)/1x blocked`) while
  my run produced the clean oneshot distribution
  (`h=0.0 -> 10x(exit None, blocked: no verdict within 10 s)`), verbatim
  identical to the committed oneshot clause.
- **Committed-receipt anchors: 106/121 byte-identical, 15 DIFFER**
  (`receipt-compare.tsv`) — the DIFFER row set and its committed sha prefixes
  are **identical to r76's** (`committed-02 normal`, `committed-03
  fifo-hold-ladder-r70`, twelve `ui-*`, `committed-116 invalid`).
- **Fresh-receipt membership: 109/126** sha256 present in the committed
  same-mode receipt set (`receipt-membership.tsv`); all six fresh `normal`
  receipts are the canonical `8e8cdad6…` (unchanged since r66).
- **17 NOT-INSET receipts:** the 13-mode **path-embedding class** (12 `ui-*` +
  `invalid`; EQUAL-ANCHORED-TAIL on the JSON leaf-walk, zero CONTENT-DIFF —
  `semantic-compare.txt`; the **same 13-mode set as r68–r76**), **plus four
  anchorless modes** — row-02 `capture-r76` (set size 0; new this round),
  row-03 `consumers2-r75`, row-04 `lavfsweep-r74`, row-05 `consumers-r73`.
- **committed-02 `normal`** and **committed-03 `fifo-hold-ladder-r70`**:
  STRUCTURE-DIFF with `only-fresh=[]` — the committed receipts are strict
  supersets from uncommitted impl variants, exactly as r74/r75/r76 recorded.

### Prior-row stability vs the r76 canonical receipts (the round's core check)

The r76-baseline ledger (`corpus/live/r76-baseline/ledger-r76-baseline.tsv`,
125 rows; all 125 receipt files still present) is the prior canonical set —
no committed ledger past ledger-r71 exists. `prior_compare.py`:

- **Row level: 125/125 ROW-STABLE** — every prior mode reproduced with the
  **same exit code and the same failure summary**. Zero exit-only, zero
  no-match, zero missing.
- **Receipt level (fresh r77 receipt vs prior r76 receipt, infix-rewritten):
  110 byte-EQUAL, 13 EQUAL-MOD-PATHS, 2 JITTER-LEAVES, 0 declared-drift,
  0 undeclared-diff, 0 STRUCTURE-DIFF** (`prior-receipt-compare.tsv`).
  - The 110 byte-EQUAL rows are byte-identical across two different displaced
    env trees (these modes embed no absolute path).
  - The 13 EQUAL-MOD-PATHS rows are exactly the 13 path-embedding modes above
    (`ui-*` + `invalid`) — only the env infix differs.
  - The 2 JITTER-LEAVES rows are `lavfsweep-r74` and `consumers-r73`,
    differing only in the declared wall-clock keys
    (`consumer_pwcat_ops2_r74_probe.target0_unlinked_stream.wall_s`,
    `consumer_pwcat_ops_r73_probe.{daemon_gate,pacing_instant}.wall_s`).
  - `prior-undeclared-diffs.txt` was not written: there are no undeclared
    differences.

**Anchorless rows vs canonical sibling receipts** (`semantic-compare.txt`) —
partitions are **identical to r76's**, with the new family added:

- **capture-r76** vs 14 canonical siblings: **14 STRUCTURE-DIFF, 0
  byte-EQUAL** — every sibling is a pre-fold mid-flight variant of the
  twice-folded family (they carry `file.data_declared_field` /
  `file.data_finalized` / `file.duration_bucket_s` / `file.fmt.*` where the
  folded impl at `b0b5d4d` emits `file.kind` / `error` / `stderr_tail`).
  One sibling (`181356*`) has no `measurements.json` at all. No post-fold
  canonical sibling exists: my receipt is the first post-fold capture of this
  family and becomes the next round's reference.
- **consumers2-r75** vs 7 siblings: 6 STRUCTURE-DIFF (pre-fold key names
  `sigterm_immune` vs `alive_after_term1` + `viable_legs`; `171455*`
  additionally carries `failures[]` the folded impl no longer emits),
  **3 CONTENT-DIFF** (`172034*`, `183519*`, `192523*`) — all confined to
  `consumer2_dec_{act,hcom}_r75_probe.consumers.aplay.transport_axis.file.stderr_tail`,
  i.e. the **declared aplay tail-scrub window**.
- **lavfsweep-r74** vs 7 siblings: 3 byte-EQUAL-class JITTER-LEAVES,
  3 STRUCTURE-DIFF (lack `fork_kind`), 1 CONTENT-DIFF
  (`153635*`, `lavf_iss_multi.fork_kind`) — the r76 partition verbatim.
- **consumers-r73** vs 16 siblings: 9 JITTER-LEAVES, 5 STRUCTURE-DIFF
  (`pwcat_name_axis` legs / `stderr_tail` variants), 2 CONTENT-DIFF
  (`153153*`, `154324*`, `daemon_live.default_sink` `.2`-suffix) — the r76
  partition verbatim.

- **Census: env `runs/` = 129 receipts** = the 126 ledger rows plus 3 bounded
  repeat-probe reps (`receipt-shas.txt`); all 126 ledger col-3 paths carry the
  `r77-baseline/measure-env/` infix. Canonical `corpus/live/runs/` held at
  **5,643** through the replay (+0) and reached **5,647** by 19:56Z — the four
  additions are all `capture-r77` receipts from the r77 author's live arm.
  **Zero name overlap** with my env receipts; zero canonical writes by me.
- Committed-ledger guard: blob/sha unchanged before and after.

### Declared host-drift leaves — reproduced and attributed

1. **`capture_gate_r76_probe.inventory.pw_capture_ports`** — my replay row-02
   measured the clean base inventory **12** (8 sink monitors + 4 source
   captures), as did 7 of the 14 canonical siblings. The three repeat-probe
   receipts measured **15** and **16**: the extra entries are one FL/FR pair
   per *concurrent capture client belonging to another seat* —
   `gst-launch-1.0:monitor_MONO` (r77-gst-scout), `parecord:monitor_FL/FR`
   (r77-boundary), `pw-record:monitor_FL/FR`, `Lavf63.1.101:monitor_FL/FR`
   (ffmpeg legs). Canonical siblings show the same pollution
   (`192133*` = 14, `183404*` = 16). This is the r76 reviewer's finding
   (`12 → 16` under concurrent capture) reproduced, with the polluting clients
   named.
2. **aplay tail-scrub window** — 3 CONTENT-DIFF rows on
   `consumers.aplay.transport_axis.file.stderr_tail` against consumers2
   siblings (above); my own receipt is byte-identical to the r76 canonical
   receipt for that mode, so the delta is sibling-window, not mine.
3. **hw contention** — the `capture_roundtrip_r76_probe` content-witness
   episodes below.

### The one deviating row: `capture-r76` roundtrip content witness

Row-02 (`--probe-capture-r76`) is the only fresh row whose `failures` is
non-empty:

```
capture_roundtrip_r76_probe:
  roundtrip content witness deviated (captured pcm silent or level-far from the member)
```

`content_witness = {nonzero_fraction_gt_half: true, peak_within_3db_of_member:
false}`; the captured sink-monitor peak measured **+3.802 dB** above the
member's own peak (bound 3.0 dB). Member `artifacts/stem_sections.wav` peak =
5648/32768 (−15.271 dBFS); sox reports the member at `Volume adjustment:
5.802` and my captured file at `2.000`. All five other capture-r76 arms
(gate, bounded, sever, name_axis, device_axis) were clean — the failures dict
has exactly one key. All 13 canonical siblings with receipts passed the same
witness (captured vol `5.802` = the member's, 0.0 dB delta).

Bounded follow-up probes (all under `corpus/live/r77-baseline/`, all writing
only into the env tree):

| run | reps | over 3 dB | deltas (dB) |
| --- | --- | --- | --- |
| replay row-02 | 1 | 1 | +3.802 |
| `roundtrip_repeat.py` (fixture arm ×3 + direct harness ×3) | 3 + 3 | 1 / 0 | +1.366, +4.312, 0.0 / 0.0 ×3 |
| `residue_probe.py` A/B (clean vs two-member-play residue) | 3 + 3 | 1 / 0 | +3.134, 0.0, 0.0 / 0.0 ×3 |
| `transient_probe.py` (18 reps, shape metrics) | 18 | **5** | +4.459, +3.342, +4.3, +3.195, +4.3 (+1.938, +0.505) |
| `gain_source_probe.py` (12 reps, sink volume/mute logged) | 12 | 0 | 0.0 ×12 |

Level readings in this section use the fixture's own sox `Volume adjustment`
field; `sox-scale-check.txt` verifies it is a true dB level measure (a 6.02 dB
amplitude halving moves it by exactly +6.02 dB, 5.802 → 11.603), so
differences are exact dB deltas and the sign convention is *smaller printed
value = louder capture*.

**Mechanism, as far as this seat can pin it:**

- **Not a uniform gain and not a lone transient.** In the 5 failing reps the
  number of samples above the member's peak is **9,396–39,464** (2–8 % of the
  480,000-sample capture) and the capture RMS rises **+0.05 … +2.56 dB** while
  the peak rises **+3.2 … +4.5 dB** — a *partial-duration elevation of the
  monitored mix*, not a scaled copy of the whole capture.
- **Not prior-playback residue.** The A/B (two full member plays into the
  default sink, then the capture idiom immediately) matched the member
  **3/3 at 0.000 dB**, while the paired clean arm deviated once (+3.134 dB) —
  the residue hypothesis is falsified.
- **Not the sink volume/mute.** 12/12 reps at 0.000 dB with the SPDIF sink
  pinned at 40 % / −23.88 dB, unmuted, before *and* after every rep
  (`gain-source.txt`). The monitor is pre-volume (the captured peak equals the
  member's unattenuated peak, not 40 % of it).
- **Not the capture-port pollution.** The replay row deviated with the clean
  12-port inventory; repeat rep 2 deviated at 15 ports; repeat rep 3 passed at
  16 ports.
- **Episodic, not per-run.** The deviations arrive in bursts: 5 of 18
  consecutive reps deviated in 19:55:52–19:57:40Z, then **0 of 12** in
  19:57:50–19:59:00Z, and 0 of 3 + 0 of 6 in two earlier windows. Across all
  43 standalone-idiom reps this seat ran, **8 exceeded the 3 dB bound
  (18.6 %)**.
- **Every burst coincides with multi-seat concurrent audio probing on this
  host.** The 19:40:43Z replay row overlapped the r77 author's scratch WAV
  work (`link.wav` 19:40:06Z, `pwcat.wav`/`pwcat2.err` 19:41:18Z, `sev*.wav`,
  `syn.wav`, `dump.wav`) and r77-boundary probe files; the 19:51–19:52Z
  repeat window overlapped the boundary chain with the default sink moved to
  the Speaker sink at 19:51:08Z and up to 11 audio processes; the 19:55:40–
  19:57:40Z burst overlapped r77-boundary, r77-author and a **new r78-scout**
  seat. The scout independently measured the same class on this host
  (`ffmpeg` monitor capture peak 26230 vs a 16384 member tone = +4.1 dB,
  §7 of `reports/round-77/r77-scout.md`).

The producer of the extra mix content is **not pinned by this seat** — the
host carried 9–11 concurrent audio processes belonging to other seats for the
whole window, and this seat cannot isolate them. The class is named and
bounded: *intermittent, partial-duration elevation of the monitored sink mix,
+3.2…+4.5 dB peak, arriving in multi-seat-contention episodes, on an idiom
(`play into the sink while capturing its monitor`) that the r77 author's arm
also uses.*

**Drift verdict: zero prior-row drift.** Every delta from the r76 canonical
receipts is one of the known classes (path-embedding ×13; wall-clock jitter
×2). The single non-canonical row is a **new** row (`capture-r76`, absent from
the 125-row prior ledger) whose deviation is the declared host-drift class
above, not an implementation change: the frozen impl's five other capture arms
and all 125 prior rows reproduced exactly.

## Post-commit re-verification (r77 work commit `65790f13`, landed 20:10:35 UTC)

- **`65790f13e75a69afb2ef2b3ccdb1fd488d778eff`** — "r77 work: capture-source
  lattice + fallback law + reader matrix". `postcommit-verify.txt`:
  - `ledger-r71.tsv` blob `c4f5c619…` / sha256 `8d59f552…` **unchanged** at both
    commits.
  - `git ls-tree -r corpus/live/runs`: **5,290 rows old and new, object-id
    diff = 0 lines** — every committed receipt byte-identical across the move.
  - **7 changed paths, +4,398 / −2**: `corpus/fixtures/measure_audio.py` plus
    six reports. **Zero `corpus/live/runs/` paths.**
  - `measure_audio.py`: **1,552 added lines, 2 deleted lines**, and both
    deletions are the dispatch wiring chains (`mode =` and `suffix =`), each
    replaced by the same chain extended with `args.probe_capture_r77` /
    `"probe-capture-r77"` / `"-capture-r77"`. Insertion-only guard holds.
  - New mode wired at `:5798` (argparse), `:6092` (dispatch), `:6597` (mode
    chain), `:6617` (suffix chain); six new entry functions
    (`capture_source_lattice_r77_entry`, `capture_target_loss_r77_entry`,
    `capture_readers_r77_entry`, `capture_arecord_sever_r77_entry`,
    `capture_split_sentinel_r77_entry`, `capture_format_axis_r77_entry`).
  - **The r76 arm is code-identical across the move**: `capture_gate_r76_entry`
    `586ff653f273`, `capture_bounded_r76_entry` `9f422bd88443`,
    `capture_sever_r76_entry` `0f5cbc9287ab`, `capture_name_axis_r76_entry`
    `9826bcfd2812`, `capture_device_axis_r76_entry` `c421555e3543`,
    `capture_roundtrip_r76_entry` `01c370996d52`, and the shared helpers
    `_capture_wav_inspect` `31055c757a3b`, `_capture_inventory` `653a23ed08b0`,
    `aplay_leg` `a752d174479b`, `transport_leg` `4e7666042318` — all unchanged
    (per-function sha256 of the extracted source at both commits).

### Post-commit replay (same 126-command battery, post env pinned to `65790f13`)

`build_env_post.py` materialized 663/663 files byte-equal to `65790f1` blobs
(`env-post-proofs.txt`, comm checks 0/0); `rerun_post.py` imports `MODES` from
`rerun.py`, so **row N of the post ledger is the same flag as row N of the
Phase-1 ledger** and the comparison is index-exact. Ran **20:12:4x → 20:22:31
UTC (9 m 45 s), 126/126 rows** (`rerun-post.log`, `out-post/` 252 captures).

- **Counts by exit: 53 × exit 0 / 73 × exit 1** — vs Phase 1's 52/74. The
  single flipped row is **row-02 `capture-r76`**: Phase 1 exited 1 with the
  roundtrip content-witness failure, the post run exited 0 with `failures: {}`
  (the witness passed). Same frozen code (the r76 arm is byte-identical across
  the commit), same battery — this is the intermittent class above, not a
  commit effect.
- **(a) post vs Phase-1, index-exact: 125/126 ROW-STABLE** on (exit,
  failure-summary); the one ROW-DIFF is row-02, as above.
  Receipt-level: **110 EQUAL, 13 EQUAL-MOD-PATHS, 1 DECLARED-DRIFT,
  1 JITTER-LEAVES, 1 STRUCTURE-DIFF, 0 undeclared**
  (`post-receipt-compare.tsv`, `post-undeclared-diffs.txt` not written).
  - the DECLARED-DRIFT row is row-03 `consumers2-r75`, differing only in the
    two `consumers.aplay.transport_axis.file.stderr_tail` leaves (the declared
    aplay tail-scrub window);
  - the JITTER-LEAVES row is row-05 `consumers-r73`
    (`consumer_pwcat_ops_r73_probe.pacing_instant.wall_s` only);
  - the STRUCTURE-DIFF row is row-02: the **bounded** arm's per-leg key sets
    differ because a device-dependent `arecord` leg produced a file in one run
    and errored in the other (`…arecord_duration_hw.file.{bytes,data_actual,
    data_declared,…}` vs `…arecord_duration_hw.{error,file.kind}`) — a
    host-dependent leg *outcome*, not a code path (the entry function is
    byte-identical across the commit, proven above).
  - `pw_capture_ports` inventory: **12 in both runs** (clean base inventory in
    both windows).
- **(b) post vs the r76 canonical receipts: 125/125 ROW-STABLE** — every one of
  the 125 prior modes again reproduced with identical exit and identical
  failure summary on the committed post-move bytes. Receipt-level: **109
  EQUAL, 13 EQUAL-MOD-PATHS, 2 JITTER-LEAVES, 1 DECLARED-DRIFT, 0 undeclared**.
  The one DECLARED-DRIFT is `consumers2-r75`'s aplay `stderr_tail` leaves —
  i.e. the post run's aplay tail window differs from the r76 canonical window
  by exactly the declared leaf, and nothing else.

### Finding for the round: `--probe-capture-r77` escapes the exclusivity guard

Evidence-only (this seat makes no tracked edits) — `exclusivity-check.txt`:

- The guard at `measure_audio.py:5801` is
  `if sum([… , args.probe_consumers2_r75, args.probe_capture_r76]) > 1:
  parser.error("choose one probe mode")` — **`args.probe_capture_r77` is not in
  the sum.** The two dispatch blocks are independent:
  `:6092 if args.probe_capture_r77:` and `:6111 if args.probe_capture_r76:`.
- Dynamic A/B on the post-commit fixture (`measure-env-post`):
  - control, two *guarded* flags
    (`--probe-consumers2-r75 --probe-capture-r76`) → **rc=2, guard fires**
    ("choose one probe mode" + usage).
  - `--probe-consumers2-r75 --probe-capture-r77` → **rc=124 (ran to the
    15 s bound), guard does not fire**.
  - `--probe-capture-r77 --probe-capture-r76` → **rc=124 (ran to the 15 s
    bound), guard does not fire**.
- Consequence, from the two independent dispatch blocks: any pairing of
  `--probe-capture-r77` with another probe flag passes the guard and executes
  **both** families in one process, producing one receipt whose `mode`/`suffix`
  claim `capture-r77` (the chain orders r77 first) while its `measurements`
  carries both families' keys — and the r76 roundtrip's own playback lands
  inside the r77 receipt (a self-inflicted mix confound of exactly the class
  that broke row-02's witness). The both-families-execute step is **derived
  from the two dispatch blocks and the guard text, not executed to completion**
  by this seat: running the pair to a finished receipt would exercise the r77
  split-sentinel leg's ~2 GiB crossing write, which this seat declined to
  spend on a shared host. Flagged for the author/reviewer; not corrected here.



## Live-tree events during the window (observed, not mine)

- `b0b5d4d` held as HEAD for the entire replay. `503689c` (r77 scribe,
  report-only) committed 19:56:13Z; `corpus/fixtures/measure_audio.py` was
  live-dirty (` M`, worktree sha256 `138290fd…` vs frozen blob `c35e2c62…`)
  from ~19:56Z — the r77 author's in-flight work commit; it landed as
  **`65790f13`** at 20:10:35Z (`head-moved.txt`), after the Phase-1 replay and
  before the post-commit replay. My env runs pinned `git show` blobs at both
  anchors, so neither replay surface was affected (all 126 Phase-1 receipts
  carry the frozen-env infix, all 126 post receipts the post-env infix; 10/10
  fixture re-check EQUAL in the frozen env).
- Canonical `corpus/live/runs/` 5,643 → 5,647: four `capture-r77` receipts
  (19:46:52Z, 19:49:26Z, 19:53:09Z, 19:55:45Z) — the r77 author's arm with the
  new mode. No committed receipt blob changed (committed count 5,290 at both
  commits).
- Sibling seats live on the shared audio stack throughout: r77-author,
  r77-boundary, r77-scout (until ~19:28Z), r77-gst-scout, and r78-scout from
  ~19:56Z. `contention-watch.txt` samples host/audio state every 30 s;
  `commit-watch.txt` logs every distinct HEAD.
- Pre-existing uncommitted state persists untouched (`pre-state.txt` /
  `post-state.txt`, 411 untracked entries).

## Toolchain + consumer-class viability (measured)

`SoX_ng v14.8.0.1`, `ffmpeg/ffprobe n9.0.1`, `python3 3.14.7` + `numpy 2.5.3`,
`libsndfile.so.1`, `pw-cat` w/ libpipewire **1.6.8**, `mpv v0.41.0`, `pactl`
Server Version 15.0.0 (PulseAudio-on-PipeWire), default sink
`alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink` at 40 % / −23.88 dB
unmuted. PipeWire daemon pids `1203634/1203790` throughout — the same pair
r76 recorded; no restart inside my window.

## Write-scope accounting

Wrote only: this report; `corpus/live/r77-baseline/` (`frozen/`
head-b0b5d4d.tar + manifest + sha — ignored dir per `corpus/.gitignore`,
receipt only, never extracted; `measure-env/` 663 verified files + 129 receipt
dirs; `measure-env-post/` 663 verified files + 126 post receipts;
`build_env.py`, `build_env_post.py`, `rerun.py`, `rerun_post.py`, `rerun.log`,
`rerun-post.log`, `ledger-r77-baseline.tsv`, `ledger-r77-baseline-post.tsv`,
`out/` 252 captures, `out-post/` 252 captures, `compare.py`, `prior_compare.py`,
`semantic_compare.py`, `post_compare.py`, `postreplay_check.py`,
`postcommit_verify.py`, `contention_watch.py`, `commit_watch.py`,
`roundtrip_repeat.py`, `quiescent_repeat.py`, `residue_probe.py`,
`transient_probe.py`, `gain_source_probe.py`, `post-measure_audio.py`
(post-commit fixture copy, read-only use), and their outputs:
`ledger-compare-mode.tsv`, `ledger-compare-mismatches.txt`,
`receipt-compare.tsv`, `receipt-membership.tsv`, `semantic-compare.txt`,
`prior-rows-stable.txt`, `prior-receipt-compare.tsv`,
`post-rows-stable.txt`, `post-receipt-compare.tsv`, `exclusivity-check.txt`,
`receipt-shas.txt`, `roundtrip-repeat.txt`, `residue-ab.txt`,
`transient-shape.txt`, `gain-source.txt`, `sox-scale-check.txt`,
`contention-watch.txt`, `commit-watch.txt`, `env-filelist.txt`,
`env-proofs.txt`, `env-comm.txt`, `env-post-filelist.txt`,
`env-post-proofs.txt`, `env-post-comm.txt`, `post-replay-fixture-check.txt`,
`committed-ledger-sha.{before,after}.txt`, `postcommit-verify.txt`,
`head-moved.txt`, `toolchain.txt`, `pre-state.txt`, `post-state.txt`,
`runs-canonical-{before,after,added}.txt`). No canonical
`corpus/live/runs/` writes, no tracked-file edits, no commits, no pushes.
Leaf seat. One read-only `labrat` probe was dispatched by this seat (the
frozen probeParent allowance, exactly one) — a deliberately **audio-free**
independent re-derivation of this report's four central claims, so it could not
add capture clients to the monitor under measurement; no other descendant was
spawned.

## Independent corroboration (one read-only labrat probe)

The seat's frozen probeParent allowance was spent on exactly one read-only
`labrat`, tasked to **falsify** the central claim — deliberately audio-free (no
playback/capture), because a probing descendant would have added capture
clients to the monitor under measurement. Its hypothesis: *"the r77 baseline's
prior-row stability claim is overstated or wrong."* **Not falsified.**

- **Row-level stability — CONFIRMED independently.** The labrat re-derived it
  with its own method (read all three ledgers in full, key by mode, compare
  `(exit, failsum)` verbatim): **0 mismatches across all 125 paired modes** for
  *both* the frozen-env ledger and the post-commit ledger, with `capture-r76`
  correctly excluded as the one unpaired mode, and it verified the mode
  multiset is otherwise identical (mode `normal` ×6 in all three ledgers).
- **Failed falsification attempts** (evidence in themselves): no exit/failsum
  divergence found in any paired row; no extra or missing mode beyond
  `capture-r76`.
- **What it could not check, and why:** the labrat substrate exposes only
  read/grep/glob — no shell — so `git`, `tar`, and `sha256sum` were
  unavailable. Receipt-level byte-classes (claim 3) were therefore only
  *corroborated* from this seat's own artifacts, not re-derived; it confirmed
  the published class counts sum correctly to 125 in both directions and that
  the pre/post class sets are distinguished correctly (110 EQUAL / 0
  DECLARED-DRIFT pre vs r76; 109 EQUAL / 1 DECLARED-DRIFT post vs r76).
- **Its one apparent falsification, resolved:** the labrat reported
  `corpus/live/r77-baseline/frozen/head-b0b5d4d.tar` as **absent** (and could
  not find any `*.tar` under `r77-baseline/`). The tar is present on disk —
  **345,763,840 bytes**, `frozen/archive-sha256.txt`
  `2411cebfbd7fac84dd02acf7c996c8f87c5568c00601d87f7c20e82382ff2af9` — and is
  **gitignored** by `corpus/.gitignore:5 (live/*/frozen/)`, which the labrat's
  gitignore-respecting glob does not traverse (the r76 analog
  `r76-baseline/frozen/head-2250be9.tar` is hidden by the same rule; the r75
  analog is visible only because it sits outside that pattern, under
  `recovery-prior/`). The "absence" is a **tool-visibility artifact, not a
  missing receipt** — recorded here rather than silently dropped.
- **Nit closed:** the labrat observed that the frozen env's `env-comm.txt` did
  not print its pin string (unlike `env-post-comm.txt`, which does).
  `env-comm.txt` now carries
  `pin=b0b5d4d5c8bfd3356fb6c761cae7f40d0978d588` on its first line.
- Its reading of `ledger-compare-mismatches.txt` (the single
  `fifo-hold-ladder-r70` EXIT-ONLY) does not contradict any claim here: that
  row is a *fresh receipt vs committed receipt* difference (documented above as
  the load-dependent band), not a prior-row instability, and the
  object-identity claim concerns the **committed** receipt blobs across the
  author move (0-line `ls-tree` diff), not fresh-vs-committed byte equality.

## Residual gaps

- **No quiescent window was ever available on this host.** `quiescent_repeat.py`
  was aborted before its first rep (host never reached 3 consecutive
  quiet samples; see `quiescent-repeat.log`) and superseded by the A/B control,
  which is internally paired and therefore contention-robust. The
  roundtrip-witness episode therefore has a **named class and a bounded rate,
  not a pinned producer**.
- The 13 path-embedding receipts can never raw-match off the canonical path;
  anchored-tail JSON compare is the strongest displaced-tree check (unchanged
  since r68).
- Committed ledger-r71 row-02 anchors a receipt no frozen tree can reproduce
  (uncommitted-impl artifact); flagged, not correctable from this seat.
- `capture-r76`, `consumers2-r75`, `lavfsweep-r74`, `consumers-r73` have **no
  committed receipt anchor**; sibling-receipt compares stand in. For
  `capture-r76` all 14 siblings are pre-fold variants, so my receipt is the
  first post-fold capture and becomes the next round's reference.
- `fifo-hold-ladder-r70` remains a load-dependent band: this run landed the
  canonical stable oneshot signature; occasional EXIT-ONLY failsum drift
  expected.
- The consumers-r73 `daemon_live.default_sink` leaf is environment-live —
  expect CONTENT-DIFF vs `.2`-suffixed siblings whenever the USB sink
  re-enumerates or another seat moves the default sink (observed this round
  via r77-boundary's `p1b_moved` arm moving the default sink to the Speaker
  sink at 19:51:08Z).
- **The post-commit battery deliberately excludes `--probe-capture-r77`**: the
  post replay isolates "did the author commit change any prior row", so row N
  of the post ledger is the same flag as row N of the Phase-1 ledger. Folding
  the new family into the battery (a 127-row ledger, `capture-r77` newest-first
  at 02) is the next round's decision, and the four canonical `capture-r77`
  receipts already on disk from the author's own arm are its first siblings.
- **The exclusivity-guard gap is reported, not corrected** (this seat makes no
  tracked edits), and its "both families execute" consequence is derived from
  the guard text plus the two independent dispatch blocks rather than executed
  to a finished receipt — running the pair to completion would spend the r77
  split-sentinel leg's ~2 GiB crossing write on a shared host.
- **The roundtrip content-witness idiom is the round's live idiom** (the r77
  author's arm uses the same play-into-sink-while-capturing-its-monitor shape).
  This seat's 43 standalone reps put the 3 dB bound's false-alarm rate at
  8/43 (18.6 %) on this host, in multi-seat-contention episodes; a witness that
  is meant to certify "the capture carried the member" should not be read as
  evidence of an impl defect when it fires without a contention check.
