import os
HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)
BODY = body(HERE)
rd = lambda f: open(os.path.join(UP, f)).read()

META = dict(
    module='08-mapreduce-fundamentals', lesson='03-the-mapper', n='8.3',
    module_label='Module 8 · MapReduce fundamentals',
    title='The Mapper',
    desc='The Hadoop Mapper class explained with a real map-only job on Hadoop 3.5.0: Mapper<KEYIN, VALUEIN, KEYOUT, VALUEOUT>, the setup → map → cleanup lifecycle seen in real task logs, Context.write, custom counters (GOOD=300059, HEADER=42, WRONG_FIELDS=94, BAD_AMOUNT=107 on 300,302 dirty canteen orders), Writable types, object reuse, map-only jobs with part-m files and zero spilled records, skip vs fail on bad records. Python simulation, quiz and interview scenarios.',
    og_desc='Clean 3 lakh dirty orders with a map-only job, count every bad line with counters, and watch setup() and cleanup() run once per task.',
    minutes=26, level='Beginner',
    lead='The Mapper is where most of your MapReduce code lives. This lesson opens the class up: its four type parameters, the setup–map–cleanup lifecycle, the Context object and counters. We clean a deliberately dirty file of 300,302 orders with a map-only job on the lab cluster and account for every single line.',
    chips=['Map-only job on a real cluster', 'Custom counters: every line accounted for', 'Runs in your browser (Python)'],
)

RUN = dict(
    heading='Simulate a Mapper with setup, map, cleanup and counters',
    intro='<p>This Python class mirrors <code>CleanOrders.CleanMapper</code>. The <code>run()</code> method is what Hadoop\'s own <code>Mapper.run()</code> does: setup once, map per record, cleanup once. Counters are a dictionary here.</p>',
    code='''class CleanMapper:
    def setup(self, ctx):
        self.calls = 0
        print("setup() for split", ctx["split"])

    def map(self, key, line, ctx):
        self.calls += 1
        f = line.split(",")
        if f[0] == "order_id":
            ctx["counters"]["HEADER"] += 1; return
        if len(f) != 3:
            ctx["counters"]["WRONG_FIELDS"] += 1; return
        try:
            amount = int(f[2].strip())
        except ValueError:
            ctx["counters"]["BAD_AMOUNT"] += 1; return
        if amount <= 0:
            ctx["counters"]["BAD_AMOUNT"] += 1; return
        ctx["counters"]["GOOD"] += 1
        ctx["out"].append(f"{f[0]},{f[1].strip().lower()},{amount}")

    def cleanup(self, ctx):
        print("cleanup(): map() was called", self.calls, "times")

    def run(self, records, ctx):                 # what Hadoop's Mapper.run() does
        self.setup(ctx)
        for key, value in records:
            self.map(key, value, ctx)
        self.cleanup(ctx)

lines = ["order_id,item,amount", "1001,samosa,18", "901714,chai,abc", "1002,vada pav,20",
         "904721,Vada Pav ,20", "905000,samosa,-18", "906000,dosa", "907000,poha,25,extra"]
ctx = {"split": "dirty_orders.csv:0+2097152", "out": [],
       "counters": {"GOOD": 0, "HEADER": 0, "WRONG_FIELDS": 0, "BAD_AMOUNT": 0}}
offset, records = 0, []
for l in lines:                                   # TextInputFormat: key = byte offset
    records.append((offset, l))
    offset += len(l) + 1
CleanMapper().run(records, ctx)
print(ctx["counters"])
print(ctx["out"])
''',
    anno=[
        ('    def run(self, records, ctx):                 # what Hadoop\'s Mapper.run() does', 'Hadoop calls run(); the default runs setup, then map for every record, then cleanup. You rarely override it.'),
        ('        ctx["counters"]["GOOD"] += 1', 'Like ctx.getCounter(Quality.GOOD).increment(1): Hadoop sums these over all tasks of the job.'),
        ('        ctx["out"].append(f"{f[0]},{f[1].strip().lower()},{amount}")', 'Like context.write(): trim and lower-case repairs “Vada Pav ” into “vada pav”.'),
    ],
    tasks=[
        dict(label='1 · One map task', hint='Press <b>Run</b>. Check that the four counters add up to the 8 input lines.', code=None),
        dict(label='2 · Three map tasks', hint='<b>Predict first:</b> split the lines into 3 tasks. Each task has its own <code>calls</code>, but there is one set of counters for the job. What do the cleanup() lines print?',
             code='''lines = ["order_id,item,amount", "1001,samosa,18", "901714,chai,abc", "1002,vada pav,20",
         "904721,Vada Pav ,20", "905000,samosa,-18", "906000,dosa", "907000,poha,25,extra"]
splits = [lines[0:3], lines[3:6], lines[6:8]]
job_counters = {"GOOD": 0, "BAD": 0}
for n, split in enumerate(splits):
    calls = 0                                    # a Mapper field: one per task
    for line in split:
        calls += 1
        f = line.split(",")
        ok = len(f) == 3 and f[2].strip().lstrip("-").isdigit() and int(f[2]) > 0
        job_counters["GOOD" if ok else "BAD"] += 1
    print(f"task {n}: cleanup() says map() was called {calls} times")
print("job counters:", job_counters)
'''),
        dict(label='3 · Emit 0, 1 or many', hint='A mapper may write any number of pairs per record. This one emits one (word, 1) per word and nothing for empty lines. Count the pairs.',
             code='''lines = ["the chai was hot", "", "dosa was cold"]
pairs = []
for line in lines:
    for word in line.split():
        pairs.append((word, 1))
print(len(lines), "records ->", len(pairs), "pairs")
print(pairs)
'''),
        dict(label='4 · Read a setting', hint='Jobs get parameters with <code>-D min.amount=20</code> and read them with <code>context.getConfiguration().getInt(...)</code>. Make the mapper drop orders below the configured minimum.',
             code='''conf = {"min.amount": "20"}                       # from -D min.amount=20
min_amount = int(conf.get("min.amount", "0"))      # read once, as in setup()
orders = ["1001,samosa,18", "1002,vada pav,20", "1003,dosa,45", "1005,chai,15"]
for o in orders:
    if int(o.split(",")[2]) >= min_amount:
        print(o)
'''),
        dict(label='5 · Spot the error', hint='This mapper has no checks. Which line of the dirty file makes it crash, and what would Hadoop do with the task? Add a try/except and a counter.',
             code='''lines = ["1001,samosa,18", "1002,vada pav,20", "901714,chai,abc"]
for line in lines:
    oid, item, amount = line.split(",")
    print(item, int(amount))
''', expect='error'),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run it on your PC: clean dirty orders with a map-only job',
    intro='<p>Use the Module 8 lab from Lesson 8.1. First create the dirty file next to <code>canteen_orders.csv</code> with <code>make_dirty.py</code>, then copy both files below into <code>/tmp/mr</code> in the namenode container, compile and run <code>mapper_lab.sh</code>.</p>',
    items=[
        dict(title='Make the dirty data', file='make_dirty.py',
             cmd=rd('make_dirty.py') + '\n# Run, next to canteen_orders.csv (from Lesson 4.3):\n#   python3 make_dirty.py\n#   docker cp dirty_orders.csv lab8-namenode-1:/tmp/mr/',
             output="300302 lines; {'{id},chai,abc': 46, '{id},poha,25,extra': 47, '{id},dosa': 47, 'order_id,item,amount': 41, '{id},Vada Pav ,20': 59, '{id},samosa,-18': 61}",
             note='Real output. Seeded, so you get exactly the same 301 extra lines. These numbers explain every counter in the next step.'),
        dict(title='The cleaning mapper and the lab run', file='CleanOrders.java',
             cmd=rd('java/CleanOrders.java') + '\n\n// ---- mapper_lab.sh ----\n' + '\n'.join('// ' + l for l in rd('mapper_lab.sh').strip().split('\n')) + '\n\n// In the mr-lab folder:\n//   docker cp CleanOrders.java lab8-namenode-1:/tmp/mr/\n//   docker cp mapper_lab.sh lab8-namenode-1:/tmp/mr/\n//   docker exec lab8-namenode-1 bash -c \'cd /tmp/mr && mkdir -p classes && javac -cp $(hadoop classpath) -d classes *.java && jar cf mr.jar -C classes .\'\n//   docker exec lab8-namenode-1 bash /tmp/mr/mapper_lab.sh',
             output=rd('tx83.txt').strip(),
             note='Real output. Container _000001 is the MRAppMaster, which is why it has no setup() or cleanup() lines. Which worker runs which task will differ on your PC.'),
    ],
)

TRACE = dict(
    heading='Mapper.run(): one setup, many maps, one cleanup',
    intro='<p>Hadoop\'s <code>Mapper.run()</code> in a few lines of Python. Watch <code>calls</code> grow and <code>bad</code> count the skipped lines.</p>',
    code='''records = [(0, "1001,chai,15"), (13, "1002,chai,abc"), (27, "1003,dosa,45")]
calls, bad, out = 0, 0, []
print("setup()")
for key, value in records:
    calls += 1
    f = value.split(",")
    if not f[2].isdigit():
        bad += 1
        continue
    out.append((f[1], int(f[2])))
print("cleanup()", calls, "calls,", bad, "bad")
print(out)
''',
    notes={3: 'setup :: Runs once, before the first record.',
           8: 'Counter :: The bad record is counted and skipped, not written.',
           11: 'cleanup :: Runs once, after the last record.'},
)

WORKED_INTRO = 'Three Mapper problems: picking the type parameters, deciding skip vs fail, and making a slow mapper fast.'
EXAMPLES = [
    dict(level='b', tag='Types · generics', title='Choose the four type parameters',
         problem='<p>A mapper reads text lines <code>student_id,canteen,amount</code> and emits (canteen, amount). Write its <code>Mapper&lt;…&gt;</code> declaration and show what one line becomes.</p>',
         inp='TextInputFormat · line “S17,north,45”',
         approach=['Text input gives (byte offset, line): LongWritable, Text.',
                   'Output key is a canteen name: Text. Output value is an amount: IntWritable.',
                   'Simulate one record.'],
         code='''key, value = 0, "S17,north,45"
sid, canteen, amount = value.split(",")
print("Mapper<LongWritable, Text, Text, IntWritable>")
print((key, value), "->", (canteen, int(amount)))
''', notes={3: 'Generics :: KEYIN, VALUEIN, KEYOUT, VALUEOUT, in that order.'},
         tryit='If the mapper only needs to pass lines through, KEYOUT becomes NullWritable, as in CleanOrders.'),
    dict(level='i', tag='Design · bad data', title='Skip and count, or fail the job?',
         problem='<p>A job loads 10 crore bank transactions a night. Policy: up to 0.01% bad rows may be skipped; above that the load must stop. The mapper counts BAD rows. How does the driver enforce this, and is our canteen file (243 bad of 300,302) acceptable under the same policy?</p>',
         inp='limit 0.01% · canteen: 243 / 300,302',
         approach=['Mappers skip and count; they cannot see the job total.',
                   'After waitForCompletion(), the driver reads the counters and decides.',
                   'Compute the canteen ratio.'],
         code='''bad, total = 243, 300302
ratio = bad / total * 100
print(f"bad = {ratio:.3f}% ->", "OK" if ratio <= 0.01 else "STOP the pipeline")
''', notes={3: 'Decide in the driver :: Only the driver sees job-wide counter totals.'},
         tryit='0.081%: eight times over the bank\'s limit. Throwing an exception inside map() instead would fail the task on the first bad row, retry it 4 times and kill the whole job.'),
    dict(level='a', tag='Performance · reuse', title='Why setup() and object reuse matter',
         problem='<p>A mapper compiles a regex and creates a new <code>Text</code> for every record. Compiling costs 20 µs, creating an object 0.2 µs plus garbage-collection work. For 2.7 crore records, how much time goes to work that could be done once?</p>',
         inp='27,000,000 records · 20 µs + 0.2 µs per record',
         approach=['Per-record waste × records.',
                   'Move the compile to setup() and reuse one Text field.',
                   'Compare with doing it once per task (4 tasks).'],
         code='''records, tasks = 27_000_000, 4
waste = records * (20 + 0.2) / 1e6
print(f"in map(): {waste:.0f} s of CPU; in setup(): {tasks * 20 / 1e6:.5f} s")
''', notes={3: 'Once per task :: setup() runs 4 times for 4 tasks, map() 2.7 crore times.'},
         tryit='545 s of CPU, about 9 minutes, saved by moving two lines. On real clusters, the same mistake with a database connection in map() can take a job down.'),
]

QUIZ = mix([
    dict(q='What are the four type parameters of Mapper, in order?', options=['KEYOUT, VALUEOUT, KEYIN, VALUEIN', 'KEYIN, VALUEIN, KEYOUT, VALUEOUT', 'INPUT, OUTPUT, KEY, VALUE', 'KEY, VALUE, SPLIT, CONTEXT'], answer=1,
         why='Mapper<KEYIN, VALUEIN, KEYOUT, VALUEOUT>; for text input KEYIN is LongWritable and VALUEIN is Text.'),
    dict(q='How many times is setup() called in a job with 3 map tasks?', options=['Once for the whole job', '3 times, once per map task', 'Once per record', 'Never, unless configured'], answer=1,
         why='Our logs had one setup() line per task.'),
    dict(q='How many times is map() called in a map task?', options=['Once', 'Once per input record of its split', 'Once per key', 'Once per block'], answer=1,
         why='137,786 + 131,050 + 31,466 = 300,302 = Map input records.'),
    dict(q='How do you count bad records across the whole job?', options=['A static int in the Mapper', 'Counters via context.getCounter(...).increment(1)', 'Print to System.out', 'Write them to a reducer'], answer=1,
         why='Fields live in one task\'s JVM; counters are summed by the framework.'),
    dict(q='What happens when the number of reduce tasks is 0?', options=['The job fails', 'Map output goes straight to the output files (part-m-*), with no sort or shuffle', 'One reducer is used anyway', 'Output is kept in memory'], answer=1,
         why='Our map-only job reported Spilled Records=0 and wrote part-m-00000 to 00002.'),
    dict(q='Why reuse one Text object for output in a mapper?', options=['It is required by Hadoop', 'To avoid creating crores of short-lived objects; write() serializes immediately', 'Because Text cannot be created twice', 'So keys are sorted'], answer=1,
         why='Reuse is safe for output and saves garbage collection.'),
    dict(q='A mapper stores the input value objects in a list and later finds they are all the same line. Why?', options=['HDFS returned duplicate lines', 'Hadoop reuses the same value object for every record, so the list holds many references to it', 'The split was read twice', 'Counters overwrote them'], answer=1,
         why='Copy with new Text(value) before keeping it.'),
    dict(q='What happens if map() throws an exception on a bad record?', options=['The record is skipped automatically', 'The task attempt fails and is retried; after 4 failed attempts the job fails', 'The reducer handles it', 'Hadoop removes the record from HDFS'], answer=1,
         why='Skip and count instead when bad data is expected.'),
])

REVISION = [
    '<code>Mapper&lt;KEYIN, VALUEIN, KEYOUT, VALUEOUT&gt;</code>; text input = (LongWritable offset, Text line).',
    '<b>run()</b> = <code>setup()</code> once → <code>map()</code> per record → <code>cleanup()</code> once; one Mapper object per map task.',
    '<code>context.write()</code> 0, 1 or many times; <code>getCounter</code>, <code>getConfiguration</code>, <code>getInputSplit</code>.',
    'Writables: Text, IntWritable, LongWritable, DoubleWritable, NullWritable; reuse your output objects, copy input values before storing.',
    'Fields are per task; job-wide numbers need <b>counters</b>. Lab: GOOD 300,059 + HEADER 42 + WRONG_FIELDS 94 + BAD_AMOUNT 107 = 300,302.',
    '<b>Map-only</b>: <code>setNumReduceTasks(0)</code> → <code>part-m-NNNNN</code>, no sort, Spilled Records=0.',
    'Expected bad data: skip and count; unexpected: throw (task retried, then job fails). Heavy work in <code>setup()</code>.',
]
FAQ = [
    ('What is the Mapper in Hadoop MapReduce?', 'The Mapper is the user class that processes input records. Hadoop runs one map task per input split; inside it, the Mapper\'s setup() is called once, map() once for every key-value record from the RecordReader, and cleanup() once. map() emits intermediate key-value pairs through the Context, which are then partitioned, sorted and shuffled to reducers (or written directly as output in a map-only job).'),
    ('What are setup() and cleanup() used for in a Mapper?', 'setup() runs once per map task before any record: use it to read configuration values, load small lookup files, compile patterns or open resources. cleanup() runs once after the last record: use it to emit results aggregated inside the task (in-mapper combining) and to close resources.'),
    ('What is a map-only job?', 'A job with the number of reduce tasks set to 0 (job.setNumReduceTasks(0)). The output of each map task is written directly by the OutputFormat as part-m-NNNNN files, skipping the sort, spill, shuffle and reduce phases. It suits filtering, cleaning, format conversion and enrichment.'),
    ('How do you create custom counters in MapReduce?', 'Define a Java enum (enum Quality { GOOD, BAD }) and call context.getCounter(Quality.GOOD).increment(1), or use context.getCounter("group", "name"). The framework sums counters from all task attempts that succeed and shows them in the job output, the web UI and job.getCounters() in the driver.'),
    ('Why does Hadoop use Writable types instead of Java types?', 'Writable types (Text, IntWritable, LongWritable…) serialize compactly to a byte stream with write() and readFields(), are fast to compare in their serialized form during the sort, and can be reused and refilled with set() to avoid creating objects for every record. Keys must be WritableComparable so they can be sorted.'),
]

PRACTICE_INTRO = 'Mapper exercises built on the real counters and logs from the lab.'
PROBLEMS = [
    dict(level='easy', title='Every line accounted for', stmt='Check that the four counters add up to Map input records.', inp='GOOD 300059 · HEADER 42 · WRONG_FIELDS 94 · BAD_AMOUNT 107',
         code='''print(300059 + 42 + 94 + 107 == 300302)
''', explain='True: each line hits exactly one counter.'),
    dict(level='easy', title='Explain BAD_AMOUNT', stmt='make_dirty.py added 46 “abc” amounts and 61 negative amounts. Do they explain BAD_AMOUNT=107?', inp='46 + 61',
         code='''print(46 + 61)
''', explain='107: both kinds fail the amount check, one in parseInt, one in the “≤ 0” test.'),
    dict(level='easy', title='map() calls per task', stmt='Add the three map() call counts from the task logs.', inp='137,786 · 131,050 · 31,466',
         code='''print(137786 + 131050 + 31466)
''', explain='300,302, equal to Map input records: map() is called once per record, in exactly one task.'),
    dict(level='medium', title='Repair counted', stmt='Without the trim/lower-case repair, how many “vada pav,20” lines would be in the output, and which counter would the 59 “Vada Pav ” lines land in?', inp='50,045 with repair · 59 repaired',
         code='''print(50045 - 59, "lines; the 59 would still be GOOD, just with a different item name")
''', explain='49,986. They would pass all checks and be written as “Vada Pav ”, creating a seventh “item” in later reports. Counters only catch what you test for.'),
    dict(level='medium', title='Output size per task', stmt='The three part-m files are 2,094,939, 2,095,388 and 502,829 bytes. Why is the last one about a quarter of the others?', inp='split lengths 2 MB, 2 MB, 0.48 MB',
         code='''print(503302 / 2097152)
''', explain='Its split is only 503,302 bytes (0.24 of a 2 MB split), the leftover end of the file.'),
    dict(level='medium', title='In-mapper totals', stmt='Instead of emitting (item, amount) for every order, keep totals in a dictionary and emit them once in cleanup(). How many pairs leave this task?', inp='one task, 6 orders',
         code='''orders = [("chai", 15), ("dosa", 45), ("chai", 15), ("poha", 25), ("dosa", 45), ("chai", 15)]
totals = {}
for item, amount in orders:                 # map()
    totals[item] = totals.get(item, 0) + amount
for item, total in totals.items():          # cleanup()
    print(item, total)
print(len(orders), "records ->", len(totals), "pairs emitted")
''', explain='3 pairs instead of 6. With 6 items and 9 lakh orders per task, 6 pairs instead of 9 lakh, which shrinks the shuffle enormously (combiners do this automatically, Lesson 9.1).'),
    dict(level='business', title='Is the tablet vendor good enough?', stmt='The contract says at most 1 bad order line per 1,000. Our file has 243 bad lines among 300,302 (ignoring the one true header). Does the vendor meet it?', inp='242 bad of 300,301 data lines',
         code='''rate = (243 - 1) / 300301 * 1000
print(f"{rate:.2f} bad lines per 1,000 ->", "OK" if rate <= 1 else "breach")
''', explain='0.81 per 1,000: within the contract, barely. Counters give the manager this number every night for free.'),
    dict(level='advanced', title='Mapper with a lookup in setup()', stmt='Load a price list once in setup() and flag orders whose amount does not match the menu price, using a counter.', inp='menu + 5 orders',
         code='''class PriceCheck:
    def setup(self):
        self.menu = {"chai": 15, "samosa": 18, "dosa": 45}      # e.g. read from a small file
        self.counters = {"OK": 0, "WRONG_PRICE": 0}
    def map(self, line):
        oid, item, amount = line.split(",")
        key = "OK" if self.menu.get(item) == int(amount) else "WRONG_PRICE"
        self.counters[key] += 1
m = PriceCheck(); m.setup()
for line in ["1,chai,15", "2,dosa,40", "3,samosa,18", "4,chai,20", "5,dosa,45"]:
    m.map(line)
print(m.counters)
''', explain='OK 3, WRONG_PRICE 2. The menu is loaded once per task, not once per line; Lesson 9.6 ships such files to every task with the distributed cache.'),
]

SCN_INTRO = 'Mapper questions test whether you have written real MapReduce code: lifecycle, types, counters and the reuse trap.'
SCENARIOS = '''    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Concepts · lifecycle</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“What methods does a Mapper have, and when are they called?”</h4>
      <p class="scn__situation">A standard question after “explain MapReduce”.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> setup, map, cleanup, run, and one object per task.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>run() drives the task: setup() once, map() for every record of the split, cleanup() once.</li>
          <li>One Mapper instance per map task; tasks don't share fields.</li>
          <li>setup for configuration and lookups, cleanup for emitting in-task totals and closing resources.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Data quality · design</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>The job fails with NumberFormatException after 40 minutes</h4>
      <p class="scn__situation">One line in 3 crore has “N/A” as the amount.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> defensive mappers and counters.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Catch the parse error, increment a BAD_AMOUNT counter and skip (or write the line to a side output for review).</li>
          <li>In the driver, read the counters and fail the pipeline only if the bad ratio exceeds an agreed threshold.</li>
          <li>Throwing in map() makes the task retry 4 times on the same line and then kills the whole job.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Debugging · object reuse</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>A mapper that buffers lines outputs the same line again and again</h4>
      <p class="scn__situation">The code adds each value to an ArrayList and emits the list in cleanup().</p>
      <p class="scn__look"><b>The interviewer is checking:</b> knowing that Hadoop reuses input objects.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>The RecordReader refills the same Text object for every record, so the list holds many references to one object, which ends up holding the last line.</li>
          <li>Fix: store copies (new Text(value) or value.toString()).</li>
          <li>Also check the buffer size: holding a whole split in memory can exceed the container's heap.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Performance · design</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>“Our cleaning job has 200 reducers that just write what they receive. Can it be faster?”</h4>
      <p class="scn__situation">An inherited ETL job validates records and passes them through an identity reducer.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> map-only jobs.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>If nothing needs grouping or sorting, set the reducers to 0: no spill, sort or shuffle, often several times faster.</li>
          <li>Output becomes one part-m file per map task; if file count matters, tune split size or compact later.</li>
          <li>Keep data-quality numbers in counters and check them in the driver.</li>
        </ul>
      </div></details>
    </article>
'''
