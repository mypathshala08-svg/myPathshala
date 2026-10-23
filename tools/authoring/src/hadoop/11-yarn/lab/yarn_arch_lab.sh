# yarn_arch_lab.sh: look at YARN's parts while a job runs (run on your PC, in the mr-lab folder)
echo "== 1. Java processes (daemons) on each machine"
for c in resourcemanager namenode historyserver worker1; do
  echo "$c: $(docker exec lab8-$c-1 jps 2>/dev/null | awk '{print $2}' | grep -v Jps | sort | tr '\n' ' ')"
done
echo "== 2. what the ResourceManager knows about its NodeManagers"
docker exec lab8-resourcemanager-1 yarn node -list -showDetails 2>/dev/null | grep -E "Node-Id|worker|Resource Utilization|Configured Resources|Allocated" | head -12
echo "== 3. cluster metrics (RM REST API)"
docker exec lab8-namenode-1 curl -s http://resourcemanager:8088/ws/v1/cluster/metrics | python3 -c '
import sys, json; m = json.load(sys.stdin)["clusterMetrics"]
for k in ["activeNodes", "totalMB", "totalVirtualCores", "allocatedMB", "appsRunning", "appsCompleted", "containersAllocated"]: print(f"  {k:20} {m[k]}")'
echo "== 4. start a job and look again while it runs"
docker exec -d lab8-namenode-1 bash -c 'cd /tmp/mr9; hdfs dfs -rm -r -f -skipTrash /out/yarn_arch >/dev/null 2>&1; hadoop jar /tmp/mr/mr.jar ItemRevenue /user/hadoop/data/orders_x90.csv /out/yarn_arch > /tmp/yarn_arch.log 2>&1'
sleep 20
echo "-- processes on worker1 now:"
docker exec lab8-worker1-1 jps 2>/dev/null | awk '{print $2}' | grep -v Jps | sort | uniq -c
docker exec lab8-namenode-1 curl -s http://resourcemanager:8088/ws/v1/cluster/metrics | python3 -c '
import sys, json; m = json.load(sys.stdin)["clusterMetrics"]
print("  allocatedMB", m["allocatedMB"], "of", m["totalMB"], "| allocatedVirtualCores", m["allocatedVirtualCores"], "| containersAllocated", m["containersAllocated"], "| appsRunning", m["appsRunning"])'
app=$(docker exec lab8-resourcemanager-1 yarn application -list 2>/dev/null | grep -o "application_[0-9_]*" | head -1)
att=$(docker exec lab8-resourcemanager-1 yarn applicationattempt -list $app 2>/dev/null | grep -o "appattempt_[0-9_]*" | head -1)
echo "-- containers of $att:"
docker exec lab8-resourcemanager-1 yarn container -list $att 2>/dev/null | grep "^container_" | awk -F'\t' '{print "  " $1, $4, $5}' | tr -s ' ' | head -8
echo "-- per-node view (RM REST /ws/v1/cluster/nodes)"
docker exec lab8-namenode-1 curl -s http://resourcemanager:8088/ws/v1/cluster/nodes | python3 -c '
import sys, json
for n in json.load(sys.stdin)["nodes"]["node"]:
    print("  %-8s used %4d MB / %d MB, %d vcores used, %d containers" % (n["nodeHostName"], n["usedMemoryMB"], n["usedMemoryMB"] + n["availMemoryMB"], n["usedVirtualCores"], n["numContainers"]))'
docker exec lab8-namenode-1 bash -c 'while ! grep -qE "completed|failed" /tmp/yarn_arch.log; do sleep 2; done; grep -E "completed|Launched map" /tmp/yarn_arch.log | sed -E "s/^[0-9-]+ [0-9:]+ INFO  //"'
