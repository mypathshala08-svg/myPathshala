import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='12-spark-in-industry', lesson='02-spark-vs-pandas-polars-duckdb-flink-trino', n='12.2',
    module_label='Module 12 · Spark in industry',
    title='Spark vs pandas, Polars, DuckDB, Flink and Trino',
    desc='A real benchmark of pandas 3.0, Polars 2.1, DuckDB 2.0 and PySpark 4.3 on 5M and 50M orders (2 CPUs, 8 GB): groupBy, join and top-3 per city timings and peak memory (DuckDB 0.03 s and 140 MB on 5M rows; pandas killed out of memory on 50M; Spark’s ~6 s start-up), and when to use Spark, single-node engines, Flink for low-latency streaming or Trino for federated interactive SQL.',
    og_desc='We benchmarked pandas, Polars, DuckDB and PySpark on 5M and 50M rows: pandas ran out of memory, DuckDB used 386 MB. When Spark is (and is not) the right tool.',
    minutes=26, level='Intermediate',
    lead='Spark is not always the right engine. This lesson <b>benchmarks pandas, Polars, DuckDB and PySpark</b> on the same queries at 5M and 50M rows, measuring time and memory, and then places Spark, Flink and Trino in a modern data stack. <b>Benchmark outputs are real</b>.',
    chips=['4 engines benchmarked', '5M and 50M rows', 'Memory measured', 'Runs in your browser (Python)'],
)

MAIN = '''# Rough rule: which engine for which job?
def pick(data_gb, ram_gb, latency_ms=None, sources=1, interactive=False):
    if latency_ms is not None and latency_ms < 200:
        return "Flink (or Spark Real-Time Mode)"
    if sources > 3 and interactive:
        return "Trino"
    if data_gb * 3 < ram_gb:
        return "DuckDB / Polars"
    return "Spark"

print(pick(0.4, 8))                       # our 50M-row Parquet
print(pick(2000, 64))                     # nightly lake ETL
print(pick(1, 16, latency_ms=50))         # fraud scoring
print(pick(500, 64, sources=5, interactive=True))
'''
RUN = dict(
    heading='Run the code: picking an engine',
    intro='<p>A deliberately simple rule of thumb. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('    if data_gb * 3 < ram_gb:', 'Single-node engines need headroom; pandas needs much more than columnar engines.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then try 20 GB on a 16 GB laptop.', code=None),
        dict(label='2 · Predict first: speed-up', hint='<b>Predict first:</b> DuckDB vs PySpark on the 5M groupBy.',
             code='''print(round(3.20 / 0.03), "x faster (lab, including Spark JIT warm-up)")
'''),
        dict(label='3 · Memory ratio', hint='Peak memory pandas vs DuckDB at 5M rows.',
             code='''print(round(1118 / 140, 1), "x more memory")
'''),
        dict(label='4 · Start-up share', hint='Spark start-up vs query time at 5M.',
             code='''start, query = 6.5, 3.2
print(round(start / (start + query) * 100), "% of the run was start-up")
'''),
        dict(label='5 · Spot the error', hint='pandas on 50M rows with 8 GB RAM.', expect='error',
             code='''needed_gb, ram_gb = 6.0, 8.0
other_services_gb = 3.0
assert needed_gb + other_services_gb < ram_gb, "Killed: out of memory (pandas held all rows in RAM)"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: the benchmark',
    intro='<p><code>pip install polars duckdb pandas pyarrow pyspark</code>, then the lab’s <code>bench.py</code>. <b>Outputs are real</b>.</p>',
    items=[
        dict(title='1 · DuckDB', cmd='python bench.py duckdb 5m', file='bash',
             output='duckdb   5m   | load/start   0.0 s | q1 groupBy  0.03 s | q2 join+groupBy  0.04 s | q3 top-3 per city  0.13 s | peak RSS    140 MB', note='Fastest here.'),
        dict(title='2 · PySpark', cmd='python bench.py pyspark 5m', file='bash',
             output='pyspark  5m   | load/start   6.5 s | q1 groupBy  3.20 s | q2 join+groupBy  1.39 s | q3 top-3 per city  6.53 s | peak RSS    108 MB (+JVM 1631 MB)', note='Start-up + JVM.'),
        dict(title='3 · pandas at 50M', cmd='python bench.py pandas 50m', file='bash',
             output='Killed', note='Out of memory on 8 GB.'),
    ],
)

TRACE = dict(
    heading='Eager vs lazy',
    intro='<p>Why lazy engines read less data.</p>',
    code='''columns = ["order_id", "customer_id", "city", "order_date", "amount", "status"]
needed = ["city", "amount"]
eager_reads = len(columns)
lazy_reads = len(needed)
print(eager_reads, lazy_reads)
''',
    notes={3: 'Eager :: pandas loads every column first.', 4: 'Lazy :: Polars/DuckDB/Spark prune to used columns.'},
)

WORKED_INTRO = 'Three engine choices at TiffinGo.'
EXAMPLES = [
    dict(level='b', tag='Engines · basics', title='Daily 300 MB report',
         problem='<p>One analyst, a 300 MB Parquet extract, results in seconds.</p>',
         inp='single machine',
         approach=['Fits easily in RAM.', 'No cluster needed.', 'DuckDB SQL or Polars.'],
         code='''print("DuckDB:", "SELECT city, sum(amount) FROM 'extract/*.parquet' GROUP BY city")
''', notes={1: 'Fast :: Milliseconds, as in the lab.'},
         tryit='Step 2.'),
    dict(level='i', tag='Engines · growth', title='pandas job running out of memory',
         problem='<p>A pandas job now processes 50M rows and crashes.</p>',
         inp='8 GB machine',
         approach=['Switch to Polars/DuckDB first.', 'Reads only needed columns.', 'Move to Spark only if it keeps growing.'],
         code='''print("pandas: Killed | DuckDB: 386 MB | Polars: 4912 MB (lab, 50M rows)")
''', notes={1: 'Cheapest fix :: Columnar single-node engine.'},
         tryit='Step 3.'),
    dict(level='a', tag='Engines · architecture', title='Design a stack',
         problem='<p>ETL over 40 sources, live fraud scores, BI dashboards.</p>',
         inp='mixed workloads',
         approach=['Spark for ETL/ML.', 'Flink (or Spark RTM) for low latency.', 'Trino for BI; Iceberg underneath.'],
         code='''stack = {"ETL/ML": "Spark", "fraud <100 ms": "Flink", "BI SQL": "Trino", "tables": "Iceberg"}
print(stack)
''', notes={1: 'Shared format :: Every engine reads the same tables.'},
         tryit='Scenario 3.'),
]

QUIZ = mix([
    dict(q='Beginner: Fastest engine in our 5M benchmark?', options=['pandas', 'Polars', 'DuckDB', 'PySpark'], answer=2,
         why='0.03 s groupBy.'),
    dict(q='Beginner: What happened to pandas at 50M rows?', options=['Fastest', 'Killed: out of memory', 'Same as DuckDB', 'Wrong result'], answer=1,
         why='~6 GB on 8 GB.'),
    dict(q='Beginner: Spark is built for…', options=['Tiny local data', 'Data and jobs bigger than one machine', 'Only streaming', 'Spreadsheets'], answer=1,
         why='Distributed processing.'),
    dict(q='Intermediate: Why was PySpark slowest on 5M rows?', options=['Bad code', 'Start-up and distribution overhead', 'No Parquet support', 'Python'], answer=1,
         why='~6 s start-up.'),
    dict(q='Intermediate: DuckDB used little memory because…', options=['Compression only', 'It streams columnar data and can spill', 'It skipped rows', 'Caching'], answer=1,
         why='386 MB at 50M.'),
    dict(q='Intermediate: Interactive SQL across many databases?', options=['pandas', 'Trino', 'Polars', 'Flink'], answer=1,
         why='Federation.'),
    dict(q='Advanced: Millisecond stateful streaming?', options=['Trino', 'Flink (Spark RTM catching up)', 'DuckDB', 'pandas'], answer=1,
         why='Event-at-a-time.'),
    dict(q='Advanced: Where does Spark clearly win?', options=['5 MB CSV', 'TB-scale ETL with retries, streaming and ML', 'One quick query', 'Spreadsheet math'], answer=1,
         why='Beyond one machine.'),
])

REVISION = [
    'Single-node engines (DuckDB, Polars) are fastest when data fits one machine.',
    '5M rows: DuckDB 0.03 s, Polars 0.07 s, pandas 0.23 s, PySpark 3.2 s (+6.5 s start).',
    '50M rows: pandas OOM-killed; DuckDB 386 MB; Polars 4.9 GB; Spark JVM 3.6 GB.',
    'Spark: TB–PB, fault tolerance, batch + streaming + ML, shared platform.',
    'Flink: low-latency stateful streaming; Trino: interactive federated SQL.',
    'Benchmark your own workload, including start-up and memory.',
    'Mix engines over shared open table formats.',
]
FAQ = [
    ('Will Spark ever be fast on small data?', 'Spark 4.3 adds opt-in single-task execution for small queries, and Spark Connect avoids per-user start-up, but single-node engines remain hard to beat on small data.'),
    ('Is pandas API on Spark a replacement for pandas?', 'It runs pandas-like code on Spark for large data; for small data, plain pandas or Polars is simpler and faster.'),
    ('Can DuckDB read Delta or Iceberg?', 'Yes, through extensions, so it can query tables that Spark writes.'),
    ('Should I learn Flink instead of Spark?', 'Learn Spark first for broad batch/streaming/ML work; add Flink if you build low-latency streaming systems.'),
    ('Why was the Polars top-3 slower than DuckDB?', 'Our Polars query sorted all 50M rows before taking the top 3; different formulations and versions change results, which is why you benchmark your own queries.'),
]

PRACTICE_INTRO = 'Programs for engine comparisons.'
PROBLEMS = [
    dict(level='easy', title='Speed-up', stmt='DuckDB vs pandas groupBy at 5M.', inp='0.23, 0.03',
         code='''print(round(0.23 / 0.03, 1))
''', explain='~7.7×.'),
    dict(level='easy', title='Memory saved', stmt='DuckDB vs Polars at 50M.', inp='386, 4912',
         code='''print(4912 - 386, "MB")
''', explain='Big difference.'),
    dict(level='easy', title='Start-up', stmt='Spark start-up for 100 tiny reports.', inp='6.5 s each',
         code='''print(round(100 * 6.5 / 60, 1), "minutes")
''', explain='Overhead adds up.'),
    dict(level='medium', title='Fits in RAM?', stmt='Rule: data × 3 < RAM.', inp='0.43 GB, 8 GB',
         code='''print(0.43 * 3 < 8)
''', explain='Single-node OK.'),
    dict(level='medium', title='Ranking', stmt='Rank engines by q1 time at 50M.', inp='times',
         code='''t = {"duckdb": 0.23, "polars": 0.58, "pyspark": 6.26}
print(sorted(t, key=t.get))
''', explain='pandas did not finish.'),
    dict(level='medium', title='Pick', stmt='Engine for 5 TB nightly ETL.', inp='5000 GB',
         code='''print("Spark" if 5000 * 3 > 64 else "DuckDB")
''', explain='Beyond one machine.'),
    dict(level='business', title='Cluster cost avoided', stmt='Monthly cost of 20 small reports moved off a ₹300/h cluster (0.2 h each daily).', inp='20 × 0.2 × 30',
         code='''print("₹", int(20 * 0.2 * 30 * 300))
''', explain='Use laptops/DuckDB.'),
    dict(level='business', title='Right tool', stmt='Count workloads per engine.', inp='list',
         code='''w = ["etl", "bi", "fraud", "report", "report"]
m = {"etl": "Spark", "bi": "Trino", "fraud": "Flink", "report": "DuckDB"}
from collections import Counter
print(Counter(m[x] for x in w))
''', explain='Mixed stack.'),
]

SCN_INTRO = 'Engine trade-off questions test judgement, not syntax.'
SCENARIOS = (
    scn('Any company · Spark', 'Fresher', '“Spark vs pandas”',
        'When use each?',
        'difference?',
        '<p>pandas runs in one process and holds data in memory: great for small data and exploration. Spark distributes work across a cluster for data and jobs larger than one machine. In my benchmark pandas was killed by out-of-memory at 50M rows on 8 GB, while Spark completed.</p>', 'Saying Spark is always faster.') +
    scn('Data engineering', 'Mid-level', 'Small data on Spark',
        'Many small reports run slowly on the Spark cluster.',
        'suggestion?',
        '''<ul>
          <li>Measure: start-up and scheduling dominate small jobs.</li>
          <li>Move them to DuckDB/Polars reading the same Parquet/Iceberg tables.</li>
          <li>Keep Spark for large ETL.</li>
        </ul>''', 'Adding more executors.') +
    scn('Data engineering', 'Mid-level', 'Streaming choice',
        'Need sub-100 ms stateful decisions on events.',
        'engine?',
        '''<ol>
          <li>Flink is designed for this.</li>
          <li>Spark Real-Time Mode (4.1+) targets ~100 ms for supported queries; evaluate.</li>
          <li>Benchmark with real traffic.</li>
        </ol>''', 'Micro-batches with 1-minute triggers.') +
    scn('Architecture', 'Senior', 'Modern stack',
        'Design a data stack for 500 TB and 200 analysts.',
        'design?',
        '''<ul>
          <li>Iceberg/Delta tables as the shared layer.</li>
          <li>Spark for ETL/ML, Trino for BI, Flink for low latency.</li>
          <li>DuckDB/Polars for local analysis.</li>
        </ul>''', 'One engine for everything.')
)
