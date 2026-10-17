import numpy as np, wave, struct, hashlib, pathlib
p=pathlib.Path(__file__).parent
N=5760; rate=48000
n=np.arange(N)
x=.25*np.sin(2*np.pi*1000*n/rate)+.08*np.sin(2*np.pi*1500*n/rate)
# Quantize one common normalized sequence to PCM16; PCM24 uses the identical values.
i16=np.rint(x*32768).astype(np.int16)
# PCM24 integer representation uses the same amplitude, scaled by 256.
i24=i16.astype(np.int32)*256
with wave.open(str(p/'pair_pcm16.wav'),'wb') as w:
 w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(i16.astype('<i2').tobytes())
with open(p/'pair_pcm24.wav','wb') as f:
 f.write(b'RIFF'+struct.pack('<I',36+N*3)+b'WAVEfmt '+struct.pack('<IHHIIHH',16,1,1,rate,rate*3,3,24)+b'data'+struct.pack('<I',N*3))
 for v in i24:
  u=int(v)&0xffffff; f.write(bytes((u&255,(u>>8)&255,(u>>16)&255)))
for name,a in [('pcm16',i16.astype('<i2').tobytes()),('pcm24',i24.astype('<i4').tobytes())]: print(name,hashlib.sha256(a).hexdigest(),len(a))
print('intended_pcm16_sha256',hashlib.sha256(i16.astype('<i2').tobytes()).hexdigest())
