import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
C = 'l122_bench.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)

R5 = [('pandas', 0.23, 1118), ('Polars', 0.07, 979), ('DuckDB', 0.03, 140), ('PySpark', 3.20, 1739)]
R50 = [('pandas', None, 5827), ('Polars', 0.58, 4912), ('DuckDB', 0.23, 386), ('PySpark', 6.26, 3731)]
def mem_bars(x, y, rows, scale=0.045, label=''):
    o = t(x, y - 6, label, 7.2, 'ink2', anchor='start', bold=True) if label else ''
    for k, (n, s, m) in enumerate(rows):
        yy = y + k * 20
        o += t(x + 50, yy + 11, n, 7, 'ink', anchor='end', bold=True) + box(x + 54, yy, max(m * scale, 2), 14, 'red' if s is None else ('green' if m < 1000 else 'amber'), rx=3)
        o += t(x + 58 + m * scale, yy + 11, ('OOM killed' if s is None else f'{m} MB'), 6.6, 'red' if s is None else 'ink2', anchor='start', mono=True)
    return o

# ---------------------------------------------------------------- story
sc_ = (mem_bars(14, 36, R50, 0.045, 'peak memory, 50M rows (8 GB machine)') +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Measured: groupBy on 50M rows', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('DuckDB : 0.23 s, 386 MB', 'green'), ('Polars : 0.58 s, 4.9 GB', 'blue'),
           ('PySpark: 6.26 s, 3.6 GB JVM', 'amber'), ('pandas : killed (out of memory)', 'red'),
           ('5M rows: DuckDB 0.03 s', 'green'), ('Spark start-up alone: ~6 s', 'amber')])))
scene_svg = scene('Spark is not the only engine for data. We ran the same three queries (group by, join + group by, top 3 per city) on 5 million and 50 million rows with pandas, Polars, DuckDB and PySpark on one 2-CPU, 8 GB machine, and measured time and peak memory.', sc_,
                  'On one machine, Spark is often the <tspan font-weight="700" class="s-acc">slowest</tspan> choice. It wins when one machine is not enough.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Do we really need Spark for this?”</h2>
  <div class="story">
    <p class="narration">A new TiffinGo analyst asked why a simple report on 5 million orders took a Spark cluster and 10 seconds, when her laptop answered it in a blink with DuckDB. A senior engineer replied that the nightly job processes billions of rows from 40 sources. Both were right.</p>

{scene_svg}

K> Sir, if DuckDB is 100 times faster, why did we learn Spark for 12 modules?
A> Because “faster” depends on the size and shape of the work. Single-machine engines avoid all distribution overhead, so on data that fits one machine they usually win. Spark pays that overhead to scale out to many machines, many hours and many teams.
R> And Flink and Trino?
A> Different jobs again: Flink for low-latency streaming, Trino for interactive SQL over many sources. Today we benchmark the single-machine tools against PySpark on our own data, then map out where each one fits. All benchmark outputs are real.
  </div>
</section>
'''

lv = '''
LEVELS> Choosing an engine at three levels
L1> Vehicles
      <ul>
        <li>pandas is a bicycle: easy, everywhere, but not for heavy loads. Polars and DuckDB are sports cars: very fast on one road. Spark is a fleet of trucks: slow to start, but it moves a city’s goods.</li>
        <li>Flink is an ambulance (always on, lowest latency); Trino is a taxi network (go anywhere, ask questions fast).</li>
      </ul>
L2> The tools
      <ul>
        <li><b>pandas</b>: eager, in-memory, single-threaded mostly; huge ecosystem.</li>
        <li><b>Polars</b>: Rust, multi-threaded, lazy query plans (<code>scan_parquet … collect()</code>).</li>
        <li><b>DuckDB</b>: embedded columnar SQL engine, vectorised, streams from Parquet, spills to disk.</li>
        <li><b>Spark</b>: distributed batch + streaming + ML; <b>Flink</b>: distributed stream-first; <b>Trino</b>: distributed interactive SQL over many sources.</li>
      </ul>
L3> What the benchmark showed
      <ul>
        <li>5M rows: DuckDB 0.03 s, Polars 0.07 s, pandas 0.23 s, PySpark 3.2 s for the same groupBy.</li>
        <li>50M rows: pandas was killed by the OS (out of memory); DuckDB used 386 MB, Polars 4.9 GB, Spark’s JVM 3.6 GB.</li>
        <li>Top-3 per city on 50M rows: DuckDB 1.3 s, Polars 8.6 s, PySpark 48.7 s on 2 local cores.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Spark and the alternatives</h2>
''' + def_block(
    'Data engines differ in <b>execution scope</b> (single process vs distributed cluster), <b>processing model</b> (eager vs lazy/optimised, batch vs streaming-first) and <b>interface</b> (DataFrame vs SQL). <b>pandas</b> is an eager in-memory DataFrame library; <b>Polars</b> is a multi-threaded columnar DataFrame engine with lazy query optimisation; <b>DuckDB</b> is an in-process analytical SQL database with vectorised execution and out-of-core processing. They avoid network and coordination overhead and excel when data fits one machine. <b>Apache Spark</b> distributes batch, streaming and ML workloads across a cluster with fault tolerance. <b>Apache Flink</b> is a distributed stream processor built around continuous, event-at-a-time processing with managed state and low latency. <b>Trino</b> is a distributed massively parallel SQL query engine for interactive analytics that federates many data sources without loading them.',
    'pandas, Polars and DuckDB run on one computer and are very fast when the data fits there. Spark spreads big jobs over many computers and survives failures. Flink is built for always-on streaming with very low delay, and Trino for fast SQL questions across many databases and lakes.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Single-node engine', 'Runs in one process/machine.'),
    ('Distributed engine', 'Runs across a cluster.'),
    ('Eager', 'Runs each step immediately (pandas).'),
    ('Lazy', 'Builds a plan, optimises, then runs.'),
    ('Vectorised', 'Processes batches of values at once.'),
    ('Out-of-core', 'Spills to disk when RAM is short.'),
    ('Federation', 'Query many sources in one SQL (Trino).'),
    ('Event-at-a-time', 'Flink’s streaming model.'),
]) + '''

  <h3>Where each engine fits</h3>
''' + table(['Engine', 'Scale', 'Best at', 'Not ideal for'], [
    ['pandas', 'Fits in RAM (×5–10 overhead)', 'Exploration, small data, ecosystem', 'Tens of millions of rows on a laptop (OOM in our lab)'],
    ['Polars', 'One machine, multi-core', 'Fast DataFrame pipelines', 'Data bigger than one machine'],
    ['DuckDB', 'One machine, can spill', 'Local SQL analytics on Parquet', 'Many concurrent writers, cluster scale'],
    ['Spark', 'Cluster, TB–PB', 'Big batch ETL, streaming, ML, many sources', 'Tiny, interactive single-machine queries'],
    ['Flink', 'Cluster', 'Low-latency stateful streaming', 'Ad-hoc batch analytics'],
    ['Trino', 'Cluster', 'Interactive SQL, federation', 'Long, complex ETL with retries'],
], minw=680) + lv + '''
EXAM> “When would you not use Spark?” When data fits comfortably on one machine and latency matters: DuckDB or Polars are often 10–100× faster there because they avoid cluster start-up, serialization and shuffles. Use Spark when data or compute exceed one machine, when you need fault-tolerant long jobs, unified batch/streaming/ML, or a shared platform; Flink for millisecond-level stateful streaming; Trino for interactive federated SQL.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>The same query in four tools</h2>
''' + table(['Tool', 'Group revenue by city'], [
    ['pandas', '<code>pd.read_parquet(p).groupby("city", as_index=False)["amount"].sum()</code>'],
    ['Polars', '<code>pl.scan_parquet(files).group_by("city").agg(pl.col("amount").sum()).collect()</code>'],
    ['DuckDB', '<code>duckdb.sql("SELECT city, sum(amount) FROM \'orders/*.parquet\' GROUP BY city")</code>'],
    ['PySpark', '<code>spark.read.parquet(p).groupBy("city").agg(F.sum("amount"))</code>'],
], minw=620) + '''
WARN> Benchmarks are easy to misread. Ours ran on 2 CPUs and 8 GB with other services running, Spark in <code>local[4]</code> with its ~6-second start-up, and a 431 MiB Parquet dataset: the home ground of single-node engines. On a 2 TB dataset none of the single-node tools would finish on that machine, while Spark would simply use more executors. Benchmark your own workload at your own size, and include start-up, memory and reliability, not just one query time.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Benchmarking four engines</h2>
  <p>All outputs are real: pandas 3.0.5, Polars 2.1.0, DuckDB 2.0.0, PySpark 4.3.0 (<code>local[4]</code>, 3 GB driver). Each engine ran in a fresh process; peak memory from <code>getrusage</code> (and the Spark JVM’s high-water mark). Data: the course’s 5M-row orders (34.6 MiB Parquet) and a 50M-row copy (431 MiB), joined with 4,000 customers.</p>
''' + stepper([
    ('Step 1 · The three queries',
     code('python', 'bench.py', '# q1 groupBy:       revenue per city\n# q2 join+groupBy:  orders ⋈ customers, revenue per tier\n# q3 top-3 per city: window / sort + head(3)\n# DuckDB example:\ncon.sql(f"SELECT city, sum(amount) FROM \'{P}/*.parquet\' GROUP BY city").fetchall()\ncon.sql(f"SELECT * FROM \'{P}/*.parquet\' QUALIFY row_number() OVER (PARTITION BY city ORDER BY amount DESC) <= 3")'),
     'The same logical queries written idiomatically in each tool. pandas loads the data first (eager); Polars and DuckDB scan Parquet lazily and only read needed columns; Spark builds a plan and runs it on its executors.'),
    ('Step 2 · 5 million rows',
     code('bash', 'run', 'for e in pandas polars duckdb pyspark; do python bench.py $e 5m; done', sec('# machine', 'pandas   50m')),
     'DuckDB answered the groupBy in <b>0.03 s</b> with 140 MB of memory; Polars in 0.07 s; pandas in 0.23 s after a 2.4 s load. PySpark needed 6.5 s just to start and 3.2 s for the first query (JVM warm-up), using a 1.6 GB JVM. For this size Spark is the wrong tool.'),
    ('Step 3 · 50 million rows',
     code('bash', 'run', 'for e in pandas polars duckdb pyspark; do python bench.py $e 50m; done', sec('pandas   50m')),
     'pandas tried to hold all 50M rows as Python-friendly columns and the OS <b>killed it</b> at about 6 GB. Polars finished but peaked at 4.9 GB. DuckDB stayed at <b>386 MB</b> by streaming through the files and was fastest everywhere. Spark’s JVM peaked at 3.6 GB within its 3 GB heap plus overhead and completed every query, but slowly on 2 cores, especially the full sort for top-3 (48.7 s).'),
    ('Step 4 · Where Spark wins (and Flink, Trino)',
     code('text', 'when', 'data > one machine (TB–PB)       -> Spark (or Trino for interactive SQL)\nlong ETL with retries, many joins  -> Spark\nbatch + streaming + ML, one API    -> Spark\nmillisecond stateful streaming     -> Flink (Spark Real-Time Mode is catching up)\nSQL across Postgres + lake + Kafka -> Trino (federation)\nfits in RAM, one user              -> DuckDB / Polars'),
     'Our lab cannot show Spark’s strengths, because they start where one machine ends: 10 TB jobs that need 200 executors, tasks retried on failure, and one engine for ETL, streaming (Module 9) and ML (Module 10). Flink and Trino were not run here; the guidance comes from their design. Many teams combine tools: DuckDB/Polars for local work, Spark for the platform, Trino for BI.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('q1 groupBy, 5M rows', W), ('DuckDB 0.03 s | Polars 0.07 s', G), ('pandas 0.23 s | PySpark 3.20 s', Y)], size=7.2),
    term([('peak memory, 5M rows', W), ('DuckDB 140 MB | Polars 979 MB', G), ('pandas 1118 MB | Spark JVM 1631 MB', Y)], size=7.0),
    term([('50M rows', W), ('pandas: Killed (out of memory)', RD), ('DuckDB 386 MB | Polars 4912 MB', G), ('Spark JVM 3622 MB, completed', Y)], size=7.0),
    term([('top-3 per city, 50M rows', W), ('DuckDB 1.27 s | Polars 8.64 s', G), ('PySpark 48.73 s (2 cores)', Y)], size=7.2),
]
B1 = [
    t(180, 14, 'Overhead vs work', 9.4, bold=True) + flow([('start JVM', '~6 s', 'amber'), ('plan + tasks', 'scheduling', 'violet'), ('work', 'tiny here', 'green')], y=50, w=96, gap=16) + cap('Small data: overhead dominates.', '', 'amber', y=144, h=30),
    t(180, 14, 'Memory at 5M rows', 9.4, bold=True) + mem_bars(30, 36, R5, 0.12) + cap('Columnar engines use less.', '', 'green', y=144, h=30),
    t(180, 14, 'Memory at 50M rows', 9.4, bold=True) + mem_bars(30, 36, R50, 0.036) + cap('pandas hit the RAM wall.', '', 'red', y=144, h=30),
    t(180, 14, 'Scale decides', 9.4, bold=True) + ''.join(opbox(14 + k * 112, 46, n, s, tone, 104, 34) for k, (n, s, tone) in enumerate([('DuckDB/Polars', 'fits one box', 'green'), ('Spark', 'beyond one box', 'blue'), ('Flink / Trino', 'stream / SQL', 'violet')])) + cap('Right tool per job.', '', 'blue', y=144, h=30),
]
see_caps = ['5M rows: time.', '5M rows: memory.', '50M rows.', 'Heavy query.']
behind_caps = ['Fixed overhead.', 'Columnar efficiency.', 'Out of memory.', 'Choosing an engine.']
two = anim_two('Spark vs single-node engines', 'Same queries, four engines', 'Real benchmark outputs', 'What it means', see, B1, see_caps, behind_caps)

e1 = (t(180, 22, 'Analyst report, 5M rows', 9.4, bold=True) + t(180, 56, 'Spark cluster, 10 s per run', 8.4, 'ink2') + cap('Shared cluster queue.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'DuckDB on the laptop', 9.4, bold=True) + t(180, 56, '0.03 s for the groupBy (lab)', 8.4, 'ink2') + cap('100× faster here.', '', 'green', y=150, h=34))
e3 = (t(180, 22, 'Read Parquet from the lake', 9.4, bold=True) + t(180, 56, 'same tables Spark writes', 8.4, 'ink2') + cap('Open formats help.', '', 'green', y=150, h=34))
e4 = (t(180, 22, 'Spark keeps the big jobs', 9.4, bold=True) + t(180, 56, 'nightly ETL over billions', 8.4, 'ink2') + cap('Right tool each.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Cluster freed for real work', 9.4, 'acc', bold=True) + t(180, 56, 'lower cost, happier analysts', 8.4, 'ink2') + cap('Mixed stack.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Small reports, big cluster',
              'Using single-node engines for small data. (Typical; timings from our lab.)',
              'Small data', 'Use DuckDB or Polars for data that fits one machine and keep Spark for large jobs', [e1, e2, e3, e4, e5],
              ['Slow.', 'DuckDB.', 'Same files.', 'Spark ETL.', 'Mixed.'],
              hid='scenario-small')
b1 = (t(180, 22, 'pandas script grew', 9.4, bold=True) + t(180, 56, '5M → 50M rows over a year', 8.4, 'ink2') + cap('Worked until it didn’t.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Killed: out of memory', 9.4, bold=True) + t(180, 56, '~6 GB on an 8 GB box (lab)', 8.4, 'ink2') + cap('No error message, just gone.', '', 'red', y=150, h=34))
b3 = (t(180, 22, 'Step 1: Polars or DuckDB', 9.4, bold=True) + t(180, 56, 'lazy scans, columnar', 8.4, 'ink2') + cap('386 MB with DuckDB.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'Step 2: Spark when it outgrows', 9.4, bold=True) + t(180, 56, 'one machine is not enough', 8.4, 'ink2') + cap('Or many sources/teams.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Plan the growth path', 9.4, 'acc', bold=True) + t(180, 56, 'pandas API on Spark helps', 8.4, 'ink2') + cap('pyspark.pandas.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'The pandas script that outgrew the laptop',
              'Growing beyond pandas. (Typical; OOM from our lab.)',
              'Growth path', 'Move from pandas to Polars/DuckDB, then to Spark as data and needs grow', [b1, b2, b3, b4, b5],
              ['Growth.', 'OOM.', 'Single-node.', 'Spark.', 'Plan.'],
              hid='scenario-growth')
u1 = (t(180, 22, 'Fraud scores in < 50 ms', 9.4, bold=True) + t(180, 56, 'per payment, stateful', 8.4, 'ink2') + cap('Strict latency.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Flink or Spark Real-Time Mode', 9.4, bold=True) + t(180, 56, 'event-at-a-time vs ~100 ms RTM', 8.2, 'ink2') + cap('Evaluate both.', '', 'amber', y=150, h=34))
u3 = (t(180, 22, 'BI on lake + Postgres', 9.4, bold=True) + t(180, 56, 'interactive dashboards', 8.4, 'ink2') + cap('Trino federation.', '', 'green', y=150, h=34))
u4 = (t(180, 22, 'Nightly ETL + ML', 9.4, bold=True) + t(180, 56, 'Spark batch + MLlib', 8.4, 'ink2') + cap('Spark’s home.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Shared tables (Iceberg)', 9.4, 'acc', bold=True) + t(180, 56, 'every engine reads the same data', 8.2, 'ink2') + cap('Composable stack.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'One company, four engines',
              'Spark, Flink and Trino in one architecture. (Typical.)',
              'Architecture', 'Combine engines by job type over shared open table formats', [u1, u2, u3, u4, u5],
              ['Latency.', 'Streaming.', 'BI.', 'ETL/ML.', 'Shared.'],
              hid='scenario-stack')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Same queries, four engines</h2>
  <p>Left: real benchmark outputs. Right: what they mean.</p>
''' + two + '''
  <p>Three live scenarios follow: small reports, a growing pandas script, and a multi-engine architecture.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Engines at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'DuckDB', 11, 'blue', bold=True) + t(60, 58, 'local', 7.4, 'ink2'),
    '1. Local analytics',
    'Analysts query lake Parquet files with DuckDB on laptops.',
    ['Parquet', '*DuckDB', 'Report']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'Polars', 11, 'green', bold=True) + t(60, 58, 'features', 7.4, 'ink2'),
    '2. Fast feature prep',
    'Data scientists prepare model features with Polars on one big machine.',
    ['Extract', '*Polars', 'Features']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'Spark', 12, 'violet', bold=True) + t(60, 58, 'platform', 7.4, 'ink2'),
    '3. Company data platform',
    'Spark runs ingestion, ETL, streaming and ML over the lakehouse.',
    ['40 sources', '*Spark', 'Lakehouse']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'Flink', 12, 'acc', bold=True) + t(60, 58, 'events', 7.4, 'ink2'),
    '4. Real-time decisions',
    'Flink powers millisecond fraud and pricing decisions on event streams.',
    ['Kafka', '*Flink', 'Decision']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'Trino', 12, 'acc', bold=True) + t(60, 58, 'BI', 7.4, 'ink2'),
    '5. Interactive BI',
    'Trino answers dashboard SQL across Iceberg, PostgreSQL and more.',
    ['BI tool', '*Trino', 'Many sources']) + '''
  <p class="muted">Examples are simplified. Benchmarks depend heavily on hardware, data and versions.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> what Spark is in <a href="../../01-introduction/02-what-is-apache-spark/">1.2</a>, toPandas and Arrow in <a href="../../04-dataframes/06-collect-topandas-and-arrow/">4.6</a>, Parquet in <a href="../../05-reading-and-writing-data/02-parquet-orc-and-avro/">5.2</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
