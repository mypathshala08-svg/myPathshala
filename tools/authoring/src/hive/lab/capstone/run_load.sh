#!/bin/bash
# usage: run_load.sh 2026-10-01 [2026-10-31]   -> runs the nightly load for each date, logs time
s=$1; e=${2:-$1}; d=$s
while [[ "$d" < "$e" || "$d" == "$e" ]]; do
  t0=$(date +%s.%N)
  docker exec -e HADOOP_CLIENT_OPTS='-Dorg.jline.terminal.type=dumb -Dorg.jline.terminal.provider=exec' hiveserver2 \
    beeline -u jdbc:hive2://localhost:10000/tiffingo_dw -n hive --silent=true \
    --hivevar load_date=$d -f /data/daily_load.hql > /root/lab/hive/capstone/logs/load_$d.log 2>&1
  rc=$?; t1=$(date +%s.%N)
  printf "%s rc=%s %.1fs\n" $d $rc $(echo "$t1 - $t0" | bc)
  d=$(date -I -d "$d + 1 day")
done
