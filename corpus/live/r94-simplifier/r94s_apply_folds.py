#!/usr/bin/env python3
"""r94s_ simplifier: apply the proven fold set to the SCRATCH copy of the r94
fixture (tree/fixtures/measure_audio.py) and emit a unified diff.

Every replacement asserts count==1 so a drifted anchor fails loudly instead of
silently applying to the wrong site. Variant A = the behavior-preserving fold
set; variant B = A + the duplicate-leg dedup (a leg-census tradeoff for the L1).

Usage: python3 r94s_apply_folds.py {A|B}
"""
import difflib
import pathlib
import sys

TARGET = pathlib.Path(__file__).parent / "tree" / "fixtures" / "measure_audio.py"
PRISTINE = pathlib.Path(__file__).parent / "r94s_pristine.py"


def main(variant):
    src = TARGET.read_text()
    before = src
    applied = []

    def rep(old, new, tag):
        nonlocal src
        n = src.count(old)
        assert n == 1, f"{tag}: anchor count {n} (expected 1)"
        src = src.replace(old, new)
        applied.append(tag)

    # ---- A1: drop the two metrics fields no law and no ref reads ----------
    rep('    m = {"frames": meta["frames"], "channels": meta["channels"],\n'
        '         "rate": meta["rate"], "bits": meta["bits"], '
        '"fmt_tag": meta["fmt_tag"]}',
        '    m = {"frames": meta["frames"], "channels": meta["channels"],\n'
        '         "rate": meta["rate"], "bits": meta["bits"]}',
        "A1a metrics: drop fmt_tag")
    rep('    first = (arr[:8] * (2 ** (meta["bits"] - 1))).round()'
        '.astype("int64")\n'
        '    m["first8_ints"] = [[int(v) for v in row] for row in first]\n'
        '    return m, arr',
        '    return m, arr',
        "A1b metrics: drop first8_ints")

    # ---- A2: the length_rows 5th column is never read ---------------------
    rep('    length_rows = (("len_12000_to_44100", B, 44100, 12000, 11025),\n'
        '                   ("len_12001_to_44100", I, 44100, 12001, 11026),\n'
        '                   ("len_12000_to_22050", B, 22050, 12000, 5512),\n'
        '                   ("len_12000_to_24050", B, 24050, 12000, 6013),\n'
        '                   ("len_12000_to_11025", B, 11025, 12000, 2756),\n'
        '                   ("len_12000_to_32000", B, 32000, 12000, 8000))',
        '    length_rows = (("len_12000_to_44100", B, 44100, 12000),\n'
        '                   ("len_12001_to_44100", I, 44100, 12001),\n'
        '                   ("len_12000_to_22050", B, 22050, 12000),\n'
        '                   ("len_12000_to_24050", B, 24050, 12000),\n'
        '                   ("len_12000_to_11025", B, 11025, 12000),\n'
        '                   ("len_12000_to_32000", B, 32000, 12000))',
        "A2a length_rows: drop unused expect column")
    rep('    for name, infile, out_rate, in_frames, expect in length_rows:',
        '    for name, infile, out_rate, in_frames in length_rows:',
        "A2b length_rows: drop expect binding")

    # ---- A3: the orphan lattice row --------------------------------------
    rep('        ("alias_20k_v", H, ["rate", "-v", "44100"], "v"),\n', "",
        "A3 alias_specs: drop unreferenced alias_20k_v leg")

    # ---- A4: one railed-sample authority ---------------------------------
    rep('def _sox_r94_m(leg, key, default=None):\n'
        '    m = leg.get("metrics") or {}\n'
        '    return m.get(key, default)',
        'def _sox_r94_m(leg, key, default=None):\n'
        '    m = leg.get("metrics") or {}\n'
        '    return m.get(key, default)\n'
        '\n'
        '\n'
        'def _sox_r94_railed(leg, thresh):\n'
        '    """Count of samples railed at/above `thresh` LSB on one leg\'s\n'
        '    product — the single authority behind both -G guard rows."""\n'
        '    arr = leg.get("_arr")\n'
        '    if arr is None:\n'
        '        return None\n'
        '    ints = np.rint(arr * 32768.0)\n'
        '    return int(np.count_nonzero(np.abs(ints) >= thresh))',
        "A4a add _sox_r94_railed helper")
    rep('    def clipped_ge(arr, thresh):\n'
        '        if arr is None:\n'
        '            return None\n'
        '        ints = np.rint(arr * 32768.0)\n'
        '        return int(np.count_nonzero(np.abs(ints) >= thresh))\n'
        '\n'
        '    plain =',
        '    plain =',
        "A4b gain: drop duplicate clipped_ge")
    rep('    c_plain = clipped_ge(plain.get("_arr"), 32766)\n'
        '    c_guard = clipped_ge(guarded.get("_arr"), 32766)',
        '    c_plain = _sox_r94_railed(plain, 32766)\n'
        '    c_guard = _sox_r94_railed(guarded, 32766)',
        "A4c gain: call the shared helper")
    rep('    def railed(leg, thresh):\n'
        '        arr = leg.get("_arr")\n'
        '        if arr is None:\n'
        '            return None\n'
        '        ints = np.rint(arr * 32768.0)\n'
        '        return int(np.count_nonzero(np.abs(ints) >= thresh))\n'
        '\n', "",
        "A4d dither: drop duplicate railed")
    rep('    c1, c2_ = railed(g_def, 32767), railed(g_g_def, 32767)',
        '    c1, c2_ = (_sox_r94_railed(g_def, 32767),\n'
        '               _sox_r94_railed(g_g_def, 32767))',
        "A4e dither: call the shared helper")

    # ---- A5: one trailing-zero authority ---------------------------------
    rep('    N = bin_arr.shape[0]\n',
        '    N = bin_arr.shape[0]\n'
        '\n'
        '    def trail_zeros(arr):\n'
        '        """Trailing zero-frame count of a product\'s channel 0 — the one\n'
        '        authority behind the three silence rows."""\n'
        '        ints = np.rint(arr[:, 0] * 32768.0).astype("int64")\n'
        '        trail = 0\n'
        '        for v in ints[::-1]:\n'
        '            if v != 0:\n'
        '                break\n'
        '            trail += 1\n'
        '        return trail\n',
        "A5a repeat/pad/silence: add trail_zeros helper")
    rep('    arr = sil.get("_arr")\n'
        '    if arr is not None:\n'
        '        ints = np.rint(arr[:, 0] * 32768.0).astype("int64")\n'
        '        trail = 0\n'
        '        for v in ints[::-1]:\n'
        '            if v != 0:\n'
        '                break\n'
        '            trail += 1\n'
        '        sil["trailing_zero_frames"] = trail',
        '    arr = sil.get("_arr")\n'
        '    if arr is not None:\n'
        '        ints = np.rint(arr[:, 0] * 32768.0).astype("int64")\n'
        '        trail = trail_zeros(arr)\n'
        '        sil["trailing_zero_frames"] = trail',
        "A5b silence_above_only: use trail_zeros")
    rep('    arr = both.get("_arr")\n'
        '    if arr is not None:\n'
        '        ints = np.rint(arr[:, 0] * 32768.0).astype("int64")\n'
        '        trail = 0\n'
        '        for v in ints[::-1]:\n'
        '            if v != 0:\n'
        '                break\n'
        '            trail += 1\n'
        '        both["trailing_zero_frames"] = trail',
        '    arr = both.get("_arr")\n'
        '    if arr is not None:\n'
        '        trail = trail_zeros(arr)\n'
        '        both["trailing_zero_frames"] = trail',
        "A5c silence_both_0.1: use trail_zeros")
    rep('    arr = leave.get("_arr")\n'
        '    if arr is not None:\n'
        '        ints = np.rint(arr[:, 0] * 32768.0).astype("int64")\n'
        '        trail = 0\n'
        '        for v in ints[::-1]:\n'
        '            if v != 0:\n'
        '                break\n'
        '            trail += 1\n'
        '        leave["trailing_zero_frames"] = trail',
        '    arr = leave.get("_arr")\n'
        '    if arr is not None:\n'
        '        trail = trail_zeros(arr)\n'
        '        leave["trailing_zero_frames"] = trail',
        "A5d silence_both_leave: use trail_zeros")

    # ---- A6: the verdict-redundant arm -----------------------------------
    rep('    _sox_r94_arm(entry, d20,\n'
        '                 d20.get("band_21100hz_db") is not None and\n'
        '                 d20["band_21100hz_db"] < -110.0,\n'
        '                 "the only ~-129.6 dB row in the lattice is the 20 kHz '
        'stimulus "\n'
        "                 f\"DEFAULT leg; got {d20.get('band_21100hz_db')}\")\n",
        "",
        "A6 rate: drop the arm subsumed by the -120 dB arm")

    # ---- A7: dead bindings ----------------------------------------------
    rep('    A, B, F, I = st["a"], st["b"], st["f"], st["i"]',
        '    A, B, F = st["a"], st["b"], st["f"]',
        "A7a det: drop the never-read stim_i binding")
    rep('    arr = np.asarray(data_i16)\n'
        '    if arr.ndim == 1:\n'
        '        arr = arr[:, None]\n'
        '    frames, channels = arr.shape',
        '    arr = np.asarray(data_i16)\n'
        '    if arr.ndim == 1:\n'
        '        arr = arr[:, None]\n'
        '    channels = arr.shape[1]',
        "A7b write_pcm16: drop the unused frames binding")
    rep('        n, mx = _sox_r94_mismatch(arr * 32768.0, bin_i[:4800])',
        '        n, _ = _sox_r94_mismatch(arr * 32768.0, bin_i[:4800])',
        "A7c trim: drop the unused max-abs binding")
    rep('        n, mx = _sox_r94_mismatch(arr[:, 0] * 32768.0, tiled)',
        '        n, _ = _sox_r94_mismatch(arr[:, 0] * 32768.0, tiled)',
        "A7d repeat: drop the unused max-abs binding")

    # ---- A8: _sox_r94_leg's `note` is unreachable in this family ---------
    rep('def _sox_r94_leg(scratch, name, argv, infile, reps=1, env=None,\n'
        '                 timeout=SOX_R94_WALL, want_metrics=True, note=None):',
        'def _sox_r94_leg(scratch, name, argv, infile, reps=1, env=None,\n'
        '                 timeout=SOX_R94_WALL, want_metrics=True):',
        "A8a _sox_r94_leg: drop the never-passed note parameter")
    rep('    if note:\n'
        '        leg["note"] = note\n',
        "",
        "A8b _sox_r94_leg: drop the unreachable note branch")

    # ---- A9: _sox_r94_spawn's `wd` is always None ------------------------
    rep('def _sox_r94_spawn(argv, timeout=SOX_R94_WALL, env=None, wd=None):',
        'def _sox_r94_spawn(argv, timeout=SOX_R94_WALL, env=None):',
        "A9a _sox_r94_spawn: drop the never-passed wd parameter")
    rep('            env=env, cwd=wd, start_new_session=True,',
        '            env=env, start_new_session=True,',
        "A9b _sox_r94_spawn: drop the always-None cwd")

    if variant == "B":
        # ---- B1: the two duplicate identity rows (leg-census tradeoff) ----
        rep('    for name, infile, tail in (("det_gain0_identity", A, '
            '["gain", "0"]),\n'
            '                               ("det_passthrough_identity", A, []),\n'
            '                               ("det_rate_same_identity", B, '
            '["rate", "48000"]),\n'
            '                               ("det_pad_pct50_identity", B, '
            '["pad", "%50"])):',
            '    for name, infile, tail in (("det_gain0_identity", A, '
            '["gain", "0"]),\n'
            '                               ("det_passthrough_identity", A, '
            '[])):',
            "B1a det: drop the rate/pad rows duplicated in their own entries")
        rep('    _sox_r94_ref_arm(entry, L["det_pad_pct50_identity"], refs,\n'
            '                     "repeat_pad_silence_D.json", "pad_pct50")\n',
            "",
            "B1b det: drop the ref_arm of the dropped row")
        rep('    A, B, F = st["a"], st["b"], st["f"]\n'
            '    L = entry["legs"]\n'
            '\n'
            '    # --- the auto-dither predicate',
            '    A, F = st["a"], st["f"]\n'
            '    L = entry["legs"]\n'
            '\n'
            '    # --- the auto-dither predicate',
            "B1c det: drop the now-unused stim_b binding")

    TARGET.write_text(src)
    diff = "".join(difflib.unified_diff(
        before.splitlines(True), src.splitlines(True),
        fromfile="a/measure_audio.py", tofile=f"b/measure_audio.py (r94s variant {variant})",
        n=3))
    out = pathlib.Path(__file__).parent / f"r94s_folds_variant{variant}.diff"
    out.write_text(diff)
    print(f"variant {variant}: {len(applied)} folds applied")
    for tag in applied:
        print("   ", tag)
    print(f"diff -> {out}  ({diff.count(chr(10))} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "A"))
