#!/bin/bash
# Format this NameNode once with the SHARED cluster ID, then run it.
NAME=/tmp/hadoop-hadoop/dfs/name
[ -d $NAME/current ] || hdfs namenode -format -nonInteractive -clusterId campus-cluster
exec hdfs namenode
