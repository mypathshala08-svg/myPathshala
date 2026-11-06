import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='04-dataframes', lesson='05-sorting-distinct-limit-and-union', n='4.5',
    module_label='Module 4 · DataFrames',
    title='Sorting, distinct, limit and union',
    desc='orderBy, sortWithinPartitions, limit, distinct and union in PySpark 4.3.0 on 5 million orders: a global sort that shuffled 120 MiB in 6.7 s against 2.0 s with no shuffle within partitions, where nulls go, a top-5 query planned as TakeOrderedAndProject in 0.8 s, exact versus approximate distinct counts (3,999 vs 3,985), union matching columns by position so that "Card" became a city, unionByName with allowMissingColumns, and intersect, subtract and exceptAll.',
    og_desc='union matches columns by position: our "Card" became a city with no error. Plus a top-5 of 5M rows in 0.8 s with no shuffle. Sorting, distinct, limit and union, measured.',
    minutes=30, level='Beginner → Intermediate',
    lead='Sorting, de-duplicating, taking the top rows and stacking DataFrames are everyday operations with very different costs, and one of them, <code>union</code>, has a silent trap. This lesson measures them on 5 million orders. <b>All outputs are real</b> (PySpark 4.3.0).',
    chips=['PySpark 4.3.0', '5M orders timed', 'union trap reproduced', 'Runs in your browser (Python)'],
)

MAIN = '''# union by position vs unionByName (plain Python model)
app     = {"cols": ["order_id", "city", "payment"], "rows": [(1, "Pune", "UPI")]}
partner = {"cols": ["order_id", "payment", "city"], "rows": [(2, "Card", "Delhi")]}

def union(a, b):                  # by position: b's names are ignored
    return a["rows"] + b["rows"]

def union_by_name(a, b):
    idx = [b["cols"].index(c) for c in a["cols"]]
    return a["rows"] + [tuple(r[i] for i in idx) for r in b["rows"]]

print("columns    :", app["cols"])
print("union      :", union(app, partner))
print("unionByName:", union_by_name(app, partner))
'''
RUN = dict(
    heading='Run the code: union vs unionByName',
    intro='<p>A model of Step 5. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('def union(a, b):                  # by position: b\'s names are ignored', 'In our lab, Card landed in city with no error.'),
        ('    idx = [b["cols"].index(c) for c in a["cols"]]', 'unionByName looks each column up by name.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then add a partner column "tip" and handle it like allowMissingColumns.', code=None),
        dict(label='2 · Predict first: top-k', hint='<b>Predict first:</b> how many rows reach the driver for top 5 with 2 partitions?',
             code='''partitions, k = 2, 5
print(partitions * k, "rows merged on the driver (TakeOrderedAndProject)")
'''),
        dict(label='3 · Nulls in order', hint='Sort with None first (ascending) and last.',
             code='''vals = [300, None, 120]
print(sorted(vals, key=lambda v: (v is not None, v or 0)))
print(sorted(vals, key=lambda v: (v is None, v or 0)))
'''),
        dict(label='4 · Set operations', hint='intersect, subtract and union counts.',
             code='''x, y = set(range(0, 6)), set(range(3, 9))
print(sorted(x & y), sorted(x - y), len(list(range(0, 6)) + list(range(3, 9))), len(x | y))
'''),
        dict(label='5 · Spot the error', hint='This job takes the "latest 10 orders" without ordering.', expect='error',
             code='''query = "orders.limit(10)"
assert "orderBy" in query, "limit without orderBy returns any 10 rows: add orderBy(desc('order_ts'), 'order_id')"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: sorting and unions',
    intro='<p>In the <code>pyspark</code> shell. <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · Nulls in order', cmd='[r.amount for r in d.orderBy("amount").collect()]', file='pyspark',
             output='[None, 120, 300]', note='Ascending: nulls first.'),
        dict(title='2 · union keeps duplicates', cmd='u = spark.range(0, 6, 1, 2).union(spark.range(3, 9, 1, 3))\nu.count(), u.distinct().count(), u.rdd.getNumPartitions()', file='pyspark',
             output='(12, 9, 5)', note='Partitions add up.'),
        dict(title='3 · exceptAll', cmd='sorted(r.id for r in z.exceptAll(w).collect())', file='pyspark',
             output='[1, 2]', note='subtract would give [2].'),
    ],
)

TRACE = dict(
    heading='How top-k avoids a full sort',
    intro='<p>Follow each partition sending only its own top rows.</p>',
    code='''p1, p2 = [530, 120, 840], [300, 760, 210]
k = 2
local = sorted(p1, reverse=True)[:k] + sorted(p2, reverse=True)[:k]
top = sorted(local, reverse=True)[:k]
print(local, top)
''',
    notes={3: 'Per partition :: Each partition keeps only k rows.', 4: 'Driver :: Merges 2 × k rows instead of sorting all.'},
)

WORKED_INTRO = 'Three tasks from TiffinGo reports.'
EXAMPLES = [
    dict(level='b', tag='Sorting · basics', title='Top 3 cities by revenue',
         problem='<p>Return the three cities with the highest revenue.</p>',
         inp='city revenue',
         approach=['groupBy + sum.', 'orderBy desc.', 'limit(3).'],
         code='''rev = {"Mumbai": 2712820, "Bengaluru": 2499060, "Pune": 2148270, "Delhi": 1501340}
print(sorted(rev.items(), key=lambda kv: -kv[1])[:3])
''', notes={2: 'Top-k :: In Spark this is TakeOrderedAndProject, no full sort.'},
         tryit='Revenue from Lesson 4.1.'),
    dict(level='i', tag='Union · feeds', title='Merge three regional feeds safely',
         problem='<p>Combine feeds whose columns differ in order and one lacks tip.</p>',
         inp='north, south, west',
         approach=['unionByName.', 'allowMissingColumns=True.', 'Validate city values.'],
         code='''print("""from functools import reduce
feeds = [north, south, west]
orders = reduce(lambda a, b: a.unionByName(b, allowMissingColumns=True), feeds)""")
''', notes={3: 'Missing :: Columns absent in a feed are filled with null.'},
         tryit='Step 5: union put Card in city.'),
    dict(level='a', tag='Set ops · reconciliation', title='What changed since yesterday?',
         problem='<p>List orders added and removed between two snapshots.</p>',
         inp='yesterday, today',
         approach=['today.exceptAll(yesterday) = added.', 'yesterday.exceptAll(today) = removed.', 'exceptAll keeps duplicates honest.'],
         code='''yesterday, today = [101, 102, 103], [102, 103, 104, 104]
added = [x for x in today if x not in yesterday]
removed = [x for x in yesterday if x not in today]
print("added", added, "removed", removed)
''', notes={2: 'exceptAll :: A repeated 104 shows up twice, like exceptAll.'},
         tryit='subtract would hide the duplicate 104.'),
]

QUIZ = mix([
    dict(q='Beginner: Is sort() different from orderBy()?', options=['Yes', 'No, aliases', 'sort is local', 'orderBy is approximate'], answer=1,
         why='Same plan.'),
    dict(q='Beginner: Where do nulls go in ascending order?', options=['Last', 'First', 'Removed', 'Random'], answer=1,
         why='[None, 120, 300].'),
    dict(q='Beginner: union matches columns by…', options=['Name', 'Position', 'Type', 'Alphabet'], answer=1,
         why='Like UNION ALL.'),
    dict(q='Intermediate: What did orderBy + limit(5) become?', options=['Full sort', 'TakeOrderedAndProject', 'CollectLimit', 'Exchange'], answer=1,
         why='0.8 s, no shuffle.'),
    dict(q='Intermediate: sortWithinPartitions…', options=['Shuffles', 'Sorts each partition without a shuffle', 'Is approximate', 'Returns one partition'], answer=1,
         why='2.0 s vs 6.7 s.'),
    dict(q='Intermediate: union of 2 and 3 partitions has…', options=['2', '3', '5', '200'], answer=2,
         why='No shuffle; partitions concatenate.'),
    dict(q='Advanced: Why use approx_count_distinct?', options=['It is exact', 'It shuffles small sketches instead of values', 'It sorts', 'It caches'], answer=1,
         why='3,985 vs 3,999 here.'),
    dict(q='Advanced: z = [1,1,2], w = [1]. z.exceptAll(w) gives…', options=['[2]', '[1, 2]', '[1, 1, 2]', '[]'], answer=1,
         why='Removes one copy per match.'),
])

REVISION = [
    '<code>orderBy</code> = <code>sort</code>: range shuffle + sampling (5M rows: 6.7 s, 120 MiB).',
    '<code>sortWithinPartitions</code>: no shuffle (2.0 s).',
    'Ascending → nulls first; descending → nulls last; use <code>asc_nulls_last</code> etc.',
    '<code>orderBy().limit(k)</code> → <b>TakeOrderedAndProject</b> (0.8 s); <code>limit</code> without order = any rows.',
    '<code>distinct</code>/<code>countDistinct</code> shuffle; <code>approx_count_distinct</code> uses sketches.',
    '<code>union</code> = by <b>position</b>, keeps duplicates; <code>unionByName(allowMissingColumns=True)</code>.',
    'Set ops: <code>intersect</code>, <code>subtract</code>, <code>exceptAll</code>, <code>intersectAll</code>.',
]
FAQ = [
    ('Is unionAll different from union?', 'No. In DataFrames both keep duplicates; unionAll is an older alias.'),
    ('Does orderBy before write keep the order in files?', 'Rows are sorted across output files, but readers do not guarantee order unless they sort again. Sort when you read for a report.'),
    ('How does Spark choose range boundaries?', 'It samples the data (the extra job we saw) and picks boundaries so partitions are roughly equal; skewed keys can still make one partition large.'),
    ('Is limit cheap on any plan?', 'Only when Spark can stop early. After a wide transformation such as groupBy, the whole input is still processed.'),
    ('Can I sort by an expression?', 'Yes: <code>df.orderBy(F.length("city").desc())</code> or <code>df.orderBy(F.expr("amount * 1.05"))</code>.'),
]

PRACTICE_INTRO = 'Programs about order, distinct values and set operations.'
PROBLEMS = [
    dict(level='easy', title='Shuffle saved', stmt='Seconds saved by sorting within partitions.', inp='6.7 vs 2.0',
         code='''print(round(6.7 - 2.0, 1))
''', explain='No range shuffle.'),
    dict(level='easy', title='Approx error', stmt='Relative error of the estimate.', inp='3,985 vs 3,999',
         code='''print(f"{abs(3985 - 3999) / 3999:.2%}")
''', explain='Well inside the default 5%.'),
    dict(level='easy', title='Top 2', stmt='Top 2 amounts.', inp='[530, 120, 840, 300]',
         code='''print(sorted([530, 120, 840, 300], reverse=True)[:2])
''', explain='orderBy(desc).limit(2).'),
    dict(level='medium', title='UNION semantics', stmt='Rows after UNION (distinct) of two lists.', inp='0..5 and 3..8',
         code='''print(len(set(range(0, 6)) | set(range(3, 9))))
''', explain='union().distinct() = 9.'),
    dict(level='medium', title='Reorder columns', stmt='Reorder a row to match another column order.', inp='partner order',
         code='''target = ["order_id", "city", "payment"]
src = {"order_id": 2, "payment": "Card", "city": "Delhi"}
print(tuple(src[c] for c in target))
''', explain='What unionByName does.'),
    dict(level='medium', title='Partitions after unions', stmt='Partitions after unioning 30 daily DataFrames of 4 partitions.', inp='30 × 4',
         code='''print(30 * 4)
''', explain='Coalesce afterwards if they are small.'),
    dict(level='business', title='Wrong city orders', stmt='Share of orders in a fake city after the bad union.', inp='partner 12,000 of 62,000',
         code='''print(f"{12000 / 62000:.1%}")
''', explain='All partner rows were affected.'),
    dict(level='business', title='Leaderboard', stmt='Top 3 restaurants by orders.', inp='counts',
         code='''c = {"Desai Mess": 812, "Nair Bhojanalay": 790, "Patel Thali": 845, "Rao Tiffins": 640}
print(sorted(c, key=c.get, reverse=True)[:3])
''', explain='groupBy, count, orderBy, limit.'),
]

SCN_INTRO = 'These operations look simple; interviewers ask about their cost and traps.'
SCENARIOS = (
    scn('Any company · PySpark', 'Fresher', '“union vs unionByName?”',
        'What is the difference between union and unionByName?',
        'do you know resolution rules?',
        '<p><code>union</code> stacks rows by column position and keeps duplicates; it does not check names, so same-typed columns in another order get mixed silently. <code>unionByName</code> matches names and can fill missing columns with <code>allowMissingColumns=True</code>.</p>', '“union removes duplicates.”') +
    scn('Data engineering', 'Fresher', 'Top N efficiently',
        'Return the 10 biggest orders out of a billion.',
        'do you know top-k planning?',
        '''<ul>
          <li><code>orderBy(F.desc("amount")).limit(10)</code>.</li>
          <li>Spark plans TakeOrderedAndProject: k rows per partition, merged on the driver.</li>
          <li>No full sort; 0.8 s on 5M rows in my test.</li>
        </ul>''', 'Sorting everything and calling take(10) on a cached result.') +
    scn('Data engineering', 'Mid-level', 'Slow orderBy before write',
        'A job sorts all data before writing and is slow.',
        'can you remove unnecessary shuffles?',
        '''<ol>
          <li>Ask whether a global order is needed.</li>
          <li>Use sortWithinPartitions or partitionBy on write.</li>
          <li>Our lab: 6.7 s and 120 MiB vs 2.0 s and 0.</li>
        </ol>''', 'Increasing executors first.') +
    scn('Analytics', 'Senior', 'Distinct users at scale',
        'Dashboards count distinct users on billions of events every few minutes.',
        'do you know approximate algorithms?',
        '''<ul>
          <li>approx_count_distinct (HyperLogLog) with a chosen rsd.</li>
          <li>Pre-aggregate sketches per hour/day where possible.</li>
          <li>Exact counts only for billing or audits.</li>
        </ul>''', 'Exact distinct everywhere.')
)
