# R74 reviewer — landed lavf no-seek sweep + pw-cat ops-2 (`+544/−3`, insertion-only): 3 receipts byte-stable modulo one 1 ms wall leaf, `failures {}` reproduced by my own replay, all 7 member matrices reproduce my pre-landing independent predictions cell-for-cell — **but the acm "wound" claim is falsified by the arm's own extent instrument** (acm 868 B == 868 B, rc=0 both arms), and the blockage path is silent (exit 0 / `failures {}`)

Seat: **reviewer** (leaf, report-only). Wave `shokunin-train-20261101-w13`, round 74, lane audio.
Repo `/home/vgpnk/Projects/shokunin/audio-shokunin`. Host `plazir27`; system clock
**2026-10-14 15:18–15:42 UTC**. HEAD at open **`1ba8103`** (r73 report-last) — unchanged
all session (the arm landed in the worktree at 15:29:17 and is not yet committed; operator
commit pending, as in r73). Write scope honoured: this report + `corpus/live/r74-reviewer/`
only; no tracked file modified by this seat, no git mutation.

Under review: `corpus/fixtures/measure_audio.py` worktree revision
sha256 **`154a35a034fcba554427133c6026ce5bb6adcb11a54b36450171b02150ff9d49`**
(== `git diff HEAD` content; pre-landing revision was `77f107864b74f794aea1d4fa8ea28f6f50d741591297dff192b9b6f949b2543b`,
both in `corpus/live/r74-reviewer/pre-fixshas.txt`). Diff captured verbatim:
`corpus/live/r74-reviewer/r74-fixture.diff` sha256 `84bdc39a01836d6be2c69bbfe262ac07ec83e1c95802774be92f170a29f44f47`.
Toolchain: `mpv v0.41.0` (libavformat 63.1.101), `ffmpeg/ffprobe n9.0.1` (libavformat
63.1.101), `pw-cat` libpipewire 1.6.8, CPython 3.14.7, live PipeWire daemon.

## 0. Diff shape (reviewed hunk-by-hunk)

`git diff HEAD` = **+544/−3, 5 hunks**. The three deletions are exactly the wiring triple
(`if sum([...]) > 1:` mutex, `mode =`, `suffix =`), each **replaced by a line that preserves
the prior expression verbatim and inserts one r74 clause** — verified mechanically
(difflib opcode check): the `mode` line is a single-point insertion at char 10
(`"probe-lavfsweep-r74" if args.probe_lavfsweep_r74 else` before the unchanged r73 chain),
the `suffix` line likewise at char 12; the mutex appends `, args.probe_lavfsweep_r74` to the
same sum. Flag count 117 → **118**; `--probe-lavfsweep-r74 --probe-consumers-r73` → exit 2
`error: choose one probe mode`; `ast.parse` OK; **no new imports** (the r72 D1 import-time
class is not repeated). New code: `build_lavf_r74_members` `:1470`, `mpv_extent_leg` `:1541`,
`lavf_transport_entry` `:1620`, `lavf_startpos_entry` `:1709`, `pwcat_ops2_entry` `:1746`,
dispatch `:2327-2377`. Members land under `corpus/live/round-74/` (the tracked-member
convention; 6 new untracked files, regenerated deterministically each run).

## 1. Independent replay

Harness (all `corpus/live/r74-reviewer/`): `mk_noseek_members.py` (own members built from the
fetched n9.0.1 demuxer sources), `mpv_matrix.py` (own 4-transport mpv runner),
`mpv_position.py` (`--ao=pcm` extent), `mpv_start_probe.py`, `ops2_probe.py`,
`compare_post.py`, `acm-extent-check.json` (the **landed fixture's own** `mpv_extent_leg`
called on the landed members).

**Pre-landing predictions (my instruments, before the arm landed)** — iss 1-packet: rc fork
2/0; iss 6-packet: rc0+EPERM file, **head truncation 4064 B**; apc: rc fork 2/0; acm:
rc0+EPERM file, **no data loss (868 B == 868 B)**; wav/aiff/adx/wv controls invariant;
`--start=0.5` on wav: 44170 B file vs 88268 B fifo; ops-2: writerless-fifo TERM-immune
(`sigsuspend`, killpg −9), `--target 0` rc124 @4.001 s, raw mode rc0 on `axis.{snd,wav,bin}`.
Mechanism: `seek_frame_internal` returns a **bare `-1`** (seek.c) that mpv renders as EPERM;
the wound is `ff_read_frame_flush` on the generic branch (iss/apc take it, acm does not —
`AVFMT_NOGENSEARCH|AVFMT_NO_BYTE_SEEK` early-return).

**Landed-arm replay (3 receipts: author `…153027…`, reviewer run1 `…153053…`, run2 `…153341…`)**:
- run1 vs run2: 2 diff lines; author vs run1: 2 diff lines; run2 sha `5c9b4ab1…` **== author's
  receipt byte-for-byte**. The only varying leaf is `target0_unlinked_stream.wall_s`
  (4.001/4.002) — a 1 ms wall-clock leaf of the same class as r73's `pacing_*` leaves.
- `failures: {}`, exit 0, in all three runs; my independent matrix reproduces **every**
  member cell: iss/apc `[2,detected,EPERM]` vs `[0,…,null]`; acm `[0,'acm',EPERM]` vs
  `[0,'acm',null]`; iss_multi `[0,'iss',EPERM]` vs `[0,'iss',null]` + head truncation
  516196 B vs 520260 B (**delta 4064 B — the same constant my different-sized member lost**);
  adx/aiff/wav invariant; startpos 192068 B / 2.0 s (file, redirected_fd) vs 384068 B / 4.0 s
  (stdin, fifo); ops-2 all four cells reproduce my pre-landing numbers.
- Member bytes: generated members are **byte-identical across 3 generations**; my
  independently-built `my_apc_multi.apc` and `my_acm_multi.acm` are **byte-identical** to the
  landed `lavf_apc.apc` / `lavf_acm.acm` (two independent derivations converged).
- Receipt hygiene: 0 absolute paths, 0 `/tmp` leaks, 0 ASLR tags, 0 temp-dir names.

**Prior-row gate (pre/post pairs, my own captures)**: `--probe-sndfile-transport-r72`,
`--probe-ffprobe-transport-r71`, `--probe-transport-extsuffix-snd-r69` **byte-identical**
(shas `f7faaedb…`, `578cad95…`, `80f6d64b…` — matching the r73 reviewer's independently
recorded values). `--probe-consumers-r73`: 2 leaf diffs — `pacing_instant.wall_s` 4.031→4.033
(known jitter) and `daemon_live.default_sink` `…__SPDIF__sink` → `…__SPDIF__sink.2` (F4).

## 2. Findings by severity

### F1 — medium-high (claim drift): the acm "wound" is asserted, unmeasured, and falsified by the arm's own instrument

- The author report (`reports/round-74/r74-author.md:82,128-129`) says acm is a
  "FORK — **ENOSYS-class wound**" and that "acm shows the second shape at small size because
  its raw-packet reads queue data ahead of the failed refresh seek"; the fixture comment
  repeats it (`measure_audio.py:1443` "the acm row shows the same ENOSYS-class wound at small
  size"). The landed `LAVF_R74_MEMBERS` labels acm `"fork"` (`:1458`).
- **Measured**: calling the **landed fixture's own** `mpv_extent_leg` on the landed
  `lavf_acm.acm`: file **868 B / 0.00907 s**, fifo **868 B / 0.00907 s**, rc=0 both,
  `seek_failed` EPERM vs null (`acm-extent-check.json`). No truncation, no wound. My
  independent instrument agrees (868/868), as does r74-critic F1 (`pcm 800/800`) and
  r74-boundary §7 ("FALSIFIED as fork — invariant rc=0").
- **Mechanism**: acm's `AVFMT_NOGENSEARCH` makes `seek_frame_internal` return `-1`
  **without** `ff_read_frame_flush`; iss/apc take the generic branch and flush the packets
  `find_stream_info` already consumed — that flush is the wound. The receipt is honest
  (its verdict tuples show rc=0 on both sides); the *label* `predicted: "fork"` is satisfied
  only because the grouping key includes `seek_failed` (`:1638`), i.e. **acm forks by
  construction on a leaf that is not a playback verdict**.
- Impact: any downstream restatement ("the 4-clause rule is CONFIRMED, 3/3 demuxers fork")
  lands a claim the wave's own critic has already refuted for acm. Required restatement:
  *the rule predicts a seek-refusal for all three; the playback wound is shape-dependent —
  rc2 when the probe drains the stream (iss small, apc), rc0 + constant 2-packet head
  truncation when packets survive (iss multi), and **no wound at all** for acm (no flush).*
- Note the fixture's two shape comments are otherwise correct and the receipt carries the
  evidence for both; this is a labeling/attribution defect, not a fabrication.

### F2 — low-medium (silent saturation): a generation/member blockage yields exit 0 with `failures {}`

- `measurements["lavfsweep_generation_r74_probe"] = {..., "failures": [], **gen}`
  (`:2360`) and blocked members get `{"blockage": …, "failures": []}` — so a host without
  `ffmpeg -f lavfi` (adx/aifc blocked), or any member-generation failure, still exits 0 and
  reports no failures. The blockage is *recorded* (the brief's degrade clause is honoured)
  but not *signalled*, so a wave-level gate keyed on `failures`/exit code sees success.
- Not triggered here (`blocked: {}`; all 6 members generated), so it is a dormant
  robustness gap. Minimal fix: append the blockage to that entry's `failures`.

### F3 — low (error-path robustness): the `--target 0` backstop does not bound the grandchild

- `:1816-1833`: `subprocess.run(["timeout","-s","TERM","4","pw-cat",…], timeout=15)`. If
  pw-cat were ever TERM-immune (the class the cell exists to separate), python kills only the
  `timeout` wrapper at 15 s; the orphaned pw-cat holds the captured pipes and the recorded
  bound becomes 15 s, not 4 s, with a leaked pw-cat holding an unlinked live stream. The
  comment "the subprocess timeout is only the backstop" overstates the backstop. I reproduced
  the orphan class myself (`timeout -s KILL 10 timeout -s TERM 3 pw-cat …` → pw-cat alive
  after the wrapper died). Dormant on this host: rc124 @4.001 s in 3/3 runs.

### F4 — low (environment leaf / honesty): the r73 `daemon_live` cell is live-session state and it moved during the window

- My pre/post pair for the untouched r73 row shows `default_sink` `…__SPDIF__sink` →
  `…__SPDIF__sink.2`. **Attribution: not the r74 arm** — the change coincides with the
  r74-boundary seat's *non-isolated* private-daemon+wireplumber experiment at ~15:30
  (`reports/round-74/r74-boundary.md:190-198`: the live session transiently lost its sinks
  and re-registered them). My controlled private-daemon spawn (no session manager) and two
  subsequent lavfsweep runs did **not** change the sink name (`.2` before and after).
- Consequence: "prior rows byte-identical" can only hold **modulo live-session leaves**; the
  r73 consumers row embeds one by construction (`pactl info` read). The other 3 prior rows I
  paired are byte-identical. Recorded so the wave's byte-identity claims stay honest; the
  peer incident itself is not mine to adjudicate.

### F5 — informational (traceability): member bytes are not pinned in the receipt

- `lavfsweep_generation_r74_probe.generated` records extension labels, not sha256. Members are
  regenerated every run; they are deterministic here (verified across 3 builds, and my
  independent apc/acm are byte-identical), but a changed ffmpeg synth would silently change
  the members without the receipt noticing. The hashes exist in the author's report
  (`r74-author.md:58-65`) and I re-derived them independently
  (`corpus/live/r74-reviewer/round74-members-sha.txt`), so the record is complete across
  artifacts — just not in the machine receipt.

## 3. Verified PASS (reviewed, not assumed)

1. **Insertion-only**: 5 hunks; only the 3 wiring lines replaced, prior expressions preserved
   verbatim (opcode-verified); everything else additive. No shared function edited.
2. **Flag/wiring**: 118 flags; mutex works; mode `probe-lavfsweep-r74`, suffix
   `-lavfsweep-r74`; AST OK; no new imports.
3. **Members**: correct hand-built headers (iss ASCII tokens; apc 32-B header; acm 14-B
   extradata **including** the magic — the trap I bisected independently), detected by lavf
   (iss/apc 100, acm 66), decodable; deterministic and idempotent; tracked-location
   convention `corpus/live/round-74/`.
4. **ARM A replay**: all 7 member cells reproduce my pre-landing independent predictions;
   controls invariant (adx GENERIC_INDEX, aiff own read_seek, dec_act wav+PCM-hack);
   two wound shapes measured, head-truncation delta **4064 B** constant across three
   independently built iss members (mine 6-packet, the author's 256-packet, the critic's 40-packet).
5. **Position fork**: `--start=2` → 192068 B/2.0 s (seekable) vs 384068 B/4.0 s (streaming),
   matching my independent 44170/88268 on a 1 s wav.
6. **ARM B ops-2**: all four cells reproduce my independent pre-landing measurements —
   TERM-immune open-block + killpg −9 (`wait_for_partner`, `sigsuspend`), `--target 0`
   rc124 @4.001 s (TERM-terminable), raw bypass rc0 on all three names, zero-sink private
   daemon = hang (sink census 0) with clean teardown (**no stray daemons/processes** after
   3 runs).
7. **Stability**: 3 receipts byte-stable except one 1 ms wall leaf; `failures {}` in all.
8. **Prior rows**: 3/4 byte-identical pre/post; the 4th differs only in the two documented
   leaves (F4).
9. **Receipt hygiene**: no abs paths, no `/tmp`, no ASLR tags, no temp names.

## 4. Residual risk / verification gaps

- The acm "fork" is definitional; if the wave text keeps "3/3 fork" without the shape split,
  the claim is false in the playback sense (critic F1 + this review + boundary §7 all agree).
- Head-truncation delta is packet-granular and build-pinned (4064 B here); pin the **sign**,
  not the exact value.
- `--target 0` rc124 is a *class* pin (TERM-terminable), measured at a 4 s bound; the
  zero-sink cell is measured **without** a session manager — the boundary seat's
  wireplumber variant was not isolated (do not repeat it without a private device set).
- wall leaves (`target0.wall_s` ±1 ms, `pacing_*` ±1–2 ms) remain run-to-run noise.
- My prior-row gate is 4 rows, not the full 123-mode ledger (the r74-baseline seat's ledger
  is the wave-level instrument for that).
- The landed worktree still carries the untracked `corpus/live/round-74/` members and a
  modified tracked `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc` (a run
  artifact; r73's commit excluded it) — operator commit hygiene, noted.

## 5. Evidence index (all paths under `corpus/live/r74-reviewer/` unless noted)

| artifact | sha256 / value |
|---|---|
| landed fixture (`corpus/fixtures/measure_audio.py`) | `154a35a0…` |
| pre-landing fixture | `77f10786…` |
| diff | `84bdc39a…` (`r74-fixture.diff`) |
| author receipt `runs/20261014T153027827786Z-lavfsweep-r74` | `5c9b4ab1…` |
| reviewer run1 `…153053003782Z` | `d272a13f…` |
| reviewer run2 `…153341301201Z` | `5c9b4ab1…` (== author) |
| my members / instruments | `mk_noseek_members.py 7ee5b7cb…`, `mpv_matrix.py 80a82966…`, `ops2_probe.py 6131c966…` |
| acm extent check (landed leg) | `acm-extent-check.json 65122157…` |
| wound-shape extents | `position-wound.jsonl 7cb7a01b…` |
| ops-2 pre-landing cells | `ops2-pre.json`, `ops2-termimmunity.json`, `ops2-target0-fifo.json` |
| prior-row pre/post receipts + shas | `pre-*/`, `post-*.out`, `pre-receipts-sha.txt` |

Commands (exact): `python3 corpus/fixtures/measure_audio.py --probe-lavfsweep-r74` ×3 (exit 0,
`failures {}`); `--probe-{consumers-r73,sndfile-transport-r72,ffprobe-transport-r71,transport-extsuffix-snd-r69}`
pre and post; `git diff HEAD -- corpus/fixtures/measure_audio.py`;
`python3 - <<EOF` harnesses as listed above.

**Seat stop.** Review of the landed diff complete; findings above are recommendations, not
admissions. The canonical runtime remains the sole judge.
