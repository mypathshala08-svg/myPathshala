import os, re
HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)
BODY = body(HERE)
rd = lambda f: open(os.path.join(UP, f), encoding='utf-8').read()


def mr_out(name, extra=()):
    keep = []
    for ln in rd('lab/txout/' + name).split('\n'):
        if re.search(r'map \d+% reduce', ln) or ln.strip().startswith('at ') or 'WARN' in ln:
            continue
        if ' INFO ' in ln and not re.search(r'number of splits|Running job|completed successfully|Task Id', ln):
            continue
        if not re.search(r'number of splits|Running job|completed successfully|Task Id|Killed by|Launched|Failed map|Failed reduce|Killed map|Data-local|Map input records|Reduce output|CLEAN|DUPLICATE|LATE|MALFORMED|PRICE|TEST_ORDER|UNDER|UNKNOWN|^real|ERROR|Failed!|  -$', ln):
            continue
        keep.append(re.sub(r'^\d{4}-\d\d-\d\d (\d\d:\d\d:\d\d) (INFO|ERROR) +(\w+):\d+ - ', r'\1 \2 \3 - ', ln))
    return '\n'.join(list(keep) + list(extra)).strip()


STATUS = rd('lab/txout/tx_drill_status.txt').strip().split('\n')

META = dict(
    module='14-capstone', lesson='03-review-and-interview-preparation', n='14.3',
    module_label='Module 14 · Capstone project',
    title='Review and interview preparation',
    desc='Capstone part 3: a production-readiness review of our Hadoop pipeline with real experiments. CombineTextInputFormat made the clean job 7× faster and wrong twice (Streaming passed byte-offset keys; the input-file environment variable is set once per task: LATE 46,646 instead of 2,100); a Spark compaction that writes the file day into every line gave 4 maps and 53 s instead of 4 min 39 s, with a byte-identical output checksum. A failure drill killed tasks and a DataNode mid-job: data correct, but the job client failed until replace-datanode-on-failure.policy=NEVER. Sizing for 40 canteens, a STAR project answer, a resume line and an interview question bank for the whole course.',
    og_desc='Fast and wrong, then fast and proven right: reviewing the capstone, breaking a worker on purpose, and turning it all into interview answers.',
    minutes=34, level='Intermediate',
    lead='The last part of the capstone does what senior engineers and interviewers do with any project: question it. We measure where the time goes, try to make it faster (and catch two real bugs with our checks), break a worker during a job to watch Hadoop recover, size the system for growth, and turn the whole project into answers you can give in an interview.',
    chips=['4 real experiments on our cluster', 'Interview question bank', 'Runs in your browser (Python)'],
)

RUN = dict(
    heading='Why one file name for many files breaks "late"',
    intro='<p>A simulation of our second combine attempt. One Python process reads lines from three files but is told only one file name at start-up, as Streaming does with its environment.</p>',
    code='''files = {"orders_KHR_2026-09-12.csv": ["KHR-0912-1,2026-09-12", "KHR-0912-2,2026-09-12"],
         "orders_KHR_2026-09-14.csv": ["KHR-0912-9,2026-09-12", "KHR-0914-1,2026-09-14"],
         "orders_KHR_2026-09-15.csv": ["KHR-0915-1,2026-09-15"]}

def late_count(lines_with_day):
    return sum(1 for fday, line in lines_with_day if fday > line.split(",")[1])

# baseline: one process per file, each knows its own file name
per_file = [(name[-14:-4], line) for name, lines in files.items() for line in lines]
# combined split: one process, one file name for the whole split (here: the last file)
told = list(files)[-1][-14:-4]
combined = [(told, line) for lines in files.values() for line in lines]
# fix: the file day travels inside every line (compaction)
tagged = [(name[-14:-4], line) for name, lines in files.items() for line in lines]

print("one file per map :", late_count(per_file))
print("combined, env var:", late_count(combined))
print("lineage in data  :", late_count(tagged))
''',
    anno=[
        ('told = list(files)[-1][-14:-4]', 'Like mapreduce_map_input_file: fixed when the process starts, wrong for the other files in the split.'),
        ('tagged = [(name[-14:-4], line) for name, lines in files.items() for line in lines]', 'compact.py does this with input_file_name(): each line carries its own file day.'),
    ],
    tasks=[
        dict(label='1 · Three ways to know the file', hint='Press <b>Run</b>. Only one order is really late (KHR-0912-9). Which method gets it right?', code=None),
        dict(label='2 · Where the time goes', hint='<b>Predict first:</b> with 6 vcores, 104 maps of about 20 s each run in waves. Estimate the map phase, then try 4 maps.',
             code='''import math
def map_phase(maps, seconds_each=20, slots=6):
    waves = math.ceil(maps / slots)
    return waves, waves * seconds_each
print("104 maps:", map_phase(104))
print("  4 maps:", map_phase(4, seconds_each=30))
'''),
        dict(label='3 · Regression check', hint='Compare the counters of the baseline and a new version. Change one value and run again.',
             code='''baseline = {"CLEAN": 354135, "DUPLICATE": 2784, "LATE": 2100, "MALFORMED": 296}
new      = {"CLEAN": 354135, "DUPLICATE": 2784, "LATE": 46646, "MALFORMED": 296}
diffs = {k: (baseline[k], new[k]) for k in baseline if baseline[k] != new[k]}
print("SAME" if not diffs else f"DIFFERENT: {diffs}")
'''),
        dict(label='4 · Your STAR answer', hint='Fill in your own numbers and print a two-minute answer skeleton.',
             code='''star = {
    "Situation": "4 canteens, 130 messy daily files, owner could not trust totals",
    "Task": "daily revenue, item mix, peak hours, UPI reconciliation, verified",
    "Action": "MapReduce dedupe + rules, Spark Parquet silver/gold, 10 acceptance checks",
    "Result": "10/10 PASS; found Rs 43,710 undercharged and a Rs 6,854 UPI gap; clean job 4m39s -> 53s",
}
for k, v in star.items():
    print(f"{k:<10}: {v}")
'''),
        dict(label='5 · Spot the error', hint='This regression check crashes when the new run has no LATE counter at all. Make it report the missing counter instead.',
             code='''baseline = {"CLEAN": 354135, "LATE": 2100}
new = {"CLEAN": 354135}
for k in baseline:
    print(k, "same" if new[k] == baseline[k] else "different")
''', expect='error'),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

COMPACT_OUT = '''lines: 357228
8607649 /capstone/bronze_monthly/orders/college=KHR/part-00002-bde4b71f-917a-4ab4-905c-5cdcde03e351.c000.txt
4192061 /capstone/bronze_monthly/orders/college=NRL/part-00000-bde4b71f-917a-4ab4-905c-5cdcde03e351.c000.txt
5728542 /capstone/bronze_monthly/orders/college=PNL/part-00001-bde4b71f-917a-4ab4-905c-5cdcde03e351.c000.txt
7329058 /capstone/bronze_monthly/orders/college=VSH/part-00000-bde4b71f-917a-4ab4-905c-5cdcde03e351.c000.txt
real	1m16.745s
'''

PCRUN = dict(
    heading='Run it on your PC: the review experiments',
    intro='<p>Same container and folder as Lessons 14.1–14.2, after the baseline clean job. Job logs are filtered to the lines that matter (splits, attempts, counters, timing).</p>',
    items=[
        dict(title='1 · Combine small files (first try: wrong)', file='combine_job.sh without the ignoreKey line',
             cmd=rd('lab/combine_job.sh').replace('  -D stream.map.input.ignoreKey=true \\\n', ''),
             output=mr_out('tx_combine_bug1.txt'),
             note='3 maps instead of 104 and 7× faster, but CLEAN is 192,799 instead of 354,135: the mapper received "offset TAB line".'),
        dict(title='2 · Combine with ignoreKey (second try: LATE wrong)', file='combine_job.sh',
             cmd=rd('lab/combine_job.sh'),
             output=mr_out('tx_combine_bug2.txt'),
             note='Every counter equals truth except LATE: one file name per task for about 35 files.'),
        dict(title='3 · Compact with lineage, then clean v2', file='compact.py · compact_job.sh · clean_job_v2.sh',
             cmd=rd('lab/compact.py') + '\n' + rd('lab/compact_job.sh') + '\n# clean_mapper_v2.py = clean_mapper.py plus two lines after line.rstrip():\n#     if "\\t" in line:\n#         fday, line = line.split("\\t", 1)\n' + rd('lab/clean_job_v2.sh'),
             output=COMPACT_OUT + '\n' + mr_out('tx_v2.txt'),
             note='Spark also printed a harmless "FileNotFoundException … college=*" while checking the glob for a metadata folder (removed). The two md5 lines are the baseline and v2 outputs: identical.'),
        dict(title='4 · Failure drill (first run: client fails, job succeeds)', file='drill.sh (bash on your PC)',
             cmd=rd('lab/drill.sh') + '\n# afterwards, inside the namenode container:\n# yarn application -status application_<id> | grep State\n# yarn logs -applicationId application_<id> -log_files syslog | grep JobHistoryEventHandler',
             output=mr_out('tx_drill.txt') + '\n$ yarn application -status application_1792730826465_0014\n' + '\n'.join(STATUS[1:]) + '\n$ yarn logs … | grep JobHistoryEventHandler\nERROR … JobHistoryEventHandler: Error writing History Event: …MapAttemptFinishedEvent\n… ' + STATUS[0],
             note='The output in HDFS was byte-identical to the baseline (same md5). Only the job-history file was lost, so the client could not report the final status.'),
        dict(title='5 · Failure drill with the small-cluster setting', file='clean_job_small.sh',
             cmd=rd('lab/clean_job_small.sh'),
             output=mr_out('tx_drill_fix.txt', ['e4cb870499eba837b494c5e4e85582dc  -   (sort | md5sum of the output)']),
             note='4 failed attempts, 108 map attempts launched, every counter exact, same checksum. Same drill.sh, calling clean_job_small.sh.'),
    ],
)

TRACE = dict(
    heading='A regression check, line by line',
    intro='<p>The check that rejected the second combine attempt: compare every counter of a new run with the trusted baseline and list the differences.</p>',
    code='''baseline = {"CLEAN": 354135, "DUPLICATE": 2784, "LATE": 2100}
runs = {"combine#2": {"CLEAN": 354135, "DUPLICATE": 2784, "LATE": 46646},
        "v2": {"CLEAN": 354135, "DUPLICATE": 2784, "LATE": 2100}}
for name, counters in runs.items():
    bad = [k for k in baseline if counters.get(k) != baseline[k]]
    print(name, "PASS" if not bad else f"FAIL {bad}")
''',
    notes={(5, 1): 'Compare :: Every counter of combine#2 against the baseline: only LATE differs.',
           (5, 2): 'Compare :: v2 matches on every counter.'},
)

WORKED_INTRO = 'Three calculations a reviewer or interviewer will ask you to do on the spot.'
EXAMPLES = [
    dict(level='b', tag='Performance · overhead', title='How much of the job was start-up?',
         problem='<p>The baseline spent 2,049,842 ms in 104 map tasks of about 3,435 lines each. If the real processing is about 1 second per map, what share of the map time was overhead?</p>',
         inp='2,049,842 ms · 104 maps · ~1 s real work per map',
         approach=['Average map time = total ÷ maps.', 'Overhead = average − real work.', 'Share = overhead ÷ average.'],
         code='''total_ms, maps, work_s = 2049842, 104, 1.0
def overhead(total_ms, maps, work_s):
    avg = total_ms / maps / 1000
    return round(avg, 1), round((avg - work_s) / avg * 100)
print("avg seconds per map, overhead %:", overhead(total_ms, maps, work_s))
''', notes={4: 'Result :: About 19.7 s per map, of which roughly 95% is start-up and scheduling (the 1 s of work is an estimate).'},
         tryit='That is why packing or compacting files gave a 5.3× speed-up without changing any logic.'),
    dict(level='i', tag='Sizing · growth', title='Size the system for 40 canteens and 3 years',
         problem='<p>Per canteen per month our raw data is (20.9 + 28.8) ÷ 4 MB. Kadak plans 40 canteens and wants 3 years online with replication 3. How much HDFS space, and how many daily order files a year without compaction?</p>',
         inp='12.4 MB per canteen-month · 40 canteens · 36 months · rf 3',
         approach=['Raw = per canteen-month × canteens × months.', 'Disk = raw × 3.', 'Files = canteens × open days per year.'],
         code='''per_cm = (20.9 + 28.8) / 4
def size_gb(canteens, months, rf=3):
    raw = per_cm * canteens * months / 1024
    return round(raw, 1), round(raw * rf, 1)
print("raw GB, with replicas GB:", size_gb(40, 36))
print("order files per year:", 40 * 312)
''', notes={4: 'Size :: About 17.5 GB raw, 52 GB with 3 replicas: small for HDFS (silver Parquet is about 4× smaller still).'},
         tryit='The answer to "will it scale?" is "storage yes, files no": compact daily, keep Parquet partitions per day, not per canteen-day.'),
    dict(level='a', tag='Reliability · recovery', title='What did the failure cost?',
         problem='<p>The drill killed 4 running map attempts on worker2. Each map takes about 20 s; the job ran 5 min 48 s instead of the baseline 4 min 39 s. How much of the extra time is re-running the 4 killed maps in parallel, and how much is something else?</p>',
         inp='4 attempts × ~20 s · 348 s vs 279 s',
         approach=['Extra time = drill − baseline.', 'Re-run cost ≈ one wave of 20 s.', 'The rest: detecting failures, fewer DataNodes to read from, run-to-run noise.'],
         code='''drill_s, base_s, rerun_s = 5 * 60 + 48, 4 * 60 + 39, 20
def explain(drill_s, base_s, rerun_s):
    extra = drill_s - base_s
    return extra, extra - rerun_s
print("extra seconds, not explained by re-runs:", explain(drill_s, base_s, rerun_s))
''', notes={4: 'Extra :: 69 s extra; only about 20 s is re-running the 4 maps.'},
         tryit='Honest interview answer: "the job recovered by itself and the output was identical; it cost about a minute, partly re-runs, partly a degraded cluster and normal run-to-run variation."'),
]

QUIZ = mix([
    dict(q='The first combine attempt finished in 38 s. Why was it rejected?', options=['It was too slow', 'Its counters disagreed with the baseline and truth (CLEAN 192,799)', 'It used 3 reducers', 'It wrote Parquet'], answer=1,
         why='Optimisations are judged by results first: counters and checksums must be identical.'),
    dict(q='With CombineTextInputFormat, what did our Python mapper receive until stream.map.input.ignoreKey=true?', options=['Only the line', '"byte offset TAB line"', 'A JSON object', 'Nothing'], answer=1,
         why='With TextInputFormat keys are discarded; with the combine format our mapper got the key too.'),
    dict(q='Why was LATE 46,646 in the second attempt?', options=['Duplicates were counted as late', 'The input-file environment variable is set once per task, but each task read about 35 files', 'The menu was missing', 'Clock skew'], answer=1,
         why='Streaming copies the configuration into the environment when it starts the process.'),
    dict(q='How did we fix it properly?', options=['Smaller splits', 'Compaction that writes each line\'s file day into the data, then 4 maps', 'More memory', 'Turning off counters'], answer=1,
         why='Lineage in the data works with any engine and split size: 53 s, byte-identical.'),
    dict(q='In the failure drill, what happened to counters of the killed attempts?', options=['They were added twice', 'They were discarded; only successful attempts count', 'They became negative', 'The job failed'], answer=1,
         why='CLEAN stayed exactly 354,135 with 108 map attempts for 104 maps.'),
    dict(q='The client printed "Streaming Command Failed!" but YARN said SUCCEEDED. Why?', options=['The output was corrupt', 'The job-history file lost its write pipeline on a 3-DataNode cluster, so the client could not get the final status', 'Python crashed', 'Kerberos expired'], answer=1,
         why='"Failed to replace a bad datanode … no more good datanodes"; the data itself was correct.'),
    dict(q='Which setting fixed it on our 3-node lab?', options=['dfs.replication=1', 'dfs.client.block.write.replace-datanode-on-failure.policy=NEVER', 'mapreduce.job.reduces=1', 'yarn.nodemanager.vmem-check-enabled=false'], answer=1,
         why='For extremely small clusters, keep writing to the remaining DataNodes; keep DEFAULT on normal clusters.'),
    dict(q='What is the best structure for "Tell me about your project"?', options=['List every tool you know', 'STAR: Situation, Task, Action, Result, with measured numbers', 'Explain Hadoop history', 'Show the code'], answer=1,
         why='A short story with numbers, then let the interviewer dig into what they care about.'),
])

REVISION = [
    'Review areas: correctness, idempotency, performance, scalability, reliability, cost, operability, security.',
    'Baseline: 104 maps × ~19.7 s, 4 min 39 s; the work per map was tiny: start-up dominated.',
    'Combine #1: 3 maps, 38 s, wrong (offset keys). Combine #2 (ignoreKey): 44 s, LATE 46,646 (env var once per task).',
    'Fix: compact.py tags each line with its file day → 4 maps, 53 s, identical counters and md5 e4cb8704…',
    'Drill: killed tasks + DataNode: attempts re-ran, output identical; 3-node history-file failure fixed with policy NEVER.',
    'Sizing: ~6 GB raw a year at 40 canteens; files, not bytes, are the scaling problem.',
    'Interview: STAR with numbers, one hard bug, one failure story, one design trade-off.',
]
FAQ = [
    ('Walk me through your capstone project.', 'Situation: four college canteens sent 130 daily files a month (POS orders, UPI payments, a menu) and could not trust their totals. Task: daily revenue per canteen, item mix, peak hours and UPI reconciliation, proven correct. Action: landed raw files in HDFS, wrote a MapReduce Streaming job keyed on order_id to deduplicate and apply quality rules with counters, used Spark to write Parquet silver partitioned by day and five gold tables, and wrote ten acceptance checks against a trusted total. Result: 10/10 checks, ₹43,710 of undercharging and a ₹6,854 UPI gap found, and the clean job cut from 4 min 39 s to 53 s with byte-identical output.'),
    ('What was the hardest problem?', 'Making the clean job faster. Packing small files with CombineTextInputFormat made it 7× faster but wrong: the Python mapper received byte-offset keys, and after fixing that the input-file environment variable named only one file per combined split, so 46,646 orders looked late instead of 2,100. Counters and acceptance checks caught both; the fix was compacting the files and writing each line\'s source day into the data.'),
    ('How does Hadoop handle a node failure during a job?', 'The ApplicationMaster re-runs failed or lost task attempts on other nodes, and HDFS readers switch to other replicas. Counters from failed attempts are discarded, so results stay exact. In our drill 4 attempts were killed, 108 launched for 104 maps, and the output was byte-identical. On a 3-DataNode cluster open writes can fail when one DataNode dies unless the replace-datanode-on-failure policy is NEVER.'),
    ('How do you prove that an optimisation did not change the results?', 'Run old and new versions on the same input, compare every counter and a checksum of the sorted output, and run the acceptance checks. Keep that golden output for future changes.'),
    ('Why did you use both MapReduce and Spark?', 'MapReduce made deduplication explicit as a shuffle on order_id and shows the classic Hadoop job model many companies still run; Spark was better for typed columns, Parquet, joins and several aggregations in one job. In a new project I would likely do it all in Spark (dropDuplicates or a window) with the same rules and checks.'),
    ('What would you change for production?', 'Schedule it in Airflow with retries and an SLA; compact daily; move silver to a table format such as Iceberg for safe corrections; add Kerberos and Ranger for access to student IDs; alert on check failures and on the UPI gap table; write a runbook that includes checking the YARN final status, not only the client exit code.'),
]

PRACTICE_INTRO = 'Review calculations and interview drills using the experiment numbers.'
PROBLEMS = [
    dict(level='easy', title='Speed-up', stmt='Baseline 4 min 39 s, compacted 53 s. What is the speed-up? Include the 1 min 17 s compaction: is it still worth it?', inp='279 s · 53 s · 77 s',
         code='''print(round(279 / 53, 1), "x without compaction,", round(279 / (53 + 77), 1), "x including it")
''', explain='5.3× for the job, 2.1× even counting compaction; compaction runs once while the clean job may run many times.'),
    dict(level='easy', title='Lines per map', stmt='357,332 lines over 104 maps, or 357,228 lines over 4 maps. How many lines per map task?', inp='two layouts',
         code='''print(round(357332 / 104), round(357228 / 4))
''', explain='3,436 vs 89,307 lines per task: the second is a sensible amount of work per task.'),
    dict(level='easy', title='Extra attempts', stmt='The drill launched 108 map attempts for 104 maps with 4 failed. How many attempts succeeded?', inp='108 · 4',
         code='''print(108 - 4)
''', explain='104: one successful attempt per map, which is what the counters are built from.'),
    dict(level='medium', title='How wrong was combine #1?', stmt='Compute the error in CLEAN and DUPLICATE against truth.', inp='192,799 vs 354,135 · 164,120 vs 2,784',
         code='''for name, got, want in [("CLEAN", 192799, 354135), ("DUPLICATE", 164120, 2784)]:
    print(name, got - want, f"{(got - want) / want:+.0%}")
''', explain='Orders −46%, duplicates +5,795%: wrong enough to notice, if anyone looks at the counters.'),
    dict(level='medium', title='Average file size after compaction', stmt='The four compacted files were 8,607,649, 4,192,061, 5,728,542 and 7,329,058 bytes. Average size, and share of a 128 MB block?', inp='4 sizes',
         code='''sizes = [8607649, 4192061, 5728542, 7329058]
avg = sum(sizes) / len(sizes)
print(round(avg / 1e6, 1), "MB,", f"{avg / (128 * 1024 * 1024):.1%} of a block")
''', explain='About 6.5 MB, 4.8% of a block: still small but fine for one month; at 40 canteens monthly files would be about 65 MB.'),
    dict(level='medium', title='STAR in numbers', stmt='Print a one-line result statement from a dictionary of measured numbers.', inp='your project numbers',
         code='''r = {"checks": "10/10", "undercharged": 43710, "upi_gap": 6854, "before_s": 279, "after_s": 53}
print(f"{r['checks']} checks; found Rs {r['undercharged']:,} undercharged and a Rs {r['upi_gap']:,} UPI gap; "
      f"clean job {r['before_s']}s -> {r['after_s']}s ({r['before_s'] / r['after_s']:.1f}x)")
''', explain='Results with numbers are what interviewers remember.'),
    dict(level='business', title='Is the pipeline worth it?', stmt='The accountant spent 4 days a month reconciling. The pipeline found ₹43,710 undercharged and ₹6,854 unconfirmed in one month. Accountant cost ₹2,500/day. What is the first month\'s value?', inp='4 days × ₹2,500 · ₹43,710 · ₹6,854',
         code='''time_saved = 4 * 2500
print(f"Rs {time_saved + 43710 + 6854:,} in the first month (illustrative)")
''', explain='About ₹60,600 in month one; the price bug, once fixed, keeps paying back.'),
    dict(level='advanced', title='Plan a failure test matrix', stmt='List failure drills for the pipeline with what to observe, and print them as a checklist.', inp='components',
         code='''drills = [("kill a map task JVM", "attempt re-runs, counters exact"),
          ("stop a DataNode", "reads use replicas; writes continue (policy on small clusters)"),
          ("stop a NodeManager", "containers lost after expiry, tasks rescheduled"),
          ("fill a disk to 97%", "write failures; alert before it happens (Lesson 13.4 incident)"),
          ("re-run a finished day", "idempotent: totals unchanged")]
for i, (what, observe) in enumerate(drills, 1):
    print(f"{i}. {what:<22} -> {observe}")
''', explain='A drill without a written expectation is just breaking things; each line is a test with a pass condition.'),
]

SCN_INTRO = 'Project deep-dive questions, the kind asked for 20–30 minutes in data-engineering interviews.'
SCENARIOS = '''    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Project · storytelling</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>"Tell me about a project you are proud of" (2 minutes)</h4>
      <p class="scn__situation">The opening question of most interviews.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> clarity, ownership and numbers.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li><b>S:</b> Four college canteens, 130 daily files a month from tills and the UPI gateway, totals never matched.</li>
          <li><b>T:</b> Daily revenue per canteen, item mix, peak hours and UPI reconciliation that the owner could trust.</li>
          <li><b>A:</b> HDFS bronze; MapReduce Streaming keyed on order_id for dedupe and rules with counters; Spark silver Parquet by day and gold tables; ten acceptance checks against trusted totals.</li>
          <li><b>R:</b> 10/10 checks; found ₹43,710 undercharged at one canteen and a ₹6,854 gateway gap in one hour; cut the clean job from 4 min 39 s to 53 s with byte-identical output.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Project · depth</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>"What went wrong, and how did you find it?"</h4>
      <p class="scn__situation">The follow-up to every project story.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> honesty and debugging method.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>A speed-up (combining small files) produced wrong counters twice: offset keys, then one file name per task making 46,646 orders "late".</li>
          <li>Found by comparing counters with the baseline and running acceptance checks, not by looking at run time.</li>
          <li>Fixed by carrying the source file day in the data; proved with identical counters and output checksum.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Design · scale</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>"The business grows 10×. What breaks first?"</h4>
      <p class="scn__situation">40 canteens, 3 years of history.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> sizing with numbers, knowing bottlenecks.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Bytes are fine: about 6 GB raw a year, about 52 GB with replicas for 3 years.</li>
          <li>Files are not: 12,480 order files a year would mean 1,040 map tasks a month and many NameNode objects; compact daily and partition silver by day.</li>
          <li>Then: more reducers for the clean shuffle, Spark for everything, an Iceberg table for corrections, Airflow for scheduling and backfills.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Operations · reliability</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>"Your scheduler marked the job failed, but the data looks complete. What do you do?"</h4>
      <p class="scn__situation">The client exited with an error at the very end.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> not trusting a single signal.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Check the application's final state in YARN (in our drill: FINISHED / SUCCEEDED), the output's _SUCCESS marker, counters and checks.</li>
          <li>Read the AM log: ours showed the job-history file lost its write pipeline when a DataNode died on a 3-node cluster.</li>
          <li>Decide from the checks (the job is idempotent, so a re-run is safe anyway); fix the root cause and add it to the runbook.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Career · resume</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>"I see Hadoop on your resume. Is it still relevant?"</h4>
      <p class="scn__situation">A common challenge in 2026 interviews.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> balanced judgement, not tool loyalty.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>New projects mostly use Spark, object storage and lakehouse tables, but many banks, telecoms and governments still run Hadoop clusters, and migrations need people who understand them (Lessons 2.1, 13.3).</li>
          <li>The ideas carry over directly: blocks and replicas, data locality, shuffle by key, small files, YARN scheduling, idempotent pipelines.</li>
          <li>My capstone shows both: a MapReduce job and a Spark job on the same cluster, verified the same way.</li>
        </ul>
      </div></details>
    </article>
'''
