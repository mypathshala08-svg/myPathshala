# reducer_lab.sh: number of reducers = number of output files; which key goes where; the object-reuse trap
cd /tmp/mr
D=/user/hadoop/data/canteen_orders.csv
for r in 3 10; do
  hdfs dfs -rm -r -f -skipTrash /out/red_$r > /dev/null 2>&1
  hadoop jar mr.jar ItemRevenue -D mapreduce.job.reduces=$r $D /out/red_$r 2>&1 | grep -E "Launched reduce tasks|Reduce input groups|Reduce output records"
  echo "== $r reducers: output files"
  for f in $(hdfs dfs -ls /out/red_$r | grep part-r | awk '{print $8}'); do
    echo "$(basename $f) ($(hdfs dfs -stat %b $f) bytes): $(hdfs dfs -cat $f | cut -f1 | tr '\n' ' ')"
  done
done
echo "== 0 reducers (map-only): mapper output written directly, unsorted"
hdfs dfs -rm -r -f -skipTrash /out/red_0 > /dev/null 2>&1
hadoop jar mr.jar ItemRevenue -D mapreduce.job.reduces=0 $D /out/red_0 2>&1 | grep -E "Launched (map|reduce)"
hdfs dfs -ls /out/red_0 | grep part | awk '{print $5, $8}'
hdfs dfs -cat /out/red_0/part-m-00000 2>/dev/null | head -3
echo "== first 3 order ids per item, copying each value (correct)"
hdfs dfs -rm -r -f -skipTrash /out/sample_ok /out/sample_bug > /dev/null 2>&1
hadoop jar mr.jar SampleOrders $D /out/sample_ok > /dev/null 2>&1
hdfs dfs -cat /out/sample_ok/part-r-00000
echo "== the same job WITHOUT copying (-D sample.copy=false)"
hadoop jar mr.jar SampleOrders -D sample.copy=false $D /out/sample_bug > /dev/null 2>&1
hdfs dfs -cat /out/sample_bug/part-r-00000
