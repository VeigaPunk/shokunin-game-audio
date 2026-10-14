# R74 critic (audio) — the 4-condition no-seek rule has a counterexample demuxer (acm), the wound-shape corollary is falsified on its own anchor (multi-packet hcom still rc=2/zero-data), and the r73 class-polarity wording is still in the fixture

Seat: **critic** (leaf). Wave `shokunin-train-20261101-w13`, round 74, audio lane.
Lane repo `~/Projects/shokunin/audio-shokunin`. Host `plazir27`; system clock
**2026-10-14 15:19–15:26 UTC** (local `-03`; wave-label date differs — recorded, not a claim).
HEAD **`1ba8103`** (r73 report-last) — unchanged all session; no tracked file modified by this seat.
Toolchain re-read this session: `mpv v0.41.0` (libavformat **63.1.101**), `ffmpeg n9.0.1`
(`libavutil 61.1.101`), `pw-cat` libpipewire 1.6.8, Python 3.14.7.
Source-truth inputs (fetched this session, not from the repo): `FFmpeg n9.0.1` tarball
sha256 `195d54bebe1a27f84d77f4b989d193466f305b355da92292766a69f16880b18a`, `mpv v0.41.0`
tarball sha256 `ee21092a5ee427353392360929dc64645c54479aefdb5babc5cfbb5fad626209`
(extracted under `/tmp/r74crit/`; source citations below are from these trees).
Scratch + receipts: `corpus/live/r74-critic/` — `cells.tsv`
sha256 `453ca5d622f955253596836089c9464eb8609ad338eb9f74acdf7b05366c1dea`
(7 cells × {file,fifo}, raw mpv logs + raw PCM under `cells/`), `probe-results.json`
sha256 `5a70f1cce3bc90ec8cad0192dc810cdd8ea0f669f4efae10c74df2d4452a4026`,
runners `r74c_probe.py` sha256 `ea021c1a…`, `receipts.py` sha256 `53f4e642…`.

## 0. Landing state — author diff ABSENT; replay is pending, not claimed

- `git status --porcelain` (tracked): **empty** at 15:19Z, 15:22Z, 15:24Z, 15:25Z, 15:25:49Z.
- `grep -c 'probe-lavfsweep' corpus/fixtures/measure_audio.py` → **0**; fixture blob still
  `9b6e836…` == HEAD (matches r74-scribe's independent landing checks, `reports/round-74/r74-scribe.md:59-63`).
- `reports/round-74/` contained only `r74-scribe.md` (landed 15:24Z) at every check.
- Author scratch `corpus/live/r74-author/` was mid-flight from ~15:19Z (`mk_members.py`,
  `members/lavf_{iss,iss_multi,apc,acm,adx,aifc}`, per-member `log-file-*.log`, `log-pcm-*`).
- **Consequence:** the required replay/mutant of the author diff is **not exercisable this
  window**; §9 records the mutants I ran against the *declared* surface instead, plus the
  author-scratch cell that already exists. If the diff lands later, the replay recipe is
  the two commands in §9.

## 1. Attack surfaces (verbatim, from the artifacts, not from memory)

- **4-condition rule** (`xconnector.md:16-19`, re-stated in `tasks/audio-author.md:6-9`):
  "fork requires ALL of (1) content-probe detection; (2) demuxer has no `.read_seek` and no
  `.read_timestamp`; (3) no AVFMT_GENERIC_INDEX; (4) codec not pcm_*+block_align (mpv PCM
  seek hack)". Predicted FORK: **iss, apc, acm**.
- **Wound-shape corollary** (`xconnector.md:29-32`; author brief line 19-21): "seekable-arm
  rc=2 requires find_stream_info to consume the whole stream — a MULTI-PACKET member on a
  no-seek demuxer predicts head-truncation rc=0 fork, not rc=2."
- **Consumer-polarity overclaim residue** (`corpus/fixtures/measure_audio.py:988-994`,
  constant-area r73 block, quoted in §5): class-partition wording + wrong driver attribution.

## 2. Method

Own member builder (from the n9.0.1 demuxer sources, hand-built headers) + own mpv runner
(no import of `measure_audio.py` and no reuse of sibling runners), 2 transports {file, fifo},
`timeout -s KILL 15`; measurement = rc **+ decoded bytes** written by `--ao=pcm`
(raw u8, `--ao-pcm-waveheader=no`) + parsed lavf log fields. The decoded-byte column is the
point: rc alone and `seek_failed` alone are both forgeable/ambiguous (§6).

| cell (member) | file arm | fifo arm | shape |
|---|---|---|---|
| A hcom 1 pkt (600 B, r73 anchor) | rc=2, pcm=0, `no data` | rc=0, pcm=3520 | rc fork, file loses all |
| B hcom **4 pkt** (16984 B, 5 packets) | rc=2, pcm=0, `no data` | rc=0, pcm=134592 | **rc fork, file loses all — corollary predicted rc0 head-truncation** |
| C iss 6 pkt | rc=0, pcm=8128 | rc=0, pcm=12192 | data fork, loss = 4064 B = **2 packets** |
| D acm multi (subfmt 0x7700) | rc=0, pcm=800 | rc=0, pcm=800 | **NO fork (rule predicted fork)** |
| E adx control (GENERIC_INDEX) | rc=0, pcm=44160, no `Seek failed` | rc=0, pcm=44160 | no fork, refresh seek **succeeded** |
| F apc 2 pkt | rc=2, pcm=0 | rc=0, pcm=20480 | rc fork (loss = all = 2 pkt) |
| G iss 40 pkt | rc=0, pcm=77216 | rc=0, pcm=81280 | data fork, loss = 4064 B = **2 packets (constant)** |

(full rows incl. `fsi_bytes`, `refresh_seek`, `seek_failed`, log sha16 in `cells.tsv`.)

## 3. F1 (HIGH) — counterexample demuxer: **acm satisfies all 4 conditions and does not fork**

**Source.** `libavformat/acm.c:67`:
`.p.flags = AVFMT_NOBINSEARCH | AVFMT_NOGENSEARCH | AVFMT_NO_BYTE_SEEK | AVFMT_NOTIMESTAMPS`
— no `.read_seek`, no `.read_timestamp`, no `AVFMT_GENERIC_INDEX`, probe present, codec
`AV_CODEC_ID_INTERPLAY_ACM` (not `pcm_*`). The rule's conditions (1)-(4) therefore all hold.
But `libavformat/seek.c` (n9.0.1) gates the generic-search fallback on a **different flag**:

```
seek.c:628-636  (seek_frame_internal)
    if (ffifmt(s->iformat)->read_seek) { ... } else ret = -1;
    if (read_timestamp && !(flags & AVFMT_NOBINSEARCH)) { ff_read_frame_flush; return ff_seek_frame_binary(...); }
    else if (!(s->iformat->flags & AVFMT_NOGENSEARCH)) { ff_read_frame_flush(s); return seek_frame_generic(...); }
    else return -1;            <-- acm lands here: -1 with ZERO consumption, no flush, no re-read
```

`AVFMT_GENERIC_INDEX` (rule condition 3) is instead the **index-building** flag
(`libavformat/demux.c:1501`: index entries are added only when it is set) — it decides
whether `seek_frame_generic` can *succeed* (control E), not whether the fallback *runs*.
So the rule needs **both** flags, and condition (3) as written misses the acm class.

**Measurement (my receipts).** D row: file rc=0 pcm=800 / fifo rc=0 pcm=800 — identical
decoded bytes; the only file-arm differences are the verbose refresh-seek lines
(`refresh seek to 0.000000`, then `[v][lavf] Seek failed (Operation not permitted)`; the seek
is attempted and fails, but with zero consumption the packet buffer survives; playback
decodes the same 800 B).
Corroboration (sibling scratch, labelled as such): `corpus/live/r74-reviewer/matrix-part1.json`
(`my_acm_multi`: rc=0 + `success (reason 0)` on all four transports);
`corpus/live/r74-scout/runs/mpv-matrix-r74b.json` (`acm_2000blk`: 32000/32000 B, rc 0/0);
the author's own scratch `corpus/live/r74-author/log-file-lavf_acm.acm.log:183-186,279`
(`refresh seek to 0.000000`, `Seek failed (Operation not permitted)`,
`finished playback, success (reason 0)`).

**Source-pinned, unmeasured members of the same class** (all inside the 4-condition set of
78 demuxers I enumerated over `libavformat/*.c`): `apac`, `bonk`, `hnm`, `osq`, `shorten`,
`wavarc` — each sets `AVFMT_NOGENSEARCH` and has no read_seek/read_timestamp/GENERIC_INDEX,
so each is predicted **no fork**, contra the rule.

**Independent corroboration (report landed 15:26Z, not my evidence):**
`reports/round-74/r74-scout.md:21-26, 96-120, 133-152` — same host, separate harness
(`mpv_matrix.py` sha `b7b25904…`) and separate hand-built members reach the same acm
invariance (`acm_64blk` 1024/1024, `acm_2000blk` 32000/32000) and the same refined gate
("`acm` is immune because it sets `AVFMT_NOGENSEARCH` → early `return -1` with no flush").
The scout's refined condition set (3′) keeps only `not NOGENSEARCH`; my reading keeps
**both** flags because `AVFMT_GENERIC_INDEX` is what lets the fallback *succeed* (control E,
scout adx/wv rows) — the two statements are compatible, mine is the conservative one.

Repro: `cd corpus/live/r74-critic && python3 receipts.py` (cell D), or by hand:
`mpv --no-config --vo=null --ao=pcm --ao-pcm-file=/tmp/d.raw --ao-pcm-waveheader=no --really-quiet --log-file=/tmp/d.log c5-acm-multi.acm; echo rc=$?` vs the same over a fifo fed by `cat c5-acm-multi.acm > fifo`.

## 4. F2 (HIGH) — wound-shape corollary: prediction falsified on the anchor; cause misattributed

**(a) Prediction falsified.** The corollary says a multi-packet member on a no-seek demuxer
yields "head-truncation rc=0", not rc=2. Measured on the demuxer the whole claim is anchored
on: **B hcom-4pkt (5 packets, 16984 B) → file rc=2, pcm=0, `got EOF with no data before it`**;
fifo rc=0, pcm=134592. Same for **F apc-2pkt** (file rc=2, pcm=0) and, per the scout's
independent matrix, `apc_multi` (rc=2, pcm=0) and `apc_1pkt` (rc=2, pcm=0). The rc0
head-truncation shape exists only for members whose packets carry usable dts **and** enough
packets to survive the loss: iss 6 pkt / 40 pkt (C/G), scout `iss_4pkt`/`iss_40pkt`/`apc_3pkt`
(loss exactly 2 packets each), and it disappears at ≤2 packets (F, apc_1pkt, iss_1pkt → rc=2).

**(b) Cause misattributed.** The file arm's loss is produced by mpv's refresh-seek path, not
by `find_stream_info`:
- the seek is issued iff the demuxer is seekable (`demux/demux.c:3915-3916`
  `bool seekable = demux->desc->seek && demux->seekable && !demux->partially_seekable;`,
  `:3976` `refresh seek to %f`);
- the seek call runs **twice** on failure — `demux/demux_lavf.c:1391-1397` retries without
  `AVSEEK_FLAG_BACKWARD`;
- each attempt first runs `ff_read_frame_flush` (`seek.c:632-636`), which **discards the
  packet buffer that `find_stream_info` filled**, then `seek_frame_generic` rewinds to
  `si->data_offset` and consumes the head (`seek.c:526-583`), breaking only on
  `pkt->dts > timestamp && AV_PKT_FLAG_KEY` (`seek.c:566`), else reading to EOF.
- Discriminating evidence that fsi consumption is **not** the driver: B's fifo arm has the
  same `fsi=16984` (= whole stream read by `avformat_find_stream_info`, both arms) yet
  delivers all 134592 B — lavf buffers the packets fsi reads; and C/G file arms are rc0 with
  a constant 2-packet loss although fsi also read the whole file (3111 / 20521 B).
  Packet-level discriminator (ffprobe on my members): hcom packets `dts=N/A flags=K__`
  (so the loop never breaks → whole stream consumed → rc2 at any packet count); iss packets
  `dts=256,512,…` and apc `dts=0,92160,…` (loop breaks → bounded loss).
  The author's own in-flight scratch already carries this shape for a 256-packet iss member:
  `log-pcm-file.log` / `log-pcm-fifo.log` with `/tmp/out-file.wav` = 516196 B vs
  `/tmp/out-fifo.wav` = 520260 B → Δ = **4064 B = 2 packets** (not a fraction of 256).

**(c) Corrected law (bounded to this host/version).** File-arm loss = (head consumed by the
generic-search loop per `av_seek_frame` attempt) × 2 attempts (demux_lavf.c:1391-1397);
per-attempt head = up to the first packet with (`dts > ts` ∧ KEY), else EOF. Measured:
**whole stream** for NOPTS-dts hcom (any size) → rc=2; **exactly 2 packets** for dts-carrying
iss/apc (constant across 4/6/40-packet iss and 3-packet apc, my C/G + scout rows) → rc0 with
head truncation, rc2 only when the stream has ≤2 packets; **zero** for the NOGENSEARCH class
(acm) → no fork. `find_stream_info`'s own consumption is rewound (file arm) or replayed from
the buffer (non-seekable arm) and cancels out.

## 5. F3 (MEDIUM) — consumer-polarity residue and two misattributions still on disk

**(a) Stale class-polarity wording, fixture constant block** `corpus/fixtures/measure_audio.py:988-994`:

```
988 #   mpv detects by content via libavformat on every transport but forks
989 #   DECODE on the stream's seekable bit: a seekable hcom stream gets a
990 #   "refresh seek to 0" the hcom demuxer refuses EPERM (zero data -> rc=2),
991 #   while the same bytes on a non-seekable stream skip the refresh and
992 #   decode (rc=0) — the INVERSE polarity of the decoder {named} axis.
993 # Claim under test: consumer verdicts partition by mandatory-seek vs
994 # stream-consume polarity — opposite of the decoder axis.
```

The r73 reviewer-fold D12 (`3b4c3b7`) restated only the **main() block** comment
(`measure_audio.py:1799-1810` region, "the briefed class-polarity partition was falsified
corpus-wide"); this constant-area copy still carries the falsified claim. Three defects:
(i) "forks DECODE on the stream's seekable bit" — layer misattribution: the fork is in the
demux/seek layer (refresh seek); on the starved arm the decoder never receives a packet;
(ii) "the hcom demuxer refuses EPERM" — wrong variable attribution: `libavformat/hcom.c:88-93`
defines **no** `.read_seek`/`.read_timestamp` at all; the `-1` comes from `seek_frame_generic`
returning -1 because no index entries exist, and "Operation not permitted" is merely
`av_strerror(-1)` = EPERM — a synthetic error code, not a demuxer refusal (r73 adjudicator's
"0 failing syscalls" strace stands);
(iii) "Claim under test: … partition by mandatory-seek vs stream-consume polarity" — the
adjudicated r73 verdict is member-local forks, driver-diverse (`r73-adjudicator.md:14-31`).

**(b) Condition (4) rationale is misattributed.** `xconnector.md:18-19` explains condition
(4) as "mpv PCM seek hack rescues — why dec_act stayed invariant". The r73 `dec_act` mpv legs
never exercised the act demuxer: the member is detected as **wav**
(`corpus/live/r73-author/scratch/mpv-file-act.log:165` `Detected file format: wav`), so wav's
own `ff_pcm_read_seek` handled the refresh seek. Also, reading `demux/demux_lavf.c:1364-1387`,
the PCM hack **cannot** rescue a failing refresh seek: it reads one packet to learn the packet
size and aligns the target, then still calls the failing `av_seek_frame` (and the extra read
*adds* consumption). I did not build a `pcm_*+block_align` no-seek member this window
(9 candidates carry a PCM codec id in the 4-condition set: 4xm, ads, electronicarts, genh,
ipmovie, msf, tiertexseq, wc3movie, siff — siff's `block_align` is a demuxer-context field,
not `codecpar->block_align`, so only 8 satisfy the hack's own condition) — condition (4) is
**unfalsified here, but unsupported by the code path**; bounded claim.

## 6. Harness trap that the author diff must not inherit (HIGH for the landing)

`measure_audio.py:1169-1170` keys the mpv fork groups on
`(exit_code, lavf_detected, seek_failed)`. Under that key **acm reads as a fork** while rc and
decoded bytes are byte-identical (file: `seek_failed="Operation not permitted"`; fifo:
`seek_failed=None`) — a false positive created by an *unforged* log line. The scribe's
independent audit found the same key is forgeable with one appended line
(`r74-scribe.md`, F-b). If `--probe-lavfsweep-r74` reuses the r73 key (or any key containing
`seek_failed`), the landed matrix will report `acm: fork=true` and the r74 report will
contradict its own raw logs. Note also control E: for adx the refresh seek **succeeds**
(`seek_failed` absent) — "refresh seek attempted" is not a failure witness either.

## 7. Impacted axes

- **X2 rule text** (xconnector.md:16-19 + author brief ARM A): sufficiency false (acm + 6
  source-pinned demuxers); condition (3) targets the wrong flag for the run/succeed decision.
- **Wound-shape corollary** (xconnector.md:29-32): prediction false on hcom/apc; causal
  sentence ("requires find_stream_info to consume the whole stream") false.
- **Predicted-fork list** in the brief: `acm` must move to the predicted **no-fork** side;
  the multi-packet cell must be conditioned on packet dts/KEY (per-demuxer), not on count.
- **Fixture residue** at `measure_audio.py:988-994` (r73 class-polarity + driver attribution).
- **Harness keys**: any lavfsweep fork key containing `seek_failed` (r73 key at `:1169-1170`).

## 8. Smallest safe corrections

1. **Rule (text only):** replace condition (3) with two conditions and re-state sufficiency:
   fork requires (1) probe detection; (2) no working seek path — no `.read_seek`, no
   `.read_timestamp`(+`NOBINSEARCH`), no usable index entries, **and not
   `AVFMT_NOGENSEARCH`**; (3) the generic-search fallback actually consuming the stream head
   (packet dts/KEY property); (4) codec not `pcm_*+block_align` (untested; keep with a
   "rationale unsupported by demux_lavf.c:1364-1387" note). Move acm/apac/bonk/hnm/osq/
   shorten/wavarc to predicted no-fork.
2. **Corollary (text only):** "the seekable arm loses exactly the head the *failed refresh
   seek* consumes — the whole stream when packets carry no dts (hcom: rc=2/zero data at any
   packet count), a bounded head (measured 2 packets, one per `av_seek_frame` attempt) when
   packets carry dts+KEY (rc0 with head truncation, rc2 if the stream is ≤2 packets)."
3. **Fixture residue:** do **not** let the insertion-only author diff touch bytes 981-994;
   route the restatement to the r74 reviewer/simplifier fold (same mechanism as D12), or
   record it as a carried correction for the next round.
4. **Harness:** `--probe-lavfsweep-r74` must key forks on `(rc, decoded_bytes | no_data)`,
   keep `seek_failed`/`refresh_seek` as non-keyed columns, and persist the raw mpv log per
   leg (the r73 family has none — scribe D1); without that, the acm cell lands mislabelled.

## 9. Mutants run this window (author diff pending) + replay recipe

- **Multi-packet mutant on the anchor** (B): hcom 600 B + 16384 B appended → 5 packets; the
  corollary's predicted rc0 did not appear (rc2/pcm0). Control A unchanged.
- **Size-scaling mutant** (G vs C): iss 40 pkt vs 6 pkt → loss constant at 2 packets (4064 B),
  so the loss is a head constant, not a fraction.
- **Collapse-control mutant** (probe run): `c6-acm-multi-s0.acm` (decoder-failing subformat 0)
  → rc=2, pcm=0 on **both** arms — the acm no-fork in D is not an artifact of successful
  decoding, and a failing member forks on nothing.
- **Index control** (E): adx (GENERIC_INDEX) → refresh seek succeeds, pcm equal.
- **Replay recipe when the diff lands** (not run — diff absent at write time):
  `python3 corpus/fixtures/measure_audio.py --probe-lavfsweep-r74` then replay the receipt's
  acm/iss/apc rows against `cells.tsv` above; mutants = (i) append `Seek failed (Operation
  not permitted)` to an acm fifo log and re-parse (must not create a fork under the corrected
  key), (ii) feed the 5-packet hcom member (B) and assert the row is rc2/pcm0, not rc0.

## 10. Limits

One host; `mpv 0.41.0` + lavf `63.1.101` + ffmpeg `n9.0.1` source-matched. Members are
hand-built (fabricated but demuxer-validated headers); the measured shapes are properties of
demuxer+mpv on these members, not byte-fidelity claims. The 6 NOGENSEARCH demuxers beyond acm
are source-pinned only. The per-attempt split of the 2-packet loss (1+1 vs 2+0 across the two
`av_seek_frame` calls) is not pinned — only the constant total (5 cells, two seats). Condition
(4)'s PCM-hack rescue is unprobed. The `mpv --start=N` position-fork cell (brief ARM A (ii))
is out of this seat's assigned scope and was not probed. Sibling scratch was read as landing
state / corroboration only; my evidence is `corpus/live/r74-critic/` + the two fetched source
trees.
