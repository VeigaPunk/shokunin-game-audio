#!/usr/bin/env python3
"""r84b follow-up — targeted falsification legs:
1) empty-device-arg divergence (aplay vs arecord) two-form test
2) capture node witness during plugin NODE= capture (claim: alsa_capture.aplay)
3) EXCLUSIVE=1 arg-form matrix
4) speaker-test plugin leg with natural exit (no early kill)
5) bare plugin capture shape hunt across formats/rates
6) null-capture period law across rates (period-dependent?)
Reuses r84b_probe helpers. Namespace r84b_*. No tracked writes.
"""
import json, os, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r84b_probe as R

PROBE = "pF2-followup"

def main():
    results = {"loadavg_start": R.loadavg(), "default_sink": R.default_sink()}
    # ---- 1) empty-device two-form ----
    legs = [
        ("empty_bash_real",   ["bash", "-c", "arecord -D '' -d 1 -f cd /tmp/r84b_ef1.wav"]),
        ("empty_bash_dropped",["bash", "-c", "arecord -D -d 1 -f cd /tmp/r84b_ef2.wav"]),
        ("empty_execve_real", ["arecord", "-D", "", "-d", "1", "-f", "cd", "/tmp/r84b_ef3.wav"]),
        ("empty_execve_dropped", ["arecord", "-D", "-d", "1", "-f", "cd", "/tmp/r84b_ef4.wav"]),
        ("empty_aplay_real",  ["bash", "-c", "aplay -D '' " + R.tone_short()]),
        ("empty_aplay_dropped", ["bash", "-c", "aplay -D -d 1 " + R.tone_short()]),
    ]
    for name, argv in legs:
        reps = []
        for rep in range(1):
            res = R.run(argv, 6)
            R.record_leg(PROBE, name, rep, res, {"loadavg": R.loadavg()})
            reps.append(R.compact(res))
            print(f"{name:22s} rc={res['rc']} err1={res['err'].splitlines()[:1]}")
        results[name] = reps
    # ---- 2) capture node witness during plugin NODE= capture ----
    out = R.TMP / "fw_node.wav"
    p = R.Proc(["arecord", "-D", f"pipewire:NODE={R.LINE}", "-d", "3", "-f", "cd", str(out)])
    time.sleep(1.2)
    nodes = []
    for o in R.pw_dump():
        if o.get("type") != "PipeWire:Interface:Node": continue
        pr = o.get("info", {}).get("props", {}) or {}
        blob = f"{pr.get('node.name','')} {pr.get('application.name','')} {pr.get('media.class','')}"
        if any(s in blob for s in ("aplay", "capture", "arecord", "Stream/Input")):
            nodes.append({"name": pr.get("node.name"), "media.class": pr.get("media.class"),
                          "app": pr.get("application.name"), "target.object": pr.get("target.object"),
                          "state": o.get("info", {}).get("state"), "id": o.get("id")})
    so = [{"index": x.get("index"), "app": (x.get("properties") or {}).get("application.name"),
           "node": (x.get("properties") or {}).get("node.name")} for x in R.pactl_json("source-outputs")]
    fin = p.finish()
    res = {"rc": fin["rc"], "wall": fin["wall"], "out": fin["out"], "err": fin["err"],
           "timeout": False, "cmd": f"arecord -D pipewire:NODE={R.LINE} -d 3 -f cd <out>"}
    extra = {"nodes_during": nodes, "source_outputs_during": so, "hdr": R.file_hdr(out),
             "loadavg": R.loadavg()}
    R.record_leg(PROBE, "capture_node_witness", 0, res, extra)
    results["capture_node_witness"] = R.compact(res, extra)
    print(f"capture_node_witness   rc={fin['rc']} size={extra['hdr']['size']} nodes={[n['name'] for n in nodes]}")
    print(f"   source-outputs: {so}")
    # ---- 3) EXCLUSIVE forms ----
    s1 = R.load_ns(R.NS)
    assert s1["verified"], s1
    try:
        for name, argv in [
            ("excl_node1", ["aplay", "-D", f"pipewire:NODE={R.NS},EXCLUSIVE=1", R.tone_short()]),
            ("excl_node0", ["aplay", "-D", f"pipewire:NODE={R.NS},EXCLUSIVE=0", R.tone_short()]),
            ("excl_bare1", ["aplay", "-D", "pipewire:EXCLUSIVE=1", R.tone_short()]),
            ("excl_bare1_ns", ["aplay", "-D", f"pipewire:NODE={R.NS}", R.tone_short()]),
        ]:
            reps = []
            for rep in range(2):
                res, w = R.during(PROBE, name, rep, argv, wait=0.5,
                                  witness=lambda: R.witness_nodes("alsa_playback"))
                R.record_leg(PROBE, name, rep, res, {"witness": w, "loadavg": R.loadavg()})
                reps.append(R.compact(res, {"nodes": [n["name"] for n in w],
                                            "target": [n["props"].get("target.object") for n in w]}))
            results[name] = reps
            print(f"{name:14s} rc={[x['rc'] for x in reps]} err_last={reps[0]['err'][-1:]}")
        # ---- 4) speaker-test natural exit ----
        reps = []
        for rep in range(2):
            p = R.Proc(["speaker-test", "-D", f"pipewire:NODE={R.NS}", "-c", "2", "-l", "1",
                        "-t", "sine", "-S", "5"])
            time.sleep(1.0)
            w = R.witness_nodes("speaker-test")
            for _ in range(140):
                if not p.alive(): break
                time.sleep(0.1)
            fin = p.finish()
            res = {"rc": fin["rc"], "wall": fin["wall"], "out": fin["out"], "err": fin["err"],
                   "timeout": False, "cmd": f"speaker-test -D pipewire:NODE={R.NS} -c 2 -l 1 -t sine -S 5"}
            extra = {"nodes": w, "loadavg": R.loadavg()}
            R.record_leg(PROBE, "st_natural", rep, res, extra)
            reps.append(R.compact(res, {"nodes": [n["name"] for n in w]}))
            print(f"st_natural rep{rep} rc={fin['rc']} wall={fin['wall']} nodes={[n['name'] for n in w]}")
        results["st_natural"] = reps
        # ---- 5) bare plugin capture shape hunt ----
        for name, argv in [
            ("hunt_dat",      ["arecord", "-D", "pipewire", "-d", "2", "-f", "dat", str(R.TMP / "h_dat.wav")]),
            ("hunt_f32_48",   ["arecord", "-D", "pipewire", "-d", "2", "-f", "FLOAT_LE", "-r", "48000", str(R.TMP / "h_f32.wav")]),
            ("hunt_c1",       ["arecord", "-D", "pipewire", "-d", "2", "-c", "1", "-f", "cd", str(R.TMP / "h_c1.wav")]),
            ("hunt_u8",       ["arecord", "-D", "pipewire", "-d", "2", "-f", "U8", "-r", "8000", "-c", "1", str(R.TMP / "h_u8.wav")]),
            ("hunt_def_dat",  ["arecord", "-D", "default", "-d", "2", "-f", "dat", str(R.TMP / "h_ddat.wav")]),
            ("hunt_node_dat", ["arecord", "-D", f"pipewire:NODE={R.LINE}", "-d", "2", "-f", "dat", str(R.TMP / "h_ndat.wav")]),
        ]:
            reps = []
            for rep in range(1):
                res = R.run(argv, 10)
                extra = {"hdr": R.file_hdr(argv[-1]), "loadavg": R.loadavg()}
                R.record_leg(PROBE, name, rep, res, extra)
                reps.append(R.compact(res, extra))
                print(f"{name:14s} rc={res['rc']} size={extra['hdr']['size']} "
                      f"first={res['err'].splitlines()[:1]} last={res['err'].splitlines()[-1:]}")
            results[name] = reps
        # ---- 6) null period law across rates ----
        for name, argv in [
            ("null_r48000", ["arecord", "-D", "null", "-d", "1", "-f", "S16_LE", "-r", "48000", "-c", "2", str(R.TMP / "n48.wav")]),
            ("null_r8000",  ["arecord", "-D", "null", "-d", "1", "-f", "S16_LE", "-r", "8000", "-c", "1", str(R.TMP / "n8.wav")]),
        ]:
            res = R.run(argv, 8)
            nz = R.nz_stats(argv[-1])
            extra = {"nz": nz, "hdr": R.file_hdr(argv[-1])}
            R.record_leg(PROBE, name, 0, res, extra)
            results[name] = R.compact(res, extra)
            print(f"{name:14s} rc={res['rc']} nz={nz}")
        (R.RCPTS / "pF2-followup.json").write_text(json.dumps(results, indent=1))
    finally:
        R.unload_idx(s1["idx"], R.NS)
    print("DONE followup")

if __name__ == "__main__":
    sys.exit(main() or 0)
