#!/usr/bin/env python3
"""r85-scribe: either-way pinning harness for the three host-bimodal arms.

Method (read-only, no PipeWire object, no fixture execution): the verdict
blocks of `cdup_cap`, `sd_prop` and `latebind` are extracted *verbatim*
from the committed fixture (pin 2a49d540, sha256 714564a3…) by anchor
search, then exec'd against synthetic leg records shaped like every
realization named in the author report, the boundary report and the
committed comments. The harness never re-implements the predicates — it
runs the committed source lines.

Usage: python3 bimodal-arm-harness.py <pinned-measure_audio.py>
"""
import sys
import textwrap

PIN = sys.argv[1]
SRC = open(PIN).read().splitlines()


def extract(start_anchor, end_anchor):
    starts = [i for i, l in enumerate(SRC) if start_anchor in l]
    assert len(starts) == 1, (start_anchor, starts)
    s = starts[0]
    ends = [i for i in range(s, len(SRC)) if end_anchor in SRC[i]]
    assert ends, (end_anchor,)
    e = ends[0]
    return textwrap.dedent("\n".join(SRC[s:e + 1]))


BLOCKS = {
    "cdup_cap": extract('cl = legs.get("cdup_cap") or {}',
                        '"digits-resolution lattice fails")'),
    "sd_prop": extract('l = legs["sd_prop"]', '"measured nothing")'),
    "latebind": extract('l = legs["latebind"]', '"bind, no refusal measured")'),
}

NS = "r85a_ns_<pid>"      # the serial holder / digits-named sink
LATE = "r85a_late_<pid>"  # the late source name
DEF = "alsa_output.usb-...sink.29"
FOREIGN = "r85a_vsrc_<pid>"
SD = "r85a_sd_<pid>"


def link(out_node, out_port):
    return {"out_node": out_node, "out_port_name": out_port,
            "in_node": "r85a_<pid>_rec", "in_port_name": "input_FL",
            "state": "active"}


def run(arm, block, leg, extra):
    """Exec the committed verdict block; return (failures, leg).

    Only the *environment* is stubbed (the module-table reader, which
    would need a live pactl): every predicate line is the committed one.
    """
    failures = []
    legs = {arm: leg}
    state = {"sd_gone": bool(extra.pop("sd_gone", False))}
    env = {"legs": legs, "failures": failures,
           "PACTLMON_R85_NS": NS, "PACTLMON_R85_LATE": LATE,
           "PACTLMON_R85_SD": SD, "def_sink": DEF,
           "_pactlmon_r85_module_index":
               lambda field, value: None if state["sd_gone"] else 4242}
    env.update(extra)
    exec(compile(block, "<committed-block>", "exec"), env)
    return list(failures), legs[arm]


def leg(exit_code=1, alive=True, samples=(), **kw):
    d = {"exit_code": exit_code, "alive_at_end": alive,
         "samples": [{"at_s": a, "links": ls} for a, ls in samples]}
    d.update(kw)
    return d


SCEN = []

# ---- cdup_cap (digits resolve as serial vs name-first) ----
SCEN.append(("cdup_cap", "serial_monitor_bypass (THIS host: digits=serial, monitor links -> NS)",
             leg(samples=[(1.0, [link(NS, "monitor_FL"), link(NS, "monitor_FR")])]), {}))
SCEN.append(("cdup_cap", "stalled (BOUNDARY host: digits=name(sink) noprop -> 44 B, no links, alive)",
             leg(samples=[(1.0, [])]), {}))
SCEN.append(("cdup_cap", "name_shadow_bound (links exist, none monitor; unmeasured shape)",
             leg(samples=[(1.0, [link(FOREIGN, "capture_FL")])]), {}))
SCEN.append(("cdup_cap", "refused (rc1, dead, no links)",
             leg(exit_code=1, alive=False, samples=[(1.0, [])]), {}))
SCEN.append(("cdup_cap", "foreign_monitor (monitor link on a NON-serial-holder)",
             leg(samples=[(1.0, [link(FOREIGN, "monitor_FL")])]), {}))
SCEN.append(("cdup_cap", "other (no links, rc0, dead = measured nothing)",
             leg(exit_code=0, alive=False, samples=[(1.0, [])]), {}))

# ---- sd_prop (prop form: never touch the trap vs transient bind-kill) ----
SCEN.append(("sd_prop", "clean_default_fallback (BOUNDARY: module alive, default-monitor links)",
             leg(samples=[(1.0, [link(DEF, "monitor_FL")])]), {"sd_gone": False}))
SCEN.append(("sd_prop", "bind_killed_then_default (THIS host: module gone, default-monitor links)",
             leg(samples=[(1.0, [link(DEF, "monitor_FL")])]), {"sd_gone": True}))
SCEN.append(("sd_prop", "no links + module gone (trap destroyed, nothing bound)",
             leg(samples=[(1.0, [])]), {"sd_gone": True}))
SCEN.append(("sd_prop", "no links + module alive (measured nothing)",
             leg(samples=[(1.0, [])]), {"sd_gone": False}))
SCEN.append(("sd_prop", "non-monitor links",
             leg(samples=[(1.0, [link(DEF, "capture_FL")])]), {"sd_gone": False}))
SCEN.append(("sd_prop", "monitor links on a NON-default node",
             leg(samples=[(1.0, [link(NS, "monitor_FL")])]), {"sd_gone": False}))

# ---- latebind (stalled record vs re-target by the late conforming source) ----
SCEN.append(("latebind", "late_bound (THIS host: late source re-armed the record)",
             leg(samples=[(0.9, []), (2.6, [link(LATE, "capture_FL"), link(LATE, "capture_FR")])]),
             {}))
SCEN.append(("latebind", "stalled (BOUNDARY: no link ever, 44 B, alive)",
             leg(samples=[(0.9, []), (4.0, [])]), {}))
SCEN.append(("latebind", "refused (rc1, dead, no links)",
             leg(exit_code=1, alive=False, samples=[(0.9, [])]), {}))
SCEN.append(("latebind", "foreign_bind (link lands on a foreign/monitor node)",
             leg(samples=[(0.9, []), (2.6, [link(FOREIGN, "capture_FL")])]), {}))
SCEN.append(("latebind", "other (no links, rc0, dead = measured nothing)",
             leg(exit_code=0, alive=False, samples=[(0.9, [])]), {}))

print("committed verdict blocks extracted (line counts):",
      {k: len(v.splitlines()) for k, v in BLOCKS.items()})
print()
for arm, label, l, extra in SCEN:
    fails, out = run(arm, BLOCKS[arm], dict(l), dict(extra))
    real = out.get("realization")
    print(f"{arm:9s} | {label:72s} | realization={real!r:28s} "
          f"| failures={len(fails)} {'FAIL' if fails else 'pass'}")
    for f in fails:
        print(f"            └─ {f[:150]}")
