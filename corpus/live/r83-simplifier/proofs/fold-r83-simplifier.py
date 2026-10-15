#!/usr/bin/env python3
"""r83-simplifier fold — apply the 6-item YAGNI fold to a scratch copy of
the committed fixture. Every replacement is asserted to match EXACTLY
once; a zero or multi match aborts without writing.

Usage:
    python3 fold-r83-simplifier.py <base.py> <out.py>
"""
import sys

REPLACEMENTS = [
    # ---- T1: ftag is a write-only loop variable -------------------------
    ("T1 ftag dead store",
     "    for ftag, f in feeds.items():\n"
     "        if f.poll() is None:\n"
     "            os.killpg(f.pid, signal.SIGKILL)\n"
     "        f.wait()\n"
     '    cell["feeds"] = {k: {"exit_code": v.returncode}\n',
     "    for f in feeds.values():\n"
     "        if f.poll() is None:\n"
     "            os.killpg(f.pid, signal.SIGKILL)\n"
     "        f.wait()\n"
     '    cell["feeds"] = {k: {"exit_code": v.returncode}\n'),

    # ---- T2a: (leaf or {}) dead falsy guard, teardown -------------------
    ("T2a teardown leaf guard",
     '    for tag, leaf in (loads or {}).items():\n'
     '        entry.setdefault("unloads", {})[tag] = _pwcat_r83_unload_own(\n'
     '            (leaf or {}).get("module_id"), tag)\n'
     '    sinks_now = _capture_r77_sink_names_strict()\n',
     '    for tag, leaf in (loads or {}).items():\n'
     '        entry.setdefault("unloads", {})[tag] = _pwcat_r83_unload_own(\n'
     '            leaf.get("module_id"), tag)\n'
     '    sinks_now = _capture_r77_sink_names_strict()\n'),

    # ---- T2b: (leaf or {}) dead falsy guard, block ----------------------
    ("T2b block leaf guard",
     '    for tag, leaf in (loads or {}).items():\n'
     '        entry.setdefault("unloads", {})[tag] = _pwcat_r83_unload_own(\n'
     '            (leaf or {}).get("module_id"), tag)\n'
     '    entry["failures"] = failures\n',
     '    for tag, leaf in (loads or {}).items():\n'
     '        entry.setdefault("unloads", {})[tag] = _pwcat_r83_unload_own(\n'
     '            leaf.get("module_id"), tag)\n'
     '    entry["failures"] = failures\n'),

    # ---- T3: _pwcat_r83_rec_leg's `extra` is never supplied -------------
    ("T3a rec_leg docstring",
     '    [extra] --target <sink> -n <frames> --rate 48000 --channels 2\n',
     '    --target <sink> -n <frames> --rate 48000 --channels 2\n'),
    ("T3b rec_leg signature",
     "def _pwcat_r83_rec_leg(name, ctx, *, props=(), extra=(), frames=96000,\n"
     "                       sink=None, sample_at=1.0, timeout_s=8.0):\n",
     "def _pwcat_r83_rec_leg(name, ctx, *, props=(), frames=96000,\n"
     "                       sink=None, sample_at=1.0, timeout_s=8.0):\n"),
    ("T3c rec_leg dead argv slot",
     '    argv += ["-P", f"node.name={tag}", *extra, "--target", sink,\n'
     '             "-n", str(frames), "--rate", "48000", "--channels", "2",\n',
     '    argv += ["-P", f"node.name={tag}", "--target", sink,\n'
     '             "-n", str(frames), "--rate", "48000", "--channels", "2",\n'),
    ("T3d rec_leg extra_argv leaf",
     '    cell = {"name": name, "tag": tag, "argv": shown,\n'
     '            "props_argv": list(props), "extra_argv": list(extra)}\n',
     '    cell = {"name": name, "tag": tag, "argv": shown,\n'
     '            "props_argv": list(props)}\n'),

    # ---- T4a: `cons[0] == nsb` subsumed by `cons[0] in own_names` -------
    ("T4a p_empty subsumed disjunct",
     "                if len(cons) != 1 or cons[0] in own_names or \\\n"
     "                        cons[0] == nsb or \\\n"
     '                        ccls.get(cons[0]) not in ("Audio/Sink",):\n',
     "                if len(cons) != 1 or cons[0] in own_names or \\\n"
     '                        ccls.get(cons[0]) not in ("Audio/Sink",):\n'),

    # ---- T4b: `cons[0] != nsb` subsumed by `cons[0] not in own_names` ---
    ("T4b n_empty subsumed conjunct",
     "                ok = (len(cons) == 1 and cons[0] not in own_names and\n"
     '                      cons[0] != nsb and\n'
     '                      ccls.get(cons[0]) == "Audio/Sink")\n',
     "                ok = (len(cons) == 1 and cons[0] not in own_names and\n"
     '                      ccls.get(cons[0]) == "Audio/Sink")\n'),

    # ---- T5: unreachable `min is None` continue -------------------------
    ("T5 dead min guard",
     "                    for ci, c in enumerate(chans[:2]):\n"
     '                        if c.get("min") is None:\n'
     "                            continue\n"
     "                        # the artifact doubles EACH channel's OWN freq\n",
     "                    for ci, c in enumerate(chans[:2]):\n"
     "                        # the artifact doubles EACH channel's OWN freq\n"),

    # ---- T6: unreachable `move never fired` failure arm -----------------
    ("T6 unreachable move arm",
     '            if leg.get("move_rc") is None:\n'
     '                if not leg.get("move_skipped"):\n'
     '                    failures.append("dm_move: the move never fired "\n'
     '                                    "and no skip was recorded")\n'
     "            else:\n"
     '                if leg["move_rc"] != 0:\n',
     '            if leg.get("move_rc") is not None:\n'
     '                if leg["move_rc"] != 0:\n'),

    # ---- T7a: `tapf` component of `tap = tapf = None`, lb_leg -----------
    ("T7a lb_leg dead tapf init",
     '    tap = tapf = None\n'
     '    if tap_target is not None:\n'
     '        tapf = Path(ctx["tmp"]) / f"r83a_tap_{name}.wav"\n',
     '    tap = None\n'
     '    if tap_target is not None:\n'
     '        tapf = Path(ctx["tmp"]) / f"r83a_tap_{name}.wav"\n'),

    # ---- T7b: `tapf` component of `tap = tapf = None`, play_leg ---------
    ("T7b play_leg dead tapf init",
     '    tap = tapf = None\n'
     '    if tap_seconds:\n'
     '        tapf = Path(ctx["tmp"]) / f"r83a_{name}_tap.wav"\n',
     '    tap = None\n'
     '    if tap_seconds:\n'
     '        tapf = Path(ctx["tmp"]) / f"r83a_{name}_tap.wav"\n'),
]


def main():
    base, out = sys.argv[1], sys.argv[2]
    text = open(base).read()
    for label, old, new in REPLACEMENTS:
        n = text.count(old)
        if n != 1:
            print(f"ABORT {label}: {n} matches (expected 1)")
            sys.exit(2)
        text = text.replace(old, new, 1)
        print(f"OK   {label}: 1 match, "
              f"{len(old.splitlines())} -> {len(new.splitlines())} lines")
    open(out, "w").write(text)
    print(f"wrote {out} ({len(text.splitlines())} lines)")


if __name__ == "__main__":
    main()
