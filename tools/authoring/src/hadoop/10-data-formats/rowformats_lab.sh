# rowformats_lab.sh: the same 5 lakh orders as Text, SequenceFile and Avro: size, what's inside, read speed
cd /tmp/mr10; source formats_env.sh
D=/user/hadoop/data/student_orders.csv
conv() {  # name, class, options
  name=$1; cls=$2; shift 2
  hdfs dfs -rm -r -f -skipTrash /out/f_$name > /dev/null 2>&1
  hadoop jar mr10.jar $cls -libjars $LIBJARS "$@" $D /out/f_$name > /tmp/conv_$name.log 2>&1 || echo "$name FAILED"
}
conv seq_none   ToSequenceFile -D seq.compress=NONE
conv seq_record ToSequenceFile -D seq.compress=RECORD
conv seq_block  ToSequenceFile -D seq.compress=BLOCK
conv avro_null   ToAvro -D avro.codec=null
conv avro_deflate ToAvro -D avro.codec=deflate
conv avro_snappy ToAvro -D avro.codec=snappy
echo "== size on HDFS (one replica)"
printf "%-14s %12s\n" text $(hdfs dfs -du -s $D | awk '{print $1}')
for n in seq_none seq_record seq_block avro_null avro_deflate avro_snappy; do
  printf "%-14s %12s\n" $n $(hdfs dfs -du -s /out/f_$n | awk '{print $1}')
done
echo "== the first bytes of a SequenceFile (a header that names its own types)"
hdfs dfs -cat /out/f_seq_block/part-m-00000 2>/dev/null | head -c 150 | tr -c '[:print:]' '.'; echo
echo "== hdfs dfs -text decodes both binary formats"
hdfs dfs -text /out/f_seq_block/part-m-00000 2>/dev/null | grep -v INFO | head -2
hdfs dfs -text /out/f_avro_deflate/part-m-00000.avro 2>/dev/null | grep -v INFO | head -2
echo "== an Avro file carries its schema"
hdfs dfs -get -f /out/f_avro_deflate/part-m-00002.avro /tmp/orders.avro 2>/dev/null
java -jar lib/avro-tools-1.11.5.jar getmeta /tmp/orders.avro 2>/dev/null | cut -c1-200
echo "== schema evolution: read the old file with a NEW schema that has an extra field with a default"
cat > /tmp/order_v2.avsc <<'J'
{"type":"record","name":"Order","namespace":"in.myphatshala","fields":[
 {"name":"order_id","type":"long"},{"name":"student","type":"string"},{"name":"time","type":"string"},
 {"name":"item","type":"string"},{"name":"amount","type":"int"},
 {"name":"payment","type":"string","default":"cash"}]}
J
java -jar lib/avro-tools-1.11.5.jar tojson --head=2 --reader-schema-file /tmp/order_v2.avsc /tmp/orders.avro 2>/dev/null
echo "-- and a new field WITHOUT a default:"
sed 's/,"default":"cash"//' /tmp/order_v2.avsc > /tmp/order_bad.avsc
java -jar lib/avro-tools-1.11.5.jar tojson --head=2 --reader-schema-file /tmp/order_bad.avsc /tmp/orders.avro 2>&1 | grep -m1 -oE "AvroTypeException.*|Found .*" | cut -c1-170
echo "== read each format with the same item-count job"
read_job() {  # name, input path, format
  hdfs dfs -rm -r -f -skipTrash /out/r_$1 > /dev/null 2>&1
  start=$(date +%s%N)
  hadoop jar mr10.jar ItemCountAny -libjars $LIBJARS -D in.format=$3 $2 /out/r_$1 > /tmp/read_$1.log 2>&1
  ms=$(( ($(date +%s%N) - start) / 1000000 ))
  printf "%-14s %6d ms  HDFS bytes read %10s  map input records %s  chai=%s\n" $1 $ms \
    $(grep "HDFS: Number of bytes read=" /tmp/read_$1.log | head -1 | cut -d= -f2) \
    $(grep "Map input records" /tmp/read_$1.log | cut -d= -f2) \
    $(hdfs dfs -cat /out/r_$1/part-r-00000 | grep chai | cut -f2)
}
read_job text $D text
read_job seq_block /out/f_seq_block seq
read_job avro_deflate /out/f_avro_deflate avro
