#!/bin/bash
D="docker exec k1 /opt/kafka/bin"; B="--bootstrap-server k1:9092"
for t in orders-91 big-orders-91 small-orders-91; do $D/kafka-topics.sh $B --delete --topic $t >/dev/null 2>&1; done
$D/kafka-consumer-groups.sh $B --delete --group kitchen-91 >/dev/null 2>&1; sleep 3
$D/kafka-topics.sh $B --create --topic orders-91 --partitions 3 --replication-factor 3 >/dev/null
for t in big-orders-91 small-orders-91; do $D/kafka-topics.sh $B --create --topic $t --partitions 3 --replication-factor 3 >/dev/null; done
printf 'Mumbai:idli,2,40\nPune:thali,1,150\nDelhi:dosa,0,90\nMumbai:thali,2,300\nPune:vada,3,60\nDelhi:lassi,1,45\n' | docker exec -i k1 /opt/kafka/bin/kafka-console-producer.sh $B --topic orders-91 --reader-property parse.key=true --reader-property key.separator=:
echo "== run the app with 2 stream threads (topology, state changes, records)"
java -cp "out:libs/*" Kitchen91 2 15000 2>/dev/null | grep -v "^SLF4J"
echo "== outputs"
for t in big-orders-91 small-orders-91; do echo " $t:"; $D/kafka-console-consumer.sh $B --topic $t --from-beginning --timeout-ms 5000 --formatter-property print.key=true 2>/dev/null | sed 's/^/   /'; done
echo "== the app is a consumer group named after application.id"
$D/kafka-consumer-groups.sh $B --describe --group kitchen-91 2>/dev/null | awk 'NR>1 && NF {print "  "$2" p"$3" offset "$4" lag "$6}'
