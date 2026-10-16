# r88-verifier — labrat (read-only) static probe, verbatim seat output

Dispatched exactly one `ufo-labrat` (frozen probeParent duty), bounded
depth-2, read-only, agent `0789feda`, hypothesis = "no r88 arm's verdict
can be flipped by a last-N-char session-log window or a keep_chars-
truncated capture". It ran no commands against the live host and mutated
nothing; its line numbers and arm table are its own static reading of the
committed fixture. Its one *executable* claim (the `pt_nneg`/`pt_nabc`
empty-capture corner) was independently measured by this seat in
`runs/infinite_flush.py` (see the verifier report §6.1: 1/10 empty
captures at a 3 s bound, 0/10 at the shipped 4 s bound).

---

## Seat output — labrat static probe

**Hypothesis:** "No r88 arm's verdict can be flipped by (a) a last-N-char window over a long-lived session log, or (b) a truncated (`keep_chars`-bounded) capture of a one-shot command whose output can be polluted by foreign churn."

**Method:** read-only line inspection of lines 27507–29255 and all r88 helper parsers (27762–28096). No probe executed; no files mutated.

### Key structural fact (measured, not inferred)

`_btwit_r88_run` (27659) computes `error_class`/`error_hit` on the **full untruncated** `errt + "\n" + outt` at line 27686, **before** `[:keep_chars]` is applied at 27693/27696. Every arm keyed on `exit_code`/`error_class`/`stdout_bytes` is therefore truncation-immune by construction. Truncation is head-keeping (`[:N]`), never tail (`[-N:]`). **No `[-N:]` window over a session log exists anywhere in the r88 block — part (a) is absent.**

### `failures.append` arm table

**`btabs_bluez_r88_entry` (28099–28423)** — plus teardown appends at 28049, 28064 (shared helper, parsed readers):

| Line | Leg | Text source | Truncation-flippable? |
|---|---|---|---|
| 28273 | bz_nullsink_ctl | (iii) parsed rc/module_id | no |
| 28278, 28282, 28298 | bz_cards / bz_sinks | (iii) `pactl … short` full readers | no |
| 28288, 28292 | bz_pactl_lines | (iii) dedicated full-stream grep (27730) | no |
| 28301, 28306 | bz_midi_bridge | (iii) full pw-dump census | no |
| 28311 | bz_tree adapters | **(ii) `tree["stdout"]`, keep=2400** | `/org/bluez/hci0` sits at byte ~0–60 of `busctl tree org.bluez` → effectively no |
| 28316 | bz_adapter Powered | (ii) stdout, 2400; answer is `"b true"` ~6 B | no |
| 28322 | bz_media1 UUIDs | (ii) stdout, 2400; UUID list ~200 B | no |
| 28326 | bz_device audio UUIDs | (iii) per-prop get-property; **but `devs` enumerated from truncated tree stdout (28148)** | one-directional: truncation can only *drop* dev paths → under-coverage, never a false FAIL |
| 28331 | bz_media_transport | **(ii) findall on truncated tree stdout** | same: can only hide objects → false-PASS direction only |
| 28340 (5 legs), 28347, 28357, 28367 | refusal battery | error_class/exit_code (full text) | no |
| 28376 | bz_mods bluez_modules | (iii) full `pactl list modules short` | no |
| 28381, 28387 | bz_spa_inventory | os.listdir | no |
| 28393, 28397 | bz_spa_codecs_str | in-process `strings` filter, untruncated | no |
| 28401 | bz_find_module | (ii) `find["stdout"]`, **keep=900** | hits are ~60–100 B paths; output >900 B still leaves hits in head → cannot produce empty | no |
| 28413 (4 legs) | fabrication refusals | `"can't create node"` in truncated stderr+stdout (2400); pw-cli refusal text ~80 B at offset 0 | no |
| 28418 | bz_own_residue | (iii) parsed graph | no |

**`witdiff_dump_r88_entry` (28426–29007)**

| Lines | Leg | Source | Flippable? |
|---|---|---|---|
| 28775 (4 legs) | wd_setrule_* | (iii) parsed full pw-dump JSON; recensus-on-mismatch | no |
| 28781, 28788 | wd_no_nested, wd_mode_* | (iii) parsed | no |
| 28796 | wd_mode_spa | **(i) `stdout_raw` preferred** (`keep_raw=True`, 28515) | no |
| 28801 | wd_cli_id | **(ii) `l["stdout"]`, keep=2400** — needs `"PipeWire:Interface:Node"` (byte ~30, header) **and** `BTWIT_R88_NS` inside the props block. A null-sink prop block is ~1.5–2 KB and `node.name` ordering is implementation-dependent — the needed substring *can* sit near the 2400 B bound | **low but real** (see below) |
| 28810 | wd_cli_serial/dead/enum | rc + error_class + stdout emptiness; truncation cannot empty a nonempty capture | no |
| 28818 | wd_ls_serial | (i) `stdout_raw` preferred | no |
| 28823–28870 | wd_propblock / keyset / types / params | all parsed from `stdout_raw` (`keep_raw=True` on every feeder leg) | no |
| 28879, 28889, 28933, 28980 | silent-class arms (dump_id/abc/huge, cli_meta, meta_extra, dead_serial; keep=300) | emptiness + rc only | no |
| 28894, 28898, 28903 | wd_dump_empty / wd_dump_two | separate **full** `subprocess.run` JSON parse (28617, 28631) | no |
| 28909 | wd_dump_color | has_ansi/json_parses on full runs (28639–49) | no |
| 28916 | wd_dump_neg | error_class | no |
| 28923 | wd_ls_metadata | ls_ids parsed from `stdout_raw` (28653) | no |
| 28938 | wd_info_all | ids regex on `stdout_raw` (28671) | no |
| 28949 | wd_enum_fmt/num4 | `"Object:" in stdout` (2400); if a pod exists it begins at byte ~0 | no |
| 28960 | wd_enum_num2 | compares **truncated** normed t1 vs t2 (2400 each) — but identical inputs truncate identically, so truncation can only mask a divergence (false-PASS), never create one | no false-FAIL |
| 28966 | wd_enum_bogus | error_class | no |
| 28988 | wd_serial_law | (iii) pactl short + graph | no |
| 29001 | wd_state3 | cli state regex on `stdout_raw` (28752) | no |

**`pwtop_r88_entry` (29010–29252)**

| Lines | Leg | Source | Flippable? |
|---|---|---|---|
| 29170 | pt_n1 | frames parsed from `stdout_raw` (keep_raw, 29044) | no |
| 29182–29196 | pt_n3 | `_frames_cache` parsed from `stdout_raw` inside `_btwit_r88_top_until` (27872) | no |
| 29205 | pt_n0 | `stdout_raw` | no |
| **29211** | **pt_nneg / pt_nabc** | **`_btwit_r88_top_frames(l.get("stdout"))` — the truncated capture, keep=200, and `keep_raw` is NOT set on these legs (29051–56)** | **yes — see below** |
| 29217 | pt_rbogus | error_class | no |
| 29231, 29247 | pt_state_idle/active | parsed vocab; top rows from raw frames | no |

### Fragile arms

1. **`pt_nneg`/`pt_nabc` (29207–29213)** — the one arm that arms a *truncated* capture for content. It requires `killed_at_bound` **and** ≥1 parseable frame in the **first 200 bytes** of stdout from a SIGKILLed streaming process. Since `pw-top` writes to a pipe (block-buffered, not a tty), it is legitimate for a `-n -1` run to be killed at `BTWIT_R88_PWT_BOUND_S` with **zero flushed stdout bytes** → `fr == []` → false FAIL of a correct infinite class. Not the r87-F1 tail-window shape, but a real capture-content assumption with a flip path. (Head-truncation itself is safe — a frame header would be at byte ~0 — but the *empty-capture* case is not distinguished from "infinite class broken.")

2. **`wd_cli_id` (28798–28803)** — reads truncated `l["stdout"]` (2400 B) despite `keep_raw=True` being set on this leg; needs `BTWIT_R88_NS` inside the prop block. If the own node's prop block orders `node.name` past byte 2400, a true positive becomes a false FAIL. Low probability (null-sink props typically fit), but the raw channel exists and is bypassed — an unforced class-(b) exposure.

3. **Coverage-narrowing only (false-PASS direction, cannot flip a PASS→FAIL):** `bz_tree` dev/MediaTransport enumeration and `devs` list (28148–28152, 28183) run on 2400-truncated `busctl tree` output; on a host with many paired devices, tail objects are silently dropped → `bz_device`/`bz_media_transport` arms judge a subset. `wd_enum_num2` truncation is self-masking.

### Verdict

**CONFIRMED for the r87-F1 class as stated**, with one caveat: part (a) — no last-N-char window over a session log exists; every long/multi-frame read is a full `stdout_raw` parse (deliberate design: `keep_raw=True` on every frame/ls/info leg the verdicts consume). Part (b) — no arm can be flipped by *foreign churn* in a truncated capture, because error classes are computed pre-truncation and emptiness checks are truncation-stable. The hypothesis survives in spirit, but **the literal claim "no r88 arm's verdict can be flipped by a truncated capture" is falsified in the corner**: `pt_nneg`/`pt_nabc` (keep=200, no raw fallback, requires a nonzero frame in captured head of a kill-bound buffered stream) and `wd_cli_id` (reads `stdout` when `stdout_raw` is available) retain residual flip paths — neither is the r87 shape, and only `pt_nneg/pt_nabc` has a plausible false-FAIL mechanism.

**Cleanup:** nothing created or modified; read-only throughout.
