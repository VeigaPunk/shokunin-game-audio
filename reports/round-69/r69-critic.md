# R69 critic — declared claim VERIFIED on the landed diff (named arm = 6 verdict outcomes across 5 identical-byte members; `.snd` is a real DETECTION fork, first tracked member); census sound only as coverage bookkeeping — "dead" mislabels ≥16 live rows I detect today (plus `wma` dead-by-shadow, the one row that deserves the label); author's scratch `check_table.py` cannot return `sndr` (literal-decoding bug on the one row this round measures); prior-114 byte-stable on a 6-mode post-diff replay sample

Seat: **critic** (leaf). Lane: audio. Repo `~/Projects/shokunin/audio-shokunin`
(worktree `~/Projects/prymeagnt/audio`, `.shokunin/audio` symlink). Host:
SoX_ng 14.8.0.1 `/usr/bin/sox` (USING_FFMPEG + libsndfile + libmagic linked),
ffmpeg/ffprobe n9.0.1, python 3.14.7. Landing state at measurement: HEAD
`7b8d423`, working tree carries the author's r69 diff (`measure_audio.py`
+49/−3, `build_artifacts.py` +46/−1, five 512-B members
`corpus/live/round-69/extsuffix_nomatch.{wav,bin,txw,f32,snd}` all sha256
`f073e70ad6e9d8c9f06697a9ca61d0a67bf4c351bcbe742c06c4a611d9d5e5d7`).
Scratch `corpus/live/r69-critic/` — `probes/` (14 renamed members on 2
byte-shapes), `probes2/` (5 sndr-conjunct probes), `checkrows/` (31
live-row battery), `run_matrix.sh` → `runs/matrix-hold1.0.tsv` (52 legs),
`logs/` (per-leg stderr).

## Attack item 1 — is the extension-suffix partition real, and could the split be a harness artifact?

**Real — independently reproduced at two levels.**

(a) *Raw legs on my own renamed members* (`run_matrix.sh`, mirrors
`transport_matrix` arms + `transport_leg` extraction): identical 300-zero
bytes (`d13d4a8b…`) under 8 names give six named-arm outcomes —
`.wav`→`RIFF header not found`, `.bin`/`.xyz`→`no handler for file
extension '<e>'`, `.txw`→file `invalid filetype ID…` / fifo `input must be
a file, not a pipe`, `.f32`→decode 75 exit 0, `.snd`→detected `sndr` +
`invalid rate value`, `.au`→`can't find Sun/NeXT/DEC identifier`,
`.raw`→`sample rate is zero or negative`. Identical r68-member bytes
(512 B, sha `6373923f…`) under 6 names give the same classes **except
`.snd`** (see attack 2 — content contract).

(b) *The landed probes themselves* — ran all five modes on the landed
harness (`timeout 180 python3 corpus/fixtures/measure_audio.py
--probe-transport-extsuffix-{wav,bin,txw,f32,snd}-r69`, receipts
`runs/20261014T110053–110101Z-transport-extsuffix-*-r69/`). On the
author's buffer the named arm produces: `.wav`→`RIFF header not found`,
`.bin`→`no handler 'bin'`, `.txw`→`invalid filetype ID != LM8953` (file)
vs `input must be a file, not a pipe` (fifo) — the member itself is
**3 verdict groups**, `.f32`→decode **128** exit 0, `.snd`→detected
`sndr` → decode **504** exit 0. **≥3 satisfied at six distinct named-arm
outcomes across five members** — claim VERIFIED. (The `.snd` reader lands
on decode-504, not the `invalid rate value` of a zero buffer — the ramp's
u16-BE rate @2–3 is `0x1118`=4376; same detection fork, different
reader-ladder rung. Scribe measured the same.)

**Could the split be fabricated by the harness?** Checked three suspects:

- *fifo writer timing*: verdicts are writer-**content**-dependent, not
  linger-dependent. Same 300-B member under hold=0 / hold=1 s / 1 B-per-
  10 ms trickle / 2 B-then-rest writers → identical verdicts on
  `.snd`/`.txw`/`.f32`/`.wav` (`/tmp/fifo_slow.py` runs, `logs2/`). But a
  writer that pushes **2 B then closes** flips `.snd` fifo to
  `premature EOF` (detection still `sndr` — the row arms at len≥2) and
  `.f32` to `0 samples` exit 0. Under the pinned protocol (one-shot write
  ≤ pipe buffer + 1 s linger) deterministic — my hold0/hold1/chunk
  agreement is direct evidence; boundary's `fifo_starve.tsv` maps the
  full N-byte boundary (wav's truncated|not-found flip is
  byte-content-dependent via `lsx_reads` NUL early-out).
- *prefetch accounting*: AUTO_DETECT_SIZE=257 < member 512 — fifo decodes
  full bytes (`f32` 128 = 512/4; `sndr` 504 = 512−8 header) — pending-
  buffer replay is non-lossy on these members. No artifact.
- *fifo-name extension*: the scout's own runner showed the hazard —
  `mktemp --suffix ".nm_zeros_noext"` fabricates a `nm_zeros_noext`
  extension, splitting file (`can't determine type of file`) from fifo
  (`no handler for file extension 'nm_zeros_noext'`) on a *nameless*
  member. The landed harness uses `Path(tmp)/path.name` — basename
  preserved exactly — so no split is fabricated on named members
  (verified: all five receipts' fifo `input` = member basename; no
  `/tmp/` or `transport-r67-` substring in any of the five receipts).
  The `.mp3` empty-verdict/SIGTERM race scribe+boundary flagged does not
  touch the five landed members.

## Attack item 2 — is the `.snd` detection-fork real DETECTION vs a reader verdict?

**Real detection, byte-level verified.** On the landed receipt
(`runs/20261014T110101884677Z-transport-extsuffix-snd-r69/measurements.json`):
`file`/`fifo_path` arms carry `sox_detected_format="sndr"` (route
`native`, exit 0, 504 samples); both `-` arms carry `null` + `sox FAIL
formats: can't determine type of  \`-'`. My own stderr captures show the
emitting `sox INFO formats: detected file format type 'sndr'` line on
named arms and its **absence** on `-` (`logs/cz_nomatch.snd.*.stderr`
counts: file 1, fifo 1, pipe 0, redir 0). The row fires inside
`auto_detect_format` (formats.c:247-248 `if (ext &&
!strcasecmp(ext,"snd")) CHECK(sndr,7,1,"",0,2,"\0")`) — detection
proper, evaluated before post-table dispatch; `ft->seekable` is never
consulted. The fork partitions on the **named** axis
{file,fifo}=`sndr` vs {pipe,redir}=null — redirected_fd is
seekable-but-anonymous and gets no detection at all.

**"First tracked member where detection forks"** — verified two ways:
every committed `transport_axis` receipt entry I scanned (r67's 10 +
r68's 2 members ×4 arms) has detection uniform across arms; the ledger's
receipt field has never before differed. TRUE.

**But the fork is content-contracted — checked the boundary:** the sndr
conjuncts are `data[0:2]=={0,0}` ∧ `data[7]==0` ∧ `ext=="snd"`
(case-insensitive). `probes2/nz7.snd` (300 B, byte 7 = `0x41`) → **no
detection** → post-table ext `snd` → `can't find Sun/NeXT/DEC identifier`
(the au-dispatch fate — `snd` resolves to the au handler at au.c:221).
And the tracked r68 member's bytes (starting `ufo-r68 post-tab…`) renamed
`.snd` → same au verdict, `detected=null` on all 4 arms. **Had the author
reused r68 bytes, the "detection itself forks" clause would be falsified**
— the claim is bound to the zero-prefix contract the landed buffer
satisfies (`b[0]=b[1]=b[7]=b[256]=0`; my byte-exact table replica fires
**zero** non-gated rows on it, sha `f073e70a…` matching the code comment).
Short-member edge: `z2.snd`/`z7.snd` still detect `sndr` (the row's
`data[7]` read is unguarded at len<8 — boundary's 46/46 determinism
matches; the conjunct lives in a reader-skipped field).

## Attack item 3 — dead-CHECK-row census soundness: "never first-match" ≠ "dead"

Table truth (all four seats converge): **131 source `CHECK(` rows** at
`corpus/live/r64-reviewer/r64rev-formats.c:78-248` (sha `82c3058e…` ==
upstream tag), **130 compiled in this build** (adx:165 inside `#if 0`),
~77 distinct types, exactly one ext-gated row (sndr:248). The brief's
"~97" undercounts — 130 is the measured number.

Receipt scan (mine, independent): 4,784 `runs/*/measurements.json` —
`sox_detected_format` values = **`{act, gsrt, hcom, txw, wav}` + null** —
5 types ever first-match in ledger receipts. Scout's ledger census
(5/130) and scribe's three-tier census (ledger 5 / recorded 16 /
simulated 20 over all tracked files) bracket the same scope ladder.

**The "dead" label is unsound as stated — live rows it mislabels:**
`corpus/live/r69-critic/checkrows/` holds 31 minimal-magic members, each
`sox -V6 <f> -n stat`-probed — **28 types detect today that have never
first-matched in any committed receipt**: `wve` (`ALawSoundFile**`),
`smp` (`SOUND SAMPLE DATA`), `sph` (`NIST_1A`), `au` (`.snd` magic),
`8svx`/`aiff`/`maud`/`nsp` (FORM variants), `xa`, `flac`, `voc`, `caf`,
`wv`, `paf`, `pcm` (MSU1), `sf`, `sox` (.SoX), `prc`, `amr-nb`, `amr-wb`,
`wsd`, `sds`, `mpc2k`, `avr`, `sndt`, `dsf`, `mp4` (ftypisom), plus `wav`
**via the RIFX and RF64 rows** (`checkrows/rifx.wav`, `rf64.wav` →
`detected 'wav'`). None of these rows is dead — the member corpus simply
never carried their bytes. Coverage bookkeeping is the correct reading;
"dead" is the wrong word.

**Sharper falsification of scout's RIFX/RF64 "dead-verified" call:**
git-tracked members *do* carry those bytes —
`corpus/live/r63-critic/var/D_rifx_{00,84,pcm16_84}.wav`,
`D_rf64_84.wav`, `corpus/live/r65-boundary/probes/m_rifx_*.wav`,
`m_rf64_act.wav` — and committed `r63-critic/sweep_results.csv:1382-1387`
records `wav` detections on them. The scout's hex survey covered
`round-5[5-9],6[0-8]` member dirs and missed `r63-critic/var/` +
`r65-boundary/probes/`. Scribe's recorded tier catches the same rows.

**The one row that IS dead — for the right reason:** `wma:238` shares
the *identical* 16-byte GUID predicate as `asf:174`
(`\x30\x26\xB2\x75…\x6C`) and `asf` is earlier in first-match order —
demonstrated: `checkrows/wma.bin` → `detected 'asf'`. `wma` can never
first-match while `asf` precedes it — dead *by construction*, the only
row in the table provably so (my identical-predicate scan finds no other
pair). This is what "dead" should mean; the receipt census cannot
distinguish it from the 16+ live rows it equally labels dead.

Row-vs-type attribution bound (scribe's caveat, extended): receipts
record the winning **type** only — the 3 wav rows, 4 au, 7 sf, 9 ea, 5
avi/flv, 4 eac3/mov/mp4, 3 adts/xa/argo_asf/3gp/aac-asf... all collapse
to one detected name; a per-ROW census is underdetermined by receipts
alone even at simulation scope.

## Attack item 4 — ledger rows / prior-receipt drift — none found

- **Row arithmetic**: HEAD `measure_audio.py` = 108 probe flags; landed
  diff +5 → 113. Ledger convention (r68 TSV): 109 mode rows + 5 extra
  `-normal` determinism rows = 114. Landed expectation **119 rows**,
  exits 49/65 → 49/70 (all five new rows fork → exit 1). Scribe/scout
  predict the same. Mutual-exclusion `sum()` extended +5; `mode`/`suffix`
  chains prepended newest-first (5 hyphenated occurrences per member =
  flag + forwarder + mode + suffix — matches r68's ×4 convention).
- **Post-diff byte-stability (sampled 6 modes on the landed tree)**:
  `--probe-transport-posttable-nomatch-r68` → sha `52bbb1a9…` and
  `--probe-transport-txw-piperefuse-r68` → `762aff12…`, both byte-
  identical to the committed r68 receipts; `transport-preempt-act-r67` =
  committed 18,871 B; `transport-dec-act-r67` identical to **all 25**
  committed copies; `ui-route-act-84-r63` = all 21; `ui-lengate-
  gsrt-25-r66` = all 13. `git status --porcelain` on `corpus/live/runs`
  shows zero tracked-receipt modifications (4,670 tracked; untracked =
  fresh concurrent-seat run dirs only).
- **Diff audit**: `measure_audio.py` +49/−3 (the 3 "deletions" are the
  re-wrapped `sum()`/`mode`/`suffix` chain lines — extended, not
  altered); `build_artifacts.py` +46/−1. Shared `transport_leg`/
  `transport_matrix`/`transport_entry` untouched. Members byte-identical
  ×5, sha `f073e70a…`.
- **Nit (inert)**: `build_artifacts.py` dispatch reorders the r68 `if`
  into an `elif` after the r69 arm — semantics change only on multi-flag
  invocation, which `measure_audio.py`'s mutual exclusion already
  forbids. Inert under the harness contract.
- **My own footprint**: `py_compile` during verification regenerated the
  two tracked `.pyc`; restored both to HEAD bytes via `git show
  HEAD:... > ...` — tree left exactly as the author landed it.

## Internal inconsistency found (LOW — scratch tool, not the claim)

The author's scratch `corpus/live/r69-author/check_table.py` parses the
CHECK table correctly (131 rows / 1 compiled-out / 1 ext-gated — agrees
with everyone), but `first_match()` **cannot return `sndr`**: it decodes
the row's literals to `d1=b'\x00'` (1 B vs `l1=2` needed — the C literal
`"\0"` is the two-byte array `{0,0}`) and `d2=b''` (0 B vs `l2=1` — `""`
is the one-byte array `{0}`), so `data[0:2] != b'\x00'` and
`data[7:8] != b''` fail by construction. Run on the author's own landed
buffer: `first_match(buf, 'snd') → NULL` — the simulation predicts **no**
detection while the measured receipt shows `detected 'sndr'`. The bug is
confined to the sndr row (the only row whose literals are `""`/`"\0"`
with nonzero compare lengths) — the tool's NULL verdicts for
wav/bin/txw/f32 remain valid, and the *measured* `matrix-r69.json` +
receipts are correct. But if the author report cites the simulator as
corroborating the `.snd` fork, that citation is backwards on the exact
row this round measures. Fix: decode `d""`-class literals as the C array
(contents + implicit NUL) before slicing to compare length.

## Verdict on the declared claim

Both clauses **VERIFIED on the landed diff**, with sharpenings:

1. Named arm splits ≥3 groups by extension alone on identical bytes —
   measured **six named-arm outcomes / five members** (`.txw` alone is
   three 4-arm groups; `.snd` and `.f32` share the
   `{file,fifo}|{pipe,redir}` shape with distinct signatures).
2. `.snd` is the first tracked member where **detection** forks on
   transport name — `{file,fifo}='sndr'` vs `{pipe,redir}=null`,
   byte-level in receipts and stderr; content-contracted to
   `b[0]=b[1]=b[7]=0` (the landed buffer satisfies; r68 bytes would
   falsify — the contract is part of the member).
3. The census is sound **as coverage bookkeeping** — 5/130 ledger,
   ~20/130 broadest-scope — and unsound as deadness: ≥16 demonstrably
   live rows sit in the "dead" set, while `wma` is the one row dead by
   construction (predicate-identical, `asf`-shadowed). Terminology fix
   recommended: *unexercised-in-scope*, per scope tier.
4. No drift: prior-114 receipts byte-stable on the post-diff tree
   (6-mode sample, 0 diffs vs committed copies); ledger arithmetic
   114→119 consistent; diff additive modulo one inert `elif` reorder.

## UNKNOWNs / limits

- All findings single-host/toolchain (SoX_ng 14.8.0.1 USING_FFMPEG,
  libsndfile+libmagic). `HAVE_MAGIC` post-table path unexercised (not a
  CHECK row; `--magic` off by default).
- The fifo verdicts under adversarial/truncated writers are
  protocol-dependent — the pinned one-shot+linger protocol is what the
  receipts mean; boundary's starve matrix owns the full N-byte picture.
- Census "simulated" tier inherits the table parser's literal-decoding
  caveat — verify any per-row dead list against a corrected evaluator
  (the sndr bug above shows the class of error).
- Receipt-level detection history does not cover `|cmd`/`--magic`
  spellings or formats reached only via extension dispatch (aptx, dfpwm
  comments in formats.c:169,181) — those rows are dead-by-design for
  detection but live via names[]; out of ledger scope.
- No fidelity/conformance/production claim; leaf seat — no commits, no
  dispatches, no writes outside `reports/round-69/r69-critic.md` +
  `corpus/live/r69-critic/` (`.pyc` churn reverted).
