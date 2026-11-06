import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from svgkit import scn
BODY = body(HERE)
META = dict(module='09-stream-processing', lesson='02-ktables-and-state-stores', n='9.2', module_label='Module 9 · Stream processing',
    title='KTables and state stores',
    desc='Stateful stream processing with Kafka Streams: stream–table duality, KTable and GlobalKTable, groupBy vs groupByKey, count/reduce/aggregate, RocksDB state stores, changelog and repartition topics, restore, standby replicas and interactive queries. Real Kafka Streams 4.4 lab: counts per item survive deleting all local state, restored from 9 changelog records.',
    og_desc='Delete the state, restart, and get the same counts: KTable restore from a changelog on Kafka Streams 4.4.',
    minutes=24, level='Intermediate',
    lead='Where does stream state live, and how does it survive a crash? We count orders in a <b>KTable</b>, find the hidden <b>changelog</b> and <b>repartition</b> topics, and <b>restore</b> after deleting local state. <b>All outputs are real.</b>',
    chips=['dosa=3 idli=4 thali=2', 'Restored 9 records', 'Changelog + repartition', 'Runs in your browser (Python)'])
MAIN = '''# A KTable with a changelog, and restore after a crash
from collections import defaultdict
changelog = []                    # compacted topic (we keep all, compaction keeps last per key)
store = defaultdict(int)

def process(city, item):
    store[item] += 1
    changelog.append((item, store[item]))

for c, i in [("Mumbai","idli"),("Pune","dosa"),("Mumbai","idli"),("Delhi","thali"),("Pune","idli"),("Delhi","dosa")]:
    process(c, i)
print("store:", dict(store))

store = defaultdict(int)          # machine lost: local state gone
for k, v in changelog:            # restore
    store[k] = v
print("restored from", len(changelog), "changelog records:", dict(store))
'''
RUN = dict(heading='Run the code: store + changelog', intro='<p>State, backup, restore. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('    changelog.append((item, store[item]))', 'Every update is also written to Kafka.'), ('for k, v in changelog:            # restore', 'Replay keeps the latest value per key.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Then compact the changelog.', code=None),
        dict(label='2 · Predict first: compaction', hint='<b>Predict first:</b> records after compaction of 6 updates over 3 keys.', code='print(3)\n'),
        dict(label='3 · Stream vs table', hint='Same key twice.', code='events = [("idli", 1), ("idli", 2)]\nprint("stream:", events, "table:", dict(events))\n'),
        dict(label='4 · Tombstone', hint='Null deletes.', code='t = {"idli": 3}\nt.pop("idli")\nprint(t)\n'),
        dict(label='5 · Spot the error', hint='Query before RUNNING.', expect='error', code='state = "REBALANCING"\nif state != "RUNNING":\n    raise RuntimeError("InvalidStateStoreException: Cannot get state store item-counts because the stream thread is REBALANCING")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC: state', intro='<p>Needs the Kafka Streams setup from 9.1. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Internal topics', cmd='kafka-topics.sh --bootstrap-server k1:9092 --list | grep kitchen-92', file='terminal', output='kitchen-92-item-counts-changelog\nkitchen-92-item-counts-repartition', note='Auto-created.'),
           dict(title='2 · Local state', cmd='ls /tmp/kstate/kitchen-92/', file='terminal', output='', note='One folder per task (RocksDB).'),
           dict(title='3 · Lose it', cmd='rm -rf /tmp/kstate && java -cp "out:libs/*" Kitchen92 15000', file='terminal', output='  restored 9 records into item-counts\n  store item-counts: dosa=3 idli=4 thali=2', note='Rebuilt.')])
TRACE = dict(heading='One update step by step', intro='<p>Re-key, count, back up.</p>',
    code='key = "idli"\nstore = {"idli": 3}\nstore[key] += 1\nchangelog = [(key, store[key])]\nprint(store, changelog)\n',
    notes={3: 'Count :: RocksDB put.', 4: 'Changelog :: Compacted backup.'})
WORKED_INTRO = 'Three state decisions.'
EXAMPLES = [
    dict(level='b', tag='State · table', title='Stream or table?', problem='<p>Latest address per customer.</p>', inp='need',
         approach=['Latest per key.', 'KTable from topic.', 'Compacted input.'], code='print("b.table(\\"customers\\")")\n', notes={1: 'Table :: Upserts.'}, tryit='Types table.'),
    dict(level='i', tag='State · groupBy', title='Avoid a repartition', problem='<p>Key already the item.</p>', inp='key',
         approach=['groupByKey().', 'No internal topic.', 'Less traffic.'], code='print("groupByKey()")\n', notes={1: 'Cheaper :: No shuffle.'}, tryit='Warning box.'),
    dict(level='a', tag='State · HA', title='Fast failover', problem='<p>Big store, slow restore.</p>', inp='config',
         approach=['num.standby.replicas=1.', 'Persistent volume for state.dir.', 'Monitor restore time.'], code='print({"num.standby.replicas": 1, "state.dir": "/data/kstreams"})\n', notes={1: 'Warm :: Seconds not minutes.'}, tryit='Scenario 1.')]
QUIZ = mix([
    dict(q='Beginner: A KTable holds…', options=['Every event', 'Latest value per key', 'Only keys', 'Offsets'], answer=1, why='Upserts.'),
    dict(q='Beginner: The default state store is…', options=['MySQL', 'RocksDB', 'Redis', 'HDFS'], answer=1, why='Embedded.'),
    dict(q='Beginner: State is backed up to…', options=['A file share', 'A changelog topic', 'ZooKeeper', 'Email'], answer=1, why='Compacted.'),
    dict(q='Intermediate: groupBy (new key) creates…', options=['Nothing', 'A repartition topic', 'A new broker', 'A schema'], answer=1, why='Shuffle.'),
    dict(q='Intermediate: After deleting local state our app restored…', options=['0 records', '9 records', '3 records', 'nothing, counts lost'], answer=1, why='Step 5.'),
    dict(q='Intermediate: A null value in a table means…', options=['Zero', 'Delete the key', 'Error', 'Skip'], answer=1, why='Tombstone.'),
    dict(q='Advanced: Standby replicas…', options=['Serve writes', 'Keep warm copies for failover', 'Replace brokers', 'Compress'], answer=1, why='Fast restore.'),
    dict(q='Advanced: Interactive queries read…', options=['Topics only', 'Local state stores', 'Brokers', 'The registry'], answer=1, why='streams.store().')])
REVISION = ['Stream = events, table = latest per key; duality.', 'Aggregations → RocksDB store per task + compacted changelog.',
    'groupBy re-key → repartition topic; groupByKey avoids it.', 'Lab: dosa=2 idli=3 thali=1 → dosa=3 idli=4 thali=2; rm state → restored 9.', 'Standby replicas, interactive queries, GlobalKTable.']
FAQ = [('Can I use an in-memory store?', 'Yes (Stores.inMemoryKeyValueStore); still backed by a changelog, but restored fully on every start.'),
    ('How big can state be?', 'Limited by local disk per instance; RocksDB handles large stores, restore time grows with size.'),
    ('Why did updates appear one by one?', 'We set the record cache to 0; by default caching batches updates and emits fewer.'),
    ('KTable vs GlobalKTable?', 'KTable is partitioned; GlobalKTable copies the whole topic to every instance and supports joins on non-key fields.')]
PRACTICE_INTRO = 'State programs.'
PROBLEMS = [
    dict(level='easy', title='Count', stmt='Count items.', inp='list', code='from collections import Counter\nprint(Counter(["idli", "dosa", "idli"]))\n', explain='idli 2.'),
    dict(level='easy', title='Upsert', stmt='Table from events.', inp='list', code='print(dict([("a", 1), ("a", 2), ("b", 1)]))\n', explain='a=2.'),
    dict(level='easy', title='Internal name', stmt='Changelog name.', inp='str', code='print("kitchen-92" + "-item-counts" + "-changelog")\n', explain='Pattern.'),
    dict(level='medium', title='Compact', stmt='Keep last per key.', inp='list', code='log = [("idli", 1), ("dosa", 1), ("idli", 2)]\nprint(list(dict(log).items()))\n', explain='Compaction.'),
    dict(level='medium', title='Restore', stmt='Rebuild from log.', inp='list', code='s = {}\nfor k, v in [("idli", 3), ("idli", 4)]: s[k] = v\nprint(s)\n', explain='idli 4.'),
    dict(level='medium', title='Salt', stmt='Spread a hot key.', inp='str', code='import random\nprint([f"sweets#{random.randint(0, 9)}" for _ in range(3)])\n', explain='Sub-keys.'),
    dict(level='business', title='Restore time', stmt='20 GB at 100 MB/s.', inp='ints', code='print(20 * 1024 / 100 / 60, "min")\n', explain='~3.4 min.'),
    dict(level='business', title='Disk', stmt='Store 5 GB + standby.', inp='ints', code='print(5 * 2, "GB across instances")\n', explain='10 GB.')]
SCN_INTRO = 'State interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“KStream vs KTable?”', 'Explain.', 'answer?', '<p>A KStream is every event; a KTable is the latest value per key, where new records update and null deletes. Aggregating a stream gives a table; a table’s changes form a stream.</p>', '“Same thing.”') +
    scn('Platform', 'Mid-level', 'Long startup', 'App takes 20 min to start.', 'cause?', '<ul><li>Restoring big stores.</li><li>Standbys, persistent volumes.</li></ul>', 'Delete changelog.') +
    scn('Platform', 'Mid-level', 'Extra topics', 'Unknown -repartition topics.', 'explain?', '<ul><li>groupBy/selectKey before aggregation.</li><li>Use groupByKey when possible.</li></ul>', 'Delete them.') +
    scn('E-commerce', 'Senior', 'Serve counts', 'API for live counts.', 'design?', '<ul><li>Interactive queries + REST.</li><li>Route by queryMetadataForKey.</li></ul>', 'Poll the output topic.'))
