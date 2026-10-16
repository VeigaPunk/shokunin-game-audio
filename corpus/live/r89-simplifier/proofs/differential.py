#!/usr/bin/env python3
"""r89 simplifier — executed differential suite.

Loads the commit-pinned blob and the folded copy as modules (no bytecode
writes, no live PipeWire) and compares the folded surfaces under stubs:

  D1  _pwprof_r89_play        dead role param       (T1)
  D2  _pwprof_r89_nleg        dead wd param         (T2)
  D3  _pwprof_r89_block       dead players param    (T3/T6)
  D4  _pwprof_r89_ensure_player dead wait_s default (T4)
  D5  _pwprof_r89_teardown    dead guards           (T5)
  D6  out-of-domain disclosures (unreachable shapes)
  D7  pwprof_gate_r89_entry   full entry, happy + load-failure paths
  D8  pwprof_schema_r89_entry full entry (T4/T5/T6/T7 end-to-end)

Writes nothing.
"""
import importlib.util
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
FAIL = []


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


base = load("r89simp_base", os.path.join(HERE, "base-measure_audio.py"))
fold = load("r89simp_folded", os.path.join(HERE, "folded",
                                           "measure_audio.py"))


def check(name, cond, detail=""):
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")
    if not cond:
        FAIL.append(name)


NS = "r89a_ns_TEST"


class FakeClock:
    def __init__(self):
        self.t = 1000.0
        self.tn = 10**12

    def monotonic(self):
        return self.t

    def sleep(self, s):
        self.t += s
        self.tn += int(s * 10**9)

    def monotonic_ns(self):
        return self.tn


# ================= D1: play dead role param =============================
def play_case(mod):
    cap = {}

    class FakePopen:
        def __init__(self, argv, **kw):
            cap["argv"] = list(argv)
            cap["kw"] = kw

    orig = mod.subprocess.Popen
    mod.subprocess.Popen = FakePopen
    try:
        res = mod._pwprof_r89_play("t_pl", NS, "tone.wav")
    finally:
        mod.subprocess.Popen = orig
    return cap, type(res).__name__


cb, rb = play_case(base)
cf, rf = play_case(fold)
check("D1 argv identical base vs folded", cb["argv"] == cf["argv"],
      f"{cb['argv']}")
check("D1 media.role is the private seat role",
      any("media.role=r89arole" in a for a in cb["argv"]))
check("D1 node.name + target + tone identical",
      cb["argv"] == ["pw-play", "-P", "node.name=t_pl", "-P",
                     f"media.role={base.PWPROF_R89_ROLE}",
                     "--target", NS, "tone.wav"])
check("D1 Popen kwargs identical", cb["kw"] == cf["kw"], f"{cb['kw']}")

# ================= D2: nleg dead wd param ==============================
def mk_payload(n, driver=NS, count0=0, nsec0=10**12):
    arr = []
    prev_sig = None
    for i in range(n):
        nsec = nsec0 + i * 42666666
        sig = nsec + 1000
        aw = sig + 2550
        fin = aw + 1400
        prev = prev_sig if prev_sig is not None else sig - 42666666
        arr.append({"type": "info", "count": count0 + i,
                    "cpu_load0": 1.0, "cpu_load1": 0.9,
                    "cpu_load2": 0.8})
        arr.append({"type": "clock", "id": 42,
                    "name": "clock.system.monotonic", "nsec": nsec,
                    "duration": 2048, "rate": "1/48000",
                    "next_nsec": nsec + 42666666,
                    "position": 1000 + i * 2048,
                    "transport": "stopped", "diff": 1.0, "xrun": 0})
        arr.append({"type": "driver", "id": 42, "name": driver,
                    "prev": prev, "signal": sig, "awake": aw,
                    "finish": fin, "status": "finished",
                    "latency": "0/0", "xrun_count": 0})
        prev_sig = sig
    arr.append({})
    return json.dumps(arr)


def nleg_case(mod, n_arg, **kw):
    cap = {"calls": []}

    def fake_stream(argv, timeout_s, **skw):
        cap["calls"].append({
            "argv": [str(a) for a in argv], "timeout_s": timeout_s,
            "wd_present": "wd" in skw, "wd_effective": skw.get("wd"),
            "sig_at": skw.get("sig_at"), "sig": skw.get("sig")})
        n = 8 if str(n_arg).strip("+ ") == "8" else 4
        payload = mk_payload(n)
        return {"argv": " ".join(str(a) for a in argv), "exit_code": 0,
                "signal": None, "killed_at_bound": False,
                "alive_at_sig": None, "wall_s": 0.05,
                "stdout": payload[:300], "stdout_bytes": len(payload),
                "stderr": "", "stderr_bytes": 0, "stream_samples": [],
                "error_class": None, "error_hit": None,
                "stdout_raw": payload, "stderr_raw": ""}

    orig = mod._pwprof_r89_stream
    mod._pwprof_r89_stream = fake_stream
    try:
        rec = mod._pwprof_r89_nleg(n_arg, **kw)
    finally:
        mod._pwprof_r89_stream = orig
    return rec, cap


def strip_wd(calls):
    return [{k: v for k, v in c.items() if k != "wd_present"}
            for c in calls]


for n_arg, kw in ((8, {}), ("007", {"bound_s": 2.5})):
    rb, cb = nleg_case(base, n_arg, **kw)
    rf, cf = nleg_case(fold, n_arg, **kw)
    check(f"D2[{n_arg}] argv/timeout/sig identical (wd presence excluded)",
          strip_wd(cb["calls"]) == strip_wd(cf["calls"]),
          f"base={cb['calls']} fold={cf['calls']}")
    check(f"D2[{n_arg}] effective wd is None on both sides",
          cb["calls"][0]["wd_effective"] is None and
          cf["calls"][0]["wd_effective"] is None)
    check(f"D2[{n_arg}] base passes wd explicitly, folded omits it "
          "(same effective default)",
          cb["calls"][0]["wd_present"] and not cf["calls"][0]["wd_present"])
    check(f"D2[{n_arg}] rec identical", rb == rf,
          "" if rb == rf else f"\n  base={rb}\n  fold={rf}")

# ================= D3: block dead players + guards =====================
LEAF = {"module_id": 4242, "rc": 0, "error": None,
        "field": "sink_name", "value": NS}


class FakeProc:
    def __init__(self):
        self.waited = 0

    def wait(self, timeout=None):
        self.waited += 1
        return 0


def blk_case(mod, loads, shape="4arg"):
    calls = {"killpg": [], "unload": []}

    def unload(mid, field, value):
        calls["unload"].append((mid, field, value))
        return {"verified_index": 1, "captured": mid, "field": field,
                "value": value}

    def killpg(*a, **k):
        calls["killpg"].append(a)

    orig = {k: getattr(mod, k) for k in
            ("_pactlmon_r85_unload_own", "_alsapw_r84_killpg")}
    mod._pactlmon_r85_unload_own = unload
    mod._alsapw_r84_killpg = killpg
    try:
        entry, failures = {}, []
        if shape == "3arg":
            out = mod._pwprof_r89_block(entry, failures, "missing tools")
        else:
            out = mod._pwprof_r89_block(entry, failures, "msg", loads)
    finally:
        for k, v in orig.items():
            setattr(mod, k, v)
    return out, failures, calls


for name, loads, shape in (("tools-3arg", None, "3arg"),
                           ("empty", {}, "4arg"),
                           ("leaf", {NS: LEAF}, "4arg"),
                           ("mid-none", {NS: {**LEAF, "module_id": None}},
                            "4arg")):
    ob, fbb, cb = blk_case(base, loads, shape)
    of_, fbf, cf = blk_case(fold, loads, shape)
    check(f"D3[{name}] entry identical", ob == of_,
          "" if ob == of_ else f"\n  base={ob}\n  fold={of_}")
    check(f"D3[{name}] failures identical", fbb == fbf)
    check(f"D3[{name}] unload calls identical", cb["unload"] == cf["unload"],
          f"{cb['unload']} vs {cf['unload']}")
    check(f"D3[{name}] killpg never fired (players unbound)",
          cb["killpg"] == [] and cf["killpg"] == [])

# ================= D4: ensure_player dead wait_s default ===============
def ep_case(mod, scenario):
    clock = FakeClock()
    calls = {"play": 0, "graph": 0, "killpg": []}

    class Proc:
        def __init__(self):
            self.n = 0

        def poll(self):
            self.n += 1
            return None if scenario != "dead-play" else 0

    def fake_play(*a, **k):
        calls["play"] += 1
        return Proc()

    linked = scenario != "never"

    def fake_graph():
        calls["graph"] += 1
        return {"nodes": {}, "edges": []}

    def fake_node(g, tag):
        return {"node_id": 1} if linked else None

    def fake_edges(g, tag):
        return [{"in_node": NS}] if linked else []

    orig = {k: getattr(mod, k) for k in
            ("_pwprof_r89_play", "_pactlmon_r85_graph",
             "_pactlmon_r85_node", "_pactlmon_r85_edges_out")}
    orig_time = mod.time
    mod._pwprof_r89_play = fake_play
    mod._pactlmon_r85_graph = fake_graph
    mod._pactlmon_r85_node = fake_node
    mod._pactlmon_r85_edges_out = fake_edges
    mod.time = clock
    try:
        ctx = {"ns": NS, "tone": "t.wav", "player": None, "linked": False}
        out = mod._pwprof_r89_ensure_player(ctx, "t_pl")
        ctx_state = dict(ctx)
    finally:
        for k, v in orig.items():
            setattr(mod, k, v)
        mod.time = orig_time
    return out, ctx_state, calls, clock.t, clock.tn


def ctx_view(ctx):
    return {k: v for k, v in ctx.items() if k != "player"}


for scenario in ("linked", "never", "dead-play"):
    rb, sb, cb, tb, nb = ep_case(base, scenario)
    rf, sf, cf, tf, nf = ep_case(fold, scenario)
    check(f"D4[{scenario}] return identical", rb == rf, f"{rb} vs {rf}")
    check(f"D4[{scenario}] ctx identical (player object excluded)",
          ctx_view(sb) == ctx_view(sf) and
          (sb["player"] is None) == (sf["player"] is None),
          f"base={ctx_view(sb)} fold={ctx_view(sf)}")
    check(f"D4[{scenario}] play/graph call counts identical",
          cb == cf, f"base={cb} fold={cf}")
    check(f"D4[{scenario}] fake-clock end state identical (wait_s==6.0 "
          "inlined)",
          (tb, nb) == (tf, nf), f"base=({tb},{nb}) fold=({tf},{nf})")
    if scenario == "never":
        check("D4[never] the 6.0 s default was actually consumed",
              nb == 10**12 + 6 * 10**9 and cb["graph"] == 24,
              f"tn={nb} graph_calls={cb['graph']}")

# ================= D5: teardown dead guards ============================
def td_case(mod, loads, graph, sinks_now, names):
    calls = {"unload": [], "cli": [], "killpg": []}

    def unload(mid, field, value):
        calls["unload"].append((mid, field, value))
        return {"verified_index": 1, "captured": mid, "field": field,
                "value": value}

    def cli(*args, **kw):
        calls["cli"].append((args, kw))
        return {"exit_code": 0}

    def killpg(*a, **k):
        calls["killpg"].append(a)

    orig = {k: getattr(mod, k) for k in
            ("_pactlmon_r85_graph", "_capture_r77_sink_names_strict",
             "_playback_r78_node_names", "_pactlmon_r85_unload_own",
             "_pwprof_r89_stream", "_alsapw_r84_killpg")}
    orig_time = mod.time
    mod._pactlmon_r85_graph = lambda: graph
    mod._capture_r77_sink_names_strict = lambda: sinks_now
    mod._playback_r78_node_names = lambda: names
    mod._pactlmon_r85_unload_own = unload
    mod._pwprof_r89_stream = cli
    mod._alsapw_r84_killpg = killpg
    mod.time = FakeClock()
    try:
        entry, failures = {}, []
        mod._pwprof_r89_teardown(entry, failures, loads)
    finally:
        for k, v in orig.items():
            setattr(mod, k, v)
        mod.time = orig_time
    return entry, failures, calls


G = {"nodes": {5: {"name": "foreign"},
               7: {"name": f"r89a_{base.PWPROF_R89_PID}_x"},
               9: {"name": NS}}}
TD_CASES = [
    ("empty", {}, {"nodes": {}}, set(), []),
    ("one-leaf", {NS: LEAF}, {"nodes": {}}, {"foreign"}, []),
    ("residual-destroy", {NS: {**LEAF, "module_id": None}},
     {"nodes": {7: {"name": f"r89a_{base.PWPROF_R89_PID}_z"}}}, set(), []),
    ("reader-error-sinks", {NS: LEAF}, {"nodes": {}}, None, []),
    ("reader-error-nodes", {NS: LEAF}, {"nodes": {}}, {NS}, None),
    ("foreign+own", {NS: LEAF}, G, {NS}, ["foreign", NS]),
]
for name, loads, graph, sinks_now, names in TD_CASES:
    eb, fb_, cb = td_case(base, loads, graph, sinks_now, names)
    ef, ff, cf = td_case(fold, loads, graph, sinks_now, names)
    check(f"D5[{name}] entry identical", eb == ef,
          "" if eb == ef else f"\n  base={eb}\n  fold={ef}")
    check(f"D5[{name}] failures identical", fb_ == ff)
    check(f"D5[{name}] unload/cli/killpg calls identical",
          cb == cf, f"base={cb} fold={cf}")

# ================= D6: out-of-domain disclosures =======================
# (a) teardown(loads=None): base graceful, folded AttributeError
ob, of_ = {}, {}
tb, _fb, cb = td_case(base, None, {"nodes": {}}, set(), [])
try:
    ef, ff, cf = td_case(fold, None, {"nodes": {}}, set(), [])
    of_ = {"entry": ef, "failures": ff, "calls": cf}
except AttributeError as exc:
    of_ = {"AttributeError": str(exc)}
check("D6[teardown loads=None] disclosed divergence (unreachable: all 4 "
      "call sites pass a dict)", "AttributeError" in of_, f"fold={of_}")

# (b) leaf missing field/value: base falls back, folded KeyError
_, _, cb2 = blk_case(base, {NS: {"module_id": 1}}, "4arg")
try:
    blk_case(fold, {NS: {"module_id": 1}}, "4arg")
    od = "no-divergence"
except KeyError as exc:
    od = f"KeyError {exc}"
check("D6[leaf missing field] disclosed divergence (unreachable: every "
      "leaf comes from _pwprof_r89_load_ns, which sets both keys)",
      od.startswith("KeyError") and cb2["unload"] == [(1, "sink_name", NS)],
      f"base={cb2['unload']} fold={od}")

# (c) block(players=[proc]): base kills, folded TypeError
orig = base._alsapw_r84_killpg
killed = []
base._alsapw_r84_killpg = lambda *a, **k: killed.append(a)
try:
    e, f, c = {}, [], {}
    p = FakeProc()
    base._pwprof_r89_block(e, f, "m", None, [p])
    base_killed = list(killed)
finally:
    base._alsapw_r84_killpg = orig
try:
    fold._pwprof_r89_block({}, [], "m", None, [FakeProc()])
    folded_res = "no-divergence"
except TypeError as exc:
    folded_res = f"TypeError {exc}"
check("D6[block players=[proc]] disclosed divergence (unreachable: 0/10 "
      "call sites bind players)", base_killed and
      folded_res.startswith("TypeError"), f"{folded_res}")

# ================= D7/D8: full-entry differential ======================
def install_backend(mod, mode):
    """Stub every external surface the gate/schema entries touch."""
    clock = FakeClock()
    calls = {"killpg": [], "unload": [], "stream": [], "popen": []}
    state = {"load_none": False, "kill_ns": None, "linked": False}

    class Proc:
        def __init__(self):
            self.rc = None

        def poll(self):
            return None

        def wait(self, timeout=None):
            return 0

    def fake_stream(argv, timeout_s, **kw):
        argv = [str(a) for a in argv]
        joined = " ".join(argv)
        calls["stream"].append({"argv": argv,
                                "kw": sorted(k for k in kw if k != "wd"),
                                "wd_present": "wd" in kw})
        rec = {"argv": joined, "exit_code": 0, "signal": None,
               "killed_at_bound": False, "alive_at_sig": None,
               "wall_s": 0.05, "stdout": "", "stdout_bytes": 0,
               "stderr": "", "stderr_bytes": 0, "stream_samples": [],
               "error_class": None, "error_hit": None}
        for _t, h in kw.get("hooks", ()):
            h()
        import signal as _s
        sig_at = kw.get("sig_at")
        two_n = argv.count("-n") == 2
        # dispatch by the leg's signal point (the crafted scenario set
        # keeps these disjoint; the stub is deterministic and identical
        # for base and folded)
        if sig_at == 1.0:
            sig = kw.get("sig", _s.SIGTERM)
            if sig == _s.SIGKILL:
                rec.update(exit_code=-9, signal="SIGKILL",
                           stdout_raw='[{"type":"info","count":1},')
            elif sig == _s.SIGHUP:
                rec.update(exit_code=-1, signal="SIGHUP",
                           stdout_raw='[{"type":"info","count":1},')
            elif sig == _s.SIGUSR1:
                rec.update(exit_code=-10, signal="SIGUSR1",
                           stdout_raw='[{"type":"info","count":1},')
            else:
                payload = mk_payload(47, driver=mod.PWPROF_R89_NS)
                rec.update(exit_code=0, alive_at_sig=True,
                           stdout_raw=payload)
        elif sig_at == 0.8:
            sig = kw.get("sig", _s.SIGHUP)
            code = -1 if sig == _s.SIGHUP else -10
            rec.update(exit_code=code, signal=sig.name,
                       stdout_raw='[{"type":"info","count":1},')
        elif sig_at == 1.2:
            payload = mk_payload(47, driver=mod.PWPROF_R89_NS)
            rec.update(exit_code=0, alive_at_sig=True, stdout_raw=payload)
            rec["stream_samples"] = [
                {"t": 0.3, "bytes": 8192}, {"t": 0.6, "bytes": 12288},
                {"t": 0.9, "bytes": 16384}]
        elif sig_at == 2.4:
            # suspension leg: every own block BEFORE the hook kill
            payload = mk_payload(47, driver=mod.PWPROF_R89_NS,
                                 nsec0=clock.monotonic_ns() - 3 * 10**9)
            rec.update(exit_code=0, alive_at_sig=True,
                       stdout_raw=payload)
        elif sig_at is not None and two_n:
            # g_lastwins: last -n wins -> unbounded
            payload = mk_payload(47, driver=mod.PWPROF_R89_NS)
            rec.update(exit_code=0, alive_at_sig=True, stdout_raw=payload)
        elif joined.endswith("--version"):
            rec.update(stdout="libpipewire 1.6.8\n",
                       stdout_bytes=18)
        elif "--r89bogus" in joined:
            rec.update(exit_code=255,
                       stderr="pw-profiler: unrecognized option "
                              "'--r89bogus'\n")
        elif "-r r89a_bogus" in joined or kw.get("env"):
            rec.update(exit_code=255,
                       stderr="pw-profiler: Can't connect: Host is "
                              "down\n")
        elif kw.get("keep_raw"):
            # nleg legs: -J -n <n_arg> (extra argv may precede -n)
            n_arg = argv[argv.index("-n") + 1]
            valid = {"8": 8, "4": 4, "007": 7, "+3": 3, " 3": 3}
            if n_arg in valid:
                payload = mk_payload(valid[n_arg],
                                     driver=mod.PWPROF_R89_NS)
                rec.update(exit_code=0, alive_at_sig=False,
                           stdout_raw=payload)
            elif n_arg == "40":
                nsec0 = clock.monotonic_ns()
                payload = mk_payload(40, count0=0, nsec0=nsec0,
                                     driver=mod.PWPROF_R89_NS)
                rec.update(exit_code=0, stdout_raw=payload)
            elif n_arg == "10":
                payload = mk_payload(10, count0=40,
                                     nsec0=clock.monotonic_ns(),
                                     driver=mod.PWPROF_R89_NS)
                rec.update(exit_code=0, stdout_raw=payload)
            else:
                # unbounded class: still alive at the bound
                payload = mk_payload(65, driver=mod.PWPROF_R89_NS)
                rec.update(exit_code=0, alive_at_sig=True,
                           stdout_raw=payload)
        rec["error_class"], rec["error_hit"] = mod._pwprof_r89_errclass(
            rec["stderr"] + "\n" + rec["stdout"])
        return rec

    def fake_popen(argv, **kw):
        calls["popen"].append([str(a) for a in argv])
        return Proc()

    def fake_killpg(proc, sig=None):
        calls["killpg"].append(sig)

    def fake_load_ns(name, extra_args=()):
        if state["load_none"]:
            return {"module_id": None, "rc": 1, "error": "boom"}
        return {"module_id": 500 + len(calls["unload"]), "rc": 0,
                "error": None}

    def fake_unload(mid, field, value):
        calls["unload"].append((mid, field, value))
        return {"verified_index": 1, "captured": mid, "field": field,
                "value": value}

    def fake_graph():
        return {"nodes": {42: {"name": NS}}, "edges": []}

    def fake_node(g, tag):
        return {"node_id": 42}

    def fake_edges(g, tag):
        return [{"in_node": mod.PWPROF_R89_NS}]

    orig = {}
    for k in ("_capture_inventory", "_playback_r78_node_names",
              "_playback_r78_foreign_clients", "_loopback_r79_oracle",
              "_alsapw_r84_loadavg", "_pwcat_r83_ns_load",
              "_playback_r78_write_tone", "_pactlmon_r85_graph",
              "_pactlmon_r85_node", "_pactlmon_r85_edges_out",
              "_pactlmon_r85_unload_own", "_alsapw_r84_killpg",
              "_capture_r77_sink_names_strict", "_pwprof_r89_stream",
              "_pwprof_r89_play"):
        orig[k] = getattr(mod, k)
    orig_time = mod.time
    orig_which = mod.shutil.which
    orig_popen = mod.subprocess.Popen
    mod._capture_inventory = lambda: {
        "default_sink": "d", "default_source": "s", "sources": [1],
        "monitors": [1], "alsa_capture_devices": []}
    mod._playback_r78_node_names = lambda: []
    mod._playback_r78_foreign_clients = lambda: []
    mod._loopback_r79_oracle = lambda: None
    mod._alsapw_r84_loadavg = lambda: "0.00 0.00 0.00"
    mod._pwcat_r83_ns_load = fake_load_ns
    mod._playback_r78_write_tone = lambda p, d: None
    mod._pactlmon_r85_graph = fake_graph
    mod._pactlmon_r85_node = fake_node
    mod._pactlmon_r85_edges_out = fake_edges
    mod._pactlmon_r85_unload_own = fake_unload
    mod._alsapw_r84_killpg = fake_killpg
    mod._capture_r77_sink_names_strict = lambda: []
    mod._pwprof_r89_stream = fake_stream
    mod._pwprof_r89_play = lambda *a, **k: Proc()
    mod.time = clock
    mod.shutil.which = lambda t: f"/usr/bin/{t}"
    mod.subprocess.Popen = fake_popen
    return (calls, state, clock,
            (orig, orig_time, orig_which, orig_popen))


def uninstall(mod, saved):
    orig, orig_time, orig_which, orig_popen = saved
    for k, v in orig.items():
        setattr(mod, k, v)
    mod.time = orig_time
    mod.shutil.which = orig_which
    mod.subprocess.Popen = orig_popen


def gate_run(mod, load_none=False):
    calls, state, clock, saved = install_backend(mod, "gate")
    state["load_none"] = load_none
    try:
        entry = mod.pwprof_gate_r89_entry()
    finally:
        uninstall(mod, saved)
    return entry, calls


def norm(obj):
    """Volatile tempdir names are scrubbed before comparison (they are
    recorded in real receipts too, never armed)."""
    import re as _re
    s = json.dumps(obj, sort_keys=True)
    return _re.sub(r"r89a-(gate|oart|schema|xw)-[A-Za-z0-9_]+",
                   r"r89a-\1-<TMP>", s)


eb, cb = gate_run(base)
ef, cf = gate_run(fold)
check("D7[gate happy] entry byte-identical (json sort_keys, tempdir "
      "scrubbed)",
      norm(eb) == norm(ef),
      "" if norm(eb) == norm(ef) else "ENTRIES DIFFER")
check("D7[gate happy] failures empty on both (crafted green path)",
      eb["failures"] == [] and ef["failures"] == [],
      f"{eb['failures']} / {ef['failures']}")
check("D7[gate happy] stream call surface identical (wd presence "
      "excluded, tempdir scrubbed)",
      norm([{k: v for k, v in c.items() if k != "wd_present"}
            for c in cb["stream"]]) ==
      norm([{k: v for k, v in c.items() if k != "wd_present"}
            for c in cf["stream"]]))
check("D7[gate happy] only nleg legs differ in wd presence",
      all(c["wd_present"] for c in cb["stream"] if "wd" in c["kw"]) and
      not any(c["wd_present"] for c in cf["stream"]))
check("D7[gate happy] popen argv (pw-play) identical",
      cb["popen"] == cf["popen"])
check("D7[gate happy] 27 gate legs recorded",
      len(eb["legs"]) == 27 and len(ef["legs"]) == 27)

eb2, cb2 = gate_run(base, load_none=True)
ef2, cf2 = gate_run(fold, load_none=True)
check("D7[gate load-failure] entry byte-identical (exercises block)",
      json.dumps(eb2, sort_keys=True) == json.dumps(ef2, sort_keys=True),
      "" if json.dumps(eb2, sort_keys=True) == json.dumps(ef2,
                                                            sort_keys=True)
      else "ENTRIES DIFFER")
check("D7[gate load-failure] block unload calls identical",
      cb2["unload"] == cf2["unload"], f"{cb2['unload']} vs {cf2['unload']}")
check("D7[gate load-failure] no killpg from the dead block loop",
      cb2["killpg"] == [] and cf2["killpg"] == [])


def schema_run(mod):
    calls, state, clock, saved = install_backend(mod, "schema")
    try:
        entry = mod.pwprof_schema_r89_entry()
    finally:
        uninstall(mod, saved)
    return entry, calls


eb, cb = schema_run(base)
ef, cf = schema_run(fold)
same = json.dumps(eb, sort_keys=True) == json.dumps(ef, sort_keys=True)
check("D8[schema] entry byte-identical (json sort_keys)", same,
      "" if same else "ENTRIES DIFFER")
check("D8[schema] failures empty on both (crafted green path)",
      eb["failures"] == [] and ef["failures"] == [],
      f"{eb['failures']} / {ef['failures']}")
check("D8[schema] stream call surface identical", cb["stream"] == cf["stream"])
check("D8[schema] unload calls identical", cb["unload"] == cf["unload"])

print()
print(f"DIFFERENTIAL: {'ALL PASS' if not FAIL else 'FAILURES: ' + str(FAIL)}")
sys.exit(1 if FAIL else 0)
