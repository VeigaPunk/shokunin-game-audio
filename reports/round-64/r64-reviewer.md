# R64 non-author reviewer — r63 audit: 86-command serial replay + source-citation re-verification

host: devin. Canonical lane repo `~/Projects/shokunin/audio-shokunin` HEAD `37d4c57`
("audio r63 adjudication: ADMIT — …"); worktree `~/Projects/prymeagnt/audio` with
`.shokunin/audio` a symlink into the canonical repo (the prymeagnt repo's own HEAD
`8ec47838` is a different history line — ancestry checked canonically). I authored
none of r63's content. My only writes: this report and scratch under
`corpus/live/r64-reviewer/` (`rerun.py`, `modes.txt`, `ledger-r64-reviewer.tsv`,
`rerun.log`, `out/{NN}.stdout|stderr`, `variants/`, `census-{before,after}.txt`,
`fresh-runs.txt`, `receipt-pairs.tsv`, `r62-receipt-pairs.tsv`, `pair-shas.txt`,
`route{84,00}-v6.txt`, `r63-receipt-paths.txt`), plus the runner's own receipts under
`corpus/live/runs/` — the runner still has no `--runs` flag; fresh dirs identified by
before/after census (2,968 → 3,054 = **exactly +86**, all mine, zero interleaving).

Toolchain: `SoX_ng v14.8.0.1`, ffmpeg/ffprobe `n9.0.1`, python3 + numpy 2.5.3 —
matches r63's declared toolchain exactly.

## Verdict: AGREE with every pivotal claim. Two minor disclosure nits (non-gate).

| # | checked claim | result | evidence |
|---|---|---|---|
| 1 | 86-cmd ledger totals 43 exit0 / 43 exit1 | **AGREE** — replayed serially once each from worktree root (MODES ast-verified verbatim-identical to `r63-author/run_ledger.py`); my totals 43/43 | `ledger-r64-reviewer.tsv`, `rerun.log` |
| 2 | 86/86 exits match `ledger-r63.tsv` row-for-row | **AGREE** — zero diffs | paste/diff cols 2 |
| 3 | 86/86 failure-summary strings match | **AGREE** — zero diffs (col 4) | same |
| 4 | fresh receipts byte-identical to committed col-3 receipts | **AGREE** — 86/86 `cmp`-identical; all 86 committed paths git-tracked and on disk | `receipt-pairs.tsv` |
| 5 | prior-84 ↔ r62: exit sequence position-identical; receipts byte-identical | **AGREE** — removing rows 2–3, exits = `r62-author/scratch/ledger-r62.tsv` exactly; 84/84 fresh receipts `cmp`-identical to r62's committed paths (three generations now agree: r62 author, r63 author, me). r62 base 43/41 confirmed → 43/43 arithmetic exact | `r62-receipt-pairs.tsv` |
| 6 | pair_route_84 → `act`/(ffmpeg), 3,839 samples, exit 0 | **AGREE** — `detected file format type 'act'`, `(ffmpeg)` tag, `Samples read: 3839`, raw exit 0; ffprobe `pcm_s24le`/24-bit/`0.080 s` | `route84-v6.txt` |
| 7 | pair_route_00 → native `wav` fatal, exit 2 | **AGREE on the decode path** — `detected 'wav'`, FAIL `number of valid bits exceeds the number of bits per sample`, raw exit **2** (`-n stat`, ±`-V6`). See nit N1 for the `--i` attribution | `route00-v6.txt` |
| 8 | pair bytes: SHA `cf5edecc…`/`cb77db31…`, sole diff byte 257 (offset 256) 0x84/0x00 | **AGREE** — sha256/cmp/xxd reproduced verbatim; both 11,588 B, `RIFF…WAVE`; header is genuinely valid17-extensible (`wFormatTag 0xfffe`, fmt40, 16-bit container, **validBits 17**, mask 0x4, subformat PCM tag 0x1) | `pair-shas.txt` |
| 9 | formats.c citations: `AUTO_DETECT_SIZE 257 /* for act */` (:61, `#if USING_FFMPEG`, else 132 for hcom :63); CHECK macro :71-72; `CHECK(act,0,4,"RIFF",256,1,"\x84")` :93 + "Must come before wav" comment; `CHECK(wav,RIFF/WAVE)` :95 (+RIFX :96, RF64 :97); act precedes wav | **AGREE — verified against independently fetched upstream** `codeberg.org/sox_ng/sox_ng` tag `sox_ng-14.8.0.1` `src/formats.c` (sha256 `82c3058e…`), not merely the seat's pruned tree. The surviving `/tmp/sox_ng` extraction (formats.c+ffmpeg.c only) is byte-identical to upstream | /tmp fetch, `diff` clean |
| 10 | ffmpeg.c: `act` in names[] (:116), `FFMPEG_FORMAT(act)`/`G729A` (:196-7), pipe `ffmpeg -loglevel quiet -nostdin -strict -2 -i FILE -f au -` | **AGREE** — upstream ffmpeg.c fetched, argv verbatim | /tmp fetch |
| 11 | commits `1a97b0e`/`37d4c57` resolve and are ancestors of HEAD | **AGREE** — both `merge-base --is-ancestor` HEAD in canonical repo; `37d4c57` IS HEAD. Not ancestors of the prymeagnt worktree repo (different history; `.shokunin/audio` symlinks in — same note r63-verifier made) | git |
| 12 | receipt fields: row-02 `act`/`ffmpeg`/`pcm_s24le` + 4-gate signature; row-03 `wav`/`native`/`sox_exit_code 2` + verbatim stderr | **AGREE** — fresh receipts carry all fields; stderr embeds absolute canonical path (same-host coupling, verifier's caveat stands) | rows 02/03 receipt JSON |
| 13 | predicate falsification controls (independent re-derivation) | **AGREE** — my own `v256_42.wav` (0x42@256) → `wav`/FAIL/exit 2; `v257_84.wav` (0x84@257, 256 stays 0x00) → `wav`/FAIL/exit 2. Both directions hold | `variants/` |
| 14 | rebuild determinism | **AGREE** — replay re-ran the r63 probe builders; tracked pair SHA unchanged (`cf5edecc…`), zero modified tracked files | git status |

## Findings (severity: minor — non-gate; nothing blocking)

- **N1 — `sox --i` exit-code misattribution (r63-author.md:126).** The author writes
  "`sox --i` → FAIL … (exit 2)". Measured three times on this host: `sox --i
  pair_route_00.wav` exits **1** (info-mode exit convention), while the decode path
  `sox [-V6] pair_route_00.wav -n stat` exits **2**. The substantive claim — native
  `wav` route fatally rejects the valid17 header, decode exit 2 — is fully correct,
  and the adjudicator/verifier attributed exit 2 to the `-V6 -n stat` path correctly.
  Only the author's parenthetical on the `--i` invocation is wrong. Cosmetic; no
  contract, receipt, or verdict depends on it (`sox_exit_code: 2` in the row-03
  receipt records the decode-path invocation, which is the meaningful one).
- **N2 — "tarball retained for citation" is false in the committed tree
  (r63-adjudicator.md:46).** `corpus/live/r63-boundary/` contains no `src/` and no
  `*.tar.gz`; nothing named sox_ng/formats.c exists anywhere in the repo or in git
  history at `1a97b0e`/`37d4c57` (never tracked; pruned or cleaned on disk too). On
  this host only a two-file `/tmp/sox_ng/` extraction survives — outside the repo,
  ephemeral. Consequence: none for correctness (I re-fetched the upstream tag and
  verified every cited line independently), but the disclosure's "retained" wording
  overstates what an auditor will find; future audits must re-fetch upstream.
- **Observed, not a defect:** verifier's same-host caveat stands — row-03 receipt's
  `sox_stderr` embeds the absolute canonical path; byte-identity holds only where
  the worktree resolves to the same canonical path (true here).

## Residual risk / verification gaps

- Same-host verification only (SoX_ng 14.8.0.1 + ffmpeg n9.0.1, devin). Non-
  `USING_FFMPEG` builds lack the `act` row entirely — bound disclosed by r63, held here.
- The exhaustive sweeps (512-value / 23,176-position) were **not** re-run — verified
  by independent targeted falsification controls in both directions plus the pinned
  pair, same posture as r63-verifier; full rows live in `r63-author/results.tsv`.
- Sibling r64 seats (`r64-author`, `r64-scout`) were active during my replay; my
  census shows exactly +86 fresh dirs all attributable to my run — clean, but the
  shared `runs/` namespace remains an interleaving surface.
- No commit/push/merge performed; leaf reviewer seat.
