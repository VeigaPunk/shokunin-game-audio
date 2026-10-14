# R75 simplifier — two duplicate-authority folds + one shadowed-pattern deletion (all byte-identical), the inert `Time:` alternation proven but withheld (re-anchor, not delete); the 910-line r75 arm is otherwise dead-symbol-free

**Seat:** simplifier (delete-and-measure, not subjective trim). Lane: audio. Repo
`/home/vgpnk/Projects/shokunin/audio-shokunin`, host `plazir27`.
**State at measurement (2026-10-14 16:55–17:05 UTC):** HEAD **`db46fba`** (the r75
landing; unchanged through the session), fixture blob sha256
**`13c3c9087ed83b62fbeb7cfa508f87d5c9f37a9b4ee8a72600efae6b58e844ce`** (3812 lines),
committed r75 receipt `corpus/live/runs/20261014T165017429491Z-consumers2-r75`
sha256 **`0829a5986bb6ca70c5c9b06b50bf661e9c8dbbe7cddefac5b16e860e2c2a76d4`**
(byte-identical ×3 per the author). **Deletions made in the shared tree: none** —
write scope is this report + `corpus/live/r75-simplifier/`; every treatment ran in
the scratch tree (`corpus/live/r75-simplifier/tree/`). Shared fixture sha before ==
after (`13c3c908…`), `git status --porcelain -- corpus/fixtures/` empty. No git
mutation, no subagents, no probe run against the shared tree by this seat.
**LSP device — unavailable on this host/task (re-recorded empirically, per seat
card; `lsp-device-record.txt`):** `pyright`, `pylsp`, `jedi-language-server`, `lsp` all
absent; `pygls` and `jedi` not importable. The sole MCP server (`rea`) is the
Ghidra-bound native-binary device: `binary_overview({})` →
`target_unavailable: "No app is open. … call open_binary with its local path"`, and its
reference tools (`procedure_references`, `procedure_callers`, `find_xrefs_to_name`,
`xrefs`) serve loaded native binaries, not this Python source file. No server was
started or queried cold, so no empty cold-start result is recorded as absence. Every
"no callers / unreferenced" statement below is therefore **grep-literal fallback,
explicitly not semantic proof**.
**Prior scratch (dead generation) verified before reuse:** `head-at-start.txt`
(`6f905c3`, fixture `317c0b48…`), `landing-poll.txt` (no landing through 16:10:50Z),
`revisions.txt` (rev1 `317c0b48…`), `dead-symbol-scan-base.txt` (pre-r75 blob clean),
`baseline-*-receipt.json` (pre-landing r73/r74 replays). Reused after verification:
`diff_receipts.py` (jitter-aware comparator), `build_scratch_tree.sh` (rebuilt from
the landed blob; tree sha == landed sha). Replaced: `run_final_proofs.sh` →
`run_proofs.sh` (per-treatment isolation, restore assertions, r73/r74 replays).
**Toolchain (this session):** pacat **17.0-98-gb096** / libpulse **17.0.0**
(daemon live: `PulseAudio (on PipeWire 1.6.8)`, pactl rc=0), aplay **1.2.16**,
ffplay **n9.0.1** (libavformat **63.1.101**), Python **3.14.7**, kernel
**7.2.3-arch1-3**.

## Candidate table (measured)

| # | Site (landed blob) | Change | Byte-identity proof (scratch tree, full `--probe-consumers2-r75`) | Ruling |
|---|---|---|---|---|
| **D1** | `_paplay_fields` pattern 3, `:2027` | delete `r"pa_context_connect\(\) failed: [^\n]+",` (1 line) | **t1** receipt `0829a598…` **byte-identical** to (a) my landed control run and (b) the committed receipt. Shadowing proven on all 7 captured pacat surfaces (§D1) | **Fold** — admissible; bound named below |
| **D2** | `consumers2_ffplay_ops_entry` `:2773` + `:2778` | fold the 2nd copy of `Input #0, …` to `_ffplay_fields(text)["ffplay_detected"]` | **t2** 0 stable diffs vs control; exactly **1** differing leaf, named: `consumer2_paplay_ops_r75_probe.daemon_gate_dead.wall_s` `0.001 → 0.002` (declared jitter, unrelated entry); the whole `consumer2_ffplay_ops_r75_probe` subtree is **deep-equal** | **Fold** — duplicate authority removed |
| **D3** | `consumers2_ffplay_ops_entry` `:2851-2852` | fold the 2nd copy of the `Invalid data found…` literal to `_ffplay_fields(text)["ffplay_invalid"]` | **t3** receipt `0829a598…` **byte-identical** to control + committed | **Fold** — same class as D2 |
| **D4** | `_PACAT_RACY_TAIL` alternation 1, `:2015` | delete `Time:.*Latency:` (inert: `$`-anchored, cannot match the real line) | **t4** receipt `0829a598…` **byte-identical** to control + committed | **Do not fold as a deletion** — the site's correct fold is the re-anchor (F21); preview in §D4 |

Treatments are exact single-occurrence replacements (anchors asserted by
`make_treatments.py`; files `t1-paplay-shadowed-pattern.py` `01080fa6…`,
`t2-ops-detect-fold.py` `3846a60a…`, `t3-ops-invalid-fold.py` `8febeaf6…`,
`t4-inert-time-branch.py` `e8a8a974…`).

### D1 — the `pa_context_connect()` fallback is shadowed on every captured surface

`_paplay_fields` (`:2020-2035`) takes the **first** matching pattern in list order:
`open():` → `Connection failure:` → `pa_context_connect() failed:` →
`Failed to open audio file.`. Evidence (all pacat captures on disk, scribe raw/;
`shadow-proof.txt`):

| capture | bytes | winner idx (full list) | `_paplay_fields` full | without pattern 3 | identical |
|---|---|---|---|---|---|
| `rv-pp-xdg.stderr` | 87 | 1 (`Connection failure:`) | `(None, 'Connection failure: Connection refused')` | same | yes |
| `rv-pp-pulseserver.stderr` | 39 | 1 | `(None, 'Connection failure: Connection refused')` | same | yes |
| `pp2.err` | 87 | 1 | same | same | yes |
| `pp3.err` | 39 | 1 | same | same | yes |
| `np-paplay_v_invalid.stderr` | 27 | 3 (`Failed to open audio file.`) | `(None, 'Failed to open audio file.')` | same | yes |
| `rv-paplay-noise.stderr` | 27 | 3 | same | same | yes |
| `np-paplay_v_valid.stderr` | 700 | none (accept) | `('s16le 1ch 44100Hz', None)` | same | yes |

The only two captures that contain `pa_context_connect() failed:` (87 B, XDG-severed)
also contain `Connection failure:` **first**, so pattern 2 always wins; on the other
surfaces pattern 3 has nothing to match. **ALL IDENTICAL: True** on 7/7. The full
probe treatment t1 then reproduces the receipt byte-for-byte.
**Tradeoff / bound:** a pacat surface that printed *only* the connect line would lose
its `pa_error` fallback. No such surface is observed on pacat 17.0-98-gb096 (4
reject surfaces, 2 spellings); the claim is bounded to observed surfaces. The
`daemon_gate_dead` cell keys on the **tail** (which carries the connect line), not on
`pa_error`, so no gate reads the deleted pattern.

### D2/D3 — the second ffplay parse authority inside the ops entry

`dup_scan.py` finds exactly one duplicated regex in the whole r75 region —
`'Input #0, ([^,\s]+), from'` at `:2185` (`_ffplay_fields`, the declared ffplay
surface parser) and `:2773` (ops driver leg) — and exactly one duplicated literal
worth folding: `'Invalid data found when processing input'` at `:2200` and `:2851`.
Both `:2773` and `:2851` are new r75 lines; folding them to `_ffplay_fields` leaves
one authority per surface and makes future parser edits (e.g. the F18 loglevel
question) propagate to the ops legs. t2/t3 prove the folds change nothing observable
(§proofs). **Tradeoff:** the ops legs now run the full 9-regex parse instead of one
regex — negligible cost, and the coupling is the point.

### D4 — F21 re-confirmed on the landed bytes; the alternation is inert, the tail is the Time line

Regex test on the landed pattern (`shadow-proof.txt` §b/c): the first alternative
`^Time:.*Latency:$` matches **no line** of the 14-line captured valid surface (the
real line is `Time: 0.000 sec; Latency: 200000 usec.` — text follows `Latency:`), while
the other four alternatives each match real lines (`Connected to device…` line 5,
`Stream started.` line 6, `Playback stream drained.` line 12, `Draining connection to
server.` line 13). The committed receipt confirms the effect: **all 8 accepting paplay
matrix arms carry the Time line as `stderr_tail`** (`Time: 0.000 sec; Latency: 34750
usec.`), i.e. the author's stated goal ("a successful leg ends on the negotiated
`Using sample spec …` line") is not reached. Re-anchor preview on the captured
surface (`^Time:.*Latency:.*`):

```
landed      tail = 'Time: 0.160 sec; Latency: 39980 usec.'
re-anchored tail = "Using sample spec <input>', channel map <input>'."
```

so the re-anchor would change 8 receipt leaves (and inherits the F17b stray-quote
residue; the spec line duplicates the `pa_sample_spec` field while the current tail
carries the latency value). **Ruling:** the deletion t4 is receipt-invisible and
proven, but folding it would remove the branch that documents the intended filter and
leave the comment (`:2086-2090`) describing behavior the code does not have. The
correct fold is the author's re-anchor (a receipt change — not a simplifier fold).
**Stability note for the re-anchor decision:** in my window the landed family is
**6/6 byte-identical** (3 committed + my control + 2 sibling runs that appeared in the
shared tree at 16:57:17Z / 16:58:21Z — not this seat's writes); the scribe's F24 flips
were measured in the revision-A/B family, so F21 is latent, not currently materialized.

## Ruled-out candidates (measured reasons)

| Candidate | Reason |
|---|---|
| Extract a shared `run()` timeout closure (3 copies: `:2050`, `:2125`, `:2220`) | The per-leg self-contained closure is the established r73 shape (`pwcat_leg :1045`, `mpv_leg :1098`; r74 `mpv_extent_leg :1549`). Extraction would create a second convention for the same purpose — the r74-D7 ruling (duplication is the contract's measured cost) applies |
| Extract a shared empty-writer cell (3 copies: paplay `:2555-2579`, aplay `:2711-2737`, ffplay `:2831-2863`) / shared name-axis fifo loop (paplay `:2475/:2491`, aplay `:2679`) | Per-entry verbose ops blocks are the convention (r73 ops inlines its own writer-attach cell `:1259+`; the `axis.snd/wav/bin` loop shape already exists in r69/r70 lines `:1387`, `:1852`). The three cells differ on argv, env, parse and tail filter; extraction adds indirection, not authority removal |
| Fold the r75 `daemon_live` pactl block (`:2409-2422`) onto the r73 block (`:1219-1232`) — same two regexes (`^Server Name:`, `^Default Sink:`), same dict | The r73 copy is prior-round frozen; folding would touch prior lines and re-open the insertion-only contract (r74-D7). Recorded as a convention note |
| Delete the bound aliases `CONSUMER_R75_TIMEOUT_S` `:1991`, `CONSUMER_R75_NOWRITER_WAIT_S` `:1992`, `CONSUMER_R75_START_S` `:1994` | The landed r74 fold (`6727fed`) *keeps* the per-round name and re-points its value at the canonical authority (`LAVF_R74_EXTENT_TIMEOUT_S = CONSUMER_R73_TIMEOUT_S`, `:1452`). Deleting the r75 aliases would read prior-round names directly — a second convention |
| Delete `CONSUMER_R75_MEMBERS` `:1990` (alias of `CONSUMER_R73_MEMBERS`) | Per-round member authority is the alias chain convention (`TRANSPORT_R72_MEMBERS = TRANSPORT_R71_MEMBERS`, `CONSUMER_R73_MEMBERS = TRANSPORT_R72_MEMBERS`); it is used once (`:3312`) as the dispatch authority |
| `CONSUMER_R75_SIGTERM_WAIT_S = 1.0` `:1993` | First *named* declaration of the SIGTERM grace window; receipt-visible (`sigterm_wait_s: 1.0`). The r74 cell's literal `1.0` (`:1800`) is prior-round frozen. Convention note only |
| Receipt evidence fields (`pa_error`, `alsa_*`, `ffplay_*`, `avio_*`, `wchan`, `argv`, `waited_s`, `plugin_census.has_*`) | Evidence rows, not dead code (seat card: never delete provenance). Two recorded-but-ungated notes for the verifier: `plugin_census` (`:2623-2629`) is never read by a gate; and the paplay empty-writer cell (`:2555-2579`) is **recorded without a gate** while aplay (`:2737`) and ffplay (`:2863`) both gate theirs — an asymmetry, not a deletion candidate (r74-F2 class) |
| `_nowriter_cell`'s defensive branches (`:2384-2386` finally-killpg, `:2371-2373` stderr-read guard, `:2358-2360` wchan OSError) | Reachable on exception/non-blocking paths; not proven dead. Keep |
| r75 inline `SDL_AUDIODRIVER` key literal `:2766` | Key name for the *varied* axis; the constant `FFPLAY_R75_ENV` (`:1995`) holds the pinned value. No authority duplication |

## Dead-symbol audit (grep-literal fallback — LSP unavailable)

- `scan_dead.py` on the landed blob: **no dead symbols found** (defs, flags,
  module/local constants, locals).
- `refs-landed.txt`: all **20** new r75 symbols have ≥2 whole-file references
  (`CONSUMER_R75_TIMEOUT_S` 19, `_consumer2_tail` 9, `_paplay_fields` 6,
  `_nowriter_cell` 5, …); `CONSUMER_R75_MEMBERS` 2 (def + dispatch), `_PACAT_RACY_TAIL`
  2 (def + use).
- `unused_locals.py` over the r75 window (`:1959-2868`): no unused params/locals.
  (Whole-file hits are prior-round: `pwcat_ops2_entry` throwaway `_` `:1895`, and
  `_alarm`'s signal-API `signum/frame`.)
- `dup_scan.py` (whole file): the only in-r75 duplicate authorities are D2/D3; the
  other regex duplicates (`Detected file format:`, `Found '…' at score=`,
  `Seek failed`, `finished playback` ×2 at `:1133-1137`/`:1598-1601`) and the pactl
  pair are prior-round, frozen by the insertion-only contract.

## Proof harness, receipts, preserved contract

Driver `run_proofs.sh` (asserts tree == landed blob before, and restore == landed
after every treatment). All runs `timeout -s KILL 2400`, inside `tree/`, stderr 0 B:

| run | flag | rc | receipt sha256 (scratch copy) | comparison |
|---|---|---|---|---|
| control | `--probe-consumers2-r75` | 0 | `0829a598…` | **== committed receipt** (byte-identical) |
| t1 | `--probe-consumers2-r75` | 0 | `0829a598…` | byte-identical to control |
| t2 | `--probe-consumers2-r75` | 0 | `a2eb2c73…` | stable projection identical; 1 named jitter leaf (paplay gate `wall_s` 0.001→0.002) |
| t3 | `--probe-consumers2-r75` | 0 | `0829a598…` | byte-identical to control |
| t4 | `--probe-consumers2-r75` | 0 | `0829a598…` | byte-identical to control |
| r73 replay | `--probe-consumers-r73` | 1 (by design; `failures: 2`) | `d684403a…` | vs committed `20261014T154324595001Z` (`ef2647b5…`): **1 stable diff** = `daemon_live.default_sink` `…SPDIF__sink.2` → `…SPDIF__sink` (host-state oscillation: plain at 15:12Z, `.2` at 15:31/15:43Z, plain at 17:01Z — the r74-F3 leaf class) + 2 declared jitter `wall_s` leaves |
| r74 replay | `--probe-lavfsweep-r74` | 0 | `ebddda25…` | **== committed `20261014T153739783116Z-lavfsweep-r74`** (byte-identical) |

Stable projection = full leaf map minus `*.stderr_tail*` and the declared jitter keys
`wall_s / waited_s / live_s / elapsed_s / duration_s_wall` (the tasking's scribe-F24
caution). **Named exclusions:** for control/t1/t3/t4 the exclusion was not
load-bearing — even the `stderr_tail` leaves matched (byte-identity); for t2 the only
excluded difference is the named paplay-gate `wall_s` leaf. Receipt schema preserved:
2056 leaves / 29 entries / identical key sets; `failures: []` in every r75 run; rc=0.
**Only new r75 lines are touched** by D1–D4 (`:2015`, `:2027`, `:2773`, `:2778`,
`:2851`), so prior rows cannot move by construction — and the r73/r74 replays confirm
it. No provenance comment is deleted by any fold.

## Tradeoffs / bounds

- **D1** is the only pure deletion (−1 line, −57 chars); its bound is the unobserved
  pacat surface class. **D2/D3** remove duplicate authority (net −1 line) and couple
  the ops legs to the declared parser (intended). **D4** is proven inert but withheld;
  the re-anchor is an author/critic receipt-changing fold, and its value is debatable
  because the current tail carries latency evidence that the spec-line tail would
  replace with a duplicate of `pa_sample_spec`.
- Cost: 7 probe runs ≈ 6.5 min wall, no daemon restart, no host reconfiguration,
  child-env overrides only; all probe invocations bounded (`timeout -s KILL`).
- Scratch inventory (this generation): `landed-diff.patch`, `dead-symbol-scan-landed.txt`,
  `refs-landed.txt`, `dup_scan.py`, `unused_locals.py`, `make_treatments.py`,
  `t1..t4*.py`, `run_proofs.sh`, `proof-*.{out,err,json}`,
  `proof-summary.txt`, `proof-driver.log`, `shadow_proof.py`, `shadow-proof.txt`,
  `rebuild-landed.log`, `tree/` (rebuilt from landed bytes).

**Seat stop.** Deletions applied to the tracked tree: none (by tasking). Proposed
integrator folds: D1, D2, D3 (each with a byte-identity or stable-projection proof).
Recorded-not-folded: D4 (re-anchor is the correct fold), the convention rulings above,
and the `plugin_census` recorded-ungated note for the verifier. The next deletion in
this arm would harm an axis: the remaining duplication is the per-leg / per-entry
convention cost (r74-D7 class), and the remaining "dead" branch is the intent marker
for a live defect.
