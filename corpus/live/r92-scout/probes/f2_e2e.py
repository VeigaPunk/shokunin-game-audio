#!/usr/bin/env python3
"""f2 — end-to-end pipeline verification for the filter-chain as an effect sink.

Arms: null-sink source -> filter-chain capture (media.class=Audio/Sink) ->
filter-chain playback -> null-sink out -> pw-record. Verifies link rc, captured
bytes, peak, and the exact port names at each hop.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pwlib as L
import driver as D

res = {"probe": "f2", "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
tone = os.path.join(D.SCRATCH, "tone.wav")
L.write_wav(tone, L.multitone(D.TONE_FREQS, 1.0, rate=D.RATE, amp=0.2), rate=D.RATE, ch=1)
res["tone"] = tone

ARGS = D.fckwargs([D.NODE("bq_lowpass", Freq=1000.0, Q=0.707)],
                  capture_props="node.name=%s,node.autoconnect=false,media.class=Audio/Sink" % D.FC_IN,
                  playback_props="node.name=%s,node.autoconnect=false" % D.FC_OUT)
res["args"] = ARGS

p = D.Pipeline("f2", ARGS)
p.arm(link=False)
time.sleep(0.8)
res["census_armed"] = D.census("f2-armed")
res["load_out"] = p.load_out[-400:]
res["fc_log"] = p.fc_log()
res["fc_module_var"] = p.fc_module_var

# wait-and-see: do the ports appear later?
time.sleep(2.0)
res["census_after_2s"] = D.census("f2-2s")

recpath = os.path.join(D.SCRATCH, "f2_out.wav")
if os.path.exists(recpath):
    os.unlink(recpath)
rec = D.Bg(["pw-record", "--channels", "1", "-P", "node.name=%s" % D.RECN,
            "-P", "node.autoconnect=false", recpath], wall=14.0)
time.sleep(0.8)
res["census_rec"] = D.census("f2-rec")

play = D.Bg(["pw-play", "-P", "node.name=%s" % D.PLAY,
             "-P", "node.autoconnect=false", tone], wall=12.0)
time.sleep(0.8)
res["census_play"] = D.census("f2-play")

# every hop, with the verbatim rc/err
hops = [
    ("feed-handlink-into-fc-sink", f"{D.NS_IN}:monitor_MONO", f"{D.FC_IN}:playback_MONO"),
    ("feed-handlink-fl-fallback", f"{D.NS_IN}:monitor_MONO", f"{D.FC_IN}:playback_FL"),
    ("tone-into-null-sink", f"{D.PLAY}:output_MONO", f"{D.NS_IN}:playback_MONO"),
    ("fc-out-into-null-sink", f"{D.FC_OUT}:output_MONO", f"{D.NS_OUT}:playback_MONO"),
    ("null-sink-monitor-to-rec", f"{D.NS_OUT}:monitor_MONO", f"{D.RECN}:input_MONO"),
]
res["hops"] = []
for tag, a, b in hops:
    r = L.run(["pw-link", a, b], wall=5.0)
    res["hops"].append({"tag": tag, "argv": [a, b], "rc": r.rc,
                        "err": r.err.strip(), "out": r.out.strip()[:200]})
    time.sleep(0.25)

# alternative feed: pw-play straight at the FC sink by name (WP target resolution)
alt = D.Bg(["pw-play", "--target", D.FC_IN, "-P", "node.name=r92s_alt",
            tone], wall=12.0)
time.sleep(1.0)
lk = L.run(["pw-link", "-l"], wall=5.0).out
res["links_with_alt_play"] = [l.strip() for l in lk.splitlines() if "r92s" in l or "SPDIF" in l]
res["alt_play_alive"] = alt.alive()
res["alt_play_out"] = alt.stop()
res["play_out"] = play.stop()
time.sleep(0.4)
res["rec_out"] = rec.stop()
time.sleep(0.5)
res["rec_bytes"] = os.path.getsize(recpath) if os.path.exists(recpath) else 0
if res["rec_bytes"] > 1000:
    w = L.read_wav(recpath)
    x = w["x"][0]
    res["rec_frames"] = w["frames"]
    res["rec_peak"] = round(max(abs(v) for v in x), 6)
    res["rec_rms"] = round((sum(v * v for v in x) / len(x)) ** 0.5, 6)
    res["rec_gain_db"] = L.dft_mags(x[int(0.6 * w["rate"]):int(0.6 * w["rate"]) + 24000], D.TONE_FREQS, D.RATE)
    ref = L.read_wav(tone)["x"][0]
    refm = L.dft_mags(ref[:24000], D.TONE_FREQS, D.RATE)
    res["gain_db"] = {str(f): round(20 * L.math.log10(max(1e-12, res["rec_gain_db"][f]) / max(1e-12, refm[f])), 3)
                      for f in D.TONE_FREQS}
res["teardown"] = p.disarm()
res["final"] = D.census("f2-final")
L.jdump(os.path.join(D.REC, "f2_e2e.json"), res)

print("hops:", json.dumps(res["hops"], indent=0))
print("armed nodes:", [(n["name"], n["class"], n["ports"]) for n in res["census_armed"]["nodes"]])
print("after2s nodes:", [(n["name"], n["ports"]) for n in res["census_after_2s"]["nodes"]])
print("rec_bytes", res["rec_bytes"], "peak", res.get("rec_peak"), "gain_db", res.get("gain_db"))
print("links_with_alt_play:", res["links_with_alt_play"])
print("teardown exit:", res["teardown"].get("nodes_at_exit"), "stray:", res["teardown"].get("stray_procs"))
