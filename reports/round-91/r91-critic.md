# r91 critic — the gstfrz capture-freeze landing (`d78f1cc9`), attacked

Seat: **CRITIC (leaf)**. Host `plazir27`, window **2026-10-16 09:58–10:06Z (06:58–07:06 local)**.
Lane repo `~/Projects/shokunin/audio-shokunin` @ HEAD `7358f13b` (r96) at window start — a sibling
lane landed `b8ff4efc` (r97) mid-window; the artifact under review **`d78f1cc9`** is unaffected
(`git status --porcelain -uno` clean of this seat's writes, zero commits by this seat).
Namespace `r91c_*`;
`TMPDIR=~/Projects/shokunin/tmp`; every child its own session, SIGTERM→SIGKILL bounded;
**no `pactl set-default-sink` / `set-default-source` was ever issued** (defaults re-read after every
run: `…HiFi__SPDIF__sink` / `…HiFi__Line__source`, unchanged).

Artifact copies (`git archive d78f1cc9` under `/home`, never `/tmp`):

| tree | contents | purpose |
| --- | --- | --- |
| `~/Projects/shokunin/r91c-tree/` | pristine landed bytes | landed runs 1–2, splice checks, probes |
| `~/Projects/shokunin/r91c-tree2/` | landed bytes, **fresh lock inode** | concurrent landed run 2 (cross-tree lock probe) |
| `~/Projects/shokunin/r91c-mut1/`, `r91c-mut2/` | landed bytes + mutated expectations | mutation probes |
| `~/Projects/shokunin/r91c/evidence/` | every artifact cited below | stable copy (receipts, stdout, probes) |

Landed fixture sha256 **`7f9ee31b3b7f9269333387868a036a54beb38d633abac0a69cf839c434943cb3`**.
The author's cited implementation sha is **`b0ab6fda8b35eafa76b753ce8e31687b14ec278396fbdd00c8efc2b432124af0`** —
the **author worktree** file (`audio-shokunin-wt-r91`), not the landed file — see F1.

---

## 0. Verdict (critic seat: attack report, not a judge's ruling)

The **splice is faithful** (byte-identical family *and* dispatch blocks, exactly three wiring
deletions, 0 symbol collisions, mutex proven live) and the **arms are live** (7 mutated cells red
with the actual value quoted; the transitive helper closure has **zero** drift — the r90-critic F1
class does *not* recur). The landed bytes are **green twice** on this host (my runs 1–2), reproducing
every pinned cell of the author's greens.

What did not survive: the round's **evidence identity** (the cited greens are worktree-byte runs; the
landing carries no run dir at all — F1), one **claimed-armed cell that cannot fire at the canonical
timings** and whose receipt prints the single sample twice (F2), the **blocked-run-reads-as-green**
shape already realized inside the author's own receipts table (F3), the **connect "hard refusal" law
being host-state-conditional** — falsified on the landed bytes in my mutation window, and already
falsified once in the author's own dev1 (F4) — and the **family lock re-instantiating the shape r95
already superseded** (F5). F1–F4 are fixable defects; F5 is a fixable defect that is also the
already-adjudicated r90-critic F5 / r95 C3–C5 class, so the judge should weigh it as a repeat.

---

## 1. What I attacked, and what survived

| # | attack | result |
| --- | --- | --- |
| A1 | family block byte-identical to the author's worktree? | **SURVIVED.** Landed 37712–39175 = WT 30982–32445, 1464 lines, sha `c70b7bf9cdc8980e04d1405b341ae882dd1a453a053e8b0c2d98973523a73f7a` both sides. |
| A2 | dispatch block byte-identical? | **SURVIVED.** Landed 39878–39910 = WT 33045–33077, 33 lines, sha `a542d6ade995f94a79c7935dedf09a2c20c07ac83529682f5ef302f650a2d3d4`. |
| A3 | splices exactly the three shared lines? | **SURVIVED.** `--numstat` `1501 3`, 6 hunks; the only deletions are the probe-mutex `sum([…])` line, the `mode` ternary, the `suffix` ternary. Argparse row `--probe-gstfrz-r91` 1×; `--probe-gstfrz-r91 --probe-sox-r94` → **rc 2** `choose one probe mode` (no run dir, receipt or lock written); `--help` lists the flag; `py_compile` rc 0; 0 conflict markers; **51** block-defined names vs 979 outside, **0 collisions**; fixture `066d6fff…` verbatim and compiles. |
| A4 | inherited helper drift inside the family's call graph (the r90 F1 defect)? | **SURVIVED.** 19 direct foreign helpers + transitive closure of **47** module-level names: **0 AST drift, 0 missing** vs the worktree. |
| A5 | do the pinned cells re-derive on the **landed** bytes? | **SURVIVED (measured).** Run 1 `20261016T100142016632Z` and run 2 `20261016T100412393015Z`: `failures: {}`, `coverage_blocked` empty in all five entries, **15 legs** (4/4/1/2/4); `cells` dict-identical to the WT green (`true` / `"FALSE"` / absent / absent / pre `running` / `survived_running`); `frozen` identical (204844, `align_ok` true, `fed_by []`, `idle`); keepalive 0/0 (6957 B); `shapes` `freeze_idle` + `grows_running`; `remapfed` `linked_live` 573484 B; connect rc 1 / 255 / 44 B / named classes. |
| A6 | are the arms *armed* (mutation probes)? | **SURVIVED — 7 mutated cells, 11 mutation-attributable leg failures, every message quoting the mutated value** (F0 below). |
| A7 | is the resume "flat while no link" cell actually armed? | **FAILED — it cannot fire at the canonical timings** (F2). |
| A8 | can `failures: []` mean "nothing measured"? | **FAILED — yes, and the author's own table already labels such a run green** (F3). |
| A9 | is the connect "hard refusal" a law? | **FAILED — it is host-state-conditional**; falsified on the landed bytes (F4). |
| A10 | is the cited evidence the landed artifact? | **FAILED** (F1). |
| A11 | lock / residue | **Mixed**: residue clean and the census arms fire (A12, clean), but the lock is tree-local + unbounded (F5). |
| A12 | census / residue checks armed? | **SURVIVED.** Residue-present probe reds both arms; reader-failure probe names coverage; independent post-run census 0/0/0 (F0/C). |

### F0 (clean) — mutation probes: the arms are live

Each mutation changes the fixture's *expectation*; the battery is then re-run in its own archive tree.
Every red quotes the **actual** value, which is only possible if the comparison executed.

| tree (sha) | mutated expectation | landed-code failure produced (excerpt) |
| --- | --- | --- |
| `r91c-mut1` (`7371f6b9…`) | `GSTFRZ_R91_RIFF_SIZE 0x7FFF0024 → 0x7FFF0034` | `c_quiet / c_verbose / c_keepalive: frozen artifact must carry the pinned wavenc streaming placeholders — riff_size=2147418148 data_declared=2147418112` |
| `r91c-mut1` | `GSTFRZ_R91_CLOCK_LINE …"new one" → …"NEW one"` | `c_verbose: the launcher's own CLOCK_LOST handler line must appear — stdout='…Clock lost, selecting a new one\n'` |
| `r91c-mut1` | srcloss class set `"freeze_idle" → "freeze_zzz"` | `s_norelink: the post-loss shape must land in one of the two named classes — freeze_idle (sizes [229420, 229420]..[229420, 229420], states ['idle','idle','idle'])` |
| `r91c-mut2` (`d74db249…`) | `!= 44` → `!= 45` (x_rec_sink header stop) | `x_rec_sink: the artifact must stop at the 44 B header — 44` |
| `r91c-mut2` | `x_gst_sink rc != 255` → `!= 256` | `x_gst_sink: rc must be 255 — 255` |
| `r91c-mut2` | remapfed class set `"linked_live" → "live_zzz"` | `x_rec_sink_remapfed: the bounded outcome must be one of the two named classes — rc=-9 killed=wallcap` |
| `r91c-mut2` | `GSTFRZ_R91_DATA_SIZE 0x7FFF0000 → 0x7FFF0001` | same three frozen-header failures, actual `data_declared=2147418112` quoted |

Mutated fixtures `7371f6b9cdfd8dfd…` / `d74db2493f8c7df6…`; receipts
`r91c/evidence/receipts/mut1.json` (`abd73e8a…`), `mut2.json` (`b5eefd02…`). **No dead arm was found
among the cells probed** — the one dead cell (F2) was found by receipt arithmetic, not by mutation —
and this is the strongest part of the landing.

### C (clean) — census and residue

- **Arms fire on residue.** `_gstfrz_r91_teardown` with a surviving sink and a surviving own node
  (readers stubbed, no real objects touched) produces exactly
  `teardown: probe sinks survived unload: ['r91a_ns_424242']` and
  `teardown: r91a-tagged nodes survived: ['r91a_424242_leak']`, with `sinks_gone` `False` and
  `own_nodes_after` listing the leak. The census is armed.
- **Independent residue census after landed run 1** (pid 738093): `pactl` modules 0, `pw-dump`
  objects 0, processes 0; defaults unchanged. The author's own teardown census agrees
  (`sinks_gone` all true, `own_nodes_after []`, every fired unload `verified_index == captured`,
  `recycled: false`; the `not_listed` skips are the legs' own earlier gated unloads, as disclosed).

---

## 2. Findings

### F1 — the landed bytes carry no green of their own (fixable defect: evidence identity)

**Counterexample.** The report's evidence section declares the implementation sha `b0ab6fda…`
"final bytes, re-verified after both green runs" and cites the two run dirs under the **worktree**.
The landed file is `7f9ee31b…`, and `git show --name-only d78f1cc9` carries **four paths, zero under
`corpus/live/`** — so the landing tree contains no receipt, no run dir, no lock: the round's green
does not exist on the artifact under review.

**Evidence.** Landed `7f9ee31b3b7f9269333387868a036a54beb38d633abac0a69cf839c434943cb3` vs cited
`b0ab6fda8b35eafa76b753ce8e31687b14ec278396fbdd00c8efc2b432124af0` (the WT file, re-hashed here);
both cited greens (`20261016T093036393664Z`, `20261016T093129552702Z`) live in
`audio-shokunin-wt-r91/corpus/live/runs/`, and their `resume` cells carry that worktree's pid
`r91a_…_3791811`. The integrate note is honest about the merged sha — the *author* report is not.
Mitigation measured here: family + dispatch blocks byte-identical (A1/A2), 47-name closure 0 drift
(A4), and my two landed-byte runs are green (A5) — the missing green now exists, in
`r91c/evidence/receipts/landed-run{1,2}.json`.

**Impacted axes:** evidence identity; integration fidelity.
**Smallest safe correction:** cite the landed sha's own green (foldfix/verify-on-committed-bytes
playbook) and never let `b0ab6fda…` stand as the landing's implementation sha.

### F2 — the resume flatness cell is dead at the canonical timings, and its receipt doubles the single sample (fixable defect: claim-arming)

**Counterexample.** `gstfrz_resume_r91_entry` arms flatness only when the pre-link window holds
**≥2 samples**: `if len(pre) >= 2 and max(pre) - min(pre) > 8192`. The window is
`[unl_at + 0.35, rel_at - 0.05]` — **0.20 s wide** — while the leg's sample timeline is 0.2 s, so it
holds exactly **one** sample. The arm never executes; a leg that grew between the unload and the
manual link would pass.

**Evidence.** Author runs: `len(pre) == 1` in **12 of the 13 receipts that measured the resume leg**
(the 13th, `dev1`, had 3; two further runs blocked the entry), including **both cited greens**
(unl 1.201/rel 1.803 → window [1.551, 1.753], one sample at 1.603). Landed run 1 the same
(window [1.551, 1.751], one sample). Worse, the receipt field is computed
`pre[:3] + pre[-3:]`, so the single sample is **printed twice** — `"pre": [204844, 204844]` — which
reads as two measurements and is what makes the cell look armed to a reader. The report's entry-3
list claims "Armed: flat while no link exists (204844)". The app's own status file *does* record
~2.6 s of flat 204844 (37 samples) — but it is recorded, never armed.

**Impacted axes:** claim-arming; evidence identity (a receipt field that inflates n).
**Smallest safe correction:** arm on the app's own status samples (they are already in the receipt),
or require `len(pre) >= 1` and compare `at_relink == pre[0]`, and print the raw list (no `[:3]+[-3:]`).

### F3 — a blocked family reads as green, and the author's own table already labels such a run green (fixable defect: dead entry)

**Counterexample.** The block path returns `failures: []` with zero legs; `main()` prints
`failures: {}` and exits 0. A fully blocked family is indistinguishable from a measured green by the
two fields the harness emits; only `coverage_blocked`/`blocked` carry the truth.

**Evidence (landed bytes).** With `GSTFRZ_R91_RESUME_APP` pointed at a missing file, the landed
`gstfrz_resume_r91_entry()` returns `failures: []`, `legs: {}`, `coverage_blocked: ['resume fixture
… is missing']` → `main()` would print `failures: {}` and exit 0.
**Evidence (author's own receipts).** `20261016T091656945259Z` — all five r91 entries blocked
("probe null sink never enumerated", both census readers failed), **zero legs**, `failures: {}` —
is listed in `RECEIPTS.md` as **"green (843 s)"**. `20261016T092456396469Z` (labelled "green (440 s)")
has three of five entries blocked with zero legs. The cited final pair is clean, but the receipts
table's green label is not a measured-legs claim.
**Same shape at teardown:** a failed census reader yields `sinks_gone: "reader_error"` +
`coverage_blocked` and **no failure** (probe C) — an unmeasured census can ride a green entry.

**Impacted axes:** evidence identity; claim-arming; census coverage.
**Smallest safe correction:** record a per-entry measured-leg count and make a blocked family entry
non-green at the harness level (distinct mode or non-zero exit), and never label a blocked run
"green" in the receipts table.

### F4 — the connect "hard refusal" is host-state-conditional, not a law (fixable defect: determinism / premature saturation)

**Counterexample (landed bytes).** In `r91c-mut1`'s own run `20261016T100459503765Z` — whose
mutations touch the clock pin and the srcloss class set only — the **unmutated** `x_rec_sink` leg
against a sink verified bare immediately before (`targets_present_bare.sink: true`) **linked and
recorded**: `rc=-9`, **143404 B**, `error_class=None`, with `contention` 13 foreign clients and
loadavg 5.49 — instead of `rc 1` at the 44 B header. The family's own arm reds
(`x_rec_sink: rc must be 1 — -9` …), so the ledger catches it, but the round's green is then not
reproducible under co-tenancy. The same run's `s_relink` envelope broke the same way:
`other:state=suspended,tail=81920` with a **foreign lane's** node in the feeder list
(`r98a_x_crash_source`) — the two-class envelope has no class for a suspended stream under a foreign
feeder.

**Evidence (author's own).** `dev1` `20261016T084957787425Z` shows **both** refusal arms linked:
`x_rec_sink rc=-9 b=2301996`, `x_gst_sink rc=-9 cls=None`. `RECEIPTS.md` calls this "connect arms
ordered after the monitor consumer"; the reorder (refusal arms first, bare sink) did **not** close the
hole, and the connect entry has **no gate** on the `contention` census it records (the only
`contention` reference in the whole block is the entry head's). The report's own risk section
concedes "an extreme window can still produce honest contention failures" — this is that window,
observed from a second, independent seat.

**Impacted axes:** determinism; law-vs-envelope honesty; co-tenancy robustness.
**Smallest safe correction:** arm the refusal cell as the envelope it is (`refused | linked_live`,
the treatment `remapfed` already gets) with the bare-target verification and the foreign-feeder
witness recorded, or gate it on a quiet window (contention census empty) and name a coverage block
otherwise. Do not claim a hard law.

### F5 — the family lock re-instantiates the shape r95 already superseded (fixable defect: duplicate authority)

**Counterexample.** `_gstfrz_r91_family_lock()` takes `fcntl.flock(fd, LOCK_EX)` — **unbounded,
blocking** — on `ROOT/live/measure_audio-gstfrz-r91.lock`, a path that **moves with the tree**
(`ROOT = Path(__file__).resolve().parents[1]`). Same-family runs in two trees therefore do not
exclude each other. The same landed file already carries the accepted fix:
`_jack_r95_family_lock` (r95 foldfix `6ba0201c`) uses a **host-global** path, a **bounded
non-blocking** retry, a named coverage block on a live holder, stale-holder text, and
truncate-on-release.

**Evidence.** Three same-family r91 batteries live on this host at one time, each "holding the family
lock", in three distinct inodes: `24269902` (my `r91c-tree`, pid 783056), `24596328`
(`r91c-tree2`, pid 790163), `24497202` (`/home/vgpnk/r91-verify-tree`, pid 760375 — the verifier
seat's own concurrent run). A fourth (`r91a_869686`, at window end) was still live after my runs
exited. The author's claim "a second acquisition is **refused** while the seat holds the family lock
(proven live)" is inaccurate in two ways: flock *blocks* rather than refuses, and it only excludes
within one tree.

**Impacted axes:** duplicate authority; determinism (co-tenancy); contract conformance.
**Smallest safe correction:** give the r91 family the r95 pattern (host-global path + bounded
`LOCK_EX|LOCK_NB` + named block + truncate on release); if the r84 "fixed lane path" consensus is
held to win, at minimum bound the wait and name the block instead of hanging.

### F6 — minor: the "non-volatile cells dict-identical" claim is imprecise (no axis harm)

The two cited greens are *not* dict-identical outside the volatile set: `shapes.s_relink`
(fed_by pid, frozen sizes), `remapfed.fed_by`, `resume_bytes.post` and `relink.at` differ. The
**classes** are identical, which is what the claim needs; the wording overreaches.

---

## 3. Evidence index (all under `/home`)

- Trees: `~/Projects/shokunin/r91c-tree`, `r91c-tree2`, `r91c-mut1`, `r91c-mut2` (landed bytes
  `7f9ee31b…`; mutated fixtures `7371f6b9…`, `d74db249…`).
- Landed greens: `r91c-tree/corpus/live/runs/20261016T100142016632Z-gstfrz-r91/measurements.json`
  (`5a108805…`), `r91c-tree2/…/20261016T100412393015Z-gstfrz-r91/…` (`be75bd52…`) — copies in
  `r91c/evidence/receipts/landed-run{1,2}.json`.
- Mutation greens/reds: `…/20261016T100459503765Z-gstfrz-r91/…` (`abd73e8a…`),
  `…/20261016T100356024598Z-gstfrz-r91/…` (`b5eefd02…`) + `r91c/evidence/mut{1,2}.out`.
- Author artifacts read (never written): `audio-shokunin-wt-r91/corpus/live/runs/*gstfrz-r91/`,
  `…/r91-author/{RECEIPTS.md,evidence-summary.txt,frozen-shas.txt,impl-shas.txt}`.
- Hashes: landed fixture `7f9ee31b…`; family block `c70b7bf9…`; dispatch `a542d6ad…`; fixture
  `066d6fff…`; author report `de9e9ecd…`; WT file `b0ab6fda…`.

**Disclosures.** (1) My `cp -al` hard-linked the r91 lock file into `r91c-mut1/2` (inode 24269902,
link count 3), so those two mutation batteries serialized against each other; `r91c-tree2` was
rebuilt with a **fresh** lock file, which is why it ran concurrently. This is my setup artifact, not
a landing property — the cross-tree non-exclusion (F5) is proven by the three distinct inodes above,
one of them the verifier seat's. (2) My mutation trees contain hard-linked copies of earlier run
dirs; receipts were selected by the path each run printed, not by glob order. (3) Host was shared:
3–4 same-family batteries plus foreign r98/r100 lanes, loadavg 5.1–8.5 on 32 cores; contention-
attributable failures are named as such (F4) and never counted as mutation evidence.

**Not attacked.** `r76–r90` inherited families, the non-r91 entries in the same receipt, the
`on-disconnect`/`resend-last` rows (unmeasured by the author too), and the resume fixture's internals
beyond its status contract.

*critic leaf — attacked, not judged; no edits to the landing, nothing committed.*
