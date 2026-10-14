# R73 reviewer — landed consumer arm (`febf34b`) reviewed: 466+/3- insertion-only, 36/36 receipt cells independently reproduced, 2 member-local forks confirmed with the arm's own name-axis control; proposed class claim FALSIFIED as stated; receipt not byte-stable (1 ms `wall_s` leaf); pw-cat verdicts are libsndfile's (name-gated `.snd`), mpv's EPERM is lavf-synthetic (strace: 0 failing syscalls)

Seat: **reviewer** (leaf, report-only). Wave `shokunin-train-20261101-w12`, round 73, lane audio.
Repo `/home/vgpnk/Projects/shokunin/audio-shokunin`. Host `plazir27`; system clock
**2026-10-14 11:35–12:02 -03** (14:35–15:02 UTC).
HEAD at open `50f55eb`, `f5d7faf` at 11:38:20 (r72 reviewer-fold), **`febf34b`** at 11:57 (the r73 arm,
operator-committed). The arm's own revision under review: `corpus/fixtures/measure_audio.py` content
sha256 **`834823ea5a85c63e6e1a79db22399c0c781bed163ea9c3ca627b6a4e8c0df88a`** == `git show HEAD:…`
(verified by `cmp`); the pre-landing baseline was taken on `b765ee76…` == HEAD `f5d7faf`.
Toolchain: `pw-cat`/`pw-play` libpipewire **1.6.8**, `mpv` **v0.41.0** (libavformat 63.1.101 / ffmpeg
n9.0.1), libsndfile 1.2.2, CPython 3.14.7. PipeWire daemon live throughout (`pipewire` 1905,
`wireplumber` 1906, `pipewire-pulse` 2290; `pactl` → "PulseAudio (on PipeWire 1.6.8)", 4 sinks).
Write scope honoured: this report + `corpus/live/r73-reviewer/` only; no tracked file modified by this
seat, no git mutation. Fixture receipts written by *running* the fixture land under `corpus/live/runs/`
(the fixture's own output path, same convention the r72 reviewer used, `reports/round-72/r72-reviewer.md:6-9`).

## 0. What is under review (exact) — and the tree movement

The arm landed **at 11:50** (after 15 minutes of my window) and was committed by the operator as
**`febf34b`** ("r73: CONSUMER class expansion — pw-cat (PipeWire realtime) + mpv (lavf) on the 9-member
transport matrix", `466 insertions(+), 3 deletions(-)`). My review anchors on the **committed content**:
fixture content sha256 **`834823ea5a85c63e6e1a79db22399c0c781bed163ea9c3ca627b6a4e8c0df88a`** ==
`git show HEAD:corpus/fixtures/measure_audio.py` (verified `cmp`). Diff: `corpus/live/r73-reviewer/
r73-fixture-latest.diff`.

**Tree movement inside the window (disclosed).** The arm moved twice while I reviewed it:
`1d0b2d34…` (11:50, arm + flag/mode/suffix, no ops name-axis cell) → `834823ea…` (11:54, +`pwcat_name_axis`
2×2 control, +20 lines of ops assertions) → committed `febf34b` (11:57). Receipts taken against the
intermediate revision (`…T145113997684Z`, `…T145204328075Z`) are **stale** and are not used as evidence;
every landing number below is from the two runs against `834823ea…` (`…T150022971775Z`, `…T150103164753Z`)
or from my independent harness. A pre-landing baseline (`replay-pre.json`, fixture `b765ee76…` = HEAD
`f5d7faf`) was captured before the edit, so the prior-row gate is a real pre/post pair.

**Finding D0 (process).** The arm landed 15 min after dispatch and 8 min before the wave's adjudication;
`reports/round-73/r73-author.md` **never appeared** (author report still pending at adjudication,
`reports/round-73/r73-adjudicator.md:52-53`). The diff is therefore reviewed from the fixture and receipts
only — the author's own claim text is not available to check against the receipt, and no author self-verify
was published.

## 1. Independent reproduction — my own harness, not the frontier's

Harness (all in `corpus/live/r73-reviewer/`): `consumer_matrix.py` → 9 canonical members
(`TRANSPORT_R72_MEMBERS`, `measure_audio.py:735`/`:557`) × {pw-cat, mpv} × {file, fifo} = **36 cells**,
one-shot writer feed, writer hold 1.0 s (the fixture's `fifo_writer_hold_s()` value, `measure_audio.py:285`),
`timeout -s KILL 15` per arm; run twice — once with my own fifo name (`my-matrix.json`, `matrix-out.txt`),
once with the **fixture's naming convention** (fifo in a temp dir named with the member basename, as
`measure_audio.py:878` and `:611` do; `my-matrix-fixture-naming.json`, `matrix-fixture-naming-out.txt`).

| member | pw-cat file | pw-cat fifo | mpv file | mpv fifo |
|---|---|---|---|---|
| posttable_nomatch | 1 Format not recognised | 1 same | 2 unrecognized | 2 unrecognized |
| txw_piperefuse | 1 unimplemented format | 1 same | 2 unrecognized | 2 unrecognized |
| dec_act | 0 | 0 | 0 (wav) | 0 (wav, not seekable) |
| dec_hcom | 0 | 0 | **2 refresh-seek-EPERM** | **0 (hcom, not seekable)** |
| extsuffix_wav | 1 | 1 | 2 | 2 |
| extsuffix_bin | 1 | 1 | 2 | 2 |
| extsuffix_txw | 1 | 1 | 2 | 2 |
| extsuffix_f32 | 1 | 1 | 2 | 2 |
| extsuffix_snd | 0 | 0 *(`.snd` fifo)* / 1 *(unnamed fifo)* | 2 | 2 |

- **Exactly one fork under the fixture's naming convention**: mpv × dec_hcom (file rc=2, fifo rc=0).
  pw-cat: 0 forks.
- With an **unnamed** fifo (my first run, and the frontier's `fifo1`/`fifo3` style) a second fork appears:
  pw-cat × extsuffix_snd, file rc=0 / fifo rc=1 — see D2/D3; it is **not** a transport fork.
- This matches the critic's independent 52-leg matrix (`reports/round-73/r73-critic.md:38-52`) on the
  canonical 9 cell-for-cell, and the boundary seat's 40-cell scratch matrix
  (`reports/round-73/r73-boundary.md`, verdicts.json `9f8bc309…`).

Decisive controls for the `.snd` row (`pwcat_snd_controls.py` → `pwcat-snd-controls.json`), same bytes
(`extsuffix_nomatch.snd`, sha256 `f073e70a…`), 2×2 + extension ladder:

| input | name | seekable | rc |
|---|---|---|---|
| fifo | `ctl-named.snd` | no | **0** |
| fifo | `ctl-named.au` | no | **0** |
| fifo | `ctl-named` (no suffix) | no | 1 "Format not recognised." |
| file | `ctl-noext-file` | yes | 1 "Format not recognised." |
| file | `extsuffix_nomatch.snd` | yes | **0** |
| file | `ctl-copy.au` | yes | **0** |

Verdict = **f(filename suffix)**; seekability is orthogonal. That is the r69/r72 *name axis* surfacing in
the consumer class, not a consumer/realtime axis.

**pw-cat is the third decoder wearing a drain.** Every pw-cat rejection string on the canonical 9 is a
byte-equal substring of the libsndfile r72 receipt's `error` field (5/5 rejects; accepts agree: dec_act,
dec_hcom, extsuffix_snd) — `pw-cat` stderr `sndfile: … : File contains data in an unimplemented format.` vs
`sndfile_txw_piperefuse_r72_probe.error` = `File contains data in an unimplemented format.` (same for
`Format not recognised.` ×4). The pw-cat arm therefore adds realtime/transport semantics only; it carries
**no new detection verdict**.

Supporting arms (all receipts in my scratch, commands in §7):

- **Playback pacing** (`replay_pacing2.py` → `replay-pacing2.json`): 4 s tone — file **3.99 s**, fifo instant
  dump **4.35 s** (playback-paced, not read-paced), fifo 1600 B/0.2 s trickle **8.51 s** (blocks when
  starved, no underrun abort), fifo `-a` raw **4.33 s**, empty writer → rc=1 `Format not recognised.`
- **Bounds** (`replay_pwcat_mpv.py pwcat-bounds` → `replay-pwcat-bounds.json`): no-writer fifo → **SIGKILL
  only** (rc=−9 at my 8 s bound; `timeout`'s SIGTERM is ignored); no-daemon `PIPEWIRE_RUNTIME_DIR=emptyrt` →
  **rc=1 in 0.0 s** with `error: pw_context_connect() failed: Host is down`, on the file arm *and* on a
  no-writer fifo (gate precedes input open — the fifo never blocks).
- **Operational traps** (`pwcat_probes.py` → `pwcat-probes.json`): `--target 0` unlinked stream → hangs
  (SIGKILL at 8 s); fifo named `probe-name.txw` carrying valid WAV bytes → rc=0 (content beats name when a
  header exists — the name axis is a *fallback*, not a first predicate); WAV bytes in a file named `.txw` → rc=0.
- **Writer-close semantics** (`pwcat_linger_proof.py`, `pwcat-linger-proof.json` + hold ladder): reader wall
  = hold + 0.21 s → **1.21 s (hold 1.0) / 3.21 s (hold 3.0) / 6.31 s (hold 6.0)**. pw-cat over a fifo exits
  when the **writer closes (EOF)**, not at the WAV data-chunk end.
- **mpv mechanism, straced** (frontier left this "not straced", `fb-pipewire.md:74`): `strace-mpv-file4.log`
  — member opened fd 11; `lseek(11,0,SEEK_END)=600`, `lseek(11,0,SEEK_SET)=0`; `read(11,"RIFF…",131072)=600`;
  then 5× `read(11,"",130472)=0`; **no failing syscall anywhere** → the `Seek failed (Operation not
  permitted)` is synthesized inside libavformat. Corroboration from the same library:
  `ffmpeg -v debug -ss 0.005 -i pair_dec_hcom.wav` → `[in#0/hcom] could not seek to position 0.005`,
  `pos: 600 bytes read:600 seeks:0`, **rc=0** — the hcom demuxer consumes the whole input at open and cannot
  seek, ffmpeg *tolerates* the refused seek while mpv treats its post-open refresh-seek as fatal
  (`refresh seek to 0.000000` → EPERM → `EOF reached` → `no audio or video data played`, rc=2).
  The fifo arm never attempts it (`Stream is not seekable.` → `success`, rc=0).
- **Flag-flip control** (`mpv_seekability_causal.py` → `mpv-seekability-causal.json`): mpv's own
  `--force-seekable=no` on the file arm does **not** suppress the refresh seek (still rc=2 EPERM), and
  `--force-seekable=yes` on the fifo does **not** induce it (still rc=0). The lever is the
  stream/demuxer seekability as lavf sees it, not mpv's player-level property.

## 1b. Landing review — committed `febf34b` (fixture `834823ea…`), replayed

**Diff shape / insertion-only — PASS.** `git diff f5d7faf febf34b -- corpus/fixtures/measure_audio.py`
= 466 insertions, 3 deletions, 5 hunks. The **three deletions are exactly** the guard line, the `mode =`
line and the `suffix =` line — the same replaced triple r72 used (`r72-reviewer.md:17-19`); every other
hunk is additive. Flag count 116 → **117**; the new flag is in the usage list; mutual exclusion works:
`--probe-consumers-r73 --probe-sndfile-transport-r72` → **exit 2**, `error: choose one probe mode`.
New code: constants `:995-1003`, `_consumer_tail :1006`, `_pwcat_fields :1020`, `pwcat_leg :1030`,
`mpv_leg :1083`, `consumer_transport_entry :1151`, `consumer_ops_entry :1203`, dispatch `:1811-1815`,
flag `:1577`, `mode` `:2241`, `suffix` `:2261`. **No new imports** (no import-time dependency added — the
r72 D1 class is not repeated); `build_artifacts.py` has **0** consumer tokens (no member build, no
forwarding line).

**Independent 36-cell agreement — PASS.** `compare_r73_receipt.py` against the committed receipt
(`…T150022971775Z`): **cells compared=36 agree=36 diff=0** on the two shared transports (file, fifo_path)
for both consumers. Fork set = **2**, both predicted by my pre-landing work: the mpv fork is the one my
2-transport matrix showed directly, and the pw-cat `.snd` fork is the one my named/unnamed controls
predicted — the arm's two extra anonymous transports (stdin_pipe, redirected_fd) are what make it visible
inside the receipt. The arm's 4-transport structure is *better* than the frontier's 2-transport test:

```
consumer_dec_hcom_r73_probe   mpv    -> {file, redirected_fd}=[2,hcom,Operation not permitted]
                                       {stdin_pipe, fifo_path}=[0,hcom,None]
consumer_extsuffix_snd_r73_probe pw-cat -> {file, fifo_path}=[0,None]
                                       {stdin_pipe, redirected_fd}=[1,'Format not recognised.']
```

The mpv grouping separates the **seekable** pair from the **non-seekable** pair regardless of namedness
(`redirected_fd` is anonymous-but-seekable and fails like `file`) — that is a strictly stronger statement
than the frontier's, and it independently reproduces the scout's stdin-pair experiment. The pw-cat grouping
is the **name** pair (named arms accept via the libsndfile fallback, anonymous arms reject) and reproduces
my controls exactly. The receipt also carries the arm's own control, `pwcat_name_axis`
(`:1403-1407`): same no-magic bytes through fifos named `axis.snd`/`axis.wav`/`axis.bin` → **rc 0/1/1** —
identical to my independent controls (`pwcat-snd-controls.json`), so the name-vs-transport separation is
inside the receipt and does not depend on a reader trusting the critic.

**Ops entry — PASS (all five cells reproduce my own measurements).** `consumer_pwcat_ops_r73_probe`:
daemon gate `PIPEWIRE_RUNTIME_DIR=<empty>` → rc=1, `wall_s` 0.002, `pw_context_connect() failed: Host is
down` (my 0.0 s / same string); `fifo_no_writer` blocked with `wchan=wait_for_partner`, SIGKILL exit −9 (my
8 s SIGKILL-only bound); `fifo_empty_writer` rc=1 `Format not recognised.`; `pacing_instant` 4.031 s for a
4.0 s/384044 B member (`playback_paced: true`; my 3.99–4.35 s on tone4s); `pacing_trickle` 6.004 s with a
6.0 s delivery window, rc=0 (`starved_ok: true`; my 8.51 s on a 8.2 s window).

**Daemon-down error path — PASS (tested end-to-end).** Whole arm re-run with `PIPEWIRE_RUNTIME_DIR=<empty>`
(`…T150305963053Z`): every pw-cat leg records rc=1 with `pw_error` = the connect failure (distinguishable
from a format reject by reason, not rc — D6 satisfied in practice); the mpv legs are **unaffected** and the
`dec_hcom` fork is still detected; the ops entry records **five failures** instead of silently passing.
The `.snd` pw-cat fork correctly collapses to a single group under the gate.

**Receipt hygiene — PASS.** 0 absolute `/home` or `/tmp` paths, 0 `[ 0.00x]` timestamps, 0 ASLR `0x…` tags,
0 temp-dir names in the committed receipt (`compare_r73_receipt.py` hygiene scan). The new
`_consumer_tail`/`_pwcat_fields` normalizers do the work the r71 `_tail` could not (D-class from C5).

**Prior rows — 7/8 byte-identical pre→post; the 8th is revision-independent noise (see D10).**
`replay-pre.json` (HEAD `f5d7faf`) vs `replay-post.json` (committed revision): `normal 8e8cdad6…`,
`ffprobe-transport-r71 578cad95…`, `sndfile-transport-r72 f7faaedb…`, `transport-txw-piperefuse-r68
762aff12…`, `transport-extsuffix-snd-r69 80f6d64b…`, `transport-dec-act-r67 195d7554…`,
`ui-preempt-gsrt-r65 099c76de…` — all unchanged. `fifo-hold-ladder-r70` moved (`4b12add6…` →
`a1db85ff…`) but a **third run on the same committed revision returned `4b12add6…`** (identical to the
pre-landing value), so the movement is run-to-run variance at that row's transition band, not an
insertion effect.

**Receipt determinism — FAIL (one measured leaf).** The two committed-revision runs are **not
byte-identical**: `pacing_trickle.wall_s` 6.004 vs 6.003 (one line; the intermediate revision showed the
same on `pacing_instant.wall_s`, 4.033 vs 4.032). Everything else — all 36 cells, both fork groups, the
ops gate/writer/pacing verdicts — is byte-identical. See D9.

## 2. Findings by severity

### D1 — high (claim): "consumer verdicts partition by mandatory-seek vs stream-consume polarity — opposite of the decoder axis" is falsified as stated

- On the canonical 9, **one member** forks on stream seekability (mpv × dec_hcom); pw-cat shows **zero**
  seekability forks; 8 of 9 members are transport-invariant under both consumers (§1).
- The decoder-axis comparison I ran from committed receipts (`decoder_axis_rows.py` →
  `decoder-axis-rows.txt`): sox r67 `dec_hcom` is transport-invariant (all four transports, native route,
  exit 0, 9 samples); ffmpeg r71 `dec_hcom` all four arms exit 0; sndfile r72 `dec_hcom` all four arms 278
  frames. So on this corpus the *decoder* axis does not fork for the member the *consumer* axis forks on.
  The polarity *contrast* is real but pairwise, not a partition: the decoder-side fork in the opposite
  direction is sox × `txw_piperefuse` (file/redirected_fd accept 64 samples, stdin_pipe/fifo_path reject
  `input must be a file, not a pipe`) — seekable/named **helps** there, whereas mpv × `dec_hcom` seekable
  **hurts**. Two single members, opposite directions; neither is a class law. The landed receipt confirms
  the consumer side independently (2 forks, §1b), as does the critic's F1 (`r73-critic.md:63-86`) and the
  scout's headline.
- Correct statement (smallest safe restatement, agreeing with the critic's §6.1): *consumer verdicts fork
  per member, not per class: (a) mpv × seek-gated lavf demuxers (`dec_hcom`): seekable → lavf-synthesized
  refresh-seek EPERM → rc=2, non-seekable → skip the refresh → rc=0 (name-independent, opposite in
  direction to sox's txw pipe-refusal); (b) pw-cat × the named-fork member (`.snd`): the verdict is
  filename-extension-driven on every transport — the r69/r72 name axis, not a consumer axis. All other
  members are transport-invariant under both consumers.*
- Impact if landed as stated: a false class-level generalization in `knowledge/`, `LOG.md`, `SCORECARD.md`
  and the wave ledger, plus a `transport_fork` boolean that would be wrong for 8 of 9 pw-cat members.
  (The landed adjudication restates it correctly — `r73-adjudicator.md:14-31` — so the exposure is the
  fixture comment, D12.)

### D2 — high (axis/independence): pw-cat rows are naming-contingent, and pw-cat adds no detection verdict

- The `.snd` row flips on the fifo's **name** alone (§1 controls). The fixture's own fifo convention names
  the fifo with the member basename (`measure_audio.py:611`, `:878`), so a landed arm following it records
  pw-cat extsuffix_snd **rc=0 on both transports** (no fork), while a frontier-style `fifo1` name records
  rc=0/rc=1. Both are "correct" measurements of different objects: the receipt must therefore record the
  fifo name (or run the named/unnamed control) or its pw-cat verdicts are not interpretable.
- pw-cat's verdicts are libsndfile's verdicts (§1 string equality) — the consumer arm must not be counted
  as a fourth detection authority alongside sox/ffmpeg/sndfile; it is the r72 decoder + a realtime drain.
- Also worth stating in-receipt: `.snd` acceptance is a *fallback* (RAW|U-Law 500 frames, r72), reached only
  when content sniff fails; content beats name (valid WAV bytes named `.txw` play, rc=0).
- **Landed arm status: fixed.** `consumer_ops_entry` now carries the `pwcat_name_axis` control
  (`measure_audio.py:1403-1407`) — `axis.snd` rc=0 vs `axis.wav`/`axis.bin` rc=1 on identical fifo-fed
  bytes — so the receipt separates name from transport internally. Residual: the *member* cells still
  inherit the fixture's basename-fifo naming, so a reader comparing the `fifo_path` cell against a
  differently-named fifo would see a different verdict; the control cell is what makes this readable.

### D3 — medium (frontier basis): `ports/frontier/fb-pipewire.md` claims are falsified or over-scoped

- `fb-pipewire.md:27` "Format selection is pure content sniff — a fifo named `fifo1` plays a WAV fine, and
  `extsuffix_nomatch.txw` … **No suffix/name axis**" is **falsified** for the fallback path: same bytes,
  `.snd`/`.au` rc=0 vs no-suffix rc=1, on both transports (§1). The frontier never ran the canonical
  `.snd` member through pw-cat (its table `:47` lists only `extsuffix_nomatch.wav/.txw`).
- `fb-pipewire.md:50` "pw-cat verdicts are **transport-invariant** on every member tried" survives only in
  the scoped sense "…on the members tried"; as a class rule it is false (D2) and it is also *naming*-scoped.
- The frontier's one genuinely new fork (mpv × dec_hcom) reproduces exactly, including rc vocabulary
  (0 played / 2 failure) and the fifo arm's `Stream is not seekable.` → success path.

### D4 — medium-low (brief/receipt hygiene): the brief's frontier path does not exist

Brief (both author and reviewer seats) cites `reports/frontier/fb-pipewire.md`; that path is absent —
`reports/frontier/` contains only `fa-sndfile.md`; the artifact is **`ports/frontier/fb-pipewire.md`**
(verified `ls` 11:35, read in full). Same defect the critic recorded (`r73-critic.md:28-30`). Any r73
report/receipt that inherits the brief's path will point at a non-existent file.

### D5 — low (mechanism attribution): "mandatory-seek" describes the consumer, not the format

The frontier's inference ("lavf hcom demuxer likely declines the seek; not straced", `:74`) is now measured
(§1): the refusal is **lavf-synthesized** (0 failing syscalls), the hcom demuxer has `seeks:0` and consumes
the whole input at open, and **ffmpeg decodes the same file arm with rc=0** despite `could not seek`. So the
correct attribution is *mpv's post-open refresh-seek is fatal when the demuxer cannot honour it*, not "the
format requires seekability" — the distinction matters because it predicts which future members fork
(seek-gated demuxers + a seekable stream), and it warns against pooling content-gate failures such as
`lengate_hcom_132` (critic F3) under a "seek" column.

### D6 — low (verdict granularity): rc alone pools distinct classes (measured, both consumers)

- mpv rc=2 covers: refresh-seek EPERM (dec_hcom file), unrecognized format (7 members), and load failure on
  a missing path (`loading failed`) — measured in my (buggy, retained) first matrix run.
- pw-cat rc=1 covers: `Format not recognised.`, `File contains data in an unimplemented format.`,
  `System error : No such file or directory.` (missing path), and the daemon-down `pw_context_connect()
  failed: Host is down` (rc=1, no `sndfile:` prefix at all). A `blocked:`/reason-normalized field is
  required for the arm to be replay-comparable — agrees with the simplifier's C6 ruling.

### D7 — low (cross-seat wording): pw-cat fifo exit is writer-close driven

Measured hold-scaling (1.21/3.21/6.31 s for holds 1/3/6 s) contradicts the boundary report's phrasing
"writer semantics: exit at data-chunk end (linger irrelevant)" (`reports/round-73/r73-boundary.md:1`). The
fixture's 1.0 s hold is therefore *load-bearing for wall-time* (fifo arms land ≈1.3 s), though not for any
verdict. Flagged for the scribe; no artifact depends on the wording today.

### D8 — low (self-disclosure): three harness artifacts in my own runs, corrected

Recorded because all three are live traps for the landed arm:
1. Writer fd held open by the *parent* → reader never sees EOF → false "hang" (25 s SIGKILL).
2. Writer stdout not redirected to the fifo → no bytes ever delivered → false "hang".
3. Member paths missing the `corpus/` prefix → all 36 cells read ENOENT; pw-cat's reason then is
   `System error : No such file or directory.` (rc=1), which is exactly why D6 matters.
All corrected; the matrix in §1 is the corrected data. My invalid runs are kept (`my-matrix.json`,
`replay-pacing.json`) so the correction is auditable rather than invisible.

### D9 — low (determinism): the r73 receipt is not byte-reproducible — one measured `wall_s` leaf drifts

Two runs of the **committed** revision differ by exactly one line: `pacing_trickle.wall_s` 6.004 vs 6.003
(`…T150022971775Z` vs `…T150103164753Z`); the intermediate revision drifted on `pacing_instant.wall_s`
(4.033 vs 4.032). 2 of 2 run pairs drifted, each by ≤1 ms in a `wall_s` leaf that is a wall-clock
measurement of realtime playback. Every verdict cell, both fork groups and the ops gate/writer assertions
are byte-identical, and the semantic pins (`playback_paced`, `starved_ok`, `exit_code`) are stable. Impact:
the wave's "byte-stable ×2" convention (r67→r72 receipts were byte-identical) is **not** met by this row,
and a downstream ledger that hashes the receipt will see churn. The adjudicator/scribe record this
honestly as "1 ms leaf drift" (`r73-adjudicator.md:46-48`, `r73-scribe.md`), so the risk is textual
discipline rather than a hidden claim — but "byte-stable" should not be asserted for r73. Cheapest fix:
round `wall_s` to 1 decimal, or keep `playback_paced`/`starved_ok` and drop the raw wall leaves.

### D10 — low (prior-row stability, pre-existing): `fifo-hold-ladder-r70` is not byte-stable at its band edge

Pre `4b12add6…` → post `a1db85ff…` → **third run on the same revision `4b12add6…`**. The varying field is
the ladder's own transition-band classification for the **chunked** feed at `hold=0.0`
(`hold_transition_band_s.chunked.{max_divergent,min_stable}_hold_s`: `None/0.0` vs `0.0/0.05`, i.e. 1 of 10
reps flipping between `blocked` and `exit 2`). This is the r70 round's own conclusion ("transition band,
not a point bound") showing up as receipt churn under load. It is **not** caused by the r73 insertion
(same revision produced both values; the insertion touches only new functions + the dispatch/mode/suffix
triple). Recorded so the wave ledger does not read the pre/post delta as an insertion defect.

### D11 — low (robustness): a reachable-but-sink-less daemon stalls the pw-cat arm at 15 s per leg

The ops gate tests **connect**, not playback viability: with a daemon reachable and zero sinks, pw-cat
hangs in an unlinked stream (the boundary seat measured the hang; the frontier's `--target 0` trap is the
same class, and my `--target 0` bound also hit SIGKILL at 8 s). The arm's per-leg bound is 15 s
(`CONSUMER_R73_TIMEOUT_S`), so on such a host the pw-cat half would spend ≈9 min (9 members × 4 legs) in
`blocked: no verdict within 15 s` before finishing, and every blocked leg would be recorded honestly but
slowly. Not a correctness defect — a runtime-cost note for a future sink-less dispatch (the frontier
listed the same gap as unresolved, `fb-pipewire.md:75`).

### D12 — low (claim text): the in-fixture claim sentence still states the falsified class law

`measure_audio.py:993-994` (the arm's own comment block, block starts `:981`) states the claim "consumer
verdicts partition by mandatory-seek vs stream-consume polarity — opposite of the decoder axis" as *under
test*, while the arm's own receipt falsifies it corpus-wide (2 member-local forks with different drivers)
and the adjudicator/LOG restate it correctly (`r73-adjudicator.md:14-31`, `LOG.md` round-73 entry).
Precedent in this lane is that the fixture comment is where the round's claim text lives
(`r72-reviewer.md:24-26`), so the sentence is the one artifact still carrying the falsified form.
Recommend the member-local restatement (D1) in the comment at the next touch — no behavior change implied,
and nothing depends on it today. The mechanism paragraph above it (`:984-992`) is accurate.

## 3. Contracts and error paths I verified as sound (independent)

- **Daemon-required gate precedes input open**: rc=1 in 0.0 s with `Host is down` on the file arm *and* on
  a writer-less fifo (which otherwise blocks forever) → the arm cannot hang on a daemon-less host; the
  blockage is a recorded verdict, not a stall.
- **No-writer fifo is SIGTERM-immune**: bounded kill must be SIGKILL (Python `subprocess.run(timeout=…)`
  already uses SIGKILL; a shell `timeout` without `-s KILL` would leak).
- **Empty writer → rc=1 `Format not recognised.`**; **writer holds fd → reader waits for close** (D7);
  **writer closes → rc=0 after playback-paced drain**.
- **mpv exits at writer EOF on a fifo** (no hang in any of my fifo cells; 1.3–1.5 s wall at hold 1.0 s).
- **Receipt-path hygiene** (measured, `text_stability.py` → `text-stability.json`): the fixture's r71
  `_tail` normalizer (`measure_audio.py:647-653` at HEAD) strips ffmpeg `@ 0x…` tags and sox backtick paths
  but does **not** normalize pw-cat's quoted absolute path or mpv's `[ 0.00x]` timestamps (the simplifier's
  C5 measured the same). Two-run diff of the raw texts on `dec_hcom`: pw-cat stderr **byte-identical**
  (accept path, no path in output); mpv logs **164/248 diff lines** (file arm), every one a timestamp
  prefix, plus the log-file path in mpv's own argv echo. So the mpv leg must strip `[ T]` + paths to be
  replay-stable; the pw-cat leg must strip its `"<path>"` when the fifo lives in a temp dir (my matrix
  reasons are `<input>`-normalized for exactly this reason).
- **Mutual exclusion / dispatch / prior rows — exercised on the landed arm** (§1b): mutual exclusion exit 2
  with the new flag in the usage list; the 3-deletion diff shape is exactly guard+mode+suffix; the 8-mode
  baseline replay is 7/8 byte-identical with the 8th explained as revision-independent (D10). Baseline
  values: `normal 8e8cdad6…`, `ffprobe-transport-r71 578cad95…`, `sndfile-transport-r72 f7faaedb…`,
  `transport-txw-piperefuse-r68 762aff12…`, `transport-extsuffix-snd-r69 80f6d64b…`,
  `transport-dec-act-r67 195d7554…`, `ui-preempt-gsrt-r65 099c76de…`, `fifo-hold-ladder-r70 4b12add6…`
  (pre and third run). The first six equal the r72 reviewer's recorded values (`r72-reviewer.md:196-200`),
  so the baseline is cross-seat corroborated; `ui-preempt-gsrt-r65` remains the known ASLR-tag-sensitive row.

## 4. Prior-evidence corrections (independent)

- `fb-pipewire.md:27` name-axis claim — falsified (D3); `:50` transport-invariance — over-scoped (D2/D3);
  `:74` un-straced mechanism — now measured (D5); `:68` "no linger protocol needed" — true for verdicts,
  false for wall-time (D7).
- Brief frontier path — wrong directory (D4).
- Boundary report wording on pw-cat exit semantics — conflicts with the measured hold scaling (D7).

## 5. Residual risk

1. **Single host / single build.** pw-cat's verdict strings, the `.snd`/`.au` fallback set and the hcom
   demuxer's non-seekability are properties of libpipewire 1.6.8 + libsndfile 1.2.2 + libavformat
   63.1.101 on Arch. The receipt pins the PipeWire side indirectly (`daemon_live.server_name` =
   "PulseAudio (on PipeWire 1.6.8)") but **not** the mpv/libavformat/libavutil versions that drive the mpv
   fork or the libsndfile version that drives the pw-cat strings — the r72 arm pinned `sf_version_string()`
   and r71 pinned ffprobe's version, so this row is a step *back* on provenance (low, textual).
2. **One member, one mechanism.** The mpv fork is 1/9 canonical (plus `lengate_hcom_132` is a content-gate
   failure per the critic, not a seek fork). A class claim from one member is not supportable; the
   restatement in D1 is the honest ceiling for this corpus.
3. **Naming is load-bearing.** Any consumer arm that changes fifo naming (temp dir name, suffix
   stripping) changes the pw-cat `.snd` row. The receipt must record the fifo name or run the control.
4. **The tree moved three times inside the window** (`f5d7faf` → `1d0b2d34…` → `834823ea…` → commit
   `febf34b`); my landing numbers are pinned to `834823ea…` == `git show HEAD:…` at commit time. Any later
   edit to `measure_audio.py` invalidates the receipt hashes here and needs a fresh replay.
5. **Receipt byte-stability is not guaranteed** (D9) and the r70 ladder row is band-edge noisy (D10), so a
   wave-level "byte-stable" claim must be scoped: verdict cells stable, `wall_s` leaves and the ladder band
   classification are not.
6. **`wall_s`-only drift could hide a real regression** in a hash-compare ledger: the gate that matters is
   the verdict-signature comparison (`compare_r73_receipt.py`, 36/36), not a whole-file hash.

## 6. Verification gaps (explicit)

- **No `lsp` device** — checked, not assumed: this seat's toolset exposes no `lsp` tool; `mcp_list_servers`
  → `["rea"]` only (Ghidra binary-RE toolset: `annotate_native_function`, procedure dossiers — no
  status/references/definition/diagnostics for a Python source file); `which pyright pylsp
  jedi-language-server lsp basedpyright` → all absent; `import pygls` → ImportError. Caller/definition
  checks were therefore done by **literal text search + execution**, explicitly **not** semantic proof.
- **`resume_continuity_v1` is not applicable to this lane**: `grep -rn "resume_continuity\|preflight"` hits
  only prose inside baseline snapshot trees (`corpus/live/r64-baseline/tree/…`, `r65-baseline/frozen/…`);
  there is no resume/preflight path in the fixture, so there is no failed-preflight/mutation contract to
  verify here. Recorded as absence-of-surface, not as a pass.
- **Not exercised**: the intermediate `1d0b2d34…` revision's receipts (superseded); the sink-less daemon
  case end-to-end (D11 is predicted from the boundary/frontier hang measurements plus my `--target 0`
  bound, not re-run); `pw-record`/MIDI/multiple-writers/writer-dies-mid-stream; the 4 non-canonical lengate
  members (critic's additions, not contract); a HEAD-revision-only run of the r70 ladder (relocating the
  fixture breaks its `ROOT`, and a copy under `corpus/fixtures/` would be outside my write scope — D10
  therefore rests on the same-revision run triple, which is sufficient to show revision-independence).
- I did not adjudicate; this is a recommendation, never an admission. No git mutation performed by this
  seat (the fixture edits and the `febf34b` commit are the author's/operator's; `LOG.md`/`SCORECARD.md`
  and the r72-baseline replica were modified by sibling seats, not by me).

## 7. Commands / exits (as run)

```sh
cd ~/Projects/shokunin/audio-shokunin
# device + surface checks
mcp_list_servers                                   # ["rea"] only — no lsp device
which pyright pylsp jedi-language-server lsp basedpyright   # all absent
grep -rn "resume_continuity\|preflight" .          # prose-only hits in baseline trees
grep -c probe-consumers-r73 corpus/fixtures/measure_audio.py   # 0 (11:35→11:47, 6 polls)
sha256sum corpus/fixtures/measure_audio.py         # b765ee76… == HEAD f5d7faf (unchanged all window)

# independent consumer matrix (36 canonical cells), plain fifo name then fixture basename
python3 corpus/live/r73-reviewer/consumer_matrix.py                       # exit 0 → my-matrix.json
R73_FIFO_NAMING=fixture R73_MATRIX_OUT=my-matrix-fixture-naming.json \
  python3 corpus/live/r73-reviewer/consumer_matrix.py                     # exit 0
python3 corpus/live/r73-reviewer/pwcat_snd_controls.py                    # exit 0 → pwcat-snd-controls.json
python3 corpus/live/r73-reviewer/decoder_axis_rows.py                     # exit 0 → decoder-axis-rows.txt
python3 corpus/live/r73-reviewer/replay_pacing2.py                        # exit 0 → replay-pacing2.json
python3 corpus/live/r73-reviewer/replay_pwcat_mpv.py pwcat-bounds         # exit 0 → replay-pwcat-bounds.json
python3 corpus/live/r73-reviewer/pwcat_probes.py                          # exit 0 → pwcat-probes.json
python3 corpus/live/r73-reviewer/pwcat_linger_proof.py                    # exit 0 → pwcat-linger-proof.json
python3 corpus/live/r73-reviewer/mpv_seekability_causal.py                # exit 0 → mpv-seekability-causal.json
strace -f -e trace=lseek,read,openat -o strace-mpv-file4.log \
  timeout -s KILL 15 mpv --no-config --vo=null --ao=null --audio-display=no \
  --really-quiet --log-file=strace4.mpv.log corpus/live/round-66/pair_dec_hcom.wav   # mpv rc=2, 0 failing syscalls
ffmpeg -v debug -ss 0.005 -i corpus/live/round-66/pair_dec_hcom.wav -f null -        # rc=0, "could not seek to position 0.005"
# pre-landing byte baseline (8 modes; fixture sha256 identical before/after)
python3 corpus/live/r73-reviewer/replay_modes.py pre                      # exit 0 → replay-pre.json

# ---- landing review (committed febf34b, fixture 834823ea…) ----
git log --oneline -3                                 # febf34b r73: CONSUMER class expansion …
git diff f5d7faf febf34b -- corpus/fixtures/measure_audio.py > corpus/live/r73-reviewer/r73-fixture-latest.diff
                                                     # 466+/3-, 5 hunks; deletions = guard/mode/suffix only
grep -c add_argument corpus/fixtures/measure_audio.py                     # 117 (was 116)
python3 corpus/fixtures/measure_audio.py --probe-consumers-r73 \
  --probe-sndfile-transport-r72                      # exit 2, "choose one probe mode"
python3 corpus/fixtures/measure_audio.py --probe-consumers-r73 > r73-arm-final-run1.stdout  # exit 1 (2 forks)
python3 corpus/fixtures/measure_audio.py --probe-consumers-r73 > r73-arm-final-run2.stdout  # exit 1
#   receipts corpus/live/runs/…T150022971775Z-consumers-r73/ and …T150103164753Z-consumers-r73/
#   NOT byte-identical: pacing_trickle.wall_s 6.004 vs 6.003 (one line)
python3 corpus/live/r73-reviewer/compare_r73_receipt.py \
  corpus/live/runs/20261014T150022971775Z-consumers-r73/measurements.json   # cells=36 agree=36 diff=0
PIPEWIRE_RUNTIME_DIR=$PWD/corpus/live/r73-reviewer/emptyrt-arm \
  python3 corpus/fixtures/measure_audio.py --probe-consumers-r73           # exit 1; ops records 5 failures,
                                                     # pw-cat legs rc=1 "Host is down", mpv fork still found
# prior-row gate, post-landing (fixture 834823ea…)
python3 corpus/live/r73-reviewer/replay_modes.py post                     # exit 0 → replay-post.json
#   7/8 modes byte-identical to pre; fifo-hold-ladder-r70 differed
python3 corpus/fixtures/measure_audio.py --probe-fifo-hold-ladder-r70     # third run == pre hash 4b12add6… (D10)
```

Receipts cited: `my-matrix-fixture-naming.json`, `my-matrix.json`, `matrix-{out,fixture-naming-out}.txt`,
`pwcat-snd-controls.json`, `pwcat-probes.json`, `pwcat-linger-proof.json`, `replay-pacing2.json`,
`replay-pwcat-bounds.json`, `replay-pre.json`, `mpv-seekability-causal.json`, `decoder-axis-rows.txt`,
`strace-mpv-file4.log`, `strace-mpv-fifo.log`, `matrix-mpv-*.log` — all under `corpus/live/r73-reviewer/`.
