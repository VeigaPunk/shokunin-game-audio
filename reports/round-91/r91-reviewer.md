# r91 REVIEWER — the gst capture-freeze mechanism lattice (landing `d78f1cc9`)

Seat: **reviewer** (read-only; not the judge, no admission). Lane
`~/Projects/shokunin/audio-shokunin`. Basis: the **committed** bytes of
`d78f1cc9` (`git show`), the author worktree receipts
`../audio-shokunin-wt-r91/corpus/live/r91-author/` and its 15 run dirs, the
verifier's landed-byte receipts (`corpus/live/r91-verifier/`,
`~/r91-verify-tree/`), and upstream source for the two mechanism citations.

**No battery run by this seat** — no host mutation, no module load/unload, no
lock, no run dir. What I did execute is listed in §1.3. Main's working tree is
being edited by a concurrent lane (`git diff --numstat` = +659/−194 vs HEAD),
so every byte claim below is taken from the commit, and the landed r91 family
block is re-checked byte-identical at its new offset in the working tree
(line 38128, sha `6fe734a8…`).

## 0. Result

| claim group | verdict |
| --- | --- |
| 5 entries / 15 legs + 1 fixture process | **re-derived** — 4/4/1/2/4 on both cited greens, `failures: []` per entry, no `blocked` key |
| gst freeze lattice (prop lattice + frozen invariants) | **re-derived** — every armed cell holds on the receipts; the header arm reads the artifact bytes |
| clock_lost mechanism | **re-derived** — `gst-launch.c:642-646` verified against upstream; the fixture's no-`set_state` control and the battery's default-verbosity stdout cell both hold |
| defects | no lattice law falsified by me; 2 claim-arming / evidence-labeling defects worth fixing (F1, F2), 3 low, 4 trivial |

Findings marked **[conv]** were reached independently here and also appear in
`r91-critic.md` / `r91-verifier.md`; they are cited as convergence, not as my
evidence.

## 1. Re-derivation

### 1.1 Byte identity (all shas recomputed here)

| item | declared | measured |
| --- | --- | --- |
| landed `corpus/fixtures/measure_audio.py` | (integrate: `7f9ee31b…`) | `7f9ee31b3b7f9269333387868a036a54beb38d633abac0a69cf839c434943cb3` |
| author WT file | `b0ab6fda…` | `b0ab6fda8b35eafa76b753ce8e31687b14ec278396fbdd00c8efc2b432124af0` (differs from the landed file — declared) |
| family block | `6fe734a8…` | landed 37712–39175 = 1464 lines = `6fe734a8ff7cd530b8790c4ada4cec6fae58216955ef3cbe7d5bc6fc0a52570d` = WT 30982–32445 (`diff` empty) |
| dispatch block | `91bb18f8…` | landed 39878–39910 = 33 lines = `91bb18f8decae5beb30232ead31c03e3be917c59200705530419dde747f2e562` = WT 33045–33077 (`diff` empty) |
| fixture `gstfreeze_r91_resume.py` | `066d6fff…` | `066d6fff7ba74ef40d11b2f3a71ae336d4ee21c6d73d0975d6dc94fe714b1dc2` both sides |
| author report | `de9e9ecd…` | `de9e9ecd5bf8914d045303df54a66533fdc10315bf8dc57877c63700d8a30bd5` both sides |
| WT diff stat | +1501/−3 | `git -C ../audio-shokunin-wt-r91 diff --numstat` = `1501 3`; WT HEAD `5a632a4f` |
| run dirs | 15 | 15 in the WT, 0 in main (as the integrate note declares) |

`r91-author/run1|run2.measurements.json` are sha-identical to
`corpus/live/runs/20261016T093036393664Z|20261016T093129552702Z-gstfrz-r91/measurements.json`
(`f68edac8…`, `d00b5f5a…`).

### 1.2 Cells re-derived from the two cited greens (and the verifier's landed run)

- **5 entries, 15 legs**: `gstfrz_prop_r91_probe` p_cap/p_cap_false/p_rec/p_sink,
  `gstfrz_clock_r91_probe` c_quiet/c_verbose/c_keepalive/c_alive,
  `gstfrz_resume_r91_probe` r_app, `gstfrz_srcloss_r91_probe`
  s_norelink/s_relink, `gstfrz_connect_r91_probe`
  x_rec_sink/x_gst_sink/x_rec_sink_remapfed/x_rec_src. Every entry
  `failures: []`; `blocked`/`coverage_blocked` absent from all five; CLI prints
  `{"failures": {}}`.
- **Prop lattice** (from the recorded node props, not only the arm):
  `p_cap` `node.dont-reconnect: true` (JSON boolean), `stream.capture.sink:
  "TRUE"`, `target.object = r91a_ns_3791811`; `p_cap_false` `"FALSE"` (literal
  string); `p_rec` absent; `p_sink` absent, pre-loss `running` 6/6, post class
  `survived_running` (arms at 38510–38586).
- **Frozen invariants**: c_quiet/c_verbose/c_keepalive all `204844 B`,
  `sizes_tail` flat ×3, `fed_by []`, `states_tail ["idle"]*3`,
  `align_ok true`; header from the artifact bytes
  `riff_size=2147418148 (0x7FFF0024)`, `data_declared=2147418112
  (0x7FFF0000)` via `_gst_r81_wav_inspect` (12753). Arms: 38168–38195.
- **c_verbose**: stdout `Setting pipeline to PAUSED … / Setting pipeline to
  PLAYING … / New clock: pipewireclock0 / … / Clock lost, selecting a new
  one`, stderr 0 B; c_quiet stdout 0 B. Arm 38693–38700.
- **keepalive**: `keepalive-time=20`, `line_counts` 0 `timeout, send keepalive
  buffer` / 0 `popped buffer` over a **live** 6958 B `pipewiresrc:5` stderr
  (the stored text is real `gstpipewiresrc.c:1027/1074/1113/1200…` debug
  output);
  `c_alive` grows `[413740, 413740, 483372]`, state `running`.
- **srcloss**: `s_norelink freeze_idle` (0 B tail, `idle`), `s_relink
  grows_running` (relink rc 0 ×2, `running`, fed by `r91a_ns2_*`); classes
  identical in both runs, sizes volatile (as declared).
- **connect**: `x_rec_sink` rc 1, 44 B, `gstfrz_no_target_node`;
  `x_gst_sink` rc 255, 0 B, `gstfrz_target_not_found`; `x_rec_src` alive at
  wallcap, 761900 B, producer seen; `x_rec_sink_remapfed` `linked_live`,
  rc −9, **573484 B in both runs**, fed by `r91a_src_*` (recorded, not claimed).
- **resume/fixture**: relink at 1.803 (2 discovered `monitor_* → input_*`
  pairs, rc 0 both), pre-link `204844`, growth to `274476/340012` (run1) and
  `274476` (run2), `fed_by_after_link = [r91a_ns2_*]`; app status
  `clock_lost: true` @ 1.233/1.211, `forced: null`, `errors: []`,
  `exit: "wall"`, `rc: 0`, `state_changes` exactly
  `null→ready→paused→playing`, `killed: null` (the battery never killed it).
  The fixture's pipeline description is the battery's canonical capture shape
  (`GSTFRZ_R91_RAW` 37757) minus the launcher; the fixture has no
  `set_state` between the initial `PLAYING` and the `NULL` in its `finally`,
  flushes its status per tick via `os.replace`, and bounds itself (wall,
  4 MiB byte cap, SIGTERM/SIGINT handler).
- **p_sink two-class envelope is admissible**: evaluating the committed arm
  expressions (`_gstfrz_r91_unload_at` / `_gstfrz_r91_last_node(after=unl_at)`
  / `_gstfrz_r91_post`) on the receipted `exited` realization
  (`20261016T092549793652Z`, rc 1, `killed: None`, no post-loss sample) gives
  class `exited` with **no** failure — the dying node is still seen in the
  `[unl_at, unl_at+0.2)` window (`state: idle`, no `dont-reconnect`), so the
  38547 `if not nd` arm does not fire. The claim holds for the one realized
  cell (residual in §4).
- **clock_lost mechanism, source side**: upstream `gst-launch.c` at
  `GST_MESSAGE_CLOCK_LOST` (lines 642–646) does exactly
  `PRINT("Clock lost, selecting a new one"); gst_element_set_state(pipeline,
  PAUSED); gst_element_set_state(pipeline, PLAYING);`. The capture-side half
  is confirmed in the scout's version-matched copy
  (`corpus/live/r91-scout/sources/gstpipewiresrc.c`, manifest-pinned sha
  `0e2248a9…`): line 1207–1208 `flags = PW_STREAM_FLAG_DONT_RECONNECT |
  PW_STREAM_FLAG_ASYNC;` (unconditional on the element), line 1094 the
  `"error during negotiation"` debug the boundary cites, line 1074 the
  `waiting for NEGOTIATED` predecessor.

### 1.3 What I executed (and nothing else)

`git show`/`diff`/`sha256sum` reads; `python3 corpus/fixtures/measure_audio.py
--help` (rc 0, `[--probe-gstfrz-r91]` listed) and
`--probe-gstfrz-r91 --probe-sox-r94` (rc 2, `choose one probe mode`) — both
exit inside `parse_args`, no run dir/lock written (re-checked: no r91 lock in
main); an `importlib` load of the committed file calling only the pure helpers
`_gstfrz_r91_unload_at`/`_gstfrz_r91_last_node`/`_gstfrz_r91_post` on receipt
data; read-only receipt re-derivation scripts; two upstream source fetches.
No battery, no mutation/negative controls (see §5).

## 2. Findings

### F1 (medium, claim-arming) — the resume "flat while no link" cell is recorded, not armed, and the receipt prints the single sample twice **[conv: critic F2]**

`gstfrz_resume_r91_entry` arms flatness only when the pre-link window holds
**≥2 samples** (`measure_audio.py:38838–38848`); the window is
`[unl_at+0.35, rel_at−0.05]` — with `LOSS_S=1.2`, `RELINK_S=1.8` that is
**0.20 s wide** against a 0.2 s sample timeline, so it holds exactly one
sample and `if len(pre) >= 2 …` never executes. The report's entry 3 claims
"Armed: flat while no link exists (204844)".

Evidence: author run1 window `[1.551, 1.753]` → 1 sample @1.603; run2
`[1.560, 1.753]` → 1 sample @1.609; the verifier's landed run2 → 1 sample
@1.609. `entry["resume_bytes"]["pre"] = pre[:3] + pre[-3:]` (38845) duplicates
a 1-element list, so the receipt reads `"pre": [204844, 204844]` — two
"measurements" that are one, which is what makes the cell look armed. The
fixture's own status file does hold the flat window (18 samples of 204844 over
2.604 s in run1, 14 over 1.956 s in run2 — recorded, never asserted).
Smallest fix: arm on the app's status samples, or
require `len(pre) >= 1` with `at_relink == pre[0]`, and print the raw list.

### F2 (medium, evidence-labeling) — two coverage-blocked runs are labelled "green", and a fully blocked family is indistinguishable from a measured green in the CLI summary **[conv: critic F3]**

`20261016T091656945259Z` (attempt-2 run2, "green (843 s)" in
`r91-author/RECEIPTS.md`) has **all five entries blocked** (`probe null sink
r91a_ns_3238720 never enumerated`, both census readers failed) and **zero
legs**; `20261016T092456396469Z` ("green (440 s)") has 3/5 entries blocked
(zero legs inside those three, the other two measured). The block path returns `failures: []` and `main()` prints
`failures: {}` / rc 0, so the two summary fields cannot distinguish "measured
green" from "nothing measured" — only `blocked`/`coverage_blocked` can, and
the committed report points readers at that receipts directory as the attempt
trail. The cited final pair is genuinely clean. Smallest fix: record a
measured-leg count per entry, make a blocked entry non-green at the harness
level, and never label a blocked run "green".

### F3 (low, claim vs bytes) — the family lock "refused" claim is a blocking wait on a tree-relative path **[conv: critic F5, verifier §1/§6]**

`_gstfrz_r91_family_lock` (38205–38222) takes `fcntl.flock(fd, LOCK_EX)` —
unbounded and **blocking** (`:38213`), no `LOCK_NB` — so a second same-family
run *waits*, it is not "refused" as the report's evidence bullet states; the
path is `ROOT/live/…`, so it excludes only runs in the same tree (the verifier
observed three concurrent same-family trees each "holding the lock"). The
landed file already carries the accepted r95 pattern
(`_jack_r95_family_lock`: host-global path, bounded non-blocking retry, named
coverage block) — the r91 family re-instantiates the shape r95 superseded.

### F4 (low, claim-arming) — the c_verbose "empty stderr" claim is measured but not armed **[conv: verifier §3 note (a)]**

`want_silent=(tag == "c_quiet")` (`:38690`) arms stderr-silence for c_quiet
only; c_verbose's 0 B stderr is true in the receipts but nothing reds if a
future c_verbose is non-silent.

### F5 (low, claim-arming) — the keepalive non-rescue arm cannot tell a dead debug channel from a silent one

The arm is `if resend or popped` over `line_counts` (`:38709–38716`); a
`GST_DEBUG` that produced no pipewiresrc output at all also yields 0/0 and
passes. The receipts make the cell real (6958 B of live `pipewiresrc:5`
output, so the 0 counts are meaningful), but the arm itself has no liveness
guard (e.g. require the debug stream to be non-empty).

### F6 (trivial, wording) — "Non-volatile cells dict-identical between the pair" overreaches the enumerated list **[conv: critic F6]**

Outside the volatile set the two greens differ in `resume_bytes.post`
(`[274476,274476,340012]` vs `[274476,274476,274476]`), `relink.at`
(2.205/2.209), `shapes.s_relink` sizes/`grew` (`720940/753708` vs
`798764/831532`), `r_app.out.bytes` (340012/331820) and every pid-bearing
`fed_by`. The report's *enumerated* cells (prop lattice, frozen cells,
keepalive, resume pre/relink rc/growth/forced, srcloss classes, connect rc,
remapfed class+bytes) are identical — the claim just needs to stay inside that
list.

### F7 (trivial, provenance) — the frozen-size list mixes values from other argv

"this seat froze at 135212 / 202796 / 204844 / 229420 / 413740 B with
identical argv": 229420 is the **boundary's** force-quantum leg (and this
seat's pw-record srcloss size), and 413740 is a dev1 mid-flight sample of a
*non-flat* leg. This seat's frozen gst legs (all runs) landed at
135212 ×10, 202796 ×1, 204844 ×25, 831532 ×1, 2572332 ×1 — the decision to
record rather than arm the size is correct and better supported by that
histogram than by the list.

### F8 (trivial) — the integrate note's WT dispatch-block range is off by one

`r91-integrate.md` cites WT lines 33045–33076; the block is 33045–**33077**
(33 lines). The declared sha `91bb18f8…` matches the 33-line range, and the
merged range 39878–39910 is correct.

### F9 (trivial) — `evidence-summary.txt`'s `coverage_blocked` map is synthesized

The receipts carry **no** `coverage_blocked` key (absence = not blocked); the
summary prints `{"gstfrz_…": null}` for all five, which reads like a receipt
cell. Not wrong in substance, but a reader cannot tell it was derived.

## 3. What held (no finding)

- Entry/leg count, per-entry failures, coverage keys, the 15 run dirs, the
  sha table, the WT diff stat, the block/dispatch byte identity and the
  splice's name closure (41 foreign helper references, all resolving to defs
  in the landed file; `py_compile` rc 0 per the integrate note; my `--help` /
  mutex re-check).
- The prop lattice, frozen header/flat/no-relink/state-drop, keepalive 0/0,
  c_alive control, srcloss classes, connect rc/bytes/classes, remapfed
  envelope and the fixture's resume — all as claimed.
- The clock_lost mechanism, both halves, against source (§1.2).
- The p_sink two-class envelope claim is admissible for the one realized
  `exited` cell (evaluated with the committed helpers on the receipt).

## 4. Residual risk

- **The landing's own green** [conv: critic F1]: the author's cited greens run
  on the WT file `b0ab6fda…`, not the landed `7f9ee31b…`; the bridge is the
  byte-identity of the family+dispatch blocks plus the verifier's and critic's
  landed-byte runs (verifier run2 green, run1 red on c_alive). This seat added
  no landed-byte green of its own.
- **Determinism**: the verifier saw 2/6 full-family reds (`c_alive` binding
  race; `s_norelink` third shape `running`+4096 B tail) and the critic saw the
  `x_rec_sink` refusal link live under co-tenancy with `s_relink` landing in a
  `suspended`+foreign-feeder shape that neither armed class covers. A
  single-run rc-0 gate will flake; the classes are host-conditional, not laws.
- **p_sink `exited` admissibility** depends on the dying node still appearing
  in the first post-unload sample window; it did (`state: idle`), but a node
  that vanishes sooner would red on "no p_sink node observed" instead of
  classifying — unproven either way.
- `x_rec_sink_remapfed`'s discriminator stays untested (verifier labrat
  refusal; recorded as the landing's open mechanism question).
- `gst-launch.c` line numbers were verified against upstream `main` today, not
  against the host's GStreamer 1.28.6 tag — the handler text and behaviour
  match, the exact line numbers may drift.
- Receipts are untracked by convention (`corpus/live/**` is not in the commit,
  and main has no r91 run dir): the cited evidence lives only in the WT and
  the verifier/critic trees, which are not part of the landing.

## 5. Verification gaps (this seat)

- No landed-byte battery run and no mutation/negative-control re-run
  (read-only review): arm liveness for the constants and the stim fixture is
  taken from the verifier/critic controls, not reproduced here.
- The `c_alive`/`s_norelink`/`x_rec_sink` intermittency was not re-attacked
  (would require host mutation and co-tenancy); I only re-derived its
  arithmetic from receipts.
- The frozen-artifact reader `_gst_r81_wav_inspect` is an r81 helper verified
  by reading, not re-executed.
- Two parse_args-level invocations and pure-helper calls are the only code I
  ran; everything else is byte and receipt arithmetic.

*reviewer leaf — re-derived, not judged.*
