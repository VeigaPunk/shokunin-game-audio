bash -c ls -la /usr/lib/spa-0.2/v4l2/; strings -a /usr/lib/spa-0.2/v4l2/libspa-v4l2.so | grep -cE 'v4l2' 
