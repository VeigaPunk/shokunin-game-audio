
# SoX_ng preemptor map COMPLETE on RIFF+0x84@256 — wve unreachable on RIFF; decodable preemptors and exact length gates (round 66)

- Source: round-66 seat evidence (`reports/round-66/r66-{author,reviewer,
  simplifier,scribe,baseline}.md`; independent sweeps
  `corpus/live/r66-{author,scribe,simplifier,boundary,scout}/…`); upstream
  sox_ng-14.8.0.1 `src/formats.c` (local verified copy
  `corpus/live/r64-reviewer/r64rev-formats.c`, sha256 `82c3058e…`), `wve.c`,
  `gsrt.c`, `hcom.c` — source citations corroborative; all load-bearing
  claims empirical. Commit: 014b532.
- Verified at: 2026-10-14, host `/usr/bin/sox` SoX_ng v14.8.0.1
  (USING_FFMPEG build), ffmpeg/ffprobe n9.0.1. Work commit: 014b532.
- Recheck when: SoX or ffmpeg version/build changes (the `act` row is
  `#if USING_FFMPEG`; ffmpeg-less builds compile `AUTO_DETECT_SIZE 132` and
  drop act), when the CHECK table gains or reorders any row, when a new row
  without an offset-0 anchor lands before `act`, or when fixture families
  change shape.

## Full measured ordering (first matching CHECK row wins)

`auto_detect_format` reads ≤ AUTO_DETECT_SIZE (257 on this build) once and
returns the FIRST matching row (formats.c:66-97). Measured table order,
with reachability on the RIFF family:

    voc(78) ≺ smp(79) ≺ wve(80) ≺ gsrt(81) ≺ amr-wb(82) ≺ prc(83) ≺
    sph(84) ≺ amr-nb(85) ≺ txw(86) ≺ sndt(87) ≺ vorbis(88) ≺ opus(89) ≺
    hcom(90) ≺ act(93) ≺ wav(95-97) ≺ aiff/aifc/8svx…

- Every row before `hcom` anchors a non-RIFF literal at offset 0
  (voc/smp/wve/amr-wb/prc/sph/amr-nb/txw/sndt) or `OggS`@0 (vorbis/opus) —
  all unreachable on `RIFF`/`RIFX`/`RF64`@0 files.
- On a `RIFF`@0 file the reachable pre-act preemptor set is exactly
  **{gsrt, hcom}**; measured order `gsrt ≺ hcom ≺ act ≺ wav` (r65 entry,
  re-verified r66).
- On non-RIFF carriers wve DOES preempt gsrt/hcom/act-shaped co-signatures
  (scribe `Q01–Q05`, author `W02–W04`, reviewer `p2/p3`,
  `m_wve_gsrt.bin` re-run) — table position 80 < 81 is live but only off
  the RIFF family.

### wve predicate (new this round)

    detect(wve) ⟺ len ≥ 15 ∧ file[0:15] == "ALawSoundFile**"

- All 15 bytes individually load-bearing (15 single-byte mutants →
  no-detect); `**` are literal `0x2A` bytes (`00`/`1A`/`?` substitutions all
  fail); case-sensitive; bytes ≥15 unconstrained; length floor exactly 15
  (14 → no-detect, 15 → wve). formats.c:80 corroborative.
- **Geometric exclusion**: byte 0 must be `0x41 'A'`; RIFF/RIFX/RF64 all
  require `0x52 'R'` at byte 0. No byte stream satisfies both — a
  "wve-shaped RIFF file" cannot exist. ~25 independent RIFF/RIFX
  constructions embedding the wve magic at offsets {4,8,12,15,16,36,44,64,
  100,128,200,252,300} detected `act`, `gsrt` or `wav` — never `wve`
  (scribe `Q1*/Q120/Q121`, author `W3*/W4*`, reviewer `p7`, simplifier
  `s_riff_wve300*`).

### Detection ≠ accept — the reader keeps its own contract

| format | detector | reader additionally requires | measured asymmetry |
|---|---|---|---|
| wve | 15-B literal @0 | 18-B ID1 `ALawSoundFile**\x00\x0f\x10` + BE32 num_samples + 10-B pad (wve.c:22-37) | detector **looser** — detects on 15 B, reader rejects `can't find Psion identifier` (15-B-only / wrong-tail files) |
| gsrt | `ring.bin\0` @16-24 (9 B incl. NUL) | `memcmp(read_id,"ring.bin",8)` @16 (gsrt.c:105) + file_size/encoding fields | detector **stricter** at byte 24 — `ring.bin`+`0x2E` does NOT detect gsrt (falls to act); byte 24 is never read by the reader's id check |
| hcom | `FSSD`@65 ∧ `HCOM`@128 | field chain @132+: compresstype ≤1, divisor 1-4, dictsize 1-511, valid dict entries | reader rejects at named gates (`bad compression type`/`bad sampling rate divisor`/`implausible dictionary size`/`invalid dictionary`) AFTER detection claims hcom |
| act | `RIFF`@0 ∧ `0x84`@256 | none — the "reader" is a `popen ffmpeg -f au` bridge; ffmpeg re-probes the bytestream | act-detected RIFF decodes as `pcm_s16le` via ffmpeg when the RIFF is parseable — detection routes, ffmpeg decides |

- A failed open is **terminal**: no re-detection, no second handler, no
  fallback to wav/act (r63+; re-verified on r66 fail-ladders).
- Error strings do not attribute the route (`premature EOF` has ≥3
  emitters); only the `-V4/-V6` `detected file format type` line does.
- hcom's close-time guards (`not all HCOM data read`, `checksum error in
  HCOM data`; hcom.c:265-272) produced **no observable failure** — wrong
  declared checksum still decoded 5 samples exit 0; impossible huffcount
  still opened and emitted what existed (scribe `S09`/`S10`). Declared
  integrity fields are advisory on the stat/decode path on this build.
- wve reader clamp: samples read = **min(declared num_samples, available
  data bytes)** both directions (32-declared→32; 500-declared→268, with
  WARN), not a failure.

### The seekability conjunct (invisible, load-bearing)

gsrt.c:88 `if (file_size >= 2 && ft->seekable)` gates a checksum-scan loop
over the whole stream. A RIFF collider reads `file_size` = `0x52494646`
(≈1.38 G): on a seekable fd the loop walks to real EOF → `premature EOF`
exit 2; on a non-seekable pipe the loop is skipped and the same bytes
decode 88 samples exit 0 (600-B carrier − 512-B HEADER_SIZE; r65 critic D2
and r66 scribe T04, independent constructions, identical fork). Transport,
not content, decides the outcome.

### Tracked decodable-preemptor controls and length gates (round-66)

`corpus/live/round-66/` (probe modes `--probe-ui-{dec-hcom,dec-act,
lengate-gsrt-24,lengate-gsrt-25,lengate-hcom-131,lengate-hcom-132}-r66`):

| member | construction | detected | decode fate |
|---|---|---|---|
| `pair_dec_hcom.wav` (600 B, sha [pending-pinned] `325fb967…`) | fmt-16 RIFF/WAVE + `FSSD`@65 + `HCOM`@128 + reader-valid hcom chain + `0x84`@256 | `hcom` | **native hcom reader decodes 9 samples @22050 Hz, exit 0**; `-t wav` 278; `-t act` 3,520 (ffmpeg's own hcom demuxer); byte-identical to r65-critic's `D1_hcomdecode+act.wav` |
| `pair_dec_act.wav` (`777b6764…`) | sole byte @68 `D`→`E` | `act` | ffmpeg bridge 278 samples pcm_s16le — detection flips on one conjunct byte |
| `pair_lengate_gsrt_{24,25}.wav` (`e7db9976…`/`ede4161b…`) | RIFF shells 24/25 B, `ring.bin[\0]`@16 | `wav`/`gsrt` | gate exactly 25 = 16+9; below-gate member is a wav-claimed honest shell |
| `pair_lengate_hcom_{131,132}.wav` (`6fd9f471…`/`a1abdac4…`) | RIFF shells 131/132 B, `FSSD`@65 + `HCO[M]`@128 | `wav`/`hcom` | gate exactly 132 = 128+4; 131-member decodes 43 samples as wav (the suppressed reader is genuinely readable) |

Exact gates independently re-pinned on bare carriers: wve **14‖15**,
gsrt **24‖25**, hcom **131‖132**, act **256‖257** — the `len ≥ p + l`
conjunct is a read-window property, not container-bound. Ledger 96→102
commands (44 exit 0 / 58 exit 1); all prior receipts byte-identical modulo
the pre-disclosed same-host path-embedding class.

## Falsifiable recheck conditions

1. `sox -V4 corpus/live/round-66/pair_dec_hcom.wav -n stat 2>&1` must print
   `detected file format type `hcom'` AND `Samples read: 9` exit 0 —
   `act`/`wav` detection, or 0 samples, falsifies the decodable-preemptor
   claim. Partner `pair_dec_act.wav` must detect `act` and read 278.
2. `sox -V4 pair_lengate_{gsrt_24,gsrt_25,hcom_131,hcom_132}.wav -n stat`
   must detect `wav`/`gsrt`/`wav`/`hcom` respectively; any flanking flip
   falsifies the exact-gate claim.
3. wve unreachability: any construction with `RIFF`/`RIFX`/`RF64` at byte 0
   that detects `wve` falsifies the geometric-exclusion claim regardless of
   embedded magic placement.
4. Rebuild determinism: `build_ui_dec_preempt_r66_probe()` +
   `build_ui_lengate_r66_probe()` must reproduce all six members
   byte-identically (`cmp` vs committed blobs); ledger re-run must hold
   44/58.
5. Any SoX/ffmpeg version or build-flag change → re-run the scratch sweeps
   (`corpus/live/r66-scribe/sweep.sh`, `r66-author` equivalents); a
   CHECK-table addition before row 93 without an offset-0 anchor, or an
   `AUTO_DETECT_SIZE` resize, invalidates the ordering at the first
   differing row.

## Bounded UNKNOWNs retained

- Single host/toolchain (SoX_ng 14.8.0.1 USING_FFMPEG + ffmpeg n9.0.1);
  ffmpeg-less builds drop the act row and shrink the read window to 132
  (untested compile-level inference) — gsrt/hcom ordering survives, act
  claims evaporate.
- wve reader/write semantics beyond `start_read` (ID2 pad, repeat info);
  hcom Huffman correctness vs reference; gsrt non-seekable length semantics
  — decode-count claims only, no fidelity/conformance claim.
- Whether stopread-class failures ever propagate on any code path
  (observed inert on stat/decode/`--i` legs only).
- `--magic`/`use_magic` path; plugin-registered CHECK rows (none
  installed); non-RIFF containers beyond spot checks.
