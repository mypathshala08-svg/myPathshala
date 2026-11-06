import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()

# parse the real output files
F = {}
cur = None
for ln in capf('l34_files.txt').split('\n'):
    if ln.startswith('=== '):
        name = ln[4:]; F[name] = {}
    elif ln.startswith('--- '):
        cur = ln[4:]; F[name][cur] = []
    elif ln.strip():
        F[name][cur].append(ln)
def files_txt(name):
    return '\n'.join(f'--- {fn}\n' + '\n'.join(rows) for fn, rows in F[name].items())

# ---------------------------------------------------------------- story
def col(x, title, rows, tone, w=140):
    o = box(x, 34, w, 104, tone) + t(x + w / 2, 48, title, 8, bold=True, mono=True)
    for k, r in enumerate(rows[:6]):
        o += t(x + 8, 62 + k * 12, r, 7, 'ink', anchor='start', mono=True)
    return o
sc = (t(160, 22, 'SORT BY amount DESC (3 reducers)', 8.8, 'red', bold=True) + ''.join(col(10 + k * 102, fn, F['sortby'][fn], 'amber', 96) for k, fn in enumerate(F['sortby'])) +
      t(480, 22, 'ORDER BY amount DESC', 8.8, 'green', bold=True) + col(400, '000000_0', F['orderby']['000000_0'], 'green', 160) + t(480, 150, '+ 6 more rows…', 7.4, 'ink2'))
scene_svg = scene('The same twelve orders sorted with SORT BY into three separately sorted files, and with ORDER BY into one fully sorted file.', sc,
                  'SORT BY sorts <tspan font-weight="700" class="s-acc">inside each reducer</tspan>; ORDER BY sorts everything, in one reducer.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“The file is sorted… but Rs 530 is at the bottom”</h2>
  <div class="story">
    <p class="narration">Kabir exports the twelve newest orders sorted by amount, highest first, for the finance team. He used <code>SORT BY amount DESC</code> because a colleague said it is faster than ORDER BY. Finance replies with a screenshot: three files, each sorted, but the Rs 530 order sits alone in the last file, after Rs 40.</p>

{scene_svg}

K> Sir, SORT BY and ORDER BY both sort. Why did I get three files?
A> Because Hive gives you four ordering tools, and they answer different questions. <b>ORDER BY</b> promises one total order, so it must bring all rows to <b>one reducer</b>. <b>SORT BY</b> only sorts within each reducer, so with three reducers you get three sorted pieces. <b>DISTRIBUTE BY</b> decides which reducer each row goes to, and <b>CLUSTER BY</b> does both distribute and sort on the same column.
R> So SORT BY is useless?
A> Not at all. It is exactly what you want when the next step works per group, like writing one sorted file per city, or feeding a script that processes each customer’s orders in time order. We will run all four on the same twelve orders with three reducers and open the files they write.
  </div>
</section>
'''

lv = '''
LEVELS> Ordering at three levels
L1> Sorting exam papers
      <ul>
        <li><b>ORDER BY</b>: one teacher collects every paper and sorts the whole pile. Correct, but one person does all the work.</li>
        <li><b>SORT BY</b>: three teachers each sort the papers they happened to receive. Three neat piles, but not one ordered pile.</li>
        <li><b>DISTRIBUTE BY section</b>: all papers of section A go to teacher 1, B to teacher 2… Nobody sorts yet.</li>
        <li><b>CLUSTER BY section</b>: same distribution, and each teacher sorts by section.</li>
      </ul>
L2> The four clauses
      <ul>
        <li><code>ORDER BY col [ASC|DESC] [NULLS FIRST|LAST]</code>: total order of the final result; uses a single reducer for the sort.</li>
        <li><code>SORT BY col</code>: each reducer sorts its own rows; no global order.</li>
        <li><code>DISTRIBUTE BY col</code>: rows with the same value go to the same reducer (by hash); no sorting.</li>
        <li><code>CLUSTER BY col</code> = <code>DISTRIBUTE BY col SORT BY col</code>, ascending only. For descending or a different sort column, write DISTRIBUTE BY + SORT BY yourself.</li>
        <li>Number of reducers for SORT/DISTRIBUTE/CLUSTER: estimated from data size or set with <code>mapred.reduce.tasks</code> (we used 3).</li>
      </ul>
L3> Details tested on Hive 4.2.1
      <ul>
        <li>With <code>mapred.reduce.tasks=3</code>, ORDER BY still wrote <b>one</b> file; SORT BY, DISTRIBUTE BY and CLUSTER BY wrote three.</li>
        <li><b>Strict mode:</b> <code>hive.strict.checks.orderby.no.limit=true</code> rejects ORDER BY without LIMIT (“disabled for safety reasons”); it is false by default.</li>
        <li><b>NULL order:</b> <code>hive.default.nulls.last=true</code> (default) puts NULLs last in ASC and first in DESC; override with <code>NULLS FIRST/LAST</code>.</li>
        <li><b>Positions:</b> <code>ORDER BY 2 DESC</code> works by default (<code>hive.orderby.position.alias=true</code>), unlike GROUP BY 1.</li>
        <li><b>Top-N:</b> <code>ORDER BY … LIMIT 10</code> lets each task keep only its top rows before the final merge, so it is cheap even on big data.</li>
        <li>DISTRIBUTE BY uses a hash of the value: which city lands in which file is not alphabetical (Delhi alone in file 0).</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>ORDER BY, SORT BY, DISTRIBUTE BY and CLUSTER BY</h2>
''' + def_block(
    '<b>ORDER BY</b> guarantees a total ordering of the query result and is executed with a single final reducer. <b>SORT BY</b> sorts rows within each reducer only, giving a partial order when several reducers run. <b>DISTRIBUTE BY</b> controls how rows are partitioned among reducers: rows with equal distribute-key values are sent to the same reducer, without sorting. <b>CLUSTER BY col</b> is shorthand for <code>DISTRIBUTE BY col SORT BY col</code> (ascending).',
    'ORDER BY sorts the whole result (one reducer does it). SORT BY sorts each reducer’s share separately. DISTRIBUTE BY decides which reducer gets which rows. CLUSTER BY distributes and sorts by the same column.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Total order', 'Every row is in order relative to every other row.'),
    ('Partial order', 'Rows are ordered only inside groups (here: inside each reducer’s output).'),
    ('Reducer', 'A task after the shuffle; each one writes its own output file (000000_0, 000001_0 …).'),
    ('Hash partitioning', 'hash(key) mod number-of-reducers decides the reducer for a row.'),
    ('Top-N', 'ORDER BY … LIMIT n: only the n best rows are needed.'),
    ('Strict mode', 'Safety checks that reject risky queries, such as ORDER BY without LIMIT.'),
    ('NULLS FIRST/LAST', 'Where NULL values go in the sort order.'),
    ('mapred.reduce.tasks', 'A setting that fixes the number of reducers (−1 = let Hive estimate).'),
]) + '''

  <h3>Side by side (12 orders, 3 reducers, real output)</h3>
''' + table(['Clause', 'Output files', 'Within a file', 'Across files', 'Typical use'], [
    ['<code>ORDER BY amount DESC</code>', '1', 'Sorted', 'n/a (single file)', 'Final reports, top-N with LIMIT'],
    ['<code>SORT BY amount DESC</code>', '3', 'Sorted', 'Not ordered; a city can be in several files', 'Pre-sorting per reducer'],
    ['<code>DISTRIBUTE BY city</code>', '3', 'Not sorted', 'Each city in exactly one file', 'Grouping rows for the next step'],
    ['<code>CLUSTER BY city</code>', '3', 'Sorted by city', 'Each city in one file', 'Per-key processing, ascending'],
    ['<code>DISTRIBUTE BY city SORT BY city, amount DESC</code>', '3', 'By city, then amount high → low', 'Each city in one file', 'Per-key processing with custom order'],
], minw=760) + lv + '''
EXAM> “Differentiate ORDER BY, SORT BY, DISTRIBUTE BY and CLUSTER BY.” A four-row table: ORDER BY = total order, one reducer; SORT BY = sorted per reducer, partial order; DISTRIBUTE BY = same key to same reducer, unsorted; CLUSTER BY = DISTRIBUTE BY + SORT BY on one column, ascending only. Add “ORDER BY needs LIMIT in strict mode”.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Which ordering for which job?</h2>
''' + cards([
    ('ORDER BY … LIMIT', 'Top 10 restaurants by revenue, latest 50 orders. Cheap: each task keeps its own top rows; the final reducer merges a few.', 'Most common'),
    ('ORDER BY (whole result)', 'A small final report that people read. Fine for thousands of rows; dangerous for billions (one reducer).', 'Small results'),
    ('DISTRIBUTE BY + SORT BY', 'Write one sorted file per city, or feed a TRANSFORM script that needs each customer’s orders together and in time order.', 'Per-key work'),
    ('CLUSTER BY', 'Short form when you distribute and sort by the same column, ascending. Also used before writing bucketed tables in older Hive.', 'Shorthand'),
]) + '''
  <h3>Settings that change ordering behaviour</h3>
''' + table(['Setting', 'Default in our lab', 'Effect'], [
    ['<code>hive.strict.checks.orderby.no.limit</code>', 'false', 'true → ORDER BY without LIMIT is rejected'],
    ['<code>hive.default.nulls.last</code>', 'true', 'NULLs last in ASC, first in DESC'],
    ['<code>hive.orderby.position.alias</code>', 'true', '<code>ORDER BY 2</code> means the second select column'],
    ['<code>mapred.reduce.tasks</code>', '−1 (estimate)', 'Fixed number of reducers for SORT/DISTRIBUTE/CLUSTER BY'],
], minw=600) + '''
WARN> CLUSTER BY is not the same as a bucketed table (<code>CLUSTERED BY … INTO n BUCKETS</code>, Module 5). CLUSTER BY arranges rows for one query only; buckets fix the file layout of a table permanently.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Twelve orders, four clauses, real files</h2>
  <p>We take the 12 orders with <code>order_id &lt; 100013</code>, force 3 reducers with <code>SET mapred.reduce.tasks=3;</code> and write each result with <code>INSERT OVERWRITE LOCAL DIRECTORY</code> so we can open every reducer’s file. All outputs are real.</p>
''' + stepper([
    ('Step 1 · SORT BY: three sorted pieces',
     code('sql', 'Beeline', "SET mapred.reduce.tasks=3;\nINSERT OVERWRITE LOCAL DIRECTORY '/data/exports/sortby'\nROW FORMAT DELIMITED FIELDS TERMINATED BY ','\nSELECT city, amount FROM orders WHERE order_id < 100013 SORT BY amount DESC;", files_txt('sortby')),
     'Each file is sorted high → low, but the files overlap: Rs 530 is alone in file 2. Rows were spread over reducers without a key, so the split is arbitrary.'),
    ('Step 2 · ORDER BY: one total order',
     code('sql', 'Beeline', "… SELECT city, amount FROM orders WHERE order_id < 100013 ORDER BY amount DESC;", files_txt('orderby')),
     'Despite <code>mapred.reduce.tasks=3</code>, ORDER BY wrote a single file: one reducer did the final sort. Correct, but on billions of rows that one reducer becomes the bottleneck.'),
    ('Step 3 · DISTRIBUTE BY: same city, same file',
     code('sql', 'Beeline', "… SELECT city, amount FROM orders WHERE order_id < 100013 DISTRIBUTE BY city;", files_txt('distby')),
     'Every Mumbai and Pune order is in file 1, Thane and Hyderabad in file 2, Delhi in file 0. Nothing is sorted. Which city goes where comes from a hash, not the alphabet.'),
    ('Step 4 · CLUSTER BY: distribute and sort by city',
     code('sql', 'Beeline', "… SELECT city, amount FROM orders WHERE order_id < 100013 CLUSTER BY city;", files_txt('clusterby')),
     'Same distribution as Step 3, now sorted by city inside each file. The amounts within a city are in no particular order, and CLUSTER BY cannot sort descending.'),
    ('Step 5 · DISTRIBUTE BY + SORT BY: full control',
     code('sql', 'Beeline', "… SELECT city, amount FROM orders WHERE order_id < 100013\nDISTRIBUTE BY city SORT BY city, amount DESC;", files_txt('distsort')),
     'Each city in one file, cities in order, and each city’s orders from highest to lowest amount. This is the pattern for per-key processing.'),
    ('Step 6 · Strict mode, NULL order and positions',
     code('sql', 'Beeline', "SET hive.strict.checks.orderby.no.limit=true;\nSELECT city, amount FROM orders ORDER BY amount DESC;\n\nSELECT payment, orders FROM payment_mix ORDER BY orders DESC NULLS LAST;\nSELECT city, SUM(amount) AS revenue FROM orders GROUP BY city ORDER BY 2 DESC LIMIT 3;",
          capf('l34_strict.txt').split('If you know')[0].strip() + ' …\n\n' + tables(capf('l34_nulls.txt'))[0] + '\n' + tables(capf('l34_nulls.txt'))[2]),
     'Strict mode blocks an unlimited ORDER BY on a big table. <code>NULLS LAST</code> moves Crypto (NULL orders) to the end; by default it came first in a DESC sort. <code>ORDER BY 2</code> sorts by the second column.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
def red_boxes(name, title, tone='card', hl=None):
    o = t(180, 22, title, 9.4, bold=True)
    for k, (fn, rows) in enumerate(F[name].items()):
        x = 8 + k * 118
        o += box(x, 36, 110, 18 + 11 * max(1, len(rows[:12])), tone) + t(x + 55, 48, f'reducer {k} · {fn}', 6.8, bold=True, mono=True)
        for j, r in enumerate(rows[:12]):
            o += t(x + 6, 61 + j * 11, r, 6.8, 'acc' if hl and hl in r else 'ink', anchor='start', mono=True, bold=bool(hl and hl in r))
    return o
see = [
    term([('> SET mapred.reduce.tasks=3;', W), ('> … SORT BY amount DESC;', W), ('$ ls sortby/', W), ('000000_0  000001_0  000002_0', G), ('$ cat sortby/000002_0', W), ('Mumbai,530.00', Y)]),
    term([('> … ORDER BY amount DESC;', W), ('$ ls orderby/', W), ('000000_0', G), ('$ head -3 orderby/000000_0', W), ('Mumbai,590.00', G), ('Mumbai,530.00', G), ('Mumbai,500.00', G)]),
    term([('> … DISTRIBUTE BY city;', W), ('$ cat distby/000001_0', W), ('Pune,40.00', G), ('Mumbai,590.00', G), ('Pune,460.00', G), ('… (Mumbai and Pune only)', G)]),
    term([('> … CLUSTER BY city;', W), ('$ cat clusterby/000001_0', W), ('Mumbai,530.00', G), ('Mumbai,500.00', G), ('…', G), ('Pune,410.00', G), ('Pune,460.00', G)]),
    term([('> … DISTRIBUTE BY city', W), ('    SORT BY city, amount DESC;', W), ('$ cat distsort/000001_0', W), ('Mumbai,590.00', G), ('Mumbai,530.00', G), ('…', G), ('Pune,40.00', G)]),
]
B1 = [
    red_boxes('sortby', 'SORT BY: each reducer sorts what it got', 'amber', '530') + cap('Three sorted files, no global order.', '', 'amber', y=196, h=28),
    t(180, 22, 'ORDER BY: everything through one reducer', 9.4, bold=True) + ''.join(arrow(60 + k * 120, 44, 180, 70, 'ink3', 1.4) for k in range(3)) + ''.join(chip(20 + k * 120, 34, f'map out {k}', 'grey', w=80, h=16, size=7) for k in range(3)) +
    box(110, 72, 140, 120, 'green') + t(180, 86, 'reducer 0 · 000000_0', 7.2, bold=True, mono=True) + ''.join(t(118, 100 + j * 11, r, 7, 'ink', anchor='start', mono=True) for j, r in enumerate(F['orderby']['000000_0'][:8])) + cap('Total order; one reducer.', '', 'green', y=196, h=28),
    red_boxes('distby', 'DISTRIBUTE BY city: same city → same reducer', 'blue', 'Pune') + cap('Grouped by hash(city), not sorted.', '', 'blue', y=196, h=28),
    red_boxes('clusterby', 'CLUSTER BY city: distribute + sort by city', 'violet') + cap('Sorted by city only, ascending.', '', 'violet', y=196, h=28),
    red_boxes('distsort', 'DISTRIBUTE BY city SORT BY city, amount DESC', 'green') + cap('Each city together, amounts high → low.', '', 'green', y=196, h=28),
]
see_caps = ['SORT BY with three reducers writes three files; the 530 order ends up alone in the third file.',
            'ORDER BY writes a single file in total order.',
            'DISTRIBUTE BY city puts all Mumbai and Pune orders in the same file, unsorted.',
            'CLUSTER BY city sorts each file by city.',
            'DISTRIBUTE BY city with SORT BY city, amount DESC gives each city’s orders from highest to lowest.']
behind_caps = ['Rows go to reducers without a key, and each reducer sorts only its own rows.',
               'All rows meet in one reducer for the final sort.',
               'hash(city) chooses the reducer, so every row of a city meets in one place.',
               'Each reducer receives whole cities and sorts them by city name.',
               'The sort key can differ from the distribute key, giving any order within each group.']
two = anim_two('Ordering clauses', 'The same 12 rows, four ways', 'Real output files', 'What each of the three reducers received and wrote (real files)', see, B1, see_caps, behind_caps)

# ---- scenario 1: ORDER BY on a huge table
o1 = (t(180, 22, 'Nightly export: 2 billion rows, ORDER BY ts', 9.4, bold=True) + ''.join(fill(30 + k * 60, 60, 44, 40, 'green') for k in range(5)) + t(180, 120, '500 map tasks finish in 6 minutes…', 8.4, 'ink2') + cap('Then the job sits at 99% for hours.', '(illustrative)', 'amber', y=150, h=46))
o2 = (t(180, 22, 'One reducer sorts 2 billion rows', 9.6, 'red', bold=True) + box(130, 50, 100, 70, 'red') + t(180, 90, '1 reducer', 9, 'red', bold=True) + cap('A total order needs a single sorter.', '', 'red', y=150, h=34))
o3 = (t(180, 22, 'Ask: who needs the global order?', 9.6, bold=True) + ''.join(t(26, 52 + k * 19, s, 8.4, anchor='start') for k, s in enumerate(['• a person reading the top rows → ORDER BY … LIMIT', '• a per-customer process → DISTRIBUTE + SORT BY', '• a downstream system → often no order at all'])) + cap('Most big exports do not need a total order.', '', 'blue', y=150, h=34))
o4 = (t(180, 22, 'Turn on the guard', 9.6, 'green', bold=True) + t(180, 56, 'SET hive.strict.checks.orderby.no.limit=true;', 8.4, 'ink', mono=True) + t(180, 76, '“Order by-s without limit are disabled for safety reasons”', 7.8, 'red') + cap('Real message from our lab.', '', 'green', y=150, h=34))
o5 = (t(180, 22, 'Top-N stays cheap', 9.6, 'acc', bold=True) + t(180, 56, 'ORDER BY amount DESC LIMIT 10', 8.6, 'ink', mono=True) + t(180, 76, 'each task keeps 10 rows; the reducer merges a few', 8.4, 'ink2') + cap('Limit early, sort little.', '', 'green', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'The export stuck at 99%',
              'A global sort of a huge table funnels everything into one reducer. (Volumes illustrative.)',
              'ORDER BY at scale', 'A global ORDER BY of two billion rows runs on one reducer; alternatives and strict mode', [o1, o2, o3, o4, o5],
              ['Map tasks finish quickly, then the job waits at 99%.',
               'ORDER BY needs a single reducer for a total order: one task sorts everything.',
               'Ask who really needs a global order; often LIMIT, per-key sorting or no sort is enough.',
               'Strict mode rejects ORDER BY without LIMIT, preventing the problem.',
               'ORDER BY … LIMIT stays cheap because each task keeps only its own top rows.'],
              hid='scenario-orderby')

# ---- scenario 2: per-customer sessionisation
p1 = (t(180, 22, 'Task: each customer’s orders in time order', 9.4, bold=True) + t(180, 56, 'a Python script computes gaps between orders', 8.4, 'ink2') + cap('It needs all orders of a customer, sorted, together.', '', 'blue', y=150, h=34))
p2 = (t(180, 22, 'DISTRIBUTE BY customer_id', 9.6, bold=True) + t(180, 56, 'every order of customer 17 → the same reducer', 8.4, 'ink2') + cap('Rows of one customer never split across tasks.', '', 'blue', y=150, h=34))
p3 = (t(180, 22, 'SORT BY customer_id, order_ts', 9.6, bold=True) + t(180, 56, 'inside each reducer: customer by customer, oldest first', 8.4, 'ink2') + cap('Exactly the order the script expects.', '', 'green', y=150, h=34))
p4 = (t(180, 22, 'Feed the script', 9.6, bold=True) + t(180, 52, "SELECT TRANSFORM (customer_id, order_ts, amount)", 8, 'ink', mono=True) + t(180, 66, "USING 'python3 gaps.py' AS (customer_id, gap_hours)", 8, 'ink', mono=True) + t(180, 80, 'FROM (SELECT … DISTRIBUTE BY … SORT BY …) t;', 8, 'ink', mono=True) +
      cap('TRANSFORM is covered in Module 9.', '', 'blue', y=150, h=34))
p5 = (t(180, 22, 'Today: window functions', 9.6, 'acc', bold=True) + t(180, 56, 'LAG(order_ts) OVER (PARTITION BY customer_id ORDER BY order_ts)', 7.6, 'ink', mono=True) + cap('Same idea, pure SQL: Lesson 3.6.', '', 'green', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Per-customer processing with DISTRIBUTE BY and SORT BY',
              'When each key must be processed whole and in order, distribute and sort by that key.',
              'Per-key processing', 'Orders distributed by customer and sorted by time so a script sees each customer’s orders together and in order', [p1, p2, p3, p4, p5],
              ['A script needs every customer’s orders together and in time order.',
               'DISTRIBUTE BY customer_id sends all rows of a customer to one reducer.',
               'SORT BY customer_id, order_ts orders them inside each reducer.',
               'The sorted stream can be fed to a TRANSFORM script.',
               'Window functions do the same job in SQL, partitioned and ordered per customer.'],
              hid='scenario-perkey')

# ---- scenario 3: one file per city
c1 = (t(180, 22, 'Request: one CSV per city for the city teams', 9.4, bold=True) + t(180, 56, '8 cities, 50,000 orders', 8.6, 'ink2') + cap('Can Hive write one file per city?', '', 'blue', y=150, h=34))
c2 = (t(180, 22, 'DISTRIBUTE BY city with 8 reducers', 9.6, bold=True) + t(180, 56, 'each city goes to one reducer…', 8.4, 'ink2') + t(180, 74, '…but hash collisions put two cities in one file', 8.4, 'red', bold=True) + cap('We saw Mumbai and Pune share a file.', '', 'amber', y=150, h=34))
c3 = (t(180, 22, 'Better: partitions', 9.6, 'green', bold=True) + t(180, 56, 'INSERT OVERWRITE TABLE export PARTITION (city) SELECT …', 7.8, 'ink', mono=True) + t(180, 74, 'one folder per city, guaranteed', 8.4, 'ink2') + cap('Dynamic partitions: Module 5.', '', 'green', y=150, h=34))
c4 = (t(180, 22, 'Still useful: sorted inside each file', 9.6, bold=True) + t(180, 56, 'DISTRIBUTE BY city SORT BY city, amount DESC', 8.4, 'ink', mono=True) + cap('Combine with partitions for sorted per-city files.', '', 'blue', y=150, h=34))
c5 = (t(180, 22, 'Rule', 9.6, 'acc', bold=True) + t(180, 56, 'DISTRIBUTE BY = “these rows together”, not “one file each”', 8.4, 'ink2') + cap('Know what each clause guarantees.', '', 'green', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'One file per city? What DISTRIBUTE BY does and does not promise',
              'DISTRIBUTE BY keeps a key together, but several keys can share a reducer. Our real files showed it.',
              'Guarantees', 'DISTRIBUTE BY with hash collisions puts two cities in one file; dynamic partitions give one folder per city', [c1, c2, c3, c4, c5],
              ['City teams each want their own file.',
               'DISTRIBUTE BY keeps each city together, but hashing can place two cities on one reducer, as Mumbai and Pune were.',
               'Dynamic partitions write one folder per city by design.',
               'Use DISTRIBUTE BY and SORT BY to control order inside those files.',
               'DISTRIBUTE BY guarantees “together”, not “alone”.'],
              hid='scenario-files')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>The same 12 rows, sorted four ways</h2>
  <p>Left: the commands and the real files. Right: what each of the three reducers wrote (real contents).</p>
''' + two + '''
  <p>Three live scenarios follow: a huge ORDER BY, per-customer processing and one file per city.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Ordering in real pipelines</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'TOP 10', 10, 'green', bold=True) + t(60, 58, 'ORDER BY … LIMIT', 7.4, 'ink2'),
    '1. Leaderboards',
    'Top restaurants by rating, top customers by spend, latest failed payments: ORDER BY with LIMIT stays fast on any table size.',
    ['Big table', '*ORDER BY … LIMIT', 'Top-N list']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'DISTRIBUTE', 8.6, 'blue', bold=True, mono=True) + t(60, 58, 'per-customer', 7.4, 'ink2'),
    '2. Per-customer processing',
    'Session building, churn features and fraud scoring scripts need each customer’s events together and in time order: DISTRIBUTE BY customer SORT BY time.',
    ['Events', '*DISTRIBUTE + SORT', 'Script / UDF']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'SORT BY', 9, 'violet', bold=True, mono=True) + t(60, 58, 'better ORC', 7.4, 'ink2'),
    '3. Better-compressed files',
    'Writing ORC data sorted by a filter column (SORT BY city, order_date) makes min/max statistics tight, so later queries skip more data.',
    ['INSERT …', '*SORT BY', 'Skippable stripes']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'strict', 10, 'acc', bold=True) + t(60, 58, 'no unlimited sort', 7.4, 'ink2'),
    '4. Cluster guard rails',
    'Shared clusters enable strict checks so a single careless ORDER BY on a billion rows cannot block a reducer slot for hours.',
    ['Query', '*Strict mode', 'Rejected early']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'NULLS LAST', 8.6, 'acc', bold=True, mono=True) + t(60, 58, 'clean reports', 7.4, 'ink2'),
    '5. Readable reports',
    'Reports that sort descending add NULLS LAST so missing values do not crowd the top of the page.',
    ['Report', '*ORDER BY … NULLS LAST', 'Readable list']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> know what a reducer and the shuffle are (<a href="../../01-introduction/04-how-a-hive-query-becomes-a-job/">Lesson 1.4</a>) and how INSERT OVERWRITE DIRECTORY works (<a href="../../02-hiveql/06-alter-drop-and-export/">Lesson 2.6</a>).</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
