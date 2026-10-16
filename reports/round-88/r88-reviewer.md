# r88 REVIEWER — wave-B gate on committed `c19bec96`

**Seat: REVIEWER (executor-class, leaf, frozen `probeParent`).** Lane
`/home/vgpnk/Projects/shokunin/audio-shokunin`. Scope **only** the r88
btwit landing: `git show c19bec96 -- corpus/fixtures/measure_audio.py`
(committed blob sha256
`ad9d59b1e0dc5e2be4274f4966e571dabefed94076c06093eed1bf4cd2aef4c4`,
30 504 lines) plus `reports/round-88/r88-author.md` (+175) and the two
green receipts under `corpus/live/runs/`. The worktree fixture was
**byte-identical to the committed blob at entry and at exit**
(`ad9d59b1…`); every measurement below ran against a **frozen
`git archive c19bec96` tree**
(`corpus/live/r88-reviewer/tree/`, 44 064 files / 0 symlinks), never the
worktree fixture. **Zero tracked writes** — this seat's only writes are
`?? corpus/live/r88-reviewer/**` and the new `reports/round-88/r88-reviewer.md`;
nothing committed, nothing pushed; **no `set-default-*`, no subject-0
write**; every audio object this seat created is `r88r_*`-tagged,
name-verified-unloaded and census-confirmed gone (§7). The tracked
`.pyc` dirt predates this seat (mtime 04:22:52 local; seat window
04:25→04:35 local). `TMPDIR=~/Projects/shokunin/tmp`,
`PYTHONDONTWRITEBYTECODE=1`. **Load preferred: every replay ran at
loadavg 63–80** with the **r88 verifier's own frozen-tree btwit replay
live throughout** (its `battery-v45.sh`; my r88r1 receipts record its
residue as foreign witnesses — §5.3).

The frozen `probeParent` seat dispatched **exactly one** `ufo-labrat`
(agent `03c9e94f`, bounded, read-only, no edits) on a fail-open-arm
hypothesis. Its three findings were **re-derived by this seat** (F2, F3,
F4) — two confirmed empirically, one confirmed in code; its crash-path
observation is folded into F4.

---

## 0. Verdict

**PASS with findings.** The r88 family is **insertion-only** (surgery
proof: dropping the inserted block and reversing the five wiring
splices reproduces the parent blob **byte-for-byte**, sha256
`be31da67…`), `py_compile` is clean, prior r76–r87 rows are untouched,
and **every armed verdict re-derives independently from receipt data
alone — 106 checks/run, 106/106 on both committed receipts and on 2 of
my 3 frozen-tree replays (424/424 green checks)**. The encoded boundary
corrections are armed as data and all reproduce: the bluetooth class is
**vacuous by absence** (HID-only DualSense with `audio_uuids=[]`, zero
bluez cards/sinks/modules, 4/4 `create-node` fabrications refused with
`res:-2`/`res:-22` and zero residue, the live BLE-MIDI bridge pinned as
the stack-alive witness), `pw-dump <K>` is the **`{id==K} ∪
{serial==K}`** set query (4/4 legs + mode invariance), `ls Metadata` is
a strict superset of the dump set (**9 vs 4**, extra
`[35,37,38,41,42]`, 3/3 runs), pactl's sink index **is** the native
`object.serial` (**6/6, 0 violations**), and the `pw-top` traps hold
(`-n 1`/`-n 0` one all-`C` frame, `-n 3`'s last frame carries real
states, `-n -1`/`abc` infinite bound-killed, `-r` bogus the one loud
rc 255). The sharpest finding is **load-sensitive, not law-breaking**:
the `wd_dump_empty` arm requires the `pw-dump ''` id-set to equal one of
two bracketing censuses *exactly*, so under co-tenant churn it
**false-FAILs (fail-closed)** — reproduced once in three replays and
then deterministically (F1). Secondary findings are fail-open or
evidence-only (F2–F4), a silent lock-open failure (F5), an incomplete
dev-run disclosure (F6) and the known cross-ROOT lock residual (F7).

| check | required | measured | verdict |
| --- | --- | --- | --- |
| committed-blob pin | `c19bec96` fixture | `ad9d59b1…`, 30 504 lines; worktree byte-identical at entry **and** exit | PASS |
| diff shape | insertion-only, 79 legs / 3 entries, +1772/−3 | numstat `1772 3`; 28+41+10 = 79 legs; only the 3 shared splices modified | PASS |
| surgery proof | parent reconstructible | reversed diff → sha256 `be31da67…` **BYTE-EXACT** | PASS |
| `py_compile` | clean | rc=0 on the pinned blob | PASS |
| committed receipts ×2 | `failures: {}` | `20261016T072313132218Z` + `20261016T072341162452Z`: 79 legs, 0 failures, no `coverage_blocked` | PASS |
| independent law re-derivation | armed law set | **106 checks × 4 green receipts = 424/424** (A, B, r88r1, r88r3); dev-run control 78/102 reproduces the recorded failure surface on a 75-leg pre-correction revision | PASS |
| bluetooth vacuous-by-absence | pinned honestly | HID-only DualSense (`1124`,`1200`; `audio_uuids=[]`), 0 bluez cards/sinks, 4/4 refusals `res:-2`/`res:-22` rc 0, 0 residue, BLE-MIDI bridge live | PASS |
| `{id∪serial}` set rule | armed both key kinds | 4/4 `got == predicted`; `-R`/`-i 0`/`-s` membership invariant; 0 nested Port objects | PASS |
| ls⊋dump Metadata split | 9 vs 4 | 9 ls ids vs 4 dump ids, extra `[35,37,38,41,42]`, ls-only id silent rc 0 — **3/3 runs** | PASS |
| pactl-index == serial | all matched sinks | **6/6 matched, 0 violations**, own index follows — 3/3 runs | PASS |
| pw-top `-n` traps | armed as measured | `n1` 1×12 all-`C`; `n3` 3 frames `[C]→[I,S]→[I,S]`, own row `S` (independent spot); `n0` 1 frame; `nneg`/`nabc` SIGKILL@4.0 s; `rbogus` rc 255 | PASS |
| frozen-tree replay (load) | green | r88r1 `…T072815…` rc=0, r88r3 `…T072952…` rc=0; r88r2 `…T072937…` **rc=1 — F1 false-fail, diagnosed** | PASS-with-finding |
| fixed-path lock | NOT TMPDIR-scoped | resolved path invariant across TMPDIRs; same-ROOT cross-TMPDIR probes **serialized end-to-end** (r88r3 waited ~12.9 s); cross-ROOT not serialized (**F7**, known class) | PASS-with-finding |

---

## 1. Landing integrity

- `git show --stat c19bec96`: exactly two files — the fixture
  (`+1772/−3` per numstat; the `--stat` 1775 is +1772−3 churn) and the
  175-line author report. The two green receipts and the family lock are
  **untracked** `corpus/live/` artifacts (the r83–r87 convention; the
  orchestrator commits seat receipts later).
- **Insertion-only surgery** (`r88r_surgery.py`): drop committed lines
  27507–29254 (the 1748-line r88 block), the
  `--probe-btwit-r88` argument line, the 20-line `if args.probe_btwit_r88:`
  branch, and the three inserted terms from the `sum([…])` mutex, `mode`
  and `suffix` splices → rebuilt bytes sha256
  `be31da679be229074690dc5157edcc122612560594baa8ba62a9b5ce26dd9516`
  = parent `a7d2367b` blob, **BYTE-EXACT**. Prior rows are provably
  untouched.
- `python3 -m py_compile` on the pinned blob: rc 0.
- Wiring is complete and collision-free: arg, mutex term, mode, suffix,
  branch, family lock; only one `--probe-*` mode can be selected.

## 2. Independent re-derivation (receipt-only)

`r88r_audit.py` re-implements **every armed verdict branch** of the three
entries (lines 27507–29252 of the pinned blob) against receipt JSON only
— no fixture import, no live host. One check per law (set-rule 4,
mode-invariance 3, cli singleton 3, propblock 1, keysets 2, types 2,
params 3, silent classes 5, dump-empty/2/color/neg 4, ls-metadata 2,
info-all 1, enum classes 5, dead serial 1, serial law 1, state3 1,
bluetooth 21, pw-top 10, teardown 6, structure 4):

| receipt | checks | passed | failed | note |
| --- | --- | --- | --- | --- |
| A `…T072313132218Z` | 106 | 106 | 0 | committed green |
| B `…T072341162452Z` | 106 | 106 | 0 | committed green |
| r88r1 `…T072815755760Z` | 106 | 106 | 0 | my replay, co-tenant verifier |
| r88r2 `…T072937176820Z` | 106 | 104 | 2 | F1 false-fail (one law) |
| r88r3 `…T072952725402Z` | 106 | 106 | 0 | my replay, post-lock |
| dev `…T071710822152Z` | 102 | 78 | 24 | pre-correction revision control |

- The dev run is the **04:17 local RED run** (75 legs: 28+39+8; 14
  recorded failure strings; 1 `coverage_blocked`); my audit reproduces
  its failure surface (its `cli_cant_create` classes, empty
  `ls`-Metadata parse, missing `pt_n3`/`wd_enum_props` legs prove it
  predates the committed revision). See F6 for the disclosure gap.
- The one receipt-unrecoverable sub-check (`pt_n3` own-row identity —
  `stdout_raw` is popped by design) was **closed by an independent
  spot**: `pw-top -b -n 3` on a seat-owned null sink →
  frames `[12,12,12]`, first frame `["C"]`, last frame `{I:3, S:9}`,
  **own row `S`** (id 102), 1 attempt, teardown clean
  (`receipts/spot-pwtop-ownrow.json`).
- Volatile-text discipline verified: all normed fields scrub
  `id:<n> seq:<n>`/`object <n>`; the only raw seq counters live in the
  explicitly-raw `*_head` channels (5 occurrences, recorded, never
  armed).

## 3. The brief-named claims — exact evidence (run A; B/r88r1/r88r3 identical modulo volatile ids)

- **Vacuous-by-absence.** `bz_device`: `/org/bluez/hci0/dev_BC_C7_46_34_C5_66`,
  `uuid16 ["1124","1200"]` (HID + PnP only), **`audio_uuids []`**,
  `connected "b false"`, `class "u 1288"`, `icon "input-gaming"`;
  `bz_pactl_lines` = exactly **1** match and it is
  `session.services = "[bluetooth.audio, …]"` (advertisement, not an
  object); `bz_midi_bridge` = the live `bluez_midi.server`
  (`Midi/Bridge`, `api.bluez5.midi.node`); adapter `b true`, Media1
  advertises `110a`+`110b`; 0 bluez cards/sinks; 0 `MediaTransport`;
  20 module ids with **no bluez module**; `bz_spa_inventory` = 14 files;
  `bz_spa_codecs_str` = both substrings, 0 standalone; `find` = 0 hits.
- **4/4 create-node fabrications refused.** rc **0** each,
  `a2dp-sink`/`sink` → `pwcli_remote_enoent` `res:-2`, `a2dp.source`/
  `midi.node` → `pwcli_remote_einval` `res:-22`, all with
  `can't create node`; `bz_own_residue` = `[]`. Positive control:
  `bz_nullsink_ctl` rc 0 with enumerated module.
- **`{id∪serial}` set rule.** `wd_setrule_own_id` `153→["153"]`,
  `own_serial` `251940→["153"]`, `foreign_id`/`foreign_serial` `29→["29"]`
  — **4/4 `got == predicted`**, `churn_recensus false`; `-R`/`-i 0`
  `["153"]`; `-s` carries `id = 153` + `object.serial = 251940`;
  `wd_no_nested` 0 Port objects.
- **ls⊋dump Metadata split.** `ls_ids` 9 vs `dump_ids` 4, extra
  `[35,37,38,41,42]`; `pw-cli info 35` rc 0 silent; `info all`
  described 85/91 with **0 Metadata described**. Reproduced 3/3 (A, B,
  my replay).
- **pactl index == serial.** 6 matched sinks (3 ALSA + `r84a_probe_548706`
  + `r87t_ns` + own `r88a_ns_<pid>`), **0 violations**, own index
  follows — 3/3 runs. `wd_state3` SUSPENDED/suspended/suspended.
- **pw-top traps.** `pt_n1` 1 frame, 12 rows, all `C`; `pt_n3` 3 frames
  `[C] → [I,S] → [I,S]` attempt 1 (own row `S` by independent spot);
  `pt_n0` 1 frame; `pt_nneg`/`pt_nabc` SIGKILL at 4.0 s with output;
  `pt_rbogus` rc 255 `Can't connect: Host is down`; four-witness
  agreement `suspended×4` idle and `running×4` under a `pw-play` load
  (`linked true`).

## 4. Findings

**F1 — `wd_dump_empty` false-FAILs under churn (fail-closed; reproduced).**
The arm (lines 28612–28629, verdict 28892–28900) requires the `pw-dump ''`
id-set to equal the c1 **or** c2 bracketing census *exactly*. My r88r2
replay failed it: census 97 objects vs `''` 98 ids, `equals_before/after`
false → rc 1 (the family's only non-green realization in 5 green-capable
runs). Deterministic reproduction (`spot-dumpempty-controlled`): control
iteration 98/98/98 pass; churn iteration (one seat-owned null sink
created between brackets, name-verified unloaded) c1 98 / `''` 105 /
c2 99, `eq_before=false, eq_after=false` → **arm false-fail**. A quiet
12-iteration bracket spot passes 12/12 (`delta 0`), so the *law* holds —
the arm is co-tenancy sensitive. **Verdict-changing? No — fail-closed**
(never a false green); but it makes the "2 green" claim load-dependent.
Same class as r87 F1 (load-sensitive false-FAIL). The author's boundary
V21 `'' == full dump` claim is not falsified (the `''` set is the full
dump at its instant, including transient objects).

**F2 — `bz_device` is a negative-only (vacuous) arm (fail-open;
evidence-only in this landing).** Lines 28148–28181 build `dev_recs`
from a regex over `busctl tree`; the verdict loop 28324–28329 only fails
when a device *advertises audio UUIDs*. With `devs == []` — or with a
failed `get-property UUIDs`, whose error-class string parses to
`uuid16 []` (28171–28173) — the entry **passes with zero
`coverage_blocked`**. Empirically re-derived by this seat
(`spot-device-absent.json`): fault-injecting the tree call to carry the
adapter but no `dev_*` path → `devices []`, **`failures []`**,
`coverage_blocked null`, teardown clean. The green receipts do contain
the real measurement (`bz_device.devices[0]` = DualSense, `uuid16
["1124","1200"]`, `audio_uuids []`), so the current green verdicts stand
— but the entry's headline "HID-only DualSense" witness is not armed
against a device-census regression.

**F3 — missing-leg skips without `coverage_blocked` (fail-open;
evidence-only).** `wd_setrule_foreign_id`/`_foreign_serial` are created
only `if foreign is not None` (28495–28500) and the verdict loop
`continue`s on an absent leg (28766–28773) — unlike the sibling `got is
None` arm, which *does* record coverage. `wd_dump_two` is likewise gated
by `if f_id` (28630–28634) and its verdict `if l and …` (28901–28905)
silently passes when absent. The receipts contain both real measurements
(`29→["29"]`; `pw-dump 153 29 → ["153"]`), so this is evidence-present-
but-unarmed; a foreign-node-less host would pass green while the
cross-object generalization is unmeasured.

**F4 — latent `IndexError` in the `wd_no_nested` verdict (fail-loud,
robustness).** If `pw-dump <own_id>` fails, `members` is `[]`
(28502–28507) while `port_objects` is 0 (no failure recorded), and the
mode verdict then indexes `members[0]` (28785–28790) → uncaught
`IndexError` aborts the run without a receipt. Not a false green (a
crash is loud), but a single transient `pw-dump` failure kills the whole
receipt. Also latent: `pt_state_active`'s `elif l.get("vocab")`
(29243) would silently pass on an empty vocab; unreachable without an
exception. (Labrat-flagged; code-confirmed here.)

**F5 — the family lock fails silently when it cannot open (evidence-only).**
`_btwit_r88_family_lock` (27968–27984) returns `None` on `OSError` and
`main()` proceeds unlocked with no `coverage_blocked`. Witnessed live:
the first cross-ROOT experiment ran with the alt-root `live/` directory
absent → `lock_path=NONE`, no lock, no record. In-lane the directory
always exists, so this is a nit — but it means "lock held" is not
self-evidencing.

**F6 — the 04:17 RED dev run is only partially disclosed (completeness).**
`corpus/live/runs/20261016T071710822152Z-btwit-r88/` is an untracked
**75-leg / 14-failure / 1-`coverage_blocked`** pre-correction run. The
author report cites only the two green runs and mentions "the dev run"
solely as the source of one leg's refusal-path variance (line 114). The
r87-scribe ADJ-1 class ("undisclosed RED dev runs") is therefore
partially open: the run exists, is not cited, and its failure surface is
not reported. Not verdict-changing (the committed revision's green
receipts are real), but the wave's citation discipline asks for it.

**F7 — cross-ROOT lock co-tenancy (residual, known class).** The
fixed-path lock is per-ROOT (`ROOT/live/measure_audio-btwit-r88.lock`).
Witnessed again this round: the r88 verifier replayed the same family
from its own frozen tree (`r88-verifier/tree/…`) **while** my frozen
tree ran the same probe — no serialization between the two (the worktree
lock still holds the author's pid/mtime 04:23 local). This is the
r86-F1/r87-F7 class, already queued; not new.

## 5. Frozen-tree replays and the serialization pair

### 5.1 Replays (all from `git archive c19bec96`, TMPDIR fixed)

| run | stamp (UTC) | pid | loadavg (1/5/15) | result |
| --- | --- | --- | --- | --- |
| r88r1 | `20261016T072815755760Z` | 1458207 | 75.54/79.75/79.77 | **green**, 79 legs, audit 106/106 |
| r88r2 | `20261016T072937176820Z` | 1481496 | 76.98/79.24/79.58 | **rc=1 — F1** (1 failure string) |
| r88r3 | `20261016T072952725402Z` | 1483465 | 75.60/78.84/79.45 | **green**, 79 legs, audit 106/106 |

### 5.2 Serialization pair (same ROOT, different TMPDIRs, real probes)

r88r2 start 07:29:19.26 → end 07:29:37.20 (17.9 s); r88r3 start
07:29:24.26 → end 07:29:52.75 (28.5 s total = **~12.9 s lock wait** +
15.6 s own work). Receipt stamps are strictly sequential
(07:29:37.177 < r88r3 work < 07:29:52.725) — **the lock serialized two
same-ROOT cross-TMPDIR probes end-to-end** (held to process exit).

### 5.3 Co-tenancy

The r88 verifier's `battery-v45.sh` tree replay was live in the same
window; my r88r1 recorded its objects as foreign witnesses
(`foreign_r88a_nodes: ['r88a_ns_1450101']` in btabs,
`['r88a_1450101_pt','r88a_ns_1450101']` in witdiff) and `host_is_quiet:
false` — exactly the designed witness-not-verdict behavior. My r88r2's
F1 failure occurred while that co-tenant churn was active; the quiet
12-iteration spot passes 12/12.

## 6. Lock

- **Path invariance:** `lockchild.py` under two TMPDIRs resolves both to
  `…/tree/corpus/live/measure_audio-btwit-r88.lock` (realpath via
  `/proc/self/fd`) — never `$TMPDIR`. Source: `ROOT/"live"/…` (27972).
- **Same-ROOT cross-TMPDIR:** holder locked at 0.357 s / released at
  3.359 s; second process (other TMPDIR, +0.4 s) locked at **2.969 s** —
  blocked, not raced. Real-probe pair §5.2 confirms end-to-end.
- **Cross-ROOT:** second process locks its own ROOT's lock immediately
  (0.343 s) while the first holds — **not serialized** (F7), as designed
  by the r84 F1 consensus (family-scoped, not global).
- **Open failure:** silent `None` (F5).

## 7. Hygiene

- `git status --short` at exit: only the pre-existing
  ` M corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`
  (mtime 04:22:52 local, before this seat) and `??` artifacts.
- Residue census after all work: `r88r_`/`r88a_` modules 0, sinks 0,
  nodes 0; no `pw-top`/`pw-play`/`measure_audio` processes; the
  accidentally-loaded churn sink was name-verified-unloaded mid-session
  (rc 0) and every subsequent load used the same name-verified pattern.
- Receipts: `corpus/live/r88-reviewer/` — pins (both blobs),
  `scripts/r88-landing.diff`, `r88r_surgery.py`, `r88r_audit.py`,
  `receipts/audit-summary.json`, `receipts/lock-*.txt`,
  `receipts/serialization.log`, `receipts/spot-*.json`,
  `runs/r88r{1,2,3}.*`, the frozen `tree/` (44 064 files) and
  `pins/__pycache__` (untracked, reviewer-side only).

## 8. Blockers and non-blocking notes

None blocking. Notes for the fold:

- **F1** is the actionable one: the `wd_dump_empty` arm should tolerate a
  bracketed churn delta (or retry brackets) in a later round — it is the
  only arm that can redden an otherwise-green run under co-tenancy.
- **F2/F3/F4/F5** are arm-quality/robustness items; the committed
  receipts contain the real measurements, so no green claim is
  unsupported today.
- **F6** is a citation-discipline item for the scribe/fold.
- The author's "both runs identical bytes" claim is not receipt-derivable
  (no fixture hash is recorded in the receipt); the receipts' leg sets
  and class names are consistent with the committed revision, and the
  committed blob itself is pinned and replayed byte-exact here.
- `pt_n3`'s frame count remains advisory by upstream design (attempt 1 in
  all runs; retry helper present).
- `wd_enum_fmt`/`num4`'s refusal path is bimodal (run A `remote res:-5`,
  B/my replays silent) and armed only on the no-pod signature — the
  author's disclosure matches the data exactly (only law-relevant
  run-to-run variance found in the normalized surface).
- Two pre-existing foreign null sinks (`r87t_ns`, `r84a_probe_548706`)
  are another round's residue; untouched.
- `bz_setcard_validctl` re-sets a real ALSA card's **current** profile
  (rc 0, idempotent) — the only foreign-object write, disclosed by the
  author as the positive control; no `set-default-*` anywhere.
