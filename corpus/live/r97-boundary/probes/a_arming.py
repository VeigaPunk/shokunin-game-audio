#!/usr/bin/env python3
"""r97b stage A — replay of the r97 scout arming law (claims 1-2, rows
`wp.arming.*`) with fresh processes, under an ambient and a seat-hog arm.

Variants (each a fresh `wireplumber` process, own wall cap, WIREPLUMBER_DEBUG=I):
  V1 WIREPLUMBER_CONFIG_DIR=<empty dir>        -> the scout claims rc 78 with
      "no modules loaded from context.modules" / "can't find protocol ..."
  V2 WIREPLUMBER_CONFIG_DIR=<copy of conf>     -> runs; shipped conf.d no longer read
  V3 private XDG_CONFIG_HOME (arming shape)    -> runs; shipped + own fragment opened
  V4 no override (operator config)             -> runs; operator fragment opened
  V5 private XDG_CONFIG_HOME + DATA_DIR=<one script> -> expect rc 78 sm-objects.lua
  V6 WIREPLUMBER_CONFIG_DIR=<dir with an EMPTY wireplumber.conf> -> tests whether
      the scout's "no modules loaded" chain belongs to this shape instead

Records rc, wall time, fragment files actually opened, the failure strings, the
raw text length and (for the short legs) the raw text. Bounded: 20 s cap,
process-group kill.
"""
import json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r97blib import (SEAT, RUN, ENV, REC, SCR, run, stage_out,
                     stage_write, loadavg, ensure_up, down)

FRAG_MARK = "opening fragment file:"
USING_MARK = "using configuration file:"
FAIL_MARKS = ["no modules loaded from context.modules",
              "can't find protocol 'PipeWire:Protocol:Native'",
              "Failed to connect to PipeWire",
              "Could not locate configuration file 'wireplumber.conf'",
              "Could not locate script 'sm-objects.lua'",
              "failed to load components"]


def variant_env(v):
    e = dict(ENV)
    e["PIPEWIRE_RUNTIME_DIR"] = RUN
    e["XDG_RUNTIME_DIR"] = RUN
    e["WIREPLUMBER_DEBUG"] = "I"
    if v == "V1":
        e["WIREPLUMBER_CONFIG_DIR"] = SEAT + "/conf/wp-empty"
        e["XDG_CONFIG_HOME"] = SEAT + "/conf/xdg-config"
    elif v == "V2":
        e["WIREPLUMBER_CONFIG_DIR"] = SEAT + "/conf/wp-copy"
        e["XDG_CONFIG_HOME"] = SEAT + "/conf/xdg-config"
    elif v == "V3":
        e["XDG_CONFIG_HOME"] = SEAT + "/conf/xdg-config"
    elif v == "V4":
        e.pop("XDG_CONFIG_HOME", None)
    elif v == "V5":
        e["XDG_CONFIG_HOME"] = SEAT + "/conf/xdg-config"
        e["WIREPLUMBER_DATA_DIR"] = SEAT + "/conf/wpdata"
    elif v == "V6":
        e["WIREPLUMBER_CONFIG_DIR"] = SEAT + "/conf/wp-stub"
        e["XDG_CONFIG_HOME"] = SEAT + "/conf/xdg-config"
    return e


def one_rep(rep, cap=20.0):
    out = {"rep": rep, "variants": {}}
    for v in ("V1", "V2", "V3", "V4", "V5", "V6"):
        logp = os.path.join(SCR, f"a_{v}_rep{rep}.log")
        env = variant_env(v)
        r = run(["wireplumber", "-c", "wireplumber.conf", "-p", "main"],
                timeout=cap, env=env)
        text = r["stderr"] + r["stdout"]
        open(logp, "w").write(text)
        frags = sorted({l.split(FRAG_MARK, 1)[1].strip()
                        for l in text.splitlines() if FRAG_MARK in l})
        using = sorted({l.split(USING_MARK, 1)[1].strip()
                        for l in text.splitlines() if USING_MARK in l})
        marks = {m: (m in text) for m in FAIL_MARKS}
        out["variants"][v] = {
            "rc": r["rc"], "timed_out": r["timed_out"], "dur_s": r["dur_s"],
            "raw_len": len(text),
            "fragments_opened": [f.replace(SEAT, "$SEAT") for f in frags],
            "using_config": using,
            "failure_marks": marks,
            "log": logp.replace(SEAT, "$SEAT"),
            "loadavg": loadavg(),
            "raw_head": text[:1500],
        }
        time.sleep(0.4)
    return out


def main():
    arm = sys.argv[1] if len(sys.argv) > 1 else "ambient"
    reps = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    cap = float(sys.argv[3]) if len(sys.argv) > 3 else 20.0
    out = stage_out("a_arming")
    out["arm"] = arm
    out["debug_level"] = "I"
    out["cap_s"] = cap
    # core only: the variant WirePlumbers need a private core, but no second
    # policy daemon may run while a variant is measured.
    down("wp")
    time.sleep(0.5)
    e = ensure_up(verbose=True)
    out["pair"] = e
    if not e.get("ok") and not e.get("already"):
        out["fatal"] = "private core did not come up"
        stage_write(out, "a_arming.json")
        return
    for n in range(reps):
        out["reps"].append(one_rep(n, cap))
        out["loadavg_end_rep"] = loadavg()
    for rep in out["reps"]:
        print(f"--- rep {rep['rep']}")
        for v, d in rep["variants"].items():
            hit = [k for k, x in d["failure_marks"].items() if x]
            print(f"  {v} rc={d['rc']:<4} timed={str(d['timed_out']):<5} "
                  f"{d['dur_s']:>6}s raw={d['raw_len']:<6} frags={len(d['fragments_opened'])} "
                  f"marks={[h[:26] for h in hit]}")
            for f in d["fragments_opened"]:
                print(f"        frag {f}")
    stage_write(out, "a_arming.json")


if __name__ == "__main__":
    main()
