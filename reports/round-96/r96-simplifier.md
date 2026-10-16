# r96 simplifier — proven folds in the pulsecli block (`7358f13b`), queued, not landed

**Verdict: PASS — 2 proven folds queued (F1 `t_proc_lat_b` −2 lines; F2 the
pid-keyed `_pulsecli_r96_run`/`_row` repair, +1 line +2 re-keyed call sites),
1 proven weight-first alternative held (F3, −7 lines, F-axis tradeoff named),
1 candidate class held with its convention reason. Nothing landed, zero
tracked writes, zero commits.**

The folds live only in the archive checkouts under
`/home/vgpnk/Projects/shokunin/r96s/` (the tasking's "archive under /home");
the shared tree is byte-identical at entry and exit (§1). Every fold is proved
by a fresh before/after battery on this host (7 batteries, §5) plus a narrow
C4 probe (§6), and the round's own verifier law set re-derives the folded
receipts (§5.3).

- **Lane**: `/home/vgpnk/Projects/shokunin/audio-shokunin`. The audit is on
  the commit-pinned blob `7358f13b:corpus/fixtures/measure_audio.py`; the
  archive basis is `git archive 7358f13b`, tar sha256 `5a6a1000…` — **the r96
  verifier's own frozen-tree sha**, 44 579 files / 11 772 dirs / 0 symlinks.
- **The shared tree MOVED under this seat** (disclosed): HEAD advanced
  `a2c6e3b7` → `d41cfa68` ("r98 author: pw-stream … lattice, +2389/−3") at
  10:37:55Z, mid-window. Checked: the **r96 block is byte-identical in both**
  (span 41471–43787, sha `be60f1ba…`, at the same lines in the new HEAD), the
  audited `7358f13b` fixture blob hashes equal at entry and exit, and both
  fold patches still apply **exactly once** on the new HEAD's bytes
  (`headcheck`, §1).
- **Writes**: this report + `corpus/live/r96-simplifier/` (small evidence
  copies, untracked) + the archive checkouts, run receipts and scripts under
  `/home/vgpnk/Projects/shokunin/r96s/`. `git status --porcelain
  --untracked-files=no` is **identical at entry and exit** (§1).
- **No `lsp` device** answers this tree: this seat's tool surface exposes no
  language-server session and the only MCP server on this substrate is `rea`
  (a Ghidra-family native-binary provider — no Python source semantics, no
  `references` verb). **Recorded unavailable.** Every "no callers" claim below
  is the declared literal fallback — an AST load/call-site census over the
  whole 45 271-line module plus `grep` — never presented as semantic proof.
  No rename is proposed (renaming is the class of change that would need the
  device).

## 0. Axes named for this gate

| axis | direction | what would harm it |
| --- | --- | --- |
| weight | fewer lines / recorded keys / dead paths in the pulsecli block | — |
| preserved contract | the 5 entries, the armed laws and values, the receipt surface the round's seats diff against | deleting a law, a cell, an armed value, or a recorded witness that a consumer reads |
| honesty / falsifiability | a recorded witness that cannot witness (or can fire on the wrong subject) must not read as one | keeping a dead or misdirected predicate while its message claims a witness |
| convention consistency | one authority per job; the r84/r96 pid-keyed conventions | inventing a second form of an existing helper; diverging a wrapper from its twin |
| proof cost | every queued fold proved by a fresh before/after battery on this host | a fold whose proof needs a new measurement or a mutant |

## 1. Audited revision, archive checkouts, custody

| artifact | revision | size | sha256 |
| --- | --- | --- | --- |
| `corpus/fixtures/measure_audio.py` | committed blob `7358f13b:` | 45 271 lines | `97ed1b1c586d2d5446f2ae85d1ab158e43b0f7d71edf430c2c5f045ed5299efc` |
| the pulsecli block | lines 41471–43787 | 2 317 lines | `be60f1bae6db9859839ebe2f3daf6938af3bc03f2d7595bdf5c97ac82968b97d` |
| `corpus/fixtures/pulse_r96_probe.c` | committed blob | 383 lines | `fe2c168352144cd66e6977debd84c3ebee80b9ace80c26c4f0bc37d00a8fc64c` |
| archive tar | `git archive 7358f13b` | 3 318 476 800 B | `5a6a10007560163db43881a9e98bfe3a49c123c247f38f42bcb5ffd1b754a6f4` |

Archive checkouts (hardlink copies of the one extract; only the fixture
differs — the probe C's inode/sha is shared and identical in all six trees):
`r96s/base` (pristine), `r96s/f1` (F1), `r96s/f2` (F2), `r96s/f3` (F3),
`r96s/f12` (F1+F2), `r96s/f13` (F1+F3). Folded fixture shas:

| tree | fold set | fixture sha256 | line delta |
| --- | --- | --- | --- |
| `f1` | F1 (C5) | `c78942e6911a523328918cf4121467ff50857a76206a9a947e3855f4b6a096a9` | −2 |
| `f2` | F2 (C4 repair) | `a1938e40411685d9897c5470e04607a41b1fc368e5895b10df7d0429cb716e12` | +2 |
| `f3` | F3 (C4 delete) | `65fb58d68a2b3d34bdcf944e0e36701b230458e5d0176546c9d5a3ff821eabae` | −7 |
| `f12` | F1+F2 | `014dc69d06a1090854f8e7946038dd72e5cdd2c1cb74ae9202ae8aa6d645f1d2` | 0 |
| `f13` | F1+F3 | `0d34655fd7c8ae6d941e7b50dbb8c96ec2d96bf55bdbc9a084511fb8336d1246` | −9 |

`fold_apply.py` is exact-string with occurrence asserts (every anchor asserted
to occur exactly once) and unlink-then-create writes, so a folded fixture can
never be written *through* a hardlinked inode (the first draft of the script
did exactly that and was corrected before any run — the trees' shas in the
table above are the post-correction values). All six variants pass
`py_compile` and `ast.parse` (`fold-apply.log`).

**HEAD-landability check.** On `d41cfa68`'s bytes (the r98 landing), all four
fold anchors still occur exactly once and the F1+F2 application yields
`headcheck-f12.py` sha `cf0c00a1…` with delta 0 — the queued folds are still
landable after the r98 landing, and the r96 block bytes they touch are
unchanged.

**Custody.** Entry and exit `git status --porcelain --untracked-files=no` are
byte-identical (` M corpus/fixtures/measure_audio.py`,
` M reports/round-90/r90-author.md` — both foreign, untouched); the audited
blobs hash equal at entry and exit (`entry-state.txt`, `exit-state.txt`). No
`pactl set-default-*` was issued; the probe's own null sink was name-verified
unloaded and censused (`sink_gone: true`, `own_nodes_after: []`); the family
lock was read/created only inside the archive checkouts.

## 2. Fold targets and the reference census (literal fallback)

**Target F1 (critic C5, reviewer R5).** The two `_attr_leg` calls at committed
lines 42979–42980:

```python
        _attr_leg("t_proc_lat_a", 2, latency_ms=100, process_ms=5)
        _attr_leg("t_proc_lat_b", 2, latency_ms=100, process_ms=5,
                  extra=())
```

`extra=()` is the parameter's own default (`_attr_leg(name, reps, fmt="s16le",
channels=1, latency_ms=None, process_ms=None, env_raw=None, extra=())`), so
the two calls build the identical argv/env/tone and the identical prediction:
four legs for one cell, and the family's "16 flag/env/frame cells" prose is 15
cells. AST literal-cell census: base has 16 cells including both
`t_proc_lat_a`/`t_proc_lat_b`; f1 has 15 (`census-base.txt`, `census-f1.txt`).
The receipt proves it byte-wise: in base1, `t_proc_lat_a__r1.argv ==
t_proc_lat_b__r1.argv` (byte-equal), `env_keys` equal, `predicted` equal,
`attrs_after_resnapshot` equal (assertions PASS, `eff-f1.json`).

**Target F2/F3 (critic C4, reviewer R4).** The two committed `_pulsecli_r96_row`
call sites keyed on pid `0`:

- 43000 `_bad_spec` (`t_f32le_invalid`): `leaf["row"] =
  _pulsecli_r96_row_view(_pulsecli_r96_row("sink-inputs", 0))` — a recorded
  witness that reads `null` in every receipt;
- 43135 `_malformed` (`p_malformed`): `if _pulsecli_r96_row("sink-inputs", 0)
  is not None:` — a failure branch whose message claims the no-stream witness.

AST call-site census (`census-base.txt`): `_pulsecli_r96_row` has 4 call sites
— `proc.pid` ×2 (42005 `_stream_leg`, 43250 the cork leg) and `0` ×2 (the two
above). The helper stays live after either fold; no other name is touched.
Grep fallback for the target names across the landing commit, the untracked
seat artifacts and the verifier's law set is in §8.

## 3. Fold F1 (queued) — drop the byte-equivalent duplicate cell

```
-        _attr_leg("t_proc_lat_b", 2, latency_ms=100, process_ms=5,
-                  extra=())
```

−2 lines, no replacement, no new name. Census 178 → 176 (41/27/66/20/22);
`late_attr_census.legs` 66 → 64; every other leg, law and armed value
unchanged (base1→f1 normalized diff: **143 diffs = 142 duplicate-leg leaves +
1 census, 0 residual**; 19/19 intended-effect assertions PASS). The round's
verifier law set re-derives the folded receipt with exactly the bookkeeping
constants updated (§5.3).

## 4. Fold F2 (queued) / F3 (held alternative) — the dead pid-0 predicate

The critic's and reviewer's smallest safe correction is the pid-keyed repair;
F3 is the pure deletion. Both are proven here; the report queues **F2** and
holds **F3** with its tradeoff named.

### F2 — re-key the two lookups to the leg's own child pid (queued)

```diff
     except OSError as exc:
         rec["spawn_error"] = str(exc)[:160]
         return rec
+    rec["pid"] = proc.pid
     t0 = time.monotonic()
```

```diff
-            leaf["row"] = _pulsecli_r96_row_view(
-                _pulsecli_r96_row("sink-inputs", 0))
+            leaf["row"] = _pulsecli_r96_row_view(
+                _pulsecli_r96_row("sink-inputs", leaf.get("pid")))
```

```diff
-            if _pulsecli_r96_row("sink-inputs", 0) is not None:
+            if _pulsecli_r96_row("sink-inputs",
+                                 leaf.get("pid")) is not None:
                 leaf["failures"].append(
-                    "an index-0 sink-input exists while the malformed "
+                    "a sink-input for this leg's pid exists while the "
                     "property leg ran — the no-stream claim is "
                     "unwitnessed")
```

+1 line in `_pulsecli_r96_run`, two call sites re-keyed. `rec["pid"] =
proc.pid` is the existing r84 convention (`_alsapw_r84_prop_leg`, committed
line 20527) and the r96 family's own convention is already pid-keyed
(`_stream_leg` and the cork leg look up `_pulsecli_r96_row(what, proc.pid)`);
no second convention is introduced. Effect: 49 `pid` keys in the f2 receipt
(44 inside leg leaves, incl. the two `a_version` sub-runs, + 5 entry
`server_gate` leaves); `t_f32le_invalid`'s recorded `row` stays `null` — but
now as a live lookup that found no stream; the `p_malformed` rc-1 +
`pulse_invalid_property` half is untouched (8/8 assertions PASS).

### F3 — delete both dead lookups (held, weight-first)

−7 lines (the 5-line `_malformed` branch and the 2-line recorded lookup). The
receipt loses exactly the two constant-`null` `row` keys and nothing else
(base1→f3: **4 diffs = the 2 removed `row` keys + 2 foreign-subscribe-event
digests, 0 unexplained**; 7/7 assertions PASS). **Held** because it leaves the
round's verifier law `t_f32le_invalid__r{rep}.no_row` permanently vacuous
(`(leaf.get("row") or {}).get("index") is None` passes on an absent key), and
it withdraws the `p_malformed` no-stream claim instead of re-arming it — the F
axis the critic filed the finding under. If the round's axes weight line count
over the live witness, F3 is the proven alternative (−9 lines combined with
F1, `f13`).

### Why the pid-0 predicate is not merely dead — it is misdirected (§6)

The probe shows a client **can claim pid 0**: `pacat
--property=application.process.id=0` lands a row whose
`application.process.id == "0"` on this host (`pid_census` `[…, [136970,
'0']]`), and the old predicate **matches it** (`row_pid0_found: True`) while
never matching the leg's own stream. So the old branch could only ever fire on
a foreign forgery — a false red — never on the leg it claims to witness. The
repaired form keys on the leg's real pid and is immune (the forged row does
not carry that pid).

## 5. Fresh before/after batteries (live, archive checkouts under /home)

Seven batteries, each from the tree named, each with the pinned sha256 of the
bytes it ran, serialized, with a foreign-same-family census before and after
every run (`run_batteries.sh`, `run-log.txt`; no foreign
`--probe-pulsecli-r96` process was live at any start or end, `waited=0s`).

| tag | tree | fixture sha (12) | start→end (UTC) | wall | rc | legs | failures | blocks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base1 | base | `97ed1b1c586d` | 10:23:58→10:26:21 | 143 s | 0 | 178 | `{}` | 2 |
| f1 | f1 | `c78942e6911a` | 10:26:21→10:28:43 | 142 s | 0 | 176 | `{}` | 2 |
| f2 | f2 | `a1938e404116` | 10:28:43→10:31:13 | 150 s | 0 | 178 | `{}` | 3 |
| f12 | f12 | `014dc69d06a1` | 10:31:14→10:33:36 | 142 s | 0 | 176 | `{}` | 2 |
| base2 | base | `97ed1b1c586d` | 10:33:36→10:35:59 | 143 s | 0 | 178 | `{}` | 2 |
| f3 | f3 | `65fb58d68a2b` | 10:35:59→10:38:22 | 143 s | 0 | 178 | `{}` | 2 |
| f13 | f13 | `0d34655fd7c8` | 10:38:22→10:40:45 | 143 s | 0 | 176 | `{}` | 2 |

The two named blocks in every green run are the author's own
`e_native_corked` rep 1/2 (the cached-`dev_info` disagreement). **f2's third
block is a host anomaly, not a fold effect**: `c_source_missing rep 1` hung to
the 8 s wall cap (the author's own disclosed anomaly class — "in the first dev
run one of two capture-miss reps hung"), recorded as a named coverage block;
the same leg is green in base1/base2/f12/f3/f13 (and the author/verifier/critic
windows saw 3/3 refusals). It is the only run where the verifier's
`capture_miss_census` law (`measured == refused + hung == 3`) fails — the law
is not hang-tolerant; reported as evidence, not as a fold effect.

### 5.1 The control pair

`base1 → base2` (identical bytes, identical tree): **0 normalized diffs**
(`cmpN-base2.txt`). Every volatile class the normalizer maps away is a class
that varies between identical runs; nothing else does.

### 5.2 Pair comparison (normalized, path-driven)

The comparator normalizes only named volatile classes by path (per-run
namespace/pid, server indices, module ids, wall times, recorded text tails,
race/foreign censuses, bounded witness counts) and compares everything else
exactly — every armed value, every predicted/measured attr, every rc/class,
every census list, every receipt key, and every key's *presence*. Raw
(un-normalized) views are also produced (`cmp-*.txt/json`).

| pair | kind | normalized diffs | intended | residual |
| --- | --- | --- | --- | --- |
| base1 → f1 | C5 | 143 | 143 (142 leg leaves + 1 census) | **0** |
| base1 → f2 | C4rep | 58 | 49 (`pid`) | 9 = the hang class (8) + one foreign `remove` event in the subscribe digest (1) |
| base1 → f12 | C5+C4rep | 192 | 192 (142 + 1 + 49) | **0** |
| base1 → f3 | C4del | 4 | 2 (the two removed `row` keys) | 2 = the same foreign-subscribe digest class |
| base1 → f13 | C5+C4del | 145 | 145 (142 + 1 + 2) | **0** |
| base1 → base2 | control | 0 | — | **0** |

The two residual classes are named host state: (a) the `c_source_missing`
hang, a named coverage block; (b) one `Event 'remove' on source-output` line
in a rep's subscribe digest — the **armed** subscribe fields are identical in
base1 and f2 (`changes_at_uncork == 1`, `new_events == 1` in all reps;
`foreign_sink_input_events` is a recorded count: 24/20 vs 17/14). Both classes
appear in folded and pristine trees alike and in neither case touch an armed
value.

Raw view as a second check (`cmp-*.txt/json`): the curated armed surface
(per-leg verdict-bearing keys, normalized) differs **only** where intended —
f1/f12/f13: the removed `t_proc_lat_b` legs' armed leaves (30 missing, 24 of
them also non-`None` value diffs) and nothing else; f2: the 5
`c_source_missing__r1` hang fields; f3: 0; control: 0.

### 5.3 The round's own law set on the folded receipts

The verifier's `r96v_laws.py` (sha256 `a5b87585…`) re-derives every r96 leg
from recorded fields only. Run as-is and with exactly three bookkeeping edits
(declared leg census 68→66, the `t_proc_lat_b` table row dropped,
`late_attr_census.legs` 66→64 — `r96v_laws_folded.py`):

| receipt | law set | legs | laws | PASS | FAIL | BLOCKED |
| --- | --- | --- | --- | --- | --- | --- |
| base1 | as-is | 178 | 509 | 507 | 0 | 2 |
| base2 | as-is | 178 | 509 | 507 | 0 | 2 |
| f1 | as-is | 176 | 507 | 499 | **6** | 2 |
| f1 | 3 edits | 176 | 505 | 503 | 0 | 2 |
| f2 | as-is | 178 | 508 | 503 | **2** | 3 |
| f12 | 3 edits | 176 | 505 | 503 | 0 | 2 |
| f3 | as-is | 178 | 509 | 507 | 0 | 2 |
| f13 | 3 edits | 176 | 505 | 503 | 0 | 2 |

The 6 as-is failures on f1 are exactly the bookkeeping the fold moves
(`struct.…legs` 66≠68, `struct.total_legs` 176≠178, `t_proc_lat_b__r{1,2}`
missing, `late_attr_census.legs` 64≠66, and the derived
`receipt.failures_agree` that follows from them). The 2 failures on f2 are the
host hang's (`capture_miss_census`, plus the derived
`receipt.failures_agree`). With the three edits the folded receipts are
**0 FAIL** on the same law surface — and F3/F13 keep the *as-is* law set green
(F3 changes no census value).

## 6. The C4 probe (narrow, decisive; run twice)

`probe_c4.py` (receipts `probe-c4.json`, `probe-c4-run2.json`) imports the
**archived base and folded modules themselves** and exercises the predicate;
run 1 on base+f2, run 2 on base+f3 — both reproduce every line:

| observation | result (both runs) |
| --- | --- |
| helper source identical in base and folded | `True` |
| a live `pacat` stream on a seat null sink: `_pulsecli_r96_row("sink-inputs", <child pid>)` | returns the row (`app_pid` = the child's pid) — the pid-keyed form is **live** |
| same moment: `_pulsecli_r96_row("sink-inputs", 0)` | `None` — the pid-0 predicate cannot witness even a live stream |
| pid census while live | `[[136904, None], [136928, None], [136952, '1187199']]` — no row carries `0` |
| the exact `p_malformed` command (family's own `_run`) | rc 1, class `pulse_invalid_property`; watched by pid: pid-0 `None`, pid-keyed `None` (no stream created — the repaired predicate passes) |
| forgery control: `--property=application.process.id=0` | the forged row **lands** (`[136970, '0']`); `_pulsecli_r96_row(…, 0)` **matches it**; the same client's real pid does **not** match — the old predicate is misdirected, the repaired one immune |
| teardown | name-verified unload (`verified_index == captured`, `recycled: False`, rc 0); sink gone; `own_nodes_after: []` |

## 7. Preserved contract (what a landing must not lose)

1. All 5 entries and every leg stay wired in `main()` (`--probe-pulsecli-r96`),
   with the fixed-path family lock and the `r96a_<pid>` namespace.
2. Every armed law and armed value is unchanged; F1 removes one duplicate
   cell, F2 changes no expected value, no band, no law name, no law order.
3. Every recorded receipt field survives except the one duplicate cell's
   leaves (F1) — F2 *adds* the recorded `pid` key, it removes nothing.
4. The `t_f32le_invalid` `row` value stays `null` under F2 (now a live lookup);
   under F3 the key disappears and the round's `no_row` law stays vacuously
   green — the tradeoff that holds F3.
5. Nothing in this report edits another seat's artifacts; the folded fixtures
   exist only in the archive checkouts. The author/reviewer prose ("178 legs",
   "16 cells", the `p_malformed` "with no stream") becomes historical, and the
   verifier's law-set constants are the named downstream update.

## 8. Deletion-candidate census (literal fallback) and the stop condition

Grep fallback for the target names across the landing commit
(`git grep … 7358f13b`), the untracked r96 seat artifacts, the reviewer's
report and the verifier's law set: `t_proc_lat_b` occurs only in the fixture's
two `_attr_leg` calls (the landing), the critic's byte-copies (derived), the
seat receipts (historical evidence) and the verifier's `r96v_laws.py`
(`ENTRY_LEGS` + `attr_cells` + `late_attr_census` law — the named downstream
consumer); `sink-inputs", 0` occurs only in the fixture's two dead lookups and
the critic's copies; `late_attr_census` is written once in the fixture and
read by the verifier's law set and the author's prose.

| candidate | proof | why held / queued |
| --- | --- | --- |
| `t_proc_lat_b` (F1) | AST cell census + byte-equal argv/predicted/measured | **queued** (−2); consumers: the verifier's law table/census constants (§5.3) — a named downstream update, not a caller |
| the two pid-0 lookups (F2/F3) | AST call-site census; probe (§6) | **F2 queued** (+1 line, 2 re-keyed sites); **F3 held** (F-axis tradeoff) |
| `t_proc_lat_a` name | now the only `t_proc_lat*` cell | held: a rename churns every receipt key and the verifier's law names — and a rename is exactly what the missing `lsp` device would have to prove |
| `tap_exit_code` (43304) | AST: 1 store, **0 loads**; nothing reads it | held: recorded-not-armed evidence — deleting it costs the receipt surface the reviewer diffs against |
| never-overridden helper defaults (`_pulsecli_r96_run(cwd=…)`, `_kill(term_wait_s)`, `_stream_leg(need_link)`, `_client_run(snapshot_hz)`, `_teardown(players)`, `_block(players)`, `_tone(rate)`, …) | AST call-site/keyword census | held: defaults, not dead code; `players` is the r89/r90 twin's own parameter shape (`_pwprof_r89_teardown(…, players=())`, `_wpstate_r90_teardown(…, players=())`) — deleting it here would create a second helper shape |
| `pulse_r96_probe.c` dead knobs (`--attr-mode`, `--amp`, `--server`) | the harness never passes them (grep) | out of the granted scope (a different file; the critic's own minor note) — reported, not folded |

**Stop condition reached.** The next deletion inside the block would harm an
axis: the remaining weight is (a) recorded-not-armed evidence
(`tap_exit_code` and the recorded witnesses generally), whose removal costs
the receipt axis, and (b) helper defaults/branches shared with the r84–r90
families, whose removal costs the convention axis. Beyond F1/F2 (or F1/F3) the
pulsecli block has no dead path, no unreferenced helper and no duplicate
authority left that can be removed without paying one of those two axes.

## 9. Evidence index

Under `/home/vgpnk/Projects/shokunin/r96s/` (archive checkouts, receipts,
scripts, logs; the big tree + receipts stay there) and copied small under
`corpus/live/r96-simplifier/`:

| file | what it is |
| --- | --- |
| `fold_apply.py`, `fold-apply.log` | the folds, occurrence-asserted, unlink-then-write; per-variant sha/line delta/py_compile |
| `census.py`, `census-{base,f1,f2,f3,f12,f13}.txt` | AST cell + call-site + load census (literal fallback) |
| `probe_c4.py`, `probe-c4.json`, `probe-c4-run2.json` | the C4 narrow probe ×2 (deadness, liveness, forgery control, teardown) |
| `run_batteries.sh`, `run-log.txt`, `{base1,f1,f2,f12,base2,f3,f13}.{out,err}` | the 7 batteries: tree, sha, rc, receipt, foreign census, load |
| `compare_norm.py`, `cmpN-*.txt/json` | normalized pair comparator + one receipt per pair |
| `compare_runs.py`, `cmp-*.txt/json` | raw leaf-diff view + normalized armed projection |
| `assert_effects.py`, `eff-*.json` | intended-effect assertions per pair |
| `r96v_laws_folded.py`, `r96v_laws.orig.sha256`, `laws-*.txt` | the round's law set as-is and with the 3 bookkeeping edits |
| `entry-state.txt`, `exit-state.txt`, `headcheck-f12.py` | shared-tree entry/exit state, audited blob shas, HEAD-landability check |
