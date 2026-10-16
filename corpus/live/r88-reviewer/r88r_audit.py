#!/usr/bin/env python3
"""r88 reviewer — independent re-derivation of every armed btwit-r88 law
from receipt data ALONE (no fixture import, no live host access).

Each check mirrors one verdict branch in the committed fixture
(c19bec96:corpus/fixtures/measure_audio.py, sha256 ad9d59b1…, lines
27507-29252).  A check PASS means "the receipt data satisfies the law the
fixture would arm"; the receipt's own `failures` list is then compared
against the set of laws that failed here (for a green receipt the two must
agree: zero).

Usage: r88r_audit.py <measurements.json> [more.json ...]
"""
import json
import re
import sys


def top_frames(text):
    """mirror of _btwit_r88_top_frames"""
    frames, cur = [], None
    for ln in (text or "").splitlines():
        if re.match(r"^S\s+ID\s+QUANT", ln):
            cur = []
            frames.append(cur)
            continue
        m = re.match(r"^([A-Za-z])\s+(\d+)\s", ln)
        if cur is not None and m:
            cur.append({"status": m.group(1), "id": int(m.group(2))})
    return frames


class Audit:
    def __init__(self):
        self.checks = []          # (name, ok, detail)
        self.skips = []           # unmeasurable / not receipt-derivable

    def check(self, name, ok, detail=""):
        self.checks.append((name, bool(ok), detail))
        return bool(ok)

    def skip(self, name, detail):
        self.skips.append((name, detail))


def audit(receipt):
    a = Audit()
    m = receipt.get("measurements") or {}

    a.check("mode", receipt.get("mode") == "probe-btwit-r88",
            f"mode={receipt.get('mode')!r}")
    for e in ("btabs_bluez_r88_probe", "witdiff_dump_r88_probe",
              "pwtop_r88_probe"):
        a.check(f"entry_present::{e}", e in m)

    # ---------------- btabs (28 legs) ----------------
    if "btabs_bluez_r88_probe" in m:
        b = m["btabs_bluez_r88_probe"]
        L = b.get("legs") or {}
        a.check("btabs::leg_count", len(L) == 28, f"{len(L)} legs")

        c = L.get("bz_nullsink_ctl") or {}
        a.check("bz_nullsink_ctl", c.get("rc") == 0
                and c.get("module_id") is not None,
                f"rc={c.get('rc')} module_id={c.get('module_id')}")

        cards = (L.get("bz_cards") or {}).get("cards") or []
        a.check("bz_cards::nonempty", bool(cards), f"{len(cards)} cards")
        bluez_cards = [c["name"] for c in cards
                       if re.search("bluez", str(c.get("name")), re.I)]
        a.check("bz_cards::no_bluez", not bluez_cards, f"{bluez_cards}")

        pl = L.get("bz_pactl_lines") or {}
        mt = pl.get("matches") or []
        a.check("bz_pactl_lines::count", pl.get("count") == 1,
                f"count={pl.get('count')}")
        a.check("bz_pactl_lines::session_services",
                bool(mt) and "session.services" in str(mt[0]),
                f"{str(mt[:1])[:120]}")
        a.check("bz_pactl_lines::bluetooth_audio",
                bool(mt) and "bluetooth.audio" in str(mt[0]),
                f"{str(mt[:1])[:120]}")

        sinks = (L.get("bz_sinks") or {}).get("sinks") or []
        bluez_sinks = [n for n in sinks if re.search("bluez", str(n), re.I)]
        a.check("bz_sinks::no_bluez", not bluez_sinks, f"{bluez_sinks}")

        mb = L.get("bz_midi_bridge") or {}
        bos = mb.get("bluez_objects") or []
        a.check("bz_midi_bridge::nonempty", bool(bos), f"{len(bos)} objs")
        a.check("bz_midi_bridge::all_midi_bridge",
                all(o.get("media_class") == "Midi/Bridge" for o in bos),
                f"{[o.get('media_class') for o in bos]}")

        t = L.get("bz_tree") or {}
        a.check("bz_tree::adapter", bool(t.get("adapters")),
                f"adapters={t.get('adapters')}")

        ad = L.get("bz_adapter") or {}
        a.check("bz_adapter::powered",
                '"b true"' in json.dumps(ad.get("stdout")) or
                re.search(r"^b true$", ad.get("stdout") or "", re.M),
                f"stdout={str(ad.get('stdout'))[:80]}")

        md = L.get("bz_media1") or {}
        uu = md.get("stdout") or ""
        a.check("bz_media1::a2dp_uuids",
                "0000110a-" in uu and "0000110b-" in uu,
                f"uuid_text={uu[:80]}")

        devs = (L.get("bz_device") or {}).get("devices") or []
        a.check("bz_device::no_audio_uuids",
                all(not d.get("audio_uuids") for d in devs),
                f"{[(d.get('path'), d.get('audio_uuids')) for d in devs]}")
        # reviewer-extra (evidence, not the fixture's arm): the HID-only
        # DualSense record must be present with uuid16 {1124,1200}
        if devs:
            d0 = devs[0]
            a.check("bz_device::hid_only_uuid16",
                    sorted(d0.get("uuid16") or []) == ["1124", "1200"],
                    f"uuid16={d0.get('uuid16')} path={d0.get('path')}")
            a.check("bz_device::connected_false",
                    str(d0.get("connected", "")).strip() == "b false",
                    f"connected={d0.get('connected')!r}")
        else:
            a.skip("bz_device::hid_only_uuid16",
                   "no device record in receipt — negative-only arm")

        a.check("bz_media_transport::none",
                not (L.get("bz_media_transport") or {})
                .get("media_transport_objects"),
                f"{(L.get('bz_media_transport') or {}).get('media_transport_objects')}")

        for name in ("bz_loadmod_discover", "bz_loadmod_device",
                     "bz_loadmod_device_path", "bz_loadmod_discover_arg",
                     "bz_setcard"):
            l = L.get(name) or {}
            a.check(f"{name}::pa_module_noent",
                    l.get("exit_code") != 0 and
                    l.get("error_class") == "pa_module_noent",
                    f"rc={l.get('exit_code')} class={l.get('error_class')}")

        l = L.get("bz_sendmsg") or {}
        a.check("bz_sendmsg::pa_sendmsg_noent",
                l.get("exit_code") != 0 and
                l.get("error_class") == "pa_sendmsg_noent",
                f"rc={l.get('exit_code')} class={l.get('error_class')}")

        l = L.get("bz_setcard_bogusctl") or {}
        if l.get("skipped"):
            a.skip("bz_setcard_bogusctl", "skipped in receipt")
        else:
            a.check("bz_setcard_bogusctl::confound",
                    l.get("exit_code") != 0 and
                    l.get("error_class") == "pa_module_noent",
                    f"rc={l.get('exit_code')} class={l.get('error_class')}")

        l = L.get("bz_setcard_validctl") or {}
        if l.get("skipped"):
            a.skip("bz_setcard_validctl", "skipped in receipt")
        else:
            a.check("bz_setcard_validctl::rc0",
                    l.get("exit_code") == 0,
                    f"rc={l.get('exit_code')} profile={l.get('active_profile')}")

        for tag in ("bz_mods_before", "bz_mods_after"):
            l = L.get(tag) or {}
            if l.get("ids") is None:
                a.skip(f"{tag}::ids", "module census unreadable")
            else:
                a.check(f"{tag}::no_bluez_module",
                        not l.get("bluez_modules"),
                        f"{l.get('bluez_modules')}")

        l = L.get("bz_spa_inventory") or {}
        files = l.get("files") or []
        a.check("bz_spa_inventory::count14", l.get("count") == 14,
                f"count={l.get('count')}")
        a.check("bz_spa_inventory::lib_and_codecs",
                "libspa-bluez5.so" in files and
                sum(1 for f in files
                    if str(f).startswith("libspa-codec-bluez5-")) >= 8,
                f"files={files}")

        l = L.get("bz_spa_codecs_str") or {}
        hits = l.get("substring_hits") or []
        a.check("bz_spa_codecs_str::substring_hits",
                any("spa.bluez5.codecs" in h for h in hits) and
                any("is not an array" in h for h in hits),
                f"hits={hits}")
        a.check("bz_spa_codecs_str::no_standalone",
                l.get("standalone_lines") == 0,
                f"standalone={l.get('standalone_lines')}")

        a.check("bz_find_module::none",
                not (L.get("bz_find_module") or {}).get("hits"),
                f"{(L.get('bz_find_module') or {}).get('hits')}")

        want = {"bz_create_a2dpsink": "pwcli_remote_enoent",
                "bz_create_sink": "pwcli_remote_enoent",
                "bz_create_a2dpsource": "pwcli_remote_einval",
                "bz_create_midi": "pwcli_remote_einval"}
        for name, cls in want.items():
            l = L.get(name) or {}
            txt = (l.get("stderr") or "") + (l.get("stdout") or "")
            a.check(f"{name}::refused",
                    l.get("exit_code") == 0 and
                    l.get("error_class") == cls and
                    "can't create node" in txt,
                    f"rc={l.get('exit_code')} class={l.get('error_class')}")
            # reviewer-extra: the res: value named in the task brief
            head = " ".join(l.get("stderr_head") or [])
            want_res = "-2" if "enoent" in cls else "-22"
            a.check(f"{name}::res{want_res}",
                    f"res:{want_res}" in head, f"head={head[:90]}")

        a.check("bz_own_residue::empty", not L.get("bz_own_residue"),
                f"{L.get('bz_own_residue')}")
        a.check("btabs::sinks_gone",
                isinstance(b.get("sinks_gone"), dict) and
                all(b["sinks_gone"].values()),
                f"{b.get('sinks_gone')}")
        a.check("btabs::own_nodes_after_empty",
                b.get("own_nodes_after") == [],
                f"{b.get('own_nodes_after')}")
        a.check("btabs::no_failures_recorded", not b.get("failures"),
                f"{b.get('failures')}")

    # ---------------- witdiff (41 legs) ----------------
    if "witdiff_dump_r88_probe" in m:
        w = m["witdiff_dump_r88_probe"]
        L = w.get("legs") or {}
        refs = w.get("refs") or {}
        own_id = str(refs.get("own_id"))
        own_ser = str(refs.get("own_serial"))
        a.check("witdiff::leg_count", len(L) == 41, f"{len(L)} legs")

        for name in ("wd_setrule_own_id", "wd_setrule_own_serial",
                     "wd_setrule_foreign_id", "wd_setrule_foreign_serial"):
            l = L.get(name)
            if l is None:
                a.skip(name, "leg absent (guard) — set rule unmeasured")
                continue
            a.check(f"{name}::set_rule",
                    l.get("got") is not None and l.get("got") == l.get("predicted"),
                    f"got={l.get('got')} pred={l.get('predicted')}")

        l = L.get("wd_no_nested") or {}
        a.check("wd_no_nested::no_ports", l.get("port_objects") == 0,
                f"port_objects={l.get('port_objects')}")
        members = l.get("members") or []
        for name in ("wd_mode_raw", "wd_mode_indent0"):
            l2 = L.get(name) or {}
            a.check(f"{name}::mode_invariant",
                    bool(members) and l2.get("ids") == [str(members[0])],
                    f"ids={l2.get('ids')} first_member={members[:1]}")

        l = L.get("wd_mode_spa") or {}
        spa = l.get("stdout_raw") or l.get("stdout") or ""
        a.check("wd_mode_spa::id_serial_pair",
                f"id = {own_id}" in spa and
                f"object.serial = {own_ser}" in spa,
                f"own_id={own_id} own_serial={own_ser}")

        l = L.get("wd_cli_id") or {}
        a.check("wd_cli_id::live_node",
                "PipeWire:Interface:Node" in (l.get("stdout") or ""),
                f"rc={l.get('exit_code')}")

        for name in ("wd_cli_serial", "wd_cli_dead", "wd_silent_cli_enum"):
            l = L.get(name) or {}
            a.check(f"{name}::unknown_global_rc0",
                    l.get("exit_code") == 0 and
                    l.get("error_class") == "pwcli_unknown_global" and
                    not (l.get("stdout") or "").strip(),
                    f"rc={l.get('exit_code')} class={l.get('error_class')}")

        l = L.get("wd_ls_serial") or {}
        ls = l.get("stdout_raw") or l.get("stdout") or ""
        a.check("wd_ls_serial::serial_exposed",
                f'object.serial = "{own_ser}"' in ls,
                f"own_serial={own_ser}")

        l = L.get("wd_propblock") or {}
        a.check("wd_propblock::ls_flat_info_star",
                l.get("ls_layout") == "flat" and l.get("info_layout") == "star",
                f"ls={l.get('ls_layout')} info={l.get('info_layout')}")

        l = L.get("wd_keyset_own") or {}
        a.check("wd_keyset_own::keys_equal",
                not l.get("cli_only") and not l.get("dump_only"),
                f"cli_only={l.get('cli_only')} dump_only={l.get('dump_only')}")

        l = L.get("wd_keyset_dev")
        if l is None:
            a.skip("wd_keyset_dev", "no Device object")
        else:
            a.check("wd_keyset_dev::keys_equal",
                    not l.get("cli_only") and not l.get("dump_only"),
                    f"cli_only={l.get('cli_only')} dump_only={l.get('dump_only')}")

        pairs = (L.get("wd_types") or {}).get("pairs") or []
        a.check("wd_types::pairs_present", bool(pairs), f"{len(pairs)} pairs")
        a.check("wd_types::all_stringified",
                bool(pairs) and all(t.get("cli_has") for t in pairs),
                f"bad={[t.get('key') for t in pairs if not t.get('cli_has')]}")

        l = L.get("wd_params_own") or {}
        a.check("wd_params_own::names_equal", l.get("cli") == l.get("dump"),
                f"cli={l.get('cli')} dump={l.get('dump')}")
        de = l.get("dump_empty") or []
        a.check("wd_params_own::empty_visible_both",
                bool(de) and set(de).issubset(set(l.get("cli") or [])),
                f"dump_empty={de}")

        l = L.get("wd_params_port")
        if l is None:
            a.skip("wd_params_port", "no own ports")
        else:
            a.check("wd_params_port::names_equal",
                    l.get("cli") == l.get("dump"),
                    f"cli={l.get('cli')} dump={l.get('dump')}")
            a.check("wd_params_port::dump_empty",
                    bool(l.get("dump_empty")), f"{l.get('dump_empty')}")

        for name in ("wd_silent_dump_id", "wd_silent_dump_abc",
                     "wd_silent_dump_huge"):
            l = L.get(name) or {}
            a.check(f"{name}::silent_rc0",
                    l.get("exit_code") == 0 and
                    not (l.get("stdout") or "").strip() and
                    not (l.get("stderr") or "").strip(),
                    f"rc={l.get('exit_code')}")

        l = L.get("wd_silent_cli_meta") or {}
        if l.get("skipped"):
            a.skip("wd_silent_cli_meta", "skipped")
        else:
            a.check("wd_silent_cli_meta::silent_rc0",
                    l.get("exit_code") == 0 and
                    not (l.get("stdout") or "").strip() and
                    not (l.get("stderr") or "").strip(),
                    f"rc={l.get('exit_code')}")

        l = L.get("wd_dump_empty") or {}
        a.check("wd_dump_empty::full_dump",
                l.get("exit_code") == 0 and bool(l.get("parsed_ids")) and
                (l.get("equals_before") or l.get("equals_after")),
                f"rc={l.get('exit_code')} parsed={bool(l.get('parsed_ids'))} "
                f"before={l.get('equals_before')} after={l.get('equals_after')}")

        l = L.get("wd_dump_two")
        if l is None:
            a.skip("wd_dump_two", "no foreign id")
        else:
            a.check("wd_dump_two::id1_only",
                    l.get("ids") == [own_id], f"ids={l.get('ids')}")

        l = L.get("wd_dump_color") or {}
        a.check("wd_dump_color::ansi_breaks_json",
                l.get("exit_code") == 0 and l.get("has_ansi") and
                not l.get("json_parses"),
                f"rc={l.get('exit_code')} ansi={l.get('has_ansi')} "
                f"parses={l.get('json_parses')}")

        l = L.get("wd_dump_neg") or {}
        a.check("wd_dump_neg::invalid_opt",
                l.get("exit_code") != 0 and
                l.get("error_class") == "pwdump_invalid_opt",
                f"rc={l.get('exit_code')} class={l.get('error_class')}")

        l = L.get("wd_ls_metadata") or {}
        ls_ids = [str(i) for i in (l.get("ls_ids") or [])]
        dump_ids = [str(i) for i in (l.get("dump_ids") or [])]
        a.check("wd_ls_metadata::extra_nonempty", bool(l.get("extra")),
                f"extra={l.get('extra')} ls={ls_ids} dump={dump_ids}")
        a.check("wd_ls_metadata::dump_subset_of_ls",
                set(dump_ids).issubset(set(ls_ids)),
                f"ls={ls_ids} dump={dump_ids}")

        l = L.get("wd_cli_meta_extra") or {}
        if l.get("skipped"):
            a.skip("wd_cli_meta_extra", "skipped")
        else:
            a.check("wd_cli_meta_extra::silent_rc0",
                    l.get("exit_code") == 0 and
                    not (l.get("stdout") or "").strip() and
                    not (l.get("stderr") or "").strip(),
                    f"rc={l.get('exit_code')}")

        l = L.get("wd_info_all") or {}
        a.check("wd_info_all::metadata_omitted",
                not l.get("metadata_described"),
                f"described={l.get('described')} metadata="
                f"{l.get('metadata_described')} dump_count="
                f"{l.get('dump_count')}")

        for name in ("wd_enum_fmt", "wd_enum_num4"):
            l = L.get(name) or {}
            a.check(f"{name}::no_pod_write_only",
                    "Object:" not in (l.get("stdout") or ""),
                    f"outcome={l.get('outcome')} class={l.get('error_class')}")

        p1 = L.get("wd_enum_props") or {}
        p2 = L.get("wd_enum_num2") or {}
        t1 = (p1.get("stdout") or "") + "\n" + (p1.get("stderr") or "")
        t2 = (p2.get("stdout") or "") + "\n" + (p2.get("stderr") or "")
        if "Object:" not in t1:
            a.skip("wd_enum_num2::numeric_equiv_name",
                   "readable param answered nothing (vacuous leg)")
        else:
            a.check("wd_enum_num2::numeric_equiv_name", t1 == t2,
                    "recorded normed stdout/stderr identical"
                    if t1 == t2 else "differ")

        l = L.get("wd_enum_bogus") or {}
        a.check("wd_enum_bogus::unknown_param",
                l.get("exit_code") == 0 and
                l.get("error_class") == "pwcli_unknown_param",
                f"rc={l.get('exit_code')} class={l.get('error_class')}")

        l = L.get("wd_enum_client") or {}
        a.check("wd_enum_client::not_implemented",
                l.get("exit_code") == 0 and
                l.get("error_class") == "cli_enum_notimpl",
                f"rc={l.get('exit_code')} class={l.get('error_class')} "
                f"tried={l.get('tried')}")

        l = L.get("wd_dead_serial") or {}
        if l.get("skipped"):
            a.skip("wd_dead_serial", "skipped")
        else:
            a.check("wd_dead_serial::silent_rc0",
                    l.get("exit_code") == 0 and
                    not (l.get("stdout") or "").strip() and
                    not (l.get("stderr") or "").strip(),
                    f"rc={l.get('exit_code')} serial={l.get('serial')}")

        l = L.get("wd_serial_law") or {}
        a.check("wd_serial_law::no_violations",
                not l.get("violations") and l.get("own_index_follows") and
                bool(l.get("matched")),
                f"violations={l.get('violations')} own="
                f"{l.get('own_index_follows')} matched={len(l.get('matched') or [])}")

        l = L.get("wd_state3") or {}
        voc = l.get("vocab") or {}
        vals = {voc.get("pactl"), voc.get("dump"), voc.get("cli")}
        a.check("wd_state3::vocab_agree",
                len(vals) == 1 and None not in vals,
                f"pactl={l.get('pactl')} dump={l.get('dump')} "
                f"cli={l.get('cli')} vocab={voc}")

        a.check("witdiff::no_failures_recorded", not w.get("failures"),
                f"{w.get('failures')}")

    # ---------------- pwtop (10 legs) ----------------
    if "pwtop_r88_probe" in m:
        p = m["pwtop_r88_probe"]
        L = p.get("legs") or {}
        refs = p.get("refs") or {}
        own_id = refs.get("own_id")
        a.check("pwtop::leg_count", len(L) == 10, f"{len(L)} legs")

        l = L.get("pt_n1") or {}
        fr = top_frames(l.get("stdout_raw") or "")
        a.check("pt_n1::one_frame_all_C",
                len(fr) == 1 and bool(fr[0]) and
                all(r["status"] == "C" for r in fr[0]),
                f"frames={len(fr)} "
                f"statuses={sorted({r['status'] for f in fr for r in f})}")

        l = L.get("pt_n3") or {}
        counts = l.get("frames") or []
        sets = l.get("status_sets") or []
        a.check("pt_n3::multi_frame", len(counts) >= 2,
                f"frames={counts} attempt={l.get('attempt')}")
        a.check("pt_n3::first_all_C", bool(sets) and sets[0] == ["C"],
                f"first={sets[:1]}")
        a.check("pt_n3::last_real_states",
                bool(sets) and any(s != "C" for s in (sets[-1] or [])),
                f"last={sets[-1:]}")
        a.skip("pt_n3::own_row_not_C",
               "raw frame rows not retained in receipt (stdout_raw popped) "
               "— own-row identity re-checked in live replay")

        l = L.get("pt_n0") or {}
        fr = top_frames(l.get("stdout_raw") or "")
        a.check("pt_n0::one_frame", len(fr) == 1, f"frames={len(fr)}")

        for name in ("pt_nneg", "pt_nabc"):
            l = L.get(name) or {}
            fr = top_frames(l.get("stdout") or "")
            a.check(f"{name}::infinite_bound_killed",
                    bool(l.get("killed_at_bound")) and bool(fr),
                    f"killed={l.get('killed_at_bound')} frames={len(fr)}")

        l = L.get("pt_rbogus") or {}
        a.check("pt_rbogus::connect_down",
                l.get("exit_code") != 0 and
                l.get("error_class") == "pwtop_connect_down",
                f"rc={l.get('exit_code')} class={l.get('error_class')}")

        l = L.get("pt_state_idle") or {}
        if (l.get("top_frames") or 0) < 2:
            a.skip("pt_state_idle::four_witness",
                   f"top_frames={l.get('top_frames')} (unmeasured)")
        else:
            voc = l.get("vocab") or {}
            vals = {voc.get("pactl"), voc.get("dump"), voc.get("cli"),
                    voc.get("top")}
            a.check("pt_state_idle::four_witness",
                    len(vals) == 1 and None not in vals,
                    f"pactl={l.get('pactl')} dump={l.get('dump')} "
                    f"cli={l.get('cli')} top={l.get('top')}")

        l = L.get("pt_state_active") or {}
        if not l.get("linked"):
            a.skip("pt_state_active::four_witness", "stream never linked")
        elif (l.get("top_frames") or 0) < 2:
            a.skip("pt_state_active::four_witness",
                   f"top_frames={l.get('top_frames')} (unmeasured)")
        else:
            voc = l.get("vocab") or {}
            a.check("pt_state_active::four_witness_running",
                    len(set(voc.values())) == 1 and
                    voc.get("dump") == "running" and
                    None not in voc.values(),
                    f"vocab={voc}")

        a.check("pwtop::sinks_gone",
                isinstance(p.get("sinks_gone"), dict) and
                all(p["sinks_gone"].values()),
                f"{p.get('sinks_gone')}")
        a.check("pwtop::own_nodes_after_empty",
                p.get("own_nodes_after") == [],
                f"{p.get('own_nodes_after')}")
        a.check("pwtop::no_failures_recorded", not p.get("failures"),
                f"{p.get('failures')}")

    return a


def main():
    out = {}
    for path in sys.argv[1:]:
        receipt = json.load(open(path))
        a = audit(receipt)
        passed = sum(1 for _, ok, _ in a.checks if ok)
        failed = [(n, d) for n, ok, d in a.checks if not ok]
        out[path] = {
            "checks": len(a.checks), "passed": passed,
            "failed": failed, "skips": a.skips,
            "recorded_failures": {
                k: v.get("failures")
                for k, v in (receipt.get("measurements") or {}).items()
                if isinstance(v, dict) and k.endswith("_r88_probe")},
        }
        print(f"== {path}")
        print(f"   checks={len(a.checks)} passed={passed} "
              f"failed={len(failed)} skips={len(a.skips)}")
        for n, d in failed:
            print(f"   FAIL {n}: {d}")
        for n, d in a.skips:
            print(f"   SKIP {n}: {d}")
    with open("corpus/live/r88-reviewer/receipts/audit-summary.json",
              "w") as fh:
        json.dump(out, fh, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
