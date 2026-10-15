#!/usr/bin/env python3
"""f3 — driver law: which topology actually runs, and why.

Arms (all seat-local, no host sink):
  S1 one null sink (driver) -> FC -> record directly from the FC playback stream
  S2 two null sinks (the f2 shape)                          [negative control]
  S3 two null sinks + playback.props node.passive=true      [mechanism test]
  S4 one null sink + capture.props media.class=Audio/Sink   [shipped-config shape]
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pwlib as L
import driver as D

res = {"probe": "f3", "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
tone = os.path.join(D.SCRATCH, "tone.wav")
if not os.path.exists(tone):
    L.write_wav(tone, L.multitone(D.TONE_FREQS, 1.0, rate=D.RATE, amp=0.2), rate=D.RATE, ch=1)
ref = L.read_wav(tone)["x"][0]
refm = L.dft_mags(ref[:24000], D.TONE_FREQS, D.RATE)


def driver_census(tag):
    d = L.run(["pw-dump"], wall=6.0)
    objs = json.loads(d.out)
    rows = []
    for o in objs:
        if o.get("type") != "PipeWire:Interface:Node":
            continue
        p = o.get("info", {}).get("props", {})
        nm = p.get("node.name", "")
        if not (nm.startswith("r92s") or nm.startswith("filter-chain-")
                or nm.startswith("input.") or nm.startswith("output.")
                or p.get("node.description") == "r92s_fc"):
            continue
        rows.append({"name": nm, "driver": p.get("node.driver"),
                     "passive": p.get("node.passive"),
                     "state": o.get("info", {}).get("state"),
                     "class": p.get("media.class"),
                     "ports": sorted(q["info"]["props"].get("port.name")
                                     for q in objs if q.get("type") == "PipeWire:Interface:Port"
                                     and q["info"]["props"].get("node.id") == o["id"])})
    return {"tag": tag, "nodes": rows}


def run_shape(tag, args, sink_names, hops, recpath, tone_dur=1.0):
    out = {"tag": tag, "args": args, "hops": []}
    sinks = {n: D.sink_load(n) for n in sink_names}
    cli = L.PwCli(env={"PIPEWIRE_DEBUG": "3"})
    lo, var = cli.load("libpipewire-module-filter-chain", args)
    out["load_out"] = lo[-300:]
    out["fc_var"] = var
    time.sleep(0.7)
    if os.path.exists(recpath):
        os.unlink(recpath)
    rec = D.Bg(["pw-record", "--channels", "1", "-P", "node.name=%s" % D.RECN,
                "-P", "node.autoconnect=false", recpath], wall=14.0)
    time.sleep(0.8)
    play = D.Bg(["pw-play", "-P", "node.name=%s" % D.PLAY,
                 "-P", "node.autoconnect=false", tone], wall=12.0)
    time.sleep(0.8)
    for htag, a, b in hops:
        r = L.run(["pw-link", a, b], wall=5.0)
        out["hops"].append({"tag": htag, "argv": [a, b], "rc": r.rc, "err": r.err.strip()})
        time.sleep(0.25)
    out["census_running"] = driver_census(tag + "-run")
    t0 = time.time()
    while play.alive() and time.time() - t0 < 8:
        time.sleep(0.1)
    out["play"] = play.stop()
    time.sleep(0.4)
    out["rec"] = rec.stop()
    time.sleep(0.4)
    out["rec_bytes"] = os.path.getsize(recpath) if os.path.exists(recpath) else 0
    if out["rec_bytes"] > 1000:
        w = L.read_wav(recpath)
        x = w["x"][0]
        skip = int(0.6 * w["rate"])
        seg = x[skip:skip + 24000] if len(x) >= skip + 24000 else x[-24000:]
        mags = L.dft_mags(seg, D.TONE_FREQS, D.RATE)
        out["mags"] = mags
        out["gain_db"] = {str(f): round(20 * L.math.log10(max(1e-12, mags[f]) / max(1e-12, refm[f])), 3)
                          for f in D.TONE_FREQS}
        out["peak"] = round(max(abs(v) for v in seg), 6)
        out["frames"] = w["frames"]
    # teardown
    lk = L.run(["pw-link", "-l"], wall=5.0).out
    out["links"] = [l.strip() for l in lk.splitlines() if "r92s" in l]
    out["fc_log"] = [l for l in "".join(cli.log).splitlines()
                     if "[E]" in l or "[W]" in l or "graph rate" in l][:20]
    try:
        if var is not None:
            out["unload"] = cli.cmd("unload-module %d" % var)[-200:]
        out["cli_close"] = cli.close()
    except Exception as e:
        out["cli_error"] = repr(e)
        try:
            os.killpg(os.getpgid(cli.p.pid), 9)
        except Exception:
            pass
    time.sleep(0.5)
    out["after_exit"] = driver_census(tag + "-exit")
    out["sink_unload"] = [D.sink_unload(n, sinks[n]["id"]) for n in sinks]
    out["stray"] = D.stray_procs()
    return out


ARGS_PLAIN = D.fckwargs([D.NODE("bq_lowpass", Freq=1000.0, Q=0.707)],
                        capture_props="node.name=%s,node.autoconnect=false,media.class=Audio/Sink" % D.FC_IN,
                        playback_props="node.name=%s,node.autoconnect=false" % D.FC_OUT)
ARGS_PASSIVE = D.fckwargs([D.NODE("bq_lowpass", Freq=1000.0, Q=0.707)],
                          capture_props="node.name=%s,node.autoconnect=false,media.class=Audio/Sink" % D.FC_IN,
                          playback_props="node.name=%s,node.autoconnect=false,node.passive=true" % D.FC_OUT)
ARGS_PLAYBACK_SINK = D.fckwargs([D.NODE("bq_lowpass", Freq=1000.0, Q=0.707)],
                                capture_props="node.name=%s,node.autoconnect=false" % D.FC_IN,
                                playback_props="node.name=%s,node.autoconnect=false,media.class=Audio/Sink" % D.FC_OUT)

res["S1"] = run_shape("S1-one-sink-direct-rec", ARGS_PLAIN, [D.NS_IN], [
    ("tone-into-null-sink", f"{D.PLAY}:output_MONO", f"{D.NS_IN}:playback_MONO"),
    ("sink-monitor-into-fc", f"{D.NS_IN}:monitor_MONO", f"{D.FC_IN}:playback_MONO"),
    ("fc-out-direct-to-rec", f"{D.FC_OUT}:output_MONO", f"{D.RECN}:input_MONO"),
], os.path.join(D.SCRATCH, "f3_s1.wav"))

res["S2"] = run_shape("S2-two-sinks", ARGS_PLAIN, [D.NS_IN, D.NS_OUT], [
    ("tone-into-null-sink", f"{D.PLAY}:output_MONO", f"{D.NS_IN}:playback_MONO"),
    ("sink-monitor-into-fc", f"{D.NS_IN}:monitor_MONO", f"{D.FC_IN}:playback_MONO"),
    ("fc-out-into-out-sink", f"{D.FC_OUT}:output_MONO", f"{D.NS_OUT}:playback_MONO"),
    ("out-sink-monitor-to-rec", f"{D.NS_OUT}:monitor_MONO", f"{D.RECN}:input_MONO"),
], os.path.join(D.SCRATCH, "f3_s2.wav"))

res["S3"] = run_shape("S3-two-sinks-passive-playback", ARGS_PASSIVE, [D.NS_IN, D.NS_OUT], [
    ("tone-into-null-sink", f"{D.PLAY}:output_MONO", f"{D.NS_IN}:playback_MONO"),
    ("sink-monitor-into-fc", f"{D.NS_IN}:monitor_MONO", f"{D.FC_IN}:playback_MONO"),
    ("fc-out-into-out-sink", f"{D.FC_OUT}:output_MONO", f"{D.NS_OUT}:playback_MONO"),
    ("out-sink-monitor-to-rec", f"{D.NS_OUT}:monitor_MONO", f"{D.RECN}:input_MONO"),
], os.path.join(D.SCRATCH, "f3_s3.wav"))

try:
    res["S4"] = run_shape("S4-playback-as-sink", ARGS_PLAYBACK_SINK, [D.NS_IN], [
    ("tone-into-null-sink", f"{D.PLAY}:output_MONO", f"{D.NS_IN}:playback_MONO"),
    ("sink-monitor-into-fc", f"{D.NS_IN}:monitor_MONO", f"{D.FC_IN}:input_MONO"),
], os.path.join(D.SCRATCH, "f3_s4.wav"))
except Exception as e:
    res["S4_error"] = repr(e)

L.jdump(os.path.join(D.REC, "f3_driver.json"), res)
for k in ("S1", "S2", "S3", "S4"):
    r = res.get(k)
    if not r:
        print("== %s MISSING: %s" % (k, res.get(k + "_error"))); continue
    print("== %-34s bytes=%-8d gain=%s peak=%s frames=%s" %
          (r["tag"], r["rec_bytes"], r.get("gain_db"), r.get("peak"), r.get("frames")))
    print("   states:", [(n["name"], n["state"], "drv=%s" % n["driver"], "pas=%s" % n["passive"]) for n in r["census_running"]["nodes"]])
    print("   hops:", [(h["tag"], h["rc"]) for h in r["hops"]], "stray:", r["stray"])
print("final nodes:", [(n["name"], n["state"]) for n in res["S4"]["after_exit"]["nodes"]])
