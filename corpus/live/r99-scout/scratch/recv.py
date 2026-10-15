import socket, time, sys, json
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("127.0.0.1", 46100))
s.settimeout(float(sys.argv[1]) if len(sys.argv)>1 else 3.0)
pkts=[]
t0=time.monotonic()
try:
    while True:
        d,a = s.recvfrom(2048)
        pkts.append((time.monotonic()-t0, len(d), d[:16].hex(), a))
        if len(pkts)>=4000: break
except socket.timeout:
    pass
print("packets:", len(pkts))
if pkts:
    print("first:", pkts[0]); print("last:", pkts[-1])
    print("sizes:", sorted(set(p[1] for p in pkts)))
    # inter-arrival
    d=[round(pkts[i+1][0]-pkts[i][0],4) for i in range(min(9,len(pkts)-1))]
    print("first intervals:", d)
