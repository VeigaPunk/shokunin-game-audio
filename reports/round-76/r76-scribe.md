# R76 scribe (audio) — receipt hygiene + raw-vs-parsed audit (capture direction)

**Headline.** Wave `shokunin-train-20261101-w15`, audio lane, round 76 — written
**mid-flight**: at 17:38Z (local 14:38) **no r76 seat report had landed**
(`reports/round-76/` absent), HEAD was still **`2250be9`**, the fixture blob
**`85fb6914f432aa7dde408e9ca6b96702d953bba6`** was byte-identical to the HEAD
blob (`git hash-object` == `git rev-parse HEAD:corpus/fixtures/measure_audio.py`),
**zero** r76 canonical receipts existed in `corpus/live/runs/`, and `git ls-files
| grep -c r76` → **0**. This seat therefore audited **(a)** the *landed
artifacts* of the four working seats (scout 107 files / boundary 219 / baseline
697 / author 10), **(b)** the carried receipt-hygiene debt from r75 — where the
assignment's **3rd recurrence of the untracked-vs-"committed" wording defect is
CONFIRMED verbatim**, and **(c)** the raw-vs-parsed hazard classes that r76's
capture artifacts already instantiate.

Three measured results carry the round's raw side:

1. **Capture headers are placeholder-bearing in 3 distinct conventions**, so a
   parsed duration/byte field derived from a header contradicts the byte count
   for exactly the classes r76 studies — `arecord` writes `0x7FFFFFFF` (and once
   `0x80000000`) at open, `parec` writes `0`, `lavf`/ffmpeg writes
   `0xFFFFFFFF`. Measured on 181 artifacts: **117 finalized / 19 unfinalized
   declared-zero / 14 placeholder-max / 31 non-wav**.
2. **Captured byte counts are flush-quantized, not time-proportional** — the
   scout's own TERM ladder produced 0 / 0 / 0 / **65536** / **262144** bytes and
   a 2.5 s TERM produced **131072** data bytes (44 B header + 131072); every
   nonzero count is a 64 KiB multiple (`131072` = 2 × 65536), matching the
   SHARED.md carried guard that `io.DEFAULT_BUFFER_SIZE` is build-specific and
   that **rc alone is never a verdict**.
3. **A seat's parsed record and its raw artifact can disagree without either
   being wrong**: the scout's `runs/scout-capture-*.json` records
   `out_bytes: 0` + `wav: {"absent": true}` for `cap-arec-d0`, `sev1-arec-null`,
   `sev2-arec-null` while disk holds **three numbered siblings per leg,
   ~5.5–6.0 GB each** (`-01/-02` at 2 147 483 692 B with a placeholder header,
   `-03` finalized at 1.21–1.75 GB). The zero is a statement about the harness's
   *declared* path in the *current* revision, not about the capture surface.

Seat: **scribe** (leaf, report-only). Host `plazir27`; kernel `7.2.3-arch1-3`;
Python 3.14.7. Clock: **17:29Z** at open, **17:38Z** at write (local TZ = UTC−3;
`ls` mtimes are local, receipt stamps UTC — recorded, not a defect claim). Wave
label `shokunin-train-20261101-w15` (wave-name date ≠ clock date — carried).
Repo `/home/vgpnk/Projects/shokunin/audio-shokunin`. Write scope: this report +
`corpus/live/r76-scribe/` only; no git mutation, no product-code edit, **no
fixture probe mode run, no receipt written by this seat**.

## §0 State at write (17:38Z) — `corpus/live/r76-scribe/final-census-1738.txt`

| item | value |
|---|---|
| HEAD | `2250be9552afb3b06a4e13aeaabd802787fcc6de` (`2250be9`) |
| fixture blob (worktree) / (HEAD) | `85fb6914f432aa7dde408e9ca6b96702d953bba6` / same → **no r76 fixture edit yet** |
| `corpus/live/runs/` | 5622 dirs / 5290 tracked / 332 untracked entries |
| r76 canonical receipts | **0** (`ls -d corpus/live/runs/*r76*` → none) |
| r76 tracked files | **0** |
| `reports/round-76/` | **absent** |
| `r76-scout` | 107 files, **25 GB**, newest `runs/scout-capture-all.json` 17:34:34Z |
| `r76-boundary` | 219 files, 54 MB, newest `probe_boundary_r76.py` 17:35:11Z |
| `r76-baseline` | 697 files, 376 MB, newest `measure-env/...` 17:33:42Z |
| `r76-author` | 10 files, 1.1 MB, newest `scratch/ffm_alsa.wav` 17:34:42Z |
| files > 1 GB under `r76-*` | **13** |

## §1 Landing timeline (this seat's window)

| UTC | event | evidence |
|---|---|---|
| 17:29:56 | `r76-scout/`, `r76-scribe/` exist; HEAD `2250be9` | `corpus/live/r76-scribe/landing-watch.log` iter 1 |
| 17:29–17:30 | scout raw inventory lands (`probe-{pactl-sources,pactl-info,pwlink,arecord-devices,ffmpeg-capture,versions-help}.txt`, `legs/`) | `scout-raw-inventory.txt` |
| 17:30:16 | `r76-boundary/` created | landing-watch iter 2 |
| 17:30:26 | `r76-baseline/` lands pre-state, toolchain, frozen tar, measure-env build | `pre-state.txt`, `toolchain.txt` |
| 17:31:26 | first 2 GiB-class `arecord -D null` captures on disk | `cap-arec-d0-01/02.out` |
| 17:31:35 / 17:31:45 | boundary batches `boundary-r76-gates`, `-name` receipts written | `runs/*/measurements.json` |
| 17:32:06 | scout `runs/scout-capture-gates.json` (43 legs) | JSON `utc` field |
| 17:33:13–17:33:19 | more numbered captures (`x-arec-null-nod-0{1..4}`); boundary `-main` batch starts | `legs/`, `logs/run-main.out` |
| 17:33:40 | **boundary `main` batch crashes** — `probe_boundary_r76.py:414` `ValueError` in `sever_cells` (verbatim below) | `logs/run-main.out` |
| 17:34:34 | scout `runs/scout-capture-all.json` (64 legs) | JSON `utc` field |
| 17:35:11 | boundary **rewrites** `probe_boundary_r76.py` (34782 B) — recovering from the crash | mtime |
| 17:35:31–17:36 | boundary batch 3 `boundary-r76-main2` running; scout still writing (`legs/wchan-test-28.wav` 17:35:59Z) | `runs/…-main2/cells/*.log` |
| 17:34:56–17:38 | this seat's audits run; **no sibling report landed** | `final-census-1738.txt` |

Boundary crash, verbatim (`corpus/live/r76-boundary/logs/run-main.out`):

```
  File ".../corpus/live/r76-boundary/probe_boundary_r76.py", line 414, in sever_cells
    t1, t2, tk = dict(PHASES)[phase]
                 ~~~~^^^^^^^^^^^^^^
ValueError: dictionary update sequence element #0 has length 3; 2 is required
```

Recorded as an **event**, not a verdict: the script was rewritten 91 s later, so
the seat is self-recovering. Any boundary `sever`-group claim must be re-read
after that re-run.

## §2 Receipt hygiene

### 2.1 F1 — "committed receipt" for an untracked receipt: 3rd recurrence CONFIRMED

| evidence | value |
|---|---|
| `reports/round-75/r75-author.md:55` | `## Measured (committed receipt \`runs/20261014T165017429491Z-consumers2-r75\`, \`failures: {}\`; byte-identical ×3 — sha256 \`0829a5986b…\` reproduced by \`…T164819Z\` and \`…T164913Z\`)` |
| `reports/round-75/r75-author.md:170` | "consumers2-r75` (**committed shape**) + two byte-identical prior runs" |
| `reports/round-75/r75-author.md:173-174` | "No git mutation, no commits — all work left **uncommitted** for the integrator" (self-contradiction inside the same report) |
| `git ls-files corpus/live/runs \| grep -c consumers2` | **0** |
| commit `2250be9` content | `LOG.md`, `SCORECARD.md`, `reports/round-75/*.md` — **no receipts** (`git show --stat 2250be9`) |
| canonical judge's own record | `reports/round-75/r75-adjudicator.md:71-72` — "Recurring defect (**3rd recurrence**): author report called untracked scratch receipts 'committed' — filed report stands; flagged in adjudication." |

So: **members committed, receipts not**; the wording drift is confirmed for the
3rd time (r73→r74→r75 lineage per `r75-scribe.md:313` F1 and this instance).
The **ledger itself is clean** on this point: `LOG.md`'s r75 entry (lines
1250-1269) says only "receipts byte-identical ×5" — no "committed". No r76
artifact yet repeats the defect (`grep -rn -i "committed\|commit"` over
`r76-scout/*.py`, `r76-scout/runs/*.json`, `r76-boundary/*.py`,
`r76-boundary/logs/*.out` → 0 hits).

**Naming rule carried for r76** (from `r75-scribe.md:398-399`): say
**"on-disk receipt"** unless the integrator commits it. A receipt under
`corpus/live/runs/` that `git ls-files` does not list is **untracked**.

### 2.2 The canonical r75 family on disk today: 7 receipts / 3 sha groups

| receipt dir (UTC stamp) | bytes | sha256[0:16] | entries | non-empty `failures` |
|---|---|---|---|---|
| `…T164819343934Z` | 99159 | `0829a5986bb6ca70` | 29 | 0 |
| `…T164913129596Z` | 99159 | `0829a5986bb6ca70` | 29 | 0 |
| `…T165017429491Z` | 99159 | `0829a5986bb6ca70` | 29 | 0 |
| `…T165717676332Z` | 99159 | `0829a5986bb6ca70` | 29 | 0 |
| `…T165821738609Z` | 99159 | `0829a5986bb6ca70` | 29 | 0 |
| `…T171455054130Z` | 101630 | `0da11c7daa897c3c` | 29 | **7** |
| `…T172034398145Z` | 99852 | `9de8b8f8483cb777` | 29 | 0 |

- The "byte-identical ×5" claim in `LOG.md` / `r75-adjudicator.md:22` matches
  the 5×`0829a5986b` group exactly (this seat re-hashed all 7).
- **The last two receipts are orphans**: `grep -rn "171455\|172034"`
  over `reports/round-75/*.md`, `LOG.md`, `SCORECARD.md` → **0 hits**. They are
  fold-intermediate revisions left in the canonical dir: their leaf diff vs the
  `0829a5986b` group is 107 / 92 leaves, including new fields
  (`viable_legs` `None → 4`, `alive_after_term1` `None → True` replacing
  `sigterm_immune`) — i.e. the C1/C2 folds of `5f60747` were already live in the
  worktree when those two runs were written.
- **The 17:14:55Z receipt carries the vacuity guard FIRING** on exactly the 7
  reject-member probes (`consumer2_{posttable_nomatch,txw_piperefuse,
  extsuffix_wav,extsuffix_bin,extsuffix_txw,extsuffix_f32,extsuffix_snd}_r75_probe`),
  each with two rows, verbatim:
  `transport: paplay collapsed — all four arms errored; the invariance verdict is vacuous (dead server/device)`
  (and the ffplay twin). The 17:20:34Z receipt carries **0**. The adjudicated
  rule (`r75-adjudicator.md:37-44`) is that uniform content rejection on reject
  members is a real verdict, so the 17:14 firing state is the over-firing
  revision; the 17:20 state is the narrowed one. **A future family scan that
  reads `failures` without naming receipts would report 7 false regressions.**
- No top-level `failures` key exists in any of the 7 (the `failures: []` arrays
  live per measurement). `LOG.md:1269` writes "`failures: {}`" — a dict where
  the artifact has a list; cosmetic, but it is the same wording-drift family.

### 2.3 Four r75 receipts pinned by r75 reports are no longer on disk

`r75-scribe.md` pins `…T164125737824Z`, `…T164319396674Z`, `…T164418398152Z`,
`…T164603163948Z` (`:377`, `:440-441`); `r75-critic.md:50` also cites them.
`find` over the whole lane (any file type, `.git` excluded) resolves those
stamps **only** inside: `r75-baseline/{post-state.txt, runs-canonical-after.txt,
runs-canonical-added.txt}`, `r76-baseline/frozen/head-2250be9.tar`,
`reports/round-75/{r75-scribe.md, r75-critic.md}`. No `measurements.json` for
them exists anywhere.

Timing window, from the baseline's own snapshots:

| local | UTC | evidence |
|---|---|---|
| 13:44:17 | 16:44:17 | `r75-baseline/post-state.txt` lists `?? …T164125737824Z` and `?? …T164319396674Z`; `runs-canonical-added.txt` lists exactly those two as added |
| 13:52:48 | 16:52:48 | `r75-baseline/runs-canonical-final.txt` (5618 entries) lists only `…T164819…`, `…T164913…`, `…T165017…` |

⇒ the four were removed **between 16:44:17Z and 16:52:48Z**, before this seat's
generation existed. `stat corpus/live/runs` mtime = `17:20:34Z` (the last
creation) is consistent: a later creation masks the delete time. **Mechanism
unidentified** by this seat (no `rm`/`rmtree` in any r75 scratch script targets
the canonical runs dir; the fixture has no prune path — `grep -n
"prune\|retention\|keep_\|MAX_RUNS" corpus/fixtures/measure_audio.py` → no
hits). `r75-critic.md:50` already recorded the absence ("no longer on disk …
the path-bearing first receipt survives only as a citation"); this seat adds the
window and the negative sweep. **Carried as an open hygiene item: report pins
must resolve at read time, and nothing in the repo guarantees receipt
persistence.**

## §3 Raw-vs-parsed A — capture-header classes (this seat, independent)

Method: `corpus/live/r76-scribe/raw_header_audit_v3.py` walks the RIFF chunk
table in place (v1/v2 were superseded: v1 missed `LIST`-bearing lavf files, v2
assumed `data` at offset 36 and produced a **false** "unfinalized" verdict on
every ffmpeg WAV — corrected before reporting). Output:
`raw-header-audit-v3b.tsv` (181 artifacts; `finalized=117 placeholder-max=14
unfinalized-declared-zero=19 non-wav=31`).

| convention | who writes it | measured example | consequence for a header-derived parse |
|---|---|---|---|
| `data = 0`, `riff = 8` | `parec`/`pw-record` killed or TERM'd before any flush | `out/pa_term.wav` 196652 B, `data_declared=0`, `tail=196608`; `legs/a5-pwrec-nolink.wav`, `out/pw_t0.wav` 44 B `riff=8` | parsed duration = **0.0 s** for a 1.024 s file |
| `data = 0x7FFFFFFF` / `0x80000000` | `arecord` header-at-open, never finalized | `legs/kill-arec-hw00.wav` 216044 B → `data_declared=2147483648`, `tail=216000`; 2 GiB null-device captures | parsed duration ≈ **6.2 h** for a 216 KB (or 2 GiB) file |
| `data = 0xFFFFFFFF` | lavf muxer, LIST-bearing WAV | `legs/ff-flush.wav` 2359296 B **at the v3b snapshot**, `chunks=fmt :16@12\|LIST:26@36\|data:4294967295@70`; `out/pin_ff_8s.wav` 1310720 B, `pin_ff_n_8s.wav` 20447232 B | parsed duration ≈ **12.4 h**; a 44-byte-offset parser also mis-reads `LIST:26` as the data size |
| finalized | `-d N` / `--sample-count` paths, graceful exit | `legs/gate-arec-hw00.out` 192044 → `riff=192036`, `data=192000` (= 1.000 s mono 48 k s16) | parsed == byte count |

**Snapshot discipline for every number in this report.** The four working seats
were still writing at 17:36Z (scout newest file `legs/wchan-test-28.wav`
17:35:59Z; `legs/ff-flush.wav` grew 2359296 B → 11534336 B between the v3b
snapshot and 17:36Z; boundary started a third batch `boundary-r76-main2`
17:35:31Z). Every size/hash here is therefore stamped: **`raw-header-audit-v3b.tsv`
(17:35Z, 181 artifacts)** and **`final-census-1738.txt` (17:34:56Z)**; live
values may differ. This is the same class as F8 (§4.2), stated at report level.

**Flush quantization (raw, this seat).** `flush-parec-term-{0.5,1.0,1.5,2.0,3.0}.wav`
= 0 / 0 / 0 / **65536** / **262144** bytes on disk; `cap-parec-ff-wav-term-2.5.wav`
= 131116 B = 44 + **131072** (finalized, `riff=131108`, `data=131072`).
Every nonzero count is an exact multiple of 65536; `131072` is 2 × 65536. So a
"bounded capture" byte count is set by the writer's flush quantum and the moment
of the signal, **not** by the requested duration — the SHARED.md guard
(`io.DEFAULT_BUFFER_SIZE=131072` is build-specific; wire order + write order both
needed as witness) is instantiated by r76's own artifacts.

**Live-device content is not reproducible (raw, this seat).**
`legs/c1-arecord-null.wav` and `legs/c4-arecord-plughw00.wav` are both exactly
96044 B (1.000 s mono 48 k s16) with **different** sha256
(`02a5aeeaac4593b2` vs `0dcc24b97fe80056`); `legs/name-arec-t-raw.raw` vs
`...-ext-wav.wav` likewise 192000 B with different content
(`d2d3394ada3a4f7d` vs `2cb849e5ca669528`). Conversely the *unpaced* null-device
captures **are** reproducible: `x-arec-null-nod-01/02/03.wav` share sha16
`3407a98f15a3c4f2` (2 147 483 692 B each), and `cap-arec-d0-01 == -02`
(`87287b53da75dde5`), `sev2-arec-null-01 == -02` (`adb4be8d340f4922`). Any
"byte-identical ×N" claim in the capture direction must therefore name the
device class (unpaced-null vs real capture), not just the consumer.

## §4 Raw-vs-parsed B — seat-local receipts vs disk

### 4.1 The scout's JSON: `out: None` for all 43 legs, and 0-byte records beside GB of disk

`corpus/live/r76-scout/runs/scout-capture-gates.json` (utc 17:32:06Z, 43 legs;
`scout-capture-all.json` utc 17:34:34Z, 64 legs) records `"out": null` for
**every** leg; the only path is inside `argv[-1]` (absolute, unscrubbed — 43/43).
For the three arec-null legs it records `out_bytes: 0`, `out_sha16: null`,
`wav: {"absent": true}` while disk holds:

| leg id | declared path | recorded | numbered siblings on disk (v3b snapshot, 17:35Z) |
|---|---|---|---|
| `cap-arec-d0` | `legs/cap-arec-d0.out` | `bytes=0`, `wav={absent:true}`, `rc=1`, `term=1.208` | `-01` 2147483692, `-02` 2147483692, `-03` 1639824044 (sha `0d027c631333c020`) |
| `sev1-arec-null` | `legs/sev1-arec-null.out` | `bytes=0`, `wav={absent:true}` | `-01` 2147483692, `-02` 2147483692, `-03` 1750824044 (`47e30564e42eb6ca`) |
| `sev2-arec-null` | `legs/sev2-arec-null.out` | `bytes=0`, `wav={absent:true}` | `-01` 2147483692, `-02` 2147483692, `-03` 1213392044 (`b8a07e2884dc6c8f`) |

The harness that wrote the JSON (`corpus/live/r76-scout/capture_probe.py`, read
in full) computes `out_path = LEGS/spec["out_name"]`, **`os.remove`s** it before
each run (`:220-225`), and stats it after (`:274`). It cannot produce the
numbered names, and its own `scrub()` replaces the legs path with `<legs>` in
`stderr_tail` while leaving `argv` absolute (`:213`). So: **the 0-byte record
describes the current revision's declared path, not the leg class** — a reader
must not infer "arecord -d 0 produced nothing on this host" from it.

### 4.2 Recorded values go stale as soon as a leg is re-run (harness deletes first)

Three legs' recorded fields no longer match disk (this seat's readings, 17:40Z
and 17:42Z vs JSON snapshots 17:32:06Z / 17:34:34Z):

| leg | recorded | disk now | class |
|---|---|---|---|
| `gate-pwrec-sink-capsink-sc` | sha16 `3ac1bdf363578593` | sha16 `0cb129400ef49770` (same 19244 B) | re-run replaced content |
| `gate-parec-defsrc` | 1966080 B | 1703936 B | file still being rewritten (12 s wall bound, `rc=-9`) |
| `name-parec-ff-wav` | `riff_size=36` (finalized) | `riff_size=8` (unfinalized) | header state changed by a later attempt |

⇒ a seat-local receipt is only valid against the file state at its write instant;
the harness's delete-then-write pattern makes earlier receipts **unverifiable**,
not wrong. Report wording should pin "as of <stamp>".

### 4.3 Boundary receipts: a second schema under the same filename, and host paths

`corpus/live/r76-boundary/runs/*/measurements.json` and `gates-measurements.json`
are **JSON lists** of cell records (`argv`, `cell`, `out`, `probe`, `quant`,
`rc`, `riff`, `sha256`, …) — not the fixture ledger dict
(`mode/thresholds/measurements/…`). A family scanner that globs
`**/measurements.json` and assumes the ledger idiom will fail on these
(`json.load(...).get` → `AttributeError`, observed). Both boundary and scout
seat-local records embed **absolute host paths** in `argv`/`out` (e.g.
`"/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r76-boundary/out/nm_pw_n.wav"`),
which is the same path-embedding class the r75 baseline counted (13-mode class).
Acceptable for scratch; **must be scrubbed before any promotion to a canonical
receipt family**.

Independent re-measure of the boundary's referenced captures
(`seat_receipt_crosscheck.py`, 17:47Z): **50 size+sha agree, 18 not yet written**
(the newest `gates2`/`main` batches were still landing — in-flight, not defects).
The boundary's own `riff`/`quant` blocks were confirmed against disk on every
settled row.

## §5 Report integrity checks that PASSED (this seat)

| check | command | result |
|---|---|---|
| frozen archive self-consistency | `tar -tf …/head-2250be9.tar \| wc -l` vs `wc -l archive-manifest.txt` | **29039 == 29039**; tar sha256 `e22f852a0e184f6f4ca6b428f2aaa030b45089ce6d634123ed4ebb313b466489` == `frozen/archive-sha256.txt` |
| committed-ledger pin resolves | `git ls-tree -r HEAD \| grep c4f5c619…` → `corpus/live/r70-author/ledger-r71.tsv`; `git cat-file blob c4f5c619 \| sha256sum` | **`8d59f552e1370c5e…` == `committed-ledger-sha.before.txt`**; identical pin in r75 and r76 baselines ⇒ ledger byte-stable across the wave boundary |
| pre-state receipt census | `wc -l runs-canonical-before.txt` vs `ls -d corpus/live/runs/*/ \| wc -l` | **5622 == 5622** (17:30:37Z) |
| scout probe files re-measured | `pactl list sources short`, `arecord -l` (17:34–17:35Z) vs `probe-pactl-sources.txt`, `probe-arecord-devices.txt` | source/device **rows identical**; only the volatile state column differs (Line source `SUSPENDED` → `RUNNING`) |
| r75 receipt hashes | `sha256sum corpus/live/runs/*consumers2-r75*/measurements.json` | 5× `0829a5986bb6ca70`, plus `0da11c7daa897c3c`, `9de8b8f8483cb777` (matches §2.2) |

## §6 Hazards (measured, for the operator/integrator)

1. **25 GB of untracked scratch, not ignored.** `du -sh corpus/live/r76-scout`
   = 25 GB (107 files; 13 files > 1 GB; largest 2 147 483 692 B × 10).
   `git status --porcelain corpus/live/r76-scout/legs/cap-arec-d0-01.out` → `??`
   and `git check-ignore -v …` → **NOT ignored** (`corpus/.gitignore` covers
   `tree/`, `frozen/`, `head/`, `snapshot/`, `*.tar`, `live/r71-critic/big.wav`,
   `live/*/measure-env/` — no rule covers `legs/*.out`). A `git add -A` at
   integration would stage ~25 GB (GitHub hard limit 100 MB/file; the r70
   precedent is `head.tar` 265 MB flagged "oversized … untracked+ignored").
   Disk headroom is not the constraint (845 GB free, 9 % used).
2. **Device/source state is contention-sensitive.** `arecord -l` sampled 4 s
   apart: card 0 device 0 `1/1 → 0/1 → 1/1`; device 1 **0/1 in all three
   samples** — held by the PipeWire daemon (`fuser -v /dev/snd/pcmC0D1c` →
   `pipewire` pid 1203634, `F...m`). A sibling capture was live during the
   sample (`ffmpeg … -f pulse -i …Line__source -t 2 -f s16le …/r76-scout/legs/cap-ff-pulse-raw-t2.raw`).
   ⇒ `hw:0,1`-based cells are daemon-blocked, `hw:0,0` cells race sibling seats,
   and a `blocked` verdict from either must name the sampling instant and the
   concurrent holder. `arecord -l` "Subdevices" is **not** a stable gate input.
3. **Unpaced `-D null` capture is unbounded in bytes.** `arecord -D null`
   without `-d` produced 2 GiB files in ~1–3 s of wall time (13 files > 1 GB,
   written 17:31:26–17:33:19Z). Any r76 arm that touches `-D null` without a
   byte or duration bound must carry an explicit cap; the 25 GB above is the
   evidence.
4. **Orphan receipts in the canonical dir** (§2.2) and **unresolvable pins**
   (§2.3) — both degrade family-level aggregation.

## Findings (verbatim for the canonical judge)

- **F1 — "committed receipt" wording drift, 3rd recurrence CONFIRMED** in
  `reports/round-75/r75-author.md:55` and `:170`, contradicted by `:173-174`
  ("all work left uncommitted") and by `git ls-files corpus/live/runs | grep -c
  consumers2` → **0**; already filed by the canonical judge
  (`r75-adjudicator.md:71-72`). Members committed, receipts not.
- **F2 — the canonical r75 family is 7 receipts / 3 sha groups**, not 5: the
  17:14:55Z (`0da11c7daa897c3c`, 101630 B) and 17:20:34Z (`9de8b8f8483cb777`,
  99852 B) receipts are **uncited by every r75 report, `LOG.md` and
  `SCORECARD.md`** (0 grep hits). "Byte-identical ×5" is correct only for the
  `0829a5986b` group.
- **F3 — the 17:14:55Z receipt carries the vacuity guard firing on 7 reject
  members** (2 rows each, `… collapsed — all four arms errored; the invariance
  verdict is vacuous (dead server/device)`); the 17:20:34Z receipt carries 0.
  Both states are on disk. Reading `failures` without naming receipts yields 7
  false regressions.
- **F4 — the four r75 receipts pinned by `r75-scribe.md:377/440-441` and cited
  by `r75-critic.md:50` no longer exist**; they were on disk at 16:44:17Z
  (`r75-baseline/post-state.txt`, `runs-canonical-added.txt`) and gone by
  16:52:48Z (`runs-canonical-final.txt`). Mechanism unidentified; no prune path
  exists in the fixture or in any r75 scratch script. Carried by
  `r75-critic.md:50`.
- **F5 — three placeholder-header conventions in r76 capture artifacts**
  (`0` parec/pw-record, `0x7FFFFFFF`/`0x80000000` arecord, `0xFFFFFFFF` lavf);
  14/181 artifacts carry a max placeholder, 19/181 an unfinalized zero. A
  header-derived duration contradicts the byte count in every one.
- **F6 — captured byte counts are flush-quantized**: 0/0/0/65536/262144 (TERM
  ladder) and 131072 (2.5 s TERM) — all 64 KiB multiples; `131072` = 2 × 65536.
  Duration bounds do not translate into byte bounds (SHARED.md guard
  instantiated).
- **F7 — the scout's JSON records `out: null` for all 43 legs and `out_bytes: 0`
  with `wav:{absent:true}` for the three arec-null legs**, while disk holds 9
  numbered siblings (5.5–6.0 GB per leg, two of three with a placeholder
  header). Provenance-scoped zero, not an empty capture surface.
- **F8 — seat-local receipts go stale**: 3 legs' recorded sha/size/header no
  longer match disk because the scout harness `os.remove`s and rewrites the
  declared path per run (`capture_probe.py:220-225`, `:274`).
- **F9 — schema collision**: `corpus/live/r76-boundary/runs/*/measurements.json`
  is a JSON **list**, not the fixture ledger dict — a `**/measurements.json`
  family scan breaks on it (observed `AttributeError`).
- **F10 — host paths in seat-local evidence**: 43/43 scout `argv` and all
  boundary `argv`/`out` fields are absolute; tails are scrubbed (`<legs>`,
  `<scout>`), argv is not. Same class as the r75 13-mode path-embedding set.
- **F11 — device availability is dynamic and contention-driven**: `arecord -l`
  device 0 `1/1→0/1→1/1` in 8 s; device 1 pinned `0/1` by the PipeWire daemon
  (`fuser` evidence). A `blocked` device verdict needs the sampling instant.
- **F12 — live-device capture content is not reproducible** (same-size,
  different-sha pairs), while unpaced-null captures are
  (`3407a98f15a3c4f2` ×3, `87287b53da75dde5` ×2). Byte-identical claims must
  name the device class.
- **F13 — 25 GB of untracked, unignored capture scratch** under
  `corpus/live/r76-scout/legs/` (13 files > 1 GB) — an integration hazard, not a
  disk-capacity one.
- **F14 — boundary `main` batch crashed at `probe_boundary_r76.py:414`**
  (`ValueError: dictionary update sequence element #0 has length 3; 2 is
  required`, `logs/run-main.out`); script rewritten 91 s later (self-recovery).
  `sever`-group claims from that batch must be re-read after the re-run.
- **F15 — `LOG.md:1269` writes `failures: {}`** where the artifact carries
  per-measurement `failures: []` lists and no top-level key; cosmetic, same
  wording-drift family as F1.
- **F16 — carried state, unchanged**: HEAD `2250be9`, fixture blob
  `85fb6914…` == HEAD, zero r76 canonical receipts, zero r76 tracked files,
  `reports/round-76/` absent at 17:38Z — this report audits artifacts, not
  verdicts.

## Gates

| gate | state (17:38Z) |
|---|---|
| author arm landed | **NO fixture edit** — worktree blob `85fb6914…` == HEAD blob; author scratch only (`scratch/{arc_hw,pwr_t,parec_d,pwr_mon,pwr_n96k,mon,ffm_alsa,…}.wav`) |
| r76 canonical receipts | **0** |
| r76 tracked files / commit | **0** / none (`git log 2250be9..HEAD` = 0) |
| seat reports | **0 of 5** audio seats (`reports/round-76/` absent) |
| prior rows byte-stable | not yet testable (no author edit); ledger pin `8d59f552…` == r75 baseline pin |
| insertion-only | not yet testable (no fixture diff) |
| raw-vs-parsed audit (this seat) | DONE — 181 artifacts classified; 3 placeholder conventions; flush ladder; 3 legs' records stale vs disk |
| receipt hygiene (this seat) | DONE — F1 3rd recurrence confirmed; 7/3 family census; 2 orphans; 4 unresolvable pins; schema collision |
| report integrity (this seat) | DONE — tar/manifest, ledger pin, runs census, probe re-measure all pass |
| verifier replay / adjudication | not started (no r76 commit) |
| ledger (LOG/SCORECARD) | not drafted — r76 arm uncommitted; wording rule for the eventual entry: **"on-disk receipt"** unless committed (F1) |

## LOG / SCORECARD draft (conditional — nothing to ledger yet)

The r76 move (`--probe-capture-r76`, capture direction: pw-record / parec /
arecord / ffmpeg) has **no landed fixture edit and no receipt** at this seat's
write. When it lands, the ledger entry must name: the consumer set and the exact
argv shapes; the source/device gate instant (`pactl list sources short`,
`arecord -l` are **state-varying** — F11); the byte-bound class per consumer
(F6); the header-finalization class per consumer (F5) — **and it must not derive
duration from a header**; the device class for any byte-identity claim (F12);
and it must name receipts by stamp with their revision, since the r76 canonical
dir will otherwise mix pre-fold and post-fold variants exactly as r75's did
(F2/F3). `failures` rows must be read as fork/vacuity signatures, not defects.

## Touched surfaces

- Wrote **only**: `reports/round-76/r76-scribe.md` and
  `corpus/live/r76-scribe/**` (`landing-watch.log`, `scout-raw-inventory.txt`,
  `wave-start-state.txt`, `final-census.txt`, `final-census-1738.txt`,
  `raw_header_audit.py`, `raw_header_audit_v3.py`, `raw-header-audit-1732.txt`,
  `raw-header-audit-v3.{tsv,err}`, `raw-header-audit-v3b.{tsv,err}`,
  `seat_receipt_crosscheck.py`, `seat-receipt-crosscheck-1735.txt`,
  `scout_crosscheck_v2.py`, `scout-crosscheck-1740.txt`,
  `scout-crosscheck-1742.txt`, `boundary-crosscheck-1747.txt`,
  `reverify-pactl-sources-1735.txt`, `reverify-arecord-l-1735.txt`).
- No tracked file modified by this seat; no git mutation; no product-code edit;
  **no fixture probe mode run; no receipt written by this seat**. Sibling
  scratch (scout/boundary/baseline/author) read-only.
- Live-stack disclosure: read-only `pactl list sources short`, `arecord -l`
  (4 samples), `fuser -v /dev/snd/pcmC0D1c`, `ffprobe -v error` on 14 capture
  files, `xxd`/header reads; no capture process started, daemon untouched.

## Out-of-scope (explicitly not done)

- Auditing sibling *reports* — none had landed at 17:38Z; claims made in the
  r76 scout/boundary/baseline/author reports are outside this seat's window.
- Adjudicating the r76 capture arm, its partition, or any seat's scratch as a
  verdict; running the author's probe mode; writing or re-deriving receipts.
- Deleting or ignoring the 25 GB scratch (operator/integrator-owned); patching
  the scout harness or the boundary script (F7/F8/F14 are reported, not fixed).
- Commit/push/publish (operator/integrator-owned).

## Artifact paths + hashes (scratch, this seat; sha256[0:20])

| artifact | sha256[0:20] |
|---|---|
| `corpus/live/r76-scribe/raw_header_audit_v3.py` | `1c3fb24830f33049857f` |
| `corpus/live/r76-scribe/raw-header-audit-v3b.tsv` | *(181 rows; see `final-census-1738.txt` for the run stamp)* |
| `corpus/live/r76-scribe/scout_crosscheck_v2.py` | `23f922f38ee2407fc942` |
| `corpus/live/r76-scribe/seat_receipt_crosscheck.py` | `4ded5653a11ab51d8af7` |
| `corpus/live/r76-scribe/raw_header_audit.py` | `612617fdf38d1a69c9b9` |
| `corpus/live/r76-scribe/final-census-1738.txt` | `a47d742ba3646f74a433` |
| `corpus/live/r76-scribe/scout-crosscheck-1742.txt` | `1fe46dd54e82fa5bc4db` |
| `corpus/live/r76-scribe/boundary-crosscheck-1747.txt` | `7612785968209aef31df` |
| `corpus/live/r76-scribe/wave-start-state.txt` | `d0dce6bf51540d6cf287` |
| `corpus/live/r76-scribe/landing-watch.log` | (append-only; live) |

Evidence cited (read-only, not this seat's): `r75-author.md:55/170/173`,
`r75-adjudicator.md:22/37-44/71-72`, `r75-critic.md:50`, `r75-scribe.md:377/398-399/440-441`,
`r75-baseline/{post-state,runs-canonical-added,runs-canonical-final}.txt`,
`r76-baseline/{committed-ledger-sha.before,frozen/archive-sha256,runs-canonical-before}.txt`,
`r76-scout/{capture_probe.py,runs/scout-capture-{gates,all}.json,probe-*.txt}`,
`r76-boundary/{logs/run-main.out,probe_boundary_r76.py,runs/*/measurements.json}`,
`corpus/live/runs/20261014T{164819343934,164913129596,165017429491,165717676332,165821738609,171455054130,172034398145}Z-consumers2-r75/measurements.json`.

## Exact commands / exits (appendix)

```sh
cd ~/Projects/shokunin/audio-shokunin
# state
git rev-parse HEAD                                   # 2250be9552afb3b0… (2250be9)
git hash-object corpus/fixtures/measure_audio.py     # 85fb6914f432aa7d… == HEAD blob
git ls-files corpus/live/runs | grep -c consumers2   # 0  (receipts untracked)
git show --stat --oneline 2250be9                    # reports+LOG+SCORECARD only, no receipts
ls -d corpus/live/runs/*consumers2-r75* | wc -l      # 7
sha256sum corpus/live/runs/*consumers2-r75*/measurements.json   # 5×0829a598… + 2 distinct
grep -rn "171455\|172034" reports/round-75/*.md LOG.md SCORECARD.md   # 0 hits (orphans)
find . -path ./.git -prune -o -name '*164125*' -print -o -name '*164418*' -print -o -name '*164603*' -print   # only baseline snapshots + reports
grep -n "committed receipt\|committed shape\|left uncommitted" reports/round-75/r75-author.md   # :55, :170, :173
# integrity
tar -tf corpus/live/r76-baseline/frozen/head-2250be9.tar | wc -l     # 29039 == manifest
sha256sum corpus/live/r76-baseline/frozen/head-2250be9.tar           # e22f852a… == archive-sha256.txt
git ls-tree -r HEAD | grep c4f5c619…                                 # corpus/live/r70-author/ledger-r71.tsv
git cat-file blob c4f5c6196f398585f55a8237ab9cbc3f34760621 | sha256sum  # 8d59f552… == pin
# raw-vs-parsed
python3 -B corpus/live/r76-scribe/raw_header_audit_v3.py corpus/live/r76-scout/legs corpus/live/r76-boundary/out > raw-header-audit-v3b.tsv   # 181 artifacts
python3 -B corpus/live/r76-scribe/scout_crosscheck_v2.py     # 28 OK / 2 DIFF / 13 MISS-or-SIB
python3 -B corpus/live/r76-scribe/seat_receipt_crosscheck.py # boundary: 50 OK / 18 in-flight
pactl list sources short; arecord -l; fuser -v /dev/snd/pcmC0D1c     # F11 contention evidence
```

Exit codes: all inspection commands exited 0; the deliberate zero-match greps
return 1 (`grep -c` → 0). One transient in this seat's own tooling: `raw_header_audit.py`
(v1) reported a `LIST`-bearing lavf WAV as unfinalized — **false positive,
corrected in v3 before any finding was written**; v1/v2 are preserved unedited in
the scratch dir as the audit trail.

**Seat stop.** Report complete; no further action taken (leaf, no dispatch, no
commit, no receipt).
