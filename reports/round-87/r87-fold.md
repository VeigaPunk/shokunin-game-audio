# r87 FOLD — the landed correction queue applied to the `--probe-pwbind-r87` family

**Seat** FOLD-VERIFY (executor; the combined r87+r88 fold seat applied the
diff in w22 and died before filing — this seat verified and reports per the
w23 task `audio-r87r88-foldverify.md`) · **host** devin/plazir27 · **repo**
`/home/vgpnk/Projects/shokunin/audio-shokunin` · HEAD at verify `0cbbb3bb`
(r89 verifier; last fixture commit `0d732989` r89 author). **Scope**:
`corpus/fixtures/measure_audio.py` only (+ this report + receipts under
`corpus/live/r87-fold/`). No commit, no push — the orchestrator commits.

Fixture sha: `623c25cc55521472dc54a1ab2b4ccb4a9836fda3ca1a71dcca06092a4317cd22`
(pre-fold, == `0d732989` tree; snapshot in `corpus/live/r87-fold/proofs/`)
→ `d278458501a966cf621ff3f858ae6b932c0621df1083bf30559cf5f0325a4dd9`
(post-fold, **32 260 lines**). `python3 -m py_compile` clean (this seat,
re-run). `git diff --stat`: **+310/−112** combined r87+r88.

## Items applied — r87 queue (`audio-r87-fold.md`, w22)

Line numbers are post-fold file positions.

| # | queue item | change | evidence |
|---|-----------|--------|----------|
| 1 | **GATE-BLOCKER** (verifier F1 + reviewer F1): `create_badfac`/`create_usage` read only last 500 chars of a block-buffered pw-cli held-session log; refusal printed 12/12, in-window 2/12 | each create leg now records `"log": _pwbind_r87_norm(log)` — the FULL normed session log (:26966, `log_tail` kept as context); verdicts match over `bf.get("log") or bf.get("log_tail")` (:27160) and `cu.get("log") or cu.get("log_tail")` (:27166) | verify run: both legs carry the full `log` field and the `res:-2`/usage refusals matched in-window — **green while a foreign `--probe-btwit-r88` run churned the registry concurrently** (the exact async-churn class that pushed refusals past the tail bound) |
| 2 | **m_sysex vacuous arm** (reviewer F2 + simplifier F1): "stays running" fired only on rc==0 while harness SIGTERM gives rc=1; 1.7 s window < 4.0 s fixture | new `PWBIND_R87_SYSEX_OBSERVE_S = (0.9, 5.0)` (:25574) — second sample sits past the 4.0 s SMF EOF; `_pwbind_r87_target_leg` gained `observe_s` (:26074); m_sysex leg passes it (:26196); verdict now arms on node-present at the LAST (post-EOF) snapshot, not exit status (:26277–85) | run snaps `[0.919, 5.021]`, `last.present=true` — the law measured past fixture EOF, not vacuous |
| 3 | **skeleton rc arm accepted harness SIGKILL** (reviewer F3) | leg records `self_exited: sk_rc is not None` (:27336) — the process must refuse on its own; verdict now requires `rc != 0 AND self_exited AND` the 20–34 B MThd/no-note-on file witness (:27495) | run: `self_exited=true`, `rc=1`, file witness green — discriminating term live |
| 4 | **midi dead-target census silent-skip + mdump_live empty-attempts** (critic F1/F2) | each unmeasured `m_t_*` leg → `coverage_blocked` ("dead-target census is partial") (:27451); zero mdump_live attempts → `coverage_blocked` naming the absent bridge/seq-14:0 premise (:27514) | run: all 24 midi legs measured, `coverage_blocked` absent |
| 5 | **hard-no-link switches accepted real-link-with-unresolved-peer** (critic F3) | p_zero/p_zero_prop/p_noauto verdicts now accumulate raw `edges_out` over ALL snaps — a real edge whose peer name missed the snapshot's node map still proves the switch failed; node must be present at the LAST snap, not any (:26470–84); same fix on the midi publish-unlinked arms (:27468–76) | run green under concurrent r88 co-tenancy (unresolved-peer window live) |
| 6 | **cold_nowarm bypass / unarmed p_coll + foreign arms** (reviewer F4/F5) | cold_nowarm requires `unknown global '<own nid>'` — the generic `or "unknown global"` bypass is gone; a foreign dead object's line can no longer satisfy the arm (:26987–93); p_coll records `collision_objects` and its Stream/Output/Audio precondition is armed via `coverage_blocked` (:26507); coll_ports playback check unconditional (:26518); `props_unk` leg missing → `coverage_blocked` (:27044–48); foreign `volume_read` unparsed → `coverage_blocked` (:27123) | run: cold_nowarm fired on own id; collision stream published (precondition met, no coverage_blocked) |
| 7 | **Simplifier patch net −7** (T1–T9, proven) | `(loads or {})` → `loads` in teardown sink-sweep/residue arms and `_block` (:25901–48 — teardown callers always pass the dict); dead `leaf = leaf or {}` dropped; `solo_lo, solo_hi = mark(), None` → `solo_lo = mark()` (:26628); `if nid is not None` guard removed around the fmt_sink pwcli block (:26667–77 — nid is bound by construction) | `py_compile` clean; diff shows −112 deletions; all touched arms green in the verify run |

Citation fixes (queue item 8): the two undisclosed RED dev runs are
declared here — the fold seat's own pre-fold replay history is retained in
`corpus/live/runs/` (r87 family dirs `…064958`, `…065456`, `…065750`,
`…070036` precede its green `…070305`); line refs in this table are exact
post-fold positions (verified by grep this seat).

## Leg results — green runs on the folded bytes

| run | receipt (`corpus/live/runs/`) | seat | result |
|-----|------------------------------|------|--------|
| fold r1 | `20261016T070305393338Z-pwbind-r87` sha `2970c944375f2e3b8b6f3ab16bdd5a343521222844d9a3a044a0a7d9a974a655` | fold (w22) | `{"failures": {}}` — declared green in w23 task card |
| **verify r1** | `20261016T083046454782Z-pwbind-r87` sha **`895deece0eedb48e5cf9c86077cb15831d1371006fbd74922be69c279601d61c`** | **fold-verify (w23, this seat)** | exit 0 · `{"failures": {}}` · 4 entries / **105 legs** · `coverage_blocked` absent — every folded arm measured |

Verify-run particulars: launched `TMPDIR=/home/vgpnk/Projects/shokunin/tmp
python3 corpus/fixtures/measure_audio.py --probe-pwbind-r87`, **concurrent
with a live `--probe-btwit-r88` run on the same daemon** — the two families'
locks are disjoint by design and the overlap exercised precisely the
co-tenancy class the queue repaired. Seat-owned objects: probe-internal
`r87a_<pid>` namespace only; no manual PipeWire objects needed (the
`r87f_`/`r88f_` prefix reservation went unused); no `set-default-*` call
made (the probe's own read-only `default_sink_at_start/end` compare ran —
unchanged in receipt). Receipt copies + `proofs.txt` + `fold.diff` under
`corpus/live/r87-fold/`.

## Remaining risks / blockers

1. **None blocking.** Both runs green on the first attempt; no host
   confound observed, so no second run was needed.
2. The concurrent-verify design means a real defect and a co-tenancy
   confound would both have shown red; they showed green — the stronger
   evidence for the repair class. Had either run gone red, a serial rerun
   would have separated the two causes (none needed).
3. `p_coll`'s armed precondition and the new `coverage_blocked` arms can
   go non-vacuously red on a busier host — that is the intended honest
   signal vs the old silent pass.
4. No resume mutation attempted; no commit, no push.

Seat stop — files changed by THIS seat: `reports/round-87/r87-fold.md`,
receipts `corpus/live/r87-fold/` (measurements copy, run1 stdout/stderr,
`fold.diff`, `proofs.txt`). The fixture diff itself is the w22 fold seat's
uncommitted work, verified not modified. The canonical Rust runtime remains
the sole judge.
