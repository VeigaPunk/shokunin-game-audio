# r83-critic manifest

Seat: CRITIC (wave-B gate, leaf, frozen probeParent). Repo
`/home/vgpnk/Projects/shokunin/audio-shokunin`; every measurement is against a
**commit pin** — `git archive a151a226` -> `/tmp/r83critic-src` (fixture md5
`1fd0a2496b8fb2c4f65b58b33fe044f1` = committed blob `27fe9710…`; the worktree
drifted to `bc3f55ca`/`2b221233` mid-window and its fixture is dirty from a
sibling fold — never used).

Host `plazir27`, 2026-10-15 22:11–22:21Z (-03 19:11–19:21). PipeWire 1.6.8,
pactl 17.0-98-gb096, WirePlumber 0.5.17, Python 3.14.7, numpy 2.5.3, kernel
7.2.3-arch1-3, 32 cores. Ambient load only: loadavg 75.98 at replay start,
81.6 mid-replay, 122–124 during the probes (sibling seats). No hogs of mine.
Zero tracked writes, no commits, no `set-default-*`, no foreign object touched.
Seat namespace `r83c_*`; every module loaded by this seat was unloaded and
verified gone; defaults unchanged (`…SPDIF__sink.29` / `…Line__source.29`).

| artifact | sha256 | bytes |
| --- | --- | --- |
| `labrat-receipt-audit.md` | `5fef38c038c59c166486a8731abfbd81ba4ce11f7b72c73655a9546dce228f72` | 4094 |
| `probeA-onset-hole.json` | `102dd07405f6a5183ff89294e8ab42925e021998caeb44388eed924eb40bc8c1` | 1027 |
| `probeB-unload-substring-run1.json` | `37a151874c139ac867b93bf7aca76a23b0a398a4af307e1eb2c7a8428dee99c9` | 659 |
| `probeB-unload-substring-run2.json` | `bddb848763d253d39e4ef1ba52d69374e048ac0fbc85e1c207c3ec7aee51b0f9` | 712 |
| `probeC-env-hermeticity.json` | `5e155cd829953a69ccc88f51b660a75489e9e16248153c03e236777eee07e97d` | 6927 |
| `probeD-failopen-env.json` | `723254a5dc1d7e51377ed2afc71a52b386189953866d29233cc467db23ae84d4` | 992 |
| `probe_env_hermeticity.py` | `f2613d45f4144fc051dee9cb60659cc3e4cc83bed0152f2ff7f744db81d617db` | 4937 |
| `probe_failopen_env.py` | `261fdada589c71d2d2b972d072288086cc1b7c18b25e7af43dd44da39d2e87ab` | 2536 |
| `probe_onset_hole.py` | `e04d648a7efc7f055c4d2195d2c698007442a254f422f3df41a8376bc35499cf` | 2137 |
| `probe_unload_substring.py` | `d5abf36b8d7dc1cbaf8be8faf1878950da138e98fbd57dd2dd06822454fc37a0` | 2363 |
| `receipt-audit.txt` | `fe01ac83295f7c588cf9e234eceb38636188965ccd62fe5ea71e108ecc1b1a81` | 12691 |
| `replay-run1.measurements.json` | `60a235c6b916c824b355da3de6fd506c443662f5d8089663bcfc83cc6e15a8b0` | 782902 |
| `replay-run1.stderr.txt` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | 0 |
| `replay-run1.stdout.json` | `4c8248fd6304cd9c833445b5808fd5e7ed8cd422820880209832dfd9ed25dbed` | 118 |

## Artifact notes

- `replay-run1.measurements.json` — the full `--probe-pwcat-r83` replay on the
  pinned export: 7 entries / **128 legs** / `failures {}`; all 14 unloads rc=0
  `recycled=false`; `sinks_gone` all true; `own_nodes_after []`. Run dir
  `20261015T221700821010Z-pwcat-r83` (22:11:54Z→22:17:00Z, loadavg 76–82).
- `replay-run1.stdout.json` / `.stderr.txt` — the runner's summary line and its
  (empty) stderr.
- `probeA-onset-hole.json` — committed `pwcat_latency_props_r83_entry()` with the
  four d025/l1000 onset reps monkeypatched to the real `blocked` shape: entry
  returned `failures: []` with `d025_transports: []`, `l1000_transports: []`.
- `probeB-unload-substring-run{1,2}.json` — `_gst_r81_sink_module_index` /
  `_pwcat_r83_unload_own` against nested probe-owned names (`r83c_a`, `r83c_a2`):
  run 1 returned the nested module's index and destroyed it (rc=0,
  `recycled: true`); run 2 (fresh indices, reversed listing order) picked
  correctly — selection is listing-order dependent.
- `probeC-env-hermeticity.json` / `probeD-failopen-env.json` — ambient
  `PIPEWIRE_LATENCY`/`PIPEWIRE_NODE`/`PIPEWIRE_PROPS` override r83 leg flags
  (`-l 5`→`1024/48000`; `-C`/`-P ''` steered to the env node; env node.name
  lands); `PULSE_SINK` has no effect on native clients.
- `probe*.py` — the four probe harnesses (they import the pinned export only;
  `PYTHONDONTWRITEBYTECODE=1`).
- `receipt-audit.txt` — 3-way audit of run1/run2/critic-replay: per-entry legs,
  failures, teardown witnesses, onset/matrix/resample/remix/failopen summaries.
- `labrat-receipt-audit.md` — the single frozen-probeParent depth-2 read-only
  audit of the two committed receipts (verdict **CONFIRMED**; 4 minor nits).

## Contention (never touched)

`r83a_4030452` sibling family run live in `pw-dump`/`ps` throughout the probe
window (modules `r83a_ns_{a,b}_4030452`, in-flight `pw-loopback -n
r83a_4030452_l2_5` / `…_lneg5`); sibling fold rewriting the worktree fixture at
19:16:13; wave-B commits `bc3f55ca`/`52c5d807`/`2b221233` landing mid-window.
The pre-existing tracked `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`
modification predates this seat.
