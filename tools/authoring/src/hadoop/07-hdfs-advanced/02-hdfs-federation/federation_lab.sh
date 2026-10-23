#!/usr/bin/env bash
# federation_lab.sh: two NameNodes (canteen, hostel) share the same 3 DataNodes.
P=lab72
C="docker exec $P-datanode-1"
V='HADOOP_CONF_DIR=/opt/client-conf'          # client config with the ViewFS mount table
run() { echo "\$ $1"; $C bash -c "$1" 2>&1 | grep -v -E "WARN|^\s*$"; echo; }
$C bash -c 'cp /opt/hadoop/etc/hadoop/hdfs-site.xml /opt/hadoop/etc/hadoop/log4j.properties /opt/client-conf/'
run "hdfs dfs -mkdir -p hdfs://nn-canteen:8020/canteen hdfs://nn-hostel:8020/hostel hdfs://nn-hostel:8020/tmp"
run "seq 1 200000 | sed 's/^/order,/' > /tmp/orders.csv; seq 1 50000 | sed 's/^/room,/' > /tmp/rooms.csv"
run "$V hdfs dfs -put -f /tmp/orders.csv /canteen/ && $V hdfs dfs -put -f /tmp/rooms.csv /hostel/"
run "$V hdfs dfs -ls /"
run "$V hdfs dfs -ls /canteen /hostel"
run "hdfs dfs -ls -R hdfs://nn-canteen:8020/ ; echo ---; hdfs dfs -ls -R hdfs://nn-hostel:8020/"
for n in canteen hostel; do echo "nn-$n: $(docker exec $P-nn-$n-1 grep -E 'clusterID|blockpoolID' /tmp/hadoop-hadoop/dfs/name/current/VERSION | tr '\n' ' ')"; done; echo
run "ls /tmp/hadoop-hadoop/dfs/data/current/ ; du -sh /tmp/hadoop-hadoop/dfs/data/current/BP-*"
run "for nn in nn-canteen nn-hostel; do echo \$nn: \$(hdfs dfsadmin -fs hdfs://\$nn:8020 -report 2>/dev/null | grep -m1 'Live datanodes'); done"
run "$V hdfs dfs -mv /canteen/orders.csv /hostel/orders.csv"
echo ">>> docker stop $P-nn-canteen-1"; docker stop $P-nn-canteen-1 > /dev/null; echo
run "$V hdfs dfs -ls /hostel"
run "$V timeout 40 hdfs dfs -ls /canteen 2>&1 | grep -m1 -- -ls:"
docker start $P-nn-canteen-1 > /dev/null
