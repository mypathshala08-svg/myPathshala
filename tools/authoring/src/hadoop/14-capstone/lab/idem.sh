# idem.sh: backfill one day twice, and show what blind "append" would have done
export SPARK_HOME=/tmp/opt/spark-4.0.4-bin-hadoop3 HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop
S="$SPARK_HOME/bin/spark-submit --master yarn --num-executors 3 --executor-memory 768m --driver-memory 768m"
q() { hdfs dfs -ls -R /capstone/silver/orders/dt=2026-09-14 | grep -c parquet; }
echo "files in dt=2026-09-14 before: $(q)"
$S silver_gold.py 2026-09-14 2>/dev/null | sed -n '/silver.orders/,/^$/p'
$S silver_gold.py 2026-09-14 2>/dev/null | sed -n '/silver.orders/,/^$/p'
echo "files in dt=2026-09-14 after two backfills: $(q)"
$S append_demo.py 2>/dev/null
