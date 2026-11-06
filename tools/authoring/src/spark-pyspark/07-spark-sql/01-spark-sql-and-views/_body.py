import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
C = 'l71_sql.txt'
def sec(a, b=None, drop=()):
    s = capsec(C, a, b, drop)
    return '\n'.join(l if len(l) <= 140 else l[:137] + ' …' for l in s.split('\n'))

def sessions(hi=None):
    o = box(10, 26, 340, 108, 'card') + t(180, 40, 'One Spark application (SparkContext)', 8, bold=True)
    o += box(22, 50, 140, 46, 'blue' if hi == 's1' else 'card') + t(92, 64, 'session A', 7.6, bold=True) + opbox(32, 68, 'temp view', 'orders', 'green', 120, 24)
    o += box(198, 50, 140, 46, 'blue' if hi == 's2' else 'card') + t(268, 64, 'session B', 7.6, bold=True) + opbox(208, 68, 'orders?', 'not found', 'acc', 120, 24)
    o += opbox(110, 104, 'global_temp.orders_g', 'all sessions', 'violet', 140, 24)
    return o

# ---------------------------------------------------------------- story
sc_ = (sessions() +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Measured', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('temp view: invisible elsewhere', 'amber'), ('global_temp view: 5,000,000', 'green'),
           ('view count after append: 3 (!)', 'red'), ('after REFRESH TABLE: 8', 'green'),
           ("f-string 'OR 1=1': 5,000,000", 'red'), ('named parameter: 0', 'green')])))
scene_svg = scene('Spark SQL runs SQL text on the same engine as DataFrames. Temporary views give DataFrames a name for SQL. We tested where views are visible, whether they see new data, and what happens when user input is pasted into SQL.', sc_,
                  'A view is a <tspan font-weight="700" class="s-acc">named query</tspan>, not a copy; pass values as <tspan font-weight="700" class="s-acc">parameters</tspan>.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“The report showed every city”</h2>
  <div class="story">
    <p class="narration">TiffinGo’s internal report page let managers type a city name. A Python function built the query with an f-string: <code>f"... WHERE city = '{{city}}'"</code>. One curious manager typed <code>Pune' OR '1'='1</code> and got all 5 million orders, including cities he was not allowed to see.</p>

{scene_svg}

K> Sir, Spark is not a website database. Does SQL injection even apply?
A> Any time you paste user text into SQL, yes. Spark supports <b>parameter markers</b>, so the value is never parsed as SQL. We will reproduce the attack and the fix.
R> And the analysts say their view “did not see” today’s data.
A> A temp view is a saved <b>query</b>, but Spark caches the file listing behind it. Today: SQL and DataFrames together, temp and global views, refreshing, parameters, Spark 4’s pipe syntax and SQL errors. All outputs are real (PySpark 4.3.0).
  </div>
</section>
'''

lv = '''
LEVELS> Spark SQL at three levels
L1> Two languages, one kitchen
      <ul>
        <li>Some cooks read recipes in Hindi, others in English; the kitchen is the same. SQL and DataFrames are two languages for the same engine.</li>
        <li>A view is a name on a recipe card, not a cooked dish.</li>
        <li>Filling a blank on a form (a parameter) is safe; letting a customer rewrite the recipe is not.</li>
      </ul>
L2> The API
      <ul>
        <li><code>df.createOrReplaceTempView("orders")</code>, <code>createOrReplaceGlobalTempView</code> (<code>global_temp.name</code>), <code>spark.sql(...)</code> returns a DataFrame.</li>
        <li>Parameters: <code>spark.sql("… WHERE city = :city", args={"city": v})</code> or <code>?</code> with a list; DataFrames as <code>{t}</code> keyword arguments.</li>
        <li><code>REFRESH TABLE name</code> or <code>spark.catalog.refreshTable</code> after files change; pipe syntax <code>FROM t |&gt; WHERE … |&gt; AGGREGATE …</code> (Spark 4).</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>A temp view was invisible to a new session; a global temp view returned 5,000,000 rows there.</li>
        <li>After appending 5 rows to the files, the view still counted 3 until <code>REFRESH TABLE</code> (then 8).</li>
        <li>The injected f-string matched 5,000,000 rows; the same text as a named parameter matched 0.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Spark SQL and views</h2>
''' + def_block(
    '<b>Spark SQL</b> is Spark’s module for structured data; its SQL interface (<code>spark.sql</code>) parses ANSI-style SQL into the same logical plans as the DataFrame API, optimised by Catalyst and returned as DataFrames. A <b>temporary view</b> registers a logical plan under a name for the lifetime of a SparkSession; a <b>global temporary view</b> is registered in the system database <code>global_temp</code> and is shared by all sessions of the application until it ends. Views store no data: each query re-executes the plan, though file-based relations may reuse cached file listings until refreshed. Since Spark 3.4, <code>spark.sql</code> accepts named (<code>:name</code>) and positional (<code>?</code>) <b>parameter markers</b> bound as literals, which prevents SQL injection.',
    'You can write SQL against DataFrames by giving them a name with a temp view. SQL and DataFrame code run on the same engine. A view is a stored query, not stored data, and user input should always be passed as parameters, never pasted into the SQL text.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('spark.sql()', 'Run SQL, get a DataFrame.'),
    ('Temp view', 'Name for a DataFrame in one session.'),
    ('Global temp view', 'Shared by sessions: global_temp.name.'),
    ('REFRESH TABLE', 'Forget cached file listings and metadata.'),
    ('Parameter marker', ':name or ? bound as a value.'),
    ('SQL injection', 'User text changing the meaning of SQL.'),
    ('Pipe syntax', 'FROM t |&gt; WHERE … |&gt; … (Spark 4).'),
    ('AnalysisException', 'Errors found before running (names, grouping).'),
]) + '''

  <h3>Kinds of named objects</h3>
''' + table(['Object', 'Lives', 'Visible to', 'Stores data?'], [
    ['Temp view', 'Until the session ends', 'That session', 'No'],
    ['Global temp view', 'Until the application ends', 'All sessions (<code>global_temp.</code>)', 'No'],
    ['Persistent view', 'In the catalog', 'All applications with that catalog', 'No'],
    ['Table (Lesson 7.2)', 'In the catalog + storage', 'All applications', 'Yes'],
], minw=600) + lv + '''
EXAM> “Temp view vs global temp view?” A temp view is scoped to the SparkSession that created it; a global temp view lives in the <code>global_temp</code> database and is visible to all sessions of the same application. Neither stores data or survives the application; for that, create a table.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Passing values into SQL</h2>
''' + table(['Method', 'Example', 'Safe?'], [
    ['f-string / concatenation', '<code>spark.sql(f"… city = \'{c}\'")</code>', '<b>No</b>: injection, quoting bugs'],
    ['Named parameter', '<code>spark.sql("… city = :c", args={"c": c})</code>', 'Yes'],
    ['Positional parameter', '<code>spark.sql("… city = ?", args=[c])</code>', 'Yes'],
    ['DataFrame / Column as argument', '<code>spark.sql("SELECT * FROM {t}", t=df)</code>', 'Yes (objects, not text)'],
    ['DataFrame API', '<code>df.where(F.col("city") == c)</code>', 'Yes'],
], minw=640) + '''
WARN> Python’s <code>{t}</code> formatting in <code>spark.sql(query, **kwargs)</code> is safe for DataFrames and Columns, but plain strings passed that way are still inserted as SQL text. For values that come from users, files or APIs, always use parameter markers (<code>:name</code>, <code>?</code>).
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>SQL on the orders table</h2>
  <p>All outputs are real: PySpark 4.3.0, local mode, 5,000,000 orders registered as a temp view.</p>
''' + stepper([
    ('Step 1 · A temp view and a SQL query',
     code('python', 'l71_sql.py', 'o.createOrReplaceTempView("orders")\nspark.sql("""SELECT city, count(*) AS orders, sum(amount) AS revenue FROM orders\n             WHERE status = \'DELIVERED\' GROUP BY city ORDER BY revenue DESC LIMIT 3""").show()\ntype(spark.sql("SELECT 1"))', sec('== 1)', '== 3)')),
     'Registering a view costs nothing: it only names the DataFrame’s plan. <code>spark.sql</code> returned an ordinary <b>DataFrame</b>, so DataFrame methods continued on the SQL result. Mix freely: SQL for readable aggregations, Python for logic around them.'),
    ('Step 2 · Temp vs global temp views',
     code('python', 'l71_sql.py', 'o.createOrReplaceGlobalTempView("orders_g")\ns2 = spark.newSession()\ns2.sql("SELECT count(*) FROM orders")\ns2.sql("SELECT count(*) FROM global_temp.orders_g")', sec('== 3)', '== 4)')),
     'The new session (as a notebook gateway or Thrift Server gives each user, Lesson 4.1) could not see <code>orders</code>, but read the global view through the <code>global_temp</code> database. Both disappear when the application stops.'),
    ('Step 3 · A view does not always see new files',
     code('python', 'l71_sql.py', 'spark.range(3).write.parquet(p)\nspark.read.parquet(p).createOrReplaceTempView("live")\nspark.sql("SELECT count(*) FROM live")\nspark.range(100, 105).write.mode("append").parquet(p)\nspark.sql("SELECT count(*) FROM live")\nspark.sql("REFRESH TABLE live"); spark.sql("SELECT count(*) FROM live")', sec('== 4)', '== 5)')),
     'The view stores the query, but the DataFrame behind it had already <b>listed the files</b>. After 5 rows were appended by another writer, the view still counted 3. <code>REFRESH TABLE live</code> dropped the cached listing: 8. Long-running notebooks and servers need refreshes (or re-reading) when data changes underneath them.'),
    ('Step 4 · Views on views',
     code('python', 'l71_sql.py', 'spark.sql("""CREATE OR REPLACE TEMP VIEW city_daily AS\n  SELECT city, order_date, sum(amount) AS revenue, count(*) AS n FROM orders GROUP BY city, order_date""")\nspark.sql("SELECT city, round(avg(revenue)) AS avg_daily FROM city_daily GROUP BY city ORDER BY avg_daily DESC LIMIT 3")', sec('== 5)', '== 6)')),
     'SQL views can build on each other, like steps of a pipeline. Catalyst expands them into one plan and optimises the whole thing, so layering views costs nothing extra at run time.'),
    ('Step 5 · SQL injection and parameters',
     code('python', 'l71_sql.py', 'city = "Pune\' OR \'1\'=\'1"\nspark.sql(f"SELECT count(*) FROM orders WHERE city = \'{city}\'")\nspark.sql("SELECT count(*) FROM orders WHERE city = :city", args={"city": city})\nspark.sql("SELECT count(*) FROM orders WHERE city = :city", args={"city": "Pune"})\nspark.sql("SELECT count(*) FROM {t} WHERE amount > {m}", t=o, m=900)', sec('== 6)', '== 7)')),
     'The f-string turned the input into SQL: <code>city = \'Pune\' OR \'1\'=\'1\'</code>, true for <b>all 5,000,000</b> rows. As a named parameter the same text was just a strange city name: 0 rows. Real values worked normally (498,646 for Pune). DataFrames can be passed to SQL as objects with <code>{t}</code>.'),
    ('Step 6 · Pipe syntax and SQL errors',
     code('python', 'l71_sql.py', 'spark.sql("""FROM orders\n  |> WHERE status = \'CANCELLED\'\n  |> AGGREGATE count(*) AS cancelled GROUP BY city\n  |> ORDER BY cancelled DESC\n  |> LIMIT 3""").show()\nspark.sql("SELECT cty FROM orders"); spark.sql("SELECT city, sum(amount) FROM orders")\nspark.catalog.listTables()', sec('== 7)')),
     'Spark 4’s <b>pipe syntax</b> writes SQL in the order it runs, like a chain of DataFrame calls. Mistakes are <code>AnalysisException</code>s raised before any job: a misspelt column (with a suggestion) and a missing GROUP BY. The catalog lists our three temp views.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('spark.sql(...) -> DataFrame', G), ('Mumbai 951430 484935971', W)], size=7.6),
    term([('orders in new session: NOT_FOUND', RD), ('global_temp.orders_g: 5000000', G)], size=7.4),
    term([('count: 3', W), ('append 5 rows -> view: 3', RD), ('REFRESH TABLE -> 8', G)], size=7.6),
    term([("f-string  : 5000000", RD), ('parameter : 0', G), ('Pune      : 498646', W)], size=7.6),
    term([('FROM orders |> WHERE … |> AGGREGATE', G), ('cty: UNRESOLVED_COLUMN', RD)], size=7.4),
]
B1 = [
    t(180, 14, 'SQL text, same engine', 9.4, bold=True) + flow([('SQL text', 'parser', 'blue'), ('DataFrame', 'API', 'blue'), ('Catalyst', 'one plan', 'violet')], y=50, w=96, gap=22) + cap('spark.sql returns a DataFrame.', '', 'blue', y=144, h=30),
    t(180, 14, 'Where views live', 9.4, bold=True) + sessions('s2') + cap('global_temp is shared by sessions.', '', 'violet', y=144, h=30),
    t(180, 14, 'A view keeps the plan', 9.4, bold=True) + flow([('view', 'plan', 'blue'), ('file list', 'cached', 'amber'), ('new files', 'unseen', 'acc')], y=50, w=96, gap=22) + cap('REFRESH TABLE re-lists files.', '', 'amber', y=144, h=30),
    t(180, 14, 'Text vs value', 9.4, bold=True) + opbox(20, 36, "WHERE city = 'Pune' OR '1'='1'", 'parsed as SQL', 'acc', 320, 30) + opbox(20, 84, 'WHERE city = :city', "value: Pune' OR '1'='1", 'green', 320, 30) + cap('Parameters are never parsed.', '', 'red', y=144, h=30),
    t(180, 14, 'Read in execution order', 9.4, bold=True) + flow([('FROM', 'orders', 'card'), ('WHERE', 'CANCELLED', 'blue'), ('AGGREGATE', 'by city', 'violet'), ('LIMIT', '3', 'green')], y=50, w=72, gap=14) + cap('Pipe syntax (Spark 4).', '', 'green', y=144, h=30),
]
see_caps = ['SQL gave a DataFrame.', 'Global view visible elsewhere.', 'The view missed 5 new rows.', 'Injection vs parameter.', 'Pipe syntax and analysis errors.']
behind_caps = ['One optimizer for both.', 'Sessions isolate temp views.', 'File listings are cached.', 'Values are bound, not pasted.', 'Errors before any job.']
two = anim_two('Spark SQL and views', 'SQL on the same engine', 'Real lab outputs', 'Names, plans and values', see, B1, see_caps, behind_caps)

# ---- scenarios
e1 = (t(180, 22, 'Report page with a city box', 9.4, bold=True) + t(180, 56, "f\"… WHERE city = '{city}'\"", 8.4, 'ink', mono=True) + cap('Built quickly.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, "User types Pune' OR '1'='1", 9.4, bold=True) + t(180, 56, 'sees every city', 8.4, 'ink2') + cap('5,000,000 rows in our lab.', '', 'red', y=150, h=34))
e3 = (t(180, 22, 'Parameter markers', 9.4, bold=True) + t(180, 56, 'spark.sql(q, args={"city": city})', 8.2, 'ink', mono=True) + cap('0 rows for the attack.', '', 'green', y=150, h=34))
e4 = (t(180, 22, 'Allow-list values', 9.4, bold=True) + t(180, 56, 'city must be one of the 8 cities', 8.4, 'ink2') + cap('Defence in depth.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Access control in the catalog', 9.4, 'acc', bold=True) + t(180, 56, 'row filters (Unity/Ranger)', 8.4, 'ink2') + cap('Not only in the app.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'A city box that showed every city',
              'SQL injection in Spark SQL. (Behaviour from our lab.)',
              'SQL parameters', 'Building SQL with f-strings lets input change the query; parameter markers bind values safely', [e1, e2, e3, e4, e5],
              ['f-string.', 'Injection.', 'Parameters.', 'Allow-list.', 'Access control.'],
              hid='scenario-injection')
b1 = (t(180, 22, 'Notebook open all day', 9.4, bold=True) + t(180, 56, 'temp view over today’s folder', 8.4, 'ink2') + cap('Hourly files land.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Counts do not change', 9.4, bold=True) + t(180, 56, 'file list cached at read', 8.4, 'ink2') + cap('3 stayed 3 in our lab.', '', 'amber', y=150, h=34))
b3 = (t(180, 22, 'REFRESH TABLE', 9.4, bold=True) + t(180, 56, 'or re-read and re-register', 8.4, 'ink2') + cap('Now 8.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'Tables with a catalog', 9.4, bold=True) + t(180, 56, 'Delta/Iceberg track new files', 8.4, 'ink2') + cap('Lesson 11.5.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Or streaming', 9.4, 'acc', bold=True) + t(180, 56, 'for continuously arriving files', 8.4, 'ink2') + cap('Module 9.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'A view that stopped updating',
              'Cached file listings. (Behaviour from our lab.)',
              'Stale views', 'File-based views cache their file listing; refresh or re-read when new files arrive', [b1, b2, b3, b4, b5],
              ['Long session.', 'Stale.', 'Refresh.', 'Table formats.', 'Streaming.'],
              hid='scenario-stale-view')
u1 = (t(180, 22, 'SQL analysts, Python engineers', 9.4, bold=True) + t(180, 56, 'two code bases for one report', 8.4, 'ink2') + cap('Logic drifts apart.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'One plan either way', 9.4, bold=True) + t(180, 56, 'SQL and DataFrame → Catalyst', 8.4, 'ink2') + cap('Lesson 4.1: equal plans.', '', 'green', y=150, h=34))
u3 = (t(180, 22, 'Shared views', 9.4, bold=True) + t(180, 56, 'business logic in SQL views', 8.4, 'ink2') + cap('Python reads them.', '', 'green', y=150, h=34))
u4 = (t(180, 22, 'Pipe syntax for readability', 9.4, bold=True) + t(180, 56, 'step order like DataFrame code', 8.4, 'ink2') + cap('Spark 4.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Persistent views in the catalog', 9.4, 'acc', bold=True) + t(180, 56, 'CREATE VIEW db.v AS …', 8.4, 'ink', mono=True) + cap('Lesson 7.2.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Two teams, two versions of one metric',
              'Sharing logic between SQL and Python. (Typical.)',
              'Shared SQL logic', 'SQL and DataFrames compile to the same plans; keep shared logic in views that both use', [u1, u2, u3, u4, u5],
              ['Two teams.', 'One engine.', 'Views.', 'Pipe syntax.', 'Catalog views.'],
              hid='scenario-shared-sql')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>SQL on the same engine</h2>
  <p>Left: real outputs. Right: names, plans and values.</p>
''' + two + '''
  <p>Three live scenarios follow: SQL injection, a stale view, and one metric for two teams.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Spark SQL at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'BI', 12, 'blue', bold=True) + t(60, 58, 'dashboards', 7.4, 'ink2'),
    '1. BI over the lake',
    'Dashboards send SQL to Spark through the Thrift Server or Databricks SQL.',
    ['Dashboard', '*Spark SQL', 'Lake tables']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'ETL', 12, 'green', bold=True) + t(60, 58, 'SQL steps', 7.4, 'ink2'),
    '2. SQL pipelines',
    'Transformations written as SQL views and executed by Spark (dbt-spark, Declarative Pipelines).',
    ['SQL models', '*views', 'Tables']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'apps', 12, 'violet', bold=True) + t(60, 58, 'parameters', 7.4, 'ink2'),
    '3. Internal tools',
    'Report pages pass user filters as SQL parameters, never as concatenated text.',
    ['User input', '*:param', 'Safe query']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'mixed', 11, 'acc', bold=True) + t(60, 58, 'SQL + Py', 7.4, 'ink2'),
    '4. Notebooks',
    'Analysts mix %sql cells and PySpark cells on the same temp views.',
    ['DataFrame', '*temp view', 'SQL cell']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'migrate', 10, 'acc', bold=True) + t(60, 58, 'Hive SQL', 7.4, 'ink2'),
    '5. Migrating Hive jobs',
    'HiveQL scripts move to Spark SQL with few changes and run much faster.',
    ['HiveQL', '*Spark SQL', 'Faster jobs']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> SparkSession and plans in <a href="../../04-dataframes/01-sparksession-and-dataframes/">4.1</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
