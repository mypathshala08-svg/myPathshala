# distcp_lab.sh: copy a production folder to a second (DR) cluster, keep it in sync, then fail over.
# PROD = the Module 8 cluster (hdfs://namenode). DR = the federation cluster of Lesson 7.2 (hdfs://nn-canteen:8020).
# The lab8 workers are joined to the DR cluster's Docker network (join_clusters.sh). Run inside lab8-worker1-1.
DR=hdfs://nn-canteen:8020
P=/prod/canteen
D=$DR/dr/canteen
run() { local name=$1; shift; local s=$(date +%s%N)
  hadoop distcp "$@" > /tmp/$name.log 2>&1; echo "   exit $?, took $(( ($(date +%s%N) - s) / 1000 / 1000 )) ms"
  grep -E "Bytes Copied|Bytes Skipped|Files Copied|Files Skipped|DIR_COPY|Launched map tasks|Deleted|Files Deleted|Bytes Expected" /tmp/$name.log | sed 's/^\s*/   /' | sort -u; }
hdfs dfs -rm -r -f -skipTrash $P $DR/dr > /dev/null 2>&1
hdfs dfs -mkdir -p $P $DR/dr
hdfs dfs -cp /user/hadoop/data/{canteen_orders.csv,student_orders.csv,menu.csv,feedback.txt,orders_x30.csv} $P/
echo "== 0. what we protect (prod)"
hdfs dfs -count -h $P
echo "== 1. first full copy to the DR cluster (one map per file here)"
run d1 $P $DR/dr/
hdfs dfs -count -h $D
echo "== 2. a day later: one new file, one changed file, one deleted file"
hdfs dfs -cat $P/canteen_orders.csv | head -5001 > /tmp/day31.csv; hdfs dfs -put -f /tmp/day31.csv $P/orders_day31.csv
hdfs dfs -cat $P/menu.csv | sed 's/^chai,drink,15/chai,drink,18/' > /tmp/menu.csv; hdfs dfs -put -f /tmp/menu.csv $P/menu.csv
hdfs dfs -rm -skipTrash $P/feedback.txt > /dev/null
echo "-- plain distcp again (no -update): the existing files are NOT replaced"
run d2a $P $DR/dr/
hdfs dfs -ls $D | awk '{print "   ", $5, $8}' | sed "s#$DR##"
echo "-- distcp -update: copy only what is new or different"
run d2 -update $P $D
echo "-- distcp -update -delete: also remove what prod deleted"
run d3 -update -delete $P $D
hdfs dfs -ls $D | awk '{print "   ", $5, $8}' | sed "s#$DR##"
echo "-- is the price change there?"; hdfs dfs -cat $D/menu.csv | head -1
echo "== 3. snapshot-based sync: only the difference between two snapshots"
hdfs dfsadmin -allowSnapshot $P > /dev/null; hdfs dfsadmin -fs $DR -allowSnapshot /dr/canteen > /dev/null
hdfs dfs -createSnapshot $P s1 > /dev/null; hdfs dfs -createSnapshot $D s1 > /dev/null
hdfs dfs -mv $P/orders_day31.csv $P/orders_2026-10-31.csv
hdfs dfs -cat $P/canteen_orders.csv | head -2001 | tail -2000 > /tmp/day32.csv; hdfs dfs -put /tmp/day32.csv $P/orders_2026-11-01.csv
hdfs dfs -createSnapshot $P s2 > /dev/null
hdfs snapshotDiff $P s1 s2 2>/dev/null | sed 's/^/   /'
run d4 -update -diff s1 s2 $P $D
hdfs dfs -ls $D | awk '{print "   ", $5, $8}' | sed "s#$DR##"
echo "== 4. throttle: -bandwidth 1 (MB/s per map) on the 19 MB student_orders.csv"
run d5 -bandwidth 1 $P/student_orders.csv $DR/dr/throttled.csv
echo "== 5. disaster drill: prod is down, run the report on the DR cluster"
hdfs dfs -rm -r -f -skipTrash $DR/dr/report > /dev/null 2>&1
hadoop jar /tmp/mr.jar ItemRevenue $D/canteen_orders.csv $DR/dr/report > /tmp/dr_job.log 2>&1
grep -oE "completed successfully|failed with state [A-Z]+" /tmp/dr_job.log
hdfs dfs -cat $DR/dr/report/part-r-00000 | head -3
echo "-- recovery point: what DR has vs prod right now"
hdfs dfs -put -f /tmp/day32.csv $P/orders_2026-11-02.csv     # written after the last sync
echo "   prod files: $(hdfs dfs -ls $P | grep -c '^-')   DR files: $(hdfs dfs -ls $D | grep -c '^-')   missing on DR: $(diff <(hdfs dfs -ls $P | grep '^-' | awk -F/ '{print $NF}') <(hdfs dfs -ls $D | grep '^-' | awk -F/ '{print $NF}') | grep '^<' | cut -c3-)"
