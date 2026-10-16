    # ---------------- verdicts ----------------
    for name in ("pt_n1", "pt_n0"):
        l = legs[name]
        frames = _btwit_r88_top_frames(l.get("stdout_raw") or "")
        l["frames"] = [len(f) for f in frames]
        l["status_sets"] = [sorted({r["status"] for r in f})
                            for f in frames]
    l = legs["pt_n1"]
    fr = _btwit_r88_top_frames(l.get("stdout_raw") or "")
    if len(fr) != 1 or not fr[0] or \
            any(r["status"] != "C" for r in fr[0]):
        failures.append(
            f"pt_n1: frames={len(fr)} statuses="
            f"{sorted({r['status'] for f in fr for r in f})} — the "
            "all-CREATING first frame fails")
    l = legs["pt_n3"]
    fr = l.pop("_frames_cache", [])
    if len(fr) < 2:
        entry.setdefault("coverage_blocked", []).append(
            f"pt_n3: {len(fr)} frames in {l.get('attempt')} tries — "
            "the -n advisory emitted no real-state frame")
    else:
        if any(r["status"] != "C" for r in fr[0]):
            failures.append(
                "pt_n3: first frame is not all-CREATING")
        own_row = next((r for r in fr[-1]
                        if r["id"] == int(entry["refs"]["own_id"])),
                       None)
        if own_row is None:
            failures.append(
                "pt_n3: own sink row absent from the last frame")
        elif own_row["status"] == "C":
            failures.append(
                "pt_n3: own row still CREATING in the last frame — "
                "the real-state frame fails")
        elif own_row["status"] not in ("S", "I", "R", "E"):
            failures.append(
                f"pt_n3: own row status {own_row['status']} not a "
                "known state")
        l["last_frame_status_hist"] = sorted(
            {r["status"]: sum(1 for x in fr[-1]
                             if x["status"] == r["status"])
             for r in fr[-1]}.items())
    l = legs["pt_n0"]
    fr = _btwit_r88_top_frames(l.get("stdout_raw") or "")
    if len(fr) != 1:
        failures.append(
            f"pt_n0: {len(fr)} frames — expected exactly one")
    for name in ("pt_nneg", "pt_nabc"):
        l = legs[name]
        fr = _btwit_r88_top_frames(l.get("stdout") or "")
        if not l.get("killed_at_bound") or not fr:
            failures.append(
                f"{name}: killed={l.get('killed_at_bound')} "
                f"frames={len(fr)} — the infinite class fails")
    l = legs["pt_rbogus"]
    if l.get("exit_code") == 0 or \
            l.get("error_class") != "pwtop_connect_down":
        failures.append(
            f"pt_rbogus: rc={l.get('exit_code')} "
            f"class={l.get('error_class')} — the loud remote "
            "refusal fails")
    l = legs["pt_state_idle"]
    if (l.get("top_frames") or 0) < 2:
        entry.setdefault("coverage_blocked", []).append(
            "pt_state_idle: pw-top never emitted a real-state frame "
            f"({l.get('top_frames')} frames) — the top witness is "
            "unmeasured")
    else:
        voc = l.get("vocab") or {}
        if len({voc.get("pactl"), voc.get("dump"), voc.get("cli"),
                voc.get("top")}) != 1 or None in voc.values():
            failures.append(
                f"pt_state_idle: {l} — the four-witness agreement "
                "fails")
    l = legs.get("pt_state_active") or {}
    if not l.get("linked"):
        entry.setdefault("coverage_blocked", []).append(
            "pt_state_active: stream never linked/running — the "
            "RUNNING-side agreement is unmeasured")
    elif (l.get("top_frames") or 0) < 2:
        entry.setdefault("coverage_blocked", []).append(
            "pt_state_active: pw-top never emitted a real-state "
            "frame under load — the top witness is unmeasured")
    elif l.get("vocab"):
        voc = l["vocab"]
        if len(set(voc.values())) != 1 or \
                voc.get("dump") != "running" or None in voc.values():
            failures.append(
                f"pt_state_active: {l} — the RUNNING-side "
                "four-witness agreement fails")
