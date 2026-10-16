# labrat probe (read-only, depth-2) — r87-verifier dispatch, 2026-10-16 ~07:2xZ

Hypothesis: "the create_badfac / create_usage verdicts read only the
last-500-char window of the merged pw-cli session log".

## Seat report — labrat static probe

**Verdict: CONFIRMED** (by the committed source alone).

Evidence — frozen copy
`corpus/live/r87-verifier/tree/corpus/fixtures/measure_audio.py`:

Leg bodies (log capture), lines 26924–26937:
```
26924|            # ---------- create-node refusals ----------
26925|            for lname, cargs in (
26926|                    ("create_badfac",
26927|                     'create-node adapter { factory.name='
26928|                     '"no_such_r87_factory" }'),
26929|                    ("create_usage", 'create-node adapter { }')):
26930|                proc, chunks = _pwbind_r87_cli_open()
26931|                time.sleep(1.2)
26932|                _pwbind_r87_cli_send(proc, cargs)
26933|                time.sleep(1.6)
26934|                log = _pwbind_r87_cli_close(proc, chunks)
26935|                legs[lname] = {
26936|                    "log_tail": _pwbind_r87_norm(log)[-500:],
26937|                    "errors": _pwbind_r87_errors(log)}
```
The leg stores only `log_tail` = normalized log sliced `[-500:]`, plus
an `errors` list (local `Error: "..."` regexes over the full log — see
25629–25632). The full `log` string is not retained in the leg.

`log` source — `_pwbind_r87_cli_close`, lines 25733–25745:
```
25733|def _pwbind_r87_cli_close(proc, chunks, bound_s=8.0):
25734|    """Send `quit`, close stdin, bounded wait, return merged log."""
25735|    _pwbind_r87_cli_send(proc, "quit")
...
25745|    return b"".join(chunks).decode(errors="replace")
```
`chunks` are filled by a drain thread from the merged stdout/stderr pipe
of the held `pw-cli` session (25704–25721) — async registry events
interleave with the refusal text in one buffer.

Verdict expressions, lines 27121–27131:
```
27121|    bf = (legs.get("create_badfac") or {})
27122|    if "res:-2" not in (bf.get("log_tail") or ""):
27123|        failures.append(
27124|            f"create_badfac: no async res:-2 refusal "
27125|            f"({(bf.get('log_tail') or '')[-160:]})")
27126|    cu = (legs.get("create_usage") or {})
27127|    if "usage: factory.name=" not in (cu.get("log_tail") or "") and \
27128|            "res:-22" not in (cu.get("log_tail") or ""):
27129|            failures.append(
27130|            f"create_usage: no usage refusal "
27131|            f"({(cu.get('log_tail') or '')[-160:]})")
```

Redundancy check: the `"errors"` key recorded at line 26937 is never
consulted for these two legs in the verdict block; no other site checks
`res:-2` or `usage: factory.name=` against the full log — the tail-window
check is the sole arm.

Interpretation: both verdicts read only the last 500 normalized
characters of the merged session log. A printed refusal followed by
>~500 chars of trailing async registry-event text would push the refusal
out of the window and fail the arm. CONFIRMED.

sha256: UNREPORTED — this substrate exposes only read/grep/find_file_by_name
(no exec/hash tool); the labrat refused to fabricate a digest. The sha of
the file it read is
`be31da679be229074690dc5157edcc122612560594baa8ba62a9b5ce26dd9516`
(verified by the verifier seat itself).

Cleanup: read-only probe; no files modified, no processes spawned, no
scratch artifacts.
