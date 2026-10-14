# R69 boundary (mutation-tester) — extension sweep on identical bytes splits into ≥12 file-transport verdict classes; `.snd` is the ONLY ext-gated CHECK row (gate = `\0`@0 ∧ `\0`@7, case-insensitive, last-dot-only, preempted by unconditioned rows); fifo-starve × extension partitions into fail-fast / decode-anything / content-gated / **bridge-hang** classes; `.txw` fifo → pipe-refusal at every byte count

Seat: **mutation-tester** — edge-probe the landed r69 extension-suffix surface;
no tracked mutation. Host: `sox` = SoX_ng **14.8.0.1** (`/usr/bin/sox`,
USING_FFMPEG + libmagic), ffmpeg **n9.0.1**, python **3.14.7**, kernel
`7.2.3-arch1-3` — same toolchain as r63–r68. Source reading against the
build-matched copy at `/tmp/sox_ng_src/sox_ng/src/`. Scratch:
`corpus/live/r69-boundary/` (`run_ext_matrix.py`, `run_fifo_starve.py`;
TSVs `runs/ext_matrix.tsv` 40 rows, `runs/landed_edge_matrix.tsv` 26 rows,
`runs/fifo_starve.tsv` 118 rows; per-leg verbatim `-V6` logs `runs/logs/`;
strace `runs/strace-aptx-fifo.txt`; `author_probe_snapshot/` pre-landing copy).
`git status --porcelain` audit: **zero tracked writes by this seat** — only
the `?? corpus/live/r69-boundary/` scratch entry + my report; `git diff HEAD`
shows only the author's `M` fixtures.

## Author landing state (verified at probe time)

Author diff **landed during this seat's window** (~07:59–08:03 -03):
`build_artifacts.py` +47 (`build_ui_extsuffix_r69_probe`), `measure_audio.py`
+52 (`TRANSPORT_R69_MEMBERS`, five `--probe-transport-extsuffix-*-r69` flags —
all parse under `--help`), tracked members `corpus/live/round-69/
extsuffix_nomatch.{wav,bin,txw,f32,snd}` — **all five byte-identical** (md5
`31b8e3c87ada059e726be98666a594c2`, 512 B, ramp `(i*7+3)&0xff` with
`b[0]=b[1]=b[7]=0`, `b[256]=0`). Identical to the author's pre-landing probe
snapshot (md5-verified). I do **not** run their probe modes — they write
receipts into `corpus/live/runs/` outside my write scope; all probing below
is raw `sox -V6` on the member bytes (same mechanism the modes wrap).
My 16-name × 4-transport matrix on their pre-landing buffer and the
author's own `r69-author/matrix-r69.json` agree **verbatim on every cell**
(RIFF / no-handler-bin / invalid-filetype+pipe-refusal / decode-128 /
sndr-detected-504 / can't-determine).

## E1 — edge names on identical bytes: 12 file-transport verdict classes

`runs/landed_edge_matrix.tsv` — the landed 512-B buffer renamed under 26
edge names × {file, stdin_pipe, redirected_fd, fifo_path}. On the `file`
transport alone, name alone selects among **12 distinct verdict classes**:

| name(s) | verdict class |
|---|---|
| `.wav`, `.WAV`, `.Wav`, `.wAv`, `e..wav`, `.wav` (dotfile) | `RIFF header not found` |
| `.bin` | `no handler for file extension 'bin'` |
| `.BIN` | `no handler for file extension 'BIN'` — echoes input case, still unhandled |
| `.tar.gz`, `.snd.gz` | `no handler for file extension 'gz'` — **last-dot only**; the `.tar`/`.snd` components are invisible |
| `e.` (trailing dot) | `no handler for file extension ''` — **empty-string extension**: a third class distinct from both no-handler-named and can't-determine |
| `e` (no dot) | `can't determine type of file '<full path>'` — embeds the path verbatim; on the fifo arm it embeds the **mktemp nonce path** (`/tmp/r69-ext-*/…` — nondeterministic string, r68 simplifier hazard reconfirmed live) |
| `.txw`, `.TXW` | `invalid filetype ID in input file header, != LM8953` |
| `.f32`, `.F32` | decode 128 samples, exit 0 |
| `.snd`, `.SND`, `.Snd`, `.tar.snd`, `.snd` (dotfile) | **detected `sndr` → decode 504** (see E2) |
| `.au` | `can't find Sun/NeXT/DEC identifier` |
| `.sndt` | `can't find SoundTool identifier` |
| `.ogg` | `input is not an Ogg Vorbis audio stream` |
| `.mp3` | FAIL with **empty message** (`WARN mp3-mad: MAD lost sync` → `can't open input file '…': ` — verbatim empty tail) |
| `.aptx` | decode **0 samples, exit 0** (ffmpeg headerless family reads garbage) |
| `.dts` | `premature EOF` (ffmpeg probe fails on the bytes) |

`lsx_find_file_extension` (util.c:130-143) = `strrchr(basename,'.')+1`:
last-component-only, trailing-dot → `""` (non-NULL — so `e.` skips the
`can't determine` branch at formats.c:925 and dies inside
`sox_find_format("")`), dotfile `.wav` → extension `wav`. `sox_find_format`
(formats.c:1823) matches `strcasecmp` — **all case variants dispatch
identically**, and the sndr gate is `!strcasecmp` too. A `.wav`-named
directory does not leak into the extension (`/tmp/dir.wav/fifo` →
`can't determine type of file` — basename only).

Anonymous `-` transports are still `can't determine type of  '-'` on every
name — the r68 named-axis partition `{file,fifo}|{-,-}` holds for dispatch;
verdicts split *inside* the named pair only where the selected handler is
seek-gated or name-reopening (E3/E4).

## E2 — name-gated CHECK rows: `.snd` is the ONLY one — and it has a duality

Source census (`formats.c`): `ext` is used **exactly once** in
`auto_detect_format` — line 247, `if (ext && !strcasecmp(ext,"snd"))
CHECK(sndr,7,1,"", 0,2,"\0")`. No other CHECK row reads the name. The gate
predicate is `len ≥ 2 ∧ data[0]=='\0' ∧ data[7]=='\0'` — where `data[7]` at
`len<8` is **uninitialized stack** (r68 E5 reconfirmed: 46/46 fifo legs at
len∈{2..7} → `sndr` across both buffer families + `.SND`, deterministic on
this build, formally nondeterministic).

Measured consequences:

1. **`.snd` duality.** `snd` is a name of the **au** handler (au.c:221
   `{"au","snd"}`), not the sndr one. Same name, two byte-selected fates:
   gate passes (b[0]=b[7]=0) → `detected 'sndr'` → sounder reader;
   gate fails (b[7]≠0, or any byte[0]≠0) → post-table → **au reader**
   (`can't find Sun/NeXT/DEC identifier`). The author's buffer is exactly
   one conjunct from the non-forking fate — if `b[7]` had been nonzero the
   `.snd` member would decode nothing and DETECTION would not fork. The
   claim's load-bearing member is fragile by construction; it measures the
   gate, not `.snd` semantics generally.
2. **Table order preempts the gate.** A `.snd`-named file with real au
   magic (`.snd` + valid header) → `detected 'au'` → decode 16
   (`probes/au_real.snd`) — the unconditioned au row (line 106) wins; the
   gated row is last in the table. Name gating only *adds* a row.
3. **`.snd`-inside-a-name is not `.snd`.** `e.tar.snd` arms the gate
   (detected `sndr`); `e.snd.gz` does not (ext `gz` → no-handler).
4. **Extension-only formats are a separate name-dependence class.** 99 of
   177 handler names have **no CHECK row at all** (raw encodings `f32 u8
   s16 …`, `aptx dfpwm dts rso sbc spdif` per source comments, aliases like
   `3gp2/aif/mpg`). For these the name is not a gate — it is the *only*
   route in; detection never fires.
5. **Receipt-side cross-check for the dead-row census:** `sox_detected_format`
   values across every committed receipt in `corpus/live/runs/` =
   `{act:471, gsrt:267, hcom:266, wav:158, txw:54}` — exactly **5 of 78**
   CHECK types have ever appeared as a detected format in a committed
   receipt. (`sox_detected_format` only records transport-arm legs, so this
   is a lower bound on first-match coverage — the author's receipt census
   is authoritative.)

## E3 — extension sweep × fifo-starved delivery

`runs/fifo_starve.tsv` (118 legs: writer pushes N bytes, closes
immediately, no linger) + landed-buffer re-runs:

| ext | starved-fifo behavior vs N |
|---|---|
| `.bin` | `no handler for file extension 'bin'` at **every** N — post-table never reads bytes |
| `.txw` | `input must be a file, not a pipe` at **every** N incl. 0 — `!seekable` gate (tx16w.c:90) precedes any read |
| `.f32` | decode ⌊N/4⌋ samples, exit 0 at **every** N incl. 0 — raw reader has no floor |
| `.wav` | `file is truncated` → `RIFF header not found` at a **byte-content-dependent** boundary: `lsx_reads` (formats_i.c:404) is a byte-at-a-time read that **breaks on NUL or `\n`**, so the gate is `min(first NUL/\n offset, 4)`. Landed buffer (b[0]=0) flips at n=0\|1; ASCII-lead buffer at n=3\|4. Empty regular `empty.wav` → `file is truncated` |
| `.au` | `premature EOF` → `can't find Sun/NeXT/DEC identifier` at a **fixed** n=3\|4 — `lsx_readchars` is a fixed 4-byte read, no NUL early-out. The two "4-byte magic" readers have different short-input semantics |
| `.snd` (gate bytes) | n∈{0,1}: post-table → au `premature EOF`; n∈{2..7}: **`detected 'sndr'` → `premature EOF`** (the uninit-window — 46/46 deterministic here); n≥8: `sndr` → decode N−8 |
| `.SND` | identical at n=2 and n=8 — gate is case-insensitive |
| `.mp3` | empty FAIL tail at every N |
| `.ogg` | `input is not an Ogg Vorbis audio stream` at every N |
| `.aptx`, `.dts` | **`blocked:` — HANGS the whole leg** (10 s timeout) at n=0 AND n=512 |

**The ffmpeg-bridge hang cell** is the sharpest starve interaction:
`startread_ffmpeg` (ffmpeg.c:33-107) execs `ffmpeg -i <path> -f au -` and
parses the child's stdout with the **au** reader. On a starved fifo the
child's `openat(O_RDONLY)` on the path **blocks forever** — the writer has
already exited and a fifo with no writer refuses new readers. strace
(`runs/strace-aptx-fifo.txt:457`) shows the child's openat left unfinished.
With the 1.0 s writer-linger the open succeeds and the child sees an
**emptied pipe** (sox's prefetch already consumed the bytes) →
`can't find Sun/NeXT/DEC identifier` — which is why `.aptx`/`.dts` give a
3-group split {file decode/fail}|{fifo au-identifier}|{- can't-determine}
under the linger protocol. Under starvation the same names turn the leg
into a hang cell: **extension choice decides whether a dead fifo fails
instantly, decodes empty, or hangs the probe outright** — an operational
asymmetry no native extension produces (`never-close .bin` also blocks,
but inside the *prefetch* — E4 note — not a child open).

Stall cells (writer holds open without EOF): `bin` stall k=0 → verdict
lands at hold end (t=1.00/3.00 s tracking the hold); `wav` k=257 → verdict
immediately (prefetch already satisfied); `snd` k=2 h≥1 → prefetch waits
for the remainder, then `sndr` decode-504 — **the len<8 uninit window is
reachable only via early-EOF, never via stall** (stdio fread fills the
257-B window or waits). Never-close writer on `.bin` → `blocked:` —
the post-table path cannot run before `lsx_readbuf_rewind` returns.

## E4 — `.txw`-named no-match member on fifo: pipe-refusal, not the named group

On the landed member `extsuffix_nomatch.txw` (and `.TXW`, and under
starvation at every N ∈ {0..512}): fifo → `input must be a file, not a
pipe`, file → `invalid filetype ID in input file header, != LM8953`,
anon arms → `can't determine type of  '-'` — a **3-group** partition.
The fifo arm is still inside the named group *for dispatch* (extension
resolved → txw handler selected), but the handler's `!seekable` refusal
(tx16w.c:90) overrides the group's verdict **before a single byte is
read** — refusal precedes even the LM8953 check the file arm reports.
So: **pipe-refusal**; the {file,fifo} named group splits exactly when the
extension-selected handler carries its own seekable gate (txw, smp per
r68) or re-opens by name (the ffmpeg bridge: aptx/dts family).

## Declared-claim verdict: CONFIRMED — with edges the declared set can't see

- *"named arm splits into ≥3 distinct verdict groups by extension alone on
  identical bytes"* — **confirmed ≥5 on the author's own five names**
  (RIFF / no-handler / invalid-filetype / decode-128 / sndr-detection on
  `file` alone; 3-group `txw` across transports), and **≥12 classes** on
  my 26-name edge sweep on identical bytes.
- *"`.snd` is the first tracked member where DETECTION forks on transport
  name"* — **confirmed on the landed member**: `det='sndr'` on
  {file,fifo_path} vs `det=None` on {stdin_pipe,redirected_fd}, same bytes.
  Structural note: it is also the *only* member that can — `sndr` is the
  single ext-gated CHECK row in the table (E2).

## Divergences / disclosures

1. The `.wav` `truncated|not-found` boundary is **byte-content-dependent**,
   not a length constant — `lsx_reads` stops at NUL/`\n`; landed buffer
   flips at n=0|1, ASCII-lead buffer at n=3|4. Any receipt that records
   `.wav` short-fifo verdicts inherits the member's first-NUL offset.
2. The `.snd` member's detection-fork is **one byte-conjunct fragile**:
   b[7]≠0 → no detection, au-reader verdict. Buffer-contract, not semantics.
3. Author probe-mode runs absent by scope (they write into `runs/`); my
   matrices use raw `sox -V6` on the identical member bytes, and my
   16-name matrix reproduces the author's `matrix-r69.json` cell-verbatim.
4. `e` (no-dot) fifo arms embed the mktemp-nonce path in the error string —
   a non-deterministic receipt string if a no-extension name is ever
   ledgered on fifo (r68 simplifier hazard, re-measured).
5. ffmpeg-bridge extensions on a dead fifo are a **hang cell** — the r67
   writer-liveness finding now mapped to the extension axis: the linger
   protocol is load-bearing for any ffmpeg-family name on fifo.
6. Prior-114 receipt byte-stability is the author/verifier audit surface;
   this seat made no tracked writes (`??`-only scratch).

## UNKNOWNs / limits

- Single host/toolchain; the len<8 `sndr` cell is formally
  nondeterministic (uninit stack read) though 46/46 reps here → `sndr`.
- `sox_find_format`'s `;`-clause mime path and `--magic` remain off-ledger
  (r68), unmeasured this round.
- The `empty FAIL tail` on `.mp3` and decode-0 on `.aptx` are this build's
  native-mad/ffmpeg behaviors; not generalized.
- `.wav` short-input semantics verified via `lsx_reads` source +
  2 buffer families; other NUL/\n placements not swept.

## Confidence

**High** on the extension matrix (40 + 26 member-name rows × 4 transports,
per-leg verbatim `-V6` logs, determinism ×3 spot-checks byte-identical),
**high** on the sndr-gate census (single `ext` use at formats.c:247 +
behavioral reps incl. case/dot-component/order-preemption cells), **high**
on the fifo-starve partition incl. the bridge-hang (118 legs + stall/
never-close cells + unfinished-`openat` strace), **high** on the `.txw`
fifo answer. **Medium-high** on the uninit-byte cell (deterministic here,
formally stack-dependent).

## Receipts

- `corpus/live/r69-boundary/run_ext_matrix.py` — 26-name × 4-transport
  extension matrix on member bytes.
- `corpus/live/r69-boundary/run_fifo_starve.py` — N-byte starve / stall /
  never-close fifo harness.
- `runs/ext_matrix.tsv` (40 rows, pre-landing own buffers),
  `runs/landed_edge_matrix.tsv` (26 rows, landed member),
  `runs/fifo_starve.tsv` (118 rows), `runs/logs/*.log` verbatim tails,
  `runs/strace-aptx-fifo.txt` (bridge second-open evidence),
  `author_probe_snapshot/` (md5-pinned pre-landing member).
- Source citations (build-matched `/tmp/sox_ng_src/sox_ng/src/`):
  `formats.c:66-271` (CHECK table; `ext` used once at 247-248),
  `formats.c:910-933` (post-table dispatch), `formats.c:1809-1833`
  (`sox_find_format` strcasecmp), `util.c:130-143` (`strrchr` extension),
  `formats_i.c:404` (`lsx_reads` NUL/\n break), `au.c:138-141,221`
  (`lsx_readchars` 4-B floor; `{"au","snd"}`), `tx16w.c:90` (`!seekable`
  refusal), `sounder.c:45`, `ffmpeg.c:33-107,110-142` (bridge exec + au
  stdout parse + name list).
