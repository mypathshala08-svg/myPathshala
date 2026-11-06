#!/bin/bash
R=localhost:8083; D="docker exec k1 /opt/kafka/bin"; B="--bootstrap-server k1:9092"
J(){ python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d,indent=1))" ; }
put(){ curl -s -X PUT -H 'Content-Type: application/json' $R/connectors/$1/config -d "$2" >/dev/null; }
for c in $(curl -s $R/connectors | tr -d '[]"' | tr , ' '); do curl -s -X DELETE $R/connectors/$c; done
for t in orders-71 orders-71-raw bad-71 dlq-71; do $D/kafka-topics.sh $B --delete --topic $t >/dev/null 2>&1; done; sleep 3
rm -f ~/lab/kafka/connect/data/*; printf 'idli,2,40\ndosa,1,90\nthali,1,150\n' > ~/lab/kafka/connect/data/orders.txt
echo "== 1) the worker and its plugins (REST API on :8083)"
curl -s $R/; echo
curl -s $R/connector-plugins | python3 -c "import sys,json; [print('  ',p['type'].ljust(7),p['class'].split('.')[-1],p['version']) for p in json.load(sys.stdin)]"
echo "== 2) Connect stores its own state in Kafka topics"
$D/kafka-topics.sh $B --describe --topic connect-configs,connect-offsets,connect-status 2>/dev/null | grep PartitionCount | awk '{print "  "$2" partitions="$6" "$NF}'
echo "== 3) file source, JsonConverter with schemas.enable=true (default)"
put file-raw '{"connector.class":"org.apache.kafka.connect.file.FileStreamSourceConnector","file":"/data/orders.txt","topic":"orders-71-raw","tasks.max":"1"}'
sleep 8; $D/kafka-console-consumer.sh $B --topic orders-71-raw --from-beginning --timeout-ms 5000 2>/dev/null | head -2
echo "== 4) same file with SMTs (HoistField + InsertField) and schemas.enable=false"
put file-src '{"connector.class":"org.apache.kafka.connect.file.FileStreamSourceConnector","file":"/data/orders.txt","topic":"orders-71","tasks.max":"1",
 "value.converter":"org.apache.kafka.connect.json.JsonConverter","value.converter.schemas.enable":"false",
 "transforms":"wrap,tag","transforms.wrap.type":"org.apache.kafka.connect.transforms.HoistField$Value","transforms.wrap.field":"line",
 "transforms.tag.type":"org.apache.kafka.connect.transforms.InsertField$Value","transforms.tag.static.field":"source","transforms.tag.static.value":"kitchen-file"}'
sleep 8; $D/kafka-console-consumer.sh $B --topic orders-71 --from-beginning --timeout-ms 5000 2>/dev/null
echo "== 5) status, then append 2 lines: streamed within seconds; source offset = file position"
curl -s $R/connectors/file-src/status | python3 -c "import sys,json; d=json.load(sys.stdin); print('  connector',d['connector']['state'],'on',d['connector']['worker_id'],'| tasks',[(t['id'],t['state']) for t in d['tasks']])"
printf 'vada,3,60\nlassi,2,90\n' >> ~/lab/kafka/connect/data/orders.txt; sleep 6
$D/kafka-console-consumer.sh $B --topic orders-71 --from-beginning --timeout-ms 5000 2>/dev/null | wc -l | sed 's/^/  records in orders-71 now: /'
curl -s $R/connectors/file-src/offsets; echo
echo "== 6) sink with errors.tolerance=all and a dead letter queue"
$D/kafka-topics.sh $B --create --topic bad-71 --partitions 1 --replication-factor 3 >/dev/null
printf '{"item":"idli","qty":2}\n{item: broken\n{"item":"dosa","qty":1}\n' | docker exec -i k1 /opt/kafka/bin/kafka-console-producer.sh $B --topic bad-71
put file-sink '{"connector.class":"org.apache.kafka.connect.file.FileStreamSinkConnector","file":"/data/out.txt","topics":"bad-71","tasks.max":"1",
 "value.converter":"org.apache.kafka.connect.json.JsonConverter","value.converter.schemas.enable":"false",
 "errors.tolerance":"all","errors.deadletterqueue.topic.name":"dlq-71","errors.deadletterqueue.topic.replication.factor":"3","errors.deadletterqueue.context.headers.enable":"true"}'
sleep 12; echo "  out.txt:"; sed 's/^/    /' ~/lab/kafka/connect/data/out.txt
echo "  dlq-71:"; $D/kafka-console-consumer.sh $B --topic dlq-71 --from-beginning --timeout-ms 5000 --formatter-property print.headers=true 2>/dev/null | tr ',' '\n' | grep -E "exception.class|exception.message|original.topic|original.offset|broken" | cut -c1-110 | sed 's/^/    /'
curl -s $R/connectors/file-sink/status | python3 -c "import sys,json; d=json.load(sys.stdin); print('  sink task state:',d['tasks'][0]['state'])"
