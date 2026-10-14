# R70 adjudicator (Sol) — fifo writer-hold ladder: transition band, not a point bound

Round: 70. Wave: `shokunin-train-20261014-w9`. Work commit: `59a7440`
("r70: fifo writer-hold ladder — transition band, not a point bound").

## Declared move (depth/calibration)

Pin `fifo_writer_hold_s=1.0` as a MEASURED determinism bound — ladder
{0, 0.05, 0.2, 0.5, 1.0, 2.0}s on the `dec_act` member (the arm whose
verdict needs the ffmpeg bridge's second open) plus one chunked-feed
variant on `fifo_feed`. Falsifiable claim: a rep-stable h* < 1.0s
exists, OR the verdict is binary on writer-attached-at-open-#2.
Per-cell verdict distributions in the receipt; 119 prior ledger rows
byte-stable.

## Seat convergence

| seat | landing | contribution |
|---|---|---|
| author | partial | complete implementation landed (+252/+9) — env-param hold, chunked feed variant, killpg+start_new_session ladder runner, per-cell distributions; seat died to rate limits before its report (3 respawns); operator integration applied the critic's corrections |
| scout | yes | mechanism map: open #2 exists ONLY on the ffmpeg route ({dec_act, preempt_act}); every other member single-open / hold-invariant; chunked-feed analysis predicted the third cell (feed duration = implicit hold); O_RDWR timing-free holder prior art cited unmerged; orphan-hazard guard |
| critic | yes | **5 defects found, all corrected at integration**: (1) canonical fifo leg lacked killpg — critic falsified "cannot orphan" via its own 5-min survivor; (2) `wall_s` floats broke the ledger's byte-identity; (3) `__pycache__` drift; (4) point-min h* conceals the stochastic band + load dependence; (5) latent ledger-row-timeout note. Report honestly restated: "transition zone, load-dependent, outcome space = attach x close-before-deadline" |
| baseline | yes | frozen `939fe47` archive-only; 119/119 ledger replay (49 exit-0 / 70 exit-1), 106 exact + 13 path-normalized equivalences; independent hold ladder: h=0 10/10 blocked, >=50ms 10/10 exit-2 |
| reviewer | yes | committed r69 replay 119/119 byte-exact; remaining timing constants enumerated (arm_timeout_s=10, +5 join grace, no per-row timeout) |
| boundary | partial | scratch landed (~250 files) but no report — died mid-write |
| scribe / simplifier | never landed | rate-limit churn |
| verifier | never landed | operator verification below |

## Operator verification (adjudicator own reproduction, committed `59a7440`)

- `--probe-fifo-hold-ladder-r70` end-to-end: receipt
  `corpus/live/runs/20261014T124018313832Z-fifo-hold-ladder-r70/measurements.json`
  — oneshot h=0 10/10 blocked / >=0.05 10/10 exit-2; **chunked 10/10
  at every hold incl. h*=0** (the binary-arm control); bands
  {oneshot: 0.0→0.05, chunked: none→0.0}; no `wall_s` in committed
  receipt; `hold_transition_band_s` + `hstar_semantics` fields carry
  the honest shape.
- Byte-stability: `--probe-transport-dec-act-r67` on the committed
  tree vs r69 committed receipt — all 4 transport arms + verdict
  groups + fork pin identical (reap is post-verdict cleanup).

## Measured headline (multi-seat convergence)

- **The bound is a transition zone, not a point**: oneshot
  {h=0 blocked → h>=50ms stable} on this host; critic's finer sweep
  puts a mixed band near ~18ms. `h*` is load-dependent — reported as
  {max divergent, min all-stable} per feed per run.
- **Strict binary-on-attach is falsified by the third outcome**:
  chunked feed lands the normal verdict at h*=0 because delivery spans
  open #2 — attach-through-delivery, exactly the scout's predicted
  third cell.
- **1.0 s holds ~20x margin over the zone** — a defensible default,
  never a measured edge.
- **Orphan falsification → mechanism**: killpg alone insufficient
  (bridge grandchild escapes the child's group); `/proc` cmdline reap
  now backstops both fifo legs — verdict-neutral.

## Bounds

SoX_ng 14.8.0.1 USING_FFMPEG + ffmpeg n9.0.1; this host. The
(0, ~50ms] zone is load-dependent — re-measure on a differently-loaded
host. Outcome space = attach x close-before-deadline. Ledger-row
timeout absence disclosed (critic #5 — bounded but slow under full
divergence). No conformance/fidelity/production inference.

## Verdict — **ADMIT**

- depth: improved locally — point constant → measured band; third
  outcome refutes strict binary-on-attach.
- coverage: improved locally — ladder probe flag + chunked feed +
  reap backstop.
- calibration: unchanged — default preserved; prior-119 byte-stable.
