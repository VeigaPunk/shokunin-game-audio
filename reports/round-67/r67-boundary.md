# R67 boundary (revenger) — transport-axis edges: the verdict space is not {named × seekable} — it's *what the ffmpeg child can re-resolve*; fifo+act hangs without a held writer; early-EOF on fifo flips detection at each member's len gate

Seat: **revenger** — reconstruct host behavior from executable evidence; no tracked
mutation. Host: `sox` = SoX_ng **14.8.0.1** (`/usr/bin/sox -> sox_ng`, USING_FFMPEG
build), ffmpeg/ffprobe **n9.0.1**, python **3.14.7**, kernel `7.2.3-arch1-3` — identical
toolchain to r63–r66. No `lsp` device answers this repo (same as r64–r66; symbol
adjacency checks are text-grep + strace fallbacks). Scratch:
`corpus/live/r67-boundary/` (harness `run_probes.py`, `fifo_race.py`; logs in
`runs/logs/`; matrices `runs/edge_matrix.tsv`, `runs/race.tsv`,
`runs/forced_t_pipe.tsv`). `git status` audit: **zero tracked writes by this seat** —
the only `M` is the author's own `measure_audio.py` (+141) plus its mechanical
`.pyc` regeneration.

## Author landing state (verified at probe time)

Author landed uncommitted: `corpus/fixtures/measure_audio.py` +141/−0 —
`TRANSPORT_R67_ARMS = {file, stdin_pipe, redirected_fd, fifo_path}` as a
{named × seekable} 2×2, `TRANSPORT_R67_MEMBERS` = the 10 tracked autodetect members
(r65 preempt ×4 + r66 dec/lengate ×6), `transport_leg` = `sox -V6 … -n stat` under a
10 s arm timeout, fifo writer protocol "one-shot write then **writer lingers 1.0 s**"
(`TRANSPORT_R67_FIFO_WRITER_HOLD_S`), receipt fields `transport_axis`,
`transport_verdict_groups`, `transport_fork`. Determinism spot-check by this seat:
`--probe-transport-dec-act-r67` ×5 → all receipts `*-transport-dec-act-r67`,
**byte-identical** (sha `195d7554…` twice `cmp`-verified). The author's measured fork
set on the tracked family (their arm, my run): **5/10 fork** — `preempt_act`,
`dec_act` (3 groups), `preempt_gsrt`, `preempt_both`, `lengate_gsrt_25` (2 groups);
invariant: `preempt_hcom`, `dec_hcom`, `lengate_gsrt_24`, `lengate_hcom_131`,
`lengate_hcom_132`. Consistent with the declared claim (≥1 member forks; the set is
exactly measurable).

## Reconstructed contract — the real verdict discriminator

`sox`'s detection is transport-invariant on a fully-written stream (r66 confirmed
again here — every detection column identical across 14 transports). The fork lives
entirely **after** detection, in three independent mechanisms:

1. **Seekable side-paths in native readers.** `gsrt.c:88` (`file_size >= 2 &&
   ft->seekable`) gates the checksum scan — on a RIFF collider `file_size` is the
   literal `0x52494646` ≈ 1.38 G → seekable transports walk to real EOF
   (`premature EOF`), non-seekable transports skip the loop and die at the header
   parse instead (`invalid format for this file type` /
   `invalid/missing file name in header`). Same verdict pair on every
   non-seekable fd — pipe, /dev/stdin-pipe, /proc/self/fd-of-a-pipe, socket-fd.
   `txw`/`smp` readers refuse non-seekable outright (`input must be a file, not a
   pipe`). `wve`'s declared-length WARN and `amr-nb`'s decode count
   (800 seekable / 1120 non-seekable — see E5) ride the same gate.
2. **The act bridge = `popen("ffmpeg -nostdin -i <LITERAL-SPEC> -f au -")`.**
   strace evidence (`runs/strace-*.txt`):
   `openat(f)=3 → fstat → lseek ESPIPE-or-0 → read(3)=600 → detect act →
   pipe2([4,5]) → clone → child closes fds (incl. 3), dup2(5→1) → execve ffmpeg`.
   The verdict is decided by **what the literal spec resolves to inside the
   child** and by the shared-offset state of `-`:

   | input spec given to sox | ffmpeg argv | child-side resolution | verdict |
   |---|---|---|---|
   | regular path | `-i <path>` | fresh open, offset 0 | **decodes** (278/3839) |
   | `-` (fd0 = pipe/socket) | `-i -` | residue after detection's 257-B read | `can't find Sun/NeXT/DEC identifier` |
   | `-` (fd0 = regular, offset 600) | `-i -` | inherited offset = EOF | `premature EOF` |
   | `/proc/self/fd/N` | `-i /proc/self/fd/N` | **ENOENT** — child fd-sanitized (strace: `close(3)` then `openat("…/fd/3") = -1 ENOENT`) | `premature EOF` |
   | `/dev/stdin` (fd0 = regular) | `-i /dev/stdin` | child's fd0 = the real file, fresh open | **decodes** (278/3839) |
   | fifo path | `-i <fifo>` | `openat(fifo)` — second open, needs a live writer | **HANG** if writer gone; tail-steal → `Sun identifier` if writer lingers |

   SoX then runs the child output through its au parser and `pclose()`-waits on the
   child — which is why the fifo-dead-writer cell hangs the whole command, not just
   the bridge leg.
3. **Detection blocks for the full predicate window.** `auto_detect`'s first read
   wants `AUTO_DETECT_SIZE` (257) bytes or EOF — a lazy fifo writer cannot cause a
   short-window misdetect (E2); only an early EOF can.

The author's receipt model {named × seekable} is accurate **inside the declared
four transports** — but it is a proxy. The actual axis is *child-side spec
resolvability × fd seekability × writer liveness × reader side-paths*. Two
seekable-named fd-indirections split the same way the 2×2 cannot predict:
`/dev/stdin`-over-file decodes, `/proc/self/fd/3`-over-file dies ENOENT.

## E1 — transports outside the declared set (27 members × 14 transports = 378 legs)

Harness `run_probes.py`; full TSV `runs/edge_matrix.tsv`; per-leg `-V4` output in
`runs/logs/<member>.<transport>.log`. Verdict summary (error tail after `':`):

| member | seekable-named (file, /dev/stdin<reg, tmpfs) | seekable-fd (`-`<reg, procfd_reg, memfd, O_WRONLY, O_PATH) | nonseek-fd (pipe, devstdin_pipe, procfd_pipe, sockstdin) | fifo (writer one-shot) | socket path |
|---|---|---|---|---|---|
| pair_route_84 / preempt_act | act **3839** | act `premature EOF` | act `Sun/NeXT identifier` | **HANG** ≥20 s | ENXIO open |
| pair_valid_{8,9,24,25,57} | act {11520,5760,3839,2880,1440} | act `premature EOF` | act `Sun identifier` | **HANG** | ENXIO |
| pair_valid_56 | act `premature EOF` | act `premature EOF` | act `Sun identifier` | **HANG** | ENXIO |
| pair_route_00 | wav `number of valid bits exceeds…` identical all 14 | — | — | same | ENXIO |
| preempt_gsrt / preempt_both | gsrt `premature EOF` | gsrt `premature EOF` | gsrt `invalid format for this file type` | same as nonseek | ENXIO |
| lengate_gsrt_25 | gsrt `premature EOF` | same | gsrt `invalid/missing file name in header` | same | ENXIO |
| dec_act | act **278** | act `premature EOF` | act `Sun identifier` | **HANG** | ENXIO |
| dec_hcom / z_hcom_dec | hcom **9** — invariant on all 14 | — | — | hcom 9 | ENXIO |
| preempt_hcom | hcom `bad compression type` — invariant | — | — | same | ENXIO |
| lengate_gsrt_24 | wav `fmt chunk not found` — invariant | — | — | same | ENXIO |
| lengate_hcom_131 | wav **43** — invariant | — | — | same | ENXIO |
| lengate_hcom_132 | hcom `premature EOF` — invariant | — | — | same | ENXIO |
| z_gsrt_ulaw (real gsrt) | gsrt **1000** | same | same | same | ENXIO |
| b_wve_dec / a_wve_valid | wve 100 / 16 — invariant | — | — | same | ENXIO |
| g_txw_hcom | txw **178** | txw **178** | txw `input must be a file, not a pipe` | same | ENXIO |
| p_smp_intact | smp `header is not version 2.1` | same | smp `input must be a file…` | same | ENXIO |
| p_voc_intact | voc FAIL, empty error string — invariant | — | — | same | ENXIO |
| g_amrnb_hcom | amr-nb **800** | amr-nb **800** | amr-nb **1120** | amr-nb 1120 | ENXIO |

Measured facts the declared set doesn't reach:

- **`/proc/self/fd/N` indirection exists and splits by the fd's own type, not the
  path**: fd→regular-file gives the seekable class (`premature EOF` on act members);
  fd→pipe gives the non-seekable class (`Sun identifier`). `openat("/proc/self/fd/3")`
  re-opens the underlying file description — the kernel does the class assignment.
- **`O_PATH` and `O_WRONLY` fds are not barriers**: `openat("/proc/self/fd/3")` on
  an O_PATH fd *succeeds* on this kernel (strace `openat … = 4`) — sox reads and
  detects normally; verdict lands in the seekable-fd class. `memfd_create` (anonymous
  regular file) same class.
- **socket as fd-0** (`socketpair` → `sox -`): behaves exactly like a pipe —
  non-seekable class, identical verdicts (`Sun identifier`, `invalid format`, pipe
  refusal, amr-nb 1120).
- **socket as path** (`sox <unix-socket-path>`): `openat` fails ENXIO —
  `can't open input file '…': No such device or address`, **detection never runs**
  — a fifth verdict class (transport-layer open failure) no declared arm covers.
- **`/dev/shm` tmpfs regular file** = file class (seekable named), as expected —
  the mmap'd-tmpfs flavor of "transport" is invisible because readers `read()`,
  not `mmap()`.

## E2 — fifo write pacing (racing writer vs lazy reader)

Harness `fifo_race.py`; TSV `runs/race.tsv`.

- **Detection does NOT short-read**: writer splits at {16,24,64,100,128,131,200,
  255,256} bytes with a 0.8 s gap — every member still detected its designed
  format (hcom@cut64 → hcom; gsrt@cut16 → gsrt). The autodetect read blocks for
  the 257-B window (or EOF). The brief's hypothesized "257-byte predicate split
  across two writes" misdetect **does not exist** — timing cannot fork detection.
- **Early-EOF DOES fork detection — exactly at each member's length gate**
  (writer writes N<257 then closes):
  - `dec_act` close@{24: `wav` `file is truncated` exit 2; 64,128,131,200,256:
    `wav` + **partial successful decode** 10/42/43/78/106 samples, exit 0 + WARN
    `premature EOF`. The act conjunct needs byte 256 — a sub-257 EOF flips
    act→wav and the suppressed wav member yields a working partial decode.
  - `dec_hcom` close@≤131 → `wav` partial (10–43); close@≥132 → `hcom` 9 — the
    131‖132 hcom gate reproduces on fifo EOF.
  - `preempt_gsrt`/`lengate_gsrt_25` close@24 → `wav`; close@≥25 → `gsrt`
    non-seekable error — the 24‖25 gsrt gate reproduces.
  So fifo EOF truncation is a real **detection** fork reachable only through
  transport timing — same bytes, different route.
- **act on fifo — writer liveness at bridge-open decides the failure MODE**
  (both dead, differently): writer-gone → `openat(fifo)` in the ffmpeg child
  blocks → **indefinite hang** (strace `runs/strace-fifo-act.txt`: child `openat …
  = ? ERESTARTSYS`, killed at timeout; my matrix legs hung ≥20 s ×4 act members);
  writer-held → child's open succeeds, reads the stream **tail** (prefix already
  consumed by sox) → `can't find Sun/NeXT/DEC identifier`, fast exit 2.
  The author's 1.0 s `FIFO_WRITER_HOLD_S` pins the second cell — the hold is
  **load-bearing**, not cosmetic: without it the fifo arm is hang-class. The
  recorded `Sun identifier` verdict is itself the tail-steal artifact, which is
  honest (the bridge is dead either way); the `transport_protocol` block discloses
  the protocol. Residual race margin: ffmpeg's fifo `openat` lands ~0.5–1.0 s
  after spawn (exec chain + lib loading, strace-timed) — on a loaded host the
  1.0 s hold could expire first, flipping the arm to the timeout verdict
  (`blocked: no verdict within 10 s`). Thin but real.

## E3 — transport axis on the r63/r64 valid-bits family

All six `pair_valid_{8,9,24,25,56,57}.wav` detect **`act`** — they are built on the
0x84@256 carrier, so they fork identically to the act members (seekable-named =
decode {11520,5760,3839,2880,1440}; seekable-fd = `premature EOF`; nonseek-fd =
`Sun identifier`; fifo = HANG). `pair_valid_56` fails even on file
(`premature EOF` — its payload isn't ffmpeg-decodable) but still forks. The wav
member `pair_route_00` is transport-invariant (`number of valid bits exceeds…`
on all 14). **Answer: the fork follows the routed reader, not the fixture family —
every act-routed member forks, including the whole valid-bits set; the u8/s16/s24/
s32/s64 distinction never reaches the transport decision.**

## E4 — pipe + `-t` forced legs (does forcing bypass the fork?)

`runs/forced_t_pipe.tsv` (9 members × 7 forced types):

- **`-t act` on pipe WORKS** — `pair_dec_act`→278, `pair_route_84`→3839,
  `pair_dec_hcom`→3520 (ffmpeg hcom demuxer), `g_txw_hcom`→1120. With `-t`,
  autodetect never runs, so detection's 257-B consumption never happens — the
  bridge reads the stream intact. **The r64 "stdin bridge is structurally dead"
  is dead *because detection consumed the stream*, not because the bridge can't
  read a pipe** — sharpening, not contradiction (autodetect+pipe is what the
  ledger runs).
- `-t wav` on `pair_dec_act`/hcom pipe → 278 / `-t wav` `pair_lengate_hcom_132` → 44
  (suppressed members readable through pipe).
- `-t hcom` `pair_dec_hcom` → 9 (invariant); `-t gsrt` `z_gsrt_ulaw` → 1000.
- `-t txw` / `-t smp` → `input must be a file, not a pipe` **on every member** —
  the refusal is reader-side; forcing cannot bypass.
- So: forcing bypasses the *detection-consumption* poison but not reader-side
  transport gates.

## E5 — mid-stream starvation (slow writer)

- `dec_hcom`/`z_hcom_dec`: detection+decode complete inside the first 257-B
  window — 0.00 s exits while the writer still slept (EPIPE on the tail write;
  harmless). Immune to starvation.
- `preempt_gsrt`/`lengate_gsrt_25`: die at header parse immediately — starvation
  irrelevant.
- `g_amrnb_hcom`: **1120 samples on every non-seekable transport regardless of
  pacing** (contiguous, 2.0 s starve, 64 B×60 ms dribble); 800 on every seekable
  one — the r66 800-vs-1120 fork reproduced across fifo/devstdin_pipe/procfd_pipe/
  sockstdin; mechanism flagged by r66 stays flagged (frame-boundary vs buffered-
  chunk inference, still inference).
- `dec_act` dribble → `Sun identifier` 0.61 s; preempt_gsrt dribble →
  `invalid format` 0.42 s — both die before dribble matters.

## Divergences / disclosures

1. **The {named × seekable} 2×2 is a proxy, not the mechanism** — `/proc/self/fd/N`
   (named+seekable, 2×2 predicts file-class decode) actually fails `premature EOF`
   via child ENOENT; `/dev/stdin` (same booleans) decodes. Harmless inside the
   declared four arms; mislabels edge transports.
2. **fifo+act is a two-cell fork**: HANG (writer gone) vs `Sun identifier`
   (writer held → tail-steal). The author's held-writer protocol lands the
   second cell deterministically (5/5 runs byte-identical); the hold is
   load-bearing with a ~0.5–1.0 s margin against ffmpeg's open latency.
3. **socket-path open failure** (ENXIO) and **early-EOF detection flips**
   (act→wav partial decode below 257) are verdict classes outside the arm.
4. **`-t act` on pipe works** — "structurally dead" pins to
   detection-consumption, not pipe-read inability.
5. Author-arm audit from this seat: receipts deterministic (5× byte-identical
   dec_act); `named`/`seekable` fields accurate on the declared arms; the
   `transport_protocol` disclosure block is honest.
6. My run of `--probe-transport-dec-act-r67` at 05:15:17 emitted a `-normal`
   receipt dir (suffix chain not yet in the then-working file) — transient
   mid-edit state, superseded; all later runs suffix correctly.

## UNKNOWNs / limits

- Single host/toolchain (SoX_ng 14.8.0.1 USING_FFMPEG + ffmpeg n9.0.1). The
  ENOENT-in-child mechanism depends on SoX's popen fd-sanitization; a build
  passing fds differently changes the procfd cell. ffmpeg's own probe/read
  internals inferred from argv+strace, not source.
- The `Sun identifier` vs `premature EOF` emitter split inside the au-parse is
  inference (different child outputs), not pinned to a code line.
- Hang verified ≥20 s (legs killed at 20/8 s timeouts), strace shows indefinite
  `openat` block — "hangs until a writer appears", not "hangs forever" formally.
- amr-nb chunk mechanism still unexplained (carried from r66).

## Confidence

**High** on the measured table (378 matrix legs + ~60 race legs + 63 forced legs,
verbatim `-V4` logs retained per leg; strace evidence for the bridge argv, the
child fd-sanitize ENOENT, the fifo second-open block, and O_PATH re-open success).
**Medium** on the au-emitter split and the writer-hold margin (timed on two
strace runs). Author arm re-run by this seat produced byte-identical receipts —
the landed code does what its protocol block says.

## Receipts

- `corpus/live/r67-boundary/run_probes.py` — 14-transport harness.
- `corpus/live/r67-boundary/fifo_race.py` — split/starve/dribble/early-close.
- `corpus/live/r67-boundary/runs/edge_matrix.tsv` (+ `edge_matrix_console.txt`) —
  378 rows; `runs/logs/*.log` — per-leg verbatim `-V4`.
- `corpus/live/r67-boundary/runs/race.tsv`, `runs/forced_t_pipe.tsv`,
  `runs/member-shas.txt` (tracked-member digests match published values).
- Author-arm evidence: receipts under `corpus/live/runs/*-transport-*-r67/`
  (10 modes × several runs; `195d7554…` byte-identical pair cited above).
- strace captures: `runs/strace-fifo-act.txt` (child `-i` argv + blocked
  `openat(fifo)`), `runs/strace-procfd-act.txt` (`openat /proc/self/fd/3 =
  -1 ENOENT` inside ffmpeg), `runs/strace-redir-act.txt` (`-i -` + offset
  evidence), `runs/strace-fifo-heldwriter-tt.txt` (timing),
  `runs/strace-opathfd.txt` (`openat /proc/self/fd/3 = 4` on an O_PATH fd).
