#!/usr/bin/env python3
"""r84b monfix — clean re-runs: (1) monitor-stream pre-gain with stream-restore
reset between reps; (2) stream-death growth trace sampled while parec is alive;
(3) pw-play default props check. Namespace r84b_*. No tracked writes."""
import json, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r84b_probe as R

PROBE = "pF3-monfix"

def reset_restore(ns):
    """Write 100% on a LIVE pw-play stream (same restore key), let it die."""
    p = R.play_at(ns, R.tone_short(), "r84b_reset")
    time.sleep(0.5)
    ia = R.si_index("r84b_reset")
    wr = R.run(["pactl", "set-sink-input-volume", str(ia), "100%"], 4)
    for _ in range(40):
        if not p.alive(): break
        time.sleep(0.1)
    p.finish()
    time.sleep(0.3)
    return wr["rc"]

def main():
    results = {"loadavg_start": R.loadavg()}
    s1 = R.load_ns(R.NS); s2 = R.load_ns(R.NS2)
    assert s1["verified"] and s2["verified"]
    try:
        # pw-play default props (explains restore key seen in pF-monstream)
        p = R.play_at(R.NS, R.tone_short(), "r84b_propschk")
        time.sleep(0.5)
        nodes = R.witness_nodes("r84b_propschk")
        si = R.si_witness("r84b_propschk")
        p.kill(); p.finish()
        results["pwplay_default"] = {"nodes": nodes, "si": si}
        print("pw-play default node props:", nodes[0]["props"] if nodes else None)
        print("pw-play default si:", si)
        # (1) clean sivol reps
        for rep in range(2):
            rc_reset = reset_restore(R.NS)
            pa = R.play_at(R.NS, R.tone_long(9), "r84b_ta"); pb = R.play_at(R.NS, R.tone_b(), "r84b_tb")
            time.sleep(0.6)
            ia = R.si_index("r84b_ta")
            pre = R.si_witness("r84b_ta")
            p, o = R.parec_pin(["-d", R.NS, "--monitor-stream", str(ia)], 6.6, f"sivolc{rep}")
            r, x, _o = R.fin_parec(p, o, 6.6,
                                   actions=[(2.4, ["pactl", "set-sink-input-volume", str(ia), "50%"])])
            w = R.windows(_o, win=0.25)
            before = [row["peak"] for row in w if 1.0 <= row["t0"] <= 2.2]
            after = [row["peak"] for row in w if 2.6 <= row["t0"] <= 5.0]
            extra = {"reset_rc": rc_reset, "pre_si": pre, "idxA": ia,
                     "amps_before": before, "amps_after": after, **x}
            R.record_leg(PROBE, "sivol_clean", rep, r, extra)
            results.setdefault("sivol_clean", []).append(R.compact(r, extra))
            print(f"sivol_clean rep{rep} reset_rc={rc_reset} pre={pre[0]['value_percent'] if pre else None} "
                  f"before={before} after={after} acts_rc={[a['res']['rc'] for a in x['acts']]}")
            pa.kill(); pb.kill(); pa.finish(); pb.finish()
            try: _o.unlink()
            except FileNotFoundError: pass
            time.sleep(0.3)
        reset_restore(R.NS)
        # (2) stream-death growth trace
        for rep in range(2):
            pa = R.play_at(R.NS, R.tone_long(9), "r84b_ta"); pb = R.play_at(R.NS, R.tone_b(), "r84b_tb")
            time.sleep(0.6)
            ia = R.si_index("r84b_ta")
            p, o = R.parec_pin(["-d", R.NS, "--monitor-stream", str(ia)], 6.6, f"killc{rep}")
            time.sleep(2.4)
            pa.kill()
            trace = []
            for _ in range(7):
                time.sleep(0.45)
                trace.append({"t": round(time.time() - (time.time() - 0), 2), "size": R.file_hdr(o)["size"],
                              "parec_alive": p.alive()})
            r = p.finish()
            w = R.windows(o, win=0.25)
            sig = R.sig_of(w)
            res = {"rc": r["rc"], "wall": r["wall"], "out": "", "err": r["err"], "timeout": False,
                   "cmd": f"parec --latency-msec=50 -d {R.NS} --monitor-stream {ia}; kill A at 2.4s"}
            extra = {"idxA": ia, "size_trace": trace, "sig": sig, "loadavg": R.loadavg()}
            R.record_leg(PROBE, "kill_trace", rep, res, extra)
            results.setdefault("kill_trace", []).append(R.compact(res, extra))
            print(f"kill_trace rep{rep} rc={r['rc']} trace={[(t['size'], t['parec_alive']) for t in trace]} sig={sig}")
            pb.kill(); pb.finish()
            try: o.unlink()
            except FileNotFoundError: pass
            time.sleep(0.3)
        results["loadavg_end"] = R.loadavg()
        (R.RCPTS / "pF3-monfix.json").write_text(json.dumps(results, indent=1))
    finally:
        R.unload_idx(s1["idx"], R.NS); R.unload_idx(s2["idx"], R.NS2)
    print("DONE monfix")

if __name__ == "__main__":
    sys.exit(main() or 0)
