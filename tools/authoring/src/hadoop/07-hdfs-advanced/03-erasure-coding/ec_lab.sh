#!/usr/bin/env bash
# ec_lab.sh: store the same file with 3x replication and with RS-3-2 erasure coding, then lose DataNodes.
P=lab5
NN="docker exec $P-namenode-1"
run() { echo "\$ $1"; $NN bash -c "$1" 2>&1 | grep -v -E "^\s*$|WARN|INFO"; echo; }
run "hdfs ec -enablePolicy -policy RS-3-2-1024k"
run "hdfs ec -verifyClusterSetup -policy RS-6-3-1024k"
run "hdfs ec -verifyClusterSetup -policy RS-3-2-1024k"
run "hdfs dfs -rm -r -f -skipTrash /ec /rep > /dev/null; hdfs dfs -mkdir -p /ec /rep && hdfs ec -setPolicy -path /ec -policy RS-3-2-1024k"
run "hdfs ec -getPolicy -path /ec ; hdfs ec -getPolicy -path /rep"
run "hdfs dfs -cp /user/hadoop/data/orders_x30.csv /rep/ && hdfs dfs -cp /user/hadoop/data/orders_x30.csv /ec/"
run "echo 'one tiny order' | hdfs dfs -put - /ec/tiny.txt; echo 'one tiny order' | hdfs dfs -put - /rep/tiny.txt"
run "hdfs dfs -du /rep /ec"
run "hdfs fsck /ec/orders_x30.csv -files -blocks -locations | grep -E 'bytes|blk_' | cut -c1-210"
run "hdfs dfs -get -f /ec/orders_x30.csv /tmp/ec.csv > /dev/null 2>&1; hdfs dfs -get -f /rep/orders_x30.csv /tmp/rep.csv > /dev/null 2>&1; md5sum /tmp/ec.csv /tmp/rep.csv"
echo ">>> docker stop $P-datanode-4 $P-datanode-5   (2 of 5 DataNodes gone)"; docker stop $P-datanode-4 $P-datanode-5 > /dev/null; echo
run "s=\$(date +%s); hdfs dfs -get -f /ec/orders_x30.csv /tmp/ec2.csv > /dev/null 2>&1; echo read took \$(( \$(date +%s) - s )) s; md5sum /tmp/ec2.csv"
echo ">>> docker stop $P-datanode-3   (3 of 5 gone: more than the 2 parity blocks)"; docker stop $P-datanode-3 > /dev/null; echo
run "hdfs dfs -get -f /ec/orders_x30.csv /tmp/ec3.csv > /tmp/err 2>&1; echo exit=\$?; grep -m1 -oE '[0-9]+ missing blocks, the stripe is: AlignedStripe[^;]*' /tmp/err; grep -m1 -oE 'get: .*' /tmp/err"
run "s=\$(date +%s); hdfs dfs -get -f /rep/orders_x30.csv /tmp/rep3.csv > /dev/null 2>&1; echo read took \$(( \$(date +%s) - s )) s; md5sum /tmp/rep3.csv"
docker start $P-datanode-3 $P-datanode-4 $P-datanode-5 > /dev/null
