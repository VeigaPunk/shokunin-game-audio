"""Clock/teardown guards; inert audio witnesses and one owned test child."""
import ast
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest


class SofaWitnessTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).with_name("measure_audio.py")
        tree = ast.parse(path.read_text())
        names = {"_sofa_r100_fail", "_sofa_r100_eq", "_sofa_r100_block",
                 "_sofa_r100_leg_ok", "_sofa_r100_teardown_laws",
                 "_sofa_r100_sandbox_start", "_sofa_r100_sandbox_stop",
                 "sofa_clock_r100_entry"}
        body = [n for n in tree.body
                if isinstance(n, ast.FunctionDef) and n.name in names]
        if {n.name for n in body} != names:
            raise AssertionError("missing actual sofa helpers")
        cls.code = compile(ast.Module(body=body, type_ignores=[]),
                           str(path), "exec")
        wanted = {"SOFA_R100_CLOCK_VARIANTS", "SOFA_R100_FC_RATE",
                  "SOFA_R100_N_SAMPLES", "SOFA_R100_FINE_ILD",
                  "SOFA_R100_MISMATCH_ILD_TOL"}
        cls.constants = {}
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id in wanted:
                        cls.constants[target.id] = ast.literal_eval(node.value)
        if set(cls.constants) != wanted:
            raise AssertionError("missing actual sofa constants")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="sofa-witness-test-",
                                               dir="/tmp")

    def tearDown(self):
        self.tmp.cleanup()

    def namespace(self):
        ns = {"Path": Path, "os": os, "signal": signal,
              "subprocess": subprocess, "tempfile": tempfile,
              "shutil": SimpleNamespace(which=lambda _: "/inert/tool",
                                        rmtree=shutil.rmtree),
              "time": SimpleNamespace(sleep=lambda _: None),
              "SOFA_R100_SRC": Path(__file__), "SOFA_R100_TMP": self.tmp.name,
              "_sofa_r100_preexec": lambda: None, **self.constants}
        exec(self.code, ns)
        return ns

    @staticmethod
    def valid_row(leg="test"):
        return {"leg": leg, "post_sweep": {"clean": True},
                "sink_unload": {"rc": 0},
                "module_unload_verified": {"matched": True,
                                           "own_nodes_after": []}}

    def clock_namespace(self, variant, props, alter=None, bad_log=False,
                        missing_log=False, abort=False):
        ns = self.namespace()
        calls = []
        ns["SOFA_R100_CLOCK_VARIANTS"] = ((variant, props),)
        ns["_sofa_r100_entry"] = lambda _: {"failures": [], "legs": {}}

        def start(root, name, _props):
            logs = root / "logs"
            logs.mkdir(exist_ok=True)
            if not missing_log:
                (logs / f"{name}-wp.log").write_text("")
            if bad_log:
                (logs / "a-wp.log").mkdir()
                (logs / "b-wp.log").write_text("ALSA witness\n")
            return {"test_variant": name}, {}, []

        def leg(entry, name, *_args, **_kwargs):
            if abort:
                raise RuntimeError("injected fixture failure")
            settings = {k.removeprefix("default."): str(v)
                        for k, v in props.items()}
            if alter is not None:
                key, value = alter
                if value is None:
                    settings.pop(key)
                else:
                    settings[key] = value
            row = self.valid_row(name)
            row["clock_mid"] = {"settings": settings}
            row["n_samples"] = ns["SOFA_R100_N_SAMPLES"][
                ns["SOFA_R100_FC_RATE"]]
            entry["legs"][name] = row
            return row

        ns.update({"_sofa_r100_sandbox_start": start,
                   "_sofa_r100_sandbox_stop": lambda _: [],
                   "_sofa_r100_leg": leg,
                   "_sofa_r100_teardown": lambda *_: calls.append("census"),
                   "_sofa_r100_close": lambda *_args, **_kwargs: None,
                   "_sofa_r100_ild": lambda _: None})
        return ns, calls

    def test_missing_unload_witness_cannot_pass(self):
        for mod in (None, {}, {"matched": False}):
            with self.subTest(mod=mod):
                ns = self.namespace()
                row = self.valid_row()
                row.pop("module_unload_verified")
                if mod is not None:
                    row["module_unload_verified"] = mod
                entry = {"failures": []}
                ns["_sofa_r100_teardown_laws"](entry, "test", row)
                self.assertTrue(entry["failures"])

    def test_verified_unload_control_passes(self):
        ns = self.namespace()
        entry = {"failures": []}
        ns["_sofa_r100_teardown_laws"](entry, "test", self.valid_row())
        self.assertFalse(entry["failures"])

    def test_each_requested_clock_property_needs_a_live_witness(self):
        for variant, props in self.constants["SOFA_R100_CLOCK_VARIANTS"]:
            for prop in props:
                key = prop.removeprefix("default.")
                for value in (None, "unapplied"):
                    with self.subTest(variant=variant, key=key, value=value):
                        ns, _ = self.clock_namespace(variant, props,
                                                     alter=(key, value))
                        row = ns["sofa_clock_r100_entry"]()
                        self.assertTrue(row["failures"])
                        self.assertTrue(any(key in s for s in row["failures"]))

    def test_matching_clock_controls_pass(self):
        for variant, props in self.constants["SOFA_R100_CLOCK_VARIANTS"]:
            with self.subTest(variant=variant):
                ns, calls = self.clock_namespace(variant, props)
                row = ns["sofa_clock_r100_entry"]()
                self.assertFalse(row["failures"])
                self.assertEqual(row["wp_alsa_lines"], 0)
                self.assertEqual(calls, ["census"])

    def test_unreadable_log_cannot_be_cancelled_by_one_alsa_line(self):
        variant, props = self.constants["SOFA_R100_CLOCK_VARIANTS"][0]
        ns, _ = self.clock_namespace(variant, props, bad_log=True)
        row = ns["sofa_clock_r100_entry"]()
        self.assertTrue(row["failures"])
        self.assertIsNone(row["wp_alsa_lines"])
        self.assertTrue(row["wp_alsa_log_errors"])

    def test_missing_session_manager_logs_are_not_a_zero_count(self):
        variant, props = self.constants["SOFA_R100_CLOCK_VARIANTS"][0]
        ns, _ = self.clock_namespace(variant, props, missing_log=True)
        row = ns["sofa_clock_r100_entry"]()
        self.assertTrue(row["failures"])
        self.assertIsNone(row["wp_alsa_lines"])

    def test_clock_census_still_runs_when_a_leg_raises(self):
        variant, props = self.constants["SOFA_R100_CLOCK_VARIANTS"][0]
        ns, calls = self.clock_namespace(variant, props, abort=True)
        with self.assertRaisesRegex(RuntimeError, "injected fixture failure"):
            ns["sofa_clock_r100_entry"]()
        self.assertEqual(calls, ["census"])

    def test_late_log_open_failure_reaps_the_already_spawned_child(self):
        ns = self.namespace()
        root = Path(self.tmp.name)
        (root / "rt").mkdir()
        (root / "rt/pipewire-0").touch()
        (root / "logs/test-wp.log").mkdir(parents=True)
        children, handles = [], []

        def spawn(argv, **kwargs):
            self.assertEqual(argv, ["pipewire", "-c", "pipewire.conf"])
            child = subprocess.Popen(
                [sys.executable, "-c", "import time; time.sleep(60)"], **kwargs)
            children.append(child)
            handles.append(kwargs["stdout"])
            return child

        ns["_sofa_r100_env"] = lambda *_args, **_kwargs: {}
        ns["subprocess"] = SimpleNamespace(Popen=spawn, DEVNULL=subprocess.DEVNULL,
                                           TimeoutExpired=subprocess.TimeoutExpired)
        try:
            with self.assertRaises(IsADirectoryError):
                ns["_sofa_r100_sandbox_start"](root, "test", {})
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
