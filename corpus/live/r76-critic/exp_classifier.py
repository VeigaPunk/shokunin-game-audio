import importlib.util, struct, wave, os, tempfile, json
spec = importlib.util.spec_from_file_location("ma", "corpus/fixtures/measure_audio.py")
ma = importlib.util.module_from_spec(spec); spec.loader.exec_module(ma)
tmp = tempfile.mkdtemp(prefix="r76crit-", dir="corpus/live/r76-critic")

def mkwav(path, ndata):
    with open(path,"wb") as f:
        f.write(b"RIFF"+struct.pack("<I",36+ndata)+b"WAVE")
        f.write(b"fmt "+struct.pack("<IHHIIHH",16,1,2,48000,192000,4,16))
        f.write(b"data"+struct.pack("<I",ndata))
        f.write(b"\x00"*ndata)
    return path

# 1) empty capture: 44-byte finalized wav (the shape a FAILED pw-record/parecord leaves)
p0 = mkwav(os.path.join(tmp,"empty.wav"), 0)
i0 = ma._capture_wav_inspect(ma.Path(p0))
print("EMPTY44 inspect:", json.dumps(i0))
print("EMPTY44 out_kind:", ma._capture_out_kind(i0))
# same file as a REDUCED sever leaf (what the name axis actually sees)
leaf = {"exists": True, "file_zero_bytes": False, "riff_size_field": i0["riff_size_field"],
        "data_declared_field": i0["data_declared_field"], "data_finalized": i0["data_finalized"],
        "data_actual_zero": True, "data_64k_aligned": True}
print("EMPTY44 sever-leaf out_kind:", ma._capture_out_kind(leaf))

# 2) parser verdict with the fmt leaf missing (frame_bytes == 0)
p1 = mkwav(os.path.join(tmp,"real.wav"), 4096)
i1 = ma._capture_wav_inspect(ma.Path(p1))
print("REAL inspect fmt:", i1.get("fmt"), "data_actual:", i1.get("data_actual"))
print("REAL parser verdict (fmt present):", json.dumps(ma._capture_parser_verdict(p1, i1)))
i1b = dict(i1); i1b.pop("fmt")
print("REAL parser verdict (fmt ABSENT):", json.dumps(ma._capture_parser_verdict(p1, i1b)))

# 3) partition probe: riff says finalized while data is a placeholder
def raw(path, riff_sz, data_sz, ndata):
    with open(path,"wb") as f:
        f.write(b"RIFF"+struct.pack("<I",riff_sz)+b"WAVE")
        f.write(b"fmt "+struct.pack("<IHHIIHH",16,1,2,48000,192000,4,16))
        f.write(b"data"+struct.pack("<I",data_sz))
        f.write(b"\x00"*ndata)
    return path
for nm,(rs,ds,nd) in {"riff_final_data_ff":(None,0xFFFFFFFF,1024),"riff8_data_ff":(8,0xFFFFFFFF,1024),
                      "riff_final_data_80":(None,0x80000000,1024)}.items():
    p = os.path.join(tmp, nm+".wav")
    n = 36+8+nd if rs is None else rs
    raw(p, n if rs is None else rs, ds, nd)
    i = ma._capture_wav_inspect(ma.Path(p))
    print(nm, "->", i.get("riff_size_field"), i.get("data_declared_field"), "data_finalized", i.get("data_finalized"),
          "out_kind", ma._capture_out_kind(i))
print("TMP:", tmp)
