    # ---------------- verdicts ----------------
    for name in ("wd_setrule_own_id", "wd_setrule_own_serial",
                 "wd_setrule_foreign_id", "wd_setrule_foreign_serial"):
        l = legs.get(name)
        if not l:
            continue
        if l.get("got") is None:
            entry.setdefault("coverage_blocked", []).append(
                f"{name}: pw-dump unparsable")
        elif l["got"] != l["predicted"]:
            failures.append(
                f"{name}: pw-dump {l['key']} -> {l['got']} but "
                f"census predicts {l['predicted']} — the "
                "{id∪serial} set-query law fails")
    l = legs["wd_no_nested"]
    if l["port_objects"] != 0:
        failures.append(
            f"wd_no_nested: pw-dump {l['key']} returned "
            f"{l['port_objects']} Port objects — nested expansion "
            "falsified")
    for name in ("wd_mode_raw", "wd_mode_indent0"):
        if legs[name]["ids"] != [str(legs["wd_no_nested"]
                                     ["members"][0])]:
            failures.append(
                f"{name}: mode output {legs[name]['ids']} — "
                "membership not mode-invariant")
    l = legs["wd_mode_spa"]
    _spa_text = l.get("stdout_raw") or l.get("stdout") or ""
    if f"id = {entry['refs']['own_id']}" not in _spa_text or \
            f"object.serial = {entry['refs']['own_serial']}" not in \
            _spa_text:
        failures.append(
            "wd_mode_spa: SPA form lacks the id/serial pair")
    l = legs["wd_cli_id"]
    if "PipeWire:Interface:Node" not in (l.get("stdout") or "") or \
            BTWIT_R88_NS not in (l.get("stdout") or ""):
        failures.append(
            f"wd_cli_id: info on the live own id failed "
            f"(rc={l.get('exit_code')})")
    for name in ("wd_cli_serial", "wd_cli_dead",
                 "wd_silent_cli_enum"):
        l = legs[name]
        if l.get("exit_code") != 0 or \
                l.get("error_class") != "pwcli_unknown_global" or \
                (l.get("stdout") or "").strip():
            failures.append(
                f"{name}: rc={l.get('exit_code')} "
                f"class={l.get('error_class')} — the id-keyed "
                "singleton law fails")
    l = legs["wd_ls_serial"]
    _ls_text = l.get("stdout_raw") or l.get("stdout") or ""
    if f'object.serial = "{entry["refs"]["own_serial"]}"' not in \
            _ls_text:
        failures.append(
            "wd_ls_serial: ls Node does not expose the own serial — "
            "the serial IS resolvable through ls fails")
    l = legs["wd_propblock"]
    if l["ls_layout"] != "flat" or l["info_layout"] != "star":
        failures.append(
            f"wd_propblock: ls={l['ls_layout']} "
            f"info={l['info_layout']} — the two-layout law fails")
    l = legs["wd_keyset_own"]
    if l["cli_only"] or l["dump_only"]:
        failures.append(
            f"wd_keyset_own: prop keys diverge "
            f"cli_only={l['cli_only']} dump_only={l['dump_only']}")
    l = legs.get("wd_keyset_dev")
    if l is None:
        entry.setdefault("coverage_blocked", []).append(
            "wd_keyset_dev: no Device object in census")
    elif l["cli_only"] or l["dump_only"]:
        failures.append(
            f"wd_keyset_dev: prop keys diverge "
            f"cli_only={l['cli_only']} dump_only={l['dump_only']}")
    typed = legs["wd_types"]["pairs"]
    if not typed:
        entry.setdefault("coverage_blocked", []).append(
            "wd_types: no int/bool prop on the own node — "
            "stringification unmeasured")
    else:
        bad = [t for t in typed if not t["cli_has"]]
        if bad:
            failures.append(
                f"wd_types: cli did not stringify "
                f"{[(t['key'], t['dump_type']) for t in bad]}")
    l = legs["wd_params_own"]
    if l["cli"] != l["dump"]:
        failures.append(
            f"wd_params_own: param names diverge "
            f"cli={l['cli']} dump={l['dump']}")
    if not l["dump_empty"] or not set(l["dump_empty"]).issubset(
            set(l["cli"])):
        failures.append(
            f"wd_params_own: no unreadable param appears in both "
            f"lists {l['dump_empty']}")
    l = legs.get("wd_params_port")
    if l is None:
        entry.setdefault("coverage_blocked", []).append(
            "wd_params_port: own sink published no ports")
    else:
        if l["cli"] != l["dump"]:
            failures.append(
                f"wd_params_port: param names diverge "
                f"cli={l['cli']} dump={l['dump']}")
        if not l["dump_empty"]:
            failures.append(
                "wd_params_port: no empty-list params — key presence"
                " ≠ value availability fails")
    for name in ("wd_silent_dump_id", "wd_silent_dump_abc",
                 "wd_silent_dump_huge"):
        l = legs[name]
        if l.get("exit_code") != 0 or \
                (l.get("stdout") or "").strip() or \
                (l.get("stderr") or "").strip():
            failures.append(
                f"{name}: rc={l.get('exit_code')} — the silent-"
                "absence class fails (expected rc 0 + both empty)")
    l = legs["wd_silent_cli_meta"]
    if l.get("skipped"):
        entry.setdefault("coverage_blocked", []).append(
            "wd_silent_cli_meta: no dump-visible metadata")
    elif l.get("exit_code") != 0 or \
            (l.get("stdout") or "").strip() or \
            (l.get("stderr") or "").strip():
        failures.append(
            f"wd_silent_cli_meta: rc={l.get('exit_code')} — the "
            "messageless silent class fails")
    l = legs["wd_dump_empty"]
    if l.get("exit_code") != 0 or not l.get("parsed_ids"):
        failures.append(
            f"wd_dump_empty: rc={l.get('exit_code')} parsed="
            f"{bool(l.get('parsed_ids'))} — '' is not the full dump")
    elif not (l.get("equals_before") or l.get("equals_after")):
        failures.append(
            "wd_dump_empty: object set matches neither bracket "
            "census — '' is not the full dump")
    l = legs.get("wd_dump_two")
    if l and l.get("ids") != [entry["refs"]["own_id"]]:
        failures.append(
            f"wd_dump_two: ids {l.get('ids')} — the two-arg form "
            "does not honor id1 only")
    l = legs["wd_dump_color"]
    if l.get("exit_code") != 0 or not l.get("has_ansi") or \
            l.get("json_parses"):
        failures.append(
            f"wd_dump_color: rc={l.get('exit_code')} ansi="
            f"{l.get('has_ansi')} parses={l.get('json_parses')} — "
            "the ANSI-breaks-JSON class fails")
    l = legs["wd_dump_neg"]
    if l.get("exit_code") == 0 or \
            l.get("error_class") != "pwdump_invalid_opt":
        failures.append(
            f"wd_dump_neg: rc={l.get('exit_code')} "
            f"class={l.get('error_class')}")
    l = legs["wd_ls_metadata"]
    if not l.get("extra") or not set(
            l.get("dump_ids") or []).issubset(
            set(str(i) for i in (l.get("ls_ids") or []))):
        failures.append(
            f"wd_ls_metadata: ls={l.get('ls_ids')} "
            f"dump={l.get('dump_ids')} — the ls⊋dump visibility "
            "split fails")
    l = legs["wd_cli_meta_extra"]
    if l.get("skipped"):
        pass  # the superset arm already carries the claim
    elif l.get("exit_code") != 0 or \
            (l.get("stdout") or "").strip() or \
            (l.get("stderr") or "").strip():
        failures.append(
            "wd_cli_meta_extra: info on an ls-only metadata id was "
            "not silent-rc0")
    l = legs["wd_info_all"]
    if l.get("metadata_described"):
        failures.append(
            f"wd_info_all: info all describes Metadata objects "
            f"{l['metadata_described']} — the silent-omission "
            "class fails")
    for name in ("wd_enum_fmt", "wd_enum_num4"):
        l = legs[name]
        l["has_pod"] = "Object:" in (l.get("stdout") or "")
        l["outcome"] = ("pod" if l["has_pod"]
                        else ("silent" if l.get("error_class") is None
                              else l["error_class"]))
        if l["has_pod"]:
            failures.append(
                f"{name}: a write-only param returned a pod on the "
                "suspended own sink — the write-only signature fails")
    p1, p2 = legs["wd_enum_props"], legs["wd_enum_num2"]
    t1 = ((p1.get("stdout") or "") + "\n" + (p1.get("stderr") or ""))
    t2 = ((p2.get("stdout") or "") + "\n" + (p2.get("stderr") or ""))
    if not t1.strip() or "Object:" not in t1:
        entry.setdefault("coverage_blocked", []).append(
            "wd_enum_props: the readable param answered nothing — "
            "the ≡ leg was vacuous")
    elif _btwit_r88_norm(t1) != _btwit_r88_norm(t2):
        failures.append(
            "wd_enum_num2: `enum-params <id> 2` differs from "
            "`enum-params <id> Props` — the numeric≡name law fails")
    l = legs["wd_enum_bogus"]
    if l.get("exit_code") != 0 or \
            l.get("error_class") != "pwcli_unknown_param":
        failures.append(
            f"wd_enum_bogus: rc={l.get('exit_code')} "
            f"class={l.get('error_class')}")
    l = legs["wd_enum_client"]
    if l.get("exit_code") != 0 or \
            l.get("error_class") != "cli_enum_notimpl":
        entry.setdefault("coverage_blocked", []).append(
            "wd_enum_client: no client returned the "
            "not-implemented class "
            f"(last class={l.get('error_class')})")
    l = legs["wd_dead_serial"]
    if l.get("skipped"):
        entry.setdefault("coverage_blocked", []).append(
            "wd_dead_serial: ns2 serial never resolved")
    elif l.get("exit_code") != 0 or \
            (l.get("stdout") or "").strip() or \
            (l.get("stderr") or "").strip():
        failures.append(
            f"wd_dead_serial: rc={l.get('exit_code')} — the "
            "dead-serial silent-absence class fails")
    l = legs["wd_serial_law"]
    if l["violations"] or not l["own_index_follows"]:
        failures.append(
            f"wd_serial_law: violations={l['violations']} "
            f"own={l['own_index_follows']} — pactl index ≠ "
            "object.serial")
    if not l["matched"]:
        entry.setdefault("coverage_blocked", []).append(
            "wd_serial_law: zero sinks matched both witnesses "
            "(churn)")
    l = legs["wd_state3"]
    voc = l.get("vocab") or {}
    if len({voc.get("pactl"), voc.get("dump"), voc.get("cli")}) != 1 \
            or None in (voc.get("pactl"), voc.get("dump"),
                        voc.get("cli")):
        failures.append(
            f"wd_state3: pactl={l.get('pactl')} dump="
            f"{l.get('dump')} cli={l.get('cli')} — the tight-window "
            "vocab agreement fails")
