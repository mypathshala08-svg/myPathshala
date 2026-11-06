#!/bin/bash
X="docker exec sec1 /opt/kafka/bin"; S="--bootstrap-server sec1:9095"
echo "== 1) the broker certificate (signed by our lab CA)"
docker exec sec1 keytool -list -v -keystore /s/sec1.p12 -storepass brokerpass -alias sec1 2>/dev/null | grep -E "^Owner|^Issuer|DNSName|^Valid" | head -4 | sed 's/^/  /'
echo "== 2) three wrong ways in, one right way"
printf 'security.protocol=PLAINTEXT\n' | docker exec -i sec1 sh -c 'cat > /tmp/plain.properties'
echo "  a) plaintext client on the TLS port:"; timeout 25 docker exec sec1 /opt/kafka/bin/kafka-topics.sh $S --command-config /tmp/plain.properties --list 2>&1 | grep -oE "(TimeoutException|SslAuthenticationException|Disconnected)[^.]*" | head -1 | sed 's/^/     /'
sed 's/admin-secret/wrong-password/' ~/lab/kafka/sec/admin.properties > ~/lab/kafka/sec/bad.properties
echo "  b) wrong password:"; timeout 25 $X/kafka-topics.sh $S --command-config /s/bad.properties --list 2>&1 | grep -oE "SaslAuthenticationException[^(]*" | head -1 | sed 's/^/     /'
sed 's#/s/trust.p12#/s/ca.p12#; s/trustpass/wrongpass/' ~/lab/kafka/sec/admin.properties > ~/lab/kafka/sec/notrust.properties
echo "  c) client that does not trust the CA:"; timeout 25 $X/kafka-topics.sh $S --command-config /s/notrust.properties --list 2>&1 | grep -oE "(SslAuthenticationException|KafkaException|IOException)[^\n]{0,90}" | head -1 | sed 's/^/     /'
echo "  d) admin with SCRAM over TLS:"; $X/kafka-broker-api-versions.sh $S --command-config /s/admin.properties 2>/dev/null | head -1 | cut -c1-60 | sed 's/^/     /'
echo "== 3) create SCRAM users and a topic (as admin)"
for u in billing:billing-secret kitchen:kitchen-secret; do $X/kafka-configs.sh $S --command-config /s/admin.properties --alter --entity-type users --entity-name ${u%%:*} --add-config "SCRAM-SHA-512=[iterations=8192,password=${u##*:}]" 2>&1 | sed 's/^/  /'; done
$X/kafka-configs.sh $S --command-config /s/admin.properties --describe --entity-type users 2>/dev/null | sed 's/^/  /'
$X/kafka-topics.sh $S --command-config /s/admin.properties --create --topic payments-103 --partitions 1 --replication-factor 1 2>&1 | sed 's/^/  /'
echo "== 4) no ACLs yet: everyone except admin is denied"
echo '{"order":7,"amount":80}' | timeout 25 docker exec -i sec1 /opt/kafka/bin/kafka-console-producer.sh $S --producer.config /s/billing.properties --topic payments-103 2>&1 | grep -oE "TopicAuthorizationException[^\n]{0,80}|Not authorized[^\n]{0,60}" | head -1 | sed 's/^/  billing write: /'
echo "== 5) grant least privilege"
$X/kafka-acls.sh $S --command-config /s/admin.properties --add --allow-principal User:billing --operation Write --operation Describe --topic payments-103 >/dev/null
$X/kafka-acls.sh $S --command-config /s/admin.properties --add --allow-principal User:kitchen --operation Read --topic payments-103 --group kitchen-103 >/dev/null
$X/kafka-acls.sh $S --command-config /s/admin.properties --list 2>/dev/null | grep -E "resourceType|principal" | sed 's/^\s*//; s/^/  /'
echo "== 6) try again"
echo '{"order":7,"amount":80}' | timeout 25 docker exec -i sec1 /opt/kafka/bin/kafka-console-producer.sh $S --producer.config /s/billing.properties --topic payments-103 2>&1 | grep -c Exception | sed 's/^/  billing write: exceptions = /'
timeout 30 $X/kafka-console-consumer.sh $S --consumer.config /s/kitchen.properties --topic payments-103 --group kitchen-103 --from-beginning --timeout-ms 8000 2>/dev/null | sed 's/^/  kitchen read: /'
echo '{"order":8,"amount":-999}' | timeout 25 docker exec -i sec1 /opt/kafka/bin/kafka-console-producer.sh $S --producer.config /s/kitchen.properties --topic payments-103 2>&1 | grep -oE "TopicAuthorizationException[^\n]{0,80}|Not authorized[^\n]{0,60}" | head -1 | sed 's/^/  kitchen write: /'
timeout 30 $X/kafka-console-consumer.sh $S --consumer.config /s/kitchen.properties --topic payments-103 --group other-group --from-beginning --timeout-ms 8000 2>&1 | grep -oE "GroupAuthorizationException[^\n]{0,80}|Not authorized[^\n]{0,60}" | head -1 | sed 's/^/  kitchen with another group: /'
