import math, struct, wave
from pathlib import Path
p=Path(__file__).parent
rate=48000; n=5760
# Deterministic UI-like two-tone transient; signed PCM16 grid.
samples=[max(-32768,min(32767,round((.25*math.sin(2*math.pi*1000*i/rate)+.08*math.sin(2*math.pi*1500*i/rate))*32767))) for i in range(n)]
data=struct.pack('<'+'h'*n,*samples)
with wave.open(str(p/'pcm16-tag1.wav'),'wb') as w:
 w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(data)
# WAVEFORMATEXTENSIBLE: PCM subtype GUID; mono front-center mask.
guid=bytes.fromhex('0100000000001000800000aa00389b71')
fmt=struct.pack('<HHIIHHHHI',0xfffe,1,rate,rate*2,2,16,22,16,0x4)+guid
assert len(fmt)==40
riff_data=b'WAVE'+b'fmt '+struct.pack('<I',40)+fmt+b'data'+struct.pack('<I',len(data))+data
(p/'extensible-40.wav').write_bytes(b'RIFF'+struct.pack('<I',len(riff_data))+riff_data)
