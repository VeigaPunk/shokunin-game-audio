import sys, time
path, fifo, hold = sys.argv[1], sys.argv[2], float(sys.argv[3])
f = open(fifo, 'wb', buffering=0)
f.write(open(path, 'rb').read())
time.sleep(hold)
f.close()
