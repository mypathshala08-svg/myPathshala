# combiner_lab.sh: what a combiner saves, and how a wrong combiner silently breaks results
cd /tmp/mr9
hdfs dfs -D dfs.blocksize=8388608 -put -f student_orders.csv /user/hadoop/data/student_orders.csv
run() {  # name, then job args
  name=$1; shift
  hdfs dfs -rm -r -f -skipTrash /out/$name > /dev/null 2>&1
  start=$(date +%s%N)
  hadoop jar mr9.jar "$@" /out/$name > /tmp/$name.log 2>&1
  echo "== $name   $(( ($(date +%s%N) - start) / 1000000 )) ms"
  grep -E "Launched map tasks|Map output records|Combine input records|Combine output records|Reduce input records|Reduce shuffle bytes|Spilled Records" /tmp/$name.log | sed 's/^\s*/  /'
}
echo "### Word count on feedback_x20.txt (102 MB, 3 maps)"
run wc_nocomb WordCountCombiner -D wc.combiner=false /user/hadoop/data/feedback_x20.txt
run wc_comb   WordCountCombiner -D wc.combiner=true  /user/hadoop/data/feedback_x20.txt
echo "-- same answer?"
diff <(hdfs dfs -cat /out/wc_nocomb/part-r-00000) <(hdfs dfs -cat /out/wc_comb/part-r-00000) && echo "identical output"
echo
echo "### Average spend per order, per student (student_orders.csv, 5 lakh orders)"
run avg_none  AvgSpend -D avg.combiner=none  /user/hadoop/data/student_orders.csv
run avg_wrong AvgSpend -D avg.combiner=wrong /user/hadoop/data/student_orders.csv
run avg_right AvgSpend -D avg.combiner=right /user/hadoop/data/student_orders.csv
echo "-- three students, three runs"
for s in S0001 S0007 S1413; do
  echo "$s  none: $(hdfs dfs -cat /out/avg_none/part-r-00000 | grep "^$s" | cut -f2)  |  wrong: $(hdfs dfs -cat /out/avg_wrong/part-r-00000 | grep "^$s" | cut -f2)  |  right: $(hdfs dfs -cat /out/avg_right/part-r-00000 | grep "^$s" | cut -f2)"
done
echo "-- students whose answer differs from the no-combiner run"
echo "wrong: $(diff <(hdfs dfs -cat /out/avg_none/part-r-00000) <(hdfs dfs -cat /out/avg_wrong/part-r-00000) | grep -c '^>') of 2000"
echo "right: $(diff <(hdfs dfs -cat /out/avg_none/part-r-00000) <(hdfs dfs -cat /out/avg_right/part-r-00000) | grep -c '^>') of 2000"
