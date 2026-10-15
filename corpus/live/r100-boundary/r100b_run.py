#!/usr/bin/env python3
"""r100b runner — arms, own-hog lifecycle, incremental receipts.

Usage: r100b_run.py <arm> [stage ...]
  arm: quiet | load | axes | timing | all
Every stage writes corpus/live/r100-boundary/receipts/<arm>-<stage>.json after
EACH leg, so a crash cannot lose measured rows. Own PIDs only; foreign objects
are counted in the census and never signalled (r95 sweep incident precedent).
"""
import json
import os
import signal
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "probes"))
import r100b_sofa as P  # noqa: E402

REC = os.path.join(HERE, "receipts")
RUNS = os.path.join(HERE, "runs")
HOG = os.path.join(HERE, "probes", "r100b_hog.py")
os.makedirs(REC, exist_ok=True)
os.makedirs(RUNS, exist_ok=True)

STATE = {"hogs": [], "stop": False}


# ------------------------------------------------------------------ hog layer
def starttime(pid):
    try:
        with open("/proc/%d/stat" % pid) as f:
            return f.read().rsplit(") ", 1)[1].split()[19]
    except Exception:
        return None


def comm(pid):
    try:
        with open("/proc/%d/comm" % pid) as f:
            return f.read().strip()
    except Exception:
        return None


def spawn_hogs(n):
    for i in range(n):
        p = subprocess.Popen(["python3", HOG], stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL,
                             start_new_session=True)
        STATE["hogs"].append({"pid": p.pid, "starttime": starttime(p.pid),
                              "comm": comm(p.pid), "idx": i, "popen": p})
    time.sleep(2.0)
    return [{k: h[k] for k in ("pid", "starttime", "comm", "idx")} for h in STATE["hogs"]]


def kill_hogs():
    out = {"attempted": [], "refused": [], "remaining": []}
    for h in STATE["hogs"]:
        pid = h["pid"]
        if comm(pid) == h["comm"] and starttime(pid) == h["starttime"]:
            try:
                os.kill(pid, signal.SIGKILL)
                out["attempted"].append(pid)
            except Exception as e:
                out["refused"].append({"pid": pid, "err": repr(e)})
        else:
            out["refused"].append({"pid": pid, "reason": "identity-changed",
                                   "comm": comm(pid), "starttime": starttime(pid)})
    time.sleep(1.0)
    for h in STATE["hogs"]:
        p = h.get("popen")
        try:
            p.wait(timeout=3)          # reap: a SIGKILLed child is a zombie until waited
        except Exception:
            pass
        if comm(h["pid"]) is not None:
            out["remaining"].append(h["pid"])
    STATE["hogs"] = []
    return out


def loadavg_watch(path, period=2.0):
    def run():
        while not STATE["stop"]:
            try:
                la = P.loadavg()
                with open(path, "a") as f:
                    f.write(json.dumps({"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                        "load1": la["l1"], "load5": la["l5"],
                                        "load15": la["l15"],
                                        "own_hogs": len(STATE["hogs"])}) + "\n")
            except Exception:
                pass
            time.sleep(period)
    t = threading.Thread(target=run, daemon=True)
    t.start()
    return t


# ---------------------------------------------------------------------- stages
def leg(spec, max_tries=2, attempts_out=None):
    """One leg with one retry on a zero-frame capture (a rig flake, r98 §3.5 class).

    A zero-frame capture is a *client* failure (pw-record/pw-play died before
    producing data), not a property of the cell; the retry is disclosed in the row
    (`retry_of` / `attempt`) and counted in the report's flake census.
    """
    first = P.run_leg(**spec)
    if (first.get("analysis") or {}).get("frames"):
        return first
    spec2 = dict(spec)
    spec2["tag"] = (spec.get("tag") or ("%s_r%d" % (spec["name"], spec.get("rep", 0)))) + "_retry"
    second = P.run_leg(**spec2)
    second["retry_of"] = first.get("utc")
    second["first_attempt_frames"] = 0
    if attempts_out is not None:
        attempts_out.append(first)
    return second


def stage_replay(arm, only=None):
    """The r100 scout's armed cells, replayed with fresh processes."""
    for stage, legs in STAGES_REPLAY.items():
        if only and stage not in only:
            continue
        rows = []
        for spec in legs:
            row = leg(spec)
            rows.append(row)
            P.write_json(os.path.join(REC, "%s-%s.json" % (arm, stage)), rows)
            a = row.get("analysis", {})
            print("[%s/%s] %-18s r%d ild=%-8s rms=%s wall=%s load1=%s" % (
                arm, stage, row["leg"], row["rep"], a.get("ild_db"),
                [c["rms"] for c in a.get("channels", [])], row.get("wall_s"),
                row["loadavg_end"]["l1"]), flush=True)


STAGES_REPLAY = {
    "gate": [
        {"name": "noconfig_48k", "rate": 48000, "az": None, "tok": "{type=sofa,name=s0,label=spatializer}"},
        {"name": "sofa_48k", "rate": 48000, "az": None, "rep": 0},
        {"name": "sofa_44k_az0", "rate": 44100, "az": 0.0, "el": 0.0, "radius": 1.0},
    ],
    "azimuth": [{"name": "sofa_44k_az%d" % int(az), "rate": 44100, "az": az, "el": 0.0,
                 "radius": 1.0, "rep": rep}
                for az in (0.0, 90.0, 270.0) for rep in range(3)],
    "extra": ([{"name": "sofa_48k_az90", "rate": 48000, "az": 90.0, "el": 0.0,
                "radius": 1.0, "rep": rep} for rep in range(3)]
              + [{"name": "sofa_44k_az180", "rate": 44100, "az": 180.0, "el": 0.0,
                  "radius": 1.0, "rep": rep} for rep in range(2)]),
    # the scout's EXACT foreground shape (`pw-play --target`, no explicit node name,
    # no manual link): does it reproduce under a fresh process / under load?
    "fgprobe": ([{"name": "fg_az0", "rate": 44100, "az": 0.0, "el": 0.0, "radius": 1.0,
                  "play": "fg", "rep": rep} for rep in range(3)]
                + [{"name": "fg_az90", "rate": 44100, "az": 90.0, "el": 0.0, "radius": 1.0,
                    "play": "fg", "rep": rep} for rep in range(3)]),
    # the scout armed the rate-mismatch cell ONCE (n=1). Repeat it 5x, plus two
    # higher-rate cells, to test whether that cell is reproducible at all.
    "mismatch": ([{"name": "sofa_48k_rep%d" % rep, "rate": 48000, "az": None, "rep": rep}
                  for rep in range(5)]
                 + [{"name": "sofa_96k_rep%d" % rep, "rate": 96000, "az": None, "rep": rep}
                    for rep in range(2)]),
}


def stage_axes(arm="axes", only=None):
    stages = {}

    # 1. argv token order / node-spec order / quoting
    stages["argvorder"] = (
        [{"name": "order_base", "rate": 44100, "az": 90.0, "el": 0.0, "radius": 1.0,
          "argv_order": o, "rep": rep}
         for o in ("base", "reversed", "graph_last", "props_first", "rates_first")
         for rep in range(2)]
        + [{"name": "ctl_first", "rate": 44100, "az": 90.0, "el": 0.0, "radius": 1.0,
            "ctl_order": "control_first", "rep": rep} for rep in range(2)]
        + [{"name": "quoted", "rate": 44100, "az": 90.0, "el": 0.0, "radius": 1.0,
            "quote": True, "rep": rep} for rep in range(2)]
        + [{"name": "no_desc", "rate": 44100, "az": 90.0, "el": 0.0, "radius": 1.0,
            "rep": rep, "argv_order": "props_first"} for rep in range(1)])

    # 2. control value forms + curve shape
    stages["azcurve"] = (
        [{"name": "az_%d" % int(a), "rate": 44100, "az": a, "el": 0.0, "radius": 1.0,
          "rep": rep} for a in (45.0, 135.0, 225.0, 315.0) for rep in range(1)]
        + [{"name": "az_int_90", "rate": 44100, "az": 90, "el": 0.0, "radius": 1.0,
            "rep": rep} for rep in range(2)]
        + [{"name": "az_450", "rate": 44100, "az": 450.0, "el": 0.0, "radius": 1.0,
            "rep": rep} for rep in range(1)]
        + [{"name": "az_neg90", "rate": 44100, "az": -90.0, "el": 0.0, "radius": 1.0,
            "rep": rep} for rep in range(1)])

    # 3. rate ladder (file is 44100) — IR resample law
    stages["rates"] = [{"name": "fc_%d_az90" % r, "rate": r, "az": 90.0, "el": 0.0,
                        "radius": 1.0, "rep": rep}
                       for r in (22050, 48000, 88200, 96000) for rep in range(1)]

    # 4. extra config keys (gain / normalize / blocksize / tailsize)
    stages["cfgkeys"] = (
        [{"name": "gain050", "rate": 44100, "az": 90.0, "el": 0.0, "radius": 1.0,
          "extra_cfg": {"gain": "0.5"}, "rep": 0},
         {"name": "gain200", "rate": 44100, "az": 90.0, "el": 0.0, "radius": 1.0,
          "extra_cfg": {"gain": "2.0"}, "rep": 0},
         {"name": "normalize_true", "rate": 44100, "az": 90.0, "el": 0.0, "radius": 1.0,
          "extra_cfg": {"normalize": "true"}, "rep": 0},
         {"name": "blocksize128", "rate": 44100, "az": 90.0, "el": 0.0, "radius": 1.0,
          "extra_cfg": {"blocksize": "128"}, "rep": 0},
         {"name": "tailsize2048", "rate": 44100, "az": 90.0, "el": 0.0, "radius": 1.0,
          "extra_cfg": {"tailsize": "2048"}, "rep": 0},
         {"name": "latency256", "rate": 44100, "az": 90.0, "el": 0.0, "radius": 1.0,
          "extra_cfg": {"latency": "256"}, "rep": 0},
         {"name": "default_sofa", "rate": 44100, "az": 90.0, "el": 0.0, "radius": 1.0,
          "extra_cfg": {"filename": P.DEFAULT_SOFA}, "rep": 0}]
        + [{"name": "elev90", "rate": 44100, "az": 0.0, "el": 90.0, "radius": 1.0, "rep": 0},
           {"name": "radius05", "rate": 44100, "az": 90.0, "el": 0.0, "radius": 0.5, "rep": 0},
           {"name": "radius30", "rate": 44100, "az": 90.0, "el": 0.0, "radius": 3.0, "rep": 0}])

    # 5. rig-artifact falsifiers: channel swap + reference tap + multi-tone
    stages["rigart"] = (
        [{"name": "swap_az90", "rate": 44100, "az": 90.0, "el": 0.0, "radius": 1.0,
          "swap_channels": True, "rep": rep} for rep in range(2)]
        + [{"name": "swap_az0", "rate": 44100, "az": 0.0, "el": 0.0, "radius": 1.0,
            "swap_channels": True, "rep": rep} for rep in range(1)]
        + [{"name": "reftap_az0", "rate": 44100, "az": 0.0, "el": 0.0, "radius": 1.0,
            "ref_tap": True, "rep": rep} for rep in range(1)]
        + [{"name": "reftap_az90", "rate": 44100, "az": 90.0, "el": 0.0, "radius": 1.0,
            "ref_tap": True, "rep": rep} for rep in range(1)]
        + [{"name": "multi_az0", "rate": 44100, "az": 0.0, "el": 0.0, "radius": 1.0,
            "tone_freq": 997.0, "rep": rep} for rep in range(1)]
        + [{"name": "multi_az180", "rate": 44100, "az": 180.0, "el": 0.0, "radius": 1.0,
            "tone_freq": 997.0, "rep": rep} for rep in range(1)])

    # 6. sibling presence
    stages["sibling"] = (
        [{"name": "sib_az90", "rate": 44100, "az": 90.0, "el": 0.0, "radius": 1.0,
          "sib": 48000, "rep": rep} for rep in range(2)]
        + [{"name": "sib_az0", "rate": 44100, "az": 0.0, "el": 0.0, "radius": 1.0,
            "sib": 48000, "rep": rep} for rep in range(1)])

    for stage, legs in stages.items():
        if only and stage not in only:
            continue
        rows = []
        for spec in legs:
            row = leg(spec)
            rows.append(row)
            P.write_json(os.path.join(REC, "%s-%s.json" % (arm, stage)), rows)
            a = row.get("analysis", {})
            print("[%s/%s] %-18s r%d ild=%-8s rms=%s wall=%s" % (
                arm, stage, row["leg"], row["rep"], a.get("ild_db"),
                [c["rms"] for c in a.get("channels", [])], row.get("wall_s")), flush=True)


def stage_timing(arm="timing"):
    stages = {
        "runtime": [
            {"name": "rt_az0_to_90", "rate": 44100, "az": 0.0, "el": 0.0, "radius": 1.0,
             "play": "bg", "tone_secs": 5.0, "rec_secs": 5.5, "save_series": True,
             "post": [{"t": 1.2, "do": "set_azimuth", "node": P.FC_IN, "key": "Azimuth",
                       "value": 90.0}], "rep": 0},
            {"name": "rt_az90_to_270", "rate": 44100, "az": 90.0, "el": 0.0, "radius": 1.0,
             "play": "bg", "tone_secs": 5.0, "rec_secs": 5.5, "save_series": True,
             "post": [{"t": 1.2, "do": "set_azimuth", "node": P.FC_IN, "key": "Azimuth",
                       "value": 270.0}], "rep": 0},
        ],
        "sourceloss": [
            {"name": "kill_src_az90", "rate": 44100, "az": 90.0, "el": 0.0, "radius": 1.0,
             "play": "bg", "tone_secs": 4.0, "rec_secs": 5.0, "save_series": True,
             "post": [{"t": 1.5, "do": "kill_source"}], "rep": 0},
        ],
        "relink": [
            {"name": "relink_out_az90", "rate": 44100, "az": 90.0, "el": 0.0, "radius": 1.0,
             "play": "bg", "tone_secs": 4.0, "rec_secs": 5.0, "save_series": True,
             "post": [{"t": 1.2, "do": "relink_out"}], "rep": 0},
            {"name": "relink_in_az90", "rate": 44100, "az": 90.0, "el": 0.0, "radius": 1.0,
             "play": "bg", "tone_secs": 4.0, "rec_secs": 5.0, "save_series": True,
             "post": [{"t": 1.2, "do": "relink_in"}], "rep": 0},
        ],
        "driverdrop": [
            {"name": "drop_driver_az90", "rate": 44100, "az": 90.0, "el": 0.0, "radius": 1.0,
             "play": "bg", "tone_secs": 4.0, "rec_secs": 5.0, "save_series": True,
             "post": [{"t": 1.2, "do": "drop_driver"}], "rep": 0},
        ],
        "unloadfc": [
            {"name": "unload_fc_az90", "rate": 44100, "az": 90.0, "el": 0.0, "radius": 1.0,
             "play": "bg", "tone_secs": 4.0, "rec_secs": 5.0, "save_series": True,
             "post": [{"t": 1.2, "do": "unload_fc"}], "rep": 0},
        ],
    }
    for stage, legs in stages.items():
        if only and stage not in only:
            continue
        rows = []
        for spec in legs:
            row = leg(spec)
            rows.append(row)
            P.write_json(os.path.join(REC, "%s-%s.json" % (arm, stage)), rows)
            a = row.get("analysis", {})
            print("[%s/%s] %-18s ild=%-8s rms=%s post=%s" % (
                arm, stage, row["leg"], a.get("ild_db"),
                [c["rms"] for c in a.get("channels", [])],
                [e.get("action") for e in row.get("post_events", [])]), flush=True)


# ------------------------------------------------------------------------ main
def main():
    arm = sys.argv[1] if len(sys.argv) > 1 else "quiet"
    stages = sys.argv[2:] or None
    P.write_json(os.path.join(REC, "census-entry-%s.json" % arm), P.census())
    la_path = os.path.join(REC, "loadavg-%s.jsonl" % arm)
    loadavg_watch(la_path)
    entry = None
    try:
        if arm in ("load", "all", "mismatchload"):
            n = 16
            entry = {"hogs": spawn_hogs(n), "loadavg": P.loadavg()}
            P.write_json(os.path.join(REC, "hogs-%s.json" % arm), entry)
            print("spawned %d hogs, loadavg %s" % (n, entry["loadavg"]), flush=True)
        if arm in ("quiet", "load", "all"):
            if stages is None or any(s in STAGES_REPLAY for s in (stages or [])):
                stage_replay(arm)
        if arm in ("mismatch", "mismatchload"):
            stage_replay(arm, only=["mismatch"])
        if arm in ("axes", "all"):
            stage_axes("axes")
        if arm == "axes2":
            stage_axes("axes2", only=["rigart", "argvorder"])
        if arm in ("timing", "all"):
            stage_timing("timing")
    finally:
        STATE["stop"] = True
        killed = kill_hogs()
        P.write_json(os.path.join(REC, "hog-kill-%s.json" % arm), killed)
        P.write_json(os.path.join(REC, "census-exit-%s.json" % arm), P.census())
        print("hog kill:", killed, flush=True)
        print("exit census:", P.census()["nodes"], P.census()["modules"], flush=True)


if __name__ == "__main__":
    main()
