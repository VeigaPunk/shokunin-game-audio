# r79-author receipts — provenance and artifact index

Seat: AUTHOR (audio-shokunin round 79). Repo `~/Projects/shokunin/audio-shokunin`
@ HEAD `a2616f732253ed90110ba16a223ec7d10224740c` (`r78 LOG: adjudicator
ADMIT-corr`). Host `plazir27`. **No commit — the tree is left dirty by design.**

## Frozen artifact (the only tracked edit)

```
corpus/fixtures/measure_audio.py
  sha256 4ee754b3fa7dab6c7be7c60930fc8c14854acf7f5439c9b150bb40aba0805095
  bytes  672390
  diff vs HEAD  +2737 / −3   (the three rewrites are prepend-only wiring:
                              the one-mode exclusivity sum, the `mode`
                              ternary, the `suffix` ternary)
frozen  2026-10-15T07:16:51Z  (frozen-artifact.txt)
python3 -m py_compile  clean
```

Both formal runs executed **byte-identical** code (the hash is re-checked in
`host-window.log` at every snapshot).

## Formal runs (the ≥2 end-to-end requirement)

| run | window (UTC) | receipt | sha256 | exit | failures |
| --- | --- | --- | --- | --- | --- |
| B | 07:22:19Z start | `corpus/live/runs/20261015T072219089606Z-capture-r79/measurements.json` | `658773646ec8381b…` | 0 | `{}` |
| C | 07:27:46Z start | `corpus/live/runs/20261015T072746218296Z-capture-r79/measurements.json` | `f4572530cbf0c708…` | 0 | `{}` |

Byte-equal copies live beside this file as
`receipt-runB-20261015T072219089606Z-capture-r79.json` and
`receipt-runC-20261015T072746218296Z-capture-r79.json` (sha256 in
`receipt-shas.txt`). Both receipts: 25 measurements, 8/8 r79 entries, **66
r79 legs**, no `blocked`/`coverage_blocked` entry, no surviving probe node
(`own_nodes_after: []`), every probe sink confirmed gone. Probe stderr was
0 bytes on both runs. Driver: `formal-runs.sh`; host snapshots before/after
each run in `host-window.log`.

Run-B/run-C verdict-field replication: `receipt-BC-diff.txt` (68/70 fields
identical after normalizing pid-stamped names; the two remaining diffs are a
0.1 amplitude rounding on the filter-chain DSP witness and a run-local client
id).

## This seat's delta over the inherited (unverified) r79 arm

`reports/round-79/r79-author.md` §1 lists them in full. In one line each:

1. `_loopback_r79_wait_monitor` — the monitor-readiness gate had to stop
   using `_playback_r78_wait_source(<sink>.monitor)`, which can never
   succeed on this host (monitor ports are owned by the SINK node).
2. `_loopback_r79_write_silence` + the pw-cat fallback leg's silent feed
   (no tag tone on the shared default sink).
3. `_loopback_r79_watch_sample` — extracted so a client can stay alive
   across sub-legs; the record entry now spawns its loopback directly
   (the inherited version ran it through the blocking runner, so every
   record leg resolved a dead target).
4. `_loopback_r79_default_source_probe` + `_loopback_r79_unnegotiated` +
   the `capture_default_source_unnegotiated` / foreign-tone named classes.
5. `_loopback_r79_two_tone` band recalibration + the matrix entry's
   cross-leg half-gain ratio.
6. `@SRC@` substitution in the capture lattice's expected producers.
7. pw-cat `latency_param_verdict` (named set, not a hard failure).
8. Filter-chain node matching by the fragment's short tag + `stderr_scan`.
9. Cosmetic: the always-true string operand in the f7 verdict.

## Exploratory diagnostics (bounded, read-only w.r.t. the repo)

| artifact | what it answers |
| --- | --- |
| `exp_default_source.py`, `exp-default-source-r79.json` | is the missing `default.audio.source` key the reason the `-C` fallback does not link? **No** — writing it changes nothing, WirePlumber drops the key again mid-leg. |
| `exp_capture_ports.py`, `exp-capture-ports-r79.json` | `pw-record --target 0` publishes ports; `pw-record --target <garbage>` dies `no target node available`; holding the default source RUNNING changes nothing. |
| `exp_record_targets.py`, `exp-record-targets-r79.json` | the scout's D2b/D2c/D17 arms DO resolve against a **live** loopback (`output.<lb>`, `input.<lb>` monitor, manual monitor pins rc=0). |

Host-state snapshots: `pre-state-run1.txt`, `pre-state-runA.txt`,
`post-state-run4.txt`, `host-window.log`, `toolchain.txt`.

Derived views used in the report: `measured-cells-runB.txt` (every measured
cell of the primary receipt), `receipt-BC-diff.txt`, `frozen-artifact.txt`.

## Contamination accounting (this seat)

* **Zero tag tone on the shared default sink from this arm.** The one leg
  whose destination is the shared default sink (pw-cat `d12`) is fed
  digital silence; every tone-fed loopback leg is refused at spawn unless
  its effective playback target is probe-owned (`_loopback_r79_guard_playback`).
* The arm only ever **reads** the shared default sink (monitor taps, and the
  `-C` fallback legs that capture its monitor).
* Named, measured foreign event (run A, 07:16Z): a concurrent lane's
  tag-shaped tone (peaks 11997/8997 — above this arm's 8192 ceiling) was on
  the shared default sink and was forwarded into a probe sink by the very
  fallback leg `b09` measures. Recorded as `foreign_tone_on_shared_monitor`
  with the peaks; it did **not** recur in runs B/C.
* Diagnostics mutated `default.audio.source` once (write, then delete) and
  held the default source open ~10 s for measurement; both restored/verified
  (`exp-default-source-r79.json` `restored_metadata.raw: null`, matching the
  pre-run state).
