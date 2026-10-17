import os, sys, time
fifo, path, hold = sys.argv[1], sys.argv[2], float(sys.argv[3])
f = open(fifo, 'wb', buffering=0)
f.write(open(path, 'rb').read())
print('WROTE', flush=True)
time.sleep(hold)
print('CLOSING', flush=True)
f.close()
