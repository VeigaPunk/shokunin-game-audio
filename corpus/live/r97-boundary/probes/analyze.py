#!/usr/bin/env python3
"""r97b analyze — compact, receipt-grounded extraction for the boundary report.

Reads every receipt JSON in receipts/ and prints the facts the verdict table
needs. Read-only; prints to stdout.
"""
import json, os, sys

SEAT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REC = os.path.join(SEAT, "receipts")


def load(name):
    p = os.path.join(REC, name)
    if not os.path.exists(p):
        return None
    try:
        return json.load(open(p))
    except Exception as e:
        return {"_error": repr(e)}


def sec(t):
    print("\n" + "=" * 78)
    print(t)
    print("=" * 78)


def main():
    which = sys.argv[1:] or ["a_arming", "a2", "b_access", "c_defaults", "d_linking",
                             "e_wpexec", "f_settings", "w_wedge", "g", "wedge"]

    if "a_arming" in which:
        d = load("a_arming.json")
        if d:
            sec(f"a_arming arm={d.get('arm')} loadavg {d.get('loadavg_start')} -> {d.get('loadavg_end')}")
            for rep in d["reps"]:
                for v, x in rep["variants"].items():
                    marks = [k for k, y in x["failure_marks"].items() if y]
                    print(f"  rep{rep['rep']} {v} rc={x['rc']} timed={x['timed_out']} "
                          f"raw={x['raw_len']} frags={x['fragments_opened']} "
                          f"marks={marks} using={x['using_config']}")
    if "a2" in which:
        d = load("a2_core_no_modules.json")
        if d:
            sec("a2 core-without-context.modules")
            for rep in d["reps"]:
                for k, L in rep["legs"].items():
                    print(f"  rep{rep['rep']} {k} rc={L['rc']} timed={L['timed_out']} "
                          f"chain={[c for c, y in L['chain'].items() if y]}")
    if "b_access" in which:
        d = load("b_access.json")
        if d:
            sec(f"b_access arm={d.get('arm')} loadavg {d.get('loadavg_start')} -> {d.get('loadavg_end')}")
            for rep in d["reps"]:
                for c, o in rep["cells"].items():
                    print(f"  rep{rep['rep']} {c} sock={o['sock_present']} "
                          f"answered={o['answered']} cli_rc={o['pw_cli']['rc']} "
                          f"cli_timed={o['pw_cli']['timed_out']} {o['pw_cli']['dur_s']}s "
                          f"dump_rc={o['pw_dump']['rc']} dump_len={o['pw_dump']['out_len']}")
    if "c_defaults" in which:
        d = load("c_defaults.json")
        if d:
            sec(f"c_defaults arm={d.get('arm')} loadavg {d.get('loadavg_start')} -> {d.get('loadavg_end')} "
                f"recoveries={len(d.get('wedge_recoveries', []))}")
            for r in d["reps"]:
                print(f"  -- rep {r['rep']} attempt={r.get('attempt')} "
                      f"wedge_events={r.get('wedge_events')} {r.get('aborted', '')} {r.get('context', '')}")
                for s in r["steps"]:
                    keep = {k: v for k, v in s.items()
                            if k in ("ok", "default", "secs", "polls", "max_dump_s", "found",
                                     "node", "rows", "error")}
                    print(f"     {s['tag']:<44} {json.dumps(keep)[:170]}")
                for k in ("state_file_after_c4", "state_before", "state_after", "state_file_final"):
                    if k in r:
                        print(f"     {k}: {json.dumps(r[k])[:220]}")
    if "d_linking" in which:
        d = load("d_linking.json")
        if d:
            sec(f"d_linking arm={d.get('arm')} loadavg {d.get('loadavg_start')} -> {d.get('loadavg_end')}")
            for r in d["reps"]:
                print(f"  -- rep {r['rep']}")
                for o in r["obs"]:
                    if o["tag"] == "setup":
                        print(f"     setup id_a={o['id_a']} id_b={o['id_b']} "
                              f"serial_a={o['serial_a']} default={o['default']}")
                    elif "links" in o:
                        print(f"     {o['tag']:<34} links={o['links']} "
                              f"stderr={o['stop']['stderr'].strip()[:60]!r}")
                    else:
                        print(f"     {o['tag']:<34} before={o['before']} after={o['after']}")
    if "e_wpexec" in which:
        d = load("e_wpexec.json")
        if d:
            sec(f"e_wpexec arm={d.get('arm')} loadavg {d.get('loadavg_start')} -> {d.get('loadavg_end')}")
            for rep in d["reps"]:
                print(f"  -- rep {rep['rep']}")
                for k, v in rep["legs"].items():
                    if k == "e10_settings_inert":
                        print(f"     e10 before={v['before']['stdout'].strip()[:100]}")
                        print(f"     e10 after_false={v['after_false']['stdout'].strip()[:100]}")
                    elif isinstance(v, dict) and "rc" in v:
                        head = [l for l in v["stdout"].splitlines()
                                if l.startswith(("FOUND", "MISSING", "ENV="))]
                        print(f"     {k:<22} rc={v['rc']} timed={v['timed_out']} "
                              f"{(head[0][:80] + ' | ' + head[1][:60]) if len(head) > 1 else (v['stdout'].strip()[:80] or v['stderr'].strip()[:80])!r}")
    if "f_settings" in which:
        d = load("f_settings.json")
        if d:
            sec(f"f_settings arm={d.get('arm')}")
            for rep in d["reps"]:
                L = rep["legs"]["f1_listing"]
                print(f"  rep{rep['rep']} keys={L['n_keys']} sha={L['sha256'][:16]} "
                      f"rc={L['rc']} {L['dur_s']}s bytes={L['bytes']}")
                print(f"     metadata: {json.dumps({k: v['rows'] for k, v in rep['legs']['f2_metadata_faces'].items()})}")
            print("  shared:", d["f3_shared_listing"]["n_keys"],
                  d["f3_shared_listing"]["sha256"][:16])
            print("  diff:", json.dumps(d.get("f4_diff")))
            print("  scout compare:", json.dumps(d.get("f5_scout_list_compare")))
    if "w_wedge" in which:
        d = load("w_wedge.json")
        if d:
            sec(f"w_wedge arm={d.get('arm')} loadavg {d.get('loadavg_start')} -> {d.get('loadavg_end')}")
            for v in d["variants"]:
                print(f"  {v['variant']:<24} wedge_at={v.get('wedge_at')} "
                      f"steps={len(v['log'])} loadavg={v['loadavg_start']} "
                      f"hogs={v['hogs']} {v.get('skipped', '')}")
    if "wedge" in which:
        d = load("wedge_forensics.json")
        if d:
            sec("wedge_forensics")
            print("  pw_dump:", json.dumps(d["wf1_pw_dump"]))
            print("  pw_cli :", json.dumps({k: v for k, v in d["wf1_pw_cli_ls_client"].items()
                                            if k != "stdout"}))
            print("  wpctl  :", json.dumps(d["wf1_wpctl_status"]))
            print("  core   :", json.dumps({k: v for k, v in d["wf1_core_proc"].items()
                                            if k != "threads"}))
            print("  wp     :", json.dumps({k: v for k, v in d["wf1_wp_proc"].items()
                                            if k != "threads"}))
            print("  wp kill:", d["wf2_kill_wp"],
                  "after:", json.dumps(d["wf2_health_after_wp_kill"]))
            print("  rearm  :", json.dumps(d["wf3_health_after_rearm"]))
        led = os.path.join(REC, "wedge_ledger.jsonl")
        if os.path.exists(led):
            print("  ledger:")
            for line in open(led):
                print("   ", line.strip()[:200])
    if "g" in which:
        d = load("g_sibling_exit.json")
        if d:
            sec("g_sibling_exit")
            print("  g1:", json.dumps(d.get("g1_sibling"))[:700])
            print("  g3:", json.dumps(d.get("g3_census_with_main_up"))[:400])
            print("  g4:", json.dumps(d.get("g4_after_down"))[:500])
            print("  daemons start:", json.dumps(d.get("g2_shared_daemons_at_start")))
            print("  daemons end  :", json.dumps(d.get("g2_shared_daemons_at_end")))
            for k in ("g5_state_at_start", "g5_state_at_end"):
                v = d.get(k) or {}
                print(f"  {k}: " + json.dumps({kk: {a: b for a, b in vv.items() if a != 'head'}
                                               for kk, vv in v.items()})[:300])


if __name__ == "__main__":
    main()
