#!/usr/bin/env python3
"""Parse the SoX_ng auto_detect CHECK table from the verified local copy
corpus/live/r64-reviewer/r64rev-formats.c (== upstream tag 14.8.0.1) into an
ordered row list, and evaluate first-match for a byte buffer + extension.

CHECK(type, p2, l2, d2, p1, l1, d1) fires iff
    len >= p1 + l1 && memcmp(data+p1, d1, l1)==0 && memcmp(data+p2, d2, l2)==0
Rows are evaluated in source order; the first match wins (return #type).
The sndr row (line 247-248) is additionally gated by `if (ext &&
!strcasecmp(ext, "snd"))`. The adx row sits inside `#if 0` — compiled out,
marked unreachable. USING_FFMPEG / HAVE_SNDFILE / HAVE_SF_FORMAT_MPC2K rows
are live in this build (sox --help lists sds, mpc2k; act bridge proves
USING_FFMPEG).
"""
import re
from pathlib import Path

FORMATS = Path(__file__).resolve().parents[1] / "r64-reviewer" / "r64rev-formats.c"


def c_literal(text):
    """Decode a C string literal (already quote-stripped) to bytes."""
    out = bytearray()
    i = 0
    while i < len(text):
        c = text[i]
        if c != "\\":
            out.append(ord(c) & 0xFF)
            i += 1
            continue
        i += 1
        e = text[i]
        if e == "x":
            j = i + 1
            while j < len(text) and text[j] in "0123456789abcdefABCDEF":
                j += 1
            out.append(int(text[i + 1:j], 16) & 0xFF)
            i = j
        elif e in "01234567":
            j = i
            while j < len(text) and j < i + 3 and text[j] in "01234567":
                j += 1
            out.append(int(text[i:j], 8) & 0xFF)
            i = j
        else:
            out.append({"n": 10, "r": 13, "t": 9, "v": 11, "a": 7, "b": 8,
                        "f": 12, "\\": 92, "'": 39, '"': 34, "?": 63,
                        "0": 0}[e] if e not in "0" else 0)
            i += 1
    return bytes(out)


def split_args(body):
    """Split a CHECK(...) arg list on top-level commas, honoring literals."""
    args, cur, in_str, esc = [], [], False, False
    for ch in body:
        if esc:
            cur.append(ch); esc = False
        elif ch == "\\" and in_str:
            cur.append(ch); esc = True
        elif ch == '"':
            cur.append(ch); in_str = not in_str
        elif ch == "," and not in_str:
            args.append("".join(cur).strip()); cur = []
        else:
            cur.append(ch)
    args.append("".join(cur).strip())
    return args


def lit_bytes(arg):
    m = re.match(r'^"(.*)"$', arg.strip(), re.S)
    return c_literal(m.group(1)) if m else None


def parse_rows(path=FORMATS):
    """Ordered CHECK rows: (line, type, p2, l2, d2, p1, l1, d1, ext_gated, dead)."""
    text = path.read_text()
    # strip /* */ comments while preserving line numbers: replace each
    # comment with its own newline count so reported lines match the file.
    text = re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"),
                  text, flags=re.S)
    lines = text.splitlines()
    rows, dead, ext_next = [], False, False
    i = 0
    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if s.startswith("#if"):
            if s == "#if 0":
                dead = True
            i += 1
            continue
        if s.startswith(("#endif", "#else", "#elif")):
            dead = False
            i += 1
            continue
        if re.match(r"if \(ext && !strcasecmp\(ext,", s):
            ext_next = True
            i += 1
            continue
        if s.startswith("#define"):
            i += 1
            continue
        if "CHECK(" in line:
            start = i
            # consume chars until the first `)` outside a string literal;
            # some CHECKs (adts) continue on a second physical line.
            blob, in_str, esc, done = [], False, False, False
            while i < len(lines) and not done:
                for ch in (lines[i] if i != start else lines[i][lines[i].index("CHECK(") + 6:]):
                    if done:
                        break
                    if esc:
                        blob.append(ch); esc = False
                    elif ch == "\\" and in_str:
                        blob.append(ch); esc = True
                    elif ch == '"':
                        blob.append(ch); in_str = not in_str
                    elif ch == ")" and not in_str:
                        done = True
                    else:
                        blob.append(ch)
                i += 1
            i -= 1
            blob = "".join(blob)
            args = split_args(blob)
            assert len(args) == 7, (start + 1, args)
            typ = args[0].strip()
            p2, l2 = int(args[1]), int(args[2])
            d2 = lit_bytes(args[3])
            p1, l1 = int(args[4]), int(args[5])
            d1 = lit_bytes(args[6])
            rows.append({"line": start + 1, "type": typ, "p2": p2, "l2": l2,
                         "d2": d2, "p1": p1, "l1": l1, "d1": d1,
                         "ext_gated": ext_next, "compiled_out": dead})
            ext_next = False
        i += 1
    return rows


def first_match(data, ext, rows):
    """Return (row_index, row) of the first matching live row, else None."""
    for idx, r in enumerate(rows):
        if r["compiled_out"]:
            continue
        if r["ext_gated"] and not (ext and ext.lower() == "snd"):
            continue
        if len(data) < r["p1"] + r["l1"]:
            continue
        # C memcmp reads l bytes from the literal's array, which includes
        # the implicit NUL terminator ("ring.bin", l=9 -> "ring.bin\0").
        d1 = (r["d1"] or b"") + b"\x00"
        if data[r["p1"]:r["p1"] + r["l1"]] != d1[:r["l1"]]:
            continue
        # memcmp over l2==0 always equals; beyond-EOF bytes treated as
        # non-match (deterministic stand-in for the stack-buffer read).
        if r["p2"] + r["l2"] > len(data):
            if r["l2"]:
                continue
        d2 = (r["d2"] or b"") + b"\x00"
        if data[r["p2"]:r["p2"] + r["l2"]] != d2[:r["l2"]]:
            continue
        return idx, r
    return None


if __name__ == "__main__":
    rows = parse_rows()
    print(f"{len(rows)} CHECK rows parsed "
          f"({sum(r['compiled_out'] for r in rows)} compiled-out, "
          f"{sum(r['ext_gated'] for r in rows)} ext-gated)")
    for i, r in enumerate(rows):
        print(f"{i:3d} L{r['line']:4d} {r['type']:10s} "
              f"p1={r['p1']} l1={r['l1']} d1={r['d1']!r} "
              f"p2={r['p2']} l2={r['l2']} d2={r['d2']!r} "
              f"{'EXT' if r['ext_gated'] else ''}{'#if0' if r['compiled_out'] else ''}")
