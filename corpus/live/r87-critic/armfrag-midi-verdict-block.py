    # ---------------- verdicts ----------------
    for name in ("m_t_bridge", "m_t_serial", "m_t_objid",
                 "m_t_garbage", "m_t_prop", "m_t_nt"):
        l = legs.get(name)
        if l is None:
            continue
        blob = (l.get("stderr") or "") + (l.get("stdout") or "")
        if l.get("exit_code") == 0 or \
                "no target node available" not in blob or \
                "res:-2" not in blob:
            failures.append(
                f"{name}: rc={l.get('exit_code')} — the target-dead "
                f"law fails ({blob[-160:]})")
    for name in ("m_t_zero", "m_noauto"):
        leg = legs[name]
        snap = _pwbind_r87_last_snap(leg)
        got = _pwbind_r87_consumers(leg)
        if not snap.get("present") or got or \
                snap.get("media_class") != "Stream/Output/Midi":
            failures.append(
                f"{name}: present={snap.get('present')} "
                f"class={snap.get('media_class')} links={got} — the "
                "publish-unlinked arm fails")
    pin = legs["pin"]
    if pin.get("file"):
        f = pin["file"]
        pl = pin.get("pwlink") or {}
        if pl.get("exit_code") != 0:
            failures.append(
                f"pin: pw-link refused rc={pl.get('exit_code')}")
        if not f.get("has_mthd") or (f.get("bytes") or 0) < 40 or \
                not all(f.get("note_ons") or []) or \
                not any(f.get("note_offs") or []):
            failures.append(
                f"pin: the pinned capture lacks the injected events "
                f"{f} — the pin-carries law fails")
    else:
        entry.setdefault("coverage_blocked", []).append(
            "midi pin leg unmeasured — bridge capture port or seq "
            "14:0 absent")
    sk = legs["skeleton"]["file"]
    if legs["skeleton"].get("rc") == 0 or not sk.get("has_mthd") \
            or not (20 <= (sk.get("bytes") or 0) <= 34) \
            or any(sk.get("note_ons") or []):
        failures.append(
            f"skeleton: refused midirecord wrote {sk} rc="
            f"{legs['skeleton'].get('rc')}")
    md = legs["mdump_off"]
    if md.get("exit_code") != 0 or "Note On" not in (
            md.get("stdout") or ""):
        failures.append(
            f"mdump_off: rc={md.get('exit_code')} — the offline "
            "parse failed")
    live = legs["mdump_live"]["attempts"]
    noted = [a for a in live if a.get("node")]
    if live and not noted:
        entry.setdefault("coverage_blocked", []).append(
            "pw-mididump never published a node in 3 attempts — the "
            "boundary's startup flake (live dump unmeasured)")
    elif noted and not any("Note On" in (a.get("stdout") or "")
                           for a in noted):
        failures.append(
            "mdump_live: a live node published and pinned but no "
            "Note On/Off lines arrived")
    for name in ("pactl_raop", "pactl_zc", "pactl_bogus"):
        l = legs[name]
        if l.get("exit_code") == 0 or \
                "Failure: No such entity" not in (
                    (l.get("stderr") or "") + (l.get("stdout") or "")):
            failures.append(
                f"{name}: rc={l.get('exit_code')} — the uniform "
                "module-miss class fails")
    for name in ("pwcli_raop", "pwcli_zc", "pwcli_null",
                 "pwcli_panull"):
        l = legs[name]
        if "Could not load module" not in (
                (l.get("stderr") or "") + (l.get("stdout") or "")):
            failures.append(
                f"{name}: the pw-cli module-miss class failed")
    for name in ("remote_flag", "remote_env"):
        l = legs[name]
        if l.get("exit_code") == 0 or "Host is down" not in (
                (l.get("stderr") or "") + (l.get("stdout") or "")):
            failures.append(
                f"{name}: rc={l.get('exit_code')} — the host-down "
                "class fails")
    l = legs["remote_cli"]
    if l.get("exit_code") == 0 or "Host is down" not in (
            (l.get("stderr") or "") + (l.get("stdout") or "")):
        failures.append(
            f"remote_cli: rc={l.get('exit_code')} — the -r refusal "
            "failed")
    cen = legs["remote_census"]
    if cen["remote_named_nodes"]:
        failures.append(
            f"remote_census: remote-classed nodes exist "
            f"{cen['remote_named_nodes']}")
    if cen["net_modules"]:
        failures.append(
            f"remote_census: raop/zeroconf modules on disk "
            f"{cen['net_modules']}")
    entry["legs"] = legs
    entry["failures"] = failures