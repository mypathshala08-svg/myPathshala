# get_jars.sh: download the Avro-MapReduce, Parquet and ORC jars (Hadoop ships only avro core)
mkdir -p lib && cd lib
M=https://repo1.maven.org/maven2
for a in org/apache/avro/avro-mapred/1.11.5/avro-mapred-1.11.5.jar \
  org/apache/avro/avro-tools/1.11.5/avro-tools-1.11.5.jar \
  org/apache/parquet/parquet-hadoop/1.15.2/parquet-hadoop-1.15.2.jar \
  org/apache/parquet/parquet-column/1.15.2/parquet-column-1.15.2.jar \
  org/apache/parquet/parquet-common/1.15.2/parquet-common-1.15.2.jar \
  org/apache/parquet/parquet-encoding/1.15.2/parquet-encoding-1.15.2.jar \
  org/apache/parquet/parquet-format-structures/1.15.2/parquet-format-structures-1.15.2.jar \
  org/apache/parquet/parquet-jackson/1.15.2/parquet-jackson-1.15.2.jar \
  org/apache/orc/orc-core/1.9.5/orc-core-1.9.5.jar \
  org/apache/orc/orc-mapreduce/1.9.5/orc-mapreduce-1.9.5.jar \
  org/apache/orc/orc-shims/1.9.5/orc-shims-1.9.5.jar \
  org/apache/orc/orc-tools/1.9.5/orc-tools-1.9.5-uber.jar \
  org/apache/hive/hive-storage-api/2.8.1/hive-storage-api-2.8.1.jar \
  io/airlift/aircompressor/0.27/aircompressor-0.27.jar \
  com/google/protobuf/protobuf-java/3.21.12/protobuf-java-3.21.12.jar \
  org/threeten/threeten-extra/1.7.1/threeten-extra-1.7.1.jar \
  commons-pool/commons-pool/1.6/commons-pool-1.6.jar; do
  curl -sfO $M/$a || echo "download failed: $a"
done
ls | wc -l
