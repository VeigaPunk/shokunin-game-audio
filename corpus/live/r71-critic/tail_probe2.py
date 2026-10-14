import sys
sys.path.insert(0, "corpus/fixtures")
import measure_audio as m
from pathlib import Path
p = Path("corpus/live/r71-critic/test.wv")
data = p.read_bytes()
for i in (1, 2):
    leg = m.ffprobe_leg("pipe:", "pipe:", data=data)
    print(i, "ffmpeg_exit:", leg["ffmpeg_exit"])
    print("   ffmpeg_error:", repr(leg["ffmpeg_error"]))
