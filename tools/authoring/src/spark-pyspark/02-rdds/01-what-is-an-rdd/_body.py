import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return open(CAP + n).read().rstrip()
def sect(n, a, b=None):
    s = capf(n); i = s.index(a); j = s.index(b, i) if b else len(s)
    return s[i:j].rstrip()

def opbox(x, y, label, sub='', tone='card', w=128, h=26):
    o = box(x, y, w, h, tone) + t(x + w / 2, y + (11 if sub else 16), label, 7.2, 'ink', bold=True)
    if sub:
        o += t(x + w / 2, y + 21, sub, 6.4, 'ink2', mono=True)
    return o

def rdd(hi=-1, vals=('530 210', '480 990', '120 340'), title='amounts · 3 partitions', x0=20):
    o = box(x0, 26, 320, 64, 'card') + t(x0 + 160, 40, title, 7.6, 'ink2', bold=True)
    for k, v in enumerate(vals):
        o += opbox(x0 + 12 + k * 104, 48, f'partition {k}', v, 'acc' if k == hi else 'blue', 92, 30)
    return o

# ---------------------------------------------------------------- story
sc = (rdd(-1, title='RDD = list of partitions') + t(180, 110, 'on executors · immutable · rebuilt from lineage', 7.2, 'ink2') +
      box(410, 12, 222, 136, 'card') + t(521, 30, 'Five ways in, measured', 8.6, bold=True) +
      ''.join(t(422, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
          ('parallelize(list, 3) → 3 parts', 'ink'), ('textFile: 5,000 lines, 2 parts', 'ink'), ('wholeTextFiles: 3 files → 3', 'ink'),
          ('df.rdd → Row objects', 'ink'), ('same answer as DataFrame …', 'green'), ('… but 8× slower (30.2 s)', 'red')])))
scene_svg = scene('An RDD is a read-only collection split into partitions that live on executors. Spark records how each one was built, so it can rebuild lost partitions. We created RDDs five ways and compared them with DataFrames.', sc,
                  'An RDD is <tspan font-weight="700" class="s-acc">data in pieces</tspan> plus the recipe to rebuild them.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“If DataFrames exist, why learn RDDs?”</h2>
  <div class="story">
    <p class="narration">TiffinGo’s kitchen partners send messy text: order notes like <code>100001|Chole Bhature,Aloo Paratha|spice:medium</code>, raw review lines, whole files per month. Riya has learnt DataFrames, but Kabir found an old Spark job full of <code>sc.textFile</code> and <code>lambda</code>s that nobody understands.</p>

{scene_svg}

R> Sir, DataFrames are faster. Why does this old job use RDDs?
A> RDDs are <b>Spark’s foundation</b>. Every DataFrame runs on RDDs underneath, and when data has no schema (free text, odd formats) or you need full control, the RDD API is what you reach for. Every Spark interview asks about them, and every Spark UI you read shows them.
K> So what exactly is an RDD?
A> A <b>Resilient Distributed Dataset</b>: a read-only collection split into <b>partitions</b> spread over executors, with a record of how it was built. Today we create RDDs five ways, look inside the partitions, and race the same question against a DataFrame. All outputs are real, from PySpark 4.3.0.
  </div>
</section>
'''

lv = '''
LEVELS> RDDs at three levels
L1> A big box of order slips, split into trays
      <ul>
        <li>An RDD is like a pile of order slips split into <b>trays</b> (partitions), one tray per cook.</li>
        <li>You never write on the slips: every step makes a new pile (immutability).</li>
        <li>Each pile has a note saying how it was made, so a lost tray can be made again (lineage).</li>
      </ul>
L2> What makes an RDD
      <ul>
        <li><b>Resilient</b>: lost partitions are recomputed from lineage, not from replicas.</li>
        <li><b>Distributed</b>: partitions live on different executors and are processed in parallel.</li>
        <li><b>Dataset</b>: any Python objects (strings, tuples, dicts, Rows), no schema required.</li>
        <li>Create from a collection (<code>parallelize</code>), from files (<code>textFile</code>, <code>wholeTextFiles</code>) or from a DataFrame (<code>df.rdd</code>).</li>
      </ul>
L3> Inside, and what the lab showed
      <ul>
        <li>Every RDD has five properties: its partitions, a function to compute each partition, dependencies on parent RDDs, and optionally a partitioner and preferred locations.</li>
        <li><code>glom()</code> showed the six amounts split 2-2-2 over 3 partitions; <code>toDebugString()</code> showed the lineage.</li>
        <li>The same city revenue took 4.0 s as a DataFrame and 30.2 s as an RDD: Python lambdas, pickling and no Catalyst optimizer.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Resilient Distributed Dataset</h2>
''' + def_block(
    'A <b>Resilient Distributed Dataset (RDD)</b> is Spark’s fundamental data abstraction: an immutable, partitioned collection of elements that can be operated on in parallel. An RDD is defined by a list of <b>partitions</b>, a function for computing each partition, a list of <b>dependencies</b> on parent RDDs (its lineage), and optionally a <b>partitioner</b> for key-value RDDs and <b>preferred locations</b> for each partition. RDDs are created by parallelising a driver collection or by reading external storage, and transformed with coarse-grained operations; because the lineage is recorded, lost partitions can be recomputed. In PySpark the elements are arbitrary Python objects processed by Python worker processes; the higher-level DataFrame API is built on RDDs and is usually preferred because Catalyst can optimise it.',
    'An RDD is a collection of data split into pieces (partitions) on many machines. You cannot change it; you make new RDDs from it. Spark remembers how every RDD was made, so lost pieces can be rebuilt.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('RDD', 'Resilient Distributed Dataset.'),
    ('SparkContext (<code>sc</code>)', 'Entry point for RDDs: <code>spark.sparkContext</code>.'),
    ('Partition', 'One slice of an RDD, processed by one task.'),
    ('parallelize', 'Turns a driver list into an RDD.'),
    ('textFile', 'Reads files; one element per line.'),
    ('wholeTextFiles', 'Reads files; one element per file: (path, content).'),
    ('glom()', 'Turns each partition into a list, to see how data is split.'),
    ('Lineage', 'The chain of parent RDDs and operations; <code>toDebugString()</code>.'),
]) + '''

  <h3>RDD, DataFrame or Dataset?</h3>
''' + table(['', 'RDD', 'DataFrame', 'Dataset'], [
    ['Data', 'Any Python objects', 'Rows with named, typed columns', 'Typed objects (Scala/Java only)'],
    ['Schema', 'None', 'Yes', 'Yes'],
    ['Optimised by Catalyst', 'No', 'Yes', 'Yes'],
    ['Python code runs in', 'Python workers (pickling)', 'JVM, unless you use UDFs', '—'],
    ['Our lab: city revenue on 5 M rows', '30.2 s', '4.0 s', 'not available in PySpark'],
    ['Use for', 'Unstructured text, custom logic, low-level control', 'Almost everything else', 'Scala/Java type safety'],
], minw=720) + lv + '''
EXAM> “What is an RDD and what are its properties?” An immutable, partitioned, fault-tolerant collection processed in parallel. Defined by partitions, a compute function, dependencies (lineage), and optionally a partitioner and preferred locations. Fault tolerance comes from recomputing lost partitions using lineage.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Ways to create an RDD</h2>
''' + table(['Method', 'Element type', 'Partitions by default', 'Typical use'], [
    ['<code>sc.parallelize(list, n)</code>', 'Whatever is in the list', '<code>defaultParallelism</code> or n', 'Tests, small lookups, generated data'],
    ['<code>sc.textFile(path)</code>', 'One string per line', 'Based on file splits (at least 2 locally)', 'Logs, CSV-like text, free text'],
    ['<code>sc.wholeTextFiles(dir)</code>', '(path, whole content)', 'Based on files', 'Many small files, JSON/XML documents'],
    ['<code>df.rdd</code>', '<code>Row</code> objects', 'Same as the DataFrame', 'Custom logic on structured data'],
    ['<code>rdd.map(…)</code>, <code>filter</code>, …', 'New elements', 'Usually same as parent', 'Every transformation makes a new RDD'],
    ['<code>sc.emptyRDD()</code>, <code>sc.range()</code>', 'None / integers', '0 / chosen', 'Placeholders, generated keys'],
], minw=760) + '''
WARN> <code>parallelize</code> copies the list from the <b>driver</b> to the executors. It is fine for test data and small lookups, but never a way to load real data: the whole list must first fit in the driver’s memory. Read big data from storage with <code>textFile</code> or a DataFrame reader instead.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Five RDDs, looked at from inside</h2>
  <p>All outputs are real: PySpark 4.3.0, local mode with 2 cores. Data: TiffinGo’s <code>order_items.txt</code> (5,000 lines), three months of review text (24,000 lines in 3 files), <code>orders.csv</code> and <code>orders_big</code> (5,000,000 orders) from Module 1.</p>
''' + stepper([
    ('Step 1 · parallelize: a list becomes partitions',
     code('python', 'create.py', 'sc = spark.sparkContext\namounts = sc.parallelize([530, 210, 480, 990, 120, 340], 3)\nprint(amounts, "| partitions:", amounts.getNumPartitions())\nprint("glom():", amounts.glom().collect())', sect('l21_create.txt', '    ParallelCollectionRDD', '2)')),
     'We asked for 3 partitions and Spark split the six amounts 2-2-2. <code>glom()</code> is a debugging tool: it turns each partition into a list so you can see the split. The printed name <code>ParallelCollectionRDD[0]</code> is the RDD’s class and id; every new RDD gets the next id.'),
    ('Step 2 · textFile: one element per line',
     code('python', 'create.py', 'items = sc.textFile("order_items.txt")\nprint("partitions:", items.getNumPartitions(), "| lines:", items.count())\nprint("first():", items.first())\n\nreviews = sc.textFile("reviews")          # a folder of 3 files\nprint("partitions:", reviews.getNumPartitions(), "| lines:", reviews.count())', sect('l21_create.txt', '    partitions: 2', '4)').replace('3) textFile on a folder (3 files)\n', '')),
     'Each line is one string; Spark knows nothing about the <code>|</code> and <code>,</code> inside. A small file still gave <b>2</b> partitions (textFile’s default minimum is min(cores, 2)); a folder of 3 files gave 3, one per file. Paths can be local, <code>hdfs://</code>, <code>s3a://</code> or wildcards like <code>reviews/*.txt</code>.'),
    ('Step 3 · wholeTextFiles: one element per file',
     code('python', 'create.py', 'whole = sc.wholeTextFiles("reviews")\nprint(whole.count(), [(p.split("/")[-1], len(c)) for p, c in whole.collect()])', sect('l21_create.txt', '    elements: 3', '5)')),
     'Three elements, each a pair (path, entire content). Useful when a file must be parsed as a whole (a JSON or XML document per file) or when the file name carries information, such as the month here. Not for huge files: each file is one element in memory.'),
    ('Step 4 · From a DataFrame: Row objects',
     code('python', 'create.py', 'df = spark.read.csv("orders.csv", header=True)\nrows = df.rdd\nprint(type(rows.first()).__name__, rows.first()["city"], rows.first()["amount"])', sect('l21_create.txt', '    type of element', 'Immutability')),
     'Every DataFrame has an RDD of <code>Row</code> objects underneath. A Row behaves like a named tuple: <code>r["city"]</code> or <code>r.city</code>. Going from DataFrame to RDD is easy; it is also the moment Spark stops optimising your code (Step 6).'),
    ('Step 5 · Immutable, with a recorded lineage',
     code('python', 'create.py', 'big = amounts.filter(lambda a: a >= 300)\nprint("amounts:", amounts.collect())\nprint("big    :", big.collect(), "| same object?", big is amounts)\nprint(big.toDebugString().decode())', sect('l21_create.txt', '    amounts:')),
     'The filter did not change <code>amounts</code>; it returned a new RDD. <code>toDebugString()</code> shows the lineage: <code>big</code> (a <code>PythonRDD</code>, because a Python lambda computes it) depends on the original <code>ParallelCollectionRDD</code>; <code>(3)</code> is the number of partitions. If an executor holding a partition of <code>big</code> dies, Spark reruns the filter on that partition of <code>amounts</code>.'),
    ('Step 6 · The same question as RDD and DataFrame',
     code('python', 'rdd_vs_df.py', "df = spark.read.parquet(\"orders_big\")      # 5,000,000 orders\nres_df = (df.where(\"status = 'DELIVERED'\").groupBy(\"city\").agg(F.sum(\"amount\").alias(\"rev\"))\n            .orderBy(F.desc(\"rev\")).collect())\n\nres_rdd = (df.rdd.filter(lambda r: r.status == \"DELIVERED\")\n                 .map(lambda r: (r.city, r.amount))\n                 .reduceByKey(lambda a, b: a + b)\n                 .sortBy(lambda kv: -kv[1]).collect())", capf('l21_vs_df.txt')),
     'Identical answers; the RDD version took <b>8 times longer</b>. Each of the 5,000,000 rows was converted to a Python <code>Row</code>, sent to a Python worker, filtered and mapped there, and pickled back. The DataFrame version stayed in the JVM, read only the three columns it needed and used code generation. Rule of thumb: <b>DataFrames for structured data</b>, RDDs for what DataFrames cannot express.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('sc.parallelize([...], 3)', W), ('ParallelCollectionRDD[0]', W), ('glom(): [[530, 210], [480, 990],', G), ('        [120, 340]]', G)], size=7.4),
    term([('sc.textFile("order_items.txt")', W), ('partitions: 2 | lines: 5000', G), ('100001|Chole Bhature,Aloo …', Y)], size=7.4),
    term([('sc.wholeTextFiles("reviews")', W), ('elements: 3', G), ('(reviews_2026-09.txt, 302582 chars)', W)], size=7.2),
    term([('big = amounts.filter(a >= 300)', W), ('same object? False', G), ('(3) PythonRDD[30]', Y), (' |  ParallelCollectionRDD[0]', Y)], size=7.4),
    term([('DataFrame: Mumbai 484935971  4.0 s', G), ('RDD      : Mumbai 484935971 30.2 s', RD), ('same answer: True | 8x', Y)], size=7.2),
]
B1 = [
    t(180, 14, 'A list, split into partitions', 9.4, bold=True) + rdd(-1) + cap('Each partition goes to a task.', '', 'blue', y=110, h=30),
    t(180, 14, 'Lines from files', 9.4, bold=True) + rdd(0, ('lines 1–2517', 'lines 2518–5000'), 'items · 2 partitions') + cap('Just strings: no schema.', '', 'amber', y=110, h=30),
    t(180, 14, 'Whole files as elements', 9.4, bold=True) + rdd(-1, ('Aug file', 'Sep file', 'Oct file'), 'whole · 3 partitions') + cap('(path, content) pairs.', '', 'violet', y=110, h=30),
    t(180, 14, 'New RDD, same parent', 9.4, bold=True) + rdd(2, ('530 —', '480 990', '— 340'), 'big = filter(a >= 300)') + cap('Lineage: big ← amounts.', '', 'green', y=110, h=30),
    t(180, 14, 'Python objects cost time', 9.4, bold=True) + opbox(20, 34, 'JVM (DataFrame)', 'columnar · codegen', 'green', 150, 30) + opbox(190, 34, 'Python worker (RDD)', 'pickle · lambdas', 'amber', 150, 30) + arrow(170, 49, 190, 49, 'red', 1.6) + t(180, 84, '5,000,000 rows crossed this line', 7.4, 'red') + cap('Catalyst cannot optimise lambdas.', '', 'amber', y=110, h=30),
]
see_caps = ['Six amounts became three partitions of two.',
            'Each line of the file became one element.',
            'Each file became one element.',
            'filter() returned a new RDD with a lineage.',
            'Same answer; the RDD took 8× longer.']
behind_caps = ['glom() shows the split, for debugging.',
               'textFile knows nothing about the line’s format.',
               'Good for documents and small files.',
               'Lost partitions are rebuilt from the parent.',
               'Rows travel JVM → Python → JVM.']
two = anim_two('What is an RDD', 'Data in partitions + a recipe', 'Real lab outputs', 'Inside the RDD', see, B1, see_caps, behind_caps)

# ---- scenario 1: messy text
e1 = (t(180, 22, 'Kitchen partners send text', 9.4, bold=True) + t(180, 56, '100001|Poha,Idli|spice:hot,cutlery:no', 8, 'ink', mono=True) + cap('No schema, mixed separators.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'textFile + map(split)', 9.4, bold=True) + t(180, 56, 'line.split("|")', 8.4, 'ink', mono=True) + cap('Parse in Python, line by line.', '', 'green', y=150, h=34))
e3 = (t(180, 22, 'Bad lines?', 9.4, bold=True) + t(180, 56, 'filter(lambda f: len(f) == 3)', 8.4, 'ink', mono=True) + cap('Keep them aside, count them.', '', 'amber', y=150, h=34))
e4 = (t(180, 22, 'Convert to a DataFrame', 9.4, bold=True) + t(180, 56, 'spark.createDataFrame(rdd, schema)', 8.2, 'ink', mono=True) + cap('Structure from here on.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Fast from then on', 9.4, 'acc', bold=True) + t(180, 56, 'joins and aggregates as DataFrames', 8.4, 'ink2') + cap('Best of both.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Parsing messy partner files',
              'The most common reason RDD code still exists. (Typical pattern.)',
              'Text to structure', 'Use RDDs to parse unstructured text, set bad lines aside, then convert to a DataFrame for the heavy work', [e1, e2, e3, e4, e5],
              ['Raw text.', 'Split lines.', 'Handle bad lines.', 'Give it a schema.', 'Use DataFrames.'],
              hid='scenario-parse')

# ---- scenario 2: slow legacy job
b1 = (t(180, 22, 'Legacy job: 3 hours', 9.4, bold=True) + t(180, 56, 'df.rdd.map(...).reduceByKey(...)', 8.4, 'ink', mono=True) + cap('Written in 2016.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Why so slow?', 9.4, bold=True) + t(180, 56, 'every row pickled to Python', 8.4, 'ink2') + cap('Our lab: 8× slower.', '', 'amber', y=150, h=34))
b3 = (t(180, 22, 'Rewrite with DataFrames', 9.4, bold=True) + t(180, 56, 'where · groupBy · agg', 8.4, 'ink', mono=True) + cap('Same logic, no lambdas.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'Compare outputs', 9.4, bold=True) + t(180, 56, 'same answer: True', 8.4, 'ink', mono=True) + cap('Before switching over.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Minutes, not hours', 9.4, 'acc', bold=True) + t(180, 56, 'and cheaper clusters', 8.4, 'ink2') + cap('A common migration.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Speeding up a legacy RDD job',
              'Why teams rewrite old RDD code. (Typical; speed-up from our lab.)',
              'RDD to DataFrame', 'Python RDD code pays for pickling and gets no optimisation; rewriting structured logic as DataFrames is usually much faster', [b1, b2, b3, b4, b5],
              ['Old RDD job.', 'Python overhead.', 'Rewrite.', 'Verify.', 'Much faster.'],
              hid='scenario-legacy')

# ---- scenario 3: parallelize misuse
u1 = (t(180, 22, 'Driver OutOfMemoryError', 9.4, bold=True) + t(180, 56, 'rows = read_all_from_api()', 8.4, 'ink', mono=True) + cap('10 GB into a Python list.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Then parallelize', 9.4, bold=True) + t(180, 56, 'sc.parallelize(rows)', 8.4, 'ink', mono=True) + cap('Too late: driver already full.', '', 'amber', y=150, h=34))
u3 = (t(180, 22, 'Read in parallel instead', 9.4, bold=True) + t(180, 56, 'land files, then textFile/read', 8.4, 'ink2') + cap('Executors read their parts.', '', 'green', y=150, h=34))
u4 = (t(180, 22, 'Or parallelize the work', 9.4, bold=True) + t(180, 56, 'parallelize(page_numbers).flatMap(fetch)', 7.8, 'ink', mono=True) + cap('Small list, big result.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Rule', 9.4, 'acc', bold=True) + t(180, 56, 'parallelize small things only', 8.4, 'ink2') + cap('Data flows into executors.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'When parallelize is the wrong tool',
              'A driver memory incident and two better designs. (Typical.)',
              'Loading data', 'Never collect big data into the driver to parallelize it; read from storage or parallelize a small list of work items', [u1, u2, u3, u4, u5],
              ['Driver OOM.', 'parallelize copies from the driver.', 'Read in parallel.', 'Distribute the work list.', 'Small lists only.'],
              hid='scenario-parallelize')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Data in partitions, plus a recipe</h2>
  <p>Left: real outputs. Right: inside the RDD.</p>
''' + two + '''
  <p>Three live scenarios follow: parsing messy text, speeding up a legacy job, and misusing parallelize.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Where RDDs are still used</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'logs', 12, 'blue', bold=True) + t(60, 58, 'parsing', 7.4, 'ink2'),
    '1. Parsing unusual text formats',
    'Old log formats, multi-line records and partner files are often parsed with RDDs before becoming DataFrames.',
    ['Raw text', '*RDD parse', 'DataFrame']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'legacy', 10, 'green', bold=True) + t(60, 58, 'jobs', 7.4, 'ink2'),
    '2. Maintaining older pipelines',
    'Many Spark 1.x-era jobs are RDD code; engineers must read them before migrating them.',
    ['Old job', '*understand', 'Migrate']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'control', 10, 'violet', bold=True) + t(60, 58, 'partitions', 7.4, 'ink2'),
    '3. Fine control over partitions',
    'Custom partitioners and per-partition logic (mapPartitions with one connection per partition) need the RDD API.',
    ['Data', '*mapPartitions', 'External system']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'UI', 12, 'acc', bold=True) + t(60, 58, 'reading', 7.4, 'ink2'),
    '4. Reading the Spark UI',
    'DataFrame jobs appear as RDD operations (mapPartitions, ShuffledRDD) in DAG views; RDD knowledge explains them.',
    ['DAG view', '*RDD names', 'Understanding']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'interview', 8, 'acc', bold=True) + t(60, 58, 'basics', 7.4, 'ink2'),
    '5. Interviews',
    'RDD properties, lineage, transformations vs actions and RDD vs DataFrame are standard questions.',
    ['Question', '*RDD basics', 'Offer']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> Module 1, especially Lesson <a href="../../01-introduction/04-how-a-spark-job-runs/">1.4</a> (jobs, stages, tasks) and the Python patterns in <a href="../../01-introduction/01-prerequisites-python-sql-and-hadoop/">1.1</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
