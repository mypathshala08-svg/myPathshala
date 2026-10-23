import os
HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)
BODY = body(HERE).replace('{{PLAYGROUND}}', playground(dict(
    title='A job that survives a failure',
    intro='<p>Two racks of workers. Run the word count job, then fail a node and run it again: map tasks on the failed node are rescheduled on nodes that hold another replica of their block.</p>',
    racks=2, nodes=3, features=['upload', 'job', 'locality', 'chaos'],
    preload=[dict(name='feedback_x20.txt', sizeMB=1024)],
    **{'try': [
        dict(text='Upload a file (or use the preloaded one).', on='upload-done'),
        dict(text='Press <b>Run word count job</b> and let it finish.', on='job-done'),
        dict(text='Press <b>Fail a random node</b>.', on='node-stop'),
        dict(text='Run the job again. Does it still finish, and where did the maps run?', on='job-done'),
    ]},
)))
rd = lambda f: open(os.path.join(UP, f)).read()

META = dict(
    module='08-mapreduce-fundamentals', lesson='06-word-count-end-to-end', n='8.6',
    module_label='Module 8 · MapReduce fundamentals',
    title='Word count end to end',
    desc='The complete life of a Hadoop MapReduce job on a real Hadoop 3.5.0 cluster with HDFS and YARN: WordCount with the new org.apache.hadoop.mapreduce API (vs the old mapred API), javac with hadoop classpath, jar, hadoop jar and GenericOptionsParser, submission (staging directory, splits, ResourceManager, MRAppMaster, task containers), counters and output for 2 lakh feedback lines (1,033,238 words, 31 distinct), common errors (FileAlreadyExistsException, InvalidInputException), and a map task killed with kill -9: exit code 137, retried on another worker, same answer. Python simulation, quiz and interview scenarios.',
    og_desc='Write, build, run and break a real WordCount job: a killed map task, exit code 137, a retry on another worker, and the exact same counts.',
    minutes=30, level='Beginner',
    lead='Every MapReduce program has the same parts: a mapper, a reducer, a driver, a jar and one command. This lesson takes word count from an empty Java file to a sorted result in HDFS on a real cluster, follows what YARN does at each step, reads the errors you will meet first, and then kills a running task to watch Hadoop recover.',
    chips=['Real job, killed and recovered', 'Every command and error explained', 'Runs in your browser (Python)'],
)

RUN = dict(
    heading='Word count, exactly like the Java version',
    intro='<p>The tokenizer below uses the same delimiters as <code>WordCount.java</code> (space, tab and <code>.,!?;:"\'()</code>, after lowercasing), so for the same lines it gives the same counts as the real job.</p>',
    code='''DELIMS = " \\t.,!?;:\\"'()"

def tokens(line):                         # like java.util.StringTokenizer(line.toLowerCase(), DELIMS)
    word, out = "", []
    for ch in line.lower():
        if ch in DELIMS:
            if word: out.append(word)
            word = ""
        else:
            word += ch
    if word: out.append(word)
    return out

lines = ["the idli was fresh", "Why is the chai was cold?", "loved the vada pav was tasty!", "the chai was hot"]
pairs = [(w, 1) for line in lines for w in tokens(line)]       # map
print(len(pairs), "pairs, e.g.", pairs[:5])

counts = {}
for w, one in pairs:                                           # shuffle + reduce
    counts[w] = counts.get(w, 0) + one
for w in sorted(counts):
    print(w, counts[w])
''',
    anno=[
        ('    for ch in line.lower():', 'toLowerCase() first, so “Why” and “why” are one key.'),
        ('        if ch in DELIMS:', 'Punctuation splits words just like spaces: “cold?” becomes “cold”.'),
        ('pairs = [(w, 1) for line in lines for w in tokens(line)]       # map', 'One pair per word: our 2 lakh lines produced 1,033,238 pairs.'),
    ],
    tasks=[
        dict(label='1 · Count the words', hint='Press <b>Run</b>. Why does “vada pav” show up as two words?', code=None),
        dict(label='2 · Sort by count', hint='<b>Predict first:</b> which word is on top? Sort the counts from high to low, like <code>sort -k2,2nr</code>.',
             code='''counts = {"amazing": 17687, "chai": 33431, "the": 166921, "was": 200000, "loved": 33570, "cold": 8452}
for w, c in sorted(counts.items(), key=lambda x: -x[1])[:3]:
    print(w, c)
'''),
        dict(label='3 · Stop words', hint='Remove “the”, “was”, “is”, “my” before counting. Which real words are left on top?',
             code='''STOP = {"the", "was", "is", "my", "today", "why", "please"}
counts = {"was": 200000, "the": 166921, "loved": 33570, "dosa": 33566, "chai": 33431, "cold": 8452, "my": 33079}
useful = {w: c for w, c in counts.items() if w not in STOP}
print(sorted(useful.items(), key=lambda x: -x[1]))
'''),
        dict(label='4 · A task fails', hint='Simulate the killed map: attempt 0 crashes halfway, attempt 1 redoes the whole split. Check that partial output of the failed attempt is never counted.',
             code='''split = ["the chai was hot", "the dosa was cold", "the chai was late"]
committed = None
for attempt in range(4):                    # mapreduce.map.maxattempts = 4
    out = []
    for i, line in enumerate(split):
        if attempt == 0 and i == 2:
            print(f"attempt {attempt}: killed after {len(out)} pairs -> output discarded")
            break
        out += [(w, 1) for w in line.split()]
    else:
        committed = out
        print(f"attempt {attempt}: SUCCEEDED with {len(out)} pairs")
        break
print(sum(1 for w, _ in committed if w == "chai"), "x chai")
'''),
        dict(label='5 · Spot the error', hint='This driver-like code reads the two paths from args, but the user passed <code>-D mapreduce.job.reduces=2</code> first. Fix it so options are removed before reading the paths (what GenericOptionsParser does).',
             code='''args = ["-D", "mapreduce.job.reduces=2", "/data/feedback.txt", "/out/wc"]
input_path, output_path = args[0], args[1]
if not input_path.startswith("/"):
    raise ValueError("input path looks wrong: " + input_path)
print(input_path, output_path)
''', expect='error'),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run it on your PC: build, run and break word count',
    intro='<p>Use the Module 8 lab from Lesson 8.1. Create <code>feedback.txt</code> with <code>make_feedback.py</code>, copy it and <code>WordCount.java</code> into the namenode container, put the text into HDFS, then run <code>wordcount_lab.sh</code> inside the container. <code>kill_task.sh</code> runs on your PC because it needs <code>docker exec</code> into a worker.</p>',
    items=[
        dict(title='Compile, package, run, read, fail', file='WordCount.java',
             cmd=rd('java/WordCount.java') + '\n// ---- make_feedback.py (run on your PC) ----\n' + '\n'.join('// ' + l for l in rd('make_feedback.py').strip().split('\n')) + '\n\n// ---- wordcount_lab.sh (inside the namenode container) ----\n' + '\n'.join('// ' + l for l in rd('wordcount_lab.sh').strip().split('\n')) + '\n\n// In the mr-lab folder:\n//   python3 make_feedback.py\n//   docker cp feedback.txt lab8-namenode-1:/tmp/mr/\n//   docker cp WordCount.java lab8-namenode-1:/tmp/mr/\n//   docker cp wordcount_lab.sh lab8-namenode-1:/tmp/mr/\n//   docker exec lab8-namenode-1 hdfs dfs -put feedback.txt /user/hadoop/data/   (run from /tmp/mr)\n//   docker exec lab8-namenode-1 bash /tmp/mr/wordcount_lab.sh',
             output=rd('tx86.txt').strip(),
             note='Real output; only the timestamp prefix of each log line was removed by the script. Section 4 lists two applications because the job had been run once before; yours shows one.'),
        dict(title='Kill a running map task', file='kill_task.sh',
             cmd=rd('kill_task.sh') + '\n# Needs attempts.sh (Lesson 8.1) in /tmp/mr in the namenode container.\n# Run on your PC, in the mr-lab folder:  bash kill_task.sh',
             output=rd('tx86k.txt').strip(),
             note='Real output. The killed attempt _0 is reported FAILED (exit code 137); _1 succeeded on worker3; _2 was a speculative copy, killed when _1 won. Which worker and which map you hit will differ.'),
    ],
)

TRACE = dict(
    heading='Tokenizing one feedback line',
    intro='<p>Follow how the tokenizer turns a line with capitals and punctuation into clean words. This is the only logic in the mapper.</p>',
    code='''line = "Why is the CHAI cold?"
clean = line.lower().replace("?", " ")
words = clean.split()
for w in words:
    print((w, 1))
''',
    notes={2: 'Lowercase :: “CHAI” becomes “chai” and the “?” becomes a space, like a delimiter in StringTokenizer.',
           3: 'Split :: The line breaks into words at every delimiter.',
           5: 'Emit :: In Java this is context.write(word, ONE).'},
)

WORKED_INTRO = 'Three end-to-end problems: sizing the shuffle, reading counters after a failure, and planning reruns.'
EXAMPLES = [
    dict(level='b', tag='Counters · shuffle', title='How much data did the shuffle move?',
         problem='<p>Our job had 1,033,238 map output records and 9,226,914 map output bytes. Map output materialized bytes were 11,293,396. How many bytes per record were shuffled, and what is the extra over the raw bytes?</p>',
         inp='1,033,238 records · 9,226,914 bytes · 11,293,396 materialized',
         approach=['Divide materialized bytes by records.',
                   'Compare with raw map output bytes.',
                   'The extra is per-record framing (key and value lengths) and partition data.'],
         code='''records, raw, mat = 1033238, 9226914, 11293396
print(f"{mat / records:.1f} bytes per record shuffled, {raw / records:.1f} raw")
print(f"framing overhead: {mat - raw:,} bytes ({(mat - raw) / records:.1f} per record)")
''', notes={2: 'Per record :: A word plus an IntWritable 1, plus lengths.'},
         tryit='Only 31 different words were shuffled as over 10 lakh records. Lesson 9.1\'s combiner sums the ones inside each map task first, so far fewer records travel.'),
    dict(level='i', tag='Failures · counters', title='Read the counters after a failure',
         problem='<p>The 20× job had 3 splits. Counters: Launched map tasks=5, Failed map tasks=1, Data-local map tasks=3. Attempts: one FAILED, one KILLED by speculation. Explain why 5 launches for 3 maps, and how many map outputs the reducer used.</p>',
         inp='3 splits · 5 launched · 1 failed · 1 killed',
         approach=['Successful attempts = number of maps (one each).',
                   'Extra launches = failed + killed attempts.',
                   'The reducer fetches only from successful attempts.'],
         code='''splits, launched, failed, killed = 3, 5, 1, 1
print("extra attempts:", launched - splits, "=", failed, "failed +", killed, "killed")
print("map outputs used by the reducer:", splits)
''', notes={2: 'Attempts :: Every retry or speculative copy is another launch.'},
         tryit='Data-local map tasks=3 counts the three first attempts placed next to their blocks; the retry and the speculative copy were not counted as data-local launches.'),
    dict(level='a', tag='Operations · reruns', title='Make a daily job safe to rerun',
         problem='<p>A daily word count writes to <code>/out/wc</code>. It fails with FileAlreadyExistsException on day 2. Design output paths so that every day has its own folder, reruns of the same day are explicit, and the driver can check before submitting.</p>',
         inp='dates · existing folders',
         approach=['Use a dated path: /out/wc/dt=YYYY-MM-DD.',
                   'If it exists with _SUCCESS, skip; if it exists without _SUCCESS, it is a failed run: remove and rerun.',
                   'Simulate the decision for three days.'],
         code='''existing = {"/out/wc/dt=2026-10-19": ["_SUCCESS", "part-r-00000"],
            "/out/wc/dt=2026-10-20": ["_temporary"]}
for day in ["2026-10-19", "2026-10-20", "2026-10-21"]:
    path = f"/out/wc/dt={day}"
    files = existing.get(path)
    if files is None:            action = "run"
    elif "_SUCCESS" in files:    action = "skip (already done)"
    else:                        action = "delete half-written folder, then run"
    print(path, "->", action)
''', notes={6: 'Marker :: _SUCCESS is written only after every reducer committed.'},
         tryit='This is how schedulers like Airflow and Oozie make Hadoop jobs idempotent.'),
]

QUIZ = mix([
    dict(q='What does job.setJarByClass(WordCount.class) do?', options=['Compiles the class', 'Tells Hadoop which jar contains the job, so it can be shipped to the tasks', 'Sets the output format', 'Starts the ResourceManager'], answer=1,
         why='The jar is copied to the staging directory and localized on every task node.'),
    dict(q='Why must TokenizerMapper be a static nested class?', options=['For speed', 'Hadoop creates it by reflection without an outer WordCount object', 'Static classes use less memory on disk', 'The old API requires it'], answer=1,
         why='A non-static inner class needs an instance of the outer class, which Hadoop cannot supply.'),
    dict(q='What does GenericOptionsParser do?', options=['Parses the input file', 'Applies options like -D key=value to the Configuration and returns the remaining arguments', 'Checks the Java version', 'Validates the output path'], answer=1,
         why='rest[0] and rest[1] are then the input and output paths.'),
    dict(q='Which runs the job\'s tasks\' bookkeeping on YARN?', options=['The NameNode', 'The MRAppMaster, one per job', 'The client', 'The JobHistory Server'], answer=1,
         why='The ResourceManager only hands out containers; the AM manages the job.'),
    dict(q='Running the job again into /out/wc gave which error?', options=['InvalidInputException', 'FileAlreadyExistsException: Output directory … already exists', 'ClassNotFoundException', 'Exit code 137'], answer=1,
         why='Hadoop refuses to overwrite output; the check happens before submission.'),
    dict(q='What does exit code 137 mean for a task container?', options=['Out of disk', 'The process was killed with SIGKILL (128 + 9)', 'Wrong input format', 'The job succeeded'], answer=1,
         why='We sent kill -9; YARN also kills containers that exceed memory limits.'),
    dict(q='After map 0 failed, what happened?', options=['The job failed', 'A new attempt reran the whole split on another worker and the job succeeded', 'The reducer skipped that split', 'The other maps restarted too'], answer=1,
         why='attempt _1 SUCCEEDED on worker3; up to 4 attempts are allowed by default.'),
    dict(q='Why is part-r-00000 sorted alphabetically and not by count?', options=['The reducer sorts its output by value', 'The shuffle sorts by key; the reducer writes keys in that order', 'HDFS sorts files', 'TextOutputFormat sorts lines'], answer=1,
         why='Sorting by count needs a second step (e.g. sort -k2,2nr, or a second job).'),
])

REVISION = [
    'A job = <b>Mapper</b> + <b>Reducer</b> + <b>driver</b>; nested classes must be <code>static</code>; mapper output types = reducer input types.',
    'Build: <code>javac -cp $(hadoop classpath)</code> → <code>jar cf wc.jar</code>; run: <code>hadoop jar wc.jar WordCount in out</code>; <code>-D key=value</code> via GenericOptionsParser/ToolRunner.',
    'Submission: output check → splits → staging dir in HDFS → RM → <b>MRAppMaster</b> container → task containers (YarnChild JVMs).',
    'Lab: 2 lakh lines → 1,033,238 pairs → 31 words; top: was 200000, the 166921.',
    'Errors before start: FileAlreadyExistsException (output exists), InvalidInputException (input missing).',
    'Failure: kill -9 → exit code 137 → attempt FAILED → rerun elsewhere (max 4 attempts); same counts.',
    'New API <code>org.apache.hadoop.mapreduce</code> (Context, Iterable) vs old <code>mapred</code> (OutputCollector, Reporter, JobConf).',
    'UIs: ResourceManager :8088 while running, JobHistory :19888 after; <code>yarn logs -applicationId</code> for task logs.',
]
FAQ = [
    ('How do you run a MapReduce program in Hadoop?', 'Compile the Java classes against the Hadoop libraries (javac -cp $(hadoop classpath)), package them into a jar (jar cf app.jar ...), make sure the input is in HDFS and the output folder does not exist, then run hadoop jar app.jar MainClass &lt;input&gt; &lt;output&gt;. Progress and counters are printed in the terminal; the result is in the output folder as part-r-NNNNN files.'),
    ('What happens when you submit a MapReduce job to YARN?', 'The client checks the output path, computes input splits and uploads the jar, job.xml and split files to a staging directory in HDFS, then submits an application to the ResourceManager. The RM launches the MRAppMaster in a container; the AM requests containers for map and reduce tasks, NodeManagers launch them, the AM tracks progress and failures, and on success commits the output and passes the job history to the JobHistory Server.'),
    ('What is the difference between the mapred and mapreduce APIs?', 'org.apache.hadoop.mapred is the original (old) API with Mapper and Reducer interfaces, OutputCollector, Reporter and JobConf. org.apache.hadoop.mapreduce is the newer API with abstract Mapper and Reducer classes, a Context object, Iterable values, setup/cleanup methods and the Job class. Both still work; new code should use org.apache.hadoop.mapreduce and never mix classes from the two.'),
    ('What happens if a map task fails in Hadoop?', 'The MRAppMaster notices the failed attempt (an exception, a non-zero container exit code, or no progress for mapreduce.task.timeout) and schedules a new attempt, preferably on another node. A task may be attempted mapreduce.map.maxattempts times (4 by default) before the job fails. Output of failed attempts is discarded, so results are not affected.'),
    ('Why does my job fail with “Output directory already exists”?', 'FileOutputFormat refuses to write into an existing directory so a job never overwrites earlier results by accident. Delete the folder with hdfs dfs -rm -r, or better, write each run to a new path such as a dated folder.'),
]

PRACTICE_INTRO = 'Word count exercises using the real counters and output from our lab.'
PROBLEMS = [
    dict(level='easy', title='Words per line', stmt='2,00,000 lines produced 1,033,238 map output records. How many words per line on average?', inp='1,033,238 / 200,000',
         code='''print(round(1033238 / 200000, 2), "words per line")
''', explain='About 5.17 words per line, matching lines like “the idli was fresh” (4) and “today the poha was crispy” (5).'),
    dict(level='easy', title='Scale check after a failure', stmt='The 20× run gave chai 668620 and was 4000000. Check both against 20 × the small run.', inp='chai 33431 · was 200000',
         code='''print(33431 * 20 == 668620, 200000 * 20 == 4000000)
''', explain='True, True: the killed attempt left no trace in the answer.'),
    dict(level='easy', title='Exit codes', stmt='Decode exit code 137 and 143 for a container (128 + signal number).', inp='137 · 143',
         code='''for code in (137, 143):
    sig = code - 128
    print(code, "-> signal", sig, {9: "SIGKILL", 15: "SIGTERM"}[sig])
''', explain='137 = SIGKILL (kill -9, or YARN killing a container over its memory limit); 143 = SIGTERM (a polite stop request, e.g. when YARN stops a container it no longer needs).'),
    dict(level='medium', title='Good vs bad words', stmt='Using real counts, compute the share of feedback words that are positive.', inp='8 good words · 7 bad words',
         code='''good = {"tasty": 17338, "hot": 17294, "fresh": 17426, "crispy": 17585, "perfect": 17706, "good": 17616, "nice": 17485, "amazing": 17687}
bad = {"cold": 8452, "late": 8792, "oily": 8444, "salty": 8541, "costly": 8410, "stale": 8617, "slow": 8607}
g, b = sum(good.values()), sum(bad.values())
print(g, b, f"{g / (g + b):.1%} positive")
''', explain='140,137 good vs 59,863 bad: about 70% positive, matching the 0.7 probability used in make_feedback.py.'),
    dict(level='medium', title='Join the two-word item', stmt='“vada pav” is split into “vada” and “pav”. Write a tokenizer that keeps known two-word phrases together.', inp='one line',
         code='''PHRASES = {"vada pav"}
def tokens(line):
    w = line.lower().split()
    out, i = [], 0
    while i < len(w):
        if i + 1 < len(w) and w[i] + " " + w[i + 1] in PHRASES:
            out.append(w[i] + " " + w[i + 1]); i += 2
        else:
            out.append(w[i]); i += 1
    return out
print(tokens("loved the vada pav was tasty"))
''', explain='Mapper logic decides what a “word” is; Hadoop just counts whatever keys you emit.'),
    dict(level='medium', title='How many reducers\' files?', stmt='The same job is run with -D mapreduce.job.reduces=4. How many part files, and can one word appear in two of them?', inp='4 reducers · 31 words',
         code='''print(4, "part-r files: part-r-00000 .. part-r-00003")
print("each word goes to exactly one reducer: (hash(word) & MAX) % 4")
''', explain='4 files; a word never appears in two files, because the partitioner sends every pair of one key to the same reducer (Lesson 8.5).'),
    dict(level='business', title='Retry cost', stmt='A nightly job has 2,000 map tasks of 60 s each. 1% of attempts fail once and are rerun. How much extra cluster time does that cost, and is it worth fixing?', inp='2,000 tasks · 60 s · 1% retries',
         code='''extra = 2000 * 0.01 * 60
print(f"{extra / 60:.0f} extra task-minutes per night ({extra / (2000 * 60):.0%} of the job)")
''', explain='20 task-minutes, 1% overhead: retries are cheap insurance. Fix the cause only if failures cluster on one node or grow.'),
    dict(level='advanced', title='Word count with a combiner (preview)', stmt='Simulate 3 map tasks; each first sums its own (word, 1) pairs (a combiner) before the shuffle. Count shuffled records with and without the combiner.', inp='3 splits',
         code='''splits = [["the chai was hot", "the chai was cold"], ["the dosa was hot"], ["the chai was late", "the idli was hot"]]
plain = combined = 0
for split in splits:
    words = [w for line in split for w in line.split()]
    plain += len(words)
    combined += len(set(words))
print("shuffled without combiner:", plain, "| with combiner:", combined)
''', explain='20 vs 15 here; on our real job 1,033,238 records would shrink to at most 31 per map task. That is Lesson 9.1.'),
]

SCN_INTRO = 'Interviewers love asking you to walk through a job end to end, and what happens when it breaks.'
SCENARIOS = '''    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Concepts · flow</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“What happens after you type hadoop jar?”</h4>
      <p class="scn__situation">A favourite follow-up after word count.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> the YARN execution flow.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>The driver configures a Job; the client checks the output path, computes splits and uploads jar, job.xml and splits to the HDFS staging directory.</li>
          <li>The ResourceManager starts the MRAppMaster in a container; the AM requests containers for maps (near their data) and reducers.</li>
          <li>NodeManagers launch task JVMs; maps run, shuffle, reducers write part files; the committer writes _SUCCESS; history goes to the JobHistory Server.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Debugging · errors</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>Job fails with ClassNotFoundException: WordCount$TokenizerMapper</h4>
      <p class="scn__situation">It ran fine in local mode but fails on the cluster.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> how code reaches the tasks.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>The tasks run on other machines and only see what is in the job jar: check that setJarByClass is called and the jar contains the $ classes (jar tf).</li>
          <li>Third-party libraries must be shipped too: -libjars (with ToolRunner), a fat jar, or the distributed cache.</li>
          <li>Make sure nested Mapper/Reducer classes are public static.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Operations · failures</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>Map tasks keep failing with exit code 137 on a big input</h4>
      <p class="scn__situation">Nobody is running kill -9. The job eventually fails after 4 attempts.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> container memory limits.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>137 means SIGKILL; YARN kills containers that exceed their memory (“running beyond physical memory limits” in the diagnostics), or the OS OOM killer does.</li>
          <li>Check yarn logs and the attempt diagnostics; raise mapreduce.map.memory.mb and keep mapreduce.map.java.opts (-Xmx) at about 80% of it.</li>
          <li>Also look for a mapper that holds too much in memory (big HashMaps) and fix the code.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Design · pipelines</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>“Top 10 words by count” with MapReduce</h4>
      <p class="scn__situation">Word count output is sorted by word, not count.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> chaining jobs.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Job 1: word count. Job 2: each map keeps a local top 10 (counts are already final per word) and one reducer merges them.</li>
          <li>Or swap key and value in job 2 and sort counts in descending order with a custom comparator and one reducer.</li>
          <li>For small outputs like our 31 lines, hdfs dfs -cat | sort -k2,2nr | head is enough.</li>
        </ul>
      </div></details>
    </article>
'''
