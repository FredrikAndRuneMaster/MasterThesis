set terminal png size 800,225
set key top center outside

stats '10-all.txt' using 1

set output "wp70_detection_graph.png"

set ytics 1,1,6
set ytics add ("Ground truth" 1)
set ytics add ("10%% confidence" 2)
set ytics add ("30%% confidence" 3)
set ytics add ("50%% confidence" 4)
set ytics add ("70%% confidence" 5)
set ytics add ("90%% confidence" 6)

set xlabel "Frame number"

set yrange[0:7]
set xrange[*:STATS_records]


plot "90-detected_polyps.txt" using 1:2 notitle with points pointtype 7 pointsize 1 lc rgb 'blue', \
	 "70-detected_polyps.txt" using 1:2 notitle with points pointtype 7 pointsize 1 lc rgb '#B22222', \
	 "50-detected_polyps.txt" using 1:2 notitle with points pointtype 7 pointsize 1 lc rgb '#C0C0C0', \
     "30-detected_polyps.txt" using 1:2 notitle with points pointtype 7 pointsize 1 lc rgb '#DAA520', \
     "10-detected_polyps.txt" using 1:2 notitle with points pointtype 7 pointsize 1 lc rgb '#32CD32', \
     "10-ground_truth.txt" using 1:2 notitle with points pointtype 7 pointsize 1 lc rgb '#696969'

exit
