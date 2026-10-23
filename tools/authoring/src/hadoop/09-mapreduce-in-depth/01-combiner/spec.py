import os
HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)
BODY = body(HERE)
rd = lambda f: open(os.path.join(UP, f)).read()
TX = rd('tx91.txt')
TX_WC = TX[:TX.index('### Average')].strip()
TX_AVG = TX[TX.index('### Average'):TX.index('-- three students')].strip()
TX_CMP = TX[TX.index('-- three students'):].strip()

META = dict(
    module='09-mapreduce-in-depth', lesson='01-combiner', n='9.1',
    module_label='Module 9 · MapReduce in depth',
    title='Combiner',
    desc='The MapReduce combiner measured on a real Hadoop 3.5.0 cluster: word count on 102 MB went from 225,867,818 shuffle bytes and 52.9 s to 1,083 bytes and 29.2 s with identical output. Why Combine input records exceeded Map output records (the combiner runs again while merging spills), why an averaging combiner silently broke all 2,000 students\' averages, and the (sum, count) fix. setCombinerClass, commutative and associative functions, in-mapper combining, Python simulation, quiz and interview scenarios.',
    og_desc='One line cut the shuffle from 226 MB to 1 KB. The same trick made 2,000 of 2,000 averages wrong. Learn when a combiner is safe.',
    minutes=26, level='Intermediate',
    lead='A combiner runs a mini-reduce on each map task\'s output before the shuffle, so the network carries totals instead of lakhs of ones. It can make a job much faster, but Hadoop may run it zero, one or many times, and some logic breaks when that happens. This lesson measures both sides on a real cluster.',
    chips=['226 MB → 1 KB shuffle, measured', 'A wrong combiner caught', 'Runs in your browser (Python)'],
)

RUN = dict(
    heading='Simulate a combiner running on spills',
    intro='<p>One map task\'s output is cut into spills, as the sort buffer would. The combiner runs on each spill, then once more on the merged spills. Compare the final answer with no combiner, a sum combiner and an averaging combiner.</p>',
    code='''pairs = [("chai", 15), ("chai", 15), ("dosa", 45), ("chai", 15), ("thali", 80),
         ("dosa", 45), ("chai", 15), ("thali", 80), ("chai", 20), ("dosa", 40)]
spills = [pairs[0:4], pairs[4:7], pairs[7:10]]        # the sort buffer filled 3 times

def combine(records, fn):                             # group by key, apply fn to each group
    groups = {}
    for k, v in records:
        groups.setdefault(k, []).append(v)
    return [(k, fn(vs)) for k, vs in sorted(groups.items())]

total = lambda vs: sum(vs)
avg = lambda vs: sum(vs) / len(vs)

for name, fn in [("sum", total), ("average", avg)]:
    after_spills = [r for s in spills for r in combine(s, fn)]   # combiner on every spill
    merged = combine(after_spills, fn)                           # and again on the merge
    print(f"{name:8} combiner ->", merged)
print("true sums      ->", combine(pairs, total))
print("true averages  ->", [(k, round(v, 2)) for k, v in combine(pairs, avg)])
''',
    anno=[
        ('spills = [pairs[0:4], pairs[4:7], pairs[7:10]]        # the sort buffer filled 3 times', 'With 3 or more spills Hadoop also runs the combiner while merging them, like our 102 MB maps did.'),
        ('    merged = combine(after_spills, fn)                           # and again on the merge', 'Its output becomes its own input: the function must give the same answer however often it runs.'),
        ('avg = lambda vs: sum(vs) / len(vs)', 'Average is not associative: averaging partial averages loses how many values each stood for.'),
    ],
    tasks=[
        dict(label='1 · Sum vs average', hint='Press <b>Run</b>. Which combiner gives the true answer for every item?', code=None),
        dict(label='2 · Fix the average', hint='<b>Predict first:</b> emit (amount, 1), combine by adding both parts, divide only at the end. Does it match the true averages?',
             code='''pairs = [("chai", 15), ("chai", 15), ("dosa", 45), ("chai", 15), ("thali", 80),
         ("dosa", 45), ("chai", 15), ("thali", 80), ("chai", 20), ("dosa", 40)]
spills = [pairs[0:4], pairs[4:7], pairs[7:10]]

def combine(records):
    g = {}
    for k, (s, n) in records:
        a, b = g.get(k, (0, 0))
        g[k] = (a + s, b + n)
    return sorted(g.items())

partials = [r for s in spills for r in combine([(k, (v, 1)) for k, v in s])]
for k, (s, n) in combine(partials):
    print(k, round(s / n, 2), f"({n} orders)")
'''),
        dict(label='3 · Max is safe too', hint='Write a max combiner and check it gives the largest order per item, however the spills are cut.',
             code='''pairs = [("chai", 15), ("chai", 20), ("dosa", 45), ("dosa", 40), ("chai", 15), ("thali", 80)]
spills = [pairs[0:2], pairs[2:5], pairs[5:6]]
best = {}
for s in spills:
    local = {}
    for k, v in s:
        local[k] = max(local.get(k, 0), v)        # combiner: max per spill
    for k, v in local.items():
        best[k] = max(best.get(k, 0), v)          # reducer: max of maxes
print(sorted(best.items()))
'''),
        dict(label='4 · Is it worth it?', hint='Compute the combine ratio (output ÷ input) for our two real jobs. A ratio near 1 means the combiner is wasted work.',
             code='''jobs = {"word count": (20665132, 465), "avg spend (right)": (500000, 6000)}
for name, (cin, cout) in jobs.items():
    print(f"{name:18} {cout / cin:.6f}  ({cin // cout:,}x fewer records)")
'''),
        dict(label='5 · Spot the error', hint='This combiner counts distinct students per item by adding partial counts. Map 1 and map 2 both saw S0001. Find the bug: the answer should be 3, not 4.',
             code='''map1 = {"S0001", "S0002"}
map2 = {"S0001", "S0003"}
partial_counts = [len(map1), len(map2)]
answer = sum(partial_counts)
assert answer == len(map1 | map2), f"counted {answer} students, but there are {len(map1 | map2)}"
''', expect='error'),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run it on your PC: with and without a combiner',
    intro='<p>Module 9 uses the Module 8 lab cluster (start it with <code>docker compose -p lab8 up -d</code> in your <code>mr-lab</code> folder, Lesson 8.1) and a new dataset: run <code>make_student_orders.py</code> to create <code>student_orders.csv</code> (5 lakh orders by 2,000 students, with time) and <code>menu.csv</code>. Copy both, the Java files and the script into <code>/tmp/mr9</code> in the namenode container, compile everything into <code>mr9.jar</code>, and run the script. <code>feedback_x20.txt</code> is the 20× feedback file from Lesson 8.6. It takes about 3 minutes.</p>',
    items=[
        dict(title='The Module 9 dataset', file='make_student_orders.py',
             cmd=rd('make_student_orders.py') + '\n# Run on your PC, in the mr-lab folder:\n#   python make_student_orders.py\n#   docker exec lab8-namenode-1 mkdir -p /tmp/mr9\n#   docker cp student_orders.csv lab8-namenode-1:/tmp/mr9/\n#   docker cp menu.csv lab8-namenode-1:/tmp/mr9/',
             output='student_orders.csv: 500,000 orders; menu.csv: 8 items\n$ head -3 student_orders.csv\n1,S1413,2026-09-14 15:30,dosa,45\n2,S0973,2026-09-26 20:11,samosa,18\n3,S0007,2026-09-01 13:37,samosa,18',
             note='Real output. The random seed is fixed, so your file is identical to ours.'),
        dict(title='Word count with an optional combiner', file='WordCountCombiner.java',
             cmd=rd('java/WordCountCombiner.java') + '\n// Copy all Module 9 .java files to /tmp/mr9 in the namenode container, then inside it:\n//   cd /tmp/mr9\n//   mkdir -p classes && javac -cp $(hadoop classpath) -d classes *.java && jar cf mr9.jar -C classes .\n//   hadoop jar mr9.jar WordCountCombiner -D wc.combiner=false /user/hadoop/data/feedback_x20.txt /out/wc_nocomb',
             output=TX_WC,
             note='Real output from combiner_lab.sh (below). The reducer doubles as the combiner because its input and output types are both (Text, IntWritable).'),
        dict(title='Average spend: no, wrong and right combiner', file='AvgSpend.java',
             cmd=rd('java/AvgSpend.java'),
             output=TX_AVG,
             note='Real output from combiner_lab.sh. The value travels as the text "sum,count" so the reducer can read both map output and combiner output.'),
        dict(title='Run all five jobs and compare', file='combiner_lab.sh',
             cmd=rd('combiner_lab.sh') + '\n# Inside the namenode container:  bash /tmp/mr9/combiner_lab.sh',
             output=TX_CMP,
             note='Real output: the last part of the script, comparing the three average runs (the job counters are shown with the two Java files above). “Launched map tasks=4” in the first word count run is a speculative extra attempt (Lesson 8.1), not a 4th split. Your timings will differ; the record counts and the 2000-of-2000 result will not.'),
    ],
)

TRACE = dict(
    heading='The combiner runs twice inside one map task',
    intro='<p>Two spills are combined, then merged and combined again. Watch <code>out</code> after each pass.</p>',
    code='''spill1 = [("chai", 1), ("chai", 1), ("was", 1)]
spill2 = [("chai", 1), ("was", 1), ("was", 1)]
def combine(recs):
    g = {}
    for k, v in recs:
        g[k] = g.get(k, 0) + v
    return sorted(g.items())
out = combine(spill1) + combine(spill2)
out = combine(out)
print(out)
''',
    notes={8: 'Spill pass :: Each spill shrinks to one record per word before it is written.',
           9: 'Merge pass :: The combiner\'s own output goes through it again. Sum doesn\'t mind.'},
)

WORKED_INTRO = 'Three combiner problems: estimating the saving, deciding whether a function is safe, and designing a partial aggregate.'
EXAMPLES = [
    dict(level='b', tag='Sizing · shuffle', title='How much does the combiner save?',
         problem='<p>Our word count job emitted 20,664,760 pairs and shuffled 225,867,818 bytes without a combiner. With it, the reducer received 93 records in 1,083 bytes. Compute bytes per record in both runs and the reduction factor.</p>',
         inp='20,664,760 pairs / 225,867,818 B · 93 records / 1,083 B',
         approach=['Bytes per record = bytes / records.',
                   'Reduction = bytes before / bytes after.',
                   'Compare.'],
         code='''before, after = (225867818, 20664760), (1083, 93)
print(f"{before[0] / before[1]:.1f} B/record before, {after[0] / after[1]:.1f} B/record after")
print(f"{before[0] / after[0]:,.0f}x less data shuffled")
''', notes={2: 'Per record :: About 11 bytes each: the word, a 1, and framing.'},
         tryit='The bytes per record stay about the same; the saving comes entirely from having 2 lakh times fewer records.'),
    dict(level='i', tag='Correctness · rule', title='Which functions are safe to combine?',
         problem='<p>Test sum, max, average and “count” (number of values) by combining a list in two different groupings and checking whether the results agree with applying the function once to the whole list.</p>',
         inp='values 15, 20, 45, 80, 15',
         approach=['Apply f to the whole list.',
                   'Split into two parts, apply f to each, then f to the results.',
                   'Safe if both ways agree.'],
         code='''vals = [15, 20, 45, 80, 15]
fns = {"sum": sum, "max": max, "avg": lambda v: sum(v) / len(v), "count": len}
for name, f in fns.items():
    once = f(vals)
    twice = f([f(vals[:2]), f(vals[2:])])
    print(f"{name:5} once={once:<6} combined={twice:<6} safe={once == twice}")
''', notes={4: 'Re-apply :: The combiner\'s output may be fed to the same function again.'},
         tryit='Count fails too: re-applying len() counts partial results (2), not values (5). For counting, emit 1 and combine with sum.'),
    dict(level='a', tag='Design · partials', title='Design a combiner for min, max and average together',
         problem='<p>The canteen wants per student: number of orders, total, average, smallest and largest order. Design one partial aggregate that a combiner can merge safely, and finish it in the reducer.</p>',
         inp='two partial results for S1413',
         approach=['Partial = (count, sum, min, max): all merge with +, +, min, max.',
                   'Combiner merges partials field by field.',
                   'Reducer computes average = sum / count at the end.'],
         code='''def merge(a, b):
    return (a[0] + b[0], a[1] + b[1], min(a[2], b[2]), max(a[3], b[3]))
p1 = (100, 2510, 15, 80)       # (count, sum, min, max) from map 1
p2 = (84, 2114, 15, 80)        # from map 2
c, s, lo, hi = merge(p1, p2)
print(f"{c} orders, total {s}, avg {s / c:.2f}, min {lo}, max {hi}")
''', notes={1: 'Merge :: Every field merges with an associative operation.'},
         tryit='This is how Hive and Spark compute AVG in a GROUP BY: a (sum, count) buffer on the map side, a division at the end. (Partial values here are illustrative.)'),
]

QUIZ = mix([
    dict(q='What does a combiner do?', options=['Combines input files before the map', 'Aggregates one map task\'s output locally before the shuffle', 'Merges the reducers\' output files', 'Combines splits into one'], answer=1,
         why='It is a mini-reducer on map output, to shuffle less data.'),
    dict(q='How much did the combiner cut word count\'s shuffle in our lab?', options=['From 226 MB to about 113 MB', 'From 225,867,818 bytes to 1,083 bytes', 'Not at all, only the time changed', 'From 20 MB to 1 MB'], answer=1,
         why='93 records reached the reducer instead of 20,664,760.'),
    dict(q='Why was Combine input records (20,665,132) larger than Map output records (20,664,760)?', options=['A counter bug', 'The combiner ran again on its own output while merging spills', 'The reducer counted twice', 'Speculative execution'], answer=1,
         why='372 records from spill combines were combined again during the merge.'),
    dict(q='How many times does Hadoop run the combiner?', options=['Exactly once per map task', 'Zero, one or many times: not guaranteed', 'Once per key', 'Once per reducer'], answer=1,
         why='So the reducer must give the right answer even if it never ran.'),
    dict(q='Which property must a combiner\'s function have?', options=['It must be fast', 'Commutative and associative, so partial results can be merged in any grouping', 'It must output Text', 'It must sort its input'], answer=1,
         why='Sum, max and min qualify; average does not.'),
    dict(q='What went wrong when the averaging reducer was used as a combiner?', options=['The job failed', 'Every student\'s average was slightly wrong, with no error', 'Only heavy users were wrong', 'The output was empty'], answer=1,
         why='2,000 of 2,000 differed; S1413 showed 25.30 instead of 25.13.'),
    dict(q='How do you combine safely for an average?', options=['Average the averages', 'Emit (sum, count), add them in the combiner, divide in the reducer', 'Use more reducers', 'Sort the values first'], answer=1,
         why='Our right combiner: 0 of 2,000 differed and the shuffle fell 61 times.'),
    dict(q='What must the combiner\'s input and output types be?', options=['Anything you like', 'Both equal to the map output key and value types', 'The reducer\'s output types', 'Text and Text'], answer=1,
         why='Its output goes to the reducer, or back into the combiner, as if the map had written it.'),
])

REVISION = [
    'Combiner = mini-reducer on <b>one map task\'s output</b>, before the shuffle; <code>job.setCombinerClass(...)</code>.',
    'Runs on each spill and again on merges (≥ 3 spills, <code>mapreduce.map.combine.minspills</code>); may run <b>0, 1 or many times</b>.',
    'Must be <b>commutative and associative</b>; input type = output type = map output type.',
    'Lab word count: 225,867,818 → 1,083 shuffle bytes, 52.9 s → 29.2 s, identical output; Combine input 20,665,132 &gt; Map output (ran twice).',
    'Safe: sum, count (as sum of 1s), max, min. Unsafe as-is: average, median, distinct count.',
    'Average: emit <b>(sum, count)</b>, divide only in the reducer. Wrong combiner → 2,000 of 2,000 averages wrong, silently.',
    'Alternative: in-mapper combining (HashMap + <code>cleanup()</code>). Useless when keys are nearly unique.',
]
FAQ = [
    ('What is a combiner in MapReduce?', 'A combiner is an optional local reducer that runs on the output of each map task before the shuffle. It aggregates values for the same key on the map side, so far less data is written to disk and sent over the network to the reducers. It is set with job.setCombinerClass() and often reuses the reducer class when the reduce function is commutative and associative.'),
    ('Is the combiner guaranteed to run?', 'No. Hadoop may run the combiner zero, one or several times for a map task: on each spill of the sort buffer, again while merging spill files (when there are at least 3 spills), and sometimes during reduce-side merges. The job must produce correct results whether or not it runs.'),
    ('Can every reducer be used as a combiner?', 'No. Only when the reduce function is commutative and associative and its input and output types are the same as the map output types. Sums, counts expressed as sums, max and min work. Averages, medians and distinct counts do not; for an average, emit (sum, count) pairs and divide only in the reducer.'),
    ('What is the difference between a combiner and a reducer?', 'A reducer receives all values of a key from every map task and produces the final output, which is written to HDFS. A combiner sees only part of the values (one map task\'s, often one spill\'s), its output goes into the shuffle rather than HDFS, and it may run any number of times, so it can only do work that is safe to repeat on partial data.'),
    ('What is in-mapper combining?', 'Aggregating inside the mapper itself, for example in a HashMap of key → running total, and writing the totals once in cleanup(). It avoids creating and sorting every intermediate pair, so it is usually faster than a combiner, but it uses mapper memory and you must flush the map if it grows too large.'),
]

PRACTICE_INTRO = 'Combiner exercises using the real counters from our lab.'
PROBLEMS = [
    dict(level='easy', title='Time saved', stmt='Word count took 52,918 ms without a combiner and 29,249 ms with one. What percentage of time was saved?', inp='52,918 ms vs 29,249 ms',
         code='''print(f"{(52918 - 29249) / 52918 * 100:.0f}% faster")
''', explain='About 45% less time, from shuffling 93 records instead of 2 crore.'),
    dict(level='easy', title='Records per map', stmt='The reducer received 93 records from 3 map tasks. How many distinct words are there?', inp='93 records, 3 maps',
         code='''print(93 // 3, "distinct words")
''', explain='31: each map sends one combined record per word, and every map saw all 31 words.'),
    dict(level='easy', title='Partial averages', stmt='With the right combiner the reducer got 6,000 records for 2,000 students. Why 6,000?', inp='6,000 records, 2,000 students',
         code='''print(6000 / 2000, "partial (sum, count) records per student = number of map tasks")
''', explain='3 per student: one partial from each of the 3 map tasks.'),
    dict(level='medium', title='The second combine pass', stmt='Combine input was 20,665,132 and map output 20,664,760. Combine output was 465 and the reducer got 93. Work out how many records the spill passes produced.', inp='four counters',
         code='''extra_input = 20665132 - 20664760
print("records combined a second time:", extra_input)
print("spill passes produced:", 465 - 93, "-> merge pass produced:", 93)
print("spills in total:", extra_input // 31)
''', explain='372 records from 12 spills (31 words each) were combined again into 93 during the merges.'),
    dict(level='medium', title='Recreate the wrong average', stmt='S1413 had 184 orders. Suppose maps saw 70, 52 and 62 orders with averages 25.4, 24.1 and 25.7. Compute the wrong (average of averages) and the right (weighted) answer.', inp='3 partial averages and counts',
         code='''parts = [(25.4, 70), (24.1, 52), (25.7, 62)]
wrong = sum(a for a, n in parts) / len(parts)
right = sum(a * n for a, n in parts) / sum(n for a, n in parts)
print(f"wrong {wrong:.2f}  right {right:.2f}")
''', explain='The unweighted average gives each map equal weight, whatever it saw. Weighting by count fixes it. (Partials illustrative.)'),
    dict(level='medium', title='Distinct students, safely', stmt='Combine partial sets of student IDs instead of partial counts, and count only at the end.', inp='2 maps',
         code='''map1, map2 = {"S0001", "S0002"}, {"S0001", "S0003"}
combined = map1 | map2               # union is commutative and associative
print(len(combined), "distinct students")
''', explain='3. Set union is safe to combine; adding counts is not. With millions of IDs, teams use HyperLogLog sketches instead of full sets.'),
    dict(level='business', title='Network bill', stmt='A nightly job shuffles 4 TB between racks without a combiner; with one it shuffles 40 GB. If cross-rack transfer is the bottleneck at 10 Gbit/s, how long does the shuffle take each way?', inp='4 TB vs 40 GB at 10 Gbit/s',
         code='''rate = 10e9 / 8                         # bytes per second
for name, b in [("no combiner", 4e12), ("combiner", 40e9)]:
    print(f"{name:12} {b / rate / 60:.1f} minutes")
''', explain='About 53 minutes vs half a minute of pure transfer (illustrative). The combiner also saves the disk writes on both sides.'),
    dict(level='advanced', title='In-mapper combining', stmt='Instead of a combiner, aggregate inside the mapper with a dictionary and emit totals at the end (cleanup). Flush when the dictionary exceeds 3 keys, to bound memory. How many records are emitted?', inp='10 words, flush above 3 keys',
         code='''words = "chai was hot chai was cold chai was late chai".split()
buf, emitted = {}, []
for w in words:
    buf[w] = buf.get(w, 0) + 1
    if len(buf) > 3:                     # memory guard: flush partial totals
        emitted += buf.items(); buf = {}
emitted += buf.items()                   # cleanup()
print(len(emitted), "records emitted for", len(words), "words:", emitted)
''', explain='7 records for 10 words: one flush happened, so chai and was are emitted twice. Without the memory limit it would be 5 (one per word). The reducer still sums correctly because partial totals for the same word are simply added.'),
]

SCN_INTRO = 'Combiners are a favourite interview topic because one wrong answer reveals whether a candidate understands what “local aggregation” really means.'
SCENARIOS = '''    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Concepts · basics</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“What is a combiner and why is it used?”</h4>
      <p class="scn__situation">Asked right after word count.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> where it runs and what it saves.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>A local mini-reducer that runs on each map task's output, set with setCombinerClass.</li>
          <li>It reduces the data written to local disk and sent in the shuffle, e.g. (chai, 1) × lakhs → (chai, total).</li>
          <li>In our lab word count: 225 MB of shuffle became 1 KB and the job ran 45% faster.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Correctness · design</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“Can I use my average reducer as a combiner?”</h4>
      <p class="scn__situation">The classic trick question.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> associativity and partial aggregates.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>No: an average of partial averages is wrong unless every part has the same count, and Hadoop may run the combiner any number of times.</li>
          <li>Emit (sum, count) from the map, let the combiner add both, and divide once in the reducer.</li>
          <li>The combiner's input and output types must both match the map output types, which (sum, count) does.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Debugging · production</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>Results changed slightly after a “performance fix”</h4>
      <p class="scn__situation">A colleague added a combiner to a metrics job; dashboards now differ from last month by 0.5–2%. No job failed.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> silent correctness bugs.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Suspect a non-associative combiner (average, ratio, percentile, distinct count).</li>
          <li>Rerun the same input with and without the combiner and diff the outputs; check Combine input/output counters.</li>
          <li>Fix with partial aggregates (sum, count; min, max; sets or sketches) and add a regression test comparing both modes on a sample.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Performance · tuning</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>“We added a combiner but the job didn't get faster”</h4>
      <p class="scn__situation">Counters show Combine input 50 crore, Combine output 49 crore.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> reading counters.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>The ratio is about 0.98: keys are almost unique per map task, so there is nothing to combine; the combiner only adds CPU.</li>
          <li>Remove it, or change the key design (coarser keys) if aggregation is the goal.</li>
          <li>Look elsewhere: compress map output, filter earlier, or use in-mapper combining for hot keys.</li>
        </ul>
      </div></details>
    </article>
'''
