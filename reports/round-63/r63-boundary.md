# Round 63 — boundary (revenger): the `act`→ffmpeg→au dispatch ordering — no fallback exists

Seat: **revenger** — reconstruct host behavior from executable evidence. Scope: resolve the
surface r62 left flagged-inference — *once a file is `act`-routed, what runs, and does SoX
ever fall back to a native reader when the ffmpeg bridge fails?* Plus: map other autodetect
formats for payload-collision offsets inside a RIFF/WAVE file. Host: Arch Linux,
`sox` = SoX_ng 14.8.0.1 (`/usr/lib/libsox_ng.so.3`), `ffmpeg`/`ffprobe` = n9.0.1.
All work scratch-only in `.shokunin/audio/corpus/live/r63-boundary/`; sox_ng-14.8.0.1
source fetched to `src/` for citation (codeberg release tarball, sha of tree inspected).

## Verdict: ordering fully established — single dispatch, zero fallback, no native `act` reader

The r62 flagged inference is resolved **against** the fallback reading. Three independent
evidence classes converge on the same model:

1. **Source:** `open_read` (formats.c:855–994) calls `auto_detect_format` once, gets **one**
   type string (the CHECK macro `return #type`s on the first match, formats.c:71–72),
   looks up **one** handler via `sox_find_format`, calls **one** `startread`
   (formats.c:961). Failure → `lsx_fail` → `goto error` → NULL. There is no candidate
   list, no retry loop, no second handler anywhere on the open path. If autodetect finds
   nothing, the only secondary mechanism is filename→extension lookup (formats.c:925–932);
   libmagic is compiled in but `use_magic` defaults `sox_false` (libsox_ng.c:134).
2. **Binary:** `nm -D libsox_ng.so.3` shows `lsx_act_format_fn` at `0x35cb0`, inside the
   contiguous ffmpeg-pseudo-handler block (`lsx_ffmpeg_format_fn` `0x32da0` … `0x36xxx`),
   far from the native-handler region (`lsx_au_format_fn` `0x6e0f0`, `lsx_wav_format_fn`
   `0x84340`, `lsx_gsrt_format_fn` `0x6e310`, `lsx_hcom_format_fn` `0x79a60`). Its disasm
   is the verbatim codegen of `FFMPEG_FORMAT(act)`: `call lsx_ffmpeg_format_fn`, nine
   movdqu/movaps copies of the returned ~144-byte handler struct into a static, patch in
   `names[]={"act"}`. There is **no `lsx_act*read`** symbol — no native act reader exists
   to "try first". `strings` shows act's only payload: the description `"G729A speech
   compression"`.
3. **Behavior:** the error-string provenance experiments below show the same file reaches
   different readers only when the *detect-time bytes* change — never when the first
   reader fails.

So the chain is:

```
open_read -> readbuf_rewind(≤257 B) -> auto_detect_format (first CHECK match wins)
   "act" -> sox_find_format("act") -> GENERIC ffmpeg pseudo-handler
        (no FORMAT(act) in formats.h; "act" is a member of names[] at ffmpeg.c:116)
   -> startread_ffmpeg (ffmpeg.c:33): popen `ffmpeg -loglevel quiet -nostdin
        -strict -2 -i <file> -f au -`
   -> tail-call lsx_au_format_fn()->startread(ft)  on the PIPE (ffmpeg.c:101–107)
   -> au reader parses the .snd stream produced by the ffmpeg child
```

`-V6` shows the chain directly: `sox INFO formats: detected file format type 'act'`
immediately followed by `sox INFO au: found big-endian '.snd' identifier` — the format
layer never sees WAV bytes; it sees an AU stream. `strace -f -e execve` captures the
child exec verbatim matching ffmpeg.c:35–44. The `(ffmpeg)` suffix in `--i` output is
`handler.names[0]=="ffmpeg"` printed because the `.wav` extension isn't among the
handler's names (sox_ng.c:418–424).

## Experiment matrix — what happens once `act`-routed

All variants are byte-edited copies of the r61 pair (SHAs verified:
`pair_valid_16.wav` `2c5e244f…`, `pair_valid_17.wav` `15cadf24…`); construction and
per-variant SHAs in `runs/variant-shas.txt`. `stat` output trimmed; exits captured
separately (open failure → exit 2).

| variant | bytes changed | detected | outcome | reader that produced it |
|---|---|---|---|---|
| `pair_valid_17` | — (0x84@256) | `act` | **3,839** samples, exit 0 | ffmpeg→au |
| `pair_valid_16` | — (0x84@256) | `act` | 5,760 samples, exit 0 | ffmpeg→au — **both r61 files were always act-routed** |
| `v1` | WAVE@8→`XXXX` (RIFF kept) | `act` | FAIL `premature EOF` exit 2 | au reader, empty pipe |
| `v2` | wFormatTag→0x1234 (0x84 kept) | `act` | FAIL `premature EOF` exit 2 | au reader, empty pipe |
| `v3` | v2 + byte256→0x00 | `wav` | FAIL `file encoding 0x1234 (Unknown) is not supported` exit 2 | **native wav** (wav.c:773) |
| `v4` | truncate to 300 B | `act` | **77** samples, exit 0 | ffmpeg→au (232 B → s24le, 1 B residue) |
| `v9` | truncate to 500 B | `act` | 144 samples, exit 0 | ffmpeg→au |
| `v10` | data-size field→0 | `act` | **3,839**, exit 0 | ffmpeg **ignores declared data-size 0**, reads to EOF |
| `v10b` | v10 + byte256→0x00 | `wav` | FAIL `number of valid bits exceeds…` exit 2 | native fmt-guard fires before data |
| `v8` | header-only 68 B | `wav` | FAIL valid-bits exit 2 | **act needs len≥257** (AUTO_DETECT_SIZE) |
| `v5` | `FSSD`@65 + `HCOM`@128 | `hcom` | FAIL `bad compression type` exit 2 | **native hcom** (hcom.c:132) |
| `v6` | `ring.bin\x00`@16 | `gsrt` | FAIL `premature EOF` exit 2 | **native gsrt** |
| `v7` | pair_valid_16, byte256→0 | `wav` | 5,760, exit 0 | native wav |
| ffmpeg absent (`PATH=/tmp/noff`) | — | `act` | FAIL `premature EOF` exit 2 | indistinguishable from undecodable input |

**Decisive pair: v2 vs v3.** Identical bytes except offset 256. With the trigger, the
terminal error is the au reader's generic `premature EOF` (formats_i.c:572/588 — the
first `lsx_readchars(magic,4)` on an empty pipe); without it, the terminal error is the
native wav reader's `file encoding 0x1234 … is not supported` (wav.c:773). ffmpeg on v2
demuxed the WAV fine but found `Audio: none (…/0x1234): unknown codec` → zero bytes on
stdout → au dies. If a failure-driven fallback to native wav existed, v2 would show
wav.c:773's error (or succeed): it shows neither. The ffmpeg child's stderr/exit status
is invisible to SoX — direct reproductions emit ffmpeg diagnostics (`Invalid data`,
`Could not find codec parameters`) that never surface in sox's output, and with ffmpeg
absent from PATH the identical `premature EOF` results: **the byte stream is the whole
contract; a missing decoder, a demux failure, and a missing binary are indistinguishable.**

**"Premature EOF" provenance (r62 open point):** the string is *not* the wav reader's —
wav.c's own warn is the longer `premature EOF on input file` (wav.c:131/172/1504). The
short `premature EOF` is formats_i.c's generic read-helper fail set on `ft->sox_errstr`
when any `lsx_read*` hits EOF. On the act path it is the **au reader** reporting an
empty ffmpeg pipe; r62's "premature EOF after ffmpeg fallback fails" was the au
reader's death inside `startread_ffmpeg`'s tail call, after which `open_read` dies —
no fallback ever ran.

**Position/value exactness of the act predicate** (supports the lane's declared claim):

- Offset: `0x84` at 255 → `wav`; at 256 → `act`; at 257 → `wav`. Exactly offset 256.
- Value @256 on the native-decodable v16 base: `0x00`/`0x83`/`0x85`/`0xff` → `wav`;
  only `0x84` → `act`. Exactly `0x84`.
- `RIFF`@0 is required: `XFFX`+`0x84`@256 → no CHECK match → extension `.wav` →
  native reader → `RIFF header not found` (wav.c:821).
- Length floor: ≥257 B (`AUTO_DETECT_SIZE 257 /* for act */`, formats.c:61); the
  68-byte header-only file detects `wav`.
- The second predicate is `"RIFF"@0`, **not** `WAVE`@8 → *every* RIFF container is
  capturable: `RIFF`+`AVI `+`0x84`@256 → `detected 'act'` → `premature EOF`
  (avi demuxer can't parse the wav payload; a real AVI with `0x84`@256 would also
  take this route — harmless in practice since ffmpeg reads AVI, but the type tag
  would be wrong).

## Other formats' collision surfaces inside a RIFF/WAVE file

First-match-wins means only CHECKs **before** `wav` (formats.c:95) can preempt, and
their predicates must be compatible with `RIFF`@0/`WAVE`@8. The reachable set is
exactly:

| offsets | predicate | detects as | handler | notes |
|---|---|---|---|---|
| 16–24 | `ring.bin` + NUL (9 B) | `gsrt` | native | overwrites fmt size/tag/channels/rate-LSB in a fmt@12 WAV; the CHECK's `l1=9` **includes the C literal's terminating `\x00`** — 8 visible bytes + NUL |
| 65–68 + 128–131 | `FSSD` + `HCOM` | `hcom` | native | for this fmt40 layout offset 65 sits in the data-chunk size field, 128 in payload — both are content bytes |
| 256 | `0x84` | `act` | ffmpeg pseudo | payload byte in all standard layouts |
| 0–3 + 8–11 | `RIFF`/`RIFX`/`RF64` + `WAVE` | `wav` | native | the intended match |

Negative results (eliminated hypotheses):

- **`vms`/`dvms` have no autodetect predicate at all** — `dvms-fmt.c:22` names
  `{"dvms","vms"}`; no CHECK line exists, so they can only be reached by filename
  extension. No payload offset collides.
- **`8svx`** needs `FORM`@0 + `8SVX`@8 — both fixed magics contradict RIFF/WAVE.
  Same for every FORM-family type (aiff/aifc/maud/nsp) and every @0-magic type
  (xa, au, flac, avr, caf, wv, paf, pcm/MSU1, sf, sox, mp3, mp2, voc, smp, wve,
  amr-*, prc, sph, txw, sndt, vorbis, opus, dff, dsf, wsd, sds, mpc2k): unreachable
  on a RIFF file. All post-wav CHECKs (avi, mkv, mov, mpeg, …) are unreachable by
  definition — wav always matches first.

## Boundary disclosures (new, measured)

- **ffmpeg child exit status is never consulted.** `startread_ffmpeg` replaces
  `ft->fp` with the popen stream but leaves `ft->io_type = lsx_io_file`, so the close
  path uses `fclose`, never `pclose`/waitpid (formats.c:557–561, 1498–1499). ffmpeg's
  failure mode is observable only as missing/short AU bytes.
- **One fd leaks per act-routed open:** `open_read` keeps the real file's `FILE*`
  open because the ffmpeg handler lacks `SOX_FILE_NOSTDIO` (it inherits au's flags
  `SOX_FILE_BIG_END|SOX_FILE_REWIND`, au.c:231, ffmpeg.c:131); `startread_ffmpeg`
  then overwrites `ft->fp` (ffmpeg.c:101) without closing it.
- **The s16le detour is bit-exact:** `sox -t act v7.wav -t f32` vs native
  `sox v7.wav -t f32` → 23,040 B each, `max|Δ| = 0.0`, 0/5,760 diffs. The r62
  one-frame loss is specific to frame widths that don't divide the 8,192/3,328-B
  packets (s24le only: 8,192%3=2, 3,328%3=1); u8/s16/s32/s64 packets are
  residue-free (r62 table consistent: valid25–32 → 2,880 exact, valid63–64 →
  1,440 exact). Prior rounds that compared "native vs SoX decode" on the r61 pair
  were unknowingly comparing **two ffmpeg-path decodes** — harmless for s16le
  (bit-exact) but the confound is now bounded, not just disclosed.
- **Truncated files decode partially on the act path** (v4: 77 samples from 300 B,
  v9: 144 from 500 B) where the native reader would warn `premature EOF on input
  file` and decode by its own rules — different short-input semantics per route.
- **Forced types bypass detection entirely** (`-t wav` on the act file → native
  valid-bits refusal; `-t act`/`-t ffmpeg` on a non-trigger file → 5,760 via the
  pipe), confirming `-t` skips `auto_detect_format` (formats.c:871–877).

## Answer to the seat question, verbatim

*Once a file is act-routed, what happens — does SoX's own act reader try first and
fail (then ffmpeg bridge), or does ffmpeg get it directly?* **ffmpeg gets it
directly and exclusively.** There is no native act reader: `lsx_act_format_fn`
either resolves to the generic ffmpeg pseudo-handler (static build: `"act"` is in
`names[]` at ffmpeg.c:116 — `sox_find_format` first-match, formats.c:1818–1826) or
to a verbatim clone of it (the `FFMPEG_FORMAT(act)` stub, disasm-proven). The
handler's `startread` popens the ffmpeg child and hands the pipe to the **au**
reader; on any pipe-level failure `open_read` dies with the au reader's error —
it never consults another handler. What r62 recorded as fallback-like behavior
(native wav engaging after byte-256 edits) is the **detector** choosing a
different first match, not the runtime recovering.

## Residual scope limits

- Exact for this host's SoX_ng 14.8.0.1 + ffmpeg n9.0.1, static-handler build
  (no `libsox_ng_fmt_*` plugins installed — plugin path would register the
  per-name stubs via ltdl, formats.c:1682–1741, same semantics).
- `use_magic`/`--magic` path unexercised (off by default; libmagic MIME strings
  would be looked up as format names — different resolution, not fallback).
- Collision map covers the compiled-in CHECK table only; dynamic plugin formats
  could add predicates (none installed here).
- The hcom/gsrt detours were demonstrated as *detection* reroutes; their readers'
  failure modes are incidental, not mapped exhaustively.

## Confidence

**High.** Source-cited at line granularity on the exact installed version
(sox_ng-14.8.0.1 tarball), corroborated by dynamic-symbol geography + disasm of
the act stub, strace of the child argv, and a discriminating-fixture matrix where
error-string provenance (au `premature EOF` vs wav.c's named fails) proves which
reader produced each terminal error. The no-fallback claim rests on code absence
(single `startread`, `goto error`) *and* the v2/v3 divergence experiment.

## Receipts / artifacts

- `corpus/live/r63-boundary/runs/measurement-log.txt` — consolidated command/output log (sections A–J).
- `corpus/live/r63-boundary/runs/{v6-baseline,v6-matrix-1,v6-matrix-2,v6-detect,v6-forcing,strace-v17,disasm-act,variant-shas,sox-help-formats}.txt`, `v7_{native,actpath}.f32`.
- `corpus/live/r63-boundary/variants/` — 20 discriminating fixtures (`v1`–`v10b`, `p1`–`p5`, `s_256_*`).
- `corpus/live/r63-boundary/src/sox_ng/` — sox_ng-14.8.0.1 source tree (citation target).
