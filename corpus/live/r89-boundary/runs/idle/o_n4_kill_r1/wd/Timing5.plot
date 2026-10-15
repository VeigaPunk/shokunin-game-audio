set output 'Timing5.svg
set terminal svg
set multiplot
set grid
set key tmargin
set title "Clients duration (active -> finished)"
set xlabel "audio cycles"
set ylabel "usec"
plot "idle_o" using 10 title "Lavf63.1.101/258" with lines
unset multiplot
unset output
