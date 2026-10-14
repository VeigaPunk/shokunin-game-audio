#!/usr/bin/env python3
"""r72-reviewer: independent spot-check of the frontier evidence rows that the
wave-11 author is told to build on (fa-sndfile.md), plus the libsndfile format
table inventory. Anything not reproduced here is reported as unverified rather
than assumed.
"""
import ctypes, json, os, shutil, subprocess, sys, tempfile

sys.path.insert(0, "corpus/live/r72-reviewer")
import probe_sndfile_r72 as P  # reuse the reviewer's own ctypes surface

out = {}

# 1. format-major inventory (does this build carry TXW / HCOM readers?)
out["majors"] = sorted(v for v in P.MAJORS.values() if v)
out["has_txw_major"] = any("TXW" in (v or "").upper() for v in P.MAJORS.values())
out["has_hcom_major"] = any("HCOM" in (v or "").upper() for v in P.MAJORS.values())

# 2. extension fallback set, measured on the reviewer's own copy of the
#    identical no-magic bytes under different names
src = "corpus/live/round-69/extsuffix_nomatch.bin"
tmp = tempfile.mkdtemp(prefix="r72-rev-ext-")
ext_map = {}
for ext in ("au", "snd", "gsm", "vox", "wav", "aif", "f32", "txw", "raw",
            "ulaw", "bin", "mp3", "flac", "SND"):
    dst = os.path.join(tmp, "member." + ext)
    shutil.copyfile(src, dst)
    v = P.leg_file(dst)
    ext_map[ext] = {"format": v["format_name"], "read": v["read_frames"],
                    "error": v["error"]}
out["extension_fallback"] = ext_map
shutil.rmtree(tmp)

# 3. content beats the fallback: RIFF bytes under a .snd name
tmp = tempfile.mkdtemp(prefix="r72-rev-content-")
dst = os.path.join(tmp, "riff.snd")
shutil.copyfile("corpus/live/round-66/pair_dec_act.wav", dst)
v = P.leg_file(dst)
out["content_beats_fallback_riff_named_snd"] = {"format": v["format_name"],
                                                "read": v["read_frames"]}
shutil.rmtree(tmp)

# 4. CLI exit codes: sndfile-info on a reject, sndfile-convert on reject/convert
p = subprocess.run(["sndfile-info", "corpus/live/round-68/posttable_nomatch.wav"],
                   capture_output=True, timeout=20)
out["sndfile_info_reject_exit"] = p.returncode
out["sndfile_convert_present"] = shutil.which("sndfile-convert") is not None
out["sndfile_convert_to_raw_present"] = shutil.which("sndfile-convert-to-raw") is not None
with tempfile.TemporaryDirectory() as td:
    p1 = subprocess.run(["sndfile-convert", "corpus/live/round-69/extsuffix_nomatch.snd",
                         os.path.join(td, "ok.wav")], capture_output=True, timeout=20)
    p2 = subprocess.run(["sndfile-convert", "corpus/live/round-69/extsuffix_nomatch.f32",
                         os.path.join(td, "no.wav")], capture_output=True, timeout=20)
    out["sndfile_convert_snd_exit"] = p1.returncode
    out["sndfile_convert_f32_exit"] = p2.returncode
    out["sndfile_convert_f32_stderr"] = p2.stderr.decode(errors="replace").strip()[:120]

# 5. sf_read vs the CLI Frames line on the .snd member (estimate vs decode)
v = P.leg_file("corpus/live/round-69/extsuffix_nomatch.snd")
p = subprocess.run(["sndfile-info", "corpus/live/round-69/extsuffix_nomatch.snd"],
                   capture_output=True, timeout=20)
frames_line = [ln for ln in p.stdout.decode(errors="replace").splitlines()
               if ln.startswith("Frames")]
out["snd_read_vs_cli_frames"] = {"sf_info_frames": v["frames"],
                                 "sf_read_frames": v["read_frames"],
                                 "cli_frames_line": frames_line}

json.dump(out, sys.stdout, indent=1)
