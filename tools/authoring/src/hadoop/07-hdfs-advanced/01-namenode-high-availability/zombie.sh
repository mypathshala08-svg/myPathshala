#!/usr/bin/env bash
# zombie.sh: freeze the active NameNode (it is alive but silent), let the other take over,
# then wake the old one up and watch the JournalNodes refuse its writes.
P=lab7
state() { docker exec $P-nn2-1 hdfs haadmin -getAllServiceState 2>/dev/null | awk '/^nn[12]:8020/{printf "%s=%s  ", $1, $2}'; }
epoch() { for j in 1 2 3; do printf "jn$j=%s " "$(docker exec $P-jn$j-1 cat /tmp/hadoop-hadoop/dfs/journal/canteen/current/last-promised-epoch)"; done; }
echo "$(date +%T) before : $(state)| epochs: $(epoch)"
echo "$(date +%T) >>> docker pause $P-nn1-1   (active NameNode frozen, e.g. a 60 s GC pause)"
docker pause $P-nn1-1 > /dev/null
sleep 25
echo "$(date +%T) during : nn2=$(docker exec $P-nn2-1 hdfs haadmin -getServiceState nn2 2>/dev/null) | epochs: $(epoch)"
echo "order after takeover" | docker exec -i $P-datanode-1 hdfs dfs -put -f - /after_takeover.txt 2>/dev/null && echo "$(date +%T) client write to the new active: ok"
echo "$(date +%T) >>> docker unpause $P-nn1-1   (the old active wakes up, still thinking it is active)"
docker unpause $P-nn1-1 > /dev/null
sleep 20
echo "--- old active nn1, last log lines"
docker logs $P-nn1-1 2>&1 | grep -E "epoch|IPC's epoch|FATAL|Error: flush|shutting down|SHUTDOWN_MSG|Transitioning to standby|standby" | cut -c1-190 | tail -6
echo "$(date +%T) after  : $(state)"
