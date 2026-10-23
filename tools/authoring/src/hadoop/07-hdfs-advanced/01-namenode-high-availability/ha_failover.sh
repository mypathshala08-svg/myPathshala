#!/usr/bin/env bash
# ha_failover.sh: crash the active NameNode while a client keeps writing, and watch HDFS fail over.
# Run from the folder with docker-compose.yaml (project name lab7).
P=lab7
state() { docker exec $P-nn2-1 hdfs haadmin -getAllServiceState 2>/dev/null | awk '/^nn[12]:8020/{printf "%s=%s  ", $1, $2}'; }
echo "$(date +%T) before: $(state)"

# a client on datanode-1 writes one small file every loop, and logs success or failure
docker exec -d $P-datanode-1 bash -c 'for i in $(seq 1 12); do
  start=$(date +%s)
  if echo "order $i" | hdfs dfs -put -f - /orders_$i.txt >/tmp/err_$i 2>&1; then r=ok; else r=FAILED; fi
  echo "$(date +%T) write $i $r  (took $(( $(date +%s) - start )) s)"
done > /tmp/writer.log 2>&1'
sleep 8
echo "$(date +%T) >>> docker kill $P-nn1-1   (the active NameNode crashes)"
docker kill $P-nn1-1 > /dev/null
for t in $(seq 1 30); do
  s=$(docker exec $P-nn2-1 hdfs haadmin -getServiceState nn2 2>/dev/null)
  echo "$(date +%T) nn2 is $s"
  [ "$s" = "active" ] && break
done
until [ "$(docker exec $P-datanode-1 bash -c 'wc -l < /tmp/writer.log')" -ge 12 ]; do sleep 2; done
echo "--- client log (datanode-1)"
docker exec $P-datanode-1 cat /tmp/writer.log
echo "--- ZKFC log on nn2"
docker exec $P-nn2-1 bash -c 'grep -hE "Checking for any old active|Beginning Service Fencing|Fencing successful|Trying to make|Successfully transitioned" /var/log/hadoop/*zkfc*.out | cut -c1-150 | tail -5'
echo "$(date +%T) files written: $(docker exec $P-nn2-1 hdfs dfs -ls / 2>/dev/null | grep -c orders_)"
