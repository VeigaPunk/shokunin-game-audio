from pathlib import Path
import struct
p=Path(__file__).parent
for name in ('valid14.wav','valid16.wav'):
 b=(p/name).read_bytes(); i=b.index(b'fmt '); size=struct.unpack_from('<I',b,i+4)[0]; f=b[i+8:i+8+size]
 print(name,'riff',b[:4],'wave',b[8:12],'fmt_size',size,'tag',hex(struct.unpack_from('<H',f)[0]),'channels',struct.unpack_from('<H',f,2)[0],'rate',struct.unpack_from('<I',f,4)[0],'block_align',struct.unpack_from('<H',f,12)[0],'container_bits',struct.unpack_from('<H',f,14)[0],'cbSize',struct.unpack_from('<H',f,16)[0],'valid_bits',struct.unpack_from('<H',f,18)[0],'mask',hex(struct.unpack_from('<I',f,20)[0]),'guid',f[24:40].hex(),'data_bytes',len(b)-68)
