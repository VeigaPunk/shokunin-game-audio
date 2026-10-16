# r100 scribe — provenance chain audit: report → receipt → author bytes → integrated bytes → pin

Seat: **scribe** (leaf; wave `shokunin-train-20261016-w24`, round 100). Model pin
`glmseat` invoked as first action (`glm-5-3-flash-max`; seat substrate GLM-5.3
Flash Max). This is a read-only chain audit: **no live family was run** (the
verifier seat alone runs `--probe-sofa-r100`), no original measurement was
recomputed, no source/fixture/report other than this file was written, no
commit, push, routing edit, or subagent. `RTP_R99_ALLOW_LAN_CONTROL` was never
set; no service or daemon was touched. Scratch:
`/home/vgpnk/Projects/shokunin/audio-waveb-resume/r100-scribe/commands.md`
(every command executed).

## 1. Identity, scope, pin

- **Pin:** `bb177513a615a32d3bc150ecbdcf78302e110d8c` = commit `bb177513`
  "r99 safety: require explicit opt-in before physical LAN control"
  (2026-10-16 12:29:41Z), parent `193acbed` "r100 integrate: recovered SOFA
  capstone and merged-byte evidence" (12:21:49Z). The main checkout
  (`/home/vgpnk/Projects/shokunin/audio-shokunin`) is **at the pin** on
  `[main]` with a clean tracked tree — the frozen pin is materialized, not
  hypothetical.
- **Family flag:** `sofa-r100`. Declared counts (review-common): nine entries,
  37 leg keys — verified against three receipts (§2.1).
- **Method:** literal source inspection, `git show` at the pin, sha256 byte
  comparisons, JSON parsing of existing receipts. No LSP was used; nothing
  below is described as semantic proof.

## 2. Chain audit — every link observed

### 2.1 Report → receipt (verified)

`reports/round-100/r100-author.md` §5 cites two green receipts; both exist and
parse as claimed (in the **author worktree** `audio-shokunin-wt-r100/`, see
§2.5):

| receipt | entries | legs | failures | coverage_blocked |
| --- | --- | --- | --- | --- |
| `corpus/live/runs/20261016T103052642013Z-sofa-r100/measurements.json` | 9 sofa | 37 (2+7+4+5+3+7+4+3+2) | `{}` | `{}` |
| `corpus/live/runs/20261016T103758962243Z-sofa-r100/measurements.json` | 9 sofa | 37 (same shape) | `{}` | `{}` |
| `corpus/live/runs/20261016T121334985146Z-sofa-r100/measurements.json` (main tree; integration note line 49) | 9 sofa | 37 (same shape) | `{}` | `{}` |

Entry/leg names match the author report §4 exactly (shape 2, azimuth 7, curve
4, rate 5, control 3, transfer 7, inert 4, clock 3, shared 2). The integration
note's r100 row ("rc 0, nine entries and 37 leg keys, no entry failures or
coverage blocks") is confirmed against the receipt bytes, and the orchestrator's
run log (`audio-resume-integrations/r100.rc` = 0; `r100.stdout` tail records the
receipt path and `"failures": {}`).

Counting note (prevents a stale-count misread): each receipt's `measurements`
dict has **26 keys** — the 9 sofa entries plus 17 canonical-battery section
placeholders (`ui`/`impact`/`movement`/`ambience`/`stem*`) with **0 legs** in
probe mode. "Nine entries, 37 leg keys" counts the sofa family only; a naive
key count of 26 is not a discrepancy.

### 2.2 Receipt → author bytes (verified, with a hash-scope observation)

The receipt JSONs themselves do **not** embed the fixture source hash — a
full hex64 walk of `run-1.measurements.json` finds only per-leg
`analysis/sha256` (capture digests) and `host/sofa_sha256` +
`host/default_sofa_sha256` (both `2768ac84…`, the symlink-identity value the
boundary §3.4 and author §3 report). The frozen-bytes binding
(`measure_audio.py e965f56c…`, `r100sofa.py 26e96660…`) is carried by the four
sidecars — `RECEIPTS.md`, `run-log.txt`, `stability.txt`, `exit-census.json` —
all four state the hashes, and `manifest.sha256` covers all 8 files in
`corpus/live/r100-author/` and **verifies OK** (`sha256sum -c`, rc 0). The
binding is therefore intact but sidecar-borne, not receipt-borne (finding F1).

### 2.3 Author bytes → integrated bytes (verified)

- Author worktree bytes match every declared hash today:
  `sha256sum` → `e965f56c…` / `26e96660…` (= RECEIPTS.md, run-log,
  stability.txt, exit-census.json, author report §5).
- **Sofa family slice is byte-identical** between the author's frozen bytes and
  the pin: extracted from the `# ROUND 100 -- the sofa/spatializer` header back
  to its `# ---` separator, forward to `def main` — author lines 35061–36503 vs
  pin lines 52809–54251, slice sha256 `0a59febb…` **identical**. The
  integration note's "the family and dispatch are verbatim author slices" is
  byte-verified for the family body.
- `r100sofa.py` is byte-identical at the author worktree, at `193acbed`, and at
  the pin (`26e96660…` all three).
- Orchestrator comparison evidence (frozen under
  `/home/vgpnk/Projects/shokunin/audio-resume-integrations/`): `cmp-r100-fixture`,
  `cmp-r100-report`, `cmp-final-source` all **rc 0** (byte-identical);
  `stage-r100.py` = `5c8f7e9d…` = `193acbed:corpus/fixtures/measure_audio.py` =
  `source-final.sha256` = `r100-source.sha256` — the integration ran on exactly
  the bytes now committed.
- Wiring verbatim: argparse row `parser.add_argument("--probe-sofa-r100",
  action="store_true")` identical in both trees (author 36635 / pin 54389);
  `mode = "probe-sofa-r100" if args.probe_sofa_r100 else …` and
  `suffix = "-sofa-r100" if …` lead both select chains; the family lock path
  line is inside the (already identical) slice.
- `git show 193acbed --stat`: 4 files, 3126 insertions / 3 deletions;
  `measure_audio.py` 1487 changed lines = the author's declared **+1484/−3**
  (1484+3=1487) plus the new fixture (1175), author report (395) and
  integration note (72).
- All three r100 reports are byte-identical between main tree and author
  worktree: `r100-author.md b517adfa…`, `r100-scout.md 645b606f…`,
  `r100-boundary.md 0ba489e7…`.

### 2.4 Integrated bytes → pinned revision (verified)

`bb177513` touches only `corpus/fixtures/measure_audio.py` (64 lines — the
rtp-r99 LAN-control opt-in) and adds tracked
`corpus/fixtures/test_rtp_r99_lan_control.py` (49 lines, blob `587e6548`). The
sofa slice sha is **identical at `193acbed` and at the pin**, so the r99 safety
commit did not perturb the r100 family: pin `measure_audio.py` =
`801e153b…` = `5c8f7e9d…` + safety delta, with the r100 evidence chain valid at
the pin. `r100sofa.py` at the pin imports stdlib only (argparse…wave; no
`pwlib`, no local imports) — the author's self-containment claim ("a verifier
can run it from tracked bytes alone") is supported at the pin.

### 2.5 Timestamps, locations, uncommitted state (observed)

- Ordering is coherent in UTC: author runs 09:41Z–10:37Z inside the declared
  window 09:19Z→10:38Z; exit census 10:38:30Z; integration run 12:13:34Z;
  integration commit 12:21:49Z; safety commit (the pin) 12:29:41Z. Receipt
  stamps are UTC; host tz −0300 matches the commit dates.
- **Location split:** the author's eight run receipts and
  `corpus/live/r100-author/` exist **only in `audio-shokunin-wt-r100/`**; the
  main tree holds the integration receipt `20261016T121334985146Z-sofa-r100`
  plus `corpus/live/r100-boundary/` and `r100-scout/`. Citations in the author
  report resolve against the worktree; citations in the integration note
  resolve against the main tree.
- **Nothing is committed from `corpus/live/`:** `git ls-files corpus/live/runs`
  contains zero `sofa-r100` paths; all receipts are untracked local files. The
  integration note discloses this ("not silently claimed to be uploaded by
  Git"); this report preserves it: **no r100 receipt is committed or remotely
  available.**
- Worktree state matches the author report: `wt-r100` @ `6fcff792` ("r94
  adjudicate…"), zero commits, `measure_audio.py` modified-uncommitted (the
  frozen bytes), `r100sofa.py`/receipts untracked, and the pre-existing
  tracked-dirty `__pycache__` pyc the author disclosed. The main tree's pyc is
  currently clean at the pin.
- The canonical-battery receipt the author cites (`20261016T102052126803Z-normal`)
  exists in the worktree runs dir.

## 3. Original vs corrected artifact distinction (verified, labeled)

`run-log.txt` labels all eight author full-battery receipts, and the labels
check out against the receipts themselves:

| stamp | era (run-log) | observed |
| --- | --- | --- |
| 094138682218Z | pre-fix clobber | failures=1 — only the teardown-path failure survived (§6.1 class) |
| 094854139065Z / 095537818511Z | pre-fix clobber | failures=0 — meaningless (laws never read) |
| 100240878238Z | **RED** (arming fixed) | 6 FAIL lines = exactly the 3 disclosed defect classes: 4 shape-law reads (frames/peak/nonzero), `i_default` key, shared silent take |
| 101141575150Z | green, SUPERSEDED | **38 legs** — `shared_az90_retry` leg materialized (one-retry policy); see F2 |
| 101821860983Z | green, SUPERSEDED | 37 legs |
| 103052642013Z / 103758962243Z | **GREEN on frozen bytes** | cited by the author report |
| 121334985146Z | integration run on `5c8f7e9d…` | cited by the integration note |

The failure-accumulator fix demonstrably **precedes** the cited greens (RED at
10:02Z, greens at 10:30/10:37Z), and the arming-live negative control is
receipted: `negative-control.json` lists 21 failures and ends
`"verdict": "ARMING LIVE"` (`negative-control.err` is empty, manifest-verified).
The corrected-key fix is visible in the green receipts: `i_default` compares
`sofa_sha256` vs `default_sofa_sha256` (both `2768ac84…`), and the shape legs
carry analysis-level `frames`/`peak`/`nonzero`. The byte-identical
shared/private az90 claim is visible in the receipt: `shared_az90`,
`az90_r0/r1`, `x_az90`, `i_radius30` all carry capture sha `7a344c25…`.

## 4. Findings (severity-ordered)

No high- or medium-severity defect was found in the r100 chain. All links
verified byte-level. Remaining findings are calibration/record items:

- **F1 (low, hash scope, observed):** the green receipts do not embed the
  fixture source hash; the frozen-bytes binding rests on the four sidecar
  files (themselves manifest-covered). If sidecars and receipts were ever
  separated, the green runs' byte binding would rest on prose. Smallest
  correction, if the lead wants it: add a `source_sha256` field when writing
  future receipts; no existing artifact needs mutation.
- **F2 (low, wording, observed):** RECEIPTS.md says the two superseded greens
  differ from the frozen bytes "without changing a single armed value or
  measurement" — true for 1018→frozen (provenance-comment-only), but run 1011
  has **38 legs** (`shared_az90_retry` materialized under the one-retry
  policy), so the two superseded runs are not shape-identical to each other.
  Record-only; no artifact correction proposed.
- **F3 (informational, observed):** `LOG.md` and `SCORECARD.md` contain **zero**
  `r100` rows (LOG's last entry is ROUND 97; the r97 "required safety fold"
  anchor `b8ff4efc` resolves to the r97 author commit). The round is **not
  closed** in the round-ledger artifacts; the integration note says the same
  ("Independent wave-B review and final adjudication remain pending"). This
  report admits nothing and claims no judge verdict.
- **F4 (informational, observed):** all r100 receipts are untracked local
  files; author-side receipts live in the wt-r100 worktree, the integration
  receipt in the main tree (§2.5). Nothing here implies committed or remote
  availability.
- **F5 (informational, observed):** citation locations resolve —
  `r100-boundary.md` exists; boundary `scratch/window-landing.json`,
  `scratch/fine-ild.json`, `scratch/align.json` and
  `receipts/axes-azcurve.json` (the 3-decimal ILD source for §3.1) all exist
  under `corpus/live/r100-boundary/`; the `audio-resume-integrations/` frozen
  evidence dir exists (115 files). Coverage labels in the integration note
  ("no entry failures or coverage blocks") match the receipt bytes; the
  author's disclosed ambiguities (the ~2e-4 XFER recompute ambiguity, the
  coarse-recipe witness recorded-not-armed) are carried in the report text,
  not silently dropped.

## 5. What the evidence supports — and what stays blocked

**Supported (observed):** the r100 provenance chain is intact end-to-end at
pin `bb177513…` — declared counts match receipts; author bytes match declared
hashes; the family slice, supporting fixture, wiring tokens and all three
reports are byte-identical through integration and the safety commit; the
accumulator fix precedes the cited greens; the arming-live negative control
and the RED run are receipted; mutex (12/12 rc 2), help and compile checks
(rc 0) exist as frozen orchestrator evidence.

**Not claimable from this seat:** every physical number remains the author's /
orchestrator's receipted output — this seat recomputed no measurement and ran
no family (verifier-only). The intermediate stage hashes in the integration
note (`91f42214…`, `59708fca…`, `7b372a6b…`) were **not** re-verified by this
seat (r93/r99 chain scope). `corpus/QUALITY.md` / `corpus/README.md` conformance
and any learning-trend verdict remain unmakeable, per the plan. Audio publishing
remains separately blocked pending operator approval; no fold or
round-closure is declared here.

## 6. Residual risks and explicit checks not run

- No live execution of any family; no `--probe-sofa-r100` run; the
  verifier's export/run recipe was not exercised by this seat.
- Boundary/scout receipts were checked for existence and cited-file presence,
  not for internal content (other seats' scope).
- The 1.5 GB full-history archive was not touched (and must not be copied).
- No LSP; no semantic analysis claimed — byte/hash/JSON evidence only.
- Shared daemons were left exactly as found; the family lock files exist
  unheld (`exit-census.json`: `family_lock_held: false`, content
  `pid=978564 ns=r100a_978564` — a released lock's stale content, recorded not
  repaired).

## 7. Artifacts and attribution

- **This report:** `reports/round-100/r100-scribe.md` (the only repo file this
  seat wrote).
- **Scratch:** `/home/vgpnk/Projects/shokunin/audio-waveb-resume/r100-scribe/commands.md`
  — the faithful command log (18 numbered command groups).
- **Read-only evidence relied on:** author report/receipts in
  `audio-shokunin-wt-r100/` (author seat's outputs); integration note and
  receipt in the main tree (orchestrator's outputs); frozen orchestrator
  comparisons under `/home/vgpnk/Projects/shokunin/audio-resume-integrations/`;
  boundary/scout receipt dirs; `LOG.md`/`SCORECARD.md` tails. All hashes and
  counts above were recomputed by this seat **from those bytes**; the
  measurements inside the receipts are quoted, not re-derived.
- Sibling wave scratch observed at audit time (state only, no conclusion):
  `r100-critic`, `r100-simplifier`, `r100-verifier` present;
  `r100-reviewer` not yet present in `audio-waveb-resume/`.

— scribe, round 100, pin `bb177513a615a32d3bc150ecbdcf78302e110d8c`. Advisory
only; not a gate-admission or shipping decision.
