# r85 scribe — evidence custody + either-way arm audit

host: `plazir27` (local = UTC−3). Lane `~/Projects/shokunin/audio-shokunin`.
Seat: SCRIBE (wave-B gate, r85). Scope: audit the committed r85 landing
`2a49d540` — `reports/round-85/r85-author.md`, the two committed receipts
`corpus/live/r85-author/runs/run{1,2}/measurements.json`, the fixture delta
`corpus/fixtures/measure_audio.py` (+2178/−3) — for claim→sha chains,
arithmetic reconciliation (87 legs / 5 entries / 2 green runs), file
existence, hash re-derivation, unreported evidence, and (the round's
assigned focus) whether the **three host-bimodal realizations
(`latebind`, `cdup_cap`, `sd_prop`) are pinned either-way rather than
silently absorbing**.

**Read-only on everything except this report and `corpus/live/r85-scribe/`;
no commits, no judgment passed** — every discrepancy below is handed to the
canonical judge as an adjudication item.

Entry state: HEAD `2a49d5401b55371a667ac86f66a3c200648f19e9` (`r85 author:
87 legs / 5 entries`, 03:16:13 −0300). Every r85 claim was re-derived from a
**commit pin** (`git archive 2a49d540` →
`~/Projects/shokunin/tmp/r85-scribe-work/tree`), not from the worktree.
Ambient at audit: loadavg ≈ 49–50 / 32 cores, and **sibling wave-B seats
were executing the r85 fixture live** from ~03:20Z (`r85a_mix_2599248`,
`r85a_2599248_mixinv_*`, then `r85a_*` pid 2598411; the family lock was
rewritten to their pid; `corpus/live/r85-{verifier,reviewer,critic,simplifier}`
dirs all written 03:18–03:21). No r85 claim below depends on live state —
all of it comes from the pin. A live residue check at 03:19, *before* the
siblings started, showed only the long-lived foreign `r84a_probe_548706`
and **zero r85a residue**.

---

## 0. Verdict

| # | question | answer |
| --- | --- | --- |
| 1 | Do the claim→sha chains hold? | **Yes.** Fixture chain re-derived byte-exact: pin `714564a3…` (24 900 lines) vs parent `8ed09d19…` (= the r84 pin, 22 725 lines), `+2178/−3` in 6 hunks, **exactly 3 deleted lines** (mutex-sum, `mode`, `suffix`) — insertion-only otherwise; worktree = pin. Both committed receipts are **byte-identical to their canonical run dirs** (`69a96ad6…`, `98267a0f…`). **But the canonical inventory holds four `*-pactlmon-r85` dirs, not two**: two earlier executions (03:02:44Z **red**, 03:10:03Z green) are uncited (**ADJ-1/2**). |
| 2 | Does the arithmetic reconcile? | **Yes for every headline cell.** 40+7+6+17+17 = **87 legs** × 2 runs; `failures` empty in all 5 entries both runs; `blocked`/`coverage_blocked` absent; `sinks_gone` all `true`, `sources_gone` all `true` (capture entry), `own_nodes_after []` in every entry; 13 unload records per run, 4 `skipped: not_listed` (already-gone modules — the reader refuses rather than firing a stale index). Every encoded law re-derives from the committed bytes (serials monotonic + index recycled, solo ref 8190.7, mix2 4 links→2 ports, aplay props-win, capture lattice, loss law, negctl table). One count nit: the mix entry's “7 legs” includes the boolean `solo_ref_ok` (**ADJ-5**). |
| 3 | Do the claimed files exist? | **Yes.** Every backticked repo path in the report resolves (`path-existence.txt`); the only miss is my own brace-splitting artifact of `runs/run{1,2}/measurements.json`, both of which exist. Toolchain strings re-verify live (pipewire 1.6.8, wireplumber 0.5.17, pactl 17.0-98-gb096, aplay 1.2.16, python 3.14.7, numpy 2.5.3). No r84-ADJ-8-class path defect. |
| 4 | Are the three bimodal arms pinned either-way? | **Two of three yes; `cdup_cap` is not.** Executing the committed verdict blocks against synthetic realizations: `latebind` and `sd_prop` accept both named host sides **and** fail on a wrong-side shape (foreign bind / non-monitor or non-default links / vacuity); `cdup_cap` accepts both named sides but its `name_shadow_bound` branch **passes any non-monitor link set with no `out_node` constraint** — a foreign `capture_*` bind is silently absorbed, contradicting its own block comment (**ADJ-3**). Independently corroborated by the frozen-probeParent labrat. |
| 5 | Custody verdict | **INTACT (pin, receipt/canonical chain, teardown witnesses) · CITATION-DEFECTIVE (uncited red + uncited green executions, ADJ-1/2) · ONE ARM-PINNING DEFECT (ADJ-3) · latent sd_prop holes (ADJ-4) · tracked `.pyc` dirt persists (ADJ-9).** No falsified measurement, no red landing *in the cited pair*, no residue, no write-scope violation. |

---

## 1. Claim→sha chain, re-derived

### 1.1 Fixture chain (commit pin)

| revision | sha256 | re-derivation |
| --- | --- | --- |
| `2a49d540` (pin) | `714564a32141f134f849401dd029e1e10c4aa19bb848a43fd50f70a251499ee2` | pinned archive file = worktree copy; 24 900 lines; matches the sha the report cites |
| `2a49d540^` (`b5a89c9b`) | `8ed09d19990480fd337cba99e45cb0588e0615fd90e34793ecc4841c21368e4e` | equals `fbe65713` (the r84 pin) — the parent fixture is the r84 fixture, an independent cross-round match |
| diff | `+2178/−3`, 6 hunks | one 2 156-line family block at `main():21576`, the 30-line dispatch at `24217`, and 4 wiring hunks; `git diff \| grep '^-'` = exactly 3 lines |

Namespace/wiring census on the pinned copy (`namespace-census.txt`):
`_pactlmon_r85` ×195, `PACTLMON_R85_` ×215, `r85a_` ×24, `probe-pactlmon-r85`
×4, each entry name ×1; `--probe-pactlmon-r85` appears in `add_argument`
(L23854), the mutex sum (L23862), the dispatch guard (L24219), `mode`
(L24870) and `suffix` (L24890) — the r82/r83/r84 convention, prior families
untouched. Commit totals: 4 files, 14 131 insertions, 3 deletions.

### 1.2 Receipts — two copies, and **four** canonical executions

| canonical dir (untracked) | wall (local) | sha256 | status | landed as |
| --- | --- | --- | --- | --- |
| `20261016T060244900131Z-pactlmon-r85` | 03:02:44 | `732be9a5…` | **RED — 10 failures across all 5 entries** | **uncited** |
| `20261016T061003728457Z-pactlmon-r85` | 03:10:03 | `9bf5e3c5…` | green (70 legs; negctl has no `legs` key) | **uncited** |
| `20261016T061227150495Z-pactlmon-r85` | 03:12:27 | `69a96ad6…` | green, 87 legs | `runs/run1` (byte-identical) |
| `20261016T061417931113Z-pactlmon-r85` | 03:14:17 | `98267a0f…` | green, 87 legs | `runs/run2` (byte-identical) |

Both cited seat copies are the canonical files **verbatim** (`sha256` equal,
no normalization); the commit (03:16:13) sits after both cited runs. The
fixture's last write is **03:10:35** (`stat`, and the tracked `.pyc`'s
embedded source mtime/size = that file), i.e. after the 03:10:03 run and
before both cited runs — so “two green runs on identical source bytes” is
consistent with the bytes on disk and the run/commit timeline (the receipts
themselves still carry no fixture sha / git HEAD — the r84-ADJ-6 class,
unchanged).

**ADJ-1 (uncited executions).** The two earlier canonical dirs are not
mentioned anywhere in the report. The 03:02 one is **red on all five
entries** (10 failure strings); the 03:10 one is green. The report's
“Green receipts (identical source bytes, two runs)” is true of the cited
pair only; the corpus retains a fourth, red execution.

**ADJ-2 (the red run is the un-disclosed evidence for the bimodality
claims).** The red run's failures are the *strong-form* arms failing on this
host, verbatim: `cdup_cap: monitor-links=4 realization=refused — the
digits-as-name shadow fails`; `latebind: … realization=refused — the
no-link stall arm fails`; `sd_prop: the module died under the prop form —
the never-touched arm fails`; `mixdup: l_a=6221.3 vs ref=8190.7 — the
coherent 2x-sum envelope fails`; `mixdelay: late l_a=205.8 …`; `mixclip:
peak=32768.0 != 32767 — the s16-tap hard-clip arm fails` (a *single-value
pin*); `env_serial: no node carried target.object=233497`; `cap_loss_1: NEW
CONTENT post-loss (peak=8192) — the no-new-content law fails`; `u_move_parse:
class pa_no_such_entity != pa_failure_noent`. The raw legs show the host
realizations the final arms record (`cdup_cap` monitor links → the serial
holder; `latebind` links → the late source's `capture_*`; `sd_prop` → the
default monitor with `sd_module_gone_after true`). The report describes the
narrowing as “author-discovered host variances … encoded as recorded
realizations with invariant arms” but does not disclose that the strong-form
arms were executed and failed in a canonical run, nor that the negctl
expectation was flipped (`pa_failure_noent` → `pa_no_such_entity`, L23651-52)
and the negctl `legs` serialization was added between the 03:10 and 03:12
runs. The final expectation is the classifier's own precedence-resolved
class for canned text (`hit: 'No such entity'`), i.e. a unit-table
correction, not a host-variance absorption — but the edit trail is invisible
in the report.

---

## 2. Arithmetic reconciliation

### 2.1 Assigned cells (both cited runs)

| entry | legs | content verified |
| --- | --- | --- |
| `pactlmon_addr_r85_probe` | 40 | 20 `g_*` (19 armed + `g_lead0` `armed False`) + 8 `s_*` + 2 `pwcli_*` + `mv_spawn` + 3 `mv_*` + 3 `cdup_*` + 3 `cyc_*` |
| `pactlmon_mix_r85_probe` | 7 | 6 measured legs + the `solo_ref_ok` boolean (**ADJ-5**) |
| `pactlmon_aplayenv_r85_probe` | 6 | `env_node`, `env_props`, `env_conflict`, `env_serial`, `env_bogus`, `env_none` |
| `pactlmon_capture_r85_probe` | 17 | baseline + 7 `t_*` + 3 loss + 4 sd + `sd_pwlink` + `latebind` |
| `pactlmon_negctl_r85_probe` | 17 | 13 unit cases + 3 live controls + `ctl_sigkill` |
| **total** | **87** | `failures: []` ×5 ×2 runs; `blocked`/`coverage_blocked` absent; `sinks_gone` all true; `sources_gone` `{vsrc, vsrcb, late: true}` (capture); `own_nodes_after []` ×5 |

The uncited runs hold 70 legs — the difference is exactly the negctl
`legs` key (0 → 17), i.e. the source changed between 03:10:03 and 03:12:27.

### 2.2 Headline laws, re-derived from the committed bytes (`laws-recheck.txt`)

- **serials**: run1 `235347→235361→235375`, run2 `236361→236375→236389`
  (strictly increasing, 3 distinct) with module index `536870916` **identical
  ×3** in both — the monotonicity arm and the index-recycle record both hold.
- **`0` = live default**: `g_zero` pct = 40 = `g_defsink` pct in both runs;
  `g_lead0` `rc1 pa_get_info_noent`, `armed False` (record-only, as claimed).
- **collision**: `cdup_move` lands on `ns_idx` (the serial holder) both runs;
  `cdup_cap` `serial_monitor_bypass` (monitor links → `r85a_ns_*`) both runs.
- **mix**: solo ref `l_a=8190.7 r_b=8190.8/8190.7`, bleed 0; `mix2` 4 edges →
  2 `playback_*` ports with all four tone medians 8190.7 and zero bleed;
  `mixdup` 2.0 (run1 `coherent_2x`) / 0.259 (run2 `partial`); `mixdelay`
  0.226/0.025; `mixinv` 1.87/1.85; `mixclip` peak 32768, rail 0.2321/0.2325,
  spur 1921.5/1921.3 — all inside the armed bounds (≤2.05, ≥32767,
  [0.08,0.60], >300) and inside the boundary's measured values (2×, 32767,
  25 %, 800–938).
- **tap protocol**: every mix leg's `tap_link` is 2 `monitor_*` → `input_*`
  edges *before* any player spawns (`_pactlmon_r85_tapped_mix`,
  L22109–22122) — the boundary §2.1 hazard protocol is implemented, and the
  `tap_ok` gate fails a leg whose tap never linked.
- **aplay env**: `env_node`/`env_props`/`env_conflict` publish
  `target.object=<ns>` and link the ns; `env_conflict` links **only** ns
  (props win); `env_serial` publishes the *int* serial (`235558`/`236572`)
  and links the ns name; `env_bogus` publishes `no_such_r85a` but links the
  live default sink (silence file); `env_none` links the default sink.
- **capture lattice**: `t_srcname`/`t_srcserial`/`t_srcid` → the remap
  source's `capture_*`; `t_sinkserial` → `r85a_ns2_*:monitor_*`;
  `t_sinkname` → `bound_source` (the live remap source's `capture_*`, never
  a monitor); `t_prop_sinkname` → own `monitor_*`; `t_prop_srcname` → the
  **default** sink's `monitor_*`.
- **loss law**: `cap_loss_{0,1}` pre-links die, no post-links, process alive,
  last two sample sizes equal, `post_frames` ≤ 16384 (2048 run2 ×2; run1
  2048/0) — the bounded in-flight flush; `cap_loss_prop` re-links to the
  default sink's `monitor_*` in both runs.
- **self-destruct**: `sd_idle` module+source alive through the 3.6 s window;
  `sd_record`/`sd_parec` module death 0.08/0.08 (run1), 0.08/0.09 (run2),
  44-byte stub, no links; `sd_pwlink` `module_alive true` + `source_alive
  true` with the link present; `sd_prop` → default-monitor links with
  `sd_module_gone_after true` (`bind_killed_then_default`).
- **negctl table**: 13 cases (9 expect-a-class, 4 expect-`null`), all
  `got == expect` in both runs; live controls `ctl_pactl_info`/`ctl_pwdump`
  rc0 classless, `ctl_pwcli_ser` rc0 `pwcli_unknown_global`, `ctl_sigkill`
  `rc=-9 SIGKILL class=None` — the kill-vs-refusal discriminator holds.

### 2.3 Run-to-run stability (`run-diff.txt`)

4 265 pid-normalized leaf paths; 1 311 values differ, and after
pid/tmp/wall/serial normalization **29 leaves remain** — every one of them
identity (serials, object ids, module indices, pids), timing jitter
(`solo/ref/r_b` 8190.8↔8190.7; `sd_parec` death 0.08↔0.09 s) or the two
documented phase realizations (`mixdup` `coherent_2x`↔`partial`, `mixdelay`
`partial`↔`cancelled`). Every *armed* verdict is identical across the two
runs — the report's claim holds.

---

## 3. The three host-bimodal arms — either-way or absorbing?

Method: the three verdict blocks were extracted **verbatim** from the pinned
fixture by anchor search and executed against synthetic leg records shaped
like each named realization (`bimodal-arm-harness.py` → `bimodal-arms.txt`);
only the live module-table reader is stubbed. A frozen-probeParent
`ufo-labrat` (one dispatch, read-only, advisory) independently hand-traced
the same committed lines (`labrat-r85-bimodal-advisory.txt`) and reached the
identical accept/fail sets.

| arm (committed lines) | accepts | fails | either-way? |
| --- | --- | --- | --- |
| `latebind` L23589–23608 | `late_bound` (all links = LATE `capture_*`), `stalled` (no links, alive), `refused` (rc1, dead) | `foreign_bind` (any link not the late source), `other` (no links, rc0, dead) | **YES — properly pinned.** Both named sides pass; foreign/monitor binds and vacuity fail. |
| `sd_prop` L23545–23575 | `clean_default_fallback` (links on the default monitor, module alive), `bind_killed_then_default` (same, module gone), **and zero-link + module gone** | non-`monitor_` links; all-`monitor_` links with none on `default_sink`; zero links with module alive | **YES with holes (ADJ-4).** Both named sides pass; non-monitor/non-default/vacuous shapes fail — but a *zero-link* leg whose module died passes with no destination evidence, and the destination check short-circuits if `inventory.default_sink` is falsy. |
| `cdup_cap` L22706–22737 | `serial_monitor_bypass` (monitor links → the serial holder), `stalled`, `refused`, **`name_shadow_bound`** | `foreign_monitor`, `other` | **NO (ADJ-3).** Both named sides pass, but `elif cl_links:` (L22724-25) accepts **any** non-monitor link set: a link on a *foreign* node's `capture_*` passes, although the block comment (L22716-18) claims “the digits never resolve a foreign target”. The `out_node == PACTLMON_R85_NS` check is applied only inside the monitor-link subset. |

Measured side, per run: all four canonical executions realize only one side
(`cdup_cap serial_monitor_bypass`, `latebind late_bound`, `sd_prop
bind_killed_then_default`); the **opposite** sides (boundary: no-links stall
for both, clean fallback for `sd_prop`) are **not realized anywhere in the
corpus** — the either-way property is verified statically against the
committed predicates, not empirically. For `latebind` and `sd_prop` that is
sufficient (the other side's branch is a named, reachable, failure-free
path); for `cdup_cap` the branch that absorbs is not the boundary's
realization (`stalled`) but an unmeasured third shape.

---

## 4. Adjudication items (no judgment passed — for the canonical judge)

| # | seat | severity | item | evidence |
| --- | --- | --- | --- | --- |
| ADJ-1 | author | custody | Two **uncited canonical executions** of the r85 family exist: `20261016T060244900131Z` (03:02:44) and `20261016T061003728457Z` (03:10:03). The report cites only the 03:12/03:14 pair. (The r83 ADJ-1 “uncited execution” class, absent in r84, recurs here.) | `receipt-chain.txt`; dir listing + shas |
| ADJ-2 | author | custody | The uncited 03:02 run is **red on all 5 entries** (10 failures) — the direct evidence that the strong-form arms were executed and failed on this host before being narrowed. Not disclosed; the report presents the narrowing as a design choice. The same run also shows the pre-narrowing `mixclip` **single-value pin** (`peak != 32767`). Source changed between 03:10:03 and 03:12:27 (negctl `legs` added; expectation flipped). | red receipt failure lists; `leg-census.txt`; fixture mtime 03:10:35 |
| ADJ-3 | author | **moderate (gate item)** | `cdup_cap` is not fully “armed both ways”: the `name_shadow_bound` branch (L22724-25) accepts any non-monitor link set with no `out_node` constraint, so a foreign `capture_*` bind passes despite the comment's “never resolve a foreign target” invariant. Reproduced by the scribe harness and independently by the labrat. | `bimodal-arms.txt`; `labrat-r85-bimodal-advisory.txt` |
| ADJ-4 | author | minor (latent) | `sd_prop` passes a zero-link + module-gone leg with no destination evidence (L23572 only guards the module-alive case), and skips its destination check entirely when `inventory.default_sink` is falsy (L23567). Not live in the cited runs (default sink present, links present). | `bimodal-arms.txt`; L23561-23575 |
| ADJ-5 | author | nit | Mix entry “7 legs” includes the boolean `solo_ref_ok` → 6 leg dicts + 1 scalar (the r84 ADJ-10 class). | `leg-census.txt` |
| ADJ-6 | author | nit | Report: “The feeder pw-play is killed **before** the tone-sink loss leg”; in the committed code the kill is **after** `cap_loss_prop` (L23263-23274). The guard exists and the shared-sink outcome holds; the ordering statement is inverted. | fixture L23263-23274 |
| ADJ-7 | author | nit | “idle survives ≥3.6 s”: the leg's window is 3.6 s and the last grid witness is at **3.57 s** (module+source true) — the window, not a measured instant, is 3.6 s. | `laws-recheck.txt` |
| ADJ-8 | author | nit | Dead code: `sers = [s for s in entry["serial_cycles"]["serials"] …]` (L22738-39) is computed and never used; the monotonicity arm reads the local `serials`. | fixture L22738-22744 |
| ADJ-9 | lane | custody | Tracked `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc` is **dirty in the worktree** (1 369 991 B, sha `e5a32d87…`, r85 bytecode, embedded source mtime/size = the committed fixture). Sha was **unchanged for the whole audit**; its mtime advanced 03:10:39 → 03:20:10 when a sibling wave-B seat imported the fixture (identical bytes). Pre-existing r84-ADJ-7 class, attribution ambiguous, worktree only; this seat wrote no tracked file (every python invocation ran with `PYTHONDONTWRITEBYTECODE=1` and never imported the fixture). | `commit-pin.txt`; pyc header parse; `host-live.txt` |
| ADJ-10 | lane | note | The family lock is **TMPDIR-scoped** (`tempfile.gettempdir()`, L22317), so “same-family exclusion” holds only within one TMPDIR — the r84 critic F1 finding, inherited unchanged. | fixture L22313-22331 |
| ADJ-11 | lane | note | Prose shapes: “`failures: {}`” (actual `failures: []`); “all `sinks_gone`/`sources_gone` true” (the latter is `{}` in the four entries that load no source); the “boundary's 3 + 1 vacuity pair” heading lists 4 falsifications + 1 pair. | both receipts; `reports/round-85/r85-boundary.md` §1–§3, §5 |
| ADJ-12 | lane | note | Ambient: sibling wave-B seats ran the r85 fixture live during this audit (03:18–03:21Z); the canonical inventory and live-residue surface are timestamped accordingly (4 dirs as of 03:21 local). | `host-live.txt` |

---

## 5. Write-scope / custody notes

- Committed in `2a49d540`: fixture (+2178/−3), the two receipts (5 878 +
  5 884 lines), the author report (191 lines) — 4 files, 14 131 insertions,
  3 deletions.
- Author evidence: 2 tracked receipt files; the two canonical run dirs are
  **untracked** (host-only) — as in r83/r84 — and here the seat copies are
  byte-identical to them, so no re-run is needed for any landed number.
- This seat wrote only `reports/round-85/r85-scribe.md` and
  `corpus/live/r85-scribe/` (12 receipts + `manifest.json`; the manifest
  lists each receipt's bytes+sha256 and this report's sha). **No tracked
  file was modified**, no
  commit, no push, no PipeWire object created, no `set-default-*`, no
  unload. All scratch lived in `~/Projects/shokunin/tmp/r85-scribe-work`;
  every python invocation ran with `PYTHONDONTWRITEBYTECODE=1`.
- Exactly one descendant was spawned: the frozen-probeParent `ufo-labrat`
  (read-only, advisory, no edits).

---

## 6. Remaining risks / blockers

1. ADJ-3 is the only verdict-bearing item: the `cdup_cap` arm passes a
   foreign non-monitor bind, so the round's “three host-bimodal realizations
   armed both ways” claim is **two-of-three** on the committed bytes. The
   measured sides are unaffected (both runs realize `serial_monitor_bypass`
   and the arm's failure branches are reachable).
2. ADJ-1/2 are preservation defects: a red canonical execution and a third
   green execution are on disk but uncited; the bimodality evidence they
   carry is not reproducible from the report alone.
3. ADJ-4 is latent (needs a falsy `default_sink` or a zero-link death to
   bite); ADJ-5…ADJ-11 are count/prose/code nits that change no verdict cell.
4. ADJ-9 remains the only tracked-file custody item and is an operator item
   (unchanged from r84); no shipping decision is made or implied here.
5. No blockers for the round. The cited landing is a clean, green, two-run,
   insertion-only landing with byte-faithful receipts, clean teardown
   witnesses, and every encoded law re-derivable from the committed bytes;
   the defects are citation-level plus the one arm-pinning hole.

*Seat stop. Read-only; no commits; no judgment — the canonical Rust runtime
remains the sole judge.*
