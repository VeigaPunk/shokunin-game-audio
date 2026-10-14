# R67 critic — attack the TRANSPORT axis landing

Seat: critic. Target: the r67 declared move — pin TRANSPORT as a measured
first-class axis; per-member {file, stdin-pipe, redirected-fd, fifo-path}
detection+decode verdict matrix on `measure_audio.py`; 102 prior rows +
receipts byte-stable. Host: SoX_ng 14.8.0.1 (`/usr/bin/sox`), ffmpeg n9.0.1,
python 3.14.7. Scratch: `corpus/live/r67-critic/` (`NOTES.md`, `matrix.tsv`,
`fifo.tsv`, `logs/` — my independent 5+2-transport matrix incl. `/dev/stdin`
and fifo-as-fd legs the arm doesn't cover). No tracked writes; no commits.

**Author-landing status**: `corpus/fixtures/measure_audio.py` +183/−3 landed
uncommitted (10 `--probe-transport-*-r67` flags, `transport_{error,leg,matrix,
entry}` helpers, `TRANSPORT_R67_*` constants). Author's ledger run 3 is
contiguous and clean; runs 1–2 each self-quarantined one crashed row as
`ledger-r67-run{1,2}-defect.tsv`.

## Verdict

**The arm SURVIVES all five attack angles — the strongest counterexample found
is outside it.** Independently re-measured fork set on the landed
implementation matches the author's exactly: **5 forking members**
{preempt_act, preempt_gsrt, preempt_both, dec_act, lengate_gsrt_25} =
precisely the gsrt- and act-detected members; **5 invariant** {preempt_hcom,
dec_hcom, lengate_gsrt_24, lengate_hcom_131, lengate_hcom_132} = the hcom- and
wav-detected members. 102/102 prior receipts byte-identical (author's
`compare_receipts.py`, re-run by me); my own receipts for the forking members
are byte-identical to the author's ledger receipts.

**The real defect surfaced this round is process-level, pre-existing, and
already cost this wave two ledger rows**: concurrent `measure_audio.py`
invocations race `build_artifacts.py`'s non-atomic in-place rebuild of
`corpus/artifacts/*.wav`. Author run 1 row 06 (`transport-dec-hcom`) crashed
`ValueError: Invalid number of FFT data points (0)` — sox decoded 0 samples
from a mid-rewrite fixture; run 2 row 26 (`ui-extensible-valid-56-r64`, a
*prior* mode) crashed on `ffprobe … artifacts/impact.wav` exit 1. Mechanism
proven below; fix is small (atomic `save()`).

## Attack 1 — is the fork set complete? (transports the ledger doesn't cover)

I ran two transports beyond the arm's four on all 10 members:

- **`sox /dev/stdin < member`** (named path, seekable target): act members
  **decode** (278/3839, exit 0) — identical to `file`.
- **`cat member | sox /dev/stdin`** (named path, pipe target): act members
  fail `can't find Sun/NeXT/DEC identifier` — identical to `stdin_pipe`.
- **`sox - < fifo`** (fifo bytes on fd0, `-` spelling): `preempt_both` →
  `invalid format for this file type` — identical to `stdin_pipe`.

Result: **the author's {named × seekable} 2x2 is confirmed by the cell that
discriminates it** — `/dev/stdin` on a regular file is (named, seekable) and
decodes exactly like `file`; the *same spelling* on a pipe fails. The bridge
requires a **re-openable path whose re-open yields seekable data**, not merely
a seekable fd: `redirected_fd` (unnamed `-`, seekable) fails `premature EOF`
while `/dev/stdin` (named, same fd class) decodes. Every spelling I tried
lands inside the declared 2x2 — the four arms are complete representatives.
Forced legs corroborate mechanism: `cat pair_dec_act.wav | sox -t act -`
decodes **278 on a pipe** — the fork is the *autodetect prefetch*
(pending_bytes→au-reader poison), not the bridge needing seekability.

## Attack 2 — fifo semantics (hang/orphan risk)

**Confirmed real, and the landed fix works.** With a naive one-shot writer,
the fifo-path leg on act members is *racy*: 6 identical trials gave 5×
exit-2 in ~4 ms and 1× **sox blocked ≥6 s** (log stops before the `detected`
line). Worse, every such leg — even the 4 ms clean-fail ones — leaks an
`ffmpeg -i <fifo> -f au -` blocked in `open()` **permanently** (survives sox's
exit, `timeout` kill of sox, and fifo `unlink`). Host census during the wave:
28 blocked ffmpegs — boundary's `.fifo_probe`×10 + `.race_fifo`×5, reviewer's
`/tmp/r67rev_fifo`×2, author's *scratch* `r67-author/fifo`×2 (pre-fix),
scribe×1, `/tmp` misc×4.

The landed `TRANSPORT_R67_FIFO_WRITER_HOLD_S = 1.0` (writer writes, lingers
holding the fifo open, then closes) resolves the bridge's second `open()`
deterministically: **10/10 landed-mode runs on the two act members produced
byte-identical receipts and zero `transport-r67-*` orphans.** Residual, not
blocking: the 1.0 s constant is probabilistic — if ffmpeg's exec were delayed
past the linger under extreme load, `open()` misses the writer → hang +
orphan + verdict records `blocked: no verdict within 10 s`. Self-describing
if it ever trips; airtight alternative is holding the fifo `O_RDWR` for the
arm duration (permanent writer, no timing constant) or killing sox's process
group.

## Attack 3 — does transport interact with detection?

**No.** `sox_detected_format` is identical across all four arms on all 10
members in both my matrix and the ledger receipts. Additionally I trickle-fed
a pipe — `(head -c100; sleep 1.5; tail -c+101) | sox -` — and detection still
returned `act`: sox blocks to fill the 257-byte autodetect buffer, and an
EOF-terminated short fill (<257 B members like lengate_gsrt_24) detects
identically. No detect-stage fork exists on this member set; every fork is
decode-stage, consistent with the author's claim.

## Attack 4 — receipt determinism

**Clean.** 6/6 byte-identical receipts for `transport-preempt-act-r67`, 4/4
for `transport-dec-act-r67` (sha `195d7554…`, matching the author's reported
rerun digests); my receipts byte-equal the author's ledger receipts. The
`stderr_tail` scrub (`` `…' → `<input>' ``, ASLR ` @ 0x…]` stripped) erases
the `tempfile` fifo path and `-` vs path spellings; `input` labels are static
(relpath / `-` / basename). `transport_protocol` pins the only
protocol-sensitive values (arm_timeout_s, fifo_writer_hold_s, feed shape).
Residual edge (unexercised on this member set): the scrub only catches
backtick-quoted names — a hypothetical unquoted-path FAIL line would leak the
tmpdir path; none of the 10 members emit one.

**But the ledger *run* is not determinism-safe under concurrency** — see the
main counterexample below.

## Attack 5 — are "invariant" members invariant across all four?

Yes, verified independently on all four arms plus my two extra spellings:
`dec_hcom` dec 9×6, `lengate_hcom_131` dec 43×6, `preempt_hcom`/`lengate_
gsrt_24`/`lengate_hcom_132` fail identically ×6. The non-autodetect tracked
members are all wav-routed — wav is transport-invariant (proven by the two
in-matrix wav controls plus `ui.wav` 5760×4 in my scratch and the author's).
The member-subset justification ("every member whose route is a detection
decision") holds.

## The counterexample (process-level, now disclosed but unfixed)

Two of the author's three ledger runs each lost exactly one row to a
concurrent-rebuild race:

- run 1 row 06 (`--probe-transport-dec-hcom-r67`): `ValueError: Invalid
  number of FFT data points (0)` — `np.fft.rfft` on an empty decode inside
  `measure()`'s SPECS phase.
- run 2 row 26 (`--probe-ui-extensible-valid-56-r64`): `CalledProcessError` —
  `ffprobe … artifacts/impact.wav` exit 1 mid-rewrite.

Mechanism, proven in scratch: `wave.open(path, "wb")` writes a valid header
claiming 0 frames while frames flush; a concurrent `sox wav -t f32 -` in that
window returns 0 bytes + exit 0 → `np.fft.rfft` of an empty array raises the
*byte-identical* error text (`/tmp/empty.wav` demo in NOTES.md). Corroborating
concurrency: `runs/` timestamps show interleaved transport receipts at
05:15–05:16 inside the author's ledger window, and a second
`measure_audio.py --probe-ui-crest-46` (baseline replay, PID 2196572) ran
alongside the author's `run_ledger.py` (PID 2157032) during run 2.

Impact on the declared claim: "102 prior rows + receipts byte-stable" is
demonstrated only for a **serially-executed** ledger. Under concurrent
invocation — the wave's actual operating mode — a row can crash (loud, caught
by compare via missing receipt/exit mismatch) or produce a silently
byte-different receipt (partial decode → different duration/measure values —
still caught by byte-compare, but a corrupted artifact exists). Not
introduced by this arm (the SPECS phase is identical for every mode), but the
first wave where it produced observed damage on tracked rows.

## Claim-wording correction (minor)

The brief's parenthetical "gsrt does — file vs pipe" is true only at the
normalized-`error` level: tracked gsrt members exit 2 on **all** transports
and never decode (encoding byte `0x0177` → `invalid format for this file
type` on non-seekable, `invalid/missing file name` on the 25-byte member).
The r65/r66 "88 samples on pipe" was a non-tracked variant carrying a valid
gsrt encoding byte (`coll_gsrt_alaw` class; author correctly notes the tracked
`pair_preempt_gsrt` is `coll_gsrt_g726`). Under the landed signature
(detected, route, exit, samples, error) the gsrt members fork → the claim
stands as implemented; under a stricter {exit, samples}-only reading the fork
set would be {2 act members}. Either way ≥1 member forks — the core claim is
confirmed, but "verdict forks" should be read as verdict+error signature.

## Impacted axes

- **claim-fidelity**: CONFIRMED — fork set over the tracked autodetect family
  is exactly {gsrt∧act-detected} = 5 members; invariance set = {hcom∧wav} = 5.
  gsrt forking is die-position-level on the tracked members, not decode-level.
- **depth**: transport now a measured receipt axis; additionally pinned this
  round: `-` vs `/dev/stdin` split proves the bridge's need is a re-openable
  path (pending-poison on `-`, path-reopen on named), and forced `-t act`
  decodes on pipes — autodetect×prefetch is the true fork locus.
- **coverage**: the 4-arm matrix is complete under the {named × seekable}
  factorization — /dev/stdin and fifo-as-fd probes land inside declared cells.
- **calibration**: `premature EOF` on a seekable `-` = nameless-input bridge
  failure (not a read-EOF); `invalid format for this file type` on non-
  seekable gsrt = checksum-skipped encoding-check die; `blocked:` verdict
  exists for contended-fifo. New: a `UNPARSED` ledger row can mean a
  concurrent-rebuild flake, not a mode defect — check sibling activity before
  attributing.
- **byte-stability**: 102/102 verified post-landing; new receipts
  deterministic across my and the author's processes. Conditional caveat:
  only under serial ledger execution (see counterexample).

## Smallest safe correction

1. `build_artifacts.py` `save()`: write to a sibling temp path then
   `os.replace()` (atomic rename). Removes both the crash and the
   byte-divergent-receipt class under concurrent runs — the fix that makes
   "receipts byte-stable" robust to the wave's real operating mode.
   (~3 lines; alternatively a lockfile around the build+measure phase.)
2. Optional hardening of the fifo arm: hold `O_RDWR` on the fifo for the arm
   duration instead of timing the writer linger — eliminates the residual
   >1.0 s spawn-delay race and the `blocked:` verdict path entirely.
3. Wording: record that `transport_fork` counts normalized-error forks — the
   gsrt members fork on die position, not on exit/samples.

## Receipts / evidence

- `corpus/live/r67-critic/{NOTES.md,matrix.tsv,fifo.tsv,logs/}` — independent
  5+2-transport matrix over all 10 members; fifo race log; trickle test.
- Landed runs (mine): `runs/20261014T05173{4,6,8}*`–`052*` transport receipts,
  6× sha-identical `preempt-act` (`434d82d3…`), 4× `dec-act` (`195d7554…`),
  byte-equal to author's ledger receipts `20261014T0522{09,19}*`.
- Prior-mode byte-stability spot: `runs/20261014T052259607461Z-ui-dec-hcom-r66`
  ≡ r66 `023252189954Z`; `052302995453Z-ui-preempt-both-r65` ≡ `023301983754Z`.
- Author ledger: `r67-author/ledger-r67.tsv` 112 rows (49 exit-0/63 exit-1);
  `compare_receipts.py` re-run by me → "102 prior-mode pairs, 0 mismatches".
- Defect evidence: `r67-author/ledger-r67-run{1,2}-defect.tsv` rows 06/26;
  mechanism demo `/tmp/empty.wav` → 0-byte decode + identical ValueError;
  orphan census `pgrep -af "ffmpeg -loglevel"` → 28 blocked bridge processes
  (none on `transport-r67-*` paths post-fix).
