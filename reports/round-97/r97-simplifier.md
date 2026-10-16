# r97 SIMPLIFIER — proven folds in the `wppol` block at `b8ff4efc`

**Seat.** `r97-simplifier` (specialist dispatch; non-judge — the canonical Rust
runtime remains the sole judge). **Target.** `b8ff4efc` "r97 author: wppol
WirePlumber policy lattice (5 entries/69 legs, +2156/-3)" in
`/home/vgpnk/Projects/shokunin/audio-shokunin`; the block under fold is
`corpus/fixtures/measure_audio.py` **lines 43788–45905** (committed blob sha256
`7a070fa817c4de6f4ae5eb5be38e7cfc2cdbb18cad605ee52427afcf0a6ca2bc`).
**Tasking.** proven folds only in the wppol block; critic **F2** (constant
`errclass`), **F6** (duplicate leg) and **F7** (dead entries) are the fold
targets; before/after runs on an archive under `/home`; file this report; land
nothing; do not commit.

**Host** `plazir27` (32 cores; PipeWire 1.6.8 / WirePlumber 0.5.17 / Lua 5.5 /
Python 3.14.7). **Window** 2026-10-16 10:19Z–10:36Z (local UTC−3).

**Archive (under /home, never /tmp).**
`/home/vgpnk/Projects/shokunin/simplifier-r97/` — `wt/` is `git archive
b8ff4efc` extracted (fixture sha `7a070fa8…` = the committed blob), `folded/`
is the same archive with the fold applied (fixture sha `c2937912…`). Receipts,
patch, LSP logs and the law-set outputs live in `out/`, `logs/`, `lsp/`.
The main checkout was **not** written by this seat except this report (§6).

**Verdict shape (no judgment).** All three named findings are **proven folds**:
the `lsp` device answers the file and every candidate deletion has **zero
semantic references** (or zero in-body uses); a paired before/after battery on
the archived bytes is **green with no armed cell moved** (the receipt delta is
the fold itself plus the family's recorded-volatile classes); and the existing
r97 verifier law set scores **260/260 on the pristine bytes and 255 PASS /
4 FAIL / 1 BLOCKED on the folded bytes, flipping exactly the five bookkeeping
laws the fold predicts** and nothing else. Fold size: **+16/−27 lines** (net
−11) inside the block; census **69 → 68** legs.

---

## 1. Fold inventory (E1–E9) — critic F2 / F6 / F7 only

| # | finding | deletion | patch effect |
| --- | --- | --- | --- |
| E1 | F7 | `WPPOL_R97_SINK_D` constant (defined, never referenced) | −1 line |
| E2a | F7 | `_wppol_r97_run(..., keep_raw=False)` parameter (never passed) | 1↔1 |
| E2b | F7 | the `if keep_raw:` branch inside `_wppol_r97_run` (dead) | −2 |
| E3 | F7 | `_wppol_r97_spawn(..., root=None)` parameter (never read, never passed) | 1↔1 |
| E4 | F7 | `_wppol_r97_purge(env, cli, root)` → `(env)`; `cli`/`root` never read (def + 7 call sites) | 8↔8 |
| E5 | F2 | `a3_conf_dir_missing.errclass` — the constant-fed pair (`"Could not locate…"` literal is *always* fed whenever `marks` is a dict, so the field is not a function of the log) | 5→1 |
| E6 | F2 | `a9_wp_on_modules_less_core.errclass` — `[None, None]` in every receipt (the variant's streams are empty; the marks are the armed witness) | 4→1 |
| E7 | F6 | `entry["d9_lag_s"]` — the same expression on the same `t0` as the retained `d9_explicit_beats_priority.state_file_row_secs` (1.003/1.003 before, 1.002 retained after) | −1 |
| E8 | F6 | header census `69 … (arming 14 / defaults 15 / …)` → `68 … (14 / 14 / …)` | 2↔2 |
| E9 | F6 | header rule list: drop `d9_lag_s` (the folded key) and `unloads` / `residual_destroy` (never written by this family) | 2↔2 |

Totals: **+16 / −27 lines, net −11**, 14 hunks, all inside the r97 block. Full
patch in Appendix A (`out/r97-fold.patch`, sha256 `13b0f5306845e34b…`,
`patch -p1 --dry-run` clean against the pristine archive).

Nothing else is folded. In particular the *remaining* `errclass` writes are
kept: `_wppol_r97_stream_leg` (44594) and `d9_explicit_beats_priority` (45204)
both derive it from **real stderr**, and the LSP proof below shows the helper
keeps 4 genuine uses — E5/E6 delete only the two flagged fields.

---

## 2. Reference proof — the `lsp` device (semantic), and its literal fallback

Server: `~/.hermes/lsp/bin/pyright-langserver --stdio` (node v24.21.0) answered
the archived file. Warmup discipline was followed: the first request
(anchor `WPPOL_R97_SINK_C`) returned **8 references** on the first call, so no
cold-empty result was ever recorded as absence; the client is
`lsp/lsp_refs.py`, raw results `lsp/lsp_refs.json`.

| symbol / position | refs | non-declaration | conclusion |
| --- | --- | --- | --- |
| `WPPOL_R97_SINK_D` (43865) | 1 | **0** | zero references — delete |
| `_wppol_r97_spawn` `root` (44199) | 1 | **0** | never read — drop (callers: 3, none passes it) |
| `_wppol_r97_run` `keep_raw` (44166) | 2 | 1 (the dead branch itself) | no caller passes it — drop param + branch |
| `_wppol_r97_purge` `cli` / `root` (44515) | 1 / 1 | **0 / 0** | never read — drop (fn has 8 refs = def + 7 call sites, all edited) |
| anchor `WPPOL_R97_SINK_C` | 8 | 7 | server warm/answer verified |
| anchor `_wppol_r97_errclass` | 5 | 4 | helper stays (stream_leg, a3, a9, d9) — only a3/a9 fields fold |

**Literal fallback, explicitly not semantic proof** (the folded keys are *dict
strings*, not symbols — pyright cannot resolve them): in the whole archived
tree (1 021 `.py` files) `d9_lag_s` occurs exactly **twice** — the header rule
line and the writer — with **no reader**; `errclass` inside the block is
**4 writes, 0 reads**; `wppol_config_missing` occurs only in the helper's own
class table. A literal census of all 30 `WPPOL_R97_*` constants finds
`WPPOL_R97_SINK_D` as the **only** single-occurrence name (independently
corroborating the LSP result).

---

## 3. Before / after runs on the archive

| run | command (same bytes except the fold) | receipt | sha256 | legs | verdict | wall |
| --- | --- | --- | --- | --- | --- | --- |
| before | `python3 corpus/fixtures/measure_audio.py --probe-wppol-r97` in `wt/` | `wt/corpus/live/runs/20261016T102636213705Z-wppol-r97/measurements.json` | `06d7fcbccf132a29…` | **69** = 14/15/21/15/4 | rc 0, `failures {}`, no blocks | 10:21:14→10:26:36Z |
| after | same in `folded/` | `folded/corpus/live/runs/20261016T103215168278Z-wppol-r97/measurements.json` | `76bf623a5669f5b1…` | **68** = 14/14/21/15/4 | rc 0, `failures {}`, no blocks | 10:26:53→10:32:15Z |

Both runs: `TMPDIR=~/Projects/shokunin/tmp`, `PYTHONDONTWRITEBYTECODE=1`; host
loadavg at entry heads 1.35–6.33 (before) / 2.29–4.60 (after); `own_procs_after
== []` and `shared_census.own_hits == []` in all five entries; no `r97a`
process survived either run.

**Armed cells reproduced on the folded bytes** (the family's own checks, not a
re-derivation): `a3` rc 78 + naming mark + no fragments/chain marks; `a9` rc 69
+ connect mark + middle mark absent; `a1` ready 0.256 s; `a11` rc 0; `d9` rc 0
+ both metadata rows + state-file row at 1.002 s; `d12` flush window lost
(`flushed_before_restart False`, default → `sq`, 1.304 s); `d13` durable row at
1.003 s; `l4` rc None / `l7` rc 1 / `l8` alive at cap; `l18` movement B→A
recorded, unarmed; `w7` rc −9 timed out; `s1` 25 keys + sha `56526540…`; `s2`
two metadata faces; `s4` same key set; `s3` operator value unchanged.

**Receipt delta (raw leaf diff `out/receipt-diff.txt`, classifier
`out/diff-classified.txt`).** 298 leaves differ raw; after volatile
normalization **119** remain, classified as: **5 = the fold itself**
(`a3.errclass[0..1]`, `a9.errclass[0..1]`, `d9_lag_s` absent) and **114 =
recorded-volatile classes** — 42 private pids, 28 loadavg values, 18 timing
floats, 15 operator-graph census ints (`objects`, `monitors_count`,
`sources_count`, `fixture_runs`, `paplay`), 5 runtime node ids, 6 explained
misc (3 `argv` strings carrying the runtime-assigned node id 37→38; 3
entry-head fields carrying the operator's live default source — an **r91 lane's
node** `r91a_src_1229645` was the operator's default during the after run).
**No armed cell differs.**

**Independent law-set re-run** (`corpus/live/r97-verifier/runs/r97v_laws.py`,
read-only, cross-root = the verifier's frozen tree):

| receipt | laws | PASS | FAIL | BLOCKED |
| --- | --- | --- | --- | --- |
| before (pristine bytes) | 260 | **260** | 0 | 0 |
| after (folded bytes) | 260 | **255** | **4** | **1** |

The five flips are exactly the predicted bookkeeping laws —
`arming.a3.errclass` (FAIL), `arming.a9.errclass_key_present` (FAIL),
`defaults.d9_lag_s` (BLOCKED), `global.leg_census` (FAIL, defaults 14≠15),
`global.leg_census_total` (FAIL, 68≠69). **Every mechanism, custody and
cross-seat law still passes.**

**Narrow checks on the folded file before claiming improvement:** `compile()`
ok (47 413 lines), `--help` lists `--probe-wppol-r97`, the probe mutex returns
rc 2 against `--probe-pulsecli-r96` and `--probe-failing`, and the patch
re-applies cleanly to the pristine archive (dry-run).

---

## 4. Preserved contract

- The **armed witnesses are untouched**: the a3 naming mark / rc 78, the a9
  connect mark / rc 69, the a2 non-gate, the default-rank lattice, the
  flush-gated restart race with its vacuity guard, the linking namespace
  lattice, the wpexec sandbox, the 25-key settings lattice, and the custody
  censuses. The two deleted `errclass` fields were **recorded-only**; the
  classes they carried remain derivable from the retained `log_tail` and the
  armed scan marks.
- `d9_explicit_beats_priority` keeps the observation F6 pointed at
  (`state_file_row_secs`, 1.002 s after the fold vs 1.003 s before) — only the
  duplicate top-level key goes.
- No other family, no dispatch/mutex/mode/suffix wiring, and no shared line is
  touched; the 17 base entries ran green in both batteries.
- Nothing historical is deleted: `r97-author.md`, `r97-critic.md` and
  `r97-verifier.md` keep their "69" census as the r97 record; the live block
  header is updated to 68 so the fixture and its receipt cannot disagree.

---

## 5. Candidates found but **not** folded (proof attached)

The AST sweep (and the second LSP pass, `lsp/lsp_refs_candidates.json`) found
**four more never-read parameters** in the block — same class as F7, but
outside the tasking's named fold set:

| candidate | refs (LSP) | non-decl | call sites that would need editing |
| --- | --- | --- | --- |
| `_wppol_r97_stream_leg(env, root, …)` — `root` never read | 1 | **0** | 1 |
| `_wppol_r97_teardown(…, conf, …)` — `conf` never read | 1 | **0** | 5 |
| `_wppol_r97_block(…, conf=None, …)` — `conf` never read | 1 | **0** | 7 |
| `_wppol_r97_restart_wp(…, conf, …)` — `conf` never read | 1 | **0** | 3 |

They are left as **deletion candidates** on purpose: dropping them costs 16
call-site edits and removes no lines (each call line just gets shorter), so it
is diff churn rather than weight removal — and the tasking bounds this fold set
to the critic's F2/F6/F7 items. An author lane may take them as a separate,
deliberate diff.

---

## 6. Disclosures and tradeoffs

1. **The fold invalidates five laws of the *existing* r97 verifier law set**
   (listed in §3) — not because a mechanism changed, but because those laws are
   keyed on the deleted fields and the 69-leg census. The next law set must
   expect `14/14/21/15/4 = 68` and drop the two `errclass` laws (or read the
   armed scan marks, which remain). This is the accepted cost of removing two
   fields that *looked* derived and a duplicate leg.
2. **Census headline moves 69 → 68.** The commit message and the historical
   r97 reports keep "69"; the live header (E8/E9) is corrected so a recount of
   the folded receipt is exactly 68.
3. **Not folded, deliberately:** F1 (would *add* an armed check — new
   behaviour), F3 (zombie-aware death detector + first-signal instant —
   behaviour change), F4 (spawn-set membership in the kill guard — behaviour
   change), F5 (report wording, not a fixture byte). All are author-lane work,
   not deletions.
4. **Main checkout state.** HEAD `a2c6e3b7`; `corpus/fixtures/measure_audio.py`
   is the pre-existing r90-foldfix dirt (sha `e2e5a002…`, not mine and not the
   reviewed blob) — unchanged before and after this seat; no commit, no stage,
   no lock/receipt written under main's `corpus/live/`; the only file this seat
   adds to main is this report (verified in §7). The reviewed landing is the
   committed `b8ff4efc` blob, which is what the archive carries.
5. **Foreign load.** Other lanes were live in the window (an r99 rtp battery,
   an r93 ebur battery, an r90 wpstate battery; an **r91 lane's node** was the
   operator's default source during the after run). Every such value is
   recorded-not-armed in the receipts; both batteries stayed green.
6. **Residue.** No `r97a` process survived either run; the private roots remain
   on disk as the family's own evidence (the 81 `wppol-r97-*` roots under
   `~/Projects/shokunin/tmp/` are the accumulated r97 lanes', not this fold's).

---

## 7. Shared-tree verification

Captured `git status --porcelain` (sorted) + fixture sha256 at 10:27:23Z, then
again after the after-run and the law-set re-runs: the only delta is a
**foreign** lane's `?? reports/round-92/r92-simplifier.md`; the fixture sha is
`e2e5a002…` both times. After writing this report the only new entry is this
file. Main tree bytes are otherwise identical; nothing was committed.

---

## 8. Stop line — where the next deletion would harm an axis

- Deleting the two **remaining** `errclass` writes would delete *observations*
  (both derive from real stderr) — receipt provenance.
- Deleting `scan` / `log_tail` would delete the **armed witnesses** — the
  mechanism axes themselves.
- Deleting `state_file_row_secs` (the retained field behind F6) would delete
  the flush observation.
- Deleting the custody keys (`own_procs_after`, `shared_census`, the environ
  kill guard's records) would delete the isolation witness.
- Dropping the four candidate parameters would be churn without weight
  reduction (§5) — a reviewability wash, not a Pareto move.

Seat stop. The canonical Rust runtime remains the sole judge.

---

## Appendix A — the exact fold patch (+16 / −27, net −11)

`out/r97-fold.patch` (sha256 `13b0f5306845e34bb299019687c5bb375aa4208fd97400d76b662d693b3501f9`),
applies with `patch -p1` / `git apply` at the repo root against the committed
blob `7a070fa8…`:

```diff
--- a/corpus/fixtures/measure_audio.py
+++ b/corpus/fixtures/measure_audio.py
@@ -43834,15 +43834,15 @@
 #     3/3 in the plain-pw-cat shape — the leg records the observation
 #     and arms only the settings read-back).
 #
-#     Leg census: 69 top-level observation keys across the 5 entries
-#     (arming 14 / defaults 15 / linking 21 / wpexec 15 / settings 4).
+#     Leg census: 68 top-level observation keys across the 5 entries
+#     (arming 14 / defaults 14 / linking 21 / wpexec 15 / settings 4).
 #     The rule, so the receipt can be recounted: the named context keys
 #     (probe, contention, oracle_at_start, foreign_r97a_nodes,
 #     inventory, loadavg, private_root, conf_paths, starts, pair,
 #     wp_restarts, stops, purge_before, own_procs_after, shared_census,
-#     coverage_blocked, failures, blocked, unloads, residual_destroy)
+#     coverage_blocked, failures, blocked)
 #     are NOT counted; the custody sub-records that carry an observation
-#     each (a1_core, a2_stop_wp, d9_lag_s, l7_node_gone, w14_wp_stop,
+#     each (a1_core, a2_stop_wp, l7_node_gone, w14_wp_stop,
 #     own_nodes_before_teardown, setup) ARE. The pre-measurement "63"
 #     headline in the first draft of this header was arithmetic drift —
 #     the receipt leg keys are the record (r89 fold convention).
@@ -43862,7 +43862,6 @@
 WPPOL_R97_SINK_A = f"r97a_sa_{WPPOL_R97_PID}"
 WPPOL_R97_SINK_B = f"r97a_sb_{WPPOL_R97_PID}"
 WPPOL_R97_SINK_C = f"r97a_sc_{WPPOL_R97_PID}"
-WPPOL_R97_SINK_D = f"r97a_sd_{WPPOL_R97_PID}"
 WPPOL_R97_SINK_E = f"r97a_se_{WPPOL_R97_PID}"
 WPPOL_R97_SINK_F = f"r97a_sf_{WPPOL_R97_PID}"
 WPPOL_R97_SINK_G = f"r97a_sg_{WPPOL_R97_PID}"
@@ -44163,7 +44162,7 @@
 
 
 def _wppol_r97_run(argv, timeout_s, env=None, stdin_data=None,
-                   keep_chars=2400, keep_raw=False):
+                   keep_chars=2400):
     """One bounded leg. Own session; SIGKILL of the process group on
     timeout (never a namespace-blind sweep)."""
     rec = {"argv": [str(a) for a in argv]}
@@ -44191,12 +44190,10 @@
                 "stdout": (out or b"")[:keep_chars].decode("utf-8", "replace"),
                 "stderr": (err or b"")[:keep_chars].decode("utf-8", "replace"),
                 "bytes": len(out or b"") + len(err or b"")})
-    if keep_raw:
-        rec["stdout_raw"] = (out or b"")[:1 << 18].decode("utf-8", "replace")
     return rec
 
 
-def _wppol_r97_spawn(argv, env=None, log=None, root=None):
+def _wppol_r97_spawn(argv, env=None, log=None):
     """Spawn a private daemon in its own session, log to file."""
     lf = open(str(log), "w") if log else subprocess.DEVNULL
     proc = subprocess.Popen([str(a) for a in argv], stdin=subprocess.DEVNULL,
@@ -44512,7 +44509,7 @@
     return cli.cmd(f"create-node adapter {props}")
 
 
-def _wppol_r97_purge(env, cli, root):
+def _wppol_r97_purge(env):
     """Destroy every own-namespace node (a leftover sink is the r97b
     c_defaults contamination class — the incumbent must never be a
     stale one)."""
@@ -44689,7 +44686,7 @@
     environ-aware guard, then census own processes and the operator's
     graph (a private lane must leave zero r97a_ objects behind)."""
     if cli is not None:
-        _wppol_r97_purge(env, cli, root)
+        _wppol_r97_purge(env)
         cli.close()
     for tag in ("wp", "core"):
         pid = None
@@ -44731,7 +44728,7 @@
     record the block (never a fabricated pass)."""
     if cli is not None:
         try:
-            _wppol_r97_purge(env, cli, root)
+            _wppol_r97_purge(env)
         except Exception:
             pass
         cli.close()
@@ -44899,11 +44896,7 @@
                                     "dur_s": v1.get("dur_s"),
                                     "scan": scan,
                                     "log_tail": _wppol_r97_log_tail(
-                                        v1.get("log")),
-                                    "errclass": _wppol_r97_errclass(
-                                        (scan or {}).get("marks") and
-                                        "Could not locate configuration file "
-                                        "'wireplumber.conf'" or "")}
+                                        v1.get("log"))}
     if v1.get("rc") != 78:
         failures.append(f"a3_conf_dir_missing: rc {v1.get('rc')} — expected "
                         "78 (EX_CONFIG)")
@@ -45020,10 +45013,7 @@
                                            runtime=conf["run_stub"]))
     scan_l2 = l2.get("scan")
     entry["a9_wp_on_modules_less_core"] = {"rc": l2.get("rc"),
-                                           "scan": scan_l2,
-                                           "errclass": _wppol_r97_errclass(
-                                               (l2.get("stderr") or "")
-                                               + (l2.get("stdout") or ""))}
+                                           "scan": scan_l2}
     if l2.get("rc") != 69:
         failures.append(f"a9_wp_on_modules_less_core: rc {l2.get('rc')} — "
                         "expected 69 (EX_UNAVAILABLE)")
@@ -45119,10 +45109,10 @@
                                 "defaults: private pair not ready", root, conf,
                                 env)
     cli = _WppolR97Cli(root, env)
-    entry["purge_before"] = _wppol_r97_purge(env, cli, root)
+    entry["purge_before"] = _wppol_r97_purge(env)
 
     def fresh(*sinks):
-        _wppol_r97_purge(env, cli, root)
+        _wppol_r97_purge(env)
         for nm, sess, drv in sinks:
             _wppol_r97_null(cli, nm, sess, drv)
         time.sleep(0.8)
@@ -45177,7 +45167,7 @@
 
     # d9 — an explicit set-default outranks every later priority, writes
     # BOTH metadata rows and (lagging ~1 s) the state file.
-    _wppol_r97_purge(env, cli, root)
+    _wppol_r97_purge(env)
     _wppol_r97_null(cli, WPPOL_R97_SINK_C, 50, 100)
     time.sleep(0.6)
     _wppol_r97_null(cli, WPPOL_R97_SINK_Q, 300, 100)
@@ -45214,7 +45204,6 @@
         failures.append("d9_explicit_beats_priority: the state file never "
                         f"gained the configured row (cap "
                         f"{WPPOL_R97_FLUSH_CAP}s)")
-    entry["d9_lag_s"] = round(time.monotonic() - lag_t0, 3)
 
     # d10 — clear-default hands the default back to the best available.
     clr = _wppol_r97_run(["wpctl", "clear-default"], 12.0, env=env,
@@ -45244,7 +45233,7 @@
     # d12/d13 — the restart race: a restart inside the ~1 s flush window
     # loses the configured choice (and leaves NO configured row); after
     # the row appears the choice survives.
-    _wppol_r97_purge(env, cli, root)
+    _wppol_r97_purge(env)
     _wppol_r97_null(cli, WPPOL_R97_SINK_Q, 500, 100)
     time.sleep(0.6)
     _wppol_r97_null(cli, WPPOL_R97_SINK_P, 50, 100)
@@ -45341,7 +45330,7 @@
                                 "linking: private pair not ready", root, conf,
                                 env)
     cli = _WppolR97Cli(root, env)
-    _wppol_r97_purge(env, cli, root)
+    _wppol_r97_purge(env)
     _wppol_r97_null(cli, WPPOL_R97_SINK_A, 100, 100)
     time.sleep(0.6)
     _wppol_r97_null(cli, WPPOL_R97_SINK_B, 500, 100)
```

## Appendix B — evidence index (all under `/home`, scratch, untracked)

- `simplifier-r97/wt/` — pristine archive (`git archive b8ff4efc`);
  fixture sha `7a070fa8…`; before receipt `…T102636213705Z-wppol-r97/`.
- `simplifier-r97/folded/` — folded archive; fixture sha `c2937912…`; after
  receipt `…T103215168278Z-wppol-r97/`.
- `simplifier-r97/out/r97-fold.patch` (+16/−27), `out/receipt-diff.txt` (raw
  leaf diff), `out/diff-classified.txt` (volatile-class census),
  `out/laws-before.json`, `out/laws-after.json`, `out/main-status-*.txt`.
- `simplifier-r97/lsp/lsp_refs.py`, `lsp_refs.json` (fold proof);
  `lsp_refs_candidates.py`, `lsp_refs_candidates.json` (candidate proof).
- `simplifier-r97/logs/{before,after}.out` — battery stdout (the receipts'
  own `measurements.json` are the record).
