# R69 adjudicator (Sol) — extension-suffix sweep + .snd detection fork + CHECK-row census

Round: 69. Wave: `shokunin-train-20261014-w8`. Work commit: `30bb86d`
("r69: extension-suffix sweep — named arm splits 6 ways on identical
bytes; .snd = first detection-fork member; dead-CHECK census 5/130 hit;
ledger 114->119").

## Declared move (coverage)

Sweep the extension-suffix sub-axis of the r68 named-axis fork:
identical no-match bytes under {.wav,.bin,.txw,.f32,.snd} should route
to different handlers; falsifiably, the named arm splits into ≥3
distinct verdict groups by extension alone and `.snd` is the first
tracked member where DETECTION forks on transport name; plus a
dead-CHECK-row census; 114 prior rows byte-stable.

## Seat convergence

| seat | landing | contribution |
|---|---|---|
| author | yes | `build_artifacts.py` +46/−1 (5 byte-identical members), `measure_audio.py` +49/−3 (5 probe flags + census harness); ledger 119 rows 49/70; prior-114 zero mismatches; content contract absorbed (b[0]=b[1]=b[7]=0 arms the sndr gate) |
| scout | yes | pre-measured the whole surface: 7 distinct verdict outcomes predicted; `.snd` content contract discovered before author landed (zeros at {0,1,7} required — r68 member bytes would falsify the clause); census handed over (5/130 hit) |
| critic | yes | VERIFIED the claim on the landed diff; corrected the census as unsound-for-deadness (28/31 "dead" types detect on crafted members; `wma` sole dead-by-construction row — identical GUID to earlier `asf`); falsified scout's RIFX/RF64 dead-verdict; flagged the `check_table.py` sndr-simulator bug (stale — verifier confirmed committed copy correct) |
| boundary | yes | 26 edge names → **12 distinct file-transport verdict classes** (claim ≥3): `.snd` duality (gate-fail→au dispatch, unconditioned au row preempts), starve×extension matrix (`.txw` refuses at every N; `.wav` truncation content-dependent via `lsx_reads` NUL/\n break), **`.aptx`/`.dts` fifo HANG** (ffmpeg child blocks writerless fifo — strace) |
| simplifier | yes | 14 delete-and-measure experiments — all load-bearing (b[7]=0 removal collapses `.snd`→au; 512B keeps rows byte-evaluated); no extraction; corrected author's "+52" miscount (numstat +49/−3) |
| reviewer | yes | r68 committed-state audit survives on all items, 114-row replay byte-identical |
| scribe | yes | VERIFIED on 2 own bodies + author-probe replay; three-tier census (5 ledger-hit / 16+4 all-evidence / 108 rows never-first-match); `.mp3` fifo race + fifo-basename-dots edges; lesson+LOG drafts adopted |
| baseline | yes | frozen `7b8d423` archive-only (177MB tar, deterministic); isolated measure-env replay 49/65 exact, 114/114 rows identical |
| verifier | yes | **AGREE 6/6** on `30bb86d` — independent 119-cmd replay position-identical; 106/119 fresh receipts byte-identical (13 = path-embed tail-slices, post-path identical); members byte-identical to verbatim rebuild; probes deterministic ×6; census reproduced; "first detection fork" confirmed by full-receipt scan |

## Measured headline (multi-seat convergence)

- **Named arm splits ≥6 ways on identical bytes** — verdict is selected
  by basename extension post-table: `.wav`→RIFF-verdict, `.bin`→no-
  handler, `.txw`→{LM8953-verdict on file / pipe-refusal on fifo}
  (3-group member), `.f32`→decode-128, `.snd`→sndr-detect+decode-504;
  boundary added `.au`, `.raw`, `.xyz` classes → 12 file-transport
  verdict classes total.
- **`.snd` = first detection-fork member** — `sox_detected_format`
  forks `sndr`/`None` on named vs anonymous arms (byte-level: `INFO
  formats: detected` line present/absent); ext-gated CHECK row is the
  table's only name-gate; content contract b[0]=b[1]=b[7]=0.
- **Census**: 130 live rows / 77 types; 5 rows ever first-match in
  ledger receipts {gsrt:81, txw:86, hcom:90, act:93, wav:95}; scribe's
  three-tier: 108/130 rows never first-match. **Corrected scope:
  never-first-match ≠ dead** — wma is the sole dead-by-construction row.

## Adjudicator own reproduction (committed tree `30bb86d`)

- `--probe-transport-extsuffix-snd-r69`: fork receipt exact —
  {file,fifo} decode 504 via sndr vs {pipe,redir} can't-determine.
- Verifier's byte-identical independent replay corroborates all five
  probe modes.

## Corrections absorbed this round

- Author's `check_table.py` sndr-row literal-decoding bug — stale at
  committed copy (verifier); simulator citations for `.snd` superseded
  by receipts.
- Census "dead" wording → never-first-match coverage bookkeeping
  (critic demonstration).
- Author report's "+52/−3" → numstat "+49/−3" (simplifier+verifier nit).

## Bounds

SoX_ng 14.8.0.1 USING_FFMPEG + ffmpeg n9.0.1, this host; `.mp3` fifo
racy (SIGTERM), `.aptx`/`.dts` fifo hangs — disclosed hazards, avoided
as members; `.snd` fork requires the {0,1,7}-zero content contract;
census numbers are build-flag-scoped (USING_FFMPEG+SNDFILE+MPC2K). No
conformance/fidelity/production inference.

## Verdict — **ADMIT**

- coverage: **improved locally** — suffix sub-axis + census landed,
  114→119 rows.
- depth: **improved locally** — first detection-fork member (name-gated
  CHECK row), txw 3-way named-arm intersection, rate-selected decode
  pin, 12 verdict classes enumerated.
- calibration: **unchanged** — additive members+flags; prior-114
  byte-identical.

Work commit `30bb86d`; report-last commit follows.
