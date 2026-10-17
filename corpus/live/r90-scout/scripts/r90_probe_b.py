#!/usr/bin/env python3
"""r90 scout addendum — refinements for f2 (pulse module edges), f4 (pw-link
grammar), f6 (session-manager restore). Same receipt layout as r90_probe.py.

Stages: f2b | f4b | f6b   (>=3 reps/leg; all seat-owned objects torn down by ID)
"""
import json
import re
import signal
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from r90_probe import (ROOT, REC, RUNS, census, load_null_sink, module_ids,  # noqa
                       node_id, nodes_by_name, parse_stream_props, ports_of,
                       pw_dump, sh, spawn, step, stop, tone, unload,
                       wait_for_entry)

TONEQ = ROOT / "r90_toneq.wav"


def link_ids():
    """Parse pw-link -I -l: link ids live on the '|->' rows."""
    r = sh(["pw-link", "-I", "-l"])
    ids = []
    for line in r["out"].decode().splitlines():
        if "|->" in line:
            tok = line.split()
            if tok and tok[0].isdigit():
                ids.append(tok[0])
    return ids, r["out"].decode()


def link_count():
    r = sh(["pw-link", "-l"])
    return sum(1 for ln in r["out"].decode().splitlines() if "|->" in ln), r["out"].decode()


def module_alive(mid):
    return int(mid) in set(module_ids())


def metadata_entries(name):
    for o in pw_dump():
        if o.get("type") == "PipeWire:Interface:Metadata" and \
                (o.get("props", {}) or {}).get("metadata.name") == name:
            return o.get("metadata", [])
    return []


# ------------------------------------------------------------------ stage f2b
def stage_f2b(rep):
    res = {"entry_modules": module_ids()}

    # 1) tunnel self-destruct latency with an unreachable remote
    r = sh(["pactl", "load-module", "module-tunnel-sink",
            "server=127.0.0.1:1", "sink_name=r90tun2"])
    mid = r["out"].decode().strip()
    res["t1_load"] = {"rc": r["rc"], "id": mid, "err": r["err"].decode()[:80]}
    probes = []
    t0 = time.time()
    for delay in (0.0, 0.03, 0.06, 0.12, 0.25, 0.5, 1.0, 2.0):
        while time.time() - t0 < delay:
            time.sleep(0.005)
        probes.append({"t": round(time.time() - t0, 3),
                       "module_alive": module_alive(mid),
                       "sink_nodes": [n["info"]["props"].get("node.name")
                                      for n in nodes_by_name("r90tun2")],
                       "sink_in_pactl": "r90tun2" in sh(
                           ["pactl", "list", "sinks", "short"])["out"].decode()})
    res["t1_probes"] = probes
    res["t1_unload"] = unload(mid) if mid.isdigit() else None

    # 2) same, but with reconnect_interval_ms -> module should persist
    r = sh(["pactl", "load-module", "module-tunnel-sink", "server=127.0.0.1:1",
            "sink_name=r90tun3", "reconnect_interval_ms=1000"])
    mid2 = r["out"].decode().strip()
    res["t2_load"] = {"rc": r["rc"], "id": mid2, "err": r["err"].decode()[:80]}
    time.sleep(0.6)
    res["t2_alive_after_0.6s"] = module_alive(mid2) if mid2.isdigit() else None
    res["t2_node"] = [{"name": n["info"]["props"].get("node.name"),
                       "id": n["id"],
                       "props": {k: v for k, v in n["info"]["props"].items()
                                 if k in ("node.name", "node.description", "media.class",
                                          "factory.name", "device.api", "pulse.module.id",
                                          "node.driver", "tunnel.remote.name")}}
                      for n in nodes_by_name("r90tun3")]
    res["t2_pactl_sink"] = [l for l in sh(["pactl", "list", "sinks", "short"])["out"].decode().splitlines()
                            if "r90tun3" in l]
    res["t2_unload"] = unload(mid2) if mid2.isdigit() else None

    # 3) arg/class lattice for the remaining pulse module names
    for label, argv in (
            ("roc_sink_named", ["module-roc-sink", "sink_name=r90roc"]),
            ("roc_source", ["module-roc-source"]),
            ("raop_discover", ["module-raop-discover"]),
            ("zeroconf_discover_opt", ["module-zeroconf-discover", "latency_msec=100"]),
            ("tunnel_bad_server", ["module-tunnel-sink", "server="]),
            ("tunnel_no_server", ["module-tunnel-sink", "sink_name=r90tun4"]),
            ("pipe_tunnel", ["module-pipe-tunnel"]),
            ("switch_on_connect", ["module-switch-on-connect"]),
            ("rtp_send", ["module-rtp-send", "source=r90a.monitor"])):
        rr = sh(["pactl", "load-module"] + argv)
        out = rr["out"].decode().strip()
        rec = {"argv": argv, "rc": rr["rc"], "out": out[:40],
               "err": rr["err"].decode().strip()[:80]}
        if out.isdigit():
            rec["alive"] = module_alive(out)
            rec["r90_nodes"] = [n["info"]["props"].get("node.name")
                                for n in pw_dump()
                                if n.get("type") == "PipeWire:Interface:Node"
                                and str(n.get("info", {}).get("props", {}).get("node.name", "")).startswith("r90")]
            rec["unload"] = unload(out)
        res[label] = rec

    # 4) unload-by-name form (man page claims name or index accepted)
    r = sh(["pactl", "load-module", "module-null-sink", "sink_name=r90un"])
    mid3 = r["out"].decode().strip()
    res["un_by_name"] = {"loaded": mid3,
                         "unload_name": sh(["pactl", "unload-module", "module-null-sink"]).__dict__
                         if False else None}
    u = sh(["pactl", "unload-module", "module-null-sink"])
    res["un_by_name"]["rc"] = u["rc"]
    res["un_by_name"]["err"] = u["err"].decode().strip()[:80]
    res["un_by_name"]["still_alive"] = module_alive(mid3) if mid3.isdigit() else None
    if mid3.isdigit() and module_alive(mid3):
        res["un_by_name"]["unload_by_id"] = unload(mid3)
    res["exit_modules"] = module_ids()
    return res


# ------------------------------------------------------------------ stage f4b
def stage_f4b(rep):
    res = {}
    mid_a, _, _ = load_null_sink("r90a")
    mid_b, _, _ = load_null_sink("r90b")
    res["setup"] = {"mid_a": mid_a, "mid_b": mid_b}
    time.sleep(0.5)
    A, B = "r90a:monitor_FL", "r90b:playback_FL"
    A2, B2 = "r90a:monitor_FR", "r90b:playback_FR"

    # two links created one at a time, then bulk disconnect by 4 port names
    res["d1_link1"] = step("f4b", rep, "link1", ["pw-link", A, B])
    res["d1_link2"] = step("f4b", rep, "link2", ["pw-link", A2, B2])
    res["d1_count"] = link_count()
    ids, raw = link_ids()
    res["d1_ids"] = ids
    res["d1_bulk_disc_names"] = step("f4b", rep, "bulk_disc_names",
                                     ["pw-link", "-d", A, B, A2, B2])
    res["d1_count_after"] = link_count()

    # two links again, then disconnect by two link ids in one call
    step("f4b", rep, "link1b", ["pw-link", A, B])
    step("f4b", rep, "link2b", ["pw-link", A2, B2])
    ids2, raw2 = link_ids()
    res["d2_ids"] = ids2
    if len(ids2) >= 2:
        res["d2_disc_two_ids"] = step("f4b", rep, "disc_two_ids",
                                      ["pw-link", "-d", ids2[0], ids2[1]])
    res["d2_count_after"] = link_count()
    res["d2_remaining_ids"] = link_ids()[0]
    for i in link_ids()[0]:
        sh(["pw-link", "-d", i])

    # -w wait on a missing OUTPUT side
    res["w1_wait_missing_out"] = step("f4b", rep, "wait_missing_out",
                                      ["pw-link", "-w", "r90a:monitor_ZZ", B], timeout=2)
    # passive link + link object witness
    res["p1_passive"] = step("f4b", rep, "passive", ["pw-link", "-P", A, B])
    objs = pw_dump()
    res["p1_link_objects"] = [{"id": o["id"],
                               "props": {k: v for k, v in (o.get("info", {}).get("props", {}) or {}).items()
                                         if k in ("link.output.port", "link.input.port",
                                                  "link.passive", "link.state", "object.serial")}}
                              for o in objs if o.get("type") == "PipeWire:Interface:Link"]
    res["p1_latency"] = step("f4b", rep, "latency", ["pw-link", "-t"])
    res["p1_cleanup"] = step("f4b", rep, "cleanup", ["pw-link", "-d", A, B])
    res["p1_after"] = link_count()
    res["teardown"] = {"a": unload(mid_a) if mid_a else None,
                       "b": unload(mid_b) if mid_b else None}
    time.sleep(0.3)
    res["r90_nodes_after"] = [n["info"]["props"].get("node.name")
                              for n in pw_dump() if n.get("type") == "PipeWire:Interface:Node"
                              and str(n.get("info", {}).get("props", {}).get("node.name", "")).startswith("r90")]
    return res


# ------------------------------------------------------------------ stage f6b
def store_entry(key):
    try:
        return parse_stream_props()["entries"].get(key)
    except Exception as e:
        return {"_error": str(e)}


def poll_value(key, field, want, timeout=12.0, poll=0.4):
    t0 = time.time()
    seen = []
    while time.time() - t0 < timeout:
        v = store_entry(key)
        seen.append((round(time.time() - t0, 2), json.dumps(v)[:80]))
        if isinstance(v, dict) and abs(float(v.get(field, -1)) - want) < 1e-6:
            return {"ok": True, "delay_s": round(time.time() - t0, 2), "value": v, "polls": seen}
        time.sleep(poll)
    return {"ok": False, "delay_s": None, "last": seen[-1] if seen else None, "polls": seen}


def sink_input_index(app):
    r = sh(["pactl", "list", "sink-inputs"])
    idx, cur = None, None
    for line in r["out"].decode().splitlines():
        m = re.match(r"^Sink Input #(\d+)", line)
        if m:
            cur = m.group(1)
        if "application.name" in line and app in line:
            idx = cur
    return idx, r["out"].decode()


def stage_f6b(rep):
    res = {}
    mid_a, _, _ = load_null_sink("r90a")
    mid_b, _, _ = load_null_sink("r90b")
    res["setup"] = {"mid_a": mid_a, "mid_b": mid_b}
    time.sleep(0.5)

    # A) pw-cli Props write -> is it stored?  (long window)
    app = f"r90u{rep}"
    key = f"Output/Audio:application.name:{app}"
    p = spawn(["pw-play", "--target", "r90a", "-P", f"application.name={app}",
               "-P", f"node.name={app}", str(ROOT / "r90_tone48.wav")])
    time.sleep(1.0)
    nid = node_id(app)
    res["a_setparam"] = step("f6b", rep, "setvol_cli",
                             ["pw-cli", "set-param", str(nid), "Props", "{ volume: 0.5 }"])
    res["a_live_props"] = step("f6b", rep, "live_props",
                               ["pw-cli", "enum-params", str(nid), "Props"])
    res["a_store_poll"] = poll_value(key, "volume", 0.5, timeout=6.0)
    res["a_stop"] = stop(p)

    # B) pulse-path volume write -> is that stored?
    app_b = f"r90s{rep}"
    key_b = f"Output/Audio:application.name:{app_b}"
    p = spawn(["pw-play", "--target", "r90a", "-P", f"application.name={app_b}",
               "-P", f"node.name={app_b}", str(ROOT / "r90_tone48.wav")])
    time.sleep(1.2)
    idx, listing = sink_input_index(app_b)
    res["b_index"] = idx
    if idx:
        res["b_setvol"] = step("f6b", rep, "setvol_pactl",
                               ["pactl", "set-sink-input-volume", idx, "50%"])
        res["b_store_poll"] = poll_value(key_b, "volume", 0.5, timeout=8.0)
        res["b_live"] = step("f6b", rep, "si_list", ["pactl", "list", "sink-inputs", "short"])
    res["b_stop"] = stop(p)

    # C) read side: replay same app name, no --volume, witness live Props
    p = spawn(["pw-play", "--target", "r90a", "-P", f"application.name={app_b}",
               "-P", f"node.name={app_b}b", str(ROOT / "r90_tone48.wav")])
    time.sleep(1.2)
    nid3 = node_id(f"{app_b}b")
    res["c_replay_node"] = nid3
    if nid3:
        res["c_replay_props"] = step("f6b", rep, "replay_props",
                                     ["pw-cli", "enum-params", str(nid3), "Props"])
    res["c_stop"] = stop(p)

    # D) target store + restore (metadata witness; quiet tone; fast kill)
    app_t = f"r90z{rep}"
    key_t = f"Output/Audio:application.name:{app_t}"
    p = spawn(["pw-play", "--target", "r90a", "-P", f"application.name={app_t}",
               "-P", f"node.name={app_t}", str(ROOT / "r90_tone48.wav")])
    time.sleep(1.2)
    idx_t, _ = sink_input_index(app_t)
    res["d_index"] = idx_t
    if idx_t:
        res["d_move"] = step("f6b", rep, "move", ["pactl", "move-sink-input", idx_t, "r90b"])
        time.sleep(0.5)
        res["d_links_moved"] = step("f6b", rep, "links_moved", ["pw-link", "-l"])
    res["d_store_poll"] = poll_value(key_t, "volume", 1.0, timeout=0.1)
    res["d_entry_after_move"] = store_entry(key_t)
    res["d_stop"] = stop(p)
    # replay with NO --target: does the stored target win?
    p = spawn(["pw-play", "-P", f"application.name={app_t}", "-P", f"node.name={app_t}b",
               str(TONEQ)])
    time.sleep(0.45)
    nid_r = node_id(f"{app_t}b")
    res["d_replay_node"] = nid_r
    res["d_replay_links"] = step("f6b", rep, "links_replay", ["pw-link", "-l"])
    res["d_replay_si"] = sink_input_index(f"{app_t}b")[0]
    res["d_replay_meta"] = [m for m in metadata_entries("default")
                            if m.get("subject") and m.get("key") == "target.object"]
    res["d_replay_kill"] = stop(p, sig=signal.SIGKILL)
    time.sleep(0.3)

    # E) capture-direction key discovery
    app_c = f"r90g{rep}"
    before = set(parse_stream_props()["entries"])
    p = spawn(["pw-record", "--target", "r90a", "-P", f"application.name={app_c}",
               "-P", f"node.name={app_c}", "/dev/null"])
    time.sleep(1.5)
    nid_c = node_id(app_c)
    res["e_capture_node"] = nid_c
    if nid_c:
        res["e_capture_props"] = step("f6b", rep, "capture_props",
                                      ["pw-cli", "info", str(nid_c)])
    res["e_stop"] = stop(p)
    time.sleep(1.0)
    after = set(parse_stream_props()["entries"])
    res["e_new_keys"] = sorted(after - before)
    res["e_capture_keys"] = sorted(k for k in after if app_c in k or "r90g" in k)

    # F) device-node opt-out (sink_properties=state.restore-props=false)
    name_o = f"r90o{rep}"
    r = sh(["pactl", "load-module", "module-null-sink", f"sink_name={name_o}",
            "sink_properties=state.restore-props=false"])
    mid_o = r["out"].decode().strip()
    res["f_load"] = {"rc": r["rc"], "id": mid_o, "err": r["err"].decode()[:80]}
    time.sleep(1.0)
    res["f_entry_present"] = f"Audio/Sink:node.name:{name_o}" in parse_stream_props()["entries"]
    res["f_node_props"] = step("f6b", rep, "optout_props",
                               ["pw-cli", "info", str(node_id(name_o))]) if node_id(name_o) else None
    res["f_unload"] = unload(mid_o) if mid_o.isdigit() else None
    # control: same sink without the opt-out property
    name_c = f"r90q{rep}"
    r = sh(["pactl", "load-module", "module-null-sink", f"sink_name={name_c}"])
    mid_c = r["out"].decode().strip()
    time.sleep(1.0)
    res["f_control_entry_present"] = f"Audio/Sink:node.name:{name_c}" in parse_stream_props()["entries"]
    res["f_control_unload"] = unload(mid_c) if mid_c.isdigit() else None

    res["teardown"] = {"a": unload(mid_a) if mid_a else None,
                       "b": unload(mid_b) if mid_b else None}
    res["r90_store_keys"] = sorted(k for k in parse_stream_props()["entries"] if "r90" in k)
    return res


STAGE_FN = {"f2b": stage_f2b, "f4b": stage_f4b, "f6b": stage_f6b}


def main():
    stage = sys.argv[1]
    reps = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    tone(TONEQ, 48000, secs=3.0, freq=660.0)
    out = {"stage": stage, "reps": reps, "entry_census": census(),
           "started": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "legs": []}
    for rep in range(1, reps + 1):
        t0 = time.time()
        try:
            r = STAGE_FN[stage](rep)
            r["_wall_s"] = round(time.time() - t0, 2)
        except Exception as e:
            import traceback
            r = {"error": f"{type(e).__name__}: {e}", "tb": traceback.format_exc()[-600:]}
        out["legs"].append({"rep": rep, **r})
        print(f"[{stage}] rep{rep} {round(time.time()-t0,2)}s {'ERR' if 'error' in r else ''}",
              flush=True)
    out["exit_census"] = census()
    out["census_restored"] = out["entry_census"]["modules"] == out["exit_census"]["modules"]
    (REC / f"{stage}.json").write_text(json.dumps(out, indent=1))
    print("wrote", REC / f"{stage}.json")


if __name__ == "__main__":
    main()
