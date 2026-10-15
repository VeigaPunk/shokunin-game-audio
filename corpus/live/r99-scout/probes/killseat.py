#!/usr/bin/env python3
"""r99-scout: kill ONLY this seat's private core/wp processes (matched by cmdline).

Never matches the shared daemons (/usr/bin/pipewire, /usr/bin/wireplumber with the
operator's config) because those cmdlines do not carry the r99s seat path.
"""
import os, signal, sys, time

SEAT = os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(__file__))))
PATTERNS = (SEAT + "/conf/pw/r99s-pipewire.conf",)


def cmdline(pid):
    try:
        return open("/proc/%d/cmdline" % pid, "rb").read().replace(b"\0", b" ").decode(errors="replace")
    except OSError:
        return ""


def main():
    killed = []
    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue
        pid = int(entry)
        if pid == os.getpid():
            continue
        c = cmdline(pid)
        if any(p in c for p in PATTERNS):
            try:
                os.kill(pid, signal.SIGTERM)
                killed.append(pid)
            except OSError:
                pass
    time.sleep(1.0)
    for pid in killed:
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass
    # seat-started wireplumber: cmdline carries the seat's xdg-config via env, so match
    # on the private runtime dir instead (read from /proc/<pid>/environ)
    wp = []
    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue
        pid = int(entry)
        if pid == os.getpid() or pid in killed:
            continue
        try:
            env = open("/proc/%d/environ" % pid, "rb").read().replace(b"\0", b"\n").decode(errors="replace")
        except OSError:
            continue
        if ("PIPEWIRE_RUNTIME_DIR=" + SEAT + "/run") in env and "wireplumber" in cmdline(pid):
            try:
                os.kill(pid, signal.SIGTERM)
                wp.append(pid)
            except OSError:
                pass
    time.sleep(1.0)
    for pid in wp:
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass
    for f in ("core.pid", "wp.pid"):
        p = os.path.join(SEAT, "run", f)
        if os.path.exists(p):
            os.remove(p)
    print("killed cores:", killed, "wp:", wp)


if __name__ == "__main__":
    main()
