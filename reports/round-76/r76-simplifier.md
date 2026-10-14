# R76 simplifier — capture lattice (`d566a31`): replay-proven deletions + candidates

Seat: **simplifier** (audio lane). Round 76, post-commit verify.
Repo `~/Projects/shokunin/audio-shokunin` @ `d566a31` (fixture sha
`691d730d4b4b2aa1475aa03bd4d9d7b5c9bdd3baf6a62d24923097f6fb9e9734` = HEAD).
Scope reviewed: the committed r76 diff **only** (`git show d566a31 --
corpus/fixtures/measure_audio.py`, +1147 lines, the `capture_*_r76_probe`
family and its helpers). Nothing was applied to the fixture: every
proposal below is a diff in my scratch scope
(`corpus/live/r76-simplifier/`). **No tracked file was written; no git
mutation; the shared tree is byte-identical to HEAD** (`git status
--porcelain -uno` empty at 18:34Z, 18:39Z and 18:45Z; fixture sha above).

Host `plazir27` (measured 2026-10-14 18:31–18:45Z): Python **3.14.7**,
pacat **17.0-98-gb096** (libpulse 17.0.0), alsa-utils **1.2.16**, ffmpeg
/ffprobe **n9.0.1**, kernel **7.2.3-arch1-3**. All claims are this-host,
this-session, named-version bounded.

## 0. Verdict

| | |
|---|---|
| deletions proposed (replay-proven byte-identical) | **D1–D9**, 13 diff lines out, 8 in → −5 lines, −301 B, all inside the r76 block |
| deletions applied | **none** (LEAF seat; proposals + variants only) |
| candidates found but deliberately **not** proposed | C1–C6 (§5), each with its receipt delta |
| preserved contract | prior rows untouched, all six `capture_*_r76_probe` entries still emitted, `failures: {}` in all 8 replay passes, every assertion and armed witness kept (§4) |
| axes | weight/brevity ↑, replay determinism =, evidence integrity =, contract (prior rows + pinned classes) = — no axis regressed, one improved |

The honest headline: the r76 diff is **mostly irreducible measurement
surface**. The six entry bodies are the deliverable, not redundancy, and
the only weight that can be removed without touching a witness is a dead
binding / dead key / dead parameter / an over-defensive branch. That is
what D1–D9 are — small, mechanical, and each one replay-proven.

## 1. Method (and why a mirror)

The fixture derives `ROOT = parents[1]` from `__file__`, so a scratch copy
that keeps the `…/corpus/fixtures/measure_audio.py` shape has its own
`artifacts/`, `live/runs/` and roundtrip scratch dir. I ran every pass
from a mirrored tree
(`corpus/live/r76-simplifier/mirror/corpus/fixtures/measure_audio.py`,
ROOT = `…/r76-simplifier/mirror/corpus`) with cwd = repo root (the
author's invocation). Consequences, all verified:

- every receipt I produced lives under my write scope
  (`corpus/live/r76-simplifier/mirror/corpus/live/runs/`, copied to
  `…/r76-simplifier/receipts/`); nothing under `corpus/live/runs/` was
  written or modified by me;
- `build_artifacts.py` regenerated only the mirror's artifact copy (which
  it reproduced byte-identically from the pristine copy — see
  `mirror-artifacts-pristine/`), so no tracked artifact was touched;
- the mirror isolates my passes from the **concurrently running sibling
  battery** on this host (§6 O4) only in *file* terms — device and
  PipeWire state are still shared, and that is visible in the receipts
  (§6 O2/O3).

Passes (8 × `--probe-capture-r76`, `timeout -s KILL 600`, exit 0, wall
48.9–49.2 s): `A2 B1 B2 A3` (round 1) then `B3 A4 A5 B4` (round 2), where
A = HEAD-bytes fixture and B = variant. Interleaved so an environment flip
shows up as a *baseline* difference rather than being misread as a
deletion effect. Driver: `replay_ab.py`, `replay_ab2.py`; logs
`replay-log.json`, `replay-log-round2.json`; raw stdout/stderr kept.

**LSP device: unavailable.** No language server answers this file in this
session — `mcp_list_servers` exposes only `rea` (no `lsp` server), and no
language-server binary or semantic library is installed (`pyright`,
`basedpyright`, `pylsp`, `jedi`, `rope`, `pyflakes`, `astroid`, `libcst`
all absent). Every "no caller / never loaded" statement below is therefore
**the literal fallback, not semantic proof**: a scope-aware AST
name-binding scan (`unused_names.py`, output in
`unused-names-baseline.txt` / `unused-names-variant.txt`) plus literal
grep counts, explicitly labelled as such.

## 2. The deletion set (proposed, not applied)

Variant files: `variants/measure_audio_simplified_d1d8.py` (round 1) and
`variants/measure_audio_simplified_d1d9.py` (final), patch script
`apply_r76_simplifier_deletions.py` (each anchor asserts exactly one
match, so the patch cannot drift), diff
`variants/deletions-d1d9.diff`. Line numbers are HEAD
(`corpus/fixtures/measure_audio.py`).

| id | line(s) | deletion | proof of neutrality |
|---|---|---|---|
| D1 | 3080 | `insp["data_4k_aligned"] = actual % 4096 == 0` | computed, **never serialized and never asserted**: the name occurs exactly once in the module (grep count 1); the two consumers of an inspect dict copy explicit keys only (`_capture_file_leg` 3249–3269, `_capture_sever_cell` 3323–3334) and `_capture_parser_verdict`/the roundtrip read `fmt`/`data_actual`/`chunks`/`bytes`/`data_finalized`, never `data_4k_aligned` |
| D2 | 3353 | `hw0` → `_` in `capture_gate_r76_entry` | AST: bound-but-never-loaded in that function; the gate's arecord legs are literal `-D default/pipewire/does_not_exist` |
| D3 | 3643 | `mon, hw0` → `_, _` in `capture_sever_r76_entry` | AST: both bound-but-never-loaded; the arecord cells iterate `inv["alsa_capture_devices"]` directly (3671–3690) |
| D4 | 3774 | `hw0` → `_` in `capture_name_axis_r76_entry` | AST: bound-but-never-loaded; name legs use `-D null` only |
| D5 | 3540 | `cls, line = _capture_errclass(err)` → `cls, _ = …` (parec byte-cap leg) | AST: `line` bound-but-never-loaded in `capture_bounded_r76_entry`; the leaf records `error_class` only, and the same stderr is still witnessed by `stderr_tail` (`_capture_tail(err, "-")`, 3553) — on both observed runs `error_class` is `null` and the tail is `"Got signal, exiting."` |
| D6 | 3707 | `"kill_riff": None` from the `ffmpeg` entry of the sever `expected` map | the value is never read: the ffmpeg branch asserts the deliberately-unpinned unfinalized **union** class (3730–3741); only the `elif` at 3757 reads `exp["kill_riff"]`, and it is reached only for `pwrecord`/`parecord` |
| D7 | 3827–3831 | collapse the two-branch `out_kind` assignment to `if leg.get("file"): leg["out_kind"] = _capture_out_kind(leg["file"])` | extensional equality on the reachable domain: `_capture_out_kind` already returns `"missing"` for `exists is False` (3084–3089), and the `elif` is unreachable because every `file` leaf comes from `_capture_file_leg`/`_capture_sever_cell`, which always set `"exists"` (so a present leaf is never falsy); only an impossible `{}` leaf would differ |
| D8 | 3987, 3989 | drop `cap_rel = str(cap)` and pass `str(cap)` at its single use | stale name + single-use alias: `cap_rel` holds an **absolute** path while its sibling `mem_rel` is genuinely relative (`str(member.relative_to(ROOT))`); the value passed to `transport_leg` is unchanged |
| D9 | 3281–3283, 3295 | drop `_capture_sever_cell`'s `env=None` parameter and the internal `env={**os.environ, **(env or {})}` | AST call-site scan over all 26 `_capture_*` call sites: **no caller passes `env=`** to `_capture_sever_cell` (only `_capture_file_leg`, line 3371, ever does); `os.environ` is never mutated in the module (no `os.environ[...]`, `putenv`, `update`), so the merge was a copy of an unchanged mapping — dropping it makes the child inherit the same environment and leaves **one** env convention (merge at the caller) |

Byte/line budget: baseline 4993 lines / 288 051 B → D1–D8 4989 lines /
287 827 B → D1–D9 4988 lines / 287 750 B. All hunks fall inside the r76
block (HEAD 2907–4033); no pre-existing row's code, no assertion, no
comment and no pinned class is touched.

## 3. Replay evidence

`receipts/*.json` (copies of each pass's `measurements.json`),
`receipt-compare.txt` (full pairwise table), `compare_receipts.py`.

| pass | fixture | receipt sha256 | failures |
|---|---|---|---|
| A2 baseline | `691d730d…` (HEAD) | `cbb7bda6a925f203383a52eac92eee913ac36bd2fc4f2770aacaa4c817197b89` | `{}` |
| B1 D1–D8 | variant d1d8 | `3cf80369b2f277bc6bf38e7c19f0640fdd30ededf863d79aa153f3cc761a680e` | `{}` |
| B2 D1–D8 | variant d1d8 | `cbb7bda6a925f203…` | `{}` |
| A3 baseline | HEAD | `3cf80369b2f277bc…` | `{}` |
| B3 D1–D9 | variant d1d9 | `cbb7bda6a925f203…` | `{}` |
| A4 baseline | HEAD | `3cf80369b2f277bc…` | `{}` |
| A5 baseline | HEAD | `3cf80369b2f277bc…` | `{}` |
| B4 D1–D9 | variant d1d9 | `3cf80369b2f277bc…` | `{}` |

Two byte-identity classes, one per observed environment state:

- **ports-present state**: `A2-baseline ≡ B2(D1–D8) ≡ B3(D1–D9)` — three
  byte-identical receipts, differing_leaves = 0;
- **ports-absent state**: `A3-baseline ≡ A4-baseline ≡ A5-baseline ≡
  B1(D1–D8) ≡ B4(D1–D9)` — five byte-identical receipts,
  differing_leaves = 0.

Across all 28 pairwise comparisons the **only** leaves that ever differ
are `capture_gate_r76_probe.inventory.pw_capture_ports[12]` and `[13]`
(`parecord:monitor_FL/FR`), and they differ *within* the baseline group as
well (A2 vs A3) — i.e. they are a host process-state artifact, not an
effect of any deletion (§6 O2). Baseline-only samples (A2/A3/A4/A5) also
show the environment is deterministic in each state, which is what makes
the A/B identity meaningful.

Independent replication: my receipts differ from the author's canonical
`ba36cd70…` in **1 leaf** (ports-absent passes) — the roundtrip aplay tail
`"Playing WAVE …"` → `"laying WAVE …"`, fully explained by §6 O1 and
reproduced arithmetically by `aplay_tail_mechanism.py`. Every other leaf,
including all six entries, every pinned class, the arecord hw success
leaves, the parecord 64-KiB-aligned TERM bound, the arecord
accept-and-lie KILL shape, the name axis, the device axis and the
roundtrip's exact 960 044 B capture with its content witness, matches the
canonical receipt byte-for-byte from a relocated tree.

## 4. Preserved contract

- **Prior rows untouched.** My patches touch only the r76 block; the
  insertion-only discipline of the r76 diff (mutex sum, `mode` and
  `suffix` ternary clauses) is untouched. All my receipts are new
  timestamped dirs under my own scope; no receipt under
  `corpus/live/runs/` was written or modified by this seat.
- **All six entries still emitted** in every pass
  (`capture_gate_r76_probe`, `…_bounded_…`, `…_sever_…`, `…_name_axis_…`,
  `…_device_axis_…`, `…_roundtrip_…`) with `failures: {}`.
- **Witnesses deliberately kept** (deletion considered and refused, or
  not even considered as weight): `data_64k_aligned` / `data_256k_aligned`
  (3076–3078, recorded at 3331–3332 and asserted at 3606), `ffprobe_parses` (3103/3129/3133 —
  recorded, never asserted; it is a witness a verifier can compare, so it
  stays even though it cannot by itself falsify anything),
  `paced_expectation` (3274), the `arecord -L` plugin enumeration
  (`alsa_plugins`, 3144/3196 — it is the evidence that `default`/`pipewire`
  are *plugin* routes, i.e. the device-axis inversion's premise), the
  `env_override` labels on the dead-daemon legs (3397/3418), the
  ffmpeg-KILL unfinalized **union** class (3730–3741, deliberately not
  pinned), the arecord accept-and-lie assertion on
  `wave_frames_class == "inflated"` (3753), the `hw_first_mono` channels
  leg (3884/3907), `arecord_contention` / `arecord_*_blockage`
  (3691–3696), the `_ba`/`_br` names in the `fmt` struct unpack (3058 —
  they document the layout and are underscore-marked as intentional
  discards), and every named failure class in `_CAPTURE_ERR_CLASSES`
  (2982–2995), including the four the *gate* legs never exercise (`alsa_channels`, `alsa_busy`, `ffmpeg_muxer`, `aborted_by_signal`), which the device-axis, contention, name-axis and sever legs exercise respectively.

## 5. Candidates found, NOT proposed (each changes receipt bytes)

- **C1 — `viability.pw_target` (3356) duplicates `pulse_source` (3355)**:
  the same expression `bool(inv["sources"])` under two names. Deleting it
  removes a receipt key. Kept: it is the gate's per-consumer digest, and
  the two names read as different consumer questions even though the host
  answers them identically today.
- **C2 — the roundtrip hardcodes the author's seat**:
  `scratch = ROOT / "live" / "r76-author"` (3935) and the literal label
  `"live/r76-author/<tmp>/roundtrip_capture.wav"` (3990–3991). This is a stale
  name *and* a second labelling convention (r75's `aplay_leg` derives
  `str(path.relative_to(ROOT))`; here the label is a literal because the
  scratch dir must live under ROOT). Demonstrated live: three
  `-capture-r76` receipts in the real tree at 18:32:15Z / 18:33:09Z /
  18:34:04Z — not mine (mine are in the mirror), not the author's
  (181454–182539Z) — all carry the label `live/r76-author/<tmp>/…`, and
  any seat's run creates/uses `corpus/live/r76-author/`. Minimal fix
  shape: one round-scoped dir + `str(cap.relative_to(ROOT))` for the
  label; receipt delta = that one label string. Not applied (byte-visible
  and it is the author's call, not a simplifier's).
- **C3 — duplicated racy-tail scrub**: the `_PACAT_RACY_TAIL` filter
  expression is written twice (r75 `paplay_leg` 2099–2100, r76
  `_capture_tail` 2967–2968). One `_pacat_scrub(text)` helper would make
  it single-authority, but it is **net-zero in lines** and touches r75
  source; the win is convention, not weight. Deferred, not proposed.
- **C4 — three magic timeout literals** in the gate's named-failure legs
  (`10`, `10`, `15` at 3382/3391/3412) where the module's convention is a
  named constant. Substituting `CAPTURE_R76_TIMEOUT_S` is behaviourally
  identical for legs that fail in milliseconds but *not provably*
  byte-identical: the `blocked` string interpolates the timeout
  (`_capture_run`, 3014–3016), so a hanging host would change a receipt
  leaf. Not proposed (unprovable under this round's standard).
- **C5 — `arecord -L` is the only enumeration without exit/error
  recording** (3194–3201: bare `except … pass`, no `arecord_L_exit`),
  unlike its five siblings. Kept per the evidence axis (C-section above);
  the asymmetry is worth one line of the L1's attention, not a deletion.
- **C6 — out of scope**: `ffprobe_leg:574 dout` is an r71-era dead
  binding found by the whole-file scan. Not proposed: the tasking is the
  r76 diff only.

## 6. Evidence-integrity observations (not deletions)

- **O1 — the roundtrip's aplay tail is ROOT-prefix-length sensitive.**
  `_consumer_tail` (1013–1024) truncates to the last 160 chars *after*
  substituting the relative label; the aplay line carries the absolute
  path, so only the label part is substituted and the surviving head
  depends on the absolute prefix length. Arithmetic
  (`aplay_tail_mechanism.py`, output saved): author tree → 127 chars, no
  cut, `"Playing WAVE <input>' : …"`; my mirror (34 chars longer) → 161
  chars, 1-char cut, `"laying WAVE <input>' : …"`. This exactly
  reproduces both receipts and also predicts the three real-tree sibling
  receipts (`"Playing…"`). **The verdict is unaffected** — `same_detect_class`
  compares `alsa_kind`/`sox_detected_format` parsed from the full text —
  but any receipt comparison across differently-rooted trees will show
  this phantom leaf.
- **O2 — `inventory.pw_capture_ports` is process-state sensitive**, not a
  pure device inventory: any live parecord/pw-record node in the session
  contributes ports. Observed 12 ports (author's six runs, my A3/A4/A5/B1/B4),
  14 ports (my A2/B2/B3, when a foreign `parecord:monitor_FL/FR` was
  registered) and 16 ports (real-tree sibling run 18:34:04Z, two consumer
  nodes). This is the *only* leaf that varied between otherwise identical
  runs, including baseline-vs-baseline.
- **O3 — the arecord hw legs flip on a concurrent holder.** My first pass
  (18:33Z) recorded `alsa_busy` (a *named* class, correctly not raised as
  a failure) on `arecord_duration_hw`, `sysdefault`, `plughw_first`,
  `hw_first` and `hw_first_mono`, while the later passes recorded the
  canonical success leaves (192 044 B, `wall_lt_0.5s=False`). Same
  fixture, same host, ~2 min apart: the hw leaves are session-state
  dependent, and the design absorbs it without a failure — worth stating
  explicitly wherever those leaves are cited as pins.
- **O4 — a sibling seat's battery ran concurrently** (`corpus/live/r76-verifier/run{1,2}.stdout.json`,
  `…consumers2-r75`, `…failing`; live PIDs 611955/611977/611979 at 18:39Z).
  My A/B pairs were obtained *under* that interference and still came out
  byte-identical in both states, which strengthens the neutrality claim;
  but receipt-vs-receipt comparisons in this wave should be serialized
  (or normalized on O2's leaf) to avoid reading interference as a
  difference.
- **O5 — provenance correction of my own earlier observation.** The two
  consumer processes holding the ALSA card at 18:34:01Z (PIDs 83601
  `arecord -D hw:0,0 … sev_arc_kill.wav`, 83622 `parecord … nx_rf.raw`,
  both with r76 tmp argv, both gone by 18:35Z) are consistent with the
  concurrent sibling battery (O4), **not** with the author's 18:24/18:25Z
  runs. No claim is made about the author's process hygiene.

## 7. Tradeoff and stop condition

Tradeoff: D1–D9 remove 5 lines and 301 bytes of genuinely dead weight and
nothing else. The bigger "weight" in the diff is the six leg matrices —
that is the measurement, and the seat refuses to touch it. The one place
where a deletion narrows evidence is **D5**: in a hypothetical parec error
on the byte-cap leg the raw error line would no longer be recorded
(`error_class` and `stderr_tail` still are). If the L1 prefers the
opposite convention (record the raw line, as the gate legs do), the
evidence-preserving alternative is to *add* `"error": line` there rather
than delete the binding — a witness addition, out of this seat's mandate.

Next deletion would harm an axis, so I stop here:

- removing `data_64k_aligned`/`data_256k_aligned`/`wave_frames_class`
  checks, `ffprobe_parses`, `paced_expectation` or the `env_override`
  labels → **evidence** axis;
- removing the `arecord -L` enumeration → the device-axis inversion loses
  its premise (evidence);
- pinning the ffmpeg-KILL class to one of {missing, 0-byte,
  placeholder_ff} → over-pins a boundary the author measured both ways
  (falsifiability);
- folding the three gate named-failure legs into one helper → loses the
  per-leg `env_override` witnesses or re-adds the weight as a parameter
  (net zero, and a second convention for one leg);
- merging the r75/r76 tail scrub (C3) or the r75 per-arm `run()` closures
  into `_capture_run` → touches r75 rows for zero line win; a later round's
  job, not this diff's.

## 8. Provenance

Commands (all exits 0 unless noted): `git show d566a31`; `git status
--porcelain -uno` (empty, three times); `python3
corpus/live/r76-simplifier/apply_r76_simplifier_deletions.py <base>
<variant>` (anchor assertions); `python3
corpus/live/r76-simplifier/replay_ab.py` / `replay_ab2.py` (8 passes,
`timeout -s KILL 600 python3 <mirror fixture> --probe-capture-r76`, cwd =
repo root, exit 0, wall ≈ 49 s each); `python3
corpus/live/r76-simplifier/compare_receipts.py`; `python3
corpus/live/r76-simplifier/unused_names.py`; `python3
corpus/live/r76-simplifier/aplay_tail_mechanism.py`. Evidence files:
`receipts/`, `replay-log.json`, `replay-log-round2.json`,
`receipt-compare.txt`, `variants/`, `unused-names-*.txt`,
`aplay_tail_mechanism.out`, `stdout-*.txt` / `stderr-*.txt`,
`mirror/corpus/live/runs/*/measurements.json` (raw pass receipts). Read-only
references: `corpus/live/runs/20261014T182450100472Z-capture-r76` and
`…182539237046Z-capture-r76` (author canonical pair, `ba36cd70…`), the
three real-tree sibling receipts (18:32:15Z/18:33:09Z/18:34:04Z),
`reports/round-76/r76-author.md`. Fixture at HEAD sha
`691d730d…` before and after; no tracked file written by this seat.
