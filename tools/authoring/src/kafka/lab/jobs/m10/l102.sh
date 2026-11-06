#!/bin/bash
D="docker exec -e JMX_PORT= k2 /opt/kafka/bin"; B="--bootstrap-server k2:9092"
for t in perf-1p perf-12p; do $D/kafka-topics.sh $B --delete --topic $t >/dev/null 2>&1; done; sleep 3
$D/kafka-topics.sh $B --create --topic perf-1p --partitions 1 --replication-factor 3 >/dev/null
$D/kafka-topics.sh $B --create --topic perf-12p --partitions 12 --replication-factor 3 >/dev/null
P(){ $D/kafka-producer-perf-test.sh --topic $1 --num-records 200000 --record-size 1000 --throughput -1 --producer-props bootstrap.servers=k1:9092,k2:9092,k3:9092 acks=all $2 2>/dev/null | tail -1 | awk -F, '{print $2","$3","$4}'; }
echo "== 1) producer: 200,000 x 1 KB, acks=all, one variable at a time (topic with 12 partitions)"
echo "  defaults (linger 5 ms, batch 16 KB, none):     $(P perf-12p)"
echo "  batch.size 256 KB + linger 20 ms:               $(P perf-12p 'batch.size=262144 linger.ms=20')"
echo "  + compression lz4:                              $(P perf-12p 'batch.size=262144 linger.ms=20 compression.type=lz4')"
echo "== 2) partitions: same tuned producer, 1 partition vs 12"
echo "  1 partition:   $(P perf-1p 'batch.size=262144 linger.ms=20')"
echo "  12 partitions: $(P perf-12p 'batch.size=262144 linger.ms=20')"
printf "fetch.min.bytes=1048576\nmax.partition.fetch.bytes=4194304\n" | docker exec -i k2 sh -c "cat > /tmp/cbig.properties"
echo "== 3) consumer: read 200,000 records, default fetch vs bigger fetches"
C(){ $D/kafka-consumer-perf-test.sh --bootstrap-server k1:9092 --topic perf-12p --messages 200000 --group perf-$RANDOM $1 2>/dev/null | tail -1 | awk -F, '{printf "%s MB/s, %s msg/s, fetch time %s ms\n",$4,$6,$9}'; }
echo "  defaults:                                        $(C)"
echo "  fetch.min.bytes 1 MB, max.partition.fetch 4 MB:  $(C '--command-config /tmp/cbig.properties')"
