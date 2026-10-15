import socket, struct, time
def counters(iface):
    for line in open("/proc/net/dev"):
        if line.strip().startswith(iface + ":"):
            f = line.split(":")[1].split()
            return int(f[0]), int(f[8])  # rx packets, tx packets
def send_batch(n, bind_lo):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if bind_lo:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, b"lo")
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, struct.pack("4s", socket.inet_aton("127.0.0.1")))
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
    s.connect(("239.255.42.97", 46196))
    for i in range(n):
        s.send(b"x" * 100)
    s.close()
r = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
r.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
r.bind(("0.0.0.0", 46196))
r.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, struct.pack("4s4s", socket.inet_aton("239.255.42.97"), socket.inet_aton("0.0.0.0")) + struct.pack("I", socket.if_nametoindex("lo")))
r.settimeout(0.2)
for label, bind_lo in (("default-route", False), ("bound-lo", True)):
    rx0, tx0 = counters("enp7s0")
    send_batch(200, bind_lo)
    got = 0
    while True:
        try:
            r.recvfrom(256); got += 1
        except socket.timeout:
            break
    rx1, tx1 = counters("enp7s0")
    print(f"{label}: enp7s0 tx delta={tx1-tx0} rx delta={rx1-rx0} local_recv={got}")
