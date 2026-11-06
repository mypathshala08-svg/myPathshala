FROM apache/hadoop:3.4.1 AS h
FROM tiffingo/spark:4.3.0
COPY --from=h /opt/hadoop /opt/hadoop
ENV HADOOP_HOME=/opt/hadoop HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop PATH=$PATH:/opt/hadoop/bin:/opt/hadoop/sbin \
    HDFS_NAMENODE_USER=root HDFS_DATANODE_USER=root YARN_RESOURCEMANAGER_USER=root YARN_NODEMANAGER_USER=root
COPY conf/ /opt/hadoop/etc/hadoop/
COPY start.sh /start.sh
