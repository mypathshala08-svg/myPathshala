# partitioner_lab.sh: who decides which reducer gets which key? Default hash vs a custom partitioner.
cd /tmp/mr9
D=/user/hadoop/data/student_orders.csv
for mode in hash counter; do
  hdfs dfs -rm -r -f -skipTrash /out/part_$mode > /dev/null 2>&1
  hadoop jar mr9.jar ItemPartition -D part.mode=$mode $D /out/part_$mode > /tmp/part_$mode.log 2>&1
  echo "== part.mode=$mode, 4 reducers"
  for f in $(hdfs dfs -ls /out/part_$mode | grep part-r | awk '{print $8}'); do
    echo "$(basename $f): $(hdfs dfs -cat $f | awk -F'\t' '{printf "%s(%s) ", $1, $2}')"
  done
  sleep 3
  bash reduce_tasks.sh $(grep -o "job_[0-9_]*" /tmp/part_$mode.log | head -1)
done
echo "== a partitioner that returns 8 for 4 reducers"
hdfs dfs -rm -r -f -skipTrash /out/part_bad > /dev/null 2>&1
hadoop jar mr9.jar ItemPartition -D part.mode=bad $D /out/part_bad 2>&1 | grep -E "Illegal partition|Task Id|failed with state|Job .* failed|Failed map tasks" | sed -E 's/^[0-9-]+ [0-9:]+ INFO  //' | cut -c1-160 | sort -u | head -6
