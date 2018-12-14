# BT-Based-File-Dist-System
python tracker_simple.py
python3 controller.py PORT TRACKER_URL FILE_ID PEER_ID TOTAL_PIECES OUTPUT_FILE subpieces_start subpieces_end+1


python3 controller.py 8007 localhost:8999 1234 1 1800 r.txt 1 601
python3 controller.py 9004 localhost:8999 1234 2 1800 r.txt 1 601
python3 controller.py 8005 localhost:8999 1234 3 1800 r.txt 601 1201
python3 controller.py 8006 localhost:8999 1234 4 1800 r.txt 1201 1801


python3 controller.py 8007 localhost:8999 1234 1 1800 r.txt 1 601
python3 controller.py 8005 localhost:8999 1234 3 1800 r.txt 601 1201
python3 controller.py 8006 localhost:8999 1234 4 1800 r.txt 601 1201