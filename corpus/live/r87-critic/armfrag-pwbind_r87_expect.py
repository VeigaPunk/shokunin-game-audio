def _pwbind_r87_expect(legs, failures, name, want):
    """Arm a routing leg: consumers == want (list)."""
    got = _pwbind_r87_consumers(legs[name])
    if got != want:
        failures.append(
            f"{name}: consumers={got} expected {want} — the binding "
            "lattice fails")
