import socket, struct, sys, time
def t(name, fn):
    try:
        r = fn(); print(f"{name}: OK {r}")
    except Exception as e:
        print(f"{name}: ERR {type(e).__name__}: {e}")

# 1. connect() to port 0
def c0():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("0.0.0.0", 0))
    s.connect(("127.0.0.1", 0))
    p = s.getpeername()
    return p
t("udp-connect-port0", c0)

# 2. overlapping binds with SO_REUSEADDR
def ob():
    a = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); a.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    a.bind(("0.0.0.0", 46199))
    b = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); b.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    b.bind(("127.0.0.1", 46199))
    return "both bound"
t("overlap-bind-reuseaddr", ob)

# 3. multicast on lo: join + send + recv
def mlo():
    ifidx = socket.if_nametoindex("lo")
    r = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    r.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    r.bind(("0.0.0.0", 46198))
    r.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, struct.pack("4s4s", socket.inet_aton("239.255.42.99"), socket.inet_aton("0.0.0.0")) + struct.pack("I", ifidx))
    r.settimeout(1.0)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, struct.pack("4s", socket.inet_aton("127.0.0.1")))
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
    s.sendto(b"hello-lo-mcast", ("239.255.42.99", 46198))
    data, peer = r.recvfrom(64)
    return f"recv {data!r} from {peer}"
t("multicast-on-lo", mlo)
