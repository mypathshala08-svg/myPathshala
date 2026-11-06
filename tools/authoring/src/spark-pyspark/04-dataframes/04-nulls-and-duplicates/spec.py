import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='04-dataframes', lesson='04-nulls-and-duplicates', n='4.4',
    module_label='Module 4 · DataFrames',
    title='Nulls and duplicates',
    desc='Handling missing values and duplicate rows in PySpark 4.3.0 on a dirty TiffinGo sign-up export: null counts per column, "NA" strings and NaN that are not null, three-valued logic that made 404 + 1,642 miss 154 rows, count(col) and avg skipping nulls, na.drop keeping only 742 of 2,200 rows, type-aware na.fill, distinct versus dropDuplicates, and proof that dropDuplicates keeps different rows on different runs while row_number() does not.',
    og_desc='dropDuplicates kept different rows on three runs; row_number() kept the same. And a != filter lost 154 users. Nulls and duplicates in PySpark, measured.',
    minutes=34, level='Beginner → Intermediate',
    lead='Real data has gaps and repeats. This lesson shows how Spark treats <b>null</b> in filters and aggregates, how to drop and fill missing values without damaging your data, and how to remove <b>duplicates</b> so the same rows survive every run. <b>All outputs are real</b> (PySpark 4.3.0).',
    chips=['PySpark 4.3.0', 'Dirty sign-up export', 'Non-determinism proven', 'Runs in your browser (Python)'],
)

MAIN = '''# Three-valued logic: what a filter keeps
cities = ["Pune", "Delhi", None, "Pune", None, "Mumbai"]

def not_pune(c):
    if c is None:
        return None              # unknown, like SQL NULL
    return c != "Pune"

kept = [c for c in cities if not_pune(c) is True]   # a filter keeps only True
print("= Pune :", sum(c == "Pune" for c in cities))
print("!= Pune:", len(kept))
print("null   :", cities.count(None))
print("total  :", len(cities))
'''
RUN = dict(
    heading='Run the code: why rows disappear',
    intro='<p>A model of Step 3. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('        return None              # unknown, like SQL NULL', 'In Spark, null != \'Pune\' is null, not true.'),
        ('kept = [c for c in cities if not_pune(c) is True]   # a filter keeps only True', 'Our lab: 404 + 1,642 = 2,046 of 2,200 rows.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then make not_pune treat None as “not Pune” (like eqNullSafe).', code=None),
        dict(label='2 · Predict first: average', hint='<b>Predict first:</b> avg of [25, 32, None, 41] in Spark, and sum / rows.',
             code='''ages = [25, 32, None, 41]
known = [a for a in ages if a is not None]
print("avg  :", sum(known) / len(known))
print("sum/n:", sum(known) / len(ages))
'''),
        dict(label='3 · Type-aware fill', hint='fill(0) touches only numeric columns.',
             code='''row = {"city": None, "age": None, "rating": None}
types = {"city": str, "age": int, "rating": float}
print({k: (0 if v is None and types[k] in (int, float) else v) for k, v in row.items()})
'''),
        dict(label='4 · Deterministic dedup', hint='Keep the earliest sign-up per user.',
             code='''rows = [(1425, "10-17 11:02"), (1425, "10-15 03:55"), (1738, "10-20 21:53")]
first = {}
for uid, ts in sorted(rows, key=lambda r: (r[0], r[1])):
    first.setdefault(uid, ts)
print(first)
'''),
        dict(label='5 · Spot the error', hint='This cleaning step drops every row with any null.', expect='error',
             code='''kept, total = 742, 2200
assert kept / total > 0.9, "na.drop() with how='any' removed two thirds of the rows: use subset or thresh"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: nulls',
    intro='<p>In the <code>pyspark</code> shell. <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · Null logic', cmd='spark.sql("SELECT NULL = NULL, NULL <=> NULL").first()', file='pyspark',
             output='Row((NULL = NULL)=None, (NULL <=> NULL)=True)', note='Equality with null is unknown.'),
        dict(title='2 · count(col) vs count(*)', cmd='s.select(F.count("*"), F.count("age")).first()', file='pyspark',
             output='Row(count(1)=2200, count(age)=2082)', note='Nulls are not counted.'),
        dict(title='3 · Duplicates', cmd='s.count(), s.distinct().count(), s.dropDuplicates(["user_id"]).count()', file='pyspark',
             output='(2200, 2080, 2000)', note='120 exact copies, 80 repeat sign-ups.'),
    ],
)

TRACE = dict(
    heading='Which duplicate does first() keep?',
    intro='<p>Follow how the kept row depends on the order rows arrive in.</p>',
    code='''def keep_first(rows):
    seen = {}
    for uid, ts in rows:
        seen.setdefault(uid, ts)
    return seen
a = [(1425, "10-15"), (1425, "10-17")]
print(keep_first(a), keep_first(list(reversed(a))))
''',
    notes={4: 'first() :: Keeps whichever row comes first in its partition.', 7: 'Order :: A different partitioning gives a different winner.'},
)

WORKED_INTRO = 'Three cleaning tasks on the sign-up export.'
EXAMPLES = [
    dict(level='b', tag='Nulls · basics', title='A null report',
         problem='<p>Print the share of nulls per column.</p>',
         inp='null counts from Step 2',
         approach=['Count nulls per column in one select.', 'Divide by row count.', 'Sort descending.'],
         code='''nulls = {"phone": 77, "city": 154, "referral": 850, "age": 118, "rating": 776}
for c, n in sorted(nulls.items(), key=lambda x: -x[1]):
    print(f"{c:9} {n / 2200:6.1%}")
''', notes={2: 'Order :: Look at the worst columns first.'},
         tryit='Run it daily and alert on jumps.'),
    dict(level='i', tag='Nulls · cleaning', title='Per-column fill policy',
         problem='<p>Fill nulls with sensible defaults per column.</p>',
         inp='city, referral, rating',
         approach=['city → "unknown".', 'referral → "none".', 'rating stays null (do not invent ratings).'],
         code='''policy = {"city": "unknown", "referral": "none"}
print("s.na.fill(", policy, ")")
print("rating: keep null; avg ignores it")
''', notes={1: 'Dict :: na.fill with a dict sets a value per column.'},
         tryit='Step 5 shows fill(0) touching only numbers.'),
    dict(level='a', tag='Duplicates · deterministic', title='Latest record per key',
         problem='<p>Keep the newest row per user, the same on every run.</p>',
         inp='user_id, signed_up_at, city',
         approach=['Window by user_id.', 'Order by signed_up_at desc, then a tiebreaker.', 'row_number() == 1.'],
         code='''print("""w = Window.partitionBy("user_id").orderBy(F.desc("signed_up_at"), F.col("email"))
latest = df.withColumn("rn", F.row_number().over(w)).where("rn = 1").drop("rn")""")
''', notes={1: 'Tiebreaker :: Two rows with the same time still need a fixed order.'},
         tryit='Lesson 6.3 covers windows fully.'),
]

QUIZ = mix([
    dict(q='Beginner: What does NULL = NULL return?', options=['true', 'false', 'NULL', 'error'], answer=2,
         why='Unknown compared with unknown is unknown.'),
    dict(q='Beginner: Which counts only non-null values?', options=['count(*)', 'count(col)', 'both', 'neither'], answer=1,
         why='2,082 vs 2,200 in our lab.'),
    dict(q='Beginner: How do you make "NA" in a CSV read as null?', options=['inferSchema', 'nullValue="NA"', 'na.drop', 'header=True'], answer=1,
         why='61 NA cities became null.'),
    dict(q='Intermediate: Is NaN the same as null?', options=['Yes', 'No, NaN is a double value', 'Only in pandas', 'Only in JSON'], answer=1,
         why='Use F.isnan().'),
    dict(q='Intermediate: What does na.fill(0) do to string columns?', options=['Puts "0"', 'Nothing', 'Error', 'Drops them'], answer=1,
         why='fill is type-aware.'),
    dict(q='Intermediate: How many rows did na.drop() keep?', options=['2,200', '2,152', '742', '0'], answer=2,
         why='how="any" drops rows with any null.'),
    dict(q='Advanced: Why is dropDuplicates(["user_id"]) non-deterministic?', options=['It samples', 'It keeps first() of each column, which depends on row order', 'It uses random seeds', 'It is not'], answer=1,
         why='Three checksums in our lab.'),
    dict(q='Advanced: Which keeps the earliest sign-up per user reliably?', options=['distinct()', 'dropDuplicates', 'row_number() over a window ordered by time', 'limit(1)'], answer=2,
         why='Explicit ordering plus a tiebreaker.'),
])

REVISION = [
    'Null = unknown. Count nulls per column first; <code>"NA"</code> strings and <b>NaN</b> are not null.',
    'Three-valued logic: <code>null != \'Pune\'</code> is null, filters drop it (404 + 1,642 ≠ 2,200).',
    '<code>isNull()</code>, <code>eqNullSafe</code> / <code>&lt;=&gt;</code>, <code>coalesce()</code>.',
    'Aggregates skip nulls: <code>count(col)</code> 2,082, <code>avg</code> 38.85.',
    '<code>na.drop</code> (how, thresh, subset): default kept only 742 rows. <code>na.fill</code> is type-aware.',
    '<code>distinct()</code> = all columns (2,080); <code>dropDuplicates(subset)</code> = keys (2,000).',
    'dropDuplicates keeps an arbitrary row; use <code>row_number()</code> with an ordered window.',
]
FAQ = [
    ('What is the difference between distinct() and dropDuplicates()?', 'Without arguments they are the same. dropDuplicates(subset) compares only the listed columns and keeps one arbitrary row per key.'),
    ('Does dropDuplicates work in streaming?', 'Yes, with a watermark to bound state; Spark 3.5+ also has dropDuplicatesWithinWatermark (Module 9).'),
    ('How do nulls sort?', 'First in ascending order and last in descending by default; use asc_nulls_last etc. (Lesson 4.5).'),
    ('How do nulls behave in joins?', 'A null key never matches with ==; use eqNullSafe if nulls should match (Lesson 6.2).'),
    ('Is it faster to dedup with row_number?', 'It needs a sort within each key, so it can cost more than dropDuplicates; pay it when you need the same answer every run.'),
]

PRACTICE_INTRO = 'Programs about missing values and duplicates.'
PROBLEMS = [
    dict(level='easy', title='Missing rows', stmt='Rows missed by = and != filters.', inp='2,200 total, 404 and 1,642',
         code='''print(2200 - 404 - 1642)
''', explain='The null cities.'),
    dict(level='easy', title='coalesce', stmt='First non-null of several values.', inp='None, None, "Pune"',
         code='''vals = [None, None, "Pune"]
print(next((v for v in vals if v is not None), None))
''', explain='F.coalesce(c1, c2, c3).'),
    dict(level='easy', title='Exact copies', stmt='Exact duplicates removed by distinct().', inp='2,200 → 2,080',
         code='''print(2200 - 2080)
''', explain='App retries.'),
    dict(level='medium', title='Null share', stmt='Columns above 10% nulls.', inp='null counts',
         code='''nulls = {"phone": 77, "city": 154, "referral": 850, "age": 118, "rating": 776}
print([c for c, n in nulls.items() if n / 2200 > 0.10])
''', explain='Candidates for a fill policy or a source fix.'),
    dict(level='medium', title='thresh', stmt='Keep rows with at least k non-null values.', inp='k = 3',
         code='''rows = [(1, None, None), (2, "Pune", 25), (3, None, 30)]
print([r for r in rows if sum(v is not None for v in r) >= 3])
''', explain='na.drop(thresh=3).'),
    dict(level='medium', title='Latest per key', stmt='Keep the latest row per id.', inp='(id, ts) pairs',
         code='''rows = [(1, 5), (1, 9), (2, 3), (2, 3)]
best = {}
for i, ts in rows:
    best[i] = max(best.get(i, ts), ts)
print(best)
''', explain='row_number ordered by ts desc.'),
    dict(level='business', title='Duplicate cost', stmt='SMS cost of messaging duplicate sign-ups twice.', inp='200 extra rows, ₹0.20 each, daily',
         code='''print("₹", round(200 * 0.20 * 30, 2), "per month")
''', explain='Dedup before campaigns.'),
    dict(level='business', title='Unknown bucket', stmt='Build the three-bucket report.', inp='Pune 404, other 1,642, unknown 154',
         code='''r = {"Pune": 404, "other": 1642, "unknown": 154}
print(r, "total", sum(r.values()))
''', explain='Totals reconcile with the raw count.'),
]

SCN_INTRO = 'Null and duplicate questions separate people who have cleaned real data.'
SCENARIOS = (
    scn('Any company · PySpark', 'Fresher', '“How do you handle nulls?”',
        'How do you find and handle missing values in a DataFrame?',
        'do you know the toolkit?',
        '<p>Count nulls per column with one select. Normalise other forms of missing (NA strings, NaN). Then decide per column: <code>na.drop(subset=…)</code>, <code>na.fill({…})</code>, <code>coalesce</code>, or keep the null and use null-safe logic. I remember that filters and aggregates silently skip nulls.</p>', '“I always use na.drop().”') +
    scn('Data engineering', 'Mid-level', 'Counts don’t reconcile',
        'Pune + not-Pune counts are less than the total. Why?',
        'do you know three-valued logic?',
        '''<ul>
          <li>Null cities give null for both = and !=; filters drop them.</li>
          <li>Use isNull for a third bucket or eqNullSafe.</li>
          <li>Our lab: 404 + 1,642 + 154 null = 2,200.</li>
        </ul>''', 'Suspecting a Spark bug.') +
    scn('Data engineering', 'Mid-level', 'Dedup gives different results',
        'The deduplicated table changes between runs.',
        'do you know dropDuplicates semantics?',
        '''<ol>
          <li>dropDuplicates keeps an arbitrary row per key (first() per column).</li>
          <li>Use row_number over a window ordered by a timestamp and a tiebreaker.</li>
          <li>Or min_by/max_by in an aggregation.</li>
        </ol>''', 'Adding orderBy before dropDuplicates and assuming it is kept.') +
    scn('Analytics', 'Senior', 'Data quality checks',
        'Design null and duplicate checks for a daily feed.',
        'can you make quality measurable?',
        '''<ul>
          <li>Per-column null rates and duplicate-key counts stored daily.</li>
          <li>Thresholds per column; fail or quarantine above them.</li>
          <li>Fix at the source (required fields, idempotent event ids).</li>
        </ul>''', 'Filling everything with zeros.')
)
