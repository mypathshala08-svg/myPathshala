#!/bin/bash
R=localhost:8083; D="docker exec k1 /opt/kafka/bin"; B="--bootstrap-server k1:9092"
P(){ docker exec pg psql -U postgres -d tiffingo -qAt -c "$1"; }
curl -s -X DELETE $R/connectors/pg-cdc >/dev/null; curl -s -X DELETE $R/connectors/pg-flat >/dev/null; sleep 2
P "select pg_drop_replication_slot(slot_name) from pg_replication_slots" >/dev/null 2>&1
for t in tiffingo.public.orders flat.public.orders; do $D/kafka-topics.sh $B --delete --topic $t >/dev/null 2>&1; done; sleep 3
P "drop table if exists orders; create table orders(id int primary key, item text, qty int, status text); alter table orders replica identity full; insert into orders values (1,'idli',2,'PLACED'),(2,'dosa',1,'PLACED');"
echo "== 1) Postgres table (wal_level=logical) with 2 existing rows"
P "show wal_level"; P "select * from orders"
echo "== 2) register the Debezium Postgres connector"
curl -s -X PUT -H 'Content-Type: application/json' $R/connectors/pg-cdc/config -d '{"connector.class":"io.debezium.connector.postgresql.PostgresConnector","database.hostname":"pg","database.port":"5432","database.user":"postgres","database.password":"pw","database.dbname":"tiffingo","topic.prefix":"tiffingo","plugin.name":"pgoutput","slot.name":"tiffingo_slot","table.include.list":"public.orders","value.converter":"org.apache.kafka.connect.json.JsonConverter","value.converter.schemas.enable":"false","key.converter":"org.apache.kafka.connect.json.JsonConverter","key.converter.schemas.enable":"false"}' | python3 -c "import sys,json; d=json.load(sys.stdin); print('  created', d['name'], '->', d['config']['connector.class'])"
sleep 15
curl -s $R/connectors/pg-cdc/status | python3 -c "import sys,json; d=json.load(sys.stdin); print('  state', d['connector']['state'], [t['state'] for t in d['tasks']])"
echo "== 3) INSERT, UPDATE, DELETE in Postgres"
P "insert into orders values (3,'thali',1,'PLACED')"; P "update orders set status='COOKED' where id=1"; P "delete from orders where id=2"
sleep 6
echo "== 4) the change events in topic tiffingo.public.orders (key | op before -> after)"
$D/kafka-console-consumer.sh $B --topic tiffingo.public.orders --from-beginning --timeout-ms 6000 --formatter-property print.key=true 2>/dev/null | python3 -c "
import sys,json
for line in sys.stdin:
    k,_,v=line.rstrip('\n').partition('\t')
    if v=='null': print('  ',k,'| TOMBSTONE (null value, for compaction)'); continue
    d=json.loads(v); f=lambda r: None if r is None else {x:r[x] for x in ('id','item','status')}
    print('  ',k,'| op',d['op'],f(d['before']),'->',f(d['after']),' lsn',d['source']['lsn'],'snapshot',d['source']['snapshot'])"
echo "== 5) one full event (the UPDATE), trimmed"
$D/kafka-console-consumer.sh $B --topic tiffingo.public.orders --from-beginning --timeout-ms 6000 2>/dev/null | python3 -c "
import sys,json
for line in sys.stdin:
    if 'COOKED' in line and '\"op\":\"u\"' in line:
        d=json.loads(line); s=d['source']; d['source']={k:s[k] for k in ('connector','version','db','table','lsn','txId','ts_ms')}; print(json.dumps(d,indent=1)); break"
echo "== 6) Postgres side: the replication slot Debezium reads from"
P "select slot_name, plugin, active, confirmed_flush_lsn from pg_replication_slots"
echo "== 7) flatten with ExtractNewRecordState SMT (what most sinks want)"
curl -s -X PUT -H 'Content-Type: application/json' $R/connectors/pg-flat/config -d '{"connector.class":"io.debezium.connector.postgresql.PostgresConnector","database.hostname":"pg","database.port":"5432","database.user":"postgres","database.password":"pw","database.dbname":"tiffingo","topic.prefix":"flat","plugin.name":"pgoutput","slot.name":"flat_slot","table.include.list":"public.orders","value.converter":"org.apache.kafka.connect.json.JsonConverter","value.converter.schemas.enable":"false","key.converter":"org.apache.kafka.connect.json.JsonConverter","key.converter.schemas.enable":"false","transforms":"unwrap","transforms.unwrap.type":"io.debezium.transforms.ExtractNewRecordState","transforms.unwrap.add.fields":"op","transforms.unwrap.delete.tombstone.handling.mode":"rewrite"}' >/dev/null
sleep 15; P "update orders set qty=3 where id=3"; sleep 5
$D/kafka-console-consumer.sh $B --topic flat.public.orders --from-beginning --timeout-ms 6000 2>/dev/null | sed 's/^/  /'
echo "== 8) stop worker, change data, start again: no event lost (resumes from stored LSN)"
docker stop kc >/dev/null; P "insert into orders values (4,'vada',3,'PLACED')"; docker start kc >/dev/null; sleep 35
$D/kafka-console-consumer.sh $B --topic tiffingo.public.orders --from-beginning --timeout-ms 6000 2>/dev/null | grep -c . | sed 's/^/  events now: /'
$D/kafka-console-consumer.sh $B --topic tiffingo.public.orders --from-beginning --timeout-ms 6000 2>/dev/null | grep vada | python3 -c "import sys,json; d=json.loads(sys.stdin.readline()); print('  ', d['op'], d['after'])"
