#!/bin/bash
D="docker exec k1 /opt/kafka/bin"; B="--bootstrap-server k1:9092"
$D/kafka-topics.sh $B --delete --topic jobs-61 >/dev/null 2>&1; sleep 3
$D/kafka-topics.sh $B --create --topic jobs-61 --partitions 2 --replication-factor 3 >/dev/null
for g in kitchen-61 rej-61 rel-61 rel2-61; do $D/kafka-configs.sh $B --entity-type groups --entity-name $g --alter --add-config share.auto.offset.reset=earliest >/dev/null; done
echo "== 1) topic with 2 partitions, 3000 cooking jobs (we show counts)"
seq 1 3000 | sed 's/^/job-/' | docker exec -i k1 /opt/kafka/bin/kafka-console-producer.sh $B --topic jobs-61
$D/kafka-topics.sh $B --describe --topic jobs-61 | grep Partition: | awk '{print "  " $3 $4 " leader " $6}'
echo "== 2) three share consumers in one share group (3 consumers > 2 partitions)"
for c in A B C; do (docker exec k1 /opt/kafka/bin/kafka-console-share-consumer.sh $B --topic jobs-61 --group kitchen-61 --timeout-ms 10000 --command-property max.poll.records=50 2>/dev/null | sed "s/^/  chef $c got /" > /tmp/sc_$c.txt) & done; wait
for c in A B C; do head -2 /tmp/sc_$c.txt; done
for c in A B C; do echo "  chef $c total: $(wc -l < /tmp/sc_$c.txt)"; done
echo "  all: $(cat /tmp/sc_?.txt | wc -l) records, unique: $(cat /tmp/sc_?.txt | awk '{print $NF}' | sort -u | wc -l)"
echo "== 3) describe the share group"
$D/kafka-share-groups.sh $B --describe --group kitchen-61 2>&1 | sed 's/  */ /g'
echo "== 4) --reject: records are archived, never redelivered"
$D/kafka-console-share-consumer.sh $B --topic small-61 --group rej-61 --reject --timeout-ms 6000 2>/dev/null | wc -l | sed 's/^/  first pass rejected: /'
$D/kafka-console-share-consumer.sh $B --topic small-61 --group rej-61 --timeout-ms 6000 2>/dev/null | wc -l | sed 's/^/  second pass got: /'
$D/kafka-topics.sh $B --create --topic small-61 --partitions 1 --replication-factor 3 >/dev/null 2>&1; seq 1 12 | sed "s/^/job-/" | docker exec -i k1 /opt/kafka/bin/kafka-console-producer.sh $B --topic small-61
echo "== 5) --release: records come back; after the delivery-count limit they are archived"
$D/kafka-configs.sh $B --entity-type groups --entity-name rel2-61 --describe --all 2>/dev/null | grep -E "delivery.count|record.lock" | sed 's/^ */  /'
for i in 1 2 3; do n=$($D/kafka-console-share-consumer.sh $B --topic small-61 --group rel2-61 --release --timeout-ms 5000 2>/dev/null | wc -l); echo "  pass $i (release): received $n"; done
