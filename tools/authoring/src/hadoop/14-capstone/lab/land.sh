# land.sh: copy the raw files into the bronze layer of HDFS, exactly as received
hdfs dfs -rm -r -f -skipTrash /capstone
hdfs dfs -mkdir -p /capstone/bronze/payments /capstone/ref
for c in KHR VSH PNL NRL; do
  hdfs dfs -mkdir -p /capstone/bronze/orders/college=$c
  hdfs dfs -put capstone_raw/orders/$c/*.csv /capstone/bronze/orders/college=$c/
done
hdfs dfs -put capstone_raw/payments/*.jsonl /capstone/bronze/payments/
hdfs dfs -put capstone_raw/menu.csv /capstone/ref/
hdfs dfs -count -h /capstone/bronze/orders /capstone/bronze/payments /capstone/ref
