#!/bin/bash
P="docker exec -e JMX_PORT= k2 /opt/kafka/bin"; PB="--bootstrap-server k2:9092"; R="docker exec dr1 /opt/kafka/bin"; RB="--bootstrap-server dr1:9092"
echo "== 1) primary: topic orders-104 (1,000 orders) and group kitchen-104 (read 600)"
$P/kafka-consumer-groups.sh $PB --describe --group kitchen-104 2>/dev/null | awk 'NR>1&&NF&&$2=="orders-104"{print "  p"$3" committed "$4" end "$5" lag "$6}'
echo "== 2) DR cluster after MirrorMaker 2 started: topics"
$R/kafka-topics.sh $RB --list | grep -v "^__" | sed 's/^/  /'
echo "== 3) the remote topic has the same records"
$R/kafka-get-offsets.sh $RB --topic primary.orders-104 | sed 's/^/  /'
$R/kafka-console-consumer.sh $RB --topic primary.orders-104 --from-beginning --max-messages 2 --formatter-property print.headers=true 2>/dev/null | sed 's/^/  /'
echo "== 4) the group offset, translated and synced on DR"
$R/kafka-consumer-groups.sh $RB --describe --group kitchen-104 2>/dev/null | awk 'NR>1&&NF&&$2!="TOPIC"{print "  "$2" p"$3" committed "$4" end "$5" lag "$6}'
echo "== 5) failover: a consumer on DR with the same group continues, no re-read from 0"
$R/kafka-console-consumer.sh $RB --topic primary.orders-104 --group kitchen-104 --max-messages 3 2>/dev/null | sed 's/^/  first records read on DR: /'
echo "== 6) new orders on primary keep flowing to DR"
seq 1001 1010 | sed 's/^/order-/' | docker exec -i k2 /opt/kafka/bin/kafka-console-producer.sh $PB --topic orders-104; sleep 12
$R/kafka-get-offsets.sh $RB --topic primary.orders-104 | sed 's/^/  /'
