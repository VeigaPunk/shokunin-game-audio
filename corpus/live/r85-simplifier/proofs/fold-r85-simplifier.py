#!/usr/bin/env python3
"""r85 simplifier FOLD — exact-match, single-occurrence replacements.

Input : proofs/base-measure_audio.py  (== 2a49d540:corpus/fixtures/measure_audio.py)
Output: proofs/folded/measure_audio.py + proofs/fold-apply.txt

Every replacement asserts EXACTLY ONE match in the base text; the fold aborts
on a 0- or multi-match (the r84 convention — this is how file-wide homographs
are caught and context-anchored).
"""
import re
import sys
from pathlib import Path

BASE = Path("proofs/base-measure_audio.py")
OUTD = Path("proofs/folded")
OUTD.mkdir(parents=True, exist_ok=True)
OUT = OUTD / "measure_audio.py"

src = BASE.read_text(encoding="utf-8")
log = []


def rep(label, old, new, delta):
    global src
    n = src.count(old)
    if n != 1:
        sys.exit(f"ABORT {label}: expected exactly 1 match, found {n}")
    src = src.replace(old, new, 1)
    log.append(f"{label}: matches=1 delta_lines={delta:+d}")


# ---------------------------------------------------------------- T1
rep("T1 PACTLMON_R85_STREAM_WAIT_S (unused constant)",
    "PACTLMON_R85_STREAM_WAIT_S = 8.0\n",
    "",
    -1)

# ---------------------------------------------------------------- T2
rep("T2 _pactlmon_r85_wait_node (zero-call helper)",
    'def _pactlmon_r85_wait_node(name, timeout_s=PACTLMON_R85_LINK_WAIT_S):\n'
    '    """Poll pw-dump until node.name == `name` exists."""\n'
    '    t0 = time.monotonic()\n'
    '    while time.monotonic() - t0 < timeout_s:\n'
    '        g = _pactlmon_r85_graph()\n'
    '        if _pactlmon_r85_node(g, name):\n'
    '            return True, round(time.monotonic() - t0, 3)\n'
    '        time.sleep(0.12)\n'
    '    return False, round(time.monotonic() - t0, 3)\n'
    '\n'
    '\n',
    "",
    -11)

# ---------------------------------------------------------------- T3
rep("T3a _pactlmon_r85_sd_leg signature (ctx dead param)",
    "def _pactlmon_r85_sd_leg(name, ctx, sd, client_argv, dur_s=2.6):",
    "def _pactlmon_r85_sd_leg(name, sd, client_argv, dur_s=2.6):",
    0)
rep("T3b sd_idle call site (ctx arg dropped)",
    '                legs["sd_idle"] = _pactlmon_r85_sd_leg(\n'
    '                    "sd_idle", ctx, PACTLMON_R85_SD,\n'
    '                    ["pw-record", "--version"], dur_s=3.6)',
    '                legs["sd_idle"] = _pactlmon_r85_sd_leg(\n'
    '                    "sd_idle", PACTLMON_R85_SD,\n'
    '                    ["pw-record", "--version"], dur_s=3.6)',
    0)
rep("T3c connect-leg call site (ctx arg dropped)",
    '                        legs[nm] = _pactlmon_r85_sd_leg(\n'
    '                            nm, ctx, PACTLMON_R85_SD, argv,\n'
    '                            dur_s=2.6)',
    '                        legs[nm] = _pactlmon_r85_sd_leg(\n'
    '                            nm, PACTLMON_R85_SD, argv,\n'
    '                            dur_s=2.6)',
    0)

# ---------------------------------------------------------------- T4
rep("T4a _pactlmon_r85_wait_tap_link signature (sink dead param)",
    "def _pactlmon_r85_wait_tap_link(sink, tap_tag,\n"
    "                                timeout_s=PACTLMON_R85_TAP_WAIT_S):",
    "def _pactlmon_r85_wait_tap_link(tap_tag,\n"
    "                                timeout_s=PACTLMON_R85_TAP_WAIT_S):",
    0)
rep("T4b wait_tap_link call site (sink arg dropped)",
    '    edges, waited = _pactlmon_r85_wait_tap_link(ctx["mix"],\n'
    '                                              f"{tag}_tap")',
    '    edges, waited = _pactlmon_r85_wait_tap_link(\n'
    '        f"{tag}_tap")',
    0)

# ---------------------------------------------------------------- T5
rep("T5a _pactlmon_r85_cap_leg `hit` dead store",
    '    err = proc.stderr.read().decode(errors="replace")\n'
    '    cls, hit = _pactlmon_r85_errclass(err)\n'
    '    leg.update({"samples": samples, "size_at_loss": size_at_loss,',
    '    err = proc.stderr.read().decode(errors="replace")\n'
    '    cls, _ = _pactlmon_r85_errclass(err)\n'
    '    leg.update({"samples": samples, "size_at_loss": size_at_loss,',
    0)
rep("T5b _pactlmon_r85_sd_leg `hit` dead store",
    '    err = proc.stderr.read().decode(errors="replace")\n'
    '    cls, hit = _pactlmon_r85_errclass(err)\n'
    '    leg.update({"exit_code": proc.returncode,',
    '    err = proc.stderr.read().decode(errors="replace")\n'
    '    cls, _ = _pactlmon_r85_errclass(err)\n'
    '    leg.update({"exit_code": proc.returncode,',
    0)

# ---------------------------------------------------------------- T6
rep("T6 addr entry `sers` dead store",
    '            sers = [s for s in\n'
    '                    entry["serial_cycles"]["serials"] if s is not None]\n',
    "",
    -2)

# ---------------------------------------------------------------- T7
rep("T7 capture entry `lp` dead store (t_prop_srcname)",
    '            lp = link_ports("t_prop_srcname")\n',
    "",
    -1)

# ---------------------------------------------------------------- T8
rep("T8 capture entry `want_node` dead loop payload",
    '            for nm, want_node in (("t_srcname", PACTLMON_R85_VSRC +\n'
    '                                   "b"),\n'
    '                                  ("t_srcserial", PACTLMON_R85_VSRC +\n'
    '                                   "b"),\n'
    '                                  ("t_srcid", PACTLMON_R85_VSRC +\n'
    '                                   "b")):',
    '            for nm in ("t_srcname", "t_srcserial", "t_srcid"):',
    -5)

# ---------------------------------------------------------------- T9
rep("T9a gsv closure signature (label dead param)",
    "                def gsv(arg, label):",
    "                def gsv(arg):",
    0)
GSV_SITES = [
    ('gsv(PACTLMON_R85_NS, "name")', 'gsv(PACTLMON_R85_NS)'),
    ('gsv(str(ser_a), "serial")', 'gsv(str(ser_a))'),
    ('gsv(str(oid_a), "object.id")', 'gsv(str(oid_a))'),
    ('gsv("@DEFAULT_SINK@", "defsink")', 'gsv("@DEFAULT_SINK@")'),
    ('gsv("@DEFAULT_SOURCE@", "defsrc")', 'gsv("@DEFAULT_SOURCE@")'),
    ('gsv("@DEFAULT_MONITOR@", "defmon")', 'gsv("@DEFAULT_MONITOR@")'),
    ('gsv(\n                    f"{PACTLMON_R85_NS}.monitor", '
     '"monitor_as_sink")',
     'gsv(\n                    f"{PACTLMON_R85_NS}.monitor")'),
    ('gsv(PACTLMON_R85_BOGUS, "bogus")', 'gsv(PACTLMON_R85_BOGUS)'),
    ('gsv("99999999", "huge")', 'gsv("99999999")'),
    ('gsv("-1", "neg")', 'gsv("-1")'),
    ('gsv("", "empty")', 'gsv("")'),
    ('gsv("0", "zero")', 'gsv("0")'),
    ('gsv(f" {ser_a}", "leadspace")', 'gsv(f" {ser_a}")'),
    ('gsv(f"+{ser_a}", "plus")', 'gsv(f"+{ser_a}")'),
    ('gsv(f"{ser_a}.0", "float")', 'gsv(f"{ser_a}.0")'),
    ('gsv(f"{ser_a}x", "xsuf")', 'gsv(f"{ser_a}x")'),
    ('gsv(f"0x{ser_a:X}", "hex")', 'gsv(f"0x{ser_a:X}")'),
    ('gsv(f"{s[:-3]}_{s[-3:]}", "uscr")', 'gsv(f"{s[:-3]}_{s[-3:]}")'),
    ('gsv(f"0{s}", "lead0")', 'gsv(f"0{s}")'),
    ('gsv("@DEFAULT_SINK@X", "defsinkX")', 'gsv("@DEFAULT_SINK@X")'),
]
for i, (o, n) in enumerate(GSV_SITES, 1):
    rep(f"T9-{i:02d} gsv call site label dropped", o, n, 0)

# ---------------------------------------------------------------- T10
rep("T10a teardown (loads or {}) + leaf guard",
    '    for tag, leaf in (loads or {}).items():\n'
    '        leaf = leaf or {}\n'
    '        entry.setdefault("unloads", {})[tag] = \\\n'
    '            _pactlmon_r85_unload_own(\n'
    '                leaf.get("module_id"),\n'
    '                leaf.get("field", "sink_name"),\n'
    '                leaf.get("value", tag))\n'
    '    sinks_now = _capture_r77_sink_names_strict()',
    '    for tag, leaf in loads.items():\n'
    '        entry.setdefault("unloads", {})[tag] = \\\n'
    '            _pactlmon_r85_unload_own(\n'
    '                leaf.get("module_id"),\n'
    '                leaf.get("field", "sink_name"),\n'
    '                leaf.get("value", tag))\n'
    '    sinks_now = _capture_r77_sink_names_strict()',
    -1)
rep("T10b teardown sink_names comprehension guards",
    '        sink_names = [t for t, l in (loads or {}).items()\n'
    '                      if (l or {}).get("field", "sink_name") ==\n'
    '                      "sink_name"]',
    '        sink_names = [t for t, l in loads.items()\n'
    '                      if l.get("field", "sink_name") ==\n'
    '                      "sink_name"]',
    0)
rep("T10c teardown src_names comprehension guards",
    '        src_names = [t for t, l in (loads or {}).items()\n'
    '                     if (l or {}).get("field") == "source_name"]',
    '        src_names = [t for t, l in loads.items()\n'
    '                     if l.get("field") == "source_name"]',
    0)
rep("T10d teardown own_nodes_after membership guard",
    '                      if PACTLMON_R85_PREFIX in n\n'
    '                      or n in (loads or {}))',
    '                      if PACTLMON_R85_PREFIX in n\n'
    '                      or n in loads)',
    0)

# ---------------------------------------------------------------- T11
rep("T11 block `leaf = leaf or {}` (loads guard kept — live)",
    '    entry.setdefault("coverage_blocked", []).append(msg)\n'
    '    for tag, leaf in (loads or {}).items():\n'
    '        leaf = leaf or {}\n'
    '        entry.setdefault("unloads", {})[tag] = \\',
    '    entry.setdefault("coverage_blocked", []).append(msg)\n'
    '    for tag, leaf in (loads or {}).items():\n'
    '        entry.setdefault("unloads", {})[tag] = \\',
    -1)

# ---------------------------------------------------------------- T12
rep("T12a mv_name subsumed (a1 or {})",
    'f"mv_name: sink={(a1 or {}).get(\'sink\')} != "',
    'f"mv_name: sink={a1.get(\'sink\')} != "',
    0)
rep("T12b mv_serial subsumed (a2 or {})",
    'f"mv_serial: sink={(a2 or {}).get(\'sink\')} "',
    'f"mv_serial: sink={a2.get(\'sink\')} "',
    0)
rep("T12c mv_bogus subsumed (a2 or {})",
    '                        (l3.get("after") or {}).get("sink") != \\\n'
    '                        (a2 or {}).get("sink"):',
    '                        (l3.get("after") or {}).get("sink") != \\\n'
    '                        a2.get("sink"):',
    0)
rep("T12d cdup_move subsumed (a4 or {})",
    'f"cdup_move: sink={(a4 or {}).get(\'sink\')}"',
    'f"cdup_move: sink={a4.get(\'sink\')}"',
    0)

# ---------------------------------------------------------------- T13
rep("T13 _pactlmon_r85_vol_pct (rec or {})",
    '    m = re.search(r"(\\d+)\\s*%", (rec or {}).get("stdout") or "")',
    '    m = re.search(r"(\\d+)\\s*%", rec.get("stdout") or "")',
    0)

# ---------------------------------------------------------------- T14
rep("T14 capture feeder pre-ladder guard (dead conjunct)",
    '                # sink (only silence may ever land there).\n'
    '                if feeder is not None and feeder.poll() is None:',
    '                # sink (only silence may ever land there).\n'
    '                if feeder.poll() is None:',
    0)

OUT.write_text(src, encoding="utf-8")
log.append(f"base={BASE} bytes={BASE.stat().st_size}")
log.append(f"folded={OUT} bytes={OUT.stat().st_size}")
Path("proofs/fold-apply.txt").write_text("\n".join(log) + "\n",
                                         encoding="utf-8")
print("\n".join(log))
