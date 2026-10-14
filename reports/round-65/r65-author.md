# R65 author — preemptor ordering on RIFF files PINNED (gsrt < hcom < act < wav) + 4-member tracked collision family

host: devin (same lane as R61–R64)
Clean-before: canonical lane repo `/home/vgpnk/Projects/shokunin/audio-shokunin` HEAD `b1e286c`;
worktree `/home/vgpnk/Projects/prymeagnt/audio` (`.shokunin/audio` symlinks into the canonical repo).
Toolchain under test: SoX_ng v14.8.0.1, ffmpeg/ffprobe n9.0.1, python 3.14.7.

## Scoped move — declared claim CONFIRMED: preemptors claim the file, in table order

R63 pinned the `act` predicate (`len≥257 ∧ RIFF@0 ∧ file[256]==0x84`) as one row in
SoX_ng's first-match-wins CHECK table and recorded two RIFF-compatible earlier
rows as preemptor candidates: `gsrt` (`"ring.bin\0"`@16 — the 9-byte C literal,
terminating NUL compared) and `hcom` (`"FSSD"`@65 ∧ `"HCOM"`@128). R65's declared
move: build RIFF+0x84@256 files that also match each preemptor predicate, measure
which detection wins and which reader/route it selects, falsify or pin.

**No preemptor-shaped file routed `act`.** Measured order on 19 collision
variants plus the tracked family: **`gsrt` ≺ `hcom` ≺ `act` ≺ `wav`** — every
matching preemptor claims the file before `act`, and `gsrt` claims it before
`hcom` when all signatures are present. The ordering claim survives; it is now
tracked, not just scratch.

## Empirical sweep (scratch: `corpus/live/r65-author/`)

Generator/prober `gen_collision.py`; **19 variants**, all rows in `results.tsv`.
Two bases: `b_*` = the r61-family 11,588-B valid17 extensible fixture (shared
deterministic payload, 0x84@256 pinned by assignment) and `m_*` = a minimal
257-B RIFF/WAVE shell (exactly the autodetect window). Probes per variant:
`sox -V6 <f> -n stat` (detected/samples/exit), `sox --i`, raw f32 decode,
forced `sox -t {act,gsrt,hcom,wav}` legs, `ffprobe` codec/duration.

### Detection results (`b_*` family, all carrying 0x84@256 unless noted)

| variant | signature deltas vs base | detected | outcome |
|---|---|---|---:|
| `b_base84` | — | act | ffmpeg bridge, 3,839 samples, exit 0 |
| `b_base00` | byte256→0x00 | wav | native reject exit 2 `number of valid bits exceeds…` |
| `b_gsrt` | `ring.bin\0`@16–24 | **gsrt** | exit 2 `premature EOF` (native gsrt reader) |
| `b_gsrt_m23` | `ring.bim\0` (1-B off @23) | act | bridge → `premature EOF` exit 2 |
| `b_gsrt_x24` | `ring.binX` (NUL broken @24) | act | bridge → `premature EOF` exit 2 |
| `b_gsrt_no84` | `ring.bin\0`, byte256→0x00 | **gsrt** | exit 2 — preemptor needs no act byte |
| `b_hcom` | `FSSD`@65 + `HCOM`@128 | **hcom** | exit 2 `bad compression type` |
| `b_hcom_x131` | `FSSD`@65 + `HCOX` (1-B off @131) | act | bridge decodes 3,839, exit 0 |
| `b_hcom_fssd_only` | `FSSD`@65 only | act | 3,839, exit 0 |
| `b_hcom_hcom_only` | `HCOM`@128 only | act | 3,839, exit 0 |
| `b_hcom_x65` | `XSSD`@65 + `HCOM`@128 | act | 3,839, exit 0 |
| `b_hcom_no84` | hcom sigs, byte256→0x00 | **hcom** | exit 2 |
| `b_both` | all three sigs | **gsrt** | exit 2 — earliest matching row wins |
| `b_both_no84` | all sigs, byte256→0x00 | **gsrt** | exit 2 |
| `m_base84` (257 B) | — | act | bridge → `premature EOF` |
| `m_gsrt` | gsrt sig | **gsrt** | exit 2 |
| `m_hcom` | hcom sigs | **hcom** | exit 2 `bad sampling rate divisor` |
| `m_both` | all sigs | **gsrt** | exit 2 |
| `m_gsrt25` (25 B, no RIFF) | gsrt sig only | **gsrt** | exit 2 `invalid/missing file name in header` |

Detected tally over 19 rows: **gsrt 7, act 8, hcom 3, wav 1**. The signature
literals are exact: one byte off anywhere in `ring.bin\0` (`m23`, `x24`) or in
the hcom conjunction (`x131`, `x65`, lone conjuncts) and the file falls through
to `act`. A 25-byte file needs no RIFF at all to detect `gsrt` (its row's length
floor is 16+9).

### Route and reader evidence (the preempted route is terminal)

- `sox --i` on the act member → `Input File '…' (ffmpeg)`, no Duration line
  (the r63 bridge signature); on every collider it exits 1 with the *detected
  handler's own* error — no `(ffmpeg)` tag, no wav-reader error.
- Per-handler forced legs on the same bytes (scratch, `sox -t <h> <f> -n stat`):
  `-t gsrt` → `premature EOF` everywhere; `-t hcom` → `Mac header type is not
  FSSD` when FSSD@65 absent, `Mac data fork is not HCOM` when FSSD present but
  HCOM differs, `bad compression type` when both conjuncts hold — the hcom
  reader re-verifies the same two conjuncts inside startread; `-t wav` →
  `file encoding 0x622e (Unknown) is not supported` on gsrt members (fmt tag
  destroyed by `ring.bin`) vs `number of valid bits exceeds…` on the hcom
  member (fmt intact — `FSSD`@65–68 only touches the data-size field).
- **The collision reruns inside ffmpeg too.** `ffprobe -v debug` on the tracked
  members: `pair_preempt_{hcom,both}.wav` → `Format hcom probed with size=2048
  and score=100` then `Invalid data found when processing input` — ffmpeg's
  hcom demuxer out-scores `wav` (score 99) on the identical signature, so even
  a forced `sox -t act` bridge leg fails `premature EOF` on those files.
  `pair_preempt_gsrt.wav` → `wav` score 99 then `no 'data' tag found` (the
  `ring.bin` write destroyed the fmt-size field). `pair_preempt_act.wav` →
  `wav` 99 → `pcm_s24le` as usual.
- Detection picks the reader once: collider outcomes are the *detected
  handler's verdict on a malformed body* (gsrt's `premature EOF`, hcom's
  `bad compression type`/`bad sampling rate divisor`), not a fallback chain —
  consistent with r63's single-dispatch finding and with r65-critic's
  independent strace (0 child execve on gsrt-detected files) and valid-hcom
  decode counterexample (`reports/round-65/r65-critic.md`).

## Source basis (corroborative; the measurements above stand alone)

Upstream `sox_ng-14.8.0.1` `src/formats.c` (codeberg tag, fetched this round —
same file r64-reviewer independently verified): `CHECK(gsrt,0,0,"",16,9,"ring.bin")`
at :81, `CHECK(hcom,65,4,"FSSD",128,4,"HCOM")` at :90, `CHECK(act,0,4,"RIFF",256,1,"\x84")`
at :93 (`#if USING_FFMPEG`), `CHECK(wav,…)` :95–97 — textual order gsrt ≺ hcom ≺
act ≺ wav, matching the measured winner on every collision file. All other
pre-act rows carry an offset-0 anchor incompatible with `RIFF` (r63 enumeration;
re-verified by reading the full table).

## Tracked changes (additive only; all prior fixtures/modes/thresholds untouched)

`corpus/fixtures/build_artifacts.py` **+40/−1**: `build_ui_preempt_r65_probe()`
emits `corpus/live/round-65/pair_preempt_{act,gsrt,hcom,both}.wav` — the
r61-family valid17 header over the shared deterministic payload
(`0.25·sin 920 + 0.10·sin 1380` ×8191, 5,760 frames), every member 0x84@256.
`act` is the uncollided control — **byte-identical to `round-63/pair_route_84.wav`**
(verified by cmp + sha256); `gsrt` adds `ring.bin\0`@16; `hcom` adds
`FSSD`@65+`HCOM`@128; `both` adds all three. Four argparse flags + newest-first
dispatch branch.

`corpus/fixtures/measure_audio.py` **+65/−4**: four flags
(`--probe-ui-preempt-{act,gsrt,hcom,both}-r65`), mutual-exclusion sum,
builder-flag forwarding, one measurement block at the newest-first head
(default-route `sox -V6` → `sox_detected_format`/`sox_route`/`sox_stat_*`,
plus counterfactual forced legs `sox_bridge_*` (`-t act`) and `sox_native_*`
(`-t wav`), r64 entry-shape extended with `decode_error_tool` naming which
child call raised), and `mode`/`suffix` chain heads prepended.

Pair byte evidence (all members 11,588 B; `cmp -l` 1-based offsets, octal):
- `act↔gsrt`: offsets **17–25** only (9 B, the `ring.bin\0` span).
- `act↔hcom`: offsets **66–69 + 129–132** only (8 B, the two signature spans).
- `act↔both`: 17–25 + 66–69 + 129–132 (17 B); `gsrt↔both`: 66–69+129–132;
  `hcom↔both`: 17–25 — every pair differs only at signature bytes.
- SHA-256: act `cf5edecce1812f0a0a5c1a16f0b2a920118be3f281b3f43638c1bc2f9f6b93e4`
  (== r63 `pair_route_84`), gsrt `477bd371fe1c69d580a0ae008a1f86c94da5184677fad0af32a2e5aac1d9e762`,
  hcom `bfc6141326434a991bbaaa8d9561579a4a659b8bc1a4de8be0554285559f6893`,
  both `a37adc7c16796f8d98d1157298ece5fbcdbba93f766c8d32e24f991c800c94db`.
  Rebuild deterministic (each of 96 ledger builds rewrote identical bytes).

Live routing on the tracked members (`sox -V4`/`--i` verbatim):
- `pair_preempt_act.wav`: `` detected file format type `act' ``; `--i` →
  `Input File '…' (ffmpeg)`; decode 3,839 via bridge (pcm_s24le, 0.080 s).
- `pair_preempt_gsrt.wav`: `` detected file format type `gsrt' `` →
  `FAIL … premature EOF`, exit 2.
- `pair_preempt_hcom.wav`: `` detected file format type `hcom' `` →
  `FAIL … bad compression type`, exit 2.
- `pair_preempt_both.wav`: `` detected file format type `gsrt' `` →
  `FAIL … premature EOF`, exit 2.

## What ran — 96-command ledger (92 prior verbatim + 4 new modes at positions 2–5)

All commands `python3 .shokunin/audio/corpus/fixtures/measure_audio.py <flag>`
from the worktree root; receipts under `corpus/live/runs/<stamp>-<suffix>/measurements.json`.
Runner `corpus/live/r65-author/run_ledger.py`; TSV `ledger-r65.tsv`; comparison
`compare_receipts.py`. Totals: **44 exit 0 / 52 exit 1** (r64's 44/48 plus the
four new exit-1 probes).

Prior-92 replay (my rows {1}∪{6–96} vs r64 rows 1–92): exit sequence
position-identical, failure summaries verbatim, and **all 92 receipts
byte-identical** to the r64 receipt files (`compare_receipts.py`: 0 mismatches).
Normal-run receipt `20261014T014330610722Z-normal/measurements.json` is
byte-identical to r64's normal `20261014T003914751250Z-normal`.

New-mode receipts (deterministic — re-runs produced byte-identical JSON):
- `--probe-ui-preempt-act-r65` → exit 1,
  `runs/20261014T014331736394Z-ui-preempt-act-r65/measurements.json`;
  `ui_preempt_act_r65_probe`: format/duration/level/spectrum 4-gate (the
  r61-valid17 signature); entry records `sox_detected_format: "act"`,
  `sox_route: "ffmpeg"`, stat samples 3,839, bridge 3,839, native exit 2
  (`number of valid bits exceeds…`), codec `pcm_s24le`, 0.080 s.
- `--probe-ui-preempt-gsrt-r65` → exit 1,
  `runs/20261014T014332805968Z-ui-preempt-gsrt-r65/measurements.json`;
  decode-failure entry (`decode_error_tool: "ffprobe"` — ffprobe itself rejects
  the file), `sox_detected_format: "gsrt"`, `sox_route: "native"`,
  `sox_stat_stderr` `premature EOF`, bridge `premature EOF`, native
  `file encoding 0x622e (Unknown) is not supported`.
- `--probe-ui-preempt-hcom-r65` → exit 1,
  `runs/20261014T014333872621Z-ui-preempt-hcom-r65/measurements.json`;
  `sox_detected_format: "hcom"`, `sox_route: "native"`, stat
  `bad compression type`, bridge `premature EOF` (ffmpeg's hcom probe claims
  the same bytes), native `number of valid bits exceeds…` (intact fmt
  underneath).
- `--probe-ui-preempt-both-r65` → exit 1,
  `runs/20261014T014334931555Z-ui-preempt-both-r65/measurements.json`;
  `sox_detected_format: "gsrt"` (earliest matching row beats hcom+act),
  native `file encoding 0x622e`, bridge `premature EOF`.

Setup notes: `python3 -m py_compile` on gen_collision.py + both fixture
scripts → exit 0; `git diff --check` → clean. Two tracked `__pycache__/*.pyc`
binaries differ — mechanical `py_compile` regeneration churn, same disclosure
as r62/r63/r64; parent decides. One caught-and-fixed defect before the ledger:
the first version of the measurement block recorded ffprobe's raw stderr in
`sox_stderr`, which embeds an ASLR context address (`[wav @ 0x…]`) — the entry
now strips ` @ 0x[0-9a-f]+]` → `]` keeping the message verbatim; post-fix
receipts are byte-identical across independent runs for all four modes
(gsrt and both verified twice; act and hcom identical to their ledger
receipts). Pre-fix spot-run receipts remain in `corpus/live/runs/` — they are
per-run complete and superseded by the final-ledger rows above.
No `lsp` device is exposed on this substrate — symbol-adjacent edits (chain
heads, exclusion sum) applied by hand against read file text, per the
fallback rule (same as r64).

## Per-axis claim (author evidence only; verdict belongs to verifier + adjudicator)

- **depth**: the preemptor ordering went from "two candidates recorded" to a
  measured total order `gsrt ≺ hcom ≺ act ≺ wav` — conjunction-exact
  (one-byte-off and lone-conjunct variants all fall to `act`),
  byte-256-independent (`*_no84` rows), minimal-file confirmed (257-B shells,
  a 25-B no-RIFF gsrt hit), and double-layered (ffmpeg's own probe re-runs the
  contest: hcom score 100 > wav 99 inside the bridge).
- **coverage**: a 4-member tracked family where detection flips on signature
  spans alone — {act,gsrt} and {act,hcom} are the "preemptor wins" pairs,
  {hcom,both} and {gsrt,both} pin the preemptor-vs-preemptor order; receipts
  carry detected format, route, all three forced-leg verdicts, and the
  decode_error_tool field. Ledger 92→96 commands.
- **calibration**: prior-92 exits position-exact, all 92 receipts
  byte-identical, normal receipt byte-identical to r64's; new probes land
  inside expected failure classes (4-gate on the act member, decode-failure
  entries on colliders); ASLR nondeterminism caught and normalized before the
  ledger.

## Conditional replay shape (for the non-author verifier)

96 commands = the r64 92 verbatim with `--probe-ui-preempt-{act,gsrt,hcom,both}-r65`
inserted newest-first at positions 2–5 (TSV order in `ledger-r65.tsv`).
Expected 44 exit 0 / 52 exit 1; prior-92 receipts byte-identical to r64's;
new receipts deterministic (each re-produced byte-identical JSON).

## UNKNOWNs / limits

- Verified on this host only: SoX_ng 14.8.0.1 handler order + ffmpeg n9.0.1;
  the `act` row is `#if USING_FFMPEG` — ffmpeg-less builds reorder (gsrt/hcom
  still precede wav; AUTO_DETECT_SIZE shrinks to 132).
- Sweep coverage: two base families (r61 valid17 fixture, 257-B shell).
  Colliders were measured at detection + forced-leg level; preemptor readers'
  acceptance criteria on well-formed bodies is out of scope (r65-critic's
  valid-hcom decode shows `hcom`-detected files CAN decode when the body is
  genuinely hcom — the tracked members pin detection, not reader semantics).
- stdin/pipe detection on colliders unexercised here (r65-critic probed a
  stdin case; my tracked controls cover regular files only).
- The gsrt literal's NUL conjunct is pinned by `b_gsrt_x24`; the hcom
  conjunction by the lone-conjunct and one-byte-off rows. No claim that other
  exotic pre-act collisions exist beyond the enumerated two rows.
- No standards-conformance, decoder-correctness, fidelity, audibility,
  production, rights, engine, or promotion claim — local fixture measurements.

## Blockers

None. No labrat dispatched this round (the sweep was cheap enough to run
directly). No commit/push/merge performed; parent integrates.
