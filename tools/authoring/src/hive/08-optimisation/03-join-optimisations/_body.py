import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()
def plain(n, start=0, end=None):
    lines = [l for l in capf(n).split('\n') if l.startswith('| ')]
    lines = [re.sub(r'\s*\|$', '', l[2:]).rstrip() for l in lines]
    lines = [l for l in lines if l.strip() not in ('Explain',)]
    return '\n'.join(lines[start:end]).strip('\n')
def pick(n, keys):
    return '\n'.join(l for l in plain(n).split('\n') if any(k in l for k in keys))
def summ(n):
    return '\n'.join(l for l in capf(n).split('\n') if not l.startswith('|'))

def opbox(x, y, label, sub='', tone='card', w=128, h=26):
    o = box(x, y, w, h, tone) + t(x + w / 2, y + (11 if sub else 16), label, 7.2, 'ink', bold=True)
    if sub:
        o += t(x + w / 2, y + 21, sub, 6.4, 'ink2', mono=True)
    return o

# ---------------------------------------------------------------- story
sc = (box(10, 12, 196, 128, 'card') + t(108, 30, 'Same join, four plans', 8.8, bold=True) +
      ''.join(opbox(22, 40 + k * 24, a, b, tone, 172, 20) for k, (a, b, tone) in enumerate([('Shuffle (merge) join', '342,929 bytes shuffled', 'red'), ('Map join', 'small side broadcast', 'green'), ('Bucket map join', '8 tasks, bucket i ↔ i', 'blue'), ('SMB join', 'merge sorted buckets', 'violet')])) +
      arrow(212, 76, 252, 76, 'acc', 2.2) + box(258, 46, 110, 60, 'acc') + t(313, 72, 'Optimiser', 8.4, bold=True) + t(313, 88, 'chooses', 8.4, bold=True) +
      arrow(374, 76, 410, 76, 'acc', 2.2) + box(416, 12, 214, 128, 'amber') + t(523, 30, 'It decides from', 8.8, bold=True) +
      ''.join(t(430, 54 + k * 18, s, 7.4, 'ink2', anchor='start', mono=True) for k, s in enumerate(['estimated size of each side', 'bucketing + sorting metadata', 'table type (managed/external)', 'settings and thresholds'])))
scene_svg = scene('One join between orders and customers can run as a shuffle join, a map join, a bucket map join or a sort-merge-bucket join. The optimiser chooses from estimated sizes, bucketing and sorting metadata, table type and settings.', sc,
                  'The fastest join is the one that <tspan font-weight="700" class="s-acc">moves the least data</tspan>.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Can we make the join stop shuffling?”</h2>
  <div class="story">
    <p class="narration">TiffinGo’s biggest nightly job joins orders with customers. Kabir read the plan (Lesson 8.1) and fixed the statistics (Lesson 8.2). Now the team wants to know which join methods Hive has and how to get the fast ones.</p>

{scene_svg}

K> Sir, Lesson 5.3 said bucketing gives faster joins. But my plan still broadcasts.
A> Hive has four join methods. A <b>shuffle join</b> sends both tables across the network by key. A <b>map join</b> copies the small table to every task and skips the shuffle. A <b>bucket map join</b> loads only the matching bucket. An <b>SMB join</b> merges sorted buckets without any hash table. Each has conditions, and Hive is strict about them.
R> And skew? One corporate customer has 40% of the orders.
A> We will build that table, see what Hive’s skew settings do on Tez (in our lab: nothing), and fix it by hand. Every plan and counter today is real, from Hive 4.2.1, including the conditions that made bucket joins finally appear.
  </div>
</section>
'''

lv = '''
LEVELS> Join optimisation at three levels
L1> Matching two lists
      <ul>
        <li>To join orders with customers, Hive must bring each order and its customer to the same place.</li>
        <li><b>Shuffle join:</b> both lists are sorted into piles by customer_id and sent over the network. Works for any size, but moves a lot of data.</li>
        <li><b>Map join:</b> if one list is small, give a full copy to every worker. No piles needed.</li>
      </ul>
L2> The four methods and their conditions
      <ul>
        <li><b>Shuffle (common / merge) join:</b> default fallback. Both sides go through SIMPLE_EDGE to a reducer running <code>Merge Join Operator</code>.</li>
        <li><b>Map (broadcast) join:</b> small side under <code>hive.auto.convert.join.noconditionaltask.size</code> (10,000,000 bytes in our lab); <code>BROADCAST_EDGE</code>, <code>Map Join Operator</code>.</li>
        <li><b>Bucket map join:</b> both tables bucketed on the join key with compatible counts; each big-table task gets only its bucket of the small table (<code>CUSTOM_EDGE</code>, <code>BucketMapJoin:true</code>).</li>
        <li><b>SMB join:</b> both bucketed <i>and sorted</i> on the key, same bucket count: merge bucket i with bucket i inside the map task (<code>Merge Join Operator</code> + <code>Dummy Store</code>).</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>Bucketed, sorted <b>external</b> tables never got a bucket map or SMB join; <b>managed</b> transactional tables did.</li>
        <li>Full ACID tables cannot be <code>SORTED BY</code> (“cannot support full ACID functionality since it is sorted”); SMB worked with insert-only tables.</li>
        <li>Shuffle join moved 342,929 bytes vs 31,867 for the map join. <code>/*+ MAPJOIN */</code> hints are ignored by default. Skew settings did not change the Tez plan; splitting the hot key did the job.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Join optimisations in Hive</h2>
''' + def_block(
    'Hive executes an equi-join with one of several physical algorithms. The <b>shuffle (common) join</b> repartitions both inputs by the join key and joins them in reducers. A <b>map join</b> (broadcast join) loads the smaller input into an in-memory hash table on every task processing the larger input, avoiding the shuffle; Hive converts joins automatically when the estimated size of the small inputs is below <code>hive.auto.convert.join.noconditionaltask.size</code>. When both tables are bucketed on the join key, a <b>bucket map join</b> sends each task only the matching bucket of the small table, and when they are also sorted on the key with the same number of buckets, a <b>sort-merge-bucket (SMB) join</b> merges the buckets directly. <b>Skew join</b> handling separates heavily repeated keys so they do not overload one task.',
    'Hive can join tables in different ways. The slow, general way sends both tables over the network. Faster ways copy a small table to every worker, or use matching buckets so each worker only needs a slice. The plan shows which one Hive picked.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Shuffle join', 'Both sides repartitioned by key to reducers (Merge Join Operator).'),
    ('Map join', 'Small side broadcast; join in the map task (Map Join Operator).'),
    ('Bucket map join', 'Each task loads only the matching bucket of the small side.'),
    ('SMB join', 'Sort-merge-bucket: merge sorted buckets, no hash table.'),
    ('Big / small table', 'The side streamed vs the side held in memory.'),
    ('Skew', 'A few key values with far more rows than the rest.'),
    ('Hot key', 'One very frequent key, e.g. a corporate customer.'),
    ('Semi-join reduction', 'Bloom/min-max filter from one side applied to the other’s scan.'),
]) + '''

  <h3>Choosing a join</h3>
''' + table(['Join', 'Needs', 'Plan clue', 'Lab result'], [
    ['Shuffle (merge) join', 'Nothing', '<code>Reducer n &lt;- Map a, Map b (SIMPLE_EDGE)</code>', '342,929 bytes shuffled'],
    ['Map join', 'Small side under the size threshold', '<code>BROADCAST_EDGE</code>, Map Join Operator', '31,867 bytes; 3 tasks'],
    ['Bucket map join', 'Both bucketed on key; managed tables', '<code>CUSTOM_EDGE</code>, <code>BucketMapJoin:true</code>', '8 map tasks, one per bucket'],
    ['SMB join', 'Bucketed + sorted, same buckets; not full ACID', 'Merge Join in Map, <code>Dummy Store</code>', 'No shuffle for the join'],
    ['Skew handling', 'Hot keys known', 'Manual split / UNION ALL in our lab', 'Same result, hot key isolated'],
], minw=760) + lv + '''
EXAM> “Explain map join, bucket map join and SMB join.” Map join: small table copied to every task, no shuffle; automatic below a size threshold. Bucket map join: both tables bucketed on the join key (compatible counts); each task loads only its bucket of the small table. SMB: both bucketed and sorted on the key with the same bucket count; buckets are merged, so neither side must fit in memory. Verify in EXPLAIN.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Settings that control joins</h2>
''' + table(['Setting', 'Lab value', 'Meaning'], [
    ['<code>hive.auto.convert.join</code>', 'true', 'Convert to map join when the small side is small enough'],
    ['<code>hive.auto.convert.join.noconditionaltask.size</code>', '10000000', 'Bytes allowed for the small side(s)'],
    ['<code>hive.convert.join.bucket.mapjoin.tez</code>', 'true', 'Allow bucket map join on Tez'],
    ['<code>hive.auto.convert.sortmerge.join</code>', 'true', 'Allow SMB join conversion'],
    ['<code>hive.ignore.mapjoin.hint</code>', 'true', '<code>/*+ MAPJOIN(x) */</code> hints are ignored'],
    ['<code>hive.optimize.skewjoin</code> / <code>.compiletime</code>', 'false / false', 'Skew join handling (no plan change on Tez in our lab)'],
    ['<code>hive.skewjoin.key</code>', '100000', 'Rows per key treated as skewed (runtime skew join)'],
    ['<code>hive.tez.dynamic.semijoin.reduction</code>', 'true', 'Bloom-filter semi-join reduction when worthwhile'],
], minw=720) + '''
WARN> Turning <code>hive.auto.convert.join</code> off to “be safe” forces shuffle joins everywhere: 10× more shuffled bytes in our lab. Fix the statistics or lower the threshold for one query instead.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Four join methods, real plans and counters</h2>
  <p>All outputs are real, from the Hive 4.2.1 lab. Plans keep the lines that identify the join; counters come from <code>SET hive.tez.exec.print.summary=true</code>.</p>
''' + stepper([
    ('Step 1 · Shuffle (merge) join',
     code('sql', 'Beeline', "SET hive.auto.convert.join=false;\nEXPLAIN SELECT c.city, COUNT(*), SUM(o.amount)\nFROM orders o JOIN customers c ON o.customer_id = c.customer_id GROUP BY c.city;", pick('l83_shuffle.txt', ('<-', 'Join', 'TableScan'))),
     'Both tables are read by their own map vertex (Map 1, Map 4) and <b>shuffled</b> by customer_id (SIMPLE_EDGE) into Reducer 2, where the <code>Merge Join Operator</code> joins rows with the same key. A third vertex groups by city. This works for any size, but every row of both tables crosses the network.'),
    ('Step 2 · Map join (the default here)',
     code('sql', 'Beeline', "EXPLAIN SELECT c.city, COUNT(*), SUM(o.amount)\nFROM orders o JOIN customers c ON o.customer_id = c.customer_id GROUP BY c.city;", pick('l83_mj.txt', ('<-', 'Join', 'TableScan'))),
     'With the default settings customers (2,000 rows) is under the 10,000,000-byte limit, so Map 3 <b>broadcasts</b> it to every task of Map 1, which joins in memory. The join needs no reducer; one shuffle remains for GROUP BY.'),
    ('Step 3 · Measure it: counters of both runs',
     code('sql', 'Beeline', "SET hive.tez.exec.print.summary=true;\n-- run the query once with the map join, once with hive.auto.convert.join=false", '-- map join\n' + summ('l83_sum_mj.txt') + '\n\n-- shuffle join\n' + summ('l83_sum_sj.txt')),
     'Same 8 result rows. The shuffle join sends all <b>52,000</b> rows to Reducer 2 and moves <b>342,929</b> bytes; the map join sends 8 partial results and 31,867 bytes (mostly the broadcast copy of customers): <b>10.8× less</b>. Map 1’s 52,000 input records in the map join include the 2,000 broadcast rows. Durations on 50,000 rows are mostly start-up overhead, so compare bytes and records, not milliseconds.'),
    ('Step 4 · Hints are ignored',
     code('sql', 'Beeline', "SET hive.ignore.mapjoin.hint;   -- true\nEXPLAIN SELECT /*+ MAPJOIN(o) */ c.city, SUM(o.amount)\nFROM orders o JOIN customers c ON o.customer_id = c.customer_id GROUP BY c.city;", pick('l83_hint.txt', ('<-', 'Join', 'rows=50000'))),
     'The hint asked Hive to hold <b>orders</b> (50,000 rows) in memory. Hive ignored it and still streamed orders (SEL_25, rows=50000) and broadcast customers. Old tutorials rely on <code>MAPJOIN</code> and <code>STREAMTABLE</code> hints; in Hive 4 the cost-based decision wins unless you set <code>hive.ignore.mapjoin.hint=false</code>.'),
    ('Step 5 · Bucketed external tables: still a broadcast',
     code('sql', 'Beeline', "-- orders_bkt, customers_bkt: EXTERNAL, CLUSTERED BY (customer_id) SORTED BY (customer_id) INTO 8 BUCKETS\nSET hive.auto.convert.join.noconditionaltask.size=20000;\nSET hive.optimize.bucketmapjoin=true; SET hive.optimize.bucketmapjoin.sortedmerge=true;\nEXPLAIN SELECT … FROM orders_bkt o JOIN customers_bkt c ON …;", '-- default settings\n' + pick('l83_bkt_default.txt', ('<-', 'Join')) + '\n\n-- small threshold + bucket settings\n' + pick('l83_bkt_forced.txt', ('<-', 'Join'))),
     'This is why Lesson 5.3 never saw a bucket join. With default settings the bucketed tables got an ordinary <b>broadcast</b>; with a small threshold and every bucket setting on, a <b>shuffle</b> merge join. In Hive 4.2.1 our <b>external</b> bucketed tables were never joined bucket by bucket, most likely because Hive cannot guarantee that files written outside it follow the bucketing.'),
    ('Step 6 · Bucket map join on managed tables',
     code('sql', 'Beeline', "CREATE TABLE ob_acid (order_id BIGINT, customer_id INT, amount DECIMAL(10,2), order_date DATE)\n  CLUSTERED BY (customer_id) INTO 8 BUCKETS STORED AS ORC TBLPROPERTIES ('transactional'='true');\nCREATE TABLE cb_acid (customer_id INT, city STRING, plan STRING)\n  CLUSTERED BY (customer_id) INTO 8 BUCKETS STORED AS ORC TBLPROPERTIES ('transactional'='true');\n-- INSERT … SELECT from orders / customers, then:\nEXPLAIN SELECT … FROM ob_acid o JOIN cb_acid c ON o.customer_id = c.customer_id GROUP BY c.city;", pick('l83_bmj.txt', ('<-', 'Join', 'MULTICAST')) + '\n\n-- run summary\n' + summ('l83_sum_bmj.txt')),
     'Now the plan says <code>CUSTOM_EDGE</code>, <code>MULTICAST</code> and <b><code>BucketMapJoin:true</code></b>. Map 1 ran <b>8 tasks</b>, one per bucket of orders (10 tasks in total), and each received only the customers of its own bucket: 64 partial rows = 8 tasks × 8 cities. Because each task holds one bucket, the plan stayed a bucket map join even with the 20,000-byte threshold; at 1,000 bytes Hive fell back to a shuffle join.'),
    ('Step 7 · SMB join: sorted buckets, merged in the map',
     code('sql', 'Beeline', "CREATE TABLE ob_acid (…) CLUSTERED BY (customer_id) SORTED BY (customer_id) INTO 8 BUCKETS\n  STORED AS ORC TBLPROPERTIES ('transactional'='true');      -- full ACID: refused\n\nCREATE TABLE ob_mm (…) CLUSTERED BY (customer_id) SORTED BY (customer_id) INTO 8 BUCKETS STORED AS ORC\n  TBLPROPERTIES ('transactional'='true','transactional_properties'='insert_only');   -- same for cb_mm\nSET hive.auto.convert.join.noconditionaltask.size=1000;\nEXPLAIN SELECT … FROM ob_mm o JOIN cb_mm c ON o.customer_id = c.customer_id GROUP BY c.city;", capf('l83_acid_sorted.txt').split('; Query ID')[0] + '\n\n' + pick('l83_smb.txt', ('<-', 'Join', 'Dummy', 'TableScan')) + '\n\n' + summ('l83_smb_summary.txt')),
     'Full ACID tables cannot be sorted, so we used <b>insert-only</b> transactional tables. With a threshold too small for any map join, Hive chose <b>SMB</b>: the vertex list has <b>no join shuffle</b> (only Reducer 2 for GROUP BY), and the <code>Merge Join Operator</code> runs <b>inside Map 1</b>, with customers read through a <code>Dummy Store</code>. 8 tasks merged bucket i of orders with bucket i of customers. Note that Map 1 is not marked <i>vectorized</i> here.'),
    ('Step 8 · A skewed key',
     code('sql', 'Beeline', "CREATE TABLE orders_skew STORED AS ORC AS SELECT order_id,\n  CASE WHEN order_id % 10 < 4 THEN 7 ELSE customer_id END AS customer_id, amount FROM orders;\nSELECT customer_id, COUNT(*) AS n FROM orders_skew GROUP BY customer_id ORDER BY n DESC LIMIT 3;\n\nSET hive.auto.convert.join=false; SET hive.optimize.skewjoin=true; SET hive.skewjoin.key=5000;\nALTER TABLE orders_skew SKEWED BY (customer_id) ON (7); SET hive.optimize.skewjoin.compiletime=true;\nEXPLAIN SELECT c.city, COUNT(*), SUM(o.amount) FROM orders_skew o JOIN customers c ON … GROUP BY c.city;", capf('l83_skewmk.txt') + '\n\n' + pick('l83_skewset.txt', ('<-', 'Join'))),
     'Customer 7 now has <b>20,016</b> of 50,000 orders; the next customer has 31. In a shuffle join, all 20,016 rows go to <b>one</b> reducer task while others idle. We switched on both skew-join settings and declared the skewed value: the Tez plan in Hive 4.2.1 <b>did not change</b> (the runtime skew join is a MapReduce-era feature). Two fixes worked: a map join (the default for this small dimension: no shuffle on the key at all), or splitting the hot key by hand, shown in the code section below.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('Reducer 2 <- Map 1 (SIMPLE_EDGE),', W), ('             Map 4 (SIMPLE_EDGE)', W), ('Merge Join Operator [MERGEJOIN_19]', G), ('Reducer 2  INPUT_RECORDS 52,000', Y), ('SHUFFLE_BYTES: 342929', RD)], size=7.6),
    term([('Map 1 <- Map 3 (BROADCAST_EDGE)', G), ('Map Join Operator [MAPJOIN_26]', G), ('Reducer 2  INPUT_RECORDS 8', G), ('SHUFFLE_BYTES: 31867', G)], size=7.6),
    term([('Map 1 <- Map 3 (CUSTOM_EDGE)', G), ('MULTICAST [RS_33]', G), ('BucketMapJoin:true', G), ('TOTAL_LAUNCHED_TASKS: 10', Y)], size=7.6),
    term([('Reducer 2 <- Map 1 (SIMPLE_EDGE)', G), ('Merge Join Operator [MERGEJOIN_29]', G), ('<-Dummy Store [DUMMY_STORE_30]', G), ('  tiffingo@cb_mm … transactional table', W)], size=7.4),
    term([('customer_id = 7    20,016 rows', RD), ('customer_id = 1044     31 rows', W), ('skewjoin settings on:', W), ('  plan unchanged', Y)], size=7.6),
]
def lanes(kind):
    o = ''
    for k in range(4):
        y = 44 + k * 22
        o += box(20, y, 70, 16, 'card') + t(55, y + 11, f'orders {k}', 6.8, 'ink', mono=True)
        if kind == 'shuffle':
            o += arrow(92, y + 8, 200, 44 + ((k * 3) % 4) * 22 + 8, 'red', 1.2)
        else:
            o += arrow(92, y + 8, 128, y + 8, 'green', 1.4)
        if kind in ('bucket', 'smb'):
            o += box(130, y, 70, 16, 'blue') + t(165, y + 11, f'cust {k}', 6.8, 'ink', mono=True)
        if kind == 'map':
            o += box(130, y, 70, 16, 'green') + t(165, y + 11, 'all cust', 6.8, 'ink', mono=True)
    if kind == 'shuffle':
        o += ''.join(box(202, 44 + k * 22, 70, 16, 'amber') + t(237, 55 + k * 22, f'reducer {k}', 6.8, 'ink', mono=True) for k in range(4))
    return o
B1 = [
    t(180, 22, 'Shuffle join: everything moves', 9.4, bold=True) + lanes('shuffle') + cap('Rows of both tables cross the network.', '', 'amber', y=150, h=34),
    t(180, 22, 'Map join: small side copied to all', 9.4, bold=True) + lanes('map') + cap('Big side stays; no shuffle for the join.', '', 'green', y=150, h=34),
    t(180, 22, 'Bucket map join: bucket i gets bucket i', 9.4, bold=True) + lanes('bucket') + cap('Each task holds 1/8 of the small table.', '', 'blue', y=150, h=34),
    t(180, 22, 'SMB: sorted buckets merged', 9.4, bold=True) + lanes('smb') + t(290, 80, 'merge', 8, 'violet', bold=True) + cap('No hash table: neither side must fit in memory.', '', 'violet', y=150, h=34),
    t(180, 22, 'Skew: one key, one overloaded task', 9.4, bold=True) + fill(40, 50, 260, 12, 'acc', rx=2) + t(40, 76, 'key 7: 20,016 rows → one reducer', 7.6, 'red', anchor='start', mono=True) + fill(40, 86, 4, 12, 'blue', rx=1) + t(50, 96, 'key 1044: 31 rows', 7.6, 'ink2', anchor='start', mono=True) + cap('Map join or a hot-key split avoids it.', '', 'amber', y=150, h=34),
]
see_caps = ['The shuffle join moved 342,929 bytes.',
            'The map join moved 31,867 bytes: 10.8× less.',
            'Managed bucketed tables got a bucket map join with 8 tasks.',
            'Sorted insert-only tables got an SMB join inside Map 1.',
            'One customer holds 40% of the skewed table.']
behind_caps = ['Both inputs are repartitioned by key so equal keys meet in one reducer.',
               'Every map task builds a hash table of the small side and streams the big side through it.',
               'Bucket i of the big table only needs bucket i of the small one.',
               'Sorted buckets are merged like two sorted lists.',
               'Hash partitioning sends every row of a key to the same task.']
two = anim_two('Join methods', 'How rows meet', 'Real plans and counters', 'Where the data moves', see, B1, see_caps, behind_caps)

# ---- scenario 1: OOM map join
m1 = (t(180, 22, 'Nightly job fails: “GC overhead / OOM” in Map 1', 9.4, bold=True) + t(180, 56, 'plan: BROADCAST_EDGE to a dimension', 8.2, 'ink2', mono=True) + cap('A map join that no longer fits.', '', 'amber', y=150, h=34))
m2 = (t(180, 22, 'Check the estimate', 9.4, bold=True) + t(180, 56, 'statistics: 5 MB · real table: 900 MB', 8.2, 'red', mono=True) + cap('Stale statistics (Lesson 8.2). Illustrative sizes.', '', 'amber', y=150, h=34))
m3 = (t(180, 22, 'Fix the cause', 9.4, bold=True) + t(180, 56, 'ANALYZE TABLE dim COMPUTE STATISTICS FOR COLUMNS', 7.8, 'ink', mono=True) + cap('Planner now picks a shuffle join.', '', 'green', y=150, h=34))
m4 = (t(180, 22, 'Or for this query only', 9.4, bold=True) + t(180, 56, 'SET hive.auto.convert.join.noconditionaltask.size=…', 7.6, 'ink', mono=True) + cap('Never switch auto.convert.join off globally.', '', 'blue', y=150, h=34))
m5 = (t(180, 22, 'Long term', 9.4, 'acc', bold=True) + t(180, 56, 'bucket both tables → bucket map join', 8.2, 'ink2') + cap('Each task holds 1/N of the dimension.', '', 'green', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'A map join runs out of memory',
              'A frequent production failure and its fixes. (Sizes illustrative; the mechanisms are those we measured.)',
              'Map join OOM', 'A dimension grew beyond what fits in memory; fresh statistics or bucketing restore a safe plan', [m1, m2, m3, m4, m5],
              ['Map tasks fail while building the hash table.',
               'The estimate says small, the table is big.',
               'Refresh statistics so the planner sees the real size.',
               'Override the threshold for one query if needed.',
               'Bucketing splits the small side across tasks.'],
              hid='scenario-oom')

# ---- scenario 2: skew
k1 = (t(180, 22, 'One reducer runs for an hour', 9.4, bold=True) + t(180, 56, '199 tasks done in 2 minutes, 1 still running', 8.2, 'ink2') + cap('Classic sign of a skewed key.', '', 'amber', y=150, h=34))
k2 = (t(180, 22, 'Find the hot key', 9.4, bold=True) + t(180, 56, 'GROUP BY key ORDER BY COUNT(*) DESC LIMIT 10', 8, 'ink', mono=True) + cap('Lab: customer 7 = 20,016 of 50,000.', '', 'blue', y=150, h=34))
k3 = (t(180, 22, 'Small other side? Use a map join', 9.4, bold=True) + t(180, 56, 'no shuffle on the key → no skew in the join', 8.2, 'ink2') + cap('Our default plan did exactly this.', '', 'green', y=150, h=34))
k4 = (t(180, 22, 'Both sides big? Split the hot key', 9.4, bold=True) + t(180, 52, 'join WHERE key != 7  (shuffle)', 8, 'ink', mono=True) + t(180, 70, 'UNION ALL join WHERE key = 7 (map join)', 8, 'ink', mono=True) + cap('Same result, verified in the lab.', '', 'green', y=150, h=34))
k5 = (t(180, 22, 'Or salt it', 9.4, 'acc', bold=True) + t(180, 56, 'spread key 7 over N random sub-keys', 8.2, 'ink2') + cap('Replicate the other side N times.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'One task that never finishes',
              'Skew is diagnosed from data, not settings. Lab numbers are real; the 200-task job is typical.',
              'Skewed join', 'Find the hot key, prefer a map join, otherwise split or salt the hot key', [k1, k2, k3, k4, k5],
              ['One straggler task is the symptom.',
               'Count rows per key to find it.',
               'A map join avoids the shuffle on the key.',
               'Split the hot key into a separate join.',
               'Salting spreads one key over many tasks.'],
              hid='scenario-skew')

# ---- scenario 3: design for SMB
d1 = (t(180, 22, 'Two big tables joined every hour', 9.4, bold=True) + t(180, 56, 'orders × payments on order_id, both huge', 8.2, 'ink2') + cap('No side fits in memory.', '', 'blue', y=150, h=34))
d2 = (t(180, 22, 'Bucket and sort both the same way', 9.4, bold=True) + t(180, 56, 'CLUSTERED BY (order_id) SORTED BY (order_id) INTO 256 BUCKETS', 7, 'ink', mono=True) + cap('Same key, same count (or multiples).', '', 'green', y=150, h=34))
d3 = (t(180, 22, 'Table type matters', 9.4, bold=True) + t(180, 56, 'managed insert-only (sorted) · not external', 8.2, 'ink2') + cap('What our Hive 4.2.1 lab required.', '', 'amber', y=150, h=34))
d4 = (t(180, 22, 'Verify', 9.4, bold=True) + t(180, 56, 'EXPLAIN: Merge Join in Map, Dummy Store', 8.2, 'ink', mono=True) + cap('No SIMPLE_EDGE into the join.', '', 'green', y=150, h=34))
d5 = (t(180, 22, 'Or Iceberg + Spark', 9.4, 'acc', bold=True) + t(180, 56, 'storage-partitioned joins in other engines', 8.2, 'ink2') + cap('Same idea in the lakehouse world.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Designing two big tables for SMB',
              'When both sides are large, the layout decides the join. (Typical design; table-type rules from our lab.)',
              'SMB design', 'Bucket and sort both tables identically on the join key, use managed tables, and verify the SMB plan', [d1, d2, d3, d4, d5],
              ['Two large tables, joined often.',
               'Use the same bucketing and sorting on the key.',
               'Choose a table type Hive trusts for bucketing.',
               'Confirm the SMB plan with EXPLAIN.',
               'Other engines offer similar bucket-aligned joins.'],
              hid='scenario-smb')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Where the rows go in each join</h2>
  <p>Left: real plans and counters. Right: how the data moves.</p>
''' + two + '''
  <p>Three live scenarios follow: a map join out of memory, a skewed join, and a design for SMB.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Join optimisation at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'map join', 11, 'green', bold=True) + t(60, 58, 'star schema', 7.4, 'ink2'),
    '1. Fact-to-dimension joins',
    'Reports join a huge fact table with small dimensions (stores, plans, dates); map joins keep them shuffle-free.',
    ['Fact + dims', '*broadcast', 'Fast report']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'buckets', 11, 'blue', bold=True) + t(60, 58, 'big × big', 7.4, 'ink2'),
    '2. Large-to-large joins',
    'Orders with payments or clicks with sessions: tables bucketed (and sorted) on the key avoid repeated full shuffles.',
    ['Same buckets', '*bucket / SMB', 'Less shuffle']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'hot keys', 10, 'violet', bold=True) + t(60, 58, 'skew', 7.4, 'ink2'),
    '3. Marketplaces and telecom',
    'A few sellers or cell towers dominate the data; hot keys are split out or salted so one task does not hold up the job.',
    ['Hot key', '*split / salt', 'Even tasks']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'OOM', 11, 'acc', bold=True) + t(60, 58, 'incident', 7.4, 'ink2'),
    '4. Incident response',
    'Map-join memory failures are traced to stale statistics or a grown dimension, fixed with ANALYZE or a threshold change.',
    ['Failure', '*EXPLAIN + stats', 'Stable job']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'review', 11, 'acc', bold=True) + t(60, 58, 'join type', 7.4, 'ink2'),
    '5. Code review',
    'Reviewers check the join type in the plan and ask why a large shuffle join is needed before a job goes live.',
    ['New job', '*join check', 'Approved']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> joins (<a href="../../03-querying/03-joins/">3.3</a>), bucketing (<a href="../../05-partitioning-and-bucketing/03-bucketing/">5.3</a>), plans (<a href="../01-explain-in-depth/">8.1</a>) and statistics (<a href="../02-cbo-and-statistics/">8.2</a>).</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
