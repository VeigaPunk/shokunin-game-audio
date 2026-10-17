#!/usr/bin/env python3
"""r90 scout addendum D — per-rep seat-owned sinks (never unload by name):
  - pw-link -t latency lattice with a link, with and without a live stream
  - pw-link listing patterns (-o/-i/-l with globs)
  - passive link object props vs normal (pw-dump Link)
  - target-restore: store the 'target' field, then replay without --target
Receipts: receipts/f2d.json
"""
import json
import re
import signal
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from r90_probe import (ROOT, REC, census, load_null_sink, node_id,  # noqa
                       parse_stream_props, pw_dump, sh, spawn, step, stop,
                       unload)

TONE48, TONEQ = ROOT / "r90_tone48.wav", ROOT / "r90_toneq.wav"


def poll_target(key, want="r90b", timeout=8.0, poll=0.25):
    t0 = time.time()
    seen = []
    while time.time() - t0 < timeout:
        e = parse_stream_props()["entries"].get(key)
        seen.append((round(time.time() - t0, 2), json.dumps(e)[:70]))
        if isinstance(e, dict) and e.get("target") == want:
            return {"ok": True, "delay_s": round(time.time() - t0, 2), "entry": e}
        time.sleep(poll)
    return {"ok": False, "delay_s": None, "polls": seen[-2:]}


def sink_input_index(app):
    r = sh(["pactl", "list", "sink-inputs"])
    idx, cur = None, None
    for line in r["out"].decode().splitlines():
        m = re.match(r"^Sink Input #(\d+)", line)
        if m:
            cur = m.group(1)
        if "application.name" in line and app in line:
            idx = cur
    return idx


def stage_f2d(rep):
    res = {}
    mid_a, ra, _ = load_null_sink("r90a")
    mid_b, rb, _ = load_null_sink("r90b")
    res["setup"] = {"mid_a": mid_a, "mid_b": mid_b, "rc_a": ra["rc"], "rc_b": rb["rc"]}
    time.sleep(0.6)
    A, B = "r90a:monitor_FL", "r90b:playback_FL"

    # a) listing patterns
    res["pat_o_glob"] = step("f2d", rep, "o_glob", ["pw-link", "-o", "r90a:*"])
    res["pat_o_exact"] = step("f2d", rep, "o_exact", ["pw-link", "-o", A])
    res["pat_i_glob"] = step("f2d", rep, "i_glob", ["pw-link", "-i", "r90b:*"])
    res["pat_o_all"] = step("f2d", rep, "o_all", ["pw-link", "-o"])
    res["pat_star"] = step("f2d", rep, "o_star", ["pw-link", "-o", "*monitor_FL"])

    # b) normal vs passive link object props
    res["ln_normal"] = step("f2d", rep, "link_normal", ["pw-link", A, B])
    res["ln_normal_list"] = step("f2d", rep, "list_normal", ["pw-link", "-l"])
    res["ln_normal_dump"] = [{"id": o["id"], "props": o.get("info", {}).get("props", {})}
                             for o in pw_dump() if o.get("type") == "PipeWire:Interface:Link"]
    step("f2d", rep, "disc_normal", ["pw-link", "-d", A, B])
    res["ln_passive"] = step("f2d", rep, "link_passive", ["pw-link", "-P", A, B])
    res["ln_passive_dump"] = [{"id": o["id"], "props": o.get("info", {}).get("props", {})}
                              for o in pw_dump() if o.get("type") == "PipeWire:Interface:Link"]

    # c) pw-link -t with a link present, then with a live stream on it
    res["lat_link_only"] = step("f2d", rep, "lat_link_only", ["pw-link", "-t"])
    p = spawn(["pw-play", "--target", "r90a", "-P", f"node.name=r90lat{rep}",
               "-P", f"application.name=r90lat{rep}", str(TONE48)])
    time.sleep(1.2)
    res["lat_stream"] = step("f2d", rep, "lat_stream", ["pw-link", "-t"])
    res["lat_stream_list"] = step("f2d", rep, "lat_list", ["pw-link", "-l"])
    res["lat_stop"] = stop(p)
    step("f2d", rep, "disc_passive", ["pw-link", "-d", A, B])

    # d) target restore: store then replay
    app = f"r90t{rep}"
    key = f"Output/Audio:application.name:{app}"
    p = spawn(["pw-play", "--target", "r90a", "-P", f"application.name={app}",
               "-P", f"node.name={app}", str(TONE48)])
    time.sleep(1.2)
    idx = sink_input_index(app)
    res["t_index"] = idx
    if idx:
        res["t_move"] = step("f2d", rep, "move", ["pactl", "move-sink-input", idx, "r90b"])
        res["t_store_poll"] = poll_target(key)
        res["t_links_after_move"] = step("f2d", rep, "links_moved", ["pw-link", "-l"])
    res["t_stop"] = stop(p)
    # replay without --target (quiet tone, 0.6 s bound)
    p = spawn(["pw-play", "-P", f"application.name={app}", "-P", f"node.name={app}b", str(TONEQ)])
    time.sleep(0.55)
    res["t_replay_links"] = step("f2d", rep, "links_replay", ["pw-link", "-l"])
    res["t_replay_si"] = sink_input_index(f"{app}b")
    res["t_replay_meta"] = [m for m in pw_dump()
                            if m.get("type") == "PipeWire:Interface:Metadata"
                            and (m.get("props", {}) or {}).get("metadata.name") == "default"]
    res["t_replay_kill"] = stop(p, sig=signal.SIGKILL)

    res["teardown"] = {"a": unload(mid_a), "b": unload(mid_b)}
    time.sleep(0.3)
    res["nodes_after"] = [n["info"]["props"].get("node.name") for n in pw_dump()
                          if n.get("type") == "PipeWire:Interface:Node"
                          and str(n.get("info", {}).get("props", {}).get("node.name", "")).startswith("r90")]
    return res


def main():
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    out = {"stage": "f2d", "reps": reps, "entry_census": census(),
           "started": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "legs": []}
    for rep in range(1, reps + 1):
        t0 = time.time()
        try:
            r = stage_f2d(rep)
            r["_wall_s"] = round(time.time() - t0, 2)
        except Exception as e:
            import traceback
            r = {"error": f"{type(e).__name__}: {e}", "tb": traceback.format_exc()[-600:]}
        out["legs"].append({"rep": rep, **r})
        print(f"[f2d] rep{rep} {round(time.time()-t0,2)}s {'ERR' if 'error' in r else ''}", flush=True)
    out["exit_census"] = census()
    out["census_restored"] = out["entry_census"]["modules"] == out["exit_census"]["modules"]
    (REC / "f2d.json").write_text(json.dumps(out, indent=1))
    print("wrote", REC / "f2d.json")


if __name__ == "__main__":
    main()
