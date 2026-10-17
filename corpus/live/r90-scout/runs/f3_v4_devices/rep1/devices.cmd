bash -c ls -la /dev/video* 2>&1; lsmod | grep -icE 'v4l2|uvcvideo'; ls /sys/class/video4linux 2>&1
