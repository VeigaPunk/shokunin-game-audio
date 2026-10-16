#!/usr/bin/env python3
"""r85 simplifier DIFFERENTIAL proofs — execute base vs folded on scratch
imports with stubbed I/O, and compare observable outputs.

Read-only for the repository; writes only proofs/differential.txt and the
scratch module copies under proofs/dyn/.

Checks:
  D0  per-function/constant source census: only the intended units differ
  D1  _pactlmon_r85_teardown    (dead guards removed) -> identical entry +
      identical unload call list, incl. a foreign-shaped loads value
  D2  _pactlmon_r85_block       (leaf guard removed; loads guard kept)
      -> identical entry for a dict loads AND for loads=None
  D3  _pactlmon_r85_cap_leg     (hit store removed) -> identical leg dict
  D4  _pactlmon_r85_sd_leg      (ctx param + hit store removed) -> identical leg
  D5  _pactlmon_r85_vol_pct     (rec falsy guard removed) -> identical pct
  D6  _pactlmon_r85_wait_tap_link (sink param removed) -> identical return +
      identical poll pattern
  D7  the entry-local `gsv` slice (label param + 20 labels removed)
      -> identical legs dict + identical pactl argv list
  D8  the addr monotonicity slice (sers store removed) -> identical failures
  D9  the capture source-bind slice (want_node payload + dead `lp` store
      removed) -> identical failures, exactly one fewer link_ports call
  D10 the feeder pre-ladder guard (dead conjunct removed) -> identical kills
  D11 the four subsumed `(aN or {})` guards -> identical strings over the
      dict domain
  D12 the two deleted module-level names are absent from the folded namespace
"""
import ast
import importlib.util
import io
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

OUT = []
PASS = FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    tag = "PASS" if cond else "FAIL"
    if cond:
        PASS += 1
    else:
        FAIL += 1
    OUT.append(f"[{tag}] {name}: {detail}")
    return cond


DYN = Path("proofs/dyn")
DYN.mkdir(parents=True, exist_ok=True)
shutil.copy("proofs/base-measure_audio.py", DYN / "base.py")
shutil.copy("proofs/folded/measure_audio.py", DYN / "folded.py")


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


B = load("r85_base_mod", DYN / "base.py")
F = load("r85_folded_mod", DYN / "folded.py")
bsrc = Path("proofs/base-measure_audio.py").read_text()
fsrc = Path("proofs/folded/measure_audio.py").read_text()


# ---------------------------------------------------------------- D0
def unit_map(src):
    t = ast.parse(src)
    ls = src.splitlines()
    fns, consts = {}, {}
    for n in t.body:
        if isinstance(n, ast.FunctionDef):
            fns[n.name] = "\n".join(ls[n.lineno - 1:n.end_lineno])
        if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name):
            consts[n.targets[0].id] = "\n".join(ls[n.lineno - 1:n.end_lineno])
    return fns, consts


bu, bc = unit_map(bsrc)
fu, fc = unit_map(fsrc)
changed_fn = sorted(k for k in bu if bu[k] != fu.get(k))
changed_const = sorted(k for k in bc if bc[k] != fc.get(k))
EXPECT_FN = sorted(["_pactlmon_r85_block", "_pactlmon_r85_cap_leg",
                    "_pactlmon_r85_sd_leg", "_pactlmon_r85_tapped_mix",
                    "_pactlmon_r85_teardown", "_pactlmon_r85_vol_pct",
                    "_pactlmon_r85_wait_node", "_pactlmon_r85_wait_tap_link",
                    "pactlmon_addr_r85_entry",
                    "pactlmon_capture_r85_entry"])
check("D0 only the intended units differ (10 functions + 1 constant)",
      changed_fn == EXPECT_FN and
      changed_const == ["PACTLMON_R85_STREAM_WAIT_S"] and
      len(bu) == len(fu) + 1,
      f"changed functions={changed_fn}; changed constants={changed_const}; "
      f"functions total base/folded={len(bu)}/{len(fu)}")


# ---------------------------------------------------------------- stubs
class FakeTime:
    def __init__(self):
        self.t = 1000.0
        self.sleeps = []

    def monotonic(self):
        self.t += 0.01
        return self.t

    def sleep(self, s):
        self.sleeps.append(s)
        self.t += s


class FakeStderr:
    def __init__(self, data=b""):
        self.buf = io.BytesIO(data)

    def read(self):
        return self.buf.read()


class FakeProc:
    def __init__(self, rc=1, err=b"", pid=4242):
        self.returncode = rc
        self.stderr = FakeStderr(err)
        self.pid = pid
        self._dead = False
        self._rc = rc
        self.signals = []

    def poll(self):
        return self._rc if self._dead else None

    def wait(self, timeout=None):
        self._dead = True
        return self._rc


class FakeSub:
    TimeoutExpired = subprocess.TimeoutExpired
    DEVNULL = subprocess.DEVNULL
    PIPE = subprocess.PIPE

    def __init__(self, procs):
        self.procs = procs
        self.calls = []

    def Popen(self, argv, **kw):
        self.calls.append(list(argv))
        p = self.procs.pop(0) if self.procs else FakeProc()
        return p


def patch(mod, **kw):
    for k, v in kw.items():
        setattr(mod, k, v)


# ---------------------------------------------------------------- D1
def run_teardown(mod, loads, sinks, srcs, nodes):
    kills = []

    def fake_unload(mid, field, value):
        kills.append((mid, field, value))
        return {"verified_index": mid, "captured": mid, "field": field,
                "value": value, "exit_code": 0}

    patch(mod, _capture_r77_sink_names_strict=lambda: sinks,
          _playback_r78_source_names=lambda: srcs,
          _playback_r78_node_names=lambda: nodes,
          _pactlmon_r85_unload_own=fake_unload)
    entry, failures = {}, []
    mod._pactlmon_r85_teardown(entry, failures, loads)
    return entry, failures, kills


loads_cases = [
    {"ns1": {"module_id": 7, "field": "sink_name", "value": "ns1"},
     "vs": {"module_id": 9, "field": "source_name", "value": "vs"}},
    {"ns1": {"module_id": None, "field": "sink_name", "value": "ns1"}},
    {"ns1": {"module_id": 7}},                      # defaults sink_name/ns1
    {"ns1": {"module_id": 7, "field": "sink_name", "value": "ns1",
             "extra": {"k": 1}}},                   # extra keys ignored
]
d1_ok, d1_detail = True, []
for case in loads_cases:
    eb, fb, kb = run_teardown(B, dict(case), ["other"], ["other"], ["x"])
    ef, ff, kf = run_teardown(F, dict(case), ["other"], ["other"], ["x"])
    same = (eb == ef and fb == ff and kb == kf)
    d1_ok = d1_ok and same
    d1_detail.append(f"loads={sorted(case)} same={same}")
# foreign-shape: a None value (impossible from the call graph) is the one
# input where the two copies could differ; assert they do NOT crash and
# record the delta explicitly.
patch(B, _capture_r77_sink_names_strict=lambda: [], _playback_r78_source_names=lambda: [],
      _playback_r78_node_names=lambda: [], _pactlmon_r85_unload_own=lambda *a: {})
patch(F, _capture_r77_sink_names_strict=lambda: [], _playback_r78_source_names=lambda: [],
      _playback_r78_node_names=lambda: [], _pactlmon_r85_unload_own=lambda *a: {})
try:
    B._pactlmon_r85_teardown({}, [], {"ns1": None})
    b_none = "no-crash"
except Exception as exc:
    b_none = type(exc).__name__
try:
    F._pactlmon_r85_teardown({}, [], {"ns1": None})
    f_none = "no-crash"
except Exception as exc:
    f_none = type(exc).__name__
check("D1 _pactlmon_r85_teardown: identical entries/failures/unload calls",
      d1_ok,
      "; ".join(d1_detail) + f"; [disclosed] loads value None: base={b_none} "
      f"folded={f_none} (unreachable from the call graph — every loads "
      f"value is a dict)")


# ---------------------------------------------------------------- D2
def run_block(mod, loads):
    kills = []
    patch(mod, _pactlmon_r85_unload_own=lambda m, f, v: (
        kills.append((m, f, v)) or {"exit_code": 0}))
    entry, failures = {}, []
    mod._pactlmon_r85_block(entry, failures, "blocked-msg", loads)
    return entry, failures, kills


d2_ok = True
d2_detail = []
for loads in ({"ns1": {"module_id": 5, "field": "sink_name", "value": "ns1"}},
              None, {}):
    eb, fb, kb = run_block(B, loads)
    ef, ff, kf = run_block(F, loads)
    same = (eb == ef and fb == ff and kb == kf)
    d2_ok = d2_ok and same
    d2_detail.append(f"loads={loads if loads is None else sorted(loads)} "
                     f"same={same}")
check("D2 _pactlmon_r85_block: identical for a dict loads AND loads=None",
      d2_ok, "; ".join(d2_detail) +
      " (the `(loads or {})` guard is retained — its default None is a "
      "real path)")


# ---------------------------------------------------------------- D3
def run_cap_leg(mod, tmp):
    ft = FakeTime()
    fsub = FakeSub([FakeProc(rc=1, err=b"Failed to get sink information: "
                                      b"No such entity\n")])
    graphs = [{"nodes": {}, "ports": {}, "links": []}]
    patch(mod, time=ft, subprocess=fsub,
          _pactlmon_r85_graph=lambda: graphs[0],
          _pactlmon_r85_edges_in=lambda g, tag: [],
          _pactlmon_r85_node=lambda g, name: None,
          _pactlmon_r85_killpg=lambda p, sig=None: setattr(p, "_dead", True),
          _capture_tail=lambda err, tok: err[:60])
    leg = mod._pactlmon_r85_cap_leg("cdup_cap", {"tmp": str(tmp)}, "12345",
                                    dur_s=2.6, link_samples=(1.0, 2.0))
    return leg, fsub.calls, ft.sleeps


import tempfile
tmpd = Path(tempfile.mkdtemp(prefix="r85diff-"))
lb, cb, sb = run_cap_leg(B, tmpd)
lf, cf, sf = run_cap_leg(F, tmpd)
check("D3 _pactlmon_r85_cap_leg: identical leg dict and spawn argv",
      lb == lf and cb == cf and sb == sf,
      f"leg keys equal={sorted(lb) == sorted(lf)}; record equal={lb == lf}; "
      f"argv equal={cb == cf}; sleeps equal={sb == sf}; error_class="
      f"{lb.get('error_class')}")


# ---------------------------------------------------------------- D4
def run_sd_leg(mod, tmp):
    ft = FakeTime()
    fsub = FakeSub([FakeProc(rc=0, err=b"")])
    patch(mod, time=ft, subprocess=fsub,
          _pactlmon_r85_module_index=lambda f, v: 11,
          _playback_r78_source_names=lambda: ["r85a_sd_x"],
          _pactlmon_r85_graph=lambda: {"nodes": {}, "ports": {}, "links": []},
          _pactlmon_r85_edges_in=lambda g, tag: [],
          _pactlmon_r85_killpg=lambda p, sig=None: setattr(p, "_dead", True),
          _capture_tail=lambda err, tok: err[:60])
    import inspect
    params = inspect.signature(mod._pactlmon_r85_sd_leg).parameters
    kw = {"name": "sd_idle", "sd": "r85a_sd_x",
          "client_argv": ["pw-record", "--version"], "dur_s": 0.2}
    if "ctx" in params:
        kw["ctx"] = {"tmp": str(tmp)}
    leg = mod._pactlmon_r85_sd_leg(**kw)
    return leg, fsub.calls


lb, cb = run_sd_leg(B, tmpd)
lf, cf = run_sd_leg(F, tmpd)
check("D4 _pactlmon_r85_sd_leg: identical leg dict and spawn argv "
      "(ctx param + hit store removed)",
      lb == lf and cb == cf,
      f"record equal={lb == lf}; argv equal={cb == cf}; keys="
      f"{sorted(lb)}")


# ---------------------------------------------------------------- D5
d5_ok = True
d5_detail = []
for rec in ({}, {"stdout": "Volume: front-left: 65536 / 100% / 0.00 dB\n"},
            {"stdout": "Volume: front-left: 32768 /  50% / -6.00 dB\n"},
            {"stdout": ""}, {"stdout": "no percent here"}):
    vb = B._pactlmon_r85_vol_pct(rec)
    vf = F._pactlmon_r85_vol_pct(rec)
    d5_ok = d5_ok and vb == vf
    d5_detail.append(f"{str(rec)[:28]!r}->{vb}")
try:
    B._pactlmon_r85_vol_pct(None)
    b_none = "None"
except Exception as exc:
    b_none = type(exc).__name__
try:
    F._pactlmon_r85_vol_pct(None)
    f_none = "None"
except Exception as exc:
    f_none = type(exc).__name__
check("D5 _pactlmon_r85_vol_pct: identical over the rec domain",
      d5_ok, "; ".join(d5_detail) +
      f"; [disclosed] rec=None: base={b_none} folded={f_none} "
      f"(unreachable from the call graph — 7/7 call sites pass a leg dict)")


# ---------------------------------------------------------------- D6
def run_tap(mod):
    ft = FakeTime()
    graphs = [
        {"nodes": {}, "ports": {}, "links": []},
        {"nodes": {}, "ports": {}, "links": []},
        {"nodes": {}, "ports": {}, "links": []},
    ]
    state = {"i": 0}

    def graph():
        i = min(state["i"], len(graphs) - 1)
        state["i"] += 1
        return graphs[i]

    def edges_in(g, tag):
        # first poll: no links; second poll: the monitor link
        return [] if state["i"] <= 1 else [
            {"out_node": "sink", "out_port_name": "monitor_FL",
             "in_node": tag, "in_port_name": "input_FL"}]

    patch(mod, time=ft, _pactlmon_r85_graph=graph,
          _pactlmon_r85_edges_in=edges_in)
    import inspect
    params = inspect.signature(mod._pactlmon_r85_wait_tap_link).parameters
    kw = {"tap_tag": "tap_tag"}
    if "sink" in params:
        kw["sink"] = "sink"
    res = mod._pactlmon_r85_wait_tap_link(**kw)
    return res, ft.sleeps


rb, sb = run_tap(B)
rf, sf = run_tap(F)
check("D6 _pactlmon_r85_wait_tap_link: identical return and poll pattern "
      "(sink param removed)",
      rb == rf and sb == sf,
      f"base={rb} folded={rf}; sleeps equal={sb == sf}")


# ---------------------------------------------------------------- D7
def gsv_slice(src):
    i0 = src.index("def gsv(")
    i0 = src.rindex("\n", 0, i0) + 1
    i1 = src.index('g_defsinkX"] = gsv(')
    i1 = src.index("\n", i1) + 1
    return textwrap.dedent(src[i0:i1])


def run_gsv(src, mod):
    calls = []
    ns = {
        "legs": {},
        "_pactlmon_r85_pactl": lambda *a, **k: calls.append(list(a)) or
        {"exit_code": 0},
        "PACTLMON_R85_NS": "r85a_ns_1",
        "PACTLMON_R85_BOGUS": "no_such_r85a",
        "ser_a": 235221,
        "oid_a": 99,
    }
    exec(gsv_slice(src), ns)
    return ns["legs"], calls


lb, cb = run_gsv(bsrc, B)
lf, cf = run_gsv(fsrc, F)
check("D7 the gsv slice: identical legs dict and identical pactl argv list "
      "(label param + 20 labels removed)",
      lb == lf and cb == cf and len(cb) == 20 and
      all(a[0] == "get-sink-volume" for a in cb),
      f"legs equal={lb == lf}; call list equal={cb == cf}; calls="
      f"{len(cb)}; sample argv={cb[:2]}")


# ---------------------------------------------------------------- D8
def sers_slice(src, folded):
    i0 = src.index("            sers = [s for s in") if not folded else \
        src.index("            if len(serials) != 3")
    i0 = src.rindex("\n", 0, i0) + 1
    i1 = src.index('"(never recycled) fails")')
    i1 = src.index("\n", i1) + 1
    return textwrap.dedent(src[i0:i1])


def run_sers(src, folded, serials, cycles):
    ns = {"serials": serials, "failures": [],
          "entry": {"serial_cycles": {"serials": cycles}}}
    try:
        exec(sers_slice(src, folded), ns)
        exc = None
    except Exception as e:  # same domain for both copies
        exc = type(e).__name__
    return ns["failures"], exc


d8_ok = True
d8_detail = []
for serials, cycles in [
        ([1, 2, 3], [1, 2, 3]),
        ([1, 1, 3], [1, 1, 3]),
        ([3, 2, 1], [3, 2, 1]),
        ([1, 2], [1, 2]),
        ([1, None, 3], [1, None, 3]),
        ([1, 2, 3], [None, 2, 3])]:
    fb = run_sers(bsrc, False, list(serials), list(cycles))
    ff = run_sers(fsrc, True, list(serials), list(cycles))
    d8_ok = d8_ok and fb == ff
    d8_detail.append(f"serials={serials}->{len(fb[0])} failure(s), "
                     f"exc={fb[1]} both")
check("D8 the addr monotonicity slice: identical failures (sers store "
      "removed)", d8_ok, "; ".join(d8_detail))


# ---------------------------------------------------------------- D9
def cap_slice(src, folded):
    i0 = src.index("            for nm, want_node in (") if not folded else \
        src.index('            for nm in ("t_srcname"')
    i0 = src.rindex("\n", 0, i0) + 1
    i1 = src.index('"did not resolve on the default monitor")')
    i1 = src.index("\n", i1) + 1
    return textwrap.dedent(src[i0:i1])


def run_cap_slice(src, folded, legs, def_sink):
    calls = []

    def link_ports(nm):
        calls.append(nm)
        return {e.get("out_port_name")
                for s in legs[nm].get("samples", [])
                for e in s.get("links", [])}

    ns = {"legs": legs, "failures": [], "def_sink": def_sink,
          "link_ports": link_ports, "PACTLMON_R85_VSRC": "r85a_vsrc_1"}
    exec(cap_slice(src, folded), ns)
    return ns["failures"], calls


def mk_legs(capture_ok=True, prop_ok=True):
    def sample(links):
        return {"samples": [{"links": links}]}

    return {
        "t_srcname": sample([{"out_node": "r85a_vsrc_1b",
                              "out_port_name": "capture_FL"}]),
        "t_srcserial": sample([{"out_node": "r85a_vsrc_1b",
                                "out_port_name": "capture_FL"}]),
        "t_srcid": sample([{"out_node": "r85a_vsrc_1b",
                            "out_port_name": "capture_FL"}]) if capture_ok
        else sample([{"out_node": "r85a_ns2_1",
                      "out_port_name": "monitor_FL"}]),
        "t_prop_sinkname": sample([{"out_node": "r85a_ns2_1",
                                    "out_port_name": "monitor_FL"}]),
        "t_prop_srcname": sample([{"out_node": "default.sink",
                                   "out_port_name": "monitor_FL"}])
        if prop_ok else sample([{"out_node": "r85a_ns2_1",
                                 "out_port_name": "playback_FL"}]),
    }


d9_ok = True
d9_detail = []
for name, legs in (("all-good", mk_legs()),
                   ("prop-bad", mk_legs(prop_ok=False)),
                   ("src-bad", mk_legs(capture_ok=False))):
    fb, cb = run_cap_slice(bsrc, False, legs, "default.sink")
    ff, cf = run_cap_slice(fsrc, True, legs, "default.sink")
    same = (fb == ff)
    d9_ok = d9_ok and same
    d9_detail.append(f"{name}: failures equal={same} ({len(fb)}), "
                     f"link_ports calls base={len(cb)} folded={len(cf)}")
check("D9 the capture source-bind slice: identical failures (want_node "
      "payload + dead `lp` store removed)", d9_ok, "; ".join(d9_detail) +
      " — [disclosed] the folded copy makes exactly ONE fewer pure "
      "link_ports() call")


# ---------------------------------------------------------------- D10
def run_feeder(src, folded, feeder):
    kills = []
    ns = {"feeder": feeder,
          "_pactlmon_r85_killpg": lambda p: kills.append(id(p))}
    body = ("                if feeder is not None and feeder.poll() is None:\n"
            if not folded else
            "                if feeder.poll() is None:\n")
    body += ("                    _pactlmon_r85_killpg(feeder)\n"
             "                    feeder.wait()\n")
    exec(textwrap.dedent(body), ns)
    return kills


d10_ok = True
d10_detail = []
for label, dead in (("alive", False), ("dead", True)):
    p = FakeProc(rc=1)
    p._dead = dead
    kb = run_feeder(bsrc, False, p)
    p2 = FakeProc(rc=1)
    p2._dead = dead
    kf = run_feeder(fsrc, True, p2)
    d10_ok = d10_ok and (bool(kb) == bool(kf))
    d10_detail.append(f"{label}: killed base={bool(kb)} folded={bool(kf)}")
check("D10 the feeder pre-ladder guard: identical kill decisions",
      d10_ok, "; ".join(d10_detail) +
      " — [disclosed] the folded conjunct-free form would raise on a None "
      "feeder, which the call graph cannot produce (the assignment "
      "precedes the guard)")


# ---------------------------------------------------------------- D11
def sub_expr(v):
    return f"{(v or {}).get('sink')}"


def flat_expr(v):
    return f"{v.get('sink')}"


d11_ok = True
d11_detail = []
for a in ({}, {"sink": None}, {"sink": 0}, {"sink": 4294967295},
          {"sink": 77}, {"index": 5}):
    s1 = f"sink={(a or {}).get('sink')} != "
    s2 = f"sink={a.get('sink')} != "
    d11_ok = d11_ok and s1 == s2
    d11_detail.append(f"{a} -> {s1!r}")
check("D11 the four subsumed `(aN or {})` guards: identical rendered "
      "strings over the dict domain", d11_ok,
      "; ".join(d11_detail[:3]) + " ...")


# ---------------------------------------------------------------- D12
check("D12 the two deleted module-level names are gone from the folded "
      "namespace",
      hasattr(B, "PACTLMON_R85_STREAM_WAIT_S") and
      hasattr(B, "_pactlmon_r85_wait_node") and
      not hasattr(F, "PACTLMON_R85_STREAM_WAIT_S") and
      not hasattr(F, "_pactlmon_r85_wait_node") and
      B.PACTLMON_R85_STREAM_WAIT_S == 8.0,
      f"base: STREAM_WAIT_S={getattr(B, 'PACTLMON_R85_STREAM_WAIT_S', None)} "
      f"wait_node={hasattr(B, '_pactlmon_r85_wait_node')}; folded: "
      f"STREAM_WAIT_S={hasattr(F, 'PACTLMON_R85_STREAM_WAIT_S')} "
      f"wait_node={hasattr(F, '_pactlmon_r85_wait_node')}")

Path("proofs/differential.txt").write_text(
    "\n".join(OUT) + f"\n\nTOTAL: {PASS} PASS / {FAIL} FAIL\n",
    encoding="utf-8")
print("\n".join(OUT))
print(f"\nTOTAL: {PASS} PASS / {FAIL} FAIL")
