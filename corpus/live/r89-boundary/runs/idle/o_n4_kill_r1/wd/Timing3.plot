set output 'Timing3.svg
set terminal svg
set multiplot
set grid
set key tmargin
set title "Clients end date (scheduled -> finished)"
set xlabel "audio cycles"
set ylabel "usec"
plot "idle_o" using 1 title "Audio period" with lines, "idle_o" using 8 title "Lavf63.1.101/258" with lines
unset multiplot
unset output
