#!/usr/bin/env python3
"""r91 VERIFIER — mutation + negative controls on the frozen tree copy.

  neg  : PATH-less tool census — every entry must emit a NAMED
         `missing tools` coverage block (never a silent pass).
  mut  : an ARMED CONSTANT mutation (the pinned wavenc streaming header)
         — the three frozen legs must red on exactly that cell.
  stim : a STIMULUS mutation of the resume fixture (it takes the
         CLOCK_LOST PAUSED->PLAYING round-trip the claim says it does
         not) — the resume leg must red.

Read-only w.r.t. the repository; the tree is this seat's own archive
copy. Usage: controls.py <out.json> [neg|mut|stim]...
"""
import importlib.util
import json
import shutil
import sys
from pathlib import Path

TREE = Path("/home/vgpnk/r91-verify-tree")
FIX = TREE / "corpus/fixtures/measure_audio.py"
MUT_APP = "gstfreeze_r91_resume_MUT.py"
RES = {}


def load():
    spec = importlib.util.spec_from_file_location("ma_r91v", FIX)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


ENTRIES = ("gstfrz_prop_r91_entry", "gstfrz_clock_r91_entry",
           "gstfrz_resume_r91_entry", "gstfrz_srcloss_r91_entry",
           "gstfrz_connect_r91_entry")


def neg(m):
    real = shutil.which
    shutil.which = lambda *a, **k: None
    try:
        for fn in ENTRIES:
            e = getattr(m, fn)()
            cb = e.get("coverage_blocked") or []
            RES[f"neg:{fn}"] = {
                "blocked": e.get("blocked"), "coverage_blocked": cb,
                "failures": e.get("failures"),
                "ok": bool(cb) and "missing tools" in str(cb[0])
                and e.get("failures") == []}
    finally:
        shutil.which = real


def mut(m):
    m.GSTFRZ_R91_RIFF_SIZE = 0x7FFF0025          # wrong armed constant
    e = m.gstfrz_clock_r91_entry()
    fails = e.get("failures") or []
    RES["mut:header"] = {
        "failures": fails,
        "n_failures": len(fails),
        "all_header": bool(fails) and all(
            "pinned wavenc streaming placeholders" in f for f in fails),
        "frozen": e.get("frozen"),
        "ok": len(fails) == 3 and all(
            "pinned wavenc streaming placeholders" in f for f in fails)}


def stim(m):
    src = (TREE / "corpus/fixtures/gstfreeze_r91_resume.py").read_text()
    old = ('            if m.type == Gst.MessageType.CLOCK_LOST:\n'
           '                # Observed, never acted on: no set_state(PAUSED/PLAYING)\n'
           '                # anywhere in this process after the initial PLAYING.\n'
           '                st["clock_lost"] = True\n'
           '                st["clock_lost_t"] = t\n')
    assert src.count(old) == 1, "fixture anchor moved — mutation not applied"
    new = old + ('                # VERIFIER STIMULUS MUTATION: take the\n'
                 '                # launcher\'s own PAUSED->PLAYING round-trip.\n'
                 '                st["forced"] = "clock_lost_roundtrip"\n'
                 '                pipe.set_state(Gst.State.PAUSED)\n'
                 '                pipe.set_state(Gst.State.PLAYING)\n')
    (TREE / "corpus/fixtures" / MUT_APP).write_text(src.replace(old, new))
    real = m.GSTFRZ_R91_RESUME_APP
    m.GSTFRZ_R91_RESUME_APP = MUT_APP
    try:
        e = m.gstfrz_resume_r91_entry()
    finally:
        m.GSTFRZ_R91_RESUME_APP = real
        (TREE / "corpus/fixtures" / MUT_APP).unlink(missing_ok=True)
    fails = e.get("failures") or []
    leg = (e.get("legs") or {}).get("r_app") or {}
    st = leg.get("app_status") or {}
    RES["stim:sticky_app"] = {
        "failures": fails,
        "forced": st.get("forced"), "exit": st.get("exit"),
        "rc": st.get("rc"), "errors": (st.get("errors") or [])[:2],
        "clock_lost": st.get("clock_lost"),
        "state_changes": [c.get("new") for c in (st.get("state_changes")
                                                 or [])],
        "relink": e.get("relink"), "resume_bytes": e.get("resume_bytes"),
        "ok": any("never set_state(PLAYING)" in f for f in fails)}


if __name__ == "__main__":
    which = sys.argv[2:] or ["neg", "mut", "stim"]
    m = load()
    if "neg" in which:
        neg(m)
    if "mut" in which:
        mut(m)
    if "stim" in which:
        stim(m)
    Path(sys.argv[1]).write_text(json.dumps(RES, indent=1, default=str)
                                 + "\n")
    for k, v in RES.items():
        print(("PASS" if v.get("ok") else "FAIL"), k,
              json.dumps({kk: vv for kk, vv in v.items()
                          if kk not in ("ok", "frozen")})[:400])
