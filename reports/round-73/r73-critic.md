# R73 critic — CONSUMER CLASS (pw-cat + mpv): proposed claim falsified pre-landing; the r73 author diff was ABSENT for the whole critic window; pw-cat forks on FILENAME (`.snd`), not on seekability; only mpv×dec_hcom forks on seekability (1/13 members)

Seat: **critic** (leaf). Wave `shokunin-train-20261101-w12`, round 73, audio lane.
Lane repo `~/Projects/shokunin/audio-shokunin`. Host `plazir27`; system clock
**2026-10-14 14:34–14:46 UTC** (local `-03`; wave-label date differs — recorded, not a claim).
HEAD at start `50f55eb`, at end `f5d7faf` (r72 reviewer-fold landed mid-window, 14:38Z —
not mine; fixture blob changed `df1e5bec…`→`b068dbb5…` by that commit only).
Toolchain re-read this session: `pw-cat` libpipewire **1.6.8** (`pw-play`→`pw-cat`),
`mpv` **v0.41.0** (libavformat **63.1.101**), `sox` (txw control), pipewire daemon live
(pids 1905/2290/1906; `pactl` proto 35). Scratch/receipts: `corpus/live/r73-critic/`
(276 files; `matrix.tsv` sha256 `f2fdc112…`, `controls.tsv` sha256 `c7658054…`).
No tracked file modified; no git mutation.

## 1. Landing state — nothing was landed to falsify; falsification targets the proposed claim + frontier basis

Checks (all receipts in `corpus/live/r73-critic/`; sibling-verified independently by r73-scribe at 14:36Z):

- `grep -c 'probe-consumers-r73' corpus/fixtures/measure_audio.py` → **0** at 14:34Z, 14:35Z,
  14:38:55Z, 14:40:22Z, 14:40:35Z…14:41:25Z (6×10s poll), 14:41:37Z, and 14:42:23Z…14:46:03Z
  (12×20s poll — end of critic window).
- fixture blob `b068dbb5cb4966ada05fb596960122d6f416d846` == `HEAD:corpus/fixtures/measure_audio.py`
  (no tracked-fixture modification; `git status --porcelain corpus/fixtures/` empty).
- `corpus/live/r73-author/` absent through 14:38:55Z; first seen 14:39Z (`scratch/mpv-{rfd,pipe}-hcom.log`
  only — author mid-measurement, stdin `-` legs). `reports/round-73/r73-author.md` never appeared.
- `reports/round-73/` contains only sibling reports (`r73-scribe.md` 14:36Z, `r73-simplifier.md` 14:40Z,
  `r73-scout.md` 14:42Z).

Consequence: the "insertion-only / prior rows byte-stable" gate is **not exercisable** (nothing inserted);
all r73 consumer numbers in the author arm are still pending. The falsification below therefore attacks
the *proposed* claim (brief §MOVE) and the frontier claims (`ports/frontier/fb-pipewire.md`, the file the
brief cites as `reports/frontier/fb-pipewire.md` — **that path does not exist**; `reports/frontier/` holds
only `fa-sndfile.md`. Receipt-path defect, minor) that the harness would encode.

## 2. Measured matrix — 13 members × {pw-cat, mpv} × {file, fifo} = 52 legs (`matrix.tsv`)

Commands: `pw-cat -p <file|fifo>` and `mpv --no-config --vo=null --ao=null --audio-display=no
--really-quiet --log-file=<log> <file|fifo>`, all under `timeout -s KILL 20`; fifo writer = `cat member > fifo`.
rc vocabulary measured: pw-cat 0=plays / 1=open-or-format fail; mpv 0=played / 2=load-or-zero-data failure.

| member | pw-cat file | pw-cat fifo | mpv file | mpv fifo |
|---|---|---|---|---|
| posttable_nomatch | 1 | 1 | 2 | 2 |
| txw_piperefuse | 1 | 1 | 2 | 2 |
| dec_act | 0 | 0 | 0 | 0 |
| dec_hcom | 0 | 0 | **2** | **0** |
| extsuffix_wav | 1 | 1 | 2 | 2 |
| extsuffix_bin | 1 | 1 | 2 | 2 |
| extsuffix_txw | 1 | 1 | 2 | 2 |
| extsuffix_f32 | 1 | 1 | 2 | 2 |
| extsuffix_snd | **0** | **1** | 2 | 2 |
| lengate_gsrt_24 | 1 | 1 | 2 | 2 |
| lengate_gsrt_25 | 1 | 1 | 2 | 2 |
| lengate_hcom_131 | 0 | 0 | 0 | 0 |
| lengate_hcom_132 | 0 | 0 | 2 | 2 |

**Exactly two transport forks exist in 52 legs**, with *different* drivers (§3). All canonical-9 members
(`TRANSPORT_R72_MEMBERS`, `measure_audio.py:735`) plus 4 lengate extras covered. Mechanisms per leg
(3rd column `matrix.tsv`): dec_hcom/mpv/file = `refresh-seek-EPERM` (`Seek failed (Operation not permitted)`
then `EOF reached`, `finished playback, no audio or video data played (reason 4)`; log
`mx-mpv-file-dec_hcom.log:175-203`); dec_hcom/mpv/fifo = `Stream is not seekable` → decoder `hcom` selected,
AO null, `finished playback, success` (`mx-mpv-fifo-dec_hcom.log:165-218`).

## 3. Falsifications

### F1 (primary) — "consumer verdicts partition by mandatory-seek vs stream-consume polarity" is over-strong / falsified as stated

- Only **1 of 13** members forks on stream seekability in the whole consumer matrix: mpv × dec_hcom
  (seekable→rc2, pipe→rc0). **pw-cat shows 0/13 seekability forks.**
- pw-cat's single fork (`extsuffix_snd`) is **not seekability-driven**. 2×2 control on the identical
  `.snd` bytes (`controls.tsv`, `snd_2x2.sh`):

  | | named `m.snd` | unnamed `m.dat` |
  |---|---|---|
  | seekable regular file | rc=0 (119 ms) | rc=1 "Format not recognised" |
  | non-seekable fifo | rc=0 (122 ms) | rc=1 "Format not recognised" |

  Verdict = f(filename extension); seekability is orthogonal. Extension controls on fifo (`controls.tsv`):
  `f.snd` rc=0, `f.SND` rc=0 (case-insensitive), `f.wav` rc=1, `f.fifo` rc=1 — all the same bytes
  (five round-69 members are byte-identical, sha256 `f073e70a…`, verified against committed blobs).
  Library corroboration: `sndfile-info` on a fifo named `g.snd` opens (`Seekable: FALSE`, rate 8000;
  `sndfile-info-pipe-named.txt`) — the same extension fallback r72 measured for the named `.snd` arm.
- So the consumer class does not partition by one polarity; the correct statement is *member-level
  mechanism*, not *consumer-class polarity*: pw-cat's only fork is the r69/r72 **name axis** (the
  decoder axis!), not a consumer/realtime axis.
- The "opposite of the decoder axis" clause is true only for the mpv×dec_hcom pair (non-seekable helps)
  versus the decoder-side mandatory-seek gate: sox × txw_piperefuse re-measured this session —
  file rc=0 / fifo rc=2 `sox FAIL formats: can't open input file …: input must be a file, not a pipe`
  (`sox-file-txw.err`, `sox-fifo-txw.err`). It does not generalize across the consumer class.

### F2 — frontier `fb-pipewire.md:27` "Format selection is pure content sniff … **No suffix/name axis**" (pw-cat) is falsified

Same bytes, five names, both transports: `.snd`/`.SND` rc=0 vs `.wav`/`.bin`/`.f32`/`.txw`/anonymous
rc=1 under pw-cat (matrix rows `extsuffix_*`; controls rows `pwcat-seek-named` vs `pwcat-seek-unnamed`,
`pwcat-pipe-f.{snd,SND,wav,fifo}`). The frontier tested only `extsuffix_nomatch.{wav,txw}` for pw-cat
(fb-pipewire.md:47) and never the canonical named-fork member `.snd` — the claim is scoped to a member
set that cannot show the axis.

### F3 — mechanism-attribution caution (frontier table would mislabel if pooled)

`lengate_hcom_132` is rc=2 on **both** arms via `Found 'hcom' at score=100` → `avformat_open_input() failed`
(twice) → `unrecognized file format` (`mx-mpv-{file,fifo}-lengate_hcom_132.log`) — a content/length-gate
failure, **not** the refresh-seek mechanism; its sibling 131 (1 byte shorter) is detected as `wav` and
plays on both arms (rc=0). Do not pool 132 under a "seek" column, and do not read "hcom detected ⇒
seek fork" as a class rule.

## 4. Frontier claims that survived re-measurement (corroborations, with receipts)

- Daemon gate precedes input open: `PIPEWIRE_RUNTIME_DIR=emptyrt pw-cat -p <file>` rc=1 in 2 ms,
  `error: pw_context_connect() failed: Host is down`; with a **no-writer fifo** (which blocks forever
  with a daemon) rc=1 in 2 ms (`ctl-nodaemon-file.*`, `ctl-nodaemon-nowriterfifo.*`). Daemon live now
  (`env.txt`: pids 1905/2290/1906, pactl proto 35).
- Playback-paced consumption: tone4s.wav (64078 B, 4 s) file arm rc=0 wall **4046 ms**; fifo instant-dump
  rc=0 wall **4021 ms**; fifo 1600 B/0.2 s trickle (8 s delivery) rc=0 wall **8044 ms** — streams as
  bytes arrive, no underrun abort (`ctl-pace-*`).
- Writer-attach semantics: no writer → blocks in `open()`; SIGTERM at 3 s ignored, SIGKILL at +3 s →
  rc=137 wall 6001 ms (`ctl-nowriter.*`); empty writer → rc=1 `Format not recognised` in 3 ms.
- `--target 0` unlinked-stream hang → rc=137 after 5 s KILL (`ctl-target0.*`).
- mpv inverted fork mechanism and name-independence: hcom bytes as seekable `h.dat` → rc=2 with
  refresh-seek-EPERM; hcom bytes over fifo named `h.wav` → rc=0 non-seekable decode (`ctl-mpv-seek-unnamed.log`,
  `ctl-mpv-pipe-named.log`); `fd://0` from a stdin file-redirect is seekable → rc=2 EPERM (`ctl-mpv-fd0.log`).
- mpv has no extension fallback: fifo named `s2.snd` → rc=2 (`ctl-mpv-pipe-named-snd.log`).

## 5. Impacted axes

- **r73 consumer-class claim** (seekability-polarity partition): falsified as stated; must be restated
  member-level (two mechanisms, one member each on this corpus).
- **Frontier pw-cat arm** (`fb-pipewire.md:27`, and the "transport-invariant" phrasing at :50 when read
  as a class rule): name axis present; `.snd` must be in the pw-cat member set.
- **Harness constants**: any per-consumer "transport-sensitive" boolean, any `pw-cat ⇒ transport-invariant`
  assertion, and any pw-cat timeout ≤6 s (no-writer legs are SIGTERM-immune; KILL mandatory) would be wrong.

## 6. Smallest safe correction

1. Claim (replace brief §MOVE sentence): *"Consumer verdicts fork per member, not per class: (a) mpv ×
   seek-gated lavf demuxers (dec_hcom): seekable→refresh-seek-EPERM→rc2, non-seekable→decode rc0
   (name-independent; opposite direction to sox's txw pipe-refusal); (b) pw-cat × the named-fork member
   (.snd): verdict is filename-extension-driven on both transports (named .snd/.SND rc0, anonymous rc1) —
   the r69/r72 name axis, not a transport axis. All other 11 members: transport-invariant under both consumers."*
2. If/when the author arm lands: include the canonical 9 (incl. `extsuffix_snd`) in the pw-cat arm, plus
   the 2×2 controls (named/unnamed × file/fifo) so the name/seek confound is separated in-receipt
   (`snd_2x2.sh`, `controls.sh` are ready reproducers, but the insertion must be in the tracked fixture).
3. Receipt hygiene for the landed diff: pw-cat rc∈{0,1} (+137 = harness kill), mpv rc∈{0,2}; `timeout -s KILL`
   everywhere; ≥6 s for no-writer legs; ≥10 s for trickle legs; never `--target 0`; record the daemon-gate
   receipt (`PIPEWIRE_RUNTIME_DIR=emptyrt`) as the viability-conditional leg.
4. Fix the brief's frontier path (`ports/frontier/fb-pipewire.md`, not `reports/frontier/…`) in the next
   dispatch text — no artifact depends on it today.

## 7. Limits

One host (`plazir27`), daemon live with sinks suspended; EPERM source not straced (mpv log order only);
4 extra members beyond the canonical 9 (lengate 24/25/131/132) are this-seat additions, not contract;
sibling scratch (`r73-scout/-reviewer/-boundary`) was not used as evidence. F1/F2 are correctable
text/member-set defects, not judge-level tradeoffs; no runtime contract or axis table was modified by this seat.
