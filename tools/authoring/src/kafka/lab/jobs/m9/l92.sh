#!/bin/bash
D="docker exec k1 /opt/kafka/bin"; B="--bootstrap-server k1:9092"
P(){ printf "$1" | docker exec -i k1 /opt/kafka/bin/kafka-console-producer.sh $B --topic orders-92 --reader-property parse.key=true --reader-property key.separator=: ; }
R(){ java -cp "out:libs/*" Kitchen92 $1 2>/dev/null | grep -v SLF4J; }
docker exec k1 /opt/kafka/bin/kafka-streams-application-reset.sh $B --application-id kitchen-92 --force >/dev/null 2>&1
for t in orders-92 item-counts-92; do $D/kafka-topics.sh $B --delete --topic $t >/dev/null 2>&1; done; rm -rf /tmp/kstate; sleep 3
$D/kafka-topics.sh $B --create --topic orders-92 --partitions 2 --replication-factor 3 >/dev/null
echo "== 1) 6 orders (key = city, value = item); count per item"
P 'Mumbai:idli\nPune:dosa\nMumbai:idli\nDelhi:thali\nPune:idli\nDelhi:dosa\n'
R 15000
echo "== 2) internal topics Kafka Streams created"
$D/kafka-topics.sh $B --list | grep kitchen-92 | sed 's/^/  /'
$D/kafka-topics.sh $B --describe --topic kitchen-92-item-counts-changelog | head -1 | tr '\t' '\n' | grep -E "Configs" | sed 's/^/  changelog /'
echo "== 3) the output topic is a changelog of the table (every update)"
$D/kafka-console-consumer.sh $B --topic item-counts-92 --from-beginning --timeout-ms 5000 --formatter-property print.key=true --formatter-property value.deserializer=org.apache.kafka.common.serialization.LongDeserializer 2>/dev/null | tr '\t' '=' | tr '\n' ' ' | sed 's/^/  /'; echo
echo "== 4) 3 more orders, app restarted with its local state: counts continue"
P 'Mumbai:dosa\nPune:thali\nDelhi:idli\n'
R 12000
echo "== 5) local state deleted (new machine): store rebuilt from the changelog topic"
rm -rf /tmp/kstate
R 15000
