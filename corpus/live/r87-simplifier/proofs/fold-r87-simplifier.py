#!/usr/bin/env python3
"""r87 simplifier fold — 12 exact-string edits, each asserted to match
EXACTLY ONCE inside the r87 family region of the pinned d1e687b9 blob.

Region = the r87 family block (the header comment at its first line
through the end of the r87 dispatch block in main()).  Homograph edits
(`(loads or {})` / `leaf = leaf or {}` also exist in the r86/r85/r84
families) are applied region-scoped so every prior family stays
byte-identical.

Usage: fold-r87-simplifier.py <base.py> <out.py>
"""
import sys
import pathlib

BASE = pathlib.Path(sys.argv[1])
OUT = pathlib.Path(sys.argv[2])

src = BASE.read_text()
lines = src.splitlines(keepends=True)

# ---- locate the r87 family region (line numbers, 1-based) ----
# region = [header-comment first line .. last line of the r87 dispatch
# block] i.e. everything up to (not incl.) the r85 dispatch block, which
# is the next sibling `if args.` block after the r87 one.
start = None
end = None
for i, ln in enumerate(lines, 1):
    if ln.startswith("# r87: the DEVICE-BINDING lattice"):
        start = i
    if start is not None and ln.startswith("    if args.probe_pactlmon_r85:"):
        end = i - 1          # last line of the r87 dispatch block
        break
if start is None or end is None:
    raise SystemExit("ABORT: r87 region not located")

region = "".join(lines[start - 1:end])
head = "".join(lines[:start - 1])
tail = "".join(lines[end:])

EDITS = [
    # T1/T2 — the two dead wait constants (r86 T1/T2 shape)
    ("PWBIND_R87_LINK_WAIT_S = 5.0\n", ""),
    ("PWBIND_R87_TAP_WAIT_S = 6.0\n", ""),
    # T3 — teardown: loads is a required positional that is always a dict
    # (anchored on the teardown-only trailing `g = _pwbind_r87_graph()`
    # line — the block twin is textually identical otherwise)
    ("    for tag, leaf in (loads or {}).items():\n        leaf = leaf or {}\n"
     "        entry.setdefault(\"unloads\", {})[tag] = \\\n"
     "            _pactlmon_r85_unload_own(\n"
     "                leaf.get(\"module_id\"),\n"
     "                leaf.get(\"field\", \"sink_name\"),\n"
     "                leaf.get(\"value\", tag))\n"
     "    g = _pwbind_r87_graph()\n",
     "    for tag, leaf in loads.items():\n"
     "        entry.setdefault(\"unloads\", {})[tag] = \\\n"
     "            _pactlmon_r85_unload_own(\n"
     "                leaf.get(\"module_id\"),\n"
     "                leaf.get(\"field\", \"sink_name\"),\n"
     "                leaf.get(\"value\", tag))\n"
     "    g = _pwbind_r87_graph()\n"),
    ("        gone = {nm: nm not in sinks_now for nm in (loads or {})}\n",
     "        gone = {nm: nm not in sinks_now for nm in loads}\n"),
    ("                      or n in (loads or {}))\n",
     "                      or n in loads)\n"),
    # T4 — block: the `loads` guard is LIVE (default None, 4/9 call
    # sites omit it); only the leaf guard is dead (anchored on the
    # block-only preceding coverage_blocked append).
    ("    entry.setdefault(\"coverage_blocked\", []).append(msg)\n"
     "    for tag, leaf in (loads or {}).items():\n        leaf = leaf or {}\n",
     "    entry.setdefault(\"coverage_blocked\", []).append(msg)\n"
     "    for tag, leaf in (loads or {}).items():\n"),
    # T5 — cli dsp: the None init of solo_hi is overwritten before any
    # read (r86 T8 shape)
    ("                solo_lo, solo_hi = mark(), None\n",
     "                solo_lo = mark()\n"),
    # T6 — cli fmt_sink: nid is guaranteed non-None (early block-return
    # at `if nid is None`), so the guard is always true -> dedent.
    ("            fs = {}\n"
     "            if nid is not None:\n"
     "                fs[\"pre\"] = _pwbind_r87_pwcli(\n"
     "                    \"enum-params\", nid, \"Format\", timeout_s=10.0,\n"
     "                                           keep_chars=4000)\n"
     "                fs[\"write_valid\"] = _pwbind_r87_pwcli(\n"
     "                    \"set-param\", nid, \"Format\",\n"
     "                    \"{ mediaType: 1, mediaSubtype: 1, format: 259, \"\n"
     "                    \"rate: 44100, channels: 2 }\", timeout_s=10.0)\n"
     "                fs[\"post_valid\"] = _pwbind_r87_pwcli(\n"
     "                    \"enum-params\", nid, \"Format\", timeout_s=10.0,\n"
     "                                           keep_chars=4000)\n"
     "            legs[\"fmt_sink\"] = fs\n",
     "            fs = {}\n"
     "            fs[\"pre\"] = _pwbind_r87_pwcli(\n"
     "                \"enum-params\", nid, \"Format\", timeout_s=10.0,\n"
     "                                       keep_chars=4000)\n"
     "            fs[\"write_valid\"] = _pwbind_r87_pwcli(\n"
     "                \"set-param\", nid, \"Format\",\n"
     "                \"{ mediaType: 1, mediaSubtype: 1, format: 259, \"\n"
     "                \"rate: 44100, channels: 2 }\", timeout_s=10.0)\n"
     "            fs[\"post_valid\"] = _pwbind_r87_pwcli(\n"
     "                \"enum-params\", nid, \"Format\", timeout_s=10.0,\n"
     "                                       keep_chars=4000)\n"
     "            legs[\"fmt_sink\"] = fs\n"),
    # T7 — target: the "<unreadable-default>" fallback is unreachable
    # (a falsy DEF0 block-returns before any verdict)
    ("    DEF = entry.get(\"default_sink_at_start\") or \"<unreadable-default>\"\n",
     "    DEF = entry[\"default_sink_at_start\"]\n"),
    # T8 — cold_nowarm: the id-specific term is subsumed by the generic
    # "unknown global" term (the id form CONTAINS the generic form)
    ("    if f\"unknown global '{nid}'\" not in blob and \\\n"
     "            \"unknown global\" not in blob:\n",
     "    if \"unknown global\" not in blob:\n"),
    # T9 — p_coll port check: `coll_ports and` is subsumed — `all([])`
    # is True, so on an empty list the unguarded predicate is False too
    ("    if coll_ports and not all(str(p).startswith(\"playback_\")\n"
     "                              for p in coll_ports):\n",
     "    if not all(str(p).startswith(\"playback_\") for p in coll_ports):\n"),
]

applied = []
work = region
for old, new in EDITS:
    n = work.count(old)
    if n != 1:
        raise SystemExit(f"ABORT: pattern matched {n} times (want 1):\n{old!r}")
    work = work.replace(old, new, 1)
    applied.append(old.splitlines()[0][:78])

# sanity: the folded region must not contain the removed forms anymore
for probe in ("PWBIND_R87_LINK_WAIT_S", "PWBIND_R87_TAP_WAIT_S"):
    if probe in work:
        raise SystemExit(f"ABORT: {probe} still present")

OUT.write_text(head + work + tail)
print(f"region lines {start}-{end} of {len(lines)}; edits applied: {len(applied)}")
for a in applied:
    print("  ", a)
