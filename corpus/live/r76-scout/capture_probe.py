#!/usr/bin/env python3
"""r76-scout capture-surface harness (scratch, leaf seat, no receipt mode).

Runs bounded capture legs for pw-record / parec / arecord / ffmpeg on this host
and records: rc, wall, output byte count, WAV header fields (RIFF/data sizes),
TERM1 survival, stderr tail.  Every leg is bounded twice: an internal
TERM->KILL ladder and an outer `timeout -s KILL`-equivalent wall bound.

Usage: python3 capture_probe.py <batch-name> [leg-filter-substring]
"""
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "runs")
LEGS = os.path.join(HERE, "legs")
os.makedirs(RUNS, exist_ok=True)
os.makedirs(LEGS, exist_ok=True)

LINE = "alsa_input.usb-Generic_USB_Audio-00.HiFi__Line__source"
MIC = "alsa_input.usb-Generic_USB_Audio-00.HiFi__Mic__source"
MON = "alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink.monitor"
SINK = "alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink"
DEFAULT_SRC = "alsa_input.usb-Generic_USB_Audio-00.HiFi__Line__source"

# ---------------------------------------------------------------- leg table
# mode: "run"  -> wait for natural exit (bounded by wall_max)
#       "term" -> SIGTERM at term_at, then poll; SIGKILL at kill_at
# out:  "file" -> consumer writes the path itself; "stdout" -> we redirect
LEGS_SPEC = []


def leg(lid, argv, out="file", mode="run", wall_max=12.0, term_at=1.2,
        kill_at=3.2, env=None, note="", out_name=None):
    LEGS_SPEC.append(dict(id=lid, argv=argv, out=out, mode=mode,
                          wall_max=wall_max, term_at=term_at,
                          kill_at=kill_at, env=env or {}, note=note,
                          out_name=out_name or (lid + ".out")))


# ---- batch: gates ----------------------------------------------------------
leg("gate-pwrec-default-sc", ["pw-record", "--sample-count", "4800",
                              "--rate", "48000", "--channels", "2",
                              "--format", "s16", "OUT"],
    note="no --target: pw-record default target")
leg("gate-pwrec-line-sc", ["pw-record", "--target", LINE,
                           "--sample-count", "4800", "--rate", "48000",
                           "--channels", "2", "--format", "s16", "OUT"],
    note="explicit source target")
leg("gate-pwrec-sink-sc", ["pw-record", "--target", SINK,
                           "--sample-count", "4800", "--rate", "48000",
                           "--channels", "2", "--format", "s16", "OUT"],
    note="sink node as capture target")
leg("gate-pwrec-sink-capsink-sc", ["pw-record", "--target", SINK,
                                   "-P", "stream.capture.sink=true",
                                   "--sample-count", "4800",
                                   "--rate", "48000", "--channels", "2",
                                   "--format", "s16", "OUT"],
    note="sink node + stream.capture.sink=true")
leg("gate-parec-nodev", ["parec", "--rate=48000", "--channels=2",
                         "--format=s16le", "--raw", "OUT"], out="stdout",
    note="no -d")
leg("gate-parec-defsrc", ["parec", "-d", "@DEFAULT_SOURCE@", "--rate=48000",
                          "--channels=2", "--format=s16le", "--raw", "OUT"],
    out="stdout", note="-d @DEFAULT_SOURCE@")
leg("gate-arec-null", ["arecord", "-D", "null", "-d", "1", "-f", "S16_LE",
                       "-r", "48000", "-c", "2", "OUT"],
    note="null plugin (unpaced, zero samples)")
leg("gate-arec-hw00", ["arecord", "-D", "hw:0,0", "-d", "1", "-f", "S16_LE",
                       "-r", "48000", "-c", "2", "OUT"],
    note="direct kernel device")
leg("gate-ff-alsa-null-t1", ["ffmpeg", "-hide_banner", "-nostdin", "-y",
                             "-f", "alsa", "-i", "null", "-t", "1", "OUT"],
    note="ffmpeg alsa null, -t 1", out_name="gate-ff-alsa-null-t1.wav")
leg("gate-ff-pulse-line-t1", ["ffmpeg", "-hide_banner", "-nostdin", "-y",
                              "-f", "pulse", "-i", LINE, "-t", "1", "OUT"],
    note="ffmpeg pulse line, -t 1", out_name="gate-ff-pulse-line-t1.wav")
leg("gate-ff-pulse-mon-t1", ["ffmpeg", "-hide_banner", "-nostdin", "-y",
                             "-f", "pulse", "-i", MON, "-t", "1", "OUT"],
    note="ffmpeg pulse monitor, -t 1", out_name="gate-ff-pulse-mon-t1.wav")

# ---- batch: duration / byte caps ------------------------------------------
leg("cap-pwrec-sc4800", ["pw-record", "--target", LINE, "--sample-count",
                         "4800", "--rate", "48000", "--channels", "2",
                         "--format", "s16", "OUT"],
    note="sample-count cap")
leg("cap-pwrec-sc0", ["pw-record", "--target", LINE, "--sample-count", "0",
                      "--rate", "48000", "--channels", "2", "--format",
                      "s16", "OUT"], mode="term", wall_max=6.0,
    note="sample-count 0 = unbounded?")
leg("cap-arec-d1", ["arecord", "-D", "null", "-d", "1", "-f", "S16_LE",
                    "-r", "48000", "-c", "2", "OUT"], note="arecord -d 1")
leg("cap-arec-d0", ["arecord", "-D", "null", "-d", "0", "-f", "S16_LE",
                    "-r", "48000", "-c", "2", "OUT"], mode="term",
    wall_max=6.0, note="arecord -d 0")
leg("cap-arec-nodev-d1", ["arecord", "-D", "null", "-d", "1", "-f", "S16_LE",
                          "-r", "48000", "-c", "2", "OUT"], note="repeat")
leg("cap-ff-pulse-t0.5", ["ffmpeg", "-hide_banner", "-nostdin", "-y", "-f",
                          "pulse", "-i", LINE, "-t", "0.5", "OUT"],
    note="pulse -t 0.5", out_name="cap-ff-pulse-t0.5.wav")
leg("cap-ff-pulse-t1-b", ["ffmpeg", "-hide_banner", "-nostdin", "-y", "-f",
                          "pulse", "-i", LINE, "-t", "1", "OUT"],
    note="pulse -t 1 repeat", out_name="cap-ff-pulse-t1-b.wav")
leg("cap-ff-alsa-null-t1-b", ["ffmpeg", "-hide_banner", "-nostdin", "-y",
                              "-f", "alsa", "-i", "null", "-t", "1", "OUT"],
    note="alsa null -t 1 repeat", out_name="cap-ff-alsa-null-t1-b.wav")
leg("cap-parec-4s-stdout", ["parec", "-d", "@DEFAULT_SOURCE@",
                            "--rate=48000", "--channels=2", "--format=s16le",
                            "--raw", "OUT"], out="stdout", mode="term",
    wall_max=8.0, note="parec raw stdout, TERM at 1.2s")

# ---- batch: sever classes --------------------------------------------------
for consumer, argv, out, note in [
    ("pwrec", ["pw-record", "--target", LINE, "--rate", "48000", "--channels",
               "2", "--format", "s16", "OUT"], "file", "wav header finalize"),
    ("parec", ["parec", "-d", "@DEFAULT_SOURCE@", "--rate=48000",
               "--channels=2", "--format=s16le", "--file-format=wav", "OUT"],
     "file", "parecord wav header finalize"),
    ("arec-hw00", ["arecord", "-D", "hw:0,0", "-f", "S16_LE", "-r", "48000",
                   "-c", "2", "OUT"], "file", "hw capture header finalize"),
    ("ff-pulse", ["ffmpeg", "-hide_banner", "-nostdin", "-y", "-f", "pulse",
                  "-i", LINE, "OUT"], "file", "ffmpeg trailer on TERM"),
    ("ff-alsa-null", ["ffmpeg", "-hide_banner", "-nostdin", "-y", "-f",
                      "alsa", "-i", "null", "OUT"], "file",
     "ffmpeg alsa null trailer on TERM"),
]:
    ext = ".wav" if consumer.startswith("ff") else ".out"
    leg("sev1-%s" % consumer, argv, out=out, mode="term", wall_max=10.0,
        term_at=1.2, kill_at=3.2, note=note + " [TERM1]",
        out_name="sev1-%s%s" % (consumer, ext))
    leg("sev2-%s" % consumer, argv, out=out, mode="term", wall_max=10.0,
        term_at=1.2, kill_at=1.6, note=note + " [TERM2 @1.6]",
        out_name="sev2-%s%s" % (consumer, ext))

# ---- batch: output-name / format axis -------------------------------------
leg("name-pwrec-raw-ext-wav", ["pw-record", "--target", LINE,
                               "--sample-count", "4800", "--rate", "48000",
                               "--channels", "2", "--format", "s16", "OUT"],
    note=".wav default container", out_name="name-pwrec-raw-ext-wav.wav")
leg("name-pwrec-raw-ext-raw", ["pw-record", "--target", LINE, "--raw",
                               "--sample-count", "4800", "--rate", "48000",
                               "--channels", "2", "--format", "s16", "OUT"],
    note="-a/--raw into .raw name", out_name="name-pwrec-raw-ext-raw.raw")
leg("name-pwrec-container-raw", ["pw-record", "--target", LINE,
                                 "--container", "raw", "--sample-count",
                                 "4800", "--rate", "48000", "--channels",
                                 "2", "--format", "s16", "OUT"],
    note="--container raw into .wav name",
    out_name="name-pwrec-container-raw.wav")
leg("name-parec-raw-ext-wav", ["parec", "-d", "@DEFAULT_SOURCE@", "--raw",
                               "--rate=48000", "--channels=2",
                               "--format=s16le", "OUT"], out="stdout",
    mode="term", wall_max=6.0, note="parec --raw into .wav name",
    out_name="name-parec-raw-ext-wav.wav")
leg("name-parec-ff-wav", ["parec", "-d", "@DEFAULT_SOURCE@",
                          "--file-format=wav", "--rate=48000", "--channels=2",
                          "--format=s16le", "OUT"], out="file", mode="term",
    wall_max=6.0, note="--file-format=wav into .wav name",
    out_name="name-parec-ff-wav.wav")
leg("name-parec-ff-wav-ext-raw", ["parec", "-d", "@DEFAULT_SOURCE@",
                                  "--file-format=wav", "--rate=48000",
                                  "--channels=2", "--format=s16le", "OUT"],
    out="file", mode="term", wall_max=6.0, note="--file-format=wav into .raw",
    out_name="name-parec-ff-wav-ext-raw.raw")
leg("name-arec-t-wav", ["arecord", "-D", "null", "-d", "1", "-t", "wav",
                        "-f", "S16_LE", "-r", "48000", "-c", "2", "OUT"],
    note="arecord -t wav", out_name="name-arec-t-wav.wav")
leg("name-arec-t-raw", ["arecord", "-D", "null", "-d", "1", "-t", "raw",
                        "-f", "S16_LE", "-r", "48000", "-c", "2", "OUT"],
    note="arecord -t raw", out_name="name-arec-t-raw.raw")
leg("name-arec-t-raw-ext-wav", ["arecord", "-D", "null", "-d", "1", "-t",
                                "raw", "-f", "S16_LE", "-r", "48000", "-c",
                                "2", "OUT"], note="arecord -t raw, .wav name",
    out_name="name-arec-t-raw-ext-wav.wav")
leg("name-ff-alsa-null-fraw", ["ffmpeg", "-hide_banner", "-nostdin", "-y",
                               "-f", "alsa", "-i", "null", "-t", "1", "-f",
                               "s16le", "OUT"], note="ffmpeg -f s16le out",
    out_name="name-ff-alsa-null-fraw.raw")
leg("name-ff-alsa-null-fwav", ["ffmpeg", "-hide_banner", "-nostdin", "-y",
                               "-f", "alsa", "-i", "null", "-t", "1", "OUT"],
    note="ffmpeg wav out (default muxer)",
    out_name="name-ff-alsa-null-fwav.wav")

# ---- batch: round 2 — rc probes, flush timing, KILL-only sever -------------
# pw-record rc on a *complete* bounded capture (rc was 1 with full data).
leg("rc-pwrec-sc4800-v", ["pw-record", "-v", "--target", LINE,
                          "--sample-count", "4800", "--rate", "48000",
                          "--channels", "2", "--format", "s16", "OUT"],
    note="verbose, 0.1s bounded capture",
    out_name="rc-pwrec-sc4800-v.wav")
leg("rc-pwrec-sc48000", ["pw-record", "--target", LINE, "--sample-count",
                         "48000", "--rate", "48000", "--channels", "2",
                         "--format", "s16", "OUT"],
    note="1.0s bounded capture", out_name="rc-pwrec-sc48000.wav")
leg("rc-pwcat-r-sc4800", ["pw-cat", "-r", "--target", LINE, "--sample-count",
                          "4800", "--rate", "48000", "--channels", "2",
                          "--format", "s16", "OUT"],
    note="pw-cat -r explicit record mode",
    out_name="rc-pwcat-r-sc4800.wav")
leg("rc-pwrec-mon-sink", ["pw-record", "--target", SINK, "-P",
                          "stream.capture.sink=true", "--sample-count",
                          "48000", "--rate", "48000", "--channels", "2",
                          "--format", "s16", "OUT"],
    note="monitor capture via sink+property, 1s",
    out_name="rc-pwrec-mon-sink.wav")
# parec flush timing on stdout (TERM at increasing offsets) + KILL-only.
for off in ("0.5", "1.0", "1.5", "2.0", "3.0"):
    leg("flush-parec-term-%s" % off, ["parec", "-d", "@DEFAULT_SOURCE@",
                                      "--rate=48000", "--channels=2",
                                      "--format=s16le", "--raw", "OUT"],
        out="stdout", mode="term", wall_max=8.0, term_at=float(off),
        kill_at=float(off) + 2.0, note="TERM at %ss" % off,
        out_name="flush-parec-term-%s.wav" % off)
leg("flush-parec-kill-1.2", ["parec", "-d", "@DEFAULT_SOURCE@",
                             "--rate=48000", "--channels=2",
                             "--format=s16le", "--raw", "OUT"], out="stdout",
    mode="term", wall_max=8.0, term_at=99.0, kill_at=1.2,
    note="SIGKILL only at 1.2s", out_name="flush-parec-kill-1.2.wav")
# KILL-only sever for every consumer (header state after an ungraceful kill).
for consumer, argv, note in [
    ("pwrec", ["pw-record", "--target", LINE, "--rate", "48000", "--channels",
               "2", "--format", "s16", "OUT"], "pw-record SIGKILL only"),
    ("parec-wav", ["parec", "-d", "@DEFAULT_SOURCE@", "--rate=48000",
                   "--channels=2", "--format=s16le", "--file-format=wav",
                   "OUT"], "parecord --file-format=wav SIGKILL only"),
    ("arec-hw00", ["arecord", "-D", "hw:0,0", "-f", "S16_LE", "-r", "48000",
                   "-c", "2", "OUT"], "arecord hw SIGKILL only"),
    ("ff-pulse", ["ffmpeg", "-hide_banner", "-nostdin", "-y", "-f", "pulse",
                  "-i", LINE, "OUT"], "ffmpeg pulse SIGKILL only"),
]:
    leg("kill-%s" % consumer, argv, mode="term", wall_max=8.0, term_at=99.0,
        kill_at=1.2, note=note, out_name="kill-%s.wav" % consumer)
# ffmpeg: does the wav muxer hold a trailer hostage on TERM?  (real source)
leg("sev-ff-pulse-term-1.2", ["ffmpeg", "-hide_banner", "-nostdin", "-y",
                              "-f", "pulse", "-i", LINE, "OUT"], mode="term",
    wall_max=8.0, term_at=1.2, kill_at=3.2,
    note="ffmpeg pulse, TERM at 1.2s (no -t)",
    out_name="sev-ff-pulse-term-1.2.wav")
leg("sev-ff-pulse-term-2.5", ["ffmpeg", "-hide_banner", "-nostdin", "-y",
                              "-f", "pulse", "-i", LINE, "OUT"], mode="term",
    wall_max=8.0, term_at=2.5, kill_at=4.5,
    note="ffmpeg pulse, TERM at 2.5s (no -t)",
    out_name="sev-ff-pulse-term-2.5.wav")
# ffmpeg with explicit raw muxer on a *real* source (byte-cap semantics).
leg("cap-ff-pulse-raw-t1", ["ffmpeg", "-hide_banner", "-nostdin", "-y", "-f",
                            "pulse", "-i", LINE, "-t", "1", "-f", "s16le",
                            "OUT"], note="ffmpeg pulse -> raw s16le, -t 1",
    out_name="cap-ff-pulse-raw-t1.raw")
leg("cap-ff-pulse-raw-t2", ["ffmpeg", "-hide_banner", "-nostdin", "-y", "-f",
                            "pulse", "-i", LINE, "-t", "2", "-f", "s16le",
                            "OUT"], note="ffmpeg pulse -> raw s16le, -t 2",
    out_name="cap-ff-pulse-raw-t2.raw")
leg("cap-ff-pulse-t2", ["ffmpeg", "-hide_banner", "-nostdin", "-y", "-f",
                        "pulse", "-i", LINE, "-t", "2", "OUT"],
    note="ffmpeg pulse -> wav, -t 2", out_name="cap-ff-pulse-t2.wav")
# arecord duration axis at 2ch (d1 vs d0 vs no -d) on the real device.
leg("cap-arec-hw00-d1", ["arecord", "-D", "hw:0,0", "-d", "1", "-f",
                         "S16_LE", "-r", "48000", "-c", "2", "OUT"],
    note="hw device, -d 1", out_name="cap-arec-hw00-d1.wav")
leg("cap-arec-hw00-d0", ["arecord", "-D", "hw:0,0", "-d", "0", "-f", "S16_LE",
                         "-r", "48000", "-c", "2", "OUT"], mode="term",
    wall_max=6.0, note="hw device, -d 0 (TERM at 1.2s)",
    out_name="cap-arec-hw00-d0.wav")
leg("cap-arec-hw00-nod", ["arecord", "-D", "hw:0,0", "-f", "S16_LE", "-r",
                          "48000", "-c", "2", "OUT"], mode="term",
    wall_max=6.0, note="hw device, no -d (TERM at 1.2s)",
    out_name="cap-arec-hw00-nod.wav")
# parec wav-to-file: is the RIFF header patched on a natural (bounded) exit?
leg("cap-parec-ff-wav-term-2.5", ["parec", "-d", "@DEFAULT_SOURCE@",
                                  "--rate=48000", "--channels=2",
                                  "--format=s16le", "--file-format=wav",
                                  "OUT"], out="file", mode="term",
    wall_max=8.0, term_at=2.5, kill_at=4.5,
    note="parecord wav, TERM at 2.5s",
    out_name="cap-parec-ff-wav-term-2.5.wav")

# ---------------------------------------------------------------- harness

def wav_fields(path):
    try:
        with open(path, "rb") as fh:
            head = fh.read(64)
        if len(head) < 12:
            return {"magic": head[:4].decode("latin1", "replace"),
                    "short": len(head)}
        out = {"magic": head[:4].decode("latin1", "replace"),
               "form": head[8:12].decode("latin1", "replace")}
        if out["magic"] == "RIFF" and len(head) >= 44:
            out["riff_size"] = int.from_bytes(head[4:8], "little")
            out["fmt_size"] = int.from_bytes(head[16:20], "little")
            out["data_tag"] = head[36:40].decode("latin1", "replace")
            out["data_size"] = int.from_bytes(head[40:44], "little")
        return out
    except FileNotFoundError:
        return {"absent": True}


def scrub(text, limit=3):
    lines = [ln for ln in text.splitlines() if ln.strip()]
    lines = [ln.replace(LEGS, "<legs>").replace(HERE, "<scout>") for ln in lines]
    return lines[-limit:]


def run_leg(spec):
    lid = spec["id"]
    out_path = os.path.join(LEGS, spec["out_name"])
    for suffix in (".out", ".stdout"):
        p = os.path.join(LEGS, lid + suffix)
        if os.path.exists(p):
            os.remove(p)
    if os.path.exists(out_path):
        os.remove(out_path)
    argv = [out_path if a == "OUT" else a for a in spec["argv"]]
    env = dict(os.environ)
    env.update(spec["env"])
    stdout_target = subprocess.PIPE
    fh = None
    if spec["out"] == "stdout":
        fh = open(out_path, "wb", buffering=0)
        stdout_target = fh
    t0 = time.monotonic()
    proc = subprocess.Popen(argv, stdout=stdout_target,
                            stderr=subprocess.PIPE, env=env,
                            start_new_session=True, cwd=LEGS)
    term_sent = None
    kill_sent = None
    rc = None
    while True:
        rc = proc.poll()
        el = time.monotonic() - t0
        if rc is not None:
            break
        if spec["mode"] == "term" and term_sent is None and el >= spec["term_at"]:
            try:
                os.killpg(proc.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            term_sent = round(el, 3)
        if spec["mode"] == "term" and kill_sent is None and el >= spec["kill_at"]:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            kill_sent = round(el, 3)
        if el > spec["wall_max"]:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.wait()
            rc = proc.returncode
            break
        time.sleep(0.01)
    wall = round(time.monotonic() - t0, 3)
    err = proc.stderr.read().decode("utf-8", "replace")
    proc.stderr.close()
    if fh:
        fh.flush()
        os.fsync(fh.fileno())
        fh.close()
    size = os.path.getsize(out_path) if os.path.exists(out_path) else 0
    sha = None
    if size:
        h = hashlib.sha256()
        with open(out_path, "rb") as f2:
            for chunk in iter(lambda: f2.read(1 << 20), b""):
                h.update(chunk)
        sha = h.hexdigest()[:16]
    rec = {"id": lid, "argv": argv, "mode": spec["mode"], "rc": rc,
           "wall_s": wall, "term_sent_at": term_sent, "kill_sent_at": kill_sent,
           "out_bytes": size, "out_sha16": sha,
           "wav": wav_fields(out_path), "stderr_tail": scrub(err),
           "note": spec["note"], "env": spec["env"]}
    return rec


def main():
    batch = sys.argv[1] if len(sys.argv) > 1 else "all"
    flt = sys.argv[2] if len(sys.argv) > 2 else None
    specs = [s for s in LEGS_SPEC if flt is None or flt in s["id"]]
    recs = []
    for s in specs:
        try:
            r = run_leg(s)
        except Exception as exc:  # keep the batch alive
            r = {"id": s["id"], "harness_error": repr(exc), "note": s["note"]}
        recs.append(r)
        print("%-28s rc=%-5s wall=%-6s bytes=%-9s %s" % (
            r["id"], r.get("rc"), r.get("wall_s"), r.get("out_bytes"),
            (r.get("wav") or {}).get("data_size", "")))
        sys.stdout.flush()
    dest = os.path.join(RUNS, "scout-capture-%s.json" % batch)
    payload = {"batch": batch, "host": os.uname().nodename,
               "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "filter": flt, "legs": recs}
    with open(dest, "w") as fh:
        json.dump(payload, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print("wrote %s (%d legs)" % (dest, len(recs)))


if __name__ == "__main__":
    main()
