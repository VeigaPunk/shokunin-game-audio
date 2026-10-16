# r87 VERIFIER — wave-B gate on committed `d1e687b9` (frozen tree)

Seat: verifier (non-author). Host `plazir27` (`Linux 7.2.3-arch1-3`, 32
cores), lane `~/Projects/shokunin/audio-shokunin`, window
**2026-10-16 07:05:01Z–07:25Z**, loadavg **72–105** throughout (load
preferred; every run below ran under it). Target: commit **`d1e687b9`**
("r87 author: 4 entries pwbind lattice — routing law
target.object>flag>node.target, Props DSP witness, midi dead-target
census, pw-link events; fixed-path lock; 2 green"), frozen via
`git archive` — **not** the worktree (a sibling **r88 author** seat
edited the worktree fixture at 04:21:52 local, §8). Toolchain: PipeWire
**1.6.8**, pactl/libpulse **17.0-98-gb096**, WirePlumber 0.5.17, Python
**3.14.7**, numpy 2.5.3; all scratch under
`TMPDIR=~/Projects/shokunin/tmp`. **No tracked writes by this seat, no
commits, no pushes, no `set-default-*`; every seat artifact under
`corpus/live/r87-verifier/`.**

## 0. Verdict

**GATE FAIL — NOT VERIFIED as a reproducible green landing.** On the
frozen `d1e687b9` tree this seat's **three** replays (r87v1, r87v2,
r87v3) all exited **rc=1**, and the r87-reviewer seat's concurrent
replay (R1, read-only census) also exited rc=1: **4 of the 7 runs on
the committed bytes are red** (4 of the 5 post-commit runs), against the
author's 2 green and the reviewer's second replay (R2) green. The reds are
**not falsified laws** — they are the landing's own **two cli refusal
arms** (`create_badfac`, `create_usage`) reading a **last-500-char
window of a block-buffered pw-cli session log**, which foreign
registry-event churn pushes the refusal text out of (mechanism proven
executed, §6; confirmed statically by the labrat, §12). One further
one-off red: the `midi.pin` arm (1/7 runs, V2, under co-tenancy).

Everything else verifies: the **verdict surface is byte-identical to
both author runs** (0 exact / 0 named diffs on 105 legs × 4 entries for
v1, v3, R2; one exact diff in v2 = the one-off pin), **40 of 43
independent laws pass on all 7 receipts** (280/280), and the headline
boundary-corrected routing chain is independently re-derived by this
seat's own code (**9/9 legs**, §7). The fixed-path lock fold is verified
executed (TMPDIR-independent, exclusion real) **plus** the r86-F1
corollary is now realized in the wave: the lock is tree-relative, so
this seat's frozen-tree runs and the reviewer's frozen-tree runs were
**not serialized** (both lock files held concurrently, §3/§8).

| check | required | measured | verdict |
| --- | --- | --- | --- |
| frozen tree integrity | `git archive d1e687b9` | tar sha256 `cca0812c…`; 43 923 files / 11 690 dirs / 0 symlinks; symdiff vs `git ls-tree -r` = **0** | PASS |
| fixture identity | committed blob | sha256 `be31da679be229074690dc5157edcc122612560594baa8ba62a9b5ce26dd9516` — identical to the author's declared pin | PASS |
| py_compile / ast | clean | rc=0 inside the frozen tree | PASS |
| `normal` receipt sha | canonical pin | `8e8cdad6cc3c356d07c463498f4759b8d73e73935cf591d117732f09ffaffb1b` — byte-identical to the r85/r86 canonical normal pin | PASS |
| `--probe-pwbind-r87` replays | green | **v1 rc1, v2 rc1, v3 rc1** (105 legs each, `failures` non-empty) | **FAIL** |
| verdict-surface stability | deterministic | v1 vs A1 **0/0/1**, v2 vs A1 **1/0/4**, v3 vs A1 **0/0/3**, R2 vs A1 **0/0/3**, calibration A1 vs A2 **0/0/0** (entry diffs = failures + foreign census) | PASS (surface) |
| independent law re-derivation | armed law set | **43 laws × 7 receipts = 301; 295 PASS**; the 6 failures are exactly the two ARM_WINDOW cli laws (4 receipts) + `midi.pin` (1) | FAIL (as a gate) |
| fixed-path family lock (r84 fold) | not TMPDIR-scoped | static: `path = ROOT / "live" / …`, no env input; executed 4/4: frozen-tree lock, absent under foreign TMPDIR; blocking + release proven; **cross-materialization: two ROOTs → two locks both held simultaneously**; r85 control lands **under** the foreign TMPDIR | PASS |
| caveat rows | as declared | executed slice probe: `mdump_live` real→pass, no-node×3→`coverage_blocked`, node-no-notes→failure (fail-closed); record-only rows confirmed by static scan | PASS with F5 |
| custody/teardown | zero residue | all 7 receipts: `sinks_gone` all-true, `own_nodes_after: []`, name-verified unloads (`verified_index==captured`, no recycle); post-state **0** `r87a_*`/`r87v_*` modules/sinks/sources/nodes/processes; defaults unchanged | PASS |
| independent spots | ≥5 shapes | **routing 9/9**, pin 6/6 reps, cli-refusal 12/12 sessions, link probe, lock probe 4/4 — own code, own `r87v_<pid>` namespace | PASS |
| zero tracked writes | none | this seat wrote only under `corpus/live/r87-verifier/`; the pyc was dirty **before** the window; the worktree fixture edit is the r88 seat's | PASS (for this seat) |

## 1. Frozen tree

- `git archive d1e687b9 -o $TMPDIR/r87v-tree.tar` → sha256
  `cca0812c2ba51f9898cec526e6990881729c75b785c7fc9ae2b7682566d8d7d6`
  (1 618 001 920 B); extracted to `corpus/live/r87-verifier/tree/`
  (gitignored regenerable path per `corpus/.gitignore`
  `live/**/*tree*/`); tar deleted after extraction, sha pinned in
  `runs/tree-tar-sha.txt`.
- Census **43 923 files / 11 690 dirs / 0 symlinks**; file-set symdiff vs
  `git ls-tree -r d1e687b9 --name-only` = **0 lines**
  (`runs/tree-symdiff.txt`).
- Fixture inside the tree: sha256 `be31da67…` — unchanged after 1 normal
  + 3 probe runs. Commit shape `+2083/−3`; the author receipts are
  byte-identical to the declared pins (A1 `01f04d35…`, A2 `2970c944…`).
- `py_compile` rc=0 inside the frozen tree; `ast.parse` ok.

## 2. Battery — CWD = frozen tree root (`runs/commands.log`)

| run | window (UTC) | cmd | rc | failures | receipt sha256 |
| --- | --- | --- | --- | --- | --- |
| normal | 07:05:22→07:05:24 | `python3 corpus/fixtures/measure_audio.py` | 0 | `{}` | **`8e8cdad6…`** (canonical pin) |
| r87v1 | 07:05:26→07:07:54 | `… --probe-pwbind-r87` | **1** | `create_usage` | `3fd7d46e0836608d363fe5687dfcce3b024ff09db060c466c3a919e999a9f942` |
| r87v2 | 07:08:17→07:10:48 | `… --probe-pwbind-r87` | **1** | `create_badfac`, `create_usage`, `pin` | `1e8683f0b452364e7ce2ec47f72845334e269b22a57f4db0ac83c1860a0dd088` |
| r87v3 | 07:11:37→07:14:08 | `… --probe-pwbind-r87` | **1** | `create_badfac`, `create_usage` | `2d8ddd6dace8dfdb058509401ee6dfcffec656abfc162cbf84869ba4c85fa6fb` |

- Leg census per run: **105 legs / 4 entries** (18/33/30/24) — exact
  match to the committed count; no `coverage_blocked` in any run.
- Load at starts: 72.66 / 86.24 / 97.94 (1-min) — the replays are also
  load replays.
- v1 headline values: `regions` solo 8192 / vol25 2048 / mute 0 /
  unmute 8192; `volume_legs` v100 8192, v050 4096, v000 0, v150 12288;
  `pin` 45 B with both note-ons/offs (v1, v3); v2 `pin` 0 B (F3).
- The two failure texts are always the same class: the leg's `log_tail`
  (last 500 chars) contains only trailing registry-event text + `quit`,
  no `res:-2` / `usage: factory.name=`.

## 3. Fixed-path family lock (the r84 fold) — static + executed

**Static (committed blob).** `_pwbind_r87_family_lock` (line 25844):
`path = ROOT / "live" / "measure_audio-pwbind-r87.lock"` with
`ROOT = Path(__file__).resolve().parents[1]` (line 26). The only
`TMPDIR` mention in the helper is the docstring prose; no `tempfile`,
`os.environ`, or argument reaches the path. Acquisition site (28046):
`_r87_family_lock = _pwbind_r87_family_lock()  # held to exit` — one fd
for the whole four-entry family. Contrast: the r85 helper (22324) is
`Path(tempfile.gettempdir()) / "measure_audio-pactlmon-r85.lock"`.

**Executed (`runs/lockprobe.py`, helper extracted verbatim by anchor,
4/4 as declared; `runs/lockprobe.json`):**

1. With `TMPDIR` pointed at a fresh foreign dir, the r87 lock appears at
   `<frozen tree>/corpus/live/measure_audio-pwbind-r87.lock` with the
   witness `pid=424242 ns=r87v_ns_424242 role=r87vrole424242`, and
   **not** under the foreign TMPDIR.
2. A second exclusive attempt blocks while held (`BlockingIOError`) and
   succeeds after release — the "waits HERE" serialization is real.
3. **Cross-materialization (r86-F1 corollary, realized):** with two
   scratch ROOTs the two lock files are held **simultaneously** —
   tree-relative locks do not serialize runs from different tree
   materializations.
4. **Control:** the r85 helper's lock lands **under** the foreign TMPDIR
   and not under the tree — the TMPDIR-scoping contrast is proven.

**Lane evidence.** In-window lock witnesses: lane worktree
`pid=3585207` (07:11:10), r87-reviewer tree `pid=11633` (07:11:5x),
r87-verifier tree `pid=2476582`/`4055867` (my v2/v3), r88 seat lock
`measure_audio-btwit-r88.lock` (07:23:25). Three distinct r87 lock files
existed concurrently — §8.

## 4. Verdict-surface stability

Tiered comparator (`runs/surface.py`, r83/r86 convention, extended):
**exact** = verdict-bearing keys (exit codes/signals/killed-at-bound/
state/consumers/media_class/ports/`has_pod`/booleans + `error_class`/
`error_hit` **only where armed** — the seven modes refusal legs; the
reviewer's R1 run shows a recorded `error_class` shadowed by foreign
churn, §9-F4); **named** = law-bearing magnitudes/witnesses
(`median_peak`, `bytes`, `note_ons/offs`, ratios, `pct`); **entry** =
teardown projections + `failures`/`coverage_blocked` + the foreign-node
census; **analog** = everything else (timings, ids/serials, argv,
census). Normalization collapses pids, `r87a_/r87v_/r86a_/r85v_`
namespaces, ids, serials, `unknown global '<id>'`, tmp paths, hex.

- Calibration: **A1 vs A2 = 0 exact / 0 named / 0 entry** (137 analog
  volatile fields) — the comparator pins exactly the surface the
  author's two green runs agree on.
- **v1 vs A1: 0/0/1** — the single entry diff is the `create_usage`
  failure.
- **v3 vs A1: 0/0/3** — the two cli failures + `foreign_r87a_nodes`
  census.
- **R2 (reviewer green) vs A1: 0/0/3** — `foreign_r87a_nodes` census
  only: surface-identical to the author.
- **R1 vs A1: 0/2/4** — the two cli failures + census, plus two
  *recorded* `latency.error_class/error_hit` fields (res:-95 shadowed by
  a foreign churn `res:-2` line in the same one-shot stderr; the arm
  itself reads `res:-95` from stderr and passed).
- **v2 vs A1: 1/0/4** — the single exact diff is
  `pin.record_rc 1 → −9` (the one-off pin failure), plus the two cli
  failures + census.
- **v1 vs v3: 0/0/3** (two cli failures + census).

## 5. Independent law re-derivation (`runs/laws.py`, no fixture import)

**43 verifier-owned laws** re-derived from raw receipt data, run on all
seven receipts: **295/301 PASS** (`runs/laws-all.txt`). Coverage:
modes (binary aliasing, 7 refusal classes, last-wins directions both
ways, midi shapes, no-duplex-shape), target (9 happy legs, flag-beats-
node.target, 4 NS2 legs, 14 default-landed legs, 3 hard-no-link legs,
collision, no default drift), cli (cold registry, 5 unknowns, Props
live-DSP envelope + exact ratio, `--volume` 1.0/0.5/0.0/1.5 unclamped,
unknown-key silent drop, Format seal on stream+sink, unlinked Format
res:-2 + Props read, send-command state machine, Latency res:-95,
foreign no-gate, destroy stream/sink lifecycle, session-bound vs linger
create-node), midi (6 dead targets, 2 publish-unlinked, pin 45 B with
both on/offs, 26 B skeleton, offline dump, live-dump either-way,
pactl/pw-cli module-miss classes, 3 remote refusals, stall record,
remote census), and custody per entry.

The 6 failures are exactly:
`cli.create_usage` (v1, v2, v3, R1), `cli.create_badfac` (v2, v3, R1)
— the **ARM_WINDOW** laws, i.e. the fixture's own log-tail arms — and
`midi.pin` (v2). Every other law passes on every receipt (280/280).

## 6. Mechanism of the red — executed either-way (`runs/repro_cli_refusal.py`)

Verifier-owned held pw-cli sessions (own code, no fixture import),
12 sessions = {create_badfac, create_usage} × {no churn, churn} × 3 reps
(`runs/repro-cli.json`):

- The refusal text is printed in **12/12** sessions (the law holds).
- At the harness's sampling point (t+1.6 s) the accumulated output is
  **0 bytes in 12/12** — pw-cli's stdout is **block-buffered** when
  piped, so nothing is readable until the buffer fills or the process
  exits; the fixture only ever sees the buffer flushed at `quit`.
- The refusal is inside the **last-500-char window in only 2/12**
  sessions — exactly the two whose final logs are tiny (433/437 B) with
  **zero** registry-event lines after the refusal. Any foreign client
  connect/disconnect line (~180–330 B each) that lands after the refusal
  pushes it out (`tail_after_marker` 99 B → 114 899 B across reps).
- Deliberate churn (6 short-lived `pw-cli ls Node` clients) reproduced
  the push-out 6/6; the recorded tails are dominated by
  `remote 0 … changed / removed global … application.name = "pw-cli" |
  "blender"` lines.
- **Labrat** (read-only, static, §12) independently CONFIRMED from the
  committed source that `log_tail = _pwbind_r87_norm(log)[-500:]` is the
  **sole** arm for both legs and that no site checks the refusal against
  the full log.

So: the law is intact; the **arm is a lottery on what the final
buffer's tail contains**. Under the wave's host churn it loses roughly
half the time per leg: `create_usage` failed in 4 of 7 runs (v1, v2,
v3, R1), `create_badfac` in 3 of 7 (v2, v3, R1) — both passed in the two
author runs and in R2.

## 7. Independent spots (own code, own `r87v_<pid>` namespace)

- **Routing precedence — 9/9 PASS** (`spot/spots_routing.py`,
  `spot/routing.out.json`): own null sinks + own tone; verdict = link
  witness. `--target`→ns; **flag beats node.target**→ns; `node.target`
  alone→ns2; **`target.object` prop beats flag**→ns2; **env
  `PIPEWIRE_PROPS` beats `-P`**→ns2; `--target 0`→no links;
  `target.object=<serial>`→ns2; `--target <object.id>`→**default** (id
  never resolves); garbage `--target` **does not fall through** to
  `node.target`→default. Both sinks unloaded by name-verified index.
- **midi pin — 6/6 reps carry the events** (`runs/repro_pin.py`): own
  `pw-midirecord --target 0`, own link from
  `Midi-Bridge:Midi Through: Port-0 (capture)`, `aplaymidi -p 14:0`,
  own SMF → 46 B with 2 note-ons + 2 note-offs; link visible at +0.4 s
  in 2/2 (reader-fixed reps).
- **cli refusals — 12/12 sessions print the refusal** (§6).
- **link probe** — `pw-link` + `pw-dump` link-object shape
  (`output-node-id`/`input-node-id`) verified on a live own link.
- **lock probe — 4/4** (§3).

## 8. Custody, contention, host state

- **Custody**: every receipt (7/7) carries `sinks_gone` all-true,
  `own_nodes_after: []`, name-verified unloads; the cli entry's
  `destroy_sink_module` leg is the designed module-unload path (its
  unload record is `skipped: not_listed` by design — the author's
  receipts show the same shape). Post-state 07:24:00Z: **0**
  `r87a_*`/`r87v_*` modules, sinks, sources, nodes or processes; default
  sink `…HiFi__SPDIF__sink.29` / source `…HiFi__Line__source.29`
  unchanged.
- **Co-tenancy ledger** (read-only observation; this seat touched no
  foreign object):
  - **r87-reviewer** ran the probe **twice from its own frozen tree**
    (`corpus/live/r87-reviewer/tree/…`): R1 07:08:35→07:11:06 (red:
    both cli arms; sha `b3a316ab…`), R2 07:11:5x→07:14:42 (**green**;
    sha `2998ef71…`). My v2 overlapped R1 (its entry heads show
    `r87a_2643100_*` foreign nodes, `fixture_runs: 1`); my v3 overlapped
    R2 (heads show `r87a_11633_*`).
  - **r87-simplifier** appears in the lane lock witness
    (`pid=3585207`, 07:11:10) — a lane-worktree run.
  - **r88 author** (sibling round) edited the worktree fixture at
    04:21:52 local (+1772 lines, "BLUEZ ABSENT-CLASS + WITNESS-DIFF
    lattice") and took `corpus/live/measure_audio-btwit-r88.lock`
    (07:23:25) — the worktree is no longer the r87 tree; all my evidence
    comes from the frozen `d1e687b9` archive.
  - Ambient load 72–105 on 32 cores; a foreign `application.name =
    "blender"` client appears in the churn tails.
- **Interference by this seat**: 1 normal + 3 probe runs (frozen tree),
  12 repro pw-cli sessions (refusals only), 6 pin reps, 9 routing legs,
  1 link probe, 1 lock probe — all in `r87v_<pid>` namespace; no
  `set-default-*`, no foreign writes.

## 9. Findings (ranked)

- **F1 (blocking for the gate) — the two create-node refusal arms are
  log-tail lotteries and false-FAIL under host churn.** `log_tail` is
  the last 500 chars of a block-buffered merged session log; any
  registry-event line after the refusal evicts it (12/12 printed, 2/12
  in-window; 4 of 7 wave runs red on these two arms). The law is intact — the arm is the
  defect. Minimal repair: check the **full** log (or the already-recorded
  `errors` list / `res:-2|res:-22` regex over the full text), or
  `log_tail = norm(log)` and assert with the same substrings. Carry to
  the fold: this is the same *class* as r86-F2 (recorded race field),
  but here the field is **armed**, so it flips the verdict.
  **Cross-seat corroboration:** the committed `r87-reviewer` report
  (commit `a7d2367b`) records the same defect as its F1 ("500-char log
  window -> measured false-FAIL under load") — two independent seats,
  two independent trees, same mechanism.
- **F2 (major, structural) — cross-materialization co-tenancy is now
  realized.** The fixed path is ROOT-relative (`Path(__file__)`), so
  every frozen-tree seat locks its own file: three r87 lock files were
  held concurrently in-window (verifier tree, reviewer tree, lane), and
  no serialization happened across them (executed proof, §3.3). The
  landing's docstring says "$TMPDIR-scoped lock lets cross-TMPDIR
  same-family runs race" — the fold closed TMPDIR but not
  materialization. Impact observed: my v2/v3 and the reviewer's runs
  co-ran; the midi legs share `Midi-Bridge`/seq 14:0 and the cli arms
  share registry churn. **Cross-seat corroboration:** the committed
  `r87-reviewer` report records the same structural caveat as its F7
  (cross-ROOT not serialized, r86-F1 class).
- **F3 (minor, race) — `midi.pin` flaked once in 7 runs (v2)**: `pw-link`
  rc=0 but zero edges visible at +0.4 s and a 0-byte SMF; the same leg
  passed in 6/7 (including both author runs and both reviewer runs). My
  own pin repro passed 6/6 under the same host state, so the law holds;
  the single realization coincided with a concurrent sibling probe
  (F2). The arm is fail-closed (good), but its base rate is not 0 under
  co-tenancy.
- **F4 (observation, recorded field) — `error_class` can be captured
  from foreign churn.** R1's `latency` one-shot stderr carried two
  foreign registry errors (`no global 68`, `unknown resource 97`)
  before the real `res:-95`; `_pwbind_r87_errclass` scans in table
  order, so the recorded class became `pwcli_remote_enoent`. The
  **armed** check reads `res:-95` from stderr and passed — but any
  future arm on `error_class` for one-shot legs would be churn-flaky.
  The modes refusal legs (which *are* armed on `error_class`) did not
  bite in any of the 7 runs.
- **F5 (minor, silent-skip edge) — `mdump_live` passes vacuously if the
  Midi-Bridge/seq is absent.** `live = {"attempts": []}` is only filled
  under `if bridge and bridge.get("capture_port") and seq`; an empty
  attempts list satisfies neither branch (`live and not noted` false;
  `noted` empty) → no failure **and** no `coverage_blocked`. Executed
  either-way slice probe confirms: real→pass, 3×no-node→blocked,
  node-no-notes→failure, **[]→silent pass**. Unreachable on this host
  today (bridge present), but it is a fail-open channel.
- **F6 (corpus hygiene) — the wave is running the same family from at
  least three trees plus an r88 round on the worktree**; receipts cited
  by this report live in three different `corpus/live/*/tree/…` paths.
  A later reader must not mistake the reviewer's receipts for the
  author's (all shas listed in §11).

## 10. Risks / blockers

- **Blocker for a "green gate" reading**: F1. The committed landing's
  own arms cannot be relied on for a green/red verdict on a busy host;
  the author's "2 green" was true but not reproducible (4 of the 5
  post-commit runs red, same tree bytes).
- Carries for the wave-B fold: **F1** (arm the full log, not the tail —
  or re-derive the refusal from `errors`), **F2** (state the intended
  lock scope; if host-global serialization is wanted, resolve the lock
  from an explicit lane root), **F3** (pin arm's co-tenancy base rate),
  **F4** (don't arm one-shot `error_class`), **F5** (make the
  empty-attempts path `coverage_blocked`).
- Residual uncertainty: the author receipts' provenance is inferred from
  the identical fixture sha (`be31da67…`) plus the reproduced surface —
  the commit (07:04:24Z) is ~4 min after A2 (07:03:05Z), so the committed
  blob is the file that produced them only if it was unchanged in that
  window; the identical sha of the frozen archive and the author's
  declared pin is the strongest available check.
- Not verified here (out of scope): any r88 content now in the worktree;
  the r87 report's narrative claims beyond the armed surface (e.g. the
  exact `pw-mididump` live-flake rate) are recorded as declared.

## 11. Evidence map (`corpus/live/r87-verifier/`, 56 files / 6 128 733 B excluding the gitignored tree; `manifest.json` + `manifest.sha256`)

`runs/`: `window-start.txt`, `toolchain.txt`, `pre-state.txt`,
`post-state.txt`, `co-tenancy-pre-v3.txt`, `commands.log`,
`tracked-status-before.txt`, `tracked-status-after.txt`,
`tree-tar-sha.txt`, `tree-census` (via `tree-files.txt` + `ls-tree-…`),
`tree-symdiff.txt`, `tree-fixture-sha.txt`, `normal.stdout.json` +
`normal.receipt.json` + `normal.stderr.log`, `r87v{1,2,3}.stdout.json` +
`.stderr.log` + `.receipt.json`, `receipt-shas.txt`,
`surface.py` + `surface-{A1-vs-A2,V1-vs-A1,V2-vs-A1,V3-vs-A1,R1-vs-A1,R2-vs-A1,V1-vs-V3}.txt`,
`laws.py` + `laws-all.txt`, `lockprobe.py` + `lockprobe.json`,
`armprobe.py` + `armprobe.json`, `repro_cli_refusal.py` + `repro-cli.json`,
`repro_pin.py` + `repro-pin{,2}.out.txt`;
`spot/spots_routing.py` + `routing.out.json`;
`tree/` (gitignored `git archive` materialization holding the receipts as
written by the fixture); `labrat/` — see §12.

Receipt shas: A1 `01f04d35…`, A2 `2970c944…`, V1 `3fd7d46e…`,
V2 `1e8683f0…`, V3 `2d8ddd6d…`, R1 `b3a316ab…`, R2 `2998ef71…`
(full digests in `runs/receipt-shas.txt`).

## 12. Labrat (one read-only probe, per the probeParent card)

Dispatched once with the falsifiable hypothesis "the `create_badfac`/
`create_usage` verdicts read only the last 500 chars of the merged
session log". The labrat answered **CONFIRMED** from the frozen copy
alone: it quoted the leg body (lines 26924–26937: only `log_tail =
_pwbind_r87_norm(log)[-500:]` + `errors` are stored), `_pwbind_r87_cli_close`
(25733–25745, merged drain-thread buffer), and the verdict expressions
(27121–27131), and verified no site checks the refusal against the full
log. Its substrate exposed read/grep only — **no exec/hash tooling** —
so it reported `UNREPORTED` for the sha rather than guessing; the sha it
was asked for is `be31da679be229074690dc5157edcc122612560594baa8ba62a9b5ce26dd9516`
(verified by this seat, §1). Read-only: no files modified, no processes
spawned.
