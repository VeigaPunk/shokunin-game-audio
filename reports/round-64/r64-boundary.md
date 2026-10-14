# Round 64 — boundary (revenger): the valid-bits step map is exact, and stdin+autodetect+ffmpeg is broken two ways

Seat: **revenger** — reconstruct host behavior from executable evidence. Scope: (1) the lane's
declared axis-move — sweep `wValidBitsPerSample` through the step boundaries under the SAME
act-forced route and pin where ffmpeg's codec/width steps; (2) scratch recon of r63's UNKNOWNs —
stdin autodetect path, `goto error` no-fallback terminal ordering, and whether a second
autodetect can re-claim the ffmpeg pipe. Host: Arch Linux, `sox` = SoX_ng 14.8.0.1,
`ffmpeg`/`ffprobe` = n9.0.1 (same host as r62/r63). All work under
`.shokunin/audio/corpus/live/r64-boundary/`; report only; no repo content changed.

## Verdict: step map established — seven boundaries pinned exactly; tracked pairs landed

The reclassification is a pure step function of `wValidBitsPerSample`, exact on this host
over the full u16 range (39 variants, all `act`-routed, single field at offset 38 changed on
the deterministic `pair_route_84` base — `s_valid_00017.wav` is byte-identical to it):

```
valid bits     ffmpeg codec   width  packets (B)          sox samples   law
0              pcm_s16le      2      8192+3328            5,760         field ignored (bps=0 keeps container 16)
1–8            pcm_u8         1      4096+4096+3328       11,520        4096/1+4096/1+3328/1
9–16           pcm_s16le      2      8192+3328            5,760         4096+1664
17–24          pcm_s24le      3      8192+3328            3,839         2730+1109 (2 B+1 B dropped)
25–32          pcm_s32le      4      11520               2,880         single packet, %4=0
33–56          NONE           —      demux ok, no decoder FAIL exit 2   au 'premature EOF'
57–64          pcm_s64le      8      11520               1,440
65–65535       NONE           —                          FAIL exit 2   bps>64 guard
```

**Boundaries at 0|1, 8|9, 16|17, 24|25, 32|33, 56|57, 64|65** — every one crossed and
confirmed on both sides. `pred_count` (Σ⌊packet/width⌋) == observed SoX sample count on all
decodable rows (`runs/sweep.tsv`). The map is **non-monotone**: codec NONE in 33–56, then
`pcm_s64le` *reappears* at 57 — the surprise boundary.

Source of the steps (n9.0.1 `lavf_utils.c:157-198`, cited copy in r62-boundary/src):
`ff_get_pcm_codec_id(bps, flt=0, be=0, sflags=~1)` — `bps<=0||bps>64 → NONE`; else
`w=(bps+7)>>3`; `sflags & (1<<(w-1))` selects signed. **Note the sflags subtlety**: `~1` =
`0xFFFFFFFE` — bit 0 is *clear*, so width-1 lands in the **unsigned** branch → `pcm_u8`,
not s8 (verified: ffprobe `codec_name=pcm_u8`). w∈{5,6,7} have no case → NONE;
w=8 → `pcm_s64le`; w>8 unreachable (`bps>64` guard). Packet widths come from the codec's
recomputed bitrate via `ff_pcm_default_packet_size` (`pcm.c:29-55`): u8→4,096 B,
s16/s24→8,192 B, s32→16,384 B, s64→32,768 B max_size — hence the packet column above.
AU intermediary is uniform across widths: `.snd`, offset 32, size `0xffffffff`, **encoding 3
(s16be)**, 48 kHz mono — SoX's count is always payload/2 (`runs/au-headers.txt`).

### Landed boundary-family pairs (tracked, `corpus/live/r64-boundary/`)

| pair | valid | act-route result | native `-t wav` | purpose |
|---|---|---|---|---|
| `pair_step_24.wav` / `pair_step_25.wav` | 24 / 25 | s24le → **3,839** / s32le → **2,880** | both FAIL valid-bits | canonical interior width step (17–24 \| 25–32) |
| `pair_step_56.wav` / `pair_step_57.wav` | 56 / 57 | FAIL `premature EOF` / s64le → **1,440** | both FAIL valid-bits | the non-monotone NONE→s64le resurrection boundary |

Each member differs from `pair_route_84` only at offset 38 (`wValidBitsPerSample`), byte
256 stays `0x84` → identical act route; SHAs in `runs/pair-verify.txt` /
`measurement-log.txt`.

## Recon (a): stdin — same 257-byte detection, but the ffmpeg bridge dies two different ways

`open_read` (formats.c:880-911) puts `stdin` in `ft->fp` for `-`, then runs the **same**
`auto_detect_format` → `lsx_readbuf_rewind(ft, data, 257)` — same buffer size, same CHECK
table, same `act` predicate. Observed: `cat pair_route_00 | sox -` detects `wav` (native
valid-bits fail); `cat pair_route_84 | sox -` detects `act`. Detection on stdin is
identical — what diverges is everything after it, split on `ft->seekable`:

- **Pipe stdin** (`cat f | sox -`): non-seekable → detection's 257 bytes are stashed in
  `pending_buffer` (formats_i.c:201-209); `startread_ffmpeg` sees `"-"` + `!seekable` →
  **forks a regurgitation child** (ffmpeg.c:52-91) that re-feeds pending + the rest of stdin
  into a fresh pipe dup2'd onto fd 0. strace: the child pushed all **11,588 B**, ffmpeg's
  `dup(0)` input read = 11,588 B, it decoded and wrote `.snd`+32 B — into a pipe whose read
  end SoX had already closed (`write = -1 EPIPE`, `SIGPIPE`, exit 224).
  **Why SoX died first:** the regurgitation child drains `pending` only in its *private*
  copy; the parent's `ft->pending_count` is still 257 when `ft->fp` is swapped to the popen
  stream (ffmpeg.c:101). au's first `lsx_readchars(4)` takes pending-first
  (formats_i.c:104-113) → gets `"RIFF"` → `can't find Sun/NeXT/DEC identifier` → dies →
  `xfclose` → EPIPE kills ffmpeg. Terminal error: **`can't find Sun/NeXT/DEC identifier`**,
  exit 2 — the file's own bytes poisoned the pipe reader.
- **File/seekable stdin** (`sox - < f`): seekable → `rewind()` path, no pending buffer, no
  fork. stdio had prefetched 4,096 B; `rewind()` is an in-buffer logical seek — glibc leaves
  fd 0 at the buffer-window end (traced `lseek(0,4096,SEEK_SET)`). ffmpeg `dup(0)` inherits
  offset 4096 → reads only the **7,492-byte** tail (no RIFF header) → probe fails → zero
  stdout → au `premature EOF`, exit 2. ffmpeg.c:52's comment *"if stdin comes from a file,
  ffmpeg rewinds it anyway"* is **false on n9.0.1** — the child issued no seek on its input.
- **Controls (decisive):** `cat f | sox -t act -` and `sox -t act - < f` both decode
  **3,839** — forcing the handler skips detection → no prefetch → neither failure mode.
  So: same detection buffer/predicate (YES), but `stdin + autodetect + ffmpeg-route` is a
  dead combination on this build; only `-t` saves it.

## Recon (b): `goto error` no-fallback — terminal ordering is exact

Constructed act-triggered files ffmpeg cannot even demux (`nf_zeros`: RIFF+WAVE+512 zero
bytes; `nf_chunk`: bogus `JUNK` chunk, no `fmt `), `0x84`@256 kept. Terminal sequence
(-V6, verbatim): `INFO formats: detected file format type 'act'` →
`FAIL formats: can't open input file 'X': premature EOF`, exit 2. **No** `au: found .snd`
line — the au reader died on the first 4-byte magic read of an *empty* pipe; the `FAIL` line
is `open_read`'s wrapper (formats.c:962) around the au reader's `sox_errstr`. ffmpeg's
own diagnostics (`no 'fmt ' or 'XMA2' tag found`, `Error opening input`, exit 183) never
surface. The indistinguishable-failure set is now four members deep: demux-open failure,
missing decoder (valid 33–56, 65+), missing binary (r63), truncated child input (stdin-file
case) — **all** → `premature EOF`, exit 2, zero fallback, zero second detection.

## Recon (c): no second autodetect on the pipe — au claims it unconditionally

PATH-stub `ffmpeg` (`execvp`-resolved, argv logged verbatim — `-nostdin -strict -2 -i <f> -f au -`)
emitting controlled pipe bytes while SoX reads the real `pair_route_84.wav`:

| pipe payload | au outcome |
|---|---|
| valid `.snd` (enc 3, 1000 B) | `found .snd`, decodes **500** samples — *input file content irrelevant* |
| **valid WAV file bytes** | `can't find Sun/NeXT/DEC identifier` — *no re-detection to wav* |
| junk | same wrong-magic fail |
| empty | `premature EOF` |
| `.snd` + 8 B only | `found .snd` **then** `premature EOF` (header-word read) |

`startread_ffmpeg` tail-calls `lsx_au_format_fn()->startread` unconditionally
(ffmpeg.c:107) — the au reader's own 4-magic check is the only gate on the pipe; a valid wav
streamed through it is refused. The input file's bytes never reach the au reader at all.
Input-side corollary: `act`'s `RIFF`@0 and `au`'s `.snd`@0 are mutually exclusive — no file
can satisfy both; only *pre-act* CHECKs can preempt an otherwise act-bound file
(`gsrt` `ring.bin\x00`@16, `hcom` `FSSD`@65+`HCOM`@128 — r63 demonstrated the hcom reroute).

## Boundary disclosures (new, measured)

- **Pending-buffer poisoning on stdin:** `startread_ffmpeg` replaces `ft->fp` but never
  clears `ft->pending_count`; on non-seekable stdin the au reader consumes the 257-byte
  detection prefetch ("RIFF…") as ffmpeg output → wrong-magic fail → SIGPIPE kill. The
  regurgitation fork itself is correct (ffmpeg received all 11,588 B).
- **fd-offset leak on seekable stdin:** the stdio prefetch (4 KiB) is never rewound at the
  kernel level; ffmpeg's `dup(0)` reads from offset 4,096. `-nostdin` does NOT redirect fd 0
  to /dev/null when `-` is an input — ffmpeg genuinely tried to decode the tail.
- **Width-1 bucket is unsigned:** `sflags=~1` has bit 0 clear → `pcm_u8`, not `pcm_s8`
  (r62's "u8" annotation confirmed mechanistically).
- **ffmpeg's stderr/exit code never propagates:** all bridge failures converge on the au
  reader's `premature EOF` (empty pipe) or `can't find Sun/NeXT/DEC identifier` (non-au
  bytes); child's exit status unobservable (r63's `fclose`-not-`pclose` finding).

## Residual UNKNOWNs / eliminated hypotheses

- **non-USING_FFMPEG build**: still unverifiable on this host (no such binary). Source-level
  only: `AUTO_DETECT_SIZE` drops to 132 and the `act` CHECK compiles out (formats.c:61-63,
  93-94) → these fixtures would detect `wav` → native valid-bits refusal. Untested —
  inference.
- Eliminated: "stdin uses a different/detect-less path" (same 257-byte buffer + table);
  "SoX retries a second reader when the pipe fails" (single `startread`, `goto error`;
  pipe-side stub proves fixed au tail-call); "ffmpeg rewinds seekable stdin" (n9.0.1 doesn't);
  "the ffmpeg child's exit/stderr reaches SoX" (four failure modes → identical terminal).

## Confidence

**High.** Step map: 39-value empirical sweep with per-row codec (ffprobe), packet list,
predicted-vs-observed counts — every boundary crossed on both sides, source-cited to n9.0.1
`lavf_utils.c`. Stdin findings: strace-level fd evidence (dup/dup2/lseek/read counts) plus
discriminating `-t` controls. Pipe-claim: controlled-byte stub with logged argv. The one
inference flagged: the glibc-internal reason `rewind()` leaves fd 0 at 4096 (in-buffer
short-seek normalization — mechanism detail; the observable offset is direct evidence).

## Receipts / artifacts (`.shokunin/audio/corpus/live/r64-boundary/`)

- `pair_step_{24,25,56,57}.wav` — landed boundary pairs (SHAs in `runs/pair-verify.txt`).
- `gen_sweep.py`, `run_sweep.sh`, `variants/` — 39 sweep fixtures + `sweep-shas.txt`.
- `runs/sweep.tsv` — full sweep table; `runs/measurement-log.txt` — consolidated log;
  `runs/{recon-a-stdin,recon-b-nofallback,recon-c-second-detect}.txt` — recon logs;
  `runs/{strace-stdin-pipe,strace-stdin-file,strace-stdin-file2}.txt` — syscall traces;
  `runs/stub-bin/ffmpeg` + `payload_*.bin` + `stub-argv.log` — pipe-contract rig;
  `runs/au-headers.txt`, `au_v*.bin` — AU intermediary captures;
  `runs/{nf_zeros,nf_chunk,pair56}-*stderr.txt`, `probe-none-s64.txt` — ffmpeg diagnostics.
