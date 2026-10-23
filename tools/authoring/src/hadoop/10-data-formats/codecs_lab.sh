# codecs_lab.sh: Hadoop's codecs compared, which compressed files can be split, and compressing map output
cd /tmp/mr10; source formats_env.sh
for i in $(seq 10); do cat /tmp/mr9/student_orders.csv; done > orders_x10.csv
echo "== 1. one file, every codec (single thread, 194 MB of CSV)"
# lz4-java lives in share/hadoop/tools/lib, so add it; native zlib, bzip2 and zstd come from lib/native
java -Djava.library.path=/opt/hadoop/lib/native -cp mr10.jar:$(hadoop classpath):$(ls /opt/hadoop/share/hadoop/tools/lib/lz4-java-*.jar) \
  CodecBench orders_x10.csv 2>&1 | grep -vE "INFO|WARN"
echo "== 2. put them in HDFS with 8 MB blocks and run the same job on each"
hdfs dfs -mkdir -p /user/hadoop/codec
for ext in "" .gz .bz2 .zst .snappy; do
  hdfs dfs -D dfs.blocksize=8388608 -put -f orders_x10.csv$ext /user/hadoop/codec/ 2>/dev/null
done
for ext in "" .gz .bz2 .zst .snappy; do
  f=orders_x10.csv$ext
  hdfs dfs -rm -r -f -skipTrash /out/c_$ext > /dev/null 2>&1
  start=$(date +%s%N)
  hadoop jar mr10.jar ItemCountAny -libjars $LIBJARS /user/hadoop/codec/$f /out/c_$ext > /tmp/c_$ext.log 2>&1
  printf "%-20s %5s blocks  %-18s %6d ms  chai=%s\n" $f $(hdfs fsck /user/hadoop/codec/$f 2>/dev/null | grep "Total blocks" | awk '{print $4}') \
    "$(grep -o 'number of splits:[0-9]*' /tmp/c_$ext.log)" $(( ($(date +%s%N) - start) / 1000000 )) \
    $(hdfs dfs -cat /out/c_$ext/part-r-00000 | grep chai | cut -f2)
done
echo "== 3. compress the map output (shuffle) of a job without a combiner"
for codec in none SnappyCodec ZStandardCodec; do
  opts="-D part.reducers=1"
  [ $codec != none ] && opts="$opts -D mapreduce.map.output.compress=true -D mapreduce.map.output.compress.codec=org.apache.hadoop.io.compress.$codec"
  hdfs dfs -rm -r -f -skipTrash /out/mo_$codec > /dev/null 2>&1
  start=$(date +%s%N)
  hadoop jar /tmp/mr9/mr9.jar ItemPartition $opts /user/hadoop/codec/orders_x10.csv /out/mo_$codec > /tmp/mo_$codec.log 2>&1
  printf "%-15s %6d ms  Map output bytes %s  materialized %s  shuffle %s\n" $codec $(( ($(date +%s%N) - start) / 1000000 )) \
    $(grep "Map output bytes=" /tmp/mo_$codec.log | cut -d= -f2) $(grep "Map output materialized bytes=" /tmp/mo_$codec.log | cut -d= -f2) \
    $(grep "Reduce shuffle bytes=" /tmp/mo_$codec.log | cut -d= -f2)
done
echo "== 4. compress the job's final output"
hdfs dfs -rm -r -f -skipTrash /out/gzout > /dev/null 2>&1
hadoop jar mr10.jar ItemCountAny -libjars $LIBJARS -D mapreduce.output.fileoutputformat.compress=true \
  -D mapreduce.output.fileoutputformat.compress.codec=org.apache.hadoop.io.compress.GzipCodec \
  /user/hadoop/data/student_orders.csv /out/gzout > /dev/null 2>&1
hdfs dfs -ls /out/gzout | grep part | awk '{print $5, $8}'
hdfs dfs -text /out/gzout/part-r-00000.gz 2>/dev/null | grep -v INFO | head -3
