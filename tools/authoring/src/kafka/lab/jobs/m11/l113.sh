#!/bin/bash
D="docker exec -e JMX_PORT= k2 /opt/kafka/bin"; B="--bootstrap-server k2:9092"
for t in jobs-113 dlq.jobs-113; do $D/kafka-topics.sh $B --delete --topic $t >/dev/null 2>&1; done; $D/kafka-share-groups.sh $B --delete --group cooks-113 >/dev/null 2>&1; sleep 3
echo "== 1) the version and the feature levels of this cluster"
$D/kafka-topics.sh --version 2>/dev/null | sed 's/^/  kafka /'
$D/kafka-features.sh $B describe 2>/dev/null | awk '{print "  "$2, "level", $8}'
echo "== 2) one cluster, four kinds of groups"
$D/kafka-groups.sh $B --list 2>/dev/null | awk 'NR>1{print $2"/"$3}' | sort | uniq -c | sed 's/^/  /'
echo "== 3) new in 4.4: a dead letter queue for share groups (KIP-1191)"
$D/kafka-topics.sh $B --create --topic jobs-113 --partitions 1 --replication-factor 3 >/dev/null
$D/kafka-topics.sh $B --create --topic dlq.jobs-113 --partitions 1 --replication-factor 3 >/dev/null
$D/kafka-configs.sh $B --entity-type groups --entity-name cooks-113 --alter --add-config 'share.auto.offset.reset=earliest,errors.deadletterqueue.topic.name=dlq.jobs-113,errors.deadletterqueue.copy.record.enable=true' 2>&1 | sed 's/^/  /'
printf 'job-1\njob-2\njob-3\n' | docker exec -i k2 /opt/kafka/bin/kafka-console-producer.sh $B --topic jobs-113
timeout 30 docker exec k2 /opt/kafka/bin/kafka-console-share-consumer.sh $B --topic jobs-113 --group cooks-113 --reject --timeout-ms 8000 2>/dev/null | sed 's/^/  rejected: /'
sleep 3
echo "  dlq.jobs-113 now holds:"
timeout 30 docker exec k2 /opt/kafka/bin/kafka-console-consumer.sh $B --topic dlq.jobs-113 --from-beginning --timeout-ms 6000 --formatter-property print.headers=true 2>/dev/null | cut -c1-230 | sed 's/^/    /'
