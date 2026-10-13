# R63 author — `act` autodetect predicate PINNED (file[0:4]=="RIFF" ∧ file[256]==0x84)

host: devin (same lane as R61/R62)
Clean-before: canonical lane repo `/home/vgpnk/Projects/shokunin/audio-shokunin` HEAD `3c96a69`;
worktree `/home/vgpnk/Projects/prymeagnt/audio` (`.shokunin/audio` symlinks into the canonical repo).
Toolchain under test: SoX_ng v14.8.0.1 (`sox: SoX_ng v14.8.0.1`), ffmpeg/ffprobe n9.0.1.

## Scoped move — declared claim: RESOLVED, predicate established exactly

R62 disclosed the fixture fragility: the r61 pair's payload happens to carry `0x84` at file
offset 256, which trips SoX_ng's `act` format autodetect (probed before `wav`) and silently
routes the file through the `(ffmpeg)` bridge; flipping byte 256 to `0x00` restores the native
`wav` reader, which FATALLY rejects the valid17 header. R63's declared depth move: pin or
falsify the `act` trigger — which byte positions and which values flip `sox --i`/decode
routing on this file family.

**Result: the trigger is a two-conjunct exact predicate, not a window and not near-offset.**

```
act detected  <=>  len >= 257  ∧  file[0:4] == "RIFF"  ∧  file[256] == 0x84
```

- **value-exact**: over ALL 256 byte values at offset 256 on both r61 pair members, `0x84`
  alone selects `act`; the other 255 values all select `wav` (512 probes).
- **position-exact**: over ALL 11,588 byte positions on both pair members, `0x84` at offset
  256 alone selects `act`; no other position ever triggers it (23,176 probes). Positions
  ≥257 cannot be triggers by construction — the autodetect buffer is exactly 257 bytes.
- **conjunction-exact**: `RIFF`@0 is required (RIFX doesn't satisfy it — it matches the
  separate `CHECK(wav,"RIFX",…)` row instead); `WAVE`@8 is NOT consulted — a file with
  WAVE destroyed still detects `act`.
- **order-exact**: the `act` row precedes `wav` in the table; files matching both
  (RIFF+WAVE+0x84@256) detect `act`, never `wav`.

## Source basis (upstream sox_ng-14.8.0.1 tarball, `src/formats.c`)

`AUTO_DETECT_SIZE 257` ("for act") — `auto_detect_format` reads at most 257 bytes:
```c
#define CHECK(type, p2, l2, d2, p1, l1, d1) if (len >= p1 + l1 && \
    !memcmp(data + p1, d1, (size_t)l1) && !memcmp(data + p2, d2, (size_t)l2)) return #type;
/* Must come before wav because it looks like a PCM WAV file */
CHECK(act   , 0, 4, "RIFF" , 256,1, "\x84")      /* formats.c:93 */
CHECK(wav   , 0, 4, "RIFF" , 8,  4, "WAVE")      /* formats.c:95 */
```
First matching row wins; on no match SoX falls back to the file extension
(`auto_detect_format` NULL → `lsx_find_file_extension`, formats.c:911-925).

Source tarball: `corpus/live/r63-boundary/src/sox_ng-14.8.0.1.tar.gz` (sibling seat's
fetched copy; extracted to /tmp for reading only — their scratch is untouched).
The `act` handler name resolves to the FFmpeg pseudo-handler (`src/ffmpeg.c`), which pipes
`ffmpeg -loglevel quiet -nostdin -strict -2 -i FILE -f au -` — the bridge whose downstream
behavior R62 decomposed.

## Empirical sweep (scratch: `corpus/live/r63-author/`)

Generator/runner `gen_sweep.py`; every variant probed with `sox -V6 <f> -n stat` and the
detected format / `(ffmpeg)` tag / Samples-read / exit / FAIL line recorded in
`results.tsv` (23,738 data rows, header at line 1). Bases: the real r61 pair —
`corpus/live/round-61/pair_valid_{17,16}.wav`, both carrying natural `0x84` at offset 256
(file[256] = payload byte 188 = sample 94's low byte, data chunk at offset 68).

### Targeted batch (50 named variants in `variants/`)

| variant | detected | route | samples | exit | observation |
|---|---|---|---|---:|---|
| v17_val_{00,01,7f,80,83,85,ff} | wav | native | — | 2 | only 0x84 triggers |
| v17_val_84 (=base) | act | ffmpeg | 3,839 | 0 | base route confirmed |
| v16_val_{00,01,7f,80,83,85,ff} | wav | native | 5,760 | 0 | same predicate, non-fatal readout |
| v16_val_84 (=base) | act | ffmpeg | 5,760 | 0 | route flips, count unchanged |
| v17_pos_{255,257,258,511,512,1024} | wav | native | — | 2 | 0x84 nowhere else triggers |
| v17_pos_256 | act | ffmpeg | 3,839 | 0 | (byte256→0x00 then →0x84 = base) |
| v16_pos_{255,257,258,511,512,1024} | wav | native | 5,760 | 0 | same on control member |
| v16_pos_256 | act | ffmpeg | 5,760 | 0 | |
| v{16,17}_c_riff0 (byte0 'R'→'X') | NONE | none→ext wav | — | 2 | autodetect NULL; ext→native `RIFF header not found` |
| v{16,17}_c_riff3 (byte3 'F'→'X' = "RIFX") | wav | native | — | 2 | separate `CHECK(wav,"RIFX")` matched; `file encoding 0xfeff … not supported` — RIFX ≠ RIFF for act |
| v{16,17}_c_wave8 (byte8 'W'→'X', 0x84@256 kept) | **act** | ffmpeg tried | — | 2 | act does NOT consult WAVE@8; ffmpeg can't parse → `premature EOF` |
| v{16,17}_c_n{255,257}_{00,ff} (neighbors mutated, 0x84@256 kept) | act | ffmpeg | 3,839/5,760 | 0 | predicate is the single byte; neighbors unconstrained |
| v16_c_len257_keep84 (257-B prefix) | act | ffmpeg | 94 | 0 | `len>=257` boundary: fires |
| v16_c_len257_zero84 (257-B prefix, byte256→0x00) | wav | native | 94 | 0 | same length, no trigger |
| v16_c_len256_84at255 (256-B file, 0x84@255) | wav | native | 94 | 0 | `len<257` → act row skipped even with 0x84 in buffer |
| v16_c_len258_keep84 (258-B prefix) | act | ffmpeg | 95 | 0 | longer-than-buffer files still fire |
| v17_c_ext.bin (same bytes, real `.bin` name) | act | ffmpeg | 3,839 | 0 | autodetect is content-based; extension unneeded on a match |
| v16_c_noriff.bin (RIFF destroyed, `.bin`) | NONE | — | — | 2 | NULL detect → ext fallback → `no handler for file extension 'bin'` |

### Exhaustive batches (streamed through one tempfile; all rows in `results.tsv`)

- **Value domain** `fullval` (512 probes): per base, detected `act` = **1 of 256** (value
  `0x84`), `wav` = 255. No other format name ever emitted.
- **Position domain** `fullpos` (23,176 probes): per base, `act` at **exactly offset 256**
  (1 of 11,588); `wav` = 11,579; `NONE` = 8 — precisely positions 0-3 (RIFF destroyed) and
  8-11 (WAVE destroyed), consistent with both conjunct semantics and ext-fallback.
- On v17 every non-`act` row exits 2 (`number of valid bits exceeds the number of bits per
  sample`) — the fatal consequence; on v16 every `wav` row decodes 5,760 except rows whose
  `0x84` landed inside structured header fields (fmt tag/size @12-19, format tag @20-21,
  channels @22-23 → 5,676 and 0 samples respectively, bits @34-35, valid-bits @38-39,
  GUID subtype tag @44-45, data tag @60-63 → native exit 2; data-size @64-67 increases
  clamp to EOF → still 5,760). These are native-reader header-corruption artifacts, not
  act-predicate data — recorded verbatim, interpretation out of scope.

**Answer to the declared question**: the `act` trigger is one specific byte predicate at
exactly offset 256 (the last byte SoX_ng's 257-byte probe window can see), value `0x84`
exactly, AND-ed with `RIFF`@0 on files of ≥257 bytes — never a window, never near-offset,
never WAVE-dependent. The claim is PINNED, not merely near/at-256.

## Tracked changes (additive only; `format_failures`, `SPECS["ui"]`, thresholds, canonical17, prior modes untouched)

`corpus/fixtures/build_artifacts.py` **+32/−1**: `build_ui_route_act_r63_probe()` emits
`corpus/live/round-63/pair_route_{84,00}.wav` — WAVE_FORMAT_EXTENSIBLE mono48k fmt40
**valid17** headers (the fragile family) over one shared deterministic payload
(`0.25·sin 920 + 0.10·sin 1380` ×8191, 5,760 frames), byte 256 pinned by assignment to
`0x84` vs `0x00`. Two argparse flags + newest-first dispatch branch.

`corpus/fixtures/measure_audio.py` **+25/−4**: two flags
(`--probe-ui-route-act-{84,00}-r63`), mutual-exclusion sum, builder-flag forwarding, one
measurement block (runs `sox -V6 -n stat` to record `sox_detected_format`/`sox_route` in
the entry, `measure()` under `SPECS["ui"]`, `CalledProcessError` → decode-failure entry),
and the `mode`/`suffix` chain heads prepended.

Pair byte evidence: both 11,588 B; `cmp -l` → **only 1-based offset 257 (= file byte 256)
differs** (`204` vs `0` octal). SHA-256 `cf5edecce1812f0a0a5c1a16f0b2a920118be3f281b3f43638c1bc2f9f6b93e4`
(84) / `cb77db319a7a791fa95ed14d83ab08f0c75b5c80635ec1897a9dea7c591c621a` (00); rebuild
deterministic (identical SHA on re-run under either flag).

Live routing on the tracked pair:
- `pair_route_84.wav`: `sox --i` → `Input File … (ffmpeg)`; `-V6` → `detected file format
  type 'act'`, `Samples read: 3839`; ffprobe `pcm_s24le`/24-bit/`0.080 s`.
- `pair_route_00.wav`: `sox --i` → FAIL `number of valid bits exceeds the number of bits
  per sample` (exit 2); `-V6` → `detected file format type 'wav'` then the same FAIL.

## What ran — 86-command ledger (84 prior verbatim + 2 new modes at positions 2–3)

All commands `python3 .shokunin/audio/corpus/fixtures/measure_audio.py <flag>` from the
worktree root; receipts under `corpus/live/runs/<stamp>-<suffix>/measurements.json`.
Runner `corpus/live/r63-author/run_ledger.py`; full TSV
`corpus/live/r63-author/ledger-r63.tsv`. Totals: **43 exit 0 / 43 exit 1** (r62's 43/41
plus the two new exit-1 probes). Removing my two new rows, the prior-84 exit sequence
matches r62's ledger position-for-position (zero diffs), and **all 84 prior-mode receipts
are byte-identical** (sha256 compared file-by-file against the r62 ledger paths).

New-mode receipts (deterministic — a manual re-run produced JSON-identical files):
- `--probe-ui-route-act-84-r63` → exit 1, receipt
  `corpus/live/runs/20261013T234233555211Z-ui-route-act-84-r63/measurements.json`;
  sole failing entry `ui_route_act_84_r63_probe`: `format: expected PCM16`,
  `duration: outside ±1 ms`, `level: clipping headroom or near silence`,
  `spectrum: centroid outside fixture band` — the r61 valid17 signature; entry also
  records `sox_detected_format: "act"`, `sox_route: "ffmpeg"`, codec `pcm_s24le`, 0.080 s.
- `--probe-ui-route-act-00-r63` → exit 1, receipt
  `corpus/live/runs/20261013T234234583776Z-ui-route-act-00-r63/measurements.json`;
  `ui_route_act_00_r63_probe`: `decode: default SoX route rejected input`, with
  `sox_detected_format: "wav"`, `sox_route: "native"`, `sox_exit_code: 2`, and the verbatim
  stderr (`number of valid bits exceeds the number of bits per sample`).
- Normal-run receipt `20261013T234232472196Z-normal/measurements.json` is byte-identical
  to r62's normal receipt (row-01 of both ledgers compared).

Setup notes: `python3 -m py_compile` both fixture scripts → exit 0; `git diff --check` →
clean. First ternary-chain edit unbalanced the giant `mode`/`suffix` heads (one extra
open paren) — caught by py_compile before any runner invocation; zero receipts affected.
First draft of the two extension controls wrote `*_bin.wav` (named `.bin` intended but
`.wav` written); the mislabeled rows were removed from `results.tsv`, real `.bin`
variants re-probed — the corrected rows above are what stand.
Two tracked `__pycache__/*.pyc` binaries differ — mechanical `py_compile` regeneration
churn, same disclosure as r62; parent decides. A sibling `r63-boundary` seat is probing
the same predicate concurrently (their variants tar/source tree read-only-referenced);
shared `corpus/live/runs/` timestamps interleave but receipts are per-run complete.

## Per-axis claim (author evidence only; verdict belongs to verifier + adjudicator)

- **depth**: the r62-disclosed fragility is now a closed predicate — one exact byte
  (position 256, value 0x84) AND-ed with RIFF@0, order-pinned before `wav`, proven over
  the full byte-value domain (512 probes) and the full position domain (23,176 probes)
  on both r61 pair members, plus length-boundary (256/257/258-B) and conjunct-elimination
  controls (RIFX, WAVE, neighbors, extension).
- **coverage**: a tracked matched pair differing only at the discriminating byte —
  `pair_route_{84,00}.wav` + two opt-in modes — replays the route flip and both
  consequences (ffmpeg-bridge decode vs native fatal) as first-class receipts carrying
  `sox_detected_format`/`sox_route` fields; ledger 84→86 commands.
- **calibration**: prior 84 exits position-exact and all 84 prior receipts byte-identical;
  normal receipt byte-identical to r62's; new probes land inside the expected failure
  classes (4-gate signature / decode).

## Conditional replay shape (for the non-author verifier)

86 commands = the r62 84 verbatim with `--probe-ui-route-act-84-r63` and
`--probe-ui-route-act-00-r63` inserted at positions 2–3 (TSV order in `ledger-r63.tsv`).
Expected 43 exit 0 / 43 exit 1; prior-84 receipts byte-identical to r62's; new receipts
deterministic (two independent runs produced identical JSON).

## UNKNOWNs / limits

- Verified on this host only: SoX_ng 14.8.0.1 handler order + ffmpeg n9.0.1; the `act`
  row is `#if USING_FFMPEG` — ffmpeg-less builds skip it entirely (AUTO_DETECT_SIZE 132).
- Exhaustiveness is over THIS file family's bytes: 11,588-byte WAVE_FORMAT_EXTENSIBLE
  fixtures. Other containers/payloads share the same row semantics (source), but only
  this family's sweep was executed.
- Native-reader behavior on header-corrupted positions (22→5,676 samples, 23→0, etc.) is
  recorded as data, not explained — outside the act-predicate question.
- `v16_c_wave8` observed: detected `act` → ffmpeg pipe fails → `premature EOF` (no
  `(ffmpeg)` tag printed since startread never completes); whether SoX retries other
  handlers after an act-handler failure was not traced further here — the sibling
  `r63-boundary` report resolves it convergently (single dispatch, `lsx_fail` on
  handler failure, no retry loop or fallback on the open path).
- No standards-conformance, decoder-correctness, fidelity, audibility, production,
  rights, engine, or promotion claim.

## Blockers

None. No labrat dispatched this round (the sweep was cheap enough to run directly).
No commit/push/merge performed; parent integrates.
