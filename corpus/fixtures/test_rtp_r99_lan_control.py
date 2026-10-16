"""Exercise the LAN opt-in branch without any audio or network operation."""
import ast
import os
from pathlib import Path
import unittest
from unittest.mock import patch


class ControlReached(Exception):
    pass


class LanControlTest(unittest.TestCase):
    def run_guard(self, value):
        source = Path(__file__).with_name("measure_audio.py")
        tree = ast.parse(source.read_text())
        function = next(n for n in tree.body
                        if isinstance(n, ast.FunctionDef)
                        and n.name == "rtp_e2e_r99_entry")
        guards = [n for n in ast.walk(function) if isinstance(n, ast.If)
                  and "RTP_R99_ALLOW_LAN_CONTROL" in ast.unparse(n.test)]
        self.assertEqual(len(guards), 1)
        code = compile(ast.Module(body=[guards[0]], type_ignores=[]),
                       str(source), "exec")
        def barrier(*args, **kwargs):
            raise ControlReached()
        scope = {"os": os, "inst": object(), "iface": "test-interface",
                 "legs": {}, "entry": {}, "_rtp_r99_cli_open": barrier}
        env = {} if value is None else {"RTP_R99_ALLOW_LAN_CONTROL": value}
        with patch.dict(os.environ, env, clear=True):
            exec(code, scope)
        return scope

    def test_no_opt_in_is_unmeasured_and_never_opens_client(self):
        for value in (None, "", "0", "true"):
            with self.subTest(value=value):
                scope = self.run_guard(value)
                leg = scope["legs"]["e_lan_control"]
                self.assertIs(leg["measured"], False)
                self.assertIn("requires explicit operator approval", leg["blocked"])
                self.assertEqual(scope["entry"]["coverage_blocked"], [leg["blocked"]])

    def test_exact_opt_in_reaches_control_without_sending(self):
        with self.assertRaises(ControlReached):
            self.run_guard("1")


if __name__ == "__main__":
    unittest.main()
