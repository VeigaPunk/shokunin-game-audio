# R74 scribe (audio) — parser/witness audit + evidence ledger

**Headline:** the r74 author arm was **absent at every check** (0 `r74` refs in the
fixture, 0 r74 receipts, no `reports/round-74/` until this file) while sibling
scratch trees went active from 15:19Z (author members `lavf_{iss,iss_multi,apc,
acm,adx,aifc}`; boundary `ffdec-*`/`smoke-*` member validation; critic/scout/
reviewer `iss/acm/hcom` mutants). This seat ran a **read-only parser
audit** of the production parse paths against real raw streams (frontier mpv +
pw-cat logs) and synthetic forged streams: **27 cases** — mpv verdict is
first-match (a prepended forged `finished playback` line flips the verdict while
rc stays), sox error is last-match (an appended forged `FAIL` line replaces the
genuine verdict), pw-cat's two fields can be forged independently (first-match
`sndfile:` + last-match `error:`), one appended forged `Seek failed` line
re-partitions the mpv transport fork, the mpv raw log is **not persisted**
(receipt is a parse result with no raw backing), and the sox-side ASLR strip
requires a `]` (latent leak; ffprobe's `_tail` does not). Receipt hygiene:
the 14-receipt `consumers-r73` family is **not homogeneous** — one receipt
(`20261014T150305963053Z`, sha `f1ddc75d…`) records **all 36 pw-cat member legs
rc=1 `Host is down` while `pactl` reports the daemon live**, self-flagged only at
the ops entry (member-level `transport_fork` booleans all read `false`);
8 of the 13 others differ from the r73-era base only in ≤1 ms `wall_s` leaves,
4 only in `wall_s` + the post-base `pwcat_name_axis` key; stamp ==
mtime (≤1.4 ms); 3 historical receipts carry raw ASLR addresses; 399 receipts
embed absolute host paths (legacy r63–r66 families); the whole `consumers-r73`
family is **untracked** (the r73 author report's "committed receipt" wording is
not git-accurate — newest tracked receipt is `20261014T142733592435Z`). One
incident: this seat's audit import regenerated the **tracked** fixture `.pyc`;
committed bytes were restored (sha `9e333fe1…`) and the worktree is clean.

Seat: **scribe** (leaf, report-only). Host: `plazir27`; system clock
**2026-10-14 15:18:36Z** at open (**15:26:33Z** at final check,
**15:24:31Z** at write; local TZ = UTC−3 — `ls` mtimes are local, receipts are
UTC; recorded, not a defect claim).
Wave label `shokunin-train-20261101-w13` (wave-name date ≠ clock date —
carried from r73, recorded, not a defect claim).
Repo `/home/vgpnk/Projects/shokunin/audio-shokunin`, HEAD **`1ba8103`**
(r73 report-last) — unchanged all session. Fixture
`corpus/fixtures/measure_audio.py` blob **`9b6e836ebda4c0ce6bfedec281a6d8d14d4a91d8`**,
sha256 `77f107864b74f794aea1d4fa8ea28f6f50d741591297dff192b9b6f949b2543b`
(2315 lines) — byte-identical to HEAD at every check. Toolchain re-read this
session: `pw-cat` libpipewire **1.6.8**, `mpv` **v0.41.0** (libavformat
**63.1.101**), `ffmpeg` **n9.0.1**, `sox` **SoX_ng 14.8.0.1**, Python **3.14.7**,
libsndfile via ctypes. Write scope: this report + `corpus/live/r74-scribe/`
only; no git mutation, no product-code edit, no consumer re-run (all raw inputs
and receipts below were already on disk; the audit's subprocess layer was
monkeypatched — **no real subprocess was spawned, no receipt written**).

## Mandate (verbatim, from the r74 scribe task)

*"Own the evidentiary layer: watch the probe's raw stream vs the battery's parsed
view — find lines the parser drops, misattributes, or would forge-accept.
Catalog the hazard surface honestly (survival != safety). Cross-check receipt
hygiene (paths/timestamps/ASLR stability). Track seat landings and flag
report-vs-receipt drift."* Report → `reports/round-74/r74-scribe.md`.

## Landing state (checks at 15:18:36Z, 15:19:18Z, 15:22:14Z, 15:23:06Z, 15:23:39Z, 15:24:28Z, 15:26:33Z)

| probe | state at every check |
|---|---|
| fixture `r74` refs (`grep -c 'r74'`) | **0** (author arm absent) |
| fixture blob vs HEAD | `9b6e836…` == HEAD (clean; no author edit yet) |
| r74 receipts (`ls corpus/live/runs \| grep -c r74`) | **0** |
| r73-mode re-runs during session | one new `consumers-r73` receipt at 15:25:02Z (sibling replay; sha `9b422aa2…`, byte-identical to the 14:56:06/15:01:03 pair; family now 14) |
| `reports/round-74/` | absent until this report; **`r74-scout.md` (15:26:19Z, sha `388bd35e…`) and `r74-critic.md` (15:26:31Z, sha `f502b394…`) landed during the final check** — existence/hash spot-checked only, not read/adjudicated by this seat |
| author scratch | `corpus/live/r74-author/` appeared between the 15:23:06Z and 15:23:39Z checks: `mk_members.py` + `members/lavf_{iss,iss_multi,apc,acm,adx,aifc}` (ARM A member generation, mid-flight) |
| boundary scratch | `build_members.py`, `probe_boundary_r74.py`, `members/` (50 entries: `acm_*` edge family, …), `logs/ffdec-{iss,apc,acm}_valid.txt`, `logs/smoke-{iss,apc,acm}_valid.log`, then `logs/r74-mpv-{file,fifo}-{acm_valid,acm_ch_zero,apc_hdr_trunc8,apc_hdr_trunc20}.log` by the last check |
| critic scratch | `c2-hcom-multipkt.wav`, `c3-iss-6pkt.iss`, `c4-iss-1pkt.iss`, `c5-acm-multi.acm`, `c6-acm-multi-s0.acm`, `m1-hcom-600.wav`, `probe-results.json` |
| scout scratch | `build_members.py`, `mpv_matrix.py`, `members/`, `runs/`, `raw/`, `logs/` |
| reviewer scratch | `acm_0100.acm`, `acm_7700.acm`, `acm-strace.log`, `mk_noseek_members.py`, `mpv_matrix.py`, `mpv_position.py`, `matrix-part1.json`, `matrix-controls.json` |
| simplifier scratch | `measure_audio.py.before-ops2sim`, `diff_receipts.py`, `scan_dead.py`, landing polls |
| baseline scratch | `frozen/`, `measure-env/`, env proofs, `committed-ledger-sha.before.txt` |
| verifier scratch | `env.txt`, `ffmpeg-inventory.txt` |

Sibling scratch is **landing-state only, never evidence** (uncommitted; not
replayed by this seat). `reports/round-74/` held no sibling file until
15:26:19Z; `r74-scout.md` and `r74-critic.md` landed during the final check
(untracked, hashes above; **not read or adjudicated here**). No r74 commit
exists.

## Parser audit — raw stream vs the battery's parsed view

Method: `corpus/live/r74-scribe/parser_audit.py` (sha256 `8d49296e…`) imports
the fixture (blob pinned above) and feeds (a) **real raw streams** from
`corpus/live/frontier-pipewire/` and (b) **synthetic forged streams** through the
**production** parse paths: `transport_leg`, `mpv_leg`, `pwcat_leg`,
`transport_error`, `_pwcat_fields`, `_consumer_tail`, and the ffprobe `_tail`
closure (source-slice exec, boundary asserted at `measure_audio.py:647-653`).
`subprocess.run` is replaced by a fake that writes a crafted `--log-file` /
returns a crafted stderr+rc — no real process, no fifo, no receipt. 27 cases →
`audit-output.json` (sha256 `1216a034…`). Inputs are labelled synthetic; none of
the forged-stream results is a product-behavior claim.

### Surface inventory (parse sites, what persists, match policy)

| surface | parse site | raw input | persists | policy |
|---|---|---|---|---|
| sox verdict | `:244-251` `transport_error` | `sox -V6` stderr | `error` (message after `':`) | **last** `sox FAIL` line |
| sox leg | `:267-281` | same | `sox_detected_format` (first `detected file format type \`X'`), `samples_read` (first `Samples read:`), `sox_route` (heuristic), `stderr_tail` (**last** line, 160-char cap) | mixed first/last |
| sox fifo-hold leg | `:416-431` | same | as above + `verdict_emitted` | mixed |
| ffprobe leg | `:640-665` | ffprobe stdout JSON + stderr | `ffprobe_format`, `probe_score`, exits, `_tail` (last line, 160 cap) | first/only |
| libsndfile leg | `:805-831` | in-process ctypes (no text) | format/frames/seekable/error_str | n/a |
| sndfile-info CLI | `:941-948` | `sndfile-info` stdout | `format_hex`, `frames_field`, `reason` | `reason` = **last non-empty line iff "Error" appears anywhere in output** |
| pw-cat leg | `:1020-1027`, `:1073-1079` | `pw-cat -p` stderr | `sndfile_error` (**first** `sndfile:` line), `pw_error` (**last** `error:` line), `error` = blocked ∨ sndfile ∨ pw, `stderr_tail` (last line, 160 cap) | first + last |
| mpv leg | `:1129-1147` | mpv `--log-file` text | `lavf_detected`/`lavf_probe`/`lavf_score`/`seek_failed`/`audio_track`/`mpv_verdict` (all **first** match), `stream_not_seekable`/`refresh_seek` (substring), `error` (blocked ∨ reason ∨ `exit N`) | first + substring |
| consumer groups | `:1169-1170` | leg dicts | fork keyed `(exit_code, sndfile_error)` / `(exit_code, lavf_detected, seek_failed)` | — |
| ops entry | `:1249-1253`, `:1302-1313`, `:1407-1413` | pw-cat/pactl | gate = rc + substring `pw_context_connect`; name axis keyed on exit codes only | substring/rc |

### What the parser drops (D-cases)

- **D1 — the mpv raw log is dropped entirely.** `mpv_leg` writes the log into a
  `TemporaryDirectory` (`:1102-1128`) and persists **only** the 13 parsed leg
  keys (audit case `J`); `grep -rl "Detected file format" corpus/live/runs/*/
  measurements.json` → **0** files. Real raw logs: 217/236/207/207 lines, of
  which the 6 regexes touch **5/4/2/2** lines (`A.real:*`). The receipt is a
  **parse result with no raw backing** — nothing in a receipt can be re-derived
  or re-audited without the ephemeral log. (Frontier/sibling raw logs exist and
  were used here; r73-era consumer legs have no raw artifact anywhere.)
- **D2 — sox keeps only the last stderr line**, 160-char capped (`:276-281`,
  `:427-431`); earlier `FAIL`/INFO lines are dropped. `detected`/`samples_read`
  are first-match while `error` is last-match — an injected *trailing* line
  changes `error`/`stderr_tail` but not detection.
- **D3 — pw-cat keeps 2 parsed fields + the last line** (real raw stderr is 2
  lines: `sndfile:` + `error:`; `K.real:*` — the line not captured by
  `sndfile_error` survives only as the 160-char tail; for `pwcat-nodaemon.log`
  the single line yields `sndfile_error=None`, `pw_error`=message).
- **D4 — ffprobe tail is last-line/160-cap** (`:647-653`); `probe_score` is
  `null` on this host (field absent from ffprobe n9.0.1 JSON — r71 LOG recorded
  it; confirmed in `20261014T141033155858Z-ffprobe-transport-r71`). **ARM A
  note:** the live score witness on this host is mpv's `Found 'x' at score=NN`
  (`mpv_leg.lavf_score`), not the ffprobe JSON field.
- **D5 — the Found-line `size=600` is dropped** (`A.real:…dec_hcom` keeps
  name+score only).
- **D6 — convention inconsistency**: most surfaces are first-match; sox error
  and pw-cat `error:` are last-match; `measure()`'s ebur128 is **last**-match
  (`:75-76`). Mixed policies are the raw material for F5.

### Misattributions (M-cases)

- **M1 — `sox_route` from a bare substring with no detection.** `:271-272`
  (`:424-426`, `:1950-1951`, `:2005-2006`): `"(ffmpeg)" in text` ⇒ route
  `ffmpeg` **even when `sox_detected_format is None`** (case `I1`). A route
  attribution can exist without a detection witness.
- **M2 — `mpv_leg.error` conflates four provenances** (`:1146-1147`): blocked
  marker ∨ log `reason` ∨ synthetic fallback ∨ `exit N`. Case `B`: forged
  `success (reason 0)` + rc=2 yields `error="success (reason 0)"` — an `error`
  field that says success.
- **M3 — fallback/real collapse.** The synthetic fallback string
  `"Failed to recognize file format."` (`:1134-1136`) is byte-identical to the
  real log line (`mpv-file-extsuffix_nomatch.wav.log:189`); case `C1` shows a
  log without a `finished playback` line but with that error line yields the
  same `mpv_verdict` string as the fallback — provenance is unrecoverable from
  the receipt. Case `C2`: neither witness ⇒ `mpv_verdict=None`, `error="exit 2"`.
- **M4 — pw-cat field split.** `sndfile_error` is first-match, `pw_error` is
  last-match (case `E1`): a forged pair produces two fields from different raw
  lines; `error` silently prefers `sndfile_error` over the `error:` line
  (`:1074-1076`), so the pw-level message is present in the receipt but absent
  from the keyed verdict.
- **M5 — sndfile-info `reason` rule** (`:944-948`): last non-empty line
  **iff the word "Error" appears anywhere** in the output. Measured raw
  (`sndfile-info corpus/live/round-68/txw_piperefuse.wav`): exit **0**, output
  ends `File contains data in an unimplemented format.` ⇒ `reason` = that line
  (correct here); a non-error file whose output merely contains "Error" would
  get a bogus `reason`. `frames_field` is the container field, never a decode
  count (r72 critic rule, kept).

### Forge-accept (F-cases — synthetic raw streams only)

- **F-a (mpv, first-wins):** a **prepended** forged
  `finished playback, success (reason 0)` line flips `mpv_verdict` to success
  while rc stays 2 (case `B`) — `re.search(..., re.M)` takes the first match.
- **F-b (fork re-partition, one line):** appending a forged
  `Seek failed (Operation not permitted)` to the real **fifo** log sets
  `seek_failed`, moving that leg out of the `[0, hcom, None]` group — the fork
  partition is forgeable from a single log line because groups key on
  `(exit_code, lavf_detected, seek_failed)` (`:1169-1170`) (cases `B2` vs
  `B3`).
- **F-c (sox, last-wins):** an **appended** forged `sox FAIL …: <msg>` line
  replaces the genuine `error` and becomes `stderr_tail` (cases `D1`, `D3`);
  no cross-check between the two fields. A `FAIL` line without `':` returns the
  whole line (`D2`).
- **F-d (pw-cat, both ends):** forged first `sndfile:` line and forged last
  `error:` line are both accepted independently (cases `E1`, `E2`).
- **F-e (route):** a bare `(ffmpeg)` substring forges route=ffmpeg with no
  detection (case `I1`).
- Bounded: no forged-stream mutation was observed in any landed artifact; these
  are parser-capability demonstrations on synthetic inputs, not product claims.

### Survival ≠ safety (S-case — a landed receipt with a hidden environment fork)

`corpus/live/runs/20261014T150305963053Z-consumers-r73` (sha256 `f1ddc75d…`)
is a **valid, schema-complete** receipt that records a run in which:
- **all 36 pw-cat member legs rc=1** with `pw_error = "pw_context_connect()
  failed: Host is down"` (36/36), **all 3** `pwcat_name_axis` legs rc=1
  Host-is-down, `pacing_instant` rc=1 in **0.002 s** (`playback_paced: false`),
  `fifo_no_writer.blocked: false` (connect gate fired before the fifo open);
- **`daemon_live`: `pactl_exit 0`, `live: true`,
  `"PulseAudio (on PipeWire 1.6.8)"`** — the PulseAudio endpoint answered while
  the native PipeWire client could not connect (the pactl-vs-pw-cat
  disagreement shape r73-simplifier C1 ruled on; mechanism **not re-measured by
  this seat**);
- the ops entry self-flags **5 failures** (no-writer did not block, empty-writer
  deviated, name axis deviated, pacing not paced, trickle aborted) — but the
  **member-level** `consumer_*_r73_probe` entries (all 9 checked) show pw-cat
  `transport_verdict_groups = [[1, null] × 4]` and `transport_fork: false`: a
  member-level reader sees "no fork, all transports agree", i.e. an environment
  failure rendered as a clean invariance cell. There is no
  per-member daemon-viability guard; the only honest witnesses are
  `daemon_live` + the ops failures. **This is the survival≠safety cell in
  receipt form** and it sits inside the family the r73 author report cites.

### ASLR / stability gaps (A-cases)

- `_tail` (ffprobe, `:651-653`) strips ` @ 0x…` with **or without** `]` and
  plain-replaces `probe_arg` (cases `G1`–`G3`); the plain replace also rewrites
  the literal `pipe:` in other contexts (`pipe:0` → `<input>0`, case `G4`).
- the **sox-side** regex requires `]` after the address (`:281`, `:430`):
  observed ffmpeg-bridge form `[wav @ 0x…]` strips (case `H1`), a bracket-less
  address does **not** (case `H2`) — latent, no such form on disk.
- live unnormalized surfaces: `sox_native_stderr`/`sox_stat_stderr`/
  `sox_bridge_stderr` capture `tail[-1][-160:]` with **no** ASLR/path strip
  (`:1966`, `:2011`, `:2021`, `:2061`); the r64 valid-bits and r63 route
  exception paths record `exc.stderr` **raw** (`:2049`, `:2075`); `invalid`
  detail records raw stderr (`:150`). Consequence measured globally below.

## Receipt hygiene (paths / timestamps / ASLR stability)

1. **`consumers-r73` family (14 receipts, on disk; still growing — a sibling
   re-ran the mode at 15:25:02Z mid-session):** sha256 groups
   `3c3b19a0…`×2, `3a0218b3…`, `e7f0d609…`, `245dfa1a…`, `9b422aa2…`×**3**,
   `5d025afb…`, `8d689232…`, `f6d5379a…`×2, `f1ddc75d…`, `a4bc7c37…`
   (10 distinct). Against the r73-era base (`…145502288182Z`, `245dfa1a…`),
   **8 of the 13** others differ only in `pacing_instant`/`pacing_trickle`
   `wall_s` (±1 ms); **4** (the pre-14:54:23Z fixture revision, no
   `pwcat_name_axis` key) differ in wall_s + that key only; the **13th** is the
   S-case environment run (`…150305963053Z`, 184 differing leaves). The
   `9b422aa2…` content is byte-identical across three wall times
   (14:56:06 / 15:01:03 / 15:25:02) and `f6d5379a…` across two
   (15:01:42 / 15:12:40) — full-file byte-stability is achievable on this host.
2. **Timestamps:** receipt dir stamp == `measurements.json` mtime (max delta
   **0.001362 s** across the 14) — the stamp is the **write** time (UTC, µs);
   the receipt carries **no run-start/duration** field (stamp is computed after
   all measurements, `:2304-2308`; `mkdir(parents=True)` without `exist_ok`).
3. **ASLR scan (all `corpus/live/runs/*/measurements.json`):** 18 files match
   `0x[0-9a-f]{8,}`; **15 are `format_hex` values** (e.g. `0x00010002`, benign);
   **3 are genuine pre-fix ASLR leaks** in `ui-preempt-gsrt-r65` receipts from
   01:40–01:42Z (before commit `50f55eb`, the `_tail` ASLR fix at 14:33Z):
   `…014008064525Z` (`cacc5a19…`, `0x559e1fb98e40`), `…014058497253Z`
   (`8bea94e3…`, `0x558acfaebe40`), `…014257840421Z` (`87fbd3be…`,
   `0x5602c15ece40`) — **each run carries a different address** (the ASLR
   instability itself), plus an absolute path. Prior rows are byte-frozen
   (insertion-only policy); recorded, not a change request.
4. **Path embedding:** 399 receipt files contain `/home/vgpnk/…`
   (r65 110, invalid 107, r64 90, r66 61, r63 26, normal 5) — those families
   cannot be byte-stable across hosts/clones. The post-r67 transport/consumer
   families are path-clean.
5. **Tracked vs untracked (durable evidence):** newest **tracked** receipt =
   `20261014T142733592435Z-sndfile-transport-r72`; **305 untracked receipt
   files** at the final check (incl. **all 14** `consumers-r73` —
   `git ls-files` count 0). The
   r73 author report says *"Measured (committed receipt
   `20261014T145502288182Z-consumers-r73`)"* and the adjudicator calls the diff
   *"operator-committed `febf34b`"* — the **diff** is committed; the **receipt**
   is on-disk-only at snapshot. See F1.
6. **`.pyc` incident (disclosed):** importing the fixture for the audit
   regenerated the **tracked** bytecode cache
   `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`
   (157,038 B → 183,923 B; first observed dirty at the 15:22:14Z check). The
   committed blob was restored byte-identically at ~15:22:2xZ via `git cat-file`
   (no checkout/index mutation; sha256
   `9e333fe1ff95fdbaf9b481844f480c1ec7f5d8c9ccb1216236169dd6c02338ed`);
   `git status --porcelain --untracked-files=no` → **0** afterwards, and the
   audit was re-run with `python3 -B`. Root cause: the committed `.pyc` is
   stale w.r.t. the r73-era source mtime, so **any import-based tooling
   rewrites it** — `git status` cleanliness for this repo depends on whether a
   seat *runs* the fixture (as `__main__`, no cache write) or *imports* it.
   Baseline "zero-drift" and verifier "prior rows byte-stable" checks must
   exclude `__pycache__` or expect this churn.

## Seat landings + report-vs-receipt drift

- **r74:** no author arm, no receipts, no reports at every check (table above);
  sibling scratch only. Nothing to admit at scribe snapshot.
- **r73 drift items** (verbatim quotes, evidence): F1 (receipt-not-committed),
  F2/S-case (family heterogeneity), F4 (raw log not persisted), plus the
  r73-era receipts at 14:56–15:25Z were produced **after** the r73 scribe
  snapshot (5 → 14 receipts, the 15:25:02Z one during this session) by the
  closeout replay seats — a family-size drift worth recording in the ledger.
- **r74 sibling reports landed at the wire:** `r74-scout.md` (15:26:19Z, sha
  `388bd35e…`) and `r74-critic.md` (15:26:31Z, sha `f502b394…`), untracked;
  existence/hash spot-checked only — their claims are the judge's to weigh.
- Sibling scratch trees (all untracked, in flight, **not evidence**; used as
  landing-state only): author, baseline, boundary, critic, reviewer, scout,
  simplifier, verifier — inventory above.

## Findings reported verbatim for the canonical judge

- **F1 — "committed receipt" wording vs git state.** `r73-author.md:47`:
  *"Measured (committed receipt `20261014T145502288182Z-consumers-r73`)"*;
  actual: `git ls-files corpus/live/runs | grep -c consumers-r73` → **0**;
  `git status` shows the whole family untracked; the r73 report-last commit
  `1ba8103` touched reports/LOG/SCORECARD only. Durable-evidence frontier in
  git = `20261014T142733592435Z-sndfile-transport-r72`. No verdict impact;
  ledger wording must be corrected.
- **F2 — the `consumers-r73` family contains an environment-failure receipt
  that reads as a clean invariance cell at member level**
  (`…150305963053Z`, sha `f1ddc75d…`; 36/36 pw-cat legs `Host is down`,
  `pactl` live, 5 ops failures, member forks all `false`). Any family-level
  aggregation, byte-compare, or "N receipts agree" statement must classify or
  exclude it. This is measured, in-receipt evidence of the pactl-vs-pw-cat
  disagreement (r73-simplifier C1) and of the carried guard *"rc alone is not a
  verdict"*.
- **F3 — no per-member daemon-viability guard.** In the fixture, member legs
  never consult `daemon_live`; only the ops entry carries it
  (`:1215-1253`). A daemon-down run yields member verdicts that are
  connectivity failures rendered as `transport_fork: false`. (Hazard for ARM
  B's ops-2 fold; not fixed by this seat.)
- **F4 — receipts are not self-re-derivable for the mpv surface** (raw log
  ephemeral, `:1102-1128`; 0 receipts contain log text). mpv-keyed claims are
  supported only by ephemeral logs or sibling/frontier raw logs; the landed
  receipt alone cannot be re-audited for them.
- **F5 — forge-accept positions are asymmetric** (first-wins mpv verdict /
  last-wins sox error / pw-cat first+last split / one-line fork re-partition).
  No mutated stream observed in any landed artifact; the parser has no
  cross-field consistency check (e.g. `error` vs `stderr_tail` provenance).
- **F6 — `mpv_verdict` fallback collapse** (`:1134-1136`): the synthetic
  fallback is byte-identical to the real log's error line text; receipts
  cannot distinguish the provenances (case `C1`).
- **F7 — `sox_route` attribution without detection** (`:271-272` and the three
  sibling sites): `"(ffmpeg)"` substring ⇒ route `ffmpeg` with
  `sox_detected_format None` (case `I1`).
- **F8 — ASLR-strip asymmetry:** sox-side requires `]` (`:281`, `:430`),
  ffprobe-side does not (`:652`); `sox_native_stderr`/r64/r63 exception paths
  have no normalization at all (`:1966`, `:2049`, `:2061`, `:2075`). Latent on
  the current corpus; 3 historical receipts already carry raw addresses.
- **F9 — 399 receipts embed absolute host paths** (legacy r63–r66 + invalid
  families) — cross-host byte-stability is impossible for them; prior rows
  frozen (recorded, not a change request).
- **F10 — tracked `.pyc` churn:** the committed cache is stale w.r.t. current
  source; any import-based tooling dirties the worktree (incident disclosed,
  bytes restored, sha `9e333fe1…`).
- **F11 — wave-label date vs system clock** (`20261101` vs 2026-10-14;
  carried from r73) and **local TZ = UTC−3** (ls mtimes vs UTC receipt stamps).
  Recorded, not defect claims.
- **F12 — receipt stamp semantics:** dir stamp = write time (µs, UTC), no
  run-start/duration field; stamp==mtime verified (≤1.4 ms across 14). Minor.

## Gates

| gate | state at final check (15:26:33Z) |
|---|---|
| author landing (`--probe-lavfsweep-r74` + receipts) | **ABSENT** — 0 r74 refs, 0 r74 receipts; author scratch/members appeared between 15:23:06Z and 15:23:39Z |
| fixture / prior rows byte-stable | worktree clean (0 tracked-modified) at every check; fixture blob == HEAD `9b6e836…` |
| r74 receipts | 0 (r73-mode replay receipts keep appearing: 14 `consumers-r73`) |
| sibling seat landings | scratch active (author/baseline/boundary/critic/reviewer/scout/simplifier/verifier); **`r74-scout.md` `388bd35e…` + `r74-critic.md` `f502b394…` landed 15:26:19–15:26:31Z** (untracked; existence/hash only) |
| parser audit (this seat) | **DONE** — 27 cases, read-only, `audit-output.json` `1216a034…` |
| receipt hygiene (this seat) | **DONE** — 14-receipt family + global scans; F1–F3, F9–F10 |
| verifier replay / adjudication | not started (no r74 commit) |
| ledger drafts (LOG/SCORECARD) | **deferred** — nothing landed to record; scribe snapshot only |

## LOG / SCORECARD draft

No r74 arm landed during this seat's window; per the seat rule *"Do not rerun
work merely to decorate the report"* and the ledger convention (entries record
landed moves), **no LOG/SCORECARD entry is drafted here**. When the author arm
lands, the ledger entry must carry: the ARM A fork/invariant cells per member
(iss/apc/acm vs wav/aifc/adx controls), the multi-packet truncation-shape cell,
the `mpv --start=N` position cell, ARM B's kill-escalation rc cell + `--target
0` negative case + raw-mode name-axis death, plus this seat's parser-audit
hazard list and the F1/F2 receipt-hygiene corrections.

## Touched surfaces

- Wrote **only**: `reports/round-74/r74-scribe.md` (this file) and
  `corpus/live/r74-scribe/{parser_audit.py, audit-output.json,
  audit-stdout.txt, receipt_hygiene.py, receipt-hygiene.json, watch.sh,
  landing-watch.log, checks.txt}`.
- Restored (byte-identical to HEAD): `corpus/fixtures/__pycache__/
  measure_audio.cpython-314.pyc` — incident disclosed above; end state
  `git status --porcelain --untracked-files=no` → empty.
- No other tracked file modified; no git mutation (no commit/push/checkout/
  stash); no product-code edit; no consumer re-run.

## Out-of-scope (explicitly not done)

- Implementing/repairing the r74 arms or any fixture/parser change (author's
  move; scribe seat forbids product-code edits). Findings F3/F5/F6/F7/F8 are
  reported for the author/critic/judge, not patched.
- Re-running any measurement (all raw inputs and receipts were already on
  disk; the audit spawned no real subprocess).
- Verification/adjudication (verifier/critic/boundary/reviewer/judge seats).
- Commit/push/publish (operator-owned).

## Artifact paths + hashes (snapshot)

- This report: `reports/round-74/r74-scribe.md`
- Scratch: `corpus/live/r74-scribe/parser_audit.py` (`8d49296e11f2520a…`),
  `audit-output.json` == `audit-stdout.txt` (`1216a0342b53b8a9…`),
  `receipt_hygiene.py` (`d97ddecba41e5382…`), `receipt-hygiene.json`
  (`3e5fd2adb7f9f5d7…`, 14 receipts), `watch.sh` (`70520111d1c0c49a…`),
  `landing-watch.log` (`ecec3aa3edb7a91c…`, 5 snapshots 15:22:14Z–15:25:13Z),
  `checks.txt` (`a87b5ba48090b163…`)
- Fixture: blob `9b6e836ebda4c0ce6bfedec281a6d8d14d4a91d8`, sha256
  `77f107864b74f794aea1d4fa8ea28f6f50d741591297dff192b9b6f949b2543b`
- Raw streams used: `corpus/live/frontier-pipewire/mpv-{file,fifo}-pair_dec_hcom.wav.log`,
  `mpv-file-{extsuffix_nomatch.wav,txw_piperefuse.wav}.log`,
  `pwcat-{file,fifo}-txw_piperefuse.wav.log`, `pwcat-fifo-empty.log`,
  `pwcat-nodaemon.log`
- Receipts: `corpus/live/runs/20261014T145502288182Z-consumers-r73`
  (`245dfa1a41131a55…` base), `…20261014T150305963053Z-consumers-r73`
  (`f1ddc75d…`, S-case), `…20261014T151240011154Z-consumers-r73`
  (`f6d5379a…`), `…20261014T152502427863Z-consumers-r73`
  (`9b422aa2…`, sibling replay at 15:25:02Z); all 14 listed in
  `receipt-hygiene.json`
- Pre-fix ASLR receipts: `20261014T014008064525Z` (`cacc5a19…`),
  `20261014T014058497253Z` (`8bea94e3…`), `20261014T014257840421Z`
  (`87fbd3be…`) — all `ui-preempt-gsrt-r65`
- Restored `.pyc` sha256: `9e333fe1ff95fdbaf9b481844f480c1ec7f5d8c9ccb1216236169dd6c02338ed`
- Prior-wave basis: `../shokunin-train-20261101-w12/xconnector.md`
  (X2/X3 arm ranking + scope guards); r73 reports in `reports/round-73/`
- Sibling r74 reports spot-checked (untracked; existence/hash only, not
  replayed): `reports/round-74/r74-scout.md` (`388bd35ea977e96b…`),
  `r74-critic.md` (`f502b3947b1be046…`)

## Exact commands / exits (appendix)

```sh
cd ~/Projects/shokunin/audio-shokunin
hostname; date; date -u                                    # plazir27; local 12:18–12:29 −03 == 15:18–15:29Z
git log --oneline -1; git status --porcelain --untracked-files=no   # 1ba8103; clean (0)
git hash-object corpus/fixtures/measure_audio.py           # 9b6e836… (== HEAD) at every check
grep -c 'r74' corpus/fixtures/measure_audio.py             # 0
ls corpus/live/runs | grep -c r74                          # 0
ls reports/round-74                                        # absent (until this report)
pw-cat --version; mpv --version; ffmpeg -version; sox --version   # 1.6.8 / v0.41.0 lavf 63.1.101 / n9.0.1 / SoX_ng 14.8.0.1
# parser audit (read-only; subprocess layer monkeypatched; python -B to avoid .pyc writes)
timeout 90 python3 -B corpus/live/r74-scribe/parser_audit.py   # exit 0; 27 cases -> audit-output.json
python3 -B corpus/live/r74-scribe/receipt_hygiene.py           # exit 0; 14 receipts, 10 sha groups
grep -rl "Detected file format" corpus/live/runs/*/measurements.json | wc -l   # 0 (no mpv log persisted)
grep -rl '0x[0-9a-fA-F]\{6,\}' corpus/live/runs/*/measurements.json | wc -l    # 18 (15 format_hex, 3 ASLR)
grep -rl '/home/vgpnk' corpus/live/runs/*/measurements.json | wc -l            # 399
git ls-files corpus/live/runs | grep -c consumers-r73      # 0 (family untracked)
git ls-files corpus/live/runs | sed 's|.*/runs/||;s|/.*||' | sort | tail -1    # newest tracked = 20261014T142733592435Z
git status --porcelain --untracked-files=all corpus/live/runs | wc -l          # 303 at 15:20Z, 305 at 15:25Z
# .pyc incident + restore
git cat-file blob HEAD:corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc > /tmp/r74-scribe-pyc-restore.bin
sha256sum /tmp/r74-scribe-pyc-restore.bin                  # 9e333fe1…
cp /tmp/r74-scribe-pyc-restore.bin corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc
git status --porcelain --untracked-files=no | wc -l        # 0
# S-case receipt inspection
python3 -B -c "…20261014T150305963053Z walk…"              # 36/36 pw-cat legs Host is down; pactl live=true; 5 ops failures
# landing watch
corpus/live/r74-scribe/watch.sh                            # 5 snapshots appended to landing-watch.log
```

Exit codes: all inspection commands exited 0 except documented absence probes
(`ls reports/round-74`, `grep -c r74` → 0) and the one deliberate
`git status` dirty window during the `.pyc` incident (restored). The audit
script's first run exited 1 twice on harness bugs of this seat's own script
(path base + exec indent), fixed before the recorded runs; the recorded runs
(`exit 0`) are the ones behind `audit-output.json`.

**Seat stop.** Report complete; no further action taken (leaf, no dispatch, no
commit).
