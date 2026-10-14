# R72 reviewer — third decoder (libsndfile 1.2.2): landed arm reviewed, 36/36 cells independently reproduced, 8/8 receipts byte-identical, insertion-only confirmed; 7 findings, none verdict-breaking

Seat: **reviewer** (leaf, report-only). Wave `shokunin-train-20261101-w11`, round 72, lane audio.
Repo `/home/vgpnk/Projects/shokunin/audio-shokunin`. Host: devin — libsndfile **1.2.2**,
SoX_ng v14.8.0.1, ffmpeg/ffprobe n9.0.1, CPython 3.14. Observation window **14:17–14:45 UTC**.
Write scope honoured: this report + `corpus/live/r72-reviewer/` scratch. The fixture's own
receipts under `corpus/live/runs/` are the *fixture's* output (same convention the r71
verifier used, `reports/round-71/r71-verifier.md:19-24`); every file I derived lives in the
scratch dir.

## 0. The diff under review (exact)

```
git diff c079aba 26baed1 -- corpus/fixtures/measure_audio.py   # 236 insertions, 3 deletions
```

- The **3 deletions are exactly** the replaced mutual-exclusion-guard line, the `mode =`
  line and the `suffix =` line. Everything else is additive → **insertion-only confirmed
  structurally**, not just by receipt comparison.
- Landed arm: `--probe-sndfile-transport-r72` (`measure_audio.py:1103`), guard
  (`:1106`, now 116 flags), dispatch (`:1326-1336`), `mode` (`:1792`), `suffix` (`:1812`),
  ctypes bindings + legs (`:4`, `:735-889`), entry builder `sndfile_transport_entry` (`:892`).
- Receipt family `sndfile_{member}_r72_probe`, 9 members × 4 transports (`:1335`).
- Landing context: author = **operator-substituted** (`reports/round-72/r72-adjudicator.md`);
  no `reports/round-72/r72-author.md` exists. The round's claim text lives in the fixture
  comment (`measure_audio.py:1327-1333`), the commit message and the adjudicator report.
- **Tree movement during review (disclosed).** After the r72 landing the tree advanced one
  commit: `50f55eb` "r71 fix: strip ffmpeg ASLR module tags in `_tail` normalizer"
  (11:33:33 local) adds a single line at `measure_audio.py:652`, *above* the r72 block.
  `git diff 26baed1 HEAD -- corpus/fixtures/measure_audio.py` is **exactly that one line**, so
  the arm I reviewed is byte-identical to HEAD; **all line numbers below are HEAD
  (`50f55eb`) numbering** (+1 vs `26baed1` below line 652). I re-ran the affected modes after
  the edit: `--probe-ffprobe-transport-r71` → `578cad95…` and `--probe-sndfile-transport-r72`
  → `f7faaedb…`, both byte-identical to their pre-edit runs, so the edit is inert for this
  round's rows. Uncommitted in-flight edits by sibling seats remain in
  `corpus/live/r72-baseline/measure-env/…` and `corpus/live/r72-verifier/lattice.json`
  (outside the arm).

## 1. Independent reproduction (my own measurement path, not the frontier harness)

I wrote my own ctypes harness (`probe_sndfile_r72.py`, sha256 `b7ec38ab…`) **before** the arm
landed and ran the 9-member × 4-arm matrix (`sndfile-matrix.json`, `c06d3215…`).

- **36/36 cells agree** with the landed receipt — verdict, `read_frames`, `frames`, and the
  exact `error` string (`compare_r72_receipt.py` → `cells=36 agree=36 diff=0`).
- **Every r72 receipt on disk is byte-identical (8/8, one unique sha256)**:
  `f7faaedb375e6c01f00402d472c5b20dbca6a583a88a7628731e8eac338d032e` for the 3
  author-tracked runs (`…142618906524Z`, `…142634507936Z`, `…142733592435Z`), the verifier's
  run (`…142954167521Z`), another seat's run (`…143300250668Z`) and my three
  (`…142824524743Z`, `…142841935923Z` pre-`50f55eb`; `…143409279922Z` post-`50f55eb`) —
  determinism across seats and across the mid-review ASLR commit.
- **Exactly one transport fork**: `extsuffix_snd` `{file,fifo_path}`=RAW|U-Law/500 vs
  `{stdin_pipe,redirected_fd}`=`Format not recognised.`; the other 8 members are
  single-group. My harness produced the same fork and the same wording.
- **Same-identity rerouting vs the r71 arm**: identical member set (9), identical
  `named`/`seekable` flags on all 36 cells, identical `transport_protocol`
  (`15 s`, `fifo_writer_hold_s 1.0`, one-shot feed) — checked programmatically, 0 mismatches.

Measured lattice (my numbers; sox from committed r67/r68/r69 receipts, ffmpeg from the r71
receipt, libsndfile from my harness — full table `lattice.tsv`, classes `lattice-classes.txt`):

| class | cells | members |
|---|---|---|
| all three accept | 5 | dec_act/file, dec_hcom ×4 |
| ffmpeg∩sndfile (sox rejects pipes) | 3 | dec_act {stdin_pipe, redirected_fd, fifo_path} |
| sox∩sndfile (ffmpeg rejects) | 2 | extsuffix_snd {file, fifo_path} |
| **sox-only** | 4 | txw_piperefuse {file, redirected_fd}, extsuffix_f32 {file, fifo_path} |
| ffmpeg-only | **0** | — |
| sndfile-only | **0** | — |
| all reject | 22 | posttable ×4, extsuffix_{wav,bin,txw} ×4 each, txw_piperefuse pipes ×2, f32 anon ×2, snd anon ×2 |

Acceptance-cell counts: **sox 11, libsndfile 10, ffmpeg 8**.

## 2. Findings by severity

### D1 — medium-low: the new arm made libsndfile a hard *import-time* dependency of every mode

`_SNDFILE = ctypes.CDLL("libsndfile.so.1")` sits at module scope (`measure_audio.py:749`), so
the library is loaded on `import` — before any flag dispatch. Measured with a PYTHONPATH stub
that makes `ctypes.CDLL("libsndfile.so.1")` raise (`ldstub/sitecustomize.py`, `9f4d780b…`):

```
PYTHONPATH=corpus/live/r72-reviewer/ldstub python3 corpus/fixtures/measure_audio.py --probe-transport-dec-act-r67
  File "corpus/fixtures/measure_audio.py", line 748, in <module>      # verbatim run output, 26baed1 numbering (:749 at HEAD)
    _SNDFILE = ctypes.CDLL("libsndfile.so.1")
OSError: stub: libsndfile.so.1 not present on this host        # exit 1
# same failure for the bare `normal` mode
```

The pre-change fixture has **0** `ctypes|sndfile` tokens (`git show c079aba:… | grep -c` → 0),
so the coupling is new. Impact on this host: none (library present; 8/8 identical receipts).
Impact on the contract: every prior caller — `normal`, all 116 probe modes, the wave ledger —
now fails at import on a host without libsndfile, and the receipt records no environment
precondition. Recommendation: import inside the r72 branch (or `try/except` and raise only
when `args.probe_sndfile_transport_r72` is used).

### D2 — low: "full drain" is a single `sf_readf_short` call

`_sndfile_verdict` docstring and `sndfile_transport_entry:894` say "full drain"; the code does
**one** call, `sf_readf_short(snd, buf, 65536)` (`:810`). Measured on this corpus the two are
equal — single call vs loop-to-EOF: dec_act 278/278, dec_hcom 278/278, extsuffix_snd
500/500 — so no number in the round is affected. But for a member longer than 65536 frames
the recorded `read_frames` would silently become a partial read. Note the *other* r72 leg in
this commit (D3) loops to EOF, so the two implementations of the same arm disagree in decode
semantics. Recommendation: loop until 0, or rename the field.

### D3 — low (provenance / one-canonical-runtime): a second copy of the fixture is tracked, and the working tree is turning it into a divergent r72 implementation

- **Committed at HEAD:** `corpus/live/r72-baseline/measure-env/corpus/fixtures/measure_audio.py`
  = sha256 `33f0a57764f38d5ec372ff2c19729593fe5e2acfb4cfa2ff191294c2da8e4c6c` = **exactly the
  pre-r72 canonical fixture** (`git show c079aba:corpus/fixtures/measure_audio.py`), shipped
  alongside its own `sndfile_leg_r72.py` (`47bdc6e5…`, tracked).
- **Working tree (uncommitted, mtime 11:30:14):** that replica fixture is now a **variant** r72
  implementation (`0cefb1d8…`, `git diff --stat` = 261 insertions / 3 deletions) which shells
  out to `sndfile_leg_r72.py`, and whose comment block states the **pre-critic** claim — "a
  libsndfile-only-vs-ffmpeg acceptance (.snd on named arms …), ffmpeg as the transport-invariant
  superset on detect" — i.e. the two clauses the round falsified.
- I ran the variant leg directly (stdout only, nothing written into the tree): all 9 file-arm
  verdicts and numbers equal the canonical receipt (`replica-leg-check.txt`), so it is not
  numerically divergent on this corpus. But two implementations of the same arm now exist, and
  the r69 precedent (`corpus/live/r69-verifier/run_ledger_v.py:10` points `MEASURE` at a
  `measure-env` copy) is exactly how a replica gets executed as if it were canonical.
- Recommendation: keep one authority for the r72 arm (the fixture); if the replica is kept for
  env proof, keep it byte-identical to the file it claims to copy.

### D4 — low: the env-proof is invalidated by the in-flight replica edit (it was accurate at commit time)

`corpus/live/r72-baseline/env-proofs.txt:2` claims
`EQUAL fixtures/measure_audio.py 33f0a57764f38d5ec372ff2c19729593fe5e2acfb4cfa2ff191294c2da8e4c6c`.
Checked line by line: **at HEAD 28/28 lines hold** — the proof was correct when committed —
but **in the working tree 27/28 hold**, the fixture line failing because the uncommitted replica
edit replaced that file (`0cefb1d8…`). Honest for the commit it ships with, stale for the
current tree, and it will silently become wrong if the in-flight edit lands without
regenerating the proof.

### D5 — low (hygiene): the replica escapes the snapshot-ignore net

`corpus/live/r72-baseline/measure-env/` is 30 tracked files / 2.8 MB, including
`…/__pycache__/probe_sndfile_r72.cpython-314.pyc`, and `git check-ignore` says
**NOT IGNORED**. `corpus/.gitignore` covers `live/*/{tree,frozen}/`, `live/*/{head,snapshot,base}/`,
`live/*/*extract*/` and `live/**/*tree*/` (xsentinel w7-F1 / w8-F4 / w9 classes) — `measure-env`
is outside every pattern. Bounded, but the same side-channel class the sentinel closed for
other names. Recommendation: extend the pattern (`live/*/*env*/`) or untrack the replica.

### D6 — low (claim precision): "measured 4-class partition" is not reproducible at one granularity

My numbers (`lattice_classes.py`):

- arm-qualified **member** classes: **6** (dec_hcom all/all; dec_act mixed; txw sox-only-seekable;
  f32 sox-only-named; snd sox∩sndfile-named; the four none-members).
- cell acceptance-signature classes over the 36 cells: **7** (sox-only 4, ffmpeg∩sndfile 3,
  sox∩sndfile 2, all-three 5, none 22, plus the two **empty** private classes).
- **private** (single-decoder) cells: sox **4**, ffmpeg **0**, sndfile **0**.

So "distinct decoder-coverage classes" holds only in the weak sense (no decoder's acceptance
set contains another's: 11 / 10 / 8 with incomparable overlaps). The only *sndfile-unique
acceptance* in this repo is on a member that is **not** in the canonical 9: a `.au`-named copy
of the same 512 bytes — I measured it independently: sox exit 2
(`can't find Sun/NeXT/DEC identifier`), ffprobe/ffmpeg exit 1 (`Invalid data`), libsndfile
`RAW (header-less)/U-Law`, 500 decoded frames (`au-check/member.au`). sndfile's r72-unique
contributions on the canonical corpus are the **verdict tier** (`unimplemented format`) and
the **fallback mechanism**, not an exclusive acceptance class — which the adjudicator report
records correctly in prose; only the "4-class" label is loose. The untracked `.au` probe is
seat scratch, so it cannot carry the round's claim (the critic's recommendation 3 — add it in
a later, all-three-arm round — is the right home for it).

### D7 — low (cosmetic consistency)

- `decoder` = `"libsndfile libsndfile-1.2.2"` (double prefix, `:933-934`); the critic asked for
  `decoder: "libsndfile"` + `sf_version_string` separately.
- The same format value is rendered two ways inside one entry: ctypes `hex(info.format)` =
  `"0x40010"` vs the CLI string `"0x00040010"` (`:919`); a reader diffing them sees a
  non-divergence.
- `named`/`seekable` are hard-coded literals (`:902-905`) instead of being derived from
  `TRANSPORT_R67_ARMS` as the r67/r71 arms do — duplicated truth source (values verified
  correct on all 36 cells).

## 3. Error paths and contracts I verified as sound

- **Bounded fifo leg, honest verdict.** Driving the landed `_sndfile_leg("file", <fifo with no
  writer>, …)` (`fifo_timeout_test.py`) returns after **15.00 s** with
  `{"error": "blocked: no verdict within 15 s"}` — the SIGALRM bound fires through the
  blocking `sf_open`, and the arm cannot hang a receipt. (A bare `sf_open` on a writer-less
  fifo blocks indefinitely — measured, `boundary-probes.json` `C_fifo_no_writer`.)
- **Anonymous arms are the API boundary, not a path spelling.** `sf_open_fd` on a fresh
  pipe/file fd (`:839-858`), exactly as the critic required; `/dev/stdin` is not used.
  (I also measured that `/dev/stdin`/`-` happen to give the same verdict on these members,
  which is why the honest bound matters rather than the incidental agreement.)
- **The CLI leg cannot be mistaken for the decode verdict.** `sndfile-info` exits 0 on reject;
  the arm records it as an auxiliary field only, and I measured why: the CLI `Frames` line is
  the container estimate (512) against a 500-frame drain, and prints `unknown` on the fifo.
- **Replay-stable text.** No absolute/tmp path appears anywhere in the r72 receipt
  (`grep -o -E "(/tmp/[^\" ]*|/home/[^\" ]*)"` → empty); the CLI `reason` field is the last
  stdout line (`Format not recognised.` / `File contains data in an unimplemented format.`),
  not the path-bearing `File :`/`Error :` lines — the r71-D1 class is avoided.
- **Mutual exclusion.** `--probe-sndfile-transport-r72 --probe-ffprobe-transport-r71` →
  exit 2, `error: choose one probe mode`, and the new flag appears in the usage list.
- **Insertion-only / prior rows byte-stable (empirical, 5 modes, pre-change vs post-change):**

| mode | sha256 pre = post |
|---|---|
| `normal` | `8e8cdad6cc3c356d07c463498f4759b8d73e73935cf591d117732f09ffaffb1b` |
| `--probe-ffprobe-transport-r71` | `578cad954839885bfa81e62ccf369400adf27fc3b0f62db7b3f45f3927c4d96e` |
| `--probe-transport-extsuffix-snd-r69` | `80f6d64b0f959007ab361128c0f1461063f71e21e6e032f60176aeebc7eae8ba` |
| `--probe-transport-txw-piperefuse-r68` | `762aff12c5c512bfa3871afb519869a5ac2c473a7853e837b5afd2dd841f66dc` |
| `--probe-transport-dec-act-r67` | `195d755410c97d119356bd7dbdb5ed220425603887b97fd419cab95138aa9410` |

  The `normal` and r71 rows are additionally identical to their committed references
  (`…140849989520Z-normal`, `…141033155858Z-ffprobe-transport-r71`), so the r71 arm's own
  replay is the control the critic asked for.
- **The post-landing ASLR edit is inert for r71/r72** (re-run after `50f55eb`, §0): both
  receipts byte-identical. But the class it fixes is real and **three tracked receipts are
  already not byte-reproducible**: `…014008064525Z/…014058497253Z/…014257840421Z-ui-preempt-gsrt-r65`
  differ from a fresh run in **exactly one leaf** — `sox_stderr`, `[wav @ 0x559e1fb98e40] no
  'data' tag found` (tracked) vs `[wav] no 'data' tag found` (fresh). So the wave's
  "prior rows byte-stable" claim holds for receipts produced after the r71 normalization
  change, and the new commit prevents the class going forward; it cannot retroactively make
  those three tracked rows reproducible.

## 4. Prior-evidence corrections (independent)

- **`fa-sndfile.md:65` is wrong on one number**: it says extsuffix_f32 "decode **75**, exit 0";
  all 8 committed `transport-extsuffix-f32-r69` receipts read `samples_read: 128` on
  `file`/`fifo_path`, and `reports/round-69/r69-author.md:27` says 128. (Matches the scribe's
  F1 and the critic's note — three seats, same correction.)
- **The frontier's open case-sensitivity gap is closed**: the post-sniff fallback is
  **case-insensitive** — `.SND` on the identical no-magic bytes opens `RAW (header-less)/U-Law`,
  500 frames (`frontier-audit.json`).
- **The txw tier's onset is exactly 12 bytes** (LM8953 prefix ladder: 11 B → `Format not
  recognised.`, 12 B → `File contains data in an unimplemented format.`), independently
  reproducing the boundary seat's 12 B finding.
- Frontier rows reproduced in full: 26 format majors with **no TXW and no HCOM**; the
  fallback set `{.au,.snd → RAW|U-Law 500, .gsm → GSM 6.10 2560, .vox → VOX ADPCM 1024}`;
  content beats the fallback (RIFF named `.snd` → WAV/PCM16 278); `sndfile-info` exit 0 on
  reject; `sndfile-convert` exit 0/1; no `sndfile-convert-to-raw`.

## 5. Residual risk

1. **Unreplayed modes.** No r72 ledger exists (`ledger-r72.tsv` / `run_ledger.py`: none), so
   the wave's 121-mode byte-identity replay was not executed this round; the adjudicator's
   "byte-identity by insertion-only construction" is an inference. My 5-mode empirical subset
   plus the 236/3 diff shape is the evidence available; 116 modes remain unreplayed.
2. **Host-compiled format set.** The `unimplemented format` tier, the 12-byte onset and the
   four-extension fallback set are build properties of libsndfile 1.2.2-4 on Arch. The receipt
   pins `sf_version_string()` (good) but the claims are single-build claims.
3. **Two r72 legs, one corpus.** If a later round extends the member set past 65536 frames, the
   canonical single-call read (D2) and the replica's loop-to-EOF leg will disagree.
4. **Fork-as-failure convention.** The r72 mode exits 1 by design (the `.snd` fork is recorded
   as a failure, matching r67/r68/r69); a caller treating non-zero as "arm broken" would
   misread a correct receipt. Stated, not a defect.
5. **The tree is still moving.** HEAD advanced to `50f55eb` mid-review (r71 ASLR fix, inert for
   r71/r72 receipts — verified) and sibling seats hold uncommitted edits in
   `corpus/live/r72-baseline/measure-env/…` and `corpus/live/r72-verifier/lattice.json`. This
   review anchors on the r72 arm's code, which is byte-identical between `26baed1` and HEAD;
   any later change to `measure_audio.py` invalidates the receipt hashes above and needs a
   fresh replay.

## 6. Verification gaps (explicit)

- **No `lsp` device is available to this seat** — checked twice: the seat's toolset has no
  `lsp` tool, and the only MCP server exposed is `rea` (binary/browser reverse-engineering;
  its tool list contains no status/references/definition/diagnostics device). Caller/definition
  checks were therefore done by the **literal text-search fallback + execution**, explicitly
  **not** semantic proof: `grep` for the flag
  (`measure_audio.py` only; `build_artifacts.py` has 0 `sndfile` tokens — no member build
  needed, no forwarding line added), `grep` for `sndfile_` in `corpus/live/runs/*/measurements.json`
  (only the r72 runs), and `grep -rn resume` (0 hits → the seat-card `resume_continuity_v1`
  clause is **not applicable** to this lane; there is no resume/preflight path).
- I did not re-run the full 121-mode ledger (see residual risk 1) and did not verify the
  r72-baseline variant end-to-end (only its leg, file arm).
- I did not adjudicate; this is a recommendation. No git mutation was performed by this seat;
  no file outside my scope was written.

## 7. Commands / exits (as run)

```sh
cd ~/Projects/shokunin/audio-shokunin
git diff c079aba 26baed1 -- corpus/fixtures/measure_audio.py > corpus/live/r72-reviewer/r72-fixture.diff   # 236+/3-
python3 corpus/live/r72-reviewer/probe_sndfile_r72.py '{…9 members…}' > corpus/live/r72-reviewer/sndfile-matrix.json  # exit 0
python3 corpus/live/r72-reviewer/lattice_extract.py > corpus/live/r72-reviewer/lattice.tsv                # exit 0
python3 corpus/live/r72-reviewer/lattice_classes.py > corpus/live/r72-reviewer/lattice-classes.txt        # exit 0
python3 corpus/fixtures/measure_audio.py --probe-sndfile-transport-r72                                    # exit 1 (fork recorded)
#   receipt corpus/live/runs/20261014T142824524743Z-sndfile-transport-r72/measurements.json (f7faaedb…)
#   rerun → 20261014T142841935923Z-… : byte-identical
python3 corpus/live/r72-reviewer/compare_r72_receipt.py corpus/live/runs/20261014T142824524743Z-sndfile-transport-r72/measurements.json  # cells=36 agree=36 diff=0
python3 corpus/fixtures/measure_audio.py --probe-sndfile-transport-r72 --probe-ffprobe-transport-r71      # exit 2, "choose one probe mode"
PYTHONPATH=corpus/live/r72-reviewer/ldstub python3 corpus/fixtures/measure_audio.py --probe-transport-dec-act-r67  # exit 1, OSError at :748 (26baed1 numbering; :749 at HEAD)
timeout 60 python3 corpus/live/r72-reviewer/fifo_timeout_test.py   # elapsed_s=15.00, "blocked: no verdict within 15 s"
# prior-mode pre/post replay (5 modes, exit 0/1 as designed) → byte-identical, hashes in §3
# after HEAD moved to 50f55eb (ASLR edit): re-ran r71 + r72 + r65-gsrt
python3 corpus/fixtures/measure_audio.py --probe-ffprobe-transport-r71     # exit 0, 578cad95… (unchanged)
python3 corpus/fixtures/measure_audio.py --probe-sndfile-transport-r72     # exit 1, f7faaedb… (unchanged)
python3 corpus/fixtures/measure_audio.py --probe-ui-preempt-gsrt-r65       # exit 1; vs 3 tracked refs: 1 leaf differs (ASLR tag)
```

Artifacts + hashes: `corpus/live/r72-reviewer/evidence-manifest.txt`; harness
`probe_sndfile_r72.py` (`b7ec38ab…`), matrix (`c06d3215…`), lattice (`5d9cfc26…`/`ffb4d19c…`),
boundary probes (`a1c1a109…`/`d024137c…`), frontier audit (`3bbde043…`/`a86a6677…`),
receipt comparer (`92519340…`), timeout test (`2e3f812e…`), stub (`9f4d780b…`), diff
(`58808717…`). Canonical fixture: sha256 `515aabeb6aa49363caf8af49020f657365661a5c1000bf056643e2d12bb918dc`
at `26baed1` (the revision that produced every r72 receipt cited here) and
`2eb70bb1d7d1d494af46cde6a998503a4ee6768455b96a0a3a5c6924beea2267` at HEAD (`50f55eb`, same
arm + the one-line ASLR fix); replica copy at HEAD `33f0a577…`, replica working tree `0cefb1d8…`;
replica leg `47bdc6e5…`; env-proofs `d186a4df…`.

Provenance note: the landing commit `26baed1` swept part of this scratch dir into the tracked
tree (harness, matrix, lattice, boundary/frontier probes, comparer, pre-change run logs, two
`__pycache__` files). Those tracked copies are **unmodified** in the working tree
(`git status --porcelain corpus/live/r72-reviewer` shows only `??` entries for files created
after the commit), so every hash above identifies both the working and the tracked artifact.
The post-change runs, the stub, the timeout test, `au-check/` and the manifest itself are
untracked scratch.

**Seat stop.** Findings reported; no edit, no commit, no dispatch, no verdict claimed as
admission.
