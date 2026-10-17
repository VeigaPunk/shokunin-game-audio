#!/usr/bin/env python3
"""Compact verdict/coverage summary of an audio-shokunin receipt.

Prints, per r7x/r8x probe entry: leg count, failures, named outcomes,
coverage blocks, teardown (own_nodes_after / sinks_gone), and the
contention census. Used to characterise the post-commit arm's own
measurements without dumping 1 MB of JSON.
"""
import json, sys

R79 = ["loopback_shape_r79_probe", "loopback_capture_lattice_r79_probe",
       "loopback_playback_lattice_r79_probe", "loopback_matrix_r79_probe",
       "loopback_record_target_r79_probe", "loopback_hotplug_r79_probe",
       "pwcat_latency_r79_probe", "filterchain_module_r79_probe"]
R78 = ["playback_target_lattice_r78_probe", "playback_default_follow_r78_probe",
       "playback_target_loss_r78_probe", "playback_props_r78_probe",
       "playback_class_segv_r78_probe", "playback_aplay_axis_r78_probe",
       "capture_unlinked_zeros_r78_probe", "capture_parec_fix_r78_probe"]

def entry_line(k, e):
    legs = e.get("legs") or {}
    bits = [f"{k}: legs={len(legs)}"]
    if e.get("class"):
        bits.append(f"class={e['class']}")
    if e.get("classes_extra"):
        bits.append(f"extra={e['classes_extra']}")
    if e.get("failures"):
        bits.append(f"FAILURES={e['failures']}")
    else:
        bits.append("failures=[]")
    if "own_nodes_after" in e:
        bits.append(f"own_nodes_after={e['own_nodes_after']}")
    if "sinks_gone" in e:
        sg = e["sinks_gone"]
        # r81 fix (r80 copy crashed on the r78 family's bool shape):
        if isinstance(sg, bool):
            bits.append(f"sinks_gone={sg}")
        else:
            bits.append(f"sinks_gone={all(sg.values()) if sg else '{}'}")
    no = e.get("named_outcomes")
    if no:
        bits.append(f"named_outcomes={len(no)}")
    cb = [l for l, v in legs.items() if isinstance(v, dict)
          and (v.get("blocked") or v.get("coverage_blocked"))]
    if cb:
        bits.append(f"blocked_legs={cb}")
    return "  " + " | ".join(str(b) for b in bits)

def main(path):
    d = json.load(open(path))
    m = d["measurements"]
    print(f"# {path}")
    print(f"# mode={d['mode']} cases={len(m)}")
    fails = {k: v["failures"] for k, v in m.items() if v.get("failures")}
    print(f"# cases with failures: {len(fails)}")
    for k, f in fails.items():
        print(f"  FAIL {k}: {f}")
    for group, names in (("r79 entries", R79), ("r78 entries", R78)):
        present = [n for n in names if n in m]
        if not present:
            continue
        print(f"## {group} ({len(present)}/{len(names)})")
        for n in present:
            print(entry_line(n, m[n]))
    r79 = [n for n in R79 if n in m]
    if r79:
        tot_legs = sum(len(m[n].get("legs") or {}) for n in r79)
        print(f"## r79 total legs: {tot_legs}")
        nos = [o for n in r79 for o in (m[n].get("named_outcomes") or [])]
        print(f"## r79 named_outcomes: {len(nos)}")
        for o in nos[:12]:
            print(f"   - {o[:160]}")
        if len(nos) > 12:
            print(f"   … {len(nos) - 12} more")
    cont = {n: m[n].get("contention") for n in list(m) if m[n].get("contention")}
    if cont:
        keys = sorted(cont)
        print("## contention census (per entry, first 3 keys shown)")
        for k in keys[:3]:
            c = cont[k]
            print(f"   {k}: {json.dumps({kk: c[kk] for kk in list(c)[:12]})}")
        quiet = [k for k, c in cont.items() if c.get("host_is_quiet")]
        print(f"   host_is_quiet True in {len(quiet)}/{len(cont)} entries")

if __name__ == "__main__":
    for p in sys.argv[1:]:
        main(p)
