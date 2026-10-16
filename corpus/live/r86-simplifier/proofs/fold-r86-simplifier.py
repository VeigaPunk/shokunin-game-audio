#!/usr/bin/env python3
"""r86-simplifier fold: exact-match, abort on 0- or multi-match.
Input:  base-measure_audio.py (fa5994a0-pinned blob, 26655 lines)
Output: folded/measure_audio.py

The two guard lines that also exist in the r83/r84 families
(`gone = {...}`, `or n in (loads or {})`) are folded inside their
FUNCTION REGION only, so the r83/r84 copies stay byte-identical."""
import hashlib
import sys
from pathlib import Path

BASE = Path("base-measure_audio.py")
OUT = Path("folded/measure_audio.py")

src = BASE.read_text(encoding="utf-8")
folded = src
applied = []


def replace_region(text, start_marker, end_marker, old, new, tag):
    a = text.index(start_marker)
    b = text.index(end_marker, a)
    region = text[a:b]
    n = region.count(old)
    if n != 1:
        sys.exit(f"{tag}: region match count {n} != 1 — ABORT")
    text = text[:a] + region.replace(old, new) + text[b:]
    applied.append(tag)
    return text


# ---- region: _pwctl_r86_teardown (T4) ------------------------------------
folded = replace_region(
    folded,
    "def _pwctl_r86_teardown(entry, failures, loads, meta_subject=False):",
    "def _pwctl_r86_block(entry, failures, msg, loads=None):",
    '    in the default store."""\n'
    "    for tag, leaf in (loads or {}).items():\n"
    "        leaf = leaf or {}\n",
    '    in the default store."""\n'
    "    for tag, leaf in loads.items():\n",
    "T4a teardown load-loop guard")
folded = replace_region(
    folded,
    "def _pwctl_r86_teardown(entry, failures, loads, meta_subject=False):",
    "def _pwctl_r86_block(entry, failures, msg, loads=None):",
    "        gone = {nm: nm not in sinks_now for nm in (loads or {})}\n",
    "        gone = {nm: nm not in sinks_now for nm in loads}\n",
    "T4b teardown sinks_gone guard")
folded = replace_region(
    folded,
    "def _pwctl_r86_teardown(entry, failures, loads, meta_subject=False):",
    "def _pwctl_r86_block(entry, failures, msg, loads=None):",
    "                      or n in (loads or {}))\n",
    "                      or n in loads)\n",
    "T4c teardown own_nodes guard")

# ---- region: _pwctl_r86_block (T5) ---------------------------------------
folded = replace_region(
    folded,
    "def _pwctl_r86_block(entry, failures, msg, loads=None):",
    "def _pwctl_r86_load_ns():",
    '    entry.setdefault("coverage_blocked", []).append(msg)\n'
    "    for tag, leaf in (loads or {}).items():\n"
    "        leaf = leaf or {}\n",
    '    entry.setdefault("coverage_blocked", []).append(msg)\n'
    "    for tag, leaf in (loads or {}).items():\n",
    "T5 block leaf guard")

# ---- globally unique edits ----------------------------------------------
EDITS = [
    # T1 — dead constant (never referenced)
    ("PWCTL_R86_LINK_WAIT_S = 5.0\n", ""),
    # T2 — dead constant (never referenced)
    ("PWCTL_R86_TAP_WAIT_S = 6.0\n", ""),
    # T3 — self_serials accumulator: three write sites, value never read
    ("        self_serials = []\n", ""),
    ('                self_serials.append({s for s in\n'
     '                                     legs[f"dump_full{rep}"]\n'
     '                                     ["self_serials"]})\n', ""),
    ("                self_serials.append(set())\n", ""),
    # T6 — own_links subsumed guards (out/in are f-strings from
    # _pwctl_r86_links: always non-empty str)
    ('    return [l for l in links\n'
     '            if (l["out"] or "").startswith(sink + ":")\n'
     '            or (l["in"] or "").startswith(sink + ":")]\n',
     '    return [l for l in links\n'
     '            if l["out"].startswith(sink + ":")\n'
     '            or l["in"].startswith(sink + ":")]\n'),
    # T7 — unreachable verdict: the `if not edges:` early return above
    # makes legs["tap_link"]["edges"] always truthy after the finally
    ('    # ---------------- verdicts ----------------\n'
     '    if not legs["tap_link"]["edges"]:\n'
     '        failures.append("tap_link: the monitor tap never '
     'validated")\n',
     "    # ---------------- verdicts ----------------\n"),
    # T8 — solo_hi dead None init (overwritten before any read)
    ("                solo_lo, solo_hi = mark(), None\n",
     "                solo_lo = mark()\n"),
    # T9 — dead None member: ser is str(...) on every path
    ('        if nid is None or ser in (None, "None"):\n',
     '        if nid is None or ser == "None":\n'),
]

for i, (old, new) in enumerate(EDITS, 1):
    n = folded.count(old)
    if n != 1:
        sys.exit(f"EDIT {i}: global match count {n} != 1 — ABORT")
    folded = folded.replace(old, new)
    applied.append(f"E{i}")

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(folded, encoding="utf-8")

print(f"edits applied: {len(applied)} -> {applied}")
print(f"base   sha256 {hashlib.sha256(src.encode()).hexdigest()} "
      f"lines={src.count(chr(10))}")
print(f"folded sha256 {hashlib.sha256(folded.encode()).hexdigest()} "
      f"lines={folded.count(chr(10))}")
print(f"net line delta: {folded.count(chr(10)) - src.count(chr(10))}")
