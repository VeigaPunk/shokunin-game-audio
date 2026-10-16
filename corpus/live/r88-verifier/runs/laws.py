#!/usr/bin/env python3
"""r88-verifier independent law re-derivation.

No fixture import: every law is re-derived from the raw receipt JSON of a
--probe-btwit-r88 run (author receipts + this seat's replays).  Usage:
    python3 laws.py receipt.json [receipt.json ...]
"""
import json
import re
import sys


def norm(s):
    s = re.sub(r"id:\d+ seq:\d+", "id:<n> seq:<n>", s or "")
    s = re.sub(r"object \d+", "object <n>", s)
    return s


def legs(entry, name):
    return (entry.get("legs") or {}).get(name) or {}


def text(l):
    return (l.get("stdout") or "") + "\n" + (l.get("stderr") or "")


def raw(l):
    return (l.get("stdout_raw") or l.get("stdout") or "") + "\n" + \
           (l.get("stderr_raw") or l.get("stderr") or "")


def top_frames(t):
    frames, cur = [], None
    for ln in (t or "").splitlines():
        if re.match(r"^S\s+ID\s+QUANT", ln):
            cur = []
            frames.append(cur)
            continue
        m = re.match(r"^([A-Za-z])\s+(\d+)\s", ln)
        if cur is not None and m:
            cur.append({"status": m.group(1), "id": int(m.group(2))})
    return frames


def laws(receipt):
    m = receipt["measurements"]
    out = []  # (name, ok, detail)
    for ent in ("btabs_bluez_r88_probe", "witdiff_dump_r88_probe",
                "pwtop_r88_probe"):
        if ent not in m:
            out.append((f"{ent[:6]}.PRESENT", False, "entry absent"))
    if any(e not in m for e in ("btabs_bluez_r88_probe",
                                "witdiff_dump_r88_probe",
                                "pwtop_r88_probe")):
        return out

    b = m["btabs_bluez_r88_probe"]
    w = m["witdiff_dump_r88_probe"]
    p = m["pwtop_r88_probe"]

    # ---------------- btabs: absent class ----------------
    l = legs(b, "bz_nullsink_ctl")
    out.append(("bz.ctl", l.get("rc") == 0 and l.get("module_id")
                is not None and l.get("sink_seen") is True
                and l.get("monitor_seen") is True, str(l)))
    cards = legs(b, "bz_cards").get("cards") or []
    out.append(("bz.cards", bool(cards) and not any(
        re.search("bluez", c.get("name", ""), re.I) for c in cards),
        f"{len(cards)} cards"))
    pl = legs(b, "bz_pactl_lines")
    out.append(("bz.pactl_ad", pl.get("count") == 1 and bool(pl.get("matches"))
                and "session.services" in pl["matches"][0]
                and "bluetooth.audio" in pl["matches"][0],
                str(pl.get("matches"))[:110]))
    sk = legs(b, "bz_sinks").get("sinks") or []
    out.append(("bz.sinks", bool(sk) and not any(
        re.search("bluez", s, re.I) for s in sk), f"{len(sk)} sinks"))
    bo = legs(b, "bz_midi_bridge").get("bluez_objects") or []
    out.append(("bz.midi_bridge", bool(bo) and all(
        o.get("media_class") == "Midi/Bridge" for o in bo), str(bo)))
    tr = legs(b, "bz_tree")
    out.append(("bz.adapter", bool(tr.get("adapters")) and
                "b true" in (legs(b, "bz_adapter").get("stdout") or ""),
                str(tr.get("adapters"))))
    out.append(("bz.media1_a2dp",
                "0000110a-" in (legs(b, "bz_media1").get("stdout") or "")
                and "0000110b-" in
                (legs(b, "bz_media1").get("stdout") or ""),
                (legs(b, "bz_media1").get("stdout") or "")[:80]))
    devs = legs(b, "bz_device").get("devices") or []
    out.append(("bz.device_hid", bool(devs) and all(
        d.get("audio_uuids") == [] for d in devs) and all(
        "1124" in (d.get("uuid16") or []) for d in devs),
        str([d.get("uuid16") for d in devs])))
    out.append(("bz.no_media_transport",
                legs(b, "bz_media_transport").get(
                    "media_transport_objects") == [],
                str(legs(b, "bz_media_transport"))))
    refusals = ["bz_loadmod_discover", "bz_loadmod_device",
                "bz_loadmod_device_path", "bz_loadmod_discover_arg",
                "bz_setcard"]
    ok = all(legs(b, n).get("exit_code") != 0 and
             legs(b, n).get("error_class") == "pa_module_noent"
             for n in refusals)
    out.append(("bz.module_refusals", ok,
                str({n: (legs(b, n).get("exit_code"),
                         legs(b, n).get("error_class")) for n in refusals})))
    sg = legs(b, "bz_sendmsg")
    out.append(("bz.sendmsg", sg.get("exit_code") != 0 and
                sg.get("error_class") == "pa_sendmsg_noent",
                f"rc={sg.get('exit_code')} {sg.get('error_class')}"))
    # the V3 confound: identical refusal text on a real card + bogus profile
    bctl = legs(b, "bz_setcard_bogusctl")
    sc = legs(b, "bz_setcard")
    out.append(("bz.confound_text",
                bctl.get("exit_code") != 0 and
                bctl.get("error_class") == "pa_module_noent" and
                norm(sc.get("stderr")) == norm(bctl.get("stderr")),
                f"setcard={sc.get('stderr')!r} bogus={bctl.get('stderr')!r}"))
    vctl = legs(b, "bz_setcard_validctl")
    out.append(("bz.validctl", vctl.get("exit_code") == 0,
                f"rc={vctl.get('exit_code')}"))
    mb, ma = legs(b, "bz_mods_before"), legs(b, "bz_mods_after")
    out.append(("bz.module_census",
                mb.get("ids") == ma.get("ids") and not mb.get("bluez_modules")
                and not ma.get("bluez_modules"),
                f"{len(mb.get('ids') or [])} ids"))
    spa = legs(b, "bz_spa_inventory")
    files = spa.get("files") or []
    out.append(("bz.spa14", spa.get("count") == 14 and
                "libspa-bluez5.so" in files and sum(
                    1 for f in files
                    if f.startswith("libspa-codec-bluez5-")) >= 8,
                f"count={spa.get('count')}"))
    cs = legs(b, "bz_spa_codecs_str")
    hits = cs.get("substring_hits") or []
    out.append(("bz.codecs_strings",
                any("spa.bluez5.codecs" in h for h in hits) and
                any("is not an array" in h for h in hits) and
                cs.get("standalone_lines") == 0, str(hits)))
    out.append(("bz.find_module", legs(b, "bz_find_module").get("hits") == [],
                str(legs(b, "bz_find_module").get("hits"))))
    want = {"bz_create_a2dpsink": "res:-2", "bz_create_sink": "res:-2",
            "bz_create_a2dpsource": "res:-22", "bz_create_midi": "res:-22"}
    ok, det = True, {}
    for name, token in want.items():
        l = legs(b, name)
        good = (l.get("exit_code") == 0 and
                "can't create node" in text(l) and token in
                (l.get("stderr") or "") and
                l.get("error_class") == ("pwcli_remote_enoent"
                                         if token == "res:-2"
                                         else "pwcli_remote_einval"))
        ok = ok and good
        det[name] = (l.get("exit_code"), l.get("error_class"),
                     token in (l.get("stderr") or ""))
    out.append(("bz.create_refused", ok, str(det)))
    residue = (b.get("legs") or {}).get("bz_own_residue")
    out.append(("bz.residue", residue == [], str(residue)))

    # ---------------- witdiff ----------------
    refs = w.get("refs") or {}
    own_id, own_ser = str(refs.get("own_id")), str(refs.get("own_serial"))
    sr = [legs(w, n) for n in ("wd_setrule_own_id", "wd_setrule_own_serial",
                               "wd_setrule_foreign_id",
                               "wd_setrule_foreign_serial")]
    out.append(("wd.setrule", all(x.get("got") == x.get("predicted")
                                  for x in sr) and
                legs(w, "wd_setrule_own_id").get("got") == [own_id],
                str([(x.get("key"), x.get("got"), x.get("predicted"))
                     for x in sr])[:220]))
    nn = legs(w, "wd_no_nested")
    out.append(("wd.no_nested", nn.get("port_objects") == 0 and
                [str(i) for i in (nn.get("members") or [])] == [own_id],
                str(nn)[:120]))
    out.append(("wd.mode_invariance",
                legs(w, "wd_mode_raw").get("ids") == [own_id] and
                legs(w, "wd_mode_indent0").get("ids") == [own_id],
                f"raw={legs(w, 'wd_mode_raw').get('ids')} "
                f"i0={legs(w, 'wd_mode_indent0').get('ids')}"))
    spa_txt = raw(legs(w, "wd_mode_spa"))
    out.append(("wd.spa_form", f"id = {own_id}" in spa_txt and
                f"object.serial = {own_ser}" in spa_txt, spa_txt[:120]))
    cli_id = legs(w, "wd_cli_id")
    out.append(("wd.cli_id_keyed",
                "PipeWire:Interface:Node" in (cli_id.get("stdout") or "") and
                "r88a_ns" in (cli_id.get("stdout") or ""), ""))
    bad = []
    for n in ("wd_cli_serial", "wd_cli_dead", "wd_silent_cli_enum"):
        l = legs(w, n)
        if l.get("exit_code") != 0 or \
                l.get("error_class") != "pwcli_unknown_global" or \
                (l.get("stdout") or "").strip():
            bad.append(n)
    out.append(("wd.cli_singleton", not bad, str(bad)))
    out.append(("wd.ls_serial",
                f'object.serial = "{own_ser}"' in raw(legs(w, "wd_ls_serial")),
                ""))
    pb = legs(w, "wd_propblock")
    out.append(("wd.two_layouts", pb.get("ls_layout") == "flat" and
                pb.get("info_layout") == "star", str(pb)))
    ks, kd = legs(w, "wd_keyset_own"), legs(w, "wd_keyset_dev")
    out.append(("wd.keysets",
                not ks.get("cli_only") and not ks.get("dump_only") and
                not kd.get("cli_only") and not kd.get("dump_only") and
                ks.get("cli") == ks.get("dump") and
                kd.get("cli") == kd.get("dump"),
                f"own={len(ks.get('cli') or [])} dev={len(kd.get('cli') or [])}"))
    pairs = legs(w, "wd_types").get("pairs") or []
    out.append(("wd.types_stringified", bool(pairs) and all(
        p.get("cli_has") for p in pairs), f"{len(pairs)} typed pairs"))
    po = legs(w, "wd_params_own")
    out.append(("wd.params_own",
                po.get("cli") == po.get("dump") and bool(po.get("dump_empty"))
                and set(po.get("dump_empty") or []).issubset(
                    set(po.get("cli") or [])), str(po)[:140]))
    pp = legs(w, "wd_params_port")
    out.append(("wd.params_port",
                pp.get("cli") == pp.get("dump") and bool(pp.get("dump_empty")),
                str(pp)[:140]))
    bad = [n for n in ("wd_silent_dump_id", "wd_silent_dump_abc",
                       "wd_silent_dump_huge")
           if legs(w, n).get("exit_code") != 0 or
           (legs(w, n).get("stdout") or "").strip() or
           (legs(w, n).get("stderr") or "").strip()]
    out.append(("wd.silent_dump", not bad, str(bad)))
    scm = legs(w, "wd_silent_cli_meta")
    out.append(("wd.silent_cli_meta",
                scm.get("exit_code") == 0 and
                not (scm.get("stdout") or "").strip() and
                not (scm.get("stderr") or "").strip(),
                str(scm.get("exit_code"))))
    de = legs(w, "wd_dump_empty")
    out.append(("wd.dump_empty_full",
                de.get("exit_code") == 0 and bool(de.get("parsed_ids")) and
                (de.get("equals_before") or de.get("equals_after")),
                f"ids={len(de.get('parsed_ids') or [])} "
                f"before={de.get('equals_before')} "
                f"after={de.get('equals_after')}"))
    dt = legs(w, "wd_dump_two")
    out.append(("wd.dump_two", dt.get("ids") == [own_id],
                f"{dt.get('ids')} vs [{own_id}]"))
    dc = legs(w, "wd_dump_color")
    out.append(("wd.color_breaks_json",
                dc.get("exit_code") == 0 and dc.get("has_ansi") is True and
                dc.get("json_parses") is False, str(dc)[:120]))
    dn = legs(w, "wd_dump_neg")
    out.append(("wd.dump_neg", dn.get("exit_code") != 0 and
                dn.get("error_class") == "pwdump_invalid_opt",
                f"rc={dn.get('exit_code')} {dn.get('error_class')}"))
    lm = legs(w, "wd_ls_metadata")
    ls_ids = [str(i) for i in (lm.get("ls_ids") or [])]
    dp_ids = [str(i) for i in (lm.get("dump_ids") or [])]
    out.append(("wd.ls_superset_dump",
                bool(lm.get("extra")) and bool(dp_ids) and
                set(dp_ids).issubset(set(ls_ids)) and
                len(ls_ids) > len(dp_ids),
                f"ls={len(ls_ids)} dump={len(dp_ids)} extra={lm.get('extra')}"))
    cme = legs(w, "wd_cli_meta_extra")
    out.append(("wd.cli_meta_extra_silent",
                cme.get("exit_code") == 0 and
                not (cme.get("stdout") or "").strip() and
                not (cme.get("stderr") or "").strip(),
                f"rc={cme.get('exit_code')}"))
    ia = legs(w, "wd_info_all")
    out.append(("wd.info_all_omits_meta",
                ia.get("metadata_described") == [] and
                ia.get("described") and ia.get("dump_count") and
                ia["described"] < ia["dump_count"],
                f"described={ia.get('described')} "
                f"dump={ia.get('dump_count')} "
                f"meta={ia.get('metadata_described')}"))
    out.append(("wd.enum_write_only",
                legs(w, "wd_enum_fmt").get("has_pod") is False and
                legs(w, "wd_enum_num4").get("has_pod") is False,
                f"fmt={legs(w, 'wd_enum_fmt').get('outcome')} "
                f"num4={legs(w, 'wd_enum_num4').get('outcome')}"))
    p1 = norm(text(legs(w, "wd_enum_props")))
    p2 = norm(text(legs(w, "wd_enum_num2")))
    out.append(("wd.enum_name_eq_number",
                bool(p1.strip()) and p1 == p2, f"equal={p1 == p2}"))
    eb = legs(w, "wd_enum_bogus")
    out.append(("wd.enum_bogus", eb.get("exit_code") == 0 and
                eb.get("error_class") == "pwcli_unknown_param",
                f"rc={eb.get('exit_code')} {eb.get('error_class')}"))
    ec = legs(w, "wd_enum_client")
    out.append(("wd.enum_client_notimpl",
                ec.get("exit_code") == 0 and
                ec.get("error_class") == "cli_enum_notimpl",
                f"rc={ec.get('exit_code')} {ec.get('error_class')} "
                f"tried={len(ec.get('tried') or [])}"))
    ds = legs(w, "wd_dead_serial")
    out.append(("wd.dead_serial_silent",
                ds.get("exit_code") == 0 and
                not (ds.get("stdout") or "").strip() and
                not (ds.get("stderr") or "").strip(),
                f"serial={ds.get('serial')}"))
    sl = legs(w, "wd_serial_law")
    out.append(("wd.pactl_index_is_serial",
                not sl.get("violations") and sl.get("own_index_follows")
                is True and bool(sl.get("matched")),
                f"matched={len(sl.get('matched') or [])} "
                f"unmatched={len(sl.get('unmatched') or [])} "
                f"viol={len(sl.get('violations') or [])}"))
    s3 = legs(w, "wd_state3")
    voc = s3.get("vocab") or {}
    out.append(("wd.state3_agreement",
                len(set(voc.values())) == 1 and None not in voc.values(),
                str(voc)))

    # ---------------- pwtop ----------------
    l = legs(p, "pt_n1")
    fr = top_frames(l.get("stdout_raw") or "")
    out.append(("pt.n1_all_creating", len(fr) == 1 and bool(fr[0]) and all(
        r["status"] == "C" for r in fr[0]),
        f"frames={len(fr)} statuses={sorted({r['status'] for f in fr for r in f})}"))
    l3 = legs(p, "pt_n3")
    # the in-run frame cache is not recorded; re-derive from the recorded
    # frame counts / status sets / last-frame histogram
    counts = l3.get("frames") or []
    ssets = l3.get("status_sets") or []
    hist = l3.get("last_frame_status_hist") or []
    hist = dict(hist) if isinstance(hist, list) else hist
    out.append(("pt.n3_last_frame_real",
                len(counts) >= 2 and bool(ssets) and
                ssets[0] == ["C"] and
                bool(set(hist) - {"C"}) and l3.get("attempt", 0) >= 1,
                f"counts={counts} status_sets={ssets} hist={hist} "
                f"attempt={l3.get('attempt')}"))
    l0 = legs(p, "pt_n0")
    out.append(("pt.n0_one_frame",
                len(top_frames(l0.get("stdout_raw") or "")) == 1,
                str(l0.get("frames"))))
    ok, det = True, {}
    for n in ("pt_nneg", "pt_nabc"):
        l = legs(p, n)
        nfr = len(top_frames(l.get("stdout") or ""))
        det[n] = (l.get("killed_at_bound"), nfr)
        ok = ok and l.get("killed_at_bound") is True and nfr >= 1
    out.append(("pt.infinite_bound", ok, str(det)))
    rb = legs(p, "pt_rbogus")
    out.append(("pt.rbogus_loud", rb.get("exit_code") != 0 and
                rb.get("error_class") == "pwtop_connect_down",
                f"rc={rb.get('exit_code')} {rb.get('error_class')}"))
    si = legs(p, "pt_state_idle")
    voc = si.get("vocab") or {}
    out.append(("pt.state_idle",
                (si.get("top_frames") or 0) >= 2 and
                len(set(voc.values())) == 1 and None not in voc.values(),
                f"frames={si.get('top_frames')} {voc}"))
    sa = legs(p, "pt_state_active")
    voc2 = sa.get("vocab") or {}
    out.append(("pt.state_active",
                sa.get("linked") is True and
                (sa.get("top_frames") or 0) >= 2 and
                len(set(voc2.values())) == 1 and
                voc2.get("dump") == "running",
                f"linked={sa.get('linked')} frames={sa.get('top_frames')} "
                f"{voc2}"))

    # ---------------- custody (per entry) ----------------
    for ent, e in (("btabs", b), ("wd", w), ("pt", p)):
        gone = e.get("sinks_gone")
        out.append((f"cust.{ent}.sinks_gone",
                    isinstance(gone, dict) and bool(gone) and
                    all(v is True for v in gone.values()), str(gone)))
        out.append((f"cust.{ent}.nodes_after",
                    e.get("own_nodes_after") == [],
                    str(e.get("own_nodes_after"))))
        unl = e.get("unloads") or {}
        good = True
        for tag, u in unl.items():
            u = u or {}
            if u.get("exit_code") != 0 or \
                    u.get("verified_index") != u.get("captured") or \
                    u.get("recycled") is not False:
                good = False
        out.append((f"cust.{ent}.unloads", good and bool(unl),
                    f"{len(unl)} unloads"))
        out.append((f"cust.{ent}.clean", e.get("failures") == [] and
                    not e.get("coverage_blocked"),
                    f"fail={e.get('failures')} "
                    f"blocked={e.get('coverage_blocked')}"))
    return out


def main(paths):
    receipts = [(p.split("/")[-1].replace(".receipt.json", ""),
                 json.load(open(p))) for p in paths]
    table = {}
    names = []
    for label, r in receipts:
        for name, ok, det in laws(r):
            table.setdefault(name, {})[label] = (ok, det)
            if name not in names:
                names.append(name)
    labels = [l for l, _ in receipts]
    w = max(len(n) for n in names) + 1
    print("law".ljust(w), " ".join(l.rjust(4) for l in labels))
    npass = 0
    ntot = 0
    fails = []
    for name in names:
        row = []
        for l in labels:
            ok, det = table[name].get(l, (None, ""))
            row.append(("PASS" if ok else "FAIL" if ok is False else "----"))
            ntot += 1
            if ok:
                npass += 1
            elif ok is False:
                fails.append((name, l, det))
        print(name.ljust(w), " ".join(c.rjust(4) for c in row))
    print(f"\nTOTAL: {npass}/{ntot} PASS")
    for name, l, det in fails:
        print(f"FAIL {name} @ {l}: {det}")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
