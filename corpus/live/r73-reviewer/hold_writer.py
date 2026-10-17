import sys,time
f=open(sys.argv[1],'wb',buffering=0)
f.write(open(sys.argv[2],'rb').read())
time.sleep(float(sys.argv[3]))
f.close()
