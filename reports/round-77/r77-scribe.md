# R77 scribe (audio) — evidence audit of the r76 ledger

Seat: **SCRIBE (leaf, report-only)**. Repo `/home/vgpnk/Projects/shokunin/audio-shokunin`.
Wave `shokunin-train-20261101-w17`. Host `plazir27`, Linux 7.2.3-arch1-3,
Python 3.14.7.

Write scope: **this report only** (`reports/round-77/r77-scribe.md`). Every
audit script lives in `/tmp/r77_scribe/` (outside the repo); no repo file was
created, edited, deleted, committed or pushed by this seat, and no probe was
re-run for the report. Read-only audit: all numbers below are re-derivations
from on-disk artifacts, not new measurements.

**Readings are stamped, and the wave is live.** Every reading below was taken
**19:39–19:45Z (2026-10-14)** unless a different stamp is named. The r77 lanes
are concurrent: at 19:40Z the worktree fixture was still byte-identical to
HEAD `18deef6` (`c35e2c62…`); at **19:42:29Z** the r77 author lane had it dirty
(`72378165…`, `git diff --numstat HEAD` = `1289/2`) and an r77-baseline replay
was running (pid 313184). The r76 blob pins in this report (`691d730d…`,
`c35e2c62…`) are therefore *historical* reads, true at 19:40Z and no longer
true of the live worktree.

---

## 0. Audit surface and commands

| # | audit item (from the assignment) | command / method |
|---|---|---|
| A1 | six entries' verdicts vs raw `measurements.json` leaves | `python3 /tmp/r77_scribe/entries.py <receipt>` + per-entry leaf dump over `corpus/live/runs/*capture-r76*/measurements.json` |
| A2 | fold diff vs the fold commit's declared set | `python3 /tmp/r77_scribe/leafdiff.py <pre-fold> <post-fold>` (leaf-walk, same convention as `corpus/live/r76-simplifier/compare_receipts.py`); all 91 pairs via `/tmp/r77_scribe/allpairs.py` |
| A3 | canonical-sha rescope vs verifier mechanism | `sha256sum corpus/live/runs/*capture-r76*/measurements.json`; leaf diffs of the verifier's three runs vs canonical |
| A4 | ~29 GB sweep | `du -sh corpus/live/r76-*`; `find corpus/live -type f -size +1900M`; `find -size +1G`; `stat` mtimes; `sha256sum corpus/live/r76-author/scratch/sev_probe.py` |
| A5 | report cites resolve | `/tmp/r77_scribe/cites2.py` (359 path-like tokens → repo-root / seat-dir / runs-dir / basename index); `/tmp/r77_scribe/stamps.py` (all `T…Z` receipt citations → `corpus/live/runs/`) |
| A6 | base rows / prior rows | `/tmp/r77_scribe/common.py` (common-key leaf diff) vs three r75 receipts |
| A7 | D1 vacuity sweep | `/tmp/r77_scribe/d1sweep.py` over all 14 receipts |
| A8 | fold's code-side declared set | `git show 18deef6:corpus/fixtures/measure_audio.py` vs `git show d566a31:…` (guard sites, `fmt_absent`, `seq[:=]`, roundtrip scratch) |

Repo state at read time: `git log --oneline -4` → `b0b5d4d` (report-last,
19:33:05Z) ← `18deef6` (folds, 19:31:49Z) ← `d566a31` (work, 18:30:35Z) ←
`2250be9` (r75 report-last). `corpus/live/runs/` = **5,643** dirs; `*capture-r76*`
= **15** dirs, **14** with `measurements.json` (one empty — §5.4).

---

## 1. A1 — the six entries re-derived from receipt leaves

Canonical receipt `corpus/live/runs/20261014T182450100472Z-capture-r76/measurements.json`
sha256 `ba36cd70f765826a9937fc78c62143c984790f1bdc26a4ad8aaf813cfc00f92f`,
1,172 leaves, `mode: probe-capture-r76`. All six entries carry
`failures: []`.

| entry | claimed (r76-author.md / r76-adjudicator.md) | receipt leaves | verdict |
|---|---|---|---|
| `capture_gate_r76_probe` | 12 legs, exact (rc, class) pairs (author §gate) | 12/12 match verbatim: `no_target_node` ×2, `pw_connect_failed`, `pa_no_such_entity` ×2, `pa_connect_failed`, `ffmpeg_io` 251, `ffmpeg_alsa` 251, `ffmpeg_esrch` 253, `alsa_hwparams` ×2, `alsa_unknown_pcm` | **confirmed** |
| `capture_bounded_r76_probe` | pw-record `-n` = 192044 B rc=1; arecord hw `-d 1` = 192044 rc=0 paced (`wall_lt_0.5s=false`); `-D null -d 1` = 192044 rc=0 unpaced (`true`); parec cap 262144 read; parecord TERM granule; ffmpeg pulse/alsa rc=0 finalized bucket 1.0 | every leaf matches (`file/bytes` 192044 ×4, `cap_bytes`=`bytes_read`=262144, `cap_honored` true, `data_64k_aligned` true, `duration_bucket_s` 1.0) | **confirmed** |
| `capture_sever_r76_probe` | TERM finalizes all four; KILL wound per consumer (pw-record/parecord `placeholder_8`+`zero`; ffmpeg `placeholder_ff`; arecord `placeholder_80000000` accept-and-lie) | `cells` rc/riff/data_declared_field match all 8 cells; `parsers/wave_frames_class` = `honest` on all TERM cells, `inflated` on `arecord_kill` | **confirmed** |
| `capture_name_axis_r76_probe` | pw-record extension-driven + flag override; parecord same; arecord flag-driven/name-blind; ffmpeg extension-strict (`rc=234`) | 14 legs match, incl. `ffmpeg_bin` rc=234 `ffmpeg_muxer`, `out_kind: missing` | **confirmed** |
| `capture_device_axis_r76_probe` | `{sysdefault, plughw:0,0, hw:0,0}` viable 192044 B; `{default, pipewire}` `alsa_hwparams`; `hw_first_mono` `alsa_channels`; `null` unpaced | 7 legs match exactly | **confirmed** |
| `capture_roundtrip_r76_probe` | 960044 B finalized, `pw-cat -p` rc=0, sox `wav==wav`, aplay `WAVE==WAVE`, both content witnesses true | `960044 == 44 + 240000×4`, `data_finalized` true, `sox.same_detect_class`/`aplay.same_detect_class` true, `nonzero_fraction_gt_half`/`peak_within_3db_of_member` true | **confirmed** |

**Prior-row check (independent).** Common-key leaf diff of the r76 canonical
against all three candidate r75 receipts (`…T172034398145Z` `9de8b8f8…`,
`…T165017429491Z` `0829a598…`, critic replay `…T183519581984Z` `6ffb0f81…`):
**0 differing leaves**; the only common-key difference is `mode`. The "17 base
rows byte-identical" claim reproduces independently of the author's own runs.

**Three claims in the six-entry surface are NOT receipt-derivable** (recorded
as honest edges, not defects):

1. `arecord -D null -d 1` wall time — cited as `~0.01 s` (author),
   `~0.02 s` (adjudicator, LOG). The receipt carries only
   `wall_lt_0.5s: true`; the verifier's independent re-measure was **0.001 s**
   and it labels both cited figures "10–20× high" with the class correct.
2. `8134×` inflation (adjudicator) — the receipt carries
   `wave_frames_class: inflated` and `data_declared_field:
   placeholder_80000000`, no byte count; the ratio comes from the verifier's
   byte re-derivation.
3. parecord/ffmpeg sever cells carry **no `bytes`/`data_actual` leaf** (only
   `data_actual_zero` + `data_64k_aligned`), exactly as the critic D2/D4
   family and the verifier §4b state. Any byte figure for those cells is
   derived or verifier-measured, never receipt-direct.

Verifier N3 is receipt-visible and confirmed: every parecord cell's
`file/fmt/rate` is **44100** while the stream is 48000 (e.g. `parecord_term`,
`parecord_term_bound`).

---

## 2. A2 — the fold diff: the brief's "20-leaf" premise does not reproduce; the re-derived diff is 5 leaves, all declared

**Post-fold verification receipt** = `corpus/live/runs/20261014T193039362478Z-capture-r76/`
(19:30:39Z, 70 s before the fold commit; the only run dir created after the
verifier's window and before the commit; `mode: probe-capture-r76`, six
entries, all `failures: []`, sha256 `6774ec94c8943ed6…`).

**Re-derived diff vs the pre-fold canonical (`ba36cd70…`), full leaf walk:
exactly 5 differing leaves.**

| # | leaf | pre-fold | post-fold | declared class |
|---|---|---|---|---|
| 1 | `measurements/capture_gate_r76_probe/gate/pwrecord_auto_target/stderr_tail` | `…id=2 seq:7 res:-2…` | `…id=<n> seq=<n> res:-2…` | **scrub-fire** (`seq[:=]`) |
| 2 | `…/gate/pwrecord_monitor_alias/stderr_tail` | `…id=2 seq:7…` | `…id=<n> seq=<n>…` | **scrub-fire** |
| 3 | `measurements/capture_roundtrip_r76_probe/capture_leg/argv` | `pw-record -P stream.capture.sink=true --target <default-sink> -n 240000` | `… -n 240000 --rate 48000 --channels 2 --format s16 <out>` | **argv** |
| 4 | `…/capture_leg/player_argv` | `pw-cat -p <pacer>` | `pw-cat -p stem_sections.wav` | **argv** |
| 5 | `…/detect_legs/sox/captured/input` | `live/r76-author/<tmp>/roundtrip_capture.wav` | `live/capture-r76-roundtrip/<tmp>/roundtrip_capture.wav` | **label** (seat-neutral scratch) |

**The fold commit's declared set, verbatim (`18deef6` body):** *"verify:
--probe-capture-r76 failures:{} on folded tree; receipt deltas = declared
leaves only (argv/label/scrub-fire + host-drift rows)"*.

⇒ **5 observed = 2 argv + 1 label + 2 scrub-fire + 0 host-drift.** Every
observed leaf is inside the declared classes; **zero undeclared leaves**. The
verdict surface is untouched: all six entries, every pinned class, size and
parser leaf are identical between pre- and post-fold receipts.

**The "20-leaf" premise in the assignment does not reproduce.** No on-disk
pair of capture-r76 receipts differs in exactly 20 leaves (all 91 pairs
computed). Relevant counts: post-fold vs canonical = **5**; vs the other
canonical-group receipts (`T183926`, `T192337`) = **5**; vs `T182210` = 6;
vs verifier run1 = 13; vs the contention run `T183404` = 26; vs verifier
run2 = 37; vs pre-fix runs = 27/37. Nearest to 20 anywhere on disk: **21**
(`T183404` vs canonical) and **22** (`T181743` vs canonical). The commit body
states the declared set qualitatively and carries **no count**, so no 20-leaf
number is checkable against `18deef6`; the reproducible post-fold delta is 5.

**Code-side declared set, verified in the fold blob (`c35e2c62…`)** —
`data_actual_zero is False` guards present at **two** check sites (`:3625`
`parecord_term_bound`, `:3781` sever TERM loop) and absent in the pre-fold
blob; `fmt_absent` at `:3118`; scrub regex `re.sub(r"id=\d+ seq[:=]\d+", …)`
at `:2975`; seat-neutral `ROOT/"live"/"capture-r76-roundtrip"` at `:4017`;
`ffmpeg_alsa_t` check at `:3649`; device-axis legs `sysdefault/plughw_first/
hw_first` checked at `:3981`. The commit body says the guard was applied to
"sever entry AND parecord_term_bound" (2 sites); the adjudicator's "all
**three** TERM-site checks" is a count overstatement (2 sites in the blob).

---

## 3. A3 — canonical-sha rescope vs the verifier's mechanism evidence

**Sha census, all 14 receipts (19:41Z):** 6 carry `ba36cd70…`, 8 do not.

| receipt (UTC) | sha256[0:16] | who / class | leaves vs canonical |
|---|---|---|---|
| `T181454123380Z` | `92d80fb4efc1e320` | author run 1, 3 failures | 33 |
| `T181743427243Z` | `d6f5fe2110bf911d` | author run 2, `failures: []` **carrying the D1 vacuous row** | 22 |
| `T182210846231Z` / `T182305432796Z` | `217702cc…` / `2ee23bfb…` | pre-fix clean pair (1 leaf apart: tmp-path leak) | 1 each |
| `T182450100472Z` / `T182539237046Z` | **`ba36cd70…`** | author canonical + rerun | 0 |
| `T183215518470Z` | **`ba36cd70…`** | critic run 1 | 0 |
| `T183309733895Z` | **`ba36cd70…`** | concurrent seat | 0 |
| `T183404004733Z` | `10d6d8b2fbf2b094` | contention run (critic's run-2 log points here) | **21** |
| `T183926872201Z` | **`ba36cd70…`** | post-commit run | 0 |
| `T192041795661Z` | `94150fbc1a5a3ccc` | verifier run 1 | 8 |
| `T192133221690Z` | `4b9d4897a75a32bb` | verifier run 2 | 32 |
| `T192337920612Z` | **`ba36cd70…`** | verifier run 3 | 0 |
| `T193039362478Z` | `6774ec94c8943ed6` | post-fold verification | 5 (all declared) |

**Verifier's mechanism evidence reproduces exactly.** Run 1's 8 leaves are all
`capture_device_axis_r76_probe/legs/sysdefault` flipping to `blocked: true`,
`error: "blocked: no verdict within 15 s"`, 44 B, `data_actual 0`,
`riff/data_declared_field: other` — with the entry's `failures` still `[]`.
Run 2's 32 leaves are `bounded/legs/ffmpeg_alsa_t` → rc 251 `alsa_busy`,
`file.kind: missing`; `sever/arecord_contention[0..3]` (`hw:0,0`/`hw:0,1`,
`named_failure: alsa_busy`, SIGTERM/SIGKILL) and the arecord sever cells
falling `hw:0,0 → hw:0,2`; and `inventory/pw_capture_ports` growing by
`pw-record:monitor_FL/FR`. That is the verifier's stated mechanism — a live
`pw-record` node surviving its process and contending for the ALSA card —
visible as receipt leaves, and the deviating runs are indeed
indistinguishable from the canonical run by `failures` (all `[]`).

**Rescope verdict: supported as worded.** The whole-receipt sha is
quiescent-host bounded: **6 receipts are byte-identical** (`ba36cd70…`) on a
quiet host, and the 8 that are not decompose into 4 pre-fix revisions
(`T181454` 33 leaves, `T181743` 22 — the D1-vacuous "clean" run — and the
`T182210`/`T182305` pair, 1 leaf apart by the tmp-path fix), 1 contention run
(`T183404`, 21 leaves), 2 verifier runs whose deviating leaves are exactly the
measured contention mechanism (`T192041` 8, `T192133` 32), and 1 post-fold run
(`T193039`, the 5 declared fold leaves). The verdict surface (`failures` +
every pinned leaf) is stable across all 14. The bound is carried
in the adjudicator (×2), reviewer LOW-3, and LOG; the author's own
"byte-identical rerun" line (`r76-author.md:191`) is *true for its pair* but
unscoped — the reviewer's LOW-3 asked for the bound, and reports are immutable,
so the ledger's scope lives in the adjudicator, not the author report.

### Conflicts found (verbatim, for the canonical judge)

**C1 — a byte-identity claim that the artifact falsifies.** `r76-critic.md` §1
and `corpus/live/r76-critic/RECEIPTS.md` list
`20261014T183404004733Z-capture-r76` (**critic run 2**) with sha
`ba36cd70… (same)`, under the headline *"the receipt reproduces byte-for-byte
(one sha, five runs, including two of mine)"* / *"one sha, four runs"*.
On disk that receipt is `10d6d8b2fbf2b094…`, 54,138 B, and differs from the
canonical in **21 leaves** (`arecord_duration_hw` → rc 1 `alsa_busy` missing
file, plus four `pw_capture_ports` including `Lavf63.1.101:monitor_FL/FR`).
The critic's run 1 (`T183215…`) is genuinely `ba36cd70…`; the run-2 row is
not. The reviewer's count at write time — *"four receipts carry that sha"* —
is the correct one; today the on-disk group is **6**. The adjudicator's
"byte-identical ×2" (author pair) is unaffected.

**C2 — three different diff sizes for one commit.** `d566a31`'s fixture delta
is cited as `+1123/−3` (r76-author, r76-critic), `+1147/−3` (r76-reviewer,
r76-simplifier), and `+1150/−3` (r76-adjudicator ×2, r76-baseline ×2, LOG.md).
`git diff --numstat 2250be9 d566a31` = **1147 insertions / 3 deletions**
(`--stat` prints 1150 *changed lines* = 1147+3, so the `+1150` form conflates
changed-lines with insertions). Only **`+1147/−3`** reproduces; `+1123` is the
author's mid-flight worktree value.

**C3 — guard-site count.** Adjudicator: *"`data_actual_zero is False` on all
three TERM-site checks"*. The fold blob has **two** guard sites; the commit
body says "sever entry AND parecord_term_bound" (2).

**C4 — a text/count mismatch inside the author report.** `r76-author.md:206`
says *"the 5 `-capture-r76` receipt dirs above"* while the bullets above list
**6** dirs (`T181454`, `T181743`, `T182210`, `T182305`, `T182450`, `T182539`),
and the empty `T181356…` dir (§5.4) is unlisted.

**C5 — transcribed traceback carets.** `r76-scribe.md:82-87` quotes
`run-main.out` with `~~~~^^^^^^^^^^^^^^` where the file has `~~~~^^^^^^^^`
(8 carets); the path/line/message are verbatim, so this is cosmetic, not a
claim defect.

---

## 4. A4 — the ~29 GB sweep: executed, verified by absence, no deletion receipt

- Critic D9 (18:32Z): `du -sh corpus/live/r76-author/scratch` → **29 G**,
  60 files, 11 rotation files > 1.9 GB (four exactly 2,147,483,692 B).
- **Now (19:43Z): `corpus/live/r76-author` = 15 M; `scratch/` = 15 M,
  44 files; largest retained file 3.2 MB (`nx_prd.bin`); 16 files gone.**
- **`sev_probe.py` retained** and byte-pinned: sha256
  `9c2c97eb79b1edf91a36f108e91c9834f9b035fbd0b8db649e8c321e1e3197b4` —
  identical to the pin in `r76-author.md:199-200` and `r76-reviewer.md:186`.
- **Zero files > 1.9 GB and zero > 1 GB anywhere under `corpus/live`**
  (largest: the 345.8 MB `r77-baseline/frozen/head-b0b5d4d.tar`). The
  r76-scribe's own 17:34Z snapshot counted 13 files > 1 GB under `r76-*`;
  that set is empty now.
- Timing: `scratch/` mtime **19:34:54Z**, i.e. after `b0b5d4d` (19:33:05Z) —
  the sweep ran at closeout, as the adjudicator's housekeeping line directs.
  The LOG's r76 entry does **not** record the sweep; the only record is the
  critic's D9 instruction plus the adjudicator's line. **There is no deletion
  receipt** — the sweep is evidenced by absence + the retained set, which is
  the strongest available evidence but not an operation log.
- The r77 scout's own flood is likewise gone: `corpus/live/r77-scout` =
  **36 M**, no `scratch/` dir, no file > 1 GB; `/tmp` (16 G tmpfs) at 52 %
  (7.9 G) — consistent with its "everything is deleted; footprint 36 MB".

---

## 5. A5 — report cites resolve (F4 precedent)

**Receipt stamps.** 70 `T…Z` citations across the ten r76 reports resolve to a
receipt dir. The 12 that do not resolve against `corpus/live/runs/` are:
(a) the **4 r75 receipts the r76-scribe itself documents as missing**
(`T164125737824Z`, `T164319396674Z`, `T164418398152Z`, `T164603163948Z`) —
**re-verified missing today**, so the F4 provenance hole is still open and no
r76 report contradicts it; (b) 7 boundary seat-local stamps, all resolving
under `corpus/live/r76-boundary/runs/` (12 per-run `env.txt` files present);
(c) 1 reviewer seat-local stamp (`T183354979511Z`) resolving under
`corpus/live/r76-reviewer/scratch/tree/corpus/live/runs/`. Every cited receipt
that should exist does exist, including the `…T182621929798Z-failing`
regression receipt and the r75 replay `…T192523848909Z-consumers2-r75`.

**File cites.** 359 distinct path-like backtick tokens were extracted. Of
these, **225 resolve directly** (repo root / the citing seat's dir /
`corpus/live/runs/` / a basename index over `corpus/live`, `corpus/fixtures`,
`corpus/artifacts`, `reports`, `scripts`); the residue is command strings,
line-count fragments, brace/ellipsis patterns, and directory-only fragments
(e.g. `scratch/`, `frozen/`) — **not** file citations. Every residual token
that could name an artifact was hand-checked (the 12 receipt stamps above, the
seat dirs, `r75-baseline/*`, the boundary's 12 per-run `env.txt`) and **all
resolve except the 4 r75 receipts the scribe itself documents as missing.**
Spot-confirmed in full: the verifier's whole §8 index (17 files), the critic's
`repro/` wavs, the reviewer's `sev_wounds/`, the simplifier's 8
`receipts/*.json` + `receipt-compare.txt`, the boundary's
`edge/partials-r76/usability.json` (21 rows; its `sev_ar_hw-mid` /
`sev_ar_null` rows match the report's table leaf-for-leaf), the scribe's own
18 audit files, and `r75-baseline/{post-state,runs-canonical-added,
runs-canonical-final}.txt` (the scribe's §2.3 window claim re-derived:
post-state lists both `??` stamps, added = exactly those two, final = 5,618
lines listing exactly the three `T164819/164913/165017` receipts).

**5.4 Hygiene item.** `corpus/live/runs/20261014T181356386452Z-capture-r76/`
is an **empty dir** (no `measurements.json`) inside the canonical runs dir,
created 18:13:56Z. The reviewer names it (`r76-reviewer.md:310`, "9 dirs, one
empty"); the author does not (C4). It is counted by both baselines' censuses
and by the r77 freeze, so nothing downstream is wrong — it is a stub that a
future reader of the canonical dir will have to skip.

**Other re-derived r76-scribe checks (all pass):** frozen tar 29,039 members
== manifest, sha256 `e22f852a0e184f6f…` == `archive-sha256.txt`; committed
ledger `8d59f552e1370c5e…` (blob `c4f5c619…`) identical before/after; pre-state
5,622 == 5,622 at 17:30Z (5,643 now; r77 freeze lists 5,643). The two r75
orphan receipts are still on disk with the claimed shapes (29 entries;
`…T171455054130Z` 7 non-empty per-entry `failures`; `…T172034398145Z` 0).

---

## 6. A6/A7 — prior-row stability and the D1 sweep, re-derived

- **Base rows:** 0 differing common leaves vs all three r75 receipts (only
  `mode`). The verifier's r75 replay (`T192523848909Z`, `6ffb0f81…`) is
  **byte-identical** to the critic's replay (`T183519581984Z`), and its only
  leaf vs the r75 canonical is `consumer2_paplay_ops_r75_probe/daemon_gate_dead/
  wall_s 0.001 → 0.002` — the unbucketed wall float the critic named.
- **D1 sweep over all 14 receipts:** exactly **2** receipts carry
  `sever/parecord_term/file/data_actual_zero: true` with
  `wave_frames_class: honest_empty` — `T181454` (3 failures) and **`T181743`
  ("clean", `failures: []`)**; the other 12 carry `false`/`honest`. The
  bounded `parecord_term_bound` leg is `data_actual_zero: false` in all 14.
  The critic's D1 and the verifier's §5 are therefore receipt-proven, and the
  fold's `data_actual_zero is False` guard closes exactly those two sites.
- **Boundary headline counts (seat-local, spot re-derived):** 48 pw-record
  cell records with rc ∈ {1 ×42, −9 ×6} ✓; 27 harness kills ✓; "20 of the
  rc=1 cells carry a complete, correctly finalized WAV" ✓ exactly 20 by the
  leaf predicate (`riff.riff == true`, `declared == size−8`,
  `data_declared > 0`); "229 cells total" vs **233 unique cell records on
  disk** — the delta is the last `-decl` batch (4 cells, 17:41:12Z) landing
  after the count; a snapshot difference, not a defect.

---

## 7. Findings summary (for the canonical judge)

**Conflicts (unresolved by this seat; reported verbatim):**

1. **C1** — critic run-2 receipt `T183404004733Z` is cited as `ba36cd70…` in
   `r76-critic.md` §1 and `RECEIPTS.md`; on disk it is `10d6d8b2…` with 21
   leaves off canonical. The "one sha, five runs" / "four runs" wording is
   falsified by the artifact it cites. (The adjudicated verdict did not adopt
   this count.)
2. **C2** — `d566a31` fixture delta cited three ways (`+1123/−3`, `+1147/−3`,
   `+1150/−3`); only `+1147/−3` reproduces (`--numstat`); `+1150` is
   changed-lines, not insertions.
3. **C3** — adjudicator's "three TERM-site checks" vs 2 guard sites in the
   fold blob (commit body says two).
4. **C4** — author's "5 receipt dirs" vs its own list of 6.
5. **C5** — scribe's traceback caret count (14 vs 8); cosmetic.
6. **Assignment premise** — the "20-leaf fold diff" does not reproduce; the
   re-derived post-fold diff is **5 leaves**, all inside the fold commit's
   declared set (`argv` 2, `label` 1, `scrub-fire` 2, host-drift 0), with
   zero undeclared leaves and an unchanged verdict surface.

**Carried open items (no claim error, but not closed by the ledger):**

7. F4 receipt persistence: the four r75 receipts are still absent; nothing in
   the repo guarantees a pinned receipt survives to read time. All r76 cites
   resolve *today*.
8. The ~29 GB sweep has no operation receipt (absence + retained set only),
   and the LOG's r76 entry does not mention it.
9. Empty receipt dir `T181356386452Z-capture-r76` remains in the canonical
   runs dir.
10. Three six-entry claims are prose/derived, not receipt-direct: the
    `~0.01/0.02 s` null-oracle wall (verifier: 0.001 s), the `8134×` ratio,
    and any byte figure for parecord/ffmpeg sever cells.
11. The whole-receipt sha bound is carried in the adjudicator/reviewer/LOG but
    not in the author report's own honest-bounds section (reports immutable).

**What this audit found clean:** the six entries' pinned verdicts, the
17-base-row identity, the D1 vacuity sweep, the fold's receipt delta and its
code-side guards, the sha-quiescence mechanism, the sweep, the base-row
stability, and the cite surface — all reproduce from on-disk leaves without
importing the fixture or trusting any report's own numbers.

---

## 8. Out of scope / not done

- No probe was re-run; no fixture imported; no receipt written by this seat
  (the assignment's F4 lesson is about receipt persistence, and this seat adds
  none).
- The r76 boundary/scout/baseline seat-local receipts were checked for
  existence and headline counts only, not re-derived cell-by-cell (their own
  seats and the r76 scribe's cross-check cover that surface).
- The r77 in-flight work (fixture dirty from 19:42:29Z, live replay pid
  313184) was not touched, not audited, and not judged; it is named only to
  stamp the r76 reads.
- No product code, config, contract, or judgment surface was modified; no
  git mutation of any kind.

## Artifact paths

- This report: `reports/round-77/r77-scribe.md`
- Audit scripts (outside repo): `/tmp/r77_scribe/{leafdiff,allpairs,nodediff,
  entries,baserows,common,cites,cites2,stamps,d1sweep}.py`
- Receipts re-derived: `corpus/live/runs/*capture-r76*/measurements.json`
  (15 dirs, 14 receipts), `corpus/live/runs/20261014T172034398145Z-consumers2-r75/`,
  `…T165017429491Z-consumers2-r75/`, `…T183519581984Z-consumers2-r75/`,
  `…T192523848909Z-consumers2-r75/`, `…T171455054130Z-consumers2-r75/`
- Blob pins used: `git show d566a31:corpus/fixtures/measure_audio.py`
  (`691d730d…`), `git show 18deef6:…` (`c35e2c62…`, snapshotted to
  `/tmp/r77_scribe/fold_blob.py` and `pre_fold_blob.py`)
- Retained evidence spot-checked: `corpus/live/r76-author/scratch/sev_probe.py`,
  `corpus/live/r76-boundary/edge/partials-r76/usability.json`,
  `corpus/live/r76-boundary/logs/run-main.out`,
  `corpus/live/r76-verifier/{run1,run2,run3,r75}.{stdout.json,exit}`,
  `corpus/live/r76-simplifier/receipts/*.json`,
  `corpus/live/r76-reviewer/scratch/tree/…/T183354979511Z-capture-r76/`
