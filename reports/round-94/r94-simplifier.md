# r94 simplifier — proven folds on the SoX_ng effect lattice (queued, not landed)

**Verdict: PASS — 23 proven folds (variant A) / 26 with the leg-dedup
(variant B).** Every fold is proved by the family's own narrow check
(`--probe-sox-r94`, green: 0 failures, 0 `coverage_blocked`, all 8 entries) plus
a structural receipt walk against a pristine control run. **Nothing landed**:
the fold set is queued as a diff. Zero tracked writes, zero commits.

- Lane: `/home/vgpnk/Projects/shokunin/audio-shokunin`. The tree moved under
  the lane: entry HEAD `aaf56d30` → exit HEAD `021bde86` (`ffeb5155`, the r95
  author's JACK family, landed mid-lane).
- Audited revision: `corpus/fixtures/measure_audio.py` at entry HEAD
  `aaf56d30`, blob sha256
  `4808c4cfb17c311204398c9858bea3582d512090cc4a075cf31c01f4a064ee26` (the
  r94 author's `+2231/-3` sox family: block lines 31091-33306, 2 215 lines).
  **The r94 block is content-identical at the new HEAD** (`git show
  HEAD:… | block-sha f9753be…` vs the audited `a6e5da78…` — the two differ only
  by the trailing blank lines before the appended r95 header), and both fold
  variants re-apply to the current HEAD with every anchor found exactly once
  and the result AST-valid. The queued diffs are landable as they stand.
- Scratch: `corpus/live/r94-simplifier/` (mirror root, see `RECEIPTS.md`).
- `TMPDIR=/home/vgpnk/Projects/shokunin/tmp`, bounded runs (`timeout 900`),
  never `pactl set-default-*`, no device and no PipeWire object touched.

## Reference proof — and the `lsp` unavailability record

**No language server is available in this lane** (no `lsp` device in the seat's
toolset; no server answers `corpus/fixtures/measure_audio.py`). Deletion
candidates were therefore screened by AST reference analysis over the module
(store/load accounting, call-site keyword accounting) plus a repo-wide literal
grep as the *fallback*. That is not semantic proof and is not presented as
such; where a name survives only in another seat's derived artifact
(`r94-critic/armlog.jsonl`, `armsites.txt`, `addlines-*.txt`, its own tree
copies) that artifact is *derived*, not a caller, and is called out in the fold
table.

## Proven fold set

All anchors assert `count == 1`; the applier is
`corpus/live/r94-simplifier/r94s_apply_folds.py`. Diff scope is proved inside
the r94 block only (hunks 31255-33128, no other family's identifier appears in
the diff).

| # | fold | site | what it removes | proof | tradeoff |
| --- | --- | --- | --- | --- | --- |
| A1a | drop `metrics.fmt_tag` | `_sox_r94_metrics` | 1 recorded key on 120 legs | 0 readers (AST: the only 2 occurrences are the reader-meta write and the metrics write); walk shows only its removal | receipt-schema change; the verifier's cross-run key diff must be re-baselined |
| A1b | drop `metrics.first8_ints` | `_sox_r94_metrics` | 1 recorded key + its `arr[:8]` conversion on 120 legs | 0 readers; not in `SOX_R94_REF_METRIC_KEYS`, never compared | **59 526 B of the receipt (19.2 % of the sox payload)**; the r94 *scout* records a `first8_ints` of its own, so the family diverges from that recording convention |
| A2 | drop the `expect` column | `sox_rate_r94_entry` `length_rows` | 6 unread values + 1 binding | AST: `expect` stored, never loaded; the law derives from `in_frames`/`out_rate` and the measured `frames` stay in the receipt; 5 of the 6 rows still pinned by the cross-seat metric arm | the source no longer carries the scout's measured length table (the receipt does) |
| A3 | drop `alias_20k_v` | `sox_rate_r94_entry` `alias_specs` | 1 leg (1 spawn, ~1 554 B) | 0 readers: the only occurrence in the tracked fixture is its own tuple row — no `_sox_r94_arm`, no `ref_arm`, no `ref_metric_arm`, and no row in the author's report table (the other repo hits are another seat's derived copies of the block under `r94-critic/`, not callers) | leg census 150→149, rate entry 22→21 |
| A4 | one railed-sample authority | `_sox_r94_railed` | the two local counters `clipped_ge` (gain) and `railed` (dither) — same 4-line body, same law | identical expression `rint(arr*32768) >= thresh`; receipts unchanged | none observed |
| A5 | one trailing-zero authority | `trail_zeros` in `sox_repeat_pad_silence_r94_entry` | 3 identical 6-line loops (silence above / both / `-l`) | byte-identical arithmetic; the local `trail` binding is kept because three arms read it | none observed |
| A6 | drop the entailed arm | `sox_rate_r94_entry` (`d20 < -110`) | 1 arm site | **entailment proof**: both arms read the same unmuted attribute, nothing writes `d20` between them, `x < -120 ⟹ x < -110` over 15 000 sampled values → the entry verdict can never change; only one duplicate failure line is lost in [-120,-110) | arm-site census 103→102; the r94-critic's `armsites.txt` counts 103. The dropped arm is an **equivalent mutant** |
| A7a | drop the dead `stim_i` binding | `sox_det_r94_entry` | `I` | AST: stored, never loaded in that entry | none |
| A7b | drop the dead `frames` binding | `_sox_r94_write_pcm16` | `frames` (only `channels` is used) | AST: stored, never loaded | none |
| A7c/d | drop the dead max-abs bindings | `sox_trim_r94_entry`, `sox_repeat_pad_silence_r94_entry` | 2 × `mx` | AST: `_sox_r94_mismatch`'s 2nd return unused at both sites | none |
| A8 | drop `_sox_r94_leg`'s `note` parameter + branch | `_sox_r94_leg` | 1 parameter, 1 unreachable `if note:` branch | no call site passes `note=`; the 8 legs carrying a `note` key in the green receipt are hand-built synthetic rows, not `_sox_r94_leg` products → the branch cannot fire | a future round wanting per-leg notes must re-add it (the synthetic rows keep their literals) |
| A9 | drop `_sox_r94_spawn`'s `wd` parameter | `_sox_r94_spawn` | 1 parameter + `cwd=wd` | no call site passes `wd`; every invocation uses absolute paths | none observed; `timeout` is retained (live pass-through to the spawn) |
| B1 | drop the two duplicate identity rows | `sox_det_r94_entry` identity loop | `det_rate_same_identity`, `det_pad_pct50_identity` (2 spawns, 2 receipt rows) + their `ref_arm` | the same invocation on the same stimulus is measured **twice in one run**: `det_rate_same_identity` ≡ `sox_rate_r94_probe:rate_same_identity` and `det_pad_pct50_identity` ≡ `sox_repeat_pad_silence_r94_probe:pad_pct50` (identical `argv`, identical sha `6a2a6b0cad80`, identical law `sha == sha(B)`). Deleting the *det* copies keeps both laws armed where they own their cross-seat refs — both still `sha_match: True` in the variant-B receipt | leg census 150→148; the det entry's headline "4/4 integer-unity rows" becomes 2 in that entry |

Totals: variant A `+43/-58` (net **-15** lines, 23 folds); variant B
`+44/-63` (net **-19** lines, 26 folds).

## Preserved contract

- **Control experiment.** Two *pristine* runs differ in **exactly one** field
  outside the declared volatile set:
  `sox_dither_stat_r94_probe:guard_default_path_row/railed_G_gain12_default`
  (14979 → 14873) — the row the author marks "IMPRECISION, recorded, never
  armed" and whose two source legs carry `volatile_sha: true`. This proves the
  volatile exclusion is complete for this fixture: every other field of all 150
  legs is byte-stable across runs.
- **Variant A** vs the baseline: 1 leg removed (`alias_20k_v`), all remaining
  field differences are the intended `first8_ints`/`fmt_tag` removals, and the
  **only** residual is that same documented dither-sensitive row (14979 → 15000,
  i.e. run-to-run variance, not a fold effect). No leg was added, no armed value
  moved, no `failures`/`coverage_blocked` appeared.
- **Variant B** vs the baseline: 3 legs removed (the orphan + the two duplicate
  rows); the only residuals are the removed legs' own fields.
- Cross-seat witnesses stay armed: 59 sha + 15 metric (A), 58 sha + 15 metric
  (B) — the one fewer sha witness is the dropped duplicate `pad_pct50` row,
  whose witness survives in the repeat entry.
- All runs: 8/8 entries, `failures: {}`, `coverage_blocked` empty.

## Examined and declined (measured, not folded)

| candidate | measurement | why it is not a Pareto move |
| --- | --- | --- |
| memoize `_sox_r94_scout_refs()` + `_sox_r94_stimuli()` (each rebuilt once per entry = 8×/run) | 8× refs = 53 ms, 8× stimuli = 30 ms, 16× host = 106 ms → **189 ms of a 5 s pass (3.8 %)** | buys 0.2 s with a cache convention; the per-entry rebuild is the family's self-sufficiency rule |
| `metrics.bits` | 0 law readers, but it is the only format witness for the `-b 16/24/32` conversion legs | evidence value > its bytes |
| `_sox_r94_norm`'s `\b\d+\.\d{4,} s\b` wall scrub | never fires in either green receipt (`<wall> s` count 0) | sox/ffmpeg are the only stderr producers, but "cannot match" is not provable from one window; a scrub that never fires is still a guard |
| `_SOX_R94_ERR_CLASSES` entries | **all 7 classes fire** in the green run (`sox_r94_fail`, `_opt`, `_parse`, `_rate_override`, `_repeat_range`, `_silence_args`, `_usage`) | no dead classifier |
| `half_hz=` / `span=` / `tol=` / `sig=` / `default=` defaults | never overridden | each is a *named constant seam*; inlining turns it into a magic number — a second convention |
| `ROOT/live/r94-author/scratch` | the family's scratch dir carries the **authoring seat's** name in a shared tracked artifact | stale name, but renaming moves the path the author's receipts record — queue as a naming fix, not a fold |
| recorded-only r94 witnesses: `band_997hz_db` (11 alias legs), `trailing_zero_frames` (3), `nonzero_err_samples` (2), `exact_frames`/`delta_vs_exact`/`delta`/`want_frames`, `option` (11), `max_abs_diff*`/`mismatch_vs_input_head`/`mismatch_vs_mean`/`mismatch_vs_nearest_even` | a systematic sweep of every key the family writes into a leg/metrics dict against every read site found these with no *comparison* consumer | they are the receipt-side witness of laws the report cites (and `band_997hz_db` sits in the declared `SOX_R94_REF_METRIC_KEYS` merge list, so a later round can promote it to a compared key). Evidence, not dead weight — the one exception, `first8_ints`, is folded as A1b |

## Blockers and hazards (observed, not mine)

1. **The shared tree moved under the lane (not my writes).** At entry the
   fixture was clean and byte-identical to HEAD (`4808c4cf…`). Mid-lane the r95
   author's merge was visible as `UU corpus/fixtures/measure_audio.py` (24
   conflict markers, mtime `05:57:03`, with `corpus/fixtures/r95jack.c` and
   `reports/round-95/r95-author.md` staged) — then it landed as `ffeb5155` and
   the adjudicator commit `021bde86`; the tracked tree is clean again and the
   r94 block is content-identical (see above). **This lane made no write outside
   `corpus/live/r94-simplifier/`, `reports/round-94/r94-simplifier.md`, and
   `$TMPDIR`**; the audited revision is entry-HEAD's committed blob, which my
   pristine copy still matches byte-for-byte.
2. **The host's `pipewire-pulse` daemon stalled mid-lane** (sibling lanes' bare
   `pactl` calls hanging; a `pactl load-module` wedged for minutes). The r94
   family's per-entry census is a 5-call serial ladder with a 12 s per-call
   timeout, so a stalled daemon turns a **5 s pass into >8 min** (16 censuses ×
   up to 60 s). It degrades *correctly* (each unreadable call is recorded, never
   a green), and the r96 lane is already adding a one-call server gate for the
   same class. Inherited r76-r93 convention → reported, not folded.
3. The final variant-B re-run (23+3 folds) was launched at `05:58:50`, inside
   that stall; it was still cycling the census ladder nine minutes later and was
   terminated at the lane's wall bound (bounded compute on a host already
   carrying six sibling fixture runs). The variant-B evidence in this report is
   therefore the green `085724` receipt (22 folds). The 4-fold delta between
   that run and the final B (A8a/A8b/A9a/A9b) is proved receipt-invisible by the
   variant-A pair: `085646` (19 folds) and `085841` (23 folds) are both green
   with the identical residual set.

## Evidence index

`corpus/live/r94-simplifier/` — `RECEIPTS.md`, `r94s_pristine.py`,
`r94s_folds_variant{A,B}.diff`, `r94s_apply_folds.py`, `r94s_compare.py`,
`r94s_evidence_control.txt`, `r94s_evidence_variant{A,B}.txt`,
`r94s_evidence_arm_entailment.txt`, `r94s_status_exit.txt`, the run
stdout/stderr pairs, and the five receipts under `tree/live/runs/` (plus the
symlinked read-only scout witness `tree/live/r94-scout`).

**Stop condition reached**: the next deletions in this family are the two
recorded-not-armed rows the author justified by name (the `-G` default-path
guard and `metrics.bits`), the per-entry self-sufficiency rebuild, and the
census ladder — each of which trades a named axis (evidence, coverage
semantics, or convention) for weight, so they are left standing.
