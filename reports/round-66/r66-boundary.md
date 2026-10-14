# Round 66 — boundary (revenger): preemptor-map edges — wve decodes on pipe; RIFX/RF64 keep hcom live; rows 78–97 fully pinned; tracked members fork on transport

Seat: **revenger** — reconstruct host behavior from executable evidence. Scope: the five
edge probes of the r66 preemptor-map completion — (1) ordering on stdin, (2) RIFX/RF64
variants, (3) co-satisfaction with post-act rows, (4) forced `-t` legs on mismatched
bodies, (5) any unmapped CHECK row between wve and wav. Host: `sox` = SoX_ng 14.8.0.1
(`/usr/bin/sox -> sox_ng`), ffmpeg/ffprobe n9.0.1 (identical toolchain to r62–r65 and to
the author's landing). Work scratch-only under `.shokunin/audio/corpus/live/r66-boundary/`
(symlinked into the canonical repo); `git status` shows my writes confined to untracked
`corpus/live/r66-boundary/` — zero tracked mutation. Author landed on HEAD `30e5e32`
as uncommitted working-tree state: `build_artifacts.py` +113/−1, `measure_audio.py`
+93/−4, six `corpus/live/round-66/` members.

Prior scratch was partially complete on arrival (generator, 79 probes, full
13-mode matrix, 768-file sweep). Verified rather than restarted: `gen_probes.py`
regenerated into a clean dir → **byte-identical tree** (`diff -r` clean); `run_sweep.sh`
recreated and re-run → `sweep.tsv` **reproduced byte-identical**; fresh re-probes of
`b_wve_hcomsig_dec`, `d_rifx_hcom`, `e_riff_avi_hcom`, `g_amrnb_hcom` match the recorded
matrix. Added 12 fixtures (`gen_probes_p.py`, `run_matrix_p.sh`): the voc/smp ordering
pins the prior matrix lacked, mutual-exclusivity demonstrators, and byte-identical
copies (`t_*`) of the six tracked round-66 members for transport/forced-t coverage the
author left unexercised. Totals: **91 fixtures × 13 modes = 1,183 matrix rows + 768
sweep rows**, verbatim logs in `runs/logs/`, SHAs in `runs/probe-shas.txt` /
`runs/sweep-shas.txt`.

Source corroboration (`corpus/live/r64-reviewer/r64rev-formats.c`, diff-verified == the
installed build's upstream tag per author+reviewer): CHECK rows at
`voc(78) → smp(79) → wve(80) → gsrt(81) → amr-wb(82) → prc(83) → sph(84) → amr-nb(85)
→ txw(86) → sndt(87) → vorbis(88) → opus(89) → hcom(90) → act(93, USING_FFMPEG) →
wav(95 RIFF / 96 RIFX / 97 RF64)`. Lines 91,92,94 are preprocessor/comment — **no
unmapped CHECK row exists between wve and wav** (edge 5 resolved: none left).

## wve byte predicate — empirical pin (independent of author's W-series)

| evidence | result |
|---|---|
| `a_wve_14` (14 B) vs `a_wve_magic15`/`n_wve_15` (15 B) | no-detect vs `wve` → floor = **15** exactly |
| `a_wve_pos00_mut`…`pos14_mut` (each byte flipped) | all 15 → no detect — **every byte required** |
| sweep: pos {0,7,14} × 256 values, 768 files | **3 detections only**: v0x41@0 (`A`), v0x6e@7 (`n`), v0x2a@14 (`*`) — exact-match bytes, `*` is literal not wildcard |
| `a_wve_valid` (18-B ID1 + nsamp + pad + data) | `wve`, **decodes 16 samples, all transports** |
| `a_wve_badid` (bytes 15–17 `XYZ`) | detected `wve`, reader dies `can't find Psion identifier` |
| `n_wve_31` / `n_wve_32` | detect `wve` both; reader EOF at 31, **opens at 32** (reader floor = 32 B) |
| `b_wve_dec_actbyte` / `e_wve_ftyp32` (declared nsamp < actual data) | file+redir: WARN `file header gives the total number of samples as N but file length indicates…`; **pipe: no WARN** — strace `lseek(0,0,SEEK_CUR) = -1 ESPIPE` (`runs/strace-wve-pipe.txt`) |

Predicate (measured): `len ≥ 15 ∧ file[0:15] == "ALawSoundFile**"` — a single @0
conjunct. Convergent with author W-series and reviewer's p-fixtures (three independent
seats, same predicate). Detector 15 B < reader's 18-byte ID1 (`ALawSoundFile**\0\x0f\x10`
+ BE32 nsamp + 10-B pad): the **opposite asymmetry to gsrt** (detector 9 B > reader's
8-byte memcmp). The declared-length WARN is **seekable-gated** — same fingerprint as
gsrt's checksum WARN (present on file+redir, absent on pipe).

## Complete row map 78–97 (measured; first match wins; all transports agree on detection)

| row | predicate span | vs gsrt(81) | vs hcom(90) | vs act(93)/wav | coexists with RIFF@0? |
|---|---|---|---|---|---|
| 78 voc | `Creative Voice File\x1a` @0–19 | **range-incompatible** (bytes 16–19 = `ring`) | `p_voc_hcom` → **voc** | byte-0 `C` ≠ `R` → impossible | no |
| 79 smp | `SOUND SAMPLE DATA` @0–16 | range-incompatible (byte 16 `A`≠`r`) | `p_smp_hcom` → **smp** | byte-0 `S` ≠ `R` → impossible | no |
| 80 wve | `ALawSoundFile**` @0–14 | `b_wve_gsrt` → **wve** | `b_wve_hcomsig_dec` → **wve** | byte-0 `A` ≠ `R`/`RIFX`/`RF64` → impossible | **no (geometric)** |
| 81 gsrt | `ring.bin\0` @16–24 | — | `g_*_gsrt` → **gsrt** (8 rows beaten) | beats avi/mp4 rows (`e_riff_avi_gsrt`, `e_ftyp_gsrt`) | yes (@16 only) |
| 82 amr-wb | `#!AMR-WB\n` @0–8 | loses | `g_amrwb_hcom` → **amr-wb**, decodes 4,160 | byte-0 `#` ≠ `R` | no |
| 83 prc | `\x37\x00\x00\x10\x6d\x00\x00\x10` @0–7 | loses | `g_prc_hcom` → **prc** `not a Psion Record file` | `0x37` ≠ `R` | no |
| 84 sph | `NIST_1A` @0–6 | loses | `g_sph_hcom` → **sph** `error reading header` | `N` ≠ `R` | no |
| 85 amr-nb | `#!AMR\n` @0–5 | loses | `g_amrnb_hcom` → **amr-nb** (see div. 6) | `#` ≠ `R` | no |
| 86 txw | `LM8953` @0–5 | loses | `g_txw_hcom` → **txw**, 178 smp file/redir — **pipe refused** | `L` ≠ `R` | no |
| 87 sndt | `SOUND\x1a` @0–5 | loses | `g_sndt_hcom` → **sndt** `invalid rate value` | `S` ≠ `R` | no |
| 88 vorbis | `OggS`@0 ∧ `vorbis`@29 | loses | `g_vorbis_hcom` → **vorbis** `input is not an Ogg Vorbis…` | `O` ≠ `R` | no |
| 89 opus | `OggS`@0 ∧ `OpusHead`@28 | loses | `g_opus_hcom` → **opus** `input is not an Ogg Opus…` | `O` ≠ `R` | no |
| 90 hcom | `FSSD`@65 ∧ `HCOM`@128 | wins over all 82–89 | — | beats act+avi+mp4 (`e_riff_avi_hcom` → hcom 9 smp; `e_ftyp_hcom` → hcom 9 smp) | **yes (decodes)** |
| 93 act | `RIFF`@0 ∧ `\x84`@256 | loses | loses | beats avi(176)+mp4(216): `e_riff_avi_act`, `e_riff_ftyp_act` → **act** | self |
| 95–97 wav | {RIFF,RIFX,RF64}@0 ∧ `WAVE`@8 | loses | loses | residual below act's 0x84 conjunct | self |

`p_voc_intact`/`p_voc_broken_gsrt` and `p_smp_intact`/`p_smp_broken_gsrt` demonstrate the
voc/smp↔gsrt exclusivity empirically: on the same 300-B carrier, whichever signature is
byte-intact wins (`voc`/`smp` vs `gsrt`); no byte stream can satisfy both. The r65
"unreachable-by-construction" note is now measured both directions.

## Edge 1 — stdin: wve decodes on pipe; two readers hard-refuse pipes; tracked act member forks

| fixture | file | `cat f \| sox -` | `sox - < f` |
|---|---|---|---|
| `b_wve_dec` (100 alaw) | wve 100 exit 0 | **wve 100 exit 0** | wve 100 |
| `b_wve_hcomsig_dec` (wve + live hcom chain + 0x84) | wve **268** | wve **268** | wve 268 |
| `a_wve_valid` (16) / `a_wve_valid0` (0) | wve 16/0 | wve 16/0 | wve 16/0 |
| `e_wve_ftyp32` (wve + ftyp@32 in payload) | wve 168 +WARN | wve 168 **no WARN** | wve 168 +WARN |
| `z_gsrt_ulaw` (control) | gsrt 1,000 +WARN | gsrt 1,000 **no WARN** | gsrt 1,000 +WARN |
| `*_gsrt` carriers (RIFF/RIFX/ftyp/amr/prc/sph…) | gsrt FAIL `premature EOF` | **gsrt opens, 0 smp exit 0** | `premature EOF` |
| `z_hcom_dec` / all hcom carriers | hcom 9 | hcom 9 | hcom 9 — transport-invariant |
| `*_act` carriers | act: decode-or-EOF | act FAIL `can't find Sun/NeXT/DEC identifier` | act FAIL `premature EOF` |
| `g_txw_*`, `p_smp_*` | txw 178 / smp fail `header is not version 2.1` | **`input must be a file, not a pipe`** | same as file |

Answers to the edge question: **yes, wve's reader decodes through a pipe** — wve has no
seekable gate in its read path (the only seekable-coupled behavior is the WARN-vs-length
check, strace-confirmed ESPIPE). gsrt's r65 transport fork reproduces verbatim on every
new carrier shape. act's ffmpeg bridge still dies on pipe (pending-buffer poison, r64
mechanism). **New transport class found**: `txw` and `smp` readers reject non-seekable
input outright (`input must be a file, not a pipe`) — detection fires, open refuses.
Three distinct stdin behaviors now pinned: pipe-refusing readers (txw, smp),
seekable-gated side paths (gsrt checksum pass, wve length WARN — silent on pipe),
transport-insensitive readers (hcom, wve decode path, amr).

**On the tracked members** (`t_*` = `cmp`-verified byte-identical copies of
`corpus/live/round-66/`; SHAs match author's published values):

- `t_pair_dec_hcom.wav` → `hcom`, **9 samples on all three transports** (reader is
  sequential — invariant as r65 predicted). `-t wav` leg decodes **278** (the suppressed
  wav member is genuinely readable); `-t act` pipe → **3,520** via ffmpeg's hcom
  demuxer (author's bridge leg reproduced).
- `t_pair_dec_act.wav` → `act`, **278 samples on file, exit 0** — but on **pipe**
  FAIL `can't find Sun/NeXT/DEC identifier`, on **redir** FAIL `premature EOF`.
  **The tracked dec pair carries a latent transport fork**: identical 600-B files
  differing by one byte (@68 `D`→`E`); the hcom member decodes everywhere, the act
  member decodes only on a seekable path. Author's legs recorded file-mode only;
  receipts capture `act` as decode-0 where the pipe verdict is FAIL.
- `t_pair_lengate_gsrt_24` → `wav` `fmt chunk not found` (all transports);
  `t_pair_lengate_gsrt_25` → `gsrt`; pipe leg dies `invalid/missing file name in
  header` (r65's 25–31 ladder rung — checksum skipped on pipe, EOF at filename field),
  file/redir `premature EOF` (checksum pass on RIFF-derived file_size).
- `t_pair_lengate_hcom_131` → `wav`, **43 samples exit 0 all transports** (the
  cleanest fallthrough evidence — below-gate member is a working wav); `-t hcom` leg →
  `Mac data fork is not HCOM` (HCOM truncated to `HCO` — hcom ladder step 2).
  `t_pair_lengate_hcom_132` → `hcom` `premature EOF`; `-t wav` decodes **44**
  (suppressed member readable).

## Edge 2 — RIFX/RF64 variants of the whole family

| fixture | detects | terminal |
|---|---|---|
| `d_rifx_act.wav` (RIFX+WAVE+0x84) | `wav` (row 96) | `fmt chunk not found` — act's `RIFF`@0 conjunct is **literal** |
| `d_rf64_act.wav` (RF64+WAVE+0x84) | `wav` (row 97) | `fmt chunk not found` |
| `d_rifx_gsrt.wav` | `gsrt` | file/redir `premature EOF`; pipe opens 0 smp |
| `d_rifx_hcom.wav` | **`hcom`** | **decodes 9 samples, all transports** |
| `d_rf64_hcom.wav` | **`hcom`** | **decodes 9 samples, all transports** |

`CHECK(hcom)` has no @0 conjunct → on RIFX/RF64 carriers hcom(90) still preempts the
wav rows 96/97 **and its reader decodes the full 9-sample stream** — the
DECODABLE-preemptor behavior survives the byte-0 container swap. act(93) does not fire
on RIFX/RF64 (needs literal `RIFF`), so the "act slot" on those containers is plain wav.

## Edge 3 — post-act co-satisfaction: earliest wins, no exception

`e_riff_avi_{act,gsrt,hcom}` (RIFF+`AVI `@8): `act`/`gsrt`/`hcom` — the pre-act winner
never yields to avi(176). `e_riff_ftyp_act` (RIFF + `ftypisom`@4 over the size field):
`act` — act(93) < mp4(216). `e_ftyp_{gsrt,hcom}.bin` (non-RIFF ftyp carriers):
`gsrt`/`hcom` — both beat mp4(216), hcom decodes 9. `e_wve_ftyp32` (`ftypisom` inside
wve payload @32): `wve`, 168 samples — interior post-act signatures are inert; only
offset-anchored conjuncts matter. Combined with r65's probe set: every row after act
tested so far loses to the earliest matching preemptor.

## Edge 4 — forced `-t` legs on mismatched bodies: reader signatures ≠ detector signatures

Per-fixture forced legs (`pipe-t{wve,gsrt,hcom,act,wav}` + `file-t{wve,gsrt,hcom}` on all
91 files) give a clean reader-level map:

- `-t wve` on every non-wve body → `can't find Psion identifier` (18-B ID1 check; the
  reader is *stricter* than its 15-B detector — opposite of gsrt).
- `-t gsrt` on `b_wve_gsrt` (wve+ring.bin carrier) → **opens, 0 samples, exit 0**:
  the reader's 8-byte `ring.bin` memcmp accepts a file its own row never reached.
  On bodies without the id → `invalid/missing file name in header`.
- `-t hcom` decodes **9 samples on every carrier that embeds the chain** — including
  files detected as `wve`/`voc`/`smp`/`prc`/`sph`/`txw`/`amr-*`/`opus`/`vorbis` —
  proving the suppressed member is decodable on each (detect ≠ accept boundary).
  Ladder re-confirmed: `Mac header type is not FSSD` → `Mac data fork is not HCOM` →
  `bad sampling rate divisor` (`c_riff_wve16_hcom`, bare FSSD+HCOM without chain) →
  `premature EOF`.
- `-t act` (ffmpeg bridge) on hcom-bodied files engages ffmpeg's **hcom demuxer**:
  320 samples on the 200-B `z_hcom_dec`, 1,120 on 300-B carriers, **3,520 on the 600-B
  `t_pair_dec_hcom`** — the bridge's yield scales with file size, always diverging
  from SoX-native 9 (cross-implementation decode divergence, r65-convergent).
  On `g_amrnb_actbyte` → 3,520 (amr misread as au-family stream).
- `-t wav` failure vocabulary is three-valued: `RIFF header not found` (no RIFF@0),
  `fmt chunk not found` (RIFF+WAVE, no fmt), **`header not found`** (RIFF + `AVI `@8 —
  the wav reader distinguishes a foreign RIFF form-type).

## Divergences / disclosures (measured)

1. **wve decodes on pipe** (edge-1 answer); its only transport-sensitive behavior is
   the seekable-gated declared-length WARN (strace ESPIPE evidence).
2. **txw and smp readers hard-refuse pipes** — `input must be a file, not a pipe`
   after successful detection. Third transport class beyond gsrt's behavioral fork and
   act's bridge poison.
3. **Tracked dec pair forks on transport**: `pair_dec_act` decodes 278 on file but
   fails on pipe/redir (`Sun/NeXT identifier` / `premature EOF`); `pair_dec_hcom` is
   invariant (9 everywhere). The author's single-transport receipts pin detection but
   not this asymmetry — noted for the verifier, not a defect in the members.
4. **hcom preempts wav on RIFX/RF64** and decodes 9 — wav's rows 96/97 lose to row 90;
   act never fires without literal `RIFF`.
5. **voc reader fails with an empty error string** (`can't open input file
   'p_voc_hcom.bin': ` — nothing after the colon) on all transports.
6. **amr-nb decode progress is transport-sensitive**: `g_amrnb_hcom` reads 800 samples
   on file/redir vs **1,120 on pipe** (warn-level `amr: invalid block type`, exit 0
   both) — same bytes, different decode count. Mechanism not established (inference:
   frame-boundary alignment vs buffered read chunking; flagged, not asserted).
   `g_amrnb_actbyte` (same body minus hcom chain) reads 3,520 uniformly.
7. Detector-vs-reader asymmetry runs **both directions**: wve detector 15 B < reader
   18 B; gsrt detector 9 B > reader 8 B (r65). `pipe-tgsrt` opens a wve-detected file;
   `-t wve` dies on every non-ID1 body.
8. ffprobe disagreements recorded as data: detects `hcom` on every hcom-chain carrier
   regardless of SoX's detected type (`b_wve_hcomsig_dec`, `d_rifx_hcom`,
   `p_voc_hcom`, …); `voc` unknown-header-size on `p_voc_intact`; avi/mp4 probe
   attempts on e_* files. ffprobe ordering is unrelated to SoX's.

## Eliminated hypotheses

- "wve is reachable on a RIFF-family file" — falsified geometrically AND empirically
  (author's N=16 battery + my `c_riff_*` carriers: magic at @16/@40 inside RIFF is
  inert; byte-0 `A` vs `R`/`RIFX`/`RF64` is disjoint). No wve-collision member exists
  or can exist on this build's row order.
- "stdin ordering differs from file ordering" — **detection** is transport-invariant
  on every one of 91 fixtures (file ≡ pipe ≡ redir in the `detected` column; only
  reader-side behavior diverges).
- "CHECK rows remain unmapped between wve and wav" — none: 82–89 all probed
  co-satisfying hcom; 91/92/94 are preprocessor lines; 78/79 pinned against hcom.
- "voc/smp vs gsrt ordering is merely unreachable" — upgraded to demonstrated mutual
  exclusivity (`p_*_intact` vs `p_*_broken_gsrt` flip detection on the same carrier).

## UNKNOWNs / limits

- Same-host verification only (SoX_ng 14.8.0.1 + ffmpeg n9.0.1, USING_FFMPEG build;
  ffmpeg-less builds drop `AUTO_DETECT_SIZE` to 132 and compile out act — untested
  source-level inference; wve/gsrt/hcom/voc/smp geometry unchanged by it).
- amr-nb 800-vs-1,120 transport divergence is measured, not mechanized.
- wve reader internals beyond `start_read` (ID2 semantics, checksum behavior) unprobed.
- voc/smp readers' full failure ladders unprobed beyond the first rung.
- `use_magic` path unexercised (off by default). No fidelity/audibility/standards or
  production claims — detection+decode measurements only.

## Next-round surface proposals

- **Transport-aware receipts**: the tracked dec pair's fork (act member: file-decode /
  pipe-fail) is invisible to the current single-mode receipt schema — propose an
  optional pipe leg in `measure_audio.py` for preemptor-family members, or record
  `sox_pipe_exit_code` alongside `sox_f32_*` (the fork is exactly what r65 pinned on
  gsrt and r64 on the ffmpeg route).
- **smp/txw pipe-refusal pins**: two readers reject non-seekable stdin with a distinct
  error — a cheap tracked member would pin "detection fires, open refuses".
- **wve reader floor**: n_wve_31|32 measured 31→EOF / 32→open(0); the ID1/ID2/pad
  internal gates (nsamp vs actual, ID2 contents) are unmapped — a dictsize-style
  ladder for wve is open territory.

## Confidence

**High.** 1,183 executed matrix rows + 768 sweep rows, every detection claim backed by
a verbatim `-V4`/`--i`/ffprobe log in `runs/logs/`; generator regen diff-clean; sweep
re-run byte-identical; tracked members `cmp`-verified before probing; strace ESPIPE
evidence for the wve WARN gate; three-seat convergence on the wve predicate (author
W-series, reviewer p-fixtures, this sweep). Source citations corroborative only. One
inference flagged (amr-nb mechanism), one empty-string voc error recorded verbatim.

## Receipts

- `corpus/live/r66-boundary/gen_probes.py` (79+768 fixtures, deterministic),
  `gen_probes_p.py` (12 supplementary), `run_matrix.sh`, `run_matrix_p.sh`,
  `run_sweep.sh`.
- `corpus/live/r66-boundary/probes/` — 91 matrix fixtures + `sweep/` 768.
- `corpus/live/r66-boundary/runs/matrix.tsv` — 1,183 parsed rows;
  `runs/sweep.tsv` — 768 detect-only rows; `runs/logs/` — verbatim output;
  `runs/probe-shas.txt` / `runs/sweep-shas.txt` — fixture SHAs;
  `runs/strace-wve-{pipe,file}.txt` — lseek evidence; `runs/README.txt` — index.
- Tracked members probed via byte-identical `probes/t_pair_*.wav` copies
  (`round-66/` SHAs `325fb967…`/`777b6764…`/`e7db9976…`/`ede4161b…`/`6fd9f471…`/
  `a1abdac4…` — all match author's published values).
