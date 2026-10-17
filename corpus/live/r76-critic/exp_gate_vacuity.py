import sys; sys.dont_write_bytecode = True
import importlib.util, json, hashlib, subprocess
spec = importlib.util.spec_from_file_location("ma", "corpus/fixtures/measure_audio.py")
ma = importlib.util.module_from_spec(spec); spec.loader.exec_module(ma)

def empty_inv():
    # a degraded host: enumeration empty, demuxers present (so the
    # dependent legs still run and can be classified)
    return {"sources": [], "monitors": [], "default_source": None,
            "default_sink": None, "server_name": None, "pw_capture_ports": [],
            "alsa_capture_devices": [], "alsa_plugins": [],
            "ffmpeg_demuxers": {"pulse": True, "alsa": True},
            "pactl_sources_exit": 0, "pw_link_exit": 0, "arecord_l_exit": 0}

ma._capture_inventory = empty_inv
e = ma.capture_gate_r76_entry()
print("viability:", json.dumps(e["viability"]))
print("legs present:", sorted(e["gate"].keys()))
print("EXPECTED legs total:", 12, "-> present:", len(e["gate"]))
print("failures:", e["failures"])
print("MONITOR-ALIAS LEG ABSENT:", "pwrecord_monitor_alias" not in e["gate"])
