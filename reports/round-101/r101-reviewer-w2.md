# Round 101 — wave-2 read-only reviewer findings

- Source: `W2RoundAudio-8.ReviewerW2` (reviewer L2); output transcribed by the continuation L1 on 2026-10-19. This is lane-dispatched review, not non-author adjudication. No worktree writes were made by the reviewer.
- Scope: C2 additions at the time of review; the inherited lane was still based on `defbe128` and had no commit. Findings below were corrected in the continuation.

## Findings

1. **K1 filter/output rate was mislabeled.** `af_loudnorm.c` initializes `frame_type` to `FIRST_FRAME` at n9.0.1 line 808, then `query_formats()` offers 192000 Hz at lines 740 and 751-752 before processing can choose `LINEAR_MODE`. A tap immediately after `loudnorm` observed `rate:192000` for 0.4 s and 3.0 s; the `Audio: pcm_f32le, 48000 Hz` line in the prior recheck described downstream output. The old K1 table incorrectly labeled 48 kHz as the linear-path filter rate and 192 kHz only for dynamic mode.
2. **SOURCES tier histogram was wrong.** The contract census gives 13 original rows, malformed 0, tiers `A=9 B=2 C=2`, status `mined=12 rejected=1`; the gate text had `A=10 B=2 C=1`.
3. **M13 overstated the cause of the citation mismatch.** The ART used a moving `master` URL and wrong line references, but the reviewed n9.0.1 and master cited loci were both 450/463; version drift was not established as the cause. See `reports/round-101/r101-reviewer.md:24,35`.
4. **K3 rounded a per-fixture range into an exact value.** The table includes +3.011 as well as +3.010 LU, so the prose should say `+3.010/+3.011 LU`, not exactly +3.010 on every gated fixture.
5. **K1's grouped table count was inaccurate.** It has 12 table rows covering 15 signal inputs, not 13 rows. Its `recheck:` loop runs eight of those inputs; the reviewer also ran the seven omitted cases (0.41, 1.0, 2.5 and 3.01 s, amp 0.0001, `ui.wav`, `stem_sections.wav` as grouped in the table) and reported that they matched. The K1 table and gate text needed to distinguish table rows from inputs and disclose the extra rechecks.
6. **Gate criteria range was stale.** `corpus/lessons/round-101.md` said Q1–Q15 while `corpus/QUALITY.md` already contained Q16.
7. **S001's teaching dropped a source qualifier.** BS.1770-5 Annex 2 lines 788-789 describes a 3 dB fs/4 under-read for an “unfortunately-phased” continuous tone; that is not a phase-independent limit.
8. **SOURCES `used-by` was incomplete.** Every row cited by the lesson's Gate omitted `corpus/lessons/round-101.md` from `used-by`; path-existence checks alone do not detect omitted citations.

## Checks reported

- All four existing knowledge-entry `recheck:` commands ran with rc 0 and their printed numbers matched: K1's eight loop inputs, the 17 K3 fixtures, K4's version/import checks, and K5's source-string counts. The reviewer separately ran K1's seven table inputs omitted from its command and reported matching values.
- S003, S004, S007, S008–S010 and rejected S011 were re-opened; cited PDF lines and the relevant FFmpeg/Godot source lines were checked.
- K4 and K5 verified; K1, K3, SOURCES, lesson, and README were marked verifies-with-fixes. QUALITY verified. This verdict is pre-correction; the correction records and final census are in `corpus/lessons/round-101.md` and `corpus/SOURCES.md`.

## Continuation recheck — final Q20 closure

- Reviewer follow-up confirmed S011's final `used-by` lists both K4 (`corpus/knowledge/2026-10-19-godot-wav-import-default-qoa.md`) and the lesson. The round lesson records the full change chain `— → lesson → K4, lesson`; all other source-ID `used-by` values match their knowledge-entry and lesson citers.
- K1's immediate filter-rate witness, K1 12-row/15-input accounting, K3 +3.010/+3.011 LU wording, S014/S015 quotes, Q1–Q20 links, and 15-row census were rechecked and passed. The reviewer reported no remaining blockers.
