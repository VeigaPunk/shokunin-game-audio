def _pwbind_r87_last_snap(leg):
    """The last present snap (the stable one)."""
    for s in reversed(leg.get("snaps") or []):
        if s.get("present"):
            return s
    return (leg.get("snaps") or [{}])[-1]
