import os, re
HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)
BODY = body(HERE)
rd = lambda f: open(os.path.join(UP, f), encoding='utf-8').read()


def mr_out(name):
    """Job log without progress lines, Java stack lines and INFO noise; keep the facts."""
    keep = []
    for ln in rd('lab/txout/' + name).split('\n'):
        if re.search(r'map \d+% reduce', ln) or ln.strip().startswith('at ') or 'WARN' in ln:
            continue
        if ' INFO ' in ln and not re.search(r'Total input files|number of splits|Running job|completed successfully|Task Id|Output directory', ln):
            continue
        if re.search(r'(FILE|HDFS): Number of (read|large|write)|erasure|vcore|megabyte|occupied slots|snapshot=|committed heap|Peak|BAD_ID|CONNECTION|WRONG_|IO_ERROR|Input split bytes|Combine (in|out)put|Merged Map|GC time|CPU time|Spilled|Failed Shuffles|Shuffle Errors', ln):
            continue
        if ln.startswith('packageJobJar') or ln.startswith('Deleted') or ln.strip() == '':
            continue
        keep.append(re.sub(r'^\d{4}-\d\d-\d\d (\d\d:\d\d:\d\d) INFO  (\w+):\d+ - ', r'\1 \2 - ', ln))
    return '\n'.join(keep).strip()


def spark_out(name):
    keep = []
    for ln in rd('lab/txout/' + name).split('\n'):
        if re.match(r'^(WARN|\d\d/\d\d/\d\d |\s)', ln) or ln.startswith('Using Spark') or ln.startswith('Exception in thread'):
            continue
        keep.append(ln)
    return '\n'.join(keep).strip()


META = dict(
    module='14-capstone', lesson='02-build-the-pipeline', n='14.2',
    module_label='Module 14 · Capstone project',
    title='Build the pipeline',
    desc='Capstone part 2, run for real on Hadoop 3.5.0 + Spark 4.0.4: a Python MapReduce Streaming job cleans and deduplicates 3.57 lakh raw lines (104 maps, 3 reducers, 8 custom counters, 4 min 39 s), Spark writes silver Parquet by day (29.7 MB text → 7.2 MB) and five gold tables, UPI reconciliation finds a ₹6,854 gateway gap in one hour at one canteen, and check.py passes 10/10 acceptance tests against truth.json. Idempotent backfill vs append (13,007 → 26,014 orders), findings for the owner, Python simulation, quiz and interview scenarios.',
    og_desc='Raw files to trusted answers: MapReduce cleaning, Spark silver and gold, UPI reconciliation and 10/10 acceptance checks on a real cluster.',
    minutes=34, level='Intermediate',
    lead='Today we build the pipeline designed in Lesson 14.1 and run every stage on our cluster: a MapReduce Streaming job that cleans and deduplicates the raw orders, a Spark job that writes silver Parquet and the gold tables the owner asked for, a UPI reconciliation, and the acceptance checks that decide whether any number may be shown to her.',
    chips=['Full pipeline on our cluster', '10/10 acceptance checks', 'Runs in your browser (Python)'],
)

RUN = dict(
    heading='The whole pipeline in 40 lines',
    intro='<p>A miniature of our pipeline: the mapper, the shuffle (<code>sorted</code>), the reducer and one gold table, on eight raw lines from two files. The rules are the real ones.</p>',
    code='''files = {"09-12": ["K-0912-1,2026-09-12 08:10:00,KHR,S1,chai,1,15,UPI",
                   "K-0912-2,2026-09-12 13:05:00,KHR,S2,thali,1,80,UPI",
                   "K-0912-2,2026-09-12 13:05:00,KHR,S2,thali,1,80,UPI",
                   "K-0912-3,2026-09-12 13:40:00,KHR,S3,dosa"],
         "09-14": ["K-0912-4,2026-09-12 17:55:00,KHR,S4,vada pav,2,40,UPI",
                   "K-0914-1,2026-09-14 08:02:00,KHR,S5,maggi,1,30,CASH",
                   "K-0914-2,2026-09-14 09:15:00,KHR,TEST,idli,1,30,CASH",
                   "K-0912-2,2026-09-12 13:05:00,KHR,S2,thali,1,80,UPI"]}
menu = {"chai": "drink", "thali": "meal", "dosa": "meal", "vada pav": "snack", "idli": "breakfast"}
count = {}

def mapper(file_day, line):
    f = line.split(",")
    if len(f) != 8:
        count["MALFORMED"] = count.get("MALFORMED", 0) + 1
        return []
    if f[3] == "TEST":
        count["TEST_ORDER"] = count.get("TEST_ORDER", 0) + 1
        return []
    return [(f[0], file_day, line)]

pairs = [p for day, lines in files.items() for line in lines for p in mapper(day, line)]
pairs.sort()                                   # the shuffle and sort
clean, i = [], 0
while i < len(pairs):                          # the reducer: one group per order_id
    j = i
    while j < len(pairs) and pairs[j][0] == pairs[i][0]:
        j += 1
    file_day, line = min((d, l) for _, d, l in pairs[i:j])
    count["DUPLICATE"] = count.get("DUPLICATE", 0) + (j - i - 1)
    f = line.split(",")
    late = file_day > f[1][5:10]
    clean.append((f[1][:10], f[4], menu.get(f[4], "unknown"), int(f[6]), late))
    i = j

gold = {}
for dt, item, cat, amount, late in clean:
    gold[dt] = gold.get(dt, 0) + amount
print("counters:", count)
print("clean   :", clean)
print("gold    :", gold)
''',
    anno=[
        ('    return [(f[0], file_day, line)]', 'Key = order_id, plus the file day: exactly what clean_mapper.py prints, as a tuple.'),
        ('pairs.sort()                                   # the shuffle and sort', 'Sorting puts every copy of an order next to the others, like Hadoop\'s shuffle.'),
        ('    file_day, line = min((d, l) for _, d, l in pairs[i:j])', 'Earliest file wins; the other copies are counted as DUPLICATE.'),
        ('    late = file_day > f[1][5:10]', 'Sold on the 12th, first seen in the 14th\'s file: late, but counted on the 12th.'),
    ],
    tasks=[
        dict(label='1 · Mini pipeline', hint='Press <b>Run</b>. Which day does the vada pav order count on? How many duplicates?', code=None),
        dict(label='2 · Forget the sort', hint='<b>Predict first:</b> without the shuffle\'s sort, copies of K-0912-2 are not next to each other. How many orders come out?',
             code='''pairs = [("K-2", "09-12"), ("K-1", "09-12"), ("K-2", "09-12"), ("K-3", "09-14"), ("K-2", "09-14")]
# pairs.sort()   <- the shuffle forgot to sort
out, prev = [], None
for key, day in pairs:
    if key != prev:
        out.append(key)
    prev = key
print(len(out), "orders:", out)
'''),
        dict(label='3 · Inner vs left join', hint='Reconcile UPI orders with gateway SUCCESS records. Compare what an inner join and a left join show.',
             code='''orders = {"N-1": 40, "N-2": 30, "N-3": 80}
success = {"N-1": 40, "N-3": 80}
inner = {k: v for k, v in orders.items() if k in success}
left = {k: success.get(k) for k in orders}
print("inner join rows:", inner)
print("left join rows :", left)
print("unconfirmed    :", [k for k, v in left.items() if v is None])
'''),
        dict(label='4 · Append vs overwrite', hint='A retry writes the same day twice. Our lab: 13,007 orders became 26,014 with append.',
             code='''table_append, table_dt = [], {}
day = ("2026-09-14", 13007)
for run in (1, 2):
    table_append.append(day)
    table_dt[day[0]] = day[1]
    print("run", run, "append:", sum(n for _, n in table_append), "| overwrite:", sum(table_dt.values()))
'''),
        dict(label='5 · Spot the error', hint='This reducer crashes on Kharghar\'s new dish. Fix it so unknown items get the category "unknown" (as clean_reducer.py does).',
             code='''menu = {"chai": "drink", "dosa": "meal"}
for item in ["chai", "maggi", "dosa"]:
    print(item, menu[item])
''', expect='error'),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run it on your PC: the full pipeline',
    intro='<p>Continue in the namenode container in <code>/tmp/capstone</code> after landing (Lesson 14.1). Spark 4.0.4 is unpacked as in Lesson 13.2 (<code>/tmp/opt/spark-4.0.4-bin-hadoop3</code>). Outputs are real; progress lines, Java stack traces and Spark INFO/WARN lines are removed.</p>',
    items=[
        dict(title='1 · Clean and deduplicate (MapReduce Streaming)', file='clean_job.sh',
             cmd=rd('lab/clean_job.sh') + '\n# time bash clean_job.sh      (clean_mapper.py and clean_reducer.py: see Lesson 14.1)',
             output=mr_out('tx_clean.txt'),
             note='104 splits for 104 small files. The custom "capstone" counter group is printed with the framework counters (some framework counters removed here).'),
        dict(title='2 · Silver and gold (Spark on YARN)', file='silver_gold.py · spark_job.sh',
             cmd=rd('lab/silver_gold.py') + '\n' + rd('lab/spark_job.sh'),
             output=spark_out('tx_spark.txt'),
             note='Run with day arguments (bash spark_job.sh 2026-09-14) to backfill only those days.'),
        dict(title='3 · Acceptance checks', file='check.py',
             cmd=rd('lab/check.py') + '\n' + rd('lab/check_job.sh'),
             output=rd('lab/txout/tx_check.txt').strip(),
             note='The pipeline is accepted only when every line says PASS.'),
        dict(title='4 · Backfill twice, and the append mistake', file='idem.sh · append_demo.py',
             cmd=rd('lab/idem.sh') + '\n' + rd('lab/append_demo.py'),
             output=spark_out('tx_idem.txt'),
             note='Each backfill rewrote only dt=2026-09-14 (still 3 files) and the month\'s totals did not move. With append, a retry doubles the day.'),
    ],
)

TRACE = dict(
    heading='Inside the reducer: one group at a time',
    intro='<p>The reducer sees sorted lines, one at a time. It must notice where one order_id ends, then keep the earliest copy. Watch <code>copies</code> fill and empty.</p>',
    code='''lines = [("K-1", "09-12"), ("K-2", "09-12"), ("K-2", "09-14"), ("K-3", "09-14")]
out, key, copies, dups = [], None, [], 0
for k, day in lines:
    if k != key and copies:
        out.append((key, min(copies)))
        dups += len(copies) - 1
        copies = []
    key = k
    copies.append(day)
out.append((key, min(copies)))
print(out, "duplicates:", dups)
''',
    notes={(4, 2): 'New key :: K-2 is different from K-1, so the K-1 group is complete: write it out.',
           10: 'Last group :: After the loop the last order is still open. Forgetting this line loses one order per reducer.'},
)

WORKED_INTRO = 'Three questions Mrs. Shinde asked after seeing the gold tables, answered from the lab numbers.'
EXAMPLES = [
    dict(level='b', tag='Reconciliation · UPI', title='Where did the UPI money go?',
         problem='<p>The tills say ₹80,76,462 was paid by UPI. The gateway confirmed ₹80,69,608 and refunded ₹31,811. How much should reach the bank, and how much is unexplained?</p>',
         inp='POS ₹8,076,462 · SUCCESS ₹8,069,608 · refunds ₹31,811',
         approach=['Net to bank = confirmed − refunds.', 'Unexplained = POS − confirmed (refunds are explained).', 'Compare with upi_gaps.'],
         code='''pos, success, refunds = 8076462, 8069608, 31811
def summary(pos, success, refunds):
    return success - refunds, pos - success
net, gap = summary(pos, success, refunds)
print(f"net to bank Rs {net:,}  unexplained Rs {gap:,}")
''', notes={4: 'Result :: ₹80,37,797 to the bank; ₹6,854 unexplained = exactly upi_gaps (Nerul, 22 Sept, 13:00).'},
         tryit='Mrs. Shinde raises a ticket with the gateway for 201 orders in one hour, instead of "UPI doesn\'t match".'),
    dict(level='i', tag='Gold · staffing', title='How many counter staff at 13:00?',
         problem='<p>Across 26 days and 4 canteens, 13:00–14:00 had 52,866 orders. One staff member can serve about 90 orders an hour. How many people does an average canteen need at that hour?</p>',
         inp='52,866 orders · 26 days · 4 canteens · 90 orders/person/hour',
         approach=['Orders per canteen in that hour on an average day.', 'Divide by 90 and round up.', 'Compare with 08:00 (49,660).'],
         code='''import math
def staff(orders, days=26, canteens=4, per_person=90):
    per_hour = orders / days / canteens
    return round(per_hour), math.ceil(per_hour / per_person)
for hour, n in [("13:00", 52866), ("08:00", 49660)]:
    print(hour, staff(n))
''', notes={3: 'Per hour :: About 508 orders in one hour at an average canteen.'},
         tryit='Kharghar is busier than average: use item_mix and daily_college to staff per canteen.'),
    dict(level='a', tag='Operations · backfill', title='How long to re-run the whole month?',
         problem='<p>The menu is corrected (maggi added at ₹30). The clean job must re-run on all 104 files (4 min 39 s) and Spark for all days (1 min 32 s), then checks. Later the canteens grow to 40: clean time grows with the number of files at the same per-map cost, Spark time roughly with data. Estimate both.</p>',
         inp='measured: clean 279 s for 104 maps · Spark 92 s',
         approach=['Today: add the measured times.', 'At 40 canteens: 10 × files and 10 × data, same cluster.', 'Notice which stage explodes.'],
         code='''clean_s, spark_s, scale = 279, 92, 10
def minutes(seconds):
    return round(seconds / 60, 1)
print("today      :", minutes(clean_s + spark_s), "min")
print("40 canteens:", minutes(clean_s * scale + spark_s * scale), "min")
''', notes={4: 'Today :: About 6 minutes for a full backfill.'},
         tryit='Over an hour at 40 canteens, mostly map-task start-up for tiny files. Lesson 14.3 cuts the clean job from 279 s to 53 s.'),
]

QUIZ = mix([
    dict(q='Why is order_id the map output key in the clean job?', options=['It is the first column', 'So every copy of an order reaches the same reducer and can be deduplicated', 'Hadoop requires string keys', 'To sort by time'], answer=1,
         why='Same key → same reducer; copies come one after another after the sort.'),
    dict(q='The job ran 104 map tasks because…', options=['We set mapreduce.job.maps=104', 'There were 104 small input files, each one split', 'The cluster has 104 cores', 'Streaming always uses 104 maps'], answer=1,
         why='"number of splits:104": one per file, as each file is smaller than a block.'),
    dict(q='Reduce input groups were 354,136 but clean orders 354,135. Why the extra group?', options=['A bug', 'All broken lines share the key ~BAD, which is one more group', 'The header', 'A duplicate'], answer=1,
         why='296 BAD lines arrive as one ~BAD group and pass through as BAD lines.'),
    dict(q='Which join finds UPI orders that the gateway never confirmed?', options=['Inner join', 'Left join from orders to SUCCESS records, keeping rows with no match', 'Cross join', 'No join, compare totals only'], answer=1,
         why='An inner join drops exactly the unmatched orders we are looking for.'),
    dict(q='What does setting Spark\'s partitionOverwriteMode to dynamic change?', options=['Spark writes faster', 'mode("overwrite") replaces only the partitions being written', 'Partitions are created automatically', 'It enables appends'], answer=1,
         why='Backfilling dt=2026-09-14 left the other 25 days untouched.'),
    dict(q='Silver orders were 7.2 MB in Parquet vs 29.7 MB of cleaned text because…', options=['Rows were dropped', 'Parquet is columnar and compressed, with real types', 'Spark samples data', 'HDFS replication'], answer=1,
         why='Same 354,135 rows; columnar encoding and compression (Lesson 10.2).'),
    dict(q='The append demo wrote 13,007 orders twice and read 26,014. What prevents this in the pipeline?', options=['More memory', 'Overwriting the day\'s partition instead of appending', 'A combiner', 'Speculative execution'], answer=1,
         why='Idempotent writes: a retry or backfill produces the same result.'),
    dict(q='When are the gold tables shown to the owner?', options=['As soon as Spark finishes', 'Only after check.py passes all acceptance tests', 'After one week', 'When the MapReduce job ends'], answer=1,
         why='Checks gate publication; a FAIL stops the run.'),
])

REVISION = [
    'Stages: bronze (104 CSV, 20.9 MB) → clean (MapReduce Streaming) → stage/clean (29.7 MB TSV) → silver (Parquet by dt, 7.2 MB) → gold (5 tables) → check.py.',
    'Clean job: key = order_id; reducer keeps earliest file copy; counters per rule; 104 maps, 3 reduces, 4 min 39 s.',
    'Conservation: 357,332 lines − 104 headers − 13 test = 357,215 mapped; 354,135 OK + 296 BAD = 354,431 out.',
    'Spark: explicit schema for mixed TSV; partitionBy("dt"); dynamic overwrite; coalesce(1) for small gold tables; 1 min 32 s.',
    'UPI: POS ₹80,76,462 vs SUCCESS ₹80,69,608 → gap ₹6,854 = 201 orders, Nerul, 22 Sept 13:00; refunds ₹31,811.',
    'Findings: Panvel undercharged ₹43,710; maggi ₹60,300 uncategorised; peak hour 13:00 (52,866 orders).',
    '10/10 acceptance checks; backfill twice = same totals; append twice = 26,014 instead of 13,007.',
]
FAQ = [
    ('How did you remove duplicates in MapReduce?', 'The mapper emits order_id as the key with the file day and the raw line as the value. The shuffle sends all records with the same key to the same reducer, sorted, so the copies arrive together. The reducer keeps the copy from the earliest file and increments a DUPLICATE counter by the number of extra copies.'),
    ('How do you make a Spark job idempotent?', 'Write output partitioned by business date and use overwrite with dynamic partition overwrite mode, so each run replaces exactly the partitions it produces. Never append blindly. Then a retry or backfill for a day gives the same result as the first run.'),
    ('What is the difference between silver and gold?', 'Silver holds cleaned, typed, deduplicated records at the original grain (one row per order). Gold holds aggregated tables designed for specific consumers and questions, such as revenue per canteen per day.'),
    ('How do you reconcile two datasets?', 'Agree a key and a measure, join from the system that should be complete (left join), and compare per group: counts and amounts. Explain every difference with a category (refunds, failed attempts) and report what is left as a gap with its exact keys, dates and amounts.'),
    ('Why use counters instead of print statements?', 'Counters are aggregated by the framework across all tasks, keep only successful attempts, appear in the job output and history server, and can be checked automatically. Prints in hundreds of task logs cannot be summed reliably.'),
]

PRACTICE_INTRO = 'Pipeline exercises using the real outputs of our run.'
PROBLEMS = [
    dict(level='easy', title='Check conservation in the map phase', stmt='Map input records were 357,332, with 104 headers and 13 test orders skipped. Do the map output records (357,215) add up?', inp='357,332 · 104 · 13',
         code='''print(357332 - 104 - 13)
''', explain='357,215: nothing vanished in the mappers.'),
    dict(level='easy', title='Shuffles', stmt='How many map-output fetches does the shuffle make with 104 maps and 3 reducers?', inp='104 × 3',
         code='''print(104 * 3)
''', explain='312, the "Shuffled Maps" counter: every reducer fetches its partition from every map.'),
    dict(level='easy', title='Compression ratio', stmt='Cleaned text was 29.7 MB, silver Parquet 7.2 MB. What is the ratio?', inp='29.7 · 7.2',
         code='''print(round(29.7 / 7.2, 1), "x smaller")
''', explain='About 4 times smaller, with real column types.'),
    dict(level='medium', title='Revenue per canteen per day', stmt='Aggregate a few clean rows into a daily revenue table like gold.daily_college.', inp='(dt, college, amount) rows',
         code='''rows = [("09-12", "KHR", 40), ("09-12", "KHR", 80), ("09-12", "NRL", 30), ("09-14", "KHR", 15)]
gold = {}
for dt, c, amt in rows:
    gold[(dt, c)] = gold.get((dt, c), 0) + amt
for k in sorted(gold):
    print(k, gold[k])
''', explain='A dictionary keyed by (day, canteen) is groupBy("dt", "college").agg(sum("amount")).'),
    dict(level='medium', title='Find the gap hour', stmt='Given UPI orders and confirmed order_ids, print unconfirmed orders grouped by hour.', inp='orders with hours',
         code='''orders = [("N-1", 13, 40), ("N-2", 13, 30), ("N-3", 12, 18), ("N-4", 13, 25)]
confirmed = {"N-3"}
gaps = {}
for oid, hour, amt in orders:
    if oid not in confirmed:
        n, s = gaps.get(hour, (0, 0))
        gaps[hour] = (n + 1, s + amt)
print(gaps)
''', explain='Everything unconfirmed falls in 13:00: an outage, not random failures.'),
    dict(level='medium', title='Average undercharge', stmt='11,711 Panvel orders were undercharged by ₹43,710 in total. What is the average per order, and what does that say about quantities?', inp='₹43,710 · 11,711',
         code='''print(round(43710 / 11711, 2))
''', explain='₹3.73 per order: more than ₹3 means some orders had 2 or 3 chais.'),
    dict(level='business', title='Maggi pricing', stmt='Maggi sold 1,619 orders for ₹60,300 at Kharghar from 21 Sept. If it is added to the menu at ₹30, are the amounts consistent?', inp='1,619 orders · ₹60,300',
         code='''orders, revenue = 1619, 60300
print("average per order:", round(revenue / orders, 2), "| qty per order:", round(revenue / orders / 30, 2))
''', explain='About 1.24 plates per order at ₹30: consistent, so the menu fix needs no correction of amounts.'),
    dict(level='advanced', title='A conservation check function', stmt='Write a function that checks received = clean + duplicates + malformed + test, and prints the difference if not.', inp='counter dictionary',
         code='''def conserved(c):
    total = c["CLEAN"] + c["DUPLICATE"] + c["MALFORMED"] + c["TEST_ORDER"]
    diff = c["RECEIVED"] - total
    print("OK" if diff == 0 else f"MISSING {diff} lines")
conserved({"RECEIVED": 357228, "CLEAN": 354135, "DUPLICATE": 2784, "MALFORMED": 296, "TEST_ORDER": 13})
conserved({"RECEIVED": 357228, "CLEAN": 353135, "DUPLICATE": 2784, "MALFORMED": 296, "TEST_ORDER": 13})
''', explain='Add it as a check after every clean run: a reducer that forgets its last group shows up immediately.'),
]

SCN_INTRO = 'Questions interviewers ask after you describe a pipeline like this one.'
SCENARIOS = '''    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Debugging · data</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>"Your dashboard shows yesterday\'s revenue doubled. What happened?"</h4>
      <p class="scn__situation">Nothing changed in the code; the scheduler retried a failed run.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> idempotency.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>The retry appended the same day again: the first attempt had already written part of its output.</li>
          <li>Fix the data by overwriting that day's partition; fix the job by writing per-day partitions with overwrite (dynamic mode) instead of append.</li>
          <li>Add a check: today's row count within a range and no duplicate keys, so it fails before the dashboard.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">MapReduce · design</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>"How would you remove duplicates from 100 files where a copy can be in another file?"</h4>
      <p class="scn__situation">Follow-up: "And which copy do you keep?"</p>
      <p class="scn__look"><b>The interviewer is checking:</b> key choice and determinism.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Key by the business key (order_id); the shuffle groups all copies in one reducer whatever file they came from.</li>
          <li>Keep a deterministic copy: earliest arrival (file day), so re-runs pick the same one and lateness is measured.</li>
          <li>Count extra copies in a counter; in Spark the same is a window with row_number() over order_id ordered by file day.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Reconciliation · finance</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>"Finance says UPI collections don\'t match the bank. Investigate."</h4>
      <p class="scn__situation">The difference is a few thousand rupees in a month.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> structured reconciliation.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Left join POS UPI orders to gateway records on order_id; classify: confirmed, failed-then-paid, refunded, unconfirmed.</li>
          <li>Group the unconfirmed by day, shop and hour: one cluster (ours: 201 orders, Nerul, 22 Sept 13:00) means an outage or a file missing, not random loss.</li>
          <li>Send the exact list to the gateway; add a daily gold table and alert so it is caught the next day, not at month-end.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Engineering · quality</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>"How do you test a data pipeline?"</h4>
      <p class="scn__situation">The team has unit tests for code but numbers still go wrong.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> testing data, not only code.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Unit-test the logic on tiny files with known edge cases (duplicate in the next file, broken line, unknown item); run mapper | sort | reducer locally.</li>
          <li>On every run, check conservation (in = out + rejected), uniqueness of keys, and totals against an independent source.</li>
          <li>Gate publication on those checks and keep the quarantine so failures are explainable.</li>
        </ul>
      </div></details>
    </article>
'''
