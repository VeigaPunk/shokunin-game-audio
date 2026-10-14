# Round 65 — boundary (revenger): preemptor ordering edges — stdin inverts the gsrt outcome; RIFF is optional; no fallthrough

Seat: **revenger** — reconstruct host behavior from executable evidence. Scope: the four
edge probes of the r65 preemptor-ordering move — (1) does a preemptor-shaped *stdin* stream
behave differently where the ffmpeg bridge died, (2) is `RIFF` actually required for the
preemptor claims, (3) files matching multiple preemptors, (4) detect-then-fail fallthrough
into a different reader. Host: Arch Linux, `sox` = SoX_ng 14.8.0.1, `ffmpeg`/`ffprobe` = n9.0.1
(same host as r62–r64). All work scratch-only under
`.shokunin/audio/corpus/live/r65-boundary/`; no tracked content modified
(`git status` shows only untracked `corpus/live/r65-boundary/` from this seat).

Source corroboration (sox_ng-14.8.0.1, tree at `/tmp/sox_ng_src/sox_ng/src`): CHECK table
order at formats.c:78–97 is `voc(78) → smp(79) → wve(80) → gsrt(81) → amr-wb(82) → prc(83)
→ sph(84) → amr-nb(85) → txw(86) → sndt(87) → vorbis(88) → opus(89) → hcom(90) →
act(93) → wav(95,96,97)`. `CHECK(gsrt, 0,0,"", 16,9,"ring.bin")` and
`CHECK(hcom, 65,4,"FSSD", 128,4,"HCOM")` carry **no** @0 conjunct — only `act`
(`RIFF`@0 ∧ `\x84`@256, len≥257) does. `gsrt.c:88` gates its whole-file checksum pass on
`file_size >= 2 && ft->seekable`; `hcom.c:75–195` is purely sequential (zero seeks).

## Ordering verdict (empirical; first match wins)

| fixture (all RIFF@0 + 0x84@256 unless noted) | detects | terminal |
|---|---|---|
| `coll_gsrt_{alaw,ulaw,g726}.wav` (ring.bin\0@16) | `gsrt` | file: `premature EOF`; pipe: decode / EINVAL (below) |
| `t_hcom_act.wav` (FSSD@65 + HCOM@128) | `hcom` | `bad compression type` |
| `t_gsrt_hcom_act.wav` (all three) | `gsrt` | gsrt-side fail — never hcom's |
| `m_rifx_act.wav` (RIFX+WAVE+0x84) | `wav` | `file encoding 0xfeff … not supported` |
| `m_rf64_act.wav` (RF64+WAVE+0x84) | `wav` | `fmt chunk not found` |
| `m_rifx_gsrt.wav` (RIFX + ring.bin@16) | `gsrt` | (checksum EOF / EINVAL) |
| non-RIFF `m_{sph,aiff,au}_gsrt.bin` | `gsrt` | gsrt preempts rows 84/98/106 |
| non-RIFF `m_wve_gsrt.bin` | `wve` | wve(80) < gsrt(81) — the one coexisting pre-gsrt row wins |
| non-RIFF `m_gsrt_hcom.bin` | `gsrt` | opens, 0 samples (see quirk 2) |

`voc`(78) and `smp`(79) are **byte-range-incompatible** with `ring.bin`@16 — voc's 20-byte
magic occupies 0–19, smp's 17-byte magic occupies 0–16; `ring.bin`@16 destroys both. No
file can satisfy voc+gsrt or smp+gsrt simultaneously, so the only meaningful statement is
"gsrt is the first *reachable* row on any file carrying `ring.bin`@16" — measured, not
ordering. `wve`'s 15-byte magic ends at 14 → coexists → wins (detected `wve`).

**Cross-validation:** the author's tracked fixtures
`corpus/live/round-65/pair_preempt_{gsrt,hcom,both,act}.wav` are **byte-identical** to my
independently built `coll_gsrt_g726.wav` / `t_hcom_act.wav` / `t_gsrt_hcom_act.wav` /
`coll_act_base.wav` (SHA256 `477bd371…`, `bfc61413…`, `a37adc7c…`, `cf5edecc…` —
`runs/probe-shas.txt` vs `sha256sum round-65/*`). Author receipts
(`corpus/live/runs/*-ui-preempt-*-r65/measurements.json`) record `sox_detected_format`
gsrt/hcom/gsrt/act — convergent with every probe here.

## Edge 1 — stdin: the preemptor's reader survives where the bridge died; indeed it *inverts*

r64 pinned `stdin + autodetect + ffmpeg-route` as dead two ways (pending-buffer poison →
au `can't find Sun/NeXT/DEC identifier`; seekable-stdin fd-offset leak → `premature EOF`).
Reproduced verbatim on `coll_act_base.wav` (file: 3,839; pipe: au-magic fail; redir:
premature EOF). The **native preemptor readers behave entirely differently**:

| fixture | file | `cat f \| sox -` (pipe) | `sox - < f` (seekable stdin) |
|---|---|---|---|
| `coll_gsrt_alaw.wav` / `_ulaw.wav` | gsrt, FAIL `premature EOF` | **gsrt, decode 11,076 samples, exit 0** | gsrt, FAIL `premature EOF` |
| `coll_gsrt_g726.wav` (enc@32–33=2) | gsrt, FAIL `premature EOF` | gsrt, FAIL **`invalid format for this file type`** (+ `INFO gsrt: unsupported encoding: G726`) | gsrt, FAIL `premature EOF` |
| `bare_gsrt_fsbig.bin` (declared 1,600 B > actual 768 B) | FAIL `premature EOF` | **decode 256, exit 0** | FAIL `premature EOF` |
| `bare_gsrt_badck.bin` (corrupt checksum) | WARN `invalid checksum`, decode 1,000 | decode 1,000, **no WARN** | WARN + decode 1,000 |
| `bare_gsrt_{ulaw,alaw,fs0}.bin` | decode 1,000 / 1,000 / 0 | identical | identical |
| `bare_hcom_*.bin` | identical results on all three transports | | |

Mechanism (probed, then source-cited): `gsrt.c:88` — `if (file_size >= 2 && ft->seekable)`
wraps a whole-file checksum scan + `lsx_seeki(4)`. On a RIFF collision file bytes 0–3 =
`"RIFF"` → file_size = 0x52494646 → the scan demands ~1.38 G int16s and dies at EOF
(`premature EOF`) before the id check ever runs. On a **pipe**, `is_seekable` fails
(strace: `lseek(0,0,SEEK_CUR) = -1 ESPIPE`, `runs/strace-badck-pipe.txt`) → the pass is
skipped → id@16 matches → enc@32–33 selects ULAW/ALAW → `lsx_skipbytes(478)` → raw data at
512 → **11,076** samples (11,588 − 512, exactly). The transport flip inverts the outcome on
identical bytes — opposite polarity to the act/ffmpeg route (which works on file, dies on
pipe). Seekable stdin (`< f`) behaves exactly like a file: the pass runs and dies.

- `badck` is the fingerprint: `invalid checksum` WARN on file+redir, **absent** on pipe —
  the pass ran iff `seekable`.
- Declared-length side effect: pipe-mode `Duration` reports the bogus header value
  (RIFF-derived 2,761,067,148 samples ≈ 95 h) — warn-free since `lsx_filelength` can't
  measure a pipe. Decode itself stops at real EOF.
- Pending-buffer fidelity: detection's 257-byte prefetch is replayed byte-exact to native
  readers (decode count matches len−512 precisely; no loss/dup) — the r64 au-reader poison
  was specific to `startread_ffmpeg` swapping `ft->fp` without clearing `pending_count`.
- Forced `-t gsrt` on pipe reproduces the autodetect-pipe outcome exactly (11,076) —
  pending-buffer replay is transparent to the reader.
- hcom's reader never seeks → identical behavior on all three transports (fail ladder and
  16-sample decode alike).

## Edge 2 — RIFF is not required for the preemptor claims

`CHECK(gsrt)` is `ring.bin\0`@16 alone (len≥25); `CHECK(hcom)` is `FSSD`@65 ∧ `HCOM`@128
(len≥132). Bare non-RIFF files decode fully:

- `bare_gsrt_ulaw.bin` / `_alaw.bin` (1,512 B, honest file_size, correct checksum) →
  `gsrt`, 1,000 samples @8 kHz, exit 0 — on every transport.
- `bare_hcom_valid.bin` (168 B; FSSD/HCOM, divisor 2, dictsize 2 leaf-dict) → `hcom`,
  16 samples @11,025 Hz `8-bit HCOM`, exit 0 — every transport.
- `n_gsrt_act.bin` (ring.bin@16 + 0x84@256, **no RIFF**) → `gsrt`, decode.
- `n_act_noRIFF.bin` (0x84@256, no RIFF) → no match → `.bin` ext → `no handler for file
  extension 'bin'`; renamed `.wav` → `RIFF header not found` — the extension fallback is
  the only second stage, and it is name-driven, never content-driven.
- `n_act_noRIFF.bin` on pipe → `can't determine type of '-'` (stdin has no extension).
- Length floors: `n_gsrt_24` → no detect vs `n_gsrt_25` → `gsrt`; `n_hcom_131` → none vs
  `n_hcom_132` → `hcom`. (`len >= p1+l1` exact at 25 and 132.)

## Edge 3 — multi-preemptor files

`t_gsrt_hcom_act.wav` matches gsrt+hcom+act → detects `gsrt` (row 81 < 90 < 93), confirmed
by author pair `pair_preempt_both` receipt (`sox_detected_format: "gsrt"`). Non-RIFF triple
`m_gsrt_hcom.bin` → `gsrt`. On RIFF files the complete reachable pre-act set is exactly
{gsrt@16, hcom@65+128}; every other pre-act row needs a @0 magic RIFF can't carry, and every
post-act row loses to act/wav ordering anyway (scout's `probe_avi_act`/`probe_ftyp_act`
already showed act>avi/mp4 rows; my RIFX/RF64 rows show wav's own secondary rows fire when
act's RIFF conjunct fails).

## Edge 4 — detect-then-fail: terminal error belongs to the detected reader; zero fallthrough

Same bytes forced through each handler give **distinct** error strings, and a detected file
always emits its own reader's — never a later candidate's:

| forced mode on `t_gsrt_hcom_act.wav` (matches gsrt+hcom+act+wav) | terminal |
|---|---|
| detected (gsrt), file | `premature EOF` (checksum-scan EOF) |
| detected (gsrt), pipe | `invalid format for this file type` + `unsupported encoding: G726` |
| `-t hcom` | `bad compression type` |
| `-t act` | `premature EOF` (au reader, empty pipe) |
| `-t wav` | `file encoding 0x622e (Unknown) is not supported` |

If SoX retried the next matching row on failure, `t_gsrt_hcom_act` would show hcom's
`bad compression type`; `t_hcom_act` (hcom+act+wav all match) shows only hcom's error on
every transport — the act and wav readers are never reached. Single dispatch stands (r63
convergent). hcom's own failure ladder is staged and all native:
`Mac header type is not FSSD` → `Mac data fork is not HCOM` → `bad compression type` →
`bad sampling rate divisor` → `implausible dictionary size` → `invalid dictionary`
(all observed: `f_hcom_badcomp`, `f_hcom_div9`, `bare_hcom_div0`, `bare_hcom_baddict`,
`n_hcom_131` under `-t hcom`).

## New boundary disclosures (measured)

1. **gsrt checksum pass is transport-gated** (`ft->seekable`): identical bytes give
   file=FAIL vs pipe=decode. Corrupt-checksum WARN is emitted only where the pass ran.
2. **gsrt ignores `lsx_skipbytes` return** (gsrt.c:102,117): a file that dies mid-pad still
   "opens" — `n_gsrt_34.bin` (34 B!) → detected, opened, 0 samples, exit 0. gsrt's own
   reader ladder: len<25 undetectable; 25–31 → `invalid/missing file name in header`;
   32–33 → `premature EOF` (enc readsw); ≥34 → opens regardless of the 478-byte pad's
   existence.
3. **Detector stricter than the reader it guards**: CHECK needs `ring.bin`+NUL (9 bytes);
   `start_read` memcmps only 8 (`strlen("ring.bin")`). `f_badnul_dec.wav`
   (`ring.bin\x80`@16, enc=8@32) detects **act** and dies on the ffmpeg path — but
   `-t gsrt` accepts and decodes **11,076** samples on pipe. The byte the detector demands
   is one the reader ignores.
4. **`-t act` bridge on pipe works when detection never ran** (pending empty → no poison):
   `-t act` on `bare_hcom_valid.bin` decodes **64** samples via ffmpeg's own hcom demuxer
   (vs SoX native 16 — a real cross-implementation decode divergence); on 300-B zeros+0x84
   it yields a 0-sample au stream, exit 0.
5. ffprobe cross-check (`runs/logs/*.ff.log`): pair_preempt files → `no 'data' tag found`/
   `Invalid data` (ring.bin clobbers fmt fields); bare gsrt → `Invalid data` (ffmpeg has no
   gsrt demuxer); `bare_hcom_valid` → hcom demuxer engages; `n_act_noRIFF` →
   `tiertexseqvideo`; `bare_gsrt_fs0` → `bintext`. ffprobe's probe ordering is unrelated to
   SoX's — recorded as data.

## Eliminated hypotheses

- "Preemptors need the RIFF shell" — falsified: bare gsrt/hcom decode end-to-end.
- "stdin+autodetect is dead for all routes" — falsified: native preemptor readers consume
  pending-buffer replay correctly; gsrt even gets *further* on pipe than on file.
- "A detected-then-failed open retries the next CHECK" — falsified again on hcom/act/wav
  triple-match files; terminal error is the detected reader's, on every transport.
- "gsrt detection implies gsrt readability" — falsified twice: file-mode dies in the
  checksum pass; detector requires NUL@24 that the reader ignores (decodable under `-t`).

## UNKNOWNs / limits

- Same-host verification only (SoX_ng 14.8.0.1 + ffmpeg n9.0.1). Non-USING_FFMPEG builds
  drop `AUTO_DETECT_SIZE` to 132 and compile out the act row — a RIFF+0x84 file would fall
  to `wav`; gsrt/hcom preemption is unaffected (untested, source-level inference).
- `use_magic` path unexercised (off by default).
- The 95-hour declared duration on pipe-decoded gsrt files is a header-value artifact;
  whether downstream consumers act on `signal.length` before EOF was not traced.
- voc/smp vs gsrt ordering is unreachable-by-construction (mutually exclusive byte ranges),
  stated as such rather than claimed.
- No standards-conformance, fidelity, audibility, or rights claims.

## Next-round surface proposals

- **Transport-divergence tracked pair**: `coll_gsrt_alaw`-shape file is the first fixture
  whose verdict *depends on invocation transport* (file=fail / pipe=decode). Propose a
  probe mode that records the (file | pipe | redir) triple per fixture so receipts capture
  the divergence, not just the verdict.
- **gsrt encoding map**: sweep int16 enc @32–33 (table has 8 entries; enc 0→ulaw, 8→alaw
  decode; 2 observed → `invalid format for this file type`); pin which encodings open.
- **hcom dictionary-gate ladder**: dictsize 0 / 1 / 511 / 512 and leaf-placement edges —
  `dictvalid`'s `n>0` asymmetry means entry 0 can never be a leaf; worth pinning empirically.
- **checksum-pass semantics**: on a *seekable* gsrt whose declared size exceeds actual,
  the pass dies at EOF (`bare_gsrt_fsbig`); declared<actual passes then decode clamps by
  `num_samples`? — untested edge (file_size=0 vs small values vs exact).
- Keep: pair_preempt_* byte-identical convergence makes the collision pair already
  reproducible from either seat's generator.

## Confidence

**High.** Every ordering and transport claim above is an executed `sox -V4`/`--i`/ffprobe
row in `runs/logs/` (340 log rows over 40 fixtures), with strace-level ESPIPE evidence for
the seekable gate, per-reader error-string provenance, byte-identical convergence with the
author's tracked pair, and r64's stdin failure modes reproduced verbatim as controls.
Source citations corroborate only. One inference flagged: glibc's in-buffer `fseeko`
behavior hides the post-checksum `lsx_seeki(4)` — observable only via the WARN/decode
difference, not via an `lseek` syscall.

## Receipts

- `corpus/live/r65-boundary/gen_probes.py`, `run_matrix.sh` — generators/runner.
- `corpus/live/r65-boundary/probes/` — 40 fixtures; SHAs in `runs/probe-shas.txt`.
- `corpus/live/r65-boundary/runs/matrix2.tsv` — 340-row parsed matrix (fixture × mode ×
  detected × samples × terminal line); `runs/logs/` — verbatim `-V4`/`--i`/ffprobe output;
  `runs/strace-badck-{file,pipe}.txt` — lseek evidence; `runs/README.txt` — index.
