"""Hermetic truepeak parser, analytic-control, and CLI-dispatch checks."""
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import tempfile
import unittest
from unittest import mock


METADATA_EBUR128 = """[Parsed_ametadata_1 @ 0x123] frame:0 pts:0 pts_time:0
[Parsed_ametadata_1 @ 0x123] lavfi.r128.I=-23.456
[Parsed_ametadata_1 @ 0x123] lavfi.r128.sample_peak=0.500
[Parsed_ametadata_1 @ 0x123] lavfi.r128.true_peak=0.707
[Parsed_ebur128_0 @ 0x456] Summary:

  Integrated loudness:
    I:         -23.5 LUFS
    Threshold: -34.0 LUFS

  Sample peak:
    Peak:       -6.0 dBFS

  True peak:
    Peak:       -3.0 dBFS
"""


SUMMARY_ONLY_EBUR128 = """[Parsed_ebur128_0 @ 0x456] Summary:

  Integrated loudness:
    I:         -23.5 LUFS
    Threshold: -34.0 LUFS

  Sample peak:
    Peak:       -6.0 dBFS

  True peak:
    Peak:       -3.0 dBFS
"""
FLOOR_EBUR128 = """[Parsed_ametadata_1 @ 0x123] frame:0 pts:0 pts_time:0
[Parsed_ametadata_1 @ 0x123] lavfi.r128.I=-70.000
[Parsed_ametadata_1 @ 0x123] lavfi.r128.sample_peak=0.010
[Parsed_ametadata_1 @ 0x123] lavfi.r128.true_peak=0.010
[Parsed_ebur128_0 @ 0x456] Summary:

  Integrated loudness:
    I:         -70.0 LUFS
    Threshold:   0.0 LUFS

  Sample peak:
    Peak:       -40.0 dBFS

  True peak:
    Peak:       -40.0 dBFS
"""

NEGATIVE_INFINITY_EBUR128 = """[Parsed_ametadata_1 @ 0x123] frame:0 pts:0 pts_time:0
[Parsed_ametadata_1 @ 0x123] lavfi.r128.I=-inf
[Parsed_ametadata_1 @ 0x123] lavfi.r128.sample_peak=0.010
[Parsed_ametadata_1 @ 0x123] lavfi.r128.true_peak=0.010
[Parsed_ebur128_0 @ 0x456] Summary:

  Integrated loudness:
    I:         -inf LUFS
    Threshold:   0.0 LUFS

  Sample peak:
    Peak:       -40.0 dBFS

  True peak:
    Peak:       -40.0 dBFS
"""

MISSING_TRUE_PEAK_EBUR128 = """[Parsed_ametadata_1 @ 0x123] frame:0 pts:0 pts_time:0
[Parsed_ametadata_1 @ 0x123] lavfi.r128.I=-23.456
[Parsed_ametadata_1 @ 0x123] lavfi.r128.sample_peak=0.500
[Parsed_ebur128_0 @ 0x456] Summary:

  Integrated loudness:
    I:         -23.5 LUFS
    Threshold: -34.0 LUFS

  Sample peak:
    Peak:       -6.0 dBFS
"""


class TruePeakR101ParserTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).with_name("measure_audio.py")
        ns = {"__file__": str(path), "__name__": "truepeak_r101_parser_test"}
        exec(compile(path.read_bytes(), str(path), "exec"), ns)
        cls.namespace = ns
        cls.parse = staticmethod(ns["_truepeak_r101_parse_ebur128"])

    def test_metadata_precision_wins_over_summary(self):
        got = self.parse(METADATA_EBUR128)
        self.assertAlmostEqual(got["sample_peak_dbfs"], -6.0206, places=3)
        self.assertAlmostEqual(got["true_peak_dbtp"], -3.0117, places=3)
        self.assertEqual(got["integrated_lufs"], -23.456)
        self.assertEqual(got["precision"]["integrated_lufs"]["resolution"],
                         "0.001 LU")

    def test_summary_fallback_records_coarse_precision(self):
        got = self.parse(SUMMARY_ONLY_EBUR128)
        self.assertEqual(got["sample_peak_dbfs"], -6.0)
        self.assertEqual(got["true_peak_dbtp"], -3.0)
        self.assertEqual(got["integrated_lufs"], -23.5)
        self.assertEqual(got["precision"]["sample_peak_dbfs"]["source"],
                         "summary:Sample peak")
        self.assertEqual(got["precision"]["true_peak_dbtp"]["resolution"],
                         "0.1 dB")

    def test_minus_70_lufs_floor_is_null(self):
        self.assertIsNone(self.parse(FLOOR_EBUR128)["integrated_lufs"])

    def test_negative_infinity_integrated_is_null(self):
        self.assertIsNone(
            self.parse(NEGATIVE_INFINITY_EBUR128)["integrated_lufs"])

    def test_missing_true_peak_block_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "True peak"):
            self.parse(MISSING_TRUE_PEAK_EBUR128)

    def test_duplicate_summary_is_ambiguous(self):
        with self.assertRaisesRegex(ValueError, "exactly one Summary"):
            self.parse(METADATA_EBUR128 + METADATA_EBUR128)

    def test_positive_control_accepts_analytic_peak_and_rejects_zero(self):
        matches = self.namespace[
            "_truepeak_r101_control_overshoot_matches"]
        self.assertTrue(matches(
            "positive_12khz_phase_pi_over4", 2.999, 0.08))
        self.assertFalse(matches(
            "positive_12khz_phase_pi_over4", 0.0, 0.08))

    def test_phase0_control_accepts_zero_overshoot(self):
        matches = self.namespace[
            "_truepeak_r101_control_overshoot_matches"]
        self.assertTrue(matches("negative_12khz_phase0", 0.0, 0.08))

    def test_truepeak_cli_does_not_rebuild_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifacts = root / "artifacts"

            truepeak_scratch = root / "live" / "round-101-truepeak"
            def measure_without_audio(name, spec, path=None):
                target = path or artifacts / (name + ".wav")
                scale = (1.6 if name.endswith("_third") else
                         1.25 if name.endswith("_alt") else 1.0)
                return {
                    "path": str(target.relative_to(root)),
                    "duration_s": spec[0],
                    "spectral_centroid_hz": float(spec[1]) * scale,
                    "failures": [],
                }

            def section_contrast_without_audio(_path, component_hz=30):
                return {
                    "passed": True,
                    "component_hz": component_hz,
                    "internal_join_adjacent_delta_full_scale": None,
                    "internal_join_side_slope_mismatch_full_scale_per_sample":
                        None,
                }

            def truepeak_probe_without_audio():
                (truepeak_scratch / "test-run").mkdir(parents=True)
                return {"failures": [], "run_id": "test-run"}

            command = mock.Mock()
            probe = mock.Mock(side_effect=truepeak_probe_without_audio)
            replacements = {
                "ROOT": root,
                "ARTIFACTS": artifacts,
                "TRUEPEAK_R101_SCRATCH": truepeak_scratch,
                "command": command,
                "measure": measure_without_audio,
                "section_contrast": section_contrast_without_audio,
                "_truepeak_r101_probe": probe,
            }
            with mock.patch.dict(self.namespace, replacements), \
                    mock.patch.object(
                        self.namespace["sys"], "argv",
                        ["measure_audio.py", "--probe-truepeak-r101"]), \
                    redirect_stdout(StringIO()):
                self.assertFalse(self.namespace["main"]())

            builder_calls = [
                call for call in command.call_args_list
                if any(Path(str(argument)).name == "build_artifacts.py"
                       for argument in call.args)
            ]
            self.assertEqual(builder_calls, [])
            probe.assert_called_once_with()
            self.assertTrue((
                truepeak_scratch / "test-run" / "measurements.json"
            ).is_file())

    def test_normal_cli_still_builds_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifacts = root / "artifacts"

            def measure_without_audio(name, spec, path=None):
                target = path or artifacts / (name + ".wav")
                scale = (1.6 if name.endswith("_third") else
                         1.25 if name.endswith("_alt") else 1.0)
                return {
                    "path": str(target.relative_to(root)),
                    "duration_s": spec[0],
                    "spectral_centroid_hz": float(spec[1]) * scale,
                    "failures": [],
                }

            def section_contrast_without_audio(_path, component_hz=30):
                return {
                    "passed": True,
                    "component_hz": component_hz,
                    "internal_join_adjacent_delta_full_scale": None,
                    "internal_join_side_slope_mismatch_full_scale_per_sample":
                        None,
                }

            command = mock.Mock()
            replacements = {
                "ROOT": root,
                "ARTIFACTS": artifacts,
                "command": command,
                "measure": measure_without_audio,
                "section_contrast": section_contrast_without_audio,
            }
            with mock.patch.dict(self.namespace, replacements), \
                    mock.patch.object(
                        self.namespace["sys"], "argv", ["measure_audio.py"]), \
                    redirect_stdout(StringIO()):
                self.assertFalse(self.namespace["main"]())

            builder_calls = [
                call for call in command.call_args_list
                if any(Path(str(argument)).name == "build_artifacts.py"
                       for argument in call.args)
            ]
            self.assertEqual(len(builder_calls), 1)
            self.assertTrue(list(
                (root / "live" / "runs").glob("*/measurements.json")))


if __name__ == "__main__":
    unittest.main()
