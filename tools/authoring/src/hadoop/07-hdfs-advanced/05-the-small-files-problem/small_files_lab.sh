#!/usr/bin/env bash
# small_files_lab.sh: the same 10 MB of orders as 10,000 tiny files vs 1 file, and what the NameNode pays.
NN="docker exec lab5-namenode-1"
jmx() { sleep 6; $NN bash -c "curl -s 'http://localhost:9870/jmx?qry=Hadoop:service=NameNode,name=FSNamesystem'" | python3 -c "import sys,json; b=json.load(sys.stdin)['beans'][0]; print('FilesTotal', b['FilesTotal'], ' BlocksTotal', b['BlocksTotal'])"; }
run() { echo "\$ $1"; $NN bash -c "$1" 2>&1 | grep -v -E "^\s*$|WARN|INFO"; echo; }
run "hdfs dfs -rm -r -f -skipTrash /small /big /archives > /dev/null; rm -rf /tmp/small && mkdir -p /tmp/small && cd /tmp/small && seq 1 10000 | while read i; do printf 'order_id,item,amount\n%d,chai,20\n' \$i > o_\$i.csv; done; ls | wc -l; du -sh /tmp/small; cat /tmp/small/*.csv > /tmp/big.csv; ls -l /tmp/big.csv | awk '{print \$5, \"bytes in big.csv\"}'"
echo "NameNode before : $(jmx)"; echo
run "hdfs dfs -mkdir -p /small /big; s=\$(date +%s%N); hdfs dfs -put /tmp/small/*.csv /small/; echo put 10000 files: \$(( (\$(date +%s%N)-s)/1000000 )) ms"
echo "NameNode after small files: $(jmx)"; echo
run "s=\$(date +%s%N); hdfs dfs -put /tmp/big.csv /big/; echo put 1 file: \$(( (\$(date +%s%N)-s)/1000000 )) ms"
echo "NameNode after big file   : $(jmx)"; echo
run "hdfs dfs -count -v /small /big"
run "hdfs dfs -du -s /small /big"
run "s=\$(date +%s%N); hdfs dfs -cat '/small/*.csv' | wc -l; echo read 10000 files: \$(( (\$(date +%s%N)-s)/1000000 )) ms"
run "s=\$(date +%s%N); hdfs dfs -cat /big/big.csv | wc -l; echo read 1 file: \$(( (\$(date +%s%N)-s)/1000000 )) ms"
run "hdfs fsck /small | grep -E 'Total files|Total blocks|Average block size'; hdfs fsck /big | grep -E 'Total files|Total blocks|Average block size'"
echo "=== FIX 1: pack the small files into a Hadoop Archive (HAR)"
run "s=\$(date +%s); hadoop archive -archiveName orders.har -p /small /archives > /dev/null 2>&1; echo archive job took \$(( \$(date +%s)-s )) s; hdfs dfs -ls /archives/orders.har"
run "hdfs dfs -count -v har:///archives/orders.har; hdfs dfs -cat har:///archives/orders.har/o_42.csv"
run "hdfs dfs -rm -r -skipTrash /small > /dev/null && echo removed /small"
echo "NameNode after HAR, without /small: $(jmx)"
