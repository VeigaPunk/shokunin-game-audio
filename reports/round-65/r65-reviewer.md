# R65 non-author reviewer — r64 committed-state audit + preemptor latent-collision check

Seat: **reviewer** (leaf; authored none of r64). Host devin, 2026-10-14.
Canonical repo `~/Projects/shokunin/audio-shokunin`, HEAD `b1e286c` (r64
adjudication ADMIT); r64 work commit `4c12342` confirmed `merge-base
--is-ancestor` of HEAD. Worktree `~/Projects/prymeagnt/audio`,
`.shokunin/audio` → canonical symlink. Toolchain identical to r64's declared:
SoX_ng v14.8.0.1 (pacman `sox 14.8.0.1-1`, USING_FFMPEG build), ffmpeg/ffprobe
n9.0.1, python3 3.14.7. My only writes: this report +
`corpus/live/r65-reviewer/` scratch (`collision_scan.py`, `collision-scan.tsv`,
`rerun_r64_pairs.sh`, `boundary-rerun.log`, `probe_claims.sh`,
`claims-probe.log`, `gate_*.wav`, `collide_*.wav`, `collision-live-probe.txt`),
plus one harness receipt dir under `corpus/live/runs/` (the runner has no
`--runs` flag; same posture r64-reviewer recorded).

## Verdict: AGREE with every re-executed r64 claim. Zero latent preemptor collisions. No gate-blocking findings.

### 1. r64 boundary pairs re-run — all six match the r64 table exactly

Committed `corpus/live/round-64/pair_valid_{8,9,24,25,56,57}.wav`, probed with
`ffprobe -show_entries stream=codec_name,bits_per_sample` + default-route
`sox -V6 -n stat` + forced-native `sox -t wav -n stat` (log: `boundary-rerun.log`):

| member | SHA-256 vs author-recorded | ffprobe codec/bps | detected | bridge samples/exit | native `-t wav` |
|---|---|---|---|---|---|
| v8  | `bc9878f7…a1927` ✓ | `pcm_u8`/8 | `act` `(ffmpeg)` | 11,520 / 0 | 5,760 / 0 |
| v9  | `02887d11…7378` ✓ | `pcm_s16le`/16 | `act` `(ffmpeg)` | 5,760 / 0 | 5,760 / 0 |
| v24 | `714998b8…bb64` ✓ | `pcm_s24le`/24 | `act` `(ffmpeg)` | 3,839 / 0 | FAIL exit 2 `valid bits exceeds…` |
| v25 | `614845eb…b91c` ✓ | `pcm_s32le`/32 | `act` `(ffmpeg)` | 2,880 / 0 | FAIL exit 2 same |
| v56 | `d4ee4431…f681` ✓ | `unknown`/0 (no codec) | `act` then FAIL | exit 2 `premature EOF` | FAIL exit 2 same |
| v57 | `aa520464…fd94` ✓ | `pcm_s64le`/64 | `act` `(ffmpeg)` | 1,440 / 0 | FAIL exit 2 same |

All six rows reproduce the r64-author/verifier table verbatim, including the
non-obvious bridge-vs-native split (8|9 both native-decode 5,760 — bridge-only
boundary). `cmp -l` vs `round-63/pair_route_84.wav`: exactly one differing byte
at file offset 38 (octal values 010/011/030/031/070/071 vs 021=17) — the
sole-diff claim holds. `file[256]==0x84` on all six (collision-scan.tsv).

### 2. Knowledge entry `2026-10-13-sox-validbits-codec-map.md` — three sharpest claims, live re-execution: all AGREE

**Claim A — non-monotone step map (codec-NONE band 33–56, s64le re-entry 57–64).**
Re-probed the tracked `corpus/live/r64-author/sweep/` variants at every band
edge plus interior and far tail (`claims-probe.log`): vb0→`pcm_s16le`/5,760;
vb1→`pcm_u8`/11,520; vb33→`unknown`/exit 2; vb40→`unknown`/exit 2 (dead-band
interior); vb64→`pcm_s64le`/1,440; vb65→`unknown`/exit 2; vb65535→`unknown`/
exit 2. Every row `act`-detected. The resurrection boundary and the >64 tail
survive re-execution.

**Claim B — the map is gated on the 0xFFFE ∧ cbSize≥22 ∧ PCM-GUID envelope**
(the r64 adjudication's absorbed falsification). I built byte-patched copies of
`pair_valid_24.wav` in my scratch (tracked bytes untouched): tag→`0x0001`
yields `pcm_s16le`/5,760 (valid-bits demoted to extradata, map inapplicable);
cbSize→21 yields `unknown`/exit 2 `premature EOF` (parse gate closed);
subtype-GUID tag→`0x0003` (float path) yields `unknown`/exit 2. Byte-identical
control → `pcm_s24le`/3,839. All three gate legs confirm the precondition
verbatim as recorded.

**Claim C — `s24le + block_align==4·ch + bpcs==24 → pcm_f24le` promotion and
the lossless-3,840 container claim.** Tracked scribe variants re-probed:
`vb024_c32.wav` (ba=4, bps=32) → **`pcm_f24le`/2,880** — promotion fires;
`vb024_c24.wav` (ba=3, bps=24) → `pcm_s24le`/**3,840**; `vb017_c24.wav` →
`pcm_s24le`/**3,840** — the "vb17 on a 24-bit container decodes its nominal
3,840" claim is exact (residue is the alignment×width packet-boundary
interaction, not a codec property).

Corroborating sub-claims also re-verified live: `sox --i pair_valid_57.wav`
prints `Precision: 16-bit` while ffprobe reports `pcm_s64le` — display-artifact
caveat holds; the ffmpeg→au wire is `.snd`/offset 32/size `0xffffffff`/
encoding 3 (s16be)/48 kHz mono on u8, s64le AND f24le inputs — uniform across
widths as boundary recorded.

### 3. Measurer/harness level

`python3 .shokunin/audio/corpus/fixtures/measure_audio.py
--probe-ui-extensible-valid-25-r64` from the worktree root → exit 1; fresh
receipt `corpus/live/runs/20261014T014118286015Z-ui-extensible-valid-25-r64/
measurements.json` records `codec_name=pcm_s32le`, `bits_per_sample=32`,
`sox_detected_format=act`, `sox_route=ffmpeg`, `sox_stat_samples_read=2880`,
native exit 2 with the verbatim valid-bits line, failures `format: expected
PCM16` + `duration: outside ±1 ms` — the author's recorded -25 shape verbatim.
Committed `corpus/live/r64-author/ledger-r64.tsv`: 92 data rows, 44 exit-0 /
48 exit-1, matching author+verifier.

### 4. Preemptor latent-collision check (wave-4 interaction) — CLEAN, ordering corroborated

Static scan of **all 51 tracked `pair_*` fixtures** (`collision_scan.py`,
full TSV committed in scratch): **zero** carry `ring.bin\x00`@16, `FSSD`@65, or
`HCOM`@128; 21 satisfy the act predicate (RIFF@0 ∧ 0x84@256 ∧ ≥257 B) and would
indeed route `act` unimpeded. Bytes actually present: off16–24 is always the
fmt-chunk size+tag area (`28 00 00 00 fe ff…` fmt40-extensible, or
`10 00 00 00 01 00…` fmt16-PCM) — header fields structurally incompatible with
the gsrt literal; off65–68 is the data-size field or payload; off128–131 is
payload. Extending the scan to the **whole tracked tree (7,999 files)** finds
preemptor bytes only inside r63's own deliberate exhibits
(`r63-boundary/variants/v5_wave_hcomSig.wav`, `v6_wave_gsrtSig.wav`,
`r63-critic/var/E_{gsrt,hcom}_*.wav`, `r63-scribe/variants/v17_{gsrt,hcom}.wav`,
`r63-simplifier/scratch/pre*.wav`). The only near-misses — 8-byte `ring.bin`
without the trailing NUL in `E_gsrt_{00,84}.wav` / `pre_gsrt@16+b256=*.wav` —
are r63's own controls documenting that the NUL is compared (they still
detected `act`).

Live ordering check (independent of the wave-4 author's in-flight work):
byte-patched `pair_valid_24.wav` copies in my scratch, `RIFF`@0 and `0x84`@256
kept — `ring.bin\x00`@16 → detected **`gsrt`** → `premature EOF` exit 2;
`FSSD`@65+`HCOM`@128 → detected **`hcom`** → `bad compression type` exit 2
(`collision-live-probe.txt`). Pre-act CHECKs genuinely outrank act on this
host; the r63 ordering record is not falsified — it is reproduced.

**Consequence for r64 mechanism claims: none contradicted.** r64's "all rows
were `act`-detected" and the boundary-pair tables stand precisely because no
tracked fixture carries a preemptor signature. The r64-boundary claim that only
pre-act CHECKs lacking an offset-0 anchor can preempt a RIFF+0x84 file is
consistent with both my scan and the live probes.

## Findings by severity

None blocking; nothing in r64 failed re-execution.

- **Observation (provenance, not a defect):** during my audit, sibling r65
  seats held uncommitted working-tree edits to
  `corpus/fixtures/{build_artifacts,measure_audio}.py` (additive r65 preemptor
  probe flags; `git diff` inspected — the committed `-25` mode path is
  untouched) plus mechanical `__pycache__/*.pyc` churn. My one measurer
  spot-check therefore ran against the working tree rather than HEAD; its
  output matches the r64-recorded fields verbatim, so the evidence value is
  unaffected. Same shared-tree interleaving surface r64-reviewer flagged.
- **Observation:** `r64-boundary/pair_step_{24,25,56,57}.wav` are byte-identical
  to `round-64/pair_valid_{24,25,56,57}.wav` (`cmp -s` clean) — the same four
  bytes tracked under two names/dirs by two seats. Consistent with both
  reports (common `pair_route_84` base, sole byte-38 diff); harmless, but
  auditors should not count them as independent fixture families.
- **Standing caveat (r63/r64 lineage, still true):** receipt `sox_*_stderr`
  embeds the absolute canonical path — byte-identity holds only on this host's
  path layout.
- `r64-boundary/variants/s_valid_00017.wav` verified byte-identical to
  `round-63/pair_route_84.wav` as claimed.

## Residual risk / verification gaps

- I re-ran the six boundary pairs, seven sweep edge/interior/tail rows, three
  gate legs, three cross-container legs, and one measurer flag — I did **not**
  serially replay the full 92-command ledger (r64-verifier did at commit time)
  nor the 74-variant sweep exhaustively (sampled at every boundary).
- r64-boundary's stdin/EPIPE strace recon (recon-a) not re-executed — outside
  this brief's pair+claim scope.
- Same-host scope throughout (SoX_ng 14.8.0.1 + n9.0.1); non-USING_FFMPEG
  build behavior remains the disclosed UNKNOWN.
- My collision probes live in `corpus/live/r65-reviewer/`; the r65 author's
  `corpus/live/round-65/pair_preempt_*` family is untracked working-tree state
  at audit time — related but independent artifacts.
- Leaf seat: no commits, no subagent dispatch, no edits outside report+scratch.
