    # ---------------- verdicts ----------------
    DEF = entry.get("default_sink_at_start") or "<unreadable-default>"
    entry["default_sink_at_end"] = _pwbind_r87_default_sink()
    if entry["default_sink_at_end"] != DEF:
        failures.append(
            f"the default sink drifted mid-entry {DEF} -> "
            f"{entry['default_sink_at_end']} — routing verdicts "
            "unstable")
    NS, NS2 = PWBIND_R87_NS, PWBIND_R87_NS2
    _pwbind_r87_expect(legs, failures, "p_own", [NS])
    _pwbind_r87_expect(legs, failures, "p_cat", [NS])
    _pwbind_r87_expect(legs, failures, "p_garbage", [DEF])
    _pwbind_r87_expect(legs, failures, "p_pb1", [DEF])
    _pwbind_r87_expect(legs, failures, "p_pb2", [NS])
    _pwbind_r87_expect(legs, failures, "p_pb3", [NS2])
    _pwbind_r87_expect(legs, failures, "p_nt", [NS])
    _pwbind_r87_expect(legs, failures, "p_nt_vs_flag", [NS])
    _pwbind_r87_expect(legs, failures, "p_nt_rev", [NS2])
    _pwbind_r87_expect(legs, failures, "p_nt_garbage", [DEF])
    _pwbind_r87_expect(legs, failures, "p_three", [NS2])
    _pwbind_r87_expect(legs, failures, "p_prop_twice", [NS2])
    _pwbind_r87_expect(legs, failures, "p_serial", [NS])
    _pwbind_r87_expect(legs, failures, "p_objid", [DEF])
    _pwbind_r87_expect(legs, failures, "p_serial_stale", [DEF])
    _pwbind_r87_expect(legs, failures, "p_prop_serial", [NS])
    _pwbind_r87_expect(legs, failures, "p_prop_objid", [DEF])
    for name in ("p_zero", "p_zero_prop", "p_noauto"):
        got = _pwbind_r87_consumers(legs[name])
        snap = _pwbind_r87_last_snap(legs[name])
        if got or not any(s.get("present")
                          for s in legs[name]["snaps"]):
            failures.append(
                f"{name}: consumers={got} present="
                f"{snap.get('present')} — the hard no-link switch "
                "fails")
    _pwbind_r87_expect(legs, failures, "p_mon", [DEF])
    _pwbind_r87_expect(legs, failures, "p_mon_cs", [DEF])
    if src:
        _pwbind_r87_expect(legs, failures, "p_src_name", [DEF])
        _pwbind_r87_expect(legs, failures, "p_src_serial", [DEF])
    else:
        entry.setdefault("coverage_blocked", []).append(
            "no foreign Audio/Source — the wrong-class source legs "
            "unmeasured")
    _pwbind_r87_expect(legs, failures, "p_env", [NS])
    _pwbind_r87_expect(legs, failures, "p_env_nobrace", [NS])
    _pwbind_r87_expect(legs, failures, "p_env_vs_prop", [NS])
    _pwbind_r87_expect(legs, failures, "p_env_garbage", [DEF])
    _pwbind_r87_expect(legs, failures, "p_mediarole", [DEF])
    _pwbind_r87_expect(legs, failures, "p_capsink", [DEF])
    _pwbind_r87_expect(legs, failures, "p_empty", [DEF])
    got = _pwbind_r87_consumers(legs.get("p_coll") or {})
    if got != [NS]:
        failures.append(
            f"p_coll: consumers={got} expected {[NS]} — the "
            "sink-wins-name-resolution law fails")
    coll_ports = [e.get("in_port_name")
                  for s in (legs.get("p_coll") or {}).get("snaps", [])
                  for e in s.get("edges_out") or []]
    if coll_ports and not all(str(p).startswith("playback_")
                              for p in coll_ports):
        failures.append(
            f"p_coll: linked to non-playback ports {coll_ports}")
    entry["legs"] = legs
    entry["failures"] = failures