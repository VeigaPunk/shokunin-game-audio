# r88 scribe — wave-B gate on the committed btwit landing (c19bec96)

host: `plazir27` (local = UTC−3). Lane `~/Projects/shokunin/audio-shokunin`.
Seat: SCRIBE (wave-B gate, r88). Scope: audit the committed r88 landing
`c19bec96` — `corpus/fixtures/measure_audio.py` (+1772/−3, sha
`ad9d59b1…`), `reports/round-88/r88-author.md`, and the two cited green
receipts — for claim→sha chains, arithmetic reconciliation (3 entries /
79 legs / 2 green runs), file existence, hash re-derivation, unreported
evidence, the caveat rows, and (the round's assigned focus) **whether the
r88 family lock is at a fixed lane path rather than TMPDIR-scoped**.

**Read-only on everything except this report and `corpus/live/r88-scribe/`;
no commits, no judgment passed** — every discrepancy below is handed to the
canonical judge as an adjudication item.

Entry state: HEAD `c19bec96087713633b817b47b8509d936da4fa56` (`r88 author:
79 legs / 3 entries`, 04:25:01 −0300; parent `a7d2367b`). **During the audit
the orchestrator advanced HEAD to `c8a958e2`** — a late *r87* verifier
landing (04:25:48) touching only `corpus/live/r87-verifier/*` and
`reports/round-87/r87-verifier.md`, with **no r88 file and no fixture
change** (`git diff --name-only c19bec96 c8a958e2` contains no r88 path; the
worktree fixture sha is unchanged). Every fixture
claim was re-derived from a **commit pin** (`git archive c19bec96` →
`~/Projects/shokunin/tmp/r88-scribe-work`), not from the worktree; worktree
fixture sha == pin sha == the sibling verifier's tree copy sha
(`ad9d59b1…`, 30 504 lines). Ambient at audit: loadavg ≈ 74–83 / 32 cores,
and **sibling wave-B seats were executing r88 work live** — the r88-verifier
seat ran `--probe-btwit-r88` five times from its own extracted tree
(04:26:38 → 04:28:01, all green) and the reviewer/critic/simplifier seats
were live (ADJ-11). No r88 claim below depends on live state; the cited
receipts and the lock witness were sha-stable for the whole audit.

---

## 0. Verdict

| # | question | answer |
| --- | --- | --- |
| 1 | Do the claim→sha chains hold? | **Yes.** Pin fixture sha `ad9d59b1e0dc5e2be4274f4966e571dabefed94076c06093eed1bf4cd2aef4c4` (30 504 lines) = worktree = the verifier's tree copy; diff is **+1772/−3** (stat 1 775 changed, 6 hunks) with exactly 3 deleted lines (mutex sum, `mode`, `suffix` — each replaced in place); the commit is 2 files (fixture + report) and both cited receipt shas re-derive (`a1c7746d…`, `cce9164f…`). **Nits: an uncited RED dev receipt (ADJ-1); receipts host-only and unpinned (ADJ-2); “8 codec plugins” contradicts the receipt's 13 (ADJ-3); “85 of 92” is the run-B denominator (ADJ-4); one mis-attributed refusal path (ADJ-5); prose nits (ADJ-6, ADJ-9).** |
| 2 | Does the arithmetic reconcile? | **Yes.** 28+41+10 = **79 legs × 2 green runs**; `failures: []` on all 3 entries in both runs; the `coverage_blocked` key is **absent** on all 3 entries both runs. **144/144 re-derivation checks pass** (`laws-recheck.txt`) covering every headline law (bluetooth absent-class, the four fabrication refusals, the set rule, the `ls⊋dump` Metadata split, pactl index≡serial, the pw-top frame traps, the four-witness state agreement). Cross-run: 176/1 544 pid/number-normalized leaves differ, **zero semantic verdict-class differences** (the 9 raw hits are 8 pid-key renames of the same unload + the one acknowledged `wd_enum_fmt.outcome`). |
| 3 | Do the claimed files exist? | **Yes.** Every repo path in the report resolves (`path-existence.txt`; the “SKIP” tokens are prose pairs like `r86/r87`, no path defect). The commit contains exactly 2 files; the cited receipts and the lock are untracked/host-only (`git ls-files` = 0 for `*btwit-r88*`). |
| 4 | **Is the family lock fixed-path, not TMPDIR-scoped?** | **YES — verified statically, dynamically, by a live sibling seat, and by a negative control.** Statically: `ROOT` L26, lock path L27972 `ROOT/"live"/"measure_audio-btwit-r88.lock"`, blocking `LOCK_EX` L27977 (no `LOCK_NB`), dispatch L29817 “held to exit”; **no `tempfile.gettempdir()` anywhere in the r88 family** (the three hits L14764/L19846/L22318 are the r82/r84/r85 locks, untouched). Dynamically: two concurrent acquirers with **different TMPDIRs** resolved the identical path and serialized (B waited 1.9084 s, overlap −0.0002 s); same-TMPDIR serialized; dead holder re-acquired in 0.0001 s; the r84 TMPDIR-scoped control **raced** (overlap 1.9859 s). Live: the sibling verifier's five runs locked their own `corpus/live` inside its tree copy — the fixed **per-checkout** residual, raced (overlap 1.9869 s, E case). Caveats: the lock is fixed per checkout (cross-tree copies race — the known r86/r87 residual, now live-witnessed), and `os.open` failure silently skips exclusion (L27973-27976). |
| 5 | Are the encoded claims as reported? | **Yes.** Bluetooth **vacuous by absence**: hci0 Powered=true, Media1 advertises A2DP source+sink UUIDs, the single paired device is the DualSense (`dev_BC_C7_46_34_C5_66`, `Connected=false`, Class 1288, `input-gaming`, uuid16 `1124`+`1200`, **`audio_uuids=[]`**); zero bluez cards/sinks; the only `bluez\|a2dp\|sco` pactl line is the `session.services` advertisement; the only bluez object is `bluez_midi.server` (`api.bluez5.midi.node`, `Midi/Bridge`); `module-bluez5-discover/-device` refuse rc 1 `Failure: No such entity` (bare and with args), `send-message` refuses `pa_sendmsg_noent`, and **4/4 `create-node` fabrications are refused `res:-2`/`-22` at process rc 0 with zero residue**; 14 SPA files, `bluez5.codecs` present as a substring with 0 standalone lines; `{id ∪ serial}` set rule 4/4 got==predicted; `ls Metadata` **9** ids ⊋ dump **4** (`extra=[35,37,38,41,42]`) with `info` silent rc-0 on an ls-only id; pactl index **is** the native serial (6/6, 0 violations, own index follows); `pw-top -n 1` = one all-CREATING 12-row frame, `-n 0` = one frame, `-n 3` = `[C]→[I,S]→[I,S]` (9 S + 3 I), `-n -1`/`-n abc` infinite (killed at 4 s), `-r bogus` = the one loud refusal (rc 255); four-witness state agreement idle and RUNNING. |
| 6 | Custody verdict | **INTACT (pin, receipt chain, teardown witnesses) · GREEN ×2 (both cited receipts re-derive; 144/144 checks) · LOCK FOCUS VERIFIED · NO VERDICT-BEARING DEFECT FOUND.** Defects are disclosure/preservation/prose/arm-design level: an uncited red dev run (ADJ-1), host-only unpinned receipts (ADJ-2), a prose arithmetic slip (ADJ-3), a run-B-only denominator (ADJ-4), one mis-attributed refusal path (ADJ-5), prose nits (ADJ-6, ADJ-9), a degenerate foreign arm pair (ADJ-7), one code-inferred arm (ADJ-8), plus ambient/tracked-file items (ADJ-10…12). No falsified measurement, no residue, no write-scope violation. |

---

## 1. Claim→sha chain, re-derived

### 1.1 Fixture chain (commit pin)

| revision | sha256 | re-derivation |
| --- | --- | --- |
| `c19bec96` (pin) | `ad9d59b1e0dc5e2be4274f4966e571dabefed94076c06093eed1bf4cd2aef4c4` | pinned archive file = worktree copy = the verifier's tree copy; 30 504 lines; matches the sha the report cites |
| diff | `+1772 / −3` (stat: 1 775 changed), 6 hunks | `@@ -27506,0 +27507,1748 @@` (family block L27507–29254, inserted between the r87 midi entry and `def main()`), `@@ -27634,0 +29383 @@` (add_argument **L29383**), `@@ -27642 +29391 @@` (mutex sum **L29391**), `@@ -28054,0 +29804,20 @@` (dispatch **L29804–29823**), `@@ -28705 +30474 @@` (`mode` **L30474**), `@@ -28725 +30494 @@` (`suffix` **L30494**) |
| deleted lines | exactly 3 | the pre-r88 mutex sum, `mode`, `suffix` — each replaced in place with the `probe_btwit_r88` head; insertion-only otherwise |
| commit totals | 2 files, 1 947 insertions, 3 deletions | fixture + report; **the receipts are not in the commit** |

Namespace/wiring census on the pinned copy: `btwit_r88` ×163, `BTWIT_R88` ×65,
`r88a_` ×13, `probe-btwit-r88` ×4, `probe_btwit_r88` ×4 (add_argument L29383,
mutex sum L29391, dispatch guard L29804, mode/suffix heads L30474/L30494),
`r88arole` ×3; prior families untouched apart from the 3 splices and the
helper references the new block makes (`pwbind_r87` 222→224, `pactlmon_r85`
210→229, `alsapw_r84` 389→392; `pwctl_r86` unchanged at 173).

### 1.2 Receipts — three lane executions, two cited

| canonical dir (untracked) | wall (local) | sha256 | status | landed as |
| --- | --- | --- | --- | --- |
| `20261016T071710822152Z-btwit-r88` | 04:17:10 | `8ea27480de11cda6267188ae9be9c9c5c3910ec378aa2a3d1482c6a2e5ca2976` | **red — 14 failures** (btabs 6, witdiff 5, pwtop 3) + 1 `coverage_blocked`; 75 legs (28/39/8) | **not listed, not counted** (prose “a dev capture” / “the dev run” only) |
| `20261016T072313132218Z-btwit-r88` | 04:23:13 | `a1c7746d8a7c18ab647f868816d128cf46c90d5bc6fccb32c0085130c08e83d4` | green, 79 legs | cited (run 1) |
| `20261016T072341162452Z-btwit-r88` | 04:23:41 | `cce9164f5a537f349e449be4576623fce44cfd4d3e2f6364383f515e0d9b640d` | green, 79 legs | cited (run 2) |

Timeline: dev 04:17:10 → **fixture mtime 04:21:52** (size 1 539 408) → **pyc
rewritten 04:22:52** (header `src_mtime 04:21:52`, `src_size 1539408` — i.e.
compiled from the final bytes) → run 1 04:23:13 → **lock witness 04:23:25
(`pid=1298372` = run 2's pid)** → run 2 04:23:41 → commit 04:25:01. The dev
receipt therefore measured **pre-final bytes** (75 legs, a `pt_n2` leg the
committed family no longer has, `own_id=200`, `ls` parsing not yet fixed) and
its source is not recoverable (no snapshot). The two cited runs and the pyc
header are mutually consistent with “green twice on identical bytes”: the
fixture's last write (04:21:52) precedes both runs, and no write follows.

**ADJ-1 (disclosure).** The report never discloses that a third, RED receipt
exists on disk (14 failures across all three entries plus one
`coverage_blocked`), and lists only the two green dirs under “Files changed”.
The r87 “uncited red run” class recurs — here the dev run *is* referenced in
prose (“a dev capture emitted 1 frame”, “Newly discovered in dev”, “`remote
res:-5` in the dev run”), but never as a red receipt and never as a count.
Preservation-level, not a measurement defect (the green pair stands).

**ADJ-2 (custody).** No `btwit-r88` receipt is tracked (`git ls-files` = 0):
the landed commit contains the fixture and the report only, so the two green
receipts and the lock witness are host-only (r86/r87 class), and the receipts
embed **no fixture sha / git HEAD** (`grep ad9d59b1` = 0 hits in all three
files; the verifier's tree-copy runs likewise), so “identical bytes” is
re-derivable only from the host timeline + the pyc header. The report's
“Files changed … Nothing committed.” heading is stale in the landed artifact
(the fixture and report *are* the commit) — ADJ-9.

---

## 2. Arithmetic reconciliation

### 2.1 Assigned cells (both cited runs)

| entry | legs | content verified |
| --- | --- | --- |
| `btabs_bluez_r88_probe` | 28 | stack alive (hci0 Powered, Media1 A2DP UUIDs, BLE-MIDI bridge); the single device record HID-only with `audio_uuids=[]`; zero bluez cards/sinks; the one pactl advertisement line; 6/6 `load-module` refusals (`pa_module_noent`, bare + args); `send-message` refusal; the fabricated-card refusal **and** its first-class confound (identical text on a real card + bogus profile) **and** the positive control (real card + its own profile, rc 0, profile unchanged); 4/4 `create-node` fabrications refused `res:-2`/`-22` at rc 0 with zero residue; 14 SPA files; `bluez5.codecs` substring ×2 with 0 standalone lines (126 `bluez5.*` names); no `module-bluez5*.so`; module census unchanged |
| `witdiff_dump_r88_probe` | 41 | the `{id ∪ serial}` set rule (4 arms) + no nesting + mode invariance (`-R`, `-i 0`, `-s`); `info` strictly id-keyed (serial/dead → `unknown global` at rc 0); `ls` exposes serials and a **9-id** Metadata set ⊋ dump's 4; two prop-block layouts (flat vs starred); identical dump/info key sets on Node and Device with JSON-vs-stringified types; param names agree while dump's `[]` marks unreadable values; 5 silent rc-0 absences + dead serial; `''` = full census; two keys → first only; `--color=always` breaks JSON; `-1` the one loud refusal; `info all` 85 described with every visible Metadata omitted; `Props ≡ 2` byte-identical; `Format`/`4` never return a pod; `BogusXYZ` → unknown param type; `enum-params` on a Client → not implemented; pactl index ≡ native serial 6/6; three-witness state agreement |
| `pwtop_r88_probe` | 10 | `-n 1` all-CREATING (12/12 rows), `-n 0` one frame, `-n 3` `[C]→[I,S]→[I,S]` (9 S + 3 I) with a bounded retry, `-n -1`/`-n abc` infinite (killed at 4 s), `-r bogus` rc 255 `pwtop_connect_down`, four-witness agreement idle (`SUSPENDED`/`suspended`/`suspended`/`S`) and under a `pw-play` stream (`RUNNING`/`running`/`running`/`R`) |
| **total** | **79** | `failures: []` ×3 ×2; `coverage_blocked` **absent** ×3 ×2; teardown witnesses clean in every entry (`own_nodes_after []`, `foreign_r88a_nodes []`, `sinks_gone` all true, name-verified `sink_name=` unloads not recycled) |

### 2.2 Re-derivation (`laws-recheck.txt`)

**144/144** checks pass on the two cited receipts: every bluetooth
absent-class witness, the four refusal classes and the zero-residue arm, the
set-rule memberships, the `ls⊋dump` split, the prop/param/type relationships,
the silent-absence census, the enum-params laws, pactl≡serial, and all
pw-top/teardown/meta witnesses. One arm — `pt_n3`'s “own sink row non-`C`” —
is behaviour-verified but its raw witness is not in the receipt
(`stdout_raw` is popped), so it is code-verifiable only (ADJ-8).

### 2.3 Cross-run stability (run 1 vs run 2, pid/number-normalized)

176 of 1 544 leaves differ; **zero semantic verdict-class differences**. The
8 `exit_code` hits are the same unload recorded under a pid-keyed name
(`unloads/r88a_ns_<pid>`), and the single non-timing verdict-class drift is
`wd_enum_fmt.outcome` (`pwcli_remote_eio` → `silent`) — explicitly
acknowledged by the report as a varying refusal path on a suspended node,
with `has_pod=false` and `exit_code=0` in both runs. Everything else is
volatile by design: live ids/serials (own id 153 vs 96 in the pwtop entry,
own serial 251940/252142), the census id list (91 vs 92 objects — one Client
churned), observation offsets, `wall_s`, and log text carrying ids.

---

## 3. The assigned focus — the fixed-path family lock

Method: the committed `ROOT` expression, the `BTWIT_R88_PID/NS/NS2/ROLE`
constants and the `_btwit_r88_family_lock` body were extracted **verbatim**
from the pin (L26, L27608-27612, L27968-27984) and exec'd with `__file__`
pointed at a pinned copy; two children were spawned back-to-back (Popen) with
**different TMPDIRs** and raced for the lock. A second copy of the pin
supplied the cross-tree case, and the r84 TMPDIR-scoped lock the negative
control. Independently, the sibling r88-verifier seat's five live runs and
the frozen-probeParent `ufo-labrat` (one dispatch, read-only, advisory)
corroborate the receipt arithmetic (ADJ-11; the labrat confirmed the 79-leg
count, the empty `failures`, the 4/4 set-rule arms, the foreign-pair
degeneracy and the absence of an embedded fixture sha).

| probe | result |
| --- | --- |
| resolved path, child A (`TMPDIR=…/tmpA1`) | `…/r88-scribe-work/treeA/corpus/live/measure_audio-btwit-r88.lock` |
| resolved path, child B (`TMPDIR=…/tmpB1`) | **identical** — outside both TMPDIRs |
| acquire windows (A) | 0.0001→2.0001 s; B waited **1.9084 s** → strict serialization (overlap −0.0002 s) |
| same-TMPDIR pair (C) | serialized (one waited 1.9508 s, overlap −0.0032 s) |
| dead holder (D) | re-acquired in **0.0001 s** (flock released on process death; the file is never unlinked) |
| r84 TMPDIR-scoped control (F) | two paths inside each TMPDIR, overlap **1.9859 s** — RACED as expected |
| cross-tree copy of the same commit (E) | two paths, overlap **1.9869 s** — RACED: the lock is fixed **per checkout** (known r86/r87 residual) |
| sibling r88-verifier seat (live, 04:26–04:28) | five `--probe-btwit-r88` runs from its own extracted tree, each green, each locking `…/r88-verifier/tree/corpus/live/measure_audio-btwit-r88.lock` — the E case witnessed live |
| lane file, `O_RDONLY` + `LOCK_SH\|LOCK_NB` probe | acquired in 4.76e-06 s (no exclusive holder at probe time), content unchanged (sha `930d6404…` before and after) |

Static properties: blocking `fcntl.flock(fd, LOCK_EX)` (no `LOCK_NB`
fallback); fd stored in a `main()`-local at L29817 (“held to exit”), so
release is process-scoped; witness write `pid=… ns=… role=…` guarded by
`except OSError: pass`; the function returns `None` if `os.open` fails
(exclusion silently skipped — open-failure path, not TMPDIR-dependent); no
`unlink()` of the lock path anywhere; the three r88 entry calls (L29818/
29820/29822) all follow the lock line inside the same `if` block.

Lane witness timeline (last-writer-wins, never unlinked): at audit the file
held `pid=1298372 ns=r88a_ns_1298372 role=r88arole1298372` (52 B, sha
`930d6404…`) — **run 2's pid**, matching that receipt's unload keys, with the
mtime (04:23:25) sitting between run 1's start (04:23:13) and run 2's
(04:23:41). It is not a lock record, only a witness. The r84 F1 fold
(r84 critic F1, 3-seat consensus) is **applied for r88**; the r82/r84/r85
locks remain `$TMPDIR`-scoped and untouched.

---

## 4. Caveat rows and the encoded claims

| encoded claim | committed arm | run 1 | run 2 |
| --- | --- | --- | --- |
| bluetooth absent-class (HID-only DualSense) | `bz_device` L28181 | `audio_uuids=[]`, uuid16 `1124`/`1200`, paired/not connected | same |
| 4/4 fabrications refused | `bz_create_*` loop L28253-28262 | rc 0 + `res:-2`/`-2`/`-22`/`-22`, residue `[]` | same |
| `{id ∪ serial}` set rule | `_btwit_r88_setrule_leg` L27799 | 4/4 got==predicted, no churn re-census | same |
| `ls` ⊋ dump Metadata | `wd_ls_metadata` L28653-28661 | ls 9 ⊋ dump 4, `extra=[35,37,38,41,42]` | same |
| pactl index ≡ serial | `wd_serial_law` L28741 | 6/6 matched, 0 violations, own index follows | same |
| pw-top `-n` traps | verdicts L29159-29251 | 1/0/3 frames, infinite class, rc 255 | same |
| four-witness state agreement | `pt_state_idle/active` L29074/L29118 | idle `S`, RUNNING `R` | same |
| write-only `Format`/`4` never a pod | `wd_enum_fmt/num4` L28688/L28690 | **`remote res:-5`** / silent | silent / silent |
| `info all` silent omission | `wd_info_all` L28667-28675 | 85 described of **91** | 85 of **92** |

The degradation paths are real and correctly fail-closed: the dev run's
`wd_enum_client` leg degraded to `coverage_blocked` (never a vacuous pass) and
its `pt_n2` leg recorded a single 4-row frame (the retry helper's advisory
premise, later replaced by `-n 3` + retry). The report's caveat names the
mdump-style flake correctly; what it mis-attributes is the `res:-5` path
(ADJ-5).

---

## 5. Adjudication items (no judgment passed — for the canonical judge)

| # | seat | severity | item | evidence |
| --- | --- | --- | --- | --- |
| ADJ-1 | author | disclosure | A third receipt exists on disk and is RED (75 legs; 6+5+3 = 14 failures; 1 `coverage_blocked`); the report lists only the two green dirs and never discloses a red run, referencing dev only in prose. | `receipt-chain.txt`; dev receipt |
| ADJ-2 | author | custody | Receipts are host-only (commit = fixture + report) and embed no fixture sha / HEAD; the dev source bytes are unrecoverable (fixture mtime 04:21:52 > dev run 04:17:10). | `receipt-chain.txt`; `git show --numstat c19bec96`; `grep ad9d59b1` = 0 |
| ADJ-3 | author | nit (arithmetic) | “`libspa-bluez5.so` + 8 `libspa-codec-bluez5-*`” — the receipt lists **13** codec files (1 + 13 = 14, the same sentence's own total); “8” contradicts both. | `bz_spa_inventory`; report L70-71 |
| ADJ-4 | author | minor (report completeness) | “`info all` described 85 of 92 objects” is the run-2 denominator; run 1 measured 85 of **91** (one Client churned mid-round). Both runs agree on 85 described; the denominator is live-churn-dependent and should be marked so. | `wd_info_all` both runs; `wd_census.objects` |
| ADJ-5 | author | minor (mis-attribution) | “measured `silent`/`silent` in run 2; `remote res:-5`/`silent` in the dev run” — the cited **run 1** also measured `remote res:-5` on `Format`; that is the only non-pid verdict-class drift between the two cited runs. | `wd_enum_fmt.outcome` A/B/dev; `run-diff.txt` |
| ADJ-6 | author | nit | “`failures: {}`” — actual `[]`; “`coverage_blocked` empty in all three entries” — the key is **absent** in all three entries in both cited runs. | receipts; `laws-recheck.txt` |
| ADJ-7 | author | weakness (arm design) | The set rule's **foreign arms are degenerate**: `refs.foreign == refs.foreign_serial == "29"` (Dummy-Driver, id==serial), so “foreign id” and “foreign serial” query the identical key and cannot discriminate id-keying from serial-keying. The own pair (153 vs 251940/252142) does discriminate, and the boundary measured the id/serial ranges as disjoint on this host (V10), so the ∪ shape is only half-discriminated here. The report presents four arms as if independent. | `refs`, `wd_setrule_foreign_*`; boundary V10 |
| ADJ-8 | author | minor (report completeness) | `pt_n3`'s “own sink row non-`C`” is not re-derivable from the receipt: `_btwit_r88_top_until` pops `stdout_raw`, so only frame row-counts and the status histogram survive; the own-row arm is code-verifiable only (`failures == []` implies it passed). | `pt_n3` leg; L27862-27882 |
| ADJ-9 | author | nit | “Files changed (nothing committed)” is stale in the landed artifact — the fixture and this report *are* the commit (2 files). | report L9-20; `git show --numstat` |
| ADJ-10 | lane/host | custody (inherited) | The tracked `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc` is dirty and was **rewritten inside the r88 author window** (mtime 04:22:52, 1 670 979 B, sha `d758dabd…`; committed copy 580 245 B, sha `6e271a2d…`; header `src_mtime 04:21:52`/`src_size 1539408` = the final fixture). Unchanged by this scribe (import-free audit, `PYTHONDONTWRITEBYTECODE=1`). Operator item (r84/r85/r87 class). | `host-live.txt`; `git status` |
| ADJ-11 | lane/host | ambient | Sibling wave-B seats ran r88 live during the audit: the r88-verifier seat executed `--probe-btwit-r88` five times from its own extracted tree (04:26:38 → 04:28:01, all green, own lock file), plus reviewer/critic/simplifier activity; HEAD also advanced to `c8a958e2` (late r87 verifier landing, no r88 path). The lane's receipts and the lock witness were sha-stable throughout; the author's post-run-2 zero census is corroborated by the receipts' own teardown witnesses and by the current live census (only the pre-existing `r84a_probe_548706` and `r87t_ns` remain). | `host-live.txt`; `lock-verify.txt` |
| ADJ-12 | lane | custody (inherited) | The fixed-path lock is fixed **per checkout**: a copy of the same commit at another path locks its own `corpus/live`, so two trees can run the same family concurrently — witnessed live (ADJ-11) and reproduced in the E case (overlap 1.9869 s). TMPDIR-independence holds; global exclusion does not. | `lock-verify.txt` |

---

## 6. Write-scope / custody notes

- Committed in `c19bec96`: fixture (+1772/−3) and the author report — 2
  files, 1 947 insertions, 3 deletions. Nothing else.
- This seat wrote only `reports/round-88/r88-scribe.md` and
  `corpus/live/r88-scribe/` (8 artifacts + `manifest.json`; the manifest
  lists each artifact's bytes+sha256 and this report's sha). **No tracked
  file was modified**, no commit, no push, no PipeWire object created or
  destroyed (only read-only `pw-dump`/`pactl list`/`pgrep` queries and one
  `O_RDONLY` shared non-blocking flock on the lane lock whose content was
  sha-verified unchanged).
- All scratch lived in `~/Projects/shokunin/tmp/r88-scribe-work` (pin copy,
  two lock-test trees, lock harness, analysis scripts); every python
  invocation ran with `PYTHONDONTWRITEBYTECODE=1` and never imported the
  fixture (the lock test exec'd verbatim-extracted source lines, not the
  module). No LSP device was exposed to this seat; the work is read-only
  audit, so static reads + pinned-copy dynamic exec were used and no
  text-rename risk exists.
- The lock-test children wrote their witness only inside the two scratch
  trees; the lane lock file was never opened for write by this seat.
- Exactly one descendant was spawned: the frozen-probeParent `ufo-labrat`
  (read-only, advisory, no edits, no exec substrate used). It returned a
  measured report on the receipt arithmetic; its one deviation — a 37-leg
  count for the dev `witdiff` entry (the direct `len(legs)` is 39) — is a
  counting-method artifact of its grep heuristic, not a claim of this
  report; the authoritative count is `len(legs)` on the JSON.

---

## 7. Remaining risks / blockers

1. No verdict-bearing defect was found. Both cited green receipts re-derive
   end-to-end (144/144), the assigned focus is verified statically,
   dynamically (cross-TMPDIR serialization; dead-holder re-acquire;
   negative control raced), by a live sibling seat and by the labrat's
   independent arithmetic pass, and all encoded claims hold on the raw
   receipt evidence.
2. Residual risks are preservation-level: the receipts are host-only (ADJ-2)
   and do not pin their source bytes; a red dev run is undisclosed and its
   source bytes are lost (ADJ-1); the lock is fixed per checkout, so a
   fixture copied elsewhere locks its own `corpus/live` — TMPDIR-independence
   holds, global exclusion does not (ADJ-12).
3. The `{id ∪ serial}` foreign arm pair is non-discriminating on this host
   (ADJ-7); the boundary's V10 (disjoint id/serial ranges) is the reason, and
   it means the ∪ shape cannot be fully discriminated without a colliding
   instance.
4. ADJ-10 is the only tracked-file item and is an operator decision
   (unchanged from r84/r85/r87, but the pyc was rewritten again inside the
   r88 window); no shipping decision is made or implied here.
5. No blockers for the round.

*Seat stop. Read-only; no commits; no judgment — the canonical Rust runtime
remains the sole judge.*
