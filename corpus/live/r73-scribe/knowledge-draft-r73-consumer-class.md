# Knowledge draft (r73) — consumer class: pw-cat (PipeWire) + mpv (lavf)

Status: DRAFT at scribe time. Basis = frontier pre-measurement
(`ports/frontier/fb-pipewire.md`, committed c079aba) + tracked corpus
`corpus/live/frontier-pipewire/` (25 files) + scribe artifact audit
(`frontier-claims-audit.tsv`, this dir). The round-73 author arm
(`--probe-consumers-r73`) was absent through 14:49:30Z and **landed in the
working tree at ~14:50:23Z (uncommitted; 4 receipts — runs 1–2 byte-identical,
runs 3–4 one ≤1 ms `wall_s` leaf apart; verdict/partition/fork fields identical
across all four)**. The draft below was assembled from the frontier artifacts
before the landing; the landed receipt confirms the per-member fork picture
(see `reports/round-73/r73-scribe.md`, landed-arm audit).

**In-flight sibling corrections (uncommitted, added 14:45Z; not replayed by
this seat — quoted in `reports/round-73/r73-scribe.md`):** r73-scout /
-boundary / -critic converge that the briefed *class* partition is falsified
as stated — mpv forks on exactly one member (`dec_hcom`, seekable bit proven
by a same-transport pair: `-` with pipe stdin rc0 vs regular-file stdin rc2),
and pw-cat's only corpus fork is the `.snd` filename axis (same polarity as
the decoder axis); `Seek failed (Operation not permitted)` is library-synthetic
(strace: 0 failing syscalls; `av_strerror(-1)` "no seek path" sentinel);
zero-sink daemon → HANG (rc=-9); pw-cat exits at data-chunk end (linger
irrelevant); daemon gate fires 3–4 ms before input open. Treat as provisional
until the author arm lands and the verifier replays.

## 1. pw-cat (libpipewire 1.6.8; `pw-play` symlink → `pw-cat`)

Mechanism, in order of gates:

1. **Daemon gate precedes input open.** `PIPEWIRE_RUNTIME_DIR=<empty> pw-cat -p <any>`
   → `error: pw_context_connect() failed: Host is down`, rc=1, before the
   input (file or fifo) is touched; `pactl info` under the same empty runtime
   → Connection refused. Evidence: `pwcat-nodaemon.log`; independently
   reproduced in-flight by r73-critic (`r73-critic/pwcat-nodaemon-{file,fifo}.stderr`).
2. **Decode layer = libsndfile.** Every open error carries the `sndfile:`
   prefix. Format selection is content sniff first: no suffix/name axis on the
   frontier members (`extsuffix_nomatch.txw` raw bytes not opened as TXW; a
   fifo named `fifo1` plays a WAV). **Exception (sibling-measured,
   uncommitted): the `.snd` member is filename-gated** — named `.snd` → rc0
   (post-sniff libsndfile U-Law fallback, r72 mechanism), unnamed fifo / `-`
   → rc1. `-a/--raw` + `--rate/--channels/--format` bypass sniffing.
3. **Fifo writer-attach semantics.** open() blocks for a writer
   (wchan `wait_for_partner`), zero output, survives `timeout` SIGTERM >30 s
   (SIGKILL or writer attach required). Writer attaches then closes empty →
   `sndfile: ... Format not recognised.` rc=1. Writer delivers a member then
   closes → sniff + play, rc=0 at writer EOF.
4. **Consumption is playback-paced, not read-paced.** 64 KB (4 s) dumped in
   one write: wall ≈ 4 s; half-rate trickle: wall ≈ 9 s, blocks when starved,
   no underrun abort. (Numbers are report-text; see limits.)
5. **Single open.** No re-open-by-name bridge (contrast the SoX act path's
   `-`/name re-resolution). Fifo EOF = writer close is the only transport
   difference.
6. **Verdicts transport-invariant on every member tried.** Same sndfile
   predicate file vs fifo: hcom/act rc=0; `txw_piperefuse` rc=1
   "unimplemented format"; `extsuffix_nomatch.{wav,txw}` rc=1 "Format not
   recognised"; `pair_lengate_gsrt_25` rc=1 "No 'data' chunk marker" (file
   arm). Evidence: `pwcat-{file,fifo}-*.log`; r73-reviewer replay JSON agrees
   (uncommitted scratch).
7. **Operational hazards.** `--target 0` (unlinked stream) never drains —
   hangs forever (rc=124 under timeout); harnesses must use linked default
   (real sink) and `timeout -s KILL` (open-block is SIGTERM-immune).

## 2. mpv v0.41.0 (libavformat 63.1.101 / FFmpeg n9.0.1)

Mechanism:

1. **Probe = content sniff via lavf, transport-invariant.** `Found 'hcom' at
   score=100 size=600` on both file and fifo arms. Extension plays no role:
   `.wav` does not rescue no-magic bytes, does not prevent hcom detection.
2. **INVERTED seekability fork (hcom member).**
   - seekable input (regular file): after detection the demuxer issues
     `refresh seek to 0.000000` → `Seek failed (Operation not permitted)` →
     `finished playback, no audio or video data played (reason 4)` → rc=2.
     Zero audio frames played.
   - non-seekable input (fifo): `Stream is not seekable.` → no refresh seek →
     hcom decoder consumes the forward stream → plays (`● Audio --aid=1
     (hcom 1ch 22050 Hz)`), EOF at writer close, rc=0.
   Evidence: `mpv-{file,fifo}-pair_dec_hcom.wav.log:162/168, 171, 178–181, 203`.
3. **Non-forking members.** `txw_piperefuse`, `extsuffix_nomatch`: both arms
   fail at probe (`No format found ... Failed to recognize file format`,
   rc=2) — never reach the demuxer; no seekability exposure.
4. **Fork locus** = a post-detection reposition request by the hcom demuxer
   that a seekable input accepts the call on but the demuxer refuses (EPERM);
   non-seekable inputs skip the reposition. Not straced (frontier caveat) —
   inferred from log order.

## 3. Cross-consumer partition (the round's claim, as pre-measured)

| stage | pw-cat | mpv |
|---|---|---|
| detection | content sniff (libsndfile), transport-invariant | content sniff (lavf), transport-invariant |
| verdict fork on seekability | none observed on tested members (transport-invariant) | yes, inverted: seekable → refuse-to-play; non-seekable → play |
| transport contract | stream-consume, single forward open, playback-paced | mandatory-seek for the hcom demuxer refresh (file), stream-consume otherwise |

Polarity vs the decoder axis: decoder acceptance in prior rounds keys
POSITIVELY on seekability/namedness (SoX txw reader refuses pipes; act
ffmpeg-bridge decodes only from a name-resolvable regular file), while the
mpv consumer's hcom playback keys NEGATIVELY on it (non-seekable helps).
**Sibling-corrected (uncommitted):** this is a per-member fork, not a class
partition — mpv forks on exactly one member (`dec_hcom`), pw-cat's only corpus
fork is the `.snd` filename axis (same polarity as the decoder axis), and the
"opposite polarity" comparison holds only across *different* members. No
member was measured on which the same runtime flips polarity between the
decoder and consumer axes. Author landing/verification pending at scribe
snapshot.

## 4. Limits (do not upgrade past these)

- Wall-clock numbers (4 s instant dump, 9 s trickle, ~5 s raw) and most rc
  values are report-text only; the sole persisted rc artifact is
  `pwcat-fifo-w1.rc` (`pwcat-rc:0`). `--target 0` rc=124 likewise text-only.
  (Sibling re-measurements in flight: 4.38 s / 8.56 s, rc −9 hang — uncommitted.)
- mpv EPERM string is library-synthetic (sibling strace: 0 failing syscalls);
  the library-internal context is not identified.
- Fork measured on one member (`dec_hcom`); other members never reach the
  demuxer. pw-cat's `.snd` filename fork measured by siblings only.
- pw-cat requires a live daemon **with a linkable sink**; zero-sink daemon →
  HANG (sibling-measured, uncommitted). No daemon → rc=1 before input open.
- Untested: pw-record, MIDI modes; writer-dies-mid-stream and multiple writers
  now sibling-measured (rc=0 both) but uncommitted.
- Single host (plazir27), libpipewire 1.6.8, mpv 0.41.0 / lavf 63.1.101,
  ffmpeg n9.0.1; no portability or conformance claim.
