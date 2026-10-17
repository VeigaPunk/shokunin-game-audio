#!/usr/bin/env python3
"""p3 — speaker-test headless: device/cell lattice, node naming, refusal classes."""
import sys, time, json
import r84_probe as R

PROBE = "p3-speaker"
LEGS = [
    ("null_c2",      "-D null -c 2 -l 1 -t sine -S 10",                    8),
    ("pipewire_c2",  "-D pipewire -c 2 -l 1 -t sine -S 5",                10),
    ("default_c2",   "-D default -c 2 -l 1 -t sine -S 5",                 10),
    ("pw_node_ns",   f"-D pipewire:NODE={R.NS} -c 2 -l 1 -t sine -S 20",  10),
    ("hw00_c2",      "-D hw:0,0 -c 2 -l 1 -t sine -S 10",                 10),
    ("plughw00_c2",  "-D plughw:0,0 -c 2 -l 1 -t sine -S 10",             10),
    ("plughw_c6",    "-D plughw:0,0 -c 6 -l 1 -t sine -S 10",             12),
    ("hw00_c6",      "-D hw:0,0 -c 6 -l 1 -t sine -S 10",                 12),
    ("hw00_c1",      "-D hw:0,0 -c 1 -l 1 -t sine",                        8),
    ("hw00_c8",      "-D hw:0,0 -c 8 -l 1 -t sine -S 5",                  14),
    ("bogus_dev",    "-D nosuch_pcm_r84 -c 2 -l 1",                        8),
    ("c0",           "-D null -c 0 -l 1",                                  8),
    ("t_bogus",      "-D null -c 2 -l 1 -t bogus",                         8),
    ("wav",          "-D plughw:0,0 -c 2 -l 1 -t wav",                    12),
    ("s1",           "-D plughw:0,0 -c 2 -l 1 -t sine -s 1 -S 10",        10),
    ("m_bogus",      "-D plughw:0,0 -c 2 -l 1 -m bogusmap",                8),
    ("r96",          "-D plughw:0,0 -c 2 -l 1 -t sine -r 96000 -S 10",    10),
    ("fmt_float",    "-D plughw:0,0 -c 2 -l 1 -t sine -F FLOAT_LE -S 10", 10),
    ("pink",         "-D null -c 2 -l 1 -t pink -S 10",                    8),
]

def sptest_leg(args, cap):
    before = {n["name"] for n in R.nodes_named("")}
    p = R.Proc(f"speaker-test {args}".split())
    nodes = []; cons = []
    t_end = time.time() + cap
    while p.alive() and time.time() < t_end:
        time.sleep(0.15)
        for n in R.nodes_named("speaker-test", "alsa_"):
            if n["name"] not in [x["name"] for x in nodes]: nodes.append(n)
        for c in R.consumers_of("alsa_playback.speaker-test"):
            if c not in cons: cons.append(c)
    timed = p.alive()
    if timed: p.kill()
    res = p.finish(); res["cmd"] = f"speaker-test {args}"
    res["timeout"] = timed
    res["new_nodes"] = sorted(({n["name"] for n in R.nodes_named("")} | set()) - before)
    res["nodes"] = [{"name": n["name"], "class": n["props"].get("media.class"),
                     "props": {k: v for k, v in n["props"].items()
                               if k in ("node.name","media.class","media.role","target.object","node.rate","application.name")}}
                    for n in nodes]
    res["consumers"] = cons
    return res

def main():
    sink = R.load_ns(R.NS); assert sink["verified"]
    results = {"legs": {}}
    try:
        for leg, args, cap in LEGS:
            reps = []
            for rep in range(3):
                r = sptest_leg(args, cap)
                R.record_leg(PROBE, leg, rep, r, {"err1": r["err"].splitlines()[:3],
                                                "out1": r["out"].splitlines()[:3],
                                                "consumers": r["consumers"]})
                reps.append({k: r[k] for k in ("rc","wall","timeout")} |
                            {"err": r["err"].splitlines()[-3:], "out1": r["out"].splitlines()[:2],
                             "nodes": [n["name"] for n in r["nodes"]],
                             "consumers": r["consumers"]})
                time.sleep(0.3)
            results["legs"][leg] = {"args": args, "reps": reps}
            print(f"{leg:12s} rc={[x['rc'] for x in reps]} wall={reps[0]['wall']} "
                  f"nodes={reps[0]['nodes']} cons={reps[0]['consumers'][:2]} err={reps[0]['err'][-1:]}")
        (R.RCPTS/"p3-speaker.json").write_text(json.dumps(results, indent=1))
    finally:
        R.unload_idx(sink["idx"], R.NS)

if __name__ == "__main__":
    sys.exit(main() or 0)
