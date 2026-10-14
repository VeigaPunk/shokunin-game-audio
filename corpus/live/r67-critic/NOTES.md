# r67-critic scratch evidence

Host: sox SoX_ng 14.8.0.1 /usr/bin/sox, ffmpeg n9.0.1, python 3.14.7.

## Landed diff (observed ~05:16 UTC): corpus/fixtures/measure_audio.py +183/-3
- 10 new flags --probe-transport-{preempt-act,preempt-gsrt,preempt-hcom,preempt-both,
  dec-hcom,dec-act,lengate-gsrt-24,lengate-gsrt-25,lengate-hcom-131,lengate-hcom-132}-r67
- TRANSPORT_R67_ARMS = file(named+seek)/stdin_pipe(unnamed+nonseek)/redirected_fd
  (unnamed+seek)/fifo_path(named+nonseek); members = the 10 tracked autodetect pair wavs.
- transport_leg: `sox -V6 <input> -n stat`, timeout 10s, capture_output.
  stdin_pipe: subprocess input=bytes (real pipe). redirected_fd: stdin=open file (seekable fd).
  fifo_path: tempfile.TemporaryDirectory fifo + daemon writer thread:
  write bytes, sleep 1.0s holding the fifo open (TRANSPORT_R67_FIFO_WRITER_HOLD_S),
  close; join(<=6s) in finally.
- error extraction: last `sox FAIL` line, text after "': " ; None on decode.
- signature/grouping key: (detected, route, exit_code, samples_read, error).
- stderr_tail: `...` strings scrubbed to `<input>` + ASLR ` @ 0x...]` stripped, [-160:].
- transport_fork = len(groups)>1 -> adds a failures[] entry -> mode exit 1.
- Receipts: corpus/live/runs/<stamp>-transport-<member>-r67/measurements.json

## Independent transport findings (this seat)

matrix.tsv / fifo.tsv / logs/ in this dir.

1. `/dev/stdin` path-arg splits the same fd by seekability:
   `sox /dev/stdin < pair_dec_act.wav` (seekable) -> act, 278 samples, exit 0.
   `cat pair_dec_act.wav | sox /dev/stdin` (pipe) -> Sun/NeXT fail.
   `sox - < pair_dec_act.wav` (seekable fd, UNNAMED) -> `premature EOF` exit 2.
   => the bridge needs a re-openable PATH, not merely a seekable fd. The author's
   {named x seekable} 2x2 is corroborated: /dev/stdin<reg = (named,seek) = file;
   /dev/stdin<pipe = (named,nonseek) = fifo class. `sox - < fifo` = (unnamed,
   nonseek) = stdin_pipe class (preempt_both -> invalid format, verified).

2. Forced legs: `cat pair_dec_act.wav | sox -t act - -n stat` -> 278 samples
   (works on pipe!), `sox -t act - -n stat < pair_dec_act.wav` -> 278 (seekable).
   => autodetect-on-`-` is what poisons the bridge (pending_bytes), not "bridge
   needs seekable". Detected-act is transport-forked; forced-act is not.

3. fifo-path with ONE-SHOT writer is RACY on act members: 6 trials ->
   5x exit 2 (~4 ms, au-magic poison) + 1x sox blocked >=6 s (timeout 124).
   Blocked run's log ends after the banner — hang precedes detection output.
   Also every fifo act leg leaks an `ffmpeg -i <fifo> -f au -` blocked in open()
   FOREVER (survives sox exit, timeout kill, fifo unlink). Census at ~05:20 UTC:
   boundary seat .fifo_probe x10 + .race_fifo x5, reviewer /tmp/r67rev_fifo x2,
   author scratch r67-author/fifo x2 (pre-fix), scribe .fifo x1, misc /tmp x4.
   => the author's writer-hold (1.0 s linger) is a REAL fix: 10/10 landed-mode
   runs deterministic, zero transport-r67-* orphans. Residual: if ffmpeg's exec
   is delayed >1.0 s under load, open misses the writer -> block + orphan
   (recorded verdict becomes "blocked: no verdict within 10 s"). Airtight fix:
   harness holds fifo O_RDWR for the whole arm (permanent writer) or kills the
   sox process group.

4. Detection is transport-invariant incl. trickle-feed:
   `(head -c100 f; sleep 1.5; tail -c+101 f) | sox -V6 -` still detects `act` —
   sox blocks to fill the 257-byte autodetect buffer; EOF terminates the fill for
   <257 B members. No detect fork observed on any transport.

5. Landed-mode determinism (this seat's runs, runs/2026*):
   - preempt-act x6 -> 6/6 receipts sha-identical (434d82d35902...), groups:
     file=dec 3839 | stdin_pipe/fifo_path=can't find Sun/NeXT/DEC identifier |
     redirected_fd=premature EOF
   - dec-act x4 -> 4/4 identical (195d755410c9...)
   - preempt-gsrt: file/redir=premature EOF | pipe/fifo=invalid format -> fork
   - preempt-both: same split -> fork
   - lengate-gsrt-25: file/redir=premature EOF | pipe/fifo=invalid/missing file
     name in header -> fork
   - preempt-hcom: bad compression type x4 -> invariant (exit 0)
   - dec-hcom: dec 9 x4 -> invariant (exit 0)
   - lengate-gsrt-24: fmt chunk not found x4; lengate-hcom-131: dec 43 x4;
     lengate-hcom-132: premature EOF x4 -> invariant
   => verdict-fork set under the landed signature = 5 members
     {preempt_act, preempt_gsrt, preempt_both, dec_act, lengate_gsrt_25}.
     Under a stricter {exit,samples}-only signature it would be {2 act members}.
     The brief's "(gsrt does - file vs pipe)" holds only via the error field —
     tracked gsrt members never decode on any transport (encoding byte 0x0177
     invalid -> `invalid format for this file type`; the r65/66 "88 samples on
     pipe" case needs a valid gsrt encoding byte).

6. Prior-row byte-stability spot checks (new code, prior flags):
   - --probe-ui-dec-hcom-r66  receipt == r66 recorded 023252189954Z  IDENTICAL
   - --probe-ui-preempt-both-r65 == r66 recorded 023301983754Z        IDENTICAL

## THE BIG FIND: concurrent-invocation corruption of ledger rows

- Author ledger run #1 (~05:16:30-05:18): row 06 = --probe-transport-dec-hcom-r67
  crashed, no receipt: `UNPARSED ... ValueError: Invalid number of FFT data
  points (0) specified.` — np.fft.rfft on a 0-sample decode inside measure().
- Author ledger run #2 (~05:19:33+): row 26 crashed:
  `... 'json', '.../artifacts/impact.wav')' returned non-zero exit status 1.`
  — ffprobe exit 1 on impact.wav mid-rewrite. Author quarantined it as
  ledger-r67-run2-defect.tsv and started run #3.
- Mechanism PROVEN: wave.open(wb) writes a valid header claiming 0 frames while
  frames are being flushed; a concurrent `sox wav -t f32 -` in that window
  decodes 0 samples, exit 0 -> /tmp/empty.wav demo: 0 bytes + ValueError
  identical to the row-06 text.
- Root cause: build_artifacts.py rebuilds corpus/artifacts/*.wav IN PLACE on
  every measure_audio.py invocation; non-atomic. Any two concurrent
  measure processes race. runs/ timestamps show interleaved transport receipts
  (051637, 051639) inside the author's row-02..05 window (051632-051638), and
  PID 2196572 `measure_audio.py --probe-ui-crest-46` (baseline seat replay)
  ran concurrently with the author's run_ledger PID 2157032/2225888.
- Impact: missing receipts (loud crash, caught by compare via exit/missing) OR
  silently-different receipts (partial wav -> short decode -> different
  duration/failures but valid JSON). The "102 prior rows byte-stable" claim is
  only defensible for a serially-executed ledger; this wave ran >=2 replays
  concurrently.
- Not introduced by the arm (SPECS measure loop is identical for every mode)
  but OBSERVED for the first time on tracked ledger rows this round.

## Remaining notes

- `error` regex `':\s*(.*)$` on last FAIL line: conflates `-`/path spelling
  deliberately (names scrubbed to `<input>` in stderr_tail). FAIL lines
  without a backtick-quoted name would fall back to whole-line — none in set.
- Verdict sig excludes stderr_tail (normalized tail) but includes error —
  the right granularity: die-position forks counted, path-spelling not.
- Mode semantics: uniform-fail invariant members (preempt_hcom) exit 0 —
  arm records verdicts not correctness; consistent.
- `input` labels: file=relative path, pipe/redir=`-`, fifo=basename —
  deterministic.
- git diff --check clean; ast.parse clean; 106/106 flags in sum() mutex list;
  r67 modes lead both mode-name and suffix chains.
- Author ledger: run_ledger.py asserts 112 modes = 102 prior + 10 new at rows
  2-11 (newest-first convention as r66).
