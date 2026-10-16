def _pactlmon_r85_family_lock():
    """Same-family exclusion — two concurrent pactlmon runs would
    cross-credit monitor taps and contest the collision/cycle sinks, so
    a second --probe-pactlmon-r85 waits HERE (the r82 convention)."""
    path = Path(tempfile.gettempdir()) / \
        "measure_audio-pactlmon-r85.lock"
    try:
        fd = os.open(str(path), os.O_RDWR | os.O_CREAT, 0o644)
    except OSError:
        return None
    fcntl.flock(fd, fcntl.LOCK_EX)
    try:
        os.ftruncate(fd, 0)
        os.write(fd, f"pid={PACTLMON_R85_PID} ns={PACTLMON_R85_NS} "
                     f"role={PACTLMON_R85_ROLE}\n".encode())
    except OSError:
        pass
    return fd


