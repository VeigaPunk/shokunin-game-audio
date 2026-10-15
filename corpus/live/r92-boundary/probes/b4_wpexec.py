#!/usr/bin/env python3
"""B4 — wpexec error classes, the bare-`Lua runtime error` narrowing, and residue
on the ERROR path (the scout measured residue only on the clean-exit path).

argv[1] = reps (default 3).
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig as R

S = R.SCRATCH
ARGS = ("node.description=r92b_wpx,filter.graph={nodes=[{type=builtin,name=n0,label=copy}]},"
        "audio.channels=1,audio.position=[MONO],"
        "capture.props={node.name=r92b_wpx_in,node.autoconnect=false,media.class=Audio/Sink},"
        "playback.props={node.name=r92b_wpx_out,node.autoconnect=false}")

SCRIPTS = {
    "hello": "print('r92b hello')\nCore.quit()\n",
    "noquit": "print('r92b no quit here')\n",
    "syntax": "this is not lua at all (((\n",
    "ladder-version": "print(_VERSION)\nCore.quit()\n",
    "ladder-core": "print('Core=' .. type(Core))\nCore.quit()\n",
    "ladder-localmodule": "print('LocalModule=' .. type(LocalModule))\nCore.quit()\n",
    "ladder-settings": "print('Settings=' .. type(Settings))\nCore.quit()\n",
    "ladder-require-api": "print('require_api=' .. type(require_api))\nCore.quit()\n",
    "ladder-rawget": "print('rawget=' .. type(rawget(_G, 'Core')))\nCore.quit()\n",
    "ladder-pairs": "local t = {}\nfor _, n in ipairs({'Core','Settings'}) do t[#t+1] = n end\nprint('ipairs ok ' .. #t)\nCore.quit()\n",
    "ladder-format": "print(string.format('GLOBAL %s type=%s', 'Core', type(Core)))\nCore.quit()\n",
    "ladder-settings-get": "print('get=' .. tostring(Settings.get_boolean('node.stream.restore-props')))\nCore.quit()\n",
    "ladder-core-require": "print('api=' .. tostring(Core.require_api('support.settings')))\nCore.quit()\n",
    "w2-full": ("local names = { 'Core', 'Settings', 'Log', 'LocalModule', 'PipewireObject',\n"
                "  'ObjectManager', 'SessionItem', 'EventDispatcher', 'Script', 'Components',\n"
                "  'Metadata', 'Node', 'Device', 'Client', 'Link', 'Plugin', 'Conf', 'Json',\n"
                "  'Utils', 'Debug', 'Loop', 'Timer' }\n"
                "for _, n in ipairs(names) do\n"
                "  local v = rawget(_G, n)\n"
                "  print(string.format('GLOBAL %s type=%s', n, type(v)))\n"
                "end\nprint('_VERSION ' .. tostring(_VERSION))\nCore.quit()\n"),
    "lm-ok": ("local ok, mod = pcall(LocalModule, 'libpipewire-module-filter-chain', [==[%s]==])\n"
              "print('lm-ok pcall ok=' .. tostring(ok) .. ' mod=' .. tostring(mod))\n"
              "Core.timeout_add(2200, function() Core.quit() end)\n" % ARGS),
    "lm-badlabel": ("local ok, mod = pcall(LocalModule, 'libpipewire-module-filter-chain', [==[%s]==])\n"
                    "print('lm-badlabel pcall ok=' .. tostring(ok) .. ' mod=' .. tostring(mod))\n"
                    "Core.timeout_add(2200, function() Core.quit() end)\n"
                    % ARGS.replace("label=copy", "label=not_a_filter")),
    "lm-badmodule": ("local ok, mod = pcall(LocalModule, 'libpipewire-module-nope', 'x=1')\n"
                     "print('lm-badmodule pcall ok=' .. tostring(ok) .. ' mod=' .. tostring(mod))\n"
                     "Core.quit()\n"),
    "lm-error-after-load": ("local ok, mod = pcall(LocalModule, 'libpipewire-module-filter-chain', [==[%s]==])\n"
                            "print('lm-err pcall ok=' .. tostring(ok))\n"
                            "Core.timeout_add(1800, function() error('r92b boom') end)\n" % ARGS),
    "runtime-error": "print('before')\nlocal x = nil\nprint(x.y)\nCore.quit()\n",
}


def write_scripts():
    paths = {}
    for name, body in SCRIPTS.items():
        p = os.path.join(S, "r92b_wx_%s.lua" % name)
        with open(p, "w") as f:
            f.write(body)
        paths[name] = p
    return paths


def main():
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    t0 = time.time()
    paths = write_scripts()
    pf = R.preflight()
    out = {"stage": "b4_wpexec", "reps": reps, "preflight": pf, "args": ARGS,
           "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "legs": {}}

    # 1. rc classes (bounded, no graph contact)
    for name in ("hello", "syntax", "ladder-version", "ladder-core", "ladder-localmodule",
                 "ladder-settings", "ladder-require-api", "ladder-rawget", "ladder-pairs",
                 "ladder-format", "ladder-settings-get", "ladder-core-require", "w2-full",
                 "runtime-error", "lm-badmodule"):
        rows = []
        for rep in range(reps):
            r = R.run(["wpexec", paths[name]], wall=6.0)
            rows.append(r.d())
            print("b4 %-22s r%d rc=%-4s dur=%-6s out=%r err=%r" %
                  (name, rep, r.rc, r.dur, r.out.strip()[:110], r.err.strip()[:110]))
        out["legs"][name] = {"script": paths[name], "rows": rows}

    # 2. legs that hold a live graph: census during, residue after
    for name in ("noquit", "lm-ok", "lm-badlabel", "lm-error-after-load"):
        rows = []
        for rep in range(reps):
            p = R.Bg(["wpexec", paths[name]], wall=10.0)
            time.sleep(1.4)
            during = R.census()
            alive = p.alive()
            st = p.stop()
            time.sleep(0.8)
            after = R.live_r92b()
            rows.append({"rep": rep, "alive_at_1.4s": alive, "during_nodes": during["nodes"],
                         "during_links": during["r92b_links"], "spdif": during["spdif_links"],
                         "stdout": st["out"][-500:], "stderr": st["err"][-300:], "rc": st["rc"],
                         "dur": st["dur"], "after": after})
            print("b4 %-22s r%d alive=%-5s during=%s links=%d after=%s rc=%s out=%r err=%r" %
                  (name, rep, alive, [n["name"] for n in during["nodes"]], len(during["r92b_links"]),
                   after["nodes"], st["rc"], st["out"].strip()[:90], st["err"].strip()[:90]))
            time.sleep(0.3)
        out["legs"][name] = {"script": paths[name], "rows": rows}

    # 3. missing argv / missing file / directory / empty
    for nm, argv in (("no-argv", ["wpexec"]),
                     ("missing-file", ["wpexec", "/nonexistent/r92b.lua"]),
                     ("dir-as-script", ["wpexec", S]),
                     ("empty-script", ["wpexec", os.path.join(S, "r92b_wx_empty.lua")])):
        if nm == "empty-script":
            open(argv[-1], "w").close()
        rows = []
        for rep in range(reps):
            r = R.run(argv, wall=6.0)
            rows.append(r.d())
            print("b4 %-22s r%d rc=%-4s out=%r err=%r" % (nm, rep, r.rc, r.out.strip()[:110], r.err.strip()[:110]))
        out["legs"][nm] = {"argv": argv, "rows": rows}

    out["elapsed_s"] = round(time.time() - t0, 1)
    out["sweep"] = R.sweep()
    out["final"] = R.live_r92b()
    R.jdump(os.path.join(R.REC, "b4_wpexec.json"), out)
    print("WROTE b4_wpexec.json (%.1fs)" % (time.time() - t0))
    print("SWEEP clean:", out["sweep"]["clean"], "final:", out["final"])


if __name__ == "__main__":
    main()
