# R69 scribe — EXTENSION-SUFFIX sweep independently re-measured: declared claim VERIFIED — identical no-match bytes split the named arm into 5 distinct verdict groups by extension alone (.wav→RIFF-verdict / .bin→no-handler / .txw→LM8953-verdict+pipe-refusal / .f32→decode / .snd→sndr-detected), and .snd is the FIRST member where DETECTION forks across transports; dead-CHECK-row census: 108/130 active rows never first-match

Seat: **scribe** (leaf, report-only). Host: devin — `/usr/bin/sox` = SoX_ng
v14.8.0.1 (USING_FFMPEG build; libsndfile + libmagic linked, re-verified via
`ldd` + live sds/mpc2k detection probes this session), ffmpeg/ffprobe n9.0.1,
python 3.14.7 — the declared r62–r68 toolchain. Canonical repo
`/home/vgpnk/Projects/shokunin/audio-shokunin`; the brief's line-6 worktree
`~/Projects/prymeagnt/audio` resolves `.shokunin/audio` via symlink into it
(r68 note carried). Scratch `corpus/live/r69-scribe/`; this file is the only
report path written.

Axis-move (verbatim, from the brief): *"sweep the EXTENSION-SUFFIX sub-axis
of the r68 post-table named-axis fork — the same no-match bytes under
different names should route to different handlers (.wav→wav-reader verdict,
.bin→no-handler, .txw→txw-reader pipe-refusal, .f32→f32 decode, .snd→ext-gated
CHECK row — i.e. detection itself forks). Declared falsifiable claim: the
named arm splits into ≥3 distinct verdict groups by extension alone on
identical bytes, and the .snd member is the first tracked member where
DETECTION (not just decode) forks on transport name. Additionally land a
dead-CHECK-row census: which of the ~97 CHECK rows have EVER been first-match
across all committed receipts (coverage bookkeeping). Land additive members +
probe modes on measure_audio.py; all 114 prior ledger rows + receipts
byte-stable."*

## Author-landing state at observation

Verified repeatedly this session (final check **2026-10-14 10:57 UTC**):

- HEAD = `7b8d423` (r68 report-last); `git status --porcelain` shows **no
  modification to any tracked file** — `measure_audio.py` /
  `build_artifacts.py` carry no r69 probe modes yet.
- Author scratch exists **uncommitted**: `corpus/live/r69-author/probes/
  extsuffix_nomatch.{wav,bin,txw,f32,snd}` — all five sha256
  `f073e70a…`, a byte-identical 512-B body with 0x00 @0,1,7 (my CHECK-table
  simulation: no unconditional row matches; the ext-gated `sndr` row
  @formats.c:248 arms iff ext=snd — the member contract is exactly right).
- Sibling scratch present: `r69-{scout,critic,boundary,reviewer}` dirs
  (untracked). Scout's `matrix-r69.tsv` and `check-row-census.tsv` converge
  with my numbers (details + one scope divergence below).

**Consequence:** the author-mode re-run is *absent, not failed* (r68-scribe
phrasing). I ran the sweep on (a) my own members through the landed
`transport_matrix` machinery imported verbatim from the tracked
`corpus/fixtures/measure_audio.py`, and (b) the author's own five probes
through the same machinery — member-level evidence for exactly the partition
the declared claim predicts.

## Independent measurement (own scratch, landed arm machinery)

Runner `corpus/live/r69-scribe/run_sweep.py` (imports the tracked module —
no copy, no edit). Two own bodies, each replicated under 8 names
(`wav bin txw f32 snd au mp3 noext`), sha256-verified identical across names:

- **body A** = 300 B all-zeros (sha `d13d4a8b…`) — bytes 0,1,7 = 0x00 arms
  `sndr` iff ext=snd; no unconditional CHECK row satisfiable.
- **body B** = 512 B, bytes 0–7 zero + deterministic nonzero tail
  (sha `2dc87072…`) — robustness/decorrelation check.

Every arm's `sox_detected_format` recorded; results
`runs/sweep-body-{a,b}.json`, per-arm JSON legs `runs/logs/`, author-probe
run `runs/sweep-author-probes.json`.

### Named-arm verdicts on identical bytes — the declared partition holds, 5 groups ≥ 3

| member (identical bytes) | `file` arm | `fifo_path` arm |
|---|---|---|
| `.wav` | `RIFF header not found`, exit 2 | `RIFF header not found`, exit 2 |
| `.bin` | `no handler for file extension 'bin'`, exit 2 | same |
| `.txw` | `invalid filetype ID in input file header, != LM8953`, exit 2 | **`input must be a file, not a pipe`**, exit 2 |
| `.f32` | **decode 75 samples, exit 0** (body B: 128) | **decode 75/128, exit 0** |
| `.snd` | detected **`sndr`** → `invalid rate value`, exit 2 | detected **`sndr`** → `invalid rate value`, exit 2 |
| `.au` (extra) | `can't find Sun/NeXT/DEC identifier`, exit 2 | same |
| `.mp3` (extra) | `can't open input file '…':` **empty reason**, exit 2 | run-1 same; **run-2 exit −15 (SIGTERM, no verdict)** |
| no-ext (extra) | `can't determine type of file '<path>'`, exit 2 | `can't determine type of file '<tmp path>'` — volatile path in `error` |

Anonymous arms (`stdin_pipe`, `redirected_fd`) are `can't determine type of
 '-'`, exit 2, on **every** member — extensionless names reach no post-table
handler at all (r68's named-axis finding, reconfirmed).

- The five declared names produce **five distinct verdict signatures on the
  named arms from byte-identical input** — the claim's "≥3 distinct verdict
  groups" is satisfied at strength five, on both bodies, and again on the
  author's own five probes (same classes; their `.snd` reads
  `detected 'sndr'` → **decode 504, exit 0** because their u16-BE rate field
  @2–3 is 0x1118 = 4376 Hz > 0; mine is 0 → `invalid rate value`. Same
  detection fork, different reader-ladder landing — see below).
- The `.txw` member alone splits into **3 groups** —
  `{file}` vs `{fifo_path}` vs `{pipe,redir}` — because ext `txw` dispatches
  the *one* handler that carries the lane's only tracked seekable gate
  (tx16w.c `!seekable` → pipe refusal before any byte read). The
  extension-suffix axis and the reader-gate axis intersect on this member.
- Verbatim legs preserved in `runs/logs/`; the fifo `.f32` decode (exit 0)
  re-confirms prefetch replay on non-seekable named transports.

### The `.snd` member — DETECTION itself forks; first such member on record

On both bodies and the author's probe: `sox_detected_format` =
**`{file: sndr, fifo_path: sndr}` vs `{stdin_pipe: null,
redirected_fd: null}`** — the ext-gated row `CHECK(sndr,7,1,"",0,2,"\0")`
(formats.c:247-248) is armed only when `ext=="snd"`, so the *detection* —
not just the decode verdict — partitions on the name before a single
reader byte matters.

"First tracked member" check: I scanned **all 165 committed
`transport_axis` receipt entries** (`git ls-files '*.json'`, r67+r68
members) — **zero** have differing `sox_detected_format` across arms.
Detection-invariance held for every tracked member until now; the `.snd`
member is measurably the first counterexample at receipt level.

Mechanism, source-corroborative (`/tmp/sox_ng_src/sox_ng/src/sounder.c`,
local tree == tag 14.8.0.1): the `sndr` reader reads u16-BE `type`@0–1 and
u16-BE `rate`@2–3 then skips 4 — the CHECK row's `0x00@0,1` conjuncts
*guarantee* `type==0`, so detected members can never hit the reader's
`invalid header` rung; the only post-detection variable is `rate > 0`
(formats_i.c:73 else `invalid rate value`). Author's body passes
(0x1118=4376); a body with rate=0 lands `invalid rate value`. Byte 7's
0x00 guard sits inside the skipped field — pure detection predicate, no
reader meaning. **Member-design corollary:** a decode-positive `.snd`
member needs `rate > 0` @2–3; a verdict-pinning member uses rate=0.

### Determinism check

Second full sweep run vs first: **all five declared members byte-stable**
on both bodies (groups, detected values, exits, samples, error strings
identical). Two *extra* controls moved: `.mp3` fifo arm is **racy**
(run-1 `can't open …:` empty message like file; run-2 `exit -15` SIGTERM
mid-banner, no verdict — the mp3-mad scan-to-EOF vs the fifo writer; a
`.mp3` member would need protocol care), and no-ext keeps the r68-documented
tmp-path-in-`error` hazard (scout's fifo additionally showed `no handler
for file extension 'nm_zeros_noext'` because *their* fifo basename
`tmp.<nonce>.nm_zeros_noext` contains dots — `lsx_find_file_extension`
takes the basename suffix after the last dot, so fifo-name construction
itself is part of the verdict. Consistent with the mechanism on both
harnesses.)

## Dead-CHECK-row census (independent, row-level)

Script `corpus/live/r69-scribe/census_checkrows.py`; result
`runs/census.json`. Table parsed from the lane-verified
`corpus/live/r64-reviewer/r64rev-formats.c` (sha `82c3058e…` == upstream tag
14.8.0.1, C-string escapes decoded, conjuncts evaluated in source order,
`AUTO_DETECT_SIZE`=257, the `sndr` ext gate applied). **Build flags verified
empirically**: sds → `detected 'sds'`, \x01\x04 → `detected 'mpc2k'` →
`HAVE_SNDFILE`/`HAVE_SF_FORMAT_MPC2K` are on, and USING_FFMPEG is on, so the
compiled table is **131 source rows − 1 `#if 0` adx row = 130 active rows /
77 distinct types** (the brief's "~97" is loose; my measured count is
authoritative here).

Three tiers of "ever first-match across committed receipts":

| tier | scope | types first-match | rows first-match |
|---|---|---|---|
| **ledger** | 4,670 committed `corpus/live/runs/*.json` | **5**: `act, gsrt, hcom, txw, wav` | 5 (wav = RIFF row @95 only) |
| **recorded** | all tracked files (receipts, CSVs, tsv, stderr, logs, reports) | **16**: above + `amr-nb, amr-wb, opus, prc, smp, sndr, sndt, sph, voc, vorbis, wve` | 18 (wav rows 95+96+97 — r63-critic `sweep_results.csv` records `wav` detection on RIFX *and* RF64 members) |
| **simulated** | 5,091 tracked member files' bytes through the parsed table | **20**: above + `au, flac, mp3, sox` (members exist, detection never recorded) | **22** (+au@106 `.snd`-magic, flac@110, mp3@125 `ID3`, sox@123 `.SoX`) |

**Dead rows under the broadest reading: 108/130 (57 fully-dead types +
9 dead rows inside 3 live types).** Partially-dead live types: `au` rows
107–109 (`dns.`, `\0ds.`, `.sd\0` — every committed au member uses `.snd`
magic), `sox` row 124 (`XoS.`), `mp3` rows 127–128 (`\xFF\xFA`, `\xFF\xFB`
— only ID3 carriers committed). Fully dead include all of `sf`×7, `ea`×9,
`avi`×5, `flv`×5, `eac3`×4, `adts`×3, `xa`×3, `mp4`×4, `mov`×4, plus every
single-row type never exercised (`aiff aifc 8svx maud nsp sds mpc2k dff
dsf wsd 3g2 3gp aa aac ac3 ape apm argo_asf asf ast avr caf wv paf pcm
mp2 f4v gxf ism kvag m4a m4v mkv mlp mpeg mpegts mxf_opatom nut oga ra
rm smjpeg spx tta vag wma wsaud wtv`). Full row list: `runs/census.json`
`dead_rows`.

**Cross-seat scope note:** scout's committed-scope census
(`check-row-census.tsv`) counts only the 114-row ledger and marks wav
rows 96/97 dead ("no committed member has those bytes") — true at ledger
scope, false at all-committed scope: r63-critic `sweep_results.csv`
records `wav` detection on `D_rifx_*`/`D_rf64_*` members (row-level
evidence above). My three-tier table keeps both readings explicit.

## Cross-seat convergence

| seat | evidence | result |
|---|---|---|
| **this scribe** | 16 members × 4 arms on landed machinery + author probes ×4 arms + 130-row census | named arm = 5 verdict groups; `.snd` detection fork; .txw 3-group self-fork; 108 dead rows |
| r69-scout (untracked scratch, read) | 13-member × 4-arm matrix + row census | identical per-name verdicts; adds `.raw`→`bad input format … rate is zero`, `.xyz`→no-handler, `.sndr`→`invalid header`, `.au`→`can't find Sun/NeXT/DEC identifier`; fifo-basename nuance on no-ext |
| r69-author (untracked probes) | 5 byte-identical `extsuffix_nomatch.*` | same 5 classes; `.snd` decode-positive (rate=4376) vs my verdict-pinning (rate=0) — complementary member designs |

- **Verdict on the declared claim: VERIFIED on both clauses** — the named
  arm splits into ≥3 (measured: 5) distinct verdict groups by extension
  alone on identical bytes, and the `.snd` member is the first member on
  record whose *detection* forks across transports ({file,fifo}=`sndr`
  vs {-}=NULL).
- Sharpenings for the record: the `.txw` member itself is a 3-way fork
  (extension selects the seekable-gated reader); the `.snd` CHECK
  conjuncts pin `type==0` so detection pre-clears the reader's header
  rung — decode-vs-verdict on `.snd` is decided solely by u16-BE rate @2–3;
  `.mp3`-named members are fifo-racy; `sndr` is the only ext-gated row in
  the entire table.

## Draft knowledge entry — for `corpus/knowledge/2026-10-14-sox-extension-suffix.md` (fenced; parent lands it)

```markdown
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

Ledger receipts (`corpus/live/runs/*.json`): only `act gsrt hcom txw wav` ever first-match (wav = RIFF row only). All committed evidence adds 11 recorded types (amr-nb, amr-wb, opus, prc, smp, sndr, sndt, sph, voc, vorbis, wve) and 4 simulated-only (au@.snd-magic, flac, mp3@ID3, sox@.SoX). **108/130 rows never first-match**: 57 fully-dead types (all ffmpeg-tail rows incl. ea×9 avi×5 flv×5 sf×7, and aiff-family core rows) plus dead rows inside live types — au{dns.,\0ds.,.sd\0}, sox{XoS.}, mp3{\xFF\xFA,\xFF\xFB}. Census is scope-sensitive: ledger-scope marks wav@RIFX/RF64 dead; committed-seat-scope keeps them live (r63 critic CSV).

## Edges

- `.mp3`-named fifo arms are racy (mp3-mad scan-to-EOF vs writer-linger; observed exit −15 vs empty-message open-fail) — avoid `.mp3` as a tracked transport member without protocol care.
- `lsx_find_file_extension` reads the basename suffix after the LAST dot: a fifo named `tmp.<nonce>.x` yields extension `x`; extensionless basenames embed volatile paths into `error`. Keep member names single-dotted.
- `.au`/`.raw`-named post-table members land au-reader (`can't find Sun/NeXT/DEC identifier`) and raw-reader (`bad input format … rate is zero or negative`) verdicts — further distinct groups off the declared five.
```

## LOG.md round-entry draft (fenced; parent edits)

```markdown
## Round 69 — devin host — depth: extension-suffix dispatch + .snd detection fork + CHECK-row census

- Declared (author dispatch brief): sweep the EXTENSION-SUFFIX sub-axis of the
  r68 named-axis fork — identical no-match bytes under .wav/.bin/.txw/.f32/.snd
  should route to different handlers; falsifiably, the named arm splits into
  ≥3 distinct verdict groups by extension alone and the .snd member is the
  first tracked member where DETECTION (not just decode) forks on transport
  name; plus a dead-CHECK-row census over committed receipts; 114 prior
  ledger rows byte-stable.
- Wave `shokunin-train-20261014-w8`: 8-seat devin leaf set
  `reports/round-69/r69-{scout,author,critic,reviewer,simplifier,scribe,baseline,boundary}.md`.
- Measured outcome — declared claim **VERIFIED** (scribe: 2 own bodies ×
  8 names × 4 arms + author-probe replay on landed machinery; scout:
  independent 13-member matrix): identical bytes yield 5 distinct named-arm
  verdicts (RIFF-verdict / no-handler / LM8953-verdict+pipe-refusal / f32
  decode / sndr-detected), and `.snd` is the first member on record whose
  sox_detected_format differs across transports ({file,fifo}=sndr vs {-}=NULL;
  0/165 prior transport_axis entries differed). `.txw` member self-forks 3
  ways (ext selects the seekable-gated reader); `.snd` decode positivity is
  u16-BE rate@2–3 (author 4376→504 samples; rate 0→invalid rate value).
- Census (scribe, row-level, build flags probed live): 130 active CHECK rows
  / 77 types; committed ledger receipts ever first-match only {act, gsrt,
  hcom, txw, wav@RIFF}; all committed evidence: 16 recorded + 4
  simulated-only types; **108/130 rows never first-match** (57 dead types;
  au 107–109, sox 124, mp3 127–128 dead inside live types).
- Edges: `.mp3` fifo arm racy (SIGTERM observed); fifo basename with dots
  changes the extension `lsx_find_file_extension` returns; `sndr` remains
  the table's only ext-gated row.
- Per-axis verdict (Sol `r69-adjudicator.md`): PENDING.
```

## Touched surfaces / out-of-scope

- **Wrote:** `reports/round-69/r69-scribe.md` (this file);
  `corpus/live/r69-scribe/` — `run_sweep.py`, `census_checkrows.py`,
  `probes/` (16 members), `runs/sweep-body-{a,b}.json`,
  `runs/sweep-author-probes.json`, `runs/census.json`,
  `runs/logs/*.stderr` (64 per-arm legs).
- **Read-only cross-references:** `corpus/live/r69-author/probes/*` (ran
  the author's uncommitted members through the landed machinery — read,
  never modified), `corpus/live/r69-scout/runs/*.tsv`, sibling reports.
- **Zero tracked mutation:** `git status --porcelain` shows only `??`
  entries from my scratch; `git diff HEAD` empty. No commits/pushes/merges;
  no dispatches; `git archive` n/a (baseline owns it). No writes outside my
  scratch + this report.

## Bounded UNKNOWNs / limits

- The author's r69 tracked landing (members + probe modes + receipts) was
  absent at every observation (final check 10:57 UTC); author-mode receipt
  comparison remains for the verifier once the diff lands. My measurement
  covers the claim on three independent member sets.
- Census "ever first-match" is scope-sensitive; I report ledger/recorded/
  simulated tiers explicitly rather than one number. Simulated rows credit
  a row whose committed member bytes would fire it first — whether that
  member was ever executed is a separate (recorded) tier.
- Single host/toolchain; verdict-level evidence; source cites
  corroborative. No conformance/fidelity/production inference.

## Stop

Report complete. Leaf seat: nothing further.
