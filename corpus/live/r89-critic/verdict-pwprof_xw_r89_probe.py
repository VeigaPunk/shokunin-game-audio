    # ---------------- verdicts ----------------
    if not legs["x_link"].get("player"):
        entry.setdefault("coverage_blocked", []).append(
            "seat pw-play never linked — every cross-witness arm "
            "below is contention, not measurement")
    l = legs["x_modreg"]
    if l.get("own_in_dump_modules") is not False or \
            l.get("own_node_in_dump") is not True or \
            str(l.get("own_pactl_idx")) not in \
            (l.get("pactl_added") or ()):
        failures.append(
            f"x_modreg: {l} — the pactl-vs-native Module mismatch "
            "fails")
    l = legs["x_blank"]
    if not l.get("blank_lines") or l.get("own_found") is None:
        failures.append(
            f"x_blank: {l} — the guarded blank-line parse fails")
    l = legs["x_foot"]
    if l.get("pwprof_during") != (l.get("pwprof_before") or 0) + 1 or \
            l.get("nodes_delta") != 0:
        failures.append(
            f"x_foot: {l} — the one-Client footprint fails")
    l = legs["x_conc"]
    if l.get("rc1") != 0 or l.get("rc2") != 0 or \
            l.get("parse1") or l.get("parse2"):
        failures.append(
            f"x_conc: rc={l.get('rc1')},{l.get('rc2')} parse="
            f"{l.get('parse1')},{l.get('parse2')} — the concurrent "
            "capture failed")
    elif not l.get("shared"):
        entry.setdefault("coverage_blocked", []).append(
            "x_conc: zero overlapping (driver,count) blocks — the "
            "streams were staggered (the r88 frame-count advisory "
            "again); the broadcast law is unmeasured this run")
    elif l.get("shared_identical") is not True:
        failures.append(
            f"x_conc: overlapping blocks differ — the one-stream "
            "broadcast law fails")
    l = legs["x_top"]
    row = l.get("own_row") or {}
    pw, pb = l.get("prof_wait_us_med"), l.get("prof_busy_us_med")
    if l.get("own_row") is None:
        entry.setdefault("coverage_blocked", []).append(
            "x_top: no real-state own row in the last pw-top frame "
            "— the cross-witness is unmeasured")
    elif pw is None or pb is None or row.get("wait_us") is None or \
            row.get("busy_us") is None:
        entry.setdefault("coverage_blocked", []).append(
            f"x_top: partial witnesses {l} — the agreement arm is "
            "unmeasured")
    else:
        def _close(a, b):
            return a is not None and b is not None and \
                0.25 <= (a / b if b else float("inf")) <= 4.0
        if not (_close(row["wait_us"], pw) and
                _close(row["busy_us"], pb)):
            failures.append(
                f"x_top: top {row['wait_us']}/{row['busy_us']}us vs "
                f"profiler {pw}/{pb}us — the WAIT/BUSY cross-witness "
                "fails")
    l = legs["x_profobj"]
    if not l.get("ids"):
        entry.setdefault("coverage_blocked", []).append(
            "x_profobj: no Profiler object in pw-dump — the refusal "
            "leg is unmeasured")
    else:
        for sub in ("info", "enum"):
            r = l.get(sub) or {}
            if r.get("exit_code") != 0 or \
                    "unsupported type PipeWire:Interface:Profiler" \
                    not in (r.get("stderr") or "") + \
                    (r.get("stdout") or ""):
                failures.append(
                    f"x_profobj.{sub}: rc={r.get('exit_code')} — the "
                    "introspection refusal fails")
    l = legs["x_sigpipe"]
    if l.get("rc") != -13:
        failures.append(
            f"x_sigpipe: rc={l.get('rc')} — the closed-reader SIGPIPE "
            "law fails")
    l = legs["x_devfull"]
    if l.get("rc") != 0 or l.get("stderr_bytes") != 0:
        failures.append(
            f"x_devfull: rc={l.get('rc')} stderr={l.get('stderr_bytes')}"
            " — the silent write-error law fails")
