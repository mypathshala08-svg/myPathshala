# kill_task.sh (run on your PC, in the lab folder): kill a running map task and watch Hadoop retry it
docker exec lab8-namenode-1 bash -c 'cd /tmp/mr; for i in $(seq 20); do cat feedback.txt; done > feedback_x20.txt
  hdfs dfs -D dfs.blocksize=33554432 -put -f feedback_x20.txt /user/hadoop/data/ 2>/dev/null
  hdfs dfs -rm -r -f -skipTrash /out/wc_big > /dev/null 2>&1'
docker exec -d lab8-namenode-1 bash -c 'hadoop jar /tmp/mr/wc.jar WordCount /user/hadoop/data/feedback_x20.txt /out/wc_big > /tmp/wc_big.log 2>&1'
until docker exec lab8-worker2-1 pgrep -f "java.*YarnChild.*_m_" > /dev/null; do sleep 1; done
sleep 6                                              # let the map task get going
echo "map tasks running on worker2:"
docker exec lab8-worker2-1 pgrep -af "java.*YarnChild.*_m_" | grep -o "attempt_[0-9]*_[0-9]*_m_[0-9]*_[0-9]*" | sort -u
victim=$(docker exec lab8-worker2-1 pgrep -f "java.*YarnChild.*_m_" | head -1)
docker exec lab8-worker2-1 kill -9 $victim && echo "killed JVM $victim on worker2 at $(date +%T)"
until docker exec lab8-namenode-1 grep -qE "completed successfully|failed with state" /tmp/wc_big.log; do sleep 2; done
docker exec lab8-namenode-1 bash -c 'grep -E "number of splits|map [0-9]+%|Task Id|Error:|exit code|completed|Failed map tasks|Launched map tasks|Data-local|Rack-local" /tmp/wc_big.log | sed -E "s/^[0-9-]+ [0-9:]+ INFO  //" | cut -c1-150
  hdfs dfs -cat /out/wc_big/part-r-00000 | grep -wE "chai|was"
  echo "-- every attempt of this job"
  bash /tmp/mr/attempts.sh $(grep -o "job_[0-9_]*" /tmp/wc_big.log | head -1)'
