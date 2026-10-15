#!/usr/bin/env python3
"""r88b boundary falsification harness — attack the round-88 scout claims under load.

Seat: BOUNDARY (falsification), lane ~/Projects/shokunin/audio-shokunin.
Writes ONLY under corpus/live/r88-boundary/. Audio objects created by this seat are
named r88b_* (sink r88b_ns / r88b_ctl, stream r88b_stream, burners argv r88b_hog).
Never touches sibling objects; kills only its own pids (pgrep -x r88b_hog / recorded pids).

Batteries:
  replay   scout legs re-run verbatim on the current (post-reboot) host + refusal controls
  modes    unstated modes the scout never exercised (pw-dump/pw-cli/pw-top boundary modes)
  setrule  exhaustive id-union-serial membership sweep for pw-dump, plus pw-cli singletons
  pwt      pw-top -n 1 trap and refresh cadence, with per-frame parse and wall timing
  pactl    pulse index <-> native serial map, plus set-card-profile / load-module controls
  ghost    the scout's unresolved pulse-only-sink observation, driven by my own r88b_ sink
  hog      controlled CPU hog (r88b_hog) + re-run of the load-sensitive legs
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw"
REC = ROOT / "receipts"
RAW.mkdir(parents=True, exist_ok=True)
REC.mkdir(parents=True, exist_ok=True)

DEV = "/org/bluez/hci0/dev_BC_C7_46_34_C5_66"
BOOT_SINCE = "2026-10-15 13:38:00"


def utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def run(argv, timeout=60, env=None):
    """Run argv in a fresh process; return rc/stdout/stderr/wall_ms/sha."""
    t0 = time.monotonic()
    ts = utc()
    try:
        p = subprocess.run(argv, capture_output=True, text=True, timeout=timeout, env=env)
        rc, out, err = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        def dec(x):
            if x is None:
                return ""
            return x.decode(errors="replace") if isinstance(x, bytes) else x
        rc, out, err = 124, dec(e.stdout), "TIMEOUT"
    wall = round((time.monotonic() - t0) * 1000, 1)
    return {
        "argv": argv if isinstance(argv, list) else argv,
        "rc": rc,
        "wall_ms": wall,
        "start_utc": ts,
        "stdout_sha256": hashlib.sha256(out.encode()).hexdigest(),
        "stderr_sha256": hashlib.sha256(err.encode()).hexdigest(),
        "stdout_len": len(out),
        "stderr_len": len(err),
        "stdout": out,
        "stderr": err,
    }


def leg(name, argv, reps=1, ext="txt", timeout=60, keep=True):
    """Run argv `reps` times in fresh processes; persist raw + receipt row."""
    rows = []
    for i in range(1, reps + 1):
        r = run(argv, timeout=timeout)
        rows.append({k: v for k, v in r.items() if k not in ("stdout", "stderr")})
        if keep:
            (RAW / f"{name}.{i}.{ext}").write_text(r["stdout"])
            (RAW / f"{name}.{i}.err").write_text(r["stderr"])
    return {
        "leg": name,
        "argv": argv,
        "reps": reps,
        "rcs": [r["rc"] for r in rows],
        "stable_rc": len({r["rc"] for r in rows}) == 1,
        "stable_stdout": len({r["stdout_sha256"] for r in rows}) == 1,
        "stdout_sha256": [r["stdout_sha256"] for r in rows],
        "stderr_sha256": [r["stderr_sha256"] for r in rows],
        "wall_ms": [r["wall_ms"] for r in rows],
        "rows": rows,
    }


# ---------------------------------------------------------------- census

def census(tag):
    """One snapshot of graph + pulse + bluez, stored under raw/. Returns a compact dict."""
    snap = {"tag": tag, "utc": utc()}
    d = run(["pw-dump"], timeout=60)
    snap["pw_dump_rc"] = d["rc"]
    snap["pw_dump_sha"] = d["stdout_sha256"]
    (RAW / f"census-{tag}.json").write_text(d["stdout"])
    try:
        objs = json.loads(d["stdout"])
    except Exception as e:  # pragma: no cover
        snap["pw_dump_error"] = repr(e)
        objs = []
    snap["n_objects"] = len(objs)
    snap["objects"] = [
        {
            "id": o.get("id"),
            "type": o.get("type", "").split(":")[-1],
            "serial": o.get("info", {}).get("props", {}).get("object.serial"),
            "name": (
                o.get("info", {}).get("props", {}).get("node.name")
                or o.get("info", {}).get("props", {}).get("device.name")
                or o.get("info", {}).get("props", {}).get("application.name")
                or ""
            ),
            "state": o.get("info", {}).get("state"),
        }
        for o in objs
    ]
    for nm, argv in (
        ("pactl_sinks", ["pactl", "list", "sinks", "short"]),
        ("pactl_sources", ["pactl", "list", "sources", "short"]),
        ("pactl_cards", ["pactl", "list", "cards", "short"]),
        ("pactl_sink_inputs", ["pactl", "list", "sink-inputs", "short"]),
        ("pactl_modules", ["pactl", "list", "modules", "short"]),
        ("wpctl", ["wpctl", "status"]),
        ("bluez_tree", ["busctl", "--system", "tree", "org.bluez"]),
    ):
        r = run(argv, timeout=60)
        (RAW / f"census-{tag}-{nm}.txt").write_text(r["stdout"])
        snap[nm] = r["stdout"]
        snap[nm + "_rc"] = r["rc"]
    snap["module_ids"] = sorted(re.findall(r"^\s*(\d+)\t", snap["pactl_modules"], re.M))
    (REC / f"census-{tag}.json").write_text(json.dumps(snap, indent=1))
    return snap


def parse_pwdump_keys(objs):
    """(ids, serials, keys, members_pred) from a pw-dump object list."""
    by_id = {}
    sers = {}
    for o in objs:
        oid = o.get("id")
        by_id[oid] = o
        s = o.get("info", {}).get("props", {}).get("object.serial")
        if s is not None:
            sers.setdefault(s, []).append(oid)
    keys = sorted(set(by_id) | set(sers))
    pred = {}
    for k in keys:
        m = set()
        if k in by_id:
            m.add(k)
        m.update(sers.get(k, []))
        pred[k] = sorted(m)
    return by_id, sers, keys, pred


# ---------------------------------------------------------------- battery: replay

def battery_replay():
    legs = []
    census_before = census("replay-before")

    # 1. scout refusal probes, verbatim argv, same reps
    for nm, argv, reps in [
        ("refuse-load-bluez5-discover", ["pactl", "load-module", "module-bluez5-discover"], 3),
        ("refuse-load-bluez5-device", ["pactl", "load-module", "module-bluez5-device"], 3),
        ("refuse-load-bluez5-device-path", ["pactl", "load-module", "module-bluez5-device", "path=/org/bluez/hci0"], 3),
        ("refuse-load-bluez5-discover-a2dpfalse", ["pactl", "load-module", "module-bluez5-discover", "a2dp_source=false"], 1),
        ("refuse-sendmsg-bluez", ["pactl", "send-message", "/org/bluez/hci0", "/org/bluez/hci0"], 3),
        ("refuse-setcard-bluez", ["pactl", "set-card-profile", "bluez_card.BC_C7_46_34_C5_66", "a2dp-sink"], 3),
        ("refuse-pwcli-info-99999", ["pw-cli", "info", "99999"], 3),
        ("refuse-pwcli-format-99999", ["pw-cli", "enum-params", "99999", "Format"], 3),
        ("refuse-pwdump-99999", ["pw-dump", "99999"], 3),
    ]:
        legs.append(leg(nm, argv, reps=reps))

    # 2. the one grep the scout reported as a single line
    r = run(["pactl", "list"])
    matches = [ln for ln in r["stdout"].splitlines() if re.search(r"bluez|a2dp|sco", ln, re.I)]
    legs.append({
        "leg": "pactl-list-bluez-grep",
        "argv": ["pactl", "list"],
        "rcs": [r["rc"]],
        "stable_stdout": True,
        "match_count": len(matches),
        "matches": matches,
        "stdout_sha256": [r["stdout_sha256"]],
        "wall_ms": [r["wall_ms"]],
        "rows": [{k: v for k, v in r.items() if k not in ("stdout", "stderr")}],
    })
    (RAW / "pactl-list-bluez-grep.txt").write_text(r["stdout"])

    # 3. static inventory replays
    legs.append(leg("spa-bluez5-inventory", ["ls", "-la", "/usr/lib/spa-0.2/bluez5/"], reps=1))
    legs.append(leg("find-module-bluez5", ["bash", "-c", "find /usr/lib* -name '*module-bluez5*' | wc -l"], reps=1))
    legs.append(leg("pacman-Ql-pipewire-bluez-count",
                    ["bash", "-c", "pacman -Ql pipewire | grep -c bluez || true"], reps=1))
    legs.append(leg("pacman-Qo-spa-bluez5",
                    ["bash", "-c", "pacman -Qo /usr/lib/spa-0.2/bluez5/libspa-bluez5.so || true"], reps=1))
    legs.append(leg("strings-libspa-bluez5-codecs",
                    ["bash", "-c", "strings /usr/lib/spa-0.2/bluez5/libspa-bluez5.so | grep -c 'bluez5\\.codecs' || true"], reps=1))
    legs.append(leg("strings-libspa-bluez5-enable-props",
                    ["bash", "-c", "strings /usr/lib/spa-0.2/bluez5/libspa-bluez5.so | grep -o 'bluez5\\.[a-z0-9.-]*' | sort -u | head -40"], reps=1))
    legs.append(leg("strings-sbc-xq",
                    ["bash", "-c", "strings /usr/lib/spa-0.2/bluez5/libspa-codec-bluez5-sbc.so | grep -E 'sbc_xq|SBC-XQ|spa.bluez5.codecs.sbc' | sort -u"], reps=1))
    legs.append(leg("wireplumber-config-present",
                    ["bash", "-c", "ls -la ~/.config/wireplumber/wireplumber.conf.d/ 2>&1; echo ---; cat ~/.config/wireplumber/wireplumber.conf.d/bluetooth-a2dp-autoconnect.conf 2>&1"], reps=1))
    legs.append(leg("grep-bluez5-codecs-systemwide",
                    ["bash", "-c", "grep -rl 'bluez5.codecs' /usr/share/wireplumber /etc/wireplumber /usr/share/pipewire 2>/dev/null | head; echo 'rc='$?"], reps=1))

    # 4. bluez D-Bus witnesses (current boot)
    for nm, argv in [
        ("bluez-tree", ["busctl", "--system", "tree", "org.bluez"]),
        ("bluez-device-props", ["busctl", "--system", "introspect", "org.bluez", DEV, "org.bluez.Device1"]),
        ("bluez-adapter-props", ["busctl", "--system", "introspect", "org.bluez", "/org/bluez/hci0", "org.bluez.Adapter1"]),
        ("bluez-media1", ["busctl", "--system", "introspect", "org.bluez", "/org/bluez/hci0", "org.bluez.Media1"]),
        ("bluez-dev-connected", ["busctl", "--system", "get-property", "org.bluez", DEV, "org.bluez.Device1", "Connected"]),
        ("bluez-dev-paired", ["busctl", "--system", "get-property", "org.bluez", DEV, "org.bluez.Device1", "Paired"]),
        ("bluez-dev-uuids", ["busctl", "--system", "get-property", "org.bluez", DEV, "org.bluez.Device1", "UUIDs"]),
        ("bluez-dev-class", ["busctl", "--system", "get-property", "org.bluez", DEV, "org.bluez.Device1", "Class"]),
        ("bluez-dev-icon", ["busctl", "--system", "get-property", "org.bluez", DEV, "org.bluez.Device1", "Icon"]),
        ("bluez-dev-modalias", ["busctl", "--system", "get-property", "org.bluez", DEV, "org.bluez.Device1", "Modalias"]),
        ("bluez-endpoint-log", ["bash", "-c",
                                f"journalctl -u bluetooth --no-pager --since '{BOOT_SINCE}' | grep -E 'Endpoint (un)?registered'"]),
        ("bluez-endpoint-senders", ["bash", "-c",
                                    f"journalctl -u bluetooth --no-pager --since '{BOOT_SINCE}' | grep 'Endpoint registered' | sed 's/.*sender=\\([^ ]*\\).*/\\1/' | sort | uniq -c"]),
    ]:
        legs.append(leg(nm, argv, reps=1))

    # 5. control: is the *command class* broken, or only the bluez target?
    #    5a. load-module with a module that does exist -> r88b_ctl, then unload.
    lc = run(["pactl", "load-module", "module-null-sink", "sink_name=r88b_ctl",
              "sink_properties=device.description=r88b_ctl"])
    mid = lc["stdout"].strip()
    legs.append({
        "leg": "control-load-null-sink", "argv": lc["argv"], "rcs": [lc["rc"]],
        "stdout": lc["stdout"], "stderr": lc["stderr"], "module_id": mid,
        "stable_stdout": True, "wall_ms": [lc["wall_ms"]],
        "rows": [{k: v for k, v in lc.items() if k not in ("stdout", "stderr")}],
    })
    time.sleep(0.7)
    legs.append(leg("control-null-sink-visible",
                    ["bash", "-c", "pactl list sinks short | grep r88b_ctl; echo rc=$?; pw-dump | grep -c r88b_ctl"], reps=1))
    if mid.isdigit():
        ul = run(["pactl", "unload-module", mid])
        legs.append({
            "leg": "control-unload-null-sink", "argv": ul["argv"], "rcs": [ul["rc"]],
            "stdout": ul["stdout"], "stderr": ul["stderr"], "stable_stdout": True,
            "wall_ms": [ul["wall_ms"]],
            "rows": [{k: v for k, v in ul.items() if k not in ("stdout", "stderr")}],
        })
    #    5b. set-card-profile idempotent on a card that exists (current profile re-applied)
    cards = run(["pactl", "list", "cards"])
    active = re.findall(r"Name: (\S+)\n(?:.|\n)*?Active Profile: (\S+)", cards["stdout"])
    legs.append({
        "leg": "control-card-active-profiles", "argv": ["pactl", "list", "cards"],
        "rcs": [cards["rc"]], "stable_stdout": True, "active_profiles": active,
        "wall_ms": [cards["wall_ms"]],
        "rows": [{k: v for k, v in cards.items() if k not in ("stdout", "stderr")}],
    })
    if active:
        cname, cprof = active[0]
        legs.append(leg("control-setcard-idempotent",
                        ["pactl", "set-card-profile", cname, cprof], reps=2))
        legs.append(leg("control-setcard-bogus-profile",
                        ["pactl", "set-card-profile", cname, "bogus-profile-xyz"], reps=2))

    census_after = census("replay-after")
    out = {
        "battery": "replay",
        "generated_utc": utc(),
        "module_ids_before": census_before["module_ids"],
        "module_ids_after": census_after["module_ids"],
        "module_state_unchanged": census_before["module_ids"] == census_after["module_ids"],
        "legs": legs,
    }
    (REC / "B1-replay.json").write_text(json.dumps(out, indent=1))
    print("replay legs:", len(legs), "module_state_unchanged:", out["module_state_unchanged"])


# ---------------------------------------------------------------- battery: modes

PARAM_NAMES = ["Format", "EnumFormat", "Props", "PropInfo", "IO", "Buffers", "Meta",
               "Latency", "ProcessLatency", "Tag", "Route", "Profiles", "EnumProfile",
               "BogusXYZ", "4", "0"]


def battery_modes():
    legs = []
    c = census("modes")
    objs = json.loads((RAW / "census-modes.json").read_text())
    by_id, sers, keys, pred = parse_pwdump_keys(objs)
    # pick a stable serial-only key and a stable collision key from THIS census
    serial_only = sorted(k for k in keys if k not in by_id and k in sers)
    collide = sorted(k for k in keys if k in by_id and k in sers and pred[k] == [k])
    sk = serial_only[0] if serial_only else None
    ck = next((k for k in collide if k >= 40), None)
    node_ids = sorted(o["id"] for o in objs
                      if o["type"].endswith("Node") and "state" in o.get("info", {}))
    port_ids = sorted(o["id"] for o in objs if o["type"].endswith("Port"))
    nd = node_ids[0] if node_ids else None
    pt = port_ids[0] if port_ids else None

    # --- pw-dump boundary / output modes
    for nm, argv in [
        ("mode-dump-serialonly", ["pw-dump", str(sk)] if sk else None),
        ("mode-cli-serialonly", ["pw-cli", "info", str(sk)] if sk else None),
        ("mode-dump-collide", ["pw-dump", str(ck)] if ck else None),
        ("mode-dump-spa", ["pw-dump", "-s", str(ck)] if ck else None),
        ("mode-dump-spa-serialonly", ["pw-dump", "-s", str(sk)] if sk else None),
        ("mode-dump-raw", ["pw-dump", "-R", str(ck)] if ck else None),
        ("mode-dump-indent0", ["pw-dump", "-i", "0", str(ck)] if ck else None),
        ("mode-dump-color-always", ["pw-dump", "--color=always", str(ck)] if ck else None),
        ("mode-dump-zero", ["pw-dump", "0"]),
        ("mode-dump-negative", ["pw-dump", "-1"]),
        ("mode-dump-nonnumeric", ["pw-dump", "abc"]),
        ("mode-dump-empty", ["pw-dump", ""]),
        ("mode-dump-huge", ["pw-dump", "99999999999999999999"]),
        ("mode-dump-two-ids", ["pw-dump", str(nd), str(ck)] if nd and ck else None),
    ]:
        if argv is None:
            continue
        legs.append(leg(nm, argv, reps=3 if nm.startswith("mode-dump-serialonly") or nm.startswith("mode-cli") else 1))
    # multi-id variant: check whether both members appear or only the first
    if nd and ck:
        legs.append(leg("mode-dump-two-ids-parse", ["bash", "-c",
                       f"pw-dump {nd} {ck} | jq -c '[.[]|.id]'"], reps=1))

    # --- pw-cli witness modes
    for nm, argv in [
        ("mode-cli-info-0", ["pw-cli", "info", "0"]),
        ("mode-cli-info-all", ["bash", "-c", "pw-cli info all | wc -l"]),
        ("mode-cli-info-all-has-core", ["bash", "-c", "pw-cli info all | grep -c 'PipeWire:Interface:Core' || true"]),
        ("mode-cli-ls-node", ["bash", "-c", "pw-cli ls Node | grep -c '^\\tid ' || true"]),
        ("mode-cli-ls-device", ["bash", "-c", "pw-cli ls Device | grep -c '^\\tid ' || true"]),
        ("mode-cli-ls-client", ["bash", "-c", "pw-cli ls Client | grep -c '^\\tid ' || true"]),
        ("mode-cli-ls-port", ["bash", "-c", "pw-cli ls Port | grep -c '^\\tid ' || true"]),
        ("mode-cli-ls-link", ["bash", "-c", "pw-cli ls Link | grep -c '^\\tid ' || true"]),
        ("mode-cli-ls-factory", ["bash", "-c", "pw-cli ls Factory | grep -c '^\\tid ' || true"]),
        ("mode-cli-ls-metadata", ["bash", "-c", "pw-cli ls Metadata | grep -c '^\\tid ' || true"]),
        ("mode-cli-ls-module", ["bash", "-c", "pw-cli ls Module | grep -c '^\\tid ' || true"]),
        ("mode-cli-ls-serial-resolve", ["bash", "-c",
                                        f"pw-cli ls Node | grep -c 'object.serial = \"{sk}\"' || true"] if sk else None),
        ("mode-cli-ls-json", ["bash", "-c", "pw-cli ls -N Node | head -5"]),
    ]:
        if argv is None:
            continue
        legs.append(leg(nm, argv, reps=1))
    # key-set equality on a Device and a Client (classes the scout never compared)
    dev_id = next((o["id"] for o in objs if o["type"].endswith("Device")), None)
    cli_id = next((o["id"] for o in objs if o["type"].endswith("Client")), None)
    for tag, oid in (("device", dev_id), ("client", cli_id)):
        if oid is None:
            continue
        legs.append(leg(f"mode-keyset-{tag}-dump", ["pw-dump", str(oid)], reps=1, ext="json"))
        legs.append(leg(f"mode-keyset-{tag}-cli", ["pw-cli", "info", str(oid)], reps=1))
    # param-name matrix on a node and a port
    for tag, oid in (("node", nd), ("port", pt)):
        if oid is None:
            continue
        for pname in PARAM_NAMES:
            legs.append(leg(f"mode-param-{tag}-{pname}", ["pw-cli", "enum-params", str(oid), pname], reps=1))
    # pw-top boundary modes
    for nm, argv in [
        ("mode-pwt-n0", ["pw-top", "-b", "-n", "0"]),
        ("mode-pwt-nneg", ["pw-top", "-b", "-n", "-1"]),
        ("mode-pwt-nabc", ["pw-top", "-b", "-n", "abc"]),
        ("mode-pwt-remote-bogus", ["pw-top", "-b", "-n", "1", "-r", "bogus-remote-xyz"]),
    ]:
        legs.append(leg(nm, argv, reps=1, timeout=30))

    out = {
        "battery": "modes",
        "generated_utc": utc(),
        "picked": {"serial_only_key": sk, "collision_key": ck, "node": nd, "port": pt,
                   "device": dev_id, "client": cli_id, "n_objects": len(objs)},
        "serial_only_keys": serial_only,
        "legs": legs,
    }
    (REC / "B2-modes.json").write_text(json.dumps(out, indent=1))
    print("modes legs:", len(legs), "picked:", out["picked"])


# ---------------------------------------------------------------- battery: setrule

def battery_setrule():
    """Exhaustive: for EVERY key in ids|serials, pw-dump K must equal the predicted member set."""
    c0 = census("setrule-before")
    objs0 = json.loads((RAW / "census-setrule-before.json").read_text())
    by_id, sers, keys, pred = parse_pwdump_keys(objs0)
    results = []
    for k in keys:
        r = run(["pw-dump", str(k)], timeout=30)
        try:
            got = sorted(o.get("id") for o in json.loads(r["stdout"]))
        except Exception:
            got = None
        results.append({
            "key": k, "rc": r["rc"], "predicted": pred[k], "got": got,
            "match": got == pred[k], "wall_ms": r["wall_ms"],
            "stdout_sha256": r["stdout_sha256"], "stdout_len": r["stdout_len"],
            "stderr": r["stderr"][:200],
        })
    c1 = census("setrule-after")
    objs1 = json.loads((RAW / "census-setrule-after.json").read_text())
    by_id1, sers1, keys1, pred1 = parse_pwdump_keys(objs1)
    stable_keys = sorted(set(keys) & set(keys1))
    for row in results:
        row["stable"] = row["key"] in stable_keys and pred1.get(row["key"]) == row["predicted"]
    mismatches = [r for r in results if not r["match"]]
    mismatches_stable = [r for r in mismatches if r["stable"]]
    # pw-cli singleton: id-only keying, serial-only keys unresolvable
    cli = []
    for k in keys:
        r = run(["pw-cli", "info", str(k)], timeout=30)
        unknown = "unknown global" in r["stderr"]
        cli.append({"key": k, "rc": r["rc"], "unknown_global": unknown,
                    "in_ids": k in by_id, "in_serials": k in sers,
                    "stdout_len": r["stdout_len"], "stderr": r["stderr"][:160]})
    # pw-cli must resolve exactly the id-keys and fail on serial-only keys
    cli_viol = [c for c in cli
                if (c["in_ids"] and c["unknown_global"]) or ((not c["in_ids"]) and (not c["unknown_global"]))]
    # nested-reference non-expansion: pw-dump <node id> must NOT include that node's ports
    nested = []
    ports = [o for o in objs0 if o.get("type", "").endswith("Port")]
    for p in ports[:40]:
        nid = p.get("info", {}).get("props", {}).get("node.id")
        if nid is None:
            continue
        r = run(["pw-dump", str(nid)], timeout=30)
        try:
            got = sorted(o.get("id") for o in json.loads(r["stdout"]))
        except Exception:
            got = None
        nested.append({"port": p["id"], "node_id": nid, "node_key_result": got,
                       "port_included": (got is not None and p["id"] in got),
                       "predicted": pred.get(nid)})
    nested_viol = [n for n in nested if n["port_included"]]
    out = {
        "battery": "setrule",
        "generated_utc": utc(),
        "n_keys": len(keys),
        "n_objects_before": len(objs0),
        "n_objects_after": len(objs1),
        "n_mismatch": len(mismatches),
        "n_mismatch_stable": len(mismatches_stable),
        "mismatches": mismatches[:20],
        "n_serial_only": len([k for k in keys if k not in by_id and k in sers]),
        "n_id_only": len([k for k in keys if k in by_id and k not in sers]),
        "n_bundles": len([k for k in keys if len(pred[k]) > 1]),
        "bundle_keys": [k for k in keys if len(pred[k]) > 1][:20],
        "cli_violations": cli_viol,
        "n_cli_serial_only_unknown": len([c for c in cli if c["in_serials"] and not c["in_ids"] and c["unknown_global"]]),
        "n_cli_serial_only_total": len([c for c in cli if c["in_serials"] and not c["in_ids"]]),
        "nested_checks": len(nested),
        "nested_violations": nested_viol,
        "results": results,
        "cli_results": cli,
        "nested_results": nested,
    }
    (REC / "B3-setrule.json").write_text(json.dumps(out, indent=1))
    print("setrule: keys=%d mismatch=%d mismatch_stable=%d bundles=%d cli_viol=%d nested_viol=%d"
          % (len(keys), len(mismatches), len(mismatches_stable),
             out["n_bundles"], len(cli_viol), len(nested_viol)))


# ---------------------------------------------------------------- battery: pwt

FRAME_RE = re.compile(r"^([A-Za-z])\s+(\d+)\s")


def parse_pwt(text):
    """Split batch output into frames; per frame: list of (state, id, name)."""
    frames = []
    cur = None
    for line in text.splitlines():
        if line.startswith("S   ID") or line.startswith("S  ID"):
            if cur is not None:
                frames.append(cur)
            cur = []
            continue
        if cur is None:
            continue
        m = FRAME_RE.match(line)
        if m:
            toks = line.split()
            cur.append({"state": m.group(1), "id": int(m.group(2)), "name": toks[-1]})
    if cur is not None:
        frames.append(cur)
    return frames


def battery_pwt():
    legs = []
    # -n 1 trap: many reps under the current (already loaded) host
    for i in range(1, 13):
        r = run(["pw-top", "-b", "-n", "1"], timeout=60)
        frames = parse_pwt(r["stdout"])
        states = [row["state"] for f in frames for row in f]
        legs.append({
            "leg": f"pwt-n1-rep{i}", "argv": r["argv"], "rc": r["rc"], "wall_ms": r["wall_ms"],
            "n_frames": len(frames), "n_rows": len(states),
            "all_C": bool(states) and all(s == "C" for s in states),
            "non_C": sorted({s for s in states if s != "C"}),
            "state_hist": {s: states.count(s) for s in sorted(set(states))},
            "stdout_sha256": r["stdout_sha256"], "stderr": r["stderr"][:120],
        })
        (RAW / f"pwt-n1-rep{i}.txt").write_text(r["stdout"])
    # -n 2 / -n 3 / -n 4 with per-frame parse + timing
    for n in (2, 3, 4):
        for i in range(1, 4):
            r = run(["pw-top", "-b", "-n", str(n)], timeout=90)
            frames = parse_pwt(r["stdout"])
            legs.append({
                "leg": f"pwt-n{n}-rep{i}", "argv": r["argv"], "rc": r["rc"], "wall_ms": r["wall_ms"],
                "n_frames": len(frames),
                "frames": [{"rows": len(f), "states": {s: [x["state"] for x in f].count(s)
                                                        for s in sorted({x["state"] for x in f})},
                            "running": [x["name"] for x in f if x["state"] in ("R", "t", "T")]} for f in frames],
                "stdout_sha256": r["stdout_sha256"], "stderr": r["stderr"][:120],
            })
            (RAW / f"pwt-n{n}-rep{i}.txt").write_text(r["stdout"])
    # correlation leg: same-window running-node count vs -n 2 wall time
    corr = []
    for i in range(8):
        r = run(["pw-top", "-b", "-n", "2"], timeout=90)
        frames = parse_pwt(r["stdout"])
        nrun = sum(1 for f in frames for x in f if x["state"] in ("R", "t", "T"))
        corr.append({"rep": i, "wall_ms": r["wall_ms"], "n_running_in_frames": nrun,
                     "n_frames": len(frames), "states2": [x["state"] for x in frames[-1]] if frames else []})
        (RAW / f"pwt-corr-{i}.txt").write_text(r["stdout"])
    out = {"battery": "pwt", "generated_utc": utc(), "legs": legs, "corr": corr}
    (REC / "B4-pwt.json").write_text(json.dumps(out, indent=1))
    print("pwt legs:", len(legs), "n1_all_C:", sum(1 for l in legs if l.get("all_C")), "/12")


# ---------------------------------------------------------------- battery: pactl

def battery_pactl():
    legs = []
    snaps = []
    for i in range(3):
        c = census(f"pactl-{i}")
        snaps.append(c)
    legs.append(leg("pactl-sinks-short", ["pactl", "list", "sinks", "short"], reps=3))
    legs.append(leg("pactl-sources-short", ["pactl", "list", "sources", "short"], reps=3))
    legs.append(leg("pactl-cards-short", ["pactl", "list", "cards", "short"], reps=3))
    legs.append(leg("pactl-sink-inputs-short", ["pactl", "list", "sink-inputs", "short"], reps=3))
    legs.append(leg("pactl-source-outputs-short", ["pactl", "list", "source-outputs", "short"], reps=3))
    # full cards text for index/profile mapping
    legs.append(leg("pactl-cards-full", ["pactl", "list", "cards"], reps=1))
    # tight same-window triple on one node: pulse state vs native state vs pwt
    objs = json.loads((RAW / "census-pactl-0.json").read_text())
    by_id, sers, keys, pred = parse_pwdump_keys(objs)
    target = None
    for o in objs:
        if o.get("type", "").endswith("Node") and o.get("info", {}).get("props", {}).get("media.class", "").startswith("Audio/Sink"):
            target = o["id"]
    composite = (
        "echo '== pactl =='; pactl list sinks short | head -6; "
        "echo '== dump =='; pw-dump | jq -r '.[]|select(.type|endswith(\"Node\"))|[.id,.info.state,.info.props[\"node.name\"]]|@tsv'; "
        "echo '== ptop =='; pw-top -b -n 2 2>/dev/null | tail -n +1 | grep -E '^[A-Za-z] ' | tail -12"
    )
    legs.append(leg("pactl-native-triple", ["bash", "-c", composite], reps=3, timeout=90))
    out = {
        "battery": "pactl", "generated_utc": utc(),
        "target_node": target,
        "census_module_ids": [s["module_ids"] for s in snaps],
        "legs": legs,
        "census_summaries": [
            {"tag": s["tag"], "n_objects": s["n_objects"], "utc": s["utc"],
             "pactl_sinks": s["pactl_sinks"], "pactl_cards": s["pactl_cards"]} for s in snaps
        ],
    }
    (REC / "B5-pactl.json").write_text(json.dumps(out, indent=1))
    print("pactl legs:", len(legs))


# ---------------------------------------------------------------- battery: ghost

def battery_ghost():
    """Scout 4.5: pulse-only sink observation. Drive it with my own r88b_ sink lifecycle."""
    events = []
    brackets = []

    def bracket(tag, i):
        p = run(["pactl", "list", "sinks", "short"], timeout=30)
        d = run(["pw-dump"], timeout=60)
        pulse = {ln.split("\t")[1] for ln in p["stdout"].splitlines() if "\t" in ln}
        try:
            native = {o.get("info", {}).get("props", {}).get("node.name", "") for o in json.loads(d["stdout"])
                      if o.get("type", "").endswith("Node")}
        except Exception:
            native = set()
        only_pulse = sorted(n for n in pulse - native if n)
        only_native = sorted(n for n in native - pulse if n and not n.endswith(".monitor"))
        row = {"tag": tag, "i": i, "utc": utc(), "pulse_n": len(pulse), "native_n": len(native),
               "pulse_only": only_pulse, "native_only": only_native,
               "pactl_wall_ms": p["wall_ms"], "dump_wall_ms": d["wall_ms"]}
        brackets.append(row)
        if only_pulse:
            events.append(row)
        return row

    for i in range(15):
        bracket("pre-create", i)
    lc = run(["pactl", "load-module", "module-null-sink", "sink_name=r88b_ns",
              "sink_properties=device.description=r88b_ns"], timeout=30)
    mid = lc["stdout"].strip()
    time.sleep(0.5)
    for i in range(15):
        bracket("alive", i)
    ul = run(["pactl", "unload-module", mid], timeout=30) if mid.isdigit() else None
    for i in range(40):
        bracket("post-unload", i)
        time.sleep(0.05)
    out = {
        "battery": "ghost", "generated_utc": utc(),
        "load": {"argv": lc["argv"], "rc": lc["rc"], "module_id": mid, "stderr": lc["stderr"][:200]},
        "unload": None if ul is None else {"argv": ul["argv"], "rc": ul["rc"], "stderr": ul["stderr"][:200]},
        "n_brackets": len(brackets),
        "n_pulse_only_events": len(events),
        "events": events,
        "brackets": brackets,
    }
    (REC / "B6-ghost.json").write_text(json.dumps(out, indent=1))
    print("ghost: brackets=%d pulse_only_events=%d" % (len(brackets), len(events)))


# ---------------------------------------------------------------- battery: hog

HOG_N = 16


def hog_pids():
    """My burners only: `exec -a r88b_hog yes` sets argv[0]; -x matches comm (=yes), so
    match the full command line instead, anchored so no sibling pattern can collide."""
    r = run(["pgrep", "-f", "^r88b_hog$"], timeout=10)
    return sorted(int(x) for x in r["stdout"].split() if x.isdigit())


def battery_hog():
    """Add a controlled r88b_hog CPU layer, re-run the load-sensitive legs, kill only my own."""
    legs = []
    load_before = run(["bash", "-c", "cat /proc/loadavg; cat /proc/pressure/cpu | head -1; echo -n 'foreign_yes='; pgrep -c -x yes || true"], timeout=10)
    spawn = []
    for i in range(HOG_N):
        p = subprocess.Popen(["bash", "-c", f"exec -a r88b_hog yes > /dev/null"],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        spawn.append(p.pid)
    time.sleep(8)
    mine = hog_pids()
    load_under = run(["bash", "-c", "cat /proc/loadavg; cat /proc/pressure/cpu | head -1; echo -n 'foreign_yes='; pgrep -c -x yes || true"], timeout=10)
    (RAW / "hog-load-before.txt").write_text(load_before["stdout"])
    (RAW / "hog-load-under.txt").write_text(load_under["stdout"])
    # load-sensitive legs under my hog
    for i in range(1, 7):
        r = run(["pw-top", "-b", "-n", "1"], timeout=60)
        frames = parse_pwt(r["stdout"])
        states = [row["state"] for f in frames for row in f]
        legs.append({"leg": f"hog-pwt-n1-rep{i}", "argv": r["argv"], "rc": r["rc"], "wall_ms": r["wall_ms"],
                     "n_rows": len(states), "all_C": bool(states) and all(s == "C" for s in states),
                     "state_hist": {s: states.count(s) for s in sorted(set(states))},
                     "stderr": r["stderr"][:120]})
        (RAW / f"hog-pwt-n1-rep{i}.txt").write_text(r["stdout"])
    for i in range(1, 4):
        r = run(["pw-top", "-b", "-n", "2"], timeout=90)
        frames = parse_pwt(r["stdout"])
        legs.append({"leg": f"hog-pwt-n2-rep{i}", "argv": r["argv"], "rc": r["rc"], "wall_ms": r["wall_ms"],
                     "frames": [{"rows": len(f), "states": {s: [x["state"] for x in f].count(s)
                                                            for s in sorted({x["state"] for x in f})}} for f in frames],
                     "stderr": r["stderr"][:120]})
        (RAW / f"hog-pwt-n2-rep{i}.txt").write_text(r["stdout"])
    legs.append(leg("hog-refuse-pwcli-info-99999", ["pw-cli", "info", "99999"], reps=3))
    legs.append(leg("hog-refuse-pwdump-99999", ["pw-dump", "99999"], reps=3))
    legs.append(leg("hog-refuse-load-bluez5-discover", ["pactl", "load-module", "module-bluez5-discover"], reps=3))
    legs.append(leg("hog-bluez-tree", ["busctl", "--system", "tree", "org.bluez"], reps=3))
    legs.append(leg("hog-pactl-list", ["pactl", "list"], reps=3, timeout=90))
    # set-rule spot check under hog (deterministic law should not care about load)
    d = run(["pw-dump"], timeout=90)
    (RAW / "hog-census.json").write_text(d["stdout"])
    try:
        objs = json.loads(d["stdout"])
    except Exception:
        objs = []
    by_id, sers, keys, pred = parse_pwdump_keys(objs)
    spot = [k for k in keys if k in (1, 2, 6, 8, 11, 13, 15, 19, 21, 25)][:8]
    spot += [k for k in keys if k not in by_id][:6]
    spot_res = []
    for k in sorted(set(spot)):
        r = run(["pw-dump", str(k)], timeout=30)
        try:
            got = sorted(o.get("id") for o in json.loads(r["stdout"]))
        except Exception:
            got = None
        spot_res.append({"key": k, "predicted": pred[k], "got": got, "match": got == pred[k], "wall_ms": r["wall_ms"]})
    legs.append({"leg": "hog-setrule-spot", "results": spot_res,
                 "n_match": sum(1 for s in spot_res if s["match"]), "n": len(spot_res)})
    # kill ONLY my own burners
    killed = []
    for pid in mine:
        try:
            os.kill(pid, signal.SIGTERM)
            killed.append(pid)
        except ProcessLookupError:
            pass
    time.sleep(1.5)
    survivors = hog_pids()
    for pid in survivors:
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    time.sleep(0.5)
    final = hog_pids()
    load_after = run(["bash", "-c", "cat /proc/loadavg; cat /proc/pressure/cpu | head -1; pgrep -c -x yes || true"], timeout=10)
    (RAW / "hog-load-after.txt").write_text(load_after["stdout"])
    out = {
        "battery": "hog", "generated_utc": utc(), "hog_n": HOG_N,
        "spawn_pids": spawn, "mine_pids": mine, "killed": killed,
        "survivors_after_sigterm": survivors, "final_r88b_hog": final,
        "load_before": load_before["stdout"], "load_under": load_under["stdout"],
        "load_after": load_after["stdout"],
        "legs": legs,
    }
    (REC / "B7-hog.json").write_text(json.dumps(out, indent=1))
    print("hog: mine=%d killed=%d final=%s" % (len(mine), len(killed), final))


BATTERIES = {
    "replay": battery_replay,
    "modes": battery_modes,
    "setrule": battery_setrule,
    "pwt": battery_pwt,
    "pactl": battery_pactl,
    "ghost": battery_ghost,
    "hog": battery_hog,
}

if __name__ == "__main__":
    which = sys.argv[1:] or list(BATTERIES)
    for b in which:
        print(f"### battery {b} start {utc()}", flush=True)
        BATTERIES[b]()
        print(f"### battery {b} done {utc()}", flush=True)
