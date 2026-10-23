import os
HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)
BODY = body(HERE)
rd = lambda f: open(os.path.join(UP, f)).read()

META = dict(
    module='11-yarn', lesson='05-logs-and-debugging', n='11.5',
    module_label='Module 11 · YARN',
    title='Logs and debugging',
    desc='Debug a failed Hadoop job the way on-call engineers do, on a real Hadoop 3.5.0 YARN cluster: client error, yarn application -status diagnostics, aggregated container logs in HDFS (/tmp/logs), yarn logs -containerId -log_files syslog, the exception with its source line (ItemRevenue.java:27), the bad input record, the ApplicationMaster log, and DEBUG log levels (82 vs 2,134 lines). Where daemon and container logs live, log aggregation and retention, web UIs on 8088, 8042 and 19888, a symptoms table of 10 real failures, Python log parser, quiz and interview scenarios.',
    og_desc='A job failed on our cluster. Follow the logs from “FAILED” to the exact bad record, with real yarn logs output.',
    minutes=28, level='Intermediate',
    lead='A failed job leaves logs on every machine it touched. YARN collects them into HDFS so you can read any container\'s log from one terminal. This lesson takes one real failed job and walks from the vague client error to the exact line of code and the exact input record, then shows where every kind of log lives and how to read them quickly.',
    chips=['One real failed job, end to end', '10 real errors mapped', 'Runs in your browser (Python)'],
)

RUN = dict(
    heading='Find the first exception in a log',
    intro='<p>These are real lines from our failed job\'s client output and map syslog. The parser finds the failed attempts, the first exception, and the first stack frame that is <i>our</i> code rather than Java or Hadoop.</p>',
    code='''log = """Task Id : attempt_1792655556966_0006_m_000000_0, Status : FAILED
Error: java.lang.NumberFormatException: For input string: "abc"
Task Id : attempt_1792655556966_0006_m_000000_1, Status : FAILED
Task Id : attempt_1792655556966_0006_m_000000_2, Status : FAILED
WARN [main] org.apache.hadoop.mapred.YarnChild: Exception running child : java.lang.NumberFormatException: For input string: "abc"
\\tat java.base/java.lang.NumberFormatException.forInputString(NumberFormatException.java:67)
\\tat ItemRevenue$OrderMapper.map(ItemRevenue.java:27)
\\tat ItemRevenue$OrderMapper.map(ItemRevenue.java:18)"""

FRAMEWORK = ("java.", "javax.", "org.apache.hadoop.", "sun.", "jdk.")
attempts, exception, user_frame = [], None, None
for line in log.splitlines():
    if line.startswith("Task Id :") and "FAILED" in line:
        attempts.append(line.split()[3].rstrip(","))
    if exception is None and "Exception" in line and ":" in line and not line.strip().startswith("at "):
        exception = line[line.find("java."):]
    s = line.strip()
    if s.startswith("at ") and user_frame is None:
        method = s[3:]
        if not method.startswith(FRAMEWORK):
            user_frame = method
print("failed attempts:", len(attempts), attempts[-1])
print("exception      :", exception)
print("your code      :", user_frame)
''',
    anno=[
        ('FRAMEWORK = ("java.", "javax.", "org.apache.hadoop.", "sun.", "jdk.")', 'Frames from Java and Hadoop tell you where the error surfaced; the first frame from your own classes tells you what to fix.'),
        ('    if exception is None and "Exception" in line and ":" in line and not line.strip().startswith("at "):', 'Read the FIRST exception. Later ones are often consequences (a task failing, then the job failing).'),
        ('        if not method.startswith(FRAMEWORK):', 'The first frame from our own code: class ItemRevenue$OrderMapper, method map, file ItemRevenue.java, line 27.'),
    ],
    tasks=[
        dict(label='1 · Parse the log', hint='Press <b>Run</b>. Which line of which file must you open?', code=None),
        dict(label='2 · A Streaming failure', hint='<b>Predict first:</b> in Lesson 9.8 the Java log only said “subprocess failed”. Where is the useful line, and what does the parser find in this stderr?',
             code='''stderr = """Traceback (most recent call last):
  File "/tmp/.../broken_mapper.py", line 14, in <module>
    print(f"{menu.get(itme, 'unknown')}\\\\t{amount}")
NameError: name 'itme' is not defined"""
lines = stderr.splitlines()
print("error :", lines[-1])
where = [l.strip() for l in lines if l.strip().startswith("File ")][-1]
print("where :", where)
'''),
        dict(label='3 · Log volume', hint='A cluster runs 4,000 jobs a day, 300 containers each, about 20 KB of logs per container at INFO. How much does aggregation write to HDFS per day, and over a 7-day retention? What if DEBUG makes logs 26× bigger (as in our lab)?',
             code='''jobs, containers, kb = 4000, 300, 20
day_gb = jobs * containers * kb / 1024 / 1024
print(f"INFO : {day_gb:.0f} GB/day, {day_gb * 7:.0f} GB kept for 7 days")
print(f"DEBUG: {day_gb * 26:.0f} GB/day")
'''),
        dict(label='4 · Files, not bytes', hint='Aggregation writes one HDFS file per app per node. With 4,000 apps a day each touching 40 nodes and 7 days retention, how many files does the NameNode hold just for logs?',
             code='''apps, nodes, days = 4000, 40, 7
files = apps * nodes * days
print(f"{files:,} files (+ about as many blocks) -> {files * 2 * 150 / 1024**2:.0f} MB of NameNode heap")
'''),
        dict(label='5 · Spot the error', hint='This parser takes the LAST exception line instead of the first, and crashes on a log that has none. Make it safe and return the first one.',
             code='''log = ["INFO starting", "INFO map 50%", "INFO done"]
exceptions = [l for l in log if "Exception" in l]
print("cause:", exceptions[-1])
''', expect='error'),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run it on your PC: fail a job on purpose and debug it',
    intro='<p>Use the Module 8 lab cluster with log aggregation on (it is in the lab <code>config</code>: <code>yarn.log-aggregation-enable=true</code>). The script needs <code>mr.jar</code> from Lesson 8.1 and <code>dirty_orders.csv</code> from Lesson 8.3 in HDFS. Copy it into the namenode container and run it there; it takes about two minutes.</p>',
    items=[
        dict(title='Debug a failed job with YARN tools only', file='logs_lab.sh',
             cmd=rd('lab/logs_lab.sh') + '\n# In the mr-lab folder:\n#   docker cp logs_lab.sh lab8-namenode-1:/tmp/mr/\n#   docker exec lab8-namenode-1 bash /tmp/mr/logs_lab.sh',
             output=rd('tx115.txt').strip(),
             note='Real output. Application and container IDs will differ on your machine. Container _000002 was the first map attempt. In part 7 the DEBUG run is a different, successful job on the clean file, used only to compare log sizes.'),
        dict(title='Every attempt of a job, from the JobHistory REST API', file='attempts.sh',
             cmd=rd('../08-mapreduce-fundamentals/attempts.sh') + '\n# Inside the namenode container:\n#   bash attempts.sh job_<your failed job id>',
             output='$ bash attempts.sh job_1792601400460_0033   (Lesson 8.6: a map JVM killed on purpose)\n' + rd('../08-mapreduce-fundamentals/tx86k.txt').strip().split('-- every attempt of this job\n')[-1],
             note='Real output from Lesson 8.6. The REST API gives every attempt with its node, time and diagnostics in one call; for our failed job above it would list the FAILED attempts and their NumberFormatException messages.'),
    ],
)

TRACE = dict(
    heading='Reading a stack trace from the top',
    intro='<p>A stack trace lists the calls that were active when the exception happened, newest first. Skip the library frames until you reach your own code.</p>',
    code='''frames = ["java.lang.NumberFormatException.forInputString",
          "java.lang.Integer.parseInt",
          "ItemRevenue$OrderMapper.map",
          "org.apache.hadoop.mapreduce.Mapper.run"]
for depth, f in enumerate(frames):
    mine = not f.startswith(("java.", "org.apache.hadoop."))
    if mine:
        print("start here:", f, "at depth", depth)
        break
''',
    notes={5: 'Filter :: Library frames say where the error surfaced, not why.',
           7: 'Your frame :: The first frame in your own code is where to look.'},
)

WORKED_INTRO = 'Four debugging problems from different domains: a stack trace, log retention, finding a bad record in a big file, and choosing a log level.'
EXAMPLES = [
    dict(level='b', tag='Retail · stack trace', title='Which line do you open?',
         problem='<p>A Flipkart-style sale report job fails. The syslog shows the trace below. Which file and line should the developer open first?</p>',
         inp='4 stack frames',
         approach=['Read from the top.',
                   'Skip java.* and org.apache.hadoop.* frames.',
                   'The first remaining frame is the answer.'],
         code='''trace = ["java.lang.ArrayIndexOutOfBoundsException: Index 5 out of bounds for length 5",
         "at SaleMapper.parse(SaleMapper.java:41)",
         "at SaleMapper.map(SaleMapper.java:22)",
         "at org.apache.hadoop.mapreduce.Mapper.run(Mapper.java:146)"]
frame = next(t for t in trace[1:] if not t.split()[1].startswith(("java.", "org.apache.hadoop.")))
print("open:", frame.split("(")[1].rstrip(")"), "| error:", trace[0].split(": ")[1])
''', notes={5: 'First user frame :: parse() at line 41 tried to read field 6 of a 5-field line.'},
         tryit='The message “Index 5 out of bounds for length 5” already tells you the line had 5 fields where 6 were expected.'),
    dict(level='i', tag='Telecom · retention', title='How long can we keep aggregated logs?',
         problem='<p>A telecom cluster writes about 120 GB of aggregated container logs a day (one replica). Logs live in HDFS with replication 3, and the admins allow at most 10 TB of raw space for logs. How many days of retention fit?</p>',
         inp='120 GB/day · replication 3 · 10 TB',
         approach=['Raw space per day = logs × replication.',
                   'Days = budget / raw per day.',
                   'Round down; that is retain-seconds / 86,400.'],
         code='''per_day = 120 * 3
days = int(10 * 1024 / per_day)
print(f"{per_day} GB raw per day -> keep {days} days -> retain-seconds = {days * 86400}")
''', notes={2: 'Raw :: Replication triples the space, as for any HDFS data (Lesson 5.3).'},
         tryit='Storing logs with replication 2, or compressing them (the IndexedFile format can), changes the answer a lot. Try both.'),
    dict(level='i', tag='Payments · bad record', title='Find the bad record without scanning 1.2 TB',
         problem='<p>A UPI settlement job fails on one map task. Its syslog starts with <code>Processing split: hdfs://…/part-0412.csv:268435456+134217728</code>. Which byte range must you search, and what fraction of the 1.2 TB is that?</p>',
         inp='start 268,435,456 · length 134,217,728 · 1.2 TB',
         approach=['The split string is file:start+length.',
                   'Search only that range (Lesson 8.2: the reader may run a little past the end to finish a line).',
                   'Compare with the whole input.'],
         code='''split = "part-0412.csv:268435456+134217728"
name, rng = split.split(":")
start, length = map(int, rng.split("+"))
print(f"{name}: bytes {start:,} to {start + length:,} ({length / 1024**2:.0f} MB)")
print(f"that is {length / (1.2 * 1024**4) * 100:.3f}% of the input")
''', notes={3: 'Range :: dd or a small Java/Python reader with seek() reads just this part.'},
         tryit='hdfs dfs -cat … | tail -c +START | head -c LENGTH works for a quick look; for big files a seekable reader is faster.'),
    dict(level='a', tag='Healthcare · log level', title='DEBUG for everyone, or for one task?',
         problem='<p>A claims job has 2,000 map tasks; one map keeps failing with an unclear error. At INFO each map writes about 82 log lines; at DEBUG about 2,134 (our lab). Compare turning DEBUG on for the whole job with rerunning only the failing split with DEBUG.</p>',
         inp='2,000 maps · 82 vs 2,134 lines',
         approach=['Lines for the whole job at DEBUG.',
                   'Lines for a one-split rerun at DEBUG.',
                   'Compare.'],
         code='''maps, info, debug = 2000, 82, 2134
print(f"whole job at DEBUG : {maps * debug:,} lines")
print(f"one split at DEBUG : {debug:,} lines (plus the normal run at INFO: {maps * info:,})")
''', notes={2: 'Scope :: Debug the smallest thing that reproduces the problem.'},
         tryit='Copy the failing split\'s byte range into a small file and run the job on it in local mode (Lesson 4.2) with DEBUG: seconds per try instead of minutes.'),
]

QUIZ = mix([
    dict(q='Where are a finished application\'s container logs when log aggregation is on?', options=['Only on each worker\'s local disk', 'In HDFS under /tmp/logs/<user>/…, one file per node', 'In the NameNode\'s memory', 'In the client\'s terminal only'], answer=1,
         why='Our lab: /tmp/logs/hadoop/bucket-logs-tfile/0006/application_…/worker1_36427.'),
    dict(q='Which command shows one container\'s syslog?', options=['hdfs dfs -cat syslog', 'yarn logs -applicationId <app> -containerId <c> -log_files syslog', 'yarn node -list', 'mapred queue -list'], answer=1,
         why='-log_files limits the output to that file.'),
    dict(q='Our application showed State FINISHED and Final-State FAILED. What does that mean?', options=['YARN crashed', 'The application ran to its end, and it reported failure itself', 'The job is still running', 'It was killed by a user'], answer=1,
         why='State is YARN\'s view of the app\'s life; Final-State is what the app (its AM) reported.'),
    dict(q='In a stack trace, which line usually tells you what to fix?', options=['The last line', 'The first frame that belongs to your own code', 'Any line from org.apache.hadoop', 'The line with the thread name'], answer=1,
         why='Here: ItemRevenue$OrderMapper.map(ItemRevenue.java:27).'),
    dict(q='A map fails on the same bad record every time. What helps?', options=['Raising mapreduce.map.maxattempts', 'Validating the field, counting and skipping bad records in the code', 'Adding more NodeManagers', 'Rerunning the job at night'], answer=1,
         why='Every attempt reads the same data and fails the same way.'),
    dict(q='How many map syslog lines did DEBUG produce compared with INFO in our lab?', options=['About the same', '2,134 vs 82', '200 vs 82', '20,000 vs 82'], answer=1,
         why='About 26 times more, for one small map task.'),
    dict(q='Where do you look when a Streaming (Python) task fails with “subprocess failed with code 1”?', options=['The ResourceManager log', 'The container\'s stderr, which holds the Python traceback', 'The NameNode log', 'The client output only'], answer=1,
         why='Lesson 9.8: the NameError was only in stderr.'),
    dict(q='The ResourceManager itself won\'t start. Where is the reason?', options=['In yarn logs of an application', 'In the ResourceManager\'s daemon log', 'In HDFS /tmp/logs', 'In the JobHistory UI'], answer=1,
         why='Lesson 11.4: “Queue configuration missing child queue names for root” was in the RM daemon log; no application existed.'),
])

REVISION = [
    '<b>Daemon logs</b> (RM, NM, NN, DN, JobHistory) stay on each machine in <code>$HADOOP_LOG_DIR</code>; <b>container logs</b> are <code>stdout</code>, <code>stderr</code>, <code>syslog</code>.',
    '<b>Log aggregation</b> uploads finished apps\' container logs to HDFS (<code>/tmp/logs/&lt;user&gt;/…</code>), one file per node; kept <code>retain-seconds</code>.',
    '<code>yarn logs -applicationId</code> with <code>-show_application_log_info</code>, <code>-containerId</code>, <code>-log_files</code>, <code>-am 1</code>.',
    'Order: client error → <code>yarn application -status</code> diagnostics → failed attempt syslog → first exception + your frame → input record → fix + counter.',
    'Lab: NumberFormatException "abc" at ItemRevenue.java:27; bad line 1,715 <code>901714,chai,abc</code>; Final-State FAILED, failedMaps:1.',
    'UIs: ResourceManager 8088, NodeManager 8042, JobHistory 19888 (Spark has its own History Server).',
    'DEBUG only when needed: 82 → 2,134 lines per map in our lab; <code>-D mapreduce.map.log.level=DEBUG</code> for one run, <code>yarn daemonlog -setlevel</code> for a daemon.',
]
FAQ = [
    ('How do I see the logs of a YARN application?', 'Run <code>yarn logs -applicationId &lt;id&gt;</code> after the application finishes (log aggregation must be enabled). Add <code>-containerId</code> and <code>-log_files syslog</code> (or stderr) to see one container\'s file, <code>-am 1</code> for the ApplicationMaster, and <code>-show_application_log_info</code> to list containers. While it runs, use the ResourceManager UI on port 8088 and follow the links to each container\'s logs on its NodeManager (port 8042).'),
    ('Where are YARN container logs stored?', 'While the container runs, in the NodeManager\'s local log directories (<code>yarn.nodemanager.log-dirs</code>, under <code>userlogs/application_…/container_…</code>). After the application finishes, with log aggregation enabled, each NodeManager uploads them to HDFS under <code>yarn.nodemanager.remote-app-log-dir</code> (default <code>/tmp/logs</code>) and deletes the local copies after <code>yarn.nodemanager.delete.debug-delay-sec</code>.'),
    ('Why does yarn logs say the logs are not available?', 'Common reasons: the application is still running (logs are aggregated at the end; use the NodeManager UI), log aggregation is disabled, the logs were already deleted by retention, or you are not the owner. Without aggregation the logs stay on each NodeManager\'s local disk.'),
    ('What is the difference between syslog, stderr and stdout in a container?', 'syslog is Hadoop\'s own log4j output from the task (framework messages and the full stack trace of a failure); stderr receives anything written to System.err and, for Streaming, the script\'s errors; stdout receives System.out. In MapReduce, data goes through the context, never stdout.'),
    ('How do I change the log level of a Hadoop job or daemon?', 'For one MapReduce job, pass <code>-D mapreduce.map.log.level=DEBUG</code> (and <code>mapreduce.reduce.log.level</code> or <code>yarn.app.mapreduce.am.log.level</code>). For a running daemon, use <code>yarn daemonlog -setlevel host:port logger LEVEL</code> (or <code>hadoop daemonlog</code>); it lasts until the daemon restarts. Permanent changes go in log4j.properties.'),
]

PRACTICE_INTRO = 'Debugging exercises using the real outputs from our failed job and earlier lessons.'
PROBLEMS = [
    dict(level='easy', title='Attempts per task', stmt='The client showed Failed map tasks=10 and the job failed when one task ran out of attempts (4 by default). How many failed attempts belonged to other tasks?', inp='10 failed · 4 per task',
         code='''print(10 - 4, "failed attempts belonged to other tasks (they were still retrying when the job stopped)")
''', explain='6. The bad lines are spread over the file, so several map tasks were failing at the same time.'),
    dict(level='easy', title='Aggregated log size', stmt='Add up the two aggregated log files of our failed app.', inp='108,540 and 142,851 bytes',
         code='''print(f"{108540 + 142851:,} bytes for one small failed job")
''', explain='About 251 KB for one small job with 15 containers; multiply by thousands of jobs a day to see why retention matters.'),
    dict(level='easy', title='DEBUG factor', stmt='How many times bigger was the DEBUG syslog?', inp='82 vs 2,134 lines',
         code='''print(round(2134 / 82, 1), "times")
''', explain='About 26 times.'),
    dict(level='medium', title='Split string to byte range', stmt='Parse a syslog split line and print the file, first byte and last byte.', inp='Processing split: hdfs://namenode/user/hadoop/data/dirty_orders.csv:2097152+2097152',
         code='''line = "Processing split: hdfs://namenode/user/hadoop/data/dirty_orders.csv:2097152+2097152"
path, rng = line.split(": ")[1].rsplit(":", 1)
start, length = map(int, rng.split("+"))
print(path.split("/")[-1], start, start + length - 1)
''', explain='dirty_orders.csv bytes 2,097,152 to 4,194,303 (the second 2 MB split from Lesson 8.3).'),
    dict(level='medium', title='Find bad amounts', stmt='Scan order lines and report the line number of every amount that is not a positive whole number.', inp='5 lines',
         code='''lines = ["1001,chai,15", "1002,dosa,45", "901714,chai,abc", "1004,samosa,-18", "1005,poha,25"]
for n, l in enumerate(lines, 1):
    amount = l.split(",")[2]
    if not amount.isdigit() or int(amount) <= 0:
        print(n, l)
''', explain='Lines 3 and 4: "abc" and a negative amount, the same kinds of problem as in dirty_orders.csv. ItemRevenue crashed only on "abc"; -18 would have silently reduced revenue.'),
    dict(level='medium', title='Group errors', stmt='Count failed attempts by error message to see if they share one cause.', inp='5 diagnostics',
         code='''diags = ["NumberFormatException: abc", "NumberFormatException: abc", "Java heap space",
         "NumberFormatException: abc", "NumberFormatException: abc"]
from collections import Counter
for msg, n in Counter(diags).most_common():
    print(n, msg)
''', explain='One dominant cause plus one different one: fix the data issue, then look at the heap error separately.'),
    dict(level='business', title='Cost of a late fix', stmt='A settlement job must finish by 06:00. A rerun takes 2.5 hours. If the on-call engineer needs 40 minutes to debug with yarn logs but 2 hours by logging in to workers one by one, what is the latest failure time each approach can recover from?', inp='06:00 deadline · 2.5 h rerun · 40 min vs 2 h',
         code='''from datetime import datetime, timedelta
deadline = datetime(2026, 10, 22, 6, 0)
for name, debug in [("yarn logs", 40), ("worker by worker", 120)]:
    print(f"{name:17} latest failure {(deadline - timedelta(minutes=150 + debug)):%H:%M}")
''', explain='02:50 vs 01:30: knowing the tools buys 80 minutes of safety every night (illustrative).'),
    dict(level='advanced', title='Retention planner', stmt='Given per-day aggregated log volume and HDFS budget, find the longest retention in whole days, for replication 3 and 2.', inp='180 GB/day · 12 TB budget',
         code='''per_day_gb, budget_tb = 180, 12
for rep in (3, 2):
    days = int(budget_tb * 1024 // (per_day_gb * rep))
    print(f"replication {rep}: {days} days, yarn.log-aggregation.retain-seconds={days * 86400}")
''', explain='22 days at replication 3, 34 at replication 2. Logs matter less than business data, so some teams accept lower replication for them.'),
]

SCN_INTRO = 'Debugging questions test whether you have actually run jobs on a cluster. Interviewers want an order of steps, not guesses.'
SCENARIOS = '''    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Debugging · basics</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“Your MapReduce job failed. What do you do?”</h4>
      <p class="scn__situation">The most common practical question.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> a systematic order and the right commands.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Read the client output, then <code>yarn application -status</code> for the diagnostics and the failed task.</li>
          <li><code>yarn logs -applicationId … -containerId … -log_files syslog</code> (or the JobHistory UI) for the failed attempt; find the first exception and the first frame of my code.</li>
          <li>Find the input (the split is in the syslog), reproduce on a sample in local mode, fix, and add a counter for bad records.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Operations · logs</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“yarn logs says no logs found for my application”</h4>
      <p class="scn__situation">A colleague's job finished an hour ago.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> how log aggregation works.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Check that log aggregation is enabled (<code>yarn.log-aggregation-enable</code>) and look in HDFS under the remote app log dir (<code>/tmp/logs/&lt;user&gt;</code>).</li>
          <li>Check the user: you can only read your own app's logs unless you are an admin; pass <code>-appOwner</code>.</li>
          <li>If aggregation is off, the logs are on each NodeManager's local disk until they are deleted; if retention already removed them, they are gone.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Operations · on-call</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>A nightly job fails at 2 AM; rerunning it fails again</h4>
      <p class="scn__situation">The report is due at 6 AM.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> data errors vs infrastructure errors, and a safe fix.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Same task failing with the same exception on different nodes = data or code, not a bad machine; different errors on one node = infrastructure.</li>
          <li>Locate the bad split and record, decide with the business: quarantine bad rows (count + side output) or stop; test the fix on that split.</li>
          <li>Afterwards: alert on the bad-row counter, contract with the data provider, and a runbook entry.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Platform · design</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>The NameNode is slowing down; /tmp/logs has 80 lakh files</h4>
      <p class="scn__situation">An admin notices the aggregated log directory is huge.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> log aggregation as a small-files problem.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Each app writes one file per node it used; thousands of apps a day × many nodes × long retention gives millions of files.</li>
          <li>Shorten <code>yarn.log-aggregation.retain-seconds</code>, use the IndexedFile (IFile) log aggregation format, and keep DEBUG off by default.</li>
          <li>Ship logs that must be kept longer to a log platform or object storage instead of HDFS.</li>
        </ul>
      </div></details>
    </article>
'''
