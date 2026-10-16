# r90 SIMPLIFIER — proven folds in the wpstate / wplink / wpformat block (f50cf66a)

**Seat** simplifier (r90) · **host** plazir27 (devin substrate) ·
**scope** the r90 landing only — `git show f50cf66a -- corpus/fixtures/measure_audio.py`
(**+2183/−3**): the insertion-only family block (`ROUND 90` banner → end of
`wpformat_r90_entry`, lines **35554–37709**, 2156 lines, 4 entry functions,
60 legs) plus its wiring (argparse row, mutex token, `mode`/`suffix` ternary
entries, the 20-line dispatch block in `main()`).

**Writes**: this report + `corpus/live/r90-simplifier/` (scripts, censuses,
run logs, 9 batteries' receipts, comparison receipts) + the archive
checkouts under `/home/vgpnk/Projects/shokunin/r90s/`. **Zero tracked
writes, no commit, nothing landed.** The folds exist only inside the archive
checkouts.

## 0. Axes named for this gate

| axis | direction | what would harm it |
| --- | --- | --- |
| weight | fewer symbols / lines / dead paths in the fixture | — |
| evidence fidelity | the 60-leg receipt surface, the armed laws, and the round's provenance comments stay intact | deleting a law, a leg, a recorded claim, or a historical note; editing the receipt surface |
| convention consistency | one authority per job; the r8x/r9x family-local helper shape (a wrapper mirrors its parent) | inventing a second form of an existing helper; diverging a wrapper from its parent's signature |
| proof cost | a fold must be provable by a fresh before/after battery on this host | a fold whose proof needs a new measurement, a mutant, or a new leg |

## 1. Custody / tree state

- **Analysis base** = the commit-pinned blob
  `git show f50cf66a:corpus/fixtures/measure_audio.py`, sha256
  **`d3119c5d88228349b54996e23978cf726d59bfc615739838177a5a5e14551154`**
  (39 093 lines, 1 960 884 B). The r90 block itself is lines 35554–37709,
  sha256 **`8279f05901b737d08a481640c2d4aeda9c6a3b49c415fd271a972d27c1b0096b`**.
- **The shared tree MOVED under this seat**: HEAD advanced
  `f50cf66a` → `d78f1cc9` (r91) → `ccbce758` (r92) → `7358f13b` (r96) →
  `b8ff4efc` (r97) during the window. Checked: the **r90 block is
  byte-identical in f50cf66a and b8ff4efc** (same 2156-line span, same
  sha256), and both fold patches still apply **exactly once** on HEAD's
  bytes (`r90s/headcheck-f1`, `r90s/headcheck-f2`). The working tree's
  fixture is byte-identical to `HEAD`'s blob
  (`7a070fa817c4de6f4ae5eb5be38e7cfc2cdbb18cad605ee52427afcf0a6ca2bc`,
  `git diff` clean) — **this seat touched no tracked file**.
- **Archive checkouts under `/home`** (`git archive f50cf66a | tar -x`):
  `r90s/base` (pristine), `r90s/f1` (base + fold 1), `r90s/f2` (base +
  fold 2). Each fold script asserts its own occurrence counts, so a drifted
  tree refuses instead of folding something else.
- **No `lsp` device answers this tree.** The seat's tool surface exposes no
  language-server session, and the only MCP server on this substrate is
  `rea` (a Ghidra native-binary provider — no Python source semantics, no
  `references` verb). **Recorded unavailable.** Every "no callers" claim
  below is a **literal fallback** — an AST load/call-site census over the
  whole 39 093-line module plus `grep` — and is labelled as such, never
  presented as semantic proof. No rename is proposed or performed: renaming
  is exactly the class of change that would need the device.
- **Provenance preserved.** No comment line of the r90 block was deleted:
  the `ROUND 90` banner, the boundary-correction notes, the "recorded,
  never armed" notes and the r84 F1 fixed-path lock note are byte-identical
  in `f1`/`f2` (see the diffs in §2/§3 — they are the only hunks).
- **A sibling wave was live throughout** (r91/r92/r96/r97/r98/r100 seats,
  and an independent r90 verifier + r90c seat). Every battery's receipt
  records its own contention census; the host-noise controls in §5 are what
  make the pairs readable.

## 2. Fold 1 — delete `_wpstate_r90_edges_out` (dead alternate path)

`base` lines 35943–35945:

```python
def _wpstate_r90_edges_out(g, name):
    return [e for e in _wpstate_r90_edges(g) if e.get("out_node") == name]
```

**Deletion evidence (literal fallback — `lsp` unavailable, §1).**

| probe | result |
| --- | --- |
| AST load census over the whole module (`census-base.txt`) | `_wpstate_r90_edges_out` **loads = 0, call sites = 0** — the only module-level name in the 72-name r90 region with zero loads |
| call-signature census (`callsig.py`) | 0 call sites of any arity |
| `grep -n "_wpstate_r90_edges_out" corpus/fixtures/measure_audio.py` | **1 hit — the `def` line itself** |
| dynamic-name dispatch (`globals()`, `getattr`, `eval`, string-built `_wpstate_r90_edges_{…}`) | none in the module — the static census is the whole story |

Its twin `_wpstate_r90_edges_in` (same 2-line shape) **is** used 5×. The
pair is the r85 convention copied in (`_pactlmon_r85_edges_in` /
`_pactlmon_r85_edges_out`, both live in r85); the r90 copy of the *out* half
is unreachable — a dead alternate path, not a missing one.

**Fold shape** (`r90s/f1`, sha256
`ada9627341eba884fad94f3073ed1e3097f40e9e850040892ed401758d109f98`,
39 089 lines / 1 960 770 B):

```diff
@@ -35940,10 +35940,6 @@
     return [e for e in _wpstate_r90_edges(g) if e.get("in_node") == name]
 
 
-def _wpstate_r90_edges_out(g, name):
-    return [e for e in _wpstate_r90_edges(g) if e.get("out_node") == name]
-
-
 def _wpstate_r90_own_links(g, names):
```

5 lines removed, no replacement, no new name.

## 3. Fold 2 — drop `count()`'s dead second return and four dead bindings

Inside `wplink_r90_entry` (the only place `count()` exists):

```python
        def count():
            g = _wpstate_r90_graph()
            return len(_wpstate_r90_own_links(g, own)), g      # <- `g` dead
```

`count()` is called 10×, always as `n, _g = count()`, and **`_g` is never
read** (AST "locals assigned but never loaded" census over the function —
`dead-base.txt`; the graph object is only ever used to count the own link
set). Three more bindings in the block are assigned and never read:

| site | base line | binding | why it is dead |
| --- | --- | --- | --- |
| `w_pulse` | 36539 | `t_row, val_row, _ = _wpstate_r90_store_poll(skv)` | `val_row` never read; the leg records `t_row_s`, and the fresh-key guard lives in `entry["key_pre"]` |
| `w_optout_stream` | 36816 | `proc_y, argv_y = _wpstate_r90_play(…)` | `argv_y` never read (the *opt-out* stream's argv is the recorded one) |
| `k_t_live` | 37444 | `proc, argv = _wpstate_r90_play(tag, L2, t48)` | `argv` never read |

**Fold shape** (`r90s/f2`, sha256
`074cfdf0de1975c62740fd5a4e099f7baff1c6c7f8b9411abdf33e25d09055c1`,
39 093 lines / 1 960 827 B; 5 hunks, 14 lines changed): `count()` returns
the count only; the 10 call sites become `n = count()`; the three bindings
become `_`. **No recorded key changes** — the legs, the receipt keys and the
armed laws are untouched.

## 4. Preserved contract

| item | base | f1 | f2 |
| --- | --- | --- | --- |
| module-level names in the r90 region | 72 | 71 | 72 |
| `python3 -m py_compile` | rc 0 | rc 0 | rc 0 |
| entry functions (4) / dispatch rows (4) / receipt names | present | present | present |
| leg census per entry | 15 / 15 / 24 / 6 = **60** | 15/15/24/6 | 15/15/24/6 |
| `ROUND 90` banner + every law/provenance comment | — | byte-identical | byte-identical |
| wiring (argparse row, mutex token, `mode`/`suffix`, dispatch block) | — | untouched | untouched |

## 5. Fresh before/after batteries (live, archive checkouts under /home)

Nine batteries were run, each from the tree named, each with the pinned
sha256 of the bytes it ran. Runner: `run_pairs.sh` / `run_pairs2.sh` /
`run_pairs3.sh` (same-family exclusion is a **fixed per-tree path**, so a
sibling seat in another tree is *not* excluded — the runners therefore wait
for a 20 s window with no other `--probe-wpstate-r90` process and log the
census on both sides of every run; raw log: `run-log.txt`).

| tag | tree | fixture sha256 (12) | start (UTC) | rc | `m_phantom` | store entry |
| --- | --- | --- | --- | --- | --- | --- |
| before1 | base | `d3119c5d8822` | 10:00:12 | 0 | ok | ok |
| after1 | f1 | `ada9627341eb` | 10:01:31 | 1 | **rc 1** | ok |
| before2 | base | `d3119c5d8822` | 10:02:51 | 0 | ok | ok |
| after2 | f2 | `074cfdf0de19` | 10:04:11 | 0 | ok | ok |
| after1b | f1 | `ada9627341eb` | 10:05:38 | 1 | **rc 1** | ok |
| before3 | base | `d3119c5d8822` | 10:06:57 | 1 | **rc 1** | ok |
| after1c | f1 | `ada9627341eb` | 10:09:01 | 0 | ok | ok |
| after1d | f1 | `ada9627341eb` | 10:10:23 | 0 | ok | ok |
| before4 | base | `d3119c5d8822` | 10:11:47 | 1 | **rc 1** | **2 timing laws** |

### 5.1 The pairs, and what actually differs

Each pair is compared by `compare_runs.py`: it projects both receipts onto
their **law surface** (every armed field the round's report cites — rcs,
error classes/hits, sha12s, byte counts, link/row counts, the fresh-key
guard, the row field splits, the teardown census, the unload rc/field/value)
with every pid / nonce / module index / link id / object serial / wall time /
sample / foreign-seat object normalized away, and prints the **changed
leaves** out of the ~915 projected leaves per run (`changed-leaves.txt`).

| pair | kind | changed leaves | classes |
| --- | --- | --- | --- |
| before2 → **after2** | **FOLD-2 primary pair** | **0 / 914** | — (both batteries green) |
| before2 → **after1c** | **FOLD-1 primary pair** | **1 / 914** | `m_phantom.id_recycled_by_foreign` (recorded, unarmed) |
| before1 → **after1d** | **FOLD-1 second pair** | 5 / 914 | `f_post.node_format` stderr tail (4) + the same recycling witness (1) |
| before2 → after1 | FOLD-1, race firing | 17 | the `m_phantom` race (7) + the `k_reset` drop race (10) |
| before1 → before2 | **CONTROL** pristine vs pristine | 14 | `f_post` stderr tail (4) + `k_reset` drop race (10) |
| before2 → before3 | **CONTROL** pristine vs pristine | 7 | the `m_phantom` race (7) |
| before3 → before4 | **CONTROL** pristine vs pristine | 13 | `k_reset` drop race (10) + store timing laws (3) |
| after1c → after1d | **CONTROL** folded vs folded | 10 | `k_reset` drop race (10) |

**Reading.** Every leaf that differs in a fold pair is an instance of a
class that also differs between two runs of *identical bytes* — and the
identical-bytes controls carry **more** variation (14 and 13 leaves) than
either fold pair. Concretely:

- `m_phantom.id_recycled_by_foreign` is the leg's *recycling witness*
  (recorded, never armed — the boundary itself declares module indices
  recycled immediately). It reads `True` in the pristine trees too
  (verifier 2/2, r90c 1/1 of their green runs), so the fold-1 residual is
  host state, not fold state.
- `f_post.node_format` stderr carries a transient
  `res:-2 (No such file or directory)` tail in some runs while the armed
  `sha12` stays at the boundary value — it flips between two pristine runs
  as well.
- `k_reset.drop[0]/[1]` records *which* of the two `pw-link -d` calls lost
  the race with the previous legs' link teardown; the armed post-condition
  (`own_links == 2`) holds in every run.

### 5.2 Host-fragile laws (recorded, not this seat's verdict)

The same battery census over **all 16 distinct r90 batteries in the window**
(this seat's 9 + the independent r90c seat's 2 + the verifier's 5) —
`flake-census.txt`:

- **`m_phantom` load rc ≠ 0 in 5 of 16 batteries**, including **3 of the 8
  pristine-tree batteries** (r90c 09:56:15 — concurrent with the verifier's
  v1; my base 10:07:44; my base 10:12:34). The failure is
  `rc 1 / "Failure: Unknown error code"` on
  `pactl load-module module-tunnel-sink server=127.0.0.1:1` — a race between
  the unreachable tunnel's connect failure and the module registration.
  It is **not fold-attributable**: the two pristine trees fail it, and the
  leg's executed bytes are identical in base and f1 (the fold removes a
  symbol nothing calls).
- **Store timing laws also fail on pristine bytes**: my before4 battery
  (pristine `d3119c5d…`, 10:11:47) reports `w_props: … landed at 3.282 s,
  outside the coalescing band [0.5, 3.0]` and `w_optout_stream: the control
  stream wrote no row in the same window — the opt-out leg is vacuous`. The
  host was carrying 3–8 sibling fixture batteries per receipt
  (`contention.fixture_runs`).
- `w_vanished_target.outcome` = `fallback_to_default` in **16/16**
  batteries (the author's window and the boundary saw `no_link` too) — the
  class is stable in this window, which is what a *recorded* class is for.

I report these as evidence, not as a verdict: they are the reason every
fold pair is read against its identical-bytes control rather than against
`rc == 0`.

## 6. Deletion candidates found but NOT landed

Each is proven dead by the same literal fallback census; none is landed,
because the next deletion would harm an axis. The counts are from
`callsig.py` on the pinned bytes.

| candidate | proof of deadness | why not landed |
| --- | --- | --- |
| `_wpstate_r90_run(env=None, wd=None)` | 33/33 call sites pass 2 positional args; kwargs ever used = `keep_chars` (1), `keep_raw` (4) | deletes a *capability*, and diverges the helper from the r89 parent `_pwprof_r89_stream(wd=…, env=…)`; weight gain = 2 params |
| `_wpstate_r90_stream(sig_at, sig, keep_raw, sample_ts, watch)` | 4/4 call sites pass 2 positional args + `keep_chars`/`hooks` | this wrapper's job is to *mirror* its parent's signature; deleting the mirror is a convention change for 2 lines |
| `_wpstate_r90_pwlink(args, timeout_s=10.0)` | 14/14 call sites pass 1 positional arg | one parameter; the default is the family's timeout convention |
| `_wpstate_r90_store_poll(step_s=0.05)` | 8/8 call sites pass 1 positional arg (+ `want` ×4) | one parameter |
| `_wpstate_r90_block(players=())` | 10/10 call sites pass 3 or 4 positional args | the r89 twin `_pwprof_r89_block(…, players=())` carries the same parameter — deleting it here would *diverge* from the twin |
| `_wpstate_r90_loopback_arm(sources, sinks)` | 2/2 call sites pass byte-identical argument tuples — one instantiation | folding it hoists a new module-level name to save two argument lists (weight-neutral at best) |
| the three `"pre": None` fields (`w_create`, `w_pulse`, `w_target`) | constant-None; no writer after construction (AST store census finds no `["pre"]` assignment) | deletes 3 **receipt keys** — the artifact a reviewer diffs against the author's receipts; the fresh-key guard's real record is `entry["key_pre"]` |
| `wplink_r90_entry` / `wpformat_r90_entry` vs their `*_probe` receipt names | name drift only | a rename; the r90 author report cites both names (§3, §4 and its receipt table), and no `lsp` device answers this tree |
| `_wpstate_r90_pwlink_links` bypassing the `_wpstate_r90_pwlink` wrapper | two forms for "run `pw-link`" | not a fold: the raw form needs `keep_raw=True`, which the wrapper does not forward — folding would *add* a parameter |
| `_wpstate_r90_norm` vs `_pwprof_r89_norm` | not duplicates (`<mid>`/`<seq>` vs the r88 classes + `<ns>`) | nothing to delete; the family-local scrubber is the convention |

## 7. Stop condition

The next deletion would harm an axis: the parameter surface (§6 rows 1–5)
buys a handful of tokens at the price of a capability or a divergence from
the r89 twin, the `"pre"` fields buy 3 keys at the price of the receipt
surface, and the name drift is a rename the seat may not prove without the
`lsp` device. Fold 1 and fold 2 are the two deletions whose weight gain is
real and whose proof is a fresh before/after pair. I stop here.

## 8. Evidence index (`corpus/live/r90-simplifier/`)

| file | what it is |
| --- | --- |
| `fold_apply.py` | the two folds, exact-string with occurrence asserts |
| `census-base/f1/f2.txt` | AST load/call-site census per tree (fold 1's zero-load proof) |
| `dead-base/f1/f2.txt` | AST "assigned but never loaded" census (fold 2's proof) |
| `callsig.py` + output in §6 | call-signature census (never-supplied params) |
| `run_pairs{,2,3}.sh`, `run-log.txt` | the 9 batteries: tree, sha, rc, receipt path, quiet-window census |
| `base.before{1..4}.out`, `f1.after1{,b,c,d}.out`, `f2.after2.out` | raw fixture stdout per battery |
| `compare_runs.py`, `compare_all.py`, `diff_paths.py`, `summary_paths.py` | the law projection + the pair driver |
| `cmp-*.txt` (8 pairs), `summary.txt`, `changed-leaves.txt` | one receipt per pair + the changed-leaf table |
| `flake_census.py`, `flake-census.txt` | the 16-battery `m_phantom`/timing census |

Archive checkouts: `/home/vgpnk/Projects/shokunin/r90s/{base,f1,f2}` (+
`headcheck{,-f1,-f2}` for the HEAD-landability check).
