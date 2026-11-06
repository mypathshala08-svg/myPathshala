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
    module='02-rdds', lesson='04-narrow-vs-wide-and-the-shuffle', n='2.4',
    module_label='Module 2 · RDDs: Spark’s foundation',
    title='Narrow vs wide transformations and the shuffle',
    desc='Narrow and wide dependencies measured on a Spark 4.3.0 cluster with 2,000,000 TiffinGo order amounts: map and filter with 0 bytes of shuffle, groupByKey writing 355.6 KiB in 5.0 s against reduceByKey’s 106.7 KiB in 2.3 s with identical results, repartition(2) shuffling 11.5 MiB while coalesce(2) shuffles nothing, a join that shuffles both sides, a co-partitioned join with no new shuffle, and mapValues keeping the partitioner while map loses it.',
    og_desc='Same answer, a third of the shuffle: groupByKey vs reduceByKey, repartition vs coalesce and a join with no shuffle, measured on a real Spark cluster.',
    minutes=36, level='Intermediate',
    lead='The shuffle is where most Spark jobs spend their time. This lesson measures it: every common narrow and wide operation runs on 2,000,000 TiffinGo order amounts on our cluster, and the Spark UI reports how much data each one moved. <b>All numbers and screenshots are real</b> (Spark 4.3.0).',
    chips=['Spark 4.3.0 cluster', 'Shuffle bytes measured', 'Join with no shuffle', 'Runs in your browser (Python)'],
)

MAIN = '''# How much moves in a shuffle? groupByKey vs reduceByKey, simulated
partitions = [
    [("c1", 530), ("c2", 210), ("c1", 480), ("c3", 990)],
    [("c2", 120), ("c1", 340), ("c3", 60), ("c3", 300)],
]
# groupByKey: every (key, value) crosses the network
moved_group = sum(len(p) for p in partitions)

# reduceByKey: combine inside each partition first, then move one value per key
combined = []
for p in partitions:
    acc = {}
    for k, v in p:
        acc[k] = acc.get(k, 0) + v
    combined.append(acc)
moved_reduce = sum(len(acc) for acc in combined)

print("records moved by groupByKey :", moved_group)
print("records moved by reduceByKey:", moved_reduce)
print("partials:", combined)
'''
RUN = dict(
    heading='Run the code: simulate a shuffle',
    intro='<p>Two partitions of (customer, amount) pairs. Count how many records each approach sends across the network. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('moved_group = sum(len(p) for p in partitions)', 'groupByKey ships every pair: here 8 records.'),
        ('moved_reduce = sum(len(acc) for acc in combined)', 'reduceByKey ships one partial sum per key per partition: here 6. With many values per key the saving is huge.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then add 20 more pairs for c1 to one partition and compare again.', code=None),
        dict(label='2 · Predict first: our lab', hint='<b>Predict first:</b> 2,000,000 pairs, 2,000 keys, 8 partitions. How many records does each approach shuffle?',
             code='''pairs, keys, parts = 2_000_000, 2000, 8
print("groupByKey :", pairs)
print("reduceByKey:", keys * parts, "(at most one per key per partition)")
'''),
        dict(label='3 · Hash partitioning', hint='Which reduce partition does each key go to?',
             code='''n = 4
for key in [17, 2000, 1999, 42]:
    print(key, "-> partition", hash(key) % n)
'''),
        dict(label='4 · coalesce vs repartition', hint='coalesce merges neighbours; repartition spreads by hash.',
             code='''old = [[1, 2], [3, 4], [5, 6], [7, 8]]
coalesced = [old[0] + old[1], old[2] + old[3]]
repart = [[x for p in old for x in p if x % 2 == i] for i in range(2)]
print("coalesce(2)   :", coalesced, "(no data moved between tasks)")
print("repartition(2):", repart, "(every element re-assigned)")
'''),
        dict(label='5 · Spot the error', hint='This code loses the partitioner before a join.', expect='error',
             code='''ops = ["partitionBy(8)", "map(lambda kv: (kv[0], kv[1]*2))", "join"]
keeps = {"partitionBy(8)": True, "mapValues": True}
partitioned = all(keeps.get(op.split("(")[0], False) for op in ops[:2])
assert partitioned, "use mapValues instead of map to keep the partitioner, or the join will shuffle"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: check partitioners and shuffles',
    intro='<p>In the <code>pyspark</code> shell or on the Docker cluster. <b>Outputs are real</b> (Spark 4.3.0).</p>',
    items=[
        dict(title='1 · Does it keep the partitioner?', cmd='p = pairs.reduceByKey(add, 8)\np.mapValues(lambda v: v * 2).partitioner is not None, p.map(lambda kv: (kv[0], kv[1] * 2)).partitioner is not None', file='pyspark',
             output='(True, False)', note='Only operations that cannot change keys keep it.'),
        dict(title='2 · Partitions after coalesce and repartition', cmd='pairs.coalesce(2).getNumPartitions(), pairs.repartition(2).getNumPartitions()', file='pyspark',
             output='(2, 2)', note='Same result; very different cost (Step 4).'),
        dict(title='3 · Shuffle bytes per job', cmd='python3 shuffle_report.py tiffingo-rdd-shuffle     # history server REST API', file='terminal',
             output='\n'.join(capf('l24_rest.txt').split('\n')[:5]), note='Sum of shuffleWriteBytes over the stages of each job.'),
    ],
)

TRACE = dict(
    heading='Map-side combine, step by step',
    intro='<p>Follow reduceByKey on one partition before the shuffle.</p>',
    code='''partition = [("c1", 530), ("c2", 210), ("c1", 480)]
combined = {}
for key, value in partition:
    if key in combined:
        combined[key] = combined[key] + value
    else:
        combined[key] = value
shuffle_out = sorted(combined.items())
print(shuffle_out)
''',
    notes={2: 'Combiner :: A small hash map per task, one entry per key.', 5: 'Merge :: The same function you passed to reduceByKey.', 8: 'Shuffle :: Only these partial results are written: 2 records instead of 3.'},
)

WORKED_INTRO = 'Three shuffle decisions from real jobs.'
EXAMPLES = [
    dict(level='b', tag='Performance · aggregation', title='Rewrite a groupByKey',
         problem='<p>Revenue per customer was computed with groupByKey. Rewrite it.</p>',
         inp='pairs of (customer_id, amount)',
         approach=['Spot groupByKey + sum.', 'Replace with reduceByKey.', 'Compare results.'],
         code='''print("before: pairs.groupByKey().mapValues(sum)")
print("after : pairs.reduceByKey(add)")
print("lab   : 355.6 KiB -> 106.7 KiB shuffled, 5.0 s -> 2.3 s")
''', notes={2: 'add :: from operator import add'},
         tryit='Use aggregateByKey for averages: (sum, count) per key.'),
    dict(level='i', tag='Data engineering · files', title='Fewer output files',
         problem='<p>A job writes 400 small files. Reduce to about 20 without a shuffle.</p>',
         inp='400 partitions',
         approach=['coalesce(20) before writing.', 'Check file sizes.', 'Use repartition only if skewed.'],
         code='''parts, target = 400, 20
print(f"coalesce({target}): each output task merges {parts // target} partitions, no shuffle")
''', notes={1: 'Merge :: Like our coalesce(2) reading 4 partitions each.'},
         tryit='If one output file becomes huge, the input was skewed: repartition instead.'),
    dict(level='a', tag='Architecture · joins', title='Co-partition for repeated joins',
         problem='<p>Plan an hourly join of new orders with 10 million customers.</p>',
         inp='customers static, orders hourly',
         approach=['partitionBy(n) customers once, cache.', 'reduceByKey(…, n) orders with the same n.', 'Join each hour without shuffling customers.'],
         code='''n = 200
print(f"customers = customers.partitionBy({n}).cache()")
print(f"hourly    = orders.reduceByKey(add, {n})")
print("joined    = hourly.join(customers)   # customers not shuffled again")
''', notes={2: 'Same n :: Both sides must use the same partitioner and number of partitions.'},
         tryit='For DataFrames, broadcast joins and bucketing play this role (Lessons 8.2, 7.2).'),
]

QUIZ = mix([
    dict(q='Beginner: Which is a narrow transformation?', options=['groupByKey', 'filter', 'distinct', 'repartition'], answer=1,
         why='Each output partition needs only one input partition.'),
    dict(q='Beginner: What is a shuffle?', options=['Sorting a list', 'Redistributing data between partitions across executors', 'Caching', 'A random sample'], answer=1,
         why='Map tasks write, reduce tasks fetch.'),
    dict(q='Beginner: How many bytes did map + filter shuffle?', options=['0', '106.7 KiB', '355.6 KiB', '11.5 MiB'], answer=0,
         why='Narrow steps move nothing.'),
    dict(q='Intermediate: Why did reduceByKey shuffle less than groupByKey?', options=['Compression', 'It combines values per key inside each partition first', 'Fewer partitions', 'Caching'], answer=1,
         why='106.7 vs 355.6 KiB.'),
    dict(q='Intermediate: Which reduces partitions without a shuffle?', options=['repartition', 'coalesce', 'partitionBy', 'sortByKey'], answer=1,
         why='0 bytes in our lab.'),
    dict(q='Intermediate: Which keeps the partitioner?', options=['map', 'mapValues', 'flatMap', 'distinct'], answer=1,
         why='Keys cannot change.'),
    dict(q='Advanced: When can a join avoid a new shuffle?', options=['Always', 'When both RDDs share the same partitioner and number of partitions', 'Never in PySpark', 'When cached'], answer=1,
         why='Job 8: one stage, 0 KiB.'),
    dict(q='Advanced: Why did the first join shuffle both sides?', options=['A bug', 'names had no partitioner and a different number of partitions', 'AQE', 'Python version'], answer=1,
         why='Matching keys were not in matching partitions.'),
])

REVISION = [
    '<b>Narrow</b>: child partition ← one parent partition (map, filter, mapValues, union, coalesce). One stage.',
    '<b>Wide</b>: child ← many parents (groupByKey, reduceByKey, distinct, join, sortBy, repartition). Shuffle + new stage.',
    'Shuffle = write map output to local disk + fetch over the network: the main cost of jobs.',
    'Lab: groupByKey 355.6 KiB / 5.0 s vs reduceByKey 106.7 KiB / 2.3 s (map-side combine).',
    'repartition(2): 11.5 MiB shuffled; coalesce(2): 0 (merges neighbours).',
    'Co-partitioned RDDs (same partitioner, same n) join with no new shuffle; partition once, cache, reuse.',
    '<code>mapValues</code> keeps the partitioner; <code>map</code> loses it.',
]
FAQ = [
    ('Is groupByKey ever right?', 'Yes, when you really need all values of a key together (for example to sort a customer’s orders by time). If the next step is an aggregation, use reduceByKey, aggregateByKey or combineByKey instead.'),
    ('Where are shuffle files stored?', 'On the local disks of the executors that ran the map tasks (spark.local.dir), not in HDFS. That is why losing an executor can force map tasks to rerun (Lesson 1.3).'),
    ('What decides the number of reduce partitions?', 'For RDDs: the numPartitions argument of the operation, otherwise the parent’s partitioner or spark.default.parallelism. For DataFrames: spark.sql.shuffle.partitions, adjusted by AQE.'),
    ('Does coalesce ever shuffle?', 'Only with coalesce(n, shuffle=True), which is what repartition does. Without it, coalesce can only reduce the number of partitions.'),
    ('Do DataFrames have the same rules?', 'Yes. Exchange operators in a DataFrame plan are shuffles; Catalyst adds partial aggregation automatically, which is why DataFrame groupBy behaves like reduceByKey (Lesson 1.4).'),
]

PRACTICE_INTRO = 'Programs about dependencies, partitioning and shuffle sizes.'
PROBLEMS = [
    dict(level='easy', title='Narrow or wide?', stmt='Classify operations.', inp='names',
         code='''wide = {"groupByKey", "reduceByKey", "distinct", "join", "sortBy", "repartition"}
for op in ["map", "reduceByKey", "filter", "join", "coalesce"]:
    print(op, "wide" if op in wide else "narrow")
''', explain='coalesce is narrow (without shuffle=True).'),
    dict(level='easy', title='Shuffle saving', stmt='Percent less shuffle with reduceByKey.', inp='355.6 vs 106.7 KiB',
         code='''print(f"{1 - 106.7 / 355.6:.0%}")
''', explain='About 70% less data moved.'),
    dict(level='easy', title='Stages', stmt='Stages in textFile → map → reduceByKey → join (not co-partitioned).', inp='ops',
         code='''print(3)
''', explain='One for the map side, one after reduceByKey, one after the join’s shuffle.'),
    dict(level='medium', title='Partition of a key', stmt='Hash-partition customer ids into 8 partitions.', inp='ids',
         code='''for c in [0, 7, 8, 1999]:
    print(c, c % 8)
''', explain='Python ints hash to themselves; Spark’s portable_hash behaves similarly for ints.'),
    dict(level='medium', title='Combine per partition', stmt='Partial sums per partition.', inp='two partitions',
         code='''from collections import Counter
p0 = Counter(); p1 = Counter()
for k, v in [("c1", 5), ("c1", 3), ("c2", 1)]: p0[k] += v
for k, v in [("c1", 2), ("c2", 4)]: p1[k] += v
print(dict(p0), dict(p1), dict(p0 + p1))
''', explain='What reduceByKey does before and after the shuffle.'),
    dict(level='medium', title='Files after coalesce', stmt='Partitions merged per output task.', inp='400 → 20',
         code='''print(400 // 20)
''', explain='Each output task reads 20 old partitions.'),
    dict(level='business', title='Network bill', stmt='Monthly shuffle saved by reduceByKey.', inp='2 TB/day with groupByKey, 70% less',
         code='''print(2 * 0.7 * 30, "TB per month not moved")
''', explain='Less disk and network, faster jobs.'),
    dict(level='business', title='Repeated join cost', stmt='Customer data shuffled per day without co-partitioning.', inp='5 GB × 24 joins',
         code='''print(5 * 24, "GB/day vs 5 GB once")
''', explain='Partition once, reuse all day.'),
]

SCN_INTRO = 'Shuffle questions separate beginners from experienced Spark engineers.'
SCENARIOS = (
    scn('Any company · Spark', 'Fresher', 'Narrow vs wide',
        'Explain narrow and wide transformations with examples.',
        'do you know which ones shuffle?',
        '<p>Narrow transformations like map and filter compute each output partition from one input partition, so they run in the same stage without moving data. Wide transformations like groupByKey, reduceByKey and join need data from many partitions, so Spark shuffles data across the network and starts a new stage.</p>', 'Calling reduceByKey narrow.') +
    scn('Data engineering', 'Mid-level', 'groupByKey vs reduceByKey',
        'Why is reduceByKey preferred?',
        'do you know map-side combine?',
        '''<ul>
          <li>reduceByKey combines values per key in each partition before shuffling.</li>
          <li>groupByKey ships every value and builds full lists in memory; risk of OOM on hot keys.</li>
          <li>In our test: 106.7 vs 355.6 KiB shuffled, 2.3 vs 5.0 s.</li>
        </ul>''', '“They are the same, just different names.”') +
    scn('Data engineering', 'Mid-level', 'coalesce vs repartition',
        'When would you use coalesce instead of repartition?',
        'do you know the trade-off?',
        '''<ol>
          <li>coalesce reduces partitions without a shuffle: good for fewer output files.</li>
          <li>repartition shuffles to balance or increase partitions.</li>
          <li>coalesce can unbalance partitions and reduce upstream parallelism.</li>
        </ol>''', 'Using repartition(1) to write one file of a huge dataset.') +
    scn('Platform', 'Senior', 'Reduce shuffle in a pipeline',
        'A pipeline spends 70% of its time in shuffles.',
        'can you plan optimisations?',
        '''<ul>
          <li>Find the biggest shuffles in the Stages tab.</li>
          <li>Replace groupByKey, remove unnecessary repartitions, broadcast small tables, co-partition repeated joins, keep partitioners with mapValues.</li>
          <li>Measure shuffle bytes before and after each change.</li>
        </ul>''', 'Only increasing cluster size.')
)
