    # ---------------- verdicts ----------------
    if not legs["s_link"].get("player"):
        entry.setdefault("coverage_blocked", []).append(
            "seat pw-play never linked — every schema arm below is "
            "contention, not measurement")
    l = legs["s_window"]
    st = l.get("stats") or {}
    if l.get("exit_code") != 0 or l.get("parse_error") is not None:
        failures.append(
            f"s_window: rc={l.get('exit_code')} parse="
            f"{l.get('parse_error')} — the -J window fails")
    if (st.get("own_blocks") or 0) < 3:
        failures.append(
            f"s_window: own_blocks={st.get('own_blocks')} — the seat "
            "driver was starved out of its own window")
    if st.get("own_blocks"):
        if st.get("seq_order_ok") is not True:
            failures.append(
                f"s_window: block order != info->clock->driver: "
                f"{st.get('own_seq_shapes')}")
        if not st.get("count_step_ok"):
            failures.append(
                "s_window: own info.count does not step +1/cycle")
        if st.get("quantum_relation_ok") is not True:
            failures.append(
                "s_window: next_nsec-nsec != duration/rate on own "
                "clock rows")
        if st.get("pos_step_ok") is not True:
            failures.append(
                "s_window: position += duration fails on own clock "
                "rows")
        if (st.get("transports") or []) != ["stopped"]:
            failures.append(
                f"s_window: transports={st.get('transports')} — the "
                "stopped-while-cycling trap fails")
        if (st.get("diffs") or []) != [1.0]:
            failures.append(
                f"s_window: diffs={st.get('diffs')} — virtual-driver "
                "diff != 1.0")
        if st.get("order_ok") is not True:
            failures.append(
                "s_window: prev<=signal<=awake<=finish fails on own "
                "rows")
        if st.get("prev_is_last_signal") is not True:
            failures.append(
                "s_window: prev[k+1] != signal[k] on own driver rows")
        if (st.get("driver_statuses") or []) != ["finished"]:
            failures.append(
                f"s_window: statuses={st.get('driver_statuses')} — "
                "the finished-status law fails")
        if (st.get("driver_latencies") or []) != ["0/0"]:
            failures.append(
                f"s_window: driver latencies="
                f"{st.get('driver_latencies')} — the 0/0 null-sink "
                "latency fails")
        if set(st.get("clock_ids") or ()) != \
                {entry["refs"]["own_node_id"]} or \
                set(st.get("driver_ids") or ()) != \
                {entry["refs"]["own_node_id"]}:
            failures.append(
                f"s_window: clock_ids={st.get('clock_ids')} "
                f"driver_ids={st.get('driver_ids')} != own node "
                f"{entry['refs']['own_node_id']} — the id law fails")
        if (st.get("clock_names") or []) != \
                ["clock.system.monotonic"]:
            failures.append(
                f"s_window: clock_names={st.get('clock_names')}")
        if st.get("nsec_in_window") is not True:
            failures.append(
                "s_window: own clock nsec outside the monotonic "
                "window")
        if (st.get("xruns") or [1]) != [0] or \
                (st.get("xrun_counts") or [1]) != [0]:
            failures.append(
                f"s_window: xruns={st.get('xruns')} xrun_counts="
                f"{st.get('xrun_counts')} — the virtual-driver "
                "zero-xrun law fails")
        if st.get("fclock_rows"):
            failures.append(
                "s_window: followerClock rows inside own blocks — "
                "the pw-play-follower absence fails")
        if (st.get("nsb_blocks") or 0) != 0:
            failures.append(
                f"s_window: follower-less sink emitted "
                f"{st.get('nsb_blocks')} blocks — the suspension law "
                "fails")
    l = legs["s_second"]
    c1 = (st.get("own_counts") or [None])[-1]
    c2 = (l.get("own_counts") or [None])[0]
    if not l.get("own_counts") or c1 is None or c2 is None or \
            c2 <= c1:
        failures.append(
            f"s_second: counts {c1} -> {c2} — the per-driver count "
            "monotone-persistence fails")
    l = legs["s_suspend"]
    if l.get("kill_mono") is None:
        failures.append(
            "s_suspend: the follower kill hook never fired — the "
            "leg is unmeasured")
    elif (l.get("own_pre_kill") or 0) == 0:
        failures.append(
            "s_suspend: zero own blocks before the kill — the "
            "suspension arm is vacuous")
    elif (l.get("own_after_kill") or 0) != 0:
        failures.append(
            f"s_suspend: {l.get('own_after_kill')} own blocks after "
            "follower death — the per-driver suspension law fails")
