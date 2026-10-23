# wordcount_lab.sh: compile, package and run WordCount on YARN; read the result; make it fail on purpose
cd /tmp/mr
echo "== 1. compile and package"
mkdir -p wc_classes
javac -cp $(hadoop classpath) -d wc_classes WordCount.java && jar cf wc.jar -C wc_classes .
jar tf wc.jar | grep class
echo "== 2. run on feedback.txt"
hdfs dfs -rm -r -f -skipTrash /out/wc > /dev/null 2>&1
hadoop jar wc.jar WordCount /user/hadoop/data/feedback.txt /out/wc 2>&1 \
  | grep -vE "resource-types|ResourceUtils|Executing with tokens|Disabling Erasure" | sed -E 's/^[0-9-]+ [0-9:]+ INFO  //'
echo "== 3. the result"
hdfs dfs -ls /out/wc | awk '{print $5, $8}'
hdfs dfs -cat /out/wc/part-r-00000 | head -5
echo "-- top 8 words"
hdfs dfs -cat /out/wc/part-r-00000 | sort -k2,2nr | head -8
echo "== 4. what YARN remembers"
yarn application -list -appStates FINISHED 2>/dev/null | grep "word count" | awk -F'\t' '{print $1 " | " $2 " | " $6 " | " $7}'
echo "== 5. run again into the same output folder"
hadoop jar wc.jar WordCount /user/hadoop/data/feedback.txt /out/wc 2>&1 | grep -E "Exception" | head -1 | cut -c1-160
echo "== 6. wrong input path"
hadoop jar wc.jar WordCount /user/hadoop/data/feedbak.txt /out/wc2 2>&1 | grep -E "Exception" | head -1 | cut -c1-160
