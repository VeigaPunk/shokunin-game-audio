#!/usr/bin/env python3
"""Reproduction of the r85v2 co-tenancy crash mechanism, on the COMMITTED
blob (2a49d540, blob 0b49d554..., sha256 714564a...):

A node whose `node.name` is purely numeric is emitted by pw-dump as a JSON
NUMBER, and the fixture's node-name readers assume strings:
  * _alsapw_r84_cands   : `any(s in n["name"] ...)` -> TypeError (int)
  * _playback_r78_node_names : sorted({...} - {None}) -> TypeError
    ('<' not supported between int and str)

Bounded: one probe-owned numeric sink, name-verified unload, residue check.
"""
import importlib.util
import json
import subprocess
import sys
import time
from pathlib import Path

BLOB = Path("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/"
            "r85-reviewer/measure_audio_2a49d540.py")
DIG = "123456789"
OUT = Path(__file__).resolve().parent


def sh(argv, timeout=15):
    p = subprocess.run(argv, capture_output=True, timeout=timeout)
    return p.returncode, p.stdout.decode(errors="replace"), \
        p.stderr.decode(errors="replace")


def main():
    rep = {"blob": str(BLOB), "digits": DIG, "steps": {}}
    rc, out, err = sh(["pactl", "load-module", "module-null-sink",
                       "sink_name=" + DIG])
    rep["steps"]["load"] = {"rc": rc, "module_id": out.strip(),
                            "err": err.strip()[:120]}
    try:
        time.sleep(1.0)
        rc, out, err = sh(["pw-dump"])
        dump = json.loads(out or "[]")
        hits = []
        for o in dump:
            if not str(o.get("type", "")).endswith("Node"):
                continue
            props = ((o.get("info") or {}).get("props") or {})
            nm = props.get("node.name")
            if nm is not None and str(nm) == DIG:
                hits.append({"json_type": type(nm).__name__,
                             "value": nm,
                             "object_serial": props.get("object.serial")})
        rep["numeric_node_props"] = hits
        # import the committed blob as a module (definitions only)
        spec = importlib.util.spec_from_file_location("r85pinned", BLOB)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        try:
            names = m._playback_r78_node_names()
            rep["steps"]["r78_node_names"] = {"ok": True, "n": len(names)}
        except Exception as exc:  # noqa: BLE001
            rep["steps"]["r78_node_names"] = {
                "ok": False, "exc": f"{type(exc).__name__}: {exc}"}
        g = m._alsapw_r84_graph()
        try:
            cands = m._alsapw_r84_cands(g, "alsa_playback.aplay")
            rep["steps"]["r84_cands"] = {"ok": True, "n": len(cands)}
        except Exception as exc:  # noqa: BLE001
            rep["steps"]["r84_cands"] = {
                "ok": False, "exc": f"{type(exc).__name__}: {exc}"}
        # the r85 reader tolerates it? (_pactlmon_r85_node compares ==)
        try:
            n = m._pactlmon_r85_node(m._pactlmon_r85_graph(), DIG)
            rep["steps"]["r85_node_lookup"] = {
                "ok": True, "found": n is not None}
        except Exception as exc:  # noqa: BLE001
            rep["steps"]["r85_node_lookup"] = {
                "ok": False, "exc": f"{type(exc).__name__}: {exc}"}
    finally:
        rc_m, mods, _ = sh(["pactl", "list", "modules", "short"])
        idx = [ln.split("\t")[0] for ln in mods.splitlines() if DIG in ln]
        rep["steps"]["unload"] = {"idx": idx, "rc": sh(
            ["pactl", "unload-module", idx[0]])[0] if idx else None}
        time.sleep(0.5)
        rc_s, sinks, _ = sh(["pactl", "list", "sinks", "short"])
        rep["residue_sinks"] = [ln for ln in sinks.splitlines() if DIG in ln]
    return rep


if __name__ == "__main__":
    r = main()
    (OUT / "numeric-node-repro.json").write_text(
        json.dumps(r, indent=1, default=str) + "\n")
    print(json.dumps(r, indent=1, default=str))
    sys.exit(0)
