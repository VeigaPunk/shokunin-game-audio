# R68 boundary (revenger) — post-table fallback forks on the *named* axis (extension dispatch), not seekability; pipe prefetch is buffered not consumed; `|cmd`/`--magic`/`.snd`-name are three extra verdict arms the declared set can't see

Seat: **revenger** — reconstruct host behavior from executable evidence; no tracked
mutation. Host: `sox` = SoX_ng **14.8.0.1** (`/usr/bin/sox -> sox_ng`, USING_FFMPEG +
libmagic linked: `ldd /usr/lib/libsox_ng.so.3` → `libmagic.so.1`), ffmpeg/ffprobe
**n9.0.1**, python **3.14.7**, kernel `7.2.3-arch1-3` — identical toolchain to
r63–r67. No `lsp` device answers this repo (same as r64–r67; source reading is
against the build-matched copy at `/tmp/sox_ng_src/sox_ng/src/`). Scratch:
`corpus/live/r68-boundary/` (harness `run_probes.py` 19-transport matrix,
`len_gates.py` length/EOF/`-t` matrix; logs `runs/logs/`; TSVs
`runs/edge_matrix.tsv`, `runs/len_eof_forced.tsv`, `runs/act_snd_eof.tsv`,
`runs/sndr_uninit.tsv`; strace `runs/strace-{pipe,file}-nomatch.txt`).
`git status --porcelain` audit: **zero tracked writes by this seat** — only `??`
scratch entries; `git diff HEAD` empty at measurement time.

## Author landing state (verified at probe cutoff)

At **2026-10-14 ~07:05 -03**: HEAD = `bd5e1fe` (r67 report-last); `grep -c r68
corpus/fixtures/measure_audio.py` = **0**; `git status --porcelain` shows **no
`M` on any tracked file**; no `corpus/live/r68-author/`, no
`reports/round-68/r68-author.md`. Sibling r68 scratch dirs and the baseline +
critic + reviewer reports exist. Polled `git status`/`grep r68` repeatedly over
~20 min (06:45→07:05) — the declared "additive members + transport-probe modes"
had not landed. **The author-arm audit (receipt determinism, member naming, arm
verdicts on their modes) is therefore absent, not failed.** The mechanism probes
below are member-independent: the post-table path depends only on (a) no CHECK
row matching, (b) `ft->io_type`, (c) the input *path's* extension, (d) `--magic` —
never on which bytes formed the member.

## Reconstructed contract — what "post-table fallback" actually is

`formats.c:910-933` (`open_read`) + `formats_i.c:178-218` (`lsx_readbuf_rewind`),
all four claims verified by strace/verdicts below:

1. **The ≤257 prefetch is never consumed.** `lsx_readbuf_rewind`: seekable →
   `rewind(fp)`; non-seekable → copies into `ft->pending_buffer`/`pending_count`,
   replayed by the next `lsx_readbuf`. strace proof
   (`runs/strace-pipe-nomatch.txt:150-154`): pipe stdin
   `lseek(0,0,SEEK_CUR)=-1 ESPIPE` (the `is_seekable` probe at formats.c:511),
   `read(0,"NOMATCH68…",4096)=429` — one stdio-buffered read — then two
   `lseek(0,-172,SEEK_CUR)=-1 ESPIPE` (glibc trying to un-read the 172 B
   over-fetch; fails harmlessly). Compare `runs/strace-file-nomatch.txt:52-56`:
   `lseek(3,0,SEEK_CUR)=0`, `read(3,…,4096)=429`, `lseek(3,429,SEEK_SET)`,
   `lseek(3,4,SEEK_SET)` — the ext-fallback wav handler seeking to re-parse.
   The declared "on pipes the prefetch bytes are consumed" is **false**: they
   are buffered and replayed; that is why a non-seekable `.wav`-named fifo gets
   the identical wav-reader verdict as the file (E1).
2. **`lsx_io_pipe` means `|cmd`, not fifo/stdin.** `xfopen` (formats.c:834-837)
   sets `lsx_io_pipe` only when `identifier[0] == '|'` (popen). A fifo opened by
   path is `lsx_io_file`; `-` (stdin) never gets an io_type at all (calloc 0 =
   `lsx_io_file`, and the `type` string for the error stays `""` — hence the
   verbatim double space in `can't determine type of  '-'`).
3. **The fallback is pure name dispatch.** On NULL detection:
   `io_type==lsx_io_pipe` → `filetype="sox"` ("assuming input pipe `X' has
   file-type `sox'"); else `lsx_find_file_extension(basename(path))` →
   `sox_find_format(ext, sox_true)` → handler or `can't determine type` /
   `no handler for file extension`. **`ft->seekable` is never consulted on this
   path.** Any seekability dependence lives inside whichever handler the
   extension selects (txw/smp/8svx refuse non-seekable — E2).
4. **`--magic` sits between table and fallback on every transport.** This build
   links libmagic; `sox_globals.use_magic` set only by the `--magic` flag
   (formats.c:251-268, excludes `application/octet-stream`, `*/unknown`,
   `text/plain`). It reads the pending buffer, so it arms on pipes too (E1).

## Declared-claim verdict: FALSIFIED as stated — the fork is real but on the name axis

Declared: *"a no-match member gets a different verdict/error signature on
`file`/`redirected_fd` vs `stdin_pipe`/`fifo_path`"* (predicted partition =
seekable axis). Measured on `nomatch_txt.wav` (429 B, zero CHECK-row hits —
verified: no `detected` line on any arm):

| transport | verdict (verbatim tail) |
|---|---|
| file `.wav` | `can't open input file '…': RIFF header not found` (exit 2) |
| **fifo_path `.wav`** | **identical `RIFF header not found`** (non-seekable, same verdict) |
| **redirected_fd `sox - < f`** | **`can't determine type of  '-'`** (seekable, *pipe* verdict) |
| stdin_pipe `sox -` | `can't determine type of  '-'` |

Observed partition: **`{file, fifo_path}` vs `{stdin_pipe, redirected_fd}`** —
exactly transposed from the claim. `redirected_fd` is seekable yet takes the
pipe verdict verbatim; `fifo_path` is non-seekable yet takes the file verdict
verbatim. The fork tracks *whether the input path carries a known extension*,
never whether the stream is seekable. No member naming rescues the stated
claim: `-` always has no extension (`can't determine`), a fifo in the author's
own `Path(tmp)/path.name` arm always inherits the member's extension (file
verdict). This corroborates and extends the r68 critic's 4-transport
falsification — the same transposed partition holds across the full 19-arm
extended set below.

## E1 — no-match members across the extended transport set

`run_probes.py`; full TSV `runs/edge_matrix.tsv` (229 rows); per-leg verbatim
`-V4` in `runs/logs/<member>.<transport>.log`. Normalized verdict groups
(member-independent; shown for the `.wav` and `.bin` no-match members):

| arm | path form | no-match verdict class |
|---|---|---|
| file / tmpfs (`*.wav`) | named, seekable | `RIFF header not found` (wav handler) |
| **fifo named `*.wav`** | named, **non-seekable** | **same `RIFF header not found`** |
| `*.mp3` name | any named | `WARN mp3-mad: MAD lost sync` → empty FAIL tail |
| `*.txw` / `*.smp` name | any named | `invalid filetype ID` / `header does not begin with magic word …` |
| `*.bin` name | any named | `no handler for file extension 'bin'` |
| `*.f32` name | any named | **decodes** — 107 samples, exit 0 (float32 raw reads anything; corroborates critic's `.f32` finding on fifo too) |
| `*.snd` name + `\0\0` bytes | any named | **`detected 'sndr'` inside the table** → decode 294, exit 0 (see E5) |
| stdin_pipe / redir / sockstdin (`-`) | nameless | `can't determine type of  '-'` |
| devstdin_{reg,pipe} (`/dev/stdin`) | named, dotless | `can't determine type of file '/dev/stdin'` |
| procfd_*, memfd, owronlyfd, opathfd (`/proc/self/fd/N`) | named, dotless | `can't determine type of file '/proc/self/fd/N'` |
| file with no extension | named, dotless | `can't determine type of file '<path>'` |
| fifo named `.fifo_probe` (ext `fifo_probe`) | named, non-seekable | `no handler for file extension 'fifo_probe'` |
| **`|cmd` popen** | `io_type=lsx_io_pipe` | `assuming input pipe '…' has file-type 'sox'` → `can't find sox file format identifier` |
| **`--magic` + ELF bytes** | any transport | `detected 'application/x-executable; charset=binary'` → `no handler for detected file type 'application/x-executable; charset=binary'` |
| sockpath (unix socket as path) | transport open | `can't open input file '…': No such device or address` (ENXIO — detection never runs; carried from r67) |

Five distinct post-table verdict *classes* exist — extension-handler verdict,
`can't determine type of <io-str> 'X'`, `no handler for file extension`,
assume-sox (`|cmd` only), libmagic-detected-no-handler — and **none of them is
selected by seekability**. The only cell where seekability changes a post-table
verdict is inside a seekable-gated *handler* reached via extension (`.txw`/
`.smp` names: file → `invalid filetype ID`; same-named fifo → `input must be a
file, not a pipe`, verified on `nm.txw`/`nm.smp` fifos — a 3-group split
{file}/{fifo}/{`-`-transports} the declared arm can produce only with a
pipe-refusing extension).

## E2 — the txw/smp member at its own length/byte gates

`len_gates.py`; TSV `runs/len_eof_forced.tsv`; source `tx16w.c:77-181`,
`smp.c:217-280`. Detection gate and reader gate are **different lengths**:

**txw** (`LM8953` CHECK needs len ≥ 6; reader header = 32 B):

| bytes | file | pipe |
|---|---|---|
| 0–5 | no detect → `.bin` → `no handler for file extension` | no detect → `can't determine type of '-'` |
| 6–31 | `txw` → `file is truncated` | `txw` → `input must be a file, not a pipe` |
| 32–33+ | `txw` → decode (32 B → 0 samples, exit 0; 300 B → 178) | `txw` → refusal |

(`num_samp_bytes -= 32` at tx16w.c:99 underflows harmlessly for <32 — the
subsequent 32-B header read hits EOF first → `file is truncated`.)

**smp** (`SOUND SAMPLE DATA` CHECK needs len ≥ 17; reader = 112-B header + 4-B
count + trailer):

| bytes | file | pipe |
|---|---|---|
| 0–16 | post-table (`no handler`/`can't determine`) | `can't determine type of '-'` |
| 17–111 | `smp` → `unexpected EOF in header` | `smp` → refusal |
| 112–115 | `smp` → `unable to read sample size` | refusal |
| 116+ (short trailer) | `smp` → `unexpected EOF in trailer` | refusal |

`NoOfSamps=0x0FFFFFF0` on file → still `unexpected EOF in trailer` — `lseek`
past EOF succeeds on a regular file, so `unable to seek to trailer` (smp.c:277)
is not reachable via short files here; it needs a bounded seek target. On every
non-seekable transport ≥17 B the pipe refusal precedes all of this.

## E3 — early-EOF on fifo at the fallback boundary

Writer writes N then closes immediately (`fifo_eof_leg`, name variants
`.fifo_eof`/`.fifo_eof.wav`/`.fifo_z.snd`):

- **No-match member**: verdict is length-invariant **0–300 B** — same
  extension-dispatch verdict at every N (`.fifo_eof.wav` → `RIFF header not
  found` even at N=0; `.fifo_eof` → `no handler for file extension
  'fifo_eof'`). Post-table has no byte gate — it never read the stream.
- **Detected member**: early EOF flips the route at the member's *detection*
  length gate, not the reader's: `g_txw_hcom` N<6 → post-table (`no handler for
  file extension 'fifo_eof'`); N≥6 → `txw` → pipe refusal. `p_smp_intact`
  N<17 → post-table; N≥17 → `smp` → refusal. So truncation **can** route a
  detected member *into* the fallback path — the boundary is the CHECK row's
  own `len ≥` clause.
- **act member** (`pair_dec_act.wav`, `RIFF`+non-act-byte-256 until ≥257):
  N=0 `file is truncated`; 4–8 `header not found`; 12–255 `wav` detected →
  `fmt chunk not found`/`file is truncated`; **255,256 → `wav` partial decode
  105/106 samples, exit 0 + WARN `premature EOF`** (the r67 act→wav detection
  flip reproduces); **N≥257 → detected `act` → HANG cell**: the leg emitted the
  `can't find Sun/NeXT/DEC identifier` tail-steal FAIL line, then the process
  still had to be killed at the 15 s timeout (r67's fifo+act hang family —
  writer liveness at the bridge's second open decides the tail).
- `.snd`-named fifo on `\0\0` bytes: N=2–7 → `detected sndr` → `premature EOF`;
  N≥8 → table row fails (`data[7]≠0`) → ext-fallback → same sndr reader →
  `can't find Sun/NeXT/DEC identifier`. See E5's uninit-byte note.

## E4 — `-t` forcing × no-match fallback

`runs/len_eof_forced.tsv` tail (4 members × 6 forced types × {`-`, file}):

- **`-t` bypasses the table AND the fallback entirely** — `open_read` takes the
  `filetype` branch at formats.c:871-877, never reaching lines 910-933. No
  interaction with the no-match path exists to measure: forcing is orthogonal.
- What forcing *doesn't* bypass: handler transport gates. `-t txw`/`-t smp` on
  `-` → `input must be a file, not a pipe` on every member (reader-side
  refusal, same as r67). `-t wav` on no-match bytes → `RIFF header not found`
  on pipe and file alike (stream intact — no 257-B consumption under `-t`
  because detection never runs). `-t sox` on `-` → `can't find sox file format
  identifier` — the same verdict the `|cmd` assume-sox arm produces, i.e. the
  popen branch is `-t sox` in disguise. `-t raw` → `sample rate is zero or
  negative` (sox_checkformat). `-t txw` on `g_txw_hcom` file → 178 samples,
  matching detection-routed verdict.

## E5 — three edges the declared arm set cannot see

1. **`.snd` name arms a CHECK row inside the table.** formats.c:247-248 gates
   `CHECK(sndr, 7,1,"", 0,2,"\0")` on `!strcasecmp(ext,"snd")`. My
   `nomatch_zeros.snd` (`\0\0` + `\x11` pad, data[7]=0) → `detected 'sndr'` →
   **decode 294 samples, exit 0** on file/tmpfs/`--magic` — and on **popen**:
   `|cat nomatch_zeros.snd` extracted ext `snd` from the *command string* and
   detected `sndr` too. Same bytes on `-`/devstdin/procfd → `can't determine
   type`. Detection itself forks on the input *name*, upstream of post-table.
2. **That CHECK reads outside the fetched window at len<8.** The row compares
   `data[7]` while requiring only `len ≥ 2`; at len 2–7 `data[7]` is
   uninitialized stack. Measured 16/16 legs → `sndr` (stack reads zero on this
   build) — deterministic in practice, **formally nondeterministic** (inference:
   no memset precedes the memcmp; flagged, not claimed as a crash).
3. **`--magic` produces a third verdict signature.** `nomatch_elf.bin`
   (ELF64 header, zero CHECK-row hits): file + fifo + stdin-pipe alike →
   `detected file format type 'application/x-executable; charset=binary'` →
   `no handler for detected file type '…'` (formats.c:915-918). The MIME string
   is emitted on the `detected` line, so a `--magic` receipt records a
   "detection" that isn't in the table — a verdict class the four declared arms
   (none pass `--magic`) never produce.

## Divergences / disclosures

1. Declared claim falsified as stated (transposed partition; name axis, not
   seekable) — plus the mechanism claim "prefetch consumed on pipes" falsified
   (pending-buffer replay, strace-verified).
2. Author-arm audit absent by non-landing (see header); my matrix runs the raw
   `sox` CLI, not their receipt modes — verdict classes are member-independent.
3. Determinism spot-checks: fifo_wav and popen legs ×3 → byte-identical FAIL
   lines (md5 `1835f6a3…`, `422c4935…`).
4. The `type` string in `can't determine type of  '-'` is empty (double space)
   — a verbatim signature detail, not a typo.
5. The `>257` stdio over-read (172 B stranded in the glibc buffer on pipes) is
   invisible to the verdict — post-table on `-` never reaches a reader — but
   would matter if a `|cmd`/handler arm ever read `-` past the prefetch.

## UNKNOWNs / limits

- Single host/toolchain; `--magic` is off-ledger (not an author arm) but is a
  real flag on this build.
- smp `unable to seek to trailer` branch unmeasured (seek-past-EOF legal here).
- The fifo+act ≥257 leg is a *hang cell* (15 s timeout kill), consistent with
  r67's writer-liveness finding, not a post-table verdict.
- Whether the eventual author member is `.wav`/`.bin`/`.f32`-named changes only
  which handler runs — not the axis attribution; all namings falsify the
  declared partition the same way (fifo inherits the member name in the r67
  arm shape).

## Confidence

**High** on the measured matrix (229 matrix legs + 155 gate/EOF/forced legs +
56 sndr reps, per-leg verbatim `-V4` logs retained, strace for the pending
replay and the wav-handler seek), **high** on the falsification (transposed
partition reproduced across 19 transports and 9 no-match members, including
two independent sibling confirmations). **Medium** on the uninit-stack
mechanism attribution for the `.snd` len<8 cell (behavior measured; the absent
memset is source-inference).

## Receipts

- `corpus/live/r68-boundary/run_probes.py` — 19-transport post-table matrix.
- `corpus/live/r68-boundary/len_gates.py` — txw/smp length gates, fifo
  early-EOF, `-t` forcing.
- `runs/edge_matrix.tsv` — 229 rows; `runs/len_eof_forced.tsv` — 155 rows;
  `runs/act_snd_eof.tsv` — 16 rows; `runs/sndr_uninit.tsv` — 56 rows.
- `runs/logs/*.log` — per-leg verbatim `-V4` output.
- `runs/strace-pipe-nomatch.txt` / `runs/strace-file-nomatch.txt` — pending-
  buffer vs rewind evidence (lines 150-154 / 52-56 cited).
- Source citations (build-matched `/tmp/sox_ng_src/sox_ng/src/`):
  `formats.c:66-271` (CHECK table + ext-gated sndr row + libmagic),
  `formats.c:830-850` (xfopen io_type), `formats.c:854-994` (open_read
  post-table), `formats_i.c:178-218` (pending-buffer rewind),
  `tx16w.c:77-181`, `smp.c:217-280`, `util.c:130-143` (extension parse).
