import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
C = 'l92_ktable.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('Your app counts orders per item in memory. The machine dies. Where do the counts come from on the new machine?',
    'From Kafka itself. A <b>KTable</b> keeps its state in a local <b>state store</b> (RocksDB), and every change is also written to a compacted <b>changelog topic</b>. In our lab we deleted the whole local state folder, restarted, and the app <b>restored 9 records</b> from the changelog and answered <code>dosa=3 idli=4 thali=2</code>, exactly as before.',
    ['KStream vs KTable: events vs latest value per key.',
     'State stores, changelog and repartition topics.',
     'Restore, standby replicas and interactive queries.'])
cmap = concept_map('Concept map. Beginner: stream vs table, count per key. Intermediate: KTable, groupBy, state store, changelog topic, repartition topic. Advanced: restore, standby replicas, record cache, interactive queries, GlobalKTable.',
    [[('ks', 'KStream', 'Lesson 9.1', B + '09-stream-processing/01-kafka-streams/'), ('dq', 'Table duality', 'stream ↔ table', None)],
     [('kt', 'KTable', 'latest per key', None), ('gb', 'groupBy + count', 'aggregate', None), ('ss', 'State store', 'RocksDB', None), ('rp', 'Repartition topic', 're-key', None)],
     [('cl', 'Changelog + restore', 'compacted', B + '04-storage-internals/03-retention-and-compaction/'), ('sb', 'Standby replicas', 'fast failover', None), ('iq', 'Interactive queries', 'read the store', None), ('wj', 'Windows + joins', 'Lesson 9.3', B + '09-stream-processing/03-windows-and-joins/')]],
    [('ks', 'dq'), ('dq', 'kt'), ('kt', 'gb'), ('gb', 'ss'), ('gb', 'rp'), ('ss', 'cl'), ('cl', 'sb'), ('ss', 'iq'), ('kt', 'wj')],
    {'dq', 'kt', 'gb', 'ss', 'rp', 'cl', 'sb', 'iq'},
    '<b>Builds on:</b> <a href="../01-kafka-streams/">9.1</a>, <a href="../../04-storage-internals/03-retention-and-compaction/">4.3 compaction</a>. <b>Next:</b> <a href="../03-windows-and-joins/">9.3 Windows and joins</a>.')
whw = why_how_where(
    'Counting, summing, deduplicating and joining all need memory of the past. Keeping it only in RAM loses it on restart; an external database adds latency and a second system.',
    'Aggregations create a local state store per task. Every update is also produced to <code>&lt;app&gt;-&lt;store&gt;-changelog</code> (compacted). On restart or task move, the store is rebuilt from that topic. If the key changes first (groupBy), records go through a <code>-repartition</code> topic so all records of a key meet in one task.',
    'Live counters and dashboards, shopping carts, inventory, user profiles, deduplication, materialized views for microservices (queried via interactive queries).',
    'Restoring large stores takes time: use standby replicas and persistent volumes. State is per task, so a query for a key must go to the instance that owns it.')

def tbl(rows, hl=False):
    o = box(200, 30, 150, 96, 'acc' if hl else 'green', rx=8) + t(275, 46, 'KTable item-counts', 7.8, bold=True)
    for k, (key, v) in enumerate(rows):
        o += t(236, 64 + k * 16, key, 7.6, mono=True) + t(316, 64 + k * 16, str(v), 7.6, mono=True, bold=True)
    o += box(10, 30, 150, 96, 'blue', rx=8) + t(85, 46, 'KStream orders', 7.8, bold=True)
    for k, e in enumerate(['Mumbai: idli', 'Pune: dosa', 'Mumbai: idli', 'Delhi: thali']):
        o += t(85, 64 + k * 16, e, 7.2, mono=True)
    return o + arrow(162, 78, 198, 78) + t(180, 72, 'count', 7)
scene_svg = scene('A KStream of order events (Mumbai idli, Pune dosa, Mumbai idli, Delhi thali) is grouped by item and counted into a KTable that holds the latest count per item.', tbl([('idli', 2), ('dosa', 1), ('thali', 1)]),
                  'A stream of events becomes a <tspan font-weight="700" class="s-acc">table of latest values</tspan>.')
dialogue = '''K> Sir, the kitchen dashboard needs “orders per item so far”. I will keep a HashMap in the app.
A> And when the pod restarts, the HashMap is empty. Use a <b>KTable</b>: the count lives in a state store, and every change is backed up to a Kafka topic.
R> Backed up where exactly?
A> In a compacted <b>changelog</b> topic that Streams creates for you. We’ll delete the local data and watch it come back.'''

lv = '''
LEVELS> Tables at three levels
L1> The tally sheet
      <ul>
        <li>Each order is a tick (stream). The tally sheet shows the current total per dish (table). If the sheet is lost, you can redraw it by replaying the ticks, or faster, from a photocopy of the latest totals (the compacted changelog).</li>
      </ul>
L2> The DSL
      <ul>
        <li><b>Stream–table duality</b>: a table is the latest value per key of a stream; a table’s changes form a stream (<code>toStream()</code>).</li>
        <li><code>groupByKey()</code> keeps the key (no repartition); <code>groupBy(...)</code> re-keys → internal <code>-repartition</code> topic. Then <code>count()</code>, <code>reduce()</code>, <code>aggregate()</code> produce a KTable.</li>
        <li><code>b.table("topic")</code> reads a topic as a table; <b>GlobalKTable</b> gives every instance the full table (good for small lookup data).</li>
      </ul>
L3> Under the hood
      <ul>
        <li>Default store: RocksDB under <code>state.dir</code>, one per task; changelog topic is compacted with the same partition count as the input.</li>
        <li>Record cache (<code>statestore.cache.max.bytes</code>, 10 MB default) batches updates; we set 0 to see every update. Downstream updates also leave on commit.</li>
        <li><code>num.standby.replicas</code> keeps warm copies on other instances for fast failover. <b>Interactive queries</b>: <code>streams.store(...)</code> reads local state; route remote keys with <code>queryMetadataForKey</code>.</li>
      </ul>
/LEVELS
'''
IT = figure('Internal topics created by the app kitchen-92: a repartition topic, written after groupBy re-keys records by item, and a compacted changelog topic that backs up the item-counts store.',
    box(10, 40, 110, 40, 'blue', rx=6) + t(65, 64, 'orders-92', 8, bold=True) + arrow(122, 60, 150, 60) +
    box(152, 30, 170, 60, 'amber', rx=6) + t(237, 52, 'kitchen-92-item-counts-', 7.4, mono=True) + t(237, 68, 'repartition', 7.4, mono=True, bold=True) + arrow(324, 60, 352, 60) +
    box(354, 40, 120, 40, 'green', rx=6) + t(414, 64, 'store item-counts', 7.6, bold=True) + arrow(474, 60, 500, 60) +
    box(502, 30, 130, 60, 'violet', rx=6) + t(567, 52, 'kitchen-92-item-', 7.4, mono=True) + t(567, 68, 'counts-changelog', 7.4, mono=True, bold=True) +
    t(237, 112, 're-key city → item', 7.4) + t(567, 112, 'cleanup.policy=compact', 7.4),
    h=150, caption='Names are &lt;application.id&gt;-&lt;store&gt;-&lt;suffix&gt;.')
extra = '''

  <h3>The hidden topics</h3>
''' + IT

types_html = table(['', 'KStream', 'KTable', 'GlobalKTable'], [
    ['Meaning', 'every event', 'latest per key', 'latest per key, full copy'], ['Same key twice', 'two records', 'update', 'update'],
    ['Null value', 'a record', 'delete (tombstone)', 'delete'], ['Partitioned', 'yes', 'yes', 'no (every instance has all)'],
    ['Typical use', 'orders, clicks', 'counts, profiles', 'small lookup tables'],
], minw=600) + table(['Internal topic', 'Why', 'Policy'], [
    ['…-repartition', 'records re-keyed before grouping/joining', 'delete (purged after use)'], ['…-changelog', 'backup of a state store', 'compact'],
], minw=500)
warn = 'A groupBy that changes the key writes every record through a repartition topic. If the key is already right, use groupByKey(). And make sure co-partitioned inputs (joins) have the same number of partitions, or Streams will refuse to start.'

steps = [
    ('Step 1 · Count per item',
     code('java', 'Kitchen92.java', 'KTable<String, Long> perItem = b.<String,String>stream("orders-92")   // key city, value item\n    .groupBy((city, item) -> item)\n    .count(Materialized.as("item-counts"));\nperItem.toStream().to("item-counts-92", Produced.with(Serdes.String(), Serdes.Long()));', sec('== 1)', '== 2)')),
     'First start: restore from empty changelogs (offsets 0..0), then the store holds dosa=2, idli=3, thali=1 for 6 orders.'),
    ('Step 2 · Hidden topics',
     code('bash', 'terminal', 'kafka-topics.sh --bootstrap-server k1:9092 --list | grep kitchen-92', sec('== 2)', '== 3)')),
     'groupBy created a repartition topic; count() created a compacted changelog topic.'),
    ('Step 3 · The table as a stream',
     code('bash', 'terminal', 'kafka-console-consumer.sh … --topic item-counts-92 --from-beginning --formatter-property value.deserializer=…LongDeserializer', sec('== 3)', '== 4)')),
     'Every update is a record: idli=1, then idli=2, then idli=3. A consumer that keeps the last value per key rebuilds the table.'),
    ('Step 4 · Restart with local state',
     code('bash', 'terminal', 'produce: Mumbai:dosa, Pune:thali, Delhi:idli\njava -cp "out:libs/*" Kitchen92 12000', sec('== 4)', '== 5)')),
     'The local RocksDB files were still there, so almost nothing to restore; counts continued to dosa=3, idli=4, thali=2.'),
    ('Step 5 · New machine',
     code('bash', 'terminal', 'rm -rf /tmp/kstate      # lose all local state\njava -cp "out:libs/*" Kitchen92 15000', sec('== 5)')),
     'The store was rebuilt from the changelog: 9 records restored, same answer. This is how a task survives moving to another machine.'),
]
see = [term([('restored 0', W), ('dosa=2 idli=3 thali=1', G)], size=7.0), term([('…-changelog (compact)', G), ('…-repartition', Y)], size=7.0),
       term([('idli=1 dosa=1 idli=2', W), ('thali=1 idli=3 dosa=2', W)], size=7.0), term([('dosa=3 idli=4 thali=2', G)], size=7.2),
       term([('rm -rf state', RD), ('restored 9 records', G), ('dosa=3 idli=4 thali=2', G)], size=7.0)]
B1 = [tbl([('idli', 3), ('dosa', 2), ('thali', 1)]), tbl([('idli', 3), ('dosa', 2), ('thali', 1)], True), tbl([('idli', 1), ('idli', 2), ('idli', 3)]),
      tbl([('idli', 4), ('dosa', 3), ('thali', 2)]), tbl([('idli', 4), ('dosa', 3), ('thali', 2)], True)]
B1 = [b + cap(c, '', tn, y=136, h=30) for b, c, tn in zip(B1, ['Counts in the store', 'Backed by a changelog', 'Updates as a stream', 'Continues after restart', 'Rebuilt from Kafka'], ['green', 'violet', 'blue', 'green', 'amber'])]
two = anim_two('KTables and state', 'Count, back up, restore', 'Real outputs from the lab', 'Stream → table', see, B1, ['Count.', 'Topics.', 'Updates.', 'Restart.', 'Restore.'], ['Store.', 'Hidden.', 'Changelog.', 'Continue.', 'Rebuild.'])
pe = peel('One order, layer by layer', '“Delhi: idli” arrives. (Simplified.)',
    [('Source', ''), ('Re-key', ''), ('Repartition', ''), ('Aggregate', ''), ('Changelog', ''), ('Downstream', '')],
    [['Source', 'orders-92', 'key Delhi', ''], ['Re-key', 'groupBy → idli', '', ''], ['Repartition', 'write to -repartition', 'read back by task owning idli', ''],
     ['Aggregate', 'store get idli=3', 'put idli=4', 'RocksDB'], ['Changelog', 'produce idli=4', '-changelog (compact)', ''], ['Downstream', 'toStream()', 'item-counts-92 idli=4', '']],
    ['Read.', 'Key.', 'Shuffle.', 'Count.', 'Back up.', 'Emit.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'Slow restart', '20 GB store restores for 30 min. (Typical.)', ('Standby replicas', 'Warm copies elsewhere'), [
    ('Instance dies', 'task moves', 'Restore from changelog.', 'red'), ('30 min restore', 'no output for that task', 'Lag.', 'red'),
    ('num.standby.replicas=1', 'shadow copy', 'Config.', 'green'), ('Failover to standby', 'seconds', 'Fast.', 'green'),
    ('Persistent volumes', 'keep RocksDB on restart', 'Faster still.', 'blue')], ['Die.', 'Wait.', 'Standby.', 'Switch.', 'Persist.'], 'scenario-standby') + \
       five('Real-time scenario 2', 'Query the counts', 'Dashboard wants item totals. (Typical.)', ('Interactive queries', 'Read state directly'), [
    ('Write to DB just to read?', 'extra system', 'Avoid.', 'amber'), ('streams.store("item-counts")', 'local read', 'Fast.', 'green'),
    ('Key on another instance', 'queryMetadataForKey', 'Route.', 'blue'), ('Small REST layer', 'per instance', 'Serve.', 'green'),
    ('Dashboard live', 'no DB', 'Done.', 'blue')], ['Avoid.', 'Read.', 'Route.', 'Serve.', 'Live.'], 'scenario-iq') + \
       five('Real-time scenario 3 · advanced', 'Hot key in repartition', 'One item dominates. (Typical.)', ('Skew', 'Repartition sends a key to one task'), [
    ('Diwali: 80% are sweets', 'one key', 'One task overloaded.', 'red'), ('Lag on one partition', 'others idle', 'Skew.', 'red'),
    ('Pre-aggregate', 'count per (item, random 0–9)', 'Spread.', 'green'), ('Second step sums', '10 sub-keys', 'Combine.', 'green'),
    ('Balanced tasks', 'lag gone', 'Done.', 'blue')], ['Spike.', 'Skew.', 'Salt.', 'Sum.', 'Even.'], 'scenario-skew')
assemble(HERE, h2_story='State that survives a crash', hook_html=hk,
    narration='The kitchen dashboard shows orders per item. Kabir planned an in-memory HashMap, until a pod restart wiped it.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='KTables and state stores',
    formal='A <b>KTable</b> is an abstraction of a changelog stream in which each record is an update (upsert) of the value for its key; a null value deletes the key. Aggregations (count, reduce, aggregate) and tables are materialized in <b>state stores</b> local to each task (RocksDB by default), which are made fault-tolerant by writing every update to a compacted <b>changelog topic</b> and restoring from it when a task starts on a new instance.',
    simple='A KTable keeps the latest value for each key, like a live tally. Kafka Streams stores it on local disk and also copies every change to a special Kafka topic, so it can be rebuilt anywhere.',
    term_rows=[('KTable', 'Latest value per key.'), ('State store', 'Local key-value storage.'), ('RocksDB', 'Default embedded store.'), ('Changelog topic', 'Backup of a store.'), ('Repartition topic', 'Shuffle by new key.'), ('Restore', 'Rebuild store from changelog.'), ('Standby replica', 'Warm copy on another instance.'), ('Interactive query', 'Read a store from the app.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('Stream state is lost on restart.', 'Rebuilt from the changelog.', 'Step 5: 9 restored.'),
               ('You need a database for counts.', 'State store + interactive queries.', 'Scenario 2.'),
               ('groupBy is free.', 'Re-keying costs a repartition topic.', 'Step 2.')],
    exam='“KStream vs KTable? How is state fault tolerant?” Stream = events, table = latest per key; aggregations in local RocksDB stores per task; compacted changelog topic; restore on failover; standby replicas; groupBy re-key → repartition topic; interactive queries.',
    types_h2='Streams, tables and internal topics', types_html=types_html, warn=warn,
    steps_h2='Count, back up, restore', steps_intro='All outputs are real: Kafka Streams 4.4.0 against the 3-broker lab; record cache set to 0 to show every update.',
    steps=steps, two=two, peel_intro='Now peel one order.', peel_html=pe,
    scen_intro='Three live scenarios: slow restore, queries, and a hot key.', scen=scen,
    uc_h2='Tables at work', ucs=[uc_('count', 'counters', 'blue', '1. Live counters', 'Orders per item, per city.', ['Events', '*count', 'Dashboard']),
        uc_('cart', 'carts', 'green', '2. Shopping carts', 'Latest cart per user.', ['Cart events', '*aggregate', 'Cart']),
        uc_('dedup', 'dedupe', 'violet', '3. Deduplication', 'Remember seen ids.', ['Events', '*store', 'Unique']),
        uc_('view', 'views', 'amber', '4. Materialized views', 'Service reads state directly.', ['Topics', '*KTable', 'API'])],
    uc_note='Examples are simplified descriptions of common practice.',
    pre='<b>Before you start:</b> <a href="../01-kafka-streams/">9.1 Kafka Streams</a>.')
