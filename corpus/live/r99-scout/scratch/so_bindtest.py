import socket, struct
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, b"lo")
    print("SO_BINDTODEVICE(lo): OK")
except OSError as e:
    print("SO_BINDTODEVICE(lo): ERR", e)
s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    s2.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, b"nonexistent99")
    print("SO_BINDTODEVICE(nonexistent99): OK (unexpected)")
except OSError as e:
    print("SO_BINDTODEVICE(nonexistent99): ERR", e)
# and multicast send with SO_BINDTODEVICE=lo, no IP_MULTICAST_IF
r = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
r.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ifidx = socket.if_nametoindex("lo")
r.bind(("0.0.0.0", 46197))
r.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, struct.pack("4s4s", socket.inet_aton("239.255.42.98"), socket.inet_aton("0.0.0.0")) + struct.pack("I", ifidx))
r.settimeout(1.0)
s3 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    s3.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, b"lo")
    s3.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
    s3.connect(("239.255.42.98", 46197))
    s3.send(b"bound-dev-lo")
    print("mcast send with SO_BINDTODEVICE=lo:", r.recvfrom(64))
except OSError as e:
    print("mcast send with SO_BINDTODEVICE=lo: ERR", e)
