# R63 critic — falsify the byte-256 `act` autodetect attribution

Seat: critic. Task: falsify r62's claim that payload byte 256 = `0x84` trips
SoX_ng's `act` autodetect → `(ffmpeg)` bridge. Hypotheses under test:
(a) act scans a *range* and 256 isn't special; (b) the trigger needs a
multi-byte signature; (c) routing was content-correlated, not
position-correlated — produce act-routing without `0x84@256` and native-wav
routing with it.

Worktree: `~/Projects/prymeagnt/audio`; scratch+receipts:
`corpus/live/r63-critic/` (`sweep.py`, `sweep_results.csv` 1,408 probe rows,
`var/` 32 kept exhibits). Host: SoX_ng 14.8.0.1, ffmpeg/ffprobe n9.0.1.
Base files byte-verified vs r61 records: `pair_valid_17.wav`
`15cadf242eff13ed…` / `pair_valid_16.wav` `2c5e244fb19bed5f…` (copied to
scratch).

Probe primitive (1,408 harness runs + ~20 ad-hoc): `sox -V6 <f> -n` → parse
`` detected file format type `X' `` and the `(ffmpeg)` handler marker;
`sox <f> -t f32 -e floating-point - | wc -c` for decode counts.

## Verdict

**The byte-256 attribution survives all three falsification angles for this
fixture family, but the naive phrasing "byte 256 = 0x84 ⇒ act/ffmpeg" is
falsified in both directions at the edges.** The full predicate on this build
is a first-match table rule with two more conjuncts and two preemptors:

```
detected == act  ⟺  len ≥ 257  ∧  data[0:4] == "RIFF"  ∧  data[256] == 0x84
                    ∧  ¬("ring.bin\0" @ 16)  ∧  ¬("FSSD" @ 65 ∧ "HCOM" @ 128)
```

sox_ng-14.8.0.1 `formats.c:71-72` (CHECK macro: `len >= p1+l1 && memcmp…`),
`:93` `CHECK(act, 0,4,"RIFF", 256,1,"\x84")` — the **only** act rule — ordered
before `CHECK(wav, RIFF/RIFX/RF64 @0, "WAVE" @8)` at `:95-97`. `act` resolves
to the `(ffmpeg)` pseudo-handler via `ffmpeg.c` `names[]` (`-t act` on the
base file shows `Input File … (ffmpeg)`).

## Per-hypothesis verdicts

| hypothesis | verdict | key evidence |
|---|---|---|
| (a) act scans a byte *range*; 256 not special | **FALSIFIED** | 86 probes: `0x84` injected at each alternative file offset (255, 257, 258, 260, 512, 8192, 11587, header and deep payload positions…) with byte 256 zeroed → **every one detected `wav`**, never `act` (`sweep_results.csv` rows `B_*`: 87 wav / 1 act — the single act row is the all-zeros-except-256 file). `B_all84_not256` (11,520 payload bytes *all* `0x84` except file[256]=0x00) → `wav`. `B_only256is84` (the *only* `0x84` in the file is at 256) → `act`, decoded 3,839. Position 256 is necessary; no other position contributes. |
| (b) multi-byte signature / neighboring values | **FALSIFIED — single byte confirmed** | Full value sweep at offset 256 on both bases: exactly **1 of 256** values (`0x84`) → `act`; 255 → `wav` (`A17_*`, `A16_*` histograms). `0x83`/`0x85`/`0xC4`/`0x04` all `wav` — no mask or range semantics. Neighbor sweeps: bytes 255, 257, 258 each swept 0x00–0xFF with `0x84` held at 256 → **780/780 `act`**; bytes 259–261 spot-swept likewise. Neighbors are don't-care. |
| (c) content-correlated, not position-correlated | **claim CONFIRMED as file-position predicate; naive byte⇒ffmpeg phrasing FALSIFIED both ways** | See below. |

## (c) the decisive position-vs-content experiments

`F_junk_off84` / `F_junk_keep84`: a 16-byte `JUNK` chunk inserted before
`data` shifts the payload +16; the payload's original `0x84` moves to file
offset 272 while file[256] takes payload byte 172 (`0x03`) → detected
**`wav`** → native reject (`number of valid bits exceeds…`). The identical
shifted file with file[256] forced to `0x84` → **`act` → `(ffmpeg)` →
3,839 samples**. The predicate tests *file offset* 256, not payload content —
a payload `0x84` at 272 is inert, a non-payload-derived `0x84` at 256 fires.
(For the r61 header shape file[256] = data-chunk byte 188 = low byte of
sample 94 = `0x84` from sample value `0x0484`; "payload byte 256" in the r62
phrasing is loose — it is *file* byte 256.)

### act-routing WITHOUT `0x84@256`

- Via content autodetect: **impossible on this build** — `formats.c:93` is the
  only act CHECK and it requires the byte. All 1,408 harness rows: zero `act`
  detections without `0x84` at file offset 256.
- Via explicit type: `sox -t act pair_valid_17.wav -n` → `(ffmpeg)`, exit 0 —
  the handler route is reachable regardless of content (not autodetect).
- Via extension fallback: `var/H_rand.act` (300 magic-free bytes, name
  `.act`) → no "detected" line, fails `premature EOF` — the *same* error as
  forced `-t act` on that content and distinct from `-t wav`'s `RIFF header
  not found`: the extension resolved the act(=ffmpeg) handler, which then
  failed to open. (`H_v16_b256_00.act`, real WAV content named `.act` with
  byte 256 = `0x00` → detected `wav`, native decode 5,760: content
  autodetection precedes extension fallback.)

### native-wav routing WITH `0x84@256` — ACHIEVED, twice

- `var/D_rifx_pcm16_84.wav` — a genuine big-endian RIFX PCM16 file
  (sample 106 = `0x8400` puts `0x84` at file offset 256). `sox -V6`:
  `detected file format type 'wav'` → `Found RIFX header` →
  `Microsoft PCM format, 1 channel, 48000 … 11520 data bytes` →
  **fully decoded 23,040 B = 5,760 samples through the native wav handler**.
  `D_rf64_84` (RF64@0) likewise detects `wav`. The literal `"RIFF"` conjunct
  is load-bearing: RIFX/RF64 fail it, fall through act, match wav rules at
  formats.c:96-97.
- `var/D_xxxx_84.wav` (`XXXX`@0, `0x84`@256, name `.wav`) → no autodetect
  match → extension fallback → native wav handler (`RIFF header not found`).
  Degenerate, but the route is native wav with the byte present.

For a *conforming member of this fixture family* (RIFF+WAVE, ≥257 B), native
wav with `0x84@256` remains impossible: act precedes wav and there is no
handler fallback — `open_read` aborts on `startread` failure
(`formats.c:961-964`, `goto error`), which is also why detected-`wav`
valid17 hard-fails rather than retrying ffmpeg.

## Bounds pinned this round

- **Length floor**: predicate requires ≥257 file bytes
  (`AUTO_DETECT_SIZE 257 /* for act */`, `formats.c:61`). Truncated at 256 →
  `wav`; at 257 → `act` (then ffmpeg decodes 63 samples = `floor(189/3)` —
  incidentally corroborating r62's per-packet floor law on a fresh point).
- **RIFF only**: `riff` lowercase → no match; `WAVE`@8 is *not* part of the
  act conjunct — `D_riff_nowave_84` (RIFF+`XXXX`@8+`0x84`@256) → `act`, and
  `D_riff_avi_84` (RIFF+`AVI `) → `act`: act even preempts the `avi` CHECKs
  (formats.c:176-180). Any RIFF container ≥257 B with `0x84`@256 misdetects.
- **Preemptors**: only two earlier CHECKs can coexist with `RIFF`@0 —
  `gsrt` (`"ring.bin\0"`@16, 9 bytes incl. NUL: my first 8-byte write still
  detected `act`, confirming the terminator is compared) and `hcom`
  (`FSSD`@65 ∧ `HCOM`@128). Both → detected `gsrt`/`hcom` with the `0x84`@256
  held; their handlers then fail on the wav content. 0x84@256 is therefore
  *necessary but not literally sufficient* — table order decides.
- **Build condition**: the act CHECK sits inside `#if USING_FFMPEG`
  (`formats.c:91-94`) and `AUTO_DETECT_SIZE` is 257 only there (132
  otherwise): a non-ffmpeg sox_ng build cannot detect `act` at all — on such
  a build this file family would route native `wav` (and reject valid17)
  regardless of byte 256. Scope: this host's USING_FFMPEG build only.
- `(ffmpeg)` marker cosmetic note: `H_v16_orig84.act` detects `act` but
  prints `Input File : '…'` *without* `(ffmpeg)` — the parenthetical marks a
  handler/extension mismatch and is suppressed when they agree; the
  `detected file format type` line is the authoritative receipt.

## Smallest safe claim wording

"The routing collision on this host is: **file offset 256 = `0x84` in a
RIFF-magic file ≥257 bytes** — formats.c:93 `CHECK(act,0,4,"RIFF",256,1,0x84)`,
first-match before wav; `act` resolves to the `(ffmpeg)` pipe. For the fixed
68-byte-header fixture family, file 256 = payload byte 188 (sample 94 LSB);
any chunk insertion or header-size change relocates which payload byte is
tested." A tracked sweep-matrix control can pin exactly that predicate
(byte-256 held `0x84` vs `0x00` on the same header, plus one RIFX or
JUNK-shift row to pin the conjunct and the file-vs-payload distinction).

## Axis impact

- **expansion**: the collision surface is now fully bounded — exact byte
  value (1/256), exact position (file 256 only), two conjuncts, two
  preemptors, length floor, build flag, extension/`-t` bypasses. Previously
  the story was "a payload byte happens to be 0x84"; now the predicate's
  complete truth table is measured.
- **quality**: 1,408-row CSV + 32 named exhibits; every number quoted from
  this run's own probes; base files SHA-verified against r61 records.
- **discernment**: the naive "byte 256 ⇒ ffmpeg" claim fails at the edges
  (RIFX/RF64/extension/preemptors/build-flag); the r62 author's precise
  phrasing ("`CHECK(act, 0,4,"RIFF",256,1,"\x84")` … a property of the
  payload bytes") is essentially correct — the refinement needed is *file*
  offset 256, not payload offset, plus the preemptor/length conditions.
  `B_00256` CSV label reads `256=0x00;256=0x84` but only `0x00` was applied
  (position-loop guard) — a label artifact, result `wav` is correct.
- No runner receipts produced/needed — this round's claim is pre-measurement
  routing, exercised directly on `sox`.

## Receipts

- `corpus/live/r63-critic/sweep.py` — deterministic generator+prober.
- `corpus/live/r63-critic/sweep_results.csv` — 1,408 rows:
  name/base/mods/detected/handler/exit/fail/samples. Histograms:
  `A17_*`/`A16_*` 255 wav + 1 act each; `B_*` 87 wav + 1 act; `C_*` 780 act.
- `corpus/live/r63-critic/var/` — 32 exhibits (SHA-256 prefixes in scratch
  listing), incl. `D_rifx_pcm16_84.wav` (native decode 5,760 with `0x84`@256),
  `F_junk_{off,keep}84.wav`, `B_all84_not256.wav`, `B_only256is84.wav`,
  `E_{gsrt,hcom}_*.wav`, `G_trunc{256,257}.wav`, `H_rand.act/.wav`.
- Commands: `sox -V6 <f> -n` (detection line), `sox <f> -t f32 -e
  floating-point - | wc -c` (decode count), `sox -V6 -t act|wav|ffmpeg <f>
  -n` (forced references). Source quotes: `corpus/live/r63-boundary/src/
  sox_ng/src/formats.c:61-97, 254-267, 910-934, 961-964`; `ffmpeg.c` names[]
  `:112-116`.

## Blockers / residual unknowns

None blocking. Residual: only this host's build probed (USING_FFMPEG=1
inferred from observed `act` behavior + source); libmagic path (`formats.c`
254-267) present but untriggered in these tests (all inputs either matched a
CHECK or fell to extension); whether `sox_find_format` could ever resolve
`act` to a *native* handler on builds shipping act.c is untested here —
irrelevant to this host's predicate.
