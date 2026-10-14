# R72 simplifier — no tracked deletion is possible this round (r72 arm unlanded at measurement; write scope = report + scratch only); five pre-landing deletion candidates measured: the `sndfile-info` CLI leg is dominated by the ctypes authority (frames line 512 ≠ read 500, cannot address 2 of 4 arms), the frontier template carries an unbounded >65536 B pipe pre-write plus two dead symbols, and the member-dict / member-file / builder copies are all avoidable; transport arms and frontier provenance ruled non-deletable; retained behavior proven (ctypes rerun == committed frontier matrix, 0/36 cell mismatches; prior-121 anchor hashed)

**Seat:** simplifier (delete-and-measure, not subjective trim). Lane: audio. Repo
`/home/vgpnk/Projects/shokunin/audio-shokunin`.
**State at measurement (2026-10-14 14:19–14:21 UTC):** HEAD `c079aba`; the r72 arm is
**not landed** — `grep -c sndfile corpus/fixtures/measure_audio.py corpus/fixtures/build_artifacts.py`
= `0/0`, `git diff --stat` empty, last probe flag still `--probe-ffprobe-transport-r71`
(`measure_audio.py:881`), no `sndfile_*` key in any `runs/*/measurements.json`. There is no
landed diff to delete from, and my write scope (`reports/round-72/r72-simplifier.md` +
`corpus/live/r72-simplifier/`) excludes the fixture. **Deletions made in the shared tree:
none.** Candidates below are pre-landing weight rulings, each with measured evidence;
none was applied anywhere outside scratch.
**LSP device — unavailable on this host/task (recorded per seat card).** Probed: no
`pyright`, `pylsp`, `python-lsp-server`, `jedi-language-server`, `lsp`, `lsp-server`
binaries; no `pygls`, no `jedi` importable; `clangd` exists but serves C-family only (this
surface is Python); the only MCP server (`rea`) is a Ghidra/Android/web RE toolkit with no
`references` device. Every "no callers" statement below is therefore **grep-literal
fallback, explicitly not semantic proof**.
**Toolchain:** libsndfile 1.2.2 (`/usr/lib/libsndfile.so.1` → `libsndfile.so.1.0.37`),
`sndfile-info`, Python 3.14.7, Linux x86_64.

## Deletion candidates (measured)

| # | Candidate (weight that would be *added*) | Measured effect | Ruling |
|---|---|---|---|
| C1 | A `sndfile-info` CLI leg in the tracked arm (the brief's "or `sndfile-info` 'frames' line" route) alongside the ctypes leg | Dominated — see below | **Do not add.** One authority: ctypes `sf_open`/`sf_open_fd` + `sf_readf_short` |
| C2 | A new `TRANSPORT_R72_MEMBERS` 9-entry dict | Duplicate member authority; r71 dict is already exactly the canonical 9 | **Do not add.** Reuse `TRANSPORT_R71_MEMBERS` (`measure_audio.py:556`) |
| C3 | Copied member files / a `build_*_r72*` builder arm | No new bytes exist; r71 added none; copies create two paths for the same bytes | **Do not add** |
| C4 | Copied protocol fields (`arm_timeout_s`, hardcoded fifo hold) | Records a bound that may not exist / drops the effective-hold record | **Record the real protocol; no new constants** |
| C5 | Verbatim copy of the frontier harness template | Carries an unbounded pipe pre-write (>65536 B blocks) and two dead symbols | **Write the tracked leg to the fixture's own bounded conventions** |

### C1 — the CLI leg is not a second opinion, it is a subset

The brief offers "the frontier seat's ctypes harness pattern **or** `sndfile-info` 'frames'
line" for the decode leg. Measured, those are not equivalent routes:

- **The CLI cannot address the anonymous arms at all.** `sndfile-info` takes paths only.
  The two anonymous transports (`stdin_pipe`, `redirected_fd`) are exactly the
  {anonymous} half of this round's `.snd` fork, which the frontier measured with
  `sf_open_fd` at the API boundary. The closest CLI approximation is a *named* path:
  `sndfile-info /dev/stdin < extsuffix_nomatch.snd` → `Format not recognised.` (exit 0) —
  i.e. it conflates "anonymous fd" with "named path lacking the fallback extension"; on
  `dec_act` both shapes open WAV 278 (`cli/info-devstdin-act.txt`). It coincides on this
  9-member set only; it does not measure the axis.
- **The CLI's `Frames` line is the length field, not a decode count.** Measured on the
  `.snd` member: CLI `Frames : 512` on the file arm vs `sf_readf_short` = **500** (the
  harness's own `frames=512`, `read_frames=500`); on the named-fifo arm the CLI prints
  `Frames : unknown` and no `Signal Max` line, while the API read returns 500
  (`cli/info-fifo-snd.txt`). A CLI-derived "decode verdict" would record 512/unknown where
  the read is 500 — the very thing the brief says needs `sf_read`.
- **The CLI exits 0 on every rejection** (measured 9/9 members, including the txw
  `File contains data in an unimplemented format.` tier) — an exit-code-checked leg
  silently passes; a stdout-parsed leg re-implements what `sf_strerror`/`sf_error_str`
  return directly.

Net: the ctypes leg covers **4/4 arms with read counts + `format_check` + seekability**;
a CLI leg covers 2/4 arms with no read count. Retained behavior is proven (see Preserved
contract). **Tradeoff:** none measured — the frontier's `logs/info-*.txt` remain as
corroborating provenance and are not deleted (R2).

### C2 — no second member authority

`TRANSPORT_R71_MEMBERS` (`measure_audio.py:556`) is exactly the canonical 9 paths the
frontier probed — path-equality check **9/9** (`members.tsv`; the frontier's key
`posttable` maps to `posttable_nomatch` by path). r71 itself built its dict by *reference*
to r68/r69/r67 entries — the established same-set convention. A copied 9-tuple dict would
be a second authority that can drift silently (the failure class the `mode`/`suffix`
chains already suffer, C4). Iterate `TRANSPORT_R71_MEMBERS` directly (or alias it by
assignment). **Tradeoff:** if a future round diverges the member set, the alias is a
one-line change; no divergence exists this round.

### C3 — no member copies, no builder arm

All 9 members exist with stable sha256 (`members.tsv`; the five extsuffix members are all
`f073e70a…` — the differing extensions *are* the contract, and those names already live in
`round-69/`). r71's arm added no builder call because no new bytes were needed; r72's set
is the same 9. A `round-72/` member dir or a `build_ui_*_r72_probe()` would create a
second path for identical bytes with zero new information.

### C4 — stale names to avoid in the receipt entry

- `transport_protocol.arm_timeout_s` (`measure_audio.py:712`) is meaningful only for a
  subprocess leg. If the ctypes leg runs in-process (frontier shape) the field would
  record a bound that does not exist. If a child-process wrapper is chosen to impose a
  wall-clock bound, reuse `TRANSPORT_R71_ARM_TIMEOUT_S` (`:567`, 15 s) — a new
  `TRANSPORT_R72_ARM_TIMEOUT_S = 15` is a duplicate constant with the same role.
- Fifo hold: the tracked convention is env-resolved and recorded (`fifo_writer_hold_s()`,
  `:284`) so an override is never silent; the frontier harness hardcodes `hold=1.0`
  (`probe_sndfile.py:100`). Copying the harness's fifo protocol loses the effective-hold
  record and the `MEASURE_FIFO_WRITER_HOLD_S` path. Reuse `fifo_feed` +
  `fifo_writer_hold_s()`; `reap_fifo_orphans` is subprocess-orphan machinery and is
  unnecessary for an in-process writer (keep it only if the child-process shape is used).

### C5 — frontier-template hazards measured (do not inherit verbatim)

- **Unbounded pipe pre-write.** `leg_fd`'s bytes branch (`probe_sndfile.py:118-124`)
  writes the whole payload before the reader attaches. Mechanism pinned:
  `os.pipe()` write of **65536 B completes; 65537 B blocks** (timeout 5 → exit 124).
  Whole-harness effect: a 200 KiB no-magic member → **exit 124 at 25 s** (no internal
  bound); the same harness on a 512 B member → exit 0. Dead for the current corpus (max
  member 600 B) but unbounded for any future member > pipe capacity. The tracked fixture
  already has bounded conventions: `subprocess input=` for stdin arms
  (`transport_leg`, `:253-258`) and the writer thread for fifo arms (`fifo_feed`,
  `:293-313`).
- **Dead symbols** (grep-literal, LSP unavailable): `SFC_GET_FORMAT_INFO = 0x1028`
  (`probe_sndfile.py:22`) — **0 uses**; `subprocess` import (`:17`) — **0 uses** (the CLI
  legs live in a separate shell runner). The 0x1030–0x1033 literals *are* used
  (`fmt_names()`); only the named constant and the import are dead. Don't carry them into
  the tracked fixture.

## Ruled-out deletions (stop condition reached)

- **R1 — dropping an anonymous arm.** `redirected_fd` vs `stdin_pipe` are identical under
  libsndfile (**0/9**) and ffmpeg (**0/9**, r71 receipt) — but sox forks **6 of 17**
  transport member receipts between them (dec_act, preempt_act/both/gsrt,
  lengate_gsrt_25, txw_piperefuse; `arm-loadbearing.txt`). Deleting the arm would erase 6
  measured sox rows and break 3-decoder comparability (the 2×2 transport space is the
  lane's cross-decoder contract). Not deletable.
- **R2 — frontier provenance.** `probe_sndfile.py`, `runs/`, `logs/`, `probes/` under
  `corpus/live/frontier-sndfile/` are this round's declared READ-FIRST evidence —
  protected ("never delete provenance explicitly marked historical"). The r72-*
  re-implementations are *verification* artifacts; independence is their point, not
  duplication.
- **R3 — merging the verdict-grouping loops.** The group-by-signature loop is duplicated
  between `transport_entry` (`:736-746`) and `ffprobe_transport_entry` (`:694-708`) and a
  third copy would follow; extracting a shared helper touches landed r67/r71 lines
  (non-additive) for ~8 lines saved — same ruling as r69-#12/#13; insertion-only is the
  round contract.
- **R4 — receipt key family.** `sndfile_{member}_r72_probe` matches the r71 family shape
  (`ffprobe_{member}_r71_probe`, `:1101`) and the frontier artifact naming — no collision,
  no rename.

## Preserved contract (retained behavior proven with the narrow existing check)

- **ctypes route == committed frontier matrix.** Rerun of
  `corpus/live/frontier-sndfile/probe_sndfile.py` on the canonical 9 into
  `rerun-matrix.json`, compared to `frontier-sndfile/runs/sndfile-matrix.json`:
  **0/36 cell mismatches** over 9 fields (format, format_name, format_check, frames,
  samplerate, channels, sf_seekable, read_frames, error) — `rerun-compare.txt`.
  The lattice facts the r72 receipt must reproduce (`rerun-summary.tsv`): dec_act /
  dec_hcom WAV/PCM16 278 on all 4 arms; txw `unimplemented format` on all 4; `.snd`
  U-Law 500 on {file, fifo_path} / reject on {stdin_pipe, redirected_fd}; posttable +
  extsuffix_{wav,bin,txw,f32} reject 4/4.
- **Member identity.** 9 paths + sha256 (`members.tsv`), 9/9 path-match to the frontier
  probed set.
- **Prior-121 anchor.** `prior-121-anchor.tsv` — all 121 `ledger-r71.tsv` receipt paths
  present with sha256 recorded, **0 MISSING** — a frozen pre-landing base for the
  post-landing "prior rows byte-stable" check (HEAD `c079aba`).
- **Tree identity.** `git diff --stat` empty; `git status --porcelain | grep -v '^??'`
  = 0 lines; every byte written by this seat is under `corpus/live/r72-simplifier/`
  (sibling `r72-*` scratch dirs appeared during the session and are not mine).

## Stop condition

The next deletion that would "remove weight" — dropping a transport arm (R1), dropping
the frontier provenance (R2), or refactoring the grouping loops (R3) — harms an axis
(cross-decoder comparability / provenance / insertion-only contract). Deletions
recommended for the tracked tree: **none possible** (arm unlanded; C1–C5 are items to
*not add*). Stop.

## Evidence index

- Scratch: `corpus/live/r72-simplifier/` — `head-at-start.txt`, `wt-status-at-start.txt`;
  `rerun-matrix.json` (`890743efe3b8…`), `rerun-compare.txt` (`6f621f0f2a75…`),
  `rerun-summary.tsv` (`c389bb270890…`); `members.tsv` (`57dcfc2914f7…`);
  `prior-121-anchor.tsv` (`2b4ca1777319…`); `arm-loadbearing.txt` (`d29a82454eae…`);
  `dead-symbol-scan.txt` (`a9a473933e3c…`), `dead-symbol-scan-frontier.txt`
  (`c09ed56db643…`); `cli/info-*.txt` (12 files: 9 members + `info-fifo-snd.txt` +
  `info-devstdin-{snd,act}.txt`); `big_nomagic.bin` (200 KiB), `big-run.json` (0 B —
  killed), `small_nomagic.bin` (512 B).
- Reference: `corpus/live/frontier-sndfile/runs/sndfile-matrix.json` (`466516f95486…`);
  `corpus/live/frontier-sndfile/probe_sndfile.py`; `reports/frontier/fa-sndfile.md`;
  `corpus/live/r70-author/ledger-r71.tsv`; `corpus/live/r71-author/{run_ledger,compare_receipts}.py`.

## Exact commands / exits (key legs)

```sh
cd ~/Projects/shokunin/audio-shokunin
# state
git rev-parse HEAD                                        # c079abaf… ; git diff --stat empty
grep -c sndfile corpus/fixtures/measure_audio.py corpus/fixtures/build_artifacts.py   # 0 0
# C1: CLI vs API on the .snd member
sndfile-info corpus/live/round-69/extsuffix_nomatch.snd   # exit 0; Frames 512 (API read = 500)
tmpd=$(mktemp -d); mkfifo "$tmpd/extsuffix_nomatch.snd"; (cat corpus/live/round-69/extsuffix_nomatch.snd > "$tmpd/extsuffix_nomatch.snd" &)
timeout 20 sndfile-info "$tmpd/extsuffix_nomatch.snd"                     # exit 0; Frames unknown
sndfile-info /dev/stdin < corpus/live/round-69/extsuffix_nomatch.snd      # exit 0; Format not recognised.
for m in round-68/posttable_nomatch.wav round-68/txw_piperefuse.wav round-66/pair_dec_{act,hcom}.wav \
         round-69/extsuffix_nomatch.{wav,bin,txw,f32,snd}; do sndfile-info "corpus/live/$m" > "…/info-$(basename $m).txt" 2>&1; echo "$m exit=$?"; done   # all exit 0 (incl. rejects)
# C5: unbounded pre-write
python3 -c "import os;r,w=os.pipe();os.write(w,b'x'*65536)"               # exit 0
timeout 5 python3 -c "import os;r,w=os.pipe();os.write(w,b'x'*65537)"     # exit 124 (blocked)
timeout 25 python3 corpus/live/frontier-sndfile/probe_sndfile.py '{"big":"corpus/live/r72-simplifier/big_nomagic.bin"}'  # exit 124
# preserved contract
python3 corpus/live/frontier-sndfile/probe_sndfile.py "$(cat corpus/live/r72-simplifier/rerun_members.json)" \
  > corpus/live/r72-simplifier/rerun-matrix.json            # exit 0, 9 s; compare → 0/36 mismatches
grep -n "SFC_GET_FORMAT_INFO\|subprocess" corpus/live/frontier-sndfile/probe_sndfile.py  # def/import only
```

All inspection commands above exited 0 unless the exit is stated (124 = timeout kill).
No git mutation, no fixture edit, no decoder run outside scratch.
