#!/bin/bash
export JAVA_HOME=${JAVA_HOME:-/opt/java/openjdk}
OPENS="--add-opens=java.base/java.lang=ALL-UNNAMED --add-opens=java.base/java.util=ALL-UNNAMED --add-opens=java.base/java.lang.reflect=ALL-UNNAMED --add-opens=java.base/java.net=ALL-UNNAMED --add-opens=java.base/java.io=ALL-UNNAMED --add-opens=java.base/sun.nio.ch=ALL-UNNAMED"
echo "export JAVA_HOME=$JAVA_HOME" >> $HADOOP_CONF_DIR/hadoop-env.sh
echo "export HADOOP_OPTS=\"$OPENS\"" >> $HADOOP_CONF_DIR/hadoop-env.sh
echo "export YARN_OPTS=\"$OPENS\"" >> $HADOOP_CONF_DIR/yarn-env.sh
hdfs namenode -format -force >/tmp/fmt.log 2>&1
hdfs --daemon start namenode; hdfs --daemon start datanode
yarn --daemon start resourcemanager; yarn --daemon start nodemanager
sleep infinity
