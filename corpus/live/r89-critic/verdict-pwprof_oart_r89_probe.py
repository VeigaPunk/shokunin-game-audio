    # ---------------- verdicts ----------------
    if not legs["o_link"].get("player"):
        entry.setdefault("coverage_blocked", []).append(
            "seat pw-play never linked — every -o arm below is "
            "contention, not measurement")
    l = legs["o_live"]
    aux_want = {f"Timing{i}.plot" for i in range(1, 6)} | \
        {"Timings.html", "generate_timings.sh"}
    if l.get("exit_code") != 0 or l.get("rows") != 10 or \
            not aux_want.issubset(set(l.get("aux_present") or ())) or \
            "Logging to" not in (l.get("stderr") or "") or \
            "generate_timings" not in (l.get("stdout") or "") + \
                    (l.get("stderr") or ""):
        failures.append(
            f"o_live: rc={l.get('exit_code')} rows={l.get('rows')} "
            f"aux={l.get('aux_present')} — the graceful artifact-set "
            "law fails")
    l = legs["o_int"]
    if l.get("exit_code") != 0 or not (l.get("bytes") or 0) > 0:
        failures.append(
            f"o_int: rc={l.get('exit_code')} bytes={l.get('bytes')} — "
            "the graceful incremental-write law fails")
    l = legs["o_kill"]
    if l.get("exit_code") != -9 or not (l.get("bytes") or 0) > 0 or \
            not (l.get("rows") or 0) > 0:
        failures.append(
            f"o_kill: rc={l.get('exit_code')} bytes={l.get('bytes')} "
            f"rows={l.get('rows')} — the incremental-write law fails "
            "(the scout's 0-byte husk claim is dead on this host)")
    l = legs["o_exist"]
    if l.get("marker_gone") is not True:
        failures.append(
            f"o_exist: marker_gone={l.get('marker_gone')} — the "
            "truncating-open law fails")
    l = legs["o_eager"]
    if l.get("watch_seen") is None:
        failures.append(
            f"o_eager: file never appeared inside the run — the "
            "eager-creation law fails")
    l = legs["o_default"]
    if l.get("exit_code") != 0 or not (l.get("profiler_log") or 0) > 0:
        failures.append(
            f"o_default: rc={l.get('exit_code')} profiler.log="
            f"{l.get('profiler_log')} — the default-name law fails")
    l = legs["o_dash"]
    if l.get("exit_code") != 0 or not (l.get("dash_file") or 0) > 0:
        failures.append(
            f"o_dash: rc={l.get('exit_code')} dash={l.get('dash_file')}"
            " — the literal-filename law fails")
    l = legs["o_devnull"]
    if l.get("exit_code") != 0 or \
            not aux_want.issubset(set(l.get("aux_present") or ())):
        failures.append(
            f"o_devnull: rc={l.get('exit_code')} aux="
            f"{l.get('aux_present')} — the aux-in-cwd law fails")
    for nm in ("o_dir", "o_empty", "o_proc"):
        l = legs[nm]
        if l.get("exit_code") != 255 or \
                l.get("error_class") != "pwprof_cant_open":
            failures.append(
                f"{nm}: rc={l.get('exit_code')} class="
                f"{l.get('error_class')} — the write-error refusal "
                "fails")
