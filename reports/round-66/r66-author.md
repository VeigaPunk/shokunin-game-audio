# R66 author — preemptor map COMPLETE on RIFF+0x84@256: wve unreachable on RIFF (falsified fork), DECODABLE-hcom pair landed, len gates pinned 24|25 / 131|132

host: devin (same lane as R61–R65)
Clean-before: canonical lane repo `/home/vgpnk/Projects/shokunin/audio-shokunin` HEAD `30e5e32`;
worktree `/home/vgpnk/Projects/prymeagnt/audio` (`.shokunin/audio` symlinks into the canonical repo).
Toolchain under test: SoX_ng v14.8.0.1 (`/usr/bin/sox` -> `sox_ng` symlink), ffmpeg/ffprobe n9.0.1, python 3.14.7.

## Scoped move — mixed outcome: wve ordering claim FALSIFIED on RIFF (geometric, not just unobserved); decodable-preemptor + len-gate controls CONFIRMED and tracked

The declared move had three deliverables:

1. **wve preemptor on RIFF** — the falsifiable ordering claim is **FALSIFIED**:
   a wve-shaped RIFF file cannot exist on this build. Empirically identified
   the wve CHECK predicate as exactly `file[0:15] == "ALawSoundFile**"`
   (single conjunct, length floor 15); byte 0 must be `0x41 'A'` while every
   RIFF-family tag carries `0x52 'R'` at byte 0 — the predicates are
   geometrically disjoint. 16 RIFF/RIFX/RF64 constructions embedding the
   wve magic at offsets {4,8,12,15,16,36,44,64,128,252} detected `act` or
   `wav`, never `wve`. **No wve-collision member landed** (the brief's
   explicit else-branch: record the falsified outcome). The reachable
   pre-act preemptor set on RIFF+0x84@256 is therefore exactly {gsrt, hcom}
   — the map is complete.
2. **DECODABLE-preemptor pair** — CONFIRMED and tracked: `pair_dec_hcom.wav`
   is detected `hcom` and the native hcom reader decodes **9 samples @22050
   Hz** (exit 0); `pair_dec_act.wav` differs by one byte (@68 `D`->`E`) and
   detects `act`, decoding 278 samples through the ffmpeg bridge. The
   hcom member is **byte-identical to r65-critic's scratch
   `D1_hcomdecode+act.wav`** (sha256 `325fb967f0c9…` matches the critic's
   published `325fb967…` — independent convergence).
3. **Length gates** — pinned exactly: gsrt 24->`wav` | 25->`gsrt`,
   hcom 131->`wav` | 132->`hcom`, on tracked members whose only structural
   differences are the length-crossing signature byte plus self-consistent
   RIFF size bookkeeping.

## Empirical sweep (scratch: `corpus/live/r66-author/`)

Generator/prober `gen_probes.py`; **55 rows** in `results.tsv`
(variants + verbatim legs); shas in `runs/variant-shas.txt`.
Probes per variant: `sox -V6 <f> -n stat` (detected/samples/exit),
forced `-t {wve,act,wav}` legs, raw f32 decode, ffprobe codec.

### wve predicate identification (empirical; source corroborative only)

| probe | construction | detected | reader outcome |
|---|---|---|---|
| `W01_wve_bare` | `ALawSoundFile**`@0, 300 B | **wve** | `can't find Psion identifier` |
| `W02`/`W03`/`W04` | wve + `ring.bin\0`@16 (+`FSSD`+`HCOM`) + 0x84@256 | **wve** | same — wve beats gsrt and hcom on non-RIFF |
| `W05`/`W06`/`W07` | 14 / 15 / 16 B files | NONE / **wve** / **wve** | length floor = **15** exactly |
| `W1000`–`W1014` | single-byte XOR at each position 0–14 | all 15 x NONE | **every one of the 15 bytes required** |
| `W25` | `ALawSoundFile*?` (`*`->`?` @14) | NONE | trailing `*` is literal 0x2A, not wildcard |
| `W26` | byte 15 = 0xAA | **wve** | bytes >=15 unconstrained (no second conjunct) |
| `W42` | wve@0 + fake `RIFF`@32 | **wve** | content match anchors at offset 0 only |
| `W50_wve_valid` | + `\x00\x0F\x10`@15 + num_samples BE + pad | **wve** | **decodes 200 samples, 8-bit A-law, exit 0** |
| `W51`/`W52` | ID1 tail `\x0F\x10` vs `\x0F\x11`@17 | wve / wve | reader opens (271 smp) / `can't find Psion identifier` |

The wve row is live and its predicate is byte-exact — but its reader is
*stricter* than the detector (wve.c verifies the 18-byte ID1
`ALawSoundFile**\0\x0F\x10` + BE `num_samples` + 10 skipped pad bytes; the
CHECK row only compares the first 15). Detector 15 B < reader 18 B — the
opposite asymmetry to gsrt (detector 9 B > reader's 8-byte memcmp).

### wve on RIFF — the falsification battery (N = 16)

| file | wve magic placement | detected | note |
|---|---|---|---|
| `W304`–`W3128` | RIFF+WAVE+0x84@256, magic @ {4,8,12,15,16,36,44,64,128} | `act` | 44/64/128 decode 128 samples as pcm |
| `W3252` | magic @252-266 (covers byte 256) | `wav` | 0x84 clobbered -> act conjunct lost |
| `W40`/`W41` | `RIFX`/`RF64`@0 + magic@16 | `wav` | RIFX/RF64 wav rows fire |
| `W43` | magic @4 over the RIFF size field | `act` | — |
| `W42` (control) | wve@0, `RIFF`@32, .bin | `wve` | non-RIFF positive control |
| `X01` + forced `-t wve` | plain RIFF/WAVE | `wav` | reader-side: `can't find Psion identifier` |

Byte 0 is the geometric wall: `RIFF`/`RIFX`/`RF64` all require `0x52` at
offset 0; wve requires `0x41`. A single `CHECK(wve…)` row exists
(formats.c:80, corroborative) — no alternate wve path inside
`auto_detect_format`. On non-RIFF files wve does preempt gsrt/hcom (W02–W04,
consistent with r65-boundary's `m_wve_gsrt.bin`), so the ordering result
stands as: **wve < gsrt < hcom < act < wav where co-satisfiable — and wve is
unreachable on the entire RIFF family.**

### DECODABLE-preemptor construction (scratch candidates)

| variant | diff vs `D01` | detected | outcome |
|---|---|---|---|
| `D01_hcomdecode+act` | — | **hcom** | `Samples read: 9`, exit 0; `-t act` 3,520 (ffmpeg hcom demuxer); `-t wav` 278 (pcm_s16le); ffprobe codec `hcom` |
| `D02_dec68x+act` | byte @68 `D`->`E` | **act** | 278 samples pcm_s16le, exit 0 — chosen for the tracked pair |
| `D03_dec131x+act` | byte @131 `M`->`X` | `act` | 278 samples, exit 0 — alternate sole-byte, kept in scratch |
| `D04_hcomdecode_00` | byte 256 -> 0x00 | `hcom` | 9 samples — preemptor self-sufficient without act byte |

One byte-stream, three working readers on D01 (hcom 9 / act-bridge 3,520 /
native wav 278) — matching r65-critic's table exactly.

### Length-gate constructions

| variant | size | sig bytes present | detected | outcome |
|---|---|---|---|---|
| `L01`/`pair_lengate_gsrt_25` | 25 B | `ring.bin\0`@16-24 | **gsrt** | `premature EOF` (RIFF@0 -> file_size 1.38 G -> checksum loop EOF) |
| `L02`/`pair_lengate_gsrt_24` | 24 B | `ring.bin`@16-23, NUL truncated | **wav** | `fmt chunk not found` |
| `L03`/`pair_lengate_hcom_132` | 132 B | `FSSD`@65-68 + `HCOM`@128-131 | **hcom** | `premature EOF`; `-t wav` leg decodes 44 samples (suppressed member readable) |
| `L04`/`pair_lengate_hcom_131` | 131 B | `FSSD` + `HCO`@128-130 | **wav** | decodes 43 samples, exit 0 |
| `L05`–`L08` non-RIFF | 24/25, 131/132 | same sigs, `.bin` | gsrt / NONE / hcom / NONE | non-RIFF cross-check; NONE -> extension fallback `no handler for 'bin'` |

## Source basis (corroborative; the measurements above stand alone)

`corpus/live/r64-reviewer/r64rev-formats.c` == `/tmp/sox_ng_src/.../formats.c`
(diff-verified identical, upstream tag sox_ng-14.8.0.1): `CHECK(wve,0,0,"",0,15,"ALawSoundFile**")`
at :80 — `len >= 15 && !memcmp(data, "ALawSoundFile**", 15) && !memcmp(data,"",0)`;
gsrt :81, hcom :90, act :93, wav :95-97. `wve.c` `start_read` re-verifies the
18-byte ID1 (`ALawSoundFile**\0\017\020`) then reads BE `num_samples` and
skips 10 pad bytes — the `can't find Psion identifier` error's origin.

## Tracked changes (additive only; all prior fixtures/modes/thresholds untouched)

`corpus/fixtures/build_artifacts.py` **+112/−1**:
`build_ui_dec_preempt_r66_probe()` emits `corpus/live/round-66/pair_dec_{hcom,act}.wav`
— 600-B fmt-16 PCM RIFF/WAVE skeleton, deterministic ramp payload
`(i*7+3)&0xFF`, `FSSD`@65-68 + `HCOM`@128-131 + hcom reader field chain
(huffcount 9 @132 BE, checksum 0xA5A5A5A5 @136, compresstype 0 @140,
divisor 1 @144 -> 22050 Hz, dictsize 2 @148, dict entries @150-157, pad 0 @158,
first sample 0x40 @159, word @160-163), 0x84@256; the `act` member flips
byte @68 `D`->`E`. `build_ui_lengate_r66_probe()` emits the four
RIFF/WAVE len-gate shells (self-consistent RIFF/data size fields).
Six argparse flags + newest-first dispatch branch running both builders.

`corpus/fixtures/measure_audio.py` **+89/−4**: six flags
(`--probe-ui-dec-{hcom,act}-r66`, `--probe-ui-lengate-{gsrt-24,gsrt-25,hcom-131,hcom-132}-r66`),
mutual-exclusion sum, builder-flag forwarding, one measurement block at the
newest-first head (r65 leg set — `-V6` stat, `-t act` bridge, `-t wav`
native — plus a raw `sox <f> -t f32 -e floating-point -` leg recorded as
`sox_f32_exit_code`/`sox_f32_bytes`, the decodable-preemptor claim's direct
evidence), `pair_member` field, and a second exception branch
(`decode_error_tool: "measure_pipeline"` + `measure_error`) for members
whose decode succeeds but whose stream shape the ffprobe->duration pipeline
cannot complete (hcom's `format` object carries no duration field ->
`KeyError: 'duration'`, recorded verbatim). `mode`/`suffix` chain heads prepended.

Member byte evidence (`cmp -l`, 1-based offsets, octal):
- `pair_dec_hcom` vs `pair_dec_act` (both 600 B): **offset 69 only**
  (`104 'D'` -> `105 'E'`) — the declared sole-byte diff.
- `pair_lengate_gsrt_24` vs `_25`: offset 5 (`020`->`021`, RIFF size 16->17)
  + EOF after byte 24 (the NUL@24 is the gate-crossing byte).
- `pair_lengate_hcom_131` vs `_132`: offset 5 (`0173`->`0174`, RIFF size
  123->124), offset 41 (`0127`->`0130`, data size 87->88) + EOF after byte
  131 (the `'M'`@131 is the gate-crossing byte). Self-consistent sizes are
  intentional — each member is an honest RIFF of its own length; the pair's
  detection pin is `sox_detected_format`, not the size fields.

SHA-256 (`sha256sum corpus/live/round-66/`):
- `pair_dec_hcom.wav` `325fb967f0c9c126b7aaac5f580c92f7f3946a728c2c7323a1c8d497c23896cd`
  (**== r65-critic's `D1_hcomdecode+act.wav` sha `325fb967…`** — byte-identical
  independent construction)
- `pair_dec_act.wav` `777b6764ad75dc2cad6fa862253e106e4230107f182770fdf68a22a946176edb`
- `pair_lengate_gsrt_24.wav` `e7db997697cfb4723e95d54ce936652aae8447f6722d92e1e7f0fedaca11c571`
- `pair_lengate_gsrt_25.wav` `ede4161b73798f6d4840fc7ca0845d48d36c44404739fcdc5d384d891abc97c5`
- `pair_lengate_hcom_131.wav` `6fd9f47165bf58eb01ad5f6baaa7ea6caf5e93f4693efc816c6c06789b2790a1`
- `pair_lengate_hcom_132.wav` `a1abdac4c990764979afcfed958639f839e0630d2fef21ebcc7f740d547eb6d6`
Rebuild deterministic (a second `--probe-ui-dec-act-r66` build rewrote identical bytes).

Live routing on the tracked members (`sox -V4`/`--i` verbatim):
- `pair_dec_hcom.wav`: `` detected file format type `hcom' `` ->
  `Samples read: 9`, exit 0; `--i` -> `Input File '…' (hcom)`, 22050 Hz,
  `8-bit HCOM`, exit 0.
- `pair_dec_act.wav`: `` detected file format type `act' `` ->
  `Samples read: 278`, exit 0 (bridge, pcm_s16le).
- `pair_lengate_gsrt_24.wav`: `wav` -> `fmt chunk not found`, exit 2.
- `pair_lengate_gsrt_25.wav`: `gsrt` -> `premature EOF`, exit 2.
- `pair_lengate_hcom_131.wav`: `wav` -> `Samples read: 43`, exit 0.
- `pair_lengate_hcom_132.wav`: `hcom` -> `premature EOF`, exit 2.

## What ran — 102-command ledger (96 prior verbatim + 6 new modes at positions 2-7)

All commands `python3 .shokunin/audio/corpus/fixtures/measure_audio.py <flag>`
from the worktree root; receipts under `corpus/live/runs/<stamp>-<suffix>/measurements.json`.
Runner `corpus/live/r66-author/run_ledger.py`; TSV `ledger-r66.tsv`;
comparison `compare_receipts.py`. Totals: **44 exit 0 / 58 exit 1**
(r65's 44/52 plus six new exit-1 probes).

Prior-96 replay (rows {1} U {8-102} mapped to r65 rows 1-96): exit sequence
position-identical and **all 96 receipts byte-identical** to the r65 receipt
files (`compare_receipts.py`: "96 prior-mode pairs checked, 0 mismatches").
Normal-run receipt `20261014T023251113379Z-normal/measurements.json` is
byte-identical to r65's `20261014T014330610722Z-normal` (cmp-verified).

New-mode receipts (each re-run byte-identical across independent runs —
all six verified twice):
- `--probe-ui-dec-hcom-r66` -> exit 1,
  `runs/20261014T023252189954Z-ui-dec-hcom-r66/measurements.json`;
  `ui_dec_hcom_r66_probe`: `sox_detected_format: "hcom"`, `sox_route: "native"`,
  stat exit 0 / samples **9**, bridge (`-t act`) exit 0 / 3,520 (ffmpeg hcom
  demuxer), native (`-t wav`) 278, `sox_f32_bytes: 36`;
  `decode_error_tool: "measure_pipeline"`, `measure_error: "KeyError: 'duration'"`.
- `--probe-ui-dec-act-r66` -> exit 1,
  `runs/20261014T023253353024Z-ui-dec-act-r66/measurements.json`;
  `sox_detected_format: "act"`, `sox_route: "ffmpeg"`, all three legs
  278 samples, `sox_f32_bytes: 1112`, codec `pcm_s16le`, format/duration/
  level gate failures recorded.
- `--probe-ui-lengate-gsrt-24-r66` -> exit 1,
  `runs/20261014T023254414734Z-ui-lengate-gsrt-24-r66/measurements.json`;
  `sox_detected_format: "wav"`, stat `fmt chunk not found`,
  `decode_error_tool: "ffprobe"`.
- `--probe-ui-lengate-gsrt-25-r66` -> exit 1,
  `runs/20261014T023255482162Z-ui-lengate-gsrt-25-r66/measurements.json`;
  `sox_detected_format: "gsrt"`, stat `premature EOF`, native
  `fmt chunk not found`.
- `--probe-ui-lengate-hcom-131-r66` -> exit 1,
  `runs/20261014T023256568490Z-ui-lengate-hcom-131-r66/measurements.json`;
  `sox_detected_format: "wav"`, 43 samples on all three legs,
  `sox_f32_bytes: 172`, gate failures recorded (the below-gate member is a
  working wav — the cleanest possible fallthrough evidence).
- `--probe-ui-lengate-hcom-132-r66` -> exit 1,
  `runs/20261014T023257631686Z-ui-lengate-hcom-132-r66/measurements.json`;
  `sox_detected_format: "hcom"`, stat `premature EOF`, native (`-t wav`)
  leg decodes 44 samples (the suppressed member is genuinely readable).

Setup notes: `python3 -m py_compile` on both fixture scripts + all three
scratch tools -> exit 0; `git diff --check` -> clean. Tracked
`__pycache__/*.pyc` binaries differ — mechanical `py_compile` regeneration
churn, same disclosure as r62/r63/r64/r65; parent decides. One
caught-and-fixed defect before the ledger: the first builder left the hcom
pad byte @158 at the ramp value (0x55) instead of the critic's explicit 0 —
both members still detected correctly, but the tracked equivalent must
replicate the verified-decodable construction exactly; fixed, rebuilt, and
re-verified byte-identical to the scratch D01 (`cmp` clean). No `lsp`
device is exposed on this substrate — symbol-adjacent edits (chain heads,
exclusion sum, dispatch branch) applied by hand against read file text,
per the fallback rule (same as r64/r65).

## Labrat (the seat's one bounded probe)

One `ufo-labrat` dispatched on the falsifiable hypothesis "a RIFF-family
file can be detected `wve`". It returned **FALSIFIED** — but with an
execution caveat: its toolset exposed no shell/exec, so its contribution was
analysis over already-executed sibling evidence plus source corroboration,
not fresh probes. Its synthesized table independently re-derived my W-series
results; its one factual error (`/usr/bin/sox` "does not exist") is wrong on
this host — `/usr/bin/sox -> sox_ng` verified directly. All load-bearing
claims above are my own executed measurements; the labrat output is
advisory-corroborative only.

## Per-axis claim (author evidence only; verdict belongs to verifier + adjudicator)

- **depth**: the preemptor map on RIFF+0x84@256 is now *complete* — the
  reachable pre-act set is exactly {gsrt, hcom}; wve is geometrically
  excluded (byte-0 `A` vs `R`), with the predicate identified empirically
  (15 exact bytes, floor 15, no second conjunct, anchor at 0) and the
  reader-side asymmetry shown (reader wants 18-byte ID1). Detection is
  detect-only, not decode-only: hcom-detected files can fully decode
  through the preemptor's own reader (9 samples, exit 0).
- **coverage**: +6 tracked members — the first positive-decode preemptor
  pair (hcom decodes | act decodes, one byte between routes) and four
  exact length-gate boundaries (24|25, 131|132) pinning `len >= p + l`.
  Ledger 96->102 commands.
- **calibration**: prior-96 exits position-exact, all 96 receipts
  byte-identical, normal receipt byte-identical to r65's; new receipts
  deterministic across independent runs; the tracked hcom member is
  byte-identical to the critic's independently built D1 (sha256 match).

## Conditional replay shape (for the non-author verifier)

102 commands = the r65 96 verbatim with
`--probe-ui-{dec-hcom,dec-act,lengate-gsrt-24,lengate-gsrt-25,lengate-hcom-131,lengate-hcom-132}-r66`
inserted newest-first at positions 2-7 (TSV order in `ledger-r66.tsv`).
Expected 44 exit 0 / 58 exit 1; prior-96 receipts byte-identical to r65's;
new receipts deterministic (each re-produced byte-identical JSON).

## UNKNOWNs / limits

- Verified on this host only: SoX_ng 14.8.0.1 handler order + ffmpeg n9.0.1.
  The `act` row is `#if USING_FFMPEG` — ffmpeg-less builds drop
  `AUTO_DETECT_SIZE` to 132; the act row and this dec-pair's bridge leg
  vanish, but the wve/gsrt/hcom geometry is unchanged (untested,
  source-level inference).
- The wve falsification is for the RIFF family (`RIFF`/`RIFX`/`RF64`@0);
  other containers were out of scope. wve's reader semantics beyond
  start_read (checksum behavior, ID2 semantics) unprobed — boundary-seat
  territory.
- `pair_dec_hcom`'s `measure_pipeline` entry records the pipeline stop
  point, not a decode failure — the hcom decode itself is proven by
  `sox_stat_samples_read: 9` and `sox_f32_bytes: 36`.
- The len-gate below-gate members carry self-consistent (smaller) RIFF
  sizes, so pair `cmp -l` shows the size bookkeeping bytes plus the
  gate-crossing byte — intentional, documented above.
- stdin/pipe transports on the new members unexercised here (r65-boundary
  covered the gsrt transport fork).
- No standards-conformance, decoder-correctness, fidelity, audibility,
  production, rights, engine, or promotion claim — local fixture
  measurements.

## Blockers

None. One bounded labrat dispatched (see above). No commit/push/merge
performed; parent integrates.
