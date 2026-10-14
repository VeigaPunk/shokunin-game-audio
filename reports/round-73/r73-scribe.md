# R73 scribe — CONSUMER CLASS (pw-cat + mpv): the `--probe-consumers-r73` arm **landed in the working tree mid-scribe-session (uncommitted, still evolving at snapshot)** — 5 receipts; runs 1–4 audited (runs 1–2 byte-identical, runs 3–4 one ≤1 ms `wall_s` leaf apart, verdict/partition/fork fields identical); fixture revised again at 14:54:23Z (blob `7b89bff4…`→`2334abd8…`) and run 5 adds `consumer_pwcat_ops_r73_probe/pwcat_name_axis`; landed forks are per-member (`pw-cat`×`extsuffix_snd` name axis; `mpv`×`dec_hcom` seekable bit), matching the sibling pre-landing falsification of the class-polarity claim as stated; frontier `fb-pipewire` (committed `c079aba`) audited 16 claims (detection/verdict/fork log-backed; wall-times + most rc values report-text-only); conflicts F1–F9 reported verbatim

Seat: **scribe** (leaf, report-only). Host: `plazir27`; system clock
**2026-10-14 14:36 UTC** at open, **14:55Z** at last check (wave label
`shokunin-train-20261101-w12`; the wave-name date and the clock date differ —
recorded, not a defect claim).
Toolchain re-read this session: `pw-cat` libpipewire **1.6.8** (`pw-play`
resolves to `/usr/bin/pw-cat`), `mpv` **v0.41.0** (libavformat **63.1.101**,
FFmpeg n9.0.1), `pactl` protocol 35, pipewire daemon live (pids 1905 /
pipewire-pulse 2290 / wireplumber 1906). Repo
`/home/vgpnk/Projects/shokunin/audio-shokunin`, HEAD **`50f55eb`** at session
start — **moved to `f5d7faf` at 14:38:20Z mid-session by an r72 reviewer-fold
commit (lazy libsndfile load; not an r73 landing)**, which changed the
tracked fixture blob (see landing-state below). The r73 author arm was
**absent for the first 15 minutes of this session and landed (working tree,
uncommitted) at ~14:50:23Z** — the report carries both states, timestamped.
Scratch `corpus/live/r73-scribe/`; this file is the only report path written.
No tracked file modified by this seat, no git mutation, no consumer re-run
(all numbers below re-read from existing artifacts/receipts).

Axis-move (verbatim, from the brief): *"CONSUMER CLASS expansion: pw-cat
(PipeWire realtime) + mpv (lavf) on the member corpus … MOVE (coverage):
`--probe-consumers-r73` — pw-cat playback arm (fifo realtime: playback-paced
consumption, writer-attach semantics, daemon-required gate) + mpv arm
(content sniff via libavformat; INVERTED seekability fork: non-seekable helps
— file->refresh-seek-EPERM->rc2, fifo->decodes). Claim: consumer verdicts
partition by mandatory-seek vs stream-consume polarity — opposite of the
decoder axis. Viability-conditional: pw-cat needs the pipewire daemon (live
on this host; record the exact blockage if down)."*

## Author-landing state — unlanded through 14:49Z; **arm landed (working tree) at ~14:50:23Z**

Checked this session (checks at 14:35:46Z, 14:36:10Z, 14:36:29Z, 14:36:50Z,
14:38:24Z, 14:40:48Z, 14:43:48Z, 14:44:24Z, 14:46:44Z, 14:49:30Z, 14:51:58Z,
14:55:20Z):

- **Pre-landing (through 14:49:30Z):**
  `grep -c 'probe-consumers-r73' corpus/fixtures/measure_audio.py` → **0**;
  newest flag `--probe-sndfile-transport-r72`; fixture blob `df1e5bec…`
  (== HEAD `50f55eb`) → `b068dbb5…` (== HEAD `f5d7faf` after the 14:38:20Z
  r72 reviewer-fold); `ls corpus/live/runs | grep -c r73` → **0**;
  `reports/round-73/` had only sibling reports; `corpus/live/r73-author/`
  absent through 14:38:55Z, scratch present from 14:39:07Z (mid-measurement:
  mpv hcom/act pipe/rfd/fifo legs, `fifoA`/`fifoP`/`fifoS.snd`, `emptyrt/`).
- **Landed at ~14:50:23Z (working tree, uncommitted; still evolving):**
  `git status` → ` M corpus/fixtures/measure_audio.py` (+425/−3, then
  +466/−3 after the 14:54:23Z revision);
  `grep -c 'probe-consumers-r73'` → **2** (`:1536` flag, `:1758` branch,
  `:2241` mode, `:2261` suffix); **5 receipts** in `corpus/live/runs/` as of
  14:55:20Z: `20261014T145109998458Z`, `20261014T145113997684Z`
  (byte-identical, sha256 `3c3b19a0…`), `20261014T145204328075Z`
  (`3a0218b3…`, one leaf `pacing_instant/wall_s` 4.033→4.032),
  `20261014T145319250378Z` (`e7f0d609…`, one leaf `pacing_trickle/wall_s`
  6.003→6.004), `20261014T145502288182Z` (`245dfa1a…`, newer fixture
  revision — see the landed-arm audit below). `reports/round-73/r73-author.md`
  had **not** landed at the last check (14:55Z).
- `git status --porcelain` shows **no modification to any tracked file by
  this seat** (the ` M` entries are the author's fixture edit and pre-existing
  scratch copies under `corpus/live/r72-baseline/`, `corpus/live/r72-verifier/`).
- Independent sibling check (pre-landing): `corpus/live/r73-boundary/snapshot.txt`
  records the same unlanded state verbatim — *"author-landing r73 refs: 0"*,
  HEAD `50f55eb`, fixture blob `df1e5bec…` (14:35:29Z).

**Round-73 in-flight landings (uncommitted):** `reports/round-73/r73-simplifier.md`
14:40:15Z (report-only; *"Deletions made in the shared tree: none"*; C1–C7
pre-landing rulings — `pactl`/pw-cat daemon-gate disagreement, `--target 0`
hang rc=137 @6 s, SIGTERM-immune open-block, `--ao=pipewire` daemon coupling,
`_tail` extension needs, rc-granularity); `r73-scout.md` 14:42:12Z,
`r73-boundary.md` 14:42:28Z, `r73-critic.md` 14:42:20Z (revised 14:46:36Z),
`r73-reviewer.md` 14:48:02Z — headlines + spot-checks in the sibling section;
`r73-baseline/` scratch active; no `r73-verifier.md` yet.

**Consequence:** the r73 harness insertion was *absent, not failed* through
14:49:30Z; it landed at ~14:50:23Z and produced three receipts. The sections
below carry both the frontier basis (with the 16-claim provenance audit) and
the landed-arm audit; nothing is upgraded past the artifacts.

## Landed r73 arm — scribe audit (working tree, uncommitted; not replayed)

Read-only audit of the landed diff and its receipts at 14:51–14:53Z. This
seat did not run the fixture; the author report (`r73-author.md`) and the
verifier replay are still pending at snapshot.

**Diff** (`git diff corpus/fixtures/measure_audio.py`): +425/−3. The three
deletions are the one-line probe-flag sum / mode / suffix chains, each
replaced by an extended version that appends `probe_consumers_r73` — prior
flags preserved. Additions: `_pwcat_fields` (:1020), `pwcat_leg` (:1030),
`mpv_leg` (:1083), the consumer transport/ops entry builders, a
`CONSUMER_R73_MEMBERS` dict, `--probe-consumers-r73` (:1536), the mode branch
(:1758, including the ops entry + per-member entries), mode `:2241`, suffix
`:2261`. Receipt family: `consumer_pwcat_ops_r73_probe` +
`consumer_<member>_r73_probe` ×9.

**Receipts (4 runs):**

| run | sha256 (measurements.json) | note |
|---|---|---|
| `20261014T145109998458Z-consumers-r73` | `3c3b19a0f9d1a09acdd1541d46acda0b…` | run 1 |
| `20261014T145113997684Z-consumers-r73` | `3c3b19a0…` | **byte-identical to run 1** |
| `20261014T145204328075Z-consumers-r73` | `3a0218b3fc524464…` | differs from run 1 in exactly **1 leaf**: `consumer_pwcat_ops_r73_probe/pacing_instant/wall_s` 4.033 → 4.032 |
| `20261014T145319250378Z-consumers-r73` | `e7f0d6091df23960…` | differs from run 1 in exactly **1 leaf**: `consumer_pwcat_ops_r73_probe/pacing_trickle/wall_s` 6.003 → 6.004 |
| `20261014T145502288182Z-consumers-r73` | `245dfa1a41131a55…` | **newer fixture revision** (blob `2334abd8…`): adds `consumer_pwcat_ops_r73_probe/pwcat_name_axis` (+605 B); pacing_instant leaf 4.033→4.032 |

Runs 1–4 are identical in every verdict / partition / fork field; their only
run-to-run diffs are ≤1 ms wall-clock leaves in the ops entry. Run 5 belongs
to the next fixture revision (still uncommitted; the author was iterating at
snapshot) and was **not** diff-audited beyond the new key above.

**Measured verdicts in the landed receipt (runs 1–4 identical on these
fields):** each entry carries a 4-transport axis
{file, stdin_pipe, redirected_fd, fifo_path} per consumer, a
`transport_verdict_groups` partition and a `transport_fork` boolean.

- **pw-cat forks on exactly one member: `extsuffix_snd`**
  (`transport_fork: true`; groups {file, fifo_path} → `[0, null]` vs
  {stdin_pipe, redirected_fd} → `[1, "Format not recognised."]`) — the
  filename axis, and the fixture's fifo input keeps the `.snd` extension
  (`"input": "extsuffix_nomatch.snd"`), so the cell is captured in-receipt.
- **mpv forks on exactly one member: `dec_hcom`** (`transport_fork: true`;
  seekable arms `file` + `redirected_fd` → rc=2 with
  `refresh_seek: true`, `seek_failed: "Operation not permitted"`,
  `mpv_verdict: "no audio or video data played (reason 4)"`; non-seekable
  `stdin_pipe` + `fifo_path` → rc=0, `stream_not_seekable: true`).
- All other 7 members (dec_act, posttable_nomatch, txw_piperefuse,
  extsuffix_{wav,bin,txw,f32}): **no fork under either consumer**.
- **Ops entry** (`consumer_pwcat_ops_r73_probe`): daemon live via `pactl`
  (rc=0, "PulseAudio (on PipeWire 1.6.8)", default sink SPDIF); daemon gate
  rc=1 in **0.002 s** ("Host is down"); no-writer fifo blocked, wchan
  `wait_for_partner`, waited 3.0 s, rc=−9; empty writer rc=1
  ("Format not recognised."); pacing instant 384,044 B / 4.0 s content →
  wall **4.033 s**, `playback_paced: true`; pacing trickle 8 chunks × 0.75 s →
  wall **6.003 s**, `starved_ok: true`; `failures: []`.

**Insertion-only spot-check (byte-identity across the ~14:50:23Z edit
boundary) — 5 modes:** `normal` post-edit 14:52:12 (`8e8cdad6…`) == pre-edit
14:32:50 (`8e8cdad6…`); `transport-extsuffix-snd-r69` post-edit 14:50:44
(`80f6d64b…`) == pre-edit 14:43:19 (`80f6d64b…`); `sndfile-transport-r72`
post-edit 14:53:29 (`f7faaedb…`) == pre-edit 14:50:15 (`f7faaedb…`);
`ui-preempt-gsrt-r65` post-edit 14:52:49 (`099c76de…`) == pre-edit 14:43:22
(`099c76de…`); `ffprobe-transport-r71` post-edit 14:53:49 (`578cad95…`) ==
committed r72-era `20261014T141033155858Z-ffprobe-transport-r71`
(`578cad95…`). Full-ledger prior-row byte-stability remains the verifier's
check; these are five-mode spot checks only.

**Claim vs landed data:** the landed receipt shows **per-member forks only**
(2 fork members out of 9, one per consumer), matching the four sibling
pre-landing measurements; the briefed *class* partition ("consumer verdicts
partition by mandatory-seek vs stream-consume polarity") is not what the
receipt encodes — the fixture's own comment states the claim is measured
per member per consumer. Canonical judge adjudicates.

## Sibling seat reports landed mid-session (uncommitted at snapshot; reported, not adjudicated)

Five seat reports landed in `reports/round-73/` while this seat was writing
(all untracked; no r73 commit exists). Their headline measurements, verbatim
where quoted; **this scribe did not independently replay them** — artifact
existence/hashes spot-checked only (marked ✓ below). Hashes are as of
14:49:36Z; `r73-critic.md` and `r73-simplifier.md` were revised after the
first read (quoted lines re-verified present in the current revisions). The
canonical judge owns any verdict.

- **`r73-scout.md`** (14:42:12Z, sha256 `72ea19e5…`) — *"Headline — claim is
  PARTIAL"*: mpv fork *"Reproduced exactly … with the mechanism pinned and
  quantified"*; *"mpv partitions on exactly one of 11 members (the hcom
  polyglot), and the partition key is the seekable bit, proven by a
  same-transport pair (`-` with pipe stdin → rc0, `-` with regular-file stdin
  → rc2)"*; pw-cat's only partition on the canonical corpus is the
  name/extension axis for `extsuffix_snd` (file `.snd` → rc0; fifo named
  `.fifo` → rc1; fifo named `.snd` → rc0; stdin `-` → rc1) — *"the same
  polarity as the decoder axis"*; *"The 'opposite polarity' holds only across
  different members"*; EPERM string is `av_strerror(-1)` rendering, no seek
  syscall issued. Artifacts: `corpus/live/r73-scout/runs/{mpv,pwcat}-matrix-run{1,2}.json`,
  `scout-summary.json`, `logs/mpv/dec_hcom__{file,fifo_path,stdin_pipe,stdin_file}.log` ✓
  (paths exist; matrix runs verdict-identical 44/44 per report).
- **`r73-boundary.md`** (14:42:28Z, sha256 `d7b9e7de…`) — 10 members ×
  {pw-cat, mpv} × {file, fifo} = 40 cells, **verdicts byte-identical across
  two runs** (`corpus/live/r73-boundary/runs/20261014T1437{03,17}…-consumers-r73/verdicts.json`
  both sha256 `9f8bc309…` ✓). Headline: *"the mpv inverted-seek fork is
  CONFIRMED for `dec_hcom` only … and is FALSIFIED as a corpus-wide 'consumer
  partition'; pw-cat is transport-invariant"* (10/10; acceptance set
  {dec_act, dec_hcom, extsuffix_snd}); edge probes: daemon gate rc=1 in
  3–4 ms **before** input open, attached writer stays blocked in `open()`
  (orphan hazard) (`edge_results_probe-a.json` ✓); **zero-sink private daemon
  → HANG** rc=-9 at 8.00 s, same as live `--target 0` (`probe-b.json` ✓ —
  closes the frontier's last viability gap: "daemon live" insufficient, a
  linkable sink is required, failure mode = hang); pw-cat exits at
  **data-chunk end** (linger irrelevant; writer lingers 2 s → still 0.41 s
  exit); partial/SIGKILL writers rc=0; SIGTERM-immune open-block needs
  process-group SIGKILL; **EPERM is library-synthetic** — strace shows 0
  failing syscalls, all `lseek` ≥0 (`probe-h.json` ✓); `--force-seekable` has
  no effect either direction; multiple writers stable; pacing 4.38 s instant /
  8.56 s trickle.
- **`r73-critic.md`** (14:46:36Z revision, sha256 `03b1a66e…`; first read 14:42:20Z `813bc507…`) — 13 members × 2
  consumers × 2 transports = 52 legs (`corpus/live/r73-critic/matrix.tsv`
  sha256 `f2fdc112…` ✓, `controls.tsv` `c7658054…` ✓; spot-check of rows
  agrees with boundary/scout, incl. `extsuffix_snd` pw-cat file rc=0 / fifo
  rc=1 on an unnamed fifo). Headline: *"proposed claim falsified pre-landing;
  the r73 author diff was ABSENT for the whole critic window; pw-cat forks on
  FILENAME (`.snd`), not on seekability; only mpv×dec_hcom forks on
  seekability (1/13 members)"*. Its smallest safe correction (verbatim):
  *"Consumer verdicts fork per member, not per class: (a) mpv × seek-gated
  lavf demuxers (dec_hcom): seekable→refresh-seek-EPERM→rc2,
  non-seekable→decode rc0 …; (b) pw-cat × the named-fork member (.snd):
  verdict is filename-extension-driven on both transports … All other 11
  members: transport-invariant under both consumers."* Receipt hygiene:
  `timeout -s KILL` everywhere, ≥6 s no-writer legs, never `--target 0`,
  record the daemon-gate receipt as the viability-conditional leg.
- **`r73-simplifier.md`** (14:47:15Z revision, sha256 `cd2a90d4…`; first read 14:40:15Z `47003e99…`) — *"Deletions made
  in the shared tree: none"*; C1–C7 pre-landing weight rulings (reuse the
  canonical-9 member authority / one timeout + writer protocol / pw-cat's own
  connect attempt as the only honest daemon gate — `pactl` and pw-cat were
  measured to disagree under the same env; do not couple mpv to the daemon
  (`--ao=pipewire` flips a cell when the daemon is down, `--ao=null` does
  not); `_tail` needs extension for pw-cat paths + mpv timestamps; keep
  verdict granularity above raw rc); r72 entries re-proved byte-stable 9/9
  ×3 across the mid-session fold.
- **`r73-reviewer.md`** (14:48:02Z, sha256 `2e8c117b…`, landed after the first sibling batch) —
  *"36-cell canonical matrix independently reproduced; proposed claim
  FALSIFIED as stated (1 member forks, not a class polarity); the pw-cat
  `.snd` fork is a NAME fork invisible under the fixture's own fifo naming;
  mpv's EPERM is lavf-synthetic (strace: 0 failing syscalls); r73 author arm
  ABSENT for the whole window (pre-landing byte baseline captured)"*; it also
  captured a pre-landing byte baseline (`replay-pre.json`, 8 modes) and a
  ready 36-cell comparator for the insertion-only gate once the arm lands.
  Artifacts: `corpus/live/r73-reviewer/{my-matrix.json,
  my-matrix-fixture-naming.json, pwcat-snd-controls.json, replay-pre.json,
  strace-mpv-file4.log, …}` ✓ (paths present).

Sibling scratch trees present at snapshot (untracked, in flight, **not
evidence**; used as cross-check only, never promoted): `r73-boundary/`
(`probe_consumers_r73.py`, 2× byte-identical verdict receipts, 12 edge-probe
receipts, strace log), `r73-critic/` (52-leg `matrix.tsv` + `controls.tsv` +
controls), `r73-scout/` (mpv/pwcat matrix runs, 4-transport calibration logs,
own `tone4s.wav`), `r73-reviewer/` (`replay_pwcat_mpv.py`,
`replay-pwcat-{file,fifo}.json`, `replay_pacing.py`), `r73-author/scratch/`
(mid-measurement), `r73-baseline/` (appeared 14:44Z), `r73-scribe/` (this
seat).

## Measured evidence used (sources + provenance audit)

1. **Frontier pre-measurement (tracked/committed)** —
   `ports/frontier/fb-pipewire.md` (sha256 `07492765…`, committed `c079aba`),
   report for wave-10 task `audio-frontier-b.txt`. Note the brief cites
   `reports/frontier/fb-pipewire.md`; that path does **not** exist
   (`reports/frontier/` holds only `fa-sndfile.md`) — see F1.
2. **Frontier corpus (tracked, 25 files)** —
   `corpus/live/frontier-pipewire/`: 6 mpv logs (file/fifo ×
   hcom/txw/extsuffix), 13 pw-cat logs, 1 rc file, `tone4s.wav` (64,078 B,
   sha256 `e77666ba…`), 3 named fifos (`fifo1..3`) + `emptyrt/` dir.
   All hashed this session with `find -type f` (**not** a glob — see
   appendix incident).
3. **Members exercised** (sha256 this session): `round-66/pair_dec_hcom.wav`
   `325fb967…`; `round-66/pair_dec_act.wav` `777b6764…`;
   `round-66/pair_lengate_gsrt_25.wav` `ede4161b…`;
   `round-68/txw_piperefuse.wav` `fd7911a3…`;
   `round-69/extsuffix_nomatch.wav` == `extsuffix_nomatch.txw`
   `f073e70a…` (byte-identical pair, r69 design).
4. **Scribe artifact audit** —
   `corpus/live/r73-scribe/frontier-claims-audit.tsv`: 16 frontier claims
   checked against named artifacts → **10 log-backed, 1 partial (artifact
   exists, timing not receipt-backed), 4 report-text-only, 1 in-flight
   sibling scratch**. Log-backed claims are listed in the claim audit below.
5. **Independent in-flight cross-checks (uncommitted, cited as scratch only)**
   — r73-critic's pw-cat file-arm stderr reproduces the frontier error text
   byte-for-byte; r73-reviewer's `replay-pwcat-{file,fifo}.json` reproduces
   the frontier rc pattern (file: hcom/act rc=0, lengate rc=1; fifo:
   hcom/act rc=0, txw rc=1); r73-scout's mpv logs reproduce the seek fork and
   extend it to 4 transports (file + stdin-file → refresh-seek refusal;
   fifo + stdin-pipe → "Stream is not seekable" → plays); r73-boundary's 40-cell
   matrix and r73-critic's 52-leg matrix both reproduce the frontier verdicts
   and add the `.snd` filename fork cell. Full headlines in the sibling
   section above; artifact existence/hashes spot-checked, none replayed.

## Claim audit (each clause, against the sources above)

- **pw-cat daemon-required gate — CONFIRMED (log-backed).**
  `pwcat-nodaemon.log`: `error: pw_context_connect() failed: Host is down`;
  reached before any input open (`pw-cat -p fifo3` under an empty runtime
  also rc=1 instantly). Daemon is live on this host at snapshot: pids 1905 /
  2290 / 1906, `pactl info` → `Server Name: PulseAudio (on PipeWire 1.6.8)`,
  protocol 35. Sinks at snapshot: 3 `SUSPENDED` + 1 `IDLE` (USB SPDIF) — see
  F4 for the frontier's "all SUSPENDED" wording.
- **pw-cat playback-paced consumption + writer-attach semantics —
  CONFIRMED for the phase structure (log-backed), PARTIAL for timings.**
  Empty writer close → `sndfile: ... Format not recognised.` rc=1
  (`pwcat-fifo-empty.log`); full member → sniff + play, rc=0 at writer EOF
  (`pwcat-fifo-w1.rc` = `pwcat-rc:0`); no-writer blocks with zero output
  (`pwcat-fifo-nowriter.log`, 0 B). The wall-clock numbers (instant dump ≈4 s,
  trickle ≈9 s, raw ≈5 s) and the SIGTERM-immunity/wchan claims are
  **report-text-only** (see F2).
- **pw-cat verdict transport-invariance — CONFIRMED (log-backed).**
  Same sndfile predicate file vs fifo on every member tried:
  `txw_piperefuse` rc=1 "unimplemented format" (both arms);
  `extsuffix_nomatch.{wav,txw}` rc=1 "Format not recognised" (both arms, and
  the two member files are byte-identical); hcom/act play on both arms.
- **mpv content sniff via libavformat — CONFIRMED (log-backed).**
  `mpv-{file,fifo}-pair_dec_hcom.wav.log:162/168`: `Found 'hcom' at
  score=100 size=600` on both transports; `.wav` extension did not rescue
  no-magic bytes nor prevent hcom detection (txw/extsuffix logs).
- **mpv INVERTED seekability fork — CONFIRMED on the hcom member
  (log-backed).** File arm: `refresh seek to 0.000000` →
  `Seek failed (Operation not permitted)` → `finished playback, no audio or
  video data played (reason 4)` (log lines 178–181, 203). Fifo arm:
  `Stream is not seekable.` → no refresh seek → `● Audio --aid=1 (hcom 1ch
  22050 Hz)` → `finished playback, success (reason 0)` (lines 171, 180,
  tail). Member-qualified: txw/extsuffix never reach the demuxer (probe
  failure on both arms) — see F5.
- **Partition claim ("mandatory-seek vs stream-consume polarity, opposite of
  the decoder axis") — frontier basis supports a one-member fork; sibling
  pre-landing measurement (uncommitted) falsifies the claim *as stated* and
  proposes a member-level restatement; the landed receipt (working tree,
  uncommitted) encodes per-member forks only.** Frontier basis: detection is
  transport-invariant for both consumers; the only frontier-measured consumer
  verdict fork keys on the seekable bit (mpv hcom), inverted relative to the
  decoder axis; pw-cat showed no fork on the frontier's members. Sibling
  convergence (scout 1/11 members; boundary 1/10; critic 1/13; reviewer 1/36
  canonical cells) and the landed arm agree: exactly two fork members —
  mpv×`dec_hcom` (seekable bit) and pw-cat×`extsuffix_snd` (filename axis,
  same polarity as the decoder axis). Critic's proposed restatement quoted
  verbatim above; the canonical judge adjudicates.

## Conflicts / findings reported verbatim for the canonical judge

- **F1 — brief path vs actual artifact.** Brief: *"Frontier evidence:
  reports/frontier/fb-pipewire.md + corpus/live/frontier-pipewire/."* Actual:
  the report is at **`ports/frontier/fb-pipewire.md`** (tracked, committed
  `c079aba`); `reports/frontier/` contains only `fa-sndfile.md`. The corpus
  path in the brief is correct.
- **F2 — provenance gap: wall-times and most rc values are report-text
  only.** The frontier report states pw-cat wall clocks (≈4 s / ≈9 s / ≈5 s),
  SIGTERM-immunity >30 s, `--target 0` rc=124, and per-leg rc values; the
  only persisted rc artifact in `frontier-pipewire/` is `pwcat-fifo-w1.rc`.
  The corresponding logs are 0 bytes (instant/nowriter/raw/slow/w1) and carry
  no timing. mpv rc values (0/2) are likewise not persisted as rc files
  (log text is consistent: `finished playback, success` vs `Errors when
  loading file`). No verdict impact on the detection/fork claims, which are
  log-backed; the numbers must not be cited as receipts.
- **F3 — host/date labels.** `fb-pipewire.md:4` header: *"Host: `plazir27`,
  measured 2026-11-01"*; this session: hostname `plazir27`, system clock
  `2026-10-14`. The wave label carries `20261101`; recorded as a label/clock
  mismatch, not a defect claim.
- **F4 — daemon sink-state drift.** `fb-pipewire.md:10`: *"4 real ALSA sinks
  + 2 sources, all SUSPENDED"*. Scribe snapshot (`pactl list sinks short`):
  4 sinks, **3 SUSPENDED + 1 IDLE** (`alsa_output.usb-…SPDIF… IDLE`).
  Dynamic daemon state; no verdict impact (both snapshots agree the daemon
  and sinks exist).
- **F5 — the fork is member-qualified.** The brief's *"INVERTED seekability
  fork"* is measured on the hcom polyglot only; `txw_piperefuse` and
  `extsuffix_nomatch` fail at probe on **both** arms (`Failed to recognize
  file format`) — no seekability exposure. Any generalization to "mpv
  verdicts fork by seekability" must be read as "for members that reach the
  demuxer".
- **F6 — host-process hygiene (no verdict impact).** The frontier's cited
  stale `timeout … strace sox` pids (1965371, 1970028) are **gone** at
  snapshot (`ps -p` → none). r72's ~20 leaked ffmpeg readers are down to 1
  live `ffmpeg`/`sox` pair, both in-flight from the concurrent r70 ladder
  probe (sibling seat), not this seat's.
- **F7 — sibling in-flight generalization (NOT evidence).**
  `corpus/live/r73-scout/logs/cal-{file,stdinfile,fifo,stdinpipe}-dec_hcom.log`
  extend the mpv fork across the transport axis: seekable inputs
  (file, stdin-from-regular-file) → refresh-seek EPERM → reason 4;
  non-seekable (fifo, stdin-pipe) → plays. Uncommitted sibling scratch at
  snapshot; reported as cross-check only, not promoted to evidence.
- **F8 — frontier "no suffix/name axis" overreaches as a class rule
  (reported by r73-scout/-boundary/-critic, uncommitted).** `fb-pipewire.md:27`
  says *"Format selection is pure content sniff … **No suffix/name axis.**"* —
  true for the frontier's tested members, but all three sibling seats
  measured a pw-cat filename fork on `extsuffix_snd` (named `.snd` → rc=0
  libsndfile U-Law fallback; unnamed fifo / `-` → rc=1). The frontier's member
  set never exercised that cell. Frontier's narrower content-precedence
  statement (name neither rescues nor blocks *content* detection) still holds
  (boundary probe g). Canonical judge adjudicates scope.
- **F9 — "Seek failed (Operation not permitted)" is library-synthetic, not a
  real EPERM (reported by r73-scout/-boundary, uncommitted).** Boundary's
  strace of the mpv file arm on `dec_hcom`: **0** EPERM syscall lines, all
  `lseek` ≥0; scout reads the string as `av_strerror(-1)` / "no seek path"
  sentinel. Frontier's own caveat (*"mechanism inferred from log order … not
  straced"*) is therefore narrowed, not contradicted — no failing seek reaches
  the kernel. No verdict impact on the fork (rc 2 vs 0 unchanged).

## Gates

| gate | state at snapshot (last check 14:55:20Z) |
|---|---|
| author landing (`--probe-consumers-r73` + receipts) | **LANDED in working tree (uncommitted) at ~14:50:23Z, still evolving** — 5 receipts; fixture revised again 14:54:23Z (`7b89bff4…`→`2334abd8…`); `r73-author.md` still absent |
| insertion-only / prior rows byte-stable | **spot-checked ×5** (normal, transport-extsuffix-snd-r69, sndfile-transport-r72, ui-preempt-gsrt-r65, ffprobe-transport-r71 byte-identical pre/post edit); full-ledger check pending verifier |
| tracked fixture state | HEAD still `f5d7faf`; working tree fixture modified by the r73 landing (`b068dbb5…` → `7b89bff4…` → `2334abd8…` at 14:54:23Z); no r73 commit |
| sibling seat landings | scout / boundary / critic / simplifier / reviewer reports landed 14:40–14:48Z (untracked); boundary verdicts byte-stable ×2; r73-baseline scratch active; no `r73-verifier.md` yet |
| verifier replay on committed tree | not run (no r73 commit exists; verifier dispatched) |
| adjudicator / report-last | not run (no r73 report-last commit) |
| provenance (scribe audit) | 16 frontier claims → 10 log-backed, 1 partial, 4 text-only, 1 in-flight; sibling artifact existence/hashes spot-checked; landed diff + 5 receipts audited (runs 1–4 diffed; not replayed) |

## Knowledge note draft (mechanism, not narrative)

Full draft: `corpus/live/r73-scribe/knowledge-draft-r73-consumer-class.md`
(intended destination if landed: `corpus/knowledge/2026-10-14-consumer-class-pwcat-mpv.md`).
Condensed:

- **pw-cat**: daemon reachability is a pre-input gate (`pw_context_connect`,
  rc=1 "Host is down", no fifo block); decode layer = libsndfile; over a fifo,
  open blocks for a writer, consumption is playback-paced, exit at
  data-chunk end; single open (no re-open-by-name bridge); verdicts
  transport-invariant on the frontier members, **but a filename fork exists
  on `.snd`** (libsndfile post-sniff extension fallback — sibling-measured,
  uncommitted); `--target 0` / zero-sink daemon hangs forever — linked
  playback + `timeout -s KILL` (+ process-group kill) are mandatory harness
  shapes.
- **mpv**: lavf content probe is transport-invariant; the hcom demuxer issues
  a post-detection `refresh seek` that on a seekable input fails inside
  libavformat (`av_strerror(-1)` → "Operation not permitted"; no failing
  syscall) → zero data played (rc=2), while a non-seekable input skips the
  reposition and decodes forward (rc=0). Fork locus = the demuxer's
  reposition request, not the probe, and it is **member-local** (hcom only).
- **Partition (frontier basis; sibling- and landing-corrected)**: detection
  (both consumers) is transport-invariant; the consumer verdict fork is
  per-member, not per-class — mpv×`dec_hcom` on the seekable bit (inverted vs
  the decoder axis), pw-cat×`extsuffix_snd` on the filename axis (same
  polarity as the decoder axis). The briefed "class partition, opposite
  polarity" is falsified as stated by four sibling seats (uncommitted) and is
  not encoded by the landed receipt (3 runs, working tree).
- **Limits**: one forking member per consumer; wall-time/rc provenance gap
  (F2); EPERM library-synthetic, library-internal context not identified;
  zero-sink hang measured only on a private scratch daemon; single
  host/toolchain (plazir27, libpipewire 1.6.8, mpv 0.41.0/lavf 63.1.101).

## LOG draft (append at report-last; arm landed working-tree, uncommitted)

```
## Round 73 — consumer class: pw-cat (PipeWire) + mpv (lavf) on the member corpus (wave-12)

- MOVE: `--probe-consumers-r73` (landed in working tree ~14:50Z, uncommitted at
  scribe snapshot; 4 receipts — runs 1–2 byte-identical, runs 3–4 differ from
  run 1 in one ≤1 ms `wall_s` leaf each). Basis: frontier pre-measurement
  ports/frontier/fb-pipewire.md
  (c079aba) + tracked corpus corpus/live/frontier-pipewire/ (25 files).
- Measured (landed receipt): 9 canonical members × {pw-cat, mpv} × 4 transports
  {file, stdin_pipe, redirected_fd, fifo_path}; per-consumer
  `transport_verdict_groups` + `transport_fork`. Exactly two fork members:
  pw-cat×`extsuffix_snd` (filename axis; named arms [0,null] vs anonymous
  [1,"Format not recognised."]) and mpv×`dec_hcom` (seekable arms rc=2,
  refresh-seek "Operation not permitted" / no data played; non-seekable arms
  rc=0 decode). All other 7 members transport-invariant under both consumers.
  Ops entry: daemon gate rc=1 @0.002 s; no-writer fifo blocked wchan
  `wait_for_partner` @3.0 s rc=−9; pacing instant 4.033 s playback-paced;
  trickle 6.003 s starved_ok; `failures: []`.
- Claim: consumer verdicts partition by mandatory-seek vs stream-consume
  polarity (opposite of the decoder axis) — falsified as stated pre-landing by
  4 sibling seats (scout/boundary/critic/reviewer) and not encoded by the
  landed receipt (per-member forks only; the `.snd` name fork has the SAME
  polarity as the decoder axis). Restatement proposed by critic (verbatim in
  r73-scribe.md): per-member forks; all other members transport-invariant.
- Scribe audit: 16 frontier claims artifact-checked (10 log-backed, 1 partial,
  4 report-text-only, 1 in-flight sibling); conflicts F1–F9; insertion-only
  spot-checked on 2 modes (byte-identical pre/post edit).
- Bounded: plazir27, libpipewire 1.6.8, mpv 0.41.0 (lavf 63.1.101), ffmpeg
  n9.0.1; daemon live with sinks; single host; verifier replay pending.
```

## SCORECARD draft (arm landed working-tree, uncommitted; verifier pending)

```
## Round 73 verdict — 2026-10-14 (draft at scribe time)

| axis | verdict | evidence |
|---|---|---|
| coverage | **improved locally (measured)** | consumer class added: 9 members × 2 consumers × 4 transports + ops entry in one receipt family (`consumer_*_r73_probe`); 3 runs, 2 byte-identical; sibling matrices agree (scout 44 mpv legs, boundary 10×4 byte-stable ×2, critic 52 legs, reviewer 36 canonical cells) |
| depth | **improved locally (measured)** | forks pinned to exactly 2 members: mpv×`dec_hcom` seekable bit (library-synthetic EPERM; 0 failing syscalls) and pw-cat×`extsuffix_snd` filename axis; pw-cat ops surface measured in-receipt (gate 0.002 s; writer-attach wchan; playback pacing 4.033 s / 6.003 s); briefed class-polarity claim falsified as stated (4 sibling seats + landed data) |
| calibration | unchanged | no thresholds/predicates touched; verdict keys = rc + normalized error/reason class; 1 ms `wall_s` leaf jitter between runs disclosed |

Draft note: no admission yet; author report and verifier replay pending at
scribe snapshot (arm uncommitted).
```

## Touched surfaces

- Wrote **only**: `reports/round-73/r73-scribe.md` (this file) and
  `corpus/live/r73-scribe/{checks.txt, frontier-claims-audit.tsv,
  knowledge-draft-r73-consumer-class.md}`.
- `git status --porcelain` after writing: only untracked `corpus/live/r73-*/`
  scratch dirs and the new `reports/round-73/` — **no tracked file modified,
  no git mutation, no product-code edit**.

## Out-of-scope (explicitly not done)

- Implementing the r73 probe arm or any fixture/harness change (author's
  move; scribe seat forbids product-code edits).
- Re-running consumer measurements (frontier + sibling seats measured; no
  re-run to decorate the report). All consumer runs cited were already on
  disk.
- Verification/adjudication (verifier/critic/boundary/reviewer/judge seats).
- Commit/push/publish (operator-owned).

## Artifact paths + hashes (snapshot)

- This report: `reports/round-73/r73-scribe.md`
- Scratch: `corpus/live/r73-scribe/checks.txt`;
  `frontier-claims-audit.tsv`;
  `knowledge-draft-r73-consumer-class.md`
- Frontier report: `ports/frontier/fb-pipewire.md`
  (`07492765885b84310f991f43abd8f884318b2cf934c84a8b78e23a3eb4d98667`)
- Frontier corpus highlights: `tone4s.wav` (`e77666ba…`);
  `mpv-fifo-pair_dec_hcom.wav.log` (`1a799152…`);
  `mpv-file-pair_dec_hcom.wav.log` (`3fa2a2cb…`);
  `pwcat-nodaemon.log` (`0162cae4…`); `pwcat-fifo-w1.rc` (`51832c9d…`);
  `pwcat-fifo-txw_piperefuse.wav.log` (`0e260d63…`);
  `pwcat-fifo-empty.log` (`e4a414f5…`)
- Members: `round-66/pair_dec_hcom.wav` (`325fb967…`),
  `pair_dec_act.wav` (`777b6764…`), `pair_lengate_gsrt_25.wav`
  (`ede4161b…`), `round-68/txw_piperefuse.wav` (`fd7911a3…`),
  `round-69/extsuffix_nomatch.{wav,txw}` (`f073e70a…`, byte-identical)
- Fixture: `corpus/fixtures/measure_audio.py` — at 14:36 blob `df1e5bec…`
  (== HEAD `50f55eb`), sha256 `2eb70bb1…`; after the 14:38:20Z r72
  reviewer-fold commit, blob `b068dbb5…` (== HEAD `f5d7faf`); after the
  ~14:50:23Z r73 landing (working tree), blob `7b89bff41d48…` (+425/−3,
  uncommitted; `--probe-consumers-r73` present); revised again 14:54:23Z to
  blob `2334abd893a8…` (+466/−3; adds `pwcat_name_axis`).
- Landed r73 receipts: `corpus/live/runs/20261014T145109998458Z-consumers-r73`
  (`3c3b19a0…`), `…145113997684Z` (`3c3b19a0…`, byte-identical),
  `…145204328075Z` (`3a0218b3…`, 1-leaf diff), `…145319250378Z`
  (`e7f0d609…`, 1-leaf diff), `…145502288182Z` (`245dfa1a…`, newer revision)
- Insertion-only spot-check receipts: `…145212136689Z-normal` ==
  `…143250197011Z-normal` (`8e8cdad6…`); `…145044978364Z-transport-extsuffix-snd-r69`
  == `…144319608725Z-transport-extsuffix-snd-r69` (`80f6d64b…`);
  `…145329302231Z-sndfile-transport-r72` == `…145015189920Z` (`f7faaedb…`);
  `…145249971846Z-ui-preempt-gsrt-r65` == `…144322735571Z` (`099c76de…`)
- Sibling reports (untracked at snapshot; spot-checked, not replayed):
  `reports/round-73/r73-scout.md` (`72ea19e5…`),
  `r73-boundary.md` (`d7b9e7de…`), `r73-critic.md` (`03b1a66e…`),
  `r73-reviewer.md` (`2e8c117b…`), `r73-simplifier.md` (`cd2a90d4…`)
- Sibling artifacts spot-checked: boundary
  `corpus/live/r73-boundary/runs/…-consumers-r73/verdicts.json` ×2
  (both `9f8bc309…`); `edge_results_probe-{a,b,h}.json`;
  critic `matrix.tsv` (`f2fdc112…`), `controls.tsv` (`c7658054…`);
  scout `runs/`, `logs/` trees present

## Exact commands / exits (appendix)

```sh
cd ~/Projects/shokunin/audio-shokunin
hostname                                                    # plazir27
date -u                                                     # 2026-10-14 14:36–14:55 UTC (open → last check)
git log --oneline -1                                        # 50f55eb → f5d7faf at 14:38:20Z (r72 reviewer-fold; no r73 commit)
grep -c 'probe-consumers-r73' corpus/fixtures/measure_audio.py   # 0 (both revisions)
git hash-object corpus/fixtures/measure_audio.py            # df1e5bec… (== 50f55eb) → b068dbb5… (== f5d7faf)
ls corpus/live/runs | grep -c r73                           # 0 (all checks)
ls -d reports/round-73 corpus/live/r73-author               # absent
pw-cat --version                                            # libpipewire 1.6.8
readlink -f "$(command -v pw-play)"                         # /usr/bin/pw-cat
mpv --version                                               # v0.41.0, lavf 63.1.101
pgrep -a pipewire; pgrep -a wireplumber                     # 1905 / 2290 / 1906
timeout 5 pactl info | grep 'Server Name'                   # PulseAudio (on PipeWire 1.6.8)
timeout 5 pactl list sinks short                            # 3 SUSPENDED + 1 IDLE
grep -nE "Found 'hcom'|Seek failed|not seekable|finished playback" \
  corpus/live/frontier-pipewire/mpv-{file,fifo}-pair_dec_hcom.wav.log
find corpus/live/frontier-pipewire -maxdepth 1 -type f | … sha256sum   # 24 files hashed
sha256sum corpus/live/frontier-pipewire/*                   # BLOCKED on fifo1..3 (named pipes); killed — use -type f
# sibling spot-checks (existence/hashes only; no replay)
ls -d corpus/live/r73-{author,baseline,boundary,critic,reviewer,scout,scribe}  # author+baseline appeared 14:39/14:44Z
sha256sum corpus/live/r73-boundary/runs/*/verdicts.json     # both 9f8bc309… (byte-identical ×2)
sha256sum corpus/live/r73-critic/matrix.tsv corpus/live/r73-critic/controls.tsv  # f2fdc112… / c7658054…
cat corpus/live/r73-boundary/edge_results_probe-b.json      # zero-sink hang rc=-9 wall 8.001
cat corpus/live/r73-boundary/edge_results_probe-h.json      # eperm_syscall_count: 0
# landed-arm audit (read-only; no replay)
git status --porcelain | grep measure_audio                #  M (author edit; +425/−3)
grep -c 'probe-consumers-r73' corpus/fixtures/measure_audio.py   # 2 (landed ~14:50:23Z)
sha256sum corpus/live/runs/*consumers-r73/measurements.json      # 3c3b19a0… ×2, 3a0218b3…, e7f0d609… (1-leaf wall_s diffs)
python3 -c "…json walk…"                                   # run1-vs-run3: pacing_instant/wall_s 4.033→4.032; run1-vs-run4: pacing_trickle/wall_s 6.003→6.004
sha256sum corpus/live/runs/{145212136689Z,143250197011Z}-normal/measurements.json  # 8e8cdad6… both (insertion-only spot check)
sha256sum corpus/live/runs/{145044978364Z,144319608725Z}-transport-extsuffix-snd-r69/measurements.json  # 80f6d64b… both
sha256sum corpus/live/runs/{145329302231Z,145015189920Z}-sndfile-transport-r72/measurements.json        # f7faaedb… both
sha256sum corpus/live/runs/{145249971846Z,144322735571Z}-ui-preempt-gsrt-r65/measurements.json          # 099c76de… both
sha256sum corpus/live/runs/{145349848113Z,141033155858Z}-ffprobe-transport-r71/measurements.json         # 578cad95… both
git hash-object corpus/fixtures/measure_audio.py            # 7b89bff4… → 2334abd8… (second revision, 14:54:23Z)
```

Exit codes: all inspection commands above exited 0 except the documented
non-zero/blocked cases — the glob `sha256sum` blocked reading named pipes
`fifo1..3` (killed after 10 s background wait; no mutation), and the
`ls`-style absence probes (`reports/round-73`, `corpus/live/r73-author`,
`ps -p 1965371,1970028`) exited non-zero as expected for absent objects.
Two pre-existing receipt dirs cited earlier in this session
(`20261014T143409279922Z-normal`, `20261014T143138574159Z-transport-extsuffix-snd-r69`)
were removed by sibling-seat run pruning before the final audit — the
surviving pre-edit comparators above were used instead.

**Seat stop.** Report complete; no further action taken (leaf, no dispatch,
no commit).
