# r95 foldverify — the foldfix landing re-verified on COMMITTED bytes (HEAD `6ba0201c`)

Seat: **foldverify** (leaf, `probeParent`). Lane repo `~/Projects/shokunin/audio-shokunin`.
Basis: **committed bytes only** — `git archive HEAD` of `6ba0201c076355bc01123d7c9dce1256bdf89984`
("r95 foldfix: honest blocks, exit census, host-global bounded lock (+773/-263)").
Window **2026-10-16 09:45–09:53Z** (06:45–06:53 local), host `plazir27`, loadavg 8–12 with
concurrent sibling batteries (`--probe-wppol-r97`, `--probe-sofa-r100`, `--probe-filterchain-r92`,
`--probe-pwstream-r98` all live in `ps` during the runs). **Zero commits, zero pushes, no
`set-default-*`, no daemon restart, no tracked file modified.** One file created (untracked):
`reports/round-95/r95-foldverify.md`.

## 0. Verdict table

| assigned claim | verdict | evidence |
| --- | --- | --- |
| `failures {}` with `coverage_blocked` empty **or named** | **CONFIRMED** | §3 green: `failures {}` ×2, `coverage_blocked` absent on 5/5 entries; §4 negative: named on 5/5 in both blocked batteries |
| `legs_measured > 0` per entry | **CONFIRMED** (green path) | 3/4/2/10/5 = **24 legs**, `measured: true` ×5, both runs (§3) |
| legs preserved on **every** exit path | **CONFIRMED** | green 24 legs; gate-block and lock-block carry `legs` (key present, `legs_measured 0`); abort path carries its 3 built legs; static check **26/26** call sites pass legs (§5) |
| exit census on abort paths | **CONFIRMED** | synthetic mid-entry abort → `entry aborted: …` named **and** full census (`sinks_gone`, `sinks_censused`, `own_nodes_after`, `stream_properties_own_rows`, `unloads`) (§5) |
| lock at `$XDG_RUNTIME_DIR/ufo-measure_audio-jack-r95.lock`, bounded/nonblocking | **CONFIRMED**, one caveat | live holder → refused at **2.001 s** (cap 2.0) with the named block; dispatch-level cap 2 s → whole battery 3.065 s with 5 lock-blocked entries; tree-independent (probe run from `/home/vgpnk`); stale dead-pid text recorded + displaced; 0 bytes after release. **Caveat R1**: a refused waiter truncates the live holder's text (§5, §6) |
| daemon-down negative probe yields **named blocks, not green-on-nothing** | **CONFIRMED at receipt level** | 5/5 `measured: false`, `legs_measured: 0`, `jack_r95_daemon_unresponsive: … rc=1 … 'Connection failure: Connection refused'`, `failures: []`, census keys present (§4) |
| runner stdout **no longer prints green when everything is blocked** | **NOT CONFIRMED — not landed** | the summary print is byte-identical pre-fold (`6fcff792`) and at HEAD; a fully blocked run prints `{"receipt": …, "failures": {}}` with **rc 0** (§4.3, §6 R2) |

The fold's *receipt-level* honesty is real and measured. The one assignment item that is not
true on committed bytes is the **stdout summary line**; the foldfix report itself never claimed
a stdout change (its "a blocked run can no longer read as green" claim is receipt-level, and
that claim holds). Details in §6.

## 1. Bytes, tree discipline, method

- **Archive**: `git archive HEAD | tar -x -C /home/vgpnk/r95-foldverify-archive` (fresh dir under
  `/home`, never `/tmp` — tmpfs quota exhausted). HEAD verified as `6ba0201c…` by
  `git rev-parse HEAD` in the lane repo.
- **Byte pins** (archive, after extraction):
  `corpus/fixtures/measure_audio.py` = `740d9ce39f589e781792e552976713b25c085e460a072b88417c546d50040e87`
  (matches the foldfix report's declared implementation sha),
  `corpus/fixtures/r95jack.c` = `55d4d4111bd8d46be743d0425a40dc8d938d15e071ce37f460db70de0df997be`
  (matches the reviewer's declared fixture sha). The lane worktree's tracked bytes are identical
  to HEAD (`git diff --stat HEAD -- corpus/fixtures/measure_audio.py corpus/fixtures/r95jack.c`
  empty; worktree sha `740d9ce3…`), so the archive is the committed state, not a dirty tree.
- **Fixture build (committed `r95jack.c`, host gcc 16.2.1)**:
  `gcc -O1 -w -o corpus/live/r95-foldverify/build/r95jack corpus/fixtures/r95jack.c -ljack -lm`
  → rc 0, ELF 64-bit PIE, binary sha `016a685372e6d8fab9dbd54bdb28b97e948688c2d990bf896feaf26bf9fd7ecf`;
  the per-entry in-run build recorded `build.src_sha256 55d4d411…`, `build.rc 0`,
  `build.binary_sha256 016a685372e6d8fa…` — the committed source and the run's own build agree.
- **Daemon precondition**: `pactl info` answered in **4–5 ms** (`Server Name: PulseAudio (on
  PipeWire 1.6.8)`, `<15 s` gate passed) before every run; re-checked before run 2.
- **Run hygiene**: every run under `TMPDIR=/home/vgpnk/r95-foldverify-scratch/tmp` (never `/tmp`),
  `PYTHONDONTWRITEBYTECODE=1`, `timeout 600`, and with **no other `--probe-jack-r95` process
  alive** (`ps` checked).
- **Seat method disclosure**: this seat's tool surface exposes no `lsp` device; no symbol-aware
  edit was needed (the assignment is read-only verification — **no repository file was edited**,
  so the cross-file-rename hazard does not arise). One `probeParent` child was spawned (bounded
  depth-2 `labrat`, advisory): its seat had **no command-execution tool**, so it could not run the
  battery and returned a static cross-check instead — reported verbatim in §7, never treated as
  measurement.

## 2. Exact commands

```bash
# archive (committed bytes)
cd /home/vgpnk/Projects/shokunin/audio-shokunin
git archive HEAD | tar -x -C /home/vgpnk/r95-foldverify-archive
sha256sum /home/vgpnk/r95-foldverify-archive/corpus/fixtures/measure_audio.py   # 740d9ce3…

# fixture build
cd /home/vgpnk/r95-foldverify-archive
gcc -O1 -w -o corpus/live/r95-foldverify/build/r95jack corpus/fixtures/r95jack.c -ljack -lm

# green runs (twice)
export TMPDIR=/home/vgpnk/r95-foldverify-scratch/tmp PYTHONDONTWRITEBYTECODE=1
cd /home/vgpnk/r95-foldverify-archive && timeout 600 python3 corpus/fixtures/measure_audio.py --probe-jack-r95

# daemon-down negative (dead socket, no host change)
PULSE_SERVER=unix:/home/vgpnk/r95-foldverify-scratch/dead-daemon.sock \
  timeout 600 python3 corpus/fixtures/measure_audio.py --probe-jack-r95

# lock-busy negative: live `flock` holder + helper probe (cap 2 s) and the real dispatch
# with only the wait cap patched (2 s) — see /home/vgpnk/r95-foldverify-scratch/lock_battery.py

# abort-path probe: patch _jack_r95_finish to raise, call jack_surface_r95_entry() —
# see /home/vgpnk/r95-foldverify-scratch/abort_probe.py
```

## 3. Green path — two runs on the archived committed bytes

| run | receipt | rc | stdout `failures` | wall | receipt sha256 |
| --- | --- | --- | --- | --- | --- |
| run 1 | `corpus/live/runs/20261016T094610051344Z-jack-r95/measurements.json` | **0** | `{}` | 38.828 s | `f046857f67aefaedf2359ccca50687081331a65820a4dd9b811b298ac5bcaab0` |
| run 2 | `corpus/live/runs/20261016T094828113982Z-jack-r95/measurements.json` | **0** | `{}` | 38.745 s | `4a65961ae479fa6449337a4b08e8f3d1465e1569b0666931344d2f1f0a0b2dfb` |

23 measurement entries (22 + the new `jack_r95_family_lock` record); **24 r95 legs** across the
five entries, identical shape in both runs:

| entry | legs | `measured` | `legs_measured` | `coverage_blocked` | `daemon_gate.ok` | `sinks_gone` | `sinks_censused` |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `jack_surface_r95_probe` | 3 | true | 3 | absent | true (0.012 s) | `{r95a_ns_<pid>: true}` | 1 name |
| `jack_addr_r95_probe` | 4 | true | 4 | absent | true | 2 names true | 2 names |
| `jack_bytes_r95_probe` | 2 | true | 2 | absent | true | `{r95a_ns_<pid>: true}` | 1 name |
| `jack_quantum_r95_probe` | 10 | true | 10 | absent | true | `{r95a_ns_<pid>: true}` | 1 name |
| `jack_defects_r95_probe` | 5 | true | 5 | absent | true | `{r95a_ns_<pid>: true}` | 1 name |

Everything else the green must show, both runs:

- **lock record** — `path=/run/user/1000/ufo-measure_audio-jack-r95.lock`, `acquired: true`,
  `waited_s: 0.0`, `holder_text: null`, `stale_text: null`, `block: null`, `coverage_blocked: []`.
- **F1 subject-keyed metadata** — `d_metadata.own_subjects` `[167, 187]` (run 1) / `[117, 171]`
  (run 2, pid-bearing), `get_after_remove_branch: refreshed`, `foreign_r95a_rows_while_running: {}`,
  `rows_after_exit: {}`, `rows_after_exit_subject_keyed: {}`.
- **F5 settings restore** — `settings_restore.exit_code 0`, `settings_after_restore.clock.force-quantum
  "0"`, `settings_moved []`, `settings_final.clock.force-quantum "0"` in both runs.
- **byte witnesses** — `b_jack2pw` capture ratio **0.954104 / 0.953400** (band 0.90–1.03),
  `b_pw2jack` ratio **0.999981214 / 0.999981214** (band 0.985–1.005), `in_peak 0.499969482`
  (= int16 peak / 32768) in both.
- **census** — `own_nodes_after: []`, `stream_properties_own_rows: []`, `unloads` every
  `exit_code 0`, `ns_gone_after_unload: true` where the sink is unloaded mid-entry; `sinks_gone`
  non-vacuous in **5/5** (the F7 fix holds).
- **driver** — `s_shape.driver_name: Dummy-Driver` in both runs (no foreign-driver confound fired).

**Cross-run agreement.** After pid/tmp normalization, run 1 and run 2 agree on every discriminator
(`measured`, `legs_measured`, `coverage_blocked`, `failures`, `daemon_gate.ok`, `sinks_gone`
truth-values, `sinks_censused` shape, `settings_*`, lock record). The residual leaf differences are
confined to declared-volatile families: registry ids/serials/pids, wall clocks, cycle counters,
`cpu_load`, the known-garbage `rt_prio`/`max_rt_prio`, foreign-graph census rows (sibling lanes'
`r92a`/`r98a` nodes appear in `s_shape.json.census.first40`), temp paths in `argv`, and the
`b_jack2pw` capture window (`sha256`, `frames`, `nonzero`). No armed law cell differs.

## 4. Negative probes

### 4.1 Daemon down (`PULSE_SERVER` → dead socket; no host change)

Receipt `corpus/live/runs/20261016T094623105128Z-jack-r95/measurements.json` (sha
`a71c3b7bf8f43e0b906234961980e87c55d796fc2e3450f4da1573a809cc7484`), wall **1.575 s**:

- **5/5 entries** `measured: false`, `legs_measured: 0`, `legs: {}` (key present),
  `coverage_blocked: ["jack_r95_daemon_unresponsive: bounded `pactl info` did not answer
  (rc=1 killed_at_bound=False wall_s=0.011 stderr='Connection failure: Connection refused\npa_context_connect() failed: Connection refused') — the shared daemon is not measuring; no r95 leg is armed"]`,
  `failures: []`, and the census keys present (`sinks_gone: {}`, `sinks_censused: []`,
  `own_nodes_after: []`, `stream_properties_own_rows: []`).
- No leg was armed before the gate, so `legs_measured 0` is the honest reading, and
  `measured: false` makes "green-on-nothing" impossible **at receipt level**.
- The lock entry still shows `acquired: true` (the lock is daemon-independent).

### 4.2 Family lock busy (live holder; bounded)

Holder: `flock -x /run/user/1000/ufo-measure_audio-jack-r95.lock -c 'sleep …'` with advisory text
`pid=414438 ns=foldverify role=holder`; a second `flock -n` from a fresh process confirms the
holder is live.

- **Helper probe, run from `/home/vgpnk` (a different cwd — tree independence)**:
  `waited_s: 2.001` with `wait_cap_s: 2.0`, `acquired: false`,
  `block: "jack_r95_family_lock_busy: /run/user/1000/ufo-measure_audio-jack-r95.lock held for 2.0s
  > cap 2.0s — a same-family run is live (holder text 'pid=414438 ns=foldverify role=holder'); …"`.
  Bounded refusal, holder text quoted, no unbounded wait.
- **Dispatch-level** (`/home/vgpnk/r95-foldverify-scratch/lock_battery.py`: the real
  `--probe-jack-r95` dispatch with only the wait cap patched to 2 s): receipt
  `corpus/live/runs/20261016T094700690854Z-jack-r95/measurements.json` (sha `e892f030…`), whole
  battery **3.065 s**, **5/5 entries** `_jack_r95_lock_blocked_entry`s — `measured: false`,
  `legs_measured: 0`, `legs: {}`, the named `jack_r95_family_lock_busy` block, `failures: []`.
- **Stale handling**: text with a dead pid (`pid=999999 …`) was recorded as `stale_text` and the
  lock was acquired (waited 0.0 s); after `_jack_r95_lock_release` the file is **0 bytes**.
- **Caveat R1 (measured, new)**: a *refused waiter* truncates the live holder's advisory text —
  holder text 43 B → **0 B** while the flock is still held (`flock -n` still refused). The first
  waiter's own record captured the text (`holder_text` correct), but any later waiter records
  `holder_text: ''` (visible in the dispatch-level receipt above). Exclusion is unaffected (the
  flock, not the text, is the witness); the *evidence* is destroyed. `_jack_r95_lock_release` is
  the holder's release path and should not be used on the busy path — close the fd without
  `ftruncate` there.

### 4.3 The stdout summary line — the one unlanded claim

- The summary statement is **byte-identical** at the pre-fold basis (`6fcff792`) and at HEAD:
  `failed = {k: v["failures"] for k,v in measurements.items() if v["failures"]}` →
  `print(json.dumps({"receipt": str(out / "measurements.json"), "failures": failed}))` →
  `return bool(failed)`. Both revisions carry exactly one such print line (grep count 1/1); the
  foldfix diff touches neither line.
- Measured on a **fully blocked** battery (all five r95 entries blocked, **0 legs measured**):
  stdout = `{"receipt": "/home/vgpnk/r95-foldverify-archive/corpus/live/runs/20261016T094623105128Z-jack-r95/measurements.json", "failures": {}}`,
  **rc 0**. The lock-busy battery prints the same shape, **rc 0**.
- Root cause: blocks append to `coverage_blocked`, never to `failures` (by design), and `failed`
  reads only `failures`. The receipt is honest; the console line is not.
- The assignment's item 7 is therefore **not satisfied on committed bytes**. Minimal fix (not
  applied — out of this seat's scope): carry the blocked count in the summary, e.g.
  `"blocked": {k: v["coverage_blocked"] for k,v in measurements.items() if v.get("coverage_blocked")}`,
  and/or return non-zero when every entry is unmeasured.

## 5. Exit-path matrix (legs + census)

| exit path | how induced | `measured` | legs | `coverage_blocked` | census produced |
| --- | --- | --- | --- | --- | --- |
| green | run 1 / run 2 | true | **24** (3/4/2/10/5) | absent | yes, non-vacuous |
| daemon gate block | dead `PULSE_SERVER` | false | `{}` (key present, 0) | named ×5 | keys present (`{}` census, nothing loaded) |
| lock block | live holder, cap 2 s | false | `{}` (key present, 0) | named ×5 | keys absent (entry never ran) |
| **abort** | patch `_jack_r95_finish` to raise inside the real entry | **false** | **3 preserved** (`a_avail`, `s_liveness`, `s_shape`) | `entry aborted: RuntimeError: foldverify synthetic abort (patched _jack_r95_finish)` | **yes, non-vacuous**: `sinks_gone {r95a_ns_440194: true}`, `sinks_censused [r95a_ns_440194]`, `own_nodes_after []`, `stream_properties_own_rows []`, `unloads.exit_code 0` |

Static companion check (`/home/vgpnk/r95-foldverify-scratch/legs_callsites.py`, AST over the
committed bytes): **26/26** `_jack_r95_block` / `_jack_r95_finish` call sites pass `legs`
(keyword or positional); `without-legs = 0`. The verifier's F4/F2 complaint (legs dropped on the
early-block path) is closed.

## 6. Findings and remaining risks (mine)

1. **R2 — the stdout summary still reads green on a fully blocked run** (§4.3). This is the
   assignment item that is not landed. Receipt-level honesty is unaffected.
2. **R1 — a refused waiter truncates the live holder's advisory text** (§4.2). Observed twice
   (helper probe and dispatch-level battery). Safe direction for stale-reads, but it destroys the
   holder evidence for every later reader. Fix: close without `ftruncate` on the busy path.
3. **`measured: true` means "the entry ran to the end"**, not "every arm was measured": a named
   confound can coexist with `measured: true` (inherited from the foldfix report §7.4). Gates must
   read `coverage_blocked` as well. Confirmed by construction here: the negative batteries show
   `measured: false` + named blocks, and the green shows `coverage_blocked` absent — the two
   discriminators are independent.
4. **`b_pw2jack` ±1 % energy band is a latent flake** (inherited, not re-tested to failure): both
   of my runs landed `0.999981214`, and the verifier's own flake (0.9103) came from a late
   `pw-play` link. Not fixed by the fold.
5. **The `d_metadata` post-removal pair correction is out-of-union** (disclosed by the foldfix
   seat). It is present in the committed bytes; without it the family reds on a quiet host.
6. **Except-path census is conservative**: `_jack_r95_block` censuses the entry's own sink name
   even when the abort/block happened before the load, so `sinks_gone` can claim "gone" for a sink
   that was never created (inherited; safe direction, not a load witness). The daemon-down receipt
   shows `sinks_gone {}` for the gate block, i.e. the empty-census note path.
7. **Host contention**: the runs shared the daemon with sibling batteries (`r92/r97/r98/r100`);
   the foreign-graph census rows differ run-to-run, but no armed cell did (driver stayed
   `Dummy-Driver`). The lock-busy dispatch-level probe used a patched 2 s cap (disclosed) — the
   committed default cap is 600 s, so a real busy lock would make a run wait up to 10 min before
   naming the block; the *boundedness* property is what was verified, not the 600 s constant.
8. **Hygiene after all runs** (measured with no r95 process alive): `pactl list short modules |
   grep -c r95a` = 0, sinks = 0, `pw-dump` r95a nodes = 0, `stream-properties` r95a rows = 0,
   `pw-metadata -n default` r95a rows = 0, `clock.force-quantum = "0"`,
   lock file **0 bytes**, no `--probe-jack-r95` process, default sink/source unchanged
   (`alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink` /
   `alsa_input.usb-Generic_USB_Audio-00.HiFi__Line__source`).

## 7. probeParent child (bounded depth-2 `labrat`, advisory)

One child was spawned, read-only, with one falsifiable hypothesis (the stdout green-on-blocked
claim of §4.3). **Its seat exposed no command-execution tool** (read/grep/glob only), so it could
not run the battery, could not verify the byte pin, and returned **UNVERIFIED** — reported here
verbatim rather than as absence:

> VERDICT: UNVERIFIED — hypothesis could not be empirically tested in this seat (no exec
> capability). Static analysis is consistent with CONFIRMED: dead `PULSE_SERVER` → gate block →
> all r95 entries `measured:false`/`coverage_blocked:[named]`/`failures:[]` → stdout
> `"failures": {}` with rc 0. This is inference, not measurement.
> … A `teardown aborted: …` exception inside `_jack_r95_block` lands in `coverage_blocked`, never
> `failures` — a second silent-green surface (L34174–34176). … the stdout summary itself omits
> `measured`/`coverage_blocked`, so a stdout-only reader still sees green.

The child's static cross-check is consistent with the empirical result in §4.3 (which this seat
measured directly); the child created no artifacts and touched no host state.

## 8. Artifacts (all under `/home/vgpnk`, none committed)

- `/home/vgpnk/r95-foldverify-archive/` — `git archive HEAD` tree (build + 4 receipts + probes
  live under its `corpus/live/`).
- `/home/vgpnk/r95-foldverify-scratch/` — `analyze.py`, `lock_probe.py`, `lock_battery.py`,
  `abort_probe.py`, `legs_callsites.py`, `crossrun_diff.txt`, `lock_probe_busy.json`.
- `reports/round-95/r95-foldverify.md` — this file (untracked; **not committed**).

*Leaf seat — verified, measured, probed; did not judge, admit, integrate or ship.*
