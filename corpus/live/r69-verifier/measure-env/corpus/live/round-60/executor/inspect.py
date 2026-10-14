import struct,json,hashlib
from pathlib import Path
D=Path(__file__).parent
for f in sorted(D.glob('valid-*.wav')):
 b=f.read_bytes(); riff=b[:4].decode(); size=struct.unpack_from('<I',b,4)[0]; wave=b[8:12].decode(); off=b.index(b'fmt '); fl=struct.unpack_from('<I',b,off+4)[0]; p=off+8; tag,ch,rate,br,align,bits,cb,valid,mask=struct.unpack_from('<HHIIHHHHI',b,p); sub=b[p+24:p+40]; do=b.index(b'data'); ds=struct.unpack_from('<I',b,do+4)[0]; data=b[do+8:do+8+ds]
 print(json.dumps({'file':f.name,'file_bytes':len(b),'wav_sha256':hashlib.sha256(b).hexdigest(),'riff':riff,'riff_size':size,'wave':wave,'fmt_size':fl,'format_tag':hex(tag),'channels':ch,'rate':rate,'byte_rate':br,'block_align':align,'container_bits':bits,'cbSize':cb,'valid_bits':valid,'channel_mask':hex(mask),'subformat_guid':sub.hex(),'data_bytes':ds,'payload_sha256':hashlib.sha256(data).hexdigest()}))
