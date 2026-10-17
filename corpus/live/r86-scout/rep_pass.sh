#!/bin/bash
# r86 scout rep pass — every arm 3 reps, receipts under receipts/
R=receipts; mkdir -p $R
NID=133; PID=104; DEV=48
{
echo "## A. ls class census"
for i in 1 2 3; do
  echo "-- rep$i"; for c in Core Device Node Port Client Module Link Factory Metadata Profiler Session Endpoint ClientNode Bogus node; do
    n=$(pw-cli ls "$c" 2>/dev/null | grep -c "type PipeWire"); echo "$c=$n"
  done
done
echo "## B. namespace: ls<serial> vs info<id>"
for i in 1 2 3; do echo "-- rep$i"
  pw-cli ls 63 2>&1 | grep -E "id |type" | head -2
  pw-cli info 63 2>&1 | grep -E "id:|type:" | head -2
  echo "ls99999 lines: $(pw-cli ls 99999 2>&1 | wc -l)"; pw-cli info 99999 2>&1 | head -1
done
echo "## C. enum-params matrix"
for i in 1 2 3; do echo "-- rep$i"
  for a in "$NID Props" "$NID PropInfo" "$NID EnumFormat" "$NID Format" "$NID Latency" "$NID ProcessLatency" "$NID IO" "$NID Meta" "$PID EnumFormat" "$PID Format" "$PID Latency" "$PID IO" "$PID Meta" "$PID Props" "$DEV Profile" "$DEV EnumProfile" "$DEV Route" "$DEV EnumRoute" "$DEV Props" "33 Props" "$NID BogusParam" "99999 Props"; do
    set -- $a; o=$(pw-cli enum-params $1 $2 2>&1 | head -1); echo "id=$1 $2 => ${o:-EMPTY}"
  done
done
echo "## D. set-param surface"
for i in 1 2 3; do echo "-- rep$i"
  echo "malformed: $(pw-cli set-param $NID Props 'garbage' 2>&1)"
  echo "emptyobj: $(pw-cli set-param $NID Props '{ }' 2>&1 | head -1)"
  echo "unknownkey: $(pw-cli set-param $NID Props '{ zzz.r86: 7 }' 2>&1 | head -1)"
  echo "bogusparam: $(pw-cli set-param $NID Bogus '{ }' 2>&1)"
  echo "badid: $(pw-cli set-param 99999 Props '{ }' 2>&1)"
  echo "noarg: $(pw-cli set-param $NID Props 2>&1)"
  echo "fmt-write-id133 rc-ish: $(pw-cli set-param $NID EnumFormat '{ mediaType: 1, mediaSubtype: 1 }' 2>&1 | head -1 | cut -c1-60)"
  echo "port-latency-write: $(pw-cli set-param $PID Latency '{ direction: 0, minQuantum: 2.0 }' 2>&1 | head -1 | cut -c1-60)"
  pw-cli enum-params $PID Latency 2>/dev/null | grep -A1 minQuantum | tail -1
done
} > $R/abcd.txt 2>&1
echo "rep_pass done: $(wc -l < $R/abcd.txt) lines"
