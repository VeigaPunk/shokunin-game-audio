# R68 scribe — post-table fallback independently re-measured: declared seekability fork FALSIFIED (fork is on the NAMED axis — extension dispatch); predicted seekable partition realized instead by the txw member (reader-gated, 178-sample decode vs pipe refusal)

Seat: **scribe** (leaf, report-only). Host: devin — `/usr/bin/sox` = SoX_ng
v14.8.0.1 (USING_FFMPEG build), ffmpeg/ffprobe n9.0.1, python 3.14.7 — the
declared r62–r67 toolchain, re-verified live this session. Canonical repo
`/home/vgpnk/Projects/shokunin/audio-shokunin`; the brief's line-6 worktree
`~/Projects/prymeagnt/audio` resolves `.shokunin/audio` via symlink into it
(r67/r68-baseline note carried). Scratch `corpus/live/r68-scribe/`; this file
is the only report path written.

Axis-move (verbatim, from the brief): *"pin the POST-TABLE FALLBACK path as a
measured axis of the autodetect ledger: r67 proved detection is
transport-invariant over matched members but left unmeasured what happens
when NO CHECK row matches (post-table failure) — on seekable transports SoX
can retry/re-read for fallback classification, on pipes the ≤257 prefetch
bytes are consumed. Declared falsifiable claim: post-table fallback behavior
forks on transport seekability — a no-match member gets a different
verdict/error signature on `file`/`redirected_fd` vs `stdin_pipe`/`fifo_path`.
Additionally land ONE tracked pipe-refusal member (txw or smp detected family
— r66 boundary measured both refuse pipes outright, no tracked member yet).
Land additive members + transport-probe modes on measure_audio.py; all 112
prior ledger rows + receipts byte-stable."*

## Author-landing state at observation (briefed re-run target absent)

The brief asks me to "re-run the author's landed arms". Verified at every
checkpoint this session (final check **2026-10-14 10:11 UTC**):

- HEAD = `a0958a9` ("ignore: broaden tree-pattern to *tree*/ — xsentinel
  w7-F1", a `.gitignore` hygiene commit landing ~09:59 UTC); the last
  *content* commit is `bd5e1fe` (r67 report-last).
- `grep -c 'r68' corpus/fixtures/measure_audio.py` = **0**; `git status
  --porcelain` shows **no `M` on any tracked file**; no
  `corpus/live/r68-author/`, no `reports/round-68/r68-author.md`.
- Sibling r68 seat reports present at write time: `r68-{baseline,boundary,
  critic,reviewer,scout}.md` (all uncommitted `??` entries, same as mine).
- r68-boundary's header records the same absence at ~07:05 -03 and r68-critic
  records it at its review time — the author's additive landing has not
  appeared in any observed window.

**Consequence for this seat:** the author-mode re-run is *absent, not failed*
(boundary's phrasing, verbatim accurate). I therefore re-ran the *landed r67
arm machinery* — `transport_matrix`/`transport_leg` imported verbatim from the
tracked `corpus/fixtures/measure_audio.py` (`a0b2ad6d…`, unchanged all window)
— against my own constructed post-table and pipe-refusal members, plus raw
`sox -V6` legs and strace. That is the strongest independent measurement
available and it is member-level evidence for exactly the partition the
declared claim predicts.

## Independent measurement (own scratch, landed arm machinery)

Runner `corpus/live/r68-scribe/run_posttable.py` (imports the tracked module
by path — no copy, no edit); fixtures `probes/` (7 members, SHAs below);
results `runs/posttable-matrix-run{2,3}.json` + `runs/posttable-run1.txt`
(run-1 stdout; its JSON was overwritten in place by the re-run — stdout and
both later JSONs retained), per-arm verbatim strings quoted below.

### Post-table no-match members — the declared partition is falsified on my own fixtures

| member | file | stdin_pipe | redirected_fd | fifo_path | groups |
|---|---|---|---|---|---|
| `nomatch_zeros.wav` (300 B `\x00`, sha `d13d4a8b…`) | `RIFF header not found`, exit 2 | `can't determine type of  '-'`, exit 2 | `can't determine type of  '-'`, exit 2 | `RIFF header not found`, exit 2 | 2 |
| `nomatch_noise.wav` (300 B `\x5a`, sha `dd128ff0…`) | `RIFF header not found` | `can't determine type of  '-'` | `can't determine type of  '-'` | `RIFF header not found` | 2 |
| `nomatch_zeros.bin` (sha `d13d4a8b…`) | `no handler for file extension 'bin'` | `can't determine type of  '-'` | `can't determine type of  '-'` | `no handler for file extension 'bin'` | 2 |
| `nomatch_zeros` (no ext, sha `d13d4a8b…`) | `can't determine type of file '<member path>'` | `can't determine type of  '-'` | `can't determine type of  '-'` | `can't determine type of file '<tmpdir path>'` | 3 |

Every arm's `sox_detected_format` is `null` (no `detected file format type`
line on any arm — verified: no CHECK row fires on these bytes) and
`sox_route` is `"none"`. The **measured partition is `{file, fifo_path}` vs
`{stdin_pipe, redirected_fd}` — the NAMED axis, exactly transposed from the
declared `{file, redirected_fd}` vs `{stdin_pipe, fifo_path}` seekable
partition.**

- `redirected_fd` — seekable (strace `lseek(0,0,SEEK_CUR)=0`) — takes the
  *pipe* verdict verbatim.
- `fifo_path` — non-seekable (strace `lseek(3,0,SEEK_CUR)=-1 ESPIPE`) — takes
  the *file* verdict verbatim: the `.wav` extension dispatches the wav
  reader, which is served the buffered prefetch and reports
  `RIFF header not found` identical to the file arm.

The claim's mechanism — "on seekable transports SoX can retry/re-read for
fallback classification; on pipes the ≤257 prefetch bytes are consumed" — is
**refuted on its own terms by my strace evidence**:

- `redirected_fd` on `nomatch_zeros.wav`
  (`runs/strace-nomatch-redir.txt:145-149`): `lseek(0,0,SEEK_CUR)=0` →
  `read(0,…,4096)=300` (one prefetch) → `lseek(0,300,SEEK_SET)=300` →
  **`lseek(0,-300,SEEK_CUR)=0` — the rewind SUCCEEDS** — then `+++ exited
  with 2 +++`. No second read, no second classification pass: the seekable
  capability is exercised and changes nothing, because `-` carries no
  extension.
- `fifo_path` on the same member (`runs/strace-nomatch-fifo.txt:145-149`):
  `openat(fifo)=3` → `lseek(3,0,CUR)=-1 ESPIPE` → `read(3,…,4096)=300` →
  second `lseek` ESPIPE → `close(3)` — **no further reads at all**, yet the
  wav-reader verdict `RIFF header not found` is emitted: the ≤257-B prefetch
  is *replayed to the fallback reader from the pending buffer*, not consumed.
  The "consumed on pipes" clause of the declared mechanism is false.
- `file` arm (`runs/strace-nomatch-file.txt:98-103`): `lseek(3,0,CUR)=0` →
  `read=300` → `lseek(3,300,SET)` → `lseek(3,1,SET)` → exit — reader-stage
  seeks only; no re-scan of the table on any transport.

Source corroboration (build-matched tree `/tmp/sox_ng_src/sox_ng/src/`,
`formats.c` sha256 `82c3058e…` **byte-identical to the lane's tag-verified
copy** `corpus/live/r64-reviewer/r64rev-formats.c` — re-verified by me this
session): the post-table dispatch (`open_read`, ~formats.c:910-933) reads
`ft->io_type` and `lsx_find_file_extension(path)` — **`ft->seekable` is never
consulted**. `lsx_io_pipe` is set only for `|cmd` pseudo-paths (xfopen
branch); `-` keeps `type=""` — hence the verbatim double space in
`can't determine type of  '-'`.

### txw / smp pipe-refusal members — the claim's predicted partition is real, but lives on a matched member

| member | detected ×4 | file | stdin_pipe | redirected_fd | fifo_path |
|---|---|---|---|---|---|
| `cand_txw.wav` (`LM8953`@0-5 + 294 B pad, 300 B, sha `4e68f8d3…`) | `txw` | **decode 178, exit 0** | `input must be a file, not a pipe`, exit 2 | **decode 178, exit 0** | `input must be a file, not a pipe`, exit 2 |
| `cand_smp.wav` (`SOUND SAMPLE DATA`@0-16 + pad, 300 B, sha `b54b9319…`) | `smp` | `header is not version 2.1 `, exit 2 | `input must be a file, not a pipe` | `header is not version 2.1 ` | `input must be a file, not a pipe` |

- **This is the declared claim's exact seekable partition** — `{file,
  redirected_fd}` vs `{stdin_pipe, fifo_path}` — delivered by a *matched*
  member: detection fires (`txw`/`smp` on all four arms, transport-invariant)
  and the fork lives inside the reader's own seekable gate (source:
  `tx16w.c:88-94` and `smp.c:226-233`, `if (!ft->seekable)
  lsx_fail_errno(…,"input must be a file, not a pipe")` — verbatim
  spot-checked this session), not in the post-table path.
- My txw 178-sample decode on the 300-B body is byte-for-byte the r66
  boundary's `g_txw_*` result (their 300-B carriers also read 178) and is
  consistent with the 12-bit packing arithmetic ((300−32) data bytes →
  floor(268/3)×2 = 178). Cross-seat decode counts differ only by body length
  (scout 332 B → 200, critic 600 B → 378) — same class.
- **txw is the better tracked member** (author's choice was declared
  cost-justified): 6-B predicate vs smp's 17-B; positive 178-sample decode on
  the seekable arms vs smp's reader-ladder fail — txw pins *two* classes at
  once (seekable-decode + pipe-refusal).

### The `.snd` name-gated CHECK row — detection itself forks on namedness (my spot-check)

`probes/nomatch_snd.snd` (300 zero bytes): file arm → **`detected file format
type 'sndr'`** → `invalid rate value`; `cat | sox -` and `sox - < f` → no
detection → `can't determine type of  '-'` (`runs/logs/snd-check.log`).
Source: `formats.c:247-248` `if (ext && !strcasecmp(ext,"snd")) CHECK(sndr,7,
1,"",0,2,"\0")` — confirmed verbatim. This is a live counterexample to the
r67 "detection never forks" invariant — detection can fork on the *input
name* before any transport byte matters. First reported by r68-scout/boundary
this round; my one-fixture check independently reproduces it. Member-design
consequence: **the fallback member must not be named `.snd`** (it would be
detected on the named arms and never reach post-table there).

### Third post-table signature off the 4-arm set — `|cmd` popen

`sox -V6 '|cat probes/nomatch_zeros.wav' -n stat` →
`assuming input pipe '|cat nomatch_zeros.wav' has file-type 'sox'` →
`sox FAIL formats: can't open input pipe '|cat nomatch_zeros.wav': can't find
sox file format identifier`, exit 2. The assume-sox rung is real and
unreachable by the declared four arms — consistent with scout/boundary.

### Receipt-determinism hazard — confirmed live, not just cited

`nomatch_zeros` (no extension) produced **3 verdict groups** in my matrix
because the `can't determine type of file '<path>'` message embeds the input
path, and `transport_error` (measure_audio.py:200-207) returns the whole FAIL
line when no `':` follows — so `error` carries the volatile mkdtemp fifo path
(`/tmp/transport-r67-mp17l09r/` in run 2 vs `/tmp/transport-r67-onh62l2t/` in
run 3 — byte-different receipts across identical runs). The r68 critic's
warning is thereby demonstrated, not merely endorsed: **an extension-less
tracked member name would produce non-deterministic receipts under the
current `error` field.** `.wav`/`.bin`-style names keep `error`
path-independent (my `.wav`/`.bin` rows are stable across all three runs).

## Harness sanity — prior-mode receipt byte-identical

`cd ~/Projects/prymeagnt/audio && python3 .shokunin/audio/corpus/fixtures/
measure_audio.py --probe-transport-dec-hcom-r67` → exit 0, fresh receipt
`corpus/live/runs/20261014T100820927597Z-transport-dec-hcom-r67/
measurements.json` — **`cmp` byte-identical to the author's committed r67
receipt** (`…/20261014T051943391440Z-transport-dec-hcom-r67/`). The harness
and tracked members are stable in my hands at HEAD `a0958a9`.

## Cross-seat convergence / conflicts — reported verbatim for the judge

Four independent seats now carry the same measured partition; none
contradicts another:

| seat | evidence class | partition found |
|---|---|---|
| r68-scout | 13 members × 8 transports, source-verified | `{file,fifo}` vs `{pipe,redir}` = named axis; claim "unreachable for ANY no-match member" |
| r68-critic | 6 no-match members × 4 arms + strace | identical transposed partition; mechanism falsified "twice over" (rewind succeeds, verdict unchanged; `.f32` fifo decodes 150/150 → prefetch replayed) |
| r68-boundary | 19-transport × 9-member matrix (229 legs) + strace | identical; five post-table verdict *classes* mapped (`ext-handler`, `can't-determine`, `no-handler`, `assume-sox`, `magic-detected`) |
| **this scribe** | 6 members × the landed `transport_matrix` itself + 3 straces + rerun | identical 2-group named partition; txw seekable fork 178-decode vs refusal; `.snd` and `|cmd` edges and the error-path-embedding defect each reproduced live |

- **Verdict on the declared claim: FALSIFIED as stated.** A post-table fork
  exists and is exactly measurable — but it partitions on the *named/extension*
  axis, never on seekability. The declared claim's own predicted grouping is
  realized by the txw member — on a *matched* row, inside the reader's
  seekable gate. Honest round framing (critic's suggested rewording, which my
  data supports): *matched members fork on the seekable axis (reader gates);
  post-table members fork on the named axis (extension dispatch).*
- No seat observed the author's landing; all falsifications are
  member-independent (the post-table path keys only on io_type + extension —
  whichever bytes/name the author picks cannot produce the declared
  partition, though `.snd` naming would produce a *detection* fork instead).
- Mechanism correction for the record: prefetch bytes are pending-buffer
  *replayed* to the fallback-selected reader on non-seekable transports
  (fifo `.wav` → identical reader verdict; strace shows zero post-prefetch
  reads), not consumed.

## Draft knowledge entry — for `corpus/knowledge/2026-10-15-sox-posttable-fallback.md` (fenced; parent lands it)

```markdown
# SoX_ng post-table fallback — full CHECK-table miss resolves by NAME (extension dispatch), never by seekability; txw member pins the genuine seekable-gated pipe refusal (round 68)

- Source: round-68 seat evidence (`reports/round-68/r68-{scout,critic,boundary,scribe}.md`; independent matrices `corpus/live/r68-{scout,critic,boundary,scribe}/…`); upstream sox_ng-14.8.0.1 `src/formats.c` (lane-verified copy `corpus/live/r64-reviewer/r64rev-formats.c`, sha256 `82c3058e…`), `tx16w.c`, `smp.c` — citations corroborative; load-bearing claims empirical.
- Verified at: 2026-10-14, host `/usr/bin/sox` SoX_ng v14.8.0.1 (USING_FFMPEG), ffmpeg/ffprobe n9.0.1.
- Recheck when: SoX version/build changes, when the CHECK table changes, when `AUTO_DETECT_SIZE` changes, when `lsx_find_file_extension`/`sox_find_format` or `ft->io_type` handling changes, or when member names/extensions change.

## The measured law (falsifies the round's declared wording)

After `auto_detect_format` returns NULL, `open_read` (formats.c ~910-933) resolves a handler purely by **name**:

    io_type == lsx_io_pipe   → filetype = "sox"     (|cmd pseudo-paths only)
    no extension             → "can't determine type of <io-str> `X'"
    unknown extension        → "no handler for file extension `X'"
    known extension          → that handler runs on the buffered prefetch

`ft->seekable` is never read on this path. On the tracked 4-arm transport set the verdict therefore partitions `{file, fifo_path}` (named → extension dispatch) vs `{stdin_pipe, redirected_fd}` (both spell `-`, extensionless → `can't determine type of  '-'`) — the **named axis**, the exact transpose of the declared seekable partition. The seekable rewind demonstrably happens (`lseek(0,-300,SEEK_CUR)=0` on `sox - < f`) and buys nothing — there is no second classification pass to feed.

## Prefetch bytes are replayed, not consumed

`lsx_readbuf_rewind` (formats_i.c ~178-218): seekable → `rewind()`; non-seekable → bytes stashed in `ft->pending_buffer` and replayed to whichever reader the dispatch selects. Proof classes: a `.wav`-named fifo gets the identical `RIFF header not found` verdict as the file (strace: ESPIPE, single read, no re-read); a `.f32`-named fifo decodes all samples (r68-critic, 150/150). "≤257 bytes consumed on pipes" is wrong as mechanism; consumption only matters to the ffmpeg bridge's *external* re-open (r67), which bypasses the buffer.

## Post-table verdict classes (5, measured)

extension-handler verdict | `can't determine type of <io-str> 'X'` | `no handler for file extension 'X'` | assume-`sox` (`|cmd` only) | `--magic` detected-MIME with no handler (off-ledger flag). None is selected by seekability.

## The genuine seekability fork lives on matched members

`txw` (`LM8953`@0-5, len≥6) and `smp` (`SOUND SAMPLE DATA`@0-16, len≥17) readers open with `if (!ft->seekable) → "input must be a file, not a pipe"` (tx16w.c:88-94, smp.c:226-233) — before any content read. Tracked member `pair_piperefuse_txw` shape: detected `txw` on all four transports; `{file, redirected_fd}` decode N samples exit 0 vs `{stdin_pipe, fifo_path}` refusal exit 2 — the seekable partition, inside the reader. txw preferred over smp: 6-B predicate + positive decode (300-B body → 178 samples: (len−32)÷3×2 for the 12-bit packing).

## Edges

- `.snd`-named members arm an ext-gated CHECK row (formats.c:247-248) → *detection itself* forks on the name (first counterexample to r67's detection-invariance). Never name the fallback member `.snd`.
- Extension-less member names embed the volatile path in the `error` field → non-deterministic receipts; keep an extension or scrub `error`.
- Starved fifo delivery can flip a *detected* member's detection at its len gate (protocol artifact); all-zero bodies are prefix-safe.
```

## LOG.md round-entry draft (fenced; parent edits)

```markdown
## Round 68 — devin host — depth: post-table fallback + pipe-refusal member

- Declared (author dispatch brief): pin the POST-TABLE FALLBACK path — claimed
  falsifiably that a no-CHECK-match member forks on transport seekability
  ({file,redirected_fd} vs {stdin_pipe,fifo_path}), with seekable transports
  retrying/re-reading for fallback classification and pipe transports losing
  the ≤257 prefetch bytes; plus land ONE tracked txw/smp pipe-refusal member;
  112 prior ledger rows + receipts byte-stable.
- Wave `shokunin-train-20261014-w7`: 8-seat devin leaf set
  `reports/round-68/r68-{scout,author,critic,reviewer,simplifier,scribe,baseline,boundary}.md`.
  Frozen baseline 112/112 rows (49/63 exits, 99 byte-identical + 13
  path-embedded-equal receipts, drift zero) at `bd5e1fe`; r68-reviewer audit
  of the r67 committed state SURVIVES on all items.
- Measured outcome — declared claim **FALSIFIED as stated** (four seats
  convergent: scout 13×8 matrix, critic 6×4 + strace, boundary 19-arm 229-leg
  matrix, scribe on the landed r67 machinery): post-table verdicts partition
  on the NAMED axis `{file,fifo_path}` vs `{stdin_pipe,redirected_fd}` via
  extension dispatch (formats.c ~910-933); `ft->seekable` is never consulted;
  the redirected-fd rewind succeeds and changes nothing; prefetch bytes are
  pending-buffer replayed, not consumed. The predicted seekable partition is
  realized instead by the txw member (`txw` detected ×4; {file,redir} decode
  vs {pipe,fifo} `input must be a file, not a pipe` — reader gate tx16w.c:90).
- Edges: `.snd` name gates a CHECK row → detection itself forks on namedness;
  `|cmd` assume-sox and `--magic` are post-table verdict classes off the
  4-arm set; extension-less member names would embed tmp paths in receipts.
- Per-axis verdict (Sol `r68-adjudicator.md`): PENDING.
```

## Touched surfaces / out-of-scope

- **Wrote:** `reports/round-68/r68-scribe.md` (this file);
  `corpus/live/r68-scribe/` — `probes/` (7 fixtures), `run_posttable.py`,
  `runs/posttable-matrix-run{2,3}.json`, `runs/posttable-run1.txt`,
  `runs/strace-nomatch-{file,redir,fifo}.txt`, `runs/nomatch-redir.stderr`,
  `runs/logs/{file-arms.log,snd-check.log}`.
- **Side-effect write outside my scratch (disclosed, unavoidable by harness
  design):** re-running the tracked measurer wrote one receipt dir
  `corpus/live/runs/20261014T100820927597Z-transport-dec-hcom-r67/` —
  untracked, append-only convention used by every r62–r67 seat; parent
  integrates or discards.
- **Zero tracked mutation:** `git status --porcelain` shows only `??`
  entries; `git diff HEAD` empty at write time. No commits/pushes/merges;
  no dispatches; no sibling-lane or shared-state writes. `git archive`
  not applicable to this seat (baseline owns it).

## Bounded UNKNOWNs / limits

- The author's r68 tracked landing was absent at every observation
  (final check 10:11 UTC) — my "re-run the author's landed arms" duty is
  discharged against the *arm machinery* (the landed r67 `transport_*`
  implementation itself, run verbatim on my members) plus raw `sox` legs;
  author-mode receipt comparison remains for the verifier once the diff
  lands.
- Single host/toolchain (SoX_ng 14.8.0.1 USING_FFMPEG + ffmpeg n9.0.1);
  verdict-level evidence, source cites corroborative.
- My no-match members are 300-B bodies (zeros/noise) — the verdict classes
  are member-independent per the dispatch code path, and three sibling
  matrices on different bodies (429-B text, 600-B family, RIFF+XXXX)
  agree, but member *names* other than .wav/.bin/no-ext were exercised by
  siblings (`.f32`/`.txw`/`.smp`/`.snd`/`.mp3`), not by me beyond `.snd`.
- txw/smp seekable-arm verdicts measured on 300-B minimal carriers; deeper
  reader ladders (txw truncated-header class, smp trailer seek) are
  boundary's territory (r68 `len_eof_forced.tsv`) — not re-run here.
- No standards-conformance, decoder-correctness, fidelity, audibility,
  production, rights, engine, or promotion claim — local fixture
  measurements only.

## Stop

Report complete. Leaf seat: nothing further.
