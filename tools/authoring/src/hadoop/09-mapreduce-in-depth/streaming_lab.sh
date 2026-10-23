# streaming_lab.sh: the same category-revenue job written in Python and run with Hadoop Streaming
cd /tmp/mr9
JAR=$(ls /opt/hadoop/share/hadoop/tools/lib/hadoop-streaming-*.jar); echo "streaming jar: $JAR"
O=/user/hadoop/data/student_orders.csv
echo "== 1. test the scripts locally first, with a Linux pipe (sort = the shuffle)"
head -1000 student_orders.csv | python3 revenue_mapper.py | sort | python3 revenue_reducer.py
echo "== 2. run on the cluster"
hdfs dfs -rm -r -f -skipTrash /out/stream > /dev/null 2>&1
start=$(date +%s%N)
mapred streaming -files revenue_mapper.py,revenue_reducer.py,menu.csv \
  -input $O -output /out/stream \
  -mapper "python3 revenue_mapper.py" -reducer "python3 revenue_reducer.py" > /tmp/stream.log 2>&1
echo "took $(( ($(date +%s%N) - start) / 1000000 )) ms"
grep -E "number of splits|completed successfully|Launched map tasks|Map output records|Reduce input groups|CPU time spent" /tmp/stream.log | sed -E 's/^[0-9-]+ [0-9:]+ INFO  //; s/^\s*/  /'
hdfs dfs -cat /out/stream/part-00000
echo "== 3. a bug in the mapper (a typo in a variable name)"
sed 's/print(f"{menu.get(item/print(f"{menu.get(itme/' revenue_mapper.py > broken_mapper.py
hdfs dfs -rm -r -f -skipTrash /out/stream_bad > /dev/null 2>&1
mapred streaming -files broken_mapper.py,revenue_reducer.py,menu.csv -input $O -output /out/stream_bad \
  -mapper "python3 broken_mapper.py" -reducer "python3 revenue_reducer.py" > /tmp/stream_bad.log 2>&1
grep -E "subprocess failed|failed with state" /tmp/stream_bad.log | sed -E 's/^[0-9-]+ [0-9:]+ (INFO|ERROR)  //' | sort -u | head -3 | cut -c1-160
app=$(grep -o "application_[0-9_]*" /tmp/stream_bad.log | head -1); sleep 5
echo "-- the Python error is in the task's stderr:"
yarn logs -applicationId $app -log_files stderr 2>/dev/null | grep -E "NameError|Traceback" | sort -u | head -2
