"""Actual RTP arg builders and leak branch, without network operations."""
import ast
from pathlib import Path
import re
import unittest


class LoopbackTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).with_name("measure_audio.py")
        tree = ast.parse(path.read_text())
        names = {"_rtp_r99_sink_args", "_rtp_r99_source_args", "_rtp_r99_true"}
        helpers = [n for n in tree.body
                   if isinstance(n, ast.FunctionDef) and n.name in names]
        if {n.name for n in helpers} != names:
            raise AssertionError("missing actual RTP helpers")
        cls.helpers = compile(ast.Module(body=helpers, type_ignores=[]),
                              str(path), "exec")
        entry = next(n for n in tree.body
                     if isinstance(n, ast.FunctionDef)
                     and n.name == "rtp_e2e_r99_entry")
        calls = [n for n in ast.walk(entry)
                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)]
        source = min((n for n in calls
                      if n.func.id == "_rtp_r99_source_args"),
                     key=lambda n: n.lineno)
        sink = max((n for n in calls
                    if n.func.id == "_rtp_r99_sink_args"
                    and n.lineno < source.lineno),
                   key=lambda n: n.lineno)
        cls.source_call = compile(ast.Expression(body=source), str(path), "eval")
        cls.sink_call = compile(ast.Expression(body=sink), str(path), "eval")
        allowance = next(n for n in ast.walk(entry)
                         if isinstance(n, ast.Assign)
                         and any(isinstance(t, ast.Name) and t.id == "allowance"
                                 for t in n.targets))
        branches = [n for n in ast.walk(entry)
                    if isinstance(n, ast.If)
                    and ast.unparse(n.test) == "excess <= 0"]
        if len(branches) != 1:
            raise AssertionError("missing or ambiguous actual leak branch")
        cls.leak = compile(ast.Module(body=[allowance, branches[0]],
                                      type_ignores=[]), str(path), "exec")

    def namespace(self):
        ns = {"RTP_R99_SINK": "test_sink", "RTP_R99_SRC": "test_source",
              "RTP_R99_MCAST": "239.255.42.99", "RTP_R99_PORT": 46000,
              "RTP_R99_SESS": "test_session"}
        exec(self.helpers, ns)
        return ns

    def test_native_fragment_uses_one_loopback_port(self):
        ns = self.namespace()
        sink = eval(self.sink_call, ns)
        source = eval(self.source_call, ns)
        destination = re.search(r"\bdestination\.port\s*=\s*(\d+)", sink)
        receive = re.search(r"\bsource\.port\s*=\s*(\d+)", source)
        self.assertIsNotNone(destination)
        self.assertIsNotNone(receive)
        self.assertEqual(destination.group(1), "46000")
        self.assertEqual(receive.group(1), destination.group(1))
        self.assertIn('local.ifname = "lo"', sink)
        self.assertIn('local.ifname = "lo"', source)

    def test_standalone_injection_source_retains_its_default_port(self):
        source = self.namespace()["_rtp_r99_source_args"]()
        self.assertRegex(source, r"\bsource\.port\s*=\s*46001\b")

    def test_noise_never_masks_out_of_band_excess(self):
        cases = [(-1, 9000, False, False, "armed_below_band"),
                 (1, 9000, False, True, "coverage_block"),
                 (4001, 9000, True, False, "armed"),
                 (4001, 100, True, False, "armed"),
                 (4000, 100, False, False, "armed")]
        for excess, band, failed, blocked, verdict in cases:
            with self.subTest(excess=excess, band=band):
                ns = self.namespace()
                ns.update({"entry": {}, "failures": [], "iface": "test0",
                           "lan": {"emitted": 20000, "resolution": {}},
                           "band": band, "excess": excess})
                exec(self.leak, ns)
                self.assertEqual(bool(ns["failures"]), failed)
                self.assertEqual(bool(ns["entry"].get("coverage_blocked")),
                                 blocked)
                self.assertEqual(ns["lan"]["resolution"]["verdict"], verdict)


if __name__ == "__main__":
    unittest.main()
