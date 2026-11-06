import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='07-spark-sql', lesson='01-spark-sql-and-views', n='7.1',
    module_label='Module 7 · Spark SQL',
    title='Spark SQL and views',
    desc='Spark SQL and views in PySpark 4.3.0: spark.sql returning DataFrames, temp views invisible to a new session while a global temp view returned 5,000,000 rows, a view that still counted 3 rows after 5 were appended until REFRESH TABLE, views on views, SQL injection through an f-string (5,000,000 rows) versus named parameters (0 rows), Spark 4 pipe syntax, and analysis errors.',
    og_desc='An f-string turned one city filter into all 5,000,000 rows; a parameter marker returned 0. Spark SQL and views, tested.',
    minutes=28, level='Beginner → Intermediate',
    lead='Module 7 is about Spark SQL: the SQL interface, tables and the catalog, the optimizer and adaptive execution. First: running SQL on DataFrames with <b>views</b>, how long views live, when they go stale, and how to pass values safely with <b>parameters</b>. <b>All outputs are real</b> (PySpark 4.3.0).',
    chips=['PySpark 4.3.0', 'SQL injection reproduced', 'Pipe syntax (Spark 4)', 'Runs in your browser (Python)'],
)

MAIN = '''# Why f-strings are dangerous in SQL (no Spark needed to see it)
city = "Pune' OR '1'='1"

unsafe = f"SELECT count(*) FROM orders WHERE city = '{city}'"
print("query sent:", unsafe)

# with a parameter the SQL text never changes; the value is bound separately
safe_sql = "SELECT count(*) FROM orders WHERE city = :city"
args = {"city": city}
print("query sent:", safe_sql, "| args:", args)
'''
RUN = dict(
    heading='Run the code: text vs parameters',
    intro='<p>See exactly what SQL text each approach produces. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('unsafe = f"SELECT count(*) FROM orders WHERE city = \'{city}\'"', 'The OR clause becomes part of the query: 5,000,000 rows in our lab.'),
        ('safe_sql = "SELECT count(*) FROM orders WHERE city = :city"', 'The text never changes; the value matched 0 rows.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Compare the two printed queries.', code=None),
        dict(label='2 · Predict first: views', hint='<b>Predict first:</b> which session sees each view?',
             code='''views = {"orders": "session A only", "global_temp.orders_g": "all sessions of the app"}
for v, who in views.items():
    print(f"{v:22} -> {who}")
'''),
        dict(label='3 · Stale view', hint='A cached file list misses appended files.',
             code='''listed = ["part-0.parquet"]           # listed when the view was created
on_disk = listed + ["part-1.parquet"]  # appended later
print("view reads:", listed, "| after REFRESH:", on_disk)
'''),
        dict(label='4 · Allow-list', hint='Validate a city before querying.',
             code='''CITIES = {"Pune", "Delhi", "Mumbai"}
for c in ("Pune", "Pune' OR '1'='1"):
    print(c, "->", "ok" if c in CITIES else "rejected")
'''),
        dict(label='5 · Spot the error', hint='This query is built with an f-string from user input.', expect='error',
             code='''code = 'spark.sql(f"SELECT * FROM orders WHERE city = \\'{user_city}\\'")'
assert "f\\"" not in code, "use spark.sql(q, args={...}) with :name markers"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: SQL',
    intro='<p>In the <code>pyspark</code> shell. <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · Parameter', cmd='spark.sql("SELECT count(*) FROM orders WHERE city = :city", args={"city": "Pune"}).first()[0]', file='pyspark',
             output='498646', note='Values bound, not pasted.'),
        dict(title='2 · Global view', cmd='spark.newSession().sql("SELECT count(*) FROM global_temp.orders_g").first()[0]', file='pyspark',
             output='5000000', note='Plain temp views are not visible.'),
        dict(title='3 · Catalog', cmd='[(t.name, t.tableType) for t in spark.catalog.listTables()]', file='pyspark',
             output="[('city_daily', 'TEMPORARY'), ('live', 'TEMPORARY'), ('orders', 'TEMPORARY')]", note='Temp views only.'),
    ],
)

TRACE = dict(
    heading='Which session sees which view',
    intro='<p>Follow name lookup in two sessions.</p>',
    code='''global_views = {"orders_g"}
session_views = {"A": {"orders"}, "B": set()}
def lookup(session, name):
    if name.startswith("global_temp."):
        return name.split(".")[1] in global_views
    return name in session_views[session]
print(lookup("A", "orders"), lookup("B", "orders"), lookup("B", "global_temp.orders_g"))
''',
    notes={4: 'global_temp :: A shared database for the whole application.', 6: 'Session :: Temp views are per session.'},
)

WORKED_INTRO = 'Three SQL tasks at TiffinGo.'
EXAMPLES = [
    dict(level='b', tag='SQL · basics', title='Revenue per city in SQL',
         problem='<p>Write the city revenue report in SQL.</p>',
         inp='orders DataFrame',
         approach=['Register a temp view.', 'spark.sql.', 'Continue in Python if needed.'],
         code='''print("""o.createOrReplaceTempView("orders")
spark.sql("SELECT city, sum(amount) AS revenue FROM orders GROUP BY city ORDER BY revenue DESC").show()""")
''', notes={1: 'Free :: A view only names the plan.'},
         tryit='Step 1.'),
    dict(level='i', tag='SQL · safety', title='A safe report function',
         problem='<p>Return revenue for a user-chosen city and date.</p>',
         inp='city, day from a web form',
         approach=['Allow-list the city.', 'Named parameters.', 'No string building.'],
         code='''def revenue_sql(city, day):
    return ("SELECT sum(amount) FROM orders WHERE city = :city AND order_date = :day",
            {"city": city, "day": day})
print(revenue_sql("Pune", "2026-10-29"))
''', notes={2: 'Parameters :: spark.sql(q, args=params).'},
         tryit='Step 5.'),
    dict(level='a', tag='SQL · freshness', title='Keep a long session fresh',
         problem='<p>A server keeps views over hourly folders.</p>',
         inp='temp view over files',
         approach=['REFRESH TABLE each hour.', 'Or re-read and re-register.', 'Better: a table format.'],
         code='''print("""spark.sql("REFRESH TABLE live")      # or spark.catalog.refreshTable("live")""")
''', notes={1: 'Listing :: Drops cached file lists and metadata.'},
         tryit='Step 3.'),
]

QUIZ = mix([
    dict(q='Beginner: What does spark.sql() return?', options=['A list', 'A DataFrame', 'A string', 'Nothing'], answer=1,
         why='Same engine as DataFrames.'),
    dict(q='Beginner: How do you make a DataFrame usable in SQL?', options=['cache()', 'createOrReplaceTempView', 'collect()', 'write.parquet'], answer=1,
         why='Name the plan.'),
    dict(q='Beginner: Where do global temp views live?', options=['default', 'global_temp', 'tmp', 'hive'], answer=1,
         why='global_temp.name.'),
    dict(q='Intermediate: Does a temp view store data?', options=['Yes', 'No, it stores a query plan', 'Only cached', 'In the metastore'], answer=1,
         why='Each query re-runs the plan.'),
    dict(q='Intermediate: Why did the view count stay at 3?', options=['Bug', 'The file listing was cached', 'Append failed', 'Wrong path'], answer=1,
         why='REFRESH TABLE → 8.'),
    dict(q='Intermediate: Safe way to pass a value into spark.sql?', options=['f-string', 'args with :name markers', '% formatting', 'concatenation'], answer=1,
         why='0 rows for the attack.'),
    dict(q='Advanced: What does the pipe operator |> do?', options=['Comments', 'Chains SQL operations in execution order', 'Pipes to a file', 'Parallelism'], answer=1,
         why='Spark 4 SQL pipe syntax.'),
    dict(q='Advanced: When is SELECT city, sum(amount) FROM orders rejected?', options=['At run time', 'At analysis, before any job', 'Never', 'On write'], answer=1,
         why='MISSING_GROUP_BY.'),
])

REVISION = [
    '<code>spark.sql</code> → DataFrame; SQL and DataFrames share Catalyst.',
    'Temp view: one session. Global temp view: <code>global_temp.</code>, whole application.',
    'Views store queries, not data; file listings are cached: <code>REFRESH TABLE</code> (3 → 8).',
    'Views on views are free: one combined plan.',
    'Never build SQL with f-strings: injection returned all 5,000,000 rows.',
    'Use <code>args</code> with <code>:name</code> or <code>?</code>; pass DataFrames as <code>{t}</code>.',
    'Spark 4 pipe syntax <code>|&gt;</code>; errors are AnalysisExceptions before any job.',
]
FAQ = [
    ('Can I create a permanent view?', 'Yes, with a catalog: <code>CREATE VIEW db.v AS …</code> stores the query in the metastore (Lesson 7.2). It still stores no data.'),
    ('Is SQL slower than DataFrame code?', 'No. Both compile to the same optimized plan (Lesson 4.1).'),
    ('How do I run SQL from a file?', 'Read the file into a string and call spark.sql per statement, or use spark-sql CLI / SQL scripting (Spark 4.1+).'),
    ('Can parameters be table names?', 'No, markers bind values only. Use IDENTIFIER(:name) for identifiers, or pass DataFrames with {t}.'),
    ('What is the Thrift Server?', 'A JDBC/ODBC server that lets BI tools send SQL to a Spark application; each connection gets its own session.'),
]

PRACTICE_INTRO = 'Programs about SQL text, views and parameters.'
PROBLEMS = [
    dict(level='easy', title='Escape check', stmt='Does input contain a quote?', inp="Pune' OR '1'='1",
         code='''s = "Pune' OR '1'='1"
print("'" in s)
''', explain='One reason to use parameters.'),
    dict(level='easy', title='Global name', stmt='Full name of a global view.', inp='orders_g',
         code='''print("global_temp." + "orders_g")
''', explain='Required prefix.'),
    dict(level='easy', title='Refresh gain', stmt='Rows missed before refresh.', inp='8 vs 3',
         code='''print(8 - 3)
''', explain='Appended rows.'),
    dict(level='medium', title='Build params', stmt='Build args for several filters.', inp='city, min amount',
         code='''filters = {"city": "Pune", "min_amt": 500}
where = " AND ".join(["city = :city", "amount >= :min_amt"])
print(where, filters)
''', explain='Text fixed; values bound.'),
    dict(level='medium', title='Pipe to classic', stmt='Rewrite a pipe query as classic SQL.', inp='FROM t |> WHERE x |> AGGREGATE …',
         code='''print("SELECT city, count(*) AS cancelled FROM orders WHERE status = 'CANCELLED' GROUP BY city ORDER BY cancelled DESC LIMIT 3")
''', explain='Same plan.'),
    dict(level='medium', title='Allow-list', stmt='Reject unknown cities.', inp='input list',
         code='''ok = {"Pune", "Delhi"}
print([c for c in ["Pune", "X' OR 1=1"] if c in ok])
''', explain='Defence in depth.'),
    dict(level='business', title='Leak size', stmt='Rows exposed by the injection.', inp='5,000,000 vs 498,646',
         code='''print(5_000_000 - 498_646, "rows the user should not see")
''', explain='Real data protection issue.'),
    dict(level='business', title='Stale share', stmt='Share of today’s data missed by a stale view.', inp='5 of 8 rows',
         code='''print(f"{5 / 8:.0%}")
''', explain='Refresh in long sessions.'),
]

SCN_INTRO = 'SQL questions in Spark interviews go beyond syntax.'
SCENARIOS = (
    scn('Any company · Spark', 'Fresher', '“How do you run SQL on a DataFrame?”',
        'Run a SQL query on a DataFrame.',
        'views?',
        '<p>Register it with <code>df.createOrReplaceTempView("orders")</code> and call <code>spark.sql("SELECT …")</code>, which returns a DataFrame. Temp views last for the session; global temp views are shared via <code>global_temp</code>.</p>', 'Writing the DataFrame to disk first.') +
    scn('Data engineering', 'Mid-level', 'User input in SQL',
        'A tool builds Spark SQL from user input.',
        'security?',
        '''<ul>
          <li>Never concatenate input: injection returned all rows in my test.</li>
          <li>Use parameter markers (:name, ?) via args.</li>
          <li>Allow-list values; enforce access control in the catalog.</li>
        </ul>''', '“Spark is not vulnerable to SQL injection.”') +
    scn('Data engineering', 'Mid-level', 'View does not show new data',
        'A notebook’s view misses files written later.',
        'caching of listings?',
        '''<ol>
          <li>The DataFrame behind the view cached its file listing.</li>
          <li>REFRESH TABLE or re-read.</li>
          <li>Use table formats or streaming for live data.</li>
        </ol>''', 'Restarting the cluster.') +
    scn('Analytics', 'Senior', 'SQL vs DataFrames on a team',
        'Should the team standardise on SQL or PySpark?',
        'engine knowledge?',
        '''<ul>
          <li>Same optimizer and performance.</li>
          <li>SQL views for shared business logic; Python for orchestration and complex logic.</li>
          <li>Parameterised SQL, tests on both.</li>
        </ul>''', 'Claiming one is faster.')
)
