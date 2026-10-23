import os
HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)
BODY = body(HERE)
rd = lambda f: open(os.path.join(UP, f)).read()

META = dict(
    module='09-mapreduce-in-depth', lesson='04-counters', n='9.4',
    module_label='Module 9 · MapReduce in depth',
    title='Counters',
    desc='Hadoop MapReduce counters on a real Hadoop 3.5.0 cluster: built-in counter groups, enum counters and dynamic counters, read back in the driver with getCounters(). A map-only job with NullOutputFormat counts 5 lakh orders by category (DRINK 190,033 …), by hour (14:00 busiest, 62,213) and revenue per category, then a data-quality gate sets the exit code. One counter per student fails the job: “Too many counters: 121 max=120”. How counters flow, why failed attempts don\'t count, limits, Python simulation, quiz and interview scenarios.',
    og_desc='A job with no output file that answers every question through counters, and the one extra line that makes it fail: “Too many counters: 121 max=120”.',
    minutes=24, level='Intermediate',
    lead='Counters are the job\'s built-in tally sheet: every task counts, Hadoop adds the counts up, and the driver reads the totals. This lesson uses them to answer questions without writing a single output file, turns one into a data-quality gate, and then breaks the 120-counter limit on purpose to see why counters are not for per-key data.',
    chips=['Answers from counters alone', 'Limit hit live: 121 max=120', 'Runs in your browser (Python)'],
)

RUN = dict(
    heading='Simulate how task counters become job counters',
    intro='<p>Each map task attempt keeps its own counters. The job total is the sum over the <b>successful</b> attempt of each task. Here map 1\'s first attempt fails half-way and is retried.</p>',
    code='''attempts = [
    # (task, attempt, state, counters this attempt incremented)
    ("m_0", 0, "SUCCEEDED", {"DRINK": 64000, "SNACK": 46500, "MEAL": 26700}),
    ("m_1", 0, "FAILED",    {"DRINK": 30000, "SNACK": 21000, "MEAL": 12000}),   # died half-way
    ("m_1", 1, "SUCCEEDED", {"DRINK": 63500, "SNACK": 46800, "MEAL": 26900}),
    ("m_2", 0, "SUCCEEDED", {"DRINK": 62533, "SNACK": 46338, "MEAL": 26619}),
]

job = {}
for task, n, state, counters in attempts:
    if state != "SUCCEEDED":
        print(f"{task} attempt {n}: {state}, its counts are dropped")
        continue
    for name, value in counters.items():
        job[name] = job.get(name, 0) + value

for name in sorted(job):
    print(f"{name:6} {job[name]:,}")
''',
    anno=[
        ('    if state != "SUCCEEDED":', 'Only successful attempts count, so a retried task is never counted twice.'),
        ('        job[name] = job.get(name, 0) + value', 'The framework adds the same-named counter from every task: DRINK becomes 190,033 as in our lab.'),
    ],
    tasks=[
        dict(label='1 · Merge task counters', hint='Press <b>Run</b>. Check that DRINK is 190,033, as in the lab. What would it be if the failed attempt were added too?', code=None),
        dict(label='2 · Dynamic counter names', hint='Build the “Orders by hour” group from order times, as <code>getCounter("Orders by hour", hour)</code> does. How many counter names appear?',
             code='''times = ["2026-09-14 15:30", "2026-09-26 20:11", "2026-09-01 13:37", "2026-09-02 14:05", "2026-09-02 14:59"]
group = {}
for t in times:
    hour = t[11:13]                        # same as f[2].substring(11, 13) in Java
    group[hour] = group.get(hour, 0) + 1
print(len(group), "counters:", dict(sorted(group.items())))
'''),
        dict(label='3 · Quality gate', hint='Decide the exit code like the driver does: exit 2 if any UNKNOWN orders, or if bad rows are more than 0.1% of the input.',
             code='''counters = {"MAP_INPUT_RECORDS": 500000, "UNKNOWN": 0, "BAD_ROWS": 380}
bad_share = counters["BAD_ROWS"] / counters["MAP_INPUT_RECORDS"]
if counters["UNKNOWN"] > 0 or bad_share > 0.001:
    print(f"exit 2 (bad share {bad_share:.3%})")
else:
    print(f"exit 0 (bad share {bad_share:.3%})")
'''),
        dict(label='4 · Will it fit?', hint='<b>Predict first:</b> the job already has about 100 counters (built-in plus ours). Which of these extra dynamic groups stay within the 120 limit?',
             code='''LIMIT, used = 120, 100
plans = {"orders by hour (13)": 13, "orders by weekday (7)": 7, "orders by item (8)": 8, "orders by student (2000)": 2000}
for name, n in plans.items():
    print(f"{name:26} -> {used + n:5} counters", "OK" if used + n <= LIMIT else "FAILS")
'''),
        dict(label='5 · Spot the error', hint='This counter class mimics Hadoop\'s limit check. Run it with one counter per student and read the error, then fix the design: what should hold per-student numbers instead?',
             code='''class Counters:
    def __init__(self, limit=120):
        self.values, self.limit = {}, limit
    def incr(self, group, name, n=1):
        key = (group, name)
        if key not in self.values and len(self.values) >= self.limit:
            raise RuntimeError(f"Too many counters: {len(self.values) + 1} max={self.limit}")
        self.values[key] = self.values.get(key, 0) + n

c = Counters()
for s in range(1, 2001):
    c.incr("Orders by student", f"S{s:04d}")
''', expect='error'),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run it on your PC: a counters-only job, then too many counters',
    intro='<p>Uses the Module 8 lab cluster (Lesson 8.1). <code>student_orders.csv</code> and <code>menu.csv</code> come from <code>make_student_orders.py</code>, shared by all Module 9 lessons. Copy the files into the namenode container, compile the Module 9 programs into <code>mr9.jar</code>, then run the script.</p>',
    items=[
        dict(title='Enum and dynamic counters, read by the driver', file='OrderCounters.java',
             cmd=rd('java/OrderCounters.java') + '\n// In the mr-lab folder:\n//   python3 make_student_orders.py\n//   docker exec lab8-namenode-1 mkdir -p /tmp/mr9\n//   docker cp OrderCounters.java lab8-namenode-1:/tmp/mr9/\n//   docker cp student_orders.csv lab8-namenode-1:/tmp/mr9/\n//   docker exec -it lab8-namenode-1 bash\n// Inside the container:\n//   cd /tmp/mr9\n//   hdfs dfs -D dfs.blocksize=8388608 -put student_orders.csv /user/hadoop/data/\n//   mkdir -p classes && javac -cp $(hadoop classpath) -d classes *.java && jar cf mr9.jar -C classes .\n//   hadoop jar mr9.jar OrderCounters /user/hadoop/data/student_orders.csv',
             output=rd('tx94.txt').split('== one dynamic')[0].strip(),
             note='Real output. The file is stored with 8 MB blocks so the job has 3 map tasks; the counters are the sum of all three. Nothing is written to HDFS.'),
        dict(title='The whole lab, including the counter limit', file='counters_lab.sh',
             cmd=rd('counters_lab.sh') + '\n# Inside the namenode container, in /tmp/mr9 (attempts are read from the JobHistory Server REST API):\n#   bash counters_lab.sh',
             output=rd('tx94.txt').strip(),
             note='Real output. With per-student counters every map attempt fails within seconds with LimitExceededException; after one task fails 4 times the job is failed. The limit is mapreduce.job.counters.max (120).'),
    ],
)

TRACE = dict(
    heading='Counting categories the way the mapper does',
    intro='<p>Follow four orders updating an enum-style group and a dynamic “Revenue” group, exactly like the three <code>getCounter(...).increment(...)</code> lines in <code>OrderCounters.java</code>.</p>',
    code='''cat = {"chai": "DRINK", "samosa": "SNACK", "dosa": "MEAL"}
orders = [("chai", 15), ("dosa", 45), ("chai", 15), ("samosa", 18)]
count = {}
revenue = {}
for item, amount in orders:
    c = cat.get(item, "UNKNOWN")
    count[c] = count.get(c, 0) + 1
    revenue[c] = revenue.get(c, 0) + amount
print(count)
print(revenue)
''',
    notes={6: 'Category :: Unknown items would land in UNKNOWN, which the driver checks.',
           7: 'increment(1) :: One per order, like ctx.getCounter(c).increment(1).',
           8: 'increment(amount) :: A counter is a long; it can add any number, here rupees.'},
)

WORKED_INTRO = 'Three counter problems: reading a quality gate, designing counter names, and explaining a surprising number.'
EXAMPLES = [
    dict(level='b', tag='Reading · built-in', title='What do these counters say about the job?',
         problem='<p>From Lesson 8.3: Map input records = 300,302; GOOD = 300,059; HEADER = 42; WRONG_FIELDS = 94; BAD_AMOUNT = 107. Do the custom counters explain every input record? What share of the input was bad?</p>',
         inp='five counters from CleanOrders',
         approach=['Add the custom counters and compare with Map input records.',
                   'Bad = everything except GOOD.',
                   'Share = bad / input.'],
         code='''inp, good, header, wrong, bad_amount = 300302, 300059, 42, 94, 107
print("explained:", good + header + wrong + bad_amount == inp)
bad = inp - good
print(f"bad rows {bad} = {bad / inp:.3%} of input")
''', notes={2: 'Check :: Every record falls in exactly one quality bucket: a good sign the code is right.'},
         tryit='Write the quality gate: fail the job if bad rows (excluding headers) exceed 0.05% of the input.'),
    dict(level='i', tag='Design · names', title='Counters or output?',
         problem='<p>A team wants, for a 10-crore-row clickstream job: (a) number of rows with a missing user id, (b) clicks per page for 40,000 pages, (c) clicks per device type (mobile, desktop, tablet, other), (d) clicks per country (about 200). Which belong in counters?</p>',
         inp='4 requested statistics',
         approach=['Counters suit a small, fixed set of names.',
                   'Count the names each statistic needs.',
                   'Compare with the 120-counter limit and the built-ins already used (about 50).'],
         code='''LIMIT, builtin = 120, 50
wants = {"missing user id": 1, "clicks per device": 4, "clicks per country": 200, "clicks per page": 40000}
used = builtin
for name, n in wants.items():
    ok = used + n <= LIMIT
    print(f"{name:20} {n:6} names -> {'counter' if ok else 'job output'}")
    if ok:
        used += n
''', notes={8: 'Budget :: Each accepted group uses part of the job\'s 120.'},
         tryit='200 country names would break the limit, and per-country clicks are data anyway. A reducer keyed by country is the right tool.'),
    dict(level='a', tag='Internals · attempts', title='Why didn\'t the speculative copy double the count?',
         problem='<p>In Lesson 8.1, 5 map attempts ran for 4 splits (one speculative copy was killed after processing about a quarter of its split). Map input records was exactly 27,000,000, the true number of lines. Show why, using attempt states.</p>',
         inp='4 successful attempts + 1 killed',
         approach=['List what every attempt read.',
                   'Sum all attempts (wrong) and only successful ones (what Hadoop does).',
                   'Compare with 27,000,000.'],
         code='''attempts = [("m0_0", "SUCCEEDED", 6750000), ("m0_1", "KILLED", 1700000),
            ("m1_0", "SUCCEEDED", 6750000), ("m2_0", "SUCCEEDED", 6750000), ("m3_0", "SUCCEEDED", 6750000)]
all_attempts = sum(n for _, _, n in attempts)
successful = sum(n for _, s, n in attempts if s == "SUCCEEDED")
print(f"all attempts {all_attempts:,} · successful only {successful:,}")
''', notes={4: 'Rule :: Hadoop keeps only the successful attempt\'s counters per task.'},
         tryit='The split sizes are rounded to equal shares here. While a job runs, the UI may show the killed copy\'s counts for a moment; final values never do.'),
]

QUIZ = mix([
    dict(q='What is a MapReduce counter?', options=['A record in the output file', 'A job-wide long value that tasks increment and the framework adds up', 'The number of reducers', 'A log line'], answer=1,
         why='Each task keeps its own; the framework sums them for the job.'),
    dict(q='Which line creates a dynamic counter?', options=['ctx.getCounter(Category.DRINK).increment(1)', 'ctx.getCounter("Orders by hour", "14").increment(1)', 'job.setNumReduceTasks(0)', 'ctx.write(key, value)'], answer=1,
         why='Group and name are strings chosen at run time.'),
    dict(q='How did the driver get the counter values?', options=['By reading part files', 'job.getCounters() after waitForCompletion, then findCounter / getGroup', 'From the NameNode', 'From yarn logs only'], answer=1,
         why='The final counters come back to the client when the job ends.'),
    dict(q='A map task fails half-way and its retry succeeds. What happens to the counts from the failed attempt?', options=['They are added to the job total', 'They are dropped; only the successful attempt counts', 'They are halved', 'The job fails'], answer=1,
         why='That is why retries and speculative copies never double-count.'),
    dict(q='Why did one counter per student fail the job?', options=['Counters can\'t be strings', 'It exceeded mapreduce.job.counters.max (120): “Too many counters: 121 max=120”', 'Students have no orders', 'Map-only jobs can\'t use counters'], answer=1,
         why='2,000 names, far above the limit; every attempt hit it.'),
    dict(q='Which job produced no output files at all?', options=['One with 1 reducer', 'One with 0 reducers and NullOutputFormat', 'One with a combiner', 'One with a custom partitioner'], answer=1,
         why='OrderCounters: all results were counters.'),
    dict(q='Which is a good use of a custom counter?', options=['Revenue for every one of 2,000 students', 'The number of malformed input lines', 'The list of all order ids', 'Clicks per URL'], answer=1,
         why='A small, fixed set of names about the job itself.'),
    dict(q='What should a pipeline do with a data-quality counter?', options=['Ignore it', 'Let the driver check it and exit non-zero above a threshold', 'Print it to the reducer output', 'Raise the counter limit'], answer=1,
         why='The scheduler sees the failed exit code and stops the next steps.'),
])

REVISION = [
    'Counter = job-wide <b>long</b> in a <b>group</b>; tasks increment, the framework sums.',
    'Built-in groups: File System, Job Counters, Map-Reduce Framework, File Input/Output Format, Shuffle Errors.',
    '<b>Enum</b> counters: <code>getCounter(Category.DRINK)</code>. <b>Dynamic</b>: <code>getCounter("group", "name")</code>.',
    'Final values = sum over each task\'s <b>successful attempt</b>; failed and killed attempts don\'t count.',
    'Driver: <code>job.getCounters()</code>, <code>findCounter</code>, <code>getGroup</code>; exit non-zero as a quality gate.',
    'Lab: DRINK 190,033 · SNACK 139,638 · BREAKFAST 90,110 · MEAL 80,219; busiest hour 14:00 (62,213); no output files.',
    'Limit: <code>mapreduce.job.counters.max</code> = 120 (groups 50). Per-student counters → “Too many counters: 121 max=120”.',
]
FAQ = [
    ('What are counters in Hadoop MapReduce?', 'Counters are named long values that tasks increment while a job runs and the framework aggregates into job totals. Hadoop provides built-in counters (records read and written, bytes, spills, launched and failed tasks) and lets programs define their own, typically to count categories or data-quality problems.'),
    ('What is the difference between enum counters and dynamic counters?', 'Enum counters are Java enum constants passed to context.getCounter(Enum); the enum class becomes the group and names are checked at compile time. Dynamic counters are created with context.getCounter(String group, String name), so names can be decided at run time, for example one counter per hour. Dynamic names must still stay few, because of the counter limit.'),
    ('How do you read counters in the driver?', 'After job.waitForCompletion() returns, call job.getCounters() to get a Counters object. Use findCounter(TaskCounter.MAP_INPUT_RECORDS) or findCounter(MyEnum.X) for a single value, or getGroup("name") to loop over a group. The driver can then print the values or decide its exit code.'),
    ('What is the limit on the number of counters?', 'mapreduce.job.counters.max limits a job to 120 counters by default, and mapreduce.job.counters.groups.max to 50 groups. Exceeding it throws LimitExceededException in the task (“Too many counters: 121 max=120” in our lab) and the job fails. The limit exists because counters are kept in memory by tasks, the ApplicationMaster and the JobHistory Server.'),
    ('Are counters from failed task attempts included?', 'No. The job\'s final counters are aggregated from the successful attempt of each task, so retries and speculative copies do not inflate the totals. While a job is still running, the displayed values are progress snapshots and can change.'),
]

PRACTICE_INTRO = 'Counter exercises using the real numbers from the lab.'
PROBLEMS = [
    dict(level='easy', title='Do the categories add up?', stmt='Check that the four category counters add up to Map input records (5,00,000).', inp='90,110 · 190,033 · 80,219 · 139,638',
         code='''print(90110 + 190033 + 80219 + 139638 == 500000)
''', explain='True: every order fell in exactly one category, and UNKNOWN was 0.'),
    dict(level='easy', title='Average order value per category', stmt='Divide each revenue counter by its order counter.', inp='revenue and order counters',
         code='''orders = {"BREAKFAST": 90110, "DRINK": 190033, "MEAL": 80219, "SNACK": 139638}
revenue = {"BREAKFAST": 2476620, "DRINK": 3052315, "MEAL": 4670075, "SNACK": 2652992}
for c in orders:
    print(f"{c:9} Rs {revenue[c] / orders[c]:.2f}")
''', explain='Meals average about ₹58 per order, drinks about ₹16: drinks lead in orders, meals in money.'),
    dict(level='easy', title='Peak hour share', stmt='What share of all orders came in the 14:00 hour?', inp='62,213 of 5,00,000',
         code='''print(f"{62213 / 500000:.1%}")
''', explain='12.4%: one hour in thirteen takes an eighth of the day\'s orders.'),
    dict(level='medium', title='Busiest and quietest hour', stmt='From the “Orders by hour” group, find the busiest and quietest hours and their ratio.', inp='13 hourly counters',
         code='''hours = {"08": 55852, "09": 43655, "10": 24986, "11": 25002, "12": 31091, "13": 56026, "14": 62213,
         "15": 37945, "16": 25218, "17": 37777, "18": 50133, "19": 31378, "20": 18724}
busy = max(hours, key=hours.get)
quiet = min(hours, key=hours.get)
print(busy, hours[busy], quiet, hours[quiet], f"ratio {hours[busy] / hours[quiet]:.1f}x")
''', explain='14:00 vs 20:00, about 3.3 times busier: the canteen needs most staff around lunch, least at closing time.'),
    dict(level='medium', title='Counter budget', stmt='A job has 54 built-in counters. You add 5 enum quality counters and an hour group (24 names). How many counters are left before the limit?', inp='54 + 5 + 24, limit 120',
         code='''print(120 - (54 + 5 + 24), "left")
''', explain='37 left. Enough for small groups, nowhere near enough for one per customer.'),
    dict(level='medium', title='Merge with a retry', stmt='Merge these attempt counters into job counters, ignoring failed and killed attempts.', inp='4 attempts',
         code='''attempts = [("SUCCEEDED", {"BAD": 3}), ("FAILED", {"BAD": 2}), ("SUCCEEDED", {"BAD": 5}), ("KILLED", {"BAD": 1})]
total = {}
for state, cs in attempts:
    if state == "SUCCEEDED":
        for k, v in cs.items():
            total[k] = total.get(k, 0) + v
print(total)
''', explain='BAD = 8. Adding all attempts would wrongly give 11.'),
    dict(level='business', title='Is today\'s load normal?', stmt='Yesterday the job read 5,00,000 orders; today 2,10,000. Alert if today is below 70% of yesterday. What should happen?', inp='500,000 vs 210,000',
         code='''y, t = 500000, 210000
print(f"today is {t / y:.0%} of yesterday ->", "ALERT: check the upstream feed" if t < 0.7 * y else "normal")
''', explain='42%: almost certainly a missing input file, not a quiet day. Counters caught it before the report went out.'),
    dict(level='advanced', title='Counters vs output for skewed students', stmt='Instead of per-student counters, find the 3 students with the most orders from (student, orders) pairs, the way a reducer\'s output would be used.', inp='a few (student, orders) rows',
         code='''rows = [("S0001", 3899), ("S0007", 3934), ("S1413", 184), ("S0002", 4015), ("S0003", 4031)]   # real counts from Lessons 9.1 and 9.7
top = sorted(rows, key=lambda r: -r[1])[:3]
for s, n in top:
    print(s, n)
''', explain='Per-key numbers come from the job\'s output (a reducer keyed by student), then any sort or top-N runs on that output. No counter limit involved.'),
]

SCN_INTRO = 'Counters come up in interviews as “how do you track bad records?” and in debugging questions about strange numbers.'
SCENARIOS = '''    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Concepts · basics</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“How would you count malformed records in a MapReduce job?”</h4>
      <p class="scn__situation">A standard question after you explain mappers.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> custom counters and what to do with them.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Define an enum (e.g. GOOD, BAD_FORMAT, BAD_AMOUNT) and call context.getCounter(Quality.BAD_FORMAT).increment(1) when skipping a row.</li>
          <li>After the job, read job.getCounters() in the driver and fail the pipeline if bad rows exceed a threshold.</li>
          <li>Optionally write the bad rows themselves to a side output (MultipleOutputs) for inspection.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Debugging · limits</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>A job fails with “Too many counters: 121 max=120”</h4>
      <p class="scn__situation">It started after a developer added counters “for every product”.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> knowing the right fix, not just the property.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Unbounded dynamic counter names (one per product) hit mapreduce.job.counters.max.</li>
          <li>Raising the limit is the wrong fix: counters live in memory in every task, the AM and the history server.</li>
          <li>Move per-product numbers into the job output (a reducer keyed by product) and keep counters for a small, fixed set of facts.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Internals · retries</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>“Our task was retried twice. Are the counters triple-counted?”</h4>
      <p class="scn__situation">An analyst doubts the record counts in the job report.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> attempt-level aggregation.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>No: final job counters sum only the successful attempt of each task; failed and killed attempts are excluded.</li>
          <li>Values seen while the job runs are snapshots and may include in-progress attempts.</li>
          <li>Side effects are a different story: writes to external systems from a failed attempt are NOT undone, which is why tasks should be idempotent.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Operations · monitoring</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>The nightly report was published with half the data</h4>
      <p class="scn__situation">An upstream feed delivered only some files, and the job “succeeded”.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> using counters as guardrails.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Compare Map input records (or HDFS bytes read) with the previous run or an expected range, and exit non-zero on a large drop.</li>
          <li>Collect counters from the JobHistory REST API into monitoring and alert on anomalies.</li>
          <li>Also validate inputs before the job (expected file count, _SUCCESS markers from upstream).</li>
        </ul>
      </div></details>
    </article>
'''
