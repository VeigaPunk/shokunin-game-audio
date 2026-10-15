#!/usr/bin/env python3
"""r97-scout stage B — the `wpexec` Lua scripting surface (WirePlumber 0.5.17).

Closes r92 [?]2 ("wpexec's global/API namespace ... could not be narrowed
further") and r90's unmet Settings cross-witness. Every leg is bounded.
"""
import json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r97lib import SEAT, ENV, run, dump, ensure_up

REC = os.path.join(SEAT, "receipts")
SCR = os.path.join(SEAT, "scratch")

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


def script(name, body):
    p = os.path.join(SCR, name)
    with open(p, "w") as f:
        f.write(body)
    return p


def wpexec(path, cap=10.0):
    return run(["wpexec", path], timeout=cap)


def main():
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    ensure_up()
    out = {"stage": "b_wpexec", "reps": []}

    inv_src = "local names = {" + ",".join(f'"{n}"' for n in CANDIDATES) + "}\n" + """
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
    err_src = {
        "syntax": "this is not lua\n",
        "runtime_error_msg": 'error("r97s deliberate")\nCore.quit()\n',
        "nil_index": 'local t = nil\nprint(t.x)\nCore.quit()\n',
        "pairs_G": 'for k, v in pairs(_G) do end\nCore.quit()\n',
        "nested_error": 'local function f() error("r97s deep", 2) end\nf()\nCore.quit()\n',
        "no_quit": 'print("r97s never quits")\n',
    }
    set_src = """local keys = {"linking.follow-default-target","node.stream.restore-props",
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
    setp = script("b_settings.lua", set_src)
    for n in range(reps):
        rep = {"rep": n, "legs": {}}
        rep["legs"]["inventory"] = wpexec(script("b_inv.lua", inv_src))
        for k, body in err_src.items():
            cap = 6.0 if k == "no_quit" else 10.0
            rep["legs"][f"err_{k}"] = wpexec(script(f"b_{k}.lua", body), cap=cap)
        # Settings: read, toggle via wpctl, read again, restore
        before = wpexec(setp)
        t1 = run(["wpctl", "settings", "linking.follow-default-target", "false"], timeout=8.0)
        after_false = wpexec(setp)
        t2 = run(["wpctl", "settings", "linking.follow-default-target", "true"], timeout=8.0)
        after_true = wpexec(setp)
        rep["legs"]["settings_inert"] = {"before": before, "set_false": t1,
                                         "after_false": after_false,
                                         "set_true": t2, "after_true": after_true}
        rep["legs"]["no_arg"] = run(["wpexec"], timeout=6.0)
        rep["legs"]["missing_file"] = run(["wpexec", "/nonexistent/r97s.lua"], timeout=6.0)
        out["reps"].append(rep)
    os.makedirs(REC, exist_ok=True)
    json.dump(out, open(os.path.join(REC, "b_wpexec.json"), "w"), indent=1)
    # compact echo
    for rep in out["reps"]:
        L = rep["legs"]
        inv = L["inventory"]["stdout"]
        print(f"--- rep {rep['rep']}")
        print("  inv FOUND:", [l for l in inv.splitlines() if l.startswith("FOUND")][:1])
        print("  inv MISSING:", [l for l in inv.splitlines() if l.startswith("MISSING")][:1])
        print("  inv ENV:", [l for l in inv.splitlines() if l.startswith("ENV=")][:1])
        for k in ("err_syntax", "err_runtime_error_msg", "err_nil_index", "err_pairs_G",
                  "err_nested_error", "err_no_quit"):
            r = L[k]
            print(f"  {k:<22} rc={r['rc']} timed={r['timed_out']} out={r['stdout'].strip()[:70]!r} err={r['stderr'].strip()[:70]!r}")
        s = L["settings_inert"]
        print("  settings before      :", s["before"]["stdout"].strip()[:150])
        print("  settings after_false :", s["after_false"]["stdout"].strip()[:150])
        print("  settings after_true  :", s["after_true"]["stdout"].strip()[:150])
        print("  wpctl set_false:", s["set_false"]["rc"], s["set_false"]["stdout"].strip()[:60])
        print("  no_arg rc=%s out=%r" % (L["no_arg"]["rc"], L["no_arg"]["stderr"].strip()[:60]))
        print("  missing_file rc=%s out=%r" % (L["missing_file"]["rc"], L["missing_file"]["stderr"].strip()[:60]))


if __name__ == "__main__":
    main()
