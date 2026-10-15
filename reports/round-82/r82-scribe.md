# r82 scribe — evidence custody + claim audit

host: `plazir27` (local = UTC−3). Lane `~/Projects/shokunin/audio-shokunin`.
Seat: SCRIBE (wave-B, r82). Scope: audit the r82 dossier —
`reports/round-82/r82-{author,baseline,boundary,scout}.md` plus the
`corpus/live/r82-{author,baseline,boundary,scout}/` evidence trees and the
boundary `manifest.json` — for claim→sha chains, arithmetic reconciliation
(76 legs / 304 executions / 4 runs / cell counts), file existence and hash
re-derivation. **Read-only on everything except this report; no commits, no
judgment passed** — discrepancies below are handed to the canonical judge as
adjudication items.

Audit entry state: HEAD `fd0bc8b0`, fixture
`corpus/fixtures/measure_audio.py` sha256
`eb86576063b359b8bd69d5147b03e443e73990052e76f9221a552cd0864d20b4`
(matches author §6 verbatim). All four r82 reports are tracked
(`git ls-files reports/round-82/`).

---

## 0. Verdict

| # | question | answer |
| --- | --- | --- |
| 1 | Do the claim→sha chains hold? | **Yes, with one bytes-not-preserved gap.** Fixture chain, all 4 formal `-ffmpeg-r82` receipt shas, all 8 author battery shas, all 8 baseline shas, the baseline tar sha, all 11 boundary §IV shas and all 10 scout §8 shas re-derived and match. The intermediate fixture revision `f9d88dcc…` (run1/run2 + author runs-a first three commands) exists only as a recorded sha in `commands.log` — its bytes are not in the repo (ADJ-11). |
| 2 | Does the arithmetic reconcile? | **Yes for the headline cells**: 8+17+13+14+8+6+7+3 = **76 legs**; 76×4 = **304** formal leg-executions (all four receipts `failures {}`, per-entry `failures []`, `sinks_gone` true / `own_nodes_after []`); **4 formal runs** byte-frozen on the two fixture shas; author battery census 86/136 per pass ×2 = 172/272; baseline census identical; author final-pair stability 17 612 leaf paths / 50 semantic / base rows 100 % exact. **Five off-by-count defects found** (ADJ-1/4/5/6/7). |
| 3 | Do the claimed files exist? | **Yes.** Every receipt, log, comparison output, tool and report cited by the four reports is present at the claimed path; copies are byte-equal to canonical receipts in all 3 copy-bearing seats (author 12/12, baseline 8/8, boundary manifest 803 files, scout 175 per-leg dirs). |
| 4 | Any unreported evidence? | **Yes — one.** A fifth `-ffmpeg-r82` receipt (73 legs, pre-boundary-encoding) is on disk and tracked in `aa03c347` but absent from the author report and its `commands.log`/`receipt-shas.txt` (ADJ-1). |
| 5 | Custody verdict | **INTACT for the four formal runs and all seat verdict surfaces; DISCREPANCIES in five reported counts and in one timeline label.** No verdict-surface contradiction was found between a report and its receipts; every flagged item is a count/label/inventory defect, not a falsified measurement. Items ADJ-1…ADJ-9 need adjudication; ADJ-10/11/12 are notes. |

---

## 1. Claim→sha chain, re-derived

### 1.1 Fixture chain

| revision | claimed in | re-derivation |
| --- | --- | --- |
| `eb86576063b359b8bd69d5147b03e443e73990052e76f9221a552cd0864d20b4` | author §6 | `sha256sum corpus/fixtures/measure_audio.py` → match; 17 389 lines; `compile()` clean (author §1 "py_compile clean" — verified without writing a `.pyc`) |
| `f9d88dcc40945e298e1e5c6405547e8322febce89f0b424cee8570bc48fa5d0d` | author commands.log (run1/run2, runs-a) | recorded sha only; no byte copy found (`grep -rl` → commands.log + r82-verify tree copies of those logs only). Delta vs `eb865760` is disclosed as the ci6 dead-expression cleanup but is **not byte-verifiable** (ADJ-11) |
| `5eaba74b532eb9c62d529fe3d94534c36cb3b3954365cb61b8552ade9ed49d82` | baseline §1 | `git show b7d80d0:corpus/fixtures/measure_audio.py \| sha256sum` → match; `git cat-file blob 38c67960…` → match (807 112 B); `tree/corpus/fixtures/measure_audio.py` → match |
| `ac9c64a1b51f3c986b08644c8c0e6b59be8efce1d3a7baa6994f5b3a1a4ae717` | baseline §1 (r81 freeze) | r81-baseline `env.txt` pins it at HEAD `15c6a35b`; `ed799e5e:fixture` → match; `ac9c64a1 → 5eaba74b` diff = **+1661/−3, 5 hunks** (r81 family insertion + 4 main() hunks), matching baseline §1 verbatim |
| tar `2cecf391a000fe28f6b6f0bbd7eeeb072be743a9355a6f794d9707a4a1e13b14` | baseline §1 | `sha256sum /tmp/r82-baseline-work/head-b7d80d0.tar` → match byte-exact, 483 727 360 B; `tree-archive.txt` members 30 981 / files 23 997 / dirs 6 985 / symdiff 0; `/tmp` `extracted.txt` vs `ls-tree.txt` identical (23 997 lines each) |

### 1.2 Author receipts (`corpus/live/runs/*-ffmpeg-r82/`)

| receipt | sha256 (re-derived) | copy vs canonical | legs | failures |
| --- | --- | --- | --- | --- |
| `20261015T194415547218Z` (run1) | `cd281759b47b1fa554273966cc23f651aa6da3d3de6fb1a75ce2f8882720c643` | = `run1.measurements.json` | 76 | `{}` (stdout), per-entry `[]` |
| `20261015T194659044785Z` (run2) | `9d59d5b1278369d87e3bf2baf5d34731af00e2e24d01319b21e0d74b89e5b020` | = `run2.measurements.json` | 76 | `{}` |
| `20261015T200955375107Z` (final3) | `c6c4287d265f8c784022470134908dc12152208adf9470a887aa4cd149cb947f` | = `final3.measurements.json` | 76 | `{}` |
| `20261015T201238976393Z` (final4) | `647b85fa100e7387fb08fe56b6521e311383f3b75c67804d1ef767ca426007c5` | = `final4.measurements.json` | 76 | `{}` |
| `20261015T193606166445Z` (**unreported**, ADJ-1) | `89758379f32aa8b47e7c93acf20e66b947f385aeaf5718d0796e88d8a772db16` | not copied, not in receipt-shas.txt | **73** | `{}` |

All four formal receipts: `commands.log` SHA before/after = `f9d88dcc…` (run1/run2) and `eb865760…` (final3/final4); `receipt-shas.txt` matches the four values above; `post-state.txt` (20:15:05Z) = zero `r82ff_*` sinks/modules/nodes/procs.

### 1.3 Author prior-battery replay (8 canonical receipts + copies)

| mode/pass | canonical stamp | sha256 (copy = canonical, re-derived) |
| --- | --- | --- |
| normal a | `20261015T194703860914Z` | `8e8cdad6cc3c356d07c463498f4759b8d73e73935cf591d117732f09ffaffb1b` |
| capture-r78 a | `20261015T195038800555Z` | `093a589db316f9095be7eb41db4f89e5e28f2697ec45ffdb4600114199603173` |
| capture-r79 a | `20261015T195558777081Z` | `7eeb96f93283b7862a459513e57ed23f6f8266468ef1b471c3508242ecf88c8d` |
| module-r80 a | `20261015T195628459461Z` | `4cd3c6eed1b3e289c90bf216e45c104c691a056461d7ec5b63e1983a93e05c3f` |
| normal b | `20261015T195629594751Z` | `8e8cdad6…` (identical) |
| capture-r78 b | `20261015T195956544262Z` | `ce13f92abb48ab9af9b40983891a48bd5b56ffe1cd661c317db301b67d9b7e38` |
| capture-r79 b | `20261015T200537249352Z` | `7735dbd753c628d8195f876fdd0866faf7612964831461057dfb7373798f2604` |
| module-r80 b | `20261015T200607214030Z` | `9b064ab0738d66ab948fadf55e982b5367a1222e88a72b9f6449d002caed314a` |

Red-run attribution re-derived from the receipts: `runs-a/capture-r78` and
`runs-b/capture-r78` red once each in `playback_default_follow_r78_probe`;
`runs-a/capture-r79` red in two cases (`b03_dotmonitor`, `b05_garbage`);
`runs-b/capture-r79`, both `normal`, both `module-r80` green — exactly as
author §4 states (5/8 clean).

### 1.4 Baseline receipts and byte identity

All 8 copies in `corpus/live/r82-baseline/runs-{a,b}/` are byte-equal to their
canonical tree receipts (`tree/corpus/live/runs/<stamp>/measurements.json`),
and match the baseline §2 table:
`8e8cdad6…` (normal ×2), `cc71d132741d5ff1…`, `bdeeda54503fd782…`,
`919ce1115062e518…`, `d9bfa84511c2a806…`, `f60025dfbae87519…`,
`82ee18ccc61398e4…`. `head-watch.log` = **124 samples**, `5eaba74b…` in all
124; HEAD transition `b7d80d0` → `9725e53` between 18:59:35Z and 18:59:45Z
(lines 374/379); `grep -c gst-launch` = 0. Tree now holds 24 005 files /
5 310 run files / 0 symlinks = the archived 23 997/5 302 plus the 8 battery
receipts — consistent.

`byte-identity.txt`'s "375 of 523 landed normal receipts" re-derives forward:
the corpus now has **525** `-normal` receipts, **25** distinct byte values and
**377** at `8e8cdad6…` = 523/375 + the author's two matching `normal` runs.

### 1.5 Boundary and scout chains

- Boundary §IV: all 11 sha16 prefixes re-derived exactly —
  `r82bnd_probe.py 25a1a5f86c21c986`, `setup 0424602424899216`,
  `c1 33ca97a5831b9cc8`, `c2 9e04ca364a98a126`, `c3 910def3a5c9db666`,
  `c4 92695e375fa42e7b`, `c5 9896e3779cbfaebf`, `c6 4d598bc19615032d`,
  `summary e069fb4bb4431258`, `teardown 834128007069fd83`,
  `manifest e239ef14e452bb69` (manifest embeds a generation stamp, footnote ¹
  is correct — no regeneration happened since).
- `manifest.json`: `n_files = 803` ✓; the only `r82bnd*` entry in it is
  `r82bnd_probe.py` (ADJ-10 wording note). Tracked set is 805 = 803 indexed +
  `manifest.json` + `__pycache__/r82bnd_probe.cpython-314.pyc`.
- Scout §8: all 10 receipt shas re-derived exactly (`13d892fbae6e9dd4`,
  `b9fc15f440e46dee`, `16a39637d6a880df`, `cb00415df0eb97a8`,
  `63c71c94117bac2c`, `41e17c3a23ea2699`, `c64e0d526b03a831`,
  `abf4afda7adbc4a5`, `f06b73fe3801f34c`, `b522225e3ebeb524`); 175 per-leg
  `cmd.txt` dirs ✓; 2.6 MB ✓; HEAD `a2616f7` exists (`a2616f73`); `runs/extra/`
  empty ✓. The scout evidence tree is **untracked** (0 tracked files) — custody
  currently host-worktree-only (ADJ-12; same pattern as r91/r96/r97 scouts).

---

## 2. Arithmetic reconciliation

### 2.1 The assigned cells

- **76 legs** = 8 + 17 + 13 + 14 + 8 + 6 + 7 + 3 — verified leg-by-leg against
  all five receipts; per-run totals 76/76/76/76/73.
- **304 executions** = 76 × 4 formal runs, all four `{"failures": {}}` exit 0,
  every r82 entry `failures []` and `sinks_gone`/`own_nodes_after` clean.
  On-disk total including the unreported dev run is **377** (ADJ-1).
- **4 runs**: the four formal receipts above; the report's word "total" is
  falsified by the fifth receipt (ADJ-1). Final pair is byte-frozen on
  `eb865760…` per `commands.log` before/after.
- **Cell counts** (all re-derived): author battery per pass `normal 17/0`,
  `capture-r78 25/59`, `capture-r79 25/67`, `module-r80 19/10` = **86 entries /
  136 legs**; ×2 = 172/272. Baseline `rows.txt` census identical, leaves
  `373 / 12 368 / 23 618(a)–23 617(b) / 1 786(a)–1 785(b)`.
  Author final-pair stability TOTAL row = **17 612 leaf paths, 50 semantic**,
  all non-r82 case rows exact ("base entries 100 % exact" ✓); the §6 baseline
  stability table totals re-derived exactly from the files' TOTAL rows
  (per-case sums are 2× because each file also carries its own TOTAL row).

### 2.2 Boundary leg inventory vs report

| stage | report claim | receipt on disk | note |
| --- | --- | --- | --- |
| c1.json | 13 legs | **13** | ✓; 15/15 hostile non-empty strings + 4 empty reps reconcile exactly across c1 (12 non-empty incl. control, 1 empty) + c1x (4 non-empty + control re-run) + `empty_r1..r3` |
| c2.json | 25 legs | **27** | **ADJ-5**: 19 EIO + 6 alias/monitor + 2 `nonexistent_monitor_r0/r1`; 25 = first-pass count before the two `.monitor` probes were appended |
| c3.json | 24 legs | **24** | ✓ |
| c4.json | 11 legs | **11** | ✓ (6 play + 5 cap) |
| c5.json | 6 legs | **6** | ✓ (`def_n=5, ns_n=0` in 3/3 set reps) |
| c6.json | 16 legs | **15** | **ADJ-6**: 8 `alsa_rate_*` + 6 `pulse_*` + `alsa_ch_0`; c6x 12 ✓ |
| c1x/c2x/c3x/c6x | 5 / — / 4 / 12 | 5 / 37 / 4 / 12 | ✓ |

Boundary EIO census: **41** rc=251 legs total (19 c2 + 22 c2x), min/max wall
**0.022–0.063 s** — the range claim holds over all 41; the §0 count "30 EIO
reps" does not reconcile (ADJ-7).

Boundary re-link numbers re-derived from `c4.json`: playback Δ 0.035–0.041 s
(quiet r0–r2) / 0.050–0.057 s (hogs r3–r5); capture Δ 0.019–0.053 s; pump
Δ 0.024–0.046 s — matching §0/§4. The stored tone window sets are **0.25 s**
steps (15/15 play, 25/25 cap per rep); the report's "63/63 at 0.1 s" has no
stored artifact (ADJ-8).

### 2.3 Verdict-surface spot checks (author final4 + run1, all match report §2)

`d1` rc=234; `d2` rc=0 zero rows; `d4` `*`=SPDIF (`agree`); `c1/c3×3` rc=251
`ff_io_error`; `c13` rc=0 literal-stripped target + `stream.capture.sink=True`;
`c14` `node.rate=1/12345`, `fragsize=2468`, wav 12345; `c7` env `node.name`
overridden to `Lavf63.1.101` while `stream.capture.sink=true` lands; `c8` wav
44100/1ch; `c11` 253 `ff_no_such_process`; `p12` 187 `ff_pulse_sink_info`;
`p1/p5/p6/p9` as tabled; `ci4` fragsize 9600 + no warning; `ci5` rc=−6
`ff_sched_assert`; `ci6` swallowed (wav 48000/2ch); `a5_realization=params_251`;
`a2` rc=0; `a6` wav 44100; `f0` no `client.api` + `media.role=Game`; `f1`
target=SPDIF (env ignored) `client.api=pipewire-pulse` `tlength=6144`; `f2`
rc=0 0.161 s; `e1` 222; `e4/e5` −6 libpulse asserts; `t3` rc=1 at `-n`.

---

## 3. Adjudication items (no judgment passed — for the canonical judge)

| # | seat | severity | item | evidence |
| --- | --- | --- | --- | --- |
| ADJ-1 | author | moderate | Unreported 5th `--probe-ffmpeg-r82` execution. Report §4 "four `--probe-ffmpeg-r82` executions **total**"; §6 "two `-ffmpeg-r82` dirs". On disk: 5 receipt dirs (4 formal + `20261015T193606166445Z`, **73 legs**, dev-only delta = exactly `c13`/`c14`/`p12`), tracked in `aa03c347`, absent from `commands.log`/`receipt-shas.txt`/report. Formal 304 count unaffected; total on-disk 377. | dir + receipt; leg-set diff |
| ADJ-2 | author | minor | §6 artifact inventory stale: lists `run{1,2}` only, omits `final{3,4}.{measurements,stderr,stdout}`, `stability-r82-final34.txt`, `post-state.txt`; undercounts canonical `-ffmpeg-r82` dirs. | §6 vs dir listing |
| ADJ-3 | author | minor | §6 HEAD chain `b7d80d0→2333fac→3db77b13→1abd9549` omits `9725e53` (actual order `b7d80d0→9725e53→2333fac→…`). | `git log` timestamps; baseline watcher |
| ADJ-4 | baseline | moderate | §0 "**6/8 runs green** on rc" — actual **5/8** (rc=1 in run-a `capture-r78`, run-a `module-r80`, run-b `capture-r78`; the same §0 sentence lists 5 green runs, §2 table shows 3 rc=1 rows, §4 names 3 reds). "5/8 with `failures {}`" is correct. | `runs-{a,b}/commands.log`, stdout.json |
| ADJ-5 | boundary | moderate | §IV `c2.json (25 legs)` / §2 `runs/c2/* (25)` — actual **27** legs (and 27 run dirs). Reconciliation hypothesis: 25 was the first-pass count before `nonexistent_monitor_r0/r1` were appended. | `c2.json`, `runs/c2/` |
| ADJ-6 | boundary | moderate | §IV `c6.json (16 legs)` / §6 `runs/c6/* (16)` — actual **15** legs (15 run dirs). c6x 12 ✓. | `c6.json`, `runs/c6/` |
| ADJ-7 | boundary | moderate | §0 "**30 EIO reps**" — inventory is **41** rc=251 legs (19 c2 + 22 c2x); the bounded core experiment alone is 16 quiet + 15 hog = **31**. Range claims survive: all 41 in 0.022–0.063 s; quiet 0.024–0.029; hogs 0.038–0.063. | `summary.json` roll-up |
| ADJ-8 | boundary | minor-moderate | §0/§4 "capture wav **63/63 tone windows at 0.1 s**" not re-derivable: receipts store 0.25 s windows (15/15 play, 25/25 cap per rep; probe `tone_windows(path, 0.25)`); no 0.1 s artifact in receipts or harness. Stored evidence supports "no gap ≥0.25 s", not ≥0.1 s. | `c4.json`, `r82bnd_probe.py:774,833` |
| ADJ-9 | boundary | minor | Window header "**~15:46–16:06Z**" is local (−03) mislabeled Z. Harness/manifest UTC stamps: `.state.json ts 18:50:12Z`, manifest `generated 18:59:19Z`, `c1.json` mtime 18:51:04Z → true UTC window ≈ **18:46–19:06Z**; matches baseline's r82bnd sightings 18:50:22–18:57:55Z and c4's `r79lb_7655` sighting during baseline run-a r79. | `stat`, `.state.json`, `manifest.json` |
| ADJ-10 | boundary | nit | "803 files, zero `r82bnd_*` entries" — the manifest does list `r82bnd_probe.py`; intent presumably "zero `r82bnd_*` runtime objects". Tracked set 805 incl. `manifest.json` + a tracked `__pycache__` `.pyc`. | manifest `files` list |
| ADJ-11 | author | custody note | Intermediate fixture `f9d88dcc…` bytes not preserved (sha-only chain); disclosed ci6 cleanup delta not byte-verifiable. Both shas' runs are green, which bounds but does not prove the "zero behavioral change" assertion. | `grep -rl f9d88dcc` |
| ADJ-12 | scout | custody note | Scout evidence tree untracked (0 tracked files; reports only). All 10 receipt shas re-derived from the live worktree; custody is host-only until integrated. Same pattern as r91/r96/r97 scouts. | `git ls-files corpus/live/r82-scout` = 0 |

---

## 4. Write-scope / custody notes

- Author evidence: `corpus/live/r82-author/` 49 tracked, 0 untracked (landed in
  `aa03c347`, whose `--numstat` for the fixture = **+2170/−3**, and whose three
  removed lines are exactly the mutex-sum / mode / suffix wiring rewrites —
  each prepend-only, as §1 states; 6 hunks = family block + 5 wiring sites; all
  cited line anchors 14180/14248/14279/14281/14402/14773/14903/15235/15493/
  15661/15905/15980/16180/16311/16436/16444/16735/17358/17378 land on the
  claimed constructs).
- Baseline evidence: 65 tracked; `tree/` + `/tmp/r82-baseline-work/` tar are
  out-of-tree scratch (tar sha re-verified).
- Boundary evidence: 805 tracked incl. manifest; `tmp/` and `runs/**` receipts
  are present; the disclosed first-pass c4 overwrite (harness incident §I)
  cannot be re-verified but final receipts are single-instance.
- Scout evidence: untracked (ADJ-12).
- No `pactl set-default-*` in the r82 family (only a comment mentions it); the
  unload path is `_ffpw_r82_unload_own` → `_gst_r81_unload_own(sink_name=
  FFPW_R82_NS)`; `FFPW_R82_RELINK_BOUND_S = 0.8` as reported.
- This report is the only file written by this seat; no commits, no pushes.

---

## 5. Remaining risks / blockers

1. ADJ-1 and ADJ-5/6/7 are count defects in otherwise-verdict-stable
   dossiers — if the adjudicator accepts counts as evidence, they should be
   corrected or disclosed in the round's ledger; the underlying receipts do not
   need re-running.
2. ADJ-8 asks the boundary to either publish the 0.1 s analysis artifact or
   re-scope the claim to the stored 0.25 s windows.
3. ADJ-9's 3-hour label offset must be fixed before any future cross-lane
   contention attribution uses the boundary window (contention conclusions are
   unaffected — they already reconcile under the corrected window).
4. ADJ-11/ADJ-12 are preservation gaps only; all shas they cover were
   re-derived from live bytes today.

*Seat stop. Read-only; no commits; no judgment — the canonical Rust runtime
remains the sole judge.*
