#!/usr/bin/env python3
"""B6 — the "zero [E]/[W] diagnostics" claim was measured at PIPEWIRE_DEBUG=3.
Re-arm the two silent convolver legs at debug 3 and 5 (with generous client
timeouts: at debug 5 pw-cli prints orders of magnitude more) and count the
diagnostics at each level.

Also: does a *non-WAV but readable* file (a text file, an empty file, a
directory) behave identically to a missing file? (measured in B3; here only the
log side is compared across levels)

argv[1] = reps (default 2).
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig as R

S = R.SCRATCH


def main():
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    t0 = time.time()
    R.wav_write(os.path.join(S, "r92b_delta.wav"),
                __import__("numpy").concatenate([__import__("numpy").zeros(100), [1.0],
                                                 __import__("numpy").zeros(4095)]), fmt="s16")
    pf = R.preflight()
    out = {"stage": "b6_diag", "reps": reps, "preflight": pf,
           "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "legs": {}}

    cases = {
        "missing-dbg3": ("3", R.fc_args(["{type=builtin,name=cv,label=convolver,"
                                         "config={filename=/nonexistent/r92b_ir.wav}}"])),
        "missing-dbg5": ("5", R.fc_args(["{type=builtin,name=cv,label=convolver,"
                                         "config={filename=/nonexistent/r92b_ir.wav}}"])),
        "noconfig-dbg3": ("3", R.fc_args(["{type=builtin,name=cv,label=convolver}"])),
        "noconfig-dbg5": ("5", R.fc_args(["{type=builtin,name=cv,label=convolver}"])),
        "textfile-dbg5": ("5", R.fc_args(["{type=builtin,name=cv,label=convolver,"
                                          "config={filename=%s}}" % os.path.join(S, "r92b_ir_text.wav")])),
        "valid-dbg3": ("3", R.fc_args(["{type=builtin,name=cv,label=convolver,"
                                       "config={filename=%s}}" % os.path.join(S, "r92b_ir_2tap.wav")])),
    }
    if not os.path.exists(os.path.join(S, "r92b_ir_text.wav")):
        with open(os.path.join(S, "r92b_ir_text.wav"), "w") as f:
            f.write("not a wav\n" * 40)

    for name, (lvl, args) in cases.items():
        rows = []
        for rep in range(reps):
            rig = R.Rig(name, args, debug=lvl, idle=1.0, hard=20.0, settle=1.5).arm()
            rp = os.path.join(S, "%s_ref_%d.wav" % (name, rep))
            op = os.path.join(S, "%s_out_%d.wav" % (name, rep))
            rig.start_captures(rp, op)
            rig.play(os.path.join(S, "r92b_delta.wav"))
            rig.stop()
            d = rig.disarm()
            txt = rig.cli.text()
            lines = txt.splitlines()
            interesting = [l.strip()[:230] for l in lines
                           if "[E]" in l or "[W]" in l or "convolver" in l.lower() or "ir" in l.lower()
                           or "file" in l.lower()]
            rows.append({"rep": rep, "log_stats": d.get("log_stats"), "n_lines": len(lines),
                         "n_interesting": len(interesting), "interesting": interesting[-25:],
                         "out_bytes": os.path.getsize(op) if os.path.exists(op) else 0,
                         "live": d.get("live")})
            print("b6 %-14s r%d debug=%s lines=%-5s E=%-3s W=%-3s I=%-4s interesting=%d out=%s" %
                  (name, rep, lvl, d["log_stats"]["lines"], d["log_stats"]["E"], d["log_stats"]["W"],
                   d["log_stats"]["I"], len(interesting), rows[-1]["out_bytes"]))
            for l in interesting[-6:]:
                print("        |", l)
        out["legs"][name] = {"debug": lvl, "args": args, "rows": rows}

    out["elapsed_s"] = round(time.time() - t0, 1)
    out["sweep"] = R.sweep()
    out["final"] = R.live_r92b()
    R.jdump(os.path.join(R.REC, "b6_diag.json"), out)
    print("WROTE b6_diag.json (%.1fs)" % (time.time() - t0))
    print("SWEEP clean:", out["sweep"]["clean"], "final:", out["final"])


if __name__ == "__main__":
    main()
