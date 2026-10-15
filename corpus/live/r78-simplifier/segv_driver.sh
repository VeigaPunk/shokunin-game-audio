#!/bin/bash
# r78 SIMPLIFIER — bounded mechanism probe driver (6 short runs, control arm)
FX=/tmp/r78-simpl/control/corpus/fixtures/measure_audio.py
OUT=/tmp/r78-simpl/segv-mechanism.txt
: > $OUT
for i in 1 2 3; do
  echo "--- fresh-$i ---" >> $OUT
  python3 /tmp/r78-simpl/segv_mechanism.py $FX F >> $OUT 2>&1
done
for i in 1 2 3; do
  echo "--- reused-$i ---" >> $OUT
  python3 /tmp/r78-simpl/segv_mechanism.py $FX N >> $OUT 2>&1
done
echo DONE >> $OUT
