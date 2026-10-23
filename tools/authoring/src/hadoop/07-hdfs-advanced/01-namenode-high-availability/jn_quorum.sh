#!/usr/bin/env bash
# jn_quorum.sh: the active NameNode needs a majority (2 of 3) of JournalNodes to write edits.
P=lab7
put() { if echo "x" | timeout 90 docker exec -i $P-datanode-1 hdfs dfs -put -f - /q_$1.txt > /dev/null 2>&1; then echo "$(date +%T) write $1: ok"; else echo "$(date +%T) write $1: FAILED (no answer)"; fi; }
state() { docker exec $P-datanode-1 hdfs haadmin -getAllServiceState 2>/dev/null | awk '/^nn[12]:8020/{printf "%s=%s  ", $1, $2}'; }
echo "$(date +%T) $(state)"
put 1
echo "$(date +%T) >>> stop jn3 (2 of 3 JournalNodes left)"; docker stop $P-jn3-1 > /dev/null
put 2
echo "$(date +%T) >>> stop jn2 (1 of 3 left: no majority)"; docker stop $P-jn2-1 > /dev/null
put 3
sleep 10
echo "$(date +%T) $(state)"
for n in nn1 nn2; do docker logs $P-$n-1 2>&1 | grep -E "Timed out waiting|SHUTDOWN_MSG: Shutting" | tail -2 | cut -c1-120 | sed "s/^/$n: /"; done
