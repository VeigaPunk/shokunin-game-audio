"""r77 BOUNDARY probe 5b — contention, corrected.

p5's snapshot bug: `cell()` inspected the artifact BEFORE reaping the process,
so partial files were recorded as if final. Here every leg is reaped first and
inspected after. The ALSA `hw:0,0` device is also pre-flighted to a KNOWN-FREE
state before each arecord cell (the earlier run left it busy and made three
arecord legs uninterpretable).
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

BUSY = "Device or resource busy"


def sha(p):
    p = Path(p)
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16] if p.exists() else None


def snap(tag, cmd, r):
    out = Path(cmd[-1])
    insp = inspect_wav(out)
    err = r["err"].strip()
    return {"tag": tag, "cmd": " ".join(cmd), "rc": r["rc"], "killed_by_us": r["killed_by_us"],
            "err": err[:220], "class": "alsa_busy" if BUSY in err else ("none" if not err else "other"),
            "bytes": insp.get("bytes"), "sha16": sha(out), "riff": insp.get("riff_size_field"),
            "data": insp.get("data_declared_field"), "frames": insp.get("frames"),
            "peak": insp.get("peak"), "nz": round(insp.get("nonzero_frac") or 0, 4),
            "tone": bool((insp.get("peak") or 0) > 2000 and (insp.get("nonzero_frac") or 0) > 0.3)}


def pair(tag, cmdA, cmdB, delay=0.35, timeout=20.0):
    pa = spawn(cmdA)
    time.sleep(delay)
    pb = spawn(cmdB)
    rb = reap(pb, timeout=timeout)
    ra = reap(pa, timeout=timeout)
    return {tag + "_A_first": snap(tag + "_A", cmdA, ra), tag + "_B_second": snap(tag + "_B", cmdB, rb)}


def device_free(attempts=40, gap=0.5):
    """Pre-flight: arecord -D hw:0,0 must open. Returns the attempts needed."""
    probe = SCRATCH / "free_probe.wav"
    for i in range(attempts):
        r = sh(["arecord", "-D", "hw:0,0", "-f", "cd", "-t", "wav", "-d", "1", str(probe)], timeout=8)
        if r["rc"] == 0 and probe.exists():
            return {"attempts": i + 1, "waited_s": round(i * gap, 1), "err": r["err"].strip()[:120]}
        time.sleep(gap)
    return {"attempts": attempts, "waited_s": attempts * gap, "blocked": True}


def main():
    wipe_scratch()
    make_tone()
    rec = {"probe": "r77-boundary/p5b-contention", "t0": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    rec["preflight_device_free"] = device_free()

    # A. two pw-record on the same real source
    rec["A_two_pw_same_source"] = pair(
        "A",
        ["pw-record", "--target", LINE_SRC, "-n", "96000", str(SCRATCH / "A1.wav")],
        ["pw-record", "--target", LINE_SRC, "-n", "96000", str(SCRATCH / "A2.wav")],
    )

    # B. arecord first, pw-record second (does the ALSA open lock out pulse?)
    rec["preflight_B"] = device_free()
    rec["B_arecord_then_pw"] = pair(
        "B",
        ["arecord", "-D", "hw:0,0", "-f", "cd", "-t", "wav", "-d", "2", str(SCRATCH / "B1.wav")],
        ["pw-record", "--target", LINE_SRC, "-n", "96000", str(SCRATCH / "B2.wav")],
    )

    # C. pw-record first, arecord second (the alsa_busy question)
    rec["preflight_C"] = device_free()
    rec["C_pw_then_arecord"] = pair(
        "C",
        ["pw-record", "--target", LINE_SRC, "-n", "96000", str(SCRATCH / "C1.wav")],
        ["arecord", "-D", "hw:0,0", "-f", "cd", "-t", "wav", "-d", "2", str(SCRATCH / "C2.wav")],
    )

    # D. two arecord on hw:0,0
    rec["preflight_D"] = device_free()
    rec["D_two_arecord"] = pair(
        "D",
        ["arecord", "-D", "hw:0,0", "-f", "cd", "-t", "wav", "-d", "2", str(SCRATCH / "D1.wav")],
        ["arecord", "-D", "hw:0,0", "-f", "cd", "-t", "wav", "-d", "2", str(SCRATCH / "D2.wav")],
    )

    # E. THE BRIEF: monitor roundtrip while another capture holds the SOURCE (tone-anchored)
    e_hold = SCRATCH / "E_hold.wav"
    e_mon = SCRATCH / "E_mon.wav"
    ph = spawn(["pw-record", "--target", LINE_SRC, "-n", "144000", str(e_hold)])  # 3 s
    time.sleep(0.3)
    pm = spawn(["pw-record", "-P", "stream.capture.sink=true", "--target", SPDIF_SINK, "-n", "96000", str(e_mon)])
    time.sleep(0.35)
    pl = spawn(["pw-cat", "-p", "--target", SPDIF_SINK, str(TONE)])
    rm = reap(pm, timeout=16)
    reap(pl, timeout=6)
    rh = reap(ph, timeout=16)
    rec["E_monitor_during_source_hold"] = {
        "monitor_leg": snap("E_mon", ["pw-record", "-P", "stream.capture.sink=true", "--target", SPDIF_SINK,
                                      "-n", "96000", str(e_mon)], rm),
        "source_hold_leg": snap("E_hold", ["pw-record", "--target", LINE_SRC, "-n", "144000", str(e_hold)], rh),
    }

    # F. parec --raw while pw-record holds the same source
    f_hold = SCRATCH / "F_hold.wav"
    f_raw = SCRATCH / "F_raw.raw"
    pf = spawn(["pw-record", "--target", LINE_SRC, "-n", "96000", str(f_hold)])
    time.sleep(0.3)
    fr = sh(["bash", "-lc",
             f"timeout -s KILL 4 parec -d {LINE_SRC} --raw 2>{SCRATCH}/F_parec.err | head -c 65536 > {f_raw}"],
            timeout=9)
    rf = reap(pf, timeout=14)
    rec["F_parec_during_hold"] = {
        "parec_rc": fr["rc"], "raw_bytes": f_raw.stat().st_size if f_raw.exists() else None,
        "parec_err": (SCRATCH / "F_parec.err").read_text()[:200] if (SCRATCH / "F_parec.err").exists() else "",
        "hold_leg": snap("F_hold", ["pw-record", "--target", LINE_SRC, "-n", "96000", str(f_hold)], rf),
    }

    # G. how long does the ALSA device stay locked after pulse clients used it?
    rec["postflight_device_free"] = device_free()

    save_receipt("probe-p5b-contention.json", rec)
    print("preflight:", json.dumps(rec["preflight_device_free"]))
    for k in ("A_two_pw_same_source", "B_arecord_then_pw", "C_pw_then_arecord", "D_two_arecord"):
        for sub, v in rec[k].items():
            print(f"{k:22s} {v['tag']:12s} rc={v['rc']:>4} bytes={str(v['bytes']):>8} class={v['class']:<10} "
                  f"sha={v['sha16']} tone={v['tone']} err={v['err'][:60]}")
        if k in ("B_arecord_then_pw", "C_pw_then_arecord", "D_two_arecord"):
            print(f"{'':22s} preflight={json.dumps(rec['preflight_' + k.split('_')[0]])}")
    for k, v in rec["E_monitor_during_source_hold"].items():
        print(f"E {k:22s} rc={v['rc']:>4} bytes={str(v['bytes']):>8} tone={v['tone']} peak={v['peak']} "
              f"frames={v['frames']} err={v['err'][:50]}")
    print("F:", json.dumps({k: v for k, v in rec["F_parec_during_hold"].items() if k != "hold_leg"})[:200])
    print("G postflight:", json.dumps(rec["postflight_device_free"]))


if __name__ == "__main__":
    main()
