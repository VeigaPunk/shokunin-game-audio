# r99 verifier — independent frozen-source run of the native RTP family

Seat: **VERIFIER** (leaf, wave B). Round **N=99**, role `verifier`, FLAG
`rtp-r99`. Source pin **`bb177513a615a32d3bc150ecbdcf78302e110d8c`**
("r99 safety: require explicit opt-in before physical LAN control",
2026-10-16 09:29:41 −0300). Advisory only: this report is not an admission,
not a gate decision and not a canonical judge verdict. No source edits, no
routing edits, no subagents, no retries.

## 1. Identity, scope, commands actually executed

- Repo `/home/vgpnk/Projects/shokunin/audio-shokunin`; pin verified with
  `git cat-file -e <pin>^{commit}` before any write.
- Scratch `/home/vgpnk/Projects/shokunin/audio-waveb-resume/r99-verifier/`
  (parent checked first; directory did not previously exist — unique).
- Export (rc 0, 6.0 MB, 30 files): `git archive <pin> corpus/fixtures
  corpus/artifacts | tar -x -C "$SCRATCH/tree"`. Minimal tracked export;
  no working-tree copy, no full archive, no ignored author evidence.
- Single family run, executed exactly once, in the exported tree:

  ```
  env -u RTP_R99_ALLOW_LAN_CONTROL UFO_SEAT=r99-verifier-resume \
    PYTHONDONTWRITEBYTECODE=1 timeout 1500 \
    python3 corpus/fixtures/measure_audio.py --probe-rtp-r99
  ```

  Literal command, stdout, stderr and rc are saved at
  `audio-waveb-resume/r99-verifier/{command.txt,stdout.txt,stderr.txt,rc.txt}`.
  Result: **rc 0**, stderr empty, stdout exactly
  `{"receipt": ".../tree/corpus/live/runs/20261016T124136092601Z-rtp-r99/measurements.json", "failures": {}}`.
- Read-only inspection around the run: `git show`/`sha256sum` provenance
  checks, `.pyc` header read, `ps`/`ls`/`ss` exit census, receipt parsing.
  Nothing else was executed; no measurement was re-derived, re-tuned or
  repeated.
- **LSP gap (recorded):** no LSP device is available to this seat in this
  environment. All source statements below are literal source inspection of
  the pinned bytes; no grep output is offered as semantic proof.

## 2. Findings, by severity

### F1 (medium — fail-open exception path) The fixed-path family lock silently does not exist in the verifier's frozen export

- Where: `corpus/fixtures/measure_audio.py:50903-50919` (lock helper),
  caller `:55250` (`_rtp_r99_family_lock = _rtp_r99_family_lock()`).
- Failure path: the lock path is `ROOT/live/measure_audio-rtp-r99.lock`
  (`:50908`), `ROOT = Path(__file__).resolve().parents[1]` (`:27`). The
  minimal export contains only `corpus/fixtures` + `corpus/artifacts`, so
  `corpus/live/` does not exist (observed: `ls` → "No such file or
  directory"). `os.open(..., O_RDWR|O_CREAT)` at `:50910` then fails with
  ENOENT (the parent directory is missing), the `except OSError: return
  None` at `:50911-50912` swallows it, and the caller discards the `None`:
  the whole run proceeds with **no same-family exclusion**.
- Evidence: observed — `corpus/live` absent in the export before and during
  the run; the `corpus/live/runs/` directory appeared only at receipt time
  (`out.mkdir(parents=True)`, `:55966`). In the author's environment
  `corpus/live` existed (untracked), so the author's green passes were
  locked; the verifier's frozen export never is.
- Consequence: two concurrent `--probe-rtp-r99` runs in exported trees would
  not exclude each other. Port windows are pid-derived
  (`46500 + pid % 400`, `:50793`), so a `pid % 400` collision could
  interleave two seats' legs on the same ports; node names are pid-unique
  (`r99a_<pid>`), so evidence cross-talk is unlikely but the exclusion
  contract (the r84 F1 fixed-lane-path consensus, cited at `:50904-50907`)
  is not honored in this context.
- Smallest correction: `path.parent.mkdir(parents=True, exist_ok=True)`
  before `os.open`, or treat an untakeable lock as a named coverage block
  instead of returning `None`. Either keeps the fixed-path contract and
  removes the silent fail-open.
- Classification: **observed** (directory absence + source path), not
  inferred. Severity tempered by the fact that no second rtp-r99 lane was
  live during this run.

### F2 (info — verified by execution) The physical-LAN positive control is default-off at the pin and did not run

- Where: guard `corpus/fixtures/measure_audio.py:52608`
  (`os.environ.get("RTP_R99_ALLOW_LAN_CONTROL") == "1"`); blocked branch
  `:52637-52643`.
- Observed in this run's receipt (`legs.e_lan_control`): `measured: false`,
  `blocked: "e_lan_control: physical-LAN transmission disabled; requires
  explicit operator approval and RTP_R99_ALLOW_LAN_CONTROL=1"`, iface
  `enp7s0`, and exactly one `coverage_blocked` entry for it. The recipe's
  `env -u` was honored; the opt-in was never set, by me or by the source.
- The pin commit also added
  `corpus/fixtures/test_rtp_r99_lan_control.py` (49 lines): an AST-level
  regression asserting the guard is the single `RTP_R99_ALLOW_LAN_CONTROL`
  test in `rtp_e2e_r99_entry`, that None/""/0/"true" all yield
  `measured: False` + the approval message + exactly one coverage_blocked
  entry, and that "1" reaches `_rtp_r99_cli_open` (barrier) without sending
  anything. Read and confirmed line-by-line; **not executed** (outside the
  fixed recipe) — named in §4 as an unrun check.

### F3 (info — provenance, observed via hash chain) The integration r99 receipt ran on pre-repair bytes; the pin is the first guarded source

- `git show 193acbed:corpus/fixtures/measure_audio.py | sha256sum` →
  `5c8f7e9dc587346b3ec2e1f87cefd432ee873e559289b1cf5fd1c06bfa09e9ab` —
  byte-identical to the "r100 final" source sha recorded in
  `reports/round-100/r93-r99-r100-integration.md`.
- The guard commit `bb177513` (12:29:41Z) postdates the integration r99 run
  stamp `20261016T121018453359Z` (12:10:18Z). Therefore the integration's
  r99 receipt necessarily executed the physical-LAN positive control
  (disclosed egress; the author's greens at 10:35/10:40Z did too), and no
  pre-pin receipt can be cited as evidence of default-off behavior. The
  diff `193acbed..bb177513` touches exactly the e_lan_control guard + the
  new test file (verified with `git diff`), so every other leg's behavior
  is byte-identical between the integration source and the pin.
- Pinned `measure_audio.py` sha256
  `801e153b84368bba4a77e85c129376612c797694c435e9104cdad6e62169be2f`;
  pinned `r99rtp.py` sha256
  `36b6b6f8ae332d768e6129fc1fbcf56e634c2e636ceaaa043f97ad11cccfa6a1` — the
  fixture matches the author's claimed implementation sha exactly
  (`r99-author.md` §Evidence). The `measure_audio.py` delta vs the author's
  claimed `1bb2f98b…` is exactly the safety repair.

### F4 (info — honest per-pass variance) This pass's clean ts lattice was `[48]` only

- `legs.s_props.ts_lattice` in this run: `clean_deltas: [48]`,
  `wrap_deltas: []`, `scout_subset_present: false` — the scout's 6-value set
  `{48,80,96,112,128,144}` was not fully present in this 3 s leg. The armed
  law (every clean step a multiple of 16 and ≥ 48, `:51800-51815`) holds and
  fired no failure; the subset field is recorded, never armed (`:51804`).
  Same variance class the author disclosed for `a_quantum`
  (`[48]` vs `[48, 64]`). Observed, not inferred.

### F5 (info — declared block reproduced) `e_native` remains explicitly unmeasured, exactly as declared

- This run: sink side exact — tap read 8001 × 204 B, wire peak
  `0.499969482` both channels; source side silent — recorded peak `0.0`,
  `rtp.ssrc "0"`, 1 scrubbed `sync to timestamp` line; tap peer
  `192.168.0.253:51674` (the host's LAN address stamped on a lo-delivered
  packet — the author's disclosed receiver-side quirk). The leg recorded a
  named coverage block (`measure_audio.py:52396-52405`) and did not claim
  C6. Matches the author's declaration and the integration note; C6 is
  unmeasured, not falsified.

### F6 (info — export integrity) The tracked `.pyc` is stale and is ignored; no stale-bytecode hazard

- `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc` is
  timestamp-based (flags 0) with recorded source size 533517 vs actual
  2766373 bytes → invalid against the exported source; the interpreter
  recompiles in memory and `PYTHONDONTWRITEBYTECODE=1` blocks new writes.
  Verified by header read. (The tracked `.pyc` files are exported because
  they are tracked; they are inert here.)

## 3. What the run's receipt supports (measured, this pin, this pass)

Receipt:
`audio-waveb-resume/r99-verifier/tree/corpus/live/runs/20261016T124136092601Z-rtp-r99/measurements.json`.

- Shape: **six entries; 37 leg-dictionary keys = 4 `tone` setup records +
  33 non-tone cells** — exactly the declared r99 shape (census 3; sink
  7+tone; source 6+tone; refusal 8; e2e 5+tone; axis 4+tone).
- `failures: []` in all six entries; `coverage_blocked` exactly 2, both in
  `rtp_e2e_r99_probe` (`e_native`, `e_lan_control`) — nothing else blocked,
  nothing silently green.
- Reproduced laws (all observed this pass): census 34 modules / 10
  network-capable / 4 absent packages / man pages documenting min-ptime 2,
  max-ptime 20 and `rtp.ptime` under MODULE OPTIONS; `s_props` peak exact
  `0.499969482` both channels, sizes `[204]`, seq `[1]`; `s_default`
  6.458333 ms / 310 / `[1252]`; `s_lattice_50_100` `[9612]` with ts delta
  `[2400]` (no 2048 cap); `s_two` two ephemeral source ports, one
  destination; `r_shape` init fakes (`receiving true`, `ssrc 0`, per-load
  offset, no sync); `r_mcast`/`r_unicast_same` tone present (recorded-path
  peak 1.0 — the overshoot is recorded, never armed);
  `r_unicast_foreign` peak 0.0 with no sync line; `r_ts_offset` plays;
  `r_s24be` `[300]`/L24; refusals rc 234 ×4 (`x_destip`, `x_f32`,
  `x_media`, `x_srcport0`) and rc −8 SIGFPE (`x_ptime_pair`), `x_ifname`
  suspended, module-args dropped (`1.000000`/`48`), props-only honoured
  (`20`/`960`); `e_sap` zero own nodes + join lines on the named group;
  `e_relink` 9000 packets, nonzero fraction 0.8454; `e_lan` confinement
  **armed_below_band** (idle1 7687 / arm 7412 / idle2 8990 tx packets on
  `enp7s0` while 19999 packets were emitted on lo); `a_quantum` clean
  deltas `[48]`@256 and `[48, 64]`@1024 (mechanism armed, set equality not
  asserted); `a_rate` `[188]`/0.997732/44; `a_order` `[204]`/1.000000;
  `a_target_pos` 16000 packets, one size.
- Teardown witnesses: all five private-core entries report
  `socket_gone: true`, `own_daemon_pids_alive: []`,
  `shared_r99a_nodes_after: []`, `shared_stream_properties_own_rows: []`;
  the census entry owns no private core (fields absent), matching the
  integration note's "five private-core entries". Shared settings lattice
  equal at entry start and end. Post-run exit census by this seat: no
  `r99a` processes or sockets anywhere, 0 own rows in the operator's
  store, shared daemons 3549292/3549293/3549294 intact, no
  `set-default-*` ever issued.

## 4. Residual risks and explicit checks not run

1. `test_rtp_r99_lan_control.py` was **not executed** (outside the fixed
   recipe). It is the pin's own no-network regression for F2 and is cheap
   for the lead to run.
2. The `e_lan_control` opt-in branch (`"1"`) was never exercised live — by
   design; setting it is forbidden to this seat.
3. This pass's `e_lan` confinement verdict (`armed_below_band`) has **no
   same-pass positive control**: the counter method's non-vacuousness is
   inherited from the author's disclosed LAN-control runs (8626/6975
   packets), which ran on pre-guard bytes. Under the guard a same-pass
   control requires operator opt-in — an accepted trade, but the
   calibration of this pass's confinement arm rests on that inheritance.
4. The run shared the host with three concurrent sibling verifier families
   (r93/r98/r100 lanes observed in `ps`, each in its own scratch tree with
   private cores). Wall-time-sensitive quantities (packet rates, fill
   fractions) could differ from a quiet run; the armed laws are the shape
   class, which is what fired.
5. `e_native`'s receiver-side blocker (LAN address on lo) remains
   unexplained — unchanged from the author's disclosure; this pass adds a
   fresh witness, not a mechanism.
6. No LSP was available to this seat; all source statements are literal
   pinned-byte inspection. The 1.5 GB full-history archive and untracked
   author evidence were not inspected (minimal export by design).

## 5. Artifacts and attribution

- Report: `reports/round-99/r99-verifier.md` (this file; untracked new
  file; no tracked repo file was touched by this seat — the pre-existing
  foreign `M LOG.md` working-tree modification was present and untouched).
- Scratch: `/home/vgpnk/Projects/shokunin/audio-waveb-resume/r99-verifier/`
  — `command.txt` (literal commands), `stdout.txt`, `stderr.txt`, `rc.txt`
  (`RC=0`), and `tree/` (the frozen export plus the run's receipt at
  `tree/corpus/live/runs/20261016T124136092601Z-rtp-r99/measurements.json`).
- The receipt is local scratch evidence produced by this seat's single run;
  it is not committed and not remotely available. The author's and
  integration's pre-existing receipts were read, not re-run and not
  modified.
- Attribution: verifier seat `r99-verifier-resume` (own pid 1428714,
  recorded in the receipt's contention snapshot). Advisory findings only;
  the lead inspects the receipt and raw outputs. Not judged, not admitted,
  not shipped.

*verifier leaf — one frozen-source run, recorded as it fell out; not judged.*
