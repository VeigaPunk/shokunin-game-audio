# r92 reviewer — gate on the landed filter-chain lattice (`ccbce758`)

**Seat: REVIEWER (leaf).** Repo `/home/vgpnk/Projects/shokunin/audio-shokunin`.
Target: the r92 landing **`ccbce758`** — *"r92 author: filter-chain DSP lattice
(4 entries/80 legs, +2328/−3)"*. Frozen source =
`git show ccbce758:corpus/fixtures/measure_audio.py`, sha256
`4e5fe3e673d8cb586523f3d5462e915c3db255ce4ba0013c5f7157756096ca90`; family block
committed lines **39176–41470** (2295 lines) sha256
`a1b418be71203602eb012084a4e9b12080265cbedd0264babfd6f41b0f992291`. Receipts
re-read from `~/Projects/shokunin/audio-shokunin-wt-r92/corpus/live/r92-author/`
and the run dirs beside them.

**Seat discipline.** No tracked write except this report (untracked, **not
committed**); **no live probe battery** — sibling lanes were live for the whole
window (HEAD `b8ff4efc`, and a *third* tree `/home/vgpnk/Projects/shokunin/r92s/base`
was running `--probe-filterchain-r92` on the committed bytes while this seat
worked), the family lock is **tree-relative** (`ROOT = Path(__file__).parents[1]`,
committed line 26 + 39804–39820), and a re-measure would add nodes to the shared
daemon for claims decidable from the captured bytes. Evidence below is
**re-derivation**: committed bytes × committed receipts, plus an *independent*
numpy re-analysis of the author's own captured WAVs (own RIFF reader, own
max-energy window, own single-bin DFT, own RBJ — no fixture import; scratch at
`/tmp/r92-review-numeric.py`), plus bounded read-only host checks.

**`lsp` device.** Not present in this seat's tool surface (the only MCP server
offered is `rea`); no language server answers this repo. Caller/definition
checks are therefore **AST + symbol-census over the committed bytes**, recorded
as the literal fallback — not semantic proof.

---

## 1. Custody and wiring — every integrate claim re-derived, no finding

| item | re-derived value |
| --- | --- |
| committed fixture sha | `4e5fe3e6…` ✓ (integrate's claim) |
| worktree fixture sha | `5b17ad3d…` ✓ (author's claim) |
| family block sha, committed vs WT | `a1b418be…` **both sides** (byte-identical extraction) |
| dispatch block sha, committed vs WT | `802f23d1…` **both sides** (byte-identical, 28 lines, 42208–42235) |
| argparse row | `--probe-filterchain-r92` / `action="store_true"` byte-verbatim WT 33407–33408 = committed 41603–41604 |
| diff arithmetic | +2328/−3 = 2295 block + 28 dispatch + 2 argparse + 3 replaced wiring lines; `--numstat` 2328/3 ✓ |
| the 3 deletions | exactly the mutex sum, `mode` ternary, `suffix` ternary; the child mutex line = parent + **one** token (`args.probe_filterchain_r92`), removes **none**; `mode`/`suffix` child = r92 prefix + **parent tail verbatim** ⇒ no other probe's routing changes |
| entry symbols | each of the four entry names defined **1×**, referenced **2×** outside (dispatch + `measurements[...]` key); no symbol collision; AST name census finds **no** undefined global (only `__file__`) |
| author report | `aba104aa…` committed = WT = `git show` ✓ |
| files touched | fixture + the two reports; **no** `LOG.md`/`SCORECARD.md` — same file set as r91/r96/r97 landings |

Green receipts (byte copies = run dirs): `d167cdc5…` (run A),
`01465b5a…` (run B), `13eff464…` (pre-fix) — all match `RECEIPTS.md`. Run-level
stdout: `{"failures": {}}`, `rc=0` for A and B; pre-fix stdout carries the 19
failures.

## 2. Author claims vs receipts — re-derived

- **Entries/legs.** Receipts carry 4 entries with **81 top-level leg keys**
  (arm 26, dsp 20, ir **18** = 17 + `i_residual`, wpx 17 = 13 + 4 inventory);
  the pre-fix receipt carries 80 (dsp 19 — `d_gneg140` absent). The author's
  taxonomy (26 + 20 + [17 + `i_residual`] + [13 + 4]) = 80 "legs" + the
  `i_residual` sub-block, disclosed in §2's table. Commit/report headline says
  **80**; the receipt's own key count is **81**. (Critic F5 confirmed; the
  "80" also happens to be the *pre-fix* key count.)
- **Green claims.** All four entries: `failures: []`, `own_nodes_after: []`,
  `live_after = {spdif_links: 0, procs: []}`, `daemon.ok = True`,
  `host_is_quiet = False`, zero `coverage_blocked` occurrences in the JSON.
  ✓
- **Label table.** 64 rows, 0 violations against the committed 26/6 split
  (`FILTERCHAIN_R92_LABELS_OK/FAIL`, committed 39243–39250) — 26 load ×2,
  6 `fc92_label_missing` ×2. ✓
- **Residual law.** `i_residual` = 0.5/0.5/0.0 LSB, `n_gt_1lsb = 0`,
  `compared = 12287`, `peak_expected = 0.999939` (= 0.9999695², the file's own
  quantised kernel) ✓.
- **Delay map.** Residues 48 / 480 / 352 / 383 / 383 = 48 / 480 / (2400 mod
  1024) / (2431 mod 1024) ✓, `out_n_gt = 1` each; `i_441.peak_delta = 1134 =
  1024 + 110` ✓ (and the same value was **red** pre-fix — see T1).
- **Host-pinned inventories, re-read live by this seat:** PipeWire **1.6.8**;
  `/usr/lib/spa-0.2/filter-graph` = **6** plugins, no ffmpeg; `/usr/lib/lv2`
  = **25** bundles, **0** `.so`; both LADSPA dirs **absent**; the kemar conf
  references `hrir_kemar/hrir-kemar.wav`, which does not exist. All still hold.
- **Honest saturation / exit.** The daemon gate (`_fc92_daemon_health`,
  39823) makes a wedged daemon a *named block* **and** a failure in all four
  entries; the teardown (39881) carries the absence witnesses. The author's
  host incident is **independently corroborated by the journal**: last line
  05:58:33, silence, then systemd stop/start at 06:24:35 (local, UTC−3) —
  i.e. the ~26-minute wedge and the recovery instant are real. The author's
  exit sweep also holds *now*: pid 4058021 has **0** modules, **0** sinks,
  **0** nodes on the live host (the daemon has not restarted since 06:24:35,
  so a leak would still be listed).

## 3. Critic F1a / F1b — cross-checked, both **confirmed** (with one refinement)

### 3.1 F1a — `d_qneg` records a **clip transfer function** (confirmed)

Re-derived from the author's own captures (run2 = A, run3 = B), with my own
analyzer:

| quantity | run A | run B |
| --- | --- | --- |
| recorded `gain_db` (receipt) | 19.015 / 18.979 / 19.289 / **18.729** / 19.289 | 19.004 / 18.939 / 19.253 / 18.731 / 19.254 |
| my re-analysis of `d_qneg_0_{ref,out}.wav` | **identical** | **identical** |
| `out_stats.max_abs` / railed samples | 1.0 / 3844 at +rail, 3844 at −rail | 1.0 / 3621 at +rail, 3623 at −rail |
| model `clip(10·ref)` → s16 → analyzer | **19.015/18.979/19.289/18.729/19.289** (exact) | **exact** |
| model `clip(3·ref)` (below clip) | **+9.542 dB = 20·log10 3** everywhere | same |
| model `clip(30·ref)` | 21.965/21.709/22.193/20.411/22.193 → spread 1.78 dB | same |

So: the recorded vector *is* the clip ceiling; the arm's two clauses
(`|qn(200) − q707(200)| ≥ 3` and spread ≤ 2 dB, committed 40958–40967) are
satisfied by **any** flat response above ≈ +16 dB — a flat +30 dB passes too.
**Refinement (new):** the *receipt's own* `out_stats.rms` does discriminate the
magnitude — recorded 0.4172438 (A) / 0.4129832 (B) vs model `clip(10x)`
0.4186377 / 0.41285, while `clip(20x)`/`clip(30x)` read 0.574/0.623. My
independent RBJ check reproduces the critic's hypothesis exactly: peaking with
`q = 1e-4 → flat 20.000 dB` (spread 0.001), `q = 1e-6 → flat 20.000`
(spread 0.000), while `q = −1` gives the 0.707-style curve (spread 19.99 dB)
that matches nothing measured. So the *data* corroborates "flat ≈ A² = +20 dB";
the *arm* still cannot see it, and the report's "recorded, not explained" should
become "hypothesis + this rms witness" with the one-leg test (`Q=+1e-6`, or a
−26 dB stimulus) as the decisive follow-up.

### 3.2 F1b — the 20 kHz lowpass cell is the **s16 capture floor** (confirmed)

| model | 20 kHz | 12 kHz |
| --- | --- | --- |
| analytic RBJ, float64 | −70.217 | −47.339 |
| f32 coefficients **+ f32 state**, no capture quantisation | **−70.217** (bin diff ~1e-6 dB) | −47.339 |
| f64 filter, **no** capture quantisation | −70.217 | −47.339 |
| f64 filter + s16 `round(x·32768)` | **−71.437 = the recorded value** | **−47.37 = the recorded value** |
| f64 filter + s16 `round(x·32767)` | −70.868 | −47.348 |
| receipt, run A **and** run B | −71.437 | −47.37 |

The output's 20 kHz component is 0.404 LSB analytic vs **0.351 LSB recorded**;
float32 arithmetic moves the bin by ~1e-6 dB. The report's §4.4 sentence
("the lowpass numerator cancels catastrophically in float32") is therefore
quantitatively absent and empirically falsified; the true mechanism is the
s16 capture conversion (`_fc92_wav_write` uses ×32767, committed 39322; the
capture path behaves as ×32768, and the reader divides by 32768, 39369). The
record-never-arm decision is right, the reason is wrong and load-bearing, and
the fix is already in the file: `fmt="f32"` exists in `_fc92_audio_attempt`
(40216) and is **never used** by any leg.

## 4. Findings by severity

### R1 — MEDIUM (evidence chain / diagnostics): the family's name-verified
sink unload **never fires in any receipted run**, and the skip is
undiagnosable

- Every recorded sink unload in all three runs is
  `{"skipped": "not_listed"}` — **77/77** in run A, **77/77** in run B,
  75/75 pre-fix. **Zero** fired. `residual_destroy` is absent from all four
  entries, yet `sinks_gone` is all-True (3 / 40 / 34 sinks) and
  `own_nodes_after = []`.
- The skip reason is *ambiguous by construction*:
  `_pactlmon_r85_module_index` (inherited r85 helper) returns `None` both when
  the module is absent **and** on `TimeoutExpired`/`OSError` — with no
  diagnostic recorded. The receipt cannot distinguish "module gone" from
  "module table unreadable".
- The helper's input conditions are normally satisfiable on this host: I read
  the live table and it lists null sinks in exactly the matched form
  (`536870923  module-null-sink  sink_name=r92a_1175532_d_copy_ns channels=1`,
  tab-separated, digit index; the same helper fired 9/13 unloads in the r85
  family in the same window, 06:02–06:12 local, and the r83 family fired 14/14
  with the r81 reader). So the uniform skip is **not** explained by the
  reader's format.
- Consequence: the report's §2 sentence *"every unload is name-verified
  (`sink_name=`)"* describes how the code path is built, not an exercised
  outcome. The no-leak invariant itself is **not** in doubt — it rests on the
  absence witnesses, and I corroborated it independently for the author's pid
  (0 modules/sinks/nodes now).
- Mechanism **unresolved** by me: the most economical reading consistent with
  everything I measured (per-leg sinks appear/disappear around leg boundaries;
  the author's modules gone by unload time) is that the host's pipewire-pulse
  reclaims these client-loaded modules before the probe's unload runs — but the
  receipt has no field that can confirm it. Smallest safe corrections:
  record `error`/`elapsed_s`/`rc` on the list call in the skip branch, and add
  one arm asserting the unload path fires at least once per entry (or that the
  sink is listed immediately before the attempt). No law changes.

### R2 — LOW (documentation drift, critic F5 confirmed): 80 vs 81; `{}` vs `[]`

Commit message + report headline say 80 legs; the green receipts carry **81**
top-level leg keys (the pre-fix receipt carries 80). `failures: {}` is the
run-level stdout summary; per entry the receipt carries `[]`. Both are
definitional, both are disclosed in §2's table — but the commit message is the
durable artifact and it carries the pre-fix number.

### R3 — LOW (provenance drift): report §1 window date and §6 zone labels

§1 says the window was **2026-10-15** 05:42–06:50 UTC−3; every artifact
(receipts `20261016T*`, run-dir mtimes, worktree mtimes, commit date
`Fri Oct 16 06:58:18 2026 -0300`) says **Oct 16**. §6 labels the local
(UTC−3) journal times with `Z` ("wedged at 05:58:33Z", "recovery at
06:24:36Z") — the journal's 05:58:33 → 06:24:35 gap is real but local
(08:58:33Z → 09:24:35Z). The incident claim is substantiated; only the labels
are wrong.

### R4 — LOW (instrument hygiene): `d_gneg140`'s non-200 Hz cells are floor
ratios recorded unguarded

The leg drives a single 200 Hz tone, so its `gain_db` at 1000/4000/12000/20000
is a ratio of quantisation floors — the receipt records 13.06 / **171.008** /
158.985 / 162.803 dB. The arm reads only `200` (committed 40932–40940), so
nothing is armed wrongly today; but a future `max()`/spread-style clause over
that dict would read nonsense. Either drop the meaningless cells or record
them with an explicit `floor_ratio` tag.

### Confirmed critic findings that are code-read/predicate proofs (no change to
my assessment)

- **F3 (`d_fhi` fail-open, committed 40905–40909):** `any(abs(v) > 0.05 for v
  in gains("d_fhi").values())` → `False` on `{}`; the dsp validity gate
  (40296–40300) requires only `out_bytes`/`out_mags`, not `gain_db`, so a
  deleted/empty `gain_db` stays GREEN. One-line fix as the critic states.
- **F4b (`a_ports_none` fail-open, 40604–40612):** fail condition
  `(l.get("feed_link") or {}).get("rc") == 0` is `False` when the witness is
  absent (verified by predicate evaluation), while `a_ports_sink`'s
  `rc != 0` (40613–40625) is `True` when absent — the unfeedable class is
  exactly the one whose witness is optional.
- **F4a (silent-class split):** the five `i_*` silent legs record
  `load.load_text` but no arm reads it (41146–41161 read only
  `out_nz_exact` + the activation `error_class`); the load half is measured on
  a driverless configuration (a_load_noconfig/a_load_missing/a_load_dbg5,
  40541–40560, armed at 40705–40718) and the activation half on a driven one. The confound is real
  and disclosed; the split claim ("silent at LOAD, diagnosable at ACTIVATION")
  is armed on two configurations, not within one leg.
- **T1 (`_fc92_shift_ok`, 40157):** accepts `want + k·1024 ± 2`, `|k| ≤ 4` —
  a ±1024-sample and a 1–2-sample regression are invisible; the pre-fix
  `i_441 = 1134` is accepted by the final arm by design. The report discloses
  the modulo law; the arm is host accommodation, not a law relaxation.
- **T2/T3:** disclosed bands and host pins; all pins re-verified live today.

## 5. Residual risk

1. **Receipt ↔ bytes binding is author-asserted.** The receipt embeds no
   fixture sha (run dirs hold only `measurements.json`; the stdout summary
   holds the path + `failures` + rc). Mitigations: the A/B receipts carry the
   post-fix `d_gneg140` leg, and the critic's replay shows the pre-fix receipt
   cannot masquerade under the final arms. A later arm-code-only edit would
   still be invisible to this binding — repo-wide convention, not r92's.
2. **Tree-relative family lock.** `_fc92_family_lock` (39804–39820) is fixed
   *within a tree* (`ROOT/live/...`), so two lanes in different worktrees do
   not exclude each other — which is exactly the situation this window was in
   (author tree + a third tree running the same flag). The comment's
   "cross-TMPDIR runs must still exclude" holds; cross-tree exclusion does not.
3. **Orphan exposure on parent SIGKILL** (author-disclosed, §6): the hang-class
   children are killed only by the probe's own teardown; no `timeout -s KILL`
   argv backstop exists. Reachable only if the parent python is SIGKILLed.
4. **Host-pinned inventories** (`v_spa` = 6, LV2 0 `.so`, both LADSPA dirs
   absent, unshipped kemar IR): a package update reddens the family for a
   non-module reason. All hold today.
5. **20 kHz cell recorded-not-armed** with the f32 capture path unused (F1b):
   the correct fix is one `fmt="f32"` argument on the deep-attenuation legs,
   then arm at the existing 0.06 dB tolerance.
6. **Deep-attenuation bands** (T2): `d_gnegx` at 1.0 dB and `d_gneg140` at
   1.5 dB around −46.362 with a 5 dB exclusion; the decisive witness remains
   the 20 dB separation of the −140 leg.

## 6. Verification gaps (what this gate did **not** do)

- **No live re-measure** (deliberate; sibling lanes + a concurrent r92 lane on
  the same daemon; tree-relative lock). Every numeric claim above is
  re-derived from the author's captured bytes, not re-measured.
- **No re-run of the critic's arm-replay/mutation harness** — I relied on the
  committed code read + predicate evaluation for F3/F4b/F4a and on the critic's
  replay artifact for the receipt-to-arm compatibility claim.
- **R1's mechanism is unresolved**, and the receipt as written cannot resolve
  it (missing diagnostic field).
- The journal corroboration of the host incident is in local time; the author's
  `Z` labels are wrong (R3) but the event is real.
- Host state at review time is not the run-time state: a foreign lane's leaked
  `r90a_ns_1174991` sink was live at first sight and gone later; another lane's
  `r93a_1141414` module and a third tree's `r92a_1175532` legs were live
  throughout. Read-only checks only.

## 7. Recommendation (not an admission)

**PASS-with-findings on the encoding**: custody, wiring, the four entries, the
label/residual/delay/inventory laws and both green batteries re-derive clean,
and no law in the family is falsified by this gate. **FAIL on the two mechanism
sentences** (F1a's "mechanism is recorded, not explained" — replace with the
clip-ceiling fact plus the rms witness and the one-leg `Q=+1e-6` test; F1b's
float32 sentence — replace with the s16 capture-floor reproducer), and on any
reading of the `d_fhi`/`a_ports_none` arms as covering the claims they name.
The smallest safe corrections are the critic's five one-liners plus **R1's two
fields**: record why the unload skipped, and arm that the unload path fires at
least once. Nothing here requires rejecting the landing; nothing here changes
a law.

*Leaf seat — reviewed the diff and the receipts, did not judge, admit, edit,
integrate or ship. Not committed.*
