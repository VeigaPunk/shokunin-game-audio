#!/usr/bin/env python3
"""p6 — parec --monitor-stream deep: per-stream pin vs sink monitor, cross-sink,
mid-run stream death/move, index namespace, per-stream volume."""
import sys, time, json, signal, os
import r84_probe as R

PROBE = "p6-monstream"
TA = str(R.TMP / "tone_a.wav")   # L1k/R1.5k 4s
TB = str(R.TMP / "tone_b.wav")   # 2k 4s
TL = str(R.TMP / "tone_long.wav")

def si_index(name):
    for n in R.nodes_named(name):
        if n["name"] == name:
            return n["serial"]
    return None

def parec(args, dur, tag):
    o = R.TMP / f"p6_{tag}_{int(time.time()*1000)%10**7}.wav"
    p = R.Proc(["parec", "--latency-msec=50", "--rate=48000", "--channels=2",
                "--format=s16le", "--file-format=wav"] + args + [str(o)])
    return p, o

def fin(p, o, dur, actions=None):
    t0 = time.time(); acts = []
    for at, cmd in (actions or []):
        while time.time() - t0 < at: time.sleep(0.03)
        acts.append({"t": at, "cmd": cmd, "res": R.run(cmd.split(), 6)})
    while time.time() - t0 < dur and p.alive(): time.sleep(0.1)
    try: os.killpg(p.p.pid, signal.SIGTERM)
    except (ProcessLookupError, PermissionError): pass
    r = p.finish()
    w = R.windows(o)
    return {"rc": r["rc"], "err": r["err"].splitlines()[:3], "size": R.file_hdr(o)["size"],
            "acts": [{"cmd": a["cmd"], "rc": a["res"]["rc"], "err": a["res"]["err"].splitlines()[:1]}
                     for a in acts],
            "win": [(x["t0"], x["peak"], x["L@1000"], x["R@1500"], x["L@2000"]) for x in w]}, o

def sig(win):
    """compact signature: dominant bins present per window."""
    out = []
    for t, pk, l1, r15, l2 in win:
        tag = ""
        if l1 > 500 and l2 > 500: tag = "A+B"
        elif l1 > 500: tag = "A"
        elif l2 > 500: tag = "B"
        elif pk > 0: tag = "?"
        else: tag = "-"
        out.append((t, tag, pk))
    # compress to transitions
    tr = []; last = None
    for t, tag, pk in out:
        if tag != last: tr.append((t, tag, pk)); last = tag
    return tr

def main():
    s1 = R.load_ns(R.NS); s2 = R.load_ns(R.NS2)
    assert s1["verified"] and s2["verified"]
    results = {}
    try:
        # --- pinning legs: A+B both into ns ---
        for leg, argsf in [
            ("sink_monitor",  lambda ia, ib: ["-d", f"{R.NS}.monitor"]),
            ("monA",          lambda ia, ib: ["-d", R.NS, "--monitor-stream", str(ia)]),
            ("monB",          lambda ia, ib: ["-d", R.NS, "--monitor-stream", str(ib)]),
            ("monA_nod",      lambda ia, ib: ["--monitor-stream", str(ia)]),
            ("monA_bogusd",   lambda ia, ib: ["-d", "no_such_r84", "--monitor-stream", str(ia)]),
            ("monA_othersink",lambda ia, ib: ["-d", R.NS2, "--monitor-stream", str(ia)]),
            ("mon_bad0",      lambda ia, ib: ["-d", R.NS, "--monitor-stream", "0"]),
            ("mon_deadidx",   lambda ia, ib: ["-d", R.NS, "--monitor-stream", "999999"]),
        ]:
            reps = []
            for rep in range(3):
                pa = R.play_at(R.NS, TA, "r84alsa_ta"); pb = R.play_at(R.NS, TB, "r84alsa_tb")
                time.sleep(0.6)
                ia, ib = si_index("r84alsa_ta"), si_index("r84alsa_tb")
                p, o = parec(argsf(ia, ib), 3.4, leg)
                r, _o = fin(p, o, 3.4)
                r["cmd"] = f"parec --latency-msec=50 ... {' '.join(map(str,argsf(ia,ib)))}"
                r["sig"] = sig(r["win"])
                R.record_leg(PROBE, leg, rep, r, {"idxA": ia, "idxB": ib, "sig": r["sig"]})
                reps.append({"rc": r["rc"], "size": r["size"], "sig": r["sig"],
                             "err": r["err"], "idxA": ia, "idxB": ib})
                pa.kill(); pa.finish(); pb.kill(); pb.finish()
                try: _o.unlink()
                except FileNotFoundError: pass
                time.sleep(0.4)
            results[leg] = reps
            print(f"{leg:16s} rc={[x['rc'] for x in reps]} sig={reps[0]['sig']} err={reps[0]['err'][:1]}")
        # --- source-output index as monitor-stream ---
        reps = []
        for rep in range(3):
            # a running recorder = a source-output; pin monitor-stream to it
            rec0 = R.Proc(["pw-record", "-P", "stream.capture.sink=true",
                           "-P", "node.name=r84alsa_srcout", "--target", R.NS,
                           str(R.TMP/"so.wav")])
            pa = R.play_at(R.NS, TA, "r84alsa_ta"); time.sleep(0.7)
            so = si_index("r84alsa_srcout"); ia = si_index("r84alsa_ta")
            p, o = parec(["-d", R.NS, "--monitor-stream", str(so)], 2.6, "soidx")
            r, _o = fin(p, o, 2.6)
            r["sig"] = sig(r["win"])
            R.record_leg(PROBE, "mon_soidx", rep, r, {"so": so, "sig": r["sig"]})
            reps.append({"rc": r["rc"], "size": r["size"], "sig": r["sig"], "so": so,
                         "err": r["err"]})
            rec0.kill(); rec0.finish(); pa.kill(); pa.finish()
            try: _o.unlink(); (R.TMP/"so.wav").unlink()
            except FileNotFoundError: pass
            time.sleep(0.4)
        results["mon_soidx"] = reps
        print(f"{'mon_soidx':16s} rc={[x['rc'] for x in reps]} sig={reps[0]['sig']} err={reps[0]['err'][:1]}")
        # --- mid-run events on the pinned stream ---
        for leg, actf in [
            ("monA_kill",   lambda ia, ib: [(2.4, f"kill_placeholder_{ia}")]),
            ("monA_move",   lambda ia, ib: [(2.4, f"pactl move-sink-input {ia} {R.NS2}")]),
            ("monA_sivol",  lambda ia, ib: [(2.4, f"pactl set-sink-input-volume {ia} 50%")]),
            ("monA_simute", lambda ia, ib: [(2.4, f"pactl set-sink-input-mute {ia} 1"),
                                            (4.4, f"pactl set-sink-input-mute {ia} 0")]),
        ]:
            reps = []
            for rep in range(3):
                pa = R.play_at(R.NS, TL, "r84alsa_ta")
                pb = R.play_at(R.NS, TB, "r84alsa_tb")
                time.sleep(0.6)
                ia, ib = si_index("r84alsa_ta"), si_index("r84alsa_tb")
                acts = actf(ia, ib)
                if leg == "monA_kill":
                    acts = []  # kill by hand at 2.4
                p, o = parec(["-d", R.NS, "--monitor-stream", str(ia)], 6.6, leg)
                if leg == "monA_kill":
                    t0 = time.time()
                    while time.time() - t0 < 2.4: time.sleep(0.05)
                    pa.kill()  # pinned stream dies
                    dead_acts = [{"t": 2.4, "cmd": "kill A", "res": {"rc": 0, "err": ""}}]
                    r, _o = fin(p, o, 6.6)
                    r["acts"] = dead_acts
                else:
                    r, _o = fin(p, o, 6.6, actions=acts)
                # also observe where A links after move
                post = R.consumers_of("r84alsa_ta")
                r["sig"] = sig(r["win"]); r["post_links"] = post
                r["cmd"] = f"parec --latency-msec=50 -d {R.NS} --monitor-stream {ia}"
                R.record_leg(PROBE, leg, rep, r, {"idxA": ia, "sig": r["sig"], "post": post})
                reps.append({"rc": r["rc"], "size": r["size"], "sig": r["sig"],
                             "acts": r["acts"], "post": post, "err": r["err"]})
                for x in (pa, pb):
                    if x.alive(): x.kill()
                    x.finish()
                try: _o.unlink()
                except FileNotFoundError: pass
                R.run(f"pactl set-sink-input-volume {ia} 100%".split(), 4)
                time.sleep(0.4)
            results[leg] = reps
            print(f"{leg:16s} rc={[x['rc'] for x in reps]} sig={reps[0]['sig']} post={reps[0].get('post')} err={reps[0]['err'][:1]}")
        (R.RCPTS/"p6-monstream.json").write_text(json.dumps(results, indent=1))
    finally:
        R.unload_idx(s1["idx"], R.NS); R.unload_idx(s2["idx"], R.NS2)

if __name__ == "__main__":
    sys.exit(main() or 0)
