# spark_job.sh: run silver_gold.py on YARN (pass days to backfill only those days)
export SPARK_HOME=/tmp/opt/spark-4.0.4-bin-hadoop3 HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop
$SPARK_HOME/bin/spark-submit --master yarn --deploy-mode client \
  --num-executors 3 --executor-memory 768m --executor-cores 1 --driver-memory 768m \
  silver_gold.py "$@"
