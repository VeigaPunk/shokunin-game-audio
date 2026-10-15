#!/usr/bin/env python3
"""f4 — wpexec (WirePlumber script interpreter) as an ad-hoc graph/loader surface.

Legs (each triple-bounded: element bound in argv, wall cap, byte cap):
  W1 hello + Core.quit                 -> rc / stdout grammar
  W2 globals inventory                 -> what the interpreter exposes
  W3 Settings read                     -> cross-witness of the r90 25-key lattice
  W4 LocalModule(filter-chain)         -> can a script load a DSP graph?
  W5 no-quit / bad file / syntax error -> failure classes
  W6 residue law                       -> modules/nodes/defaults before vs after
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pwlib as L
import driver as D
import driver2 as D2

SCR = D.SCRATCH
REC = D.REC


def w(name, body):
    p = os.path.join(SCR, name)
    open(p, "w").write(body)
    return p


S_HELLO = w("w1_hello.lua", 'print("r92s hello from wpexec")\nCore.quit()\n')

S_GLOBALS = w("w2_globals.lua", r'''
local names = { "Core", "Settings", "Log", "LocalModule", "PipewireObject",
                "ObjectManager", "SessionItem", "EventDispatcher", "Script",
                "Components", "Metadata", "Node", "Device", "Client", "Link",
                "Plugin", "Conf", "Json", "Utils", "Debug", "Loop", "Timer" }
for _, n in ipairs(names) do
  local v = rawget(_G, n)
  print(string.format("GLOBAL %s type=%s", n, type(v)))
end
print("_VERSION " .. tostring(_VERSION))
Core.quit()
''')

S_SETTINGS = w("w3_settings.lua", r'''
print("api=" .. tostring(Core.require_api("support.settings")))
local keys = { "node.stream.restore-props", "node.stream.restore-target",
               "device.routes.default-sink-volume", "device.routes.default-source-volume",
               "node.restore-default-targets", "device.restore-profile",
               "bluetooth.use-persistent-storage", "node.features.audio.monitor-ports" }
for _, k in ipairs(keys) do
  local b = Settings.get_boolean(k)
  local f = Settings.get_float(k)
  local s = Settings.get_string(k)
  print(string.format("SET %s bool=%s float=%s str=%s", k, tostring(b), tostring(f), tostring(s)))
end
Core.quit()
''')

S_LOCALMODULE = w("w4_localmodule.lua", r'''
print("LocalModule type=" .. type(LocalModule))
local args = "node.description=r92s_wpx,filter.graph={nodes=[{type=builtin,name=n0,label=copy}]},audio.channels=1,audio.position=[MONO],capture.props={node.name=r92s_wpx_in,node.autoconnect=false,media.class=Audio/Sink},playback.props={node.name=r92s_wpx_out,node.autoconnect=false}"
local ok, mod = pcall(LocalModule, "libpipewire-module-filter-chain", args)
print("LocalModule pcall ok=" .. tostring(ok) .. " mod=" .. tostring(mod))
if ok and mod then
  print("mod type=" .. type(mod) .. " name=" .. tostring(mod.name))
end
Core.quit()
''')

S_NOQUIT = w("w5_noquit.lua", 'print("r92s no quit here")\n')

S_BAD = w("w6_syntax.lua", 'this is not lua at all (((\n')


def census():
    d = L.run(["pw-dump"], wall=6.0)
    try:
        objs = json.loads(d.out)
    except Exception:
        objs = []
    nodes = sorted(o["info"]["props"].get("node.name", "") for o in objs
                   if o.get("type") == "PipeWire:Interface:Node")
    mods = []
    for l in L.run(["pactl", "list", "modules", "short"], wall=6.0).out.splitlines():
        t = l.split()
        if len(t) >= 2:
            mods.append(t[0] + ":" + t[1])
    mods = sorted(mods)
    return {"n_nodes": len(nodes), "n_modules": len(mods),
            "r92s_nodes": [n for n in nodes if "r92s" in n],
            "r92s_mods": [m for m in mods if "r92s" in m],
            "default_sink": L.run(["pactl", "get-default-sink"], wall=5.0).out.strip()}


res = {"probe": "f4_wpexec", "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
res["wpexec"] = {"which": L.run(["which", "wpexec"], wall=5.0).out.strip(),
                 "man": L.run(["man", "-w", "wpexec"], wall=5.0).out.strip()}
res["before"] = census()

legs = [
    ("W1-hello", ["wpexec", S_HELLO], 8.0),
    ("W2-globals", ["wpexec", S_GLOBALS], 8.0),
    ("W3-settings", ["wpexec", S_SETTINGS], 8.0),
    ("W4-localmodule", ["wpexec", S_LOCALMODULE], 10.0),
    ("W5-noquit", ["wpexec", S_NOQUIT], 4.0),
    ("W6-badscript", ["wpexec", S_BAD], 8.0),
    ("W7-missing-file", ["wpexec", "/nonexistent/r92s.lua"], 8.0),
    ("W8-noargs", ["wpexec"], 8.0),
]
res["legs"] = {}
for name, argv, wall in legs:
    rows = []
    for rep in range(3):
        b = L.run(argv, wall=wall)
        rows.append({"rep": rep, "rc": b.rc, "dur": round(b.dur, 3),
                     "timed_out": b.timed_out, "out": b.out[-2500:], "err": b.err[-1500:]})
        print("%-16s r%d rc=%-4s dur=%.2f timedout=%s | %s" %
              (name, rep, b.rc, b.dur, b.timed_out,
               (b.out or b.err).strip().replace("\n", " | ")[:150]))
    res["legs"][name] = {"argv": argv, "rows": rows}
    res["census_after_" + name] = census()

# does wpexec's LocalModule object survive the interpreter?
res["after"] = census()
res["sweep"] = D2.sweep()
res["final"] = census()
L.jdump(os.path.join(REC, "f4_wpexec.json"), res)
print("BEFORE:", json.dumps(res["before"]))
print("AFTER :", json.dumps(res["after"]))
print("FINAL :", json.dumps(res["final"]), "sweep clean:", res["sweep"]["clean"])
