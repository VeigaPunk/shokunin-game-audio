"""Missing-witness branches from production; all I/O is inert callbacks."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest


class MissingWitnessTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).with_name("measure_audio.py")
        tree = ast.parse(path.read_text())
        names = {"_rtp_r99_sink_args", "_rtp_r99_unmeasured", "_rtp_r99_true"}
        helpers = [n for n in tree.body if isinstance(n, ast.FunctionDef)
                   and n.name in names]
        cls.helpers = compile(ast.Module(body=helpers, type_ignores=[]),
                              str(path), "exec")
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                  and n.name == "rtp_e2e_r99_entry")
        guards = [n for n in ast.walk(fn) if isinstance(n, ast.If)
                  and "RTP_R99_ALLOW_LAN_CONTROL" in ast.unparse(n.test)]
        if len(guards) != 1:
            raise AssertionError("missing or ambiguous physical-LAN gate")
        cls.control = compile(ast.Module(body=guards, type_ignores=[]),
                              str(path), "exec")
        branch = next(n for n in ast.walk(fn) if isinstance(n, ast.If)
                      and ast.unparse(n.test) == "not iface")
        for parent in ast.walk(fn):
            body = getattr(parent, "body", None)
            if not isinstance(body, list) or branch not in body:
                continue
            stop = body.index(branch)
            start = next(i for i, n in enumerate(body[:stop])
                         if isinstance(n, ast.Assign)
                         and any(isinstance(t, ast.Name) and t.id == "iface"
                                 for t in n.targets))
            cls.lan = compile(ast.Module(body=body[start:stop + 1],
                                         type_ignores=[]), str(path), "exec")
            break
        else:
            raise AssertionError("missing actual LAN statement group")
        cls.aborts = {}
        for fn in tree.body:
            if (isinstance(fn, ast.FunctionDef) and fn.name.startswith("rtp_")
                    and fn.name.endswith("_r99_entry")):
                for handler in ast.walk(fn):
                    if (isinstance(handler, ast.ExceptHandler)
                            and isinstance(handler.type, ast.Name)
                            and handler.type.id == "Exception"):
                        cls.aborts[fn.name] = compile(ast.Module(
                            body=handler.body, type_ignores=[]),
                            str(path), "exec")

    def namespace(self, iface="test0", cli=None, optin=None):
        def barrier(*_args, **_kwargs):
            raise AssertionError("unexpected actor/tap/play operation")

        ns = {
            "entry": {"default_iface": iface}, "legs": {}, "failures": [],
            "inst": object(), "tone": Path("/inert/unused.wav"),
            "os": SimpleNamespace(environ={"RTP_R99_ALLOW_LAN_CONTROL": optin}),
            "time": SimpleNamespace(sleep=lambda _: None),
            "RTP_R99_MCAST": "239.255.42.99", "RTP_R99_PORT": 46000,
            "RTP_R99_SINK": "test_sink", "RTP_R99_SESS": "test_session",
            "_rtp_r99_ifcounters": lambda _: {"tx_packets": 0},
            "_rtp_r99_cli_open": lambda _: (cli, "injected open failure"),
            "_rtp_r99_cli_load": lambda *_args: None,
            "_rtp_r99_node": lambda *_args: {"reached": False},
            "_rtp_r99_reap": lambda *_args: None,
            "_rtp_r99_tap": barrier, "_rtp_r99_play": barrier,
        }
        exec(self.helpers, ns)
        return ns

    def assert_blocked(self, ns, key):
        leg = ns["legs"].get(key, {})
        self.assertIs(leg.get("measured"), False)
        self.assertIn(key, leg.get("blocked", ""))
        self.assertIn(leg["blocked"], ns["entry"]["coverage_blocked"])

    def test_no_iface_preserves_both_named_legs(self):
        ns = self.namespace(iface=None)
        exec(self.lan, ns)
        for key in ("e_lan", "e_lan_control"):
            self.assert_blocked(ns, key)

    def test_missing_cli_blocks_both_legs_without_actor_operations(self):
        ns = self.namespace(optin="1")
        exec(self.lan, ns)
        for key in ("e_lan", "e_lan_control"):
            self.assert_blocked(ns, key)

    def test_unreached_sink_blocks_both_legs_without_tap_or_play(self):
        ns = self.namespace(cli=object(), optin="1")
        exec(self.lan, ns)
        for key in ("e_lan", "e_lan_control"):
            self.assert_blocked(ns, key)

    def test_unexpected_entry_abort_is_a_harness_failure(self):
        self.assertTrue(self.aborts)
        for name, code in self.aborts.items():
            with self.subTest(entry=name):
                ns = {"entry": {}, "failures": [],
                      "exc": RuntimeError("injected backend exception")}
                exec(code, ns)
                self.assertTrue(ns["failures"])
                self.assertEqual(ns["failures"], ns["entry"]["coverage_blocked"])

    def test_observed_control_can_be_measured_and_refuted(self):
        ns = self.namespace(cli=object(), optin="1")
        ns.update({"iface": "test0",
                   "_rtp_r99_node": lambda *_args: {"reached": True},
                   "_rtp_r99_play": lambda *_args: (None, {"inert": True})})
        exec(self.control, ns)
        leg = ns["legs"]["e_lan_control"]
        self.assertIs(leg["measured"], True)
        self.assertEqual(leg["arm_tx_packets"], 0)
        self.assertTrue(ns["failures"])


if __name__ == "__main__":
    unittest.main()
