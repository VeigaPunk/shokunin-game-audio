# R66 non-author verifier — named independent replay of committed state `014b532`

host: devin (same lane). Canonical repo `/home/vgpnk/Projects/shokunin/audio-shokunin` @ `014b532`
("r66: preemptor-map completion — wve falsified-on-RIFF, dec controls, len gates").
Toolchain re-measured: `/usr/bin/sox -> sox_ng` SoX_ng **v14.8.0.1**, ffprobe **n9.0.1**, python **3.14.7**.
Scratch: `corpus/live/r66-verifier/` (untracked). No dispatches, no commits, no tracked edits by me.

Tracked-member SHAs re-measured (`sha256sum corpus/live/round-66/`) — **all six match the author's
published digests exactly**; `pair_dec_hcom.wav` (`325fb967…96cd`) is `cmp`-byte-identical to
r65-critic's scratch `var/D1_hcomdecode+act.wav` (independent convergence claim confirmed).

`cmp -l` (1-based, octal):
- dec pair: **offset 69 only** — `104 'D'` → `105 'E'` (sole-byte demotion inside `FSSD`@65-68).
- gsrt pair: offset 5 (`020`→`021`) + EOF after byte 24 (24 B member ends `ring.bin` w/o NUL@24).
- hcom pair: offsets 5 (`0173`→`0174`), 41 (`0127`→`0130`) + EOF after byte 131 (`HCO` vs `HCOM`).

---

## Claim 1 — reachable preemptor set on RIFF+0x84@256 = exactly {gsrt, hcom}; gsrt ≺ hcom ≺ act ≺ wav — **AGREE**

Spot-checks verbatim:
- `sox -V3 corpus/live/round-66/pair_dec_hcom.wav -n stat` → `` detected file format type `hcom' ``, `Samples read: 9`, exit 0.
- `…pair_dec_act.wav…` → `` `act' ``, `Samples read: 278`, exit 0.

Completeness (geometric, against committed `corpus/live/r64-reviewer/r64rev-formats.c` —
`CHECK(type,p2,l2,d2,p1,l1,d1) if (len >= p1+l1 && !memcmp(data+p1,d1,l1) && !memcmp(data+p2,d2,l2))`):
rows before `act` (:93) are voc/smp/wve/gsrt/amr-wb/prc/sph/amr-nb/txw/sndt/vorbis/opus/hcom (:78–90).
Every row except gsrt and hcom carries a conjunct at offset 0 requiring byte 0 ≠ `0x52 'R'`
(voc `C`, smp `S`, wve `A`, amr `#`, prc `0x37`, sph `N`, txw `L`, sndt `S`, vorbis/opus `O`).
Only gsrt (`ring.bin\0`@16, len≥25) and hcom (`FSSD`@65 + `HCOM`@128, len≥132) anchor off-byte-0 —
reachable on RIFF. Set is *exactly* {gsrt,hcom}: source-enumerated, not merely unobserved.

Ordering re-measured on MY OWN constructions (scratch, `.wav`):
- `v08_riff_all_sigs.wav` = RIFF/WAVE + `ring.bin\0`@16-24 + `FSSD`@65-68 + `HCOM`@128-131 + `0x84`@256 → **gsrt** (gsrt ≺ hcom ∧ gsrt ≺ act in one byte-stream).
- `v09_riff_hcom_act.wav` (hcom sigs + act trigger, gsrt sig cleared) → **hcom** (hcom ≺ act).
- `v10_riff_gsrt_act.wav` (gsrt sig + act trigger) → **gsrt**.
- Tracked corroboration: `pair_dec_hcom`→hcom with `0x84`@256 present (hcom ≺ act); `pair_dec_act`→act on RIFF/WAVE (act ≺ wav); r65 tracked `pair_preempt_both.wav`→**gsrt**, `pair_preempt_hcom`→hcom, `pair_preempt_act`→act — all reproduced live.

## Claim 2 — wve predicate `len≥15 ∧ file[0:15]=="ALawSoundFile**"`; unreachable on RIFF — **AGREE**

Own constructions (`corpus/live/r66-verifier/`):
- `v01_wve_bare.bin` (`ALawSoundFile**`@0, 300 B) → **wve** (positive control; bytes ≥15 unconstrained — zeros pass).
- `v02_wve_len15.bin` (exactly 15 B) → **wve**; `v03_wve_len14.bin` (14 B) → **NONE** — floor is exactly 15.
- `v04_wve_mut14.bin` (byte 14 `*`→`?`) → **NONE** — all 15 bytes load-bearing; trailing `*` is literal `0x2A`.
- `v07_wve_at0_riff_at32.bin` (wve@0, `RIFF`@32, `WAVE`@40, `0x84`@256) → **wve** — the CHECK anchors at offset 0 only; interior RIFF bytes irrelevant.
- `v05_riff_wve_at16.bin` / `v06_riff_wve_at16.wav` (RIFF@0 + wve magic @16 + `0x84`@256) → **act** — wve magic inside a RIFF carrier never reaches the wve row.
- `v11_act_flip0.bin` (tracked act member, byte 0 `R`→`A`) → **NONE** — act/wav rows die with the `RIFF`@0 conjunct.
- `v12_wve_over_riff.wav` (wve magic written over bytes 0–14 of the act member) → detected **wve**, but `file` reports `data` — it is *no longer RIFF*. The only route to wve destroys the RIFF signature.
Byte-0 conflict is geometric: wve needs `0x41`@0; RIFF/RIFX/RF64 need `0x52`@0 (wav rows :95–97). A RIFF-wve file cannot exist on this build.

## Claim 3 — pair_dec_hcom decodes 9 via native hcom reader; pair_dec_act 278 via ffmpeg act bridge on a regular file — **AGREE**

- `sox -V6 pair_dec_hcom.wav -n stat`: `` detected … `hcom' ``, DBUG `hcom:` reader lines (`HCOM data using value compression`), `Input File '(hcom)'`, `Samples read: 9`, exit 0. `sox --i`: `22050 Hz`, `8-bit HCOM`. Route tag is `(hcom)`, **no `(ffmpeg)` marker** — native reader (`sox --help-format hcom`: "Mac FSSD files with Huffman compression", Reads: yes). Raw `sox … -t f32 -` leg: **36 B = 9×4 B**.
- `sox -V6 pair_dec_act.wav -n stat`: `` `act' ``, `Input File '(ffmpeg)'`, `Samples read: 278`, exit 0 — regular-file path input. `act` appears only under the `ffmpeg` pseudo-format alias list (`sox --help-format act` → `Format: ffmpeg`, `Writes: no`). f32 leg: **1112 B = 278×4 B**.
- Forced legs on the hcom member: `-t act` → 3520 samples (ffmpeg hcom demuxer), `-t wav` → 278 — identical to the author's receipt fields (`sox_stat_samples_read: 9`, bridge 3520, native 278, `sox_f32_bytes: 36`).

## Claim 4 — exact length gates 24|25 (gsrt) and 131|132 (hcom) — **AGREE**

- `pair_lengate_gsrt_25.wav` (25 B, `ring.bin\0`@16-24) → **gsrt**, `premature EOF`, exit 2. `pair_lengate_gsrt_24.wav` (24 B, ends `ring.bin` — byte 24 absent) → **wav**, `fmt chunk not found`, exit 2.
- `pair_lengate_hcom_132.wav` (132 B, `FSSD`@65-68 + `HCOM`@128-131) → **hcom**, `premature EOF`, exit 2. `pair_lengate_hcom_131.wav` (131 B, `HCO`@128-130) → **wav**, `Samples read: 43`, exit 0.
- Gate values match the CHECK macro floors: gsrt `len ≥ 16+9 = 25`; hcom `len ≥ 128+4 = 132`.

## Claim 5 — 102-command ledger reproduces — **AGREE (full replay, not spot-check)**

Re-ran all 102 commands verbatim: imported the author's committed `MODES` list from
`corpus/live/r66-author/run_ledger.py` into `corpus/live/r66-verifier/run_ledger_verifier.py`
(same `python3 corpus/fixtures/measure_audio.py [flag]` sequence; my TSV:
`corpus/live/r66-verifier/ledger-r66-verifier.tsv`).

- Totals: **44 exit 0 / 58 exit 1** — matches author's `44/58`.
- Row-by-row vs `r66-author/ledger-r66.tsv`: **102/102 exit codes position-identical; 102/102 failure-summary strings identical** (0 mismatches).
- Receipt bytes: **all 102 fresh receipts byte-identical to the author's on-disk receipts** (`corpus/live/runs/20261014T0232*Z-*`) — cmp semantics over `measurements.json`, 0 diffs, 0 missing.
- Prior-96 mode-pair check (author's `compare_receipts.py` semantics, r66 row 1 ↔ r65 row 1, r66 rows 8–102 ↔ r65 rows 2–96): author's script reports `96 prior-mode pairs checked, 0 mismatches` (ran it read-only); **the same mapping applied to MY fresh receipts vs r65's → 96/96 byte-identical, 0 mismatches**. My row-1 normal receipt is byte-identical to r65's `20261014T014330610722Z-normal`.
- New-mode determinism: three independent `--probe-ui-dec-hcom-r66` runs (two manual + ledger) → byte-identical receipts.
- New-mode receipt fields spot-verified end-to-end: dec_hcom `{hcom, native, stat 9/exit0, bridge 3520, native-wav 278, f32 36B, decode_error_tool: measure_pipeline, KeyError:'duration'}`; dec_act `{act, ffmpeg, 278 on all legs, f32 1112B, pcm_s16le}`; lengate_gsrt_24 `{wav, fmt chunk not found, ffprobe err}`; lengate_gsrt_25 `{gsrt, premature EOF}`; lengate_hcom_131 `{wav, 43 samples, f32 172B}`; lengate_hcom_132 `{hcom, premature EOF, -t wav leg decodes 44}`.

Caveat on my earlier bulk frozen-tree diff: naive suffix-matching vs `r65-baseline/frozen` flags
receipts from *older* rounds (e.g. 20261012T* stamps) as DIFF — those predate the current fixture
set and are outside the claim. Scoped to the r65 ledger's 96 modes the identity is exact, as above.

## Verdicts

| # | claim | verdict |
|---|---|---|
| 1 | reachable preemptor set {gsrt,hcom}; order gsrt≺hcom≺act≺wav | **AGREE** |
| 2 | wve = `ALawSoundFile**`@0 len≥15; geometrically unreachable on RIFF | **AGREE** |
| 3 | hcom 9 native / act 278 ffmpeg bridge | **AGREE** |
| 4 | gates 24\|25 gsrt, 131\|132 hcom exact | **AGREE** |
| 5 | 102-command ledger reproduces | **AGREE** — 102/102 exits+failsums identical; 102/102 receipts byte-identical; prior-96 byte-identity vs r65 confirmed on my own runs |

## Environment / scope notes

- Concurrent uncommitted edits observed mid-session: `LOG.md`, `SCORECARD.md` carry the r66
  adjudication entries (mtime 2026-10-14 01:39 -03, content references "r66-verifier.md: [pending]")
  — **not mine**; I made zero tracked modifications. All six tracked wavs hash-identical after my
  102-run ledger → `build_artifacts.py` rebuilds are byte-deterministic.
- `git status` footprint from me: untracked `corpus/live/r66-verifier/` + `corpus/live/runs/20261014T0445*–0446*`
  receipt dirs (the latter is where `measure_audio.py` writes by design; claim 5 requires running it).
- Scope: verification is detection/route/count facts on this host's SoX_ng 14.8.0.1 USING_FFMPEG +
  ffmpeg n9.0.1 only; wve-reader interior semantics and non-RIFF carriers not re-adjudicated here.

## Blockers

None. Leaf seat — no descendants dispatched.
