# labrat probe — BLOCKED (substrate), no evidence produced

Seat: `ufo-labrat` (depth-2, read-only, advisory), dispatched by the audio r77
BOUNDARY executor as its single permitted probe. Recorded here verbatim-in-
substance because the operator sees only the parent seat's report.

**Hypothesis assigned:** "arecord's split/rotation filename counter is unbounded
— `%s-01.%s` first, `%s-%02i.%s` thereafter, widening past `-99`; the `-m`
rotation shares that template with the 2 GiB `0x80000000` split."

**Outcome: UNTESTED — neither falsified nor survived. No measured evidence.**

The labrat's substrate exposes **no exec/shell tool** (only `find_file_by_name`,
`grep`, `read`), so none of the prescribed commands (`strings`, `timeout arecord
-D null …`, python header reads) could be executed. It wrote no receipt: it has
no write capability either. Zero scratch created, no tracked file touched.

Two claims from its report, with the parent seat's correction:

| labrat claim | parent seat's direct check |
| --- | --- |
| "`/usr/bin/arecord` does not exist on this host" (`find_file_by_name` → only `arecordmidi`) | **wrong** — `command -v arecord` → `/usr/bin/arecord`; `arecord --version` → `1.2.16`. The labrat's file-finder is sandboxed away from `/usr`, so its negative is an artefact of the tool scope, not a host fact. |
| advisory inference: `aplay.c` uses `"%s-01.%s"` then `"%s-%02i.%s"` with an unbounded `int` counter, and `new_file()` serves both the `-m` rotation and the 2 GiB `MAX_FILE_SIZE` split | **agrees with the strings evidence** (`/usr/bin/arecord`: `%s-01.%s`, `%s-%02i.%s`, one occurrence each) and with the measured `split-01..-04` sequence. Still **unmeasured past `-07`** — see the parent report §4.1 and §10. |

**Named class:** `labrat_substrate_no_exec` — a delegated probe that cannot run
commands cannot produce empirical evidence, and its negative existence checks
must not be read as host facts. The parent seat ran the probe itself
(`p6_sentinel.py`, `p7p8_bigwav_counter.py`).
