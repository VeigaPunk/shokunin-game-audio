#!/usr/bin/env python3
"""p4 — PULSE_PROP env vars / paplay --property: which land on the pw node,
which only on the pulse proplist (pactl), which drop."""
import sys, time, json, subprocess
import r84_probe as R

PROBE = "p4-props"
TONE = str(R.TMP / "tone_a.wav")   # 4 s

LEGS = [
    ("baseline",      {}),
    ("appname",       {"PULSE_PROP_application.name": "r84alsa_app"}),
    ("role_comm",     {"PULSE_PROP_media.role": "Communication"}),
    ("role_bogus",    {"PULSE_PROP_media.role": "notarole"}),
    ("medianame",     {"PULSE_PROP_media.name": "r84alsa_media"}),
    ("iconname",      {"PULSE_PROP_application.icon_name": "r84alsa_icon"}),
    ("invented",      {"PULSE_PROP_zzz.invented": "42"}),
    ("proc_bin",      {"PULSE_PROP_application.process.binary": "r84alsa_bin"}),
    ("restore_id",    {"PULSE_PROP_module-stream-restore.id": "r84alsa_rs"}),
    ("filter_want",   {"PULSE_PROP_filter.want": "echo-cancel"}),
    ("bare_prop",     {"PULSE_PROP": "media.role=Communication"}),
    ("combo",         {"PULSE_PROP_application.name": "r84alsa_app",
                       "PULSE_PROP_media.role": "Video",
                       "PULSE_PROP_media.name": "r84alsa_m"}),
]

def si_props_for(needle):
    """sink-input entries whose properties contain needle anywhere."""
    for si in R.pactl_json("sink-inputs"):
        props = si.get("properties", {})
        if any(needle in str(v) or needle in str(k) for k, v in props.items()):
            return props
    return None

def paplay_leg(env):
    p = R.Proc(["paplay", "-d", R.NS, TONE], env_extra=env)
    node = None; siprops = None
    t_end = time.time() + 6
    while p.alive() and time.time() < t_end:
        time.sleep(0.15)
        ns = [n for n in R.nodes_named("paplay", "r84alsa") if n["name"] != R.NS]
        for n in ns:
            if node is None or "r84alsa" in n["name"]: node = n
        # also scan pactl view
        si = si_props_for("r84alsa") or (R.pactl_json("sink-inputs") or [{}])[-1].get("properties")
        if si: siprops = si
    res = p.finish(); res["cmd"] = "paplay -d r84alsa_ns tone_a.wav " + json.dumps(env)
    res["node_props"] = (node or {}).get("props")
    res["node_name"] = (node or {}).get("name")
    res["si_props"] = siprops
    return res

def parec_leg(env):
    out = R.TMP / "p4_rec.wav"
    player = R.play_at(R.NS, TONE, "r84alsa_p4tone"); time.sleep(0.5)
    p = R.Proc(f"parec -d {R.NS}.monitor --file-format=wav {out}".split(), env_extra=env)
    time.sleep(2.0)
    node = None
    for n in R.nodes_named("parec", "pacat", "r84alsa"):
        if n["name"] != R.NS: node = n
    so = None
    for s in R.pactl_json("source-outputs"):
        props = s.get("properties", {})
        if "r84alsa" in json.dumps(props) or s.get("index"): so = props
    p.kill(); res = p.finish()
    player.kill(); player.finish()
    res["node_props"] = (node or {}).get("props")
    res["node_name"] = (node or {}).get("name")
    res["so_props"] = so
    res["rec_size"] = R.file_hdr(out)["size"]
    try: out.unlink()
    except FileNotFoundError: pass
    return res

KEEP = ("node.name","media.class","media.role","media.name","application.name",
        "application.icon_name","application.process.binary","target.object",
        "module-stream-restore.id","filter.want","zzz.invented","stream.id",
        "media.category","node.rate","media.filename")

def trim(props):
    if not props: return None
    return {k: v for k, v in props.items() if k in KEEP or "r84alsa" in str(v)}

def main():
    sink = R.load_ns(R.NS); assert sink["verified"]
    results = {"play": {}, "rec": {}}
    try:
        for leg, env in LEGS:
            reps = []
            for rep in range(3):
                r = paplay_leg(env)
                R.record_leg(PROBE, leg, rep, r, {"node": r["node_name"],
                                                "node_props": trim(r["node_props"]),
                                                "si_props": trim(r["si_props"])})
                reps.append({"rc": r["rc"], "wall": r["wall"], "node": r["node_name"],
                             "node_props": trim(r["node_props"]), "si_props": trim(r["si_props"])})
                time.sleep(0.3)
            results["play"][leg] = {"env": env, "reps": reps}
            print(f"play/{leg:12s} rc={[x['rc'] for x in reps]} node={reps[0]['node']} "
                  f"np={json.dumps(reps[0]['node_props'])[:220]}")
        # record side (subset)
        for leg, env in LEGS[:4] + [("rec_invented", {"PULSE_PROP_zzz.invented": "42"})]:
            reps = []
            for rep in range(3):
                r = parec_leg(env)
                R.record_leg(PROBE, "rec_" + leg, rep, r,
                             {"node": r["node_name"], "node_props": trim(r["node_props"]),
                              "so_props": trim(r["so_props"]), "rec_size": r["rec_size"]})
                reps.append({"rc": r["rc"], "node": r["node_name"], "size": r["rec_size"],
                             "node_props": trim(r["node_props"]), "so_props": trim(r["so_props"])})
                time.sleep(0.3)
            results["rec"][leg] = {"env": env, "reps": reps}
            print(f"rec/{leg:12s} node={reps[0]['node']} np={json.dumps(reps[0]['node_props'])[:220]}")
        (R.RCPTS/"p4-props.json").write_text(json.dumps(results, indent=1))
    finally:
        R.unload_idx(sink["idx"], R.NS)

if __name__ == "__main__":
    sys.exit(main() or 0)
