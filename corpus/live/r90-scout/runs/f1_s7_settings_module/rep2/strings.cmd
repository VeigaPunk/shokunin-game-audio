bash -c strings -a /usr/lib/wireplumber-0.5/libwireplumber-module-settings.so | grep -iE 'persistent|sm-settings|state' | sort -u
