import sys, json
sys.path.insert(0, "corpus/fixtures")
import measure_audio as m
from pathlib import Path
e = m.ffprobe_transport_entry("wv_seek", Path("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r71-critic/test.wv"))
print("fork:", e["transport_fork"], "| failures:", e["failures"])
for g in e["transport_verdict_groups"]:
    print(" group:", g["transports"], "| fmt:", g["ffprobe_format"], "| exit:", g["ffmpeg_exit"], "| err:", g["ffmpeg_error"])
