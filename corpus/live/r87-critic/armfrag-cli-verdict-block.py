    # ---------------- verdicts ----------------
    l = legs["cold_nowarm"]
    blob = (l.get("stdout") or "") + (l.get("stderr") or "")
    if f"unknown global '{nid}'" not in blob and \
            "unknown global" not in blob:
        failures.append(
            "cold_nowarm: the cold-registry artifact did not fire "
            f"({blob[-160:]})")
    if legs["warm_control"].get("exit_code") != 0 or \
            "id:" not in (legs["warm_control"].get("stdout") or ""):
        failures.append(
            "warm_control: a warm pw-cli info failed — the artifact "
            "contrast is unmeasured")
    for v, l in legs["unknowns"].items():
        if PWBIND_R87_DEAD not in ((l.get("stderr") or "")
                                   + (l.get("stdout") or "")) \
                or "unknown global" not in ((l.get("stderr") or "")
                                            + (l.get("stdout") or "")):
            failures.append(
                f"unknowns/{v}: the unknown-global class failed "
                f"({l.get('error_class')})")
    if not legs["tap_link"]["edges"]:
        failures.append("tap_link: the monitor tap never validated")
    regs = legs.get("regions") or {}
    solo = (regs.get("solo") or {}).get("median_peak")

    def ratio(name):
        v = (regs.get(name) or {}).get("median_peak")
        return (v / solo) if (v is not None and solo) else None

    if solo is None or not (PWBIND_R87_SOLO_ENV[0] * PWBIND_R87_AMP
                            <= solo <=
                            PWBIND_R87_SOLO_ENV[1] * PWBIND_R87_AMP):
        failures.append(
            f"solo: median_peak={solo} outside the x8192 "
            f"{PWBIND_R87_SOLO_ENV} envelope — the tap reference fails")
    else:
        for name, env in (("vol25", PWBIND_R87_V25_ENV),
                          ("restore", PWBIND_R87_SOLO_ENV),
                          ("unmute", PWBIND_R87_SOLO_ENV)):
            r = ratio(name)
            if r is None or not (env[0] <= r <= env[1]):
                failures.append(
                    f"{name}: ratio={r} outside {env} — the live-DSP "
                    "law fails")
        mv = (regs.get("mute") or {}).get("median_peak")
        if mv is None or mv > PWBIND_R87_MUTE_MAX:
            failures.append(
                f"mute: median_peak={mv} > {PWBIND_R87_MUTE_MAX} — "
                "mute is not live DSP")
        for wn in ("w_v25", "w_v10", "w_mute", "w_unmute"):
            if (legs.get("writes") or {}).get(wn, {}).get(
                    "exit_code") != 0:
                failures.append(
                    f"{wn}: the Props write refused "
                    f"(rc={legs['writes'][wn].get('exit_code')})")
    if legs.get("props_unk") is not None:
        pu = legs["props_unk"]
        if pu.get("exit_code") != 0 or pu.get("errors"):
            failures.append(
                "props_unk: the unknown-key write was not the silent "
                f"drop ({pu.get('errors') or pu.get('error_class')})")
    for scope, key in (("fmt_stream", "post_valid"),
                       ("fmt_stream", "post_empty"),
                       ("fmt_sink", "post_valid")):
        f = legs.get(scope) or {}
        pre = _pwbind_r87_parse_format((f.get("pre") or {})
                                       .get("stdout") or "")
        post = _pwbind_r87_parse_format((f.get(key) or {})
                                        .get("stdout") or "")
        if pre.get("rate") is None or post != pre:
            failures.append(
                f"{scope}: negotiated Format moved {pre} -> {post} "
                "— the seal fails")
    fu = legs.get("fmt_unlinked") or {}
    if fu:
        ef = (fu["enum_fmt"].get("stderr") or "") + \
            (fu["enum_fmt"].get("stdout") or "")
        ep = (fu["enum_props"].get("stderr") or "") + \
            (fu["enum_props"].get("stdout") or "")
        if "res:-2" not in ef:
            failures.append(
                "fmt_unlinked: enum Format did not fail res:-2 "
                f"({ef[-160:]})")
        if "Object:" not in ep or "res:-" in ep:
            failures.append(
                "fmt_unlinked: enum Props did not read on the "
                f"unlinked node ({ep[-160:]})")
    else:
        entry.setdefault("coverage_blocked", []).append(
            "unlinked stream node never published — fmt_unlinked "
            "unmeasured")
    sc = legs.get("sendcmd") or {}
    if (sc.get("Suspend") or {}).get("state_after") != "suspended":
        failures.append(
            "sendcmd/Suspend: state_after="
            f"{(sc.get('Suspend') or {}).get('state_after')}")
    if "unknown node command type: Resume" not in (
            ((sc.get("Resume") or {}).get("cmd") or {})
            .get("stderr") or ""):
        failures.append(
            "sendcmd/Resume: the unknown-command refusal failed")
    st = (sc.get("Start") or {})
    if (st.get("cmd") or {}).get("errors") or \
            st.get("state_after") != "suspended":
        failures.append(
            "sendcmd/Start: not an accepted no-op "
            f"(errors={st.get('cmd', {}).get('errors')} "
            f"state={st.get('state_after')})")
    if (sc.get("Pause") or {}).get("state_after") != "suspended":
        failures.append("sendcmd/Pause: state did not stay suspended")
    for c in ("0", "bogus-cmd"):
        if "unknown node command type" not in (
                ((sc.get(c) or {}).get("cmd") or {})
                .get("stderr") or ""):
            failures.append(
                f"sendcmd/{c}: the unknown-command class failed")
    if not ((sc.get("no_args") or {}).get("cmd") or {}).get("errors"):
        failures.append("sendcmd/no_args: no usage refusal")
    lat = (legs.get("latency") or {}).get("stderr") or ""
    if "res:-95" not in lat:
        failures.append(
            f"latency: the res:-95 class failed ({lat[-160:]})")
    fo = legs.get("foreign") or {}
    if fo:
        allerr = (fo["write_samevalue"].get("errors") or []) + \
            (fo["write_unk"].get("errors") or []) + \
            (fo["enum_pre"].get("errors") or []) + \
            (fo["enum_post"].get("errors") or [])
        if allerr:
            failures.append(
                f"foreign: errors on foreign verbs {allerr} — a gate "
                "appeared")
        if fo.get("volume_read") is not None and \
                fo.get("volume_after") != fo.get("volume_read"):
            failures.append(
                f"foreign: identical-value write moved the volume "
                f"{fo.get('volume_read')} -> {fo.get('volume_after')}")
        bog_err = (fo["write_bogus"].get("stderr") or "") + \
            (fo["write_bogus"].get("stdout") or "")
        if "unknown param type" not in bog_err:
            failures.append(
                "foreign: BogusType did not refuse "
                f"({bog_err[-160:]})")
    ds = legs.get("destroy_stream") or {}
    if ds:
        if ds.get("play_rc") != 1 or "unconnected" not in (
                ds.get("play_err") or ""):
            failures.append(
                f"destroy_stream: rc={ds.get('play_rc')} "
                f"err={ds.get('play_err')} — the unconnected-exit "
                "law fails")
        if ds.get("node_after"):
            failures.append("destroy_stream: node survived destroy")
    cs = legs.get("create_session") or {}
    if not cs.get("present_in_session") or \
            cs.get("present_after_quit"):
        failures.append(
            f"create_session: in={cs.get('present_in_session')} "
            f"after={cs.get('present_after_quit')} — the "
            "session-bound law fails")
    cl = legs.get("create_linger") or {}
    if not cl.get("present_after_quit") or \
            cl.get("present_after_destroy"):
        failures.append(
            f"create_linger: after_quit={cl.get('present_after_quit')} "
            f"after_destroy={cl.get('present_after_destroy')} — the "
            "linger carve-out fails")
    bf = (legs.get("create_badfac") or {})
    if "res:-2" not in (bf.get("log_tail") or ""):
        failures.append(
            f"create_badfac: no async res:-2 refusal "
            f"({(bf.get('log_tail') or '')[-160:]})")
    cu = (legs.get("create_usage") or {})
    if "usage: factory.name=" not in (cu.get("log_tail") or "") and \
            "res:-22" not in (cu.get("log_tail") or ""):
        failures.append(
            f"create_usage: no usage refusal "
            f"({(cu.get('log_tail') or '')[-160:]})")
    dk = legs.get("destroy_sink_module") or {}
    if dk.get("sink_listed_after") is not False or \
            dk.get("node_after"):
        failures.append(
            "destroy_sink_module: the module survived "
            f"(listed={dk.get('sink_listed_after')} "
            f"node={dk.get('node_after')})")
    if legs["vol_tap_link"]["edges"]:
        vm = legs.get("volume_legs") or {}
        base = (vm.get("v100") or {}).get("median_peak")
        if base is None or not (
                PWBIND_R87_SOLO_ENV[0] * PWBIND_R87_AMP
                <= base <= PWBIND_R87_SOLO_ENV[1] * PWBIND_R87_AMP):
            failures.append(
                f"v100: median_peak={base} outside the solo "
                "envelope — the --volume reference fails")
        else:
            for vk, env in (("v050", PWBIND_R87_V50_ENV),
                            ("v150", PWBIND_R87_V150_ENV)):
                r = (vm.get(vk) or {}).get("ratio_vs_v100")
                if r is None or not (env[0] <= r <= env[1]):
                    failures.append(
                        f"{vk}: ratio={r} outside {env} — the "
                        "--volume law fails")
            mv = (vm.get("v000") or {}).get("median_peak")
            if mv is None or mv > PWBIND_R87_V000_MAX:
                failures.append(
                    f"v000: median_peak={mv} > "
                    f"{PWBIND_R87_V000_MAX} -- the unclamped-zero law "
                    "fails")
    else:
        entry.setdefault("coverage_blocked", []).append(
            "--volume monitor tap never linked — vol arms skipped")
    entry["legs"] = legs
    entry["failures"] = failures