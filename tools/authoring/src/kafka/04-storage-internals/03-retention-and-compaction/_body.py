import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
R, K = 'l43_retention.txt', 'l43_compact.txt'
def sec(c, a, b=None, drop=()):
    return capsec(c, a, b, drop)
B = '../../'
hk = hook('We wrote 10 menu price changes. A minute later Kafka kept only 3. Nothing was lost.',
    'Kafka has two ways to clean up. <b>Retention</b> deletes whole old segments by time or size: we watched four segments vanish and the log start jump from 0 to 301. <b>Compaction</b> keeps only the latest value for each key: thali went 120 → 130 → 140 → 150 and only 150 remained, and a “deleted” dish disappeared completely.',
    ['When a “7-day” topic really deletes data.',
     'How compaction turns a topic into a latest-value table.',
     'What a tombstone is and why it also disappears later.'])
cmap = concept_map('Concept map. Beginner: retention, compaction, cleanup.policy. Intermediate: retention.ms and bytes, log start offset, latest value per key, tombstones. Advanced: log cleaner, dirty ratio, delete.retention.ms, compact plus delete.',
    [[('rt', 'Retention', 'delete old', None), ('cp', 'Compaction', 'keep latest per key', None), ('po', 'cleanup.policy', 'delete / compact', None)],
     [('tm', 'retention.ms / .bytes', 'time / size', None), ('ls', 'Log start offset', 'moves forward', B + '03-consumers/03-offsets-commits-and-lag/'), ('lv', 'Latest value per key', 'table view', None), ('tb', 'Tombstones', 'null value', None)],
     [('lc', 'Log cleaner', 'background threads', None), ('dr', 'Dirty ratio + lags', 'when to clean', None), ('cd', 'compact,delete', 'both', None)]],
    [('rt', 'tm'), ('tm', 'ls'), ('cp', 'lv'), ('lv', 'tb'), ('po', 'rt'), ('po', 'cp'), ('cp', 'lc'), ('lc', 'dr'), ('tb', 'cd')],
    {'rt', 'cp', 'po', 'tm', 'ls', 'lv', 'tb', 'lc', 'dr'},
    '<b>Builds on:</b> <a href="../01-the-commit-log-and-segments/">4.1 Segments</a>. <b>Next:</b> <a href="../04-tiered-storage-and-zero-copy/">4.4 Tiered storage and zero-copy</a>.')
whw = why_how_where(
    'Disks are finite, and some topics represent “current state” (prices, profiles) where old versions are noise.',
    'delete policy: remove closed segments older than retention.ms or beyond retention.bytes. compact policy: a cleaner rewrites old segments keeping the newest record per key; null values (tombstones) delete keys.',
    'Event streams (orders, clicks): delete. State/changelog topics (prices, user profiles, Kafka Streams changelogs, __consumer_offsets): compact.',
    'Compaction needs keys and does not keep history; retention deletes even unread data, so slow consumers can lose records.')

sc_ = (t(160, 18, 'retention: delete old segments', 8.8, 'red', bold=True) + ''.join(box(14 + k * 58, 32, 52, 30, 'red' if k < 4 else 'green', rx=4) + t(40 + k * 58, 51, ['0', '100', '200', '300', '301'][k], 8, 'ink', mono=True) for k in range(5)) +
       t(160, 80, 'log start 0 → 301 after 60 s retention', 8, 'ink2') +
       t(480, 18, 'compaction: latest value per key', 8.8, 'green', bold=True) +
       ''.join(box(334 + k * 26, 32, 23, 30, 'green' if k in (6, 7, 8) else 'card', rx=3) + t(345.5 + k * 26, 51, ['T', 'D', 'T', 'L', 'D', 'T', 'L', 'D', 'T', 'V', '∅'][k], 8, 'ink', bold=True) for k in range(11)) +
       t(480, 80, 'thali 150 · dosa 90 · lassi 45 kept; vada deleted', 8, 'ink2') +
       box(14, 96, 612, 30, 'card', rx=6) + t(320, 115, 'Both work on closed segments; offsets never change, they just disappear', 8.4, 'ink', bold=True))
scene_svg = scene('Left: retention deleted segments 0, 100, 200 and 300, moving the log start offset to 301. Right: compaction of 11 records kept only the latest thali, dosa and lassi prices and removed vada after its tombstone.', sc_,
                  'Two clean-up policies: <tspan font-weight="700" class="s-acc">by age</tspan> or <tspan font-weight="700" class="s-acc">by key</tspan>.')
dialogue = '''R> Sir, if Kafka never deletes on read, won’t the disk fill up?
A> It deletes by <b>retention</b>: whole old segments, by age or size. Orders older than 7 days simply vanish, read or not.
K> But for our menu prices we only care about the current price of each dish.
A> Then use <b>compaction</b>: Kafka keeps the latest value per key and throws away older versions. And to remove a dish you send a <b>tombstone</b>: the key with a null value. Let’s watch both happen.'''

lv = '''
LEVELS> Clean-up at three levels
L1> Two kinds of cupboards
      <ul>
        <li><b>Retention</b>: a newspaper rack that throws out papers older than a week. <b>Compaction</b>: a price board where writing a new price wipes the old one; erasing a dish removes its line.</li>
      </ul>
L2> The settings
      <ul>
        <li><code>cleanup.policy=delete</code> (default): <code>retention.ms</code> (7 days) and/or <code>retention.bytes</code> (unlimited) per partition. Only closed segments are deleted; the log start offset moves forward.</li>
        <li><code>cleanup.policy=compact</code>: keeps the last record for every key; a record with a <b>null value</b> is a tombstone that deletes the key.</li>
        <li><code>cleanup.policy=compact,delete</code>: compact and also drop old segments by retention.</li>
      </ul>
L3> The log cleaner
      <ul>
        <li>Background cleaner threads pick partitions whose “dirty” (uncleaned) share exceeds <code>min.cleanable.dirty.ratio</code> (0.5) and whose records are older than <code>min.compaction.lag.ms</code>; <code>max.compaction.lag.ms</code> forces cleaning.</li>
        <li>The active segment is never cleaned. Tombstones are kept for <code>delete.retention.ms</code> (1 day) so slow consumers see the deletion, then removed.</li>
        <li>Retention checks run every <code>log.retention.check.interval.ms</code> (5 min) on the broker; deleted files are first renamed <code>.deleted</code> and removed after <code>file.delete.delay.ms</code> (1 min).</li>
      </ul>
/LEVELS
'''
DIS = figure('Dissection of compaction on topic menu-prices: offsets 0 to 10 with keys thali, dosa, lassi and vada; after cleaning only offsets 6 lassi 45, 7 dosa 90 and 8 thali 150 remain, with original offsets kept.',
    t(16, 22, 'Before compaction (11 records)', 8.6, 'ink', anchor='start', bold=True) +
    fields(16, 32, [('0 thali=120', 'card', None), ('1 dosa=80', 'card', None), ('2 thali=130', 'card', None), ('3 lassi=40', 'card', None), ('4 dosa=85', 'card', None), ('5 thali=140', 'card', 1)], size=7.2) +
    fields(16, 62, [('6 lassi=45', 'green', None), ('7 dosa=90', 'green', None), ('8 thali=150', 'green', 2), ('9 vada=30', 'amber', None), ('10 vada=NULL', 'red', 3)], size=7.2) +
    t(16, 104, 'After the cleaner', 8.6, 'ink', anchor='start', bold=True) + fields(16, 114, [('6 lassi=45', 'green', None), ('7 dosa=90', 'green', None), ('8 thali=150', 'green', 4)], size=7.2) +
    legend(16, 162, [(1, 'Old versions', 'superseded by a later record with the same key'), (2, 'Latest per key', 'kept forever (while the key exists)'),
                     (3, 'Tombstone', 'null value: delete vada; removed itself after delete.retention.ms'), (4, 'Offsets kept', '6, 7, 8 keep their numbers; gaps are normal')], size=8, gap=15, w=110),
    h=232, caption='Real records from our lab topic menu-prices.')
extra = '''

  <h3>Dissect a compaction</h3>
''' + DIS

types_html = table(['Policy', 'Keeps', 'Typical topics', 'Key needed?'], [
    ['delete', 'everything newer than retention', 'orders, clicks, logs', 'no'],
    ['compact', 'latest record per key', 'prices, profiles, changelogs, __consumer_offsets', 'yes'],
    ['compact,delete', 'latest per key, but nothing older than retention', 'session state, caches', 'yes'],
], minw=600) + table(['Setting', 'Default', 'Meaning'], [
    ['retention.ms', '604800000 (7 days)', 'delete segments older than this (-1 = forever)'],
    ['retention.bytes', '-1 (no limit)', 'per-partition size cap'],
    ['min.cleanable.dirty.ratio', '0.5', 'compact when this share is uncleaned'],
    ['min.compaction.lag.ms / max.compaction.lag.ms', '0 / ∞', 'how soon a record may / must be compacted'],
    ['delete.retention.ms', '86400000 (1 day)', 'how long tombstones stay'],
], minw=600)
warn = 'Retention deletes data <b>whether or not anyone has read it</b>. A consumer group that falls more than retention.ms behind will find its offset gone (OFFSET_OUT_OF_RANGE) and jump according to <code>auto.offset.reset</code>, silently skipping data. Alert on lag well before that.'

steps = [
    ('Step 1 · A topic with 60-second retention',
     code('python', 'l43_ret_start.py', 'fresh("ret-43", 1, 3, {"retention.ms": "60000", "segment.ms": "10000"})\n# 3 waves of 100 records, 15 s apart, so segments roll', sec(R, '== 1)', '== 2)')),
     '<code>segment.ms=10000</code> made each wave close its own segment: base offsets 0, 100, 200, 300. Log start is 0.'),
    ('Step 2 · Two minutes later',
     code('bash', 'terminal', 'ls /var/lib/kafka/data/ret-43-0/\nkafka-get-offsets.sh --topic ret-43 --time -2      # log start offset', sec(R, '== 2)', '== 3)')),
     'At the next retention check the old segments were renamed <code>.deleted</code> (removed a minute later) and the <b>log start offset</b> jumped to 301. A group still at offset 50 would now be out of range.'),
    ('Step 3 · The broker explains',
     code('bash', 'terminal', 'docker logs k1 | grep "Deleting segment"', sec(R, '== 3)')),
     'Retention is judged per segment by its <b>largest record timestamp</b>: a segment is deleted only when even its newest record is older than retention.ms.'),
    ('Step 4 · A compacted topic',
     code('python', 'l43_compact.py', 'fresh("menu-prices", 1, 3, {"cleanup.policy": "compact", "segment.ms": "5000",\n      "min.cleanable.dirty.ratio": "0.01", "delete.retention.ms": "5000"})\nfor k, v in updates: p.produce(T, key=k, value=v)\np.produce(T, key="vada", value=None)          # tombstone', sec(K, '== 2)', '== 3)')),
     'Ten price updates for four dishes plus a tombstone for vada. Right after writing, everything is still there, because only closed segments are cleaned.'),
    ('Step 5 · After the cleaner',
     code('python', 'l43_compact.py', '# keep producing small "tick" records so segments roll, wait ~50 s, read again', sec(K, '== 3)')),
     'Only the latest price per dish survives (offsets 6, 7, 8), and vada is gone entirely: first its old value was removed, then, after <code>delete.retention.ms</code>, the tombstone too. The cleaner’s log shows it rewriting the segment.'),
]

see = [term([('…0000.log …0100.log …0200.log …0300.log', W), ('log start: ret-43:0:0', W)], size=6.8),
       term([('…0000.log.deleted … …0300.log.deleted', RD), ('…0301.log', G), ('log start: ret-43:0:301', G)], size=6.8),
       term([('Deleting segment baseOffset=0', W), ('due to log retention time 60000ms', Y), ('breach', Y)], size=7.0),
       term([('0:thali=120 1:dosa=80 2:thali=130', W), ('… 8:thali=150 9:vada=30 10:vada=NULL', W)], size=6.8),
       term([('6:lassi=45 7:dosa=90 8:thali=150', G), ('Cleaner 0: Swapping in cleaned segment', W)], size=6.8)]
def segs(gone, title, tone):
    return t(180, 14, title, 9, bold=True) + ''.join(box(10 + k * 68, 50, 60, 34, 'red' if k < gone else 'green', rx=4) + t(40 + k * 68, 71, ['0', '100', '200', '300', '301'][k], 8, 'ink', mono=True) for k in range(5)) + cap(title, '', tone, y=144, h=30)
def keys(after, title, tone):
    ks = ['T', 'D', 'T', 'L', 'D', 'T', 'L', 'D', 'T', 'V', '∅']
    show = [k for k in range(11) if not after or k in (6, 7, 8)]
    return t(180, 14, title, 9, bold=True) + ''.join(box(10 + i * 31, 50, 27, 34, 'green' if k in (6, 7, 8) else 'card', rx=3) + t(23 + i * 31, 71, ks[k], 8, 'ink', bold=True) for i, k in enumerate(show)) + cap(title, '', tone, y=144, h=30)
B1 = [segs(0, 'Four closed segments', 'blue'), segs(4, 'Retention deletes whole segments', 'red'), segs(4, 'Judged by newest record time', 'amber'), keys(False, 'Many versions per key', 'blue'), keys(True, 'Latest per key only', 'green')]
two = anim_two('Retention and compaction', 'Delete by age, keep by key', 'Real outputs from the lab', 'What remains on disk', see, B1, ['Before.', 'Deleted.', 'Why.', 'Versions.', 'Compacted.'], ['Segments.', 'Log start moves.', 'Timestamp.', 'Keys.', 'Table.'])
pe = peel('One log-cleaner pass', 'How compaction rewrites a segment. (Simplified.)',
    [('Pick partition', ''), ('Build offset map', ''), ('Copy survivors', ''), ('Tombstones', ''), ('Swap', ''), ('Delete old', '')],
    [['Pick partition', 'dirty ratio ≥ 0.01 here', 'and records old enough', ''], ['Build offset map', 'scan the dirty part:', 'key → latest offset', 'thali → 8, dosa → 7'],
     ['Copy survivors', 'rewrite old segments', 'keep a record only if it is', 'the latest for its key'], ['Tombstones', 'vada=NULL kept until', 'delete.retention.ms', 'then dropped too'],
     ['Swap', 'cleaned segment', 'replaces the old ones', '(.cleaned → .swap)'], ['Delete old', 'old files removed', 'offsets unchanged', 'gaps are normal']],
    ['Choose.', 'Map.', 'Copy.', 'Tombstones.', 'Swap.', 'Clean.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'Consumer fell off the end', 'Retention vs lag. (Typical.)', ('Retention and lag', 'Lag beyond retention means silent data loss for that group'), [
    ('Analytics down 9 days', 'retention 7 days', 'Offsets gone.', 'red'), ('OFFSET_OUT_OF_RANGE', 'auto.offset.reset=latest', 'Skips 2 days.', 'red'),
    ('Reports wrong', 'nobody noticed', 'Silent.', 'red'), ('Alert on lag age', 'well before retention', 'Early warning.', 'green'),
    ('Longer retention or tiered', 'for slow consumers', 'Lesson 4.4.', 'blue')], ['Down.', 'Out of range.', 'Impact.', 'Alert.', 'Fix.'], 'scenario-outofrange') + \
       five('Real-time scenario 2', 'A price table from a topic', 'Compaction as a changelog. (Typical.)', ('Compacted topics', 'Rebuild current state by reading a compacted topic from the start'), [
    ('Menu service restarts', 'needs all current prices', 'From where?', 'blue'), ('Read menu-prices from start', 'compacted', 'Small.', 'green'),
    ('One record per dish', 'latest price', 'Fast rebuild.', 'green'), ('Deleted dishes absent', 'tombstones', 'Correct.', 'green'),
    ('Same idea as Streams changelogs', '__consumer_offsets too', 'Pattern.', 'blue')], ['Restart.', 'Read.', 'Latest.', 'Deleted.', 'Pattern.'], 'scenario-changelog') + \
       five('Real-time scenario 3 · advanced', 'GDPR delete request', 'Erasing a customer from Kafka. (Typical.)', ('Tombstones and erasure', 'Compaction plus tombstones can remove a key; deleted-policy topics cannot'), [
    ('Customer asks for erasure', 'profile topic', 'Must delete.', 'blue'), ('Compacted profiles', 'send tombstone for id', 'Key removed after cleaning.', 'green'),
    ('Event topics (delete policy)', 'old events stay until retention', 'Plan retention.', 'amber'), ('Or crypto-shredding', 'encrypt per customer, drop key', 'Common pattern.', 'green'),
    ('Document the process', 'with timings', 'Audit.', 'blue')], ['Request.', 'Tombstone.', 'Events.', 'Shred.', 'Document.'], 'scenario-gdpr')
assemble(HERE, h2_story='Ten prices in, three prices out', hook_html=hk,
    narration='TiffinGo keeps orders for 7 days, but for the menu it only needs today’s price of each dish. Kabir sets up two topics with different clean-up policies and watches what Kafka throws away.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Retention and compaction',
    formal='Kafka bounds log growth with a per-topic <b>cleanup.policy</b>. With <code>delete</code>, closed segments whose newest timestamp is older than <code>retention.ms</code>, or that exceed <code>retention.bytes</code>, are removed and the log start offset advances. With <code>compact</code>, the <b>log cleaner</b> rewrites closed segments to retain at least the last record for every key, deleting keys whose latest record is a <b>tombstone</b> (null value) after <code>delete.retention.ms</code>. Offsets of retained records never change.',
    simple='Retention throws away old files by age or size. Compaction keeps just the newest value for each key, like a table of current prices, and a record with an empty value deletes that key.',
    term_rows=[('cleanup.policy', 'delete, compact or both.'), ('retention.ms', 'Max age of data.'), ('retention.bytes', 'Max size per partition.'), ('Log start offset', 'Oldest offset still kept.'), ('Compaction', 'Keep latest record per key.'), ('Tombstone', 'Key with null value = delete.'), ('Log cleaner', 'Background compaction threads.'), ('Dirty ratio', 'Share not yet compacted.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('Retention deletes records exactly at retention.ms.', 'It deletes whole closed segments at the next check, judged by the newest record.', 'Steps 1–3.'),
               ('Compaction changes offsets.', 'Offsets stay; there are just gaps.', 'Step 5: 6, 7, 8.'),
               ('A tombstone stays forever.', 'It is removed after delete.retention.ms.', 'Step 5: vada fully gone.')],
    exam='“Retention vs compaction?” delete policy removes closed segments older than retention.ms or above retention.bytes (log start moves); compact keeps the latest record per key via the log cleaner, tombstones delete keys after delete.retention.ms; compact,delete combines them; active segment never cleaned.',
    types_h2='Policies and settings', types_html=types_html, warn=warn,
    steps_h2='Watch Kafka clean up', steps_intro='All outputs are real: Kafka 4.4.0, 3 brokers; topic <code>ret-43</code> (retention 60 s, segments every 10 s) and compacted topic <code>menu-prices</code> (aggressive cleaner settings for the demo). Scripts: <code>jobs/m4/l43_ret_start.py</code>, <code>l43_compact.py</code>.',
    steps=steps, two=two, peel_intro='Now peel one log-cleaner pass.', peel_html=pe,
    scen_intro='Three live scenarios: falling off the end, a price table, and a deletion request.', scen=scen,
    uc_h2='Clean-up policies at work', ucs=[uc_('orders', 'delete', 'blue', '1. Event streams', '7–30 days retention for orders and clicks.', ['Events', '*delete', 'Bounded disk']),
        uc_('prices', 'compact', 'green', '2. Reference data', 'Latest price, stock or profile per key.', ['Updates', '*compact', 'Table']),
        uc_('offsets', 'internal', 'violet', '3. __consumer_offsets', 'Compacted: latest commit per group-partition.', ['Commits', '*compact', 'Bookmarks']),
        uc_('streams', 'state', 'acc', '4. Kafka Streams changelogs', 'State stores restore from compacted topics (Module 9).', ['Store', '*changelog', 'Restore']),
        uc_('CDC', 'tables', 'blue', '5. Database change streams', 'Compacted CDC topics hold the latest row per primary key.', ['DB rows', '*compact', 'Snapshot'])],
    uc_note='Demo settings (60 s retention, 0.01 dirty ratio) are only for the lab.',
    pre='<b>Before you start:</b> <a href="../01-the-commit-log-and-segments/">4.1 Segments</a>.')
