#!/usr/bin/env python3
"""r99-boundary static census (C1): module classes, absent packages/tools, man pages.

Read-only. Writes receipts/census.json.
"""
import json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r99b_common import sh, receipt, loadavg


def main():
    r = {"t": time.time(), "loadavg": loadavg(), "whoami_host": os.uname().nodename}
    rc, out, err = sh("ls /usr/lib/pipewire-0.3/ | grep -E 'rtp|roc|zeroconf|vban|netjack|tunnel|avb|sap' | sort")
    r["network_capable_modules"] = out.split()
    rc, out, err = sh("ls /usr/lib/pipewire-0.3/libpipewire-module-*.so | wc -l")
    r["native_module_count"] = out.strip()
    rc, out, err = sh("pacman -Q pipewire pipewire-audio 2>&1; pacman -Q pipewire-zeroconf roc-toolkit snapcast jack-trip 2>&1")
    r["packages"] = out.strip().splitlines()
    rc, out, err = sh("command -v snapcast snapclient roc-send roc-recv jack-trip; echo rc=$?")
    r["absent_tools"] = out.strip().splitlines()
    rc, out, err = sh("man -w pipewire-rtp-sink pipewire-rtp-source pipewire-rtp-sap 2>&1")
    r["man_pages"] = out.strip().splitlines()
    rc, out, err = sh("systemctl is-active avahi-daemon 2>&1; pacman -Q avahi 2>&1")
    r["avahi"] = out.strip().splitlines()
    rc, out, err = sh("pipewire --version 2>&1 | head -2; pacman -Q pipewire wireplumber 2>&1")
    r["toolchain"] = out.strip().splitlines()
    r["module_file_sha256"] = {}
    for m in ("rtp-sink", "rtp-source", "rtp-sap"):
        rc, out, err = sh("sha256sum /usr/lib/pipewire-0.3/libpipewire-module-%s.so" % m)
        r["module_file_sha256"][m] = out.split()[0] if rc == 0 else None
    receipt("census.json", r)
    print(json.dumps({k: r[k] for k in ("native_module_count", "network_capable_modules",
                                        "packages", "absent_tools", "man_pages")}, indent=1))


if __name__ == "__main__":
    main()
