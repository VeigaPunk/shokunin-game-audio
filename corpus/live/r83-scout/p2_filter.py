#!/usr/bin/env python3
"""P2 — pw-filter existence inventory: binary, package, modules, factories,
SPA filter plugins. Purely read-only."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r83_probe as P


def main():
    res = {"checked": []}
    res["which_pw_filter"] = P.sh(["which", "pw-filter"])["rc"]
    res["path_entries"] = [
        b for b in ("pw-filter", "pw-mididump", "pw-midiplay", "pw-midirecord",
                    "pw-midi2play", "pw-midi2record", "pw-sysex", "pw-encplay",
                    "pw-dsdplay", "pw-loopback", "spa-resample", "pw-jack")
    ]
    res["binaries"] = {}
    for b in res["path_entries"]:
        r = P.sh(["which", b])
        res["binaries"][b] = (r["out"].decode().strip()
                              if r["rc"] == 0 else None)
    res["pkg_pipewire_bins"] = P.sh(
        ["bash", "-c", "pacman -Ql pipewire | grep 'bin/'"])["out"].decode()
    res["pkg_pipewire_audio_bins"] = P.sh(
        ["bash", "-c", "pacman -Ql pipewire-audio | grep 'bin/'"])["out"].decode()
    res["pkg_owner"] = {b: P.sh(["pacman", "-Qo", f"/usr/bin/{b}"])["out"]
                        .decode().strip()
                        for b in ("pw-mididump", "pw-midiplay", "pw-loopback")}

    # pw-cli has no `list-modules` command; `ls Module` is the real surface.
    res["pw_cli_help_has_list_modules"] = "list-modules" in P.sh(
        ["pw-cli", "help"])["out"].decode()
    res["pw_cli_ls_module"] = P.sh(["pw-cli", "ls", "Module"])["out"].decode()

    # factories from pw-dump
    d = P.pw_dump()
    factories, modules = [], []
    for o in d or []:
        t = o.get("type", "")
        p = (o.get("info", {}) or {}).get("props", {}) or {}
        if t.endswith("Factory"):
            factories.append({"id": o["id"],
                              "name": p.get("factory.name"),
                              "type": p.get("factory.type.name")})
        elif t.endswith("Module"):
            modules.append({"id": o["id"], "name": p.get("module.name")})
    res["factories"] = factories
    res["modules"] = modules
    res["filter_factories"] = [f for f in factories
                               if "filter" in (f["name"] or "").lower()
                               or "dsp" in (f["name"] or "").lower()]
    res["spa_lib_dirs"] = P.sh(
        ["bash", "-c", "ls /usr/lib/spa-0.2/ && ls /usr/lib/spa-0.2/filter-graph/ 2>/dev/null"]
    )["out"].decode()
    res["spa_inspect_filter"] = P.sh(
        ["bash", "-c", "spa-inspect /usr/lib/spa-0.2/filter-graph/libspa-filter-graph.so 2>&1 | head -60"],
        timeout=20.0)["out"].decode()
    res["fs_pw_filter"] = P.sh(
        ["bash", "-c", "find /usr -name 'pw-filter*' -o -name '*example-filter*' 2>/dev/null | head"]
    )["out"].decode()
    res["man_pw_filter"] = P.sh(
        ["bash", "-c", "man -w pw-filter 2>&1; man -w libpipewire-module-filter-chain 2>&1"])["out"].decode()
    return P.save_receipt("p2-filter.json", res)


if __name__ == "__main__":
    print(main())
