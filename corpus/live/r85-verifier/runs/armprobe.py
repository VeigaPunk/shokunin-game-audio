#!/usr/bin/env python3
"""r85 verifier — executed verdict-block probe for the three host-bimodal
sites (latebind, cdup_cap, sd_prop).

The committed fixture's verdict slices are extracted verbatim by anchor
from the frozen tree and `exec`d against synthetic `legs` dicts. This is
a mutation-style unit probe of the *verdict logic* (not a live audio
run): it tests that each non-observed host realization passes and each
hostile shape fails — i.e. the pinning is real, not silently absorbing.

Usage: armprobe.py <frozen-tree-root>
"""
import hashlib
import json
import re
import sys
import textwrap
from pathlib import Path

NS = "r85a_ns_1"
NS2 = "r85a_ns2_1"
LATE = "r85a_late_1"
SD = "r85a_sd_1"
DEF = "alsa_output.default_sink"


def slice_by_anchors(src, start_anchor, end_anchor, name):
    i = src.index(start_anchor)
    assert src.count(start_anchor) == 1, f"{name}: start anchor not unique"
    j = src.index(end_anchor, i)
    assert src.count(end_anchor) == 1, f"{name}: end anchor not unique"
    text = src[i:j]
    return text


def edge(out_node, out_port, in_node, in_port):
    return {"out": f"{out_node}:{out_port}", "in": f"{in_node}:{in_port}",
            "out_node": out_node, "in_node": in_node,
            "out_port_name": out_port, "in_port_name": in_port,
            "state": "active"}


def run_slice(text, name, legs, module_alive):
    failures = []

    def module_index(field, value):
        return 123 if module_alive else None
    ns = {"legs": legs, "failures": failures,
          "PACTLMON_R85_NS": NS, "PACTLMON_R85_NS2": NS2,
          "PACTLMON_R85_LATE": LATE, "PACTLMON_R85_SD": SD,
          "def_sink": DEF, "_pactlmon_r85_module_index": module_index,
          "re": re}
    code = compile(textwrap.dedent(text), f"<{name}-slice>", "exec")
    exec(code, ns)  # noqa: S102 — verbatim committed slice
    return failures


def main():
    root = Path(sys.argv[1])
    fx = root / "corpus" / "fixtures" / "measure_audio.py"
    src = fx.read_text()
    print(f"# fixture {fx} sha256 {hashlib.sha256(src.encode()).hexdigest()}")
    slices = {
        "latebind": slice_by_anchors(
            src, '            l = legs["latebind"]',
            '    finally:\n        if feeder is not None', "latebind"),
        "cdup_cap": slice_by_anchors(
            src, '                cl = legs.get("cdup_cap") or {}',
            '            sers = [s for s in', "cdup_cap"),
        "sd_prop": slice_by_anchors(
            src, '            l = legs["sd_prop"]',
            '            l = legs["sd_pwlink"]', "sd_prop"),
    }
    for k, v in slices.items():
        print(f"# slice {k}: {len(v.splitlines())} lines, "
              f"sha256 {hashlib.sha256(v.encode()).hexdigest()[:16]}")
    rows = []

    def case(site, label, legs, alive, expect_fail):
        fails = run_slice(slices[site], site, legs, alive)
        real = legs["latebind"].get("realization") if site == "latebind" \
            else legs["cdup_cap"].get("realization") if site == "cdup_cap" \
            else legs["sd_prop"].get("realization")
        got_fail = bool(fails)
        rows.append({"site": site, "case": label, "realization": real,
                     "failures": fails, "expect_fail": expect_fail,
                     "pass": got_fail == expect_fail})
        print(f"{site:9s} {label:34s} realization={real:26s} "
              f"failures={fails} expect_fail={expect_fail} "
              f"{'OK' if got_fail == expect_fail else 'MISMATCH'}")

    # ---------------- latebind ----------------
    good_links = [edge(LATE, "capture_FL", "r85a_late_1_rec", "input_FL")]
    case("latebind", "observed late_bound",
         {"latebind": {"samples": [{"links": good_links}],
                       "alive_at_end": True, "exit_code": None}}, True, False)
    case("latebind", "boundary stalled",
         {"latebind": {"samples": [{"links": []}],
                       "alive_at_end": True, "exit_code": None}}, True, False)
    case("latebind", "refused",
         {"latebind": {"samples": [{"links": []}],
                       "alive_at_end": False, "exit_code": 1}}, True, False)
    case("latebind", "hostile foreign bind",
         {"latebind": {"samples": [{"links": [edge(
             "r85a_ns_1", "monitor_FL", "r85a_late_1_rec", "input_FL")]}],
             "alive_at_end": True, "exit_code": None}}, True, True)
    case("latebind", "hostile dead rc0",
         {"latebind": {"samples": [{"links": []}],
                       "alive_at_end": False, "exit_code": 0}}, True, True)

    # ---------------- cdup_cap ----------------
    holder_mon = [edge(NS, "monitor_FL", "r85a_1_cdup", "input_FL")]
    case("cdup_cap", "observed serial_monitor_bypass",
         {"cdup_cap": {"samples": [{"links": holder_mon}],
                       "alive_at_end": True, "exit_code": None}}, True, False)
    case("cdup_cap", "boundary name_shadow_bound",
         {"cdup_cap": {"samples": [{"links": [edge(
             "r85a_vsrc_1", "capture_FL", "r85a_1_cdup", "input_FL")]}],
             "alive_at_end": True, "exit_code": None}}, True, False)
    case("cdup_cap", "stalled",
         {"cdup_cap": {"samples": [{"links": []}],
                       "alive_at_end": True, "exit_code": None}}, True, False)
    case("cdup_cap", "refused",
         {"cdup_cap": {"samples": [{"links": []}],
                       "alive_at_end": False, "exit_code": 1}}, True, False)
    case("cdup_cap", "hostile foreign_monitor",
         {"cdup_cap": {"samples": [{"links": [edge(
             "r85a_other_1", "monitor_FL", "r85a_1_cdup", "input_FL")]}],
             "alive_at_end": True, "exit_code": None}}, True, True)
    case("cdup_cap", "hostile dead rc0",
         {"cdup_cap": {"samples": [{"links": []}],
                       "alive_at_end": False, "exit_code": 0}}, True, True)

    # ---------------- sd_prop ----------------
    def_mon = [edge(DEF, "monitor_FL", "r85a_1_sd_prop", "input_FL")]
    case("sd_prop", "observed bind_killed_then_default",
         {"sd_prop": {"samples": [{"links": def_mon}],
                      "alive_at_end": True, "exit_code": 1}}, False, False)
    case("sd_prop", "boundary clean_default_fallback",
         {"sd_prop": {"samples": [{"links": def_mon}],
                      "alive_at_end": True, "exit_code": 1}}, True, False)
    case("sd_prop", "hostile non-monitor link",
         {"sd_prop": {"samples": [{"links": [edge(
             SD, "capture_FL", "r85a_1_sd_prop", "input_FL")]}],
             "alive_at_end": True, "exit_code": 1}}, False, True)
    case("sd_prop", "hostile non-default monitor",
         {"sd_prop": {"samples": [{"links": [edge(
             "r85a_other_1", "monitor_FL", "r85a_1_sd_prop", "input_FL")]}],
             "alive_at_end": True, "exit_code": 1}}, False, True)
    case("sd_prop", "HOLE? no links + trap dead",
         {"sd_prop": {"samples": [{"links": []}],
                      "alive_at_end": False, "exit_code": 1}}, False, None)
    case("sd_prop", "hostile no links + trap alive",
         {"sd_prop": {"samples": [{"links": []}],
                      "alive_at_end": True, "exit_code": None}}, True, True)

    mismatches = [r for r in rows if not r["pass"]]
    print(json.dumps({"cases": len(rows), "mismatches": len(mismatches),
                      "holes": [r["case"] for r in rows
                                if r["expect_fail"] is None]}))
    return 1 if mismatches else 0


if __name__ == "__main__":
    sys.exit(main())
