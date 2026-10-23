#!/usr/bin/env bash
# restore.sh: start everything again (JournalNodes first, then NameNodes)
docker start lab7-jn1-1 lab7-jn2-1 lab7-jn3-1 > /dev/null; sleep 5
docker start lab7-nn1-1 lab7-nn2-1 > /dev/null; sleep 45
docker exec lab7-datanode-1 hdfs haadmin -getAllServiceState 2>/dev/null
