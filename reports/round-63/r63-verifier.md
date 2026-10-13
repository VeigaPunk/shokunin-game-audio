# R63 non-author verifier — 86-command serial replay + act-predicate spot-checks

host: devin. Canonical lane repo `~/Projects/shokunin/audio-shokunin` HEAD `1a97b0e`
("audio r63: act autodetect predicate pinned — RIFF@0 AND file[256]==0x84"); worktree
`~/Projects/prymeagnt/audio` HEAD `8ec47838` with `.shokunin/audio` a symlink into the
canonical repo — the "round commit is HEAD" claim holds canonically. I authored none of
this round's content. My only writes: this report, scratch under
`corpus/live/r63-verifier/` (`rerun.py`, `ledger-verifier.tsv`, `rerun.log`, `out/`,
`variants/`), and the runner-generated receipts under `corpus/live/runs/` (the runner
has no `--runs` flag; fresh dirs identified by before/after timestamp census).

Toolchain observed: `sox: SoX_ng v14.8.0.1`, `ffmpeg version n9.0.1`, `ffprobe` (same
build), `python3` + numpy 2.5.3 — matches the author's declared toolchain exactly.

## Verdict: AGREE with every checked claim. No disagreement found.

## 1. 86-command serial replay (task 1) — CONFIRMED, exact

`corpus/live/runs/` censused before (2,879 dirs) and after (2,966 = +87: the 86 replay
runs plus one `normal` timing probe `20261013T235431336164Z`, also byte-identical to the
committed row-01 receipt). Ran all 86 commands serially once each from
`~/Projects/prymeagnt/audio` as `python3 .shokunin/audio/corpus/fixtures/measure_audio.py
<flag>` in the author's declared order (the r62 84 verbatim + `--probe-ui-route-act-
{84,00}-r63` at positions 2–3 — MODES copied verbatim from `corpus/live/r63-author/
run_ledger.py` into `corpus/live/r63-verifier/rerun.py`). Per-row ledger:
`corpus/live/r63-verifier/ledger-verifier.tsv`; per-command stdout/stderr captures in
`corpus/live/r63-verifier/out/{NN}.stdout|stderr`.

- Totals: **43 exit 0 / 43 exit 1** — matches the claimed 43/43 exactly (r62's 43/41
  plus the two new exit-1 probes).
- **86/86 exit codes match** the author's committed `ledger-r63.tsv` row-for-row, and
  **86/86 failure-summary strings match** (`diff` over TSV cols 1,2,4 → empty).
- Removing my rows 2–3, the prior-84 exit sequence is identical to
  `corpus/live/r62-author/scratch/ledger-r62.tsv` position-for-position (one cosmetic
  note: r62's TSV wrote invalid-battery failures `k=v`-style, r63 writes `k: v`-style;
  same payload — my row 81 matches r63's verbatim).
- **86/86 fresh receipts are BYTE-IDENTICAL** (`cmp`-equivalent hash compare, all rows)
  to the committed counterparts named in `ledger-r63.tsv` col 3. All 86 committed
  receipt paths are git-tracked (`git ls-files` → 86/86 present).
- New r63 rows land in the claimed classes: row 02 `ui_route_act_84_r63_probe` → exit 1,
  `format: expected PCM16; duration: outside ±1 ms; level: clipping headroom or near
  silence; spectrum: centroid outside fixture band`; row 03 `ui_route_act_00_r63_probe`
  → exit 1, `decode: default SoX route rejected input`.
- Bonus determinism check: the author's two earlier exploratory receipts
  (`20261013T2341{57,58}*-ui-route-act-{84,00}-r63`) are byte-identical to the ledger
  receipts — three independent generations now agree (author's two + my one).
- The `00` receipt embeds the absolute input path inside `sox_stderr`
  (`/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/round-63/pair_route_00.wav`)
  — identical on my run only because the worktree resolves to the same canonical path;
  noted as a same-host coupling, not a defect.

## 2. Pair byte evidence (task 2) — CONFIRMED

```
$ sha256sum corpus/live/round-63/pair_route_{84,00}.wav
cf5edecce1812f0a0a5c1a16f0b2a920118be3f281b3f43638c1bc2f9f6b93e4  pair_route_84.wav
cb77db319a7a791fa95ed14d83ab08f0c75b5c80635ec1897a9dea7c591c621a  pair_route_00.wav
$ cmp -l pair_route_84.wav pair_route_00.wav
  257 204   0          # sole diff: 1-based byte 257 = file offset 256; 0o204=0x84 vs 0x00
$ xxd -s 252 -l 8 pair_route_84.wav   →  80f5 54f5 [84]f5 9af5   (offset 256 = 0x84)
$ xxd -s 252 -l 8 pair_route_00.wav   →  80f5 54f5 [00]f5 9af5   (offset 256 = 0x00)
$ xxd -l 16 pair_route_84.wav         →  "RIFF" <2d3c> "WAVEfmt "
```

Both 11,588 B, both `RIFF…WAVE` headed; SHAs match the author's cited
`cf5edecc…`/`cb77db31…` verbatim. Rebuild determinism confirmed incidentally: the replay's
two r63 modes re-ran `build_ui_route_act_r63_probe()` twice; post-replay SHAs unchanged
and `git status` shows no modification to the tracked pair.

## 3. Discernment spot-checks (task 3) — CONFIRMED both directions

Admitted (act/ffmpeg bridge):

```
$ sox -V6 corpus/live/round-63/pair_route_84.wav -n stat
sox INFO formats: detected file format type `act'
Input File     : 'pair_route_84.wav' (ffmpeg)
Samples read:              3839        # exit 0
```

Rejected (native wav route):

```
$ sox -V6 corpus/live/round-63/pair_route_00.wav -n stat
sox INFO formats: detected file format type `wav'
sox FAIL formats: can't open input file `…/pair_route_00.wav': number of valid bits
exceeds the number of bits per sample                              # exit 2
```

Predicate falsification controls (scratch `corpus/live/r63-verifier/variants/`):

- `v256_42.wav` = pair_route_84 with offset 256 → `0x42` (`dd conv=notrunc`; `cmp -l`
  vs base confirms sole diff at byte 257): `detected file format type 'wav'` → FAIL
  valid-bits, exit 2. **Value-exact direction holds** — 0x42 does not trigger act.
- `v257_84.wav` = pair_route_00 with offset 257 → `0x84` (byte 256 stays `0x00`; `xxd
  -s 256 -l 4` → `0084 9af5`): `detected file format type 'wav'` → FAIL valid-bits,
  exit 2. **Position-exact direction holds** — 0x84 at offset 257 does not trigger act.

## 4. Cited commits (task 4) — CONFIRMED

```
$ git merge-base --is-ancestor <c> HEAD && git log -1 --format="%h %s" <c>
cbe763e IS ancestor — "audio r62: SoX 3,839 decode gap resolved — ffmpeg packet-residue"
3c96a69 IS ancestor — "audio r62 adjudication: ADMIT — …"
1a97b0e IS ancestor — "audio r63: act autodetect predicate pinned …"   (= HEAD itself)
```

## 5. Commit shape (supporting) — CONFIRMED additive

`git show --stat HEAD` (`1a97b0e`): `build_artifacts.py` 33 +− (+32/−1 per author's
accounting) including `build_ui_route_act_r63_probe()` (byte-256 pinned by assignment
0x84/0x00 over the r61 valid17 fragile-header family, shared deterministic payload),
`measure_audio.py` 29 +− (+25/−4): two flags + mutual-exclusion extension + one
measurement block recording
`sox_detected_format`/`sox_route` + `mode`/`suffix` chain heads, two `__pycache__/*.pyc`
(mechanical py_compile churn — same disclosure as r62; not audited), pair wavs, r63
author scratch (`ledger-r63.tsv`, `run_ledger.py`, `gen_sweep.py`, `results.tsv`,
`variants/`, `fullpos.log`), 88 tracked `20261013T234*` run receipts, 8 seat reports.
All tracked content inside lane scope.

## Residual risk / gaps

- Same-host verification only (SoX_ng v14.8.0.1 + ffmpeg n9.0.1); the author disclosed
  the `#if USING_FFMPEG` / AUTO_DETECT_SIZE host bound. Not re-checked against source —
  my spot-checks are empirical against installed sox, plus ledger-level replay.
- The exhaustive sweeps (512-value, 23,176-position) were NOT re-run — verified by
  targeted falsification controls in both directions instead; full rows live in
  committed `corpus/live/r63-author/results.tsv`.
- The `00` receipt's embedded absolute path means byte-identity holds only on hosts
  where the worktree resolves to the same canonical path (my host does).
- Working tree now carries my verifier detritus: `corpus/live/r63-verifier/` scratch +
  87 new untracked `corpus/live/runs/` receipts, plus pre-existing untracked
  `reports/round-63/r63-simplifier.md` (not mine). Zero modified tracked files.
- No commit/push/merge performed; leaf seat.
