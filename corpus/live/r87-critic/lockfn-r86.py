def _pwctl_r86_family_lock():
    """Same-family exclusion at a FIXED lane path — the r84 F1 3-seat
    consensus fix: a $TMPDIR-scoped lock lets two same-family runs on
    different TMPDIRs race and cross-credit node names, so this lock
    lives under corpus/live/ (outside $TMPDIR entirely). A second
    --probe-pwctl-r86 waits HERE (the r82 convention)."""
    path = ROOT / "live" / "measure_audio-pwctl-r86.lock"
    try:
        fd = os.open(str(path), os.O_RDWR | os.O_CREAT, 0o644)
    except OSError:
        return None
    fcntl.flock(fd, fcntl.LOCK_EX)
    try:
        os.ftruncate(fd, 0)
        os.write(fd, f"pid={PWCTL_R86_PID} ns={PWCTL_R86_NS} "
                     f"role={PWCTL_R86_ROLE}\n".encode())
    except OSError:
        pass
    return fd
