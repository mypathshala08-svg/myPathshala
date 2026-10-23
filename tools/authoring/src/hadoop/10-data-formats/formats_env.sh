# formats_env.sh: put the Avro-MapReduce, Parquet and ORC jars on the client and task classpaths
L=/tmp/mr10/lib
export LIBJARS=$(ls $L/*.jar | grep -vE "tools|cli" | paste -sd,)
export HADOOP_CLASSPATH=$(echo $LIBJARS | tr , :)
export LIBJARS=$LIBJARS,$(ls /opt/hadoop/share/hadoop/tools/lib/zstd-jni-*.jar)   # Parquet ZSTD needs zstd-jni (in tools/lib, not on the task classpath)
export HADOOP_CLASSPATH=$(echo $LIBJARS | tr , :)
