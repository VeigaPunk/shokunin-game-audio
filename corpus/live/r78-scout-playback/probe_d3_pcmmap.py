#!/usr/bin/env python3
"""Probe D3 — sink↔ALSA-PCM mapping, the witness×PCM lock matrix, and the
r78 `alsa_tick_time` row re-tested request-by-request.

D2 established: direct-ALSA playback works when NO PipeWire stream holds that
PCM, and a monitor witness on the *same* PCM is enough to make it EBUSY
(`wit_spkmon_hw00` rc=1) — while a witness on another card is harmless
(`wit_hdmimon_hw01` rc=0).  D1's all-EBUSY lattice was that observer effect.
"""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r78p as H

TONE = os.path.join(H.RAW, "tone_r78p_12.wav")
TONE6 = os.path.join(H.RAW, "tone_r78p_6s.wav")
ALSA_KEYS = ("api.alsa.card", "api.alsa.pcm.device", "api.alsa.path",
             "api.alsa.card.name", "alsa.device", "alsa.card",
             "device.api", "api.alsa.htimestamp", "node.description",
             "device.description", "alsa.id", "alsa.name", "alsa.subdevice")
TARGETS = ["hw:0,0", "hw:0,1", "hw:0,2", "hw:0,3"]
WITS = [("spdif", H.S_SPDIF), ("spk", H.S_SPK), ("hp", H.S_HP),
        ("hdmi", H.S_HDMI)]


def aplay_rc(dev, timeout=6.0, file=TONE):
    try:
        p = subprocess.run(["aplay", "-D", dev, file], capture_output=True,
                           timeout=timeout)
        return p.returncode, p.stderr.decode(errors="replace").strip(
        ).splitlines()[:2]
    except subprocess.TimeoutExpired as exc:
        return None, (exc.stderr or b"").decode(errors="replace").splitlines()[:2]


def main():
    out = {"probe": "aplay-pcm-map-lock-matrix-r78p", "matrix": [],
           "active": [], "arecord_rows": [], "toolchain": H.toolchain()}
    out["pre_cleanup"] = H.unload_all_mine()
    H.make_tone(TONE, dur=1.2)
    H.make_tone(TONE6, dur=6.0)
    time.sleep(0.5)

    # (a) which ALSA PCM backs each PipeWire sink
    nodes = H.pw_nodes()
    for label, name in (("spdif", H.S_SPDIF), ("spk", H.S_SPK),
                        ("hp", H.S_HP), ("hdmi", H.S_HDMI),
                        ("line", H.LINE), ("mic", H.MIC)):
        props = nodes.get(name, {})
        out.setdefault("pcm_map", []).append(
            {"label": label, "node": name,
             "alsa": {k: props.get(k) for k in ALSA_KEYS if k in props}})
    print(json.dumps(out["pcm_map"], indent=1)[:1800], flush=True)

    # (b) witness x target lock matrix
    for wlabel, wsink in WITS:
        for target in TARGETS:
            mon = H.Monitors(sinks=[(wlabel, wsink)],
                             tag=f"r78pmonD3_{wlabel}", win=0.25)
            mon.start()
            rc, err = aplay_rc(target)
            time.sleep(0.2)
            mon.stop()
            out["matrix"].append({"witness": wlabel, "target": target,
                                  "rc": rc, "err": err})
            print(f"  matrix wit={wlabel:5s} target={target:8s} rc={rc} "
                  f"{err[:1]}", flush=True)
            for f in os.listdir(H.RAW):
                if f.startswith("r78pmonD3_"):
                    os.unlink(os.path.join(H.RAW, f))

    # (c) active PipeWire playback into sink X -> which direct PCM is blocked?
    for label, sink in (("spdif", H.S_SPDIF), ("spk", H.S_SPK)):
        proc = subprocess.Popen(["pw-play", "-P", f"node.name=r78pD3_{label}",
                                 "--target", sink, TONE6],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        time.sleep(1.0)
        row = {"sink": label, "legs": []}
        for target in TARGETS:
            rc, err = aplay_rc(target)
            row["legs"].append({"target": target, "rc": rc, "err": err})
            print(f"  active sink={label:5s} target={target:8s} rc={rc} "
                  f"{err[:1]}", flush=True)
        proc.kill()
        time.sleep(0.8)
        out["active"].append(row)

    # (d) arecord pipewire/default: request-by-request
    tmp = os.path.join(H.RAW, "arec_d3.wav")
    rows = [
        ("default_nod_file", ["arecord", "-D", "default", tmp], 6.0),
        ("default_d2_file", ["arecord", "-D", "default", "-d", "2", tmp], 6.0),
        ("default_d2_devnull", ["arecord", "-D", "default", "-d", "2",
                                "/dev/null"], 6.0),
        ("default_fcd_d2_file", ["arecord", "-D", "default", "-f", "cd",
                                 "-d", "2", tmp], 6.0),
        ("pipewire_d2_file", ["arecord", "-D", "pipewire", "-d", "2", tmp],
         6.0),
        ("pipewire_nod_file", ["arecord", "-D", "pipewire", tmp], 6.0),
        ("sysdefault_d2_file", ["arecord", "-D", "sysdefault", "-d", "2",
                                tmp], 6.0),
    ]
    for label, argv, to in rows:
        try:
            p = subprocess.run(argv, capture_output=True, timeout=to)
            rc, err, kill = p.returncode, p.stderr.decode(
                errors="replace").strip().splitlines()[:3], False
        except subprocess.TimeoutExpired as exc:
            rc, err, kill = None, (exc.stderr or b"").decode(
                errors="replace").strip().splitlines()[:3], True
        size = os.path.getsize(tmp) if os.path.exists(tmp) else None
        out["arecord_rows"].append({"label": label, "argv": argv, "rc": rc,
                                    "err": err, "timed_out": kill,
                                    "file_bytes": size})
        print(f"  arecord {label:22s} rc={rc} bytes={size} {err[:1]}",
              flush=True)
        if os.path.exists(tmp):
            os.unlink(tmp)

    H.save("probe-aplay-pcm-map-r78p.json", out)


if __name__ == "__main__":
    main()
