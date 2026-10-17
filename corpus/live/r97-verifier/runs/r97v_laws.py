#!/usr/bin/env python3
"""r97 verifier law set — an independent re-derivation over a receipt's
RECORDED FIELDS ONLY (the fixture's own `failures` lists are never an input;
they are used at the end as a cross-check).

Expectations are taken from the tracked cross-seat receipts where one exists
(the r97-boundary `f_settings` lattice + listing sha, the r97-scout
`b_wpexec` Lua inventory lines) and from the committed block's armed values
otherwise.  Usage:

    python3 r97v_laws.py --receipt <measurements.json> \
        [--cross-root <frozen-tree/corpus/live>] [--out <json>]

Statuses: PASS / FAIL / BLOCKED.  An absent witness or a named vacuity is
BLOCKED, never green.
"""
import argparse
import json
import re
import sys
from pathlib import Path

CTX = {
    "probe", "contention", "oracle_at_start", "foreign_r97a_nodes",
    "inventory", "loadavg", "private_root", "conf_paths", "starts", "pair",
    "wp_restarts", "stops", "purge_before", "own_procs_after",
    "shared_census", "coverage_blocked", "failures", "blocked", "unloads",
    "residual_destroy",
}
ENTRIES = ["wppol_arming_r97_probe", "wppol_defaults_r97_probe",
           "wppol_linking_r97_probe", "wppol_wpexec_r97_probe",
           "wppol_settings_r97_probe"]
LEG_COUNTS = {"wppol_arming_r97_probe": 14, "wppol_defaults_r97_probe": 15,
              "wppol_linking_r97_probe": 21, "wppol_wpexec_r97_probe": 15,
              "wppol_settings_r97_probe": 4}
SETTINGS_SHA = ("56526540bdc17f5287f59d057edebf22d5de61653f622dc990a28e382db48a46")
LUA_ENV = "ENV=table G=nil VERSION=Lua 5.5"
LUA_GETREG = "debug.getregistry=function"
WP_READY_CAP = 30.0
FLUSH_CAP = 8.0


def load_cross(cross_root):
    """Cross-seat expectations from the frozen tree's tracked receipts."""
    out = {"lattice_keys": None, "known_sha": SETTINGS_SHA,
           "lua_found": None, "lua_missing": None, "source": {}}
    b = cross_root / "r97-boundary" / "receipts" / "f_settings.json"
    if b.exists():
        d = json.loads(b.read_text())
        out["lattice_keys"] = d["f3_shared_listing"]["keys"]
        out["known_sha"] = d["f5_scout_list_compare"]["scout_sha256"]
        out["source"]["lattice"] = str(b)
    s = cross_root / "r97-scout" / "receipts" / "b_wpexec.json"
    if s.exists():
        d = json.loads(s.read_text())
        lines = d["reps"][0]["legs"]["inventory"]["stdout"].splitlines()
        for ln in lines:
            if ln.startswith("FOUND "):
                out["lua_found"] = ln[len("FOUND "):]
            elif ln.startswith("MISSING "):
                out["lua_missing"] = ln[len("MISSING "):]
        out["source"]["lua"] = str(s)
    return out


class Res:
    def __init__(self):
        self.rows = []

    def add(self, name, status, detail=""):
        self.rows.append((name, status, detail))

    def chk(self, name, cond, detail="", blocked=False):
        if blocked:
            self.add(name, "BLOCKED", detail)
        elif cond:
            self.add(name, "PASS", "")
        else:
            self.add(name, "FAIL", detail)

    def miss(self, name, key):
        self.add(name, "BLOCKED", f"required key {key!r} absent")

    def fail(self, name, detail):
        self.add(name, "FAIL", detail)


def own_names(pid):
    return {f"r97a_{s}_{pid}" for s in
            ("sa", "sb", "sc", "sd", "se", "sf", "sg", "sh", "si", "sj",
             "sk", "sp", "sq")}


def pid_of(entry):
    m = re.search(r"wppol-r97-(\d+)-", entry.get("private_root") or "")
    if m:
        return int(m.group(1))
    c = entry.get("contention") or {}
    return c.get("own_pid")


def own_name_ok(name, pid):
    return bool(name) and name.startswith("r97a_") and name.endswith(f"_{pid}")


def links_to(rec, sink):
    return any(p[1] == sink for p in (rec.get("links") or []))


def sc(entry, key):
    """sub-record or None"""
    return entry.get(key)


# --------------------------------------------------------------- arming
def laws_arming(e, R, ctx):
    pid = pid_of(e)
    R.chk("arming.probe_name", e.get("probe") == "wppol_arming_r97_probe")
    a1c = e.get("a1_core")
    if a1c is None:
        R.miss("arming.a1_core", "a1_core")
    else:
        R.chk("arming.a1_core.up", a1c.get("up") is True)
        R.chk("arming.a1_core.socket_suffix",
              str(a1c.get("socket", "")).endswith("/run/pipewire-0"))
        R.chk("arming.a1_core.pid_positive", (a1c.get("pid") or 0) > 0)
    a1 = e.get("a1_pair_up")
    if a1 is None:
        R.miss("arming.a1_pair_up", "a1_pair_up")
    else:
        R.chk("arming.a1_pair_up.core_up", a1.get("core_up") is True)
        R.chk("arming.a1_pair_up.wp_ready", a1.get("wp_ready") is True)
        R.chk("arming.a1_pair_up.ready_within_cap",
              (a1.get("wp_ready_s") or 1e9) <= WP_READY_CAP,
              f"wp_ready_s={a1.get('wp_ready_s')}")
        R.chk("arming.a1_pair_up.core_pid_matches",
              a1c is not None and a1.get("core_pid") == a1c.get("pid"))
        R.chk("arming.a1_pair_up.objects_nonzero",
              (a1.get("objects") or 0) >= 1)
    stop = e.get("a2_stop_wp")
    if stop is None:
        R.miss("arming.a2_stop_wp", "a2_stop_wp")
    else:
        R.chk("arming.a2_stop_wp.killed", stop.get("killed") is True,
              json.dumps(stop))
        R.chk("arming.a2_stop_wp.pid_matches",
              a1 is not None and stop.get("pid") == a1.get("wp_pid"))
        R.chk("arming.a2_stop_wp.guard_not_refused",
              stop.get("reason") != "REFUSED foreign pid")
    a2 = e.get("a2_status_wp_down")
    if a2 is None:
        R.miss("arming.a2_status_wp_down", "a2_status_wp_down")
    else:
        R.chk("arming.a2_status_wp_down.sm_settings_absent",
              a2.get("sm_settings_absent") is True)
        R.chk("arming.a2_status_wp_down.rc0", a2.get("rc") == 0,
              f"rc={a2.get('rc')}")
        R.chk("arming.a2_status_wp_down.stdout_nonempty",
              bool((a2.get("stdout_head") or "").strip()))
        R.chk("arming.a2_status_wp_down.own_rows_empty",
              a2.get("own_rows") == [])
        head = a2.get("stdout_head") or ""
        R.chk("arming.a2_status_wp_down.listing_shape",
              "Clients:" in head and "Sinks:" in head)
    a3 = e.get("a3_conf_dir_missing")
    if a3 is None:
        R.miss("arming.a3_conf_dir_missing", "a3_conf_dir_missing")
    else:
        scan = a3.get("scan") or {}
        marks = scan.get("marks") or {}
        R.chk("arming.a3.rc78", a3.get("rc") == 78, f"rc={a3.get('rc')}")
        R.chk("arming.a3.naming_mark",
              marks.get("Could not locate configuration file "
                        "'wireplumber.conf'") is True)
        R.chk("arming.a3.chain_absent",
              not any(marks.get(k) for k in (
                  "no modules loaded from context.modules",
                  "can't find protocol 'PipeWire:Protocol:Native'",
                  "Failed to connect to PipeWire")))
        R.chk("arming.a3.no_fragments",
              (scan.get("fragments_opened") or []) == [])
        R.chk("arming.a3.using_config_empty",
              (scan.get("using_config") or []) == [])
        ec = a3.get("errclass") or []
        R.chk("arming.a3.errclass", bool(ec) and ec[0] == "wppol_config_missing")
    a4 = e.get("a4_conf_dir_replaces")
    if a4 is None:
        R.miss("arming.a4_conf_dir_replaces", "a4_conf_dir_replaces")
    else:
        scan = a4.get("scan") or {}
        frags = scan.get("fragments_opened") or []
        cfgs = scan.get("config_files") or []
        R.chk("arming.a4.copy_fragment",
              any("/conf/wp-copy/wireplumber.conf.d/" in f for f in frags),
              f"frags={frags}")
        R.chk("arming.a4.shipped_dir_absent",
              not any("/usr/share/wireplumber/wireplumber.conf.d" in f
                      for f in frags))
        R.chk("arming.a4.using_config_nonempty",
              bool(scan.get("using_config")))
        R.chk("arming.a4.config_file_is_copy",
              any("/conf/wp-copy/wireplumber.conf" in c for c in cfgs))
    a5 = e.get("a5_xdg_config_adds")
    if a5 is None:
        R.miss("arming.a5_xdg_config_adds", "a5_xdg_config_adds")
    else:
        scan = a5.get("scan") or {}
        frags = scan.get("fragments_opened") or []
        wp_frag = (e.get("conf_paths") or {}).get("wp_frag") or "\0"
        R.chk("arming.a5.shipped_frag",
              any("/usr/share/wireplumber/wireplumber.conf.d/alsa-vm.conf"
                  in f for f in frags))
        R.chk("arming.a5.own_frag", any(wp_frag in f for f in frags))
        R.chk("arming.a5.rc0", a5.get("rc") == 0, f"rc={a5.get('rc')}")
    a6 = e.get("a6_home_config_read")
    if a6 is None:
        R.miss("arming.a6_home_config_read", "a6_home_config_read")
    else:
        scan = a6.get("scan") or {}
        frags = scan.get("fragments_opened") or []
        shim = a6.get("shim_frag") or "\0"
        R.chk("arming.a6.shim_frag", any(shim in f for f in frags))
        R.chk("arming.a6.operator_dir_absent",
              not any("/home/vgpnk/.config/wireplumber" in f for f in frags),
              f"frags={frags}")
        R.chk("arming.a6.rc0", a6.get("rc") == 0, f"rc={a6.get('rc')}")
    a7 = e.get("a7_data_dir_replaces")
    if a7 is None:
        R.miss("arming.a7_data_dir_replaces", "a7_data_dir_replaces")
    else:
        scan = a7.get("scan") or {}
        marks = scan.get("marks") or {}
        R.chk("arming.a7.rc78", a7.get("rc") == 78, f"rc={a7.get('rc')}")
        R.chk("arming.a7.script_mark",
              marks.get("Could not locate script 'sm-objects.lua'") is True)
        R.chk("arming.a7.fragments_ge2",
              len(scan.get("fragments_opened") or []) >= 2)
    a8 = e.get("a8_core_no_modules")
    if a8 is None:
        R.miss("arming.a8_core_no_modules", "a8_core_no_modules")
    else:
        marks = (a8.get("scan") or {}).get("marks") or {}
        R.chk("arming.a8.up_false_socket_wait",
              a8.get("up") is False,
              "the modules-less core has no socket; the helper's socket "
              f"wait is expected to time out (up={a8.get('up')!r})")
        R.chk("arming.a8.alive_after_1s", a8.get("alive_after_1s") is True)
        R.chk("arming.a8.no_socket", a8.get("socket_present") is False)
        R.chk("arming.a8.warning_mark",
              marks.get("no modules loaded from context.modules") is True)
    a9 = e.get("a9_wp_on_modules_less_core")
    if a9 is None:
        R.miss("arming.a9_wp_on_modules_less_core",
               "a9_wp_on_modules_less_core")
    else:
        marks = (a9.get("scan") or {}).get("marks") or {}
        R.chk("arming.a9.rc69", a9.get("rc") == 69, f"rc={a9.get('rc')}")
        R.chk("arming.a9.connect_mark",
              marks.get("Failed to connect to PipeWire") is True)
        R.chk("arming.a9.middle_absent",
              marks.get("can't find protocol 'PipeWire:Protocol:Native'")
              is not True)
        ec = a9.get("errclass") or []
        # recorded, deliberately unarmed: the variant's stderr is empty in
        # this shape, so errclass is [None, None]; the scan marks are the
        # armed witness.  Shape law only.
        R.chk("arming.a9.errclass_key_present", "errclass" in a9,
              "errclass absent from the a9 record")
    a10 = e.get("a10_access_off")
    if a10 is None:
        R.miss("arming.a10_access_off", "a10_access_off")
    else:
        R.chk("arming.a10.core_up", a10.get("core_up") is True)
        R.chk("arming.a10.socket_present",
              a10.get("socket_present") is True)
        for tag in ("pw_dump", "pw_cli"):
            sub = a10.get(tag) or {}
            R.chk(f"arming.a10.{tag}_hang",
                  sub.get("timed_out") is True and sub.get("bytes") == 0,
                  json.dumps(sub))
    a11 = e.get("a11_access_on")
    if a11 is None:
        R.miss("arming.a11_access_on", "a11_access_on")
    else:
        R.chk("arming.a11.core_up", a11.get("core_up") is True)
        R.chk("arming.a11.rc0", a11.get("rc") == 0, f"rc={a11.get('rc')}")
        R.chk("arming.a11.has_client", a11.get("has_client") is True)
    a12 = e.get("a12_shared_untouched")
    if a12 is None:
        R.miss("arming.a12_shared_untouched", "a12_shared_untouched")
    else:
        R.chk("arming.a12.unreadable_false", a12.get("unreadable") is False)
        R.chk("arming.a12.own_hits_empty", a12.get("own_hits") == [],
              json.dumps(a12.get("own_hits")))
        R.chk("arming.a12.objects_gt0", (a12.get("objects") or 0) > 0)
    custody(e, R, "arming", pid)


# --------------------------------------------------------------- defaults
def laws_defaults(e, R, ctx):
    pid = pid_of(e)
    S = {k: f"r97a_{k}_{pid}" for k in
         ("sa", "sb", "sc", "sd", "se", "sf", "sg", "sh", "si", "sj", "sk",
          "sp", "sq")}
    R.chk("defaults.probe_name", e.get("probe") == "wppol_defaults_r97_probe")
    checks = [("d1_first_sink_wins", "sa"), ("d2_higher_session_takes", "sb"),
              ("d3_lower_session_does_not", "sb"),
              ("d4_tie_keeps_incumbent_low_driver_first", "se"),
              ("d5_tie_keeps_incumbent_high_driver_first", "sg"),
              ("d6_no_priority_does_not_displace", "si"),
              ("d7_driver_fallback_takes", "sp"),
              ("d8_driver_rank_beats_session", "sp")]
    for key, sink in checks:
        rec = e.get(key)
        if rec is None:
            R.miss(f"defaults.{key}", key)
            continue
        want = S[sink]
        R.chk(f"defaults.{key}.ok", rec.get("ok") is True,
              f"got={rec.get('got')!r} want={want!r}")
        R.chk(f"defaults.{key}.got", rec.get("got") == want,
              f"got={rec.get('got')!r}")
        R.chk(f"defaults.{key}.default_row",
              (rec.get("default") or {}).get("default.audio.sink") == want)
    d9 = e.get("d9_explicit_beats_priority")
    if d9 is None:
        R.miss("defaults.d9_explicit_beats_priority",
               "d9_explicit_beats_priority")
    else:
        want = S["sc"]
        R.chk("defaults.d9.set_rc0", d9.get("set_default_rc") == 0)
        R.chk("defaults.d9.after_set", d9.get("after_set") == want)
        rows = d9.get("metadata_rows") or {}
        R.chk("defaults.d9.metadata_default",
              rows.get("default.audio.sink") == want)
        R.chk("defaults.d9.metadata_configured",
              rows.get("default.configured.audio.sink") == want)
        body = d9.get("state_file") or ""
        R.chk("defaults.d9.state_file_row",
              f"default.configured.audio.sink={want}" in body)
        R.chk("defaults.d9.state_file_row_secs_le_cap",
              (d9.get("state_file_row_secs") or 1e9) <= FLUSH_CAP)
    lag = e.get("d9_lag_s")
    if lag is None:
        R.miss("defaults.d9_lag_s", "d9_lag_s")
    else:
        R.chk("defaults.d9_lag_le_cap", lag <= FLUSH_CAP, f"lag={lag}")
    d10 = e.get("d10_clear_default")
    if d10 is None:
        R.miss("defaults.d10_clear_default", "d10_clear_default")
    else:
        R.chk("defaults.d10.rc0", d10.get("rc") == 0)
        R.chk("defaults.d10.ok", d10.get("ok") is True,
              f"got={d10.get('got')!r}")
        R.chk("defaults.d10.got", d10.get("got") == S["sq"])
        R.chk("defaults.d10.configured_cleared",
              d10.get("configured_after") is None,
              f"configured_after={d10.get('configured_after')!r}")
    d11 = e.get("d11_removed_default_falls_back")
    if d11 is None:
        R.miss("defaults.d11_removed_default_falls_back",
               "d11_removed_default_falls_back")
    else:
        R.chk("defaults.d11.ok", d11.get("ok") is True,
              f"got={d11.get('got')!r}")
        R.chk("defaults.d11.got", d11.get("got") == S["sc"])
    d12 = e.get("d12_restart_race_lost")
    if d12 is None:
        R.miss("defaults.d12_restart_race_lost", "d12_restart_race_lost")
    else:
        R.chk("defaults.d12.set_ok", d12.get("set_ok") is True)
        R.chk("defaults.d12.restart_ready",
              d12.get("wp_restart_ready") is True)
        flushed = d12.get("flushed_before_restart")
        R.chk("defaults.d12.vacuity",
              flushed is False,
              "state file already flushed before the restart — race window "
              "missed, cell unarmed", blocked=(flushed is not False))
        if flushed is False:
            R.chk("defaults.d12.lost_default",
                  d12.get("default_after") == S["sq"],
                  f"default_after={d12.get('default_after')!r}")
            R.chk("defaults.d12.no_configured_row",
                  d12.get("configured_after") is None,
                  f"configured_after={d12.get('configured_after')!r}")
    d13 = e.get("d13_restart_durable")
    if d13 is None:
        R.miss("defaults.d13_restart_durable", "d13_restart_durable")
    else:
        want = S["sp"]
        R.chk("defaults.d13.state_row",
              f"default.configured.audio.sink={want}"
              in (d13.get("state_file_row") or ""))
        R.chk("defaults.d13.restart_ready",
              d13.get("wp_restart_ready") is True)
        R.chk("defaults.d13.default_after",
              d13.get("default_after") == want,
              f"default_after={d13.get('default_after')!r}")
        R.chk("defaults.d13.configured_after",
              d13.get("configured_after") == want,
              f"configured_after={d13.get('configured_after')!r}")
    custody(e, R, "defaults", pid)


# --------------------------------------------------------------- linking
def laws_linking(e, R, ctx):
    pid = pid_of(e)
    S = {k: f"r97a_{k}_{pid}" for k in
         ("sa", "sb", "sc", "sd", "se", "sf", "sg", "sh", "si", "sj", "sk",
          "sp", "sq")}
    stream = f"r97a_str_{pid}"
    R.chk("linking.probe_name", e.get("probe") == "wppol_linking_r97_probe")
    setup = e.get("setup")
    if setup is None:
        R.miss("linking.setup", "setup")
    else:
        R.chk("linking.setup.default_is_b", setup.get("default_is_b") is True)
        R.chk("linking.setup.a_id_positive", (setup.get("a_id") or 0) > 0)
        R.chk("linking.setup.a_serial_positive",
              (setup.get("a_serial") or 0) > 0)
        R.chk("linking.setup.b_serial_positive",
              (setup.get("b_serial") or 0) > 0)
    simple = [("l1_auto_default", "sb"), ("l3_target_serial", "sa"),
              ("l5_target_name", "sa"), ("l9_prop_target_object_serial", "sa"),
              ("l10_prop_target_object_id", "sb"),
              ("l11_prop_node_target_id", "sa"),
              ("l12_prop_node_target_serial", "sb"),
              ("l13_flag_order_early", "sa"), ("l14_flag_order_equals", "sa"),
              ("l15_flag_order_after_input", "sa"),
              ("l16_flag_order_between_props", "sa"),
              ("l17_media_role_no_target", "sb")]
    for key, sink in simple:
        rec = e.get(key)
        if rec is None:
            R.miss(f"linking.{key}", key)
            continue
        R.chk(f"linking.{key}.linked", links_to(rec, S[sink]),
              f"links={rec.get('links')!r} want={S[sink]!r}")
    for key in ("l13_flag_order_early", "l14_flag_order_equals",
                "l15_flag_order_after_input", "l16_flag_order_between_props"):
        rec = e.get(key) or {}
        R.chk(f"linking.{key}.alive_at_settle",
              rec.get("alive_at_settle") is True)
    l1 = e.get("l1_auto_default") or {}
    R.chk("linking.l1.default_row",
          (l1.get("default") or "") == S["sb"])
    l2 = e.get("l2_target_zero")
    if l2 is None:
        R.miss("linking.l2_target_zero", "l2_target_zero")
    else:
        R.chk("linking.l2.no_links", not l2.get("links"),
              f"links={l2.get('links')!r}")
    l4 = e.get("l4_target_global_id")
    if l4 is None:
        R.miss("linking.l4_target_global_id", "l4_target_global_id")
    else:
        R.chk("linking.l4.linked_default", links_to(l4, S["sb"]))
        R.chk("linking.l4.silent",
              l4.get("rc") in (0, None)
              and not (l4.get("stderr") or "").strip(),
              f"rc={l4.get('rc')} stderr={l4.get('stderr')!r}")
    l6 = e.get("l6_bogus_falls_back")
    if l6 is None:
        R.miss("linking.l6_bogus_falls_back", "l6_bogus_falls_back")
    else:
        R.chk("linking.l6.linked_default", links_to(l6, S["sb"]))
        R.chk("linking.l6.rc_not_error", l6.get("rc") in (0, None),
              f"rc={l6.get('rc')}")
        R.chk("linking.l6.stderr_empty",
              not (l6.get("stderr") or "").strip())
    l7 = e.get("l7_dont_fallback_destroys")
    if l7 is None:
        R.miss("linking.l7_dont_fallback_destroys",
               "l7_dont_fallback_destroys")
    else:
        R.chk("linking.l7.no_links", not l7.get("links"))
        R.chk("linking.l7.error_text",
              "defined target not found" in (l7.get("stderr") or ""))
    gone = e.get("l7_node_gone")
    if gone is None:
        R.miss("linking.l7_node_gone", "l7_node_gone")
    else:
        R.chk("linking.l7.node_gone", gone.get("gone") is True,
              json.dumps(gone))
    l8 = e.get("l8_linger_waits")
    if l8 is None:
        R.miss("linking.l8_linger_waits", "l8_linger_waits")
    else:
        R.chk("linking.l8.no_links", not l8.get("links"))
        R.chk("linking.l8.stderr_empty",
              not (l8.get("stderr") or "").strip())
        R.chk("linking.l8.node_present", l8.get("stream_node") is not None)
        R.chk("linking.l8.alive_at_cap", l8.get("alive_at_cap") is True)
    l17 = e.get("l17_media_role_no_target") or {}
    R.chk("linking.l17.role_recorded",
          (l17.get("stream_node") or {}).get("media.role") == "Communication")
    l18 = e.get("l18_follow_default_recorded")
    if l18 is None:
        R.miss("linking.l18_follow_default_recorded",
               "l18_follow_default_recorded")
    else:
        R.chk("linking.l18.readback_false",
              "Value: false" in (l18.get("readback") or ""))
        R.chk("linking.l18.sm_row_false",
              l18.get("sm_settings_row_after") is False,
              f"row={l18.get('sm_settings_row_after')!r}")
        R.chk("linking.l18.set_rc0", l18.get("set_rc") == 0)
        R.chk("linking.l18.set_default_rc0",
              l18.get("set_default_rc") == 0)
        R.chk("linking.l18.read_before_true",
              "Value: true" in (l18.get("read_before") or ""),
              f"read_before={l18.get('read_before')!r}")
        R.chk("linking.l18.movement_recorded",
              isinstance(l18.get("links_before"), list)
              and isinstance(l18.get("links_after"), list))
    for key in ("l1_auto_default", "l4_target_global_id",
                "l6_bogus_falls_back", "l17_media_role_no_target"):
        rec = e.get(key) or {}
        node = rec.get("stream_node")
        if node is not None:
            R.chk(f"linking.{key}.stream_name_own",
                  node.get("node.name") == stream,
                  f"node.name={node.get('node.name')!r}")
    custody(e, R, "linking", pid)


# --------------------------------------------------------------- wpexec
def laws_wpexec(e, R, ctx):
    pid = pid_of(e)
    R.chk("wpexec.probe_name", e.get("probe") == "wppol_wpexec_r97_probe")
    w1 = e.get("w1_inventory")
    if w1 is None:
        R.miss("wpexec.w1_inventory", "w1_inventory")
    else:
        lines = w1.get("lines") or []
        R.chk("wpexec.w1.rc0", w1.get("rc") == 0, f"rc={w1.get('rc')}")
        R.chk("wpexec.w1.lines4", len(lines) == 4, f"n={len(lines)}")
        if len(lines) == 4:
            if ctx.get("lua_found") is not None:
                R.chk("wpexec.w1.found_line",
                      lines[0] == "FOUND " + ctx["lua_found"],
                      "cross-witness: r97-scout inventory")
            else:
                R.add("wpexec.w1.found_line", "BLOCKED",
                      "scout inventory unavailable")
            if ctx.get("lua_missing") is not None:
                R.chk("wpexec.w1.missing_line",
                      lines[1] == "MISSING " + ctx["lua_missing"],
                      "cross-witness: r97-scout inventory")
            else:
                R.add("wpexec.w1.missing_line", "BLOCKED",
                      "scout inventory unavailable")
            R.chk("wpexec.w1.env_line", lines[2] == LUA_ENV,
                  f"line={lines[2]!r}")
            R.chk("wpexec.w1.getreg_line", lines[3] == LUA_GETREG,
                  f"line={lines[3]!r}")
        R.chk("wpexec.w1.stderr_empty",
              not (w1.get("stderr") or "").strip())
    w2 = e.get("w2_compile_error_located")
    if w2 is None:
        R.miss("wpexec.w2_compile_error_located", "w2_compile_error_located")
    else:
        R.chk("wpexec.w2.rc70", w2.get("rc") == 70, f"rc={w2.get('rc')}")
        R.chk("wpexec.w2.located",
              (w2.get("stderr") or "").startswith(
                  'Failed to compile: [string "w_syntax.lua"]:1:'))
    for key in ("w3_runtime_error_msg", "w4_nested_error", "w5_nil_index",
                "w6_pairs_G"):
        rec = e.get(key)
        if rec is None:
            R.miss(f"wpexec.{key}", key)
            continue
        R.chk(f"wpexec.{key}.rc70", rec.get("rc") == 70,
              f"rc={rec.get('rc')}")
        R.chk(f"wpexec.{key}.opaque",
              (rec.get("stderr") or "").strip() == "Lua runtime error",
              f"stderr={rec.get('stderr')!r}")
        R.chk(f"wpexec.{key}.stdout_empty",
              (rec.get("stdout") or "") == "")
    w7 = e.get("w7_no_quit")
    if w7 is None:
        R.miss("wpexec.w7_no_quit", "w7_no_quit")
    else:
        R.chk("wpexec.w7.killed_at_cap",
              w7.get("timed_out") is True and w7.get("rc") == -9,
              json.dumps(w7))
        R.chk("wpexec.w7.print_flushed",
              "r97a never quits" in (w7.get("stdout") or ""))
    w8 = e.get("w8_no_argument")
    if w8 is None:
        R.miss("wpexec.w8_no_argument", "w8_no_argument")
    else:
        R.chk("wpexec.w8.rc70", w8.get("rc") == 70)
        R.chk("wpexec.w8.null_refusal",
              "Could not locate script '(null)'" in (w8.get("stderr") or ""))
    w9 = e.get("w9_missing_file")
    if w9 is None:
        R.miss("wpexec.w9_missing_file", "w9_missing_file")
    else:
        R.chk("wpexec.w9.rc70", w9.get("rc") == 70)
        R.chk("wpexec.w9.path_named",
              "/nonexistent/r97a-missing.lua" in (w9.get("stderr") or ""))
    w10 = e.get("w10_positional_argument")
    if w10 is None:
        R.miss("wpexec.w10_positional_argument", "w10_positional_argument")
    else:
        R.chk("wpexec.w10.rc64", w10.get("rc") == 64, f"rc={w10.get('rc')}")
        R.chk("wpexec.w10.json_refusal",
              "script argument must be a JSON object"
              in (w10.get("stderr") or ""))
    w11 = e.get("w11_json_argument")
    if w11 is None:
        R.miss("wpexec.w11_json_argument", "w11_json_argument")
    else:
        R.chk("wpexec.w11.rc0", w11.get("rc") == 0)
        R.chk("wpexec.w11.arg_invisible",
              "arg=nil n=1" in (w11.get("stdout") or ""))
    w12 = e.get("w12_help")
    if w12 is None:
        R.miss("wpexec.w12_help", "w12_help")
    else:
        R.chk("wpexec.w12.rc0", w12.get("rc") == 0)
    w13 = e.get("w13_settings_unbound")
    if w13 is None:
        R.miss("wpexec.w13_settings_unbound", "w13_settings_unbound")
    else:
        R.chk("wpexec.w13.all_inert", w13.get("all_inert") is True)
        R.chk("wpexec.w13.identical", w13.get("identical") is True)
        R.chk("wpexec.w13.readback_false",
              "Value: false" in (w13.get("readback") or ""))
        R.chk("wpexec.w13.set_rc0", w13.get("set_rc") == 0)
        R.chk("wpexec.w13.before_after_equal",
              w13.get("before") == w13.get("after"))
    w14 = e.get("w14_sandbox_without_daemon")
    if w14 is None:
        R.miss("wpexec.w14_sandbox_without_daemon",
               "w14_sandbox_without_daemon")
    else:
        R.chk("wpexec.w14.sm_settings_absent",
              w14.get("sm_settings_absent") is True)
        R.chk("wpexec.w14.inventory_identical",
              w14.get("inventory_identical") is True)
        R.chk("wpexec.w14.settings_inert",
              w14.get("settings_inert") is True)
    stop = e.get("w14_wp_stop")
    if stop is None:
        R.miss("wpexec.w14_wp_stop", "w14_wp_stop")
    else:
        R.chk("wpexec.w14_wp_stop.killed", stop.get("killed") is True,
              json.dumps(stop))
    wr = (e.get("wp_restarts") or {}).get("after-down")
    if wr is None:
        R.miss("wpexec.wp_restart_after_down", "wp_restarts.after-down")
    else:
        R.chk("wpexec.wp_restart_after_down.ready",
              wr.get("wp_ready") is True)
    custody(e, R, "wpexec", pid)


# --------------------------------------------------------------- settings
def laws_settings(e, R, ctx):
    pid = pid_of(e)
    R.chk("settings.probe_name", e.get("probe") == "wppol_settings_r97_probe")
    s1 = e.get("s1_lattice")
    if s1 is None:
        R.miss("settings.s1_lattice", "s1_lattice")
    else:
        R.chk("settings.s1.rc0", s1.get("rc") == 0, f"rc={s1.get('rc')}")
        R.chk("settings.s1.n_keys", s1.get("n_keys") == 25,
              f"n={s1.get('n_keys')}")
        if ctx.get("lattice_keys") is not None:
            R.chk("settings.s1.key_set",
                  s1.get("keys") == ctx["lattice_keys"],
                  "cross-witness: r97-boundary f_settings lattice")
        else:
            R.add("settings.s1.key_set", "BLOCKED",
                  "boundary lattice unavailable")
        R.chk("settings.s1.sha", s1.get("sha256") == ctx["known_sha"],
              f"sha={s1.get('sha256')!r}")
        R.chk("settings.s1.sha_matches_boundary",
              s1.get("sha_matches_boundary") is True)
    s2 = e.get("s2_metadata_faces")
    if s2 is None:
        R.miss("settings.s2_metadata_faces", "s2_metadata_faces")
    else:
        for face in ("sm-settings", "schema-sm-settings"):
            sub = s2.get(face)
            if sub is None:
                R.fail(f"settings.s2.{face}", "metadata object absent")
            else:
                R.chk(f"settings.s2.{face}.rows", sub.get("rows") == 25,
                      f"rows={sub.get('rows')}")
        R.chk("settings.s2.settings_face_present",
              s2.get("settings") is not None)
    s3 = e.get("s3_write_scope")
    if s3 is None:
        R.miss("settings.s3_write_scope", "s3_write_scope")
    else:
        R.chk("settings.s3.set_rc0", s3.get("set_rc") == 0)
        R.chk("settings.s3.private_readback_false",
              "Value: false" in (s3.get("private_readback") or ""))
        readable = s3.get("shared_env_rc") == 0
        R.chk("settings.s3.shared_readable", readable,
              f"shared_env_rc={s3.get('shared_env_rc')}", blocked=not readable)
        if readable:
            R.chk("settings.s3.shared_unchanged",
                  s3.get("shared_before") == s3.get("shared_after"),
                  f"before={s3.get('shared_before')!r} "
                  f"after={s3.get('shared_after')!r}")
    s4 = e.get("s4_shared_lattice")
    if s4 is None:
        R.miss("settings.s4_shared_lattice", "s4_shared_lattice")
    else:
        readable = s4.get("rc") == 0
        R.chk("settings.s4.rc0", readable, f"rc={s4.get('rc')}",
              blocked=not readable)
        if readable:
            R.chk("settings.s4.n_keys", s4.get("n_keys") == 25)
            R.chk("settings.s4.same_key_set",
                  s4.get("same_key_set") is True)
            if s1 is not None:
                R.chk("settings.s4.sha_equal_private",
                      s4.get("sha256") == s1.get("sha256"))
    custody(e, R, "settings", pid)


# --------------------------------------------------------------- custody
def custody(e, R, prefix, pid):
    own = e.get("own_procs_after")
    if own is None:
        R.miss(f"{prefix}.custody.own_procs_after_empty",
               "own_procs_after")
    else:
        R.chk(f"{prefix}.custody.own_procs_after_empty", own == [],
              json.dumps(own)[:200])
    cen = e.get("shared_census")
    if cen is None:
        R.miss(f"{prefix}.custody.shared_own_hits_empty", "shared_census")
    else:
        R.chk(f"{prefix}.custody.shared_unreadable_false",
              cen.get("unreadable") is False)
        R.chk(f"{prefix}.custody.shared_own_hits_empty",
              cen.get("own_hits") == [], json.dumps(cen.get("own_hits")))
    stops = e.get("stops") or {}
    for tag, rec in stops.items():
        R.chk(f"{prefix}.custody.stop_{tag}_not_refused",
              (rec or {}).get("reason") != "REFUSED foreign pid")
    nodes = e.get("own_nodes_before_teardown")
    if nodes is not None:
        R.chk(f"{prefix}.custody.own_nodes_predicate",
              all(own_name_ok(n[1], pid) for n in nodes),
              json.dumps(nodes)[:200])
    R.chk(f"{prefix}.failures_empty",
          (e.get("failures") or []) == [], json.dumps(e.get("failures"))[:300])
    R.chk(f"{prefix}.no_blocked_key", "blocked" not in e)
    cb = e.get("coverage_blocked")
    R.chk(f"{prefix}.coverage_blocked_empty", not cb,
          json.dumps(cb)[:300])


def prefix_of(e):
    return (e.get("probe") or "?").replace("wppol_", "").replace(
        "_r97_probe", "")


# --------------------------------------------------------------- global
def laws_global(m, R):
    for name in ENTRIES:
        if name not in m:
            R.add(f"global.entry_present.{name}", "BLOCKED", "absent")
    present = [n for n in ENTRIES if n in m]
    R.chk("global.entries_present", len(present) == len(ENTRIES))
    counts = {}
    for name in present:
        legs = sorted(set(m[name]) - CTX)
        counts[name] = len(legs)
    R.chk("global.leg_census",
          counts == LEG_COUNTS,
          json.dumps(counts))
    R.chk("global.leg_census_total", sum(counts.values()) == 69,
          f"total={sum(counts.values())}")
    allf = {n: (m[n].get("failures") or []) for n in present}
    R.chk("global.all_failures_empty",
          all(not v for v in allf.values()), json.dumps(allf)[:400])
    allcb = {n: (m[n].get("coverage_blocked") or []) for n in present}
    R.chk("global.no_coverage_blocks",
          all(not v for v in allcb.values()), json.dumps(allcb)[:400])
    R.chk("global.own_procs_after_all_empty",
          all((m[n].get("own_procs_after") or []) == [] for n in present))
    R.chk("global.shared_own_hits_all_empty",
          all(((m[n].get("shared_census") or {}).get("own_hits") or [])
              == [] for n in present))
    pids = {pid_of(m[n]) for n in present}
    R.chk("global.single_pid", len(pids) == 1, json.dumps(sorted(pids)))
    pid = next(iter(pids)) if len(pids) == 1 else None
    if pid:
        bad = []
        for n in present:
            for k, v in m[n].items():
                if k == "own_nodes_before_teardown" and isinstance(v, list):
                    bad += [x[1] for x in v if not own_name_ok(x[1], pid)]
        R.chk("global.own_names_pid_suffix", bad == [], json.dumps(bad)[:200])
        R.chk("global.private_root_shape",
              all(f"wppol-r97-{pid}-" in (m[n].get("private_root") or "")
                  for n in present))
    R.chk("global.no_pactl_set_default",
          "pactl set-default" not in json.dumps(m))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--receipt", required=True)
    ap.add_argument("--cross-root", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--skip-global", action="store_true",
                    help="single-entry receipts: skip the cross-entry laws")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    receipt = json.loads(Path(args.receipt).read_text())
    m = receipt["measurements"]
    # the single-entry driver keys its receipt by the entry FUNCTION name;
    # normalise to the probe key the family's own receipts carry.
    for k in list(m):
        if k.endswith("_r97_entry"):
            m[k[:-len("_r97_entry")] + "_r97_probe"] = m[k]
    if args.cross_root:
        ctx = load_cross(Path(args.cross_root))
    else:
        here = Path(__file__).resolve().parents[1]  # r97-verifier/
        ctx = load_cross(here / "tree" / "corpus" / "live")
    R = Res()
    for name in ENTRIES:
        if name in m:
            fn = {"wppol_arming_r97_probe": laws_arming,
                  "wppol_defaults_r97_probe": laws_defaults,
                  "wppol_linking_r97_probe": laws_linking,
                  "wppol_wpexec_r97_probe": laws_wpexec,
                  "wppol_settings_r97_probe": laws_settings}[name]
            fn(m[name], R, ctx)
    if not args.skip_global:
        laws_global(m, R)
    n_pass = sum(1 for _, s, _ in R.rows if s == "PASS")
    n_fail = sum(1 for _, s, _ in R.rows if s == "FAIL")
    n_block = sum(1 for _, s, _ in R.rows if s == "BLOCKED")
    if not args.quiet:
        for name, status, detail in R.rows:
            if status != "PASS":
                print(f"{status:7s} {name}  {detail}")
    print(json.dumps({"receipt": args.receipt, "laws": len(R.rows),
                      "PASS": n_pass, "FAIL": n_fail, "BLOCKED": n_block}))
    if args.out:
        Path(args.out).write_text(json.dumps(
            {"receipt": args.receipt, "ctx_sources": ctx.get("source"),
             "laws": [{"law": n, "status": s, "detail": d}
                      for n, s, d in R.rows],
             "summary": {"laws": len(R.rows), "PASS": n_pass,
                         "FAIL": n_fail, "BLOCKED": n_block}}, indent=1))
    return 0 if (n_fail == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
