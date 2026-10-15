#!/usr/bin/env python3
"""r88b analysis — consolidate every receipt into receipts/summary.json with verdicts.

Reads only files under corpus/live/r88-boundary/ (plus the scout's receipts for the
verbatim-replay and provenance comparisons) and writes receipts/summary.json.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]           # corpus/live/r88-boundary
REC = ROOT / "receipts"
RAW = ROOT / "raw"
SCOUT = ROOT.parent / "r88-scout"


def j(name):
    return json.loads((REC / name).read_text())


def raw(name, i=1, ext="txt"):
    p = RAW / f"{name}.{i}.{ext}"
    return p.read_text() if p.exists() else None


def main():
    summary = {"generated_utc": None, "verdicts": [], "numbers": {}, "contention": []}

    # ---------- replay: verbatim equality with the scout's own receipts
    replay = j("B1-replay.json")
    scout_ref = json.loads((SCOUT / "receipts" / "r88-legs.json").read_text())
    scout_by_leg = {l["leg"]: l for l in scout_ref["legs"]}
    scout_analysis = json.loads((SCOUT / "receipts" / "analysis.json").read_text())
    replay_cmp = []
    for leg in replay["legs"]:
        nm = leg["leg"]
        if nm not in scout_by_leg:
            continue
        s = scout_by_leg[nm]
        # the scout's receipt rows carry hashes only; authoritative text lives in their raw/
        scout_txt = set()
        for i in range(1, s["reps"] + 1):
            p = SCOUT / "raw" / f"{nm}.{i}.err"
            if p.exists():
                scout_txt.add(p.read_text().strip())
        mine_txt = {(raw(nm, i, "err") or "").strip() for i in range(1, leg["reps"] + 1)}
        replay_cmp.append({
            "leg": nm,
            "reps_mine": leg["reps"], "reps_scout": s["reps"],
            "rc_match": set(leg["rcs"]) == set(s["rcs"]) and len(leg["rcs"]) == len(s["rcs"]),
            "rc_values_match": set(leg["rcs"]) == set(s["rcs"]),
            "rep_count_differs": len(leg["rcs"]) != len(s["rcs"]),
            "stderr_text_match": (mine_txt == scout_txt) if scout_txt else None,
            "mine_rcs": leg["rcs"], "scout_rcs": s["rcs"],
            "mine_stderr": sorted(mine_txt), "scout_stderr": sorted(scout_txt),
        })
    summary["numbers"]["replay_legs_compared"] = len(replay_cmp)
    summary["numbers"]["replay_rc_value_mismatches"] = [c["leg"] for c in replay_cmp if not c["rc_values_match"]]
    summary["numbers"]["replay_rc_shape_diffs_repcount_only"] = [
        c["leg"] for c in replay_cmp if c["rc_values_match"] and c["rep_count_differs"]]
    summary["numbers"]["replay_stderr_mismatches"] = [c["leg"] for c in replay_cmp if c["stderr_text_match"] is False]
    summary["numbers"]["replay_exact_rc_and_text_matches"] = [
        c["leg"] for c in replay_cmp if c["rc_match"] and c["stderr_text_match"] is not False]
    summary["replay_comparison"] = replay_cmp

    # ---------- setrule
    sr = j("B3-setrule.json")
    summary["numbers"]["setrule"] = {
        "keys": sr["n_keys"], "stable_keys_all_match": all(r["match"] for r in sr["results"] if r["stable"]),
        "n_stable": sum(1 for r in sr["results"] if r["stable"]),
        "n_mismatch": sr["n_mismatch"], "n_mismatch_stable": sr["n_mismatch_stable"],
        "n_bundles": sr["n_bundles"],
        "serial_only_unknown_by_pwcli": f'{sr["n_cli_serial_only_unknown"]}/{sr["n_cli_serial_only_total"]}',
        "nested_checks": sr["nested_checks"], "nested_violations": len(sr["nested_violations"]),
        "cli_violations": sr["cli_violations"],
        "silent_empty_rc0_ids": [c["key"] for c in sr["cli_results"] if c["stdout_len"] == 0 and c["rc"] == 0],
    }
    census_before = json.loads((RAW / "census-setrule-before.json").read_text())
    ids = [o["id"] for o in census_before]
    shifted = [o["info"]["props"]["object.serial"] for o in census_before
               if o.get("info", {}).get("props", {}).get("object.serial") is not None
               and o["info"]["props"]["object.serial"] != o["id"]]
    summary["numbers"]["bundle_mechanism"] = {
        "max_live_id": max(ids), "min_shifted_serial": min(shifted) if shifted else None,
        "disjoint": (max(ids) < min(shifted)) if shifted else None,
        "n_shifted_objects": len(shifted),
    }

    # ---------- pw-top
    pwt = j("B4-pwt.json")
    n1 = [l for l in pwt["legs"] if l["leg"].startswith("pwt-n1")]
    n23 = [l for l in pwt["legs"] if re.match(r"pwt-n[234]", l["leg"])]
    summary["numbers"]["pwt"] = {
        "n1_all_C": f'{sum(1 for l in n1 if l["all_C"])}/{len(n1)}',
        "n1_wall_ms": sorted(l["wall_ms"] for l in n1),
        "first_frame_all_C": f'{sum(1 for l in n23 if l["frames"] and all(s == "C" for s in l["frames"][0]["states"]))}/{len(n23)}',
        "wall_ms_n2": [l["wall_ms"] for l in n23 if l["leg"].startswith("pwt-n2")],
        "wall_ms_n3": [l["wall_ms"] for l in n23 if l["leg"].startswith("pwt-n3")],
        "wall_ms_n4": [l["wall_ms"] for l in n23 if l["leg"].startswith("pwt-n4")],
        "frame_counts": {l["leg"]: l["n_frames"] for l in n23},
        "corr_wall_ms": [c["wall_ms"] for c in pwt["corr"]],
    }
    hog = j("B7-hog.json")
    hn1 = [l for l in hog["legs"] if l.get("all_C") is not None]
    summary["numbers"]["pwt_under_hog"] = {
        "n1_all_C": f'{sum(1 for l in hn1 if l["all_C"])}/{len(hn1)}',
        "load_before": hog["load_before"].strip().split("\n"),
        "load_under": hog["load_under"].strip().split("\n"),
        "load_after": hog["load_after"].strip().split("\n"),
        "mine": len(hog["mine_pids"]), "killed": len(hog["killed"]), "final": hog["final_r88b_hog"],
        "setrule_spot": [l for l in hog["legs"] if l["leg"] == "hog-setrule-spot"][0],
    }

    # ---------- pactl map
    pactl = j("B5-pactl.json")
    c0 = json.loads((REC / "census-pactl-0.json").read_text())
    objs = json.loads((RAW / "census-pactl-0.json").read_text())

    def props(o):
        return o.get("info", {}).get("props", {})

    by_name = {(props(o).get("node.name") or props(o).get("device.name")):
               (o["id"], props(o).get("object.serial")) for o in objs}
    by_serial = {props(o).get("object.serial"): (o["id"], props(o).get("node.name")) for o in objs}

    def check(lines, resolve_monitor=False):
        rows = []
        for ln in lines.splitlines():
            if not ln.strip():
                continue
            f = ln.split("\t")
            idx, name = f[0], f[1]
            base = name[:-8] if (resolve_monitor and name.endswith(".monitor")) else name
            nid, ser = by_name.get(base, (None, None))
            rows.append({"idx": idx, "name": name, "native_id": nid, "serial": ser,
                         "idx_eq_serial": str(ser) == idx, "idx_eq_id": str(nid) == idx})
        return rows

    sinks = check(c0["pactl_sinks"])
    sources = check(c0["pactl_sources"], resolve_monitor=True)
    cards = check(c0["pactl_cards"])
    si = []
    for ln in c0["pactl_sink_inputs"].splitlines():
        if ln.strip():
            idx = ln.split("\t")[0]
            tgt = by_serial.get(int(idx)) if idx.isdigit() else None
            si.append({"idx": idx, "native_serial_owner": tgt})
    summary["numbers"]["pactl_map"] = {
        "sinks": f'{sum(1 for r in sinks if r["idx_eq_serial"])}/{len(sinks)}',
        "sources": f'{sum(1 for r in sources if r["idx_eq_serial"])}/{len(sources)}',
        "cards": f'{sum(1 for r in cards if r["idx_eq_serial"])}/{len(cards)}',
        "sink_inputs": f'{sum(1 for r in si if r["native_serial_owner"])}/{len(si)}',
        "discriminators_serial_ne_id": [r for r in sinks if r["idx_eq_serial"] and not r["idx_eq_id"]],
    }

    # ---------- ghost
    gh = j("B6-ghost.json")
    summary["numbers"]["ghost"] = {
        "brackets": gh["n_brackets"], "pulse_only_events": gh["n_pulse_only_events"],
        "load_rc": gh["load"]["rc"], "unload_rc": gh["unload"]["rc"],
        "pulse_n_alive": sorted({b["pulse_n"] for b in gh["brackets"] if b["tag"] == "alive"}),
        "pulse_n_post": sorted({b["pulse_n"] for b in gh["brackets"] if b["tag"] == "post-unload"}),
    }

    # ---------- state A/B
    st = j("B10-state.json")
    summary["numbers"]["state_ab"] = {
        "idle": [{"pactl": t["pactl_state"], "native": t["native"][1], "ptop": t["ptop_state"]} for t in st["A_idle"]],
        "active": [{"pactl": t["pactl_state"], "native": t["native"][1], "ptop": t["ptop_state"]} for t in st["B_active"]],
        "notes": {k: v for k, v in st["notes"].items() if k != "pwcat_stderr"},
    }

    # ---------- fix / modes / keyset
    fx = j("B8-fix.json")
    summary["numbers"]["witness_coverage"] = {
        "ls_counts": {k: {"n": v["n"], "expected": v["expected_n"], "missing": v["missing"], "extra": v["extra"]}
                      for k, v in fx["ls"].items()},
        "info_all": fx["info_all"],
        "param_names_rejected": sorted({r["param"] for r in fx["param_matrix"]
                                        if "unknown param type" in r["err"]}),
        "param_class_limits": sorted({r["err"] for r in fx["param_matrix"] if "not implemented" in r["err"]}),
        "stale_global_error": sorted({r["err"] for r in fx["param_matrix"] if "Stale file handle" in r["err"]}),
    }
    ks = j("B11-keyset.json")
    summary["numbers"]["keyset"] = {k: {"id": v["id"], "n_dump": v["n_dump"], "n_cli": v["n_cli"],
                                        "only_in_dump": v["only_in_dump"], "only_in_cli": v["only_in_cli"],
                                        "n_typed": v["n_typed"]} for k, v in ks["objects"].items()}
    br = j("B9-bracket.json")
    summary["numbers"]["ls_metadata_disagreement"] = [
        {"round": r["i"], "dump": r["meta_dump"], "ls": r["meta_ls"], "ls_extra": r["meta_ls_extra"]}
        for r in br["rounds"]]

    # ---------- scout provenance recompute
    add = json.loads((SCOUT / "receipts" / "r88-addendum.json").read_text())
    legs_all = scout_ref["legs"] + add["legs"]
    summary["numbers"]["scout_provenance"] = {
        "legs_total": len(legs_all),
        "stable_stdout": sum(1 for l in legs_all if l.get("stable_stdout")),
        "unstable": [l["leg"] for l in legs_all if not l.get("stable_stdout")],
        "claim_in_report": "56/62 legs byte-identical",
        "set_card_profile_receipt_present": any(
            "set-card-profile" in json.dumps(l) for l in scout_ref["legs"]),
    }

    # ---------- verdicts
    V = summary["verdicts"]
    def add(id_, claim, verdict, evidence):
        V.append({"id": id_, "claim": claim, "verdict": verdict, "evidence": evidence})

    add("V1", "bluez audio device class absent; paired DualSense is HID-only and cannot become audio",
        "SURVIVES (re-measured post-reboot)",
        "bluez tree = adapter + dev_BC_C7_46_34_C5_66 only; device Class 1288, Icon input-gaming, "
        "Connected=false, Paired=true, UUIDs = HID 0x1124 + PnP 0x1200; pactl cards = 3 ALSA only; "
        "pactl-list bluez|a2dp|sco matches = 1 (session.services); no bluez5 Device in pw-dump")
    add("V2", "module-bluez5 does not exist on this host (pactl load-module refuses rc 1)",
        "SURVIVES", "6/6 load-module refusals rc 1 'Failure: No such entity' (3 discover + 3 device + path + arg "
        "variant); find /usr/lib* = 0; pacman -Ql pipewire bluez = 0; SPA lib owned by pipewire-audio; "
        "module-id set identical before/after")
    add("V3", "the rc-1 refusal text identifies a missing object (scout's inference)",
        "WEAKENED (confound)", "control: set-card-profile on an existing ALSA card with a BOGUS profile also "
        "returns rc 1 'Failure: No such entity' — the text cannot distinguish 'no such card' from 'no such profile'; "
        "the card's absence is established only by the independent pactl list cards witness")
    add("V4", "the bluez stack is alive with 21 A2DP endpoints and zero devices",
        "SURVIVES across reboot", "post-reboot journal: 21 'Endpoint registered' from a single sender (:1.47 = "
        "wireplumber pid 2063), 0 unregistered; adapter Powered=true, Connectable=false, 11 UUIDs; "
        "node bluez_midi.server live (id 49, api.bluez5.midi.node)")
    add("V5", "codec switch / SBC-XQ params unmeasurable (device-absence, not stack-absence)",
        "SURVIVES (+ new witness)", "no bluez media node; create-node with api.bluez5.a2dp-sink/sink/source and "
        "api.bluez5.midi.node all refused (res -2/-22), nothing created; 14 SPA bluez5 files present")
    add("V6", "'bluez5.codecs is not a string in libspa-bluez5.so (measured absence)'",
        "FALSIFIED",
        "strings -a libspa-bluez5.so (sha256 a2e8537a…, byte-identical to the scout's inventory line) gives 2 hits: "
        "'spa.bluez5.codecs' and \"property bluez5.codecs '%s' is not an array\"; the error string proves the library "
        "parses bluez5.codecs as an array property. Standalone exact-line form is absent (grep -xc = 0), which is the "
        "likely origin of the error; the report's guidance 'do not cite bluez5.codecs as live' does not follow")
    add("V7", "'15 files in /usr/lib/spa-0.2/bluez5/'",
        "FALSIFIED (off-by-one)", "ls -1 = 14; the scout's own raw/spa-bluez5-inventory.1.txt lists 14 entries and the "
        "same sentence names 1+13=14")
    add("V8", "'56/62 legs byte-identical across fresh x3'",
        "FALSIFIED (arithmetic)", "recomputed from the scout's own receipts: 64 legs total, 58 stable; the 6 unstable "
        "legs named in the report are exactly right")
    add("V9", "pw-dump <N> returns exactly {object.id==N} U {object.serial==N}",
        "SURVIVES (exact, and mode-invariant)",
        f'{summary["numbers"]["setrule"]["n_stable"]}/{summary["numbers"]["setrule"]["n_stable"]} stable keys match; '
        f'{sr["n_mismatch"]} non-matches are all objects that died mid-sweep (rc 0, empty stdout); 0 bundles; '
        f'{sr["nested_checks"]}/{sr["nested_checks"]} checks show no nested-reference expansion (ports are never '
        "returned by their node.id); membership identical under -s/-R/-i 0")
    add("V10", "'the serial collision is not exotic: 3 of 7 live keys return a two-object bundle'",
        "NOT REPRODUCIBLE (mechanism identified)", "0 bundle keys in a 150-key universe; bundle requires a live id to "
        "equal some object's serial, and here max live id 258 < min shifted serial 47326 — the two ranges are disjoint "
        "by construction. The 3/7 rate was boot-local (fresh counters)")
    add("V11", "pw-cli info is a singleton keyed by native id only",
        "SURVIVES (extended)",
        f'{sr["n_cli_serial_only_unknown"]}/{sr["n_cli_serial_only_total"]} serial-only keys: rc 0 + unknown global; '
        "0 id-keys misreported; NEW silent classes: 6 ids return rc 0 with empty stdout and (4 of them) empty stderr; "
        "`info all` describes 135 of 141 objects; `ls <iface>` DOES expose object.serial (serial resolvable there)")
    add("V12", "pw-cli info and pw-dump agree on prop keys but not on types/params/state",
        "SURVIVES, extended to Device and Client",
        "device 44: 40/40 keys equal, 0 either-side-only; client 32: 41/41; bools become quoted strings "
        "(api.acp.auto-port false -> \"false\"); param values absent in cli, empty lists in dump")
    add("V13", "pw-top -n 1 is a trap (every row C = CREATING)",
        "SURVIVES under load", f'{summary["numbers"]["pwt"]["n1_all_C"]} all-C in the busy window; '
        f'{summary["numbers"]["pwt_under_hog"]["n1_all_C"]} all-C under +16 own burners; 32/32 including the scout')
    add("V14", "pw-top cadence 3-21 ms busy vs 1002 ms idle; mechanism unresolved",
        "REPRODUCED + MECHANISM RESOLVED",
        "second frame carries the driver row QUANT=1024 RATE=48000 (=21.3 ms cycle); measured per-frame wall times "
        "cluster at one cycle (n2 6.8-25.5 ms, n3 40-44 ms, n4 40-49 ms) while the graph runs, and 1010 ms when idle; "
        "unchanged under CPU hog -> stats/graph-driven, not timer- or CPU-driven")
    add("V15", "pactl index is the native serial, not the native id",
        "SURVIVES, strengthened",
        "14/14 sinks, 16/16 sources (monitor-resolved), 5/5 sink-inputs; 11 witnesses have serial!=id and every one "
        "follows the serial (e.g. r96s_ns: idx 116459, id 110, serial 116459); cards 3/3 but non-discriminating (id==serial)")
    add("V16", "'expect the pulse vocabulary to disagree with the native vocabulary on the same object'",
        "NOT REPRODUCIBLE as a rule",
        "24/24 agreement over 6 sinks x 3 tight reps; controlled A/B on my own r88b_state null sink: idle = "
        "pactl SUSPENDED / native suspended / ptop S, active (own pw-cat stream) = RUNNING / running / R, 3/3 each")
    add("V17", "scout 4.5: a pulse-only sink observed while its native node was absent",
        "NOT REPRODUCED", "0 pulse-only events in 70 tight brackets, including 15 while my own r88b_ns existed in "
        "both witnesses and 40 after unloading it (sensitivity verified: the object appeared/disappeared in step)")
    add("V18", "scout 2: `pactl set-card-profile bluez_card.BC_C7_46_34_C5_66 a2dp-sink` -> 1,1,1 'No such entity'",
        "PROVENANCE GAP + REPLICATED",
        "no receipt for that probe anywhere in corpus/live/r88-scout/; re-run 3/3 rc 1 'Failure: No such entity' "
        "(receipts B1) — but see V3 for the confound")
    add("V19", "NEW: pw-cli ls Metadata vs pw-dump disagree on the same object class",
        "NEW FINDING (reproducible)",
        "ls Metadata = 9 ids, pw-dump = 4 ids, extra [35,37,38,41,42] in 4/4 tight brackets and on both sockets; "
        "pw-dump 35 and pw-cli info 35 both return rc 0 with empty stdout while ls Metadata prints the object")
    add("V20", "NEW: pw-cli info all silently omits 6 objects",
        "NEW FINDING", "135 described vs 141 in pw-dump; missing exactly [3,5,31,34,36,39] = SecurityContext, "
        "Profiler and all 4 visible Metadata objects")
    add("V21", "NEW: rc-0 failure modes beyond the scout's list",
        "NEW FINDINGS", "pw-dump <non-numeric|overflow> = rc 0 + empty stdout + empty stderr; pw-dump '' = FULL dump; "
        "pw-dump <id1> <id2> returns only id1; pw-dump --color=always injects ANSI escapes (invalid JSON); "
        "pw-dump -1 = rc 255; pw-cli create-node failure = rc 0; pw-top -n 0 = one frame, -n -1 and -n abc = infinite "
        "(timeout), -r bogus = rc 255 'Can't connect: Host is down'")
    add("V22", "NEW: pw-cli info prop-block layout is class-dependent",
        "NEW HAZARD", "nodes/ports print flat `key = value`; Device/Client print a `* properties:` header with "
        "`*\\t\\tkey = value`; a parser tuned to nodes silently yields 0 props for devices/clients (observed while "
        "building this analysis)")

    summary["generated_utc"] = __import__("datetime").datetime.now(
        __import__("datetime").timezone.utc).isoformat(timespec="seconds")
    summary["contention"] = [
        "g3d lane `yes` burners, cwd /home/vgpnk/Projects/shokunin/game-dev-3d-shokunin (48-64 procs, ppid 1537) — "
        "the host was already at loadavg ~70 on 32 CPUs before my hog",
        "audio siblings live in the graph throughout: r82ff_ns_2737990 + r82ff_2737990_tns/tdef_*_alias/env_sink, "
        "r86b_ns, r87b_ns, r87b_ns2, r87bfmt, r89b_ns, r89b_ns44, r93s_in (graph driver, QUANT 1024), r93s_fc_in, "
        "r93s_fc_out, r93s_rec, r96s_ns, r98s_ns, r98s_stall, Lavf63.1.101, pw-play x2, pw-cat, "
        "pipewire -c filter-chain.conf (pid 2377877)",
        "my own objects, all removed: r88b_ctl, r88b_ns, r88b_state (null sinks), r88b_tone.wav, 16 r88b_hog burners "
        "(16/16 killed), r88b_stream (pw-cat, terminated)",
    ]
    (REC / "summary.json").write_text(json.dumps(summary, indent=1))
    print("verdicts:", len(V))
    print("replay rc_value_mismatches:", summary["numbers"]["replay_rc_value_mismatches"],
          "stderr_mismatches:", summary["numbers"]["replay_stderr_mismatches"],
          "exact:", len(summary["numbers"]["replay_exact_rc_and_text_matches"]), "/",
          summary["numbers"]["replay_legs_compared"])
    print("setrule stable:", summary["numbers"]["setrule"]["n_stable"],
          "all match:", summary["numbers"]["setrule"]["stable_keys_all_match"],
          "bundles:", sr["n_bundles"])


if __name__ == "__main__":
    main()
