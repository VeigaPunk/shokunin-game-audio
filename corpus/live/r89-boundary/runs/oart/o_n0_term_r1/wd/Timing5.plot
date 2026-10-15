set output 'Timing5.svg
set terminal svg
set multiplot
set grid
set key tmargin
set title "Clients duration (active -> finished)"
set xlabel "audio cycles"
set ylabel "usec"
plot "o_int" using 10 title "pw-play/258" with lines, "o_int" using 18 title "pw-play/164" with lines
unset multiplot
unset output
