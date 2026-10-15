bash -c ls /dev/video* 2>&1; ls /sys/class/video4linux 2>&1; lsmod | grep -icE 'v4l2|uvcvideo'
