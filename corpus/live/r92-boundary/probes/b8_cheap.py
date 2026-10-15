#!/usr/bin/env python3
"""B8 — cheap replays: the disputed label set, the `links=[...]` grammar, and the
read-only absent-class inventory (ffmpeg / LADSPA / LV2 / hrir dirs).

Load-only legs: one pw-cli per variant, `quit` always sent, no audio, no sink.
"""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig as R

DISPUTED = ["gain", "nop", "passthrough", "sum", "avg", "min"]
CONTROLS = ["copy", "bq_lowpass", "convolver"]


def load_only(tok, reps=2):
    rows = []
    for _ in range(reps):
        one = R.run(["pw-cli"], wall=10.0,
                    stdin_data=("load-module libpipewire-module-filter-chain " + tok + "\nquit\n").encode())
        txt = one.out + "\n" + one.err          # pw-cli splits streams: scan both
        loaded = "@module:" in one.out
        why = [l.strip()[:200] for l in txt.splitlines()
               if "cannot create label" in l or "[E]" in l or "[W]" in l or "Mismatched" in l
               or "error parsing" in l or "can't load graph" in l or "can not be set" in l
               or "Could not load module" in l]
        rows.append({"loaded": loaded, "rc": one.rc, "why": why[-5:],
                     "n_E": txt.count("[E]"), "n_W": txt.count("[W]")})
    return rows


def main():
    t0 = time.time()
    pf = R.preflight()
    out = {"stage": "b8_cheap", "preflight": pf,
           "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "labels": {}, "grammar": {}, "fs": {}}

    for lab in DISPUTED + CONTROLS:
        tok = ("node.description=r92b_lab,filter.graph={nodes=[{type=builtin,name=n0,label=%s}]},"
               "audio.channels=1,audio.position=[MONO]" % lab)
        rows = load_only(tok)
        out["labels"][lab] = rows
        print("b8 label %-12s loaded=%s  %s" % (lab, [r["loaded"] for r in rows],
                                                rows[0]["why"][:1]))

    # links grammar (the two forms the scout measured) -- load-only
    base = ("node.description=r92b_lk,filter.graph={nodes=["
            "{type=builtin,name=b1,label=bq_lowpass,control={Freq=1000.0,Q=0.707}},"
            "{type=builtin,name=b2,label=bq_highpass,control={Freq=200.0,Q=0.707}}]")
    variants = {
        "quoted-colon": base + ',links=[{output="b1:Out",input="b2:In"}]},audio.channels=1,audio.position=[MONO]',
        "unquoted-colon": base + ',links=[{output=b1:Out,input=b2:In}]},audio.channels=1,audio.position=[MONO]',
        "hash-in-value": ("node.description=r92b_lk,filter.graph={nodes=[{type=lv2,name=v,"
                          "plugin=http://example.org/r92b#none,label=x}]},audio.channels=1,audio.position=[MONO]"),
    }
    for nm, tok in variants.items():
        rows = load_only(tok)
        out["grammar"][nm] = {"rows": rows}
        print("b8 grammar %-16s loaded=%s %s" % (nm, [r["loaded"] for r in rows], rows[0]["why"][:1]))

    # read-only filesystem inventory
    def lsdir(d):
        try:
            return sorted(os.listdir(d))
        except Exception as e:
            return ["<ERR %s>" % e]
    out["fs"] = {
        "spa_filter_graph": lsdir("/usr/lib/spa-0.2/filter-graph"),
        "ladspa_dirs": {d: lsdir(d) for d in ("/usr/lib64/ladspa", "/usr/lib/ladspa")},
        "lv2": lsdir("/usr/lib/lv2"),
    }
    f = subprocess.run(["find", "/usr/share/pipewire", "-name", "*kemar*"], capture_output=True, text=True)
    f2 = subprocess.run(["find", "/usr/share/pipewire", "-name", "*hesuvi*"], capture_output=True, text=True)
    out["fs"]["hrir_kemar"] = f.stdout.strip().splitlines()
    out["fs"]["hrir_hesuvi"] = f2.stdout.strip().splitlines()
    print("b8 fs spa:", out["fs"]["spa_filter_graph"])
    print("b8 fs ladspa:", out["fs"]["ladspa_dirs"], "lv2 bundles:", len(out["fs"]["lv2"]))
    print("b8 fs hrir kemar/hesuvi:", out["fs"]["hrir_kemar"], out["fs"]["hrir_hesuvi"])

    out["elapsed_s"] = round(time.time() - t0, 1)
    out["sweep"] = R.sweep()
    out["final"] = R.live_r92b()
    R.jdump(os.path.join(R.REC, "b8_cheap.json"), out)
    print("WROTE b8_cheap.json (%.1fs)" % (time.time() - t0))
    print("SWEEP clean:", out["sweep"]["clean"], "final:", out["final"])


if __name__ == "__main__":
    main()
