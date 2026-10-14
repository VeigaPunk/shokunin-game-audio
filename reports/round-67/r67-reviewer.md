# R67 reviewer — audit of r66 committed state (`014b532` + `0df212f`) + live transport-fork exercise

Seat: **reviewer** — audit-only; no tracked mutation performed or proposed. Host:
`sox` = SoX_ng **14.8.0.1** (`/usr/bin/sox -> sox_ng`, USING_FFMPEG build), ffmpeg/ffprobe
**n9.0.1**, python **3.14.7** — identical toolchain to the r66 record. Audited tree:
canonical repo `/home/vgpnk/Projects/shokunin/audio-shokunin` @ HEAD `0df212f`; ledger
commands re-run from the lane worktree `~/Projects/prymeagnt/audio` so `.shokunin/audio`
resolves through the symlink, matching `run_ledger.py`'s invocation contract.
Scratch: `corpus/live/r67-reviewer/` (probes `r67rev_*`, `fakebin/ffmpeg` argv+stdin
capture stub, `ffmpeg-capture/`). Post-audit `git status`: **0 tracked modifications**
(untracked = my `r67-reviewer/` scratch + `runs/20261014T050{3,4}*` receipts written by
`measure_audio.py` by design, same class as every prior round).

**LSP note**: no `lsp` device answers this repo on this substrate (author/verifier
recorded the same); caller/definition checks are text-grep fallbacks over the local
upstream tree `/tmp/sox_ng_src/sox_ng/src` (verified identical to committed
`corpus/live/r64-reviewer/r64rev-formats.c` in r66). All load-bearing verdicts are live
`sox`/`ffmpeg` executions — the stronger evidence class here.

## Verdict summary

| audit item (per brief) | result |
|---|---|
| r66 family verbatim re-run — all 6 members' detection lines + decode counts | **SURVIVES** — 6/6 detection lines, sample counts, exits; forced legs + `--i` all consistent |
| 102-ledger spot-set replay (6 new + 4 prior r65 modes) | **SURVIVES** — 10/10 exit 1 as recorded; **all 10 receipts byte-identical** to r66's recorded receipts; the 4 priors also byte-identical to r65's originals; new-mode receipts deterministic across two of my independent runs |
| six-member SHAs + rebuild determinism | **SURVIVES** — all 6 sha256 match published digests; unchanged after probe rebuilds |
| wve geometric exclusion (own wve+RIFF attempt) | **SURVIVES** — `RIFF`+`ALawSoundFile**`@16+`0x84`@256 → `act`, never `wve` |
| detector-vs-reader asymmetries (wve / gsrt / hcom) | **SURVIVES** — all three asymmetries reproduced on fresh constructions with named reader gates |
| transport-fork disclosure (`pair_dec_act` file-only) | **SURVIVES and SHARPENS** — the "unexercised" stdin transports are now exercised: `pair_dec_act` decodes **only** via a re-openable named path; both stdin modes fail at the ffmpeg bridge; fifo deadlocks on a single writer. New measured evidence, mechanism identified (§4) |

**No claim in the audited r66 record fails re-execution.** One clarifying observation
(LOW, §5) and one substantive new transport measurement set (§4) that directly informs
the r67 declared axis-move.

---

## 1. r66 family verbatim — six tracked members

Commands: `sox -V6 corpus/live/round-66/<m>.wav -n stat` (+ forced legs where claimed).
SHAs re-measured first — **all six match the author's published digests exactly**:

| member (sha256 prefix verified) | claimed | observed |
|---|---|---|
| `pair_dec_hcom.wav` `325fb967…96cd` | `hcom`, Samples read 9, exit 0 | `` detected file format type `hcom' ``, `Samples read: 9`, exit **0**; `-t act`→**3520** (ffmpeg demuxer), `-t wav`→**278**, raw f32 leg **36 B** = 9×4, `--i`→**22050 Hz / 8-bit** ✓ |
| `pair_dec_act.wav` `777b6764…6edb` | `act`, 278, exit 0 | `` `act' ``, `Input File … (ffmpeg)`, `Samples read: 278`, exit **0** ✓ |
| `pair_lengate_gsrt_24.wav` `e7db9976…c571` | `wav`, fmt chunk not found, exit 2 | `` `wav' ``, `fmt chunk not found`, exit **2** ✓ |
| `pair_lengate_gsrt_25.wav` `ede4161b…97c5` | `gsrt`, premature EOF, exit 2 | `` `gsrt' ``, `premature EOF`, exit **2** ✓ |
| `pair_lengate_hcom_131.wav` `6fd9f471…b0a1` | `wav`, 43, exit 0 | `` `wav' ``, `Samples read: 43`, exit **0** ✓ |
| `pair_lengate_hcom_132.wav` `a1abdac4…d6d6` | `hcom`, premature EOF, exit 2; `-t wav` 44 | `` `hcom' ``, `premature EOF`, exit **2**; `-t wav` leg `Samples read: 44`, exit 0 ✓ |

Rebuild determinism: members re-hashed **after** my ledger probes (which invoke the
builders) — digests unchanged, i.e. `build_ui_dec_preempt_r66_probe()` /
`build_ui_lengate_r66_probe()` rebuild byte-identically (falsifiable recheck #4 holds).

## 2. Ledger spot-set replay — rows 02–07 (new) + 08–11 (prior)

Ran verbatim from `~/Projects/prymeagnt/audio`:
`python3 .shokunin/audio/corpus/fixtures/measure_audio.py <flag>`.

| flag | exit (expected) | fresh receipt | vs r66 recorded | vs r65 original |
|---|---|---|---|---|
| `--probe-ui-dec-hcom-r66` | 1 (1) | `…050406106862Z-…` | `cmp` = `023252189954Z` **IDENTICAL** | n/a (new mode) |
| `--probe-ui-dec-act-r66` | 1 (1) | `…050407267154Z-…` | `023253353024Z` **IDENTICAL** | n/a |
| `--probe-ui-lengate-gsrt-24-r66` | 1 (1) | `…050408346513Z-…` | `023254414734Z` **IDENTICAL** | n/a |
| `--probe-ui-lengate-gsrt-25-r66` | 1 (1) | `…050409425032Z-…` | `023255482162Z` **IDENTICAL** | n/a |
| `--probe-ui-lengate-hcom-131-r66` | 1 (1) | `…050410520214Z-…` | `023256568490Z` **IDENTICAL** | n/a |
| `--probe-ui-lengate-hcom-132-r66` | 1 (1) | `…050411593732Z-…` | `023257631686Z` **IDENTICAL** | n/a |
| `--probe-ui-preempt-act-r65` | 1 (1) | `…050412745489Z-…` | `023258755411Z` **IDENTICAL** | `014331736394Z` **IDENTICAL** |
| `--probe-ui-preempt-gsrt-r65` | 1 (1) | `…050413823457Z-…` | `023259829120Z` **IDENTICAL** | `014332805968Z` **IDENTICAL** |
| `--probe-ui-preempt-hcom-r65` | 1 (1) | `…050414904921Z-…` | `023300898052Z` **IDENTICAL** | `014333872621Z` **IDENTICAL** |
| `--probe-ui-preempt-both-r65` | 1 (1) | `…050416007794Z-…` | `023301983754Z` **IDENTICAL** | `014334931555Z` **IDENTICAL** |

Fresh-receipt probe fields spot-checked against the author's published values:
`dec_hcom {hcom, native, stat 9/exit0, f32 36B, KeyError:'duration'}`;
`dec_act {act, ffmpeg, 278, f32 1112B, pcm_s16le}`; `gsrt_24 {wav, ffprobe err}`;
`gsrt_25 {gsrt, ffprobe err}`; `hcom_131 {wav, 43, f32 172B}`; `hcom_132 {hcom, ffprobe err}` — all match.

Determinism bonus: an accidental first pass of the same 10 commands (exit capture bug
on my side — piped `$?` read `tail`'s status; corrected, not a repo defect) produced a
second receipt set `…0503*`; `cmp` vs the `…0504*` set → **6/6 new-mode pairs
byte-identical** across independent invocations.

## 3. Knowledge entry — `2026-10-14-sox-preemptor-map-complete.md`

### 3a. wve geometric exclusion — fresh construction

`corpus/live/r67-reviewer/probes/r67rev_wve_in_riff.wav` (300 B, `0x11` filler):
`RIFF`@0 + size + `WAVE`@8 + `ALawSoundFile**`@16–30 + `0x84`@256.

```
sox -V6 r67rev_wve_in_riff.wav -n stat
→ detected file format type `act'
→ FAIL … premature EOF   (act bridge on a 300-B RIFF — the RIFF is parseable but short)
```

Detected **`act`**, never `wve` — falsifiable recheck #3 holds on an independent
construction (byte-0 `0x52` vs `0x41` is a geometric wall; magic at an interior offset
is dead code for the wve row). Source corroboration re-verified:
`formats.c:80` `CHECK(wve,0,0,"",0,15,"ALawSoundFile**")` in the local
`sox_ng-14.8.0.1` tree.

### 3b. Detector-vs-reader asymmetries — all three reproduced

**wve — detector looser (15 B) than reader (18-B ID1):**
- `r67rev_wve_15.bin` (exactly 15 B `ALawSoundFile**`) → `detected 'wve'` →
  reader `premature EOF` (can't even supply the ID1).
- `r67rev_wve_badtail.bin` (300 B, magic + `\xAA\xBB\xCC`@15–17) → `detected 'wve'`
  → reader **`can't find Psion identifier`** — detection succeeded, reader's 18-byte
  `ID1 = ALawSoundFile**\0\017\020` gate (wve.c:22-37) rejected. Exact named-gate
  evidence for the asymmetry row.

**gsrt — detector stricter (9 B incl. NUL@24) than reader (8-B memcmp):**
- `r67rev_gsrt_2e.wav` (600-B RIFF/WAVE + `ring.bin`@16–23 + `0x2E`@24 + `0x84`@256) →
  detected **`act`** — the implicit `\0` in the C literal is load-bearing at byte 24.
- `r67rev_gsrt_nul.wav` control (same bytes, `0x00`@24) → detected **`gsrt`** —
  byte 24 alone flips gsrt↔act on a RIFF+0x84 carrier.
- Reader side: `sox -t gsrt r67rev_gsrt_id8.bin` (`ring.bin`+`0x2E`@24, file_size=0) →
  **opened and ran to `Samples read: 0`, exit 0** — the reader's `memcmp(read_id,
  "ring.bin", 8)` (gsrt.c:105) accepts byte24=anything; control `r67rev_gsrt_badid.bin`
  (`ring.bjn`) → `invalid/missing file name in header`. The reader literally never
  reads byte 24.

**hcom — reader gates fire after detection:**
- `r67rev_hcom_badcomp.wav` (`pair_dec_hcom` + compresstype@140→5) → `detected 'hcom'`
  → **`bad compression type`**.
- `r67rev_hcom_baddiv.wav` (divisor@144→9) → `detected 'hcom'` →
  **`bad sampling rate divisor`**.
Both named post-detection gates reproduced verbatim from the table.

### 3c. gsrt seekability fork — re-confirmed on the canonical carrier

`corpus/live/r65-critic/var/D2_gsrtULAW+act.wav` (600 B):

| transport | result |
|---|---|
| file: `sox -V4 D2 -n stat` | `` `gsrt' `` → `premature EOF`, exit **2** |
| pipe: `cat D2 \| sox -V4 - -n stat` | `` `gsrt' `` → **`Samples read: 88`, exit 0** |

Byte-identical input, opposite verdicts — decided by `ft->seekable` at gsrt.c:88
(`file_size >= 2 && ft->seekable` gates the whole-stream checksum scan; `file_size`
reads `0x52494646` ≈ 1.38 G on the RIFF collider). The knowledge entry's fork holds.

## 4. NEW MEASUREMENT — `pair_dec_act` transport matrix (the "file-only" disclosure, exercised)

The r66 author disclosed "stdin/pipe transports on the new members unexercised here."
I exercised them. `pair_dec_act` (and the whole `act`→ffmpeg-bridge route) forks on
transport — a **second tracked member** beyond gsrt where transport silently changes
the verdict:

| transport | command | detection | outcome |
|---|---|---|---|
| named path | `sox f.wav -n stat` | `act` | **278 samples, exit 0** |
| stdin pipe (autodetect) | `cat f.wav \| sox - -n stat` | `act` | FAIL `can't find Sun/NeXT/DEC identifier`, exit 2 (deterministic ×3) |
| stdin redirected fd (seekable, autodetect) | `sox - -n stat < f.wav` | `act` | FAIL `premature EOF`, exit 2 |
| fifo, single writer | `sox f.fifo -n stat` | — | **HANG** (>15 s, killed) — see mechanism |
| fifo, looping writer | `sox f.fifo -n stat` | `act` | FAIL `can't find Sun/NeXT/DEC identifier`, exit 2 |
| stdin pipe, **forced** `-t act` / `-t ffmpeg` | `cat f.wav \| sox -t ffmpeg - -n stat` | — | **278 samples, exit 0** |
| stdin fd, forced `-t act` | `sox -t act - -n stat < f.wav` | — | **278 samples, exit 0** |

For contrast, `pair_dec_hcom` on a stdin pipe shows **no fork**: `` `hcom' `` →
`Samples read: 9`, exit 0 — the native hcom reader is transport-tolerant.

### Mechanism (identified via a `fakebin/ffmpeg` argv+stdin capture stub in PATH)

`startread_ffmpeg` (ffmpeg.c:33-108) spawns
`ffmpeg -loglevel quiet -nostdin -strict -2 -i <ft->filename> -f au -`, then parses
ffmpeg's stdout as `au`. Captures prove the three transports fail by three distinct
mechanisms:

1. **stdin pipe (autodetect)**: ffmpeg received the **complete 600-byte stream**
   (captured `stdin-…2899554016.bin` `cmp`-equal to the member; argv `-i -`), identical
   argv and identical stdin bytes to the working forced-mode run — yet the parent's au
   parser fails. Cause: autodetect's `lsx_readbuf_rewind` left the 257-byte probe
   window in `ft->pending_buffer`; the fork-child regurgitates pending+rest to ffmpeg
   in *its own* address space, so the **parent's** `pending_count` survives —
   `lsx_au_format_fn()->startread` drains `pending_bytes` first (formats_i.c:109-115),
   sees `"RIFF…"`, and rejects the au magic (au.c:141). The detection residue is
   prepended to ffmpeg's output: the autodetect→ffmpeg-bridge path on non-seekable
   stdin is **structurally dead by construction**, exactly the r67 claim's phrase —
   while forced `-t act`/`-t ffmpeg` on the same pipe works (no probe, `pending_count`=0).
2. **stdin seekable fd (autodetect)**: ffmpeg's stdin capture was **0 bytes** —
   `rewind(fp)` on a fully-buffered FILE whose buffer covers the whole file is an
   in-buffer seek that never issues `lseek`; the inherited fd sits at EOF → ffmpeg
   reads nothing → au parser hits EOF → `premature EOF`. Forced mode keeps fd at 0
   (no probe ran) → works.
3. **fifo named path**: filename ≠ `-`, so no regurgitate path; sox detects `act` off
   the fifo (pending-buffered), then `ffmpeg -i f.fifo` **re-opens the path** — a
   second `open()` on a writerless fifo blocks → deadlock with a single-shot writer.
   With a looping writer ffmpeg re-opens and decodes, but the same parent-side pending
   contamination then fails the au parse (`can't find Sun/NeXT/DEC identifier`).

So `pair_dec_act`'s "decodes 278" verdict is **pathname-dependent**: it holds only
when ffmpeg can re-open the input by name. The r66 records were honest (disclosed as
unexercised, and every recorded receipt is a named-path measurement); what my audit
adds is that the fork is **real, deterministic, and mechanism-pinned** — with three
distinct failure modes per transport class. This is direct supporting evidence for
the r67 declared axis-move's premise that transport silently forks outcomes and is
unrecorded in the ledger.

## 5. Clarifying observation (LOW — no misstatement, but auditors should know)

The 88-sample pipe decode attaches to the **scratch 600-B carrier** (r65-critic `D2`,
r66-scribe `T04`), exactly as the knowledge entry scopes it. On the **tracked** r65
member `pair_preempt_gsrt.wav` (11,588 B — different construction), the same fork
holds only at the failure-path level: file → `premature EOF` vs pipe →
**`invalid format for this file type`** (the reader gets past the skipped checksum
loop and dies at the `ft_encoding` gate instead). Same verdict class (exit 2 both),
different gate — so "transport decides the outcome" is true of the tracked member too,
but the *decode-to-88-samples* fork is a property of the collider constructions, not
of the tracked fixture. Anyone re-executing the "88 samples" claim against
`pair_preempt_gsrt.wav` will not observe it.

## Findings by severity

- **HIGH/MED defects against r66 committed state: none.** Every audited claim —
  six members' detection lines + decode counts, spot-set ledger replay with
  byte-identical receipts, wve geometric exclusion, all three detector-vs-reader
  asymmetries, exact length gates, rebuild determinism — survives verbatim
  re-execution on this host.
- **New measured evidence (positive, not a defect)**: `pair_dec_act` is a second
  tracked member whose verdict forks on transport — named-path-only decode;
  stdin-pipe and fifo both fail the bridge's au parse via leftover autodetect
  `pending_bytes`; seekable stdin fails via an at-EOF inherited fd; single-writer
  fifo deadlocks on the bridge's re-open-by-name. Mechanisms at ffmpeg.c:33-108 +
  formats_i.c pending-buffer semantics. Directly relevant to the r67 transport
  axis: the fork set is measurable and extends beyond gsrt.
- **LOW**: §5 — the 88-sample pipe decode is collider-specific, not a property of
  the tracked `pair_preempt_gsrt` fixture (that member forks at the error-gate
  level only). Knowledge entry already scopes this correctly; flagging to prevent
  a future mis-replay.

## Residual risk / verification gaps

- Spot-set, not the full 102: I replayed the 6 new + the 4 r65-preempt priors
  (rows 02–11). The r66 verifier ran all 102 byte-identical at commit time; my
  10/10 spot-set adds nothing contradictory but does not re-prove rows 12–102.
- The pending-contamination mechanism for act-on-pipe is proven by
  identical-argv/identical-stdin captures + the au magic error string + the code
  path (lsx_readbuf drains `pending_bytes` before fp); I did not run a debugger.
  The fifo deadlock is observed-hang + re-open-by-name inference (argv capture
  proves ffmpeg is invoked with the path, not a fd).
- Knowledge rows not re-audited this round (cited to other seats' evidence):
  hcom close-time guards (`checksum error` still decoding), wve reader clamp
  `min(declared, available)`, act 256‖257 bare-carrier gate, non-RIFF wve
  preemption over gsrt/hcom.
- Single host/toolchain: SoX_ng 14.8.0.1 USING_FFMPEG + ffmpeg n9.0.1. The
  act-row claims still vanish on ffmpeg-less builds (`AUTO_DETECT_SIZE` 132).
- `lsp` device absent on this substrate — semantic checks were live-execution +
  local-source reads, not LSP references/definitions.

## Receipts / evidence index

- Fresh ledger receipts (my runs): `corpus/live/runs/20261014T050{3,4}*-{ui-dec-hcom,ui-dec-act,ui-lengate-gsrt-24,ui-lengate-gsrt-25,ui-lengate-hcom-131,ui-lengate-hcom-132}-r66/measurements.json`, `…T0504*-ui-preempt-{act,gsrt,hcom,both}-r65/measurements.json`.
- Comparisons: `cmp` vs `runs/20261014T02325{2189954,3353024,4414734,5482162,6568490,7631686,8755411,9829120,0898052,1983754}Z-*/measurements.json` → 10/10 identical; vs r65 `…T0143{31736394,32805968,33872621,34931555}Z-*` → 4/4 identical.
- Probes (all built by me, in scratch): `corpus/live/r67-reviewer/probes/r67rev_{wve_in_riff,wve_15,wve_badtail,gsrt_2e,gsrt_nul,gsrt_id8,gsrt_badid,hcom_badcomp,hcom_baddiv}.{wav,bin}`.
- Bridge captures: `corpus/live/r67-reviewer/ffmpeg-capture/stdin-*.bin` (pipe-autodetect = full 600 B; seekable-fd = 0 B) + stub `fakebin/ffmpeg`.
- Source basis: `/tmp/sox_ng_src/sox_ng/src/{formats.c:80,90,93,95-97; gsrt.c:88,105; wve.c:22-37; ffmpeg.c:33-108; formats_i.c:104-115,178-220; au.c:141}`.
- Leaf seat: no commits, no pushes, no tracked edits, no dispatches.
