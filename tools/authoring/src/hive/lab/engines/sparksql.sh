#!/bin/bash
# usage: sparksql.sh "SQL"   -> runs spark-sql against the lab's Hive Metastore
docker run --rm --network hivelab_default -u 0 \
  -v hivelab_warehouse:/opt/hive/data/warehouse -v /root/lab/hive/data:/data \
  apache/spark:3.5.6 /opt/spark/bin/spark-sql \
  --conf spark.hadoop.hive.metastore.uris=thrift://metastore:9083 \
  --conf spark.sql.warehouse.dir=file:/opt/hive/data/warehouse \
  --conf spark.ui.enabled=false \
  -e "$1" 2>&1 | grep -vE "^[0-9]{2}/[0-9]{2}/[0-9]{2} [0-9:]+ (INFO|WARN)|^WARNING|^Setting default log level|^To adjust logging|SLF4J|^Spark Web UI|^Spark master|^\s*$"
