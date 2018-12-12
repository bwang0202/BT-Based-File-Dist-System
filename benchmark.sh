#!/bin/bash
set -e

FILEID=1234
PORT=9001
RESULTFILE="r.txt"
PEERS=10
TOTAL=$((PEERS*5))

rm -f $RESULTFILE
touch $RESULTFILE

python tracker_simple.py >/dev/null 2>/dev/null &
python -c 'import time; print int(round(time.time() * 1000000))' >> $RESULTFILE

for i in $(seq 1 $PEERS)
do
	PORT=$((PORT + 1))
	set -x
	python3 controller.py $PORT "localhost:8999" $FILEID $i $TOTAL "$RESULTFILE" $(($((5*i))-4)) $(($((5*i))-3)) $(($((5*i))-2)) $(($((5*i))-1)) $((5*i)) &
	set +x
	sleep 1
done


tail -f $RESULTFILE
