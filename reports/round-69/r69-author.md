# R69 author — EXTENSION-SUFFIX sub-axis swept: declared claim CONFIRMED — named arm splits into 6 verdict groups on identical bytes; `.snd` is the first tracked member where DETECTION (not just decode) forks on transport name; dead-CHECK census landed (5/130 live rows ever first-match)

host: devin (same lane as R61–R68)
Clean-before: canonical lane repo `/home/vgpnk/Projects/shokunin/audio-shokunin` HEAD `7b8d423`;
worktree `/home/vgpnk/Projects/prymeagnt/audio` (`.shokunin/audio` symlinks into the canonical repo).
Toolchain under test: SoX_ng v14.8.0.1 (`/usr/bin/sox` -> `sox_ng`), ffmpeg/ffprobe n9.0.1, python 3.14.7.

## Scoped move — declared claim CONFIRMED, measured exactly

The declared claim: *the named arm splits into ≥3 distinct verdict groups by
extension alone on identical bytes, and the `.snd` member is the first
tracked member where DETECTION (not just decode) forks on transport name.*

ONE 512-B no-match buffer (sha256
`f073e70ad6e9d8c9f06697a9ca61d0a67bf4c351bcbe742c06c4a611d9d5e5d7`)
was committed under five names —
`corpus/live/round-69/extsuffix_nomatch.{wav,bin,txw,f32,snd}` — all five
files byte-identical (`sha256sum` output identical on all five). Each member
ran the same 4-transport matrix through the unchanged r67 `transport_entry`
machinery. Measured verdict groups (identical input bytes on every row):

| member | file | stdin_pipe | redirected_fd | fifo_path |
|---|---|---|---|---|
| `.wav` | `RIFF header not found` (exit 2) | can't determine (2) | can't determine (2) | `RIFF header not found` (2) |
| `.bin` | `no handler for file extension \`bin'` (2) | can't determine (2) | can't determine (2) | `no handler ... \`bin'` (2) |
| `.txw` | `invalid filetype ID in input file header, != LM8953` (2) | can't determine (2) | can't determine (2) | `input must be a file, not a pipe` (2) |
| `.f32` | decode **128 samples** (exit 0) | can't determine (2) | can't determine (2) | decode **128** (0) |
| `.snd` | **detected `sndr`** -> decode **504 samples** (0) | can't determine (2) | can't determine (2) | **detected `sndr`** -> decode **504** (0) |

Named-arm verdict groups by extension alone: **6 distinct**
({wav-reader, bin-no-handler, txw-header-fail, txw-pipe-refusal,
f32-decode, sndr-decode}) — well over the declared ≥3. The `.txw` member
further splits the named arm internally: `file` reaches the txw reader's own
LM8953 header check (`invalid filetype ID`), `fifo_path` hits the reader's
`!seekable` gate (`input must be a file, not a pipe`, tx16w.c:90 class —
same refusal as the r68 member). Detection stays NULL on all four
`.wav/.bin/.txw/.f32` arms and on every anonymous arm of all five members.

**`.snd` is the first tracked member whose DETECTION forks on transport
name**: `sox_detected_format` = `sndr` on {file, fifo_path} vs `None` on
{stdin_pipe, redirected_fd} — the receipt records the fork in the
`sox_detected_format` field itself, not merely in the decode verdict. The
mechanism is the only extension-parameterized CHECK row in the table
(formats.c:247-248: `if (ext && !strcasecmp(ext, "snd")) CHECK(sndr, 7,1,"",
0,2,"\0")`): the row exists only when the input NAME resolves to extension
`snd`. Buffer contract: `b[0]==b[1]==0` (memcmp over `"\0"`'s 2-byte array)
and `b[7]==0` (`""`'s 1-byte NUL array at p2=7). Under `.wav/.bin/.txw/.f32`
names the row is skipped and detection returns NULL on identical bytes;
anonymous `-` arms carry no extension on any member.

Every other CHECK row verified dead on this buffer (ramp bytes
`(i*7+3)&0xFF` with b[256]=0 belt): offset-0 magics all need a nonzero or
mismatched lead (mpeg `00 00 01 BA`, gxf `00*4 01 BC`, au `\0ds.`, sf
`\0\00x`, apm `\x00\x20` — all break at b[1..5]); ring.bin@16, FSSD@65,
HCOM@128, `\x84`@256, wsaud {1,0x63}@11, every `ftyp`@4 variant — all
mismatch. Evaluator cross-check: `first_match(bytes,"snd")` -> row 130
(sndr); `first_match(bytes, ext)` -> None for wav/bin/txw/f32
(`corpus/live/r69-author/check_table.py`).

## Dead-CHECK-row census — receipt coverage bookkeeping

Scanner `corpus/live/r69-author/census_check_rows.py`; table parser
`corpus/live/r69-author/check_table.py` (verified local copy
`corpus/live/r64-reviewer/r64rev-formats.c` == upstream tag 14.8.0.1).
Method: every committed receipt (`git ls-files corpus/live/runs` = 4670
receipts) contributes measurement entries; each entry's `path` input file is
evaluated against the ordered CHECK table in-source (C-literal decode incl.
implicit NUL terminator — `"ring.bin"` compares 9 bytes), with the file's
own filename extension as `ext`. Where a receipt also records
`sox_detected_format`, the recorded type must equal the evaluated
first-match row's type — **0 mismatches** across all recordings.

- **131 CHECK rows parsed**: 130 live + 1 compiled-out (`adx`, L136, inside
  `#if 0`) + 1 ext-gated (`sndr`, L248 — counted among the 130 live).
- Inputs: 126 distinct files, 0 missing; 79,398 measurement entries scanned.
- **rows_hit = 5 of 130 live**:
  `wav` L95 (`RIFF`/`WAVE` — 105 inputs), `act` L93 (`RIFF`+`\x84`@256 — 13),
  `hcom` L90 (`FSSD`@65+`HCOM`@128 — 3), `gsrt` L81 (`ring.bin\0`@16 — 3),
  `txw` L86 (`LM8953`@0 — 1).
- **rows_dead = 125 of 130 live** — every other row including all alternate
  literal variants of hit types (wav RIFX/RF64 rows L96-97, au ×4, sf ×6,
  xa ×3, mp3 ×3, avi ×5, ea ×9, eac3 ×4, adts ×3, flv ×5, mov/mp4/3gp/3g2
  ftyp rows, wsaud ×2, etc.) and the ext-gated `sndr` L248.
- Full JSON: `corpus/live/r69-author/census-r69.json` (row index, source
  line, type, predicate bytes, hit inputs).
- **r69 delta**: the new `.snd` member flips `sndr` L248 from dead to hit
  once its receipts are committed (evaluator confirms the only file under a
  `.snd` name first-matches row 130) — the ext-gated row was unreachable
  coverage debt until this round.

## Tracked changes (additive only)

- `corpus/fixtures/build_artifacts.py` **+46/−1**: `build_ui_extsuffix_r69_probe()`
  writes the five members to `corpus/live/round-69/`; five argparse flags;
  one newest-first dispatch arm (`main()` + builder). Builder output
  byte-identical to the scratch probes (sha256 `f073e70a…` ×5) and to a
  standalone rebuild.
- `corpus/fixtures/measure_audio.py` **+52/−3**: five flags; mutual-exclusion
  sum +5; five forwarding splats to `build_artifacts.py` (newest-first);
  `TRANSPORT_R69_MEMBERS` map; the r69 arm block prepended before the r68
  block recording `transport_extsuffix_<ext>_r69_probe` via the unchanged
  `transport_entry` machinery; `mode`/`suffix` chain heads prepended. No
  prior path, mode string, or helper touched.
- New member files (uncommitted working-tree, parent integrates):
  `corpus/live/round-69/extsuffix_nomatch.{wav,bin,txw,f32,snd}` — 512 B
  each, all sha256 `f073e70ad6e9d8c9f06697a9ca61d0a67bf4c351bcbe742c06c4a611d9d5e5d7`.
  **The differing extensions ARE the member contract** — identical bytes
  fork purely on the name.
- Tracked `corpus/fixtures/__pycache__/*.cpython-314.pyc` differ —
  mechanical `py_compile` regeneration churn, same disclosure as r62-r68;
  parent decides.

## What ran — 119-command ledger (114 prior verbatim + 5 new modes at positions 2-6)

Commands `python3 .shokunin/audio/corpus/fixtures/measure_audio.py <flag>`
from the worktree root; receipts under `corpus/live/runs/<stamp>-<suffix>/`.
Runner `corpus/live/r69-author/run_ledger.py`; TSV `ledger-r69.tsv`;
comparison `compare_receipts.py`. Single contiguous clean run: **49 exit 0 /
70 exit 1**, zero UNPARSED (r68's 49/65 + the 5 new forking rows exit 1).

Prior-114 replay (r69 rows {1} ∪ {7-119} ↔ r68 rows {1-114}): exit sequence
position-identical and **all 114 receipts byte-identical** to the r68
receipt files — `compare_receipts.py`: "114 prior-mode pairs checked, 0
mismatches", exit 0.

New-mode receipts byte-deterministic across 5 runs each (ledger run +
4 standalone reruns, sha256 identical per member):

- `--probe-transport-extsuffix-wav-r69` -> exit 1, sha256 `e0d10839…`
  (`runs/20261014T110644052272Z-transport-extsuffix-wav-r69/measurements.json`);
  fork `file/fifo_path=RIFF header not found` vs `can't determine`.
- `--probe-transport-extsuffix-bin-r69` -> exit 1, sha256 `68d21799…`;
  fork `file/fifo_path=no handler for file extension \`bin'` vs
  `can't determine`.
- `--probe-transport-extsuffix-txw-r69` -> exit 1, sha256 `8bfbfe67…`;
  THREE groups: `file=invalid filetype ID ... != LM8953` /
  `fifo_path=input must be a file, not a pipe` / `-'=can't determine`.
- `--probe-transport-extsuffix-f32-r69` -> exit 1, sha256 `a89d6fcf…`;
  fork `file/fifo_path=decode 128 samples` vs `can't determine`.
- `--probe-transport-extsuffix-snd-r69` -> exit 1, sha256 `80f6d64b…`;
  fork `file/fifo_path=detected sndr, decode 504 samples` vs `can't
  determine` — detection field itself differs across arms.

Empirical sweep ahead of the tracked arm (scratch `run_matrix.py` ->
`matrix-r69.json`, probe generator inline): the tracked matrices reproduce
the probes verbatim. Builder reruns verified byte-identical.

Setup notes: `python3 -m py_compile` on both touched tracked scripts + the
scratch tools -> exit 0; `git diff --check` -> clean.

## Per-axis claim (author evidence only; verdict belongs to verifier + adjudicator)

- **depth**: extension-suffix is now a measured axis INSIDE the named arm —
  the ledger pins five fallback-handler destinations plus the only
  extension-parameterized detection row. Detection itself (not just decode)
  is now provably name-dependent: `sndr` fires iff `ext=="snd"`, on bytes
  that satisfy no other row.
- **coverage**: +5 members over the extension-suffix class → the autodetect
  ledger now covers detection-match forks (r67), post-table no-match name
  forks (r68), extension-suffix handler forks + the first detection-fork
  member (this round). CHECK-row coverage census: 5/130 live rows have ever
  been first-match; 125 dead (incl. 1 compiled-out `adx` row tracked
  separately). Ledger 114->119 commands.
- **calibration**: 114/114 prior receipts byte-identical; all 5 new receipts
  byte-deterministic across 5 runs; builder reproduces members
  byte-identically; census self-check (recorded vs evaluated detection)
  0 mismatches.

## Conditional replay shape (for the non-author verifier)

119 commands = the r68 114 verbatim with
`--probe-transport-extsuffix-{wav,bin,txw,f32,snd}-r69` inserted newest-first
at positions 2-6 (TSV order in `ledger-r69.tsv`). Expected 49 exit 0 /
70 exit 1; prior-114 receipts byte-identical to r68's; new receipts
deterministic (fifo arm uses the pinned 1.0 s writer linger; no member
engages the ffmpeg bridge so no second-open dependency).

## UNKNOWNs / limits

- Verified on this host only: SoX_ng 14.8.0.1 + ffmpeg n9.0.1,
  `USING_FFMPEG`+`HAVE_SNDFILE` build (AUTO_DETECT_SIZE 257); the compiled
  row set is build-gated (`adx` is `#if 0` everywhere; `sds`/`mpc2k` need
  sndfile).
- `.snd`'s sndr decode verdict (504 samples) is a reader-level observation —
  no claim about what the sndr reader semantics are beyond the receipt.
- Census `first_match` treats bytes beyond EOF in the p2 conjunct as
  non-match (the C read is into a 257-B stack buffer; every measured input
  is >=24 B so no evaluated row's result depended on it).
- `use_magic`/`--magic` path unexercised; `|cmd` popen inputs (the only
  `lsx_io_pipe` arm) unprobed — out of the 4-transport envelope.
- No standards-conformance, fidelity, audibility, production, or promotion
  claim — local fixture measurements.

## Blockers

None. Zero subagents dispatched (LEAF per brief). No commit/push/merge
performed; parent integrates.
