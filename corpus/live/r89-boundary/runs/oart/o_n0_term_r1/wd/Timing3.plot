set output 'Timing3.svg
set terminal svg
set multiplot
set grid
set key tmargin
set title "Clients end date (scheduled -> finished)"
set xlabel "audio cycles"
set ylabel "usec"
plot "o_int" using 1 title "Audio period" with lines, "o_int" using 8 title "pw-play/258" with lines, "o_int" using 16 title "pw-play/164" with lines
unset multiplot
unset output
