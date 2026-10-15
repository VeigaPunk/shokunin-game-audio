import socket, time, sys, numpy as np
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("127.0.0.1", 46100)); s.settimeout(float(sys.argv[1]) if len(sys.argv)>1 else 2.0)
pkts=[]; t0=time.monotonic()
try:
    while True:
        d,a = s.recvfrom(2048); pkts.append((time.monotonic()-t0, d))
        if len(pkts)>=3000: break
except socket.timeout: pass
print("packets:", len(pkts), "sizes:", sorted(set(len(p[1]) for p in pkts))[:5])
if pkts:
    hdr = pkts[0][1][:12]
    print("hdr:", hdr.hex(), "V=%d PT=%d seq=%d ts=%d ssrc=%08x" % (hdr[0]>>6, hdr[1]&0x7f, int.from_bytes(hdr[2:4],'big'), int.from_bytes(hdr[4:8],'big'), int.from_bytes(hdr[8:12],'big')))
    seqs=[int.from_bytes(p[1][2:4],'big') for p in pkts]
    tss=[int.from_bytes(p[1][4:8],'big') for p in pkts]
    dseq=[(seqs[i+1]-seqs[i])%65536 for i in range(len(seqs)-1)]
    dts=[(tss[i+1]-tss[i])%2**32 for i in range(len(tss)-1)]
    print("seq deltas:", sorted(set(dseq)), "ts deltas:", sorted(set(dts)))
    arr=np.frombuffer(b"".join(p[1][12:] for p in pkts), dtype=">i2").reshape(-1,2)
    fl=arr[:,0].astype(float)/32768
    print("frames:", len(fl), "peak:", abs(fl).max())
    def goertzel(x,f,sr=48000):
        n=len(x); k=int(0.5+n*f/sr); w=2*np.pi*k/n; c=np.cos(w); s_=np.sin(w)
        coeff=2*c; q1=0.0;q2=0.0
        for v in x: q0=coeff*q1-q2+v; q2=q1; q1=q0
        return q1*q1+q2*q2-coeff*q1*q2
    print("Goertzel 997Hz=%.1f 440Hz=%.1f 2000Hz=%.1f" % (goertzel(fl,997),goertzel(fl,440),goertzel(fl,2000)))
