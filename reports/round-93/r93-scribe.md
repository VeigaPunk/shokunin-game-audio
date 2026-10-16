# r93 scribe — report → receipt → author bytes → integrated bytes → pin chain audit

Seat: **scribe**, round **93**, wave `shokunin-train-20261016-w24`. Leaf member,
read-only audit; no live family run (the round's single live run belongs to its
verifier lane), no source edits, no subagents, no commits.

- **Source pin:** `bb177513a615a32d3bc150ecbdcf78302e110d8c` — verified: it is
  HEAD of `main` in `/home/vgpnk/Projects/shokunin/audio-shokunin`
  ("r99 safety: require explicit opt-in before physical LAN control",
  2026-10-16 09:29:41 −0300). Tracked tree at HEAD is clean
  (`git status --porcelain` shows only untracked evidence: worktrees,
  `corpus/live/**` receipts, locks, Timing plots).
- **Scope:** the r93 `ebur128` family chain only — the three round-93 reports
  (scout/boundary/author), the author's receipts, the author worktree bytes,
  the integration stage, the integrator's final-byte run, and the pin. r98/r99/
  r100 chains are other seats' rounds and were not audited.
- **LSP:** not used; all inspection is literal (grep/byte comparison). No
  finding below claims semantic proof from grep alone.

## 1. Commands actually executed (all read-only)

`git rev-parse`/`log`/`show`/`status`/`worktree list`/`ls-tree`/`diff` on the
audio repo and the `wt-r93` worktree; `sha256sum` on the pinned source, the
author worktree source and report, `build_artifacts.py`, the 14 WAVs and the
battery receipts; `git show <commit>:corpus/fixtures/measure_audio.py |
sha256sum` at 753f13a6/63b81d07/74b75fce/81a5b55d/193acbed/bb177513; Python
JSON reads (structure, counts, field values — no measurement recomputed) of six
author-side receipts and the integrator's T1219 receipt; `.pyc` header parse;
`grep` token checks against the pinned source; citation greps into the
scout/boundary reports; `stat` mtimes; one read-only environment check
`timeout 15 pactl info` (rc 0 — daemon answering, PulseAudio on PipeWire 1.6.8,
host `plazir27`; nothing restarted). Full log and hash tables:
`/home/vgpnk/Projects/shokunin/audio-waveb-resume/r93-scribe/evidence-notes.md`.

## 2. Findings, by severity

### F1 (moderate, observed) — pin bytes ≠ author-tested bytes at file level; family block verbatim at every stage

- **Where:** `corpus/fixtures/measure_audio.py` at the pin vs the author's
  recorded implementation hash (`reports/round-93/r93-author.md` §6, line 240).
- **Failure path:** a reader who verifies the author's §6 hash
  `62e2606ebeb8f1d93…` against the pin gets a mismatch: the pin's file hashes
  `801e153b84368bba…`. The two green batteries ran on the author worktree bytes
  (`audio-shokunin-wt-r93` @ `5a632a4f`, file hashes exactly `62e2606…` — the
  §6 hash is genuine), and the integrator's final-byte run (T1219) ran on
  `5c8f7e9d…` (the r100-final source). Three different file hashes for one
  family.
- **Evidence:** the r93 family block — the 1995 inserted lines (wt new-side
  30983–32977), sha256 `32061b8c5b160433…` — is a byte-identical contiguous
  match in **all five** surfaces: author worktree, `74b75fce` (r93 integrate),
  `81a5b55d`, `193acbed` (the bytes T1219 actually ran on), and the pin. The
  file-level deltas are base drift (r90 fold, r98 family, r99/r100 families)
  plus wiring and the post-run r99 safety edit. The integration note's stage
  hash table (`reports/round-100/r93-r99-r100-integration.md` lines 12–17)
  verifies exactly against the fixture blobs at those commits.
- **Smallest correction:** none required if the lead accepts block-granularity
  identity (the greens transfer to the pin's family code verbatim); otherwise
  the assigned r93-verifier run on the pin bytes is the direct closure. State
  the granularity explicitly wherever the chain is summarized.
- **Observed** (byte comparisons), not inferred.

### F2 (moderate, observed) — §5.4 attributes bug #3 (l2g) to the 10:02 run; that receipt shows the fix already in place

- **Where:** `reports/round-93/r93-author.md` §5.4 (lines 212–233).
- **Failure path:** §5.4 says the 10:02 run "failed exactly four arms",
  including the lufs2gain double-meter bug ("the graph refused `l2g:LUFS` with
  unknown input port"). The 10:02 receipt
  (`wt-r93/corpus/live/runs/20261016T100229270710Z-ebur-r93/measurements.json`)
  substantiates bugs #1 (`topo_load` ×2, "got [7, 7, 0, 7]" against the mistyped
  `[7,7,7,7]` expectation — measurement already correct), #2 (12
  "feed link never bound (cls=ebur_r93_feed_refused)" coverage records across
  channel/peaks) and #4 (`e_bad_history` ×1) — but shows **no** buggy l2g
  declaration: all 9 of its `name=l2g` occurrences already read
  `label=lufs2gain`, the gain-leg loads are clean, and `g_target0` stats are
  identical to the greens. "Exactly four arms" also does not match the
  receipt's census (2 failure keys / 3 failure records + 12 feed-link coverage
  records).
- **Evidence:** the bug's actual exposure artifact exists —
  `wt-r93/corpus/live/r93-author/dev/dev4.json` (mtime 05:59:11 −0300 =
  08:59:11 UTC, mid-wedge): 4 × `name=l2g,label=ebur128` (buggy bytes) + 1 ×
  `label=lufs2gain`, with `[E] … parse_link()] unknown input port l2g:LUFS`
  refusal lines.
- **Smallest correction:** reword §5.4 to attribute bug #3 to the dev-probe
  phase (dev4.json) and count arms per the receipt census. The bug is real,
  evidenced and fixed before the greens; only the run attribution is imprecise.
- **Observed.**

### F3 (minor, observed) — §2.3's `unloads[*].exit_code == 0` does not exist in the receipt schema

- **Where:** `reports/round-93/r93-author.md` §2.3 (line 84).
- **Evidence:** in both green batteries and T1219, entry-level `unloads` is a
  name-keyed record `{verified_index: null, captured: …, field: "sink_name",
  value: "r93a_<pid>_in", skipped: "not_listed"}` — no `exit_code` field; the
  leg-level `unload` record is `{var, error_class, error_hit, lines}` with
  `error_class: null` on all 83 dict records (7 legs `unload: null`). The
  receipt's 184 `exit_code: 0` live in link/load/notify records; its 8
  `exit_code: 1` are `pre_stop`/`post_stop` tap-stop records on
  `m_window_only`/`m_momentary_only`/`g_default` legs — not unloads.
- **Smallest correction:** cite the fields that exist (`legs[*].unload.
  error_class == null`, `unloads[*].skipped == "not_listed"`, `sinks_gone`
  all-true, empty `own_nodes_after`/`own_procs_after`). The teardown substance
  is receipt-backed; the field citation is not.
- **Observed.**

### F4 (minor, observed) — stale line count in §6

`reports/round-93/r93-author.md` §6 (line 241) says the implementation change
is "+2035/−3"; §1 (line 20) says "+2056/−3". Measured: the author diff vs its
base `5a632a4f` is **+2056/−3** (1995-line block + 56-line dispatch block + 1
argparse row + 1 `import math` + 3 wiring rewrites; 149 of the added lines are
blank), and integration commit `74b75fce` is +2056/−3. §6's "+2035" is stale.

### F5 (minor, observed) — receipt-copy paths resolve only in the author worktree

§1 lists `corpus/live/r93-author/runs|probes|dev|stim` as changed paths. In the
main repo / at the pin, `corpus/live/r93-author/` **does not exist**; the
copies (and the batteries themselves) live only under
`/home/vgpnk/Projects/shokunin/audio-shokunin-wt-r93/corpus/live/…`. The report
names its worktree at the top, so this is a locator nuance, not a false claim —
but a pin-side reader following §1's paths finds nothing. The byte-identity of
the copies was verified (battery #1: `5e68daa7…` in both locations).

### F6 (minor, observed) — one gate-blocked attempt is uncited and uncopied

§5.3 cites two blocked attempts (`092003125628Z`, `092216336849Z`); disk has a
third, `20261016T092620653912Z-ebur-r93` (09:26 UTC, after the 09:24:59 daemon
recovery — the gate blocked again), with the same
`ebur_r93_daemon_unavailable` / `ready: false` / `pactl_exit −9` /
`pw_dump_bytes 0` / 0-legs shape. It is absent from §5.3 and from the
`r93-author/runs/` copy set. Honest evidence exists on disk; the report
under-cites it by one.

### F7 (info, observed) — receipt hash scope covers stimuli, not the source

Every entry's `stimuli` table carries all 14 member sha256s at full precision,
and each matches the actual WAV bytes (checked against the T1219 receipt and
the files in both worktree and main repo — byte-identical everywhere). The
receipts record **no** fixture-source sha256, so the receipt→source binding
rests on the reports' claims plus the integration note's stage table (which
verifies, F1). The author's §3.1 "sha256 recorded in every receipt" is true for
stimuli only.

### F8 (info, observed) — stale tracked `.pyc` at the pin

`corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc` is tracked and
clean at HEAD, but its header embeds `src_size 533517` /
`src_mtime 2026-10-15T05:53:24Z` — the r78-era source (commit `a005e1e4`,
source size 533517) — vs the pin source's 2,766,373 bytes; the cached blob
contains no `ebur_r93` string. Python recompiles on mtime/size mismatch, so no
runtime effect (and the verifier recipe sets `PYTHONDONTWRITEBYTECODE=1`). The
author's §1 disclosure about the regenerated `.pyc` is accurate for the
worktree (`wt-r93` shows it modified, uncommitted).

### F9 (info, observed) — integration-note wording: "byte-identically" is slice-true, not file-true for r93

`reports/round-100/r93-r99-r100-integration.md` line 23–24 says the two
supporting Python fixtures and all three author reports "compare
byte-identically against their author worktrees". True for
`build_artifacts.py` (`8ce62990…` wt==pin) and the r93 author report
(`e4e3de7a…` wt==pin — no post-authoring edit). **Not** file-level true for
r93's `measure_audio.py` (`62e2606…` vs stage `59708fca…`) — true only at the
family-slice level (`32061b8c…`), which the note's own stage table documents.
Advisory wording fix only; the note was not edited.

### F10 (info, observed) — T1219 provenance rests on the note's citation

The integrator's final-byte receipt
(`corpus/live/runs/20261016T121901064467Z-ebur-r93/measurements.json`, main
repo, mtime 12:19 UTC — 10 min before the pin commit) carries no seat/argv
identity; its content matches the note's r93 bullet verbatim (9 entries, 90
legs, no entry failures, `notify_bogus` + `g_default` coverage-blocked with the
g_default message twice, all nine censuses empty). It predates the r93-verifier
lane's scratch (created 09:38 local), so it is not the verifier's run.

## 3. What the evidence supports (blocked vs measured)

- **Measured (receipt-backed, both author batteries and T1219 agree):** 9
  entries / 90 leg keys (cal 9, channel 10, error 14, gain 9, history 8, modes
  11, peaks 6, topology 17, window 6); `failures: {}`; coverage blocked on
  exactly the two disclosed sub-arms — `g_default` audio-domain ratio
  (per-rep tap RMS recorded: pre 0.20658457 / 0.20976177 vs post 0.0, matching
  the report's "pre≈0.207") and `notify_bogus` load refusal
  (`cls=pwcli_module_load_fail`, `control_class` recorded). Teardown censuses
  empty and `sinks_gone` all-true in all 27 entry-records. Window decays
  identical across batteries at field level (`decay_s`: 0.427 ×2, 1.856 ×2,
  absent → None). Headline constants reproduce identically across batteries
  (spot-checked substring counts for −9.024196/−3.003596/−15.044795/−19.024195).
- **Measured (byte-backed):** the family block is verbatim at every stage
  (F1); the 14 analytic WAVs are byte-identical across surfaces and match the
  receipts' full-precision hashes (F7); the author report is unedited between
  worktree and pin; the author's "zero commits" is true (two modified tracked
  files in `wt-r93`, both disclosed in §1).
- **Source-linked at the pin:** daemon gate, `EBUR_R93_STIM_DIR =
  ROOT/"live"/"round-93"`, the fixed family lock path (lock file present in
  both repos, untracked), `allow_nan=False` ×8, six refusing arms via two
  `expect_refusal=True` sites (one inside the 5-label loop), `PIPEWIRE_DEBUG`,
  seat-owned `r93a_<pid>` names, the private `r93arole<pid>` key, and
  "never set-default-*" as a comment with no such call in the block. No
  `def *_ebur_r93*` name exists in the pre-r93 base (0 vs 53 in the pin) —
  the no-collision claim is source-consistent.
- **Blocked (not re-run, by role):** no measurement was recomputed and no
  family was executed by this seat; the daemon-gate behavior, the K-weighting
  arithmetic and the boundary's libebur128 witness were checked only as
  citation resolution (boundary lines 70/78/79/83 and scout lines 60/65/168
  contain the cited values; scout/boundary reports are tracked, added by
  `1e88e8e2`/`b5d0f673`).

## 4. Residual risks and explicit checks not run

- The single live `--probe-ebur-r93` run on the **pin** bytes belongs to the
  r93-verifier lane (its scratch existed at dispatch); this report pre-dates or
  is parallel to that run and does not cite it.
- The raw substring count of "1.856" differs by one between the two battery
  files (70 vs 69); resolved as irrelevant at the `decay_s` field level, not
  chased to the differing series value.
- The 9th `name=l2g` occurrence (all 9 sit in the gain entry) was not
  itemized per leg.
- `pactl info` was run once as a read-only environment observation; no
  `pw-dump`, no load/unload, no fixture execution.
- The dev-probe JSONs (dev1–dev7) were not audited beyond dev4's bug-#3
  evidence; the r93 scout/boundary receipts (`receipts/stereo.json` etc.) were
  not opened — their report tables were citation-checked only.
- Whether the pulse *module* listed in the author's §5.2 residual was ever
  removed is unresolved by this seat (the author disclosed it as
  unresolvable while `pactl` was down).

## 5. Artifact paths and attribution

- **This report:** `/home/vgpnk/Projects/shokunin/audio-shokunin/reports/round-93/r93-scribe.md` (the only report file this seat wrote).
- **Scratch/evidence log:** `/home/vgpnk/Projects/shokunin/audio-waveb-resume/r93-scribe/evidence-notes.md` (hash ladder, receipt censuses, token checks, command log).
- **Audited inputs (read-only, none modified):** `reports/round-93/{r93-scout,r93-boundary,r93-author}.md` (tracked; scout/boundary added at `1e88e8e2`/`b5d0f673`, author at `74b75fce`); author receipts and dev probes under `/home/vgpnk/Projects/shokunin/audio-shokunin-wt-r93/corpus/live/…`; integrator receipt `corpus/live/runs/20261016T121901064467Z-ebur-r93/` in the main repo; `reports/round-100/r93-r99-r100-integration.md`; pinned source at `bb177513`.
- **Attribution:** r93 family, report and receipts — the r93 author seat (worktree `wt-r93` @ `5a632a4f`, bytes `62e2606…`); integration and final-byte run — the orchestrator's integration lane (commits `74b75fce`/`81a5b55d`/`193acbed`, run T1219 on `5c8f7e9d…`); pin — the r99 safety commit `bb177513`. All receipts cited are local frozen evidence; none is claimed committed or remotely available. The WAVs and lock files are untracked local evidence.
- **No shipping or gate-admission decision is made or implied by this report.**
