import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
C = 'l53_write.txt'
def sec(a, b=None, drop=()):
    s = capsec(C, a, b, drop)
    s = re.sub(r'#\d+L?', '', s)
    return '\n'.join(l if len(l) <= 140 else l[:137] + ' …' for l in s.split('\n'))
S3 = sec('== 3)', '== 4)', drop=('FileScan',))
_fs = [l for l in capsec(C, '== 3)', '== 4)').split('\n') if 'FileScan' in l][0]
_fs = re.sub(r'#\d+L?', '', _fs)
S3 += '\n   +- FileScan parquet [amount,city] … ' + re.search(r'PartitionFilters: \[[^\]]*\]', _fs).group(0)

def folder(x, y, name, nfiles, tone='card', w=96):
    o = box(x, y, w, 20, tone, rx=3) + t(x + 6, y + 13, name, 6.8, 'ink', anchor='start', mono=True)
    for k in range(min(nfiles, 12)):
        o += box(x + 6 + k * 7, y + 24, 5, 7, tone, rx=1)
    if nfiles > 12:
        o += t(x + 94, y + 31, f'+{nfiles - 12}', 6.2, 'ink2', anchor='end')
    return o

# ---------------------------------------------------------------- story
sc_ = (''.join(folder(14 + (k % 3) * 104, 22 + (k // 3) * 42, f'city={c}', n, 'acc' if n > 12 else 'card') for k, (c, n) in enumerate([('Pune', 55), ('Delhi', 57), ('Mumbai', 53), ('Thane', 50), ('Chennai', 52), ('Bengaluru', 49)])) +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Measured', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('groupBy + partitionBy: 421 files', 'red'), ('repartition("city"): 8 files', 'green'),
           ('read back: 1.33 s vs 0.28 s', 'green'), ('pruning: 498,646 of 5M rows', 'green'),
           ('static overwrite: Delhi deleted!', 'red'), ('dynamic overwrite: only Pune', 'green')])))
scene_svg = scene('Writing decides how the next job reads. We wrote orders with save modes, partition folders, file-size limits and partition overwrites, and counted the files each choice produced.', sc_,
                  'Partition by what you <tspan font-weight="700" class="s-acc">filter</tspan>; control the number of <tspan font-weight="700" class="s-acc">files</tspan>.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Where did Delhi go?”</h2>
  <div class="story">
    <p class="narration">A bug in Pune’s prices had to be fixed in the daily revenue table, partitioned by city. Riya recomputed Pune and wrote it with <code>mode("overwrite")</code>. The Pune numbers were right the next morning. Every other city was gone.</p>

{scene_svg}

R> Sir, I only wrote Pune rows. Why were the other folders deleted?
A> Because by default an overwrite replaces the <b>whole table path</b>, not just the partitions in your DataFrame. That is “static” partition overwrite. With <code>partitionOverwriteMode=dynamic</code> Spark replaces only the partitions you write.
K> And why does the same table have 421 tiny files?
A> That is the other classic: every task writes its own file into every folder it touches. Today: what a write produces, save modes, <code>partitionBy</code> and pruning, the small-files problem and its fix, <code>maxRecordsPerFile</code>, static vs dynamic overwrite, and tables instead of paths. All outputs are real (PySpark 4.3.0).
  </div>
</section>
'''

lv = '''
LEVELS> Writing data at three levels
L1> Filing papers
      <ul>
        <li>Each worker puts their own pile of papers in the cabinet; ten workers make ten files.</li>
        <li>Folders per city let you open only the Pune folder later.</li>
        <li>If every worker drops one sheet into every folder, you get thousands of single sheets: hard to find anything.</li>
      </ul>
L2> The API
      <ul>
        <li><code>df.write.mode(m).format(f).option(…).partitionBy(cols).save(path)</code> or <code>.saveAsTable(name)</code>; modes: <code>errorifexists</code> (default), <code>append</code>, <code>overwrite</code>, <code>ignore</code>.</li>
        <li>File count = number of tasks that write × partition folders each task touches. Control it with <code>repartition</code>/<code>coalesce</code> and <code>maxRecordsPerFile</code>.</li>
        <li><code>spark.sql.sources.partitionOverwriteMode</code>: <code>static</code> (default) or <code>dynamic</code>.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>A groupBy result written with <code>partitionBy("city")</code> made <b>421 files</b> of about 1 KiB; <code>repartition("city")</code> first made 8, read back 4.8x faster.</li>
        <li>Partition pruning read 498,646 of 5,000,000 rows for a Pune query.</li>
        <li>Static overwrite of one city deleted the others; dynamic overwrite replaced only Pune.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Writing DataFrames</h2>
''' + def_block(
    '<code>DataFrameWriter</code> (<code>df.write</code>) saves a DataFrame through a data source. Each task writes its partition of the data to one or more <b>part files</b> in the output directory, and a commit protocol makes the result visible atomically, marked by a <code>_SUCCESS</code> file. The <b>save mode</b> defines behaviour when the target exists: <code>errorifexists</code> (default), <code>append</code>, <code>overwrite</code> or <code>ignore</code>. <code>partitionBy(cols)</code> writes a directory hierarchy <code>col=value/</code>, and readers prune directories that do not satisfy filters on those columns (<b>partition pruning</b>). Because every task writes a separate file for every partition directory it holds rows for, the number of files can grow to tasks × partition values (the <b>small-files problem</b>). With <code>overwrite</code>, <b>static</b> mode (default) deletes all existing partitions of the target first, whereas <b>dynamic</b> mode overwrites only partitions present in the data being written.',
    'When Spark writes, each task writes its own file, and partitionBy makes a folder per value. Plan the number of files, partition by columns you filter on, and use dynamic overwrite when you replace only some partitions.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Part file', 'One output file written by one task.'),
    ('_SUCCESS', 'Marker that the whole write committed.'),
    ('Save mode', 'errorifexists, append, overwrite, ignore.'),
    ('partitionBy', 'Folders per column value: city=Pune/.'),
    ('Partition pruning', 'Skip folders that cannot match a filter.'),
    ('Small files', 'Many tiny files: slow listing and reading.'),
    ('maxRecordsPerFile', 'Cap rows per output file.'),
    ('Dynamic overwrite', 'Replace only the partitions being written.'),
]) + '''

  <h3>Save modes</h3>
''' + table(['Mode', 'Target exists', 'Lab (1,000 rows, 3 files)'], [
    ['<code>errorifexists</code> (default)', 'Fail', 'PATH_ALREADY_EXISTS'],
    ['<code>ignore</code>', 'Do nothing', '1,000 rows'],
    ['<code>append</code>', 'Add new files', '2,000 rows, 6 files'],
    ['<code>overwrite</code>', 'Replace (whole path in static mode)', '1,000 rows, 3 files'],
], minw=600) + lv + '''
EXAM> “What is the small-files problem and how do you fix it?” Each write task creates one file per partition folder it touches, so a shuffle with 200 partitions written with partitionBy can produce thousands of tiny files; listing and opening them makes reads slow and stresses the NameNode or object store. Fix it with <code>repartition(partition_cols)</code> or <code>coalesce</code> before writing, AQE partition coalescing, <code>maxRecordsPerFile</code>, and periodic compaction (OPTIMIZE in Delta).
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Choosing partition columns</h2>
''' + table(['Good partition column', 'Bad partition column', 'Why'], [
    ['<code>order_date</code>, <code>month</code>', '<code>order_id</code>, <code>customer_id</code>', 'Low vs very high number of distinct values'],
    ['<code>city</code>, <code>country</code>', '<code>amount</code>', 'Filters use it vs nobody filters on exact amounts'],
    ['Few hundred to few thousand folders', 'Millions of folders', 'Each folder adds listing and metadata cost'],
    ['Each partition ≥ ~1 GB of data (big tables)', 'Partitions of a few KB', 'Otherwise every partition is a small file'],
], minw=680) + '''
WARN> Writing with <code>mode("overwrite")</code> to a partitioned path in the default <b>static</b> mode deletes every existing partition, even those not in your DataFrame. Set <code>spark.sql.sources.partitionOverwriteMode=dynamic</code> (per session or per write with <code>.option("partitionOverwriteMode", "dynamic")</code>) for jobs that rewrite only some days or cities, or use a table format with <code>replaceWhere</code>/<code>MERGE</code>.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Writes, folders and files</h2>
  <p>All outputs are real: PySpark 4.3.0, local mode with 4 cores, the 5-million-row orders table, default 200 shuffle partitions (AQE partition coalescing switched off so the effect is visible).</p>
''' + stepper([
    ('Step 1 · What a write produces',
     code('python', 'l53_write.py', 'small = orders.limit(1000).repartition(3)\nsmall.write.parquet(f"{O}/first")\nsorted(os.listdir(f"{O}/first"))', sec('== 1)', '== 2)')),
     'Three partitions became <b>three part files</b> named <code>part-0000N-&lt;job uuid&gt;-c000.snappy.parquet</code>, plus <code>_SUCCESS</code>, written last when the job committed. Readers ignore files starting with <code>_</code> or <code>.</code>; the <code>.crc</code> checksums are added by Hadoop’s local file system. On S3 or HDFS you will see only the part files and <code>_SUCCESS</code>.'),
    ('Step 2 · Save modes',
     code('python', 'l53_write.py', 'small.write.parquet(path)                    # again: default mode\nsmall.write.mode("ignore").parquet(path)\nsmall.write.mode("append").parquet(path)\nsmall.write.mode("overwrite").parquet(path)', sec('== 2)', '== 3)')),
     'The default refused to touch an existing path. <code>ignore</code> silently did nothing, <code>append</code> added 3 more files (2,000 rows), <code>overwrite</code> replaced everything. Re-running an <code>append</code> job after a failure duplicates data: design jobs to be safely re-runnable (overwrite a partition, or MERGE in a table format).'),
    ('Step 3 · partitionBy and pruning',
     code('python', 'l53_write.py', 'orders.write.partitionBy("city").parquet(f"{O}/by_city")\np = spark.read.parquet(f"{O}/by_city"); p.columns\np.where("city = \'Pune\'").select("amount").explain()\n# same query on the flat table vs the partitioned one', S3 + '\n' + sec('== 4)', '== 5)')),
     'Spark created a folder per city. The <code>city</code> values now live in folder names, not in the files, and come back as the <b>last column</b> when read. The plan shows <code>PartitionFilters</code>: the Pune query listed and read only <code>city=Pune/</code>, <b>498,646 rows instead of 5 million</b>, 2.5x faster.'),
    ('Step 4 · The small-files problem',
     code('python', 'l53_write.py', 'agg = orders.groupBy("city", "order_date").agg(F.sum("amount").alias("revenue"), F.count("*").alias("orders"))\nagg.write.partitionBy("city").parquet(f"{O}/daily")              # 200 tasks after the shuffle\nagg.repartition("city").write.partitionBy("city").parquet(f"{O}/daily2")', sec('== 5)', '== 6)')),
     'After the groupBy, the data sat in 200 shuffle partitions, each holding a few dates of <b>every</b> city, so each task wrote a file into every city folder: <b>421 files of 1 KiB</b>, 10.9 s to write and 1.33 s to read back a tiny table. <code>repartition("city")</code> put each city in one task: <b>8 files</b>, 5.4 s to write and 0.28 s to read. On object stores, where listing and opening files is slow, the gap is far bigger.'),
    ('Step 5 · Capping file size',
     code('python', 'l53_write.py', 'orders.repartition(1).write.option("maxRecordsPerFile", 1_000_000).parquet(f"{O}/capped")', sec('== 6)', '== 7)')),
     'One task wrote 5 million rows but rolled over to a new file every million: five files of 6.9 MiB. Use it to keep files in a sensible size range when one partition is large, without an extra shuffle. Aim for roughly 128 MB to 1 GB per file in big tables.'),
    ('Step 6 · Overwriting one partition, and tables',
     code('python', 'l53_write.py', 'base.write.partitionBy("city").parquet(path)          # Pune, Delhi, Mumbai\nspark.conf.set("spark.sql.sources.partitionOverwriteMode", mode)\nfix.write.mode("overwrite").partitionBy("city").parquet(path)   # only Pune rows\nagg.repartition("city").write.mode("overwrite").partitionBy("city").saveAsTable("daily_city")', sec('== 7)')),
     'Riya’s accident, reproduced: in <b>static</b> mode the Pune fix wiped Delhi and Mumbai. In <b>dynamic</b> mode only <code>city=Pune</code> was replaced. Finally, <code>saveAsTable</code> registered a managed, partitioned table in the catalog: other jobs and SQL users refer to <code>daily_city</code> by name, and Spark knows its partitions (Module 7).'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('part-00000-…snappy.parquet', W), ('part-00001-…  part-00002-…', W), ('_SUCCESS', G)], size=7.4),
    term([('default : PATH_ALREADY_EXISTS', RD), ('append  : 2000 rows, 6 files', Y), ('overwrite: 1000 rows, 3 files', G)], size=7.4),
    term([('city=Pune/ … 10 entries', W), ('flat       : 5,000,000 rows read', Y), ('partitioned:   498,646 rows read', G)], size=7.2),
    term([('200 tasks: 421 files, 1 KiB', RD), ('repartition(city): 8 files', G), ('read 1.33 s -> 0.28 s', G)], size=7.4),
    term([('static : [Pune 999]', RD), ('dynamic: [Delhi, Mumbai, Pune 999]', G)], size=7.6),
]
B1 = [
    t(180, 14, 'One file per task', 9.4, bold=True) + ''.join(opbox(20, 34 + k * 30, f'task {k}', '', 'blue', 70, 22) + arrow(90, 45 + k * 30, 170, 45 + k * 30, 'ink3', 1.0) + opbox(176, 34 + k * 30, f'part-0000{k}', '', 'green', 120, 22) for k in range(3)) + cap('Then _SUCCESS when all commit.', '', 'blue', y=144, h=30),
    t(180, 14, 'Modes decide what happens', 9.4, bold=True) + flow([('existing', 'path', 'card'), ('append', '+ files', 'amber'), ('overwrite', 'replace', 'green')], y=50, w=96, gap=22) + cap('Re-running append duplicates data.', '', 'amber', y=144, h=30),
    t(180, 14, 'Folders let Spark skip data', 9.4, bold=True) + folder(20, 34, 'city=Pune', 4, 'green') + folder(130, 34, 'city=Delhi', 4) + folder(240, 34, 'city=Mumbai', 4) + folder(20, 80, 'city=Thane', 4) + folder(130, 80, 'city=…', 4) + cap('PartitionFilters: only Pune is read.', '', 'green', y=144, h=30),
    t(180, 14, 'Every task touches every folder', 9.4, bold=True) + folder(20, 34, 'city=Pune', 55, 'acc') + folder(130, 34, 'city=Delhi', 57, 'acc') + folder(240, 34, 'city=Mumbai', 53, 'acc') + folder(20, 84, 'city=Pune', 1, 'green') + folder(130, 84, 'city=Delhi', 1, 'green') + folder(240, 84, 'city=Mumbai', 1, 'green') + cap('repartition("city") → one file each.', '', 'green', y=144, h=30),
    t(180, 14, 'Static vs dynamic overwrite', 9.4, bold=True) + folder(20, 34, 'Pune (new)', 1, 'green') + folder(130, 34, 'Delhi', 1, 'red') + folder(240, 34, 'Mumbai', 1, 'red') + t(120, 78, 'static: deleted', 7.4, 'red', anchor='start') + folder(20, 90, 'Pune (new)', 1, 'green') + folder(130, 90, 'Delhi', 1, 'green') + folder(240, 90, 'Mumbai', 1, 'green') + cap('dynamic: other partitions kept.', '', 'green', y=144, h=30),
]
see_caps = ['Three tasks, three part files.', 'Four modes, four outcomes.', 'Pune read 10% of the rows.', '421 files became 8.', 'Static overwrite deleted two cities.']
behind_caps = ['Commit makes the write visible.', 'Choose a re-runnable mode.', 'Folder names hold the values.', 'Files = tasks × folders touched.', 'partitionOverwriteMode matters.']
two = anim_two('Writing data', 'Folders, files and modes', 'Real lab outputs', 'What lands on disk', see, B1, see_caps, behind_caps)

# ---- scenario 1: overwrite accident
e1 = (t(180, 22, 'Fix one day of data', 9.4, bold=True) + t(180, 56, 'fixed.write.mode("overwrite").partitionBy("dt")', 7.8, 'ink', mono=True) + cap('A routine backfill.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Table now has one day', 9.4, bold=True) + t(180, 56, 'two years of partitions gone', 8.4, 'ink2') + cap('Static overwrite.', '', 'red', y=150, h=34))
e3 = (t(180, 22, 'Restore from backup', 9.4, bold=True) + t(180, 56, 'hours of downtime', 8.4, 'ink2') + cap('If there is a backup.', '', 'amber', y=150, h=34))
e4 = (t(180, 22, 'partitionOverwriteMode=dynamic', 9.4, bold=True) + t(180, 56, 'set as the platform default', 8.4, 'ink2') + cap('Only written days replaced.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Or a table format', 9.4, 'acc', bold=True) + t(180, 56, 'replaceWhere, MERGE, time travel', 8.4, 'ink2') + cap('Undo is possible.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'A backfill that deleted two years',
              'Static partition overwrite. (Behaviour from our lab.)',
              'Partition overwrite', 'Static overwrite deletes all partitions of the path; use dynamic mode or table-format operations for partial rewrites', [e1, e2, e3, e4, e5],
              ['Backfill.', 'Data gone.', 'Restore.', 'Dynamic mode.', 'Table format.'],
              hid='scenario-overwrite')

# ---- scenario 2: small files
b1 = (t(180, 22, 'Hourly job, partitionBy(date, city)', 9.4, bold=True) + t(180, 56, 'after a groupBy with 200 partitions', 8.4, 'ink2') + cap('Runs fine for months.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Millions of tiny files', 9.4, bold=True) + t(180, 56, 'queries spend minutes listing', 8.4, 'ink2') + cap('Like our 421 files.', '', 'amber', y=150, h=34))
b3 = (t(180, 22, 'repartition by partition columns', 9.4, bold=True) + t(180, 56, 'df.repartition("date", "city")', 8.4, 'ink', mono=True) + cap('One task per folder.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'Compact old partitions', 9.4, bold=True) + t(180, 56, 'rewrite or OPTIMIZE (Delta)', 8.4, 'ink2') + cap('Fix the history too.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'AQE coalescing helps', 9.4, 'acc', bold=True) + t(180, 56, 'on by default (Lesson 7.4)', 8.4, 'ink2') + cap('But check file counts.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'A lake drowning in small files',
              'The small-files problem. (Typical; file counts from our lab.)',
              'Small files', 'Writing many shuffle partitions into partition folders creates tasks × folders files; repartition by the partition columns and compact', [b1, b2, b3, b4, b5],
              ['Hourly job.', 'Tiny files.', 'Repartition.', 'Compact.', 'AQE.'],
              hid='scenario-small-files')

# ---- scenario 3: over-partitioning
u1 = (t(180, 22, 'partitionBy("customer_id")', 9.4, bold=True) + t(180, 56, '4 million customers', 8.4, 'ink2') + cap('“Fast lookups per customer.”', '', 'blue', y=150, h=34))
u2 = (t(180, 22, '4 million folders', 9.4, bold=True) + t(180, 56, 'each with a few KB', 8.4, 'ink2') + cap('Listing takes forever.', '', 'red', y=150, h=34))
u3 = (t(180, 22, 'Partition by date instead', 9.4, bold=True) + t(180, 56, 'hundreds of folders', 8.4, 'ink2') + cap('Low cardinality.', '', 'green', y=150, h=34))
u4 = (t(180, 22, 'Cluster by customer_id', 9.4, bold=True) + t(180, 56, 'sort within files → min/max skipping', 8.2, 'ink2') + cap('Lesson 5.2.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Or bucketing / clustering', 9.4, 'acc', bold=True) + t(180, 56, 'bucketBy, Delta liquid clustering', 8.4, 'ink2') + cap('Module 8.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Four million folders',
              'Choosing partition columns. (Typical.)',
              'Over-partitioning', 'Partition by low-cardinality filter columns; use sorting or clustering for high-cardinality keys', [u1, u2, u3, u4, u5],
              ['High cardinality.', 'Too many folders.', 'Partition by date.', 'Cluster ids.', 'Bucketing.'],
              hid='scenario-overpartition')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Folders, files and modes</h2>
  <p>Left: real outputs. Right: what lands on disk.</p>
''' + two + '''
  <p>Three live scenarios follow: a backfill that deleted two years, a lake of small files, and four million folders.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Writing data at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'daily', 12, 'blue', bold=True) + t(60, 58, 'partitions', 7.4, 'ink2'),
    '1. Daily partitioned tables',
    'Fact tables are partitioned by date; each run writes only its day with dynamic overwrite, so re-runs are safe.',
    ['Day’s data', '*dynamic overwrite', 'dt=2026-11-04']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'files', 12, 'green', bold=True) + t(60, 58, 'right size', 7.4, 'ink2'),
    '2. File-size control',
    'Writers repartition by partition columns and cap records per file so tables keep 128 MB–1 GB files.',
    ['DataFrame', '*repartition + cap', 'Healthy files']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'compact', 11, 'violet', bold=True) + t(60, 58, 'nightly', 7.4, 'ink2'),
    '3. Compaction jobs',
    'Streaming tables collect small files all day; a nightly job rewrites them into large files.',
    ['Small files', '*compaction', 'Large files']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'catalog', 10, 'acc', bold=True) + t(60, 58, 'tables', 7.4, 'ink2'),
    '4. Tables, not paths',
    'Outputs are saved as catalog tables so analysts query names and the platform tracks schemas and partitions.',
    ['DataFrame', '*saveAsTable', 'SQL by name']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'export', 11, 'acc', bold=True) + t(60, 58, 'one file', 7.4, 'ink2'),
    '5. Single-file exports',
    'Small partner exports use coalesce(1) to produce one CSV; never for large data.',
    ['Small result', '*coalesce(1)', 'One CSV']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> partitions and shuffles in <a href="../../02-rdds/04-narrow-vs-wide-and-the-shuffle/">2.4</a>, formats in <a href="../02-parquet-orc-and-avro/">5.2</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
