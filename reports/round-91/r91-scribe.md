# r91 scribe — custody audit of the gstfrz landing (`d78f1cc9`)

Seat: **scribe (leaf)**. Scope: report claims vs worktree receipts vs committed diff,
with three named blocks: **block byte-identity**, **3-splice shape**, **`RECEIPTS.md`
"green" label on blocked runs (critic F3)**. Host `plazir27`.
Read-only on product code; **no commits, no reruns, no lock taken, no run dir created**.
Only artifact written: this file (untracked).

Objects under audit:

| object | identity |
| --- | --- |
| landing commit | `d78f1cc9a0aa122de8fdef316034cab6eb9e2c31` — "r91 author: gst capture-freeze mechanism lattice (5 entries/15 legs, +1501/-3)" |
| landing repo | `~/Projects/shokunin/audio-shokunin`, HEAD `a2c6e3b7` at audit time |
| author worktree | `~/Projects/shokunin/audio-shokunin-wt-r91`, branch `wt-r91` @ `5a632a4f`, receipts under `corpus/live/r91-author/` + `corpus/live/runs/*-gstfrz-r91/` |
| author report (committed) | `reports/round-91/r91-author.md` sha256 `de9e9ecd5bf8914d045303df54a66533fdc10315bf8dc57877c63700d8a30bd5` |
| integrate note (committed) | `reports/round-91/r91-integrate.md` sha256 `fdaaffbbae8944a9b8cdf7b45f3708fbbc001c8e643f0e91a44e691f219438c7` |
| critic report (untracked) | `reports/round-91/r91-critic.md` (read only; source of F1–F6) |

Method: `git show d78f1cc9:<path>` (immutable blobs) + `sed`/`sha256sum` on the
landed blob and the worktree file, `python3` over the receipt JSONs. No battery was
re-executed; nothing was re-run to decorate this report.

---

## 1. Block byte-identity — **holds** (family and dispatch)

Extraction is by line range; two hash conventions exist in the record, and the
apparent disagreement between the integrate note and the critic report is a
**convention difference (trailing newline), not a content difference**. Both sides
agree under either convention:

| block | range (landed) | range (WT) | sha256 incl. trailing `\n` | sha256 stripped of trailing `\n` |
| --- | --- | --- | --- | --- |
| family (`r91:` … `    return entry` + blank) | 37712–39175 (1464 lines) | 30982–32445 | `6fe734a8ff7cd530b8790c4ada4cec6fae58216955ef3cbe7d5bc6fc0a52570d` **both sides** | `c70b7bf9cdc8980e04d1405b341ae882dd1a453a053e8b0c2d98973523a73f7a` **both sides** |
| dispatch (`if args.probe_gstfrz_r91:` … `gstfrz_connect_r91_entry()`) | 39878–39910 (33 lines) | 33045–33077 | `91bb18f8decae5beb30232ead31c03e3be917c59200705530419dde747f2e562` **both sides** | `a542d6ade995f94a79c7935dedf09a2c20c07ac83529682f5ef302f650a2d3d4` **both sides** |

- The integrate note (`r91-integrate.md`) cites the with-newline shas (`6fe734a8…`,
  `91bb18f8…`); the critic (`r91-critic.md` A1/A2) cites the stripped shas
  (`c70b7bf9…`, `a542d6ad…`). I reproduced **both** and each is self-consistent on
  both trees.
- One doc typo: the integrate note's dispatch row prints the WT range as
  `33045–33076` while labelling it "33 lines" and citing the `91bb18f8…` sha; the
  sha corresponds to `33045–33077` (33045–33076 hashes to
  `e58f216ef030921ff065568affef805f485c82ddab72e1ce2458d6979b307dd6`). The range
  text is off by one; the sha and the count are right.
- Anchor checks: landed 39174 `    return entry`, 39175 blank, 39176 `def main():`
  (family inserted immediately before `def main()`); landed 39911
  `    if args.probe_pactlmon_r85:` follows the dispatch block.
- Fixture: `corpus/fixtures/gstfreeze_r91_resume.py` sha256
  `066d6fff7ba74ef40d11b2f3a71ae336d4ee21c6d73d0975d6dc94fe714b1dc2` — identical
  landed blob and worktree file (155 lines).

## 2. Three-splice shape — **holds**

`git show --numstat d78f1cc9`: `1501 3 corpus/fixtures/measure_audio.py`,
`155 0 corpus/fixtures/gstfreeze_r91_resume.py`, `228 0 r91-author.md`,
`66 0 r91-integrate.md`. `git show d78f1cc9 -- corpus/fixtures/measure_audio.py`
carries **6 hunks**; the **only three deleted lines** are the three shared wiring
lines, each replaced by its r91-carrying twin:

| # | deleted line | replacement |
| --- | --- | --- |
| 1 | `if sum([…, args.probe_pwprof_r89, args.probe_jack_r95]) > 1:` (136 `args.probe_` tokens) | same list with `, args.probe_gstfrz_r91` appended (137 tokens) |
| 2 | `mode = "probe-wpstate-r90" if …` | `mode = "probe-gstfrz-r91" if args.probe_gstfrz_r91 else "probe-wpstate-r90" if …` |
| 3 | `suffix = "-wpstate-r90" if …` | `suffix = "-gstfrz-r91" if args.probe_gstfrz_r91 else "-wpstate-r90" if …` |

Plus the fourth (insertion-only) wiring edit: the argparse row
`parser.add_argument("--probe-gstfrz-r91", action="store_true")`. The author report's
"three splices" and the integrate note's "four shared-line wiring edits" are the
same shape counted two ways (3 replacements + 1 insertion), not a conflict.

## 3. `RECEIPTS.md` "green" label on blocked runs — **confirmed** (critic F3)

Mechanism (landed bytes, end of `main()`): `failed = {k: v["failures"] for k,v in
measurements.items() if v["failures"]}` → `return bool(failed)`; `coverage_blocked`
never reaches the exit code. A fully blocked family therefore prints `failures: {}`
and exits 0.

Reproduced from the receipts on disk (15 run dirs, each with one `measurements.json`):

| run dir | r91 entries (legs/failures/blocked) | stdout `failures` | rc | `RECEIPTS.md` label |
| --- | --- | --- | --- | --- |
| `20261016T091656945259Z` | **0/0/blocked ×5** | `{}` (rc 0; rc from `commands.log`) | 0 | **"green (843 s)"** — *"green (same bytes as attempt-2 run1)"* |
| `20261016T092456396469Z` | prop 0/0/B, clock 0/0/B, resume 0/0/B, srclos 2/0, connec 4/0 | `{}` (`dev5.stdout.json`) | 0 | **"green (440 s)"** — *"green (loader liveness + 6 s dump bound)"* |
| `20261016T093036393664Z` | 4/0, 4/0, 1/0, 2/0, 4/0 (15 legs) | `{}` (`run1.stdout.json`) | 0 | "green on the frozen bytes" |
| `20261016T093129552702Z` | 4/0, 4/0, 1/0, 2/0, 4/0 (15 legs) | `{}` (`run2.stdout.json`) | 0 | "green on the frozen bytes" |

Blocked reasons quoted verbatim from `20261016T091656945259Z`: `"probe null sink
r91a_ns_3238720 never enumerated"`, `"teardown: pactl sink reader failed —
sinks_gone unmeasured"`, `"teardown: node reader failed — own_nodes_after
unmeasured"` — in all five entries, with `legs = {}` and `failures = []`.
So the receipts table's "green" is a **rc-0 / `failures: {}` label**, and at least
two of the nine "green"-labelled rows are rc-0 runs with **zero measured legs in the
family** (one of them fully blocked). The two cited final greens *are* fully measured
(15 legs, 0 failures, 0 blocked). This matches critic F3 exactly.

## 4. Claims vs receipts vs diff — the rest

| claim (author report / RECEIPTS.md) | receipt/diff observation | status |
| --- | --- | --- |
| `+1501 / −3`, only deletions are the three splices; block = 1464 lines at WT line 30982 | diff hunks + line ranges above | holds |
| 15 canonical run dirs (every attempt) | 15 dirs `*-gstfrz-r91`; 15 start/rc/wall rows in `commands.log` | holds |
| rc/wall table (76/54/55/54/55/54/292/843/440/51/53/53/53/53/53 s) | `commands.log`; run-dir stamp = start + wall (e.g. 09:02:53+843 s → `091656945259Z`) | holds |
| impl sha `b0ab6fda…` = "final bytes, re-verified after both green runs" | WT file today = `b0ab6fda…`; `impl-shas.txt` last 3 `measure_audio` lines = `b0ab6fda…`; `frozen-shas.txt` = `b0ab6fda…`; WT file mtime 06:29 local precedes both final runs (06:29:43, 06:30:36) | holds **for the worktree**; see F1 |
| "Nothing committed. HEAD stays `5a632a4f`" | `wt-r91` HEAD `5a632a4f`; tracked modifications: `measure_audio.py` + `__pycache__/*.pyc` (disclosed) | holds |
| "Green run #1/#2 … `failures: {}`, `coverage_blocked` empty in all five entries" | both receipts: 15 legs, 0 failures, 0 blocked | holds |
| "Non-volatile cells dict-identical between the pair" | classes/values listed in the report match both runs; raw size fields differ (`resume_bytes.post` `[…,340012]` vs `[…,274476]`; `s_relink` sizes `229420→753708` vs `237612→831532`; `relink.at` 2.205 vs 2.209) | imprecise wording (critic F6) — the *classes* are identical |
| "Armed: flat while no link exists (204844)" | arm is `if len(pre) >= 2 and max(pre)-min(pre) > 8192`; window `[unl+0.35, rel−0.05]` = 0.20 s; both cited greens hold **exactly 1** harness sample in-window (t=1.603, t=1.609, size 204844); the stored `pre` is `pre[:3]+pre[-3:]` → `[204844, 204844]` (one sample printed twice) | **not substantiated by the receipts** (critic F2, arithmetic reproduced) |
| "a second acquisition is refused while the seat holds the family lock (proven live)" | landed `_gstfrz_r91_family_lock()` uses `fcntl.flock(fd, fcntl.LOCK_EX)` (blocking) at a tree-relative path `ROOT/"live"/"measure_audio-gstfrz-r91.lock"`; its own docstring says "A second `--probe-gstfrz-r91` **waits HERE**" | claim wording conflicts with the code (critic F5); same file already carries the r95 pattern (`_jack_r95_family_lock`, `LOCK_EX|LOCK_NB`, host-global path, named block) |
| attempts' rc/outcome narrative (dev1 3 defects, dev2 falsified arm, attempt-3 alignment falsification, etc.) | spot-checked: dev1 clock 10 failures + connec 5; dev2 `s_norelink` state list; attempt-3 run1 `"p_sink: the sink stream's state must stay running after the target unload — []"` and `"c_verbose: frozen payload 202796 is not 4096-aligned"` | holds |
| r91-author copies = run-dir receipts | `run1.measurements.json` = `f68edac8…` = `…093036393664Z`; `run2` = `d00b5f5a…` = `…093129552702Z`; `dev1–dev5` copies sha-match their run dirs | holds |

### Evidence identity (critic F1) — reproduced

| file | sha256 |
| --- | --- |
| landed blob `d78f1cc9:corpus/fixtures/measure_audio.py` | `7f9ee31b3b7f9269333387868a036a54beb38d633abac0a69cf839c434943cb3` |
| author worktree file (cited in `r91-author.md` / `RECEIPTS.md`) | `b0ab6fda8b35eafa76b753ce8e31687b14ec278396fbdd00c8efc2b432124af0` |
| main-repo file at HEAD `a2c6e3b7` (r92/r96/r97 landed on top) | `7a070fa817c4de6f4ae5eb5be38e7cfc2cdbb18cad605ee52427afcf0a6ca2bc` |
| main-repo worktree file (dirty, moved during this audit) | `5e4150d9…` at 07:1x → `e2e5a002a701bf5165cc04ee2f20e473148723df379b0f72058716187df18923` at 07:2x local |

`git show --name-only d78f1cc9` = 4 paths, **zero under `corpus/live/`**: the landing
carries no receipt, no run dir, no lock. The main repo has no `*gstfrz*` run dir at
all (0 matches). The cited greens live only in the worktree, and both their `resume`
receipts carry that worktree's pid (`r91a_…_3791811`). The integrate note states the
merged sha ≠ the WT sha honestly; the author report's evidence section does not say
the sha is worktree-scoped. (The critic's two landed-byte greens, `r91c/evidence/…`,
are outside my read scope.)

### Receipt archive gap (observation, no claim harmed)

Run dirs contain `measurements.json` only; `stdout.json` copies live in
`r91-author/` and are overwritten per label, so the top-level `failures` dict of the
intermediate attempts (attempt-1…attempt-4 `run1`/`run2`) is **not archived** — only
their rc/wall (`commands.log`) and their per-entry failures survive. The final pair
and dev1–dev5 stdout files are present and match their run dirs.

---

## 5. Conflicts for the canonical judge (verbatim, unresolved by this seat)

1. **Evidence identity (F1).** Author: implementation sha `b0ab6fda…` with greens in
   `corpus/live/runs/…`; landing: `7f9ee31b…` with no run dir. Both facts are true
   of different trees; the report never names the tree.
2. **F2.** Author: "Armed: flat while no link exists (204844)". Code + receipts:
   arm needs ≥2 in-window samples, both cited greens have 1, and `pre[:3]+pre[-3:]`
   prints it twice. *Verified independently here.*
3. **F3.** `RECEIPTS.md` labels `20261016T091656945259Z` (all five entries blocked,
   zero legs, `failures: {}`, rc 0) and `20261016T092456396469Z` (3/5 entries
   blocked) as "green". *Verified independently here.*
4. **F4** (connect refusal host-state-conditional, falsified in the critic's mutation
   window; author's own dev1 shows both refusal arms linked) — reported as filed by
   the critic; **not re-tested by this seat**.
5. **F5.** Lock: RECEIPTS.md "refused"; code `LOCK_EX` (waits) at a tree-relative
   path; the r95 pattern already in the same file. *Code facts verified here; the
   live-holder concurrency claim is the critic's, not re-run by this seat.*
6. **F6.** "dict-identical" overreaches; classes identical, raw fields differ.
   *Verified here.*
7. **Sha-convention noise (resolved).** Integrate-note shas vs critic shas differ
   only by a stripped trailing newline; both reproduce on both sides.

## 6. Touched surfaces

- Read: landing repo (`git show`, `git log`, `git status`, `reports/round-91/*`),
  worktree `audio-shokunin-wt-r91` (`corpus/live/r91-author/*`,
  `corpus/live/runs/*-gstfrz-r91/measurements.json`, `corpus/fixtures/measure_audio.py`,
  `reports/round-91/r91-author.md`), `reports/round-91/r91-critic.md`.
- Written: `reports/round-91/r91-scribe.md` (this file, **not staged, not committed**)
  and a scratch copy `/tmp/r91-landed.py`.
- Not written: product code, receipts, run dirs, lock file, any git ref; no battery
  re-run; no `flock` taken.

## 7. Out of scope / not audited

- The battery's own behavior on the landed bytes (critic A5/A6 mutation runs,
  `r91c-*` trees) — not re-executed here.
- F4's host-state conditionality, F5's live-holder census, the verifier report, and
  the non-r91 entries in the same receipts.
- The main worktree's dirty `measure_audio.py` (moved under me mid-audit; another
  lane's in-flight state, no attribution).

*scribe leaf — custody report, not a judge's ruling; nothing committed.*
