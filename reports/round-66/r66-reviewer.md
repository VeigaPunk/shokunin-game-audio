# R66 reviewer — audit of r65 committed state (`1b0d276` + `30e5e32`) + wve collision scan

Seat: **reviewer** — audit-only; no tracked mutation performed or proposed. Host:
`sox` = SoX_ng **14.8.0.1** (`/usr/bin/sox`, USING_FFMPEG build), ffmpeg/ffprobe n9.0.1 —
identical toolchain to the round-65 record. Scratch: `corpus/live/r66-reviewer/`
(probes `p1`–`p8`, `reruns/` verbatim `-V4`/`-V2` captures, `pairfile-list.txt`,
`allfiles-list.txt`). Re-execution ran from the lane worktree
`~/Projects/prymeagnt/audio` so `.shokunin/audio` resolves through the symlink into the
canonical repo, matching `run_ledger.py`'s invocation contract. Post-audit
`git status`: **0 tracked modifications** (untracked = prior-round `runs/` receipts +
my `r66-reviewer/` scratch only).

**LSP note**: no language server answers this repo's files on this host (no `lsp`
device available to this seat); caller/definition checks are text-grep fallbacks.
All load-bearing verdicts below are live `sox` executions, which are the stronger
evidence class for an autodetect audit anyway.

## Verdict summary

| audit item | result |
|---|---|
| `pair_preempt_*` re-run verbatim (detection lines, exits, `-t act`/`-t wav` legs) | **SURVIVES** — 4/4 members, every leg byte-consistent with r65 records |
| bounded ledger replay (4 new rows + 4 prior) | **SURVIVES** — 8/8 exits + failure summaries identical to `ledger-r65.tsv` |
| knowledge-entry ordering table `gsrt ≺ hcom ≺ act ≺ wav` | **SURVIVES** — `pair_preempt_both` detects `gsrt` (not `hcom`), falsifiable recheck #1 passes |
| critic corrections (9-sample hcom decode, EOF non-attribution, seekability) | **SURVIVES** — all three reproduced on the critic's own tracked variants |
| rebuild determinism `build_ui_preempt_r65_probe()` | **SURVIVES** — in-place rebuild left `git status` clean; SHAs match |
| latent wve collision scan (61 pair fixtures + all 9,145 tracked files) | **ZERO collisions** — only intentional `m_wve_gsrt.bin` carries the magic |
| wve byte predicate (scout delivery absent — derived empirically here) | `len ≥ 15 ∧ file[0:15]=="ALawSoundFile**"`, `*`s literal; **geometrically unreachable on RIFF** |

One documentation-level finding (LOW, below). No claim fails re-execution.

---

## 1. `pair_preempt` family, verbatim re-run

Commands: `sox -V4 corpus/live/round-65/pair_preempt_<m>.wav -n stat`;
forced legs `sox -V2 -t {act,wav} <f> -n stat`. Captures:
`corpus/live/r66-reviewer/reruns/pp_<m>_{stat,forcedact,forcedwav}.txt`.

| member | detected | stat exit | terminal line | `-t act` | `-t wav` |
|---|---|---|---|---|---|
| `pair_preempt_act.wav` | `act` | 0, **3,839 samples** | — | 0 / 3,839 | **2** `number of valid bits exceeds the number of bits per sample` |
| `pair_preempt_gsrt.wav` | `gsrt` | 2 | `premature EOF` | 2 `premature EOF` | 2 `file encoding 0x622e (Unknown) is not supported` |
| `pair_preempt_hcom.wav` | `hcom` | 2 | `bad compression type` | 2 `premature EOF` | 2 `number of valid bits exceeds…` |
| `pair_preempt_both.wav` | **`gsrt`** | 2 | `premature EOF` | 2 `premature EOF` | 2 `file encoding 0x622e …` |

Every reading matches the knowledge entry
(`corpus/knowledge/2026-10-14-sox-autodetect-preemptor-ordering.md`) and the
critic's tracked-controls table (`r65-critic.md:185-190`): `both` detecting
`gsrt` — not `hcom` — re-pins the ordering; the three colliders fail even under
`-t act` (hcom/gsrt shapes are ffmpeg-fatal: `premature EOF` on the empty
bridge pipe); the `act` member's `-t wav` vb-gate failure and the gsrt members'
`0x622e` encoding failure match the "gsrt collision is never WAV-valid" clause.

**SHA/identity checks**: `sha256sum` — act `cf5edecc…`, both `a37adc7c…`,
gsrt `477bd371…`, hcom `bfc61413…` — all match the recorded prefixes.
`cmp corpus/live/round-65/pair_preempt_act.wav corpus/live/round-63/pair_route_84.wav`
→ clean (byte-identical claim holds). Rebuild determinism: running the four
`--probe-ui-preempt-*-r65` modes rewrites the blobs in place
(`build_artifacts.py:192-220`) and `git status corpus/live/round-65/` stayed
clean — byte-identical regeneration confirmed (knowledge recheck #3 passes).

## 2. Bounded ledger replay — rows 02–05 + 06, 12, 17, 91

`python3 .shokunin/audio/corpus/fixtures/measure_audio.py <mode>` from the
worktree root; fresh receipts under `corpus/live/runs/20261014T0224*Z-*/`.

| row | mode | ledger exit / failsum | replayed exit / failsum |
|---|---|---|---|
| 02 | `ui-preempt-act-r65` | 1 / format·duration·level·spectrum | 1 / identical 4 failures |
| 03 | `ui-preempt-gsrt-r65` | 1 / `decode: default SoX route rejected input` | 1 / identical |
| 04 | `ui-preempt-hcom-r65` | 1 / same | 1 / identical |
| 05 | `ui-preempt-both-r65` | 1 / same | 1 / identical |
| 06 | `ui-extensible-valid-8-r64` (prior) | 1 / format·duration·level·spectrum | 1 / identical |
| 12 | `ui-route-act-84-r63` (prior) | 1 / format·duration·level·spectrum | 1 / identical |
| 17 | `ui-extensible-valid-16-r61` (prior) | 0 / none | 0 / `{}` |
| 91 | `invalid` (prior, 8-probe row) | 1 / 8-entry failsum | 1 / identical incl. `native16_probe: null` |

Receipt schema verified on a fresh receipt
(`runs/20261014T022459979438Z-ui-preempt-hcom-r65/measurements.json`):
`sox_detected_format:"hcom"`, `sox_route:"native"`, and the three legs
(`sox_stat_*`/`sox_bridge_*`/`sox_native_*` with per-leg exit/samples/stderr) —
exactly the attribution-correct shape the critic demanded (`r65-critic.md:201-206`).
Fresh `sox_stderr` fields embed absolute paths — the pre-disclosed same-host
determinism caveat (r63 verifier note), not a new defect.

## 3. Knowledge-entry ordering table + critic corrections, live

**Ordering** (`gsrt ≺ hcom ≺ act ≺ wav`, first-match): covered by §1 —
`pair_preempt_both` satisfies all three signatures and detects `gsrt`.
Auxiliary re-verifications on tracked r65 material:

- `--i` asymmetry: `sox --i pair_preempt_gsrt.wav` → `premature EOF`, **exit 1**
  (vs `-n stat` exit 2) — measured, as recorded.
- Length gates on tracked variants: `E1_hcom_len132` → `hcom`;
  `E2b_gsrt_len25` → `gsrt`; author's boundary members `b_gsrt_m23`,
  `b_gsrt_x24`, `b_hcom_x131` → all `act` (signature-position exactness intact).
- Boundary headline claims re-executed: `coll_gsrt_alaw.wav` file → `gsrt`
  `premature EOF` exit 2, **pipe → 11,076 samples exit 0** (transport
  inversion); `n_gsrt_24`/`n_hcom_131` → no detect vs `n_gsrt_25`/`n_hcom_132`
  → `gsrt`/`hcom` (floors exact); `m_rifx_act` → `wav` `file encoding 0xfeff`;
  `m_rf64_act` → `wav` `fmt chunk not found`; `m_gsrt_hcom.bin` → `gsrt`;
  `m_wve_gsrt.bin` → **`wve`**, exit 2 `can't find Psion identifier`.
- Scout's r66-cited fmt-16 pair re-verified: `pcm_hcom_act` → `hcom`,
  `pcm_hcom68x_act` → `act`, `pcm_hcom131x_act` → `act`; `-t wav` on
  `pcm_hcom_act` emits 2,048 B — the pair's detection-flip claim stands (its
  hcom member still fails its reader — `bad compression type` — so it proves
  flip-only, not decodability; the decodable shape is the critic's D1).

**Critic correction 1 — hcom accepts a crafted RIFF (9 samples)**:
`D1_hcomdecode+act.wav` (sha `325fb967…` matches record) — autodetect →
`hcom`, `Samples read: 9`, exit 0; `--i` → `(hcom)` 22050 Hz `8-bit HCOM`,
**exit 1, no Duration** (the recorded `--i` quirk); `-t wav` → 278 samples
exit 0; `-t act` → 3,520 samples exit 0 (ffmpeg's own hcom demuxer wins
inside ffmpeg). One byte-stream, three working readers — reproduced exactly.

**Critic correction 2 — `premature EOF` does not attribute a reader**:
`A5_gsrt+act.wav` autodetect (gsrt) vs `sox -t act A5` (au-reader-on-empty-pipe)
emit the *byte-identical* FAIL line `premature EOF`, both exit 2 — only the
`-V4/-V6` detection line distinguishes them. Third emitter confirmed:
`E1b_hcom_len131.wav` detects `wav` → `sox WARN wav: premature EOF on input
file` (non-fatal, 43 samples, exit 0). Three emitters, one fatal pair
indistinguishable — reproduced.

**Critic correction 3 — fd seekability is an invisible conjunct**:
`D2_gsrtULAW+act.wav` (sha `bf60b294…`) — seekable file → `gsrt` `premature
EOF` exit 2; `cat D2 | sox - -n stat` → `gsrt`, **88 samples** exit 0,
Duration = **2,761,067,148** samples; a named FIFO in my scratch → `--i`
prints `(gsrt)` 8000 Hz, stat reads 88 samples. File/pipe/FIFO fork
reproduced exactly.

## 4. wve predicate + latent-collision scan

r66-scout delivery status at audit time: **absent** (no
`reports/round-66/r66-scout.md`, no `corpus/live/r66-scout/`). I derived the
predicate empirically in my own scratch; if the scout lands divergent numbers,
this section re-checks cheaply.

**Predicate (empirically pinned, corroborated by source row
`CHECK(wve,0,0,"",0,15,"ALawSoundFile**")` formats.c:80)** — scratch probes
`corpus/live/r66-reviewer/p*.bin`:

| probe | construction | detected | reads as |
|---|---|---|---|
| `p1` | `ALawSoundFile**`@0, 64 B | `wve` | predicate = magic alone, len≥15 |
| `p5`/`p6` | 14 B prefix / exact 15 B | none / `wve` | length floor is **exactly 15** |
| `p4` | `ALawSoundFileXX`@0 | none | `*` is a **literal byte**, not a wildcard |
| `p4b` | `ALawSoundFile*Z`@0 | none | both `*`s compared literally |
| `p2` | wve + `ring.bin\0`@16 + `0x84`@256, **no RIFF** | `wve` | wve preempts gsrt (row 80 < 81) |
| `p3` | wve + gsrt + `FSSD`@65 + `HCOM`@128 + `0x84`@256 | **`wve`** | wve beats gsrt **and** hcom simultaneously |
| `p7` | `RIFF`@0 + `ALawSoundFile**`@64 + `0x84`@256 | `act` | embedded wve magic is inert — offset-0 anchor |
| `p8` | wve@0 + `RIFF`@32 + `0x84`@256 | `wve` | embedded RIFF never fires act |

**Resolution of the r66 ordering question**: wve anchors 15 literal bytes at
offset 0 — geometrically **exclusive** with `RIFF`@0 (they disagree at byte 0).
A "wve-shaped RIFF file" cannot exist; on RIFF+`0x84`@256 files wve is
unreachable and the reachable pre-act set remains exactly `{gsrt, hcom}` —
r65's map is already complete for the RIFF family. On **non-RIFF** files wve
does preempt both (p2, p3, and re-run of tracked `m_wve_gsrt.bin` → `wve`).
The r65 boundary report's phrasing — "the one coexisting pre-gsrt row wins"
(`r65-boundary.md:31,38`) — is exactly right; voc(78)/smp(79) are likewise
@0-anchored and byte-range-incompatible with `ring.bin`@16.

**Latent-collision scan** (byte-prefix read of every tracked path):
- 61 tracked `pair*.{wav,bin,f32,…}` fixtures: **0** carry `ALawSoundFile**`
  at offset 0. gsrt/hcom signature hits are exactly the 8 intentional members
  (4 `corpus/live/round-65/pair_preempt_*` + 4 `r65-simplifier/replica/`
  copies) — no accidental preemption anywhere. 29 files carry `0x84`@256
  (the r61–r65 act families, expected). 6 non-RIFF `.f32` pair members —
  none wve-shaped.
- Widened to **all 9,145 tracked files** (`git ls-files`): exactly **one**
  wve-magic hit — the intentional `corpus/live/r65-boundary/probes/
  m_wve_gsrt.bin`. Zero near-miss `ALawSoundFile*` prefixes.

## Findings by severity

**HIGH/MEDIUM: none.** Nothing in the r65 committed state failed re-execution.

**LOW-1 — SCORECARD wording presents wve inside the RIFF ordering.**
`SCORECARD.md` r65 coverage cell reads "a measured total order —
`wve ≺ gsrt ≺ hcom ≺ act ≺ wav`". In table order wve(80) does precede
gsrt(81), but on RIFF files — the family that cell scopes to — wve is
**unreachable** (offset-0 anchor contradicts `RIFF`; §4 p7). The knowledge
entry is correctly scoped ("on a `RIFF`@0 file only {gsrt, hcom, act, wav,
avi-family} can match"), so this is a summary-cell imprecision, not a data
error — but a reader of the scorecard alone could inherit "wve preempts on
RIFF" as established. Evidence: probes `p1`–`p8` above; formats.c:78-81.

**INFO-1 — r66 scout artifact absent at audit time.** The brief conditioned
the wve scan on the scout's predicate; none was delivered when I audited
(2026-10-14 ~02:30Z). I derived it empirically (§4); if r66-scout lands with
a different predicate or length floor, re-run `p5`/`p6`-style floor probes —
the scan itself needs no redo (it's a byte-prefix test any predicate revision
can be re-applied to).

**INFO-2 — pre-disclosed caveats re-observed, not new defects.** Fresh
receipts embed absolute repo paths in `sox_stderr`/`sox_*_stderr` (r63
verifier's determinism wrinkle; same-host property). ~900 untracked
`corpus/live/runs/*` receipt dirs plus `r64-baseline/tree/` and
`r65-baseline/` sit in the canonical worktree — routine receipt/scratch
accumulation, zero tracked drift.

## Residual risk / verification gaps

- **Same-host bound**: every re-execution is SoX_ng 14.8.0.1 USING_FFMPEG +
  ffmpeg n9.0.1 on this host. The knowledge entry's own recheck triggers
  (version/build change, CHECK-table additions, `AUTO_DETECT_SIZE` resize)
  remain the right ones; a 132-B-window build still drops the `act` row
  (untested here — compile-level claim, recorded as such by r65).
- **`--magic` / `use_magic` path** unexercised again (off by default; r65's
  retained UNKNOWN stands).
- **wve reader semantics** beyond the open guard (`can't find Psion
  identifier`) unexplored — a wve-valid body was not constructed this audit
  (out of scope: the declared question was ordering/preemption, which is
  detection-level).
- **Ledger slice was bounded by brief** (8/96 rows): the four new preempt
  rows + a prior cross-section covering pass/fail/multi-probe shapes. The
  r65 verifier's full 96-row replay remains the exhaustive record; my slice
  found zero divergence.
- **Not re-verified** (bounded): the strace-level execve counts
  (gsrt-native = 0 child execve vs ffmpeg bridge spawn) — detection lines
  already attribute the route unambiguously; the execve claim is consistent
  with every observed leg but I did not re-trace.

## Receipts

- `corpus/live/r66-reviewer/reruns/` — 12 verbatim `sox` captures
  (`pp_{act,gsrt,hcom,both}_{stat,forcedact,forcedwav}.txt`).
- `corpus/live/r66-reviewer/p{1..8}_*` — wve predicate/preemption probes
  (constructions in §4 table; built and run in scratch only).
- `corpus/live/r66-reviewer/{pairfile,allfiles}-list.txt` — the scanned
  file lists (61 pair fixtures; 9,145 tracked paths).
- Fresh measure receipts: `corpus/live/runs/20261014T022{457..504}*-*/`
  (8 probe-mode re-runs §2).
- FIFO used for the seekability leg was created and removed inside
  `corpus/live/r66-reviewer/`.

**Bottom line**: every load-bearing r65 claim — the ordering, the tracked
pair family, the ledger shape, the three critic corrections, and the
boundary/edge table — survives verbatim re-execution on the committed tree.
The wve question resolves empirically as *unreachable-on-RIFF* (and
preemptive-off-RIFF), which confirms rather than amends the knowledge
entry's scoped claim; only the SCORECARD's flattened ordering string
deserves a wording touch-up when a writer next lands.
