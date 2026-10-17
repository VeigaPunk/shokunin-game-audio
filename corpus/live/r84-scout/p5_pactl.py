#!/usr/bin/env python3
"""p5 — pactl write surface on a live stream: volume mid-stream (sink+source),
suspend semantics, port lattice, refusal classes. Own sink only for writes."""
import sys, time, json
import r84_probe as R

PROBE = "p5-pactl"
TONE = str(R.TMP / "tone_a.wav")      # 4 s, L1k/R1.5k amp 8192
MIC = "alsa_input.usb-Generic_USB_Audio-00.HiFi__Mic__source"
SPDIF = "alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink"
HDMI = "alsa_output.pci-0000_01_00.1.hdmi-stereo"

def capture_while(actions, dur=4.6, dev=None):
    """parec on <dev or NS.monitor>; run actions=[(t, cmd)] during it; return
    window peaks + action results + player finish."""
    out = R.TMP / f"p5_{int(time.time()*1000)%10**7}.wav"
    player = R.play_at(R.NS, TONE, "r84alsa_p5play")
    time.sleep(0.5)
    rec = R.Proc(["parec", "-d", dev or f"{R.NS}.monitor",
                  "--rate=48000", "--channels=2", "--format=s16le",
                  "--file-format=wav", str(out)])
    t0 = time.time(); acts = []
    for at, cmd in actions:
        while time.time() - t0 < at: time.sleep(0.03)
        acts.append({"t": at, "cmd": cmd, "res": R.run(cmd if isinstance(cmd, list) else cmd.split(), 6)})
    # wait out the player
    while player.alive() and time.time() - t0 < dur + 3: time.sleep(0.1)
    pres = player.finish()
    time.sleep(0.3)
    import signal
    try: import os; os.killpg(rec.p.pid, signal.SIGTERM)
    except (ProcessLookupError, PermissionError): pass
    rres = rec.finish()
    w = R.windows(out)
    res = {"actions": acts, "player": {"rc": pres["rc"], "wall": pres["wall"],
                                       "err": pres["err"].splitlines()[-2:]},
           "rec": {"rc": rres["rc"], "size": R.file_hdr(out)["size"]},
           "windows": w}
    try: out.unlink()
    except FileNotFoundError: pass
    return res

def simple(cmd, reps=3):
    reps_l = []
    for i in range(reps):
        r = R.run(cmd.split(), 8)
        reps_l.append({"rc": r["rc"], "err": r["err"].splitlines()[:2], "out": r["out"].splitlines()[:2]})
        R.record_leg(PROBE, "cls_" + cmd.split()[1] + "_" + cmd.split()[2].replace("/", "_"), i, r)
        time.sleep(0.2)
    return reps_l

def main():
    sink = R.load_ns(R.NS); sink2 = R.load_ns(R.NS2)
    assert sink["verified"] and sink2["verified"]
    serial = None
    for n in R.nodes_named(R.NS):
        if n["name"] == R.NS: serial = n["serial"]
    results = {"sink_idx": sink["idx"], "serial": serial, "legs": {}}
    try:
        # ---- live-volume legs ----
        for leg, actions in [
            ("vol_base",  []),
            ("vol_50",    [(1.6, f"pactl set-sink-volume {R.NS} 50%")]),
            ("vol_150",   [(1.6, f"pactl set-sink-volume {R.NS} 150%")]),
            ("vol_0_100", [(1.6, f"pactl set-sink-volume {R.NS} 0%"),
                          (3.2, f"pactl set-sink-volume {R.NS} 100%")]),
            ("vol_idx",   [(1.6, f"pactl set-sink-volume {serial} 25%")]),
            ("mute",      [(1.6, f"pactl set-sink-mute {R.NS} 1"),
                          (3.2, f"pactl set-sink-mute {R.NS} 0")]),
            ("src_vol50", [(1.6, f"pactl set-source-volume {R.NS}.monitor 50%")]),
        ]:
            reps = []
            for rep in range(3):
                r = capture_while(actions)
                R.record_leg(PROBE, leg, rep,
                             {"cmd": leg, "rc": r["player"]["rc"], "wall": r["player"]["wall"], "timeout": False},
                             {"acts": [{ "cmd": a["cmd"], "rc": a["res"]["rc"],
                                         "err": a["res"]["err"].splitlines()[:2]} for a in r["actions"]],
                              "rec_size": r["rec"]["size"],
                              "peaks": [x["peak"] for x in r["windows"]]})
                reps.append({"acts": [{ "cmd": a["cmd"], "rc": a["res"]["rc"],
                                        "err": a["res"]["err"].splitlines()[:1]} for a in r["actions"]],
                             "player_rc": r["player"]["rc"], "player_wall": r["player"]["wall"],
                             "rec_size": r["rec"]["size"],
                             "peaks": [x["peak"] for x in r["windows"]]})
                # restore volume between reps
                R.run(f"pactl set-sink-volume {R.NS} 100%".split(), 6)
                R.run(f"pactl set-source-volume {R.NS}.monitor 100%".split(), 6)
                R.run(f"pactl set-sink-mute {R.NS} 0".split(), 6)
                time.sleep(0.4)
            results["legs"][leg] = reps
            print(f"{leg:10s} player_rc={[x['player_rc'] for x in reps]} acts_rc={[a['rc'] for a in reps[0]['acts']]} peaks={reps[0]['peaks']}")
        # ---- suspend legs ----
        for leg, actions in [
            ("susp_sink",    [(1.6, f"pactl suspend-sink {R.NS} 1"),
                              (3.2, f"pactl suspend-sink {R.NS} 0")]),
            ("susp_src",     [(1.6, f"pactl suspend-source {R.NS}.monitor 1"),
                              (3.2, f"pactl suspend-source {R.NS}.monitor 0")]),
        ]:
            reps = []
            for rep in range(3):
                r = capture_while(actions)
                # state witness right after suspend
                R.record_leg(PROBE, leg, rep,
                             {"cmd": leg, "rc": r["player"]["rc"], "wall": r["player"]["wall"], "timeout": False},
                             {"acts": [{"cmd": a["cmd"], "rc": a["res"]["rc"],
                                        "err": a["res"]["err"].splitlines()[:2]} for a in r["actions"]],
                              "rec_size": r["rec"]["size"],
                              "peaks": [x["peak"] for x in r["windows"]]})
                reps.append({"acts": [{"cmd": a["cmd"], "rc": a["res"]["rc"],
                                       "err": a["res"]["err"].splitlines()[:1]} for a in r["actions"]],
                             "player_rc": r["player"]["rc"], "player_wall": r["player"]["wall"],
                             "rec_size": r["rec"]["size"],
                             "peaks": [x["peak"] for x in r["windows"]]})
                time.sleep(0.4)
            results["legs"][leg] = reps
            print(f"{leg:10s} player_rc={[x['player_rc'] for x in reps]} acts_rc={[a['rc'] for a in reps[0]['acts']]} peaks={reps[0]['peaks']}")
        # suspend before play: sink held suspended, then play into it
        R.run(f"pactl suspend-sink {R.NS} 1".split(), 6)
        st = R.run(["pactl", "list", "short", "sinks"], 6)["out"]
        p = R.play_at(R.NS, TONE, "r84alsa_p5pre")
        time.sleep(1.2)
        st2 = R.run(["pactl", "list", "short", "sinks"], 6)["out"]
        cons = R.consumers_of("r84alsa_p5pre")
        pres = p.finish()
        results["legs"]["susp_before_play"] = {
            "state_at_suspend": [l for l in st.splitlines() if R.NS in l],
            "state_during_play": [l for l in st2.splitlines() if R.NS in l],
            "consumers": cons, "player_rc": pres["rc"], "player_wall": pres["wall"]}
        print("susp_before_play:", results["legs"]["susp_before_play"])
        # ---- refusal classes (no stream) ----
        cls = {}
        for name, cmd in [
            ("vol_bogus_val",   f"pactl set-sink-volume {R.NS} bogus"),
            ("vol_dead_idx",    "pactl set-sink-volume 999999 50%"),
            ("vol_bogus_sink",  "pactl set-sink-volume no_such_r84 50%"),
            ("vol_extra",       f"pactl set-sink-volume {R.NS} 50% 60%"),
            ("vol_neg",         f"pactl set-sink-volume {R.NS} -10%"),
            ("vol_700",         f"pactl set-sink-volume {R.NS} 700%"),
            ("svol_bogus_src",  "pactl set-source-volume no_such_r84 50%"),
            ("susp_bogus",      "pactl suspend-sink no_such_r84 1"),
            ("susp_dead_idx",   "pactl suspend-sink 999999 1"),
            ("susp_bad_arg",    f"pactl suspend-sink {R.NS} 2"),
            ("susp_src_bogus",  "pactl suspend-source no_such_r84 1"),
            ("sport_ns_noport", f"pactl set-sink-port {R.NS} bogus_port_r84"),
            ("sport_hdmi_ok",   f"pactl set-sink-port {HDMI} hdmi-output-0"),
            ("sport_hdmi_bad",  f"pactl set-sink-port {HDMI} bogus_port_r84"),
            ("sport_spdif",     f"pactl set-sink-port {SPDIF} spdif-output"),
            ("srport_mic_bad",  f"pactl set-source-port {MIC} bogus_port_r84"),
            ("sivol_bogus",     "pactl set-sink-input-volume 999999 50%"),
            ("getvol_alias",    "pactl get-sink-volume @DEFAULT_SINK@"),
        ]:
            cls[name] = simple(cmd)
            print(f"cls/{name:16s} rc={[x['rc'] for x in cls[name]]} err={cls[name][0]['err'][:1]}")
            R.run(f"pactl set-sink-volume {R.NS} 100%".split(), 6)  # restore own sink vol after vol legs
        results["classes"] = cls
        (R.RCPTS/"p5-pactl.json").write_text(json.dumps(results, indent=1))
    finally:
        R.run(f"pactl suspend-sink {R.NS} 0".split(), 6)
        R.run(f"pactl set-sink-volume {R.NS} 100%".split(), 6)
        R.unload_idx(sink["idx"], R.NS); R.unload_idx(sink2["idx"], R.NS2)

if __name__ == "__main__":
    sys.exit(main() or 0)
