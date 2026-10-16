# r90 reviewer — independent re-derivation of the author claims

Seat: reviewer (UFO-FSD). Scope: landing `f50cf66a` in
`/home/vgpnk/Projects/shokunin/audio-shokunin`, re-derived against
**committed bytes** (`git show f50cf66a:corpus/fixtures/measure_audio.py`,
sha256 `d3119c5d88228349b54996e23978cf726d59bfc615739838177a5a5e14551154`)
plus the **worktree receipts** at
`/home/vgpnk/Projects/shokunin/audio-shokunin-wt-r90/corpus/live/r90-author/`
and `.../corpus/live/runs/`. Nothing committed; no live audio leg was run.

## Method and provenance notes

- **`lsp` device: unavailable.** This seat's tool surface exposes no
  language-server session (the only MCP server is `rea`, a binary-analysis
  surface). Recorded per seat card; caller/definition checks were done on the
  committed blob via `ast` name resolution and by executing the two
  `parse_args` paths. `grep` was used only as the literal fallback and is never
  presented here as semantic proof.
- **The main worktree moved under this review.** At 09:57Z
  `corpus/fixtures/measure_audio.py` was dirty (` M`), 40591 lines, mutex
  tokens 137 — a later round is splicing into main concurrently. All byte
  checks below bind to the commit blob, not the live worktree.
- Local timezone is −0300; timestamps are UTC in this report.

## Headline claims

### 1. Four entries, 60 legs — VERIFIED

- Committed blob defines exactly four r90 entries and registers exactly four
  measurement keys once each: `wpstate_store_r90_probe` (def 36253),
  `wpstate_pmod_r90_probe` (36871), `wplink_r90_entry` (37158),
  `wpformat_r90_entry` (37489); dispatch block 38365–38384 assigns
  `measurements["wpstate_store_r90_probe" | "wpstate_pmod_r90_probe" |
  "wplink_r90_probe" | "wpformat_r90_probe"]`, 1× each.
- Both green runs: **15 / 15 / 24 / 6 = 60 legs**, `failures: []` for all four
  entries, `coverage_blocked` absent in all four. Leg-name sets are identical
  to the code's leg names for store/wplink/wpformat; pmod's 15 = 6 static + 4
  `m_stub_*` + 3 by-name variants generated from tuple loops
  (`("m_stub_stream_restore", …)` etc.), all present in both receipts.
- The two entry-name spellings in the report headings
  (`wplink_r90_entry`, `wpformat_r90_entry`) are the *function* names; the
  measurement keys and receipt labels are `wplink_r90_probe` /
  `wpformat_r90_probe` / `wplink_r90_entry` — the sha table's labels match the
  actual receipt filenames (cosmetic, see F5).

### 2. Two greens — VERIFIED on the measured revision; landed-vs-measured delta is disclosed (F1)

- Run dirs exist and are the ones claimed:
  `runs/20261016T085347601935Z-wpstate-r90/measurements.json` (08:53:47Z) and
  `runs/20261016T085628919120Z-wpstate-r90/measurements.json` (08:56:28Z);
  `mode = "probe-wpstate-r90"` in both.
- The 8 receipt sha256 prefixes in the report's evidence table reproduce
  **8/8** exactly (e.g. run1 store `0bd7081d162f6674…`, run2 store
  `4ffa08082fe90716…`, run1 wplink `cb52c938048e4138…`, run2 wpformat
  `35cb424c5dfe59a2…`).
- Post-run census holds in both runs, all four entries: `own_nodes_after: []`,
  `own_modules_after: []`, `sinks_gone` all true, every `unloads[*].exit_code
  == 0`. Live re-check now (read-only, bounded): 0 `r90a` modules, 0 `r90a`
  nodes, no `r90a` processes.
- The measured revision is the worktree file
  `d9a07b14af4e605353b2b07e6fccff41ff0eb083c1d430fb58e7192b1fb276eb`
  (matches the report's declared sha). **The landed blob is not that file**
  (`d3119c5d…`): the landed r90 **family block is byte-identical** to the
  measured one (2159 lines, lines 35553–37711 ≡ WT 30982–33140, sha256
  `85f10b6619f9c45bb3b535a8f389dabfae0fcd750c3d67bf3115a156774d7eaa` on both
  sides) and the dispatch block is byte-identical
  (`797be5b6dbedcaaa54775b2a88158bffcd2f1d67a8d4a1303ef607d248792c80` both
  sides), so the green evidence transfers to the landed family. The only r90
  content delta is the one disclosed wiring line (F1).

### 3. SIGSEGV cold-read disclosure — VERIFIED, corroborated at both ends

- Code: `_wpstate_r90_settings()` (blob 35795–35816) retries once after
  `time.sleep(0.8)` when `exit_code != 0 or entries == 0`, and stores
  `attempts`.
- **Run 2 of the final bytes caught it live**: `w_settings.attempts ==
  [{"attempt": 1, "exit_code": -11, "entries": 0}, {"attempt": 2,
  "exit_code": 0, "entries": 25}]` in both the receipt
  (`wpstate_store_r90_probe.20261016T085607219492Z.json`) and the run's
  `measurements.json`; run 1 recorded a single successful attempt.
- Provenance of the disclosure is real: the first battery's receipt
  (`…084910016047Z.json`) carries the full cascade —
  `w_settings: \`wpctl settings\` rc -11`, `expected the 25-entry lattice,
  saw 0`, `type histogram drifted: {}`, both `w_meta … key set != wpctl
  settings id set` failures, and `w_cross_volume: … reads "Setting
  'device.routes.default-sink-volume' not found"` — exactly the "rc −11 …
  followed by … not found, in the same window" the report describes. The
  superseded run (085112) is likewise clean on the settings read.
- The crash is disclosed as unexplained; I did not reproduce it (no re-run).

### 4. `w_vanished_target` named-class — VERIFIED

- Code (blob ≈36725–36810) arms **only**: fourth-sink enumeration (else
  `coverage_blocked`), sink-input index resolvable, `target` reached the store
  (else "the leg is vacuous"), and `replay_node_present` (else failure). The
  outcome is a *recorded* named class —
  `fallback_to_default` / `linked_elsewhere` / `no_link` — with
  `edges_into_default` / `edges_from_replay` recorded; the code comment states
  the outcome is host/session-manager-state dependent and is deliberately not
  armed to either value. The replay is played as digital silence and records
  `content_witness: "declined_shared_default"`.
- Both greens: `outcome == fallback_to_default`, `edges_into_default` 2,
  `edges_from_replay` 2, `replay_node_present` true, `content_witness`
  `declined_shared_default`; the store-write half is armed and measured at
  1.811 s (run 1) / 1.056 s (run 2).
- The contradicted boundary claim is real: `reports/round-90/r90-boundary.md`
  lines 142–146 measure "no link forms (3/3 quiet + 3/3 load) — no fallback …
  within the 2.2 s window". The armed version of the negative **fired** in the
  superseded run (`failures: ["w_vanished_target: a vanished stored target
  fell back to the default sink"]`) and in the first battery; the report names
  the correction as not-surviving and carries it as a named class. Honest.

## Spot re-derivation of the entry claims (sample ≈40 of 60 legs, both runs)

All numbers below were read from the receipts; none contradicted the report.

- **Store**: `w_settings` 25 rows with Id/Name/Desc/Type/Default/Value,
  histogram `{Boolean:17, Float:5, Integer:1, String:2}`, `at_default` 25;
  `w_settings_flags` help carries `-d/--delete`, `-s/--save`, `-r/--reset`;
  `w_meta` exactly one 25-key scalar twin (id 36) and one 25-key schema twin
  (id 34), both key-set-equal to the CLI ids (ids recorded, not armed);
  `w_state_dir` = `default-nodes` + `stream-properties` only;
  `w_cross_volume` `Value: 0.064`, delta `3e-06`, attempt 1;
  write-path timings run1/run2 = 1.852/1.053 (`w_create`), 1.058/1.061
  (`w_props`), 1.483/1.057 (`w_pulse`, `cmd_ms` 4 both), 2.588/1.645
  (`w_target`); field split and `w_replay_fields`/`w_replay_target`/
  `w_explicit_target` (2/0 edges) as reported; both opt-out legs row-absent
  with the paired control row present.
- **Pmod**: control round trip rc 0 → sink seen → name-verified unload rc 0 →
  gone; `m_phantom` rc 0 + id, `mine` false at all 8 probes
  (0/30/60/120/250/500/1000/2000 ms), `id_recycled_by_foreign` **true in both
  runs**; `m_unassignable` rc 1 `Failure: No such entity`;
  `m_unix` rc 1 `Failure: Connection refused`; zeroconf split rc 1 / rc 0 +
  marker row + unload rc 0; stubs rc 1 `Entity exists` ×3, rc 1 `No such
  entity` for unknown; by-name control 2 → 1 unload → 0 with own sinks alive;
  prefix/nodename/unknown rc 0 with error only on stderr and count still 2;
  `m_byname_final` re-cleans 2 → 0.
- **Wplink** (both runs unless noted): `k_connect` 1; `k_bulk` rc 0 first pair
  only (2); `k_dup` rc 255 `File exists`, count unchanged; `k_two_ids` rc 255,
  nothing unlinked; `k_single_id` rc 0, one gone; `k_bulk_d` 2 → 1;
  `k_reversed`/`k_glob` rc 255; `k_w_valid` rc 0; `k_w_missing` SIGKILL at
  3.01 s bound; `k_w_late` rc 0 wall 1.52 (run 1) / 1.527 (run 2) with the
  late→L3 edge witnessed; `k_p_foo` rc 0 with 1 `foo=bar` link; `k_p_passive`
  rc 0, link present, no `link.passive` prop visible; `k_t`/`k_t_live` 0 B
  (stream alive at the live probe); `k_m` rc 255
  `missing output and input port names to connect`; `k_m_stream` 3279 B,
  killed at bound; `k_v` 34/38 rows (≥2 armed); listing patterns as reported.
- **Wpformat**: `f_rest` EnumFormat `1735b4739ef7` (1128 B), node and port
  Format 0 B with `res:-5`; `f_mid48` `1735b4739ef7`/1128,
  `91f7342230f7`/863, `5a828addfad7`/456, `e718690a7ce2`/1247;
  `f_setparam_sink` rc 0 + 622 B echo + `res:-5 … set param id:4 … failed`
  stderr; `f_setparam_stream` rc 0 + 622 B echo + 0 B stderr; `f_44k`
  `684a7c8dad24`/1247 vs `91f7342230f7`/863; `f_post` sticky `91f7342230f7`,
  port Format `res:-5`, EnumFormat unmoved.

## Independently verified integrate-note claims

`r90-integrate.md` (same commit) discloses the landing shape; I reproduced:
family-block sha `85f10b66…` (both sides, byte-identical), dispatch sha
`797be5b6…` (both sides), mutex tokens 135 → 136, prefix census merged/WT
`wpstate` 315/314 (+1 = mutex row), `wplink` 6/6, `wpformat` 7/7, 4 defs and
4 dispatch rows 1× each, `py_compile` rc 0, 0 conflict markers,
`custody.json deleted_kinds == ["mutex-sum","mode-ternary","suffix-ternary"]`,
`--help` rc 0 listing `--probe-wpstate-r90`, and the mutex refusal
`--probe-wpstate-r90 --probe-sox-r94` → rc 2 `error: choose one probe mode`
with **no** run dir, receipt, or lock written (main `corpus/live` still has no
wpstate artifacts). My independent AST pass over the landed block reproduces
its check exactly: **372 loaded names, 0 unresolved**. The commit contains
exactly the three files claimed (`+2183/−3` on the fixture; two reports).

## Findings by severity

**F1 — LOW (report-scope accuracy; disclosed deviation).** The landed bytes
are not the declared twice-verified revision, and `r90-author.md`'s Evidence
line ("both green runs are byte-identical to this file:
`d9a07b14…`") is true only of the *worktree* file; the landed blob is
`d3119c5d…`. Likewise `r90-author.md`'s "+2182/−2 … the only deletions are the
two shared-line splices" is false for the landing (+2183/−3, three replaced
wiring lines). The correction exists and is honest — `r90-integrate.md`
records the deliberate 1-line deviation (the `args.probe_wpstate_r90` token in
the `if sum([…]) > 1:` guard, justified by the canonical r8x/r9x landing shape
and `custody.json deleted_kinds`), names the hash divergence as expected, and
verifies the token behaviorally — but it claims the omission "is recorded
here and in `r90-author.md`", and `r90-author.md` does not record it. Net
effect: the greens transfer to the landed *family* by byte-identity; the
mutex line is the only landed r90 line no green run executed (I executed it:
rc 2, inside `parse_args`, zero artifacts). Recommendation: keep the
deviation, fix the cross-reference/wording in a fold note.

**F2 — LOW (numeric provenance).** `k_w_late` "rc 0 at 1.526 s / 1.527 s":
run 1's green receipt and measurement both record `wall_s 1.52`; **1.526 is
the superseded run's** value (`runs/20261016T085112273969Z-wpstate-r90`). The
"~26 ms after the port appeared at 1.5 s" delta is therefore ~20 ms for green
run 1. All other numbers in the §1/§3 tables reproduced exactly.

**F3 — LOW (arithmetic).** `r90-integrate.md`'s "in 4 hunks" is 6 hunks in
the actual commit diff (block, argparse row, mutex, dispatch, mode, suffix).
Combined with F1's +2182/−2 vs +2183/−3, these are counting slips, not
behavioral differences.

**F4 — INFO (disclosure completeness / harness shape).** The receipts dir
holds 17 receipts, including a third battery (09:01:59Z / 09:03:29Z /
09:06:00Z) from a revision that is **neither** the green revision nor the
landed one: its wplink receipt label is `wplink_r90_probe` (the green/landed
label is `wplink_r90_entry`). Its store entry records 5 failures (all
wedge-signature: sink-input unresolvable, target never stored, replay no
link, control no row) and its wplink entry recorded **0 legs with
`failures: []`**; its pmod `coverage_blocked` is the null-sink block the
report cites. The report discloses the third battery's daemon wedge and cites
that block, but does not itemize these failures or the label divergence. The
vacuous shape is worth naming for the harness: "failures empty" alone cannot
distinguish a wedged battery from a green — the greens are properly green
because their leg counts are 60/60.

**F5 — INFO (wording).** "all four entries `coverage_blocked` empty" means
*key absent* (the harness writes it only when non-empty; the superseded and
third-battery receipts carry non-empty lists). §3/§4 headings use function
names while the sha table uses receipt labels. Cosmetic.

**F6 — INFO (foreign-object census sample).** The wplink receipts show live
foreign `r89a_*` links/ports in session listings (`k_ids.head`, `k_v`,
`k_list_slot`) that the contention list does not name (it names
r91a/r92a/r93a/r93b/r99asmoke/r100a-sbx). Every counting leg is own-scoped
(`own_links`, `mine`), so no claim depends on them; the list is introduced as
a sample.

## Residual risk and verification gaps

- **G1 — no hash in run artifacts.** Grep confirms `d9a07b14`/`d3119c5d`
  appear nowhere in `runs/` or `r90-author/receipts/`. Byte-identity rests on
  the declared sha matching the current worktree file, whose mtime
  (09:23:28Z) **postdates** both greens (08:53:47Z, 08:56:28Z) and the third
  battery (09:01–09:06Z) — the file was rewritten after the runs. The
  strongest available binding is satisfied: the landed family block is
  byte-identical to the worktree block (sha `85f10b66…` both sides).
- **G2 — no live re-measurement.** No audio leg was re-run (reviewer scope;
  shared live session; the report's own post-greens host wedge). Today's
  session answers queries and holds 0 `r90a` objects, but the 60 legs' current
  live behavior is not independently re-measured.
- **G3 — partial line audit.** ~40 of 60 legs were re-derived from receipts
  plus all four entries' leg-name sets and all four headline claims; the
  remaining armed conditions were not line-audited. No discrepancy surfaced
  in the sample.
- **G4 — store-residue number not re-derivable.** "57 `r90a_`-tagged rows at
  the final census" has no snapshot; the store now holds 187 rows containing
  `r90a_` of 7841 (67 matching the seat's pid+nonce stream-key shape; the
  rest are device-node keys and later round-90 seats' rows). Consistent with
  the disclosed permanent-residue class; the historical 57 stands as
  author-declared.
- **G5 — `lsp` unavailable** (recorded above); AST + two `parse_args`
  executions were the substitute.
- The author report's "it never reproduced on a standalone invocation"
  (SIGSEGV) is not independently verifiable without re-runs; carried as
  author-declared.
- Canonical-runtime discipline: the author report explicitly defers to the
  canonical Rust runtime as the only judge ("Verdicts here are seat-side…"),
  no lane was rerouted or respawned under another identity, and the
  saturation claims are honest (two greens on the measured revision; the
  superseded and third batteries kept as disclosed history, not counted as
  greens). Resume/`resume_continuity_v1` paths: not exercised by this
  artifact — n/a.

## Recommendation

No actionable defect in the landed artifact: the r90 family block is
byte-identical between measured and landed bytes, the one landed deviation is
disclosed in-commit and behaviorally verified (rc 2 mutex refusal, no
artifacts), the four headline claims re-derive cleanly from the committed
blob and the worktree receipts, and the two greens are honest (60/60 legs,
empty failures, clean census). Findings F1–F3 are documentation-accuracy
items fixable in a fold note; F4–F6 are informational. **Recommendation:
ADMIT-with-findings** — recommendation only; the canonical Rust runtime
remains the sole judge.
