# R71 boundary — direct ffmpeg on fifo needs NO writer-hold band (60/60 legs stable at every hold incl. 0); the detect-ok/decode-fail '-' split is a SoX artifact that `pipe:` does not reproduce (fd 0 is never lseek'd); truncation exposes a non-monotone hcom dead-zone (132–157 B) — two landed bookkeeping defects confirmed (already corrected in `77768fa`)

Seat: **boundary** — post-landing edge-probe of the r71 ffprobe transport
matrix (`--probe-ffprobe-transport-r71`, landed as `7b9e75d` 11:03 -03,
"operator-substituted author" per its message + `reports/round-71/r71-author.md`
provenance note). Host: `sox` SoX_ng 14.8.0.1, `ffmpeg`/`ffprobe` **n9.0.1**,
python 3.14.7, kernel 7.2.3-arch1-3. Scratch: `corpus/live/r71-boundary/`
(`edge_probes.py` + `edge_results_probe-{a,b,c}.json` — committed via
`5415115`). No `lsp` device exposed; checks by read + grep per fallback rule.

Repo state moved during the seat window (wave-10 was still landing):
`7b9e75d` author landing → `abfc6a0` adjudicator → `77768fa` **r71
corrections** (verifier D1–D3) → `5415115` report-last + seat scratch →
`6b46b7c` HEAD. All my probes ran on the committed `ffprobe_leg`
mechanics — the `77768fa` diff touches only stderr-tail normalization and
the mode/suffix selector chains, so leg behavior is identical in both
revisions; where the two revisions differ I say which one the evidence
binds to. `git status` is clean at report time; this seat wrote only the
scratch dir + this report (zero git mutations, zero tracked edits).

## Landed matrix verdict (as committed, all 9 members × 4 transports)

From the author's own ledger row-2 receipt
`corpus/live/runs/20261014T140306084044Z-normal/measurements.json`:

| member | ffprobe verdict (all 4 transports) | transport_fork |
|---|---|---|
| posttable_nomatch, txw_piperefuse | `format=null`, ffmpeg exit 183 `Invalid data` | no |
| dec_act | `format=wav score=99`, ffmpeg exit 0 | no |
| dec_hcom | `format=hcom score=100`, ffmpeg exit 0 | no |
| extsuffix_{wav,bin,txw,f32,snd} | `format=null`, ffmpeg exit 183 | no |

Zero transport forks — consistent with the declared claim (content
probing, no suffix axis). Note `.snd`: SoX's ext-gated `sndr` CHECK row
detection-forked on the name; ffprobe reports `null` on **every**
transport including named `file` — ffmpeg never sees a name to gate on.

## Probe A — fifo writer-hold sweep on dec_act: NO transition band for direct ffmpeg

Command: `python3 edge_probes.py probe-a` → calls the **landed**
`ffprobe_leg(None, "pair_dec_act.wav", feed=(tmp, name, data, hold))`
verbatim (per-subprocess fifo + `fifo_feed` + `reap_fifo_orphans`),
holds {0, 0.05, 0.2, 0.5, 1.0, 2.0} × 10 reps, oneshot feed.
Raw: `edge_results_probe-a.json`.

| hold s | signature | count | elapsed s/rep | orphans after |
|---|---|---|---|---|
| 0.0 | `(wav, 99, pexit 0, perr None, dexit 0, derr None)` | 10/10 | 0.047–0.051 | [] |
| 0.05 | same | 10/10 | 0.148–0.154 | [] |
| 0.2 | same | 10/10 | 0.449–0.454 | [] |
| 0.5 | same | 10/10 | 1.051–1.054 | [] |
| 1.0 | same | 10/10 | 2.051–2.054 | [] |
| 2.0 | same | 10/10 | 4.051–4.053 | [] |

**Distribution is flat at every hold including 0** — one signature, no
blocks, no orphans (orphan sweep = read-only `/proc/*/cmdline` scan for
the tmpdir path after each leg). Contrast with the SoX bridge on the
same member (r70 receipt `20261014T124153223493Z-fifo-hold-ladder-r70`):
oneshot h=0 → **10/10 `blocked: no verdict within 10 s`** (bridge open #2
deadlock), h≥0.05 → stable.

Mechanism: the SoX hold exists for the ffmpeg bridge's *second* open() of
the input; direct ffprobe/ffmpeg opens the fifo **once** and reads to
EOF — the writer's `open("wb")` rendezvous blocks until the reader
attaches, so hold can only cost wall-clock, never change a verdict.
elapsed ≈ `2×hold + ~0.05 s` (two serialized legs, each waiting out its
own writer's linger) confirms the linger is the only hold effect: the
pinned 1.0 s default costs ~2 s/member ≈ 18 s/r71-run of pure sleep.
**The r70 transition band does NOT transfer to this decoder** — the
env-overridable hold is verdict-irrelevant here (though harmless and
still honestly recorded via `transport_protocol`).

Flake record: three pre-commit author runs
(`…T135947…`, `…T140155…`, `…T140306…` `-normal` receipts) show fifo-path
`ffmpeg_exit=None, 'blocked: no verdict within 15 s'` on dec_act/dec_hcom/
extsuffix_snd — the shared-fifo r67-analog defect the author fixed with
per-subprocess fifos. `corpus/live/r71-simplifier/watch.log` shows the
fixture hash changing at 13:56:09Z/13:56:29Z/13:59:29Z/14:01:49Z between
those runs → in-flight revisions, not the committed mechanics. My 60-leg
sweep of the committed protocol produced zero blocks.

## Probe B — truncation/probesize: no probesize cliff for tracked members; a non-monotone hcom dead-zone at 132–157 B

Command: `python3 edge_probes.py probe-b` → file-transport `ffprobe …
format=format_name,probe_score` + `ffmpeg -v error -i <in> -f null -` on
truncated/oversized variants. Raw: `edge_results_probe-b.json`.

**Truncation cliffs (file:):**
- `dec_act` (600 B RIFF/WAVE): `null` below **44 B** → `wav/99, decode 0`
  at ≥44 B. The cliff is the full RIFF+WAVE+`fmt `+`data` header
  (offsets 36–43); decode never verifies the declared 556-B data length —
  44 B decodes "0 samples" silently, and odd residual sizes print
  `Invalid PCM packet, data has size N…` / `Decoding error` at `-v error`
  yet **still exit 0** (soft errors — a verdict SoX's samples-read field
  would have caught; ffmpeg's binary exit does not).
- `dec_hcom` (600 B, RIFF shell with `FSSD`@65 + `HCOM`@128):
  `null` <44 B → **`wav/99` at 44–131 B** → **`null` at 132–157 B** →
  **`hcom/100` at ≥158 B**. Fine grid 128–176 confirms the edges exactly
  (131=wav, 132=None, 157=None, 158=hcom). This is a *non-monotone*
  verdict: appending bytes (131→132) takes the member from
  detect+decode-ok to total rejection. Mechanism (inferred, consistent
  with all cells): once `HCOM`@128 is complete, hcom's probe claims the
  buffer at score 100 > wav's 99, but the hcom header isn't parseable
  until ~158 B — ffprobe commits to the top-scoring claimant and rejects
  rather than falling back. A dead-zone exists **only because the
  higher-scoring demuxer's signature completes before its header does**.
- `posttable_nomatch` (512 B no-match): `null` at every size — but the
  ffmpeg decode-exit *taxonomy* forks on truncation: exit 183
  `Invalid data` vs exit **187 `End of file`** at 256/300/400 B
  (a no-detection member whose error class still carries a size signal).

**probesize axis:** `-probesize` CLI floor is **32** — `-probesize 16`
rejects outright (`Value 16.000000 for parameter 'probesize' out of
range [32 - 9.2e18]`; ffprobe exit 1/no JSON, ffmpeg exit 222). Above
the floor detection is flat: dec_act `wav/99` and dec_hcom `hcom/100`
unchanged 32→5,000,000. The internal probe-buffer minimum (~2048 B)
already exceeds every tracked member (512–600 B; preempt 11,588 B), so
**no probesize cliff exists in the member set**. The cliff mechanism is
offset-absolute, not window-relative: `dec_hcom` prefixed with 3000 zero
bytes (signature pushed to 3065/3128) → `null` at *every* probesize
including 5 MB — hcom needs its markers at fixed buffer offsets, so
"signature inside the probe window" is necessary but not sufficient.
**Oversized**: `dec_act`+zeros to 6,000,000 B (> default 5 MB window) →
`wav/99, decode 0` on `file`, `stdin_pipe`, `redirected_fd` (fresh-fd),
`fifo_path` — magic-at-offset-0 means >probesize tails are irrelevant;
a true-size variant (RIFF/`data` size fields rewritten to cover the pad)
is identical. No verdict cliff at the 5 MB default.

## Probe C — `pipe:` on a redirected real-file fd: the SoX '-' split does NOT reproduce; fd 0 is never lseek'd

Command: `python3 edge_probes.py probe-c` + `strace -f -e trace=lseek
ffmpeg -v error -i pipe: -f null - < member`. Raw:
`edge_results_probe-c.json`.

| member | file | stdin_pipe | redirected_fd (fresh fd/leg) |
|---|---|---|---|
| posttable_nomatch | `null`/d183 | `null`/d183 | `null`/d183 |
| txw_piperefuse | `null`/d183 | `null`/d183 | `null`/d183 |
| extsuffix_wav | `null`/d183 | `null`/d183 | `null`/d183 |
| extsuffix_snd | `null`/d183 | `null`/d183 | `null`/d183 |
| dec_act | `wav/99`/d0 | `wav/99`/d0 | `wav/99`/d0 |
| dec_hcom | `hcom/100`/d0 | `hcom/100`/d0 | `hcom/100`/d0 |

**No detect-ok/decode-fail split anywhere** — the split is a SoX-side
property (name→extension dispatch + the `-` pending-buffer/seek gates);
under direct ffmpeg both anonymous arms equal the file arm on every
member. Seekability evidence: `strace` on `ffmpeg -i pipe: < real_file`
shows **zero `lseek(0,…)` calls** (only `lseek(3</etc/gnutls/config>)`
at init — same count as a true-pipe run) and `ffprobe …
format=…,size` reports `size=null` on `pipe:`-fd and `pipe:`-pipe alike
vs `"600"` on `file:`. The `pipe:` protocol treats fd 0 as a pure byte
stream; the {named × seekable} transport space collapses to a single
verdict axis for this decoder.

**The split shape does exist — as the harness artifact the landed code
documents.** Passing ONE shared fd to both legs (my
`redirected_fd_shared_fh` arm): dec_act → `wav/99` detect + **d183**
decode, dec_hcom → `hcom/100` + d183, and the 6 MB padded member →
`wav/99` + d183 (ffprobe consumes the ~5 MB probe window; the decode leg
inherits a mid-stream/EOF offset). That is a deterministic reproduction
of the "fh consumed by the ffprobe leg leaves ffmpeg reading EOF"
mechanism in `ffprobe_leg`'s docstring — the fresh-fd-per-subprocess fix
is verified correct, and the two anonymous arms are otherwise
equivalent. The pre-commit runs `…T140155…`/`…T140306…` show exactly
this 183 on their `redirected_fd` arm → pre-fix in-flight revisions.

## Landed-state defects (verified on `7b9e75d`; corrected in `77768fa`)

The verifier's D1/D2 are confirmed independently; `77768fa` (11:14 -03)
fixes both. Evidence as measured on the pinned commit:

- **D1 — mode/suffix wiring missing.** Committed blob grep:
  `probe-ffprobe-transport-r71` appears once (`:876` argparse) — absent
  from the `mode` and run-dir `suffix` chains. All four r71-era receipts
  + ledger `corpus/live/r70-author/ledger-r71.tsv` row 2 land at
  `runs/*-normal/measurements.json` with `"mode": "normal"`. Cosmetic
  but real: the r71 receipt is indistinguishable from a normal run by
  name/mode. Fixed in `77768fa` (chains now carry
  `"probe-ffprobe-transport-r71"`/`"-ffprobe-transport-r71"`).
- **D2 — fifo-arm stderr tail leaks the mkdtemp nonce → receipts not
  byte-stable.** Committed normalization strips only backticked spans;
  ffmpeg's `<path>: <msg>` diagnostic keeps the raw path, and the fifo
  arm's is `/tmp/transport-r71-XXXXXXXX/<name>`. Across the four r71-era
  runs `ffprobe_posttable_nomatch_r71_probe` entries are **4/4
  byte-distinct** (e.g. `…/txysbu33/…`, `…/rk275v9d/…`, `…/fmddvzde/…`,
  `…/nczyoo5h/…`); `extsuffix_*` same. Fixed in `77768fa` via `_tail()` +
  `replace(probe_arg, "<input>")`.
- **Residual latent nits (still on HEAD `6b46b7c`, no landed call site
  triggers them):** `ffprobe_leg(data=…, stdin_path=…)` builds
  `kw={"input":…}` then `stdin=fh` → `subprocess.run` raises
  `ValueError: stdin and input arguments may not both be used`
  (reproduced verbatim); and `run()` opens `fh = open(stdin_path)` before
  the `if fifodata is None` branch but closes it only inside that branch
  → **fd leak** if stdin_path+feed are ever combined. Robustness notes
  for future callers, not live defects.

## Other observations

- `corpus/live/r71-scout/ffprobe_matrix.json` is **empty** (`members: {}`)
  and a scout-spawned `ffmpeg -i /tmp/r71-scout-fifo-*/txw_piperefuse.wav`
  has been blocked on the dead fifo since 10:41 — the same shared-fifo
  deadlock class (scout ran its own protocol without per-subprocess
  fifos). ~77 stale ffmpeg processes from earlier rounds' probe dirs
  persist on this host (pre-existing; none from this seat — my orphan
  sweep read `/proc` without killing).
- The author's `run_ledger.py` finished all 121 rows; the updated
  `compare_receipts.py` reports **84 matched+identical**, 36 rows it
  labels r71-only, and **1 mismatch** — row 3 `fifo-hold-ladder-r70`,
  whose receipt carries the load-dependent transition band
  (`{oneshot 0.0→blocked}, {chunked 0.05→9/10 stable}` this run vs the
  r70-time `{0.05→stable}`) — divergence by design of that mode, not an
  r71 regression.
- The ledger itself straddled the 11:09 -03 fixture edit (row 2 ran
  pre-fix → `-normal` receipt; rows 3+ post-fix). Harmless to the
  byte-identity claim — the fix touches only r71 legs + r71 naming — but
  row 2's receipt path stays `*-normal` in the committed TSV.

## Answers to the brief's three questions

1. **Writer-hold band for ffmpeg-on-fifo?** No — 10/10 identical verdicts
   at every hold 0→2.0 on dec_act (60/60 stable). The band was the SoX
   bridge's open-#2 artifact; direct ffmpeg opens once and reads to EOF.
   The 1.0 s default only costs ~2×hold wall-clock.
2. **Verdict cliffs at probesize boundaries?** None for tracked members —
   CLI floor at 32 B, flat above (probe-window min ~2048 > members).
   Real cliffs are at the truncation floor: wav detect ≥44 B; dec_hcom's
   non-monotone `wav(44–131) → null(132–157) → hcom(≥158)` dead-zone;
   posttable's 183↔187 exit-taxonomy fork at 256–400 B; oversized 6 MB
   rides through flat on all four transports.
3. **`pipe:` on a real-file fd reproducing the detect-ok/decode-fail
   split?** No — verdicts identical to `stdin_pipe` on posttable,
   txw_piperefuse, extsuffix_wav, extsuffix_snd (all `null`/183) and on
   dec_act/dec_hcom (detect+decode ok). fd 0 is never lseek'd; the split
   exists only as the shared-fd *harness* artifact (deterministically
   reproduced: detect-ok + d183), which the landed fresh-fd fix already
   documents and neutralizes.

## Blockers / remaining risks

- None blocking. Residual: the four r71-era receipts are pre-correction
  revisions — the committed-code flake rate for the fifo arm is bounded
  by my 60/60 clean sweep but not exhausted (10 reps/hold on one member,
  one host, while a 121-row ledger ran concurrently).
