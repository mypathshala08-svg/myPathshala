#!/bin/bash
D="docker exec -e JMX_PORT= k1 /opt/kafka/bin"; B="--bootstrap-server k1:9092"
J(){ docker exec -e JMX_PORT= k1 /opt/kafka/bin/kafka-run-class.sh org.apache.kafka.tools.JmxTool --jmx-url service:jmx:rmi:///jndi/rmi://k1:9101/jmxrmi --object-name "$1" ${2:+--attributes $2} --one-time true 2>/dev/null | tail -1; }
$D/kafka-topics.sh $B --delete --topic orders-101 >/dev/null 2>&1; $D/kafka-consumer-groups.sh $B --delete --group slow-kitchen-101 >/dev/null 2>&1; sleep 3
$D/kafka-topics.sh $B --create --topic orders-101 --partitions 3 --replication-factor 3 >/dev/null
echo "== 1) produce 30,000 orders (perf test, 2,000/s)"
$D/kafka-producer-perf-test.sh --topic orders-101 --num-records 30000 --record-size 200 --throughput 2000 --command-property bootstrap.servers=k1:9092 2>/dev/null | tail -1 | sed 's/^/  /'
echo "== 2) a slow consumer (50 orders/s): lag over time"
python3 slow.py > /tmp/slow.txt 2>&1 &
for i in 1 2 3; do sleep 6; echo "  t+$((i*6))s:"; $D/kafka-consumer-groups.sh $B --describe --group slow-kitchen-101 2>/dev/null | awk 'NR>1 && $2=="orders-101" {printf "    p%s current %s end %s lag %s\n",$3,$4,$5,$6}'; done
wait; cat /tmp/slow.txt
echo "== 3) broker metrics over JMX (broker 1)"
echo "  MessagesInPerSec (1-min rate):   $(J kafka.server:type=BrokerTopicMetrics,name=MessagesInPerSec OneMinuteRate | cut -d, -f2)"
echo "  BytesInPerSec (1-min rate):      $(J kafka.server:type=BrokerTopicMetrics,name=BytesInPerSec OneMinuteRate | cut -d, -f2)"
echo "  UnderReplicatedPartitions:       $(J kafka.server:type=ReplicaManager,name=UnderReplicatedPartitions | cut -d, -f2)"
echo "  ActiveControllerCount:           $(J kafka.controller:type=KafkaController,name=ActiveControllerCount | cut -d, -f2)"
echo "  OfflinePartitionsCount:          $(J kafka.controller:type=KafkaController,name=OfflinePartitionsCount | cut -d, -f2)"
echo "  RequestHandlerAvgIdlePercent:    $(J kafka.server:type=KafkaRequestHandlerPool,name=RequestHandlerAvgIdlePercent OneMinuteRate | cut -d, -f2)"
echo "  NetworkProcessorAvgIdlePercent:  $(J kafka.network:type=SocketServer,name=NetworkProcessorAvgIdlePercent | cut -d, -f2)"
echo "  Produce TotalTimeMs p99:         $(J kafka.network:type=RequestMetrics,name=TotalTimeMs,request=Produce 99thPercentile | cut -d, -f2)"
echo "== 4) break something: pause broker 3, watch the alert metric"
docker pause k3 >/dev/null; sleep 14
echo "  UnderReplicatedPartitions (k3 paused): $(J kafka.server:type=ReplicaManager,name=UnderReplicatedPartitions | cut -d, -f2)"
echo "  IsrShrinksPerSec count:                $(J kafka.server:type=ReplicaManager,name=IsrShrinksPerSec Count | cut -d, -f2)"
docker unpause k3 >/dev/null; sleep 15
echo "  UnderReplicatedPartitions (k3 back):   $(J kafka.server:type=ReplicaManager,name=UnderReplicatedPartitions | cut -d, -f2)"
echo "== 5) disk per broker for the topic (kafka-log-dirs)"
$D/kafka-log-dirs.sh $B --describe --topic-list orders-101 2>/dev/null | grep '^{' | python3 -c "
import sys,json
d=json.load(sys.stdin)
for b in d['brokers']:
    s=sum(p['size'] for ld in b['logDirs'] for p in ld['partitions'])
    print(f\"  broker {b['broker']}: {s/1e6:.2f} MB in {sum(len(ld['partitions']) for ld in b['logDirs'])} partitions\")"
