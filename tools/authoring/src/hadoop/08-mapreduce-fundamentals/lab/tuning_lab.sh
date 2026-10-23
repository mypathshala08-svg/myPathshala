# tuning_lab.sh: how YARN sizes containers, how many fit, and what happens when the heap is too small
# Run on your PC in the mr-lab folder (it switches the ResourceManager's calculator in part 3).
T=/opt/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-client-jobclient-3.5.0-tests.jar
sleepjob() {  # extra args...
  docker exec -d lab8-namenode-1 bash -c "export HADOOP_CLASSPATH=$T; yarn org.apache.hadoop.mapreduce.SleepJob -libjars $T $* -r 1 -rt 1000 > /tmp/tune.log 2>&1"
}
metrics() { docker exec lab8-namenode-1 curl -s http://resourcemanager:8088/ws/v1/cluster/metrics | python3 -c '
import sys, json; m = json.load(sys.stdin)["clusterMetrics"]
print("   running containers %2d | memory %4d of %d MB | vcores %d of %d" % (m["containersAllocated"], m["allocatedMB"], m["totalMB"], m["allocatedVirtualCores"], m["totalVirtualCores"]))'; }
wait_job() { until docker exec lab8-namenode-1 grep -qE "completed successfully|failed with state" /tmp/tune.log 2>/dev/null; do sleep 3; done; }
bash rm.sh default > /dev/null 2>&1
echo "== 1. a request is rounded UP to a multiple of the minimum allocation (256 MB here)"
for mb in 300 384 600 1100; do
  sleepjob -D mapreduce.map.memory.mb=$mb -m 1 -mt 20000
  sleep 14
  app=$(docker exec lab8-namenode-1 grep -o "application_[0-9_]*" /tmp/tune.log | head -1)
  docker exec lab8-namenode-1 curl -s http://resourcemanager:8088/ws/v1/cluster/apps/$app | python3 -c '
import sys, json; a = json.load(sys.stdin)["app"]
print("map asks %4s MB -> app holds %4d MB = AM 512 + map %d MB" % (sys.argv[1], a["allocatedMB"], a["allocatedMB"] - 512))' $mb
  docker exec lab8-resourcemanager-1 yarn application -kill $app > /dev/null 2>&1; sleep 3
done
echo "== 2. how many maps run at once: 384 MB maps vs 1024 MB maps (24 maps of 30 s each)"
for mb in 384 1024; do
  sleepjob -D mapreduce.map.memory.mb=$mb -m 24 -mt 30000
  sleep 25; echo " maps of $mb MB:"; metrics
  app=$(docker exec lab8-namenode-1 grep -o "application_[0-9_]*" /tmp/tune.log | head -1)
  docker exec lab8-resourcemanager-1 yarn application -kill $app > /dev/null 2>&1; sleep 3
done
echo "== 3. CPU: the default calculator ignores vcores; DominantResourceCalculator counts them"
for calc in default drf; do
  bash rm.sh $calc > /dev/null 2>&1
  sleepjob -D mapreduce.map.memory.mb=384 -m 24 -mt 30000
  sleep 25; echo " calculator $calc:"; metrics
  app=$(docker exec lab8-namenode-1 grep -o "application_[0-9_]*" /tmp/tune.log | head -1)
  docker exec lab8-resourcemanager-1 yarn application -kill $app > /dev/null 2>&1; sleep 3
done
bash rm.sh default > /dev/null 2>&1
echo "== 4. a map that keeps every line in memory: heap 64 MB vs 300 MB (student_orders.csv, 3 maps)"
for heap in 64 300; do
  docker exec lab8-namenode-1 bash -c "cd /tmp/mr11; hdfs dfs -rm -r -f -skipTrash /out/hog$heap > /dev/null 2>&1
    hadoop jar mr11.jar HeapHog -D mapreduce.map.java.opts=-Xmx${heap}m /user/hadoop/data/student_orders.csv /out/hog$heap > /tmp/hog.log 2>&1
    echo \" -Xmx${heap}m: \$(grep -oE 'completed successfully|failed with state [A-Z]+' /tmp/hog.log)\"
    grep -oE 'Error: Java heap space|OutOfMemoryError: [A-Za-z ]+' /tmp/hog.log | sort | uniq -c | head -2
    grep -E 'Failed map tasks' /tmp/hog.log | sed 's/^\s*/   /'
    hdfs dfs -cat /out/hog$heap/part-m-* 2>/dev/null | sed 's/^/   /'"
done
