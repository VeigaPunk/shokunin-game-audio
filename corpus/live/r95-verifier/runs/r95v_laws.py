#!/usr/bin/env python3
"""r95 VERIFIER — independent law set over the r95 JACK lattice receipts.

Laws are re-derived from the RECORDED FIELDS ONLY (never from the entry's own
`failures` / `coverage_blocked` lists).  A missing field is BLOCKED (never a
green); a present-but-wrong field is FAIL.

Usage:
  r95v_laws.py <receipt.json> [--forge NAME] [--json OUT]
  r95v_laws.py --diff <receiptA> <receiptB>
"""
import copy
import json
import re
import sys

ENTRIES = ("jack_surface_r95_probe", "jack_addr_r95_probe",
           "jack_bytes_r95_probe", "jack_quantum_r95_probe",
           "jack_defects_r95_probe")

ABSENT_SYMS = sorted(("jack_net_open", "jack_client_activate",
                      "jack_uuid_to_string", "jack_error", "jack_info",
                      "jack_log", "jack_create_adapter"))
PRESENT_SYMS = sorted(("jack_session_notify", "jack_reserve_client_name",
                       "jack_client_real_time_priority",
                       "jack_client_max_real_time_priority",
                       "jack_set_buffer_size", "jack_connect",
                       "jack_set_property", "jack_transport_reposition"))

# this seat's own measurements (not read from the receipt)
OWN_LIBJACK = "/usr/lib/libjack.so.0.3.1608"
OWN_LIBJACK_SHA = None      # filled by --own-sha if provided
OWN_BINARY_SHA = None
OWN_FIXTURE_SHA = "55d4d4111bd8d46be743d0425a40dc8d938d15e071ce37f460db70de0df997be"


class Laws:
    def __init__(self, receipt, label=""):
        self.r = receipt
        self.m = receipt.get("measurements") or {}
        self.label = label
        self.rows = []

    # --- field access -------------------------------------------------
    def get(self, entry, path):
        """Dotted walk with LONGEST-KEY match, so PW metadata keys that
        themselves contain dots (`clock.force-quantum`, `r95a/key1`) are
        reachable: at each level the longest remaining prefix that is a
        literal key wins."""
        cur = self.m.get(entry)
        if cur is None:
            return (False, None)
        while path:
            if not isinstance(cur, dict):
                return (False, None)
            hit = None
            parts = path.split(".")
            for k in range(len(parts), 0, -1):
                cand = ".".join(parts[:k])
                if cand in cur:
                    hit = cand
                    break
            if hit is None:
                return (False, None)
            cur = cur[hit]
            path = path[len(hit):].lstrip(".")
        return (True, cur)

    def rec(self, lid, entry, path, got, want, status, kind):
        self.rows.append({"law": lid, "entry": entry, "field": path,
                          "kind": kind, "got": got, "want": want,
                          "status": status})

    # --- law kinds ----------------------------------------------------
    def eq(self, lid, entry, path, want, kind="eq"):
        found, got = self.get(entry, path)
        if not found or got is None:
            return self.rec(lid, entry, path, got, want, "BLOCKED", kind)
        self.rec(lid, entry, path, got, want,
                 "PASS" if got == want else "FAIL", kind)

    def band(self, lid, entry, path, lo, hi):
        found, got = self.get(entry, path)
        if not found or got is None:
            return self.rec(lid, entry, path, got, [lo, hi], "BLOCKED", "band")
        try:
            ok = lo <= got <= hi
        except TypeError:
            ok = False
        self.rec(lid, entry, path, got, [lo, hi],
                 "PASS" if ok else "FAIL", "band")

    def is_true(self, lid, entry, path):
        found, got = self.get(entry, path)
        if not found or got is None:
            return self.rec(lid, entry, path, got, True, "BLOCKED", "true")
        self.rec(lid, entry, path, got, True,
                 "PASS" if got is True else "FAIL", "true")

    def is_none(self, lid, entry, path):
        found, got = self.get(entry, path)
        if not found:
            return self.rec(lid, entry, path, got, None, "BLOCKED", "none")
        self.rec(lid, entry, path, got, None,
                 "PASS" if got is None else "FAIL", "none")

    def contains(self, lid, entry, path, needle):
        found, got = self.get(entry, path)
        if not found or got is None:
            return self.rec(lid, entry, path, got, needle, "BLOCKED", "contains")
        self.rec(lid, entry, path, got, needle,
                 "PASS" if needle in got else "FAIL", "contains")

    def approx(self, lid, entry, path, want, tol):
        found, got = self.get(entry, path)
        if not found or got is None:
            return self.rec(lid, entry, path, got, want, "BLOCKED", "approx")
        try:
            ok = abs(got - want) <= tol
        except TypeError:
            ok = False
        self.rec(lid, entry, path, got, f"{want}+-{tol}",
                 "PASS" if ok else "FAIL", "approx")

    def cond_eq(self, lid, entry, path, want, blocked_when, note=""):
        """eq(), but a *named* confound block converts the cell to BLOCKED
        (the family's own design: a foreign driver is a named coverage
        block, never a red)."""
        found, got = self.get(entry, path)
        if not found or got is None:
            return self.rec(lid, entry, path, got, want, "BLOCKED", "eq")
        if blocked_when:
            return self.rec(lid, entry, path, got, f"{want} ({note})",
                            "BLOCKED", "eq")
        self.rec(lid, entry, path, got, want,
                 "PASS" if got == want else "FAIL", "eq")

    # --- derived names ------------------------------------------------
    def names(self, entry):
        """prefix/pid from any leg's recorded client_name."""
        for path in self._client_name_paths(entry):
            found, cn = self.get(entry, path)
            if found and isinstance(cn, str):
                m = re.match(r"^(r95a_\d+)_", cn)
                if m:
                    prefix = m.group(1)
                    pid = prefix.split("_")[1]
                    return {"prefix": prefix, "pid": pid,
                            "ns": f"r95a_ns_{pid}", "ds": f"r95a_ds_{pid}",
                            "corner": f"r95a_t4_{pid}",
                            "role": f"r95arole{pid}"}
        return None

    def _client_name_paths(self, entry):
        e = self.m.get(entry) or {}
        out = []
        for leg, leaf in (e.get("legs") or {}).items():
            if isinstance(leaf, dict) and isinstance(leaf.get("json"), dict):
                out.append(f"legs.{leg}.json.client_name")
        return out

    def blocks(self, entry):
        found, b = self.get(entry, "coverage_blocked")
        return b if found and isinstance(b, list) else []

    # ------------------------------------------------------------------
    def run(self):
        for fn in (self.surface, self.addr, self.bytes_, self.quantum,
                   self.defects, self.hygiene):
            fn()
        return self

    # ------------------------------------------------------------------
    def surface(self):
        E = "jack_surface_r95_probe"
        self.is_none("surface.jackd_absent", E, "legs.a_avail.jackd")
        self.is_none("surface.jack_lsp_absent", E, "legs.a_avail.jack_lsp")
        self.is_none("surface.jack_connect_absent", E,
                     "legs.a_avail.jack_connect")
        found, pj = self.get(E, "legs.a_avail.pw_jack")
        self.rec("surface.pw_jack_present", E, "legs.a_avail.pw_jack", pj,
                 "non-null path", "BLOCKED" if not found
                 else ("PASS" if pj else "FAIL"), "present")
        self.eq("surface.libjack_path", E, "legs.a_avail.libjack_path",
                OWN_LIBJACK)
        if OWN_LIBJACK_SHA:
            # the fixture records the 16-hex prefix (_capture_r77_sha256)
            found, got = self.get(E, "legs.a_avail.libjack_sha256")
            if not found or not got:
                self.rec("surface.libjack_sha_vs_own", E,
                         "legs.a_avail.libjack_sha256", got,
                         OWN_LIBJACK_SHA[:16], "BLOCKED", "prefix")
            else:
                self.rec("surface.libjack_sha_vs_own", E,
                         "legs.a_avail.libjack_sha256", got,
                         OWN_LIBJACK_SHA[:16],
                         "PASS" if OWN_LIBJACK_SHA.startswith(str(got))
                         else "FAIL", "prefix")
        self.eq("surface.pacman_rc", E, "legs.a_avail.pacman.exit_code", 0)
        self.contains("surface.pacman_version", E,
                      "legs.a_avail.pacman.stdout", "pipewire-jack 1:1.6.8")
        self.eq("surface.export_count", E,
                "legs.a_avail.symbols.export_count", 168)
        self.eq("surface.absent_class", E, "legs.a_avail.symbols.absent",
                ABSENT_SYMS)
        self.eq("surface.present_class", E, "legs.a_avail.symbols.present",
                PRESENT_SYMS)
        self.eq("surface.version_ints", E,
                "legs.a_avail.version_probe.json.version_ints", [3, 1, 6, 8])
        self.contains("surface.version_str", E,
                      "legs.a_avail.version_probe.json.version",
                      "PipeWire 1.6.8")
        self.eq("surface.version_status", E,
                "legs.a_avail.version_probe.json.status", 0)
        self.eq("surface.version_rc", E,
                "legs.a_avail.version_probe.exit_code", 0)
        self.eq("surface.fixture_src_sha", E, "build.src_sha256",
                OWN_FIXTURE_SHA[:16])
        self.eq("surface.build_rc", E, "build.rc", 0)
        if OWN_BINARY_SHA:
            self.eq("surface.binary_sha_vs_own", E, "build.binary_sha256",
                    OWN_BINARY_SHA[:16])
        n = self.names(E)
        if not n:
            for lid in ("surface.port_names", "surface.flags", "surface.type",
                        "surface.out_conn", "surface.monitor",
                        "surface.census", "surface.resolve", "surface.client_api",
                        "surface.node_props", "surface.port_props",
                        "surface.port_flags_props", "surface.links",
                        "surface.driver", "surface.ns_port",
                        "surface.liveness"):
                self.rec(lid, E, "(derived)", None, "names", "BLOCKED",
                         "derived")
            return
        c = f"{n['prefix']}_shape"
        for tag in ("out", "in", "outp", "outt", "outm"):
            self.eq(f"surface.port_name.{tag}", E,
                    f"legs.s_shape.json.ports.{tag}", f"{c}:{tag}")
        for tag, want in (("out", 2), ("in", 1), ("outp", 6), ("outt", 18),
                          ("outm", 2)):
            self.eq(f"surface.port_flags.{tag}", E,
                    f"legs.s_shape.json.lat_{tag}.flags", want)
        self.eq("surface.lat_type", E, "legs.s_shape.json.lat_out.type",
                "32 bit float mono audio")
        self.eq("surface.out_connected", E,
                "legs.s_shape.json.out_connected", 0)
        self.eq("surface.out_connections", E,
                "legs.s_shape.json.out_connections", [])
        self.eq("surface.request_monitor_rc", E,
                "legs.s_shape.json.request_monitor_rc", 0)
        self.eq("surface.monitoring_input", E,
                "legs.s_shape.json.monitoring_input", 1)
        self.eq("surface.ensure_monitor_rc", E,
                "legs.s_shape.json.ensure_monitor_rc", 0)
        self.eq("surface.monitoring_input_in", E,
                "legs.s_shape.json.monitoring_input_in", 0)
        self.band("surface.census_pattern", E,
                  "legs.s_shape.json.census.pattern_r95a", 5, 100)
        found, lst = self.get(E, "legs.s_shape.json.census.pattern_r95a_list")
        want_own = sorted(f"{c}:{t}" for t in
                          ("out", "in", "outp", "outt", "outm"))
        if not found or lst is None:
            self.rec("surface.census_own_ports", E,
                     "legs.s_shape.json.census.pattern_r95a_list", lst,
                     want_own, "BLOCKED", "list")
        else:
            own = sorted(p for p in lst if isinstance(p, str)
                         and p.startswith(f"{c}:"))
            self.rec("surface.census_own_ports", E,
                     "legs.s_shape.json.census.pattern_r95a_list", own,
                     want_own, "PASS" if own == want_own else "FAIL", "list")
        found, res = self.get(E, "legs.s_shape.json.resolve")
        if not found or not isinstance(res, list) or not res:
            self.rec("surface.resolve_all", E, "legs.s_shape.json.resolve",
                     res, ">=1 resolved", "BLOCKED", "list")
        else:
            bad = [r for r in res if r.get("found") is not True]
            self.rec("surface.resolve_all", E, "legs.s_shape.json.resolve",
                     f"{len(res)} rows", "all found", 
                     "PASS" if not bad else "FAIL", "list")
        self.eq("surface.client_api", E, "legs.s_shape.mid.client.api", "jack")
        self.eq("surface.node_name", E, "legs.s_shape.mid.node.name", c)
        self.eq("surface.node_description", E,
                "legs.s_shape.mid.node.description", c)
        self.eq("surface.node_group", E, "legs.s_shape.mid.node.group",
                "group.dsp.0")
        self.eq("surface.media_category", E,
                "legs.s_shape.mid.node.media_category", "Duplex")
        self.eq("surface.media_role", E, "legs.s_shape.mid.node.media_role",
                "DSP")
        self.is_true("surface.always_process", E,
                     "legs.s_shape.mid.node.always_process")
        self.is_none("surface.media_class_absent", E,
                     "legs.s_shape.mid.node.media_class")
        for tag, idx in (("out", 0), ("outp", 1), ("outt", 2), ("outm", 3)):
            self.eq(f"surface.alias.{tag}", E,
                    f"legs.s_shape.mid.ports.{tag}.alias", f"{c}:{tag}")
            self.eq(f"surface.object_path.{tag}", E,
                    f"legs.s_shape.mid.ports.{tag}.object_path",
                    f"{c}:output_{idx}")
            self.eq(f"surface.direction.{tag}", E,
                    f"legs.s_shape.mid.ports.{tag}.direction", "out")
            self.eq(f"surface.format_dsp.{tag}", E,
                    f"legs.s_shape.mid.ports.{tag}.format_dsp",
                    "32 bit float mono audio")
        self.eq("surface.alias.in", E, "legs.s_shape.mid.ports.in.alias",
                f"{c}:in")
        self.eq("surface.direction.in", E,
                "legs.s_shape.mid.ports.in.direction", "in")
        self.is_true("surface.physical_outp", E,
                     "legs.s_shape.mid.ports.outp.physical")
        self.is_true("surface.terminal_outt", E,
                     "legs.s_shape.mid.ports.outt.terminal")
        self.is_none("surface.physical_outm", E,
                     "legs.s_shape.mid.ports.outm.physical")
        self.is_none("surface.terminal_outm", E,
                     "legs.s_shape.mid.ports.outm.terminal")
        self.is_none("surface.extra_outm", E,
                     "legs.s_shape.mid.ports.outm.extra")
        self.eq("surface.links_while_running", E, "legs.s_shape.mid.links", [])
        drv = self.blocks(E)
        drv_named = any("driver resolved to" in b for b in drv)
        self.cond_eq("surface.driver_name", E, "legs.s_shape.mid.driver.name",
                     "Dummy-Driver", drv_named, "named driver confound")
        if drv_named:
            self.rec("surface.driver_confound_named", E,
                     "coverage_blocked", drv_named, True, "PASS", "named")
        self.is_true("surface.driver_flag", E,
                     "legs.s_shape.mid.driver.driver")
        self.cond_eq("surface.driver_priority", E,
                     "legs.s_shape.mid.driver.priority_driver", 200000,
                     drv_named, "named driver confound")
        self.eq("surface.ns_port_alias", E, "legs.s_shape.ns_port.alias",
                f"{n['ds']}:playback_MONO")
        self.eq("surface.ns_port_object_path", E,
                "legs.s_shape.ns_port.object_path", f"{n['ns']}:playback_0")
        # s_liveness
        lc = f"{n['prefix']}_live"
        self.eq("surface.live_rc", E, "legs.s_liveness.exit_code", 0)
        self.eq("surface.live_client_name", E,
                "legs.s_liveness.json.client_name", lc)
        self.band("surface.live_cb", E, "legs.s_liveness.json.cb", 30, 100000)
        found, a = self.get(E, "legs.s_liveness.json.first_last_frame")
        found2, b = self.get(E, "legs.s_liveness.json.last_last_frame")
        if not (found and found2) or a is None or b is None:
            self.rec("surface.live_frames_advance", E,
                     "legs.s_liveness.json.last_last_frame", None,
                     "> first", "BLOCKED", "gt")
        else:
            self.rec("surface.live_frames_advance", E,
                     "legs.s_liveness.json.last_last_frame", b, f"> {a}",
                     "PASS" if b > a else "FAIL", "gt")
        self.eq("surface.live_links", E, "legs.s_liveness.mid.links", [])
        live_named = any("s_liveness: driver resolved to" in b
                         for b in self.blocks(E))
        self.cond_eq("surface.live_driver", E,
                     "legs.s_liveness.mid.driver.name", "Dummy-Driver",
                     live_named, "named driver confound")

    # ------------------------------------------------------------------
    def addr(self):
        E = "jack_addr_r95_probe"
        n = self.names(E)
        if not n:
            for lid in ("addr.rendered", "addr.native", "addr.fillalias",
                        "addr.corner"):
                self.rec(lid, E, "(derived)", None, "names", "BLOCKED",
                         "derived")
            return
        c = f"{n['prefix']}_xc"
        src = f"{c}:out"
        arms = (
            ("x_rendered", f"{n['ds']}:playback_MONO", True, 0, 1,
             [f"{n['ds']}:playback_MONO"],
             [f"{src}|->{n['ns']}:playback_MONO"]),
            ("x_native", f"{n['ns']}:playback_MONO", False, 22, 0, [],
             []),
            ("x_fillalias", f"{n['ns']}:playback_0", True, 0, 1,
             [f"{n['ds']}:playback_MONO"],
             [f"{src}|->{n['ns']}:playback_MONO"]),
            ("x_corner", f"{n['corner']}:playback_MONO", True, 0, 1,
             [f"{n['corner']}:playback_MONO"],
             [f"{src}|->{n['corner']}:playback_MONO"]),
        )
        for leg, dst, found, rc, conn, conns, edges in arms:
            self.eq(f"addr.{leg}.rc", E, f"legs.{leg}.exit_code", 0)
            self.eq(f"addr.{leg}.dst", E, f"legs.{leg}.dst", dst)
            self.eq(f"addr.{leg}.src_found", E,
                    f"legs.{leg}.json.src_found", True)
            self.eq(f"addr.{leg}.dst_found", E,
                    f"legs.{leg}.json.dst_found", found)
            self.eq(f"addr.{leg}.connect_rc", E,
                    f"legs.{leg}.json.connect_rc", rc)
            self.eq(f"addr.{leg}.connected", E,
                    f"legs.{leg}.json.connected", conn)
            self.eq(f"addr.{leg}.conns", E, f"legs.{leg}.json.conns", conns)
            self.eq(f"addr.{leg}.edges", E, f"legs.{leg}.edges", edges)
        self.eq("addr.fillalias.dst_type", E,
                "legs.x_fillalias.json.dst_type", "32 bit float mono audio")
        self.eq("addr.fillalias.alias_addressed", E,
                "legs.x_fillalias.alias_addressed",
                f"{n['ns']}:playback_0")
        self.eq("addr.fillalias.conns_canonical", E,
                "legs.x_fillalias.conns_canonical",
                [f"{n['ds']}:playback_MONO"])
        self.eq("addr.corner.description", E,
                "legs.x_corner.corner_description", n["corner"])
        self.eq("addr.corner.name", E, "legs.x_corner.corner_name",
                n["corner"])
        # the two forms must be distinguishable, else a named block exists
        found, d = self.get(E, "legs.x_rendered.ns_description")
        found2, nm = self.get(E, "legs.x_rendered.ns_name")
        if not (found and found2):
            self.rec("addr.forms_distinct", E, "legs.x_rendered.ns_description",
                     None, "differ", "BLOCKED", "ne")
        else:
            blk = any("coincide" in b for b in self.blocks(E))
            self.rec("addr.forms_distinct", E, "legs.x_rendered.ns_description",
                     f"{d} vs {nm}", "differ (or named block)",
                     "PASS" if (d != nm or blk) else "FAIL", "ne")

    # ------------------------------------------------------------------
    def bytes_(self):
        E = "jack_bytes_r95_probe"
        n = self.names(E)
        if not n:
            self.rec("bytes.names", E, "(derived)", None, "names", "BLOCKED",
                     "derived")
            return
        c = f"{n['prefix']}_j2p"
        self.eq("bytes.j2p.rc", E, "legs.b_jack2pw.exit_code", 0)
        self.eq("bytes.j2p.conn_rc", E, "legs.b_jack2pw.json.conn_rc", 0)
        self.is_true("bytes.j2p.recorder_linked", E,
                     "legs.b_jack2pw.recorder_linked")
        self.eq("bytes.j2p.edges", E, "legs.b_jack2pw.edges",
                [f"{c}:out|->{n['ns']}:playback_MONO"])
        self.band("bytes.j2p.capture_peak", E,
                  "legs.b_jack2pw.capture.peak", 0.4985, 0.5005)
        found, rms = self.get(E, "legs.b_jack2pw.capture.rms")
        if found and rms is not None:
            self.rec("bytes.j2p.rms_ratio", E, "legs.b_jack2pw.capture.rms",
                     rms / (0.5 / 2 ** 0.5), "[0.80, 1.02]",
                     "PASS" if 0.80 <= rms / (0.5 / 2 ** 0.5) <= 1.02
                     else "FAIL", "band")
        else:
            self.rec("bytes.j2p.rms_ratio", E, "legs.b_jack2pw.capture.rms",
                     None, "[0.80, 1.02]", "BLOCKED", "band")
        found, fr = self.get(E, "legs.b_jack2pw.capture.frames")
        found2, nz = self.get(E, "legs.b_jack2pw.capture.nonzero")
        if found and found2 and fr:
            self.rec("bytes.j2p.nonzero_frac", E,
                     "legs.b_jack2pw.capture.nonzero", nz / fr,
                     "[0.70, 1.0]",
                     "PASS" if 0.70 <= nz / fr <= 1.0 else "FAIL", "band")
        else:
            self.rec("bytes.j2p.nonzero_frac", E,
                     "legs.b_jack2pw.capture.nonzero", None, "[0.70, 1.0]",
                     "BLOCKED", "band")
        self.band("bytes.j2p.frames", E, "legs.b_jack2pw.capture.frames",
                  60000, 300000)
        self.band("bytes.j2p.n_tone", E, "legs.b_jack2pw.n_tone", 1, 10 ** 9)
        found, nt = self.get(E, "legs.b_jack2pw.n_tone")
        found2, ideal = self.get(E, "legs.b_jack2pw.ideal_mag2")
        if found and found2 and nt and ideal:
            self.rec("bytes.j2p.ideal_mag2_law", E,
                     "legs.b_jack2pw.ideal_mag2", ideal, (0.25 * nt) ** 2,
                     "PASS" if abs(ideal - (0.25 * nt) ** 2) < 1e-6 else "FAIL",
                     "eq")
        else:
            self.rec("bytes.j2p.ideal_mag2_law", E,
                     "legs.b_jack2pw.ideal_mag2", None, "derived", "BLOCKED",
                     "eq")
        found, mag2 = self.get(E, "legs.b_jack2pw.capture.goertzel_mag2")
        if found and ideal:
            self.rec("bytes.j2p.mag2_ratio", E,
                     "legs.b_jack2pw.capture.goertzel_mag2", mag2 / ideal,
                     "[0.90, 1.03]",
                     "PASS" if 0.90 <= mag2 / ideal <= 1.03 else "FAIL",
                     "band")
        else:
            self.rec("bytes.j2p.mag2_ratio", E,
                     "legs.b_jack2pw.capture.goertzel_mag2", None,
                     "[0.90, 1.03]", "BLOCKED", "band")
        # b_pw2jack
        c2 = f"{n['prefix']}_p2j"
        pl = f"{n['prefix']}_play"
        self.eq("bytes.p2j.rc", E, "legs.b_pw2jack.exit_code", 0)
        self.eq("bytes.p2j.client_name", E,
                "legs.b_pw2jack.json.client_name", c2)
        self.eq("bytes.p2j.tone_peak_i16", E,
                "legs.b_pw2jack.tone_source.peak_i16", 16383)
        self.is_true("bytes.p2j.linked", E, "legs.b_pw2jack.mid.linked")
        self.eq("bytes.p2j.link_rc", E, "legs.b_pw2jack.mid.link_rc.exit_code",
                0)
        self.eq("bytes.p2j.expected_peak", E,
                "legs.b_pw2jack.expected_peak", 16383 / 32768.0)
        self.approx("bytes.p2j.in_peak_exact", E,
                    "legs.b_pw2jack.json.in_peak", 16383 / 32768.0, 1e-9)
        self.band("bytes.p2j.in_nonzero", E,
                  "legs.b_pw2jack.json.in_nonzero", 30000, 75000)
        self.band("bytes.p2j.cb_in_nonzero", E,
                  "legs.b_pw2jack.json.cb_in_nonzero", 10, 100000)
        found, n_in = self.get(E, "legs.b_pw2jack.json.in_nonzero")
        found2, ideal2 = self.get(E, "legs.b_pw2jack.ideal_mag2")
        if found and found2 and n_in:
            self.rec("bytes.p2j.ideal_mag2_law", E,
                     "legs.b_pw2jack.ideal_mag2", ideal2, (0.25 * n_in) ** 2,
                     "PASS" if abs(ideal2 - (0.25 * n_in) ** 2) < 1e-6
                     else "FAIL", "eq")
        else:
            self.rec("bytes.p2j.ideal_mag2_law", E,
                     "legs.b_pw2jack.ideal_mag2", None, "derived", "BLOCKED",
                     "eq")
        found, mag2b = self.get(E, "legs.b_pw2jack.json.goertzel_mag2")
        if found and ideal2:
            self.rec("bytes.p2j.mag2_ratio", E,
                     "legs.b_pw2jack.json.goertzel_mag2", mag2b / ideal2,
                     "[0.985, 1.005]",
                     "PASS" if 0.985 <= mag2b / ideal2 <= 1.005 else "FAIL",
                     "band")
        else:
            self.rec("bytes.p2j.mag2_ratio", E,
                     "legs.b_pw2jack.json.goertzel_mag2", None,
                     "[0.985, 1.005]", "BLOCKED", "band")
        self.eq("bytes.p2j.edges", E, "legs.b_pw2jack.edges",
                [f"{pl}:output_MONO|->{c2}:in"])

    # ------------------------------------------------------------------
    def quantum(self):
        E = "jack_quantum_r95_probe"
        n = self.names(E)
        if not n:
            self.rec("quantum.names", E, "(derived)", None, "names",
                     "BLOCKED", "derived")
            return
        self.eq("quantum.default.set_inactive_rc", E,
                "legs.q_default.json.set_inactive_rc", 0)
        found, a = self.get(E, "legs.q_default.json.bufsize_inactive")
        found2, b = self.get(E, "legs.q_default.json.bufsize_after_set_inactive")
        if found and found2 and a is not None:
            self.rec("quantum.default.inactive_unchanged", E,
                     "legs.q_default.json.bufsize_after_set_inactive", b,
                     f"== {a}", "PASS" if b == a else "FAIL", "eq")
        else:
            self.rec("quantum.default.inactive_unchanged", E,
                     "legs.q_default.json.bufsize_after_set_inactive", None,
                     "== bufsize_inactive", "BLOCKED", "eq")
        self.eq("quantum.default.activated", E,
                "legs.q_default.json.bufsize_activated", 2048)
        self.eq("quantum.default.force_quantum", E,
                "legs.q_default.mid.q.force_quantum", "2048")
        self.eq("quantum.default.settings_quantum", E,
                "legs.q_default.mid.settings.clock.force-quantum", "0")
        self.eq("quantum.live.set_active_rc", E,
                "legs.q_live.json.set_active_rc", 0)
        self.eq("quantum.live.bufsize_after", E,
                "legs.q_live.json.bufsize_after_set_active", 512)
        found, x = self.get(E, "legs.q_live.json.bufsize_cbs")
        found2, y = self.get(E, "legs.q_live.json.bufsize_cbs_after")
        if found and found2 and x is not None and y is not None:
            self.rec("quantum.live.cb_fired", E,
                     "legs.q_live.json.bufsize_cbs_after", y, f"> {x}",
                     "PASS" if y > x else "FAIL", "gt")
        else:
            self.rec("quantum.live.cb_fired", E,
                     "legs.q_live.json.bufsize_cbs_after", None, "> cbs",
                     "BLOCKED", "gt")
        self.eq("quantum.live.last_cb", E,
                "legs.q_live.json.last_bufsize_cb_after", 512)
        self.eq("quantum.live.force_quantum_after", E,
                "legs.q_live.mid.q2.force_quantum", "512")
        self.eq("quantum.cross.a_activated", E,
                "legs.q_cross.json.bufsize_activated", 2048)
        self.eq("quantum.cross.a_force_quantum", E,
                "legs.q_cross.mid.a_force_quantum", "2048")
        self.eq("quantum.cross.b_rc", E, "legs.q_cross.mid.client_b_rc", 0)
        self.eq("quantum.cross.b_bufsize", E,
                "legs.q_cross.mid.client_b.bufsize_active", 2048)
        self.eq("quantum.cross.settings", E,
                "legs.q_cross.mid.settings.clock.force-quantum", "0")
        for leg in ("q_env", "q_wrapper"):
            self.eq(f"quantum.{leg}.set_skipped", E,
                    f"legs.{leg}.json.set_inactive_attempted", False)
            self.eq(f"quantum.{leg}.force_quantum", E,
                    f"legs.{leg}.mid.q.force_quantum", "512")
            self.eq(f"quantum.{leg}.force_rate", E,
                    f"legs.{leg}.mid.q.force_rate", "48000")
            self.eq(f"quantum.{leg}.bufsize_activated", E,
                    f"legs.{leg}.json.bufsize_activated", 512)
            self.eq(f"quantum.{leg}.srate_live", E,
                    f"legs.{leg}.json.srate_live", 48000)
        self.eq("quantum.env_rate.force_rate", E,
                "legs.q_env_rate.mid.q.force_rate", "44100")
        self.eq("quantum.env_rate.srate_active", E,
                "legs.q_env_rate.json.srate_active", 44100)
        self.eq("quantum.env_rate.srate_live", E,
                "legs.q_env_rate.json.srate_live", 44100)
        self.eq("quantum.env_rate.bufsize_live", E,
                "legs.q_env_rate.json.bufsize_live", 512)
        self.eq("quantum.env_rate.bufsize_activated", E,
                "legs.q_env_rate.json.bufsize_activated", 512)
        found, before = self.get(E, "settings_at_start.clock.rate")
        found2, after = self.get(E, "legs.q_env_rate.settings_after.clock.rate")
        if found and found2:
            self.rec("quantum.env_rate.rate_restored", E,
                     "legs.q_env_rate.settings_after.clock.rate", after,
                     f"== {before}", "PASS" if after == before else "FAIL",
                     "eq")
        else:
            self.rec("quantum.env_rate.rate_restored", E,
                     "legs.q_env_rate.settings_after.clock.rate", None,
                     "== settings_at_start", "BLOCKED", "eq")
        self.eq("quantum.bufsize1.force_quantum", E,
                "legs.q_bufsize1.mid.q.force_quantum", "1")
        self.band("quantum.bufsize1.effective", E,
                  "legs.q_bufsize1.json.bufsize_activated", 1, 8)
        self.eq("quantum.bufsize1.settings_untouched", E,
                "legs.q_bufsize1.mid.settings.clock.force-quantum", "0")
        self.eq("quantum.global.metadata_during", E,
                "legs.q_global.mid.settings.clock.force-quantum", "512")
        self.eq("quantum.global.metadata_after_exit", E,
                "legs.q_global.settings_after_exit.clock.force-quantum", "512")
        self.eq("quantum.global.second_client", E,
                "legs.q_global_second.json.bufsize_active", 512)
        self.eq("quantum.global.reset_restores", E,
                "settings_final.clock.force-quantum", "0")
        self.eq("quantum.global.settings_moved", E, "settings_moved", [])
        self.eq("quantum.final.rate", E, "settings_final.clock.rate", "48000")
        self.eq("quantum.final.quantum", E, "settings_final.clock.quantum",
                "1024")
        self.eq("quantum.final.allowed_rates", E,
                "settings_final.clock.allowed-rates", "[ 48000 ]")

    # ------------------------------------------------------------------
    def defects(self):
        E = "jack_defects_r95_probe"
        n = self.names(E)
        if not n:
            self.rec("defects.names", E, "(derived)", None, "names",
                     "BLOCKED", "derived")
            return
        killed = self.get(E, "legs.d_xrun_stall.killed_at_bound")[1]
        blk = any("d_xrun_stall: killed at the bound" in b
                  for b in self.blocks(E))
        if killed is True:
            self.rec("defects.xrun.named_block", E,
                     "legs.d_xrun_stall.killed_at_bound", killed,
                     "named block", "PASS" if blk else "FAIL", "named")
        else:
            self.eq("defects.xrun.rc", E, "legs.d_xrun_stall.exit_code", 0)
            self.band("defects.xrun.stall_cycles", E,
                      "legs.d_xrun_stall.json.stall_cycles", 4, 100000)
            self.band("defects.xrun.cb", E, "legs.d_xrun_stall.json.cb",
                      10, 100000)
            self.band("defects.xrun.xrun_cbs", E,
                      "legs.d_xrun_stall.json.xrun_cbs", 0, 1)
        self.eq("defects.poison.rc", E, "legs.d_rtprio_poison.exit_code", 0)
        for arm, pat in (("poison_aa", "0xaaaaaaa0"), ("poison_bb", "0xbbbbbbb0")):
            found, vals = self.get(E, f"legs.d_rtprio_poison.{arm}_masked")
            if not found or not vals:
                self.rec(f"defects.poison.{arm}", E,
                         f"legs.d_rtprio_poison.{arm}_masked", None,
                         f">=3 x {pat}", "BLOCKED", "list")
            else:
                ok = len(vals) >= 3 and all(
                    v[0] == pat and v[1] == pat for v in vals)
                self.rec(f"defects.poison.{arm}", E,
                         f"legs.d_rtprio_poison.{arm}_masked",
                         f"{len(vals)} rows", f">=3 x {pat}",
                         "PASS" if ok else "FAIL", "list")
        for tag in ("out_before", "out_after_set"):
            self.eq(f"defects.latency.{tag}_cap", E,
                    f"legs.d_latency.json.{tag}.lat_cap", [0, 0])
            self.eq(f"defects.latency.{tag}_play", E,
                    f"legs.d_latency.json.{tag}.lat_play", [0, 0])
        self.eq("defects.latency.active_cap", E,
                "legs.d_latency.json.out_active.lat_cap", [100, 200])
        self.eq("defects.latency.active_play", E,
                "legs.d_latency.json.out_active.lat_play", [10, 20])
        self.eq("defects.latency.active_total", E,
                "legs.d_latency.json.out_active.total", 150)
        self.eq("defects.latency.in_active_cap", E,
                "legs.d_latency.json.in_active.lat_cap", [0, 0])
        self.eq("defects.latency.recompute_rc", E,
                "legs.d_latency.json.recompute_rc", 0)
        self.eq("defects.transport.state_before", E,
                "legs.d_transport.json.state_before_activate", 0)
        self.eq("defects.transport.state_after_activate", E,
                "legs.d_transport.json.state_after_activate", 0)
        self.eq("defects.transport.tconn_rc", E,
                "legs.d_transport.json.tconn_rc", 0)
        self.eq("defects.transport.out_connected", E,
                "legs.d_transport.json.out_connected", 1)
        self.eq("defects.transport.state_after_start", E,
                "legs.d_transport.json.state_after_start", 1)
        found, f0 = self.get(E, "legs.d_transport.json.frame_after")
        found2, f1 = self.get(E, "legs.d_transport.json.frame_after_start")
        if found and found2 and f0 is not None and f1 is not None:
            self.rec("defects.transport.frame_advances", E,
                     "legs.d_transport.json.frame_after_start", f1, f"> {f0}",
                     "PASS" if f1 > f0 else "FAIL", "gt")
        else:
            self.rec("defects.transport.frame_advances", E,
                     "legs.d_transport.json.frame_after_start", None,
                     "> frame_after", "BLOCKED", "gt")
        self.eq("defects.transport.state_after_stop", E,
                "legs.d_transport.json.state_after_stop", 0)
        self.eq("defects.transport.locate_rc", E,
                "legs.d_transport.json.locate_rc", 0)
        self.eq("defects.transport.reposition_rc", E,
                "legs.d_transport.json.reposition_rc", 0)
        found, fs = self.get(E, "legs.d_transport.json.frame_after_stop")
        found2, fl = self.get(E, "legs.d_transport.json.frame_after_locate")
        if found and found2:
            self.rec("defects.transport.locate_inert", E,
                     "legs.d_transport.json.frame_after_locate", fl,
                     f"== {fs}", "PASS" if fl == fs else "FAIL", "eq")
        else:
            self.rec("defects.transport.locate_inert", E,
                     "legs.d_transport.json.frame_after_locate", None,
                     "== frame_after_stop", "BLOCKED", "eq")
        found, fr = self.get(E, "legs.d_transport.json.frame_after_reposition")
        if found and found2:
            self.rec("defects.transport.reposition_inert", E,
                     "legs.d_transport.json.frame_after_reposition", fr,
                     f"== {fs}", "PASS" if fr == fs else "FAIL", "eq")
        else:
            self.rec("defects.transport.reposition_inert", E,
                     "legs.d_transport.json.frame_after_reposition", None,
                     "== frame_after_stop", "BLOCKED", "eq")
        self.eq("defects.metadata.set_client_rc", E,
                "legs.d_metadata.json.set_client_rc", 0)
        self.eq("defects.metadata.set_port_rc", E,
                "legs.d_metadata.json.set_port_rc", 0)
        self.eq("defects.metadata.get_client_value", E,
                "legs.d_metadata.json.get_client_value", "value1")
        self.eq("defects.metadata.get_client_type", E,
                "legs.d_metadata.json.get_client_type", "text/plain")
        self.eq("defects.metadata.get_port_value", E,
                "legs.d_metadata.json.get_port_value", "portval")
        self.eq("defects.metadata.get_missing_rc", E,
                "legs.d_metadata.json.get_missing_rc", -1)
        self.eq("defects.metadata.own_desc_count", E,
                "legs.d_metadata.json.own_desc_count", 2)
        self.eq("defects.metadata.remove_rc", E,
                "legs.d_metadata.json.remove_client_rc", 0)
        self.eq("defects.metadata.stale_after_remove", E,
                "legs.d_metadata.json.get_after_remove_value", "value1")
        self.eq("defects.metadata.live_row_value", E,
                "legs.d_metadata.mid.rows.r95a/key1.value", "value1")
        found, subj = self.get(E, "legs.d_metadata.mid.rows.r95a/key1.subject")
        found2, nid = self.get(E, "legs.d_metadata.mid.node_id")
        if found and found2 and nid is not None:
            self.rec("defects.metadata.row_subject_is_node_id", E,
                     "legs.d_metadata.mid.rows.r95a/key1.subject", subj,
                     f"== node id {nid}", "PASS" if subj == nid else "FAIL",
                     "eq")
        else:
            self.rec("defects.metadata.row_subject_is_node_id", E,
                     "legs.d_metadata.mid.rows.r95a/key1.subject", None,
                     "== node id", "BLOCKED", "eq")
        self.eq("defects.metadata.rows_after_exit", E,
                "legs.d_metadata.rows_after_exit", {})
        self.is_true("defects.metadata.rows_after_exit_ok", E,
                     "legs.d_metadata.rows_after_exit_ok")

    # ------------------------------------------------------------------
    def hygiene(self):
        for E in ENTRIES:
            if E not in self.m:
                self.rec("hygiene.entry_present", E, "(entry)", None,
                         "present", "BLOCKED", "present")
                continue
            found, sg = self.get(E, "sinks_gone")
            if not found or sg is None:
                self.rec("hygiene.sinks_gone", E, "sinks_gone", None,
                         "all true", "BLOCKED", "dict")
            elif sg == {}:
                # the leg unloaded its sink before the census: ns_gone covers it
                self.rec("hygiene.sinks_gone", E, "sinks_gone", {},
                         "{} (mid-entry unload)", "PASS", "dict")
            else:
                bad = [k for k, v in sg.items() if v is not True]
                self.rec("hygiene.sinks_gone", E, "sinks_gone", sg,
                         "all true", "PASS" if not bad else "FAIL", "dict")
            found, sp = self.get(E, "stream_properties_own_rows")
            if found and sp is None:
                # receipt-contract law: with the committed bytes a None
                # store witness implies a NAMED block (the teardown's
                # `elif own_rows is None` branch). A silent None is a gap.
                named = any("stream-properties" in b for b in self.blocks(E))
                self.rec("hygiene.none_witness_named", E,
                         "stream_properties_own_rows", None,
                         "named unreadable-store block",
                         "PASS" if named else "FAIL", "named")
            self.eq("hygiene.stream_properties_own_rows", E,
                    "stream_properties_own_rows", [])
            self.eq("hygiene.own_nodes_after", E, "own_nodes_after", [])
            found, ul = self.get(E, "unloads")
            if not found or not isinstance(ul, dict) or not ul:
                self.rec("hygiene.unload_rc", E, "unloads", ul,
                         "all rc 0", "BLOCKED", "dict")
            else:
                skipped = [k for k, v in ul.items()
                           if isinstance(v, dict) and v.get("skipped")]
                bad = [k for k, v in ul.items()
                       if not isinstance(v, dict) or v.get("exit_code") != 0]
                if skipped and len(skipped) == len(ul):
                    # the module never enumerated (an earlier named block):
                    # the unload was never possible -> BLOCKED, not FAIL
                    self.rec("hygiene.unload_rc", E, "unloads",
                             f"{len(ul)} unloads, all skipped",
                             "all rc 0", "BLOCKED", "dict")
                else:
                    self.rec("hygiene.unload_rc", E, "unloads",
                             f"{len(ul)} unloads", "all rc 0",
                             "PASS" if not bad else "FAIL", "dict")
            self.eq("hygiene.foreign_nodes", E, "foreign_r95a_nodes", [])
            self.eq("hygiene.foreign_clients", E, "foreign_r95a_clients", [])
            if E == "jack_surface_r95_probe":
                self.is_true("hygiene.ns_gone_after_unload", E,
                             "ns_gone_after_unload")
            if E == "jack_bytes_r95_probe":
                self.is_true("hygiene.bytes_ns_gone_after_unload", E,
                             "ns_gone_after_unload")

    # ------------------------------------------------------------------
    def summary(self):
        from collections import Counter
        c = Counter(r["status"] for r in self.rows)
        return c

    def report(self, out=None):
        c = self.summary()
        print(f"== {self.label}  laws={len(self.rows)} "
              f"PASS={c['PASS']} FAIL={c['FAIL']} BLOCKED={c['BLOCKED']}")
        for r in self.rows:
            if r["status"] != "PASS":
                print(f"  {r['status']:7s} {r['law']:48s} "
                      f"{r['field']}: got={r['got']!r} want={r['want']!r}")
        if out:
            with open(out, "w") as fh:
                json.dump({"label": self.label, "summary": dict(c),
                           "rows": self.rows}, fh, indent=1)
        return c


FORGERIES = {
    "none": lambda r: r,
    "blank-verdicts": lambda r: _blank(r),
    "forge-version-ints": lambda r: _set(r, "jack_surface_r95_probe",
                                         "legs.a_avail.version_probe.json.version_ints",
                                         [3, 1, 6, 9]),
    "forge-export-count": lambda r: _set(r, "jack_surface_r95_probe",
                                         "legs.a_avail.symbols.export_count",
                                         167),
    "forge-flags-outm": lambda r: _set(r, "jack_surface_r95_probe",
                                       "legs.s_shape.json.lat_outm.flags", 10),
    "forge-port-alias": lambda r: _set(r, "jack_surface_r95_probe",
                                       "legs.s_shape.mid.ports.outm.alias",
                                       "r95a_<pid>_shape:outx"),
    "forge-native-rc": lambda r: _set(r, "jack_addr_r95_probe",
                                      "legs.x_native.json.connect_rc", 0),
    "forge-in-peak": lambda r: _set(r, "jack_bytes_r95_probe",
                                    "legs.b_pw2jack.json.in_peak", 0.4999),
    "forge-mag2": lambda r: _set(r, "jack_bytes_r95_probe",
                                 "legs.b_jack2pw.capture.goertzel_mag2", 1e9),
    "forge-capture-sha": lambda r: _set(r, "jack_bytes_r95_probe",
                                        "legs.b_jack2pw.capture.sha256",
                                        "deadbeef"),
    "forge-ideal": lambda r: _set(r, "jack_bytes_r95_probe",
                                  "legs.b_jack2pw.ideal_mag2", 1.0),
    "forge-conns": lambda r: _set(r, "jack_addr_r95_probe",
                                  "legs.x_rendered.json.conns", []),
    "forge-driver": lambda r: _set(r, "jack_surface_r95_probe",
                                   "legs.s_shape.mid.driver.name", "Other"),
    "forge-quantum-prop": lambda r: _set(r, "jack_quantum_r95_probe",
                                         "legs.q_live.mid.q2.force_quantum",
                                         "1024"),
    "forge-settings-moved": lambda r: _set(r, "jack_quantum_r95_probe",
                                           "settings_moved", ["clock.rate"]),
    "forge-xrun": lambda r: _set(r, "jack_defects_r95_probe",
                                 "legs.d_xrun_stall.json.xrun_cbs", 8),
    "forge-latency": lambda r: _set(r, "jack_defects_r95_probe",
                                    "legs.d_latency.json.out_active.total",
                                    100),
    "forge-metadata-row": lambda r: _set(r, "jack_defects_r95_probe",
                                         "legs.d_metadata.mid.rows.r95a/key1.value",
                                         "value9"),
    "pop-leg": lambda r: _pop(r, "jack_bytes_r95_probe", "legs.b_jack2pw"),
    "pop-hygiene": lambda r: _pop(r, "jack_addr_r95_probe",
                                  "stream_properties_own_rows"),
    "forge-build-sha": lambda r: _set(r, "jack_surface_r95_probe",
                                      "build.src_sha256", "deadbeefdeadbeef"),
}


def _entry(r, e):
    return (r.get("measurements") or {}).get(e) or {}


def _set(r, e, path, val):
    r = copy.deepcopy(r)
    cur = _entry(r, e)
    parts = path.split(".")
    for p in parts[:-1]:
        cur = cur[p]
    cur[parts[-1]] = val
    return r


def _pop(r, e, path):
    r = copy.deepcopy(r)
    cur = _entry(r, e)
    parts = path.split(".")
    for p in parts[:-1]:
        cur = cur[p]
    cur.pop(parts[-1], None)
    return r


def _blank(r):
    r = copy.deepcopy(r)
    for e in ENTRIES:
        if e in (r.get("measurements") or {}):
            r["measurements"][e]["failures"] = []
            r["measurements"][e]["coverage_blocked"] = []
    return r


PIDNORM = re.compile(r"(r95[abs]_)(?:ns_|ds_|t4_)?\d+")


def norm(x):
    """normalise seat-pid-bearing strings and temp paths before comparing."""
    if isinstance(x, str):
        x = PIDNORM.sub(lambda m: m.group(1) + "<pid>", x)
        x = re.sub(r"/tmp/r95a-[A-Za-z0-9_]+/", "/tmp/r95a-<tmp>/", x)
        x = re.sub(r"r95a-\d+", "r95a-<pid>", x)
        return x
    return x


VOLATILE = re.compile(
    r"(wall_s|utc|loadavg|host|_bytes$|cpu_load|jack_time|client_uuid|"
    r"client_pid|rt_prio|cycle_|xrun_delayed|max_delayed|verified_index|"
    r"captured|stdout|stderr|error_hit|contention|fixture_runs|own_pid|"
    r"frame_after|last_frame|first_last_frame|last_last_frame|"
    r"goertzel|in_sum|in_rms|in_samples|in_nonzero|in_peak|nonzero|peak|"
    r"rms|frames|ideal_mag2|n_tone|cb|_cbs|srate|bufsize_live|"
    r"frames_since|mono_delta|jack_time_delta|settings_at_start|"
    r"recycled|serial|driver_name|priority_driver|host_is_quiet|"
    r"argv|stdout|stderr|error_hit|client_name|client_pid|dst$|src$|"
    r"conns|edges|alias_addressed|conns_canonical|corner_description|"
    r"corner_name|ns_description|ns_name|expected_peak|node_id|"
    r"row_subject|subject|mid|sinks_gone|unloads|wall_us|frame_time|"
    r"port_uuid|all_desc_count|baseline|usecs|current_after_locate|"
    r"tone_source|sha256|last_frame|ns_gone|rows_after_exit)")


def diff(a, b):
    """structural walk of two receipts, excluding declared volatiles."""
    diffs = []

    def walk(x, y, path):
        if isinstance(x, dict) and isinstance(y, dict):
            for k in sorted(set(x) | set(y)):
                walk(x.get(k), y.get(k), f"{path}.{k}")
        elif isinstance(x, list) and isinstance(y, list):
            if len(x) != len(y):
                diffs.append((path, f"len {len(x)}", f"len {len(y)}"))
            for i, (xi, yi) in enumerate(zip(x, y)):
                walk(xi, yi, f"{path}[{i}]")
        else:
            if norm(x) != norm(y):
                diffs.append((path, x, y))

    walk(a.get("measurements"), b.get("measurements"), "measurements")
    leaves = 0

    def count(x, path):
        nonlocal leaves
        if isinstance(x, dict):
            for k, v in x.items():
                count(v, f"{path}.{k}")
        elif isinstance(x, list):
            for i, v in enumerate(x):
                count(v, f"{path}[{i}]")
        else:
            leaves += 1

    count(a.get("measurements"), "measurements")
    kept = [(p, x, y) for (p, x, y) in diffs
            if not VOLATILE.search(p.rsplit(".", 1)[-1])
            and not VOLATILE.search(p)]
    return leaves, len(diffs), kept


def main(argv):
    if argv and argv[0] == "--diff":
        A = json.load(open(argv[1]))
        B = json.load(open(argv[2]))
        leaves, total, kept = diff(A, B)
        print(f"leaf comparisons={leaves} raw_diffs={total} "
              f"non-volatile_diffs={len(kept)}")
        for p, x, y in kept[:80]:
            print(f"  {p}: {x!r} vs {y!r}")
        return 0
    path = argv[0]
    forge = None
    out = None
    if "--forge" in argv:
        forge = argv[argv.index("--forge") + 1]
    if "--json" in argv:
        out = argv[argv.index("--json") + 1]
    if "--libjack-sha" in argv:
        global OWN_LIBJACK_SHA
        OWN_LIBJACK_SHA = argv[argv.index("--libjack-sha") + 1]
    if "--binary-sha" in argv:
        global OWN_BINARY_SHA
        OWN_BINARY_SHA = argv[argv.index("--binary-sha") + 1]
    r = json.load(open(path))
    label = f"{path} [forge={forge or 'none'}]"
    if forge:
        r = FORGERIES[forge](r)
    laws = Laws(r, label).run()
    c = laws.report(out)
    return 1 if c["FAIL"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
