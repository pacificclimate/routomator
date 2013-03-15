#!/bin/bash
set -e

#TWO FILES NEEDED: INPUT FLOW ACCUMULATION AND OUTPUT FLOW DIRECTION
#30 arc-second flow accumulation grid
ACC=flow-acc-15.asc
OUT=flow-dir-16th.asc
#output file is 1/16 degree -- change script for other resolutions
#END OF INPUT

#dump top six lines - get number of ROWS and COLS
head -n 6 $ACC > temp_head.junk

ROWS=`awk '{if(NR==2) print $2}' temp_head.junk`
COLS=`awk '{if(NR==1) print $2}' temp_head.junk`

# get remaining lines to process
tail -n +7 $ACC > temp_body.junk

#convert to long ints
#convert ascii longint temp_body.junk temp_li.junk $ROWS $COLS
./bin/convert ascii longint temp_body.junk temp_li.junk $ROWS $COLS

#run program to generate 1/16 degree flow directions
./bin/flowgen temp_li.junk $ROWS $COLS temp_fd.junk 15 15

#put new header back on top
RR=`echo $ROWS '/' '15.0' | bc -l`
CC=`echo $COLS '/' '15.0' | bc -l`
gawk '{if(NR==1) $2='"$CC"'; if(NR==2) $2='"$RR"'; if(NR==5) $2=0.0625; if(NR==6) $2=0; print $0; }' temp_head.junk > temp_newh.junk

cat temp_newh.junk temp_fd.junk > $OUT

rm -f temp*.junk
