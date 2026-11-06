#!/bin/sh
# 3-node KRaft (combined broker+controller) Kafka 4.4.0 lab
docker network create kafnet 2>/dev/null
for i in 1 2 3; do docker rm -f k$i >/dev/null 2>&1; docker run -d --name k$i --hostname k$i --network kafnet \
 -e KAFKA_NODE_ID=$i -e KAFKA_PROCESS_ROLES=broker,controller \
 -e KAFKA_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093 -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://k$i:9092 \
 -e KAFKA_CONTROLLER_LISTENER_NAMES=CONTROLLER -e KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT \
 -e KAFKA_CONTROLLER_QUORUM_VOTERS=1@k1:9093,2@k2:9093,3@k3:9093 -e CLUSTER_ID=TiffinGoKafkaLab0001A \
 -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=3 -e KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR=3 -e KAFKA_TRANSACTION_STATE_LOG_MIN_ISR=2 \
 -e KAFKA_LOG_DIRS=/var/lib/kafka/data apache/kafka:4.4.0; done
