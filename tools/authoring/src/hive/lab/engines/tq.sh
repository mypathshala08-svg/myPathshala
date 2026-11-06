#!/bin/bash
# tq.sh NAME "SQL" -> Trino CLI output (aligned) saved to captures/NAME.txt
docker exec trino trino --output-format ALIGNED --execute "$2" 2>&1 | grep -vE "^WARNING|jline|^Oct [0-9]+, 20" > /root/lab/hive/captures/$1.txt
cat /root/lab/hive/captures/$1.txt
