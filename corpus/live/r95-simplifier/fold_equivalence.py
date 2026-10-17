#!/usr/bin/env python3
"""r95 SIMPLIFIER — fold-equivalence tables (scratch only, daemon-free).

For each queued fold, the OLD and NEW shapes are executed side by side on
the fold's whole reachable input domain and their observables compared
(failures list + entry dict + returned values).  Anything that cannot be
decided this way is declared as such rather than assumed.

Writes fold-equivalence.json next to this file.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = {}

# ---------------------------------------------------------------- F3
# OLD:  if dst != conns_want[0] if conns_want else False:
# NEW:  if conns_want and dst != conns_want[0]:
def old_f3(dst, conns_want):
    return bool(dst != conns_want[0] if conns_want else False)


def new_f3(dst, conns_want):
    return bool(conns_want and dst != conns_want[0])


f3_rows = []
for dst, cw in (("A:playback_MONO", []),
                ("A:playback_0", ["A:playback_MONO"]),
                ("A:playback_MONO", ["A:playback_MONO"]),
                ("", ["A:playback_MONO"]),
                ("A:playback_0", [])):
    o, n = old_f3(dst, cw), new_f3(dst, cw)
    f3_rows.append({"dst": dst, "conns_want": cw, "old": o, "new": n,
                    "equal": o == n})
OUT["F3_conditional"] = {"rows": f3_rows,
                         "all_equal": all(r["equal"] for r in f3_rows)}
# the four arms the entry actually reaches (arms table of jack_addr_r95_entry)
arms = (("x_rendered", "r95a_ds:playback_MONO", ["r95a_ds:playback_MONO"]),
        ("x_native", "r95a_ns:playback_MONO", []),
        ("x_fillalias", "r95a_ns:playback_0", ["r95a_ds:playback_MONO"]),
        ("x_corner", "r95a_corner:playback_MONO",
         ["r95a_corner:playback_MONO"]))
OUT["F3_real_arms"] = [
    {"arm": a, "old_alias_addressed": old_f3(d, c),
     "new_alias_addressed": new_f3(d, c)} for a, d, c in arms]

# ---------------------------------------------------------------- F4
# OLD: two tests of killed_at_bound (if/else then `if not ...`)
# NEW: one if/else
LAWS = ("rc", "stall_cycles", "cb", "xrun_cbs")


def old_f4(killed):
    failures, blocked = [], []
    if killed:
        blocked.append("d_xrun_stall: killed at the bound (unjudged)")
    else:
        failures.append("rc")
    if not killed:
        failures.extend(["stall_cycles", "cb", "xrun_cbs"])
    return failures, blocked


def new_f4(killed):
    failures, blocked = [], []
    if killed:
        blocked.append("d_xrun_stall: killed at the bound (unjudged)")
    else:
        failures.append("rc")
        failures.extend(["stall_cycles", "cb", "xrun_cbs"])
    return failures, blocked


f4_rows = []
for killed in (True, False):
    o, n = old_f4(killed), new_f4(killed)
    f4_rows.append({"killed_at_bound": killed, "old": o, "new": n,
                    "equal": o == n})
OUT["F4_double_killed_test"] = {"rows": f4_rows,
                                "all_equal": all(r["equal"] for r in f4_rows)}

# ---------------------------------------------------------------- F2
# the two driver-sink unload blocks: identical modulo the failure label
import re  # noqa: E402
src = (HERE.parents[2] / "corpus" / "fixtures" /
       "measure_audio.py").read_text().split("\n")
blk_a = src[34171:34182]          # 34172..34182 (surface entry, label s_shape)
blk_b = src[34461:34472]          # 34462..34472 (bytes entry, label b_jack2pw)
norm = lambda lines: [re.sub(r'"(s_shape|b_jack2pw): ', '"<label>: ', l.strip())
                      for l in lines]
OUT["F2_unload_blocks"] = {
    "a": norm(blk_a), "b": norm(blk_b),
    "identical_modulo_label": norm(blk_a) == norm(blk_b),
    "shared_lines": len(norm(blk_a)),
}

# ---------------------------------------------------------------- F5
# row_count: any reader anywhere in the module?
import ast  # noqa: E402
tree = ast.parse("\n".join(src))
readers = []
for node in ast.walk(tree):
    if isinstance(node, ast.Subscript) and isinstance(node.ctx, ast.Load):
        v = node.value
        if isinstance(v, ast.Name) and v.id == "rec" and \
                isinstance(node.slice, ast.Constant) and \
                node.slice.value == "row_count":
            readers.append(node.lineno)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
            and node.func.attr == "get" and node.args and \
            isinstance(node.args[0], ast.Constant) and \
            node.args[0].value == "row_count":
        readers.append(node.lineno)
OUT["F5_row_count"] = {"writer_lines": [33667], "reader_lines": readers,
                       "has_reader": bool(readers)}

(HERE / "fold-equivalence.json").write_text(
    json.dumps(OUT, indent=2, sort_keys=True) + "\n")
print(json.dumps(OUT, indent=2, sort_keys=True))
