import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from svgkit import scn
BODY = body(HERE)
META = dict(module='07-kafka-connect', lesson='02-change-data-capture-with-debezium', n='7.2', module_label='Module 7 · Kafka Connect',
    title='Change data capture with Debezium',
    desc='Log-based change data capture with Debezium on Kafka Connect: Postgres WAL and logical replication slots, snapshots, the change event envelope (before, after, source, op), tombstones, ExtractNewRecordState, slot lag, and the outbox pattern. Real lab: Postgres 16 and Debezium 3.7 on Kafka 4.4 turn INSERT, UPDATE and DELETE into events, and a change made while Connect was down still arrives.',
    og_desc='Postgres to Kafka with Debezium 3.7: r/c/u/d events, tombstones, and no loss while Connect is down.',
    minutes=24, level='Intermediate',
    lead='How do database changes become Kafka events without touching the app? We run <b>Debezium</b> on Postgres, read <b>c/u/d</b> events, flatten them, and stop Connect to prove <b>nothing is lost</b>. <b>All outputs are real.</b>',
    chips=['op r c u d', 'before → after', 'Replication slot', 'Runs in your browser (Python)'])
MAIN = '''# Turn row changes into Debezium-style events
table = {1: {"item": "idli", "status": "PLACED"}}
events = []

def change(op, id, row=None):
    before = table.get(id)
    if op == "d":
        del table[id]
    else:
        table[id] = row
    events.append({"key": {"id": id}, "op": op, "before": before, "after": table.get(id)})
    if op == "d":
        events.append({"key": {"id": id}, "value": None})   # tombstone

change("c", 2, {"item": "dosa", "status": "PLACED"})
change("u", 1, {"item": "idli", "status": "COOKED"})
change("d", 2)
for e in events: print(e)
'''
RUN = dict(heading='Run the code: change events', intro='<p>The CDC envelope in plain Python. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('    events.append({"key": {"id": id}, "op": op, "before": before, "after": table.get(id)})', 'before/after images keyed by primary key.'), ('        events.append({"key": {"id": id}, "value": None})   # tombstone', 'Lets compaction remove the row.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Add another update.', code=None),
        dict(label='2 · Predict first: topic', hint='<b>Predict first:</b> prefix tiffingo, schema public, table orders.', code='print(".".join(["tiffingo", "public", "orders"]))\n'),
        dict(label='3 · Flatten', hint='ExtractNewRecordState.', code='e = {"op": "u", "after": {"id": 1, "status": "COOKED"}}\nprint({**e["after"], "__op": e["op"]})\n'),
        dict(label='4 · Op names', hint='Decode ops.', code='print({"r": "snapshot", "c": "insert", "u": "update", "d": "delete"})\n'),
        dict(label='5 · Spot the error', hint='wal_level not logical.', expect='error', code='wal_level = "replica"\nif wal_level != "logical":\n    raise RuntimeError("Postgres server wal_level property must be \\"logical\\" but is: replica")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC: Debezium CDC', intro='<p>Needs Docker, the lab, and the Debezium plugin in plugin.path. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Postgres', cmd='docker run -d --name pg --network kafnet -e POSTGRES_PASSWORD=pw -e POSTGRES_DB=tiffingo postgres:16 -c wal_level=logical', file='terminal', output='', note='Logical decoding on.'),
           dict(title='2 · Plugin', cmd='curl -L https://repo1.maven.org/maven2/io/debezium/debezium-connector-postgres/3.7.0.Final/debezium-connector-postgres-3.7.0.Final-plugin.tar.gz | tar xz -C plugins', file='terminal', output='', note='Restart the worker after.'),
           dict(title='3 · Events', cmd='kafka-console-consumer.sh --bootstrap-server k1:9092 --topic tiffingo.public.orders --from-beginning', file='terminal', output='{"before":null,"after":{"id":1,"item":"idli","qty":2,"status":"PLACED"},…,"op":"r"}', note='Snapshot first.'),
           dict(title='4 · Slot', cmd='psql -c "select slot_name, active, confirmed_flush_lsn from pg_replication_slots"', file='terminal', output='tiffingo_slot|pgoutput|t|0/197FD30', note='Monitor lag.')])
TRACE = dict(heading='A delete step by step', intro='<p>Event, then tombstone.</p>',
    code='row = {"id": 2, "item": "dosa"}\nevent = {"op": "d", "before": row, "after": None}\ntomb = {"key": {"id": 2}, "value": None}\nprint(event, tomb)\n',
    notes={2: 'Delete event :: before kept.', 3: 'Tombstone :: For compaction.'})
WORKED_INTRO = 'Three CDC decisions.'
EXAMPLES = [
    dict(level='b', tag='CDC · why', title='Polling or CDC?', problem='<p>Need deletes and every change.</p>', inp='need',
         approach=['Polling misses deletes.', 'CDC reads the log.', 'Choose Debezium.'], code='print({"polling": "misses deletes", "CDC": "every change"})\n', notes={1: 'Exact :: Ordered per row.'}, tryit='Types table.'),
    dict(level='i', tag='CDC · sinks', title='Feed a JDBC sink', problem='<p>Sink wants plain rows.</p>', inp='config',
         approach=['ExtractNewRecordState.', 'add.fields=op.', 'Handle deletes (rewrite or drop).'], code='print({"transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState"})\n', notes={1: 'Flatten :: Step 7.'}, tryit='Step 7.'),
    dict(level='a', tag='CDC · outbox', title='Publish domain events', problem='<p>Avoid dual writes.</p>', inp='design',
         approach=['Outbox table in same tx.', 'Debezium outbox event router.', 'Consumers dedupe by event id.'], code='print("BEGIN; insert order; insert outbox; COMMIT;")\n', notes={1: 'Atomic :: One transaction.'}, tryit='Scenario 3.')]
QUIZ = mix([
    dict(q='Beginner: CDC captures…', options=['Only inserts', 'Inserts, updates and deletes', 'Schemas only', 'Queries'], answer=1, why='Every change.'),
    dict(q='Beginner: Debezium reads Postgres changes from…', options=['Table scans', 'The WAL via a replication slot', 'Triggers', 'Backups'], answer=1, why='Log-based.'),
    dict(q='Beginner: op "u" means…', options=['Unknown', 'Update', 'Upsert', 'Undo'], answer=1, why='before + after.'),
    dict(q='Intermediate: Snapshot rows have op…', options=['c', 'r', 's', 'u'], answer=1, why='Read.'),
    dict(q='Intermediate: After a delete Debezium also sends…', options=['Nothing', 'A tombstone', 'A snapshot', 'A schema'], answer=1, why='Null value.'),
    dict(q='Intermediate: Event key is…', options=['Random', 'The primary key', 'The LSN', 'The table name'], answer=1, why='Order per row.'),
    dict(q='Advanced: An unused replication slot can…', options=['Speed up Postgres', 'Fill the disk with WAL', 'Delete tables', 'Nothing'], answer=1, why='WAL retained.'),
    dict(q='Advanced: The outbox pattern avoids…', options=['Snapshots', 'Dual writes', 'Compaction', 'Partitions'], answer=1, why='Same transaction.')])
REVISION = ['Log-based CDC: snapshot (r), then stream WAL via slot (pgoutput).', 'Event: key=PK, before/after/source/op; delete + tombstone.',
    'Lab: r r c u d + tombstone; txId 744; slot active; flattened rows with __op.', 'Resume from LSN after downtime (vada arrived).', 'Watch slot lag; outbox for domain events.']
FAQ = [('Does Debezium slow the database?', 'Slightly: logical decoding has some cost, far less than polling. The snapshot reads tables once.'),
    ('What about schema changes?', 'New columns appear in events; with Schema Registry the schema evolves (Module 8).'),
    ('MySQL?', 'Debezium reads the binlog (row format); concepts are the same.'),
    ('Exactly-once?', 'At-least-once by default; consumers should be idempotent (upsert by key). Debezium supports Connect exactly-once source on some connectors.')]
PRACTICE_INTRO = 'CDC programs.'
PROBLEMS = [
    dict(level='easy', title='Topic', stmt='prefix shop, schema public, table items.', inp='str', code='print("shop.public.items")\n', explain='Naming.'),
    dict(level='easy', title='Op count', stmt='Count ops.', inp='list', code='from collections import Counter\nprint(Counter(["r", "r", "c", "u", "d"]))\n', explain='Lab mix.'),
    dict(level='easy', title='Tombstone?', stmt='Is value None?', inp='val', code='print(None is None)\n', explain='Yes.'),
    dict(level='medium', title='Changed fields', stmt='Diff before/after.', inp='dicts', code='b = {"status": "PLACED", "qty": 2}\na = {"status": "COOKED", "qty": 2}\nprint({k: (b[k], a[k]) for k in a if a[k] != b[k]})\n', explain='status only.'),
    dict(level='medium', title='Apply events', stmt='Rebuild a table from events.', inp='list', code='t = {}\nfor op, id, row in [("c", 1, "idli"), ("u", 1, "idli2"), ("d", 1, None)]:\n    t.pop(id) if op == "d" else t.update({id: row})\nprint(t)\n', explain='Empty.'),
    dict(level='medium', title='Flatten', stmt='Unwrap a delete.', inp='dict', code='e = {"op": "d", "before": {"id": 2}}\nprint({**e["before"], "__deleted": "true"})\n', explain='Rewrite mode.'),
    dict(level='business', title='WAL growth', stmt='20 GB/day, slot stuck 3 days.', inp='ints', code='print(20 * 3, "GB retained")\n', explain='60 GB.'),
    dict(level='business', title='Freshness', stmt='Nightly batch vs CDC lag 2 s.', inp='ints', code='print(24 * 3600 // 2, "x fresher")\n', explain='Huge.')]
SCN_INTRO = 'CDC interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“What is CDC?”', 'Explain.', 'answer?', '<p>Capturing every insert, update and delete from a database as events, usually by reading its transaction log (Debezium), so other systems stay in sync in near real time.</p>', '“A backup tool.”') +
    scn('E-commerce', 'Mid-level', 'Missing deletes', 'Search shows deleted products.', 'fix?', '<ul><li>Use CDC; handle op d / tombstones in the sink.</li></ul>', 'Poll more often.') +
    scn('Platform', 'Mid-level', 'DB disk alarm', 'WAL folder huge.', 'cause?', '<ul><li>Inactive slot.</li><li>Drop or resume, monitor lag.</li></ul>', 'Delete WAL files by hand.') +
    scn('Fintech', 'Senior', 'Reliable events', 'Payments service must emit events.', 'design?', '<ul><li>Outbox table + Debezium router.</li><li>Idempotent consumers.</li></ul>', 'Send to Kafka after commit.'))
