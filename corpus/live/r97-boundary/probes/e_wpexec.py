#!/usr/bin/env python3
"""r97b stage E — replay of the r97 scout `wpexec` cells (claims 8-10, rows
`wp.wpexec.*`) with fresh processes, plus axes the scout did not vary:

  daemon presence : the same legs with the private WirePlumber **down** (core only)
  argument form   : `wpexec <script> <json-arg>` (the scout never armed it;
                    `wpexec <script> extra1` answers "script argument must be a
                    JSON object")
  --help          : flag-order/usage leg

Legs (fresh `wpexec` process each):
  e1 inventory 65 candidates (FOUND/MISSING/ENV/VERSION/getregistry)
  e2 syntax error, e3 error(), e4 nil index, e5 pairs(_G), e6 nested error(),
  e7 no Core.quit (6 s cap), e8 no argument, e9 missing file
  e10 Settings.get_* x6 before / after `wpctl settings ... false` / after true
  e11 JSON argument
  e12 --help
  e13 inventory + Settings with the private WP down (core only)
Bounded: 10 s cap (6 s for the no-quit leg), process-group kill.
"""
import json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r97blib import (SEAT, ENV, REC, SCR, run, dump, ensure_up, down,
                     stage_out, stage_write, loadavg)

CANDIDATES = ["Core", "Settings", "Log", "LocalModule", "LocalNode", "SpaDevice",
              "StaticObject", "ObjectManager", "Object", "Node", "Device", "Client",
              "Link", "Metadata", "Session", "Endpoint", "SiLink", "SiAdapter",
              "SiNode", "Wp", "utils", "table", "string", "math", "os", "io",
              "debug", "load", "loadstring", "dofile", "require", "require_api",
              "print", "type", "pairs", "ipairs", "next", "select", "pcall",
              "xpcall", "error", "assert", "setmetatable", "getmetatable", "rawget",
              "rawset", "tonumber", "tostring", "unpack", "_G", "_ENV", "_VERSION",
              "json", "spa", "GObject", "GLib", "bit32", "utf8", "Script", "Feature",
              "Features", "Interest", "Constraint", "ImplMetadata", "ImplModule"]

INV_SRC = "local names = {" + ",".join(f'"{n}"' for n in CANDIDATES) + "}\n" + """
local found, missing = {}, {}
for _, n in ipairs(names) do
  local v = _ENV[n]
  if v == nil then missing[#missing+1] = n else found[#found+1] = n .. "=" .. type(v) end
end
print("FOUND " .. table.concat(found, " "))
print("MISSING " .. table.concat(missing, " "))
print("ENV=" .. type(_ENV) .. " G=" .. tostring(_G) .. " VERSION=" .. _VERSION)
print("debug.getregistry=" .. type(debug.getregistry))
Core.quit()
"""

ERR_SRC = {
    "syntax": "this is not lua\n",
    "runtime_error_msg": 'error("r97b deliberate")\nCore.quit()\n',
    "nil_index": 'local t = nil\nprint(t.x)\nCore.quit()\n',
    "pairs_G": 'for k, v in pairs(_G) do end\nCore.quit()\n',
    "nested_error": 'local function f() error("r97b deep", 2) end\nf()\nCore.quit()\n',
    "no_quit": 'print("r97b never quits")\n',
}

SET_SRC = """local keys = {"linking.follow-default-target","node.stream.restore-props",
              "node.features.audio.no-dsp","device.routes.default-sink-volume",
              "bluetooth.profile-preference","node.stream.default-media-role"}
local o = {}
for _, k in ipairs(keys) do
  o[#o+1] = string.format("%s=%s/%s/%s", k, tostring(Settings.get_boolean(k)),
            tostring(Settings.get_float(k)), tostring(Settings.get_string(k)))
end
print(table.concat(o, " "))
Core.quit()
"""

ARG_SRC = """print("argv_type=" .. type(arg))
print("select=" .. tostring(select("#", ...)))
print("ENV_Core=" .. tostring(_ENV.Core ~= nil))
Core.quit()
"""


def script(name, body):
    p = os.path.join(SCR, name)
    with open(p, "w") as f:
        f.write(body)
    return p


def wpexec(path, cap=10.0, args=()):
    return run(["wpexec", path, *args], timeout=cap)


def main():
    arm = sys.argv[1] if len(sys.argv) > 1 else "ambient"
    reps = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    out = stage_out("e_wpexec")
    out["arm"] = arm
    e = ensure_up(verbose=True)
    out["pair"] = e
    inv = script("e_inventory.lua", INV_SRC)
    setp = script("e_settings.lua", SET_SRC)
    argp = script("e_arg.lua", ARG_SRC)

    for n in range(reps):
        rep = {"rep": n, "legs": {}}
        L = rep["legs"]
        L["e1_inventory"] = wpexec(inv)
        for k, body in ERR_SRC.items():
            cap = 6.0 if k == "no_quit" else 10.0
            L[f"e_{k}"] = wpexec(script(f"e_{k}.lua", body), cap=cap)
        before = wpexec(setp)
        t1 = run(["wpctl", "settings", "linking.follow-default-target", "false"], timeout=10.0)
        after_false = wpexec(setp)
        t2 = run(["wpctl", "settings", "linking.follow-default-target", "true"], timeout=10.0)
        after_true = wpexec(setp)
        L["e10_settings_inert"] = {"before": before, "set_false": t1,
                                   "after_false": after_false, "set_true": t2,
                                   "after_true": after_true}
        L["e11_json_arg"] = wpexec(argp, args=('{"x":1}',))
        L["e11b_bad_arg"] = wpexec(argp, args=("extra1",))
        L["e12_help"] = run(["wpexec", "--help"], timeout=8.0)
        L["e8_no_arg"] = run(["wpexec"], timeout=8.0)
        L["e9_missing_file"] = run(["wpexec", "/nonexistent/r97b.lua"], timeout=8.0)
        L["loadavg"] = loadavg()
        out["reps"].append(rep)

        # e13: same legs with the private WirePlumber DOWN (core only)
        down("wp")
        time.sleep(1.0)
        rep13 = {"rep": n, "legs": {}}
        rep13["legs"]["e13a_inventory"] = wpexec(inv)
        rep13["legs"]["e13b_settings"] = wpexec(setp)
        rep13["legs"]["e13c_wpctl_status"] = run(["wpctl", "status"], timeout=10.0)
        rep13["legs"]["e13d_metadata_default"] = {
            "dump_ok": dump() is not None,
            "loadavg": loadavg()}
        out["reps"].append(rep13)
        ensure_up(verbose=False)
        out["loadavg_end_rep"] = loadavg()

    for rep in out["reps"]:
        print(f"--- rep {rep['rep']}")
        for k, v in rep["legs"].items():
            if k == "e10_settings_inert":
                print(f"  {k:<22} before={v['before']['stdout'].strip()[:90]}")
                print(f"  {'':<22} after_false={v['after_false']['stdout'].strip()[:90]}")
                print(f"  {'':<22} after_true={v['after_true']['stdout'].strip()[:90]}")
                print(f"  {'':<22} set rc={v['set_false']['rc']} {v['set_false']['stdout'].strip()[:60]}")
            elif k == "e13d_metadata_default":
                print(f"  {k:<22} dump_ok={v['dump_ok']}")
            elif isinstance(v, dict) and "rc" in v:
                inv_lines = [l for l in v["stdout"].splitlines()
                             if l.startswith(("FOUND", "MISSING", "ENV="))]
                if inv_lines:
                    for l in inv_lines:
                        print(f"  {k:<22} {l[:150]}")
                else:
                    print(f"  {k:<22} rc={v['rc']} timed={v['timed_out']} "
                          f"out={v['stdout'].strip()[:70]!r} err={v['stderr'].strip()[:70]!r}")
    stage_write(out, "e_wpexec.json")


if __name__ == "__main__":
    main()
