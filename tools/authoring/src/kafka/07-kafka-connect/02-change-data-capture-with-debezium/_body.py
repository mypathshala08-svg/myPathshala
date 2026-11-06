import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
C = 'l72_cdc.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('Can you turn every INSERT, UPDATE and DELETE in a database into a Kafka event, without touching the application or polling the table?',
    'Yes: <b>change data capture (CDC)</b>. <b>Debezium</b> reads the database’s own transaction log (Postgres WAL) through a <b>replication slot</b>, and emits one event per row change with <b>before</b> and <b>after</b> images. In our lab: 2 snapshot rows, then an insert, an update and a delete appeared as events with op codes <code>c/u/d</code>, the delete was followed by a tombstone, and a row inserted while Connect was <b>down</b> still arrived after restart.',
    ['Why log-based CDC beats polling and dual writes.',
     'The Debezium event envelope: before, after, source, op.',
     'Snapshots, replication slots, tombstones, flattening, and the outbox pattern.'])
cmap = concept_map('Concept map. Beginner: database, change, event. Intermediate: transaction log (WAL), replication slot, Debezium connector, envelope, snapshot. Advanced: tombstones and compaction, ExtractNewRecordState, outbox pattern, slot lag and WAL growth, schema changes.',
    [[('db', 'Database table', 'rows change', None), ('kc', 'Kafka Connect', 'Lesson 7.1', B + '07-kafka-connect/01-kafka-connect/')],
     [('wl', 'WAL / binlog', 'DB’s own log', None), ('sl', 'Replication slot', 'bookmark', None), ('dz', 'Debezium', 'source connector', None), ('en', 'Envelope', 'before/after/op', None)],
     [('sn', 'Snapshot', 'op r', None), ('tb', 'Tombstone + compaction', 'Lesson 4.3', B + '04-storage-internals/03-retention-and-compaction/'), ('fl', 'Flatten SMT', 'for sinks', None), ('ob', 'Outbox pattern', 'events from apps', None)]],
    [('db', 'wl'), ('wl', 'sl'), ('sl', 'dz'), ('kc', 'dz'), ('dz', 'en'), ('dz', 'sn'), ('en', 'tb'), ('en', 'fl'), ('dz', 'ob')],
    {'wl', 'sl', 'dz', 'en', 'sn', 'tb', 'fl', 'ob'},
    '<b>Builds on:</b> <a href="../01-kafka-connect/">7.1</a>, <a href="../../04-storage-internals/03-retention-and-compaction/">4.3</a>. <b>Next:</b> Module 8 schemas.')
whw = why_how_where(
    'Polling (SELECT … WHERE updated_at > x) misses deletes and intermediate updates and loads the DB. Writing to DB and Kafka in the app (dual write) can leave them inconsistent. The transaction log already has every committed change, in order.',
    'Debezium takes an initial consistent snapshot (op r), then streams from the log via a logical replication slot (pgoutput). Each change becomes a record keyed by the primary key, with before/after, source metadata (LSN, txId, table) and op c/u/d; deletes add a tombstone. Its position (LSN) is stored as the Connect source offset.',
    'Microservice data sync, cache invalidation, search indexing, feeding data lakes/warehouses in near real time, audit trails, and migrations off legacy DBs. Supported: Postgres, MySQL/MariaDB, SQL Server, Oracle, MongoDB, Db2 and more.',
    'Needs DB settings (Postgres wal_level=logical, replication privileges). An inactive slot makes Postgres keep WAL forever: monitor slot lag. Full before images need REPLICA IDENTITY FULL.')

def cdc(hl=-1):
    parts = [('app SQL', 'card'), ('WAL', 'violet'), ('slot', 'amber'), ('Debezium', 'blue'), ('topic', 'green')]
    o = ''
    for k, (n, tn) in enumerate(parts):
        o += box(8 + k * 70, 50, 62, 40, 'acc' if k == hl else tn, rx=6) + t(39 + k * 70, 74, n, 7.4, bold=True)
        if k < 4: o += arrow(70 + k * 70, 70, 78 + k * 70, 70)
    return o + t(180, 30, 'Postgres → Kafka Connect → tiffingo.public.orders', 7.4)
scene_svg = scene('Change data capture: the application writes SQL, Postgres records it in the write-ahead log, a logical replication slot feeds Debezium running in Kafka Connect, which writes change events to a Kafka topic.', cdc(),
                  'Read the <tspan font-weight="700" class="s-acc">database’s own log</tspan>, not the table.')
dialogue = '''K> Sir, the orders service writes to Postgres. Ten other teams want to know when an order changes. Should every team poll the orders table?
A> No. Polling misses deletes and hammers the DB. Postgres already writes every change to its <b>WAL</b>. Debezium reads that log and turns each change into a Kafka event.
R> And if Connect is down for an hour?
A> The <b>replication slot</b> keeps the WAL until Debezium confirms it. Nothing is lost; we’ll prove it by stopping the worker.'''

lv = '''
LEVELS> CDC at three levels
L1> The bank passbook
      <ul>
        <li>Instead of checking your balance every minute to guess what happened, read the passbook: every deposit and withdrawal is printed in order. Debezium reads the database’s passbook (its log) and announces each line.</li>
      </ul>
L2> The event
      <ul>
        <li>Topic name: <code>&lt;topic.prefix&gt;.&lt;schema&gt;.&lt;table&gt;</code> (ours: <code>tiffingo.public.orders</code>); key = primary key, so all changes of one row stay ordered in one partition.</li>
        <li><code>op</code>: <b>r</b> read (snapshot), <b>c</b> create, <b>u</b> update, <b>d</b> delete, <b>t</b> truncate. <code>before</code>/<code>after</code> row images; <code>source</code> has connector version, db, table, LSN, txId, timestamps.</li>
        <li>After a delete Debezium sends a <b>tombstone</b> (same key, null value) so compacted topics drop the row entirely (Lesson 4.3).</li>
      </ul>
L3> Production
      <ul>
        <li><code>snapshot.mode</code> (initial, no_data, when_needed, …) and <b>incremental snapshots</b> via a signal table let you re-snapshot big tables without stopping streaming.</li>
        <li><b>ExtractNewRecordState</b> SMT flattens the envelope to just the row (+ <code>__op</code>, <code>__deleted</code>) for sinks like JDBC/Elasticsearch.</li>
        <li><b>Outbox pattern</b>: the service writes business data and an event row to an <code>outbox</code> table in the same transaction; Debezium’s outbox router publishes those events. This avoids dual writes and exposes intentional events, not raw table rows.</li>
        <li>Watch <b>slot lag</b> (<code>pg_replication_slots.confirmed_flush_lsn</code> vs current WAL), set <code>heartbeat.interval.ms</code> for quiet tables, and drop slots of deleted connectors. Schema changes flow as new event schemas: use Schema Registry (Module 8).</li>
      </ul>
/LEVELS
'''
EV = figure('Dissection of a Debezium update event: before shows status PLACED, after shows status COOKED, source shows connector postgresql, table orders, lsn 26737800 and txId 744, and op is u.',
    t(16, 22, 'The UPDATE event for order 1', 8.6, 'ink', anchor='start', bold=True) +
    fields(16, 34, [('before: PLACED', 'blue', 1), ('after: COOKED', 'green', 2), ('source: lsn 26737800 tx 744', 'violet', 3), ('op: "u"', 'acc', 4)]) +
    legend(16, 84, [(1, 'before', 'row before the change (needs REPLICA IDENTITY FULL for all columns)'), (2, 'after', 'row after the change (null for a delete)'),
                    (3, 'source', 'where/when in the DB log: LSN, transaction, table'), (4, 'op', 'r snapshot, c insert, u update, d delete')], size=8, gap=15, w=90),
    h=152, caption='Real event from our lab.')
extra = '''

  <h3>Dissect a change event</h3>
''' + EV

types_html = table(['Approach', 'Deletes?', 'DB load', 'Consistency'], [
    ['Polling query (updated_at)', 'no', 'high', 'misses intermediate changes'], ['Dual write in app', 'yes', 'none', 'can diverge on failure'],
    ['Triggers to a table', 'yes', 'medium', 'OK, but couples DB'], ['Log-based CDC (Debezium)', 'yes', 'low', 'exact, ordered per row'],
    ['Outbox + CDC', 'events by design', 'low', 'transactional events'],
], minw=600) + table(['op', 'Meaning', 'before', 'after'], [
    ['r', 'snapshot read', 'null', 'row'], ['c', 'insert', 'null', 'row'], ['u', 'update', 'old row', 'new row'], ['d', 'delete', 'old row', 'null (+ tombstone)'],
], minw=480)
warn = 'A stopped or deleted Debezium connector leaves its Postgres replication slot behind, and Postgres will keep WAL files until the disk fills and the database stops. Monitor slot lag and drop unused slots (pg_drop_replication_slot).'

steps = [
    ('Step 1 · Prepare Postgres',
     code('sql', 'psql', "-- server started with: -c wal_level=logical\ncreate table orders(id int primary key, item text, qty int, status text);\nalter table orders replica identity full;\ninsert into orders values (1,'idli',2,'PLACED'),(2,'dosa',1,'PLACED');", sec('== 1)', '== 2)')),
     'wal_level=logical lets the WAL be decoded into row changes. REPLICA IDENTITY FULL puts all old columns into update/delete records.'),
    ('Step 2 · Register Debezium',
     code('json', 'pg-cdc config', '{"connector.class": "io.debezium.connector.postgresql.PostgresConnector",\n "database.hostname": "pg", "database.dbname": "tiffingo",\n "database.user": "postgres", "database.password": "…",\n "topic.prefix": "tiffingo", "plugin.name": "pgoutput",\n "slot.name": "tiffingo_slot", "table.include.list": "public.orders"}', sec('== 2)', '== 3)')),
     'Debezium 3.7.0 on a Kafka 4.4 Connect worker. It creates the slot and a publication, snapshots the table, then streams.'),
    ('Step 3 · Change data',
     code('sql', 'psql', "insert into orders values (3,'thali',1,'PLACED');\nupdate orders set status='COOKED' where id=1;\ndelete from orders where id=2;", sec('== 3)', '== 4)')),
     'Plain SQL: the application does not know Kafka exists.'),
    ('Step 4 · The events',
     code('bash', 'terminal', 'kafka-console-consumer.sh --bootstrap-server k1:9092 --topic tiffingo.public.orders --from-beginning --formatter-property print.key=true', sec('== 4)', '== 5)')),
     'Two snapshot reads (r, snapshot first/last), then c, u and d, each with the LSN. The delete is followed by a tombstone for key {"id":2}.'),
    ('Step 5 · One full event',
     code('bash', 'terminal', '… | grep \'"op":"u"\' | python3 -m json.tool', sec('== 5)', '== 6)')),
     'before and after differ only in status. source.txId 744 ties it to the Postgres transaction.'),
    ('Step 6 · The replication slot',
     code('sql', 'psql', 'select slot_name, plugin, active, confirmed_flush_lsn from pg_replication_slots;', sec('== 6)', '== 7)')),
     'The slot is active and its confirmed_flush_lsn shows how far Debezium has acknowledged. Postgres keeps WAL from that point.'),
    ('Step 7 · Flatten for sinks',
     code('json', 'pg-flat config', '"transforms": "unwrap",\n"transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",\n"transforms.unwrap.add.fields": "op",\n"transforms.unwrap.delete.tombstone.handling.mode": "rewrite"', sec('== 7)', '== 8)')),
     'A second connector (its own slot) snapshotted the current rows and then the qty update: just the row plus <code>__op</code> and <code>__deleted</code>.'),
    ('Step 8 · Survive downtime',
     code('bash', 'terminal', "docker stop kc\npsql -c \"insert into orders values (4,'vada',3,'PLACED')\"\ndocker start kc", sec('== 8)')),
     'The insert made while the worker was stopped arrived after restart: Debezium resumed from the LSN stored in connect-offsets, and the slot had kept the WAL.'),
]
see = [term([('wal_level logical', G), ('1 idli PLACED', W), ('2 dosa PLACED', W)], size=7.2), term([('pg-cdc RUNNING', G)], size=7.4),
       term([('insert 3 · update 1 · delete 2', W)], size=7.2), term([('r r c u d', Y), ('+ TOMBSTONE {"id":2}', RD)], size=7.2),
       term([('before PLACED', W), ('after COOKED', G), ('txId 744', W)], size=7.2), term([('tiffingo_slot pgoutput t', G)], size=7.2),
       term([('{"id":3,"qty":3,', G), ('"__op":"u"}', Y)], size=7.2), term([('worker stopped', RD), ('c vada after restart', G)], size=7.2)]
B1 = [cdc(1), cdc(3), cdc(0), cdc(4), cdc(4), cdc(2), cdc(4), cdc(2)]
B1 = [b + cap(c, '', tn, y=120, h=30) for b, c, tn in zip(B1, ['WAL logical', 'Connector running', 'SQL changes', 'Events per row', 'Envelope', 'Slot bookmark', 'Flattened rows', 'Slot kept WAL'], ['violet', 'blue', 'blue', 'green', 'green', 'amber', 'green', 'amber'])]
two = anim_two('CDC with Debezium', 'From SQL to events', 'Real outputs from the lab', 'Inside CDC', see, B1, ['Prepare.', 'Register.', 'Change.', 'Events.', 'Envelope.', 'Slot.', 'Flatten.', 'Downtime.'], ['WAL.', 'Snapshot.', 'SQL.', 'c/u/d.', 'before/after.', 'Bookmark.', 'Sink-ready.', 'No loss.'])
pe = peel('One UPDATE, layer by layer', 'update orders set status=\'COOKED\' where id=1. (Simplified.)',
    [('Commit', ''), ('WAL', ''), ('Decode', ''), ('Debezium', ''), ('Kafka', ''), ('Ack', '')],
    [['Commit', 'tx 744', 'row 1 updated', ''], ['WAL', 'record at', 'LSN 26737800', ''], ['Decode', 'pgoutput', 'via tiffingo_slot', 'old + new tuple'],
     ['Debezium', 'envelope', 'op u, before/after', 'key {"id":1}'], ['Kafka', 'tiffingo.public.orders', 'partition by key', ''], ['Ack', 'offset flushed', 'slot confirmed LSN', 'WAL can be recycled']],
    ['Commit.', 'Log.', 'Decode.', 'Wrap.', 'Send.', 'Confirm.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'Search index out of date', 'Products edited, search shows old prices. (Typical.)', ('CDC to search', 'Every change reaches the index'), [
    ('Nightly batch reindex', 'stale for hours', 'Problem.', 'red'), ('Debezium on products', 'events in seconds', 'Stream.', 'green'),
    ('Unwrap SMT', 'row + __deleted', 'Shape.', 'green'), ('Elasticsearch sink', 'upsert / delete by key', 'Index.', 'blue'),
    ('Seconds-fresh search', 'no app change', 'Done.', 'blue')], ['Stale.', 'Capture.', 'Flatten.', 'Sink.', 'Fresh.'], 'scenario-search') + \
       five('Real-time scenario 2', 'Postgres disk full', 'Forgotten slot. (Typical.)', ('Slot lag', 'Inactive slot retains WAL'), [
    ('Test connector deleted', 'slot left behind', 'Unnoticed.', 'blue'), ('WAL grows 50 GB/day', 'disk 95%', 'Alarm.', 'red'),
    ('Find inactive slots', 'pg_replication_slots', 'Diagnose.', 'amber'), ('pg_drop_replication_slot', 'WAL recycled', 'Fix.', 'green'),
    ('Monitor slot lag', 'alert > threshold', 'Prevent.', 'blue')], ['Leave.', 'Grow.', 'Find.', 'Drop.', 'Watch.'], 'scenario-slot') + \
       five('Real-time scenario 3 · advanced', 'Order placed but event missing', 'Dual write failure. (Typical.)', ('Outbox pattern', 'One transaction, CDC publishes'), [
    ('Service: DB commit, then Kafka send', 'two systems', 'Fragile.', 'blue'), ('Crash between them', 'order saved, no event', 'Inconsistent.', 'red'),
    ('Write outbox row in same tx', 'atomic', 'Fix.', 'green'), ('Debezium outbox router', 'publishes outbox events', 'Reliable.', 'green'),
    ('Consumers idempotent', 'by event id', 'Safe.', 'blue')], ['Dual.', 'Crash.', 'Outbox.', 'Route.', 'Dedupe.'], 'scenario-outbox')
assemble(HERE, h2_story='Every database change becomes an event', hook_html=hk,
    narration='TiffinGo’s orders live in Postgres. Delivery, billing and analytics teams all want to react when an order changes, without asking the orders team to change their code.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Change data capture with Debezium',
    formal='<b>Change data capture (CDC)</b> is the practice of capturing row-level changes from a database and publishing them as events. <b>Debezium</b> is an open-source set of Kafka Connect source connectors that perform log-based CDC: they take an initial consistent snapshot and then read the database transaction log (e.g. the Postgres WAL via a logical replication slot), emitting one record per change with before/after images, source metadata and an operation type, keyed by primary key.',
    simple='Debezium watches the database’s own diary of changes and turns each insert, update and delete into a Kafka message, in order, without the app doing anything.',
    term_rows=[('CDC', 'Capturing DB changes as events.'), ('WAL', 'Postgres write-ahead log.'), ('Replication slot', 'Bookmark that keeps WAL.'), ('LSN', 'Position in the WAL.'), ('Snapshot', 'Initial copy (op r).'), ('Envelope', 'before/after/source/op.'), ('Tombstone', 'Null value after delete.'), ('Outbox', 'Event table written in the same tx.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('CDC means polling the table.', 'Log-based CDC reads the WAL.', 'Step 6 slot.'),
               ('Deletes cannot be captured.', 'op d + tombstone.', 'Step 4.'),
               ('Downtime loses changes.', 'Slot + stored LSN resume.', 'Step 8.')],
    exam='“How does Debezium CDC work?” Snapshot then stream from DB log (Postgres WAL via logical slot, pgoutput); events keyed by PK with before/after/source/op (r/c/u/d), tombstones; LSN stored as Connect offset; ExtractNewRecordState for sinks; outbox pattern; watch slot lag.',
    types_h2='CDC approaches and op codes', types_html=types_html, warn=warn,
    steps_h2='From SQL to events', steps_intro='All outputs are real: Postgres 16, Debezium 3.7.0.Final on a Kafka 4.4.0 Connect worker, 3-broker lab.',
    steps=steps, two=two, peel_intro='Now peel one UPDATE.', peel_html=pe,
    scen_intro='Three live scenarios: stale search, a full disk, and the outbox.', scen=scen,
    uc_h2='CDC at work', ucs=[uc_('ms', 'services', 'blue', '1. Microservice sync', 'Other services react to order changes.', ['Orders DB', '*CDC', 'Services']),
        uc_('dw', 'analytics', 'green', '2. Real-time warehouse', 'Lake/warehouse minutes fresh.', ['OLTP', '*CDC', 'Lakehouse']),
        uc_('cache', 'cache', 'violet', '3. Cache invalidation', 'Evict keys on change.', ['DB', '*CDC', 'Redis']),
        uc_('mig', 'migrate', 'amber', '4. Zero-downtime migration', 'Old DB → new DB while live.', ['Legacy', '*CDC', 'New'])],
    uc_note='Examples are simplified descriptions of common practice.',
    pre='<b>Before you start:</b> <a href="../01-kafka-connect/">7.1 Kafka Connect</a>.')
