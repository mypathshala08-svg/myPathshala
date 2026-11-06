import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()
def has(n, *keys):
    return '\n'.join(l for l in capf(n).split('\n') if any(k in l for k in keys))
CK = capf('l33_ckpt.txt')
def sec(a, b=None):
    i = CK.index(a); j = CK.index(b, i) if b else len(CK)
    return CK[i:j].rstrip()
FILES = re.sub(r"files: \[.*\] … (\d+) files", lambda m: f"files: <ckpt>/<uuid>/rdd-62/part-00000 … part-00033  ({m.group(1)} files)", sec('checkpoint() called', '== 2)'))
FILES = re.sub(r'<ckpt>/[0-9a-f-]{36}/', '<ckpt>/<uuid>/', FILES).replace('/root/lab/spark/jobs/m3/', '')

def opbox(x, y, label, sub='', tone='card', w=128, h=26):
    o = box(x, y, w, h, tone) + t(x + w / 2, y + (11 if sub else 16), label, 7.2, 'ink', bold=True)
    if sub:
        o += t(x + w / 2, y + 21, sub, 6.4, 'ink2', mono=True)
    return o

def chain(n=6, cut=None, hi=None):
    """a lineage chain; optionally cut by a checkpoint"""
    o = ''
    for k in range(n):
        x = 8 + k * 58
        tone = 'card' if (cut is not None and k < cut) else ('acc' if k == hi else 'blue')
        o += opbox(x, 40, f'RDD {k}', 'ckpt' if cut is not None and k == cut else '', tone, 50, 26)
        if k:
            o += arrow(x - 8, 53, x, 53, 'ink3', 1.1)
    if cut is not None:
        o += f'<line x1="{8 + cut * 58 - 4}" y1="30" x2="{8 + cut * 58 - 4}" y2="76" stroke="#D64545" stroke-width="2" stroke-dasharray="4 3"/>'
        o += opbox(8 + cut * 58 - 20, 86, 'reliable storage', 'HDFS · S3 · shared disk', 'violet', 130, 28)
    return o

# ---------------------------------------------------------------- story
sc = (chain(6, 4) +
      box(410, 12, 222, 136, 'card') + t(521, 30, 'Measured', 8.6, bold=True) +
      ''.join(t(422, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
          ('30 unions: lineage 92 lines', 'amber'), ('after checkpoint: 2 lines', 'green'), ('no cache: computed twice', 'red'),
          ('400-step plan: 9.9 s → 5.7 s', 'green'), ('worker lost, cache: +200,000 calls', 'amber'), ('worker lost, checkpoint: +0', 'green')])))
scene_svg = scene('Checkpointing saves an RDD or DataFrame to reliable storage and cuts its lineage, so it no longer needs to be recomputed from its sources. We compared cache and checkpoint when a worker disappeared mid-job.', sc,
                  'Cache is <tspan font-weight="700" class="s-acc">fast but fragile</tspan>; a checkpoint is <tspan font-weight="700" class="s-acc">slower but durable</tspan>.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“The lost worker took two hours with it”</h2>
  <div class="story">
    <p class="narration">TiffinGo’s fraud model scores every order with an expensive Python function, then joins the scores with ten other datasets. One night a cloud node was reclaimed during the joins. The cached scores on that node vanished and Spark quietly recomputed them: the job finished, two hours late.</p>

{scene_svg}

K> Sir, Spark recovered. Isn’t that what fault tolerance means?
A> It is. Spark rebuilds lost partitions from their <b>lineage</b>, as we saw in Lessons 1.3 and 2.3. But if rebuilding means re-running expensive work, or the lineage has grown very long, recovery is slow. A <b>checkpoint</b> writes the data to reliable storage and cuts the lineage there.
R> So should we checkpoint instead of caching?
A> They solve different problems, and a checkpoint has its own costs. Today we grow a lineage until it is long, checkpoint it, count how often the work runs, speed up a 400-step DataFrame, and stop a worker to compare cache with checkpoint. All outputs are real (Spark 4.3.0).
  </div>
</section>
'''

lv = '''
LEVELS> Checkpointing at three levels
L1> Saving your game
      <ul>
        <li>Lineage is the list of moves from the start of the game; if you lose, you replay every move.</li>
        <li>A cache is a quick save in memory: fast, but lost if the machine restarts.</li>
        <li>A checkpoint is a save to the cloud: slower to make, but you restart from there, not from the beginning.</li>
      </ul>
L2> The API
      <ul>
        <li><code>sc.setCheckpointDir(path)</code> on reliable storage (HDFS, S3, shared disk), then <code>rdd.checkpoint()</code> or <code>df.checkpoint()</code>.</li>
        <li>RDD checkpoints are lazy and run as an <b>extra job</b> after the first action, recomputing the RDD unless it is cached. DataFrame <code>checkpoint()</code> is eager by default and returns a new DataFrame.</li>
        <li><code>localCheckpoint()</code> cuts lineage using executor storage only: fast, but not fault tolerant.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>30 unions grew a lineage to 92 lines; after a checkpoint, 2 lines pointing at a <code>ReliableCheckpointRDD</code> of 34 files.</li>
        <li>Without cache, checkpointing ran the work function 20,000 times for 10,000 elements; with cache 10,000.</li>
        <li>After a worker was stopped, a cached RDD recomputed 200,000 expensive calls; a checkpointed one recomputed <b>none</b> and answered in 0.8 s.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Checkpointing and Spark’s fault tolerance</h2>
''' + def_block(
    'Spark achieves <b>fault tolerance</b> mainly through lineage: failed tasks are retried (up to <code>spark.task.maxFailures</code>, 4 by default), lost shuffle outputs and cached partitions are recomputed from their parent RDDs. <b>Checkpointing</b> saves the partitions of an RDD or DataFrame to files in a reliable checkpoint directory and replaces its lineage with a reference to those files, so later recovery reads the files instead of recomputing the chain. Reliable checkpoints of RDDs are lazy: they are written by an additional job after the first action, which recomputes the RDD unless it is persisted. <b>Local checkpoints</b> truncate lineage using executor-local storage and therefore do not survive executor loss. Checkpointing is used for very long lineages (iterative algorithms, loops of unions or joins), for expensive results that must survive failures, and in Structured Streaming to store progress and state.',
    'Spark recovers from failures by redoing lost work using lineage. A checkpoint saves data to safe storage and forgets the lineage, so recovery reads the saved files instead of redoing everything. It costs an extra write, so use it when lineages are long or recomputing is expensive.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Checkpoint directory', '<code>sc.setCheckpointDir()</code>: reliable storage for checkpoints.'),
    ('checkpoint()', 'Save to the checkpoint dir and cut the lineage.'),
    ('ReliableCheckpointRDD', 'What a checkpointed RDD reads from afterwards.'),
    ('localCheckpoint()', 'Cut lineage using executor storage (not fault tolerant).'),
    ('Task retry', 'A failed task is re-run, up to spark.task.maxFailures times.'),
    ('Stage retry', 'Map stages re-run when their shuffle output is lost.'),
    ('Eager checkpoint', 'DataFrame checkpoint(eager=True) runs immediately.'),
    ('Speculation', 'Optional: start copies of slow tasks elsewhere.'),
]) + '''

  <h3>Cache, checkpoint or local checkpoint?</h3>
''' + table(['', 'cache() / persist()', 'checkpoint()', 'localCheckpoint()'], [
    ['Stored in', 'Executor memory / local disk', 'Reliable storage (HDFS, S3, shared)', 'Executor storage'],
    ['Lineage', 'Kept', 'Cut', 'Cut'],
    ['After executor loss', 'Recomputed from lineage', 'Read from files', 'Lost: job fails'],
    ['Cost', 'Fill once (memory)', 'Extra write job (recompute unless cached)', 'Like a cache'],
    ['Lives until', 'Application ends / unpersist', 'Files deleted', 'Application ends'],
    ['Lab', '+200,000 calls after worker loss', '+0 calls, 0.8 s', 'lineage cut, 0 files'],
], minw=740) + lv + '''
EXAM> “Cache vs checkpoint?” Cache keeps data on executors and keeps the lineage; it is fast but lost with the executor and recomputed from lineage. Checkpoint writes to reliable storage and truncates the lineage; it costs a write but survives failures and stops lineages from growing. Cache before checkpointing an RDD to avoid computing it twice.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Fault-tolerance mechanisms in Spark</h2>
''' + table(['Failure', 'What Spark does', 'Seen in this course'], [
    ['A task throws an error', 'Retries it up to 4 times (spark.task.maxFailures)', 'Lesson 3.2: flaky task succeeded on retry'],
    ['An executor or worker dies', 'Re-runs its tasks elsewhere; recomputes lost shuffle files and cached blocks', 'Lesson 1.3 and Step 6 here'],
    ['Shuffle files unreachable', 'FetchFailed → re-runs the map stage', 'Lesson 1.3 (77 s stall)'],
    ['Task much slower than others', 'Optional speculative copy (spark.speculation)', '—'],
    ['Driver dies', 'Application fails (cluster mode can restart it on some managers)', 'Lesson 1.3'],
    ['Streaming query restarts', 'Resumes from checkpointed offsets and state', 'Module 9'],
], minw=720) + '''
WARN> A checkpoint is not a backup or a table. Files in the checkpoint directory are written in Spark’s internal format for this application; they are not meant to be read by other jobs and are not cleaned up automatically by default (<code>spark.cleaner.referenceTracking.cleanCheckpoints</code> is false). Put the directory on reliable storage, give it a lifecycle rule, and write real outputs as tables.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Long lineages, checkpoints and a lost worker</h2>
  <p>All outputs are real: PySpark 4.3.0 in local mode (Steps 1–5) and on our standalone cluster with a checkpoint directory on storage shared by all containers (Step 6).</p>
''' + stepper([
    ('Step 1 · Watching a lineage grow',
     code('python', 'ckpt.py', "r = sc.parallelize(range(100_000), 4).map(lambda x: (x % 100, 1))\nfor i in range(30):\n    r = r.mapValues(lambda v: v + 1)\nprint(len(r.toDebugString().decode().splitlines()))\n\nday = sc.parallelize([(0, 1)], 1)\nfor i in range(30):                      # append one small batch per day\n    r = r.union(day)\nprint(len(r.toDebugString().decode().splitlines()), r.getNumPartitions())", sec('30 x mapValues', 'checkpoint() called')),
     'Thirty <code>mapValues</code> did not grow the lineage at all: PySpark fused them into one Python step (Lesson 2.3). Thirty <code>union</code>s did: <b>92 lines</b> and 34 partitions. Loops that union, join or reduce in every iteration (daily appends, graph algorithms, iterative ML) grow lineages like this. Long lineages make scheduling slower and recovery expensive.'),
    ('Step 2 · Checkpoint: lazy, then cut',
     code('python', 'ckpt.py', 'sc.setCheckpointDir("/root/lab/spark/data/ckpt")\nr.checkpoint()\nprint(r.isCheckpointed())\nr.count()\nprint(r.isCheckpointed(), r.getCheckpointFile())\nprint(r.toDebugString().decode())', FILES),
     '<code>checkpoint()</code> only marked the RDD. The next action computed it and wrote <b>one file per partition</b> (34) into a sub-folder with a random id for this SparkContext. The lineage now ends at a <code>ReliableCheckpointRDD</code>: 92 lines became 2. Any later action or recovery reads those files.'),
    ('Step 3 · A checkpoint computes the RDD twice, unless cached',
     code('python', 'ckpt.py', 'calls = sc.accumulator(0)\ndef work(x):\n    calls.add(1); return x * 2\na = sc.parallelize(range(10_000), 4).map(work); a.checkpoint(); a.count()\nb = sc.parallelize(range(10_000), 4).map(work).cache(); b.checkpoint(); b.count()', sec('no cache', '== 3)')),
     'The action computed the RDD once for <code>count()</code>, then Spark started a <b>separate job</b> to write the checkpoint and computed it again: 20,000 calls for 10,000 elements. With <code>cache()</code> first, the checkpoint job read the cached partitions: 10,000 calls. The documentation’s advice, confirmed: persist an RDD before checkpointing it.'),
    ('Step 4 · localCheckpoint: fast, but not safe',
     code('python', 'ckpt.py', 'c = sc.parallelize(range(1000), 2).map(lambda x: x + 1)\nc.localCheckpoint(); c.count()\nprint(c.toDebugString().decode())', sec('lineage: (2)', '== 4)')),
     'The lineage was cut, but <b>no files</b> were written: the data sits in executor storage with a disk-and-memory level. Good for cutting very long lineages in iterative algorithms when speed matters more than surviving executor loss; if an executor dies, its locally checkpointed partitions cannot be rebuilt and the job fails.'),
    ('Step 5 · A DataFrame built in a loop',
     code('python', 'ckpt.py', "def build(n, ck_every=None):\n    df = spark.range(200_000).withColumn(\"v\", F.lit(0))\n    for i in range(n):\n        df = df.withColumn(\"v\", F.col(\"v\") + F.col(\"id\") % 7)\n        if ck_every and (i + 1) % ck_every == 0:\n            df = df.checkpoint()          # eager: writes now, returns a new DataFrame\n    return df", sec('100 steps')),
     'Each <code>withColumn</code> added a node to the logical plan: 400 steps meant a 402-line plan that Catalyst had to analyse and optimise again and again, <b>9.9 s</b> in total. Checkpointing every 50 steps kept the plan at one line (a scan of the checkpoint) and took <b>5.7 s</b>, writes included. For small loops the checkpoint was not worth it; that is why it is a tool for long chains, not a habit.'),
    ('Step 6 · A worker dies: cache vs checkpoint',
     code('python', 'ckpt_failover.py (cluster, run twice)', "sc.setCheckpointDir(\"/data/ckpt_cluster\")          # shared by all containers\ncalls = sc.accumulator(0)\nr = sc.parallelize(range(400_000), 8).map(expensive).cache()\nif mode == \"checkpoint\":\n    r.checkpoint()\nr.count()                         # 1st action\n# … docker stop sparklab-spark-worker-2-1 …\nr.count()                         # 2nd action, one executor fewer", capf('l33_fail_cache.txt') + '\n\n' + capf('l33_fail_checkpoint.txt')),
     'Both runs lost executor 0 with half of the cached partitions. The <b>cached-only</b> RDD rebuilt those 4 partitions from lineage: <b>200,000</b> extra calls to the expensive function. The <b>checkpointed</b> RDD read its files from shared storage: <b>0</b> extra calls, 0.8 s. The first run with a checkpoint was slower (7.8 s vs 6.4 s) because of the extra write. Pay that when recomputation is expensive or workers are unreliable.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('30 x mapValues -> 2 lines (fused)', G), ('+ 30 x union   -> 92 lines', Y), ('partitions: 34', W)], size=7.4),
    term([('checkpoint(); isCheckpointed: False', W), ('count(); isCheckpointed: True', G), ('UnionRDD → ReliableCheckpointRDD', G), ('34 part files', W)], size=7.2),
    term([('no cache  : work() calls = 20000', RD), ('with cache: work() calls = 10000', G)], size=7.6),
    term([('400 steps, no checkpoint : 9.9 s', Y), ('400 steps, every 50      : 5.7 s', G), ('plan lines 402 → 1', G)], size=7.4),
    term([('worker stopped', W), ('cache     : +200000 calls, 1.9 s', Y), ('checkpoint: +0 calls, 0.8 s', G)], size=7.6),
]
B1 = [
    t(180, 14, 'Lineage grows with each step', 9.4, bold=True) + chain(6, None, 5) + cap('Longer graph, costlier recovery.', '', 'amber', y=112, h=30),
    t(180, 14, 'Checkpoint cuts the chain', 9.4, bold=True) + chain(6, 4) + cap('Later reads start from the files.', '', 'green', y=124, h=30),
    t(180, 14, 'An extra job writes the files', 9.4, bold=True) + chain(6, 4) + cap('Cache first, or compute twice.', '', 'red', y=124, h=30),
    t(180, 14, 'Plans grow too', 9.4, bold=True) + chain(6, 4) + cap('A checkpoint resets the plan.', '', 'violet', y=124, h=30),
    t(180, 14, 'Recovery from files, not work', 9.4, bold=True) + chain(6, 4, 5) + cap('Lost executor, nothing recomputed.', '', 'green', y=124, h=30),
]
see_caps = ['Unions grew the lineage to 92 lines.',
            'After the first action, the lineage was 2 lines.',
            'Without cache, the work ran twice.',
            'Checkpointing kept a 400-step plan small.',
            'The checkpointed RDD survived the lost worker.']
behind_caps = ['Narrow Python steps fuse; unions and joins add nodes.',
               'Files in the checkpoint dir replace the parents.',
               'The checkpoint job recomputes unpersisted RDDs.',
               'Catalyst re-analyses long plans on every step.',
               'Cached blocks die with executors; files do not.']
two = anim_two('Checkpointing', 'Save the data, forget the past', 'Real lab outputs', 'The lineage', see, B1, see_caps, behind_caps)

# ---- scenario 1: spot nodes and expensive scores
e1 = (t(180, 22, 'Fraud scores take 2 hours', 9.4, bold=True) + t(180, 56, 'then joined with 10 datasets', 8.4, 'ink2') + cap('Cached, on spot nodes.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'A node is reclaimed', 9.4, bold=True) + t(180, 56, 'cached scores on it are lost', 8.4, 'ink2') + cap('Recomputed from lineage.', '', 'amber', y=150, h=34))
e3 = (t(180, 22, 'Checkpoint the scores', 9.4, bold=True) + t(180, 56, 'scores.cache(); scores.checkpoint()', 8.2, 'ink', mono=True) + cap('To S3 or HDFS.', '', 'green', y=150, h=34))
e4 = (t(180, 22, 'Next loss', 9.4, bold=True) + t(180, 56, 'read files, +0 scoring calls', 8.4, 'ink2') + cap('Like our Step 6.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Or write a table', 9.4, 'acc', bold=True) + t(180, 56, 'if other jobs need the scores', 8.4, 'ink2') + cap('Checkpoints are internal.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Expensive results on unreliable nodes',
              'Why checkpoints exist. (Typical; behaviour from our lab.)',
              'Durable intermediate results', 'Cached data dies with executors; checkpoint expensive results to reliable storage so recovery reads files instead of recomputing', [e1, e2, e3, e4, e5],
              ['Expensive step.', 'Node lost.', 'Checkpoint it.', 'Recovery is cheap.', 'Or a real table.'],
              hid='scenario-spot2')

# ---- scenario 2: iterative graph
b1 = (t(180, 22, 'Graph algorithm, 100 rounds', 9.4, bold=True) + t(180, 56, 'ranks = ranks.join(links)… each round', 8.2, 'ink', mono=True) + cap('Lineage grows every round.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Round 60: driver crawls', 9.4, bold=True) + t(180, 56, 'StackOverflowError on serialising', 8.4, 'ink', mono=True) + cap('A very deep DAG.', '', 'amber', y=150, h=34))
b3 = (t(180, 22, 'Checkpoint every 10 rounds', 9.4, bold=True) + t(180, 56, 'ranks.cache(); ranks.checkpoint()', 8.2, 'ink', mono=True) + cap('Lineage stays short.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'Or localCheckpoint', 9.4, bold=True) + t(180, 56, 'faster, not fault tolerant', 8.4, 'ink2') + cap('Acceptable for short jobs.', '', 'amber', y=150, h=34))
b5 = (t(180, 22, 'Stable run time per round', 9.4, 'acc', bold=True) + t(180, 56, 'like 9.9 s → 5.7 s in Step 5', 8.4, 'ink2') + cap('And safe recovery.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'An iterative job that slows down every round',
              'Lineage truncation in iterative algorithms. (Typical.)',
              'Long lineages', 'Iterations that join or union grow the lineage; periodic checkpoints keep scheduling and recovery fast', [b1, b2, b3, b4, b5],
              ['Many rounds.', 'Deep DAG.', 'Checkpoint periodically.', 'Or local.', 'Stable again.'],
              hid='scenario-iter')

# ---- scenario 3: checkpoint dir grows
u1 = (t(180, 22, 'Storage bill keeps rising', 9.4, bold=True) + t(180, 56, 's3://…/checkpoints: 40 TB', 8.4, 'ink', mono=True) + cap('Nobody deletes them.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Why', 9.4, bold=True) + t(180, 56, 'cleanCheckpoints is false by default', 8.4, 'ink2') + cap('Files outlive applications.', '', 'amber', y=150, h=34))
u3 = (t(180, 22, 'Per-run directories', 9.4, bold=True) + t(180, 56, 'checkpoints/&lt;job&gt;/&lt;run-date&gt;/', 8.4, 'ink', mono=True) + cap('Easy to clean.', '', 'green', y=150, h=34))
u4 = (t(180, 22, 'Lifecycle rule', 9.4, bold=True) + t(180, 56, 'delete after 7 days', 8.4, 'ink2') + cap('Bucket policy.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Except streaming', 9.4, 'acc', bold=True) + t(180, 56, 'never delete a live query’s checkpoint', 8.2, 'ink2') + cap('Module 9.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'The checkpoint folder nobody cleans',
              'Operating checkpoints in production. (Typical.)',
              'Checkpoint housekeeping', 'Batch checkpoints are not cleaned automatically; use per-run directories and lifecycle rules, but keep streaming checkpoints', [u1, u2, u3, u4, u5],
              ['Bill rises.', 'No automatic cleanup.', 'Per-run folders.', 'Lifecycle rule.', 'Not for streaming.'],
              hid='scenario-cleanup')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Save the data, forget the past</h2>
  <p>Left: real outputs. Right: what happens to the lineage.</p>
''' + two + '''
  <p>Three live scenarios follow: expensive results on spot nodes, an iterative graph job, and a growing checkpoint folder.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Checkpoints at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'graphs', 11, 'blue', bold=True) + t(60, 58, 'iterations', 7.4, 'ink2'),
    '1. Iterative algorithms',
    'PageRank-style and connected-component jobs checkpoint every few iterations to keep lineage short.',
    ['Round n', '*checkpoint', 'Round n+1']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'ML', 12, 'green', bold=True) + t(60, 58, 'features', 7.4, 'ink2'),
    '2. Expensive feature steps',
    'Costly feature computations are cached and checkpointed before long training or joining phases.',
    ['Features', '*checkpoint', 'Training']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'stream', 11, 'violet', bold=True) + t(60, 58, 'state', 7.4, 'ink2'),
    '3. Streaming queries',
    'Every Structured Streaming query keeps offsets and state in a checkpoint location to restart exactly where it stopped.',
    ['Kafka', '*checkpoint', 'Restart safely']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'spot', 12, 'acc', bold=True) + t(60, 58, 'clusters', 7.4, 'ink2'),
    '4. Cheap, unreliable compute',
    'Jobs on spot instances checkpoint expensive intermediate results so reclaimed nodes cost minutes, not hours.',
    ['Spot loss', '*read files', 'Continue']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'plans', 11, 'acc', bold=True) + t(60, 58, 'loops', 7.4, 'ink2'),
    '5. DataFrame loops',
    'Code that builds DataFrames in loops checkpoints periodically to keep Catalyst’s plans small.',
    ['Loop', '*df.checkpoint()', 'Small plan']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> lineage in <a href="../../02-rdds/03-lazy-evaluation-and-the-dag/">2.3</a>, worker loss in <a href="../../01-introduction/03-spark-architecture/">1.3</a> and caching in <a href="../01-cache-and-persist/">3.1</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
