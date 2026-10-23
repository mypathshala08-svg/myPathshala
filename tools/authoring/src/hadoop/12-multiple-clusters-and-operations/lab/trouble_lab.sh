# trouble_lab.sh: four common incidents reproduced on the Module 8 lab, with the exact message each one gives.
# Run on your PC.
NN="docker exec lab8-namenode-1"
clean() { grep -vE "^\s+at |INFO|^$|WARN.*retry|Retrying" | cut -c1-170; }
echo "== A. 'Connection refused': wrong port in the URI (8020 is right, 9000 was the Hadoop 1/2 habit)"
$NN hdfs dfs -ls hdfs://namenode:9000/ 2>&1 | grep -m1 -oE "Call From .* failed on connection exception: java.net.ConnectException: Connection refused"
echo "== B. 'Name node is in safe mode': writes fail, reads still work"
$NN hdfs dfsadmin -safemode enter 2>/dev/null
$NN hdfs dfs -mkdir /incident_b 2>&1 | grep -m1 -oE "Cannot create directory /incident_b. Name node is in safe mode."
echo "   read still works: $($NN hdfs dfs -cat /user/hadoop/data/menu.csv 2>/dev/null | head -1)"
$NN hdfs dfsadmin -safemode leave 2>/dev/null
echo "== C. a file with ONE replica, and its DataNode goes down"
$NN bash -c 'hdfs dfs -D dfs.replication=1 -put -f /tmp/mr/menu.csv /incident_c.csv 2>/dev/null; hdfs fsck /incident_c.csv -files -blocks -locations 2>/dev/null | grep -oE "DatanodeInfoWithStorage\[[0-9.]+"'
ip=$($NN hdfs fsck /incident_c.csv -files -blocks -locations 2>/dev/null | grep -oE "DatanodeInfoWithStorage\[[0-9.]+" | grep -oE "[0-9.]+$" | head -1)
for w in worker1 worker2 worker3; do
  if docker exec lab8-$w-1 hostname -i | grep -q "$ip"; then victim=$w; fi
done
echo "   the only replica is on $victim; stopping its DataNode"
docker exec lab8-$victim-1 hdfs --daemon stop datanode
$NN bash -c 'start=$(date +%s); hdfs dfs -cat /incident_c.csv 2>&1 | grep -m2 -oE "Could not obtain block: [^ ]+|BlockMissingException|No live nodes contain current block"; echo "   the read gave up after $(( $(date +%s) - start )) s"'
docker exec lab8-$victim-1 hdfs --daemon start datanode; sleep 15
echo "   DataNode back: $($NN hdfs dfs -cat /incident_c.csv 2>/dev/null | head -1)"
$NN hdfs dfs -rm -skipTrash /incident_c.csv > /dev/null 2>&1
echo "== D. a job stuck in ACCEPTED"
T=/opt/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-client-jobclient-3.5.0-tests.jar
for n in 1 2; do $NN bash -c "export HADOOP_CLASSPATH=$T; yarn org.apache.hadoop.mapreduce.SleepJob -libjars $T -m 30 -r 1 -mt 30000 -rt 1000 > /tmp/acc$n.log 2>&1" & sleep 3; done
sleep 25
docker exec lab8-resourcemanager-1 yarn application -list 2>/dev/null | grep -E "RUNNING|ACCEPTED" | awk -F'\t' '{print "  ", $1, $6}' | tr -s ' '
app=$(docker exec lab8-resourcemanager-1 yarn application -list -appStates ACCEPTED 2>/dev/null | grep -o "application_[0-9_]*" | head -1)
docker exec lab8-resourcemanager-1 yarn application -status $app 2>/dev/null | grep -A2 "Diagnostics" | sed 's/^\s*/   /' | cut -c1-200
echo "-- the queue's limit on ApplicationMasters:"
docker exec lab8-namenode-1 curl -s http://resourcemanager:8088/ws/v1/cluster/scheduler | python3 -c '
import sys, json
q = json.load(sys.stdin)["scheduler"]["schedulerInfo"]["queues"]["queue"][0]
r = q["resources"]["resourceUsagesByPartition"][0]
print("   queue", q["queueName"], "| AM limit", r["amLimit"]["memory"], "MB | AM used", r["amUsed"]["memory"], "MB | maxAMPercent", q.get("maxAMPercent", q.get("maximumAMResourcePercent")))' 2>&1 | head -2
for a in $(docker exec lab8-resourcemanager-1 yarn application -list 2>/dev/null | grep -o "application_[0-9_]*"); do docker exec lab8-resourcemanager-1 yarn application -kill $a > /dev/null 2>&1; done
wait
