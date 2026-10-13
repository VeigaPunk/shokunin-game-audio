import math, wave, struct
from pathlib import Path
out=Path(".shokunin/audio/corpus/live/round-25/executor")
for name, rate, channels in (("sine_48k_stereo_pcm16.wav",48000,2),("sine_44k1_mono_pcm16.wav",44100,1)):
    frames=bytearray()
    for i in range(rate*4):
        v=round(.2*32767*math.sin(2*math.pi*440*i/rate))
        frames.extend(struct.pack("<h",v)*channels)
    with wave.open(str(out/name),"wb") as w:
        w.setnchannels(channels); w.setsampwidth(2); w.setframerate(rate); w.writeframes(frames)
