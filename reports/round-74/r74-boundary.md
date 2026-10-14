# R74 boundary — hand-built iss/apc/acm edge lattice (37 inputs × 5 arms = 185 cells, verdicts byte-stable ×2), author-member cross-check, `--target 0` kill class under load, zero-sink daemon = blockage, `mpv --start=N` position fork pinned by PCM bytes

Seat: **boundary** (leaf). Lane: audio. Repo: `/home/vgpnk/Projects/shokunin/audio-shokunin`.
Host: `plazir27`, measured 2026-10-14 ~15:21–15:33 UTC.
Tools: `pw-cat` (libpipewire **1.6.8**), `mpv` **v0.41.0** (FFmpeg **n9.0.1**, libavformat **63.1.101**),
`ffmpeg`/`ffprobe` n9.0.1 (libavformat 63.1.101), live daemon `pipewire` pid 1905,
`pipewire-pulse` 2290, `wireplumber` 1906 (pids identical at close).
Observation snapshot: HEAD **`1ba8103`**; the **r74 author arm landed mid-window** in the working tree
(`corpus/fixtures/measure_audio.py` = `154a35a0…`, `grep -c r74` = **23**, uncommitted) and its members
exist under `corpus/live/round-74/`; this seat re-measured those bytes read-only (cross-check §7).
No `lsp` device in this seat window — all claims below are direct measurement; FFmpeg header layouts
were read from upstream source (raw.githubusercontent.com/FFmpeg/FFmpeg `master`/`n9.0.1`
`libavformat/{iss,apc,acm}.c`, `libavcodec/interplayacm.c`) and are flagged where they are inference.
Write scope respected: this file + `corpus/live/r74-boundary/` only; no tracked file modified
(`git status --porcelain` shows only the author's `measure_audio.py` + `__pycache__`); no git mutation.

## Headline

1. **The briefed "iss/apc/acm → file rc=2 / fifo rc=0 fork" is member-size dependent, not
   demuxer-name dependent.** Measured forks (file rc=2 reason 4 / fifo rc=0): `apc_valid` (4128 B,
   single-packet) and the author's `lavf_iss.iss` (552 B, 2×256 B packets). Invariant rc=0 both arms:
   `iss_valid` (20516 B, 40 packets), `acm_valid` (11218 B, 350 frames), author's `lavf_iss_multi.iss`
   (131118 B) and author's `lavf_acm.acm` (2394 B). Mechanism (inference): the refresh seek after
   `avformat_find_stream_info` fails with synthetic EPERM either way; rc=2 requires that find_stream_info
   drained the stream and left no residual packet/decoder data, otherwise playback proceeds from the
   residual queue (head-truncation, rc=0).
2. **`--target 0` unlinked-stream class = TERM-terminable, not SIGTERM-immune** (rc124 @4.002 s;
   `-k 3` escalation never fires; 8× concurrent all rc124 @4.003 s). Writerless-fifo open-block is the
   opposite class (TERM ignored, KILL @7.001 s). Mixed 4+4 load keeps the classes independent.
3. **Zero-sink private daemon = blockage** (recorded, not a seat failure): private daemon up in 50 ms,
   0 sinks, `pw-cat -p` hangs (rc −9 @8 s); `libpipewire-module-fallback-sink` in the *daemon* config
   creates node `auto_null` (Audio/Sink) with **0 ports** → still hangs; `pw-cli load-module` is a
   *client*-context no-op for the daemon. Adding `wireplumber` makes it playable but **breaks
   isolation** (it enumerated the real ALSA devices; the live session transiently showed `auto_null`
   and then re-registered its 4 sinks) — arm stopped, incident recorded in §9.
4. **`mpv --start=N` position fork CONFIRMED** (PCM-byte witness, `--ao=pcm` is untimed):
   `--start=1` on a 4 s wav → file 48000 B (3.0 s), fifo 64000 B (4.0 s); `--start=5` → file rc=2 /
   0 B, fifo rc=0 / 64000 B.
5. Negative control: **pw-cat's libsndfile layer rejects all iss/apc/acm/adx members** (rc=1
   `Format not recognised.`, identical file/fifo) — the `--target 0` / fifo-hang cells are *unreachable*
   for those members (the gate fires in 2–4 ms before the stream/link stage).

## 1. Members built (scratch, byte-deterministic; `build_members.py` `95c5b59d…`)

Layouts from upstream ffmpeg source; validated by `ffprobe`/`ffmpeg -f null -` before any mpv arm.
**ACM trap (cost this seat one rebuild):** `ff_get_extradata(…,14)` reads from file offset **0**, i.e.
the 14 B *include* the BE magic — layout = magic(4) + max_samples u32le + ch u16le + rate u16le +
`(rows<<4|level)` u16le, data at offset 14. An extra u32 at offset 4 → `INVALIDDATA` at open.
The author's `mk_members.py` uses the same layout (comment "extradata INCLUDES the BE magic").

| member | bytes | sha256 (manifest) | note |
|---|---|---|---|
| `iss_valid` | 20516 | `8fa9e733…` | 40×512 B packets, mono, rate_div 1 |
| `apc_valid` | 4128 | (manifest) | single 4096 B packet |
| `acm_valid` | 11218 | (manifest) | level 0 / rows 32, 350 frames × 32 B |
| `iss_pkt_huge` | 554 | `570f7b0e…` | packet_size 100 000 000, 512 B data |
| `apc_partial_100` | 132 | (manifest) | header + 100 of 4096 B |
| `acm_partial_20` | 38 | (manifest) | header + 20 B (< one 32 B frame) |
| `tone4s.wav` | 64044 | `71abef1b…` | r73 scratch 4 s tone, copied (sndfile-accepted) |

Full hash table: `corpus/live/r74-boundary/members/manifest.json` (`ff315863…`).
37 inputs (35 edge members + `manifest.json` + `tone4s.wav` control) × {ffprobe, mpv file, mpv fifo, pw-cat file, pw-cat fifo} = **185 cells**;
all fifo arms: fresh fifo named with the member basename, writer `cat member > fifo`,
reader `timeout -s KILL 20 mpv …`; mpv shape `--no-config --vo=null --ao=null --audio-display=no
--really-quiet --log-file=…` (r73/frontier shape, lavf log fields parsed, never bare rc).

## 2. Matrix — the fork table (receipts `…152117…`/`…153117…`-matrix-r74, verdicts byte-identical ×2)

`f` = file arm, `F` = fifo arm. mpv rc=0 ⇒ success; rc=2 ⇒ reason 4 (`no audio or video data played`
or `unrecognized file format`). `eperm` = "Seek failed (Operation not permitted)" in log;
`ns` = "Stream is not seekable." in fifo log.

| member | f rc / fin | F rc / fin | f eperm | F ns | fork? |
|---|---|---|---|---|---|
| iss_valid (40 pkt) | 0 success | 0 success | ✓ | ✓ | **no** (head-truncated rc=0) |
| apc_valid (1 pkt) | **2** reason 4 | **0** success | ✓ | ✓ | **YES** |
| acm_valid (350 fr) | 0 success | 0 success | ✓ | ✓ | **no** |
| iss_partial_1pkt | **2** reason 4 | **0** success | ✓ | ✓ | **YES** |
| iss_partial_1.5pkt | **2** reason 4 | **0** success | ✓ | ✓ | **YES** |
| iss_partial_halfpkt | 2 reason 4 | 2 reason 4 | ✓ | ✓ | no |
| iss_partial_0pkt | 2 reason 4 | 2 reason 4 | ✓ | ✓ | no |
| apc_partial_100 | **2** reason 4 | **0** success | ✓ | ✓ | **YES** |
| apc_partial_0data | 2 reason 4 | 2 reason 4 | ✓ | ✓ | no |
| acm_partial_20 / 1frame / 1.5frame | 0 success | 0 success | ✓ | ✓ | no |
| acm_nodata / partial_0data | 2 reason 4 | 2 reason 4 | ✓ | ✓ | no |
| iss_stereo1 / apc_stereo | 0 success / 2 reason 4 | 0 / 0 | ✓ | ✓ | mixed (iss no, apc yes) |
| tone4s.wav (control) | 0 success | 0 success | – | ✓ | no |

- pw-cat: **37/37 transport-invariant** (0 file/fifo rc mismatches); accepted set = {tone4s.wav rc=0} (and nothing else);
  iss/apc/acm/adx → rc=1 `sndfile: … Format not recognised.` file and fifo alike.
- The `.snd` name-axis fallback from r73 was not re-probed (not this seat's cell).

## 3. Wound shape and head-truncation (quantified; `…153315…`-truncation-r74)

`--ao=pcm --ao-pcm-waveheader=no` byte counts; **ao=pcm is untimed** (file arms 0.038–0.039 s wall),
so bytes — not wall — are the witness.

| member | arm | rc | PCM bytes | played s | expected bytes |
|---|---|---|---|---|---|
| iss_valid (40×512) | file | 0 | 77216 | 0.875 | 81920 |
| iss_valid | fifo | 0 | 81280 | 0.922 | 81920 |
| acm_valid | file/fifo | 0 | 229376 | 5.201 | (decoder re-frames 32 B→~3 B/frame; inflated) |
| lavf_iss.iss (author, 2×256) | file | **2** | 0 | 0 | 4096 |
| lavf_iss.iss | fifo | 0 | 2016 | 0.023 | 4096 |
| lavf_iss_multi.iss (author, 256×512) | file | 0 | 516128 | 5.852 | 524288 |
| lavf_iss_multi.iss | fifo | 0 | 520192 | 5.898 | 524288 |
| lavf_acm.acm (author, 20 fr) | file/fifo | 0 | 800 | 0.018 | — |

Log chains (exact, from `logs/`): file arm `Found 'iss' score=100` → `avformat_find_stream_info()
finished after <n> bytes` → `refresh seek to 0.005805` → `Seek failed (Operation not permitted)` →
[residual queue? `playback restart complete @ -0.126259, audio=playing` → plays] or [`error reading
packet: Invalid data…` ×10 → `…treating it as fatal error.` → `EOF reached.` → reason 4].
Fifo arm replaces the refresh-seek pair with `Stream is not seekable.` (no seek attempt) and plays.
**Inference (not traced into lavf):** the fork is decided by how much of the stream
`find_stream_info` consumed vs how much remains queued; the head-skip equals the consumed prefix
(file arms lost 1.6–5.7 % of the PCM, fifo arms lost 0.8 % at the tail; exact packet counts not pinned).
Every complete iss member also ends with the demuxer's `INVALIDDATA` tail (10× `error reading
packet` then `treating it as fatal error`) **yet rc=0** — `rc alone is not a verdict` applies to iss.

## 4. Malformed headers (probe-rejected vs probe-accepted/header-rejected)

| class | members | mpv file | mpv fifo | ffprobe |
|---|---|---|---|---|
| magic mutated / truncated | iss_magic_bad, iss_magic_trunc, apc_magic_bad, acm_magic_bad | rc=2 `unrecognized file format`, no `Found '…'` | same | rc≠0 Invalid data |
| probe 100/66, header parse fails | iss_hdr_2tok, iss_pkt_zero, iss_pkt_neg, iss_pkt_nan, apc_hdr_trunc8, apc_hdr_trunc20, acm_hdr_trunc10, acm_ch_zero, acm_rate_zero | rc=2 `unrecognized file format` (detected line present) | same | rc≠0 Invalid data |
| header accepted, bad params | apc_rate_zero / apc_rate_huge (`-1 Hz` track line, decoder `Could not open`) | rc=2 reason 4 | rc=2 reason 4 | ffmpeg decode rc=234 `Invalid argument` (rate 0) |
| header accepted, huge packet | iss_pkt_huge (packet_size 1e8, 512 B data) | rc=2 reason 4 + `error reading` | rc=2 reason 4 (closing writer) | rc=0 detected |
| header accepted, zero frame | acm_rows0 (block_len 0) | rc=2 reason 4 | rc=2 reason 4 | rc≠0 |
| short payload | acm_nodata, acm_partial_0data | rc=2 reason 4 | rc=2 reason 4 | rc=0 detected |

No malformed member produced a *distinct* fork: the probe-accepted/header-rejected class is
rc=2 both transports (a third wound shape, distinct from both §2 shapes).

## 5. Linger-writer hang class (non-closing writer; `…152431…`-linger-r74)

Writer = `linger_writer.py` (holds the fifo fd open 30 s, bounded `timeout -s KILL 20`).

| member (bytes) | reader | writer | outcome |
|---|---|---|---|
| iss_valid (20516) | mpv | rc −9 @20 s KILL | hangs **after** detection+find_stream_info, in playback (awaiting data) |
| acm_valid (11218) | mpv | rc −9 | same |
| apc_valid (4128) | mpv | rc −9 | hangs **before** the `Found 'apc'` line (initial fill never completes) |
| iss_pkt_huge (554) | mpv | rc −9 | same pre-detection hang (malformed header + linger) |
| iss_valid | pw-cat | rc=1 @0.35 s | sndfile reject exits promptly even with a live writer |

So a linger harness needs `timeout -s KILL` for mpv **both** pre- and post-detection; the pre-detection
fill threshold sits in (4128 B, 11218 B] on this build (not pinned — remaining unknown).

## 6. `--target 0` kill class under load (`…152725…`-target0-r74)

Member `tone4s.wav` (sndfile-accepted; the gate confound is its own cell).

| cell | rc | wall | note |
|---|---|---|---|
| `t0_single_term` (`timeout -s TERM 4`) | 124 | 4.002 | TERM terminates the unlinked stream |
| `t0_single_term_k3` (`-k 3 -s TERM 4`) | 124 | 4.002 | KILL escalation never fires |
| `t0_kill8_hang_proof` (`-s KILL 8`) | −9 | 8.001 | 4 s member does **not** finish in 8 s → never drains |
| `linked_control_kill8` (linked playback) | 0 | 4.033 | playback-paced control |
| `t0_load8_term` (8 concurrent) | 124 ×8 | 4.003 | class stable under load |
| `writerless_load4_term_k3` (4 concurrent) | −9 ×4 | 7.001 | SIGTERM-immune; KILL required |
| `mixed_load8` (4 t0 + 4 writerless) | 124 ×4 / −9 ×4 | 7.000 | classes independent under mixed load |
| `t0_iss_sndfile_gate` (iss + `--target 0`) | 1 | 0.002 | sndfile gate fires before the link stage |

## 7. Author-member cross-check (read-only; `…153240…`-crosscheck-r74)

The author's landed bytes (`corpus/live/round-74/`, hashes recorded in the receipt) through this
seat's harness — independent of the author's receipts (not read):

| member | sha256 | mpv file | mpv fifo | pw-cat | author prediction | measured |
|---|---|---|---|---|---|---|
| lavf_iss.iss (552 B) | `4fbc2ca5…` | **2** reason 4 | **0** | 1 | fork | **CONFIRMED** |
| lavf_iss_multi.iss (131118 B) | `85a518c8…` | 0 success | 0 | 1 | head-truncation rc=0 | **CONFIRMED** |
| lavf_apc.apc (5152 B) | `684d2794…` | **2** reason 4 | **0** | 1 | fork | **CONFIRMED** |
| lavf_acm.acm (2394 B) | `5afaa65a…` | 0 success | 0 | 1 | fork (ENOSYS-class) | **FALSIFIED as fork** (invariant rc=0; `EOF reached` → `audio=draining` → success) |
| lavf_aifc.aifc (control) | `23aa8a65…` | 0 | 0 | 0 | no fork | confirmed |
| lavf_adx.adx (GENERIC_INDEX control) | `3831ef47…` | 0 | 0 | 1 | no fork | confirmed |

## 8. Claim adjudication

| briefed clause | measured outcome |
|---|---|
| malformed iss/apc/acm headers | pinned: magic mutations → probe 0, rc=2 both arms; probe-accepted/header-rejected → rc=2 both arms; apc accepts rate 0/huge (decoder refuses), acm rejects ch/rate ≤0 at header |
| partial members | pinned incl. 3 forks (iss 1/1.5 pkt, apc 100 B); 0-pkt/0-data tails rc=2 both arms; acm partials rc=0 both arms |
| `--target 0` kill class under load | TERM-terminable rc124 @4.002 s, no KILL escalation, stable 8×; contrast writerless-fifo −9 @7.001 s; unreachable for iss/apc/acm (sndfile gate rc=1 @2 ms) |
| zero-sink private daemon feasibility | **blockage recorded**: up in 50 ms but 0 sinks/0 ports → pw-cat hangs (rc −9 @8 s); fallback-sink daemon-config → `auto_null` node, 0 ports, still hangs; `pw-cli load-module` is a client-context no-op; +wireplumber plays but is **not isolated** (§9) |
| `mpv --start=N` position fork | **CONFIRMED** by PCM bytes: file seeks (3.0 s of 4 s), fifo from 0 (4.0 s), `--start=5` → rc=2 vs rc=0 |
| `timeout -s KILL` everywhere fifo-adjacent | all fifo arms, linger writers and mpv readers wrapped; only the deliberate kill-class cells use TERM |
| author's predicted iss/apc/acm fork | member-local, size-gated: 2/3 confirmed on the author's own bytes (iss small, apc), acm falsified; multi-packet iss confirmed as head-truncation rc=0 |

## 9. Incident / caveat (recorded, bounded)

The private-daemon + `wireplumber` arm (rt-fb5, ~15:30 UTC) was **not isolated**: the private session
enumerated the real ALSA outputs and the **live** session transiently reported a single `auto_null`
sink (id 4541) while the private daemon held the devices; after teardown the live session re-registered
its 4 ALSA sinks + 2 sources (new ids 4839–4844, all SUSPENDED) and is healthy at close
(`pactl list short sinks` = 4, sources = 6, pids unchanged 1905/2290/1906). A 4 s 8 kHz tone may have
played on the default hardware sink during that arm. The arm was stopped immediately after and is not
repeated; the zero-sink verdict rests on the no-session-manager arms (safe, hang-only).

## 10. Commands / exits (exactly as run, in `corpus/live/r74-boundary/`)

```sh
python3 build_members.py                        # exit 0; manifest.json
python3 probe_boundary_r74.py matrix            # exit 0; 185 cells; verdicts df7ea1a9… (×2, byte-identical)
python3 probe_boundary_r74.py linger            # exit 0; 5 cells (writer KILLed at its 20 s bound)
python3 probe_boundary_r74.py target0           # exit 0; 8 cells
python3 probe_boundary_r74.py daemon            # exit 0; 10 cells (private daemon, default config)
python3 probe_boundary_r74.py daemon2           # exit 0; 6 cells (fallback-sink in daemon config)
python3 probe_boundary_r74.py crosscheck        # exit 0; 30 cells on the author's landed members
python3 probe_boundary_r74.py truncation        # exit 0; 10 cells (ao=pcm byte counts)
python3 probe_boundary_r74.py startpos          # exit 0; 4 cells + 2 log tails
```
rc vocabulary: mpv/pw-cat 0/1/2; `timeout -s KILL` expiry = −9 (shell 137); `timeout -s TERM`
expiry = 124. `pw-cli load-module` rc=0 is not evidence of a daemon-side module (client context).

## 11. Artifacts (sha256, all under `corpus/live/r74-boundary/`)

`build_members.py` `95c5b59d…`; `probe_boundary_r74.py` `7bd9f65e…` (final); `linger_writer.py` `c1b04f64…`;
`members/manifest.json` `ff315863…`; `fallback.conf` `7982b238…`; `logs/matrix-summary.tsv` `16e90be0…`;
receipts `runs/<stamp>Z-<cell>-r74/` with `measurements.json` (walls, stderr) + `verdicts.json`
(replay core). **Valid receipts** (use these): matrix `…152117…` + `…153117…`
(verdicts `df7ea1a9…` ×2 byte-identical), linger `…152431…` (`2148afcc…`), target0 `…152725…`
(`45848bc6…`), daemon `…152825…` (`8bd11ca4…`), daemon2 `…152918…` (`3b408aca…`),
crosscheck `…153240…` (`4354ac72…`), truncation `…153315…` (`ff4e43ad…`), startpos `…153112…`
(`397bb9b6…`). Superseded runs (kept, do not cite): linger `…152236…` (`ba82134d…`; writer closed the
fifo early — wrong script), target0 `…152628…`/`…152649…` (`5c0a70e8…`/`b2ccec39…`; sndfile gate
confound), daemon `…152806…` (serialization failure, no verdicts), daemon `…152816…` (`e30f9a3a…`;
gate confound), daemon2 `…152903…` (`12ec6f5b…`; module inserted before protocol-native, daemon
refused to start). Logs under `logs/` (mpv lavf chains, daemon logs, matrix-summary.tsv).

## 12. Remaining unknowns / risks

- Residual-queue mechanism is inferred from log order + byte counts; the exact packet counts consumed
  by `find_stream_info` and the pre-detection fifo fill threshold (4128 B < T ≤ 11218 B) are not pinned.
- My members are hand-built; verdicts are properties of *these bytes* (hashes in the receipts).
  Author members were measured at the hashes in §7 and may be regenerated later.
- `--ao=pcm` untimed behaviour was used only as a position witness; ao=null arms' walls are not
  position evidence.
- The zero-sink conclusion covers this host's pipewire 1.6.8 + config; a daemon with a *proper*
  private session manager + null sink was attempted but abandoned for isolation reasons (§9).
- The private-daemon-with-wireplumber arm perturbed live device ids (recovered); do not repeat on a
  shared host.

**Seat stop.** Measured output above; no edits outside the stated scope; no git mutation.
