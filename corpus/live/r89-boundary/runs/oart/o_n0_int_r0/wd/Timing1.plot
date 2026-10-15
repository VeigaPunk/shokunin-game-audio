set output 'Timing1.svg
set terminal svg
set multiplot
set grid
set title "Audio driver timing"
set xlabel "audio cycles"
set ylabel "usec"
plot "o_int" using 3 title "Audio driver delay (h/w ptr - wakeup time)" with lines, "o_int" using 1 title "Audio period (current wakeup - prev wakeup)" with lines,"o_int" using 4 title "Audio estimated (cycle period or quantum)" with lines
unset multiplot
unset output
