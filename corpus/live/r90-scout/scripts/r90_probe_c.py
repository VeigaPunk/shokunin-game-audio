#!/usr/bin/env python3
"""r90 scout addendum C — closing legs:
  f2c: unload-by-name semantics; store debounce at creation; capture leg with
       the r77-pinned stream.capture.sink prop; passive-link props; pw-link -t
       with a live link; pw-link listing patterns; target-store long poll.
Receipts: receipts/f2c.json, raw under runs/f2c_*/rep<N>/.
"""
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from r90_probe import (ROOT, REC, census, load_null_sink, module_ids,  # noqa
                       node_id, parse_stream_props, pw_dump, sh, spawn, step,
                       stop, unload)

TONE48 = ROOT / "r90_tone48.wav"


def n_modules_named(name):
    return [l.split("\t")[0] for l in sh(["pactl", "list", "modules", "short"])["out"]
            .decode().splitlines() if name in l]


def poll_key(key, timeout=8.0, poll=0.15, field=None, want=None):
    t0 = time.time()
    seen = []
    while time.time() - t0 < timeout:
        try:
            e = parse_stream_props()["entries"].get(key)
        except Exception:
            e = None
        seen.append((round(time.time() - t0, 2), json.dumps(e)[:70]))
        if e is not None and (field is None or (isinstance(e, dict)
                                                and e.get(field) == want)):
            return {"ok": True, "delay_s": round(time.time() - t0, 2), "entry": e,
                    "polls": seen[:4]}
        time.sleep(poll)
    return {"ok": False, "delay_s": None, "polls": seen[-2:]}


def stage_f2c(rep):
    res = {}
    # 1) unload-by-name with two same-named seat-owned modules
    m1, _, _ = load_null_sink(f"r90n1r{rep}")
    m2, _, _ = load_null_sink(f"r90n2r{rep}")
    before = n_modules_named("module-null-sink")
    res["u_load"] = {"m1": m1, "m2": m2, "null_sinks_before": before}
    res["u_by_name"] = step("f2c", rep, "unload_by_name",
                            ["pactl", "unload-module", "module-null-sink"])
    time.sleep(0.3)
    res["u_null_sinks_after"] = n_modules_named("module-null-sink")
    res["u_my_modules_alive"] = [m for m in (m1, m2) if m and str(m) in module_ids()]
    for m in res["u_my_modules_alive"]:
        res.setdefault("u_cleanup", []).append(unload(m))

    # 2) store debounce measured from stream creation (no stop)
    app = f"r90d{rep}"
    key = f"Output/Audio:application.name:{app}"
    p = spawn(["pw-play", "--target", "r90a", "-P", f"application.name={app}",
               "-P", f"node.name={app}", str(TONE48)])
    res["d_creation_poll"] = poll_key(key, timeout=8.0)
    res["d_stop"] = stop(p)

    # 3) pulse volume write -> channelVolumes store -> replay restore
    app2 = f"r90s{rep}"
    key2 = f"Output/Audio:application.name:{app2}"
    p = spawn(["pw-play", "--target", "r90a", "-P", f"application.name={app2}",
               "-P", f"node.name={app2}", str(TONE48)])
    time.sleep(1.2)
    r = sh(["pactl", "list", "sink-inputs"])
    idx = None
    cur = None
    for line in r["out"].decode().splitlines():
        m = re.match(r"^Sink Input #(\d+)", line)
        if m:
            cur = m.group(1)
        if "application.name" in line and app2 in line:
            idx = cur
    res["v_index"] = idx
    if idx:
        res["v_setvol"] = step("f2c", rep, "setvol", ["pactl", "set-sink-input-volume", idx, "50%"])
        res["v_store_poll"] = poll_key(key2, timeout=6.0, field="channelVolumes", want=[0.125, 0.125])
    res["v_stop"] = stop(p)
    # replay: does the stored channelVolumes get restored?
    p = spawn(["pw-play", "--target", "r90a", "-P", f"application.name={app2}",
               "-P", f"node.name={app2}b", str(TONE48)])
    time.sleep(1.3)
    nid = node_id(f"{app2}b")
    res["v_replay_node"] = nid
    if nid:
        res["v_replay_props"] = step("f2c", rep, "replay_props",
                                     ["pw-cli", "enum-params", str(nid), "Props"])
    res["v_replay_stop"] = stop(p)

    # 4) target store: long poll for the 'target' field
    app3 = f"r90y{rep}"
    key3 = f"Output/Audio:application.name:{app3}"
    p = spawn(["pw-play", "--target", "r90a", "-P", f"application.name={app3}",
               "-P", f"node.name={app3}", str(TONE48)])
    time.sleep(1.2)
    r = sh(["pactl", "list", "sink-inputs"])
    idx3, cur = None, None
    for line in r["out"].decode().splitlines():
        m = re.match(r"^Sink Input #(\d+)", line)
        if m:
            cur = m.group(1)
        if "application.name" in line and app3 in line:
            idx3 = cur
    res["y_index"] = idx3
    if idx3:
        res["y_move"] = step("f2c", rep, "move", ["pactl", "move-sink-input", idx3, "r90b"])
        res["y_store_poll"] = poll_key(key3, timeout=6.0, field="target", want="r90b")
    res["y_stop"] = stop(p)

    # 5) passive link props vs normal link props
    A, B = "r90a:monitor_FL", "r90b:playback_FL"
    res["p_normal"] = step("f2c", rep, "link_normal", ["pw-link", A, B])
    objs = pw_dump()
    res["p_normal_links"] = [{"id": o["id"], "props": o.get("info", {}).get("props", {})}
                             for o in objs if o.get("type") == "PipeWire:Interface:Link"]
    sh(["pw-link", "-d", A, B])
    res["p_passive"] = step("f2c", rep, "link_passive", ["pw-link", "-P", A, B])
    objs = pw_dump()
    res["p_passive_links"] = [{"id": o["id"], "props": o.get("info", {}).get("props", {})}
                              for o in objs if o.get("type") == "PipeWire:Interface:Link"]
    # 6) pw-link -t with a live stream on the link
    p = spawn(["pw-play", "--target", "r90a", "-P", f"node.name=r90lat{rep}",
               "-P", f"application.name=r90lat{rep}", str(TONE48)])
    time.sleep(1.2)
    res["t_latency"] = step("f2c", rep, "latency", ["pw-link", "-t"])
    res["t_latency2"] = step("f2c", rep, "latency2", ["pw-link", "--latency"])
    res["t_list_pattern"] = step("f2c", rep, "list_pattern",
                                 ["pw-link", "-o", "r90a:*"])
    res["t_list_pattern2"] = step("f2c", rep, "list_pattern2",
                                  ["pw-link", "r90a:monitor_FL"])
    res["t_stop"] = stop(p)
    res["t_cleanup"] = step("f2c", rep, "cleanup", ["pw-link", "-d", A, B])

    # 7) capture leg with the r77-pinned stream.capture.sink prop
    app4 = f"r90k{rep}"
    key4 = f"Input/Audio:application.name:{app4}"
    p = spawn(["pw-record", "--target", "r90a", "-P", "stream.capture.sink=true",
               "-P", f"application.name={app4}", "-P", f"node.name={app4}", "/dev/null"])
    time.sleep(1.5)
    res["k_alive"] = p.poll() is None
    res["k_node"] = node_id(app4)
    res["k_stop"] = stop(p)
    res["k_store_poll"] = poll_key(key4, timeout=8.0)
    return res


def main():
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    out = {"stage": "f2c", "reps": reps, "entry_census": census(),
           "started": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "legs": []}
    mid, _, _ = load_null_sink("r90a")
    midb, _, _ = load_null_sink("r90b")
    time.sleep(0.5)
    for rep in range(1, reps + 1):
        t0 = time.time()
        try:
            r = stage_f2c(rep)
            r["_wall_s"] = round(time.time() - t0, 2)
        except Exception as e:
            import traceback
            r = {"error": f"{type(e).__name__}: {e}", "tb": traceback.format_exc()[-600:]}
        out["legs"].append({"rep": rep, **r})
        print(f"[f2c] rep{rep} {round(time.time()-t0,2)}s {'ERR' if 'error' in r else ''}", flush=True)
    out["teardown"] = {"a": unload(mid), "b": unload(midb)}
    time.sleep(0.4)
    out["exit_census"] = census()
    out["census_restored"] = out["entry_census"]["modules"] == out["exit_census"]["modules"]
    (REC / "f2c.json").write_text(json.dumps(out, indent=1))
    print("wrote", REC / "f2c.json")


if __name__ == "__main__":
    main()
