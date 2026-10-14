# R76 verifier — capture arm (`--probe-capture-r76`), post-commit independent verification

Seat: verifier (LEAF). Repo `~/Projects/shokunin/audio-shokunin`.
Commit under test: **`d566a317e6b849032c444155e933b33a102bbada`** (r76 capture-side
consumers). Fixture under test: `corpus/fixtures/measure_audio.py` at
**HEAD blob `691d730d4b4b2aa1475aa03bd4d9d7b5c9bdd3baf6a62d24923097f6fb9e9734`**.
Every measurement below was taken against that blob (all runs finished before
19:26:01 UTC; see §7 for the concurrent working-tree edit that landed after).

Scratch: `corpus/live/r76-verifier/` only. No tracked file was modified by this
seat.

## §0 Bottom line

The arm's **pinned classes are correct** — I reproduced every byte-level shape I
tested, including the two accept-and-lie placeholders and the exact
`192044`/`960044` sizes, and the **17 base rows are byte-identical** to the r75
canonical. The prior arm is intact.

The **canonical receipt sha did not reproduce deterministically**: `ba36cd70…`
came back on **1 of 3** runs; the other two produced different shas — and **all
three reported `failures: {}`**. The two deviations were real (a 15 s blocked
leg; a missing-file `alsa_busy` leg) and the failure carrier did not record
either. I also found **two legs the arm never checks at all** (`ffmpeg_alsa_t`
in the bounded entry; `sysdefault`/`plughw_first`/`hw_first` in the device-axis
entry) — both fired in my runs and both still passed. The critic's D1 vacuity
hole is **not latent**: a `SIGTERM` inside parecord's dead start produces
exactly the `rc=0 + finalized + zero-audio` shape the gate accepts.

All three gaps survive the sibling seat's in-flight fold-in (§7).

## §1 Claim-by-claim verdicts

| # | Claim (source) | Verdict | Evidence |
| --- | --- | --- | --- |
| 1a | `--probe-capture-r76` → `failures: {}` | **AGREE** | 3/3 runs (`T192041795661Z`, `T192133221690Z`, `T192337920612Z`), `EXIT=0`, each under `timeout -s KILL 480` |
| 1b | receipt sha256 == `ba36cd70f765826a9937fc78c62143c984790f1bdc26a4ad8aaf813cfc00f92f` | **DISAGREE** (1/3) | run3 `ba36cd70…` ✓; run1 `94150fbc…`; run2 `4b9d4897…`. Determinism is **not** established by 3 runs, and the deviating runs are **indistinguishable from the canonical one by `failures`** (§2) |
| 1c | briefed "quiescent-host sensitivity" limited to `inventory.pw_capture_ports` and an aplay `stderr_tail` window | **DISAGREE** | `pw_capture_ports` did differ (12→14) but **not** in the way briefed, and **three further leaves** deviated outside the allowance: `device_axis/legs/sysdefault`, `bounded/legs/ffmpeg_alsa_t`, `sever/cells/arecord_{term,kill}/device`. No aplay tail leaf appears in r76 at all |
| 2a | `--probe-consumers2-r75` still runs clean | **AGREE** | `T192523848909Z`, `failures: {}`, `EXIT=0` |
| 2b | the 17 base rows byte-identical vs the r75 canonical receipt | **AGREE** | **0 differing leaves** vs *all three* candidate r75 receipts: canonical `9de8b8f8` (`T172034398145Z`), `0829a598` (`T165017429491Z`), critic replay `6ffb0f81` (`T183519581984Z`) |
| 2c | full r75 tree stability | **AGREE** | exactly **1** differing leaf vs r75 canonical: `consumer2_paplay_ops_r75_probe/daemon_gate_dead/wall_s` `0.001 → 0.002` (the pre-existing unbucketed wall float the critic named). **0** leaves vs the critic's replay `6ffb0f81` — my replay is byte-identical to the critic's |
| 3a | pw-record TERM finalizes / KILL wounds | **AGREE** | TERM: `rc=1`, `286764 B`, riff `finalized` (`286756 == bytes-8`), `data 286720 == 286720`, wave opens `71680` frames. KILL: `rc=-9`, `riff_sz=8`, `data_decl=0` over `282624` real bytes, **stdlib wave rejects** (`Error`) |
| 3b | parecord TERM finalizes / KILL wounds | **AGREE** | TERM: `rc=0`, `131116 B`, finalized, `data 131072 == 131072`, 64-KiB-aligned, wave opens. KILL: `rc=-9`, `riff_sz=8`, `data_decl=0` over `131072`, wave rejects |
| 3c | arecord KILL `0x80000000` accept-and-lie | **AGREE** | `rc=-9`, `264044 B`, `data_decl=0x80000000`, `data_actual=264000`, honest `66000` frames, **stdlib wave reports `536870912` frames = 8134×**. Reproduced on a free device after the first attempt hit a busy card. The lie also holds with **zero** audio (see §5) |
| 3d | ffmpeg `0xFFFFFFFF` inflated / 0-byte class | **AGREE** | TERM: `rc=255`, `489678 B`, finalized, `data 489600 == 489600`, wave opens `122400` frames (**rc=255 with a usable file**). KILL: `rc=-9`, `262144 B`, `riff=0xFFFFFFFF`, `data_decl=0xFFFFFFFF` over `262066`, wave opens `1073741823` frames = **16389×** inflated. (The 0-byte sub-class is a *union member* in the receipt; not drawn this pass) |
| 3e | rc is never the verdict | **AGREE** (all three named cases) | `rc=1` complete capture: `286764 B` finalized, wave opens. `rc=0` **empty**: reachable — see §5. `rc=255` valid: `489678 B` finalized, wave opens |
| 3f | arecord `-D null -d 1` → `~192044 B` in `~0.02 s` | **AGREE** (size exact; the time figure is conservative) | `rc=0`, **exactly `192044 B`**, wall **`0.001 s`**. The briefed `~0.02 s` and the author's `~0.01 s` are both 10–20× high; the class ("unpaced, CPU-speed") is right |
| 3g | parecord has a `~1.9 s` dead start | **AGREE** (within granule resolution) | two-point fit: TERM@4.0 s → `393216 B`; TERM@8.0 s → `1114112 B`. At the true 48000 Hz: `2.048 s` / `5.803 s` captured ⇒ dead start **1.952 s / 2.197 s**; boundary seat's 8 s point gives `1.856 s`. All within **one 64-KiB granule = 0.341 s**, which is the fit's resolution limit. See §4.3 for the rate trap |
| 3h | roundtrip monitor capture = `960044 B` nonzero | **AGREE** | `960044 B == 44 + 240000×4`, finalized, `nonzero_fraction 0.780`, `peak 5648`, `pw-cat rc=0`. Plus the canonical receipt's own `nonzero_fraction_gt_half`/`peak_within_3db` witnesses on 3/3 runs |
| 4a | `data_actual_zero` is recorded on HEAD | **AGREE** | `measure_audio.py:3334` — recorded on sever cells (and only there) |
| 4b | the **current canonical** receipt's `parecord_term` carries nonzero audio | **AGREE** | `data_actual_zero: false` **and** `data_64k_aligned: true` ⇒ `data_actual` is a positive multiple of 65536. Same on my runs 1–3. (The receipt carries no byte count for sever cells — those two derived leaves are the only evidence) |
| 4c | the critic's D1 is real (two receipts with `data_actual_zero: true` still passing) | **AGREE** | `T181454123380Z` and `T181743427243Z` both carry `parecord_term/file/data_actual_zero: true` + `wave_frames_class: honest_empty`; `T181743427243Z`'s sever entry `failures: []` |
| 4d | the hole is still live on HEAD | **AGREE — and it is reachable, not latent** | two unchecked sites (§5) + a trivially producible accepted shape |
| 5 | fixture sha on HEAD == `691d730d…` | **AGREE** | `git show HEAD:corpus/fixtures/measure_audio.py \| sha256sum` → `691d730d4b4b2aa1475aa03bd4d9d7b5c9bdd3baf6a62d24923097f6fb9e9734`. **Working tree now differs** — see §7 |
| N1 | (new) `ffmpeg_alsa_t` is checked | **DISAGREE — no check exists** | §6 |
| N2 | (new) device-axis hw-route legs are checked | **DISAGREE — no check exists** | §6 |

## §2 Reproduction — 3 runs, 2 deviating, 3 × `failures: {}`

| run | receipt | sha256 | `failures` |
| --- | --- | --- | --- |
| 1 | `T192041795661Z-capture-r76` | `94150fbc1a5a3ccc1829bf52a48c5ef5e8f1d67e2bd1dbb1ad234ab9102c62a7` | `{}` |
| 2 | `T192133221690Z-capture-r76` | `4b9d4897a75a32bbcc0c04c389d9f737eb512c5aee312352a891e3d1733d69a5` | `{}` |
| 3 | `T192337920612Z-capture-r76` | **`ba36cd70f765826a9937fc78c62143c984790f1bdc26a4ad8aaf813cfc00f92f`** | `{}` |

A key-walk of the JSON trees (not a hash compare) isolates the deviating leaves:

- **run1** — `capture_device_axis_r76_probe/legs/sysdefault`: `blocked False → True`,
  `error: "blocked: no verdict within 15 s"`, `exit_code 0 → null`,
  `file/bytes 192044 → 44`, `data_actual 192000 → 0`,
  `riff_size_field finalized → other`, `data_finalized True → False`.
  `capture_device_axis_r76_probe.failures` stayed `[]`.
- **run2** — `capture_bounded_r76_probe/legs/ffmpeg_alsa_t`: `exit_code 0 → 251`,
  `error_class null → alsa_busy`, `error "Device or resource busy"`,
  `file: {exists: True, riff finalized, duration_bucket_s 1.0} → {exists: False, kind: "missing"}`.
  `capture_bounded_r76_probe.failures` stayed `[]`.
- **run2** — `capture_sever_r76_probe/cells/arecord_{term,kill}` fell from
  `hw:0,0` to `hw:0,2` after `arecord_contention` recorded `alsa_busy` on
  `hw:0,0` and `hw:0,1` (the arm's designed named-failure path).
- **run2** — `capture_gate_r76_probe/inventory/pw_capture_ports` `12 → 14`, the
  extra two being **`pw-record:monitor_FL` / `pw-record:monitor_FR`**.

**Root cause of run2's contamination — measured, not inferred.** Those two extra
ports are a **live `pw-record` node**, i.e. the *previous run's own* pw-record
legs were still registered when run2 took its inventory (run1 ended 19:20:41,
run2's gate ran ~19:20:42–45). A 1 Hz port sampler across run3 shows the same
teardown lag: 2 live `pw-record` ports still present at **19:23:38–39**, i.e.
≥1 s *after* run3's receipt was written at 19:23:37. A live PipeWire capture
node contends for the ALSA card, which is exactly what run2 saw (`ffmpeg -f alsa
-i plughw:0,0` → `alsa_busy`; `arecord hw:0,0`/`hw:0,1` → `alsa_busy`).

So the canonical sha is a **host-state-dependent** value, and the arm's
`failures: {}` cannot distinguish a clean run from a contaminated one — the
operational form of the critic's D2/D3 family. Two isolated primitives
(`pw-record -n N` via `subprocess.run`, and the roundtrip spawn) exit and
release cleanly when run in isolation (`corpus/live/r76-verifier/leak_test.py`);
the lag is a PipeWire node-teardown property, not a leaked process — no
`pw-record` process was alive at any check.

## §3 Prior-row stability (item 2) — AGREE

```
timeout -s KILL 480 python3 corpus/fixtures/measure_audio.py --probe-consumers2-r75
→ corpus/live/runs/20261014T192523848909Z-consumers2-r75   failures: {}
→ sha256 6ffb0f819ea998cc75413b0e04d5f068d29cc8d52f52936ffaa5fc54beb4c410
```

That sha is **byte-identical to the critic's r75 replay** (`T183519581984Z`,
`6ffb0f81…`) — 0 differing leaves in the whole tree. Against the r75 canonical
`9de8b8f8…` (`T172034398145Z`) the 17 base rows differ in **0 leaves** and the
full tree in exactly **1** (`daemon_gate_dead/wall_s 0.001 → 0.002`). The same
0-leaf result holds for the 17 base rows against `0829a598…`. The r75 arm is
therefore *more* reproducible than the r76 arm on the same host in the same
window.

## §4 Byte-level spot verification (item 3)

All numbers below are re-derived from raw bytes by
`corpus/live/r76-verifier/spot_verify.py` + `followup.py`, which do **not**
import the fixture's classifiers.

### 4.1 Sever matrix — re-measured

| cell | rc | bytes | riff field | declared vs actual | stdlib `wave` |
| --- | --- | --- | --- | --- | --- |
| pw-record TERM | 1 | 286764 | finalized | 286720 == 286720 | opens, 71680 frames |
| pw-record KILL | −9 | 282668 | **8** | 0 over 282624 real | **rejects** (`Error`) |
| parecord TERM | 0 | 131116 | finalized | 131072 == 131072 (2×65536) | opens, 32768 frames |
| parecord KILL | −9 | 131116 | **8** | 0 over 131072 real | **rejects** |
| ffmpeg TERM | 255 | 489678 | finalized | 489600 == 489600 | opens, 122400 frames |
| ffmpeg KILL | −9 | 262144 | **0xFFFFFFFF** | 0xFFFFFFFF over 262066 | opens, **16389×** inflated |
| arecord KILL | −9 | 264044 | `other` (0x80000024) | **0x80000000** over 264000 | opens, **8134×** inflated (536870912 vs 66000) |

TERM finalizes for all four consumers; KILL wounds are consumer-specific; the
wave/ffprobe tolerance split is as pinned. This independently reproduces the
reviewer's table line for line.

### 4.2 The 0-byte KILL sub-class
The receipt pins ffmpeg-KILL as a **union** (`missing` ∪ `0-byte` ∪
`riff=placeholder_ff`), so the 0-byte branch is not falsifiable per-run and I
did not draw it. The `placeholder_ff` branch is confirmed above.

### 4.3 `parecord`'s header rate is a **mislabel** (new, and it moves the 1.9 s fit)

`parecord -d @DEFAULT_SOURCE@` with a 4.0 s window produced `data_actual = 393216`
**both** with the default header and with `--rate=48000`:

| argv | header rate | `data_actual` | rc |
| --- | --- | --- | --- |
| `parecord -d @DEFAULT_SOURCE@` | **44100** | 393216 | 0 |
| `parecord -d @DEFAULT_SOURCE@ --rate=48000` | 48000 | 393216 | 0 |

Identical byte counts for the same window rule out resampling: the stream is
**48000 Hz** and the default header simply says `44100`. Consequence: any
duration derived from the header (as a naive reader, and as my own first fit,
does) over-states the captured span by 8.8 % and under-states the dead start by
~0.19 s on a 4 s window. The boundary seat's 48000-based fit
(`1.952 / 1.856 s`) is the correct one; a header-trusting reader gets
`1.68 / 1.77 s`. The pinned `~1.9 s` holds either way within the 0.341 s
granule.

### 4.4 Roundtrip
`960044 B == 44 + 240000×4`, `data_finalized: true`, `nonzero_fraction 0.780`,
`peak 5648`, `pw-cat -p` rc=0. My first attempt reported a DISAGREE
(`nonzero_fraction 0.000`) because **my harness used the wrong member path**
(`artifacts/…` instead of `corpus/artifacts/…`), so `pw-cat` exited rc=1 and
captured silence. Corrected and re-run: AGREE. The harness bug is recorded here
rather than silently dropped.

## §5 Vacuity check (item 4) — measured, not fixed

`data_actual_zero` **is** recorded on HEAD (`:3334`), and the **current canonical
receipt's** `parecord_term` **does** carry nonzero audio (`data_actual_zero:
false` + `data_64k_aligned: true`). The critic's D1 is nevertheless real — the
two historical receipts named above carry `data_actual_zero: true` with
`honest_empty` and passed.

The hole is live in **two** places on HEAD, and it is **reachable by design, not
by accident**:

- `capture_bounded_r76_entry` parecord TERM check (`:3609-3612`) tests only
  `exit_code == 0 and data_finalized and data_64k_aligned`. `0 % 65536 == 0`
  and `0 == 0` both hold on an empty capture.
- `capture_sever_r76_entry` TERM check (`:3725-3728`) tests only
  `exit_code == exp.term_rc and data_finalized is exp.term_final` — no
  `data_actual_zero`.

**Reachability probe (my C3):** `parecord -d @DEFAULT_SOURCE@` severed at
**0.4 s** — inside the ~1.7–2.2 s dead start — lands

```
rc=0   bytes=44   riff_sz=36 (finalized)   data_decl=0   data_actual=0
stdlib wave opens, getnframes()==0
```

which is precisely the shape both checks accept. No device fault is required,
only a signal that arrives early. A verifier who wanted to certify "parecord
TERM ⇒ rc=0 with audio" cannot do so from this carrier.

Scope note: this is **measure-and-report**; I applied no fix.

## §6 New findings — two legs with no check at all (both fired, both passed)

**N1 — `capture_bounded_r76_entry` never checks `ffmpeg_alsa_t`.**
The leg is only *assigned* (`:3577`, `:3582`); the entry's last
`failures.append` belongs to `ffmpeg_pulse_t` (`:3631`). It is the **only** leg
in that entry with no verdict check. In run2 it returned `rc=251`
`alsa_busy` with `file.exists: false` (no file written) and the entry still
returned `failures: []`.

**N2 — `capture_device_axis_r76_entry` never checks the hw-route legs.**
It checks only `default`, `pipewire`, `null` and `hw_first_mono`
(`:3907`, `:3914`). `sysdefault`, `plughw_first` and `hw_first` are recorded and
then never inspected. In run1 `sysdefault` blocked for the full 15 s bound
(44 B, `riff_size_field: other`, `data_actual 0`) and the entry still returned
`failures: []`.

Both are the same family as the critic's D2 (a conditional/skipped leg passing
silently), but neither is latent: each fired in one of my three runs.

## §7 Concurrent-edit condition — verification boundary (blocker for re-verification)

`corpus/fixtures/measure_audio.py` was **modified in the working tree during
this session by a sibling seat**, not by me:

- HEAD blob: `691d730d4b4b2aa1475aa03bd4d9d7b5c9bdd3baf6a62d24923097f6fb9e9734`
  (the artifact I verified — `git show HEAD:…`).
- Worktree at 16:26:01 local: `30a5d7f3…`; ~30 s later: `eb3bcfae…`
  (still being written; snapshot preserved at
  `corpus/live/r76-verifier/worktree-snapshot.py`).
- `git status --porcelain` → ` M corpus/fixtures/measure_audio.py`
  (23 insertions / 8 deletions), folding r76 critic/reviewer corrections:
  `seq[:=]` tail regex, `data_4k_aligned` removal, a `fmt_absent`
  `wave_frames_class`, a gate `leg absent` failure, `_capture_sever_cell`'s
  unused `env` parameter removed (no caller passes it — no `TypeError`), and
  unused-variable cleanups.

**All measurements in this report are against `691d730d`** (run3 finished
19:23:37, the r75 replay 19:25:23, the edit landed 19:26:01).

**The in-flight edit does not close any of my three findings.** In the
`eb3bcfae` snapshot: `ffmpeg_alsa_t` is still assignment-only (N1), `sysdefault`
is still unchecked (N2), and `data_actual_zero` still appears only at `:3334`
as a *recording*, never as a *test* (§5). Any re-verification must therefore
target the post-fold blob, and the three gaps will still be there.

## §8 Evidence index

`corpus/live/r76-verifier/`:

| file | what |
| --- | --- |
| `run{1,2,3}.stdout.json`, `run{1,2,3}.stderr.log`, `run{1,2,3}.exit` | the three arm runs |
| `r75.stdout.json`, `r75.stderr.log`, `r75.exit` | the prior-row replay |
| `leak_test.py`, `leak_test.log` | isolated pw-record primitive leak probe |
| `spot_verify.py`, `spot_verify.log`, `spot_verify.json` | byte-level re-derivation (C1–C8) |
| `followup.py`, `followup.log`, `followup.json` | C5′/C8′/C9 resolutions |
| `port_sampler.log` | 1 Hz `pw-link` node census across run3 |
| `worktree-snapshot.py` | the sibling seat's in-flight fixture (`eb3bcfae…`) |

Receipts written by this seat (untracked scratch under `corpus/live/runs/`):
`T192041795661Z`, `T192133221690Z`, `T192337920612Z` (`-capture-r76`),
`T192523848909Z` (`-consumers2-r75`).

## §9 Remaining risks / blockers

1. **Canonical-sha determinism is unproven and the failure carrier cannot see
   the difference.** 1/3 reproduction; a contaminated run and a clean run both
   read `failures: {}`. Any claim of the form "byte-identical ×N" should be read
   as *N runs that happened to agree*, not as a determinism property.
2. **Three unchecked legs** (`ffmpeg_alsa_t`; `sysdefault`/`plughw_first`/
   `hw_first`) — verified to still be unchecked in the in-flight fold.
3. **The parecord TERM vacuity hole is reachable** with a single early signal
   (§5), on both the bounded and sever checks.
4. **parecord's default header rate is a mislabel** (44100 header / 48000
   stream) — any downstream consumer that trusts the header mis-times the file
   by 8.8 % (§4.3).
5. **Unresolved:** the exact mechanism by which a `pw-record` node survives its
   process by ≥1 s (PipeWire teardown lag vs. something in the arm). The
   consequence (cross-run inventory and ALSA contamination) is measured; the
   mechanism is not.
6. **Blocker for re-verification:** the tracked fixture is being rewritten
   concurrently (§7). Any verdict must name the blob it was taken against.
7. Not verified by this seat: the in-flight fold's own correctness (out of
   scope — it is not the artifact assigned to me).
