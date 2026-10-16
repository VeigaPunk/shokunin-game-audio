"""Production constructor/snapshot data flow; no actor or audio execution."""
import ast
from datetime import datetime, timezone
from pathlib import Path
import re
import signal
import subprocess
from types import SimpleNamespace
import unittest


class StreamScopeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).with_name("measure_audio.py")
        cls.tree = ast.parse(path.read_text())
        required = {"_pwstream_r98_run", "_pwstream_r98_parse",
                    "_pwstream_r98_int", "_pwstream_r98_node_links"}
        optional = {"_pwstream_r98_probe_args", "_pwstream_r98_probe_name"}
        body = [n for n in cls.tree.body if isinstance(n, ast.FunctionDef)
                and n.name in required | optional]
        if not required <= {n.name for n in body}:
            raise AssertionError("missing production helpers")
        cls.code = compile(ast.Module(body=body, type_ignores=[]),
                           str(path), "exec")

    def namespace(self):
        seen = {"argv": [], "graph_env": []}

        def spawn(argv, **_kwargs):
            seen["argv"].append(list(argv))
            tag = next((a[5:] for a in reversed(argv[2:])
                        if a.startswith("name=")), argv[1])
            seen["actual_node"] = "r98a_" + tag
            return SimpleNamespace(
                returncode=0,
                communicate=lambda **_kw: (
                    b"R98 state=streaming cb_count=1 stream_error=-\n", b""))

        def graph(**kwargs):
            seen["graph_env"].append(kwargs.get("env"))
            return {"nodes": {1: {"name": seen["actual_node"]},
                              2: {"name": "r98a_ns_123"}},
                    "links": [{"out_node": 1, "in_node": 2, "state": "active"}]}

        ns = {"datetime": datetime, "timezone": timezone, "re": re,
              "signal": signal, "PWSTREAM_R98_PID": 123,
              "PWSTREAM_R98_PREFIX": "r98a_123",
              "time": SimpleNamespace(monotonic=lambda: 0.0,
                                      sleep=lambda _: None),
              "subprocess": SimpleNamespace(
                  Popen=spawn, PIPE=subprocess.PIPE, DEVNULL=subprocess.DEVNULL,
                  TimeoutExpired=subprocess.TimeoutExpired),
              "_pwstream_r98_sigreset": lambda: None,
              "_pwstream_r98_corelimit": lambda: None,
              "_pwstream_r98_graph": graph}
        exec(self.code, ns)
        return ns, seen

    def test_constructor_scopes_names_without_mutating_or_double_prefixing(self):
        cases = ((["emit", "name=probe"], "123_probe"),
                 (["emit"], "123_emit"),
                 (["emit", "name=1234_probe"], "123_1234_probe"))
        for args, expected in cases:
            with self.subTest(args=args):
                ns, seen = self.namespace()
                original = list(args)
                ns["_pwstream_r98_run"]("/inert/probe", args,
                                       retry_transient=False)
                names = [a[5:] for a in seen["argv"][-1]
                         if a.startswith("name=")]
                self.assertEqual(names, [expected])
                self.assertEqual(args, original)
                ns["_pwstream_r98_run"]("/inert/probe", seen["argv"][-1][1:],
                                       retry_transient=False)
                self.assertEqual(seen["argv"][-1], seen["argv"][-2])

    def test_live_snapshot_uses_probe_environment(self):
        ns, seen = self.namespace()
        env = {"PIPEWIRE_RUNTIME_DIR": "/private/inert",
               "PIPEWIRE_REMOTE": "pipewire-0"}
        name = (ns["_pwstream_r98_probe_name"]("probe")
                if "_pwstream_r98_probe_name" in ns else "r98a_probe")
        row = ns["_pwstream_r98_run"](
            "/inert/probe", ["emit", "name=probe"], env=env,
            live=0.1, node_name=name, retry_transient=False)
        self.assertEqual(seen["graph_env"], [env])
        self.assertEqual(row["link_snapshot"]["peers"], ["r98a_ns_123"])

    def test_active_snapshot_callers_use_the_name_authority(self):
        values = []
        for fn in self.tree.body:
            if (isinstance(fn, ast.FunctionDef)
                    and fn.name.startswith("pwstream_")
                    and fn.name.endswith("_r98_probe")):
                values.extend(k.value for n in ast.walk(fn)
                              if isinstance(n, ast.Call) for k in n.keywords
                              if k.arg == "node_name")
        self.assertTrue(values)
        self.assertTrue(all(
            isinstance(v, ast.Call) and isinstance(v.func, ast.Name)
            and v.func.id == "_pwstream_r98_probe_name" for v in values))


if __name__ == "__main__":
    unittest.main()
