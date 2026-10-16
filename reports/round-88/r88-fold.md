# r88 FOLD — the landed correction queue applied to the `--probe-btwit-r88` family

**Seat** FOLD-VERIFY (executor; the combined r87+r88 fold seat applied the
diff in w22 and died before filing — this seat verified and reports per the
w23 task `audio-r87r88-foldverify.md`) · **host** devin/plazir27 · **repo**
`/home/vgpnk/Projects/shokunin/audio-shokunin` · HEAD at verify `0cbbb3bb`
(r89 verifier; last fixture commit `0d732989` r89 author). **Scope**:
`corpus/fixtures/measure_audio.py` only (+ this report + receipts under
`corpus/live/r88-fold/`). No commit, no push — the orchestrator commits.

Fixture sha: `623c25cc55521472dc54a1ab2b4ccb4a9836fda3ca1a71dcca06092a4317cd22`
(pre-fold, == `0d732989` tree; snapshot in `corpus/live/r88-fold/proofs/`)
→ `d278458501a966cf621ff3f858ae6b932c0621df1083bf30559cf5f0325a4dd9`
(post-fold, **32 260 lines**). `python3 -m py_compile` clean (this seat,
re-run). `git diff --stat`: **+310/−112** combined r87+r88.

## Items applied — r88 queue (`audio-r88-fold.md`, w22)

Line numbers are post-fold file positions.

| # | queue item | change | evidence |
|---|-----------|--------|----------|
| 1 | **wd_dump_empty bracket race** (verifier F1 + reviewer F1, 2-seat): arm required pw-dump `''` id-set == census exactly; transient clients drift ±1 | arm is now census **membership**: every object stable across BOTH bracket censuses must appear in the dump (completeness — the falsifiable half of "'' is the full dump"); dump-only ids are recorded as mid-window transients → `coverage_blocked`, and an unreadable bracket census → `coverage_blocked`; the leg records `census_bracket{stable_core, missing_from_dump, transient_in_dump}` (:29030–55) | verify run: `parsed_ids=99`, `stable_core=99`, `missing=[]`, `transient=[]` — the membership arm measured, complete, and green under a concurrent `--probe-pwbind-r87` run (live transient window) |
| 2 | **foreign stderr pollution** (verifier F2): one-shot `pw-cli info <id>` prints `remote 0: error … no global` when a foreign object dies mid-call, flipping empty-channel arms | new `_BTWIT_R88_FOREIGN_ERR` (:27740) matches the broadcast shapes (`remote N: error` + `no global`/`unknown resource`/`Stale file handle` res:-116) — lexically disjoint from the own-refusal `Error: "<verb>: unknown global '<id>'"` so it can never eat an own refusal; `_btwit_r88_scrub_foreign` (:27745) splits channels into (clean, dropped) with dropped lines recorded on the leg as `foreign_noise`, never hidden; `_btwit_r88_run` computes `error_class` on the scrubbed text (:27782–98); all silent-absence arms (`wd_silent_dump_*`, `wd_silent_cli_meta`, `wd_cli_meta_extra`, `wd_dead_serial`) and the enum-pair compare judge the own channel only (:29012–171) | run: 0 legs carried `foreign_noise` (quiet window — the scrub was armed, not needed); all silent arms green |
| 3 | **error_class precedence** (verifier F3; r87-F4 realized): preceding foreign res:-2 masks the real res:-22 | `_btwit_r88_errclass` (:27701) now does **latest-position-wins** across the r88-local AND inherited r87 tables — last `finditer` match per class, then max position across classes; the owning request's error is the last error line, so a first-table-match can no longer pick an earlier foreign refusal; r86 chain fall-through untouched | run green; errclass used by every `_btwit_r88_run` leg this run |
| 4 | **pt_nneg/pt_nabc flush-timing lottery** (verifier F4): frame arm timing-dependent | the armed law is now only "infinite" = `killed_at_bound`; the frame witness rides block-buffered stdout that a bound SIGKILL can lose entirely, so bound-killed-but-0-frames → `coverage_blocked` ("frame witness lost to block buffering"), never a law failure; `frames_seen` recorded on the leg (:29395–407) | run: `pt_nneg frames_seen=1 killed_at_bound=true` — measured, green |
| 5 | **bz_tree truncated enumeration** (verifier F8, false-PASS direction) | busctl tree bound widened 2400 → `keep_chars=16000` (:28252); leg records `stdout_bytes` + `truncated` flag; a still-truncated result → `coverage_blocked`, not silent judgment (:28421) | run: `stdout_bytes=94`, `truncated=false`, 1 adapter enumerated |
| 6 | **bz_device negative-only** (reviewer F2): fault-injected absence still green | zero paired devices → `coverage_blocked` (HID-only claim unmeasured); a device whose UUIDs prop failed to parse (`uuid16` empty) → per-device `coverage_blocked` — absence-of-evidence no longer passes as HID-only (:28437–50) | run: devices enumerated with readable UUIDs, `coverage_blocked` absent |
| 7 | **missing-leg silent skips → coverage_blocked** (critic F1–3, reviewer F3) | `wd_setrule_foreign_*` missing legs (:28897), `wd_no_nested` empty members (guards the mode-invariance pair) (:28917), `wd_dump_two` leg absent (:29068), `pt_state_active` vocab never recorded — the old `elif l.get("vocab")` made an absent vocab silently pass; now `elif not vocab → coverage_blocked` before the four-witness agreement check (:29437–42) | run: all referenced legs measured, `coverage_blocked` absent |
| 8 | **Simplifier patch net −7** (T1–T6, proven) | `_btwit_r88_run` drops dead `env`/`stdin_data` params — stdin DEVNULL unconditional (:27756–77); `bz_own_residue` `.items()` → `.values()` (unused nid) (:28375); teardown/`_block` `(loads or {})` → `loads` with direct `leaf["field"]`/`leaf["value"]` (loader always sets both) (:28120–78); redundant `_frames_cache` pops removed (:29257, :29318 — the recorded rec keeps its frames cache) | `py_compile` clean; all touched arms green in the verify run |

Citation fixes (queue item 9): the uncited RED dev run is declared here —
the fold seat's pre-green r88 family dirs `…071710822152Z` and
`…072313132218Z` sit in `corpus/live/runs/` before its green `…072341162452Z`;
line refs in this table are exact post-fold positions (grep-verified this
seat).

## Leg results — green runs on the folded bytes

| run | receipt (`corpus/live/runs/`) | seat | result |
|-----|------------------------------|------|--------|
| fold r1 | `20261016T072341162452Z-btwit-r88` sha `cce9164f5a537f349e449be4576623fce44cfd4d3e2f6364383f515e0d9b640d` | fold (w22) | `{"failures": {}}` — declared green in w23 task card |
| **verify r1** | `20261016T082832174010Z-btwit-r88` sha **`dded6f2cff9773436cd4ee01a0a97840d2f158f2be74b31ed1e74ae76bacefcc`** | **fold-verify (w23, this seat)** | exit 0 · `{"failures": {}}` · 3 entries (`btabs_bluez_r88_probe`, `witdiff_dump_r88_probe`, `pwtop_r88_probe`) · `coverage_blocked` absent — every folded arm measured |

Verify-run particulars: launched `TMPDIR=/home/vgpnk/Projects/shokunin/tmp
python3 corpus/fixtures/measure_audio.py --probe-btwit-r88`, **concurrent
with a live `--probe-pwbind-r87` run on the same daemon** — the two
families' locks are disjoint by design and the overlap exercised the
registry-churn/transient-client classes this queue repaired. Seat-owned
objects: probe-internal `r88a_<pid>` namespace only; no manual PipeWire
objects needed (the `r88f_` prefix reservation went unused); no
`set-default-*` call made. Receipt copies + `proofs.txt` + `fold.diff`
under `corpus/live/r88-fold/`.

## Remaining risks / blockers

1. **None blocking.** Green on the first attempt; no host confound
   observed, so no second run was needed.
2. The foreign-noise scrub did not fire this run (0 `foreign_noise` legs)
   — its mechanism is diff-verified and armed, but a busier registry
   window would be the stronger live exercise; the concurrent r87 run did
   produce real co-tenancy without emitting the filtered shapes.
3. The `wd_dump_empty` membership arm keeps the falsifiable completeness
   half only — a dump that is a strict subset-plus-transients of a churning
   census reports `coverage_blocked`, not failure; that asymmetry is the
   queue's intent, recorded here.
4. `bz_tree`'s 16 000-char bound can still truncate on a much more
   populated host — now honestly `coverage_blocked` instead of false-PASS.
5. No resume mutation attempted; no commit, no push.

Seat stop — files changed by THIS seat: `reports/round-88/r88-fold.md`,
receipts `corpus/live/r88-fold/` (measurements copy, run1 stdout/stderr,
`fold.diff`, `proofs.txt`). The fixture diff itself is the w22 fold seat's
uncommitted work, verified not modified. The canonical Rust runtime remains
the sole judge.
