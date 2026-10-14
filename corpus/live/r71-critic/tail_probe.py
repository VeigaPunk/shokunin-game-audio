import sys, json
sys.path.insert(0, "corpus/fixtures")
import measure_audio as m
# simulate two runs of the ffmpeg leg on the seek-sensitive wv member
p = "corpus/live/r71-critic/test.wv"
for i in (1, 2):
    leg = m.ffprobe_leg(p, "file")
    print(i, "ffprobe:", leg["ffprobe_format"], leg["ffprobe_exit"], "| ffmpeg_exit:", leg["ffmpeg_exit"])
    print("   ffmpeg_error:", repr(leg["ffmpeg_error"]))
