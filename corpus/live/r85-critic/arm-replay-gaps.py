#!/usr/bin/env python3
"""r85-critic gap replay: the arms that are NOT either-way-pinned are
exercised with mutated receipts to show exactly what they absorb.

Arm text is sliced verbatim from the COMMITTED blob
(`git show 2a49d540:corpus/fixtures/measure_audio.py`). Measurement
functions that need live files (`_pactlmon_r85_amps`) are stubbed with
canned windows — only the arm's DECISION logic is under test. No host
calls. Read-only: writes only under corpus/live/r85-critic/.
"""
import copy
import importlib.util
import sys as _sys

_sys.dont_write_bytecode = True
import json
import subprocess
import textwrap
from pathlib import Path

ROOT = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
OUT = ROOT / "corpus/live/r85-critic"
COMMIT = "2a49d540"
FIX = ROOT / "corpus/fixtures/measure_audio.py"

spec = importlib.util.spec_from_file_location("measure_audio_r85b", FIX)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

blob = subprocess.run(["git", "show", f"{COMMIT}:corpus/fixtures/measure_audio.py"],
                      cwd=ROOT, capture_output=True, check=True).stdout.decode()
lines = blob.splitlines()


def slice_by_markers(start_marker, end_marker, occurrence=1):
    hits = [i for i, ln in enumerate(lines) if start_marker in ln]
    assert hits, f"start marker missing: {start_marker}"
    i0 = hits[occurrence - 1]
    j = next(j for j in range(i0, len(lines)) if end_marker in lines[j])
    return textwrap.dedent("\n".join(lines[i0:j + 1]))


ARMS = {
    "helpers": slice_by_markers('def links_of(nm):',
                                'return {e.get("out_port_name") for e in links_of(nm)}'),
    "src_bind": slice_by_markers('for nm, want_node in (("t_srcname"',
                                 '"fails")'),
    "sd_connect": slice_by_markers('for nm in ("sd_record", "sd_parec"):',
                                   '"death — the no-link arm fails")'),
    "mixdup": slice_by_markers('da = _pactlmon_r85_amps(dup_f',
                               '"(<=2.05x) fails")'),
    "mixdelay": slice_by_markers('da = _pactlmon_r85_amps(dly_f',
                                 '"bound fails")'),
    "mixinv": slice_by_markers('ia_ = _pactlmon_r85_amps(inv_f',
                               '"realization")'),
    "g_zero": slice_by_markers('l = legs["g_zero"]',
                               '"arm fails")'),
    "cdup_move": slice_by_markers('cm = legs.get("cdup_move")',
                                  '"collision law fails")'),
}

CANNED = {"windows": [{"at_s": 2.0, "l_a": 8192.0, "peak": 32768,
                       "rail_frac": 0.23}]}


def canned_la(la):
    """A single-stream / over-sum tap window with l_a = la (ratio = la/ref)."""
    return {"windows": [{"at_s": 2.0, "l_a": la, "peak": 32768,
                         "rail_frac": 0.23}]}
report = {"commit": COMMIT, "arms": {k: ARMS[k].splitlines()[0].strip() + " ... "
                                     + ARMS[k].splitlines()[-1].strip()
                                     for k in ARMS}, "cases": []}


def run(arm, legs, *, canned=None, extra=None):
    ns = {
        "legs": copy.deepcopy(legs), "failures": [],
        "PACTLMON_R85_VSRC": "r85a_vsrc_x",
        "PACTLMON_R85_VSRC2": "r85a_vsrc_xb",
        "PACTLMON_R85_NS2": "r85a_ns2_x",
        "PACTLMON_R85_DUP_ENV": (1.80, 2.20),
        "PACTLMON_R85_RAIL_ENV": (0.08, 0.60),
        "lhz": 1000.0, "rhz": 1500.0, "ref": 8192.0, "ns_idx": 172871,
        "_pactlmon_r85_amps": lambda path, freqs, **k: (canned or CANNED),
        "_pactlmon_r85_med": mod._pactlmon_r85_med,
        "_pactlmon_r85_vol_pct": mod._pactlmon_r85_vol_pct,
        # file-path placeholders: the stubbed amps ignores them
        "dup_f": "/nonexistent/dup.wav", "dly_f": "/nonexistent/dly.wav",
        "inv_f": "/nonexistent/inv.wav",
    }
    ns["PACTLMON_R85_VSRC"] = "r85a_vsrc_x"
    ns.update(extra or {})
    exec(ARMS["helpers"], ns)  # noqa: S102
    exec(ARMS[arm], ns)  # noqa: S102
    return ns["failures"]


def case(name, arm, legs, want_fail, **kw):
    fails = run(arm, legs, **kw)
    report["cases"].append({"case": name, "arm": arm,
                            "expected_failure": want_fail,
                            "got_failure": bool(fails), "failures": fails,
                            "match": bool(fails) == want_fail})


def e(out_node, port):
    return {"out": f"{out_node}:{port}", "in": "rec:input_FL",
            "out_node": out_node, "in_node": "rec",
            "out_port_name": port, "in_port_name": "input_FL",
            "state": "active"}


# ---- GAP 1: t_srcname/t_srcserial/t_srcid never check the NODE ----
foreign = {nm: {"name": nm, "samples": [
    {"at_s": 1.0, "links": [e("some_other_source", "capture_FL"),
                            e("some_other_source", "capture_FR")],
     "size": 100}]}
    for nm in ("t_srcname", "t_srcserial", "t_srcid")}
case("GAP: source-target legs bound to a FOREIGN source still pass",
     "src_bind", foreign, False)
nonshape = {nm: {"name": nm, "samples": [
    {"at_s": 1.0, "links": [e("some_other_source", "playback_FL")],
     "size": 100}]}
    for nm in ("t_srcname", "t_srcserial", "t_srcid")}
case("control: non-capture_ port shape fails", "src_bind", nonshape, True)

# ---- GAP 2: sd_record/sd_parec accept "module never enumerated" ----
case("GAP: connect-kill arm passes with module_dead_at_s=0.0 (never loaded)",
     "sd_connect",
     {"sd_record": {"module_dead_at_s": 0.0, "source_dead_at_s": None,
                    "links": [], "out": {"data_actual": 0}},
      "sd_parec": {"module_dead_at_s": 0.0, "source_dead_at_s": None,
                   "links": [], "out": {"data_actual": 0}}}, False)
case("GAP: connect-kill legs absent -> silent skip, no failure", "sd_connect",
     {}, False)
case("control: module died at 2.5 s fails", "sd_connect",
     {"sd_record": {"module_dead_at_s": 2.5, "source_dead_at_s": 2.5,
                    "links": [], "out": {"data_actual": 0}}}, True)

# ---- GAP 3: mixdup/mixdelay/mixinv arm only the upper bound ----
# the arms recompute the ratio from the tap window (amps stubbed); l_a=8192
# with ref=8192 is the single-stream signature (ratio 1.0).
for arm, legname in (("mixdup", "mixdup"), ("mixdelay", "mixdelay"),
                     ("mixinv", "mixinv")):
    legs = {legname: {"name": legname, "samples": []}}
    case(f"GAP: {arm} passes with ratio 1.0 (single-stream signature)",
         arm, legs, False, canned=canned_la(8192.0))
    case(f"control: {arm} ratio 3.0 fails", arm, legs, True,
         canned=canned_la(24576.0))

# ---- GAP 4: g_zero percent-equality is vacuous when no % is parsed ----
case("GAP: g_zero == g_defsink with both pct None passes", "g_zero",
     {"g_zero": {"exit_code": 0, "stdout": "Volume: no percent here"},
      "g_defsink": {"exit_code": 0, "stdout": "Volume: no percent here"}},
     False)
case("control: g_zero rc=1 fails", "g_zero",
     {"g_zero": {"exit_code": 1, "stdout": ""},
      "g_defsink": {"exit_code": 0, "stdout": "Volume: 40%"}}, True)

# ---- GAP 5: cdup_move post-state == pre-state (no-op indistinguishable) ----
case("GAP: cdup_move rc=0 + unchanged sink passes (silent no-op shape)",
     "cdup_move",
     {"cdup_move": {"pactl": {"exit_code": 0}, "after": {"sink": 172871}}},
     False)
case("control: cdup_move landing on the name-shadow sink fails", "cdup_move",
     {"cdup_move": {"pactl": {"exit_code": 0}, "after": {"sink": 999999}}},
     True)
case("control: cdup_move refusal (rc!=0) fails", "cdup_move",
     {"cdup_move": {"pactl": {"exit_code": 1}, "after": {"sink": 172871}}},
     True)

report["all_match"] = all(c["match"] for c in report["cases"])
(OUT / "arm-replay-gaps.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({"all_match": report["all_match"],
                  "cases": [{k: c[k] for k in ("case", "expected_failure",
                                               "got_failure", "match")}
                            for c in report["cases"]]}, indent=1))
