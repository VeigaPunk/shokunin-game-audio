import math, struct, wave, hashlib
from pathlib import Path
out=Path(__file__).parent
rate=48000; n=5760
# Deterministic 1 kHz integer-cycle sinusoid, amplitude 0.25; derive PCM16 first, then scale to PCM24.
x=[round(0.25*32767*math.sin(2*math.pi*1000*i/rate)) for i in range(n)]
for name,width,vals in [('control_pcm16.wav',2,x),('candidate_pcm24.wav',3,[v*256 for v in x])]:
    p=out/name
    with wave.open(str(p),'wb') as w:
        w.setnchannels(1); w.setsampwidth(width); w.setframerate(rate)
        if width==2: raw=b''.join(struct.pack('<h',v) for v in vals)
        else: raw=b''.join((v & 0xffffff).to_bytes(3,'little') for v in vals)
        w.writeframes(raw)
    print(name, hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_size)
