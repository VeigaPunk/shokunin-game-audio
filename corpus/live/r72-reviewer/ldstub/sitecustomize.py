"""r72-reviewer: environment stub — simulate a host WITHOUT libsndfile.so.1.

Placed on PYTHONPATH so it runs before the fixture's module body. Any
ctypes.CDLL("libsndfile.so.1") then raises, which is what a host lacking the
library would produce. Used to test whether the r72 arm introduced an
import-time hard dependency for EVERY mode of the tracked fixture.
"""
import ctypes

_real_CDLL = ctypes.CDLL


def _CDLL(name, *args, **kwargs):
    if isinstance(name, str) and "libsndfile" in name:
        raise OSError(f"stub: {name} not present on this host")
    return _real_CDLL(name, *args, **kwargs)


ctypes.CDLL = _CDLL
