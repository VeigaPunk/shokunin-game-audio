# fa-sndfile — wave-11 frontier pre-measurement: libsndfile as third decoder

Seat: frontier-a (leaf). Lane: audio. Repo: `audio-shokunin`.
Decoder under test: **libsndfile 1.2.2-4** (`/usr/lib/libsndfile.so.1`,
`sf_version_string()` = `libsndfile-1.2.2`; tools: `/usr/bin/sndfile-info`,
`/usr/bin/sndfile-convert`, `/usr/bin/sndfile-deinterleave` — **no
`sndfile-convert-to-raw` on this host**). Baselines: sox committed receipts
(`corpus/live/runs/*-transport-*-r6[789]/measurements.json`, latest per mode)
and the r71 ffmpeg receipt
(`corpus/live/runs/20261014T140155796326Z-normal/measurements.json`,
`ffprobe_*_r71_probe` entries, ffmpeg n9.0.1).

## Headline

libsndfile is a **third, distinct detector** — it has BOTH a name axis and a
transport fork, but a much narrower name axis than sox and a different
mechanism. Measured on the canonical 9-member r71 corpus plus the 4 round-66
lengate files, all four transports:

- **Name axis: YES, post-sniff fallback only.** When content sniffing finds
  no magic, `sf_open` falls back to the filename extension — but only for a
  tiny raw-family set. Measured set on a 56-extension sweep of identical
  no-magic bytes: **`.au`/`.snd` → RAW|U-Law, `.gsm` → RAW|GSM610,
  `.vox` → RAW|VOX_ADPCM** — all 8 kHz mono, all DECODE (500/2560/1024
  frames). Every other extension tried (incl. `.wav`, `.aif`, `.f32`,
  `.txw`, `.raw`, `.ulaw`, `.bin`, `.sndr`, 40+ others) → `Format not
  recognised`. Content always wins over the fallback (RIFF bytes named
  `.snd`/`.au`/`.gsm`/`.vox` still open as WAV/PCM16). There is no ext→
  reader dispatch like sox's names[] table.
- **Transport fork: YES — the same named-vs-unnamed partition as sox's
  `.snd` sndr gate, on the same member.** `extsuffix_nomatch.snd` opens as
  RAW|U-Law on {file, fifo_path} (both carry the `.snd` name) and is
  rejected on {stdin_pipe, redirected_fd} via `sf_open_fd` (anonymous fd —
  no name at all). So sox and libsndfile both fork detection on the name
  for this member; ffmpeg does not (rejects all 4).
- **Content-accepted types are transport-invariant**, including unseekable
  pipe — the WAV members decode 278 frames on all four arms (sox decodes
  dec_act on `file` only; its act→ffmpeg bridge can't reopen pipes).
- **A verdict tier the other two lack**: `txw_piperefuse.wav` (LM8953) is
  magic-RECOGNIZED then refused — `File contains data in an unimplemented
  format` — vs `Format not recognised` for true no-match bytes. This
  build's format table (SFC_GET_FORMAT_MAJOR, 26 majors) contains **no
  TXW reader and no HCOM at all**; ffmpeg lacks both magic and decoder
  (uniform `Invalid data` reject); sox is the only one that decodes TXW.
- `sndfile-info` **exits 0 on every failure** — verdicts live in stdout
  text (`Error : Not able to open input file` + reason). `sndfile-convert`
  does propagate exit codes (exit 1 on reject, 0 on convert).

## 9-member × 3-decoder verdict table

Per-arm detection verdict; `=` means identical to `file`. sox cells:
`detected/exit/samples` (native route unless noted). ffmpeg cells:
`ffprobe_format/ffmpeg_exit`. libsndfile cells: `sf_open(+_fd)
format→frames read`, all opens that succeed also `sf_format_check`=true.

| member (path) | sox (committed receipt) | ffmpeg/ffprobe n9.0.1 (r71) | libsndfile 1.2.2 (this probe) |
|---|---|---|---|
| `dec_act` `round-66/pair_dec_act.wav` | det `act`→ffmpeg route; decode 278 **file only**; pipes `can't find Sun/NeXT/DEC identifier`, redir `premature EOF` — **fork** | `wav`/0 on all 4; decode ok — no fork | **WAV/PCM16, 278 fr on all 4** — no fork |
| `dec_hcom` `round-66/pair_dec_hcom.wav` | det `hcom`; decode 9 on all 4 — no fork | `hcom`/0 on all 4 — no fork | **WAV/PCM16, 278 fr on all 4** (labels the hcom-polyglot as WAV; no HCOM in build) — no fork |
| `posttable` `round-68/posttable_nomatch.wav` | reject all 4 (`RIFF header not found` named; `can't determine type` anonymous) | reject all 4 (`Invalid data found`) | reject all 4 `Format not recognised` |
| `txw_piperefuse` `round-68/txw_piperefuse.wav` | det `txw`; decode 64 on **seekable** {file, redirected_fd}; `input must be a file, not a pipe` on pipes — **fork** | reject all 4 | reject all 4 — **`unimplemented format` (LM8953 magic recognized, no reader compiled)** |
| `extsuffix_wav` `round-69/extsuffix_nomatch.wav` | reject all 4 (wav-reader verdict named / can't-determine anon) | reject all 4 | reject all 4 `Format not recognised` (no `.wav` fallback) |
| `extsuffix_bin` `round-69/extsuffix_nomatch.bin` | reject all 4 (`no handler for 'bin'` named) | reject all 4 | reject all 4 |
| `extsuffix_txw` `round-69/extsuffix_nomatch.txw` | reject all 4 (txw-reader verdicts by transport: `invalid filetype ID` file / `input must be a file` fifo / can't-determine anon) | reject all 4 | reject all 4 (no `.txw` fallback) |
| `extsuffix_f32` `round-69/extsuffix_nomatch.f32` | **decode 75, exit 0** on named arms; can't-determine anon — **fork** | reject all 4 | reject all 4 (no `.f32` fallback) |
| `extsuffix_snd` `round-69/extsuffix_nomatch.snd` | det `sndr` (ext-gated CHECK, bytes 0,1,7 zero) → decode 504 on named; can't-determine anon — **fork** | reject all 4 | **RAW|U-Law 8kHz, ~500 fr on {file,fifo_path}; `Format not recognised` on {stdin_pipe,redirected_fd}** — **fork, same partition** |

Supplementary round-66 lengate files (same RIFF-polyglot family, not in the
canonical 9): `pair_lengate_gsrt_{24,25}.wav` → libsndfile `Error in WAV
file. No 'data' chunk marker` on all 4 (sox: gsrt_24→det wav, gsrt_25→det
gsrt, both exit 2); `pair_lengate_hcom_{131,132}.wav` → libsndfile
WAV/PCM16 43/44 fr on all 4 (sox: 131→det wav, 132→det hcom, exit 0).

## What answers the wave-11 questions

**Suffix/name axis?** Yes — narrower than sox's, different kind. sox
dispatches extension→reader over its whole names[] table after the CHECK
table misses (and gates one CHECK row on `ext=="snd"`). libsndfile ignores
the name during content guessing, then applies a **fallback only on
no-match**, limited to four measured raw-family extensions
{`.au`,`.snd`→RAW|ULAW, `.gsm`→RAW|GSM610, `.vox`→RAW|VOX_ADPCM}. The
`.f32`-style successful-extension-dispatch class exists but the member set
is fixed and tiny. Extension case sensitivity: untested for the fallback
(sox's gate is strcasecmp; measure before relying).

**Transport fork?** Yes — but only through the name: `sf_open` sees the
basename (file AND fifo), `sf_open_fd` sees none. So the fork partition is
exactly {named arms} vs {anonymous arms} — identical shape to sox's sndr
gate and to every r69 member's sox partition. There is **no** seek-gate
internal split inside the named arm like sox's txw file-vs-fifo; WAV and
RAW|ULAW both stream fine from pipes. (`sfinfo.frames` reports
`INT64_MAX` on the fifo for RAW|ULAW — length unknown, verdict unchanged.)

**CHECK-table types accepted that ffmpeg rejects / vice versa.**
This corpus exercises sox's detected types {act, hcom, txw, sndr, gsrt,
wav}. ffmpeg accepts exactly {wav-content, hcom-content}; rejects all
else. libsndfile accepts {wav-content (incl. the hcom- and
"act"-polyglots, which it labels WAV/PCM16), and `.snd`-named no-magic
content as RAW|ULAW}. So:

- **libsndfile accepts, ffmpeg rejects**: `extsuffix_snd` on named arms
  (the name fallback — the single libsndfile-only acceptance here).
- **ffmpeg accepts, libsndfile rejects**: none in this corpus.
- **sox accepts, both others reject**: `txw` on seekable arms
  (libsndfile: recognized-but-unimplemented; ffmpeg: blind reject);
  `extsuffix_f32` named arms (sox-only raw-f32 reader dispatch).
- **All three accept**: `dec_act`, `dec_hcom` — but under three different
  detected labels: sox `act`(→ffmpeg) / `hcom`, ffprobe `wav` / `hcom`,
  libsndfile `wav` / `wav`. Detection-partition divergence, not
  acceptance divergence.
- **All three reject**: `posttable`, `extsuffix_{wav,bin,txw}`.

Net: libsndfile's acceptance partition ⊂ neither sox's nor ffmpeg's; it
adds a name-fallback acceptance class sox reaches by a different row and
ffmpeg lacks, and it uniquely separates "known magic, no reader" (txw)
from "no magic" — a third verdict tier for the receipts.

## Commands / exits (exactly as run)

```sh
cd ~/Projects/shokunin/audio-shokunin
# libsndfile matrix (all 4 arms via sf_open/sf_open_fd, ctypes):
python3 corpus/live/frontier-sndfile/probe_sndfile.py '{"dec_act":...}' \
  > corpus/live/frontier-sndfile/runs/sndfile-matrix.json   # exit 0
# CLI info leg (exit 0 even on reject — read stdout):
sndfile-info corpus/live/round-69/extsuffix_nomatch.snd     # exit 0, opens RAW|ULAW
sndfile-info corpus/live/round-68/posttable_nomatch.wav     # exit 0, "Error : Not able to open"
# decode leg:
sndfile-convert corpus/live/round-69/extsuffix_nomatch.snd /tmp/x.wav   # exit 0 (558B out)
sndfile-convert corpus/live/round-69/extsuffix_nomatch.f32 /tmp/x.wav   # exit 1 "Format not recognised."
```

Fifo legs: `mkfifo <name>; (cat member > fifo &); sf_open(fifo)` — same
protocol as r67/r71 (one-shot write + 1 s hold). Anonymous legs: genuine
`sf_open_fd(dup(fd))` — no `/dev/stdin` path tricks, so the name axis is
measured at the API boundary, not approximated.

## Gotchas for the wave-11 author

- `sndfile-info` never fails via exit code; `sndfile-convert` does
  (exit 1). For a third-decoder leg, drive `sf_open`/`sf_open_fd`
  directly (or parse sndfile-info stdout) — mirror the r71
  `ffprobe_leg` shape: detection = `SF_INFO.format` or `sf_strerror`,
  decode = `sf_readf_*` count.
- `.mp3` names trigger the mpg123 path: stderr noise (`Illegal
  Audio-MPEG-Header … resync`) and a distinct error (`File does not exist
  or is not a regular file (possibly a pipe?)`) — mpeg wants regular
  files; that path has its own transport behavior if ever probed.
- RAW fallback opens succeed where ffmpeg rejects → if wave-11 adds an
  ffmpeg-style "anonymous pipe can't determine" class, note libsndfile's
  anonymous arms lose only the name, not the content sniff (fd arms
  behave exactly like named arms for content-bearing members).
- The `.snd` fallback needs bytes that survive content sniffing
  unclaimed — the r69 member content qualifies; sox's sndr conjunct
  (bytes 0,1,7 zero) is unrelated and coincidentally satisfied by the
  same bytes. A `.snd`-named member whose bytes DO sniff (e.g. RIFF)
  opens as that format — content wins.

## Unresolved / limits

- Extension fallback was enumerated empirically (56 extensions), not from
  source; the definitive list lives in `format_from_extension()`
  (src/common.c) — fetch 1.2.2 source if a citation-grade map is needed.
- Case sensitivity of the fallback (`.SND`, `.GSM`) unmeasured.
- No pure-FSSD hcom member exists in the corpus (all are RIFF-first
  polyglots) — whether this build's magic table recognizes real HCOM
  content is unmeasured (HCOM is absent from the format-major list, so
  likely "not recognised").
- `sf_open` honors the name only via the path argument; the `|cmd` and
  `/dev/stdin` spellings were not probed (ctypes fd arm is the cleaner
  anonymous bound).
- Within-host only: libsndfile 1.2.2-4, Arch build; format set is
  compile-time — other builds may include HCOM/TXW readers.

Artifacts: `corpus/live/frontier-sndfile/` —
`probe_sndfile.py` (4-arm ctypes harness), `runs/sndfile-matrix.json`
(13 members × 4 arms, full SF_INFO + read count + error),
`runs/extsweep.json` (56-extension fallback map + content-precedence
legs), `runs/prior-verdicts.tsv` (sox+ffmpeg per-arm extract from
committed receipts), `logs/info-*.txt` (sndfile-info stdout for all 9
members), `logs/probe-stderr*.txt`.
