# r84 author — pw-dump/pw-cli introspection + monitor-tap lattice (`--probe-alsapw-r84`)

Seat: `ufo-executor` (probeParent). Authoring pass over `corpus/fixtures/measure_audio.py`.
Insertion-only: +2796 lines, 3 modified wiring lines (add_argument append, mutex-sum
append, mode/suffix ternary prepends — identical convention to r82/r83). No prior family
touched; all `r84a_*` namespaced; nothing committed.

## Host / toolchain (as measured at run time)

- host `plazir27`, kernel Linux 7.2.3-arch1-3, loadavg >100 throughout (heavily contended
  shared host — every arm carries tag/link evidence rather than timing assumptions)
- PipeWire 1.6.8, WirePlumber 0.5.17, pactl/libpulse 17.0-98-gb096 (protocol 35),
  alsa-utils 1.2.16, python 3.14.7, numpy 2.5.3
- `TMPDIR=/home/vgpnk/Projects/shokunin/tmp` for all runs (`/tmp` quota exhausted by
  sibling trees — known environmental constraint)

## Entries (6) and legs (147 total)

| entry | legs | content |
|---|---|---|
| `alsapw_dev_lattice_r84_probe` | 38 | `-D` resolution lattice + verbatim refusal taxonomy + `-D ''`/`Unknown PCM -d` argv arms + adaptive direct-hw capture arms (free vs held-ebusy, `/proc/asound` RUNNING witness via own pw-record pin) + `-D null` nonzero-burst census + speaker-test headless legs (`null` c2/c0, `-t bogus`, `-m bogusmap`, `hw:0,0 -c1`) |
| `alsapw_pw_args_r84_probe` | 22 | `pipewire:` device-string args — `NODE=` pin ×2 + silent-fallback misses (incl. `<ns>.monitor` playback), `ROLE=`, `PERIOD_BYTES=4096→node.latency 1024/48000`, `RATE=44100` warn, `CHANNELS` 2/6/1mono, `SERVER=` bogus → `Host is down`; env `PIPEWIRE_NODE`, `PIPEWIRE_PROPS={...}`; speaker-test `NODE=` pin + `-c6` pacing; **single** capture-refusal class (`alsa_pw_capture_refusal`) ×4 + `NODE=<source>` revival ×2 |
| `alsapw_pulseprop_r84_probe` | 14 | `PULSE_PROP_*` env surface — `media.role` Communication→phone canonicalization ×2, Music/notarole raw, `zzz.invented=42` int-on-node vs string-in-proplist ×3 (paplay+parec), client-keys-win (`application.name`, `media.name`), `icon_name`→`icon-name` re-key, `application.process.binary`, env `module-stream-restore.id` landing but server key winning, bare `PULSE_PROP=` |
| `alsapw_pactl_write_r84_probe` | 24 | cubic volume pins on the monitor tap — 50%→**x0.125** ×2 sink + ×2 source, 150%→**x3.375**, index-addressed 25%→**x0.015625**; 0%/100% and mute cycles; suspend classes (linked hint vs idle suspend/unsuspend-stays/wake-by-play); refusal taxonomy ×10; write semantics `50.5%`→33095, raw `1.5`→75020, `-10%` relative |
| `alsapw_monstream_r84_probe` | 16 | `parec --monitor-stream` pin lattice — A-only sig on `-d ns` ×2 / absent `-d` / bogus `-d` / foreign `-d` (all ignored); `sink_monitor` A+B mix control; index refusals `0`/`999999`; source-output empty-accept (rc0, 44B); `move-sink-input` follow to `ns2`; kill-stall (parec alive, no EOS, growth recorded not armed); mid-run si-volume **x0.125** ×2 + si-mute visibility; no-write control; stream-restore sticky leg (30%→respawn 30%/tap 221→repair→verify 100%) |
| `alsapw_negctl_r84_probe` | 33 | classifier unit table (22 named classes + 6 must-classify-nothing inputs incl. crash words/empty/noise/rate-warning) + live no-error controls (`aplay -D null`, `pactl info`, `pw-dump`, free-hw arecord) + live `SIGKILL`-vs-refusal discriminator |

## Boundary corrections encoded (folded, not re-litigated)

- **Single capture-refusal class**: bare `-D pipewire` / `-D default` capture and
  `NODE=` misses on capture all produce ONE `Unable to install hw params:` stderr
  ending `TICK_TIME: [0 0]` — class `alsa_pw_capture_refusal` matches either marker;
  the unit table proves both slices map to the one class.
- **Monitor tap is post-gain**: `set-sink-input-volume <ia> 50%` mid-run moves the
  pinned tap by exactly `x0.125` (8192→1024, measured ratio 0.125 in both reps).
- **`-D ''` argv-eating**: real empty argv element → `Unknown PCM ` (empty name) in
  both tools; `-D -d 1` (element absent) → `Unknown PCM -d` — parser artifact,
  recorded verbatim, both pinned.
- **`-d` ignored under `--monitor-stream`**: bogus/foreign/absent `-d` all pin the
  same stream; movement follows `move-sink-input` only.
- **Restore-key writes are verify-gated**: private role `r84arole<pid>` (never the
  shared `music` key the boundary contaminated); reset+verify at entry head and
  per-leg repairs.

## Author-discovered refinements (consistent with, narrower than, boundary claims)

1. **Stream-restore persistence is name-scoped on this host**: a role-keyed 30% write
   reaches a respawn only when `node.name`/`application.name` match (same-tag→30%,
   different-tag→100% measured). The sticky leg therefore respawns under the same tag;
   boundary evidence is unaffected (they always reused `r84b_ta`).
2. **Reads must wait for routing**: the pre-route leaf shows `sink=0xFFFFFFFF` and an
   all-zero volume block (reads as bogus `0%`) and swallows si-volume writes without
   registering them into the restore key — `_alsapw_r84_wait_attached` gates all
   percent reads/writes.
3. **Donor source-output must be a parec**: `pw-record --target <sink>` and
   `--target <ns>.monitor` both refuse `no target node available`; `parec -d
   <ns>.monitor` registers as a source-output attributed by `application.process.id`.
   Also: parec accepts only `--file-format=wav` (= form; split form → "Too many
   arguments").
4. **Sink/source volume is persistent object state**: every tap leg pre-resets
   sink+source gain/mute before stream spawn, else the base window inherits the prior
   leg's write (observed cascade: 25% leftover → base 128).

## Green receipts (identical final bytes, two runs)

- `corpus/live/r84-author/runs/run1/measurements.json`
  (canon `corpus/live/runs/20261016T003253840363Z-alsapw-r84/measurements.json`)
- `corpus/live/r84-author/runs/run2/measurements.json`
  (canon `corpus/live/runs/20261016T003756373122Z-alsapw-r84/measurements.json`)

Both: `failures: {}` across all six entries, `coverage_blocked: null`, sinks_gone all
true, zero r84-owned residue.

Measured headline values (run2): `vol_50` 8192→1024 (x0.125), `vol_150` 8192→27648
(x3.375), `vol_25_idx` 8192→128 (x0.0156), `src_vol50` 8192→1024 (x0.125 via monitor
source), `monA_sivol` 8192→1024 (x0.125 pinned-tap post-gain), `mute`/`vol0` →0→8192,
`susp_live` unchanged 8192, `sticky` respawn 30%/tap **221** (=8192·0.3³)/repair 100%,
`mon_soidx` parec rc0 + 44B header-only, `mon_bad0`/`mon_deadidx` rc1 `Stream error:
No such entity` + 44B.

## Cleanup witnesses

- all `r84a_ns_<pid>`/`r84a_ns2_<pid>` null sinks unloaded name-verified every entry
  (sinks_gone all true in both runs); no `r84a_*`-tagged node survives (`own_nodes_after`
  empty in receipts; post-run `pw-dump` shows only the foreign node below)
- zero r84 sink-inputs/source-outputs; zero family processes; `TMPDIR` r84a-* dirs
  removed; family lock file removed after runs
- private restore key `r84arole<pid>` repaired to 100%/unmuted and verified
- **foreign state disclosed, untouched**: sink `r84a_probe_548706` (node 77, SUSPENDED)
  is NOT this family's (`r84a_ns_*`/`r84a_ns2_*`/per-leg tags only — never
  `r84a_probe_*`); left running as found. Ambiguous `~/tmp/r84n.wav` (mtime 20:28,
  predates this session) left in place — not attributable to this author run.

## Blockers

- `/tmp` quota exhausted by sibling trees → all runs under
  `TMPDIR=/home/vgpnk/Projects/shokunin/tmp`; documented, worked around.
- Foreign `r84a_probe_548706` sink occupied index space but never intersected the
  lattice (no cross-credit: family taps read own-sink monitors only, stream leaves
  matched by tag/pid).
- `ebusy`/`ctl_arecord_free` arms are adaptive by design (free-vs-held decided by the
  `/proc` RUNNING witness); both arms measured green on this host's state.

## Report

`reports/round-84/r84-author.md` (this file). Receipts under
`corpus/live/r84-author/runs/run{1,2}/measurements.json`.
