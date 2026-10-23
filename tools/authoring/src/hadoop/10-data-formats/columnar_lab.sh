# columnar_lab.sh: the same orders as Parquet and ORC: size, what's inside, and reading only one column
cd /tmp/mr10; source formats_env.sh
D=/user/hadoop/data/student_orders.csv
conv() { name=$1; shift
  hdfs dfs -rm -r -f -skipTrash /out/f_$name > /dev/null 2>&1
  hadoop jar mr10.jar ToColumnar -libjars $LIBJARS "$@" $D /out/f_$name > /tmp/conv_$name.log 2>&1 || echo "$name FAILED"; }
conv parquet_none   -D col.format=parquet -D col.codec=UNCOMPRESSED
conv parquet_snappy -D col.format=parquet -D col.codec=SNAPPY
conv parquet_zstd   -D col.format=parquet -D col.codec=ZSTD
conv orc_none   -D col.format=orc -D col.codec=NONE
conv orc_zlib   -D col.format=orc -D col.codec=ZLIB
conv orc_zstd   -D col.format=orc -D col.codec=ZSTD
echo "== size on HDFS (one replica)"
printf "%-15s %12s\n" text.csv $(hdfs dfs -du -s $D | awk '{print $1}')
printf "%-15s %12s\n" avro_deflate $(hdfs dfs -du -s /out/f_avro_deflate | awk '{print $1}')
for n in parquet_none parquet_snappy parquet_zstd orc_none orc_zlib orc_zstd; do
  printf "%-15s %12s\n" $n $(hdfs dfs -du -s /out/f_$n | awk '{print $1}')
done
echo "== inside one ORC file (orc-tools meta)"
f=$(hdfs dfs -ls /out/f_orc_zlib | grep part | head -1 | awk '{print $8}')
hdfs dfs -get -f $f /tmp/orders.orc 2>/dev/null
java -jar lib/orc-tools-1.9.5-uber.jar meta /tmp/orders.orc 2>/dev/null > /tmp/orc_meta.txt
grep -E "^Rows:|^Compression:|^Type:" /tmp/orc_meta.txt
sed -n '/^File Statistics:/,/^$/p' /tmp/orc_meta.txt | cut -c1-150
grep -m1 "Stripe: offset" /tmp/orc_meta.txt; grep -m6 "Encoding column" /tmp/orc_meta.txt
echo "== read: all columns vs only the item column"
read_job() {  # name, input, format, projection
  hdfs dfs -rm -r -f -skipTrash /out/r_$1 > /dev/null 2>&1
  start=$(date +%s%N)
  hadoop jar mr10.jar ItemCountAny -libjars $LIBJARS -D in.format=$3 -D proj=$4 $2 /out/r_$1 > /tmp/read_$1.log 2>&1
  printf "%-22s %6d ms  HDFS bytes read %10s  chai=%s\n" $1 $(( ($(date +%s%N) - start) / 1000000 )) \
    $(grep "HDFS: Number of bytes read=" /tmp/read_$1.log | head -1 | cut -d= -f2) $(hdfs dfs -cat /out/r_$1/part-r-00000 | grep chai | cut -f2)
}
read_job text_csv $D text true
read_job parquet_all_columns /out/f_parquet_snappy parquet false
read_job parquet_item_only /out/f_parquet_snappy parquet true
read_job orc_all_columns /out/f_orc_zlib orc false
read_job orc_item_only /out/f_orc_zlib orc true
