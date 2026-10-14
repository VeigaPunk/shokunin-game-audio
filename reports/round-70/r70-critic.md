# R70 critic — audit of the fifo_writer_hold_s ladder

Lane `audio`, round r70. Audited as it landed: uncommitted diff on
`corpus/fixtures/{measure_audio,build_artifacts}.py` (first seen ~09:14 local),
one live probe receipt
`corpus/live/runs/20261014T122404585607Z-fifo-hold-ladder-r70/measurements.json`
(minted by my own run of the author's new mode, exit 1),
author scratch `corpus/live/r70-author/scratch_ladder.{py,json}` (48 legs),
plus sibling-seat evidence (scribe fine ladder + straces, boundary shape
matrix). My independent harness: `corpus/live/r70-critic/ladder.py`,
data `ladder_idle.json`, `ladder_loaded.json`, `st.log` (strace -f -ttt).
Host: SoX_ng v14.8.0.1 + ffmpeg n9.0.1, python 3.14, 32 cores.

Author report had NOT landed at write time (09:37); `ledger-r70.tsv` carries
1 row, mtime 09:26, no live run_ledger process — ledger appears stalled.

## Audit Q1 — does the ladder isolate "writer hold"? PARTIALLY, and the measured variable is attachment-span, not hold

The oneshot ladder does isolate hold (600 B member `round-66/pair_dec_act.wav`
fits the 64 KiB pipe in one non-blocking write; feed span ≈0).
The chunked cells do NOT: 100 B × 0.05 s × 6 chunks = ~0.30 s of writer
attachment during delivery — chunked@h=0 passes (author scratch 4/4, mine 8/8,
landed receipt 10/10) because the *feed window* covers open #2, not because
h=0 suffices. The author's own comment concedes this is the intent ("the
'correctly blocking writer' arm"), so this is a framing hazard, not a bug —
provided the report reads `h*(chunked)=0` as binary-arm evidence, not a hold
bound. The receipt field `minimum_stable_hold_s.chunked = 0.0` will mislead
anyone who skips the comments.

Deeper issue: the per-cell classifier is **verdict-signature only**
(`detected, route, exit, samples, error`; `wall_s` recorded per-rep but NOT in
the signature). Signature collisions across mechanisms produce false stability:
r67-author evidence had detached-branch runs land `exit 2 au-magic` — the SAME
signature as the pinned arm — 5/5 times. On a host/context where the detached
branch emits the reference signature, the ladder reports an h*=0 racy cell as
"stable" while the open-#2 race is live. Today the detached branch happens to
emit `blocked:` so divergence is visible; the classifier is one mechanism-blind
step from masking the very race it measures. `wall_s` disambiguates
(blocked=10.01 s vs au-magic≈hold+0.004 s) — it must be inside the signature.

## Audit Q2 — is h* a bound or a load-dependent point? FALSIFIED as a host bound; it is a load-conditioned, stochastic transition zone

- strace window (mine, idle): reader `openat` #1 at t=…391.864076, ffmpeg
  bridge `openat` #2 at t=…391.889972 → **Δ=25.9 ms**, spent almost entirely
  in ffmpeg's own .so loading (`st.log:52,223` — 170+ O_CLOEXEC .so opens).
  The bound is the bridge child's link+init latency — reader-side, uncontrolled
  by the ladder.
- Boundary is stochastic, not a point: scribe's fine ladder shows
  h=0.018 → **5 blocked / 6 au-magic within one 11-rep cell**
  (`r70-scribe/runs/logs/ladder-fine2.log`); h≤0.015 all-blocked; h≥0.02 all
  au-magic. "Minimum stable hold" is a probability transition ~18–20 ms wide
  on this host idle.
- Load moves it ≥2×: my loaded run (40 un-niced CPU spinners, loadavg ~50):
  **h=0.05 flipped 8/8-pass (idle) to 12/12 blocked**; h=0.10 passed 12/12
  (`ladder_loaded.json`). Boundary's nice-19 load test (their section E) did
  NOT reproduce this because niced hogs don't contend — load1 stayed 3.16;
  un-niced oversubscription is the adversary, and a 64–100-lane fleet wave
  manufactures exactly that.
- So "h* < 1.0 s exists and is rep-stable on this host" is TRUE only per-run;
  the pin's real meaning is margin: 1.0 s ≈ 50× the idle window, ≈10× the
  loaded (load~50) window. Also the stable set is an **interval**, not
  [h*, ∞): hold ≥ arm_timeout ⇒ `blocked:` — my h=12 s leg: attached at open
  #2, `blocked: no verdict within 10 s`; boundary D confirms both directions
  (h12/t11 → blocked; h12/t13.5 → au-magic at 12.0 s).

## Audit Q3 — "binary on writer-attached-at-open-#2"? OVERCLAIM; ≥4 outcomes across a 2-D race

Verdict is not a function of the attachment predicate alone:

- attached@open#2 ∧ close>deadline → `blocked:` (me: h=12; boundary:
  rdwr-forever/parked — writer attached FOREVER still read-blocks).
- attached@open#2 ∧ close<deadline → au-magic (the stable arm).
- detached@open#2 → `blocked:` (author scratch 4/4, mine 8/8+10/10 loaded,
  scribe 20/20, boundary) — OR `exit 2 au-magic` (r67 shell 5/5, same
  signature as the stable arm).
Both predicate values reach both verdict classes. Correct mechanism statement:
the arm needs writer-attached at open #2 **and** EOF (writer close) before the
arm deadline — a conjunction over a window, not a binary predicate.

## Audit Q4 — prior-row byte-stability: VERIFIED on my sample; full-ledger check is the author's still-running job

Post-diff replays by me, byte-identical to committed receipts:
`--probe-transport-dec-act-r67` (3 committed receipts, incl. two minted today),
`--probe-transport-txw-piperefuse-r68`, `--probe-transport-extsuffix-snd-r69`,
`--probe-ui-preempt-act-r65` — all `cmp`-identical. Reviewer independently
replayed 119/119 byte-exact on the pre-diff base. Env override honors
provenance: `MEASURE_FIFO_WRITER_HOLD_S=0.5` run records
`"fifo_writer_hold_s": 0.5` (not silent). Note the corollary: receipts are now
env-conditioned — a leaked env var rewrites 17 prior rows (recorded, so
detectable, but a new nondeterminism channel).

## Landed-defect list

1. **Orphan leak (confirmed live, incl. author's own path):** the canonical
   `transport_matrix` leg uses parent-only `subprocess.run(timeout=)` — every
   h=0/detached leg orphans an ffmpeg blocked in `openat` surviving sox's kill
   and fifo unlink. I orphaned 41 (`/tmp/r70critic-*`, now cleaned by me);
   ~115 pre-existing r67-era zombies remain on this host; the author's new
   `fifo_hold_leg` (killpg) STILL leaked one (PID 3979628,
   `/tmp/fifo-hold-r70-sxj5rjbi`, alive 5+ min) — its "cannot orphan" comment
   is falsified by its own run. Fix: killpg in the canonical arm too
   (verdict-neutral — same `blocked:` signature) + reap sweep.
2. **wall_s floats inside the committed receipt's `reps[]`:** 120 per-rep
   wall times make the new row non-byte-reproducible — first receipt to break
   the ledger's byte-identity discipline. Fix: keep wall_s out of the
   committed receipt (or signature it into the cell verdict as a class).
3. **Tracked `__pycache__/*.pyc` drift:** ` M` in git status — regenerated
   outside the declared two-file scope; commit consistently or leave tracked
   state clean.
4. **`minimum_stable_hold_s` semantics:** a point min over signature-stable
   cells conceals (a) the stochastic band (18 ms mixed), (b) load dependence,
   (c) the upper timeout cliff, (d) chunked tautology. Fix: report h* as
   "highest hold observed diverging + lowest all-stable hold, per run" with
   load note; keep `blocked`-fraction and wall in signatures.
5. **Ledger hang risk, latent:** `run_ledger.py` has no row timeout; the new
   ladder row needs ~4 min but a host-load flip can push a 10-rep h=0 cell to
   ~100 s — and any future wedge is unbounded. Author's own ledger run
   appears stalled mid-row-2 as I write.

## What survives

- The landed ladder works end-to-end, records per-cell distributions as
  declared, default path byte-stable (my 4-mode post-diff replay + reviewer's
  119/119), env override honestly recorded, exclusivity/mode/suffix threading
  complete, `build_artifacts.py` flag added (self-sufficient rebuild).
- Core signal is real and now measured: detached→blocked today (4 seats
  agree), stable arm needs writer-attachment spanning ffmpeg's ~26 ms open-#2
  window; 1.0 s is a defensible margin, not a bound.

## Smallest safe correction

Keep everything landed; change only the receipt semantics:
(1) fold `wall_s` (bucketed) or blocked-fraction into each cell's
`verdict_distribution` signature so mechanism collisions can't fake stability;
(2) relabel `minimum_stable_hold_s` → measured transition band {max diverging
hold, min all-stable hold} per feed, per run, with host-load note;
(3) killpg + orphan reap in the canonical `transport_matrix` fifo leg
(verdict-neutral hardening, prior receipts unchanged);
(4) drop per-rep wall floats from the committed receipt (scratch keeps them);
(5) declare chunked@h*=0 as the binary-arm control, not a hold bound.
Report honestly: "on this host at this load, the detached verdict flips to
blocked for holds ≲18–50 ms; h* is a load-dependent transition zone, not a
host constant; 1.0 s holds ~10–50× margin; the outcome space is
attach×close-before-deadline, not binary-on-attach."
