#!/usr/bin/env python3
"""P6 — hot-unload lifecycle: what a stream does when its sink's *module* is
unloaded mid-play (a third destruction mode next to r78's manual unlink and
plain target loss).

Instrument: a 100 ms pw-dump sampler thread (nodes of interest + every link),
a default-sink-monitor recorder (content witness), and the process exit code of
the consumer.  Every leg is run REPS times.
"""
import json
import os
import subprocess
import sys
import threading
import time
import wave
from array import array

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r80_probe import (Receipt, load, unload, snap, pactl, run, fft_peaks,
                       wav_stats, TONE, SR)

REPS = 3
T = "r80_h"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tmp")


def default_sink():
    r = pactl("get-default-sink")
    return r["stdout"].strip()


class Sampler(threading.Thread):
    """100 ms pw-dump sampler; keeps node + link snapshots for names of interest."""
    def __init__(self, prefixes):
        super().__init__(daemon=True)
        self.prefixes = tuple(prefixes)
        self.samples = []
        self.stop = threading.Event()
        self.t0 = time.time()

    def run(self):
        while not self.stop.is_set():
            s = snap()
            t = round(time.time() - self.t0, 3)
            if "error" in s:
                self.samples.append({"t": t, "error": s["error"]})
                time.sleep(0.1)
                continue
            nodes = {k: {"name": v["name"], "class": v["class"], "state": v["state"]}
                     for k, v in s["nodes"].items()
                     if any(p in (v.get("name") or "") for p in self.prefixes)}
            links = [{"out": l["out"], "in": l["in"], "state": l["state"]}
                     for l in s["links"]
                     if (any(p in l["out"].split(":")[0] for p in self.prefixes) or
                         any(p in l["in"].split(":")[0] for p in self.prefixes))]
            self.samples.append({"t": t, "nodes": nodes, "links": links})
            time.sleep(0.1)


def spawn(cmd):
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def kill(p):
    if p.poll() is None:
        p.terminate()
        try:
            p.wait(timeout=2)
        except Exception:
            p.kill()
    return p.poll()


def leg_common(rc, label, rep, setup, action, teardown, prefixes, rec_secs=4.0):
    """setup() -> dict(ctx); action(ctx) -> dict; teardown(ctx)"""
    ctx = setup()
    time.sleep(0.9)
    s = Sampler(prefixes)
    s.start()
    rec_path = os.path.join(OUT, f"{label}-{rep}-mon.wav")
    # content witness: record the DEFAULT sink monitor (read-only observer)
    rec = spawn(["pw-record", "-P", f"node.name={T}_{label}{rep}_rec",
                 "-P", "stream.capture.sink=true",
                 "--target", default_sink(), "-n", str(int(rec_secs * SR)),
                 rec_path])
    t0 = time.time()
    time.sleep(1.5)
    act = action(ctx)
    t_act = round(time.time() - t0, 3)
    # wait for the recorder + sampler
    try:
        rec.wait(timeout=rec_secs + 3)
    except Exception:
        kill(rec)
    time.sleep(0.6)
    s.stop.set()
    s.join(timeout=2)
    pl = ctx.get("player")
    out = {
        "action": act, "t_action": t_act,
        "samples": s.samples,
        "player_poll_after": (pl.poll() if pl is not None else None),
        "recorder_rc": rec.returncode,
        "recorder_stats": wav_stats(rec_path),
        "recorder_fft": fft_peaks(rec_path),
    }
    teardown(ctx)
    time.sleep(0.4)
    return out


def pre_tone_stats(path):
    """split the recorder wav into [0,1.5s) and [1.6s,end) windows and FFT each."""
    try:
        with wave.open(path, "rb") as w:
            n, ch, sw = w.getnframes(), w.getnchannels(), w.getsampwidth()
            raw = w.readframes(n)
    except Exception as e:
        return {"error": str(e)}
    a = array("h")
    a.frombytes(raw[: len(raw) - (len(raw) % 2)])
    split = int(1.5 * SR) * ch
    pre, post = a[:split], a[split + int(0.15 * SR) * ch:]
    def pk(x):
        return max((abs(v) for v in x), default=0)
    return {"pre_peak": pk(pre), "post_peak": pk(post),
            "n_pre": len(pre) // ch, "n_post": len(post) // ch,
            "pre_rms": round((sum(v * v for v in pre) / max(1, len(pre))) ** 0.5, 1),
            "post_rms": round((sum(v * v for v in post) / max(1, len(post))) ** 0.5, 1)}


def main():
    rc = Receipt(os.environ.get("R80_RECEIPT","p6-hotunload"))
    tone = TONE

    # ---------------- L1: unload the module of a live playback target
    def setup_l1():
        idx, r = load("module-null-sink", f"sink_name={T}_ns1")
        time.sleep(0.4)
        p = spawn(["pw-cat", "-p", "--target", f"{T}_ns1", "--volume", "0.05",
                   "-P", f"node.name={T}_play1", tone])
        return {"idx": idx, "load": r, "player": p}

    def act_l1(c):
        return {"unload": unload(c["idx"])}

    def td_l1(c):
        kill(c["player"])
        unload(c["idx"])
        for k, v in snap()["nodes"].items():
            if (v.get("name") or "").startswith(T):
                run(["pw-cli", "destroy", str(k)])

    # ---------------- L2: r78 comparison — manual unlink, target alive
    def setup_l2():
        idx, r = load("module-null-sink", f"sink_name={T}_ns2")
        time.sleep(0.4)
        p = spawn(["pw-cat", "-p", "--target", f"{T}_ns2", "--volume", "0.05",
                   "-P", f"node.name={T}_play2", tone])
        return {"idx": idx, "player": p}

    def act_l2(c):
        time.sleep(0.4)
        # find this player's links and disconnect them
        s = snap()
        mine = {k for k, v in s["nodes"].items()
                if (v.get("name") or "") == f"{T}_play2"}
        ls = [l for l in s["links"] if l["out.node"] in mine or l["in.node"] in mine]
        outs = []
        for l in ls:
            d = run(["pw-link", "-d", str(l["id"])])
            outs.append({"link": l["out"] + " -> " + l["in"], "rc": d["rc"],
                         "err": d["stderr"].strip()})
        return {"disconnect": outs, "n": len(ls)}

    def td_l2(c):
        kill(c["player"])
        unload(c["idx"])
        for k, v in snap()["nodes"].items():
            if (v.get("name") or "").startswith(T):
                run(["pw-cli", "destroy", str(k)])

    # ---------------- L3: same as L1 but node.dont-move=true on the player
    def setup_l3():
        idx, r = load("module-null-sink", f"sink_name={T}_ns3")
        time.sleep(0.4)
        p = spawn(["pw-cat", "-p", "--target", f"{T}_ns3", "--volume", "0.05",
                   "-P", f"node.name={T}_play3", "-P", "node.dont-move=true", tone])
        return {"idx": idx, "player": p}

    def act_l3(c):
        return {"unload": unload(c["idx"])}

    def td_l3(c):
        kill(c["player"])
        unload(c["idx"])
        for k, v in snap()["nodes"].items():
            if (v.get("name") or "").startswith(T):
                run(["pw-cli", "destroy", str(k)])

    # ---------------- L4: capture stream on the sink's monitor, unload module
    def setup_l4():
        idx, r = load("module-null-sink", f"sink_name={T}_ns4")
        time.sleep(0.4)
        p = spawn(["pw-record", "-P", f"node.name={T}_rec4",
                   "-P", "stream.capture.sink=true",
                   "--target", f"{T}_ns4", "-n", str(4 * SR),
                   os.path.join(OUT, "l4-cap.wav")])
        return {"idx": idx, "player": p}

    def act_l4(c):
        return {"unload": unload(c["idx"])}

    def td_l4(c):
        kill(c["player"])
        unload(c["idx"])
        for k, v in snap()["nodes"].items():
            if (v.get("name") or "").startswith(T):
                run(["pw-cli", "destroy", str(k)])

    # ---------------- L5: unload the MASTER of a remap-sink
    def setup_l5():
        midx, r1 = load("module-null-sink", f"sink_name={T}_ns5m")
        time.sleep(0.4)
        ridx, r2 = load("module-remap-sink", f"sink_name={T}_rm5",
                        f"master={T}_ns5m")
        time.sleep(0.5)
        p = spawn(["pw-cat", "-p", "--target", f"{T}_rm5", "--volume", "0.05",
                   "-P", f"node.name={T}_play5", tone])
        return {"midx": midx, "ridx": ridx, "player": p}

    def act_l5(c):
        return {"unload_master": unload(c["midx"])}

    def td_l5(c):
        kill(c["player"])
        unload(c["ridx"])
        unload(c["midx"])
        for k, v in snap()["nodes"].items():
            if (v.get("name") or "").startswith(T):
                run(["pw-cli", "destroy", str(k)])

    # ---------------- L6: linger sink -> unload module -> does the stream notice?
    def setup_l6():
        idx, r = load("module-null-sink", f"sink_name={T}_ns6",
                      "sink_properties=object.linger=true")
        time.sleep(0.4)
        p = spawn(["pw-cat", "-p", "--target", f"{T}_ns6", "--volume", "0.05",
                   "-P", f"node.name={T}_play6", tone])
        return {"idx": idx, "player": p}

    def act_l6(c):
        return {"unload": unload(c["idx"])}

    def td_l6(c):
        kill(c["player"])
        unload(c["idx"])
        for k, v in snap()["nodes"].items():
            if (v.get("name") or "").startswith(T):
                run(["pw-cli", "destroy", str(k)])

    # ---------------- L7: native destroy of the sink node (module stays)
    def setup_l7():
        idx, r = load("module-null-sink", f"sink_name={T}_ns7")
        time.sleep(0.4)
        s = snap()
        nid = next((k for k, v in s["nodes"].items()
                    if v.get("name") == f"{T}_ns7"), None)
        p = spawn(["pw-cat", "-p", "--target", f"{T}_ns7", "--volume", "0.05",
                   "-P", f"node.name={T}_play7", tone])
        return {"idx": idx, "nid": nid, "player": p}

    def act_l7(c):
        d = run(["pw-cli", "destroy", str(c["nid"])])
        time.sleep(0.4)
        s = snap()
        return {"pw_cli_destroy": d,
                "sink_back": any(v.get("name") == f"{T}_ns7" for v in s["nodes"].values()),
                "module_still": str(c["idx"]) in pactl("list", "short", "modules")["stdout"]}

    def td_l7(c):
        kill(c["player"])
        unload(c["idx"])
        for k, v in snap()["nodes"].items():
            if (v.get("name") or "").startswith(T):
                run(["pw-cli", "destroy", str(k)])

    want = set(sys.argv[1:]) or {"L1", "L2", "L3", "L4", "L5", "L6", "L7"}
    for label, setup, act, td in [
        ("L1-unload-target", setup_l1, act_l1, td_l1),
        ("L2-manual-unlink", setup_l2, act_l2, td_l2),
        ("L3-dont-move", setup_l3, act_l3, td_l3),
        ("L4-capture-unload", setup_l4, act_l4, td_l4),
        ("L5-remap-master", setup_l5, act_l5, td_l5),
        ("L6-linger-sink", setup_l6, act_l6, td_l6),
        ("L7-native-destroy", setup_l7, act_l7, td_l7),
    ]:
        if label.split("-")[0] not in want:
            continue
        for rep in range(REPS):
            pf = (T, "r80_h", "output.r80_h") if label.startswith("L5") else (T, "r80_h")
            o = leg_common(rc, label, rep, setup, act, td,
                           prefixes=pf, rec_secs=4.0)
            rp = os.path.join(OUT, f"{label}-{rep}-mon.wav")
            o["window"] = pre_tone_stats(rp)
            # summarise link history
            hist = []
            for s_ in o["samples"]:
                if "error" in s_:
                    continue
                hist.append((s_["t"], sorted(l["out"] + "->" + l["in"] for l in s_["links"]),
                             sorted(v["name"] for v in s_["nodes"].values())))
            o["link_hist"] = hist
            rc.leg(f"{label}-rep{rep}", o)
            last = hist[-1] if hist else None
            rc.note(f"{label} rep{rep}: t_act={o['t_action']} action={json.dumps(o['action'])[:120]} "
                    f"player_rc={o['action'].get('player_rc')} "
                    f"mon_peak pre={o['window'].get('pre_peak')} post={o['window'].get('post_peak')} "
                    f"n_samples={len(hist)}")
            # compact per-sample trace around the action
            for t, links, nodes in hist:
                if abs(t - o["t_action"]) < 1.2:
                    rc.note(f"    t={t:5.2f} links={links} nodes={nodes}")
    rc.close()


if __name__ == "__main__":
    main()
