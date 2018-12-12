#!/bin/bash
set -e

FILEID=1234
PORT=9001
RESULTFILE="r.txt"

rm -f $RESULTFILE
touch $RESULTFILE

python tracker_simple.py >/dev/null 2>/dev/null &

for i in {1..10}
do
	PORT=$((PORT + 1))
	set -x
	python3 controller.py $PORT "localhost:8999" $FILEID $i 50 "$RESULTFILE" $(($((5*i))-4)) $(($((5*i))-3)) $(($((5*i))-2)) $(($((5*i))-1)) $((5*i)) >/dev/null &
	set +x
done

python -c 'import time; print int(round(time.time() * 1000000))' >> $RESULTFILE

tail -f $RESULTFILE
