import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()
BODY = body(HERE)

META = dict(
    module='02-rdds', lesson='05-pair-rdds-and-word-count', n='2.5',
    module_label='Module 2 · RDDs: Spark’s foundation',
    title='Pair RDDs and the word count',
    desc='The classic PySpark word count on 24,000 real-looking TiffinGo reviews, the same result with DataFrames (split, explode, groupBy), and the pair-RDD toolkit on orders: countByKey, aggregateByKey for averages per city, combineByKey for (min, max), sortByKey, and a join of 50,001 orders with 2,000 customers for revenue per plan, with checks that catch join mistakes. Real PySpark 4.3.0 outputs throughout.',
    og_desc='The word count every interviewer asks for, on real review text, plus averages, ranges and joins with pair RDDs, and the DataFrame version that gives the same answer.',
    minutes=34, level='Beginner → Intermediate',
    lead='The <b>word count</b> is the “hello world” of big data and the doorway to <b>pair RDDs</b>: once data is in (key, value) form, Spark can count, average, sort and join by key. This lesson answers real TiffinGo questions with them and checks every answer against a DataFrame. <b>All outputs are real</b> (PySpark 4.3.0).',
    chips=['PySpark 4.3.0', 'Word count on 24,000 reviews', 'aggregateByKey · combineByKey · join', 'Runs in your browser (Python)'],
)

MAIN = '''# The word count, partition by partition (plain Python)
from collections import Counter
partitions = [
    ["poha was tasty and hot", "idli was cold and late"],
    ["dosa was tasty and fresh", "poha was cold and oily"],
]
stop = {"was", "and"}

partials = []
for p in partitions:                                   # map side: one task per partition
    c = Counter(w for line in p for w in line.lower().split() if w not in stop)
    partials.append(c)
print("per partition:", [dict(c) for c in partials])

total = sum(partials, Counter())                       # after the shuffle
print("top 3:", total.most_common(3))
'''
RUN = dict(
    heading='Run the code: word count by hand',
    intro='<p>Each partition counts its own words (the map-side combine of reduceByKey), then the partial counts are added. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('    c = Counter(w for line in p for w in line.lower().split() if w not in stop)', 'flatMap + filter + map((w, 1)) + local reduce, in one line.'),
        ('total = sum(partials, Counter())                       # after the shuffle', 'reduceByKey’s final step: partial counts for the same word are added.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then remove the stop-word filter and see what tops the list.', code=None),
        dict(label='2 · Predict first: average per city', hint='<b>Predict first:</b> carry (sum, count) per city across two partitions.',
             code='''p1 = [("Mumbai", 530), ("Pune", 210), ("Mumbai", 480)]
p2 = [("Mumbai", 120), ("Pune", 340)]
acc = {}
for part in (p1, p2):
    for city, amt in part:
        s, n = acc.get(city, (0, 0))
        acc[city] = (s + amt, n + 1)
print({c: round(s / n, 2) for c, (s, n) in acc.items()})
'''),
        dict(label='3 · Compound keys', hint='Count complaint words per dish with a (dish, word) key.',
             code='''from collections import Counter
lines = ["biryani was cold and late", "poha was tasty and hot", "biryani was cold and oily"]
bad = {"cold", "late", "oily", "spilled"}
c = Counter((l.split(" was ")[0], w) for l in lines for w in l.split() if w in bad)
print(c.most_common())
'''),
        dict(label='4 · Join by key', hint='Join orders with customer plans, then revenue per plan.',
             code='''orders = [("c1", 530), ("c2", 210), ("c1", 480)]
plans = {"c1": "Gold", "c2": "Basic"}
rev = {}
for cid, amt in orders:
    rev[plans[cid]] = rev.get(plans[cid], 0) + amt
print(rev)
'''),
        dict(label='5 · Spot the error', hint='This averages the partition averages.', expect='error',
             code='''p1, p2 = [100], [300, 300, 300]
wrong = (sum(p1) / len(p1) + sum(p2) / len(p2)) / 2
right = (sum(p1) + sum(p2)) / (len(p1) + len(p2))
assert wrong == right, f"average of averages {wrong} != true average {right}: carry (sum, count)"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: the word count and friends',
    intro='<p>In the <code>pyspark</code> shell with the course data. <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · Word count, one line', cmd='from operator import add\nsc.textFile("reviews").flatMap(lambda l: l.lower().split()).map(lambda w: (w, 1)).reduceByKey(add).takeOrdered(3, key=lambda kv: -kv[1])', file='pyspark',
             output="[('and', 24000), ('was', 24000), ('masala', 4924)]", note='Without the stop-word filter: every review has “was” and “and” (same as Lesson 2.3).'),
        dict(title='2 · Orders per city', cmd='sorted(city_amt.countByKey().items(), key=lambda kv: -kv[1])[:3]', file='pyspark',
             output=capf('l25_wordcount.txt').split('countByKey    : ')[1].split('\n')[0], note='An action: a dict on the driver.'),
        dict(title='3 · Join checks', cmd='orders_by_cust.count(), orders_by_cust.join(cust).count(), orders_by_cust.leftOuterJoin(cust).count()', file='pyspark',
             output='(50001, 50001, 50001)', note='All three equal: every order has exactly one customer.'),
    ],
)

TRACE = dict(
    heading='aggregateByKey for an average, step by step',
    intro='<p>Follow (sum, count) for Mumbai across two partitions.</p>',
    code='''zero = (0, 0)
seq = lambda acc, v: (acc[0] + v, acc[1] + 1)
comb = lambda a, b: (a[0] + b[0], a[1] + b[1])
p1, p2 = [530, 480], [120]
a1 = zero
for v in p1:
    a1 = seq(a1, v)
a2 = seq(zero, p2[0])
total = comb(a1, a2)
print(a1, a2, total, round(total[0] / total[1], 2))
''',
    notes={1: 'Zero :: The start value for each key in each partition.', 6: 'seqOp :: Adds one amount inside a partition.', 9: 'combOp :: Merges the partial pairs after the shuffle.'},
)

WORKED_INTRO = 'Three analyses built from the word count pattern.'
EXAMPLES = [
    dict(level='b', tag='Analytics · text', title='Top words without stop words',
         problem='<p>Count review words, ignoring very common ones.</p>',
         inp='reviews folder',
         approach=['lower + split.', 'filter stop words.', 'reduceByKey + takeOrdered.'],
         code='''print("""reviews.flatMap(lambda l: l.lower().split())
       .filter(lambda w: w not in stop)
       .map(lambda w: (w, 1)).reduceByKey(add)
       .takeOrdered(8, key=lambda kv: -kv[1])""")
''', notes={2: 'Stop words :: was, and, for, it, too in our lab.'},
         tryit='Real result: masala 4,924, loved 4,905, tasty 4,839.'),
    dict(level='i', tag='Analytics · KPIs', title='Average order value per city',
         problem='<p>Compute the exact average amount per city.</p>',
         inp='(city, amount) pairs',
         approach=['aggregateByKey (sum, count).', 'mapValues to divide.', 'sortByKey for output.'],
         code='''pairs = [("Mumbai", 530), ("Mumbai", 480), ("Pune", 210)]
acc = {}
for c, a in pairs:
    s, n = acc.get(c, (0, 0)); acc[c] = (s + a, n + 1)
print(sorted((c, round(s / n, 2)) for c, (s, n) in acc.items()))
''', notes={1: 'Real :: Bengaluru 292.97, Chennai 298.16, Delhi 295.0.'},
         tryit='The DataFrame version: groupBy("city").avg("amount").'),
    dict(level='a', tag='Data quality · joins', title='Guard a join',
         problem='<p>Make a nightly join fail loudly if customer keys are duplicated.</p>',
         inp='orders and customers pair RDDs',
         approach=['Count orders.', 'Count joined rows.', 'Assert equal; report duplicates.'],
         code='''orders, joined = 50001, 50001
dup_keys = 0                     # cust.countByKey() values > 1
assert joined == orders and dup_keys == 0, "duplicate or missing customers"
print("join OK")
''', notes={1: 'Counts :: Real counts from Step 7.'},
         tryit='leftOuterJoin shows orders with no customer as (cid, (amount, None)).'),
]

QUIZ = mix([
    dict(q='Beginner: What is a pair RDD?', options=['Two RDDs', 'An RDD of (key, value) tuples', 'A cached RDD', 'An RDD with two partitions'], answer=1,
         why='Keys unlock by-key operations.'),
    dict(q='Beginner: In a word count, what does map produce?', options=['(word, 1)', 'word counts', 'lines', 'a dict'], answer=0,
         why='reduceByKey then adds the 1s.'),
    dict(q='Beginner: Which word topped our filtered counts?', options=['cold', 'masala', 'poha', 'late'], answer=1,
         why='It appears in two dish names.'),
    dict(q='Intermediate: Which is an action?', options=['reduceByKey', 'countByKey', 'mapValues', 'join'], answer=1,
         why='It returns a dict to the driver.'),
    dict(q='Intermediate: How do you compute an exact average per key?', options=['reduceByKey of averages', 'aggregateByKey carrying (sum, count)', 'countByKey', 'sortByKey'], answer=1,
         why='Averages of averages are wrong with unequal groups.'),
    dict(q='Intermediate: What does join return for a key?', options=['(k, v1)', '(k, (v1, v2))', '(v1, v2)', 'a list'], answer=1,
         why='(cid, (amount, plan)) in Step 7.'),
    dict(q='Advanced: What is combineByKey?', options=['A sort', 'The general per-key aggregation: create, merge value, merge combiners', 'A join', 'An action'], answer=1,
         why='reduceByKey and aggregateByKey are built on it.'),
    dict(q='Advanced: joined.count() is larger than orders.count(). Likely cause?', options=['Nulls', 'Duplicate keys on the customer side', 'Caching', 'Too many partitions'], answer=1,
         why='Each order matched several customer rows.'),
])

REVISION = [
    '<b>Pair RDD</b> = RDD of (key, value); enables by-key operations, most with a shuffle.',
    'Word count: <code>flatMap(split) → map((w, 1)) → reduceByKey(add)</code>; <code>takeOrdered</code> for the top n.',
    'Lab: 35 words; masala 4,924, loved 4,905; complaints ~2,000 each. DataFrame (split + explode + groupBy) gave the same.',
    '<code>countByKey</code> is an action (dict on the driver); prefer <code>reduceByKey</code> for many keys.',
    'Averages: <code>aggregateByKey((0, 0), seq, comb)</code> + <code>mapValues</code>.',
    '<code>combineByKey</code>: create / merge value / merge combiners; e.g. (min, max) = (40, 840).',
    '<code>join</code> → (k, (v1, v2)); check counts (50,001 = 50,001) to catch duplicate keys.',
]
FAQ = [
    ('Should I write word counts with RDDs or DataFrames?', 'Both work and gave identical results. For text exploration RDDs are short and clear; for results that become tables, DataFrames integrate better and are optimised. Interviews often ask for both.'),
    ('Why did “masala” win?', 'Because the counter counts tokens: “masala” is part of two dish names. Real text analysis normalises tokens (lower-case, punctuation), removes stop words and may treat known phrases as one token.'),
    ('Is sortByKey expensive?', 'It is a shuffle with range partitioning, which first samples the keys. For the top n, takeOrdered is cheaper because it never sorts everything.'),
    ('What is cogroup?', 'For two pair RDDs, cogroup returns (key, (values from the first, values from the second)). joins are built on it; use it when you need all values from both sides per key.'),
    ('Can keys be tuples?', 'Yes, any hashable value: a (dish, word) tuple is a common compound key, as in scenario 1.'),
]

PRACTICE_INTRO = 'Programs built on the (key, value) pattern.'
PROBLEMS = [
    dict(level='easy', title='Words to pairs', stmt='Turn words into (word, 1) pairs.', inp='list of words',
         code='''print([(w, 1) for w in ["poha", "idli", "poha"]])
''', explain='rdd.map(lambda w: (w, 1)).'),
    dict(level='easy', title='Sum per key', stmt='Add values per key.', inp='pairs',
         code='''from collections import defaultdict
d = defaultdict(int)
for k, v in [("poha", 1), ("idli", 1), ("poha", 1)]:
    d[k] += v
print(dict(d))
''', explain='reduceByKey(add).'),
    dict(level='easy', title='Top n', stmt='Top 2 words by count.', inp='counts',
         code='''counts = {"masala": 4924, "loved": 4905, "tasty": 4839}
print(sorted(counts.items(), key=lambda kv: -kv[1])[:2])
''', explain='takeOrdered(2, key=lambda kv: -kv[1]).'),
    dict(level='medium', title='Average per key', stmt='Exact average with (sum, count).', inp='pairs',
         code='''acc = {}
for k, v in [("Pune", 210), ("Pune", 340), ("Delhi", 990)]:
    s, n = acc.get(k, (0, 0)); acc[k] = (s + v, n + 1)
print({k: s / n for k, (s, n) in acc.items()})
''', explain='aggregateByKey + mapValues.'),
    dict(level='medium', title='Min and max per key', stmt='combineByKey logic.', inp='pairs',
         code='''acc = {}
for k, v in [("Pune", 210), ("Pune", 840), ("Pune", 40)]:
    lo, hi = acc.get(k, (v, v)); acc[k] = (min(lo, v), max(hi, v))
print(acc)
''', explain='Create (v, v), merge with min/max.'),
    dict(level='medium', title='Left outer join', stmt='Keep orders without a known customer.', inp='orders, plans',
         code='''orders = [("c1", 530), ("c9", 99)]
plans = {"c1": "Gold"}
print([(c, (a, plans.get(c))) for c, a in orders])
''', explain='leftOuterJoin gives None for missing keys.'),
    dict(level='business', title='Complaint rate', stmt='Share of reviews mentioning "cold".', inp='2,027 of 24,000',
         code='''print(f"{2027 / 24000:.1%}")
''', explain='Track it per month and per dish.'),
    dict(level='business', title='Revenue share by plan', stmt='Share of revenue per plan.', inp='Basic 7,376,620 · Gold 3,827,990 · Silver 3,516,780',
         code='''r = {"Basic": 7376620, "Gold": 3827990, "Silver": 3516780}
t = sum(r.values())
print({k: f"{v / t:.0%}" for k, v in r.items()})
''', explain='Basic customers are about half of all customers, so half the revenue is expected.'),
]

SCN_INTRO = 'The word count and by-key operations are the most common PySpark coding questions.'
SCENARIOS = (
    scn('Any company · PySpark', 'Fresher', '“Write a word count”',
        'Write a word count in PySpark and explain it.',
        'can you code and explain the shuffle?',
        '<p>sc.textFile(path).flatMap(lambda l: l.split()).map(lambda w: (w, 1)).reduceByKey(lambda a, b: a + b). flatMap splits lines into words, map makes pairs, reduceByKey sums counts per word: each partition sums locally, then the partial counts are shuffled and added. With DataFrames: split, explode, groupBy("word").count().</p>', 'Using groupByKey and len without explaining the cost.') +
    scn('Data engineering', 'Fresher', 'Average per key',
        'Compute the average order value per city with RDDs.',
        'do you avoid average of averages?',
        '''<ul>
          <li>aggregateByKey((0, 0), add-one, merge) carrying (sum, count).</li>
          <li>mapValues(lambda s: s[0] / s[1]).</li>
          <li>Or the DataFrame avg(), which does the same internally.</li>
        </ul>''', 'reduceByKey on averages.') +
    scn('Data engineering', 'Mid-level', 'reduceByKey vs aggregateByKey vs combineByKey',
        'When do you use each?',
        'do you know the family?',
        '''<ol>
          <li>reduceByKey: result has the same type as values (sum, max).</li>
          <li>aggregateByKey: different result type with a zero value (sum, count).</li>
          <li>combineByKey: full control, including how to create the first combiner.</li>
        </ol>''', '“They are interchangeable.”') +
    scn('Platform', 'Senior', 'Join doubled the numbers',
        'After a dimension reload, revenue doubled in a pair-RDD join.',
        'can you diagnose join cardinality?',
        '''<ul>
          <li>Compare row counts before and after the join; check duplicate keys with countByKey or reduceByKey.</li>
          <li>Enforce one row per key in dimensions; add assertions to the job.</li>
          <li>Use leftOuterJoin counts to find missing keys.</li>
        </ul>''', 'Dividing the result by two.')
)
