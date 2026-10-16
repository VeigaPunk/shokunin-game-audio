"""r97 ownership and reaping without running an audio family."""
import ast
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch


class GuardTest(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).with_name("measure_audio.py")
        wanted = {"_wppol_r97_spawn", "_wppol_r97_own", "_wppol_r97_kill"}
        body = [n for n in ast.parse(path.read_text()).body
                if isinstance(n, ast.FunctionDef) and n.name in wanted]
        self.assertEqual({n.name for n in body}, wanted)
        self.ns = {"os": os, "Path": Path, "signal": signal, "time": time,
                   "subprocess": subprocess, "WPPOL_R97_CHILDREN": {}}
        exec(compile(ast.Module(body=body, type_ignores=[]), str(path), "exec"),
             self.ns)
        self.tmp = tempfile.TemporaryDirectory(prefix="r97-guard-test-")
        self.root = Path(self.tmp.name)
        self.children = []

    def tearDown(self):
        for proc in self.children:
            if proc.poll() is None:
                proc.kill()
            proc.wait(timeout=5)
        self.tmp.cleanup()

    def plain(self, mention=False, env_mention=False):
        argv = [sys.executable, "-c", "import time; time.sleep(60)"]
        if mention:
            argv.append(str(self.root))
        env = dict(os.environ)
        if env_mention:
            env["XDG_STATE_HOME"] = str(self.root / "state")
        proc = subprocess.Popen(argv, env=env, start_new_session=True)
        self.children.append(proc)
        return proc

    def own(self):
        proc = self.ns["_wppol_r97_spawn"](
            [sys.executable, "-c", "import time; time.sleep(60)"],
            env=dict(os.environ, XDG_RUNTIME_DIR=str(self.root / "run")),
            root=self.root)
        self.children.append(proc)
        return proc

    def test_foreign_argv_mention_is_not_signalled(self):
        proc = self.plain(mention=True)
        self.assertFalse(self.ns["_wppol_r97_own"](self.root, proc.pid))
        row = self.ns["_wppol_r97_kill"](self.root, proc.pid)
        self.assertFalse(row["killed"])
        self.assertEqual(row["reason"], "REFUSED foreign pid")
        self.assertIsNone(proc.poll())

    def test_foreign_environment_mention_is_not_signalled(self):
        proc = self.plain(env_mention=True)
        self.assertFalse(self.ns["_wppol_r97_own"](self.root, proc.pid))
        row = self.ns["_wppol_r97_kill"](self.root, proc.pid)
        self.assertFalse(row["killed"])
        self.assertIsNone(proc.poll())

    def test_owned_environment_only_child_is_reaped(self):
        proc = self.own()
        self.assertTrue(self.ns["_wppol_r97_own"](self.root, proc.pid))
        row = self.ns["_wppol_r97_kill"](self.root, proc.pid, grace=1)
        self.assertTrue(row["killed"])
        self.assertEqual(row["sig"], int(signal.SIGTERM))
        self.assertEqual(proc.returncode, -signal.SIGTERM)
        self.assertFalse(self.ns["_wppol_r97_own"](self.root, proc.pid))

    def test_wrong_root_cannot_signal_registered_child(self):
        proc = self.own()
        row = self.ns["_wppol_r97_kill"](self.root / "other", proc.pid)
        self.assertFalse(row["killed"])
        self.assertEqual(row["reason"], "REFUSED foreign pid")
        self.assertIsNone(proc.poll())

    def test_unregistered_process_and_invalid_ids_are_refused(self):
        proc = self.plain()
        for pid in (proc.pid, os.getpid(), 0, -1):
            with self.subTest(pid=pid):
                row = self.ns["_wppol_r97_kill"](self.root, pid)
                self.assertFalse(row["killed"])
                self.assertEqual(row["reason"], "REFUSED foreign pid")
        self.assertIsNone(proc.poll())

    def test_missing_root_is_rejected_before_spawn(self):
        with patch.object(subprocess, "Popen") as popen:
            with self.assertRaises(ValueError):
                self.ns["_wppol_r97_spawn"](["unused"])
            popen.assert_not_called()


if __name__ == "__main__":
    unittest.main()
