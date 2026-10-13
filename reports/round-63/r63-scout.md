# r63 — scout — audio lane — depth

Move: map the SoX_ng 14.8.0.1 `act` autodetect path on this host — the fixture
fragility r62 disclosed (payload byte 256 = `0x84` → detected `act` → ffmpeg
bridge → 3,839-sample decode of `pair_valid_17.wav`).

Seat: scout (recon only). Writes this report plus scratch under
`corpus/live/r63-scout/`. No source edits, no commits.

## Verdict

**Predicate pinned, on this host's binary and empirically.**

`act` fires iff **readable length > 256 && bytes[0..3] == "RIFF" &&
bytes[256] == 0x84**. Nothing else is examined: WAVE@8 is *not* part of the
predicate, position is exactly 256 (±1 byte kills it), value is exactly `0x84`
(`0x83`, `0x85`, `0xff` all miss). The declared claim — a specific byte
predicate at/near offset 256 — is confirmed at offset **256 exactly**, with a
RIFF-magic conjunct r62 did not state.

## Where act looks — binary-level map (`/usr/lib/libsox_ng.so.3.0.0`)

`auto_detect_format` @ `0x1a290` (disasm: `objdump -d -M intel`):

| addr | instruction | meaning |
|---|---|---|
| `0x1a291` | `mov edx,0x101` | reads **257 bytes** (upstream `AUTO_DETECT_SIZE 257 /* for act */`) into stack buf `[rbp-0x120]`; `rcx` = bytes read |
| `0x1aa76` | `cmp rcx,0x100 / jbe` | act check requires **>256 bytes readable** (file must offer ≥257 B; `cmp rcx,0x83`+`jbe` above is the earlier hcom gate pattern) |
| `0x1aa7f` | `cmp BYTE [rbp-0x20],0x84` | `buf[0x100]` = **file offset 256 == 0x84** (buffer base `rbp-0x120` + `0x100`) |
| `0x1aa83` | `je 0x1b2a6` | → `mov r8d,[rbp-0x120]; cmp r8d,0x46464952` = `"RIFF"@0` |
| `0x1b2b4` | `je 0x1b46e` → `lea rdi,[0xb836f]` | string at `0xb836f` = **`"act"`** → `jmp 0x1a670` detect tail (`detected file format type 'act'`) |

wav's own probe (for contrast): `cmp eax,0x45564157` (`"WAVE"`@8-11) +
`"RIFF"`/`"RIFX"`@0 (`0x1aa90`–`0x1ab27`). Machine order runs the act branch
before wav selection — consistent with upstream `formats.c` `CHECK(act,
0,4,"RIFF", 256,1,"\x84")` preceding `CHECK(wav,...)`, comment "Must come
before wav because it looks like a PCM WAV file" (r62-scout, codeberg read).

## act IS the ffmpeg bridge — no native act decoder

- `nm -D`: `lsx_act_format_fn` exported @ `0x35cb0`. Its body tail-calls
  **`lsx_ffmpeg_format_fn`** via GOT (`call [rip+0xa3bc2] → lsx_ffmpeg_format_fn@@Base`),
  copies the returned 0x70-byte handler struct into static `handler.83`, then
  repatches the name pointer to `names.82` @ `0xd3590` (first ptr → `"act"`).
  The act "handler" is ffmpeg's, re-labelled.
- `sox --help-format act` → `Format: ffmpeg` / `Pseudo format to use ffmpeg` /
  `Also handles: ... act ...` — the type name resolves to the ffmpeg pseudo.
- `/usr/share/doc/sox/ChangeLog`: "Add ffmpeg's 'aa', 'ea' and 'act' formats";
  `README`: "ACT files (G729A speech compression)". act exists upstream so real
  G729A voice-recorder files (RIFF-like) reach ffmpeg; the `0x84`@256 byte is
  the discriminator that separates them from PCM WAV.
- ChangeLog also: "Fail autodetection of some ffmpeg formats if the file is
  truncated" — the `rcx > 0x100` guard observed.

**Correction to r62-scout's phrasing:** there is no "act open fails → handler
fallback → ffmpeg" chain. Detected `act` *is* the ffmpeg handler; its
`startread` pipes `ffmpeg -loglevel quiet -nostdin -strict -2 -i <file> -f au -`
and the `sox INFO au: found big-endian '.snd' identifier` line is **nested
detection of the child's .snd pipe output**, not a competing probe of the
input file (r62-boundary had this right). Detected-handler failure is
terminal: `wavex_84.wav` detected `act`, ffmpeg couldn't demux `XAVE`, SoX
exited `premature EOF` — no retry of `wav` despite the extension.

## Routing signatures — `sox --i`

| file | byte[256] | `Input File` suffix | Duration line | exit |
|---|---|---|---|---|
| `round-61/pair_valid_17.wav` | `84` | **`(ffmpeg)`** | **absent** | 0 |
| `round-61/pair_valid_16.wav` | `84` | **`(ffmpeg)`** | absent | 0 |
| `round-62/pair_valid_24.wav` | `84` | **`(ffmpeg)`** | absent | 0 |
| `round-62/pair_valid_32.wav` | `84` | **`(ffmpeg)`** | absent | 0 |
| `round-60/pair_valid_16.wav` | `78` | (none) | `00:00:00.12 = 5760 samples` | 0 |

The `(ffmpeg)` suffix + **missing** `Duration`/`File Size`/`Bit Rate` lines =
bridge route (the au intermediary advertises size `0xffffffff`, r62-boundary).
Native route = no suffix + Duration present. All four above-range pair files
(17/16/24/32) carry `0x84`@256 — all four ride the bridge on this host.

## Exact commands that distinguish routing

```sh
od -A d -t x1 -j 256 -N 1 <file>                      # trigger byte (expect 84)
sox -V4 <file> -t f32 - 2>&1 | grep 'detected file format type'  # 'act' vs 'wav'
sox --i <file> | grep 'Input File'                    # '(ffmpeg)' suffix = bridge
sox --i <file> | grep Duration                        # present = native, absent = bridge
sox -t wav    <file> -t f32 - >/dev/null              # force native (v17 → fatal:
                                                      #  'number of valid bits exceeds
                                                      #   the number of bits per sample')
sox -t act    <file> -t f32 - >/dev/null              # force bridge w/o trigger byte
sox -t ffmpeg <file> -t f32 - >/dev/null              # same pipe, explicit name
ffprobe -v error -show_entries stream=codec_name -of csv=p=0 <file>
                                                    # downstream: pcm_s24le (v17) vs pcm_s16le (v16)
```

Verified this round: `sox -t act probes/b256_00.wav …` (byte 256 = `0x00`)
still routes `(ffmpeg)` — forcing bypasses autodetect entirely. `sox --magic`
on `pair_valid_17.wav` still detects `act` — libmagic changes nothing here.

## Probe matrix (scratch `corpus/live/r63-scout/probes/`, base = `pair_valid_16.wav`)

Full log: `corpus/live/r63-scout/runs/probe-matrix.txt`. Route column marked
"native" for open-failures means no `(ffmpeg)` suffix printed — open failed,
so routing is moot; the `detect=` column is the signal.

| probe | change vs base | detected | outcome |
|---|---|---|---|
| `b256_00.wav` | 256: 84→00 | `wav` | native open ok |
| `b255_84.wav` | 255←84, 256←00 | `wav` | position 255 inert |
| `b257_84.wav` | 256←00, 257←84 | `wav` | position 257 inert |
| `b300_84.wav` | 256←00, 300←84 | `wav` | deeper payload inert |
| `b256_83.wav` / `_85` / `_ff` | 256←83/85/ff | `wav` | value-specific: only `0x84` |
| `riffx_84.wav` | `RIFF`→`XIFF`, keep 84@256 | *none* | ext-fallback → wav → `RIFF header not found` (RIFF@0 is a conjunct) |
| `wavex_84.wav` | `WAVE`→`XAVE`, keep 84@256 | **`act`** | ffmpeg fails `premature EOF`; terminal — **WAVE@8 not required** |
| `wavex_00.wav` | `XAVE`, 256←00 | *none* | ext-fallback → wav → `header not found` |
| `trunc256.wav` | file = 256 B | `wav` | act skipped (needs ≥257 readable B); soxi still prints declared Duration 5760 |
| `renamed.bin` | none (extension removed) | `act` | `(ffmpeg)` — content-based, extension-independent |
| `v17_b256_00.wav` | v17 file, 256←00 | `wav` | native fmt parse → `number of valid bits exceeds the number of bits per sample` (r62 fatal reproduced) |

## Host/source availability

- `pacman -Q sox` = `14.8.0.1-1`; `pacman -Si` URL `codeberg.org/sox_ng/sox_ng`;
  binary package only — `/usr/bin/sox`, `libsox_ng.so.3.0.0`, headers, man,
  doc = `AUTHORS ChangeLog README`. **No source ships**; upstream reference is
  codeberg (r62-scout read `src/formats.c` there). This report's binary disasm
  is this-host evidence for the same predicate.
- ffmpeg `2:9.0.1-4`. Disasm labels (`auto_detect_format`, `names.82`,
  `handler.83`) resolve via dynsym + `.gnu_debuglink`-style metadata.

## Hand-off notes for the sweep-matrix seat

- Predicate is a **two-point conjunction**: `RIFF`@0-3 AND `0x84`@256. Bytes
  4–255 are unexamined; byte 256 is payload byte 188 (data-chunk interior) in
  this file family — the collision surface is payload content, not headers.
- Sufficient matrix: positions {0..3 → RIFF conjunct}, {248..264 neighbourhood},
  {256 full 0x00–0xff value sweep}; file-family cells across
  round-{57..62} pair files (all share the 11,520-B payload / header shape).
- Deterministic levers already proven: `-t wav` (native, fails on valid-bits
  >16), `-t act`/`-t ffmpeg` (bridge, byte-256-independent). Extension rename
  does not alter detection; truncation below 257 B disables the act check only.
- `--magic` is not a lever (same `act` result).

## Facts vs inference

Facts: every disasm address/instruction, string address, `soxi` suffix/Duration
asymmetry, probe outcomes, exit codes above — all observed this round on this
host. Inference: correspondence of the compiled branch tree to upstream
`CHECK(act,0,4,"RIFF",256,1,"\x84")` (r62-scout's codeberg citation; not
re-fetched this round — no network fetch performed, evidence is binary+empirical).
Remaining bounded unknown: whether `auto_detect_format`'s 257-byte window is
sized *only* for act or shared by another probe (upstream comment says
"for act"; binary shows the deepest compare at 0x100 — consistent, not exhaustively
audited across all ~40 probes in the function).

## Receipts / artifacts

- `corpus/live/r63-scout/probes/` — 12 single-field fixtures + `renamed.bin`.
- `corpus/live/r63-scout/runs/probe-matrix.txt` — detection/route/fail log.
- All commands verbatim in body; base fixture `corpus/live/round-61/
  pair_valid_{16,17}.wav` (sha `2c5e244f…` / `15cadf24…` per r62).
