# logs_lab.sh: a job fails on bad data. Find out why, using only YARN's logs and tools.
# Run inside the namenode container (in /tmp/mr). ItemRevenue (Lesson 8.1) has no check for a bad amount.
cd /tmp/mr
hdfs dfs -rm -r -f -skipTrash /out/dbg > /dev/null 2>&1
echo "== 1. the client only says it failed"
hadoop jar mr.jar ItemRevenue /user/hadoop/data/dirty_orders.csv /out/dbg > /tmp/dbg.log 2>&1
grep -E "Task Id|^Error|failed with state|Failed map tasks" /tmp/dbg.log | sed -E 's/^[0-9-]+ [0-9:]+ INFO  //' | sort -u | head -6 | cut -c1-160
app=$(grep -o "application_[0-9_]*" /tmp/dbg.log | head -1)
echo "== 2. what the ResourceManager remembers"
yarn application -status $app 2>/dev/null | grep -E "State|Final-State|Diagnostics" -A1 | grep -v "^--" | sed 's/^\s*//' | head -6
echo "== 3. aggregated logs: which containers left logs?"
sleep 8
yarn logs -applicationId $app -show_application_log_info 2>/dev/null | grep -E "Container|Application State" | head -8
echo "-- they live in HDFS now:"
hdfs dfs -ls -R /tmp/logs/hadoop 2>/dev/null | grep $app | awk '{print $5, $8}' | head -3
echo "== 4. the failed attempt's syslog: the real exception with a line number"
c=$(yarn logs -applicationId $app -show_application_log_info 2>/dev/null | grep -o "container_[0-9_]*_000002" | head -1)
yarn logs -applicationId $app -containerId $c -log_files syslog 2>/dev/null | grep -E -A4 "^java.lang|Exception" | grep -E "Exception|at ItemRevenue|at org.apache.hadoop.mapred.MapTask.run" | head -4 | cut -c1-160
echo "== 5. which line of input? (search the data for the bad value)"
hdfs dfs -cat /user/hadoop/data/dirty_orders.csv | grep -n -m3 ",abc$" 2>/dev/null
echo "== 6. the ApplicationMaster's own log (-am 1)"
yarn logs -applicationId $app -am 1 -log_files syslog 2>/dev/null | grep -E "Task failed|failedMaps|JOB_FAILED|Job failed" | sed -E 's/^[0-9-]+ [0-9:,]+ //' | head -3 | cut -c1-170
echo "== 7. more detail: the same job with DEBUG logging in the map tasks"
for lvl in INFO DEBUG; do
  hdfs dfs -rm -r -f -skipTrash /out/lvl > /dev/null 2>&1
  hadoop jar mr.jar ItemRevenue -D mapreduce.map.log.level=$lvl /user/hadoop/data/canteen_orders.csv /out/lvl > /tmp/lvl.log 2>&1
  a=$(grep -o "application_[0-9_]*" /tmp/lvl.log | head -1); sleep 8
  m=$(yarn logs -applicationId $a -show_application_log_info 2>/dev/null | grep -o "container_[0-9_]*_000002" | head -1)
  echo "map.log.level=$lvl: map container syslog has $(yarn logs -applicationId $a -containerId $m -log_files syslog 2>/dev/null | wc -l) lines"
done
