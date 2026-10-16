# r87 REVIEWER — wave-B gate on committed `d1e687b9`

**Seat: REVIEWER (executor-class, leaf, frozen `probeParent`).** Lane
`/home/vgpnk/Projects/shokunin/audio-shokunin`. Scope **only** the r87
pwbind landing — `git show d1e687b9 -- corpus/fixtures/measure_audio.py`
(committed blob `a712ccc6dbde3bf4de3626b1731557a67e8e04bc`, sha256
`be31da679be229074690dc5157edcc122612560594baa8ba62a9b5ce26dd9516`,
28 735 lines) plus the two committed receipts and the committed
`reports/round-87/r87-author.md`. The worktree file was **byte-identical
to the committed blob at entry** (04:05 local, sha256 `be31da67…`); at
04:18:38 a **co-tenant (the r88 author)** began its own in-flight
insertion-only landing in that file (`--probe-btwit-r88`, `+1678/-3`,
r87 family still present) — every measurement below therefore ran against
a **frozen `git archive d1e687b9` tree** (`corpus/live/r87-reviewer/tree/`,
tar
sha256 `cca0812c2ba51f9898cec526e6990881729c75b785c7fc9ae2b7682566d8d7d6`,
43 923 files / 11 690 dirs / 0 symlinks, file-set symdiff vs
`git ls-tree -r d1e687b9` = **0**) and pinned copies of the committed
blob, never the worktree fixture. **Zero tracked writes** (this seat's
only repository-path writes are `?? corpus/live/r87-reviewer/` and the
new `reports/round-87/r87-reviewer.md`); nothing
committed, nothing pushed; **no `set-default-*`, no subject-0 write, no
`pactl set-*`**; every audio object this seat created is
`r87r_<pid>`-tagged and every module it loaded was unloaded
name-verified (§6); the tracked `.pyc` dirt predates this seat
(mtime 03:55:12, seat window 04:05→04:26 local). `TMPDIR=~/Projects/shokunin/tmp`,
`PYTHONDONTWRITEBYTECODE=1`. **Load preferred: every run below ran at
loadavg 94–107** (siblings live throughout — §6.3). The two frozen-tree
replays necessarily executed the fixture's disclosed no-FOREIGN-gate
leg (an identical-value `set-param Props {volume:1.0}` on a
WirePlumber-owned sink — no other foreign object touched).

The frozen `probeParent` seat dispatched **one** `ufo-labrat`
(agent `b14bba87`) for a bounded arm-vacuity hypothesis. The child had
**no exec tooling**: it returned the empirical half as **UNTESTED** and
answered by source reading (its `m_sysex` conclusion is folded into F2,
its `skeleton` finding into F3, both re-verified by this seat in code and
receipts). The one-probe cap was respected; the empirical halves were
then executed **in-seat** (§5 S3/S7).

---

## 0. Verdict

**PASS with findings.** The r87 family is insertion-only (surgery proof:
dropping the two inserted blocks and removing the three inserted
`probe_pwbind_r87` terms from the wiring lines reproduces the parent blob
**byte-for-byte**), `py_compile` is clean, and **every armed verdict
re-derives independently from receipt data alone — 173/173 checks on both
committed receipts and on my green replay** (`r87r_audit.py`, receipts
only, no fixture import). The encoded boundary correction is armed as
data: `--target` beats `node.target` in both directions, a garbage
`--target` never falls through, `target.object`/env beat the flag,
`object.serial` resolves on both paths while `object.id` never does, and
every unresolvable string lands the *current* default. The DSP witness,
Format seal, midi dead-target + 45 B pin, rc255 remote refusal and
zero remote surface all reproduce in my own frozen-tree replays and in
eight independent spot rows (S1–S7). The sharpest finding is **load-sensitive, not
law-breaking**: the two create-node refusal arms read only the last
400/500 chars of a churn-heavy held-session log, so under load they
**false-FAIL** (fail-closed) — reproduced (r87r1: 2 entry failures) and
diagnosed (S7: the refusal is present in 6/6 realizations but 3 662–
31 797 chars from the end). One replay of two was red *only* for this
reason; the other was green with a **0-diff verdict surface** against
both committed receipts.

| check | required | measured | verdict |
| --- | --- | --- | --- |
| committed-blob pin | `d1e687b9` fixture | `a712ccc6…` / sha256 `be31da67…`, 28 735 lines; worktree byte-identical | PASS |
| diff shape | insertion-only | 2 083 added / 3 deleted; the 3 deletions are pure term insertions (surgery, each line); parent reconstruction byte-exact | PASS |
| `py_compile` | clean | rc=0 on the pinned blob | PASS |
| committed receipts ×2 | `failures: {}` | `01f04d35…`, `2970c944…`: all 4 r87 entries, no `blocked`/`coverage_blocked` | PASS |
| independent law re-derivation | armed law set | **173 checks × 3 green receipts = 519/519**; controls: dev run2 171/173 and dev run1 156/173 fail where the fixture's own receipts record failures (dev run1: 14 of 15; the delta is a pre-commit code revision) | PASS |
| verdict-surface stability | deterministic | curated 244-field surface, pid-normalized: **A-vs-B 0 diffs, A-vs-r87r2 0 diffs** | PASS |
| frozen-tree replay (load) | green | r87r2 `20261016T071442602285Z` rc=0 `failures: {}` (loadavg 95–97); r87r1 `20261016T071106495427Z` **2 failures** — F1, diagnosed false-fail | PASS-with-finding |
| routing law (boundary-corrected) | armed both directions | all 29 lattice legs re-derive; flag>node.target 2/2, garbage-flag no fall-through, prop>flag 2/2, env>prop, serial resolves / object.id never | PASS |
| Props live-DSP + Format seal | exact ratio / sealed | receipts: 8192→2048 (0.2500×)→8192→0→8192; independent spot 8485.0→2121.3 (0.2500×); Format `S16LE/48000` (stream) and `F32P/518` (sink) unchanged after valid+empty writes | PASS |
| midi dead-target + pin | uniform dead path / 45 B | 6/6 target forms rc≠0 `no target node available`+`res:-2`; pin → 45 B SMF with both 0x90 and both 0x80 payloads; skeleton 26 B | PASS |
| remote/RAOP surface | absent, one class | 0 remote/raop nodes, 0 net modules (34 native), pactl `Failure: No such entity`, pw-cli `Could not load module`, `Host is down`, `pw-cli -r` rc255 | PASS |
| fixed-path lock | NOT TMPDIR-scoped | resolved path invariant across TMPDIRs; same-ROOT cross-TMPDIR run serialized **4.78 s**; cross-ROOT not serialized (**F7**, r86-F1 class) | PASS-with-finding |
| custody/teardown | zero residue | all 4 receipts `sinks_gone` all-true, `own_nodes_after: []`; post-state 0 `r87a_`/`r87r_` modules/sinks/nodes/procs; defaults unchanged | PASS |
| independent spots | own code, own namespace | **8 spot rows (S1–S7) / 14 verdicts** all reproduce (§5), incl. the `-s` past-EOF law the fixture's arm does not exercise | PASS |
| zero tracked writes | none | this seat's only repository-path writes: untracked `corpus/live/r87-reviewer/` + the new `reports/round-87/r87-reviewer.md`; the worktree fixture's ` M` is the r88 author's in-flight landing (§6.4) | PASS |

---

## 1. Findings, ranked

### F1 (medium; fail-closed) — the two create-node refusal arms false-FAIL under registry churn

`create_badfac` and `create_usage` (`:26925-26937`) record
`log_tail = _pwbind_r87_norm(log)[-500:]` and the verdicts
(`:27121-27131`) search **only that tail** for `res:-2` /
`usage: factory.name=`. The async refusal is not an `Error: "…"` line,
so `errors` (extracted from the full log) never carries it either.
Measured: my frozen-tree replay **r87r1** ended with exactly these two
failures (`create_badfac: no async res:-2 refusal`, `create_usage: no
usage refusal`) while its 500-char tails were consumed by foreign client
churn (`application.name = "blender"`, `pw-dump` add/remove events).
The independent probe `spot/r87r_createnode_tail.py`
(`create-node-tail.json`) re-ran both commands with a **full** log
capture, 3 reps each: the refusal **is present 6/6** and sits
**3 662–31 797 chars from the end — inside the last 400 in 0/6**. So the
arm is not measuring the refusal's absence; it is measuring whether the
churn tail is shorter than the window. The same shape appears in the
author's own dev run 1 (`20261016T064958137082Z`:
`create_usage: no usage refusal (… application.name = "blender" …)`);
the committed report does not disclose the load sensitivity.
Fail-closed (a false RED, never a false green), but a wave-B re-run under
load cannot be expected to stay green. Fix: match the async refusal on
the **full** log (`res:-2.*can't create node`,
`res:-22.*usage: factory\.name=`) or record the full log.

### F2 (low-medium; arm does not measure its claim) — `m_sysex` "stays running past EOF" is not exercised

The row's only failure condition is `exit_code == 0` (`:26270-26273`),
but `_pwbind_r87_watch` SIGTERMs the subject at the last sample
(`:25806-25808`), so a SIGTERMed pw-cat yields rc=1 regardless of how it
behaved earlier; a **crash** (rc≠0) also passes, and
`exited_before_observe` is recorded but never consumed. Both samples
(0.9 s, 1.7 s) and the SIGTERM land **inside** the 4.0 s SMF fixture
(`_pwbind_r87_write_smf`: 3 840 ticks @480tpq/500 ms = 4.0 s), so no EOF
is ever reached. The underlying law is nevertheless **true**: my
independent S3 spot kept the `-s -p` node published at 0.9 / 1.7 / 3.0 /
5.0 / **9.0 s** (>4.0 s EOF; the boundary measured >10 s). So: the
author's claim survives, the arm's wording ("stays running past EOF
(armed)") overclaims. Fix: sample past the fixture's duration (≥5 s) and
arm on `exited_before_observe`/presence at that sample.

### F3 (low; latent arm looseness, not realized) — `skeleton`'s rc arm accepts the harness's own SIGKILL

`skeleton` (`:27277-27295`, verdict `:27441-27447`) requires `rc != 0`;
the harness SIGKILLs the refused midirecord at 1.2 s if it is still
alive, and a SIGKILL is `rc=-9 ≠ 0`, so a process that never refused and
simply kept running would pass the rc half. Only the 20–34 B
`MThd+MTrk+EOT` file witness (no note payloads) discriminates the
refusal. In practice all four receipts show `rc=1` (self-exit) and the
26 B skeleton, so the refusal exit path **is** exercised — latent, not
realized. (Labrat-originated, code-verified here.)

### F4 (low) — `cold_nowarm`'s id-specific check is bypassed

The verdict (`:26956-26960`) accepts **any** `unknown global` because of
the trailing `or "unknown global" in blob` clause, so a cold-registry
artifact for a *different* global would pass. The exact id did fire in
all four receipts (`204`, `135`, `126`, `217`), and the loose clause is
what makes the arm robust to the 700-char stdout preview — recorded, not
armed. Fix: assert the exact id (the preview keeps it; it is the
`stdout_head[1]` echo).

### F5 (low) — two recorded-but-unarmed preconditions

- `p_coll`'s verdict requires only `consumers == [NS]` + `playback_*`
  in-ports (`:26480-26491`); `collision_objects` is recorded but not
  armed, so the leg would pass if the colliding stream never published.
  Both committed receipts record the real collision (Audio/Sink id +
  `Stream/Output/Audio` id), so no false green was taken.
- `foreign`'s identical-value law (`:27086-27090`) is conditional on
  `volume_read is not None` (a 4 000-char pod preview parse); with a
  failed parse the leg degrades to the error-free check only. Both
  committed receipts parsed 1.0 and re-read 1.0.

### F6 (nits) — reported line ranges drift; the size/term claims are exact

`+2083/-3` matches `git diff --numstat` exactly, and the "3 edited lines
= mutex sum + mode ternary + suffix ternary" claim is exact (surgery
proves each). The report's later ranges are low: "helpers
`25619–26082`" (actual `25619–26093`), "four entry functions
`26095–27595`" (actual `26095–27504`), "dispatch `28005–28028`" (actual
`28031–28054`); the header/constant/error-class ranges
(`25452–25557`, `25559–25582`, `25585–25617`) are exact. Same nit class
as r86-F5.

### F7 (observation, r86-F1 class) — the fixed-path lock is ROOT-relative, and an unavailable lock is silent

`_pwbind_r87_family_lock` (`:25844-25861`) takes
`ROOT / "live" / "measure_audio-pwbind-r87.lock"` with `ROOT =
Path(__file__).resolve().parents[1]` — the **running checkout's** corpus
dir. Measured (executed, `runs/lock-*.json`): resolved path invariant
across two TMPDIRs for the same tree (the r84-F1 TMPDIR hole is closed;
the r85 control lock moves with TMPDIR), and a same-ROOT cross-TMPDIR
waiter **blocked 4.78 s** on a 6 s holder. Cross-ROOT (frozen-tree
co-tenancy — the wave-B convention) is **not** excluded: a tree2 waiter
acquired in **0.0001 s** while tree1 held. Also read: `OSError` →
`return None` and the dispatch (`:28046`) ignores the return value, so an
unavailable lock is a silent unlocked run (not realized — the tree's
`corpus/live/` exists; r86-F2 class).

### F8 (observation) — the lane lock files are co-tenant-shared during wave B

The lane lock `corpus/live/measure_audio-pwbind-r87.lock` was rewritten
by co-tenant probes inside this window (04:13:28, content restored to
the author's witness `pid=3585207`; the r86 lane lock shows
`pid=700077` at 04:05:22 — a co-tenant probe, not the r86 author). This
seat **never wrote either lane lock**: its locks live in its own trees
(`runs/…/tree1`, `tree2`, `tree`) with witnesses `pid=2174968/2236458`
(lock probe) and `pid=2643100` / `pid=11633` (the two replays) and mtimes
04:07:49 / 04:07:50 / 04:12:15. Recorded because the wave-B "fixed-path
lock" claim is a *shared* lane artifact and the witness it carries is
whoever wrote last.

---

## 2. Independent re-derivation of the armed verdicts (receipts only)

`r87r_audit.py` (sha256 `7bffde2c81e2f108…`) re-implements every r87 arm
from receipt data alone — no fixture import, no host — re-deriving
NS/NS2/DEF from the receipt's own argv/consumers/default fields. It
covers, per entry: the binary-identity lattice; the 7 refusal legs (rc +
class + not-killed); all 10 watch legs (presence, class, port sets,
never-duplex, `input_1`/`output_1`, sysex non-zero exit); all 29 routing
legs by link-witnessed consumers + the three hard-no-link legs +
`p_coll`'s playback-port law; the cold/warm contrast (incl. the exact
live id), the 5 unknown-global verbs, the tap validation, the DSP
envelopes (solo 0.85–1.18×8192, vol25 0.15–0.35, mute ≤128, restore,
unmute) and write rc0s, the unknown-key silent drop, the Format seal
(stream valid/empty + sink), the unlinked `res:-2` + Props-read, the
send-command state machine (7 rows), `res:-95` Latency, the no-FOREIGN-
gate rows, destroy-stream/unconnected, session/linger create-node, both
create-node refusals, destroy-sink-module, the 4 `--volume` ratios, and
the midi dead targets, publish-unlinked legs, pin payload, skeleton
window, offline/live mdump, 7 module-miss rows, 3 host-down rows and the
zero remote census.

| receipt | checks | result |
| --- | --- | --- |
| author run A `20261016T070036115509Z` | 173 | **173 pass / 0 fail** |
| author run B `20261016T070305393338Z` | 173 | **173 pass / 0 fail** |
| author dev run3 `20261016T065750423328Z` | 173 | 173 pass / 0 fail |
| reviewer replay `r87r2` | 173 | **173 pass / 0 fail** |
| *control*: author dev run2 `20261016T065456126915Z` | 173 | 171/2 — exactly the fixture's own 2 recorded failures |
| *control*: author dev run1 `20261016T064958137082Z` | 173 | 156/14 — 14 of the fixture's 15 recorded failures (the delta is `warm_control`, which the committed checker would pass on this receipt's data — a pre-commit code revision, not a data difference) |
| reviewer replay `r87r1` | 173 | 171/2 — F1's two tail-window arms |

Cross-run verdict surface (`r87r_surface2.py` + `r87r_surface_final.py`,
244 curated pid-normalized fields — consumers, classes, ports, medians,
ratios, byte counts, states, rc/class pairs):
**A-vs-B 0 diffs, A-vs-r87r2 0 diffs, B-vs-r87r2 0 diffs**;
A-vs-r87r1 = exactly 3 (the two F1 arm booleans + the entry failure
count). The four receipts' DSP numbers are identical to the digit
(solo 8192.0, vol25 2048.0, mute 0.0, restore 8192.0; volume ratios
1.0/0.5/0.0/1.5; pin 45 B; skeleton 26 B).

---

## 3. The r84 F1 fold — fixed path, verified NOT TMPDIR-scoped

- **Code**: `path = ROOT / "live" / "measure_audio-pwbind-r87.lock"`,
  `flock(LOCK_EX)`, witness `pid=<pid> ns=<ns> role=<role>`; no
  `tempfile`/`TMPDIR` input; fd held to process exit (the dispatch's
  local keeps it alive).
- **Resolved paths** (`r87r_lock_probe.py`, committed blob imported from
  two replica trees, `os.open` spied): `tree1` under `tmp1` and under
  `tmp2` → **the same** `tree1/corpus/live/measure_audio-pwbind-r87.lock`;
  the r85 control lock lands **under** the respective TMPDIR (contrast).
- **Executed serialization**: A (same ROOT, holder `tmp1`, waiter `tmp2`,
  waiter +1.5 s, holder 6 s) → waiter waited **4.7825 s** = serialized;
  B (cross-ROOT, same TMPDIR) → **0.0001 s** = not serialized (F7).
  All lock files are this seat's own; the lane lock was never touched.

---

## 4. Behavioral replays of the pinned committed blob (frozen tree, load)

Both runs: `tree/corpus/fixtures/measure_audio.py --probe-pwbind-r87`,
`TMPDIR=~/Projects/shokunin/tmp`, bounded `timeout 1800`, stderr **0 B**.

| run | window (UTC) | loadavg | result |
| --- | --- | --- | --- |
| r87r1 | 07:11:06 (receipt) | 99.8 / 77.3 / 66.9 → 105.6 | rc=0, **2 failures** (`pwbind_cli_r87_probe`: F1's two arms) |
| r87r2 | 07:14:42 (receipt) | 95.2 / 88.0 / 73.5 → 97.0 | rc=0, **`failures: {}`**, 4 entries |

r87r2 reproduces the committed landing at a **0-diff** verdict surface
(§2). r87r1 differs only in F1's two arms. Both runs' in-receipt
teardown witnesses are clean (`sinks_gone` true, `own_nodes_after: []`),
and both recorded the live co-tenants in `foreign_r87a_nodes`
(r87r1: `r87a_ns_/ns2_/…_p_three` of pid `2476582` — the r87-verifier's
own frozen-tree run; r87r2: pid `4055867`) — the family namespacing held
under a genuinely shared host.

---

## 5. Independent spots (own code, own `r87r_*` namespace)

| # | spot | measured |
| --- | --- | --- |
| S1 | routing precedence (2 own null sinks, link-witnessed) | flag>node.target 2/2; garbage flag → default (no fall-through); prop>flag 2/2; `--target <object.id 210>` → default; S1b re-run: `--target <serial 250682>` → own sink (`fixups.json`) |
| S2 | Props live-DSP through a capture-side tap | 8485.0 → **2121.3** after `{volume:0.25}` = **0.2500×** (`fixups.json`) |
| S2c | spawn `--volume` | 8485.0 → **12727.60** at `--volume 1.5` (**1.5000×**, unclamped) and **0.0** at `0.0` (`volume-spot.json`) |
| S3 | `-s -p` past EOF | node present at 0.9/1.7/3.0/**5.0**/**9.0** s against a 4.0 s fixture — the law F2's arm does not exercise |
| S4 | cold registry | piped `info <live id>` at t=0 → `unknown global '210'`; argv-mode info rc=0 with `id:` |
| S5 | remote census | 0 remote/raop/zeroconf/airplay nodes; 34 native modules, 0 net |
| S6 | create-node lifecycle | default create-node gone after `quit`; `object.linger=true` survives `quit` and dies on `pw-cli destroy` |
| S7 | create-node refusals (F1) | 6/6 realizations contain the refusal; 3 662–31 797 chars from the log end; inside the last 400 in **0/6** |

---

## 6. Custody, teardown, co-tenancy

1. **Residue** (`runs/residue-census.json`): 0 `r87r_` and 0 `r87a_`
   modules/sinks/nodes, 0 seat processes; default sink
   `…HiFi__SPDIF__sink.29` and default source `…Line__source.29`
   unchanged; scoped `git status` = `?? corpus/live/r87-reviewer/` only.
2. **Seat-side disclosure**: the spot harness's own `run()` helper
   truncates subprocess stdout to 200–800 chars, so its
   `pactl list modules short` verification (a 2.4 kB, 43-line table)
   never saw its own `sink_name=` row and four `r87r_` modules survived
   the first cleanup pass. Caught by this seat's full census and all four
   unloaded **name-verified** (index re-read, arg must carry
   `sink_name=r87r_<own name>`) — `runs/spot-cleanup.json`. No effect on
   the landing; recorded because it is the same "truncated reader read as
   clean" class as F1.
3. **Co-tenancy** (in-receipt + external): r87-verifier frozen-tree runs
   (pid `2476582`, and `4055867`) live during both replays; r87-critic /
   r87-simplifier / r87-scribe seat dirs active 04:04–04:13; the lane
   lock witness rewritten by co-tenant probes at 04:05:22 (r86) and
   04:13:28 (r87, restored author witness) — never by this seat (F8).
4. **Foreign worktree write (not this seat)**: at 04:18:38 the **r88
   author** began its own insertion-only landing in
   `corpus/fixtures/measure_audio.py` (`--probe-btwit-r88`, `+1678/-3`,
   sha256 moving `45765fdd…` → `06334c5e…` while observed; the committed
   r87 family still present, 224 `pwbind_r87` hits) —
   `runs/worktree-state.json`. This seat wrote **no** tracked bytes: its
   only repository-path writes are the untracked receipts dir and the new
   `reports/round-87/r87-reviewer.md`; the r87 verdicts are unaffected
   because the fixture was never imported or executed from the worktree.

---

## 7. Evidence index

- `corpus/live/r87-reviewer/r87r_pin.py`, `runs/pin.json`
  (`cd03ffca…`), `runs/measure_audio_d1e687b9.py` (pinned blob)
- `runs/r87r-tree.tar` (sha256 `cca0812c…`) → `tree/` (symdiff 0);
  `tree/corpus/live/runs/20261016T071106495427Z-pwbind-r87/`,
  `…20261016T071442602285Z-pwbind-r87/` (frozen-tree receipts)
- `runs/r87r1-live.json` (`b3a316ab…`), `runs/r87r2-live.json`
  (`2998ef71…`), `runs/live-run*.stdout|stderr`
- `r87r_audit.py` (`7bffde2c…`), `runs/audit.json` (`6d02ff10…`),
  `runs/audit-live.json` (`2d801462…`)
- `r87r_surface.py`, `r87r_surface2.py`, `r87r_surface_final.py`,
  `runs/vsurface-summary.json` (`8d51bd5c…`) + per-pair receipts
- `r87r_lock_probe.py`, `r87r_lock_experiments.sh`,
  `runs/lock-resolve-*.json`, `runs/lock-waitA.json` (`da38ef79…`),
  `runs/lock-waitB.json` (`bc05320e…`)
- `spot/r87r_spots.py` + `spot/spots.json` (`6ca86949…`),
  `spot/r87r_fixups.py` + `spot/fixups.json` (`80d69adf…`),
  `spot/r87r_volume_spot.py` + `spot/volume-spot.json` (`74c0c747…`),
  `spot/r87r_createnode_tail.py` + `spot/create-node-tail.json`
  (`841fa07c…`)
- `runs/residue-census.json` (`a9eec14e…`),
  `runs/spot-cleanup.json` (`b97982e2…`), `runs/worktree-state.json`,
  `manifest.json`
- Labrat: agent `b14bba87`, no exec tooling, static-only return
  (folded into F2/F3; no files created).

*reviewer leaf — measured, not judged; the canonical Rust runtime is the
judge.*
