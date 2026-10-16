def _pwprof_r89_family_lock():
    """Same-family exclusion at a FIXED lane path — the r84 F1 3-seat
    consensus (never $TMPDIR; cross-TMPDIR same-family runs must still
    exclude). A second --probe-pwprof-r89 waits HERE."""
    path = ROOT / "live" / "measure_audio-pwprof-r89.lock"
    try:
        fd = os.open(str(path), os.O_RDWR | os.O_CREAT, 0o644)
    except OSError:
        return None
    fcntl.flock(fd, fcntl.LOCK_EX)
    try:
        os.ftruncate(fd, 0)
        os.write(fd, f"pid={PWPROF_R89_PID} ns={PWPROF_R89_NS} "
                     f"role={PWPROF_R89_ROLE}\n".encode())
    except OSError:
        pass
    return fd


