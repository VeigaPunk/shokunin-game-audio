bash -c ps -eo pid,pcpu,args --sort=-pcpu | grep -E 'r9[0-9]|godot|filter-chain|yes|dd' | grep -v grep | head -20
