# r68 scout — post-table fallback map: fork is on the NAMED bit, not the seekable bit; txw is the cheap pipe-refusal member

Seat: scout (leaf). Lane: audio. Repo state at measurement: `audio-shokunin`
worktree (`~/Projects/prymeagnt/audio`, `.shokunin/audio` symlinks into the
canonical repo). Host: `SoX_ng v14.8.0.1` at `/usr/bin/sox`, ffmpeg n9.0.1,
Linux 7.2.3-arch1-3. Source: upstream sox_ng-14.8.0.1 tree
`/tmp/sox_ng_src/sox_ng/src/` — `formats.c` sha256 `82c3058e…` byte-identical
to the lane's verified copy (`corpus/live/r64-reviewer/r64rev-formats.c`).
Evidence: scratch `corpus/live/r68-scout/` — `probes/` (13 fixtures),
`run_matrix.sh` → `runs/matrix.tsv` (13 members × 8 transports, 104 legs),
`runs/strace-{file,pipe,fifo,redir}-nd.txt`, `logs/*.stderr`.

## Headline for the author — the declared partition is falsified

Declared claim: *post-table fallback behavior forks on transport seekability —
a no-match member gets a different verdict/error signature on
`file`/`redirected_fd` vs `stdin_pipe`/`fifo_path`.*

Measured on `.shokunin/audio/corpus/live/r68-scout/probes/` across the tracked
4-arm set: **the post-miss verdict partitions on the NAMED/extension bit, and
the seekable bit never enters the dispatch.** For every member shape:

- `redirected_fd` ALWAYS lands in the `stdin_pipe` group — both spell the
  input `-`, and `-` carries no extension, so both die
  `can't determine type of  '-'` — *even though* the redirected fd is
  measurably seekable (strace `lseek(0,0,SEEK_CUR)=0`, rewind `lseek(0,-300,
  SEEK_CUR)=0` — seekability confirmed and unused).
- `fifo_path` ALWAYS lands in the `file` group when the name carries a
  handler-known extension — the extension-dispatched reader runs on the
  pending-buffered prefetch and emits the file-identical verdict
  (`fifo/nd_zeros.wav` → `RIFF header not found` ≡ `probes/nd_zeros.wav`),
  *despite* the fifo being non-seekable.

The claim's grouping `{file,redir}|{pipe,fifo}` is unreachable for ANY
no-match member: the `-` arms can never join the named-reader verdict. A real,
differently-oriented fork exists and is exactly measurable: on a `.wav` member
`{file,fifo_path} = extension-reader verdict` vs `{stdin_pipe,redirected_fd} =
can't determine type of  '-'`. The claim's predicted seekable partition IS
realized — but by the *other* r68 member: the detected txw pipe-refusal member
forks `{file,redir}=decode` vs `{pipe,fifo}=refusal` exactly on the seekable
bit (inside the reader, not in the fallback dispatch). Per the seat rule:
report the observed outcome — a namedness fork on the fallback member, a
seekability fork on the detected member.

## 1. What SoX does after a full CHECK-table miss (per transport)

`auto_detect_format` (`formats.c:66-271`) prefetches ≤257 B once via
`lsx_readbuf_rewind` (`formats_i.c:178-219`). On miss (`return NULL`,
formats.c:270) `open_read` falls to `formats.c:920-933`, which keys on
`ft->io_type` and the path extension — **`ft->seekable` is never read**:

```
if (ft->io_type == lsx_io_pipe)            /* only `|cmd` spellings */
    filetype = "sox";  lsx_report("assuming input pipe `%s' has file-type `sox'")
else if (!(filetype = lsx_find_file_extension(path)))
    lsx_fail("can't determine type of %s `%s'", type, path)
else if (!(handler = sox_find_format(filetype, sox_true)))
    lsx_fail("no handler for file extension `%s'", filetype)
```

Measured ladder (matrix rows, `runs/matrix.tsv`):

| input shape | post-miss verdict | rung |
|---|---|---|
| `|cat x` (io_type=pipe) | `assuming input pipe '...' has file-type 'sox'` → `can't find sox file format identifier` | assume-sox |
| named, ext known (`.wav`) | extension handler runs → reader verdict (`RIFF header not found` for zeros; `header not found` for RIFF+XXXX; `invalid filetype ID ... != LM8953` for `.txw`; `header does not begin with magic word SOUND SAMPLE DATA ` for `.smp`) | extension-dispatch |
| named, ext unknown (`.bin`) | `no handler for file extension 'bin'` (path-free string) | no-handler |
| named, no ext (`nd_noext`, `fifo/noext_member`, `/dev/stdin`) | `can't determine type of file '<path>'` | can't-determine |
| `-` (pipe OR seekable redir) | `can't determine type of  '-'` — **double space**: `type` is only assigned in the xfopen branch (formats.c:895), `-` keeps `""` | can't-determine |

So **yes, a fallback "classification" runs** — but it is an *extension→handler
dispatch* (`sox_find_format(ext, is_file_extension=true)` = names[] lookup,
formats.c:1809-1832), not a re-read/retry. The dispatched reader sees the full
stream on every transport.

**The prefetch-consumption framing in the brief is wrong and worth correcting
in the round record**: on non-seekable transports the ≤257 prefetch bytes are
NOT consumed/lost — `lsx_readbuf_rewind` stashes them in `ft->pending_buffer`
(`formats_i.c:207-213`) and `lsx_readbuf` replays them to the reader first
(`:109-115`). On seekable it `rewind()`s. Strace (`runs/strace-*-nd.txt`,
probe = 300 zero bytes):

- `file`: `openat=3` → `lseek(3,0,CUR)=0` (is_seekable) → `read(3,…,4096)=300`
  (one bulk read; fread(257) buffers the surplus) → NO rewind syscall (glibc
  in-buffer pointer reset) → post-miss `lseek(3,300,SET)` + `lseek(3,1,SET)`
  — the fallback wav reader's own seeks → `RIFF header not found`.
- `stdin_pipe`: `lseek(0,CUR)=ESPIPE` → `read(0,…,4096)=300` → two
  `lseek(0,-43,CUR)=ESPIPE` (harmless glibc buffer-adjust attempts, both
  ignored) → `can't determine type of  '-'` — no reader ever ran.
- `redirected_fd`: `lseek(0,CUR)=0` → `read=300` → `lseek(0,300,SET)` +
  `lseek(0,-300,CUR)=0` (fd rewound fine) → `can't determine type of  '-'`.
- `fifo_path`: `openat(fifo)=3` → `lseek(CUR)=ESPIPE` → `read=300` →
  `lseek(3,0,CUR)=ESPIPE` → `RIFF header not found` — reader ran entirely on
  pending+stdio-buffered bytes; kernel fd never re-read.

Two edge discoveries beyond the asked map:

- **Ext-gated CHECK row — a detection fork on namedness.** formats.c:247-248:
  `if (ext && !strcasecmp(ext,"snd")) CHECK(sndr, 7,1,"", 0,2,"\0")`. My
  `nd_zeros.snd` (300 zeros) **detected `sndr`** on file/fifo/`|cmd` → sndr
  reader → `invalid rate value`; on `-` (ext NULL) the row is skipped →
  can't-determine. This is the first counterexample to r67's "detection never
  forks": a `.snd`-named member forks *in detection itself*. The fallback
  family should NOT be named `.snd` (it never reaches fallback on named
  arms); the quirk also fires on `|cmd` strings (extension parsed from the
  whole `|cat x.snd` path).
- **`--magic`/`use_magic`** (sox_ng.c:2547): off by default; when set,
  `magic_buffer` runs on the prefetch inside `auto_detect_format`
  (formats.c:251-269). Untracked axis; no arm uses it.

## 2. txw vs smp — which pipe-refusal member is cheaper: **txw**

Both readers refuse non-seekable input with the identical string
`input must be a file, not a pipe` at the very top of startread
(`tx16w.c:90-94`, `smp.c:228-232`) — before any content check — so the
refusal arm signature is identical; the member cost is all in detection bytes
and the seekable-arm verdict:

| | txw | smp |
|---|---|---|
| detect predicate | `LM8953`@0-5, len≥6 (formats.c:86) | `SOUND SAMPLE DATA`@0-16, len≥17 (formats.c:79) |
| minimal detect | **6 B** | 17 B |
| reader needs | 32-B header + N·3 B data (12-bit, 3 B→2 samples) | 112-B header + 4-B count + 2N data + 215-B trailer (two extra seeks) |
| minimal openable | **32 B** (`txw_hdr_only` → 0 samples, exit 0) | ~331 B |
| measured decode member | 332 B → **200 samples exit 0** (`txw_min.wav`, sha `f0cf2e13…`) | 339 B → 4 samples (`smp_min.wav`, sha `c2fc3627…`) |
| pipe/fifo verdict | `input must be a file, not a pipe` | identical |

Measured 4-arm matrix on `txw_min.wav` (332 B): `{file, redirected_fd,
dsredir}` → detected `txw`, decode 200, exit 0; `{stdin_pipe, fifo_path,
fifo_noext, dspipe, popen}` → detected `txw`, refusal, exit 2. Detection is
transport-invariant (txw on all 8 arms); the fork is the reader's seek gate —
a clean {seekable}|{non-seekable} 2-group partition, the mirror image of
gsrt's fork (decode on the *seekable* side). `txw_6.wav` (6 B) also detects
and gives the cheaper fail-fork (`file is truncated` vs refusal); `txw_5.wav`
(5 B) is below the detect gate → falls to the `.wav` extension →
`RIFF header not found` — the exact len≥6 gate is pinned.

Recommend `pair_piperefuse_txw.wav` = `"LM8953"` + 26-B header rest
(16 discard + format 0xC9 + rate 1 + 8 gunk) + 300 data bytes = 332 B,
sha `f0cf2e13…` as constructed. Named `.wav` deliberately: content detection
precedes extension, so it detects `txw` anyway — and the fifo inherits a
handler-known name (receipt-safe, see §4 caveat b).

## 3. Existing fixtures that exercise no-match

**Tracked: none.** Every tracked `pair_*` member is a detection-decision
member (matches a CHECK row by construction). The `--probe-invalid` set is
all wav-detected — verified `round-6/{wrong_format,short_sections}.wav` →
`detected file format type 'wav'`; `corrupt.wav` is RIFF/WAVE magic
(`xxd` shows `RIFF....WAVEfmt`) → wav-detected, its failure is downstream.
So the post-table path is a genuine unmeasured gap — the r68 move is real.

Scratch (prior rounds, untracked): r67-scout `probes/nodetect.{bin,wav}`
(300 zeros — already measured named-ext→wav-reader, `-`→can't-determine,
`|cmd`→assume-sox; my matrix reproduces verbatim); r66-boundary
`probes/{g_txw_*,p_smp_*}.bin` (txw/smp refusal probes, 300 B).

## 4. Receipt / probe-shape suggestions

**Members (minimal additive set, all deterministic literals):**

- `corpus/live/round-68/pair_fallback_wav.wav` — no-match member, `.wav` name.
  Content: 300 B of `RIFF`+LE32(292)+`XXXX`+zeros (my `nd_riffx.wav`, sha
  `98be117f…`) — recommended over flat zeros because it sits one conjunct
  away from *two* rows (wav needs `WAVE`@8; act needs `0x84`@256 — verified
  no row fires, detected=None on all arms) and lands the deeper wav-reader
  rung `header not found` (vs `RIFF header not found` for non-RIFF zeros —
  both measured, either works).
- `corpus/live/round-68/pair_piperefuse_txw.wav` — 332 B per §2.
- Optional third: `pair_fallback_ext.txw` (zeros named `.txw`) → **3 groups**
  {file=`invalid filetype ID…`}|{fifo=pipe-refusal}|{pipe,redir=can't-
  determine} — the only shape where file≠fifo splits inside the fallback
  family (seek-gated extension reader). `.smp` variant gives
  `header does not begin with magic word SOUND SAMPLE DATA ` (note trailing
  space) on file.

**Expected receipt signatures (4-arm set, `transport_entry` verbatim):**

| member | verdict groups | fork | exit |
|---|---|---|---|
| `pair_fallback_wav.wav` | {file,fifo}=`header not found` \| {pipe,redir}=`can't determine type of  '-'` | yes (named bit) | 1 |
| `pair_piperefuse_txw.wav` | {file,redir}=decode 200 \| {pipe,fifo}=refusal | yes (seekable bit) | 1 |
| `pair_fallback_ext.txw` (opt) | 3 groups as above | yes (both bits) | 1 |

`sox_detected_format` = `null` on every arm of the no-match members (new
receipt shape: `detected` absent → `sox_route` falls to `"none"` — correct as
landed); txw member = `txw`/`native` on all arms.

**Two receipt-shape additions worth landing:**

- `fallback_dispatch` per arm — an explicit enum the arm's rung can be
  recorded as: `"detected"` | `"extension:<ext>"` | `"no-handler:<ext>"` |
  `"assume-sox"` | `"can't-determine"`. Derivable deterministically
  (member basename extension + the measured error) and it makes the fork's
  real axis legible without string-parsing — the verdict signature alone
  can't tell a reader-ran arm from a can't-determine arm when `detected` is
  null (both show `route:"none"`).
- Determinism caveat in `transport_error` (measure_audio.py:200-207): it
  returns the whole FAIL line when no `':` follows. `can't determine type of
  file '<path>'` embeds the input path — on `fifo_path` that path is the
  volatile `/tmp/transport-r67-*/<name>`. `.wav`/`.txw`/`.smp`/`.bin` members
  dodge it (their errors are post-`':` or path-free: `no handler for file
  extension 'bin'` carries no path). **Do not land a no-extension member
  under the current code**, or scrub `error` with the same
  `` `[^']*' ``→`` `<input>' `` regex `stderr_tail` already applies
  (measure_audio.py:236-237).

**Insertion map** (additive; mirrors r67 exactly):

- `corpus/fixtures/measure_audio.py`: flags `--probe-fallback-wav-r68`,
  `--probe-piperefuse-txw-r68` (±`--probe-fallback-ext-txw-r68`) after the
  r67 block (~L416); exclusivity `sum()` +2/3 (L418); member map
  `FALLBACK_R68_MEMBERS` + arm block newest-first *before* the r67 block
  (L604); reuse `transport_leg`/`transport_matrix`/`transport_entry`
  unchanged (fifo writer-linger is unnecessary here — no second open on
  native fallback readers — but keeping `TRANSPORT_R67_FIFO_WRITER_HOLD_S`
  keeps the protocol uniform and is harmless); `mode`/`suffix` chain heads
  ~L1021/~L1041; no base-measurement changes → all 112 prior rows +
  receipts byte-stable.
- `corpus/fixtures/build_artifacts.py`: `build_fallback_piperefuse_r68_probe()`
  writing the two round-68 members as literal `write_bytes` (same pattern as
  `build_ui_dec_preempt_r66_probe` L192 / `build_ui_lengate_r66_probe` L246);
  dispatch branch alongside the r66 chain (~L964).
- Runner/ledger: insert the new modes newest-first after r67's block;
  expected ledger 112→114(115) rows, prior-112 byte-identical; new rows exit
  1 with the fork pinned in `failures` (same convention as r67's 5 fork rows).

## Unresolved / limits

- Exact lseek attribution inside the fallback wav reader (`lseek(300,SET)` +
  `lseek(1,SET)` on file): reader-stage seeks, not re-classification; the
  glibc in-buffer rewind shortcut is inferred from syscall *absence*, not
  source-verified on this glibc.
- `can't determine type of  '-'` double-space is stable on this build
  (`type=""` for `-`, formats.c:866/895); other builds with different
  io_types wording would differ — within-host determinism only.
- `.snd` detection fork measured on one content (300 zeros); whether other
  ext-gated behavior exists in sndr's reader is unprobed (out of scope).
- No claim beyond local fixture behavior on this host/toolchain
  (SoX_ng 14.8.0.1, USING_FFMPEG); no fidelity/conformance/quality claim.

Artifacts: `corpus/live/r68-scout/{probes/ (16 members), runs/probe-shas.txt,
run_matrix.sh, runs/matrix.tsv (13-member × 8-transport matrix, 104 legs),
runs/strace-{file,pipe,fifo,redir}-nd.txt, logs/ (116 stderr — 104 matrix +
12 supplementary `.txw`/`.smp`/`.snd` legs)}`.
