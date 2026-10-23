#!/bin/bash
# Run a single ZooKeeper server using the ZooKeeper jars shipped inside the Hadoop image.
mkdir -p /tmp/zk && printf 'tickTime=2000\ndataDir=/tmp/zk\nclientPort=2181\nadmin.enableServer=false\n4lw.commands.whitelist=*\n' > /tmp/zk/zoo.cfg
exec java -cp "/opt/hadoop/share/hadoop/common/lib/*" org.apache.zookeeper.server.quorum.QuorumPeerMain /tmp/zk/zoo.cfg
