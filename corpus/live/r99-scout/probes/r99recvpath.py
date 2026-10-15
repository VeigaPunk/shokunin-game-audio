#!/usr/bin/env python3
"""r99-scout: manual receive-path probe — rtp-source on multicast-lo, pw-record,
explicit pw-link if WirePlumber does not link. Prints ports/links and the wav analysis.
"""
import json, os, sys, time

SEAT = os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, SEAT)
import r99_probe as P

P.write_fragment([("libpipewire-module-rtp-source", P.source_args())])
ok, msg = P.core_up(with_wp=True)
print("core:", ok, msg)
print("nodes:", [(n["props"].get("node.name"), n["state"]) for n in P.nodes()])
print("wpctl sources:")
print(P.sh("wpctl status", timeout=6)[1])
wav = os.path.join(P.RAW, "d", "manual.wav")
rec = P.record(wav, "r99s_src", seconds=8)
time.sleep(1.5)
print("ports -o:", P.sh("pw-link -o", timeout=6)[1].splitlines())
print("ports -i:", P.sh("pw-link -i", timeout=6)[1].splitlines())
print("nodes:", [(n["id"], n["props"].get("node.name"), n["state"], n["n_in"], n["n_out"]) for n in P.nodes()])
send = P.sender(46101, 3.0, group="239.255.42.99", ifname="lo", count=3000)
time.sleep(1.0)
# try explicit links
for pair in (("r99s_src:output_FL", "r99s_rec:input_FL"), ("r99s_src:output_FR", "r99s_rec:input_FR")):
    print("link", pair, "->", P.sh("pw-link " + " ".join(pair), timeout=6)[1:])
time.sleep(2.5)
print("links now:", P.sh("pw-link -l", timeout=6)[1].splitlines())
send.wait(timeout=8)
print("send:", send.stdout.read().decode().strip())
time.sleep(1.0)
P.kill(rec)
time.sleep(0.3)
print("wav:", json.dumps(P.wav_analyze(wav)))
print("wp log tail:", P.sh("tail -5 " + os.path.join(SEAT, "runs", "wp.log"), timeout=6)[1])
P.core_down()
