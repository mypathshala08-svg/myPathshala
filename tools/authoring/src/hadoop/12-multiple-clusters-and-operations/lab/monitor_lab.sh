# monitor_lab.sh: break things on purpose and watch monitor.py notice. Run on your PC.
M="docker exec lab8-worker1-1 python3 /tmp/monitor.py"
docker cp monitor.py lab8-worker1-1:/tmp/monitor.py
echo "== 0. healthy fleet"; $M 1
echo "== 1. a DataNode process dies on prod's worker2"
docker exec lab8-worker2-1 hdfs --daemon stop datanode; s=$(date +%s)
# a DataNode is "stale" after 30 s without a heartbeat, but the NameNode recounts stale nodes only
# on its heartbeat check (every 5 min by default), so the metric can lag: wait until it shows
until $M 1 | grep -q "prod.*stale=[1-9]"; do sleep 10; done
echo "   (the alert appeared $(( $(date +%s) - s )) s after the DataNode stopped)"; $M 1
echo "== 2. someone sets replication 4 on a file (the cluster has only 3 DataNodes, 2 alive)"
docker exec lab8-namenode-1 hdfs dfs -setrep 4 /user/hadoop/data/menu.csv 2>/dev/null | grep -v INFO
sleep 5; $M 1
echo "== 3. an admin puts the DR NameNode into safe mode"
docker exec lab72-nn-canteen-1 hdfs dfsadmin -safemode enter 2>/dev/null
$M 1
echo "== 4. a huge job fills prod's YARN and a second job has to wait"
T=/opt/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-client-jobclient-3.5.0-tests.jar
for n in 1 2; do docker exec -d lab8-namenode-1 bash -c "export HADOOP_CLASSPATH=$T; yarn org.apache.hadoop.mapreduce.SleepJob -libjars $T -m 30 -r 1 -mt 30000 -rt 1000 > /tmp/mon$n.log 2>&1"; sleep 2; done
sleep 30; $M 1
echo "== 5. fix everything and check again"
for n in 1 2; do app=$(docker exec lab8-namenode-1 grep -o "application_[0-9_]*" /tmp/mon$n.log | head -1); docker exec lab8-resourcemanager-1 yarn application -kill $app > /dev/null 2>&1; done
docker exec lab72-nn-canteen-1 hdfs dfsadmin -safemode leave 2>/dev/null
docker exec lab8-namenode-1 hdfs dfs -setrep 3 /user/hadoop/data/menu.csv > /dev/null 2>&1
docker exec lab8-worker2-1 hdfs --daemon start datanode; s=$(date +%s)
until $M 1 | grep -q "prod.*stale=0"; do sleep 10; done
echo "   (stale cleared $(( $(date +%s) - s )) s after the restart)"; $M 1
