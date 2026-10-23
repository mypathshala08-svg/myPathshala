import os
HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)
BODY = body(HERE)
rd = lambda f: open(os.path.join(UP, f)).read()

META = dict(
    module='09-mapreduce-in-depth', lesson='07-secondary-sort', n='9.7',
    module_label='Module 9 · MapReduce in depth',
    title='Secondary sort',
    desc='Secondary sort in Hadoop MapReduce, run on a real Hadoop 3.5.0 cluster: composite key (student, time), a partitioner and a grouping comparator on the natural key, and values that arrive in time order. 5 lakh orders, 2,000 students: first order, last order and longest gap per student in one pass (2,000 groups); without the grouping comparator, 490,794 groups and wrong answers. Value-to-key conversion, sort comparator for descending order, key object reuse, sessionization and top-N per group. Python simulation, quiz and interview scenarios.',
    og_desc='Get each student\'s orders in time order without sorting in memory: composite key, partitioner and grouping comparator, tested on 5 lakh orders.',
    minutes=28, level='Advanced',
    lead='Inside a reduce group, values arrive in no particular order. Secondary sort makes the shuffle sort them for you: put the sort field into the key, then partition and group by the natural key only. This lesson builds it for 2,000 students\' orders on a real cluster and shows what goes wrong when one piece is missing.',
    chips=['2,000 groups vs 490,794, measured', 'Composite key + grouping comparator', 'Runs in your browser (Python)'],
)

RUN = dict(
    heading='Simulate composite key, partition and grouping',
    intro='<p>This model does what the framework does: sort map output by the full key (student, time), send each key to a reducer by the student only, then cut groups where the student changes. Switch <code>GROUP_BY_STUDENT</code> to <code>False</code> to see a job without a grouping comparator.</p>',
    code='''orders = [("S1413", "09-14 15:30", "dosa"), ("S0001", "09-01 08:15", "poha"),
          ("S1413", "09-01 14:18", "vada pav"), ("S0001", "09-01 08:09", "poha"),
          ("S1413", "09-30 16:30", "samosa"), ("S0001", "09-01 08:15", "thali")]
REDUCERS = 3
GROUP_BY_STUDENT = True

def partition(student):                       # natural key only
    return sum(map(ord, student)) % REDUCERS

for r in range(REDUCERS):
    mine = [o for o in orders if partition(o[0]) == r]
    mine.sort(key=lambda o: (o[0], o[1]))     # sort comparator: student, then time
    groups = []
    for student, time, item in mine:
        same = groups and (groups[-1][0] == student if GROUP_BY_STUDENT
                           else groups[-1][0] == (student, time))
        if not same:
            groups.append([student if GROUP_BY_STUDENT else (student, time), []])
        groups[-1][1].append(f"{time} {item}")
    for key, vals in groups:
        print(f"reducer {r}: reduce({key}) -> first {vals[0]!r}, last {vals[-1]!r}, {len(vals)} values")
''',
    anno=[
        ('    return sum(map(ord, student)) % REDUCERS', 'Only the student decides the reducer, never the time. (Hadoop uses the hash code; any function of the student works.)'),
        ('    mine.sort(key=lambda o: (o[0], o[1]))     # sort comparator: student, then time', 'The shuffle sorts by the full composite key: this is the key\'s compareTo.'),
        ("        same = groups and (groups[-1][0] == student if GROUP_BY_STUDENT", 'The grouping comparator: a new reduce() call starts only when the student changes.'),
    ],
    tasks=[
        dict(label='1 · Group by student', hint='Press <b>Run</b>. Each student gets one call with values oldest first.', code=None),
        dict(label='2 · No grouping comparator', hint='<b>Predict first:</b> set <code>GROUP_BY_STUDENT = False</code>. How many reduce calls for S0001? Why do poha and thali at 08:15 share one?',
             code=None),
        dict(label='3 · Latest first', hint='Sort the time in descending order (like a custom sort comparator) while still grouping by student. The first value is now the last order.',
             code='''orders = [("S1413", "09-14 15:30"), ("S1413", "09-01 14:18"), ("S1413", "09-30 16:30"), ("S0001", "09-01 08:09")]
orders.sort(key=lambda o: o[1], reverse=True)    # time descending ...
orders.sort(key=lambda o: o[0])                  # ... then student ascending (stable sort keeps time order)
current = None
for student, time in orders:
    if student != current:
        print(student, "latest order:", time)
        current = student
'''),
        dict(label='4 · Longest gap', hint='Walk one student\'s sorted times once and find the longest gap in hours, the way the reducer does.',
             code='''from datetime import datetime
times = ["2026-09-16 09:10", "2026-09-16 11:50", "2026-09-17 09:52", "2026-09-17 13:20"]
prev, best = None, (0, None, None)
for t in times:
    now = datetime.strptime(t, "%Y-%m-%d %H:%M")
    if prev and (now - prev).seconds // 60 + (now - prev).days * 1440 > best[0]:
        best = ((now - prev).seconds // 60 + (now - prev).days * 1440, prev, now)
    prev = now
print(f"longest gap {best[0] // 60} h: {best[1]:%m-%d %H:%M} -> {best[2]:%m-%d %H:%M}")
'''),
        dict(label='5 · Spot the error', hint='This “first order” code assumes the values are sorted, but they arrive unsorted. It then crashes on a bad date format. Sort first, and fix the format.',
             code='''from datetime import datetime
vals = ["2026-09-14 15:30", "2026-09-01 14:18", "2026-09-30 16:30"]
first = datetime.strptime(vals[0], "%d-%m-%Y %H:%M")
print("first order:", first)
''', expect='error'),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']
RUN['tasks'][1]['code'] = RUN['code'].replace('GROUP_BY_STUDENT = True', 'GROUP_BY_STUDENT = False')

PCRUN = dict(
    heading='Run it on your PC: first and last order per student',
    intro='<p>Use the Module 8 lab cluster and <code>student_orders.csv</code> from <code>make_student_orders.py</code> (Lesson 9.1). Copy <code>FirstLastOrder.java</code> and the script into the namenode container under <code>/tmp/mr9</code>, compile all Module 9 classes into <code>mr9.jar</code>, then run the script. It runs the job twice (with and without the grouping comparator) and checks one student with plain Linux tools.</p>',
    items=[
        dict(title='Secondary sort job', file='FirstLastOrder.java',
             cmd=rd('java/FirstLastOrder.java') + '\n// In the mr-lab folder:\n//   docker exec lab8-namenode-1 mkdir -p /tmp/mr9\n//   docker cp FirstLastOrder.java lab8-namenode-1:/tmp/mr9/\n//   docker exec -it lab8-namenode-1 bash\n// Inside the container:\n//   cd /tmp/mr9\n//   mkdir -p classes && javac -cp $(hadoop classpath) -d classes *.java && jar cf mr9.jar -C classes .\n//   hadoop jar mr9.jar FirstLastOrder /user/hadoop/data/student_orders.csv /out/ss_true',
             output=rd('tx97.txt').strip(),
             note='Real output of secondary_sort_lab.sh (below). Timings vary. With grouping: 2,000 groups for 2,000 students. Without: 490,794 groups, one per distinct (student, minute); “longest gap 0 h” there is -1 minutes divided by 60 in Java integer arithmetic, because a one-order group has no gap at all.'),
        dict(title='The experiment script', file='secondary_sort_lab.sh',
             cmd=rd('secondary_sort_lab.sh') + '\n# Inside the namenode container, in /tmp/mr9 (student_orders.csv copied there too):\n#   bash secondary_sort_lab.sh',
             output=rd('tx97.txt').strip().split('== a light user')[0].strip(),
             note='The first half of the same run. Compare Reduce input groups: it must equal the number of natural keys.'),
    ],
)

TRACE = dict(
    heading='Grouping sorted composite keys',
    intro='<p>The keys below are already sorted by (student, time). Watch how the grouping rule decides where one reduce() call ends.</p>',
    code='''keys = [("S0001", "08:09"), ("S0001", "08:15"), ("S1413", "14:18"), ("S1413", "16:30")]
calls = []
for student, time in keys:
    if not calls or calls[-1][0] != student:
        calls.append([student, []])
    calls[-1][1].append(time)
print(calls)
''',
    notes={4: 'Grouping :: Compare only the natural key (student); the time is ignored here.',
           6: 'Values :: Times are appended in sorted order, so the first is the earliest.'},
)

WORKED_INTRO = 'Three secondary-sort design problems: building the key, sizing the memory you save, and a session count.'
EXAMPLES = [
    dict(level='b', tag='Design · key', title='Design the key for “latest score per student”',
         problem='<p>Exam attempts look like <code>student,subject,attempt_time,score</code>. For each (student, subject) you need the score of the latest attempt. What is the natural key, the secondary field, and which value do you read in the reducer?</p>',
         inp='4 attempts',
         approach=['Natural key = (student, subject): the group.',
                   'Secondary field = attempt_time, sorted descending.',
                   'The reducer reads only the first value of each group.'],
         code='''rows = [("S1", "maths", "09-02", 61), ("S1", "maths", "09-20", 78), ("S1", "java", "09-05", 55), ("S2", "maths", "09-11", 90)]
rows.sort(key=lambda r: r[2], reverse=True)     # secondary: time descending
rows.sort(key=lambda r: (r[0], r[1]))           # natural key ascending (stable)
seen = set()
for s, sub, t, score in rows:
    if (s, sub) not in seen:
        seen.add((s, sub))
        print(s, sub, "latest", t, "score", score)
''', notes={5: 'First value :: Each group is read only up to its first value.'},
         tryit='Change it to the best score instead of the latest: the secondary field becomes score descending.'),
    dict(level='i', tag='Sizing · memory', title='How much memory does sorting in the reducer need?',
         problem='<p>A clickstream job groups by user. The heaviest user has 3 crore events in a month, each about 120 bytes as a Java object. The reducer heap is 3 GB. Can it sort that user\'s events in memory? How much does secondary sort need?</p>',
         inp='3 crore events × 120 B · 3 GB heap',
         approach=['Memory = events × bytes per event.',
                   'Compare with the heap.',
                   'Secondary sort keeps only the current and previous value.'],
         code='''events, size, heap = 30_000_000, 120, 3 * 1024**3
need = events * size
print(f"in-memory sort needs {need / 1024**3:.1f} GB of {heap / 1024**3:.0f} GB heap -> {'OK' if need < heap else 'OutOfMemoryError'}")
print(f"secondary sort needs about {2 * size} bytes per group at any moment")
''', notes={3: 'Need :: Lists of Java objects take even more than this in practice.'},
         tryit='Our heaviest student had only 3,899 orders: an in-memory sort would work today. Secondary sort is about the day a user has crores of rows.'),
    dict(level='a', tag='Pattern · sessions', title='Count sessions with a 30-minute gap',
         problem='<p>One user\'s click times arrive sorted (thanks to secondary sort). A new session starts when the gap since the previous click is more than 30 minutes. How many sessions, and how long is each?</p>',
         inp='8 click times (minutes since midnight)',
         approach=['Walk the sorted times once.',
                   'Start a new session when gap > 30.',
                   'Record the start and end of each session.'],
         code='''clicks = [540, 545, 560, 610, 615, 700, 701, 760]
sessions = [[clicks[0], clicks[0]]]
for t in clicks[1:]:
    if t - sessions[-1][1] > 30:
        sessions.append([t, t])
    else:
        sessions[-1][1] = t
print(len(sessions), "sessions:", [f"{s // 60:02d}:{s % 60:02d}+{e - s}m" for s, e in sessions])
''', notes={4: 'Gap :: Compares with the previous click, which is only meaningful because the times are sorted.'},
         tryit='Change the gap to 60 minutes. Sessionization is the classic secondary-sort job in web analytics.'),
]

QUIZ = mix([
    dict(q='Why do you need secondary sort at all?', options=['Keys are not sorted', 'Values inside a reduce group arrive in no guaranteed order', 'Reducers cannot read values', 'The partitioner sorts values randomly'], answer=1,
         why='Keys are sorted by the shuffle; values within a key are not.'),
    dict(q='What does the composite key contain in our job?', options=['Only the student', 'The student (natural key) and the order time (secondary field)', 'The order id and amount', 'The reducer number'], answer=1,
         why='StudentTime(student, time): value-to-key conversion.'),
    dict(q='Which field must the partitioner use?', options=['The full composite key', 'Only the natural key (student)', 'Only the time', 'The value'], answer=1,
         why='Otherwise one student\'s orders spread over several reducers.'),
    dict(q='What does the grouping comparator decide?', options=['The order of keys', 'Which consecutive keys go into the same reduce() call', 'Which reducer gets a key', 'The output format'], answer=1,
         why='Comparing only the student makes all of a student\'s keys one group.'),
    dict(q='How many reduce groups did our job get WITHOUT the grouping comparator?', options=['2,000', '490,794', '500,000', '1'], answer=1,
         why='One per distinct (student, minute); orders in the same minute shared a group.'),
    dict(q='How do you get the latest order first?', options=['Reverse the output file', 'Set a sort comparator that orders time descending, keeping grouping on student', 'Use more reducers', 'Use a combiner'], answer=1,
         why='job.setSortComparatorClass(...) controls the shuffle order.'),
    dict(q='What happens to the key object while you iterate the values?', options=['It stays the first key', 'The framework reuses it and its time field changes to each record\'s time', 'It becomes null', 'It is copied for every value'], answer=1,
         why='Read the value (or copy the key) if you need the time later.'),
    dict(q='Which counter shows that grouping works in our job?', options=['Map output records', 'Reduce input groups = 2,000, the number of students', 'Spilled Records', 'Launched map tasks'], answer=1,
         why='It must equal the number of natural keys.'),
])

REVISION = [
    'Values in a reduce group are <b>unordered</b>; sorting them in reducer memory does not scale.',
    '<b>Composite key</b> = natural key + secondary field (value-to-key conversion); <code>compareTo</code> sorts by both.',
    '<b>Partitioner</b> on the natural key only; <b>grouping comparator</b> (<code>setGroupingComparatorClass</code>) on the natural key only.',
    'Optional <b>sort comparator</b> (<code>setSortComparatorClass</code>) for descending or custom order.',
    'Lab: 5 lakh orders → 2,000 groups and lines; S1413 first 09-01 14:18, last 09-30 16:30, gap 22 h. Without grouping: 490,794 groups.',
    'The key object is reused: its secondary field changes as you iterate values.',
    'Uses: first/last event, sessionization, top-N per group, joins with the small side first.',
]
FAQ = [
    ('What is secondary sort in Hadoop MapReduce?', 'A pattern that makes the values of each reduce group arrive in a chosen order. The mapper emits a composite key (natural key plus the field to sort by), the sort comparator orders by both, a custom partitioner uses only the natural key and a grouping comparator compares only the natural key, so each reduce() call receives one natural key with its values already sorted by the secondary field.'),
    ('What is the difference between the sort comparator and the grouping comparator?', 'The sort comparator decides the order of all keys in the shuffle (by default the key\'s compareTo). The grouping comparator decides which consecutive sorted keys are passed to the same reduce() call. In secondary sort the sort comparator uses the whole composite key and the grouping comparator uses only the natural key.'),
    ('Why do we need a custom partitioner for secondary sort?', 'The default HashPartitioner hashes the whole key. With a composite key, records of the same natural key but different secondary values could go to different reducers, so no reducer would see the complete group. A partitioner on the natural key keeps them together.'),
    ('Can I just sort the values in the reducer instead?', 'Only if every group is small enough to fit in the reducer\'s heap. You must copy each value out of the reused object into a list, which costs memory proportional to the largest group. Secondary sort uses the framework\'s disk-backed sort and keeps memory constant.'),
    ('How is secondary sort done in Spark or Hive?', 'Spark uses repartitionAndSortWithinPartitions with a partitioner on the natural key and an ordering on the composite key. Hive uses DISTRIBUTE BY natural_key SORT BY natural_key, field. SQL window functions with PARTITION BY ... ORDER BY express the same idea.'),
]

PRACTICE_INTRO = 'Secondary sort exercises, using the real numbers from the lab.'
PROBLEMS = [
    dict(level='easy', title='Groups vs students', stmt='With the grouping comparator, Reduce input groups was 2,000. Without it, 490,794. How many orders shared a (student, minute) key with another order?', inp='500,000 records · 490,794 groups',
         code='''print(500000 - 490794, "orders fell into an already existing (student, minute) group")
''', explain='9,206 orders landed in a minute in which the same student had already ordered, like S0001\'s poha and thali at 08:15.'),
    dict(level='easy', title='Average orders per student', stmt='How many orders does a student have on average, and how far is S0001 above that?', inp='500,000 orders · 2,000 students · S0001 3,899',
         code='''avg = 500000 / 2000
print(avg, "average;", round(3899 / avg, 1), "x for S0001")
''', explain='250 on average; S0001 orders 15.6 times as much (one of the 20 heavy users in the generated data).'),
    dict(level='easy', title='Sort the composite key', stmt='Sort these keys the way the shuffle does: student, then time.', inp='4 keys',
         code='''keys = [("S1413", "09-30 16:30"), ("S0001", "09-01 08:15"), ("S1413", "09-01 14:18"), ("S0001", "09-01 08:09")]
for k in sorted(keys):
    print(k)
''', explain='Python sorts tuples field by field, exactly like the compareTo in StudentTime.'),
    dict(level='medium', title='Why the time format matters', stmt='Sort the same three times written as "d/m/yyyy H:MM" and as "yyyy-mm-dd HH:MM". Which gives the right order?', inp='3 times',
         code='''bad = ["1/9/2026 14:18", "30/8/2026 16:30", "14/9/2026 15:30"]
good = ["2026-09-01 14:18", "2026-08-30 16:30", "2026-09-14 15:30"]
print(sorted(bad))
print(sorted(good))
''', explain='The first list puts 30 August last because text compares character by character. Text order matches time order only when the biggest unit comes first with fixed widths, as in our data.'),
    dict(level='medium', title='Partition by natural key', stmt='With 3 reducers, assign each key to a reducer using only the student. Check that both S1413 keys land together.', inp='4 composite keys',
         code='''keys = [("S1413", "09-30"), ("S0001", "08:15"), ("S1413", "09-01"), ("S0001", "08:09")]
for s, t in keys:
    print(s, t, "-> reducer", sum(map(ord, s)) % 3)
''', explain='Both S1413 keys go to one reducer, both S0001 keys to another; the time plays no part.'),
    dict(level='medium', title='First and last per group', stmt='Given sorted (student, time) records, print each student\'s first and last time in one pass.', inp='5 sorted records',
         code='''recs = [("S0001", "08:09"), ("S0001", "08:15"), ("S0001", "20:47"), ("S1413", "14:18"), ("S1413", "16:30")]
cur, first, last = None, None, None
for s, t in recs + [(None, None)]:
    if s != cur:
        if cur:
            print(cur, first, last)
        cur, first = s, t
    last = t
''', explain='A sentinel at the end flushes the last group, the same trick reducers in streaming (Lesson 9.8) use.'),
    dict(level='business', title='Memory or redesign?', stmt='The reducer that sorts in memory needs 12 GB for its biggest user. Option A: raise reducer memory to 16 GB on 200 nodes (₹2,000 per node extra RAM per year). Option B: 2 developer-days (₹8,000 per day) to switch to secondary sort. Compare.', inp='₹2,000 × 200 vs 2 × ₹8,000',
         code='''a, b = 2000 * 200, 2 * 8000
print(f"A: Rs {a:,} per year, B: Rs {b:,} once")
''', explain='₹4 lakh a year vs ₹16,000 once (illustrative), and A breaks again when the biggest user grows.'),
    dict(level='advanced', title='Top-2 per counter', stmt='For each canteen counter, list its top 2 items by revenue, using sort by (counter, revenue descending) and taking the first 2 values per group.', inp='8 items with counter and revenue',
         code='''rows = [("A", "chai", 2245035), ("A", "coffee", 807280), ("B", "samosa", 1257912), ("B", "vada pav", 1395080),
        ("C", "poha", 1133400), ("C", "idli", 1343220), ("D", "dosa", 2246715), ("D", "thali", 2423360)]
rows.sort(key=lambda r: (r[0], -r[2]))
taken = {}
for counter, item, rev in rows:
    if taken.get(counter, 0) < 2:
        print(counter, item, rev)
        taken[counter] = taken.get(counter, 0) + 1
''', explain='Sorting by negative revenue gives descending order inside each counter group; the reducer just counts to N.'),
]

SCN_INTRO = 'Secondary sort is a favourite question for experienced Hadoop and Spark engineers.'
SCENARIOS = '''    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Concepts · basics</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“Are reducer values sorted in MapReduce?”</h4>
      <p class="scn__situation">A quick check question.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> keys vs values.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Keys are sorted by the shuffle; values for one key are not in any guaranteed order.</li>
          <li>To get ordered values, use secondary sort: composite key, partitioner and grouping comparator on the natural key.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Design · pattern</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>Each customer's transactions must be processed in time order</h4>
      <p class="scn__situation">Some customers have crores of transactions; the reducer heap is 4 GB.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> all three pieces and why.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Map emits key (customer, timestamp), value = transaction.</li>
          <li>Partitioner and grouping comparator on customer only; sort comparator on (customer, timestamp).</li>
          <li>The reducer streams each customer's transactions in order with constant memory; verify with Reduce input groups = number of customers.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Debugging · output</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>A sessionization job's output has 50 times more rows than users</h4>
      <p class="scn__situation">It ran successfully; the numbers look wrong.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> recognising a missing grouping comparator.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Check Reduce input groups: if it is near the number of (user, timestamp) pairs, the grouping comparator is missing or wrong.</li>
          <li>Set job.setGroupingComparatorClass with a comparator on the user only.</li>
          <li>Also check the partitioner: wrong results appear with 2+ reducers if it hashes the whole key.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Internals · reuse</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>“Inside the loop over values, can I read the time from the key?”</h4>
      <p class="scn__situation">A follow-up after you explain secondary sort.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> object reuse.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Yes: the framework deserializes each record's key into the same key object, so key.time changes on each step.</li>
          <li>But don't keep references to the key or values; copy the fields you need.</li>
          <li>Putting the field in the value too (as our job does) makes the code clearer.</li>
        </ul>
      </div></details>
    </article>
'''
