#!/usr/bin/env python3
"""p2 — arecord device lattice: capture-side resolution, refusal classes,
plugin NODE= semantics on capture, content floor per route."""
import sys, time, json
import r84_probe as R

PROBE = "p2-arecord"
LINE = "alsa_input.usb-Generic_USB_Audio-00.HiFi__Line__source"

LEGS = [
    ("null",         "null",                     "-d 1", False),
    ("sysdefault",   "sysdefault",               "-d 1", False),
    ("sysdef_card",  "sysdefault:CARD=Audio",    "-d 1", False),
    ("pipewire",     "pipewire",                 "-d 2", False),
    ("default",      "default",                  "-d 2", False),
    ("front",        "front:CARD=Audio,DEV=0",   "-d 1", False),
    ("hw00",         "hw:0,0",                   "-d 1", False),
    ("hw01",         "hw:0,1",                   "-d 1", False),
    ("hw02",         "hw:0,2",                   "-d 1", False),
    ("hw03_playonly","hw:0,3",                   "-d 1", False),   # playback-only PCM
    ("plughw00",     "plughw:0,0",               "-d 1", False),
    ("plughw01",     "plughw:0,1",               "-d 1", False),
    ("hw13_nocap",   "hw:1,3",                   "-d 1", False),   # HDMI: no capture subdev
    ("hw_cardname",  "hw:CARD=Audio,DEV=1",      "-d 1", False),
    ("pulse",        "pulse",                    "-d 1", False),
    ("bogus",        "nosuch_pcm_r84",           "-d 1", False),
    ("hw9",          "hw:9",                     "-d 1", False),
    ("hw09",         "hw:0,9",                   "-d 1", False),
    ("empty",        "",                         "-d 1", False),
    ("pw_node_ns",   f"pipewire:NODE={R.NS}",    "-d 3", True),    # tone plays into ns
    ("pw_node_line", f"pipewire:NODE={LINE}",    "-d 2", False),
    ("pw_node_bogus","pipewire:NODE=no_such_r84","-d 2", False),
    ("pw_role",      "pipewire:ROLE=Communication", "-d 2", False),
    ("def_card",     "default:CARD=Audio",       "-d 1", False),
]

def arecord_leg(dev, dur, tone):
    out = R.TMP / f"arec_{abs(hash((dev,time.time())))%10**8}.wav"
    player = None
    if tone:
        player = R.play_at(R.NS, str(R.TMP/"tone_a.wav"), "r84alsa_srctone")
        time.sleep(0.6)   # let tone reach the sink
    before = {n["name"] for n in R.nodes_named("")}
    p = R.Proc(f"arecord -D {dev} {dur} -f cd".split() + [str(out)])
    nodes_seen, prods = [], []
    t_end = time.time() + float(dur.split()[1]) + 5
    while p.alive() and time.time() < t_end:
        time.sleep(0.15)
        for n in R.nodes_named("arecord", "r84alsa"):
            if n["name"] not in [x["name"] for x in nodes_seen]: nodes_seen.append(n)
        for pr in R.producers_of("alsa_capture.arecord"):
            if pr not in prods: prods.append(pr)
    res = p.finish()
    if player: player.kill(); player.finish()
    res["cmd"] = f"arecord -D {dev!r} {dur} -f cd <out.wav>"
    res["hdr"] = R.file_hdr(out)
    if res["hdr"]["size"] > 60:
        w = R.windows(out)
        res["peak"] = max((x["peak"] for x in w), default=0)
        res["bins"] = [{k: x[k] for k in x if "@" in k} for x in w[:4]]
    res["nodes"] = [{"name": n["name"], "class": n["props"].get("media.class"),
                     "props": {k: v for k, v in n["props"].items()
                               if k in ("node.name","media.class","media.role","target.object",
                                        "node.target","stream.capture.sink","node.rate","node.latency","media.name")}}
                    for n in nodes_seen if n["name"] != "r84alsa_srctone"]
    res["producers"] = prods
    try: out.unlink()
    except FileNotFoundError: pass
    return res

def main():
    sink = R.load_ns(R.NS); assert sink["verified"]
    results = {"sink": sink, "legs": {}}
    try:
        for leg, dev, dur, tone in LEGS:
            reps = []
            for rep in range(3):
                r = arecord_leg(dev, dur, tone)
                R.record_leg(PROBE, leg, rep, r, {"err1": r["err"].splitlines()[:3],
                                                "size": r["hdr"]["size"],
                                                "producers": r["producers"]})
                reps.append({k: r[k] for k in ("rc","wall","timeout")} |
                            {"err": r["err"].splitlines()[:2], "size": r["hdr"]["size"],
                             "peak": r.get("peak"), "producers": r["producers"],
                             "nodes": [n["name"] for n in r["nodes"]],
                             "nodeprops": [n["props"] for n in r["nodes"] if n["name"].startswith(("alsa_","r84alsa"))][:1]})
                time.sleep(0.4)
            results["legs"][leg] = {"dev": dev, "reps": reps}
            print(f"{leg:14s} rc={[x['rc'] for x in reps]} size={reps[0]['size']} "
                  f"peak={reps[0]['peak']} prod={reps[0]['producers'][:2]} err={reps[0]['err'][:1]}")
        (R.RCPTS/"p2-arecord.json").write_text(json.dumps(results, indent=1))
    finally:
        R.unload_idx(sink["idx"], R.NS)

if __name__ == "__main__":
    sys.exit(main() or 0)
