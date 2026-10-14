# R64 verifier — NAMED NON-AUTHOR replay of the 92-command ledger + boundary-pair discriminators

Seat: verifier (did NOT author r64 — independent replay on the committed state).
Committed work under test: `4c12342` on `~/Projects/shokunin/audio-shokunin` (HEAD at
verify time); worktree `~/Projects/prymeagnt/audio`, `.shokunin/audio` symlink → canonical.
Host toolchain identical to author's: SoX_ng v14.8.0.1, ffmpeg/ffprobe n9.0.1, python 3.14.7.
Scratch: `corpus/live/r64-verifier/` (replay_ledger.py, ledger-r64-verifier.tsv,
replay.stderr.log, runs-before.txt, status-before.txt, status-after.txt).
No commits, no tracked edits, no subagents.

## Claim 1 — 92-command serial replay → 44 exit0 / 48 exit1, prior-86 receipts byte-identical: **AGREE**

Reconstructed the mode list independently from `measure_audio.py`'s argparse block and
confirmed it equals `r64-author/run_ledger.py`'s MODES verbatim (92 entries: r63's 86 in
order + the six `--probe-ui-extensible-valid-{8,9,24,25,56,57}-r64` flags newest-first at
positions 2–7). My runner `corpus/live/r64-verifier/replay_ledger.py` ran all 92 serially
from the worktree root (`python3 .shokunin/audio/corpus/fixtures/measure_audio.py <flag>`),
writing `ledger-r64-verifier.tsv` (idx \t exit \t receipt \t failsum).

- Exit tally: `awk -F'\t' '{c[$2]++}'` → **exit 0: 44, exit 1: 48** — exactly as claimed.
- Exit sequence vs committed `r64-author/ledger-r64.tsv` col 2: `diff` → empty,
  **position-identical** (all 92).
- Failure summaries vs committed col 4: `diff` → empty, **verbatim identical** (all 92,
  including the six new rows' gate lists and row 87's eight-probe invalid block).
- Prior-86 mapping (my rows {1}∪{8..92} vs the 86 committed r63 receipts listed in
  `corpus/live/r64-reviewer/r63-receipt-paths.txt` — all 86 present and committed):
  `cmp -s` per pair → **86 byte-identical, 0 differ**.
- Prior-86 vs `r63-author/ledger-r63.tsv` directly: 0 exit mismatches, 0 failsum
  mismatches across the 86 aligned rows.
- Bonus determinism check: all **6/6 new-mode receipts byte-identical to the author's
  committed receipts** (rows 02–07 vs `r64-author/ledger-r64.tsv` col 3 paths).

(Method note: an early compare passed relative reference paths from the wrong cwd and
reported 86/86 diffs — a harness artifact, not data; rerun with absolute paths gave the
86/86 identity above.)

## Claim 2 — step-map pair discriminators on the committed tree: **AGREE**

Committed files `corpus/live/round-64/pair_valid_{8,9,24,25,56,57}.wav` (all 11,588 B;
SHA-256 all six match the author's published digests verbatim — e.g. v8 `bc9878f7…a1927`,
v57 `aa520464…fd94`).

- Sole-diff check: `cmp -l pair_valid_<v>.wav ../round-63/pair_route_84.wav` → exactly one
  line each, 1-based offset **39** (file byte 38 = wValidBitsPerSample low byte), member
  values 010/011/030/031/070/071 octal vs 021 (route_84's valid=17). Byte 39 stays 0x00.
- `xxd -s 256 -l 1` → **0x84 on all six** (act-route pin holds).
- Direct probes (mine, not receipts): `ffprobe stream=codec_name,bits_per_sample`,
  default-route `sox -V6 <f> -n stat` (all six detect `` `act' `` / `(ffmpeg)`), and
  forced-native `sox -t wav <f> -n stat`:

| member | ffprobe codec | bridge samples | native `-t wav` |
|---|---|---|---:|---|
| v8 | pcm_u8/8 | 11,520 (exit 0) | 5,760 exit 0 |
| v9 | pcm_s16le/16 | 5,760 (exit 0) | 5,760 exit 0 |
| v24 | pcm_s24le/24 | 3,839 (exit 0) | exit 2 `number of valid bits exceeds the number of bits per sample` |
| v25 | pcm_s32le/32 | 2,880 (exit 0) | exit 2 same |
| v56 | `unknown`/0 (no codec) | exit 2 `premature EOF` | exit 2 same |
| v57 | pcm_s64le/64 | 1,440 (exit 0) | exit 2 same |

Both 8|9 members native-decode 5,760 — the boundary is bridge-only, as claimed. My fresh
receipts (rows 02–07) record the same fields: v56's entry is the decode-failure shape
(`sox_exit_code: 2`, stderr `premature EOF`, `decode: default SoX route rejected input`),
v9 is the pair's sole exit-0 member; v25 fails only format+duration (decodes inside the
level/centroid bands) — failure-class split confirmed.

## Claim 3 — envelope-gate precondition (non-0xFFFE tag + valid-bits set does NOT follow the map): **AGREE**

Independent re-measure of the critic's committed scratch variants (`corpus/live/r64-critic/var/`),
each carrying byte-38=0x11 (valid=17, which under the map predicts pcm_s24le/3,839):

- `A2_tag0001_pcm.wav` (wFormatTag 0x0001): ffprobe → **pcm_s16le/16**, sox act route →
  **5,760** — the "valid" bytes are inert cbSize extradata; the map does not apply.
- `A2_tag0006_alaw.wav` (tag 0x0006): ffprobe → **pcm_alaw/8**, sox → **11,520** — a
  different codec family entirely; valid-bits never consulted.
- Bonus gate leg: `A3_cb21.wav` (cbSize 21 < 22) → codec `unknown`, exit 2 `premature EOF`;
  `A3_cb22.wav` → pcm_s24le/3,839 — the cbSize≥22 precondition leg also holds.

The valid-bits step map is gated on the envelope (0xFFFE tag ∧ cbSize≥22 ∧ fmt40 ∧ base
PCM GUID), exactly as the commit message and critic record.

## Claim 4 — commit ancestry + tracked-file cleanliness: **AGREE**

- `git rev-parse --verify` resolves all three: `4c123422f2dee7…` (= HEAD), `5cc0eb0e2490c4…`,
  `37d4c57cfd2b88…`; `git merge-base --is-ancestor <c> HEAD` → YES for each.
- `git status --porcelain` post-run: **zero non-`??` lines** — no tracked file modified,
  added, or deleted by my run (the 92 `build_artifacts.py` regenerations rewrote
  byte-identical fixtures; tracked `__pycache__/*.pyc` untouched). `git diff HEAD` empty.
- New untracked entries attributable to me: 92 fresh receipt dirs under
  `corpus/live/runs/20261014T0106…–0108…` (expected per the assignment) and
  `corpus/live/r64-verifier/`. Pre-existing sibling untracked paths (`r64-baseline/tree/`,
  `r64-boundary/runs/*`, `reports/round-64/r64-boundary.md` landed during my run) are
  not mine.

## Verdict summary

| claim | verdict |
|---|---|
| 1 — ledger replay 44/48 + prior-86 byte-identical | **AGREE** (86/86 `cmp -s` clean; exits+failsums position/verbatim-identical; 6/6 new receipts also byte-identical to author's) |
| 2 — pair discriminators + sole-diff byte 38 + byte 256=0x84 | **AGREE** (all six members, direct probes match receipt fields) |
| 3 — envelope-gate precondition | **AGREE** (tag 0x0001 → s16le/5,760; tag 0x0006 → alaw/11,520; cb21/cb22 leg confirmed) |
| 4 — commits resolve + ancestors + clean tracked state | **AGREE** |

## Residual / notes

- Scope: verified the four assigned claims on the committed tree. I did not independently
  re-derive the 74-variant sweep law (author's `results.tsv` data); the three boundary
  pairs do reproduce its steps at 8|9, 24|25, 56|57.
- A sibling seat (boundary) was writing untracked files during my replay; no interference
  observed — all comparisons ran against committed paths.
- No `lsp` device on this substrate for the (trivial) script reads; grep/read sufficed —
  recorded per the fallback rule.
