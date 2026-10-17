"""r77 BOUNDARY probe 5 — roundtrip / contention: who can hold a source at once.

Answers the brief's "capture monitor while ANOTHER capture holds the source"
plus the r76 `alsa_busy` class: which concurrent pair actually collides.
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from r77b_lib import (  # noqa: E402
    LINE_SRC,
    SCRATCH,
    SPDIF_SINK,
    TONE,
    inspect_wav,
    make_tone,
    reap,
    save_receipt,
    sh,
    spawn,
    wipe_scratch,
)


def sha(p):
    p = Path(p)
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16] if p.exists() else None


def cell(tag, cmd, timeout=20.0, expect=None):
    p = spawn(cmd)
    r = reap(p, timeout=timeout)
    out = Path(cmd[-1])
    insp = inspect_wav(out)
    return {"tag": tag, "cmd": " ".join(cmd), "rc": r["rc"], "killed_by_us": r["killed_by_us"],
            "err": r["err"].strip()[:220], "bytes": insp.get("bytes"), "sha16": sha(out),
            "riff": insp.get("riff_size_field"), "data": insp.get("data_declared_field"),
            "peak": insp.get("peak"), "nz": insp.get("nonzero_frac"),
            "tone": bool((insp.get("peak") or 0) > 2000 and (insp.get("nonzero_frac") or 0) > 0.3)}


def main():
    wipe_scratch()
    make_tone()
    rec = {"probe": "r77-boundary/p5-contention", "t0": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

    # A. two concurrent pw-record on the SAME real source
    a1 = SCRATCH / "c_a1.wav"
    a2 = SCRATCH / "c_a2.wav"
    p1 = spawn(["pw-record", "--target", LINE_SRC, "-n", "96000", str(a1)])
    time.sleep(0.3)
    p2 = spawn(["pw-record", "--target", LINE_SRC, "-n", "96000", str(a2)])
    r1, r2 = reap(p1, timeout=16), reap(p2, timeout=16)
    rec["A_two_pwrecord_same_source"] = [
        {**cell("A1", ["true", str(a1)]), "rc": r1["rc"], "err": r1["err"].strip()[:200],
         "bytes": (inspect_wav(a1).get("bytes")), "sha16": sha(a1)},
        {**cell("A2", ["true", str(a2)]), "rc": r2["rc"], "err": r2["err"].strip()[:200],
         "bytes": (inspect_wav(a2).get("bytes")), "sha16": sha(a2)},
    ]

    # B. arecord -D hw:0,0 while a pw-record holds the same source
    b_hold = SCRATCH / "c_b_hold.wav"
    b_hw = SCRATCH / "c_b_hw.wav"
    ph = spawn(["pw-record", "--target", LINE_SRC, "-n", "144000", str(b_hold)])
    time.sleep(0.4)
    rec["B_arecord_during_pwrecord"] = cell("B_hw_during_pwrecord",
                                            ["arecord", "-D", "hw:0,0", "-f", "cd", "-t", "wav",
                                             "-d", "2", str(b_hw)], timeout=12)
    rec["B_hold_leg"] = {**cell("B_hold", ["true", str(b_hold)]), "rc": reap(ph, timeout=14)["rc"]}

    # C. pw-record while arecord holds hw:0,0
    c_hw = SCRATCH / "c_c_hw.wav"
    c_pw = SCRATCH / "c_c_pw.wav"
    pa = spawn(["arecord", "-D", "hw:0,0", "-f", "cd", "-t", "wav", "-d", "3", str(c_hw)])
    time.sleep(0.4)
    rec["C_pwrecord_during_arecord"] = cell("C_pw_during_arecord",
                                            ["pw-record", "--target", LINE_SRC, "-n", "96000", str(c_pw)],
                                            timeout=14)
    rec["C_arecord_leg"] = {**cell("C_arecord", ["true", str(c_hw)]), "rc": reap(pa, timeout=14)["rc"]}

    # D. two concurrent arecord -D hw:0,0 (the alsa_busy question)
    d1 = SCRATCH / "c_d1.wav"
    d2 = SCRATCH / "c_d2.wav"
    pd1 = spawn(["arecord", "-D", "hw:0,0", "-f", "cd", "-t", "wav", "-d", "2", str(d1)])
    time.sleep(0.4)
    rec["D_second_arecord"] = cell("D2", ["arecord", "-D", "hw:0,0", "-f", "cd", "-t", "wav",
                                          "-d", "2", str(d2)], timeout=12)
    rec["D_first_arecord"] = {**cell("D1", ["true", str(d1)]), "rc": reap(pd1, timeout=12)["rc"]}

    # E. THE BRIEF'S QUESTION: monitor roundtrip while another capture holds the SOURCE
    e_hold = SCRATCH / "c_e_hold.wav"
    e_mon = SCRATCH / "c_e_mon.wav"
    pe = spawn(["pw-record", "--target", LINE_SRC, "-n", "144000", str(e_hold)])  # 3 s source hold
    time.sleep(0.3)
    pm = spawn(["pw-record", "-P", "stream.capture.sink=true", "--target", SPDIF_SINK,
                "-n", "96000", str(e_mon)])
    time.sleep(0.35)
    pl = spawn(["pw-cat", "-p", "--target", SPDIF_SINK, str(TONE)])
    rec["E_monitor_during_source_hold"] = {**cell("E_mon", ["true", str(e_mon)]),
                                           "rc": reap(pm, timeout=14)["rc"]}
    reap(pl, timeout=6)
    rec["E_source_hold_leg"] = {**cell("E_hold", ["true", str(e_hold)]), "rc": reap(pe, timeout=14)["rc"]}

    # F. parec raw on a source already held by pw-record
    f_hold = SCRATCH / "c_f_hold.wav"
    f_raw = SCRATCH / "c_f_raw.raw"
    pf = spawn(["pw-record", "--target", LINE_SRC, "-n", "96000", str(f_hold)])
    time.sleep(0.3)
    fr = sh(["bash", "-c",
             f"timeout -s KILL 4 parec -d {LINE_SRC} --raw 2>/tmp/r77b_parec.err | head -c 65536 > {f_raw}"],
            timeout=8)
    rec["F_parec_during_hold"] = {"rc": fr["rc"], "bytes": f_raw.stat().st_size if f_raw.exists() else None,
                                 "stderr": Path("/tmp/r77b_parec.err").read_text()[:200] if Path("/tmp/r77b_parec.err").exists() else "",
                                 "hold_rc": reap(pf, timeout=14)["rc"]}

    save_receipt("probe-p5-contention.json", rec)
    for k, v in rec.items():
        if k in ("probe", "t0"):
            continue
        if isinstance(v, list):
            for row in v:
                print(f"{k:32s} {row['tag']:20s} rc={row['rc']:>4} bytes={str(row['bytes']):>8} "
                      f"sha={row['sha16']} tone={row.get('tone')} err={row['err'][:50]}")
        elif isinstance(v, dict):
            print(f"{k:32s} rc={v.get('rc')} bytes={v.get('bytes')} sha={v.get('sha16')} "
                  f"tone={v.get('tone')} err={(v.get('err') or v.get('stderr') or '')[:60]}")


if __name__ == "__main__":
    main()
