# R70 scout — `fifo_writer_hold_s` bound map (pre-author)

Scope: map only. Fresh probes in `corpus/live/r70-scout/` (`hold_probe.py`,
`strace-tt.txt`). Host: `sox` = SoX_ng v14.8.0.1 (`/usr/bin/sox`), bridge child
`/usr/bin/ffmpeg`, Linux 7.2.3-arch1-3, python 3.14.7.

## 1. Where the hold lives / how the writer attaches

`corpus/fixtures/measure_audio.py` — line refs are against git HEAD
(`aeab82c`, the r69-landed state I read at map time ~09:05). The author's
in-flight r70 diff landed during this map (`git diff` +245/−18 at 09:17,
inserting `TRANSPORT_R70_HOLDS`, `fifo_feed()`, `fifo_writer_hold_s()` env
override at ~:195 and ~:281) — symbols below are stable anchors, numbers
shift +9/+43 at those hunks:

- `TRANSPORT_R67_FIFO_WRITER_HOLD_S = 1.0` — line 197 (point constant).
- `transport_matrix()` lines 276–295: `tempfile` dir → `os.mkfifo(fifo)` where
  `fifo = Path(tmp)/path.name` (member basename kept) → daemon thread `feed()`
  does `fifo.open("wb")` (blocking, unblocks on reader open #1) → one-shot
  `fh.write(path.read_bytes())` + `flush()` → `time.sleep(HOLD)` inside the
  `with` block (line 285) → close. `writer.join(timeout=HOLD+5)` at line 295.
- `transport_leg()` lines 235–263: `subprocess.run(sox -V6 <fifo> -n stat,
  timeout=TRANSPORT_R67_ARM_TIMEOUT_S=10)`; `TimeoutExpired` → `exit_code=None`,
  `error="blocked: no verdict within 10 s"` (line 247 — **overwrites** any FAIL
  already on stderr).
- Receipt fields (lines 316–326): `transport_axis.<arm>.{input,
  sox_detected_format, sox_route, exit_code, samples_read, error, stderr_tail
  (input-name + ASLR scrubbed), named, seekable}`; `transport_protocol.
  {arm_timeout_s, fifo_writer_hold_s, fifo_feed}` (lines 318–320,
  `fifo_feed` currently `"one-shot write then writer lingers"`);
  `transport_verdict_groups`, `transport_fork`, `failures`. A `hold_ladder`
  group belongs next to `transport_protocol`/`transport_verdict_groups` here.

## 2. The open-#2 mechanism — corrected timing picture (fresh strace)

`corpus/live/r70-scout/strace-tt.txt` (`strace -tt -f sox -V4 <fifo> -n stat`,
held writer, dec_act 600 B):

| t (ms after sox execve) | event |
|---|---|
| +0.0 | `execve("/usr/bin/sox", …)` |
| +21.3 | **open #1**: `openat(fifo, O_RDONLY) = 3`; `lseek`→ESPIPE; `read(3)=600` (whole file in the 4096-B prefetch; AUTO_DETECT window 257 B) |
| +21.4 | stderr `detected file format type 'act'` |
| +21.5 | `pipe2([4,5])` + `clone` → bridge child |
| +21.8 | parent close(5), writes **`sox FAIL … can't find Sun/NeXT/DEC identifier`** — *before* ffmpeg execs, with **no `read(4)` at all** |
| +22.3 | `lseek(3,-343)`→ESPIPE (rewind of the 343-B post-detection overread fails); parent `exit_group(2)` |
| +22.4 | child `execve("ffmpeg -loglevel quiet -nostdin -strict -2 -i <fifo> -f au -")` via 12-entry PATH probe → `/usr/bin/ffmpeg` |
| +130.5 | **open #2**: `openat(fifo, O_RDONLY) = 3` inside ffmpeg (~109 ms of dyn-lib loading after execve; strace-inflated) |
| +1027 | ffmpeg `exit 183` — blocked reading the fifo until the writer's 1.0 s hold ended (pure EOF; reader #1 drained all 600 B) |

Corroborating r67 trace `corpus/live/r67-boundary/runs/strace-fifo-heldwriter-tt.txt`:
open #1 at +5.1 ms, open #2 at +30.0 ms, ffmpeg exit 183 at +1.007 s.

**Facts (measured):**
- The verdict does **not** depend on open #2: sox emits `exit 2 /
  can't find Sun/NeXT/DEC identifier` and exits ~22 ms in, unconditionally —
  the FAIL is emitted without ever reading the bridge pipe. The "au-magic"
  text is the `-f au` bridge contract surfaced as the input-open failure.
- The bridge is a real child: `ffmpeg -i <fifo> -f au -`. What the hold buys is
  **child liveness**, not the verdict: attached-at-open-#2 → open succeeds →
  ffmpeg reads (residual tail/EOF) → exits when the writer closes → the harness
  sees stderr-pipe EOF and `communicate()`/`run()` returns. Dead-at-open-#2 →
  ffmpeg blocks in `openat` **forever** → `communicate()` never sees EOF
  (ffmpeg inherited the stderr capture pipe) → 10 s arm timeout →
  `blocked: no verdict within 10 s` + an **orphaned ffmpeg** (pgrep showed 24
  blocked bridge children left by r67 scratch).
- Both r67 observations are the same dead-writer cell viewed through different
  harnesses: shell `sox <fifo>` returns exit 2 at ~22 ms regardless of the
  grandchild ("5/5 exit 2 au-magic"); python capture waits on the orphan
  ("blocked >10 s").

**Bound estimate (this host):** writer at h=0 detaches ≈ open#1+ε (~5–25 ms);
open #2 lands ~30 ms (r67 strace) to ~130 ms (today's strace; strace -tt -f
inflates; true warm-cache value plausibly ~30–50 ms — leg elapsed at h=0.05
was ~54 ms, meaning ffmpeg finished before ~54 ms). So **h\* ≈ O(10–50 ms)** —
above 0, below the 0.05 ladder step. r67-boundary's "~0.5–1.0 s" residual-margin
claim is **not** supported by its own `-tt` trace (+30 ms); treat 1.0 s as a
margin-of-safety pin, not a near-bound constant. Fresh sanity reps today on
`dec_act`: h=0 → 5/5 × 8 s killpg timeout (dead-writer cell, FAIL text already
on stderr); h=0.05 → 5/5 exit 2 au-magic in ~54 ms.

## 3. Which members exercise the fifo path

`transport_entry` runs all four arms on all 17 members
(`TRANSPORT_R67_MEMBERS` ×10 :179, `TRANSPORT_R68_MEMBERS` ×2 :204,
`TRANSPORT_R69_MEMBERS` ×5 :216; dispatch loops :643–709). But open #2 exists
**only on the ffmpeg route** (`sox_route=="ffmpeg"` when detected `act`,
measure_audio.py:252): exactly **`preempt_act` and `dec_act`** — the brief's
choice is right, and `preempt_act` is the natural sibling. Every other member
is `native`/`none` → single-open → hold-invariant (the blocking `fifo.open
("wb")` already covers reader #1). `preempt_both` detects `gsrt`, not act →
native despite its name. Receipt evidence: `corpus/live/runs/*-transport-
{dec-act,preempt-act}-r67/measurements.json` (`fifo_path`: exit 2 /
`can't find Sun/NeXT/DEC identifier`, proto block verbatim).

## 4. Chunked feed — changes attach semantics AND the visible stream

Current feed = one write, then linger. A chunked `fifo_feed` variant:

- Attach duration becomes the feed duration (implicit hold): a chunked writer
  that finishes before open #2 still lands the dead-writer cell. r67-boundary
  `fifo_race.py`/`runs/race.tsv` shows exactly this: `dec_act:cut128:gap0.8`
  → 8 s TIMEOUT (writer detached pre-open-#2); `cut≥257:gap0.8` → exit 2
  au-magic (writer still mid-feed when the bridge opened).
- Byte-window at open #2 shifts: reader #1 stops reading at detection (~21 ms,
  ≤ its prefetch); all chunks written after that accumulate for ffmpeg — a
  racing reader#1/ffmpeg byte-split if the feed outlasts detection, so the
  ffmpeg-visible suffix varies per rep. For dec_act the suffix is unprobeable
  PCM-tail → au-magic probably still lands (boundary E5: dribble →
  `Sun identifier` 0.61 s), but a feed that delays its *first* chunk past
  detection would hand ffmpeg the file head → real probe → possibly a
  different verdict class. That is a third cell, not just liveness.
- `writer.join(timeout=HOLD+5)` at :295 bounds cleanup; a chunked feed needs
  the same cap on its feed duration.
- `O_RDWR` holder alternative already implemented and measured in r67-scribe
  scratch (`corpus/live/r67-scribe/run_transport_ext.py:145-182`,
  `run_fifo_hold`): `os.open(fifo, O_RDWR)` before spawn → writer always
  attached (open #2 can never block — an O_RDWR fd counts as a writer);
  FIONREAD-drain + 0.4 s grace close → deterministic EOF, **no timing
  constant**. Verdicts identical to the pinned-linger cell on all act members;
  legs resolved in ~0.45 s. This is the brief's "h\*=0 with a correctly
  blocking writer" branch — prior art exists, unmerged.

## Verdict-cell signature for the ladder receipt

| writer at open #2 | harness observation | `fifo_path` leg record |
|---|---|---|
| attached | ffmpeg opens→reads→exits at writer close | `exit_code=2`, `error="can't find Sun/NeXT/DEC identifier"`, elapsed ≈ h+ε |
| gone | ffmpeg blocks in `openat` forever | `exit_code=None`, `error="blocked: no verdict within 10 s"` + orphaned grandchild |

## Confidence / unknowns

- High: file:line map, two-cell mechanism, member routing, O_RDWR prior art —
  all strace/receipt-backed.
- Medium: precise h\* (~10–50 ms estimate; strace inflation makes open #2
  timing upper-bounded — author's ladder settles it). Whether the h=0 cell is
  *ever* a python-harness win on a cold cache is open (my 5/5 = hang).
- Gap: why the FAIL emits without a `read(4)` (au-magic string appears
  pre-computed at bridge setup — worth a comment-level note, verdict-irrelevant).
- Guard for author: bare-hold reps leave blocked ffmpeg orphans; the r67 seats
  already carry 24 of them under `/tmp` scratch paths — `killpg`/`start_new_
  session` in any new ladder harness, or they accumulate.
