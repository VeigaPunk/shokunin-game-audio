# R63 scribe — `act` autodetect predicate: knowledge-entry + LOG drafts

Seat: scribe (report-only documentation draft). Host: devin. Lane axis this
round: **depth** — map the `act` autodetect predicate that r62 disclosed as
fixture fragility (r61 `pair_valid_17.wav` byte 256 = `0x84` → detected `act`
→ `(ffmpeg)` bridge → the 3,839 packet-residue count; byte 256 = `0x00` →
native `wav` → fatal reject).

Toolchain on record: `sox: SoX_ng v14.8.0.1`, `ffprobe`/`ffmpeg` n9.0.1,
Python 3.14.7 (all `/usr/bin`). Scratch under
`.shokunin/audio/corpus/live/r63-scribe/` (`variants/` 293 fixtures,
`gen_probes.py`, `sweep.sh`, `results.tsv` 293 data rows, `logs/`). No tracked
file, fixture, receipt, predicate, or other lane's surface written; nothing
committed. The project runner was deliberately not invoked (it has no
`--runs` flag — r63-reviewer — and would write the shared `live/runs/`); all
evidence is direct `sox` probing of scratch variants.

## Verdict on the declared claim

**PINNED.** The `act` trigger is an exact two-conjunct byte predicate, not a
window, not a near-offset, not payload-content-sensed:

```
detected == "act"  ⟺  len ≥ 257  ∧  file[0:4] == "RIFF"  ∧  file[256] == 0x84
                      ∧  no earlier CHECK row matched
                          (gsrt: "ring.bin\0" @16, 9 B incl. NUL;
                           hcom: "FSSD" @65 ∧ "HCOM" @128)
```

`len` = bytes available to `auto_detect_format` = min(filesize, 257)
(`AUTO_DETECT_SIZE 257 /* for act */`, formats.c:61). For this fixture
family's 68-byte header, file offset 256 = payload byte 188 = PCM16 sample 94
LSB — coincidence, not semantics: it is the **file** offset that is tested
(JUNK-shift proof below).

## Scribe's own sweep (independent of sibling sweeps; `results.tsv`)

Base fixtures SHA-verified vs r61 records: `pair_valid_17.wav`
`15cadf242eff13ede3ff25b992f4410ec89a76a9814e2afad346b4052eb63fe4`,
`pair_valid_16.wav` `2c5e244fb19bed5f6abdaa605ae503dd6685f88cb440de93a4cd313959591d00`;
`od -A d -t x1 -j 256 -N 1` → `84` on both. Probe primitive per variant:
`sox -V4 <f> -n stat` → parse `` detected file format type `X' `` + exit;
`sox <f> -t f32 - | wc -c` decode bytes; `sox --i` `(ffmpeg)` tag count.
293 rows: **act = 9, wav = 278, none = 4, gsrt = 1, hcom = 1**.

### Value domain — exactly {0x84} (256-file sweep at offset 256, real v17 payload)

`v17_b256_XX.wav` for all XX ∈ 0x00–0xFF: **255 → `wav`** (each exit 2,
native `number of valid bits exceeds the number of bits per sample`),
**1 → `act`** (XX = `84`: exit 0, 15,356 f32 bytes = 3,839 samples,
`sox --i` `(ffmpeg)` tag present). Verbatim neighbors:

| variant | b256 | detected | exit | f32 bytes |
|---|---|---|---|---:|
| v17_b256_83.wav | 83 | wav | 2 | 0 |
| v17_b256_84.wav | 84 | act | 0 | 15,356 |
| v17_b256_85.wav | 85 | wav | 2 | 0 |

### Position domain — exactly offset 256

0x84 planted singly at offsets {12, 64, 100, 128, 188, 255, 257, 258, 300,
511, 512, 1024, 2048, 4096, 8192, 11587} with byte 256 zeroed → **all `wav`**
(exit 2, vb17 native reject). `v17_off255+256.wav` (0x84 at 255 **and** 256)
→ `act`, 15,356 B. `v17_off255+257_no256.wav` (flanked, 256 clear) → `wav`.
Position 256 is necessary; neighbor bytes are don't-care.

### Length floor — ≥257 file bytes

| variant | size | detected | exit | f32 bytes |
|---|---:|---|---|---:|
| v17_trunc256.wav | 256 | wav | 2 | 0 |
| v17_trunc257.wav | 257 | **act** | 0 | 252 |
| v17_trunc257_b256_00.wav | 257 | wav | 2 | 0 |
| v17_trunc258.wav | 258 | **act** | 0 | 252 |

A 257-byte prefix with `0x84` at its last byte fires `act`; one byte shorter
(256 B) cannot — the `len >= p1+l1` guard and `AUTO_DETECT_SIZE` bound.

### Conjuncts — `RIFF`@0 required; `WAVE`@8 NOT consulted by act

| variant | change | detected | outcome |
|---|---|---|---|
| v17_xiff.wav | `RIFF`→`XIFF`, 0x84@256 kept | none | ext `.wav` → wav handler → `RIFF header not found`, exit 2 |
| v17_riff_lower.wav | `riff` lowercase | none | ext → `RIFF header not found`, exit 2 |
| v17_rifx.wav | `RIFX`@0 + `WAVE`@8 + 0x84@256 | **wav** | native reader (act requires literal `RIFF`; RIFX matches wav's own row, formats.c:96) |
| v17_nowave.wav | `WAVE`@8 zeroed, RIFF + 0x84@256 kept | **act** | ffmpeg demux fails → `premature EOF`, exit 2 |
| v17_nowave_b256_00.wav | WAVE zeroed **and** byte256→0x00 | none | ext → `RIFF header not found` |

On a RIFF-but-not-WAVE file the same byte decides **act-vs-nothing** (then
extension), not act-vs-wav — the conjunct sets differ.

### File offset, not payload offset (JUNK-shift pair)

24-byte `JUNK` chunk inserted before `data` at offset 60 (RIFF size +=24):
the payload's `0x84` moves to **file 280**; file[256] becomes `0x2b`.

- `v17_junk24.wav` → detected `wav` → `number of valid bits exceeds…`, exit 2.
- `v17_junk24_forced84.wav` (same shifted file, file[256] planted 0x84) →
  detected `act` → 15,356 B = 3,839. The inert payload `0x84` at 280 does
  not fire; the planted byte at 256 does.

### Earlier-row preemption — act is sufficient only if no earlier row matched

- `v17_gsrt.wav` (`"ring.bin\x00"` written at 16–24, 0x84@256 kept) →
  detected **`gsrt`** → `premature EOF`, exit 2. (The CHECK literal is 9
  bytes including the C string NUL — formats.c:81.)
- `v17_hcom.wav` (`FSSD`@65 + `HCOM`@128, 0x84@256 kept) → detected
  **`hcom`** → `bad compression type`, exit 2.
- All other pre-act rows require non-`RIFF` magic at offset 0 and cannot
  coexist with this family (critic's full-table enumeration concurs).

### Route is terminal — no post-detection fallback

`v17_vb33.wav` (byte 38 → `wValidBitsPerSample`=33, ffmpeg codec `unknown`,
0x84@256 kept): `detected file format type 'act'` → `FAIL … premature EOF`
(exit 2). The terminal error is the **au reader's** on the empty ffmpeg
pipe — never the native wav reader's `number of valid bits exceeds…`,
which the same header produces whenever byte 256 ≠ `0x84`. A detected-`wav`
valid17 file (e.g. `v17_b256_00.wav`) fails with the native error instead.
Each file fails with *its detected handler's* signature — detection picks one
handler once; `open_read` (formats.c:961–964) `goto error`s on `startread`
failure. This closes r62's retained UNKNOWN "act→au→ffmpeg fallback
ordering" against the fallback reading (see r63-boundary for the source-level
disasm/source proof of the same).

### Extension / forced-type behavior

`v17_act.bin` (v17 bytes, `.bin` name) → `act`, exit 0, 15,356 B —
content wins over extension. `v17_wav.bin` (byte256=0x00, `.bin`) → `wav`
(RIFF+WAVE still present) → native reject. `v17_xiff_nowav.bin` (no magic,
`.bin`) → `no handler for file extension 'bin'`. Extension is consulted only
when **no** CHECK matches (formats.c:920–932; `.snd` gets one extra row at
:247–248). `-t` bypasses detection entirely (sibling-verified: `-t act` on a
non-trigger file → bridge; `-t wav` on the trigger file → native reject).

### v16 control member

`v16_b256_84.wav` (= `pair_valid_16.wav`) → `act`, 23,040 B (5,760);
`v16_b256_00.wav` → `wav`, 23,040 B. Same predicate, non-fatal readout —
routing is invisible in decode *count* on v16; the `-V4` detected line /
`--i` `(ffmpeg)` tag is the receipt.

## Established routing chain (composed; each leg evidenced)

```
open_read → readbuf_rewind(≤257 B) → auto_detect_format (first CHECK wins)
  "act" → sox_find_format("act") → ffmpeg pseudo-handler
       ("act" ∈ names[] ffmpeg.c:116; FFMPEG_FORMAT(act) = "G729A speech
        compression" — there is no native act reader on this build)
  → startread_ffmpeg: popen `ffmpeg -loglevel quiet -nostdin -strict -2
       -i FILE -f au -`  (ffmpeg.c:35–44)
  → lsx_au_format_fn()->startread(ft) on the pipe (ffmpeg.c:101–107)
  → au reader parses the child's .snd stream (fatal on empty/truncated pipe:
       "premature EOF")
```

## Eliminated hypotheses

- **byte range / window around 256** — ELIMINATED: 16 solo positions + flank
  controls; only 256 fires (author's exhaustive 23,176-position sweep agrees).
- **multiple trigger values / mask semantics** — ELIMINATED: 255/256 values →
  wav; `0x84` alone → act (author's 512-value sweep on both bases agrees).
- **payload-content sensing** (any `0x84` in the payload) — ELIMINATED:
  payload `0x84` at file 280 after JUNK shift is inert; planted `0x84` at
  file 256 fires. Predicate is on **file** offset 256.
- **`WAVE`@8 participates in the act check** — ELIMINATED: `v17_nowave.wav`
  detects `act` with WAVE destroyed.
- **extension drives routing** — ELIMINATED: `.bin` rename still `act`; ext
  consulted only on total CHECK miss.
- **fallback to native wav after the act/ffmpeg handler fails** — ELIMINATED:
  vb33 + RIFF-no-WAVE + missing-ffmpeg cases die with the au reader's
  `premature EOF`, never wav's named errors; `open_read` has no retry path.
- **"len can be <257 with a late byte"** — ELIMINATED: 256-B file → `wav`.

## Cross-seat consistency (scribe duty — no conflicts found)

| seat | independently established | conflict |
|---|---|---|
| r63-author | identical predicate; exhaustive domains (512 values ×2 bases, 23,176 positions ×2); tracked pair `corpus/live/round-63/pair_route_{84,00}.wav` (SHAs `cf5edecc…`/`cb77db31…`, sole byte-256 diff); 86-cmd ledger 43/43 | none — its listed UNKNOWN ("retry after act-handler failure") is closed by r63-boundary's source trace + my vb33 row |
| r63-critic | same predicate plus the two preemptors phrased as conjuncts; `B_all84_not256`/`B_only256is84` necessity/sufficiency exhibits; RIFX/RF64 native-decode with 0x84@256; `(ffmpeg)`-marker cosmetic caveat | none |
| r63-boundary | source+binary+strace proof of single-dispatch/no-fallback; `premature EOF` = au reader provenance; ffmpeg child exit status never consulted; one-fd leak per act open; s16le detour bit-exact | none |
| r63-scout | disasm pin of the same predicate in `libsox_ng.so.3.0.0`; routing-signature command set; `--magic` unchanged | none |
| r63-reviewer | r62 claims re-executed clean (84/84 byte-identical receipts, both routing directions) | none |
| r63-baseline | frozen 84-cmd before-state replay: 43/41 shape, byte-identical receipts | none |

## Draft: `corpus/knowledge/2026-10-13-sox-act-autodetect-predicate.md`

```markdown
# SoX_ng `act` autodetect predicate — byte-exact routing rule (round 63)

- Source: round-63 seat evidence (`reports/round-63/r63-{author,scout,critic,
  boundary,scribe,reviewer,baseline}.md`); upstream sox_ng-14.8.0.1 source at
  `corpus/live/r63-boundary/src/sox_ng/src/formats.c` + `ffmpeg.c`; binary
  disasm of `/usr/lib/libsox_ng.so.3.0.0` (r63-scout); host disasm of
  `lsx_act_format_fn` (r63-boundary).
- Verified at: 2026-10-13, host `/usr/bin/sox` SoX_ng v14.8.0.1
  (`pacman -Q sox` = 14.8.0.1-1, USING_FFMPEG build), ffmpeg/ffprobe n9.0.1.
- Recheck when: SoX or ffmpeg version/build changes (the act row is
  `#if USING_FFMPEG`; ffmpeg-less builds compile `AUTO_DETECT_SIZE 132` and
  have no act check at all), or when authoring new WAV fixtures whose header
  shape moves payload content across file offset 256.

## The predicate (complete)

SoX reads the first **257 bytes** once (`AUTO_DETECT_SIZE`, sized "for act")
and runs a first-match-wins CHECK table. The act row — the only act rule —
is `CHECK(act, 0,4,"RIFF", 256,1,"\x84")` (formats.c:93), ordered before the
wav rows (:95–97). On this build:

    detected == "act"  ⟺  readable ≥ 257 B
                          ∧ file[0:4] == "RIFF"      (literal, case-sensitive)
                          ∧ file[256] == 0x84        (exact offset, exact value)
                          ∧ no earlier row matched   (gsrt "ring.bin\0"@16;
                                                       hcom "FSSD"@65 ∧ "HCOM"@128)

Measured on the r61 pair family: 1 value of 256 fires; 1 position of 11,588
fires; `WAVE`@8 is **not** a conjunct (RIFF+0x84@256 without WAVE → `act`);
extension is not consulted on a match. File offset, not payload offset:
inserting a JUNK chunk relocates which payload byte is tested.

## What "act" routes to

`act` names the ffmpeg pseudo-handler (ffmpeg.c names[]; description "G729A
speech compression" — the rule exists so real ACT voice-recorder files, which
look like PCM WAV, reach ffmpeg). Its startread popens
`ffmpeg -loglevel quiet -nostdin -strict -2 -i FILE -f au -` and reads the
child's stdout with the **au** handler. One handler is chosen once; a
startread failure is terminal (`open_read` → `goto error`): there is no
re-detection and no fallback to `wav`. ffmpeg's stderr and exit status never
reach SoX — a missing codec, a demux failure, and a missing ffmpeg binary are
all indistinguishable `premature EOF` from the au reader.

## Observable routing signatures

- `sox -V4 <f> -n stat 2>&1 | grep 'detected file format type'` → `act` vs
  `wav` — the authoritative receipt (fires before any decode).
- `sox --i <f>` → `Input File … (ffmpeg)` suffix + **absent** Duration line
  = bridge; no suffix + Duration present = native. Caveat: the `(ffmpeg)`
  suffix is a handler/extension-name mismatch marker — it is suppressed when
  the extension already names the handler (e.g. a `.act` filename), so a
  missing suffix alone is not proof of native routing.
- Decode consequence on the valid17 family: `act` → ffmpeg path → 3,839
  samples (r62 packet-residue law); `wav` → native reader fatal
  `number of valid bits exceeds the number of bits per sample`, exit 2
  (a receiptless `CalledProcessError` inside the project measurer).
- Forced routes for controls: `sox -t wav …` (native, bypasses detection),
  `sox -t act` / `sox -t ffmpeg …` (bridge, byte-256-independent).

## Fixture-authoring rule (fragility, now pinned)

For the 68-byte-header extensible family, file 256 = payload byte 188 =
sample 94 LSB. Any payload/header edit that changes file byte 256 to
≠`0x84` silently reroutes SoX to the fatal native reader; any file shorter
than 257 B can't trigger act; any insertion before `data` moves the tested
payload byte. SHA-pin the byte, or use the r63 tracked pair
`corpus/live/round-63/pair_route_{84,00}.wav` (sole byte-256 diff,
`--probe-ui-route-act-{84,00}-r63`) as the pinned control.

## Bounded unknowns retained

- Other hosts/builds untested; non-ffmpeg SoX_ng builds lack the act row.
- Whether any *other* pre-act CHECK can match exotic RIFF payloads is
  source-enumerated (only gsrt/hcom lack an offset-0 anchor) but only those
  two were exercised.
- stdin/pipe path (257-B pending-buffer replay) unexercised; `--magic`
  off by default and unchanged in effect on these files.
- ffmpeg child exit-code/stdio plumbing (exit status never consulted;
  one fd stays open per act-routed open — boundary's disclosure).
```

## Draft: `corpus/knowledge/2026-10-12-audio-checklist.md` — proposed appended rows

```markdown
| WAV fixture route-stability | `od -A d -t x1 -j 256 -N 1 <f>` + `sox -V4 <f> -n stat` detected line + `sox --i` `(ffmpeg)`/Duration signature | probed 2026-10-13 r63: act predicate = len≥257 ∧ "RIFF"@0 ∧ file[256]==0x84 ∧ no earlier CHECK (gsrt@16, hcom@65/128); byte decides native-vs-bridge route on this family |
| valid-bits malformed header, intended bridge route | pin file[256]=0x84 (or use `pair_route_{84,00}.wav`/`--probe-ui-route-act-*-r63`); confirm `detected file format type 'act'` in -V4 log | probed r63: any other byte → native wav → exit-2 valid-bits fatal, no receipt |
| SoX open failure attribution | compare terminal error string: `premature EOF` = au reader on empty ffmpeg pipe (act route); `number of valid bits exceeds…` / `RIFF header not found` = native wav reader | probed r63: single dispatch, no fallback — error string identifies which handler ran |
```

## Draft: LOG.md round-63 entry text (for parent integration)

```markdown
## Round 63 declared depth claim and wave spec — 2026-10-13
- Clean-before HEAD `3c96a69` (R62 final). One **depth** move: pin or falsify
  the `act` autodetect predicate that r62 disclosed as fixture fragility —
  which byte positions and which values flip `sox --i`/decode routing between
  the `(ffmpeg)` bridge and native `wav` on the r61/r62 pair family; land a
  tracked sweep-matrix control iff a predicate is established.
- Wave1 devin leaf set `reports/round-63/r63-{scout,author,critic,reviewer,
  simplifier,scribe,baseline,boundary}.md` under disjoint scratch scopes,
  single tracked writer (author); then named non-author verifier and Sol
  per-axis adjudication.

## Round 63 wave and author integration — 2026-10-13
- Author `reports/round-63/r63-author.md`: predicate **established exactly** —
  `len ≥ 257 ∧ file[0:4]=="RIFF" ∧ file[256]==0x84 ∧ ¬(earlier CHECK match)`;
  formats.c:93 `CHECK(act,0,4,"RIFF",256,1,"\x84")` first-match before wav.
  Exhaustive: 512-value sweep (1 fires: `0x84`) + 23,176-position sweep
  (1 fires: 256) on both r61 pair members. Tracked additive pair
  `corpus/live/round-63/pair_route_{84,00}.wav` (sole byte-256 diff, SHAs
  `cf5edecc…`/`cb77db31…`) + `--probe-ui-route-act-{84,00}-r63` modes
  recording `sox_detected_format`/`sox_route` in receipts. 86-command ledger
  43 exit0/43 exit1; prior-84 exits position-exact and receipts byte-identical.
- Seat corroboration (all independent, all convergent): boundary (source +
  nm/disasm + strace — single dispatch, zero fallback; `premature EOF` = au
  reader on empty pipe; act resolves to the ffmpeg pseudo-handler, "G729A");
  critic (1,408 probes; preemptors gsrt `ring.bin\0`@16 and hcom
  FSSD@65+HCOM@128; JUNK-shift proves *file* offset 256; RIFX/RF64 decode
  natively with 0x84@256); scout (binary disasm pin at libsox_ng auto_detect
  +0x100 compare; `--i` suffix/Duration signatures); scribe (293-row own
  sweep incl. 256-value and 16-position domains, length floor 257, no-WAVE
  act, no-fallback vb33, gsrt/hcom preemption, JUNK-shift pair);
  baseline (frozen before-state 84-cmd replay byte-identical) and reviewer
  (r62 replay 84/84 identical, both routing directions re-executed).
- Retained UNKNOWNs: non-ffmpeg builds and other hosts; stdin/pipe detection
  path; ffmpeg child-exit plumbing (fd-leak disclosure). r62's "act→au→ffmpeg
  fallback ordering" UNKNOWN is **closed**: open_read detects once, dispatches
  once, dies once — the au reader's `premature EOF` is the terminal error.
```

## Remaining bounded UNKNOWNs (scribe scope)

- Sibling reports not yet landed at my write time: simplifier (pending);
  verifier/adjudicator run later in the wave — the LOG draft marks them.
- Author's `results.tsv` (23,738 rows) is sibling-cited, not scribe-recounted;
  my 293-row sweep covers the same discriminating cells independently.
- `sox --i` on the `.bin` variants behaved as content-first (no ext consulted
  on a match) — the sndr special-case row (formats.c:247–248) untested
  (`.snd`-named files only).

## Out of scope (not performed)

No tracked-file writes (author is the round's tracked writer); no
`measure_audio.py` runs (shared `live/runs/` has no `--runs` redirect and my
seat's claims need only direct `sox` probes); no LOG/knowledge/checklist
edits — all supplied as drafts above for the parent's landing decision; no
git mutation, no other lanes, no network fetch (sox_ng source read is the
sibling-fetched vendored tree).
```

## Receipts index

- `corpus/live/r63-scribe/results.tsv` — 293 rows: variant, size, byte-256
  value, detected type, `sox -n stat` exit, f32 decode bytes, `(ffmpeg)` tag.
- `corpus/live/r63-scribe/variants/` — all 293 mutants (256-value sweep +
  position/length/conjunct/preemptor/JUNK/extension/v16/vb33 controls).
- `corpus/live/r63-scribe/gen_probes.py`, `sweep.sh` — deterministic
  generator + prober (SHA-256 of script/results recorded in-session:
  `781be18a…` / `81c25b35…` / `cfc22c81…` — first 16 hex chars).
