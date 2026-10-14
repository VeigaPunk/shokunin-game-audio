# Round 66 — simplifier: minimality audit of the preemptor-map completion landing

Seat: **simplifier** (leaf, report-only — no tracked edits). Host: devin. Worktree
`~/Projects/prymeagnt/audio`; `.shokunin/audio/` → `~/Projects/shokunin/audio-shokunin`
(canonical repo). Brief: after the author lands, keep/drop per landed element —
each new pair the minimal expression (wve member only if wve preempts; decodable
pair earns its place iff it pins detection≠accept; len-gate members pin exact byte
counts); flag missing minimal adds; check flags not dead, comments proportional,
no duplicated builder paths.

**Landing status at write time**: author's diff is landed as uncommitted
working-tree state on HEAD `30e5e32` (r65 adjudication): `build_artifacts.py`
**+113/−1**, `measure_audio.py` **+93/−4** (plus mechanical `__pycache__/*.pyc`
regen), `corpus/live/round-66/` **6 members** (`pair_dec_{hcom,act}.wav` 600 B,
`pair_lengate_{gsrt_24,gsrt_25,hcom_131,hcom_132}.wav` 24|25|131|132 B). Ledger
`corpus/live/r66-author/ledger-r66.tsv` landed: **102 rows** (normal + 6 new
modes at positions 02–07, newest-first + 96 prior), 44 × exit 0 / 58 × exit 1.
Author report `r66-author.md` not yet on disk; I audit the landed diff,
fixtures, ledger TSV, and sweep receipts (`r66-author/results.tsv`, 80+ rows).

## TL;DR verdict

- **The 6-member set is minimal for the declared move.** Three disjoint pins:
  dec pair {hcom↔act, sole byte @68, hcom member's own reader decodes 9},
  len gates {gsrt 24|25, hcom 131|132 exactly}. Removing any member unpins
  one arm. No redundant pair, no dead flag, no oversized comment.
- **wve correctly lands zero tracked members.** wve's predicate
  (`"ALawSoundFile**"` @0–14, len ≥15) is offset-0-exclusive with `RIFF`@0 —
  no byte stream can satisfy both. The author's 30+-variant sweep and my
  independent probes converge: wve never detects on any RIFF placement
  (@4–@252 → act or wav), and wins over gsrt+hcom+0x84 only off-RIFF. The
  declared ordering claim resolved as *falsified-on-RIFF*; a tracked wve
  member would have had to abandon the RIFF+0x84@256 family invariant.
- **Every harness element is consumed.** All six flags ran end-to-end in my
  replica (rebuild byte-identical, complete receipts, correct mode/suffix
  dir names); the new `except Exception`/`measure_pipeline` branch is *not*
  dead — it fires on `dec_hcom` (`KeyError: 'duration'`); `pair_member`,
  `sox_f32_*`, and all three forced legs discriminate per member.
- **Prior behavior byte-stable, independently verified.** All 96 prior-mode
  receipt pairs byte-identical between the r66 and r65 ledgers (my own run
  of the author's compare mapping: 96/0/0); r65 fixtures rebuild identical;
  one prior-mode receipt field-identical modulo the disclosed stderr-path
  windows; new-mode receipts byte-deterministic across re-runs.
- **Drop verdicts: none.** Nothing in +201/−5 is deletable without losing a
  receipted pin.
- **Missing-add flags** (sharpening, not completion): a bare no-RIFF decodable
  preemptor member (the brief's own example — author's scratch L05–L08 +
  my probes prove it exists and decodes); carryover single-byte edge members.

## Independent re-derivation (needed to judge "minimal")

Built my own 16 probes in `corpus/live/r66-simplifier/probes/` (builder
`make_probes.py`); detection = `sox -V6 … stat` `detected file format type`,
decode = `sox <f> -t f32 -`. Results (`probe-table.txt`):

| probe | detected | decode / outcome |
|---|---|---|
| `s_wve_all_noriff.bin` (wve@0+gsrt+hcom+0x84) | **wve** | reader fail `can't find Psion identifier` — wve wins all sigs off-RIFF |
| `s_riff_wve300_all.wav` (RIFF+wve-magic@300+all sigs) | **gsrt** | wve blind off-offset-0 |
| `s_riff_wve300_act.wav` (RIFF+wve@300 only) | **act** | 0x84 claims it |
| `s_wve0_riff300.bin` (wve@0+"RIFF"@300) | **wve** | offset-0 exclusivity: never both |
| `s_gsrt_len24.bin` / `s_gsrt_len25.bin` | **wav** / **gsrt** | gate at exactly 25; sha-identical to tracked pair (`e7db9976`/`ede4161b`) |
| `s_hcom_len131.bin` / `s_hcom_len132.bin` | **wav** / **hcom** | gate at exactly 132 (below-gate → wav on RIFF+WAVE shells) |
| `s_d1_hcomdecode_act.wav` (600-B fmt16+hcom fields) | **hcom** | **decodes 36 B = 9 samples**; `--i` → `(hcom)` 22050 Hz 8-bit HCOM; `-t wav` → 1,112 B |
| `s_d1_hcom131x_act.wav` (sole diff @131) | **act** | 1,112 B via bridge |
| `s_pcm_hcom_act.wav` (1,068-B scout shape) | **hcom** | 0 B, `bad compression type`; `-t wav` → **2,048 B** |
| `s_pcm_hcom68x_act.wav` (sole diff @68) | **act** | 2,048 B; cmp sole byte @69 |
| `s_bare_gsrt_act84.bin` (no RIFF, 0x84@256) | **gsrt** | WARN checksum, **decodes 1,000** — bare preemptor, no RIFF needed |
| `s_bare_hcom_act84.bin` (no RIFF, 0x84@256) | **hcom** | **decodes**; `--i` → `(hcom)` 22050 |
| `s_actbyte_only.wav` (0x84@256, no RIFF, .wav) | none | ext→wav reader `RIFF header not found` |

Convergent with the author's `results.tsv` (W01–W04 wve wins off-RIFF;
W05|06 len gate 14|15; W1000–x14 per-byte mutants all NONE; W3*4 wve magic at
offsets 4–252 on RIFF → act/wav, never wve; D01 hcom+decodes 9; L01–L08 gates
on RIFF *and* no-RIFF) and with r65 boundary/critic/scout derivations.

Then ran the six landed flags **end-to-end in a scratch replica**
(`r66-simplifier/replica/corpus/` — the two working-tree scripts copied under
a replica ROOT so all writes stay inside my scope): each mode exit 1,
`runs/*-ui-{dec,lengate}-*-r66/` receipts complete, and **all six fixtures
rebuild byte-identical** to the tracked files (SHAs match the author's
scratch variants exactly: `325fb967`/`777b6764`/`e7db9976`/`ede4161b`/
`a1abdac4`/`6fd9f471`). Re-ran `dec-hcom` and `lengate-hcom-132` →
**byte-identical receipts across independent runs**. Two flags together →
`error: choose one probe mode` (exclusion sum live).

## Landed diff audit — keep/drop per element

`build_artifacts.py` +113/−1: `build_ui_dec_preempt_r66_probe()` (600-B
fmt-16 PCM RIFF/WAVE + hcom conjuncts @65/128 + reader field chain
@132–163 + 0x84@256; partner = sole byte @68 `'D'→'E'`), `build_ui_lengate_r66_probe()`
(parametric `shell(n)` + 4 members), six argparse flags, newest-first
dispatch head (one branch → `main()` + both builders). `measure_audio.py`
+93/−4: six flags, exclusion-sum extension, six forwarding lines, one
~74-line measurement block at the newest-first head (r65 leg set + raw f32
leg + `except Exception` pipeline branch + `pair_member`), `mode`/`suffix`
chain heads prepended. The −5 lines are sum/forwarding/chain rewrites — no
symbol or behavior removed.

| element | verdict | reason |
|---|---|---|
| `pair_dec_hcom.wav` | **keep** | the declared decodable-preemptor arm: detected `hcom` AND hcom reader decodes 9 samples (receipt `sox_stat_samples_read: 9`, f32 36 B); also natively decodable (`-t wav` → 278) and ffmpeg-decodable (`-t act` → 3,520 via ffmpeg's hcom demuxer) — three-route evidence on one member |
| `pair_dec_act.wav` | **keep** | sole-byte partner (cmp -l: offset 69 only, `'D'→'E'`) — same bytes minus one conjunct → act → bridge decodes 278. The pair pins detection≠accept *and* presence-vs-absence ordering; a cross-round reuse (round-65 `pair_preempt_act`) is not sole-byte-comparable |
| `pair_lengate_gsrt_24/25.wav` | **keep** | gate pinned at exactly 25 = 16+9: 24→`wav` (NUL@24 truncated by EOF), 25→`gsrt`. RIFF+WAVE shell choice makes the below-gate member *claimed by the next row* — sharper than a no-detect member. My independent rebuilds are sha-identical |
| `pair_lengate_hcom_131/132.wav` | **keep** | gate pinned at exactly 132 = 128+4: 131→`wav` **and decodes 43** (valid wav underneath — the fallthrough reader accepts), 132→`hcom` with `-t wav` decoding 44 underneath the hcom detection |
| len-gate "size-field+EOF" diffs | **keep** | each below-gate member is one byte shorter *and* keeps self-consistent size fields — gsrt pair: RIFF size@4 + EOF (no data chunk <44 B); hcom pair: RIFF size@4 + data size@40 + EOF. A fixed-but-lying size field would add a malformed-size confound; honest-shell is the minimal confound-free shape, and the builder comment says so |
| dec builder comment (~17 lines) | **keep** | carries the hcom reader field chain spec — required to reproduce the member; proportional to r65's convention |
| lengate builder comment (~7 lines) + measure comment (~10 lines) | **keep** | documents gate arithmetic, fallthrough semantics, and why the new except branch exists — reader-facing load-bearing |
| `-V6` route leg + `-t act` + `-t wav` legs | **keep** | all discriminate per member: `-t wav` yields 0 on `gsrt_25` vs 44 on `hcom_132` vs 278 on `dec_hcom`; `-t act` yields 3,520 on `dec_hcom` (ffmpeg re-runs the collision) vs 278 on `dec_act` vs EOF on gates |
| raw f32 leg (`sox_f32_*`) | **keep** | the decodable-preemptor claim's direct receipt field (36 B on `dec_hcom`); also captures the below-gate decode on `hcom_131` (172 B) |
| `try/except CalledProcessError` (r65 branch) | **keep** | fires on the four fail-side members (ffprobe-death) |
| `except Exception` + `measure_pipeline`/`measure_error` (new) | **keep** | *not dead*: fires on `dec_hcom` — `KeyError: 'duration'` (ffprobe's hcom format carries no duration field). Records the stop point deterministically; without it the flagship member would be a receiptless crash |
| `pair_member` field | **keep** | consumed by all six receipts; keeps member identity inside the entry (the `ui_*_r66_probe` name alone was the r65 pattern) |
| 6 flags + sum guard + forwarding + dispatch + mode/suffix heads | **keep** | 1:1 flag↔file↔receipt↔ledger-row symmetry (102-row ledger, new at 02–07); every flag verified live in replica |
| single dispatch branch → both builders | **keep** | one r66 family trigger; splitting into two branches would duplicate the same condition for no weight saving |
| `__pycache__/*.pyc` diff | **keep** (disclosed) | mechanical `py_compile` regen, standing disclosure since r62 |

**Nothing deletable.** Rejected-as-worse alternatives checked: (a) dec pair
without `dec_act` — loses the sole-byte detection-flip control; (b) dec pair
without `dec_hcom` — loses the declared decodable-preemptor arm entirely;
(c) 2-member lengate set {25,132} only — leaves the below-gate fallthrough
unreceipted; (d) no-RIFF lengate shells instead of RIFF+WAVE — below-gate
member would show no-detect instead of the sharper wav-claim (author's own
scratch L06/L08 show NONE on bare bodies); (e) a second byte-flip partner
(131x, author's D03) alongside 68x — redundant conjunct-loss pin, correctly
left in scratch.

## Flag-for-add candidates (sharpening, NOT defects; do not add myself)

1. **Bare no-RIFF decodable preemptor member** — the brief's own example and
   the one genuine gap in the tracked map. Author scratch L05–L08 prove
   detection fires without RIFF at exact gates; my `s_bare_gsrt_act84.bin`
   (no RIFF, gsrt@16, 0x84@256) **decodes 1,000 samples** and
   `s_bare_hcom_act84.bin` **decodes** under `(hcom)` — a tracked member of
   that shape would pin "RIFF is not required for preemptors" *and*
   "0x84 is inert without RIFF" simultaneously. Cost: +1 file/flag/mode.
2. **wve top-anchor member (off-RIFF)** — optional: `wve+gsrt → wve` is the
   map's upper edge (author W03, my `s_wve_all_noriff`); it cannot carry the
   family invariant so it would be a differently-shaped member. Worth one
   member only if the parent wants the full table order tracked, not just
   the RIFF-reachable part.
3. **Single-byte signature-edge members on the 11,588-B family** (carried
   from r65): `ring.binX` (NUL@24 value mutant → act) and `HCOX`/`FSSE`
   one-byte-offs — the r66 dec pair covers the FSSD-68 byte on the 600-B
   family; the gsrt-NUL *value* edge remains scratch-only. Optional.

## Nits (none discrimination-affecting)

1. `compare_receipts.py` reads `HERE/"ledger-r65.tsv"` — absent in
   `r66-author/` at write time → FileNotFoundError as landed. The comparison
   itself is sound (I ran the mapping against the real
   `r65-author/ledger-r65.tsv`: 96 pairs, 0 mismatches, 0 missing). Presumed
   a staging step in the author's pending report, not a defect of the
   tracked surface.
2. `sox_exit_code` on ffprobe-death entries records ffprobe's returncode
   (r65 nit carried); `decode_error_tool` disambiguates in-receipt.
3. `except Exception` is broad — could mask an unrelated future regression
   under `measure_pipeline`; self-correcting via `measure_error` which
   records the exact exception. Proportional but loose.
4. Stderr tails embed absolute paths (the r62/r63/r65-disclosed same-host
   caveat; the r66-baseline seat quantified it: 10/96 rows are
   path-embedding class, 0 content diffs).
5. The fmt-16 PCM skeleton is constructed twice — inline in the dec builder
   and as parametric `shell(n)` in the lengate builder (~15 overlapping
   lines). Within lengate the helper dedupes four members correctly; across
   builders the shapes differ (fixed-600-with-fields vs parametric-n with
   `n>=44` fmt guard). Acceptable today; if a third r67 consumer lands the
   same skeleton, a shared helper earns its place.
6. Author's `runs/` spot-run receipts (pre-ledger) remain untracked —
   parent's integration concern, not tracked-surface weight.

## Preserved contract

- `git status`: the only tracked modifications are the two scripts +
  `__pycache__` — no prior fixture, receipt, or ledger row touched;
  r63/r64/r65 pair SHAs unchanged by construction (committed files).
- Byte-stability verified independently, not just reported: r66 ledger rows
  8–102 + row 1 vs r65 ledger rows 1–96 → **96 pairs, 0 mismatches**
  (byte-for-byte receipt comparison I ran myself); r65 fixtures rebuilt
  identical through the modified dispatch; new receipts deterministic.
- One convention: naming (`pair_dec_*`/`pair_lengate_*`,
  `--probe-ui-*-r66`), newest-first dispatch/chains, receipt schema all
  follow the r57–r65 pattern; ledger insertion newest-first at 02–07.
- No `lsp` device exists on this substrate — the diff removes no symbols
  (the −5 lines are chain/sum rewrites verified by `git diff`), so no
  deletion candidate required reference-proving this round.

## Scope / housekeeping

All findings host-specific (SoX_ng 14.8.0.1 + ffmpeg/ffprobe n9.0.1, devin).
Writes this round: this report +
`corpus/live/r66-simplifier/{make_probes.py, probes/*, probe-table.txt,
replica/**}`. No commits, no pushes, no tracked edits, no subagents, no
sibling writes. Working tree otherwise as the author left it.
