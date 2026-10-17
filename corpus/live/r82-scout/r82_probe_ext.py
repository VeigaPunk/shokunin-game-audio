#!/usr/bin/env python3
"""R82 scout extension — gap legs for the ffmpeg frontier.

Fills what s0-s7 left open:
  x0  `-i default` capture flake recheck (s1 c0 was hang/EIO/EIO)
  x1  -fragment_size placed BEFORE -i (indev position) — does it reach
      pulse.attr.fragsize / node.latency?  (s4 ci* had it after -i, i.e.
      consumed as an unused output-side option — different question)
  x2  -frame_size 8192 BEFORE -i — isolates the ci2 SIGABRT to option
      position (output-side) vs the option itself
  x3  ffplay playback via SDL_AUDIODRIVER=pulseaudio, PULSE_SINK=r82ff_ns —
      node name/props/class, rc; and one auto-driver contrast rep
  x4  ffprobe reading a live pulse indev (bounded)
  x5  `-f alsa -i default` node snapshot — pipewire-alsa plugin stream
      identity (who does ffmpeg look like in the graph?)
  x6  `-f alsa -i hw:0,0 -sample_rate 12345` — negotiation-failure class
      on a free capture subdevice (hw:0 playback may be PW-held)
  x7  `-f pulse -i @DEFAULT_MONITOR@` / `@DEFAULT_SOURCE@` — alias args
      in the indev (pactl verbs accept them per r85 A17/A21; does ffmpeg?)
Usage: r82_probe_ext.py
"""
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from r82_probe import (Proc, RUNS, TMP, REC, NS, SPDIF, LINE, TONE,
                       TONE_SHORT, FFMPEG, FFPROBE, sh, sha16, wav_shape,
                       pcm_peak, tone_windows, nodes_of_pid, consumers_of,
                       first_err_lines, save_receipt, pactl_load_null,
                       unload_ns, cleanup_mine, node_exists, ensure_ns,
                       ensure_tone, nodes_named, pw_dump)

OUTDIR = RUNS / "ext"
OUTDIR.mkdir(parents=True, exist_ok=True)


def legdir(name):
    d = OUTDIR / name
    d.mkdir(parents=True, exist_ok=True)
    return d


def cap_leg(name, inargs, reps=3, env_extra=None, t="2.0"):
    rows = []
    for rep in range(reps):
        env = dict(os.environ)
        env["PIPEWIRE_PROPS"] = "{ stream.capture.sink=true node.name=r82ffx_%s }" % name
        if env_extra:
            env.update(env_extra)
        out_wav = legdir(name) / f"r{rep}.wav"
        if out_wav.exists():
            out_wav.unlink()
        cmd = [FFMPEG, "-hide_banner", "-loglevel", "warning",
               "-nostdin", "-y"] + inargs + [
               "-t", t, "-c:a", "pcm_s16le", str(out_wav)]
        p = Proc(cmd, env=env, wall=15)
        time.sleep(0.9)
        nodes = nodes_of_pid(p.p.pid)
        cons, links = consumers_of(r"r82ffx_|Lavf|ffmpeg|alsa_")
        rc, out, err, wall = p.finish()
        rows.append({"rep": rep, "rc": rc, "wall_s": round(wall, 3),
                     "wav": wav_shape(out_wav), "peak": pcm_peak(out_wav),
                     "tone_windows": tone_windows(out_wav)[:8],
                     "nodes": nodes, "consumers": cons,
                     "stderr_head": first_err_lines(err)})
        save_receipt(legdir(name) / f"r{rep}", cmd, rc, out, err, wall,
                     {"peak": pcm_peak(out_wav)})
        time.sleep(0.3)
    return rows


def main():
    ensure_tone()
    res = {"host_time_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "ns_load": ensure_ns()}
    time.sleep(0.5)

    # pump tone into r82ff_ns for the whole window so monitors carry content
    pump = Proc([FFMPEG, "-hide_banner", "-loglevel", "error", "-nostdin",
                 "-stream_loop", "-1", "-re", "-f", "wav", "-i", str(TONE),
                 "-f", "pulse", "-device", NS, "-name", "r82ffx_pump",
                 "pulse-play"], wall=600)

    # ---- x0: default capture flake recheck
    res["x0_default_recheck"] = cap_leg("x0def", ["-f", "pulse", "-i", "default"])

    # ---- x1: indev-position fragment_size
    res["x1a_frag2048"] = cap_leg(
        "x1a", ["-f", "pulse", "-fragment_size", "2048", "-i", NS + ".monitor"])
    res["x1b_frag65536"] = cap_leg(
        "x1b", ["-f", "pulse", "-fragment_size", "65536", "-i", NS + ".monitor"])

    # ---- x2: indev-position frame_size (ci2 crashed on output-position)
    res["x2_framesize8192"] = cap_leg(
        "x2", ["-f", "pulse", "-frame_size", "8192", "-i", NS + ".monitor"])

    # ---- x3: ffplay via SDL pulse driver into our sink
    rows = []
    for rep in range(3):
        env = dict(os.environ)
        env["SDL_AUDIODRIVER"] = "pulseaudio"
        env["PULSE_SINK"] = NS
        cmd = ["ffplay", "-hide_banner", "-loglevel", "warning", "-nostdin",
               "-nodisp", "-autoexit", str(TONE_SHORT)]
        p = Proc(cmd, env=env, wall=20)
        time.sleep(1.2)
        nodes = nodes_of_pid(p.p.pid)
        cons, links = consumers_of(r"r82ff|ffplay|SDLAudio|Lavf")
        rc, out, err, wall = p.finish()
        rows.append({"rep": rep, "rc": rc, "wall_s": round(wall, 3),
                     "nodes": nodes, "consumers": cons,
                     "stderr_head": first_err_lines(err, 5)})
        save_receipt(legdir("x3_ffplay") / f"r{rep}", cmd, rc, out, err, wall)
        time.sleep(0.3)
    res["x3_ffplay"] = rows
    # contrast: no driver pin (SDL picks)
    env = dict(os.environ); env["PULSE_SINK"] = NS
    p = Proc(["ffplay", "-hide_banner", "-loglevel", "warning", "-nostdin",
              "-nodisp", "-autoexit", str(TONE_SHORT)], env=env, wall=20)
    time.sleep(1.2)
    nodes = nodes_of_pid(p.p.pid)
    rc, out, err, wall = p.finish()
    res["x3b_ffplay_auto"] = {"rc": rc, "wall_s": round(wall, 3),
                              "nodes": nodes,
                              "stderr_head": first_err_lines(err, 5)}
    save_receipt(legdir("x3b_ffplay_auto"), cmd, rc, out, err, wall)

    # ---- x4: ffprobe on live indev (bounded)
    rows = []
    for rep in range(2):
        cmd = [FFPROBE, "-hide_banner", "-v", "error", "-show_streams",
               "-f", "pulse", "-i", NS + ".monitor"]
        p = Proc(cmd, wall=12)
        time.sleep(1.0)
        nodes = nodes_of_pid(p.p.pid)
        rc, out, err, wall = p.finish()
        rows.append({"rep": rep, "rc": rc, "wall_s": round(wall, 3),
                     "out_head": (out or "")[:800], "nodes": nodes,
                     "stderr_head": first_err_lines(err, 4)})
        save_receipt(legdir("x4_ffprobe") / f"r{rep}", cmd, rc, out, err, wall)
    res["x4_ffprobe_indev"] = rows

    # ---- x5: -f alsa -i default → what node lands in the graph
    res["x5_alsa_default"] = cap_leg(
        "x5", ["-f", "alsa", "-i", "default"], reps=3)

    # ---- x6: -f alsa hw:0,0 negotiation failure (odd rate)
    rows = []
    for rep in range(3):
        out_wav = legdir("x6_alsa_nego") / f"r{rep}.wav"
        cmd = [FFMPEG, "-hide_banner", "-loglevel", "warning", "-nostdin",
               "-y", "-f", "alsa", "-sample_rate", "12345", "-i", "hw:0,0",
               "-t", "1.5", "-c:a", "pcm_s16le", str(out_wav)]
        _t0 = time.monotonic()
        rc, out, err = sh(cmd, timeout=10)
        rows.append({"rep": rep, "rc": rc,
                     "wall_s": round(time.monotonic() - _t0, 3),
                     "wav": wav_shape(out_wav),
                     "stderr_head": first_err_lines(err, 4)})
        save_receipt(legdir("x6_alsa_nego") / f"r{rep}", cmd, rc, out, err, 0)
        time.sleep(0.3)
    res["x6_alsa_nego_12345"] = rows

    # ---- x7: pulse aliases in the indev
    res["x7a_defmon"] = cap_leg("x7a", ["-f", "pulse", "-i", "@DEFAULT_MONITOR@"],
                                reps=3)
    res["x7b_defsrc"] = cap_leg("x7b", ["-f", "pulse", "-i", "@DEFAULT_SOURCE@"],
                                reps=3)

    # ---- hardware identity for the s5 labels
    _, res["aplay_l"], _ = sh(["aplay", "-l"], timeout=10)
    _, res["arecord_l"], _ = sh(["arecord", "-l"], timeout=10)
    _, res["asound_cards"], _ = sh(["cat", "/proc/asound/cards"], timeout=5)

    pump.kill()
    cleanup_mine()
    (REC / "s8-ext.json").write_text(json.dumps(res, indent=1))
    print("ext done")


if __name__ == "__main__":
    main()
