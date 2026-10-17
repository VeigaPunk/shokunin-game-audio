#!/usr/bin/env python3
"""r90 verifier law set — re-derives the r90 family's armed claims from the
RECORDED FIELDS of a `--probe-wpstate-r90` receipt.

Verifier-owned (seat r90-verifier). The receipt's own `failures` /
`coverage_blocked` lists are NEVER an input to a law: they are cross-checked
at the end (`x:*` laws) so a forged/silenced verdict list is visible.

Status semantics (the r95 convention):
  PASS    — the armed claim holds on the recorded field
  FAIL    — the field is present and the claim does not hold
  BLOCKED — the witness the law needs is absent (leg missing, value None,
            entry blocked) — never a green.

Usage:
    python3 r90v_laws.py <measurements.json> [--json out.json] [--census]
"""
import json
import sys

BAND = (0.5, 3.0)          # the coalescing-debounce band (fixture-armed)
ENUM_SHA = "1735b4739ef7"
SINK_SHA = "91f7342230f7"
PORT_SHA = "5a828addfad7"
S48_SHA = "e718690a7ce2"
S44_SHA = "684a7c8dad24"
ECHO_B = 622
UNASSIGNABLE = 4000000001

STORE_LEGS = ["w_settings", "w_settings_flags", "w_meta", "w_state_dir",
              "w_cross_volume", "w_create", "w_props", "w_pulse", "w_target",
              "w_replay_fields", "w_replay_target", "w_explicit_target",
              "w_vanished_target", "w_optout_stream", "w_optout_device"]
PMOD_LEGS = ["m_control", "m_phantom", "m_unassignable", "m_unix",
             "m_zeroconf_discover", "m_zeroconf_publish",
             "m_stub_stream_restore", "m_stub_device_restore",
             "m_stub_always_sink", "m_stub_unknown", "m_byname_control",
             "m_byname_prefix", "m_byname_nodename", "m_byname_unknown",
             "m_byname_final"]
WLINK_LEGS = ["k_connect", "k_bulk", "k_dup", "k_ids", "k_two_ids",
              "k_single_id", "k_reset", "k_bulk_d", "k_reversed", "k_glob",
              "k_w_valid", "k_w_missing", "k_w_late", "k_p_foo",
              "k_p_passive", "k_list_slot", "k_list_filtered",
              "k_l_pattern", "k_o_pattern", "k_t", "k_t_live", "k_m",
              "k_m_stream", "k_v"]
WFORMAT_LEGS = ["f_rest", "f_mid48", "f_setparam_sink", "f_setparam_stream",
                "f_44k", "f_post"]

ENTRY_LEGS = {
    "wpstate_store_r90_probe": STORE_LEGS,
    "wpstate_pmod_r90_probe": PMOD_LEGS,
    "wplink_r90_probe": WLINK_LEGS,
    "wpformat_r90_probe": WFORMAT_LEGS,
}


class Laws:
    def __init__(self):
        self.rows = []

    def add(self, law, status, detail=""):
        self.rows.append({"law": law, "status": status, "detail": str(detail)[:240]})

    def chk(self, law, ok, detail="", blocked=False):
        if blocked:
            self.add(law, "BLOCKED", detail)
        elif ok:
            self.add(law, "PASS", detail)
        else:
            self.add(law, "FAIL", detail)

    def status(self, prefix):
        return [r["status"] for r in self.rows if r["law"].startswith(prefix)]


def _in_band(v):
    return isinstance(v, (int, float)) and BAND[0] <= float(v) <= BAND[1]


def _rc(leg, key="exit_code"):
    return leg.get(key) if isinstance(leg, dict) else None


def _cls(leg, key="error_class"):
    return leg.get(key) if isinstance(leg, dict) else None


def _leg(L, legs, name, prefix, entry_blocked=None):
    """Return the leg or None; emit a BLOCKED law when the leg is absent."""
    leg = legs.get(name)
    if leg is None:
        L.chk(f"{prefix}.present", False,
              f"leg {name} absent from the receipt"
              + (f" (entry blocked: {entry_blocked})" if entry_blocked else ""),
              blocked=True)
    return leg


def _hygiene(L, prefix, entry, legs, want_legs):
    n = len(legs)
    L.chk(f"{prefix}.leg-census", n == want_legs,
          f"{n} legs recorded, want {want_legs}")
    fails = entry.get("failures") or []
    L.chk(f"{prefix}.verdict-failures-empty", not fails,
          f"receipt failures: {fails[:3]}", blocked=bool(entry.get("blocked")))
    blocks = entry.get("coverage_blocked") or []
    L.chk(f"{prefix}.verdict-blocks-empty", not blocks,
          f"coverage_blocked: {blocks[:3]}")
    unloads = entry.get("unloads") or {}
    if not unloads:
        L.chk(f"{prefix}.unloads", False, "no unloads recorded", blocked=True)
    else:
        bad = {k: v.get("exit_code") for k, v in unloads.items()
               if (v or {}).get("exit_code") != 0}
        L.chk(f"{prefix}.unloads-rc0", not bad, f"nonzero unloads: {bad}")
    sg = entry.get("sinks_gone")
    if sg == "reader_error" or sg is None:
        L.chk(f"{prefix}.sinks-gone", False, f"sinks_gone={sg!r}", blocked=True)
    else:
        L.chk(f"{prefix}.sinks-gone", all(sg.values()),
              f"sinks_gone={sg}")
    on = entry.get("own_nodes_after")
    if on == "reader_error" or on is None:
        L.chk(f"{prefix}.own-nodes-after", False, f"own_nodes_after={on!r}", blocked=True)
    else:
        L.chk(f"{prefix}.own-nodes-after", on == [], f"own_nodes_after={on}")
    om = entry.get("own_modules_after")
    if om is None:
        L.chk(f"{prefix}.own-modules-after", False, "own_modules_after absent", blocked=True)
    else:
        L.chk(f"{prefix}.own-modules-after", om == [], f"own_modules_after={om}")


# ----------------------------------------------------------------- store ---
def store_laws(L, entry):
    P = "store"
    legs = entry.get("legs") or {}
    eb = entry.get("blocked")

    st = _leg(L, legs, "w_settings", "store.w_settings", eb)
    if st is not None:
        L.chk("store.w_settings.rc0", _rc(st) == 0, f"rc={_rc(st)}")
        ents = st.get("entries")
        L.chk("store.w_settings.25-rows", isinstance(ents, list) and len(ents) == 25,
              f"entries={len(ents) if isinstance(ents, list) else ents}")
        bad = [e.get("id") for e in (ents or [])
               if not all(k in e for k in ("name", "desc", "type", "default", "value"))]
        L.chk("store.w_settings.typed-fields", not bad, f"missing fields: {bad}")
        L.chk("store.w_settings.type-histogram",
              st.get("types") == {"Boolean": 17, "Float": 5, "Integer": 1, "String": 2},
              f"types={st.get('types')}")
        ids, atd = set(st.get("ids") or []), set(st.get("at_default") or [])
        L.chk("store.w_settings.all-at-default", ids and ids == atd,
              f"not-at-default: {sorted(ids - atd)}")
        att = st.get("attempts") or []
        L.chk("store.w_settings.attempts-recorded",
              bool(att) and all("exit_code" in a and "entries" in a for a in att),
              f"attempts={att}")
        L.chk("store.w_settings.last-attempt-clean",
              bool(att) and att[-1].get("exit_code") == 0 and att[-1].get("entries"),
              f"last attempt={att[-1] if att else None}")

    sf = _leg(L, legs, "w_settings_flags", "store.w_settings_flags", eb)
    if sf is not None:
        out = sf.get("stdout") or ""
        L.chk("store.w_settings_flags.rc0", _rc(sf) == 0, f"rc={_rc(sf)}")
        L.chk("store.w_settings_flags.save-delete-reset",
              all(f in out for f in ("--save", "--delete", "--reset")),
              f"missing={[f for f in ('--save','--delete','--reset') if f not in out]}")

    wm = _leg(L, legs, "w_meta", "store.w_meta", eb)
    if wm is not None:
        L.chk("store.w_meta.reader-ok", wm.get("reader") == "ok",
              f"reader={wm.get('reader')}")
        objs = wm.get("objects") or []
        live = [o for o in objs if o.get("n_keys") == 25 and o.get("scalar_like")]
        schema = [o for o in objs if o.get("n_keys") == 25 and o.get("schema_like")]
        L.chk("store.w_meta.one-live-one-schema",
              len(live) == 1 and len(schema) == 1,
              f"live={len(live)} schema={len(schema)}")
        cli_ids = set((st or {}).get("ids") or [])
        if cli_ids and live and schema:
            L.chk("store.w_meta.live-keys==cli-ids",
                  set(live[0].get("keys") or []) == cli_ids,
                  f"live-only={sorted(set(live[0].get('keys') or []) ^ cli_ids)[:6]}")
            L.chk("store.w_meta.schema-keys==cli-ids",
                  set(schema[0].get("keys") or []) == cli_ids,
                  f"schema-only={sorted(set(schema[0].get('keys') or []) ^ cli_ids)[:6]}")
        else:
            L.chk("store.w_meta.twin-key-equality", False,
                  "cli ids or twins absent", blocked=True)

    sd = _leg(L, legs, "w_state_dir", "store.w_state_dir", eb)
    if sd is not None:
        names = sd.get("entries")
        if names is None:
            L.chk("store.w_state_dir.entries", False,
                  f"unreadable: {sd.get('reader_error')}", blocked=True)
        else:
            L.chk("store.w_state_dir.required-files",
                  "stream-properties" in names and "default-nodes" in names,
                  f"entries={names}")
            L.chk("store.w_state_dir.no-settings-file", "settings" not in names,
                  f"entries={names}")

    cv = _leg(L, legs, "w_cross_volume", "store.w_cross_volume", eb)
    if cv is not None:
        L.chk("store.w_cross_volume.value-0.064",
              cv.get("value") == "Value: 0.064", f"value={cv.get('value')!r}")
        L.chk("store.w_cross_volume.read-clean",
              _rc(cv) == 0 and (cv.get("attempt") or 0) >= 1,
              f"rc={_rc(cv)} attempt={cv.get('attempt')}")
        lcv = cv.get("live_channel_volumes")
        L.chk("store.w_cross_volume.live-witness-recorded",
              isinstance(lcv, list) and len(lcv) == 2
              and all(isinstance(x, (int, float)) for x in lcv),
              f"live_channel_volumes={lcv}")
        L.chk("store.w_cross_volume.default-sink-recorded",
              bool(cv.get("default_sink")), f"default_sink={cv.get('default_sink')!r}")

    keys = entry.get("keys") or {}
    kpre = entry.get("key_pre") or {}
    fresh_ok = bool(keys) and all(kpre.get(k) is False for k in keys.values())
    L.chk("store.fresh-key-guard", fresh_ok,
          f"key_pre={kpre}", blocked=not keys)

    wc = _leg(L, legs, "w_create", "store.w_create", eb)
    if wc is not None:
        L.chk("store.w_create.spawn", wc.get("spawn_ok") is True, f"spawn_ok={wc.get('spawn_ok')}")
        L.chk("store.w_create.band", _in_band(wc.get("t_row_s")),
              f"t_row_s={wc.get('t_row_s')}", blocked=wc.get("t_row_s") is None)
        row = wc.get("row") or {}
        L.chk("store.w_create.row-default-volume",
              row.get("channelVolumes") == [1.0, 1.0],
              f"channelVolumes={row.get('channelVolumes')}", blocked=not row)
        samples = wc.get("samples") or []
        L.chk("store.w_create.pre-absent-then-hit",
              bool(samples) and any(not s.get("present") for s in samples)
              and samples[-1].get("match") is True,
              f"samples={len(samples)} last={samples[-1] if samples else None}",
              blocked=not samples)

    wp = _leg(L, legs, "w_props", "store.w_props", eb)
    if wp is not None:
        L.chk("store.w_props.node", wp.get("stream_node") is not None,
              f"stream_node={wp.get('stream_node')}")
        L.chk("store.w_props.rc0", _rc(wp.get("cmd") or {}) == 0,
              f"rc={_rc(wp.get('cmd') or {})}")
        L.chk("store.w_props.band", _in_band(wp.get("t_hit_s")),
              f"t_hit_s={wp.get('t_hit_s')}", blocked=wp.get("t_hit_s") is None)
        row2 = wp.get("row") or {}
        L.chk("store.w_props.field-split",
              row2.get("channelVolumes") == [1.0, 1.0],
              f"channelVolumes={row2.get('channelVolumes')}", blocked=not row2)

    wpl = _leg(L, legs, "w_pulse", "store.w_pulse", eb)
    if wpl is not None:
        L.chk("store.w_pulse.spawn", wpl.get("spawn_ok") is True, f"spawn_ok={wpl.get('spawn_ok')}")
        si = wpl.get("sink_input") or {}
        L.chk("store.w_pulse.sink-input-index", si.get("index") is not None,
              f"sink_input.index={si.get('index')}")
        cmd = wpl.get("cmd") or {}
        L.chk("store.w_pulse.cmd-rc0", _rc(cmd) == 0, f"rc={_rc(cmd)}")
        L.chk("store.w_pulse.cmd-fast", isinstance(wpl.get("cmd_ms"), (int, float))
              and wpl["cmd_ms"] < 500, f"cmd_ms={wpl.get('cmd_ms')}")
        L.chk("store.w_pulse.band", _in_band(wpl.get("t_change_s")),
              f"t_change_s={wpl.get('t_change_s')}",
              blocked=wpl.get("t_change_s") is None)
        L.chk("store.w_pulse.not-stale-inside-band",
              isinstance(wpl.get("t_change_s"), (int, float))
              and float(wpl["t_change_s"]) >= BAND[0],
              f"t_change_s={wpl.get('t_change_s')} (a <=0.01 s hit is the "
              "stale-row class the r90 scout misread as a fast write)")
        row4 = wpl.get("row") or {}
        L.chk("store.w_pulse.field-split-volume-untouched",
              float(row4.get("volume", -1)) == 1.0,
              f"volume={row4.get('volume')}", blocked=not row4)
        cv4 = row4.get("channelVolumes")
        L.chk("store.w_pulse.field-split-channelVolumes",
              isinstance(cv4, list) and len(cv4) == 2
              and all(abs(float(x) - 0.125) < 1e-6 for x in cv4),
              f"channelVolumes={cv4}", blocked=not row4)

    wt = _leg(L, legs, "w_target", "store.w_target", eb)
    if wt is not None:
        L.chk("store.w_target.spawn", wt.get("spawn_ok") is True, f"spawn_ok={wt.get('spawn_ok')}")
        L.chk("store.w_target.rc0", _rc(wt.get("cmd") or {}) == 0,
              f"rc={_rc(wt.get('cmd') or {})}")
        L.chk("store.w_target.band", _in_band(wt.get("t_target_s")),
              f"t_target_s={wt.get('t_target_s')}",
              blocked=wt.get("t_target_s") is None)

    rf = _leg(L, legs, "w_replay_fields", "store.w_replay_fields", eb)
    if rf is not None:
        live = rf.get("live") or {}
        cvf = live.get("channelVolumes")
        L.chk("store.w_replay_fields.restores-stored-field",
              isinstance(cvf, list) and cvf and abs(float(cvf[0]) - 0.125) < 1e-6,
              f"channelVolumes={cvf}", blocked=not live)
        vol = live.get("volume")
        L.chk("store.w_replay_fields.volume-untouched",
              vol is None or float(vol) == 1.0, f"volume={vol}")

    rt = _leg(L, legs, "w_replay_target", "store.w_replay_target", eb)
    if rt is not None:
        edges = rt.get("edges_in_stored") or []
        L.chk("store.w_replay_target.links-stored-target", bool(edges),
              f"edges={len(edges)}")
        stored = rt.get("stored_target")
        L.chk("store.w_replay_target.edges-into-stored-node",
              bool(edges) and all(e.get("in_node") == stored for e in edges),
              f"stored={stored} in_nodes={sorted({e.get('in_node') for e in edges})}")

    et = _leg(L, legs, "w_explicit_target", "store.w_explicit_target", eb)
    if et is not None:
        ex = et.get("edges_in_explicit") or []
        stg = et.get("edges_in_stored") or []
        L.chk("store.w_explicit_target.explicit-wins", bool(ex), f"edges={len(ex)}")
        L.chk("store.w_explicit_target.stored-loses", not stg, f"edges={len(stg)}")
        L.chk("store.w_explicit_target.classes",
              bool(ex) and all(e.get("in_node") == et.get("explicit_target") for e in ex),
              f"in_nodes={sorted({e.get('in_node') for e in ex})}")
    else:
        blocks = entry.get("coverage_blocked") or []
        if not any("w_explicit_target" in b for b in blocks):
            L.chk("store.w_explicit_target.named-if-absent", False,
                  "leg absent and no named coverage block", blocked=True)

    vt = _leg(L, legs, "w_vanished_target", "store.w_vanished_target", eb)
    if vt is not None:
        L.chk("store.w_vanished_target.store-write-half",
              _in_band(vt.get("t_target_s")),
              f"t_target_s={vt.get('t_target_s')}",
              blocked=vt.get("t_target_s") is None)
        L.chk("store.w_vanished_target.replay-node-alive",
              vt.get("replay_node_present") is True,
              f"replay_node_present={vt.get('replay_node_present')}",
              blocked="replay_node_present" not in vt)
        outcome = vt.get("outcome")
        L.chk("store.w_vanished_target.named-outcome-class",
              outcome in ("fallback_to_default", "linked_elsewhere", "no_link"),
              f"outcome={outcome!r}", blocked="outcome" not in vt)
        fallback = vt.get("edges_into_default") or []
        anywhere = vt.get("edges_from_replay") or []
        if outcome == "fallback_to_default":
            L.chk("store.w_vanished_target.outcome-consistent",
                  bool(fallback), f"edges_into_default={len(fallback)}")
        elif outcome == "linked_elsewhere":
            L.chk("store.w_vanished_target.outcome-consistent",
                  bool(anywhere) and not fallback,
                  f"anywhere={len(anywhere)} fallback={len(fallback)}")
        elif outcome == "no_link":
            L.chk("store.w_vanished_target.outcome-consistent",
                  not fallback and not anywhere,
                  f"anywhere={len(anywhere)} fallback={len(fallback)}")
        else:
            L.chk("store.w_vanished_target.outcome-consistent", False,
                  f"outcome={outcome!r}", blocked=True)

    os_ = _leg(L, legs, "w_optout_stream", "store.w_optout_stream", eb)
    if os_ is not None:
        L.chk("store.w_optout_stream.no-row", os_.get("row_present") is False,
              f"row_present={os_.get('row_present')}")
        L.chk("store.w_optout_stream.control-row",
              os_.get("control_row_present") is True,
              f"control_row_present={os_.get('control_row_present')}")

    od = _leg(L, legs, "w_optout_device", "store.w_optout_device", eb)
    if od is not None:
        L.chk("store.w_optout_device.no-row", od.get("row_present") is False,
              f"row_present={od.get('row_present')}")
        L.chk("store.w_optout_device.control-row",
              od.get("control_row_present") is True,
              f"control_row_present={od.get('control_row_present')}")

    ent, ext = entry.get("store_at_entry") or {}, entry.get("store_at_exit") or {}
    L.chk("store.store-census-recorded",
          ent.get("reader") == "ok" and ext.get("reader") == "ok"
          and isinstance(ext.get("rows"), int),
          f"entry={ent} exit={ext}")
    L.chk("store.store-census-exit-ge-entry",
          isinstance(ext.get("rows"), int) and isinstance(ent.get("rows"), int)
          and ext["rows"] >= ent["rows"],
          f"entry={ent.get('rows')} exit={ext.get('rows')}")

    _hygiene(L, P, entry, legs, len(STORE_LEGS))


# ------------------------------------------------------------------ pmod ---
def pmod_laws(L, entry):
    P = "pmod"
    legs = entry.get("legs") or {}
    eb = entry.get("blocked")

    mc = _leg(L, legs, "m_control", "pmod.m_control", eb)
    if mc is not None:
        L.chk("pmod.m_control.load-rc0", mc.get("load_rc") == 0, f"load_rc={mc.get('load_rc')}")
        L.chk("pmod.m_control.module-id", mc.get("module_id") is not None,
              f"module_id={mc.get('module_id')}")
        L.chk("pmod.m_control.unload-rc0", (mc.get("unload") or {}).get("exit_code") == 0,
              f"unload={mc.get('unload')}")
        L.chk("pmod.m_control.sink-gone", mc.get("sink_gone") is True,
              f"sink_gone={mc.get('sink_gone')}")

    mp = _leg(L, legs, "m_phantom", "pmod.m_phantom", eb)
    if mp is not None:
        load = mp.get("load") or {}
        L.chk("pmod.m_phantom.load-rc0", _rc(load) == 0, f"rc={_rc(load)}")
        L.chk("pmod.m_phantom.id-returned", mp.get("id") is not None, f"id={mp.get('id')}")
        probes = mp.get("probes") or []
        L.chk("pmod.m_phantom.probe-lattice",
              len(probes) == 8 and all(p.get("mine") is False for p in probes),
              f"n={len(probes)} mine={[p.get('mine') for p in probes]}")
        L.chk("pmod.m_phantom.no-node", mp.get("node_present") is False,
              f"node_present={mp.get('node_present')}")
        L.chk("pmod.m_phantom.no-sink", mp.get("sink_present") is False,
              f"sink_present={mp.get('sink_present')}")
        L.chk("pmod.m_phantom.recycle-witness-recorded",
              isinstance(mp.get("id_recycled_by_foreign"), bool),
              f"id_recycled_by_foreign={mp.get('id_recycled_by_foreign')}")

    mu = _leg(L, legs, "m_unassignable", "pmod.m_unassignable", eb)
    if mu is not None:
        L.chk("pmod.m_unassignable.id-unassigned", mu.get("pre_present") is False,
              f"pre_present={mu.get('pre_present')}")
        cmd = mu.get("cmd") or {}
        L.chk("pmod.m_unassignable.rc1-no-entity",
              _rc(cmd) == 1 and _cls(cmd) == "wpstate_no_entity",
              f"rc={_rc(cmd)} class={_cls(cmd)}")
        L.chk("pmod.m_unassignable.id-is-never-assignable",
              mu.get("id") == UNASSIGNABLE, f"id={mu.get('id')}")

    mx = _leg(L, legs, "m_unix", "pmod.m_unix", eb)
    if mx is not None:
        L.chk("pmod.m_unix.rc1-conn-refused",
              _rc(mx) == 1 and _cls(mx) == "wpstate_conn_refused",
              f"rc={_rc(mx)} class={_cls(mx)}")

    zd = _leg(L, legs, "m_zeroconf_discover", "pmod.m_zeroconf_discover", eb)
    if zd is not None:
        L.chk("pmod.m_zeroconf_discover.rc1-no-entity",
              _rc(zd) == 1 and _cls(zd) == "wpstate_no_entity",
              f"rc={_rc(zd)} class={_cls(zd)}")

    zp = _leg(L, legs, "m_zeroconf_publish", "pmod.m_zeroconf_publish", eb)
    if zp is not None:
        load = zp.get("load") or {}
        L.chk("pmod.m_zeroconf_publish.load-rc0", _rc(load) == 0, f"rc={_rc(load)}")
        L.chk("pmod.m_zeroconf_publish.id-digit",
              str(load.get("stdout_token") or "").isdigit(),
              f"token={load.get('stdout_token')!r}")
        L.chk("pmod.m_zeroconf_publish.row-holds-id", bool(zp.get("rows")),
              f"rows={len(zp.get('rows') or [])}")
        L.chk("pmod.m_zeroconf_publish.unload-rc0",
              (zp.get("unload") or {}).get("exit_code") == 0,
              f"unload={zp.get('unload')}")

    for legname, want_cls in (("m_stub_stream_restore", "wpstate_entity_exists"),
                              ("m_stub_device_restore", "wpstate_entity_exists"),
                              ("m_stub_always_sink", "wpstate_entity_exists"),
                              ("m_stub_unknown", "wpstate_no_entity")):
        lg = _leg(L, legs, legname, f"pmod.{legname}", eb)
        if lg is not None:
            L.chk(f"pmod.{legname}.rc1-class",
                  _rc(lg) == 1 and _cls(lg) == want_cls,
                  f"rc={_rc(lg)} class={_cls(lg)} want={want_cls}")

    bc = _leg(L, legs, "m_byname_control", "pmod.m_byname_control", eb)
    if bc is not None:
        arm = bc.get("arm") or {}
        armed = arm.get("status") == "armed"
        L.chk("pmod.m_byname_control.armed", armed,
              f"status={arm.get('status')}", blocked=not armed)
        L.chk("pmod.m_byname_control.zero-foreign-precheck",
              (arm.get("pre") or {}).get("count") == 0
              and (arm.get("pre") or {}).get("all_mine") is True,
              f"pre={arm.get('pre')}", blocked=not armed)
        L.chk("pmod.m_byname_control.rc0", _rc(bc.get("cmd") or {}) == 0,
              f"rc={_rc(bc.get('cmd') or {})}", blocked=not armed)
        L.chk("pmod.m_byname_control.all-matching-removed",
              (bc.get("after") or {}).get("count") == 0,
              f"after={bc.get('after')}", blocked=not armed)
        L.chk("pmod.m_byname_control.own-sinks-alive",
              all(bc.get("own_sinks_alive") or []),
              f"own_sinks_alive={bc.get('own_sinks_alive')}", blocked=not armed)

    for legname in ("m_byname_prefix", "m_byname_nodename", "m_byname_unknown"):
        lg = _leg(L, legs, legname, f"pmod.{legname}", eb)
        if lg is not None:
            arm = lg.get("arm") or {}
            cmd = lg.get("cmd") or {}
            armed = arm.get("status") == "armed"
            L.chk(f"pmod.{legname}.armed", armed,
                  f"status={arm.get('status')}", blocked=not armed)
            L.chk(f"pmod.{legname}.rc0-stderr-only",
                  _rc(cmd) == 0 and _cls(cmd) == "wpstate_not_loaded"
                  and "not loaded" in (cmd.get("stderr") or ""),
                  f"rc={_rc(cmd)} class={_cls(cmd)} stderr={cmd.get('stderr')!r}",
                  blocked=not armed)
            L.chk(f"pmod.{legname}.nothing-removed",
                  (lg.get("after") or {}).get("count") == 2,
                  f"after={lg.get('after')}", blocked=not armed)

    bf = _leg(L, legs, "m_byname_final", "pmod.m_byname_final", eb)
    if bf is not None:
        pre = bf.get("pre") or {}
        after = bf.get("after")
        if pre.get("count") and pre.get("all_mine"):
            L.chk("pmod.m_byname_final.cleanup",
                  after is not None and after.get("count") == 0,
                  f"pre={pre.get('count')} after={after}")
        elif pre.get("count"):
            L.chk("pmod.m_byname_final.foreign-left-alone",
                  (entry.get("coverage_blocked") or []), "no named block")
        else:
            L.chk("pmod.m_byname_final.noop-clean", after is None or after.get("count") == 0,
                  f"pre=0 after={after}")

    _hygiene(L, P, entry, legs, len(PMOD_LEGS))


# ----------------------------------------------------------------- wplink ---
def wplink_laws(L, entry):
    P = "wplink"
    legs = entry.get("legs") or {}
    eb = entry.get("blocked")

    def simple(name, rc=None, links=None, err=None):
        lg = _leg(L, legs, name, f"wplink.{name}", eb)
        if lg is None:
            return None
        if rc is not None:
            L.chk(f"wplink.{name}.rc", _rc(lg) == rc, f"rc={_rc(lg)} want={rc}")
        if links is not None:
            L.chk(f"wplink.{name}.own-links", lg.get("own_links") == links,
                  f"own_links={lg.get('own_links')} want={links}")
        if err is not None:
            L.chk(f"wplink.{name}.stderr-class",
                  err in (lg.get("stderr") or ""), f"stderr={lg.get('stderr')!r}")
        return lg

    simple("k_connect", rc=0, links=1)
    simple("k_bulk", rc=0, links=2)
    simple("k_dup", rc=255, links=2, err="File exists")

    ki = _leg(L, legs, "k_ids", "wplink.k_ids", eb)
    if ki is not None:
        L.chk("wplink.k_ids.rc0", ki.get("rc") == 0, f"rc={ki.get('rc')}")
        mine = ki.get("mine") or []
        L.chk("wplink.k_ids.two-seat-links", len(mine) == 2, f"mine={mine}")
        rows = [l for l in (ki.get("links") or []) if l.get("link_id") in mine]
        L.chk("wplink.k_ids.link-id-is-first-token",
              len(rows) == 2 and all(isinstance(r.get("link_id"), int) for r in rows),
              f"rows={rows}")

    simple("k_two_ids", rc=255, links=2)
    simple("k_single_id", rc=0, links=1)

    kr = _leg(L, legs, "k_reset", "wplink.k_reset", eb)
    if kr is not None:
        L.chk("wplink.k_reset.known-set", kr.get("own_links") == 2,
              f"own_links={kr.get('own_links')}")
        L.chk("wplink.k_reset.rebuilt-not-lucky",
              len(kr.get("drop") or []) == 2 and len(kr.get("make") or []) == 2,
              f"drop={len(kr.get('drop') or [])} make={len(kr.get('make') or [])}")

    simple("k_bulk_d", rc=0, links=1)
    simple("k_reversed", rc=255, links=1)
    simple("k_glob", rc=255, links=1)

    wv = _leg(L, legs, "k_w_valid", "wplink.k_w_valid", eb)
    if wv is not None:
        L.chk("wplink.k_w_valid.rc0", _rc(wv) == 0 and not wv.get("killed_at_bound"),
              f"rc={_rc(wv)} killed={wv.get('killed_at_bound')}")
        L.chk("wplink.k_w_valid.fast", isinstance(wv.get("wall_s"), (int, float))
              and wv["wall_s"] <= 1.0, f"wall_s={wv.get('wall_s')}")
        L.chk("wplink.k_w_valid.link-formed", wv.get("own_links") == 2,
              f"own_links={wv.get('own_links')}")

    wm = _leg(L, legs, "k_w_missing", "wplink.k_w_missing", eb)
    if wm is not None:
        L.chk("wplink.k_w_missing.blocks-at-bound", wm.get("killed_at_bound") is True,
              f"killed_at_bound={wm.get('killed_at_bound')} rc={_rc(wm)}")

    wl = _leg(L, legs, "k_w_late", "wplink.k_w_late", eb)
    if wl is not None:
        L.chk("wplink.k_w_late.rc0", _rc(wl) == 0, f"rc={_rc(wl)}")
        wall = wl.get("wall_s")
        L.chk("wplink.k_w_late.returns-after-port",
              isinstance(wall, (int, float)) and 1.5 <= wall <= 4.0,
              f"wall_s={wall}")
        L.chk("wplink.k_w_late.link-into-l3", bool(wl.get("late_edges")),
              f"late_edges={len(wl.get('late_edges') or [])}")
        ll = wl.get("late_load") or {}
        L.chk("wplink.k_w_late.late-load-rc0", _rc(ll) == 0, f"rc={_rc(ll)}")

    pf = _leg(L, legs, "k_p_foo", "wplink.k_p_foo", eb)
    if pf is not None:
        L.chk("wplink.k_p_foo.rc0", _rc(pf) == 0, f"rc={_rc(pf)}")
        L.chk("wplink.k_p_foo.prop-on-link", (pf.get("foo_links") or 0) >= 1,
              f"foo_links={pf.get('foo_links')}")

    pp = _leg(L, legs, "k_p_passive", "wplink.k_p_passive", eb)
    if pp is not None:
        L.chk("wplink.k_p_passive.rc0", _rc(pp) == 0, f"rc={_rc(pp)}")
        links = pp.get("own_links") or []
        L.chk("wplink.k_p_passive.link-formed", bool(links), f"links={len(links)}")
        L.chk("wplink.k_p_passive.prop-invisible",
              bool(links) and not any("link.passive" in (e.get("props") or {}) for e in links),
              f"props={[e.get('props') for e in links][:2]}")

    ls = _leg(L, legs, "k_list_slot", "wplink.k_list_slot", eb)
    if ls is not None:
        rows = (ls.get("stdout") or "").splitlines()
        L.chk("wplink.k_list_slot.leaks-other-side",
              any("r90a_lc_" in r for r in rows), f"n_rows={len(rows)}")

    lf = _leg(L, legs, "k_list_filtered", "wplink.k_list_filtered", eb)
    if lf is not None:
        rows = (lf.get("stdout") or "").splitlines()
        L.chk("wplink.k_list_filtered.filters", not any("r90a_lc_" in r for r in rows),
              f"n_rows={len(rows)}")

    lp = _leg(L, legs, "k_l_pattern", "wplink.k_l_pattern", eb)
    if lp is not None:
        L.chk("wplink.k_l_pattern.ignores-pattern",
              _rc(lp) == 0 and bool((lp.get("stdout") or "").strip()),
              f"rc={_rc(lp)} bytes={lp.get('stdout_bytes')}")

    op = _leg(L, legs, "k_o_pattern", "wplink.k_o_pattern", eb)
    if op is not None:
        rows = [r for r in (op.get("stdout") or "").splitlines() if r.strip()]
        L.chk("wplink.k_o_pattern.filters-outputs",
              bool(rows) and all(r.startswith("r90a_la_") for r in rows),
              f"n_rows={len(rows)}")

    kt = _leg(L, legs, "k_t", "wplink.k_t", eb)
    if kt is not None:
        L.chk("wplink.k_t.silent", kt.get("out_len") == 0, f"out_len={kt.get('out_len')}")

    ktl = _leg(L, legs, "k_t_live", "wplink.k_t_live", eb)
    if ktl is not None:
        L.chk("wplink.k_t_live.silent-with-stream", ktl.get("out_len") == 0,
              f"out_len={ktl.get('out_len')}")
        L.chk("wplink.k_t_live.stream-alive", ktl.get("stream_alive") is True,
              f"stream_alive={ktl.get('stream_alive')}")

    km = _leg(L, legs, "k_m", "wplink.k_m", eb)
    if km is not None:
        L.chk("wplink.k_m.rc255-missing-ports",
              _rc(km) == 255 and _cls(km) == "wpstate_missing_ports",
              f"rc={_rc(km)} class={_cls(km)}")

    kms = _leg(L, legs, "k_m_stream", "wplink.k_m_stream", eb)
    if kms is not None:
        L.chk("wplink.k_m_stream.streams-and-blocks",
              kms.get("killed_at_bound") is True and (kms.get("stdout_bytes") or 0) > 0,
              f"killed={kms.get('killed_at_bound')} bytes={kms.get('stdout_bytes')}")

    kv = _leg(L, legs, "k_v", "wplink.k_v", eb)
    if kv is not None:
        L.chk("wplink.k_v.verbose-rows", (kv.get("n_rows") or 0) >= 2,
              f"n_rows={kv.get('n_rows')}")

    _hygiene(L, P, entry, legs, len(WLINK_LEGS))


# ---------------------------------------------------------------- wpformat ---
def wpformat_laws(L, entry):
    P = "wpformat"
    legs = entry.get("legs") or {}
    eb = entry.get("blocked")

    def sha_leg(legname, key, want, law):
        lg = _leg(L, legs, legname, f"wpformat.{legname}", eb)
        if lg is None:
            return None
        sub = lg.get(key) or {}
        got = sub.get("sha12")
        L.chk(law, got == want, f"{key}.sha12={got} want={want}",
              blocked=not sub)
        return lg

    fr = _leg(L, legs, "f_rest", "wpformat.f_rest", eb)
    if fr is not None:
        ef = fr.get("enumformat") or {}
        nf = fr.get("node_format") or {}
        pf = fr.get("port_format") or {}
        L.chk("wpformat.f_rest.enumformat-sha",
              ef.get("sha12") == ENUM_SHA and ef.get("out_bytes") == 1128,
              f"sha={ef.get('sha12')} bytes={ef.get('out_bytes')}")
        L.chk("wpformat.f_rest.node-format-unreadable",
              nf.get("out_bytes") == 0, f"out_bytes={nf.get('out_bytes')}")
        L.chk("wpformat.f_rest.port-format-res-minus-5",
              pf.get("out_bytes") == 0 and _cls(pf) == "wpstate_io_error",
              f"out_bytes={pf.get('out_bytes')} class={_cls(pf)}")

    fm = _leg(L, legs, "f_mid48", "wpformat.f_mid48", eb)
    if fm is not None:
        for key, want in (("enumformat", ENUM_SHA), ("node_format", SINK_SHA),
                          ("port_format", PORT_SHA), ("stream_format", S48_SHA)):
            sub = fm.get(key) or {}
            L.chk(f"wpformat.f_mid48.{key}-sha", sub.get("sha12") == want,
                  f"sha={sub.get('sha12')} want={want}", blocked=not sub)
        L.chk("wpformat.f_mid48.stream-node-present",
              fm.get("stream_node") is not None, f"stream_node={fm.get('stream_node')}")

    fs = _leg(L, legs, "f_setparam_sink", "wpformat.f_setparam_sink", eb)
    if fs is not None:
        cmd = fs.get("cmd") or {}
        L.chk("wpformat.f_setparam_sink.rc0", _rc(cmd) == 0, f"rc={_rc(cmd)}")
        L.chk("wpformat.f_setparam_sink.res-minus-5-on-stderr",
              _cls(cmd) == "wpstate_io_error", f"class={_cls(cmd)}")
        L.chk("wpformat.f_setparam_sink.stdout-echo-622",
              cmd.get("stdout_bytes") == ECHO_B, f"stdout_bytes={cmd.get('stdout_bytes')}")
        L.chk("wpformat.f_setparam_sink.link-set-unchanged",
              fs.get("after_links") == fs.get("before_links"),
              f"before={fs.get('before_links')} after={fs.get('after_links')}")
        L.chk("wpformat.f_setparam_sink.stream-alive",
              fs.get("stream_alive") is True, f"stream_alive={fs.get('stream_alive')}")

    fss = _leg(L, legs, "f_setparam_stream", "wpformat.f_setparam_stream", eb)
    if fss is not None:
        cmd2 = fss.get("cmd") or {}
        L.chk("wpformat.f_setparam_stream.rc0", _rc(cmd2) == 0, f"rc={_rc(cmd2)}")
        L.chk("wpformat.f_setparam_stream.silent",
              "res:" not in (cmd2.get("stderr") or ""),
              f"stderr={cmd2.get('stderr')!r}")
        L.chk("wpformat.f_setparam_stream.zero-stderr",
              fss.get("stderr_bytes") == 0, f"stderr_bytes={fss.get('stderr_bytes')}")

    f4 = _leg(L, legs, "f_44k", "wpformat.f_44k", eb)
    if f4 is not None:
        for key, want in (("stream_format", S44_SHA), ("node_format", SINK_SHA),
                          ("enumformat", ENUM_SHA)):
            sub = f4.get(key) or {}
            L.chk(f"wpformat.f_44k.{key}-sha", sub.get("sha12") == want,
                  f"sha={sub.get('sha12')} want={want}", blocked=not sub)

    fp = _leg(L, legs, "f_post", "wpformat.f_post", eb)
    if fp is not None:
        nf = fp.get("node_format") or {}
        pf = fp.get("port_format") or {}
        ef = fp.get("enumformat") or {}
        L.chk("wpformat.f_post.node-format-sticky",
              nf.get("sha12") == SINK_SHA, f"sha={nf.get('sha12')}")
        L.chk("wpformat.f_post.port-format-unreadable-again",
              pf.get("out_bytes") == 0 and _cls(pf) == "wpstate_io_error",
              f"out_bytes={pf.get('out_bytes')} class={_cls(pf)}")
        L.chk("wpformat.f_post.enumformat-unmoved",
              ef.get("sha12") == ENUM_SHA, f"sha={ef.get('sha12')}")

    _hygiene(L, P, entry, legs, len(WFORMAT_LEGS))


# ------------------------------------------------------------- cross-check ---
def cross_laws(L, receipt):
    m = receipt.get("measurements") or {}
    for name in ENTRY_LEGS:
        entry = m.get(name)
        if entry is None:
            L.chk(f"x.{name}.entry-present", False, "entry absent from receipt",
                  blocked=True)
            continue
        pref = name.replace("wpstate_store_r90_probe", "store") \
                   .replace("wpstate_pmod_r90_probe", "pmod") \
                   .replace("wplink_r90_probe", "wplink") \
                   .replace("wpformat_r90_probe", "wpformat")
        # field laws only: the verdict-list law itself must not satisfy the
        # "derived FAIL" side of the cross-check (that would make it vacuous).
        derived_fail = any(r["status"] == "FAIL" and r["law"].startswith(pref)
                           and "verdict-" not in r["law"]
                           for r in L.rows)
        # "unmeasured leg" witnesses only: a field-absent BLOCKED on an older
        # revision's receipt is not a silenced block claim.
        derived_block = any(r["status"] == "BLOCKED" and r["law"].startswith(pref)
                            and (r["law"].endswith(".present")
                                 or r["law"].endswith(".armed")
                                 or r["law"].endswith(".leg-census"))
                            for r in L.rows)
        receipt_fail = bool(entry.get("failures"))
        receipt_block = bool(entry.get("coverage_blocked"))
        L.chk(f"x.{pref}.no-silenced-red",
              not (derived_fail and not receipt_fail),
              f"derived FAILs but receipt failures empty: "
              f"{[r['law'] for r in L.rows if r['status'] == 'FAIL' and r['law'].startswith(pref)][:4]}")
        L.chk(f"x.{pref}.no-fabricated-red",
              not (receipt_fail and not derived_fail),
              f"receipt failures with no derived FAIL: {entry.get('failures')}")
        L.chk(f"x.{pref}.no-silenced-block",
              not (derived_block and not receipt_block),
              "derived BLOCKEDs but receipt coverage_blocked empty")
    tot = sum(len((m.get(n) or {}).get("legs") or {}) for n in ENTRY_LEGS)
    L.chk("x.leg-census-60", tot == 60, f"total legs recorded = {tot}")
    missing = [n for n in ENTRY_LEGS if (m.get(n) or {}).get("legs") is None]
    L.chk("x.all-entries-present", not missing, f"entries without legs: {missing}")


def derive(receipt):
    L = Laws()
    m = receipt.get("measurements") or {}
    store_laws(L, m.get("wpstate_store_r90_probe") or {})
    pmod_laws(L, m.get("wpstate_pmod_r90_probe") or {})
    wplink_laws(L, m.get("wplink_r90_probe") or {})
    wpformat_laws(L, m.get("wpformat_r90_probe") or {})
    cross_laws(L, receipt)
    return L


def summarize(L):
    out = {"PASS": 0, "FAIL": 0, "BLOCKED": 0}
    for r in L.rows:
        out[r["status"]] += 1
    out["TOTAL"] = len(L.rows)
    return out


def main(argv):
    path = argv[1]
    receipt = json.loads(open(path).read())
    L = derive(receipt)
    summary = summarize(L)
    if "--json" in argv:
        out = argv[argv.index("--json") + 1]
        open(out, "w").write(json.dumps(
            {"receipt": path, "summary": summary, "laws": L.rows}, indent=2) + "\n")
    print(json.dumps({"receipt": path, "summary": summary}))
    for r in L.rows:
        if r["status"] != "PASS":
            print(f"  {r['status']:7s} {r['law']}: {r['detail']}")
    if "--census" in argv:
        m = receipt.get("measurements") or {}
        for name in ENTRY_LEGS:
            legs = sorted(((m.get(name) or {}).get("legs") or {}).keys())
            print(f"  {name}: {len(legs)} legs: {legs}")
    return 1 if summary["FAIL"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
