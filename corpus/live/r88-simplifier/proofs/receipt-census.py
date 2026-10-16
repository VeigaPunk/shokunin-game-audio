#!/usr/bin/env python3
"""Receipt census over the btwit-r88 runs (structure: entries live under
`measurements[<probe>]`). Verdict surfaces, leg-key census, error
classes realized, and the surfaces relevant to the fold items."""
import json
import glob
import hashlib
import os

RUNS = sorted(glob.glob(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "runs",
    "*btwit-r88", "measurements.json")))

def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

PROBES = ("btabs_bluez_r88_probe", "witdiff_dump_r88_probe",
          "pwtop_r88_probe")

for p in RUNS:
    doc = json.load(open(p))
    print("=" * 74)
    print("run:", os.path.basename(os.path.dirname(p)))
    print("sha256:", sha(p))
    print("mode:", doc.get("mode"))
    m = doc.get("measurements") or {}
    print("measurement keys:", len(m))
    for probe in PROBES:
        e = m.get(probe)
        if e is None:
            print(f"  {probe}: ABSENT")
            continue
        legs = e.get("legs") or {}
        print(f"  {probe}: legs={len(legs)} "
              f"failures={e.get('failures')} "
              f"blocked={e.get('blocked')} "
              f"coverage_blocked={e.get('coverage_blocked')}")
        print(f"      unloads={sorted((e.get('unloads') or {}).keys())} "
              f"sinks_gone={e.get('sinks_gone')} "
              f"own_nodes_after={e.get('own_nodes_after')} "
              f"foreign_r88a={e.get('foreign_r88a_nodes')}")
        print(f"      refs={e.get('refs')}")
        cls = {}
        for k, l in legs.items():
            if isinstance(l, dict) and l.get("error_class"):
                cls.setdefault(l["error_class"], []).append(k)
        for c, ks in sorted(cls.items()):
            print(f"      class {c:26s} x{len(ks):3d} {sorted(set(ks))}")
    txt = open(p).read()
    for needle in ("unsupported type", "cli_unsupported_type",
                   "_frames_cache", "toprec", "pwtop_connect_down",
                   "pwdump_invalid_opt", "cli_enum_notimpl",
                   "pa_sendmsg_noent", "pwcli_remote_einval",
                   "pwcli_remote_enoent"):
        print(f"  needle {needle!r}: {txt.count(needle)}")
