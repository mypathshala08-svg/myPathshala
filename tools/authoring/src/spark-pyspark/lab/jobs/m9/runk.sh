#!/bin/bash
# runk.sh NAME script.py : run.sh with Kafka connector jars
cd /root/lab/spark
export PYSPARK_SUBMIT_ARGS="--jars jars/spark-sql-kafka-0-10_2.13-4.3.0.jar,jars/spark-token-provider-kafka-0-10_2.13-4.3.0.jar,jars/kafka-clients-3.9.2.jar,jars/commons-pool2-2.13.1.jar,jars/postgresql-42.7.4.jar --conf spark.ui.showConsoleProgress=false --driver-java-options -Dlog4j2.configurationFile=/root/lab/spark/log4j2.properties pyspark-shell"
./run.sh "$@"
