import math, struct, wave
from pathlib import Path
p=Path(__file__).parent
rate=48000
samples=[max(-32768,min(32767,round((.25*math.sin(2*math.pi*1000*i/rate)+.08*math.sin(2*math.pi*1500*i/rate))*32767))) for i in range(5760)]
data=struct.pack('<'+'h'*len(samples),*samples)
guid=bytes.fromhex('0100000000001000800000aa00389b71')
def write(name,mask,g=guid):
 fmt=struct.pack('<HHIIHHH',0xfffe,1,rate,rate*2,2,16,22)+struct.pack('<HI',16,mask)+g
 body=b'WAVE'+b'fmt '+struct.pack('<I',len(fmt))+fmt+b'data'+struct.pack('<I',len(data))+data
 (p/name).write_bytes(b'RIFF'+struct.pack('<I',len(body))+body)
write('mask0.wav',0);write('mask4.wav',4);write('bad-guid.wav',0,g=bytes.fromhex('0200000000001000800000aa00389b71'))
for n in ['mask0.wav','mask4.wav','bad-guid.wav']:
 b=(p/n).read_bytes(); off=b.index(b'fmt '); size=struct.unpack_from('<I',b,off+4)[0]; f=b[off+8:off+8+size]
 print(n,'bytes',len(b),'fmt_size',size,'tag',hex(struct.unpack_from('<H',f)[0]),'channels',struct.unpack_from('<H',f,2)[0],'rate',struct.unpack_from('<I',f,4)[0],'align',struct.unpack_from('<H',f,12)[0],'bits',struct.unpack_from('<H',f,14)[0],'cbSize',struct.unpack_from('<H',f,16)[0],'valid',struct.unpack_from('<H',f,18)[0],'mask',hex(struct.unpack_from('<I',f,20)[0]),'guid',f[24:40].hex(),'frames',len(data)//2)
