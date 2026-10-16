#!/usr/bin/env python3
"""r84 simplifier DIFFERENTIAL proofs — execute base vs folded on scratch
imports with stubbed I/O, and compare observable outputs.

Read-only for the repository; writes only proofs/differential.txt and the
scratch module copies under proofs/dyn/.

Checks:
  D0  per-function source census: only the 9 intended units differ
  D1  _alsapw_r84_st_leg            (ctx param removed) -> identical rec
  D2  _alsapw_r84_prop_leg          (hit store + g init removed) -> identical rec
  D3  _alsapw_r84_wait_moved        (pre-loop fetch removed) -> identical leaf,
      exactly one fewer reader call
  D4  _alsapw_r84_teardown          ((leaf or {}) + (loads or {}) removed)
      -> identical entry + identical unload call list
  D5  _alsapw_r84_block             ((leaf or {}) removed; loads guard kept)
      -> identical entry, incl. the loads=None path
  D6  alsapw_dev_lattice_r84_entry ebusy slice (init pair removed + hold_note
      -> flipped) -> identical loop outcome and identical recorded dict
  D7  class-method replay: the sticky guard and the errclass classifier behave
      identically on the same inputs
"""
import ast
import importlib.util
import io
import json
import shutil
import textwrap
import sys
import time
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


B = load("r84_base_mod", DYN / "base.py")
F = load("r84_folded_mod", DYN / "folded.py")

# ---------------------------------------------------------------- D0
def unit_map(src):
    tree = ast.parse(src)
    lines = src.splitlines()
    units = {}
    for n in tree.body:
        if isinstance(n, ast.FunctionDef):
            units[n.name] = "\n".join(lines[n.lineno - 1:n.end_lineno])
    consts = {}
    for n in tree.body:
        if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name):
            consts[n.targets[0].id] = "\n".join(lines[n.lineno - 1:n.end_lineno])
    return units, consts


bu, bc = unit_map(Path("proofs/base-measure_audio.py").read_text())
fu, fc = unit_map(Path("proofs/folded/measure_audio.py").read_text())
changed_fn = sorted(k for k in bu if bu[k] != fu.get(k))
changed_const = sorted(k for k in bc if bc[k] != fc.get(k))
EXPECT_FN = sorted(["_alsapw_r84_st_leg", "_alsapw_r84_teardown",
                    "_alsapw_r84_block", "_alsapw_r84_wait_moved",
                    "_alsapw_r84_prop_leg", "_alsapw_r84_sticky_leg",
                    "alsapw_dev_lattice_r84_entry",
                    "alsapw_negctl_r84_entry", "alsapw_pw_args_r84_entry"])
check("D0 only the intended units differ (9 functions + 1 constant)",
      changed_fn == EXPECT_FN and changed_const == ["ALSAPW_R84_LINK_WAIT_S"] and
      len(bu) == len(fu),
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
    def __init__(self, rc=0, err=b"", pid=4242):
        self.returncode = rc
        self.stderr = FakeStderr(err)
        self.pid = pid
        self._alive = False

    def poll(self):
        return None if self._alive else self.returncode

    def wait(self, timeout=None):
        return self.returncode


def patch(mod, **kw):
    saved = {}
    for k, v in kw.items():
        saved[k] = getattr(mod, k)
        setattr(mod, k, v)
    return saved


def unpatch(mod, saved):
    for k, v in saved.items():
        setattr(mod, k, v)


# ---------------------------------------------------------------- D1
def d1():
    res = {}
    for tag, mod in (("base", B), ("folded", F)):
        ft = FakeTime()
        proc = FakeProc(rc=0, err=b"Playing WAVE 'x'\n")
        calls = {"spawn": [], "graph": 0}
        graph = {"nodes": {1: {"name": "alsa_playback.speaker-test",
                               "state": "running", "media_class": "Stream/Output/Audio",
                               "props": {}}},
                 "ports": {}, "links": []}
        def spawn(argv, env=None, _c=calls):
            _c["spawn"].append(list(argv))
            return proc
        def graphf(_c=calls):
            _c["graph"] += 1
            return graph
        def killpg(p, sig=None):
            pass
        s = patch(mod, time=ft, _alsapw_r84_spawn=spawn,
                  _alsapw_r84_graph=graphf, _alsapw_r84_killpg=killpg)
        try:
            ctx = {"tmp": "/tmp/x", "redact": ("/tmp/x",)}
            if tag == "base":
                rec = mod._alsapw_r84_st_leg("pipewire:NODE=ns", ctx,
                                             ["-c", "2", "-l", "1"])
            else:
                rec = mod._alsapw_r84_st_leg("pipewire:NODE=ns",
                                             ["-c", "2", "-l", "1"])
        finally:
            unpatch(mod, s)
        res[tag] = (rec, calls, ft.sleeps)
    check("D1 st_leg: identical rec, identical spawn argv, identical sleeps",
          res["base"] == res["folded"],
          f"recs equal={res['base'][0] == res['folded'][0]} "
          f"argv={res['base'][1]['spawn']} graph_calls="
          f"{res['base'][1]['graph']}/{res['folded'][1]['graph']} sleeps="
          f"{res['base'][2]}=={res['folded'][2]}")


# ---------------------------------------------------------------- D2
def d2():
    import subprocess as sp
    res = {}
    real_popen = sp.Popen
    for tag, mod in (("base", B), ("folded", F)):
        ft = FakeTime()
        proc = FakeProc(rc=0, err=b"", pid=777)
        graph = {"nodes": {11: {"name": "paplay", "state": "running",
                                "media_class": "Stream/Output/Audio",
                                "props": {"application.process.id": "777",
                                          "media.role": "Communication"}}},
                 "ports": {}, "links": []}
        def popen(argv, **kw):
            return proc
        def graphf():
            return graph
        def leaf_pid(pid, what="sink-inputs"):
            return {"index": 3, "sink": 42, "properties": {"media.role": "phone"}}
        s = patch(mod, time=ft, _alsapw_r84_graph=graphf,
                  _alsapw_r84_stream_leaf_pid=leaf_pid)
        sp.Popen = popen
        try:
            ctx = {"tmp": "/tmp/x", "ns": "ns", "prop_tone": "/tmp/t.wav"}
            rec = mod._alsapw_r84_prop_leg("role_comm", ctx,
                                           {"PULSE_PROP_media.role": "Communication"},
                                           "paplay")
        finally:
            sp.Popen = real_popen
            unpatch(mod, s)
        res[tag] = rec
    check("D2 prop_leg: byte-identical rec (hit store + g init invisible)",
          res["base"] == res["folded"] and
          set(res["base"]) == {"argv_head", "player", "env_extra", "pid",
                               "node", "stream", "exit_code", "signal",
                               "killed", "wall_s", "stderr_tail",
                               "error_class"},
          f"equal={res['base'] == res['folded']} keys={sorted(res['base'])} "
          f"error_class={res['base'].get('error_class')!r} "
          f"has_hit={'hit' in res['base']}")


# ---------------------------------------------------------------- D3
def d3():
    """The stub models the HOST, not the call index: the stream's sink flips
    at a fixed point on the simulated clock, so both copies see the same
    stream state at the same wall time; only the number of reads differs."""
    res = {}
    for tag, mod in (("base", B), ("folded", F)):
        ft = FakeTime()
        calls = []

        def leaf(t, what="sink-inputs", _c=calls, _ft=ft):
            _c.append(_ft.t)
            return {"sink": 5 if _ft.t < 1000.15 else 9}

        s = patch(mod, time=ft, _alsapw_r84_stream_leaf=leaf)
        try:
            out = mod._alsapw_r84_wait_moved("tag", 5)
        finally:
            unpatch(mod, s)
        res[tag] = (out, len(calls), ft.sleeps)
    check("D3 wait_moved: identical returned leaf; exactly one fewer reader "
          "call; same sleep pattern",
          res["base"][0] == res["folded"][0] == {"sink": 9} and
          res["base"][1] == res["folded"][1] + 1 and
          res["base"][2] == res["folded"][2],
          f"base=(leaf {res['base'][0]}, reads {res['base'][1]}, sleeps "
          f"{res['base'][2]}) folded=(leaf {res['folded'][0]}, reads "
          f"{res['folded'][1]}, sleeps {res['folded'][2]})")


# ---------------------------------------------------------------- D4
def d4():
    res = {}
    for tag, mod in (("base", B), ("folded", F)):
        unloads = []
        def unload(mid, sink_name=None, _u=unloads):
            _u.append((mid, sink_name))
            return {"rc": 0}
        def sinks_now():
            return {"foreign"}
        def node_names():
            return ["foreign", "r84a_ns_1"]
        s = patch(mod, _gst_r81_unload_own=unload,
                  _capture_r77_sink_names_strict=sinks_now,
                  _playback_r78_node_names=node_names)
        try:
            for loads in ({"r84a_ns_1": {"module_id": 7}},
                          {"r84a_ns_1": {"module_id": None}}):
                entry, failures = {}, []
                mod._alsapw_r84_teardown(entry, failures, loads)
                res.setdefault(tag, []).append((entry, failures))
        finally:
            unpatch(mod, s)
    check("D4 teardown: identical entries/failures/unload calls for dict loads",
          res["base"] == res["folded"],
          f"base={json.dumps(res['base'], sort_keys=True)[:300]} "
          f"equal={res['base'] == res['folded']}")


# ---------------------------------------------------------------- D5
def d5():
    res = {}
    for tag, mod in (("base", B), ("folded", F)):
        unloads = []
        def unload(mid, sink_name=None, _u=unloads):
            _u.append((mid, sink_name))
            return {"rc": 0}
        s = patch(mod, _gst_r81_unload_own=unload)
        try:
            outs = []
            for loads in (None, {"r84a_ns_1": {"module_id": 7}}):
                entry, failures = {}, []
                outs.append(mod._alsapw_r84_block(entry, failures, "msg",
                                                  loads))
            res[tag] = outs
        finally:
            unpatch(mod, s)
    check("D5 block: identical entries for the loads=None and dict paths",
          res["base"] == res["folded"] and
          res["base"][0]["blocked"] == "msg",
          f"equal={res['base'] == res['folded']} first="
          f"{json.dumps(res['base'][0], sort_keys=True)[:200]}")


# ---------------------------------------------------------------- D6
def d6():
    def slice_src(mod_src, tag):
        tree = ast.parse(mod_src)
        lines = mod_src.splitlines()
        dev = [n for n in tree.body if isinstance(n, ast.FunctionDef) and
               n.name == "alsapw_dev_lattice_r84_entry"][0]
        while_node = [n for n in ast.walk(dev) if isinstance(n, ast.While) and
                      "5.0" in ast.unparse(n.test)][0]
        hold_assign = [n for n in ast.walk(dev) if isinstance(n, ast.Assign) and
                       isinstance(n.targets[0], ast.Subscript) and
                       "ebusy_hold" in ast.unparse(n.targets[0]) and
                       n.lineno > while_node.lineno][0]
        t0_assign = [n for n in ast.walk(dev) if isinstance(n, ast.Assign) and
                     ast.unparse(n.targets[0]) == "t0" and
                     n.lineno < while_node.lineno][-1]
        return textwrap.dedent(
            "\n".join(lines[t0_assign.lineno - 1:hold_assign.end_lineno]))

    res = {}
    for tag, mod, path in (("base", B, "proofs/base-measure_audio.py"),
                           ("folded", F, "proofs/folded/measure_audio.py")):
        src = Path(path).read_text()
        code = slice_src(src, tag)
        for scenario, seq in (("flipped", [("card0/pcm3c", "closed")]),
                              ("foreign-running",
                               [("card0/pcm3c", "RUNNING")])):
            ft = FakeTime()
            calls = []
            def states(_seq=seq, _c=calls):
                _c.append(1)
                return dict(_seq)
            hold = FakeProc(rc=None)
            hold._alive = True
            ns = {"time": ft, "_alsapw_r84_pcm_states": states,
                  "states0": {}, "hold": hold, "legs": {},
                  "held_pcm": None, "states_held": {}}
            exec(compile(code, f"<{tag}:{scenario}>", "exec"), ns)
            res.setdefault(scenario, {})[tag] = (
                ns["legs"]["ebusy_hold"], ns["held_pcm"], ft.sleeps)
    ok = all(res[s]["base"] == res[s]["folded"] for s in res)
    check("D6 dev_lattice ebusy slice: identical outcome + recorded dict",
          ok and set(res) == {"flipped", "foreign-running"},
          f"scenarios={ {s: res[s]['base'] for s in res} } equal={ok}")


# ---------------------------------------------------------------- D7
def d7():
    outs = {}
    for tag, mod in (("base", B), ("folded", F)):
        outs[tag] = {
            "errclass": [mod._alsapw_r84_errclass(t)[0] for t in
                         ("Unknown PCM pulse\n", "",
                          "arecord: set_params:1462: Unable to install hw "
                          "params:\nTICK_TIME: [0 0]\n",
                          "Invalid volume specification\n", "noise\n")],
            "pcm_name": [mod._alsapw_r84_unknown_pcm_name(t) for t in
                         ("Unknown PCM \n", "Unknown PCM -d\n", "x")],
            "nz": mod._alsapw_r84_si_percent({"volume": {
                "front-left": {"value_percent": "30%"}}}),
        }
    check("D7 classifier + leaf helpers identical on the same inputs",
          outs["base"] == outs["folded"],
          f"{outs['base']} == {outs['folded']}")


for fn in (d1, d2, d3, d4, d5, d6, d7):
    fn()

OUT.append(f"\nTOTAL: {PASS} PASS / {FAIL} FAIL")
Path("proofs/differential.txt").write_text("\n".join(OUT) + "\n")
print("\n".join(OUT))
sys.exit(1 if FAIL else 0)
