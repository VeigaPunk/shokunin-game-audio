#!/usr/bin/env python3
"""p1 — aplay device lattice: which -D strings resolve, refusal classes,
plugin-arg params (pipewire:NODE=/ROLE=/etc.), graph witness per leg."""
import sys, time, json
import r84_probe as R

PROBE = "p1-aplay"
TONE = str(R.TMP / "tone_short.wav")   # 1.2 s dual-tone amp 8192

# (leg, dev, extra_env)
LEGS = [
    ("null",            "null",                        None),
    ("sysdefault",      "sysdefault",                  None),
    ("sysdefault_card", "sysdefault:CARD=Audio",       None),
    ("pipewire",        "pipewire",                    None),
    ("default",         "default",                     None),
    ("default_card",    "default:CARD=Audio",          None),
    ("front",           "front:CARD=Audio,DEV=0",      None),
    ("iec958_d0",       "iec958:CARD=Audio,DEV=0",     None),
    ("iec958_d1",       "iec958:CARD=Audio,DEV=1",     None),
    ("surround51",      "surround51:CARD=Audio,DEV=0", None),
    ("surround71",      "surround71:CARD=Audio,DEV=0", None),
    ("hdmi_nvidia0",    "hdmi:CARD=NVidia,DEV=0",      None),
    ("hdmi_generic0",   "hdmi:CARD=Generic,DEV=0",     None),
    ("hw00",            "hw:0,0",                      None),
    ("hw01",            "hw:0,1",                      None),
    ("hw02",            "hw:0,2",                      None),
    ("hw03",            "hw:0,3",                      None),
    ("plughw00",        "plughw:0,0",                  None),
    ("plughw03",        "plughw:0,3",                  None),
    ("hw13",            "hw:1,3",                      None),
    ("hw23",            "hw:2,3",                      None),
    ("hw_cardname",     "hw:CARD=Audio,DEV=0",         None),
    ("hw_cardname_nv",  "hw:CARD=NVidia,DEV=3",        None),
    ("pulse",           "pulse",                       None),
    ("bogus_name",      "nosuch_pcm_r84",              None),
    ("hw9",             "hw:9",                        None),
    ("hw09",            "hw:0,9",                      None),
    ("hw99",            "hw:9,9",                      None),
    ("hw_cardnosuch",   "hw:CARD=NosuchR84",           None),
    ("hw_carddev99",    "hw:CARD=Audio,DEV=99",        None),
    ("plughw99",        "plughw:9,9",                  None),
    ("sysdefault_bad",  "sysdefault:CARD=NosuchR84",   None),
    ("hdmi_bad_dev",    "hdmi:CARD=NVidia,DEV=2",      None),
    ("front_bad",       "front:CARD=NosuchR84,DEV=0",  None),
    ("iec958_bad",      "iec958:CARD=Audio,DEV=9",     None),
    ("empty_d",         "",                            None),
    # plugin-arg surface (50-pipewire.conf @args)
    ("pw_node_ns",      f"pipewire:NODE={R.NS}",       None),
    ("pw_node_bogus",   "pipewire:NODE=no_such_r84",   None),
    ("pw_role",         "pipewire:ROLE=Communication", None),
    ("pw_node_role",    f"pipewire:NODE={R.NS},ROLE=Communication", None),
    ("pw_server_bad",   "pipewire:SERVER=nonexistent_r84", None),
    ("pw_rate44",       "pipewire:RATE=44100",         None),
    ("pw_ch1",          "pipewire:CHANNELS=1",         None),
    ("pw_excl",         f"pipewire:NODE={R.NS},EXCLUSIVE=1", None),
    ("pw_env_props",    "pipewire",                    {"PIPEWIRE_PROPS": "{ node.name=r84alsa_envp }"}),
    ("pw_env_node",     "pipewire",                    {"PIPEWIRE_NODE": R.NS}),
]

def carddev(dev):
    """hw/plughw: N[,M] or CARD name -> (card, dev, 'p')"""
    import re
    m = re.match(r"(?:plug)?hw:(\d+)(?:,(\d+))?", dev)
    if m: return (m.group(1), m.group(2) or "0", "p")
    m = re.match(r"(?:plug)?hw:CARD=(\w+)(?:,DEV=(\d+))?", dev)
    names = {"Audio": "0", "NVidia": "1", "Generic": "2"}
    if m and m.group(1) in names: return (names[m.group(1)], m.group(2) or "0", "p")
    return None

def aplay_leg(dev, env):
    before = {n["name"] for n in R.nodes_named("")}
    pcm = carddev(dev)
    pre = R.pcm_status(pcm[0], pcm[1], pcm[2]) if pcm and pcm[0].isdigit() else None
    p = R.Proc(["aplay", "-D", dev, TONE], env_extra=env)
    nodes_seen, links_seen = [], []
    t_end = time.time() + 5.0
    while p.alive() and time.time() < t_end:
        time.sleep(0.12)
        for n in R.nodes_named("aplay", "r84alsa", "speaker"):
            if n not in nodes_seen: nodes_seen.append(n)
        for c in R.consumers_of("alsa_playback.aplay") + R.consumers_of("r84alsa_envp"):
            if c not in links_seen: links_seen.append(c)
    res = p.finish()
    res["cmd"] = f"aplay -D {dev!r} tone_short.wav"
    post = {n["name"] for n in R.nodes_named("")}
    res["new_node_names"] = sorted(post - before)
    res["nodes_seen"] = [{"name": n["name"], "class": n["props"].get("media.class"),
                          "props": {k: v for k, v in n["props"].items()
                                    if k in ("node.name", "media.class", "media.role", "target.object",
                                             "node.target", "application.name", "stream.playback.sink",
                                             "media.name", "node.rate", "node.exclusive", "resample.quality")}}
                         for n in nodes_seen]
    res["consumers"] = links_seen
    res["pcm_pre"] = pre
    res["pcm_post"] = (R.pcm_status(pcm[0], pcm[1], pcm[2]) + " owner=" + R.pcm_owner(pcm[0], pcm[1], pcm[2])) if pcm and pcm[0].isdigit() else None
    return res

def main():
    sink = R.load_ns(R.NS)
    assert sink["verified"], f"own sink not verified: {sink}"
    results = {"sink": sink, "legs": {}}
    try:
        for leg, dev, env in LEGS:
            reps = []
            for rep in range(3):
                r = aplay_leg(dev, env)
                R.record_leg(PROBE, leg, rep, r,
                             {"err1": r["err"].splitlines()[:3],
                              "new_nodes": r["new_node_names"],
                              "consumers": r["consumers"]})
                reps.append({k: r[k] for k in ("rc", "wall", "timeout")} |
                            {"err": r["err"].splitlines()[:2],
                             "new_nodes": r["new_node_names"],
                             "consumers": r["consumers"],
                             "nodes": [n["name"] for n in r["nodes_seen"]],
                             "nodeprops": [n["props"] for n in r["nodes_seen"]][:1],
                             "pcm_pre": r["pcm_pre"], "pcm_post": r["pcm_post"]})
                time.sleep(0.4)
            results["legs"][leg] = {"dev": dev, "env": env, "reps": reps}
            print(f"{leg:18s} rc={[x['rc'] for x in reps]} "
                  f"links={reps[0]['consumers'][:2]} err={reps[0]['err'][:1]}")
        (R.RCPTS / "p1-aplay.json").write_text(json.dumps(results, indent=1))
    finally:
        R.unload_idx(sink["idx"], R.NS)

if __name__ == "__main__":
    sys.exit(main() or 0)
