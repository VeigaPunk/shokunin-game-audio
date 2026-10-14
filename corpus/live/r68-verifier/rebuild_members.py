#!/usr/bin/env python3
"""Independent rebuild of build_ui_posttable_r68_probe() — verifier copy.
Byte-for-byte port of the committed builder, writing into verifier scratch
instead of the tracked member dir. Then cmp against tracked members."""
from pathlib import Path

OUT = Path("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r68-verifier/probes")


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    # --- verbatim port of build_ui_posttable_r68_probe body ---
    b = bytearray(b"ufo-r68 post-table-fallback no-match member: no CHECK row\n")
    b.extend((i * 7 + 3) & 0xFF for i in range(len(b), 512))
    b[256] = 0x00
    (OUT / "posttable_nomatch.wav").write_bytes(b)
    t = bytearray(128)
    t[0:6] = b"LM8953"
    t[22] = 0xC9
    t[23] = 3
    for i in range(32, 128):
        t[i] = (i * 5 + 1) & 0xFF
    (OUT / "txw_piperefuse.wav").write_bytes(t)


if __name__ == "__main__":
    build()
