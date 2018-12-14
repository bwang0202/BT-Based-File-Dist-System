#!/bin/bash
set -e

FILEID=1234
PORT=8001
RESULTFILE="r.txt"
PEERS=10
TOTAL=$((PEERS*200))

rm -f $RESULTFILE
touch $RESULTFILE

python tracker_simple.py >/dev/null 2>/dev/null &

for i in $(seq 1 $PEERS)
do
	PORT=$((PORT + 1))
	set -x
	python3 controller.py $PORT "localhost:8999" $FILEID $i $TOTAL "$RESULTFILE" $(($((200*i))-199)) $(($((200*i))+1)) &
	set +x
	sleep 1
done


tail -f $RESULTFILE
