set output 'Timing1.svg
set terminal svg
set multiplot
set grid
set title "Audio driver timing"
set xlabel "audio cycles"
set ylabel "usec"
plot "eager_x" using 3 title "Audio driver delay (h/w ptr - wakeup time)" with lines, "eager_x" using 1 title "Audio period (current wakeup - prev wakeup)" with lines,"eager_x" using 4 title "Audio estimated (cycle period or quantum)" with lines
unset multiplot
unset output
