def _btwit_r88_family_lock():
    """Same-family exclusion at a FIXED lane path — the r84 F1 3-seat
    consensus (never $TMPDIR; cross-TMPDIR same-family runs must still
    exclude). A second --probe-btwit-r88 waits HERE."""
    path = ROOT / "live" / "measure_audio-btwit-r88.lock"
    try:
        fd = os.open(str(path), os.O_RDWR | os.O_CREAT, 0o644)
    except OSError:
        return None
    fcntl.flock(fd, fcntl.LOCK_EX)
    try:
        os.ftruncate(fd, 0)
        os.write(fd, f"pid={BTWIT_R88_PID} ns={BTWIT_R88_NS} "
                     f"role={BTWIT_R88_ROLE}\n".encode())
    except OSError:
        pass
    return fd


