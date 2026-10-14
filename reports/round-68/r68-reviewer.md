# R68 reviewer — audit of r67 committed state (`366fcc1` + `bd5e1fe`)

Seat: **reviewer** — audit-only; no tracked mutation performed or proposed. Host:
`sox` = SoX_ng **14.8.0.1** (`/usr/bin/sox -> sox_ng`, ffmpeg formats incl. `act`/`gsrt`/`hcom`/`txw`/`smp`
present in `sox --help`), ffmpeg/ffprobe **n9.0.1**, python **3.14.7** — identical toolchain to
the r67 record. Audited tree: canonical repo `/home/vgpnk/Projects/shokunin/audio-shokunin`
@ HEAD `bd5e1fe` (work commit `366fcc1`); on-disk `corpus/fixtures/measure_audio.py`
sha256 `a0b2ad6d…1d17f` = `git show HEAD:` byte-identical before **and** after my replay —
no in-flight author diff contaminated the audit window. Ledger re-run from the lane worktree
`~/Projects/prymeagnt/audio` so `.shokunin/audio` resolves through the symlink, matching
`run_ledger.py`'s invocation contract. Scratch: `corpus/live/r68-reviewer/`
(`r68rev_ledger.py`, `ledger-r68rev.tsv`, `ledger-r68rev-compare.txt`, `ledger-r68rev-stderr.log`).

**LSP note**: no `lsp` device answers this repo on this substrate (same as r64–r67 records);
definition/caller checks are text-grep + live-execution — the stronger evidence class here.

## Verdict summary

| audit item (per brief) | result |
|---|---|
| 112-row r67 ledger re-run on HEAD | **SURVIVES at the strongest level — full replay, not a spot subset**: 112/112 fresh receipts **byte-identical** to the committed r67 ledger receipts; exit sequence position-identical (49 exit-0 / 63 exit-1); 0 UNPARSED |
| 10 `--probe-transport-*-r67` modes | **SURVIVES** — exits `1,1,0,1,0,1,0,1,0,0` match committed rows 02–11; all 10 fresh receipts byte-identical |
| fork set = 5 gsrt/act members | **SURVIVES** — `preempt_act` (3-group: file=decode 3839 \| pipe+fifo=au-magic \| redir=EOF), `preempt_gsrt` (2-group: file+redir=EOF \| pipe+fifo=`invalid format for this file type`), `preempt_both` (identical shape, det=gsrt — first-match wins transport-stable), `dec_act` (3-group: file=decode 278 \| pipe+fifo=au-magic \| redir=EOF), `lengate_gsrt_25` (2-group: file+redir=EOF \| pipe+fifo=`invalid/missing file name in header`) |
| invariant set = 5 hcom/wav members | **SURVIVES** — `preempt_hcom` `bad compression type`×4, `dec_hcom` decode 9×4 (control), `lengate_gsrt_24` `fmt chunk not found`×4, `lengate_hcom_131` decode 43×4, `lengate_hcom_132` `premature EOF`×4 |
| detection invariance ("detection never forks") | **SURVIVES** — every member's `sox_detected_format` is a single-element set across all 4 arms; all forks are decode-stage |
| fifo linger determinism | **SURVIVES, extended** — fresh `transport-dec-act-r67` receipt sha256 = `195d755410c97d119356bd7dbdb5ed220425603887b97fd419cab95138aa9410`, identical to all **4** committed copies (0519Z author + 0535Z/0550Z + 0926Z reruns) → **5 independent byte-identical receipts** spanning ~4.5 h host time; `transport_protocol` = `{arm_timeout_s:10, fifo_writer_hold_s:1.0, fifo_feed:"one-shot write then writer lingers"}` uniform across all 10 committed receipts |
| prior-102 receipts byte-identical | **SURVIVES** — my 102 fresh prior-row receipts byte-identical to the r67 ledger receipts; the committed `compare_receipts.py` re-run on committed data → `102 prior-mode pairs checked, 0 mismatches` (exit 0), so my fresh priors chain byte-identically to r66's originals |
| additive-only tracked diff | **SURVIVES** — `366fcc1` modifies exactly `measure_audio.py` **+183/−3** and the disclosed `.pyc` regen; all other paths are additions (receipts + r67 scratch); `git show --name-status` shows only those two `M` entries |
| member fixtures | **SURVIVES** — all 10 `TRANSPORT_R67_MEMBERS` files present and clean; the 6 round-66 members sha256-match the r67-reviewer published digests verbatim (`325fb967`, `777b6764`, `e7db9976`, `ede4161b`, `6fd9f471`, `a1abdac4` prefixes) |
| mutual-exclusion sum +10 | **SURVIVES** — `measure_audio.py:418` sum includes all 10 `probe_transport_*_r67` flags; arm block `:604-632` and member table `:179-190` as reported |

**No drift found between committed claims and re-executed reality. Zero findings.**

## Evidence detail

- Fresh ledger: `corpus/live/r68-reviewer/ledger-r68rev.tsv` (112 rows); comparison in
  `ledger-r68rev-compare.txt` → `112 rows replayed; 112 receipts byte-identical …; 0 exit
  mismatches; 0 byte mismatches`. Exit-sequence `diff` vs committed TSV column 2: identical.
- Fresh transport receipts (rows 02–11):
  `runs/20261014T0953{19198093Z-preempt-act,21246270Z-preempt-gsrt,23297586Z-preempt-hcom,25342578Z-preempt-both,27394253Z-dec-hcom,29514874Z-dec-act,31563178Z-lengate-gsrt-24,33605199Z-lengate-gsrt-25,35667912Z-lengate-hcom-131,37726062Z-lengate-hcom-132}-r67/measurements.json`
  — each `cmp`-equal (byte-identical check via digest compare in the runner) to committed
  `runs/20261014T0522{09214985,11236923,13269799,15300985,17334521,19421143,21447023,23481879,25498972,27530025}Z-*` receipts.
- Verdict groups extracted from committed receipts (independent content check, not just
  bytes): fork members' `transport_verdict_groups` match the adjudicator table verbatim,
  including the two distinct non-seekable gsrt errors (`invalid format for this file type`
  on preempt_gsrt/preempt_both vs `invalid/missing file name in header` on lengate_gsrt_25)
  and the 3-group act split (`file` decodes / `redirected_fd` premature-EOF / both
  non-seekable arms au-magic). `transport_fork=true` exactly on the 5 claimed members.
- `stderr_tail` scrub verified in receipt shape: input names → `` `<input>' ``, ` @ 0x…]`
  ASLR tokens stripped — this is what makes the fifo path (tmpdir-embedded) byte-stable.
- Flags verified present: `measure_audio.py:407-416` (10 `--probe-transport-*-r67`),
  mode chain head `:1021`, helpers `:172-306` (`TRANSPORT_R67_ARMS` 2×2,
  `transport_error`, `transport_leg` 10 s bound, `transport_matrix` mkfifo+writer-thread,
  `transport_entry`).

## Concurrent-execution note (observation, not a finding)

r67 disclosed a non-atomic `build_artifacts.py` rebuild race: two of the author's three
ledger attempts logged exactly one UNPARSED row each (mid-write reads of
`corpus/artifacts/*.wav` while sibling seats rebuilt). During my full 112-row replay,
sibling r68 seat scratch dirs existed (`r68-baseline/-boundary/-critic/-scout/-scribe/`
untracked, observed post-run), yet my run produced **0 UNPARSED and 112/112
byte-identical receipts** — consistent with the r67 bound that the flake is a
*momentary mid-write read*, not a deterministic defect; serial-execution byte-stability
claim holds in this window. The disclosed residual stands unchanged for r68's own runs.

Post-audit `git status`: **0 tracked modifications**; untracked = my `r68-reviewer/`
scratch + `runs/20261014T0953*` receipts written by `measure_audio.py` by design +
pre-existing `r67-simplifier/head-tree/` and sibling `r68-*` seat dirs (not mine).

## Findings by severity

- **HIGH/MED/LOW defects against r67 committed state: none.** Every audited claim —
  full 112-row ledger, fork partition, detection invariance, fifo-linger determinism,
  prior-receipt byte-identity, additive-only diff — survives verbatim re-execution.

## Residual risk / verification gaps

- Byte-identity of my fresh receipts to committed receipts is a *re-execution* result
  (each row re-invokes live `sox`/`ffprobe` 4× per member + the full base measurement),
  so it simultaneously proves the harness deterministic and the verdicts reproducible
  on this host. It does not prove mechanism-level attributions (bridge re-open-by-name,
  pending-buffer poison) — those rest on r67-critic/scout strace evidence, which I did
  not re-run this round (not required by the brief; verdict-level claims are what the
  committed record asserts).
- `premature EOF` remains a verdict-level signature merging ≥3 mechanisms (r67 labrat
  disclosure); unaffected within-member grouping.
- Single host/toolchain: SoX_ng 14.8.0.1 USING_FFMPEG + ffmpeg n9.0.1; act-route claims
  vanish on ffmpeg-less builds (standing bound).
- The r68 declared move (post-table fallback for no-match members + txw/smp pipe-refusal
  member) is the author's in-flight diff — out of my audit scope; my audit window
  predates any tracked landing (`measure_audio.py` sha stable across it).

Leaf seat: no commits, no pushes, no tracked edits, no dispatches.
