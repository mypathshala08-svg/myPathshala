#!/bin/bash
# spark-sql with a Hive 3.1.3 metastore client (downloaded by Spark from Maven), host network
docker run --rm --network host -u 0 \
  -e JAVA_TOOL_OPTIONS="$JAVA_TOOL_OPTIONS" -v /etc/ssl/certs/java/cacerts:/etc/ssl/certs/java/cacerts:ro \
  -v hivelab_warehouse:/opt/hive/data/warehouse -v /root/lab/hive/data:/data -v /root/lab/engines/ivy:/root/.ivy2 \
  apache/spark:3.5.6 /opt/spark/bin/spark-sql \
  --conf spark.hadoop.hive.metastore.uris=thrift://localhost:9083 \
  --conf spark.sql.hive.metastore.version=3.1.3 --conf spark.sql.hive.metastore.jars=maven \
  --conf spark.sql.warehouse.dir=file:/opt/hive/data/warehouse \
  --conf spark.ui.enabled=false $EXTRA \
  -e "$1" 2>&1 | grep -vE "^[0-9]{2}/[0-9]{2}/[0-9]{2} [0-9:]+ (INFO|WARN)|^WARNING|^Setting default log level|^To adjust logging|SLF4J|^Spark Web UI|^Spark master|^\s*$|^Picked up JAVA_TOOL"
