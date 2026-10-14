# R73 simplifier — no tracked deletion is possible this round (r73 arm unlanded at measurement; write scope = report + scratch only); seven pre-landing weight rulings for `--probe-consumers-r73` measured on the live host: reuse the canonical-9 member authority / the one timeout + fifo-writer protocol / the fold's `blocked:` convention, do **not** add a second daemon-viability authority (pactl and pw-cat gates measured to disagree), do **not** couple mpv to the daemon (`--ao=pipewire` flips a verdict cell, `--ao=null` does not), do **not** reuse `_tail` verbatim (pw-cat paths and mpv timestamps survive it), and keep verdict granularity above raw rc; landed r72 base re-proved byte-stable across the mid-session reviewer-fold (9/9 entries, 3 reruns, identical receipt hash)

**Seat:** simplifier (delete-and-measure, not subjective trim). Lane: audio. Repo
`/home/vgpnk/Projects/shokunin/audio-shokunin`.
**State at measurement (2026-10-14 11:34–11:45 -03):** HEAD at start `50f55eb`; a late
r72 reviewer-fold `f5d7faf` ("lazy libsndfile load … + blocked-verdict arm") landed
mid-session at 11:38:20 and is the final state. The **r73 arm is not landed** in either
revision: `grep -c -iE "pw-?cat|pw-play|mpv|consumers-r73"` = `0` on
`corpus/fixtures/measure_audio.py` and `build_artifacts.py`; last probe flag is still
`--probe-sndfile-transport-r72` (`measure_audio.py:1130`); `git diff --stat` empty;
`git status --porcelain | grep -v '^??'` = 0 lines. The author seat's scratch
(`corpus/live/r73-author/scratch/`) appeared at 11:39 and was still mid-measurement at
the last polls — 11:42:52 and 11:46:57: HEAD `f5d7faf`, fixture grep still 0, author
scratch at 5 files (mpv pipe/redirected-fd legs, fifos; no fixture edit). My write scope
(`reports/round-73/r73-simplifier.md` + `corpus/live/r73-simplifier/`) excludes the
fixture. **Deletions made in the shared tree: none.** Candidates below are pre-landing
weight rulings with measured evidence; none was applied outside scratch.
**LSP device — unavailable on this host/task (recorded per seat card, empirically).**
No `pyright`/`pylsp`/`jedi-language-server`/`lsp` binaries; `pygls`/`jedi`/`lsprotocol`
not importable; `clangd` present but C-family only (surface is Python). The only MCP
server (`rea`) is Ghidra-bound: `binary_overview` → `target_unavailable: "No app is
open. … call open_binary with its local path"`; its `procedure_references` device serves
loaded native binaries, not this Python file. Every "no callers" statement below is
therefore **grep-literal fallback, explicitly not semantic proof**.
**Toolchain:** pw-cat / libpipewire **1.6.8** (pipewire pid 1905 + pipewire-pulse pid
2290 live, socket `/run/user/1000/pipewire-0`), mpv **v0.41.0** (libavformat 63.1.101),
libsndfile 1.2.2, Python 3.14.7, numpy 2.5.3, Linux x86_64.

## Deletion candidates (measured)

| # | Candidate (weight that would be *added* by the landing) | Measured effect | Ruling |
|---|---|---|---|
| C1 | A new `TRANSPORT_R73_MEMBERS` dict, or the frontier's member list copied verbatim (it includes a 10th member, `pair_lengate_gsrt_25.wav`, outside the canonical set) | 9/9 canonical paths + sha256 stable; frontier exercised 5/9 canonical + 1 non-canonical | **Do not add.** Reuse `TRANSPORT_R72_MEMBERS` (`:735` alias) / `TRANSPORT_R71_MEMBERS` (`:557`) |
| C2 | A new arm-timeout constant / a consumer-only fifo protocol (no-linger variant) | pw-cat runs rc=0 through the fixture's own `fifo_feed`+hold, writer exits cleanly (wall 1.00 s) | **Do not add.** Reuse `TRANSPORT_R71_ARM_TIMEOUT_S` (`:568`, 15 s), `fifo_feed` (`:294`), `fifo_writer_hold_s()` (`:285`) |
| C3 | A second daemon-viability authority (`pgrep pipewire`, `pactl info`) or a skip-gate that drops members when the daemon is down | `pactl` says "up" (rc=0) where pw-cat says "Host is down" (rc=1) under the same `PIPEWIRE_RUNTIME_DIR`; a pgrep gate passes on this host while the arm fails | **Do not add.** The pw-cat connect attempt is the only honest gate; record the blockage as the verdict (reuse the fold's `blocked:` shape, `:915-924`/`:837-841`) |
| C4 | Consumer flag drift: `--target 0` for pw-cat, `--ao=pipewire` for mpv | `--target 0` hangs (killed at 6.00 s, rc=137, zero output); `--ao=pipewire` flips the fifo-hcom cell rc=0→2 when the daemon is unreachable, `--ao=null` leaves it daemon-independent | **Do not add.** Keep the frontier's pinned shapes (default target; `--ao=null`) |
| C5 | Verbatim reuse of the landed `_tail` normalizer (`:647-653`) for the consumer legs | pw-cat file-arm stderr keeps the absolute path (`path-survives=True`); mpv log lines keep `[ 0.00x]` timestamps (`ts-survives=True`) → non-byte-stable receipts | **Extend, don't copy.** Strip the `[…]` prefix (stripped key lines measured identical across runs) + replace the known path with `<input>` |
| C6 | A verdict keyed on raw rc alone | mpv rc=2 covers two distinct classes (seek-EPERM vs no-format); pw-cat rc=1 covers daemon-down vs format rejects | **Record the normalized reason line**, not rc alone (stable under timestamp stripping) |
| C7 | Stale axis naming: `transport-*-r73` mode/suffix/keys, or extra per-arm top-level keys | The brief pins `--probe-consumers-r73`; the family convention is one entry per member per consumer (`decoder` field), as r71/r72 | **One flag, one branch per if-chain** (`mode :1819`, `suffix :1839`), key family `consumers_*_r73_probe`, no umbrella keys |

### C1 — member authority is already settled; the frontier list is not the canonical set

`members.tsv` (9 rows): all nine `TRANSPORT_R72_MEMBERS` paths exist with stable sha256
(five extsuffix members identical bytes `f073e70a…`; the names are the contract). The
frontier's exercised set (`fb-pipewire.md:6`) is **5 of the canonical 9**
(dec_act, dec_hcom, txw_piperefuse, extsuffix wav/txw) **plus `pair_lengate_gsrt_25.wav`,
which is not in the canonical transport set** — copying the frontier list would create a
second member authority and break the 9-member cross-decoder comparability that r67→r72
built. The 4 untested canonical members (posttable_nomatch, extsuffix bin/f32/snd) are
exactly the coverage this round adds; they have no frontier verdict to inherit, so the
landing must measure them (no pre-filled table). **Tradeoff:** none — the alias chain is
the established convention (`TRANSPORT_R72_MEMBERS = TRANSPORT_R71_MEMBERS`).

### C2 — one timeout, one writer protocol (and the existing one already survives pw-cat's traps)

- **Timeout.** Python `subprocess.run(timeout=…)` kills with **SIGKILL** on expiry
  (measured: a `trap '' TERM` child was killed anyway, 0 survivors —
  `python-timeout-signal-check2.txt`). Measured pw-cat trap: a reader blocked at fifo
  `open()` **ignores SIGTERM** — `timeout -k 2 4 pw-cat -p <no-writer-fifo>` ended only at
  **wall 6.00 s / rc 137** (TERM at 4 s had no effect; KILL at 6 s did). The landed
  convention therefore already covers the trap; a new constant or a shell-level
  `timeout -s KILL` wrapper inside the fixture would be a second authority. Reuse
  `TRANSPORT_R71_ARM_TIMEOUT_S` (`:568`). Re-ran the `--target 0` leg with an immediate
  survivor check: rc=137 and `none-mine` — no stray pw-cat from this seat.
- **Writer protocol.** pw-cat driven by the fixture's own `fifo_feed` + `fifo_writer_hold_s()`
  (hold 1.0 s): **rc=0, wall 1.00 s, writer thread exited** (`pwcat-fifo-feed-check.txt`).
  A consumer-only no-linger variant would fork the writer protocol for zero verdict change.
  **Tradeoff:** the 1.0 s hold costs ~9 s per 9-member run; it is env-overridable
  (`MEASURE_FIFO_WRITER_HOLD_S`) and the effective value is recorded, so the cost is honest.

### C3 — the daemon gate must be the attempt itself, and must not skip

Frontier (`fb-pipewire.md:8-22`) and re-measured here: with a live daemon (pgrep 1905/2290)
but an unreachable runtime dir, `PIPEWIRE_RUNTIME_DIR=emptyrt pw-cat -p <member>` →
**rc=1 instantly, `error: pw_context_connect() failed: Host is down`** — *before* any input
open. The same env against the pulse-protocol probe: `pactl info` → **rc=0** (still
connected; only `XDG_RUNTIME_DIR=emptyrt` makes pactl refuse). So a `pactl`/`pgrep` gate
disagrees with pw-cat's actual precondition and would record "up" on a down arm. And the
r73 brief explicitly asks to *record the exact blockage if down*, so a skip-gate is
backwards: run the arm, record the connect failure as its verdict. The fold already
established the vocabulary for host-viability verdicts — `"blocked: libsndfile unavailable
on host"` with a `failures` row (`:837-841`, `:915-924`) — reuse that shape, don't invent
`skipped`/`gated`/`unavailable` variants.
**Measured trap for the fifo arm when the daemon is down:** pw-cat never opens the fifo, so
the writer side blocks in `open()` forever — `pwcat-fifo-nodaemon.out` shows `pwcat-rc=1`
while the shell writer had to be killed externally (outer KILL at 8 s; no survivors). The
fixture's thread-based `fifo_feed` + bounded `writer.join(timeout=hold+5)` (`:627-629`)
keeps the *arm* bounded, but the writer thread stays blocked until process exit — worth one
comment in the landing, not a new mechanism.

### C4 — pinned consumer flags; two measured traps

- **pw-cat `--target 0`** (unlinked stream): killed at **6.00 s, rc=137, zero output** —
  an unlinked stream never drains (frontier saw rc=124 under SIGTERM). Playback requires an
  actual link; use the default target as the frontier did.
- **mpv `--ao=pipewire`**: same fifo-hcom member, same writer protocol —
  daemon reachable → **rc=0**; `PIPEWIRE_RUNTIME_DIR=emptyrt` (env-scoped, daemon untouched)
  → **rc=2** with `[e][ao/pipewire] Could not connect to context '(null)': Host is down` +
  `Failed to initialize audio driver 'pipewire'`. With `--ao=null` the file arm stays **rc=2**
  under the same unreachable env — i.e. `--ao=null` keeps the seekability fork orthogonal to
  the pw-cat viability axis; `--ao=pipewire` would duplicate that axis inside the mpv arm and
  silently conflate "no audio played" with "daemon down". Keep `--ao=null`.

### C5 — normalization: the landed `_tail` is insufficient for both consumers (measured)

`_tail` (`:647-653`) strips `` `…' `` tails and ` @ 0x…` ASLR tags. Applied verbatim to the
frontier artifacts (`normalizer-check.txt`):

- pw-cat file-arm reject line: `sndfile: failed to open audio file
  "/home/…/round-68/txw_piperefuse.wav": …` → `_tail` output **keeps the absolute path**
  (`path-survives=True`). The r71 caller's literal `.replace(probe_arg, "<input>")` would
  cover the file arm, but a copied-only `_tail` would not; the fifo arm prints the bare
  fifo name, so the file arm is the leaking one.
- mpv log lines: `[   0.006][v][lavf] Seek failed (Operation not permitted)` →
  `_tail` output **keeps the timestamp** (`ts-survives=True`).

Two-run measurement (`mpv-file-hcom-{1,2}.log`): raw logs differ (timestamps, `--log-file`
name); key lines differ by timestamp too; **timestamp-stripped key lines are byte-identical**
(`STRIPPED-KEY-LINES-IDENTICAL`). Recipe: strip `^\[[^]]*\]` (or store the message tail) and
normalize the input path — one normalizer reused by both consumer legs, not a third copy.

### C6 — verdict granularity (why the reason line is load-bearing)

mpv **rc=2** is returned for both the hcom file arm (`Seek failed (Operation not
permitted)` → `finished playback, no audio or video data played`) and the txw/no-match arms
(`Failed to recognize file format`) — frontier `mpv-file-txw_piperefuse.wav.log` /
`mpv-file-extsuffix_nomatch.wav.log` + my re-runs. A receipt keyed on rc alone collapses the
inverted-seekability fork's *mechanism*; the normalized reason line is the stable,
byte-safe discriminator (C5). Same for pw-cat: rc=1 covers "Host is down" (C3) and the three
sndfile reject tiers — keep the sndfile reason text.

### C7 — names and family shape

Mode/suffix chains are single-branch if-else ladders (`mode :1819`, `suffix :1839`); the
landing adds exactly one flag (`--probe-consumers-r73`), one mode branch, one suffix branch,
and per-member entries in the r71/r72 family (`decoder` field: `"pw-cat"` / `"mpv"`), i.e.
two entries per member — same shape the family already duplicates `path`/`pair_member` in.
No umbrella `consumers:` key that no verdict reads, no `transport-*` naming for a consumer
axis (stale name), no separate `--probe-pwcat`/`--probe-mpv` flags.

## Ruled-out deletions (stop condition reached)

- **R1 — `sndfile_info_cli` (landed r72, `:933-952`):** not deletable. It is cited by the
  landed round-72 record — `reports/round-72/r72-verifier.md:48/76/81` analyzes
  `frames_field` 512 and `.reason`; `reports/round-72/r72-baseline.md:99` describes the leg —
  and the receipt key participates in the baseline's replay comparison
  (`r72-baseline/prior-rows-stable.txt`: shared keys differing `[]`, one-sided keys listed).
  Deleting it would change the r72 receipt shape and break the replay byte-stability the
  verifier/baseline seats enforce. Keep as landed; **do not copy the advisory leg into the
  r73 consumer entries** (nothing keys on it, C1-style).
- **R2 — the reviewer-fold's blocked-verdict arm (`:837-841`, `:915-924`):** deleting it
  would re-break the host-portability axis the fold fixed (module-scope `CDLL` used to kill
  every mode at import on libsndfile-less hosts). It is a measured-needed gate, not dead
  weight.
- **R3 — group-by-signature loops (3 copies today, `:701/:706`, `:954`, `:989`; a 4th copy
  would follow):** extracting a shared helper touches landed r67/r71/r72 lines and changes
  their receipts' construction path; insertion-only is the round contract (same ruling as
  r69-#12/#13 and r72-R3). The landing should keep the loop shape identical for
  comparability.
- **R4 — frontier provenance.** `ports/frontier/fb-pipewire.md` and
  `corpus/live/frontier-pipewire/*` (logs, fifos, `tone4s.wav`) are this round's declared
  READ-FIRST evidence; protected ("never delete provenance explicitly marked historical").
  The frontier dir holds **no harness script** (ad-hoc shell legs), so unlike r72 there are
  no dead symbols to inherit — the carry-over hazards are the *recipes* (C3–C5).

## Preserved contract (retained behavior proven with the narrow existing check)

- **Landed r72 arm == committed receipt, byte-stable across the fold.** Rerun of the tracked
  `sndfile_transport_entry` on the canonical 9 (driver `compare_r72_entries.py`, read-only;
  fifos in `/tmp`) deep-compared to
  `corpus/live/runs/20261014T143409279922Z-sndfile-transport-r72/measurements.json`:
  **9/9 MATCH, 0 mismatches, 3 runs** (two at 11:37:49/11:38:00 on the fold's working
  content, one post-commit at 11:41) — all three outputs byte-identical
  (`b83fee736398…`). This is the base the r73 insertion extends.
- **Dead-symbol scan (grep-literal, post-fold):** 0/23 defs, 0/116 argparse flags, 0/25
  UPPER_CASE constants unused; every flag reaches the dispatch chain. No deletable symbol
  exists in the landed fixture.
- **Member identity.** `members.tsv`: 9 paths + sha256, 9/9 present; extsuffix five share
  `f073e70ad6e9…`.
- **Tree identity.** Final HEAD `f5d7faf`; `corpus/fixtures/measure_audio.py` sha256
  `b765ee7627b4…` unchanged across the session. At the final check the only modified
  tracked file is `corpus/live/r72-baseline/measure-env/corpus/fixtures/measure_audio.py`
  (the r72 baseline's measure-env replica, mtime 11:40:29 — a concurrent seat's file, not
  mine). Every byte written by this seat is under `corpus/live/r73-simplifier/` +
  `reports/round-73/r73-simplifier.md`; sibling `r73-*` scratch dirs belong to other seats.
  Two other seats' pw-cat processes were observed blocked
  (`r73-reviewer/fifo-pace`, `r73-boundary/logs/fifos/posttable_nomatch.wav`, later
  `r73-boundary/logs/fifos/c1.fifo`) — not mine, left untouched (same convention as the
  frontier note); this seat's legs left 0 strays (post-KILL survivor checks).
- **Environment caveat.** The r72 reviewer-fold landed mid-session; my state files record
  both revisions (`head-at-start.txt` 50f55eb, `head-after-fold.txt` f5d7faf) and the
  retained-behavior proof is re-anchored to the final revision.

## Stop condition

The next deletion that would "remove weight" — dropping the r72 CLI leg (R1), the fold's
blocked arm (R2), or refactoring the grouping loops (R3) — harms an axis (replay
byte-stability / host portability / insertion-only contract). Deletions recommended for the
tracked tree: **none possible** (r73 arm unlanded; C1–C7 are items to *not add*). Stop.

## Evidence index

Scratch `corpus/live/r73-simplifier/` (sha256 of each):

- state: `head-at-start.txt` `267de642…`, `head-after-fold.txt` `ec568569…`,
  `daemon-state.txt` `b3e28df0…`, `landing-poll.txt` (11:42:52 unlanded),
  `landing-poll2.txt` (11:46:57 unlanded)
- retained behavior: `compare_r72_entries.py` `36924fbf…`, `r72-rerun-1.txt` /
  `r72-rerun-2.txt` / `r72-rerun-3-postfold.txt` all `b83fee736398…`
- members: `members.tsv` `6f6d4ba1…`
- dead scan: `scan_dead.py` `e9fe87a6…`, `dead-symbol-scan.txt` `59609b48…`,
  `dead-symbol-scan-postfold.txt` `20b6996a…`
- normalization: `normalizer_check.py` `3002b24e…`, `normalizer-check.txt` `f36f473f…`
- timeout semantics: `python-timeout-signal-check2.txt` (SIGKILL confirmed, 0 survivors)
- pw-cat legs: `pwcat-nodaemon-gate.err` `0162cae4…` (+ `.out` empty),
  `pwcat-file-play.{out,err}` empty, `pwcat-fifo-nowriter.{out,err}` empty,
  `pwcat-target0.{out,err}` empty, `pwcat-fifo-attach.{out,err}` empty,
  `pwcat-fifo-nodaemon.out` `1e7ad79d…` / `.err` `0162cae4…`,
  `pwcat_fifo_feed_check.py` `32725c20…`, `pwcat-fifo-feed-check.txt` `d5a44abc…`
- pactl: `pactl-pwrt-down.txt` `49c1e865…`, `pactl-xdgrt-down.txt` `fec91b6b…`
- mpv legs: `mpv-file-hcom-{1,2}.log`, `mpv-fifo-hcom-{1,2}.log`,
  `mpv-file-hcom-ao-null-down.log`, `mpv-fifo-hcom-ao-pw-{up,down}.log`
- reference: `ports/frontier/fb-pipewire.md`; `corpus/live/frontier-pipewire/*`;
  `corpus/live/runs/20261014T143409279922Z-sndfile-transport-r72/measurements.json`;
  `corpus/live/r72-baseline/prior-rows-stable.txt`; `reports/round-72/r72-verifier.md`

## Exact commands / exits (key legs)

```sh
cd ~/Projects/shokunin/audio-shokunin
# state
git rev-parse HEAD            # 50f55eb… then f5d7faf… (fold mid-session); diff --stat empty
grep -c -iE "pw-?cat|pw-play|mpv|consumers" corpus/fixtures/measure_audio.py   # 0
# C3: daemon gate
pgrep -a pipewire             # 1905 /usr/bin/pipewire; 2290 pipewire-pulse
PIPEWIRE_RUNTIME_DIR=$PWD/emptyrt timeout -s KILL 8 pw-cat -p round-66/pair_dec_hcom.wav
                              # rc=1, wall 0.00; "error: pw_context_connect() failed: Host is down"
PIPEWIRE_RUNTIME_DIR=$PWD/emptyrt pactl info        # rc=0 (pactl disagrees with pw-cat)
XDG_RUNTIME_DIR=$PWD/emptyrt pactl info             # rc=1 Connection refused
# C4: traps
timeout -s KILL 15 pw-cat -p round-66/pair_dec_hcom.wav          # rc=0 wall 0.09 (daemon up)
timeout -s KILL 6  pw-cat -p --target 0 round-66/pair_dec_hcom.wav  # rc=137 wall 6.00 (hang)
timeout -k 2 4 pw-cat -p <no-writer-fifo>                       # rc=137 wall 6.00 (TERM ignored)
timeout -s KILL 15 mpv --no-config --vo=null --ao=null --audio-display=no --really-quiet \
  --log-file=mpv-file-hcom-1.log round-66/pair_dec_hcom.wav      # rc=2; Seek failed (EPERM)
mkfifo f; (cat round-66/pair_dec_hcom.wav > f &); timeout -s KILL 15 mpv … f   # rc=0; not seekable
PIPEWIRE_RUNTIME_DIR=$PWD/emptyrt timeout -s KILL 15 mpv … --ao=pipewire f     # rc=2 (coupled)
# C2/C5/C6 + preserved contract
python3 corpus/live/r73-simplifier/pwcat_fifo_feed_check.py     # rc=0 wall 1.00 writer_alive=False
python3 corpus/live/r73-simplifier/normalizer_check.py          # path-survives=True / ts=True
python3 corpus/live/r73-simplifier/compare_r72_entries.py       # 9/9 MATCH (x3, hash-identical)
python3 corpus/live/r73-simplifier/scan_dead.py                 # 0/23 defs, 0/116 flags, 0/25 consts
```

All inspection commands above exited 0 unless the exit is stated (137 = SIGKILL kill; 124
would be a plain timeout). No git mutation, no fixture edit, no decoder run outside scratch.
