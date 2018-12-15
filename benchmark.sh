#!/bin/bash
set -e

FILEID=1234
PORT=8001
RESULTFILE="r.txt"
PEER_PAIRS=5
TOTAL=$((PEER_PAIRS*400))

rm -f $RESULTFILE
touch $RESULTFILE

python tracker_simple.py >/dev/null 2>/dev/null &
j=0

for i in $(seq 1 $PEER_PAIRS)
do
	j=$((j + 1))
	PORT=$((PORT + 1))
	set -x
	python3 controller.py $PORT "localhost:8999" $FILEID $j $TOTAL "$RESULTFILE" $(($((400*i))-399)) $(($((400*i))+1)) &
	set +x
	sleep 1
	PORT=$((PORT + 1))
	j=$((j + 1))
	set -x
	python3 controller.py $PORT "localhost:8999" $FILEID $j $TOTAL "$RESULTFILE" $(($((400*i))-399)) $(($((400*i))+1)) &
	set +x
done


tail -f $RESULTFILE
