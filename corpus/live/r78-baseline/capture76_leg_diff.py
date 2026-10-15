#!/usr/bin/env python3
"""r78-baseline leg-level environmental diff for the capture-r76 row.

Groups every differing leaf of (fresh capture-r76 row 03) vs (r77-baseline
Phase-1 capture-r76 receipt) by the probe and the leg it belongs to, so the
report can name the environmental set per leg instead of asserting it.

Class per leg (first matching rule wins):
  ENV-INVENTORY   inventory.* leaves (sources/monitors/devices/plugins)
  ENV-ROUTE       gate.{arecord_default,arecord_pipewire} /
                  device_axis.legs.{default,pipewire} — the plugin routes that
                  the DualSense default source unblocked
  ENV-DEVICE      gate.{parec,parecord}_no_device — the no-device legs that now
                  block instead of returning pa_no_such_entity
  ENV-SOURCE      legs whose target resolves through the new default source
                  (src / @DEFAULT_SOURCE@ / the DualSense node name)
  CONTENTION      hw:0,0 / monitor legs whose ref verdict was a busy/held shape
  JITTER          frame-count / wall-clock / duration leaves
  PATH            env-infix path leaves
  OTHER           anything else (printed in full)
Writes capture76-leg-diff.txt.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
FRESH = (HERE / "measure-env" / "corpus" / "live" / "runs"
         / "20261014T213136105621Z-capture-r76" / "measurements.json")
REF = (REPO / "corpus" / "live" / "r77-baseline" / "measure-env" / "corpus"
       / "live" / "runs" / "20261014T194043238882Z-capture-r76"
       / "measurements.json")

JITTER = re.compile(r"\.(wall_s|frames|data_actual|data_declared|bytes|"
                    r"duration_s|duration_bucket_s|honest_frames|"
                    r"declared_frames|value|raw|peak|sha256_16|rms|"
                    r"nonzero_frac|data_64k_aligned|first_sample|last_sample|"
                    r"eintr|resumes|retries)$")
ENV_ROUTE = re.compile(r"gate\.(arecord_default|arecord_pipewire)|"
                       r"device_axis[^.]*\.legs\.(default|pipewire)")
ENV_DEVICE = re.compile(r"gate\.(parec_no_device|parecord_no_device)")
ENV_INV = re.compile(r"\.inventory\.")
ENV_SOURCE = re.compile(r"DualSense|Direct__Direct__|default_source")


def leaves(obj, prefix=""):
    if isinstance(obj, dict):
        for k in sorted(obj):
            yield from leaves(obj[k], f"{prefix}.{k}" if prefix else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from leaves(v, f"{prefix}[{i}]")
    else:
        yield prefix, obj


def leg_of(key):
    """measurements.<probe>.<rest> -> probe + leg."""
    parts = key.split(".")
    probe = parts[1] if len(parts) > 1 else "?"
    # strip the probe prefix, then find the leg container
    rest = parts[2:]
    for i, p in enumerate(rest):
        if p in ("legs", "cells", "gate"):
            return probe, "/".join(rest[i + 1:i + 2]) or "-"
        if p in ("inventory", "viability", "failures", "probe", "warmup"):
            return probe, p
    return probe, ".".join(rest[:2]) or "-"


def main():
    f = json.loads(FRESH.read_bytes())
    r = json.loads(REF.read_bytes())
    fk, rk = dict(leaves(f)), dict(leaves(r))
    out = [f"fresh: {FRESH}", f"ref:   {REF}", ""]
    only_f = sorted(set(fk) - set(rk))
    only_r = sorted(set(rk) - set(fk))
    diffs = [k for k in sorted(set(fk) & set(rk)) if fk[k] != rk[k]]
    out.append(f"leaves fresh={len(fk)} ref={len(rk)} only-fresh={len(only_f)} "
               f"only-ref={len(only_r)} differing={len(diffs)}")
    groups = {}
    for k in diffs:
        probe, leg = leg_of(k)
        if ENV_INV.search(k):
            cls = "ENV-INVENTORY"
        elif ENV_ROUTE.search(k):
            cls = "ENV-ROUTE"
        elif ENV_DEVICE.search(k):
            cls = "ENV-DEVICE"
        elif ENV_SOURCE.search(json.dumps(fk[k])) or \
                ENV_SOURCE.search(json.dumps(rk[k])):
            cls = "ENV-SOURCE"
        elif ".stderr_tail" in k or "pw_capture_ports" in k:
            cls = "DECLARED"
        elif JITTER.search(k):
            cls = "JITTER"
        elif isinstance(fk[k], str) and "corpus/" in fk[k]:
            cls = "PATH"
        else:
            cls = "OTHER"
        groups.setdefault((cls, probe, leg), []).append(k)
    for (cls, probe, leg), keys in sorted(groups.items()):
        out.append(f"[{cls}] {probe} :: {leg} :: {len(keys)} leaves")
        for k in keys[:6]:
            out.append(f"      {k}\n        fresh={json.dumps(fk[k])[:110]}"
                       f"\n        ref  ={json.dumps(rk[k])[:110]}")
        if len(keys) > 6:
            out.append(f"      … +{len(keys) - 6} more")
    out.append("")
    out.append("=== only-fresh leaves (grouped) ===")
    g2 = {}
    for k in only_f:
        probe, leg = leg_of(k)
        g2.setdefault((probe, leg), []).append(k)
    for (probe, leg), keys in sorted(g2.items()):
        out.append(f"  {probe} :: {leg} :: {len(keys)}")
    out.append("=== only-ref leaves (grouped) ===")
    g3 = {}
    for k in only_r:
        probe, leg = leg_of(k)
        g3.setdefault((probe, leg), []).append(k)
    for (probe, leg), keys in sorted(g3.items()):
        out.append(f"  {probe} :: {leg} :: {len(keys)}")
    (HERE / "capture76-leg-diff.txt").write_text("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
