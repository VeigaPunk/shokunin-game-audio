#!/usr/bin/env python3
"""r94 VERIFIER — independent law re-derivation on a --probe-sox-r94 receipt.

The verifier reads ONLY the receipt's recorded fields and re-derives each
armed law from them.  The entry's own ``failures`` / ``coverage_blocked``
lists are never an input to a law (one explicit consistency cross-check at
the end compares the derived red set against them).

Statuses per law:
  PASS     the recorded fields satisfy the law
  FAIL     the recorded fields violate it (a real red)
  BLOCKED  the witness the law needs is absent/unparseable -> never a pass

Usage:
  r94v_laws.py RECEIPT.json [--forge NAME] [--json OUT]
Forgeries mutate a COPY of the receipt (never the file) so the same law set
can be asked whether it catches a fabricated receipt.
"""
import argparse
import copy
import json
import math
import sys

FORGES = (
    "none", "clear-failures", "flip-stable", "forge-sha", "forge-band",
    "pop-scout-ref", "forge-stim", "forge-metric", "forge-text",
    "pop-frames", "forge-scout-expect", "pop-coverage",
)


class Laws:
    def __init__(self, doc):
        self.doc = doc
        self.M = doc["measurements"]
        self.rows = []

    # ---------------------------------------------------------------- utils
    def E(self, name):
        e = self.M.get(name)
        if not isinstance(e, dict):
            self.add(f"{name}.present", False, "entry missing from receipt",
                     blocked=True)
            return {}
        return e

    def leg(self, entry, name):
        legs = entry.get("legs") or {}
        leg = legs.get(name)
        if not isinstance(leg, dict):
            return None
        return leg

    def add(self, law, cond, detail, blocked=False):
        st = "BLOCKED" if blocked else ("PASS" if cond else "FAIL")
        self.rows.append({"law": law, "status": st, "detail": str(detail)[:400]})
        return cond

    def near(self, a, b, tol):
        if a is None or b is None:
            return False
        if isinstance(a, (list, tuple)) or isinstance(b, (list, tuple)):
            a = a if isinstance(a, (list, tuple)) else [a]
            b = b if isinstance(b, (list, tuple)) else [b]
            if len(a) != len(b):
                return False
            return all(x is not None and y is not None and
                       abs(float(x) - float(y)) <= tol for x, y in zip(a, b))
        return abs(float(a) - float(b)) <= tol

    def met(self, leg, key, default=None):
        return ((leg or {}).get("metrics") or {}).get(key, default)

    def stim(self, entry, key):
        return ((entry.get("stimuli") or {}).get("sha256") or {}).get(key)

    def scout_ref_law(self, entry, legname, entry_tag):
        """The signature gate, re-derived: the recorded own sha must equal the
        recorded expected sha, and the witness must have been available."""
        leg = self.leg(entry, legname)
        if leg is None:
            return self.add(f"{entry_tag}.{legname}.scout_sha", False,
                            "leg missing", blocked=True)
        ref = leg.get("scout_ref")
        if not isinstance(ref, dict):
            return self.add(f"{entry_tag}.{legname}.scout_sha", False,
                            "no scout_ref recorded -> witness not armed",
                            blocked=True)
        exp = ref.get("expected_sha256")
        if exp is None:
            return self.add(f"{entry_tag}.{legname}.scout_sha", False,
                            f"{ref.get('key')}: no recorded expected sha -> "
                            "witness not armed", blocked=True)
        own = leg.get("out_sha256")
        ok = own == exp
        return self.add(f"{entry_tag}.{legname}.scout_sha", ok,
                        f"{ref.get('key')}: own {str(own)[:16]} vs expected "
                        f"{str(exp)[:16]} (available="
                        f"{ref.get('receipt_available')})")

    def scout_metric_law(self, entry, legname, entry_tag, keys, tol):
        leg = self.leg(entry, legname)
        if leg is None:
            return self.add(f"{entry_tag}.{legname}.scout_metric", False,
                            "leg missing", blocked=True)
        ref = leg.get("scout_metric_ref")
        if not isinstance(ref, dict) or not ref.get("compared"):
            return self.add(f"{entry_tag}.{legname}.scout_metric", False,
                            "no cross-seat metric comparison recorded",
                            blocked=True)
        bad = []
        for k in keys:
            c = (ref["compared"] or {}).get(k)
            if c is None:
                bad.append(f"{k}: absent")
                continue
            a, b = c.get("own"), c.get("scout")
            if isinstance(a, list) and isinstance(b, list):
                ok = (len(a) == len(b) and
                      all(x is not None and y is not None and
                          abs(float(x) - float(y)) <= tol
                          for x, y in zip(a, b)))
            elif isinstance(a, (int, float)) and isinstance(b, (int, float)):
                ok = abs(float(a) - float(b)) <= tol
            else:
                ok = a == b
            if not ok:
                bad.append(f"{k}: own {a} vs scout {b} tol {tol}")
        return self.add(f"{entry_tag}.{legname}.scout_metric", not bad,
                        f"{ref.get('key')}: " + ("all compared" if not bad
                                                 else "; ".join(bad)))

    def census_law(self, entry, entry_tag):
        for side in ("pw_census_entry", "pw_census_exit"):
            cen = entry.get(side)
            if not isinstance(cen, dict):
                self.add(f"{entry_tag}.{side}.file_only", False,
                         "census missing", blocked=True)
                continue
            objs = cen.get("own_objects") or []
            mods = cen.get("own_modules") or []
            unreadable = cen.get("unreadable") or []
            self.add(f"{entry_tag}.{side}.file_only",
                     not objs and not mods,
                     f"own_objects={objs} own_modules={mods} "
                     f"unreadable={unreadable}")

    # ------------------------------------------------------------- entries
    def det(self):
        t = "det"
        e = self.E("sox_det_r94_probe")
        if not e:
            return
        # stimulus signature gate (9 stimuli)
        sm = (e.get("stimuli") or {}).get("scout_sha_match") or {}
        prep = (e.get("stimuli") or {}).get("scout_prep_available")
        for k in ("a", "b", "c", "c2", "f", "h", "i", "j", "r"):
            if k in sm:
                self.add(f"{t}.stim_{k}.scout_sha", bool(sm[k]),
                         f"rebuilt stimulus {k} vs scout prep.json")
            else:
                self.add(f"{t}.stim_{k}.scout_sha", False,
                         "no scout prep sha recorded -> not armed", blocked=True)
        self.add(f"{t}.stim_prep_available", bool(prep),
                 f"scout prep.json readable={prep}")
        # determinism classes
        for name, want in (("det_gain_m6_default", "multi"),
                           ("det_dither_explicit_default", "multi"),
                           ("det_dither_explicit_D", "multi"),
                           ("det_f32_to_s16_plain", "multi"),
                           ("det_concurrency_default", "multi")):
            leg = self.leg(e, name)
            if leg is None:
                self.add(f"{t}.{name}", False, "leg missing", blocked=True)
                continue
            shas = leg.get("out_sha256_all") or []
            nd = leg.get("n_distinct_shas")
            real = len({s for s in shas if s})
            self.add(f"{t}.{name}.nondeterministic", real >= 2,
                     f"distinct={real} recorded n_distinct_shas={nd}")
            self.add(f"{t}.{name}.count_consistent", real == nd,
                     f"out_sha256_all distinct {real} vs n_distinct_shas {nd}")
        for name in ("det_gain_m6_D", "det_dither_explicit_R",
                     "det_s16_to_s24_gain", "det_f32_to_s24",
                     "det_f32_to_s32", "det_concurrency_D",
                     "det_concurrency_R_dither"):
            leg = self.leg(e, name)
            if leg is None:
                self.add(f"{t}.{name}", False, "leg missing", blocked=True)
                continue
            shas = leg.get("out_sha256_all") or []
            real = len({s for s in shas if s})
            self.add(f"{t}.{name}.stable", real == 1 and shas and shas[0],
                     f"distinct={real} stable_field={leg.get('stable')}")
            self.add(f"{t}.{name}.stable_field_consistent",
                     bool(leg.get("stable")) == (real == 1 and bool(shas and shas[0])),
                     f"stable={leg.get('stable')} distinct={real}")
        # -R -D == -R
        a, b = self.leg(e, "det_dither_R_D"), self.leg(e, "det_dither_explicit_R")
        if a and b:
            self.add(f"{t}.dither_R_D_eq_R",
                     a.get("out_sha256") == b.get("out_sha256") and
                     a.get("out_sha256") is not None,
                     f"{str(a.get('out_sha256'))[:16]} vs "
                     f"{str(b.get('out_sha256'))[:16]}")
        # identity legs vs their stimulus sha
        for name, stimkey in (("det_gain0_identity", "a"),
                              ("det_passthrough_identity", "a"),
                              ("det_rate_same_identity", "b"),
                              ("det_pad_pct50_identity", "b")):
            leg = self.leg(e, name)
            exp = self.stim(e, stimkey)
            if leg is None or exp is None:
                self.add(f"{t}.{name}.input_identity", False,
                         "leg or stimulus sha missing", blocked=True)
                continue
            self.add(f"{t}.{name}.input_identity",
                     leg.get("out_sha256") == exp,
                     f"own {str(leg.get('out_sha256'))[:16]} vs stim {stimkey} "
                     f"{exp[:16]}")
        # copy token is not an effect
        leg = self.leg(e, "det_copy_token_not_an_effect")
        if leg:
            err = ((leg.get("reps") or [{}])[0]).get("stderr") or ""
            self.add(f"{t}.copy_token_not_effect",
                     leg.get("rc") == 2 and "can't open input file" in err,
                     f"rc={leg.get('rc')} stderr={err[:120]!r}")
        # flag order / buffer / env invariance
        for name, label in (("det_flag_order", "flag_order"),
                            ("det_buffer_invariant", "buffer"),
                            ("det_env_invariant", "env")):
            leg = self.leg(e, name)
            if leg is None:
                self.add(f"{t}.{label}_invariant", False, "leg missing",
                         blocked=True)
                continue
            vals = {s for s in (leg.get("variants") or {}).values() if s}
            self.add(f"{t}.{label}_invariant", len(vals) == 1,
                     f"{len(vals)} distinct sha(s) over "
                     f"{len(leg.get('variants') or {})} variants")
            self.add(f"{t}.{label}_count_consistent",
                     len(vals) == leg.get("n_distinct_shas"),
                     f"derived {len(vals)} vs recorded "
                     f"{leg.get('n_distinct_shas')}")
        # gopt-after-effect refusals
        for name, want in (("det_flag_after_effect", "sox_r94_usage"),
                           ("det_flag_after_dither", "sox_r94_opt")):
            leg = self.leg(e, name)
            if leg is None:
                self.add(f"{t}.{name}", False, "leg missing", blocked=True)
                continue
            cls = ((leg.get("reps") or [{}])[0]).get("error_class")
            self.add(f"{t}.{name}", leg.get("rc") == 1 and cls == want,
                     f"rc={leg.get('rc')} class={cls} want={want}")
        # concurrency rc sanity
        for name in ("det_concurrency_D", "det_concurrency_R_dither",
                     "det_concurrency_default"):
            leg = self.leg(e, name)
            if leg is None:
                continue
            rcs = leg.get("rcs") or []
            self.add(f"{t}.{name}.rcs_zero",
                     len(rcs) == leg.get("concurrency") and
                     all(r == 0 for r in rcs),
                     f"{len(rcs)} rcs, non-zero="
                     f"{[r for r in rcs if r != 0]}")
        # scout signature witnesses
        for legname in ("det_gain_m6_D", "det_gain0_identity",
                        "det_passthrough_identity", "det_pad_pct50_identity"):
            self.scout_ref_law(e, legname, t)
        self.census_law(e, t)

    def gain(self):
        t = "gain"
        e = self.E("sox_gain_r94_probe")
        if not e:
            return
        leg = self.leg(e, "gain_m6_rint")
        if leg:
            self.add(f"{t}.gain_m6_rint.rounding",
                     leg.get("mismatch_vs_rint_formula") == 0,
                     f"mismatch={leg.get('mismatch_vs_rint_formula')}")
            self.add(f"{t}.gain_m6_rint.peaks",
                     self.near(self.met(leg, "peak_db"),
                               [-12.0211, -18.0406], 5e-4),
                     f"peak_db={self.met(leg, 'peak_db')}")
        leg = self.leg(e, "gain_p6_rint")
        if leg:
            self.add(f"{t}.gain_p6_rint.rounding",
                     leg.get("mismatch_vs_rint_formula") == 0,
                     f"mismatch={leg.get('mismatch_vs_rint_formula')}")
        leg = self.leg(e, "vol_amp_0.5")
        if leg:
            self.add(f"{t}.vol_amp_0.5.ceil",
                     leg.get("mismatch_vs_ceil") == 0,
                     f"mismatch_vs_ceil={leg.get('mismatch_vs_ceil')}")
            self.add(f"{t}.vol_amp_0.5.not_rint",
                     (leg.get("mismatch_vs_rint_formula") or 0) > 0,
                     f"mismatch_vs_rint={leg.get('mismatch_vs_rint_formula')} "
                     "(must be > 0: the discriminator)")
        for name in ("vol_db_m6_0206", "vol_pow_0.5"):
            leg = self.leg(e, name)
            if leg:
                self.add(f"{t}.{name}.rint",
                         leg.get("mismatch_vs_rint_formula") == 0,
                         f"mismatch={leg.get('mismatch_vs_rint_formula')}")
        d = self.leg(e, "vol_spelling_delta")
        if d:
            self.add(f"{t}.vol_spelling_delta",
                     (d.get("n_diff_samples") or 0) > 0 and
                     d.get("max_abs_diff_lsb") == 1.0 and
                     d.get("same_sha") is False,
                     f"n_diff={d.get('n_diff_samples')} "
                     f"max_lsb={d.get('max_abs_diff_lsb')} "
                     f"same_sha={d.get('same_sha')}")
        a, b = self.leg(e, "global_v_0.5"), self.leg(e, "vol_amp_0.5")
        if a and b:
            self.add(f"{t}.global_v_eq_vol_amp",
                     a.get("out_sha256") == b.get("out_sha256") and
                     a.get("out_sha256") is not None,
                     "global -v 0.5 vs vol 0.5")
        leg = self.leg(e, "gain_n_normalize")
        if leg:
            self.add(f"{t}.gain_n_normalize",
                     self.near(self.met(leg, "peak_db"), [0.0, -6.0206], 5e-4),
                     f"peak_db={self.met(leg, 'peak_db')}")
        for name in ("gain_e_lift", "gain_b_lift"):
            leg = self.leg(e, name)
            if leg:
                self.add(f"{t}.{name}",
                         self.near(self.met(leg, "peak_db"),
                                   [-6.0206, -6.0206], 5e-4),
                         f"peak_db={self.met(leg, 'peak_db')}")
        a, b = self.leg(e, "gain_e_lift"), self.leg(e, "gain_b_lift")
        if a and b:
            self.add(f"{t}.gain_e_eq_b",
                     a.get("out_sha256") == b.get("out_sha256") and
                     a.get("out_sha256") is not None, "gain -e vs gain -b bytes")
        g = self.leg(e, "guard_not_limiter")
        if g:
            self.add(f"{t}.guard_not_limiter",
                     g.get("clipped_gain12_D") is not None and
                     g.get("clipped_gain12_D") == g.get("clipped_G_gain12_D") and
                     (g.get("clipped_gain12_D") or 0) > 0,
                     f"plain={g.get('clipped_gain12_D')} "
                     f"guarded={g.get('clipped_G_gain12_D')}")
        leg = self.leg(e, "chain_gain_then_norm")
        if leg:
            pk = self.met(leg, "peak_db") or [None]
            self.add(f"{t}.chain_gain_then_norm",
                     self.near(pk[0], -3.0, 5e-3), f"peak[0]={pk[0]}")
        leg = self.leg(e, "chain_norm_then_gain")
        if leg:
            pk = self.met(leg, "peak_db") or [None]
            self.add(f"{t}.chain_norm_then_gain",
                     self.near(pk[0], -8.9996, 5e-3), f"peak[0]={pk[0]}")
        for legname in ("gain_m6_rint", "gain_p6_rint", "gain_n_normalize",
                        "gain_e_lift", "vol_amp_0.5", "vol_db_m6_0206",
                        "chain_gain_then_norm", "chain_norm_then_gain"):
            self.scout_ref_law(e, legname, t)
        for legname, keys, tol in (("gain_m6_rint",
                                    ("mismatch_vs_rint_formula",
                                     "max_abs_diff_vs_formula", "peak_db"),
                                    5e-4),
                                   ("chain_gain_then_norm",
                                    ("peak_db", "rms_db"), 5e-4),
                                   ("chain_norm_then_gain",
                                    ("peak_db", "rms_db"), 5e-4)):
            self.scout_metric_law(e, legname, t, keys, tol)
        self.census_law(e, t)

    def rate(self):
        t = "rate"
        e = self.E("sox_rate_r94_probe")
        if not e:
            return
        rows = (("len_12000_to_44100", 12000, 44100),
                ("len_12001_to_44100", 12001, 44100),
                ("len_12000_to_22050", 12000, 22050),
                ("len_12000_to_24050", 12000, 24050),
                ("len_12000_to_11025", 12000, 11025),
                ("len_12000_to_32000", 12000, 32000))
        fitted = {"floor": [], "round": [], "ceil": []}
        for name, inf, orate in rows:
            leg = self.leg(e, name)
            if leg is None:
                self.add(f"{t}.{name}.length", False, "leg missing",
                         blocked=True)
                continue
            frames = self.met(leg, "frames")
            exact = inf * orate / 48000.0
            ok = frames is not None and abs(frames - exact) <= 1.0
            self.add(f"{t}.{name}.length", ok,
                     f"frames={frames} exact={exact:.4f} "
                     f"recorded_delta={leg.get('delta_vs_exact')}")
            for rule, val in (("floor", math.floor(exact)),
                              ("round", int(round(exact))),
                              ("ceil", math.ceil(exact))):
                if frames == val:
                    fitted[rule].append(name)
        half = ("len_12000_to_22050", "len_12001_to_44100", "len_12000_to_24050")
        allfit = [r for r, ns in fitted.items() if all(n in ns for n in half)]
        leg = self.leg(e, "len_rounding_rules")
        if leg:
            self.add(f"{t}.no_single_rounding_rule",
                     leg.get("rules_fitting_all_half_rows") == [],
                     f"recorded={leg.get('rules_fitting_all_half_rows')} "
                     f"derived={allfit}")
        leg = self.leg(e, "rate_same_identity")
        if leg:
            exp = self.stim(e, "b")
            self.add(f"{t}.rate_same_identity",
                     exp is not None and leg.get("out_sha256") == exp,
                     f"own {str(leg.get('out_sha256'))[:16]} vs stim b "
                     f"{str(exp)[:16]}")
        leg = self.leg(e, "rate_pitch_preserved")
        if leg:
            pk = leg.get("peak_hz") or {}
            inp = pk.get("input_hz")
            vals = [v for k, v in pk.items() if k != "input_hz" and v is not None]
            self.add(f"{t}.rate_pitch_preserved",
                     inp is not None and bool(vals) and
                     all(abs(v - inp) <= 3.0 for v in vals),
                     f"input={inp} out={{{', '.join(f'{k}:{v}' for k, v in pk.items() if k != 'input_hz')}}}")
        # alias lattice
        d23 = self.leg(e, "alias_23k_default")
        q23 = self.leg(e, "alias_23k_q")
        a23 = self.leg(e, "alias_23k_a")
        m23 = self.leg(e, "alias_23k_m_a")
        v23 = self.leg(e, "alias_23k_v")
        h23 = self.leg(e, "alias_23k_h")
        u23 = self.leg(e, "alias_23k_u")
        d20 = self.leg(e, "alias_20k_default")
        if q23:
            self.add(f"{t}.alias_23k_q.hazard",
                     q23.get("band_21100hz_db") is not None and
                     q23["band_21100hz_db"] > -20.0 and
                     q23.get("peak_db_overall") is not None and
                     abs(q23["band_21100hz_db"] - q23["peak_db_overall"]) < 3.0,
                     f"band={q23.get('band_21100hz_db')} "
                     f"peak={q23.get('peak_db_overall')}")
        if d23:
            self.add(f"{t}.alias_23k_default.rejects",
                     d23.get("band_21100hz_db") is not None and
                     d23.get("peak_db_overall") is not None and
                     d23["band_21100hz_db"] < d23["peak_db_overall"] - 10.0,
                     f"band={d23.get('band_21100hz_db')} "
                     f"peak={d23.get('peak_db_overall')}")
        if h23 and d23:
            self.add(f"{t}.alias_23k_h_eq_default",
                     h23.get("out_sha256") == d23.get("out_sha256") and
                     h23.get("band_21100hz_db") == d23.get("band_21100hz_db"),
                     "bytes + band")
        if v23 and d23:
            self.add(f"{t}.alias_23k_v_same_level_as_default",
                     v23.get("band_21100hz_db") is not None and
                     d23.get("band_21100hz_db") is not None and
                     abs(v23["band_21100hz_db"] - d23["band_21100hz_db"]) < 1.0,
                     f"v={v23.get('band_21100hz_db')} "
                     f"default={d23.get('band_21100hz_db')}")
            self.add(f"{t}.alias_23k_v_distinct_bytes",
                     v23.get("out_sha256") != d23.get("out_sha256") and
                     v23.get("out_sha256") is not None,
                     "the falsified claim's replacement half")
        if u23 and v23:
            self.add(f"{t}.alias_23k_u_eq_v",
                     u23.get("out_sha256") == v23.get("out_sha256") and
                     u23.get("out_sha256") is not None, "-u vs -v bytes")
        if a23:
            self.add(f"{t}.alias_23k_a.band",
                     a23.get("band_21100hz_db") is not None and
                     -100.0 < a23["band_21100hz_db"] < -60.0,
                     f"band={a23.get('band_21100hz_db')}")
        if m23:
            self.add(f"{t}.alias_23k_m_a.band",
                     m23.get("band_21100hz_db") is not None and
                     -95.0 < m23["band_21100hz_db"] < -60.0,
                     f"band={m23.get('band_21100hz_db')}")
        if d20:
            self.add(f"{t}.alias_20k_default.130db_home",
                     d20.get("band_21100hz_db") is not None and
                     d20["band_21100hz_db"] < -120.0,
                     f"band={d20.get('band_21100hz_db')}")
            self.add(f"{t}.alias_20k_default.below_110",
                     d20.get("band_21100hz_db") is not None and
                     d20["band_21100hz_db"] < -110.0,
                     f"band={d20.get('band_21100hz_db')}")
        guard = self.leg(e, "rate_130db_home")
        if guard:
            bands = [x.get("band_21100hz_db") for x in (d23, v23, q23, a23, m23)
                     if isinstance(x, dict)]
            bands = [b for b in bands if b is not None]
            self.add(f"{t}.rate_130db_home.no_23k_near_130",
                     bool(bands) and min(bands) > -110.0,
                     f"worst 23 kHz band={min(bands) if bands else None}")
            self.add(f"{t}.rate_130db_home.20k_carries_it",
                     (guard.get("armed_corrected") or {})
                     .get("20k_default_band_21100hz_db") is not None and
                     guard["armed_corrected"]["20k_default_band_21100hz_db"] < -120.0,
                     f"recorded="
                     f"{(guard.get('armed_corrected') or {}).get('20k_default_band_21100hz_db')}")
        l20, a20 = self.leg(e, "alias_20k_l"), self.leg(e, "alias_20k_a")
        if l20:
            self.add(f"{t}.alias_20k_l.hole",
                     l20.get("band_20000hz_db") is not None and
                     l20["band_20000hz_db"] < -10.0,
                     f"band_20000={l20.get('band_20000hz_db')}")
        if a20:
            self.add(f"{t}.alias_20k_a.flat",
                     a20.get("band_20000hz_db") is not None and
                     abs(a20["band_20000hz_db"]) < 1.5,
                     f"band_20000={a20.get('band_20000hz_db')}")
            self.add(f"{t}.alias_20k_a.best_rejection",
                     a20.get("band_21100hz_db") is not None and
                     a20["band_21100hz_db"] < -110.0,
                     f"band_21100={a20.get('band_21100hz_db')}")
        leg = self.leg(e, "rate_q_a_refusal")
        if leg:
            err = ((leg.get("reps") or [{}])[0]).get("stderr") or ""
            self.add(f"{t}.rate_q_a_refusal",
                     leg.get("rc") == 1 and
                     "override options only work at higher quality levels" in err,
                     f"rc={leg.get('rc')} stderr={err[:120]!r}")
        for legname in ("len_12000_to_44100", "len_12001_to_44100",
                        "len_12000_to_22050", "len_12000_to_24050",
                        "len_12000_to_11025", "rate_same_identity",
                        "alias_23k_default", "alias_23k_q", "alias_23k_a",
                        "alias_23k_m_a", "alias_20k_default"):
            self.scout_ref_law(e, legname, t)
        for legname, keys, tol in (("len_12000_to_44100", ("frames",), 0.05),
                                   ("len_12001_to_44100", ("frames",), 0.05),
                                   ("len_12000_to_22050", ("frames",), 0.05),
                                   ("len_12000_to_24050", ("frames",), 0.05),
                                   ("len_12000_to_11025", ("frames",), 0.05),
                                   ("alias_23k_default",
                                    ("band_21100hz_db", "band_20000hz_db",
                                     "peak_db"), 0.05),
                                   ("alias_23k_q",
                                    ("band_21100hz_db", "band_20000hz_db",
                                     "peak_db"), 0.05),
                                   ("alias_23k_a",
                                    ("band_21100hz_db", "peak_db"), 0.05),
                                   ("alias_23k_m_a",
                                    ("band_21100hz_db", "peak_db"), 0.05),
                                   ("alias_20k_default",
                                    ("band_21100hz_db", "band_20000hz_db",
                                     "peak_db"), 0.05)):
            self.scout_metric_law(e, legname, t, keys, tol)
        self.census_law(e, t)

    def remix(self):
        t = "remix"
        e = self.E("sox_remix_r94_probe")
        if not e:
            return
        for name in ("remix_1_selects_L", "remix_1_2_auto", "channels_1",
                     "remix_m_1_2", "remix_p_1_2", "remix_swap_2_1",
                     "remix_left_only", "remix_0_1_zero_then_in1",
                     "remix_v_half"):
            leg = self.leg(e, name)
            if leg is None:
                self.add(f"{t}.{name}.sample_exact", False, "leg missing",
                         blocked=True)
                continue
            self.add(f"{t}.{name}.sample_exact", leg.get("mismatch") == 0,
                     f"mismatch={leg.get('mismatch')} "
                     f"max={leg.get('max_abs_diff')}")
        leg = self.leg(e, "remix_1_selects_L")
        if leg:
            self.add(f"{t}.remix_1_not_mean",
                     (leg.get("mismatch_vs_mean") or 0) > 0,
                     f"mismatch_vs_mean={leg.get('mismatch_vs_mean')}")
        leg = self.leg(e, "remix_1_2_auto")
        if leg:
            self.add(f"{t}.downmix_not_nearest_even",
                     (leg.get("mismatch_vs_nearest_even") or 0) > 0,
                     f"mismatch_vs_nearest_even="
                     f"{leg.get('mismatch_vs_nearest_even')}")
        a, b = self.leg(e, "channels_1"), self.leg(e, "remix_1_2_auto")
        if a and b:
            self.add(f"{t}.channels_1_eq_remix_1_2",
                     a.get("out_sha256") == b.get("out_sha256") and
                     a.get("out_sha256") is not None, "bytes")
        a, b = self.leg(e, "remix_v_half"), self.leg(e, "remix_vol_control")
        if a and b:
            self.add(f"{t}.remix_v_half_eq_vol_half",
                     a.get("out_sha256") == b.get("out_sha256") and
                     a.get("out_sha256") is not None,
                     "remix 1v0.5 2v0.5 vs vol 0.5 bytes")
        leg = self.leg(e, "remix_p_minus6")
        if leg:
            self.add(f"{t}.remix_p_minus6",
                     self.near(self.met(leg, "peak_db"), [-12.0211], 5e-4),
                     f"peak_db={self.met(leg, 'peak_db')}")
        leg = self.leg(e, "mono_to_stereo_1_1")
        if leg:
            self.add(f"{t}.mono_to_stereo_1_1",
                     self.met(leg, "channels") == 2 and
                     leg.get("mismatch_ch0") == 0 and leg.get("mismatch_ch1") == 0,
                     f"channels={self.met(leg, 'channels')} "
                     f"m0={leg.get('mismatch_ch0')} m1={leg.get('mismatch_ch1')}")
        for legname in ("remix_1_2_auto", "channels_1", "remix_m_1_2",
                        "remix_p_1_2", "remix_swap_2_1", "remix_left_only",
                        "remix_0_1_zero_then_in1", "remix_v_half",
                        "remix_p_minus6", "mono_to_stereo_1_1"):
            self.scout_ref_law(e, legname, t)
        self.census_law(e, t)

    def trim(self):
        t = "trim"
        e = self.E("sox_trim_r94_probe")
        if not e:
            return
        leg = self.leg(e, "trim_0_1s")
        if leg:
            self.add(f"{t}.trim_0_1s.is_one_sample",
                     self.met(leg, "frames") == 1,
                     f"frames={self.met(leg, 'frames')} (the s suffix is SAMPLES)")
        leg = self.leg(e, "trim_0_4800s")
        if leg:
            self.add(f"{t}.trim_0_4800s", self.met(leg, "frames") == 4800,
                     f"frames={self.met(leg, 'frames')}")
        leg = self.leg(e, "trim_0_1e-9")
        if leg:
            self.add(f"{t}.trim_0_1e-9.refusal", leg.get("rc") == 1,
                     f"rc={leg.get('rc')}")
        leg = self.leg(e, "trim_0_1sec")
        if leg:
            cls = ((leg.get("reps") or [{}])[0]).get("error_class")
            self.add(f"{t}.trim_0_1sec.refusal",
                     leg.get("rc") == 1 and cls == "sox_r94_parse",
                     f"rc={leg.get('rc')} class={cls}")
        mat = self.leg(e, "trim_rounding_matrix")
        if mat:
            bad = []
            for k, frames in (mat.get("frames") or {}).items():
                want = round(float(k) * 48000)
                if frames is None or abs(frames - want) > 1:
                    bad.append(f"{k}:{frames}!={want}")
            self.add(f"{t}.trim_rounding_matrix", not bad,
                     f"out-of-tolerance={bad}")
        forms = (("trim_0_0.1", 4800), ("trim_0.1", 7200),
                 ("trim_0_minus0.1", 7200), ("trim_0_eq0.1", 4800),
                 ("trim_0.05_plus0.05", 7200), ("trim_0_100", 12000),
                 ("trim_0_0", 0))
        for name, want in forms:
            leg = self.leg(e, name)
            if leg is None:
                self.add(f"{t}.{name}.frames", False, "leg missing",
                         blocked=True)
                continue
            self.add(f"{t}.{name}.frames", self.met(leg, "frames") == want,
                     f"frames={self.met(leg, 'frames')} want={want}")
        leg = self.leg(e, "trim_0_100")
        if leg:
            err = ((leg.get("reps") or [{}])[0]).get("stderr") or ""
            self.add(f"{t}.trim_0_100.warns",
                     "End position is after expected end of audio" in err,
                     f"stderr={err[:120]!r}")
        leg = self.leg(e, "trim_0_0.1")
        if leg:
            self.add(f"{t}.trim_0_0.1.sample_exact_head",
                     leg.get("mismatch_vs_input_head") == 0,
                     f"mismatch_vs_input_head={leg.get('mismatch_vs_input_head')}")
        for legname in ("trim_round_0_09997917", "trim_0_0.1", "trim_0.1",
                        "trim_0_minus0.1", "trim_0_eq0.1", "trim_0_100",
                        "trim_0_0"):
            self.scout_ref_law(e, legname, t)
        self.census_law(e, t)

    def fade(self):
        t = "fade"
        e = self.E("sox_fade_r94_probe")
        if not e:
            return
        for name, want in (("fade_stop_0.15_len_0.1", 7200),
                           ("fade_stop_0.2_len_0.05", 9600),
                           ("fade_stop_0.25_len_0.1", 12000)):
            leg = self.leg(e, name)
            if leg is None:
                self.add(f"{t}.{name}.truncates", False, "leg missing",
                         blocked=True)
                continue
            self.add(f"{t}.{name}.truncates", self.met(leg, "frames") == want,
                     f"frames={self.met(leg, 'frames')} want={want}")
        leg = self.leg(e, "fade_log_100db")
        if leg:
            meas = leg.get("envelope_measured") or {}
            want = leg.get("envelope_expected") or {}
            bad = [x for x in want
                   if meas.get(x) is None or want.get(x) in (None, 0) or
                   abs(meas[x] - want[x]) / want[x] > 0.03]
            self.add(f"{t}.fade_log_100db", not bad,
                     f"measured={meas} expected={want} bad={bad}")
            self.add(f"{t}.fade_log_100db.first_frame_zero",
                     leg.get("first_out_sample") == 0,
                     f"first_out_sample={leg.get('first_out_sample')}")
        tab = self.leg(e, "fade_curve_table")
        if tab:
            bad = []
            for ctype, cell in (tab.get("table") or {}).items():
                got, exp = cell.get("measured") or {}, cell.get("expected") or {}
                for x, e_v in exp.items():
                    if got.get(x) is None or e_v in (None, 0) or \
                            abs(got[x] - e_v) / e_v > 0.03:
                        bad.append(f"{ctype}@{x}:{got.get(x)}!={e_v}")
            self.add(f"{t}.fade_curve_table", not bad,
                     f"out-of-tolerance={bad}")
        a, b = self.leg(e, "fade_default_type"), self.leg(e, "fade_log_100db")
        if a and b:
            self.add(f"{t}.fade_default_is_l",
                     a.get("out_sha256") == b.get("out_sha256") and
                     a.get("out_sha256") is not None, "default vs explicit l")
        for legname in ("fade_stop_0.15_len_0.1", "fade_stop_0.2_len_0.05",
                        "fade_log_100db", "fade_curve_q", "fade_curve_h",
                        "fade_curve_t", "fade_curve_p", "fade_curve_s",
                        "fade_default_type"):
            self.scout_ref_law(e, legname, t)
        self.census_law(e, t)

    def rps(self):
        t = "rps"
        e = self.E("sox_repeat_pad_silence_r94_probe")
        if not e:
            return
        leg = self.leg(e, "repeat_2")
        if leg:
            self.add(f"{t}.repeat_2.is_three_copies",
                     self.met(leg, "frames") == 36000 and
                     leg.get("mismatch_vs_tiling") == 0,
                     f"frames={self.met(leg, 'frames')} "
                     f"tiling_mismatch={leg.get('mismatch_vs_tiling')}")
        leg = self.leg(e, "repeat_0")
        if leg:
            exp = self.stim(e, "b")
            self.add(f"{t}.repeat_0.identity",
                     exp is not None and leg.get("out_sha256") == exp,
                     f"own {str(leg.get('out_sha256'))[:16]} vs stim b")
        leg = self.leg(e, "repeat_neg1")
        if leg:
            self.add(f"{t}.repeat_neg1.refusal", leg.get("rc") == 1,
                     f"rc={leg.get('rc')}")
        leg = self.leg(e, "pad_0.1_0.2")
        if leg:
            self.add(f"{t}.pad_0.1_0.2",
                     self.met(leg, "frames") == 12000 + 4800 + 9600 and
                     leg.get("first_nonzero_frame") == 4801 and
                     leg.get("last_nonzero_frame") == 16799,
                     f"frames={self.met(leg, 'frames')} "
                     f"first_nz={leg.get('first_nonzero_frame')} "
                     f"last_nz={leg.get('last_nonzero_frame')}")
        leg = self.leg(e, "pad_0.05_at_0.05")
        if leg:
            self.add(f"{t}.pad_0.05_at_0.05",
                     self.met(leg, "frames") == 12000 + 2400,
                     f"frames={self.met(leg, 'frames')}")
        leg = self.leg(e, "pad_pct50")
        if leg:
            exp = self.stim(e, "b")
            self.add(f"{t}.pad_pct50.silent_noop",
                     exp is not None and leg.get("out_sha256") == exp,
                     f"own {str(leg.get('out_sha256'))[:16]} vs stim b")
        leg = self.leg(e, "silence_above_only")
        if leg:
            self.add(f"{t}.silence_above_only.leading_cut",
                     self.met(leg, "frames") == 21600 - 4804,
                     f"frames={self.met(leg, 'frames')} want={21600 - 4804}")
            self.add(f"{t}.silence_above_only.trailing_kept",
                     leg.get("trailing_zero_frames") == 7200,
                     f"trailing={leg.get('trailing_zero_frames')}")
        leg = self.leg(e, "silence_both_0.1")
        if leg:
            self.add(f"{t}.silence_both.window_lag",
                     leg.get("trailing_zero_frames") == 959,
                     f"trailing={leg.get('trailing_zero_frames')} want=959")
            self.add(f"{t}.silence_both.frames",
                     self.met(leg, "frames") == 21600 - 4804 - (7200 - 959),
                     f"frames={self.met(leg, 'frames')} "
                     f"want={21600 - 4804 - (7200 - 959)}")
        leg = self.leg(e, "silence_both_leave")
        if leg:
            self.add(f"{t}.silence_both_leave.keeps_duration_plus_lag",
                     leg.get("trailing_zero_frames") == 959 + 4800,
                     f"trailing={leg.get('trailing_zero_frames')} want=5759")
        leg = self.leg(e, "silence_zero_periods")
        if leg:
            self.add(f"{t}.silence_zero_periods.refusal", leg.get("rc") == 1,
                     f"rc={leg.get('rc')}")
        for name in ("silence_thresh_frac", "silence_thresh_db"):
            leg = self.leg(e, name)
            if leg:
                self.add(f"{t}.{name}.accepted", leg.get("rc") == 0,
                         f"rc={leg.get('rc')}")
        for legname in ("repeat_2", "repeat_0", "pad_0.1_0.2", "pad_pct50",
                        "silence_above_only", "silence_both_0.1",
                        "silence_both_leave", "silence_thresh_frac",
                        "silence_thresh_db"):
            self.scout_ref_law(e, legname, t)
        self.census_law(e, t)

    def dither(self):
        t = "dither"
        e = self.E("sox_dither_stat_r94_probe")
        if not e:
            return
        leg = self.leg(e, "dither_s_R")
        if leg:
            self.add(f"{t}.dither_s_R.envelope",
                     leg.get("max_abs_err") is not None and
                     15 <= leg["max_abs_err"] <= 30 and
                     leg.get("err_rms") is not None and
                     5.70 <= leg["err_rms"] <= 5.78,
                     f"max={leg.get('max_abs_err')} rms={leg.get('err_rms')}")
            self.add(f"{t}.dither_s_R.stable", bool(leg.get("stable")),
                     f"stable={leg.get('stable')} "
                     f"distinct={len({s for s in (leg.get('out_sha256_all') or []) if s})}")
        leg = self.leg(e, "dither_p12_R")
        if leg:
            self.add(f"{t}.dither_p12_R.envelope",
                     leg.get("max_abs_err") is not None and
                     15 <= leg["max_abs_err"] <= 30,
                     f"max={leg.get('max_abs_err')} rms={leg.get('err_rms')}")
        leg = self.leg(e, "guard_default_path_row")
        if leg:
            self.add(f"{t}.guard_default_path_row.recorded_positive",
                     (leg.get("railed_gain12_default") or 0) > 0 and
                     (leg.get("railed_G_gain12_default") or 0) > 0,
                     f"plain={leg.get('railed_gain12_default')} "
                     f"guarded={leg.get('railed_G_gain12_default')}")
        leg = self.leg(e, "stat_plain_a")
        if leg:
            f = leg.get("fields") or {}
            self.add(f"{t}.stat_plain_a.text_stable", bool(leg.get("stable")),
                     f"n_distinct_text_shas={leg.get('n_distinct_text_shas')}")
            if "RMS amplitude" in f:
                self.add(f"{t}.stat_plain_a.rms_is_interleaved_qmean",
                         self.near(float(f["RMS amplitude"]),
                                   leg.get("numpy_rms_quadratic_mean"), 1e-5),
                         f"sox={f['RMS amplitude']} numpy="
                         f"{leg.get('numpy_rms_quadratic_mean')}")
            else:
                self.add(f"{t}.stat_plain_a.rms_is_interleaved_qmean", False,
                         "no RMS amplitude field", blocked=True)
            if "Maximum delta" in f:
                self.add(f"{t}.stat_plain_a.delta_interleaved",
                         self.near(float(f["Maximum delta"]),
                                   leg.get("numpy_max_interleaved_delta"), 1e-5),
                         f"sox={f['Maximum delta']} numpy="
                         f"{leg.get('numpy_max_interleaved_delta')}")
            else:
                self.add(f"{t}.stat_plain_a.delta_interleaved", False,
                         "no Maximum delta field", blocked=True)
            if "Volume adjustment" in f:
                self.add(f"{t}.stat_plain_a.volume_adjustment",
                         float(f["Volume adjustment"]) == 2.0,
                         f"value={f['Volume adjustment']}")
        leg = self.leg(e, "stat_v_a")
        if leg:
            self.add(f"{t}.stat_v_a.only_number",
                     (leg.get("only_number") or "").strip() == "2.000",
                     f"only_number={leg.get('only_number')!r}")
        leg = self.leg(e, "stats_j_a")
        if leg:
            j = leg.get("json") or {}
            ch0 = leg.get("channel0") or {}
            self.add(f"{t}.stats_j_a.channel_count",
                     j.get("channel_count") == 2 and
                     (j.get("overall") or {}).get("window") == 0.05,
                     f"channel_count={j.get('channel_count')} "
                     f"window={(j.get('overall') or {}).get('window')}")
            self.add(f"{t}.stats_j_a.channel0",
                     ch0.get("peak_count") == 2000 and
                     self.near(ch0.get("rms_level_db"), -9.03088, 1e-3),
                     f"channel0={ch0}")
        for name in ("stat_freq_a", "stat_freq_b"):
            leg = self.leg(e, name)
            if leg is None:
                self.add(f"{t}.{name}.line_law", False, "leg missing",
                         blocked=True)
                continue
            samples = leg.get("samples_read")
            n_spec = None if not samples else -(-samples // 4096)
            self.add(f"{t}.{name}.step",
                     leg.get("step_hz") == round(48000 / 4096.0, 6),
                     f"step={leg.get('step_hz')}")
            self.add(f"{t}.{name}.line_law",
                     n_spec is not None and
                     leg.get("numeric_lines") == 2048 * n_spec,
                     f"lines={leg.get('numeric_lines')} "
                     f"2048*ceil(samples/4096)={2048 * n_spec if n_spec else None}")
        leg = self.leg(e, "stat_e_short_mono")
        if leg:
            eb = leg.get("ebur") or {}
            self.add(f"{t}.stat_e_short_mono.length_gate",
                     "EBUR128 Momentary" in eb and "EBUR128 Integrated" not in eb,
                     f"ebur keys={sorted(eb)}")
        leg = self.leg(e, "stat_e_long_stereo")
        if leg:
            eb = leg.get("ebur") or {}
            self.add(f"{t}.stat_e_long_stereo.integrated_present",
                     "EBUR128 Integrated" in eb, f"ebur keys={sorted(eb)}")
        leg = self.leg(e, "ffmpeg_ebur128_short_mono")
        if leg:
            self.add(f"{t}.ffmpeg_ebur128.gates_short_mono",
                     leg.get("integrated_lufs") is not None and
                     float(leg["integrated_lufs"]) <= -60.0,
                     f"integrated_lufs={leg.get('integrated_lufs')}")
        self.scout_ref_law(e, "dither_s_R", t)
        self.scout_metric_law(e, "dither_s_R", t,
                              ("max_abs_err", "err_rms"), 1e-6)
        self.scout_metric_law(e, "dither_p12_R", t,
                              ("max_abs_err", "err_rms"), 1e-6)
        self.census_law(e, t)

    # ------------------------------------------------------------ run them
    def run(self):
        for fn in (self.det, self.gain, self.rate, self.remix, self.trim,
                   self.fade, self.rps, self.dither):
            fn()
        self.consistency()
        return self.rows

    def consistency(self):
        """Cross-check: every red the fixture recorded must also be derivable
        from the fields (and vice versa the fixture must not have recorded a
        red where no law fires)."""
        derived_fail = sum(1 for r in self.rows if r["status"] == "FAIL")
        derived_block = sum(1 for r in self.rows if r["status"] == "BLOCKED")
        rec_fail = rec_block = 0
        for name, e in self.M.items():
            if not isinstance(e, dict) or "legs" not in e:
                continue
            rec_fail += len(e.get("failures") or [])
            rec_block += len(e.get("coverage_blocked") or [])
        self.add("receipt.failures_empty", rec_fail == 0,
                 f"recorded failures={rec_fail}")
        self.add("receipt.coverage_blocked_empty", rec_block == 0,
                 f"recorded coverage_blocked={rec_block}")
        self.add("receipt.verifier_agrees_on_reds",
                 (rec_fail == 0) == (derived_fail == 0),
                 f"derived FAIL={derived_fail} vs recorded failures={rec_fail}; "
                 f"derived BLOCKED={derived_block} vs recorded "
                 f"coverage_blocked={rec_block}")


def apply_forge(doc, name):
    d = copy.deepcopy(doc)
    M = d["measurements"]

    def det():
        return M["sox_det_r94_probe"]

    def rate():
        return M["sox_rate_r94_probe"]

    if name == "none":
        return d
    if name == "clear-failures":
        for e in M.values():
            if isinstance(e, dict):
                e["failures"] = []
                e["coverage_blocked"] = []
    elif name == "flip-stable":
        leg = det()["legs"]["det_gain_m6_D"]
        leg["n_distinct_shas"] = 5
        leg["stable"] = False
    elif name == "forge-sha":
        det()["legs"]["det_passthrough_identity"]["out_sha256"] = "de" * 32
    elif name == "forge-band":
        rate()["legs"]["alias_20k_default"]["band_21100hz_db"] = -60.0
    elif name == "pop-scout-ref":
        det()["legs"]["det_gain_m6_D"].pop("scout_ref", None)
    elif name == "forge-stim":
        det()["stimuli"]["sha256"]["a"] = "de" * 32
    elif name == "forge-metric":
        M["sox_gain_r94_probe"]["legs"]["gain_m6_rint"][
            "mismatch_vs_rint_formula"] = 17
    elif name == "forge-text":
        M["sox_dither_stat_r94_probe"]["legs"]["stat_plain_a"][
            "fields"]["RMS amplitude"] = "0.500000"
    elif name == "pop-frames":
        M["sox_trim_r94_probe"]["legs"]["trim_0_1s"]["metrics"]["frames"] = 4800
    elif name == "forge-scout-expect":
        det()["legs"]["det_gain_m6_D"]["scout_ref"]["expected_sha256"] = "ab" * 32
    elif name == "pop-coverage":
        det()["legs"]["det_gain_m6_D"].pop("scout_ref", None)
        for e in M.values():
            if isinstance(e, dict):
                e["failures"] = []
                e["coverage_blocked"] = []
    else:
        raise SystemExit(f"unknown forge {name}")
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("receipt")
    ap.add_argument("--forge", default="none", choices=FORGES)
    ap.add_argument("--json", default=None)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    doc = json.loads(open(args.receipt).read())
    doc = apply_forge(doc, args.forge)
    laws = Laws(doc)
    rows = laws.run()
    fails = [r for r in rows if r["status"] == "FAIL"]
    blocks = [r for r in rows if r["status"] == "BLOCKED"]
    passes = [r for r in rows if r["status"] == "PASS"]
    if not args.quiet:
        for r in rows:
            if r["status"] != "PASS":
                print(f"{r['status']:8s} {r['law']}: {r['detail']}")
    print(f"FORGE={args.forge} laws={len(rows)} PASS={len(passes)} "
          f"FAIL={len(fails)} BLOCKED={len(blocks)}")
    if args.json:
        with open(args.json, "w") as fh:
            json.dump({"receipt": args.receipt, "forge": args.forge,
                       "n_laws": len(rows), "n_pass": len(passes),
                       "n_fail": len(fails), "n_blocked": len(blocks),
                       "rows": rows}, fh, indent=1)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
