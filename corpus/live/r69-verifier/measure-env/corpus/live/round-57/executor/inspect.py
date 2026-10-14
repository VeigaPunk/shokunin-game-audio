import struct,hashlib
from pathlib import Path
for n in (15,16):
 p=Path(__file__).parent/f"valid-{n}.wav"
 b=p.read_bytes(); f=b[20:60]
 print(p.name, "riff", b[:4].decode(), struct.unpack_from("<I",b,4)[0], b[8:12].decode(), "fmt",b[12:16].decode(),struct.unpack_from("<I",b,16)[0],"tag",hex(struct.unpack_from("<H",f,0)[0]),"channels",struct.unpack_from("<H",f,2)[0],"rate",struct.unpack_from("<I",f,4)[0],"align",struct.unpack_from("<H",f,12)[0],"container_bits",struct.unpack_from("<H",f,14)[0],"cbSize",struct.unpack_from("<H",f,16)[0],"valid_bits",struct.unpack_from("<H",f,18)[0],"mask",hex(struct.unpack_from("<I",f,20)[0]),"guid",f[24:40].hex(),"sha256",hashlib.sha256(b).hexdigest())
