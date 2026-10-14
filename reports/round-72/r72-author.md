# audio round 72 — author (seat: author; **operator-substituted landing**, verified by this seat; host: devin)

> Provenance: the dispatched r72 author seat produced no scratch during the
> wave window (r72-adjudicator: "swe-2 seat produced no scratch — promoted
> boundary's verified scratch arm per convention"). The move was landed by
> the operator as commit `26baed1` (2026-10-14 14:27:07 UTC) and
> reviewer-folded as `f5d7faf` (14:38:20 UTC). This seat (dispatched
> godspeed author) self-verified the landed arm end-to-end — fresh flag
> run, full 122-mode ledger, cross-decoder lattice re-derived from
> committed receipts — and authors this report. No tracked file modified
> by this seat; no git mutations.

## Declared move (verbatim)

Add `--probe-sndfile-transport-r72` mirroring the r71 ffprobe arm:
sndfile-info detection + a decode leg (sf_read via the frontier seat's
ctypes harness pattern). Receipt family `sndfile_*_r72_probe` keyed per
member x transport. Claim to test: the 3-decoder verdict lattice
partitions members into distinct decoder-coverage classes (sox-only:
txw-seekable/.f32-named; sndfile-only: .snd-named; ffmpeg superset on
detect). Insertion-only; prior rows byte-stable.

## Landed changes (`corpus/fixtures/measure_audio.py`; refs at HEAD `f5d7faf`)

- `:4` `import ctypes`; `:735` `TRANSPORT_R72_MEMBERS = TRANSPORT_R71_MEMBERS`
  (the canonical 9: r69's five identical-byte suffix members, the r68
  post-table/txw pair, dec_act/dec_hcom).
- `:750` lazy `_SNDFILE = ctypes.CDLL("libsndfile.so.1")` under try/except
  (reviewer-fold D1: a libsndfile-less host no longer kills every mode at
  import; legs then record `blocked: libsndfile unavailable on host`).
- `:784` `_sndfile_format_names()` — SFC_GET_FORMAT_MAJOR/SUBTYPE enum
  (the frontier seat's name resolution: `0x00040010` → `RAW (header-less)/U-Law`).
- `:805` `_sndfile_verdict()` — SF_INFO fields + `sf_format_check` +
  decode leg = one `sf_readf_short` drain, 65536-frame cap (equal to a
  full drain on this corpus: largest member reads 500 frames; doc states
  the cap honestly, not a proof of drain semantics past it).
- `:834` `_sndfile_leg()` — the 4 transports at the API boundary:
  `sf_open` for named {file, fifo_path}; `sf_open_fd` for anonymous
  {stdin_pipe via `os.pipe`, redirected_fd via `os.open`} — the frontier
  harness pattern (a `/dev/stdin` spelling would be a *named* open).
  Each leg bounded by `SIGALRM`/`setitimer` 15 s (reuses
  `TRANSPORT_R71_ARM_TIMEOUT_S`); fifo arm gets a per-leg fifo + writer
  thread + `reap_fifo_orphans` (r71 convention).
- `:908` `sndfile_transport_entry()` — per-arm verdict groups keyed on
  `(format_name, read_frames, error)` + `transport_fork` pin +
  `sndfile_info_cli` block (sndfile-info on the file arm: exit,
  format_hex, frames_field, reason — parsed scalars only, exit 0 even on
  reject honored as text-verdict).
- `:1130` flag, `:1133` mode-exclusivity sum, `:1353` arm emitting
  `sndfile_<member>_r72_probe` × 9, `:1819` mode, `:1839` receipt suffix
  `-sndfile-transport-r72`.
- Insertion-only: `git diff c079aba..26baed1` on the fixture = +239/-3;
  the 3 edited lines are the sum/mode/suffix chains, each extended by one
  alternative — no prior-mode code path touched (verified behaviorally
  below, not just by construction).

## Self-verify (all commands run from `~/Projects/shokunin/audio-shokunin`)

```sh
python3 corpus/fixtures/measure_audio.py --probe-sndfile-transport-r72
# exit 1 (the .snd fork is pinned as a failure line, r67 convention)
# receipt corpus/live/runs/20261014T142954167521Z-sndfile-transport-r72/measurements.json
#   sha256 f7faaedb375e6c01f00402d472c5b20dbca6a583a88a7628731e8eac338d032e
#   — byte-identical to all 8 sndfile-transport-r72 receipts in runs/
#     (sha256sum | sort -u -> single hash), spanning fixture versions
#     26baed1 -> f5d7faf -> current worktree; re-run post-fold at
#     14:50:15Z produced the identical receipt again.

python3 corpus/live/r72-author/run_ledger.py        # 122 modes, ~6.3 min
# ledger-r72.tsv: exits 50x0 + 72x1 (the +1 vs r71's 71 is the new
# mode's own fork pin). Window 14:32:50Z -> 14:39:10Z.

python3 corpus/live/r72-author/compare_receipts.py  # exit 0
# matched+identical: 122 / mismatches: 0 — every shared-mode receipt
# byte-identical to the newest prior receipt of the same mode; exit
# codes identical to the r71 ledger. Prior rows byte-stable CONFIRMED.
```

Caveat disclosed honestly: the ledger straddled the `50f55eb` (r71
`_tail` ASLR-tag strip) and `f5d7faf` (lazy-load fold) commits — every
row still matched its prior receipt, so neither commit changed emitted
bytes on this corpus (the `_tail` strip is inert where no ` @ 0x…`
module tag occurs; the fold's lazy load is behavior-neutral on a host
with libsndfile). Spot re-runs under the current worktree confirm:
`normal` → `8e8cdad6…` (all -normal receipts identical),
`--probe-transport-extsuffix-snd-r69` → `80f6d64b…` = r71-ledger receipt.

## Measured result — libsndfile 1.2.2 on 9 members x 4 transports

Verdicts field-identical to the frontier matrix
(`corpus/live/frontier-sndfile/runs/sndfile-matrix.json`) on all 36 cells
— and to the boundary seat's independent harness (36/36):

| member | file | stdin_pipe | redirected_fd | fifo_path | fork |
|---|---|---|---|---|---|
| dec_act | WAV/PCM16 278 | = | = | = | no |
| dec_hcom | WAV/PCM16 278 | = | = | = | no |
| posttable_nomatch | REJ `Format not recognised.` | = | = | = | no |
| txw_piperefuse | REJ `unimplemented format` | = | = | = | no |
| extsuffix_{wav,bin,txw,f32} | REJ `Format not recognised.` | = | = | = | no |
| extsuffix_snd | RAW/U-Law 500 | REJ | REJ | RAW/U-Law 500 | **yes** |

The single fork is the name axis: `{file, fifo_path}` (basename visible
to `sf_open`) vs `{stdin_pipe, redirected_fd}` (anonymous `sf_open_fd`) —
the same partition as sox's ext-gated sndr CHECK row, by a different
mechanism (post-sniff extension fallback, raw-family only). The fifo
arm's `frames` reads `INT64_MAX` (unknown length) with `read_frames`
still 500 — recorded verbatim, deliberately excluded from the verdict
signature (it is a container field, not a verdict; boundary measured the
same). txw carries the third verdict tier: `File contains data in an
unimplemented format.` — magic recognized, no reader compiled — vs
`Format not recognised.` for true no-match.

## Claim adjudication (independent re-derivation, this seat)

`python3 corpus/live/r72-author/lattice_extract.py` (exit 0) rebuilt the
3-decoder lattice from committed receipts — sox: newest
`transport_*_r6{7,8,9}` receipts; ffmpeg: `*-ffprobe-transport-r71`
(`578cad95…`); sndfile: this run's `f7faaedb…` receipt. Acceptance rule:
sox `exit 0 & samples_read>0`; ffmpeg `ffmpeg_exit==0`; sndfile
`read_frames>0`. Arm vectors (f=ile, p=ipe, r=edirected, q=fifo):

```
member            sox    ffmpeg  sndfile      class
dec_act           Y...   YYYY    YYYY         all-3 (sox file-only: bridge)
dec_hcom          YYYY   YYYY    YYYY         all-3, all-arms
txw_piperefuse    Y.Y.   ....    ....         sox-only, seekable arms
extsuffix_f32     Y..Y   ....    ....         sox-only, named arms
extsuffix_snd     Y..Y   ....    Y..Y         sox + sndfile, named arms
posttable + ext_{wav,bin,txw}  all ....       reject-all x4
```

- "distinct decoder-coverage classes" — **CONFIRMED**: 4 member-level
  classes, 6 arm-qualified classes; no decoder's partition equals
  another's.
- "sox-only: txw-seekable/.f32-named" — **CONFIRMED** exactly (4 cells).
- "sndfile-only: .snd-named" — **FALSIFIED as stated**: sox accepts the
  same member on the same named arms (det `sndr`, 504 samples); the
  `(F,F,T)` sndfile-only class is **empty** on this corpus. What is
  sndfile-unique is (a) the fallback mechanism and (b) the txw
  recognized-then-refused verdict tier.
- "ffmpeg superset on detect" — **FALSIFIED**: acceptance cells are sox
  11 > sndfile 10 > ffmpeg 8 of 36 — ffmpeg is the strictest detector on
  this corpus. Only narrow true reading: on the co-accepted members
  (dec_act, dec_hcom) ffmpeg's labels {wav, hcom} strictly refine
  sndfile's single {WAV/PCM16}.

Matches the adjudicator's ADMIT-with-correction and the critic/boundary/
scribe/verifier tables cell-for-cell.

## Evidence

- Receipt: `corpus/live/runs/20261014T142954167521Z-sndfile-transport-r72/measurements.json`
  (and 7 siblings incl. post-fold `20261014T145015189920Z`), all sha256
  `f7faaedb…`; exit 1 by fork-pin convention.
- Ledger: `corpus/live/r72-author/ledger-r72.tsv` (122 rows),
  `run_ledger.py`, `compare_receipts.py` (122 identical / 0 mismatch /
  exit 0), `lattice_extract.py` (the table above), `ledger-stderr.log`.
- Fixture refs at `f5d7faf`: `measure_audio.py:4,735,750,784,801,805,
  834,908,1130,1133,1353,1819,1839`.

## Remaining risks / unknowns

- In-process ctypes legs trade the r71 subprocess+timeout convention for
  a `SIGALRM` bound — a libsndfile hard crash (not a hang) would kill the
  whole measurement process; none observed on this corpus. SIGALRM is
  POSIX/main-thread only — fine for this lane's Linux host.
- `_sndfile_verdict` reads at most 65536 frames in one call; equal to a
  full drain here (max member = 500) but a cap, not a drain proof.
- `sndfile_info_cli` records the file arm only. The committed comment
  "Anonymous arms have no honest CLI arm" is imprecise — I measured
  `sndfile-info -` reading anonymous fd 0 correctly (`cat member |
  sndfile-info -` → same verdicts as the `sf_open_fd` arms; `sndfile-info
  - < member` → Seekable TRUE). A `-` CLI arm exists; it was simply not
  needed — it adds no coverage over `sf_open_fd`. Doc nuance, not a
  defect.
- Host-bound: libsndfile 1.2.2-4 format set is compile-time; a build
  with HCOM/TXW readers would shift the txw row.
- The r73 consumer-arm code is present in the worktree (uncommitted,
  another seat's in-flight work) — verified not to alter any r72/prior
  receipt byte.
