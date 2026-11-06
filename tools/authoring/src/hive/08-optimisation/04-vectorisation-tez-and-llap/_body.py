import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()
def plain(n):
    lines = [l for l in capf(n).split('\n') if l.startswith('| ')]
    lines = [re.sub(r'\s*\|$', '', l[2:]).rstrip() for l in lines]
    return '\n'.join(l for l in lines if l.strip() not in ('Explain',)).strip('\n')
def pick(n, keys):
    return '\n'.join(l for l in plain(n).split('\n') if any(k in l for k in keys))
def setlines(n):
    return '\n'.join(re.sub(r'[|\s]', '', l) for l in capf(n).split('\n') if '=' in l and l.startswith('|'))

def opbox(x, y, label, sub='', tone='card', w=128, h=26):
    o = box(x, y, w, h, tone) + t(x + w / 2, y + (11 if sub else 16), label, 7.2, 'ink', bold=True)
    if sub:
        o += t(x + w / 2, y + 21, sub, 6.4, 'ink2', mono=True)
    return o

# ---------------------------------------------------------------- story
sc = (box(10, 12, 200, 128, 'card') + t(110, 30, 'Same query, 5 million rows', 8.8, bold=True) +
      fill(26, 48, 46, 14, 'green', rx=2) + t(80, 59, 'vectorised  ≈ 1.0 s', 7.6, 'ink', anchor='start', mono=True) +
      fill(26, 72, 140, 14, 'acc', rx=2) + t(26, 100, 'row mode  ≈ 3.0 s', 7.6, 'ink', anchor='start', mono=True) +
      t(110, 124, 'real lab timings', 7, 'ink2') +
      arrow(216, 76, 256, 76, 'acc', 2.2) + box(262, 46, 110, 60, 'violet') + t(317, 72, 'Execution', 8.4, bold=True) + t(317, 88, 'engine', 8.4, bold=True) +
      arrow(378, 76, 414, 76, 'acc', 2.2) + box(420, 12, 210, 128, 'amber') + t(525, 30, 'Three levers', 8.8, bold=True) +
      opbox(432, 40, 'Vectorisation', '1,024 rows per call', 'green', 186) + opbox(432, 72, 'Tez tuning', 'tasks · reducers · memory', 'blue', 186) + opbox(432, 104, 'LLAP', 'daemons + cache', 'violet', 186))
scene_svg = scene('The same aggregation over 5 million rows took about 1 second vectorised and about 3 seconds in row mode. Three execution levers: vectorisation, Tez tuning and LLAP.', sc,
                  'Same plan, same data: <tspan font-weight="700" class="s-acc">how</tspan> the operators run makes a 3× difference.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“The plan is right. Why is it still slow?”</h2>
  <div class="story">
    <p class="narration">Kabir has a good plan now: right statistics, right join. But the platform team says many queries still waste CPU, start too few or too many tasks, and wait for containers. Arjun Sir builds a 5-million-row copy of orders to measure what the execution engine itself can do.</p>

{scene_svg}

R> Sir, what does “vectorized” in the plan actually change?
A> Instead of pushing one row at a time through every operator, Hive pushes a <b>batch of 1,024 rows</b> stored column by column. Each operator runs a tight loop over arrays, which modern CPUs love. On our 5-million-row table it made the map work about <b>6×</b> faster.
K> And Tez tuning? I see dozens of settings online.
A> Most of them control three things: how many map tasks (split grouping), how many reducers (bytes per reducer, auto parallelism), and how much memory each container gets. We will change each and count the tasks. And <b>LLAP</b>, the long-lived daemons with a cache, we will try to switch on and see exactly what it needs. All outputs are real, from Hive 4.2.1.
  </div>
</section>
'''

lv = '''
LEVELS> Execution speed at three levels
L1> Carrying bricks
      <ul>
        <li>Carrying one brick at a time is slow; carrying a stack of 1,024 bricks at once is much faster. Vectorisation does that with rows.</li>
        <li>Tez decides how many workers (tasks) to use. Too few: slow. Too many: time wasted starting them.</li>
        <li>LLAP keeps workers always running and remembers recent data, so short queries start instantly.</li>
      </ul>
L2> The settings behind them
      <ul>
        <li><code>hive.vectorized.execution.enabled</code> (map) and <code>hive.vectorized.execution.reduce.enabled</code>: process <b>VectorizedRowBatch</b>es of 1,024 rows. Best with ORC and Parquet; check <code>EXPLAIN VECTORIZATION</code>.</li>
        <li><b>Map tasks:</b> Tez groups input splits between <code>tez.grouping.min-size</code> and <code>tez.grouping.max-size</code>.</li>
        <li><b>Reducers:</b> estimated shuffle bytes / <code>hive.exec.reducers.bytes.per.reducer</code> (256 MB default), capped by <code>hive.exec.reducers.max</code> (1,009); <code>hive.tez.auto.reducer.parallelism</code> lowers the count at run time; <code>mapreduce.job.reduces</code> forces it.</li>
        <li><b>Memory:</b> <code>hive.tez.container.size</code> and <code>hive.tez.java.opts</code> (heap about 80% of the container).</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>Vectorised vs row mode on 5,000,000 rows: Map 1 about 300–400 ms vs 2,250–2,400 ms; whole query about 1.0 s vs 3.0 s, three runs each.</li>
        <li>A UDF without a vector version still ran through the <b>VectorUDFAdaptor</b> (2.1 s); forbidding the adaptor made the map side non-vectorised (3.4 s) with an explicit <code>notVectorizedReason</code>.</li>
        <li>Split grouping changed Map 1 from 1 to 8 tasks; bytes-per-reducer changed Reducer 2 from 1 to 8, auto parallelism cut it to 2. LLAP mode failed without a ZooKeeper registry.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Vectorisation, Tez tuning and LLAP</h2>
''' + def_block(
    '<b>Vectorised query execution</b> processes rows in batches (<code>VectorizedRowBatch</code>, 1,024 rows by default) stored as column vectors, so operators such as scans, filters, expressions and aggregations run as loops over primitive arrays instead of per-row object calls; it is enabled with <code>hive.vectorized.execution.enabled</code> and works best with ORC and Parquet input. <b>Tez tuning</b> adjusts how the DAG is executed: input split grouping (number of map tasks), reducer parallelism, container memory and container reuse. <b>LLAP</b> (Live Long and Process) is an optional layer of persistent daemons that execute query fragments with an in-memory columnar cache and fast start-up, coordinated by Tez and discovered through ZooKeeper.',
    'Vectorisation makes each task faster by handling 1,024 rows at a time. Tez tuning decides how many tasks run and how much memory they get. LLAP keeps worker processes running all the time, with a data cache, so interactive queries start and finish quickly.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Vectorised', 'Operators process batches of 1,024 rows, column by column.'),
    ('Row mode', 'The old path: one row object at a time through each operator.'),
    ('VectorUDFAdaptor', 'Wraps a row-mode UDF so the rest of the plan stays vectorised.'),
    ('Split grouping', 'Tez merging input splits into tasks of a target size.'),
    ('Reducer parallelism', 'How many tasks a Reducer vertex runs.'),
    ('Container', 'A YARN process with fixed memory running Tez tasks.'),
    ('LLAP daemon', 'Long-running Hive executor with cache, registered in ZooKeeper.'),
    ('Fetch task', 'Answering a simple query without any Tez job.'),
]) + '''

  <h3>Lab settings (Hive 4.2.1, Tez local mode)</h3>
''' + table(['Setting', 'Value', 'Controls'], [
    ['<code>hive.vectorized.execution.enabled</code>', 'true', 'Vectorised map side'],
    ['<code>hive.vectorized.adaptor.usage.mode</code>', 'all', 'Wrap non-vector UDFs instead of falling back'],
    ['<code>hive.exec.reducers.bytes.per.reducer</code>', '256000000', 'Shuffle bytes per reducer'],
    ['<code>hive.exec.reducers.max</code>', '1009', 'Upper bound on reducers'],
    ['<code>hive.tez.auto.reducer.parallelism</code>', 'false', 'Shrink reducers at run time'],
    ['<code>hive.tez.container.size</code>', '-1', 'Container MB (-1: use the MapReduce setting)'],
    ['<code>hive.fetch.task.conversion</code>', 'more', 'Simple SELECT/filter/LIMIT without a job'],
    ['<code>hive.execution.mode</code>', 'container', '<code>llap</code> needs LLAP daemons'],
], minw=680) + lv + '''
EXAM> “What is vectorisation in Hive?” Processing 1,024 rows at a time as column vectors instead of row by row, which cuts per-row overhead and uses the CPU efficiently. Enable with <code>hive.vectorized.execution.enabled=true</code>, best with ORC/Parquet, verify with <code>EXPLAIN VECTORIZATION</code> (look for <code>Execution mode: vectorized</code> and <code>notVectorizedReason</code>).
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Execution modes in Hive 4</h2>
''' + table(['Mode', 'How tasks run', 'Good for', 'In our lab'], [
    ['Tez containers', 'YARN containers started per query (or per session, with reuse)', 'Batch ETL, large scans', 'Yes (local mode)'],
    ['Tez + LLAP', 'Fragments run in long-lived LLAP daemons with cache', 'Interactive BI, many short queries', 'No: needs daemons + ZooKeeper'],
    ['Fetch task', 'No job; HiveServer2 reads the files directly', 'SELECT … LIMIT, simple filters', 'Yes'],
    ['MapReduce', 'Legacy engine, deprecated; Tez is the default in Hive 4', 'Old clusters only', 'Not used'],
], minw=720) + '''
WARN> Timings in this lesson come from a single-node lab running Tez in local mode. More tasks made queries <b>slower</b> here (start-up cost, no extra machines), while on a real cluster they usually make big queries faster. Learn the mechanisms here; tune numbers on your cluster.
</section>
'''

vr = capf('l84_vec_runs.txt')
ar = capf('l84_adapt_runs.txt')
steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Measuring the execution engine</h2>
  <p>All outputs are real, from the Hive 4.2.1 lab. Timings are HiveServer2’s “Completed executing … Time taken” and the Tez vertex summary.</p>
''' + stepper([
    ('Step 1 · A bigger table to measure',
     code('sql', 'Beeline', "CREATE TABLE orders_big STORED AS ORC AS\nSELECT o.order_id * 100 + r.n AS order_id, o.customer_id, o.city, o.amount, o.order_date, o.status\nFROM orders o CROSS JOIN\n  (SELECT pos AS n FROM (SELECT posexplode(split(space(99), ' ')) AS (pos, x)) t) r;\nSELECT COUNT(*) FROM orders_big;", capf('l84_mkbig.txt')),
     '50,000 orders × 100 copies = <b>5,000,000 rows</b> in one ORC file of about 10 MB (totalSize 10,195,843 bytes). <code>space(99)</code> gives 100 empty strings to explode: a handy way to generate rows in pure HiveQL.'),
    ('Step 2 · Is the query vectorised?',
     code('sql', 'Beeline', "EXPLAIN VECTORIZATION SUMMARY\nSELECT city, status, COUNT(*) AS n, SUM(amount) AS rev, AVG(amount) AS avg_amt\nFROM orders_big WHERE amount > 100 GROUP BY city, status;", pick('l84_vecplan.txt', ('ectoriz', 'allNative', 'inputFileFormats', 'Map 1', 'Reducer 2', 'usesVector'))),
     'Both vertices say <code>Execution mode: vectorized</code>. The map side reads through the ORC vectorised input format. <code>allNative: false</code> means some operator uses a generic (non-native) vector implementation, still vectorised; <code>usesVectorUDFAdaptor: false</code> means no row-mode UDF had to be wrapped.'),
    ('Step 3 · Vectorised vs row mode, three runs each',
     code('sql', 'Beeline', "SET hive.vectorized.execution.enabled=true;    -- then false\nSET hive.tez.exec.print.summary=true;\nSELECT city, status, COUNT(*) AS n, SUM(amount) AS rev, AVG(amount) AS avg_amt\nFROM orders_big WHERE amount > 100 GROUP BY city, status;", vr),
     'Map 1 (scan, filter, partial aggregation of 5,000,000 rows) took <b>302–404 ms</b> vectorised and <b>2,254–2,400 ms</b> in row mode: about <b>6–7×</b>. The whole query went from about 3.0 s to 1.0 s; the rest is fixed overhead (planning, starting tasks). Same result, 24 groups, in every run.'),
    ('Step 4 · A UDF without a vector version',
     code('sql', 'Beeline', "SET hive.vectorized.adaptor.usage.mode;          -- all\nEXPLAIN VECTORIZATION EXPRESSION SELECT md5(city) AS x, COUNT(*) FROM orders_big GROUP BY md5(city);\n\nSET hive.vectorized.adaptor.usage.mode=none;\nEXPLAIN VECTORIZATION ONLY SUMMARY SELECT md5(city) AS x, COUNT(*) FROM orders_big GROUP BY md5(city);\n-- and timing both", setlines('l84_adaptor.txt') + '\n' + pick('l84_adaptor.txt', ('VectorUDFAdaptor(', 'usesVectorUDFAdaptor')) + '\n\n-- adaptor.usage.mode=none\n' + pick('l84_novec.txt', ('notVectorizedReason', 'vectorized:')) + '\n\n' + ar),
     '<code>md5</code> has no vector implementation, so Hive wrapped it: <code>VectorUDFAdaptor(md5(city))</code> converts each batch to rows for that one expression and keeps everything else vectorised (about <b>2.1 s</b>). With the adaptor forbidden, EXPLAIN says exactly why the map side fell back: <code>notVectorizedReason: … UDF GenericUDFBridge ==> md5 … not supported</code>, and the query took about <b>3.4 s</b>. Custom Java UDFs are the most common reason for row mode in real plans.'),
    ('Step 5 · The Tez knobs and their defaults',
     code('sql', 'Beeline', "SET hive.tez.container.size; SET hive.exec.reducers.bytes.per.reducer; SET hive.exec.reducers.max;\nSET hive.tez.auto.reducer.parallelism; SET mapreduce.job.reduces; SET hive.execution.mode;\nSET hive.llap.execution.mode; SET hive.fetch.task.conversion; SET hive.fetch.task.conversion.threshold;\nSET hive.server2.tez.initialize.default.sessions;", setlines('l84_tezset.txt')),
     'Container size -1 means Hive takes the MapReduce map memory setting. One reducer per 256 MB of estimated shuffle data, at most 1,009. Auto reducer parallelism is off. Execution mode is <code>container</code>, not <code>llap</code>. Simple queries up to 200 MB of input can run as a fetch task.'),
    ('Step 6 · Changing the number of tasks',
     code('sql', 'Beeline', "-- orders_big_txt: the same 5,000,000 rows as one 246 MB text file\nSELECT customer_id, COUNT(*) AS n, SUM(amount) FROM orders_big_txt GROUP BY customer_id;\n-- run once per setting below, with hive.tez.exec.print.summary=true", capf('l84_tasks.txt')),
     'The 246 MB file has 8 input splits of up to 32 MB. By default Tez <b>grouped</b> them into 1 map task; with <code>tez.grouping.max-size</code> at 16 MB no two splits could be grouped, so <b>8</b> map tasks ran (grouping merges splits, it never cuts them). <b>Bytes per reducer</b> at 100,000 gave <b>8</b> reducers (the estimated shuffle is about 765 KB: 6,171 rows × 124 bytes). With <b>auto reducer parallelism</b> on as well, Tez lowered the reducer count at run time after seeing the real data, ending with <b>2</b>. <code>mapreduce.job.reduces=6</code> forced 6. On one machine every extra task cost time; on a cluster it buys parallelism.'),
    ('Step 7 · No job at all: fetch tasks',
     code('sql', 'Beeline', "EXPLAIN SELECT order_id, city, amount FROM orders_big WHERE city = 'Pune' LIMIT 5;\nSET hive.fetch.task.conversion=none;\nEXPLAIN SELECT order_id, city, amount FROM orders_big WHERE city = 'Pune' LIMIT 5;", plain('l84_fetch.txt') + '\n\n-- with conversion=none\n' + pick('l84_fetch_none.txt', ('Stage', 'Fetch', 'Map 1'))),
     'With <code>hive.fetch.task.conversion=more</code> the whole query is a <b>Fetch Operator</b>: HiveServer2 reads the file itself and stops after 5 rows, with no Tez DAG. With <code>none</code> the same query gets Stage-1 and a vectorised Map 1. This is why <code>SELECT … LIMIT 10</code> feels instant even on large tables; aggregations always need a job.'),
    ('Step 8 · Trying LLAP',
     code('sql', 'Beeline', "SET hive.execution.mode=llap;\nSELECT COUNT(*) FROM orders_big WHERE amount > 100;", capf('l84_llap_err.txt')),
     'LLAP mode failed: to find LLAP daemons Hive looks them up in a <b>ZooKeeper</b> registry (<code>hive.llap.daemon.service.hosts</code>, ZooKeeper quorum), and our lab has neither daemons nor ZooKeeper. A real LLAP setup runs daemons on YARN or Kubernetes with a large heap and off-heap cache. We did not measure LLAP speed-ups; see the FAQ for what it changes. The next statement in container mode worked normally (4,319,400 rows).'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('Map 1', W), ('  Execution mode: vectorized', G), ('  inputFileFormats: …OrcInputFormat', G), ('Reducer 2', W), ('  Execution mode: vectorized', G)], size=7.6),
    term([('vectorized=true   query 0.973 s  Map 1 302 ms', G), ('vectorized=false  query 3.035 s  Map 1 2360 ms', RD), ('vectorized=true   query 1.081 s  Map 1 404 ms', G), ('vectorized=false  query 3.101 s  Map 1 2400 ms', RD)], size=7.2),
    term([('VectorUDFAdaptor(md5(city))', Y), ('usesVectorUDFAdaptor: true', Y), ('adaptor none:', W), ('notVectorizedReason: … md5 … not supported', RD)], size=7.2),
    term([('defaults           Map 1: 1  Reducer 2: 1', W), ('grouping 8–16 MB   Map 1: 8', G), ('bytes/reducer 1e5  Reducer 2: 8', G), ('+ auto parallelism Reducer 2: 2', G), ('job.reduces=6      Reducer 2: 6', G)], size=7.2),
    term([('SET hive.execution.mode=llap;', W), ('FAILED: … TezTask', RD), ('Caused by: NullPointerException', RD), ('  … ZooKeeperHiveHelper … getQuorum() is null', Y)], size=7.2),
]
def batch(vec):
    o = ''
    if vec:
        o += box(20, 44, 120, 82, 'green') + t(80, 60, 'batch of 1,024', 8, 'ink', bold=True)
        for k, c in enumerate(['city[ ]', 'amount[ ]', 'status[ ]']):
            o += box(30 + k * 36, 70, 32, 48, 'card') + t(46 + k * 36, 98, c.split('[')[0][:4], 6.4, 'ink2', mono=True)
        o += arrow(144, 85, 196, 85, 'green', 2) + opbox(200, 72, 'Filter', 'loop over array', 'green', 130)
    else:
        for k in range(4):
            o += box(30, 44 + k * 22, 90, 18, 'card') + t(75, 56 + k * 22, f'row {k + 1}', 7, 'ink2', mono=True) + arrow(122, 53 + k * 22, 196, 85, 'red', 1)
        o += opbox(200, 72, 'Filter', 'one call per row', 'red', 130)
    return o
B1 = [
    t(180, 22, 'Row mode vs vectorised', 9.4, bold=True) + batch(False) + cap('Row mode: per-row calls and objects.', '', 'amber', y=150, h=34),
    t(180, 22, 'Vectorised: column arrays', 9.4, bold=True) + batch(True) + cap('One call per 1,024 rows: 6–7× faster map in our lab.', '', 'green', y=150, h=34),
    t(180, 22, 'A row-only UDF inside a vector plan', 9.4, bold=True) + opbox(20, 60, 'Scan (vector)', '', 'green', 96) + arrow(118, 73, 130, 73, 'ink3') + opbox(132, 60, 'md5 via adaptor', 'batch → rows → batch', 'amber', 110) + arrow(244, 73, 256, 73, 'ink3') + opbox(258, 60, 'Group By (vector)', '', 'green', 90) + cap('Only one expression pays the row cost.', '', 'blue', y=150, h=34),
    t(180, 22, 'Tasks per vertex', 9.4, bold=True) + ''.join(box(20 + k * 40, 50, 34, 24, 'blue') for k in range(8)) + t(180, 90, 'Map 1: input splits merged by grouping', 8, 'ink2', mono=True) + ''.join(box(110 + k * 40, 100, 34, 20, 'violet') for k in range(2)) + t(180, 134, 'Reducers: shuffle bytes / bytes-per-reducer', 7.6, 'ink2', mono=True) + cap('Auto parallelism trims reducers at run time.', '', 'green', y=150, h=34),
    t(180, 22, 'LLAP: daemons found through ZooKeeper', 9.4, bold=True) + opbox(20, 56, 'HiveServer2', 'Tez AM', 'blue', 100) + arrow(122, 69, 146, 69, 'ink3') + opbox(148, 56, 'ZooKeeper', 'registry', 'amber', 90) + arrow(240, 69, 264, 69, 'ink3') + opbox(266, 56, 'LLAP daemons', 'cache + executors', 'violet', 80) + cap('No registry, no daemons: the query fails.', '', 'amber', y=150, h=34),
]
see_caps = ['EXPLAIN VECTORIZATION: both vertices run vectorised.',
            'Vectorised map work took 300–400 ms instead of about 2,300 ms.',
            'md5 had no vector form: the adaptor wrapped it, or the map fell back.',
            'Grouping and reducer settings changed the task counts.',
            'LLAP mode failed: no ZooKeeper registry in the lab.']
behind_caps = ['Row mode calls every operator once per row.',
               'Vectorised operators loop over column arrays of 1,024 values.',
               'The adaptor turns one batch into rows for a single expression.',
               'Map tasks come from grouped input splits; reducers from estimated shuffle bytes.',
               'LLAP fragments run in daemons the Tez AM discovers via ZooKeeper.']
two = anim_two('Execution engine', 'How tasks run', 'Real lab outputs', 'Inside the engine', see, B1, see_caps, behind_caps)

# ---- scenario 1: custom UDF kills vectorisation
u1 = (t(180, 22, 'A pipeline got 3× slower after a release', 9.4, bold=True) + t(180, 56, 'new custom UDF mask_phone() in the SELECT', 8.2, 'ink2', mono=True) + cap('Same data, same plan shape.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'EXPLAIN VECTORIZATION', 9.4, bold=True) + t(180, 56, 'notVectorizedReason: … UDF … not supported', 8, 'red', mono=True) + cap('Map side fell back to row mode.', '', 'amber', y=150, h=34))
u3 = (t(180, 22, 'Check the adaptor setting', 9.4, bold=True) + t(180, 56, 'hive.vectorized.adaptor.usage.mode = all', 8.2, 'ink', mono=True) + cap('Lab: 2.1 s with adaptor vs 3.4 s without.', '', 'green', y=150, h=34))
u4 = (t(180, 22, 'Better: built-in functions', 9.4, bold=True) + t(180, 56, "regexp_replace / concat / substr instead of a UDF", 8, 'ink2', mono=True) + cap('Many built-ins have native vector versions.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Guard it', 9.4, 'acc', bold=True) + t(180, 56, 'CI check: no notVectorizedReason in key jobs', 8.2, 'ink2') + cap('Catches the next regression early.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'One UDF, three times slower',
              'A typical regression; timings in the captions are from our lab’s md5 test.',
              'UDF and vectorisation', 'A custom UDF made the map side fall back to row mode; the adaptor or built-in functions restore vectorised execution', [u1, u2, u3, u4, u5],
              ['A release added a custom UDF.',
               'EXPLAIN VECTORIZATION gives the reason.',
               'The adaptor keeps the rest vectorised.',
               'Built-in functions are often native.',
               'Check vectorisation in CI.'],
              hid='scenario-udf')

# ---- scenario 2: too many / too few reducers
r1 = (t(180, 22, 'Nightly aggregation: 1 reducer, 3 hours', 9.4, bold=True) + t(180, 56, 'estimated shuffle tiny, real shuffle 400 GB', 8.2, 'red', mono=True) + cap('Bad estimate → one reducer.', '', 'amber', y=150, h=34))
r2 = (t(180, 22, 'Fix the estimate first', 9.4, bold=True) + t(180, 56, 'ANALYZE TABLE … FOR COLUMNS (Lesson 8.2)', 8.2, 'ink', mono=True) + cap('Reducer count follows estimated bytes.', '', 'green', y=150, h=34))
r3 = (t(180, 22, 'Opposite problem: 1,009 tiny reducers', 9.4, bold=True) + t(180, 56, 'thousands of small output files', 8.2, 'ink2') + cap('Over-estimate wastes containers.', '', 'amber', y=150, h=34))
r4 = (t(180, 22, 'Let Tez adjust', 9.4, bold=True) + t(180, 56, 'hive.tez.auto.reducer.parallelism=true', 8.2, 'ink', mono=True) + cap('Lab: 8 planned → 2 at run time.', '', 'green', y=150, h=34))
r5 = (t(180, 22, 'Force only as a last resort', 9.4, 'acc', bold=True) + t(180, 56, 'mapreduce.job.reduces=N for one query', 8.2, 'ink2') + cap('Fixed numbers age badly as data grows.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Reducer counts that are badly wrong',
              'Reducer parallelism comes from estimates. Sizes are illustrative; the 8 → 2 adjustment is from our lab.',
              'Reducer tuning', 'Fix statistics so estimated shuffle bytes are right, enable auto reducer parallelism, and force counts only for exceptions', [r1, r2, r3, r4, r5],
              ['Too few reducers: one task does all the work.',
               'Better statistics give a better reducer count.',
               'Too many reducers waste containers and create small files.',
               'Auto parallelism trims at run time.',
               'Hard-coded counts are a last resort.'],
              hid='scenario-reducers')

# ---- scenario 3: BI dashboards and LLAP
l1 = (t(180, 22, '200 analysts, dashboards with 3-second goals', 9.4, bold=True) + t(180, 56, 'each query small, container start-up dominates', 8, 'ink2') + cap('Batch-style execution feels slow.', '', 'blue', y=150, h=34))
l2 = (t(180, 22, 'Options', 9.4, bold=True) + t(180, 52, 'pre-warmed Tez sessions + container reuse', 8, 'ink', mono=True) + t(180, 70, 'LLAP daemons with cache', 8, 'ink', mono=True) + cap('Remove start-up time.', '', 'green', y=150, h=34))
l3 = (t(180, 22, 'LLAP needs infrastructure', 9.4, bold=True) + t(180, 56, 'ZooKeeper registry, daemons, big memory', 8.2, 'ink2') + cap('Our lab failed exactly at the registry.', '', 'amber', y=150, h=34))
l4 = (t(180, 22, 'Workload management', 9.4, bold=True) + t(180, 56, 'resource plans: BI pool vs ETL pool', 8.2, 'ink2') + cap('ETL does not starve dashboards.', '', 'green', y=150, h=34))
l5 = (t(180, 22, 'Or another engine', 9.4, 'acc', bold=True) + t(180, 56, 'Trino / Impala on the same tables', 8.2, 'ink2') + cap('Common split: Hive for ETL, MPP for BI.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Interactive BI on Hive',
              'How platform teams make Hive interactive. (Typical architectures; we could not run LLAP in the lab.)',
              'LLAP and interactive SQL', 'For many short dashboard queries, pre-warmed sessions or LLAP remove start-up cost; LLAP needs ZooKeeper and daemons', [l1, l2, l3, l4, l5],
              ['Short queries are dominated by start-up.',
               'Pre-warm sessions or use LLAP.',
               'LLAP needs a registry and daemons.',
               'Separate BI and ETL resources.',
               'Some teams use an MPP engine for BI.'],
              hid='scenario-llap')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Inside the execution engine</h2>
  <p>Left: real lab outputs. Right: what happens inside.</p>
''' + two + '''
  <p>Three live scenarios follow: a UDF that breaks vectorisation, reducer counts, and interactive BI with LLAP.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Execution tuning at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'vectorized', 10, 'green', bold=True, mono=True) + t(60, 58, 'every job', 7.4, 'ink2'),
    '1. CPU savings on ETL',
    'Keeping heavy ETL on ORC/Parquet with vectorisation cuts CPU hours, which on cloud clusters is directly money.',
    ['ORC + vector', '*fewer CPU s', 'Lower bill']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'reducers', 11, 'blue', bold=True) + t(60, 58, 'right-sized', 7.4, 'ink2'),
    '2. Right-sized parallelism',
    'Auto reducer parallelism and split grouping keep tasks large enough to be efficient and many enough to finish on time.',
    ['Estimates', '*task counts', 'On-time SLAs']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'LLAP', 12, 'violet', bold=True, mono=True) + t(60, 58, 'interactive', 7.4, 'ink2'),
    '3. Interactive analytics',
    'Distributions such as Cloudera Data Warehouse offer LLAP-based virtual warehouses for BI tools.',
    ['BI tool', '*LLAP', 'Seconds']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'memory', 11, 'acc', bold=True) + t(60, 58, 'containers', 7.4, 'ink2'),
    '4. Fixing container failures',
    'Tasks killed for exceeding memory are fixed with container size and heap settings, or by reducing map-join sizes.',
    ['Killed task', '*memory tuning', 'Stable job']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'fetch', 11, 'acc', bold=True, mono=True) + t(60, 58, 'no job', 7.4, 'ink2'),
    '5. Fast data previews',
    'Fetch-task conversion lets analysts preview tables with SELECT … LIMIT instantly, without using cluster resources.',
    ['Preview', '*fetch task', 'Instant']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> how a query becomes a Tez job (<a href="../../01-introduction/04-how-a-hive-query-becomes-a-job/">1.4</a>), ORC (<a href="../../06-file-formats/02-orc-deep-dive/">6.2</a>) and reading plans (<a href="../01-explain-in-depth/">8.1</a>).</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
