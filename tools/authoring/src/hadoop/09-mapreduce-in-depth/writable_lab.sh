# writable_lab.sh: a custom key and value vs the same job with Text; then forget the no-arg constructor
cd /tmp/mr9
D=/user/hadoop/data/student_orders.csv
for job in StudentDay StudentDayText StudentDayCompact; do
  hdfs dfs -rm -r -f -skipTrash /out/$job > /dev/null 2>&1
  start=$(date +%s%N)
  hadoop jar mr9.jar $job $D /out/$job > /tmp/$job.log 2>&1
  echo "== $job   $(( ($(date +%s%N) - start) / 1000000 )) ms"
  grep -E "Map output records|Map output bytes|Map output materialized bytes|Combine output records|Reduce output records|CPU time spent" /tmp/$job.log | sed 's/^\s*/  /'
done
echo "-- output (custom Writable), first lines and student S0001"
hdfs dfs -cat /out/StudentDay/part-r-00000 2>/dev/null | head -3
hdfs dfs -cat /out/StudentDay/part-r-00000 | grep -P "^S0001\t" 2>/dev/null | head -3
echo "-- the Text and Compact versions agree?"
diff <(hdfs dfs -cat /out/StudentDay/part-r-00000) <(hdfs dfs -cat /out/StudentDayCompact/part-r-00000) > /dev/null && echo "compact: same rows" || echo "compact: rows differ"
diff <(hdfs dfs -cat /out/StudentDay/part-r-00000 | tr '\t' ',' | sed -E 's/^([^,]*),([^,]*),/\1\t\2\t/') <(hdfs dfs -cat /out/StudentDayText/part-r-00000) > /dev/null && echo "text: same rows" || echo "text: rows differ"
echo "== remove the no-argument constructor of the key"
sed -e 's/StudentDay\b/StudentDayNoCtor/g' -e 's/public StudentDayKey() { }.*/public StudentDayKey(String s, String d) { set(s, d); }/' \
    -e 's/new StudentDayKey()/new StudentDayKey("", "")/' StudentDay.java > StudentDayNoCtor.java
mkdir -p nc && javac -cp $(hadoop classpath) -d nc StudentDayNoCtor.java && jar cf nc.jar -C nc .
hdfs dfs -rm -r -f -skipTrash /out/nc > /dev/null 2>&1
hadoop jar nc.jar StudentDayNoCtor $D /out/nc 2>&1 | grep -E "Error|Caused by|NoSuchMethod|failed with state" | sed -E 's/^[0-9-]+ [0-9:]+ INFO  //' | cut -c1-170 | sort -u | head -5
