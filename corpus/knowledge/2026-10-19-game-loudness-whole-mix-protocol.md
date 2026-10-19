source: S003 — Sony ASWG-R001 v1.10 (Aug 2013), third-party mirror http://gameaudiopodcast.com/ASWG-R001.pdf — recs. 4, 5, 7, 9, 10, 11 and Note (3) (pdftotext -layout l.87-117, l.132); S004 — Couthier and Schembri, "Mastering a Game with Wwise Part 1" (Audiokinetic blog, 2024-02-15) https://www.audiokinetic.com/en/community/blog/mastering-a-game-with-wwise-part1/ — §Loudness Target, §Measuring Loudness; S002 — EBU R 128 (November 2023) https://tech.ebu.ch/docs/r/r128.pdf — items (h), (i), (m), note 2 (pdftotext -layout l.110-115, l.135, l.180-181); S001 — ITU-R BS.1770-5 (11/2023) https://www.itu.int/dms_pubrec/itu-r/rec/bs/R-REC-BS.1770-5-202311-I!!PDF-E.pdf — Annex 1 l.339-341; S007 (tier C, never sole support) — Sound Armoury "A Study of Video Game Loudness" https://www.soundarmoury.co.uk/blog/loudness-study — results paragraph
verified-at: 2026-10-19 (PDFs and pages fetched 2026-10-19; pdftotext from poppler on host)
recheck: curl -sL http://gameaudiopodcast.com/ASWG-R001.pdf | pdftotext - - 2>/dev/null | tr '\n' ' ' | grep -oE -- '-24 \(±2\) LKFS|-18 \(±2\) LKFS|minimum of 30 minutes|exceed -1 dBTP|measured as a whole|both stereo and surround configurations' | sort | uniq -c; curl -sL https://tech.ebu.ch/docs/r/r128.pdf | pdftotext - - 2>/dev/null | tr '\n' ' ' | grep -oE -- 'Target Level of −23.0 LUFS|tolerance of ±1.0 LU|tolerance of ±0.2 LU|shall not exceed −1 dBTP|shorter than 1 minute' | sort | uniq -c; curl -sL 'https://www.itu.int/dms_pubrec/itu-r/rec/bs/R-REC-BS.1770-5-202311-I!!PDF-E.pdf' | pdftotext - - 2>/dev/null | grep -c 'loudness of pure tones'

# Game loudness targets are whole-mix, long-capture measurements — the primary basis for "no per-fixture LUFS window"

**Claim.** The published game loudness recommendations set targets on the **whole title mix, captured for at least 30 minutes of representative play**, not on individual assets:

| Item | Value | Source + location |
|---|---|---|
| Home console target | −24 (±2) LKFS | S003 rec. 4 (l.87-89) |
| Portable target | −18 (±2) LKFS | S003 rec. 5 (l.91-92) |
| Max true peak | ≤ −1 dBTP, BS.1770-3 + Tech 3341 meter | S003 rec. 7 (l.101-103) |
| What is measured | "measured as a whole, and should not focus on dialogue, sound effects or music specifically" | S003 rec. 9 (l.108-109) |
| How long | "for as long as is practical and for a minimum of 30 minutes", representative cross-section of gameplay | S003 rec. 10 (l.111-113) |
| Channel configs | stereo and surround, consistent between them | S003 rec. 11 (l.115-117) |
| Version note | v1.10 revised the home target "from -23" to −24 LKFS | S003 Note (3) (l.132) |
| Current platform restatement (Feb 2024) | 30-min capture, −24 LUFS ±2 console, −18 ±2 portable, −1 dBTP, **max LRA 20**; measure the device's actual output, not the middleware bus | S004 §Loudness Target, §Measuring Loudness ("It is strongly recommended to measure the actual output of your device.") |
| Broadcast reference | −23.0 LUFS; ±1.0 LU only where the target is not achievable practically; ±0.2 LU for QC measurement error; ≤ −1 dBTP; LRA not recommended under 1 minute | S002 (h) l.110-113, (i) l.114-115, (m) l.135, note 2 l.180-181 |

BS.1770-5 adds that the loudness algorithm "is not, in general, suitable for use to estimate the subjective loudness of pure tones" (S001 Annex 1, l.339-341) — it does not forbid measuring tones, but it withholds the perceptual reading.

## Observed (2026-10-19)

- ASWG strings: `-24 (±2) LKFS` 1, `-18 (±2) LKFS` 1, `minimum of 30 minutes` 1, `exceed -1 dBTP` 1, `measured as a whole` 1, `both stereo and surround configurations` 2 — `recheck:` command 1, 2026-10-19.
- EBU R 128 strings: `Target Level of −23.0 LUFS` 1, `tolerance of ±1.0 LU` 1, `tolerance of ±0.2 LU` 1, `shall not exceed −1 dBTP` 1, `shorter than 1 minute` 1 — `recheck:` command 2, 2026-10-19.
- BS.1770-5 `loudness of pure tones`: 1 — `recheck:` command 3, 2026-10-19.
- Field reality (tier C lead only): the Sound Armoury survey reports "the mean average loudness is -20.6 LUFS" and median −20.7 LUFS, and states the sample "is somewhat skewed towards small indie games" (S007, results and caveat paragraphs, opened 2026-10-19). It is louder than the −24 home target; it supports no admitted claim on its own.

## Inference

- [INFERENCE] The lane's standing choice of "deliberately no acceptance window" for LUFS on fixtures (`corpus/knowledge/2026-10-12-threshold-calibration.md`) now has a primary basis: the recommendations define the target on a 30-minute whole-mix capture, so a per-fixture LUFS window on short synthetic tones would measure something none of S002/S003/S004 target, on signals S001 says the measure does not read perceptually.
- [INFERENCE] Per-asset measurements (this lane's harness, K1/K3 entries) are inputs to a mix, not compliance evidence; compliance needs a captured device-output mix — which this lane does not produce (Adjacent: engine/mix integration).

## Unknown

- Whether PlayStation's current DevNet recommendations changed after Feb 2024 (partner-only; S004 points there).
- Whether the gameaudiopodcast.com mirror is byte-identical to Sony's original distribution (no primary URL found; tiered B for that reason in `corpus/SOURCES.md`).
- Xbox / Nintendo / mobile-store equivalents: not opened this round.

coverage: corpus/README.md coverage map — Core, gap entered round 101: platform loudness targets
