# r90 critic — the wpstate / pw-link / wp-format landing (`f50cf66a`), attacked

Seat: **CRITIC (leaf)**. Host `plazir27`, window **2026-10-16 09:55–10:00Z (06:55–07:00 local)**.
Lane repo `~/Projects/shokunin/audio-shokunin` @ **`f50cf66a`** (the artifact under review;
`git status --porcelain` shows **no modified tracked path**, zero commits). The lane has since
advanced to **`7358f13b`** (r91 / r92 / r96 landings): the r90 block is **byte-identical** there
(lines 35553–37711, sha `85f10b66…`, verified on the live tree), so every finding below attaches
to HEAD as well as to the commit under review. Namespace `r90c_*`;
`TMPDIR=~/Projects/shokunin/tmp`; every child in its own session, SIGTERM→SIGKILL bounded;
**no `pactl set-default-sink` / `set-default-source` was ever issued**.

Artifact copies (`git archive f50cf66a` under `/home`, never `/tmp`):

- `~/Projects/shokunin/r90c-tree/` — pristine landed bytes (run 1, run 2, lock probe)
- `~/Projects/shokunin/r90c-mut1/`, `~/Projects/shokunin/r90c-mut2/` — mutation probes
- `~/Projects/shokunin/r90c/evidence/` — every artifact cited below (744 K), stable copy

Landed fixture sha256 `d3119c5d88228349b54996e23978cf726d59bfc615739838177a5a5e14551154`.
The two greens declare `d9a07b14af4e605353b2b07e6fccff41ff0eb083c1d430fb58e7192b1fb276eb`
(= the author worktree file, `audio-shokunin-wt-r90`). **The landed file is not the file that
was run green** — see F1.

---

## 0. Verdict (critic seat: attack report, not a judge's ruling)

The **splice is faithful** and the **pinned cells are live** — those survived. What did not
survive is the round's *evidence*: the landed bytes carry no green of their own, they are not
deterministically green when re-run (2 of 6 landed-byte runs red on pinned laws), the block
path can report `failures: []` with zero legs measured, and the receipts the report cites as
its evidence base are (a) absent from the landing tree, (b) not attributable to a seat or a
revision, and (c) on the block path missing exactly the census/residue evidence the report
claims they carry. Fixable defects: F1–F4, F6, F7. Tradeoff the judge must weigh: F5 (the
lock), which is the already-named r95-critic C3/C4/C5 defect re-instantiated.

---

## 1. What I attacked, and what survived

| # | attack on the landing | result |
| --- | --- | --- |
| A1 | **Is the family block byte-identical to the author's worktree bytes?** | **SURVIVED.** Landed lines 35553–37711 (2159 lines) sha256 `85f10b6619f9c45bb3b535a8f389dabfae0fcd750c3d67bf3115a156774d7eaa`; worktree lines 30982–33140, **same sha**, same byte count (105571 B). |
| A2 | **Are the splices exactly the author's intent?** | **SURVIVED.** `--numstat` = `2183 3`, 6 hunks; the **only** 3 deletions are the shared lines the integrate note names (mutex `sum([...])`, `mode` chain, `suffix` chain), each replaced r90-first; dispatch block = 20 lines immediately before `if args.probe_pwprof_r89:` (38365–38384), sha256 `797be5b6dbedcaaa54775b2a88158bffcd2f1d67a8d4a1303ef607d248792c80`; `--probe-wpstate-r90` argparse row 1×; `_r90_family_lock = _wpstate_r90_family_lock()   # held to exit` 1×; all four entry defs 1×. |
| A3 | **Does the mutex actually fire?** | **SURVIVED.** `--probe-wpstate-r90 --probe-sox-r94` → **rc 2**, `error: choose one probe mode` (inside `parse_args`; no run dir, receipt or lock written). The author worktree bytes lacked this token — the integrate deviation is a real improvement. |
| A4 | **Do the pinned cells re-derive on the landed bytes?** | **SURVIVED (measured).** Run 2 (pristine, landed bytes): 4/4 entries green, 60 leg keys; the four format shas `1735b4739ef7 / 91f7342230f7 / 5a828addfad7 / e718690a7ce2`; 25-row settings lattice, histogram `{Boolean 17, Float 5, Integer 1, String 2}`, all 25 at Default; `w_cross_volume` = `Value: 0.064`; the 622 B echo; band actuals 1.04 / 1.46 / 1.72 / 2.23 s (all inside `[0.5, 3.0]`); `key_pre` all `false` (fresh-key guard); census `sinks_gone` all `true`, `own_nodes_after []`, `own_modules_after []`. |
| A5 | **Are the pinned cells *armed* (mutation probes)?** | **SURVIVED — 6 cells, 12 leg failures, every message quoting the mutated value** (F0 below). |
| A6 | **Does the landed file keep the inherited helper semantics the green evidence assumed?** | **FAILED — one helper differs, and the family calls it** (F1). |
| A7 | **Is the family deterministically green on the landed bytes?** | **FAILED — 2 of 6 runs red on pinned laws** (F2, F7). |
| A8 | **Can `failures: []` mean "nothing measured"?** | **FAILED — yes, on two paths** (F3). |
| A9 | **Is the cited evidence the measured artifact, and is it attributable?** | **FAILED** (F4). |
| A10 | **Lock / residue** | **Mixed**: flock is real and same-tree serializing, daemon residue clean; store residue persists and the lock is tree-local (F5, F6). |

### F0 (clean) — mutation probes: the arms are live

Each mutated cell was changed **in the fixture's expectation**, then the battery re-run in its
own archive tree; every mutation reds with the *actual* value quoted, which is only possible
if the comparison is executed:

| run | mutated pinned cell | landed-code failure produced (excerpt) |
| --- | --- | --- |
| `mut1` | `WPSTATE_R90_ENUMFORMAT_SHA = "1735b4739ef7"` → `"deadbeefcafe"` | `f_rest / f_mid48 / f_44k / f_post: EnumFormat sha is 1735b4739ef7, not the boundary's deadbeefcafe` |
| `mut1` | `WPSTATE_R90_SETPARAM_ECHO_B = 622` → `621` | `f_setparam_sink: the stdout echo is 622 B, not the boundary's 621 B` |
| `mut1` | histogram `Boolean: 17` → `16` | `w_settings: type histogram drifted: {'Boolean': 17, 'Float': 5, 'Integer': 1, 'String': 2}` |
| `mut2` | `WPSTATE_R90_DEB_MAX_S = 3.0` → `0.05` | `w_create / w_props / w_pulse / w_target: … outside the coalescing band [0.5, 0.05]` (actuals 1.041 / 1.041 / 1.042 / 1.041 s) |
| `mut2` | `len(entries) != 25` → `!= 26` | `w_settings: expected the 25-entry lattice, saw 25` |
| `mut2` | `!= "Value: 0.064"` → `"Value: 0.065"` | `w_cross_volume: … reads 'Value: 0.064'` |

Mutated fixtures: `7b628a0f…` (mut1), `3529b61c…` (mut2); measurements in
`r90c/evidence/critic-mut{1,2}.measurements.json` (sha256 prefixes `bc3af0c3dd74c273`,
`0ae4f451c036dc3d`). **No dead arm was found** — this is the strongest part of the landing.

---

## 2. Findings

### F1 — the landed bytes are not the green bytes, and the drift is *inside the family's call graph* (fixable defect)

**Counterexample.** `r90-author.md` declares the implementation sha `d9a07b14…`; the landed
file is `d3119c5d…`; the worktree file is `d9a07b14…`. Two deltas exist, and the integrate
note names only one:

1. the mutex token (integrate's deliberate deviation — *benign, verified in A3*);
2. **`_pwprof_r89_stream` differs**: landed adds `preexec_fn=_pwprof_r89_sigreset` to the
   `Popen` call (introduced by `5755be5b r89 foldfix`, ancestor of HEAD, *not* in the author's
   branch base `5a632a4f`).

**Evidence.** AST-level comparison of every symbol the r90 block references: 14 foreign
helpers, **exactly one changed** (`_pwprof_r89_stream`); 33 referenced module constants
**none changed**; no symbol lost. `_wpstate_r90_stream` → `_pwprof_r89_stream` is the spawn
path of the family's **four** streaming legs — `k_w_valid` (37308), `k_w_missing` (37324),
`k_w_late` (37340), `k_m_stream` (37466). The r95-critic's A6 check (empty helper intersection) is the precedent;
here the intersection is **not** empty. The r89 foldfix exists precisely because an inherited
signal disposition changes child behaviour, and the verifier's own launcher
(`r90-verifier/runs/run_fixture.py`) resets SIGHUP/SIGINT/SIGQUIT before exec for the same
reason.

**Impacted axes:** evidence identity; integration fidelity.
**Smallest safe correction:** re-run the family on the *landed* bytes and record that run as
the round's green (the r94/r95 foldfix/verify-on-committed-bytes playbook), and have the
integrate note name the helper drift, not only the mutex token. Do not let `d9a07b14…` stand
as the landing's implementation sha.

### F2 — the pinned C12 "phantom tunnel" law is a **race**, not a law (fixable defect)

**Counterexample (live, landed bytes, three independent shapes).**

| observation | bytes | m_phantom load |
| --- | --- | --- |
| author run 2 / run 3 (08:53 / 08:56Z, loadavg 54.5 / 54.0) | worktree `d9a07b14` | rc 0, id 536870918 / 536870924 |
| r90-verifier v1 (09:55:34Z) / v2 (09:56:23Z) | **landed `d3119c5d`** | rc 0, id 536870916 / — |
| **critic run 1 (09:55:30Z)** | **landed `d3119c5d`** | **rc 1, `Failure: Unknown error code`, no id** |
| critic run 2 (09:57:26Z) | landed `d3119c5d` | rc 0, id 536870925 |
| bare seat-owned command, 3 sequential attempts | host | **rc 1, rc 1, rc 0** (the rc-0 attempt returned id 536870917 whose module row was **never held** and `unload-module 536870917` → rc 1: the phantom, exactly as documented) |

Two seats ran the same bytes in the same minute (09:55:30 vs 09:55:34) and reached **opposite
verdicts**; the bare command flips within three sequential attempts at loadavg ≈ 4 (the
author's greens were at loadavg 54–60). So the red is **not** load-correlated and not an
entry block: it is the module-load handshake racing the module's own connect failure
(`server=127.0.0.1:1` is a closed port; whether the reply or the connect error arrives first
decides rc). `m_phantom` arms **both** rc 0 *and* an id, so ~1 in 4 fixture runs reds.

Second defect on the same leg: the refusal class that actually occurs —
`Failure: Unknown error code` — is **not in `_WPSTATE_R90_ERR_CLASSES`** and is not in the
inherited r89 table, so `error_class` is `null` and the receipt cannot classify the failure it
recorded.

**Impacted axes:** claim determinism; coverage honesty (a red that is a coin-flip trains the
round to ignore reds).
**Smallest safe correction:** apply the family's *own* already-shipped pattern — the
`w_settings` retry-once-and-record-both-attempts (`legs["w_settings"]["attempts"]`) — to the
tunnel load; arm only the branch-invariant claims (rc 0 or rc 1; in **both** branches: no
node, no sink, and the id never holds *my* module row at the 8 args-aware probes); demote
"rc 0 + id" to a recorded field. Add `wpstate_unknown_refusal` for `Failure: Unknown error
code` so the class is named rather than `null`.

### F3 — the block path can report `failures: []` with **zero legs**, and its receipt is written *before* the teardown (fixable defect)

**Counterexample 1 (shape).** `_wpstate_r90_block` (36168–36183) sets `blocked`,
`coverage_blocked`, `unloads`, `failures` — never `legs`. Live sibling receipts in the
worktree ledger: `wpstate_pmod_r90_probe.20261016T090329913454Z.json` and
`wplink_r90_probe.20261016T090600183438Z.json` (pid 3178246) carry
`failures: []`, `blocked: "probe null sink … never enumerated"`, **no `legs` key**. A gate
reading `failures` (which is what the verifier's launcher prints) sees green where **0 of 15 /
0 of 24 legs were measured**. The family's own author criterion ("`coverage_blocked` empty")
is the only discriminator, and nothing enforces it.

**Counterexample 2 (my own, on the landed code).** In-process forced block (stub of
`_wpstate_r90_load_ns` → refusal) on the landed file:
`failures: []`, `blocked: "probe null sink r90a_ns_<pid> never enumerated"`, `legs` absent.

**Counterexample 3 (the sharper half).** In the same call, the **returned** dict has the
census (`sinks_gone`, `own_nodes_after`, `own_modules_after` — the `finally` did run), but the
**on-disk live receipt** does not:

```
forced-block.receipt.1.json keys:
  ['blocked','contention','coverage_blocked','failures','foreign_r90a_nodes','inventory',
   'loadavg','oracle_at_start','probe','tools','unloads']      ← no census, no legs
returned dict keys: … + ['own_modules_after','own_nodes_after','sinks_gone']
```

`return _wpstate_r90_receipt(_wpstate_r90_block(...))` evaluates (and **serializes**) the
receipt before the `finally` teardown/census runs, so the artifact the report calls its
evidence base ("every exit-signature claim … is readable there **without walking the run
dir**") systematically **omits the census and any teardown failure** on exactly the path where
residue is most likely (`module_id is None` ⇒ the load may have succeeded with its reply
lost). The run-level `measurements.json` — the file the report says you need not walk — is the
one that has it. The claim is inverted.

**Impacted axes:** coverage honesty; evidence provenance.
**Smallest safe correction:** (a) `entry["legs"] = legs` in `_wpstate_r90_block` (or in its
callers); (b) move the receipt write *after* the teardown (compute the block, let `finally`
run, then write); (c) surface a run-level count of blocked entries so a green `failures` can
never be read as "all legs measured".

### F4 — the cited receipt ledger is dead in the landing tree, and is a cross-seat, un-attributed directory (fixable defect)

**Counterexample (dead pointers).** `r90-author.md` cites
`corpus/live/r90-author/receipts/*.json`, `corpus/live/runs/2026…-wpstate-r90/` and
`corpus/live/measure_audio-wpstate-r90.lock` as the evidence base. In the landing tree all
are **ABSENT** (they exist only in `audio-shokunin-wt-r90`; the integrate note states, with
intent, that no `corpus/live/**` path was committed). Every evidence pointer in the landed
report therefore resolves to nothing in the landing.

**Counterexample (attribution).** `r90-author/receipts/` holds receipts from **5 distinct
pids**: 2962524, 2997833, 3056345, 3124855, 3178246. The report names three runs
(085112 / 085347 / 085628 = pids 2997833 / 3056345 / 3124855); the other two are **not named
anywhere in the round** — 2962524 (08:49:15Z, blocked, loadavg **69.32**) and 3178246
(09:01–09:06Z, loadavg 51.6–52.7, store receipt with **5 armed failures** and both census
readers failed). No receipt carries a seat, pid or fixture-sha field; the *file name* says
`r90-author`. `_wpstate_r90_receipt` hard-codes `ROOT/live/r90-author/receipts`, so **any**
seat's run files its receipts under the author's name — my own forced-block probe did exactly
that (`…/r90c-mut1/corpus/live/r90-author/receipts/wpstate_pmod_r90_probe.20261016T095726106065Z.json`,
written by the critic seat).

Consequence: the directory cannot answer "which bytes produced this receipt?" or "which seat
measured it?" — and it contains a run (3178246) that reds 5 store legs at loadavg 52.7 while
the author's greens at loadavg 54–60 were clean, so the family's variance in this regime is
visible but unattributable.

**Impacted axes:** evidence provenance; identity.
**Smallest safe correction:** add `seat`, `fixture_sha256` and `run_id` to every receipt and
index the file name by seat (or write under a seat-named directory); either commit the round's
green receipts or stop citing untracked paths as the evidence base — cite the run-dir
`measurements.json` paths that will exist.

### F5 — the family lock is tree-local, so it does not exclude the fleet it was written for (tradeoff; already-named r95-critic C3/C4/C5, re-instantiated)

**What survived:** the flock is real and *does* serialize runs from one tree — a second
process in the same tree blocked >8 s while run 2 held it; the lock file content is
`pid=672209 ns=r90a_ns_672209 role=r90arole672209 nonce=672209n144600` (readable, honest).

**Counterexample (live).** `_wpstate_r90_family_lock` derives the path from `ROOT`, and every
seat in this round runs from its own `git archive` tree, so there are *N* lock files. My run 1
(`r90c-tree` lock) and the r90-verifier's v1 (`r90-verifier/tree` lock) ran the family
concurrently (09:55:30–09:56:15 vs 09:55:34–09:56:18), both green-locking their own tree. The
r90-specific cost is concrete: the by-name vehicle's zero-foreign pre-check saw the
**verifier's own** loopback rows (`source=r90a_ns2_652285.monitor sink=r90a_ns_652285`) and
refused to fire — `m_byname_*` + `m_byname_final` = **5 `coverage_blocked` entries with
`failures: []`** in my run 1, i.e. 5 of 15 pmod legs silently unmeasured. Two concurrent r90
seats *cannot both* measure the by-name vehicle, and the loser is invisible to the gate.

Also inherited, unmodified: `flock(fd, LOCK_EX)` is an unbounded blocking acquire with no
`LOCK_NB` cap, no coverage block and no error class (C4); the lock file is never truncated or
unlinked, so it reads as a live holder forever (C5 — verified again here: three r90 lock files
remain in my throwaway trees after their processes exited).

**Impacted axes:** host isolation; coverage honesty.
**Smallest safe correction:** anchor the lock to a host-global, tree-independent path
(`${XDG_RUNTIME_DIR:-/run/user/$UID}/ufo-measure_audio-wpstate-r90.lock`) — the repo-convention
fix the r95-critic already asked for — plus `LOCK_NB` + bounded retry with a named
`wpstate_r90_family_lock_busy` coverage block. Do **not** patch r90 alone.

### F6 — the store residue is real and invisible to the family's own census (fixable defect, low severity)

**Counterexample.** The store-entry run writes keys into the operator's WirePlumber store and
leaves them:

- run 1: `store_at_entry {rows 7707, own_keys 0}` → `store_at_exit {rows 7725, own_keys 5}`;
  the 5 keys (`r90a_652161n144533_{c,t,v,y,z}`) were still present minutes later;
- run 2: `7753 → 7776`, `own_keys 5`;
- host-wide `r90a_` rows in `~/.local/state/wireplumber/stream-properties`: **131 → 176**
  across this window (the store file itself grew ~7 KB/run).

`own_keys` counts only keys containing *this pid's* prefix, so **no single run can see another
seat's accumulation**; `w_state_dir` arms only "`settings` must not exist" and "the dir holds
`default-nodes` + `stream-properties`", never the row count. There is no store-residue leg and
no cleanup. (The daemon side is clean: `sinks_gone` all true, `own_nodes_after []`,
`own_modules_after []`, no `r90a_` object from any of my pids at exit.)

**Impacted axes:** host residue; coverage honesty (a disclosed-but-unarmed residue).
**Smallest safe correction:** add a read-only store-residue leg: record `own_keys` at exit as
a *claim* and arm a host-wide count of `r90a_`-prefixed rows against a declared ceiling, so
accumulation is visible in every run instead of only to a critic grepping the file. Do not
edit the store from the fixture (WirePlumber rewrites it on exit).

### F7 — a second unstable pin on unmutated code: `k_w_late` (fixable defect, attribution open)

**Counterexample (live).** `mut2` — whose only mutations were three *store*/*format* cells —
red the **wplink** entry on untouched code:

```
k_w_late  argv: pw-link -w r90a_late_710014:monitor_FL r90a_lc_710014:playback_FR
          exit_code 255, wall 1.524 s, stderr "failed to link ports: Invalid argument"
          late_load rc 0 (id 536870922), late_edges [], own_links 2
```

The author's law is rc 0 at ~1.526 s with the link witnessed on the late→L3 edge. Four other
landed-byte runs (my run 1, run 2, verifier v1, v2) were green on this leg, so the rate is
low — but the arm has no class split and no retry, so a port-readiness race is reported as
claim falsification. Attribution (contention with 3 concurrent r90 runs at the time vs a
genuine readiness race) is **not** established by this evidence.

**Impacted axes:** claim determinism.
**Smallest safe correction:** same pattern as F2 — record the class, retry once inside the
bound, and arm the invariant that survives both branches (either the link exists on the
late→L3 edge, or `-w` refused with the refusal class recorded and no link formed).

---

## 3. What I could **not** test (named blockers, not silent)

- **No consecutive green ×2 on the landed bytes was produced by this seat.** My two pristine
  runs were red-then-green (F2); the sibling verifier's v1/v2 were green. I therefore claim a
  *flake rate* (2 of 6 landed-byte runs red on pinned laws), **not** "the landing is red".
- The by-name vehicle pins (`m_byname_prefix` / `_nodename` / `_unknown` / `_final`) were
  **unmeasurable in run 1** (foreign vehicle) and measured only in run 2/mut1/mut2. I did not
  mutate them: with the block live, a mutation there could be masked, and a masked red is not
  evidence.
- `k_w_late`'s EINVAL cause is not isolated (F7) — I did not run the leg in a quiet window
  with a single seat.
- I did not attempt to recover the revision that produced the 09:01–09:06 receipts; the
  attribution finding (F4) rests on the pid/sha absence, not on a recovered snapshot.
- Nothing here is a claim about `r90-boundary.md` / `r90-scout.md` arithmetic; I attacked the
  landed artifact and the receipts it cites, not the boundary's derivation.

---

## 4. Seat footprint / disclosures

- **Lane repo:** zero tracked writes, zero commits. The only file this seat adds to
  `~/Projects/shokunin/audio-shokunin` is this report (untracked).
- **Disk:** three archive trees under `/home` (`r90c-tree`, `r90c-mut1`, `r90c-mut2`, 3.2 GB
  each — they carry the archived `corpus/live/**` tracked content) plus `r90c/` scratch
  (440 K). Evidence copied to `r90c/evidence/` (744 K) so every citation above survives the
  trees being deleted.
- **Daemon objects:** only seat-owned `r90a_*` null-sink modules, loopbacks on the zero-foreign
  vehicle, and `pw-play` followers, all reaped; at exit no `r90a_` module, sink or node from
  any of my pids (652161, 668131, 672209, 710014) remained — the only live `r90a_` nodes
  belonged to sibling pid 722054.
- **Operator state:** the store-entry runs wrote 5 keys each (20 total, disclosed in F6); the
  one bare-command probe created a single tunnel module that never held a row (phantom,
  `unload` rc 1, no leftover row or sink). **No `pactl set-default-*` was issued.**
- **Locks:** three `measure_audio-wpstate-r90.lock` files remain in my throwaway trees
  (69 B each, stale holders — the C5 class).
- Sibling seats active in-window: r90-verifier (v1/v2, own tree), r90/r93/r98/r100 batteries —
  recorded here so the interference in F5 is attributed rather than assumed.

---

## 5. Return (seat card)

**Counterexamples.** (1) Landed bytes `d3119c5d` ≠ green bytes `d9a07b14`, and the one drifting
shared helper `_pwprof_r89_stream` is on the family's streaming path (F1). (2) Two seats ran
the same landed bytes in the same minute with opposite verdicts, and a bare 3-attempt probe
returned rc 1, rc 1, rc 0 — the pinned C12 law is a race (F2). (3) A blocked entry reports
`failures: []` with no legs, and its on-disk receipt omits the census its own `finally`
performed (F3). (4) The report's evidence directory is dead in the landing tree and mixes 5
un-attributed pids under the author's name (F4). (5) The family lock did not exclude two
concurrent r90 seats; the loser lost 5 legs to `coverage_blocked` with `failures: []` (F5).

**Evidence.** Landed fixture sha `d3119c5d…`; block sha `85f10b66…` (== worktree);
dispatch sha `797be5b6…`; 6 hunks, `+2183/−3`; `--probe-wpstate-r90 --probe-sox-r94` → rc 2;
6 mutated cells → 12 red legs quoting the mutated values; run-1/run-2/verifier-v1/v2
measurements (`6e75dd66094cb01b`, `4f3bdfbfe7bfc3a9`, `5c22eb58ba486b50`, `0ba794a274c9d776`)
and mut1/mut2 (`bc3af0c3dd74c273`, `0ae4f451c036dc3d`); forced-block receipts; the bare-command
probe log — all copied under `r90c/evidence/`.

**Impacted axes.** evidence identity (F1); claim determinism (F2, F7); coverage honesty
(F3, F5); evidence provenance/identity (F4); host residue (F6); integration fidelity (F1, and
*A2/A3/A5 held*).

**Smallest safe correction (one line per finding, in priority order).** Re-run the family on
the landed bytes and record that as the round's green, naming the helper drift (F1); retry-
once-and-record both attempts for the tunnel load and the `-w` late wait, arming only the
branch-invariant claims, and name `Failure: Unknown error code` (F2, F7); carry `legs` on the
block path, write the receipt after the teardown, and surface blocked-entry counts (F3); add
`seat`/`fixture_sha256` to every receipt and stop citing untracked paths as the evidence base
(F4); move the family lock to a host-global path with a bounded acquire (F5); add a read-only
store-residue leg with a declared ceiling (F6).

**Fixable defect vs tradeoff.** F1–F4, F6, F7 are fixable inside the family. F5 is a repo-wide
convention tradeoff (r86–r95 share it): the canonical judge should reject the *claim* that the
fixed corpus/live path makes cross-seat exclusion possible, and either fix the convention for
all families or accept per-tree locks and drop the exclusion claim.
