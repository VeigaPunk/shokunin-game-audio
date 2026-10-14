import struct, hashlib
from pathlib import Path
for name in ("valid-13.wav","valid-16.wav"):
 b=(Path(__file__).parent/name).read_bytes()
 assert b[:4]==b"RIFF" and b[8:12]==b"WAVE"
 off=12; chunks={}
 while off<len(b):
  tag=b[off:off+4]; size=struct.unpack_from("<I",b,off+4)[0]; chunks[tag]=b[off+8:off+8+size]; off+=8+size+(size&1)
 fmt=chunks[b"fmt "]; data=chunks[b"data"]
 tag,ch,rate,br,align,container,cb,valid,mask=struct.unpack_from("<HHIIHHHHI",fmt)
 print(name,"file_bytes",len(b),"wav_sha256",hashlib.sha256(b).hexdigest(),"riff_size",struct.unpack_from("<I",b,4)[0],"fmt_size",len(fmt),"format_tag",hex(tag),"channels",ch,"sample_rate",rate,"byte_rate",br,"block_align",align,"container_bits",container,"cbSize",cb,"valid_bits",valid,"channel_mask",hex(mask),"guid",fmt[24:].hex(),"data_bytes",len(data),"payload_sha256",hashlib.sha256(data).hexdigest())
