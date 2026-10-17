import sys, time
path, fifo, chunk, gap = sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4])
d = open(path, 'rb').read()
f = open(fifo, 'wb', buffering=0)
for i in range(0, len(d), chunk):
    f.write(d[i:i+chunk])
    time.sleep(gap)
f.close()
