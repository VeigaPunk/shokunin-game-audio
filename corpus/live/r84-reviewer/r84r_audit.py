#!/usr/bin/env python3
"""r84 REVIEWER — independent re-derivation of every pinned r84 constant
from the committed receipts, plus the verdict-board cross-checks.

Read-only: reads the two committed receipts (run1/run2) and the pinned
copy of the committed fixture blob; writes nothing outside this seat dir.
No host audio objects are touched by this script.

Usage: TMPDIR=... python3 r84r_audit.py
"""
import hashlib
import re
import json
import statistics
import sys
from pathlib import Path

LANE = Path(__file__).resolve().parents[3]
RUNS = {
    "run1": LANE / "corpus/live/r84-author/runs/run1/measurements.json",
    "run2": LANE / "corpus/live/r84-author/runs/run2/measurements.json",
}
CANON = {
    "run1": LANE / "corpus/live/runs/20261016T003253840363Z-alsapw-r84/measurements.json",
    "run2": LANE / "corpus/live/runs/20261016T003756373122Z-alsapw-r84/measurements.json",
}
PINNED = LANE / "corpus/live/r84-reviewer/measure_audio_fbe65713.py"
ENTRIES = ("alsapw_dev_lattice_r84_probe", "alsapw_pw_args_r84_probe",
           "alsapw_pulseprop_r84_probe", "alsapw_pactl_write_r84_probe",
           "alsapw_monstream_r84_probe", "alsapw_negctl_r84_probe")

checks = []


def check(name, ok, detail=""):
    checks.append((name, bool(ok), detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def med(series, lo, hi):
    vals = [a for t, a in series if lo <= t <= hi]
    return float(statistics.median(vals)) if vals else None


def main():
    # ---- 0. receipt provenance -------------------------------------------
    for r, p in CANON.items():
        check(f"receipt {r} == canon dir copy", sha(RUNS[r]) == sha(p),
              sha(RUNS[r])[:16])
    pinned = PINNED.read_text()
    check("pinned fixture copy present", len(pinned) > 1_000_000,
          f"{len(pinned)} bytes")

    data = {r: json.loads(Path(p).read_text()) for r, p in RUNS.items()}

    # ---- 1. census -------------------------------------------------------
    for r, d in data.items():
        m = d["measurements"]
        present = [e for e in ENTRIES if e in m]
        check(f"{r}: all 6 r84 entries present", len(present) == 6,
              ",".join(present))
        legs = {e: m[e]["legs"] for e in present}
        n = sum(len(v) for v in legs.values())
        check(f"{r}: 147 legs", n == 147, str(n))
        fails = {e: m[e].get("failures") for e in present}
        check(f"{r}: failures empty in all 6 entries",
              all(f == [] for f in fails.values()),
              json.dumps({e: f for e, f in fails.items() if f})[:200])
        blocked = {e: m[e].get("coverage_blocked") for e in present}
        check(f"{r}: no coverage_blocked key emitted",
              all(v is None for v in blocked.values()),
              json.dumps(blocked)[:200])
        for e in present:
            sg = m[e].get("sinks_gone")
            if sg is not None:
                check(f"{r}/{e}: sinks_gone all true",
                      isinstance(sg, dict) and all(sg.values()), str(sg))
                check(f"{r}/{e}: own_nodes_after empty",
                      m[e].get("own_nodes_after") == [],
                      str(m[e].get("own_nodes_after")))
                ul = m[e].get("unloads") or {}
                # the r76+ convention: the module index is re-read BY NAME
                # and must equal the captured one, rc=0, not recycled
                check(f"{r}/{e}: unloads name-verified (idx==captured, rc0)",
                      ul and all(
                          (v or {}).get("verified_index") ==
                          (v or {}).get("captured") and
                          (v or {}).get("exit_code") == 0 and
                          (v or {}).get("recycled") is False
                          for v in ul.values()),
                      json.dumps(ul)[:200])

    # ---- 2. namespace discipline ----------------------------------------
    for r, d in data.items():
        m = d["measurements"]
        bad = []
        pid = None
        for e in ENTRIES:
            for name, leg in m[e]["legs"].items():
                v = leg.get("tag") if isinstance(leg, dict) else None
                if isinstance(v, str) and v:
                    if not v.startswith("r84a_"):
                        bad.append(f"{e}/{name}/tag={v}")
                    else:
                        this = v.split("_")[1]
                        pid = this if pid is None else pid
                        if this != pid:
                            bad.append(f"{e}/{name}/tag pid={this}!={pid}")
        check(f"{r}: every leg tag is r84a_<one pid>_*", not bad,
              "; ".join(bad[:4]) or f"pid={pid}")

    # ---- 3. re-derive the pinned gain laws from raw series ---------------
    for r, d in data.items():
        m = d["measurements"]
        legs = m["alsapw_pactl_write_r84_probe"]["legs"]
        for name, want in (("vol_50_0", 0.125), ("vol_50_1", 0.125),
                           ("vol_150", 3.375), ("vol_25_idx", 0.015625),
                           ("src_vol50_0", 0.125), ("src_vol50_1", 0.125)):
            lg = legs[name]
            s = lg.get("series") or []
            base = med(s, 0.7, 2.0)
            post = med(s, 3.0, (lg.get("dur_s") or 7.2) - 0.4)
            rat = round(post / base, 6) if base else None
            check(f"{r}/{name}: independent median ratio == {want}",
                  rat == want, f"base={base} post={post} ratio={rat} "
                               f"(receipt ratio={lg.get('ratio')})")
            # envelope slack: how close is the measured value to the gate
            # edges?  (small slack => the gate is tight; huge => loose)
        # the sticky pin, re-derived arithmetically
        st = m["alsapw_monstream_r84_probe"]["legs"]["sticky"]
        check(f"{r}/sticky: 8192*0.3^3 == receipt respawn_tap_med",
              round(8192 * 0.3 ** 3) == st.get("respawn_tap_med"),
              f"8192*0.027={8192*0.027:.3f} med={st.get('respawn_tap_med')}")
        check(f"{r}/sticky: respawn percent 30 + repair 100 verified",
              st.get("respawn_percent") == 30 and
              st.get("repaired_percent") == 100 and
              st.get("repaired_mute") is False,
              f"{st.get('respawn_percent')}/{st.get('repaired_percent')}/"
              f"mute={st.get('repaired_mute')}")
        # sticky median window composition (the knife-edge check)
        tail = st.get("respawn_tap_series_tail") or []
        pre = [a for t, a in tail if a < 1000]
        check(f"{r}/sticky: repair visible inside the 0.8-3.2s median "
              "window (window is mixed pre/post-repair)", len(pre) > 0,
              f"tail={tail}")

    # ---- 4. refusal taxonomy re-derivation -------------------------------
    for r, d in data.items():
        m = d["measurements"]
        legs = m["alsapw_pactl_write_r84_probe"]["legs"]
        for name, cls in (("vol_spec_0", "pa_vol_spec"),
                          ("vol_spec_1", "pa_vol_spec"),
                          ("susp_spec_0", "pa_susp_spec"),
                          ("susp_spec_1", "pa_susp_spec"),
                          ("vol_badidx", "pa_get_info_noent"),
                          ("src_noent", "pa_get_info_noent"),
                          ("si_noent", "pa_get_info_noent"),
                          ("susp_nosuch", "pa_failure_noent"),
                          ("susp_deadidx", "pa_failure_noent"),
                          ("port_noent", "pa_failure_noent")):
            lg = legs[name]
            check(f"{r}/{name}: rc=1 class={cls} no-signal",
                  lg.get("exit_code") == 1 and lg.get("error_class") == cls
                  and not lg.get("signal"),
                  f"rc={lg.get('exit_code')} cls={lg.get('error_class')} "
                  f"sig={lg.get('signal')} hit={lg.get('error_hit')!r}")
        ms = m["alsapw_monstream_r84_probe"]["legs"]
        for name in ("mon_bad0", "mon_deadidx"):
            lg = ms[name]
            o = lg.get("out") or {}
            check(f"{r}/{name}: index refusal rc=1 + 44B header only",
                  lg.get("parec_exit_code") == 1 and
                  lg.get("parec_error_class") == "pa_stream_noent" and
                  o.get("bytes") == 44 and o.get("data_actual") == 0,
                  f"rc={lg.get('parec_exit_code')} "
                  f"cls={lg.get('parec_error_class')} "
                  f"hit={lg.get('parec_error_hit')!r} bytes={o.get('bytes')}")
        lg = ms["mon_soidx"]
        check(f"{r}/mon_soidx: source-output empty-accept rc=0 44B",
              lg.get("parec_exit_code") == 0 and
              (lg.get("out") or {}).get("bytes") == 44,
              f"rc={lg.get('parec_exit_code')} "
              f"bytes={(lg.get('out') or {}).get('bytes')}")

    # ---- 5. mid-run tap visibility (the boundary correction) -------------
    for r, d in data.items():
        ms = d["measurements"]["alsapw_monstream_r84_probe"]["legs"]
        for rep in (0, 1):
            lg = ms[f"monA_sivol_{rep}"]
            check(f"{r}/monA_sivol_{rep}: pre=100% and ratio 0.125",
                  lg.get("pre_percent") == 100 and lg.get("ratio") == 0.125,
                  f"pre={lg.get('pre_percent')} base={lg.get('base_amp')} "
                  f"post={lg.get('post_amp')} ratio={lg.get('ratio')}")
        lg = ms["monA_simute"]
        check(f"{r}/monA_simute: mute 0 then back to base",
              lg.get("muted_amp") == 0.0 and
              lg.get("restored_amp") == lg.get("base_amp"),
              f"{lg.get('base_amp')}/{lg.get('muted_amp')}/"
              f"{lg.get('restored_amp')}")

    # ---- 6. run1 vs run2 stability of the pinned leaves ------------------
    def leaves(o, path=""):
        if isinstance(o, dict):
            for k, v in o.items():
                yield from leaves(v, f"{path}/{k}")
        elif isinstance(o, list):
            for i, v in enumerate(o):
                yield from leaves(v, f"{path}[{i}]")
        else:
            yield path, o

    volatile = ("pid", "index", "serial", "id", "path", "file", "wait_s",
                "wall_s", "tmp", "loadavg", "at_s", "client.id", "object.id",
                "object.serial", "application.process.id", "module_id",
                "a_killed_at_s", "stream_wait_s", "spawn_wait", "dur_s",
                "wall", "stderr", "stdout", "hit", "name", "tag", "argv",
                "byte", "bytes", "size", "lufs", "centroid", "peak",
                "rms", "timestamp", "u", "elapsed",
                # incidental: spa buffer geometry + driver id + series tail
                # length (the tap WAV is killed at a wall-clock boundary)
                "pulse.attr", "node.driver-id", "series[",
                # recorded node-state observation (not a gated value):
                # the node may have idled/suspended before the read
                "/state")

    # enumerated non-gated witnesses: the sticky tail is a witness (its
    # *timestamps* shift with the tap start), and the sig-window amp
    # readings vary at a routing transition while the gated value there
    # is the window's sig LABEL (checked separately below).
    benign = ("respawn_tap_series_tail[", "/sig/windows[")

    def is_volatile(p):
        if any(tok in p for tok in volatile):
            return True
        if any(tok in p for tok in benign):
            return p.endswith(("/a", "/b", "/at_s", "][0]", "][1]")) or \
                "respawn_tap_series_tail" in p
        return False

    diffs = []
    a = data["run1"]["measurements"]
    b = data["run2"]["measurements"]

    def norm(v, pid):
        if isinstance(v, str):
            return re.sub(r"\d{6,}", "<n>", v.replace(pid, "<n>"))
        if isinstance(v, int) and v > 100000:
            return "<index>"
        return v

    def entry_pid(m, e):
        hit = re.search(r"r84a[a-z_]*?(\d{5,})", json.dumps(m[e]))
        return hit.group(1) if hit else ""

    for e in ENTRIES:
        la = dict(leaves(a[e]["legs"]))
        lb = dict(leaves(b[e]["legs"]))
        pida = entry_pid(a, e)
        pidb = entry_pid(b, e)
        only_a = {p for p in set(la) - set(lb) if not is_volatile(p)}
        only_b = {p for p in set(lb) - set(la) if not is_volatile(p)}
        for p in sorted(only_a):
            diffs.append(f"{e}{p}: only in run1 = {la[p]!r}")
        for p in sorted(only_b):
            diffs.append(f"{e}{p}: only in run2 = {lb[p]!r}")
        for p in set(la) & set(lb):
            if is_volatile(p):
                continue
            if norm(la[p], pida) != norm(lb[p], pidb):
                diffs.append(f"{e}{p}: {la[p]!r} != {lb[p]!r}")
    check("run1 == run2 on every non-volatile, pid-normalized leaf",
          not diffs, f"{len(diffs)} diffs: " + "; ".join(diffs[:6]))

    # ---- 6b. classifier coverage: every live-observed class is tabled --
    for r, d in data.items():
        m = d["measurements"]
        obs = set()
        for e in ENTRIES:
            for leg in m[e]["legs"].values():
                if not isinstance(leg, dict):
                    continue
                for k in ("error_class", "parec_error_class"):
                    if leg.get(k):
                        obs.add(leg[k])
                for a in (leg.get("actions") or {}).values():
                    if isinstance(a, dict) and a.get("error_class"):
                        obs.add(a["error_class"])
                for k in ("write", "repair"):
                    if isinstance(leg.get(k), dict) and \
                            leg[k].get("error_class"):
                        obs.add(leg[k]["error_class"])
        unit = {leg["expect"] for leg in m["alsapw_negctl_r84_probe"]
                ["legs"].values()
                if isinstance(leg, dict) and leg.get("expect")}
        check(f"{r}: every live-observed error class is in the unit table",
              obs <= unit, f"uncovered={sorted(obs - unit)}")
        check(f"{r}: unit table has the 18 named classes",
              len(unit) == 18, f"{len(unit)} classes")

    # ---- 7. verdict-board arithmetic ------------------------------------
    for r, d in data.items():
        m = d["measurements"]
        lg = m["alsapw_pactl_write_r84_probe"]["legs"]["vol_0_100"]
        check(f"{r}/vol_0_100: 0% then 100% restores",
              lg.get("muted_amp") == 0.0 and
              lg.get("restored_amp") == lg.get("base_amp"),
              f"{lg.get('base_amp')}/{lg.get('muted_amp')}/"
              f"{lg.get('restored_amp')}")
        lg = m["alsapw_pactl_write_r84_probe"]["legs"]["vol_frac"]
        check(f"{r}/vol_frac: 50.5% -> 33095", lg.get("volume_value") == 33095,
              f"{lg.get('volume_value')} ({lg.get('volume_percent')})")
        lg = m["alsapw_pactl_write_r84_probe"]["legs"]["vol_raw"]
        check(f"{r}/vol_raw: 1.5 -> 75020 (linear amp)",
              lg.get("volume_value") == 75020, str(lg.get("volume_value")))

    # ---- 7b. shared-host guardrails (constraint compliance) -------------
    for r, d in data.items():
        m = d["measurements"]
        flat = json.dumps(m)
        check(f"{r}: never set-default-sink/source",
              "set-default-sink" not in flat and
              "set-default-source" not in flat,
              "grep of the whole receipt")
        roles = set()
        restore_keys = set()
        for e in ENTRIES:
            for leg in m[e]["legs"].values():
                if not isinstance(leg, dict):
                    continue
                for p, v in leaves(leg):
                    if p.endswith("media.role") and isinstance(v, str):
                        roles.add(v)
                    if p.endswith("module-stream-restore.id") and \
                            isinstance(v, str):
                        restore_keys.add(v)
        # the pulseprop entry deliberately *observes* the shared keys
        # (phone/music/notarole/paplay) on its own short-lived streams;
        # every OTHER entry must show only the private role key.
        off_entry = set()
        for e in ENTRIES:
            if e == "alsapw_pulseprop_r84_probe":
                continue
            for leg in m[e]["legs"].values():
                if not isinstance(leg, dict):
                    continue
                for p, v in leaves(leg):
                    if p.endswith("media.role") and isinstance(v, str):
                        off_entry.add(v)
                    if p.endswith("module-stream-restore.id") and \
                            isinstance(v, str):
                        off_entry.add(v)
        role_keys = {x for x in off_entry
                     if "by-media-role:" in x}
        check(f"{r}: outside pulseprop every by-media-role key is private",
              all(x.split("by-media-role:", 1)[1].startswith("r84arole")
                  for x in role_keys),
              f"{sorted(role_keys)[:6]}")
        # the pulseprop entry deliberately *observes* the shared keys
        # (phone/music/notarole/paplay) on its own short-lived streams;
        # every sink-input-level GAIN WRITE must land on a stream the
        # receipt itself shows keyed to the private role.
        si_write = []
        for e in ENTRIES:
            for nm, leg in m[e]["legs"].items():
                if not isinstance(leg, dict):
                    continue
                acts = leg.get("actions") or {}
                argv = " ".join(
                    str((a or {}).get("argv", "")) for a in acts.values()
                    if isinstance(a, dict))
                if "set-sink-input-volume" not in argv and \
                        "set-sink-input-mute" not in argv:
                    continue
                keys = {v for p, v in leaves(leg)
                        if p.endswith("module-stream-restore.id") and
                        isinstance(v, str)}
                if not any("r84arole" in k for k in keys):
                    si_write.append(f"{e}/{nm} keys={sorted(keys)}")
        check(f"{r}: every sink-input gain write is on a private-role stream",
              not si_write, "; ".join(si_write[:4]))
        for e in ("alsapw_pactl_write_r84_probe",
                  "alsapw_monstream_r84_probe"):
            rr = m[e].get("role_reset") or {}
            check(f"{r}/{e}: private restore key reset+verified at entry",
                  rr.get("reset_ok") is True and
                  rr.get("post_percent") == 100 and
                  rr.get("post_mute") is False,
                  json.dumps({k: rr.get(k) for k in
                              ("spawn_percent", "post_percent",
                               "post_mute", "reset_ok")}))
        rs = m["alsapw_pactl_write_r84_probe"].get("reset_sink_end")
        check(f"{r}/pactl_write: sink/source state restored at exit",
              rs == [0, 0, 0, 0], str(rs))

    # ---- 8. gate envelope census (independent of the fixture) -----------
    env = {"x0.125": (0.105, 0.150), "x3.375": (3.00, 3.80),
           "x0.015625": (0.010, 0.024)}
    print("\n-- gate envelope census (measured vs gate edges) --")
    for k, (lo, hi) in env.items():
        exact = {"x0.125": 0.125, "x3.375": 3.375, "x0.015625": 0.015625}[k]
        print(f"   {k}: gate=({lo},{hi}) exact={exact} "
              f"low-slack={exact/lo-1:+.1%} high-slack={hi/exact-1:+.1%}")

    # ---- 9. the sticky median window composition (arithmetic) -----------
    print("\n-- sticky respawn median window composition --")
    win = [round(0.8 + 0.1 * i, 2) for i in range(25)]
    print(f"   window 0.8..3.2s = {len(win)} x 0.1s samples; repair at "
          f"~2.1s -> pre-repair samples in window = "
          f"{len([t for t in win if t <= 2.1])} / {len(win)} "
          "(median needs > 12.5 to stay on 221)")

    n_fail = sum(1 for _, ok, _ in checks if not ok)
    print(f"\n=== {len(checks)} checks, {n_fail} failed ===")
    out = Path(__file__).with_name("r84r_audit.json")
    out.write_text(json.dumps(
        {"checks": [{"name": n, "ok": o, "detail": d} for n, o, d in checks],
         "failed": n_fail}, indent=1))
    print(f"receipt: {out}")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
