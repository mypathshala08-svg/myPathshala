#!/bin/bash
# Start a NameNode plus its ZKFailoverController in one container.
# nn1 formats the namespace; nn2 copies it from nn1 (bootstrapStandby).
NAME=/tmp/hadoop-hadoop/dfs/name
if [ ! -d $NAME/current ]; then
  if [ "$(hostname)" = "nn1" ]; then
    hdfs namenode -format -nonInteractive -clusterId canteen-cluster
    hdfs zkfc -formatZK -nonInteractive
  else
    until hdfs namenode -bootstrapStandby -nonInteractive; do sleep 5; done
  fi
fi
hdfs --daemon start zkfc
exec hdfs namenode
