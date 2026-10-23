import os
HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)
BODY = body(HERE)
rd = lambda f: open(os.path.join(UP, f), encoding='utf-8').read()


def profile_out():
    keep = []
    for ln in rd('lab/txout/tx_profile.txt').split('\n'):
        if 'Unable to write to output stream' in ln or 'erasure' in ln.lower() or 'block group' in ln:
            continue
        if ln.startswith(' Total size:\t0 B') or ln.startswith(' Total files:\t0'):
            continue
        keep.append(ln)
    return '\n'.join(keep).strip()


META = dict(
    module='14-capstone', lesson='01-the-problem-and-the-dataset', n='14.1',
    module_label='Module 14 · Capstone project',
    title='The problem and the dataset',
    desc='Capstone part 1: a real data-engineering brief for four college canteens in Navi Mumbai. 130 raw files (104 POS order CSVs, 26 UPI JSON-lines files, a menu with a price change), 3.54 lakh real orders worth ₹1,15,24,009, and planted problems with known counts: 2,784 duplicates, 296 broken lines, 13 test orders, 2,100 late rows, an item missing from the menu, ₹43,710 undercharged and ₹6,854 of unconfirmed UPI. Requirements, source inventory, profiling in HDFS (130 files, 0.4 MB blocks), quality rules, a local pipe test that reproduces truth.json, and acceptance tests. Python simulation, quiz and interview scenarios.',
    og_desc='Before writing a pipeline: the business questions, 130 messy files, every kind of dirt in them, and the numbers that will prove the answer right.',
    minutes=30, level='Intermediate',
    lead='The capstone ties the whole course into one project. In this first part we do what experienced data engineers do before writing a pipeline: pin down the questions, take an inventory of the files, profile them in HDFS, list every data problem with a rule and a counter, and write the acceptance tests the finished pipeline must pass.',
    chips=['Real dataset on our cluster', 'Known right answers (truth.json)', 'Runs in your browser (Python)'],
)

RUN = dict(
    heading='Profile a sample before you trust it',
    intro='<p>Twelve lines from our files, with the same kinds of problems. The profiler counts what is wrong without fixing anything yet: that is profiling.</p>',
    code='''lines = [
    "KHR-0912-00101,2026-09-12 08:14:02,KHR,S00412,samosa,1,18,UPI",
    "KHR-0912-00102,2026-09-12 08:15:40,KHR,S03311,dosa,1,45,CASH",
    "KHR-0912-00377,2026-09-12 13:12:09,KHR,S07102,thali,1,80,UPI",
    "KHR-0912-00377,2026-09-12 13:12:09,KHR,S07102,thali,1,80,UPI",
    "KHR-BAD-2026-09-12-0,2026-09-12 10:00:00,KHR,S00042,dosa",
    "VSH-0903-00250,2026-09-03 09:40:11,VSH,TEST,idli,1,30,CASH",
    "KHR-0921-00009,2026-09-21 13:30:44,KHR,S02211,maggi,1,30,UPI",
    "PNL-0916-00031,2026-09-16 08:05:19,PNL,S05120,chai,2,30,UPI",
    "NRL-0914-00007,2026-09-14 16:02:55,NRL,S00777,samosa,1,18,CASH",
    "VSH-0915-00410,2026-09-15 13:01:00,VSH,S01010,poha,1,forty five,UPI",
    "KHR-0912-00380,2026-09-12 17:55:31,KHR,S04404,vada pav,2,40,UPI",
    "NRL-0914-00008,2026-09-14 13:20:02,NRL,S08008,thali,1,80,UPI",
]
menu = {"chai": 18, "dosa": 45, "thali": 80, "idli": 30, "samosa": 18, "poha": 25, "vada pav": 20}

seen, report = set(), {"rows": 0, "broken": 0, "test": 0, "duplicate": 0, "unknown_item": 0, "price_gap": 0}
for line in lines:
    report["rows"] += 1
    f = line.split(",")
    if len(f) != 8 or not f[6].isdigit():
        report["broken"] += 1
        continue
    if f[3] == "TEST":
        report["test"] += 1
        continue
    if f[0] in seen:
        report["duplicate"] += 1
        continue
    seen.add(f[0])
    if f[4] not in menu:
        report["unknown_item"] += 1
    elif int(f[6]) != int(f[5]) * menu[f[4]]:
        report["price_gap"] += 1
for k, v in report.items():
    print(f"{k:<13}{v}")
print("good orders :", len(seen))
''',
    anno=[
        ('    if len(f) != 8 or not f[6].isdigit():', 'Broken lines: too few fields, or an amount that is not a number. In the real job they go to quarantine.'),
        ('    if f[0] in seen:', 'A duplicate is a second row with the same order_id, the business key.'),
        ('    elif int(f[6]) != int(f[5]) * menu[f[4]]:', 'Panvel charged ₹15 for chai after the price became ₹18: 2 × 18 = 36, but the row says 30.'),
    ],
    tasks=[
        dict(label='1 · Profile the sample', hint='Press <b>Run</b>. Find each problem from the data-quality table in the output.', code=None),
        dict(label='2 · Rows per canteen', hint='<b>Predict first:</b> how many of the 12 lines come from KHR? Count by the third field.',
             code='''lines = ["KHR-1,..,KHR", "KHR-2,..,KHR", "VSH-1,..,VSH", "PNL-1,..,PNL", "KHR-3,..,KHR", "NRL-1,..,NRL", "NRL-2,..,NRL"]
count = {}
for line in lines:
    college = line.split(",")[2]
    count[college] = count.get(college, 0) + 1
print(count)
'''),
        dict(label='3 · Late or on time?', hint='An order is late when the day in its timestamp is earlier than the day of the file it arrived in. Change the file day and run again.',
             code='''file_day = "2026-09-14"
orders = ["KHR-0912-00380,2026-09-12 17:55:31", "KHR-0914-00001,2026-09-14 08:00:10"]
for o in orders:
    oid, ts = o.split(",")
    print(oid, "late" if ts[:10] < file_day else "on time")
'''),
        dict(label='4 · Which price applies?', hint='Chai cost ₹15 until 15 Sept and ₹18 from 16 Sept. Look up the price for a date.',
             code='''menu = [("chai", 15, "2026-09-01", "2026-09-15"), ("chai", 18, "2026-09-16", "2026-09-30")]
def price(item, day):
    for it, p, start, end in menu:
        if it == item and start <= day <= end:
            return p
for day in ["2026-09-15", "2026-09-16"]:
    print(day, price("chai", day))
'''),
        dict(label='5 · Spot the error', hint='This parser crashes on the broken line "forty five". Make it count the line as broken instead.',
             code='''line = "VSH-0915-00410,2026-09-15 13:01:00,VSH,S01010,poha,1,forty five,UPI"
amount = int(line.split(",")[6])
print("amount", amount)
''', expect='error'),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run it on your PC: generate, land and profile the capstone data',
    intro='<p>Start the Module 8 lab (<code>docker compose -p lab8 up -d</code> in its folder). Generate the files on your PC (Python 3, about a minute), copy the folder into the namenode container, and run the scripts there as user <code>hadoop</code>. All outputs below are real.</p>',
    items=[
        dict(title='1 · Generate the dataset (on your PC)', file='make_capstone.py',
             cmd=rd('lab/make_capstone.py') + '\n# python3 make_capstone.py\n# docker cp . lab8-namenode-1:/tmp/capstone      (run inside the folder with the scripts and capstone_raw/)',
             output=rd('lab/txout/tx_make.txt').strip(),
             note='The seed fixes every random choice, so your files and numbers are identical to ours. truth.json holds these totals.'),
        dict(title='2 · Land in bronze', file='land.sh',
             cmd=rd('lab/land.sh') + '\n# docker exec -it -w /tmp/capstone lab8-namenode-1 bash land.sh',
             output='''           5          104             20.9 M /capstone/bronze/orders
           1           26             28.8 M /capstone/bronze/payments
           1            1                389 /capstone/ref

real	0m47.052s''',
             note='Each hdfs dfs command starts a JVM, so landing 130 files took 47 seconds. Columns: directories, files, size.'),
        dict(title='3 · Profile what landed', file='profile.sh',
             cmd=rd('lab/profile.sh'),
             output=profile_out(),
             note='"head" closes the pipe early, so hdfs dfs -cat prints a harmless "Unable to write to output stream"; we removed those lines and fsck\'s erasure-coding section. du shows size and size × 3 replicas.'),
        dict(title='4 · Test the cleaning rules locally (no cluster)', file='clean_mapper.py · clean_reducer.py · local_test.sh',
             cmd=rd('lab/clean_mapper.py') + '\n' + rd('lab/clean_reducer.py') + '\n' + rd('lab/local_test.sh'),
             output=rd('lab/txout/tx_local.txt').strip(),
             note='The mapper and reducer are explained line by line in Lesson 14.2. Here they serve as a profiler: every counter equals truth.json before the cluster is involved.'),
    ],
)

TRACE = dict(
    heading='Keep the earliest copy of each order',
    intro='<p>Three copies of rows arrive in different files. The dictionary keeps, for each order_id, the copy from the earliest file. That decides both "duplicate" and "late".</p>',
    code='''rows = [("09-14", "KHR-0912-00380"), ("09-12", "KHR-0912-00377"),
        ("09-12", "KHR-0912-00377"), ("09-14", "KHR-0914-00001")]
first = {}
dups = 0
for file_day, oid in rows:
    if oid in first:
        dups += 1
        first[oid] = min(first[oid], file_day)
    else:
        first[oid] = file_day
late = [oid for oid, day in first.items() if day[3:] > oid[6:8]]
print(first, "duplicates:", dups, "late:", late)
''',
    notes={(7, 1): 'Duplicate :: Same order_id seen before: count it and keep the earlier file day.',
           11: 'Late :: The order\'s own day (characters 6–7 of the id here) is earlier than the day of the file it first arrived in.'},
)

WORKED_INTRO = 'Three calculations every capstone review asks for: how much data, how dirty, and how big next year.'
EXAMPLES = [
    dict(level='b', tag='Profiling · volume', title='Orders per canteen per open day',
         problem='<p>From the true totals, how many orders does each canteen serve on an average open day? The canteens were open 26 days in September.</p>',
         inp='KHR 117,937 · VSH 100,373 · PNL 78,438 · NRL 57,387 · 26 days',
         approach=['Divide each canteen\'s month by the open days.', 'Round to whole orders.', 'Print them busiest first.'],
         code='''orders = {"KHR": 117937, "VSH": 100373, "PNL": 78438, "NRL": 57387}
def per_day(total, days=26):
    return round(total / days)
for c in sorted(orders, key=orders.get, reverse=True):
    print(c, per_day(orders[c]), "orders/day")
''', notes={2: 'Helper :: A small function, so the trace shows a frame being pushed for each canteen.'},
         tryit='Kharghar sells about 4,536 orders a day, close to the 4,500 the generator was told.'),
    dict(level='i', tag='Profiling · quality', title='How dirty is the data?',
         problem='<p>Express each problem as a share of the 357,228 data lines, and say which ones change revenue if ignored.</p>',
         inp='duplicates 2,784 · malformed 296 · test 13 · late 2,100',
         approach=['Share = count ÷ data lines.', 'Duplicates add revenue twice; late rows move revenue to the wrong day.', 'Print as percentages.'],
         code='''lines = 357228
problems = {"duplicate": 2784, "malformed": 296, "test": 13, "late": 2100}
for name, n in problems.items():
    print(f"{name:<10}{n:>6}  {n / lines:.2%}")
print("lines that are not clean orders:", 2784 + 296 + 13)
''', notes={3: 'Share :: Under 1% each, which is exactly why nobody noticed in Excel.'},
         tryit='357,228 − 3,093 = 354,135: the true number of orders.'),
    dict(level='a', tag='Sizing · next year', title='What if Kadak grows to 40 canteens?',
         problem='<p>The owner plans 40 canteens. Keep today\'s average file size and daily volume per canteen. How many order files and bytes per year, and how many map tasks would one month need if we keep one file per canteen per day?</p>',
         inp='104 files = 20.9 MB per month for 4 canteens · 312 open days a year',
         approach=['Files per year = canteens × open days.', 'Bytes scale with canteens.', 'One map task per small file for a month.'],
         code='''canteens, days_year = 40, 312
mb_per_canteen_month = 20.9 / 4
files_year = canteens * days_year
print("files/year:", files_year)
print("MB/year:", round(canteens * mb_per_canteen_month * 12))
print("map tasks for one month:", canteens * 26)
''', notes={4: 'Files :: 12,480 small files a year, before payments.'},
         tryit='About 2.5 GB of orders a year: not big data yet, but 1,040 map tasks a month is exactly the small-files problem we fix in 14.3.'),
]

QUIZ = mix([
    dict(q='What is the first step of a data-engineering capstone?', options=['Install Spark', 'Understand the questions and profile the data', 'Tune YARN memory', 'Write the dashboard'], answer=1,
         why='Requirements, source inventory and profiling come before any pipeline code.'),
    dict(q='What is the grain of our orders data?', options=['One row per item sold', 'One row per order', 'One row per canteen per day', 'One row per payment'], answer=1,
         why='One order per row, identified by order_id.'),
    dict(q='Why must deduplication look across all files, not file by file?', options=['Files are too big', 'A re-sent row can land in the next day\'s file', 'HDFS requires it', 'To save memory'], answer=1,
         why='Copies of the same order_id can sit in different files, so all copies must meet under one key.'),
    dict(q='An order from 12 September arrives in the file of 14 September. Which day does its revenue belong to?', options=['14 September', '12 September (its timestamp)', 'Neither, drop it', 'Both days'], answer=1,
         why='The business date comes from the order timestamp; 2,100 orders are late.'),
    dict(q='Panvel charged ₹15 for chai after the price became ₹18. What should the pipeline do?', options=['Change the amount to ₹18', 'Keep the amount charged, flag it and report the ₹ gap', 'Delete the rows', 'Ignore it'], answer=1,
         why='Revenue must be what was actually charged; the ₹43,710 gap is a business finding.'),
    dict(q='What is truth.json in our capstone?', options=['Hadoop configuration', 'The correct totals written by the generator, used by acceptance tests', 'A log file', 'The menu'], answer=1,
         why='In companies the same role is played by bank statements, ledgers or the old system\'s output.'),
    dict(q='fsck reported 130 files with an average block of 400,652 bytes. What does that mean?', options=['The cluster is full', 'Many small files: NameNode memory and one map task per file are wasted', 'Replication failed', 'Blocks are corrupt'], answer=1,
         why='Each block is about 0.3% of 128 MB: the small files problem (Lesson 7.5).'),
    dict(q='Why test the mapper and reducer with a Linux pipe first?', options=['It is faster than the cluster and finds logic bugs early', 'The cluster cannot run Python', 'Pipes are required by Hadoop', 'To avoid writing tests'], answer=0,
         why='mapper | sort | reducer is a Streaming job on one machine; it reproduced every planted count in 25 seconds.'),
])

REVISION = [
    'Capstone = one realistic problem end to end: requirements → inventory → profiling → rules → pipeline → acceptance tests.',
    'Kadak Canteens: 4 canteens, 104 POS CSVs + 26 UPI files + menu = 130 files, 52 MB; 354,135 true orders, ₹11,524,009.',
    'Grain = one order; business key = <code>order_id</code>; business date from <code>ts</code>, not the file name.',
    'Planted dirt: 2,784 duplicates, 296 malformed, 13 test, 2,100 late, 1,619 unknown item, 11,711 undercharged (₹43,710), 201 unconfirmed UPI (₹6,854).',
    'Rules: quarantine broken lines, drop test rows, keep the earliest copy, keep but flag unknown items and price gaps; never fix money silently.',
    'Bronze keeps raw bytes; fsck showed 130 blocks of 0.4 MB: small files.',
    'A local pipe test (mapper | sort | reducer) reproduced every counter before using the cluster.',
]
FAQ = [
    ('How do you start a data engineering project?', 'By writing down the business questions and deliverables, listing every source (format, frequency, volume, key, owner), profiling the real data for counts, keys, nulls, invalid values, duplicates and late records, agreeing rules for each problem, and agreeing acceptance criteria against a trusted source before building the pipeline.'),
    ('What is data profiling?', 'Measuring what the data really contains before using it: row counts per source and day, distinct and duplicate keys, null and invalid values, value ranges, unexpected categories and arrival delays. Profiling turns assumptions ("order_id is unique") into facts ("2,784 order_ids appear twice").'),
    ('What is the grain of a table and why does it matter?', 'The grain is what one row represents, for example one order. Every aggregation, join and deduplication rule depends on it: if you think a row is an order but it is really an order line, revenue and counts are wrong.'),
    ('How do you handle late-arriving data?', 'Use the event time (when the order happened) for business dates, not the arrival or file date; partition by event date; and make loads idempotent so a late row can be added by re-running that day without double counting. Flag late rows so delays can be monitored.'),
    ('Why keep bad rows instead of deleting them?', 'Because someone must be able to see what was rejected and why: a quarantine table with the raw line and a reason makes the pipeline auditable, lets source teams fix their systems, and proves that the totals add up (clean + quarantined + dropped = received).'),
]

PRACTICE_INTRO = 'Profiling and planning exercises on the capstone dataset.'
PROBLEMS = [
    dict(level='easy', title='Do the lines add up?', stmt='Check that clean orders + duplicates + malformed + test orders equals the data lines in the order files.', inp='354,135 · 2,784 · 296 · 13 · 357,228',
         code='''print(354135 + 2784 + 296 + 13, 357228)
''', explain='Both are 357,228. An equation like this belongs in every pipeline review: nothing appeared or vanished.'),
    dict(level='easy', title='Headers in the files', stmt='The order files had 357,332 lines in total. How many were headers?', inp='357,332 lines · 357,228 data lines',
         code='''print(357332 - 357228, "headers, one per file")
''', explain='104 headers = 104 files. Forgetting to skip them would create 104 "malformed" rows.'),
    dict(level='easy', title='Average order value', stmt='Revenue ₹11,524,009 from 354,135 orders: what is the average order value?', inp='₹11,524,009 · 354,135',
         code='''print(round(11524009 / 354135, 2))
''', explain='About ₹32.54 per order.'),
    dict(level='medium', title='Replicated size', stmt='Bronze holds 52,084,844 bytes with replication 3. How many MB of disk does it use across the cluster?', inp='52,084,844 B · rf 3',
         code='''print(round(52084844 * 3 / 1024 / 1024, 1), "MB")
''', explain='About 149 MB (du showed 20.9 + 10.2 + 13.9 + 17.8 + 86.3 MB with replicas).'),
    dict(level='medium', title='Share of revenue per canteen', stmt='Print each canteen\'s share of total revenue.', inp='by_college revenue from truth.json',
         code='''rev = {"KHR": 3860438, "VSH": 3270741, "PNL": 2517725, "NRL": 1875105}
total = sum(rev.values())
for c, r in rev.items():
    print(c, f"{r / total:.1%}")
''', explain='Kharghar earns a third of the money; Nerul about a sixth.'),
    dict(level='medium', title='Find duplicate keys', stmt='Given a list of order_ids, print the ones that appear more than once and how often.', inp='a list of ids',
         code='''ids = ["KHR-1", "KHR-2", "KHR-1", "VSH-7", "KHR-1", "VSH-7", "PNL-3"]
counts = {}
for i in ids:
    counts[i] = counts.get(i, 0) + 1
print({k: v for k, v in counts.items() if v > 1})
''', explain='KHR-1 three times, VSH-7 twice: 3 extra rows to remove.'),
    dict(level='business', title='Cost of the Panvel price bug', stmt='Panvel sold chai at ₹15 instead of ₹18 for 15 open days (16–30 Sept, minus Sundays). The lab found ₹43,710 undercharged. What is that per open day, and per year if never fixed (312 open days)?', inp='₹43,710 · 13 open days',
         code='''days = 13          # 16-30 Sept has 15 days, 2 of them Sundays
per_day = 43710 / days
print(round(per_day), "Rs/day,", round(per_day * 312), "Rs/year")
''', explain='About ₹3,362 a day, ₹10.5 lakh a year: a data pipeline that pays for itself.'),
    dict(level='advanced', title='Write an acceptance test', stmt='Write a function that compares pipeline results with truth values and prints PASS or FAIL for each, plus a summary.', inp='two dictionaries',
         code='''truth = {"orders": 354135, "revenue": 11524009, "late": 2100}
result = {"orders": 354135, "revenue": 11524009, "late": 2101}
def check(result, truth):
    ok = 0
    for k in truth:
        good = result.get(k) == truth[k]
        ok += good
        print("PASS" if good else "FAIL", k, result.get(k), truth[k])
    print(f"{ok}/{len(truth)} passed")
check(result, truth)
''', explain='One wrong number fails the run; in the real check.py this is how a broken optimisation was caught in Lesson 14.3.'),
]

SCN_INTRO = 'Interviewers love "your first week on a project" questions. These are the common ones.'
SCENARIOS = '''    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Project start · process</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>"You get a pen drive of files and a vague request. What do you do first?"</h4>
      <p class="scn__situation">A small business wants "reports" from its till and payment files.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> that you clarify before you code.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Turn "reports" into concrete questions with the owner (revenue per canteen per day, item mix, peak hours, UPI reconciliation) and agree who uses them and how often.</li>
          <li>Inventory the sources: format, frequency, volume, key, owner, and find a trusted total to check against (bank statement).</li>
          <li>Profile, list the problems with counts, agree rules, then design the pipeline.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Data quality · judgement</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>"One shop charged the old price for two weeks. Do you correct the revenue?"</h4>
      <p class="scn__situation">The menu says ₹18; the till charged ₹15.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> that you don't change financial facts silently.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>No. Revenue is what customers actually paid; it must match the cash and UPI received.</li>
          <li>Flag the rows, compute the gap (₹43,710 in our data) and report it to the business with the shop and dates, so they fix the till.</li>
          <li>If finance wants a "list price" view, add it as a separate column, never overwrite the amount.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Design · late data</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>"Some shops upload yesterday's sales today. How do you design for that?"</h4>
      <p class="scn__situation">Daily reports were already sent when the late rows arrive.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> event time vs arrival time, idempotency.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Partition by event date from the timestamp; keep the arrival file and time as lineage columns and flag late rows.</li>
          <li>Re-process the affected event dates (a small backfill) with overwrite-by-partition, so re-runs never double count.</li>
          <li>Measure lateness; agree a cut-off (e.g. reports final after 2 days) and re-issue changed reports.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Testing · trust</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>"How do you know your pipeline's numbers are right?"</h4>
      <p class="scn__situation">The business has been burned by wrong dashboards before.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> reconciliation and automated checks.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Reconcile against an independent source: bank or gateway totals, source-system row counts, the old report during migration.</li>
          <li>Prove conservation: clean + quarantined + dropped = received, per day and source.</li>
          <li>Automate it: acceptance checks run after every load and fail the pipeline before gold is published.</li>
        </ul>
      </div></details>
    </article>
'''
