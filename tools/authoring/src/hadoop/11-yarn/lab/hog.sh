echo "== 4. a map that keeps every line in memory: heap 64 MB vs 300 MB (orders_x30.csv cut into 32 MB splits)"
for heap in 64 300; do
  docker exec lab8-namenode-1 bash -c "cd /tmp/mr11; hdfs dfs -rm -r -f -skipTrash /out/hog$heap > /dev/null 2>&1
    hadoop jar mr11.jar HeapHog -D mapreduce.map.java.opts=-Xmx${heap}m -D mapreduce.input.fileinputformat.split.maxsize=33554432 /user/hadoop/data/orders_x30.csv /out/hog$heap > /tmp/hog.log 2>&1
    echo \" -Xmx${heap}m: \$(grep -oE 'completed successfully|failed with state [A-Z]+' /tmp/hog.log)\"
    grep -oE 'Error: Java heap space|OutOfMemoryError: [A-Za-z ]+|GC overhead limit exceeded' /tmp/hog.log | sort | uniq -c | head -2
    grep -E 'Failed map tasks|Launched map tasks' /tmp/hog.log | sed 's/^\s*/   /'
    hdfs dfs -cat /out/hog$heap/part-m-* 2>/dev/null | sed 's/^/   /'"
done
