# SoX_ng preemptor ordering on RIFF files — gsrt ≺ hcom ≺ act ≺ wav (round 65)

- Source: round-65 seat evidence (`reports/round-65/r65-{author,scout,critic,
  scribe,reviewer,baseline}.md`; scribe's independent sweep
  `corpus/live/r65-scribe/results.tsv` + `variants/` + `logs/`); upstream
  sox_ng-14.8.0.1 `src/formats.c` (codeberg tag; local verified copy
  `corpus/live/r64-reviewer/r64rev-formats.c`, sha256 `82c3058e…`) —
  source citations corroborative; all load-bearing claims empirical.
- Verified at: 2026-10-14, host `/usr/bin/sox` SoX_ng v14.8.0.1
  (USING_FFMPEG build), ffmpeg/ffprobe n9.0.1. Commit: 1b0d276.
- Recheck when: SoX or ffmpeg version/build changes (the `act` row is
  `#if USING_FFMPEG`; ffmpeg-less builds compile `AUTO_DETECT_SIZE 132` and
  drop the act row entirely — ordering gsrt≺hcom≺wav survives but act
  disappears), when the CHECK table gains a pre-act row without an
  offset-0 anchor, or when fixture families change shape.

## Measured ordering result

`auto_detect_format` reads ≤257 B once (`AUTO_DETECT_SIZE 257 /* for act */
`, formats.c:61) and returns the FIRST matching CHECK row. On a RIFF file
(`RIFF`@0) the reachable pre-act rows are exactly two — every other row in
front of `act` anchors a non-RIFF literal at offset 0. Measured total order
(four independent fixture families, ~100 collision variants total):

    gsrt  ≺  hcom  ≺  act  ≺  wav
    :81      :90      :93     :95    (formats.c line order = match order)

- gsrt row: `CHECK(gsrt, 0,0,"", 16,9,"ring.bin")` — predicate
  `len ≥ 25 ∧ file[16:25] == "ring.bin\0"` (the C literal's terminating NUL
  at offset 24 is compared; a non-NUL 9th byte falls through to `act`).
- hcom row: `CHECK(hcom, 65,4,"FSSD", 128,4,"HCOM")` — predicate
  `len ≥ 132 ∧ file[65:69]=="FSSD" ∧ file[128:132]=="HCOM"` (both conjuncts
  required; either alone → `act`).
- act row: `CHECK(act, 0,4,"RIFF", 256,1,"\x84")` — the r63 predicate
  `len ≥ 257 ∧ RIFF@0 ∧ file[256]==0x84`, unchanged.
- A file satisfying all three signatures detects **gsrt** (earliest row).
  Preemptors ignore byte 256 entirely (`*_00` members still detect
  gsrt/hcom — the preemptor even beats `wav` when `0x84` is absent).
- Length gates are exact: gsrt fires at len=25 not 24; hcom at 132 not 131;
  act at 257 not 256.

## Downstream route per detection (single dispatch, no fallback)

| detected | handler | observed on collision bodies |
|---|---|---|
| `gsrt` | native gsrt reader | RIFF body → `premature EOF` exit 2 (reader treats bytes 0-3 as a BE `file_size` feeding a read/checksum loop — `RIFF`≈1.38 G > file); 25-B carrier → `invalid/missing file name in header`; zeroed 312-B carrier → **accepts**: `--i` `(gsrt)` 1ch/8kHz/14-bit/μ-law, 0 samples, exit 0 |
| `hcom` | native hcom reader | near-zero body → `bad sampling rate divisor`; r61-family body → `bad compression type` — both are hcom-startread guards (which trips is content-dependent); a genuinely valid-hcom body decodes (critic: 9 samples @22050 Hz) |
| `act` | ffmpeg pseudo-handler | `popen ffmpeg -f au` → au reader; `--i` `(ffmpeg)` + no Duration line |
| `wav` | native wav reader | normal r63 baseline |

`sox <f> -n stat` exits **2** on open failure; `sox --i <f>` exits **1** on
the same failure — the `--i` asymmetry is measured, not a typo.

## Fall-through behavior (preemptor detects but reader rejects)

Terminal — no re-detection, no second handler, no fallback to `act`/`wav`
(r63 single-dispatch chain confirmed on the collision family):
`v_hcom84.wav` (a fully valid WAV whose hcom signatures sit inside a JUNK
payload) detects `hcom` → `bad sampling rate divisor` exit 2, while the
same bytes decode cleanly under forced `-t wav` (exit 0). The preempted
verdict is *the detected reader's verdict on a malformed body*, not an
ordering property — error strings are content-dependent (`premature EOF`
alone is emitted by ≥3 readers on this family and does NOT attribute the
route; only the `-V4/-V6` `detected file format type` line does).

Two structural corollaries, both measured:

- **hcom collision is ffmpeg-fatal too.** ffmpeg's prober independently
  scores `hcom` 100 > `wav` 99 on the same FSSD@65+HCOM@128 bytes, so a
  hcom-shaped file fails even under the counterfactual `-t act` bridge
  (`premature EOF` — ffmpeg child emits nothing). The only measured
  decode route is forced `-t wav` / `-f wav`.
- **gsrt collision is never WAV-valid.** Offsets 16-19 are structurally the
  first subchunk's size field in every RIFF file; `ring.bin\0` there sets
  it to `0x676e6972` (~1.73 GB), so `-t wav` fails `fmt chunk not found` /
  `file encoding 0x622e`, ffprobe `no 'fmt '…`/`no 'data' tag found`. The
  hcom windows (65-68, 128-131) are unconstrained — they can hide inside
  any chunk payload.

## Relation to the r63 act predicate and the r64 step map

- The r63 predicate stands verbatim; r65 completes its quantifier: the
  "no earlier row matched" conjunct is now a measured total order, not an
  enumerated-candidate claim. The full detect rule on this build:
  `detected == first matching row of (voc,smp,wve,gsrt,amr-wb,prc,sph,
  amr-nb,txw,sndt,vorbis,opus,hcom,act,wav…)` where on a `RIFF`@0 file only
  {gsrt, hcom, act, wav, avi-family} can match, and the measured winner
  order is gsrt < hcom < act < wav < (post-act rows — act still beats
  `avi`/`ftyp` collisions).
- The r64 valid-bits→codec step map is unchanged and *unreached* under a
  preemptor collision: it applies only after `act` wins the table. A
  collided vb-family file never reaches ffmpeg — e.g. tracked
  `pair_preempt_hcom.wav` (a vb17 file) is claimed by hcom before the
  vb17-vs-16 question can arise.
- Fixture-authoring rule extends: a payload signature at 16-24 or
  (65-68,128-131) reroutes detection regardless of byte 256. The tracked
  collision family `corpus/live/round-65/pair_preempt_{act,gsrt,hcom,both}.wav`
  (probe modes `--probe-ui-preempt-*-r65`) pins it; `pair_preempt_act.wav`
  is byte-identical to `round-63/pair_route_84.wav` (sha256 `cf5edecc…`).

## Bounded UNKNOWNs retained

- Reader acceptance semantics of gsrt/hcom beyond the exercised bodies
  (valid-hcom decode is one critic sample; gsrt accepted only a degenerate
  zero carrier). Real-world well-formed gsrt/hcom corpus untested.
- stdin/pipe detection on colliders (one critic probe only); `--magic`
  path (off by default) untested this round.
- Non-ffmpeg SoX_ng builds: ordering derived on a USING_FFMPEG build; on a
  132-byte-window build the act row vanishes (hcom becomes the deepest
  RIFF-reachable preemptor).
- Other hosts/versions; plugin-registered formats could add CHECK rows
  (none installed here).
- Exact hcom reader guard order between `bad sampling rate divisor` and
  `bad compression type` is content-keyed; not exhaustively mapped.

## Falsifiable recheck conditions

1. `sox -V4 corpus/live/round-65/pair_preempt_both.wav -n stat 2>&1 | grep
   detected` must print `gsrt` — any `hcom`/`act`/`wav` reading falsifies
   the ordering (member sha256 `a37adc7c…`; commit slot 1b0d276).
2. `sox -V4 pair_preempt_{gsrt,hcom}.wav -n stat` must detect `gsrt`/`hcom`
   and exit 2 on this fixture body; `pair_preempt_act.wav` must detect
   `act` and read 3,839 samples.
3. Rebuild determinism: `build_ui_preempt_r65_probe()` must reproduce the
   four members byte-identically (`cmp` vs committed blobs).
4. Any SoX/ffmpeg version change → rerun this file's probes
   (`corpus/live/r65-scribe/sweep.sh` regenerates the detection matrix);
   CHECK-table additions or a resized `AUTO_DETECT_SIZE` invalidate the
   ordering claim at the first differing row.
