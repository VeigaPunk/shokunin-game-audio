    # ---------------- verdicts ----------------
    if not legs["g_link"].get("player"):
        entry.setdefault("coverage_blocked", []).append(
            "seat pw-play never linked — every -n arm below is "
            "contention, not measurement")
    l = legs["g_own"]
    if l.get("exit_code") != 0 or not l.get("term_ok") or \
            l.get("n_info") != 8:
        failures.append(
            f"g_own: rc={l.get('exit_code')} term={l.get('term_ok')} "
            f"n_info={l.get('n_info')} drivers={l.get('drivers')} — "
            "the exact-N completion fails")
    l = legs["g_two"]
    if l.get("exit_code") != 0 or l.get("n_info") != 4 or \
            not l.get("term_ok") or (l.get("wall_s") or 9) > 1.5:
        failures.append(
            f"g_two: rc={l.get('exit_code')} n_info={l.get('n_info')} "
            f"wall={l.get('wall_s')} hist={l.get('driver_info_hist')}"
            " — the multi-driver summed-N completion fails")
    for nm, sig_ok in (("g_term", 0), ("g_int", 0)):
        l = legs[nm]
        if l.get("exit_code") != sig_ok or not l.get("term_ok"):
            failures.append(
                f"{nm}: rc={l.get('exit_code')} term={l.get('term_ok')}"
                f" — the graceful-class flush fails")
    for nm, want_sig in (("g_kill", -9), ("g_hup", -1),
                         ("g_usr1", -10)):
        l = legs[nm]
        if l.get("exit_code") != want_sig or l.get("parse_error") is None:
            failures.append(
                f"{nm}: rc={l.get('exit_code')} parse="
                f"{l.get('parse_error')} — the truncating-signal "
                "class fails")
    l = legs["g_blocks"]
    samples = l.get("stream_samples") or []
    nonzero = [s for s in samples if s.get("bytes")]
    if not nonzero or any(s["bytes"] % 4096 for s in nonzero):
        failures.append(
            f"g_blocks: {samples} — the exact-4096 stream-block law "
            "fails")
    l = legs["g_o_ignored"]
    if l.get("file_created") or "Logging to" in (l.get("stderr") or ""):
        failures.append(
            f"g_o_ignored: created={l.get('file_created')} stderr="
            f"{l.get('stderr')} — -o is NOT ignored under -J")
    l = legs["g_extra"]
    if l.get("exit_code") != 0 or l.get("n_info") != 4:
        failures.append(
            f"g_extra: rc={l.get('exit_code')} n_info={l.get('n_info')}"
            " — the stray positional is not ignored")
    l = legs["g_remote_empty"]
    if l.get("exit_code") != 0 or l.get("n_info") != 4:
        failures.append(
            f"g_remote_empty: rc={l.get('exit_code')} "
            f"n_info={l.get('n_info')} — -r '' is not the default "
            "remote")
    for nm in ("g_remote_bogus", "g_env_bogus"):
        l = legs[nm]
        if l.get("exit_code") != 255 or \
                l.get("error_class") != "pwprof_connect_down":
            failures.append(
                f"{nm}: rc={l.get('exit_code')} class="
                f"{l.get('error_class')} — the rc-255 remote refusal "
                "fails")
    l = legs["g_opt_bogus"]
    if l.get("exit_code") != 255 or l.get("error_class") != "pwprof_opt":
        failures.append(
            f"g_opt_bogus: rc={l.get('exit_code')} class="
            f"{l.get('error_class')} — the option refusal fails")
    l = legs["g_version"]
    if l.get("exit_code") != 0 or \
            "libpipewire" not in (l.get("stdout") or ""):
        failures.append(
            f"g_version: rc={l.get('exit_code')} — the version leg "
            "fails")
    l = legs["g_lastwins"]
    if l.get("alive_at_sig") is not True or l.get("exit_code") != 0 \
            or (l.get("n_info") or 0) < 5:
        failures.append(
            f"g_lastwins: alive={l.get('alive_at_sig')} rc="
            f"{l.get('exit_code')} infos={l.get('n_info')} — "
            "last-wins unbounded fails")
    for nm, want in (("n_007", 7), ("n_plus3", 3), ("n_space3", 3)):
        l = legs[nm]
        if l.get("exit_code") != 0 or l.get("n_info") != want or \
                l.get("alive_at_sig") is True:
            failures.append(
                f"{nm}: rc={l.get('exit_code')} n_info="
                f"{l.get('n_info')} alive={l.get('alive_at_sig')} — "
                f"the strtol-parse-to-{want} leg fails")
    for nm in ("n_2_5", "n_3abc", "n_1e1", "n_huge", "n_neg",
               "n_abc", "n_zero"):
        l = legs[nm]
        if l.get("alive_at_sig") is not True or \
                l.get("exit_code") != 0 or \
                (l.get("n_info") or 0) < 5:
            failures.append(
                f"{nm}: alive={l.get('alive_at_sig')} rc="
                f"{l.get('exit_code')} infos={l.get('n_info')} — "
                "the unbounded-parse leg fails (cycles flowed, the "
                "run never stopped)")
