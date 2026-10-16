"""Real Unix locks with synthetic names; no audio or network operations."""
import ast
from contextlib import redirect_stdout
import fcntl
import io
import json
import os
from pathlib import Path
import re
import stat
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import uuid


WRAPPERS = {
    "_gstfrz_r91_family_lock": "gstfrz-r91",
    "_fc92_family_lock": "filterchain-r92",
    "_ebur_r93_family_lock": "ebur-r93",
    "_pulsecli_r96_family_lock": "pulsecli-r96",
    "_wppol_r97_family_lock": "wppol-r97",
    "_pwstream_r98_family_lock": "pwstream-r98",
    "_rtp_r99_family_lock": "rtp-r99",
    "_sofa_r100_family_lock": "sofa-r100",
}


class HostLockTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).with_name("measure_audio.py")
        cls.tree = ast.parse(path.read_text())
        wanted = set(WRAPPERS) | {"_audio_host_family_lock"}
        body = [n for n in cls.tree.body
                if isinstance(n, ast.FunctionDef) and n.name in wanted]
        if {n.name for n in body} != wanted:
            raise AssertionError("missing host lock helper/wrapper")
        cls.code = compile(ast.Module(body=body, type_ignores=[]),
                           str(path), "exec")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="audio-lock-test-")
        self.paths = []
        self.fds = []
        self.ns = self.namespace(Path(self.tmp.name) / "first")

    def tearDown(self):
        for fd in self.fds:
            os.close(fd)
        for path in self.paths:
            path.unlink(missing_ok=True)
        self.tmp.cleanup()

    def namespace(self, root):
        ns = {"os": os, "Path": Path, "re": re, "stat": stat,
              "time": time, "fcntl": fcntl, "ROOT": root}
        exec(self.code, ns)
        return ns

    def family(self, label):
        name = f"unit-{os.getpid()}-{uuid.uuid4().hex}-{label}"
        path = Path("/tmp") / f"shokunin-audio-{os.getuid()}-{name}.lock"
        self.assertFalse(os.path.lexists(path))
        self.paths.append(path)
        return name, path

    def acquire(self, family, ns=None):
        fd = (ns or self.ns)["_audio_host_family_lock"](family, wait_s=0.02)
        self.fds.append(fd)
        return fd

    def close(self, fd):
        os.close(fd)
        self.fds.remove(fd)

    def test_cross_root_and_env_waiter_cannot_erase_holder(self):
        family, path = self.family("shared")
        other = self.namespace(Path(self.tmp.name) / "second")
        with patch.dict(os.environ, {"XDG_RUNTIME_DIR": "/not-first",
                                     "TMPDIR": "/not-first"}):
            fd = self.acquire(family)
        os.ftruncate(fd, 0)
        os.lseek(fd, 0, os.SEEK_SET)
        os.write(fd, b"holder-text\n")
        with patch.dict(os.environ, {"XDG_RUNTIME_DIR": "/not-second",
                                     "TMPDIR": "/not-second"}):
            with self.assertRaisesRegex(RuntimeError, "wait timed out"):
                other["_audio_host_family_lock"](family, wait_s=0.02)
        self.assertEqual(path.read_bytes(), b"holder-text\n")
        with self.assertRaisesRegex(RuntimeError, "wait timed out"):
            self.ns["_audio_host_family_lock"](family, wait_s=0.02)
        self.close(fd)
        self.acquire(family, other)
        self.assertFalse((self.ns["ROOT"] / "live").exists())
        self.assertFalse((other["ROOT"] / "live").exists())

    def test_different_families_do_not_exclude(self):
        first, _ = self.family("first")
        second, _ = self.family("second")
        self.acquire(first)
        self.acquire(second)

    def test_symlink_is_refused_without_touching_target(self):
        family, path = self.family("symlink")
        target = Path(self.tmp.name) / "target"
        target.write_bytes(b"untouched\n")
        path.symlink_to(target)
        with self.assertRaisesRegex(RuntimeError, "family lock"):
            self.acquire(family)
        self.assertEqual(target.read_bytes(), b"untouched\n")

    def test_nonprivate_lock_is_refused_without_truncation(self):
        family, path = self.family("mode")
        path.write_bytes(b"untouched\n")
        path.chmod(0o644)
        with self.assertRaisesRegex(RuntimeError, "non-private"):
            self.acquire(family)
        self.assertEqual(path.read_bytes(), b"untouched\n")

    def test_hardlink_is_refused_without_touching_target(self):
        family, path = self.family("hardlink")
        with tempfile.TemporaryDirectory(dir="/tmp") as tmp:
            target = Path(tmp) / "target"
            target.write_bytes(b"untouched\n")
            target.chmod(0o600)
            os.link(target, path)
            with self.assertRaisesRegex(RuntimeError, "non-private"):
                self.acquire(family)
            self.assertEqual(target.read_bytes(), b"untouched\n")

    def test_foreign_owner_metadata_is_refused(self):
        family, _ = self.family("owner")
        meta = SimpleNamespace(st_uid=os.getuid() + 1,
                               st_mode=stat.S_IFREG | 0o600, st_nlink=1)
        with patch.object(os, "fstat", return_value=meta):
            with self.assertRaisesRegex(RuntimeError, "non-private"):
                self.acquire(family)

    def test_invalid_family_name_is_refused(self):
        with self.assertRaisesRegex(ValueError, "family lock"):
            self.ns["_audio_host_family_lock"]("../escape")

    def test_all_wrappers_delegate_to_the_declared_family(self):
        calls = []
        self.ns["_audio_host_family_lock"] = lambda family: calls.append(
            family) or 123
        for wrapper, family in WRAPPERS.items():
            with self.subTest(wrapper=wrapper):
                self.assertEqual(self.ns[wrapper](), 123)
                self.assertEqual(calls.pop(), family)
        self.assertFalse(calls)

    def test_summary_discloses_blocks_without_changing_partial_rc(self):
        main = next(n for n in self.tree.body
                    if isinstance(n, ast.FunctionDef) and n.name == "main")
        start = next(i for i, n in enumerate(main.body)
                     if isinstance(n, ast.Assign)
                     and any(isinstance(t, ast.Name) and t.id == "failed"
                             for t in n.targets))
        wrapper = ast.parse("def summary(measurements, out):\n    pass\n")
        wrapper.body[0].body = main.body[start:]
        ns = {"json": json}
        exec(compile(ast.fix_missing_locations(wrapper), "<summary>", "exec"),
             ns)
        rows = {"probe": {"failures": [], "coverage_blocked": ["unmeasured"]}}
        out = io.StringIO()
        with redirect_stdout(out):
            rc = ns["summary"](rows, Path("/not-written"))
        got = json.loads(out.getvalue())
        self.assertFalse(rc)
        self.assertEqual(got["failures"], {})
        self.assertEqual(got["coverage_blocked"], {"probe": ["unmeasured"]})


if __name__ == "__main__":
    unittest.main()
