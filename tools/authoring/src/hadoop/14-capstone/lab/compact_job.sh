export SPARK_HOME=/tmp/opt/spark-4.0.4-bin-hadoop3 HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop
$SPARK_HOME/bin/spark-submit --master yarn --num-executors 3 --executor-memory 768m --driver-memory 768m compact.py
hdfs dfs -ls -R /capstone/bronze_monthly/orders | grep part- | awk '{print $5, $8}'
