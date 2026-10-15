import socket, struct, sys, time
def tx(): return int(open("/sys/class/net/enp7s0/statistics/tx_packets").read())
def burst(n, dev):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, dev.encode())
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, struct.pack("4s", socket.inet_aton("127.0.0.1")))
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
    s.connect(("239.255.42.96", 46195))
    for _ in range(n): s.send(b"x"*12)
    s.close()
for dev in ("lo",):
    for i in range(3):
        a=tx(); burst(20000, dev); b=tx()
        print(dev, "tx delta", b-a)
