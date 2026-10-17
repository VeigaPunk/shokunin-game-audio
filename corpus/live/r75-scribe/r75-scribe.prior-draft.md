# R75 scribe (audio) — evidence ledger + raw/parsed audit (pre-landing snapshot)

**Headline:** the r75 author arm was **absent at every check** (0 `r75` refs in
the fixture, 0 r75 receipts, no `reports/round-75/` until this file, no r75
commit; HEAD `6f905c3` unchanged) while sibling scratch went active from
16:01Z. Because the r75 parser does not exist yet, this seat delivered the
two halves it can honestly own pre-landing:

1. **Raw-surface inventory of the three NEW consumers on this host**
   (`paplay`/`aplay`/`ffplay`, 15 bounded invocations, **no receipts**) — the
   *raw* half of the raw-vs-parsed audit, ready to be compared against the
   author's parser when it lands. Concrete results: ffplay is **rc=0 on
   invalid data** (2/2), aplay is **rc=0 on a text file and falls back to raw
   PCM playback** (`-q` erases the only witness), paplay's error surface is a
   single unprefixed line, ffplay's stderr is CR/ESC-interleaved and **not
   byte-stable across identical runs** (1–2 differing bytes), and the fixture's
   pw-cat daemon-severing trick (`PIPEWIRE_RUNTIME_DIR=<empty>`) **does not
   sever paplay**.
2. **A landed-family audit of the r74 `lavfsweep-r74` receipts the r74 scribe
   never saw** (they landed after its snapshot): 7 receipts / **4 distinct
   sha256 groups**, one of which carries a **superseded semantic leaf**
   (`fork_kind` `wound` → `truncation` for `lavf_iss_multi`, the adjudicated
   value), the author's cited receipt is **untracked in git** (the
   "committed receipt" wording drift **recurred**, `r74-author.md:74`), and
   every cited pin/member sha256 verifies.

Seat: **scribe** (leaf, report-only). Host `plazir27`; system clock
**2026-10-14 16:01Z** at open (**16:06Z** at final check, **16:07Z** at write;
local TZ = UTC−3 — `ls` mtimes are local, receipts are UTC; recorded, not a
defect claim). Wave label `shokunin-train-20261101-w14` (wave-name date ≠ clock
date — carried, recorded). Repo `/home/vgpnk/Projects/shokunin/audio-shokunin`,
HEAD **`6f905c3`** (2026-10-14 12:51:41 −0300) — unchanged all session.
Fixture `corpus/fixtures/measure_audio.py` blob
**`e3ef52e1e02c742d4f6dabda5c8658cc8f80a0bb`**, sha256
`317c0b486e103ac3eebc258e0c22c2cc623d3a3813f3ceae2c3d71b25f078f2e` (2879
lines) — byte-identical to HEAD at every check. Write scope: this report +
`corpus/live/r75-scribe/` only; no git mutation, no product-code edit, **no
probe mode run, no receipt written by this seat**.

## Mandate (verbatim, from the r75 scribe task)

*"Read SHARED.md + r75 author brief. Raw-stream vs parsed-view audit, receipt
hygiene, seat landings. Report -> reports/round-75/r75-scribe.md."*

## Landing state (watch snapshots 16:02:17Z, 16:02:19Z, 16:03:19Z, 16:04:19Z, 16:05:19Z + ad-hoc checks 16:03:44Z … 16:06:01Z)

| probe | state at every check |
|---|---|
| fixture `r75` refs (`grep -c 'r75'`) | **0** (author arm absent) |
| fixture `ffplay`/`paplay`/`aplay`/`SDL`/`ALSA` refs | **0 / 0 / 0 / 0 / 0** (no new leg, no device/driver gate exists yet) |
| fixture blob vs HEAD | `e3ef52e1…` == HEAD (clean) |
| r75 receipts (`ls corpus/live/runs \| grep -c r75`) | **0** |
| `reports/round-75/` | absent until this report |
| r75 commit | none (`git log --all`: newest `6f905c3`; `49747ba` = r74 report-last) |
| worktree (`--untracked-files=no`) | 1 modified: `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc` (sha `671711e2…`) — **already dirty at open** (mtime 15:32Z, pre-wave), untouched by this seat (verified before/after the audit import: same sha) |
| sibling scratch (landing-state only, never evidence) | `r75-author` (empty), `r75-baseline` (frozen/, pre-state, toolchain, committed-ledger-sha.before), `r75-boundary` (edge/, logs/, runs/, probe_boundary_r75.py), `r75-critic` (critic_probes.py + empty `20261014T160357Z-critic-probes/` dir), `r75-reviewer` (ops_probe{,2}.py/.json), `r75-scout` (fifo_cells.py, legs/, members.txt, probe-{aplay,ffplay,paplay}-*.txt, probe.sh, toolchain-gates.txt), `r75-simplifier` (17 files: baseline receipt copies, build_scratch_tree.sh, dead-symbol-scan-base.txt), `r75-scribe` (this seat) |
| sibling reports | **0** in `reports/round-75/` |

## §1 Raw-surface inventory — paplay / aplay / ffplay (scribe-side, NOT receipts)

Method: `corpus/live/r75-scribe/raw_surface.sh` + `raw_surface2.sh`
(`sha256 38239d59…` / `54f3e05b…`), all invocations wrapped in
`timeout -s KILL`, all on a synthesized 0.2 s mono silence
(`silence.wav`, sha256 `25692e7f…`) or a 19-byte text file misnamed `.wav`
(`noise.wav`, sha256 `13b518c8…`). Raw bytes in `corpus/live/r75-scribe/raw/`
(36 files). **Disclosure:** 4 `paplay`, 4 `aplay`, 7 `ffplay` invocations
reached the live audio stack (silence/text only, sub-second, `-q`/dummy-driver
where noted); the session daemon was never stopped, restarted or reconfigured —
gate probes only override child-process env. **No fixture mode ran; no receipt
was written.**

| consumer | version banner (this host) | positive surface (valid wav) | invalid-input surface | rc semantics |
|---|---|---|---|---|
| `paplay` | `pacat 17.0-98-gb096` / libpulse 17.0.0 | rc=0, **stdout 0 B, stderr 0 B** (no positive witness) | rc=1, stderr = `Failed to open audio file.` (1 line, **no `sndfile:`/`error:` prefix**) | rc distinguishes here (1 vs 0) |
| `aplay` | `aplay: version 1.2.16` | rc=0, `Playing WAVE 'silence.wav' : Signed 16 bit Little Endian, Rate 44100 Hz, Mono` | rc=**0**, `Playing raw data 'noise.wav' : Unsigned 8 bit, Rate 8000 Hz, Mono` (raw-PCM fallback, not an error); with `-q`: rc=0 and **0 B stderr** | **rc=0 is not a verdict** |
| `ffplay` | `ffplay version n9.0.1` (lavf 63.1.101) | rc=0, stdout 1 B (`\n`), stderr 2358 B / 15 lines (2331 B in the 3 repeats) | rc=**0**, `<path>: Invalid data found when processing input` (2/2 runs) | **rc=0 is not a verdict** |
| `ffplay` (SDL gate) | — | — | `SDL_AUDIODRIVER=bogus` → rc=1, `Could not initialize SDL - Audio target 'bogus' not available` + `(Did you set the DISPLAY variable?)` | gate = rc + the SDL line (the DISPLAY hint is a red herring) |

`aplay -l` on this host (the brief's viability precondition): card 0 `USB Audio`
devices 0–3, card 1 `HDA NVidia` HDMI 3/7/8/9, card 2 `HD-Audio Generic` HDMI
3/7/8/9 — a device **exists**, so the aplay arm is not `blocked` by absence
here; record the enumeration verbatim in the receipt.

**ffplay raw structure (byte-level, `cat -A` + binary scan):** the capture has
**8 CR, 15 LF, 1 `ESC[2K`**; the header is glued to a progress fragment:
`… sq=    0B \r\x1b[2K\rInput #0, wav, from '<path>':`. The fixture decodes
stderr bytes with `.decode(errors="replace")` (fixture `:1046`, `:1103`) —
**no universal-newline translation** — so a parser splitting on `\n` sees the
`Input #0` header inside a progress line; `str.splitlines()` (what
`_consumer_tail` uses, `:1014`) splits on CR, where the header **is**
line-initial. ffplay echoes the input **exactly as passed** (`noise.wav` in one
run vs `corpus/live/r75-scribe/raw/noise.wav` in another).

**ffplay run-to-run byte stability (3 identical commands):** same length
(2331 B), same fragment count (6), but sha256 differs every run — 1–2 bytes at
`M-A: -0.000` vs `M-A:  0.000` (sign of a tiny jittered value). The normalized
tail happened to be equal across these three (`   0.13 M-A:  0.000 …`), but the
**raw log is not byte-stable**; the ffplay progress fragment must not reach a
receipt as-is. The log also contains the literal tokens `nan` (1×) and
`0x0001` (`([1][0][0][0] / 0x0001)`) — see F8/F12.

## §2 Raw-vs-parsed audit — the production helper layer the new legs will inherit

Method: `corpus/live/r75-scribe/parser_surface_audit.py` (`73631bd0…`) imports
the fixture (blob pinned above, `python3 -B`; `.pyc` sha unchanged) and feeds
the **real raw streams** above through the **production** parse helpers.
Output `parser-surface-audit.json` (`8bfed3c5…`). Results (capability
demonstrations on real streams; not product claims):

| case | production call | result |
|---|---|---|
| `_consumer_tail` on a **valid** ffplay run (`:1010-1022`) | `_consumer_tail(text, silence.wav)` | `'   0.13 M-A:  0.000 fd=   0 aq=    0KB vq=    0KB sq=    0B'` — the **progress fragment**, a timing leaf |
| `_consumer_tail` on ffplay invalid / SDL-gate runs | same | the error line, **but** path normalization is a plain `replace(probe_arg, "<input>")`: it only fires when the probe passes the exact string form that appears in the log (`corpus/…/noise.wav` → `corpus/…/<input>: Invalid data…` vs `noise.wav` → `<input>: Invalid data…`) |
| `_pwcat_fields` (`:1024-1032`) on paplay / aplay / ffplay surfaces | same | **(None, None)** — the pw-cat extractor finds **nothing** on any of the three new consumers (no `sndfile:` / `error:` lines exist there) |
| consumer verdict-group key (`:1168-1170`) | source read | **binary branch on consumer name** (`"pw-cat"` → `(exit_code, sndfile_error)`, else → `(exit_code, lavf_detected, seek_failed)`); a third/fourth consumer added without extending the branch is silently keyed on the mpv signature |
| daemon-gate check (`:1255-1258`) | source read | `exit_code != 1 or "pw_context_connect" not in stderr_tail` — a **substring** check; the paplay analogue is `pa_context_connect` (one letter apart, see F7) |
| receipt writer (`:2871-2872`) | source read + verified | `json.dumps(…, allow_nan=False)` — a `float('nan')` anywhere in the receipt raises `ValueError: Out of range float values are not JSON compliant: nan` (**verified**); `out.mkdir(parents=True)` has **no `exist_ok`** (duplicate stamp ⇒ `FileExistsError`); `:2120-2121` (invalid mode) same shape |

## §2b Structural insertion-only check (the r75 author's coming edit)

The r74 edit added exactly **one** clause at the head of the `mode` and `suffix`
ternary chains (`:2846`, `:2866`) — verified by splitting both chains on
` else ` between the r74-scribe-era blob (`9b6e836e…`) and the current blob:
**117/117 prior clauses preserved verbatim and in order, 0 missing** in both
chains (118 clauses now). This corroborates the r74 author's *"each preserves
the prior expression verbatim"* claim structurally, and is the check the r75
`--probe-consumers2-r75` edit must pass too (a re-ordered or re-quoted clause
would silently change every prior mode/suffix).

## §3 Landed-family audit — `lavfsweep-r74` (the family the r75 arm extends; landed AFTER the r74 scribe snapshot)

Method: `corpus/live/r75-scribe/family_audit.py` (`1d31a4cb…`) →
`family-audit.json` (`af305eb3…`), read-only.

**7 receipts, 4 distinct sha256 groups** (all untracked; `git ls-files
corpus/live/runs | grep -c lavfsweep` → **0**):

| stamp (UTC) | sha256 (24) | bytes | fork_kind lattice | note |
|---|---|---|---|---|
| 15:30:27 | `5c9b4ab11a4c42cb69894d72` | 41476 | absent (pre-fold) | **the author report's cited receipt** (`r74-author.md:74,159`) |
| 15:30:53 | `d272a13fad2c5a8ebd74aa12` | 41476 | absent | differs from cited by 1 leaf (`target0.wall_s` 4.001 vs 4.002 — the verifier documented this) |
| 15:33:41 | `5c9b4ab11a4c42cb69894d72` | 41476 | absent | byte-identical to cited |
| 15:36:35 | `0c34e611c87c2f731e22979e` | 41671 | **`iss_multi='wound'`** | superseded classification |
| 15:37:39 | `ebddda2506212f2e004ae019` | 41676 | `iss_multi='truncation'` | matches the adjudicated value |
| 15:40:34 | `ebddda2506212f2e004ae019` | 41676 | same | verifier replay (per `r74-verifier.md:17-18`) |
| 15:41:38 | `ebddda2506212f2e004ae019` | 41676 | same | verifier replay |

- **The single semantic split:** leaf-diff `0c34e611` vs `ebddda25` = **exactly
  1 leaf**: `/measurements/lavfsweep_lavf_iss_multi_r74_probe/fork_kind`
  `'wound'` → `'truncation'` (the +5 bytes; the reviewer fold at
  `measure_audio.py:1700-1706`, comment *"Reviewer r74-F1: a measured
  head-truncation outranks the verdict-group wound label"*). The r74 verifier
  already recorded the pre-fold *citation* quirk (`r74-verifier.md:176-179`,
  verbatim: *"The author's cited receipt (`…T153027…`) is pre-fork_kind-fold;
  the newest committed-run receipt (`…T153739…`) is the correct byte-compare
  target and matches my replay exactly. Recorded as a citation quirk, not a
  defect — the report's measured VALUES are identical either way."*); this
  audit adds the **second axis** (a superseded *value*, not just a missing
  key) and the git-tracking fact.
- **Report pins verified against the cited receipt** (all match): iss
  `file rc=2`/`seek_failed=Operation not permitted`, `stdin_pipe rc=0`,
  `fifo_path rc=0`; acm `rc=0 + seek_failed=EPERM`; iss_multi extent
  **file 516196 B / 5.851791 s vs fifo 520260 B / 5.897868 s, delta 4064,
  truncated=true**; startpos **192068 B / 2.0 s vs 384068 B / 4.0 s**; ops-2
  escalation `exit_code=-9`/`sigterm_immune=true`, `--target 0`
  `exit_code=124`/`term_terminable=true`, raw name-axis **rc=0 on all three
  names**, zero-sink `audio_sink_count=0`/`-9`.
- **Member sha256 vs the `r74-author.md` table: 6/6 exact** (`4fbc2ca5…` iss,
  `85a518c8…` iss_multi, `684d2794…` apc, `5afaa65a…` acm, `3831ef47…` adx,
  `23aa8a65…` aifc). Members are **tracked** (committed in `168b165`); only the
  receipts are not.
- **Hygiene:** no `/home/vgpnk` and no `/tmp/` in any of the 7 (scratch
  `ao-pcm-file` path not embedded); stamp vs mtime 0.000301–0.001333 s; every
  entry `failures: []` (0 failures); the run's stdout summary is `{}` — the
  `failures: {}` in `r74-author.md:74` is the stdout line, consistent, not a
  drift.
- **Declared-protocol incompleteness (minor):** the entry's
  `transport_protocol.mpv` string (`"mpv --no-config --vo=null --ao=null …"`)
  describes the **axis** legs only; the extent legs actually run
  `--ao=pcm --ao-pcm-file=<scratch>` (`:1541-1559`) and that command is not
  declared in the receipt. Same class as the carried guard "wire order + write
  order both needed as witness": the receipt does not carry the argv that
  produced `pcm_out_bytes`.

## §4 `consumers-r73` family drift (16 receipts now vs 14 at the r74-scribe snapshot)

16 receipts, **11 distinct sha** (`family-audit.json`). New since the r74
snapshot: `20261014T153153302722Z` and `20261014T154324595001Z`, both
`ef2647b503bb4338` (65915 B) — a **new variant** whose leaf-diff vs the r73-era
base `245dfa1a…` is exactly **2 leaves**:
`/consumer_pwcat_ops_r73_probe/daemon_live/default_sink`
`alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink` →
`…HiFi__SPDIF__sink.2` (**a different sink instance name**) and
`pacing_instant/wall_s` 4.032 → 4.033. The r74-era S-case
(`…T150305963053Z`, `f1ddc75d…`, 36/36 pw-cat legs `Host is down` with `pactl`
live) is still present. Family-level aggregation must classify both the S-case
and the `default_sink` drift.

## §5 Global receipt hygiene (snapshot)

- Receipt population: **5615** dirs under `corpus/live/runs/`; **5290** tracked;
  **325** untracked entries; newest **tracked** receipt still
  `20261014T142733592435Z-sndfile-transport-r72` (the r74 families are
  on-disk-only).
- **ASLR scan** (`0x[12+ hex digits]`): **3 genuine leaks**, unchanged, all
  `ui-preempt-gsrt-r65` (01:40–01:42Z, pre-`50f55eb`), each a different
  address (`0x559e1fb98e40`, `0x558acfaebe40`, `0x5602c15ece40`) — prior rows
  frozen, recorded. The naive `0x[8+]` scan flags **21** files: those 3 plus
  **18** `sndfile-transport-r72` files whose `format_hex` values
  (`0x00010002`, `0x00040010`) are benign — the scan needs the two-class split.
- **Path embedding:** **399** receipts contain `/home/vgpnk/…` (invalid 107,
  r63 26, r64 90, r65 110, r66 61, normal 5) — legacy families, unchanged.
- **Timestamp semantics:** stamp == write time, stamp vs mtime ≤ 0.001333 s
  across the 7 new r74 receipts (matches the carried F12).
- **Carried worktree fact:** the tracked `.pyc` was **dirty at open** (sha
  `671711e2…`), i.e. the wave started on a non-clean `git status`; this seat's
  import (with `-B`) left it byte-identical.

## Findings reported verbatim for the canonical judge

- **F1 — "committed receipt" wording drift RECURRED in r74.**
  `r74-author.md:74`: *"## Measured (committed receipt
  `runs/20261014T153027827786Z-lavfsweep-r74`, `failures: {}`)"* and `:159`
  *"Receipt: `corpus/live/runs/20261014T153027827786Z-lavfsweep-r74/`"*.
  Actual: `git ls-files corpus/live/runs | grep -c lavfsweep` → **0**; the
  report-last commit `49747ba` touched `LOG.md`/`SCORECARD.md`/reports only.
  The **members** were committed (`168b165`), the **receipt** was not. Same
  class as the r74-scribe F1 (about r73); the ledger wording must be corrected
  in both places, or the convention changed deliberately.
- **F2 — the `lavfsweep-r74` family is semantically heterogeneous.** One leaf
  separates the 15:36:35 receipt (`fork_kind` `wound`) from the three
  byte-identical 15:37:39+ receipts (`truncation`, the adjudicated value). Any
  "receipts byte-identical ×N" or "family agrees" statement must name its
  receipts (the verifier named its replays; the adjudicator's
  *"receipts byte-identical ×3 including author's landed run"* is accurate only
  for the `ebddda25` triple).
- **F3 — the author's cited receipt is pre-fold** (corroborates
  `r74-verifier.md:176-179`, which already recorded it as a citation quirk).
  Measured values are identical across the fold; only `fork_kind` differs.
- **F4 — the inherited group-key branch is binary** (`:1168-1170`): a new
  consumer not added to the branch is keyed on the mpv signature. No guard
  exists that a leg's key matches its parser's fields.
- **F5 — `_consumer_tail` on a successful ffplay run returns the progress
  fragment** (measured: `'   0.13 M-A:  0.000 fd=   0 aq=    0KB vq=    0KB
  sq=    0B'`), and the raw ffplay log is **not byte-stable** across identical
  runs (1–2 bytes, `M-A: -0.000` vs ` 0.000`). A receipt built from that tail
  or that log inherits the instability; normalized fields must exclude the
  progress fragments.
- **F6 — rc is not a verdict for the new consumers** (carried guard, now
  instantiated): ffplay rc=0 on `Invalid data found when processing input`
  (2/2); aplay rc=0 on a text file (raw-PCM fallback `Playing raw data …`) and
  rc=0 with **0 B** stderr under `-q`; paplay is the only one whose rc
  distinguished (1 vs 0) on this surface.
- **F7 — the pw-cat daemon-severing trick does not transfer to paplay.**
  `PIPEWIRE_RUNTIME_DIR=<empty>` (fixture `:1236-1240`) → paplay **rc=0,
  silent success** (not severed). `XDG_RUNTIME_DIR=<empty>` → rc=1 with **2**
  stderr lines (`Connection failure: Connection refused` +
  `pa_context_connect() failed: Connection refused`; libpulse also creates
  `pulse/` inside the temp runtime dir). `PULSE_SERVER=nonexistent` → rc=1 with
  **1** line (`Connection failure: Connection refused`) — **no
  `pa_context_connect` token**. A gate copied from `:1255-1258` (substring
  `pw_context_connect`) would misread both mechanisms; and the paplay token
  `pa_context_connect` is one letter from `pw_context_connect`, so loose
  substring checks (`"context_connect"`) collide.
- **F8 — receipt-writer hazard: `allow_nan=False` + ffplay's literal `nan`
  token.** `json.dumps(…, allow_nan=False)` (`:2872`, `:2121`) raises
  `ValueError` on `float('nan')`/`inf` (verified); the ffplay progress fragment
  contains `nan`. An ffplay leg that parses that field into a float kills the
  whole run at write time (or must drop it).
- **F9 — ffplay stderr is CR/ESC-interleaved** (`\r\x1b[2K\r` before
  `Input #0`; 8 CR / 1 ESC[2K in the capture) and the fixture decodes stderr
  **without** universal-newline translation, so `\n`-splitting parsers see the
  header glued to a progress fragment while `str.splitlines()` sees it
  line-initial. Also: the input path is echoed **as passed**, and
  `_consumer_tail`'s plain `replace(probe_arg, "<input>")` only normalizes an
  exact string match (residual path prefix survives otherwise — the r74-scribe
  G4 hazard class).
- **F10 — no ALSA/SDL gate exists yet** (fixture refs 0). Host evidence for the
  aplay gate is captured above (`aplay -l` enumeration; a valid wav plays,
  rc=0) and should be recorded per-run, not assumed.
- **F11 — `daemon_live.default_sink` is daemon-state-dependent**: the new
  `ef2647b5` variant records `…HiFi__SPDIF__sink.2` where the r73-era base
  recorded `…HiFi__SPDIF__sink` (same host, same session). Not a stable
  invariance witness for byte-compares.
- **F12 — scan-class noise carried:** the `0x…` scan must separate genuine
  addresses (3, r65, frozen) from `format_hex` (18 files) — and the **new**
  ffplay surface adds a third class (`0x0001` inside the stream line).
- **F13 — wave-label vs clock** (`20261101` vs 2026-10-14) and **local TZ =
  UTC−3** carried. Recorded, not defect claims.

## Gates

| gate | state at final check (16:06Z) |
|---|---|
| author landing (`--probe-consumers2-r75` + receipts) | **ABSENT** — 0 refs, 0 receipts, no commit; `r75-author/` scratch empty |
| fixture / prior rows byte-stable | fixture blob `e3ef52e1…` == HEAD at every check; only the pre-existing `.pyc` dirty |
| r75 receipts | **0** |
| sibling seat landings | 7 scratch trees active (baseline/boundary/critic/reviewer/scout/simplifier/author-empty); **0 reports**; no commit |
| raw-surface inventory (this seat) | **DONE** — 15 bounded invocations, 3 consumers, 0 receipts, `raw/` 36 files |
| raw-vs-parsed audit (this seat) | **DONE** — production helpers on real raw streams; `parser-surface-audit.json` |
| landed-family audit (r74; this seat) | **DONE** — 7 receipts / 4 sha groups; F1–F3 |
| receipt hygiene (this seat) | **DONE** — global scans + family drift (§4–§5) |
| verifier replay / adjudication | not started (no r75 commit) |
| ledger drafts (LOG/SCORECARD) | **deferred** — nothing landed to record; snapshot only |

## LOG / SCORECARD draft

No r75 arm landed during this seat's window, so no ledger entry is drafted
(same convention as r74). When the author arm lands, the entry must carry: the
three consumers' per-member transport matrix + name-axis control, the
device/daemon/driver gates with their exact raw witnesses, the kill classes,
**plus** this seat's pre-landing hazard list (F4–F9) and the corrected receipt
wording (F1–F2).

## Touched surfaces

- Wrote **only**: `reports/round-75/r75-scribe.md` (this file) and
  `corpus/live/r75-scribe/{watch.sh, landing-watch.log, raw_surface.sh,
  raw_surface2.sh, raw/*, family_audit.py, family-audit.json,
  family-audit.stdout.txt, parser_surface_audit.py,
  parser-surface-audit.json}`.
- No tracked file modified by this seat; no git mutation (no commit/push/
  checkout/stash); no product-code edit; no fixture run; no receipt written.
- Live-stack disclosure (§1): bounded silence/text invocations only; child-env
  gate probes only; daemon untouched.

## Out-of-scope (explicitly not done)

- Implementing/repairing any r75 leg or fixture/gate change (author's move;
  scribe seat forbids product-code edits). F4–F9 are reported for the
  author/critic/judge, not patched.
- Re-running any probe mode or re-deriving any landed receipt (all receipts
  were already on disk; no measurement was replayed).
- Verification/adjudication of the r74 family or any sibling scratch
  (verifier/critic/boundary/reviewer/judge seats); sibling scratch is
  landing-state only.
- Commit/push/publish (operator-owned).

## Artifact paths + hashes (snapshot)

- This report: `reports/round-75/r75-scribe.md`
- Scratch: `corpus/live/r75-scribe/`
  - `watch.sh` `3c6a7e3b8a5771d302d3…`, `landing-watch.log`
    `df8ef1c9811fef5aab24…` (5 watch snapshots + ad-hoc checks)
  - `raw_surface.sh` `38239d595a630566be4a…`, `raw_surface2.sh`
    `54f3e05bae5b0a06eff5…`, `raw/` 36 files (incl. `silence.wav`
    `25692e7f…`, `noise.wav` `13b518c8…`, `rep-{1,2,3}.stderr` ffplay
    repeats, `pp{1,2,3}.{out,err}` paplay gate probes)
  - `family_audit.py` `1d31a4cbb4b3207d1dc5…`, `family-audit.json`
    `af305eb36fdf4cde0305…`, `family-audit.stdout.txt`
  - `parser_surface_audit.py` `73631bd0c1868e99b2f8…`,
    `parser-surface-audit.json` `8bfed3c5daedf6303561…`
- Fixture: blob `e3ef52e1e02c742d4f6dabda5c8658cc8f80a0bb`, sha256
  `317c0b486e103ac3eebc258e0c22c2cc623d3a3813f3ceae2c3d71b25f078f2e`
- r74 family receipts: `corpus/live/runs/{20261014T153027827786Z,
  20261014T153053003782Z, 20261014T153341301201Z, 20261014T153635661704Z,
  20261014T153739783116Z, 20261014T154034384723Z,
  20261014T154138420733Z}-lavfsweep-r74/measurements.json` (all untracked)
- Members: `corpus/live/round-74/lavf_{iss.iss,iss_multi.iss,apc.apc,acm.acm,
  adx.adx,aifc.aifc}` (tracked in `168b165`)
- Sibling scratch spot-checked (existence only, untracked, not replayed):
  `corpus/live/r75-{author,baseline,boundary,critic,reviewer,scout,simplifier}/`
- Prior-wave basis: `../shokunin-train-20261101-w12/xconnector.md`; r74 reports
  in `reports/round-74/`

## Exact commands / exits (appendix)

```sh
cd ~/Projects/shokunin/audio-shokunin
hostname; date; date -u                                   # plazir27; local 13:01–13:07 −03 == 16:01–16:07Z
git log --oneline -1; git status --porcelain --untracked-files=no  # 6f905c3; 1 (tracked .pyc, dirty at open)
git hash-object corpus/fixtures/measure_audio.py          # e3ef52e1… (== HEAD) at every check
grep -c 'r75' corpus/fixtures/measure_audio.py            # 0
grep -c 'ffplay\|paplay\|aplay' corpus/fixtures/measure_audio.py   # 0 / 0 / 0
ls corpus/live/runs | grep -c r75                         # 0
ls reports/round-75                                       # absent (until this report)
which paplay aplay ffplay                                 # all present (/usr/bin/…)
aplay -l                                                  # card 0 USB Audio 0–3, card 1/2 HDMI (exit 0)
bash corpus/live/r75-scribe/raw_surface.sh                # exit 0; raw/ inventory (15 invocations)
bash corpus/live/r75-scribe/raw_surface2.sh               # exit 0; error/gate surfaces
python3 -B corpus/live/r75-scribe/parser_surface_audit.py # exit 0; production helpers vs raw streams
timeout 300 python3 -B corpus/live/r75-scribe/family_audit.py  # exit 0; 7 r74 receipts, 16 r73 receipts
sha256sum corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc  # 671711e2… before AND after the import
git ls-files corpus/live/runs | grep -c lavfsweep         # 0 (cited receipt untracked)
git ls-files corpus/live/runs | sed 's|.*/runs/||;s|/.*||' | sort -u | tail -1  # newest tracked 20261014T142733592435Z
git status --porcelain corpus/live/runs | wc -l           # 325 untracked entries
# gate probes (child-env only; daemon untouched)
env PIPEWIRE_RUNTIME_DIR=<empty> paplay silence.wav       # rc=0 (trick does NOT sever paplay)
env XDG_RUNTIME_DIR=<empty> paplay silence.wav            # rc=1; "Connection failure…" + "pa_context_connect() failed…"
env PULSE_SERVER=nonexistent paplay silence.wav           # rc=1; single line, no pa_context_connect token
# ffplay repeats (determinism)
for i in 1 2 3; do SDL_AUDIODRIVER=dummy timeout -s KILL 20 ffplay -nodisp -autoexit -vn -loglevel info silence.wav 2>rep-$i.stderr; done
                                                          # rc=0 ×3; equal lengths, DIFFERENT sha256 (1–2 bytes)
```

Exit codes: all inspection commands exited 0 except documented absence probes
(`grep -c r75` → 0, `ls reports/round-75` → 2) and the intentional `rmdir` of a
temp runtime dir left non-empty by libpulse's `pulse/` subdir (exit 1,
removed with `rm -rf`; nothing in the repo touched). The `aplay` invalid-input
run is the one *non-zero-free* semantic surprise: rc=0 with a raw-PCM fallback
line (F6).

**Seat stop.** Report complete; no further action taken (leaf, no dispatch, no
commit).
