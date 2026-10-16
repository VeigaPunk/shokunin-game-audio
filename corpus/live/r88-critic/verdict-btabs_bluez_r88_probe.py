    # ---------------- verdicts ----------------
    l = legs["bz_nullsink_ctl"]
    if l.get("rc") != 0 or l.get("module_id") is None:
        failures.append(
            f"bz_nullsink_ctl: rc={l.get('rc')} — the load-module "
            "positive control failed")
    cards = (legs["bz_cards"].get("cards") or [])
    if not cards:
        failures.append("bz_cards: no pulse cards — census broken")
    bluez_cards = [c["name"] for c in cards
                   if re.search("bluez", c["name"], re.I)]
    if bluez_cards:
        failures.append(
            f"bz_cards: bluez card exists {bluez_cards} — the "
            "absent class fails")
    l = legs["bz_pactl_lines"]
    if l["count"] != 1 or not l["matches"] or \
            "session.services" not in l["matches"][0]:
        failures.append(
            f"bz_pactl_lines: {l['count']} bluez-lines {l['matches']}"
            " — expected exactly the session.services advertisement")
    elif "bluetooth.audio" not in l["matches"][0]:
        failures.append(
            "bz_pactl_lines: the one match is not the advertised "
            "bluetooth.audio capability")
    l = legs["bz_sinks"]
    bluez_sinks = [n for n in l["sinks"] if re.search("bluez", n, re.I)]
    if bluez_sinks:
        failures.append(f"bz_sinks: bluez sink exists {bluez_sinks}")
    l = legs["bz_midi_bridge"]
    if not l["bluez_objects"]:
        failures.append(
            "bz_midi_bridge: zero bluez5 objects — the stack-alive "
            "witness (BLE-MIDI bridge) is gone")
    for o in l["bluez_objects"]:
        if o.get("media_class") != "Midi/Bridge":
            failures.append(
                f"bz_midi_bridge: bluez object {o} is not "
                "Midi/Bridge — an audio-class bluez node exists")
    l = legs["bz_tree"]
    if not l["adapters"]:
        failures.append("bz_tree: no hci adapter — stack dead?")
    l = legs.get("bz_adapter") or {}
    if '"b true"' not in json.dumps(l.get("stdout")) and \
            not re.search(r"^b true$", (l.get("stdout") or ""),
                          re.M):
        failures.append(
            f"bz_adapter: Powered != true ({l.get('stdout')}) — "
            "stack-alive fails")
    l = legs.get("bz_media1") or {}
    uu = l.get("stdout") or ""
    if "0000110a-" not in uu or "0000110b-" not in uu:
        failures.append(
            f"bz_media1: A2DP src/sink UUIDs not advertised {uu[:80]}")
    for rec in (legs["bz_device"].get("devices") or []):
        if rec.get("audio_uuids"):
            failures.append(
                f"bz_device: {rec['path']} advertises audio UUIDs "
                f"{rec['audio_uuids']} — it could become a bluez "
                "audio node")
    if legs["bz_media_transport"]["media_transport_objects"]:
        failures.append(
            "bz_media_transport: MediaTransport objects exist "
            f"{legs['bz_media_transport']['media_transport_objects']}")
    for name in ("bz_loadmod_discover", "bz_loadmod_device",
                 "bz_loadmod_device_path", "bz_loadmod_discover_arg",
                 "bz_setcard"):
        l = legs[name]
        if l.get("exit_code") == 0 or \
                l.get("error_class") != "pa_module_noent":
            failures.append(
                f"{name}: rc={l.get('exit_code')} "
                f"class={l.get('error_class')} — the module-miss "
                "refusal class fails")
    l = legs["bz_sendmsg"]
    if l.get("exit_code") == 0 or \
            l.get("error_class") != "pa_sendmsg_noent":
        failures.append(
            f"bz_sendmsg: rc={l.get('exit_code')} "
            f"class={l.get('error_class')}")
    l = legs["bz_setcard_bogusctl"]
    if l.get("skipped"):
        entry.setdefault("coverage_blocked", []).append(
            "bz_setcard_bogusctl: no real card — confound control "
            "unmeasured")
    elif l.get("exit_code") == 0 or \
            l.get("error_class") != "pa_module_noent":
        failures.append(
            "bz_setcard_bogusctl: rc="
            f"{l.get('exit_code')} class={l.get('error_class')} — "
            "the bogus-profile confound did not reproduce")
    l = legs["bz_setcard_validctl"]
    if l.get("skipped"):
        entry.setdefault("coverage_blocked", []).append(
            "bz_setcard_validctl: no real card — valid control "
            "unmeasured")
    elif l.get("exit_code") != 0:
        failures.append(
            "bz_setcard_validctl: rc="
            f"{l.get('exit_code')} — re-setting the current profile "
            "refused")
    for tag in ("bz_mods_before", "bz_mods_after"):
        if legs[tag].get("ids") is None:
            entry.setdefault("coverage_blocked", []).append(
                f"{tag}: module census unreadable")
        elif legs[tag]["bluez_modules"]:
            failures.append(
                f"{tag}: a bluez-named module is loaded "
                f"{legs[tag]['bluez_modules']}")
    l = legs.get("bz_spa_inventory") or {}
    if l.get("count") != 14:
        failures.append(
            f"bz_spa_inventory: {l.get('count')} files — the "
            "boundary's 14-file correction fails")
    elif "libspa-bluez5.so" not in l["files"] or \
            sum(1 for f in l["files"]
                if f.startswith("libspa-codec-bluez5-")) < 8:
        failures.append(
            f"bz_spa_inventory: codec plugins missing {l['files']}")
    l = legs.get("bz_spa_codecs_str") or {}
    hits = l.get("substring_hits") or []
    if not any("spa.bluez5.codecs" in h for h in hits) or \
            not any("is not an array" in h for h in hits):
        failures.append(
            f"bz_spa_codecs_str: bluez5.codecs strings {hits} — "
            "the parsed-property evidence fails")
    if l.get("standalone_lines") != 0:
        failures.append(
            f"bz_spa_codecs_str: standalone line count "
            f"{l.get('standalone_lines')} != 0")
    if legs["bz_find_module"]["hits"]:
        failures.append(
            f"bz_find_module: module-bluez5*.so exists "
            f"{legs['bz_find_module']['hits']}")
    want_res = {"bz_create_a2dpsink": "pwcli_remote_enoent",
                "bz_create_sink": "pwcli_remote_enoent",
                "bz_create_a2dpsource": "pwcli_remote_einval",
                "bz_create_midi": "pwcli_remote_einval"}
    for name, cls in want_res.items():
        l = legs[name]
        if l.get("exit_code") != 0 or l.get("error_class") != cls \
                or "can't create node" not in (
                    (l.get("stderr") or "") + (l.get("stdout") or "")):
            failures.append(
                f"{name}: rc={l.get('exit_code')} "
                f"class={l.get('error_class')} — the fabrication "
                "refusal class fails")
    if legs["bz_own_residue"]:
        failures.append(
            f"bz_own_residue: create-node attempts left objects "
            f"{legs['bz_own_residue']}")
