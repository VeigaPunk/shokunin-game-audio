# R73 boundary — consumer arms (pw-cat + mpv) executed in boundary scratch (author landing ABSENT both ends of the window): 10×4 consumer matrix byte-stable ×2; the mpv inverted-seek fork is CONFIRMED for `dec_hcom` only (file rc=2 EPERM / fifo rc=0) and is FALSIFIED as a corpus-wide "consumer partition"; pw-cat is transport-invariant with a name-gated `.snd` fallback on fifo names; daemon gate rc=1 in 3 ms **before** input open (attached writer left blocked in open); zero-sink private daemon → HANG (frontier's last viability gap closed); writer semantics: exit at data-chunk end (linger irrelevant), partial/SIGKILL writers rc=0; mpv's "Seek failed (Operation not permitted)" is library-synthetic — 0 failing syscalls under strace

Seat: **boundary** (leaf). Lane: audio. Repo: `/home/vgpnk/Projects/shokunin/audio-shokunin`.
Host: `plazir27`, measured 2026-10-14 ~14:35–14:55 UTC.
Tools: `pw-cat` (libpipewire **1.6.8**, compiled+linked), `mpv` **v0.41.0** (libavformat 63.1.101),
live daemon: `pipewire` pid 1905, `pipewire-pulse` 2290, `wireplumber` 1906 (all untouched; pids
identical at close).
Observation snapshot start: HEAD **`50f55eb`**, `corpus/fixtures/measure_audio.py` = `df1e5bec…`;
snapshot end: HEAD **`f5d7faf`** (r72 reviewer-fold — the only intervening commit), fixture =
`b068dbb5…`, newest probe flag still `--probe-sndfile-transport-r72` (`measure_audio.py:1130`),
`grep -c r73 corpus/fixtures/measure_audio.py` = **0**. **The author's `--probe-consumers-r73` arm
did not land in this window** (r73-author scratch dir exists; sibling r73-scout/scribe/simplifier
reports appeared concurrently — not read, to keep this seat independent).
No `lsp` device in this seat window; all checks by direct measurement + read/grep.
Write scope respected: this file + `corpus/live/r73-boundary/` only; no tracked file modified
(`git status --porcelain corpus/fixtures` empty; fixture hash = HEAD at both snapshots).

## What this seat executed (scratch arm, not tracked evidence)

Following the r72 boundary convention, the MOVE's measurement half was executed as a scratch arm
mirroring the briefed shape (`--probe-consumers-r73`: pw-cat playback + mpv, file + fifo):

- `corpus/live/r73-boundary/probe_consumers_r73.py` (`f63b26f1…`) — {pw-cat, mpv} × {file, fifo} ×
  10 members = 40 cells; per-arm `timeout -s KILL 20`; fifo arms use a per-cell fifo named with the
  member basename (r72 critic convention: basename must keep the extension) + writer
  `cat member > fifo`; mpv shape = frontier's (`--no-config --vo=null --ao=null
  --audio-display=no --really-quiet --log-file=…`); verdicts parsed from normalized log/stderr.
- Receipts: `runs/20261014T143703.92109918Z-consumers-r73/` and
  `runs/20261014T143717.42228555Z-consumers-r73/`;
  `verdicts.json` byte-identical across both runs — sha256 **`9f8bc309…`** (replay-stable core);
  `measurements.json` adds walls + tool/daemon snapshot (sha `6cd670c1…` / `20260ffa…`).
- Edge probes `corpus/live/r73-boundary/edge_probes.py` (`1afd4134…`), receipts
  `edge_results_probe-{a..l}.json`. All writes in scratch.

## Consumer matrix (all measured this seat; rc, verdict)

`f`=file arm, `F`=fifo arm (fresh fifo + writer, basename preserved). pw-cat rc=0 ⇒ played;
rc=1 ⇒ sndfile open failure. mpv rc=0 ⇒ `finished playback, success`; rc=2 ⇒ load/recognize failure.

| member | pw-cat f | pw-cat F | mpv f | mpv F |
|---|---|---|---|---|
| dec_act | 0 | 0 | **0** (lavf `wav` 99, plays) | **0** (wav, not seekable) |
| dec_hcom | 0 | 0 | **2** (`hcom` 100 → refresh seek → EPERM → reason 4) | **0** (`hcom`, no refresh seek) |
| lengate_gsrt_25 | 1 `No 'data' chunk marker` | 1 identical | 2 (undetected) | 2 |
| posttable_nomatch | 1 `Format not recognised` | 1 | 2 | 2 |
| txw_piperefuse | 1 `unimplemented format` | 1 | 2 | 2 |
| extsuffix_wav | 1 `Format not recognised` | 1 | 2 | 2 |
| extsuffix_bin | 1 | 1 | 2 | 2 |
| extsuffix_txw | 1 | 1 | 2 | 2 |
| extsuffix_f32 | 1 | 1 | 2 | 2 |
| extsuffix_snd | **0** (RAW/U-Law fallback) | **0** (same, fifo name `.snd`) | 2 | 2 |

- **pw-cat: 10/10 transport-invariant** (rc and error text identical file vs fifo). Its acceptance
  set = the libsndfile predicate {dec_act, dec_hcom, extsuffix_snd}; the reject texts are the r72
  sndfile taxonomy, verbatim.
- **mpv: exactly one file/fifo fork** — `dec_hcom` (file rc=2 / fifo rc=0). `dec_act` plays on both
  arms; the other 8 members are undetected on both (`No format found` → rc=2). The fork is real and
  inverted vs the decoder axis, but it is **member-local, not a corpus partition**.
- mpv file-arm `dec_hcom` log chain (reproduced): `Found 'hcom' score=100 size=600` →
  `refresh seek to 0.000000` → `execute seek (flags 32)` → `Seek failed (Operation not permitted)` →
  `EOF reached` → `finished playback, no audio or video data played (reason 4)`. Fifo arm:
  `Stream is not seekable.` → no refresh seek → decoder consumes → `success (reason 0)`.
- `--force-seekable` does **not** override the fork (probe k): file+`=no` still EPERM rc=2;
  fifo+`=yes` still plays rc=0. The bit is transport-derived, not the mpv option.

## Edge probes (frontier's skipped cells; receipts `edge_results_probe-{a..l}.json`)

**a — daemon gate (dead runtime dir, `PIPEWIRE_RUNTIME_DIR`=empty dir).** File arm rc=1
`pw_context_connect() failed: Host is down`, wall **0.003 s**; fifo arm rc=1 same, wall 0.004 s
(gate is checked before `open()`, so the open-block never starts); with a writer attached first the
reader still rc=1 instantly and the writer **stays blocked in `open()`** (measured `true`; killed
only by process-group SIGKILL) — a live orphan hazard for naive harnesses. `pactl` → refused.

**b — zero-sink daemon (frontier's explicit gap, now measured).** Private `pipewire` daemon in a
scratch runtime dir, no session manager: socket up, `pw-dump` → **0 nodes / 0 sinks**. `pw-cat -p
member` → **hangs, killed at 8 s** (rc −9 ≡ shell 137; `timeout -s KILL` self-kills). Live-daemon
`--target 0` control: identical hang. So "daemon live" is insufficient — a linkable sink is required;
the failure mode is a hang, not an error. Teardown verified; live pids unchanged.

**c — no-writer hangs.** `pw-cat` on a writerless fifo: hang, rc −9 at 6 s (re-verify of frontier).
`mpv` on a writerless fifo: **also hangs** (rc −9 at 6 s) — previously unmeasured. Empty-writer
close (0 bytes): pw-cat rc=1 `Format not recognised` (0.35 s); mpv rc=2 `unrecognized file format`
(0.36 s) — both exit promptly.

**d — writer lingers 2 s after full member.** pw-cat exits at **data-chunk end**, not at writer
close: wall 0.411 s (dec_act) / 0.427 s (dec_hcom), rc=0, writer rc=0. Frontier's "exits rc=0 at
writer EOF" is imprecise for complete WAV data; **linger is irrelevant** (stronger than "no linger
needed").

**e — partial / dying writers (frontier predicted rc=0 partial).** 4 s scratch tone (64044 B,
`tone4s.wav` `71abef1b…`): instant full dump wall **4.38 s** (playback-paced); half dump + clean
close wall **2.39 s** rc=0 (plays exactly the delivered 2 s); half dump + writer SIGKILL
(writer_rc −9) wall **2.389 s** rc=0 — identical EOF semantics. `dec_hcom` half (300/600 B):
rc=0. **Prediction confirmed.**

**f — SIGTERM immunity of the open-block.** `timeout 5 pw-cat -p fifo` (default TERM): the timeout
wrapper is still waiting at 7 s (TERM ignored while blocked); cleaned up with process-group SIGKILL,
zero residue. Harnesses must use `-s KILL` (as frontier said) **and** kill the group.

**g — content-vs-name on fifos.** hcom bytes in a fifo named `g1.txw` → pw-cat rc=0, mpv rc=0;
no-magic bytes in `g2.wav` → pw-cat rc=1, mpv rc=2. Content precedence holds for both consumers;
the name neither rescues nor blocks *content* detection.

**h — the EPERM is library-synthetic.** strace (`openat,lseek,fcntl,ioctl,read,pread64`) of the mpv
file arm on dec_hcom: **0** syscall lines containing EPERM; all `lseek(10,…)` return ≥0
(`-901 SEEK_CUR`→529, `1429 SEEK_SET`→1429, `0 SEEK_END`→600, `0 SEEK_SET`→0). No failing seek
reaches the kernel: the refresh seek fails inside libavformat before any syscall. Mechanism
inference (not traced into the library): lavf `avio_seek` returns `AVERROR(EPERM)` when the context
has no seek callback; the exact context is unidentified. Frontier's "not straced" gap is now
narrowed to the library layer only.

**i — pacing.** Instant dump of the 4 s tone → 4.38 s wall (playback-paced, re-verify). Slow
trickle 1600 B / 0.2 s → 8.56 s wall rc=0 (blocks when starved, no underrun abort).

**j — multiple writers (3 reps).** Two concurrent full dumps of dec_act: rc=0 all 3 reps, wall
0.42 s, both writers rc=0 — the reader stops at the data-chunk end and the second dump is simply
unread. Stable, not a hazard for this member.

**k — `--force-seekable` override.** See matrix note: no effect in either direction.

**l — the `.snd` fallback is name-gated on the fifo path (frontier's "no suffix/name axis"
corrected).** Identical 512-B no-magic bytes: fifo named `l2.snd` → rc=0, `l3.SND` → rc=0,
`l1.foo` → rc=1 `Format not recognised`, `l4.wav` → rc=1. So pw-cat's libsndfile layer **does**
have a name axis (post-sniff fallback family, case-insensitive — consistent with r72 boundary c),
and it survives the fifo transport whenever the fifo name carries the extension. Content precedence
(WAV/TXW) stands; "no name axis" holds only for content-detected formats.

## Claim adjudication vs the briefed MOVE

| briefed clause | measured outcome |
|---|---|
| pw-cat playback arm: playback-paced, writer-attach semantics, daemon-required gate | CONFIRMED + extended: pacing 4.38 s/4 s; exit at data end (linger irrelevant); partial/SIGKILL writers rc=0; gate rc=1 in 3 ms pre-open; zero-sink daemon hangs |
| mpv arm: content sniff via libavformat | CONFIRMED: detects only {wav, hcom} on this corpus; 8 members `No format found` on both arms |
| INVERTED seekability fork (file→EPERM→rc2, fifo→decodes) | CONFIRMED for `dec_hcom` only (1/10 members); `--force-seekable` cannot flip it; EPERM is library-synthetic (0 failing syscalls) |
| "consumer verdicts partition by mandatory-seek vs stream-consume polarity — opposite of the decoder axis" | **FALSIFIED as a partition**: only the hcom member forks; pw-cat has 0 forks (10/10 invariant); 8 members are undetected by mpv on both arms. The polarity is a member-local fork, real and inverted vs the decoder axis |
| frontier "(pw-cat) no suffix/name axis" | **FALSIFIED as stated**: `.snd`/`.SND`-named fifos with no-magic bytes are accepted (rc=0); `.foo`/`.wav` are not (rc=1) |

## Commands / exits (exactly as run)

```sh
cd ~/Projects/shokunin/audio-shokunin/corpus/live/r73-boundary
python3 probe_consumers_r73.py            # exit 0; 40 cells; verdicts sha 9f8bc309… (×2 runs)
python3 edge_probes.py a                  # exit 0   (gate; 3 ms rc=1)
python3 edge_probes.py b                  # exit 0   (zero-sink daemon; hangs)
python3 edge_probes.py c                  # exit 0   (no-writer / empty-writer)
python3 edge_probes.py d                  # exit 0   (linger)
python3 edge_probes.py e                  # exit 0   (partial / SIGKILL writer)
python3 edge_probes.py f                  # exit 0   (TERM immunity; cleanup verified)
python3 edge_probes.py g                  # exit 0   (content-vs-name)
python3 edge_probes.py h                  # exit 0   (strace; 0 EPERM syscalls)
python3 edge_probes.py i                  # exit 0   (pacing / trickle)
python3 edge_probes.py j                  # exit 0   (2 writers ×3)
python3 edge_probes.py k                  # exit 0   (--force-seekable)
python3 edge_probes.py l                  # exit 0   (fifo-name fallback sweep)
```

Note on rc vocabulary: `timeout -s KILL` **self-kills** on expiry (Python sees rc −9, shell sees
137) — used here as the "hang" marker; `pw-cat`/`mpv` normal exits are 0/1/2.

## Artifacts (sha256, all in `corpus/live/r73-boundary/`)

`probe_consumers_r73.py` `f63b26f1…`; `edge_probes.py` `1afd4134…`; `tone4s.wav` `71abef1b…`;
`verdicts.json` `9f8bc309…` (byte-identical ×2: `…143703…` and `…143717…` run dirs);
`measurements.json` `6cd670c1…` / `20260ffa…`; `edge_results_probe-a..l.json`
`14bf4a76…/107eedb8…/9260bd5b…/9425e360…/fbc29388…/763a27eb…/50e3118b…/9600d634…/6a173dff…/84add74a…/ac52ac20…/e5d583ad…`;
strace log `logs/edge-strace-mpv-file-dec_hcom.txt`. Member bytes bound by sha256 in
`verdicts.json` (dec_act `777b6764…`, dec_hcom `325fb967…`, lengate_gsrt_25 `ede4161b…`,
posttable `6373923f…`, txw `fd7911a3…`, five extsuffix `f073e70a…`).

## Remaining unknowns / risks

- The author's landed arm (if it lands later) will define the canonical receipt shape; this scratch
  matrix must be diffed on verdicts, not bytes. My fifo arms preserve the member basename — an
  author arm using a different fifo name would legitimately fork on `extsuffix_snd` (probe l).
- The exact lavf/mpv code path returning EPERM is inferred (no failing syscall; source not read).
- mpv "Stream is not seekable" decision is transport-derived; `--force-seekable` does not move it —
  mechanism not further localized.
- Zero-sink daemon test used a private daemon with no session manager; a daemon with a session
  manager but no hardware sinks was not exercised (not measurable without touching the live session).
- Probe j (multi-writer) is 3 reps of one member only; interleaving-dependent for longer inputs.
- Sibling scout's concurrent pw-cat runs (`corpus/live/r73-scout/`, observed pids only) were left
  untouched; no cross-talk observed in my receipts (byte-stable ×2 during the overlap).

**Seat stop.** Measured output above; no edits outside the stated scope; no git mutation.
