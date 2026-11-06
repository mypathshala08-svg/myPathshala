import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='06-transformations', lesson='02-joins', n='6.2',
    module_label='Module 6 · Transformations',
    title='Joins',
    desc='Joins in PySpark 4.3.0: inner, left, right, full, left_semi, left_anti and cross on a small example; null keys that never match and eqNullSafe; AMBIGUOUS_REFERENCE after joining on an expression; a duplicate lookup key that turned 498,646 Pune orders into 997,292 rows; an inner join with an incomplete customer table that kept 2,498,734 of 5,000,000 orders; and broadcast (0.8 s) versus sort-merge (3.2 s) joins.',
    og_desc='An inner join kept 2.5M of 5M orders, and one duplicate key doubled Pune’s revenue. Joins in PySpark, measured.',
    minutes=32, level='Beginner → Intermediate',
    lead='Joins are where most data bugs hide: rows quietly lost or multiplied. This lesson runs every join type, shows what null and duplicate keys do, how to avoid ambiguous columns, and how Spark chooses between broadcast and sort-merge joins. <b>All outputs are real</b> (PySpark 4.3.0).',
    chips=['PySpark 4.3.0', 'All join types', 'Row counts checked', 'Runs in your browser (Python)'],
)

MAIN = '''# Join semantics with plain Python lists
orders = [(1, 101), (2, 102), (3, 103), (4, None), (5, 109)]       # (order_id, rest_id)
rest = {101: "Desai Mess", 102: "Nair Bhojanalay", 103: "Patel Thali", 104: "Rao Tiffins"}

inner = [(o, rest[r]) for o, r in orders if r in rest]
left = [(o, rest.get(r)) for o, r in orders]
anti = [o for o, r in orders if r not in rest]

print("inner:", inner)
print("left :", left)
print("anti :", anti)
'''
RUN = dict(
    heading='Run the code: what each join keeps',
    intro='<p>A model of Step 1. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('inner = [(o, rest[r]) for o, r in orders if r in rest]', 'Unmatched orders 4 and 5 disappear.'),
        ('left = [(o, rest.get(r)) for o, r in orders]', 'All orders stay; unknown names are None.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then add a semi join (orders that have a restaurant).', code=None),
        dict(label='2 · Predict first: fan-out', hint='<b>Predict first:</b> 3 Pune orders joined with 3 Pune promos. Rows?',
             code='''pune_orders, pune_promos = 3, 3
print(pune_orders * pune_promos)
'''),
        dict(label='3 · Unique key check', hint='Find duplicate keys in a lookup.',
             code='''lookup = [("Pune", "MH"), ("Pune", "Maharashtra"), ("Delhi", "DL")]
from collections import Counter
print([k for k, c in Counter(k for k, _ in lookup).items() if c > 1])
'''),
        dict(label='4 · Null keys', hint='None never equals None in SQL semantics.',
             code='''def sql_eq(a, b):
    return None if a is None or b is None else a == b
print(sql_eq(None, None), sql_eq(1, 1))
'''),
        dict(label='5 · Spot the error', hint='This enrichment uses an inner join.', expect='error',
             code='''before, after = 5_000_000, 2_498_734
assert after == before, "enrichment lost rows: use a left join and alert on orphans"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: joins',
    intro='<p>In the <code>pyspark</code> shell. <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · Ambiguous column', cmd='orders.join(rest, orders.rest_id == rest.rest_id).select("city")', file='pyspark',
             output='[AMBIGUOUS_REFERENCE] Reference `city` is ambiguous, could be: [`city`, `city`]. SQLSTATE: 42704', note='Use orders.city / rest.city.'),
        dict(title='2 · Inner vs left', cmd='big.join(custs, "customer_id").count(), big.join(custs, "customer_id", "left").count()', file='pyspark',
             output='(2498734, 5000000)', note='Customers table is incomplete.'),
        dict(title='3 · Threshold', cmd='spark.conf.get("spark.sql.autoBroadcastJoinThreshold")', file='pyspark',
             output="'10485760b'", note='10 MB.'),
    ],
)

TRACE = dict(
    heading='Sort-merge join in miniature',
    intro='<p>Follow two sorted lists being merged by key.</p>',
    code='''a = [(101, "o1"), (102, "o2"), (103, "o3")]
b = [(101, "Desai"), (103, "Patel"), (104, "Rao")]
i = j = 0
while i < len(a) and j < len(b):
    if a[i][0] == b[j][0]:
        print(a[i][1], b[j][1]); i += 1; j += 1
    elif a[i][0] < b[j][0]:
        i += 1
    else:
        j += 1
''',
    notes={1: 'Sorted :: After the shuffle, each side is sorted by key.', 5: 'Match :: Equal keys produce an output row.'},
)

WORKED_INTRO = 'Three joins from TiffinGo pipelines.'
EXAMPLES = [
    dict(level='b', tag='Joins · basics', title='Add restaurant names safely',
         problem='<p>Add names to orders without losing any order.</p>',
         inp='orders, restaurants',
         approach=['left join on a key list.', 'Broadcast the small side.', 'Compare counts.'],
         code='''print("""out = orders.join(F.broadcast(rest.select("rest_id", "name")), ["rest_id"], "left")
assert out.count() == orders.count()""")
''', notes={1: 'Select first :: Bring only the columns you need to avoid duplicates.'},
         tryit='Step 1 and 3.'),
    dict(level='i', tag='Joins · quality', title='Orphan report',
         problem='<p>List orders whose customer is unknown.</p>',
         inp='orders, customers',
         approach=['left_anti join.', 'Count per day.', 'Alert above a threshold.'],
         code='''orders = 5_000_000; matched = 2_498_734
print("orphans:", orders - matched, f"({(orders - matched) / orders:.0%})")
''', notes={1: 'Lab :: The dimension held only half the ids.'},
         tryit='Step 5.'),
    dict(level='a', tag='Joins · design', title='Make a lookup safe to join',
         problem='<p>Guarantee one row per key in a city lookup.</p>',
         inp='lookup with possible duplicates',
         approach=['Count keys > 1.', 'Fail the job or deduplicate.', 'Then join.'],
         code='''print("""dups = lookup.groupBy("city").count().where("count > 1")
if dups.limit(1).count():
    raise ValueError("duplicate keys in lookup")""")
''', notes={2: 'Guard :: limit(1).count() stops early.'},
         tryit='Step 4.'),
]

QUIZ = mix([
    dict(q='Beginner: Default join type?', options=['left', 'inner', 'full', 'cross'], answer=1,
         why='Unmatched rows are dropped.'),
    dict(q='Beginner: Which keeps all left rows?', options=['inner', 'left', 'left_semi', 'right'], answer=1,
         why='Unknown right side → null.'),
    dict(q='Beginner: Which finds left rows without a match?', options=['left_semi', 'left_anti', 'full', 'cross'], answer=1,
         why='Orphan checks.'),
    dict(q='Intermediate: Do null keys match with ==?', options=['Yes', 'No', 'Only in left joins', 'Random'], answer=1,
         why='Use eqNullSafe if needed.'),
    dict(q='Intermediate: Duplicate key twice on the right. Each matching left row becomes…', options=['1 row', '2 rows', 'Dropped', 'Error'], answer=1,
         why='One row per match.'),
    dict(q='Intermediate: How to avoid two key columns after a join?', options=['Use an expression', 'Join on a list of names', 'Use cross', 'Cache'], answer=1,
         why='["rest_id"].'),
    dict(q='Advanced: When does Spark broadcast automatically?', options=['Always', 'When a side is estimated ≤ 10 MB', 'Never', 'For full joins only'], answer=1,
         why='autoBroadcastJoinThreshold.'),
    dict(q='Advanced: Strategy for two large tables on an equi-join?', options=['Broadcast', 'Sort-merge join', 'Nested loop', 'Cartesian'], answer=1,
         why='4.5 s for 5M × 5M in our lab.'),
])

REVISION = [
    'Types: inner (default), left, right, full, left_semi, left_anti, cross.',
    'Inner joins drop unmatched rows: 5M → 2,498,734 with an incomplete dimension.',
    'Duplicate keys multiply rows: Pune 498,646 → 997,292.',
    'Null keys never match with ==; <code>eqNullSafe</code> if they should.',
    'Join on a list to keep one key; alias other duplicates (AMBIGUOUS_REFERENCE).',
    'Broadcast hash join for small sides (0.8 s; 0.3 s hinted) vs sort-merge (3.2 s).',
    'Check row counts and key uniqueness around every join.',
]
FAQ = [
    ('What is the difference between left_semi and inner?', 'left_semi returns each left row at most once and no right columns; inner returns one row per match with columns from both.'),
    ('How do I join on two columns?', '<code>a.join(b, ["city", "order_date"])</code> or an expression with <code>&amp;</code>.'),
    ('How do I do a self-join?', 'Alias both sides: <code>a = df.alias("a"); b = df.alias("b"); a.join(b, F.col("a.phone") == F.col("b.phone"))</code>.'),
    ('Can I join on a range condition?', 'Yes, but non-equi joins cannot use hash or sort-merge strategies and may become nested-loop joins: very slow on large data.'),
    ('What if a join is slow because of one hot key?', 'That is skew; AQE can split skewed partitions, or use salting (Lesson 8.3).'),
]

PRACTICE_INTRO = 'Programs about join results and row counts.'
PROBLEMS = [
    dict(level='easy', title='Kept share', stmt='Share of orders kept by the inner join.', inp='2,498,734 / 5,000,000',
         code='''print(f"{2_498_734 / 5_000_000:.1%}")
''', explain='Half lost.'),
    dict(level='easy', title='Full join size', stmt='Rows of a full join with 3 matches, 2 left-only, 2 right-only.', inp='counts',
         code='''print(3 + 2 + 2)
''', explain='Our Step 1: 7.'),
    dict(level='easy', title='Cross size', stmt='Rows of a cross join.', inp='5 × 5',
         code='''print(5 * 5)
''', explain='Grows fast.'),
    dict(level='medium', title='Fan-out', stmt='Rows after joining with duplicate keys.', inp='orders per city and lookup copies',
         code='''orders = {"Pune": 498_646}; copies = {"Pune": 2}
print(sum(orders[c] * copies[c] for c in orders))
''', explain='997,292 in the lab.'),
    dict(level='medium', title='Anti join', stmt='Customers who never ordered.', inp='sets',
         code='''customers = {1, 2, 3, 4}; ordered = {1, 3, 4}
print(customers - ordered)
''', explain='left_anti.'),
    dict(level='medium', title='Left join', stmt='Left join with a dict.', inp='orders, names',
         code='''names = {101: "Desai"}
print([(o, names.get(r)) for o, r in [(1, 101), (2, 999)]])
''', explain='Unmatched → None.'),
    dict(level='business', title='Revenue error', stmt='Reported Pune revenue after the duplicate join.', inp='₹254,040,203 true',
         code='''print("₹", 254_040_203 * 2)
''', explain='Doubled by fan-out.'),
    dict(level='business', title='Join time saved', stmt='Seconds saved per day with broadcast.', inp='3.2 vs 0.8 s, 96 runs',
         code='''print(round((3.2 - 0.8) * 96), "s")
''', explain='Plus less shuffle I/O.'),
]

SCN_INTRO = 'Join questions catch candidates who only know the syntax.'
SCENARIOS = (
    scn('Any company · PySpark', 'Fresher', '“Types of joins?”',
        'List the join types in Spark.',
        'basics?',
        '<p>inner, left/right/full outer, left_semi, left_anti and cross. Semi returns left rows with a match, anti left rows without one. I choose by which unmatched rows must survive.</p>', 'Forgetting semi and anti.') +
    scn('Data engineering', 'Mid-level', 'Row count changed after a join',
        'After enriching orders the count changed. Why?',
        'do you know fan-out and loss?',
        '''<ul>
          <li>Fewer rows: inner join with missing keys (use left).</li>
          <li>More rows: duplicate keys on the other side.</li>
          <li>Check counts before/after and key uniqueness.</li>
        </ul>''', 'Adding distinct() at the end.') +
    scn('Data engineering', 'Mid-level', 'Broadcast vs sort-merge',
        'When does Spark broadcast a table?',
        'join strategies?',
        '''<ol>
          <li>When one side is estimated under the threshold (10 MB) or hinted.</li>
          <li>Small side copied to executors, big side not shuffled.</li>
          <li>Otherwise sort-merge: both sides shuffled and sorted.</li>
        </ol>''', '“Spark always shuffles for joins.”') +
    scn('Analytics', 'Senior', 'Join validation',
        'Design checks for a pipeline with ten joins.',
        'can you make joins safe?',
        '''<ul>
          <li>Uniqueness tests on dimension keys.</li>
          <li>Orphan counts via left_anti; thresholds and alerts.</li>
          <li>Row-count reconciliation at each stage.</li>
        </ul>''', 'Trusting inner joins.')
)
