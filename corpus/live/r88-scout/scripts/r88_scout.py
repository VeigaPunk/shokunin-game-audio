#!/usr/bin/env python3
"""r88 scout harness — bluetooth-absent class + pw-dump/pw-top vs pw-cli witness diff.

READ-ONLY against the live graph: every leg is an observation command
(pw-dump / pw-cli info|enum-params / pw-top -b -n 1 / pactl list|info /
wpctl status / busctl get|introspect|tree / journalctl / pactl load-module
refusal probes that leave no state, verified by module-id-set comparison).
No node, link, module or file outside corpus/live/r88-scout/ is created.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]          # corpus/live/r88-scout
RAW = ROOT / "raw"
REC = ROOT / "receipts"
RAW.mkdir(parents=True, exist_ok=True)
REC.mkdir(parents=True, exist_ok=True)

# objects under three-witness comparison (native PipeWire ids)
OBJECTS = {
    35: "bluez_midi.server (Midi/Bridge, factory api.bluez5.midi.node)",
    46: "alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink (Audio/Sink)",
    133: "r86ctl_ns (Audio/Sink, null-sink, sibling-owned r86)",
}


def run(argv: list[str], timeout: int = 20) -> dict:
    t0 = datetime.now(timezone.utc)
    try:
        p = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
        rc, out, err = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        rc, out, err = 124, "", "TIMEOUT"
    t1 = datetime.now(timezone.utc)
    return {
        "argv": argv,
        "rc": rc,
        "stdout_sha256": hashlib.sha256(out.encode()).hexdigest(),
        "stderr_sha256": hashlib.sha256(err.encode()).hexdigest(),
        "stdout_len": len(out),
        "stderr_len": len(err),
        "start_utc": t0.isoformat(),
        "end_utc": t1.isoformat(),
        "stdout": out,
        "stderr": err,
    }


def leg(name: str, argv: list[str], reps: int = 3, keep_stdout: bool = True) -> dict:
    """Run argv `reps` times in fresh processes; persist raw + receipt."""
    rows = []
    for i in range(1, reps + 1):
        r = run(argv)
        rows.append({k: v for k, v in r.items() if k not in ("stdout", "stderr")})
        if keep_stdout:
            ext = "json" if argv[0] == "pw-dump" else "txt"
            (RAW / f"{name}.{i}.{ext}").write_text(r["stdout"])
            (RAW / f"{name}.{i}.err").write_text(r["stderr"])
        else:
            (RAW / f"{name}.{i}.txt").write_text(
                f"$ {' '.join(argv)}\nrc={r['rc']}\n--stdout--\n{r['stdout']}\n--stderr--\n{r['stderr']}\n"
            )
    stable_out = len({r["stdout_sha256"] for r in rows}) == 1
    stable_rc = len({r["rc"] for r in rows}) == 1
    receipt = {
        "leg": name,
        "argv": argv,
        "reps": reps,
        "stable_stdout": stable_out,
        "stable_rc": stable_rc,
        "rcs": [r["rc"] for r in rows],
        "stdout_sha256": [r["stdout_sha256"] for r in rows],
        "rows": rows,
    }
    return receipt


def main() -> int:
    receipts = []
    census = {}

    # --- 0. module-id set BEFORE any probe (state baseline) ---
    mods_before = run(["pactl", "list", "modules", "short"])
    ids_before = sorted(re.findall(r"^\s*(\d+)\t", mods_before["stdout"], re.M))

    # --- 1. pulse-layer census (bluetooth grep is derived, not a leg) ---
    for nm, argv in [
        ("pactl-list", ["pactl", "list"]),
        ("pactl-modules", ["pactl", "list", "modules", "short"]),
        ("pactl-cards", ["pactl", "list", "cards", "short"]),
        ("pactl-sinks", ["pactl", "list", "sinks", "short"]),
        ("pactl-sources", ["pactl", "list", "sources", "short"]),
        ("pactl-info", ["pactl", "info"]),
        ("wpctl-status", ["wpctl", "status"]),
    ]:
        receipts.append(leg(nm, argv, reps=3))

    # --- 2. refusal-class probes (no state change expected) ---
    for nm, argv in [
        ("refuse-load-bluez5-discover", ["pactl", "load-module", "module-bluez5-discover"]),
        ("refuse-load-bluez5-device", ["pactl", "load-module", "module-bluez5-device"]),
        ("refuse-load-bluez5-device-path", ["pactl", "load-module", "module-bluez5-device", "path=/org/bluez/hci0"]),
        ("refuse-sendmsg-bluez", ["pactl", "send-message", "/org/bluez/hci0", "/org/bluez/hci0"]),
    ]:
        receipts.append(leg(nm, argv, reps=3))

    # --- 3. module-id set AFTER probes (state proof) ---
    mods_after = run(["pactl", "list", "modules", "short"])
    ids_after = sorted(re.findall(r"^\s*(\d+)\t", mods_after["stdout"], re.M))
    census["module_ids_before"] = ids_before
    census["module_ids_after"] = ids_after
    census["module_state_unchanged"] = ids_before == ids_after

    # --- 4. bluez D-Bus witnesses (fresh ×3) ---
    DEV = "/org/bluez/hci0/dev_BC_C7_46_34_C5_66"
    for nm, argv in [
        ("bluez-tree", ["busctl", "--system", "tree", "org.bluez"]),
        ("bluez-adapters", ["busctl", "--system", "tree", "org.bluez", "--list"]),
        ("bluez-device-props", ["busctl", "--system", "introspect", "org.bluez", DEV, "org.bluez.Device1"]),
        ("bluez-adapter-props", ["busctl", "--system", "introspect", "org.bluez", "/org/bluez/hci0", "org.bluez.Adapter1"]),
        ("bluez-media1", ["busctl", "--system", "introspect", "org.bluez", "/org/bluez/hci0", "org.bluez.Media1"]),
        ("bluez-dev-connected", ["busctl", "--system", "get-property", "org.bluez", DEV, "org.bluez.Device1", "Connected"]),
        ("bluez-dev-paired", ["busctl", "--system", "get-property", "org.bluez", DEV, "org.bluez.Device1", "Paired"]),
        ("bluez-dev-uuids", ["busctl", "--system", "get-property", "org.bluez", DEV, "org.bluez.Device1", "UUIDs"]),
        ("bluez-dev-class", ["busctl", "--system", "get-property", "org.bluez", DEV, "org.bluez.Device1", "Class"]),
        ("bluez-dev-icon", ["busctl", "--system", "get-property", "org.bluez", DEV, "org.bluez.Device1", "Icon"]),
        ("bluez-endpoint-log", ["journalctl", "-u", "bluetooth", "--no-pager", "--since", "2026-10-15 02:08:27"]),
    ]:
        receipts.append(leg(nm, argv, reps=3))

    # --- 5. three-witness object comparison ---
    for oid, desc in OBJECTS.items():
        receipts.append(leg(f"pw-dump-{oid}", ["pw-dump", str(oid)], reps=3))
        receipts.append(leg(f"pw-cli-info-{oid}", ["pw-cli", "info", str(oid)], reps=3))
        receipts.append(leg(f"pw-cli-props-{oid}", ["pw-cli", "enum-params", str(oid), "Props"], reps=3))
        receipts.append(leg(f"pw-cli-format-{oid}", ["pw-cli", "enum-params", str(oid), "Format"], reps=3))
        receipts.append(leg(f"pw-cli-propinfo-{oid}", ["pw-cli", "enum-params", str(oid), "PropInfo"], reps=3))

    # --- 6. pw-top ×3, bracketed by full pw-dump censuses ---
    receipts.append(leg("pw-dump-census", ["pw-dump"], reps=3))
    for i in range(1, 4):
        receipts.append(leg(f"pw-top-n1", ["pw-top", "-b", "-n", "1"], reps=1))
        receipts.append(leg(f"pw-dump-census-bracket{i}", ["pw-dump"], reps=1))

    # --- 7. refusal probes for absent objects (pw-cli / pw-dump) ---
    for nm, argv in [
        ("refuse-pwcli-info-99999", ["pw-cli", "info", "99999"]),
        ("refuse-pwcli-format-99999", ["pw-cli", "enum-params", "99999", "Format"]),
        ("refuse-pwdump-99999", ["pw-dump", "99999"]),
    ]:
        receipts.append(leg(nm, argv, reps=3))

    # --- 8. static source evidence (installed file inventory) ---
    for nm, argv in [
        ("spa-bluez5-inventory", ["ls", "-la", "/usr/lib/spa-0.2/bluez5/"]),
        ("pipewire-modules-inventory", ["ls", "/usr/lib/pipewire-0.3/"]),
    ]:
        receipts.append(leg(nm, argv, reps=1))

    out = {
        "harness": "r88_scout.py",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "host": "plazir27",
        "objects": {str(k): v for k, v in OBJECTS.items()},
        "census": census,
        "legs": receipts,
    }
    (REC / "r88-legs.json").write_text(json.dumps(out, indent=1))
    print(f"legs={len(receipts)} module_state_unchanged={census['module_state_unchanged']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
