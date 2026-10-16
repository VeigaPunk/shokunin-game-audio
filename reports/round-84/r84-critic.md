# r84 CRITIC — adversarial review of the landed pactl/monitor-tap family (`fbe65713`)

Host `plazir27`, 2026-10-15 21:40–22:00Z (−03 18:40–19:00). Seat: **CRITIC
(wave-B gate, leaf)**. Scope: the r84 landing `git archive fbe65713` →
`~/Projects/shokunin/tmp/r84critic-src` (fixture md5
`1e27992f3e3ab3cfa6ae71841827199a`, sha256
`8ed09d19…`, 22 725 lines, +2 796/−3, 6 entries / 147 legs), against
`reports/round-84/r84-{scout,boundary,author}.md` and the two committed
receipts. Toolchain: PipeWire **1.6.8**, WirePlumber **0.5.17**, pactl
**17.0-98-gb096** (protocol 35), alsa-utils **1.2.16**, Python **3.14.7**
(numpy 2.5.3), kernel **7.2.3-arch1-3**, 32 cores.

**Probe environment.** Ambient load only: loadavg **49.9–55** across the
window (sibling wave-B seats). **Zero tracked writes, no commits, no
`set-default-*`, no foreign object touched.** Seat namespace `r84c_*` (probes)
plus the family's own `r84a_ns_<own pid>` in the replays; every object loaded
by me was unloaded and verified (§5). The worktree **moved under me** during
the window (HEAD `fbe65713` → `2e4e879b` scribe → `38cf715b` simplifier, whose
−7-line patch is *unapplied*; the worktree fixture is still byte-identical to
the pinned blob), so every number below is against the pinned export.
`/tmp` is quota-bound, so the export and all `TMPDIR` work live under
`~/Projects/shokunin/tmp/`.

**Evidence.** `corpus/live/r84-critic/` (MANIFEST.md + SHA256SUMS + 16
receipts/scripts) and one read-only depth-2 labrat receipt audit (folded as §8).

## Verdict

**ADMIT-with-findings.** Every r84 pin reproduces on the pinned commit:
**replay-run2 is a clean green 147-leg run** (`failures: {}`, all six
entries, loadavg ~50, teardown clean) after it serialized behind the
shared-`TMPDIR` flock, and the labrat independently re-derived both committed
receipts as internally consistent with the author's pin table (gain laws
8192→1024 / 27648 / 128, sticky 30 % → tap **221** → repaired 100 %,
`monA_sivol` pre-100 % → ×0.125, `mon_soidx` rc 0 + 44 B, index refusals rc 1
`pa_stream_noent` + 44 B, `-D ''`/`-D -d` argv-eating verbatim, single
capture-refusal class). **But the wave-B co-tenancy regime is defective and
fired live**: (F1) the family lock is `$TMPDIR`-scoped, so my replay and the
verifier's replayed **concurrently** and *both* went red on sibling-attribution
legs (2 reds mine, 3 the verifier's) — a global `new_node_names` delta plus
bound-sensitive gates with no `killed_at_bound` branch (independently found by
the reviewer's F1); (F2) `vol_neg`'s recorded value is never read — live-proven
green with an absolute-10 % write instead of the pinned relative −10 %; (F3)
the ×3.375/×0.015625/mute/0-100 arms carry no absolute base floor —
live-proven green at base 64 (0.8 % of the tone) with a post window of
amplitude 1; (F4) every leg inherits the ambient `PIPEWIRE_*` env (r83-F3
class; `PIPEWIRE_LATENCY` beats `PERIOD_BYTES`, `PIPEWIRE_PROPS` renames a
node); (F5) control receipts (`role_reset.reset_ok`, `pre_reset` rcs,
`sticky.spawn1_percent`, `repaired_mute`, `ctl_arecord_free`, ebusy
`hold_note`) are recorded but never gated. **F1 already produced red wave-B
receipts** (the verifier's and mine); F2/F3 are the only false-green paths and
are latent in both committed runs. The r83 critic's F2 substring-unload defect
is **closed** on this commit (live re-proof, F7).

## 1. Independent replays on the pinned tree

| field | run1 (contaminated) | run2 (serialized, clean) |
| --- | --- | --- |
| command | `python3 corpus/fixtures/measure_audio.py --probe-alsapw-r84` (exported tree) | same |
| `TMPDIR` | `~/Projects/shokunin/tmp/r84critic-tmp` (own lock path) | `~/Projects/shokunin/tmp` (shared lock path) |
| window | 21:40:37 → 21:45:17 | 21:50:00 → 21:55:00 |
| loadavg | 52.4–54.4 | 49.9–51.6 |
| legs | 147 (38/22/14/24/16/33) | 147 (same split) |
| result | `failures`: dev_lattice **2**, other five `[]` | **`failures: {}`** |
| teardown | `sinks_gone` all true; `own_nodes_after []`; unloads rc 0 `recycled false` | same |
| receipt | `replay-run1.measurements.json` (sha256 `20c87e7c…`) | `replay-run2.measurements.json` (`15cf712e…`) |

Run1's two reds are **sibling-attribution artifacts**, not family defects —
proven by the node names inside them and by the verifier's symmetric reds:

- `a_front: rc=0 class=None nodes=['r84a_1682245_hold']` — the *verifier's*
  pw-record hold pin entered this leg's global before/after node delta.
- `a_iec958_d0: rc=0 class=None nodes=['alsa_playback.aplay',
  'r84a_ns_1682245']` — the verifier's plugin node + null sink.
- (sibling, `corpus/live/r84-verifier/runs/r84v1.stdout.json`, read-only
  citation) `a_plughw00: nodes=['alsa_playback.aplay']` — my run's node,
  symmetrically; `pw_server: rc=-9`, `killed_at_bound true`, `wall_s 8.009`
  — the 8 s bound SIGKILLed it (my identical leg: rc 1 `alsa_pw_conn` in
  3 ms); `st_hw00_c1: rc=1 class=None` empty stderr in 1 ms.

Run2 is single-tenant (the reviewer's run queued behind the same flock) and
reproduces every pin exactly. Structural leaf diff of the two committed
receipts (7 985 leaves; 1 235 differ — all pid/path/index/timing/noise, zero
pin/verdict leaves) and md5 equality of each committed receipt with its canon
copy (`6bf2ce12…` / `31e47301…`) were re-derived here.

## 2. Findings, ranked

### F1 — the family lock is `$TMPDIR`-scoped and the dev-lattice arms are not co-tenancy-safe (live-fired; two wave-B receipts red; corroborated by reviewer F1)

`_alsapw_r84_family_lock` (`:19840-19857`) flocks
`Path(tempfile.gettempdir()) / "measure_audio-alsapw-r84.lock"` and its
docstring promises "a second `--probe-alsapw-r84` waits HERE". The wave
instructs seats to use `TMPDIR=~/Projects/shokunin/tmp` **or the lane's
`corpus/tmp`**, so seats get different lock paths and never contend. Live at
21:40: the verifier's run (pid 1682245, shared TMPDIR) and mine (pid 1685102,
`r84critic-tmp`) held sinks **simultaneously** (`r84a_ns_1682245`,
`r84a_ns_1685102`, both `ns2`, plus the verifier's hold pin), then both went
red on legs whose `new_node_names` (`_alsapw_r84_aplay_leg`,
`:19528-19529`) is a **global** `_playback_r78_node_names()` delta with no
pid/tag ownership filter, and the verifier's `pw_server` was SIGKILLed at its
8 s bound (`killed_at_bound true`) with no such branch in its gate. My run2
(shared TMPDIR) queued behind the sibling flock and is green — the lock works
*within* one TMPDIR. **Fix shape:** fixed-path lock (not `gettempdir()`),
ownership-filtered node delta (only nodes carrying our pid/prefix), and a
`killed_at_bound` branch on the bound-sensitive gates (`pw_server`,
`st_hw00_c1`). (`probeD-lock-scope.txt`, `replay-run1.*`, sibling receipt
cited read-only; reviewer §1 F1 found the same lock defect independently and
recorded the same two concurrent runs.)

### F2 — `vol_neg`'s recorded value is never read: the "`-10%` relative" pin is unmeasured (live-proven false-green)

`:21018-21023`: the verdict is only `rc==0 and volume_value is not None`; the
leg records `volume_value` / `volume_percent` / `get_sink_volume` but no gate
compares them with the 90 %-of-base the claim implies. **Proof (probe C, the
committed entry function):** intercepting the single
`set-sink-volume <ns> -10%` call and storing an **absolute 10 %**
(`volume_value 6553`, `get_sink_volume` "10% / −60.00 dB") still yields
`vol_neg_in_failures: []` — green while the pinned semantics are violated
(the relative form must store 58982 = 6553×9). Fix shape: assert the stored
value against the pre-write level (e.g. 0.85–0.95 of the 100 % base and ≠ the
absolute-10 % value). (`probeC-ungated-pins.json`.)

### F3 — the ×3.375 / ×0.015625 / mute / 0-100 arms carry no absolute base floor (live-proven false-green at 0.8 % amplitude)

Only `vol_50_*`/`src_vol50_*` require `base >= 500` (`:20910`). `vol_150`
(`:20915-20921`), `vol_25_idx` (`:20922-20929`), `vol_0_100` (`:20942-20946`)
and `mute_cycle` (`:20954-20958`) accept any truthy base. **Proof (probe C):**
with a synthetic 64-amp base (0.8 % of the real 8192 tone) the entry returns
green for `vol_150` (ratio 3.375, post 216) and `vol_25_idx` (ratio 0.0156,
post **1** — a post window quantized to silence), while the same synthetic
base correctly reds `vol_50_*`/`src_vol50_*` on the 500 floor. Fix shape: one
shared floor on every envelope arm. (`probeC-ungated-pins.json`.)

### F4 — every leg inherits the ambient environment; `PIPEWIRE_*` overrides the flags the family pins (live-proven; r83-F3 class inherited)

All spawn paths default to `env=None` (`_alsapw_r84_run` `:19152`,
`_alsapw_r84_spawn` `:19193`, `_alsapw_r84_play` `:19459`,
`_alsapw_r84_parec_leg` `:19776`, `_alsapw_r84_arecord_leg` `:19572`).
**Proof (probe B, committed bytes):** with `PIPEWIRE_LATENCY=2048/48000` the
`pw_period` leg's `PERIOD_BYTES=4096` device-string arg is overridden —
`node.latency = 2048/48000` (control `1024/48000`): the pin reads a **false
red** under that ambient env, and would read **green** under an ambient value
that happens to equal 1024/48000. `PIPEWIRE_PROPS='{node.name=…}'` renamed an
aplay node (`r84c_envname`) — the dev_lattice witnesses search
`alsa_playback.aplay` by name, so ambient props can break them too. No
current receipt is affected (my shell and both committed runs had no audio
env). Fix shape: spawn legs with an explicit scrubbed env, as the r82
`f0`/`f1` legs already do. (`probeB-env-hermeticity.json`.)

### F5 — control receipts recorded but never gated (latent; both committed runs clean)

- `_alsapw_r84_role_reset` computes `reset_ok` (`:19654`) and every tap leg
  records its four `pre_reset` write rcs (`:19671-19685`); neither is
  referenced by any verdict — a dirty/attenuated pre-state is caught only
  indirectly by the `vol_50` 500 floor (F3 names the arms that escape it).
- `_alsapw_r84_sticky_leg` records `spawn1_percent` (`:21345`) but the verdict
  (`:21308-21322`) never checks it, although the *same* restore-trap guard IS
  enforced on `monA_sivol` (`pre_percent != 100` → failure, `:21269-21273`).
  A key already at 30 % makes the 30 % write a no-op and the arm reads green.
  `repaired_mute` is likewise recorded, not gated (only `repaired_percent`).
- `alsapw_negctl`'s `ctl_arecord_free` records `{"skipped": …}` without a
  `coverage_blocked` entry, and the verdict ignores skips (`:21562-21567`).
- The ebusy busy arm (`:20231-20239`) accepts any RUNNING pcm at probe time;
  `hold_note` (`:20041-20046`) records whether *our* pin flipped it but
  nothing gates it, so a foreign-held device satisfies the arm. Committed
  runs and both my replays: `own pin flipped a pcm`, `card0/pcm1c`; under
  co-tenancy (F1) this attribution is exactly the muddle the lock was meant
  to prevent.

### F6 — disclosure gap: the family lands tones on the shared default sink, undisclosed in the author report

dev_lattice `a_pipewire`/`a_default`, pw_args `pw_node_miss`/`pw_node_mon`
and negctl's 0.8 s `aplay -D pipewire` play 1.4 s tones into the **shared
current default sink** (receipts: `consumers = …SPDIF__sink.29`; negctl's
kill leg plays there too). The receipts record the routing, but the report's
cleanup section says only "zero r84-owned residue" — the boundary disclosed
its own landings; this report doesn't. (The remaining report-vs-receipt
hygiene items are **already adjudicated** — see §"Cross-seat finding set"
below; they are not re-claimed here.)

### F7 — `_alsapw_r84_teardown` inherits the shared unload path, and the r83-F2 destructive shape is now closed (positive; live re-proved)

`_alsapw_r84_teardown` (`:19875-19881`) routes through `_gst_r81_unload_own`
→ `_gst_r81_sink_module_index`, whose committed form (`:12803-12824`) is an
**anchored** `re.search(r"sink_name=(\S+)")` + exact field equality (the r83
critic's F2 fix). Live re-proof on the committed bytes: with `r84c_a` +
`r84c_a2` loaded, `_gst_r81_unload_own(idx_a, "r84c_a")` unloaded **`r84c_a`
only** (`a2_survived: true`); with only `r84c_ns_12` loaded a `r84c_ns_1`
query returned **None** and unloaded nothing (the pid-prefix nesting case the
r84 family's own names can produce); a mismatched captured id unloaded the
*name-verified* module, never the foreign one. (`probeA-unload-anchor.json`,
`probeA2-prefix-nesting.json`.)

## 3. Cross-seat finding set (cited, not re-litigated)

- **reviewer** (`2e4e879b`-era): F1 lock scope (independently found, see my
  F1); F2 the sticky respawn median is read over a mixed pre/post-repair
  window (14/25 samples pre-repair; ~0.2 s of scheduling from flipping the
  gate) — accepted, orthogonal to my F5; F3 gain-law envelopes wider than the
  measured law (up to −36 %/+54 % on the index pin); F4 six report-vs-receipt
  hygiene items; F5 the tap legs' recorded `stream_input` leaf is a pre-route
  read (record-only); F6 refinement #1's different-tag counterexample is
  prose-only.
- **scribe**: ADJ-1 `loadavg >100` contradicted by the receipts (51.3–59.2);
  ADJ-2/3 leg/class count defects; ADJ-4 sticky "different-tag 100 %" has no
  witness leg; ADJ-6 receipts carry no fixture identity; ADJ-7 dirty tracked
  `.pyc`; ADJ-8 path shorthand; custody INTACT.
- **simplifier**: T1–T10, net **−7** lines, patch **unapplied**, no verdict
  or receipt-key change.
- **verifier**: `r84v1` red (3 failures) — the F1 co-tenancy instance; the
  second verifier run (pid 1739244) serialized behind the shared lock.

## 4. What survived the attack (worth saying)

- **The content witness is pid-keyed and per-sink**: taps run on probe-owned
  sinks only, the A pair is the r78 pid-offset (`997 + 211·(pid%4)`, `+503`)
  and stream B is the 2700 Hz discriminator; the `sink_monitor` A+B control
  and every `monA_*` A-only pin hold in both committed receipts and both of my
  replays.
- **Fail-closed where it matters**: refusal legs gate rc **and** class **and**
  output-file absence; the single `alsa_pw_capture_refusal` class matches
  either marker of the one stderr dump (the boundary's falsification is
  genuinely folded); `-D ''` vs `-D -d` argv-eating is pinned in both tools;
  `mon_bad0`/`mon_deadidx` gate rc + class + ≤200 B + `data_actual == 0`;
  `mon_soidx` gates rc + empty body; `monA_move` gates post-move sig set
  **and** the resolved sink index; `monA_sivol` gates the pre-percent (the
  restore trap the scout's C34 fell into); `sticky` gates percent + 221 amp +
  repair.
- **Teardown discipline**: every unload re-reads the module table and records
  `verified_index`/`captured`/`recycled`; `sinks_gone` + `own_nodes_after`
  are gated; both committed runs and both my replays are clean (no `r84a_*`
  node survives, no `r84c_*` object at all).
- **The r83-F2 exposure is closed** (F7) in the shared helper — r81/r82/r83/r84
  all benefit.
- **Receipts are honest**: every unmeasured arm is a named outcome where it
  matters (`mon_soidx` skipped → failure; ebusy arms adaptive with the
  `/proc` witness recorded), and each committed receipt is byte-identical to
  its canon copy.

## 5. Probe summary (all under ambient load; `r84c_*` namespace)

| probe | result |
| --- | --- |
| replay run1, pinned export, concurrent sibling | 147 legs; 5/6 entries green; 2 reds = sibling nodes in `new_node_names` (F1) |
| replay run2, pinned export, shared TMPDIR | **147 legs, `failures: {}`, teardown clean** |
| unload predicate, nested `r84c_a`/`r84c_a2` | correct module unloaded, nested survivor intact (F7) |
| unload predicate, pid-prefix `r84c_ns_1`/`r84c_ns_12` | short-name query → None, unloads nothing (F7) |
| `PIPEWIRE_LATENCY=2048/48000` + `PERIOD_BYTES=4096` | `node.latency = 2048/48000` (control 1024/48000) (F4) |
| `PIPEWIRE_PROPS={node.name=…}` + aplay | node renamed `r84c_envname` (F4) |
| committed entry + intercepted `-10%` → absolute 10 % | green; `vol_neg` value 6553 never read (F2) |
| committed entry + synthetic 64-amp series | `vol_150`/`vol_25_idx` green (post 1); `vol_50`/`src_vol50` red on the floor (F3) |
| residue | zero `r84c_*` modules/sinks/processes; defaults unchanged (SPDIF / Line) |

## 6. Contention ledger (by name; never touched)

- **Sibling wave-B runs (same family)**: verifier pid 1682245
  (21:40:27→21:45:16, rc 1), a second verifier run pid 1739244, the reviewer
  pid 1743076 (queued behind the shared lock), my replays pid 1685102 (run1)
  and 1740760 (run2). The verifier/critic pair is the F1 live instance.
- **Pre-existing foreign sink `r84a_probe_548706`** (module 536870923,
  SUSPENDED) — present at my entry, never touched (the author and the r82
  verifier2 both document it as foreign).
- Sibling seats' non-audio work (g3d/r92 Godot runs) — CPU load only.
- Default sink/source unchanged across the window
  (`…SPDIF__sink.29` / `…Line__source.29`).
- Interference caused by me: bounded tones into the **default sink** from the
  family's own lattice legs (as in the author's runs); own-sink tones from my
  probes; one pw-record pin on the default source held ≤5 s by the
  dev_lattice ebusy arm (family design); the private restore key
  `r84arole<my pids>` repaired/verified by each replay's teardown; all my
  `r84c_*` objects/processes gone and my `TMPDIR` scratch removed.

## 7. Receipts index (sha256, `corpus/live/r84-critic/`)

| artifact | sha256 (prefix) |
| --- | --- |
| `replay-run1.measurements.json` (contaminated 147-leg run) | `20c87e7cafd931e2…` |
| `replay-run1.stdout.json` / `.stderr.txt` | `4b168823b257a622…` / `e3b0c442…` (empty) |
| `replay-run2.measurements.json` (green 147-leg run) | `15cf712e2097eb6a…` |
| `replay-run2.stdout.json` / `.stderr.txt` | `4460cb584519dd6b…` / `e3b0c442…` (empty) |
| `probeA-unload-anchor.py` / `.json` | `e4e4ab3a629cc068…` / `1d2625a63d846e84…` |
| `probeA2-prefix-nesting.py` / `.json` | `281c3c2bd7b5de7e…` / `e7fc6e72a64ca639…` |
| `probeB-env-hermeticity.py` / `.json` | `d2b0f7de01d54e43…` / `0fcf0fb64fe36f51…` |
| `probeC-ungated-pins.py` / `.json` | `fd0252826f834b6d…` / `920855e717057d81…` |
| `probeD-lock-scope.txt` | `cc729cfc320c2a68…` |
| `pre-state.txt` | `1fa481a6431c2cb6…` |
| `SHA256SUMS` / `MANIFEST.md` | full list / provenance |

## 8. Remaining risks / blockers

- **F1** is the finding that already changed wave-B outcomes: two seats'
  replays are red for sibling-attribution reasons and a third reader could
  mistake them for family defects. Two-line-class fix (lock path + ownership
  filter) plus a `killed_at_bound` branch on the bound-sensitive gates.
- **F2** is the only live-proven false-green on a claim the report makes
  (`-10%` relative); one value assertion closes it.
- **F3** is latent in the committed runs (base 8192) but lets a quiet or
  partly-broken leg read green; one shared floor closes it.
- **F4** is family-wide (r82/r83 share the `env=None` convention).
- **F5/F6** are coverage/disclosure nits; no committed receipt is affected.
- Reviewer F2's one-sample sticky margin means a future run can report a
  sticky failure that is scheduling, not regression.
- Nothing blocks the ledger standing. No shipping decision is made here
  (canonical judge's call).

Report ends. No tracked edits, no commits, no pushes; `r84c_*` objects fully
torn down and verified.

## 9. Labrat receipt audit (read-only, depth-2; folded)

Independent audit of both committed receipts (`corpus/live/r84-author/runs/`):
**CONFIRMED** — 6 entries / 147 legs (146 dict legs + the scalar `hold_exit`),
`failures: []` in all six, every headline pin present and in-envelope, no
`coverage_blocked`/`skipped`/`action_error`/null gate input anywhere; the
9 `exists: false` legs are refusal arms (absence *is* the result), not
unmeasured pins. It independently reached the "identical bytes" and
`coverage_blocked: null` wording nits (already the reviewer's F4 / scribe
ADJ-1..3) and added: the receipts carry no timestamp/run-id field (the stamp
lives only in the directory name), and the canon↔author copies are
byte-identical. It could not run a leaf-by-leaf diff (grep/read-only seat);
this report's structural diff (§1) covers that gap.
