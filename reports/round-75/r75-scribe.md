# R75 scribe (audio) — evidence ledger + raw/parsed audit (recovery generation)

**Headline.** The r75 author arm **landed in the worktree during this seat's
window** (first edit visible 16:39:27Z; 3 canonical `consumers2-r75` receipts on
disk by 16:44:18Z; HEAD still `6f905c3` — **uncommitted**, no `r75` commit yet).
This seat audited the landed arm end-to-end on the two revisions it could pin:

1. **Revision A (`b057bab6b367`, 16:40:12Z, sha256 `a56107f4…`)** — audited with
   fresh bounded runs using the new legs' exact argv shapes. **F17 confirmed:**
   the aplay/ffplay file-arm `stderr_tail` leaked the absolute host path
   (`_consumer_tail` was handed the *relative* label while the consumer echoed
   the *absolute* argv). The **first canonical receipt
   (`20261014T164125737824Z-consumers2-r75`) carries exactly that leak — 16
   path-bearing tails + `/tmp/` mkdtemp residue**.
2. **Revision B (`b0153958c28d`, 16:45:27Z, sha256 `545c9fe1…`)** — the author
   added `_consumer2_tail` (quoted-path + residual-prefix scrubbing) and
   `_PACAT_RACY_TAIL`. Re-audited: **the path leak is fixed** (the two post-fix
   receipts are path-clean, `hostpath=False tmp=False`), with one **cosmetic
   residue** (`Playing WAVE <input>' : …` — a stray opening-quote survivor,
   F17b), and one **live instability that survives the fix**: the pacat racy-tail
   filter is anchored `^Time:.*Latency:$` but the real pacat line is
   `Time: 0.040 sec; Latency: 159959 usec.` → unfiltered; the two post-fix
   receipts differ in **exactly one leaf**, the paplay `fifo_path` tail
   (`'Draining connection to server.'` vs `'Time: 0.000 sec; Latency: 34750
   usec.'`) — **F21**; a 4th receipt (16:46:03Z) extends the picture: **every**
   inter-receipt leaf delta in the post-fix family is a `stderr_tail` string
   (54 / 1 / 12 leaves for 1→2 / 2→3 / 3→4), including the ffplay progress
   fragment carrying `nan` (F22), the ALSA underrun line (F23) — the family is
   **field-stable but not byte-comparable** (F24, §6.5).

Seat: **scribe** (leaf, report-only). Host `plazir27`; kernel `7.2.3-arch1-3`;
Python 3.14.7. Clock: **16:29Z** at open, **16:45Z** at write (local TZ = UTC−3;
`ls` mtimes are local, receipt stamps UTC — recorded, not a defect claim). Wave
label `shokunin-train-20261101-w14` (wave-name date ≠ clock date — carried).
Repo `/home/vgpnk/Projects/shokunin/audio-shokunin`. HEAD **`6f905c3`**
(unchanged all session; reflog top `6f905c3`). Baseline fixture blob
**`e3ef52e1e02c742d4f6dabda5c8658cc8f80a0bb`** (sha256
`317c0b486e103ac3eebc258e0c22c2cc623d3a3813f3ceae2c3d71b25f078f2e`, 2879
lines) — the pre-landing audit (§1–§5) is pinned to it; §6 is pinned to the two
landed revisions above. Write scope: this report + `corpus/live/r75-scribe/`
only; no git mutation, no product-code edit, **no probe mode run, no receipt
written by this seat**.

## Supersession record

- Superseded: `reports/round-75/r75-scribe.md` (27948 B, sha256
  `de7c6b35a677b3a2e9f64af307597c56ffff0a2652d1e76e76a7693110aa5beb`),
  uncommitted 16:06Z pre-landing snapshot of the dead generation; preserved at
  `corpus/live/r75-scribe/r75-scribe.prior-draft.md` (same sha).
- Carried forward **verified**: §1 raw-surface inventory (F6/F7 re-measured),
  §2 helper-layer audit (JSON byte-identical on re-run), §3 lavfsweep-r74 family
  (re-run identical; 1-leaf semantic split re-derived), §4 consumers-r73 drift,
  §5 global hygiene. Added: §6 (landed-parser audit), F17–F21, three corrected
  line citations (verdict-group key `:1173-1174`, daemon gate `:1254-1256`,
  reviewer fold `:1705-1708`; the dead draft cited `:1168-1170`, `:1255-1258`,
  `:1700-1706`).

## §0 Landing timeline (this generation)

| UTC | HEAD | fixture blob | `r75` refs | r75 receipts | reports/round-75 | notes |
|---|---|---|---|---|---|---|
| 16:29:41–16:38:42 | `6f905c3` | `e3ef52e1e02c` | 0 | 0 | — | author absent; sibling scratch active; boundary/scout scratch growing |
| 16:39:27 | `6f905c3` | `793e3d958bd0` | **27** | 0 | r75-boundary.md, r75-scribe.md | **author arm lands in the worktree** (uncommitted) |
| 16:40:12 | `6f905c3` | **`b057bab6b367`** (sha256 `a56107f4…`) | 27 | 0 | +r75-scout.md | revision **A** audited by this seat (§6) |
| 16:43:12 | `6f905c3` | `ce2b6c1560ca` | 28 | **1** | 3 reports | first canonical receipt `…T164125737824Z` (written 16:41:25Z, pre-fix revision) |
| 16:44:18 | `6f905c3` | `ce2b6c1560ca` | 28 | **3** | 3 reports | receipts `…T164319396674Z`, `…T164418398152Z` |
| 16:45:27 | `6f905c3` | **`b0153958c28d`** (sha256 `545c9fe1…`) | 28 | 3 | 3 reports | revision **B** (fix) audited by this seat (§6) |
| 16:46:03 | `6f905c3` | `b0153958c28d` | 28 | **4** | 3 reports | receipt `…T164603163948Z` (`3b91594b…`) — §6.5 family-stability delta |

- `corpus/live/r75-author/` stayed **0 files** throughout (the author seat's
  scratch is empty; its artifacts are the fixture edit + the receipts).
- Landing poll: `corpus/live/r75-scribe/poll-landing.sh` + `landing-watch.log`
  (45 s cadence, 16:29:41Z → 16:45:27Z; dead-seat snapshots 16:02–16:10Z
  precede them). No new commit at any check (`git log 6f905c3..HEAD` = 0).
- Sibling reports landed: `reports/round-75/r75-boundary.md` (16:35Z),
  `r75-scout.md` (16:36Z) — landing state only, not evidence here.

## §1 Raw-surface inventory — paplay / aplay / ffplay (scribe-side, NOT receipts)

Method: dead-seat `raw_surface.sh` (`38239d59…`) + `raw_surface2.sh`
(`54f3e05b…`) + this generation's `reverify.sh`
(`bd40511cc554ede2c33150e7a304cd6f39f95894fd51a769985d10a1447fa13e`), every
invocation under `timeout -s KILL` (carried guard), inputs = 0.2 s mono silence
(`raw/silence.wav`, `25692e7f…`) or an 18-byte text file misnamed `.wav`
(`raw/noise.wav`, `13b518c8…`). `raw/` holds 60+ files now (36 dead-seat, 12
reverify, 8 new-parser runs, 4 leg-composition/ops-tail logs). **Inventory:** 26
bounded invocations by the two scribe generations (16 consumer runs, 3 version
banners, 1 `aplay -l`), plus §6's 8 new-parser runs. **Disclosure:** sub-second
silence/text only; daemon never stopped/restarted/reconfigured; child-env
overrides only; **no fixture mode run, no receipt written by this seat**.

Daemon context (`pactl info`, 16:30Z): `PulseAudio (on PipeWire 1.6.8)`, proto
35, `Is Local: yes`.

| consumer | banner | positive (valid wav) | invalid input | rc semantics |
|---|---|---|---|---|
| `paplay` | `pacat 17.0-98-gb096` / libpulse 17.0.0 | rc=0, stdout/stderr **0 B** (no positive witness) | rc=1, `Failed to open audio file.` (1 line, no prefix) | rc distinguishes (re-verified) |
| `aplay` | `aplay: version 1.2.16` | rc=0, `Playing WAVE '…' : Signed 16 bit Little Endian, Rate 44100 Hz, Mono` | rc=**0**, `Playing raw data '…' : Unsigned 8 bit, Rate 8000 Hz, Mono` (raw fallback); `-q`: rc=0, 0 B stderr | **rc=0 is not a verdict** (re-verified) |
| `ffplay` | `ffplay version n9.0.1` (lavf 63.1.101) | rc=0, stdout 1 B, stderr 2358 B / 15 lines | rc=**0**, `<path>: Invalid data found when processing input`; rc=0 also for a **nonexistent path** (`<input>: No such file or directory`, measured §6) | **rc=0 is not a verdict** (re-verified) |
| `ffplay` (SDL gate) | — | — | `SDL_AUDIODRIVER=bogus` → rc=1, `Could not initialize SDL - Audio target 'bogus' not available` (+ a DISPLAY red herring) | gate = rc + SDL line |

`aplay -l`: card 0 `Audio [USB Audio]` devices 0–3, cards 1/2 HDMI 3/7/8/9 — a
device exists, so the aplay arm is not `blocked` by absence on this host.

**F14 (this generation):** `raw/ffplay-noise.stderr` vs `raw/rv-ffplay-noise.stderr`
are **byte-identical** across sessions (1821 B), as are the paplay invalid-input
logs (27 B); the *valid-run* log is not (3 repeats, 3 sha, byte offsets 2162/2223
= `M-A: -0.000` vs ` 0.000`). The instability is confined to the progress
fragment.

## §2 Pre-landing helper-layer audit (inherited code the new legs extend)

`parser_surface_audit.py` (`73631bd0…`) re-run with `python3 -B` → output
**byte-identical** to the dead seat's JSON (`8bfed3c5…`, preserved as
`parser-surface-audit.deadseat.json`). Reproduced results: `_consumer_tail` on a
valid ffplay run returns the **progress fragment** (timing leaf);
`_pwcat_fields` returns `(None, None)` on all three new consumers' surfaces;
path normalization fires only on an exact `probe_arg` string match (fresh demo:
bare-name arg leaves the full prefix); `json.dumps(…, allow_nan=False)`
(`:2872`, `:2121`) raises on NaN; `out.mkdir(parents=True)` without `exist_ok`
(`:2871`, `:2120`; `:1491` does pass `exist_ok=True` — inconsistent writers).

**Structural insertion-only check, applied to revision B:** mode chain 119
clauses, suffix chain 119 clauses — **all 118 prior clauses preserved verbatim
and in order**, new clause at the head; the `sum([...])` flag list gained
`args.probe_consumers2_r75` appended. The 3 "deletions" in `git diff --stat` are
exactly those 3 lines (sum/mode/suffix) replaced by extended versions.

## §3 Landed-family audit — `lavfsweep-r74` (family the r75 arm sits beside)

`family_audit.py` (`1d31a4cb…`) re-run: stdout identical to the dead seat's
(`c12cb3d2…`); JSON differs in exactly one leaf (`generated_utc`). **7 receipts /
4 sha groups**; the only semantic split is **1 leaf**:
`/measurements/lavfsweep_lavf_iss_multi_r74_probe/fork_kind` `'wound'` →
`'truncation'` (fold comment now at `:1705-1708`). All report pins match the
cited receipt; members 6/6 match the author table; `failures: []` everywhere;
**no host path, no `/tmp/`, 0 hex8+ tokens**; stamp−mtime ≤ 0.001333 s.
**F16:** the extent legs' `--ao=pcm --ao-pcm-file=` argv appears **0 times** in
the receipt; `transport_protocol` is null on the startpos entry and carries only
the `--ao=null` axis command elsewhere.

## §4 `consumers-r73` drift + `failures` semantics

16 receipts / 11 sha. The `ef2647b5` variant differs from the r73-era base
`245dfa1a` in **exactly 2 leaves** (`daemon_live.default_sink` `…SPDIF__sink` →
`…SPDIF__sink.2`; `pacing_instant.wall_s` 4.032 → 4.033). **F15:** every
consumers-r73 receipt carries `failures: 2` — the two **measured forks recorded
as invariant-check failures** (mpv × dec_hcom seekable bit; pw-cat × `.snd` name
axis); the 15:03:05 S-case carries 6 (113 `Host is down` occurrences). The
baseline seat's replay exits 1 on those modes **by design**
(`corpus/live/r75-baseline/rerun.log`). Family aggregation must not read
`failures>0` as a regression.

## §5 Global receipt hygiene (16:29Z snapshot)

5615 dirs / 5290 tracked / 325 untracked entries; newest tracked receipt
`20261014T142733592435Z-sndfile-transport-r72`; ASLR two-class split verified by
family (3 genuine addresses in `ui-preempt-gsrt-r65`; 2 `format_hex` tokens in
`sndfile-transport-r72`; 21 files total); **399** receipts embed `/home/vgpnk`
(legacy families, unchanged); stamp−mtime ≤ 0.001362 s; the tracked `.pyc` was
dirty at open (`671711e2…`) and stayed byte-identical under `python3 -B`.

## §6 LANDED-parser audit (revisions A and B)

Method: `corpus/live/r75-scribe/newparser_audit.py` (`9696a3b6…`) →
`newparser-audit.json` (`3faef83d…`): the **new** parse helpers fed (a) the raw
captures on disk and (b) fresh bounded runs using the new legs' exact argv
(`paplay -v`, `aplay -D null`, `ffplay -nodisp -autoexit -v debug` + SDL dummy);
plus `leg-composition.txt` (the legs called directly), `postfix-tail-check.txt`,
`ops-tail-stability.txt`. All `timeout -s KILL`-bounded; no probe mode; no
receipt.

### 6.1 New helpers on the raw surfaces (both revisions)

| case | call | result |
|---|---|---|
| paplay invalid | `_paplay_fields` | `(None, 'Failed to open audio file.')` ✓ (F6c surface handled) |
| paplay XDG-severed | `_paplay_fields` | `(None, 'Connection failure: Connection refused')` — the **tail** holds `pa_context_connect() failed: …` (F19) |
| paplay PULSE_SERVER | `_paplay_fields` | `(None, 'Connection failure: Connection refused')` ✓ (the gate mechanism the author chose, `:2388`) |
| aplay raw fallback / valid | `_aplay_fields` | `(('raw data', 'Unsigned 8 bit, Rate 8000 Hz, Mono'), None)` / `(('WAVE', 'Signed 16 bit…'), None)` ✓ |
| ffplay invalid (`-v info`) | `_ffplay_fields` | `ffplay_invalid=True`, `avio_bytes_read=18`; probe/score/seeks null (loglevel-dependent, F18) |
| ffplay valid (`-v debug`) | `_ffplay_fields` | `detected='wav'`, `codec='pcm_s16le'`, `duration='00:00:00.20'`, `lavf_probe='wav'`, `lavf_score=99`, `avio_bytes_read=17718`, **`avio_seeks=0`** ✓ |

No float is parsed out of the ffplay progress fragment → **F8 is not
instantiated** by the new code (the writer's `allow_nan=False` hazard stays
latent).

### 6.2 F17 — path leak in the file-arm tails (revision A), and the receipt it produced

`aplay_leg`/`ffplay_leg` file arms pass `str(path)` (**absolute**) to the
consumer but hand `_consumer_tail` the **relative** label
(`str(path.relative_to(ROOT))`, fixture ROOT = `corpus/`), so the replacement
matches only the basename suffix and the host prefix survives. Demonstrated
end-to-end through the author's own leg functions (`leg-composition.txt`,
revision A): `aplay_leg("file", silence.wav).stderr_tail` =
`"Playing WAVE '/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/<input>' : …"`;
`ffplay_leg("file", noise.wav).stderr_tail` =
`"/home/vgpnk/…/corpus/<input>: Invalid data found when processing input"`.

**The first canonical receipt proves it:** `20261014T164125737824Z-consumers2-r75`
(mode `probe-consumers2-r75`, 100330 B, sha `876c810cc58b41a7…`, 29 entries,
`failures: 0`) carries **`/home/vgpnk` = True, `/tmp/` = True, 121 tails of which
16 are path-bearing** (all aplay/ffplay `file` arms across members).

**Revision B fixes it:** `_consumer2_tail` (`:1998-2013`) scrubs quoted paths and
residual unquoted prefixes; re-running the legs (`postfix-tail-check.txt`) gives
`Playing WAVE <input>' : …`, `Playing raw data <input>' : …`, `<input>: Invalid
data found…` — no path. The two post-fix receipts are **path-clean**
(`hostpath=False tmp=False`, 0 path-bearing tails).

**F17b (residual cosmetic):** the scrubber's second regex `\S+<input>` consumes
the opening quote, so aplay tails read `Playing WAVE <input>' : …` — an
unbalanced quote that survives into both post-fix receipts (cosmetic, stable).

### 6.3 F21 — the pacat racy-tail filter is anchored wrong; the tail is still unstable

`_PACAT_RACY_TAIL` (`:2016-2019`) is `^(Time:.*Latency:|Playback stream
drained\.|Draining connection to server\.|Connected to device.*|Stream
started\..*)$`. The real pacat `-v` progress line is
`Time: 0.040 sec; Latency: 159959 usec.` (3 runs measured, trailing spaces;
latency varies per run) — the alternation `Time:.*Latency:` is `$`-anchored and
**does not match** (verified by direct regex test: the full line → False, the
truncated `Time: … Latency:` → True). Consequence, measured in the family:

- the two post-fix receipts differ in **exactly one leaf**:
  `/measurements/consumer2_dec_act_r75_probe/consumers/paplay/transport_axis/fifo_path/stderr_tail`
  `'Draining connection to server.'` → `'Time: 0.000 sec; Latency: 34750 usec.'`;
- a direct `paplay -v` run reproduced the racy last-line competition
  (`Time: … Latency: N usec.` / `Playback stream drained.` / `Draining connection
  to server.`, plus an index-bearing `Connected to device … (index: N)` line).

So the author's stated goal ("a successful leg ends on the negotiated `Using
sample spec …` line") is not reached for the paplay arms; any byte-compare of two
r75 receipts must exclude that leaf.

**Confirmed at scale in the 4th receipt (§6.5):** receipt 3 → receipt 4 flips
**7** paplay tails between `'Draining connection to server.'` and
`'Time: 0.000 sec; Latency: 34750 usec.'`.

### 6.4 Other landed-code observations (code-read, bounded)

- **F4 resolved in the new entry:** `consumer2_transport_entry` (`:2242-2275`)
  keys each consumer's **own** signature — paplay `(exit, spec, pa_error)`,
  aplay `(exit, kind, aplay_error)`, ffplay `(exit, detected, seeks, invalid)` —
  and lands a fork as a `failures` row (F15 convention). The r73 binary branch is
  untouched.
- **F18 — loglevel-dependent fields:** at `-v info` the ffplay
  probe/score/`avio_*` fields are all null; they populate only at `-v debug`
  (the matrix leg's level). The ops driver legs use `-v info` and read only
  `Input #0` + the SDL error — consistent, but the pull-model witness
  (`avio_seeks`) exists only at debug.
- **F19 — paplay field/tail precedence:** `pa_error` takes the first match in
  pattern order, so on the XDG-severed surface it carries `Connection failure: …`
  while the tail carries `pa_context_connect() failed: …`. The author's gate uses
  `PULSE_SERVER=unix:/nonexistent-r75-paplay-gate` (single-line surface) and
  asserts rc=1 + a deliberately loose `"onnection"` substring on the **tail**
  (`:2409-2413`) — correct for the measured surface and safe against the
  one-letter `pw_context_connect` collision. A future gate keyed on `pa_error`
  with the token `pa_context_connect` would pass only on the XDG surface.
- **F20 — ffplay info-level tail shape is file-length dependent:** on the 4 s
  member the `-v info` last line is the `Stream #0:0: Audio: …` line (stable,
  2/2 identical, carries the benign `0x0001` token); on the 0.2 s silence it is
  the progress fragment (F5). The ops driver-leg tails therefore inherit the
  member's length class, not a fixed shape.
- Kill classes pinned by `_nowriter_cell` (`:2297-2349`): wait → wchan sample →
  SIGTERM → 1.0 s → SIGKILL process group; assertions per consumer (paplay
  `-15`, aplay `-9`, ffplay `123`) — consistent with the scout's scratch
  measurements.
- aplay matrix uses `-D null` (device-free input verdict) while the ops entry
  censuses `aplay -l`/`-L` and axes {null, default, pipewire, hw_first} — the
  `blocked` condition is "no ALSA card enumerated".

### 6.5 Family stability across the 4 canonical receipts (16:41:25Z → 16:46:03Z)

All four receipts: mode `probe-consumers2-r75`, **29 entries**, `failures: 0`,
untracked, stamp−mtime ≤ 0.000458 s.

| # | stamp (UTC) | bytes | sha256 (16) | revision | `/home/vgpnk` | `/tmp/` | path-bearing tails |
|---|---|---|---|---|---|---|---|
| 1 | 16:41:25 | 100330 | `876c810cc58b41a7` | A (pre-fix) | **True** | **True** | **16** |
| 2 | 16:43:19 | 99079 | `db4b827ae4a9972a` | B | False | False | 0 |
| 3 | 16:44:18 | 99086 | `a3047c8a4f1bb235` | B | False | False | 0 |
| 4 | 16:46:03 | 99199 | `3b91594b787f275b` | B | False | False | 0 |

Leaf deltas (full-tree diff, no exclusions):

- **1 → 2: 54 leaves, all `stderr_tail`** — the F17 scrub (16 path-bearing tails
  + `/tmp/` mkdtemp residue) plus the pacat-tail filtering change.
- **2 → 3: 1 leaf, a `stderr_tail`** — the paplay `fifo_path` tail (F21).
- **3 → 4: 12 leaves, all `stderr_tail`**, in three classes:
  - 7 paplay arms flipping between the drain line and the racy
    `Time: … Latency: 34750 usec.` line (**F21**);
  - 4 ffplay `fifo_path` tails flipping between
    `'<input>: Invalid data found when processing input'` and the **progress
    fragment** `'    nan    :  0.000 fd=   0 aq=    0KB vq=    0KB sq=    0B'`
    (**F22** — F5 instantiated in a post-fix receipt; the `nan` token enters the
    receipt as a *string*, harmless to `allow_nan=False`);
  - 1 ffplay ops `sdl_driver_axis.legs.alsa` tail flipping between
    `'ALSA lib pcm.c:8787:(snd_pcm_recover) [error.pcm] underrun occurred'` and
    the `'  Stream #0:0: Audio: pcm_s16le ([1][0][0][0] / 0x0001), …'` line
    (**F23** — the `alsa` driver leg produces a real ALSA underrun; that leg's
    tail is racy too).

**Net bounded statement:** in the post-fix family the *parsed fields* are stable
across runs — **every** inter-receipt leaf delta is a `stderr_tail` string — so
the family is field-comparable but not byte-comparable; a byte-compare must
exclude the `stderr_tail` leaves (or the racy shapes must be filtered:
`Time: … Latency: … usec.`, the ffplay progress fragment, the ALSA underrun
line).

## Findings (verbatim for the canonical judge)

- **F1 — "committed receipt" wording drift RECURRED in r74** (`r74-author.md:74`
  "committed receipt", `:159` "Receipt:"; `git ls-files corpus/live/runs |
  grep -c lavfsweep` → 0, re-verified). Members committed, receipts not.
- **F2 — `lavfsweep-r74` is semantically heterogeneous** (1 leaf separates
  `0c34e611`'s `wound` from the `ebddda25` triple's `truncation`). "Byte-identical
  ×N" claims must name receipts.
- **F3 — the author's cited r74 receipt is pre-fold** (values identical; only
  `fork_kind` differs); corroborates `r74-verifier.md:176-179`.
- **F4 — resolved in the new family entry** (per-consumer signatures,
  `:2242-2275`); the r73 binary branch (`:1173-1174`) is untouched.
- **F5 — `_consumer_tail` on a short valid ffplay run returns the progress
  fragment** (timing leaf); refined by F14 (instability confined to that
  fragment) and F20 (file-length dependent).
- **F6 — rc is not a verdict** for the new consumers (re-verified 3/3; ffplay
  also rc=0 for a nonexistent path).
- **F7 — the pw-cat `PIPEWIRE_RUNTIME_DIR` severing trick does not transfer to
  paplay** (re-verified 3/3); the landed gate correctly uses PULSE_SERVER (F19).
- **F8 — `allow_nan=False` + ffplay's `nan` token**: latent, **not instantiated**
  by the landed parser (no float parse of the progress fragment).
- **F9 — ffplay stderr is CR/ESC-interleaved** and `_consumer_tail`'s
  `replace(probe_arg, "<input>")` only fires on an exact string form (fresh demo).
- **F10 — no ALSA/SDL gate existed pre-landing**; the landed ops entries now
  carry both (`aplay -l` census; `SDL_AUDIODRIVER` axis {dummy,pulse,alsa}).
- **F11 — `daemon_live.default_sink` is daemon-state-dependent**
  (`…SPDIF__sink` vs `…SPDIF__sink.2`, same session).
- **F12 — ASLR scan needs the two-class split** (3 genuine addresses vs
  `format_hex` tokens); ffplay's `0x0001` is a third, benign class.
- **F13 — wave label date vs clock date; local TZ = UTC−3.** Recorded.
- **F14 — the ffplay instability is confined to the progress fragment**
  (invalid-input logs byte-identical across sessions).
- **F15 — `failures` rows in consumers-r73 are fork signatures**, not defects.
- **F16 — the extent legs' `--ao=pcm` argv is undeclared** in the lavfsweep-r74
  receipt (0 occurrences).
- **F17 — file-arm `stderr_tail` host-path leak (revision A), confirmed in the
  first canonical r75 receipt** (16 path-bearing tails + `/tmp/`); **fixed in
  revision B** by `_consumer2_tail`, with residual F17b (stray `'`).
- **F18 — ffplay parse fields are loglevel-dependent** (debug-only for
  probe/score/seeks).
- **F19 — paplay `pa_error` vs tail precedence**; the landed gate avoids the
  trap; a `pa_context_connect`-keyed field check would not.
- **F20 — ffplay info-level tail shape depends on member length.**
- **F21 — the pacat racy-tail filter misses the real line shape**
  (`Time: X sec; Latency: N usec.`), so the paplay tail remains run-to-run
  unstable; receipts 2/3/4 differ in exactly that leaf class (1 → 7 leaves as the
  family grew).
- **F22 — the ffplay `fifo_path` tail flips between the error line and the
  progress fragment** (`'    nan    :  0.000 fd=   0 aq=    0KB vq=    0KB sq=    0B'`)
  in the post-fix receipts (4 leaves between receipts 3 and 4) — F5 instantiated
  after the fix; `nan` enters the receipt as a string only.
- **F23 — the ffplay ops `alsa` driver-leg tail is racy** (ALSA underrun line vs
  the `Stream #0:0 … 0x0001 …` line), so the `sdl_driver_axis` leg is not
  byte-stable either.
- **F24 — every inter-receipt leaf delta in the post-fix r75 family is a
  `stderr_tail` string** (54 / 1 / 12 leaves for 1→2 / 2→3 / 3→4): the family is
  field-stable but not byte-comparable. Any "receipts byte-identical ×N" claim
  for r75 must name receipts and exclude tails.

## Gates

| gate | state (16:46:10Z) |
|---|---|
| author arm landed | **YES, in the worktree** — fixture blob `b0153958c28d` (923 insertions / 3 line-replacements vs HEAD), **4** canonical receipts, **no commit** (HEAD `6f905c3`) |
| prior rows byte-stable | pre-landing: fixture `e3ef52e1…` == HEAD at every check; after landing the fixture is dirty by design (author edit); prior *receipt* families untouched |
| insertion-only | **YES at clause level** — 118/118 mode clauses and 118/118 suffix clauses preserved verbatim/in order, new clause at head; flag-list entry appended |
| r75 receipts (canonical) | **4** (16:41:25Z → 16:46:03Z): `…T164125737824Z` (pre-fix, `876c810cc58b41a7…`, **path-bearing**), `…T164319396674Z` (`db4b827ae4a9972a…`), `…T164418398152Z` (`a3047c8a4f1bb235…`), `…T164603163948Z` (`3b91594b787f275b…`) — 29 entries, `failures: 0` each, **3 distinct sha**, all **untracked** (`git ls-files \| grep -c consumers2` → 0); inter-receipt deltas are `stderr_tail`-only (§6.5) |
| raw-surface inventory (this seat) | DONE — 26 + 8 bounded invocations, 0 receipts written by this seat |
| pre-landing helper audit (this seat) | DONE + reproduced byte-identically |
| landed-parser audit (this seat) | DONE — revisions A and B; F17 confirmed in a real receipt and fixed, F21–F24 live (family field-stable, tail-unstable) |
| landed-family audit (r74; this seat) | DONE + reproduced (7 receipts / 4 sha) |
| receipt hygiene (this seat) | DONE — global scans, family drift, r75 family classification (pre-fix vs post-fix variant) |
| verifier replay / adjudication | not started (no r75 commit) |
| ledger (LOG/SCORECARD) | draft below (conditional) |

## LOG / SCORECARD draft (conditional — arm uncommitted)

The r75 family is **not yet committable**: no author report, no verifier replay,
receipts untracked, and the family is already **semantically split** — receipt
`…T164125737824Z` (revision A) is path-bearing, the three later ones are clean and
differ from each other only in `stderr_tail` leaves (§6.5). A ledger entry must
therefore name its receipts, state the revision each was written under, and
carry: the three consumers' per-member transport matrices + paplay's name-axis
control (predicted invariant-reject), the three gate mechanisms (pulse dead
server / ALSA `-D null` + card census / SDL driver axis), the three kill classes
(paplay −15, aplay −9, ffplay 123), and this seat's hazard list F4–F9, F14,
F16–F24 — **including the byte-compare rule that `stderr_tail` leaves must be
excluded**. Receipt wording must say **"on-disk receipt"** unless the integrator
commits them (F1).

## Touched surfaces

- Wrote **only**: `reports/round-75/r75-scribe.md` and
  `corpus/live/r75-scribe/**` (poll-landing.sh, reverify.sh, landing-watch.log,
  r75-scribe.prior-draft.md, newparser_audit.py, newparser-audit.json,
  fixture-snapshot-1640.py, fixture-diff-1640.diff, raw/** incl. `rv-*`, `np-*`,
  `reverify.txt`, `leg-composition.txt`, `postfix-tail-check.txt`,
  `ops-tail-stability.txt`, family_audit.py + family-audit{,.deadseat}.json +
  stdout logs, parser_surface_audit.py + parser-surface-audit{,.deadseat}.json +
  stdout logs, watch.sh, raw_surface.sh, raw_surface2.sh).
- No tracked file modified by this seat; no git mutation; no product-code edit;
  no fixture probe mode run; **no receipt written by this seat**. The author's
  fixture edit and the 3 receipts are the author seat's, untouched by me.
- Live-stack disclosure: bounded silence/text consumer runs only (3 invalid-input
  re-runs, 3 env-gate re-runs, 8 new-parser runs incl. 2 `-v debug` ffplay runs,
  4 leg-composition runs, 2 ops-shape runs, 3 direct `paplay -v` runs); daemon
  untouched; `pactl info` read-only.

## Out-of-scope (explicitly not done)

- Patching the landed fixture (F17b/F21 are reported for the author/critic, not
  fixed by this seat), running the author's probe mode, or re-deriving the
  author's receipts.
- Adjudicating the r75 family or any sibling seat's scratch/report
  (verifier/critic/boundary/scout seats).
- Commit/push/publish (operator/integrator-owned).

## Artifact paths + hashes

- This report: `reports/round-75/r75-scribe.md`; superseded draft
  `corpus/live/r75-scribe/r75-scribe.prior-draft.md` `de7c6b35…`
- Fixture revisions audited: A `b057bab6b36756a41a41ff789066fbd684a8d581`
  (sha256 `a56107f473c116c668b6d0e487b6635761377defa0706bb54ea49eea6e462cfd`,
  snapshot `corpus/live/r75-scribe/fixture-snapshot-1640.py`, diff
  `fixture-diff-1640.diff` `cf924e43…`); B `b0153958c28dc7b7f0ff5d4ff5ef98dd4a53e4be`
  (sha256 `545c9fe1c649db0ad6a8c13578e778b707236143c7294d8d4a23e5b56b7e6e46`);
  baseline (HEAD) `e3ef52e1e02c742d4f6dabda5c8658cc8f80a0bb`
  (`317c0b48…`, 2879 lines)
- r75 receipts (canonical, untracked):
  `corpus/live/runs/{20261014T164125737824Z,20261014T164319396674Z,
  20261014T164418398152Z,20261014T164603163948Z}-consumers2-r75/measurements.json`
- r74 family: `corpus/live/runs/{20261014T153027827786Z,…,20261014T154138420733Z}-lavfsweep-r74/`
  (7 receipts, 4 sha groups, untracked); members `corpus/live/round-74/lavf_*`
  (tracked in `168b165`)
- Scratch artifacts (this seat): `poll-landing.sh` `7d829b2b…`,
  `reverify.sh` `bd40511c…`, `raw/reverify.txt` `73504013…`,
  `newparser_audit.py` `9696a3b6…`, `newparser-audit.json` `3faef83d…`,
  `raw/leg-composition.txt` `2b21e850…`, `raw/postfix-tail-check.txt` `ddc42fbe…`,
  `raw/ops-tail-stability.txt` `da360af9…`, `family-audit.json` `0719c525…`
  (dead-seat `af305eb3…`), `parser-surface-audit.json` `8bfed3c5…`,
  `raw_surface.sh` `38239d59…`, `raw_surface2.sh` `54f3e05b…`, `watch.sh`
  `3c6a7e3b…`, `landing-watch.log`
- Prior-wave basis: `../shokunin-train-20261101-w12/xconnector.md`; r74 reports
  in `reports/round-74/`

## Exact commands / exits (appendix, this generation)

```sh
cd ~/Projects/shokunin/audio-shokunin
# pre-landing (fixture e3ef52e1… == HEAD, r75 refs 0, r75 receipts 0)
bash corpus/live/r75-scribe/reverify.sh                        # exit 0; F6 3/3, F7 3/3
python3 -B corpus/live/r75-scribe/parser_surface_audit.py      # exit 0; JSON byte-identical to dead-seat
timeout 600 python3 -B corpus/live/r75-scribe/family_audit.py  # exit 0; stdout == dead-seat stdout
# landing observed
git log --oneline 6f905c3..HEAD | wc -l                        # 0 (no commit)
git hash-object corpus/fixtures/measure_audio.py               # e3ef52e1e02c -> 793e3d958bd0 -> b057bab6b367 -> ce2b6c1560ca -> b0153958c28d
git diff --stat corpus/fixtures/measure_audio.py               # 923 insertions(+), 3 deletions(-)
python3 -B corpus/live/r75-scribe/newparser_audit.py           # exit 0; new helpers vs raw surfaces + fresh runs
python3 -B - <<'PY'  # leg composition (author's own functions, scratch paths only)
  aplay_leg("file", silence.wav)   # rev A: tail leaked /home/vgpnk/… ; rev B: 'Playing WAVE <input>' : …'
  ffplay_leg("file", noise.wav)    # rev A: leaked ; rev B: '<input>: Invalid data found…'
PY
for i in 1 2 3; do timeout -s KILL 15 paplay -v silence.wav; done  # racy last-line competition (F21)
python3 -c "import re; p=re.compile(r'^(Time:.*Latency:|…)$'); p.match('Time: 0.160 sec; Latency: 39962 usec.')"  # False (F21)
ls -d corpus/live/runs/*r75*                                   # 4 dirs, mode probe-consumers2-r75, 29 entries, failures 0
git ls-files corpus/live/runs | grep -c consumers2             # 0 (receipts untracked)
# family stability: full-tree leaf diff between consecutive receipts
python3 - <<'PY'   # 1->2: 54 tail leaves; 2->3: 1; 3->4: 12 (all stderr_tail)
PY
```

Exit codes: all inspection/audit commands exited 0 except the deliberate
zero-match greps (`grep -c` → 0) and the consumer invalid-input arms whose rc is
the finding itself (ffplay 0, aplay 0, paplay 1). No git mutation, no fixture
mode, no receipt written by this seat.

**Seat stop.** Report complete; no further action taken (leaf, no dispatch, no
commit).
