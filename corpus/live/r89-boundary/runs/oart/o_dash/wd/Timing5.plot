set output 'Timing5.svg
set terminal svg
set multiplot
set grid
set key tmargin
set title "Clients duration (active -> finished)"
set xlabel "audio cycles"
set ylabel "usec"
plot "-" using 10 title "r98s_drain/194" with lines
unset multiplot
unset output
