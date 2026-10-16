def _pwbind_r87_family_lock():
    """Same-family exclusion at a FIXED lane path — the r84 F1 3-seat
    consensus: a $TMPDIR-scoped lock lets cross-TMPDIR same-family runs
    race, so this lives under corpus/live/ (outside $TMPDIR). A second
    --probe-pwbind-r87 waits HERE (the r82/r86 convention)."""
    path = ROOT / "live" / "measure_audio-pwbind-r87.lock"
    try:
        fd = os.open(str(path), os.O_RDWR | os.O_CREAT, 0o644)
    except OSError:
        return None
    fcntl.flock(fd, fcntl.LOCK_EX)
    try:
        os.ftruncate(fd, 0)
        os.write(fd, f"pid={PWBIND_R87_PID} ns={PWBIND_R87_NS} "
                     f"role={PWBIND_R87_ROLE}\n".encode())
    except OSError:
        pass
    return fd
