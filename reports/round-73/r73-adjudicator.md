# R73 adjudicator (Sol) — consumer class: pw-cat + mpv on the transport matrix

Round: 73. Wave: `shokunin-train-20261101-w12`. Work commit `febf34b`.

## Declared move (coverage — first non-decoder runtime class)

`--probe-consumers-r73`: playback consumers pw-cat (PipeWire 1.6.8
realtime, libsndfile decode layer) + mpv 0.41.0 (libavformat 63.1.101)
on the canonical 9-member × 4-transport matrix + a pw-cat operational
entry (daemon gate, writer-attach, playback pacing).

## Claim adjudication

- Briefed claim — "consumer verdicts partition by mandatory-seek vs
  stream-consume polarity, opposite of the decoder axis" — **FALSIFIED
  as a corpus-wide law, CONFIRMED member-locally** (scout + boundary +
  critic + reviewer converged on a 36–52 leg matrix before landing):
  - **mpv × dec_hcom: inverted seekability fork** — {file,
    redirected_fd} rc=2 (lavf refresh-seek → synthetic `Operation not
    permitted`; strace: 0 failing syscalls, the hcom demuxer carries no
    read_seek/read_timestamp) vs {stdin_pipe, fifo} rc=0 + 3520 PCM
    bytes. Member-local (1/9), name-independent, opposite polarity to
    sox × txw. redirected_fd correctly groups with file — lavf sees
    the fd as seekable.
  - **pw-cat × extsuffix_snd: NAME-axis fork** — {file, fifo} rc=0 vs
    {stdin, redirected_fd} rc=1 `Format not recognised.` — the r72
    post-sniff extension fallback inherited through pw-cat's own
    libsndfile decode layer. Same polarity as the decoder axis — NOT a
    consumer polarity. Frontier's "pw-cat is suffix-insensitive" was a
    member-set artifact (.snd never tried).
  - All other 8 members transport-invariant on both consumers.
- **Folded mid-landing (critic's 2×2)**: `pwcat_name_axis` cell in the
  ops entry — identical no-magic bytes through fifos named
  `.snd`/`.wav`/`.bin` → rc {0,1,1}; isolates name from transport
  decisively inside the arm itself.

## Operational surface measured (all pinned in the ops entry)

- Daemon gate fires BEFORE input open: `PIPEWIRE_RUNTIME_DIR=<empty>`
  → rc=1 "pw_context_connect() failed: Host is down" in ~2 ms.
- Writerless fifo open blocks in `wait_for_partner`, SIGTERM-immune →
  SIGKILL-bound recorded (wchan captured).
- Empty writer → rc=1 `Format not recognised.`
- Playback-paced drain: instant dump of 4.0 s member → wall 4.03 s;
  starved 8×0.75 s trickle → wall ~6.0 s rc=0 (blocks to EOF).
- `wall_s` leaves are measured jitter (realtime pacing against wall
  clock) — semantically pinned via playback_paced/starved_ok/fork
  signatures; 1 ms leaf drift across runs recorded honestly.

## Seat accounting

8/9 landed at adjudication: author diff (+466/−3, operator-committed
`febf34b` — author report still pending); scout's 2-matrix survey +
operational pins; critic's 52-leg falsification of the class claim +
2×2 requirement; boundary's zero-sink/EPERM/lavf refinements; scribe's
frontier-claims audit (16 claims, 4 textual-only) + byte-stability
watch (runs 1–2 byte-identical, 3–4 ≤1 ms leaf); reviewer pre-landing
36-cell independent repro + prepared comparator; simplifier's C1–C7
do-not-add rulings (member-authority reuse, single timeout, no second
daemon check); baseline pending. Verifier replays the committed tree.

## Verdict

**ADMIT-with-correction** — consumer class joined: decoder axis
(sox/ffprobe/sndfile) now contrasted with two consumer verdict shapes;
the seekability-vs-name fork pair is member-local and driver-diverse.
Host-pinned: PipeWire 1.6.8 live daemon, mpv 0.41.0/lavf 63.1.101.
