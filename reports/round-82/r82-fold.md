# r82 FOLD — the landed correction queue applied to the `--probe-ffmpeg-r82` family

**Seat** FOLD (executor) · **host** devin/plazir27 · **repo**
`/home/vgpnk/Projects/shokunin/audio-shokunin` · HEAD at start
`bc3f55ca`, HEAD now `2a5555b4` (sibling r83 verdict commits only —
`git log` on the fixture shows last touch `a151a226`). **Scope**:
`corpus/fixtures/measure_audio.py` only (+ this report + receipts under
`corpus/live/r82-fold/`). No commit, no push — the orchestrator commits.

Fixture sha: `26431adf29ab122b…` (pre-edit, 19 811 lines, == `a151a226`
tree) → `7984409ceb9ca7c35b18b9b28f2add445701c044d71f8ee4ddc6f35d31217ef7`
(post-edit, **19 932 lines**). `python3 -m py_compile` clean.
`git diff --stat`: **+198/−77**.

No `lsp` device answers this file on this substrate (recorded by the
r82-simplifier seat, same gap); all edits are literal review-verified
text edits over the single file, cross-references re-grepped after
editing. The frozen `probeParent` seat dispatched **one** read-only
`ufo-labrat` (agent `2a77abc9`) — its independent re-derivation of the
tone-band tables and the unload-predicate shape PASSed both hypotheses
and is folded into the item proofs below.

## Items applied

Line numbers are post-fold file positions.

| # | queue item | change | evidence |
|---|-----------|--------|----------|
| 1 | **Simplifier**: proven −25-line patch (10 items, `corpus/live/r82-simplifier/r82-simplifier.patch`) | `git apply` clean on the post-r83 fixture (context match; `git apply --check` first): T1 `FFPW_R82_FFPLAY`, T2 `require_linked`, T3 `env_extra` in `_ffpw_r82_shot`, T4 `taps` in `_landed_on`, T5 entry-6 dead artifact check, T6 missing-row predicate, T7 `_star`, T8 `_cap post`, T10 `kill_watch` None-branch, T11 falsy-path guard | patch applied = +12/−37 of the fold total; `py_compile` clean; no `require_linked`/`env_extra`/`taps=`/`_star`/`FFPW_R82_FFPLAY` references remain |
| 2 | **Reviewer F1** — r82 pair collides with r78 pid%4==1 (1208/1711 inside both ±6 % bands) | re-keyed: `_ffpw_r82_tone_pair(pid)` at :14265 → `L = 2900 + (pid%4)·400`, `R = L+560` (the 2.9–4.7 kHz band — disjoint from every r78-family class AND every sibling r82 class); `_ffpw_r82_write_tone`/`_ffpw_r82_tone_windows` re-pointed; stale "distinct pair" comment replaced | exhaustive enumeration: 16 fwd + 16 rev + 12 sibling ordered pairs all outside ±6 % (worst margin 1270 Hz vs 246 allowed); labrat `2a77abc9` PASS, min 1.43×; run1 pid-class-3 pair 4100/4660 and run2 pid-class-1 pair 3300/3860 both green live under two concurrent r83 lanes |
| 2b | (F1 guard) — "add a same-family band guard" | `_ffpw_r82_tone_band_clear()` at :14287 checked at import via a real `if … raise RuntimeError` (not `assert` — `-O`-safe) | module import prints `band_clear: True`; the check covers r78 classes both directions + sibling r82 classes |
| 3 | **Reviewer F2** — arm the ALSA `-channels 0` rc=8 class | new `ff_option_not_found` class in `_FFPW_R82_ERR_CLASSES` (:14344); new leg `a7_ch0_option_absent` (:16197) + gate (:16281): rc=8 + class + `Option channels not found` stderr token | boundary receipt `corpus/live/r82-boundary/runs/c6/alsa_ch_0/` reproduced verbatim: rc=8 `Option channels not found.`; live runs: a7 = `8 / ff_option_not_found` ×2; 0 "not found" hits across the four pinned receipts (no reclassification of armed legs) |
| 4 | **Critic F1** — `a2_hw_free_pwheld` held hw:0,1 not the claimed hw:0,0 | `holder_sink` = the Audio/Sink whose `aplay_device == cap_dev` (:16069, `Speaker__sink` here — the scout's measured cell), recorded as `entry["a2_holder_sink"]`; `coverage_blocked` names the unmeasurable premise when none maps; `holder_consumers == [holder_sink]` now **gated** (:16227) | live ×2: `a2_holder_sink = …Speaker__sink.29`, `holder_consumers = […Speaker__sink.29]`, a2 rc=0 finalized wav — the same-subdevice opposite-direction split is actually exercised now |
| 5 | **Critic F2** — `t2_cap_*` had no content gate | new post-unlink gate (:15935): `mine_spans` must contain a span ending after the unload instant (`s[1] > unl_at`), else the sustained-zeros class is indistinguishable — mirrors the t1 `post_mine` witness | live ×2: `t2_cap_r{0,1,2}` spans `[[0.1,2.0]]/[[0.2,2.0]]/[[0.1,2.1]]` with unl_at ≈1.20 s — post-unlink tone present; the gate also fired *correctly* in the red-flake run (`spans []` on a disk-quota-dead wav — it reported, not passed) |
| 6 | **Critic F3** — fixed tag + no same-family lock | tag derived from pid (`_ffpw_r82_tone_pair`, item 2); same-family flock `_ffpw_r82_family_lock()` (:14753) on `…/measure_audio-ffmpeg-r82.lock`, taken in the dispatch before the 8 entries (:19283) — a second `--probe-ffmpeg-r82` waits, never overlaps | lockfile records `pid/ns/tone` per run (`pid=268525 ns=r82ff_ns_268525 tone=3300.0/3860.0` after run2); flock fd held to process exit |
| 7 | **Critic F4** — `_gst_r81_unload_own` substring predicate kills foreign modules | `_gst_r81_sink_module_index` (:12803) now extracts `sink_name=(\S+)` and compares **exactly** (edge quotes stripped) — the shared fix; substring predicate gone | live module lines self-match; `r82c_a` query rejects `r82c_a2` and returns the correct `r82c_a` index; labrat re-verified on the real r83-critic incident receipt (`helper_picked_r83c_a2: true` case now rejected). Live unloads ×2 runs: `verified_index == captured`, `recycled:false`, `sinks_gone` true — the strict predicate still finds our modules |
| 8 | **Scribe** — A-list count/timeline corrections where they touch armed rows | audited all ADJ items against armed rows: **none touch the fixture** — ADJ-1 (5th dev run), ADJ-2/3 (author §6 inventory/HEAD chain), ADJ-4 (baseline 6/8→5/8), ADJ-5/6/7 (boundary leg counts 25→27/16→15/30→41), ADJ-8 (0.1 s window claim), ADJ-9 (window label) are all *report-file* discrepancies adjudication-side; no armed row carries those counts (grep-verified: no `30 EIO`/`63/63`/`0.1 s`/leg-count literals in the r82 block) | the fold's own count delta is declared here: family census 76 → **77 legs** (the a7 arm), ALSA entry 7 → 8 legs |

Also updated in-place (comment truthfulness, same hunks): family header
EXIT MAP now lists rc=8 option-absent; ALSA SPLIT paragraph says "the
SAME subdevice's playback direction" + the `-channels` cell; the
Contention paragraph documents the pid-keyed band + flock; dispatch
comment documents the lock.

## Leg results — two green runs on final bytes

| run | receipt (`corpus/live/runs/`) | pid→pair | result |
|-----|------------------------------|----------|--------|
| run1 | `20261015T222214878231Z-ffmpeg-r82` | 4098187→4100/4660 | `{"failures": {}}`, 77 legs, all 8 entries `[]` |
| run2 | `20261015T222550276154Z-ffmpeg-r82` | — | **RED — environmental only**: `t2_cap_r0` ffmpeg died rc=134 at 1.438 s on `Disk quota exceeded` (16 G tmpfs `/tmp` ~80 % full of sibling seat dirs); 4 failure strings on that one leg, other 76 green |
| run2b | `20261015T222951470354Z-ffmpeg-r82` | 268525→3300/3860 | `{"failures": {}}`, 77 legs, all 8 entries `[]` |

Two greens on identical final bytes (sha `7984409c…` constant across all
three runs). Folded-cell verification live, both greens:
`a2_holder_sink=…Speaker__sink.29` + `holder_consumers=[Speaker]`;
`a7=rc8/ff_option_not_found`; `t2` post-unlink `mine` spans present;
unloads `verified_index==captured`/`recycled:false`; `sinks_gone` true;
`own_nodes_after []`; `coverage_blocked` absent. Receipt copies +
`proofs.txt` under `corpus/live/r82-fold/` (run1 sha `55884b69…`,
run2b `aaddf169…`, red-flake `ed319073…` kept as honest evidence).

## Declined / out-of-scope

- Reviewer F2's *second* exception cell (outdev options in input
  position) — the queue assigned only the `-channels 0` rc=8 arm; the
  `ff_option_not_found` class added here already names the shape.
- Reviewer F3/F4/F5/F6 and critic F5–F13 — not in the assigned queue;
  left for the ledger.
- The scribe's report-file corrections — adjudication items by design,
  not armed-row changes (item 8).

## Remaining risks / blockers

1. **None blocking.** The red run is a transient `/tmp` quota flake
   (sibling work dirs), reproduced nowhere else; the offending leg's
   argv/env is byte-identical to the green runs and both new and old
   gates reported it honestly.
2. The family flock is *blocking* by design — a wedged same-family
   holder would stall a rerun; flock releases on process death, and the
   lockfile carries the holder's pid for diagnosis.
3. The pid-keyed pair changes the tag frequency per run — receipts
   self-document it (lockfile + `mine` window `f_l`/`f_r` columns); no
   armed row pinned the old literal freqs.
4. `holder_consumers` is now a hard gate — on a host where the holder's
   stream legitimately re-routes mid-leg (default churn), a2 could see
   an environmental red; that is the intended honest signal vs the old
   vacuous record.
5. No resume mutation attempted (no `resume_continuity_v1` preflight
   required or run); no commit, no push.

Seat stop — files changed: `corpus/fixtures/measure_audio.py` (+198/−77),
`reports/round-82/r82-fold.md`, receipts `corpus/live/r82-fold/`
(run1/run2/run2-red stdout+stderr, run1/run2/red measurement copies,
`proofs.txt`). The canonical Rust runtime remains the sole judge.
