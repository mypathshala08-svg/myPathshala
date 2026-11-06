import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='05-reading-and-writing-data', lesson='03-writing-data-and-small-files', n='5.3',
    module_label='Module 5 · Reading and writing data',
    title='Writing data and small files',
    desc='Writing DataFrames with PySpark 4.3.0: part files and _SUCCESS, save modes, partitionBy with partition pruning (498,646 of 5,000,000 rows read), the small-files problem where a groupBy written with partitionBy made 421 files of 1 KiB until repartition("city") made 8 (read back 1.33 s vs 0.28 s), maxRecordsPerFile, static partition overwrite deleting other cities versus dynamic overwrite, and saveAsTable.',
    og_desc='Overwriting one city deleted all the others, and a tiny table became 421 files. Writing data and the small-files problem in Spark, reproduced.',
    minutes=32, level='Intermediate',
    lead='How you write decides how fast every later job reads, and whether a re-run is safe. This lesson covers save modes, partitioned output, the <b>small-files problem</b> and the dangerous default of <b>static partition overwrite</b>. <b>All outputs are real</b> (PySpark 4.3.0).',
    chips=['PySpark 4.3.0', '421 files → 8', 'Overwrite accident reproduced', 'Runs in your browser (Python)'],
)

MAIN = '''# How many files will a partitioned write create?
tasks = 200                    # shuffle partitions after a groupBy
cities = 8
dates = 61

# each task holds a few dates of EVERY city -> one file per city it touches
per_city = min(tasks, dates)                   # tasks that hold rows of that city
print("without repartition: about", per_city * cities, "files (lab: 421)")
print("repartition('city') :", cities, "files")
'''
RUN = dict(
    heading='Run the code: counting output files',
    intro='<p>A rough model of Step 4. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('per_city = min(tasks, dates)                   # tasks that hold rows of that city', 'Rows of one city are spread over the tasks that got its dates.'),
        ('print("repartition(\'city\') :", cities, "files")', 'All rows of a city go to one task: one file per folder.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then try 2,000 shuffle partitions and 365 dates.', code=None),
        dict(label='2 · Predict first: static overwrite', hint='<b>Predict first:</b> which folders remain after writing only Pune in each mode?',
             code='''existing = {"Pune", "Delhi", "Mumbai"}
written = {"Pune"}
print("static :", sorted(written))
print("dynamic:", sorted(existing | written))
'''),
        dict(label='3 · maxRecordsPerFile', hint='Files for one task with 5M rows and a 1M cap.',
             code='''import math
print(math.ceil(5_000_000 / 1_000_000), "files")
'''),
        dict(label='4 · Pruning', hint='Share of data read for one city out of eight (lab).',
             code='''print(f"{498_646 / 5_000_000:.1%}")
'''),
        dict(label='5 · Spot the error', hint='This table is partitioned by order_id.', expect='error',
             code='''distinct_values = 5_000_000
assert distinct_values < 10_000, "too many partition folders: partition by date or city, cluster by id instead"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: writes',
    intro='<p>In the <code>pyspark</code> shell. <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · Default mode', cmd='small.write.parquet("out/first")      # second time', file='pyspark',
             output='[PATH_ALREADY_EXISTS] Path file:/…/out/first already exists. Set mode as "overwrite" to overwrite the existing path.', note='errorifexists is the default.'),
        dict(title='2 · Small files', cmd='agg.write.partitionBy("city").parquet("out/daily")\nlen(glob.glob("out/daily/*/*.parquet"))', file='pyspark',
             output='421', note='8 after repartition("city").'),
        dict(title='3 · Overwrite mode', cmd='spark.conf.get("spark.sql.sources.partitionOverwriteMode")', file='pyspark',
             output="'static'", note='Set "dynamic" for partial rewrites.'),
    ],
)

TRACE = dict(
    heading='Static vs dynamic overwrite',
    intro='<p>Follow which partitions survive.</p>',
    code='''table = {"Pune": 450, "Delhi": 380, "Mumbai": 610}
fix = {"Pune": 999}
static = dict(fix)
dynamic = {**table, **fix}
print("static :", static)
print("dynamic:", dynamic)
''',
    notes={3: 'Static :: The whole path is replaced by the new data.', 4: 'Dynamic :: Only partitions present in the new data are replaced.'},
)

WORKED_INTRO = 'Three writing tasks for TiffinGo’s lake.'
EXAMPLES = [
    dict(level='b', tag='Writes · basics', title='A daily partitioned write',
         problem='<p>Write today’s orders into a date-partitioned table, safe to re-run.</p>',
         inp='orders for 2026-11-04',
         approach=['partitionBy("order_date").', 'Dynamic overwrite.', 'Repartition by the partition column.'],
         code='''print("""(today.repartition("order_date")
      .write.mode("overwrite").option("partitionOverwriteMode", "dynamic")
      .partitionBy("order_date").parquet("lake/orders"))""")
''', notes={2: 'Safe :: A re-run replaces only that day.'},
         tryit='Step 6.'),
    dict(level='i', tag='Writes · files', title='Fix a small-files table',
         problem='<p>A table has thousands of tiny files per folder.</p>',
         inp='daily table, partitioned by city',
         approach=['Read it.', 'repartition("city").', 'Write to a new path and swap.'],
         code='''before, after = 421, 8
print(f"{before} -> {after} files, read 1.33 s -> 0.28 s (lab)")
''', notes={1: 'Compaction :: Table formats do this with OPTIMIZE.'},
         tryit='Step 4.'),
    dict(level='a', tag='Writes · design', title='Pick the layout',
         problem='<p>Design the layout of a 2 TB/year orders table queried by date and customer.</p>',
         inp='filters: date range, customer_id',
         approach=['Partition by date (≈365 folders/year).', 'Sort/cluster by customer_id inside.', 'Files 256 MB–1 GB.'],
         code='''tb_per_year, days = 2, 365
print(round(tb_per_year * 1024 / days, 1), "GB per day partition -> about", round(tb_per_year * 1024 / days / 0.5), "files of 512 MB")
''', notes={1: 'Size :: Divide data per partition by a target file size.'},
         tryit='Module 8 covers bucketing and clustering.'),
]

QUIZ = mix([
    dict(q='Beginner: Default save mode?', options=['overwrite', 'append', 'errorifexists', 'ignore'], answer=2,
         why='PATH_ALREADY_EXISTS.'),
    dict(q='Beginner: What does _SUCCESS mean?', options=['A log', 'The whole write committed', 'A schema file', 'An error'], answer=1,
         why='Written last.'),
    dict(q='Beginner: What does partitionBy("city") create?', options=['Columns', 'Folders city=…/', 'Indexes', 'Buckets'], answer=1,
         why='One folder per value.'),
    dict(q='Intermediate: Rows read for a Pune query on the partitioned table?', options=['5,000,000', '498,646', '0', '1,000'], answer=1,
         why='PartitionFilters pruned other folders.'),
    dict(q='Intermediate: Why 421 files?', options=['Bug', 'Each of many tasks wrote a file into every city folder', 'maxRecordsPerFile', 'Avro'], answer=1,
         why='tasks × folders.'),
    dict(q='Intermediate: Fix for many small files before writing?', options=['coalesce(1) always', 'repartition by the partition columns', 'More executors', 'cache()'], answer=1,
         why='One task per folder.'),
    dict(q='Advanced: Overwrite of Pune only, static mode. What remains?', options=['All cities', 'Only Pune', 'Nothing', 'Pune and Delhi'], answer=1,
         why='The whole path was replaced.'),
    dict(q='Advanced: A bad partition column is…', options=['order_date', 'city', 'order_id', 'month'], answer=2,
         why='Millions of folders.'),
])

REVISION = [
    'A write = one part file per task (+ <code>_SUCCESS</code>).',
    'Modes: errorifexists (default), append, overwrite, ignore. Re-running append duplicates.',
    '<code>partitionBy</code>: folders per value; pruning read 498,646 of 5M rows.',
    'Small files: tasks × folders (421 files) → <code>repartition(cols)</code> first (8 files).',
    '<code>maxRecordsPerFile</code> caps file size without a shuffle.',
    'Static overwrite deletes all partitions; use <code>partitionOverwriteMode=dynamic</code>.',
    'Partition by low-cardinality filter columns; <code>saveAsTable</code> for named tables.',
]
FAQ = [
    ('Is coalesce(1) a good way to get one file?', 'Only for small outputs. It makes one task write everything, losing all parallelism; for large data keep many files of sensible size.'),
    ('Does AQE fix small files?', 'AQE coalesces small shuffle partitions (on by default), which reduces files after a shuffle, but it does not know your partition folders. Check file counts.'),
    ('How do I compact an existing table?', 'Rewrite it with fewer partitions to a new location and swap, or use OPTIMIZE in Delta Lake / rewrite_data_files in Iceberg.'),
    ('What is the difference between saveAsTable and save?', 'save writes files to a path; saveAsTable also registers the table in the catalog (managed or external), so it can be queried by name.'),
    ('Is _SUCCESS reliable on S3?', 'It marks completion of a Spark job, but object stores need committers designed for them (S3A committers) or table formats for atomic, consistent writes.'),
]

PRACTICE_INTRO = 'Programs about files, folders and modes.'
PROBLEMS = [
    dict(level='easy', title='Files per write', stmt='Files written by a 12-partition DataFrame without partitionBy.', inp='12 tasks',
         code='''print(12)
''', explain='One per task.'),
    dict(level='easy', title='Pruning saving', stmt='Rows skipped for the Pune query.', inp='5,000,000 − 498,646',
         code='''print(5_000_000 - 498_646)
''', explain='Other folders were never opened.'),
    dict(level='easy', title='Append twice', stmt='Rows after appending 1,000 rows twice to 1,000.', inp='modes',
         code='''print(1000 + 1000 + 1000)
''', explain='Re-runs duplicate.'),
    dict(level='medium', title='Average file size', stmt='Average file size before and after.', inp='421 files of ~1 KiB vs 8 files',
         code='''total_kib = 421 * 1.0
print(round(total_kib / 8, 1), "KiB per file after repartition")
''', explain='Lab measured 1.8 KiB; compression differs.'),
    dict(level='medium', title='Files with a cap', stmt='Files for 23M rows, cap 5M.', inp='one task',
         code='''import math
print(math.ceil(23 / 5))
''', explain='Last file is smaller.'),
    dict(level='medium', title='Folders', stmt='Folders for partitionBy(date, city) over 61 days, 8 cities.', inp='two levels',
         code='''print(61 * 8)
''', explain='Watch combined cardinality.'),
    dict(level='business', title='Listing cost', stmt='Listing requests for a query on small files.', inp='1 million files, 1,000 per list call',
         code='''print(1_000_000 // 1000, "list calls before reading anything")
''', explain='Object stores charge and throttle per request.'),
    dict(level='business', title='Backfill risk', stmt='Days of data lost by a static overwrite of one day.', inp='730 days in the table',
         code='''print(730 - 1)
''', explain='Use dynamic overwrite.'),
]

SCN_INTRO = 'Writing questions reveal whether you have operated a real data lake.'
SCENARIOS = (
    scn('Any company · Spark', 'Fresher', '“What are save modes?”',
        'Explain Spark save modes.',
        'do you know the defaults?',
        '<p>errorifexists (default) fails if the target exists, append adds files, overwrite replaces the target, ignore does nothing. With partitioned tables I set partitionOverwriteMode to dynamic so an overwrite replaces only the partitions in the DataFrame.</p>', 'Not knowing the default.') +
    scn('Data engineering', 'Mid-level', 'Small files',
        'Queries on a table are slow and it has thousands of tiny files.',
        'can you explain and fix it?',
        '''<ul>
          <li>Each task writes one file per partition folder: tasks × folders.</li>
          <li>Repartition by the partition columns before writing; cap file size.</li>
          <li>Compact existing data; in my test 421 files → 8 and reads 4.8x faster.</li>
        </ul>''', 'coalesce(1) for a big table.') +
    scn('Data engineering', 'Mid-level', 'Backfill deleted data',
        'After a backfill of one day, the table had only that day.',
        'do you know overwrite semantics?',
        '''<ol>
          <li>Static partition overwrite replaced the whole path.</li>
          <li>Restore; then use partitionOverwriteMode=dynamic or replaceWhere/MERGE.</li>
          <li>Make dynamic the platform default and test backfills on copies.</li>
        </ol>''', 'Blaming the storage system.') +
    scn('Platform', 'Senior', 'Table layout',
        'Design partitioning for a large events table.',
        'can you balance pruning and file counts?',
        '''<ul>
          <li>Partition by date (and maybe region), not by ids.</li>
          <li>Cluster or sort by frequent filter keys within partitions.</li>
          <li>Target 128 MB–1 GB files; schedule compaction; use a table format.</li>
        </ul>''', 'Partitioning by every filter column.')
)
