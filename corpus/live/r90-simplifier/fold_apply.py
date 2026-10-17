#!/usr/bin/env python3
"""r90-simplifier fold application (exact-string, asserted, idempotence-checked).

Usage:  fold_apply.py <tree-root> <fold>

  fold = "f1"  delete the zero-caller helper `_wpstate_r90_edges_out`
  fold = "f2"  drop the dead second return path of wplink's `count()` and the
               four dead bindings (`_g` x10, `val_row`, `argv_y`, `argv`)

Every replacement asserts its own occurrence count, so a drifted tree refuses
instead of silently folding something else. Writes only under <tree-root>.
"""
import hashlib
import sys
from pathlib import Path

REL = "corpus/fixtures/measure_audio.py"

FOLDS = {
    "f1": [
        # (old, new, expected occurrences)
        ("def _wpstate_r90_edges_out(g, name):\n"
         "    return [e for e in _wpstate_r90_edges(g) "
         "if e.get(\"out_node\") == name]\n\n\n",
         "", 1),
    ],
    "f2": [
        ("            return len(_wpstate_r90_own_links(g, own)), g",
         "            return len(_wpstate_r90_own_links(g, own))", 1),
        ("n, _g = count()", "n = count()", 10),
        ("t_row, val_row, _ = _wpstate_r90_store_poll(skv)",
         "t_row, _, _ = _wpstate_r90_store_poll(skv)", 1),
        ("proc_y, argv_y = _wpstate_r90_play(",
         "proc_y, _ = _wpstate_r90_play(", 1),
        ("proc, argv = _wpstate_r90_play(tag, WPSTATE_R90_L2, t48)",
         "proc, _ = _wpstate_r90_play(tag, WPSTATE_R90_L2, t48)", 1),
    ],
}


def main():
    root, fold = Path(sys.argv[1]), sys.argv[2]
    path = root / REL
    src = path.read_text()
    before = hashlib.sha256(src.encode()).hexdigest()
    for old, new, want in FOLDS[fold]:
        got = src.count(old)
        assert got == want, (fold, old[:60], got, want)
        src = src.replace(old, new)
    path.write_text(src)
    after = hashlib.sha256(src.encode()).hexdigest()
    print(f"{fold}: {path}\n  before {before}\n  after  {after}\n"
          f"  lines  {len(src.splitlines())}")


if __name__ == "__main__":
    main()
