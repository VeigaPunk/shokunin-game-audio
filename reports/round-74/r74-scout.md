# r74-scout — lavf no-seek demuxer sweep + pw-cat ops-2: PRE-MEASUREMENT

Seat: **scout** (leaf, report-only). Wave `shokunin-train-20261101-w13`, lane
audio, repo `/home/vgpnk/Projects/shokunin/audio-shokunin`. Write scope: this
report + `corpus/live/r74-scout/` only; no fixture edit, no git mutation
(HEAD `1ba8103`, untracked scratch only).

Host `plazir27`, window 2026-10-14 15:18–15:35 UTC. Tools:
`ffmpeg/ffprobe n9.0.1` (libavformat 63.1.101), `mpv v0.41.0` linking
`/usr/lib/libavformat.so.63` = the **same lavf build as the CLI** (`ldd`),
`pw-cat` libpipewire 1.6.8, live daemon `pipewire` 1905 / `pipewire-pulse`
2290 / `wireplumber` 1906 (untouched, pids identical at close), default sink
`alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink`.

Tooling note (seat rule): **no LSP device this session** —
`mcp_list_servers` → only `rea` (Ghidra, no definition/references/hover);
`which pyright pylsp jedi-language-server lsp` → all absent. No semantic
claim below rests on grep: mechanism claims are traced in **fetched upstream
source at the exact local tags** (`n9.0.1`, `mpv v0.41.0`) and labelled
inference; everything else is process-level measurement with receipts.

## Headline (4 briefed questions, answered)

1. **Generatable demuxers on this host**: `adx` + `wv` are fully
   generatable (`E` muxers + `adpcm_adx`/`wavpack` encoders). **`iss`,
   `apc`, `acm` are demuxer-only** — no muxer, no encoder → hand-built
   members (3 layouts, validated clean against local ffmpeg; §2).
2. **mpv forks on hand-built members**: `iss` FORKS — single-packet member =
   hcom shape (file rc2 / fifo rc0), multi-packet member = **head-truncation
   fork rc0/rc0** (2 packets lost). `apc` FORKS (rc2 shape ≤2 packets,
   truncation shape ≥3). **`acm` does NOT fork — the briefed candidate-#3
   prediction is FALSIFIED** (invariant at 406 B and 12 KB). `adx`/`wv`
   (GENERIC_INDEX controls) invariant, seek *succeeds* (§3).
   Refined rule (§4): the wound is the **failed generic-search branch's
   `ff_read_frame_flush`** in `seek_frame_internal`; `acm` is immune because
   it sets `AVFMT_NOGENSEARCH` → early `return -1` with no flush.
3. **pw-cat `--raw` on a `.wav`-named fifo**: rc **1 → 0** on identical
   bytes and identical fifo name — the name axis dies in raw mode (§5).
4. **`--target 0` kill class**: **TERM-terminable** (rc124 @ 4.001 s ×3;
   direct TERM → exits rc=1 in ~1 ms), wchan `do_epoll_wait` — versus the
   writerless-fifo open-block: wchan `wait_for_partner`, TERM **ignored**,
   KILL escalation rc137/-9 @ 6.001 s (§6).

## 1. Generatability surface (observed)

`logs/tool-surface.txt` (exact greps). ffmpeg n9.0.1:

| | iss | apc | acm | adx | wv |
|---|---|---|---|---|---|
| muxer (`-muxers`) | – | – | – | **E** | **E** |
| encoder | – | – | – | **adpcm_adx** | **wavpack** |
| demuxer | D | D | D | D | D |
| decoder | adpcm_ima_iss | adpcm_ima_apc | interplayacm | adpcm_adx | wavpack |

So `ffmpeg -f lavfi -i sine=… -c:a adpcm_adx -f adx` and `-c:a wavpack -f wv`
produce valid controls (both rc0, decoded clean). `iss/apc/acm` members must
be hand-built; the local *decoders* exist, so mpv can decode them once the
bytes are valid. No sox path needed/attempted (sox present but no iss/apc/acm
support either; not probed further — the demuxer-only surface is decisive).

## 2. Hand-built members (`corpus/live/r74-scout/members/`, builder
`build_members.py` sha `98b6cf37…`)

Layouts derived from fetched `n9.0.1` demuxer/decoder source and **validated
against local ffmpeg** (`ffprobe` + `ffmpeg -i M -f null -`):

| member | bytes | sha256 (16) | layout (measured-valid) |
|---|---|---|---|
| `sweep_iss_1pkt.iss` | 295 | `e63fbcd658102fbc` | 10-token text header `IMA_ADPCM_Sound <pktsz> …` + NUL + 1 pad; 1×256 B packet = 4 B IMA hdr (pred=0, step=0) + 252 B nibbles |
| `sweep_iss_4pkt.iss` | 1064 | `4d7f6ecbcde5523e` | same, 4 packets |
| `sweep_iss_40pkt.iss` | 10281 | `950f4fdf8072f152` | same, 40 packets |
| `sweep_apc_1pkt.apc` | 544 | `a3228e8d4fbb6bcd` | `CRYO_APC 1.20` + nsamples + rate 8000 + 8 B extradata + channels=0 (32 B) + 512 B payload |
| `sweep_apc_multi.apc` | 8224 | `02b578a1b8296169` | same, 8192 B payload (= 2×4096 B packets) |
| `sweep_apc_3pkt.apc` | 12320 | `4d0fd018a3f8a7ea` | same, 12288 B payload (3 packets) |
| `sweep_acm_64blk.acm` | 406 | `f349fcc51f5fc23a` | **14 B header** magic+nsamples+channels+rate+(rows<<4\|level) + 64 blocks × 49 bits (level=0 rows=8, linear filler) |
| `sweep_acm_2000blk.acm` | 12264 | `c44dbc729c96497e` | same, 2000 blocks (2 s @ 8 kHz) |
| `sweep_adx.adx` | 2304 | `03bff40dddfb0527` | ffmpeg lavfi 0.5 s sine → adx muxer |
| `sweep_wv.wv` | 3536 | `9ce51501f35be32f` | ffmpeg lavfi → wv muxer |
| `sweep_tone2s.wav` | 32078 | `9c7f830944829360` | ffmpeg lavfi 2 s 8 kHz mono s16 (start-cell control) |

Two layout traps measured (documented in the builder comments):
- **`acm_read_header` calls `ff_get_extradata(pb, 14)` from the current
  position with no magic skip** → the 14 B extradata *includes* the magic; an
  18 B variant (separate magic) fails `avformat_open_input` with INVALIDDATA
  on local n9.0.1. Data starts at offset 14.
- ISS packets need a **4 B IMA header per packet** (`adpcm.c:1223`
  `header_size = 4*ch`; `step_index > 88` → decoder INVALIDDATA — the first
  LCG-payload attempt hit `step_index[0] = 3200`).

Known quirk (observed, not a blocker): `iss_read_packet`/`apc_read_packet`
return `AVERROR_INVALIDDATA` on the short read at EOF instead of
`AVERROR_EOF` → the ffmpeg CLI logs `Error during demuxing: Invalid data
found` (rc still 0) and mpv tolerates it (plays, rc0). Receipts must not read
that CLI line as a member defect.

## 3. mpv matrix — file vs fifo, `--ao=pcm` decode witness

Harness `mpv_matrix.py` sha `b7b25904…`; legs `timeout -s KILL 20 mpv
--no-config --vo=null --audio-display=no --really-quiet [--ao=null |
--ao=pcm --ao-pcm-file=… --ao-pcm-waveheader=no] <file|fifo>`; fifo legs =
fresh fifo named with the member basename + one-shot writer thread. Receipts
`runs/mpv-matrix-{canon,r74,r74b}.json`; r74 **verdict-identical ×2 (28
cells, 0 field diffs)**; r74b re-run identical.

Canonical controls reproduce r73 byte-exactly: `dec_hcom` file rc2/pcm 0
(refresh seek + synthetic EPERM) vs fifo rc0/**3520 B**; `dec_act` invariant
rc0/**556 B**.

| member | file rc / pcm B | fifo rc / pcm B | probe (fmt/score) | file-arm refresh seek | fork |
|---|---|---|---|---|---|
| `iss_1pkt` | **2 / 0** | 0 / 1008 | iss/100 | to 0.002902, failed | **rc fork (hcom shape)** |
| `iss_4pkt` | 0 / **2016** | 0 / 4032 | iss/100 | to 0.002902, failed | **truncation fork (−2 pkts)** |
| `iss_40pkt` | 0 / **38304** | 0 / 40320 | iss/100 | to 0.002902, failed | **truncation fork (−2 pkts)** |
| `apc_1pkt` | **2 / 0** | 0 / 2048 | apc/100 | to 0.000000, failed | **rc fork** |
| `apc_multi` (2×4096) | **2 / 0** | 0 / 32768 | apc/100 | failed | **rc fork (all lost)** |
| `apc_3pkt` | 0 / **16384** | 0 / 49152 | apc/100 | failed | **truncation fork (−2 pkts)** |
| `acm_64blk` | 0 / 1024 | 0 / 1024 | acm/**66** | failed | **INVARIANT — prediction falsified** |
| `acm_2000blk` | 0 / 32000 | 0 / 32000 | acm/66 | failed | **INVARIANT** |
| `adx` | 0 / 8000 | 0 / 8000 | adx/75 | **succeeded** | invariant (index seek) |
| `wv` | 0 / 8000 | 0 / 8000 | wv/100 | **succeeded** | invariant (index seek) |

Measured wound law (bounded to this member set):
- file-arm loss = **exactly the first 2 packets** (iss 2×1008 B; apc
  2×16384 B) regardless of stream length;
- if the stream has **≤2 packets, everything is lost → rc2 “no audio or
  video data played”**; if ≥3 → **rc0 with a PCM-byte delta**.
- **rc alone collapses the fork** — `iss_4pkt`/`iss_40pkt`/`apc_3pkt` are
  rc0/rc0 forks; the discriminating witness is decoded-PCM bytes.
- fifo arms are unwounded (`Stream is not seekable.`, no refresh seek) and
  play the full member; the ISS/APC EOF-INVALIDDATA quirk does not disturb
  the fifo verdict (rc0).

## 4. Mechanism (source-traced, labelled inference)

Local n9.0.1 source (`seek.c:597` `seek_frame_internal`, `:523`
`seek_frame_generic`):

```
read_seek?            no (iss/apc/acm/hcom)          -> ret = -1
read_timestamp?       no                             -> skipped
!(AVFMT_NOGENSEARCH)? TRUE for hcom/iss/apc          -> ff_read_frame_flush(s)
                                                        + seek_frame_generic()
   seek_frame_generic: no index entries; rewinds to data_offset, scans packets
   looking for dts > target + keyframe; for formats WITHOUT AVFMT_GENERIC_INDEX
   no index entries are ever added -> index < 0 -> return -1 (seek failed,
   demuxer already flushed, AVIO advanced by the scan)
acm: AVFMT_NOGENSEARCH set -> `else return -1` at :627 -> NO flush -> immune
adx/wv: AVFMT_GENERIC_INDEX -> the scan ADDS index entries -> seek succeeds
```

- mpv side (fetched `mpv v0.41.0`): `demux.c` `initiate_refresh_seek`
  (:3968) clears the demux reader queue and sets `ds->refreshing` with
  `last_pos/last_dts` before issuing the seek; `demux_lavf.c`
  `demux_drop_buffers_lavf` (:1314) shows the same `av_seek_frame` +
  `demux_flush` + `avformat_flush` pattern. The failed refresh seek is
  accepted (“seek done”) and playback continues from the post-flush state.
- Therefore the refined condition set is: (1) content probe detects the
  format; (2) no `.read_seek`/`.read_timestamp`; (3′) **not
  `AVFMT_NOGENSEARCH`** (this replaces the briefed “no AVFMT_GENERIC_INDEX”);
  (4) codec not pcm+block_align. `acm` satisfies (2) but violates (3′) →
  no fork. Attribution is source-derived (local binary not disassembled);
  the measured acm invariance is the witness.

## 5. pw-cat `--raw` — name axis death (receipt `runs/pwcat-ops2.json`)

Bytes = `corpus/live/round-69/extsuffix_nomatch.snd` (512 B, sha
`f073e70a…`, no magic), writer = one-shot dump + close,
`XDG_RUNTIME_DIR=/run/user/1000`, `timeout -s KILL 15`.

| cell | input name | mode | rc | stderr |
|---|---|---|---|---|
| R1 | fifo `…raw1.wav` | `pw-cat -p` | **1** | `sndfile: failed to open audio file …` |
| R2 | fifo `…raw2.wav` | `pw-cat -p --raw` | **0** (0.082 s) | — |
| R3 | fifo `…raw3.bin` | `--raw` | 0 | — |
| R4 | fifo `…raw4.snd` | no raw | 0 (fallback, r73 re-pin) | — |
| R5 | fifo `…raw5.snd` | `--raw` | 0 | — |
| R6 | file `…raw6.wav` | `--raw` | 0 | — |
| R7 | file `…raw6.wav` | no raw | 1 | `sndfile: failed to open audio file …` |

R1 vs R2 isolate the variable (identical bytes, identical fifo name):
**`--raw` bypasses the libsndfile decode layer and the name axis with it** —
the same `.wav` name that rejects in decode mode is accepted in raw mode.

Viability note for ARM B: pw-cat **cannot open the `wv` member at all**
(rc1 `sndfile: failed to open audio file`) — libsndfile has no WavPack
reader. pw-cat legs must use wav members (`dec_act`, or a scratch tone);
the adx/wv controls are mpv-only.

## 6. `--target 0` kill class (receipt `runs/pwcat-ops2-target.json`)

Input = `round-66/pair_dec_act.wav` (libsndfile-openable; the first attempt
with the wv member died rc1 pre-daemon — see §5).

| cell | command | rc | wall | wchan / state |
|---|---|---|---|---|
| T1/T2/T2b | `timeout -s TERM 4 pw-cat -p --target 0 <member>` (×3, T2 with `-k 1`) | **124, 124, 124** | 4.001 s ×3 | — |
| T3 | direct launch, sample /proc, then SIGTERM | rc=**1** after TERM | dies in **~1 ms** | `do_epoll_wait`, S |
| T4 | `pw-cat -p <member>` (linked) | 0 | 0.091 s | — |
| T5 | `pw-cat -p --target 52 <member>` (sink serial) | 0 | 0.070 s | — |
| T6a | `timeout -k 2 -s TERM 4 pw-cat -p <writerless fifo>` | **-9** (=137) | **6.001 s** | — |
| T6b | same fifo, direct TERM after 1.2 s | **IGNORED** | needed KILL | `wait_for_partner`, S |

So the ops-2 partition is pinned by **block location**: unlinked-stream
(`--target 0`, documented “0 means don't link”) waits in the pw mainloop
(`do_epoll_wait`) and is **TERM-terminable**; the fifo-open block waits in
`wait_for_partner` and is **SIGTERM-immune** (harness must use `timeout -s
KILL` / `-k`). T5 shows the hang is the missing link, not target selection.

## 7. Secondary cell — `mpv --start=N` position fork (receipt
`runs/start-cell.json`, harness `start_cell.py` sha `f70c527d…`)

2 s tone, `--ao=pcm` byte witness: file `--start=1` → **16000 B** (honours
the seek), file `--start=0` → 32000 B, fifo `--start=1` → **32000 B** (full
play from 0, “not seekable”), fifo `--start=0` → 32000 B. **Position fork
confirmed** with the same rc=0 on all four legs — bytes are the witness.

## 8. Handoff for the author (receipt design, measured not guessed)

- **Member authority**: reuse `corpus/live/r74-scout/members/*` + shas from
  `members/manifest.json`; `python3 build_members.py` regenerates byte-stable
  members. New members land under `corpus/live/` per the brief.
- **Receipt fields needed** (rc alone is insufficient on both arms):
  lavf `detected_format` + `probe_score`, `stream_not_seekable`,
  `refresh_seek_to`, `seek_failed`, `playback`+`reason`, and **decoded PCM
  bytes per arm** (the truncation fork has rc0 on both arms).
- **Expected verdict groups to check the landed receipt against**
  (`runs/mpv-matrix-r74.json`): forks {iss_1pkt: rc2; iss_4pkt/iss_40pkt:
  −2-packet truncation; apc_1pkt/apc_multi: rc2; apc_3pkt: −2-packet
  truncation}; invariants {acm_64blk, acm_2000blk, adx, wv, dec_act}.
- **Claim wording**: `acm` must not be listed as a fork candidate without the
  `AVFMT_NOGENSEARCH` immunity; the condition (3) in the brief
  (“no AVFMT_GENERIC_INDEX”) is falsified as stated — the operative branch is
  the generic-search flush. The “2 packets” quantum is measured-bounded
  (iss 256 B packets, apc 4096 B packets), not a general constant.
- **Protocol**: `timeout -s KILL` on all fifo arms; `--target 0` legs may use
  TERM (but keep a KILL backstop); pw-cat legs on wav members only.
- **pw-cat ops-2 sub-block** (insertion-only): `{raw: {wav_fifo_rc:1,
  wav_fifo_raw_rc:0, bin_fifo_raw_rc:0, file_wav_raw_rc:0}, target0:
  {rc124_wall_4.001, wchan:do_epoll_wait, term_terminable:true},
  fifo_block: {wchan:wait_for_partner, term_terminable:false,
  kill_escalation_rc:-9@6.001s}}`.

## 9. Confidence & remaining unknowns

Confidence **high** for: the tool surface; all 10 members’ validity; the
40+ mpv cells (2× replay-identical, canonical r73 controls reproduced
byte-exactly); the raw/target cells (×3 on the target-0 timeout cell); the
start-cell. Confidence **medium-high** for the `AVFMT_NOGENSEARCH`
attribution (n9.0.1 source traced, local binary not disassembled).

Unresolved:
- The exact “2 packets” quantum’s dependence on seek target/packet size —
  only two packet sizes probed; source shows the quantum = packets consumed
  by the failed generic scan.
- Other no-seek demuxers (wady/sdr2/aax) not probed; the refined rule
  predicts their outcome by flags only.
- mpv `--cache` interactions and the `redirected_fd`/`stdin` arms not
  extended to the new members (r73’s stdin pair remains the seekability-key
  proof).
- pw-cat raw cells probed on `.wav`/`.bin`/`.snd` names only.
- `--target 0` rc=1-on-direct-TERM vs rc124-under-`timeout` is a
  wrapper-vs-direct distinction; both are TERM-terminable.
- `mpv --start=N` probed on one wav member only.

## 10. Evidence index (all under `corpus/live/r74-scout/`)

| artifact | sha256 (first 16) |
|---|---|
| `build_members.py` | `98b6cf37b1d56752` |
| `mpv_matrix.py` | `b7b25904688017ec` |
| `pwcat_ops2.py` | `c1f72a4d242cd185` |
| `start_cell.py` | `f70c527d1a6ce30f` |
| `members/manifest.json` | `fb295c5d4c667fe4` |
| `runs/mpv-matrix-canon.json` | `698639898cd6036e` |
| `runs/mpv-matrix-r74.json` / `…run2` | `e2d57adf13559b80` / `563faf722c78fbe5` |
| `runs/mpv-matrix-r74b.json` | `2418b3365eeac6d0` |
| `runs/pwcat-ops2.json` (raw group) | `db136fec542700c3` |
| `runs/pwcat-ops2-target.json` | `5fd289d8acb97ac2` |
| `runs/start-cell.json` | `874b50f0eee70e8f` |
| `logs/tool-surface.txt` | (see file) |

Reproduce:
```sh
cd ~/Projects/shokunin/audio-shokunin/corpus/live/r74-scout
python3 build_members.py          # regenerate members (byte-stable)
python3 mpv_matrix.py canon       # r73 control re-pin, 8 legs
python3 mpv_matrix.py r74         # 28 legs (7 members × 2 arms × 2 legs)
python3 mpv_matrix.py r74b        # 12 legs (size lattice)
python3 pwcat_ops2.py raw         # 7 cells
python3 pwcat_ops2.py target      # 9 cells (~25 s, includes hangs)
python3 start_cell.py             # 4 legs
```

Key raw logs: `logs/iss_4pkt__file__dec.log` (refresh seek → fail → EOF
reached, yet 2016 B decoded), `logs/acm_64blk__file__dec.log` (same failure,
full 1024 B), `logs/dec_hcom__file__ver.log` (r73 re-pin).

**Seat stop.** Measured output above; no edits outside the stated scope; no
git mutation; sibling r74 scratch dirs left untouched.
