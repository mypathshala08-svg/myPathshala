# secondary_sort_lab.sh: values in time order inside each student's group, with and without a grouping comparator
cd /tmp/mr9
D=/user/hadoop/data/student_orders.csv
for g in true false; do
  hdfs dfs -rm -r -f -skipTrash /out/ss_$g > /dev/null 2>&1
  start=$(date +%s%N)
  hadoop jar mr9.jar FirstLastOrder -D ss.grouping=$g $D /out/ss_$g > /tmp/ss_$g.log 2>&1
  echo "== grouping comparator: $g   $(( ($(date +%s%N) - start) / 1000000 )) ms"
  grep -E "Reduce input records|Reduce input groups|Reduce output records" /tmp/ss_$g.log | sed 's/^\s*/  /'
  hdfs dfs -cat /out/ss_$g/part-r-00000 2>/dev/null | head -3 | cut -c1-200
done
echo "== a light user and the heaviest user"
hdfs dfs -cat /out/ss_true/part-r-00000 | grep -E "^S1413|^S0001" | cut -c1-200
echo "== the reducer's own check (task log)"
app=$(grep -o "application_[0-9_]*" /tmp/ss_true.log | head -1); sleep 5
yarn logs -applicationId $app -log_files stderr 2>/dev/null | grep "time order"
echo "== check in plain Linux: S1413's first and last order"
grep ",S1413," student_orders.csv | cut -d, -f3,4 | sort | sed -n '1p;$p'
