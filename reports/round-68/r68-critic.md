# R68 critic — declared post-table fork FALSIFIED: fallback forks on the *named* axis (extension dispatch), not the seekable axis; txw/smp pipe-refusal confirmed (reader-level seekable gate); detection flip constructible only via truncated fifo delivery

Seat: **critic**. Host: devin (same lane/toolchain as r61–r67): `sox` = SoX_ng
14.8.0.1 (`/usr/bin/sox -> sox_ng`), ffmpeg/ffprobe n9.0.1, python 3.14.7.
Scratch: `corpus/live/r68-critic/` (probes/, runs/, runner scripts). Zero
tracked mutation: `git status --porcelain` shows only `??` scratch entries;
`git diff HEAD` empty at measurement time.

**Landing status at review time:** the r68 author's tracked diff had NOT
landed (HEAD = `bd5e1fe` r67 report-last; no `corpus/live/r68-author/`, no
`reports/round-68/` author's report, zero tracked modification). Sibling
scratch dirs (baseline/boundary/reviewer/scout/scribe/simplifier) exist.
Per the seat card I attacked the declared claim itself against local
evidence — the falsification below is independent of whatever lands: the
post-table code path cannot produce the claimed partition under ANY member
naming.

## Attack 1 — the declared post-table fork: FALSIFIED (wrong axis)

Declared: *"post-table fallback behavior forks on transport seekability —
a no-match member gets a different verdict/error signature on
`file`/`redirected_fd` vs `stdin_pipe`/`fifo_path`."* Predicted partition:
`{file, redirected_fd}` (seekable) vs `{stdin_pipe, fifo_path}`
(non-seekable).

Measured — four no-match members × all four transports, harness-identical
arms (`run_transports.sh`; verbatim logs `runs/nomatch_*.txt`):

| member | file (.wav name) | stdin_pipe | redirected_fd | fifo_path (.wav name) |
|---|---|---|---|---|
| `nomatch_zeros_600.wav` (600 B `\x00`) | `can't open input file '…': RIFF header not found` (exit 2) | `can't determine type of  '-'` (exit 2) | `can't determine type of  '-'` (exit 2) | `can't open input file '…': RIFF header not found` (exit 2) |
| `nomatch_garbage_600.wav` (600 B patched random) | `RIFF header not found` | `can't determine type of  '-'` | `can't determine type of  '-'` | `RIFF header not found` |
| `nomatch_zeros_256.wav` (below 257 prefetch) | `RIFF header not found` | `can't determine type of  '-'` | `can't determine type of  '-'` | `RIFF header not found` |
| `nomatch_zeros_600.f32` | **decode 150 samples, exit 0** | `can't determine type of  '-'` | `can't determine type of  '-'` | **decode 150 samples, exit 0** |
| `nomatch_zeros_600.bin` | `no handler for file extension 'bin'` | `can't determine type of  '-'` | `can't determine type of  '-'` | `no handler for file extension 'bin'` |
| `nomatch_zeros_600` (no ext) | `can't determine type of file '…'` | `can't determine type of  '-'` | `can't determine type of  '-'` | `can't determine type of file '/tmp/…'` |

**Observed partition: `{file, fifo_path}` vs `{stdin_pipe, redirected_fd}`
— the NAMED axis.** The claimed seekable partition `{file, redirected_fd}`
vs `{stdin_pipe, fifo_path}` is transposed: `redirected_fd` (seekable!)
takes the pipe verdict verbatim, and `fifo_path` (non-seekable!) takes the
file verdict verbatim. No member naming rescues the claim — the fork tracks
*whether the input path carries an extension*, never whether the stream is
seekable.

### Mechanism — falsified twice over

`formats.c` (build-matched copy `/tmp/sox_ng_src/sox_ng/src/formats.c`,
tag-verified by r64-reviewer):

1. **No "fallback classification" pass exists.** Post-table path is pure
   extension dispatch — `auto_detect_format` returns NULL →
   `io_type == lsx_io_pipe`? (`|cmd` pseudo-paths only; none of the four
   transports) → else `lsx_find_file_extension(path)` →
   `sox_find_format(ext)` (formats.c:910-933). There is no second byte-scan;
   no `detected file format` line appears on any post-table arm. `ft->seekable`
   is never consulted on this path.
2. **The seekable retry demonstrably runs and changes nothing.** strace on
   `redirected_fd` (`runs/strace-nomatch-redir.txt`):
   `lseek(0,0,SEEK_CUR)=0` (seekable), `read(0,…,4096)=600` (prefetch),
   `lseek(0,-600,SEEK_CUR)=0` — **the rewind SUCCEEDS** — then
   `can't determine type of  '-'`. The claimed mechanism (seekable re-read
   enabling fallback classification) is refuted on its own terms: the
   capability exists, is exercised, and produces the pipe verdict anyway,
   because `-` has no filename extension. `lsx_find_file_extension("-")`
   → NULL (util.c:130: no `.` → NULL).
3. **"On pipes the ≤257 prefetch bytes are consumed" — the bytes are not
   lost.** `lsx_readbuf_rewind` (formats_i.c:207-216) stashes them into
   `ft->pending_buffer` on non-seekable input and `lsx_readbuf` replays
   them to whichever reader the fallback selects. Executable proof: the
   `.f32` member on `fifo_path` decoded **150/150 samples** (all 600 bytes
   reached the f32 reader through pending replay — a "consumed" prefetch
   would have starved it to ≤85). On `-` the point is moot: the verdict
   dies before any reader runs, identically on seekable and non-seekable
   stdin. fifo strace (`runs/strace-nomatch-fifo.txt`):
   `lseek(3,…)= -1 ESPIPE` twice (is_seekable + rewind attempt both fail),
   member fully read via prefetch+pending.
4. The `-` arm's `type` label is `""` (never set for stdin — formats.c:866,
   set only on the xfopen branch): hence the verbatim signature
   `can't determine type of  '-'` (double space — SoX does not even call
   `-` a "pipe"; `ft->io_type` stays `lsx_io_file`=0 on the `-` branch).
   The only `lsx_io_pipe` route is a `|cmd` pseudo-path — verified live:
   `sox -V6 '|cat probes/nomatch_zeros_600.wav' -n stat` →
   `assuming input pipe '|cat …' has file-type 'sox'` →
   `can't find sox file format identifier` — a THIRD post-table signature
   the 4-transport matrix cannot reach.

## Attack 2 — txw/smp member: CONFIRMED landable; the declared *partition* is real but lives in the reader, not post-table

Own constructions (600 B, signature + zero pad):

| member | file | stdin_pipe | redirected_fd | fifo_path |
|---|---|---|---|---|
| `txw_min.wav` (`LM8953`@0) | detected `txw`, **378 samples, exit 0** | detected `txw`, `input must be a file, not a pipe` exit 2 | detected `txw`, **378 samples, exit 0** | detected `txw`, `input must be a file, not a pipe` exit 2 |
| `smp_min.wav` (`SOUND SAMPLE DATA`@0) | detected `smp`, `header is not version 2.1 ` exit 2 | detected `smp`, pipe refusal exit 2 | detected `smp`, `header is not version 2.1 ` exit 2 | detected `smp`, pipe refusal exit 2 |

- **Not shadowed**: `txw` detected at row 86 — all earlier rows are
  byte-0-disjoint (`voc`/`smp`/`wve`/`amr-*`/`prc`/`sph` need
  {C,S,A,#,\x37,N}@0, none is `L`) or position-disjoint (`gsrt` needs
  `ring.bin`@16 — zero pad). `smp` at row 79 is preceded only by `voc`
  (`C`≠`S`). Live detection lines above confirm.
- **The fork IS the seekable partition** — `{file, redirected_fd}` vs
  `{stdin_pipe, fifo_path}` — but the gate is the reader's own
  `if (!ft->seekable)` at `tx16w.c:90` and `smp.c:228`, reached only after
  a CHECK-row match. The r68 pair lands a genuine seekability fork on a
  *matched* member while the declared claim's seekability fork on
  *post-table* members cannot exist. The honest framing for the round:
  **matched members fork on the seekable axis (reader gates); post-table
  members fork on the named axis (extension dispatch).**
- `txw` is the more informative of the two (positive decode 378 on the
  seekable arms vs smp's reader-fail `header is not version 2.1 ` —
  trailing space verbatim in the signature).

## Attack 3 — detection-invariance: flippable only by truncated delivery (protocol artifact, bounded)

Same tracked members, fifo writer delivering a byte-prefix then closing
(`detection_fork.sh`):

| member | full delivery (file/fifo) | truncated fifo delivery |
|---|---|---|
| `pair_lengate_hcom_132.wav` (132 B) | detected `hcom`, `premature EOF` | **131 B → detected `wav`, decodes 43 samples, exit 0** |
| `pair_lengate_gsrt_25.wav` (25 B) | detected `gsrt` | **24 B → detected `wav`, `fmt chunk not found`** |

Detection forks exactly when the delivered prefix crosses a CHECK len gate
(hcom needs len≥132, gsrt ≥25) — the r67-boundary disclosure confirmed
live. Consequence for the r68 member design:

- A truncated/starved fifo write can flip a member's *detection*, not just
  its verdict — including flipping to a POSITIVE decode (hcom_132→wav arm
  decoded 43, exit 0). If the author's no-match member has ANY prefix that
  matches a CHECK row, a starved fifo arm yields a phantom fork or a bogus
  decode. All-zero members are prefix-safe at every length (no all-zero
  magic row exists — verified over `runs/nomatch_zeros_{256,257,300,600}`);
  my garbage member is not provably prefix-safe (rows gate at len 6-9 on
  bytes I did not patch uniformly). **Member-design guidance: all-zeros,
  or verify every prefix ≥0 B is no-match.**
- Second timing artifact: for a member <257 B on fifo, the prefetch
  `fread` loop (formats_i.c:194-201) blocks until writer close, not just
  until member-end — a dead or slow writer beyond the 1.0 s linger could
  eat the 10 s arm timeout and record `blocked:` — a phantom fifth
  signature. Full-write + pinned linger keeps detection invariant; the
  invariance is a property of *complete delivery*, not of the transport.

## Attack 4 — ledger rows / receipt drift

- `corpus/live/r67-author/ledger-r67.tsv` = **112 rows** (verified, file
  line count). `git diff HEAD` empty; `git status --porcelain` shows zero
  tracked modification — the 112 prior rows + receipts are byte-stable vs
  `bd5e1fe` **because nothing has landed**. The declared "all 112 prior
  ledger rows + receipts byte-stable" is satisfiable only additively; no
  diff exists yet to check (author unlanded at review time).
- Harness-artifact risk for the landing, flagged for verifier adjudication:
  - `transport_error` (measure_audio.py:200-207) returns the message after
    the last `':` — for `-` arms no `':` exists in
    `can't determine type of  '-'`, so `error` becomes the *full* FAIL
    line `sox FAIL formats: can't determine type of  '-'`. Deterministic
    (input is literally `-`), but the signature is line-shaped, not
    message-shaped.
  - **If the member is named without an extension**, the fifo arm's
    `error` embeds the `mkdtemp` path
    (`can't determine type of file '/tmp/transport-r67-XXXX/name'`) —
    non-deterministic receipt bytes AND phantom per-transport verdict
    groups (file arm embeds its own relative path). `stderr_tail` is
    scrubbed; `error` is not. Ext-bearing member names (e.g. `.wav`)
    keep `error` path-independent. A no-ext member needs an `error`-field
    scrub or it is a rejectable receipt-determinism defect.

## Impacted axes

- **depth**: the mechanism attribution is wrong — fork locus is extension
  dispatch (formats.c:911-933), not seekable retry; "prefetch consumed"
  corrected to "pending-buffer replayed" (f32 150/150 decode proof). A
  report that describes the measured `{file,fifo}|{stdin,redir}` partition
  as a *seekability* fork lands false mechanism text.
- **coverage**: the axis-move still lands real coverage — the named-axis
  fork is measured (and the `|cmd` third signature + ext-dispatch taxonomy
  is mapped); the txw member additionally pins the genuine seekable-gated
  pipe-refusal class.
- **calibration**: no-match verdicts are deterministic across reruns
  (3 reruns of `nomatch_zeros_600.wav` ×4 arms, identical), but ext-less
  member naming + unscrubbed `error` yields non-deterministic fifo
  receipts; `blocked:` phantom-fork risk under starved fifo writers.

## Smallest safe correction

1. Re-word the claim to the measured axis: *post-table fallback verdicts
   fork on the named axis — `{file, fifo_path}` resolve the reader by
   filename extension, `{stdin_pipe, redirected_fd}` die `can't determine
   type of  '-'`; seekability is never consulted on the post-table path.*
   The falsified declared wording is itself the useful round output; do
   not soften the record.
2. Frame the pair as the two fork axes: post-table members → named axis;
   txw/smp (matched) members → seekable axis via reader gate
   (`tx16w.c:90`, `smp.c:228`). Prefer `txw` (positive 378-sample decode
   on seekable arms).
3. Member constraints: all-zero or verified all-prefixes-no-match body;
   extension-bearing name for path-independent `error`; if ext-less naming
   is wanted, scrub the input path in `error` (not only `stderr_tail`)
   before landing.
4. Knowledge correction wherever r68 text repeats the declared mechanism:
   prefetch bytes are *replayed* (pending buffer) to the fallback-selected
   reader — they are not "consumed"; `-` yields `can't determine type of
   '-'` on seekable and non-seekable stdin alike (strace: rewind succeeds
   and changes nothing).

## Evidence index

- `corpus/live/r68-critic/probes/` — 9 constructed members (no-match
  zeros 256/257/300/600, ext variants `.wav/.bin/.f32`/none, garbage
  600 B, `txw_min.wav`, `smp_min.wav`).
- `corpus/live/r68-critic/run_transports.sh` — 4-arm runner replicating
  `transport_matrix` (real pipe via `cat`, fd redirect, mkfifo + one-shot
  writer + 1.0 s linger); `detection_fork.sh` — truncated-fifo probe.
- `corpus/live/r68-critic/runs/` — verbatim arm logs
  (`nomatch_zeros_600_{wav,bin,noext,f32}.txt`, `nomatch_garbage.txt`,
  `txw_min.txt`, `smp_min.txt`), straces
  (`strace-nomatch-{file,redir,fifo}.txt`).
- Source: `/tmp/sox_ng_src/sox_ng/src/formats.c:66-270` (CHECK table),
  `:910-933` (fallback dispatch), `formats_i.c:178-219`
  (`lsx_readbuf_rewind` pending-buffer), `util.c:130-143` (extension
  resolver), `tx16w.c:90-93`, `smp.c:228-230` (reader seekable gates),
  `sox_ng.h:594-599` (`lsx_io_type` — pipe = `|cmd` only).

## Limits

Same-host measurements only (SoX_ng 14.8.0.1 + ffmpeg n9.0.1,
USING_FFMPEG build — AUTO_DETECT_SIZE 257). Author diff unlanded at
review time — byte-stability and receipt-shape findings are prospective;
the declared-claim falsification and the measured partitions stand on the
committed toolchain alone. No fidelity/production/standards inference.

## Blockers

None.
