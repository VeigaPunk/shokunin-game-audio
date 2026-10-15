# R79 SCRIBE — audit of the r79 landing (`reports/round-79/r79-author.md` vs receipts)

Seat: **SCRIBE** (audio-shokunin round 79). Lane `~/Projects/shokunin/audio-shokunin`.
Read-only: this seat wrote **only** this report and `corpus/live/r79-scribe/`.
**No commit, no push.** HEAD audited: `a2616f732253ed90110ba16a223ec7d10224740c`
(`r78 LOG: adjudicator ADMIT-corr`) — unchanged at seat start and at seat end
(`git reflog -1` = same commit; the audit added no commit).

Scope of this audit: every load-bearing claim of `reports/round-79/r79-author.md`
against `corpus/live/runs/*capture-r79*/measurements.json` (7 receipts),
`corpus/live/r79-author/`, the committed r78 sources/receipts, and the live
filesystem (read-only). 50 claims were crosswalked; the full table is
`corpus/live/r79-scribe/claim-crosswalk.tsv`.

---

## 0. Seat-start state (audited, not assumed)

| item | observed at seat start | evidence |
| --- | --- | --- |
| HEAD | `a2616f732253ed90110ba16a223ec7d10224740c`, reflog top 2026-10-15 03:00:23 -0300 | `git rev-parse HEAD`, `git reflog -1` |
| tracked dirt | exactly two files: ` M SHONEN.md`, ` M corpus/fixtures/measure_audio.py` | first `git status --short` of this seat |
| `measure_audio.py` | `sha256 4ee754b3fa7dab6c…`, 672390 B, `+2737/−3` vs HEAD | `sha256sum`, `wc -c`, `git diff --numstat` |
| `SHONEN.md` | mtime `2026-10-15T04:50:20Z`, `+10/−7`, uncommitted | `stat`, `git diff HEAD -- SHONEN.md` |
| r79 seat dirs at start | `r79-author` (04:28:51 local), `r79-baseline` (03:06), `r79-scout` (Oct 14 18:51) | `ls -d corpus/live/r79-*` |
| reports/round-79 | `r79-author.md`, `r79-baseline.md`, `r79-scout.md` only | `ls -la reports/round-79/` |

**Seat-window drift (not the author's):** during this audit four more r79 seat
dirs appeared — `r79-verify` (04:59:45 local), `r79-simplifier` (05:01:14),
`r79-boundary` (05:02:31), `r79-critic` (05:02:54) — and at 05:01:54 local the
tracked `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc` was
re-dirtied by one of them. Their outputs are **outside** this audit's scope; no
claim below rests on them.

---

## 1. Verified-sound inventory (what checked out)

Receipt integrity and run attribution:

* **C02/C03** — both formal receipts exist, are byte-equal to their canonical
  copies (`cmp` clean), and their sha256s match `receipt-shas.txt`
  (`658773646ec8381b…` B, `f4572530cbf0c708…` C).
* **C01** — 8 `*_r79_probe` entries, **66 legs** (6+12+10+4+6+3+13+12),
  `failures: {}` and `EXIT=0` in both stdout summaries, 0-byte stderr, no
  `blocked`/`coverage_blocked` key, `own_nodes_after: []` in all eight entries,
  `sinks_gone` all true.
* **C04** — `receipt-BC-diff.txt` is exactly 68 SAME / 2 DIFF as printed.
* **C05** — the "inherited arm blocked vacuously" provenance claim is receipted:
  run 1 (`20261015T063951291469Z`) blocks **all eight** entries with
  `a probe null sink/monitor did not enumerate` (fc: `the fc …`), zero legs.
* **C06–C11** — the inherited-defect table is receipted by run 2
  (`20261015T064636573588Z`): d2a+d2b `no_target_node`, d2c → SPDIF sink,
  D17 pins exit 255 `No such file or directory`; b02/b03/b05/b06/b07 `got []`;
  matrix `expected the 0.5*(L+R) mix signature` **and** `carried no tag-tone
  windows`; `expected producers [@SRC@]`; `the reported Latency param VARIED
  across legs`; fc f1/f3/f3b `alive=True nodes=[]`.
* **C20** — §3.1's run-3 story is in the receipt: `oracle_at_start.source_meta =
  r86ctl_src`, `b02`/`b03` `input_producers_union = ['r86ctl_src']`, `b05`
  producers `[]` (recorded as a failure in that run, before the class existed).

Leg-level claims (spot-checked one by one against the primary receipt):

* **C21/C22** — playback lattice c01–c10 incl. the c07 control tap
  (`tap_flag_sink`: `ran=true`, `bound_to_target=true`, `mine_windows=0`,
  peaks 0/0) against a 40-mine main tap.
* **C23** — matrix signature 2269.3 both channels, `mix_half_gain_ratio = 0.5`
  on cm1/cm3/cm4, stereo passthrough on cm2, in **both** formal runs.
* **C25/C26** — record arms: `mine_windows` 14/14/14 (d2b/d2c/D17) and 0 (d2d);
  D17's two `pw-link` pins exit 0; loopback `wall_s = 16.73`.
* **C27** — hotplug: e1 tap 16 mine (hp → SPDIF), e2 tap 37 mine (SPDIF → hp2),
  e3 capture ns_a → SPDIF monitor; every leg `killed_at_bound`, stderr null.
* **C28/C29/C30** — the 13-value latency vector, `latency_param_tracks_request`
  with a 3-entry `latency_param_set`, and d12 `feed_content=silence` /
  `content_witness=declined_shared_default` with
  `contamination.shared_default_tone=false`.
* **C31/C32/C33** — filter-chain: f1 DSP witness (`ch0 {at_l 4095.6, at_r
  4095.7, peak 8192}`, `ch1 {0.0, 0.0, 0}`, i.e. FL carries the 0.5·(L+R) mix
  and FR is digital silence); f2/f3/f3b parse-soft with the `Mismatched
  bracket` warning and live loader; f4 silent; f5 `loader_rc=254`; f7 reply
  `1 = @module:22`; f8 unload refused with nodes still up; f9/f10 refused with
  the daemon alive; f11 `nodes_after_quit=[]`.
* **C37/C38/C40/C41/C43** — contamination ledger: the fail-closed tone guard,
  the run-A foreign event on b09 (`fed=false`, `peak_l=11997`, `peak_r=8997`,
  `mine_windows=11`, one failure), `host_is_quiet=false`, `aplay=1` in every
  contention dict, and host-window snapshots whose sibling scan matched only
  the driver's own shell.
* **C44** — diagnostics' metadata footprint: `pre_metadata.raw = null`,
  `restored_metadata.raw = null`, `mid_metadata.raw = null` after the write.

Write scope:

* **C48** — exactly one tracked edit by the author, hash/bytes/diffstat all
  match; the three removed lines are the prepend-only wiring lines
  (exclusivity sum, `mode` ternary, `suffix` ternary) and nothing else.
* **C50** — `SHONEN.md` is foreign dirt: mtime 04:50:20Z, i.e. **before** the
  r79 baseline's first command (06:01Z) and the author's (06:38Z); it is still
  uncommitted and appears in the author's diff only as a pre-existing entry.
  The author's and baseline's statements about it are both accurate.

---

## 2. Findings

Severity: **HIGH** = would change a verdict or a law; **MEDIUM** = a claim is
not backed as stated; **LOW** = provenance/precision; **INFO** = record only.

### F1 — MEDIUM — `foreign_tone_on_shared_monitor` is a code-only class; no receipt contains it

The report (§12) says the arm "now decides *who fed it* from the ceiling
(`foreign_tone_on_shared_monitor`, peaks recorded)", and `RECEIPTS.md` says the
run-A event is "Recorded as `foreign_tone_on_shared_monitor` with the peaks".

What the receipts show: **zero** of the seven r79 receipts contain the string
`foreign_tone_on_shared_monitor` or `foreign_tone_witness`. In the only run
where the event occurred (`20261015T071612380726Z`, run A) the b09 leg carries
`fed=false`, `tap.peak_l=11997`, `tap.peak_r=8997`, `mine_windows=11`,
**`confound` is absent**, and the entry records the *generic* failure

```
capture b09_prop_garbage_sinkprop: tag tone on r79lb_ns_b_3889192 —
this leg was never fed our tone; a `mine` window is contamination,
not coverage
```

The ceiling branch (`measure_audio.py:9400-9419`; `PLAYBACK_R78_TONE_AMP=8192`,
so the threshold is 8601.6) takes the *other* branch for `peak=11997` with
`fed=false`, so under the frozen code that event would have been recorded as
the named class. The run-A receipt is earlier (07:16:12Z) than the frozen
artifact (07:16:51Z) and the event did not recur in runs B/C, so no artifact
distinguishes "run A executed pre-ceiling code" from "its inputs differed" —
either way, **the class is unexecuted in every artifact this round produced**.

Consequence: the contamination ledger's *named* verdict for the round's one
foreign event is a source claim standing beside measured evidence; the peaks
themselves are receipted in the tap object, so the event is real and
attributable by inspection — but the receipt does not record it as the class
the report names. Per the artifact-trust rule, the class must not be carried
forward as execution evidence until a run exercises it.

### F2 — MEDIUM — labrat H1's PipeWire sub-claim is falsified by a read-only filesystem check

Report §13: "`stream.capture.sink` appears **only** in WirePlumber's shipped
material … and in **no** PipeWire config or man page. Man pages were not decoded
(gzip), so 'absent from man pages' is bounded."

Verified true: the two WirePlumber citations
(`/usr/share/doc/wireplumber/NEWS.rst:1553`,
`/usr/share/wireplumber/scripts/lib/common-utils.lua:42`) and the absence from
`/usr/share/pipewire/` + `/usr/share/doc/pipewire/`.

Verified false: the string **is** in a shipped PipeWire man page —
`/usr/share/man/man7/libpipewire-module-protocol-simple.7.gz`
(owned by `pipewire-audio 1:1.6.8-1`, the round's own PipeWire version):
line 72 lists `\fBstream.capture.sink\fP` among the supported stream
properties, and line ~117 ships the commented example
`#stream\&.capture\.sink = false` under the comment "To make the capture stream
capture the monitor ports". Evidence: `corpus/live/r79-scribe/labrat-h1-man-page.txt`.

Also: the "(11 fragments)" count in §13 does not match the shipped directory —
12 `.conf` files, all 12 carrying at least one of the cited props, 11 carrying
`node.passive` (eq6 included, `sink-eq6.conf:66`). Since the labrat left no
artifact, its counting method is unrecoverable; the load-bearing half of H1
(the props are documented by example; `node.passive` is a real shipped idiom)
stands.

Impact: **none on any measured claim** — the author states §13's output is
advisory and that no claim depends on it. It is reported because the H1 summary
as printed is wrong and would mislead a future round's "is this documented?"
question. The labrat left no receipt anywhere under `corpus/live/`; this scribe
check is the first execution evidence for the claim.

### F3 — MEDIUM/LOW — "there is no default source at all" conflicts with the arm's own recorded oracle

The load-bearing class `capture_default_source_unnegotiated` is well gated and
receipted (per-leg correlate `source_meta_at_leg=null` +
`default_source_probe_available=false` + `default_source_probe_class=
no_target_node`, on the observed zero-port/zero-link shape; run 3 shows the
strict path when a live foreign default exists). The **prose compression** is
what conflicts:

* §2: "on this host state there is **no default source at all**"; §3.1: "the
  session manager has no source to hand out".
* The receipts simultaneously record a default source: every leg carries
  `default_source_at_leg = alsa_input.usb-Generic_USB_Audio-00.HiFi__Line__source`,
  `oracle_at_start.source_pactl` is the same name, every
  `outcome_correlate` includes `pactl_default_source: …Line__source`, and
  `host-window.log` prints `Default Source: …Line__source` at all four
  snapshots.
* The author's own probe docstring (`measure_audio.py:9518-9521`) states the
  precise form: "`pactl info`'s `Default Source:` line is NOT evidence: on
  2026-10-15 this host reports `…Line__source` while WirePlumber resolves
  nothing".

The precise measured statement is: *no `default.audio.source` metadata key
(`source_meta=null`), no `wpctl` default marker, and no default source the
session manager will hand a capture stream (`no target node available`) —
while `pactl` still names one.* The class, the law and the run-3 evidence are
unaffected; only the report's phrasing invites an apparent contradiction with
its own receipt fields.

### F4 — LOW — the r78 coverage_blocked state was durable, but not disclosed by r78's own landing

Named-item answer: **yes, durable before r79**, and the author's §11 timeline is
accurate.

| r78 receipt (UTC) | `capture_unlinked_zeros_r78` | `capture_parec_fix_r78` |
| --- | --- | --- |
| 05:28:39 | blocked `pactl could not load the capture sink` | no `monitor_source` key, 10 failures |
| **05:37:41** | `enumerated: True` | `enumerated: True` |
| **05:50:13** | `False` + blocked + `coverage_blocked` | `False` + blocked + `coverage_blocked` |
| **05:57:01** | same | same |
| **06:05:13** (r79 baseline anchor) | same | same |

Full scan: `corpus/live/r79-scribe/r78-blocked-durability.txt`. Mechanism
confirmed against committed code: the r78 helper requires both
`"<sink>.monitor"` in `pactl list sources short` **and** `pw-link -o` ports of a
*node* named `<sink>.monitor`; the r79 gate shows `pactl_listed: true` with the
monitor ports taken from the SINK node, and no `.monitor` node exists.

Two record notes the author did not state:

1. The helper first appears in commit `a005e1e` (06:00:10Z). Two of the three
   cited receipts (05:50:13Z, 05:57:01Z) therefore predate the commit; only
   06:05:13Z postdates it. "committed-fold receipts from 05:50:13Z onward"
   is loose — the receipts *show the fold's behaviour*, they were not all run
   from the committed tree.
2. The state was **not** disclosed anywhere in the r78 report set or LOG
   (`grep -rn "never enumerated\|coverage_blocked\|wait_source" reports/round-78/`
   → no hits), while `reports/round-78/r78-adjudicator.md` and the LOG both
   record probe #8 — receipt `20261015T055701745739Z`, i.e. one of the blocked
   receipts — as "zero failures". The r79 baseline then re-propagated that
   reading ("6/8 r78 arms clean", listing the two blocked arms). The author's
   §11 disclosure is the first place this is surfaced, and it is accurate.

### F5 — LOW — §5's matrix table is drawn from run 4 (07:10:14Z), not from the formal runs

§5 quotes `cm1 peak 8191` and `cm2 ch0 4538.6/2.8, ch1 4.0/4538.6`. Those
figures match **only** `20261015T071014963276Z` (run 4) exactly; run B measured
`8192` and `2.7/4.1`, run C measured `8191` and `2.9/3.9`. The load-bearing
values — 2269.3 both channels and `mix_half_gain_ratio 0.500` — replicate in
both formal runs, so the table's *signature* is sound; only the last-digit
leakage/peak columns and their run attribution are unstated. Related: §1's
"68/70 identical" is exact, but the second diff is described in §14 as "a 0.1
amplitude rounding on the filter-chain DSP witness" while the DIFF line also
carries a peak difference (B `peak 8192` vs C `peak 8191`).

### F6 — LOW — two rows of the inherited-defect table are not receipted

Rows 1, 3, 4, 5, 6, 7, 8 are receipted (§1, C05–C11). Two are not:

* **Row 2** (the pw-cat fallback leg played the tag tone into the shared
  default sink): run 1 was all-blocked, and run 2's d12 already shows the
  repaired `feed_content=silence` / `content_witness=declined_shared_default`.
  No receipt shows the inherited behaviour, so the row is a self-report.
* **Row 9** (cosmetic always-true operand): the inherited r79 arm exists in no
  committed blob, so the claim cannot be checked against anything; the evidence
  column is correctly "—".

Neither affects a measured law; the table's header ("inherited defect
(measured)") should not be read as receipted for those two rows.

### F7 — LOW — §3.1's "for legs b01–b04" is one leg too wide

Run 3's per-leg oracle shows `source_meta = r86ctl_src` at b01/b02/b03 and
`null` at b04; b04's producer is the Line source, i.e. the `@SRC@`
substitution (`sources.non_default`), not the fallback. The law ("the fallback
follows the *live* default, foreign or not") is unaffected — b02/b03 carry it —
but the span and the same wording in the code comment at `measure_audio.py:9301`
should read b01–b03.

### F8 — LOW — one contamination item is not receipted

§12 names "the game-dev lane's battery load". No r79-author artifact records
it: the host snapshots carry only load averages and a sibling-process scan that
matched nothing but the driver's own shell, and `contention.fixture_runs` is 0
in every receipt (that counter only sees sibling `measure_audio.py`
processes). The two other contention items in the same sentence **are**
receipted (`r86ctl_*` in run 3; the stale `aplay`, `aplay:1` in every
contention dict, named with pid 2202613 by the r78/r79 baselines).

### F9 — INFO — the `py_compile` restoration claim was true in its window and is no longer tree state

The author restored the tracked `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`
to HEAD (§15). At this seat's start the pyc was indeed absent from
`git status --untracked=no`; at 05:01:54 local a post-author seat re-dirtied it
(mtime later than the author's last artifact at 04:28:51). The claim is not
falsified — it is scoped to the author's window — but the tree no longer
matches it, so the round's tracked diff is now three files.

### F10 — INFO — `SHONEN.md` is compliant

Foreign dirt, uncommitted, mtime 04:50:20Z (pre-dates every r79 seat's first
command), `+10/−7`, still ` M` at seat end, and not part of the author's edit
set. The requirement "must stay uncommitted" holds at audit time.

### F11 — INFO — no finding on the formal-run freeze

The frozen hash is re-verified in `host-window.log` before and after each run
(four snapshots, identical `4ee754b3…`), the artifact is unchanged at audit
time, and both receipts are byte-equal to their copies. The two-run
requirement is satisfied by evidence, not by assertion.

---

## 3. Named-item adjudication (as dispatched)

| named item | adjudication |
| --- | --- |
| every claim receipted? | **Mostly.** 50 claims crosswalked: 43 receipted (5 of them with a note: F4/F5/F7/F9 and the guard's code path), 2 code-only/unexecuted (F1, defect row 9), 3 unreceipted (defect row 2, F8, and the labrat's advisory output by design), 1 falsified (F2), 1 unverifiable-as-printed (F2 fragment count). |
| run attribution? | **Correct where given**: §3.1 → run 3 = `070406112526Z`; §12 → run A = `071612380726Z`; formal runs B/C = `072219089606Z` / `072746218296Z`. **Unstated** for §5's table (run 4 = `071014963276Z`) — F5. |
| the two formal runs B/C sha'd? | **Yes.** sha256 recorded in `receipt-shas.txt`, matching both the canonical `runs/` files and the copied receipts, which are byte-equal (`cmp`). Freeze re-verified per snapshot. |
| r78 `_playback_r78_wait_source` can never confirm a null-sink monitor; two r78 arms coverage_blocked — durable before r79? | **Mechanism confirmed from committed code; durability confirmed from 05:50:13Z** (3 consecutive receipts incl. the LOG-designated r78 #8 receipt and the r79 baseline anchor), with the author's 05:37:41Z caveat reproduced exactly. Not disclosed by r78's own reports; re-propagated as "clean" by the r79 baseline. Timeline phrasing and the pre-commit receipts: F4. |
| labrat H1 PARTIAL (advisory, no receipt) | **No receipt exists** anywhere under `corpus/live/` for the labrat. Advisory status is honoured and no measured claim depends on it, but one sub-claim is falsified on the live filesystem (F2) and the fragment count does not match the shipped directory. |
| host-state-conditional capture-fallback legs | **Condition and gate verified in code and receipts** (per-leg correlate + run-level probe; strict path preserved; run 3 shows the fallback linking to a foreign live default). Prose compression "no default source at all" conflicts with the arm's own `pactl` oracle fields — F3. |
| foreign `SHONEN.md` dirt must stay uncommitted | **Holds** (F10). |
| audit seat-start state | §0; HEAD unmoved, author's edit set exactly one file, four sibling seats and one pyc re-dirty landed inside the audit window and are excluded from judgment. |

---

## 4. Out of scope / not claimed by this seat

* No re-execution of the r79 arm: this audit read receipts, the committed
  sources, and the live filesystem (read-only) only. Nothing here is new
  execution evidence for the r79 laws, and no receipt was regenerated.
* The concurrent seats' artifacts (`r79-verify`, `r79-simplifier`,
  `r79-boundary`, `r79-critic`, and the pyc re-dirty) were not audited, not
  judged, and are not credited or blamed.
* F2's filesystem check speaks only to the live host's shipped material at
  audit time (`pipewire-audio 1:1.6.8-1`); it does not reconstruct what the
  labrat saw, and it changes no measured r79 claim.
* No verdict on the round is offered. F1–F11 are the scribe's report for the
  canonical judge; the acceptance decision is not this seat's.

## 5. Artifact paths (this seat)

* Report: `reports/round-79/r79-scribe.md` (this file)
* Scratch: `corpus/live/r79-scribe/`
  * `claim-crosswalk.tsv` — 50 claims × (report §, evidence, verdict)
  * `seat-start.txt` — HEAD, tracked diff, mtimes, r79 seat-dir inventory
  * `r78-blocked-durability.txt` — 13-receipt r78 scan of the two arms
  * `cross-run-scan.txt` — 7-receipt scan: matrix values, latency vector, b09 peaks
  * `labrat-h1-man-page.txt` — the falsifying man-page evidence and fragment census
* Evidence read (unmodified): `corpus/live/runs/20261015T{063951291469Z,
  064636573588Z,070406112526Z,071014963276Z,071612380726Z,072219089606Z,
  072746218296Z}-capture-r79/measurements.json`, `corpus/live/r79-author/*`,
  `corpus/live/runs/*capture-r78*/measurements.json`,
  `reports/round-79/{r79-author,r79-baseline,r79-scout}.md`,
  `reports/round-78/r78-adjudicator.md`, `LOG.md`, `corpus/fixtures/measure_audio.py`
  (worktree and `git show HEAD:`).

No commit, no push, no product-code edit, no re-run of the probe.
