"""Failure-path guards; no audio/network, only freshly owned inert children."""
import ast
import json
import math
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest


class FinalGuardTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).with_name("measure_audio.py")
        cls.tree = ast.parse(path.read_text())
        names = {"_ebur_r93_run", "_pwstream_r98_teardown",
                 "_pwstream_r98_block", "_pwstream_r98_sb_start",
                 "_pwstream_r98_sb_stop", "pwstream_core_r98_probe",
                 "ebur_modes_r93_entry", "_ebur_r93_json_safe",
                 "_ebur_r93_num", "_ebur_r93_ctx", "_ebur_r93_teardown",
                 "_ebur_r93_block"}
        optional = {"_ebur_r93_cleanup_tapdir"}
        body = [n for n in cls.tree.body
                if isinstance(n, ast.FunctionDef) and n.name in names | optional]
        if not names <= {n.name for n in body}:
            raise AssertionError("missing actual final-family helpers")
        cls.code = compile(ast.Module(body=body, type_ignores=[]),
                           str(path), "exec")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="audio-final-guard-",
                                               dir="/tmp")

    def tearDown(self):
        self.tmp.cleanup()

    def namespace(self):
        ns = {"os": os, "math": math, "Path": Path, "signal": signal,
              "subprocess": subprocess, "tempfile": tempfile,
              "shutil": SimpleNamespace(which=lambda _: "/inert/tool"),
              "time": SimpleNamespace(sleep=lambda _: None),
              "PWSTREAM_R98_PID": 123, "PWSTREAM_R98_NS": "real-owned-sink",
              "PWSTREAM_R98_TOOLS": (), "_pwstream_r98_corelimit": lambda: None,
              "_EBUR_R93_TAPDIR_OWNERS": {}}
        exec(self.code, ns)
        return ns

    def test_unexpected_arm_failure_is_not_green(self):
        ns = self.namespace()
        ns["_ebur_r93_leg"] = lambda *_: {
            "tag": "test", "arm_failed": "feed refused", "error_class": "test"}
        entry, legs = {"failures": []}, {}
        ns["_ebur_r93_run"]({"stim": {}}, {"tag": "test"}, legs, entry)
        self.assertTrue(entry["failures"])
        self.assertTrue(entry["coverage_blocked"])
        self.assertEqual(len(legs), 1)

    def test_expected_refusal_retains_its_class(self):
        ns = self.namespace()
        ns["_ebur_r93_leg"] = lambda *_: {"tag": "test", "arm_failed": "refused"}
        entry = {"failures": []}
        ns["_ebur_r93_run"]({"stim": {}},
                            {"tag": "test", "expect_refusal": True}, {}, entry)
        self.assertFalse(entry["failures"])

    def test_optional_refusal_blocks_only_the_declared_cause(self):
        for cls in ("pwcli_module_load_fail", "feed_link_unbound", None):
            with self.subTest(error_class=cls):
                ns = self.namespace()
                ns["_ebur_r93_leg"] = lambda _ctx, spec: {
                    "tag": spec["tag"], "arm_failed": "setup refused",
                    "error_class": cls}
                entry, legs = {"failures": []}, {}
                ns["_ebur_r93_run"]({"stim": {}}, {
                    "tag": "notify_bogus",
                    "allow_refusal_class": "pwcli_module_load_fail"}, legs, entry)
                self.assertEqual(bool(entry["failures"]),
                                 cls != "pwcli_module_load_fail")
                self.assertTrue(entry["coverage_blocked"])
                self.assertIn("notify_bogus_r0", legs)

    def test_notify_descriptor_declares_and_forwards_its_optional_class(self):
        calls = [n for n in ast.walk(self.tree)
                 if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Name)
                 and n.func.id == "_ebur_r93_meter"
                 and any(k.arg == "tag" and isinstance(k.value, ast.Constant)
                         and k.value.value == "notify_bogus"
                         for k in n.keywords)]
        self.assertEqual(len(calls), 1)
        keywords = {k.arg: k.value for k in calls[0].keywords}
        value = keywords.get("allow_refusal_class")
        self.assertIsInstance(value, ast.Constant)
        self.assertEqual(value.value, "pwcli_module_load_fail")
        node = next(n for n in self.tree.body if isinstance(n, ast.FunctionDef)
                    and n.name == "_ebur_r93_meter")
        result = next(n.value for n in node.body if isinstance(n, ast.Return))
        fields = {k.value: v for k, v in zip(result.keys, result.values)}
        self.assertIsInstance(fields.get("allow_refusal_class"), ast.Name)
        self.assertEqual(fields["allow_refusal_class"].id, "allow_refusal_class")

    def test_every_ebur_entry_shares_the_failure_accumulator(self):
        entries = [n for n in self.tree.body if isinstance(n, ast.FunctionDef)
                   and n.name.startswith("ebur_") and n.name.endswith("_r93_entry")]
        self.assertEqual(len(entries), 9)
        for node in entries:
            with self.subTest(entry=node.name):
                prefix = []
                for statement in node.body:
                    if (isinstance(statement, ast.Assign) and any(
                            isinstance(t, ast.Name) and t.id == "ctx"
                            for t in statement.targets)):
                        break
                    prefix.append(statement)
                ns = self.namespace()
                ns["_ebur_r93_entry_head"] = lambda _: {"failures": []}
                exec(compile(ast.Module(body=prefix, type_ignores=[]),
                             "<actual-entry-initialization>", "exec"), ns)
                self.assertIs(ns["failures"], ns["entry"]["failures"])

    def test_arm_failure_survives_the_complete_modes_entry(self):
        ns = self.namespace()
        ns.update({"_ebur_r93_entry_head": lambda _: {"failures": []},
                   "_ebur_r93_ctx": lambda: {"stim": {}},
                   "_ebur_r93_meter": lambda **kwargs: kwargs,
                   "_ebur_r93_leg": lambda _, spec: {
                       "tag": spec["tag"], "arm_failed": "injected feed refusal"},
                   "_ebur_r93_teardown": lambda *_: None})
        row = ns["ebur_modes_r93_entry"]()
        self.assertTrue(any("injected feed refusal" in s for s in row["failures"]))

    def tap_namespace(self):
        ns = self.namespace()
        ns.update({"_ebur_r93_stimuli": lambda: {},
                   "_ebur_r93_refs": lambda: {},
                   "tempfile": SimpleNamespace(
                       mkdtemp=lambda **kw: tempfile.mkdtemp(dir=self.tmp.name, **kw),
                       TemporaryDirectory=lambda **kw:
                           tempfile.TemporaryDirectory(dir=self.tmp.name, **kw)),
                   "EBUR_R93_PREFIX": "r93a_owned_fixture",
                   "_pactlmon_r85_graph": lambda: {"nodes": {}},
                   "_capture_r77_sink_names_strict": lambda: [],
                   "_playback_r78_node_names": lambda: [],
                   "_btwit_r88_run": lambda *_a, **_kw: {"stdout": ""}})
        return ns

    def test_owned_tap_directory_is_cleaned_on_normal_and_blocked_exit(self):
        for blocked in (False, True):
            with self.subTest(blocked=blocked):
                ns = self.tap_namespace()
                ctx = ns["_ebur_r93_ctx"]()
                path = Path(ctx["tapdir"])
                (path / "capture.raw").write_text("owned fixture")
                json.dumps(ctx, allow_nan=False)
                entry, failures = {}, []
                try:
                    if blocked:
                        ns["_ebur_r93_block"](entry, failures, "fixture block", ctx)
                    else:
                        ns["_ebur_r93_teardown"](entry, failures, ctx)
                    self.assertFalse(path.exists())
                    self.assertIs(entry["tapdir_gone"], True)
                    self.assertNotIn(str(path), ns["_EBUR_R93_TAPDIR_OWNERS"])
                finally:
                    for owner in ns["_EBUR_R93_TAPDIR_OWNERS"].values():
                        owner.cleanup()
                    if path.exists():
                        shutil.rmtree(path)

    def test_unregistered_tap_path_is_never_deleted(self):
        ns = self.tap_namespace()
        path = Path(self.tmp.name) / "unregistered"
        path.mkdir()
        entry, failures = {}, []
        ns["_ebur_r93_teardown"](entry, failures, {"tapdir": str(path)})
        self.assertTrue(path.is_dir())
        self.assertIsNone(entry.get("tapdir_gone"))

    def test_whole_ebur_entry_block_is_not_green(self):
        ns = self.namespace()
        entry, failures = {}, []
        ns["_ebur_r93_block"](entry, failures, "missing prerequisite")
        self.assertTrue(failures)
        self.assertIs(entry["failures"], failures)

    def test_silent_readout_arms_require_successful_playback(self):
        for tag in ("ch_silent_mom", "m_range_only", "m_peak_only"):
            for rc in (None, -1, 0):
                with self.subTest(tag=tag, rc=rc):
                    ns = self.namespace()
                    ns["_ebur_r93_leg"] = lambda *_: {
                        "tag": tag, "play": {"exit_code": rc}}
                    entry = {"failures": []}
                    ns["_ebur_r93_run"]({"stim": {}}, {"tag": tag}, {}, entry)
                    self.assertEqual(bool(entry["failures"]), rc != 0)

    def test_whole_entry_block_preserves_legs_and_fails(self):
        ns = self.namespace()
        entry, failures = {"legs": {"partial": {}}}, []
        got = ns["_pwstream_r98_block"](entry, failures, "no prerequisite")
        self.assertIs(got, entry)
        self.assertEqual(got["legs"], {"partial": {}})
        self.assertIs(got["failures"], failures)
        self.assertTrue(failures)
        self.assertEqual(got["coverage_blocked"], ["no prerequisite"])

    def test_teardown_checks_loaded_names_not_aliases(self):
        for present in (False, True):
            with self.subTest(present=present):
                ns = self.namespace()
                ns.update({"_pactlmon_r85_unload_own": lambda *_: {},
                           "_pwstream_r98_graph": lambda **_: {"nodes": {}},
                           "_capture_r77_sink_names_strict":
                               lambda: ["real-owned-sink"] if present else [],
                           "_playback_r78_node_names": lambda: []})
                entry, failures = {}, []
                ns["_pwstream_r98_teardown"](
                    entry, failures,
                    {"ns": {"module_id": 1, "value": "real-owned-sink"}})
                self.assertEqual(entry["sinks_gone"],
                                 {"real-owned-sink": not present})
                self.assertEqual(bool(failures), present)

    def test_exception_after_load_still_runs_core_entry_teardown(self):
        ns = self.namespace()
        calls = []

        def fail(*_):
            raise RuntimeError("injected serial reader failure")

        ns.update({"_pwstream_r98_entry_head": lambda _: {},
                   "_pwstream_r98_probe_build": lambda _: (Path(__file__), {}),
                   "_pwstream_r98_load_ns": lambda name: {
                       "sink_seen": True, "value": name},
                   "_pwstream_r98_serial": fail,
                   "_pwstream_r98_teardown": lambda *_: calls.append("teardown"),
                   "_pwstream_r98_sweep_transient": lambda *_: None})
        with self.assertRaisesRegex(RuntimeError, "injected serial"):
            ns["pwstream_core_r98_probe"]()
        self.assertEqual(calls, ["teardown"])

    def test_all_shared_entries_have_finally_teardown(self):
        names = {f"pwstream_{part}_r98_probe"
                 for part in ("core", "run", "route", "cap", "xw")}
        for node in self.tree.body:
            if isinstance(node, ast.FunctionDef) and node.name in names:
                with self.subTest(entry=node.name):
                    final = [s for t in node.body if isinstance(t, ast.Try)
                             for s in t.finalbody]
                    calls = [n for s in final for n in ast.walk(s)
                             if isinstance(n, ast.Call)
                             and isinstance(n.func, ast.Name)
                             and n.func.id == "_pwstream_r98_teardown"]
                    self.assertEqual(len(calls), 1)

    def test_failed_setup_reaps_its_own_child(self):
        for socket_exists in (False, True):
            with self.subTest(socket_exists=socket_exists):
                ns = self.namespace()
                with tempfile.TemporaryDirectory(dir=self.tmp.name) as tmp:
                    root = Path(tmp)
                    (root / "sbx/test").mkdir(parents=True)
                    (root / "run").mkdir()
                    if socket_exists:
                        (root / "run/pipewire-0").touch()
                    children, handles = [], []

                    def spawn(argv, **kwargs):
                        self.assertEqual(argv, ["pipewire", "-c", "pipewire.conf"])
                        child = subprocess.Popen(
                            [sys.executable, "-c", "import time; time.sleep(60)"],
                            **kwargs)
                        children.append(child)
                        handles.append(kwargs["stdout"])
                        return child

                    def fail_create(*_args, **_kwargs):
                        raise subprocess.TimeoutExpired("synthetic create", 25)

                    ns["_pwstream_r98_sb_env"] = lambda *_: {
                        "PIPEWIRE_RUNTIME_DIR": str(root / "run")}
                    ns["subprocess"] = SimpleNamespace(
                        Popen=spawn, run=fail_create,
                        TimeoutExpired=subprocess.TimeoutExpired)
                    error = subprocess.TimeoutExpired if socket_exists else RuntimeError
                    try:
                        with self.assertRaises(error):
                            ns["_pwstream_r98_sb_start"](tmp, "test", with_wp=False)
                        self.assertEqual(len(children), 1)
                        self.assertIsNotNone(children[0].poll())
                        self.assertTrue(handles[0].closed)
                    finally:
                        for child in children:
                            if child.poll() is None:
                                child.terminate()
                            child.wait(timeout=5)
                        for handle in handles:
                            handle.close()


if __name__ == "__main__":
    unittest.main()
