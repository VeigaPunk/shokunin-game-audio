# r81 CRITIC — adversarial review of the landed `--probe-gst-r81` diff

Seat: critic (r81). Target: work commit `6aa03e6` (`corpus/fixtures/measure_audio.py`,
+1686/−3) and its evidence custody (`191d3f8`), as reported in
`reports/round-81/r81-author.md`. Host `plazir27`; review window
2026-10-15 17:44–17:52Z.

**Method (all executed, read-side except where noted).** `git diff` char-level
analysis of the 3 deletions; `python3 -m py_compile`; sha256 of the fixture and
every cited receipt; independent re-run of `corpus/live/r81-baseline/percase.py`
over the author's receipt pairs (including full, untruncated jitter/volatile/
semantic path enumeration and 4-way pairkind classification); JSON census of
all 8 author battery receipts and all 8 baseline receipts; receipt-level
re-derivation of all 7 claimed laws from the run-2 receipt; `pactl`/`pw-cli`
read-side host census; CLI mutex probe (`--probe-gst-r81 --probe-capture-r78`
→ rc=2, no work performed).

**Constraints honored.** No module load/unload, no `set-default-*`, no host
mutation. No fresh fixture run: the unmodified fixture stamps every resource
with `GST_R81_PID = os.getpid()` and has no env knob, so it cannot emit the
mandated `gst_r81_critic_<pid>` prefix; the review's evidence needs were met
read-side from the two pinned receipts. One custody note: my `py_compile`
rewrote the *tracked* `.pyc`; I restored it with
`git checkout -- corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`.
`git status` shows no tracked modifications (only this report is new).

---

## Findings

### F1 [INFO] — Insertion-only claim: VERIFIED, with one wording nit

The 3 deletions are exactly the three declared wiring lines, and each is a
pure addition at the character level (no byte of the old expression was
reworded):

- mutex: `, args.probe_gst_r81` appended at char offset 4013 of the
  `sum([...])` list;
- mode: `"probe-gst-r81" if args.probe_gst_r81 else ` prepended at char 10;
- suffix: `"-gst-r81" if args.probe_gst_r81 else ` prepended at char 12.

Every other one of the 1686 inserted lines is insertion. Fixture sha
`0dad37ee6500ca3d547d6b9654ad526249ae3d80215fcca3614703429b95fe56` matches the
report; `py_compile` clean; mutex fires (rc=2, `choose one probe mode`) when the
new flag is combined with `--probe-capture-r78`.

Nit: the report says the three lines are "each rewritten as a prepend-only
ternary" — the mutex line is a list-append, not a ternary. Substance holds.

Reproduction:
`git diff 6aa03e6^ 6aa03e6 -- corpus/fixtures/measure_audio.py | grep -c '^-[^-]'` → 3;
`sha256sum corpus/fixtures/measure_audio.py`;
`python3 corpus/fixtures/measure_audio.py --probe-gst-r81 --probe-capture-r78` → rc=2.

### F2 [INFO] — Arm coverage: all 7 arms are asserted; scout §0 side-facts partially covered

`failures.append` per entry: lattice 7, naming 18, routing 32, pulse 16,
target-loss 17, exit-classes 7, autodetect 9 — every arm has a machine-checked
verdict surface (the autodetect arm is not a mere recorder; it asserts
`client.api=pipewire-pulse`, default-sink consumption, `media.name`,
rc=1 + pulsesrc stderr + 0-byte artifact, and the no-node ALSA control).
Gaps vs `reports/round-81/r81-scout.md` §0: the scout's claim-4 side fact
(`pactl move-sink-input` stickiness) is not armed, and the scout's broader
lattice list (wavparse, jack\*, oss\*, playbin, …) is only partially armed
(13 elements + control + plugin). The author's §1 table already narrows claim 4
to "`device=` axis + direction split", so this is a scope statement, not a
missing assertion.

Reproduction: `sed -n '13030,14203p' corpus/fixtures/measure_audio.py | grep -c failures.append` per entry range.

### F3 [INFO] — "133-diff cluster all inside `playback_default_follow`": inaccurate containment, correct class

Independent recompute (percase.py, author runs-a vs runs-b, capture-r78):
semantic = 133 = `playback_default_follow` 127 + `playback_target_lattice` 5
+ `playback_target_loss` 1; added 7 / removed 34. The six outside
`playback_default_follow` are all `tap/windows[N]/audio` tone-window flags.
The report's "all inside `playback_default_follow_r78_probe`'s live-routing
cells" overstates containment; the class attribution (live-routing / tap
timing, same family as the baseline's own a-vs-b noise) holds.

Reproduction:
`python3 corpus/live/r81-baseline/percase.py corpus/live/r81-author/runs-a/capture-r78.receipt.json corpus/live/r81-author/runs-b/capture-r78.receipt.json`.

### F4 [INFO] — 4-way "increments dominated by the baseline's confound-hit runs": 56/44, not dominant; one confound witness undisclosed

Recomputed over baseline-{a,b} + author-{a,b} capture-r78 (424 semantic):
**ref-pair (baseline) noise 237, fresh-pair (author) noise 161, mixed 23,
CODE-DELTA 3.** The author's own pair contributes 161/424. The 3 CODE-DELTA
leaves (`playback_target_lattice_r78_probe/legs/monitor_name/tap/windows[30]/
{audio,mine}` and `windows[4]/mine`) are internally stable in *both* pairs but
differ across pairs — a stable within-session timing offset in tap-window
booleans, disclosed nowhere. No verdict moved (all four runs' failure dicts
empty), so this is an attribution-accuracy finding, not a regression.

Also on disk and not in the report's contention ledger: the author's
**runs-b** capture-r78 inventory contains foreign `r92s_in`/`r92s_out` sinks
(absent in runs-a), `confound_observed: True`, and a `coverage_blocked` naming
a pactl default-metadata mismatch — an `r92s_*` lane was live in that window.
The ledger names only the baseline (`r81_*`) and boundary (`gst_r81_bnd_*`)
lanes.

Reproduction: pairkind recompute over the four capture-r78 receipts;
`python3 -c "import json;print(json.load(open('corpus/live/r81-author/runs-b/capture-r78.receipt.json'))['measurements']['playback_target_lattice_r78_probe']['inventory'])"`.

### F5 [INFO] — Formal-run custody: receipts pin the failures; the CLI stdout does not

The two formal run dirs contain only `measurements.json`; the
`{"receipt": …, "failures": {}}` + exit-0 stdout is not pinned on disk (the
battery runs do pin stdout+EXIT). Substantively the receipts do pin it:
**24/24 entries in each run have empty `failures`** (the CLI derives the
top-level dict from exactly those). The "byte-identical frozen code" claim for
the two runs is bracketed by the battery's before/after sha snapshots
(`corpus/live/r81-author/runs-{a,b}/commands.log`, all `0dad37ee…`) and
corroborated by a stronger check the report did not claim: the 17 standard
entries *inside both gst receipts* are JSON-identical to the canonical normal
receipt, as are top-level `thresholds`/`distinctness`/`sections`.

Reproduction: `ls corpus/live/runs/20261015T171719214164Z-gst-r81/`;
JSON-compare the 17 standard entries of the gst receipt against
`corpus/live/runs/20261015T172134153125Z-normal/measurements.json`.

### F6 [INFO] — Unload ledger: every executed unload is index-verified; one teardown skip unmentioned

Both runs, all fired events and teardown records: `verified_index == captured`,
`recycled: false`, `exit_code: 0`. Exception the report's "all runs:
recycled:false, rc 0" does not mention:
`gst_target_loss_r81_probe/unloads/gst_r81_auth_<pid> =
{"verified_index": null, "captured": 536870919, "skipped": "not_listed"}`
(the t7 unload already removed the module; the teardown re-read finds nothing
and fires nothing — a safe no-op with an explicit marker, not a silent
failure).

Reproduction: dump `measurements[*]["unloads"]` and all `legs[*].fired`
from both `corpus/live/runs/*-gst-r81/measurements.json`.

### F7 [INFO] — Host cleanliness: confirmed read-side; a third, foreign run appeared

`pactl list modules short`, `pactl list short sinks`, `pw-cli ls Node` →
**0** `gst_r81` resources at review time. A third, independent `gst-r81` run
appeared on the host at 17:47:10Z (pid 2758068, 24 entries / 55 legs, empty
failures, `host_is_quiet: True`) — not part of the author's custody, but an
independent green corroboration at HEAD; the host is clean after it too.

Reproduction: `pactl list modules short | grep -c gst_r81`;
`pw-cli ls Node | grep -c gst_r81`; `ls -d corpus/live/runs/*gst-r81*`.

### F8 [INFO] — Volatile/jitter handling is honest; the report's jitter description is incomplete

The gst-r81 A-vs-B normalization erases only run-scoped differences: the 710
volatile leaves are exactly pid-stamped names/argv/env/links, `/tmp` scratch
paths, clock/pointer patterns and id fields (leaf-key histogram: `client_id`
196, `target.object` 182, `node.target` 114, `consumers` 34, `producers` 31,
`name`/`node.name` 30+30, `media.name` 26, `argv` 22, `media.filename` 22,
`own_pid` 7, …). No rc / boolean / link-state / count leaf is volatile or
jitter — all such leaves were exact — so "0 semantic over 6835" is honest.
The 556 jitter are ids, `wall_s`/`t`, module indices, contention counters,
t7 growth sizes **and** c1 tone-window amplitudes/frequencies (84 `a_*`/`f_*`
paths) — the report's "jitter is object ids, wall times, sample counts"
understates the last two classes. (Note the shared `percase.py` jitter bucket
has no tolerance: a genuine numeric `rc`/count change would classify as
jitter — here none occurred.)

Reproduction: independent flatten+classify over the two gst receipts with
`corpus/live/r81-baseline/percase.py`; compare against
`corpus/live/r81-author/stability-r81-runsAB.txt` (TOTAL 5569/710/556/0/6835,
0 collisions — reproduced exactly).

### F9 [INFO] — Claim-by-claim receipt re-derivation: no falsified claim found

Run-2 receipt verbatim reproduces every headline in §2 of the author report:
lattice rc/klass/plugin/version incl. `openalsink` 255 and control 255 and
`wavenc` `Codec/Muxer/Audio`; naming crossover n0–n4 (incl. `client.name`
null, `application.name` absent on the native node); routing r1 two-key write,
r2/r3 single-key, r4 bogus→default silent, r5 element property wins, r6 env
rename+route, r7 env node, r8 `node.autoconnect` STRING `"FALSE"` unlinked at
wallcap −9, c0 255 `target not found` + 0 B, c1 STRING `"TRUE"` + tone landed
(`carries_tone` true, finalized 819244 B), c4 default monitor, c7 prop-only;
pulse p1–p6 (p4 device beats `PULSE_SINK`; p6 rc=1 `No such entity` + 0 B);
target-loss t1–t7 (one empty-link boundary sample then re-link at +0.203 s;
t3–t6 freeze at 204 844 B with `riff_size 0x7FFF0024` / `data 0x7FFF0000`,
producers `[]`, stderr empty, alive at wallcap; t6 has **no** `node.target`
prop — the stale-prop exclusion is exact; t7 re-links and grows to 864 300 B);
exit classes e1/e3/e8/e9 rc=1 no artifact, e10 255 + 0 B, e11 rc=1 + 0 B,
p8 255, `class_summary` both true; autodetect a0/a1/a2 incl. `not-negotiated`
present in a1's full stderr. Battery: **8/8 rc=0**, stdout `failures {}`, all
per-entry failures empty in all 8 receipts, census 17/0 + 25/59 + 25/67 + 19/10
= **86 entries / 136 legs** per pass, identical to the baseline census in all
four baseline receipts; normal receipt sha `8e8cdad6…` identical author-a,
author-b, baseline-a, baseline-b and 352/500 tracked normal receipts
(`corpus/live/r81-baseline/byte-identity.txt` claims 371/519 landed). The
scout hex misquote is corrected in the fixture and the boundary's read-only
falsification is on record; the scout report text was **not** retro-edited
(still contains `0x7FFFF000` ×2).

Pre-existing, equal in both seats (not an author regression): both author and
baseline capture-r78 receipts carry the same two `coverage_blocked` entries
(`capture_unlinked_zeros`, `capture_parec_fix` — "monitor source never
enumerated"), so "green" on those two entries is named-unmeasured in both.

Reproduction: the receipt dumps above; `grep -H '^TOTAL'
corpus/live/r81-author/stability-*.txt`; census script over
`corpus/live/r81-{author,baseline}/runs-{a,b}/*.receipt.json`.

---

## Verdict recommendation

**No BLOCKER, no HIGH.** The insertion-only claim is exact (3 deletions = the
declared wiring, char-verified); the new family is seat-owned and
index-verified (no bare-index unloads, no `set-default-*`, zero leftovers);
the 7 claims reproduce verbatim from the pinned receipts; the battery census
and the normal-receipt byte-identity hold 5 ways; the 133/424-diff clusters are
run-to-run routing/timing noise (no failure dict moved anywhere), and the
volatile/jitter buckets mask nothing load-bearing. All nine findings are
documentary precision (F1–F8) plus a positive re-derivation (F9).

**Recommendation: ADMIT the work commit as landed, with the F1/F3/F4 wording
corrections noted.** Final judgment rests with the canonical Rust judge.
