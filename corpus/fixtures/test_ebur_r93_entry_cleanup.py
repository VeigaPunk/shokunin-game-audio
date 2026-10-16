"""Entry error/cleanup propagation; no audio backend or process execution."""
from pathlib import Path
import unittest


class EntryCleanupTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = Path(__file__).with_name("measure_audio.py")
        cls.code = compile(cls.path.read_bytes(), str(cls.path), "exec")

    def namespace(self):
        ns = {"__file__": str(self.path), "__name__": "r93_entry_cleanup_test"}
        exec(self.code, ns)
        ctx = {"stim": {}, "refs": {}}
        stopped = []

        def fault(_ctx, _spec, legs, _entry):
            self.assertIs(_ctx, ctx)
            legs["injected_partial"] = {"metadata_only": True}
            raise RuntimeError("injected caller backend failure")

        def stop(entry, failures, owned):
            self.assertIs(owned, ctx)
            self.assertIs(failures, entry["failures"])
            stopped.append(owned)

        ns.update({"_ebur_r93_entry_head": lambda _: {"failures": []},
                   "_ebur_r93_ctx": lambda: ctx,
                   "_ebur_r93_run": fault, "_ebur_r93_teardown": stop})
        return ns, stopped

    def assert_entry_cleanup(self, name):
        ns, stopped = self.namespace()
        row, escaped = None, None
        try:
            row = ns[name]()
        except RuntimeError as exc:
            escaped = exc
        self.assertEqual(len(stopped), 1)
        self.assertIsNone(escaped)
        self.assertIn("injected_partial", row["legs"])
        self.assertTrue(row["failures"])
        self.assertTrue(row["coverage_blocked"])

    def test_modes_entry_smoke(self):
        self.assert_entry_cleanup("ebur_modes_r93_entry")

    def test_every_entry_retains_partial_data_and_stops_on_backend_error(self):
        names = sorted(name for name in self.namespace()[0]
                       if name.startswith("ebur_") and name.endswith("_r93_entry"))
        self.assertEqual(len(names), 9)
        for name in names:
            with self.subTest(entry=name):
                self.assert_entry_cleanup(name)


if __name__ == "__main__":
    unittest.main()
