# SoX_ng extension-suffix dispatch — identical no-match bytes fan out to ≥5 distinct verdict groups by name alone; `.snd` arms the table's only ext-gated CHECK row (first member whose DETECTION forks on transport name); dead-row census of the CHECK table (round 69)

- Source: round-69 seat evidence (`reports/round-69/r69-{scribe,scout,…}.md`; independent sweep `corpus/live/r69-scribe/runs/sweep-body-{a,b}.json`, author-probe replay `runs/sweep-author-probes.json`, census `runs/census.json`); upstream sox_ng-14.8.0.1 `src/formats.c` (lane-verified `corpus/live/r64-reviewer/r64rev-formats.c`), `sounder.c`, `formats_i.c`, `tx16w.c` — citations corroborative; load-bearing claims empirical.
- Verified at: 2026-10-14, host `/usr/bin/sox` SoX_ng v14.8.0.1 (USING_FFMPEG, libsndfile+libmagic linked), ffmpeg/ffprobe n9.0.1.
- Recheck when: SoX version/build changes, the CHECK table or `AUTO_DETECT_SIZE` changes, `lsx_find_file_extension`/`sox_find_format` semantics change, extension→handler map changes, or member names/extensions change.

## The measured law

For a post-table (no-CHECK-match) member, the NAMED-arm verdict is selected by the extension after the last dot of the basename — identical bytes, different suffix, different handler:

    .wav  → wav reader      → "RIFF header not found"
    .bin  → no handler      → "no handler for file extension `bin'"
    .txw  → txw reader      → "… != LM8953" on file / "input must be a file, not a pipe" on fifo
    .f32  → raw f32 reader  → decodes len/4 samples (fifo included — prefetch replayed)
    .snd  → EXT-GATED CHECK → detected `sndr`, then reader verdict by rate@2–3

Five distinct verdict groups on identical bytes — the named axis subdivides by suffix, and `.txw` intersects the reader-gate axis (its member alone forks 3 ways). Anonymous `-` arms never see an extension: `can't determine type of  '-'` on all of them.

## The `.snd` member — detection itself forks on the name

`if (ext && !strcasecmp(ext,"snd")) CHECK(sndr,7,1,"",0,2,"\0")` (formats.c:247-248) is the table's ONLY name-gated row: a body with 0x00 @0,1,7 is detected `sndr` on {file, fifo_path} and undetected on {-, -} — the first tracked member where DETECTION forks across transports (0/165 prior transport_axis entries differed). sounder.c's reader then reads u16-BE type@0–1 (the conjuncts force 0 → `invalid header` unreachable) and u16-BE rate@2–3: rate>0 → 8-bit unsigned mono decode (512-B body → 504 samples, even on fifo via prefetch replay); rate=0 → `invalid rate value`. Pick rate to choose decode-positive vs verdict-pinning member.

## Dead-CHECK-row census (this build: 130 active rows / 77 types; adx is `#if 0`-dead)

Ledger receipts (`corpus/live/runs/*.json`): only `act gsrt hcom txw wav` ever first-match (wav = RIFF row only). All committed evidence adds 11 recorded types (amr-nb, amr-wb, opus, prc, smp, sndr, sndt, sph, voc, vorbis, wve) and 4 simulated-only (au@.snd-magic, flac, mp3@ID3, sox@.SoX). **108/130 rows never first-match**: 57 fully-dead types (all ffmpeg-tail rows incl. ea×9 avi×5 flv×5 sf×7, and aiff-family core rows) plus dead rows inside live types — au{dns.,\0ds.,.sd\0}, sox{XoS.}, mp3{\xFF\xFA,\xFF\xFB}. Census is scope-sensitive: ledger-scope marks wav@RIFX/RF64 dead; committed-seat-scope keeps them live (r63 critic CSV). Never-first-match is coverage bookkeeping, not deadness proof — 28/31 crafted members on "dead"-listed types detect today (r69-critic); `wma` is the only dead-by-construction row (identical GUID to earlier `asf` row, later in first-match order).

## Edges

- `.mp3`-named fifo arms are racy (mp3-mad scan-to-EOF vs writer-linger; observed exit −15 vs empty-message open-fail) — avoid `.mp3` as a tracked transport member without protocol care.
- `lsx_find_file_extension` reads the basename suffix after the LAST dot: a fifo named `tmp.<nonce>.x` yields extension `x`; extensionless basenames embed volatile paths into `error`. Keep member names single-dotted.
- `.au`/`.raw`-named post-table members land au-reader (`can't find Sun/NeXT/DEC identifier`) and raw-reader (`bad input format … rate is zero or negative`) verdicts — further distinct groups off the declared five.
- `.aptx`/`.dts` fifo arms HANG (ffmpeg child's openat blocks on writerless fifo — r69-boundary strace) — avoid as members.
