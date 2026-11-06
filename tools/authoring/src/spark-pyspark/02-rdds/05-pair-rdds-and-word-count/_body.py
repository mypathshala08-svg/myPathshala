import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()
def has(n, *keys):
    return '\n'.join(l for l in capf(n).split('\n') if any(k in l for k in keys))

def opbox(x, y, label, sub='', tone='card', w=128, h=26):
    o = box(x, y, w, h, tone) + t(x + w / 2, y + (11 if sub else 16), label, 7.2, 'ink', bold=True)
    if sub:
        o += t(x + w / 2, y + 21, sub, 6.4, 'ink2', mono=True)
    return o

def wc(hi=-1):
    """the word count pipeline as five boxes"""
    items = [('textFile', 'review lines'), ('flatMap', 'poha · tasty'), ('map', '(poha, 1)'), ('reduceByKey', '(poha, n)'), ('takeOrdered', 'top 8')]
    o = ''
    for k, (a, b) in enumerate(items):
        x = 6 + k * 70
        o += opbox(x, 40, a, b, 'acc' if k == hi else ['blue', 'blue', 'green', 'amber', 'violet'][k], 66, 32)
        if k:
            o += arrow(x - 4, 56, x, 56, 'ink3', 1.2)
    o += t(180, 92, 'shuffle between map and reduceByKey', 6.8, 'ink2')
    return o

# ---------------------------------------------------------------- story
sc = (wc(-1) +
      box(410, 12, 222, 136, 'card') + t(521, 30, 'From 24,000 reviews', 8.6, bold=True) +
      ''.join(t(422, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
          ('35 distinct words', 'ink'), ('masala 4924 · loved 4905', 'green'), ('cold 2027 · late 1994', 'red'),
          ('RDD top 3 = DataFrame top 3', 'green'), ('avg order: Bengaluru 292.97', 'ink'), ('join: Basic plan ₹73.8 lakh', 'ink')])))
scene_svg = scene('Pair RDDs hold (key, value) tuples and unlock by-key operations: reduceByKey, aggregateByKey, joins. The word count is the classic example; TiffinGo uses the same pattern for complaints, averages per city and revenue per plan.', sc,
                  'Turn anything into <tspan font-weight="700" class="s-acc">(key, value)</tspan> and Spark can group it.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“What are customers complaining about?”</h2>
  <div class="story">
    <p class="narration">TiffinGo’s operations head has three months of customer reviews, 24,000 lines of free text, and one question: what do people complain about most? She also wants the average order value per city and the revenue per membership plan, for a meeting tomorrow.</p>

{scene_svg}

R> Sir, reviews are just text. How do we count words on many machines?
A> With the most famous program in big data: the <b>word count</b>. Split lines into words, turn each word into a pair <code>(word, 1)</code>, and let <code>reduceByKey</code> add up the ones per word. Once data is in <b>(key, value)</b> form, a whole family of operations opens up: averages per key, joins, sorting by key.
K> Is that not what DataFrames do with groupBy?
A> Yes, and we will check that both give the same answer. Pair RDDs are how Spark did it first, how interviewers ask it, and still the simplest tool for free text. All outputs today are real (PySpark 4.3.0).
  </div>
</section>
'''

lv = '''
LEVELS> Pair RDDs at three levels
L1> Labelled boxes
      <ul>
        <li>A pair is a box with a label (the key) and something inside (the value): <code>("Mumbai", 530)</code>.</li>
        <li>Spark can then bring together all boxes with the same label, on whichever machine they are.</li>
        <li>Word count: label every word, put a 1 inside, add the 1s per label.</li>
      </ul>
L2> The pair RDD toolkit
      <ul>
        <li>Make pairs with <code>map(lambda x: (key, value))</code>; inspect with <code>keys()</code>, <code>values()</code>, <code>mapValues()</code>.</li>
        <li>Aggregate per key: <code>reduceByKey</code>, <code>aggregateByKey</code>, <code>combineByKey</code>, <code>countByKey</code> (action), <code>groupByKey</code> (only when you need all values).</li>
        <li>Order and combine: <code>sortByKey</code>, <code>join</code>, <code>leftOuterJoin</code>, <code>rightOuterJoin</code>, <code>fullOuterJoin</code>, <code>cogroup</code>.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>The word count found 35 distinct words; “masala” led because it appears in two dishes (masala dosa, paneer butter masala); the complaint words were each about 2,000.</li>
        <li>The DataFrame version (<code>split</code> + <code>explode</code> + <code>groupBy</code>) gave exactly the same top words.</li>
        <li><code>aggregateByKey</code> gave average order values per city in one pass; a pair-RDD join of 50,001 orders with 2,000 customers gave revenue per plan.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Pair RDDs and the word count</h2>
''' + def_block(
    'A <b>pair RDD</b> is an RDD whose elements are two-element tuples <code>(key, value)</code>. PySpark provides key-based operations on such RDDs: aggregations (<code>reduceByKey</code>, <code>aggregateByKey</code>, <code>combineByKey</code>, <code>groupByKey</code>, <code>countByKey</code>), value transformations that preserve partitioning (<code>mapValues</code>, <code>flatMapValues</code>), ordering (<code>sortByKey</code>) and relational operations (<code>join</code>, the outer joins, <code>cogroup</code>, <code>subtractByKey</code>). Most require a shuffle that brings equal keys to the same partition. The <b>word count</b> is the canonical example: <code>flatMap</code> lines into words, <code>map</code> each word to <code>(word, 1)</code>, and <code>reduceByKey(add)</code> to sum the counts per word, with map-side combining before the shuffle.',
    'A pair RDD is an RDD of (key, value) pairs. Spark can then add up, average, sort or join by key. Word count: split text into words, make (word, 1) pairs, and add the 1s for each word.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Pair RDD', 'RDD of (key, value) tuples.'),
    ('reduceByKey', 'Combine values per key with a function (sum, max…).'),
    ('aggregateByKey', 'Per-key aggregation into a different type, e.g. (sum, count).'),
    ('combineByKey', 'The general form: create, merge-value, merge-combiners.'),
    ('countByKey', 'Action: dict of key → number of elements.'),
    ('sortByKey', 'Sort a pair RDD by key (a shuffle with range partitioning).'),
    ('join', 'Inner join of two pair RDDs on the key.'),
    ('Stop words', 'Very common words (and, was) removed before counting.'),
]) + '''

  <h3>Pair RDD operations used today</h3>
''' + table(['Operation', 'Kind', 'Result', 'Lab'], [
    ['<code>map(lambda w: (w, 1))</code>', 'Transformation', 'pairs', 'word → (word, 1)'],
    ['<code>reduceByKey(add)</code>', 'Transformation (shuffle)', 'one value per key', '35 words with counts'],
    ['<code>takeOrdered(8, key=…)</code>', 'Action', 'top n', 'masala 4,924 …'],
    ['<code>sortByKey()</code>', 'Transformation (shuffle)', 'sorted pairs', 'complaint words A–Z'],
    ['<code>countByKey()</code>', 'Action', 'dict', 'orders per city'],
    ['<code>aggregateByKey</code> + <code>mapValues</code>', 'Transformation', 'avg per key', 'Bengaluru 292.97'],
    ['<code>combineByKey</code>', 'Transformation', '(min, max) per key', '(40, 840)'],
    ['<code>join</code>, <code>leftOuterJoin</code>', 'Transformation (shuffle)', '(k, (v1, v2))', 'revenue per plan'],
], minw=740) + lv + '''
EXAM> “Write a word count in PySpark.” <code>sc.textFile(path).flatMap(lambda l: l.split()).map(lambda w: (w, 1)).reduceByKey(lambda a, b: a + b)</code>, then <code>takeOrdered</code> or <code>saveAsTextFile</code>. Mention that reduceByKey combines counts per partition before the shuffle, and that the DataFrame equivalent is split + explode + groupBy().count().
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Which by-key operation?</h2>
''' + table(['Need', 'Use', 'Avoid', 'Note'], [
    ['Sum / count / max per key', '<code>reduceByKey</code>', '<code>groupByKey</code> + sum', 'Map-side combine (Lesson 2.4)'],
    ['Average per key', '<code>aggregateByKey((0, 0), …)</code>', 'two separate reduces', 'Carry (sum, count)'],
    ['Several statistics per key', '<code>combineByKey</code>', 'several passes', 'Full control of the combiner'],
    ['How many per key (few keys)', '<code>countByKey()</code>', '—', 'Action: dict on the driver'],
    ['All values of a key together', '<code>groupByKey</code>', '—', 'Only when truly needed'],
    ['Attach information from another dataset', '<code>join</code> / <code>leftOuterJoin</code>', 'collect + lookup', 'Broadcast if one side is small (3.2)'],
    ['Sorted output', '<code>sortByKey</code> / <code>sortBy</code>', 'collect + sort', 'Range-partitioned shuffle'],
], minw=740) + '''
WARN> A naive word count counts <b>tokens</b>, not ideas. “masala” topped our list only because two dish names contain it, and “and”/“was” would have topped it without stop-word removal. Decide what a “word” is (lower-casing, punctuation, stop words, multi-word dish names) before trusting the counts.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Word count, then by-key analytics on orders</h2>
  <p>All outputs are real: PySpark 4.3.0, local mode. Data: three months of TiffinGo reviews (24,000 lines such as <code>thepla was too spicy and oily</code>), <code>orders.csv</code> (50,002 rows) and <code>customers.csv</code> (2,000 customers with plans).</p>
''' + stepper([
    ('Step 1 · The classic word count',
     code('python', 'wordcount.py', 'from operator import add\nreviews = sc.textFile("reviews")\nstop = {"was", "and", "for", "it", "too"}\ncounts = (reviews.flatMap(lambda line: line.lower().split())\n                 .filter(lambda w: w not in stop)\n                 .map(lambda w: (w, 1))\n                 .reduceByKey(add))\nprint("distinct words:", counts.count())\nprint("top 8:", counts.takeOrdered(8, key=lambda kv: -kv[1]))', has('l25_wordcount.txt', 'distinct words', 'top 8')),
     'Four transformations and an action: lines → words → (word, 1) → sums per word → top 8. Only <b>35</b> distinct words remain because the reviews use a small vocabulary. <code>takeOrdered</code> with a negative key returns the largest counts without sorting the whole RDD. Without the stop-word filter, “and” and “was” (24,000 each, Lesson 2.3) would lead.'),
    ('Step 2 · Find the complaints',
     code('python', 'wordcount.py', 'complaints = counts.filter(lambda kv: kv[0] in {"cold", "late", "oily", "spilled"}).sortByKey().collect()', has('l25_wordcount.txt', 'complaint words')),
     'The answer for the operations head: about 2,000 mentions each of <b>cold, late, oily, spilled</b>; no single complaint dominates. <code>sortByKey()</code> returned them alphabetically. A real analysis would look at complaints <b>per dish</b>: make the key <code>(dish, word)</code> instead of <code>word</code>, a one-line change.'),
    ('Step 3 · The same with DataFrames',
     code('python', 'wordcount.py', 'from pyspark.sql import functions as F\ndf = spark.read.text("reviews")\ntop_df = (df.select(F.explode(F.split(F.lower("value"), " ")).alias("w"))\n            .where(~F.col("w").isin(*stop)).groupBy("w").count()\n            .orderBy(F.desc("count")).limit(3).collect())', has('l25_wordcount.txt', 'top 3')),
     'Identical top words and counts. <code>split</code> makes an array per line, <code>explode</code> turns it into rows (the DataFrame <code>flatMap</code>), and <code>groupBy().count()</code> does what <code>reduceByKey(add)</code> did, with partial aggregation added by Catalyst. For structured output that feeds other tables, the DataFrame version is usually preferred (Module 4).'),
    ('Step 4 · Pairs from CSV lines, countByKey',
     code('python', 'pairs.py', 'rows = (sc.textFile("orders.csv").filter(lambda l: not l.startswith("order_id"))\n          .map(lambda l: l.split(",")).filter(lambda f: f[5].isdigit()))\ncity_amt = rows.map(lambda f: (f[3], int(f[5])))          # (city, amount)\nprint(city_amt.take(2))\nprint(sorted(city_amt.countByKey().items(), key=lambda kv: -kv[1])[:3])', has('l25_wordcount.txt', 'first pairs', 'countByKey')),
     'We parsed the CSV by hand, skipped the header and dropped the row whose amount is <code>abc</code> (<code>isdigit()</code>), leaving 50,001 orders. <code>countByKey</code> is an <b>action</b>: it returns a Python dict to the driver, fine for 8 cities, dangerous for millions of keys (use <code>reduceByKey</code> instead).'),
    ('Step 5 · Average per key with aggregateByKey',
     code('python', 'pairs.py', 'sum_cnt = city_amt.aggregateByKey((0, 0),\n            lambda a, v: (a[0] + v, a[1] + 1),             # within a partition\n            lambda a, b: (a[0] + b[0], a[1] + b[1]))       # across partitions\navg = sum_cnt.mapValues(lambda s: round(s[0] / s[1], 2)).sortByKey()\nprint(avg.take(3))', has('l25_wordcount.txt', 'aggregateByKey')),
     'An average cannot be computed by reducing averages, so we carry <b>(sum, count)</b> per city: the zero value <code>(0, 0)</code>, a function to add one amount within a partition, and a function to merge two partial pairs. Then <code>mapValues</code> divides, keeping the partitioner. Average order values are close across cities (about ₹293–298) in this generated data.'),
    ('Step 6 · Several statistics with combineByKey',
     code('python', 'pairs.py', 'comb = city_amt.combineByKey(\n    lambda v: (v, v),                                         # first value of a key in a partition\n    lambda c, v: (min(c[0], v), max(c[1], v)),                # add a value\n    lambda a, b: (min(a[0], b[0]), max(a[1], b[1])))          # merge partitions\nprint(sorted(comb.collect())[:3])', has('l25_wordcount.txt', 'combineByKey')),
     '<code>combineByKey</code> is the general form behind <code>reduceByKey</code> and <code>aggregateByKey</code>: you say how to <b>create</b> a combiner from the first value, how to <b>merge a value</b> into it, and how to <b>merge two combiners</b>. Here (min, max) per city: ₹40 to ₹840 everywhere, the generator’s range.'),
    ('Step 7 · Join two pair RDDs',
     code('python', 'pairs.py', 'cust = (sc.textFile("customers.csv").filter(lambda l: not l.startswith("customer_id"))\n          .map(lambda l: l.split(",")).map(lambda f: (f[0], f[5])))        # (customer_id, plan)\norders_by_cust = rows.map(lambda f: (f[1], int(f[5])))                   # (customer_id, amount)\njoined = orders_by_cust.join(cust)                                       # (cid, (amount, plan))\nplan_rev = joined.map(lambda kv: (kv[1][1], kv[1][0])).reduceByKey(add).sortBy(lambda kv: -kv[1])\nprint(plan_rev.collect())\nprint(orders_by_cust.count(), joined.count(), orders_by_cust.leftOuterJoin(cust).count())', has('l25_wordcount.txt', 'join ->', 'rows: orders')),
     'Both RDDs were keyed by <code>customer_id</code>; <code>join</code> returned <code>(cid, (amount, plan))</code>. Re-keying by plan and reducing gave revenue per plan: Basic ₹73,76,620, Gold ₹38,27,990, Silver ₹35,16,780 (Basic customers are half of all customers). The inner and left outer joins both kept all 50,001 orders, so every order had a known customer; a smaller left-join count than orders would mean a bug, a larger one duplicate keys.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('flatMap → filter(stop) → map((w, 1))', W), ('reduceByKey(add)', W), ("top: masala 4924, loved 4905, tasty 4839", G)], size=7.0),
    term([("cold 2027 · late 1994", RD), ("oily 2071 · spilled 1996", RD), ('sortByKey(): alphabetical', W)], size=7.6),
    term([('DataFrame: split → explode → groupBy', W), ("top 3: masala 4924, loved 4905, tasty 4839", G), ('same as the RDD', G)], size=7.0),
    term([('aggregateByKey((0, 0), seq, comb)', W), ("Bengaluru 292.97 · Chennai 298.16", G), ('combineByKey (min, max): (40, 840)', G)], size=7.0),
    term([('orders.join(customers)', W), ('Basic 7376620 · Gold 3827990', G), ('orders 50001 · joined 50001', G)], size=7.4),
]
B1 = [
    t(180, 16, 'The word count pipeline', 9.4, bold=True) + wc(3) + cap('Counts combine per partition first.', '', 'green', y=112, h=30),
    t(180, 16, 'Filter the pairs', 9.4, bold=True) + wc(4) + cap('Keys are just values you can test.', '', 'amber', y=112, h=30),
    t(180, 16, 'explode = flatMap for rows', 9.4, bold=True) + wc(1) + cap('groupBy().count() = reduceByKey(add).', '', 'blue', y=112, h=30),
    t(180, 16, 'Carry what you need', 9.4, bold=True) + opbox(20, 40, 'partition 1', '(sum, count)', 'blue', 100, 32) + opbox(20, 80, 'partition 2', '(sum, count)', 'blue', 100, 32) + arrow(122, 56, 200, 74, 'acc', 1.4) + arrow(122, 96, 200, 80, 'acc', 1.4) + opbox(202, 60, 'merged', 'sum / count = avg', 'green', 140, 32) + cap('Averages need (sum, count).', '', 'violet', y=122, h=30),
    t(180, 16, 'Join on the key', 9.4, bold=True) + opbox(20, 40, 'orders', '(cid, amount)', 'blue', 110, 32) + opbox(20, 84, 'customers', '(cid, plan)', 'violet', 110, 32) + arrow(132, 56, 210, 74, 'acc', 1.4) + arrow(132, 100, 210, 82, 'acc', 1.4) + opbox(212, 62, 'joined', '(cid, (amount, plan))', 'green', 136, 32) + cap('Then re-key by plan and reduce.', '', 'green', y=126, h=30),
]
see_caps = ['The word count found the most frequent words.',
            'Complaint words, about 2,000 each.',
            'The DataFrame version agreed exactly.',
            'Per-city averages and ranges in one pass each.',
            'Revenue per plan from a pair-RDD join.']
behind_caps = ['map makes (word, 1); reduceByKey adds them up.',
               'sortByKey shuffles with range partitioning.',
               'Same plan idea, optimised by Catalyst.',
               'Partial results per partition, then merged.',
               'Both sides keyed by customer_id.']
two = anim_two('Pair RDDs', '(key, value) unlocks grouping', 'Real lab outputs', 'How it works', see, B1, see_caps, behind_caps)

# ---- scenario 1: complaints per dish
e1 = (t(180, 22, '“Which dish gets cold?”', 9.4, bold=True) + t(180, 56, 'word counts alone cannot say', 8.4, 'ink2') + cap('Need dish and word together.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Compound key', 9.4, bold=True) + t(180, 56, '((dish, word), 1)', 8.4, 'ink', mono=True) + cap('Parse the dish from the line.', '', 'green', y=150, h=34))
e3 = (t(180, 22, 'reduceByKey(add)', 9.4, bold=True) + t(180, 56, '((biryani, cold), 312)', 8.4, 'ink', mono=True) + cap('Counts per pair.', '', 'green', y=150, h=34))
e4 = (t(180, 22, 'Normalise', 9.4, bold=True) + t(180, 56, 'complaints / reviews per dish', 8.4, 'ink2') + cap('Popular dishes get more of everything.', '', 'amber', y=150, h=34))
e5 = (t(180, 22, 'Act', 9.4, 'acc', bold=True) + t(180, 56, 'packaging change for the top 2', 8.4, 'ink2') + cap('From text to a decision.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'From word counts to complaints per dish',
              'Extending the word count to a business question. (Typical analysis.)',
              'Compound keys', 'Use a compound key (dish, word) to count complaints per dish, then normalise by the number of reviews', [e1, e2, e3, e4, e5],
              ['Ask the right question.', 'Two-part key.', 'Count.', 'Normalise.', 'Decide.'],
              hid='scenario-dish')

# ---- scenario 2: wrong average
b1 = (t(180, 22, 'Dashboard average looks wrong', 9.4, bold=True) + t(180, 56, 'avg of partition averages', 8.4, 'ink2') + cap('A classic bug.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Why it is wrong', 9.4, bold=True) + t(180, 56, 'avg(100, 300) ≠ avg of 1 and 99 values', 8.2, 'ink2') + cap('Partitions have different sizes.', '', 'amber', y=150, h=34))
b3 = (t(180, 22, 'Carry (sum, count)', 9.4, bold=True) + t(180, 56, 'aggregateByKey((0, 0), …)', 8.4, 'ink', mono=True) + cap('Exact.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'Divide at the end', 9.4, bold=True) + t(180, 56, 'mapValues(lambda s: s[0] / s[1])', 8.2, 'ink', mono=True) + cap('Keeps the partitioner.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Or a DataFrame avg()', 9.4, 'acc', bold=True) + t(180, 56, 'Spark does the same internally', 8.4, 'ink2') + cap('Lesson 6.1.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'An average of averages',
              'Why aggregateByKey carries two numbers. (Typical bug.)',
              'Correct averages', 'Reducing averages gives wrong results with unequal partitions; carry (sum, count) and divide at the end', [b1, b2, b3, b4, b5],
              ['Wrong number.', 'Unequal groups.', 'Carry sum and count.', 'Divide last.', 'Or use avg().'],
              hid='scenario-avg')

# ---- scenario 3: join explosion
u1 = (t(180, 22, 'Revenue doubled overnight', 9.4, bold=True) + t(180, 56, 'after a customer table reload', 8.4, 'ink2') + cap('Nobody sold more.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Count before and after', 9.4, bold=True) + t(180, 56, 'orders 50,001 · joined 100,002', 8.4, 'ink', mono=True) + cap('Duplicate customer keys.', '', 'amber', y=150, h=34))
u3 = (t(180, 22, 'Find duplicates', 9.4, bold=True) + t(180, 56, 'cust.countByKey() values > 1', 8.4, 'ink', mono=True) + cap('Each order matched twice.', '', 'amber', y=150, h=34))
u4 = (t(180, 22, 'Fix the dimension', 9.4, bold=True) + t(180, 56, 'one row per customer_id', 8.4, 'ink2') + cap('Deduplicate upstream.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Guard in the job', 9.4, 'acc', bold=True) + t(180, 56, 'assert joined.count() == orders.count()', 8, 'ink', mono=True) + cap('Like our 50,001 = 50,001.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'A join that doubled revenue',
              'Why we compared counts in Step 7. (Typical incident.)',
              'Join checks', 'Duplicate keys on one side multiply rows in a join; compare counts before and after and enforce one row per key in dimensions', [u1, u2, u3, u4, u5],
              ['Numbers jump.', 'Counts disagree.', 'Duplicate keys.', 'Fix upstream.', 'Assert in the job.'],
              hid='scenario-joincheck')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>(key, value) unlocks grouping</h2>
  <p>Left: real outputs. Right: how each operation works.</p>
''' + two + '''
  <p>Three live scenarios follow: complaints per dish, an average of averages, and a join that doubled revenue.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Pair RDD patterns at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'text', 12, 'blue', bold=True) + t(60, 58, 'mining', 7.4, 'ink2'),
    '1. Text and log mining',
    'Counting terms, error codes or URLs in logs and reviews is the word count with a different key.',
    ['Lines', '*(term, 1)', 'Counts']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'KPIs', 12, 'green', bold=True) + t(60, 58, 'per key', 7.4, 'ink2'),
    '2. KPIs per entity',
    'Average basket per city, orders per restaurant, revenue per plan: aggregateByKey and reduceByKey.',
    ['Orders', '*by key', 'KPI table']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'enrich', 11, 'violet', bold=True) + t(60, 58, 'join', 7.4, 'ink2'),
    '3. Enriching events',
    'Joining events with customer or product attributes by id before reporting.',
    ['Events', '*join', 'Enriched']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'index', 11, 'acc', bold=True) + t(60, 58, 'search', 7.4, 'ink2'),
    '4. Inverted indexes',
    'Search systems build word → documents maps with flatMap and groupByKey or reduceByKey.',
    ['Docs', '*(word, doc)', 'Index']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'interview', 8, 'acc', bold=True) + t(60, 58, 'classic', 7.4, 'ink2'),
    '5. The interview classic',
    'Word count in PySpark, with reduceByKey and its DataFrame equivalent, is asked again and again.',
    ['Question', '*word count', 'Offer']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> Lesson <a href="../04-narrow-vs-wide-and-the-shuffle/">2.4</a> (shuffles and reduceByKey vs groupByKey).</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
