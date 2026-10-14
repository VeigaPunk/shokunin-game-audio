# r73-scout — consumer class pre-measurement: pw-cat + mpv on the member corpus

Seat: **scout** (leaf, report-only). Wave `shokunin-train-20261101-w12`, lane
audio, repo `audio-shokunin`. Scope written: this report +
`corpus/live/r73-scout/` only. No fixture edit, no git mutation.

Host `plazir27`, measurement window 2026-10-14 11:35–11:45 -03. **HEAD at
measurement `f5d7faf`** (r72 reviewer-fold landed mid-session 11:38:20; a
lazy-libsndfile-load change, not an r73 landing — the r73 arm is unlanded:
last probe flag is still `--probe-sndfile-transport-r72`,
`measure_audio.py:1130`). Fixture line anchors below are on `f5d7faf`.

Tooling note (seat rule): **no LSP device available** — verified this session:
`mcp_list_servers` exposes only `rea` (Ghidra RE toolset, no
`definition`/`references`/`hover`), and `which pyright pylsp
jedi-language-server lsp` → all absent. No semantic claim below rests on grep
output; the mechanism
section rests on process-level measurement (strace, ctypes on the installed
libs) plus fetched upstream source explicitly labelled as inference.

Tools measured: `pw-cat` libpipewire 1.6.8 (`pw-play` → `pw-cat`), `mpv`
v0.41.0 (libavformat 63.1.101, FFmpeg n9.0.1, libavutil 61.1.101), `pactl`
protocol 35. System PipeWire daemon live (pipewire 1905, wireplumber 1906,
pipewire-pulse 2290; `pactl info` → "PulseAudio (on PipeWire 1.6.8)";
4 sinks). Concurrency note: the r73-boundary seat ran a **private** pipewire
(pid 325961, runtime dir `r73-boundary/rt2`) during my window; all legs below
were served by the system daemon via `XDG_RUNTIME_DIR=/run/user/1000`.

## Headline — claim is PARTIAL

Reproduced exactly: the **mpv INVERTED seekability fork** (`file → rc2`,
`fifo → rc0`, decodes) — now with the mechanism pinned and quantified.
Not reproduced / over-strong: **"consumer verdicts partition by mandatory-seek
vs stream-consume polarity — opposite of the decoder axis"**:

1. mpv partitions on **exactly one of 11 members** (the hcom polyglot), and the
   partition key is the **seekable bit**, proven by a same-transport pair
   (`-` with pipe stdin → rc0, `-` with regular-file stdin → rc2). The other
   10 members are transport-invariant, including `dec_act` — the very member
   where the sox decoder bridge forks.
2. pw-cat's only partition on the canonical corpus is the **name/extension
   axis** for `extsuffix_snd` (file `.snd` → rc0; fifo named `.fifo` → rc1;
   fifo named `.snd` → rc0; stdin `-` → rc1) — i.e. **the same polarity as
   the decoder axis** (libsndfile's post-sniff `.snd` fallback, r72; sox's
   ext-gated `sndr`, r69), not the opposite. The frontier's
   "pw-cat is transport-invariant" held only because its member set/fifo
   names never exercised that cell.
3. The "opposite polarity" holds only **across different members**: sox forks
   on `dec_act` (seekable arm wins), mpv forks on `dec_hcom` (unseekable arm
   wins). No member was measured on which the same runtime flips polarity
   between the decoder and consumer axes.

Plus one framing correction: the mpv log string
`Seek failed (Operation not permitted)` is **not a real EPERM** — it is
`av_strerror(-1)` rendering FFmpeg's `-1` "no seek path" sentinel
(`strerror(1)` = "Operation not permitted"). No seek syscall is issued
(strace: 0 `lseek` during the refresh seek).

## 1. mpv matrix — 44 cells (11 members × 4 arms)

Harness `mpv_matrix.py` (sha256 `721a0a42…`); command shape
`timeout -s KILL 15 mpv --no-config --vo=null --ao=null --audio-display=no
--really-quiet --log-file=<log> <input>`; arms `file` (named+seekable),
`fifo_path` (named+unseekable), `stdin_pipe` (`-`, anonymous+unseekable),
`stdin_file` (`-`, anonymous+seekable). Two runs
(`runs/mpv-matrix-run{1,2}.json`) are **verdict-identical 44/44** (rc, found
format, seek lines, playback reason).

| member | file | fifo_path | stdin_pipe | stdin_file |
|---|---|---|---|---|
| `dec_hcom` | **rc2** no-data | **rc0** played | **rc0** played | **rc2** no-data |
| `dec_act` | rc0 | rc0 | rc0 | rc0 |
| `tone4s` (4 s, self-built) | rc0 (4.08 s wall) | rc0 (4.08 s) | rc0 (4.08 s) | rc0 (4.08 s) |
| `posttable_nomatch` | rc2 unrec | rc2 | rc2 | rc2 |
| `txw_piperefuse` | rc2 | rc2 | rc2 | rc2 |
| `extsuffix_{wav,bin,txw,f32,snd}` | rc2 ×4 each | | | |
| `lengate_gsrt_25` | rc2 | rc2 | rc2 | rc2 |

rc2 splits into two classes by the playback line: `unrecognized file format
(reason 4)` (probe failure, 8 members) vs `no audio or video data played
(reason 4)` (`dec_hcom` seekable arms). **rc alone cannot distinguish them** —
a receipt must carry the reason class.

- **The fork is seekability, not transport shape.** Same bytes, same `-`
  spelling: pipe stdin rc0 / regular-file stdin rc2 (logs
  `logs/mpv/dec_hcom__stdin_{pipe,file}.log`). Both seekable arms log
  `refresh seek to 0.000000` → `execute seek` → `Seek failed (Operation not
  permitted)`; both unseekable arms log `Stream is not seekable.` and no
  refresh seek. Detection is identical (`Found 'hcom' at score=100 size=600`)
  on all four.
- **Decode quantified** (`--ao=pcm --ao-pcm-file=<raw> --ao-pcm-waveheader=no`):
  fifo arm → **3520 bytes** of u8@22050 PCM (= 3520 samples = the single
  440 B hcom packet ffmpeg decodes); file arm → **no PCM file at all** (0
  samples). Artifact `pcm-fifo.raw` (3520 B).
- **`dec_act` does not fork**: lavf probes it as `wav` (score=99), and mpv's
  `using bullshit libavformat PCM seek hack` makes the refresh seek succeed
  on every arm (log `logs/mpv/dec_act__file.log`) — so the sox-bridge member
  never reaches the broken path in mpv.
- Rejects are pure content sniff: `.wav` suffix did not rescue
  `extsuffix_nomatch.wav`, and did not prevent `hcom` detection on
  `pair_dec_hcom.wav`; the five identical-byte suffix members are rc2 on all
  arms with identical `No format found` logs.

## 2. pw-cat matrix — 22 cells (11 members × file/fifo)

Harness `pwcat_matrix.py` (sha256 `7bf76dce…`); writer = one-shot write +
immediate close (no linger); `timeout -s KILL 15 pw-cat -p <input>`;
`XDG_RUNTIME_DIR=/run/user/1000`. Two runs verdict-identical 22/22.

| class | members | verdict |
|---|---|---|
| accept (rc0, empty stderr) | `dec_act`, `dec_hcom`, `tone4s`, `extsuffix_snd` **file only** | plays |
| reject rc1 `Format not recognised.` | `posttable_nomatch`, `extsuffix_{wav,bin,txw,f32}`, `extsuffix_snd` **fifo** | open failed |
| reject rc1 `File contains data in an unimplemented format.` | `txw_piperefuse` | open failed |
| reject rc1 `Error in WAV file. No 'data' chunk marker.` | `lengate_gsrt_25` | open failed |

- **The single fork is the path extension**, isolated on identical bytes
  (`corpus/live/round-69/extsuffix_nomatch.snd`, 512 B):
  file `…nomatch.snd` rc0 (RAW|U-LAW, 500 frames) / fifo `g1.fifo` rc1 /
  fifo `g2.snd` rc0 / stdin `-` rc1. Logs `logs/special/G{1,2}.out`,
  `logs/pwcat/extsuffix_snd__fifo_path.log`. This is the r72 libsndfile fork
  (`20261014T143756973418Z-sndfile-transport-r72`: named `.snd` accept,
  anonymous reject) surfacing unchanged at the consumer level — pw-cat's
  decode layer is libsndfile.
- All other 10 members are transport-invariant (incl. `dec_hcom`, which mpv
  forks on).
- Error tails embed the concrete input path → the r71 path-normalisation
  (`<input>`) is required for byte-stable receipts.

## 3. Fork mechanism (mpv/hcom) — pinned, not inferred

1. **No syscall EPERM.** `strace -f` of the file arm (`logs/strace-file-dec_hcom.txt`):
   the only lseeks are open-time (`SEEK_END`→600, `SEEK_SET`→0); the refresh
   seek issues **0 lseek**, 0 EPERM syscalls.
2. **The string is the `-1` sentinel.** On this host's libavutil 61.1.101
   (ctypes): `av_strerror(-1)` → `"Operation not permitted"`; `av_strerror(-22)`
   → `"Invalid argument"` etc. So mpv's `Seek failed (Operation not permitted)`
   = `av_seek_frame` returned `-1`.
3. **It is lavf-level, not mpv-level.** `ffmpeg -ss 0.005` on the same member
   → `could not seek to position 0.005`; AVIO statistics `600 bytes read,
   0 seeks`. Upstream `libavformat/hcom.c` (fetched master, inference):
   no `read_seek`, no `read_timestamp` → `seek_frame_internal` falls through
   to the generic path and returns `-1`; `av_strerror` maps `-1` to
   `strerror(EPERM)`.
4. **Why unseekable wins.** On seekable arms mpv's refresh seek
   (`demux.c` → `demux_seek_lavf`) attempts the seek and, before failing,
   flushes the demuxer read state — the packet buffered by
   `avformat_find_stream_info` is discarded, playback starts at EOF → 0
   samples → rc2. On unseekable arms (`demux.c: "Stream is not seekable."`)
   the refresh seek is skipped → the buffered packet decodes (3520 samples)
   → rc0.
5. **Negative discriminator:** `--force-seekable=yes` on the fifo did *not*
   flip the cell (still rc0, still no refresh seek) — that knob does not
   drive this path (`logs/cal-fifo-forceseek-dec_hcom.log`).

## 4. Special legs (14) — writer-attach, pacing, gates

Script `special_legs.sh` (sha256 `0338c7c8…`), logs `logs/special/`.

| leg | measured |
|---|---|
| daemon gate, file | `PIPEWIRE_RUNTIME_DIR=<empty>` → rc1 `error: pw_context_connect() failed: Host is down`, **0.003 s** |
| daemon gate, writerless fifo | same rc1 in 0.003 s — **fifo open never reached** (gate precedes input) |
| `pactl` dead runtime | rc1 `Connection failure: Connection refused` |
| writerless fifo | blocks in `open()` (`/proc/<pid>/wchan = wait_for_partner`, state S), 0 bytes output; **survives SIGTERM** (alive 1.5 s after); `timeout -k 2 4` → rc137 at **6.001 s** (TERM at 4 s ignored, KILL needed) |
| zero-byte writer closes | rc1 `Format not recognised.`, 0.203 s |
| pacing, instant dump of 4 s tone | rc0, **4.035 s** → playback-paced, not read-paced |
| pacing, 1600 B / 0.2 s (8 s feed) | rc0, **8.209 s** → streams as bytes arrive, no underrun abort |
| raw `-a` instant dump | rc0, 0.350 s (= 64044 B at default 48 kHz/2ch/s16; frontier's "~5 s" not reproduced) |
| `--target 0` (unlinked) | rc124 at **4.002 s** → hangs (never drains) but is **TERM-terminable**, unlike the fifo open block |
| mpv writerless fifo | rc137 at 5.001 s (blocks in open) |
| mpv fifo + 1.0 s writer linger | rc0, 1.235 s — verdict-neutral vs immediate close (mpv exits at writer EOF) |
| mpv fifo + zero-byte writer | rc2 `unrecognized file format`, 0.237 s (no hang) |

Harness hazards measured for the author:

- `timeout -s KILL` is mandatory (fifo open block is SIGTERM-immune).
- **Pin mpv's AO**: `--ao=pipewire` on the *fifo* arm with
  `XDG_RUNTIME_DIR` unset → **rc2 `audio output initialization failed
  (reason 4)`** (a *third* rc2 reason class); with the daemon reachable →
  rc0. `--ao=null` (frontier shape) is daemon-independent. This confirms the
  simplifier's "do not couple mpv to the daemon" ruling with the exact flip
  cell.
- pw-cat `PIPEWIRE_RUNTIME_DIR` overrides `XDG_RUNTIME_DIR` for the gate
  (empty `PIPEWIRE_RUNTIME_DIR` blocked while `XDG_RUNTIME_DIR` was live).

## 5. Decoder-axis comparison (primary committed receipts)

| axis | member | receipt | measured shape |
|---|---|---|---|
| sox (decoder) | `dec_act` | `runs/20261014T143702669854Z-transport-dec-act-r67` | **fork**: file exit0/278 samples (route `ffmpeg`); stdin/redirected/fifo exit2 |
| sox (decoder) | `dec_hcom` | `runs/20261014T143700572322Z-transport-dec-hcom-r67` | no fork: all 4 arms exit0/9 samples (native) |
| sndfile (decoder) | `extsuffix_snd` | `runs/20261014T143756973418Z-sndfile-transport-r72` | **fork (named vs anonymous)**: `{file, fifo_path}` RAW\|U-LAW 500 fr; `{stdin_pipe, redirected_fd}` reject (receipt records `named`; that the fifo name carried `.snd` is the r71/r72 harness convention — the extension is the key, proven by my `G1`/`G2` legs) |
| sox (decoder) | `extsuffix_snd` | `runs/20261014T143646171645Z-transport-extsuffix-snd-r69` | **fork (name)**: file+fifo `.snd` sndr 504 samples; anonymous reject |
| ffprobe | `dec_act`/`dec_hcom` | `runs/20261014T143358199155Z-ffprobe-transport-r71` | no fork, detect `wav`/`hcom` on all 4 |
| mpv (consumer) | `dec_hcom` | this seat, §1 | **fork (seekable)**: seekable rc2 / unseekable rc0 |
| pw-cat (consumer) | `extsuffix_snd` | this seat, §2 | **fork (name)**: `.snd`-named rc0 / else rc1 |

So the decoder axis itself has two fork shapes (seekable-named-only accept;
named-`.snd` accept). The consumer side adds one genuinely inverted shape
(mpv/hcom) and one *inherited* shape (pw-cat `.snd` = same as the decoder).

## 6. Deltas vs frontier `fb-pipewire.md`

- `ports/frontier/fb-pipewire.md` is at `ports/frontier/`, not
  `reports/frontier/` (brief path is stale).
- "pw-cat verdicts are transport-invariant on every member tried" — true for
  their set, **false on the canonical corpus**: `extsuffix_snd` forks on the
  fifo *name* (their fifos were `fifo1/2/3`, member not tried).
- Their mpv table left `dec_act` fifo unmeasured and skipped `lengate`; both
  measured here (`dec_act` invariant rc0; `lengate` invariant rc2).
- Their caveat "mechanism inferred from log order, not straced" — resolved
  here (§3): no syscall, `-1` sentinel, lavf-level.
- Their "`-a` raw over fifo ≈ 5 s wall" not reproduced (0.350 s with default
  raw params, instant dump).
- Their `--target 0` "hangs forever" is precise as "never drains"; the
  process is TERM-terminable at the deadline (rc124 @ 4.002 s).

## 7. Handoff for `--probe-consumers-r73` (author)

Anchors on `f5d7faf` (`corpus/fixtures/measure_audio.py`): `main()` `:1013`;
argparse tail `:1128` (r70) / `:1129` (r71) / `:1130` (r72, 2 lines); one-mode
guard `sum([...]) > 1` `:1133`; r71 dispatch `:1341`; r72 dispatch `:1353`;
mode chain `:1819`; suffix chain `:1839`. Member authority: reuse
`TRANSPORT_R71_MEMBERS` (`:557`) + `TRANSPORT_R67_ARMS` (`:179`);
`fifo_feed`/`reap_fifo_orphans` (`:294`/`:324`); arm bound
`TRANSPORT_R71_ARM_TIMEOUT_S` (`:568`).

Receipt design (all measured, not guessed):

1. **pw-cat fields**: `pwcat_rc`, `pwcat_wall_s`, normalized `stderr`
   (path → `<input>`); daemon gate = `PIPEWIRE_RUNTIME_DIR=<empty dir>` leg
   (`rc1` + `Host is down`) or the exact blockage if down. Verdict predicate:
   rc0 accept; rc1 + `Format not recognised.` / `unimplemented format` /
   `No 'data' chunk marker.` reject tiers.
2. **mpv fields**: `mpv_rc` is insufficient — carry
   `mpv_found_format` (`Found '<x>' at score=…`),
   `mpv_seekable` (presence of `Stream is not seekable.`),
   `mpv_refresh_seek` (line or null), `mpv_seek_failed` (bool/string),
   `mpv_playback` (`success (reason 0)` / `no audio or video data played
   (reason 4)` / `unrecognized file format (reason 4)` / `audio output
   initialization failed (reason 4)`). Logs embed timestamps + `Opening
   done: <path>` → extract stable lines, don't store verbatim.
3. **Fifo naming must be pinned.** Fixture convention
   (`Path(tmp)/path.name`) keeps `.snd` → pw-cat `extsuffix_snd` fifo accepts
   (my `G2`); a neutral name (frontier `fifo1`) rejects (`G1`). Either is
   fine; record which (`fifo_name = member basename` vs neutral), otherwise
   the pw-cat verdict matrix is not reproducible.
4. **Arms**: file+fifo reproduce the mpv fork, but only the
   stdin-pipe/stdin-file pair proves the fork key is seekability (same `-`
   spelling, opposite verdicts). If the receipt does not include the pair,
   record the per-arm `seekable` bit from `TRANSPORT_R67_ARMS` and cite the
   pair as the discriminator.
5. **Protocol**: `timeout -s KILL`; writer one-shot + close is sufficient for
   both consumers (1.0 s linger verdict-neutral, +~1 s wall); pin
   `--ao=null` for mpv (AO coupling measured); pacing budget ≈ audio
   duration per pw-cat/mpv tone leg (4.08 s for 4 s).
6. Expected verdict groups to check the landed receipt against:
   `runs/scout-summary.json` (pw-cat: 1 fork `extsuffix_snd` under a neutral
   fifo name, 0 forks under the fixture's name-preserving convention; mpv:
   1 fork `dec_hcom` on the seekable bit; 10 invariant members each).

## 8. Confidence & remaining unknowns

Confidence: **high** for the 66 matrix cells + 14 special legs (both matrices
verdict-identical across two runs; fork reproduced under three independent
shapes: file/fifo, stdin pair, strace/ctypes/ffmpeg cross-checks).

Unresolved:

- Local FFmpeg is n9.0.1; the seek-path source cited is upstream master
  (behaviour matched locally on all observable points, but the local binary
  was not disassembled).
- mpv with a writer that never closes (mpv waits at writer EOF — inferred
  from the linger leg, not measured to the timeout).
- mpv trickle-feed timing untested; pw-cat with a daemon but zero sinks
  untested (the boundary seat was measuring a private daemon concurrently).
- The `.snd` extension-fallback case sensitivity and cwd dependence are r72
  leftovers, untouched here.
- Two stale r72-critic shells (pids 3808/3813) and the boundary seat's
  private pipewire (325961) were present during the window; not mine, left
  untouched.

## 9. Evidence index (all under `corpus/live/r73-scout/`)

| artifact | sha256 (first 16) |
|---|---|
| `mpv_matrix.py` / `pwcat_matrix.py` | `721a0a4274bf80e4` / `7bf76dce290190eb` |
| `special_legs.sh` / `summarize.py` | `0338c7c8e532936f` / `814f242795938336` |
| `runs/mpv-matrix-run1.json` / `run2` | `805e25fb3d8d8d0d` / `8be035e9db4d1c49` |
| `runs/pwcat-matrix-run1.json` / `run2` | `0363cbfb6e7e52d0` / `6a10f1431f3a3eab` |
| `runs/scout-summary.json` | `85cd99a2bf265c80` |
| `tone4s.wav` (self-built 8 kHz s16 mono 4 s) | `2611b84731998175` |
| `pcm-fifo.raw` (3520 B, fifo-arm decode) | (see `logs/sha256.txt`) |

Reproduce:

```sh
cd ~/Projects/shokunin/audio-shokunin/corpus/live/r73-scout
python3 mpv_matrix.py run1        # 44 legs, ~20 s
python3 pwcat_matrix.py run1      # 22 legs, ~10 s (plays to default sink)
bash special_legs.sh              # 14 legs, ~40 s
python3 summarize.py
```

Key raw logs: `logs/mpv/dec_hcom__{file,fifo_path,stdin_pipe,stdin_file}.log`,
`logs/pwcat/extsuffix_snd__{file,fifo_path}.log`,
`logs/strace-file-dec_hcom.txt`, `logs/special/{A1,A2,B1.status,C1,D1,D2,D3,E1,F2,F3}*`,
`logs/special/G1.out`/`G2.out`, `logs/daemon-state.txt`,
`logs/cal-file-dec_hcom-aopipewire-*.log`.
