import os
HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)
BODY = body(HERE)
rd = lambda f: open(os.path.join(UP, f)).read()

META = dict(
    module='09-mapreduce-in-depth', lesson='08-hadoop-streaming-with-python', n='9.8',
    module_label='Module 9 · MapReduce in depth',
    title='Hadoop Streaming with Python',
    desc='Hadoop Streaming explained with a real run on Hadoop 3.5.0 (HDFS + YARN): a Python mapper and reducer compute revenue per menu category from 5 lakh canteen orders in 24.5 s, with exactly the same totals as the Java job. How the task JVM pipes lines through stdin and stdout, key TAB value splitting, the sorted-lines reducer that detects key changes, -files, -combiner, -numReduceTasks 0, stream.num.map.output.key.fields, local pipe testing, and debugging “PipeMapRed … subprocess failed with code 1” with yarn logs. Python simulation, quiz and interview scenarios.',
    og_desc='Write MapReduce in Python: two scripts, one Linux pipe test, one cluster run, and the log where Python errors hide.',
    minutes=26, level='Intermediate',
    lead='Hadoop Streaming lets any program that reads lines and prints lines be a mapper or a reducer. This lesson writes a Python mapper and reducer for revenue per menu category, tests them with an ordinary Linux pipe, runs them on the cluster with the same result as the Java job, and then breaks the mapper to show where a Python error really ends up.',
    chips=['Real Python job on YARN', 'Same totals as Java', 'Runs in your browser (Python)'],
)

RUN = dict(
    heading='Simulate a Streaming job: mapper, sort, reducer',
    intro='<p>The mapper and reducer below are the lab scripts turned into functions that take and return lines. <code>sorted()</code> plays the shuffle, exactly as <code>sort</code> does in the local pipe test.</p>',
    code='''menu = {"chai": "drink", "coffee": "drink", "samosa": "snack", "vada pav": "snack",
        "poha": "breakfast", "idli": "breakfast", "dosa": "meal", "thali": "meal"}
orders = ["1,S1413,2026-09-14 15:30,dosa,45", "2,S0973,2026-09-26 20:11,samosa,18",
          "3,S0007,2026-09-01 13:37,samosa,18", "4,S0001,2026-09-02 08:10,chai,15",
          "5,S0002,2026-09-02 13:05,thali,80", "6,S0001,2026-09-03 08:20,poha,25"]

def mapper(lines):                      # stdin lines in, "key\\tvalue" lines out
    out = []
    for line in lines:
        oid, student, time, item, amount = line.split(",")
        out.append(f"{menu.get(item, 'unknown')}\\t{amount}")
    return out

def reducer(lines):                     # SORTED lines in; no list of values per key
    out, current, orders, total = [], None, 0, 0
    for line in lines:
        key, value = line.split("\\t")
        if key != current:
            if current is not None:
                out.append(f"{current}\\t{orders}\\t{total}")
            current, orders, total = key, 0, 0
        orders += 1
        total += int(value)
    if current is not None:
        out.append(f"{current}\\t{orders}\\t{total}")
    return out

mapped = mapper(orders)
print("map output :", mapped)
shuffled = sorted(mapped)               # the shuffle and sort
print("sorted     :", shuffled)
for line in reducer(shuffled):
    print("reduce     :", line)
''',
    anno=[
        ('        out.append(f"{menu.get(item, \'unknown\')}\\t{amount}")', 'Everything is text. The tab separates the key (category) from the value (amount), exactly what Hadoop splits on.'),
        ('        if key != current:', 'The reducer only ever sees one line at a time, so it must notice where one key ends and the next begins.'),
        ('    if current is not None:', 'After the loop the last key is still open: forget this and the last category silently disappears.'),
    ],
    tasks=[
        dict(label='1 · Mapper, sort, reducer', hint='Press <b>Run</b>. Follow “snack” from two mapper lines to one reducer line.', code=None),
        dict(label='2 · Forget to sort', hint='<b>Predict first:</b> what does the key-change reducer print if the lines are NOT sorted? Run it and count the snack lines.',
             code='''lines = ["snack\\t18", "meal\\t45", "snack\\t20", "meal\\t80"]       # not sorted!
current, total = None, 0
for line in lines:
    key, value = line.split("\\t")
    if key != current:
        if current is not None:
            print(current, total)
        current, total = key, 0
    total += int(value)
print(current, total)
'''),
        dict(label='3 · Empty partition', hint='A reducer can get no input at all (more reducers than keys, Lesson 8.5). Check that this reducer prints nothing and does not crash.',
             code='''def reducer(lines):
    out, current, total = [], None, 0
    for line in lines:
        key, value = line.split("\\t")
        if key != current:
            if current is not None:
                out.append(f"{current}\\t{total}")
            current, total = key, 0
        total += int(value)
    if current is not None:
        out.append(f"{current}\\t{total}")
    return out

print("one key  :", reducer(["drink\\t15", "drink\\t20"]))
print("no input :", reducer([]))
'''),
        dict(label='4 · Composite key', hint='With <code>-D stream.num.map.output.key.fields=2</code> the first TWO fields are the key. Emit category and hour, sort, and total per (category, hour).',
             code='''orders = ["dosa,45,13", "chai,15,08", "chai,15,13", "thali,80,13", "chai,20,08"]
menu = {"chai": "drink", "dosa": "meal", "thali": "meal"}
lines = sorted(f"{menu[i]}\\t{h}\\t{a}" for i, a, h in (o.split(",") for o in orders))
totals = {}
for line in lines:
    cat, hour, amount = line.split("\\t")
    totals[(cat, hour)] = totals.get((cat, hour), 0) + int(amount)
for k, v in totals.items():
    print(k, v)
'''),
        dict(label='5 · Spot the error', hint='This mapper crashes on a line with a missing field, which kills the whole task (exit code 1). Make it skip bad lines instead.',
             code='''lines = ["1,S0001,2026-09-02 08:10,chai,15", "2,S0002,2026-09-02 08:11,poha"]
for line in lines:
    oid, student, time, item, amount = line.split(",")
    print(f"{item}\\t{amount}")
''', expect='error'),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run it on your PC: Streaming on the Module 8 lab',
    intro='<p>Use the Module 8 lab cluster (Lesson 8.1). Copy the two scripts, <code>menu.csv</code> and <code>student_orders.csv</code> (from <code>make_student_orders.py</code>, Lesson 9.1) into <code>/tmp/mr9</code> in the namenode container. The workers already have <code>python3</code>, because the apache/hadoop image includes it; on a real cluster check every NodeManager.</p>',
    items=[
        dict(title='The mapper', file='revenue_mapper.py',
             cmd=rd('revenue_mapper.py') + '\n# Test alone:  head -3 student_orders.csv | python3 revenue_mapper.py',
             output='meal\t45\nsnack\t18\nsnack\t18',
             note='Output of the first three lines of student_orders.csv (dosa, samosa, samosa). Each line is category, a tab, and the amount.'),
        dict(title='The reducer', file='revenue_reducer.py',
             cmd=rd('revenue_reducer.py') + '\n# Test the whole job locally:\n#   head -1000 student_orders.csv | python3 revenue_mapper.py | sort | python3 revenue_reducer.py',
             output='breakfast\t179\t4940\ndrink\t377\t6060\nmeal\t162\t9145\nsnack\t282\t5362',
             note='Real output of the local pipe test on the first 1,000 orders.'),
        dict(title='Local test, cluster run, and a broken mapper', file='streaming_lab.sh',
             cmd=rd('streaming_lab.sh') + '\n# In the mr-lab folder:\n#   docker cp revenue_mapper.py revenue_reducer.py menu.csv streaming_lab.sh lab8-namenode-1:/tmp/mr9/\n#   docker exec lab8-namenode-1 bash /tmp/mr9/streaming_lab.sh',
             output=rd('tx98.txt').strip(),
             note='Real output. The totals match the Java OrderCounters job of Lesson 9.4 to the rupee. In step 3 the job log only says the subprocess failed; the NameError is found in the task\'s stderr with yarn logs.'),
    ],
)

TRACE = dict(
    heading='The key-change reducer, line by line',
    intro='<p>Four sorted lines with two keys. Watch <code>current</code> and <code>total</code>: the first key is printed only when the second key arrives, the last one only after the loop.</p>',
    code='''lines = ["drink\\t15", "drink\\t20", "meal\\t45", "meal\\t80"]
current, total = None, 0
for line in lines:
    key, value = line.split("\\t")
    if key != current:
        if current is not None:
            print(current, total)
        current, total = key, 0
    total += int(value)
print(current, total)
''',
    notes={5: 'Key change :: True for the first line (current is None) and when "meal" arrives.',
           7: 'Emit :: The finished key is printed only when a NEW key shows up.',
           10: 'Last key :: Nothing comes after "meal", so it must be printed after the loop.'},
)

WORKED_INTRO = 'Three Streaming problems: designing the scripts, a map-only job, and estimating the cost of text pipes.'
EXAMPLES = [
    dict(level='b', tag='Design · scripts', title='Count orders per hour with Streaming',
         problem='<p>Write the mapper and reducer logic to count orders per hour of the day from lines like <code>4,S0001,2026-09-02 08:10,chai,15</code>. What does the mapper print, and what does the reducer do?</p>',
         inp='5 order lines',
         approach=['Mapper: cut the hour (characters 11–13 of the time) and print hour⇥1.',
                   'Shuffle: sort the lines.',
                   'Reducer: add the ones while the hour stays the same.'],
         code='''orders = ["1,S1,2026-09-02 08:10,chai,15", "2,S2,2026-09-02 13:05,thali,80",
          "3,S1,2026-09-02 08:40,poha,25", "4,S3,2026-09-03 13:30,dosa,45", "5,S2,2026-09-03 08:05,chai,15"]
mapped = sorted(f"{o.split(',')[2][11:13]}\\t1" for o in orders)
counts = {}
for line in mapped:
    hour, one = line.split("\\t")
    counts[hour] = counts.get(hour, 0) + int(one)
print(counts)
''', notes={3: 'Mapper :: One “hour⇥1” line per order, then sorted like the shuffle.'},
         tryit='Our real data (Lesson 9.4 counters) peaks at 14:00 with 62,213 orders. A Streaming job would give the same numbers.'),
    dict(level='i', tag='Map-only · filter', title='A map-only Streaming job: find the thali orders',
         problem='<p>You need every thali order as a separate file set, no aggregation. Which options make a map-only job, and what are the output files called?</p>',
         inp='-numReduceTasks 0 · 3 splits',
         approach=['A filter needs no reducer: -numReduceTasks 0.',
                   'Each map task writes its own output file.',
                   'The mapper prints only matching lines.'],
         code='''orders = ["1,S1,t,dosa,45", "2,S2,t,thali,80", "3,S3,t,thali,80", "4,S4,t,chai,15"]
matches = [o for o in orders if o.split(",")[3] == "thali"]
print(len(matches), "matching lines:", matches)
print("output files with 3 splits:", [f"part-{n:05d}" for n in range(3)])
''', notes={2: 'Filter :: The mapper prints a line only when it matches; nothing else is emitted.'},
         tryit='The same job could be just -mapper "grep ,thali," : Streaming runs any command, not only Python.'),
    dict(level='a', tag='Performance · pipes', title='What do the pipes cost?',
         problem='<p>Our Streaming mapper printed 500,000 lines of about 10 bytes. Each record crosses two pipes on the map side (line in, line out) and one on the reduce side. If a pipe crossing costs about 2 µs of CPU per record (illustrative), how much CPU do the pipes add for 5 lakh records, and for 50 crore?</p>',
         inp='2 µs per crossing · 3 crossings per record',
         approach=['Crossings = records × 3.',
                   'CPU = crossings × 2 µs.',
                   'Compare small and large data.'],
         code='''for records in [500_000, 500_000_000]:
    seconds = records * 3 * 2e-6
    print(f"{records:>11,} records -> {seconds:,.0f} s of extra CPU")
''', notes={2: 'Overhead :: Linear in the number of records, on top of the speed of Python itself.'},
         tryit='3 s for our job, about 50 minutes of CPU for 50 crore records: small per record, real at scale. That is one reason Java or Spark wins for the heaviest jobs.'),
]

QUIZ = mix([
    dict(q='What is Hadoop Streaming?', options=['A real-time stream processor like Kafka', 'A utility that runs any stdin/stdout program as a mapper or reducer', 'A faster HDFS read path', 'A Python library for HDFS'], answer=1,
         why='Despite the name, it is batch MapReduce; “streaming” refers to lines streamed through pipes.'),
    dict(q='How does Hadoop split a mapper output line into key and value?', options=['At the first comma', 'At the first tab character', 'At the last space', 'It uses JSON'], answer=1,
         why='Text before the first tab is the key; with no tab, the whole line is the key.'),
    dict(q='What does a Streaming reducer receive on stdin?', options=['One key with a list of values', 'key⇥value lines sorted by key, which it must group itself', 'The raw input file', 'Unsorted lines from one mapper'], answer=1,
         why='There is no Iterable; equal keys are simply adjacent.'),
    dict(q='Why does the reducer script print once more after its loop?', options=['To flush stdout', 'The last key is still open when input ends', 'Hadoop requires an end marker', 'To print a header'], answer=1,
         why='Without it, the last category (snack in our run) would be missing.'),
    dict(q='Which option ships revenue_mapper.py and menu.csv to the worker nodes?', options=['-input', '-files', '-mapper', '-numReduceTasks'], answer=1,
         why='-files places them in each task\'s working folder.'),
    dict(q='Our broken mapper made the job log say “subprocess failed with code 1”. Where was the actual Python error?', options=['In the job client output', 'In the task\'s stderr, read with yarn logs', 'In the NameNode log', 'In part-00000'], answer=1,
         why='“NameError: name \'itme\' is not defined” was only in the container stderr.'),
    dict(q='How do you make a map-only Streaming job?', options=['Leave out -mapper', '-numReduceTasks 0', '-reducer none.py', '-D mapreduce.map.only=true'], answer=1,
         why='No reducer: map output goes straight to the output files.'),
    dict(q='What must be true on every NodeManager for a Python Streaming job to run?', options=['Spark must be installed', 'The right Python and every imported library must be installed', 'The script must be compiled', 'Nothing; Hadoop ships Python'], answer=1,
         why='Hadoop only ships your files, not the interpreter.'),
])

REVISION = [
    '<b>Hadoop Streaming</b>: any program reading stdin and writing stdout can be mapper, combiner or reducer.',
    'Output lines are split at the <b>first tab</b> into key and value; the reducer gets lines <b>sorted by key</b> and must detect key changes (and print the last key after the loop).',
    'Command: <code>mapred streaming -files m.py,r.py,menu.csv -input … -output … -mapper "python3 m.py" -reducer "python3 r.py"</code>.',
    'Lab: 5 lakh orders, 3 maps, 24.5 s; totals identical to the Java job (drink 1,90,033 orders, ₹30,52,315).',
    'Test locally: <code>cat data | mapper | sort | reducer</code>.',
    'Errors: job log says “PipeMapRed … subprocess failed with code 1”; the Python traceback is in <code>yarn logs … -log_files stderr</code>.',
    '<code>-numReduceTasks 0</code> = map-only; <code>stream.num.map.output.key.fields</code> = composite keys. Python must be on every node. New Python work usually uses PySpark.',
]
FAQ = [
    ('What is Hadoop Streaming?', 'A utility that comes with Hadoop which lets you write the mapper and reducer of a MapReduce job in any language. Each task runs your program as a subprocess, writes input records to its standard input as lines, and reads its standard output as key and value lines separated by a tab. The shuffle, sort, scheduling and fault tolerance are the same as for Java jobs.'),
    ('How do you run a Python MapReduce job on Hadoop?', 'Write a mapper and a reducer script that read sys.stdin and print key TAB value lines, test them with cat file | python3 mapper.py | sort | python3 reducer.py, then run mapred streaming -files mapper.py,reducer.py -input &lt;hdfs input&gt; -output &lt;hdfs output&gt; -mapper "python3 mapper.py" -reducer "python3 reducer.py". Python must be installed on every NodeManager.'),
    ('How is a Streaming reducer different from a Java reducer?', 'A Java reducer is called once per key with an Iterable of all its values. A Streaming reducer is one process that reads all the lines of its partition, sorted by key, so the script must remember the current key, accumulate values, and output a result whenever the key changes and once more at the end of input.'),
    ('How do I debug a failed Hadoop Streaming job?', 'The job output usually only shows “PipeMapRed.waitOutputThreads(): subprocess failed with code 1”. Read the failed task\'s stderr with yarn logs -applicationId &lt;id&gt; -log_files stderr (or the JobHistory UI) to see the real error, such as a Python traceback. Test the scripts first with a local Unix pipe, and never print debug text to stdout.'),
    ('Is Hadoop Streaming slower than Java MapReduce?', 'Usually somewhat, because every record is converted to text and passed through pipes to and from a separate process, and the scripting language itself may be slower. For many jobs the difference is small compared with the I/O; for CPU-heavy jobs Java or Spark is faster.'),
]

PRACTICE_INTRO = 'Streaming exercises with the real output of our lab run.'
PROBLEMS = [
    dict(level='easy', title='Check the local test', stmt='The local pipe test on 1,000 lines printed 179, 377, 162 and 282 orders. Check that they add up.', inp='4 counts',
         code='''print(179 + 377 + 162 + 282)
''', explain='1,000: every input line produced exactly one mapper line.'),
    dict(level='easy', title='Split a line like Hadoop', stmt='Split each mapper line at the FIRST tab into key and value, the way Streaming does.', inp='3 lines',
         code='''for line in ["meal\\t45", "drink\\t15\\textra", "notab"]:
    key, _, value = line.partition("\\t")
    print(repr(key), repr(value))
''', explain='Only the first tab counts; the rest stays in the value. A line with no tab becomes a key with an empty value.'),
    dict(level='easy', title='Average order value per category', stmt='From the cluster output, compute the average amount per order for each category.', inp='4 output lines',
         code='''out = {"breakfast": (90110, 2476620), "drink": (190033, 3052315), "meal": (80219, 4670075), "snack": (139638, 2652992)}
for c, (n, total) in out.items():
    print(f"{c:9} Rs {total / n:.2f}")
''', explain='Meals average about ₹58 an order, drinks about ₹16: dosa and thali vs chai and coffee.'),
    dict(level='medium', title='Reducer with a minimum and maximum', stmt='Extend the key-change reducer to also print the smallest and largest amount per key.', inp='sorted lines',
         code='''lines = sorted(["drink\\t15", "drink\\t20", "meal\\t45", "meal\\t80", "drink\\t15"])
current, vals = None, []
for line in lines + [None]:                     # None marks the end of input
    key, value = line.split("\\t") if line else (None, None)
    if key != current and current is not None:
        print(current, len(vals), min(vals), max(vals))
        vals = []
    current = key
    if value is not None:
        vals.append(int(value))
''', explain='A sentinel at the end replaces the separate “print the last key” step. Both patterns are fine; forgetting both is the bug.'),
    dict(level='medium', title='Counters from Python', stmt='Write the stderr line a Streaming script prints to increment a counter BAD_LINES in group Quality, and count how many it would print for this input.', inp='3 lines',
         code='''lines = ["1,S1,t,chai,15", "broken line", "3,S3,t,dosa"]
for line in lines:
    if len(line.split(",")) != 5:
        print("reporter:counter:Quality,BAD_LINES,1")   # in a real script: sys.stderr.write(... + "\\n")
''', explain='Two lines, so the job counter Quality / BAD_LINES would show 2 in the job output.'),
    dict(level='medium', title='Combiner-safe output', stmt='Our reducer prints category⇥orders⇥total, but the mapper prints category⇥amount. Why can\'t the reducer be used as -combiner unchanged? Show what the reducer would see after such a combiner.', inp='combiner output fed to the reducer',
         code='''combined = ["drink\\t3\\t50"]                         # what the reducer script would print as a combiner
key, value = combined[0].split("\\t", 1)
print("reducer would read value:", repr(value), "-> int() fails")
''', explain='A combiner\'s output must look like the mapper\'s output (Lesson 9.1). Here the value becomes "3\\t50", which int() cannot parse.'),
    dict(level='business', title='Rewrite or keep?', stmt='A nightly Streaming job takes 40 minutes of a 20-node cluster. A PySpark rewrite (2 developer-weeks at ₹1.2 lakh each) would take 12 minutes. Node-hours cost ₹50. How many nights until the rewrite pays for itself?', inp='40 → 12 minutes · 20 nodes · ₹50/node-hour',
         code='''saved_per_night = (40 - 12) / 60 * 20 * 50
print(f"Rs {saved_per_night:.0f} saved per night, pays back in {2 * 120000 / saved_per_night:.0f} nights")
''', explain='About ₹467 a night and roughly 514 nights (illustrative). Speed alone rarely justifies a rewrite; maintainability and team skills usually decide.'),
    dict(level='advanced', title='Secondary sort with two key fields', stmt='With stream.num.map.output.key.fields=2 and a partitioner on field 1 only, each reducer sees one student\'s orders sorted by time. Simulate it: partition on the student, sort on (student, time), and print each student\'s first order.', inp='5 lines, 2 reducers',
         code='''lines = ["S2\\t2026-09-03 08:05\\tchai", "S1\\t2026-09-02 13:05\\tthali", "S1\\t2026-09-02 08:10\\tchai",
         "S2\\t2026-09-02 09:00\\tpoha", "S1\\t2026-09-03 08:40\\tpoha"]
parts = {0: [], 1: []}
for l in lines:
    parts[int(l.split("\\t")[0][1:]) % 2].append(l)          # partition on field 1 only
for p in parts:
    current = None
    for l in sorted(parts[p]):                              # sort on fields 1 and 2
        s, t, item = l.split("\\t")
        if s != current:
            print(f"reducer {p}: {s} first order {t} {item}")
            current = s
''', explain='Each student lands in one reducer, already in time order, so the first line per student is the first order: Lesson 9.7\'s secondary sort without Java comparators.'),
]

SCN_INTRO = 'Streaming comes up when interviewers check whether you know MapReduce beyond Java, and in debugging questions.'
SCENARIOS = '''    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Concepts · basics</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“Can you write MapReduce in Python?”</h4>
      <p class="scn__situation">A common follow-up after the word count question.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> knowing Streaming and how its reducer differs.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Yes, with Hadoop Streaming: the mapper and reducer are scripts reading stdin and printing key⇥value lines.</li>
          <li>The reducer gets lines sorted by key, not a list per key, so it tracks the current key and emits on change (and at the end).</li>
          <li>Run with mapred streaming -files … -mapper "python3 m.py" -reducer "python3 r.py"; Python must be on every node. Today PySpark is usually preferred.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Debugging · logs</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>“subprocess failed with code 1” and nothing else</h4>
      <p class="scn__situation">A Streaming job that worked yesterday fails on every map attempt.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> where to look and likely causes.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Read the failed attempt's stderr: yarn logs -applicationId … -log_files stderr, or the JobHistory UI. That shows the Python traceback.</li>
          <li>Typical causes: a malformed input line (unpacking error), a missing module or different Python on some nodes, a file not shipped with -files.</li>
          <li>Reproduce locally with the failing split's data through the same pipe; make the script skip and count bad lines instead of crashing.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Design · trade-offs</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>Streaming, Java or PySpark for a new job?</h4>
      <p class="scn__situation">A team of Python developers must aggregate 5 TB of logs nightly on an existing Hadoop cluster.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> balanced reasoning, not a reflex.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Streaming: fastest to start with existing scripts; text pipes add CPU; limited control (no custom comparators without Java).</li>
          <li>Java MapReduce: best per-record efficiency and control, but a skills gap for this team.</li>
          <li>PySpark on YARN: Python skills, in-memory stages, SQL/DataFrames; usually the right default for new work if Spark is available.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Correctness · reducer</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“The last category is missing from the output”</h4>
      <p class="scn__situation">A Streaming job prints totals for drink, meal and breakfast, but never snack.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> the key-change reducer pattern.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>The reducer prints a key only when the next key arrives; the final key has no successor.</li>
          <li>Fix: after the loop, print the current key's result if current is not None (or use a sentinel).</li>
          <li>Test with a local pipe whose last sorted key is known, and with empty input.</li>
        </ul>
      </div></details>
    </article>
'''
