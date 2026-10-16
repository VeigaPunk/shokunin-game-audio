"""Lock bookkeeping regression; no audio server or probe process needed."""

import fcntl
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


class WpstateLockTest(unittest.TestCase):
    def test_waiter_preserves_holder_and_owner_clears_stale_text(self):
        source = Path(__file__).with_name("measure_audio.py")
        spec = importlib.util.spec_from_file_location("r90_lock_fixture", source)
        fixture = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fixture)

        with tempfile.TemporaryDirectory(prefix="r90-lock-test-") as directory:
            path = Path(directory) / "family.lock"
            holder = os.open(path, os.O_RDWR | os.O_CREAT, 0o600)
            text = b"pid=999999999 ns=holder role=test nonce=holder\n"
            with patch.object(fixture, "_wpstate_r90_lock_path", return_value=path), \
                    patch.object(fixture, "WPSTATE_R90_LOCK_POLL_S", 0.01):
                try:
                    fcntl.flock(holder, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    os.write(holder, text)
                    busy = fixture._wpstate_r90_family_lock(wait_s=0.03)
                    self.assertIsNone(busy["fd"])
                    self.assertTrue(busy["block"].startswith(
                        "wpstate_r90_family_lock_busy:"))
                    self.assertEqual(path.read_bytes(), text)
                finally:
                    os.close(holder)

                acquired = fixture._wpstate_r90_family_lock(wait_s=0.03)
                self.assertIsNotNone(acquired["fd"])
                try:
                    self.assertIsNone(acquired["block"])
                    self.assertEqual(acquired.get("stale_pid_dead"), 999999999)
                finally:
                    fixture._wpstate_r90_lock_release(acquired["fd"])
                self.assertEqual(path.read_bytes(), b"")


if __name__ == "__main__":
    unittest.main()
