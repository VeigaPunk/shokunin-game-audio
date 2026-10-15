# R78 baseline — Phase-1 freeze + replay of the 127-command battery at `731937c`

host: devin (`Linux plazir27 7.2.3-arch1-3`, `toolchain.txt`). Seat: baseline.
Phase 1 only: this seat froze the tree, replayed the full prior battery plus the
folded-in r77 capture family, and characterised the host-topology environmental
set. Phase 2 (re-run against the **landed** r78 arm) is gated on that commit
landing; the harness for it is built and idle (see §11).

## 1. Frozen state and archive (receipt, never extracted)

Frozen anchor = **`731937ccf731c711b54942d22ae4f32b7683c498`** ("r77
report-last: adjudicator + LOG + SCORECARD (ADMIT-corr)"). HEAD was `731937c`
when the archive was cut (21:27:24Z) and stayed there through the whole replay
window (**21:27:55 → 21:40:22 UTC**); it moved to **`bdf748e33`** ("r77 fold-2:
provenance witness regression + record corrections (scribe 5.1-5.6)", 5 paths,
`measure_audio.py` +27/−3) at **21:40:47Z**, i.e. 25 s after the replay ended
(`archive-check.txt`, `commit-watch.txt`). All Phase-1 anchors reference
`731937c` exclusively; every ledger receipt carries the `r78-baseline/measure-env/`
infix, so no Phase-1 row can be attributed to the later commits.

- `frozen/head-731937c.tar` — **346,296,320 bytes**, sha256
  `b9ede943ec1a4a6d0f82bbee3a1b46a99d300ae7e0b284b1657b3d4fb03c6e05`
  (`frozen/archive-sha256.txt`), **29,059 tar members = 22,382 files + 6,677
  directory entries** (`frozen/archive-manifest.txt`). The file set is exactly
  `git ls-tree -r -z` at `731937c` — 22,382 entries, symmetric difference **0**
  (raw NUL-separated names; a whitespace-split compare fakes a 16-entry diff on
  the `r63-simplifier/scratch/*` names that contain spaces — recorded in
  `archive-check.txt`). Zero `node_modules` members.
- **Committed ledger:** `corpus/live/r70-author/ledger-r71.tsv` — blob
  `c4f5c6196f398585f55a8237ab9cbc3f34760621`, identical at `731937c` and at the
  moved HEAD `bdf748e` (`archive-check.txt`). Standing caveat (unchanged since
  r73): this ledger is the r70-order battery plus a second `""` normal — no
  r71–r77 family rows, no `capture-r76`/`capture-r77` rows.
- **Battery definition:** **127 commands** — the r77-baseline ordering verbatim
  (126: r76-baseline's 125 with `--probe-capture-r76` newest-first at 02) with
  `--probe-capture-r77` inserted newest-first at position 02, so the two capture
  families are rows 02 (r77) and 03 (r76). `MODES` is **imported from
  `../r77-baseline/rerun.py`** (`rerun.py`, `assert len(MODES) == 127`), so row
  N of this ledger is the same flag as row N of the r77 Phase-1 ledger for
  N ≥ 3 and row 01 is `normal` in both. This is the "fold the new family into
  the battery" decision the r77 baseline deferred to this round.

## 2. Replay vehicle — minimal verified materialization + fixture hashing

`measure-env/corpus/` — the **663-file tracked-only subset** materialized from
pinned-commit blobs (`build_env.py`): `corpus/fixtures/` (**including the two
tracked `__pycache__` `.pyc` files**), `corpus/artifacts/`, every tracked
`corpus/live/round-*/` fixture, plus an initially-empty `live/runs/`. All **663
byte-equal** to their `731937c` blobs (`env-proofs.txt`; `env-filelist.txt`);
direction checks clean both ways, `env-comm.txt` 0/0. `measure_audio.py:19`
anchors `ROOT = parents[1]` of the fixture file, so all regeneration and receipt
writes stayed inside the env — canonical writes are impossible from it.

**Fixture hashing at freeze** (`fixtures-hash.txt`, captured 21:27:22Z before
the replay): all **22 tracked files** under `corpus/fixtures` + `corpus/artifacts`
byte-equal to their `731937c` blobs (worktree clean for those paths), 0 DIFF —
this includes `__pycache__/measure_audio.cpython-314.pyc` and
`__pycache__/build_artifacts.cpython-314.pyc`. Post-replay re-check
(`post-replay-fixture-check.txt`) shows the *live* tree later diverged —
`measure_audio.py` and its `.pyc` DIFF against the frozen blobs — which is the
r78 author's in-flight arm (§9), not a Phase-1 env change: the env was
materialized from blobs and re-verified 663/663 EQUAL.

## 3. Replay result — prior cells byte-stable; one row is the environmental set

`rerun.py` ran **21:27:55 → 21:40:22 UTC (12 m 27 s), 127/127 rows**
(`rerun.log`; per-command captures `out/{01..127}.{stdout,stderr}` = 254 files).
Counts by exit: **53 × exit 0 / 74 × exit 1** — vs r77 Phase-1's 52/74 on 126
rows: the added row is row-02 `capture-r77` at exit 0, and row-03 `capture-r76`
stayed exit 1 (same exit as its r77 predecessor, different failure summary).

Outputs: `ledger-r78-baseline.tsv`, `ledger-compare-mode.tsv`,
`ledger-compare-mismatches.txt`, `receipt-compare.tsv`,
`receipt-membership.tsv`, `semantic-compare.txt`, `prior-rows-stable.txt`,
`prior-receipt-compare.tsv`, `prior76-receipt-compare.tsv`, `receipt-shas.txt`,
`env-diff.txt`, `capture76-leg-diff.txt`, `census.txt`, `archive-check.txt`,
`fixtures-hash.txt`, plus the mechanism probes below.

### (a) vs the r77-baseline Phase-1 canonical set (index-exact)

Mapping: row 01 ↔ row 01; row N+1 ↔ r77 row N for N ≥ 2 (`prior_compare.py`).

- **Row level: 125/126 ROW-STABLE** — every prior mode reproduced with the
  **same exit code and the same failure summary**. The one exception is
  **row-03 `capture-r76`: ROW-EXIT-ONLY** — exit **1 in both**, but the
  failure summary moved from r77's single roundtrip-content-witness failure to
  the **environmental set** (§5). Zero ROW-NO-MATCH, zero missing.
- **Receipt level: 110 byte-EQUAL, 13 EQUAL-MOD-PATHS, 1 JITTER-LEAVES,
  2 ENV-STRUCTURE, 0 declared-drift, 0 undeclared** (`prior-receipt-compare.tsv`;
  `prior-undeclared-diffs.txt` **not written — there are none**).
  - The 110 byte-EQUAL rows are byte-identical across two different displaced
    env trees.
  - The 13 EQUAL-MOD-PATHS rows are the path-embedding class: twelve `ui-*` rows
    plus `invalid` (same set as r68–r77).
  - The 1 JITTER-LEAVES row is `consumers-r73`
    (`consumer_pwcat_ops_r73_probe.{daemon_gate,pacing_instant,pacing_trickle}.wall_s`).
  - The 2 ENV-STRUCTURE rows are **row-03 `capture-r76`** (114 only-fresh / 38
    only-prior leaves: `env=66, contention=58, drift=24, failures=4`, zero
    unclassified) and **row-04 `consumers2-r75`** (4 only-fresh leaves, all
    `env`: `device_census.playback_devices[12].{card,card_id,card_name,device}`
    — the DualSense playback device now enumerated by `aplay`).

### (b) vs the r76-baseline canonical set (mode-keyed)

- **Row level: 125/125 ROW-STABLE** — every one of the 125 prior modes again
  reproduced with identical exit and identical failure summary on the
  `731937c` bytes. (No `capture-r76` row exists in that ledger.)
- **Receipt level: 109 byte-EQUAL, 13 EQUAL-MOD-PATHS, 2 JITTER-LEAVES,
  1 ENV-STRUCTURE, 0 undeclared** (`prior76-receipt-compare.tsv`). The two
  JITTER-LEAVES rows are `lavfsweep-r74` and `consumers-r73` (the r76/r77
  declared wall-clock keys); the ENV-STRUCTURE row is `consumers2-r75` again.

### Committed-anchor comparison (`731937c`)

- **Committed ledger (`ledger-r71.tsv`, 121 rows) mode-keyed: 120 MATCH,
  1 EXIT-ONLY** — `fifo-hold-ladder-r70`, byte-for-byte the same finding as
  r74/r75/r76/r77: the committed failsum carries a second chunked-flake clause
  while the run lands the canonical stable oneshot distribution. Load-dependent
  band, unchanged.
- **Committed receipt set @ `731937c` = 5,290 blobs: 109/127 fresh receipts
  byte-INSET; 2 EQUAL-MOD-PATHS; 11 DIFFER; 5 NO-COMMITTED-MODE**
  (`receipt-compare.tsv`). The 11 DIFFER rows are `ui-*` (leaf-walk
  EQUAL-ANCHORED-TAIL — `semantic-compare.txt`), and the 5 anchorless modes are
  the known set: `capture-r77` (new), `capture-r76`, `consumers2-r75`,
  `lavfsweep-r74`, `consumers-r73`.
- **Sibling partitions** (`semantic-compare.txt`), unchanged in shape from r76:
  `capture-r76` 19 STRUCTURE-DIFF — every comparable sibling of the 20 canonical
  dirs (one, `20261014T181356386452Z`, carries no `measurements.json`, exactly
  as r77 recorded) is a pre-fold or mid-flight variant; `capture-r77` 13
  STRUCTURE-DIFF (of 13); `consumers2-r75` 9 STRUCTURE-DIFF (of 9);
  `consumers-r73` 9 JITTER-LEAVES + 5 STRUCTURE-DIFF + 2 CONTENT-DIFF
  (`daemon_live.default_sink`, the environment-live leaf, vs the `.2`-suffixed
  siblings); `lavfsweep-r74` 3 JITTER-LEAVES + 3 STRUCTURE-DIFF + 1 CONTENT-DIFF
  (`lavf_iss_multi.fork_kind`). No sibling compare produced an undeclared class.

## 4. The environmental set (named in the brief, enumerated here)

The host topology changed since r76/r77: **the Sony DualSense wireless
controller became the default SOURCE** (`pactl info`: `Default Source:
alsa_input.usb-Sony_Interactive_Entertainment_DualSense_Wireless_Controller-00.Direct__Direct__source`;
`Default Sink` unchanged, SPDIF at 40 % / −23.88 dB, unmuted). It also adds a
third capture card and a playback sink. `capture76-leg-diff.txt` enumerates
every differing leaf of row-03 against its r77 reference receipt, bucketed:

| bucket | leaves | what it is |
| --- | --- | --- |
| env | 66 | inventory + plugin-route + argv/source-name leaves (below) |
| contention | 58 | hw-device busy/free, `ffmpeg_alsa_t`, aplay-tail, witness |
| drift | 24 | `stderr_tail` scrub windows (declared since r68) |
| failures | 4 | the entry-level failure summaries themselves |
| unclassified | **0** | — |

**Named environmental legs.** The complete per-leg enumeration with both values
is `capture76-leg-diff.txt` (306 lines); the bucket totals above are the
exhaustive statement (0 unclassified). What follows names the *mechanisms*, and
the six legs whose **verdict** flipped are the ones the row reports as failures:

1. `capture_gate_r76_probe.gate.parec_no_device` — was `(1, pa_no_such_entity)`
   "No such entity"; now **blocked** (`exit_code: null`, "blocked: no verdict
   within 10 s") because a default source now resolves and `parec --raw` (no
   `-d`) records from it. This is the gate's only reported failure.
2. `capture_gate_r76_probe.gate.parecord_no_device` — same cause, now
   `blocked: true` (`exit_code: null`, 15 s bound) with an **unfinalized WAV
   whose data-size field is still a placeholder** (`riff_size_field:
   "placeholder_8"`, `data_declared_field: "zero"`, `data_finalized: false`,
   `duration_bucket_s: 13.25` — it recorded ~13 s into the file before the
   bound). The gate does **not** report it (its loop skips any leg carrying
   `blocked`), so it appears as a content deviation, not a failure — worth
   knowing when reading the gate.
3. `capture_gate_r76_probe.gate.arecord_default` and `…gate.arecord_pipewire` —
   were `(1, alsa_hwparams)` / `TICK_TIME: [0 0]`; now **rc=0 with a real
   1 s / 192,044 B WAV**. The plugin routes that were *blocked for capture* in
   r75/r76 now capture, because a working default source exists.
4. `capture_device_axis_r76_probe.legs.default` and `…legs.pipewire` — the same
   two routes, same flip (rc 1 → 0, file appears). These are the two device-axis
   failures reported by the row.
5. **Inventory leaves (21)**: `sources` += DualSense source; `default_source`
   changed; `monitors` += DualSense monitor; `pw_capture_ports` += its
   `monitor_F{LR}` pair; `alsa_capture_devices` += `{card 3, "Controller",
   device 0}`; `alsa_plugins` += `sysdefault:CARD=Controller`,
   `front:CARD=Controller,DEV=0`.
6. **Target-name leaves**: every leg that resolves its target through
   `_capture_leg_targets()` — which prefers `default_source` — now names the
   DualSense instead of the USB Line source: `bounded.legs.pwrecord_sample_bound`,
   `gate.pwrecord_dead_daemon`, all four `name_axis.legs.pwrecord_*`,
   `sever.cells.{pwrecord,ffmpeg}_{term,kill}` (`argv`). This is why the row's
   content leaf set moves without any implementation change.
7. `consumers2-r75`: `device_census.playback_devices[12]` (the DualSense sink,
   card 3) — the same topology change seen from the `aplay -l` census.

Beyond those six verdict flips, the same row carries ~25 further differing leg
groups — `device_axis.legs.{hw_first,hw_first_mono,plughw_first,sysdefault}`,
`gate.{ffmpeg_alsa_default,ffmpeg_pulse_default}`, the `name_axis` `pwrecord_*`
and `parecord_*` legs, `sever.cells.{pwrecord,ffmpeg,arecord}_*`, and
`bounded.legs.ffmpeg_alsa_t` — each of which is either the same source-name
substitution (mechanism 6) or a declared contention class (below), and none of
which introduces a new/renamed key, a changed threshold, or a changed expected
value (`capture76-leg-diff.txt`; independently re-walked by the §10 probe).

**Declared contention classes in the same row** (not environmental): the
`hw:0,0` device legs (`device_axis.legs.{hw_first,plughw_first,sysdefault,
hw_first_mono}`, `bounded.legs.ffmpeg_alsa_t`, `sever.cells.arecord_{term,kill}`)
were `alsa_busy` in the r77 reference and are rc=0 in this run — the reference
was taken while another seat held the PCM, and the sever entry's device
iteration therefore landed `hw:0,2` there vs `hw:0,0` here (its
`arecord_contention` list is present in the reference and absent here). The
roundtrip witness **passed** in this run (`peak_within_3db_of_member: true`,
sox `Volume adjustment: 5.802` = the member's own level) where the r77 Phase-1
run failed it at +3.802 dB — the same multi-seat contention episode r77
documented; the fresh row's `failures` does **not** contain it.

**Drift verdict: zero prior-cell drift.** Every prior row either reproduced
byte-identically (110), differed only by the env infix (13), differed only in
declared wall-clock keys (1), or differed structurally *within the named
environmental/contention leaf set* (2). **No undeclared difference exists in
either direction.**

## 5. The one deviating row — `capture-r76` (row 03)

```
prior (r77 Phase-1, 20261014T194043238882Z): exit 1
  capture_roundtrip_r76_probe: roundtrip content witness deviated
fresh (r78 Phase-1, 20261014T213136105621Z): exit 1
  capture_gate_r76_probe: gate parec_no_device: expected (1,pa_no_such_entity) got (None,None)
  capture_device_axis_r76_probe: arecord -D default: expected the set_params:1462 capture block or a busy
  capture_device_axis_r76_probe: arecord -D pipewire: expected the set_params:1462 capture block or a busy
```

Both exits are 1, so **no row flipped its exit code**. The fresh failures are
exactly the environmental legs 1/3 above — the row is *reporting the host change
correctly*, which is the point: the r76 gate/device-axis expectations encode the
pre-DualSense host. All five other r76 arms (`bounded`, `sever`, `name_axis`,
`roundtrip`, plus the gate's other legs) produced their expected verdicts; the
only content-level deltas in them are the source-name/`argv` leaves (6) and the
declared contention leaves.

Receipt shas: fresh `b568d7665ee26391656ad0aa1df7db6211f1742a5d2322f6ea291312be35ff99`;
r77 reference `corpus/live/r77-baseline/…/20261014T194043238882Z-capture-r76`.

## 6. The r77 receipt as reference (row 02, `capture-r77`)

The assignment's "record the r77 receipt as reference" — the r77 family's
canonical reference is the **folded-run receipt
`corpus/live/runs/20261014T210316456683Z-capture-r77`**, sha256
`09ecf6e6bd722ce83006cf362a0b903b7a72f4a94ef119b13fb30edc88e4852c`.

- **Fresh row-02 receipt**: exit 0, `failures: null` (all six probes clean),
  sha256 `08c6e9d1c954f9e0d128f6d684ccbdf3aa9dd5963d065327a789fb99a150175b`.
- **vs the folded reference** (`env-diff.txt` §2): **only-fresh = 0**; the 8
  only-ref leaves are `capture_source_lattice_r77_probe.inventory.{sinks,monitors}`
  entries `r78p_ns`, `r78p_ns2` — **the r78 scout's probe sinks, loaded
  concurrently while that reference was captured** (declared contention class:
  concurrent seat's null sinks appear in the inventory). Plus the bounded
  `arecord_sever` frame-count leaves (18,033 vs 18,035 frames — 2-frame jitter)
  and the per-pid `target_loss` sink name / payload sha (the r77 fold's
  per-process sink naming convention).
- **vs all 13 canonical siblings**: 13 STRUCTURE-DIFF — every sibling is a
  mid-flight variant of the moving r77 impl (they carry
  `failures[]`/`target_object_prop`/`alsa_busy_cells`/`confound_observed` keys
  the folded impl no longer emits, or lack `contention`/`frames_per_second`).
  The two newest siblings (21:03:16 and **21:39:47**, the latter written by
  another seat inside this replay window) differ from the fresh receipt **only**
  in those concurrent sink inventory entries. So the fresh receipt is the
  **first post-fold capture of the r77 family in a displaced env tree**, and it
  becomes the next round's reference.

## 7. Standing findings — one corrected, the rest confirmed

- **CORRECTED since r77: the exclusivity-guard gap is closed.** r77 reported
  that `--probe-capture-r77` was absent from the `sum([...]) > 1` guard at
  `measure_audio.py:5801`. At `731937c` the guard sum **ends with
  `args.probe_capture_r76, args.probe_capture_r77`** — added by the r77 fold
  `1a84ca7` (`git log -S`). Dynamic A/B on the frozen env fixture:
  control `--probe-consumers2-r75 --probe-capture-r76` → rc=2 (guard fires);
  `--probe-consumers2-r75 --probe-capture-r77` → rc=2; `--probe-capture-r77
  --probe-capture-r76` → rc=2. Both r77-reported escapes now refuse.
- `fifo-hold-ladder-r70` remains the load-dependent committed-ledger band
  (EXIT-ONLY, unchanged from r74–r77).
- `consumers-r73`'s `daemon_live.default_sink` remains environment-live, and
  `lavfsweep-r74`'s `fork_kind` CONTENT-DIFF vs its oldest sibling is unchanged.
- The four anchorless families still have no committed receipt; the sibling
  compares stand in for them.

## 8. Host, contention and live-tree events during the window (observed, not mine)

- **Contention was high and constant**: `contention-watch.txt` samples every
  30 s; load average rose 4.9 → 18.5 with 1–9 concurrent audio processes
  (`pw-cat`, `pw-record`, `ffmpeg`, `aplay`, `sox`, other seats' `python3`).
  One **stale `aplay -D null /tmp/nowriter-r75-*/nowriter.wav` process (pid
  2202613) from another seat held the whole window** (started ≈76 min before
  this seat). All 127 rows still reproduced; the only contention-shaped deltas
  are the declared hw-device/witness ones in §4.
- **HEAD moved once**: `731937c` → **`bdf748e`** at 21:40:47Z, 25 s after the
  replay ended (fold-2: provenance witness regression + record corrections).
  It does not touch this seat's Phase-1 surface (env pinned to `731937c` blobs).
- **The r78 arm is in flight in the worktree** (uncommitted):
  `corpus/fixtures/measure_audio.py` **+2,124/−3** vs `bdf748e`, wiring
  `--probe-capture-r78` at `:8123` (argparse), `:8127` (guard sum),
  `:8418` (dispatch), `:8948`/`:8968` (mode/suffix chains), plus a new
  `# A NEW parallel ledger family, --probe-capture-r78` section at `:5912`.
  Its `.pyc` is dirty too. **Phase 2 cannot run until this lands as a commit.**
- **Canonical `corpus/live/runs/`**: 5,661 receipt dirs now; committed receipt
  blobs **5,290 at both `731937c` and the moved HEAD** (diff 0 — nothing was
  committed by this seat). Exactly **one** canonical receipt has an mtime inside
  the replay window — `20261014T213947947967Z-capture-r77` at 21:39:47Z, **not
  mine** (all 127 of my receipts are inside the env tree). Zero name overlap,
  zero canonical writes.

## 9. Write-scope accounting

Wrote only: this report; `corpus/live/r78-baseline/` — `frozen/`
(head-731937c.tar + manifest + sha; gitignored by `corpus/.gitignore:5
(live/*/frozen/)`, receipt only, never extracted), `measure-env/` (663 verified
files + 127 receipt dirs, 47 MB), `out/` (254 captures), `build_env.py`,
`rerun.py`, `rerun.log`, `ledger-r78-baseline.tsv`, `compare.py`,
`prior_compare.py`, `semantic_compare.py`, `env_diff.py`,
`capture76_leg_diff.py`, `census.py`, `commit_watch.py`, `contention_watch.py`,
`build_env_post.py`, `rerun_post.py`, `post_compare.py`, and their outputs:
`env-filelist.txt`, `env-proofs.txt`, `env-comm.txt`, `fixtures-hash.txt`,
`post-replay-fixture-check.txt`, `ledger-compare-mode.tsv`,
`ledger-compare-mismatches.txt`, `receipt-compare.tsv`,
`receipt-membership.tsv`, `receipt-shas.txt`, `prior-rows-stable.txt`,
`prior-receipt-compare.tsv`, `prior76-receipt-compare.tsv`,
`semantic-compare.txt`, `env-diff.txt`, `capture76-leg-diff.txt`,
`census.txt`, `runs-canonical-after.txt`, `archive-check.txt`,
`commit-watch.txt`, `contention-watch.txt`, `toolchain.txt`, `pre-state.txt`,
`exclusivity-check.txt`. No canonical `corpus/live/runs/` writes, **no tracked-file
edits, no commits, no pushes**. Leaf seat: one read-only `labrat` probe was
dispatched by this seat (the frozen probeParent allowance, exactly one) — a
deliberately **audio-free** independent re-derivation of the §3/§4 claims, so it
could not add capture clients to the stack under measurement.

## 10. Independent corroboration (one read-only labrat probe)

The seat's frozen probeParent allowance was spent on exactly one read-only
`labrat`, tasked to **falsify** the §3/§4 claims — deliberately audio-free (no
playback/capture, no shell), so a probing descendant could not add capture
clients to the stack under measurement. Its hypothesis: *"at least one of the
row-stability, class-count, environmental-confinement and no-exit-flip claims is
false."* **Not falsified.** It re-derived each claim with its own method (read
both ledgers in full, key rows by index, re-walk `(exit, failsum)` pairs, count
the compare-TSV tags itself):

- **Row level — CONFIRMED independently**: all 126 paired exits identical;
  failure summaries identical in 125; the sole divergence is prior-02 → fresh-03
  `capture-r76`; counts sum to the 126 rows compared.
- **Class counts — CONFIRMED**: (a) 110 + 13 + 1 + 2 = 126; (b) 109 + 13 + 2 +
  1 = 125; no duplicate row ids; no `*undeclared*` file present.
- **Environmental confinement — CONFIRMED with a scope caveat, now folded into
  §4**: it found the DualSense `default_source` literally in the fresh receipt,
  and no new/renamed key, threshold change, expected-value change, or vacuity
  guard anywhere in the differing leaf set. Its caveat — that naming only the
  six verdict-flip legs understates the differing-leg set — was correct and §4
  now states the exhaustive bucket totals plus the wider leg groups.
- **No exit flip — CONFIRMED**, including the check that no *other* row flipped.
- **What it could not check, and why:** the labrat substrate exposes only
  read/grep/glob — no shell — so `git`, `tar`, and `sha256sum` were unavailable.
  The archive receipt (§1), the env proofs (§2), the committed-anchor compares
  and the census (§8) were therefore not independently re-derived; its
  "no undeclared file" finding is a visibility result over `r78-baseline/`, and
  it verified failure-summary equality by eye rather than by hash (a
  whitespace-only difference could hide — the receipt-level compare TSVs
  independently classify those rows, so the risk is bounded).
- **Its one residual inference, recorded as such:** the
  `content_witness.peak_within_3db_of_member` flip (true here, false in the r77
  reference; sox `Volume adjustment` 5.802 vs 2.000) is explained by the target
  source changing, not proven by a device log — the r77 baseline reached the
  same conclusion by measurement (43 standalone reps, 8 over the bound in
  multi-seat episodes), so the class is declared either way.

## 11. Phase 2 readiness (gated on the r78 arm landing)

The Phase-2 harness is built and idle — it needs only the arm's commit sha:

1. `python3 build_env_post.py <arm-sha>` → `measure-env-post/` (tracked-only
   subset at the arm commit, `env-post-proofs.txt` + `env-post-comm.txt`).
2. `python3 rerun_post.py` → the **same 127 rows** (MODES imported from
   `rerun.py`), `ledger-r78-baseline-post.tsv` + `out-post/`. The battery gains
   the arm's own new rows when the arm lands (the r78 author brief declares
   `--probe-capture-r78`/playback entries; those become rows 02/03 newest-first
   and the battery becomes 128/129 rows — `post_compare.py`'s `NEW_MODES` set
   must be extended to match, and prior rows stay index-comparable).
3. `python3 post_compare.py` → index-exact post vs Phase-1 with the same
   classifier; the acceptance condition is **prior cells byte-stable modulo the
   SAME named environmental set (§4) + declared contention classes, 0
   undeclared**, and the arm's own rows reported separately.

## 12. Residual gaps

- **Phase 2 is not run**: the arm is uncommitted (`+2,124/−3` in the worktree at
  the time of writing). Nothing in this report certifies the arm.
- The environmental set is *named and enumerated*, not eliminated: the r76
  capture gate's device legs cannot produce their pre-DualSense verdicts on this
  host, so row-03 will keep reporting them until either the host changes back or
  the r76 expectations are updated by an author (this seat makes no edits).
- `parecord_no_device` is invisible in the row's `failures` list (the gate skips
  `blocked` legs) — an author-visible quirk of the gate's coverage, reported
  not corrected.
- The 13 path-embedding receipts can never raw-match off the canonical path;
  the anchored-tail leaf walk is the strongest displaced-tree check (unchanged
  since r68).
- No quiescent window exists on this host (9–18 load, 1–9 audio processes);
  contention-shaped deltas are declared, not pinned to a producer.
- The archive is a **receipt** (346 MB, gitignored, never extracted); the env is
  the materialization actually replayed.
